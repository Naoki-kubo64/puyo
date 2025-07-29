#!/usr/bin/env python3
"""
特殊ぷよアイコンの一貫性テスト - 落下中と着地後で同じアイコンが表示されるかチェック
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

logging.basicConfig(level=logging.DEBUG)

print('=== Icon Consistency Test ===')

# テスト環境をセットアップ
engine = GameEngine()
handler = AuthenticDemoHandler(engine)

print('Testing icon consistency between falling and landed states...')

# 特殊ぷよを持つペアを生成
pair = PuyoPair(PuyoType.RED, PuyoType.BLUE, 3, None, None, handler)
print(f'Generated pair: main_special={pair.main_special}, sub_special={pair.sub_special}')

if not pair.main_special and not pair.sub_special:
    print('No special puyos generated - cannot test consistency')
    pygame.quit()
    exit(1)

# 1. 落下中の状態確認
print('\n=== Phase 1: Falling State ===')
pair.center_y = 5.0
pair.active = True
pair.grounded = False

main_pos, sub_pos = pair.get_positions()
main_x, main_y = main_pos
sub_x, sub_y = sub_pos

print(f'Falling positions: main=({main_x}, {main_y}), sub=({sub_x}, {sub_y})')
print(f'Falling special types: main={pair.main_special}, sub={pair.sub_special}')

# 落下中のレンダリングテスト
test_surface = pygame.Surface((400, 600))
test_surface.fill((40, 40, 40))

try:
    pair.render(test_surface, handler.puyo_grid)
    pygame.image.save(test_surface, 'debug_falling_consistency.png')
    print('✓ Falling render successful - saved to debug_falling_consistency.png')
except Exception as e:
    print(f'✗ Falling render failed: {e}')

# 2. 事前登録の確認
print('\n=== Phase 2: Pre-registration ===')
print('Before pre-registration:')
grid_main_before = handler.puyo_grid.get_special_puyo_data(main_x, main_y)
grid_sub_before = handler.puyo_grid.get_special_puyo_data(sub_x, sub_y)
print(f'  Grid data: main={grid_main_before}, sub={grid_sub_before}')

# 事前登録を実行
pair._pre_register_special_puyos(handler.puyo_grid)

print('After pre-registration:')
grid_main_after = handler.puyo_grid.get_special_puyo_data(main_x, main_y)
grid_sub_after = handler.puyo_grid.get_special_puyo_data(sub_x, sub_y)
print(f'  Grid data: main={grid_main_after}, sub={grid_sub_after}')

# 3. 着地状態確認
print('\n=== Phase 3: Landed State ===')

# 通常のぷよも配置
handler.puyo_grid.set_puyo(main_x, main_y, pair.main_type)
handler.puyo_grid.set_puyo(sub_x, sub_y, pair.sub_type)

# 着地後のレンダリングテスト
test_surface2 = pygame.Surface((400, 600))
test_surface2.fill((40, 40, 40))

try:
    handler.puyo_grid.render(test_surface2)
    pygame.image.save(test_surface2, 'debug_landed_consistency.png')
    print('✓ Landed render successful - saved to debug_landed_consistency.png')
except Exception as e:
    print(f'✗ Landed render failed: {e}')

# 4. 一貫性チェック
print('\n=== Phase 4: Consistency Check ===')

consistency_ok = True

# 軸ぷよの一貫性チェック
if pair.main_special:
    if grid_main_after == pair.main_special:
        print(f'✓ Main special consistency OK: {pair.main_special.value}')
    else:
        print(f'✗ Main special inconsistency: Pair={pair.main_special}, Grid={grid_main_after}')
        consistency_ok = False

# 子ぷよの一貫性チェック
if pair.sub_special:
    if grid_sub_after == pair.sub_special:
        print(f'✓ Sub special consistency OK: {pair.sub_special.value}')
    else:
        print(f'✗ Sub special inconsistency: Pair={pair.sub_special}, Grid={grid_sub_after}')
        consistency_ok = False

print('\n=== Test Result ===')
if consistency_ok:
    print('SUCCESS: Icon consistency maintained between falling and landed states')
else:
    print('FAILED: Icon consistency problem detected')

print('Check debug_falling_consistency.png and debug_landed_consistency.png for visual comparison')

pygame.quit()