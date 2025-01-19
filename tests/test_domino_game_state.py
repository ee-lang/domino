import pytest
from DominoGameState import DominoGameState
from domino_utils import get_impossible_tiles
from domino_data_types import DominoTile, PlayerPosition, PlayerPosition_SOUTH, PlayerPosition_EAST, PlayerPosition_NORTH, PlayerPosition_WEST

def test_rollback_no_moves():
    """Test rolling back 0 moves returns same state"""
    initial_state = DominoGameState(
        played_set=set([(6, 6)]),
        ends=(6, 6),
        next_player=1,
        player_tile_counts=[9, 10, 10, 10],
        history=[(0, ((6, 6), 'l'))],
        variant="cuban"
    )
    
    rolled_back = initial_state.rollback(0)
    assert rolled_back == initial_state

def test_rollback_single_move():
    """Test rolling back one move"""
    state = DominoGameState(
        played_set=set([(6, 6), (6, 5)]),
        ends=(5, 6),
        next_player=2,
        player_tile_counts=[9, 9, 10, 10],
        history=[
            (0, ((6, 6), 'l')),
            (1, ((6, 5), 'l'))
        ],
        variant="cuban"
    )
    
    expected = DominoGameState(
        played_set=set([(6, 6)]),
        ends=(6, 6),
        next_player=1,
        player_tile_counts=[9, 10, 10, 10],
        history=[(0, ((6, 6), 'l'))],
        variant="cuban"
    )
    
    rolled_back = state.rollback(1)
    assert rolled_back == expected

def test_rollback_multiple_moves():
    """Test rolling back multiple moves"""
    state = DominoGameState(
        played_set=set([(6, 6), (6, 5), (5, 4)]),
        ends=(4, 6),
        next_player=3,
        player_tile_counts=[9, 9, 9, 10],
        history=[
            (0, ((6, 6), 'l')),
            (1, ((6, 5), 'l')),
            (2, ((5, 4), 'l'))
        ],
        variant="cuban"
    )
    
    expected = DominoGameState(
        played_set=set([(6, 6)]),
        ends=(6, 6),
        next_player=1,
        player_tile_counts=[9, 10, 10, 10],
        history=[(0, ((6, 6), 'l'))],
        variant="cuban"
    )
    
    rolled_back = state.rollback(2)
    assert rolled_back == expected

def test_rollback_all_moves():
    """Test rolling back all moves"""
    state = DominoGameState(
        played_set=set([(6, 6), (6, 5)]),
        ends=(5, 6),
        next_player=2,
        player_tile_counts=[9, 9, 10, 10],
        history=[
            (0, ((6, 6), 'l')),
            (1, ((6, 5), 'l'))
        ],
        variant="cuban"
    )
    
    expected = DominoGameState(
        played_set=set(),
        ends=(-1, -1),
        next_player=0,
        player_tile_counts=[10, 10, 10, 10],
        history=[],
        variant="cuban"
    )
    
    rolled_back = state.rollback(2)
    assert rolled_back == expected

def test_rollback_venezuelan_variant():
    """Test rolling back with Venezuelan variant (7 tiles)"""
    state = DominoGameState(
        played_set=set([(6, 6), (6, 5)]),
        ends=(5, 6),
        next_player=2,
        player_tile_counts=[6, 6, 7, 7],
        history=[
            (0, ((6, 6), 'l')),
            (1, ((6, 5), 'l'))
        ],
        variant="venezuelan"
    )
    
    expected = DominoGameState(
        played_set=set(),
        ends=(-1, -1),
        next_player=0,
        player_tile_counts=[7, 7, 7, 7],
        history=[],
        variant="venezuelan"
    )
    
    rolled_back = state.rollback(2)
    assert rolled_back == expected

def test_rollback_with_pass_moves():
    """Test rolling back when some moves are passes"""
    state = DominoGameState(
        played_set=set([(6, 6)]),
        ends=(6, 6),
        next_player=3,
        player_tile_counts=[9, 10, 10, 10],
        history=[
            (0, ((6, 6), 'l')),
            (1, None),  # pass
            (2, None)   # pass
        ],
        variant="cuban"
    )
    
    expected = DominoGameState(
        played_set=set([(6, 6)]),
        ends=(6, 6),
        next_player=1,
        player_tile_counts=[9, 10, 10, 10],
        history=[(0, ((6, 6), 'l'))],
        variant="cuban"
    )
    
    rolled_back = state.rollback(2)
    assert rolled_back == expected

def test_rollback_excessive_steps():
    """Test rolling back more steps than available moves"""
    state = DominoGameState(
        played_set=set([(6, 6)]),
        ends=(6, 6),
        next_player=1,
        player_tile_counts=[9, 10, 10, 10],
        history=[(0, ((6, 6), 'l'))],
        variant="cuban"
    )
    
    # Should return same state when steps > len(history)
    rolled_back = state.rollback(10)
    assert rolled_back == state

