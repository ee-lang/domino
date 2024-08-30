# from domino_probabiliy_calc import calculate_tile_probabilities
# from domino_game_analyzer import DominoTile, PlayerPosition

# # def calculate_tile_probabilities(
# #     remaining_tiles: list[DominoTile],
# #     not_with: dict[str, set[DominoTile]],
# #     player_tiles: PlayerTiles
# # ) -> dict[DominoTile, dict[str, float]]:

# Current board: (1, 5)
# HumanPlayer.update_missing_tiles 1 1 4
# HumanPlayer.played_tiles {(0, 1), (2, 4), (1, 2), (0, 4), (3, 4), (1, 5), (4, 6), (0, 2), (0, 5), (2, 2), (1, 6), (3, 5), (4, 4), (1, 1), (1, 4), (2, 3), (4, 5), (5, 6), (3, 6)}
# HumanPlayer.unplayed_tiles (7 remaining): [0|0, 1|3, 2|5, 2|6, 3|3, 5|5, 6|6]
# HumanPlayer.remaining_tiles_per_suit: {0: 1, 1: 1, 2: 2, 3: 2, 5: 2, 6: 2}
# HumanPlayer.possible_tiles_for_player_1: [(0, 0), (2, 5), (2, 6), (3, 3), (5, 5), (6, 6)]
# HumanPlayer.possible_tiles_for_player_3: [(0, 0), (3, 3), (5, 5), (6, 6)]
# HumanPlayer.hand: [0|6, 0|3]
# HumanPlayer.hand_stats: ['0: 2', '3: 1', '6: 1', '1: 0', '2: 0', '4: 0', '5: 0']
# Number of tiles per player: [2, 3, 2, 2]
# _starting_player PlayerPosition.WEST
# current_player PlayerPosition.SOUTH
# _final_remaining_tiles {5|5, 0|0, 3|3, 2|6, 6|6, 2|5, 1|3}
# _board_ends (1, 5)
# _player_tiles_count {<PlayerPosition.SOUTH: 0>: 2, <PlayerPosition.EAST: 1>: 3, <PlayerPosition.NORTH: 2>: 2, <PlayerPosition.WEST: 3>: 2}

# tile 0|0
# valid_players ['E', 'W']
# tile_probs {'N': 0.0, 'E': 0.0, 'W': 0.0}
# remaining_counts {'N': 0, 'E': 1, 'W': 1}
# local_not_with {'E': {1|3}, 'N': set(), 'W': {1|3}}


from domino_probability_calc import calculate_tile_probabilities, PlayerTiles,generate_scenarios, generate_sample
from domino_game_analyzer import DominoTile
import copy

def test_calculate_probabilities():
    # Define remaining tiles
    remaining_tiles = [
        DominoTile(0, 0), DominoTile(1, 3), DominoTile(2, 5), DominoTile(2, 6),
        DominoTile(3, 3), DominoTile(5, 5), DominoTile(6, 6),
        # DominoTile(2, 4), DominoTile(3, 6)  # Tiles in human player's hand
    ]

    # Define not_with based on _knowledge_tracker
    not_with = {
        'E': {DominoTile(1, 3)},
        'N': set(),
        'W': {DominoTile(1, 3)}
    }

    # Define player_tiles (assuming 7 tiles per player at the start)
    player_tiles = PlayerTiles(N=2, E=3, W=2)

    # Call calculate_tile_probabilities
    probabilities = calculate_tile_probabilities(remaining_tiles, not_with, player_tiles)

    # Print the results
    for tile, probs in probabilities.items():
        print(f"Tile {tile}:")
        for player, prob in probs.items():
            print(f"  P({player} has {tile}) = {prob:.6f}")
        print()

def test_calculate_probabilities2():
# tile 0|6
# probabilities[tile] {'N': 0.3333333333333333, 'E': 0.0, 'W': 0.0}
# not_with {'E': set(), 'N': {5|6, 1|4}, 'W': {1|4}}
# not_with_local {'E': set(), 'N': {5|6, 1|4}, 'W': {1|4}}
# known_with_local {'W': {0|6}}
# prob.sum 0.3333333333333333
# scenarios []
# player_tiles PlayerTiles(N=1, E=1, W=1)
    # Remaining tiles: [0|0, 0|1, 0|2, 0|6, 1|3, 1|4, 1|5, 1|6, 2|2, 2|3, 2|6, 3|3, 5|6]

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

    # Call calculate_tile_probabilities
    # probabilities = calculate_tile_probabilities(remaining_tiles, not_with, player_tiles)
    # Print the results
    # for tile, probs in probabilities.items():
    #     print(f"Tile {tile}:")
    #     for player, prob in probs.items():
    #         print(f"  P({player} has {tile}) = {prob:.6f}")
    #     print()

    player_tiles = PlayerTiles(N=4, E=4, W=5)
    sample = generate_sample(remaining_tiles, not_with, player_tiles)
    print('sample',sample)



def test_generate_scenarios():
    player_tiles = [DominoTile(5,6)]
    not_with = {'E': set(), 'N': set(), 'W': {DominoTile(5,6)}}
    known_with = {'N': set(), 'E': set(), 'W': set()}
    player_tiles =  PlayerTiles(N=5, E=6, W=6)
    scenarios = generate_scenarios(player_tiles, not_with, known_with)
    print(scenarios)
    print("known_with['N'].union(known_with['E']).union(known_with['W'])",known_with['N'].union(known_with['E']).union(known_with['W']))
    not_with_local = copy.deepcopy(not_with)
    # If found a duplication in not_with, it's added now to known_with and need to be removed from not_with
    if any(len(s)>0 for s in known_with.values()): 
        for p, p_set in not_with_local.items():
            not_with_local[p] = not_with_local[p] - known_with['N'].union(known_with['E']).union(known_with['W'])
    print('not_with_local',not_with_local)

if __name__ == "__main__":
    test_calculate_probabilities2()
    # test_generate_scenarios()