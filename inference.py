from collections import defaultdict, namedtuple
from dataclasses import dataclass
import itertools
from math import comb
import random
from domino_data_types import PLAYERS, DominoTile, GameState, PlayerPosition, PlayerPosition_SOUTH, PlayerPosition_names, PlayerTiles4, PLAYERS_INDEX, move
from domino_utils import list_possible_moves
from get_best_move2 import get_best_move_alpha_beta

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

    Assumes that each player has more than one tile that they can play. Tiles that are known to be with a player are not considered choices.
    """
    # Assert that the total number of unplayed tiles equals the sum of tiles remaining in each player's hand
    assert len(unplayed_tiles) == (player_tiles.S + player_tiles.N + player_tiles.E + player_tiles.W), \
        f"Number of unplayed tiles ({len(unplayed_tiles)}) does not match sum of player tiles ({player_tiles.S + player_tiles.N + player_tiles.E + player_tiles.W})\n" \
        f"Unplayed tiles: {unplayed_tiles}\n" \
        f"Player tiles: S={player_tiles.S}, N={player_tiles.N}, E={player_tiles.E}, W={player_tiles.W}"

    probabilities: dict[PlayerPosition, dict[DominoTile, float]] = {player: defaultdict(float) for player in range(4)}
    outcomes: dict[PlayerPosition, dict[DominoTile, int]] = {player: defaultdict(int) for player in range(4)}

    # Step 1: Determine possible tiles for each player
    possible_tiles: dict[PlayerPosition, set[DominoTile]] = {}
    for player_index in range(4):
        # Exclude tiles that are known not to be with the player
        possible = set(unplayed_tiles) - not_with_tiles.get(PLAYERS[player_index], set())
        possible_tiles[player_index] = possible
        # TODO: Check if this is necessary, as it may be better to just assign a probability of 1 to the tile
        # assert len(possible) > 1, f'Player {player} has no choice in tile: {possible}'
    
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
        for player_index in range(4):
            local_outcomes = 0
            if tile in possible_tiles[player_index]:
                player_tiles_local = PlayerTiles4(**{p: getattr(player_tiles, p) - (1 if player_index == PLAYERS_INDEX[p] else 0) for p in PLAYERS})
                tile_scenarios = generate_scenarios(player_tiles_local, not_with_tiles)
                for scenario in tile_scenarios:                    
                    local_outcomes += count_scenario_outcomes(scenario, player_tiles_local)
            outcomes[player_index][tile] = local_outcomes
        # Update the not_with_tiles dictionary
        for player in updated_players:
            not_with_tiles[player].add(tile)

    # Step 3: Calculate the probability of each tile being with each player
    for tile in unplayed_tiles:
        total_outcomes = sum(outcomes[player][tile] for player in range(4))
        for player_index in range(4):
            if total_outcomes > 0:
                probabilities[player_index][tile] = outcomes[player_index][tile] / total_outcomes
            else:
                probabilities[player_index][tile] = 0

    return probabilities

def generate_sample_from_game_state_from_another_perspective(unplayed_tiles: list[DominoTile], known_with_tiles: dict[str, list[DominoTile]], not_with_tiles: dict[str, set[DominoTile]], player_tiles: PlayerTiles4)-> dict[str, list[DominoTile]]:
    sample: dict[str, list[DominoTile]] = {player: [] for player in PLAYERS}

    for player in PLAYERS:
        sample[player] = known_with_tiles.get(player, [])[:]

    assert all(len(sample[player]) <= getattr(player_tiles, player) for player in PLAYERS), (
        'Sample cannot have more tiles than the player has.\n'
        f'Player S Sample: {sample["S"]}, player_tiles.S: {player_tiles.S}\n'
        f'Player N Sample: {sample["N"]}, player_tiles.N: {player_tiles.N}\n'
        f'Player E Sample: {sample["E"]}, player_tiles.E: {player_tiles.E}\n'
        f'Player W Sample: {sample["W"]}, player_tiles.W: {player_tiles.W}\n'
        f'Sample: {sample}\n'
        f'Player tiles: {player_tiles}\n'
        f'Known with tiles: {known_with_tiles}\n'
        f'Not with tiles: {not_with_tiles}\n'
        f'Unplayed tiles: {unplayed_tiles}'
    )

    known_tiles_set = set()  # Create a set to hold all known tiles
    for tiles in known_with_tiles.values():
        known_tiles_set.update(tiles)  # Add known tiles to the set

    remaining_counts = {
        player: getattr(player_tiles, player) - len(sample[player])
        for player in PLAYERS
    }

    local_not_with_tiles = {k:set(t for t in v) for k,v in not_with_tiles.items()}
    local_unplayed_tiles = [tile for tile in unplayed_tiles if tile not in known_tiles_set]  # Filter unplayed tiles

    # Assert that the number of unplayed tiles matches the sum of remaining counts
    total_remaining = sum(remaining_counts.values())
    assert len(local_unplayed_tiles) == total_remaining, \
        f"Mismatch between unplayed tiles and remaining counts:\n" \
        f"Unplayed tiles ({len(local_unplayed_tiles)}): {local_unplayed_tiles}\n" \
        f"Original unplayed tiles ({len(unplayed_tiles)}): {unplayed_tiles}\n" \
        f"Remaining counts (sum={total_remaining}): {remaining_counts}\n" \
        f"Known with tiles: {known_with_tiles}\n" \
        f"Not with tiles: {local_not_with_tiles}\n" \
        f"Original not with tiles: {not_with_tiles}"

    while local_unplayed_tiles:

        # Check if there are at least two players with tiles available
        players_with_tiles = [p for p in PLAYERS if remaining_counts[p] > 0]
        if len(players_with_tiles) < 2:
            # If only one player can receive tiles, assign all remaining tiles to that player
            last_player = players_with_tiles[0]
            sample[last_player].extend(local_unplayed_tiles)
            return sample            
        
        # print('sample',sample)
        tile_probabilities = probability_from_another_perspective(local_unplayed_tiles, local_not_with_tiles, PlayerTiles4(**remaining_counts))
        # for player in PLAYERS:
        #     print(f"{player}:")
        #     for tile, prob in tile_probabilities[PLAYERS_INDEX[player]].items():
        #         print(f"  {tile}: {prob:.4f}")
        #     print()
        
        # Choose a random tile uniformly from the local unplayed tiles
        chosen_tile = random.choice(local_unplayed_tiles)
        
        # Choose a player for the tile based on probabilities
        player_probs = [tile_probabilities[player][chosen_tile] for player in range(4)]
        chosen_player = random.choices(PLAYERS, weights=player_probs)[0]
        
        # Add the tile to the chosen player's sample
        sample[chosen_player].append(chosen_tile)
        
        # Update the remaining tiles and player tile counts
        local_unplayed_tiles.remove(chosen_tile)
        remaining_counts[chosen_player] -= 1
        
        # Update not_with_tiles
        for player in PLAYERS:
            if player in local_not_with_tiles and chosen_tile in local_not_with_tiles[player]:
                local_not_with_tiles[player].remove(chosen_tile)

    return sample

def sample_and_search4(
    unplayed_tiles: list[DominoTile],
    player_tiles: PlayerTiles4,
    known_with_tiles: dict[str, list[DominoTile]],
    not_with_tiles: dict[str, set[DominoTile]],
    board_ends: tuple[int|None, int|None],
    current_player: PlayerPosition,
    possible_moves: list[tuple[tuple[DominoTile, bool] | None, int | None, float | None]]|None = None
) -> list[tuple[move, float]]:
    """
    Sample a possible tile distribution and search for best moves using alpha-beta search.

    Args:
        unplayed_tiles: List of tiles that haven't been played yet
        player_tiles: Number of tiles each player has
        known_with_tiles: Dictionary mapping players to tiles known to be with them
        not_with_tiles: Dictionary mapping players to tiles known not to be with them
        board_ends: Current board ends (left, right)
        current_player: Current player's position
        possible_moves: Optional pre-computed list of possible moves

    Returns:
        List of tuples containing (move, score) pairs where move is (tile, is_left) or None for pass
    """

    # Assert that the number of unplayed tiles matches the sum of player tiles
    assert len(unplayed_tiles) == sum(player_tiles), f"Mismatch between unplayed tiles ({len(unplayed_tiles)}) and sum of player tiles ({sum(player_tiles)})\nUnplayed tiles: {unplayed_tiles}\nPlayer tiles counts: {player_tiles}"

    # Step 1: Generate a sample distribution of tiles
    sample = generate_sample_from_game_state_from_another_perspective(
        unplayed_tiles,
        known_with_tiles,
        not_with_tiles,
        player_tiles
    )

    # Assert that all known tiles are in the correct player's sample
    for player, known_tiles in known_with_tiles.items():
        for tile in known_tiles:
            assert tile in sample[player], f"Known tile {tile} for player {player} not found in their sampled hand: {sample[player]}"

    # Step 2: Convert sample into GameState format
    sample_hands = (
        frozenset(sample['S']),
        frozenset(sample['E']),
        frozenset(sample['N']),
        frozenset(sample['W'])
    )    

    sample_state = GameState(
        player_hands=sample_hands,
        # current_player=current_player,
        current_player=PlayerPosition_SOUTH,
        left_end=board_ends[0],
        right_end=board_ends[1],
        consecutive_passes=0
    )

    # Step 3: If possible_moves not provided, generate them
    if possible_moves is None:
        possible_moves = list_possible_moves(sample_state)

    # Step 4: Evaluate each move using alpha-beta search
    move_scores: list[tuple[move, float]] = []
    sample_cache: dict[GameState, tuple[int, int]] = {}
    
    # Use high depth to ensure we reach terminal states
    depth = 99

    for move in possible_moves:        
        # Create new state after move
        if move[0] is None:
            new_state = sample_state.pass_turn()
        else:
            tile, is_left = move[0]
            new_state = sample_state.play_hand(tile, is_left)

        # Get score for this move
        _, score, _ = get_best_move_alpha_beta(
            new_state, 
            depth,
            sample_cache,
            best_path_flag=False
        )
        
        move_scores.append((move[0], score))

    return move_scores