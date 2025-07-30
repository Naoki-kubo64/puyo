#!/usr/bin/env python3
"""
カウントダウンシステムのテスト
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

import pygame
pygame.init()

def test_countdown_system():
    print("=== COUNTDOWN SYSTEM TEST ===")
    
    try:
        from battle.battle_handler import BattleHandler
        from core.game_engine import GameEngine
        
        # モックエンジン作成
        class MockEngine:
            def __init__(self):
                self.player = MockPlayer()
                self.fonts = {
                    'small': pygame.font.Font(None, 24),
                    'medium': pygame.font.Font(None, 36),
                    'large': pygame.font.Font(None, 48)
                }
        
        class MockPlayer:
            def __init__(self):
                self.hp = 100
                self.max_hp = 100
                self.gold = 0
        
        print("Creating mock engine...")
        mock_engine = MockEngine()
        
        print("Creating battle handler...")
        battle_handler = BattleHandler(mock_engine, floor_level=1)
        
        print("Testing countdown initialization...")
        print(f"  countdown_active: {battle_handler.countdown_active}")
        print(f"  countdown_timer: {battle_handler.countdown_timer}")
        
        print("Testing countdown update...")
        # 0.5秒経過をシミュレート
        battle_handler.update(0.5)
        print(f"  After 0.5s - countdown_timer: {battle_handler.countdown_timer}")
        print(f"  countdown_active: {battle_handler.countdown_active}")
        
        # さらに3秒経過
        battle_handler.update(3.0)
        print(f"  After additional 3.0s - countdown_timer: {battle_handler.countdown_timer}")
        print(f"  countdown_active: {battle_handler.countdown_active}")
        
        print("Testing render method...")
        test_surface = pygame.Surface((1920, 1080))
        
        # カウントダウン中の描画テスト
        battle_handler.countdown_active = True
        battle_handler.countdown_timer = 2.5
        battle_handler.render(test_surface)
        print("  Countdown render test passed")
        
        print("SUCCESS: Countdown system test completed!")
        return True
        
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_countdown_system()
    sys.exit(0 if success else 1)