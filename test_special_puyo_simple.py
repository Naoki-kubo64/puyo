#!/usr/bin/env python3
import sys
import os
sys.path.insert(0, 'src')

import pygame
pygame.init()

from src.special_puyo.special_puyo import SpecialPuyoType, SpecialPuyo, SpecialPuyoManager

print('=== SPECIAL PUYO SIMPLE TEST ===')

def test_new_special_puyos():
    print('New Special Puyo Types:')
    
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
        
        print(f'{puyo_type.name}: {effect.description}')

def test_manager():
    print('\nManager Test:')
    manager = SpecialPuyoManager()
    
    # 新しい特殊ぷよがランダム選択に含まれているかテスト
    for _ in range(10):
        puyo_type = manager.get_random_special_type()
        print(f'Random puyo: {puyo_type.name}')

if __name__ == "__main__":
    test_new_special_puyos()
    test_manager()
    print('=== TEST COMPLETE ===')