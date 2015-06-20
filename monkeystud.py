# monkeystud.py -- MonkeyStud, a poker variant for bots

# see README.md for more dox

import os, random, sys, itertools, logging, imp, time, itertools


CHIPS_START    = 1024              # each player starts with 1024 chips
ANTE           = 6                 # ante is 1 / 64th total chip count each
MAX_SEATS      = 8                 # maximum seats at a table

RANKS          = 8                 # duece through nine
SUITS          = 4                 # clubs, diamonds, hearts, spades
INVALID_CARD   = 17 << 3
HIGH           = 0                 # high card
PAIR           = 1                 # one pair
STR            = 2                 # straight
FLUSH          = 3                 # flush
TRIP           = 4                 # three of a kind
STRF           = 5                 # straight flush


g_catch_exceptions = False


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


def classification_str(x):
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


def classify_hand(a, b, c):
    "classify three card hand into a uint32 that obeys cardinality"
    x = 0
    ar = a >> 3
    br = b >> 3
    cr = c >> 3
    ah = a & 7
    bh = b & 7
    ch = c & 7
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
    if 0:
        pass
    elif h == m:
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


def find_best_hand(h):
    best = None
    for i in itertools.combinations(h, 3):
        x = classify_hand(i[0], i[1], i[2])
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


def make_player(player_id, playername):
    fp = pathname = description = m = None
    try:
        fp, pathname, description = imp.find_module(playername)
    except:
        logging.warn('caught exception "%s" finding module %s'
                     % (sys.exc_info()[1], playername))
        raise
    try:
        if fp:
            m = imp.load_module(playername, fp, pathname, description)
    except:
        logging.warn('caught exception "%s" importing %s'
                     % (sys.exc_info()[1], playername))
        raise
    finally:
        if fp:
            fp.close()
    if None == m:
        return None
    p = Player()
    p.player_id = player_id
    p.playername = playername
    p.play = None
    if hasattr(m, 'play'):
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
                        history.append((players[action].player_id, 'F', None))
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
                          classification_str(find_best_hand(i.hand))))
        best_so_far = [0, []]
        for i in remaining_players:
            best_hand = find_best_hand(i.hand)
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
        logging.info('CHIPS\t%s' % t)
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
    for table in tables:
        for i in range(games_per_table):
            winner = play_game(table)
            winner.wins += 1
            t = ''
            players.sort(key = lambda x : x.wins,reverse = True)
            for j in players:
                t += '%s:%s:%d ' % (j.player_id, j.playername, j.wins)
            logging.info('WINS\t%s' % t)


def main(argv):

    random.seed(os.environ.get('SEED', time.time()))
    c = argv[1]
    
    if 0:
        pass
 
    elif 'human' == c:
        players = [make_player('human', 'p_human'), ]
        if 2 == len(argv):
            players.append(make_player('computer', 'p_computer'))
        else:
            for i in argv[2:]:
                players.append(make_player(i, i))
        winner = play_game(players)
        sys.exit()

    elif 'game' == c:
        logging.basicConfig(level=logging.DEBUG, 
                            format='%(message)s', stream=sys.stdout)
        playernames = argv[2:]
        players = []
        for player_id, playername in enumerate(playernames):
            players.append(make_player(chr(ord('a') + player_id), playername))
        winner = play_game(players)
        sys.exit()

    elif 'tournament' == c:
        global g_catch_exceptions
        g_catch_exceptions = True
        logging.basicConfig(level=logging.DEBUG, 
                            format='%(message)s', stream=sys.stdout)
        games = int(argv[2])
        playernames = argv[3:]
        players = []
        for player_id, playername in enumerate(playernames):
            players.append(make_player(chr(ord('a') + player_id), playername))
        play_tournament(games, players)
        sys.exit()

    elif 'time' == c:
        playername = argv[2]
        p1 = make_player(1, playername)
        p2 = make_player(2, 'p_random')
        print('playing 100 games against random ...')
        play_tournament(100, [p1, p2])
        print('player: %f seconds, %d calls, %f per call' % \
                (p1.elapsed, p1.calls, p1.elapsed / p1.calls))
        print('random: %f seconds, %d calls, %f per call' % \
                (p2.elapsed, p2.calls, p2.elapsed / p2.calls))
        sys.exit()

    elif 'deck' == c:
        d = new_deck()
        for i in d:
            print '%d\t%s' % (i, card_str(i))

    elif 'hands' == c:
        for a in new_deck():
            for b in new_deck():
                if b <= a:
                    continue
                for c in new_deck():
                    if c <= b:
                        continue
                    x = classify_hand(a, b, c)
                    print 'HAND\t%s\t%d\t%s' % (hand_str((a, b, c)), \
                            x >> 28, classification_str(x)) 
 
    elif 'hands4' == c:
        for a in new_deck():
            for b in new_deck():
                if b <= a:
                    continue
                for c in new_deck():
                    if c <= b:
                        continue
                    for d in new_deck():
                        if d <= c:
                            continue
                        h = (a, b, c, d)
                        x = find_best_hand(h)
                        print 'HAND\t%s\t%d\t%s' % (hand_str(h), \
                                x >> 28, classification_str(x)) 


    elif 'best' == c:
        for i in range(int(sys.argv[2])):
            d = new_deck()
            random.shuffle(d)
            best = [0, 0]
            for j in range(int(sys.argv[3])):
                h = d[:4]
                d = d[4:]
                x = find_best_hand(h)
                if x == best[0]:
                    best[1] += 1
                elif x > best[0]:
                    best = [x, 0]
            print 'HAND\t%d\t%d\t%s' % (best[1], best[0] >> 28, \
                                classification_str(best[0])) 


if __name__ == '__main__':
    main(sys.argv)
