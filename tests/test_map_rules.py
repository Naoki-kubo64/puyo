"""
ダンジョンマップ生成ルールの詳細テスト
"""

import sys
import os

# パス設定
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from src.dungeon.dungeon_map import DungeonMap, NodeType

def test_map_generation_rules():
    """マップ生成ルールの詳細テスト"""
    
    print("=== Dungeon Map Rules Test ===")
    
    # 複数回テストして傾向を確認
    for test_run in range(3):
        print(f"\n--- Test Run {test_run + 1} ---")
        
        dungeon = DungeonMap(total_floors=10)
        
        # ルール1: 1マス目は必ず戦闘
        floor_0_nodes = dungeon.get_nodes_by_floor(0)
        all_battle = all(node.node_type == NodeType.BATTLE for node in floor_0_nodes)
        print(f"Rule 1 - Floor 0 all battle: {'PASS' if all_battle else 'FAIL'}")
        if not all_battle:
            print(f"  Floor 0 types: {[n.node_type.value for n in floor_0_nodes]}")
        
        # ルール2: ランダムイベントは1マス目以外に出現
        has_events_floor_0 = any(node.node_type == NodeType.EVENT for node in floor_0_nodes)
        print(f"Rule 2 - No events on floor 0: {'PASS' if not has_events_floor_0 else 'FAIL'}")
        
        # ルール3: ショップ・休憩所は3マス目以降に出現
        early_special = False
        for floor in [0, 1]:
            nodes = dungeon.get_nodes_by_floor(floor)
            if any(node.node_type in [NodeType.SHOP, NodeType.REST] for node in nodes):
                early_special = True
                print(f"  Found special node on floor {floor}: {[n.node_type.value for n in nodes]}")
        
        print(f"Rule 3 - No shop/rest before floor 2: {'PASS' if not early_special else 'FAIL'}")
        
        # ルール4: ショップ・休憩所の連続配置チェック
        print("Rule 4 - Special node spacing:")
        special_positions = {}
        for floor in range(10):
            nodes = dungeon.get_nodes_by_floor(floor)
            for node in nodes:
                if node.node_type in [NodeType.SHOP, NodeType.REST]:
                    node_type = node.node_type.value
                    if node_type not in special_positions:
                        special_positions[node_type] = []
                    special_positions[node_type].append((floor, node.x))
        
        for node_type, positions in special_positions.items():
            print(f"  {node_type}: {positions}")
            
            # 連続配置チェック
            for i in range(len(positions) - 1):
                floor1, x1 = positions[i]
                floor2, x2 = positions[i + 1]
                
                if floor2 - floor1 <= 2:  # 2フロア以内
                    if floor2 - floor1 == 1:
                        # 隣接フロア：問題なし
                        continue
                    elif floor2 - floor1 == 2 and abs(x2 - x1) <= 2:
                        # 2フロア離れているが近すぎる
                        print(f"    WARNING: {node_type} too close at floors {floor1}-{floor2}, x-distance: {abs(x2-x1)}")
        
        # 各フロアの構成を表示
        print("\nFloor composition:")
        for floor in range(min(8, 10)):
            nodes = dungeon.get_nodes_by_floor(floor)
            node_types = [n.node_type.value for n in nodes]
            print(f"  Floor {floor}: {node_types}")

if __name__ == "__main__":
    test_map_generation_rules()