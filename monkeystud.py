# monkeystud.py -- MonkeyStud, a poker variant for bots

# see README.md for more dox

import os, random, sys, itertools, logging, imp, time, itertools, getopt

EXPECTED_PYTHON_VERSION = (2, 7)    # must be running python 2.7
MAX_TIME                = 100.0     # bot can be no more than 100x slower

CHIPS_START    = 1024               # each player starts with 1024 chips
ANTE           = 6                  # ante is 1 / 64th total chip count each
MAX_SEATS      = 8                  # maximum seats at a table

RANKS          = 8                  # duece through nine
SUITS          = 4                  # clubs, diamonds, hearts, spades
INVALID_CARD   = 17 << 3
HIGH           = 0                  # high card
PAIR           = 1                  # one pair
STR            = 2                  # straight
FLUSH          = 3                  # flush
TRIP           = 4                  # three of a kind
STRF           = 5                  # straight flush


g_catch_exceptions = False
g_max_time = MAX_TIME

def make_card(r, s):
    return (r << 3) | s


def rank_suit(c):
    return c >> 3, c & 7


def rank_str(r):
    return '23456789'[r]


def suit_str(s):
    return 'cdhs'[s]


def card_str(a):
    if INVALID_CARD == a:
        return 'xx'
    return "%s%s" % (rank_str(a >> 3), suit_str(a & 7))


def str_to_card(s):
    if 'xx' == s:
        return INVALID_CARD
    return make_card(ord(s[0]) - ord('2'), {'c': 0, 'd': 1, 'h': 2, 's': 3}[s[1]])


def str_to_hand(s):
    h = []
    for i in s.split(','):
        h.append(str_to_card(i.strip()))
    return h


def hand_str(h):
    return ','.join(map(lambda x : card_str(x), h))


def hand_value_class(x):
    return x >> 28


def hand_value_str(x):
    c = x >> 28
    if HIGH == c:
        return 'high card (%s, %s, %s)' % \
                (rank_str((x >> 8) & 15), \
                rank_str((x >> 4) & 15), rank_str(x & 15))
    if PAIR == c:
        return 'pair of %s\'s (%s, %s, %s)' % \
                (rank_str((x >> 24) & 15), rank_str((x >> 8) & 15), \
                rank_str((x >> 4) & 15), rank_str(x & 15))
    if STR == c:
        return 'straight to the %s' % rank_str((x >> 24) & 15)
    if FLUSH == c:
        return 'flush (%s, %s, %s)' % \
                (rank_str((x >> 8) & 15), \
                rank_str((x >> 4) & 15), rank_str(x & 15))
    if TRIP == c:
        return 'trip %s\'s' % rank_str((x >> 24) & 15)
    if STRF == c:
        return 'straight flush to the %s' % rank_str((x >> 24) & 15)


def new_deck():
    d = []
    for i in range(SUITS):
        for j in range(RANKS):
            d.append(make_card(j, i))
    return d


def shuffle(d):
    random.shuffle(d)
    return d


def hand_value(h):
    "classify three card hand into uint32 that supports equality and greater than"
    ar = h[0] >> 3
    br = h[1] >> 3
    cr = h[2] >> 3
    ah = h[0] & 7
    bh = h[1] & 7
    ch = h[2] & 7
    if ar < br:
        if br < cr:
            h, m, l = cr, br, ar
        elif ar < cr:
            h, m, l = br, cr, ar
        else:
            h, m, l = br, ar, cr
    else:
        if ar < cr:
            h, m, l = cr, ar, br
        elif br < cr:
            h, m, l = ar, cr, br
        else:
            h, m, l = ar, br, cr
    if h == m:
        if m == l:
            x = (TRIP << 28) | (h << 24)
        else:
            x = (PAIR << 28) | (h << 24) | (h << 8) | (m << 4) | l
    elif m == l:
        x = (PAIR << 28) | (m << 24) | (h << 8) | (m << 4) | l
    elif (h == (m + 1)) and (h == (l + 2)):
        if (ah == bh) and (ah == ch):
            x = (STRF << 28) | (h << 24)
        else:
            x = (STR << 28) | (h << 24)
    elif (ah == bh) and (ah == ch):
        x = (FLUSH << 28) | (h << 8) | (m << 4) | l
    else:
        x = (HIGH << 28) | (h << 8) | (m << 4) | l
    return x


def best_hand_value(h):
    best = None
    for i in itertools.combinations(h, 3):
        x = hand_value(i)
        if None == best or x > best:
            best = x
    return best


