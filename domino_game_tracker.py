# from typing import List, Tuple, Optional, Set
# from collections import namedtuple
# from domino_game_analyzer import GameState, PlayerPosition, DominoTile, setup_game_state
# from domino_common_knowledge import CommonKnowledgeTracker, normalize_tile

import numpy as np
from statistics import mode, mean, variance
from collections import defaultdict, Counter
from domino_game_analyzer import get_best_move_alpha_beta, list_possible_moves
# from domino_probability_calc import generate_sample, PlayerTiles  # Ensure this import is correct

# # PlayerTiles = namedtuple('PlayerTiles', ['N', 'E', 'W'])

# from collections import defaultdict
# from domino_probability_calc import calculate_tile_probabilities


from typing import Optional
from collections import defaultdict
from domino_game_analyzer import GameState, PlayerPosition, DominoTile, setup_game_state
from domino_common_knowledge import CommonKnowledgeTracker
from domino_probability_calc import calculate_tile_probabilities, PlayerTiles, generate_sample
from statistics import mean, median, stdev
import copy


def rotate_player_tiles_count(
    player_tiles_count: dict[PlayerPosition, int], 
    new_south: PlayerPosition
) -> dict[PlayerPosition, int]:
    """
    Rotate the values in player_tiles_count so that the given PlayerPosition becomes the new South.

    :param player_tiles_count: A dictionary mapping each PlayerPosition to the number of tiles they have.
    :param new_south: The PlayerPosition that should become the new South.
    :return: A new dictionary with the values rotated accordingly.
    """
    rotations = (new_south.value - PlayerPosition.SOUTH.value) % 4
    
    rotated_player_tiles_count: dict[PlayerPosition, int] = {}
    for position, count in player_tiles_count.items():
        new_position = PlayerPosition((position.value - rotations) % 4)
        rotated_player_tiles_count[new_position] = count

    return rotated_player_tiles_count


def domino_game_state_our_perspective(
    remaining_tiles: set[DominoTile],
    moves: list[Optional[tuple[DominoTile, bool]]],
    initial_player_tiles: dict[PlayerPosition, int],
    current_player: PlayerPosition = PlayerPosition.SOUTH
) -> tuple[PlayerPosition, set[DominoTile], tuple[Optional[int], Optional[int]], dict[PlayerPosition, int], CommonKnowledgeTracker]:
    knowledge_tracker = CommonKnowledgeTracker()

    # # Initialize the count of tiles for each player
    # player_tiles_count: dict[PlayerPosition, int] = {
    #     PlayerPosition.NORTH: initial_player_tiles.N,
    #     PlayerPosition.EAST: initial_player_tiles.E,
    #     PlayerPosition.WEST: initial_player_tiles.W,
    #     PlayerPosition.SOUTH: initial_player_tiles.E  # Assuming South starts with the same number as East
    # }
    player_tiles_count = initial_player_tiles

    board_ends: tuple[Optional[int], Optional[int]] = (None, None)  # (left_end, right_end)

    for move in moves:
        if move is None:
            # Player passes, update common knowledge
            knowledge_tracker.update_pass(current_player, board_ends[0], board_ends[1])
        else:
            tile, left = move
            # Update board ends
            if board_ends[0] is None:  # First move
                board_ends = (tile.top, tile.bottom)
            elif left:
                board_ends = (tile.get_other_end(board_ends[0]), board_ends[1])
            else:
                assert board_ends[1] is not None
                board_ends = (board_ends[0], tile.get_other_end(board_ends[1]))

            # Update tile counts and remaining tiles
            remaining_tiles.discard(tile)
            knowledge_tracker.update_play(tile)
            player_tiles_count[current_player] -= 1

        # Move to next player
        current_player = PlayerPosition((current_player.value + 1) % 4)

    # Return the current player, remaining tiles, board ends, tile counts, and the knowledge tracker
    return current_player, remaining_tiles, board_ends, player_tiles_count, knowledge_tracker


