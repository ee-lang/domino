from collections import defaultdict, namedtuple
from dataclasses import dataclass
import itertools
from math import comb
from domino_data_types import PLAYERS, DominoTile, PlayerPosition, PlayerPosition_names, PlayerTiles4, PLAYERS_INDEX

# type TileWithPlayer = tuple[DominoTile, PlayerPosition]
type TilesWithPlayers = tuple[int, int, int, int]

# PlayerTiles4: tuple[int, int, int, int] = namedtuple('PlayerTiles4', ['S', 'N', 'E', 'W'])

@dataclass
class Scenario:
    S: set[DominoTile]
    N: set[DominoTile]
    E: set[DominoTile]
    W: set[DominoTile]

    def total_tiles(self) -> int:
        return len(self.N) + len(self.E) + len(self.W) + len(self.S)
    
def count_scenario_outcomes(
    scenario: Scenario,
    player_tiles: PlayerTiles4
) -> int:
    s_tiles = player_tiles.S - len(scenario.S)
    n_tiles = player_tiles.N - len(scenario.N)
    e_tiles = player_tiles.E - len(scenario.E)
    w_tiles = player_tiles.W - len(scenario.W)
    total_tiles = s_tiles + n_tiles + e_tiles + w_tiles
    return (comb(total_tiles, n_tiles) * 
            comb(total_tiles - n_tiles, e_tiles) *
            comb(total_tiles - n_tiles - e_tiles, w_tiles))    

# The following function is used to generate possible assignments of tiles to players
# and to generate scenarios from these assignments.
# Assumptions: 
# - No tile is constrained to only one or zero players.
def generate_possible_assignments(not_with: dict[str, set[DominoTile]]) -> tuple[list[DominoTile], list[list[str]]]:
    """
    Generate possible assignments of tiles to players.

    Args:
        not_with (dict[str, set[DominoTile]]): Dictionary of tiles known not to be with each player.

    Returns:
        tuple[list[DominoTile], list[list[str]]]: Tuple containing the list of constrained tiles and the list of possible assignments.
    """
    # players = ['S', 'E', 'N', 'W']
    constrained_tiles = set()
    for player in not_with.keys():
        for tile in not_with[player]:
            constrained_tiles.add(tile)
    
    _constrained_tiles = list(constrained_tiles)
    possible_assignments: list[list[str]] = [[] for _ in _constrained_tiles]
    # Generate all possible tile-player assignments
    for i, tile in enumerate(_constrained_tiles):
        for player in PLAYERS:
            if tile not in not_with.get(player, set()):
                possible_assignments[i].append(player)
    
    return _constrained_tiles, possible_assignments

def generate_scenarios(
    player_tiles: PlayerTiles4,
    not_with: dict[str, set[DominoTile]]
) -> list[Scenario]:
    # other_players = {'S': 'ENW','E': 'SNW', 'N': 'ESW', 'W': 'SEN'}    

    constrained_tiles, possible_assignments = generate_possible_assignments(not_with)

    valid_scenarios = []

    # Generate all possible distributions of unknown tiles
    for scenario in itertools.product(*possible_assignments):
        
        player_counts = {player: 0 for player in PLAYERS}
        for player in scenario:
            player_counts[player] += 1
        # Check if any player has exceeded their allowed tile count
        if any(player_counts[player] > getattr(player_tiles, player) for player in PLAYERS):
            continue

        player_tiles_set: list[set[DominoTile]] = [set() for _ in range(4)]
        for tile, player in zip(constrained_tiles, scenario):
            player_tiles_set[PLAYERS_INDEX[player]].add(tile)
            
        valid_scenarios.append(Scenario(S=player_tiles_set[PLAYERS_INDEX['S']], N=player_tiles_set[PLAYERS_INDEX['N']], E=player_tiles_set[PLAYERS_INDEX['E']], W=player_tiles_set[PLAYERS_INDEX['W']]))

    return valid_scenarios

