#!/usr/bin/env python3
"""
特殊ぷよ描画フローの完全分析（ASCII出力版）
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

import pygame
import logging
pygame.init()

# 詳細ログを有効化
logging.basicConfig(level=logging.DEBUG, format='%(levelname)s:%(name)s:%(message)s')

from core.authentic_demo_handler import PuyoPair, AuthenticDemoHandler
from puzzle.puyo_grid import PuyoGrid, PuyoType
from core.game_engine import GameEngine
from core.simple_special_puyo import simple_special_manager, SimpleSpecialType

def deep_analyze():
    print("=== DEEP ANALYSIS OF SPECIAL PUYO RENDER SYSTEM ===")
    
    # 初期化
    engine = GameEngine()
    handler = AuthenticDemoHandler(engine)
    simple_special_manager.spawn_rate = 1.0  # 100%確率
    
    print("\n### STEP 1: PAIR CREATION ###")
    pair = PuyoPair(PuyoType.RED, PuyoType.BLUE, 3, None, None, handler)
    
    print(f"Pair created:")
    print(f"  main_special: {pair.main_special}")
    print(f"  sub_special: {pair.sub_special}")
    print(f"  initial center_y: {pair.center_y}")
    print(f"  active: {pair.active}")
    
    if not pair.main_special and not pair.sub_special:
        print("NO SPECIAL PUYOS - CANNOT CONTINUE ANALYSIS")
        return
    
    print("\n### STEP 2: FALLING STATE TESTING ###")
    
    # 落下中の状態設定
    pair.center_y = 8.0
    pair.active = True
    pair.grounded = False
    
    main_pos, sub_pos = pair.get_positions()
    print(f"Falling positions: main={main_pos}, sub={sub_pos}")
    
    # 落下中の描画を詳細にテスト
    print("\n--- Testing falling render methods ---")
    
    # PuyoPair.render()が呼ばれる流れを追跡
    print("1. PuyoPair.render() called")
    print("2. PuyoPair._render_puyo_at() called for main and sub")
    print("3. _render_puyo_at() calls _render_falling_special_icon()")
    
    # 実際の描画テスト
    test_surface = pygame.Surface((400, 600))
    test_surface.fill((40, 40, 40))
    
    try:
        pair.render(test_surface, handler.puyo_grid)
        pygame.image.save(test_surface, 'debug_falling_analysis.png')
        print("SUCCESS: Falling render completed")
    except Exception as e:
        print(f"FAILED: Falling render error: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n### STEP 3: LANDING PROCESS ANALYSIS ###")
    
    # 着地プロセスをステップバイステップで実行
    print("Setting up landing conditions...")
    pair.center_y = 10.0
    pair.grounded = True
    pair.grounded_timer = 1.0
    
    main_pos_before, sub_pos_before = pair.get_positions()
    print(f"Positions before lock: main={main_pos_before}, sub={sub_pos_before}")
    
    # グリッドの特殊ぷよデータを事前確認
    print("Grid special data before lock:")
    print(f"  Count: {len(handler.puyo_grid.special_puyo_data)}")
    for pos, data in handler.puyo_grid.special_puyo_data.items():
        print(f"    {pos}: {data}")
    
    # 実際の固定処理を実行
    print("\nExecuting _execute_pair_lock()...")
    lock_result = pair._execute_pair_lock(handler.puyo_grid)
    print(f"Lock result: {lock_result}")
    
    # 固定後の状態確認
    print("\nPost-lock state:")
    print(f"  Pair active: {pair.active}")
    print(f"  Main fixed: {pair.main_fixed}")
    print(f"  Sub fixed: {pair.sub_fixed}")
    
    print("Grid special data after lock:")
    print(f"  Count: {len(handler.puyo_grid.special_puyo_data)}")
    for pos, data in handler.puyo_grid.special_puyo_data.items():
        print(f"    {pos}: {data}")
    
    print("\n### STEP 4: LANDED RENDER ANALYSIS ###")
    
    # 着地後の描画テスト
    test_surface2 = pygame.Surface((400, 600))
    test_surface2.fill((40, 40, 40))
    
    print("Testing landed render flow:")
    print("1. PuyoGrid.render() called")
    print("2. PuyoGrid._render_puyos() called")
    print("3. PuyoGrid._render_simple_special_icons() called")
    
    try:
        handler.puyo_grid.render(test_surface2)
        pygame.image.save(test_surface2, 'debug_landed_analysis.png')
        print("SUCCESS: Landed render completed")
    except Exception as e:
        print(f"FAILED: Landed render error: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n### STEP 5: CONSISTENCY CHECK ###")
    
    # 一貫性を詳細にチェック
    if pair.main_special:
        grid_main = handler.puyo_grid.get_special_puyo_data(main_pos_before[0], main_pos_before[1])
        print(f"Main consistency: Pair={pair.main_special} vs Grid={grid_main}")
        if grid_main != pair.main_special:
            print("  INCONSISTENCY DETECTED IN MAIN PUYO")
    
    if pair.sub_special:
        grid_sub = handler.puyo_grid.get_special_puyo_data(sub_pos_before[0], sub_pos_before[1])
        print(f"Sub consistency: Pair={pair.sub_special} vs Grid={grid_sub}")
        if grid_sub != pair.sub_special:
            print("  INCONSISTENCY DETECTED IN SUB PUYO")
    
    print("\n### STEP 6: RENDER METHOD INSPECTION ###")
    
    # 描画メソッドの詳細確認
    print("Checking render method implementations:")
    
    # PuyoPair._render_falling_special_icon の確認
    if hasattr(pair, '_render_falling_special_icon'):
        print("  PuyoPair._render_falling_special_icon: EXISTS")
    else:
        print("  PuyoPair._render_falling_special_icon: MISSING")
    
    # PuyoGrid._render_simple_special_icons の確認
    if hasattr(handler.puyo_grid, '_render_simple_special_icons'):
        print("  PuyoGrid._render_simple_special_icons: EXISTS")
    else:
        print("  PuyoGrid._render_simple_special_icons: MISSING")
    
    # 特殊ぷよ画像の確認
    if hasattr(handler.puyo_grid, 'special_puyo_images'):
        print(f"  PuyoGrid.special_puyo_images: {len(handler.puyo_grid.special_puyo_images)} loaded")
    else:
        print("  PuyoGrid.special_puyo_images: MISSING")
    
    print("\n=== ANALYSIS COMPLETE ===")
    print("Check debug_falling_analysis.png and debug_landed_analysis.png")
    
    pygame.quit()

if __name__ == "__main__":
    deep_analyze()