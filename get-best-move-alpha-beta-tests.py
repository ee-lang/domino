import unittest
from unittest.mock import patch
# from get_best_move import get_best_move_alpha_beta, GameState, DominoTile, PlayerPosition_SOUTH, PlayerPosition_WEST, PlayerPosition_NORTH, PlayerPosition_EAST
from domino_data_types import GameState, DominoTile, PlayerPosition_SOUTH, PlayerPosition_WEST, PlayerPosition_NORTH, PlayerPosition_EAST
from get_best_move2 import get_best_move_alpha_beta
# from get_best_move import PlayerPosition_SOUTH, PlayerPosition_WEST, PlayerPosition_NORTH, PlayerPosition_EAST
# from get_best_move3 import get_best_move_alpha_beta, GameState, DominoTile

class TestGetBestMoveAlphaBeta(unittest.TestCase):

    def setUp(self):
        self.cache = {}

    def test_initial_move(self):
        # Test the first move of the game when the board is empty
        initial_hands = [
            [DominoTile(0, 0), DominoTile(0, 1), DominoTile(0, 2), DominoTile(0, 3), 
             DominoTile(0, 4), DominoTile(0, 5), DominoTile(0, 6)],
            [DominoTile(1, 1), DominoTile(1, 2), DominoTile(1, 3), DominoTile(1, 4), 
             DominoTile(1, 5), DominoTile(1, 6), DominoTile(2, 2)],
            [DominoTile(2, 3), DominoTile(2, 4), DominoTile(2, 5), DominoTile(2, 6), 
             DominoTile(3, 3), DominoTile(3, 4), DominoTile(3, 5)],
            [DominoTile(3, 6), DominoTile(4, 4), DominoTile(4, 5), DominoTile(4, 6), 
             DominoTile(5, 5), DominoTile(5, 6), DominoTile(6, 6)]
        ]
        state = GameState.new_game(initial_hands)
        best_move, score, _ = get_best_move_alpha_beta(state, depth=24, cache=self.cache, best_path_flag=False)
        
        # Check that the best move is one of the tiles in the first player's hand
        self.assertIn(best_move[0], initial_hands[0])
        # For the first move, 'left' or 'right' doesn't matter, so we don't assert on best_move[1]
        self.assertIsInstance(score, float)

    def test_single_result(self):
        # Test when only one move is available for the current player
        initial_hands = [
            [DominoTile(0, 0), DominoTile(0, 3), DominoTile(4, 6), 
             DominoTile(0, 4), DominoTile(0, 5), DominoTile(0, 6)],
            [DominoTile(0, 1), DominoTile(0, 2), DominoTile(1, 1), 
             DominoTile(1, 5), DominoTile(1, 6), DominoTile(2, 2)],
            [DominoTile(1, 3), DominoTile(1, 4), DominoTile(2, 3), 
             DominoTile(3, 3), DominoTile(3, 4), DominoTile(3, 5)],
            [DominoTile(2, 5), DominoTile(2, 6), DominoTile(3, 6), 
             DominoTile(5, 5), DominoTile(5, 6), DominoTile(6, 6)]
        ]
        state = GameState(
            player_hands=tuple(frozenset(hand) for hand in initial_hands),
            current_player=PlayerPosition_SOUTH,
            left_end=1,
            right_end=3,
            consecutive_passes=0
        )
        best_move, score, _ = get_best_move_alpha_beta(state, depth=24, cache=self.cache, best_path_flag=False)
        self.assertIn(best_move[0], initial_hands[0])
        self.assertEqual(best_move[0], DominoTile(0, 3))
        self.assertIsInstance(score, float)
        self.assertEqual(score, 62.0)
        # print('best_move, score', best_move, score)


    def test_single_move_available(self):
        # Test when only one move is available for the current player
        initial_hands = [
            [DominoTile(1, 2)],
            [DominoTile(3, 3)],
            [DominoTile(4, 4)],
            [DominoTile(5, 5)]
        ]
        state = GameState(
            player_hands=tuple(frozenset(hand) for hand in initial_hands),
            current_player=PlayerPosition_SOUTH,
            left_end=1,
            right_end=3,
            consecutive_passes=0
        )
        best_move, score, _ = get_best_move_alpha_beta(state, depth=3, cache=self.cache, best_path_flag=False)
        self.assertEqual(best_move, (DominoTile(1, 2), True))
        self.assertIsInstance(score, float)

    def test_multiple_moves_available(self):
        # Test when multiple moves are available
        initial_hands = [
            [DominoTile(1, 2), DominoTile(3, 4)],
            [DominoTile(5, 5)],
            [DominoTile(6, 6)],
            [DominoTile(0, 0)]
        ]
        state = GameState(
            player_hands=tuple(frozenset(hand) for hand in initial_hands),
            current_player=PlayerPosition_SOUTH,
            left_end=1,
            right_end=4,
            consecutive_passes=0
        )
        best_move, score, _ = get_best_move_alpha_beta(state, depth=3, cache=self.cache, best_path_flag=False)
        self.assertIn(best_move, [(DominoTile(1, 2), True), (DominoTile(3, 4), False)])
        self.assertIsInstance(score, float)

    def test_no_valid_moves(self):
        # Test when the current player has no valid moves but must keep a tile
        initial_hands = [
            [DominoTile(5, 6)],
            [DominoTile(1, 1)],
            [DominoTile(2, 2)],
            [DominoTile(3, 3)]
        ]
        state = GameState(
            player_hands=tuple(frozenset(hand) for hand in initial_hands),
            current_player=PlayerPosition_SOUTH,
            left_end=1,
            right_end=2,
            consecutive_passes=0
        )
        best_move, score, _ = get_best_move_alpha_beta(state, depth=3, cache=self.cache, best_path_flag=False)
        self.assertIsNone(best_move)  # Expecting None as the move, indicating a pass
        self.assertIsInstance(score, float)

    def test_game_over_south_win(self):
        # Test when the game is over (SOUTH has won)
        initial_hands = [
            [],  # SOUTH has no tiles (winner)
            [DominoTile(1, 1)],
            [DominoTile(2, 2)],
            [DominoTile(3, 3)]
        ]
        state = GameState(
            player_hands=tuple(frozenset(hand) for hand in initial_hands),
            current_player=PlayerPosition_WEST,  # Next player after SOUTH
            left_end=1,
            right_end=2,
            consecutive_passes=0
        )
        best_move, score, _ = get_best_move_alpha_beta(state, depth=3, cache=self.cache, best_path_flag=False)
        self.assertIsNone(best_move)  # Expecting None as the game is over
        self.assertIsInstance(score, float)
        self.assertGreater(score, 0)  # Score should be positive as SOUTH (player 0) has won

    def test_game_over_east_win(self):
        # Test when the game is over (EAST has won)
        initial_hands = [
            [DominoTile(1, 1)],
            [],  # EAST has no tiles (winner)
            [DominoTile(2, 2)],
            [DominoTile(3, 3)]
        ]
        state = GameState(
            player_hands=tuple(frozenset(hand) for hand in initial_hands),
            current_player=PlayerPosition_NORTH,  # Next player after EAST
            left_end=1,
            right_end=2,
            consecutive_passes=0
        )
        best_move, score, _ = get_best_move_alpha_beta(state, depth=3, cache=self.cache, best_path_flag=False)
        self.assertIsNone(best_move)  # Expecting None as the game is over
        self.assertIsInstance(score, float)
        self.assertLess(score, 0)  # Score should be negative as EAST (player 1) has won

    # @patch('get_best_move.min_max_alpha_beta')
    # def test_depth_limit(self, mock_min_max):
    #     # Test if the function respects the depth limit
    #     initial_hands = [
    #         [DominoTile(1, 1)],
    #         [DominoTile(2, 2)],
    #         [DominoTile(3, 3)],
    #         [DominoTile(4, 4)]
    #     ]
    #     state = GameState.new_game(initial_hands)
    #     get_best_move_alpha_beta(state, depth=5, cache=self.cache, best_path_flag=False)
    #     self.assertEqual(mock_min_max.call_args[0][1], 5)

    def test_cache_usage(self):
        # Test if the function uses and updates the cache
        initial_hands = [
            [DominoTile(1, 1)],
            [DominoTile(2, 2)],
            [DominoTile(3, 3)],
            [DominoTile(4, 4)]
        ]
        state = GameState.new_game(initial_hands)
        self.assertEqual(len(self.cache), 0)
        get_best_move_alpha_beta(state, depth=3, cache=self.cache, best_path_flag=False)
        self.assertGreater(len(self.cache), 0)

if __name__ == '__main__':
    unittest.main()
