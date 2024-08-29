import pickle
from dataclasses import dataclass
from typing import List, Tuple, Optional, FrozenSet
from enum import Enum
from collections import deque
import argparse

class PlayerPosition(Enum):
    SOUTH = 0
    EAST = 1
    NORTH = 2
    WEST = 3

    def next(self):
        return PlayerPosition((self.value + 1) % 4)

# class PlayerPosition(Enum):
#     SOUTH = 0
#     EAST = 1
#     NORTH = 2
#     WEST = 3

#     def next(self):
#         if self.value == PlayerPosition.SOUTH.value: return PlayerPosition.EAST
#         if self.value == PlayerPosition.EAST.value: return PlayerPosition.NORTH
#         if self.value == PlayerPosition.NORTH.value: return PlayerPosition.WEST
#         return PlayerPosition.SOUTH

@dataclass(frozen=True)
class DominoTile:
    top: int
    bottom: int

    @classmethod
    def new_tile(cls, top: int, bottom: int) -> 'DominoTile':
        return cls(min(top, bottom), max(top, bottom))

    @classmethod
    def loi_to_domino_tiles(cls, tuple_list: list[tuple[int, int]]) -> list['DominoTile']:
        return [DominoTile.new_tile(left, right) for left, right in tuple_list]

    def __repr__(self):
        return f"{self.top}|{self.bottom}"

    def can_connect(self, end: Optional[int]) -> bool:
        if end is None:  # This allows any tile to be played on an empty board
            return True
        return self.top == end or self.bottom == end

    def get_other_end(self, connected_end: int) -> int:
        return self.bottom if connected_end == self.top else self.top

    def get_pip_sum(self) -> int:
        return self.top + self.bottom

@dataclass(frozen=True)
class GameState:
    player_hands: Tuple[FrozenSet[DominoTile], ...]
    current_player: PlayerPosition
    left_end: Optional[int]
    right_end: Optional[int]
    consecutive_passes: int

    def __hash__(self):
        return hash((self.player_hands, self.current_player, self.left_end, self.right_end, self.consecutive_passes))

    @classmethod
    def new_game(cls, player_hands: list[list[DominoTile]]):
        return cls(
            # player_hands=tuple(frozenset(DominoTile(top, bottom) for top, bottom in hand) for hand in player_hands),
            player_hands=tuple(frozenset(tile for tile in hand) for hand in player_hands),
            current_player=PlayerPosition.SOUTH,
            left_end=None,
            right_end=None,
            consecutive_passes=0
        )

    def play_hand(self, tile: DominoTile, left: bool) -> 'GameState':
        new_hands = list(self.player_hands)
        new_hands[self.current_player.value] = self.player_hands[self.current_player.value] - frozenset([tile])

        if self.left_end is None or self.right_end is None:
            new_left_end, new_right_end = tile.top, tile.bottom
        elif left:
            new_left_end = tile.get_other_end(self.left_end)
            new_right_end = self.right_end
        else:
            new_left_end = self.left_end
            new_right_end = tile.get_other_end(self.right_end)

        return GameState(
            player_hands=tuple(new_hands),
            current_player=self.current_player.next(),
            left_end=new_left_end,
            right_end=new_right_end,
            consecutive_passes=0
        )

    def pass_turn(self) -> 'GameState':
        return GameState(
            player_hands=self.player_hands,
            current_player=self.current_player.next(),
            left_end=self.left_end,
            right_end=self.right_end,
            consecutive_passes=self.consecutive_passes + 1
        )

    def is_game_over(self) -> bool:
        return any(len(hand) == 0 for hand in self.player_hands) or self.consecutive_passes == 4

    def get_current_hand(self) -> FrozenSet[DominoTile]:
        return self.player_hands[self.current_player.value]

# def determine_winning_pair(state: GameState) -> int:
#     # Check if a player has run out of tiles
#     for i, hand in enumerate(state.player_hands):
#         if len(hand) == 0:
#             return i % 2

