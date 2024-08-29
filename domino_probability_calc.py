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


# Assumption is that the same tile can be in not_with with two (or more) different players. If it's with two players, that should go to the known_tiles
def calculate_tile_probabilities(
    remaining_tiles: list[DominoTile],
    not_with: dict[str, set[DominoTile]],
    player_tiles: PlayerTiles
) -> dict[DominoTile, dict[str, float]]:
    total_tiles = len(remaining_tiles)
    probabilities: dict[DominoTile, dict[str, float]] = {tile: {'N': 0.0, 'E': 0.0, 'W': 0.0} for tile in remaining_tiles}

    for tile in remaining_tiles:
        # known_with: dict[str, set[DominoTile]] = {}
        known_with: dict[str, set[DominoTile]] = {
            'N': not_with['W'].intersection(not_with['E']),
            'E': not_with['N'].intersection(not_with['W']),
            'W': not_with['N'].intersection(not_with['E'])
        }
        if any(len(s)>0 for s in known_with.values()):
            # Remove any from not_with
            for p, p_set in not_with.items():
                not_with[p] = not_with[p] - not_with['N'].union(not_with['E']).union(not_with['W'])

        scenarios = generate_scenarios(player_tiles, not_with, known_with)

        total_probability: float = 0.0
        for s in scenarios:
            # assigned_tiles = sum(len(e) for e in s)
            assigned_tiles = s.total_tiles()
            total_probability += calculate_scenario_probability(s, player_tiles, total_tiles-assigned_tiles)

        not_with_local = copy.deepcopy(not_with)
        for player in ['N', 'E', 'W']:
            if tile in set.union(*not_with.values()):
                if player in not_with and tile in not_with[player]:
                    probabilities[tile][player] = 0.0
                    continue
                # not_with_local = copy.deepcopy(not_with)
                for p in [p for p in 'NEW' if p!=player]:
                    if p in not_with_local and tile in not_with_local[p]:
                        not_with_local[p].remove(tile)

            if player in known_with:
                known_with_local = copy.deepcopy(known_with)
                known_with_local[player].add(tile)
            else:
                known_with_local = {player: {tile}}
            scenarios = generate_scenarios(player_tiles, not_with_local, known_with_local)

            if total_probability > 0:
                tile_probability: float = 0.0
                for s in scenarios:
                    if tile in getattr(s, player):
                        # assigned_tiles = sum(len(e) for e in s)
                        assigned_tiles = s.total_tiles()
                        tile_probability += calculate_scenario_probability(s, player_tiles, total_tiles-assigned_tiles)

                probabilities[tile][player] = tile_probability / total_probability
        try:
            assert abs(1.0 - sum(probabilities[tile][player] for player in probabilities[tile])) < 1e-5
        except AssertionError as ae:
            print('tile',tile)
            print('probabilities[tile]',probabilities[tile])
            print('prob.sum', sum(probabilities[tile][player] for player in probabilities[tile]))
            raise ae

    return probabilities    

def print_probabilities(probabilities: Dict[str, Dict[str, float]]):
    for tile, probs in probabilities.items():
        print(f"Tile {tile}:")
        for player, prob in probs.items():
            print(f"  P({player} has {tile}) = {prob:.6f}")
        print()

def generate_sample(
    remaining_tiles: list[DominoTile],
    not_with: dict[str, set[DominoTile]],
    known_with: dict[str, set[DominoTile]],
    player_tiles: PlayerTiles
) -> dict[str, set[DominoTile]]:

    assert len(remaining_tiles) == sum(e for e in player_tiles)
    assert 'S' not in not_with

    # Create local copies of not_with and known_with
    local_not_with = copy.deepcopy(not_with)
    local_known_with = copy.deepcopy(known_with)

    sample = {player: set(local_known_with.get(player, set())) for player in ['N', 'E', 'W']}
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
        probabilities = calculate_tile_probabilities(unassigned_tiles, local_not_with, PlayerTiles(**remaining_counts))

        tile = random.choice(unassigned_tiles)
        tile_probs = probabilities[tile]

        valid_players = [p for p in ['N', 'E', 'W'] if remaining_counts[p] > 0 and tile not in local_not_with.get(p, set())]

        assert len(valid_players) > 0

        if len(valid_players)==1:
            chosen_player = valid_players[0]
        else:
            # if not valid_players:
            #     # If no valid players, redistribute probabilities
            #     total_prob = sum(tile_probs[p] for p in ['N', 'E', 'W'] if remaining_counts[p] > 0)
            #     if total_prob == 0:
            #         # If all probabilities are 0, assign equal probabilities
            #         valid_players = [p for p in ['N', 'E', 'W'] if remaining_counts[p] > 0]
            #         tile_probs = {p: 1/len(valid_players) for p in valid_players}
            #     else:
            #         # Normalize probabilities
            #         tile_probs = {p: tile_probs[p] / total_prob if remaining_counts[p] > 0 else 0 for p in ['N', 'E', 'W']}

            try:
                chosen_player = random.choices(valid_players, weights=[tile_probs[p] for p in valid_players])[0]
            except ValueError as e:
                print('tile',tile)
                print('valid_players',valid_players)
                print('tile_probs',tile_probs)
                print('remaining_counts',remaining_counts)
                print('local_not_with',local_not_with)
                raise e

        # Assign the tile
        sample[chosen_player].add(tile)
        remaining_counts[chosen_player] -= 1
        unassigned_tiles.remove(tile)

        # Update local_not_with and local_known_with
        for player in ['N', 'E', 'W']:
            if player in local_not_with and tile in local_not_with[player]:
                local_not_with[player].remove(tile)
        local_known_with.setdefault(chosen_player, set()).add(tile)

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
        sample = generate_sample(remaining_tiles_converted, not_with_converted, known_with, player_tiles)
        break
    print("Generated sample:")
    for player, tiles in sample.items():
        print(f"{player}: {tiles}")    

if __name__ == "__main__":
    main()