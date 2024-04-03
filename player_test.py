from player import Player


def test_it_boots():
    player = Player()
    assert isinstance(player, Player)