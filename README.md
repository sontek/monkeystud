MonkeyStud
==========

MonkeyStud is a poker variant, suitable for computer play.

The game is played with a 32 card deck, only the duece through
nine are used. The best three card hand wins. The hand ranks are:
high card, pair, straight, flush, trips, straight flush.

Players are dealt four cards, the first face down, the rest face up.
There are betting rounds after the second, third, and fourth cards.

Up to eight players can play at once. Seats are shuffled every hand. 
Each player starts with 100 chips. Ante is 1% of total chips, divided 
evenly between all players, no more than any one player's stack.

A play is either fold, call, or raise. The raise amount is the size of
the pot, but no more than any one player's stack.

A bot must implement the `play()` function. play() should return either
'F', 'C', or 'B' for Fold, Call, or Bet, respectfully. Play takes three
arguments: `player_id`, `hand`, `chips`, `pot`, `to_call`, and `history`. 
`history` is a serialization of the action so far.

To get a copy of the game:

    $ git clone https://github.com/colinmsaunders/monkeystud.git
    $ cd monkeystud

To play against the computer:

    $ python dealer.py human p_computer

To play a game between computer and random:

    $ python dealer.py game p_computer p_random

Next, copy `p_computer.py` to `p_bot.py`, implement `play()` and
then play your bot against computer:

    $ cp p_computer.py p_bot.py
    $ python dealer.py game p_bot p_computer

To play a tournament of 100 games:

    $ python dealer.py tourney 100 p_bot p_random p_computer

The winner of the tournament is the player who wins the most games,
in total. Note that `player_id` is consistent across games.

To time your robot (to make sure it's not too slow, compared to `p_random`):

    $ python dealer.py time p_bot

Have fun!