# def domino_game_state_our_perspective(
#     remaining_tiles: set[DominoTile],
#     moves: list[Optional[tuple[DominoTile, bool]]],
#     initial_player_tiles: PlayerTiles,
#     current_player = PlayerPosition.SOUTH
# ):
#     knowledge_tracker = CommonKnowledgeTracker()

#     # Initialize the count of tiles for each player
#     player_tiles_count = {
#         PlayerPosition.NORTH: initial_player_tiles.N,
#         PlayerPosition.EAST: initial_player_tiles.E,
#         PlayerPosition.WEST: initial_player_tiles.W,
#         PlayerPosition.SOUTH: initial_player_tiles.E  # Assuming South starts with the same number as East
#     }

#     board_ends: tuple[int|None, int|None] = (None, None)  # (left_end, right_end)

#     for move in moves:
#         if move is None:
#             # Player passes, update common knowledge
#             knowledge_tracker.update_pass(current_player, board_ends[0], board_ends[1])
#         else:
#             tile, left = move
#             # Update board ends
#             if board_ends[0] is None:  # First move
#                 board_ends = (tile.top, tile.bottom)
#             elif left:
#                 board_ends = (tile.get_other_end(board_ends[0]), board_ends[1])
#             else:
#                 assert board_ends[1] is not None
#                 board_ends = (board_ends[0], tile.get_other_end(board_ends[1]))

#             # Update tile counts and remaining tiles
#             remaining_tiles.discard(tile)
#             knowledge_tracker.update_play(tile)
#             player_tiles_count[current_player] -= 1

#         # Move to next player
#         current_player = PlayerPosition((current_player.value + 1) % 4)

#     # Infer knowledge based on the remaining tiles and observed moves
#     inferred_knowledge: dict[PlayerPosition, set[DominoTile]] = {
#         player: set() for player in PlayerPosition
#     }

#     for tile in remaining_tiles:
#         for player in PlayerPosition:
#             if tile.top in knowledge_tracker.common_knowledge_missing_suits[player] or tile.bottom in knowledge_tracker.common_knowledge_missing_suits[player]:
#                 inferred_knowledge[player].add(tile)

#     return current_player, remaining_tiles, board_ends, player_tiles_count, inferred_knowledge


# def domino_game_state_our_perspective(south_hand: set[DominoTile],
#                                       remaining_tiles: set[DominoTile],
#                                       moves: list[Optional[tuple[DominoTile, bool]]],
#                                       initial_player_tiles: PlayerTiles):
#     knowledge_tracker = CommonKnowledgeTracker()

#     # Initialize the count of tiles for each player
#     player_tiles_count = {
#         PlayerPosition.NORTH: initial_player_tiles.N,
#         PlayerPosition.EAST: initial_player_tiles.E,
#         PlayerPosition.WEST: initial_player_tiles.W,
#         PlayerPosition.SOUTH: len(south_hand)
#     }

#     current_player = PlayerPosition.SOUTH
#     board_ends: tuple[int|None, int|None] = (None, None)  # (left_end, right_end)

#     for move in moves:
#         if move is None:
#             # Player passes, update common knowledge
#             knowledge_tracker.update_pass(current_player, board_ends[0], board_ends[1])
#         else:
#             tile, left = move
#             # Update board ends
#             # if board_ends[0] is None or board_ends[1] is None:  # First move
#             if board_ends[0] is None:  # First move
#                 board_ends = (tile.top, tile.bottom)
#             elif left:
#                 board_ends = (tile.get_other_end(board_ends[0]), board_ends[1])
#             else:
#                 assert board_ends[1] is not None
#                 board_ends = (board_ends[0], tile.get_other_end(board_ends[1]))

#             # Update tile counts and remaining tiles
#             if current_player == PlayerPosition.SOUTH:
#                 south_hand.remove(tile)
#             else:
#                 remaining_tiles.discard(tile)
#                 knowledge_tracker.update_play(tile)

#             player_tiles_count[current_player] -= 1

#         # Move to next player
#         current_player = PlayerPosition((current_player.value + 1) % 4)

