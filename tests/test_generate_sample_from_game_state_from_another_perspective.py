import unittest
from inference import generate_sample_from_game_state_from_another_perspective
from domino_data_types import DominoTile, PlayerTiles4

class TestAnalyticAgentPlayer(unittest.TestCase):

    def test_basic_sample_generation(self):
        unplayed_tiles = [DominoTile(1, 2), DominoTile(3, 4), DominoTile(5, 6), DominoTile(1, 1), DominoTile(1, 3)]
        known_with_tiles = {'S': [], 'E': [], 'N': [], 'W': []}
        not_with_tiles = {'S': set(), 'E': set(), 'N': set(), 'W': set()}
        player_tiles = PlayerTiles4(2, 1, 1, 1)

        sample = generate_sample_from_game_state_from_another_perspective(
            unplayed_tiles, known_with_tiles, not_with_tiles, player_tiles)

        # print(sample)
        self.assertEqual(len(sample['S']), 2)
        self.assertEqual(len(sample['E']), 1)
        self.assertEqual(len(sample['N']), 1)
        self.assertEqual(len(sample['W']), 1)
        self.assertEqual(sum(1 if DominoTile(1, 1) in tiles else 0 for tiles in sample.values()), 1)
        self.assertEqual(sum(1 if DominoTile(1, 2) in tiles else 0 for tiles in sample.values()), 1)
        self.assertEqual(sum(1 if DominoTile(3, 4) in tiles else 0 for tiles in sample.values()), 1)
        self.assertEqual(sum(1 if DominoTile(1, 3) in tiles else 0 for tiles in sample.values()), 1)
        self.assertEqual(sum(1 if DominoTile(5, 6) in tiles else 0 for tiles in sample.values()), 1)
        self.assertEqual(sum(len(tiles) for tiles in sample.values()), len(unplayed_tiles))


    def test_sample_with_known_tiles_generation(self):
        unplayed_tiles = [DominoTile(1, 2), DominoTile(3, 4), DominoTile(5, 6), DominoTile(1, 1), DominoTile(1, 3)]
        known_with_tiles = {'S': [DominoTile(1, 1)], 'E': [], 'N': [], 'W': []}
        not_with_tiles = {'S': set(), 'E': set(), 'N': set(), 'W': set()}
        player_tiles = PlayerTiles4(2, 1, 1, 1)

        sample = generate_sample_from_game_state_from_another_perspective(
            unplayed_tiles, known_with_tiles, not_with_tiles, player_tiles)

        # print(sample)
        self.assertEqual(len(sample['S']), 2)
        self.assertEqual(len(sample['E']), 1)
        self.assertEqual(len(sample['N']), 1)
        self.assertEqual(len(sample['W']), 1)
        self.assertIn(DominoTile(1, 1), sample['S'])
        self.assertEqual(sum(1 if DominoTile(1, 1) in tiles else 0 for tiles in sample.values()), 1)
        self.assertEqual(sum(1 if DominoTile(1, 2) in tiles else 0 for tiles in sample.values()), 1)
        self.assertEqual(sum(1 if DominoTile(3, 4) in tiles else 0 for tiles in sample.values()), 1)
        self.assertEqual(sum(1 if DominoTile(1, 3) in tiles else 0 for tiles in sample.values()), 1)
        self.assertEqual(sum(1 if DominoTile(5, 6) in tiles else 0 for tiles in sample.values()), 1)
        self.assertEqual(sum(len(tiles) for tiles in sample.values()), len(unplayed_tiles))

    def test_sample_with_known_tiles_generation2(self):
        unplayed_tiles = [DominoTile(1, 2), DominoTile(3, 4), DominoTile(5, 6), DominoTile(1, 1), DominoTile(1, 3)]
        known_with_tiles = {'S': [DominoTile(1, 1)], 'E': [DominoTile(1, 2)], 'N': [], 'W': []}
        not_with_tiles = {'S': set(), 'E': set(), 'N': set(), 'W': set()}
        player_tiles = PlayerTiles4(2, 1, 1, 1)

        sample = generate_sample_from_game_state_from_another_perspective(
            unplayed_tiles, known_with_tiles, not_with_tiles, player_tiles)

        # print(sample)
        self.assertEqual(len(sample['S']), 2)
        self.assertEqual(len(sample['E']), 1)
        self.assertEqual(len(sample['N']), 1)
        self.assertEqual(len(sample['W']), 1)
        self.assertIn(DominoTile(1, 1), sample['S'])
        self.assertIn(DominoTile(1, 2), sample['E'])
        self.assertEqual(sum(1 if DominoTile(1, 1) in tiles else 0 for tiles in sample.values()), 1)
        self.assertEqual(sum(1 if DominoTile(1, 2) in tiles else 0 for tiles in sample.values()), 1)
        self.assertEqual(sum(1 if DominoTile(3, 4) in tiles else 0 for tiles in sample.values()), 1)
        self.assertEqual(sum(1 if DominoTile(1, 3) in tiles else 0 for tiles in sample.values()), 1)
        self.assertEqual(sum(1 if DominoTile(5, 6) in tiles else 0 for tiles in sample.values()), 1)
        self.assertEqual(sum(len(tiles) for tiles in sample.values()), len(unplayed_tiles))

    def test_sample_with_not_with_tiles(self):
        unplayed_tiles = [DominoTile(1, 2), DominoTile(3, 4), DominoTile(5, 6), DominoTile(1, 1)]
        known_with_tiles = {'S': [], 'E': [], 'N': [], 'W': []}
        not_with_tiles = {'S': {DominoTile(1, 2)}, 'E': set(), 'N': set(), 'W': set()}
        player_tiles = PlayerTiles4(1, 1, 1, 1)

        sample = generate_sample_from_game_state_from_another_perspective(
            unplayed_tiles, known_with_tiles, not_with_tiles, player_tiles)

        # print('sample',sample)
        self.assertNotIn(DominoTile(1, 2), sample['S'])

    def test_sample_with_all_known_tiles(self):
        unplayed_tiles = [DominoTile(1, 2), DominoTile(3, 4), DominoTile(5, 6)]
        known_with_tiles = {'S': [DominoTile(1, 2)], 'E': [DominoTile(3, 4)], 
                            'N': [DominoTile(5, 6)], 'W': []}
        not_with_tiles = {'S': set(), 'E': set(), 'N': set(), 'W': set()}
        player_tiles = PlayerTiles4(1, 1, 1, 0)

        sample = generate_sample_from_game_state_from_another_perspective(
            unplayed_tiles, known_with_tiles, not_with_tiles, player_tiles)

        self.assertEqual(sample['S'], [DominoTile(1, 2)])
        self.assertEqual(sample['E'], [DominoTile(3, 4)])
        self.assertEqual(sample['N'], [DominoTile(5, 6)])
        self.assertEqual(sample['W'], [])

    def test_sample_with_more_known_tiles_than_player_count(self):
        unplayed_tiles = [DominoTile(1, 2), DominoTile(3, 4), DominoTile(5, 6)]
        known_with_tiles = {'S': [DominoTile(1, 2), DominoTile(3, 4)], 'E': [], 'N': [], 'W': []}
        not_with_tiles = {'S': set(), 'E': set(), 'N': set(), 'W': set()}
        player_tiles = PlayerTiles4(1, 1, 1, 0)

        with self.assertRaises(AssertionError):
            generate_sample_from_game_state_from_another_perspective(
                unplayed_tiles, known_with_tiles, not_with_tiles, player_tiles)

    def test_sample_with_only_one_player_remaining(self):
        unplayed_tiles = [DominoTile(1, 2), DominoTile(3, 4)]
        known_with_tiles = {'S': [], 'E': [], 'N': [], 'W': []}
        not_with_tiles = {'S': set(), 'E': set(), 'N': set(), 'W': set()}
        player_tiles = PlayerTiles4(2, 0, 0, 0)

        sample = generate_sample_from_game_state_from_another_perspective(
            unplayed_tiles, known_with_tiles, not_with_tiles, player_tiles)

        self.assertEqual(len(sample['S']), 2)
        self.assertEqual(len(sample['E']), 0)
        self.assertEqual(len(sample['N']), 0)
        self.assertEqual(len(sample['W']), 0)

if __name__ == '__main__':
    unittest.main()
