#!/usr/bin/env python3

"""
ショップ機能のテスト
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

import pygame
from core.game_engine import GameEngine
from core.player_data import PlayerData
from shop.shop_handler import ShopHandler

def test_shop_functionality():
    """ショップ機能の基本動作をテスト"""
    pygame.init()
    
    try:
        # エンジンとプレイヤーを初期化
        engine = GameEngine()
        player = PlayerData()
        player.gold = 100  # テスト用にゴールドを設定
        engine.player = player
        
        print("Testing shop functionality...")
        
        # ショップハンドラーを作成
        shop_handler = ShopHandler(engine)
        
        print(f"Shop initialized with {len(shop_handler.shop_items)} items")
        print(f"Player gold: {shop_handler.player_gold}")
        
        # ショップアイテムの詳細を表示
        for i, shop_item in enumerate(shop_handler.shop_items):
            print(f"Item {i+1}: {shop_item.get_name()} - {shop_item.price}G")
            print(f"  Description: {shop_item.get_description()}")
            print(f"  Type: {shop_item.item_type}")
            print(f"  Icon: {shop_item.get_icon()}")
            print()
        
        # 購入テスト
        if shop_handler.shop_items:
            print("Testing purchase...")
            first_item = shop_handler.shop_items[0]
            original_gold = shop_handler.player_gold
            
            if original_gold >= first_item.price:
                shop_handler.selected_index = 0
                shop_handler._attempt_purchase()
                
                print(f"Purchase result:")
                print(f"  Gold before: {original_gold}")
                print(f"  Gold after: {shop_handler.player_gold}")
                print(f"  Item sold: {first_item.sold}")
                print(f"  Last purchased: {shop_handler.last_purchased_item.get_name() if shop_handler.last_purchased_item else 'None'}")
            else:
                print("Not enough gold to test purchase")
        
        print("Shop functionality test completed successfully!")
        
    except Exception as e:
        print(f"Error during shop test: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        pygame.quit()

if __name__ == "__main__":
    test_shop_functionality()