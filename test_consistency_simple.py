#!/usr/bin/env python3
"""
シンプルな特殊ぷよアイコン一貫性テスト
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

print('=== Simple Consistency Test ===')

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

# 位置確認
main_pos, sub_pos = pair.get_positions()
main_x, main_y = main_pos
sub_x, sub_y = sub_pos

print(f'Positions: main=({main_x}, {main_y}), sub=({sub_x}, {sub_y})')

# 事前登録テスト
print('\n--- Testing pre-registration ---')
pair._pre_register_special_puyos(handler.puyo_grid)

# グリッドデータ確認
grid_main = handler.puyo_grid.get_special_puyo_data(main_x, main_y)
grid_sub = handler.puyo_grid.get_special_puyo_data(sub_x, sub_y)

print(f'Grid data after registration: main={grid_main}, sub={grid_sub}')

# 一貫性チェック
consistent = True

if pair.main_special and grid_main != pair.main_special:
    print(f'INCONSISTENT: Main puyo {pair.main_special} != {grid_main}')
    consistent = False

if pair.sub_special and grid_sub != pair.sub_special:
    print(f'INCONSISTENT: Sub puyo {pair.sub_special} != {grid_sub}')
    consistent = False

if consistent:
    print('SUCCESS: Icon consistency maintained')
else:
    print('FAILED: Icon consistency problem')

# 描画テスト
print('\n--- Testing rendering ---')
test_surface = pygame.Surface((400, 600))
test_surface.fill((50, 50, 50))

# 落下中描画
pair.center_y = 5.0
pair.active = True
pair.render(test_surface, handler.puyo_grid)

# 着地後描画
handler.puyo_grid.set_puyo(main_x, main_y, pair.main_type)
handler.puyo_grid.set_puyo(sub_x, sub_y, pair.sub_type)
handler.puyo_grid.render(test_surface)

pygame.image.save(test_surface, 'debug_consistency_final.png')
print('Saved combined render to debug_consistency_final.png')

print('\n=== Test Complete ===')

pygame.quit()