from math import factorial, comb
from collections import namedtuple, defaultdict
import itertools
from typing import List, Dict, Tuple, Set
from domino_game_analyzer import DominoTile, PlayerPosition
from dataclasses import dataclass
import copy
import random

# Scenario = namedtuple('Scenario', ['N', 'E', 'W'])
# Scenario = namedtuple('Scenario', [('N', set[DominoTile]), ('E', set[DominoTile]), ('W', set[DominoTile])])
PlayerTiles = namedtuple('PlayerTiles', ['N', 'E', 'W'])

@dataclass(frozen=True)
class Scenario:
    N: Set[DominoTile]
    E: Set[DominoTile]
    W: Set[DominoTile]

    def total_tiles(self) -> int:
        return len(self.N) + len(self.E) + len(self.W)    

def normalize_tile(tile: Tuple[int, int]) -> str:
    return f"{min(tile)}-{max(tile)}"

# def factorial(n: int) -> int:
#     return math.factorial(n)

# def combinations(n: int, r: int) -> int:
#     return factorial(n) // (factorial(r) * factorial(n - r))

# def calculate_scenario_probability(scenario: Scenario, player_tiles: PlayerTiles, total_tiles: int) -> float:
#     n_tiles = player_tiles.N - len(scenario.N)
#     e_tiles = player_tiles.E - len(scenario.E)
#     w_tiles = player_tiles.W - len(scenario.W)
#     # print('total_tiles',total_tiles)
#     # print(f'{total_tiles + len(scenario.N) + len(scenario.E) + len(scenario.W)} choose {player_tiles.N + player_tiles.E + player_tiles.W}')
#     # print('denom',combinations(total_tiles + len(scenario.N) + len(scenario.E) + len(scenario.W), 
#     #                      player_tiles.N + player_tiles.E + player_tiles.W))
#     # return (combinations(total_tiles, n_tiles) * 
#     #         combinations(total_tiles - n_tiles, e_tiles) / 
#     #         combinations(total_tiles + len(scenario.N) + len(scenario.E) + len(scenario.W), 
#     #                      player_tiles.N + player_tiles.E + player_tiles.W))
#     # return (combinations(total_tiles, n_tiles) * 
#     #         combinations(total_tiles - n_tiles, e_tiles))
#     return (comb(total_tiles, n_tiles) * 
#             comb(total_tiles - n_tiles, e_tiles))

def calculate_scenario_probability(
    scenario: Scenario,
    player_tiles: PlayerTiles,
    total_tiles: int
) -> float:
    n_tiles = player_tiles.N - len(scenario.N)
    e_tiles = player_tiles.E - len(scenario.E)
    w_tiles = player_tiles.W - len(scenario.W)
    return (comb(total_tiles, n_tiles) * 
            comb(total_tiles - n_tiles, e_tiles))

# def generate_valid_scenarios(not_with: Dict[str, List[str]], player_tiles: PlayerTiles, 
#                              target_tile: str = None, target_player: str = None) -> List[Scenario]:
#     valid_scenarios = []
#     not_with_tiles = set.union(*not_with.values())
#     # not_with_tiles = set(sum(not_with.values(), []))
#     if target_tile:
#         not_with_tiles.add(target_tile)
    
#     def backtrack(scenario: Dict[str, Set[str]], remaining: Set[str]):
#         if not remaining:
#             valid_scenarios.append(Scenario(N=list(scenario['N']), E=list(scenario['E']), W=list(scenario['W'])))
#             return
        
#         tile = remaining.pop()
#         for player in ['N', 'E', 'W']:
#             if (tile not in not_with.get(player, []) and 
#                 len(scenario[player]) < getattr(player_tiles, player) and
#                 (tile != target_tile or player == target_player)):
#                 scenario[player].add(tile)
#                 backtrack(scenario, remaining)
#                 scenario[player].remove(tile)
#         remaining.add(tile)
    
#     initial_scenario = {'N': set(), 'E': set(), 'W': set()}
#     if target_tile and target_player:
#         initial_scenario[target_player].add(target_tile)
#         not_with_tiles.remove(target_tile)
    
#     backtrack(initial_scenario, not_with_tiles)
#     return valid_scenarios


# def generate_scenarios(
#     player_tiles: PlayerTiles,
#     not_with: dict[str, set[str]],
#     known_with: dict[str, set[str]]
# ) -> list[tuple[set[str], set[str], set[str]]]:

