#!/usr/bin/env python3

"""
ゲーム内ショップ統合テスト
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

import pygame
from core.game_engine import GameEngine
from core.player_data import PlayerData
from core.constants import GameState
from dungeon.dungeon_map import DungeonMap, NodeType
from dungeon.map_handler import DungeonMapHandler

def test_shop_integration():
    """ゲーム内ショップの統合テスト"""
    pygame.init()
    
    try:
        # エンジンとプレイヤーを初期化
        engine = GameEngine()
        player = PlayerData()
        player.gold = 200  # テスト用に十分なゴールドを設定
        engine.player = player
        
        print("Testing shop integration in game...")
        
        # ダンジョンマップを作成
        dungeon_map = DungeonMap(total_floors=5)
        engine.persistent_dungeon_map = dungeon_map
        
        # ショップノードを探す
        shop_nodes = []
        for node in dungeon_map.nodes.values():
            if node.node_type == NodeType.SHOP:
                shop_nodes.append(node)
        
        print(f"Found {len(shop_nodes)} shop nodes in the dungeon")
        
        if shop_nodes:
            # 最初のショップノードを選択
            shop_node = shop_nodes[0]
            print(f"Testing shop node: {shop_node.node_id} on floor {shop_node.floor}")
            
            # マップハンドラーを作成
            map_handler = DungeonMapHandler(engine, dungeon_map)
            
            # ショップノードを利用可能にする（テスト用）
            shop_node.available = True
            
            # ショップノードの処理をシミュレート
            print("Simulating shop node selection...")
            try:
                map_handler._transition_to_shop(shop_node)
                print("Shop transition initiated successfully!")
                
                # 現在の状態を確認
                if hasattr(engine, 'current_state_handler') and engine.current_state_handler:
                    print(f"Current state handler: {type(engine.current_state_handler).__name__}")
                else:
                    print("No current state handler set")
                
                # ショップハンドラーを直接テスト
                from shop.shop_handler import ShopHandler
                shop_handler = ShopHandler(engine, current_node=shop_node)
                
                print(f"Shop handler created with {len(shop_handler.shop_items)} items")
                print(f"Player gold before shopping: {shop_handler.player_gold}")
                
                # 最初のアイテムの購入をシミュレート
                if shop_handler.shop_items:
                    first_item = shop_handler.shop_items[0]
                    print(f"Testing purchase of: {first_item.get_name()} for {first_item.price}G")
                    
                    if shop_handler.player_gold >= first_item.price:
                        shop_handler.selected_index = 0
                        shop_handler._attempt_purchase()
                        
                        print(f"Purchase completed!")
                        print(f"Gold after purchase: {shop_handler.player_gold}")
                        print(f"Item sold status: {first_item.sold}")
                        
                        # プレイヤーデータが更新されているか確認
                        print(f"Engine player gold: {engine.player.gold}")
                    else:
                        print("Not enough gold for purchase test")
                
            except Exception as e:
                print(f"Error during shop transition: {e}")
                import traceback
                traceback.print_exc()
        else:
            print("No shop nodes found in dungeon map")
        
        print("Shop integration test completed!")
        
    except Exception as e:
        print(f"Error during shop integration test: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        pygame.quit()

if __name__ == "__main__":
    test_shop_integration()