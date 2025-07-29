#!/usr/bin/env python3
"""
落下中の特殊ぷよアイコン表示テスト
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

print('=== Falling Icon Display Test ===')

# テスト環境をセットアップ
engine = GameEngine()
handler = AuthenticDemoHandler(engine)

print('Creating pair with guaranteed special puyos...')

# ペアを作成（100%確率で特殊ぷよが生成される）
pair = PuyoPair(PuyoType.RED, PuyoType.BLUE, 3, None, None, handler)
print(f'Pair created: main_special={pair.main_special}, sub_special={pair.sub_special}')

if not pair.main_special and not pair.sub_special:
    print('ERROR: No special puyos generated despite 100% rate!')
    pygame.quit()
    exit(1)

# 落下中の描画テスト
print('\n=== Falling Rendering Test ===')

# 落下状態を設定
pair.center_y = 5.0
pair.active = True
pair.grounded = False

# テスト用サーフェスを作成
test_surface = pygame.Surface((800, 600))
test_surface.fill((50, 50, 50))  # ダークグレー背景

print('Testing falling pair rendering...')

try:
    # 落下中のペア描画
    pair.render(test_surface, handler.puyo_grid)
    print('SUCCESS: Falling pair rendered without errors')
    
    # 画像を保存してデバッグ用に確認
    pygame.image.save(test_surface, 'debug_falling_render.png')
    print('DEBUG: Saved falling render to debug_falling_render.png')
    
except Exception as e:
    print(f'ERROR: Falling pair rendering failed: {e}')
    import traceback
    traceback.print_exc()

# 位置情報の詳細確認
main_pos, sub_pos = pair.get_positions()
print(f'Positions: main=({main_pos[0]}, {main_pos[1]}), sub=({sub_pos[0]}, {sub_pos[1]})')

# 特殊ぷよタイプの詳細確認
print(f'Special types: main={pair.main_special}, sub={pair.sub_special}')

# PuyoGridの特殊ぷよ画像確認
if hasattr(handler.puyo_grid, 'special_puyo_images'):
    print(f'Available special images: {list(handler.puyo_grid.special_puyo_images.keys())}')
else:
    print('ERROR: PuyoGrid has no special_puyo_images!')

print('\n=== Test Complete ===')

if pair.main_special or pair.sub_special:
    print('SUCCESS: Special puyos should be visible during falling')
else:
    print('FAILED: No special puyos to test')

pygame.quit()