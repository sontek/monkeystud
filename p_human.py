# p_human -- human player

def bet(chips, to_call):
    print 'chips: %d, to_call: %d' % (chips, to_call)
    print 'What do you bet?'
    try:
        s = raw_input()
        x = int(s)
    except KeyboardInterrupt:
        raise
    except:
        print 'Invalid input. Folding'
        x = 0
    return x

def observe(my_id, player_id, action, argument):
    print 'OBSERVE: %s %s %s' % (player_id, action, argument)

