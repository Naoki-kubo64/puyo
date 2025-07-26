#!/usr/bin/env python3
import sys
import os
sys.path.insert(0, 'src')

import pygame
pygame.init()

from src.core.constants import *

print('=== DUNGEON SCALING TEST ===')

def test_floor_scaling():
    print('\n--- Floor-by-Floor Enemy Scaling ---')
    
    base_hp = ENEMY_BASE_HP
    base_damage = ENEMY_ATTACK_DAMAGE
    base_interval = ENEMY_ATTACK_INTERVAL
    
    print(f'Base Stats: HP={base_hp}, DMG={base_damage}, Interval={base_interval:.1f}s')
    print(f'Scaling: HP×{FLOOR_SCALING_HP}, DMG×{FLOOR_SCALING_DAMAGE}, Speed×{FLOOR_SCALING_SPEED}')
    print()
    print('Floor | Enemy HP | Enemy DMG | Attack Interval | Player Survival Time')
    print('------|----------|-----------|-----------------|---------------------')
    
    for floor in range(1, 11):  # フロア1-10をテスト
        # スケーリング計算
        scaled_hp = int(base_hp * (FLOOR_SCALING_HP ** (floor - 1)))
        scaled_damage = int(base_damage * (FLOOR_SCALING_DAMAGE ** (floor - 1)))
        scaled_interval = base_interval * (FLOOR_SCALING_SPEED ** (floor - 1))
        
        # プレイヤー生存時間
        attacks_to_kill = (PLAYER_MAX_HP + scaled_damage - 1) // scaled_damage
        survival_time = attacks_to_kill * scaled_interval
        
        print(f'  {floor:2}  |    {scaled_hp:3}   |     {scaled_damage:2}    |      {scaled_interval:4.1f}s      |       {survival_time:4.1f}s')

def test_battle_progression():
    print('\n--- Battle Difficulty Progression ---')
    
    print('Damage needed to defeat enemies by floor:')
    print('Floor | Enemy HP | 1-Hit Kill | 2-Hit Kill | 3-Hit Kill')
    print('------|----------|-------------|-------------|------------')
    
    for floor in range(1, 8):
        scaled_hp = int(ENEMY_BASE_HP * (FLOOR_SCALING_HP ** (floor - 1)))
        
        # 各Hit数で必要なダメージ
        one_hit = scaled_hp
        two_hit = (scaled_hp + 1) // 2
        three_hit = (scaled_hp + 2) // 3
        
        print(f'  {floor:2}  |    {scaled_hp:3}   |     {one_hit:3}     |     {two_hit:3}     |     {three_hit:3}')

def test_progression_feel():
    print('\n--- Progression Feel Analysis ---')
    
    floors_to_test = [1, 3, 5, 7, 10]
    
    for floor in floors_to_test:
        scaled_hp = int(ENEMY_BASE_HP * (FLOOR_SCALING_HP ** (floor - 1)))
        scaled_damage = int(ENEMY_ATTACK_DAMAGE * (FLOOR_SCALING_DAMAGE ** (floor - 1)))
        scaled_interval = ENEMY_ATTACK_INTERVAL * (FLOOR_SCALING_SPEED ** (floor - 1))
        
        print(f'\nFloor {floor}:')
        print(f'  Enemy Stats: HP={scaled_hp}, DMG={scaled_damage}, Interval={scaled_interval:.1f}s')
        
        # 小さな連鎖でのダメージ効果
        small_chain_damage = 4  # スコア40程度
        hits_needed = (scaled_hp + small_chain_damage - 1) // small_chain_damage
        
        print(f'  Small chains (4 dmg): {hits_needed} hits needed')
        
        # 大きな連鎖でのダメージ効果
        big_chain_damage = 12  # スコア120程度
        big_hits_needed = (scaled_hp + big_chain_damage - 1) // big_chain_damage
        
        print(f'  Big chains (12 dmg): {big_hits_needed} hits needed')
        
        # プレイヤーが受けるプレッシャー
        survival_time = (PLAYER_MAX_HP // scaled_damage) * scaled_interval
        print(f'  Time pressure: {survival_time:.1f}s survival time')
        
        if floor == 1:
            print('  -> Tutorial difficulty: Very forgiving')
        elif floor <= 3:
            print('  -> Early game: Learning phase')
        elif floor <= 7:
            print('  -> Mid game: Skill development')
        else:
            print('  -> Late game: Mastery required')

def evaluate_scaling():
    print('\n--- Scaling Evaluation ---')
    
    print('Scaling factors per floor:')
    print(f'  HP scaling: {FLOOR_SCALING_HP}x (moderate growth)')
    print(f'  Damage scaling: {FLOOR_SCALING_DAMAGE}x (slower growth)')
    print(f'  Speed scaling: {FLOOR_SCALING_SPEED}x (gets faster)')
    
    # 10フロア後の強さ
    final_hp = int(ENEMY_BASE_HP * (FLOOR_SCALING_HP ** 9))
    final_damage = int(ENEMY_ATTACK_DAMAGE * (FLOOR_SCALING_DAMAGE ** 9))
    final_interval = ENEMY_ATTACK_INTERVAL * (FLOOR_SCALING_SPEED ** 9)
    
    print(f'\nFloor 10 enemy would have:')
    print(f'  HP: {final_hp} ({final_hp // ENEMY_BASE_HP}x stronger)')
    print(f'  Damage: {final_damage} ({final_damage / ENEMY_ATTACK_DAMAGE:.1f}x stronger)')
    print(f'  Interval: {final_interval:.1f}s ({ENEMY_ATTACK_INTERVAL / final_interval:.1f}x faster)')
    
    if final_hp > 200:
        print('  WARNING: Late game enemies might be too tanky')
    elif final_hp < 50:
        print('  WARNING: Late game enemies might be too weak')
    else:
        print('  GOOD: Late game HP scaling looks reasonable')

if __name__ == "__main__":
    test_floor_scaling()
    test_battle_progression()
    test_progression_feel()
    evaluate_scaling()
    print('\n=== DUNGEON SCALING TEST COMPLETE ===')