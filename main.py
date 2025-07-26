"""
Drop Puzzle × Roguelike
メインエントリーポイント

Python版ぷよぷよ × Slay the Spire風ローグライクゲーム
"""

import sys
import os
import logging

# パスを追加してsrcモジュールをインポート可能にする
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

try:
    import pygame
except ImportError:
    print("Error: pygame is not installed!")
    print("Please install pygame: pip install pygame")
    sys.exit(1)

from src.core.game_engine import GameEngine
from src.core.constants import *
from src.core.menu_handler import MenuHandler
from src.puzzle.puyo_grid import PuyoGrid

logger = logging.getLogger(__name__)


class DemoGameHandler:
    """デモ用ゲームハンドラー - 基本的なぷよぷよ動作をテスト"""
    
    def __init__(self, engine: GameEngine):
        self.engine = engine
        self.puyo_grid = PuyoGrid()
        self.last_drop_time = 0
        self.drop_interval = 2.0  # 2秒間隔で自動ドロップ
        
        # テスト用のランダムぷよ生成
        self.puyo_types = [PuyoType.RED, PuyoType.BLUE, PuyoType.GREEN, 
                          PuyoType.YELLOW, PuyoType.PURPLE]
        self.current_puyo_index = 0
        
        # UI要素の位置
        self.ui_start_x = GRID_WIDTH * PUYO_SIZE + GRID_OFFSET_X + 50
        
        logger.info("Demo game handler initialized")
    
    def on_enter(self, previous_state):
        """状態開始時の処理"""
        logger.info("Entering demo game state")
        self.puyo_grid.clear()
        self.last_drop_time = 0
    
    def on_exit(self):
        """状態終了時の処理"""
        logger.info("Exiting demo game state")
    
    def update(self, dt: float):
        """更新処理"""
        # 自動でぷよをドロップ
        self.last_drop_time += dt
        if self.last_drop_time >= self.drop_interval:
            self._auto_drop_puyo()
            self.last_drop_time = 0
    
    def _auto_drop_puyo(self):
        """自動でぷよをドロップ"""
        import random
        
        # ランダムな列を選択
        column = random.randint(0, GRID_WIDTH - 1)
        
        # ランダムなぷよタイプを選択
        puyo_type = random.choice(self.puyo_types)
        
        # ドロップ実行
        if self.puyo_grid.drop_puyo(column, puyo_type):
            logger.info(f"Dropped {puyo_type.name} puyo in column {column}")
            
            # 連鎖チェック
            score, eliminated = self.puyo_grid.execute_full_chain_sequence()
            if eliminated > 0:
                logger.info(f"Chain occurred! Score: {score}, Eliminated: {eliminated}")
        else:
            logger.warning(f"Failed to drop puyo in column {column} (column full)")
    
    def handle_event(self, event: pygame.event.Event):
        """イベント処理"""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.engine.quit_game()
            
            elif event.key == pygame.K_r:
                # グリッドリセット
                self.puyo_grid.clear()
                logger.info("Grid reset")
            
            elif event.key == pygame.K_SPACE:
                # 手動でぷよドロップ
                self._auto_drop_puyo()
            
            elif event.key == pygame.K_b:
                # 戦闘テストモード
                self.start_battle_test()
            
            elif event.key == pygame.K_c:
                # 連鎖実行
                score, eliminated = self.puyo_grid.execute_full_chain_sequence()
                logger.info(f"Manual chain execution: Score={score}, Eliminated={eliminated}")
        
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # 左クリック
                # クリック位置にぷよを配置
                mouse_x, mouse_y = event.pos
                grid_x, grid_y = self.puyo_grid.pixel_to_grid(mouse_x, mouse_y)
                
                if self.puyo_grid.can_place_puyo(grid_x, grid_y):
                    puyo_type = self.puyo_types[self.current_puyo_index % len(self.puyo_types)]
                    self.puyo_grid.set_puyo(grid_x, grid_y, puyo_type)
                    self.current_puyo_index += 1
                    logger.info(f"Manually placed {puyo_type.name} at ({grid_x}, {grid_y})")
    
    def render(self, surface: pygame.Surface):
        """描画処理"""
        # ぷよグリッドを描画
        self.puyo_grid.render(surface, show_grid=True)
        
        # UI情報を描画
        self._render_ui(surface)
    
    def _render_ui(self, surface: pygame.Surface):
        """UI情報を描画"""
        font_medium = self.engine.fonts['medium']
        font_small = self.engine.fonts['small']
        
        y_offset = GRID_OFFSET_Y
        
        # タイトル
        title_text = font_medium.render("Drop Puzzle Demo", True, Colors.WHITE)
        surface.blit(title_text, (self.ui_start_x, y_offset))
        y_offset += 40
        
        # 統計情報
        stats = [
            f"Total Chains: {self.puyo_grid.total_chains}",
            f"Last Score: {self.puyo_grid.last_chain_score}",
            f"Next Drop: {self.drop_interval - self.last_drop_time:.1f}s",
        ]
        
        for stat in stats:
            text = font_small.render(stat, True, Colors.LIGHT_GRAY)
            surface.blit(text, (self.ui_start_x, y_offset))
            y_offset += 25
        
        # 操作説明
        y_offset += 20
        instructions = [
            "Controls:",
            "ESC - Quit",
            "R - Reset Grid", 
            "SPACE - Drop Puyo",
            "B - Battle Test",
            "C - Execute Chain",
            "Click - Place Puyo",
        ]
        
        for instruction in instructions:
            color = Colors.WHITE if instruction == "Controls:" else Colors.GRAY
            text = font_small.render(instruction, True, color)
            surface.blit(text, (self.ui_start_x, y_offset))
            y_offset += 20
        
        # ゲームオーバー判定
        if self.puyo_grid.is_game_over():
            game_over_text = font_medium.render("GAME OVER", True, Colors.RED)
            text_rect = game_over_text.get_rect(center=(SCREEN_WIDTH // 2, 100))
            surface.blit(game_over_text, text_rect)
            
            reset_text = font_small.render("Press R to reset", True, Colors.WHITE)
            text_rect = reset_text.get_rect(center=(SCREEN_WIDTH // 2, 130))
            surface.blit(reset_text, text_rect)
    
    def start_battle_test(self):
        """戦闘テストを開始"""
        logger.info("Starting battle test mode...")
        try:
            from src.battle.battle_handler import BattleHandler
            
            # 戦闘ハンドラーを作成
            battle_handler = BattleHandler(self.engine, floor_level=2)
            
            # 戦闘状態に変更
            self.engine.register_state_handler(GameState.REAL_BATTLE, battle_handler)
            self.engine.change_state(GameState.REAL_BATTLE)
        except Exception as e:
            logger.error(f"Failed to start battle test: {e}")
            import traceback
            traceback.print_exc()


def main():
    """メイン関数"""
    # ログ設定
    logging.basicConfig(
        level=LOG_LEVEL,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    logger.info("=== Drop Puzzle × Roguelike Starting ===")
    logger.info(f"Python version: {sys.version}")
    logger.info(f"Pygame version: {pygame.version.ver}")
    
    try:
        # ゲームエンジン初期化
        engine = GameEngine()
        
        # メインメニューハンドラーを登録
        menu_handler = MenuHandler(engine)
        engine.register_state_handler(GameState.MENU, menu_handler)
        
        # デモハンドラーも登録（後方互換性のため）
        demo_handler = DemoGameHandler(engine)
        engine.register_state_handler(GameState.PLAYING, demo_handler)
        
        # ゲーム状態をメニューに設定
        engine.change_state(GameState.MENU)
        
        # メインループ開始
        engine.run()
        
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    logger.info("=== Game Ended Successfully ===")
    return 0


if __name__ == "__main__":
    sys.exit(main())