from dataclasses import dataclass

@dataclass
class DominoGameState:
	played_set: set  # set of played pieces
	ends: tuple[int, int]  # (left_end, right_end). (-1, -1) if empty
	next_player: int  # next player to move. range[0-3]
	player_tile_counts: list[int]  # number of tiles for each player
	history: list[tuple[int, tuple[tuple[int, int], str]|None]]  # list of (player, move)
	variant: str  # "cuban" or "venezuelan" or "international"