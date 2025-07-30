#!/usr/bin/env python3
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

import pygame
pygame.init()

from src.special_puyo.special_puyo import SpecialPuyoType, SpecialPuyo, SpecialPuyoManager

print('=== SPECIAL PUYO TEST ===')

def test_new_special_puyos():
    print('\n--- New Special Puyo Types ---')
    
    new_types = [
        SpecialPuyoType.BUFF,
        SpecialPuyoType.TIMED_POISON,
        SpecialPuyoType.CHAIN_EXTEND,
        SpecialPuyoType.ABSORB_SHIELD,
        SpecialPuyoType.CURSE,
        SpecialPuyoType.REFLECT,
    ]
    
    for puyo_type in new_types:
        puyo = SpecialPuyo(puyo_type, 0, 0)
        effect = puyo.effect
        
        print(f'\n{puyo_type.name}:')
        print(f'  Icon: {puyo.get_icon_char()}')
        print(f'  Color: {puyo.get_display_color()}')
        print(f'  Effect: {effect.effect_type}')
        print(f'  Power: {effect.power}')
        print(f'  Duration: {effect.duration}s')
        print(f'  Description: {effect.description}')

def test_special_puyo_manager():
    print('\n--- Special Puyo Manager Test ---')
    
    manager = SpecialPuyoManager()
    
    print('Rarity weights:')
    total_weight = sum(manager.rarity_weights.values())
    print(f'Total weight: {total_weight:.3f}')
    
    for puyo_type, weight in sorted(manager.rarity_weights.items(), key=lambda x: x[1], reverse=True):
        percentage = (weight / total_weight) * 100
        print(f'  {puyo_type.name}: {weight:.3f} ({percentage:.1f}%)')

def test_timed_poison():
    print('\n--- Timed Poison Test ---')
    
    timed_poison = SpecialPuyo(SpecialPuyoType.TIMED_POISON, 3, 5)
    print(f'Initial countdown: {timed_poison.countdown_timer:.1f}s')
    
    # シミュレート更新
    dt = 1.0
    for i in range(10):
        result = timed_poison.update(dt)
        print(f'After {i+1}s: countdown={timed_poison.countdown_timer:.1f}s', end='')
        if result:
            print(f' -> {result["description"]}')
        else:
            print()
        
        if timed_poison.countdown_timer <= 0:
            break

def test_spawn_rates():
    print('\n--- Spawn Rate Simulation ---')
    
    manager = SpecialPuyoManager()
    spawn_counts = {}
    
    # 1000回のスポーン試行
    trials = 1000
    spawned = 0
    
    for _ in range(trials):
        if manager.should_spawn_special_puyo():
            spawned += 1
            puyo_type = manager.get_random_special_type()
            spawn_counts[puyo_type] = spawn_counts.get(puyo_type, 0) + 1
    
    print(f'Special puyo spawned: {spawned}/{trials} ({spawned/trials*100:.1f}%)')
    print('Spawn distribution:')
    
    for puyo_type, count in sorted(spawn_counts.items(), key=lambda x: x[1], reverse=True):
        percentage = (count / spawned) * 100 if spawned > 0 else 0
        expected_percentage = manager.rarity_weights[puyo_type] / sum(manager.rarity_weights.values()) * 100
        print(f'  {puyo_type.name}: {count} ({percentage:.1f}%, expected: {expected_percentage:.1f}%)')

def test_battle_effects():
    print('\n--- Battle Effect Simulation ---')
    
    # バフぷよのテスト
    buff_puyo = SpecialPuyo(SpecialPuyoType.BUFF, 2, 3)
    buff_effect = buff_puyo.trigger_effect()
    print(f'Buff effect: {buff_effect["description"]}')
    
    # 呪いぷよのテスト
    curse_puyo = SpecialPuyo(SpecialPuyoType.CURSE, 1, 4)
    curse_effect = curse_puyo.trigger_effect()
    print(f'Curse effect: {curse_effect["description"]}')
    
    # 反射ぷよのテスト
    reflect_puyo = SpecialPuyo(SpecialPuyoType.REFLECT, 4, 2)
    reflect_effect = reflect_puyo.trigger_effect()
    print(f'Reflect effect: {reflect_effect["description"]}')

if __name__ == "__main__":
    test_new_special_puyos()
    test_special_puyo_manager()
    test_timed_poison()
    test_spawn_rates()
    test_battle_effects()
    print('\n=== SPECIAL PUYO TEST COMPLETE ===')