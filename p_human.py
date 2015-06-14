# p_human -- human player

import monkeystud


def play(player_id, hand, history):
    print 'History:'
    pot = 0
    for i in history.split():
        j = i.split(':')
        if j[1] in ('A', 'B', 'C'):
            pot += int(j[2])
        print '\t%s\t%s\t%s' % (j[0], j[1], j[2])

    s = 'You are player "%s". Your hand is: %s\n'
    s += 'The pot is %d. What is your bet? '
    s += '(Fold, Call, or Bet)' 
    print s % (player_id, monkeystud.hand_str(hand), pot)
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
    print 'Invalid input. Folding.'
    return 'F'

