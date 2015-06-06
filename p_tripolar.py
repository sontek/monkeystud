# p_schitzophrenic.py -- fold 1/3 of the time, call 1/3, all-in 1/3

import random


def play(my_id, stack, to_call):
    return random.choice((0, to_call, stack))

