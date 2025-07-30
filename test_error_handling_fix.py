#!/usr/bin/env python3
"""
エラーハンドリング修正のテスト
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

import pygame
pygame.init()

def test_safe_enum_methods():
    """安全なEnumメソッドのテスト"""
    print("=== TESTING SAFE ENUM METHODS ===")
    
    try:
        from core.simple_special_puyo import SimpleSpecialType
        
        # 正常なケース
        for puyo_type in SimpleSpecialType:
            try:
                name = puyo_type.get_display_name()
                desc = puyo_type.get_description()
                print(f"[OK] {puyo_type.value}: {name} - {desc}")
            except Exception as e:
                print(f"[FAIL] Error with {puyo_type.value}: {e}")
                return False
        
        return True
        
    except Exception as e:
        print(f"[FAIL] Import or general error: {e}")
        return False

def test_safe_reward_generation():
    """安全な報酬生成のテスト"""
    print("\n=== TESTING SAFE REWARD GENERATION ===")
    
    try:
        from rewards.reward_system import RewardGenerator, RewardType
        
        gen = RewardGenerator()
        
        # 複数回テスト
        for i in range(5):
            try:
                reward = gen._generate_specific_reward(RewardType.SPECIAL_PUYO, 1)
                if reward:
                    print(f"[OK] Generated: {reward.name}")
                else:
                    print(f"[INFO] No reward generated on attempt {i+1}")
            except Exception as e:
                print(f"[FAIL] Error in generation {i+1}: {e}")
                return False
        
        return True
        
    except Exception as e:
        print(f"[FAIL] Reward generation error: {e}")
        return False

def test_safe_battle_reward_handler():
    """安全なBattleRewardHandlerのテスト"""
    print("\n=== TESTING SAFE BATTLE REWARD HANDLER ===")
    
    try:
        from core.game_engine import GameEngine
        from rewards.battle_reward_handler import BattleRewardHandler
        from rewards.reward_system import Reward, RewardType
        from core.simple_special_puyo import SimpleSpecialType
        
        engine = GameEngine()
        handler = BattleRewardHandler(engine)
        print("[OK] BattleRewardHandler created")
        
        # 特殊ぷよ報酬をシミュレート
        test_reward = Reward(
            reward_type=RewardType.SPECIAL_PUYO,
            value=SimpleSpecialType.HEAL,
            name="テスト報酬",
            description="テスト用"
        )
        
        # _apply_rewardを呼び出してテスト
        try:
            handler._apply_reward(test_reward)
            print("[OK] _apply_reward executed without error")
        except Exception as e:
            print(f"[FAIL] Error in _apply_reward: {e}")
            return False
        
        return True
        
    except Exception as e:
        print(f"[FAIL] BattleRewardHandler error: {e}")
        return False

def test_complete_integration():
    """完全統合テスト"""
    print("\n=== TESTING COMPLETE INTEGRATION ===")
    
    try:
        from core.game_engine import GameEngine
        from rewards.reward_system import RewardGenerator, RewardType
        from rewards.battle_reward_handler import BattleRewardHandler
        
        # エンジン作成
        engine = GameEngine()
        print("[OK] GameEngine created")
        
        # 報酬生成
        gen = RewardGenerator()
        reward = gen._generate_specific_reward(RewardType.SPECIAL_PUYO, 1)
        
        if reward:
            print(f"[OK] Generated reward: {reward.name}")
            
            # ハンドラーで処理
            handler = BattleRewardHandler(engine)
            handler._apply_reward(reward)
            print("[OK] Reward applied successfully")
        else:
            print("[INFO] No reward generated")
        
        return True
        
    except Exception as e:
        print(f"[FAIL] Integration error: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """メイン関数"""
    print("Testing error handling fixes...")
    
    success = True
    success &= test_safe_enum_methods()
    success &= test_safe_reward_generation()
    success &= test_safe_battle_reward_handler()
    success &= test_complete_integration()
    
    print(f"\n=== FINAL RESULT ===")
    if success:
        print("All error handling tests passed!")
    else:
        print("Some error handling tests failed!")
    
    return success

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"TEST RUNNER ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)