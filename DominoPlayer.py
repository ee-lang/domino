from DominoGameState import DominoGameState
# from typing import List, Tuple, Optional
from collections import Counter, defaultdict


class DominoPlayer:
	def next_move(self, game_state: DominoGameState, player_hand: list[tuple[int, int]]) -> tuple[tuple[int, int], str]|None:
		raise NotImplementedError('Not implemented.')

	def end_round(self, scores: list[int], team: int) -> None:
		"""
		Called at the end of each round with the scores and team information.

		Args:
		scores (List[int]): A list containing two integers [Team 1 score, Team 2 score].
		team (int): The team number (0 or 1) that this player belongs to.

		The base implementation does nothing.
		"""
		pass

class HumanPlayer(DominoPlayer):
	def __init__(self) -> None:
		self.missing_tiles: dict[int, set[int]] = defaultdict(set)

	def next_move(self, game_state: DominoGameState, player_hand: list[tuple[int, int]]) -> tuple[tuple[int, int], str]|None:
		self.update_missing_tiles(game_state)
		
		while True:
			try:
				lom = available_moves(game_state, player_hand)
				print('HumanPlayer.played_tiles', game_state.played_set)
				
				unplayed_tiles = self.get_unplayed_tiles(game_state, player_hand)
				print(f'HumanPlayer.unplayed_tiles ({len(unplayed_tiles)} remaining):', unplayed_tiles)
				
				remaining_suits = self.count_remaining_pips(unplayed_tiles)
				print('HumanPlayer.remaining_tiles_per_suit:', remaining_suits)
				
				self.display_possible_tiles_for_players(game_state, unplayed_tiles)
				
				print('HumanPlayer.hand:', player_hand)

				max_pips = 9 if game_state.variant == "cuban" else 6
				hand_stats = stats(player_hand, max_pips)
				sorted_hands_freq = sorted([(k, v) for k, v in hand_stats.items()], key=lambda x: x[1], reverse=True)
				print('HumanPlayer.hand_stats:', [f'{k}: {v}' for k,v in sorted_hands_freq])				

				# Display the number of tiles each player has
				print('Number of tiles per player:', game_state.player_tile_counts)
				
				# Display available moves with 'l' and/or 'r' options
				print('HumanPlayer.available moves:')
				for move in lom:
					sides = []
					if game_state.ends[0] in move:
						sides.append('l')
					if game_state.ends[1] in move:
						sides.append('r')
					if not sides:  # This is for the first move of the game
						sides = ['l', 'r']
					print(f"{move}: {', '.join(sides)}")

				move_str = input('format: "d,d,r|l". your move:')
				if move_str.strip().lower() in ['', 'none']:
					return None
				d0, d1, s = move_str.strip().split(',')
				return (int(d0), int(d1)), s
			except Exception as e:
				print('illegal input', e)

	def end_round(self, scores: list[int], team: int) -> None:
		self.missing_tiles = defaultdict(set)
		print(f"HumanPlayer: Round ended. Scores - Team 1: {scores[0]}, Team 2: {scores[1]}")
		print(f"HumanPlayer: Your team (Team {team + 1}) score: {scores[team]}")
		print("HumanPlayer: Reset missing tiles for the next round.")

	def get_unplayed_tiles(self, game_state: DominoGameState, player_hand: list[tuple[int, int]]) -> list[tuple[int,int]]:
		max_pip = 9 if game_state.variant == "cuban" else 6
		all_tiles = set((i, j) for i in range(max_pip + 1) for j in range(i, max_pip + 1))
		played_tiles = game_state.played_set
		return sorted(list(all_tiles - set(player_hand) - played_tiles))

	def count_remaining_pips(self, unplayed_tiles: list[tuple[int, int]]) -> dict[int, int]:
		pip_counts: dict[int,int] = Counter()
		for tile in unplayed_tiles:
			pip_counts[tile[0]] += 1
			if tile[0] != tile[1]:
				pip_counts[tile[1]] += 1
		return dict(sorted(pip_counts.items()))

	def update_missing_tiles(self, game_state: DominoGameState) -> None:
		moves_to_check = min(len(game_state.history), 4)
		last_moves = game_state.history[-moves_to_check:]

		if not last_moves:
			return  # No moves to process

		# Reconstruct the game state before the last moves
		if moves_to_check < len(game_state.history):
			ends = self.get_ends_before_last_moves(game_state.history[:-moves_to_check])
		else:
			ends = (-1, -1)

		for move_index, (player, move) in enumerate(last_moves):
			current_player = (game_state.next_player - (moves_to_check - move_index)) % 4
			
			if move is None:  # The player passed
				if ends != (-1, -1):  # Only update if the game has started
					print('HumanPlayer.update_missing_tiles', player, ends[0], ends[1])
					self.missing_tiles[current_player].add(ends[0])
					self.missing_tiles[current_player].add(ends[1])
			else:  # A tile was played
				tile, side = move
				if ends == (-1, -1):  # First move of the game
					ends = tile
				elif side == 'l':
					ends = (tile[1] if tile[0] == ends[0] else tile[0], ends[1])
				else:  # side == 'r'
					ends = (ends[0], tile[1] if tile[0] == ends[1] else tile[0])

	def get_ends_before_last_moves(self, history: list[tuple[int, tuple[tuple[int, int], str]|None]]) -> tuple[int, int]:
		ends = (-1, -1)
		for _, move in history:
			if move is not None:
				tile, side = move
				if ends == (-1, -1):  # First move of the game
					ends = tile
				elif side == 'l':
					ends = (tile[1] if tile[0] == ends[0] else tile[0], ends[1])
				else:  # side == 'r'
					ends = (ends[0], tile[1] if tile[0] == ends[1] else tile[0])
		return ends

	def display_possible_tiles_for_players(self, game_state: DominoGameState, unplayed_tiles: list[tuple[int, int]]) -> None:
		for player in range(4):
			if player != game_state.next_player:
				possible_tiles = [tile for tile in unplayed_tiles 
								  if tile[0] not in self.missing_tiles[player] 
								  and tile[1] not in self.missing_tiles[player]]
				if len(possible_tiles) < len(unplayed_tiles):
					print(f'HumanPlayer.possible_tiles_for_player_{player}: {possible_tiles}')

import random
class RandomPlayer(DominoPlayer):
	def next_move(self, game_state: DominoGameState, player_hand: list[tuple[int, int]]) -> tuple[tuple[int, int], str]|None:
		lom = available_moves(game_state, player_hand)
		if len(lom) == 0: return None
		tiles = random.choice(lom)
		sides = []
		if game_state.ends[0] in tiles:
			sides += ['l']
		if game_state.ends[1] in tiles:
			sides += ['r']
		side = random.choice(sides) if len(game_state.played_set) > 0 else 'l'
		return tiles, side

def available_moves(game_state: DominoGameState, player_hand: list[tuple[int, int]]) -> list[tuple[int, int]]:
	l_end, r_end = game_state.ends
	if l_end == -1 and r_end == -1:
		return player_hand
	return list(filter(lambda h: r_end in h or l_end in h, player_hand))

def stats(player_hand: list[tuple[int, int]], max_pips: int) -> dict[int, int]:
	counter: dict[int, int] = defaultdict(int)
	for tile in player_hand:
		counter[tile[0]] += 1
		if tile[0] != tile[1]:
			counter[tile[1]] += 1
	return {i: counter[i] for i in range(max_pips + 1)}  # Ensures all figures from 0 to max_pips are included