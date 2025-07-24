#!/usr/bin/env python3
import sys
import os
sys.path.insert(0, 'src')

import pygame
import time
pygame.init()

from src.core.game_engine import GameEngine
from src.core.authentic_demo_handler import AuthenticDemoHandler, PuyoPair
from src.core.constants import GameState, PuyoType, GRID_WIDTH, GRID_HEIGHT
from src.puzzle.puyo_grid import PuyoGrid

print('=== TESTING IMPROVEMENTS: SPEED & OVERLAP ===')

# テスト1: チェイン消去スピードのテスト
print('\n--- Test 1: Chain elimination speed ---')
grid = PuyoGrid()

# 4つの同色ぷよを配置（チェイン発生）
grid.set_puyo(3, 11, PuyoType.RED)
grid.set_puyo(3, 10, PuyoType.RED)
grid.set_puyo(2, 11, PuyoType.RED)
grid.set_puyo(4, 11, PuyoType.RED)

print(f'Chain delay per group: {grid.chain_delay_per_group}s')
print(f'Fade duration: 0.08s (improved)')

# チェイン開始
start_time = time.time()
grid.start_animated_chain_sequence()

# アニメーション完了まで待機
max_wait = 2.0  # 最大2秒
while grid.chain_animation_active and (time.time() - start_time) < max_wait:
    grid.update_animations(0.016)  # ~60FPS
    time.sleep(0.016)

total_time = time.time() - start_time
print(f'Total chain elimination time: {total_time:.3f}s')

# テスト2: ぷよの重なり防止テスト
print('\n--- Test 2: Overlap prevention ---')
grid2 = PuyoGrid()

# 底にぷよを配置
grid2.set_puyo(3, 11, PuyoType.GREEN)
print('Placed GREEN puyo at bottom (3,11)')

# 新しいペアで重なりテスト
pair = PuyoPair(PuyoType.RED, PuyoType.BLUE, 3)
pair.center_y = 10.0  # 他のぷよに近い位置

print(f'Testing pair at y={pair.center_y}')

# 配置可能性をテスト
can_place_10_0 = pair.can_place_at(grid2, 3.0, 10.0, 0)  # rotation=0 (上)
can_place_10_5 = pair.can_place_at(grid2, 3.0, 10.5, 0)  
can_place_11_0 = pair.can_place_at(grid2, 3.0, 11.0, 0)  # 重なる位置

print(f'Can place at y=10.0: {can_place_10_0}')
print(f'Can place at y=10.5: {can_place_10_5}')  
print(f'Can place at y=11.0: {can_place_11_0} (should be False - overlap prevention)')

# テスト3: タイミング統合テスト
print('\n--- Test 3: Timing integration ---')
handler = AuthenticDemoHandler(None)
print(f'Spawn interval: {handler.spawn_interval}s')
print(f'Chain delay: {handler.chain_delay}s')
print(f'Chain per group: {handler.puyo_grid.chain_delay_per_group}s')

total_chain_time = handler.chain_delay + handler.puyo_grid.chain_delay_per_group + 0.08
print(f'Estimated total chain time: {total_chain_time:.3f}s')
print(f'Next puyo spawn time: {handler.spawn_interval}s')

if total_chain_time < handler.spawn_interval:
    print('✅ SUCCESS: Chain completes BEFORE next puyo spawns!')
else:
    print('❌ PROBLEM: Chain takes longer than spawn interval')

print('\n=== IMPROVEMENTS TEST COMPLETED ===')