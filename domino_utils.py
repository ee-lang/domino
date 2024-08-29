from domino_game_analyzer import DominoTile

def history_to_domino_tiles_history(move_list: list[tuple[int, tuple[tuple[int, int], str]|None]]) -> list[tuple[DominoTile, bool]|None]:
    result: list[tuple[DominoTile, bool]|None] = []
    for _, move_details in move_list:
        if move_details is not None:        
            (tile_tuple, side) = move_details
            domino_tile = DominoTile.new_tile(tile_tuple[0], tile_tuple[1])
            is_left = side == 'l'
        result.append((domino_tile, is_left) if move_details is not None else None)
    return result