class Player():
    pass


def call_player(player, args, default):
    global g_catch_exceptions
    result = default
    start = time.clock()
    try:
        result = player.play(*args)
    except KeyboardInterrupt:
        raise
    except:
        logging.warn('caught exception "%s" calling %s (%s)'
                     % (sys.exc_info()[1], player.player_id, player.playername))
        if not g_catch_exceptions:
            raise
    elapsed = time.clock() - start
    player.elapsed += elapsed
    player.calls += 1
    return result


def make_player(player_id, dirname):
    global g_catch_exceptions
    m = None
    try:
        name = 'bot'
        (f, filename, data) = imp.find_module(name, [dirname, ])
        m = imp.load_module(name, f, filename, data)
    except:
        logging.error('caught exception "%s" loading %s' % \
                      (sys.exc_info()[1], dirname))
        if not g_catch_exceptions:
            raise
    p = Player()
    p.player_id = player_id
    p.playername = dirname
    z = p.playername.rfind('/')
    if -1 != z:
        p.playername = p.playername[z + 1:]
    p.play = None
    if None == m or not hasattr(m, 'play'):
        logging.error('%s has no function "play"; ignoring ...' % filename)
    else:
        p.play = getattr(m, 'play')
    p.elapsed = 0.0
    p.calls = 0
    p.get_play = lambda x: call_player(p, (p.player_id, p.hand, x), 'F')
    return p


def serialize_history(history):
    t = ''
    for i in history:
        if 0 != len(t):
            t += ' '
        t += '%s:%s:%s' % (i[0], i[1], i[2])
    return t


