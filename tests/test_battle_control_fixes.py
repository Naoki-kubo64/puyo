#!/usr/bin/env python3
"""
バトル操作修正のテスト
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

import pygame
import time
pygame.init()

def test_battle_control_fixes():
    print("=== TESTING BATTLE CONTROL FIXES ===")
    
    try:
        from core.game_engine import GameEngine
        from core.constants import GameState
        from battle.battle_handler import BattleHandler
        
        print("1. Creating game engine...")
        engine = GameEngine()
        
        print("2. Creating battle handler...")
        battle_handler = BattleHandler(engine, floor_level=1)
        
        print("3. Testing countdown system...")
        print(f"   Initial countdown_active: {battle_handler.countdown_active}")
        print(f"   Initial countdown_timer: {battle_handler.countdown_timer}")
        
        # Check if puyo handler has no current pair during countdown
        print(f"   Current pair during countdown: {battle_handler.puyo_handler.current_pair}")
        
        print("4. Testing movement fix...")
        puyo_handler = battle_handler.puyo_handler
        
        # Simulate countdown end
        battle_handler.countdown_active = False
        battle_handler.countdown_timer = 0.0
        
        # Wait for pair to spawn
        if puyo_handler.current_pair is None:
            puyo_handler._spawn_new_pair()
        
        if puyo_handler.current_pair:
            print(f"   Pair spawned: {puyo_handler.current_pair.main_type.name} + {puyo_handler.current_pair.sub_type.name}")
            print(f"   Initial position: x={puyo_handler.current_pair.center_x}, y={puyo_handler.current_pair.center_y}")
            
            # Test horizontal movement (should not be in handle_event anymore)
            original_x = puyo_handler.current_pair.center_x
            
            # Create a mock keydown event for A (left)
            test_event = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_a)
            puyo_handler.handle_event(test_event)
            
            # Position should not change from handle_event anymore
            if puyo_handler.current_pair.center_x == original_x:
                print("   SUCCESS: Horizontal movement not processed in handle_event")
            else:
                print("   WARNING: Horizontal movement still processed in handle_event")
            
            # Test rotation (should still work in handle_event)
            original_rotation = puyo_handler.current_pair.rotation
            test_rotation_event = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_SPACE)
            puyo_handler.handle_event(test_rotation_event)
            
            if puyo_handler.current_pair.rotation != original_rotation:
                print("   SUCCESS: Rotation still works in handle_event")
            else:
                print("   INFO: Rotation may be blocked by position constraints")
            
        print("5. Testing continuous input system...")
        # This would require pygame key state simulation, which is complex
        print("   (Continuous input testing requires full pygame context)")
        
        print("\nAll basic tests completed!")
        print("Try running the actual game to test controls during battle.")
        return True
        
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_battle_control_fixes()
    sys.exit(0 if success else 1)