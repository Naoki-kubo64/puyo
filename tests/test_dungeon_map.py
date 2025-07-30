"""
ダンジョンマップシステムのテスト
"""

import pygame
import sys
import os
import logging

# パス設定
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from core.game_engine import GameEngine
from core.constants import GameState
from dungeon.map_handler import DungeonMapHandler

def test_dungeon_map():
    """ダンジョンマップシステムのテスト"""
    
    logging.basicConfig(level=logging.INFO)
    
    print("=== Dungeon Map System Test ===")
    
    # ゲームエンジン初期化
    engine = GameEngine()
    print("+ Game engine initialized")
    
    # ダンジョンマップハンドラー作成
    map_handler = DungeonMapHandler(engine)
    print("+ Map handler created")
    
    # ダンジョンマップ情報
    dungeon = map_handler.get_dungeon_map()
    print(f"+ Dungeon created: {dungeon.total_floors} floors, {len(dungeon.nodes)} nodes")
    
    # 各フロアの構成を表示
    print("\n=== Floor Structure ===")
    for floor in range(min(5, dungeon.total_floors)):
        nodes = dungeon.get_nodes_by_floor(floor)
        node_types = [n.node_type.value for n in nodes]
        print(f"Floor {floor + 1}: {node_types}")
    
    # 選択可能ノード
    available = dungeon.get_available_nodes()
    print(f"\n+ Available starting nodes: {len(available)}")
    for node in available:
        print(f"  - {node.node_id}: {node.node_type.value} at ({node.x}, {node.y})")
    
    # 接続テスト
    print(f"\n=== Connection Test ===")
    first_node = available[0] if available else None
    if first_node:
        print(f"First node connections: {first_node.connections}")
        
        # ノード選択をシミュレート
        success = dungeon.select_node(first_node.node_id)
        print(f"+ Node selection: {'Success' if success else 'Failed'}")
        
        # 次の選択可能ノード
        next_available = dungeon.get_available_nodes()
        print(f"+ Next available nodes: {len(next_available)}")
        for node in next_available:
            print(f"  - {node.node_id}: {node.node_type.value}")
    
    print("\n=== Test Completed Successfully ===")

if __name__ == "__main__":
    test_dungeon_map()