#     # If we're here, the game must be blocked
#     pair_0_pips = sum(tile.get_pip_sum() for hand in state.player_hands[::2] for tile in hand)
#     pair_1_pips = sum(tile.get_pip_sum() for hand in state.player_hands[1::2] for tile in hand)

#     if pair_1_pips == pair_0_pips:
#         return -1
#     return 1 if pair_1_pips < pair_0_pips else 0

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

# def list_possible_moves(state: GameState, cache: dict = {}) -> list[tuple[DominoTile, bool, int, float]]:
#     """
#     List all possible moves for the current player in the given game state,
#     along with the number of possible outcomes and expected score for each move.

#     :param state: The current GameState
#     :param cache: The cache dictionary to use for memoization
#     :return: A list of tuples (tile, is_left, possible_outcomes, expected_score)
#     """
#     current_hand = state.get_current_hand()
#     possible_moves = []

#     # If the board is empty, the first player can play any tile
#     if state.right_end is None and state.left_end is None:
#         for tile in current_hand:
#             new_state = state.play_hand(tile, left=True)  # Direction doesn't matter for the first tile
#             total_games, expected_score = count_game_stats(new_state, print_stats=False, cache=cache)
#             possible_moves.append((tile, True, total_games, expected_score))
#     else:
#         # Try playing each tile in the current player's hand
#         for tile in current_hand:
#             if tile.can_connect(state.left_end):
#                 new_state = state.play_hand(tile, left=True)
#                 total_games, expected_score = count_game_stats(new_state, print_stats=False, cache=cache)
#                 possible_moves.append((tile, True, total_games, expected_score))

#             if tile.can_connect(state.right_end) and state.left_end != state.right_end:
#                 new_state = state.play_hand(tile, left=False)
#                 total_games, expected_score = count_game_stats(new_state, print_stats=False, cache=cache)
#                 possible_moves.append((tile, False, total_games, expected_score))

#     # If the player can't play, include the option to pass
#     if not possible_moves:
#         new_state = state.pass_turn()
#         total_games, expected_score = count_game_stats(new_state, print_stats=False, cache=cache)
#         possible_moves.append((None, None, total_games, expected_score))

#     # Sort moves by expected score (descending order)
#     possible_moves.sort(key=lambda x: x[3], reverse=True)

#     return possible_moves


def list_possible_moves(state: GameState, cache: dict = {}, include_stats: bool = True) -> list[tuple[tuple[DominoTile, bool]|None, Optional[int], Optional[float]]]:
    """
    List all possible moves for the current player in the given game state,
    optionally including the number of possible outcomes and expected score for each move.

    :param state: The current GameState
    :param cache: The cache dictionary to use for memoization
    :param include_stats: Whether to include possible outcomes and expected score (default True)
    :return: A list of tuples (tile, is_left, possible_outcomes, expected_score)
             If include_stats is False, possible_outcomes and expected_score will be None
    """
    current_hand = state.get_current_hand()
    possible_moves: list[tuple[tuple[DominoTile, bool]|None, int|None, float|None]] = []

    # If the board is empty, the first player can play any tile
    if state.right_end is None and state.left_end is None:
        for tile in current_hand:
            if include_stats:
                new_state = state.play_hand(tile, left=True)  # Direction doesn't matter for the first tile
                total_games, total_score = count_game_stats(new_state, print_stats=False, cache=cache)
                expected_score = total_score / total_games if total_games > 0 else 0
                possible_moves.append(((tile, True), total_games, expected_score))
            else:
                possible_moves.append(((tile, True), None, None))
    else:
        # Try playing each tile in the current player's hand
        for tile in current_hand:
            if tile.can_connect(state.left_end):
                if include_stats:
                    new_state = state.play_hand(tile, left=True)
                    total_games, total_score = count_game_stats(new_state, print_stats=False, cache=cache)
                    expected_score = total_score / total_games if total_games > 0 else 0
                    possible_moves.append(((tile, True), total_games, expected_score))
                else:
                    possible_moves.append(((tile, True), None, None))

            if tile.can_connect(state.right_end) and state.left_end != state.right_end:
                if include_stats:
                    new_state = state.play_hand(tile, left=False)
                    total_games, total_score = count_game_stats(new_state, print_stats=False, cache=cache)
                    expected_score = total_score / total_games if total_games > 0 else 0
                    possible_moves.append(((tile, False), total_games, expected_score))
                else:
                    possible_moves.append(((tile, False), None, None))

    # If the player can't play, include the option to pass
    if not possible_moves:
        if include_stats:
            new_state = state.pass_turn()
            total_games, total_score = count_game_stats(new_state, print_stats=False, cache=cache)
            expected_score = total_score / total_games if total_games > 0 else 0
            possible_moves.append((None, total_games, expected_score))
            # possible_moves.append((None, None, total_games, expected_score))
        else:
            # possible_moves.append((None, None, None, None))
            possible_moves.append((None, None, None))

    # Sort moves by expected score (descending order) if stats are included
    if include_stats:
        # possible_moves.sort(key=lambda x: x[3] if x[3] is not None else float('-inf'), reverse=True)
        possible_moves.sort(key=lambda x: x[2] if x[2] is not None else float('-inf'), reverse=True)

    return possible_moves


