"""
Drop Puzzle × Roguelike - Complete Version
メインエントリーポイント（完全版）

Python版ぷよぷよ × Slay the Spire風ローグライクゲーム
プレイヤー操作可能な完全なぷよぷよゲーム
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

from src.core.game_engine import GameEngine, GameData
from src.core.constants import *
from src.core.puzzle_game_handler import PuzzleGameHandler

logger = logging.getLogger(__name__)


class MenuHandler:
    """シンプルなメニューハンドラー"""
    
    def __init__(self, engine: GameEngine):
        self.engine = engine
        self.selected_option = 0
        self.menu_options = ["Start Game", "Demo Mode", "Battle Test", "Quit"]
    
    def on_enter(self, previous_state):
        logger.info("Entering menu state")
        self.selected_option = 0
    
    def handle_event(self, event: pygame.event.Event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                self.selected_option = (self.selected_option - 1) % len(self.menu_options)
            elif event.key == pygame.K_DOWN:
                self.selected_option = (self.selected_option + 1) % len(self.menu_options)
            elif event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                if self.selected_option == 0:  # Start Game
                    self.engine.change_state(GameState.PLAYING)
                elif self.selected_option == 1:  # Demo Mode
                    self.engine.change_state(GameState.BATTLE)  # デモモード用
                elif self.selected_option == 2:  # Battle Test
                    self.engine.change_state(GameState.REAL_BATTLE)  # 戦闘テスト用
                elif self.selected_option == 3:  # Quit
                    self.engine.quit_game()
            elif event.key == pygame.K_ESCAPE:
                self.engine.quit_game()
    
    def render(self, surface: pygame.Surface):
        surface.fill(Colors.UI_BACKGROUND)
        
        font_title = self.engine.fonts['title']
        font_large = self.engine.fonts['large']
        font_medium = self.engine.fonts['medium']
        font_small = self.engine.fonts['small']
        
        # タイトル
        title_text = font_title.render("Drop Puzzle × Roguelike", True, Colors.WHITE)
        title_rect = title_text.get_rect(center=(SCREEN_WIDTH // 2, 120))
        surface.blit(title_text, title_rect)
        
        # サブタイトル
        subtitle_text = font_medium.render("Python Edition", True, Colors.LIGHT_GRAY)
        subtitle_rect = subtitle_text.get_rect(center=(SCREEN_WIDTH // 2, 170))
        surface.blit(subtitle_text, subtitle_rect)
        
        # 特徴説明
        features = [
            "✓ Full Puyo Puyo Experience",
            "✓ Player-Controlled Falling",
            "✓ Chain Detection & Scoring",
            "✓ Ghost Piece & Lock Delay",
        ]
        
        for i, feature in enumerate(features):
            text = font_small.render(feature, True, Colors.CYAN)
            text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, 210 + i * 20))
            surface.blit(text, text_rect)
        
        # メニューオプション
        for i, option in enumerate(self.menu_options):
            color = Colors.YELLOW if i == self.selected_option else Colors.WHITE
            option_text = font_large.render(option, True, color)
            option_rect = option_text.get_rect(center=(SCREEN_WIDTH // 2, 320 + i * 50))
            surface.blit(option_text, option_rect)
            
            # 選択中のオプションに矢印
            if i == self.selected_option:
                arrow_text = font_large.render(">", True, Colors.YELLOW)
                arrow_rect = arrow_text.get_rect(center=(SCREEN_WIDTH // 2 - 150, 320 + i * 50))
                surface.blit(arrow_text, arrow_rect)
        
        # 操作説明
        instructions = [
            "↑↓ - Select  |  Enter/Space - Confirm  |  ESC - Quit"
        ]
        
        for i, instruction in enumerate(instructions):
            text = font_small.render(instruction, True, Colors.GRAY)
            text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, 520 + i * 25))
            surface.blit(text, text_rect)


def main():
    """メイン関数"""
    # ログ設定
    logging.basicConfig(
        level=LOG_LEVEL,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    logger.info("=== Drop Puzzle × Roguelike (Complete) Starting ===")
    logger.info(f"Python version: {sys.version}")
    logger.info(f"Pygame version: {pygame.version.ver}")
    
    try:
        # ゲームエンジン初期化
        engine = GameEngine()
        
        # メニューハンドラーを登録
        menu_handler = MenuHandler(engine)
        engine.register_state_handler(GameState.MENU, menu_handler)
        
        # 完全なパズルゲームハンドラーを登録
        puzzle_handler = PuzzleGameHandler(engine)
        engine.register_state_handler(GameState.PLAYING, puzzle_handler)
        
        # 本格版デモモード（2個ペア）
        from src.core.authentic_demo_handler import AuthenticDemoHandler
        demo_handler = AuthenticDemoHandler(engine)
        engine.register_state_handler(GameState.BATTLE, demo_handler)
        
        # 戦闘システム
        from src.battle.battle_handler import BattleHandler
        battle_handler = BattleHandler(engine, floor_level=1)
        engine.register_state_handler(GameState.REAL_BATTLE, battle_handler)
        
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