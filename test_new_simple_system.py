#!/usr/bin/env python3
"""
新しいシンプル特殊ぷよシステムのテスト
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

print('=== Simple Special Puyo System Test ===')

# テスト環境をセットアップ
engine = GameEngine()
handler = AuthenticDemoHandler(engine)

print('Creating pair with new simple system...')

# ペアを作成（新しいシステムで特殊ぷよが自動決定される）
pair = PuyoPair(PuyoType.RED, PuyoType.BLUE, 3)
print(f'Pair created: main_special={pair.main_special}, sub_special={pair.sub_special}')

# 落下から着地のプロセスをシミュレート
print('\n=== Falling to Landing Simulation ===')

# 1. 落下中状態
pair.center_y = 5.0
pair.active = True
pair.grounded = False
print(f'Falling: center_y={pair.center_y}, active={pair.active}')

# 特殊ぷよマネージャーの状態確認
main_pos, sub_pos = pair.get_positions()
main_x, main_y = main_pos
sub_x, sub_y = sub_pos
print(f'Positions: main=({main_x}, {main_y}), sub=({sub_x}, {sub_y})')

# 2. 着地直前
pair.grounded = True
pair.grounded_timer = 0.0
print(f'Landing: grounded={pair.grounded}')

# 事前登録前の状態確認
before_main = simple_special_manager.get_special_puyo(main_x, main_y)
before_sub = simple_special_manager.get_special_puyo(sub_x, sub_y)
print(f'Before pre-registration: main={before_main}, sub={before_sub}')

# 3. 事前登録実行
print('\n--- Pre-registration ---')
pair._pre_register_special_puyos(handler.puyo_grid)

# 事前登録後の状態確認
after_main = simple_special_manager.get_special_puyo(main_x, main_y)
after_sub = simple_special_manager.get_special_puyo(sub_x, sub_y)
print(f'After pre-registration: main={after_main}, sub={after_sub}')

# 描画テスト
print('\n--- Rendering Test ---')
test_surface = pygame.Surface((800, 600))
test_surface.fill((0, 0, 0))

try:
    # ペアの描画（落下中）
    pair.render(test_surface, handler.puyo_grid)
    print('SUCCESS: Pair rendering completed without errors')
    
    # グリッドの描画（着地後）
    handler.puyo_grid.render(test_surface)
    print('SUCCESS: Grid rendering completed without errors')
    
except Exception as e:
    print(f'ERROR: Rendering failed: {e}')
    import traceback
    traceback.print_exc()

print('\n=== Test Complete ===')

# 結果判定
success = True
if pair.main_special and not after_main:
    print('FAILED: Main special puyo not pre-registered')
    success = False
if pair.sub_special and not after_sub:
    print('FAILED: Sub special puyo not pre-registered') 
    success = False

if success:
    print('SUCCESS: New simple special puyo system working correctly')
else:
    print('FAILED: New simple special puyo system has issues')

pygame.quit()