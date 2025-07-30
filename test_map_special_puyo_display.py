#!/usr/bin/env python3
"""
マップ画面の特殊ぷよ表示テスト
バトル画面との仕様統一確認用
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

import pygame
pygame.init()

def test_map_special_puyo_display():
    print("=== TESTING MAP SCREEN SPECIAL PUYO DISPLAY ===")
    
    try:
        from core.game_engine import GameEngine
        from dungeon.map_handler import DungeonMapHandler
        from dungeon.dungeon_map import DungeonMap
        from dungeon.map_renderer import MapRenderer
        
        print("1. Creating game engine...")
        engine = GameEngine()
        
        print("2. Testing map renderer special puyo loading...")
        dungeon_map = DungeonMap(total_floors=5)
        dungeon_map.engine = engine  # エンジン参照を設定
        renderer = MapRenderer(dungeon_map)
        
        # 特殊ぷよ画像の読み込み確認
        loaded_images = list(renderer.special_puyo_images.keys())
        print(f"   Loaded special puyo images: {loaded_images}")
        
        expected_types = ["heal", "bomb", "lightning", "shield", "multiplier", "poison"]
        missing_types = [t for t in expected_types if t not in loaded_images]
        if missing_types:
            print(f"   [WARNING] Missing special puyo images: {missing_types}")
        else:
            print("   [OK] All expected special puyo types loaded")
        
        print("3. Testing initial state (no special puyos)...")
        # 初期状態：すべて0%のはず
        special_puyo_rates = engine.player.special_puyo_rates
        print(f"   Initial special puyo rates: {special_puyo_rates}")
        
        non_zero_rates = {k: v for k, v in special_puyo_rates.items() if v > 0.0}
        if non_zero_rates:
            print(f"   [UNEXPECTED] Non-zero rates found: {non_zero_rates}")
        else:
            print("   [OK] All rates are 0% as expected")
        
        print("4. Testing map status bar render...")
        test_surface = pygame.Surface((1920, 1080))
        renderer._render_status_bar(test_surface, engine.fonts)
        print("   [OK] Status bar rendered without errors")
        
        print("5. Testing with simulated special puyo acquisition...")
        # 特殊ぷよを取得したシミュレーション
        engine.player.special_puyo_rates['heal'] = 0.3  # 30%
        engine.player.special_puyo_rates['bomb'] = 0.2   # 20%
        # lightning, shield, multiplier, poison は 0% のまま
        
        print(f"   Modified rates: {engine.player.special_puyo_rates}")
        
        # 再描画してテスト
        renderer._render_status_bar(test_surface, engine.fonts)
        print("   [OK] Status bar with special puyos rendered")
        
        # 表示されるべき特殊ぷよをカウント
        displayed_count = sum(1 for rate in engine.player.special_puyo_rates.values() if rate > 0.0)
        print(f"   Expected displayed special puyos: {displayed_count}")
        
        # 各特殊ぷよの表示状態を確認
        for puyo_type, rate in engine.player.special_puyo_rates.items():
            status = "DISPLAY" if rate > 0.0 else "HIDDEN"
            print(f"   - {puyo_type}: {rate*100:.0f}% [{status}]")
        
        print("6. Testing consistency with battle screen...")
        from core.top_ui_bar import TopUIBar
        
        # バトル画面のUIBarと同じロジックかテスト
        top_ui_bar = TopUIBar(engine.fonts)
        battle_surface = pygame.Surface((1920, 1080))
        
        # バトル画面での描画をテスト
        top_ui_bar.draw_top_bar(
            battle_surface,
            engine.player.hp, engine.player.max_hp,
            engine.player.gold,
            1,  # floor
            engine.player.special_puyo_rates,
            engine.player.inventory
        )
        print("   [OK] Battle screen UI rendered for comparison")
        
        return True
        
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_map_special_puyo_display()
    print(f"\nTest {'PASSED' if success else 'FAILED'}")
    sys.exit(0 if success else 1)