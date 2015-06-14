# monkeystud.py -- MonkeyStud, poker variant

# see README.md for more dox

import random, sys, itertools, logging, imp, time, itertools


CHIPS_START = 100               # each player starts with 100 chips
ANTE        = (1, 100)          # ante is 1% total chip count each

RANKS       = 8                 # duece through nine
SUITS       = 4                 # clubs, diamonds, hearts, spades

HIGH        = 0                 # high card
PAIR        = 1                 # one pair
STR         = 2                 # straight
FLUSH       = 3                 # flush
TRIP        = 4                 # three of a kind
STRF        = 5                 # straight flush


g_catch_exceptions = False


def make_card(r, s):
    return (r << 3) | s


def rank_suit(c):
    return c >> 3, c & 7


def card_str(a):
    return "%s%s" % ('?23456789TJQKABC'[a >> 3], 'cdhswxyz'[a & 7])


def hand_str(h):
    return ','.join(map(lambda x : card_str(x), h))


def new_deck():
    d = []
    for i in range(SUITS):
        for j in range(1, RANKS + 1):
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
            x = (cr << 20) | (br << 16) | (ar << 12) | \
                (ch << 8)  | (bh << 4)  | (ah)
        elif ar < cr:
            h, m, l = br, cr, ar
            x = (br << 20) | (cr << 16) | (ar << 12) | \
                (bh << 8)  | (ch << 4)  | (ah)
        else:
            h, m, l = br, ar, cr
            x = (br << 20) | (ar << 16) | (cr << 12) | \
                (bh << 8)  | (ah << 4)  | (ch)
    else:
        if ar < cr:
            h, m, l = cr, ar, br
            x = (cr << 20) | (ar << 16) | (br << 12) | \
                (ch << 8)  | (ah << 4)  | (bh)
        elif br < cr:
            h, m, l = ar, cr, br
            x = (ar << 20) | (cr << 16) | (br << 12) | \
                (ah << 8)  | (ch << 4)  | (bh)
        else:
            h, m, l = ar, br, cr
            x = (ar << 20) | (br << 16) | (cr << 12) | \
                (ah << 8)  | (bh << 4)  | (ch)
    if 0:
        pass
    elif h == m:
        if m == l:
            x |= (TRIP << 28)
        else:
            x |= (PAIR << 28) | (h << 24)
    elif m == l:
        x |= (PAIR << 28) | (m << 24)
    elif (h == (m + 1)) and (h == (l + 2)):
        if (ah == bh) and (ah == ch):
            x |= (STRF << 28)
        else:
            x |= (STR << 28)
    elif (ah == bh) and (ah == ch):
        x |= (FLUSH << 28)
    else:
        x |= (HIGH << 28)
    return x


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
    p.get_play = lambda x: call_player(p, (p.player_id, p.hand, x), 'F')
    return p


def serialize_history(history):
    t = ''
    for i in history:
        if 0 != len(t):
            t += ' '
        t += '%s:%s:%s' % (i[0], i[1], i[2])
    return t


