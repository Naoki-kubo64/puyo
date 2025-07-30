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

print('=== VISUAL OVERLAP PREVENTION TEST ===')

# 視覚的重なり防止テスト
grid = PuyoGrid()

# 既存のぷよを配置
grid.set_puyo(3, 11, PuyoType.GREEN)
grid.set_puyo(3, 10, PuyoType.YELLOW)
print('Placed existing puyos: GREEN at (3,11), YELLOW at (3,10)')

# 落下中のペアを作成
pair = PuyoPair(PuyoType.RED, PuyoType.BLUE, 3)

# 様々な浮動小数点位置でのテスト
test_positions = [
    10.0,   # 正確に既存のぷよの位置
    10.1,   # 既存のぷよに近い位置
    10.4,   # 中間位置
    10.6,   # 既存のぷよに非常に近い位置
    10.9,   # ほぼ次のグリッドに近い位置
    11.0,   # 底の既存のぷよと同じ位置
]

print('\n--- 視覚的重なり防止テスト ---')
# 描画面を作成（テスト用）
test_surface = pygame.Surface((800, 600))

for i, y_pos in enumerate(test_positions):
    print(f'\nTest {i+1}: center_y = {y_pos}')
    pair.center_y = y_pos
    
    # 描画位置を計算
    grid_x = int(round(pair.center_x + 1e-10))
    grid_y = int(round(pair.center_y + 1e-10))
    
    print(f'  Floating position: ({pair.center_x:.1f}, {pair.center_y:.1f})')
    print(f'  Snapped to grid: ({grid_x}, {grid_y})')
    
    # 軸ぷよの描画可能性
    main_can_render = grid.can_place_puyo(grid_x, grid_y) if grid_y >= 0 else True
    print(f'  Main puyo can render: {main_can_render}')
    
    # 子ぷよの描画可能性
    sub_x, sub_y = grid_x, grid_y - 1
    sub_can_render = grid.can_place_puyo(sub_x, sub_y) if sub_y >= 0 else True
    print(f'  Sub puyo can render: {sub_can_render}')
    
    # 描画をシミュレート（実際の描画処理を呼び出し）
    try:
        pair.render(test_surface, grid)
        print(f'  Render completed successfully')
    except Exception as e:
        print(f'  Render error: {e}')

print('\n--- 重なり状況の確認 ---')
print(f'Grid state at column 3:')
for y in range(8, 12):
    puyo = grid.get_puyo(3, y)
    if puyo and puyo != PuyoType.EMPTY:
        print(f'  (3, {y}): {puyo.name}')
    else:
        print(f'  (3, {y}): EMPTY')

print('\n--- 期待される動作 ---')
print('✓ 既存のぷよがある位置では描画をスキップ')
print('✓ 浮動小数点位置は整数グリッドにスナップ')
print('✓ 視覚的な重なりが完全に防止される')

print('\n=== VISUAL OVERLAP PREVENTION TEST COMPLETE ===')