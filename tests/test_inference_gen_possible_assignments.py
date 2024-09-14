import pytest
from domino_data_types import DominoTile
from inference import generate_possible_assignments

def test_generate_possible_assignments_empty():
    """Test with no constraints."""
    not_with = {'S': set(), 'E': set(), 'N': set(), 'W': set()}
    constrained_tiles, possible_assignments = generate_possible_assignments(not_with)
    assert constrained_tiles == []
    assert possible_assignments == []

def test_generate_possible_assignments_single_constraint():
    """Test with a single tile constrained to one player."""
    tile1 = DominoTile(1, 2)
    not_with = {'S': {tile1}, 'E': set(), 'N': set(), 'W': set()}
    constrained_tiles, possible_assignments = generate_possible_assignments(not_with)
    assert constrained_tiles == [tile1]
    assert possible_assignments == [['E', 'N', 'W']]

def test_generate_possible_assignments_multiple_constraints():
    """Test with multiple tiles constrained to different players."""
    tile1 = DominoTile(1, 2)
    tile2 = DominoTile(2, 3)
    not_with = {
        'S': {tile1},
        'E': {tile2},
        'N': set(),
        'W': set(),
    }
    constrained_tiles, possible_assignments = generate_possible_assignments(not_with)
    assert constrained_tiles == [tile1, tile2]
    assert possible_assignments == [
        ['E', 'N', 'W'],
        ['S', 'N', 'W']
    ]

def test_generate_possible_assignments_tile_constrained_by_multiple_players():
    """Test with a single tile constrained to multiple players."""
    tile1 = DominoTile(1, 2)
    not_with = {
        'S': {tile1},
        'E': {tile1},
        'N': set(),
        'W': set(),
    }
    constrained_tiles, possible_assignments = generate_possible_assignments(not_with)
    assert constrained_tiles == [tile1]
    assert possible_assignments == [
        ['N', 'W']  # tile1 not with S and E
    ]

def test_generate_possible_assignments_missing_player_keys():
    """Test with some players missing from the not_with dictionary."""
    tile1 = DominoTile(1, 2)
    not_with = {'S': {tile1}, 'E': set()}  # 'N' and 'W' are missing
    constrained_tiles, possible_assignments = generate_possible_assignments(not_with)
    # Assuming missing players have no constraints
    assert constrained_tiles == [tile1]
    assert possible_assignments == [['E', 'N', 'W']]