import unittest
from collections import namedtuple
from domino_data_types import DominoTile, PlayerTiles4
from inference import Scenario, count_scenario_outcomes
from math import comb

class TestCountScenarioOutcomes(unittest.TestCase):
    def setUp(self):
        # Define a complete set of DominoTiles (double-six set)
        self.all_tiles = set()
        for i in range(7):
            for j in range(i, 7):
                self.all_tiles.add(DominoTile(top=i, bottom=j))
        self.total_domino_tiles = len(self.all_tiles)  # Should be 28

    def test_no_tiles_assigned(self):
        """
        Test the scenario where no tiles have been assigned to any player.
        All tiles are unassigned.
        """
        scenario = Scenario(S=set(), N=set(), E=set(), W=set())
        player_tiles = PlayerTiles4(S=7, N=7, E=7, W=7)  # Total 28 tiles

        # Calculate expected outcome
        expected = comb(28, 7) * comb(21, 7) * comb(14, 7)

        result = count_scenario_outcomes(scenario, player_tiles)
        self.assertEqual(result, expected, "Failed when no tiles are assigned.")

    def test_all_tiles_assigned(self):
        """
        Test the scenario where all tiles have been assigned to players.
        Each player has exactly 7 unique tiles.
        """
        # Assign 7 unique tiles to each player
        tiles = list(self.all_tiles)
        scenario = Scenario(
            S=set(tiles[0:7]),
            N=set(tiles[7:14]),
            E=set(tiles[14:21]),
            W=set(tiles[21:28])
        )
        player_tiles = PlayerTiles4(S=7, N=7, E=7, W=7)

        # Expected outcome is 1 since there's only one way to assign these specific tiles
        expected = 1

        result = count_scenario_outcomes(scenario, player_tiles)
        self.assertEqual(result, expected, "Failed when all tiles are assigned uniquely.")

    def test_partial_tiles_assigned(self):
        """
        Test the scenario where some tiles have been assigned to players.
        """
        # Assign 3 tiles to South, 2 to North, 1 to East, and 0 to West
        assigned_s = set(list(self.all_tiles)[:3])
        assigned_n = set(list(self.all_tiles)[3:5])
        assigned_e = set(list(self.all_tiles)[5:6])
        assigned_w = set()

        scenario = Scenario(S=assigned_s, N=assigned_n, E=assigned_e, W=assigned_w)
        player_tiles = PlayerTiles4(S=7, N=7, E=7, W=7)

        # Calculate remaining tiles for each player
        s_remaining = player_tiles.S - len(scenario.S)  # 4
        n_remaining = player_tiles.N - len(scenario.N)  # 5
        e_remaining = player_tiles.E - len(scenario.E)  # 6
        w_remaining = player_tiles.W - len(scenario.W)  # 7

        total_tiles = s_remaining + n_remaining + e_remaining + w_remaining  # 22

        expected = comb(22, 4) * comb(18, 5) * comb(13, 6) * comb(7,7)

        result = count_scenario_outcomes(scenario, player_tiles)
        self.assertEqual(result, comb(22,4) * comb(18,5) * comb(13,6) * comb(7,7),
                         "Failed when partial tiles are assigned.")

    def test_insufficient_tiles(self):
        """
        Test the scenario where the number of remaining tiles is insufficient.
        """
        # Assign more tiles than available
        scenario = Scenario(
            S=set(list(self.all_tiles)[:8]),  # South has 8 tiles instead of 7
            N=set(),
            E=set(),
            W=set()
        )
        player_tiles = PlayerTiles4(S=7, N=7, E=7, W=7)

        # Expected outcome should reflect invalid scenario, likely 0
        expected = 0

        result = count_scenario_outcomes(scenario, player_tiles)
        self.assertEqual(result, expected, "Failed when assigned tiles exceed player limits.")

    def test_exhaustive_distribution(self):
        """
        Test an exhaustive distribution where players have varying numbers of tiles.
        """
        # Assign varying numbers of tiles to each player
        assigned_s = set(list(self.all_tiles)[:2])
        assigned_n = set(list(self.all_tiles)[2:5])
        assigned_e = set(list(self.all_tiles)[5:10])
        assigned_w = set(list(self.all_tiles)[10:15])

        scenario = Scenario(S=assigned_s, N=assigned_n, E=assigned_e, W=assigned_w)
        player_tiles = PlayerTiles4(S=7, N=7, E=7, W=7)

        # Remaining tiles
        s_remaining = 7 - 2  # 5
        n_remaining = 7 - 3  # 4
        e_remaining = 7 - 5  # 2
        w_remaining = 7 - 5  # 2

        total_remaining = s_remaining + n_remaining + e_remaining + w_remaining  # 13

        expected = comb(13,5) * comb(8,4) * comb(4,2) * comb(2,2)

        result = count_scenario_outcomes(scenario, player_tiles)
        self.assertEqual(result, expected, "Failed with varying numbers of assigned tiles.")

if __name__ == '__main__':
    unittest.main()