#     players = ['E', 'N', 'W']
#     other_players = {'E': 'NW', 'N': 'EW', 'W': 'EN'}
#     players_index = {'E': 0, 'N': 1, 'W': 2}

#     # Generate partitions for uncertain tiles
#     partitions = []
#     two_player_tiles = []
#     for player in not_with.keys():
#         for tile in not_with[player]:
#             partitions.append(other_players[player])
#             two_player_tiles.append(tile)

#     # def is_valid_scenario(scenario):
#     #     return all(len(tiles) <= getattr(player_tiles, player) for player, tiles in zip(players, scenario))

#     valid_scenarios = []

#     # Generate all possible distributions of unknown tiles
#     for distribution in itertools.product(*partitions):
#         # valid = False
#         scenario = [known_with.get(player, set()).copy() for player in players]

#         # Distribute unknown tiles according to the current distribution
#         for tile, player in zip(two_player_tiles, distribution):
#             # valid = True
#             scenario[players_index[player]].add(tile)
#             # if len(scenario[players_index[player]]) > getattr(player_tiles, player):
#             #     valid = False
#             #     break


#         # Check if the scenario is valid
#         # if is_valid_scenario(scenario):
#         if all(len(tiles) <= getattr(player_tiles, player) for player, tiles in zip(players, scenario)):
#             valid_scenarios.append(Scenario(N=scenario[1], E=scenario[0], W=scenario[2]))
#         # if valid:
#         #     valid_scenarios.append(Scenario(N=scenario[1], E=scenario[0], W=scenario[2]))

#     return valid_scenarios

def generate_scenarios(
    player_tiles: PlayerTiles,
    not_with: dict[str, set[DominoTile]],
    known_with: dict[str, set[DominoTile]]
) -> list[Scenario]:
    players = ['E', 'N', 'W']
    other_players = {'E': 'NW', 'N': 'EW', 'W': 'EN'}
    players_index = {'E': 0, 'N': 1, 'W': 2}

    # Generate partitions for uncertain tiles
    partitions = []
    two_player_tiles = []
    for player in not_with:
        for tile in not_with[player]:
            partitions.append(other_players[player])
            two_player_tiles.append(tile)

    valid_scenarios = []

    # Generate all possible distributions of unknown tiles
    for distribution in itertools.product(*partitions):
        scenario = [known_with.get(player, set()).copy() for player in players]

        # Distribute unknown tiles according to the current distribution
        for tile, player in zip(two_player_tiles, distribution):
            scenario[players_index[player]].add(tile)

        # Check if the scenario is valid
        if all(len(tiles) <= getattr(player_tiles, player) for player, tiles in zip(players, scenario)):
            valid_scenarios.append(Scenario(N=scenario[1], E=scenario[0], W=scenario[2]))

    return valid_scenarios



# # scenario_cache = {}
# import copy
# def calculate_tile_probabilities(remaining_tiles: List[Tuple[int, int]], not_with: Dict[str, List[str]], player_tiles: PlayerTiles) -> Dict[str, Dict[str, float]]:
#     normalized_tiles = [normalize_tile(tile) for tile in remaining_tiles]
#     total_tiles = len(normalized_tiles)
#     probabilities = {tile: {'N': 0.0, 'E': 0.0, 'W': 0.0} for tile in normalized_tiles}
    
#     for tile in normalized_tiles:
#         # scenarios = generate_valid_scenarios(not_with, player_tiles, target_tile=None, target_player=None)
#         known_with = {}
#         scenarios = generate_scenarios(player_tiles, not_with, known_with)

#         total_probability = 0
#         for s in scenarios:
#             # k = (frozenset(s.N), frozenset(s.E), frozenset(s.W))
#             # print('k',k)
#             # if k in scenario_cache:
#             #     assigned_tiles = scenario_cache[k]  
#             # else: 
#             #     assigned_tiles = sum(len(e) for e in s)
#             #     scenario_cache[k] = assigned_tiles
#             assigned_tiles = sum(len(e) for e in s)
#             total_probability += calculate_scenario_probability(s, player_tiles, total_tiles-assigned_tiles)
#         # total_probability = sum(calculate_scenario_probability(s, player_tiles, total_tiles-assigned_tiles) for s in scenarios)

