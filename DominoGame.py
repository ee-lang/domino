from typing import List, Tuple, Optional
import argparse
import random
from DominoGameState import DominoGameState

class DominoGame:
	def __init__(self, players, variant="cuban"):
		self.variant = variant
		self.max_pip, self.hand_size = self.get_variant_params()
		self.players = players
		self.scores = [0, 0]  # Team scores
		self.current_round = 0
		self.player_hands = []
		self.starting_player = 0
		print(f"Starting a new {self.variant.capitalize()} Domino game!")

	def get_variant_params(self):
		"""
		Determines the maximum pip value and initial hand size based on the game variant.

		Returns:
		tuple: A pair of integers (max_pip, hand_size) where:
			- max_pip (int): The maximum pip value on a domino tile for the current variant.
			- hand_size (int): The number of tiles each player starts with.

		Raises:
		ValueError: If an unsupported domino variant is specified.

		Note:
		- For the Cuban variant: max_pip is 9, hand_size is 10.
		- For the Venezuelan variant: max_pip is 6, hand_size is 7.
		- For the International variant: max_pip is 6, hand_size is 7.
		"""
		if self.variant == "cuban":
			return 9, 10
		elif self.variant in ["venezuelan", "international"]:
			return 6, 7
		else:
			raise ValueError("Unsupported domino variant")

	def determine_first_player(self)-> int:
		if self.variant == "cuban":
			return random.randint(0, 3)
		elif self.variant in ["venezuelan", "international"]:
			for i, hand in enumerate(self.player_hands):
				if (6, 6) in hand:
					return i
			raise ValueError("No player has the double-6 tile. This should not happen in Venezuelan variant.")
		else:
			raise ValueError("Unsupported domino variant")

	# def play_game(self):
	# 	print(f"Game starts with {self.variant.capitalize()} rules.")
	# 	while max(self.scores) < 100:
	# 		round_winner, round_score = self.play_round()
	# 		print(f"\nRound {self.current_round} ended.")
	# 		print(f"Round winner: {'Team 1' if round_winner % 2 == 0 else 'Team 2'} (Player {round_winner})")
	# 		print(f"Round score: {round_score}")
	# 		print(f"Total scores: Team 1 - {self.scores[0]}, Team 2 - {self.scores[1]}")
			
	# 		self.current_round += 1
	# 		self.starting_player = self.determine_next_starting_player(round_winner)
	# 		print(f"Next starting player: Player {self.starting_player}")
		
	# 	winning_team = 0 if self.scores[0] >= 100 else 1
	# 	print(f"\nGame over! Team {winning_team + 1} wins with a score of {self.scores[winning_team]}!")
		
	# 	winning_team = 0 if self.scores[0] >= 100 else 1
	# 	print(f"\nGame over! Team {winning_team + 1} wins with a score of {self.scores[winning_team]}!")

	def play_game(self):
		print(f"Game starts with {self.variant.capitalize()} rules.")
		while max(self.scores) < (100 if self.variant!='international' else 150):
			round_winner, round_score = self.play_round()
			print(f"\nRound {self.current_round} ended.")
			print(f"Round winner: {'Team 1' if round_winner % 2 == 0 else 'Team 2'} (Player {round_winner})")
			print(f"Round score: {round_score}")
			print(f"Total scores: Team 1 - {self.scores[0]}, Team 2 - {self.scores[1]}")

			self.current_round += 1
			self.starting_player = self.determine_next_starting_player(round_winner)
			print(f"Next starting player: Player {self.starting_player}")

		winning_team = 0 if self.scores[0] >= (100 if self.variant!='international' else 150) else 1
		print(f"\nGame over! Team {winning_team + 1} wins with a score of {self.scores[winning_team]}!")


	def play_round(self):
		print(f"\nStarting Round {self.current_round + 1}")
		self.initialize_round()
		print(f"All players have been dealt {self.hand_size} tiles.")
		print(f"Starting player: Player {self.starting_player}")
		
		if self.variant in ["venezuelan", "international"] and self.current_round == 0:
			print("The first player must start with the double 6.")
		
		while not self.is_round_over():
			player_index = self.game_state.next_player
			print(f"\nPlayer {player_index}'s turn")
			print(f"Current board: {self.game_state.ends}")
			move = self.players[player_index].next_move(self.game_state, self.player_hands[player_index])
			
			if self.is_legal_move(self.game_state, self.player_hands[player_index], move):
				self.apply_move(move)
				if move is None:
					print(f"Player {player_index} passes")
				else:
					print(f"Player {player_index} plays {move}")
			else:
				print(f"Illegal move by player {player_index}: {move}")
				if self.variant in ["venezuelan", "international"] and self.current_round == 0 and len(self.game_state.history) == 0:
					print("The first move must be the double 6.")
				continue  # Skip to the next iteration, keeping the same player's turn
		
		print("\nRound over. Final hands:")
		for i, hand in enumerate(self.player_hands):
			print(f"Player {i}: {hand}")
		
		round_winner, round_score = self.calculate_round_score()
		
		# Update scores
		self.scores[round_winner % 2] += round_score
		
		# Call end_round for each player
		for i, player in enumerate(self.players):
			player.end_round(self.scores, i % 2)
		
		return round_winner, round_score

	def initialize_round(self):
		all_pieces = self.generate_all_pieces()
		self.player_hands = [[] for _ in range(4)]
		for i in range(4):
			self.player_hands[i], all_pieces = self.draw_hand(all_pieces)
		
		if self.current_round == 0:
			self.starting_player = self.determine_first_player()
		
		self.game_state = DominoGameState(
			set(),
			(-1, -1),
			self.starting_player,
			[len(hand) for hand in self.player_hands],
			[],
			self.variant
		)

	def generate_all_pieces(self):
		return [(i, j) for i in range(self.max_pip + 1) for j in range(i, self.max_pip + 1)]

	def draw_hand(self, pieces):
		hand = random.sample(pieces, self.hand_size)
		remaining_pieces = [p for p in pieces if p not in hand]
		return hand, remaining_pieces

	def is_round_over(self):
		if any(count == 0 for count in self.game_state.player_tile_counts):
			return True
		if len(self.game_state.history) >= 4 and all(move is None for _, move in self.game_state.history[-4:]):
			return True
		return False

	def is_legal_move(self, game_state, player_hand, move):
		if self.variant in ["venezuelan", "international"] and self.current_round == 0 and len(game_state.history) == 0:
			return self.is_legal_first_move_venezuelan(move)
		
		if move is None:
			return not any(self.can_play(piece) for piece in player_hand)
		piece, side = move
		if piece not in player_hand:
			return False
		if game_state.ends == (-1, -1):
			return True
		return self.can_play(piece)


	def is_legal_first_move_venezuelan(self, move):
		if move is None:
			return False
		piece, side = move
		return piece == (6, 6) and side in ['l', 'r']

	def can_play(self, piece):
		return self.game_state.ends[0] in piece or self.game_state.ends[1] in piece

	def apply_move(self, move):
		player = self.game_state.next_player
		new_tile_counts = self.game_state.player_tile_counts.copy()
		
		if move is not None:
			piece, side = move
			self.player_hands[player].remove(piece)
			new_tile_counts[player] -= 1
			
			new_played_set = self.game_state.played_set.copy()
			new_played_set.add(piece)
			
			if self.game_state.ends == (-1, -1):
				new_ends = piece
				print(f"First move: {piece}")
			elif side == 'l':
				new_ends = (piece[1] if piece[0] == self.game_state.ends[0] else piece[0], self.game_state.ends[1])
				print(f"Played {piece} on the left side")
			else:  # side == 'r'
				new_ends = (self.game_state.ends[0], piece[1] if piece[0] == self.game_state.ends[1] else piece[0])
				print(f"Played {piece} on the right side")
		else:
			new_played_set = self.game_state.played_set
			new_ends = self.game_state.ends
			print("Player passed")
		
		self.game_state = DominoGameState(
			new_played_set,
			new_ends,
			(player + 1) % 4,
			new_tile_counts,
			self.game_state.history + [(player, move)],
			self.variant
		)
		print(f"New board state: {new_ends}")
		print(f"Tiles remaining per player: {new_tile_counts}")

	# def calculate_round_score(self):
	# 	p_tiles = [sum(sum(piece) for piece in hand) for hand in self.player_hands]
	# 	print(f"Remaining tiles values: {p_tiles}")
		
	# 	winner = next((i for i in range(4) if len(self.player_hands[i]) == 0), -1)
		
	# 	if winner != -1:
	# 		# A player won by playing all their tiles
	# 		winning_team = winner % 2
	# 		points = sum(p_tiles[1-winning_team::2])
	# 		print(f"Player {winner} won by playing all tiles")
	# 		return winning_team, points
	# 	else:
	# 		# The game got blocked
	# 		print("The round ended in a block")
	# 		if self.variant == "cuban":
	# 			return self.calculate_cuban_blocked_score(p_tiles)
	# 		elif self.variant == "venezuelan":
	# 			return self.calculate_venezuelan_blocked_score(p_tiles)

	def calculate_round_score(self):
		p_tiles = [sum(sum(piece) for piece in hand) for hand in self.player_hands]
		print(f"Remaining tiles values: {p_tiles}")

		winner = next((i for i in range(4) if len(self.player_hands[i]) == 0), -1)

		if winner != -1:
			# A player won by playing all their tiles
			winning_team = winner % 2
			if self.variant == "international":
				# In International variant, sum all the pips that were out
				points = sum(p_tiles)
			else:
				# For other variants, sum the opponent's pips
				points = sum(p_tiles[1-winning_team::2])
			print(f"Player {winner} won by playing all tiles")
			return winning_team, points
		else:
			# The game got blocked
			print("The round ended in a block")
			if self.variant == "cuban":
				return self.calculate_cuban_blocked_score(p_tiles)
			elif self.variant == "venezuelan":
				return self.calculate_venezuelan_blocked_score(p_tiles)
			elif self.variant == "international":
				return self.calculate_international_blocked_score(p_tiles)



	def calculate_cuban_blocked_score(self, p_tiles):
		p02_tiles = min(p_tiles[0], p_tiles[2])
		p13_tiles = min(p_tiles[1], p_tiles[3])
		print(f"Cuban scoring - Team 1 lowest: {p02_tiles}, Team 2 lowest: {p13_tiles}")
		if p02_tiles == p13_tiles:
			print("The round is tied")
			return -1, 0  # Tie
		winner = 0 if p02_tiles < p13_tiles else 1
		points = sum(p_tiles[1-winner::2])
		print(f"Winner: Team {winner + 1}, Points: {points}")
		return winner, points

	def calculate_venezuelan_blocked_score(self, p_tiles):
		p02_tiles = p_tiles[0] + p_tiles[2]
		p13_tiles = p_tiles[1] + p_tiles[3]
		print(f"Venezuelan scoring - Team 1 total: {p02_tiles}, Team 2 total: {p13_tiles}")
		if p02_tiles == p13_tiles:
			print("The round is tied")
			return -1, 0  # Tie
		winner = 0 if p02_tiles < p13_tiles else 1
		points = sum(p_tiles[1-winner::2])
		print(f"Winner: Team {winner + 1}, Points: {points}")
		return winner, points

	def calculate_international_blocked_score(self, p_tiles):
		p02_tiles = p_tiles[0] + p_tiles[2]
		p13_tiles = p_tiles[1] + p_tiles[3]
		print(f"International scoring - Team 1 total: {p02_tiles}, Team 2 total: {p13_tiles}")
		if p02_tiles == p13_tiles:
			print("The round is tied")
			return -1, 0  # Tie
		winner = 0 if p02_tiles < p13_tiles else 1
		points = sum(p_tiles)
		print(f"Winner: Team {winner + 1}, Points: {points}")
		return winner, points


	def determine_next_starting_player(self, round_winner):
		if self.variant == "cuban":
			if round_winner == -1:  # Tie
				print("Round tied, same player starts next round")
				return self.starting_player
			next_starter = random.choice([round_winner, (round_winner + 2) % 4])
			print(f"Cuban rules: Randomly chose Player {next_starter} from winning team to start next round")
			return next_starter
		elif self.variant in ["venezuelan", "international"]:
			next_starter = (self.starting_player + 1) % 4
			print(f"Venezuelan/International rules: Player {next_starter} starts next round")
			return next_starter

