import pytest


@pytest.mark.unit
def test_play_hand_valid_argument():
    from monkeystud import play_hand, make_player
    player1 = make_player('p_1', 'p_random', False)
    player1.get_play = lambda history: 'Z'
    player2 = make_player('p_2', 'p_random', False)
    play_hand([player1, player2], False)
    assert player1.folded is True
    assert player2.folded is False