# def count_game_stats(state: GameState, cache: dict = None) -> int:
#     if cache is None:
#         cache = {}

#     if state in cache:
#         return cache[state]

#     global score_acc

#     if state.is_game_over():
#         winner, pair_0_pips, pair_1_pips = determine_winning_pair(state)
#         winning_stats[winner] += 1
#         score_acc += 0 if winner == -1 else (pair_0_pips+pair_1_pips)*(1 if winner==0 else -1)
#         cache[state] = 1    
#         return 1

#     total_games = 0
#     current_hand = state.get_current_hand()
#     moves_made = 0

#     # If the board is empty, the first player can play any tile
#     if state.right_end is None and state.left_end is None:
#         for tile in current_hand:
#             new_state = state.play_hand(tile, left=True)  # Direction doesn't matter for the first tile
#             total_games += count_game_stats(new_state)
#             moves_made += 1
#     else:
#         # Try playing each tile in the current player's hand
#         for tile in current_hand:
#             if tile.can_connect(state.left_end):
#                 new_state = state.play_hand(tile, left=True)
#                 total_games += count_game_stats(new_state)
#                 moves_made += 1

#             if tile.can_connect(state.right_end) and state.left_end != state.right_end:
#                 new_state = state.play_hand(tile, left=False)
#                 total_games += count_game_stats(new_state)
#                 moves_made += 1

#     # If the player can't play, pass the turn
#     if moves_made == 0:
#         new_state = state.pass_turn()
#         total_games = count_game_stats(new_state)

#     cache[state] = total_games
#     return total_games


cache_hit: int = 0
cache_miss: int = 0
# def count_game_stats(initial_state: GameState, print_stats: bool = True, cache: dict = {}) -> tuple[int, float]:
#     global cache_hit, cache_miss
#     stack = deque([initial_state])
#     # cache = {}
#     winning_stats = {-1: 0, 0: 0, 1: 0}
#     total_score: int = 0
#     total_games: int = 0

#     while stack:
#         state = stack.pop()
#         # print(f'processing state {state}')

#         if state in cache:
#             cache_hit += 1
#             games, score = cache[state]
#             total_games += games
#             total_score += score
#             continue
#         else:
#             cache_miss +=1

#         if state.is_game_over():
#             winner, pair_0_pips, pair_1_pips = determine_winning_pair(state)
#             winning_stats[winner] += 1
#             score = 0 if winner == -1 else (pair_0_pips+pair_1_pips)*(1 if winner==0 else -1)
#             cache[state] = (1, score)
#             total_games += 1
#             total_score += score
#             continue

#         moves = []
#         current_hand = state.get_current_hand()