def test_rollback_preserves_variant_and_first_round():
    """Test that rollback preserves variant and first_round flags"""
    state = DominoGameState(
        played_set=set([(6, 6)]),
        ends=(6, 6),
        next_player=1,
        player_tile_counts=[6, 7, 7, 7],
        history=[(0, ((6, 6), 'l'))],
        variant="venezuelan",
        first_round=True
    )
    
    rolled_back = state.rollback(1)
    assert rolled_back.variant == "venezuelan"
    assert rolled_back.first_round == True

def test_rollback_invalid_steps():
    """Test rolling back with invalid step values"""
    state = DominoGameState(
        played_set=set([(6, 6)]),
        ends=(6, 6),
        next_player=1,
        player_tile_counts=[9, 10, 10, 10],
        history=[(0, ((6, 6), 'l'))],
        variant="cuban"
    )
    
    # Negative steps should return same state
    assert state.rollback(-1) == state
    # Zero steps should return same state
    assert state.rollback(0) == state

def test_initial_game_state():
    """Test with an initial game state where no tiles have been played."""
    initial_hands = [
        {DominoTile(0, 1), DominoTile(0, 2), DominoTile(0, 3)},
        {DominoTile(1, 2), DominoTile(1, 3), DominoTile(1, 4)},
        {DominoTile(2, 3), DominoTile(2, 4), DominoTile(2, 5)},
        {DominoTile(3, 4), DominoTile(3, 5), DominoTile(3, 6)}
    ]
    game_state = DominoGameState(
        played_set=set(),
        ends=(-1, -1),
        next_player=PlayerPosition_SOUTH,
        player_tile_counts=[3, 3, 3, 3],
        history=[],
        variant="international",
        first_round=True
    )

    expected_impossible = {
        0: set(),
        1: set(),
        2: set(),
        3: set()
    }

    result = get_impossible_tiles(game_state)
    assert result == expected_impossible

def test_some_tiles_played():
    """Test with some tiles already played."""
    # played_tiles = {DominoTile(0, 1), DominoTile(1, 2)}
    played_tiles = {(0, 1), (1, 2)}
    initial_hands = [
        {DominoTile(0, 2), DominoTile(0, 3), DominoTile(0, 4)},
        {DominoTile(1, 3), DominoTile(1, 4), DominoTile(1, 5)},
        {DominoTile(2, 3), DominoTile(2, 4), DominoTile(2, 5)},
        {DominoTile(3, 4), DominoTile(3, 5), DominoTile(3, 6)}
    ]
    history = [
        (PlayerPosition_SOUTH, ((0, 1), 'l')),
        (PlayerPosition_EAST, ((1, 2), 'r')),
    ]
    game_state = DominoGameState(
        played_set=played_tiles,
        ends=(0, 2),
        next_player=PlayerPosition_SOUTH,
        player_tile_counts=[2, 2, 3, 3],
        history=history,
        variant="international",
        first_round=False
    )

    expected_impossible = {
        0: {DominoTile(0, 1), DominoTile(1, 2)},  # Just played tiles
        1: {DominoTile(0, 1), DominoTile(1, 2)},  # Just played tiles
        2: {DominoTile(0, 1), DominoTile(1, 2)},  # Just played tiles
        3: {DominoTile(0, 1), DominoTile(1, 2)},  # Just played tiles
    }   

    result = get_impossible_tiles(game_state)
    assert result == expected_impossible

def test_players_passed():
    """Test scenario where players have passed, restricting their possible tiles."""
    # played_tiles = {DominoTile(0, 1), DominoTile(1, 2)}
    played_tiles = {(0, 1), (1, 2)}
    initial_hands = [
        {DominoTile(0, 2), DominoTile(0, 3), DominoTile(0, 4)},
        {DominoTile(1, 3), DominoTile(1, 4), DominoTile(1, 5)},
        {DominoTile(2, 3), DominoTile(2, 4), DominoTile(2, 5)},
        {DominoTile(3, 4), DominoTile(3, 5), DominoTile(3, 6)}
    ]
    history = [
        (PlayerPosition_SOUTH, ((0, 1), 'l')),
        (PlayerPosition_EAST, ((1, 2), 'r')),
        (PlayerPosition_NORTH, None),  # Pass
        (PlayerPosition_WEST, None),    # Pass
    ]
    game_state = DominoGameState(
        played_set=played_tiles,
        ends=(0, 2),
        next_player=PlayerPosition_SOUTH,
        player_tile_counts=[2, 2, 3, 3],
        history=history,
        variant="international",
        first_round=False
    )

    # Players NORTH and WEST have passed, so they cannot have tiles that could connect to (0,2)
    # Tiles that connect to 0: DominoTile(0, x)
    # Tiles that connect to 2: DominoTile(2, x)
    # Therefore, NORTH and WEST cannot have any DominoTile(0, x) or DominoTile(2, x)
    expected_impossible = {
        0: {DominoTile(0, 1), DominoTile(1, 2)},  # Just played tiles
        1: {DominoTile(0, 1), DominoTile(1, 2)},  # Just played tiles
        2: {DominoTile(0, 1), DominoTile(1, 2),   # Played tiles plus
           DominoTile(0, 0), DominoTile(0, 2), DominoTile(0, 3), DominoTile(0, 4), DominoTile(0, 5), DominoTile(0, 6),  # connects to 0
           DominoTile(2, 2), DominoTile(2, 3), DominoTile(2, 4), DominoTile(2, 5), DominoTile(2, 6)},  # connects to 2
        3: {DominoTile(0, 1), DominoTile(1, 2),   # Played tiles plus
           DominoTile(0, 0), DominoTile(0, 2), DominoTile(0, 3), DominoTile(0, 4), DominoTile(0, 5), DominoTile(0, 6),  # connects to 0
           DominoTile(2, 2), DominoTile(2, 3), DominoTile(2, 4), DominoTile(2, 5), DominoTile(2, 6)}   # connects to 2
    }

    result = get_impossible_tiles(game_state)
    assert result == expected_impossible

