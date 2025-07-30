#!/usr/bin/env python3
"""
NEXTぷよの特殊ぷよ表示をデバッグ
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

import pygame
pygame.init()

def debug_next_display():
    print("=== NEXT DISPLAY DEBUG ===")
    
    from core.authentic_demo_handler import AuthenticDemoHandler
    from core.simple_special_puyo import SimpleSpecialType, simple_special_manager
    
    # モックエンジン
    class MockEngine:
        def __init__(self):
            self.fonts = {'small': pygame.font.Font(None, 24)}
    
    handler = AuthenticDemoHandler(MockEngine())
    
    # 特殊ぷよ出現率を100%に設定してテスト
    simple_special_manager.spawn_rate = 1.0
    
    print("Testing NEXT queue with 100% special puyo spawn rate...")
    
    # NEXTキューを複数回生成してテスト
    for test_round in range(5):
        print(f"\n--- Test Round {test_round + 1} ---")
        handler._generate_initial_next_queue()
        
        for i, pair_info in enumerate(handler.next_pairs_queue):
            if len(pair_info) == 4:
                main_type, sub_type, main_special, sub_special = pair_info
                print(f"Pair {i+1}: {main_type.name}({main_special}) + {sub_type.name}({sub_special})")
            else:
                print(f"Pair {i+1}: Old format - {pair_info}")
        
        # ペアを1つ取得してキューの更新をテスト
        next_pair = handler._get_next_pair_colors()
        print(f"Retrieved: {next_pair[0].name}({next_pair[2]}) + {next_pair[1].name}({next_pair[3]})")
        
        # 更新後のキューを確認
        print("Updated queue:")
        for i, pair_info in enumerate(handler.next_pairs_queue):
            if len(pair_info) == 4:
                main_type, sub_type, main_special, sub_special = pair_info
                print(f"  Pair {i+1}: {main_type.name}({main_special}) + {sub_type.name}({sub_special})")

if __name__ == "__main__":
    debug_next_display()