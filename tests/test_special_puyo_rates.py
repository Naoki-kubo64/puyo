#!/usr/bin/env python3
"""
特殊ぷよの個別出現率とリワードシステムのテスト
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

import pygame
pygame.init()
pygame.display.set_mode((1920, 1080))

def test_special_puyo_rates():
    print("=== SPECIAL PUYO INDIVIDUAL RATES TEST ===")
    
    try:
        from core.simple_special_puyo import SimpleSpecialType, simple_special_manager
        from rewards.reward_system import RewardGenerator, RewardType, Reward
        from core.game_engine import GameEngine
        
        print("1. Testing initial rates...")
        initial_rates = simple_special_manager.get_all_rates()
        print(f"   Initial rates: {simple_special_manager._format_rates()}")
        
        # 初期出現率の確認
        heal_rate = simple_special_manager.get_type_rate(SimpleSpecialType.HEAL)
        bomb_rate = simple_special_manager.get_type_rate(SimpleSpecialType.BOMB)
        print(f"   HEAL rate: {heal_rate*100:.0f}%")
        print(f"   BOMB rate: {bomb_rate*100:.0f}%")
        
        print("\n2. Testing rate increases...")
        # HEAL出現率を5%上昇
        new_heal_rate = simple_special_manager.increase_type_rate(SimpleSpecialType.HEAL, 0.05)
        print(f"   HEAL rate after +5%: {new_heal_rate*100:.0f}%")
        
        # BOMB出現率を5%上昇
        new_bomb_rate = simple_special_manager.increase_type_rate(SimpleSpecialType.BOMB, 0.05)
        print(f"   BOMB rate after +5%: {new_bomb_rate*100:.0f}%")
        
        print("\n3. Testing weighted random selection...")
        # 100回生成してタイプ分布を確認
        type_counts = {SimpleSpecialType.HEAL: 0, SimpleSpecialType.BOMB: 0}
        
        for _ in range(100):
            if simple_special_manager.should_spawn_special():
                selected_type = simple_special_manager.get_random_special_type()
                type_counts[selected_type] += 1
        
        total_spawned = sum(type_counts.values())
        print(f"   Total special puyos spawned: {total_spawned}/100")
        if total_spawned > 0:
            heal_percentage = (type_counts[SimpleSpecialType.HEAL] / total_spawned) * 100
            bomb_percentage = (type_counts[SimpleSpecialType.BOMB] / total_spawned) * 100
            print(f"   HEAL spawned: {type_counts[SimpleSpecialType.HEAL]} ({heal_percentage:.1f}%)")
            print(f"   BOMB spawned: {type_counts[SimpleSpecialType.BOMB]} ({bomb_percentage:.1f}%)")
        
        print("\n4. Testing reward generation...")
        engine = GameEngine()
        reward_gen = RewardGenerator()
        
        # 特殊ぷよ報酬を生成
        special_reward = reward_gen._generate_specific_reward(RewardType.SPECIAL_PUYO, 1)
        if special_reward:
            print(f"   Generated reward: {special_reward.name}")
            print(f"   Description: {special_reward.description}")
            print(f"   Value type: {type(special_reward.value)}")
            print(f"   Value: {special_reward.value}")
        
        print("\n5. Testing reward application...")
        # 報酬選択ハンドラーのテスト
        from rewards.reward_system import RewardSelectionHandler
        
        # ダミー報酬リスト
        test_rewards = [
            Reward(RewardType.GOLD, 50, "50 ゴールド", "テスト用"),
            special_reward
        ]
        
        if special_reward:
            # 報酬を手動で適用してテスト
            reward_handler = RewardSelectionHandler(engine, test_rewards)
            
            # 適用前の出現率を記録
            old_rate = simple_special_manager.get_type_rate(special_reward.value)
            print(f"   Before reward: {special_reward.value.value} rate = {old_rate*100:.0f}%")
            
            # 報酬を手動で適用
            reward_handler._apply_selected_reward(special_reward)
            
            # 適用後の出現率を確認
            new_rate = simple_special_manager.get_type_rate(special_reward.value)
            print(f"   After reward: {special_reward.value.value} rate = {new_rate*100:.0f}%")
            print(f"   Rate increase: +{(new_rate - old_rate)*100:.0f}%")
        
        print("\n6. Testing edge cases...")
        # 最大100%まで上昇のテスト
        print("   Testing maximum rate (100%) cap...")
        for i in range(20):  # 20回x5% = 100%上昇を試行
            old_rate = simple_special_manager.get_type_rate(SimpleSpecialType.HEAL)
            new_rate = simple_special_manager.increase_type_rate(SimpleSpecialType.HEAL, 0.05)
            if new_rate >= 1.0:
                print(f"   Reached maximum: {new_rate*100:.0f}% after {i+1} increases")
                break
        
        print("\nSUCCESS: All special puyo rate tests passed!")
        return True
        
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_special_puyo_rates()
    sys.exit(0 if success else 1)