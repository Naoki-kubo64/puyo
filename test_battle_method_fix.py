#!/usr/bin/env python3
"""
BattleHandler method name fix verification
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_battle_method_fix():
    print("=== TESTING BATTLE HANDLER METHOD FIX ===")
    
    try:
        from battle.battle_handler import BattleHandler
        from core.game_engine import GameEngine
        
        print("1. Creating game engine...")
        engine = GameEngine()
        
        print("2. Creating battle handler...")
        battle_handler = BattleHandler(engine, floor_level=1)
        
        print("3. Checking if _check_battle_result method exists...")
        if hasattr(battle_handler, '_check_battle_result'):
            print("   [OK] _check_battle_result method exists")
        else:
            print("   [FAIL] _check_battle_result method missing")
            return False
        
        print("4. Checking if _check_battle_end method exists (should NOT exist)...")
        if hasattr(battle_handler, '_check_battle_end'):
            print("   [WARNING] _check_battle_end method still exists (unexpected)")
        else:
            print("   [OK] _check_battle_end method does not exist (as expected)")
        
        print("5. Testing method callable...")
        # This should not crash
        battle_handler._check_battle_result()
        print("   [OK] Method call successful")
        
        return True
        
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_battle_method_fix()
    print(f"\nTest {'PASSED' if success else 'FAILED'}")
    sys.exit(0 if success else 1)