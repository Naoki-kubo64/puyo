#!/usr/bin/env python3
import sys
import os
sys.path.insert(0, 'src')

import pygame
pygame.init()

from src.rewards.reward_system import RewardGenerator, RewardType, Reward
from src.special_puyo.special_puyo import SpecialPuyoType

print('=== REWARD SYSTEM TEST ===')

def test_reward_generation():
    print('\n--- Reward Generation Test ---')
    
    generator = RewardGenerator()
    
    # 通常戦闘の報酬テスト
    print("Floor 1 Normal Battle:")
    rewards = generator.generate_battle_rewards(floor_level=1, enemy_type="slime", is_boss=False)
    for i, reward in enumerate(rewards):
        print(f"  {i+1}. {reward.name} ({reward.reward_type.value})")
        print(f"     {reward.description}")
        if reward.reward_type == RewardType.SPECIAL_PUYO_UNLOCK:
            print(f"     Special Puyo: {reward.value}")
    
    print("\nFloor 5 Boss Battle:")
    rewards = generator.generate_battle_rewards(floor_level=5, enemy_type="dragon", is_boss=True)
    for i, reward in enumerate(rewards):
        print(f"  {i+1}. {reward.name} ({reward.reward_type.value})")
        print(f"     {reward.description}")

def test_special_puyo_rewards():
    print('\n--- Special Puyo Reward Test ---')
    
    generator = RewardGenerator()
    
    # 特殊ぷよ報酬を強制生成
    special_reward = generator._generate_specific_reward(RewardType.SPECIAL_PUYO_UNLOCK, 3)
    if special_reward:
        print(f"Special Puyo Reward: {special_reward.name}")
        print(f"Description: {special_reward.description}")
        print(f"Rarity: {special_reward.rarity.name}")
        print(f"Value: {special_reward.value}")

def test_reward_colors():
    print('\n--- Reward Color Test ---')
    
    test_rewards = [
        Reward(RewardType.GOLD, 100, "ゴールド", "通貨"),
        Reward(RewardType.HP_UPGRADE, 10, "HP強化", "体力増加"),
        Reward(RewardType.SPECIAL_PUYO_UNLOCK, SpecialPuyoType.BUFF.value, "バフぷよ解放", "攻撃力アップ"),
    ]
    
    for reward in test_rewards:
        color = reward.get_color()
        rarity_color = reward.get_rarity_color()
        print(f"{reward.name}: color={color}, rarity_color={rarity_color}")

def test_reward_display():
    print('\n--- Reward Display Test ---')
    
    # 長い説明文のテスト
    long_reward = Reward(
        RewardType.PUYO_UPGRADE, 
        25, 
        "超強力連鎖威力アップ",
        "連鎖によるダメージが大幅に増加し、敵を一撃で倒せるようになる可能性がある"
    )
    
    display_lines = long_reward.get_display_text()
    print("Long description test:")
    for line in display_lines:
        print(f"  '{line}'")

def test_reward_probabilities():
    print('\n--- Reward Probability Test ---')
    
    generator = RewardGenerator()
    reward_counts = {}
    
    # 100回生成して確率をテスト
    for _ in range(100):
        rewards = generator.generate_battle_rewards(floor_level=2, enemy_type="goblin", is_boss=False)
        for reward in rewards:
            if reward.reward_type != RewardType.GOLD:  # ゴールドは必須なのでカウントしない
                reward_type = reward.reward_type.value
                reward_counts[reward_type] = reward_counts.get(reward_type, 0) + 1
    
    print("Reward distribution (100 battles):")
    total_non_gold = sum(reward_counts.values())
    for reward_type, count in sorted(reward_counts.items(), key=lambda x: x[1], reverse=True):
        percentage = (count / total_non_gold) * 100 if total_non_gold > 0 else 0
        print(f"  {reward_type}: {count} ({percentage:.1f}%)")

if __name__ == "__main__":
    test_reward_generation()
    test_special_puyo_rewards()
    test_reward_colors()
    test_reward_display()
    test_reward_probabilities()
    print('\n=== REWARD SYSTEM TEST COMPLETE ===')