#         not_with_local = not_with
#         for player in ['N', 'E', 'W']:
#             # if player in not_with and tile in not_with[player]:
#             if tile in set.union(*not_with.values()):
#                 if player in not_with and tile in not_with[player]:
#                     probabilities[tile][player] = 0.0
#                     # print(f'P({tile} belongs to {player}) = {probabilities[tile][player]}')
#                     continue            
#                 # if we go down this path, tile should be removed from not_with as it's a known tile
#                 # it should be removed for this iteration
#                 not_with_local = copy.deepcopy(not_with)
#                 for p in [p for p in 'NEW' if p!=player]:
#                     if p in not_with_local and tile in not_with_local[p]:
#                         not_with_local[p].remove(tile)

#             # scenarios = generate_valid_scenarios(not_with, player_tiles, target_tile=tile, target_player=player)
#             known_with = {player: {tile}}
#             scenarios = generate_scenarios(player_tiles, not_with_local, known_with)


#             if total_probability > 0:

#                 tile_probability = 0
#                 for s in scenarios:
#                     if tile in getattr(s, player):
#                         # k = (frozenset(s.N), frozenset(s.E), frozenset(s.W))
#                         # if k in scenario_cache:
#                         #     assigned_tiles = scenario_cache[k]  
#                         # else: 
#                         #     assigned_tiles = sum(len(e) for e in s)
#                         #     scenario_cache[k] = assigned_tiles
#                         assigned_tiles = sum(len(e) for e in s)
#                         tile_probability += calculate_scenario_probability(s, player_tiles, total_tiles-assigned_tiles)

#                 # tile_probability = sum(calculate_scenario_probability(s, player_tiles, total_tiles-sum(len(e) for e in s)) 
#                 #                        for s in scenarios if tile in getattr(s, player))

#                 probabilities[tile][player] = tile_probability / total_probability
#             # print(f'P({tile} belongs to {player}) = {probabilities[tile][player]}')
    
#         # print('tile,probabilities[tile]',probabilities[tile])
#         # break
#     return probabilities


# # Assumption is that the same tile can be in not_with with two (or more) different players. If it's with two players, that should go to the known_tiles
# def calculate_tile_probabilities(
#     remaining_tiles: list[DominoTile],
#     not_with: dict[str, set[DominoTile]],
#     player_tiles: PlayerTiles
# ) -> dict[DominoTile, dict[str, float]]:
#     total_tiles = len(remaining_tiles)
#     probabilities: dict[DominoTile, dict[str, float]] = {tile: {'N': 0.0, 'E': 0.0, 'W': 0.0} for tile in remaining_tiles}
#     if total_tiles == 0: return probabilities

#     # known_with: dict[str, set[DominoTile]] = {}
#     known_with: dict[str, set[DominoTile]] = {
#         'N': not_with['W'].intersection(not_with['E']),
#         'E': not_with['N'].intersection(not_with['W']),
#         'W': not_with['N'].intersection(not_with['E'])
#     }
#     sanitized_not_with = copy.deepcopy(not_with)
#     # If found a duplication in not_with, it's added now to known_with and need to be removed from not_with
#     if any(len(s)>0 for s in known_with.values()): 
#         for p, p_set in sanitized_not_with.items():
#             sanitized_not_with[p] = sanitized_not_with[p] - known_with['N'].union(known_with['E']).union(known_with['W'])

#     scenarios = generate_scenarios(player_tiles, sanitized_not_with, known_with)

#     total_probability: float = 0.0
#     for s in scenarios:
#         # assigned_tiles = sum(len(e) for e in s)
#         assigned_tiles = s.total_tiles()
#         total_probability += calculate_scenario_probability(s, player_tiles, total_tiles-assigned_tiles)

#     for tile in remaining_tiles:

#         # # known_with: dict[str, set[DominoTile]] = {}
#         # known_with: dict[str, set[DominoTile]] = {
#         #     'N': not_with['W'].intersection(not_with['E']),
#         #     'E': not_with['N'].intersection(not_with['W']),
#         #     'W': not_with['N'].intersection(not_with['E'])
#         # }
#         # sanitized_not_with = copy.deepcopy(not_with)
#         # # If found a duplication in not_with, it's added now to known_with and need to be removed from not_with
#         # if any(len(s)>0 for s in known_with.values()): 
#         #     for p, p_set in sanitized_not_with.items():
#         #         sanitized_not_with[p] = sanitized_not_with[p] - known_with['N'].union(known_with['E']).union(known_with['W'])

#         # scenarios = generate_scenarios(player_tiles, sanitized_not_with, known_with)

