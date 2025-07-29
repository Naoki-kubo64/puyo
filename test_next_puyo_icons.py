#!/usr/bin/env python3
"""
NEXTぷよ特殊ぷよアイコン表示テスト
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

import pygame
pygame.init()

def test_next_puyo_icons():
    print("=== NEXT PUYO SPECIAL ICONS TEST ===")
    
    # authentic_demo_handlerをインポート
    from core.authentic_demo_handler import AuthenticDemoHandler
    from core.simple_special_puyo import SimpleSpecialType, simple_special_manager
    
    # モックエンジンを作成
    class MockEngine:
        def __init__(self):
            pass
    
    # ハンドラー作成
    mock_engine = MockEngine()
    handler = AuthenticDemoHandler(mock_engine)
    
    print("Testing NEXT queue generation with special puyo info...")
    
    # NEXTキューを生成
    handler._generate_initial_next_queue()
    
    print(f"Generated NEXT queue length: {len(handler.next_pairs_queue)}")
    
    for i, (main_type, sub_type, main_special, sub_special) in enumerate(handler.next_pairs_queue):
        print(f"NEXT Pair {i+1}:")
        print(f"  Main: {main_type.name} - Special: {main_special}")
        print(f"  Sub: {sub_type.name} - Special: {sub_special}")
        
        # 特殊ぷよタイプの確認
        if main_special:
            print(f"  Main special type: {type(main_special)} = {main_special}")
        if sub_special:
            print(f"  Sub special type: {type(sub_special)} = {sub_special}")
    
    print("\nTesting next pair retrieval...")
    
    # NEXTペアを取得
    next_pair = handler._get_next_pair_colors()
    main_type, sub_type, main_special, sub_special = next_pair
    
    print(f"Retrieved pair:")
    print(f"  Main: {main_type.name} - Special: {main_special}")
    print(f"  Sub: {sub_type.name} - Special: {sub_special}")
    
    print("\nUpdated NEXT queue after retrieval:")
    for i, (main_type, sub_type, main_special, sub_special) in enumerate(handler.next_pairs_queue):
        print(f"NEXT Pair {i+1}:")
        print(f"  Main: {main_type.name} - Special: {main_special}")
        print(f"  Sub: {sub_type.name} - Special: {sub_special}")
    
    print("\nTesting special type detection...")
    print(f"SimpleSpecialType.HEAL: {SimpleSpecialType.HEAL}")
    print(f"SimpleSpecialType.BOMB: {SimpleSpecialType.BOMB}")
    
    # 実際のSpecialTypeを確認
    for special_type in [SimpleSpecialType.HEAL, SimpleSpecialType.BOMB]:
        print(f"Testing render method for {special_type}...")
        
        # テスト用サーフェス作成
        test_surface = pygame.Surface((100, 100))
        
        try:
            handler._render_next_special_puyo(test_surface, (50, 50), special_type, 40)
            print(f"  SUCCESS: Rendered {special_type}")
        except Exception as e:
            print(f"  ERROR: Failed to render {special_type}: {e}")
    
    print("\nNEXT puyo special icons test completed!")

if __name__ == "__main__":
    test_next_puyo_icons()