#!/usr/bin/env python3
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

import pygame
pygame.init()

from core.authentic_demo_handler import PuyoPair, AuthenticDemoHandler
from puzzle.puyo_grid import PuyoGrid, PuyoType
from core.game_engine import GameEngine
from special_puyo.special_puyo import SpecialPuyoType, special_puyo_manager

print('=== SPECIAL PUYO RENDER DEBUG ===')

# テスト環境をセットアップ
engine = GameEngine()
handler = AuthenticDemoHandler(engine)

# 確実に特殊ぷよを持つPuyoPairを作成
pair = PuyoPair(PuyoType.RED, PuyoType.BLUE, 3, SpecialPuyoType.HEAL, SpecialPuyoType.BOMB, handler)
print(f'Created pair: main_special={pair.main_special}, sub_special={pair.sub_special}')

# ダミーサーフェスで描画テスト
test_surface = pygame.Surface((800, 600))
test_surface.fill((0, 0, 0))

# 落下中状態で描画
pair.center_y = 5.0  # 落下中の位置
pair.active = True

print(f'Before render: pair.active={pair.active}')
print(f'Special types: main={pair.main_special}, sub={pair.sub_special}')

# PuyoGridに特殊ぷよ画像があるかチェック
if hasattr(handler.puyo_grid, 'special_puyo_images'):
    print(f'PuyoGrid has special_puyo_images: {len(handler.puyo_grid.special_puyo_images)} images')
    for key, value in handler.puyo_grid.special_puyo_images.items():
        print(f'  {key}: {value}')
else:
    print('ERROR: PuyoGrid has no special_puyo_images attribute!')

# 実際に描画してみる
try:
    pair.render(test_surface, handler.puyo_grid)
    print('✓ Pair render executed without error')
except Exception as e:
    print(f'✗ Pair render failed: {e}')
    import traceback
    traceback.print_exc()

print('=== DEBUG COMPLETE ===')
pygame.quit()