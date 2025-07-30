#!/usr/bin/env python3
"""
ゲーム開始直後の回転問題をデバッグ
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

import pygame
import logging
pygame.init()

# デバッグレベルを設定
logging.basicConfig(level=logging.DEBUG)

def debug_rotation_startup():
    print("=== ROTATION STARTUP DEBUG ===")
    
    from core.authentic_demo_handler import AuthenticDemoHandler, PuyoPair
    from core.constants import PuyoType, GRID_WIDTH
    from puzzle.puyo_grid import PuyoGrid
    
    # モックエンジン
    class MockEngine:
        def __init__(self):
            self.fonts = {'small': pygame.font.Font(None, 24)}
    
    mock_engine = MockEngine()
    handler = AuthenticDemoHandler(mock_engine)
    
    print(f"Handler initialized. Current pair: {handler.current_pair}")
    print(f"Game active: {handler.game_active}")
    
    # 新しいペアをスポーン
    print("\n--- Spawning new pair ---")
    handler._spawn_new_pair()
    
    if handler.current_pair:
        pair = handler.current_pair
        print(f"Pair spawned successfully!")
        print(f"  Active: {pair.active}")
        print(f"  Position: ({pair.center_x}, {pair.center_y})")
        print(f"  Rotation: {pair.rotation}")
        print(f"  Main type: {pair.main_type}")
        print(f"  Sub type: {pair.sub_type}")
        print(f"  Separated: {getattr(pair, 'separated', 'N/A')}")
        
        # 回転テスト
        print(f"\n--- Testing rotation ---")
        
        # 回転前の状態
        print(f"Before rotation: rotation={pair.rotation}")
        can_place_before = pair.can_place_at(handler.puyo_grid, pair.center_x, pair.center_y, pair.rotation)
        print(f"Can place at current position: {can_place_before}")
        
        # チェイン状態の確認
        chain_active = getattr(handler.puyo_grid, 'chain_animation_active', False)
        print(f"Chain animation active: {chain_active}")
        
        # 時計回りの回転を試行
        print(f"Attempting clockwise rotation...")
        success = pair.try_rotate(True, handler.puyo_grid)
        print(f"Rotation result: {success}")
        print(f"After rotation: rotation={pair.rotation}")
        
        if not success:
            print("Rotation failed. Checking reasons:")
            
            # 各回転状態での配置可能性をチェック
            for test_rotation in range(4):
                can_place = pair.can_place_at(handler.puyo_grid, pair.center_x, pair.center_y, test_rotation)
                print(f"  Rotation {test_rotation}: can_place = {can_place}")
                
                if not can_place:
                    # 詳細な衝突チェック
                    offsets = [(0, -1), (1, 0), (0, 1), (-1, 0)]
                    offset_x, offset_y = offsets[test_rotation]
                    main_x, main_y = int(pair.center_x), int(pair.center_y)
                    sub_x, sub_y = main_x + offset_x, main_y + offset_y
                    
                    print(f"    Main puyo at ({main_x}, {main_y})")
                    print(f"    Sub puyo at ({sub_x}, {sub_y})")
                    
                    # 境界チェック
                    if main_x < 0 or main_x >= GRID_WIDTH or main_y >= 12:
                        print(f"    Main puyo out of bounds")
                    if sub_x < 0 or sub_x >= GRID_WIDTH or sub_y >= 12:
                        print(f"    Sub puyo out of bounds")
                    
                    # グリッド衝突チェック
                    if main_y >= 0:
                        main_blocked = not handler.puyo_grid.can_place_puyo(main_x, main_y)
                        print(f"    Main puyo blocked by grid: {main_blocked}")
                    if sub_y >= 0:
                        sub_blocked = not handler.puyo_grid.can_place_puyo(sub_x, sub_y)
                        print(f"    Sub puyo blocked by grid: {sub_blocked}")
        
        # 別の回転方向も試行
        print(f"\nAttempting counter-clockwise rotation...")
        success2 = pair.try_rotate(False, handler.puyo_grid)
        print(f"Counter-clockwise rotation result: {success2}")
        print(f"Final rotation: {pair.rotation}")
        
    else:
        print("Failed to spawn pair!")
        
    print("\nRotation startup debug completed!")

if __name__ == "__main__":
    debug_rotation_startup()