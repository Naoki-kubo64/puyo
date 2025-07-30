#!/usr/bin/env python3
"""
短時間ゲーム実行テスト - エラー捕捉
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

import pygame
import traceback
import signal
import time

class GameTester:
    def __init__(self):
        self.running = True
        self.error_found = False
        self.error_info = None
    
    def signal_handler(self, signum, frame):
        """シグナルハンドラー"""
        print("\nTest interrupted by user")
        self.running = False
    
    def test_game_run(self, duration=5):
        """ゲームを短時間実行してエラーをキャッチ"""
        print(f"=== RUNNING GAME FOR {duration} SECONDS ===")
        
        try:
            # シグナルハンドラーを設定
            signal.signal(signal.SIGINT, self.signal_handler)
            
            from core.game_engine import GameEngine
            from core.constants import GameState
            from core.menu_handler import MenuHandler
            
            # ゲームエンジンを初期化
            engine = GameEngine()
            menu_handler = MenuHandler(engine)
            engine.register_state_handler(GameState.MENU, menu_handler)
            
            print("[OK] Game engine initialized successfully")
            
            # 短時間実行
            start_time = time.time()
            frame_count = 0
            
            while self.running and (time.time() - start_time) < duration:
                try:
                    # イベント処理
                    engine.handle_events()
                    
                    # 更新
                    dt = 1.0 / 60  # 固定タイムステップ
                    engine.update(dt)
                    
                    # 描画
                    engine.render()
                    
                    # フレームレート制限
                    engine.clock.tick(60)
                    frame_count += 1
                    
                    # 定期的な状態出力
                    if frame_count % 60 == 0:  # 1秒ごと
                        elapsed = time.time() - start_time
                        print(f"[{elapsed:.1f}s] Frame {frame_count}, State: {engine.current_state}")
                
                except Exception as e:
                    self.error_found = True
                    self.error_info = {
                        'exception': e,
                        'traceback': traceback.format_exc(),
                        'frame': frame_count,
                        'elapsed': time.time() - start_time
                    }
                    print(f"[ERROR] Exception caught at frame {frame_count}")
                    print(f"Error: {e}")
                    break
            
            elapsed = time.time() - start_time
            print(f"[OK] Game ran for {elapsed:.1f} seconds, {frame_count} frames")
            
            # エンジン終了
            engine.quit_game()
            return not self.error_found
            
        except Exception as e:
            self.error_found = True
            self.error_info = {
                'exception': e,
                'traceback': traceback.format_exc(),
                'frame': 0,
                'elapsed': 0
            }
            print(f"[CRITICAL] Initialization error: {e}")
            traceback.print_exc()
            return False
    
    def print_error_details(self):
        """エラーの詳細を出力"""
        if self.error_info:
            print("\n=== ERROR DETAILS ===")
            print(f"Frame: {self.error_info['frame']}")
            print(f"Elapsed: {self.error_info['elapsed']:.2f}s")
            print(f"Exception: {self.error_info['exception']}")
            print("Traceback:")
            print(self.error_info['traceback'])

def main():
    """メイン実行関数"""
    print("Starting quick game test...")
    
    tester = GameTester()
    success = False
    
    try:
        success = tester.test_game_run(duration=3)  # 3秒間実行
        
        if success:
            print("\n=== TEST RESULT: SUCCESS ===")
            print("Game ran without errors!")
        else:
            print("\n=== TEST RESULT: FAILURE ===")
            print("Errors were detected during game execution.")
            tester.print_error_details()
    
    except KeyboardInterrupt:
        print("\nTest interrupted by user")
    except Exception as e:
        print(f"Test runner error: {e}")
        traceback.print_exc()
    
    return success

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"FATAL ERROR: {e}")
        traceback.print_exc()
        sys.exit(1)