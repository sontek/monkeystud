# p_random.py -- fold 1/4 of the time, call 1/4, all-in 1/4, random raise 1/4

import random


def bet(chips, to_call):
    return random.choice((0, to_call, chips, random.randint(to_call, chips)))

