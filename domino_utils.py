# from domino_game_analyzer import DominoTile
from domino_data_types import DominoTile, GameState, PlayerPosition, move

def history_to_domino_tiles_history(move_list: list[tuple[int, tuple[tuple[int, int], str]|None]]) -> list[tuple[DominoTile, bool]|None]:
    result: list[tuple[DominoTile, bool]|None] = []
    for _, move_details in move_list:
        if move_details is not None:        
            (tile_tuple, side) = move_details
            domino_tile = DominoTile.new_tile(tile_tuple[0], tile_tuple[1])
            is_left = side == 'l'
        result.append((domino_tile, is_left) if move_details is not None else None)
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