#         # total_probability: float = 0.0
#         # for s in scenarios:
#         #     # assigned_tiles = sum(len(e) for e in s)
#         #     assigned_tiles = s.total_tiles()
#         #     total_probability += calculate_scenario_probability(s, player_tiles, total_tiles-assigned_tiles)

#         for player in ['N', 'E', 'W']:
#             # if tile in set.union(*not_with_local.values()):
#             if player in not_with and tile in not_with[player]:
#                 probabilities[tile][player] = 0.0
#                 continue
#             if player in known_with and tile in known_with[player]:
#                 probabilities[tile][player] = 1.0
#                 continue
            
#             # remove the not_with restriction from the local copy to be able to assign the tile to one of the allowed players
#             not_with_local = copy.deepcopy(sanitized_not_with)
#             for p in [p for p in 'NEW' if p!=player]:
#                 if p in not_with_local and tile in not_with_local[p]:
#                     not_with_local[p].remove(tile)

#             if player in known_with:
#                 known_with_local = copy.deepcopy(known_with)
#                 known_with_local[player].add(tile)
#             else:
#                 known_with_local = {player: {tile}}

#             scenarios = generate_scenarios(player_tiles, not_with_local, known_with_local)

#             if total_probability > 0:
#                 tile_probability: float = 0.0
#                 for s in scenarios:
#                     # try:                
#                     #     assert len(s.N.intersection(s.W))==0 and len(s.N.intersection(s.E))==0 and len(s.E.intersection(s.W))==0
#                     # except AssertionError as ae:
#                     #     print('tile',tile)
#                     #     print('player',player)
#                     #     print('scenario error', s)
#                     #     # print('(player_tiles, not_with_local, known_with_local)',(player_tiles, not_with_local, known_with_local))
#                     #     print('player_tiles',player_tiles)
#                     #     print('not_with',not_with)
#                     #     print('sanitized_not_with',sanitized_not_with)
#                     #     print('not_with_local',not_with_local)
#                     #     print('known_with',known_with)            
#                     #     print('known_with_local',known_with_local)
#                     #     raise ae
#                     if tile in getattr(s, player):
#                         # assigned_tiles = sum(len(e) for e in s)
#                         assigned_tiles = s.total_tiles()
#                         tile_probability += calculate_scenario_probability(s, player_tiles, total_tiles-assigned_tiles)

#                 probabilities[tile][player] = tile_probability / total_probability
#         try:
#             assert abs(1.0 - sum(probabilities[tile][player] for player in probabilities[tile])) < 1e-5
#         except AssertionError as ae:
#             print('tile',tile)
#             print('probabilities[tile]',probabilities[tile])
#             print('not_with',not_with)
#             print('not_with_local',not_with_local)
#             print('known_with',known_with)            
#             print('known_with_local',known_with_local)            
#             print('prob.sum', sum(probabilities[tile][player] for player in probabilities[tile]))
#             print('scenarios',scenarios)
#             print('player_tiles',player_tiles)
#             raise ae

#     return probabilities    

