#!/usr/bin/env python3
"""
ゲームエラーのデバッグスクリプト
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

import traceback

def test_imports():
    """インポートエラーをチェック"""
    print("=== TESTING IMPORTS ===")
    
    try:
        import pygame
        print("[OK] pygame imported")
    except Exception as e:
        print(f"[FAIL] pygame import error: {e}")
        return False
    
    try:
        from core.simple_special_puyo import SimpleSpecialType
        print("[OK] SimpleSpecialType imported")
    except Exception as e:
        print(f"[FAIL] SimpleSpecialType import error: {e}")
        traceback.print_exc()
        return False
    
    try:
        from core.game_engine import GameEngine
        print("[OK] GameEngine imported")
    except Exception as e:
        print(f"[FAIL] GameEngine import error: {e}")
        traceback.print_exc()
        return False
    
    return True

def test_special_puyo_methods():
    """特殊ぷよのメソッドをテスト"""
    print("\n=== TESTING SPECIAL PUYO METHODS ===")
    
    try:
        from core.simple_special_puyo import SimpleSpecialType
        
        # 各メソッドをテスト
        for puyo_type in SimpleSpecialType:
            try:
                name = puyo_type.get_display_name()
                desc = puyo_type.get_description()
                print(f"[OK] {puyo_type.value}: {name} - {desc}")
            except Exception as e:
                print(f"[FAIL] Error with {puyo_type.value}: {e}")
                traceback.print_exc()
                return False
        
        return True
    except Exception as e:
        print(f"[FAIL] General error: {e}")
        traceback.print_exc()
        return False

def test_reward_system():
    """報酬システムをテスト"""
    print("\n=== TESTING REWARD SYSTEM ===")
    
    try:
        from rewards.reward_system import RewardGenerator, RewardType
        
        reward_gen = RewardGenerator()
        print("[OK] RewardGenerator created")
        
        # 特殊ぷよ報酬を生成
        reward = reward_gen._generate_specific_reward(RewardType.SPECIAL_PUYO, 1)
        if reward:
            print(f"[OK] Generated reward: {reward.name}")
            print(f"     Description: {reward.description}")
            print(f"     Value type: {type(reward.value)}")
        else:
            print("[WARNING] No reward generated")
        
        return True
    except Exception as e:
        print(f"[FAIL] Reward system error: {e}")
        traceback.print_exc()
        return False

def test_battle_handler():
    """BattleHandlerをテスト"""
    print("\n=== TESTING BATTLE HANDLER ===")
    
    try:
        import pygame
        pygame.init()
        
        from core.game_engine import GameEngine
        from battle.battle_handler import BattleHandler
        
        engine = GameEngine()
        print("[OK] GameEngine created")
        
        battle_handler = BattleHandler(engine, floor_level=1)
        print("[OK] BattleHandler created")
        
        # _check_battle_result メソッドが存在するかチェック
        if hasattr(battle_handler, '_check_battle_result'):
            print("[OK] _check_battle_result method exists")
        else:
            print("[FAIL] _check_battle_result method missing")
            return False
        
        return True
    except Exception as e:
        print(f"[FAIL] BattleHandler error: {e}")
        traceback.print_exc()
        return False

def main():
    """メイン実行関数"""
    print("Starting comprehensive error debug...")
    
    success = True
    
    success &= test_imports()
    success &= test_special_puyo_methods()
    success &= test_reward_system()
    success &= test_battle_handler()
    
    print(f"\n=== RESULT ===")
    if success:
        print("All tests passed! No obvious errors found.")
    else:
        print("Errors detected! Check the output above.")
    
    return success

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"CRITICAL ERROR: {e}")
        traceback.print_exc()
        sys.exit(1)