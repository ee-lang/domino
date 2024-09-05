# from domino_game_analyzer import GameState, DominoTile, PlayerPosition, PlayerPosition_SOUTH, PlayerPosition_NORTH
import math
from domino_data_types import GameState, DominoTile, move, PlayerPosition, PlayerPosition_SOUTH, PlayerPosition_NORTH
from domino_utils import list_possible_moves

def min_max_alpha_beta(state: GameState, depth: int, alpha: float, beta: float, cache: dict[GameState, tuple[int, int]] = {}, best_path_flag: bool = True) -> tuple[move, float, list[tuple[PlayerPosition, move]]]:
    """
    Implement the min-max algorithm with alpha-beta pruning for the domino game, including the optimal path.
    
    :param state: The current GameState
    :param depth: The depth to search in the game tree
    :param alpha: The best value that the maximizer currently can guarantee at that level or above
    :param beta: The best value that the minimizer currently can guarantee at that level or above
    :param cache: The cache dictionary to use for memoization
    :param best_path_flag: Flag to indicate if best_path is needed or not    
    :return: A tuple of (best_move, best_score, optimal_path)
    """
    if depth == 0 or state.is_game_over():
        _, total_score = count_game_stats(state, print_stats=False, cache=cache)
        return None, total_score, []

    current_player = state.current_player
    # is_maximizing = current_player in (PlayerPosition.NORTH, PlayerPosition.SOUTH)
    is_maximizing = current_player in (PlayerPosition_NORTH, PlayerPosition_SOUTH)
    
    best_move = None
    best_path = []
    
    possible_moves = list_possible_moves(state)
    
    if is_maximizing:
        best_score = -math.inf
        for move in possible_moves:
            tile_and_loc_info, _, _ = move
            # tile, is_left = tile_info if tile_info is not None else (None, None)
            
            # if tile is None:  # Pass move
            if tile_and_loc_info is None:  # Pass move
                new_state = state.pass_turn()
            else:
                # assert is_left is not None
                tile, is_left = tile_and_loc_info
                new_state = state.play_hand(tile, is_left)
            
            _, score, path = min_max_alpha_beta(new_state, depth - 1, alpha, beta, cache)
            
            if score > best_score:
                best_score = score
                # best_move = (tile, is_left)
                # best_path = [(current_player, (tile, is_left))] + path
                best_move = tile_and_loc_info
                if best_path_flag:
                    best_path = [(current_player, tile_and_loc_info)] + path
            
            alpha = max(alpha, best_score)
            if beta <= alpha:
                break  # Beta cut-off
    else:
        best_score = math.inf
        for move in possible_moves:
            tile_and_loc_info, _, _ = move
            # tile, is_left = tile_and_loc_info if tile_and_loc_info is not None else (None, None)
            
            # if tile is None:  # Pass move
            if tile_and_loc_info is None:  # Pass move
                new_state = state.pass_turn()
            else:
                # assert is_left is not None
                tile, is_left = tile_and_loc_info
                new_state = state.play_hand(tile, is_left)
            
            _, score, path = min_max_alpha_beta(new_state, depth - 1, alpha, beta, cache)
            
            if score < best_score:
                best_score = score
                # best_move = (tile, is_left)
                best_move = tile_and_loc_info
                # best_path = [(current_player, (tile, is_left))] + path
                if best_path_flag:
                    best_path = [(current_player, tile_and_loc_info)] + path
            
            beta = min(beta, best_score)
            if beta <= alpha:
                break  # Alpha cut-off
    
    return best_move, best_score, best_path

def get_best_move_alpha_beta(state: GameState, depth: int, cache: dict[GameState, tuple[int, int]] = {}, best_path_flag: bool = True) -> tuple[move, float, list[tuple[PlayerPosition, move]]]:
    """
    Get the best move for the current player using the min-max algorithm with alpha-beta pruning, including the optimal path.
    
    :param state: The current GameState
    :param depth: The depth to search in the game tree
    :param cache: The cache dictionary to use for memoization
    :param best_path_flag: Flag to indicate if best_path is needed or not
    :return: A tuple of (best_move, best_score, optimal_path)
    """
    return min_max_alpha_beta(state, depth, -math.inf, math.inf, cache, best_path_flag)

