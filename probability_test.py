import unittest
from domino_probability_calc import calculate_tile_probabilities, PlayerTiles, DominoTile
from math import comb

class TestCalculateTileProbabilities(unittest.TestCase):

    def setUp(self):
        self.player_tiles = PlayerTiles(N=1, E=1, W=1)

    def test_basic_scenario(self):
        remaining_tiles = [DominoTile(1, 2), DominoTile(3, 4), DominoTile(5, 6)]
        not_with = {'N':set(),'E':set(),'W':set()}
        probabilities = calculate_tile_probabilities(remaining_tiles, not_with, self.player_tiles)
        
        for tile in remaining_tiles:
            self.assertAlmostEqual(sum(probabilities[tile].values()), 1.0)
            for prob in probabilities[tile].values():
                self.assertAlmostEqual(prob, 1/3)

    def test_known_not_with(self):
        remaining_tiles = [DominoTile(1, 2), DominoTile(3, 4), DominoTile(5, 6)]
        not_with = {'N': {DominoTile(1, 2)},'E':set(),'W':set()}
        probabilities = calculate_tile_probabilities(remaining_tiles, not_with, self.player_tiles)
        
        self.assertEqual(probabilities[DominoTile(1, 2)]['N'], 0.0)
        self.assertAlmostEqual(probabilities[DominoTile(1, 2)]['E'], 0.5)
        self.assertAlmostEqual(probabilities[DominoTile(1, 2)]['W'], 0.5)

    # Invalid test!
    # def test_known_with(self):
    #     player_tiles = PlayerTiles(N=1, E=1, W=1)
    #     remaining_tiles = [DominoTile(1, 2), DominoTile(3, 4), DominoTile(5, 6)]
    #     not_with = {'N': {DominoTile(1, 2)}, 'E': {DominoTile(1, 2)}, 'W':set()}
    #     probabilities = calculate_tile_probabilities(remaining_tiles, not_with, player_tiles)
        
    #     self.assertEqual(probabilities[DominoTile(1, 2)]['W'], 1.0)
    #     self.assertEqual(probabilities[DominoTile(1, 2)]['N'], 0.0)
    #     self.assertEqual(probabilities[DominoTile(1, 2)]['E'], 0.0)

    def test_uneven_distribution(self):
        remaining_tiles = [DominoTile(1, 2), DominoTile(3, 4), DominoTile(5, 6), DominoTile(1, 3)]
        player_tiles = PlayerTiles(N=2, E=1, W=1)
        not_with = {'N':set(),'E':set(),'W':set()}
        probabilities = calculate_tile_probabilities(remaining_tiles, not_with, player_tiles)
        
        # print(probabilities)
        total_outcomes = comb(4,2)*comb(2,1)
        for tile in remaining_tiles:
            self.assertAlmostEqual(sum(probabilities[tile].values()), 1.0)
            for player, prob in probabilities[tile].items():
                if player == 'N':
                    self.assertAlmostEqual(prob, comb(3,1)*comb(2,1)/total_outcomes)
                else:
                    self.assertAlmostEqual(prob, comb(3,2)/total_outcomes)

    def test_empty_remaining_tiles(self):
        remaining_tiles = []
        not_with = {'N':set(),'E':set(),'W':set()}
        probabilities = calculate_tile_probabilities(remaining_tiles, not_with, self.player_tiles)
        
        self.assertEqual(probabilities, {})

    def test_all_tiles_known(self):
        remaining_tiles = [DominoTile(1, 2), DominoTile(3, 4), DominoTile(5, 6)]
        not_with = {
            'N': {DominoTile(1, 2), DominoTile(3, 4)},
            'E': {DominoTile(1, 2), DominoTile(5, 6)},
            'W': {DominoTile(3, 4), DominoTile(5, 6)}
        }
        probabilities = calculate_tile_probabilities(remaining_tiles, not_with, self.player_tiles)
        
        expected = {
            DominoTile(1, 2): {'N': 0.0, 'E': 0.0, 'W': 1.0},
            DominoTile(3, 4): {'N': 0.0, 'E': 1.0, 'W': 0.0},
            DominoTile(5, 6): {'N': 1.0, 'E': 0.0, 'W': 0.0}
        }
        self.assertEqual(probabilities, expected)

    def test_probability_sum(self):
        remaining_tiles = [DominoTile(1, 2), DominoTile(3, 4), DominoTile(5, 6), DominoTile(1, 3)]
        not_with = {'N': {DominoTile(1, 2)},'E':set(),'W':set()}
        player_tiles = PlayerTiles(N=1, E=2, W=1)
        probabilities = calculate_tile_probabilities(remaining_tiles, not_with, player_tiles)
        
        for tile in remaining_tiles:
            self.assertAlmostEqual(sum(probabilities[tile].values()), 1.0)

if __name__ == '__main__':
    unittest.main()


# import unittest
# from domino_probability_calc import calculate_tile_probabilities, PlayerTiles, DominoTile
# from math import comb

