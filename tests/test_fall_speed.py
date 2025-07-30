#!/usr/bin/env python3
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

import pygame
pygame.init()

from src.core.game_engine import GameEngine
from src.core.authentic_demo_handler import AuthenticDemoHandler, PuyoPair
from src.core.constants import GameState, PuyoType, GRID_WIDTH, GRID_HEIGHT
from src.puzzle.puyo_grid import PuyoGrid

print('=== FALL SPEED TEST ===')

# 落下速度テスト
grid = PuyoGrid()
pair = PuyoPair(PuyoType.RED, PuyoType.BLUE, 3)

print(f'初期設定:')
print(f'  通常落下速度: {pair.fall_speed} セル/秒')
print(f'  高速落下速度: {pair.fast_fall_speed} セル/秒')
print(f'  初期位置: y={pair.center_y}')

print('\n--- 通常落下シミュレーション (1秒間) ---')
pair.center_y = 5.0
pair.fast_falling = False

for frame in range(10):
    dt = 0.1  # 0.1秒間隔
    old_y = pair.center_y
    pair.update(dt, grid)
    movement = pair.center_y - old_y
    print(f'Frame {frame+1:2}: y={pair.center_y:.3f} (移動: {movement:.3f})')
    
    if not pair.active:
        print('着地により停止')
        break

print('\n--- 高速落下シミュレーション (1秒間) ---')
pair2 = PuyoPair(PuyoType.GREEN, PuyoType.YELLOW, 3)
pair2.center_y = 5.0
pair2.fast_falling = True

for frame in range(10):
    dt = 0.1  # 0.1秒間隔
    old_y = pair2.center_y
    pair2.update(dt, grid)
    movement = pair2.center_y - old_y
    print(f'Frame {frame+1:2}: y={pair2.center_y:.3f} (移動: {movement:.3f})')
    
    if not pair2.active:
        print('着地により停止')
        break

print('\n--- 速度比較 ---')
normal_speed = pair.fall_speed
fast_speed = pair2.fast_fall_speed
speed_ratio = fast_speed / normal_speed

print(f'通常落下: {normal_speed} セル/秒')
print(f'高速落下: {fast_speed} セル/秒')
print(f'速度比: {speed_ratio:.1f}倍')

if normal_speed <= 0.5:
    print('✓ 通常落下速度は適切（0.5セル/秒以下）')
else:
    print('⚠ 通常落下速度が速すぎる可能性')

if 6.0 <= fast_speed <= 10.0:
    print('✓ 高速落下速度は適切（6-10セル/秒）')
else:
    print('⚠ 高速落下速度の調整が必要')

print('\n=== FALL SPEED TEST COMPLETE ===')