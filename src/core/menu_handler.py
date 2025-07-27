"""
メインメニューハンドラー - ゲームのスタート画面とメニュー管理
Drop Puzzle × Roguelike のメインメニューシステム
"""

import pygame
import logging
import math
from typing import List, Optional

from .constants import *
from .game_engine import GameEngine

logger = logging.getLogger(__name__)


class MenuOption:
    """メニューオプション"""
    
    def __init__(self, text: str, action: str, description: str = ""):
        self.text = text
        self.action = action
        self.description = description
        self.rect: Optional[pygame.Rect] = None
        self.hovered = False


class MenuHandler:
    """メインメニューの管理クラス"""
    
    def __init__(self, engine: GameEngine):
        self.engine = engine
        
        # メニューオプション
        self.menu_options = [
            MenuOption("START ADVENTURE", "start_dungeon", "Begin your roguelike journey"),
            MenuOption("PUZZLE PRACTICE", "puzzle_mode", "Practice puyo puyo mechanics"),
            MenuOption("BATTLE TEST", "battle_test", "Test the battle system"),
            MenuOption("DUNGEON MAP", "dungeon_map", "View the dungeon map"),
            MenuOption("QUIT GAME", "quit", "Exit the game"),
        ]
        
        # UI設定
        self.title_y = 200
        self.menu_start_y = 400
        self.option_height = 80
        self.option_spacing = 20
        
        # 選択状態
        self.selected_index = 0
        self.hovered_option: Optional[MenuOption] = None
        
        # アニメーション
        self.title_pulse = 0.0
        
        # 矩形を初期化
        self._update_option_rects()
        
        logger.info("MenuHandler initialized")
    
    def on_enter(self, previous_state):
        """メニュー状態開始時の処理"""
        logger.info("Entering main menu")
        self.selected_index = 0
        self.hovered_option = None
        self._update_option_rects()
    
    def on_exit(self):
        """メニュー状態終了時の処理"""
        logger.info("Exiting main menu")
    
    def update(self, dt: float):
        """更新処理"""
        # タイトルのパルスアニメーション
        self.title_pulse += dt * 2.0
        
        # マウス位置でホバー状態を更新
        mouse_pos = pygame.mouse.get_pos()
        self._update_hover_state(mouse_pos)
    
    def handle_event(self, event: pygame.event.Event):
        """イベント処理"""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                self.selected_index = (self.selected_index - 1) % len(self.menu_options)
                logger.debug(f"Menu selection: {self.menu_options[self.selected_index].text}")
            
            elif event.key == pygame.K_DOWN:
                self.selected_index = (self.selected_index + 1) % len(self.menu_options)
                logger.debug(f"Menu selection: {self.menu_options[self.selected_index].text}")
            
            elif event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                self._execute_selected_action()
            
            elif event.key == pygame.K_ESCAPE:
                self._execute_action("quit")
        
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # 左クリック
                if self.hovered_option:
                    self._execute_action(self.hovered_option.action)
        
        elif event.type == pygame.MOUSEMOTION:
            self._update_hover_state(event.pos)
    
    def render(self, surface: pygame.Surface):
        """描画処理"""
        # 背景
        surface.fill(Colors.BLACK)
        
        # 背景グラデーション効果（簡易版）
        self._render_background_effect(surface)
        
        # タイトル
        self._render_title(surface)
        
        # メニューオプション
        self._render_menu_options(surface)
        
        # フッター情報
        self._render_footer(surface)
    
    def _render_background_effect(self, surface: pygame.Surface):
        """背景効果を描画"""
        # 簡単なグラデーション効果
        for y in range(0, SCREEN_HEIGHT, 4):
            alpha = int(30 * (1 - y / SCREEN_HEIGHT))
            if alpha > 0:
                color = (alpha, alpha // 2, alpha)
                pygame.draw.line(surface, color, (0, y), (SCREEN_WIDTH, y), 4)
    
    def _render_title(self, surface: pygame.Surface):
        """タイトルを描画"""
        font_title = self.engine.fonts['title']
        
        # パルス効果
        pulse_scale = 1.0 + 0.1 * abs(math.sin(self.title_pulse))
        
        title_lines = [
            "DROP PUZZLE",
            "×",
            "ROGUELIKE"
        ]
        
        y_offset = self.title_y
        for i, line in enumerate(title_lines):
            # 色を変化させる
            if i == 1:  # ×マーク
                color = Colors.YELLOW
            else:
                color = Colors.WHITE
            
            text = font_title.render(line, True, color)
            
            # パルス効果を適用
            if pulse_scale != 1.0:
                text_width = int(text.get_width() * pulse_scale)
                text_height = int(text.get_height() * pulse_scale)
                text = pygame.transform.scale(text, (text_width, text_height))
            
            text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, y_offset))
            surface.blit(text, text_rect)
            
            y_offset += 70 if i == 0 else 50
    
    def _render_menu_options(self, surface: pygame.Surface):
        """メニューオプションを描画"""
        font_large = self.engine.fonts['large']
        font_medium = self.engine.fonts['medium']
        
        for i, option in enumerate(self.menu_options):
            # 選択状態やホバー状態に応じて色を決定
            if option == self.hovered_option or i == self.selected_index:
                text_color = Colors.YELLOW
                bg_color = Colors.DARK_GRAY
            else:
                text_color = Colors.WHITE
                bg_color = None
            
            # 背景を描画（選択時）
            if bg_color:
                pygame.draw.rect(surface, bg_color, option.rect)
                pygame.draw.rect(surface, Colors.YELLOW, option.rect, 3)
            
            # メインテキスト
            text = font_large.render(option.text, True, text_color)
            text_rect = text.get_rect(center=option.rect.center)
            text_rect.y -= 10  # 少し上にずらす
            surface.blit(text, text_rect)
            
            # 説明テキスト
            if option.description:
                desc_text = font_medium.render(option.description, True, Colors.LIGHT_GRAY)
                desc_rect = desc_text.get_rect(center=option.rect.center)
                desc_rect.y += 15  # 少し下にずらす
                surface.blit(desc_text, desc_rect)
    
    def _render_footer(self, surface: pygame.Surface):
        """フッター情報を描画"""
        font_small = self.engine.fonts['small']
        
        footer_lines = [
            "Use UP/DOWN arrows or mouse to navigate",
            "Press ENTER/SPACE or click to select",
            "ESC to quit"
        ]
        
        y_start = SCREEN_HEIGHT - 100
        for i, line in enumerate(footer_lines):
            text = font_small.render(line, True, Colors.GRAY)
            text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, y_start + i * 20))
            surface.blit(text, text_rect)
    
    def _update_option_rects(self):
        """メニューオプションの矩形を更新"""
        for i, option in enumerate(self.menu_options):
            option.rect = pygame.Rect(
                SCREEN_WIDTH // 2 - 300,  # 中央から左に300px
                self.menu_start_y + i * (self.option_height + self.option_spacing),
                600,  # 幅600px
                self.option_height
            )
    
    def _update_hover_state(self, mouse_pos):
        """マウスホバー状態を更新"""
        self.hovered_option = None
        for option in self.menu_options:
            if option.rect and option.rect.collidepoint(mouse_pos):
                self.hovered_option = option
                break
    
    def _execute_selected_action(self):
        """選択されたアクションを実行"""
        selected_option = self.menu_options[self.selected_index]
        self._execute_action(selected_option.action)
    
    def _execute_action(self, action: str):
        """アクションを実行"""
        logger.info(f"Executing menu action: {action}")
        
        if action == "start_dungeon":
            self._start_dungeon_adventure()
        
        elif action == "puzzle_mode":
            self._start_puzzle_practice()
        
        elif action == "battle_test":
            self._start_battle_test()
        
        elif action == "dungeon_map":
            self._show_dungeon_map()
        
        elif action == "quit":
            self.engine.quit_game()
        
        else:
            logger.warning(f"Unknown menu action: {action}")
    
    def _start_dungeon_adventure(self):
        """ダンジョン冒険を開始"""
        try:
            from dungeon.map_handler import DungeonMapHandler
            
            # ダンジョンマップハンドラーを作成
            map_handler = DungeonMapHandler(self.engine)
            
            # ダンジョンマップ状態に変更
            self.engine.register_state_handler(GameState.DUNGEON_MAP, map_handler)
            self.engine.change_state(GameState.DUNGEON_MAP)
            
        except Exception as e:
            logger.error(f"Failed to start dungeon adventure: {e}")
            import traceback
            traceback.print_exc()
    
    def _start_puzzle_practice(self):
        """パズル練習モードを開始"""
        try:
            from .puzzle_game_handler import PuzzleGameHandler
            
            # パズルゲームハンドラーを作成
            puzzle_handler = PuzzleGameHandler(self.engine)
            
            # パズルゲーム状態に変更
            self.engine.register_state_handler(GameState.PLAYING, puzzle_handler)
            self.engine.change_state(GameState.PLAYING)
            
        except Exception as e:
            logger.error(f"Failed to start puzzle practice: {e}")
            import traceback
            traceback.print_exc()
    
    def _start_battle_test(self):
        """戦闘テストを開始"""
        try:
            from battle.battle_handler import BattleHandler
            
            # 戦闘ハンドラーを作成
            battle_handler = BattleHandler(self.engine, floor_level=1)
            
            # 戦闘状態に変更
            self.engine.register_state_handler(GameState.REAL_BATTLE, battle_handler)
            self.engine.change_state(GameState.REAL_BATTLE)
            
        except Exception as e:
            logger.error(f"Failed to start battle test: {e}")
            import traceback
            traceback.print_exc()
    
    def _show_dungeon_map(self):
        """ダンジョンマップを表示"""
        try:
            from dungeon.map_handler import DungeonMapHandler
            
            # ダンジョンマップハンドラーを作成
            map_handler = DungeonMapHandler(self.engine)
            
            # ダンジョンマップ状態に変更
            self.engine.register_state_handler(GameState.DUNGEON_MAP, map_handler)
            self.engine.change_state(GameState.DUNGEON_MAP)
            
        except Exception as e:
            logger.error(f"Failed to show dungeon map: {e}")
            import traceback
            traceback.print_exc()


if __name__ == "__main__":
    # テスト実行
    import sys
    import os
    
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
    
    pygame.init()
    from .game_engine import GameEngine
    
    logging.basicConfig(level=logging.INFO)
    
    engine = GameEngine()
    handler = MenuHandler(engine)
    
    engine.register_state_handler(GameState.MENU, handler)
    engine.change_state(GameState.MENU)
    
    print("Starting menu test...")
    engine.run()