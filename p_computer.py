# p_random.py -- randomly fold, call, bet

import random


def play(player_id, hand, state):
    return random.choice(('F', 'C', 'B'))

