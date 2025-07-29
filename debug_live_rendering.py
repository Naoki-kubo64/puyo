#!/usr/bin/env python3
"""
リアルタイム描画デバッグ - 実際のゲーム状況で特殊ぷよ表示を確認
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

import pygame
import logging
from core.game_engine import GameEngine
from core.constants import GameState

# ログレベルを設定
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def main():
    print("=== Live Special Puyo Rendering Debug ===")
    
    # ゲームエンジンを初期化
    engine = GameEngine()
    
    # ゲームを開始（デモモードに移行）
    engine.change_state(GameState.PLAYING)
    
    print("Game started. Press ESC to exit, SPACE to force drop special puyo.")
    print("Monitor console for special puyo rendering debug info.")
    
    # メインループを実行（10秒後に自動終了）
    clock = pygame.time.Clock()
    start_time = pygame.time.get_ticks()
    
    while True:
        current_time = pygame.time.get_ticks()
        
        # 10秒で自動終了
        if current_time - start_time > 10000:
            print("Auto-exit after 10 seconds")
            break
            
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return
                elif event.key == pygame.K_SPACE:
                    # 強制的に特殊ぷよ落下をトリガー
                    print("Forcing special puyo drop...")
                    # デモハンドラーにアクセスして特殊ぷよを強制生成
                    current_handler = engine.current_handler
                    if hasattr(current_handler, 'current_pair') and current_handler.current_pair:
                        pair = current_handler.current_pair
                        print(f"Current pair specials: main={pair.main_special}, sub={pair.sub_special}")
                        print(f"Pair position: center_y={pair.center_y}, active={pair.active}")
                        print(f"Pair grounded: {pair.grounded}, timer={pair.grounded_timer}")
            
            engine.handle_event(event)
        
        dt = clock.tick(60) / 1000.0
        engine.update(dt)
        engine.render()
        
    pygame.quit()

if __name__ == "__main__":
    main()