# cache_hit: int = 0
# cache_miss: int = 0

def count_game_stats(initial_state: GameState, print_stats: bool = True, cache: dict[GameState, tuple[int, int]] = {}) -> tuple[int, float]:
    # global cache_hit, cache_miss
    
    # stack: list[tuple[GameState, list[tuple[DominoTile, bool]]]] = [(initial_state, [])]  # Stack contains (state, path) pairs
    stack: list[tuple[GameState, list[GameState]]] = [(initial_state, [])]  # Stack contains (state, path) pairs
    winning_stats = {-1: 0, 0: 0, 1: 0}
    
    while stack:
        state, path = stack.pop()

        if state in cache:
            # cache_hit += 1
            total_games, total_score = cache[state]
            
            # Update all states in the path with this result
            for path_state in reversed(path):
                if path_state in cache:
                    cache[path_state] = (
                        cache[path_state][0] + total_games,
                        cache[path_state][1] + total_score
                    )
                else:
                    cache[path_state] = (total_games, total_score)
            
            continue
        
        # cache_miss += 1

        if state.is_game_over():
            winner, pair_0_pips, pair_1_pips = determine_winning_pair(state)
            winning_stats[winner] += 1
            score = 0 if winner == -1 else (pair_0_pips + pair_1_pips) * (1 if winner == 0 else -1)
            total_games, total_score = 1, score
            
            # Cache the result for this terminal state
            cache[state] = (total_games, total_score)
            
            # Update all states in the path with this result
            for path_state in reversed(path):
                if path_state in cache:
                    cache[path_state] = (
                        cache[path_state][0] + total_games,
                        cache[path_state][1] + total_score
                    )
                else:
                    cache[path_state] = (total_games, total_score)
        else:
            current_hand = state.get_current_hand()
            moves = []

            # Generate possible moves
            if state.right_end is None and state.left_end is None:
                moves = [(tile, True) for tile in current_hand]
            else:
                for tile in current_hand:
                    if tile.can_connect(state.left_end):
                        moves.append((tile, True))
                    if tile.can_connect(state.right_end) and state.left_end != state.right_end:
                        moves.append((tile, False))

            # If no moves are possible, pass the turn
            if not moves:
                new_state = state.pass_turn()
                stack.append((new_state, path + [state]))
            else:
                for tile, left in moves:
                    new_state = state.play_hand(tile, left)
                    stack.append((new_state, path + [state]))

    # Calculate final statistics
    total_games, total_score = cache[initial_state]
    exp_score = total_score / total_games if total_games > 0 else 0

    if print_stats:
        print(f"Number of possible game outcomes: {total_games}")
        print('Winning stats:', winning_stats)
        print(f'Expected score: {exp_score:.4f}')
        # print(f'Cache hits: {cache_hit}')        
        # print(f'Cache misses: {cache_miss}')
        print(f'Total cached states: {len(cache)}')

    return total_games, exp_score

def determine_winning_pair(state: GameState) -> tuple[int, int, int]:

    pair_0_pips = sum(tile.get_pip_sum() for hand in state.player_hands[::2] for tile in hand)
    pair_1_pips = sum(tile.get_pip_sum() for hand in state.player_hands[1::2] for tile in hand)

    # Check if a player has run out of tiles
    for i, hand in enumerate(state.player_hands):
        if len(hand) == 0:
            # print(f'player {i} domino')
            return i % 2, pair_0_pips, pair_1_pips

    # If we're here, the game must be blocked
    if pair_1_pips == pair_0_pips:
        result = -1
    else:
        result = 1 if pair_1_pips < pair_0_pips else 0
    return result, pair_0_pips, pair_1_pips


