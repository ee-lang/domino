from domino_data_types import PLAYERS, DominoTile, PlayerPosition, PlayerPosition_EAST, PlayerPosition_NORTH, PlayerPosition_SOUTH, PlayerPosition_WEST, PlayerPosition_WEST, PlayerTiles4   
from collections import defaultdict
from enum import Enum, auto
from typing import List, Dict, Tuple
import pytest

# # Assuming the DominoTile, PlayerPosition, and PlayerTiles are defined as follows:
# # These should be imported from your actual module in practice.

# class DominoTile:
#     def __init__(self, top: int, bottom: int):
#         self.top = top
#         self.bottom = bottom

#     def __eq__(self, other):
#         return isinstance(other, DominoTile) and self.top == other.top and self.bottom == other.bottom

#     def __hash__(self):
#         return hash((self.top, self.bottom))

#     def __repr__(self):
#         return f"DominoTile({self.top}, {self.bottom})"

# class PlayerPosition(Enum):
#     SOUTH = auto()
#     EAST = auto()
#     NORTH = auto()
#     WEST = auto()

# # PlayerTiles can be a dictionary mapping PlayerPosition to the number of tiles
# PlayerTiles = Dict[PlayerPosition, int]

# Import the function to be tested
from inference import probability_from_another_perspective

# For illustration, we'll define a mock function here.
# Remove the mock and import the actual function in your tests.

# def probability_from_another_perspective(unplayed_tiles: List[DominoTile],
#                                          not_with_tiles: Dict[PlayerPosition, List[DominoTile]],
#                                          player_tiles: PlayerTiles) -> Dict[PlayerPosition, Dict[DominoTile, float]]:
#     """
#     Mock implementation for testing purposes.
#     Replace this with: from analytic_agent_w_inf import probability_from_another_perspective
#     """
#     probabilities = {player: defaultdict(float) for player in range(4)}

#     # Step 1: Determine possible tiles for each player
#     possible_tiles = {}
#     for player in range(4):
#         possible = set(unplayed_tiles) - set(not_with_tiles.get(player, []))
#         possible_tiles[player] = possible

#     # Step 2: Calculate total number of possible tile assignments
#     total_possible_assignments = sum(len(tiles) for tiles in possible_tiles.values())

#     if total_possible_assignments == 0:
#         return probabilities

#     # Step 3: Assign initial probabilities
#     for player in range(4):
#         num_tiles = player_tiles.get(player, 0)
#         num_possible = len(possible_tiles[player])
#         if num_possible == 0 or num_tiles == 0:
#             continue
#         probability_per_tile = num_tiles / num_possible
#         for tile in possible_tiles[player]:
#             probabilities[player][tile] += probability_per_tile

#     # Step 4: Normalize probabilities
#     for tile in unplayed_tiles:
#         total_prob = sum(probabilities[player][tile] for player in range(4))
#         if total_prob > 1.0:
#             for player in range(4):
#                 if tile in probabilities[player]:
#                     probabilities[player][tile] /= total_prob

#     # Step 5: Ensure probabilities are between 0 and 1
#     for player in range(4):
#         for tile in probabilities[player]:
#             probabilities[player][tile] = min(probabilities[player][tile], 1.0)

#     return probabilities

# Define fixtures or helper functions if necessary
@pytest.fixture
def sample_tiles():
    return [
        DominoTile(0, 0),
        DominoTile(0, 1),
        DominoTile(1, 1),
        DominoTile(1, 2),
        DominoTile(2, 2),
    ]

@pytest.fixture
def sample_player_tiles():
    return PlayerTiles4(S=2, N=1, E=1, W=1)
    # return {
    #     PlayerPosition_SOUTH: 2,
    #     PlayerPosition_EAST: 1,
    #     PlayerPosition_NORTH: 1,
    #     PlayerPosition_WEST: 1,
    # }