#         # If the board is empty, the first player can play any tile
#         if state.right_end is None and state.left_end is None:
#             moves = [(tile, True) for tile in current_hand]
#         else:
#             # Try playing each tile in the current player's hand
#             for tile in current_hand:
#                 if tile.can_connect(state.left_end):
#                     moves.append((tile, True))
#                 if tile.can_connect(state.right_end) and state.left_end != state.right_end:
#                     moves.append((tile, False))

#         # If the player can't play, pass the turn
#         if not moves:
#             new_state = state.pass_turn()
#             stack.append(new_state)
#         else:
#             for tile, left in moves:
#                 new_state = state.play_hand(tile, left)
#                 stack.append(new_state)

#     # Calculate total games
#     # total_games = sum(cache.values())
#     # total_games = len(cache.values())
#     # total_games = sum(winning_stats.values())
#     # exp_score = score_acc / total_games
#     exp_score = total_score / total_games if total_games > 0 else 0 

#     if print_stats:
#         print(f"Number of possible game outcomes: {total_games}")
#         print('Winning stats:', winning_stats)
#         print(f'Expected score: {exp_score:.4f}')
#         print(f'Cache hits: {cache_hit}')        
#         print(f'Cache misses: {cache_miss}')        

#     return total_games, exp_score


def count_game_stats(initial_state: GameState, print_stats: bool = True, cache: dict = {}) -> tuple[int, float]:
    global cache_hit, cache_miss
    
    # stack: list[tuple[GameState, list[tuple[DominoTile, bool]]]] = [(initial_state, [])]  # Stack contains (state, path) pairs
    stack: list[tuple[GameState, list[GameState]]] = [(initial_state, [])]  # Stack contains (state, path) pairs
    winning_stats = {-1: 0, 0: 0, 1: 0}
    
    while stack:
        state, path = stack.pop()

        if state in cache:
            cache_hit += 1
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
        
        cache_miss += 1

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
        print(f'Cache hits: {cache_hit}')        
        print(f'Cache misses: {cache_miss}')
        print(f'Total cached states: {len(cache)}')

    return total_games, exp_score


# import math

# def min_max_domino(state: GameState, depth: int, cache: dict = {}) -> Tuple[Optional[Tuple[DominoTile, bool]], float, List[Tuple[PlayerPosition, Optional[Tuple[DominoTile, bool]]]]]:
#     """
#     Implement the min-max algorithm for the domino game, including the optimal path.
    
#     :param state: The current GameState
#     :param depth: The depth to search in the game tree
#     :param cache: The cache dictionary to use for memoization
#     :return: A tuple of (best_move, best_score, optimal_path)
#     """
#     if depth == 0 or state.is_game_over():
#         _, total_score = count_game_stats(state, print_stats=False, cache=cache)
#         return None, total_score, []

#     current_player = state.current_player
#     is_maximizing = current_player in (PlayerPosition.NORTH, PlayerPosition.SOUTH)
    
#     best_score = -math.inf if is_maximizing else math.inf
#     best_move = None
#     best_path = []
    
#     possible_moves = list_possible_moves(state, cache)
    
#     for move in possible_moves:
#         tile, is_left, _, _ = move
        
#         if tile is None:  # Pass move
#             new_state = state.pass_turn()
#         else:
#             new_state = state.play_hand(tile, is_left)
        
#         _, score, path = min_max_domino(new_state, depth - 1, cache)
        
#         if (is_maximizing and score > best_score) or (not is_maximizing and score < best_score):
#             best_score = score
#             best_move = (tile, is_left)
#             best_path = [(current_player, (tile, is_left))] + path
    
#     return best_move, best_score, best_path

# def get_best_move(state: GameState, depth: int, cache: dict = {}) -> Tuple[Optional[Tuple[DominoTile, bool]], float, List[Tuple[PlayerPosition, Optional[Tuple[DominoTile, bool]]]]]:
#     """
#     Get the best move for the current player using the min-max algorithm, including the optimal path.
    
#     :param state: The current GameState
#     :param depth: The depth to search in the game tree
#     :param cache: The cache dictionary to use for memoization
#     :return: A tuple of (best_move, best_score, optimal_path)
#     """
#     return min_max_domino(state, depth, cache)

