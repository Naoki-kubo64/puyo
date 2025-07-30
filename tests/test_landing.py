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

print('=== FINAL TEST: COMPLETE BOTTOM LANDING ===')

# 空のグリッド
grid = PuyoGrid()

# 新しいペアを上から落下させる
pair = PuyoPair(PuyoType.RED, PuyoType.BLUE, GRID_WIDTH // 2)
pair.center_y = 0.0  # 一番上から
print(f'Starting pair at: y={pair.center_y}')

# リアルタイムに近い設定
pair.fall_speed = 5.0  # 程よい速度
pair.grounded_grace_time = 0.2  # 短い猶予時間

print('\n--- Complete falling and landing test ---')
for i in range(60):  # 最大60フレーム
    dt = 0.05  # 50ms（20FPS相当）
    result = pair.update(dt, grid)
    
    # 重要なフレームのみ表示
    if i % 10 == 0 or pair.grounded or result or pair.center_y > 10.0:
        main_pos, sub_pos = pair.get_positions()
        print(f'Frame {i+1}: y={pair.center_y:.2f}, main={main_pos}, sub={sub_pos}, grounded={pair.grounded}, timer={pair.grounded_timer:.3f}, result={result}')
    
    if result:
        print('*** SUCCESS: PAIR LOCKED! ***')
        break

print(f'\nFinal result:')
print(f'Position: y={pair.center_y:.2f}')
print(f'Grounded: {pair.grounded}')
print(f'Active: {pair.active}')

# 最終位置の確認
if not pair.active:
    # グリッドの状態を確認
    print('\nGrid state after locking:')
    for y in range(8, 12):
        for x in range(2, 5):
            puyo = grid.get_puyo(x, y)
            if puyo != PuyoType.EMPTY:
                print(f'  ({x},{y}): {puyo.name}')