def test_all_tiles_possible(sample_tiles, sample_player_tiles):
    """
    Test when all tiles are possible for all players.
    """
    unplayed_tiles = sample_tiles.copy()
    not_with_tiles: dict[str, set[DominoTile]] = {player: set() for player in PLAYERS}

    probabilities = probability_from_another_perspective(unplayed_tiles, not_with_tiles, sample_player_tiles)

    # Calculate expected probabilities
    # Each player holds certain number of tiles
    # Total possible assignments = total tiles = 5 (each tile can be with any player)
    # Initial probabilities: player_tiles[player] / number_of_possible_tiles
    # Since all tiles are possible for all players:
    # Player SOUTH: 2/5 per tile
    # Player EAST: 1/5 per tile
    # Player NORTH: 1/5 per tile
    # Player WEST: 1/5 per tile
    # Total for each tile: 2/5 + 1/5 + 1/5 + 1/5 = 5/5 = 1.0

    for tile in unplayed_tiles:
        assert sum(probabilities[player][tile] for player in range(4)) == 1.0
        assert probabilities[PlayerPosition_SOUTH][tile] == 2/5
        assert probabilities[PlayerPosition_EAST][tile] == 1/5
        assert probabilities[PlayerPosition_NORTH][tile] == 1/5
        assert probabilities[PlayerPosition_WEST][tile] == 1/5


def test_one_tile_excluded(sample_tiles, sample_player_tiles):
    """
    Test when some tiles are excluded for certain players.
    """
    unplayed_tiles = sample_tiles.copy()
    not_with_tiles: dict[str, set[DominoTile]] = {
        'S':   {DominoTile(0, 0)},
        'E': set(),
        'N': set(),
        'W': set(),
    }

    probabilities = probability_from_another_perspective(unplayed_tiles, not_with_tiles, sample_player_tiles)
    print(probabilities)

    # Player SOUTH cannot have DominoTile(0,0)
    assert probabilities[PlayerPosition_SOUTH][DominoTile(0,0)] == 0.0
    assert probabilities[PlayerPosition_EAST][DominoTile(0,0)] == 1/3
    assert probabilities[PlayerPosition_NORTH][DominoTile(0,0)] == 1/3
    assert probabilities[PlayerPosition_WEST][DominoTile(0,0)] == 1/3


    assert probabilities[PlayerPosition_SOUTH][DominoTile(0,1)] == 0.5
    assert probabilities[PlayerPosition_EAST][DominoTile(0,1)] == 1/6
    assert probabilities[PlayerPosition_NORTH][DominoTile(0,1)] == 1/6
    assert probabilities[PlayerPosition_WEST][DominoTile(0,1)] == 1/6

    for tile in unplayed_tiles:
        if tile != DominoTile(0,0) and tile != DominoTile(0,1):
            assert probabilities[PlayerPosition_SOUTH][tile] == 0.5
            assert probabilities[PlayerPosition_EAST][tile] == 1/6
            assert probabilities[PlayerPosition_NORTH][tile] == 1/6
            assert probabilities[PlayerPosition_WEST][tile] == 1/6

    # Define a small epsilon for floating-point tolerance
    epsilon = 1e-9

    # Check normalization for remaining tiles
    for tile in unplayed_tiles:
        total_prob = sum(probabilities[player][tile] for player in range(4))
        assert total_prob <= 1.0 + epsilon, f"Total probability for {tile} exceeds 1.0: {total_prob}"


def test_some_tiles_excluded(sample_tiles, sample_player_tiles):
    """
    Test when some tiles are excluded for certain players.
    """
    unplayed_tiles = sample_tiles.copy()
    not_with_tiles = {
        'S': {DominoTile(0, 0)},
        'E': {DominoTile(0, 1), DominoTile(1, 1)},
        'N': set(),
        'W': {DominoTile(2, 2)},
    }

    probabilities = probability_from_another_perspective(unplayed_tiles, not_with_tiles, sample_player_tiles)

    # Player SOUTH cannot have DominoTile(0,0)
    assert probabilities[PlayerPosition_SOUTH][DominoTile(0,0)] == 0.0

    # Player EAST cannot have DominoTile(0,1) and DominoTile(1,1)
    assert probabilities[PlayerPosition_EAST][DominoTile(0,1)] == 0.0
    assert probabilities[PlayerPosition_EAST][DominoTile(1,1)] == 0.0

    # Player WEST cannot have DominoTile(2,2)
    assert probabilities[PlayerPosition_WEST][DominoTile(2,2)] == 0.0

    # Define a small epsilon for floating-point tolerance
    epsilon = 1e-9

    # Check normalization for remaining tiles
    for tile in unplayed_tiles:
        total_prob = sum(probabilities[player][tile] for player in range(4))
        assert total_prob <= 1.0 + epsilon, f"Total probability for {tile} exceeds 1.0: {total_prob}"

