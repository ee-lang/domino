from DominoPlayer import HumanPlayer, available_moves, stats
from collections import defaultdict, Counter
from DominoGameState import DominoGameState
from domino_game_analyzer import DominoTile, PlayerPosition, GameState, get_best_move_alpha_beta, list_possible_moves
from domino_utils import history_to_domino_tiles_history
from domino_game_tracker import domino_game_state_our_perspective, generate_sample_from_game_state
from domino_common_knowledge import CommonKnowledgeTracker
from statistics import mean, median, stdev, mode
import copy
from tqdm import tqdm

class HumanPlayerWithAnalytics(HumanPlayer):
    def __init__(self):
        super().__init__()
        self.move_history = []
        self.tile_count_history = defaultdict(list)
        self.round_scores = []

    def next_move(self, game_state: DominoGameState, player_hand: list[tuple[int,int]]) -> tuple[tuple[int,int], str] | None:
        self.update_missing_tiles(game_state)
        
        while True:
            try:
                lom = available_moves(game_state, player_hand)
                print('HumanPlayer.played_tiles', game_state.played_set)
                
                unplayed_tiles = self.get_unplayed_tiles(game_state, player_hand)
                _unplayed_tiles = DominoTile.loi_to_domino_tiles(unplayed_tiles)
                print(f'HumanPlayer.unplayed_tiles ({len(_unplayed_tiles)} remaining):', _unplayed_tiles)


                remaining_suits = self.count_remaining_pips(unplayed_tiles)
                print('HumanPlayer.remaining_tiles_per_suit:', remaining_suits)
                
                self.display_possible_tiles_for_players(game_state, unplayed_tiles)
                
                _player_hand = DominoTile.loi_to_domino_tiles(player_hand)
                print('HumanPlayer.hand:', _player_hand)                

                max_pips = 9 if game_state.variant == "cuban" else 6
                hand_stats = stats(player_hand, max_pips)
                sorted_hands_freq = sorted([(k, v) for k, v in hand_stats.items()], key=lambda x: x[1], reverse=True)
                print('HumanPlayer.hand_stats:', [f'{k}: {v}' for k,v in sorted_hands_freq])                

                # Display the number of tiles each player has
                print('Number of tiles per player:', game_state.player_tile_counts)

                # Reconstruct the game state till now
                # print('GameState.history', game_state.history)
                _moves = history_to_domino_tiles_history(game_state.history)
                # print('GameState._moves', _moves)
                _remaining_tiles = set(_unplayed_tiles)
                # _initial_player_tiles = {p: game_state.player_tile_counts[p.value] for p in PlayerPosition}
                _initial_player_tiles = {p: 7 for p in PlayerPosition}
                # print('_initial_player_tiles',_initial_player_tiles)
                _starting_player = PlayerPosition(game_state.history[0][0]) if len(game_state.history)>0 else PlayerPosition.SOUTH
                current_player, _final_remaining_tiles, _board_ends, _player_tiles_count, _knowledge_tracker = domino_game_state_our_perspective(
                    _remaining_tiles, _moves, _initial_player_tiles, current_player=_starting_player)                
                print('_starting_player',_starting_player)
                print('current_player',current_player)
                print('_final_remaining_tiles',_final_remaining_tiles)
                print('_board_ends',_board_ends)
                print('_player_tiles_count',_player_tiles_count)
                print('_knowledge_tracker',_knowledge_tracker)

                num_samples = 1000 if len(game_state.history) > 8 else 100 if len(game_state.history) > 4 else 25 if len(game_state.history) > 0 else 1
                self.print_analytics(set(_player_hand), _remaining_tiles, _knowledge_tracker, _player_tiles_count, _board_ends, num_samples = num_samples)

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
                raise e

    def end_round(self, scores: list[int], team: int):
        super().end_round(scores, team)
        self.record_round_score(scores)

    def record_move(self, game_state: DominoGameState, move: tuple[tuple[int, int], str]|None):
        self.move_history.append((game_state.next_player, move))
        for i, count in enumerate(game_state.player_tile_counts):
            self.tile_count_history[i].append(count)

    def record_round_score(self, scores: list[int]):
        self.round_scores.append(scores)

    def get_move_history(self):
        return self.move_history

    def get_tile_count_history(self):
        return dict(self.tile_count_history)

    def get_round_scores(self):
        return self.round_scores

    def print_analytics(self, final_south_hand: set[DominoTile], remaining_tiles: set[DominoTile], knowledge_tracker: CommonKnowledgeTracker, player_tiles_count: dict[PlayerPosition, int], board_ends: tuple[int|None,int|None], num_samples = 1000) -> None:

        # print('knowledge_tracker pre-rotation', knowledge_tracker)
        # knowledge_tracker = knowledge_tracker.rotate_perspective(current_player)
        # print('knowledge_tracker post-rotation', knowledge_tracker)

        inferred_knowledge: dict[PlayerPosition, set[DominoTile]] = {
            player: set() for player in PlayerPosition
        }

        for tile in remaining_tiles:
            for player in PlayerPosition:
                if tile.top in knowledge_tracker.common_knowledge_missing_suits[player] or tile.bottom in knowledge_tracker.common_knowledge_missing_suits[player]:
                    inferred_knowledge[player].add(tile)

        final_remaining_tiles_without_south_tiles = remaining_tiles - final_south_hand 
        inferred_knowledge_for_current_player = copy.deepcopy(inferred_knowledge)
        for player, tiles in inferred_knowledge_for_current_player.items():
            inferred_knowledge_for_current_player[player] = tiles - final_south_hand

        # num_samples = 1000
        move_scores = defaultdict(list)

        for _ in tqdm(range(num_samples)):
            # Generate a sample based on the current game state
            sample = generate_sample_from_game_state(
                # current_player,
                PlayerPosition.SOUTH,
                final_south_hand,
                final_remaining_tiles_without_south_tiles,
                player_tiles_count,
                inferred_knowledge_for_current_player
            )

            # Create a game state from the sample. The order is important!
            sample_hands = (
                frozenset(final_south_hand),  # South's hand
                frozenset(sample['E']),       # East's hand
                frozenset(sample['N']),       # North's hand
                frozenset(sample['W'])        # West's hand
            )

            # Create a new GameState object
            sample_state = GameState(
                player_hands=sample_hands,
                # current_player=current_player,
                current_player=PlayerPosition.SOUTH,
                left_end=board_ends[0],
                right_end=board_ends[1],
                consecutive_passes=0  # Assuming we start with 0 consecutive passes
            )

            # Analyze each possible move
            move_analysis = []        
            # Find the best move using get_best_move_alpha_beta
            depth = 24  # You can adjust this depth based on your performance requirements

            # Get the list of possible moves
            possible_moves = list_possible_moves(sample_state, include_stats=False)
            
            for move in possible_moves:
                if move[0] is None:  # Pass move
                    new_state = sample_state.pass_turn()
                else:
                    tile, is_left = move[0]
                    new_state = sample_state.play_hand(tile, is_left)
                
                # best_move, best_score, optimal_path = get_best_move_alpha_beta(new_state, depth)
                best_move, best_score, __ = get_best_move_alpha_beta(new_state, depth)
                
                move_analysis.append({
                    'move': move[0],
                    'resulting_best_move': best_move,
                    'expected_score': best_score
                    # 'optimal_path': optimal_path
                })
                if move[0] is not None:  # Pass move
                    # print(f'Move {move[0]} resulted in {best_score}')
                    move_scores[move[0]].append(best_score)

        # Calculate statistics for each move
        move_statistics = {}
        for _move, scores in move_scores.items():
            move_statistics[_move] = {
                "count": len(scores),
                "mean": mean(scores),
                "std_dev": stdev(scores) if len(scores) > 1 else 0,
                "median": median(scores),
                "mode": mode(scores),
                "min": min(scores),
                "max": max(scores)
            }

        # Sort moves by their mean score, descending order
        sorted_moves = sorted(move_statistics.items(), key=lambda x: x[1]["mean"], reverse=True)

        # Print statistics for each move
        print(f"\nMove Statistics (based on {num_samples} samples):")
        for __move, stats in sorted_moves:
            # if __move is None:
            if __move == 'Pass':
                move_str = "Pass"
            else:
                tile, is_left = __move
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
        _best_move = max(move_statistics, key=lambda x: move_statistics[x]["mean"], default=None)
        best_stats = move_statistics[_best_move] if _best_move is not None else {'mean': mean([e['expected_score'] for e in move_analysis])}

        print("\nBest Move Overall:")
        if _best_move is None:
            print(f"Best move: Pass")
        else:
            tile, is_left = _best_move
            direction = "left" if is_left else "right"
            print(f"Best move: Play {tile} on the {direction}")
        print(f"Mean Expected Score: {best_stats['mean']:.4f}")
        # print(f"Frequency: {best_stats['count']} out of {num_samples} samples")