import math

def min_max_alpha_beta(state: GameState, depth: int, alpha: float, beta: float, cache: dict = {}) -> tuple[Optional[tuple[DominoTile, bool]], float, list[tuple[PlayerPosition, Optional[Tuple[DominoTile, bool]]]]]:
    """
    Implement the min-max algorithm with alpha-beta pruning for the domino game, including the optimal path.
    
    :param state: The current GameState
    :param depth: The depth to search in the game tree
    :param alpha: The best value that the maximizer currently can guarantee at that level or above
    :param beta: The best value that the minimizer currently can guarantee at that level or above
    :param cache: The cache dictionary to use for memoization
    :return: A tuple of (best_move, best_score, optimal_path)
    """
    if depth == 0 or state.is_game_over():
        _, total_score = count_game_stats(state, print_stats=False, cache=cache)
        return None, total_score, []

    current_player = state.current_player
    is_maximizing = current_player in (PlayerPosition.NORTH, PlayerPosition.SOUTH)
    
    best_move = None
    best_path = []
    
    possible_moves = list_possible_moves(state, cache, include_stats=False)
    
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
                best_path = [(current_player, tile_and_loc_info)] + path
            
            beta = min(beta, best_score)
            if beta <= alpha:
                break  # Alpha cut-off
    
    return best_move, best_score, best_path

def get_best_move_alpha_beta(state: GameState, depth: int, cache: dict = {}) -> tuple[Optional[tuple[DominoTile, bool]], float, list[tuple[PlayerPosition, Optional[tuple[DominoTile, bool]]]]]:
    """
    Get the best move for the current player using the min-max algorithm with alpha-beta pruning, including the optimal path.
    
    :param state: The current GameState
    :param depth: The depth to search in the game tree
    :param cache: The cache dictionary to use for memoization
    :return: A tuple of (best_move, best_score, optimal_path)
    """
    return min_max_alpha_beta(state, depth, -math.inf, math.inf, cache)


# def setup_game_state(initial_hands: List[List[Tuple[int, int]]], 
#                      starting_player: PlayerPosition, 
#                      first_moves: List[Optional[Tuple[int, int, bool]]]) -> GameState:
#     """
#     Set up a game state based on initial hands, starting player, and first moves.
    
#     :param initial_hands: List of initial hands for each player
#     :param starting_player: The player who starts the game
#     :param first_moves: List of first moves. Each move is a tuple (top, bottom, left) or None for pass
#     :return: The resulting GameState after applying the first moves
#     """
#     state = GameState.new_game(initial_hands)
#     state = GameState(
#         player_hands=state.player_hands,
#         current_player=starting_player,
#         left_end=state.left_end,
#         right_end=state.right_end,
#         consecutive_passes=state.consecutive_passes
#     )

#     for move in first_moves:
#         if move is None:
#             state = state.pass_turn()
#         else:
#             top, bottom, left = move
#             tile = next((t for t in state.get_current_hand() if (t.top == top and t.bottom == bottom) or (t.top == bottom and t.bottom == top)), None)
#             if tile is None:
#                 raise ValueError(f"Tile {top}|{bottom} not found in current player's hand")
#             state = state.play_hand(tile, left)

#     return state


def setup_game_state(
    initial_hands: list[list[DominoTile]], 
    starting_player: PlayerPosition, 
    first_moves: list[Optional[tuple[DominoTile, bool]]]
) -> GameState:
    """
    Set up a game state based on initial hands, starting player, and first moves.

    :param initial_hands: List of initial hands for each player, where each hand is a list of DominoTile objects
    :param starting_player: The player who starts the game
    :param first_moves: List of first moves. Each move is a tuple (DominoTile, bool) or None for pass
    :return: The resulting GameState after applying the first moves
    """
    # Initialize the game state with the given hands
    state = GameState.new_game([[tile for tile in hand] for hand in initial_hands])
    
    # Set the starting player
    state = GameState(
        player_hands=state.player_hands,
        current_player=starting_player,
        left_end=state.left_end,
        right_end=state.right_end,
        consecutive_passes=state.consecutive_passes
    )

    # Apply the first moves
    for move in first_moves:
        if move is None:
            state = state.pass_turn()
        else:
            tile, left = move
            # Find and play the tile from the current player's hand
            if tile not in state.get_current_hand():
                print('state.get_current_hand()',state.get_current_hand())
                raise ValueError(f"Tile {tile} not found in current player's hand")
            state = state.play_hand(tile, left)

    return state


