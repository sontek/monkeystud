# monkeystud.py -- Monkey Stud, a poker variant

# see README.md for more dox

import itertools


CHIPS_START = 100
ANTE        = (1, 100)

RANKS       = 8
SUITS       = 4

HIGH        = 0
PAIR        = 1
STR         = 2
FLUSH       = 3
TRIP        = 4
STRF        = 5


def make_card(r, s):
    return (r << 3) | s


def rank_suit(c):
    return c >> 3, c & 7


def card_str(a):
    return "%s%s" % ('?23456789TJQKABC'[a >> 3], 'cdhswxyz'[a & 7])


def hand_str(h):
    return ' '.join(map(lambda x : card_str(x), h))


def new_deck():
    d = []
    for i in range(SUITS):
        for j in range(1, RANKS + 1):
            d.append(make_card(j, i))
    return d


def shuffle(d):
    random.shuffle(d)
    return d


def classify_hand(a, b, c):
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