#     # Infer knowledge based on the remaining tiles and observed moves
#     inferred_knowledge: dict[PlayerPosition, set[DominoTile]] = {
#         player: set() for player in PlayerPosition if player != PlayerPosition.SOUTH
#     }

#     for tile in remaining_tiles:
#         for player in PlayerPosition:
#             if player != PlayerPosition.SOUTH:
#                 if tile.top in knowledge_tracker.common_knowledge[player] or tile.bottom in knowledge_tracker.common_knowledge[player]:
#                     inferred_knowledge[player].add(tile)

#     # Convert inferred knowledge to the format expected by calculate_tile_probabilities
#     not_with: dict[str, set[DominoTile]] = defaultdict(set)
#     for player, tiles in inferred_knowledge.items():
#         not_with[player.name[0]] = tiles  # Use the first letter of the player's name as the key

#     player_tiles = PlayerTiles(
#         N=player_tiles_count[PlayerPosition.NORTH],
#         E=player_tiles_count[PlayerPosition.EAST],
#         W=player_tiles_count[PlayerPosition.WEST]
#     )

#     # Calculate the probabilities for remaining tiles
#     probabilities = calculate_tile_probabilities(list(remaining_tiles), not_with, player_tiles)

#     return current_player, south_hand, remaining_tiles, board_ends, player_tiles_count, inferred_knowledge, probabilities



# # Assuming you have already defined PlayerTiles and imported other necessary modules

# def domino_game_state_our_perspective(south_hand: List[Tuple[int, int]],
#                                       remaining_tiles: Set[Tuple[int, int]],
#                                       moves: List[Optional[Tuple[int, int, bool]]],
#                                       initial_player_tiles: PlayerTiles):
#     # Initialize the known hands
#     initial_hands = [south_hand, [], [], []]  # Only South's hand is known
#     state = setup_game_state(initial_hands, PlayerPosition.SOUTH, [])
#     knowledge_tracker = CommonKnowledgeTracker()

#     # Initialize the count of tiles for each player
#     player_tiles_count = {
#         PlayerPosition.NORTH: initial_player_tiles.N,
#         PlayerPosition.EAST: initial_player_tiles.E,
#         PlayerPosition.WEST: initial_player_tiles.W,
#     }

#     # Convert remaining tiles to a set of DominoTile objects with smaller number first
#     remaining_tiles = {DominoTile(min(top, bottom), max(top, bottom)) for top, bottom in remaining_tiles}

#     for move in moves:
#         current_player = state.current_player
#         if move is None:
#             # Player passes, update common knowledge
#             knowledge_tracker.update_pass(current_player, state.left_end, state.right_end)
#             state = state.pass_turn()
#         else:
#             # Player plays a tile
#             top, bottom, left = move
#             tile = DominoTile(min(top, bottom), max(top, bottom))

#             # If the move is from South, remove the tile from our hand
#             if current_player == PlayerPosition.SOUTH:
#                 state = state.play_hand(tile, left)
#             else:
#                 # For other players, remove the tile from the remaining tiles
#                 remaining_tiles.discard(tile)
#                 knowledge_tracker.update_play(tile)
#                 state = state.play_hand(tile, left)
#                 # Decrease the count of tiles for the current player
#                 player_tiles_count[current_player] -= 1

#     # Infer knowledge based on the remaining tiles and observed moves
#     inferred_knowledge = {
#         player: set() for player in PlayerPosition if player != PlayerPosition.SOUTH
#     }

#     for tile in remaining_tiles:
#         for player in inferred_knowledge:
#             if tile.top in knowledge_tracker.common_knowledge[player] or tile.bottom in knowledge_tracker.common_knowledge[player]:
#                 inferred_knowledge[player].add(tile)

#     # Convert inferred knowledge to the format expected by calculate_tile_probabilities
#     not_with = defaultdict(set)
#     for player, tiles in inferred_knowledge.items():
#         not_with[player.name[0]] = {f'{tile.top}-{tile.bottom}' for tile in tiles}

