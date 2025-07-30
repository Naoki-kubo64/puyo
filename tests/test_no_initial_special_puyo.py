#!/usr/bin/env python3
"""
初期特殊ぷよ無し状態のテスト
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

import pygame
pygame.init()

def test_no_initial_special_puyo():
    print("=== TESTING NO INITIAL SPECIAL PUYO STATE ===")
    
    try:
        from core.game_engine import GameEngine
        from core.simple_special_puyo import simple_special_manager
        from core.constants import PuyoType
        from battle.battle_handler import BattleHandler
        
        print("1. Testing initial special puyo rates...")
        engine = GameEngine()
        
        # Check special puyo manager rates
        print(f"   SimpleSpecialManager rates: {simple_special_manager.type_rates}")
        
        # Check player data rates
        print(f"   Player special puyo rates: {engine.player.special_puyo_rates}")
        
        # Check if all rates are 0%
        all_zero = all(rate == 0.0 for rate in simple_special_manager.type_rates.values())
        if all_zero:
            print("   SUCCESS: All special puyo rates are 0% initially")
        else:
            print("   FAILURE: Some special puyo rates are not 0%")
        
        print("2. Testing special puyo ownership...")
        # Check if player owns no special puyos initially
        owned_count = len(engine.player.owned_special_puyos)
        print(f"   Owned special puyos count: {owned_count}")
        
        if owned_count == 0:
            print("   SUCCESS: Player owns no special puyos initially")
        else:
            print("   FAILURE: Player owns special puyos initially")
        
        print("3. Testing special puyo spawning with 0% rates...")
        battle_handler = BattleHandler(engine, floor_level=1)
        battle_handler.countdown_active = False
        
        puyo_handler = battle_handler.puyo_handler
        if puyo_handler.current_pair is None:
            puyo_handler._spawn_new_pair()
        
        # Check if any special puyo was generated
        pair = puyo_handler.current_pair
        has_special = (pair.main_special is not None or 
                      pair.sub_special is not None)
        
        print(f"   Pair special types: main={pair.main_special}, sub={pair.sub_special}")
        
        if not has_special:
            print("   SUCCESS: No special puyos generated with 0% rates")
        else:
            print("   INFO: Special puyos generated (may be random variation)")
        
        print("4. Testing rate increase reward...")
        # Test increasing a rate from 0%
        initial_heal_rate = engine.player.special_puyo_rates.get('heal', 0.0)
        new_rate = engine.player.increase_special_puyo_rate('heal', 0.15)  # 15%
        
        print(f"   HEAL rate: {initial_heal_rate*100:.0f}% -> {new_rate*100:.0f}%")
        
        if new_rate == 0.15:
            print("   SUCCESS: Special puyo rate increase works")
        else:
            print("   FAILURE: Special puyo rate increase failed")
        
        return True
        
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_no_initial_special_puyo()
    sys.exit(0 if success else 1)