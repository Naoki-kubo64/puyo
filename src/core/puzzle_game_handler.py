"""
パズルゲームハンドラー - 完全なぷよぷよゲーム体験
Drop Puzzle × Roguelike のメインゲームプレイ部分
"""

import pygame
import logging
from typing import Dict, List

from .constants import *
from .game_engine import GameEngine
from ..puzzle.puyo_grid import PuyoGrid
from ..puzzle.falling_system import FallingSystem
from .authentic_demo_handler import AuthenticDemoHandler

logger = logging.getLogger(__name__)


class PuzzleGameHandler:
    """完全なぷよぷよゲーム体験を提供するハンドラー"""
    
    def __init__(self, engine: GameEngine):
        self.engine = engine
        
        # AuthenticDemoHandlerを内部で使用（継承せずに組み合わせ）
        self.demo_handler = AuthenticDemoHandler(engine)
        
        # UI要素の位置
        self.grid_x = GRID_OFFSET_X
        self.grid_y = GRID_OFFSET_Y
        self.ui_start_x = GRID_WIDTH * PUYO_SIZE + GRID_OFFSET_X + 30
        
        # ゲーム状態
        self.paused = False
        self.show_debug = False
        self.game_over_logged = False  # ゲームオーバーのログを一度だけ出力するフラグ
        
        # 統計表示
        self.stats_display_timer = 0.0
        self.last_chain_info = ""
        
        logger.info("PuzzleGameHandler initialized")
    
    def on_enter(self, previous_state):
        """ゲーム状態開始時の処理"""
        logger.info("Entering puzzle game state")
        self.demo_handler.on_enter(previous_state)
        self.paused = False
        self.game_over_logged = False  # 状態開始時にフラグをリセット
    
    def on_exit(self):
        """ゲーム状態終了時の処理"""
        logger.info("Exiting puzzle game state")
        self.demo_handler.on_exit()
    
    def update(self, dt: float):
        """更新処理"""
        if self.paused:
            return
        
        # デモハンドラー更新
        self.demo_handler.update(dt)
        
        # UI更新
        self.stats_display_timer += dt
        
        # ゲームオーバーチェック
        if not self.demo_handler.game_active and not self.game_over_logged:
            self._handle_game_over()
    
    def _handle_game_over(self):
        """ゲームオーバー処理"""
        if not self.game_over_logged:
            logger.info(f"Game Over - Final Score: {self.demo_handler.total_score}")
            self.game_over_logged = True
            # ここで将来的にはゲームオーバー画面に遷移
    
    def handle_event(self, event: pygame.event.Event):
        """イベント処理"""
        if event.type == pygame.KEYDOWN:
            # ゲーム制御
            if event.key == pygame.K_ESCAPE:
                if self.demo_handler.game_active:
                    self.paused = not self.paused
                    logger.info(f"Game {'paused' if self.paused else 'resumed'}")
                else:
                    # ゲームオーバー時はタイトルに戻る
                    self.engine.change_state(GameState.MENU)
            
            elif event.key == pygame.K_r:
                # リスタート
                self.demo_handler._reset_game()
                self.paused = False
                self.game_over_logged = False  # リスタート時にフラグをリセット
                logger.info("Game restarted")
            
            elif event.key == pygame.K_F3:
                # デバッグ表示切り替え
                self.show_debug = not self.show_debug
        
        # ゲーム中でない場合は入力を無視
        if not self.demo_handler.game_active or self.paused:
            return
        
        # デモハンドラーに入力を渡す
        self.demo_handler.handle_event(event)
    
    def render(self, surface: pygame.Surface):
        """描画処理"""
        # デモハンドラーでベース描画
        self.demo_handler.render(surface)
        
        # カスタムUI上書き描画
        self._render_main_game_ui(surface)
        
        # メインゲーム専用NEXTエリア
        self._render_main_game_next_area(surface)
        
        # デバッグ情報
        if self.show_debug:
            self._render_debug_info(surface)
        
        # ポーズ・ゲームオーバーオーバーレイ
        if self.paused:
            self._render_pause_overlay(surface)
        elif not self.demo_handler.game_active:
            self._render_game_over_overlay(surface)
    
    def _render_main_game_ui(self, surface: pygame.Surface):
        """UI描画"""
        font_large = self.engine.fonts['large']
        font_medium = self.engine.fonts['medium']
        font_small = self.engine.fonts['small']
        
        y_offset = self.grid_y
        
        # UI開始位置を上書き
        y_offset = GRID_OFFSET_Y + 100  # NEXTエリア分下にずらす
        
        # メインゲームタイトル
        title_rect = pygame.Rect(self.ui_start_x, GRID_OFFSET_Y, 200, 80)
        pygame.draw.rect(surface, Colors.DARK_GRAY, title_rect)
        pygame.draw.rect(surface, Colors.WHITE, title_rect, 2)
        
        title_text = font_medium.render("MAIN GAME", True, Colors.WHITE)
        title_text_rect = title_text.get_rect(center=title_rect.center)
        surface.blit(title_text, title_text_rect)
        
        # メインゲーム専用の操作説明
        game_controls = [
            "MAIN GAME MODE",
            "",
            "Same as Demo Mode:",
            "A/D - Move Left/Right",
            "S - Fast Fall (hold)",
            "Space - Rotate",
            "",
            "Special:",
            "ESC - Pause/Menu",
            "R - Restart",
            "F3 - Debug Mode",
        ]
        
        y_offset = self.ui_start_x + 400  # 画面下部に配置
        
        for control in game_controls:
            if control == "":
                y_offset += 5
                continue
            elif control in ["MAIN GAME MODE", "Same as Demo Mode:", "Special:"]:
                color = Colors.YELLOW
            else:
                color = Colors.LIGHT_GRAY
            
            control_text = font_small.render(control, True, color)
            surface.blit(control_text, (self.ui_start_x, y_offset))
            y_offset += 18
    
    def _render_main_game_next_area(self, surface: pygame.Surface):
        """メインゲーム専用NEXTぷよ表示エリアを描画"""
        if self.demo_handler.next_pair_colors is None:
            return
        
        # NEXTエリアの位置（プレイエリア右上）
        next_area_x = GRID_OFFSET_X + GRID_WIDTH * PUYO_SIZE + 10
        next_area_y = GRID_OFFSET_Y
        next_area_width = 100
        next_area_height = 80
        
        # 背景を少し目立つ色に変更（メインゲーム用）
        next_bg_rect = pygame.Rect(next_area_x, next_area_y, next_area_width, next_area_height)
        pygame.draw.rect(surface, Colors.UI_BACKGROUND, next_bg_rect)
        pygame.draw.rect(surface, Colors.YELLOW, next_bg_rect, 3)  # 黄色の太い枠線
        
        # "MAIN NEXT"タイトル
        font_small = self.engine.fonts['small']
        next_title = font_small.render("MAIN NEXT", True, Colors.YELLOW)
        title_rect = next_title.get_rect(centerx=next_area_x + next_area_width // 2, y=next_area_y + 3)
        surface.blit(next_title, title_rect)
        
        # NEXTぷよペア描画
        main_type, sub_type = self.demo_handler.next_pair_colors
        
        # ぷよサイズ（表示用に少し小さく）
        puyo_size = 25
        
        # ペアの中心位置
        center_x = next_area_x + next_area_width // 2
        center_y = next_area_y + 45
        
        # 軸ぷよ（中心）- 太い枠線で強調
        main_rect = pygame.Rect(
            center_x - puyo_size // 2,
            center_y - puyo_size // 2,
            puyo_size - 2,
            puyo_size - 2
        )
        
        main_color = PUYO_COLORS[main_type]
        main_center = main_rect.center
        main_radius = (puyo_size - 2) // 2
        
        pygame.draw.circle(surface, main_color, main_center, main_radius)
        pygame.draw.circle(surface, Colors.WHITE, main_center, main_radius, 3)  # 太い枠線
        
        # ハイライト
        highlight_radius = main_radius // 3
        highlight_center = (main_center[0] - main_radius//3, main_center[1] - main_radius//3)
        pygame.draw.circle(surface, Colors.WHITE, highlight_center, highlight_radius)
        
        # 子ぷよ（上に配置 - rotation=0の状態）
        sub_rect = pygame.Rect(
            center_x - puyo_size // 2,
            center_y - puyo_size // 2 - puyo_size,  # 上に配置
            puyo_size - 2,
            puyo_size - 2
        )
        
        sub_color = PUYO_COLORS[sub_type]
        sub_center = sub_rect.center
        sub_radius = (puyo_size - 2) // 2
        
        pygame.draw.circle(surface, sub_color, sub_center, sub_radius)
        pygame.draw.circle(surface, Colors.WHITE, sub_center, sub_radius, 2)  # 通常枠線
        
        # ハイライト
        sub_highlight_center = (sub_center[0] - sub_radius//3, sub_center[1] - sub_radius//3)
        pygame.draw.circle(surface, Colors.WHITE, sub_highlight_center, highlight_radius)
    
    def _render_debug_info(self, surface: pygame.Surface):
        """デバッグ情報描画"""
        font_small = self.engine.fonts['small']
        
        debug_x = 10
        debug_y = SCREEN_HEIGHT - 200
        
        debug_info = [
            "=== MAIN GAME DEBUG ===",
            f"Game Active: {self.demo_handler.game_active}",
            f"Paused: {self.paused}",
            f"Score: {self.demo_handler.total_score}",
            f"Chains: {self.demo_handler.total_chains}",
        ]
        
        if self.demo_handler.current_pair:
            pair = self.demo_handler.current_pair
            debug_info.extend([
                f"Current Pair: ({pair.center_x}, {pair.center_y}) R{pair.rotation}",
                f"Types: {pair.main_type.name} + {pair.sub_type.name}",
                f"Active: {pair.active}",
            ])
        
        for i, info in enumerate(debug_info):
            color = Colors.WHITE if i == 0 else Colors.LIGHT_GRAY
            text = font_small.render(info, True, color)
            surface.blit(text, (debug_x, debug_y + i * 15))
    
    def _render_pause_overlay(self, surface: pygame.Surface):
        """ポーズオーバーレイ描画"""
        # 半透明背景
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(128)
        overlay.fill(Colors.BLACK)
        surface.blit(overlay, (0, 0))
        
        # ポーズテキスト
        font_title = self.engine.fonts['title']
        font_medium = self.engine.fonts['medium']
        
        pause_text = font_title.render("PAUSED", True, Colors.WHITE)
        text_rect = pause_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50))
        surface.blit(pause_text, text_rect)
        
        # 操作説明
        instructions = [
            "ESC - Resume",
            "R - Restart",
        ]
        
        for i, instruction in enumerate(instructions):
            text = font_medium.render(instruction, True, Colors.LIGHT_GRAY)
            text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 20 + i * 30))
            surface.blit(text, text_rect)
    
    def _render_game_over_overlay(self, surface: pygame.Surface):
        """ゲームオーバーオーバーレイ描画"""
        # 半透明背景
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(160)
        overlay.fill(Colors.BLACK)
        surface.blit(overlay, (0, 0))
        
        font_title = self.engine.fonts['title']
        font_large = self.engine.fonts['large']
        font_medium = self.engine.fonts['medium']
        
        # ゲームオーバーテキスト
        game_over_text = font_title.render("GAME OVER", True, Colors.RED)
        text_rect = game_over_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 100))
        surface.blit(game_over_text, text_rect)
        
        # 最終スコア
        final_score_text = font_large.render(f"Final Score: {self.demo_handler.total_score:,}", True, Colors.WHITE)
        text_rect = final_score_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 30))
        surface.blit(final_score_text, text_rect)
        
        # 統計
        stats = [
            f"Total Chains: {self.demo_handler.total_chains}",
            f"Last Chain Score: {self.demo_handler.puyo_grid.last_chain_score}",
        ]
        
        for i, stat in enumerate(stats):
            text = font_medium.render(stat, True, Colors.LIGHT_GRAY)
            text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 20 + i * 30))
            surface.blit(text, text_rect)
        
        # 操作説明
        instructions = [
            "R - Restart",
            "ESC - Return to Menu",
        ]
        
        for i, instruction in enumerate(instructions):
            text = font_medium.render(instruction, True, Colors.YELLOW)
            text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 140 + i * 30))
            surface.blit(text, text_rect)


if __name__ == "__main__":
    # テスト実行
    import sys
    import os
    
    # パス設定
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
    
    from src.core.game_engine import GameEngine
    
    logging.basicConfig(level=logging.INFO)
    
    engine = GameEngine()
    handler = PuzzleGameHandler(engine)
    
    engine.register_state_handler(GameState.PLAYING, handler)
    engine.change_state(GameState.PLAYING)
    
    print("Starting puzzle game test...")
    engine.run()