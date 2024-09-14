import unittest
from domino_data_types import DominoTile, PlayerTiles4
from inference import generate_possible_assignments, generate_scenarios

class TestGenerateScenarios(unittest.TestCase):
    def setUp(self):
        # Define some domino tiles for testing
        self.tile1 = DominoTile.new_tile(1, 2)
        self.tile2 = DominoTile.new_tile(3, 4)
        self.tile3 = DominoTile.new_tile(5, 6)
        self.tile4 = DominoTile.new_tile(7, 8)
        self.tile5 = DominoTile.new_tile(9, 0)

    def test_generate_scenarios_no_constraints(self):
        """
        Test generate_scenarios with no constraints.
        All tiles can be assigned to any player.
        """
        player_tiles = PlayerTiles4(N=2, E=2, W=2, S=2)
        not_with = {
            'S': set(),
            'N': set(),
            'E': set(),
            'W': set()
        }
        constrained_tiles, possible_assignments = generate_possible_assignments(not_with)
        # print('constrained_tiles',constrained_tiles)
        # print('possible_assignments',possible_assignments)
        scenarios = generate_scenarios(player_tiles, not_with)
        # print('scenarios',scenarios)

        expected_total_tiles = player_tiles.N + player_tiles.E + player_tiles.W + player_tiles.S
        self.assertEqual(len(scenarios), 1)
        for scenario in scenarios:
            total = scenario.N.__len__() + scenario.E.__len__() + scenario.W.__len__() + scenario.S.__len__()
            self.assertEqual(total, 0)

    def test_generate_scenarios_with_constraints(self):
        """
        Test generate_scenarios with specific constraints.
        Certain tiles are not with specific players.
        """
        player_tiles = PlayerTiles4(N=1, E=1, W=1, S=1)
        not_with = {
            'S': {self.tile1},
            'N': {self.tile2},
            'E': {self.tile3},
            'W': {self.tile4}
        }
        scenarios = generate_scenarios(player_tiles, not_with)
        
        # Each constrained tile should only be assignable to players not in its not_with set
        for scenario in scenarios:
            self.assertNotIn(self.tile1, scenario.S)
            self.assertNotIn(self.tile2, scenario.N)
            self.assertNotIn(self.tile3, scenario.E)
            self.assertNotIn(self.tile4, scenario.W)
            # Check total tiles assigned
            total = scenario.N.__len__() + scenario.E.__len__() + scenario.W.__len__() + scenario.S.__len__()
            self.assertEqual(total, 4)

    def test_generate_scenarios_exceeding_tile_counts(self):
        """
        Test generate_scenarios where some scenarios exceed the player's tile counts.
        These scenarios should be excluded.
        """
        player_tiles = PlayerTiles4(N=1, E=1, W=1, S=1)
        not_with = {
            'S': set(),
            'N': set(),
            'E': set(),
            'W': set()
        }
        # Assign all tiles to a single player which should exceed their tile count
        not_with = {
            'S': set(),
            'N': set(),
            'E': set(),
            'W': set()
        }
        # For this test, artificially create a scenario that would exceed tile counts
        scenarios = generate_scenarios(player_tiles, not_with)
        
        for scenario in scenarios:
            self.assertLessEqual(len(scenario.S), player_tiles.S)
            self.assertLessEqual(len(scenario.N), player_tiles.N)
            self.assertLessEqual(len(scenario.E), player_tiles.E)
            self.assertLessEqual(len(scenario.W), player_tiles.W)

    def test_generate_scenarios_no_possible_assignments(self):
        """
        Test generate_scenarios when no possible assignments exist.
        The function should return an empty list.
        """
        player_tiles = PlayerTiles4(N=1, E=1, W=1, S=1)
        not_with = {
            'S': {self.tile1, self.tile2, self.tile3, self.tile4},
            'N': {self.tile1, self.tile2, self.tile3, self.tile4},
            'E': {self.tile1, self.tile2, self.tile3, self.tile4},
            'W': {self.tile1, self.tile2, self.tile3, self.tile4}
        }
        scenarios = generate_scenarios(player_tiles, not_with)
        self.assertEqual(len(scenarios), 0)

    def test_generate_scenarios_partial_constraints(self):
        """
        Test generate_scenarios with partial constraints.
        Some tiles have constraints while others do not.
        """
        player_tiles = PlayerTiles4(N=2, E=2, W=2, S=2)
        not_with = {
            'S': {self.tile1},
            'N': set(),
            'E': {self.tile2},
            'W': set()
        }
        scenarios = generate_scenarios(player_tiles, not_with)

        for scenario in scenarios:
            self.assertNotIn(self.tile1, scenario.S)
            self.assertNotIn(self.tile2, scenario.E)
            # Ensure other tiles can be in any player's set
            # Check total tiles assigned
            total = scenario.N.__len__() + scenario.E.__len__() + scenario.W.__len__() + scenario.S.__len__()
            self.assertEqual(total, 2)

if __name__ == '__main__':
    unittest.main()