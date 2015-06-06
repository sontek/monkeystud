# mhe.py -- Monkey Hold 'em, a poker variant

import random, sys, itertools

RANKS   = 8
SUITS   = 4

HIGH    = 0
PAIR    = 1
STR     = 2
FLUSH   = 3
TRIP    = 4
STRF    = 5


def call_player(player, foo, args, default, catch_exceptions):
    result = default
    start = time.clock()
    try:
        result = foo(*args)
    except KeyboardInterrupt:
        raise
    except:
        if not catch_exceptions:
            raise
        logging.warn('caught exception "%s" calling %s'
                     % (sys.exc_info()[1], player[1]))
    elapsed = time.clock() - start
    player[4] += elapsed
    return result


def make_player(player_id, playername, catch_exceptions):
    fp = pathname = description = m = None
    try:
        fp, pathname, description = imp.find_module(playername)
    except:
        if not catch_exceptions:
            raise
        logging.warn('caught exception "%s" finding module %s'
                     % (sys.exc_info()[1], playername))
    try:
        if fp:
            m = imp.load_module(playername, fp, pathname, description)
    except:
        if not catch_exceptions:
            raise
        logging.warn('caught exception "%s" importing %s'
                     % (sys.exc_info()[1], playername))
    finally:
        if fp:
            fp.close()
    if None == m:
        return None
    f_play = None
    if hasattr(m, 'play'):
        f_play = getattr(m, 'play')
    f_observe = None
    if hasattr(m, 'observe'):
        f_observe = getattr(m, 'observe')
    return [player_id, playername, f_play, f_observe, 0.0]


def make_card(r, s):
    return (r << 3) | s


def rank_suit(c):
    return c >> 3, c & 7


def card_str(a):
    return "%0X%s" % (((a + 1) >> 3), 'cdhswxyz'[a & 7])


def hand_str(h):
    return ' '.join(map(lambda x : card_str(x), h))


def new_deck():
    d = []
    for i in range(SUITS):
        for j in range(1, RANKS + 1):
            d.append(make_card(j, i))
    return d


def classify_hand3(a, b, c):
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


def best_hand3(h):
    "find best three card hand in array of cards"
    best = None
    for i in itertools.combinations(h, 3):
        x = classify_hand3(*i)
        if None == best or x > best:
            best = x
    return x


def bet(player, stack, to_call, catch):
    x = call_player(player, player[2], (player[0], stack, to_call), 0, catch)
    return x


def observe(players, action, player_id, argument, catch):
    for i in players:
        call_player(i, i[2], (i[0], action, player_id, argument), None, catch)


def play_hand(players, catch):
    """
    players is a list of:
        [player_id, player_name, bet(), observe(), chips]
    shuffle seats, play a hand, update chips
    """
    
    # sit
    #
    for i in players:
        observe(players, 'S', i[0], i[4], catch)

    # ante
    #
    pot = 0
    n = 0
    for i in players:
        n += 1
        x = math.ceil(i[4] >> n)
        i[4] -= x
        pot += x
        observe(players, 'A', i[0], x, catch)

        # not folded yet
        #
        i.append(False)

    # deal hole cards
    #
    d = new_deck()
    random.shuffle(d)
    for i in players:
        hole = d.pop()
        i.append(hole)
        observe(players, 'D', i[0], 0, catch)
        observe((i, ), 'H', i[0], hole, catch)
    
    # betting rounds
    #
    community = []
    for i in ('D', 'F', 'T', 'R'):

        # first deal the community card
        #
        if i in ('F', 'T', 'R'):
            c = d.pop()
            community.append(c)
            observe(players, 'C', None, c, catch)

        # next, betting round, repeat until nothing left to call
        #
        to_call = 0
        while 1:
            for i in players:

                # folded, or all in? just continue
                #
                if i[5] or 0 == i[4]:
                    continue

                # get their bet
                #
                x = bet(i, i[4], pot, to_call)
                if x < to_call:
                    x = 0
                if x > i[4]:
                    x = i[4]

                # all in?
                #
                if 0 == i[4] and False == i[5]:
                    # TODO:
                    pass 

                # fold?
                #
                elif x < to_call:
                    observe(players, 'F', i[0], None, catch)
                    i[5] = True

                # nope, bet
                #
                else:
                    observe(players, 'B', i[0], x, catch)
                    pot += x
                    i[4] -= x
                    
        if 0 == to_call:
            break

    # reveal
    #
    for i in players:
        if False == i[5]:
            observe(players, 'R', i[0], i[6])

    # walk pots and pay people
    #
    # TODO:

    return


def play_game(players, chips, catch):
    """
    players is a list of:
        (player_id, player_name, bet(), observe())
    return player_id of winner
    """
    entrants = []
    for i in players:
        entrants.append([i[0], i[1], i[2], i[3], chips])
    while 1:
        active_players = []
        for i in entrants.values()
            if i[4] > 0:
                active_players.append([i[0], i[1], i[2], i[3], chips])
        if 1 == len(active_players):
            return active_players[0][0]
        random.shuffle(active_players)
        play_hand(active_players, catch)


def play_tournament(players, chips, games, catch):
    """
    players is a list of:
        [player_id, player_name, bet(), observe()]
    return a map of player_id to wins
    """
    wins = {}
    for i in range(games):
        winner = play_game(players, chips, catch)
        if not wins.has_key(winner):
            wins[winner] = 0
        wins[winner] += 1
    return wins


if __name__ == '__main__':

    c = sys.argv[1]
    
    if 0:
        pass
    
    elif 'game' == c:
        logging.basicConfig(level=logging.INFO, 
                            format='%(message)s', stream=sys.stdout)
        chips = int(sys.argv[2])
        playernames = sys.argv[3:]
        players = []
        for player_id, playername in enumerate(playernames):
            players.append(make_player(player_id, playername, True))
        winner = play_game(players, chips, False)
        sys.exit()

    elif 'tournament' == c:
        logging.basicConfig(level=logging.INFO, 
                            format='%(message)s', stream=sys.stdout)
        games = int(sys.argv[2])
        chips = int(sys.argv[3])
        playernames = sys.argv[4:]
        players = []
        for player_id, playername in enumerate(playernames):
            players.append(make_player(player_id, playername, False))
        wins = play_tournament(players, chips, games, True)
        sys.exit()

