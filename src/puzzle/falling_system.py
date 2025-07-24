"""
落下システム - プレイヤー操作可能なぷよ落下制御
Drop Puzzle × Roguelike のぷよぷよゲーム部分の操作システム
"""

import pygame
import logging
from typing import List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import random

from ..core.constants import *
from .puyo_grid import PuyoGrid, PuyoPosition

logger = logging.getLogger(__name__)


class RotationDirection(Enum):
    """回転方向"""
    CLOCKWISE = 1
    COUNTER_CLOCKWISE = -1


@dataclass
class FallingPuyo:
    """落下中のぷよペア"""
    main_type: PuyoType      # メインぷよの色
    sub_type: PuyoType       # サブぷよの色
    x: int                   # 中心X座標
    y: int                   # 中心Y座標
    rotation: int = 0        # 回転状態 (0-3)
    
    def get_positions(self) -> Tuple[PuyoPosition, PuyoPosition]:
        """現在の回転状態でのぷよ位置を取得"""
        main_pos = PuyoPosition(self.x, self.y)
        
        # 回転に応じたサブぷよの相対位置
        rotation_offsets = [
            (0, -1),  # 0: 上
            (1, 0),   # 1: 右
            (0, 1),   # 2: 下
            (-1, 0),  # 3: 左
        ]
        
        offset_x, offset_y = rotation_offsets[self.rotation % 4]
        sub_pos = PuyoPosition(self.x + offset_x, self.y + offset_y)
        
        return main_pos, sub_pos
    
    def can_place(self, grid: PuyoGrid) -> bool:
        """現在位置に配置可能かチェック"""
        main_pos, sub_pos = self.get_positions()
        
        return (grid.can_place_puyo(main_pos.x, main_pos.y) and 
                grid.can_place_puyo(sub_pos.x, sub_pos.y))
    
    def can_move_to(self, grid: PuyoGrid, new_x: int, new_y: int, new_rotation: int = None) -> bool:
        """指定位置・回転に移動可能かチェック"""
        original_x, original_y, original_rotation = self.x, self.y, self.rotation
        
        # 一時的に位置を変更してチェック
        self.x = new_x
        self.y = new_y
        if new_rotation is not None:
            self.rotation = new_rotation
        
        can_place = self.can_place(grid)
        
        # 元の位置に戻す
        self.x, self.y, self.rotation = original_x, original_y, original_rotation
        
        return can_place
    
    def place_on_grid(self, grid: PuyoGrid) -> bool:
        """グリッドに配置"""
        if not self.can_place(grid):
            return False
        
        main_pos, sub_pos = self.get_positions()
        grid.set_puyo(main_pos.x, main_pos.y, self.main_type)
        grid.set_puyo(sub_pos.x, sub_pos.y, self.sub_type)
        
        return True


