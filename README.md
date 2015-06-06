Monkey Hold 'em
===============

Monkey Hold 'em is a poker variant, suitable for computer play.

The game is played with a 32 card deck, only the duece through
nine are used. The best three card hand made from one hole card
and three community cards wins the hand. The hand ranks are:
high card, pair, straight, flush, trips, straight flush.
Seats are shuffled every hand. Ante is 1% of player's chip count.
There are no-limit, check-raise allowed, betting rounds after the 
hole card, flop, turn, and river.

A bot must implement the `play()` function, and optionally `observe()`.

`play()` takes three arguments: `my_id`, `stack`, `to_call`; and should
return the number of chips to bet.

`observe()` takes four arguments: `my_id`, `player_id`, `action`, `argument`;
return value is ignored.

`action` is one of:

    S   SIT         player sits down with <argument> chips
    A   ANTE        player antes <argument> chips
    H   HOLE        player is dealt <argument> hole card
    D   DOWN        player is dealt <argument> face down
    U   UP          player is dealt <argument> face up
    B   BET         player bets <argument> chips
    F   FOLD        player folds
    C   COMMUNITY   dealer reveals <argument> community card
    R   REVEAL      dealer reveals <argument> card after a showdown
    W   WIN         dealar awards <argument> chips to player

To get a copy of the game:

    $ git clone https://github.com/colinmsaunders/mhe.git
    $ cd mhe

To play a game, human against computer:

    $ python roshambolo.py human 3 p_computer

To play a game betweent computer and random, starting with 10,000 chips:

    $ python roshambolo.py game 10000 p_computer p_random

Next, copy `p_random.py` to `p_bot.py`, implement `play()` and
optionally `observe()`, then play your bot against random:

    $ cp p_random.py p_bot.py
    $ python mhe.py game 10000 p_bot p_random

To play a tournament of 100 games each with 10,000 chips:

    $ python mhe.py tourney 100 10000 p_bot p_random p_computer

The winner of the tournament is the player who wins the most games,
in total. Note that `player_id` is consistent across games.

To time your robot (to make sure it's not too slow, compared to `p_random`):

    $ python mhe.py time p_bot

Have fun!

