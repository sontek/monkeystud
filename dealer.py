# dealer.py -- MonkeyStud dealer

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
    shuffle seats, play a hand, update chips
    """
    
    # sit
    #
    random.shuffle(players)
    d = mhe.new_deck()
    random.shuffle(d)
    for i in players:
        dealer.observe(players, 'S', i.player_id, i.chips)
        i.hand = []
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
            players.append(make_player(chr(ord('a') + player_id), playername, \
                    False))
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

