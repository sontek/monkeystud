# dealer.py -- MonkeyStud dealer

# see README.md for more dox

import random, sys, itertools, logging, imp, time, itertools


CHIPS_START = 100
ANTE        = (1, 100)

RANKS       = 8
SUITS       = 4

HIGH        = 0
PAIR        = 1
STR         = 2
FLUSH       = 3
TRIP        = 4
STRF        = 5


def make_card(r, s):
    return (r << 3) | s


def rank_suit(c):
    return c >> 3, c & 7


def card_str(a):
    return "%s%s" % ('?23456789TJQKABC'[a >> 3], 'cdhswxyz'[a & 7])


def hand_str(h):
    return ' '.join(map(lambda x : card_str(x), h))


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


g_catch_exceptions = False


def call_player(player, args, default):
    global g_catch_exceptions
    result = default
    start = time.clock()
    try:
        result = player.foo(*args)
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
    p.get_bet = lambda x, y, z: call_player(p, (p.player_id, p.hand), 'F')
    return p


def play_hand(players, dealer):
    """
    shuffle seats, play a hand, update chips
    """
    
    # sit
    #
    d = new_deck()
    random.shuffle(d)
    for i in players:
        i.hand = None
        i.paid = 0
        i.folded = False

    # state machine
    #
    pot = 0
    raised_to = 0
    for state in ('D', 'U', 'B', 'U', 'B'):

        if 0:
            pass

        # ante
        #
        elif 'A' == state:
            
            # ante is minimum of players' chip counts and 
            # sum of chips / number of players
            #
            sum_chips = 0
            min_chips = players[0].chips
            for i in players:
                sum_chips += i.chips
                if i.chips < min_chips:
                    min_chips = i.chips
            ante = min(min_chips, sum_chips / (2 * len(players)))
            raised_to = ante
            for i in players:
                pot += ante
                i.chips -= ante
                i.paid += ante
                dealer.observe(players, 'A', i.player_id, ante)

        # hole card
        #
        elif 'D' == state:
            for i in players:
                if i.folded:
                    continue
                card = d.pop()
                i.hand.append(card)
                dealer.observe(players, 'D', i.player_id, 0)
                dealer.observe((i, ), 'H', i.player_id, card)

        # face up
        #
        elif 'U' == state:
            for i in players:
                if i.folded:
                    continue
                card = d.pop()
                i.hand.append(card)
                dealer.observe(players, 'U', i.player_id, card)
    
        # betting round
        #
        elif 'B' == state:

            while 1:

                for i in players:
                    if i.folded:
                        continue
                    if 0 == i.chips:
                        continue
                    

            max_bet = 0
            for i in players:
                if i.folded
                    continue
                if None == max_bet or i.chips < max_bet:
                    max_bet = i.chips
            

            # fold?
            #
            elif x < to_call:
                del players_in_hand[player.player_id]
                dealer.observe(players, 'F', player.player_id, None)

            # nope, bet
            #
            else:
                dealer.observe(players, 'B', player.player_id, x)
                pots[-1][1] += x
                player.chips -= x
                if x > to_call:
                    raised_to += to_call - x
                    last_raise = player.player_id
                
    # walk pots, reveal cards if more than one player left, and pay people
    #
    for pot in pots:

        if 1 == len(pot[0]):
            winners = pot[0]
        else:

            # find winner(s)
            #
            best = [0, []]
            for i in pot[0]:
                player = player_map[i]
                dealer.observe(players, 'R', player.player_id, player.hole)
                player_hand = mhe.best_hand3(community + [player.hole, ])
                if player_hand > best[0]:
                    best = [player_hand, [i, ]]
                elif player_hand == best[0]:
                    best[1].append(i)
            winners = best[1]

        # divide the pot
        #
        chips_per_winner = pot[1] // len(winners)
        remainder = pot[1] % len(winners)
        for i in winners:
            player = player_map[i]
            dealer.observe(players, 'W', player.player_id, chips_per_winner)
            player.chips += chips_per_winner

        # give remainder to random winner
        #
        if 0 != remainder:
            player = player_map[random.choice(winners)]
            dealer.observe(players, 'W', player.player_id, remainder)
            player.chips += remainder

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
        random.shuffle(active_players)
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

