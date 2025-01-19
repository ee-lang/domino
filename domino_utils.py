from typing import Dict, Set
# from domino_game_analyzer import DominoTile  # Removed redundant import
from domino_data_types import DominoTile, GameState, PlayerPosition, move
from DominoGameState import DominoGameState

def history_to_domino_tiles_history(move_list: list[tuple[int, tuple[tuple[int, int], str]|None]]) -> list[tuple[DominoTile, bool]|None]:
    result: list[tuple[DominoTile, bool]|None] = []
    for _, move_details in move_list:
        if move_details is not None:        
            (tile_tuple, side) = move_details
            domino_tile = DominoTile.new_tile(tile_tuple[0], tile_tuple[1])
            is_left = side == 'l'
            result.append((domino_tile, is_left))
        else:
            result.append(None)
    return result


def setup_game_state(
    initial_hands: list[list[DominoTile]], 
    starting_player: PlayerPosition, 
    first_moves: list[move]
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

def list_possible_moves(state: GameState) -> list[tuple[move, int|None, float|None]]:
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
            possible_moves.append(((tile, True), None, None))
    else:
        # Try playing each tile in the current player's hand
        for tile in current_hand:
            if tile.can_connect(state.left_end):
                possible_moves.append(((tile, True), None, None))

            if tile.can_connect(state.right_end) and state.left_end != state.right_end:
                possible_moves.append(((tile, False), None, None))

    # If the player can't play, include the option to pass
    if not possible_moves:
        # possible_moves.append((None, None, None, None))
        possible_moves.append((None, None, None))

    return possible_moves

def list_possible_moves_from_hand(hand: set[DominoTile], board_ends: tuple[int|None,int|None]) -> list[tuple[move, int | None, float | None]]:
    possible_moves: list[tuple[move, int | None, float | None]] = []
    for tile in hand:
        if board_ends[0] is None and board_ends[1] is None:
            possible_moves.append(((tile, True), None, None))  # Arbitrary choice of left end for first move
        else:
            if board_ends[0] in (tile.top, tile.bottom):
                possible_moves.append(((tile, True), None, None))
            if board_ends[0]!= board_ends[1] and board_ends[1] in (tile.top, tile.bottom):
                possible_moves.append(((tile, False), None, None))
    if not possible_moves:
        possible_moves.append((None, None, None))  # Represent a pass move
    return possible_moves

def get_impossible_tiles(game_state: DominoGameState) -> dict[PlayerPosition, set[DominoTile]]:
    """
    Returns a dictionary mapping each player to the set of tiles they cannot have based on the current game state.
    
    This function identifies impossible tiles for each player based on:
    1. Tiles that have been played
    2. Tiles that could have been played but weren't (when a player passed)
    
    :param game_state: The current state of the game.
    :return: A dictionary where keys are player positions and values are sets of DominoTile instances that the players cannot possess.
    """
    impossible_tiles: dict[PlayerPosition, set[DominoTile]] = {
        pos: set() for pos in range(4)
    }
    
    # 1. Add tiles that have been played
    for player in range(4):
        for tile_tuple in game_state.played_set:
            impossible_tiles[player].add(DominoTile.new_tile(tile_tuple[0], tile_tuple[1]))
    
    # 2. For each pass in history, add tiles that could have been played
    for i, move in enumerate(game_state.history):
        if move[1] is None:  # This was a pass
            player = move[0]
            rollback_steps = len(game_state.history) - i
            prev_state = game_state.rollback(rollback_steps)
            if prev_state.ends != (-1, -1):  # Not the first move
                left, right = prev_state.ends
                # Add all tiles that could connect to either end
                for top in range(7):
                    for bottom in range(top, 7):
                        tile = DominoTile.new_tile(top, bottom)
                        if (left != -1 and (tile.top == left or tile.bottom == left)) or \
                           (right != -1 and left != right and (tile.top == right or tile.bottom == right)):
                            impossible_tiles[player].add(tile)
    
    return impossible_tiles