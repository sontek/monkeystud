# p_human -- human player

import mhe

g_my_id = None
g_pot = 0
g_my_hand = []
g_community = []

def bet(chips, to_call):
    global g_pot, g_my_hand, g_community
    print 'Your hand: %s; Community cards: %s' % \
            (mhe.hand_str(g_my_hand), mhe.hand_str(g_community))
    print 'You have %d chips, it\'s %d to call, pot is %d chips.' % \
            (chips, to_call, g_pot)
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
    global g_my_id, g_pot, g_my_hand, g_community
    if None == g_my_id:
        g_my_id = my_id
        print 'You are player %s.' % g_my_id

    if 0:
        pass

    elif 'S' == action:
        print 'Player %s sits down with %d chips.' % (player_id, argument)
        g_pot = 0
        g_my_hand = []
        g_community = []

    elif 'A' == action:
        print 'Player %s bets blind %d chips.' % (player_id, argument)
        g_pot += argument

    elif 'D' == action:
        print 'Player %s is dealt their hole card.' % (player_id, )

    elif 'H' == action:
        print 'Dealer deals your hole card: %s' % mhe.card_str(argument)
        g_my_hand.append(argument)

    elif 'C' == action:
        print 'Dealer deals community card: %s' % mhe.card_str(argument)
        g_community.append(argument)

    elif 'I' == action:
        print 'Player %s is all in for %d chips.' % (player_id, argument)
        g_pot += argument

    elif 'F' == action:
        print 'Player %s folds.' % (player_id, )
  
    elif 'B' == action:
        print 'Player %s bets %d chips.' % (player_id, argument)
        g_pot += argument

    elif 'R' == action:
        print 'Player %s reveals hole card: %s' % \
                (player_id, mhe.card_str(argument))
 
    elif 'W' == action:
        print 'Player %s wins %d chips.' % (player_id, argument)
    
    else:
        raise Exception('i don\'t know action "%s"' % action)

