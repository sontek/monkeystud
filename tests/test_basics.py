import pytest
import mock

@pytest.mark.unit
def test_play_hand_valid_argument():
    from monkeystud import play_hand, make_player
    player1 = make_player('p_1', 'p_random', False)
    history_ref = None

    def get_play(history):
        history_ref = history
        return 'Z'

    player1.get_play = get_play
    player2 = make_player('p_2', 'p_random', False)
    try:
        play_hand([player1, player2], 10, False)
    finally:
        player1.done()
        player2.done()

    assert player1.played is True
    assert player2.played is True


@pytest.mark.unit
def test_play_game_ante():
    from monkeystud import play_game, make_player
    player1 = make_player('p_1', 'p_random', False)
    history_ref = None

    def get_play(history):
        history_ref = history
        return 'C'

    player1.get_play = get_play
    player2 = make_player('p_2', 'p_random', False)


    try:
        with mock.patch('monkeystud.logging') as l:
            play_game([player1, player2], False)
    finally:
        player1.done()
        player2.done()

    antes = []
    for call in l.debug.mock_calls:
        data = call[1][0]
        if 'antes' in data:
            antes.append(int(data.split()[-1]))

    assert antes[0] < antes[-1]
    assert player1.played is True
    assert player2.played is True
