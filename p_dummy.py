# p_dummy.py -- just look at my hand, don't remember anything, no randomness

from monkeystud import rank_suit, hand_value, best_hand_value, hand_value_class, PAIR, STR, FLUSH, TRIP, STRF

def play(player_id, hand, history):


    # just two cards? bet on nines, call any pair or possible straight or flush, 
    # fold otherwise
    #
    if 2 == len(hand):
        rank0, suit0 = rank_suit(hand[0])
        rank1, suit1 = rank_suit(hand[1])
        if 9 == rank0 and 9 == rank1:
            return 'B'
        if rank0 == rank1:
            return 'C'
        if suit0 == suit1:
            return 'C'
        if (rank1 - rank0) in (-1, 1):
            return 'C'
        return 'F'

    # three cards? bet on a flush or better, call on a pair or straight,
    # fold otherwise
    #
    if 3 == len(hand):
        v = hand_value(hand)
        c = hand_value_class(v) 
        if c in (FLUSH, TRIP, STRF):
            return 'B'
        if c in (PAIR, STR):
            return 'C'
        return 'F'

    # four cards? bet on trips or straight flush, call on a straight or flush, fold otherwise
    #
    if 4 == len(hand):
        v = best_hand_value(hand)
        c = hand_value_class(v)
        if c in (TRIP, STRF):
            return 'B'
        if c in (STR, FLUSH):
            return 'C'
        return 'F'

