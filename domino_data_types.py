from dataclasses import dataclass
from collections import namedtuple

type move = tuple[DominoTile, bool]|None
type PlayerPosition = int

PlayerPosition_SOUTH = 0
PlayerPosition_EAST = 1
PlayerPosition_NORTH = 2
PlayerPosition_WEST = 3

def next_player(pos: PlayerPosition)-> PlayerPosition:
    return (pos + 1) % 4

PlayerPosition_names = ['SOUTH', 'EAST', 'NORTH', 'WEST']

PLAYERS = ['S', 'E', 'N', 'W']
PLAYERS_INDEX = {'S': 0, 'E': 1, 'N': 2, 'W': 3}

PlayerTiles = namedtuple('PlayerTiles', ['N', 'E', 'W'])

PlayerTiles4 = namedtuple('PlayerTiles4', ['S', 'N', 'E', 'W'])

# @dataclass(frozen=True)
@dataclass
class DominoTile:
    top: int
    bottom: int

    @classmethod
    def new_tile(cls, top: int, bottom: int) -> 'DominoTile':
        return cls(min(top, bottom), max(top, bottom))

    @classmethod
    def loi_to_domino_tiles(cls, tuple_list: list[tuple[int, int]]) -> list['DominoTile']:
        return [DominoTile.new_tile(left, right) for left, right in tuple_list]

    def __hash__(self) -> int:
        # return hash((self.top, self.bottom))
        return (self.top << 3) + self.bottom

    def __eq__(self, other: object) -> bool:
        if isinstance(other, DominoTile):
            return self.top == other.top and self.bottom == other.bottom
        return False

    def __repr__(self) -> str:
        return f"{self.top}|{self.bottom}"

    def can_connect(self, end: int|None) -> bool:
        if end is None:  # This allows any tile to be played on an empty board
            return True
        return self.top == end or self.bottom == end

    def get_other_end(self, connected_end: int) -> int:
        return self.bottom if connected_end == self.top else self.top

    def get_pip_sum(self) -> int:
        return self.top + self.bottom

# @dataclass(frozen=True)
@dataclass
class GameState:
    player_hands: tuple[frozenset[DominoTile], ...]
    current_player: PlayerPosition
    left_end: int|None
    right_end: int|None
    consecutive_passes: int

    def __hash__(self) -> int:
        return hash((self.player_hands, self.current_player, self.left_end, self.right_end, self.consecutive_passes))

    @classmethod
    def new_game(cls, player_hands: list[list[DominoTile]]) -> 'GameState':
        return cls(
            # player_hands=tuple(frozenset(DominoTile(top, bottom) for top, bottom in hand) for hand in player_hands),
            player_hands=tuple(frozenset(tile for tile in hand) for hand in player_hands),
            current_player=PlayerPosition_SOUTH,
            left_end=None,
            right_end=None,
            consecutive_passes=0
        )

    def play_hand(self, tile: DominoTile, left: bool) -> 'GameState':
        new_hands = list(self.player_hands)
        new_hands[self.current_player] = self.player_hands[self.current_player] - frozenset([tile])

        if self.left_end is None or self.right_end is None:
            new_left_end, new_right_end = tile.top, tile.bottom
        elif left:
            new_left_end = tile.get_other_end(self.left_end)
            new_right_end = self.right_end
        else:
            new_left_end = self.left_end
            new_right_end = tile.get_other_end(self.right_end)

        return GameState(
            player_hands=tuple(new_hands),
            # current_player=self.current_player.next(),
            current_player=next_player(self.current_player),
            left_end=new_left_end,
            right_end=new_right_end,
            consecutive_passes=0
        )

    def pass_turn(self) -> 'GameState':
        return GameState(
            player_hands=self.player_hands,
            # current_player=self.current_player.next(),
            current_player=next_player(self.current_player),
            left_end=self.left_end,
            right_end=self.right_end,
            consecutive_passes=self.consecutive_passes + 1
        )

    def is_game_over(self) -> bool:
        return any(len(hand) == 0 for hand in self.player_hands) or self.consecutive_passes == 4
    # def is_game_over(self) -> bool:
    #     cy_state = GameStateCy(
    #         self.player_hands,
    #         self.current_player.value,
    #         self.left_end if self.left_end is not None else -1,
    #         self.right_end if self.right_end is not None else -1,
    #         self.consecutive_passes
    #     )
    #     return cy_state.is_game_over()
    # def is_game_over(self) -> bool:
    #     return GameStateCy.static_is_game_over(self.player_hands, self.consecutive_passes)

    def get_current_hand(self) -> frozenset[DominoTile]:
        # return self.player_hands[self.current_player.value]
        return self.player_hands[self.current_player]