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


from domino_probability_calc import calculate_tile_probabilities,generate_scenarios, generate_sample
from domino_data_types import DominoTile, PlayerTiles, PlayerPosition_SOUTH, GameState, PlayerPosition
from analytic_agent_player_parallel import AnalyticAgentPlayer
from domino_game_tracker import domino_game_state_our_perspective, generate_sample_from_game_state
from domino_utils import history_to_domino_tiles_history
from get_best_move2 import list_possible_moves
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

# def test_calculate_probabilities2():
# # tile 0|6
# # probabilities[tile] {'N': 0.3333333333333333, 'E': 0.0, 'W': 0.0}
# # not_with {'E': set(), 'N': {5|6, 1|4}, 'W': {1|4}}
# # not_with_local {'E': set(), 'N': {5|6, 1|4}, 'W': {1|4}}
# # known_with_local {'W': {0|6}}
# # prob.sum 0.3333333333333333
# # scenarios []
# # player_tiles PlayerTiles(N=1, E=1, W=1)
#     # Remaining tiles: [0|0, 0|1, 0|2, 0|6, 1|3, 1|4, 1|5, 1|6, 2|2, 2|3, 2|6, 3|3, 5|6]

#     remaining_tiles = set([
#         DominoTile(0, 0), DominoTile(0, 1), DominoTile(0, 2), DominoTile(0, 6),
#         DominoTile(1, 3), DominoTile(1, 4), DominoTile(1, 5), DominoTile(1, 6),
#         DominoTile(2, 2), DominoTile(2, 3), DominoTile(2, 6), DominoTile(3, 3),
#         DominoTile(5, 6)
#         # DominoTile(2, 4), DominoTile(3, 6)  # Tiles in human player's hand
#     ])

#     # Define not_with based on _knowledge_tracker
#     not_with = {
#         'E': set(),
#         'N': {DominoTile(5, 6), DominoTile(1, 4)},
#         'W': {DominoTile(1, 4)}
#     }

#     # Define player_tiles (assuming 7 tiles per player at the start)
#     player_tiles = PlayerTiles(N=1, E=1, W=1)

#     # Call calculate_tile_probabilities
#     # probabilities = calculate_tile_probabilities(remaining_tiles, not_with, player_tiles)
#     # Print the results
#     # for tile, probs in probabilities.items():
#     #     print(f"Tile {tile}:")
#     #     for player, prob in probs.items():
#     #         print(f"  P({player} has {tile}) = {prob:.6f}")
#     #     print()

#     player_tiles = PlayerTiles(N=4, E=4, W=5)
#     sample = generate_sample(remaining_tiles, not_with, player_tiles)
#     print('sample',sample)



# def test_generate_scenarios():
#     player_tiles = [DominoTile(5,6)]
#     not_with = {'E': set(), 'N': set(), 'W': {DominoTile(5,6)}}
#     known_with = {'N': set(), 'E': set(), 'W': set()}
#     player_tiles =  PlayerTiles(N=5, E=6, W=6)
#     scenarios = generate_scenarios(player_tiles, not_with, known_with)
#     print(scenarios)
#     print("known_with['N'].union(known_with['E']).union(known_with['W'])",known_with['N'].union(known_with['E']).union(known_with['W']))
#     not_with_local = copy.deepcopy(not_with)
#     # If found a duplication in not_with, it's added now to known_with and need to be removed from not_with
#     if any(len(s)>0 for s in known_with.values()): 
#         for p, p_set in not_with_local.items():
#             not_with_local[p] = not_with_local[p] - known_with['N'].union(known_with['E']).union(known_with['W'])
#     print('not_with_local',not_with_local)


def test_initial_moves() -> None:

# Player's hand: [4|6, 1|3, 2|2, 3|4, 0|4, 2|6, 2|3]
# Remaining tiles: [0|0, 0|1, 0|2, 0|3, 0|5, 0|6, 1|1, 1|2, 1|4, 1|5, 1|6, 2|4, 2|5, 3|3, 3|5, 3|6, 4|4, 4|5, 5|5, 5|6, 6|6]
# Move Statistics (based on 5 samples):

# Move: Play 3|4 on the left
#   Count: 5
#   Mean Score: -5.5000
#   Standard Deviation: 46.9441
#   Median Score: -30.0000
#   Mode Score: -30.0000
#   Min Score: -44.0000
#   Max Score: 68.0000

# Best Move Overall:
# Best move: Play 3|4 on the left
# Mean Expected Score: -5.5000
# First move: (3, 4)
        ai_player = AnalyticAgentPlayer()
        verbose = True
        # unplayed_tiles = self.get_unplayed_tiles(game_state, player_hand)
        unplayed_tiles = [(0,0), (0,1), (0,2), (0,3), (0,5), (0,6), (1,1), (1,2), (1,4), (1,5), (1,6), (2,4), (2,5), (3,3), (3,5), (3,6), (4,4), (4,5), (5,5), (5,6), (6,6)]
        _unplayed_tiles = DominoTile.loi_to_domino_tiles(unplayed_tiles)

        player_hand = [(4,6), (1,3), (2,2), (3,4), (0,4), (2,6), (2,3)]
        _player_hand = DominoTile.loi_to_domino_tiles(player_hand)

        # _moves = history_to_domino_tiles_history(game_state.history)
        _moves = history_to_domino_tiles_history([])
        _remaining_tiles = set(_unplayed_tiles)
        # _initial_player_tiles = {p: 7 for p in PlayerPosition}
        _initial_player_tiles = {p: 7 for p in range(4)}
        # _starting_player = PlayerPosition((game_state.history[0][0] - self.position)%4) if len(game_state.history)>0 else PlayerPosition.SOUTH
        _starting_player = PlayerPosition_SOUTH

        current_player, _final_remaining_tiles, _board_ends, _player_tiles_count, _knowledge_tracker = domino_game_state_our_perspective(
            _remaining_tiles, _moves, _initial_player_tiles, current_player=_starting_player)

        if verbose:
            ai_player.print_verbose_info(_player_hand, _unplayed_tiles, _knowledge_tracker, _player_tiles_count, _starting_player)

        # num_samples = 1000 if len(game_state.history) > 8 else 100 if len(game_state.history) > 4 else 25 if len(game_state.history) > 0 else 1
        num_samples = 1
        best_move = ai_player.get_best_move(set(_player_hand), _remaining_tiles, _knowledge_tracker, _player_tiles_count, _board_ends, num_samples, verbose=True)

        # inferred_knowledge: dict[PlayerPosition, set[DominoTile]] = {
        #     player: set() for player in range(4)
        # }

        # sample = generate_sample_from_game_state(
        #     # PlayerPosition.SOUTH,
        #     PlayerPosition_SOUTH,
        #     set(_player_hand),
        #     set(_unplayed_tiles),
        #     _player_tiles_count,
        #     inferred_knowledge
        # )

        # sample_hands = (
        #     frozenset(_player_hand),
        #     frozenset(sample['E']),
        #     frozenset(sample['N']),
        #     frozenset(sample['W'])
        # )

        # sample_state = GameState(
        #     player_hands=sample_hands,
        #     # current_player=PlayerPosition.SOUTH,
        #     current_player=PlayerPosition_SOUTH,
        #     left_end=_board_ends[0],
        #     right_end=_board_ends[1],
        #     consecutive_passes=0
        # )

        # possible_moves = list_possible_moves(sample_state)

        # print('possible_moves', possible_moves)


if __name__ == "__main__":
    # test_calculate_probabilities2()
    # test_generate_scenarios()
    test_initial_moves()