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

print('=== DETAILED OVERLAP INVESTIGATION ===')

# 複雑な重なりシナリオのテスト
grid = PuyoGrid()

# シナリオ1: 他のぷよに乗る場合
print('\n--- Scenario 1: Landing on existing puyo ---')
grid.set_puyo(3, 11, PuyoType.GREEN)  # 底に緑ぷよ
print('Placed GREEN at (3,11)')

pair = PuyoPair(PuyoType.RED, PuyoType.BLUE, 3)

# 詳細テスト - 様々な浮動小数点位置
test_positions = [
    9.0, 9.1, 9.2, 9.3, 9.4, 9.5, 9.6, 9.7, 9.8, 9.9,
    10.0, 10.1, 10.2, 10.3, 10.4, 10.5, 10.6, 10.7, 10.8, 10.9,
    11.0, 11.1, 11.2
]

print('Testing floating point positions:')
for y_pos in test_positions:
    can_place = pair.can_place_at(grid, 3.0, y_pos, 0)
    main_pos = (3, int(round(y_pos)))
    sub_pos = (3, int(round(y_pos)) - 1)
    
    # グリッドの状態をチェック
    main_blocked = not grid.can_place_puyo(main_pos[0], main_pos[1]) if main_pos[1] >= 0 else False
    sub_blocked = not grid.can_place_puyo(sub_pos[0], sub_pos[1]) if sub_pos[1] >= 0 else False
    
    status = "OK" if can_place else "BLOCKED"
    details = f"main={'BLOCKED' if main_blocked else 'OK'}, sub={'BLOCKED' if sub_blocked else 'OK'}"
    
    if not can_place or main_blocked or sub_blocked:
        print(f'  y={y_pos:4.1f}: {status:7} -> main={main_pos}, sub={sub_pos} ({details})')

# シナリオ2: 実際の落下シミュレーション
print('\n--- Scenario 2: Falling simulation ---')
grid2 = PuyoGrid()
grid2.set_puyo(3, 11, PuyoType.GREEN)  # 底に緑ぷよ
grid2.set_puyo(2, 11, PuyoType.YELLOW)  # 隣にも配置

pair2 = PuyoPair(PuyoType.RED, PuyoType.BLUE, 3)
pair2.center_y = 8.0  # 上から開始
pair2.fall_speed = 1.0

print(f'Starting fall simulation from y={pair2.center_y}')
for frame in range(20):
    old_y = pair2.center_y
    
    # 手動で落下処理をシミュレート
    target_y = pair2.center_y + pair2.fall_speed * 0.1
    step_size = 0.05
    
    # ステップごとに安全に落下
    current_y = pair2.center_y
    while current_y < target_y:
        next_y = min(current_y + step_size, target_y)
        
        if pair2.can_place_at(grid2, pair2.center_x, next_y, pair2.rotation):
            current_y = next_y
        else:
            break
    
    pair2.center_y = current_y
    
    can_place = pair2.can_place_at(grid2, pair2.center_x, pair2.center_y, pair2.rotation)
    main_pos, sub_pos = pair2.get_positions()
    
    if abs(pair2.center_y - old_y) < 0.001:  # 停止した
        print(f'Frame {frame+1:2}: STOPPED at y={pair2.center_y:.3f}, main={main_pos}, sub={sub_pos}, can_place={can_place}')
        break
    else:
        print(f'Frame {frame+1:2}: y={pair2.center_y:.3f}, main={main_pos}, sub={sub_pos}, can_place={can_place}')

# シナリオ3: 回転時の重なりチェック
print('\n--- Scenario 3: Rotation overlap test ---')
grid3 = PuyoGrid()
grid3.set_puyo(2, 10, PuyoType.GREEN)  # 左に障害物
grid3.set_puyo(4, 10, PuyoType.YELLOW)  # 右に障害物

pair3 = PuyoPair(PuyoType.RED, PuyoType.BLUE, 3)
pair3.center_y = 10.0

print('Testing rotations near obstacles:')
for rotation in range(4):
    can_place = pair3.can_place_at(grid3, 3.0, 10.0, rotation)
    
    # 手動で位置計算
    main_x, main_y = 3, 10
    offsets = [(0, -1), (1, 0), (0, 1), (-1, 0)]
    offset_x, offset_y = offsets[rotation]
    sub_x, sub_y = main_x + offset_x, main_y + offset_y
    
    status = "OK" if can_place else "BLOCKED"
    print(f'  Rotation {rotation}: {status:7} -> main=({main_x},{main_y}), sub=({sub_x},{sub_y})')

print('\n=== DETAILED OVERLAP INVESTIGATION COMPLETE ===')