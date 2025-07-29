#!/usr/bin/env python3
"""
実際の固定処理での特殊ぷよ一貫性テスト
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

import pygame
import logging
pygame.init()

from core.authentic_demo_handler import PuyoPair, AuthenticDemoHandler
from puzzle.puyo_grid import PuyoGrid, PuyoType
from core.game_engine import GameEngine
from core.simple_special_puyo import simple_special_manager, SimpleSpecialType

logging.basicConfig(level=logging.INFO)

print('=== Actual Lock Consistency Test ===')

# テスト環境をセットアップ
engine = GameEngine()
handler = AuthenticDemoHandler(engine)

# 特殊ぷよを持つペアを生成
pair = PuyoPair(PuyoType.RED, PuyoType.BLUE, 3, None, None, handler)
print(f'Generated pair: main_special={pair.main_special}, sub_special={pair.sub_special}')

if not pair.main_special and not pair.sub_special:
    print('No special puyos - test failed')
    pygame.quit()
    exit(1)

# 着地可能な位置に移動
pair.center_y = 10.0  # グリッド内の位置
pair.active = True
pair.grounded = True

# 位置確認
main_pos, sub_pos = pair.get_positions()
main_x, main_y = main_pos
sub_x, sub_y = sub_pos

print(f'Positions before lock: main=({main_x}, {main_y}), sub=({sub_x}, {sub_y})')

# 実際の固定処理を実行
print('\n--- Executing actual lock process ---')
result = pair._execute_pair_lock(handler.puyo_grid)
print(f'Lock result: {result}')

# 固定後のグリッドデータ確認
print('\n--- Checking grid data after lock ---')
grid_main = handler.puyo_grid.get_special_puyo_data(main_x, main_y)
grid_sub = handler.puyo_grid.get_special_puyo_data(sub_x, sub_y)

print(f'Grid data after lock: main={grid_main}, sub={grid_sub}')

# 一貫性チェック
consistent = True

if pair.main_special:
    if grid_main == pair.main_special:
        print(f'SUCCESS: Main puyo consistency OK - {pair.main_special.value}')
    else:
        print(f'FAILED: Main puyo inconsistent - Pair: {pair.main_special}, Grid: {grid_main}')
        consistent = False

if pair.sub_special:
    if grid_sub == pair.sub_special:
        print(f'SUCCESS: Sub puyo consistency OK - {pair.sub_special.value}')
    else:
        print(f'FAILED: Sub puyo inconsistent - Pair: {pair.sub_special}, Grid: {grid_sub}')
        consistent = False

print('\n--- Final Result ---')
if consistent:
    print('SUCCESS: All special puyo icons consistent between falling and landed states')
else:
    print('FAILED: Consistency issues detected')

# 最終描画テスト
print('\n--- Final rendering test ---')
test_surface = pygame.Surface((400, 600))
test_surface.fill((60, 60, 60))

handler.puyo_grid.render(test_surface)
pygame.image.save(test_surface, 'debug_final_consistency.png')
print('Final render saved to debug_final_consistency.png')

pygame.quit()