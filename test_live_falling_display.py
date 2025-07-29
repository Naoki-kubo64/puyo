#!/usr/bin/env python3
"""
リアルタイム落下中特殊ぷよアイコン表示テスト
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

import pygame
import logging
pygame.init()

from core.authentic_demo_handler import PuyoPair, AuthenticDemoHandler
from puzzle.puyo_grid import PuyoGrid, PuyoType
from core.game_engine import GameEngine
from core.simple_special_puyo import simple_special_manager, SimpleSpecialType

# ログを設定してアイコン描画だけに焦点を当てる
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 特殊ぷよ関連のログだけDEBUGレベルで表示
logging.getLogger('core.authentic_demo_handler').setLevel(logging.DEBUG)
logging.getLogger('core.simple_special_puyo').setLevel(logging.DEBUG)

def main():
    print("=== Live Falling Special Puyo Icon Display Test ===")
    
    # ゲームエンジンを初期化
    engine = GameEngine()
    handler = AuthenticDemoHandler(engine)
    
    print("Testing multiple pair generations to verify icon display...")
    
    # 複数のペアを生成してテスト
    for i in range(5):
        print(f"\n--- Test {i+1} ---")
        
        # 新しいペアを生成
        pair = PuyoPair(PuyoType.RED, PuyoType.BLUE, 3, None, None, handler)
        print(f"Generated pair: main_special={pair.main_special}, sub_special={pair.sub_special}")
        
        if pair.main_special or pair.sub_special:
            # 落下状態を設定
            pair.center_y = 5.0
            pair.active = True
            pair.grounded = False
            
            # テスト用サーフェス
            test_surface = pygame.Surface((400, 600))
            test_surface.fill((30, 30, 30))
            
            print(f"Testing falling render for pair {i+1}...")
            
            try:
                # 落下中の描画をテスト
                pair.render(test_surface, handler.puyo_grid)
                
                # アイコンが実際に描画されたかチェック
                icon_rendered = False
                if pair.main_special:
                    print(f"  Main special: {pair.main_special.value}")
                    icon_rendered = True
                if pair.sub_special:
                    print(f"  Sub special: {pair.sub_special.value}")
                    icon_rendered = True
                
                if icon_rendered:
                    # 画像を保存
                    filename = f"debug_falling_test_{i+1}.png"
                    pygame.image.save(test_surface, filename)
                    print(f"  Saved render to {filename}")
                
            except Exception as e:
                print(f"  ERROR: Rendering failed: {e}")
                import traceback
                traceback.print_exc()
        else:
            print(f"  No special puyos in pair {i+1}")
    
    print("\n=== Summary ===")
    print("Check the generated debug_falling_test_*.png files")
    print("Icons should be visible in the center of each puyo during falling state")
    
    pygame.quit()

if __name__ == "__main__":
    main()