#     player_tiles = PlayerTiles(
#         N=player_tiles_count[PlayerPosition.NORTH],
#         E=player_tiles_count[PlayerPosition.EAST],
#         W=player_tiles_count[PlayerPosition.WEST]
#     )

#     # Calculate the probabilities for remaining tiles
#     remaining_tile_tuples = [(tile.top, tile.bottom) for tile in remaining_tiles]
#     probabilities = calculate_tile_probabilities(remaining_tile_tuples, not_with, player_tiles)

#     return state, inferred_knowledge, remaining_tiles, player_tiles_count, probabilities


def generate_sample_from_game_state(
    current_player: PlayerPosition,
    south_hand: set[DominoTile],
    remaining_tiles: set[DominoTile],
    player_tiles_count: dict[PlayerPosition, int],
    inferred_knowledge: dict[PlayerPosition, set[DominoTile]]
) -> dict[str, set[DominoTile]]:

    # Convert inferred_knowledge to the format expected by generate_sample
    not_with: dict[str, set[DominoTile]] = {
        player.name[0]: tiles for player, tiles in inferred_knowledge.items() if player != PlayerPosition.SOUTH
    }

    # Known tiles (South's hand)
    known_with: dict[str, set[DominoTile]] = {'S': south_hand}

    # Create PlayerTiles object for the remaining players
    player_tiles = PlayerTiles(
        N=player_tiles_count[PlayerPosition.NORTH],
        E=player_tiles_count[PlayerPosition.EAST],
        W=player_tiles_count[PlayerPosition.WEST]
    )

    # Assert that the lengths match
    assert len(remaining_tiles) == sum(e for e in player_tiles)

    # Generate a sample
    sample = generate_sample(list(remaining_tiles), not_with, known_with, player_tiles)

    return sample

