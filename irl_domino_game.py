import argparse
# from typing import List, Tuple, Optional
from DominoGameState import DominoGameState
from analytic_agent_player_parallel_ci import AnalyticAgentPlayer

class IRLDominoGame:
    def __init__(self, variant: str = "international") -> None:
        self.variant = variant
        self.max_pip, self.hand_size = self.get_variant_params()
        self.player_hands: list[list[tuple[int, int]]] = [[] for _ in range(4)]
        self.game_state: DominoGameState|None = None
        self.agent = AnalyticAgentPlayer(position=0)  # Assuming the agent is always Player 0 (South)

    def get_variant_params(self) -> tuple[int, int]:
        if self.variant == "cuban":
            return 9, 10
        elif self.variant in ["venezuelan", "international"]:
            return 6, 7
        else:
            raise ValueError("Unsupported domino variant")

    def initialize_round(self) -> None:
        print(f"\nStarting a new {self.variant.capitalize()} Domino round!")
        starting_player = int(input("Enter the starting player (0-3): "))
        
        # Input the agent's hand (Player 0)
        print("Enter your hand (comma-separated, e.g., '1-2,3-4,5-6'): ")
        hand_input = input().split(',')
        self.player_hands[0] = [tuple(sorted(map(int, tile.split('-')))) for tile in hand_input]
        
        # Initialize game state
        self.game_state = DominoGameState(
            set(),
            (-1, -1),
            starting_player,
            [self.hand_size] * 4,  # Assume all players start with full hands
            [],
            self.variant,
            False
        )
        self.game_state.player_tile_counts[0] = len(self.player_hands[0])
        
        print(f"Round initialized. Starting player: {starting_player}")
        print(f"Your hand: {self.player_hands[0]}")

    def play_round(self) -> None:
        assert self.game_state is not None
        while not self.is_round_over():
            current_player = self.game_state.next_player
            print(f"\nCurrent player: {current_player}")
            print(f"Current board: {self.game_state.ends}")
            
            if current_player == 0:  # Agent's turn
                recommended_move = self.agent.next_move(self.game_state, self.player_hands[0])
                print(f"Recommended move: {recommended_move}")
                move_input = input("Enter the move (e.g., '1-2,l' for left, '3-4,r' for right, or 'pass'): ")
            else:
                move_input = input(f"Enter Player {current_player}'s move: ")
            
            move = self.parse_move_input(move_input)
            self.apply_move(current_player, move)

        print("\nRound over.")
        self.calculate_round_score()

    def parse_move_input(self, move_input: str) -> tuple[tuple[int, int], str]|None:
        if move_input.lower() == 'pass':
            return None
        try:
            tile, side = move_input.split(',')
            values = list(map(int, tile.split('-')))
            piece = (min(values), max(values))
            return (piece, side.strip().lower())
        except ValueError:
            print("Invalid move format. Please try again.")
            return self.parse_move_input(input("Enter the move again: "))

    def apply_move(self, player: int, move: tuple[tuple[int, int], str]|None) -> None:
        assert self.game_state is not None
        new_tile_counts = self.game_state.player_tile_counts.copy()
        
        if move is not None:
            piece, side = move
            new_tile_counts[player] -= 1
            
            new_played_set = self.game_state.played_set.copy()
            new_played_set.add(piece)
            
            if self.game_state.ends == (-1, -1):
                new_ends = piece
            elif side == 'l':
                new_ends = (piece[1] if piece[0] == self.game_state.ends[0] else piece[0], self.game_state.ends[1])
            else:  # side == 'r'
                new_ends = (self.game_state.ends[0], piece[1] if piece[0] == self.game_state.ends[1] else piece[0])
        else:
            new_played_set = self.game_state.played_set
            new_ends = self.game_state.ends
        
        self.game_state = DominoGameState(
            new_played_set,
            new_ends,
            (player + 1) % 4,
            new_tile_counts,
            self.game_state.history + [(player, move)],
            self.variant
        )
        
        if player == 0 and move is not None:
            self.player_hands[0].remove(move[0])
        print(f"Player {player} played {move}")
        print(f"Player {player} hand: {self.player_hands[player]}")
        
        print(f"Move applied. New board state: {new_ends}")
        print(f"Tiles remaining per player: {new_tile_counts}")

    def is_round_over(self) -> bool:
        assert self.game_state is not None
        if any(count == 0 for count in self.game_state.player_tile_counts):
            return True
        if len(self.game_state.history) >= 4 and all(move is None for _, move in self.game_state.history[-4:]):
            return True
        return False

    def calculate_round_score(self) -> None:
        assert self.game_state is not None
        print("Enter the remaining tile values for each player:")
        p_tiles = [int(input(f"Player {i}: ")) for i in range(4)]
        print(f"Remaining tiles values: {p_tiles}")

        winner = next((i for i, count in enumerate(self.game_state.player_tile_counts) if count == 0), -1)

        if winner != -1:
            winning_team = winner % 2
            if self.variant == "international":
                points = sum(p_tiles)
            else:
                points = sum(p_tiles[1-winning_team::2])
            print(f"Player {winner} won by playing all tiles")
        else:
            print("The round ended in a block")
            if self.variant == "cuban":
                winning_team, points = self.calculate_cuban_blocked_score(p_tiles)
            elif self.variant == "venezuelan":
                winning_team, points = self.calculate_venezuelan_blocked_score(p_tiles)
            elif self.variant == "international":
                winning_team, points = self.calculate_international_blocked_score(p_tiles)

        if winning_team != -1:
            print(f"Team {winning_team + 1} wins {points} points")
        else:
            print("The round is tied")

    def calculate_cuban_blocked_score(self, p_tiles: list[int]) -> tuple[int, int]:
        p02_tiles = min(p_tiles[0], p_tiles[2])
        p13_tiles = min(p_tiles[1], p_tiles[3])
        if p02_tiles == p13_tiles:
            return -1, 0  # Tie
        winner = 0 if p02_tiles < p13_tiles else 1
        points = sum(p_tiles[1-winner::2])
        return winner, points

    def calculate_venezuelan_blocked_score(self, p_tiles: list[int]) -> tuple[int, int]:
        p02_tiles = p_tiles[0] + p_tiles[2]
        p13_tiles = p_tiles[1] + p_tiles[3]
        if p02_tiles == p13_tiles:
            return -1, 0  # Tie
        winner = 0 if p02_tiles < p13_tiles else 1
        points = sum(p_tiles[1-winner::2])
        return winner, points

    def calculate_international_blocked_score(self, p_tiles: list[int]) -> tuple[int, int]:
        p02_tiles = p_tiles[0] + p_tiles[2]
        p13_tiles = p_tiles[1] + p_tiles[3]
        if p02_tiles == p13_tiles:
            return -1, 0  # Tie
        winner = 0 if p02_tiles < p13_tiles else 1
        points = sum(p_tiles)
        return winner, points

def main() -> None:
    parser = argparse.ArgumentParser(description="Play a round of Dominoes")
    parser.add_argument("variant", choices=["cuban", "venezuelan", "international"], help="Choose the domino variant to play")
    args = parser.parse_args()

    game = IRLDominoGame(variant=args.variant)
    game.initialize_round()
    game.play_round()

if __name__ == "__main__":
    main()