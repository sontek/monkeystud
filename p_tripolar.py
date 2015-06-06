# p_tripolar.py -- fold 1/3 of the time, call 1/3, all-in 1/3

import random


def bet(chips, to_call):
    return random.choice((0, to_call, chips))