# Example usage
if __name__ == "__main__":
    # Create DominoTile objects for south_hand
    # south_hand = {DominoTile(min(top, bottom), max(top, bottom)) for top, bottom in [(0, 3), (6, 4), (0, 6), (0, 0), (4, 0), (4, 1), (5, 0)]}
    initial_south_hand = {DominoTile(min(top, bottom), max(top, bottom)) for top, bottom in [(0, 3), (6, 4), (0, 6), (0, 0), (4, 0), (4, 1), (5, 0)]}

    initial_north_hand = {DominoTile(min(top, bottom), max(top, bottom)) for top, bottom in [(6, 6), (2, 6), (0, 2), (6, 5), (3, 4), (2, 3), (2, 1)]}

    # Create DominoTile objects for remaining_tiles
    remaining_tiles = {
        DominoTile(min(top, bottom), max(top, bottom)) for top, bottom in {
            (3, 6), (5, 4), (2, 5), (3, 3), (1, 3), (5, 1), (1, 1),
            (6, 6), (2, 6), (0, 2), (6, 5), (3, 4), (2, 3), (2, 1),
            (4, 4), (2, 4), (2, 2), (1, 6), (5, 5), (0, 1), (3, 5)
        }
    }

    # Update moves to use DominoTile objects
    moves = [(DominoTile(min(move[0], move[1]), max(move[0], move[1])), move[2]) if move is not None else None
             for move in [
                 (0, 0, True),
                 None,
                 (0, 2, True),
                 (2, 2, True),
                 (4, 0, False),
                 (4, 5, False),
                 (6, 5, False),
                 (1, 6, False),
                 # (4, 1, False),
                 # (2, 5, True),
                #  (3, 4, False),
                #  (5, 5, True),
                # (5, 0, True),        
                # (3, 3, False),
                # (2, 3, False),
                # (0, 1, True),
                # None,
                # (1, 3, True),
                # (1, 2, False), 
                # (3, 5, True),
                # None,
                # (5, 1, True),    
                # None,
                # None,
                # None,
                # (1, 1, True)   
             ]]

    # initial_player_tiles = PlayerTiles(N=7, E=7, W=7)
    initial_player_tiles: dict[PlayerPosition, int] = {
        PlayerPosition.NORTH: 7,
        PlayerPosition.EAST: 7,
        PlayerPosition.WEST: 7,
        PlayerPosition.SOUTH: 7
    }

    remaining_tiles = remaining_tiles.union(initial_south_hand)

    # current_player, final_south_hand, final_remaining_tiles, board_ends, player_tiles_count, inferred_knowledge, probabilities = domino_game_state_our_perspective(
    #     south_hand, remaining_tiles, moves, initial_player_tiles)
    current_player, final_remaining_tiles, board_ends, player_tiles_count, knowledge_tracker = domino_game_state_our_perspective(
        remaining_tiles, moves, initial_player_tiles)

    print('knowledge_tracker pre-rotation', knowledge_tracker)
    knowledge_tracker = knowledge_tracker.rotate_perspective(current_player)
    print('knowledge_tracker post-rotation', knowledge_tracker)

    inferred_knowledge: dict[PlayerPosition, set[DominoTile]] = {
        player: set() for player in PlayerPosition
    }

    for tile in remaining_tiles:
        for player in PlayerPosition:
            if tile.top in knowledge_tracker.common_knowledge_missing_suits[player] or tile.bottom in knowledge_tracker.common_knowledge_missing_suits[player]:
                inferred_knowledge[player].add(tile)


    # Infer the current south_hand
    print('final_remaining_tiles',final_remaining_tiles)
    current_south_hand = initial_south_hand.intersection(final_remaining_tiles)
    # current_south_hand = initial_north_hand.intersection(final_remaining_tiles)
    print('current_south_hand',current_south_hand)

    # Print results
    print(f"Current player: {current_player}")
    print(f"Board ends: {board_ends[0]} | {board_ends[1]}")
    print(f"South's current hand: {current_south_hand}")

    print("\nNumber of tiles each player has:")
    for player, count in player_tiles_count.items():
        print(f"{player.name} has {count} tiles.")

    print("\nInferred Knowledge:")
    for player, tiles in inferred_knowledge.items():
        print(f"Player {player.name} is known not to have tiles: {[f'{t}' for t in tiles]}")

    print("\nRemaining Tiles:")
    print([f'{tile.top}|{tile.bottom}' for tile in final_remaining_tiles])

    # print("\nProbabilities of Remaining Tiles:")
    # for tile, probs in probabilities.items():
    #     print(f"Tile {tile}:")
    #     for player, prob in probs.items():
    #         print(f"  P({player} has {tile}) = {prob:.6f}")

    final_south_hand = current_south_hand
    # print('final_south_hand',final_south_hand)
    final_remaining_tiles_without_south_tiles = remaining_tiles - final_south_hand 
    # print('final_remaining_tiles_without_south_tiles',final_remaining_tiles_without_south_tiles, len(final_remaining_tiles_without_south_tiles))
    # print('player_tiles_count pre',player_tiles_count)
    # player_tiles_count = rotate_player_tiles_count(player_tiles_count, PlayerPosition.NORTH)
    # print('player_tiles_count post',player_tiles_count)
    inferred_knowledge_for_current_player = copy.deepcopy(inferred_knowledge)
    for player, tiles in inferred_knowledge_for_current_player.items():
        inferred_knowledge_for_current_player[player] = tiles - final_south_hand
    # print('reviewed inferred_knowledge', inferred_knowledge_for_current_player)

    num_samples = 1000
    move_scores = defaultdict(list)

    for _ in range(num_samples):
        # Generate a sample based on the current game state
        sample = generate_sample_from_game_state(
            # current_player,
            PlayerPosition.SOUTH,
            final_south_hand,
            final_remaining_tiles_without_south_tiles,
            player_tiles_count,
            inferred_knowledge_for_current_player
        )

        # Create a game state from the sample. The order is important!
        sample_hands = (
            frozenset(final_south_hand),  # South's hand
            frozenset(sample['E']),       # East's hand
            frozenset(sample['N']),       # North's hand
            frozenset(sample['W'])        # West's hand
        )

        # Create a new GameState object
        sample_state = GameState(
            player_hands=sample_hands,
            # current_player=current_player,
            current_player=PlayerPosition.SOUTH,
            left_end=board_ends[0],
            right_end=board_ends[1],
            consecutive_passes=0  # Assuming we start with 0 consecutive passes
        )

        # Get the list of possible moves
        possible_moves = list_possible_moves(sample_state, include_stats=False)

        # Analyze each possible move
        move_analysis = []        
        # Find the best move using get_best_move_alpha_beta
        depth = 24  # You can adjust this depth based on your performance requirements
        for move in possible_moves:
            if move[0] is None:  # Pass move
                new_state = sample_state.pass_turn()
            else:
                tile, is_left = move[0]
                new_state = sample_state.play_hand(tile, is_left)
            
            # best_move, best_score, optimal_path = get_best_move_alpha_beta(new_state, depth)
            best_move, best_score, __ = get_best_move_alpha_beta(new_state, depth)
            
            move_analysis.append({
                'move': move[0],
                'resulting_best_move': best_move,
                'expected_score': best_score
                # 'optimal_path': optimal_path
            })
            if move[0] is not None:  # Pass move
                # print(f'Move {move[0]} resulted in {best_score}')
                move_scores[move[0]].append(best_score)

        # best_move, best_score, _ = get_best_move_alpha_beta(sample_state, depth)

        # best_move, best_score, optimal_path = get_best_move_alpha_beta(sample_state, depth)

        # tile, is_left = best_move
        # direction = "left" if is_left else "right"
        # print('='*25)
        # print('Partner hand', sample['N'])
        # print(f"Best move: Play {tile} on the {direction}, Expected score: {best_score:.4f}")

        # print("\nOptimal path:")
        # for i, (player, move) in enumerate(optimal_path):
        #     if move is None:
        #         print(f"{i+1}. {player.name}: Pass")
        #     else:
        #         tile, is_left = move
        #         direction = "left" if is_left else "right"
        #         print(f"{i+1}. {player.name}: Play {tile} on the {direction}")


        # # Record the move and score
        # move_scores[best_move].append(best_score)

    # Calculate statistics for each move
    move_statistics = {}
    for _move, scores in move_scores.items():
        move_statistics[_move] = {
            "count": len(scores),
            "mean": mean(scores),
            "std_dev": stdev(scores) if len(scores) > 1 else 0,
            "median": median(scores),
            "mode": mode(scores),
            "min": min(scores),
            "max": max(scores)
        }

    # Sort moves by their mean score, descending order
    sorted_moves = sorted(move_statistics.items(), key=lambda x: x[1]["mean"], reverse=True)

    # Print statistics for each move
    print(f"\nMove Statistics (based on {num_samples} samples):")
    for __move, stats in sorted_moves:
        if __move is None:
            move_str = "Pass"
        else:
            tile, is_left = __move
            direction = "left" if is_left else "right"
            move_str = f"Play {tile} on the {direction}"
        
        print(f"\nMove: {move_str}")
        print(f"  Count: {stats['count']}")
        print(f"  Mean Score: {stats['mean']:.4f}")
        print(f"  Standard Deviation: {stats['std_dev']:.4f}")
        print(f"  Median Score: {stats['median']:.4f}")
        print(f"  Mode Score: {stats['mode']:.4f}")
        print(f"  Min Score: {stats['min']:.4f}")
        print(f"  Max Score: {stats['max']:.4f}")

    # Identify the best move based on the highest mean score
    best_move = max(move_statistics, key=lambda x: move_statistics[x]["mean"])
    best_stats = move_statistics[best_move]

    print("\nBest Move Overall:")
    if best_move is None:
        print(f"Best move: Pass")
    else:
        tile, is_left = best_move
        direction = "left" if is_left else "right"
        print(f"Best move: Play {tile} on the {direction}")
    print(f"Mean Expected Score: {best_stats['mean']:.4f}")
    print(f"Frequency: {best_stats['count']} out of {num_samples} samples")