# def test_no_possible_assignments(sample_tiles):
#     """
#     Test when no possible tile assignments exist.
#     All tiles are excluded for all players.
#     """
#     unplayed_tiles = sample_tiles.copy()
#     not_with_tiles = {player: unplayed_tiles.copy() for player in PLAYERS}
#     player_tiles = PlayerTiles4(S=1, N=1, E=1, W=1)

#     probabilities = probability_from_another_perspective(unplayed_tiles, not_with_tiles, player_tiles)

#     # All probabilities should be 0.0
#     for player in range(4):
#         for tile in unplayed_tiles:
#             assert probabilities[player][tile] == 0.0

def test_partial_tile_exclusions(sample_tiles, sample_player_tiles):
    """
    Test with partial exclusions and check probability distributions.
    """
    unplayed_tiles = sample_tiles.copy()
    not_with_tiles = {
        'S': {DominoTile(0, 0), DominoTile(1, 2)},
        'E': {DominoTile(0, 1)},
        'N': {DominoTile(1, 1)},
        'W': {DominoTile(2, 2)},
    }

    probabilities = probability_from_another_perspective(unplayed_tiles, not_with_tiles, sample_player_tiles)

    # Verify excluded tiles
    assert probabilities[PlayerPosition_SOUTH][DominoTile(0,0)] == 0.0
    assert probabilities[PlayerPosition_SOUTH][DominoTile(1,2)] == 0.0
    assert probabilities[PlayerPosition_EAST][DominoTile(0,1)] == 0.0
    assert probabilities[PlayerPosition_NORTH][DominoTile(1,1)] == 0.0
    assert probabilities[PlayerPosition_WEST][DominoTile(2,2)] == 0.0

    # Check normalization for remaining tiles
    for tile in unplayed_tiles:
        total_prob = sum(probabilities[player][tile] for player in range(4))
        # Tiles excluded for some players
        # Ensure total_prob <= number_of_players_possible / possible_players holding the tile
        # In this case, normalization should ensure total_prob <=1.0
        assert total_prob <= 1.0

def test_zero_player_tiles(sample_tiles):
    """
    Test when a player has zero tiles.
    """
    unplayed_tiles = sample_tiles.copy()
    not_with_tiles: dict[str, set[DominoTile]] = {player: set() for player in PLAYERS}
    player_tiles = PlayerTiles4(S=0, N=2, E=2, W=1)
    # player_tiles = {
    #     'S': 0,
    #     'E': 2,
    #     'N': 2,
    #     'W': 1,
    # }

    probabilities = probability_from_another_perspective(unplayed_tiles, not_with_tiles, player_tiles)

    # Player SOUTH has zero tiles, all probabilities should be 0
    for tile in unplayed_tiles:
        assert probabilities[PlayerPosition_SOUTH][tile] == 0.0

    # Other players should have probabilities assigned correctly
    for tile in unplayed_tiles:
        total_prob = sum(probabilities[player][tile] for player in range(4))
        assert total_prob == 1.0

