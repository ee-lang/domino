import random
from DominoPlayer import HumanPlayer, available_moves, stats
from collections import defaultdict
from DominoGameState import DominoGameState
from domino_data_types import PLAYERS, PLAYERS_INDEX, DominoTile, PlayerPosition, GameState, PlayerPosition_SOUTH, PlayerPosition_names, PlayerTiles, PlayerTiles4, move
from get_best_move2 import get_best_move_alpha_beta
from domino_utils import history_to_domino_tiles_history, list_possible_moves, list_possible_moves_from_hand
from domino_game_tracker import domino_game_state_our_perspective, generate_sample_from_game_state
from domino_common_knowledge import CommonKnowledgeTracker
from statistics import mean, median, stdev, mode
import copy, time
from tqdm import tqdm
from concurrent.futures import ProcessPoolExecutor, as_completed
from inference import probability_from_another_perspective
from scipy import stats as scipy_stats

class AnalyticAgentPlayer(HumanPlayer):
    def __init__(self, position: int = 0) -> None:
        super().__init__()
        self.move_history: list[tuple[int, tuple[tuple[int, int], str]|None]] = []
        self.tile_count_history: dict[int, list[int]] = defaultdict(list)
        self.position = position
        self.unlikely_tiles: dict[int, set[DominoTile]] = {i: set() for i in range(4)}

    def next_move(self, game_state: DominoGameState, player_hand: list[tuple[int,int]], verbose: bool = True) -> tuple[tuple[int,int], str] | None:
        # if self.first_game:
        if game_state.first_round:
            # Check if the move is forced
            if game_state.variant in {'international','venezuelan'} and len(game_state.history)==0:
                print('Playing mandatory (6,6) opening on the first game.')
                return (6,6),'l'

        if len(game_state.history) > 1:  # Ensure there are at least two moves in history
            # for i in range(len(game_state.history) - 1, max(0, len(game_state.history) - 4), -1):  # Process the last three moves in reverse order
            for i in range(3):  # Process the last three moves in reverse order
                last_move = game_state.history[-(i+1)]  # Access moves in reverse order
                player_pos_from_current_player_pov = (last_move[0] - self.position) % 4
                retro_game_state = game_state.rollback(i)
                self.update_unlikely_tiles(retro_game_state, player_pos_from_current_player_pov, actual_move=last_move, tiles_not_in_players_hand=player_hand)

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
        # num_samples = 24

        best_move = self.get_best_move(set(_player_hand), _remaining_tiles, _knowledge_tracker, _player_tiles_count, _board_ends, verbose=verbose)

        if best_move is None:
            return None
        else:
            tile, is_left = best_move
            side = 'l' if is_left else 'r'
            return (tile.top, tile.bottom), side

    def update_unlikely_tiles(self, game_state: DominoGameState, player_from_south_pov: int, actual_move: tuple[tuple[int,int],str], tiles_not_in_players_hand: list[tuple[int,int]]) -> None:
        unplayed_tiles = self.get_unplayed_tiles(game_state, [])
        _unplayed_tiles = DominoTile.loi_to_domino_tiles(unplayed_tiles)
        _tiles_not_in_players_hand = DominoTile.loi_to_domino_tiles(tiles_not_in_players_hand)
        # Generate all possible tiles that could have been played (except for the first move of the game)
        # The tile can't be in the tiles_not_in_players_hand or among the played tiles
        possible_tiles = self.generate_possible_tiles(game_state.ends, _unplayed_tiles, _tiles_not_in_players_hand)
        # Filter out the tiles that are not in the player's hand (i.e. suits where the player passed)
        # TODO: Implement this

        # Build common knowledge
        common_knowledge_with_tiles: dict[str, list[DominoTile]] = {
            'S': [actual_move],
            'E': [],
            'N': [],
            'W': [],
        }
        common_knowledge_not_with_tiles: dict[str, set[DominoTile]] = {
            'S': set(_tiles_not_in_players_hand),
            'E': set(),
            'N': set(),
            'W': set(),
        }

        # For each possible tile that theoretically could have been played
        for tile in possible_tiles:
            # Sample a hand for every player (including south)
            # Constraint: south cannot have tiles from tiles_not_in_players_hand
            # Constraint: south has to have the actual move
            # Constraint: south has to have the tile we are comparing against
            sample = self.generate_sample_from_game_state_from_another_perspective(
                _unplayed_tiles,
                common_knowledge_with_tiles,
                common_knowledge_not_with_tiles,
                _player_tiles_count
            )

        # Calculate statistics for the samples
        # If a tile has significantly better expected score than the actual , add it to the unlikely_tiles set for the player

        pass
    

    def generate_sample_from_game_state_from_another_perspective(unplayed_tiles: list[DominoTile], known_with_tiles: dict[str, list[DominoTile]], not_with_tiles: dict[PlayerPosition, set[DominoTile]], player_tiles: PlayerTiles4)-> dict[str, list[DominoTile]]:
        sample: dict[str, list[DominoTile]] = {player: [] for player in PLAYERS}

        for player in PLAYERS:
            sample[player] = known_with_tiles.get(player, [])

        assert all(len(sample[PLAYERS[player]]) <= player_tiles[player] for player in range(4)), 'Sample cannot have more tiles than the player has'

        known_tiles_set = set()  # Create a set to hold all known tiles
        for tiles in known_with_tiles.values():
            known_tiles_set.update(tiles)  # Add known tiles to the set

        remaining_counts = {
            player: getattr(player_tiles, player) - len(sample[player])
            for player in PLAYERS
        }

        local_not_with_tiles = {k:set(t for t in v) for k,v in not_with_tiles.items()}
        local_unplayed_tiles = [tile for tile in unplayed_tiles if tile not in known_tiles_set]  # Filter unplayed tiles

        while local_unplayed_tiles:

            # Check if there are at least two players with tiles available
            players_with_tiles = [p for p in PLAYERS if remaining_counts[p] > 0]
            if len(players_with_tiles) < 2:
                # If only one player can receive tiles, assign all remaining tiles to that player
                last_player = players_with_tiles[0]
                sample[last_player].extend(local_unplayed_tiles)
                return sample            
            
            # print('sample',sample)
            tile_probabilities = probability_from_another_perspective(local_unplayed_tiles, local_not_with_tiles, PlayerTiles4(**remaining_counts))
            # for player in PLAYERS:
            #     print(f"{player}:")
            #     for tile, prob in tile_probabilities[PLAYERS_INDEX[player]].items():
            #         print(f"  {tile}: {prob:.4f}")
            #     print()
            
            # Choose a random tile uniformly from the local unplayed tiles
            chosen_tile = random.choice(local_unplayed_tiles)
            
            # Choose a player for the tile based on probabilities
            player_probs = [tile_probabilities[player][chosen_tile] for player in range(4)]
            chosen_player = random.choices(PLAYERS, weights=player_probs)[0]
            
            # Add the tile to the chosen player's sample
            sample[chosen_player].append(chosen_tile)
            
            # Update the remaining tiles and player tile counts
            local_unplayed_tiles.remove(chosen_tile)
            remaining_counts[chosen_player] -= 1
            
            # Update not_with_tiles
            for player in PLAYERS:
                if player in local_not_with_tiles and chosen_tile in local_not_with_tiles[player]:
                    local_not_with_tiles[player].remove(chosen_tile)

        return sample

    def generate_possible_tiles(self, board_ends: tuple[int,int], unplayed_tiles: set[DominoTile], tiles_not_possible: set[DominoTile]) -> set[DominoTile]:
        possible_tiles = set()
               
        if board_ends != (-1, -1):  # Except first move of the game
            left_end, right_end = board_ends
            for tile in unplayed_tiles:
                if tile.top == left_end or tile.bottom == left_end:
                    possible_tiles.add(tile)
                if tile.top == right_end or tile.bottom == right_end:
                    possible_tiles.add(tile)
        
        # Remove played tiles and tiles not in player's hand
        possible_tiles = possible_tiles - tiles_not_possible
        
        return possible_tiles

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

        depth = 99 # Set it high enough, that it is never reached in practice, so the score is an integer

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

            _, best_score, _ = get_best_move_alpha_beta(new_state, depth, sample_cache, best_path_flag=False)
            move_scores.append((move[0], best_score))
        return move_scores

    def get_best_move(self, final_south_hand: set[DominoTile], remaining_tiles: set[DominoTile], 
                      knowledge_tracker: CommonKnowledgeTracker, player_tiles_count: dict[PlayerPosition, int], 
                      board_ends: tuple[int|None,int|None], verbose: bool = False) -> tuple[DominoTile, bool] | None:

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

        # Use ProcessPoolExecutor to parallelize the execution
        total_samples = 0
        batch_size = 16
        confidence_level = 0.95
        min_samples = 3 * batch_size
        max_samples = 75 * batch_size
        possible_moves = list_possible_moves_from_hand(final_south_hand, board_ends)

        # Add timer and time limit
        start_time = time.time()
        time_limit = 60  # 30 seconds time limit

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

                # Check if time limit is exceeded
                if time.time() - start_time > time_limit:
                    print(f"Time limit of {time_limit} seconds exceeded. Terminating early.")
                    break
                
                # Print statistics after each batch
                if verbose:
                    self.print_move_statistics(move_scores, total_samples)

                if not move_scores or len(move_scores) == 1:
                    # If there's only one move or a pass, we're done after min_samples
                    max_samples = min_samples
                    continue

                # Check if we can determine the best move and update possible_moves
                sorted_moves = sorted(move_stats.items(), key=lambda x: x[1]["mean"], reverse=True)
                best_move = sorted_moves[0][0]
                best_move_stats = move_stats[best_move]
                
                # Keep only moves with overlapping confidence intervals only if we have at least min_samples for every move
                if all(len(scores) >= min_samples for scores in move_scores.values()):
                    possible_moves = [(move, False, False) for move, stats in sorted_moves if stats["ci_upper"] >= best_move_stats["ci_lower"]]
                
                # If only one move remains, we're done after min_samples
                if len(possible_moves) == 1:
                    max_samples = min_samples
                    continue


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