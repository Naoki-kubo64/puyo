"""
改良版デモハンドラー - 落下アニメーション付きのデモモード
Drop Puzzle × Roguelike のビジュアル改善版デモ
"""

import pygame
import logging
import random
from typing import List, Optional

from .constants import *
from .game_engine import GameEngine
from ..puzzle.puyo_grid import PuyoGrid

logger = logging.getLogger(__name__)


class FallingDemoPuyo:
    """デモ用の落下ぷよクラス"""
    
    def __init__(self, puyo_type: PuyoType, column: int):
        self.puyo_type = puyo_type
        self.column = column
        self.y_position = -1.0  # グリッド座標（小数点で滑らかな移動）
        self.fall_speed = 1.5  # セル/秒（遅くした）
        self.active = True
        self.can_control = True  # プレイヤー操作可能フラグ
    
    def update(self, dt: float, grid: PuyoGrid) -> bool:
        """更新処理 - 着地したらTrueを返す"""
        if not self.active:
            return False
        
        # 落下処理
        self.y_position += self.fall_speed * dt
        
        # 着地判定
        target_y = grid.get_drop_position(self.column)
        
        if target_y == -1:  # 列が満杯
            self.active = False
            return True
        
        if self.y_position >= target_y:
            # 着地
            self.y_position = target_y
            grid.set_puyo(self.column, target_y, self.puyo_type)
            self.active = False
            return True
        
        return False
    
    def try_move_horizontal(self, direction: int, grid: PuyoGrid) -> bool:
        """横移動を試行"""
        if not self.can_control:
            return False
        
        new_column = self.column + direction
        
        # 範囲チェック
        if new_column < 0 or new_column >= GRID_WIDTH:
            return False
        
        # 移動先に障害物がないかチェック
        check_y = int(self.y_position)
        if check_y >= 0 and not grid.can_place_puyo(new_column, check_y):
            return False
        
        self.column = new_column
        return True
    
    def accelerate_fall(self):
        """高速落下"""
        if self.can_control:
            self.fall_speed = 6.0  # 高速化
    
    def render(self, surface: pygame.Surface, grid: PuyoGrid):
        """描画処理"""
        if not self.active:
            return
        
        # 画面外は描画しない
        if self.y_position < 0:
            return
        
        pixel_x, pixel_y = grid.grid_to_pixel(self.column, int(self.y_position))
        
        # 小数点部分でスムーズな移動
        fractional_y = self.y_position - int(self.y_position)
        pixel_y += int(fractional_y * grid.puyo_size)
        
        rect = pygame.Rect(
            pixel_x + 2,
            pixel_y + 2,
            grid.puyo_size - 4,
            grid.puyo_size - 4
        )
        
        color = PUYO_COLORS[self.puyo_type]
        center = rect.center
        radius = (grid.puyo_size - 4) // 2
        
        # ぷよ本体
        pygame.draw.circle(surface, color, center, radius)
        pygame.draw.circle(surface, Colors.WHITE, center, radius, 2)
        
        # ハイライト効果
        highlight_radius = radius // 3
        highlight_center = (center[0] - radius//3, center[1] - radius//3)
        pygame.draw.circle(surface, Colors.WHITE, highlight_center, highlight_radius)


class ImprovedDemoHandler:
    """改良版デモハンドラー - 美しい落下アニメーション付き"""
    
    def __init__(self, engine: GameEngine):
        self.engine = engine
        self.puyo_grid = PuyoGrid()
        
        # 落下中のぷよ管理
        self.falling_puyos: List[FallingDemoPuyo] = []
        
        # タイミング制御
        self.spawn_timer = 0.0
        self.spawn_interval = 4.0  # 4秒間隔でスポーン（プレイヤー操作時間を確保）
        
        # チェイン処理
        self.chain_delay_timer = 0.0
        self.chain_delay = 0.5  # チェイン後の待機時間
        self.pending_chain_check = False
        
        # ゲーム状態
        self.game_active = True
        self.total_score = 0
        self.total_chains = 0
        
        # UI要素の位置
        self.ui_start_x = GRID_WIDTH * PUYO_SIZE + GRID_OFFSET_X + 30
        
        # 使用可能なぷよタイプ
        self.puyo_types = [PuyoType.RED, PuyoType.BLUE, PuyoType.GREEN, 
                          PuyoType.YELLOW, PuyoType.PURPLE]
        
        logger.info("Improved demo handler initialized")
    
    def on_enter(self, previous_state):
        """状態開始時の処理"""
        logger.info("Entering improved demo state")
        self._reset_game()
    
    def on_exit(self):
        """状態終了時の処理"""
        logger.info("Exiting improved demo state")
    
    def _reset_game(self):
        """ゲームリセット"""
        self.puyo_grid.clear()
        self.falling_puyos.clear()
        self.spawn_timer = 0.0
        self.chain_delay_timer = 0.0
        self.pending_chain_check = False
        self.game_active = True
        self.total_score = 0
        self.total_chains = 0
    
    def update(self, dt: float):
        """更新処理"""
        if not self.game_active:
            return
        
        # 落下中のぷよ更新
        self._update_falling_puyos(dt)
        
        # スポーンタイマー更新
        self.spawn_timer += dt
        
        # チェイン遅延処理
        if self.pending_chain_check:
            self.chain_delay_timer += dt
            if self.chain_delay_timer >= self.chain_delay:
                self._execute_chain_check()
                self.pending_chain_check = False
                self.chain_delay_timer = 0.0
        
        # 新しいぷよスポーン（少し長めの間隔で自動スポーン）
        if self.spawn_timer >= self.spawn_interval and not self.falling_puyos:
            self._spawn_random_puyo()
            self.spawn_timer = 0.0
        
        # ゲームオーバー判定
        if self.puyo_grid.is_game_over():
            self.game_active = False
            logger.info(f"Demo game over - Score: {self.total_score}")
    
    def _update_falling_puyos(self, dt: float):
        """落下中のぷよを更新"""
        landed_puyos = []
        
        for puyo in self.falling_puyos[:]:  # コピーしてイテレート
            if puyo.update(dt, self.puyo_grid):
                landed_puyos.append(puyo)
                self.falling_puyos.remove(puyo)
        
        # 着地したぷよがある場合、チェイン判定を予約
        if landed_puyos and not self.pending_chain_check:
            self.pending_chain_check = True
            self.chain_delay_timer = 0.0
    
    def _spawn_random_puyo(self):
        """ランダムなぷよをスポーン"""
        # ランダムな列を選択（満杯でない列）
        available_columns = []
        for col in range(GRID_WIDTH):
            if self.puyo_grid.get_drop_position(col) != -1:
                available_columns.append(col)
        
        if not available_columns:
            logger.warning("No available columns for spawning")
            return
        
        column = random.choice(available_columns)
        puyo_type = random.choice(self.puyo_types)
        
        # 落下ぷよ作成
        falling_puyo = FallingDemoPuyo(puyo_type, column)
        self.falling_puyos.append(falling_puyo)
        
        logger.info(f"Spawned {puyo_type.name} puyo in column {column}")
    
    def _execute_chain_check(self):
        """チェイン判定と実行"""
        score, eliminated = self.puyo_grid.execute_full_chain_sequence()
        
        if eliminated > 0:
            self.total_score += score
            self.total_chains += 1
            logger.info(f"Chain executed: {eliminated} puyos eliminated, score: {score}")
    
    def handle_event(self, event: pygame.event.Event):
        """イベント処理"""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                # メニューに戻る
                self.engine.change_state(GameState.MENU)
            
            elif event.key == pygame.K_r:
                # リセット
                self._reset_game()
                logger.info("Demo reset")
            
            elif event.key == pygame.K_RETURN:
                # メインゲームに移行
                self.engine.change_state(GameState.PLAYING)
            
            elif event.key == pygame.K_c:
                # 手動チェイン実行
                self._execute_chain_check()
            
            # プレイヤー操作（落下中のぷよがある場合）
            elif self.falling_puyos:
                controlled_puyo = self.falling_puyos[0]  # 最初の落下ぷよを操作
                
                if event.key == pygame.K_a:
                    # 左移動
                    if controlled_puyo.try_move_horizontal(-1, self.puyo_grid):
                        logger.debug("Puyo moved left")
                
                elif event.key == pygame.K_d:
                    # 右移動
                    if controlled_puyo.try_move_horizontal(1, self.puyo_grid):
                        logger.debug("Puyo moved right")
                
                elif event.key == pygame.K_s:
                    # 高速落下
                    controlled_puyo.accelerate_fall()
                    logger.debug("Puyo accelerated")
                
                elif event.key == pygame.K_SPACE:
                    # 回転（デモ版では色変更で代用）
                    old_type = controlled_puyo.puyo_type
                    # 次の色に変更
                    type_list = list(self.puyo_types)
                    current_index = type_list.index(old_type) if old_type in type_list else 0
                    next_index = (current_index + 1) % len(type_list)
                    controlled_puyo.puyo_type = type_list[next_index]
                    logger.debug(f"Puyo color changed: {old_type.name} -> {controlled_puyo.puyo_type.name}")
            
            # 落下中でない場合は手動スポーン
            elif event.key == pygame.K_SPACE:
                if not self.falling_puyos:  # 落下中でない時のみ
                    self._spawn_random_puyo()
        
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # 左クリック
                # クリック位置にぷよを配置（落下中でない時のみ）
                if not self.falling_puyos:
                    mouse_x, mouse_y = event.pos
                    grid_x, grid_y = self.puyo_grid.pixel_to_grid(mouse_x, mouse_y)
                    
                    if self.puyo_grid.can_place_puyo(grid_x, grid_y):
                        puyo_type = random.choice(self.puyo_types)
                        self.puyo_grid.set_puyo(grid_x, grid_y, puyo_type)
                        logger.info(f"Manual placement: {puyo_type.name} at ({grid_x}, {grid_y})")
                        
                        # 即座にチェイン判定
                        self._execute_chain_check()
    
    def render(self, surface: pygame.Surface):
        """描画処理"""
        # ぷよぷよエリアのみの背景（全画面塗りつぶしを削除）
        puyo_area_rect = pygame.Rect(
            GRID_OFFSET_X - 10, 
            GRID_OFFSET_Y - 10, 
            GRID_WIDTH * PUYO_SIZE + 20, 
            GRID_HEIGHT * PUYO_SIZE + 20
        )
        pygame.draw.rect(surface, Colors.UI_BACKGROUND, puyo_area_rect)
        
        # グリッド描画
        self.puyo_grid.render(surface, show_grid=True)
        
        # 落下中のぷよ描画
        for puyo in self.falling_puyos:
            puyo.render(surface, self.puyo_grid)
        
        # UI描画
        self._render_ui(surface)
        
        # ゲームオーバー表示
        if not self.game_active:
            self._render_game_over_overlay(surface)
    
    def _render_ui(self, surface: pygame.Surface):
        """UI描画"""
        font_large = self.engine.fonts['large']
        font_medium = self.engine.fonts['medium']
        font_small = self.engine.fonts['small']
        
        y_offset = GRID_OFFSET_Y
        
        # タイトル
        title_text = font_large.render("Demo Mode", True, Colors.WHITE)
        surface.blit(title_text, (self.ui_start_x, y_offset))
        y_offset += 50
        
        # スコア情報
        score_text = font_medium.render(f"Score: {self.total_score:,}", True, Colors.WHITE)
        surface.blit(score_text, (self.ui_start_x, y_offset))
        y_offset += 35
        
        chains_text = font_small.render(f"Chains: {self.total_chains}", True, Colors.YELLOW)
        surface.blit(chains_text, (self.ui_start_x, y_offset))
        y_offset += 25
        
        last_score = self.puyo_grid.last_chain_score
        if last_score > 0:
            last_text = font_small.render(f"Last: {last_score}", True, Colors.CYAN)
            surface.blit(last_text, (self.ui_start_x, y_offset))
        y_offset += 35
        
        # タイミング情報
        falling_count = len(self.falling_puyos)
        if falling_count > 0:
            falling_text = font_small.render(f"Falling: {falling_count}", True, Colors.GREEN)
            surface.blit(falling_text, (self.ui_start_x, y_offset))
            y_offset += 25
        
        next_spawn = max(0, self.spawn_interval - self.spawn_timer)
        if not self.falling_puyos and self.game_active:
            spawn_text = font_small.render(f"Next: {next_spawn:.1f}s", True, Colors.LIGHT_GRAY)
            surface.blit(spawn_text, (self.ui_start_x, y_offset))
            y_offset += 30
        
        # 操作説明
        y_offset += 10
        controls_title = font_small.render("Controls:", True, Colors.WHITE)
        surface.blit(controls_title, (self.ui_start_x, y_offset))
        y_offset += 25
        
        controls = [
            "ESC - Back to Menu",
            "Enter - Main Game", 
            "R - Reset Demo",
            "",
            "While falling:",
            "A/D - Move Left/Right",
            "S - Fast Fall",
            "Space - Change Color",
            "",
            "Other:",
            "C - Execute Chain",
            "Click - Place Puyo",
        ]
        
        for control in controls:
            if control == "":
                y_offset += 5  # 空行は少しだけ間隔
                continue
            elif control in ["While falling:", "Other:"]:
                color = Colors.YELLOW  # カテゴリは黄色
            else:
                color = Colors.LIGHT_GRAY  # 通常は薄灰色
            
            control_text = font_small.render(control, True, color)
            surface.blit(control_text, (self.ui_start_x, y_offset))
            y_offset += 18
        
        # 状態表示
        if self.pending_chain_check:
            chain_progress = self.chain_delay_timer / self.chain_delay
            progress_width = 120
            progress_height = 8
            
            progress_bg = pygame.Rect(self.ui_start_x, y_offset, progress_width, progress_height)
            progress_fg = pygame.Rect(self.ui_start_x, y_offset, int(progress_width * chain_progress), progress_height)
            
            pygame.draw.rect(surface, Colors.DARK_GRAY, progress_bg)
            pygame.draw.rect(surface, Colors.YELLOW, progress_fg)
            
            status_text = font_small.render("Checking chains...", True, Colors.YELLOW)
            surface.blit(status_text, (self.ui_start_x, y_offset - 20))
    
    def _render_game_over_overlay(self, surface: pygame.Surface):
        """ゲームオーバーオーバーレイ"""
        # 半透明背景
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(128)
        overlay.fill(Colors.BLACK)
        surface.blit(overlay, (0, 0))
        
        font_title = self.engine.fonts['title']
        font_large = self.engine.fonts['large']
        font_medium = self.engine.fonts['medium']
        
        # ゲームオーバーテキスト
        game_over_text = font_title.render("DEMO COMPLETE", True, Colors.CYAN)
        text_rect = game_over_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 80))
        surface.blit(game_over_text, text_rect)
        
        # 最終スコア
        final_score_text = font_large.render(f"Final Score: {self.total_score:,}", True, Colors.WHITE)
        text_rect = final_score_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 20))
        surface.blit(final_score_text, text_rect)
        
        # 統計
        chains_text = font_medium.render(f"Total Chains: {self.total_chains}", True, Colors.YELLOW)
        text_rect = chains_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 20))
        surface.blit(chains_text, text_rect)
        
        # 操作説明
        instructions = [
            "R - Restart Demo",
            "Enter - Play Full Game", 
            "ESC - Back to Menu"
        ]
        
        for i, instruction in enumerate(instructions):
            text = font_medium.render(instruction, True, Colors.LIGHT_GRAY)
            text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 80 + i * 30))
            surface.blit(text, text_rect)


if __name__ == "__main__":
    # テスト実行
    import sys
    import os
    
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
    
    from src.core.game_engine import GameEngine
    
    logging.basicConfig(level=logging.INFO)
    
    engine = GameEngine()
    handler = ImprovedDemoHandler(engine)
    
    engine.register_state_handler(GameState.BATTLE, handler)
    engine.change_state(GameState.BATTLE)
    
    print("Starting improved demo test...")
    engine.run()