def play_hand(players, dealer):
    """
    play a single hand of monkeystud
    """
    
    # sit
    #
    history = []
    random.shuffle(players)
    d = new_deck()
    random.shuffle(d)
    for seat, i in enumerate(players):
        i.hand = []
        i.paid = 0
        i.folded = False
        history.append((i.player_id, 'S', seat))

    # state machine
    #
    pot = 0
    raised_to = 0
    for state in (0, 1, 2, 3, 4):

        # ante
        #
        if 0 == state:
            
            # ante is 1% of total chip count, or the 
            # lowest number of chips amongst active
            # players, whatever is lower
            #
            sum_chips = 0
            min_chips = players[0].chips
            for i in players:
                sum_chips += i.chips
                if i.chips < min_chips:
                    min_chips = i.chips
            ante = min(min_chips, (sum_chips * ANTE[0]) // ANTE[1])
            raised_to = ante
            for i in players:
                pot += ante
                i.chips -= ante
                i.paid += ante
                history.append((i.player_id, 'A', ante))

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
                else:
                    history.append((i.player_id, 'U', card_str(card)))
    
        # betting rounds
        #
        if state in (2, 3, 4):

            # keep asking players for their bet until 
            # there's no new action
            #
            action = None
            while 1:

                # advance the action
                #
                last_action = None
                while 1:
                    if None == action:
                        action = 0
                    else:
                        action += 1
                        if action == len(players):
                            action = 0
                    if not players[i].folded:
                        break
                if action == last_action:
                    break

                # figure out the max bet
                #
                max_bet = pot
                for i in players:
                    if i.folded:
                        continue
                    if 0 == i.chips:
                        continue
                    if i.chips < max_bet:
                        max_bet = i.chips

                # get their play
                # 
                x = i.get_play(serialize_history(history))

                # fold?
                #
                if 'F' == x:

                    # folding when there is no bet? make it a call
                    #
                    if i.paid == raised_to:
                        x = 'C'
                    else:
                        i.folded = True
                        history.append((i.player_id, 'F', None))
                
                # call?
                #
                if 'C' == x:
                    if i.paid < raised_to:
                        to_call = raised_to - i.paid
                        pot += to_call
                        i.paid += to_call
                        i.chips -= to_call
                        history.append((i.player_id, 'C', to_call))

                # bet?
                #
                if 'B' == x:
                    raised_to += max_bet
                    pot += max_bet
                    i.paid += max_bet
                    i.chops -= to_call
                    history.append((i.player_id, 'B', max_bet))

    # end of hand, figure out who won
    #
    remaining_players = []
    for i in players:
        if not i.folded:
            remaining_players.append(i)

    # reveal cards?
    #
    if 1 != len(remaining_players):
        for i in remaining_players:
            history.append((i.player_id, 'R', hand_str(i.hand)))
    
    # find the winner(s)
    #
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

    # give remainder to random winner
    #
    if 0 != remainder:
        lucky_player = random.choice(winners)
        lucky_player.chips += remainder
        history.append((i.player_id, 'Z', remainder))

    # show everyone what happened
    #
    for i in players:
        i.get_play(serialize_history(history))

    # all done.
    #
    return


def play_game(players):
    """
    play a game with chips, return winner
    """
    entrants = []
    for i in players:
        i.chips = CHIPS_START
        entrants.append(i)
    while 1:
        active_players = []
        for i in entrants:
            if i.chips > 0:
                active_players.append(i)
        if 1 == len(active_players):
            return active_players[0]
        play_hand(active_players)


def play_tournament(games, players):
    """
    play many games, return map of player_id to wins
    """
    wins = {}
    for i in range(games):
        winner = play_game(players)
        if not wins.has_key(winner.player_id):
            wins[winner.player_id] = 0
        wins[winner.player_id] += 1
    return wins


if __name__ == '__main__':

    c = sys.argv[1]
    
    if 0:
        pass
    
    elif 'game' == c:
        logging.basicConfig(level=logging.INFO, 
                            format='%(message)s', stream=sys.stdout)
        playernames = sys.argv[2:]
        players = []
        for player_id, playername in enumerate(playernames):
            players.append(make_player(chr(ord('a') + player_id), playername))
        winner = play_game(players)
        sys.exit()

    elif 'tournament' == c:
        global g_catch_exceptions
        g_catch_exceptions = True
        logging.basicConfig(level=logging.INFO, 
                            format='%(message)s', stream=sys.stdout)
        games = int(sys.argv[2])
        playernames = sys.argv[3:]
        players = []
        for player_id, playername in enumerate(playernames):
            players.append(make_player(player_id, playername))
        wins = play_tournament(games, players)
        sys.exit()

    elif 'time' == c:
        playername = sys.argv[3]
        p1 = make_player(1, playername)
        p2 = make_player(1, 'p_random')
        print('playing 100 games against random ...')
        play_tournament(100, players)
        print('random: %f seconds, %s: %f seconds; %s is %.2fx slower' \
                % (p1.elapsed, p2.elapsed, p2 / p1))
        sys.exit()

