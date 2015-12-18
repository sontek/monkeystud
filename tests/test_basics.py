import pytest
import mock

@pytest.mark.unit
def test_play_hand_valid_argument():
    from monkeystud import play_hand, make_player
    player1 = make_player('p_1', 'p_random', False)
    history_ref = None

    def get_play(history):
        history_ref = history
        print(history)
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
