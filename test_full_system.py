#!/usr/bin/env python3

"""
システム全体の統合テスト
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

import pygame
import time
from core.game_engine import GameEngine
from core.player_data import PlayerData
from core.constants import GameState
from dungeon.dungeon_map import DungeonMap, NodeType
from shop.shop_handler import ShopHandler
from battle.battle_handler import BattleHandler

def test_full_system():
    """システム全体の統合テスト"""
    pygame.init()
    
    test_results = {
        'engine_initialization': False,
        'player_data': False,
        'dungeon_map': False,
        'shop_system': False,
        'battle_system': False,
        'special_puyo_system': False,
        'inventory_system': False,
        'ui_systems': False
    }
    
    try:
        print("=== Drop Puzzle × Roguelike - Full System Test ===")
        print()
        
        # 1. エンジン初期化テスト
        print("1. Testing Engine Initialization...")
        engine = GameEngine()
        player = PlayerData()
        player.gold = 300
        player.hp = 80
        player.max_hp = 100
        engine.player = player
        test_results['engine_initialization'] = True
        print("   [OK] Engine initialized successfully")
        
        # 2. プレイヤーデータテスト
        print("2. Testing Player Data System...")
        original_hp = player.hp
        player.heal(20)
        player.gain_gold(50)
        special_rate = player.increase_special_puyo_rate('heal', 0.1)
        test_results['player_data'] = (
            player.hp > original_hp and 
            player.gold == 350 and 
            special_rate > 0
        )
        print(f"   [OK] Player HP: {player.hp}/{player.max_hp}")
        print(f"   [OK] Player Gold: {player.gold}")
        print(f"   [OK] Special Puyo Rate: {special_rate*100:.0f}%")
        
        # 3. ダンジョンマップテスト
        print("3. Testing Dungeon Map System...")
        dungeon_map = DungeonMap(total_floors=5)
        engine.persistent_dungeon_map = dungeon_map
        
        # ノードタイプの分布を確認
        node_types = {}
        for node in dungeon_map.nodes.values():
            node_type = node.node_type.value
            node_types[node_type] = node_types.get(node_type, 0) + 1
        
        has_shop = 'shop' in node_types
        has_battle = 'battle' in node_types
        has_boss = 'boss' in node_types
        test_results['dungeon_map'] = has_battle and has_boss  # Shop is optional
        
        print(f"   [OK] Generated {len(dungeon_map.nodes)} nodes")
        print(f"   [OK] Node distribution: {node_types}")
        print(f"   [OK] Available nodes: {len(dungeon_map.get_available_nodes())}")
        
        # 4. ショップシステムテスト
        print("4. Testing Shop System...")
        shop_nodes = [n for n in dungeon_map.nodes.values() if n.node_type == NodeType.SHOP]
        if shop_nodes:
            shop_node = shop_nodes[0]
            shop_handler = ShopHandler(engine, current_node=shop_node)
            
            original_gold = player.gold
            if shop_handler.shop_items and original_gold >= shop_handler.shop_items[0].price:
                shop_handler.selected_index = 0
                shop_handler._attempt_purchase()
                
                purchase_success = (
                    player.gold < original_gold and
                    shop_handler.shop_items[0].sold
                )
                test_results['shop_system'] = purchase_success
                print(f"   [OK] Shop items: {len(shop_handler.shop_items)}")
                print(f"   [OK] Purchase test: {'Success' if purchase_success else 'Failed'}")
                print(f"   [OK] Gold after purchase: {player.gold}")
        else:
            # If no shop nodes, test shop creation manually
            try:
                test_shop_handler = ShopHandler(engine)
                test_results['shop_system'] = len(test_shop_handler.shop_items) > 0
                print(f"   [OK] Shop system working: {len(test_shop_handler.shop_items)} items generated")
            except Exception as e:
                print(f"   [ERROR] Shop system failed: {e}")
                test_results['shop_system'] = False
        
        # 5. バトルシステムテスト
        print("5. Testing Battle System...")
        try:
            battle_nodes = [n for n in dungeon_map.nodes.values() if n.node_type == NodeType.BATTLE]
            if battle_nodes:
                battle_node = battle_nodes[0]
                battle_handler = BattleHandler(engine, floor_level=1, current_node=battle_node)
                
                # バトルハンドラーの基本機能をテスト
                has_enemies = len(battle_handler.enemy_group.enemies) > 0
                has_ui = hasattr(battle_handler, 'top_ui_bar')
                has_puyo_grid = (hasattr(battle_handler, 'puzzle_handler') or 
                               hasattr(battle_handler, 'puyo_grid') or
                               hasattr(battle_handler, 'puyo_handler'))
                
                test_results['battle_system'] = has_enemies and has_ui and has_puyo_grid
                print(f"   [OK] Battle handler created with {len(battle_handler.enemy_group.enemies)} enemies")
                print(f"   [OK] UI components: {'Present' if has_ui else 'Missing'}")
                print(f"   [OK] Puyo grid: {'Present' if has_puyo_grid else 'Missing'}")
            else:
                print("   [WARN] No battle nodes found")
        except Exception as e:
            print(f"   [ERROR] Battle system error: {e}")
        
        # 6. 特殊ぷよシステムテスト
        print("6. Testing Special Puyo System...")
        from core.simple_special_puyo import SimpleSpecialType
        
        special_types = list(SimpleSpecialType)
        type_names = []
        descriptions = []
        for special_type in special_types:
            try:
                name = special_type.get_display_name()
                desc = special_type.get_description()
                type_names.append(name)
                descriptions.append(desc)
            except:
                pass
        
        test_results['special_puyo_system'] = (
            len(special_types) >= 6 and 
            len(type_names) >= 6 and 
            len(descriptions) >= 6
        )
        print(f"   [OK] Special puyo types: {len(special_types)}")
        print(f"   [OK] Named types: {len(type_names)}")
        print(f"   [OK] Sample names: {type_names[:3]}")
        
        # 7. インベントリシステムテスト
        print("7. Testing Inventory System...")
        from inventory.player_inventory import create_item
        
        original_items = len(player.inventory.items)
        test_item = create_item("health_potion_small", quantity=2)
        if test_item:
            item_added = player.inventory.add_item(test_item)
            new_items = len(player.inventory.items)
            
            test_results['inventory_system'] = item_added and (new_items >= original_items)
            print(f"   [OK] Items before: {original_items}")
            print(f"   [OK] Items after: {new_items}")
            print(f"   [OK] Item addition: {'Success' if item_added else 'Failed'}")
        else:
            print("   [ERROR] Failed to create test item")
        
        # 8. UIシステムテスト
        print("8. Testing UI Systems...")
        try:
            from core.top_ui_bar import TopUIBar
            from dungeon.map_renderer import MapRenderer
            
            # UI コンポーネントの作成テスト
            ui_bar = TopUIBar(engine.fonts)
            map_renderer = MapRenderer(dungeon_map)
            
            test_results['ui_systems'] = True
            print("   [OK] Top UI Bar: Created successfully")
            print("   [OK] Map Renderer: Created successfully")
            print("   [OK] Font system: Working")
        except Exception as e:
            print(f"   [ERROR] UI system error: {e}")
        
        # テスト結果の集計
        print()
        print("=== Test Results Summary ===")
        passed_tests = sum(test_results.values())
        total_tests = len(test_results)
        
        for test_name, result in test_results.items():
            status = "[PASS]" if result else "[FAIL]"
            print(f"{test_name.replace('_', ' ').title()}: {status}")
        
        print()
        print(f"Overall Result: {passed_tests}/{total_tests} tests passed")
        
        if passed_tests == total_tests:
            print("[SUCCESS] All systems are working correctly!")
            return True
        else:
            print("[WARNING] Some systems need attention.")
            return False
        
    except Exception as e:
        print(f"[CRITICAL ERROR] System test failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    finally:
        pygame.quit()

if __name__ == "__main__":
    success = test_full_system()
    exit(0 if success else 1)