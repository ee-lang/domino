import unittest
from DominoGame import DominoGame,DominoGameState

class TestDominoGame(unittest.TestCase):
	def test_domino_game(self):
		game = DominoGame(players=[])
		self.assertEqual(len(game.game_state.played_set),0) 
		self.assertFalse(game.is_over())