def probability_from_another_perspective(unplayed_tiles: list[DominoTile], not_with_tiles: dict[str, set[DominoTile]], player_tiles: PlayerTiles4) -> dict[PlayerPosition, dict[DominoTile, float]]:
    """
    Calculate the probability of each tile being with each player from another player's perspective.

    Args:
        unplayed_tiles (list[DominoTile]): List of tiles that are not yet played.
        not_with_tiles (dict[PlayerPosition, list[DominoTile]]): Dictionary of tiles known not to be with each player.
        player_tiles (PlayerTiles): Number of tiles each player has.

    Returns:
        dict[PlayerPosition, dict[DominoTile, float]]: Probability of each tile being with each player.

    Assumes that each player has more than one tile that they can play. Tiles that are known not to be with a player are not considered choices.
    """
    assert len(unplayed_tiles) == (player_tiles.S + player_tiles.N + player_tiles.E + player_tiles.W)

    probabilities: dict[PlayerPosition, dict[DominoTile, float]] = {player: defaultdict(float) for player in range(4)}
    outcomes: dict[PlayerPosition, dict[DominoTile, int]] = {player: defaultdict(int) for player in range(4)}

    # Step 1: Determine possible tiles for each player
    possible_tiles: dict[PlayerPosition, set[DominoTile]] = {}
    for player in range(4):
        # Exclude tiles that are known not to be with the player
        possible = set(unplayed_tiles) - not_with_tiles.get(PLAYERS[player], set())
        possible_tiles[player] = possible
        assert len(possible) > 1, f'Player {player} has no choice in tile: {possible}'
    
    # Step 2: Count the number of outcomes for each tile being with each player
    for tile in unplayed_tiles:
        # Update the not_with_tiles dictionary
        # Remove the tile from the not_with_tiles dictionary as its known not to be with a player
        updated_players: list[str] = []
        for player in PLAYERS:
            if tile in not_with_tiles.get(player, set()):
                not_with_tiles[player].remove(tile)
                updated_players.append(player)
        # For each player, generate the scenarios and count the outcomes as if the tile is assigned to them
        for player in range(4):
            local_outcomes = 0
            if tile in possible_tiles[player]:
                player_tiles_local = PlayerTiles4(**{p: getattr(player_tiles, p) - (1 if player == PLAYERS_INDEX[p] else 0) for p in PLAYERS})
                tile_scenarios = generate_scenarios(player_tiles_local, not_with_tiles)
                for scenario in tile_scenarios:                    
                    local_outcomes += count_scenario_outcomes(scenario, player_tiles_local)
            outcomes[player][tile] = local_outcomes
        # Update the not_with_tiles dictionary
        for player in updated_players:
            not_with_tiles[player].add(tile)

    # Step 3: Calculate the probability of each tile being with each player
    for tile in unplayed_tiles:
        total_outcomes = sum(outcomes[player][tile] for player in range(4))
        for player in range(4):
            if total_outcomes > 0:
                probabilities[player][tile] = outcomes[player][tile] / total_outcomes
            else:
                probabilities[player][tile] = 0

    return probabilities



# def probability_from_another_perspective(unplayed_tiles: list[DominoTile], not_with_tiles: dict[PlayerPosition, list[DominoTile]], player_tiles: PlayerTiles) -> dict[PlayerPosition, dict[DominoTile, float]]:
#     """
#     Calculate the probability of each tile being with each player from another player's perspective.

#     Args:
#         unplayed_tiles (list[DominoTile]): List of tiles that are not yet played.
#         not_with_tiles (dict[PlayerPosition, list[DominoTile]]): Dictionary of tiles known not to be with each player.
#         player_tiles (PlayerTiles): Number of tiles each player has.

#     Returns:
#         dict[PlayerPosition, dict[DominoTile, float]]: Probability of each tile being with each player.
#     """
#     from collections import defaultdict

#     probabilities = {player: defaultdict(float) for player in range(4)}

#     # Step 1: Determine possible tiles for each player
#     possible_tiles = {}
#     for player in range(4):
#         # Exclude tiles that are known not to be with the player
#         possible = set(unplayed_tiles) - set(not_with_tiles.get(player, []))
#         possible_tiles[player] = possible

#     # Step 2: Calculate total number of possible tile assignments
#     total_possible_assignments = sum(len(tiles) for tiles in possible_tiles.values())

#     if total_possible_assignments == 0:
#         # If no possible assignments, return zero probabilities
#         return probabilities

#     # Step 3: Assign initial probabilities based on the proportion of tiles each player can have
#     for player in range(4):
#         num_tiles = player_tiles[player]
#         num_possible = len(possible_tiles[player])
#         if num_possible == 0 or num_tiles == 0:
#             continue
#         probability_per_tile = num_tiles / num_possible
#         for tile in possible_tiles[player]:
#             probabilities[player][tile] += probability_per_tile

#     # Step 4: Normalize probabilities so that the sum of probabilities for each tile across all players equals 1
#     for tile in unplayed_tiles:
#         total_prob = sum(probabilities[player][tile] for player in range(4))
#         if total_prob > 0:
#             for player in range(4):
#                 if tile in probabilities[player]:
#                     probabilities[player][tile] /= total_prob

#     # Step 5: Ensure that probabilities are between 0 and 1
#     for player in range(4):
#         for tile in probabilities[player]:
#             probabilities[player][tile] = min(probabilities[player][tile], 1.0)

#     return probabilities