def test_single_player_possibility(sample_tiles, sample_player_tiles):
    """
    Test when only one player can have certain tiles.
    """
    unplayed_tiles = sample_tiles.copy()
    not_with_tiles = {
        'S': {DominoTile(0, 0)},
        'E': {DominoTile(0, 1), DominoTile(1, 1), DominoTile(1, 2)},
        'N': {DominoTile(0, 0), DominoTile(0, 1)},
        'W': {DominoTile(0, 0), DominoTile(0, 1), DominoTile(1, 1)},
    }

    player_tiles = PlayerTiles4(S=1, N=1, E=1, W=2)
    # player_tiles = {
    #     PlayerPosition_SOUTH: 1,
    #     PlayerPosition_EAST: 1,
    #     PlayerPosition_NORTH: 1,
    #     PlayerPosition_WEST: 2,
    # }

    probabilities = probability_from_another_perspective(unplayed_tiles, not_with_tiles, player_tiles)

    print(probabilities)
    # Only Player WEST can have DominoTile(1,2) and DominoTile(2,2)
    assert probabilities[PlayerPosition_WEST][DominoTile(1,2)] == 1.0
    assert probabilities[PlayerPosition_WEST][DominoTile(2,2)] == 1.0

    # These tiles should have probability 0.0 for others
    for player in range(4):
        if player != PlayerPosition_WEST:
            assert probabilities[player][DominoTile(1,2)] == 0.0
            assert probabilities[player][DominoTile(2,2)] == 0.0

# def test_no_unplayed_tiles():
#     """
#     Test when there are no unplayed tiles.
#     """
#     unplayed_tiles: list[DominoTile] = []
#     not_with_tiles: dict[str, set[DominoTile]] = {player: set() for player in PLAYERS}
#     player_tiles = PlayerTiles4(S=1, N=1, E=1, W=1)
#     # player_tiles = {
#     #     PlayerPosition_SOUTH: 1,
#     #     PlayerPosition_EAST: 1,
#     #     PlayerPosition_NORTH: 1,
#     #     PlayerPosition_WEST: 1,
#     # }

#     probabilities = probability_from_another_perspective(unplayed_tiles, not_with_tiles, player_tiles)

#     # probabilities should be empty for all players
#     for player in range(4):
#         assert probabilities[player] == {}

def test_player_with_all_possible_tiles(sample_tiles, sample_player_tiles):
    """
    Test when a player can have all possible tiles.
    """
    unplayed_tiles = sample_tiles.copy()
    not_with_tiles: dict[str, set[DominoTile]] = {
        'S': set(),
        'E': {DominoTile(0, 0), DominoTile(0, 1), DominoTile(1, 1)},
        'N': {DominoTile(0, 0), DominoTile(0, 1), DominoTile(1, 1)},
        'W': set(),
    }

    probabilities = probability_from_another_perspective(unplayed_tiles, not_with_tiles, sample_player_tiles)

    # Player SOUTH can have all tiles
    assert probabilities[PlayerPosition_SOUTH][DominoTile(0,0)] > 0.0  
    assert probabilities[PlayerPosition_SOUTH][DominoTile(1,2)] == 0.0  
    assert probabilities[PlayerPosition_SOUTH][DominoTile(2,2)] == 0.0  

    # Other players have restricted probabilities
    assert probabilities[PlayerPosition_EAST][DominoTile(0,0)] == 0.0
    assert probabilities[PlayerPosition_EAST][DominoTile(0,1)] == 0.0
    assert probabilities[PlayerPosition_EAST][DominoTile(1,1)] == 0.0
    assert probabilities[PlayerPosition_EAST][DominoTile(1,2)] == 0.5
    assert probabilities[PlayerPosition_EAST][DominoTile(2,2)] == 0.5

    assert probabilities[PlayerPosition_NORTH][DominoTile(0,0)] == 0.0
    assert probabilities[PlayerPosition_NORTH][DominoTile(0,1)] == 0.0
    assert probabilities[PlayerPosition_NORTH][DominoTile(1,1)] == 0.0
    assert probabilities[PlayerPosition_NORTH][DominoTile(2,2)] == 0.5
    assert probabilities[PlayerPosition_NORTH][DominoTile(1,2)] == 0.5

    assert probabilities[PlayerPosition_WEST][DominoTile(1,2)] == 0.0
    assert probabilities[PlayerPosition_WEST][DominoTile(2,2)] == 0.0


    