# class TestCalculateTileProbabilities(unittest.TestCase):

#     def setUp(self):
#         self.player_tiles = PlayerTiles(N=1, E=1, W=1)

#     def test_basic_scenario(self):
#         remaining_tiles = [DominoTile(1, 2), DominoTile(3, 4), DominoTile(5, 6)]
#         not_with = {'N':set(),'E':set(),'W':set()}
#         known_with = {}
#         probabilities = calculate_tile_probabilities(remaining_tiles, not_with, known_with, self.player_tiles)

#         for tile in remaining_tiles:
#             self.assertAlmostEqual(sum(probabilities[tile].values()), 1.0)
#             for prob in probabilities[tile].values():
#                 self.assertAlmostEqual(prob, 1/3)

#     def test_known_not_with(self):
#         remaining_tiles = [DominoTile(1, 2), DominoTile(3, 4), DominoTile(5, 6)]
#         not_with = {'N': {DominoTile(1, 2)},'E':set(),'W':set()}
#         known_with = {}
#         probabilities = calculate_tile_probabilities(remaining_tiles, not_with, known_with, self.player_tiles)

#         self.assertEqual(probabilities[DominoTile(1, 2)]['N'], 0.0)
#         self.assertAlmostEqual(probabilities[DominoTile(1, 2)]['E'], 0.5)
#         self.assertAlmostEqual(probabilities[DominoTile(1, 2)]['W'], 0.5)

#     def test_known_with(self):
#         player_tiles = PlayerTiles(N=1, E=1, W=1)
#         remaining_tiles = [DominoTile(1, 2), DominoTile(3, 4), DominoTile(5, 6)]
#         not_with = {'N': set(), 'E': set(), 'W': set()}
#         known_with = {'W': {DominoTile(1, 2)}}
#         probabilities = calculate_tile_probabilities(remaining_tiles, not_with, known_with, player_tiles)

#         self.assertEqual(probabilities[DominoTile(1, 2)]['W'], 1.0)
#         self.assertEqual(probabilities[DominoTile(1, 2)]['N'], 0.0)
#         self.assertEqual(probabilities[DominoTile(1, 2)]['E'], 0.0)

#     def test_uneven_distribution(self):
#         remaining_tiles = [DominoTile(1, 2), DominoTile(3, 4), DominoTile(5, 6), DominoTile(1, 3)]
#         player_tiles = PlayerTiles(N=2, E=1, W=1)
#         not_with = {'N':set(),'E':set(),'W':set()}
#         known_with = {}
#         probabilities = calculate_tile_probabilities(remaining_tiles, not_with, known_with, player_tiles)

#         total_outcomes = comb(4,2)*comb(2,1)
#         for tile in remaining_tiles:
#             self.assertAlmostEqual(sum(probabilities[tile].values()), 1.0)
#             for player, prob in probabilities[tile].items():
#                 if player == 'N':
#                     self.assertAlmostEqual(prob, comb(3,1)*comb(2,1)/total_outcomes)
#                 else:
#                     self.assertAlmostEqual(prob, comb(3,2)/total_outcomes)

#     def test_empty_remaining_tiles(self):
#         remaining_tiles = []
#         not_with = {'N':set(),'E':set(),'W':set()}
#         known_with = {}
#         probabilities = calculate_tile_probabilities(remaining_tiles, not_with, known_with, self.player_tiles)

#         self.assertEqual(probabilities, {})

#     def test_all_tiles_known(self):
#         remaining_tiles = [DominoTile(1, 2), DominoTile(3, 4), DominoTile(5, 6)]
#         not_with = {'N':set(),'E':set(),'W':set()}
#         known_with = {
#             'N': {DominoTile(1, 2)},
#             'E': {DominoTile(3, 4)},
#             'W': {DominoTile(5, 6)}
#         }
#         probabilities = calculate_tile_probabilities(remaining_tiles, not_with, known_with, self.player_tiles)

#         expected = {
#             DominoTile(1, 2): {'N': 1.0, 'E': 0.0, 'W': 0.0},
#             DominoTile(3, 4): {'N': 0.0, 'E': 1.0, 'W': 0.0},
#             DominoTile(5, 6): {'N': 0.0, 'E': 0.0, 'W': 1.0}
#         }
#         self.assertEqual(probabilities, expected)

#     def test_probability_sum(self):
#         remaining_tiles = [DominoTile(1, 2), DominoTile(3, 4), DominoTile(5, 6), DominoTile(1, 3)]
#         not_with = {'N': {DominoTile(1, 2)},'E':set(),'W':set()}
#         known_with = {}
#         player_tiles = PlayerTiles(N=1, E=2, W=1)
#         probabilities = calculate_tile_probabilities(remaining_tiles, not_with, known_with, player_tiles)

#         for tile in remaining_tiles:
#             self.assertAlmostEqual(sum(probabilities[tile].values()), 1.0)

# if __name__ == '__main__':
#     unittest.main()