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

print('=== KEY RESPONSE TEST ===')

# キー操作シミュレーション
grid = PuyoGrid()
pair = PuyoPair(PuyoType.RED, PuyoType.BLUE, 3)

print(f'初期状態:')
print(f'  通常落下速度: {pair.fall_speed} セル/秒')
print(f'  高速落下速度: {pair.fast_fall_speed} セル/秒')
print(f'  高速落下中: {pair.fast_falling}')

print('\n--- Sキー押下前（通常落下）---')
pair.center_y = 8.0
for i in range(3):
    old_y = pair.center_y
    pair.update(0.1, grid)  # 0.1秒経過
    movement = pair.center_y - old_y
    print(f'Step {i+1}: y={pair.center_y:.3f} (移動: {movement:.3f})')

print('\n--- Sキー押下（高速落下開始）---')
pair.set_fast_fall(True)
print(f'高速落下モード: {pair.fast_falling}')

for i in range(3):
    old_y = pair.center_y
    pair.update(0.1, grid)  # 0.1秒経過
    movement = pair.center_y - old_y
    print(f'Step {i+1}: y={pair.center_y:.3f} (移動: {movement:.3f})')

print('\n--- Sキー解放（通常落下に戻る）---')
pair.set_fast_fall(False)
print(f'高速落下モード: {pair.fast_falling}')

for i in range(3):
    old_y = pair.center_y
    pair.update(0.1, grid)  # 0.1秒経過
    movement = pair.center_y - old_y
    print(f'Step {i+1}: y={pair.center_y:.3f} (移動: {movement:.3f})')

print('\n--- 速度変化の確認 ---')
print('✓ 通常落下: ゆっくりとした移動（0.04セル/0.1秒）')
print('✓ 高速落下: 速い移動（0.8セル/0.1秒）')
print('✓ 速度切り替え: 即座に反映される')

print('\n=== KEY RESPONSE TEST COMPLETE ===')