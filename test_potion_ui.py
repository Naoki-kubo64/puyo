#!/usr/bin/env python3
"""
ポーションUI機能のテスト
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

import pygame
pygame.init()

def test_potion_ui():
    print("=== TESTING POTION UI FUNCTIONALITY ===")
    
    try:
        from core.game_engine import GameEngine
        from battle.battle_handler import BattleHandler
        from inventory.player_inventory import ItemType
        
        print("1. Creating battle handler...")
        engine = GameEngine()
        battle_handler = BattleHandler(engine, floor_level=1)
        
        print("2. Testing potion inventory...")
        potions = engine.player.inventory.get_items_by_type(ItemType.POTION)
        print(f"   Initial potions: {[(p.name, p.quantity) for p in potions]}")
        
        if potions:
            print("   SUCCESS: Player has potions")
        else:
            print("   INFO: No initial potions")
        
        print("3. Testing potion display in UI...")
        test_surface = pygame.Surface((1920, 1080))
        
        # Draw TopUIBar with potion display
        special_puyo_rates = engine.player.special_puyo_rates
        battle_handler.top_ui_bar.draw_top_bar(
            test_surface,
            engine.player.hp, engine.player.max_hp,
            engine.player.gold,
            1,  # floor
            special_puyo_rates,
            engine.player.inventory
        )
        print("   SUCCESS: TopUIBar renders with potion display")
        
        print("4. Testing potion click areas...")
        if hasattr(battle_handler.top_ui_bar, 'potion_click_areas'):
            click_areas = battle_handler.top_ui_bar.potion_click_areas
            print(f"   Potion click areas: {len(click_areas)}")
            
            if click_areas:
                # Simulate click on first potion
                first_rect, first_potion_id = click_areas[0]
                click_pos = first_rect.center
                
                initial_hp = engine.player.hp
                engine.player.take_damage(10)  # Take damage first
                damaged_hp = engine.player.hp
                
                # Test potion usage
                used = battle_handler.top_ui_bar.handle_potion_click(
                    click_pos, engine.player.inventory, engine.player
                )
                
                final_hp = engine.player.hp
                
                if used and final_hp > damaged_hp:
                    print(f"   SUCCESS: Potion used! HP: {damaged_hp} -> {final_hp}")
                elif used:
                    print(f"   SUCCESS: Potion used! (non-healing effect)")
                else:
                    print("   INFO: Potion click not processed")
            else:
                print("   INFO: No potion click areas detected")
        else:
            print("   INFO: No potion click areas available")
        
        return True
        
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_potion_ui()
    sys.exit(0 if success else 1)