# Assumption is that the same tile can not be in not_with with two (or more) different players. If it's with two players, that should go to the known_with
# known_with information is also not passed because there's no need to calculate probs for that tile.
# The function won't check for contradictory known_with and not_with information, in those cases it will return incorrect probabilities or fail
def calculate_tile_probabilities(
    remaining_tiles: list[DominoTile],
    not_with: dict[str, set[DominoTile]],
    player_tiles: PlayerTiles
) -> dict[DominoTile, dict[str, float]]:
    total_tiles = len(remaining_tiles)
    probabilities: dict[DominoTile, dict[str, float]] = {tile: {'N': 0.0, 'E': 0.0, 'W': 0.0} for tile in remaining_tiles}
    if total_tiles == 0: return probabilities

    scenarios = generate_scenarios(player_tiles, not_with, {})

    total_probability: float = 0.0
    for s in scenarios:
        assigned_tiles = s.total_tiles()
        s_prob = calculate_scenario_probability(s, player_tiles, total_tiles-assigned_tiles)
        total_probability += calculate_scenario_probability(s, player_tiles, total_tiles-assigned_tiles)


    assert total_probability > 0.0
    
    # Using only one copy
    # not_with_local = copy.deepcopy(not_with)
    
    # Aliasing the original
    not_with_local = not_with

    for tile in remaining_tiles:

        for player in ['N', 'E', 'W']:
            not_with_local_mutated = False
            if player in not_with and tile in not_with[player]:
                probabilities[tile][player] = 0.0
                continue
            # remove the not_with restriction from the local copy to be able to assign the tile to one of the allowed players
            # trying to mutate it for performance reasons
            # not_with_local = copy.deepcopy(not_with)
            for p in [p for p in 'NEW' if p!=player]:
                # if p in not_with_local and tile in not_with_local[p]:
                if tile in not_with_local[p]:
                    not_with_local[p].remove(tile)
                    not_with_local_mutated = True
                    other_player = p
            known_with_local = {player: {tile}}

            scenarios = generate_scenarios(player_tiles, not_with_local, known_with_local)
            tile_probability: float = 0.0
            for s in scenarios:
                if tile in getattr(s, player):
                    assigned_tiles = s.total_tiles()
                    tile_probability += calculate_scenario_probability(s, player_tiles, total_tiles-assigned_tiles)

            probabilities[tile][player] = tile_probability / total_probability
            # Add back the tile if necessary
            if not_with_local_mutated:
                not_with_local[other_player].add(tile)

        try:
            assert abs(1.0 - sum(probabilities[tile][player] for player in probabilities[tile])) < 1e-5
        except AssertionError as ae:
            print('tile',tile)
            print('probabilities[tile]',probabilities[tile])
            print('not_with',not_with)
            print('not_with_local',not_with_local)
            # print('known_with',known_with)            
            print('known_with_local',known_with_local)            
            print('prob.sum', sum(probabilities[tile][player] for player in probabilities[tile]))
            print('scenarios',scenarios)
            print('player_tiles',player_tiles)
            print('remaining_tiles',remaining_tiles)
            raise ae

    return probabilities    


def no_duplicates_in_not_with(not_with: dict[str, set[DominoTile]])-> bool:
    N_set = not_with.get('N',set())
    E_set = not_with.get('E',set())
    W_set = not_with.get('W',set())
    NE_set = N_set.intersection(E_set)
    WE_set = W_set.intersection(E_set)
    NW_set = N_set.intersection(W_set)
    return len(WE_set) == 0 and len(NE_set) == 0 and len(NW_set) == 0


def print_probabilities(probabilities: Dict[str, Dict[str, float]]):
    for tile, probs in probabilities.items():
        print(f"Tile {tile}:")
        for player, prob in probs.items():
            print(f"  P({player} has {tile}) = {prob:.6f}")
        print()

