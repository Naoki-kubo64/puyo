#!/usr/bin/env python3
"""
実際のゲーム環境での特殊ぷよ一貫性テスト
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

import pygame
import logging
pygame.init()

from core.game_engine import GameEngine

def test_real_game():
    print("=== REAL GAME CONSISTENCY TEST ===")
    
    # ゲームエンジンを起動
    engine = GameEngine()
    
    # バトルテスト状態に直接移行
    from core.constants import GameState
    engine.change_state(GameState.REAL_BATTLE)
    
    print("Game initialized and moved to battle state")
    print("Test: Drop several pairs and observe icon consistency")
    print("Expected: Icons should remain same from falling to landed")
    print("Expected: No random icon changes after landing")
    
    # 短時間ゲームループを実行
    clock = pygame.time.Clock()
    
    for i in range(180):  # 3秒間実行
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                break
            engine.handle_event(event)
        
        dt = clock.tick(60) / 1000.0
        engine.update(dt)
        engine.render()
        
        if i == 60:  # 1秒後
            print("1 second passed - observing consistency...")
        elif i == 120:  # 2秒後
            print("2 seconds passed - still consistent?")
    
    print("Real game test completed")
    print("Check visually if special puyo icons remained consistent")
    
    pygame.quit()

if __name__ == "__main__":
    test_real_game()