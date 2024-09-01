from DominoPlayer import HumanPlayer, available_moves, stats
from collections import defaultdict
from DominoGameState import DominoGameState
# from domino_game_analyzer import DominoTile, PlayerPosition, GameState, get_best_move_alpha_beta, list_possible_moves, PlayerPosition_SOUTH, PlayerPosition_names
# from get_best_move import DominoTile, PlayerPosition, GameState, get_best_move_alpha_beta, list_possible_moves, PlayerPosition_SOUTH, PlayerPosition_names
from get_best_move2 import DominoTile, PlayerPosition, GameState, get_best_move_alpha_beta, list_possible_moves, PlayerPosition_SOUTH, PlayerPosition_names, move
from domino_utils import history_to_domino_tiles_history
from domino_game_tracker import domino_game_state_our_perspective, generate_sample_from_game_state
from domino_common_knowledge import CommonKnowledgeTracker
from statistics import mean, median, stdev, mode
import copy
from tqdm import tqdm
# import get_best_move

class AnalyticAgentPlayer(HumanPlayer):
    def __init__(self, position: int = 0) -> None:
        super().__init__()
        self.move_history: list[tuple[int, tuple[tuple[int, int], str]|None]] = []
        self.tile_count_history: dict[int, list[int]] = defaultdict(list)
        # self.round_scores: list[int] = []
        self.first_game = True
        self.position = position

    def next_move(self, game_state: DominoGameState, player_hand: list[tuple[int,int]], verbose: bool = True) -> tuple[tuple[int,int], str] | None:
        if self.first_game:
            # Check if the move is forced
            if game_state.variant in {'international','venezuelan'} and len(game_state.history)==0:
                self.first_game = False
                print('Playing mandatory (6,6) opening on the first game.')
                return (6,6),'l'
            else:
                self.first_game = False

        unplayed_tiles = self.get_unplayed_tiles(game_state, player_hand)
        _unplayed_tiles = DominoTile.loi_to_domino_tiles(unplayed_tiles)

        _player_hand = DominoTile.loi_to_domino_tiles(player_hand)

        _moves = history_to_domino_tiles_history(game_state.history)
        _remaining_tiles = set(_unplayed_tiles)
        # _initial_player_tiles = {p: 7 for p in PlayerPosition}
        _initial_player_tiles = {p: 7 for p in range(4)}
        # _starting_player = PlayerPosition((game_state.history[0][0] - self.position)%4) if len(game_state.history)>0 else PlayerPosition.SOUTH
        _starting_player = ((game_state.history[0][0] - self.position)%4) if len(game_state.history)>0 else PlayerPosition_SOUTH

        current_player, _final_remaining_tiles, _board_ends, _player_tiles_count, _knowledge_tracker = domino_game_state_our_perspective(
            _remaining_tiles, _moves, _initial_player_tiles, current_player=_starting_player)

        if verbose:
            self.print_verbose_info(_player_hand, _unplayed_tiles, _knowledge_tracker, _player_tiles_count, _starting_player)

        num_samples = 1000 if len(game_state.history) > 8 else 100 if len(game_state.history) > 4 else 25 if len(game_state.history) > 0 else 1
        best_move = self.get_best_move(set(_player_hand), _remaining_tiles, _knowledge_tracker, _player_tiles_count, _board_ends, num_samples, verbose=verbose)

        if best_move is None:
            return None
        else:
            tile, is_left = best_move
            side = 'l' if is_left else 'r'
            return (tile.top, tile.bottom), side

    def print_verbose_info(self, player_hand: list[DominoTile], unplayed_tiles: list[DominoTile], knowledge_tracker: CommonKnowledgeTracker, player_tiles_count: dict[PlayerPosition, int], starting_player: PlayerPosition) -> None:
        print("\n--- Verbose Information ---")
        # print(f"Starting player: {starting_player.name}")
        print(f"Starting player: {PlayerPosition_names[starting_player]}")
        print(f"Player's hand: {player_hand}")
        print(f"Remaining tiles: {unplayed_tiles}")
        print("\nCommon knowledge of missing suits:")
        # for player in PlayerPosition:
        for player in range(4):
            # print(f"  {player.name}: {knowledge_tracker.common_knowledge_missing_suits[player]}")
            print(f"  {PlayerPosition_names[player]}: {knowledge_tracker.common_knowledge_missing_suits[player]}")
        print("\nRemaining tiles for each player:")
        for player, count in player_tiles_count.items():
            # print(f"  {player.name}: {count}")
            print(f"  {PlayerPosition_names[player]}: {count}")
        print("----------------------------\n")

    def get_best_move(self, final_south_hand: set[DominoTile], remaining_tiles: set[DominoTile], 
                      knowledge_tracker: CommonKnowledgeTracker, player_tiles_count: dict[PlayerPosition, int], 
                      board_ends: tuple[int|None,int|None], num_samples: int = 1000, verbose: bool = False) -> tuple[DominoTile, bool] | None:

        inferred_knowledge: dict[PlayerPosition, set[DominoTile]] = {
            # player: set() for player in PlayerPosition
            player: set() for player in range(4)
        }

        for tile in remaining_tiles:
            # for player in PlayerPosition:
            for player in range(4):
                if tile.top in knowledge_tracker.common_knowledge_missing_suits[player] or tile.bottom in knowledge_tracker.common_knowledge_missing_suits[player]:
                    inferred_knowledge[player].add(tile)

        final_remaining_tiles_without_south_tiles = remaining_tiles - final_south_hand 
        # inferred_knowledge_for_current_player = copy.deepcopy(inferred_knowledge)
        inferred_knowledge_for_current_player = inferred_knowledge
        for player, tiles in inferred_knowledge_for_current_player.items():
            inferred_knowledge_for_current_player[player] = tiles - final_south_hand

        move_scores = defaultdict(list)

        for _ in tqdm(range(num_samples), desc="Analyzing moves", leave=False):
            sample = generate_sample_from_game_state(
                # PlayerPosition.SOUTH,
                PlayerPosition_SOUTH,
                final_south_hand,
                final_remaining_tiles_without_south_tiles,
                player_tiles_count,
                inferred_knowledge_for_current_player
            )

            sample_hands = (
                frozenset(final_south_hand),
                frozenset(sample['E']),
                frozenset(sample['N']),
                frozenset(sample['W'])
            )

            sample_state = GameState(
                player_hands=sample_hands,
                # current_player=PlayerPosition.SOUTH,
                current_player=PlayerPosition_SOUTH,
                left_end=board_ends[0],
                right_end=board_ends[1],
                consecutive_passes=0
            )

            depth = 24

            # possible_moves = list_possible_moves(sample_state, include_stats=False)
            possible_moves = list_possible_moves(sample_state)

            sample_cache: dict[GameState, tuple[int, int]] = {}
            for move in possible_moves:
                if move[0] is None:
                    new_state = sample_state.pass_turn()
                else:
                    tile, is_left = move[0]
                    new_state = sample_state.play_hand(tile, is_left)

                # _, best_score, _ = get_best_move_alpha_beta(new_state, depth, sample_cache, best_path_flag=False)
                _, best_score, _ = get_best_move_alpha_beta(new_state, depth, sample_cache, best_path_flag=False)

                move_scores[move[0]].append(best_score)

        if not move_scores:
            if verbose:
                print("No legal moves available. Player must pass.")
            return None

        if verbose:
            self.print_move_statistics(move_scores, num_samples)

        best_move = max(move_scores, key=lambda x: mean(move_scores[x]))
        return best_move

    def print_move_statistics(self, move_scores: dict[move, list[float]], num_samples: int) -> None:
        print(f"\nMove Statistics (based on {num_samples} samples):")

        # Calculate statistics for each move
        move_statistics = {}
        for move, scores in move_scores.items():
            if len(scores) > 1:
                move_statistics[move] = {
                    "count": len(scores),
                    "mean": mean(scores),
                    "std_dev": stdev(scores),
                    "median": median(scores),
                    "mode": mode(scores),
                    "min": min(scores),
                    "max": max(scores)
                }
            else:
                move_statistics[move] = {
                    "count": len(scores),
                    # "mean": scores[0] if scores else None,
                    # "std_dev": 0,
                    # "median": scores[0] if scores else None,
                    # "mode": scores[0] if scores else None,
                    # "min": scores[0] if scores else None,
                    # "max": scores[0] if scores else None
                    "mean": scores[0],
                    "std_dev": 0,
                    "median": scores[0],
                    "mode": scores[0],
                    "min": scores[0],
                    "max": scores[0]
                }

        # Sort moves by their mean score, descending order
        sorted_moves = sorted(move_statistics.items(), key=lambda x: x[1]["mean"], reverse=True)

        # Print statistics for each move
        for move, stats in sorted_moves:
            if move is None:
                move_str = "Pass"
            else:
                tile, is_left = move
                direction = "left" if is_left else "right"
                move_str = f"Play {tile} on the {direction}"

            print(f"\nMove: {move_str}")
            print(f"  Count: {stats['count']}")
            print(f"  Mean Score: {stats['mean']:.4f}")
            print(f"  Standard Deviation: {stats['std_dev']:.4f}")
            print(f"  Median Score: {stats['median']:.4f}")
            print(f"  Mode Score: {stats['mode']:.4f}")
            print(f"  Min Score: {stats['min']:.4f}")
            print(f"  Max Score: {stats['max']:.4f}")

        # Identify the best move based on the highest mean score
        best_move = max(move_statistics, key=lambda x: move_statistics[x]["mean"])
        best_stats = move_statistics[best_move]

        print("\nBest Move Overall:")
        if best_move is None:
            print(f"Best move: Pass")
        else:
            tile, is_left = best_move
            direction = "left" if is_left else "right"
            print(f"Best move: Play {tile} on the {direction}")
        print(f"Mean Expected Score: {best_stats['mean']:.4f}")

    def end_round(self, scores: list[int], team: int) -> None:
        super().end_round(scores, team)
        # self.record_round_score(scores)

    def record_move(self, game_state: DominoGameState, move: tuple[tuple[int, int], str]|None) -> None:
        self.move_history.append((game_state.next_player, move))
        for i, count in enumerate(game_state.player_tile_counts):
            self.tile_count_history[i].append(count)

    # def record_round_score(self, scores: list[int]) -> None:
    #     self.round_scores.append(scores)

    def get_move_history(self) -> list[tuple[int, tuple[tuple[int, int], str]|None]]:
        return self.move_history

    def get_tile_count_history(self) -> dict[int, list[int]]:
        return dict(self.tile_count_history)

    # def get_round_scores(self) -> list[int]:
    #     return self.round_scores