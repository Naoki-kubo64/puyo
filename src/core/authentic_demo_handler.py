"""
本格ぷよぷよデモハンドラー - 2個1組のぷよペアで本家と同じ動作
Drop Puzzle × Roguelike の完全版ぷよぷよデモ
"""

import pygame
import logging
import random
import math
from typing import List, Optional, Tuple

from .constants import *
from .game_engine import GameEngine
from .sound_manager import play_se, SoundType
from ..puzzle.puyo_grid import PuyoGrid

logger = logging.getLogger(__name__)


class PuyoPair:
    """本格的なぷよペア（2個1組）"""
    
    def __init__(self, main_type: PuyoType, sub_type: PuyoType, center_x: int):
        # ぷよタイプ
        self.main_type = main_type  # 軸ぷよ（中心）
        self.sub_type = sub_type    # 子ぷよ（回転する）
        
        # 位置（浮動小数点で滑らかな移動）
        self.center_x = float(center_x)  # 軸ぷよのX座標
        self.center_y = -1.0             # 軸ぷよのY座標
        
        # 回転状態（0=上, 1=右, 2=下, 3=左）
        self.rotation = 0
        
        # 動作状態（本家風タイミング）
        self.active = True
        self.fall_speed = 0.4  # セル/秒（本家の通常落下速度）
        self.fast_falling = False
        self.fast_fall_speed = 15.0  # 本家風高速落下（高速）
        
        # 分離状態（片方が着地した場合）
        self.main_fixed = False  # 軸ぷよが固定されたか
        self.sub_fixed = False   # 子ぷよが固定されたか
        self.separated = False   # 分離が発生したか
        
        # 本家風接地猶予システム（修正版）
        self.grounded = False  # 接地状態
        self.grounded_timer = 0.0  # 接地猶予タイマー
        self.grounded_grace_time = 0.5  # 接地猶予時間（修正：0.5秒に延長）
        self.move_reset_count = 0  # 移動によるリセット回数
        self.max_move_resets = 15  # 最大リセット回数（修正：15回に増加）
        
        # 自動固定システム（操作なしでも固定されるように）
        self.no_input_timer = 0.0  # 無操作時間
        self.auto_lock_time = 1.0  # 無操作時自動固定時間（1秒）
        
        # 分離後操作可能システム
        self.post_separation_control_time = 0.2  # 分離後操作可能時間（0.2秒）
        self.post_separation_timer = 0.0  # 分離後タイマー
        self.remaining_puyo_pos = None  # 残りのぷよの位置（分離後制御用）
    
    def get_positions(self) -> Tuple[Tuple[int, int], Tuple[int, int]]:
        """現在の軸ぷよと子ぷよの位置を取得"""
        main_pos = (int(self.center_x), int(self.center_y))
        
        # 回転に応じた子ぷよの相対位置
        offsets = [
            (0, -1),  # 0: 上
            (1, 0),   # 1: 右
            (0, 1),   # 2: 下
            (-1, 0)   # 3: 左
        ]
        
        offset_x, offset_y = offsets[self.rotation]
        sub_pos = (int(self.center_x + offset_x), int(self.center_y + offset_y))
        
        return main_pos, sub_pos
    
    def can_place_at(self, grid: PuyoGrid, test_x: float = None, test_y: float = None, test_rotation: int = None) -> bool:
        """指定位置・回転で配置可能かチェック（重なり防止強化版）"""
        # テスト用パラメータ
        center_x = test_x if test_x is not None else self.center_x
        center_y = test_y if test_y is not None else self.center_y
        rotation = test_rotation if test_rotation is not None else self.rotation
        
        # 浮動小数点の位置を厳密にチェック（重なり防止のため）
        # 微細な浮動小数点誤差を排除するための厳密な丸め処理
        main_x, main_y = int(round(center_x + 1e-10)), int(round(center_y + 1e-10))
        
        # 回転オフセット
        offsets = [(0, -1), (1, 0), (0, 1), (-1, 0)]
        offset_x, offset_y = offsets[rotation]
        sub_x, sub_y = main_x + offset_x, main_y + offset_y
        
        # 画面上部は許可（但し、画面内に入る場合は厳密チェック）
        if main_y < 0 and sub_y < 0:
            return True
        
        # 境界チェック（厳密）
        if (main_x < 0 or main_x >= GRID_WIDTH or main_y >= GRID_HEIGHT or
            sub_x < 0 or sub_x >= GRID_WIDTH or sub_y >= GRID_HEIGHT):
            return False
        
        # グリッド衝突チェック（厳密 - 重なりを絶対に防ぐ）
        main_can_place = main_y < 0 or grid.can_place_puyo(main_x, main_y)
        sub_can_place = sub_y < 0 or grid.can_place_puyo(sub_x, sub_y)
        
        result = main_can_place and sub_can_place
        
        # デバッグ：重なりの可能性がある場合はログ出力
        if not result and main_y >= 0 and sub_y >= 0:
            logger.debug(f"Placement blocked: main=({main_x},{main_y}), sub=({sub_x},{sub_y}), main_ok={main_can_place}, sub_ok={sub_can_place}")
        
        return result
    
    def try_move_horizontal(self, direction: int, grid: PuyoGrid) -> bool:
        """横移動を試行（SE付き・接地猶予リセット・分離後制御対応）"""
        # 分離後は残りのぷよのみ制御可能
        if self.separated:
            return self._try_move_remaining_puyo_horizontal(direction, grid)
        
        new_x = self.center_x + direction
        
        # 境界チェック付きで移動を試行
        if 0 <= new_x < GRID_WIDTH and self.can_place_at(grid, new_x, self.center_y, self.rotation):
            self.center_x = new_x
            # 移動SE再生
            play_se(SoundType.MOVE)
            # 接地猶予システムのリセット
            self._reset_grounded_timer()
            return True
        return False
    
    def _try_move_remaining_puyo_horizontal(self, direction: int, grid: PuyoGrid) -> bool:
        """分離後の残りぷよの横移動"""
        if self.post_separation_timer >= self.post_separation_control_time:
            return False
        
        # 残りのぷよを判定
        if not self.main_fixed:
            # 軸ぷよが残っている場合
            new_x = self.center_x + direction
            current_y = max(0, int(self.center_y))  # Y座標を有効範囲に制限
            if (0 <= new_x < GRID_WIDTH and 
                current_y < GRID_HEIGHT and 
                grid.can_place_puyo(int(new_x), current_y)):
                self.center_x = new_x
                play_se(SoundType.MOVE)
                logger.debug(f"Post-separation main puyo moved to ({new_x}, {current_y})")
                return True
        elif not self.sub_fixed:
            # 子ぷよが残っている場合
            main_pos, sub_pos = self.get_positions()
            new_sub_x = sub_pos[0] + direction
            sub_y = max(0, min(sub_pos[1], GRID_HEIGHT - 1))  # Y座標を有効範囲に制限
            
            # 子ぷよの新しい位置を軸ぷよ座標で計算
            offsets = [(0, -1), (1, 0), (0, 1), (-1, 0)]
            offset_x, offset_y = offsets[self.rotation]
            new_center_x = new_sub_x - offset_x
            
            if (0 <= new_sub_x < GRID_WIDTH and 
                0 <= sub_y < GRID_HEIGHT and
                grid.can_place_puyo(new_sub_x, sub_y)):
                self.center_x = new_center_x
                play_se(SoundType.MOVE)
                logger.debug(f"Post-separation sub puyo moved to ({new_sub_x}, {sub_y})")
                return True
        
        return False
    
    def try_rotate(self, clockwise: bool, grid: PuyoGrid) -> bool:
        """回転を試行（本家風回転挙動・分離後は回転不可）"""
        # 分離後は回転不可
        if self.separated:
            return False
        
        direction = 1 if clockwise else -1
        new_rotation = (self.rotation + direction) % 4
        
        # 本家では軸ぷよ中心の回転が基本
        if self.can_place_at(grid, self.center_x, self.center_y, new_rotation):
            self.rotation = new_rotation
            # 回転SE再生
            play_se(SoundType.ROTATE)
            # 接地猶予システムのリセット
            self._reset_grounded_timer()
            logger.debug(f"Rotation successful: {self.rotation}")
            return True
        
        # 本家風壁蹴り（回転方向と現在の状態に依存）
        authentic_kicks = self._get_authentic_wall_kicks(clockwise, self.rotation, new_rotation)
        
        for kick_x, kick_y in authentic_kicks:
            test_x = self.center_x + kick_x
            test_y = self.center_y + kick_y
            
            # グリッド範囲内チェック
            if 0 <= test_x < GRID_WIDTH and test_y >= -2:  # 上部は少し余裕を持たせる
                if self.can_place_at(grid, test_x, test_y, new_rotation):
                    # キックの有効性チェック
                    if self._is_authentic_kick_valid(grid, test_x, test_y, new_rotation):
                        self.center_x = test_x
                        self.center_y = test_y
                        self.rotation = new_rotation
                        # キック成功時も回転SE再生
                        play_se(SoundType.ROTATE)
                        logger.debug(f"Authentic wall kick: ({kick_x}, {kick_y})")
                        return True
        
        # 回転不可
        logger.debug("Rotation failed - no valid position found")
        return False
    
    def _get_authentic_wall_kicks(self, clockwise: bool, from_rotation: int, to_rotation: int) -> List[Tuple[int, int]]:
        """本家風壁蹴りテーブルを取得"""
        # 本家ぷよぷよの壁蹴りは比較的シンプル
        # 基本的には横方向と上方向の移動を試行
        
        if clockwise:
            # 時計回り回転の壁蹴りパターン
            if from_rotation == 0 and to_rotation == 1:  # 上→右
                return [(-1, 0), (0, -1), (-1, -1)]
            elif from_rotation == 1 and to_rotation == 2:  # 右→下
                return [(0, -1), (-1, 0), (-1, -1)]
            elif from_rotation == 2 and to_rotation == 3:  # 下→左
                return [(1, 0), (0, -1), (1, -1)]
            elif from_rotation == 3 and to_rotation == 0:  # 左→上
                return [(0, -1), (1, 0), (1, -1)]
        else:
            # 反時計回り回転の壁蹴りパターン
            if from_rotation == 0 and to_rotation == 3:  # 上→左
                return [(1, 0), (0, -1), (1, -1)]
            elif from_rotation == 3 and to_rotation == 2:  # 左→下
                return [(0, -1), (1, 0), (1, -1)]
            elif from_rotation == 2 and to_rotation == 1:  # 下→右
                return [(-1, 0), (0, -1), (-1, -1)]
            elif from_rotation == 1 and to_rotation == 0:  # 右→上
                return [(0, -1), (-1, 0), (-1, -1)]
        
        # デフォルトの壁蹴りパターン（対称的な試行）
        return [(-1, 0), (1, 0), (0, -1), (-1, -1), (1, -1)]
    
    def _is_authentic_kick_valid(self, grid: PuyoGrid, test_x: float, test_y: float, test_rotation: int) -> bool:
        """本家風キックの有効性チェック（厳密な判定）"""
        # 新しい位置での軸ぷよと子ぷよの位置を計算
        main_x, main_y = int(test_x), int(test_y)
        
        offsets = [(0, -1), (1, 0), (0, 1), (-1, 0)]
        offset_x, offset_y = offsets[test_rotation]
        sub_x, sub_y = main_x + offset_x, main_y + offset_y
        
        # 境界チェック（本家では厳密）
        if main_x < 0 or main_x >= GRID_WIDTH:
            return False
        if sub_x < 0 or sub_x >= GRID_WIDTH:
            return False
        
        # 天井チェック（上部は多少の余裕を持たせる）
        if main_y < -1 or sub_y < -1:
            return False
        
        # 底面チェック
        if main_y >= GRID_HEIGHT or sub_y >= GRID_HEIGHT:
            return False
        
        # 軸ぷよの衝突チェック
        if main_y >= 0 and not grid.can_place_puyo(main_x, main_y):
            return False
        
        # 子ぷよの衝突チェック
        if sub_y >= 0 and not grid.can_place_puyo(sub_x, sub_y):
            return False
        
        # 本家風の追加チェック：回転後に不自然な位置にならないか
        return self._is_rotation_natural(test_x, test_y, test_rotation, main_x, main_y, sub_x, sub_y)
    
    def _is_rotation_natural(self, test_x: float, test_y: float, test_rotation: int, 
                           main_x: int, main_y: int, sub_x: int, sub_y: int) -> bool:
        """回転が自然かどうかチェック（本家風の制約）"""
        # 基本的には軸ぷよを中心とした回転なので、
        # 軸ぷよの位置が大きく変わらないことを確認
        
        # 軸ぷよの位置変化をチェック
        original_main_x = int(self.center_x)
        original_main_y = int(self.center_y)
        
        # 軸ぷよが1マス以上移動する場合は制限
        if abs(main_x - original_main_x) > 1 or abs(main_y - original_main_y) > 1:
            return False
        
        # 子ぷよが軸ぷよの周囲8方向内にあることを確認（本家の制約）
        dx = abs(sub_x - main_x)
        dy = abs(sub_y - main_y)
        
        # 隣接する4方向のみ許可（本家の制約）
        if not ((dx == 1 and dy == 0) or (dx == 0 and dy == 1)):
            return False
        
        return True
    
    def _safe_fall_to_target(self, grid: PuyoGrid, target_y: float) -> bool:
        """安全な高速落下処理（整数座標での段階的移動）"""
        moved = False
        current_grid_y = int(self.center_y)
        target_grid_y = int(target_y)
        
        # 現在位置から目標位置まで1セルずつ移動
        while current_grid_y < target_grid_y and current_grid_y < GRID_HEIGHT - 1:
            next_y = current_grid_y + 1
            
            # 次の位置で配置可能かチェック
            if self.can_place_at(grid, self.center_x, float(next_y), self.rotation):
                # 安全に移動可能
                self.center_y = float(next_y)
                current_grid_y = next_y
                moved = True
                logger.debug(f"Fast fall: safely moved to y={next_y}")
            else:
                # 衝突が発生：現在の位置で停止
                logger.debug(f"Fast fall stopped: collision detected at y={next_y}")
                break
        
        # 目標が整数位置でない場合の微調整
        if moved and target_y > self.center_y:
            # 最後の位置で微調整が可能かチェック
            if self.can_place_at(grid, self.center_x, target_y, self.rotation):
                self.center_y = min(target_y, GRID_HEIGHT - 1)
        
        return moved
    
    def _perform_safe_fall(self, grid: PuyoGrid, old_y: float, target_y: float, step_size: float):
        """安全な落下処理（重なり完全防止版）"""
        current_y = old_y
        last_safe_y = old_y
        
        while current_y < target_y:
            # 次のステップ位置を計算
            next_y = current_y + step_size
            
            # 目標を超えないように制限
            if next_y > target_y:
                next_y = target_y
            
            # 境界チェック - 底に到達したら強制的に底の位置に設定
            if next_y >= GRID_HEIGHT - 1:
                # 底での最終チェック
                final_y = float(GRID_HEIGHT - 1)
                if self.can_place_at(grid, self.center_x, final_y, self.rotation):
                    current_y = final_y
                    logger.debug(f"Reached bottom: safely placed at y={current_y}")
                else:
                    # 底でも重なる場合は1つ上の安全な位置に
                    current_y = last_safe_y
                    logger.debug(f"Bottom placement blocked: staying at safe y={current_y:.2f}")
                break
            
            # 次の位置で配置可能かチェック（厳密）
            if self.can_place_at(grid, self.center_x, next_y, self.rotation):
                # 安全に移動可能
                last_safe_y = current_y  # 最後の安全な位置を記録
                current_y = next_y
            else:
                # 衝突が発生：最後の安全な位置で停止
                logger.debug(f"Fall stopped to prevent overlap: safe y={current_y:.2f}, blocked y={next_y:.2f}")
                break
        
        self.center_y = current_y
    
    def _is_position_safe(self, grid: PuyoGrid, test_x: float, test_y: float, test_rotation: int) -> bool:
        """位置が安全かチェック（重複防止用の厳密判定）"""
        # 整数グリッド位置での判定
        main_x, main_y = int(test_x), int(test_y)
        
        # 回転状態に応じた子ぷよの位置
        offsets = [(0, -1), (1, 0), (0, 1), (-1, 0)]
        offset_x, offset_y = offsets[test_rotation]
        sub_x, sub_y = main_x + offset_x, main_y + offset_y
        
        # 軸ぷよの安全性チェック
        if main_y >= 0:  # 画面内の場合
            if main_x < 0 or main_x >= GRID_WIDTH or main_y >= GRID_HEIGHT:
                return False
            if not grid.can_place_puyo(main_x, main_y):
                return False
        
        # 子ぷよの安全性チェック
        if sub_y >= 0:  # 画面内の場合
            if sub_x < 0 or sub_x >= GRID_WIDTH or sub_y >= GRID_HEIGHT:
                return False
            if not grid.can_place_puyo(sub_x, sub_y):
                return False
        
        return True
    
    def update(self, dt: float, grid: PuyoGrid) -> bool:
        """更新処理 - 完全に着地したらTrueを返す"""
        if not self.active:
            return False
        
        # 接地猶予タイマー更新は _check_landing 内で行う（重複を避けるため）
        
        # 分離後操作可能タイマー更新
        if self.separated:
            self.post_separation_timer += dt
        
        # 落下速度設定
        current_speed = self.fast_fall_speed if self.fast_falling else self.fall_speed
        
        # 落下処理（段階的移動で衝突判定を確実に行う）
        old_y = self.center_y
        target_y = self.center_y + current_speed * dt
        
        # 落下処理（最適化：段階的移動で重複防止）
        if self.fast_falling:
            # 高速落下：適度なステップサイズで安全かつスムーズな移動
            self._perform_safe_fall(grid, old_y, target_y, step_size=0.1)
        else:
            # 通常落下：小さなステップサイズで精密な制御
            self._perform_safe_fall(grid, old_y, target_y, step_size=0.05)
        
        # 着地判定
        return self._check_landing(grid, dt)
    
    def _check_landing(self, grid: PuyoGrid, dt: float) -> bool:
        """着地判定と接地猶予システム（修正版）"""
        main_pos, sub_pos = self.get_positions()
        main_x, main_y = main_pos
        sub_x, sub_y = sub_pos
        
        # より確実な接地判定：複数の条件をチェック
        is_grounded = False
        grounded_reason = ""
        
        # 1. 底に到達しているかチェック
        if main_y >= GRID_HEIGHT - 1 or sub_y >= GRID_HEIGHT - 1:
            is_grounded = True
            grounded_reason = "reached bottom"
        
        # 2. 下にぷよがあるかチェック（より大きな距離で確実に）
        elif not self.can_place_at(grid, self.center_x, self.center_y + 0.5, self.rotation):
            is_grounded = True
            grounded_reason = "puyo below"
            
        # 3. 現在位置の直下に障害物があるかチェック
        elif ((main_y + 1 < GRID_HEIGHT and not grid.can_place_puyo(main_x, main_y + 1)) or
              (sub_y + 1 < GRID_HEIGHT and not grid.can_place_puyo(sub_x, sub_y + 1))):
            is_grounded = True
            grounded_reason = "obstacle below"
        
        if is_grounded:
            logger.debug(f"Pair grounded at y={self.center_y:.2f} - {grounded_reason}")
        
        if is_grounded:
            if not self.grounded:
                # 接地開始
                self.grounded = True
                self.grounded_timer = 0.0
                self.no_input_timer = 0.0
                self.move_reset_count = 0
                logger.info(f"*** PAIR GROUNDED at y={self.center_y:.2f} - starting grace timer ***")
            
            # タイマーを更新（実際のデルタタイムを使用）
            self.grounded_timer += dt
            self.no_input_timer += dt
            
            # 固定条件をチェック（いずれかの条件で固定）
            should_lock = False
            lock_reason = ""
            
            # 1. 接地猶予時間経過
            if self.grounded_timer >= self.grounded_grace_time:
                should_lock = True
                lock_reason = f"grace time expired ({self.grounded_timer:.3f}s)"
            
            # 2. 無操作時間経過（自動固定）
            elif self.no_input_timer >= self.auto_lock_time:
                should_lock = True
                lock_reason = f"auto-lock time expired ({self.no_input_timer:.3f}s)"
            
            # 3. 移動リセット回数上限（操作しすぎ防止）
            elif self.move_reset_count >= self.max_move_resets:
                should_lock = True
                lock_reason = f"max resets reached ({self.move_reset_count}/{self.max_move_resets})"
            
            if should_lock:
                logger.info(f"*** LOCKING PAIR: {lock_reason} ***")
                result = self._execute_pair_lock(grid)
                logger.info(f"*** LOCK RESULT: {result} ***")
                return result
        else:
            # 接地していない場合はリセット
            if self.grounded:
                self.grounded = False
                self.grounded_timer = 0.0
                self.no_input_timer = 0.0
                self.move_reset_count = 0
                logger.debug("Puyo pair no longer grounded - resetting timers")
        
        return False
    
    def _execute_pair_lock(self, grid: PuyoGrid) -> bool:
        """ペアの固定処理（シンプル版）"""
        main_pos, sub_pos = self.get_positions()
        main_x, main_y = main_pos
        sub_x, sub_y = sub_pos
        
        logger.info(f"=== EXECUTING PAIR LOCK ===")
        logger.info(f"Main puyo: ({main_x}, {main_y}) Type: {self.main_type}")
        logger.info(f"Sub puyo: ({sub_x}, {sub_y}) Type: {self.sub_type}")
        
        # 両方のぷよを同時に固定
        lock_count = 0
        if main_y >= 0:
            try:
                grid.set_puyo(main_x, main_y, self.main_type)
                self.main_fixed = True
                lock_count += 1
                logger.info(f"✓ Main puyo LOCKED at ({main_x}, {main_y})")
            except Exception as e:
                logger.error(f"✗ Failed to lock main puyo: {e}")
        
        if sub_y >= 0:
            try:
                grid.set_puyo(sub_x, sub_y, self.sub_type)
                self.sub_fixed = True
                lock_count += 1
                logger.info(f"✓ Sub puyo LOCKED at ({sub_x}, {sub_y})")
            except Exception as e:
                logger.error(f"✗ Failed to lock sub puyo: {e}")
        
        # ペアの制御を終了
        self.active = False
        logger.info(f"=== PAIR LOCK COMPLETED ({lock_count} puyos locked) - PAIR DEACTIVATED ===")
        return True
    
    def _is_puyo_grounded(self, x: int, y: int, grid: PuyoGrid) -> bool:
        """個別ぷよの接地判定"""
        if y < 0:
            return False
        if y >= GRID_HEIGHT - 1:  # 底に到達
            return True
        if y + 1 < GRID_HEIGHT and not grid.can_place_puyo(x, y + 1):
            return True
        return False
    
    def _reset_grounded_timer(self):
        """接地猶予タイマーをリセット（移動・回転時に呼び出し）"""
        if self.grounded and self.move_reset_count < self.max_move_resets:
            self.grounded_timer = 0.0
            self.no_input_timer = 0.0  # 無操作タイマーもリセット
            self.move_reset_count += 1
            logger.debug(f"Grounded timer reset (count: {self.move_reset_count}/{self.max_move_resets})")
    
    def _handle_immediate_separation(self, grid: PuyoGrid):
        """本家風即座分離処理 - 片方が着地したら残りを即座に落下"""
        # 分離が発生したらペアの制御を無効化
        logger.debug("Puyo pair separated - handling immediate drop")
        
        # 固定されていないぷよを即座に落下させる
        if not self.main_fixed:
            # 軸ぷよが固定されていない場合、真下に即座に落下
            main_x = int(self.center_x)
            
            # 境界チェック
            if 0 <= main_x < GRID_WIDTH:
                drop_y = grid.get_drop_position(main_x)
                # drop_yが有効な範囲内かチェック
                if 0 <= drop_y < GRID_HEIGHT:
                    grid.set_puyo(main_x, drop_y, self.main_type)
                    self.main_fixed = True
                    logger.debug(f"Main puyo immediately dropped to ({main_x}, {drop_y})")
                else:
                    # 落下位置が無効な場合は現在位置で強制固定
                    current_y = max(0, min(int(self.center_y), GRID_HEIGHT - 1))
                    if grid.can_place_puyo(main_x, current_y):
                        grid.set_puyo(main_x, current_y, self.main_type)
                        self.main_fixed = True
                        logger.debug(f"Main puyo force-fixed at current position ({main_x}, {current_y})")
        
        if not self.sub_fixed:
            # 子ぷよが固定されていない場合、真下に即座に落下
            current_main_pos, current_sub_pos = self.get_positions()
            sub_x = current_sub_pos[0]
            
            # 子ぷよが有効な列にある場合のみ落下
            if 0 <= sub_x < GRID_WIDTH:
                drop_y = grid.get_drop_position(sub_x)
                # drop_yが有効な範囲内かチェック
                if 0 <= drop_y < GRID_HEIGHT:
                    grid.set_puyo(sub_x, drop_y, self.sub_type)
                    self.sub_fixed = True
                    logger.debug(f"Sub puyo immediately dropped to ({sub_x}, {drop_y})")
                else:
                    # 落下位置が無効な場合は現在位置で強制固定
                    current_y = max(0, min(current_sub_pos[1], GRID_HEIGHT - 1))
                    if current_y >= 0 and grid.can_place_puyo(sub_x, current_y):
                        grid.set_puyo(sub_x, current_y, self.sub_type)
                        self.sub_fixed = True
                        logger.debug(f"Sub puyo force-fixed at current position ({sub_x}, {current_y})")
    
    def set_fast_fall(self, fast: bool):
        """高速落下設定"""
        self.fast_falling = fast
    
    def render(self, surface: pygame.Surface, grid: PuyoGrid):
        """描画処理（分離状態も考慮）"""
        if not self.active:
            return
        
        main_pos, sub_pos = self.get_positions()
        
        # 軸ぷよ描画（固定されていない場合）
        if not self.main_fixed:
            self._render_puyo_at(surface, grid, main_pos, self.main_type, is_main=True)
        
        # 子ぷよ描画（固定されていない場合）
        if not self.sub_fixed:
            self._render_puyo_at(surface, grid, sub_pos, self.sub_type, is_main=False)
        
        # 分離状態の視覚的フィードバック
        if (self.main_fixed or self.sub_fixed) and not (self.main_fixed and self.sub_fixed):
            # 分離が発生中であることを示す（デバッグ用）
            logger.debug(f"Puyo separation in progress: main_fixed={self.main_fixed}, sub_fixed={self.sub_fixed}")
    
    def _render_puyo_at(self, surface: pygame.Surface, grid: PuyoGrid, pos: Tuple[int, int], puyo_type: PuyoType, is_main: bool):
        """指定位置にぷよを描画"""
        x, y = pos
        
        # 画面外は描画しない
        if y < 0 or x < 0 or x >= GRID_WIDTH:
            return
        
        # 重なり防止のため、描画位置を整数グリッドにスナップ
        grid_x = int(round(self.center_x + 1e-10))
        grid_y = int(round(self.center_y + 1e-10))
        
        if is_main:
            actual_x, actual_y = grid_x, grid_y
        else:
            offset_x, offset_y = [0, 1, 0, -1][self.rotation], [-1, 0, 1, 0][self.rotation]
            actual_x, actual_y = grid_x + offset_x, grid_y + offset_y
        
        # 既存のぷよとの重なりチェック（視覚的重なり防止）
        # ただし、落下中のぷよは少し上にオフセットして描画することで重なりを回避
        if actual_y >= 0 and actual_x >= 0 and actual_x < GRID_WIDTH and actual_y < GRID_HEIGHT:
            if not grid.can_place_puyo(actual_x, actual_y):
                # 既存のぷよがある場合は、少し上の位置に描画してオーバーラップを防ぐ
                pixel_y_offset = -6  # 6ピクセル上にオフセット（より明確な分離）
                logger.debug(f"Offsetting render position to prevent visual overlap at ({actual_x}, {actual_y})")
            else:
                pixel_y_offset = 0
        else:
            pixel_y_offset = 0
        
        pixel_x = grid.offset_x + actual_x * grid.puyo_size
        pixel_y = grid.offset_y + actual_y * grid.puyo_size + pixel_y_offset
        
        rect = pygame.Rect(
            int(pixel_x) + 2,
            int(pixel_y) + 2,
            grid.puyo_size - 4,
            grid.puyo_size - 4
        )
        
        color = PUYO_COLORS[puyo_type]
        center = rect.center
        radius = (grid.puyo_size - 4) // 2
        
        # ぷよ本体
        pygame.draw.circle(surface, color, center, radius)
        
        # 枠線（軸ぷよは太く）
        border_width = 3 if is_main else 2
        pygame.draw.circle(surface, Colors.WHITE, center, radius, border_width)
        
        # ハイライト
        highlight_radius = radius // 3
        highlight_center = (center[0] - radius//3, center[1] - radius//3)
        pygame.draw.circle(surface, Colors.WHITE, highlight_center, highlight_radius)


class AuthenticDemoHandler:
    """本格ぷよぷよデモハンドラー - 2個ペアで本家と同じ動作"""
    
    def __init__(self, engine: GameEngine):
        self.engine = engine
        self.puyo_grid = PuyoGrid()
        
        # 現在の落下ペア
        self.current_pair: Optional[PuyoPair] = None
        
        # ぷよタイプ（最初に定義）
        self.puyo_types = [PuyoType.RED, PuyoType.BLUE, PuyoType.GREEN, 
                          PuyoType.YELLOW, PuyoType.PURPLE]
        
        # NEXTぷよシステム（本家仕様：3ペア先まで表示）
        self.next_pairs_queue: List[Tuple[PuyoType, PuyoType]] = []
        self._generate_initial_next_queue()
        
        # 本家風タイミング制御（最適化）
        self.spawn_timer = 0.0
        self.spawn_interval = 0.35  # チェイン完了を待つための適切な間隔
        
        # 本家風チェイン処理
        self.chain_delay_timer = 0.0
        self.chain_delay = 0.15  # 高速チェイン遅延（0.15秒で十分）
        self.pending_chain_check = False
        
        # チェイン安全機構
        self.chain_timeout = 10.0  # 最大10秒でチェイン処理を強制終了
        self.chain_start_time = 0.0
        
        # ゲーム状態
        self.game_active = True
        self.total_score = 0
        self.total_chains = 0
        
        # UI位置（NEXTエリアの下から開始）
        self.ui_start_x = GRID_WIDTH * PUYO_SIZE + GRID_OFFSET_X + 30
        
        logger.info("Authentic demo handler initialized")
    
    def _generate_initial_next_queue(self):
        """初期NEXTキューを生成（2ペア分に調整）"""
        self.next_pairs_queue = []
        for i in range(2):  # 3つから2つに減らす
            main_type = random.choice(self.puyo_types)
            sub_type = random.choice(self.puyo_types)
            self.next_pairs_queue.append((main_type, sub_type))
        logger.debug(f"Generated initial NEXT queue: {[f'{m.name}+{s.name}' for m, s in self.next_pairs_queue]}")
    
    def _get_next_pair_colors(self) -> Tuple[PuyoType, PuyoType]:
        """次のペアの色を取得してキューを更新"""
        if not self.next_pairs_queue:
            self._generate_initial_next_queue()
        
        # 最初のペアを取得
        next_pair = self.next_pairs_queue.pop(0)
        
        # 新しいペアを末尾に追加
        new_main = random.choice(self.puyo_types)
        new_sub = random.choice(self.puyo_types)
        self.next_pairs_queue.append((new_main, new_sub))
        
        logger.debug(f"Used NEXT pair: {next_pair[0].name}+{next_pair[1].name}")
        logger.debug(f"Updated queue: {[f'{m.name}+{s.name}' for m, s in self.next_pairs_queue]}")
        
        return next_pair
    
    def on_enter(self, previous_state):
        """状態開始時の処理"""
        logger.info("Entering authentic demo state")
        self._reset_game()
    
    def on_exit(self):
        """状態終了時の処理"""
        logger.info("Exiting authentic demo state")
    
    def _reset_game(self):
        """ゲームリセット"""
        self.puyo_grid.clear()
        self.current_pair = None
        self._generate_initial_next_queue()
        self.spawn_timer = 0.0
        self.chain_delay_timer = 0.0
        self.pending_chain_check = False
        self.chain_start_time = 0.0
        self.game_active = True
        self.total_score = 0
        self.total_chains = 0
    
    def update(self, dt: float):
        """更新処理"""
        if not self.game_active:
            return
        
        # アニメーション更新
        self.puyo_grid.update_animations(dt)
        
        # 継続的なキー入力処理
        self._handle_continuous_input()
        
        # 現在のペア更新
        if self.current_pair and self.current_pair.active:
            if self.current_pair.update(dt, self.puyo_grid):
                # ペアが完全に着地
                logger.info(f"🎯 PAIR LANDED AND LOCKED - STARTING CHAIN CHECK 🎯")
                self.current_pair = None
                self.pending_chain_check = True
                self.chain_delay_timer = 0.0
        elif self.current_pair and not self.current_pair.active:
            # ペアが非アクティブになった場合の緊急処理
            logger.warning("⚠️ PAIR BECAME INACTIVE WITHOUT PROPER LANDING - FORCING COMPLETION ⚠️")
            self.current_pair = None
            self.pending_chain_check = True
            self.chain_delay_timer = 0.0
        
        # スポーンタイマー更新
        if self.current_pair is None:
            self.spawn_timer += dt
        
        # チェイン遅延処理
        if self.pending_chain_check:
            self.chain_delay_timer += dt
            if self.chain_delay_timer >= self.chain_delay:
                self._execute_chain_check()
                self.pending_chain_check = False
                self.chain_delay_timer = 0.0
        
        # チェイン安全機構：アニメーション中のタイムアウトチェック
        if self.puyo_grid.chain_animation_active:
            current_time = pygame.time.get_ticks() / 1000.0
            if self.chain_start_time == 0.0:
                self.chain_start_time = current_time
            
            # タイムアウトチェック
            if current_time - self.chain_start_time > self.chain_timeout:
                logger.warning(f"Chain animation timeout after {self.chain_timeout}s - forcing completion")
                self.puyo_grid.chain_animation_active = False
                self.puyo_grid.chain_queue.clear()
                self.chain_start_time = 0.0
        else:
            # アニメーション終了時にタイマーリセット
            if self.chain_start_time != 0.0:
                self.chain_start_time = 0.0
        
        # 新しいペアスポーン（連鎖アニメーション中は停止）
        if (self.current_pair is None and self.spawn_timer >= self.spawn_interval and 
            not self.puyo_grid.chain_animation_active):
            self._spawn_new_pair()
            self.spawn_timer = 0.0
        
        # ゲームオーバー判定
        if self.puyo_grid.is_game_over():
            self.game_active = False
            logger.info(f"Authentic demo game over - Score: {self.total_score}")
    
    def _handle_continuous_input(self):
        """継続的なキー入力処理"""
        if not self.current_pair or not self.current_pair.active:
            return
        
        # 連鎖アニメーション中は操作を受け付けない
        if self.puyo_grid.chain_animation_active:
            return
        
        # 分離状態では制限された操作のみ
        if (self.current_pair.separated and 
            self.current_pair.post_separation_timer >= self.current_pair.post_separation_control_time):
            return
        
        keys = pygame.key.get_pressed()
        
        # S キーの継続的な高速落下
        if keys[pygame.K_s]:
            self.current_pair.set_fast_fall(True)
        else:
            self.current_pair.set_fast_fall(False)
    
    def _spawn_new_pair(self):
        """新しいぷよペアをスポーン"""
        # 中央からスポーン
        center_x = GRID_WIDTH // 2
        
        # NEXTから色を取得
        main_type, sub_type = self._get_next_pair_colors()
        
        # ペア作成
        new_pair = PuyoPair(main_type, sub_type, center_x)
        
        # 本家風配置可能性チェック
        if self._can_spawn_authentic_pair(new_pair):
            self.current_pair = new_pair
            logger.info(f"Spawned pair: {main_type.name} (main) + {sub_type.name} (sub)")
            
            # スポーン直後にキー状態をチェック（Sキー継続対応）
            keys = pygame.key.get_pressed()
            if keys[pygame.K_s]:
                self.current_pair.set_fast_fall(True)
                logger.debug("Fast fall applied to new pair immediately")
        else:
            # 本家風ゲームオーバー
            self.game_active = False
            logger.info("Authentic Game Over - Cannot spawn new pair at authentic spawn position")
    
    def _can_spawn_authentic_pair(self, pair: PuyoPair) -> bool:
        """本家風ペアスポーン可能性チェック"""
        # 本家では上から出現するため、スポーン位置での重複チェック
        spawn_x = GRID_WIDTH // 2
        
        # スポーン時の初期位置（y=-1で軸ぷよ、y=-2で子ぷよ）から
        # 画面内に入る位置（y=0, y=1）での配置可能性をチェック
        
        # 軸ぷよが最初に画面内に入る位置（y=0）をチェック
        if not self.puyo_grid.can_place_puyo(spawn_x, 0):
            logger.debug("Authentic spawn check failed: main puyo entry position blocked")
            return False
        
        # 子ぷよが画面内に入る位置もチェック（回転状態による）
        # 初期回転（0=上）では子ぷよがy=-1の位置にあるため、画面内に入るとy=0になる
        # この場合は軸ぷよと重複するのでy=1の位置で別の配置をチェック
        
        # 最低限のスペースがあることを確認
        space_available = False
        
        # 上下の配置（軸ぷよy=1, 子ぷよy=0）をチェック
        if (self.puyo_grid.can_place_puyo(spawn_x, 0) and 
            self.puyo_grid.can_place_puyo(spawn_x, 1)):
            space_available = True
        
        # 左右の配置も可能かチェック
        for dx in [-1, 1]:
            test_x = spawn_x + dx
            if (0 <= test_x < GRID_WIDTH and 
                self.puyo_grid.can_place_puyo(spawn_x, 0) and 
                self.puyo_grid.can_place_puyo(test_x, 0)):
                space_available = True
                break
        
        if not space_available:
            logger.debug("Authentic spawn check failed: insufficient space for pair")
            return False
        
        return True
    
    def _execute_chain_check(self):
        """チェイン判定と実行（アニメーション対応）"""
        # アニメーション付き連鎖シーケンスを開始
        self.puyo_grid.start_animated_chain_sequence()
        
        if self.puyo_grid.chain_animation_active:
            logger.info("Started animated chain sequence")
    
    def handle_event(self, event: pygame.event.Event):
        """イベント処理"""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.engine.change_state(GameState.MENU)
            
            elif event.key == pygame.K_r:
                self._reset_game()
                logger.info("Authentic demo reset")
            
            elif event.key == pygame.K_RETURN:
                self.engine.change_state(GameState.PLAYING)
            
            elif event.key == pygame.K_c:
                self._execute_chain_check()
            
            # 本家風ペア操作（活発なペアがある場合、連鎖中でない場合）
            elif (self.current_pair and self.current_pair.active and 
                  not self.puyo_grid.chain_animation_active):
                if event.key == pygame.K_a:
                    # 左移動
                    if self.current_pair.try_move_horizontal(-1, self.puyo_grid):
                        logger.debug("Pair moved left")
                
                elif event.key == pygame.K_d:
                    # 右移動
                    if self.current_pair.try_move_horizontal(1, self.puyo_grid):
                        logger.debug("Pair moved right")
                
                elif event.key == pygame.K_SPACE:
                    # 時計回り回転（本家の標準操作）
                    if self.current_pair.try_rotate(True, self.puyo_grid):
                        logger.debug(f"Pair rotated clockwise to {self.current_pair.rotation}")
                
                elif event.key == pygame.K_w:
                    # 反時計回り回転（本家の追加操作）
                    if self.current_pair.try_rotate(False, self.puyo_grid):
                        logger.debug(f"Pair rotated counter-clockwise to {self.current_pair.rotation}")
            
            # 落下中でない場合は手動スポーン
            elif event.key == pygame.K_SPACE and self.current_pair is None:
                self._spawn_new_pair()
        
# KEYUPでのSキー処理は不要（継続的入力で処理）
        
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1 and self.current_pair is None:
                # クリック位置にぷよを直接配置
                mouse_x, mouse_y = event.pos
                grid_x, grid_y = self.puyo_grid.pixel_to_grid(mouse_x, mouse_y)
                
                if self.puyo_grid.can_place_puyo(grid_x, grid_y):
                    puyo_type = random.choice(self.puyo_types)
                    self.puyo_grid.set_puyo(grid_x, grid_y, puyo_type)
                    logger.info(f"Manual placement: {puyo_type.name} at ({grid_x}, {grid_y})")
                    self._execute_chain_check()
    
    def render(self, surface: pygame.Surface):
        """描画処理"""
        # プレイエリアの背景を透過（削除）
        # 白い十字線のみ描画
        self._draw_grid_lines(surface)
        
        # グリッド描画
        self.puyo_grid.render(surface, show_grid=True)
        
        # 現在のペア描画
        if self.current_pair:
            self.current_pair.render(surface, self.puyo_grid)
        
        # UI描画
        self._render_ui(surface)
        
        # NEXTぷよ表示エリア
        self._render_next_area(surface)
        
        # ゲームオーバー表示
        if not self.game_active:
            self._render_game_over_overlay(surface)
    
    def _render_ui(self, surface: pygame.Surface):
        """UI描画"""
        font_large = self.engine.fonts['large']
        font_medium = self.engine.fonts['medium']
        font_small = self.engine.fonts['small']
        
        y_offset = GRID_OFFSET_Y + 250  # 拡張されたNEXTエリア分下にずらす
        
        # タイトル
        title_text = font_large.render("Authentic Puyo (Sega)", True, Colors.WHITE)
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
        
        # 状態情報
        if self.current_pair:
            pair_info = f"Pair: {self.current_pair.main_type.name[:1]}{self.current_pair.sub_type.name[:1]}"
            pair_text = font_small.render(pair_info, True, Colors.GREEN)
            surface.blit(pair_text, (self.ui_start_x, y_offset))
            y_offset += 20
            
            rotation_text = font_small.render(f"Rotation: {self.current_pair.rotation}", True, Colors.LIGHT_GRAY)
            surface.blit(rotation_text, (self.ui_start_x, y_offset))
            y_offset += 25
        
        if self.current_pair is None and self.spawn_timer > 0:
            next_spawn = max(0, self.spawn_interval - self.spawn_timer)
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
            "Authentic Controls:",
            "A/D - Move Left/Right",
            "S - Fast Fall (hold)",
            "Space - Rotate Clockwise",
            "W - Rotate Counter-CW",
            "",
            "Other:",
            "C - Execute Chain",
            "Click - Place Single",
        ]
        
        for control in controls:
            if control == "":
                y_offset += 5
                continue
            elif control in ["Pair Control:", "Other:"]:
                color = Colors.YELLOW
            else:
                color = Colors.LIGHT_GRAY
            
            control_text = font_small.render(control, True, color)
            surface.blit(control_text, (self.ui_start_x, y_offset))
            y_offset += 18
        
        # チェイン処理中表示
        if self.pending_chain_check:
            chain_progress = self.chain_delay_timer / self.chain_delay
            progress_width = 120
            progress_height = 8
            
            progress_bg = pygame.Rect(self.ui_start_x, y_offset, progress_width, progress_height)
            progress_fg = pygame.Rect(self.ui_start_x, y_offset, int(progress_width * chain_progress), progress_height)
            
            pygame.draw.rect(surface, Colors.DARK_GRAY, progress_bg)
            pygame.draw.rect(surface, Colors.ORANGE, progress_fg)
            
            status_text = font_small.render("Checking chains...", True, Colors.ORANGE)
            surface.blit(status_text, (self.ui_start_x, y_offset - 20))
    
    def _render_next_area(self, surface: pygame.Surface):
        """NEXTぷよ表示エリアを描画（2ペア分に調整）"""
        if not self.next_pairs_queue:
            return
        
        # NEXTエリアの位置（プレイエリア右上）
        next_area_x = GRID_OFFSET_X + GRID_WIDTH * PUYO_SIZE + 10
        next_area_y = GRID_OFFSET_Y
        next_area_width = 100
        next_area_height = 160  # 2ペア分の高さに縮小
        
        # NEXTエリア背景
        next_bg_rect = pygame.Rect(next_area_x, next_area_y, next_area_width, next_area_height)
        pygame.draw.rect(surface, Colors.DARK_GRAY, next_bg_rect)
        pygame.draw.rect(surface, Colors.WHITE, next_bg_rect, 2)
        
        # NEXTタイトル
        font_small = self.engine.fonts['small']
        next_title = font_small.render("NEXT", True, Colors.WHITE)
        title_rect = next_title.get_rect(centerx=next_area_x + next_area_width // 2, y=next_area_y + 5)
        surface.blit(next_title, title_rect)
        
        # 2ペア分のNEXTぷよを描画
        for i, (main_type, sub_type) in enumerate(self.next_pairs_queue[:2]):
            # 各ペアのサイズと位置
            if i == 0:  # 最初のペア（最も近い）
                puyo_size = 25
                y_offset = 35
                border_width_main = 2
                border_width_sub = 1
            else:  # 2番目以降のペア（小さく表示）
                puyo_size = 18
                y_offset = 35 + 65 + (i - 1) * 55
                border_width_main = 1
                border_width_sub = 1
            
            # ペアの中心位置
            center_x = next_area_x + next_area_width // 2
            center_y = next_area_y + y_offset
            
            # 軸ぷよ（中心）
            main_color = PUYO_COLORS[main_type]
            main_radius = (puyo_size - 2) // 2
            main_center = (center_x, center_y)
            
            pygame.draw.circle(surface, main_color, main_center, main_radius)
            pygame.draw.circle(surface, Colors.WHITE, main_center, main_radius, border_width_main)
            
            # 軸ぷよのハイライト
            if i == 0:  # 最初のペアのみハイライト
                highlight_radius = main_radius // 3
                highlight_center = (main_center[0] - main_radius//3, main_center[1] - main_radius//3)
                pygame.draw.circle(surface, Colors.WHITE, highlight_center, highlight_radius)
            
            # 子ぷよ（上に配置 - rotation=0の状態）
            sub_color = PUYO_COLORS[sub_type]
            sub_radius = (puyo_size - 2) // 2
            sub_center = (center_x, center_y - puyo_size)
            
            pygame.draw.circle(surface, sub_color, sub_center, sub_radius)
            pygame.draw.circle(surface, Colors.WHITE, sub_center, sub_radius, border_width_sub)
            
            # 子ぷよのハイライト
            if i == 0:  # 最初のペアのみハイライト
                sub_highlight_center = (sub_center[0] - sub_radius//3, sub_center[1] - sub_radius//3)
                pygame.draw.circle(surface, Colors.WHITE, sub_highlight_center, highlight_radius)
            
            # ペア番号表示（2番目のみ）
            if i > 0:
                number_text = font_small.render("2", True, Colors.LIGHT_GRAY)
                number_rect = number_text.get_rect(centerx=next_area_x + 15, centery=center_y - puyo_size // 2)
                surface.blit(number_text, number_rect)
    
    def _render_game_over_overlay(self, surface: pygame.Surface):
        """ゲームオーバーオーバーレイ"""
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(128)
        overlay.fill(Colors.BLACK)
        surface.blit(overlay, (0, 0))
        
        font_title = self.engine.fonts['title']
        font_large = self.engine.fonts['large']
        font_medium = self.engine.fonts['medium']
        
        game_over_text = font_title.render("DEMO COMPLETE", True, Colors.ORANGE)
        text_rect = game_over_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 80))
        surface.blit(game_over_text, text_rect)
        
        final_score_text = font_large.render(f"Final Score: {self.total_score:,}", True, Colors.WHITE)
        text_rect = final_score_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 20))
        surface.blit(final_score_text, text_rect)
        
        chains_text = font_medium.render(f"Total Chains: {self.total_chains}", True, Colors.YELLOW)
        text_rect = chains_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 20))
        surface.blit(chains_text, text_rect)
        
        instructions = [
            "R - Restart Demo",
            "Enter - Play Full Game", 
            "ESC - Back to Menu"
        ]
        
        for i, instruction in enumerate(instructions):
            text = font_medium.render(instruction, True, Colors.LIGHT_GRAY)
            text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 80 + i * 30))
            surface.blit(text, text_rect)
    
    def _draw_grid_lines(self, surface: pygame.Surface):
        """白い十字線のみ描画"""
        # 縦線
        for x in range(GRID_WIDTH + 1):
            line_x = GRID_OFFSET_X + x * PUYO_SIZE
            pygame.draw.line(surface, Colors.WHITE, 
                           (line_x, GRID_OFFSET_Y), 
                           (line_x, GRID_OFFSET_Y + GRID_HEIGHT * PUYO_SIZE), 1)
        
        # 横線
        for y in range(GRID_HEIGHT + 1):
            line_y = GRID_OFFSET_Y + y * PUYO_SIZE
            pygame.draw.line(surface, Colors.WHITE, 
                           (GRID_OFFSET_X, line_y), 
                           (GRID_OFFSET_X + GRID_WIDTH * PUYO_SIZE, line_y), 1)


if __name__ == "__main__":
    # テスト実行
    import sys
    import os
    
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
    
    from src.core.game_engine import GameEngine
    
    logging.basicConfig(level=logging.INFO)
    
    engine = GameEngine()
    handler = AuthenticDemoHandler(engine)
    
    engine.register_state_handler(GameState.BATTLE, handler)
    engine.change_state(GameState.BATTLE)
    
    print("Starting authentic puyo demo test...")
    engine.run()