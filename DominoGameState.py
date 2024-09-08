from dataclasses import dataclass

@dataclass
class DominoGameState:
	played_set: set[tuple[int, int]]  # set of played pieces
	ends: tuple[int, int]  # (left_end, right_end). (-1, -1) if empty
	next_player: int  # next player to move. range[0-3]
	player_tile_counts: list[int]  # number of tiles for each player
	history: list[tuple[int, tuple[tuple[int, int], str]|None]]  # list of (player, move)
	variant: str  # "cuban" or "venezuelan" or "international"
	first_round: bool = False

	def rollback(self, step: int) -> 'DominoGameState':
		if step <= 0 or step > len(self.history):
			return self

		new_history = self.history[:-step]
		new_played_set = set()
		new_ends = (-1, -1)
		new_player_tile_counts = [7, 7, 7, 7]  # Assuming initial tile count is 7 for each player

		for player, move in new_history:
			if move is not None:
				tile, side = move
				new_played_set.add(tile)
				new_player_tile_counts[player] -= 1
				
				if new_ends == (-1, -1):  # First move
					new_ends = tile
				elif side == 'l':
					new_ends = (tile[1] if tile[0] == new_ends[0] else tile[0], new_ends[1])
				else:  # side == 'r'
					new_ends = (new_ends[0], tile[1] if tile[0] == new_ends[1] else tile[0])

		new_next_player = (new_history[-1][0] + 1) % 4 if new_history else 0

		return DominoGameState(
			played_set=new_played_set,
			ends=new_ends,
			next_player=new_next_player,
			player_tile_counts=new_player_tile_counts,
			history=new_history,
			variant=self.variant,
			first_round=self.first_round
		)