class FallingSystem:
    """落下システム管理クラス"""
    
    def __init__(self, grid: PuyoGrid):
        self.grid = grid
        self.current_puyo: Optional[FallingPuyo] = None
        self.next_puyo: Optional[FallingPuyo] = None
        
        # タイミング制御
        self.fall_timer = 0.0
        self.fall_interval = FALL_SPEED
        self.fast_fall_active = False
        
        # 入力制御
        self.move_repeat_timer = 0.0
        self.move_repeat_interval = 0.15  # キーリピート間隔
        self.rotation_cooldown = 0.0
        self.rotation_cooldown_time = 0.2  # 回転クールダウン
        
        # ゲーム状態
        self.game_active = True
        self.puyo_locked = False
        self.lock_delay = 0.3  # 着地後のロック猶予時間（短縮）
        self.lock_timer = 0.0
        
        # スコア・統計
        self.total_score = 0
        self.lines_cleared = 0
        self.level = 1
        
        # ぷよ生成用
        self.puyo_bag = self._create_puyo_bag()
        self.bag_index = 0
        
        logger.info("FallingSystem initialized")
        
        # 最初のぷよを生成
        self._spawn_next_puyo()
    
    def _create_puyo_bag(self) -> List[PuyoType]:
        """ぷよバッグ（色の組み合わせ）を生成"""
        # 基本色を2個ずつ含むバッグ
        colors = [PuyoType.RED, PuyoType.BLUE, PuyoType.GREEN, 
                 PuyoType.YELLOW, PuyoType.PURPLE]
        bag = colors * 2  # 各色2個
        random.shuffle(bag)
        return bag
    
    def _get_next_puyo_type(self) -> PuyoType:
        """次のぷよタイプを取得"""
        if self.bag_index >= len(self.puyo_bag):
            # バッグが空になったら新しいバッグを作成
            self.puyo_bag = self._create_puyo_bag()
            self.bag_index = 0
        
        puyo_type = self.puyo_bag[self.bag_index]
        self.bag_index += 1
        return puyo_type
    
    def _spawn_next_puyo(self):
        """次のぷよを生成"""
        if self.next_puyo is None:
            # 最初の生成
            main_type = self._get_next_puyo_type()
            sub_type = self._get_next_puyo_type()
            self.next_puyo = FallingPuyo(main_type, sub_type, 0, 0)
        
        # 現在のぷよを設定
        self.current_puyo = self.next_puyo
        self.current_puyo.x = GRID_WIDTH // 2
        self.current_puyo.y = 0
        self.current_puyo.rotation = 0
        
        # 次のぷよを生成
        main_type = self._get_next_puyo_type()
        sub_type = self._get_next_puyo_type()
        self.next_puyo = FallingPuyo(main_type, sub_type, 0, 0)
        
        # 配置可能性チェック（初期化時はスキップ）
        if hasattr(self, '_initialized') and self.current_puyo is not None and not self.current_puyo.can_place(self.grid):
            self.game_active = False
            logger.info("Game Over - Cannot spawn new puyo")
            return
        
        # 初期化フラグ設定
        self._initialized = True
        
        # 状態リセット
        self.fall_timer = 0.0
        self.puyo_locked = False
        self.lock_timer = 0.0
        self.fast_fall_active = False
        
        logger.info(f"Spawned new puyo: {self.current_puyo.main_type.name} + {self.current_puyo.sub_type.name}")
    
    def update(self, dt: float):
        """システム更新"""
        if not self.game_active or self.current_puyo is None:
            return
        
        # タイマー更新
        self.fall_timer += dt
        self.move_repeat_timer = max(0, self.move_repeat_timer - dt)
        self.rotation_cooldown = max(0, self.rotation_cooldown - dt)
        
        # 落下処理
        self._handle_falling(dt)
        
        # ロック処理
        if self.puyo_locked:
            self._handle_locking(dt)
    
    def _handle_falling(self, dt: float):
        """落下処理"""
        fall_interval = FAST_FALL_SPEED if self.fast_fall_active else self.fall_interval
        
        if self.fall_timer >= fall_interval:
            if self._try_move_down():
                self.fall_timer = 0.0
                self.puyo_locked = False
                self.lock_timer = 0.0
            else:
                # 着地した
                if not self.puyo_locked:
                    self.puyo_locked = True
                    self.lock_timer = 0.0
                    logger.debug("Puyo locked - starting lock delay")
    
    def _handle_locking(self, dt: float):
        """ロック処理"""
        self.lock_timer += dt
        
        # ロック猶予時間中に移動できればロック解除
        if self._try_move_down():
            self.puyo_locked = False
            self.lock_timer = 0.0
            self.fall_timer = 0.0
            logger.debug("Lock cancelled - puyo can still fall")
            return
        
        # ロック時間経過で固定
        if self.lock_timer >= self.lock_delay:
            self._lock_current_puyo()
    
    def _try_move_down(self) -> bool:
        """下移動を試行"""
        if self.current_puyo is None:
            return False
        
        if self.current_puyo.can_move_to(self.grid, self.current_puyo.x, self.current_puyo.y + 1):
            self.current_puyo.y += 1
            return True
        return False
    
    def _lock_current_puyo(self):
        """現在のぷよを固定"""
        if self.current_puyo is None:
            return
        
        # グリッドに配置
        if self.current_puyo.place_on_grid(self.grid):
            logger.info(f"Puyo locked at ({self.current_puyo.x}, {self.current_puyo.y})")
            
            # 連鎖チェックと実行
            score, eliminated = self.grid.execute_full_chain_sequence()
            if eliminated > 0:
                self.total_score += score
                self.lines_cleared += eliminated
                logger.info(f"Chain executed: {eliminated} eliminated, score: {score}")
            
            # 次のぷよ生成
            self._spawn_next_puyo()
        else:
            logger.error("Failed to place puyo on grid")
            self.game_active = False
    
    def handle_input(self, keys_pressed: dict, events: List[pygame.event.Event]):
        """入力処理"""
        if not self.game_active or self.current_puyo is None:
            return
        
        # 継続的な入力（キーが押され続けている）
        self._handle_continuous_input(keys_pressed)
        
        # 単発入力（キーが押された瞬間）
        self._handle_discrete_input(events)
    
    def _handle_continuous_input(self, keys_pressed: dict):
        """継続的な入力処理"""
        # 横移動
        if self.move_repeat_timer <= 0:
            moved = False
            
            if keys_pressed.get(pygame.K_a, False) or keys_pressed.get(pygame.K_LEFT, False):
                if self._try_move_horizontal(-1):
                    moved = True
            elif keys_pressed.get(pygame.K_d, False) or keys_pressed.get(pygame.K_RIGHT, False):
                if self._try_move_horizontal(1):
                    moved = True
            
            if moved:
                self.move_repeat_timer = self.move_repeat_interval
        
        # 高速落下
        fast_fall_requested = (keys_pressed.get(pygame.K_s, False) or 
                              keys_pressed.get(pygame.K_DOWN, False))
        self.fast_fall_active = fast_fall_requested
    
    def _handle_discrete_input(self, events: List[pygame.event.Event]):
        """単発入力処理"""
        for event in events:
            if event.type == pygame.KEYDOWN:
                # 回転
                if event.key in [pygame.K_SPACE, pygame.K_UP] and self.rotation_cooldown <= 0:
                    if self._try_rotate(RotationDirection.CLOCKWISE):
                        self.rotation_cooldown = self.rotation_cooldown_time
                
                elif event.key == pygame.K_w and self.rotation_cooldown <= 0:
                    if self._try_rotate(RotationDirection.COUNTER_CLOCKWISE):
                        self.rotation_cooldown = self.rotation_cooldown_time
                
                # ハードドロップ
                elif event.key == pygame.K_q:
                    self._hard_drop()
    
    def _try_move_horizontal(self, direction: int) -> bool:
        """横移動を試行"""
        if self.current_puyo is None:
            return False
        
        new_x = self.current_puyo.x + direction
        
        if self.current_puyo.can_move_to(self.grid, new_x, self.current_puyo.y):
            self.current_puyo.x = new_x
            
            # ロック状態の場合、移動できればロック解除
            if self.puyo_locked and self._try_move_down():
                self.puyo_locked = False
                self.lock_timer = 0.0
            
            return True
        return False
    
    def _try_rotate(self, direction: RotationDirection) -> bool:
        """回転を試行"""
        if self.current_puyo is None:
            return False
        
        new_rotation = (self.current_puyo.rotation + direction.value) % 4
        
        # 基本位置で回転チェック
        if self.current_puyo.can_move_to(self.grid, self.current_puyo.x, self.current_puyo.y, new_rotation):
            self.current_puyo.rotation = new_rotation
            logger.debug(f"Rotated to {new_rotation}")
            return True
        
        # Wall Kick（壁蹴り）を試行
        kick_offsets = [(-1, 0), (1, 0), (0, -1), (-1, -1), (1, -1)]
        
        for offset_x, offset_y in kick_offsets:
            test_x = self.current_puyo.x + offset_x
            test_y = self.current_puyo.y + offset_y
            
            if self.current_puyo.can_move_to(self.grid, test_x, test_y, new_rotation):
                self.current_puyo.x = test_x
                self.current_puyo.y = test_y
                self.current_puyo.rotation = new_rotation
                logger.debug(f"Wall kick successful: offset ({offset_x}, {offset_y})")
                return True
        
        return False
    
    def _hard_drop(self):
        """ハードドロップ（即座に着地）"""
        if self.current_puyo is None:
            return
        
        # 可能な限り下に移動
        drop_distance = 0
        while self._try_move_down():
            drop_distance += 1
        
        if drop_distance > 0:
            logger.info(f"Hard drop: {drop_distance} cells")
            # 即座にロック
            self._lock_current_puyo()
    
    def reset(self):
        """システムリセット"""
        self.current_puyo = None
        self.next_puyo = None
        self.game_active = True
        self.puyo_locked = False
        self.fall_timer = 0.0
        self.lock_timer = 0.0
        self.total_score = 0
        self.lines_cleared = 0
        self.level = 1
        
        # 新しいバッグ生成
        self.puyo_bag = self._create_puyo_bag()
        self.bag_index = 0
        
        # グリッドクリア
        self.grid.clear()
        
        # 最初のぷよ生成
        self._spawn_next_puyo()
        
        logger.info("FallingSystem reset")
    
    def render_falling_puyo(self, surface: pygame.Surface):
        """落下中のぷよを描画"""
        if self.current_puyo is None:
            return
        
        main_pos, sub_pos = self.current_puyo.get_positions()
        
        # メインぷよ描画
        self._render_puyo_at_position(surface, main_pos, self.current_puyo.main_type)
        
        # サブぷよ描画
        self._render_puyo_at_position(surface, sub_pos, self.current_puyo.sub_type)
        
        # ゴーストピース（着地予想位置）
        self._render_ghost_piece(surface)
    
    def _render_puyo_at_position(self, surface: pygame.Surface, pos: PuyoPosition, puyo_type: PuyoType):
        """指定位置にぷよを描画"""
        if not pos.is_valid():
            return
        
        pixel_x, pixel_y = self.grid.grid_to_pixel(pos.x, pos.y)
        
        rect = pygame.Rect(
            pixel_x + 2,
            pixel_y + 2,
            self.grid.puyo_size - 4,
            self.grid.puyo_size - 4
        )
        
        color = PUYO_COLORS[puyo_type]
        center = rect.center
        radius = (self.grid.puyo_size - 4) // 2
        
        # ぷよ本体
        pygame.draw.circle(surface, color, center, radius)
        pygame.draw.circle(surface, Colors.WHITE, center, radius, 2)
        
        # ハイライト
        highlight_radius = radius // 3
        highlight_center = (center[0] - radius//3, center[1] - radius//3)
        pygame.draw.circle(surface, Colors.WHITE, highlight_center, highlight_radius)
    
    def _render_ghost_piece(self, surface: pygame.Surface):
        """ゴーストピース（着地予想位置）を描画"""
        if self.current_puyo is None:
            return
        
        # 着地位置を計算
        ghost_puyo = FallingPuyo(
            self.current_puyo.main_type,
            self.current_puyo.sub_type,
            self.current_puyo.x,
            self.current_puyo.y,
            self.current_puyo.rotation
        )
        
        # 可能な限り下に移動
        while ghost_puyo.can_move_to(self.grid, ghost_puyo.x, ghost_puyo.y + 1):
            ghost_puyo.y += 1
        
        # 現在位置と同じ場合は描画しない
        if ghost_puyo.y == self.current_puyo.y:
            return
        
        main_pos, sub_pos = ghost_puyo.get_positions()
        
        # 半透明で描画
        self._render_ghost_puyo_at_position(surface, main_pos, self.current_puyo.main_type)
        self._render_ghost_puyo_at_position(surface, sub_pos, self.current_puyo.sub_type)
    
    def _render_ghost_puyo_at_position(self, surface: pygame.Surface, pos: PuyoPosition, puyo_type: PuyoType):
        """ゴーストぷよを指定位置に描画"""
        if not pos.is_valid():
            return
        
        pixel_x, pixel_y = self.grid.grid_to_pixel(pos.x, pos.y)
        
        rect = pygame.Rect(
            pixel_x + 4,
            pixel_y + 4,
            self.grid.puyo_size - 8,
            self.grid.puyo_size - 8
        )
        
        color = PUYO_COLORS[puyo_type]
        
        # 半透明の円で描画
        center = rect.center
        radius = (self.grid.puyo_size - 8) // 2
        
        # 輪郭のみ描画
        pygame.draw.circle(surface, color, center, radius, 2)
    
    def render_next_puyo(self, surface: pygame.Surface, x: int, y: int):
        """次のぷよを指定位置に描画"""
        if self.next_puyo is None:
            return
        
        puyo_size = 30  # 小さめサイズ
        
        # メインぷよ
        main_rect = pygame.Rect(x, y, puyo_size, puyo_size)
        main_color = PUYO_COLORS[self.next_puyo.main_type]
        pygame.draw.circle(surface, main_color, main_rect.center, puyo_size // 2 - 2)
        pygame.draw.circle(surface, Colors.WHITE, main_rect.center, puyo_size // 2 - 2, 1)
        
        # サブぷよ
        sub_rect = pygame.Rect(x, y + puyo_size + 5, puyo_size, puyo_size)
        sub_color = PUYO_COLORS[self.next_puyo.sub_type]
        pygame.draw.circle(surface, sub_color, sub_rect.center, puyo_size // 2 - 2)
        pygame.draw.circle(surface, Colors.WHITE, sub_rect.center, puyo_size // 2 - 2, 1)


if __name__ == "__main__":
    # テスト実行
    logging.basicConfig(level=logging.INFO)
    pygame.init()
    
    grid = PuyoGrid()
    falling_system = FallingSystem(grid)
    
    print("FallingSystem test completed")
    
    pygame.quit()