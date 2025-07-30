#!/usr/bin/env python3
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

import pygame
pygame.init()

from src.core.constants import *
from src.puzzle.puyo_grid import PuyoGrid
from src.battle.enemy import Enemy, EnemyType

print('=== BATTLE BALANCE TEST ===')

# ダメージ計算のテスト
def test_damage_calculation():
    print('\n--- Damage Calculation Test ---')
    
    # 様々な連鎖スコアでのダメージ計算
    test_scores = [40, 80, 120, 200, 300, 500, 1000]
    
    print(f'CHAIN_SCORE_BASE: {CHAIN_SCORE_BASE}')
    print(f'Base damage = chain_score // {CHAIN_SCORE_BASE}')
    print()
    
    for score in test_scores:
        base_damage = score // CHAIN_SCORE_BASE
        chain_damage = int(base_damage * 1.0)  # デフォルト倍率
        print(f'Chain Score: {score:4} -> Base Damage: {base_damage:2} -> Final Damage: {chain_damage:2}')

# 敵のHPバランステスト
def test_enemy_balance():
    print('\n--- Enemy Balance Test ---')
    
    # 現在の設定表示
    print(f'Enemy Base HP: {ENEMY_BASE_HP}')
    print(f'Enemy Attack Damage: {ENEMY_ATTACK_DAMAGE}')
    print(f'Enemy Attack Interval: {ENEMY_ATTACK_INTERVAL}s')
    print()
    
    # プレイヤーが受けるダメージ計算
    attacks_to_kill_player = PLAYER_MAX_HP // ENEMY_ATTACK_DAMAGE
    time_to_kill_player = attacks_to_kill_player * ENEMY_ATTACK_INTERVAL
    
    print(f'Player Max HP: {PLAYER_MAX_HP}')
    print(f'Attacks needed to kill player: {attacks_to_kill_player}')
    print(f'Time to kill player: {time_to_kill_player:.1f} seconds')
    print()
    
    # 敵を倒すのに必要な連鎖数
    damage_needed = ENEMY_BASE_HP
    print(f'Damage needed to kill enemy: {damage_needed}')
    
    # 様々なダメージで敵を倒すのに必要な回数
    test_damages = [2, 4, 6, 8, 10, 15, 20]
    for damage in test_damages:
        hits_needed = (damage_needed + damage - 1) // damage  # 切り上げ計算
        print(f'  {damage:2} damage per hit -> {hits_needed:2} hits needed')

# 戦闘フローシミュレーション
def test_battle_flow():
    print('\n--- Battle Flow Simulation ---')
    
    enemy_hp = ENEMY_BASE_HP
    player_hp = PLAYER_MAX_HP
    time_elapsed = 0.0
    
    print('Battle simulation (assuming player deals 8 damage every 10 seconds):')
    print(f'Time: {time_elapsed:4.1f}s | Player HP: {player_hp:3} | Enemy HP: {enemy_hp:2}')
    
    player_damage_interval = 10.0  # プレイヤーが10秒ごとに攻撃
    player_damage = 8
    
    while player_hp > 0 and enemy_hp > 0:
        # 次のイベントまでの時間を計算
        next_player_attack = ((time_elapsed // player_damage_interval) + 1) * player_damage_interval
        next_enemy_attack = ((time_elapsed // ENEMY_ATTACK_INTERVAL) + 1) * ENEMY_ATTACK_INTERVAL
        
        if next_player_attack <= next_enemy_attack:
            # プレイヤーの攻撃
            time_elapsed = next_player_attack
            enemy_hp -= player_damage
            if enemy_hp < 0:
                enemy_hp = 0
            print(f'Time: {time_elapsed:4.1f}s | Player HP: {player_hp:3} | Enemy HP: {enemy_hp:2} (Player attacks!)')
        else:
            # 敵の攻撃
            time_elapsed = next_enemy_attack
            player_hp -= ENEMY_ATTACK_DAMAGE
            if player_hp < 0:
                player_hp = 0
            print(f'Time: {time_elapsed:4.1f}s | Player HP: {player_hp:3} | Enemy HP: {enemy_hp:2} (Enemy attacks!)')
        
        # 安全措置
        if time_elapsed > 120:  # 2分でタイムアウト
            print('Battle timeout!')
            break
    
    if player_hp <= 0:
        print('\nResult: Player defeated!')
    elif enemy_hp <= 0:
        print('\nResult: Enemy defeated!')

# バランス評価
def evaluate_balance():
    print('\n--- Balance Evaluation ---')
    
    # 期待される戦闘時間
    expected_battle_time = 30  # 30秒程度が理想
    
    # プレイヤーが受けるプレッシャー
    time_pressure = PLAYER_MAX_HP / ENEMY_ATTACK_DAMAGE * ENEMY_ATTACK_INTERVAL
    
    print(f'Expected battle duration: ~{expected_battle_time} seconds')
    print(f'Player survival time (no healing): {time_pressure:.1f} seconds')
    
    if time_pressure > expected_battle_time * 2:
        print('✓ Player has sufficient time to plan attacks')
    elif time_pressure > expected_battle_time:
        print('⚠ Player has moderate time pressure')
    else:
        print('✗ Player has high time pressure - consider balancing')
    
    # 小さな連鎖でのダメージ効果
    small_chain_score = 60  # 4個消去程度
    small_damage = small_chain_score // CHAIN_SCORE_BASE
    
    print(f'\nSmall chain (score {small_chain_score}): {small_damage} damage')
    if small_damage >= 2:
        print('✓ Small chains deal meaningful damage')
    elif small_damage >= 1:
        print('⚠ Small chains deal minimal damage')
    else:
        print('✗ Small chains deal no damage - adjust CHAIN_SCORE_BASE')

if __name__ == "__main__":
    test_damage_calculation()
    test_enemy_balance()
    test_battle_flow()
    evaluate_balance()
    print('\n=== BATTLE BALANCE TEST COMPLETE ===')