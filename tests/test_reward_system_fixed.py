#!/usr/bin/env python3
"""
報酬システムの修正されたテスト
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

import pygame
pygame.init()

from rewards.reward_system import RewardGenerator, RewardType, Reward

print('=== REWARD SYSTEM TEST (FIXED) ===')

def test_reward_generation():
    print('\n--- Reward Generation Test ---')
    
    generator = RewardGenerator()
    
    # 通常戦闘の報酬テスト
    print("Floor 1 Normal Battle:")
    rewards = generator.generate_battle_rewards(floor_level=1, enemy_type="slime", is_boss=False)
    for i, reward in enumerate(rewards):
        print(f"  {i+1}. {reward.name} ({reward.reward_type.value})")
        print(f"     {reward.description}")
        if reward.reward_type == RewardType.SPECIAL_PUYO:
            print(f"     Special Puyo: {reward.value}")
    
    print("\nFloor 5 Boss Battle:")
    rewards = generator.generate_battle_rewards(floor_level=5, enemy_type="dragon", is_boss=True)
    for i, reward in enumerate(rewards):
        print(f"  {i+1}. {reward.name} ({reward.reward_type.value})")
        print(f"     {reward.description}")

def test_special_puyo_rewards():
    print('\n--- Special Puyo Reward Test ---')
    
    generator = RewardGenerator()
    
    # 複数回試行して特殊ぷよ報酬を取得
    for attempt in range(5):
        rewards = generator.generate_battle_rewards(floor_level=3, enemy_type="boss", is_boss=True)
        special_rewards = [r for r in rewards if r.reward_type == RewardType.SPECIAL_PUYO]
        
        if special_rewards:
            for reward in special_rewards:
                print(f"Special Puyo Reward: {reward.name}")
                print(f"Description: {reward.description}")
                print(f"Rarity: {reward.rarity.name}")
                print(f"Value: {reward.value}")
            break
    else:
        print("No special puyo rewards generated in test attempts")

def test_reward_types():
    print('\n--- Reward Types Test ---')
    
    # 利用可能な報酬タイプを表示
    for reward_type in RewardType:
        print(f"- {reward_type.name}: {reward_type.value}")

def test_reward_balance():
    print('\n--- Reward Balance Test ---')
    
    generator = RewardGenerator()
    
    # 異なるフロアでの報酬バランスをテスト
    for floor in [1, 3, 5, 10, 15]:
        print(f"\nFloor {floor}:")
        rewards = generator.generate_battle_rewards(floor_level=floor, enemy_type="normal", is_boss=False)
        
        reward_counts = {}
        for reward in rewards:
            reward_type = reward.reward_type.value
            reward_counts[reward_type] = reward_counts.get(reward_type, 0) + 1
        
        print(f"  Total rewards: {len(rewards)}")
        for reward_type, count in reward_counts.items():
            print(f"  {reward_type}: {count}")

if __name__ == "__main__":
    try:
        test_reward_generation()
        test_special_puyo_rewards()
        test_reward_types()
        test_reward_balance()
        print('\n=== ALL TESTS COMPLETED ===')
    except Exception as e:
        print(f'ERROR: {e}')
        import traceback
        traceback.print_exc()