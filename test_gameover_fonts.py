#!/usr/bin/env python3
"""
ゲームオーバー画面の日本語表示テスト
文字化け修正の確認用
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

import pygame
pygame.init()

def test_gameover_fonts():
    print("=== TESTING GAME OVER SCREEN FONT ENCODING ===")
    
    try:
        from core.game_engine import GameEngine
        from game_completion.game_over_handler import GameOverHandler
        from core.constants import GameState
        
        print("1. Creating game engine...")
        engine = GameEngine()
        
        print("2. Testing game over handler creation...")
        game_over_handler = GameOverHandler(engine, death_cause="テストで敗北")
        
        print("3. Testing Japanese font rendering...")
        test_surface = pygame.Surface((1920, 1080))
        
        # Test Japanese text rendering
        japanese_texts = [
            "ゲームオーバー",
            "戦闘で力尽きた", 
            "冒険の記録",
            "到達フロア",
            "もう一度挑戦",
            "メインメニュー"
        ]
        
        from core.game_engine import get_appropriate_font
        
        for text in japanese_texts:
            try:
                font = get_appropriate_font(engine.fonts, text, 'medium')
                rendered = font.render(text, True, (255, 255, 255))
                if rendered and rendered.get_width() > 0:
                    print(f"   [OK] Successfully rendered: '{text}' (width: {rendered.get_width()})")
                else:
                    print(f"   [FAIL] Failed to render: '{text}' (no width)")
            except Exception as e:
                print(f"   [ERROR] Error rendering '{text}': {e}")
        
        print("4. Testing full game over screen render...")
        game_over_handler.render(test_surface)
        print("   SUCCESS: Game over screen rendered without errors")
        
        print("5. Testing statistics display...")
        stats = game_over_handler.stats
        print(f"   Statistics collected: {len(stats)} items")
        for key, value in list(stats.items())[:3]:  # Show first 3 stats
            print(f"   - {key}: {value}")
        
        return True
        
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_gameover_fonts()
    print(f"\nTest {'PASSED' if success else 'FAILED'}")
    sys.exit(0 if success else 1)