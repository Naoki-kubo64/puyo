#!/usr/bin/env python3
"""
特殊ぷよ描画フローの完全分析
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

import pygame
import logging
pygame.init()

# ログレベルをDEBUGに設定して詳細を確認
logging.basicConfig(level=logging.DEBUG)

from core.authentic_demo_handler import PuyoPair, AuthenticDemoHandler
from puzzle.puyo_grid import PuyoGrid, PuyoType
from core.game_engine import GameEngine
from core.simple_special_puyo import simple_special_manager, SimpleSpecialType

def analyze_render_flow():
    print("=== COMPLETE RENDER FLOW ANALYSIS ===")
    
    # ゲームエンジンを初期化
    engine = GameEngine()
    handler = AuthenticDemoHandler(engine)
    
    # 出現率を100%に設定
    simple_special_manager.spawn_rate = 1.0
    
    print("\n1. PAIR CREATION ANALYSIS")
    print("-" * 40)
    
    # 特殊ぷよペアを作成
    pair = PuyoPair(PuyoType.RED, PuyoType.BLUE, 3, None, None, handler)
    
    print(f"Created pair:")
    print(f"  main_type: {pair.main_type}")
    print(f"  sub_type: {pair.sub_type}")
    print(f"  main_special: {pair.main_special}")
    print(f"  sub_special: {pair.sub_special}")
    print(f"  center_x: {pair.center_x}")
    print(f"  center_y: {pair.center_y}")
    print(f"  active: {pair.active}")
    print(f"  grounded: {pair.grounded}")
    
    print("\n2. FALLING STATE ANALYSIS")
    print("-" * 40)
    
    # 落下状態を設定
    pair.center_y = 8.0
    pair.active = True
    pair.grounded = False
    
    main_pos, sub_pos = pair.get_positions()
    print(f"Falling positions: main={main_pos}, sub={sub_pos}")
    
    # 落下中描画テスト
    test_surface = pygame.Surface((600, 800))
    test_surface.fill((30, 30, 30))
    
    print("\n3. FALLING RENDER TEST")
    print("-" * 40)
    
    try:
        pair.render(test_surface, handler.puyo_grid)
        pygame.image.save(test_surface, 'debug_falling_detailed.png')
        print("✓ Falling render completed - saved to debug_falling_detailed.png")
    except Exception as e:
        print(f"✗ Falling render failed: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n4. LANDING SIMULATION")
    print("-" * 40)
    
    # 着地状態に変更
    pair.center_y = 10.0
    pair.grounded = True
    pair.grounded_timer = 1.0  # 十分な時間
    
    # 固定処理を実行
    print("Executing lock process...")
    lock_result = pair._execute_pair_lock(handler.puyo_grid)
    print(f"Lock result: {lock_result}")
    
    print("\n5. POST-LOCK STATE ANALYSIS")
    print("-" * 40)
    
    # 固定後の状態確認
    main_pos_after, sub_pos_after = pair.get_positions()
    print(f"Positions after lock: main={main_pos_after}, sub={sub_pos_after}")
    print(f"Pair active: {pair.active}")
    print(f"Main fixed: {pair.main_fixed}")
    print(f"Sub fixed: {pair.sub_fixed}")
    
    # グリッドの特殊ぷよデータ確認
    print("\nGrid special puyo data:")
    for (x, y), special_type in handler.puyo_grid.special_puyo_data.items():
        print(f"  ({x}, {y}): {special_type}")
    
    print("\n6. LANDED RENDER TEST")
    print("-" * 40)
    
    test_surface2 = pygame.Surface((600, 800))
    test_surface2.fill((30, 30, 30))
    
    try:
        handler.puyo_grid.render(test_surface2)
        pygame.image.save(test_surface2, 'debug_landed_detailed.png')
        print("✓ Landed render completed - saved to debug_landed_detailed.png")
    except Exception as e:
        print("✗ Landed render failed: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n7. RENDER METHOD ANALYSIS")
    print("-" * 40)
    
    print("Analyzing PuyoPair.render() method:")
    print(f"  _render_puyo_at calls _render_falling_special_icon: {hasattr(pair, '_render_falling_special_icon')}")
    print(f"  PuyoGrid has special_puyo_data: {hasattr(handler.puyo_grid, 'special_puyo_data')}")
    print(f"  PuyoGrid has _render_simple_special_icons: {hasattr(handler.puyo_grid, '_render_simple_special_icons')}")
    
    print("\n8. NEXT PAIR ANALYSIS")
    print("-" * 40)
    
    # NEXTペアを生成
    print("Creating another pair to test NEXT functionality...")
    next_pair = PuyoPair(PuyoType.GREEN, PuyoType.YELLOW, 3, None, None, handler)
    print(f"Next pair specials: main={next_pair.main_special}, sub={next_pair.sub_special}")
    
    print("\n=== ANALYSIS COMPLETE ===")
    
    pygame.quit()

if __name__ == "__main__":
    analyze_render_flow()