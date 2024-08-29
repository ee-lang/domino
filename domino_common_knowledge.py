from domino_game_analyzer import GameState, PlayerPosition, DominoTile, setup_game_state
from typing import List, Tuple, Optional, Set, Dict
import copy

class CommonKnowledgeTracker:
    def __init__(self):
        self.common_knowledge_missing_suits: dict[PlayerPosition, set[int]] = {player: set() for player in PlayerPosition}
        self.played_tiles: set[DominoTile] = set()

    def update_pass(self, player: PlayerPosition, left_end: Optional[int], right_end: Optional[int]):
        if left_end is not None:
            self.common_knowledge_missing_suits[player].add(left_end)
        if right_end is not None and right_end != left_end:
            self.common_knowledge_missing_suits[player].add(right_end)

    def update_play(self, tile: DominoTile):        
        self.played_tiles.add(tile)
        # self.played_tiles.add(DominoTile(min(tile.top, tile.bottom), max(tile.top, tile.bottom)))
        # print('self.played_tiles',self.played_tiles)

    def rotate_perspective(self, new_south: PlayerPosition) -> 'CommonKnowledgeTracker':
        """
        Create a new CommonKnowledgeTracker instance with the point of view rotated
        so that the specified player becomes the new SOUTH.
        
        :param new_south: The PlayerPosition that should become the new SOUTH
        :return: A new CommonKnowledgeTracker instance with the rotated perspective
        """
        if new_south == PlayerPosition.SOUTH:
            return copy.deepcopy(self)  # Return a deep copy of the current instance

        # Create a new instance
        new_tracker = CommonKnowledgeTracker()

        # Copy the played tiles
        new_tracker.played_tiles = self.played_tiles.copy()

        # Calculate the number of clockwise rotations needed
        rotations = (new_south.value - PlayerPosition.SOUTH.value) % 4

        # Rotate the common knowledge
        for player, knowledge in self.common_knowledge_missing_suits.items():
            # Calculate the new position for each player
            new_position = PlayerPosition((player.value - rotations) % 4)
            new_tracker.common_knowledge_missing_suits[new_position] = knowledge.copy()

        return new_tracker

    def __str__(self):
        result = "Common Knowledge of players missing tiles:\n"
        for player, knowledge in self.common_knowledge_missing_suits.items():
            result += f"{player.name}: {sorted(knowledge)}\n"
        result += f"Played tiles: {sorted(str(tile) for tile in self.played_tiles)}"
        return result

def normalize_tile(tile: DominoTile) -> Tuple[int, int]:
    return (min(tile.top, tile.bottom), max(tile.top, tile.bottom))

def analyze_game_knowledge(initial_hands: list[list[DominoTile]],
                           starting_player: PlayerPosition,
                           moves: list[Optional[tuple[DominoTile, bool]]]):
    state = setup_game_state(initial_hands, starting_player, [])
    knowledge_tracker = CommonKnowledgeTracker()

    print("Initial Game State:")
    print_game_state(state)

    for turn, move in enumerate(moves, 1):
        print(f"\nTurn {turn}:")
        current_player = state.current_player
        if move is None:
            knowledge_tracker.update_pass(current_player, state.left_end, state.right_end)
            state = state.pass_turn()
            print(f"Player {current_player.name} passed.")
        else:
            # top, bottom, left = move
            tile, left = move
            # tile = next(t for t in state.get_current_hand() if normalize_tile(t) == normalize_tile(DominoTile(top, bottom)))
            knowledge_tracker.update_play(tile)
            state = state.play_hand(tile, left)
            print(f"Player {current_player.name} played {tile} on the {'left' if left else 'right'}.")

        print_game_state(state)
        print_common_knowledge(state, knowledge_tracker)

def print_game_state(state: GameState):
    print(f"Current player: {state.current_player.name}")
    print(f"Board ends: {state.left_end} | {state.right_end}")
    # for player in PlayerPosition:
    #     print(f"Player {player.name}'s hand: {state.player_hands[player.value]}")

def print_common_knowledge(state: GameState, tracker: CommonKnowledgeTracker):
    all_tiles = set(DominoTile(i, j) for i in range(7) for j in range(i, 7))
    unplayed_tiles = all_tiles - tracker.played_tiles
    # print('tracker.played_tiles',tracker.played_tiles)
    # print('unplayed_tiles',unplayed_tiles)

    print("\nCommon Knowledge:")
    for player in PlayerPosition:
        known_not_to_have = {tile for tile in unplayed_tiles 
                             if tile.top in tracker.common_knowledge_missing_suits[player] 
                             or tile.bottom in tracker.common_knowledge_missing_suits[player]}
        if known_not_to_have:
            sorted_tiles = sorted(known_not_to_have, key=lambda x: (min(x.top, x.bottom), max(x.top, x.bottom)))
            print(f"Player {player.name} doesn't have: {[f'{min(t.top, t.bottom)}|{max(t.top, t.bottom)}' for t in sorted_tiles]}")
        else:
            print(f"No certain knowledge about player {player.name}'s hand")


# Helper function to demonstrate the rotation
def print_tracker_state(tracker: CommonKnowledgeTracker, title: str):
    print(f"\n{title}")
    print(tracker)


def main():
    initial_hands = [
        [(0,3), (6,4), (0,6), (0,0), (4,0), (4,1), (5,0)],
        [(3,6), (5,4), (2,5), (3,3), (1,3), (5,1), (1,1)],
        [(6,6), (2,6), (0,2), (6,5), (3,4), (2,3), (2,1)],
        [(4,4), (2,4), (2,2), (1,6), (5,5), (0,1), (3,5)]
    ]

    starting_player = PlayerPosition.SOUTH
    moves = [
        (0, 0, True),
        None,
        (0, 2, True),
        (2, 2, True),
        (4, 0, False),
        (4, 5, False),
        (6, 5, False),
        (1, 6, False),
        (4, 1, False),            
        (2, 5, True),
        (3, 4, False),
        (5, 5, True),        
        (5, 0, True),        
        (3, 3, False),
        (2, 3, False),
        (0, 1, True),
        None,
        (1, 3, True),
        (1, 2, False), 
        (3, 5, True),
        None,
        (5, 1, True),    
        None,
        None,
        None,
        (1, 1, True)   
    ]

    # analyze_game_knowledge(initial_hands, starting_player, moves)


    # new tracker code 
    tracker = CommonKnowledgeTracker()
    
    # Simulate some game actions
    tracker.update_pass(PlayerPosition.NORTH, 3, 5)
    tracker.update_play(DominoTile(3, 5))
    tracker.update_pass(PlayerPosition.EAST, 3, 6)
    tracker.update_play(DominoTile(5, 6))

    print_tracker_state(tracker, "Initial State (SOUTH perspective)")

    # Rotate perspective to WEST
    west_tracker = tracker.rotate_perspective(PlayerPosition.WEST)
    print_tracker_state(west_tracker, "WEST perspective")

    # Rotate perspective to NORTH
    north_tracker = tracker.rotate_perspective(PlayerPosition.NORTH)
    print_tracker_state(north_tracker, "NORTH perspective")

    # Show that the original tracker is unchanged
    print_tracker_state(tracker, "Original tracker (still SOUTH perspective)")



if __name__ == "__main__":
    main()