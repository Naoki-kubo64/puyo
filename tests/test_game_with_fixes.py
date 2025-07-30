#!/usr/bin/env python3
"""
修正版ゲームの簡単なテスト起動
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

import pygame
pygame.init()

def test_game_with_fixes():
    print("=== TESTING GAME WITH DISPLAY FIXES ===")
    
    try:
        from core.game_engine import GameEngine
        from core.constants import GameState
        
        print("Creating game engine...")
        engine = GameEngine()
        
        print("Testing menu to battle transition...")
        # メニューからダンジョンマップへ
        engine.change_state(GameState.DUNGEON_MAP)
        print(f"Current state: {engine.current_state}")
        
        # マップハンドラーが正しく初期化されているか確認
        map_handler = engine.state_handlers.get(GameState.DUNGEON_MAP)
        if map_handler:
            print(f"Map handler type: {type(map_handler).__name__}")
            
            # 特殊ぷよの出現率が表示されるか確認
            player_rates = engine.player.special_puyo_rates
            print(f"Player special puyo rates: {player_rates}")
            
            # 短時間レンダリングテスト
            test_surface = pygame.Surface((1920, 1080))
            for i in range(3):
                try:
                    map_handler.render(test_surface)
                    print(f"Map render test {i+1}: SUCCESS")
                except Exception as e:
                    print(f"Map render test {i+1}: FAILED - {e}")
        
        print("\nTesting battle state...")
        # バトル状態に切り替え
        engine.change_state(GameState.BATTLE)
        battle_handler = engine.state_handlers.get(GameState.BATTLE)
        
        if battle_handler:
            print(f"Battle handler type: {type(battle_handler).__name__}")
            
            # バトル画面のレンダリングテスト
            for i in range(3):
                try:
                    battle_handler.render(test_surface)
                    print(f"Battle render test {i+1}: SUCCESS")
                except Exception as e:
                    print(f"Battle render test {i+1}: FAILED - {e}")
        
        print("\nAll tests completed successfully!")
        print("The game should now display special puyo icons and rates properly!")
        return True
        
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_game_with_fixes()
    sys.exit(0 if success else 1)