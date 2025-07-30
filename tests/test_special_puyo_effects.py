#!/usr/bin/env python3
"""
特殊ぷよ効果のテスト
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

import pygame
pygame.init()

def test_special_puyo_effects():
    print("=== TESTING SPECIAL PUYO EFFECTS ===")
    
    try:
        from core.game_engine import GameEngine
        from battle.battle_handler import BattleHandler
        from core.constants import PuyoType
        from core.simple_special_puyo import SimpleSpecialType
        from puzzle.puyo_grid import PuyoPosition
        
        print("1. Creating battle handler...")
        engine = GameEngine()
        battle_handler = BattleHandler(engine, floor_level=1)
        
        # End countdown to enable effects
        battle_handler.countdown_active = False
        battle_handler.countdown_timer = 0.0
        
        puyo_grid = battle_handler.puyo_handler.puyo_grid
        
        print("2. Testing HEAL effect...")
        # First, damage the player to test healing
        engine.player.take_damage(20)  # Take 20 damage
        
        # Set up a heal puyo
        puyo_grid.set_puyo(2, 10, PuyoType.RED)
        puyo_grid.set_special_puyo_data(2, 10, SimpleSpecialType.HEAL)
        
        # Record initial HP (after damage)
        initial_hp = engine.player.hp
        print(f"   Initial HP (after damage): {initial_hp}")
        
        # Trigger elimination (which should trigger heal effect)
        positions = {PuyoPosition(2, 10)}
        puyo_grid.eliminate_puyos(positions)
        
        # Check if HP increased
        final_hp = engine.player.hp
        print(f"   Final HP: {final_hp}")
        if final_hp > initial_hp:
            print(f"   SUCCESS: HEAL effect worked! (+{final_hp - initial_hp} HP)")
        else:
            print("   FAILURE: HEAL effect did not work")
        
        print("3. Testing BOMB effect...")
        # Set up a bomb puyo
        puyo_grid.set_puyo(3, 10, PuyoType.BLUE)
        puyo_grid.set_special_puyo_data(3, 10, SimpleSpecialType.BOMB)
        
        # Record initial enemy HP
        enemies = battle_handler.enemy_group.enemies
        if enemies:
            initial_enemy_hp = [enemy.current_hp for enemy in enemies]
            print(f"   Initial enemy HP: {initial_enemy_hp}")
            
            # Set a current chain count for damage calculation
            engine.player.current_chain_count = 2  # 2-chain for testing
            
            # Trigger elimination (which should trigger bomb effect)
            positions = {PuyoPosition(3, 10)}
            puyo_grid.eliminate_puyos(positions)
            
            # Check if enemies took damage
            final_enemy_hp = [enemy.current_hp for enemy in enemies]
            print(f"   Final enemy HP: {final_enemy_hp}")
            
            damage_dealt = [initial - final for initial, final in zip(initial_enemy_hp, final_enemy_hp)]
            if any(dmg > 0 for dmg in damage_dealt):
                print(f"   SUCCESS: BOMB effect worked! Damage dealt: {damage_dealt}")
            else:
                print("   FAILURE: BOMB effect did not work")
        else:
            print("   No enemies available for bomb test")
        
        print("4. Battle handler connection test...")
        print(f"   PuyoGrid has battle_handler: {hasattr(puyo_grid, 'battle_handler')}")
        print(f"   Battle handler is set: {puyo_grid.battle_handler is not None}")
        
        return True
        
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_special_puyo_effects()
    sys.exit(0 if success else 1)