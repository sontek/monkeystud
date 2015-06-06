# p_human -- human player

import mhe

g_my_id = None

def bet(chips, to_call):
    print 'You have %d chips, it\'s %d to call.' % (chips, to_call)
    print 'What is your bet?'
    try:
        s = raw_input()
        x = int(s)
    except KeyboardInterrupt:
        raise
    except:
        print 'Invalid input. Betting 0 chips.'
        x = 0
    return x


def observe(my_id, action, player_id, argument):
    global g_my_id
    if None == g_my_id:
        g_my_id = my_id
        print 'You are player %s.' % g_my_id

    if 0:
        pass

    elif 'S' == action:
        print 'Player %s sits down with %d chips.' % (player_id, argument)

    elif 'A' == action:
        print 'Player %s bets blind %d chips.' % (player_id, argument)

    elif 'D' == action:
        print 'Player %s is dealt their hole card.' % (player_id, )

    elif 'H' == action:
        print 'Dealer deals your hole card: %s' % mhe.card_str(argument)

    elif 'C' == action:
        print 'Dealer deals community card: %s' % mhe.card_str(argument)
           
    elif 'I' == action:
        print 'Player %s is all in for %d chips.' % (player_id, argument)

    elif 'F' == action:
        print 'Player %s folds.' % (player_id, )
  
    elif 'B' == action:
        print 'Player %s bets %d chips.' % (player_id, argument)
           
    elif 'R' == action:
        print 'Player %s reveals hole card: %s' % \
                (player_id, mhe.card_str(argument))
 
    elif 'W' == action:
        print 'Player %s wins %d chips.' % (player_id, argument)
    
    else:
        raise Exception('i don\'t know action "%s"' % action)

