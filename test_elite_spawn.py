#!/usr/bin/env python3
"""
Elite spawn rate testing script
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from dungeon.dungeon_map import DungeonMap, NodeType

def test_elite_spawn_rates():
    """Test elite spawn rates across different floors"""
    print("=== Elite Spawn Rate Test ===")
    
    # Test multiple maps to get statistical data
    num_tests = 100
    elite_counts_by_floor = {}
    
    for test_run in range(num_tests):
        dungeon = DungeonMap(total_floors=15)
        
        # Count elites per floor
        for floor in range(15):
            if floor not in elite_counts_by_floor:
                elite_counts_by_floor[floor] = 0
                
            floor_nodes = dungeon.get_nodes_by_floor(floor)
            elite_count = sum(1 for node in floor_nodes if node.node_type == NodeType.ELITE)
            elite_counts_by_floor[floor] += elite_count
    
    # Calculate and display elite spawn rates
    print(f"\nElite spawn rates across {num_tests} dungeon generations:")
    print("Floor | Elite Count | Rate per Map | Expected Rate")
    print("-" * 50)
    
    for floor in range(15):
        total_elites = elite_counts_by_floor.get(floor, 0)
        rate_per_map = total_elites / num_tests
        
        if floor == 0:
            expected_rate = 0.0  # No elites on first floor
        elif floor == 14:
            expected_rate = 0.0  # Boss floor
        else:
            expected_rate = "varies"  # Depends on weight calculation
            
        print(f"{floor:5d} | {total_elites:11d} | {rate_per_map:12.2f} | {expected_rate}")
    
    # Test consecutive elite prevention
    print(f"\n=== Consecutive Elite Prevention Test ===")
    consecutive_found = 0
    
    for test_run in range(50):
        dungeon = DungeonMap(total_floors=15)
        
        # Track elite floors
        elite_floors = []
        for floor in range(15):
            floor_nodes = dungeon.get_nodes_by_floor(floor)
            if any(node.node_type == NodeType.ELITE for node in floor_nodes):
                elite_floors.append(floor)
        
        # Check for consecutive elites
        for i in range(len(elite_floors) - 1):
            if elite_floors[i+1] - elite_floors[i] <= 3:  # Within 3 floors
                consecutive_found += 1
                print(f"Consecutive elites found in test {test_run}: floors {elite_floors[i]} and {elite_floors[i+1]}")
                break
    
    print(f"\nConsecutive elite occurrences: {consecutive_found}/{50} tests")
    print(f"Prevention rate: {((50 - consecutive_found) / 50) * 100:.1f}%")

def test_single_map_layout():
    """Test a single map layout"""
    print(f"\n=== Single Map Layout Test ===")
    
    dungeon = DungeonMap(total_floors=15)
    
    for floor in range(15):
        nodes = dungeon.get_nodes_by_floor(floor)
        node_types = [node.node_type.value for node in nodes]
        elite_count = sum(1 for node in nodes if node.node_type == NodeType.ELITE)
        
        print(f"Floor {floor:2d}: {node_types} (Elites: {elite_count})")

if __name__ == "__main__":
    test_elite_spawn_rates()
    test_single_map_layout()