def analyze_moves_backward(initial_hands: list[list[DominoTile]],
                           starting_player: PlayerPosition,
                           moves: list[Optional[tuple[DominoTile, bool]]],
                           from_move: int = 0,
                           cache: dict = {}) -> list[tuple[PlayerPosition, Optional[tuple[DominoTile, bool]], int, float, float]]:
    results: list[tuple[PlayerPosition, Optional[tuple[DominoTile, bool]], int, float, float]] = []
    
    print("\nMove Analysis (working backwards):")
    print("Player\tMove\t\tPossible Outcomes\tExpected Score\tDelta")
    print("------\t----\t\t------------------\t--------------\t-----")
    
    previous_exp_score = None
    
    for i in range(len(moves), from_move, -1):
        current_moves = moves[:i]
        current_state = setup_game_state(initial_hands, starting_player, current_moves)
        
        total_games, exp_score = count_game_stats(current_state, print_stats=False, cache=cache)

        current_player = PlayerPosition((current_state.current_player.value - 1) % 4)

        move = moves[i-1] if i > from_move else None
        
        if previous_exp_score is not None:
            delta = exp_score - previous_exp_score
            print(f'{-delta:+.4f}')
        else:
            delta = 0.0        

        move_str = f"({move[0]},{move[1]})" if move else "Pass"
        player_str = current_player.name
        print(f"{player_str:<6}\t{move_str:<12}\t{total_games:<18}\t{exp_score:<14.4f}\t", end='')
        # print(f"{player_str:<6}\t{move_str:<12}\t{total_games:<18}\t{exp_score:<14.4f}\t{delta:+.4f}")
        
        results.insert(0, (current_player, move, total_games, exp_score, delta))
        previous_exp_score = exp_score
    
    return results

def load_cache(filename: str) -> dict:
    try:
        with open(filename, 'rb') as f:
            return pickle.load(f)
    except FileNotFoundError:
        print(f"Cache file {filename} not found. Starting with an empty cache.")
        return {}

def save_cache(cache: dict, filename: str):
    with open(filename, 'wb') as f:
        pickle.dump(cache, f)