def play_hand(players):
    """
    play a single hand of monkeystud
    """
    
    # sit
    #
    history = []
    random.shuffle(players)
    d = new_deck()
    random.shuffle(d)
    player_count = 0
    for seat, i in enumerate(players):
        if 0 == i.chips:
            i.folded = True
        else:
            player_count += 1
            i.hand = []
            i.paid = 0
            i.folded = False
            history.append((i.player_id, 'S', i.chips))
            logging.debug('ACTION\t%s sits down at seat %d' % (i.player_id, seat))

    # state machine
    #
    pot = 0
    for state in (0, 1, 2, 3, 4):

        # bail out early
        #
        if 1 == player_count:
            break

        # ante
        #
        if 0 == state:
            
            # ante is 1% of total chip count, or the 
            # lowest number of chips amongst active
            # players, whatever is lower
            #
            sum_chips = 0
            min_chips = None
            for i in players:
                if 0 == i.chips:
                    continue
                sum_chips += i.chips
                if None == min_chips or i.chips < min_chips:
                    min_chips = i.chips
            ante = min(min_chips, (sum_chips >> ANTE) // player_count)
            for i in players:
                if 0 == i.chips:
                    continue
                pot += ante
                i.chips -= ante
                i.paid += ante
                history.append((i.player_id, 'A', ante))
                logging.debug('ACTION\t%s antes %d' % (i.player_id, ante))

        # cards
        #
        if state in (1, 2, 3, 4):
            for i in players:
                if i.folded:
                    continue
                card = d.pop()
                i.hand.append(card)
                if 1 == state:
                    history.append((i.player_id, 'D', 'xx'))
                    logging.debug('ACTION\t%s is dealt %s down' % \
                            (i.player_id, card_str(card)))
                else:
                    history.append((i.player_id, 'U', card_str(card)))
                    logging.debug('ACTION\t%s is dealt %s up' % \
                            (i.player_id, card_str(card)))
    
        # betting rounds
        #
        if state in (2, 3, 4):

            # keep asking players for their bet until 
            # there's no new action
            #
            raised_to = 0
            for i in players:
                i.paid = 0
                i.played = False
            action = None
            last_action = None
            while 1:

                # advance the action
                #
                while 1:
                    if None == action:
                        action = 0
                    else:
                        action += 1
                        if action == len(players):
                            action = 0
                    if not players[action].folded:
                        break
                if action == last_action:
                    break
    
                # no new action?
                #
                if players[action].played and players[action].paid == raised_to:
                    break
                
                # get their play
                # 
                x = players[action].get_play(serialize_history(history))
                players[action].played = True

                # fold?
                #
                if 'F' == x:

                    # folding when there is no bet? make it a call
                    #
                    if players[action].paid == raised_to:
                        x = 'C'
                    else:
                        players[action].folded = True
                        history.append((players[action].player_id, 'F', 0))
                        logging.debug('ACTION\t%s folds' % players[action].player_id)
                        player_count -= 1
                        if 1 == player_count:
                            break
                
                # call?
                #
                if 'C' == x:
                    to_call = raised_to - players[action].paid
                    pot += to_call
                    players[action].paid += to_call
                    players[action].chips -= to_call
                    history.append((players[action].player_id, 'C', to_call))
                    logging.debug('ACTION\t%s calls %d' % \
                            (players[action].player_id, to_call))

                # bet?
                #
                if 'B' == x:
                    to_call = raised_to - players[action].paid
                    if 0 != to_call:
                        pot += to_call
                        players[action].paid += to_call
                        players[action].chips -= to_call
                        history.append((players[action].player_id, 'C', \
                                to_call))
                        logging.debug('ACTION\t%s calls %d' % \
                                (players[action].player_id, to_call))

                    # figure out the maximum raise
                    #
                    the_raise = pot
                    for i in players:
                        if i.folded:
                            continue
                        x = i.chips - (raised_to - i.paid)
                        if x < the_raise:
                            the_raise = x

                    if 0 != the_raise:
                        raised_to += the_raise
                        pot += the_raise
                        players[action].paid += the_raise
                        players[action].chips -= the_raise
                        history.append((players[action].player_id, 'B', \
                                the_raise))
                        logging.debug('ACTION\t%s bets %d' % \
                                (players[action].player_id, the_raise))
                        last_action = action

    # end of hand, figure out who won
    #
    remaining_players = []
    for i in players:
        if not i.folded:
            remaining_players.append(i)

    # only one player left?
    #
    if 1 == len(remaining_players):
        winners = remaining_players

    # nope, let's reveal and find the best hand
    #
    else:
        for i in remaining_players:
            history.append((i.player_id, 'R', hand_str(i.hand)))
            logging.debug('ACTION\t%s reveals %s -- %s' % (i.player_id, hand_str(i.hand), \
                          hand_value_str(best_hand_value(i.hand))))
        best_so_far = [0, []]
        for i in remaining_players:
            best_hand = best_hand_value(i.hand)
            if best_hand > best_so_far[0]:
                best_so_far = [best_hand, [i, ]]
            elif best_hand == best_so_far[0]:
                best_so_far[1].append(i)
        winners = best_so_far[1]

    # divide the pot
    #
    chips_per_winner = pot // len(winners)
    remainder = pot % len(winners)
    for i in winners:
        i.chips += chips_per_winner
        history.append((i.player_id, 'W', chips_per_winner))
        if 1 == len(winners):
            logging.debug('ACTION\t%s wins %d' % (i.player_id, chips_per_winner))
        else:
            logging.debug('ACTION\t%s wins %d in split' % (i.player_id, chips_per_winner))

    # give remainder to random winner
    #
    if 0 != remainder:
        lucky_player = random.choice(winners)
        lucky_player.chips += remainder
        history.append((lucky_player.player_id, 'Z', remainder))
        logging.debug('ACTION\t%s wins remainder %s' % \
                (lucky_player.player_id, remainder))

    # show everyone what happened
    #
    serialized_history = serialize_history(history)
    logging.debug('HISTORY\t%s' % serialized_history)
    for i in players:
        i.get_play(serialized_history)

    # all done.
    #
    return


def play_game(players):
    """
    play a game with chips, return winner
    """
    for i in players:
        i.chips = CHIPS_START
    while 1:
        t = ''
        winner = None
        for i in players:
            t += '%s:%s:%d ' % (i.player_id, i.playername, i.chips)
            if i.chips == (len(players) * CHIPS_START):
                winner = i
        logging.debug('CHIPS\t%s' % t)
        if None != winner:
            return winner
        play_hand(players)


def play_tournament(games, players):
    """
    play many games, return map of player_id to wins
    """
    for i in players:
        i.wins = 0
    if MAX_SEATS < len(players):
        tables = list(itertools.combinations(players, MAX_SEATS))
        games_per_table = games // len(tables)
    else:
        tables = [players, ]
        games_per_table = games
    n = games_per_table * len(tables)
    game_num = 0
    for table in tables:
        for i in range(games_per_table):
            winner = play_game(table)
            winner.wins += 1
            t = ''
            players.sort(key = lambda x : x.wins,reverse = True)
            for j in players:
                t += '%s:%d\t' % (j.playername, j.wins)
            game_num += 1
            logging.info('BOTFIGHT\t%d\t%d\t%s' % (game_num, n, t))


def verify_player(playername):
    global g_catch_exceptions
    g_catch_exceptions = True
    logging.info('verifying %s ...' % playername)
    if EXPECTED_PYTHON_VERSION != sys.version_info[:2]:
        logging.info('verification FAILED. wrong python version.')
        return 2
    p1 = make_player(1, playername)
    if None == p1.play:
        logging.info('verification FAILED. import failed.')
        return 3
    p2 = make_player(2, 'p_random')
    logging.info('playing 100 games against random ...')
    play_tournament(100, [p1, p2])
    logging.info('%s: %f seconds, %d calls' % (playername, p1.elapsed, p1.calls))
    logging.info('random: %f seconds, %d calls' % (p2.elapsed, p2.calls))
    factor = (p1.elapsed / p1.calls) / (p2.elapsed / p2.calls)
    logging.info('player is %.1fx slower than random' % factor)
    if g_max_time < factor:
        logging.info('verification FAILED. max_time is %.1f.' % g_max_time)
        return 1
    logging.info('verification success.')
    return 0


def usage():
    print('''\
monkeystud! see: http://github.com/botfights/monkeystud for dox

usage:

    $ python monkeystud.py <command> [<option> ...] [<arg> ...]

commands:

    human [<opponent1>] [<oppponent2>] ... 
                        
                        play against the computer

    game [<player1>] [<player2>] ...

                        play a single game between players

    tournament [<player1>] [<player2>] ...

                        play a tournament between players
options:
 
    -h, --help                      show this help
    --seed=<s>                      set seed for random number generator
    --catch-exceptions=<off|on>     catch and log exceptions
    --num-games=<n>                 set number of games for tournament
    --log-level=<n>                 set log level (10 debug, 20 info, 40 error)
    --max-time=<f>                  max time relative to p_random a bot can take
    --verify=<off|on>               verify bots before fight
''')


def main(argv):
    if 1 > len(argv):
        usage()
        sys.exit()
    command = argv[0]
    try:
        opts, args = getopt.getopt(argv[1:], "h", [
                                                    "help",
                                                    "seed=",
                                                    "catch-exceptions=",
                                                    "num-games=",
                                                    "log-level=",
                                                    "max-time=",
                                                    "verify=",
                                                    ])
    except getopt.GetoptError as err:
        print(str(err))
        usage()
        sys.exit(1)
    seed = time.time()
    num_games = 1000
    log_level = logging.DEBUG
    global g_catch_exceptions
    global g_max_time
    g_catch_exceptions = False
    verify_players = False
    for o, a in opts:
        if 0:
            pass
        elif o in ("-h", "--help"):
            usage()
            sys.exit()
        elif o in ("--seed", ):
            seed = a
        elif o in ("--num-games", ):
            num_games = int(a)
        elif o in ("--log-level", ):
            log_level = int(a)
        elif o in ("--max-time", ):
            g_max_time = float(a)
        elif o in ("--catch-exceptions", ):
            g_catch_exceptions = 'off' != a
        elif o in ("--verify", ):
            verify_players = 'off' != a
        else:
            raise Exception("unhandled option")
    random.seed(seed)
    
    if 0:
        pass
 
    elif 'human' == command:
        logging.basicConfig(level=logging.INFO, format='%(message)s', 
                        stream=sys.stdout)
 

        players = [make_player('human', 'p_human'), ]
        if 0 == len(args):
            players.append(make_player('computer', 'p_computer'))
        else:
            for i in args:
                players.append(make_player(i, i))
        winner = play_game(players)
        sys.exit()

    elif 'game' == command:
        logging.basicConfig(level=log_level, format='%(message)s', 
                        stream=sys.stdout)
        players = []
        for player_id, playername in enumerate(args):
            if verify_players:
                if 0 != verify_player(playername):
                    continue
            players.append(make_player(chr(ord('a') + player_id), playername))
        winner = play_game(players)
        sys.exit()

    elif 'tournament' == command:
        logging.basicConfig(level=log_level, format='%(message)s', 
                        stream=sys.stdout)
        players = []
        for player_id, playername in enumerate(args):
            if verify_players:
                if 0 != verify_player(playername):
                    continue
            players.append(make_player(chr(ord('a') + player_id), playername))
        play_tournament(num_games, players)
        sys.exit()

    elif 'verify' == command:
        logging.basicConfig(level=logging.DEBUG, format='%(message)s', 
                        stream=sys.stdout)
        result = verify_player(args[0])
        sys.exit(result)

    else:
        print 'i don\'t know how to "%s".' % command
        usage()
        sys.exit()


if __name__ == '__main__':
    main(sys.argv[1:])