# def main():
# 	from DominoPlayer import HumanPlayer, RandomPlayer
	
# 	parser = argparse.ArgumentParser(description="Play a game of Dominoes")
# 	parser.add_argument("variant", choices=["cuban", "venezuelan"], help="Choose the domino variant to play")
# 	args = parser.parse_args()

# 	players = [HumanPlayer(), RandomPlayer(), RandomPlayer(), RandomPlayer()]
# 	game = DominoGame(players, variant=args.variant)
# 	game.play_game()

# if __name__ == "__main__":
# 	main()

def main():
	from DominoPlayer import HumanPlayer, RandomPlayer
	from HumanPlayerWithAnalytics import HumanPlayerWithAnalytics
	from analytic_agent_player import AnalyticAgentPlayer

	parser = argparse.ArgumentParser(description="Play a game of Dominoes")
	parser.add_argument("variant", choices=["cuban", "venezuelan", "international"], help="Choose the domino variant to play")
	args = parser.parse_args()

	# players = [HumanPlayer(), RandomPlayer(), RandomPlayer(), RandomPlayer()]
	# players = [HumanPlayerWithAnalytics(), RandomPlayer(), RandomPlayer(), RandomPlayer()]
	players = [AnalyticAgentPlayer(), RandomPlayer(), RandomPlayer(), RandomPlayer()]
	game = DominoGame(players, variant=args.variant)
	game.play_game()

if __name__ == "__main__":
	main()
