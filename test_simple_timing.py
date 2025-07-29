#!/usr/bin/env python3
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

logging.basicConfig(level=logging.INFO)

print('=== Special Puyo Display Timing Test ===')

# Setup test environment
engine = GameEngine()
handler = AuthenticDemoHandler(engine)

# Create pair with special puyos
print('Creating special puyo pair...')
pair = PuyoPair(PuyoType.RED, PuyoType.BLUE, 3, SpecialPuyoType.HEAL, SpecialPuyoType.BOMB, handler)
print(f'Pair created: main_special={pair.main_special}, sub_special={pair.sub_special}')

# Simulate falling to landing process
print('\n=== Falling Simulation ===')

# 1. Falling state
pair.center_y = 5.0
pair.active = True
pair.grounded = False
print(f'Falling: center_y={pair.center_y}, active={pair.active}, grounded={pair.grounded}')

# Check positions
main_pos, sub_pos = pair.get_positions()
main_x, main_y = main_pos
sub_x, sub_y = sub_pos
print(f'Positions: main=({main_x}, {main_y}), sub=({sub_x}, {sub_y})')

# 2. Just before landing
print('\n--- Just before landing ---')
pair.grounded = True
pair.grounded_timer = 0.0
print(f'Before landing: grounded={pair.grounded}, grounded_timer={pair.grounded_timer}')

# Check manager state before locking
before_lock_main = special_puyo_manager.get_special_puyo(main_x, main_y)
before_lock_sub = special_puyo_manager.get_special_puyo(sub_x, sub_y)
print(f'Before lock manager state: main={before_lock_main}, sub={before_lock_sub}')

# 3. Pre-registration (NEW FEATURE TEST)
print('\n--- Pre-registration process ---')
pair._pre_register_special_puyos(handler.puyo_grid)

# Check state after pre-registration
after_prereg_main = special_puyo_manager.get_special_puyo(main_x, main_y)
after_prereg_sub = special_puyo_manager.get_special_puyo(sub_x, sub_y)
print(f'After pre-registration: main={after_prereg_main}, sub={after_prereg_sub}')

# 4. Actual locking process
print('\n--- Lock process ---')
result = pair._execute_pair_lock(handler.puyo_grid)
print(f'Lock result: {result}')

# 5. Final state check
after_lock_main = special_puyo_manager.get_special_puyo(main_x, main_y)
after_lock_sub = special_puyo_manager.get_special_puyo(sub_x, sub_y)
print(f'After lock: main={after_lock_main}, sub={after_lock_sub}')

print('\n=== Test Complete ===')

# Result evaluation
success = True
if pair.main_special and not after_prereg_main:
    print('FAILED: Main special puyo not pre-registered')
    success = False
if pair.sub_special and not after_prereg_sub:
    print('FAILED: Sub special puyo not pre-registered') 
    success = False

if success:
    print('SUCCESS: Special puyo pre-registration working correctly')
else:
    print('FAILED: Special puyo pre-registration has issues')

pygame.quit()