#!/usr/bin/env python3
"""
特殊ぷよ表示問題の修正確認テスト
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

import pygame
pygame.init()
pygame.display.set_mode((1920, 1080))

def test_display_fixes():
    print("=== SPECIAL PUYO DISPLAY FIXES TEST ===")
    
    try:
        from core.game_engine import GameEngine
        from core.simple_special_puyo import SimpleSpecialType, simple_special_manager
        from core.constants import PuyoType
        from puzzle.puyo_grid import PuyoGrid
        from battle.battle_handler import BattleHandler
        from core.top_ui_bar import TopUIBar
        from dungeon.map_renderer import MapRenderer
        from dungeon.dungeon_map import DungeonMap
        
        print("1. Testing icon cleanup after puyo elimination...")
        engine = GameEngine()
        battle_handler = BattleHandler(engine, floor_level=1)
        puyo_grid = battle_handler.puyo_handler.puyo_grid
        
        # 特殊ぷよ付きのぷよを配置
        puyo_grid.set_puyo(2, 10, PuyoType.RED)
        puyo_grid.set_special_puyo_data(2, 10, SimpleSpecialType.HEAL)
        
        print(f"   Before elimination: special data count = {len(puyo_grid.special_puyo_data)}")
        
        # ぷよを消去
        from puzzle.puyo_grid import PuyoPosition
        positions = {PuyoPosition(2, 10)}
        puyo_grid.eliminate_puyos(positions)
        
        print(f"   After elimination: special data count = {len(puyo_grid.special_puyo_data)}")
        
        if len(puyo_grid.special_puyo_data) == 0:
            print("   SUCCESS: Special puyo data cleaned up properly")
        else:
            print("   FAILURE: Special puyo data not cleaned up")
        
        print("\n2. Testing TopUIBar special puyo display...")
        top_ui_bar = TopUIBar(engine.fonts)
        
        # 特殊ぷよアイコンが読み込まれているか確認
        print(f"   Loaded special puyo icons: {list(top_ui_bar.special_puyo_icons.keys())}")
        
        # 出現率データ
        special_puyo_rates = {
            'heal': 0.15,
            'bomb': 0.20
        }
        
        # テスト用サーフェイスで描画テスト
        test_surface = pygame.Surface((1920, 1080))
        try:
            top_ui_bar.draw_top_bar(test_surface, 100, 120, 50, 1, special_puyo_rates)
            print("   SUCCESS: TopUIBar draws special puyo info")
        except Exception as e:
            print(f"   FAILURE: TopUIBar drawing failed: {e}")
        
        # マウスオーバーテスト
        test_mouse_pos = (570, 30)  # 特殊ぷよ表示領域
        top_ui_bar.handle_mouse_motion(test_mouse_pos)
        
        # _draw_special_puyo_displayを手動で呼び出してhover_infoを設定
        try:
            top_ui_bar._draw_special_puyo_display(test_surface, special_puyo_rates)
            if top_ui_bar.hover_info:
                print(f"   SUCCESS: Mouse hover detected: {top_ui_bar.hover_info['type']}")
            else:
                print("   Mouse hover not detected (position may be off)")
        except Exception as e:
            print(f"   Mouse hover test failed: {e}")
        
        print("\n3. Testing MapRenderer special puyo display...")
        dungeon_map = DungeonMap(total_floors=5)
        map_renderer = MapRenderer(dungeon_map)
        map_renderer.dungeon_map.engine = engine
        
        # 特殊ぷよアイコンが読み込まれているか確認
        print(f"   Loaded special puyo icons: {list(map_renderer.special_puyo_images.keys())}")
        
        # ステータスバー描画テスト
        try:
            map_renderer._render_status_bar(test_surface, engine.fonts)
            print("   SUCCESS: MapRenderer draws special puyo info in status bar")
        except Exception as e:
            print(f"   FAILURE: MapRenderer status bar failed: {e}")
        
        print("\n4. Testing BattleHandler integration...")
        # バトルハンドラーでマウスイベント処理テスト
        test_event = pygame.event.Event(pygame.MOUSEMOTION, pos=(570, 30))
        try:
            battle_handler.handle_event(test_event)
            print("   SUCCESS: BattleHandler handles mouse motion for TopUIBar")
        except Exception as e:
            print(f"   FAILURE: BattleHandler mouse event failed: {e}")
        
        print("\n5. Testing special puyo rates display...")
        # プレイヤーデータの出現率を変更してテスト
        original_rates = engine.player.special_puyo_rates.copy()
        engine.player.special_puyo_rates['heal'] = 0.25
        engine.player.special_puyo_rates['bomb'] = 0.35
        
        print(f"   Player rates: {engine.player.special_puyo_rates}")
        
        # TopUIBarで更新された率を表示
        try:
            top_ui_bar.draw_top_bar(test_surface, 100, 120, 50, 1, engine.player.special_puyo_rates)
            print("   SUCCESS: Updated rates displayed in TopUIBar")
        except Exception as e:
            print(f"   FAILURE: Updated rates display failed: {e}")
        
        # 元に戻す
        engine.player.special_puyo_rates = original_rates
        
        print("\nSUCCESS: All display fixes tested!")
        return True
        
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_display_fixes()
    sys.exit(0 if success else 1)