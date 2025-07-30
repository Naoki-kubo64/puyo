#!/usr/bin/env python3
"""
特殊ぷよアイコン表示タイミングテスト
レコーディング 2025-07-29 112315.mp4 の問題を検証
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
from special_puyo.special_puyo import SpecialPuyoType, special_puyo_manager

logging.basicConfig(level=logging.DEBUG)

print('=== 特殊ぷよ表示タイミングテスト ===')

# テスト環境をセットアップ
engine = GameEngine()
handler = AuthenticDemoHandler(engine)

# 特殊ぷよを持つPuyoPairを作成
print('特殊ぷよペアを作成中...')
pair = PuyoPair(PuyoType.RED, PuyoType.BLUE, 3, SpecialPuyoType.HEAL, SpecialPuyoType.BOMB, handler)
print(f'✓ ペア作成完了: main_special={pair.main_special}, sub_special={pair.sub_special}')

# 落下中→着地プロセスをシミュレート
print('\n=== 落下シミュレーション開始 ===')

# 1. 落下中状態
pair.center_y = 5.0
pair.active = True
pair.grounded = False
print(f'落下中: center_y={pair.center_y}, active={pair.active}, grounded={pair.grounded}')

# 特殊ぷよマネージャーの現在状態を確認
main_pos, sub_pos = pair.get_positions()
main_x, main_y = main_pos
sub_x, sub_y = sub_pos

print(f'ペア位置: main=({main_x}, {main_y}), sub=({sub_x}, {sub_y})')

# 2. 着地直前状態（グラウンド判定）
print('\n--- 着地直前 ---')
pair.grounded = True
pair.grounded_timer = 0.0
print(f'着地直前: grounded={pair.grounded}, grounded_timer={pair.grounded_timer}')

# 特殊ぷよがマネージャーに登録されているかチェック
before_lock_main = special_puyo_manager.get_special_puyo(main_x, main_y)
before_lock_sub = special_puyo_manager.get_special_puyo(sub_x, sub_y)
print(f'固定前マネージャー状態: main={before_lock_main}, sub={before_lock_sub}')

# 3. 事前登録処理（新機能テスト）
print('\n--- 事前登録処理実行 ---')
pair._pre_register_special_puyos(handler.puyo_grid)

# 事前登録後の状態確認
after_prereg_main = special_puyo_manager.get_special_puyo(main_x, main_y)
after_prereg_sub = special_puyo_manager.get_special_puyo(sub_x, sub_y)
print(f'事前登録後マネージャー状態: main={after_prereg_main}, sub={after_prereg_sub}')

# 4. 実際の固定処理
print('\n--- 固定処理実行 ---')
result = pair._execute_pair_lock(handler.puyo_grid)
print(f'固定処理結果: {result}')

# 5. 固定後の状態確認
after_lock_main = special_puyo_manager.get_special_puyo(main_x, main_y)
after_lock_sub = special_puyo_manager.get_special_puyo(sub_x, sub_y)
print(f'固定後マネージャー状態: main={after_lock_main}, sub={after_lock_sub}')

# 6. グリッドの状態確認
print('\n--- グリッド状態確認 ---')
grid_main = handler.puyo_grid.grid[main_y][main_x] if 0 <= main_y < 12 and 0 <= main_x < 6 else None
grid_sub = handler.puyo_grid.grid[sub_y][sub_x] if 0 <= sub_y < 12 and 0 <= sub_x < 6 else None
print(f'グリッド状態: main={grid_main}, sub={grid_sub}')

print('\n=== テスト完了 ===')

# 結果判定
success = True
if pair.main_special and not after_prereg_main:
    print('❌ FAILED: 軸特殊ぷよが事前登録されていない')
    success = False
if pair.sub_special and not after_prereg_sub:
    print('❌ FAILED: 子特殊ぷよが事前登録されていない') 
    success = False

if success:
    print('✅ SUCCESS: 特殊ぷよ事前登録が正常に動作')
else:
    print('❌ FAILED: 特殊ぷよ事前登録に問題あり')

pygame.quit()