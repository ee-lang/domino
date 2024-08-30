import unittest
from typing import List, Tuple, Set
from domino_game_analyzer import DominoTile, PlayerPosition
from domino_probability_calc import generate_sample, PlayerTiles

class TestGenerateSample(unittest.TestCase):
    def setUp(self):
        self.remaining_tiles = [
            DominoTile(0, 1), DominoTile(0, 2), DominoTile(1, 2),
            DominoTile(1, 3), DominoTile(2, 3), DominoTile(3, 3)
        ]

    def test_basic_functionality(self):
        not_with = {'N': set(), 'E': set(), 'W': set()}
        # known_with = {}
        player_tiles = PlayerTiles(N=2, E=2, W=2)
        
        sample = generate_sample(self.remaining_tiles, not_with, player_tiles)
        # sample = generate_sample(self.remaining_tiles, not_with, known_with, player_tiles)
        
        self.assertEqual(len(sample), 3)  # Should have 3 players
        self.assertEqual(sum(len(tiles) for tiles in sample.values()), 6)  # Total tiles should be 6
        self.assertEqual(len(sample['N']), 2)
        self.assertEqual(len(sample['E']), 2)
        self.assertEqual(len(sample['W']), 2)

    def test_not_with_constraint(self):
        not_with = {'N': {DominoTile(0, 1), DominoTile(0, 2)}, 'E': set(), 'W': set()}
        known_with = {}
        player_tiles = PlayerTiles(N=2, E=2, W=2)
        
        for _ in range(25):
            sample = generate_sample(self.remaining_tiles, not_with, player_tiles)
            # sample = generate_sample(self.remaining_tiles, not_with, known_with, player_tiles)
            
            self.assertNotIn(DominoTile(0, 1), sample['N'])
            self.assertNotIn(DominoTile(0, 2), sample['N'])

    # def test_known_with_constraint(self):
    #     not_with = {}
    #     # known_with = {'E': {DominoTile(1, 2), DominoTile(2, 3)}}
    #     player_tiles = PlayerTiles(N=2, E=2, W=2)
        
    #     for _ in range(25):
    #         sample = generate_sample(self.remaining_tiles, not_with, player_tiles)
    #         # sample = generate_sample(self.remaining_tiles, not_with, known_with, player_tiles)
            
    #         self.assertIn(DominoTile(1, 2), sample['E'])
    #         self.assertIn(DominoTile(2, 3), sample['E'])

    def test_uneven_distribution(self):
        not_with = {'N': set(), 'E': set(), 'W': set()}
        # known_with = {}
        player_tiles = PlayerTiles(N=3, E=2, W=1)
        
        for _ in range(25):
            sample = generate_sample(self.remaining_tiles, not_with, player_tiles)
            # sample = generate_sample(self.remaining_tiles, not_with, known_with, player_tiles)
            
            self.assertEqual(len(sample['N']), 3)
            self.assertEqual(len(sample['E']), 2)
            self.assertEqual(len(sample['W']), 1)

    def test_all_tiles_assigned(self):
        not_with = {'N': set(), 'E': set(), 'W': set()}
        # known_with = {}
        player_tiles = PlayerTiles(N=2, E=2, W=2)
        
        for _ in range(25):
            sample = generate_sample(self.remaining_tiles, not_with, player_tiles)
            # sample = generate_sample(self.remaining_tiles, not_with, known_with, player_tiles)
            
            all_assigned_tiles = set().union(*sample.values())
            self.assertEqual(set(self.remaining_tiles), all_assigned_tiles)

    def test_no_duplicate_assignments(self):
        not_with = {'N': set(), 'E': set(), 'W': set()}
        # known_with = {}
        player_tiles = PlayerTiles(N=2, E=2, W=2)
        
        for _ in range(25):
            sample = generate_sample(self.remaining_tiles, not_with, player_tiles)
            # sample = generate_sample(self.remaining_tiles, not_with, known_with, player_tiles)
            
            all_assigned_tiles = list(sample['N']) + list(sample['E']) + list(sample['W'])
            self.assertEqual(len(all_assigned_tiles), len(set(all_assigned_tiles)))

    def test_conflicting_constraints(self):
        not_with = {'N': {DominoTile(0, 1), DominoTile(0, 2)}, 'E': {DominoTile(0, 1)}, 'W': {DominoTile(0, 1)}}
        # known_with = {'N': {DominoTile(0, 1)}}
        player_tiles = PlayerTiles(N=2, E=2, W=2)
        
        with self.assertRaises(AssertionError) as context:
            for _ in range(25):
                generate_sample(self.remaining_tiles, not_with, player_tiles)
                # generate_sample(self.remaining_tiles, not_with, known_with, player_tiles)
        self.assertEqual(str(context.exception), "Tile in remaining_tiles and not with any player!")

    def test_double_not_with_constraint(self):
        not_with = {'N': {DominoTile(0, 1), DominoTile(0, 2)}, 'E':{DominoTile(0,1),DominoTile(1,2)}, 'W': set()}
        # known_with = {}
        player_tiles = PlayerTiles(N=2, E=2, W=2)
        
        # with self.assertRaises(AssertionError):
        for _ in range(25):
            sample = generate_sample(self.remaining_tiles, not_with, player_tiles)
            # sample = generate_sample(self.remaining_tiles, not_with, known_with, player_tiles)
            self.assertIn(DominoTile(0, 1), sample['W'])
            self.assertNotIn(DominoTile(0, 1), sample['N'])
            self.assertNotIn(DominoTile(0, 1), sample['E'])
            self.assertNotIn(DominoTile(0, 2), sample['N'])
            self.assertNotIn(DominoTile(1, 2), sample['E'])


    def test_double_not_with_constraint2(self):
        remaining_tiles = set([
            DominoTile(0, 0), DominoTile(0, 1), DominoTile(0, 2), DominoTile(0, 6),
            DominoTile(1, 3), DominoTile(1, 4), DominoTile(1, 5), DominoTile(1, 6),
            DominoTile(2, 2), DominoTile(2, 3), DominoTile(2, 6), DominoTile(3, 3),
            DominoTile(5, 6)
            # DominoTile(2, 4), DominoTile(3, 6)  # Tiles in human player's hand
        ])

        # Define not_with based on _knowledge_tracker
        not_with = {
            'E': set(),
            'N': {DominoTile(5, 6), DominoTile(1, 4)},
            'W': {DominoTile(1, 4)}
        }

        # Define player_tiles (assuming 7 tiles per player at the start)
        player_tiles = PlayerTiles(N=1, E=1, W=1)

        player_tiles = PlayerTiles(N=4, E=4, W=5)
        # with self.assertRaises(AssertionError):
        for _ in range(25):
            sample = generate_sample(remaining_tiles, not_with, player_tiles)
            # sample = generate_sample(self.remaining_tiles, not_with, known_with, player_tiles)
            self.assertIn(DominoTile(1, 4), sample['E'])
            self.assertNotIn(DominoTile(1, 4), sample['N'])
            self.assertNotIn(DominoTile(1, 4), sample['W'])
            self.assertNotIn(DominoTile(5, 6), sample['N'])


    def test_invalid_player_tiles(self):
        not_with = {'N': set(), 'E': set(), 'W': set()}
        known_with = {}
        player_tiles = PlayerTiles(N=3, E=2, W=2)  # Total is 7, but we only have 6 tiles
        
        with self.assertRaises(AssertionError):
            generate_sample(self.remaining_tiles, not_with, player_tiles)
            # generate_sample(self.remaining_tiles, not_with, known_with, player_tiles)

if __name__ == '__main__':
    unittest.main()
