import sys
import click
import time
import logging
import random

from monkeystud import make_player, play_tournament, play_game, verify_player

MAX_TIME       = 100.0     # bot can be no more than 100x slower

class Config(object):
    def __init__(self, verify_players, catch_exceptions, max_time):
        self.verify_players = verify_players
        self.catch_exceptions = catch_exceptions
        self.max_time = max_time


@click.group(context_settings={'help_option_names': ['-h', '--help']})
@click.option(
    '--seed', '-s', help='set seed for random number generator', type=int,
)
@click.option(
    '--catch-exceptions', help='catch and log exceptions', default=False,
    type=bool
)
@click.option(
    '--max-time', help='max time relative to p_random a bot can take',
    default=MAX_TIME,
    type=float
)
@click.option(
    '--verify', help='verify bots before fight',
    default=False,
    type=bool
)
@click.option(
    '--log-level', help='Log level',
    default='DEBUG',
    type=str
)
@click.pass_context
@click.version_option()
def main(ctx, seed, catch_exceptions, max_time, verify, log_level):
    """
    monkeystud! see: http://github.com/botfights/monkeystud for dox
    """
    if seed is None:
        seed = time.time()

    log_level = getattr(logging, log_level)

    random.seed(seed)

    logging.basicConfig(
        level=log_level, format='%(message)s', stream=sys.stdout
    )
    obj = Config(verify, catch_exceptions, max_time)
    ctx.obj = obj



@main.command()
@click.argument('competitors', nargs=-1)
@click.pass_obj
def human(obj, competitors):
    players = [make_player('human', 'p_human', obj.catch_exceptions),]
    if competitors:
        for i in competitors:
            players.append(make_player(i, i, obj.catch_exceptions))
    else:
        players.append(make_player('computer', 'p_computer'))

    winner = play_game(players, obj.catch_exceptions)
    sys.exit()


@main.command()
@click.argument('competitors', nargs=-1, required=True)
@click.pass_obj
def game(obj, competitors):
    players = []
    for player_id, playername in enumerate(competitors):
        if obj.verify_players:
            player_valid = verify_player(
                obj.max_time, playername
            )
            if 0 != player_valid:
                continue
        players.append(make_player(
            chr(ord('a') + player_id), playername, obj.catch_exceptions
        ))
    winner = play_game(players, obj.catch_exceptions)
    sys.exit()


@main.command()
@click.option(
    '--num-games', help='set number of games for tournament', default=1000,
    type=int
)
@click.argument('competitors', nargs=-1, required=True)
@click.pass_obj
def tournament(obj, num_games, competitors):
    players = []
    for player_id, playername in enumerate(competitors):
        if obj.verify_players:
            if 0 != verify_player(obj.max_time, playername):
                continue
        players.append(make_player(
            chr(ord('a') + player_id), playername, obj.catch_exceptions
        ))
    play_tournament(num_games, players, obj.catch_exceptions)
    sys.exit()


@main.command()
@click.argument('bot')
@click.pass_obj
def verify(obj, bot):
    result = verify_player(obj.max_time, bot)
    sys.exit()
