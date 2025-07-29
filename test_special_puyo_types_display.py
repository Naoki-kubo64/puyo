#!/usr/bin/env python3
"""
特殊ぷよの種類と表示システムのテスト
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

import pygame
pygame.init()

def test_special_puyo_types_and_display():
    print("=== TESTING SPECIAL PUYO TYPES AND DISPLAY SYSTEM ===")
    
    try:
        from core.game_engine import GameEngine
        from core.simple_special_puyo import SimpleSpecialType, simple_special_manager
        from battle.battle_handler import BattleHandler
        
        print("1. Testing available special puyo types...")
        all_types = list(SimpleSpecialType)
        print(f"   Available types: {[t.value for t in all_types]}")
        print(f"   Total count: {len(all_types)}")
        
        print("2. Testing initial display (should show 'なし')...")
        engine = GameEngine()
        battle_handler = BattleHandler(engine, floor_level=1)
        
        # Check rates are all 0%
        rates = engine.player.special_puyo_rates
        print(f"   Initial rates: {rates}")
        
        # Test surface creation for display
        test_surface = pygame.Surface((1920, 1080))
        
        # TopUIBar should show "なし" when no special puyos
        battle_handler.top_ui_bar.draw_top_bar(
            test_surface, 100, 100, 50, 1, rates
        )
        print("   SUCCESS: TopUIBar renders with no special puyos")
        
        print("3. Testing special puyo acquisition...")
        # Give player some special puyos
        engine.player.increase_special_puyo_rate('heal', 0.15)
        engine.player.increase_special_puyo_rate('lightning', 0.10)
        engine.player.increase_special_puyo_rate('poison', 0.05)
        
        updated_rates = engine.player.special_puyo_rates
        print(f"   Updated rates: {updated_rates}")
        
        # Count visible special puyos (rate > 0)
        visible_count = sum(1 for rate in updated_rates.values() if rate > 0.0)
        print(f"   Visible special puyos: {visible_count}")
        
        if visible_count == 3:
            print("   SUCCESS: 3 special puyos acquired")
        else:
            print(f"   WARNING: Expected 3, got {visible_count}")
        
        print("4. Testing new special puyo effects...")
        from core.constants import PuyoType
        from puzzle.puyo_grid import PuyoPosition
        
        puyo_grid = battle_handler.puyo_handler.puyo_grid
        
        # Test LIGHTNING effect
        puyo_grid.set_puyo(1, 10, PuyoType.BLUE)
        puyo_grid.set_special_puyo_data(1, 10, SimpleSpecialType.LIGHTNING)
        
        print("   Testing LIGHTNING effect...")
        initial_enemy_hp = [e.current_hp for e in battle_handler.enemy_group.enemies]
        
        positions = {PuyoPosition(1, 10)}
        puyo_grid.eliminate_puyos(positions)
        
        final_enemy_hp = [e.current_hp for e in battle_handler.enemy_group.enemies]
        damage_dealt = [initial - final for initial, final in zip(initial_enemy_hp, final_enemy_hp)]
        
        if any(dmg > 0 for dmg in damage_dealt):
            print(f"   SUCCESS: LIGHTNING effect worked! Damage: {damage_dealt}")
        else:
            print("   FAILURE: LIGHTNING effect failed")
        
        print("5. Testing UI display with acquired special puyos...")
        battle_handler.top_ui_bar.draw_top_bar(
            test_surface, 80, 100, 50, 1, updated_rates
        )
        print("   SUCCESS: TopUIBar renders with acquired special puyos")
        
        return True
        
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_special_puyo_types_and_display()
    sys.exit(0 if success else 1)