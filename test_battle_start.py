#!/usr/bin/env python3
"""
バトル開始の詳細テスト
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

import pygame
pygame.init()
pygame.display.set_mode((1920, 1080))

def test_battle_start():
    print("=== BATTLE START DETAILED TEST ===")
    
    try:
        from core.game_engine import GameEngine
        from core.player_data import PlayerData
        from battle.battle_handler import BattleHandler
        
        print("Creating game engine...")
        engine = GameEngine()
        
        print("Creating battle handler...")
        battle_handler = BattleHandler(engine, floor_level=1)
        
        print("Testing battle handler initialization...")
        print(f"  countdown_active: {battle_handler.countdown_active}")
        print(f"  countdown_timer: {battle_handler.countdown_timer}")
        print(f"  battle_active: {battle_handler.battle_active}")
        print(f"  player stats available: {hasattr(battle_handler.player, 'stats')}")
        
        print("Testing battle handler update (countdown phase)...")
        battle_handler.update(0.1)
        print(f"  After 0.1s - countdown_timer: {battle_handler.countdown_timer}")
        
        print("Testing battle handler render (countdown phase)...")
        test_surface = pygame.Surface((1920, 1080))
        battle_handler.render(test_surface)
        print("  Countdown render successful")
        
        print("Testing battle handler update (post-countdown)...")
        # カウントダウン終了まで進める
        battle_handler.update(3.0)
        print(f"  After countdown - countdown_active: {battle_handler.countdown_active}")
        
        print("Testing battle handler render (post-countdown)...")
        battle_handler.render(test_surface)
        print("  Post-countdown render successful")
        
        print("Testing event handling...")
        # キー入力イベントをテスト
        test_event = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_SPACE)
        battle_handler.puyo_handler.handle_event(test_event)
        print("  Event handling successful")
        
        print("SUCCESS: All battle start tests passed!")
        return True
        
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_battle_start()
    sys.exit(0 if success else 1)