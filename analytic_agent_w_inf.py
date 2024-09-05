from DominoPlayer import HumanPlayer, available_moves, stats
from collections import defaultdict
from DominoGameState import DominoGameState
from domino_data_types import DominoTile, PlayerPosition, GameState, PlayerPosition_SOUTH, PlayerPosition_names, move
from get_best_move2 import get_best_move_alpha_beta
from domino_utils import history_to_domino_tiles_history, list_possible_moves, list_possible_moves_from_hand
from domino_game_tracker import domino_game_state_our_perspective, generate_sample_from_game_state
from domino_common_knowledge import CommonKnowledgeTracker
from statistics import mean, median, stdev, mode
import time, copy
from tqdm import tqdm
from concurrent.futures import ProcessPoolExecutor, as_completed
from scipy import stats as scipy_stats

class AnalyticAgentPlayer(HumanPlayer):
    def __init__(self, position: int = 0) -> None:
        super().__init__()
        self.move_history: list[tuple[int, tuple[tuple[int, int], str]|None]] = []
        self.tile_count_history: dict[int, list[int]] = defaultdict(list)
        # self.round_scores: list[int] = []
        self.first_game = True
        self.position = position

    def next_move(self, game_state: DominoGameState, player_hand: list[tuple[int,int]], verbose: bool = True) -> tuple[tuple[int,int], str] | None:
        # if self.first_game:
        if game_state.first_round:
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

        # num_samples = 1000 if len(game_state.history) > 8 else 100 if len(game_state.history) > 4 else 25 if len(game_state.history) > 0 else 1000
        num_samples = 24

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

    # def list_possible_moves_from_hand(self, hand: set[DominoTile], board_ends: tuple[int|None,int|None]) -> list[tuple[move, int | None, float | None]]:
    #     possible_moves: list[tuple[move, int | None, float | None]] = []
    #     for tile in hand:
    #         if board_ends[0] is None and board_ends[1] is None:
    #             possible_moves.append(((tile, True), None, None))  # Arbitrary choice of left end for first move
    #         else:
    #             if board_ends[0] in (tile.top, tile.bottom):
    #                 possible_moves.append(((tile, True), None, None))
    #             if board_ends[1] in (tile.top, tile.bottom):
    #                 possible_moves.append(((tile, False), None, None))
    #     if not possible_moves:
    #         possible_moves.append((None, None, None))  # Represent a pass move
    #     return possible_moves

    def sample_and_search(self, final_south_hand: set[DominoTile], final_remaining_tiles_without_south_tiles: set[DominoTile], player_tiles_count: dict[PlayerPosition, int], inferred_knowledge_for_current_player: dict[PlayerPosition, set[DominoTile]], board_ends: tuple[int|None,int|None], possible_moves: list[tuple[tuple[DominoTile, bool] | None, int | None, float | None]]|None = None) -> list[tuple[move, float]]:
        sample = generate_sample_from_game_state(
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
            current_player=PlayerPosition_SOUTH,
            left_end=board_ends[0],
            right_end=board_ends[1],
            consecutive_passes=0
        )

        depth = 24

        # possible_moves = list_possible_moves(sample_state, include_stats=False)
        if possible_moves is None:
            possible_moves = list_possible_moves(sample_state)
        move_scores: list[tuple[move, float]] = []

        sample_cache: dict[GameState, tuple[int, int]] = {}
        for move in possible_moves:
            if move[0] is None:
                new_state = sample_state.pass_turn()
            else:
                tile, is_left = move[0]
                new_state = sample_state.play_hand(tile, is_left)

            # _, best_score, _ = get_best_move_alpha_beta(new_state, depth, sample_cache, best_path_flag=False)
            _, best_score, _ = get_best_move_alpha_beta(new_state, depth, sample_cache, best_path_flag=False)
            move_scores.append((move[0], best_score))
        # return move[0], best_score
        return move_scores

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

        total_samples = 0
        batch_size = 16
        confidence_level = 0.95
        min_samples = 1 * batch_size
        max_samples = 50 * batch_size
        possible_moves = list_possible_moves_from_hand(final_south_hand, board_ends)

        # Add timer and time limit
        start_time = time.time()
        time_limit = 30  # 30 seconds time limit

        # Use ProcessPoolExecutor to parallelize the execution
        with ProcessPoolExecutor() as executor:
            
            while total_samples < max_samples:
                futures = [
                    executor.submit(
                        self.sample_and_search,
                        final_south_hand,
                        final_remaining_tiles_without_south_tiles,
                        player_tiles_count,
                        inferred_knowledge_for_current_player,
                        board_ends,
                        possible_moves
                    )
                    for _ in range(min(batch_size, max_samples - total_samples))
                ]
                for future in tqdm(as_completed(futures), total=len(futures), desc=f"Analyzing moves (total: {total_samples})", leave=False):
                    sample_scores = future.result()
                    for move, score in sample_scores:
                        move_scores[move].append(score)
                
                total_samples += len(futures)

                # Calculate confidence intervals
                move_stats = {}
                for move, scores in move_scores.items():
                    n = len(scores)
                    mean_score = mean(scores)
                    std_dev = stdev(scores) if n > 1 else 0
                    ci = scipy_stats.t.interval(confidence=confidence_level, df=n-1, loc=mean_score, scale=std_dev/n**0.5)
                    move_stats[move] = {"mean": mean_score, "ci_lower": ci[0], "ci_upper": ci[1]}

                if not move_scores or len(move_scores) == 1:
                    # If there's only one move or a pass, we're done after min_samples
                    max_samples = min_samples
                    continue
                
                # Print statistics after each batch
                if verbose:
                    self.print_move_statistics(move_scores, total_samples)

                # Check if we can determine the best move and update possible_moves
                sorted_moves = sorted(move_stats.items(), key=lambda x: x[1]["mean"], reverse=True)
                best_move = sorted_moves[0][0]
                best_move_stats = move_stats[best_move]
                
                # Keep only moves with overlapping confidence intervals
                possible_moves = [(move, False, False) for move, stats in sorted_moves if stats["ci_upper"] >= best_move_stats["ci_lower"]]
                
                # If only one move remains, we're done
                if len(possible_moves) == 1:
                    break

                # Check if time limit is exceeded
                if time.time() - start_time > time_limit:
                    print(f"Time limit of {time_limit} seconds exceeded. Terminating early.")
                    break

        if not move_scores:
            if verbose:
                print("No legal moves available. Player must pass.")
            return None

        if verbose:
            self.print_move_statistics(move_scores, total_samples)
            # Calculate the time taken to find the best move
            time_taken = time.time() - start_time
            print(f"\nTime taken to find the best move: {time_taken:.2f} seconds")

        best_move = max(move_scores, key=lambda x: mean(move_scores[x]))
        return best_move

    def print_move_statistics(self, move_scores: dict[move, list[float]], num_samples: int) -> None:
        print(f"\nMove Statistics (based on {num_samples} samples):")

        # Calculate statistics for each move
        move_statistics = {}
        for move, scores in move_scores.items():
            if len(scores) > 1:                
                n = len(scores)
                mean_score = mean(scores)
                std_dev = stdev(scores)
                confidence_interval = scipy_stats.t.interval(confidence=0.95, df=n-1, loc=mean_score, scale=std_dev/n**0.5)
                move_statistics[move] = {
                    "count": n,
                    "mean": mean_score,
                    "std_dev": std_dev,
                    "median": median(scores),
                    "mode": mode(scores),
                    "min": min(scores),
                    "max": max(scores),
                    "ci_lower": confidence_interval[0],
                    "ci_upper": confidence_interval[1]
                }
            else:
                move_statistics[move] = {
                    "count": len(scores),
                    "mean": scores[0],
                    "std_dev": 0,
                    "median": scores[0],
                    "mode": scores[0],
                    "min": scores[0],
                    "max": scores[0],
                    "ci_lower": scores[0],
                    "ci_upper": scores[0]
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
            print(f"  95% Confidence Interval (mean): ({stats['ci_lower']:.4f}, {stats['ci_upper']:.4f})")

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