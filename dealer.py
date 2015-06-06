# dealer.py -- Monkey Hold 'em dealer

# see README.md for more dox

import random, sys, itertools, logging, imp, time

import mhe


class Player():
    pass


class Dealer():
    pass


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
        logging.warn('caught exception "%s" calling %s (%s)'
                     % (sys.exc_info()[1], player.player_id, player.playername))
    elapsed = time.clock() - start
    player.elapsed += elapsed
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

    p = Player()
    p.player_id = player_id
    p.playername = playername

    p.f_bet = None
    if hasattr(m, 'bet'):
        p.f_bet = getattr(m, 'bet')
    p.f_observe = None
    if hasattr(m, 'observe'):
        p.f_observe = getattr(m, 'observe')
    p.elapsed = 0.0
    return p


def bet(player, stack, to_call, catch):
    x = call_player(player, player.f_bet, (stack, to_call), 0, catch)
    return x


def observe(players, action, player_id, argument, catch):
    for i in players:
        if None == i.f_observe:
            continue
        call_player(i, i.f_observe, 
                    (i.player_id, action, player_id, argument), None, catch)


def play_hand(players, dealer):
    """
    players is a list of:
        [player_id, player_name, bet(), observe(), chips]
    shuffle seats, play a hand, update chips
    """
    
    # sit
    #
    players_in_hand = {}
    player_map = {}
    paid_in = {}
    for i in players:
        dealer.observe(players, 'S', i.player_id, i.chips)
        players_in_hand[i.player_id] = 1
        player_map[i.player_id] = i

    # blind
    #
    pots = []
    pots.append([players_in_hand.keys(), 0])
    blind = players[0].chips // 2
    players[0].chips -= blind
    pots[-1][1] += blind
    paid_in[players[0].player_id] = blind
    dealer.observe(players, 'A', players[0].player_id, blind)

    # deal hole cards
    #
    d = mhe.new_deck()
    random.shuffle(d)
    for i in players:
        hole = d.pop()
        i.hole = hole
        dealer.observe(players, 'D', i.player_id, 0)
        dealer.observe((i, ), 'H', i.player_id, hole)
    
    # betting rounds
    #
    community = []
    for i in ('D', 'F', 'T', 'R'):

        # all done?
        # 
        if 1 == len(players_in_hand):
            break

        # first deal the community card
        #
        if i in ('F', 'T', 'R'):
            c = d.pop()
            community.append(c)
            dealer.observe(players, 'C', None, c)

        # next, betting round, repeat until nothing left to call
        #
        raised_to = blind
        last_raise = None
        action = 0
        while 1 < len(players_in_hand):

            # advance action
            #
            while 1:
                action += 1
                if action == len(players):
                    action = 0
                if players[action].player_id in players_in_hand:
                    break
            player = players[action]

            # all done?
            #
            if last_raise == player.player_id:
                break
            if None == last_raise:
                last_raise = player.player_id

            # get their bet
            #
            player_paid_in = paid_in.get(player.player_id, 0)
            to_call = raised_to - player_paid_in
            x = dealer.bet(player, player.chips, to_call)
            if x == player.chips:
                pass
            elif x < to_call:
                x = 0
            elif x > player.chips:
                x = player.chips
            paid_in[player.player_id] = player_paid_in + x

            # all in?
            #
            if x == player.chips:
                del players_in_hand[player.player_id]
                dealer.observe(players, 'I', player.player_id, x)
                pots[-1][1] += x
                player.chips -= x
                pots.append([players_in_hand.keys(), 0])

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


def play_game(players, chips, dealer):
    """
    play a game with chips, return winner
    """
    entrants = []
    for i in players:
        i.chips = chips
        entrants.append(i)
    while 1:
        active_players = []
        for i in entrants:
            if i.chips > 0:
                active_players.append(i)
        if 1 == len(active_players):
            return active_players[0]
        random.shuffle(active_players)
        play_hand(active_players, dealer)


def play_tournament(players, chips, games, dealer):
    """
    play many games, return map of player_id to wins
    """
    wins = {}
    for i in range(games):
        winner = play_game(players, chips, dealer)
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
        chips = int(sys.argv[2])
        playernames = sys.argv[3:]
        players = []
        for player_id, playername in enumerate(playernames):
            players.append(make_player(chr(ord('a') + player_id), playername, False))
        d = Dealer()
        d.observe = lambda w, x, y, z: observe(w, x, y, z, False)
        d.bet = lambda x, y, z: bet(x, y, z, False)
        winner = play_game(players, chips, d)
        sys.exit()

    elif 'tournament' == c:
        logging.basicConfig(level=logging.INFO, 
                            format='%(message)s', stream=sys.stdout)
        games = int(sys.argv[2])
        chips = int(sys.argv[3])
        playernames = sys.argv[4:]
        players = []
        for player_id, playername in enumerate(playernames):
            players.append(make_player(player_id, playername, True))
        d = Dealer()
        d.observe = lambda w, x, y, z: observe(w, x, y, z, True)
        d.bet = lambda x, y, z: bet(x, y, z, True)
        wins = play_tournament(players, chips, games, d)
        sys.exit()

