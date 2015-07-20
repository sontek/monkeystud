# p_example.py -- example bot

import random
import monkeystud


class Game:
    pass


class Player:
    pass


def parse_history(history):
    g = Game()
    g.players = {}
    g.pot = 0
    g.player_count = 0
    for i in history.split():
        player_id, code, x = i.split(':')
        if not g.players.has_key(player_id):
            p = Player()
            p.seat = len(g.players)
            p.player_id = player_id
            p.chips = 0
            p.bet = 0
            p.hand = []
            p.history = []
            p.folded = True
            g.players[player_id] = p
     	g.players[player_id].history.append((code, x))
        if 0:
            pass
        elif 'S' == code:
            p.chips = int(x)
            g.player_count += 1
            pass
        elif 'A' == code:
            g.pot += int(x)
            g.players[player_id].chips -= int(x)
            g.players[player_id].bet += int(x)
        elif 'D' == code:
            g.players[player_id].hand.append(monkeystud.INVALID_CARD)
        elif 'U' == code:
            g.players[player_id].hand.append(monkeystud.str_to_card(x))
        elif 'C' == code:
            pass
        elif 'F' == code:
            g.players[player_id].folded = True
            g.player_count -= 1
        elif 'B' == code:
            g.players[player_id].bet += int(x)
        elif 'R' == code:
            hand = monkeystud.str_to_hand(x)
            g.players[player_id].cards = hand
            g.players[player_id].best_hand = monkeystud.best_hand_value(hand)
        elif 'W' == code:
            g.players[player_id].chips += int(x)
        elif 'Z' == code:
            g.players[player_id].chips += int(x)

    return g


def play(player_id, hand, history):
 
    # parse the history into something more friendly ...
    #
    g = parse_history(history)

    # TODO: do stuff with g here ...

    # just two cards? call any pair, fold otherwise
    #
    if 2 == len(hand):
        rank0, suit0 = monkeystud.rank_suit(hand[0])
        rank1, suit1 = monkeystud.rank_suit(hand[1])
        if rank0 == rank1:
            return 'C'
        return 'F'

    # three cards? bet on a flush or better, call on a pair or straight,
    # fold otherwise
    #
    if 3 == len(hand):
        v = monkeystud.hand_value(hand)
        c = monkeystud.hand_value_class(v) 
        if c in (monkeystud.FLUSH, monkeystud.TRIP, monkeystud.STRF):
            return 'B'
        if c in (monkeystud.PAIR, monkeystud.STR):
            return 'C'
        return 'F'

    # four cards? bet on trips or straight flush, call on a straight or flush, 
    # fold otherwise
    #
    if 4 == len(hand):
        v = monkeystud.best_hand_value(hand)
        c = monkeystud.hand_value_class(v)
        if c in (monkeystud.TRIP, monkeystud.STRF):
            return 'B'
        if c in (monkeystud.STR, monkeystud.FLUSH):
            return 'C'
        return 'F'

