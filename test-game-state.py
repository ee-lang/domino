import unittest
from domino_game_analyzer import GameState, PlayerPosition, DominoTile

class TestGameState(unittest.TestCase):

    def test_is_game_over_empty_hand(self):
        # Test when a player has an empty hand
        hands = [
            [],  # South (empty hand)
            [DominoTile(1, 2)],
            [DominoTile(3, 4)],
            [DominoTile(5, 6)]
        ]
        state = GameState(
            player_hands=tuple(frozenset(hand) for hand in hands),
            current_player=PlayerPosition.SOUTH,
            left_end=1,
            right_end=6,
            consecutive_passes=0
        )
        self.assertTrue(state.is_game_over())

    def test_is_game_over_all_players_have_tiles(self):
        # Test when all players still have tiles
        hands = [
            [DominoTile(0, 1)],
            [DominoTile(1, 2)],
            [DominoTile(3, 4)],
            [DominoTile(5, 6)]
        ]
        state = GameState(
            player_hands=tuple(frozenset(hand) for hand in hands),
            current_player=PlayerPosition.SOUTH,
            left_end=1,
            right_end=6,
            consecutive_passes=0
        )
        self.assertFalse(state.is_game_over())

    def test_is_game_over_consecutive_passes(self):
        # Test when there have been 4 consecutive passes
        hands = [
            [DominoTile(0, 1)],
            [DominoTile(1, 2)],
            [DominoTile(3, 4)],
            [DominoTile(5, 6)]
        ]
        state = GameState(
            player_hands=tuple(frozenset(hand) for hand in hands),
            current_player=PlayerPosition.SOUTH,
            left_end=1,
            right_end=6,
            consecutive_passes=4
        )
        self.assertTrue(state.is_game_over())

    def test_is_game_over_less_than_four_passes(self):
        # Test when there have been less than 4 consecutive passes
        hands = [
            [DominoTile(0, 1)],
            [DominoTile(1, 2)],
            [DominoTile(3, 4)],
            [DominoTile(5, 6)]
        ]
        state = GameState(
            player_hands=tuple(frozenset(hand) for hand in hands),
            current_player=PlayerPosition.SOUTH,
            left_end=1,
            right_end=6,
            consecutive_passes=3
        )
        self.assertFalse(state.is_game_over())

if __name__ == '__main__':
    unittest.main()
