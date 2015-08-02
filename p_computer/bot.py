# p_computer.py -- just look at my hand, don't remember anything

from monkeystud import rank_suit, hand_value, best_hand_value, hand_value_class
from monkeystud import PAIR, STR, FLUSH, TRIP, STRF


def play(player_id, hand, history):

    # just two cards? call on any pair or matched suits, fold otherwise
    #
    if 2 == len(hand):
        rank0, suit0 = rank_suit(hand[0])
        rank1, suit1 = rank_suit(hand[1])
        if rank0 == rank1 or suit0 == suit1:
            return 'C'
        return 'F'

    # three cards? bet on flush or trips, call on a straight, otherwise fold
    #
    if 3 == len(hand):
        v = hand_value(hand)
        c = hand_value_class(v) 
        if c in (FLUSH, TRIP, STRF):
            return 'B'
        if c in (STR, ):
            return 'C'
        return 'F'

    # four cards? bet on straight flush, call on trips, straight, or flush, 
    # fold otherwise
    #
    if 4 == len(hand):
        v = best_hand_value(hand)
        c = hand_value_class(v)
        if c in (STRF, ):
            return 'B'
        if c in (TRIP, FLUSH):
            return 'C'
        return 'F'