def main():
    parser = argparse.ArgumentParser(description="Domino Game Analyzer")
    parser.add_argument("--cache", type=str, help="Specify a cache file to use")
    parser.add_argument("--min-max-only", action="store_true", help="Run only the min-max algorithm")    
    args = parser.parse_args()

    cache = {}
    if args.cache:
        try:
            with open(args.cache, 'rb') as f:
                cache = pickle.load(f)
            print(f"Loaded cache from {args.cache}")
        except FileNotFoundError:
            print(f"Cache file {args.cache} not found. Starting with an empty cache.")


    initial_hands_orig = [
    [(0,3), (6,4), (0,6), (0,0), (4,0), (4,1), (5,0)],
    [(3,6), (5,4), (2,5), (3,3), (1,3), (5,1), (1,1)],
    [(6,6), (2,6), (0,2), (6,5), (3,4), (2,3), (2,1)],
    [(4,4), (2,4), (2,2), (1,6), (5,5), (0,1), (3,5)]
    ]

    initial_hands: list[list[DominoTile]]
    for i, _hand in enumerate(initial_hands_orig):
        initial_hands.append([DominoTile.new_tile(*t) for t in _hand])

    starting_player = PlayerPosition.SOUTH
    moves = [(DominoTile.new_tile(move[0], move[1]), move[2]) if move is not None else None
             for move in [
                (0, 0, True), 
                None,
                (0, 2, True),
                (2, 2, True),
                (4, 0, False),
                (4, 5, False),
                (6, 5, False),
                (1, 6, False),
                (4, 1, False),            
                (2, 5, True),
                (3, 4, False),
                (5, 5, True),        
                (5, 0, True),        
                (3, 3, False),
                (2, 3, False),
                (0, 1, True),
                None,
                (1, 3, True),

                (1, 2, False), 
                # (3, 5, True),
                # None,
                # (5, 1, True),    
                # None,
                # None,
                # None,
                # (1, 1, True)            
             ]]

    # Optimal
    # moves = [
    #     # (0, 0, True), 
    #     # None,
    #     # (0, 2, True),
    #     # (2, 2, True),
    #     # (4, 0, False),
    #     # (2, 5, True),
    #     # (6, 5, True),
        
    #     # (2, 4, False),

    #     # (1, 6, True),
    #     # (4, 1, False),            
    #     # (1, 1, True),
    #     # (2, 1, True),
    #     # (2, 4, True),        
    #     # (6, 4, True),        
    #     # (5, 1, False),
    #     # (6, 6, True),
    #     # (3, 5, False),
    #     # (0, 6, True),
    #     # (3, 3, False), 
    #     # (2, 3, False),
    #     # (0, 1, True),
    #     # None,
    #     # (1, 3, True), 
    #     # (2, 6, False),
    #     # None,
    # ]

    final_state = setup_game_state(initial_hands, starting_player, moves)
    if not args.min_max_only:
        print("Starting analysis...")
        results = analyze_moves_backward(initial_hands, starting_player, moves, from_move=0, cache=cache)
        print("\nAnalysis complete.")

        print("\nFinal Game State:")
        print(f"Current player: {final_state.current_player}")
        print(f"Board ends: {final_state.left_end} | {final_state.right_end}")
        for i, hand in enumerate(final_state.player_hands):
            print(f"Player {PlayerPosition(i).name}'s hand: {hand}")

        count_game_stats(final_state, cache=cache)  # This will print the stats for the final state

        # Add this section to list possible moves
        print("\nPossible moves for the current player:")
        possible_moves = list_possible_moves(final_state, cache=cache)
        for tile_and_loc_info, outcomes, score in possible_moves:
            if tile_and_loc_info is None:
                print(f"Pass: {outcomes} possible outcomes, expected score: {score:.4f}")
            else:
                tile, is_left = tile_and_loc_info
                direction = "left" if is_left else "right"
                print(f"Play {tile} on the {direction}: {outcomes} possible outcomes, expected score: {score:.4f}")

    # Update this section to get and display the best move and optimal path using min-max algorithm
    # print("\nBest move and optimal path using Min-Max algorithm:")
    print("\nBest move and optimal path using Min-Max algorithm with Alpha-Beta pruning:")
    depth = 24  # You can adjust this depth based on your performance requirements
    # best_move, best_score, optimal_path = get_best_move(final_state, depth, cache=cache)
    best_move, best_score, optimal_path = get_best_move_alpha_beta(final_state, depth, cache=cache)
    if best_move is None:
        print(f"Best move: Pass, Expected score: {best_score:.4f}")
    else:
        tile, is_left = best_move
        direction = "left" if is_left else "right"
        print(f"Best move: Play {tile} on the {direction}, Expected score: {best_score:.4f}")
    
    print("\nOptimal path:")
    for i, (player, move) in enumerate(optimal_path):
        if move is None:
            print(f"{i+1}. {player.name}: Pass")
        else:
            tile, is_left = move
            direction = "left" if is_left else "right"
            print(f"{i+1}. {player.name}: Play {tile} on the {direction}")


    if args.cache:
        with open(args.cache, 'wb') as f:
            pickle.dump(cache, f)
        print(f"Saved cache to {args.cache}")

if __name__ == "__main__":
    main()