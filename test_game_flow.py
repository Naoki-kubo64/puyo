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

print('=== FINAL INTEGRATION TEST ===')

# AuthenticDemoHandlerを作成
engine = GameEngine()
handler = AuthenticDemoHandler(engine)

print(f'Current settings:')
print(f'  Spawn interval: {handler.spawn_interval}s')
print(f'  Chain delay: {handler.chain_delay}s') 
print(f'  Chain per group: {handler.puyo_grid.chain_delay_per_group}s')
print(f'  Fade duration: 0.08s')

total_time = handler.chain_delay + handler.puyo_grid.chain_delay_per_group + 0.08
print(f'\nEstimated chain completion: {total_time:.3f}s')
print(f'Next puyo spawn delay: {handler.spawn_interval}s')

if total_time <= handler.spawn_interval:
    print('SUCCESS: Chain will complete before next puyo!')
    margin = handler.spawn_interval - total_time
    print(f'Safety margin: {margin:.3f}s')
else:
    deficit = total_time - handler.spawn_interval
    print(f'PROBLEM: Chain exceeds spawn interval by {deficit:.3f}s')

# 重なり防止テスト
print(f'\n--- Overlap Prevention Test ---')
grid = PuyoGrid()

# 底に固定ぷよを配置
grid.set_puyo(3, 11, PuyoType.GREEN)
grid.set_puyo(2, 11, PuyoType.YELLOW)

# 新しいペアでテスト
pair = PuyoPair(PuyoType.RED, PuyoType.BLUE, 3)

# 様々な位置でテスト
test_positions = [9.0, 9.5, 10.0, 10.5, 11.0]
for y_pos in test_positions:
    can_place = pair.can_place_at(grid, 3.0, y_pos, 0)
    main_pos = (3, int(y_pos))
    sub_pos = (3, int(y_pos) - 1)
    status = "OK" if can_place else "BLOCKED"
    print(f'  y={y_pos}: {status} (main={main_pos}, sub={sub_pos})')

print(f'\n=== INTEGRATION TEST COMPLETE ===')