# Assumption: no tile should be at the same time in known_with and not_with
# def generate_sample(
#     remaining_tiles: list[DominoTile],
#     not_with: dict[str, set[DominoTile]],
#     known_with: dict[str, set[DominoTile]],
#     player_tiles: PlayerTiles
# ) -> dict[str, set[DominoTile]]:
def generate_sample(
    remaining_tiles: set[DominoTile],
    not_with: dict[str, set[DominoTile]],
    # known_with: dict[str, set[DominoTile]],
    player_tiles: PlayerTiles
) -> dict[str, set[DominoTile]]:

    assert len(remaining_tiles) == sum(e for e in player_tiles)
    assert 'S' not in not_with
    assert all(p in not_with for p in 'NEW')
    assert all(isinstance(not_with[p],set) for p in 'NEW')

    # if there's a tile with the current player and nobody else has that suit, remove that from not_with
    door_tiles = set.intersection(*not_with.values()) if not_with else set()

    assert len(door_tiles.intersection(remaining_tiles)) == 0, 'Tile in remaining_tiles and not with any player!'

    # Create local copies of not_with and known_with
    local_not_with = copy.deepcopy(not_with)
    local_known_with = {}

    if len(door_tiles) > 0:
        for p, p_set in local_not_with.items():
            local_not_with[p] = local_not_with[p] - door_tiles

    # If found a duplication in not_with, it's added now to known_with and need to be removed from not_with
    N_set = local_not_with.get('N',set())
    E_set = local_not_with.get('E',set())
    W_set = local_not_with.get('W',set())
    NE_set = N_set.intersection(E_set)
    WE_set = W_set.intersection(E_set)
    NW_set = N_set.intersection(W_set)
    if len(WE_set) > 0:
        local_known_with['N'] = WE_set
        local_not_with['W'] -= WE_set 
        local_not_with['E'] -= WE_set 
    if len(NE_set) > 0:
        local_known_with['W'] = NE_set
        local_not_with['N'] -= NE_set 
        local_not_with['E'] -= NE_set 
    if len(NW_set) > 0:
        local_known_with['E'] = NW_set
        local_not_with['N'] -= NW_set 
        local_not_with['W'] -= NW_set 



    sample = {player: set(local_known_with.get(player, set())) for player in ['N', 'E', 'W']}
    # sample = {player: set() for player in ['N', 'E', 'W']}

    remaining_counts = {
        player: getattr(player_tiles, player) - len(sample[player])
        for player in ['N', 'E', 'W']
    }

    unassigned_tiles = [tile for tile in remaining_tiles if tile not in set.union(*sample.values())]    
  
    
    while unassigned_tiles:
        # Check if there are at least two players with tiles available
        players_with_tiles = [p for p in ['N', 'E', 'W'] if remaining_counts[p] > 0]
        if len(players_with_tiles) < 2:
            # If only one player can receive tiles, assign all remaining tiles to that player
            last_player = players_with_tiles[0]
            sample[last_player].update(unassigned_tiles)
            return sample
        
        # Recalculate probabilities
        try:
            assert no_duplicates_in_not_with(local_not_with)
        except AssertionError as ae:
            print('local_not_with',local_not_with)
            raise ae
        probabilities = calculate_tile_probabilities(unassigned_tiles, local_not_with, PlayerTiles(**remaining_counts))
        # probabilities = calculate_tile_probabilities(unassigned_tiles, local_not_with, local_known_with, PlayerTiles(**remaining_counts))

        tile = random.choice(unassigned_tiles)
        tile_probs = probabilities[tile]

        valid_players = [p for p in ['N', 'E', 'W'] if remaining_counts[p] > 0 and tile not in local_not_with.get(p, set())]

        assert len(valid_players) > 0

        if len(valid_players)==1:
            chosen_player = valid_players[0]
        else:
            chosen_player = random.choices(valid_players, weights=[tile_probs[p] for p in valid_players])[0]

        # Assign the tile
        sample[chosen_player].add(tile)
        remaining_counts[chosen_player] -= 1
        unassigned_tiles.remove(tile)

        # Update local_not_with
        for player in ['N', 'E', 'W']:
            if player in local_not_with and tile in local_not_with[player]:
                local_not_with[player].remove(tile)
            # if player in local_known_with and tile in local_known_with[player]:
            #     local_known_with[player].remove(tile)

    return sample    

# Example usage
def main():
    remaining_tiles = [
        (3,6), (5,4), (2,5), (3,3), (1,3), (5,1), (1,1),
        (6,6), (2,6), (0,2), (6,5), (3,4), (2,3), (2,1),
        (4,4), (2,4), (2,2), (1,6), (5,5), (0,1), (3,5)
    ]

    # remaining_tiles = [
    #     (3,6), (5,1), (1,1),
    #     (6,6), (2,6),
    #     (4,4), (2,4),
    # ]

    
    not_with = {
        'E': {'0-1', '0-2'},
        # 'W': {'3-6'}
    }
    # not_with = {
    #     'E': {'3-6'},
    #     'W': {'4-4'}
    # }

    # known_with = {}
    
    player_tiles = PlayerTiles(N=7, E=7, W=7)  # Each player has 7 tiles

    # player_tiles = PlayerTiles(N=2, E=3, W=2)  # Each player has 7 tiles

    # Convert remaining_tiles to list[DominoTile]
    remaining_tiles_converted: list[DominoTile] = [DominoTile(min(t[0], t[1]), max(t[0], t[1])) for t in remaining_tiles]

    not_with_converted: dict[str, set[DominoTile]] = {
        player: {DominoTile(int(t.split('-')[0]), int(t.split('-')[1])) for t in tiles}
        for player, tiles in not_with.items()
    }

    known_with: dict[str, set[DominoTile]] = {}  # Assuming no known tiles for this example    
    
    # for _ in range(1000):
    #     probabilities = calculate_tile_probabilities(remaining_tiles_converted, not_with_converted, player_tiles)
    #     break
    # print_probabilities(probabilities)

    # Example usage of generate_sample
    for _ in range(1000):
        # sample = generate_sample(remaining_tiles_converted, not_with_converted, known_with, player_tiles)
        sample = generate_sample(set(remaining_tiles_converted), not_with_converted, player_tiles)
        break
    print("Generated sample:")
    for player, tiles in sample.items():
        print(f"{player}: {tiles}")    

if __name__ == "__main__":
    main()