def test_all_players_passed():
    """Test scenario where all players have passed."""
    played_tiles = {(0, 1), (1, 2)}
    initial_hands = [
        {DominoTile(0, 2), DominoTile(0, 3), DominoTile(0, 4)},
        {DominoTile(1, 3), DominoTile(1, 4), DominoTile(1, 5)},
        {DominoTile(2, 3), DominoTile(2, 4), DominoTile(2, 5)},
        {DominoTile(3, 4), DominoTile(3, 5), DominoTile(3, 6)}
    ]
    history = [
        (PlayerPosition_SOUTH, ((0, 1), 'l')),
        (PlayerPosition_EAST, ((1, 2), 'r')),
        (PlayerPosition_NORTH, None),  # Pass
        (PlayerPosition_WEST, None),    # Pass
        (PlayerPosition_SOUTH, None),   # Pass
        (PlayerPosition_EAST, None),    # Pass
    ]
    game_state = DominoGameState(
        played_set=played_tiles,
        ends=(0, 2),
        next_player=PlayerPosition_SOUTH,
        player_tile_counts=[2, 2, 3, 3],
        history=history,
        variant="international",
        first_round=False
    )

    expected_impossible = {
        0: {DominoTile(0, 1), DominoTile(1, 2),   # Played tiles plus
           DominoTile(0, 0), DominoTile(0, 2), DominoTile(0, 3), DominoTile(0, 4), DominoTile(0, 5), DominoTile(0, 6),  # connects to 0
           DominoTile(2, 2), DominoTile(2, 3), DominoTile(2, 4), DominoTile(2, 5), DominoTile(2, 6)},  # connects to 2
        1: {DominoTile(0, 1), DominoTile(1, 2),   # Played tiles plus
           DominoTile(0, 0), DominoTile(0, 2), DominoTile(0, 3), DominoTile(0, 4), DominoTile(0, 5), DominoTile(0, 6),  # connects to 0
           DominoTile(2, 2), DominoTile(2, 3), DominoTile(2, 4), DominoTile(2, 5), DominoTile(2, 6)},  # connects to 2
        2: {DominoTile(0, 1), DominoTile(1, 2),   # Played tiles plus
           DominoTile(0, 0), DominoTile(0, 2), DominoTile(0, 3), DominoTile(0, 4), DominoTile(0, 5), DominoTile(0, 6),  # connects to 0
           DominoTile(2, 2), DominoTile(2, 3), DominoTile(2, 4), DominoTile(2, 5), DominoTile(2, 6)},  # connects to 2
        3: {DominoTile(0, 1), DominoTile(1, 2),   # Played tiles plus
           DominoTile(0, 0), DominoTile(0, 2), DominoTile(0, 3), DominoTile(0, 4), DominoTile(0, 5), DominoTile(0, 6),  # connects to 0
           DominoTile(2, 2), DominoTile(2, 3), DominoTile(2, 4), DominoTile(2, 5), DominoTile(2, 6)}   # connects to 2
    }

    result = get_impossible_tiles(game_state)
    assert result == expected_impossible

def test_full_game():
    """Test a complete game where all tiles are played."""
    # TODO
    #     )
    # ]
    # game_state = DominoGameState(
    #     played_set=played_tiles,
    #     ends=(6, 6),
    #     next_player=PlayerPosition_SOUTH,
    #     player_tile_counts=[0, 0, 0, 0],
    #     history=history,
    #     variant="international",
    #     first_round=False
    # )

    # expected_impossible = {
    #     0: played_tiles,
    #     1: played_tiles,
    #     2: played_tiles,
    #     3: played_tiles
    # }

    # result = get_impossible_tiles(game_state)
    # assert result == expected_impossible 