# p_human -- human player

import monkeystud


def play(player_id, hand, history):
    print 'History:'
    hand_over = False
    for i in history.split():
        player, code, x = i.split(':')
        if 0:
            pass
        elif 'S' == code:
            print '\t%-10s sits down with %d chips' % (player, int(x))
        elif 'A' == code:
            print '\t%-10s antes %d chips' % (player, int(x))
        elif 'D' == code:
            print '\t%-10s is dealt hole card face down' % (player, )
        elif 'U' == code:
            print '\t%-10s is dealt %s face up' % (player, x)
        elif 'C' == code:
            if 0 == int(x):
                print '\t%-10s checks' % (player, )
            else:
                print '\t%-10s calls %d' % (player, int(x))
        elif 'F' == code:
            print '\t%-10s folds' % (player, )
        elif 'B' == code:
            print '\t%-10s bets %d' % (player, int(x))
        elif 'R' == code:
            hand = monkeystud.str_to_hand(x)
            print '\t%-10s reveals %s -- %s' % (player, x, \
                  monkeystud.hand_value_str(monkeystud.best_hand_value(hand)))
        elif 'W' == code:
            print '\t%-10s wins %d' % (player, int(x))
            hand_over = True
        elif 'Z' == code:
            print '\t%-10s wins lucky %d' % (player, int(x))

    if hand_over:
        print 'Press return to continue.'
    else:
        print 'You are player "%s". Your hand is: %s. ' % (player_id, monkeystud.hand_str(hand))
        print '[F]old, (C)all, or (B)et?'
    s = None
    try:
        s = raw_input()
    except KeyboardInterrupt:
        raise
    s = s.upper()
    if s.startswith('F'):
        return 'F'
    if s.startswith('C'):
        return 'C'
    if s.startswith('B'):
        return 'B'
    return 'F'

