"""
ぷよグリッドシステム
Drop Puzzle × Roguelike のぷよぷよゲーム部分の核となるグリッド管理
"""

import pygame
import logging
import math
import time
import random
from typing import List, Optional, Set, Tuple, Dict
from dataclasses import dataclass
from copy import deepcopy

from ..core.constants import *
from ..core.sound_manager import play_se, SoundType

logger = logging.getLogger(__name__)


@dataclass
class PuyoPosition:
    """ぷよの位置情報"""
    x: int
    y: int
    
    def __hash__(self):
        return hash((self.x, self.y))
    
    def __eq__(self, other):
        return isinstance(other, PuyoPosition) and self.x == other.x and self.y == other.y
    
    def is_valid(self) -> bool:
        """有効な座標かチェック"""
        return 0 <= self.x < GRID_WIDTH and 0 <= self.y < GRID_HEIGHT
    
    def get_neighbors(self) -> List['PuyoPosition']:
        """隣接する4方向の座標を取得"""
        neighbors = []
        for dx, dy in DIRECTIONS:
            new_pos = PuyoPosition(self.x + dx, self.y + dy)
            if new_pos.is_valid():
                neighbors.append(new_pos)
        return neighbors


@dataclass
class ChainResult:
    """連鎖結果情報"""
    eliminated_puyos: Set[PuyoPosition]
    chain_length: int
    puyo_count: int
    score: int
    chain_type: PuyoType


class PuyoGrid:
    """ぷよぷよグリッドの管理クラス"""
    
    def __init__(self):
        """グリッド初期化"""
        self.width = GRID_WIDTH
        self.height = GRID_HEIGHT
        
        # グリッド配列 [x][y] = PuyoType
        self.grid: List[List[PuyoType]] = [
            [PuyoType.EMPTY for _ in range(self.height)]
            for _ in range(self.width)
        ]
        
        # 描画位置
        self.offset_x = GRID_OFFSET_X
        self.offset_y = GRID_OFFSET_Y
        self.puyo_size = PUYO_SIZE
        
        # 連鎖情報
        self.total_chains = 0
        self.last_chain_score = 0
        self.last_chain_positions: Set[Tuple[int, int]] = set()  # 最後の連鎖で消去されたぷよの位置
        
        # アニメーション用データ
        self.disappearing_puyos: Dict[Tuple[int, int], dict] = {}  # 消去中のぷよ
        self.falling_puyos: List[dict] = []  # 落下中のぷよ
        
        # 連鎖アニメーション制御
        self.chain_animation_active = False
        self.chain_queue = []  # 連鎖待ちキュー
        self.current_chain_timer = 0.0
        self.chain_delay_per_group = 0.1  # 塊ごとの遅延時間（高速化：0.1秒）
        
        # アニメーション用連鎖統計
        self.animated_chain_level = 0
        self.animated_total_score = 0
        self.animated_total_eliminated = 0
        
        logger.info(f"PuyoGrid initialized: {self.width}x{self.height}")
    
    def clear(self):
        """グリッドをクリア"""
        for x in range(self.width):
            for y in range(self.height):
                self.grid[x][y] = PuyoType.EMPTY
        
        self.total_chains = 0
        self.last_chain_score = 0
        self.last_chain_positions.clear()
        logger.info("Grid cleared")
    
    def is_valid_position(self, x: int, y: int) -> bool:
        """座標が有効かチェック"""
        return 0 <= x < self.width and 0 <= y < self.height
    
    def get_puyo(self, x: int, y: int) -> PuyoType:
        """指定座標のぷよを取得"""
        if not self.is_valid_position(x, y):
            return PuyoType.EMPTY
        return self.grid[x][y]
    
    def set_puyo(self, x: int, y: int, puyo_type: PuyoType) -> bool:
        """指定座標にぷよを配置"""
        if not self.is_valid_position(x, y):
            return False
        
        self.grid[x][y] = puyo_type
        return True
    
    def is_empty(self, x: int, y: int) -> bool:
        """指定座標が空かチェック"""
        return self.get_puyo(x, y) == PuyoType.EMPTY
    
    def can_place_puyo(self, x: int, y: int) -> bool:
        """ぷよを配置可能かチェック"""
        return self.is_valid_position(x, y) and self.is_empty(x, y)
    
    def get_column_height(self, x: int) -> int:
        """指定列の高さ（一番上のぷよの位置）を取得"""
        if not (0 <= x < self.width):
            return 0
        
        for y in range(self.height):
            if not self.is_empty(x, y):
                return self.height - y
        return 0
    
    def get_drop_position(self, x: int) -> int:
        """ぷよが落下する位置のY座標を取得"""
        if not (0 <= x < self.width):
            return -1
        
        for y in range(self.height - 1, -1, -1):
            if self.is_empty(x, y):
                return y
        return -1  # 列が満杯
    
    def drop_puyo(self, x: int, puyo_type: PuyoType) -> bool:
        """ぷよを指定列に落下させる"""
        drop_y = self.get_drop_position(x)
        if drop_y == -1:
            return False
        
        self.set_puyo(x, drop_y, puyo_type)
        return True
    
    def apply_gravity(self) -> int:
        """重力を適用（浮いているぷよを落下させる） - 移動したぷよの数を返す"""
        moved_count = 0
        
        for x in range(self.width):
            # 各列を下から詰める
            write_y = self.height - 1
            
            for read_y in range(self.height - 1, -1, -1):
                puyo = self.grid[x][read_y]
                if puyo != PuyoType.EMPTY:
                    if write_y != read_y:
                        self.grid[x][write_y] = puyo
                        self.grid[x][read_y] = PuyoType.EMPTY
                        moved_count += 1
                    write_y -= 1
        
        return moved_count
    
    def find_connected_puyos(self, start_x: int, start_y: int) -> Set[PuyoPosition]:
        """指定位置から連結している同色のぷよを検索（深さ優先探索・本家アルゴリズム）"""
        if not self.is_valid_position(start_x, start_y):
            return set()
        
        start_type = self.get_puyo(start_x, start_y)
        if start_type == PuyoType.EMPTY or start_type == PuyoType.GARBAGE:
            return set()
        
        # 本家ぷよぷよのアルゴリズム：4方向連結成分探索
        visited = set()
        connected = set()
        
        def dfs(x: int, y: int):
            """深さ優先探索で連結成分を見つける"""
            pos = PuyoPosition(x, y)
            if pos in visited:
                return
            
            if not self.is_valid_position(x, y):
                return
            
            if self.get_puyo(x, y) != start_type:
                return
            
            visited.add(pos)
            connected.add(pos)
            
            # 4方向を探索（上下左右のみ）
            for dx, dy in DIRECTIONS:
                dfs(x + dx, y + dy)
        
        dfs(start_x, start_y)
        return connected
    
    def find_all_chains(self) -> List[ChainResult]:
        """グリッド全体から連鎖可能な塊を検索（本家アルゴリズム）"""
        visited = set()
        chains = []
        
        # 本家ぷよぷよの連鎖検出：全セルをスキャンして4個以上の連結成分を探す
        for y in range(self.height):  # 下から上へ
            for x in range(self.width):  # 左から右へ
                pos = PuyoPosition(x, y)
                
                if pos in visited:
                    continue
                
                puyo_type = self.get_puyo(x, y)
                if puyo_type == PuyoType.EMPTY or puyo_type == PuyoType.GARBAGE:
                    continue
                
                # 連結しているぷよを検索
                connected = self.find_connected_puyos(x, y)
                visited.update(connected)
                
                # 本家ルール：4個以上で消去
                if len(connected) >= MIN_CHAIN_LENGTH:
                    score = self._calculate_authentic_chain_score(len(connected), puyo_type)
                    
                    chain_result = ChainResult(
                        eliminated_puyos=connected,
                        chain_length=1,  # 単体の連鎖レベル
                        puyo_count=len(connected),
                        score=score,
                        chain_type=puyo_type
                    )
                    chains.append(chain_result)
        
        return chains
    
    def _calculate_chain_score(self, puyo_count: int, puyo_type: PuyoType) -> int:
        """連鎖スコアを計算（従来システム用）"""
        base_score = CHAIN_SCORE_BASE
        puyo_score = puyo_count * 10
        
        # ぷよタイプによるボーナス
        type_multiplier = 1.0
        if puyo_type in [PuyoType.PURPLE, PuyoType.ORANGE]:
            type_multiplier = 1.2  # レアカラーボーナス
        
        return int((base_score + puyo_score) * type_multiplier)
    
    def _calculate_authentic_chain_score(self, puyo_count: int, puyo_type: PuyoType) -> int:
        """本家風連鎖スコア計算"""
        # 本家ぷよぷよのスコア計算式
        # 基本点 = 消去数 × 10
        base_points = puyo_count * 10
        
        # 連結数ボーナス（4個=1.0, 5個=1.2, 6個=1.4...）
        connection_bonus = 1.0 + (puyo_count - 4) * 0.2
        
        # 色ボーナス（一部の色に特別ボーナス）
        color_bonus = 1.0
        if puyo_type in [PuyoType.PURPLE, PuyoType.ORANGE]:
            color_bonus = 1.1
        
        final_score = int(base_points * connection_bonus * color_bonus)
        return max(final_score, 40)  # 最低40点保証
    
    def _record_chain_positions(self, positions: Set[PuyoPosition]):
        """連鎖で消去される位置を記録（内部用）"""
        for pos in positions:
            self.last_chain_positions.add((pos.x, pos.y))
    
    def get_last_chain_positions(self) -> List[Tuple[int, int]]:
        """最後の連鎖で消去されたぷよの位置を取得し、クリアする
        
        Returns:
            List[Tuple[int, int]]: 消去されたぷよの位置のリスト [(x, y), ...]
            
        Note:
            この方法を呼び出すと内部の位置リストはクリアされます。
            重複した特殊効果を避けるため。
        """
        positions = list(self.last_chain_positions)
        self.last_chain_positions.clear()  # 使用後にクリア
        return positions
    
    def eliminate_puyos(self, positions: Set[PuyoPosition]) -> int:
        """指定位置のぷよを消去（フェードアウトアニメーション付き）"""
        eliminated_count = 0
        current_time = time.time()
        
        for pos in positions:
            puyo_type = self.get_puyo(pos.x, pos.y)
            if puyo_type != PuyoType.EMPTY:
                # 弾けるエフェクト用のパーティクルを生成
                particles = []
                center_x = self.offset_x + pos.x * self.puyo_size + self.puyo_size // 2
                center_y = self.offset_y + pos.y * self.puyo_size + self.puyo_size // 2
                
                # 8方向にパーティクルを飛ばす
                for i in range(8):
                    angle = (i / 8.0) * 2 * math.pi
                    speed = random.uniform(50, 100)  # ピクセル/秒
                    particles.append({
                        'x': float(center_x),
                        'y': float(center_y),
                        'vx': math.cos(angle) * speed,
                        'vy': math.sin(angle) * speed,
                        'life': random.uniform(0.3, 0.5),  # 寿命
                        'max_life': random.uniform(0.3, 0.5),
                        'size': random.uniform(3, 8)
                    })
                
                # アニメーション用データを設定（高速化）
                self.disappearing_puyos[(pos.x, pos.y)] = {
                    'type': puyo_type,
                    'start_time': current_time,
                    'duration': 0.08,  # 0.08秒でフェードアウト（超高速化）
                    'alpha': 255,
                    'scale': 1.0,  # 弾けるエフェクト用
                    'particles': particles  # パーティクルエフェクト
                }
                
                # グリッドからは即座に削除
                self.set_puyo(pos.x, pos.y, PuyoType.EMPTY)
                eliminated_count += 1
        
        # 消去SEを再生（1個以上消去された場合）
        if eliminated_count > 0:
            play_se(SoundType.ELIMINATE)
        
        logger.info(f"Eliminated {eliminated_count} puyos with fade animation")
        return eliminated_count
    
    def update_animations(self, dt: float):
        """アニメーション更新（弾けるエフェクト・連鎖アニメーション込み）"""
        current_time = time.time()
        
        # フェードアウトアニメーション更新
        to_remove = []
        for pos, data in self.disappearing_puyos.items():
            elapsed = current_time - data['start_time']
            progress = elapsed / data['duration']
            
            if progress >= 1.0:
                # アニメーション完了
                to_remove.append(pos)
            else:
                # アルファ値とスケールを更新（弾けるエフェクト）
                data['alpha'] = int(255 * (1.0 - progress))
                # 最初に少し膨らんでから縮む
                if progress < 0.3:
                    data['scale'] = 1.0 + (progress / 0.3) * 0.4  # 1.0 → 1.4
                else:
                    data['scale'] = 1.4 - ((progress - 0.3) / 0.7) * 1.4  # 1.4 → 0.0
                
                # パーティクル更新
                for particle in data['particles'][:]:  # コピーを作って安全に削除
                    particle['x'] += particle['vx'] * dt
                    particle['y'] += particle['vy'] * dt
                    particle['life'] -= dt
                    
                    # 重力効果
                    particle['vy'] += 150 * dt  # 重力加速度
                    
                    # 寿命が尽きたパーティクルを削除
                    if particle['life'] <= 0:
                        data['particles'].remove(particle)
        
        # 完了したアニメーションを削除
        for pos in to_remove:
            del self.disappearing_puyos[pos]
        
        # 連鎖アニメーション更新
        self.update_chain_animation(dt)
    
    def execute_chain_elimination(self) -> Tuple[int, int]:
        """連鎖消去を実行し、スコアと消去数を返す"""
        chains = self.find_all_chains()
        
        if not chains:
            return 0, 0
        
        # 連鎖位置をクリア
        self.last_chain_positions.clear()
        
        total_score = 0
        total_eliminated = 0
        
        # 全ての連鎖を実行
        for chain in chains:
            # 連鎖位置を記録
            self._record_chain_positions(chain.eliminated_puyos)
            
            eliminated_count = self.eliminate_puyos(chain.eliminated_puyos)
            total_score += chain.score
            total_eliminated += eliminated_count
            
            logger.info(f"Chain eliminated: {eliminated_count} {chain.chain_type.name} puyos, score: {chain.score}")
        
        # 重力適用
        self.apply_gravity()
        
        # 統計更新
        self.total_chains += len(chains)
        self.last_chain_score = total_score
        
        return total_score, total_eliminated
    
    def execute_full_chain_sequence(self) -> Tuple[int, int]:
        """本家風連鎖の段階的実行（塊ごとに順番に処理）"""
        total_score = 0
        total_eliminated = 0
        chain_level = 0
        
        # 連鎖位置をクリア
        self.last_chain_positions.clear()
        
        # 最初に重力を適用
        self.apply_gravity()
        
        while True:
            # 本家アルゴリズム：連鎖可能な塊を探す
            chains = self.find_all_chains()
            
            if not chains:
                break
            
            chain_level += 1
            logger.info(f"=== Chain Level {chain_level} Started ===")
            
            # 本家風連鎖処理：塊ごとに順番に消去
            level_score = 0
            level_eliminated = 0
            
            # 各塊を順番に消去（本家の仕様）
            for i, chain in enumerate(chains):
                logger.info(f"Eliminating chain {i+1}/{len(chains)}: {len(chain.eliminated_puyos)} {chain.chain_type.name} puyos")
                
                # 連鎖位置を記録
                self._record_chain_positions(chain.eliminated_puyos)
                
                # 塊を個別に消去
                eliminated_count = self.eliminate_puyos(chain.eliminated_puyos)
                level_score += chain.score
                level_eliminated += eliminated_count
                
                # 各塊消去後に重力を適用（本家の動作）
                self.apply_gravity()
                
                logger.info(f"Chain {i+1} eliminated: {eliminated_count} puyos, score: {chain.score}")
            
            # 連鎖レベルボーナス計算（本家風）
            chain_multiplier = self._calculate_authentic_chain_multiplier(chain_level)
            chain_bonus = int(level_score * chain_multiplier)
            total_score += chain_bonus
            total_eliminated += level_eliminated
            
            logger.info(f"Chain level {chain_level}: {level_eliminated} eliminated, multiplier: {chain_multiplier:.2f}, score: {chain_bonus}")
            
            # 次の連鎖レベルの準備ができるまで少し待つ（アニメーション用）
            # 実際のアニメーションはAuthenticDemoHandlerで制御
        
        if chain_level > 0:
            logger.info(f"Authentic chain sequence completed: {chain_level} levels, total score: {total_score}")
            # 統計更新
            self.last_chain_score = total_score
            self.total_chains += chain_level
        
        return total_score, total_eliminated
    
    def start_animated_chain_sequence(self):
        """アニメーション付き連鎖シーケンスを開始"""
        if self.chain_animation_active:
            logger.debug("Chain animation already active - ignoring start request")
            return  # 既にアニメーション中
        
        # クリーンアップ：前回のアニメーションデータをクリア
        self.disappearing_puyos.clear()
        self.chain_queue.clear()
        self.current_chain_timer = 0.0
        self.last_chain_positions.clear()  # 連鎖位置をクリア
        
        # アニメーション用連鎖情報をリセット
        self.animated_chain_level = 0
        self.animated_total_score = 0
        self.animated_total_eliminated = 0
        
        # 最初に重力を適用
        gravity_applied = self.apply_gravity()
        logger.debug(f"Applied gravity: {gravity_applied} puyos moved")
        
        # 連鎖可能な塊を探す
        chains = self.find_all_chains()
        
        if not chains:
            logger.info("No chains found - chain sequence complete")
            return  # 連鎖なし
        
        # 連鎖キューに追加
        self.chain_queue = chains.copy()
        self.chain_animation_active = True
        self.current_chain_timer = 0.0
        self.animated_chain_level = 1
        
        logger.info(f"Started animated chain sequence with {len(chains)} groups")
    
    def update_chain_animation(self, dt: float) -> bool:
        """連鎖アニメーション更新 - 完了時にTrueを返す"""
        if not self.chain_animation_active:
            return True
        
        # 安全チェック：キューが空なのにアニメーション中の場合は強制終了
        if not self.chain_queue:
            logger.warning("Chain queue empty but animation active - forcing completion")
            self.last_chain_score = self.animated_total_score
            self.total_chains += self.animated_chain_level
            self.chain_animation_active = False
            return True
        
        self.current_chain_timer += dt
        
        # 次の塊を消去するタイミングかチェック
        if self.current_chain_timer >= self.chain_delay_per_group:
            if not self.chain_queue:
                # キューが空になった - 連鎖完了
                self.chain_animation_active = False
                logger.info("Chain animation completed - queue empty")
                return True
            
            # 次の塊を消去
            chain = self.chain_queue.pop(0)
            
            logger.info(f"Eliminating chain group: {len(chain.eliminated_puyos)} {chain.chain_type.name} puyos")
            
            # 連鎖位置を記録
            self._record_chain_positions(chain.eliminated_puyos)
            
            # 塊を消去
            eliminated_count = self.eliminate_puyos(chain.eliminated_puyos)
            
            # アニメーション統計を更新
            chain_score = self._calculate_chain_level_score([chain], self.animated_chain_level)
            self.animated_total_score += chain_score
            self.animated_total_eliminated += eliminated_count
            
            logger.debug(f"Chain level {self.animated_chain_level}: +{chain_score} score, +{eliminated_count} eliminated")
            
            # 重力適用
            gravity_moved = self.apply_gravity()
            logger.debug(f"After elimination: {eliminated_count} eliminated, {gravity_moved} moved by gravity")
            
            # タイマーリセット
            self.current_chain_timer = 0.0
            
            # キューが空になったら次のレベルをチェック
            if not self.chain_queue:
                # 新しい連鎖が発生するかチェック
                new_chains = self.find_all_chains()
                if new_chains:
                    # 新しい連鎖レベル
                    self.animated_chain_level += 1
                    self.chain_queue = new_chains.copy()
                    logger.info(f"New chain level {self.animated_chain_level} started with {len(new_chains)} groups")
                else:
                    # 連鎖完了 - last_chain_scoreを設定
                    self.last_chain_score = self.animated_total_score
                    self.total_chains += self.animated_chain_level
                    self.chain_animation_active = False
                    logger.info(f"Animated chain sequence completed - {self.animated_chain_level} levels, {self.animated_total_score} total score, {self.animated_total_eliminated} eliminated")
                    return True
        
        return False  # アニメーション継続中
    
    def _calculate_authentic_chain_multiplier(self, chain_level: int) -> float:
        """本家風連鎖ボーナス倍率計算"""
        # 本家ぷよぷよの連鎖ボーナステーブル
        multipliers = {
            1: 1.0,    # 1連鎖
            2: 1.8,    # 2連鎖
            3: 2.9,    # 3連鎖
            4: 4.6,    # 4連鎖
            5: 7.7,    # 5連鎖
            6: 12.0,   # 6連鎖
            7: 16.0,   # 7連鎖
            8: 20.0,   # 8連鎖
            9: 24.0,   # 9連鎖
            10: 28.0,  # 10連鎖
        }
        
        if chain_level in multipliers:
            return multipliers[chain_level]
        elif chain_level > 10:
            # 10連鎖以上は線形増加
            return 28.0 + (chain_level - 10) * 4.0
        else:
            return 1.0
    
    def _calculate_chain_level_score(self, chains: List, chain_level: int) -> int:
        """特定の連鎖レベルでのスコアを計算"""
        if not chains:
            return 0
        
        total_score = 0
        chain_multiplier = self._calculate_authentic_chain_multiplier(chain_level)
        
        for chain in chains:
            # 各チェインの基本スコア
            puyo_count = len(chain.eliminated_puyos)
            base_score = self._calculate_authentic_chain_score(puyo_count, chain.chain_type)
            
            # 連鎖レベル倍率を適用
            chain_score = int(base_score * chain_multiplier)
            total_score += chain_score
            
            logger.debug(f"Chain score: {puyo_count} {chain.chain_type.name} puyos, base={base_score}, level {chain_level} multiplier={chain_multiplier:.1f}, final={chain_score}")
        
        return total_score
    
    def is_game_over(self) -> bool:
        """ゲームオーバー判定（本家仕様：スポーン位置でのペア配置不可）"""
        return self.is_authentic_game_over()
    
    def is_authentic_game_over(self) -> bool:
        """本家風ゲームオーバー判定"""
        # スポーン位置（中央）でのペア配置可能性をチェック
        spawn_x = self.width // 2  # 通常は3 (6x13グリッドの場合)
        
        # 本家では軸ぷよの位置（中央、y=1）がブロックされているかチェック
        main_spawn_y = 1
        if not self.can_place_puyo(spawn_x, main_spawn_y):
            logger.info("Game Over: Main puyo spawn position blocked")
            return True
        
        # 子ぷよの初期位置（上方向、y=0）もチェック
        sub_spawn_y = 0
        if not self.can_place_puyo(spawn_x, sub_spawn_y):
            logger.info("Game Over: Sub puyo spawn position blocked")
            return True
        
        # さらに本家風に：隠し行（y=-1, y=-2）もチェック
        # これらの行にぷよが積み上がっている場合もゲームオーバー
        for check_y in [-1, -2]:
            # 負の座標は範囲外なので、代わりに上端付近をチェック
            # 実際の実装では画面外の管理が必要だが、簡易版として上端をチェック
            if check_y == -1:
                # y=0 (画面最上段) に多くのぷよがある場合
                blocked_count = 0
                for x in range(self.width):
                    if not self.is_empty(x, 0):
                        blocked_count += 1
                
                # 上端の半分以上がブロックされている場合は危険
                if blocked_count >= self.width // 2:
                    logger.info(f"Game Over: Top row heavily blocked ({blocked_count}/{self.width})")
                    return True
        
        # 本家風の追加判定：中央3列の上端チェック
        center_blocked = 0
        center_cols = [spawn_x - 1, spawn_x, spawn_x + 1]
        for x in center_cols:
            if 0 <= x < self.width and not self.is_empty(x, 0):
                center_blocked += 1
        
        # 中央3列すべてがブロックされている場合
        if center_blocked >= 3:
            logger.info("Game Over: Center columns blocked")
            return True
        
        return False
    
    def get_grid_copy(self) -> List[List[PuyoType]]:
        """グリッドのコピーを取得"""
        return deepcopy(self.grid)
    
    def load_grid(self, grid_data: List[List[PuyoType]]):
        """グリッドデータを読み込み"""
        if len(grid_data) != self.width:
            logger.error(f"Invalid grid width: {len(grid_data)} (expected {self.width})")
            return False
        
        for x in range(self.width):
            if len(grid_data[x]) != self.height:
                logger.error(f"Invalid grid height at column {x}: {len(grid_data[x])} (expected {self.height})")
                return False
            
            for y in range(self.height):
                self.grid[x][y] = grid_data[x][y]
        
        logger.info("Grid data loaded successfully")
        return True
    
    def render(self, surface: pygame.Surface, show_grid: bool = True):
        """グリッドを描画"""
        # グリッド背景
        if show_grid:
            self._render_grid_background(surface)
        
        # ぷよを描画
        self._render_puyos(surface)
        
        # 連結エフェクトを描画
        self._render_connection_effects(surface)
        
        # 枠線を描画
        self._render_border(surface)
    
    def _render_grid_background(self, surface: pygame.Surface):
        """グリッド背景を描画（透過）"""
        # 背景は描画しない（透過）
        pass
    
    def _render_puyos(self, surface: pygame.Surface):
        """ぷよを描画（アニメーション込み）"""
        # 通常のぷよを描画
        for x in range(self.width):
            for y in range(self.height):
                puyo_type = self.get_puyo(x, y)
                
                if puyo_type == PuyoType.EMPTY:
                    continue
                
                self._draw_puyo_at(surface, x, y, puyo_type, 255, 1.0)
        
        # フェードアウト中のぷよを描画（弾けるエフェクト込み）
        for (x, y), data in self.disappearing_puyos.items():
            self._draw_puyo_at(surface, x, y, data['type'], data['alpha'], data['scale'])
            # パーティクルエフェクトを描画
            self._draw_particles(surface, data['particles'], data['type'])
    
    def _draw_puyo_at(self, surface: pygame.Surface, x: int, y: int, puyo_type: PuyoType, alpha: int, scale: float = 1.0):
        """指定位置にぷよを描画（アルファ・スケール対応）"""
        rect = pygame.Rect(
            self.offset_x + x * self.puyo_size + 2,
            self.offset_y + y * self.puyo_size + 2,
            self.puyo_size - 4,
            self.puyo_size - 4
        )
        
        color = PUYO_COLORS[puyo_type]
        center = rect.center
        base_radius = (self.puyo_size - 4) // 2
        radius = int(base_radius * scale)
        
        if alpha < 255 or scale != 1.0:
            # スケールまたは半透明描画用のサーフェスを作成
            surface_size = int(base_radius * 2 * max(1.5, scale))  # 十分な大きさを確保
            puyo_surface = pygame.Surface((surface_size, surface_size))
            puyo_surface.set_alpha(alpha)
            puyo_surface.fill((0, 0, 0))
            puyo_surface.set_colorkey((0, 0, 0))
            
            # サーフェスの中心
            surf_center = surface_size // 2
            
            # ぷよを描画
            if radius > 0:
                pygame.draw.circle(puyo_surface, color, (surf_center, surf_center), radius)
                pygame.draw.circle(puyo_surface, Colors.WHITE, (surf_center, surf_center), radius, max(1, int(2 * scale)))
                
                # ハイライト効果
                highlight_radius = max(1, int((radius // 3) * scale))
                highlight_center = (surf_center - int((radius//3) * scale), surf_center - int((radius//3) * scale))
                if highlight_radius > 0:
                    pygame.draw.circle(puyo_surface, Colors.WHITE, highlight_center, highlight_radius)
            
            # 描画
            surface.blit(puyo_surface, (center[0] - surface_size//2, center[1] - surface_size//2))
        else:
            # 通常描画
            pygame.draw.circle(surface, color, center, radius)
            pygame.draw.circle(surface, Colors.WHITE, center, radius, 2)
            
            # ハイライト効果
            highlight_radius = radius // 3
            highlight_center = (center[0] - radius//3, center[1] - radius//3)
            pygame.draw.circle(surface, Colors.WHITE, highlight_center, highlight_radius)
    
    def _draw_particles(self, surface: pygame.Surface, particles: List[dict], puyo_type: PuyoType):
        """パーティクルエフェクトを描画"""
        color = PUYO_COLORS[puyo_type]
        
        for particle in particles:
            if particle['life'] > 0:
                # パーティクルのアルファ値計算
                life_ratio = particle['life'] / particle['max_life']
                alpha = int(255 * life_ratio)
                size = int(particle['size'] * life_ratio)
                
                if size > 0 and alpha > 0:
                    # パーティクル描画用サーフェス
                    particle_surface = pygame.Surface((size * 2, size * 2))
                    particle_surface.set_alpha(alpha)
                    particle_surface.fill((0, 0, 0))
                    particle_surface.set_colorkey((0, 0, 0))
                    
                    # 小さな円として描画
                    pygame.draw.circle(particle_surface, color, (size, size), size)
                    
                    # 描画
                    surface.blit(particle_surface, (int(particle['x'] - size), int(particle['y'] - size)))
    
    def _render_connection_effects(self, surface: pygame.Surface):
        """連結ぷよのエフェクトを描画"""
        import time
        
        # アニメーション用の時間取得
        current_time = time.time()
        pulse_intensity = (math.sin(current_time * 8) + 1) / 2  # 0-1の間で振動
        
        # 効率化のため、処理済みの位置を記録
        processed = set()
        
        # 各ぷよについて連結をチェック
        for x in range(self.width):
            for y in range(self.height):
                pos = PuyoPosition(x, y)
                
                if pos in processed:
                    continue
                
                puyo_type = self.get_puyo(x, y)
                
                if puyo_type == PuyoType.EMPTY or puyo_type == PuyoType.GARBAGE:
                    continue
                
                # 連結している同色ぷよを検索
                connected = self.find_connected_puyos(x, y)
                
                # 処理済みに追加
                processed.update(connected)
                
                # 2個以上連結している場合にエフェクト表示
                if len(connected) >= 2:
                    self._render_connection_highlight(surface, connected, puyo_type, pulse_intensity)
    
    def _render_connection_highlight(self, surface: pygame.Surface, connected_positions: set, puyo_type: PuyoType, pulse_intensity: float):
        """連結ハイライトエフェクトを描画"""
        base_color = PUYO_COLORS[puyo_type]
        
        for pos in connected_positions:
            x, y = pos.x, pos.y
            
            # ぷよの中心座標
            center_x = self.offset_x + x * self.puyo_size + self.puyo_size // 2
            center_y = self.offset_y + y * self.puyo_size + self.puyo_size // 2
            
            # パルス効果でサイズと透明度を変化
            effect_radius = int((self.puyo_size // 2 - 2) * (0.8 + 0.4 * pulse_intensity))
            
            # 明るい色でアウトラインエフェクト
            bright_color = tuple(min(255, int(c * 1.5)) for c in base_color)
            
            # 外側のグロウエフェクト
            for i in range(3):
                glow_radius = effect_radius + i * 2
                alpha = int(80 * pulse_intensity * (3 - i) / 3)
                
                # 半透明サーフェスを作成
                glow_surface = pygame.Surface((glow_radius * 2 + 4, glow_radius * 2 + 4))
                glow_surface.set_alpha(alpha)
                glow_surface.fill((0, 0, 0))
                glow_surface.set_colorkey((0, 0, 0))
                
                pygame.draw.circle(glow_surface, bright_color, 
                                 (glow_radius + 2, glow_radius + 2), glow_radius)
                
                surface.blit(glow_surface, 
                           (center_x - glow_radius - 2, center_y - glow_radius - 2))
            
            # 連結線を描画
            self._render_connection_lines(surface, pos, connected_positions, bright_color, pulse_intensity)
    
    def _render_connection_lines(self, surface: pygame.Surface, current_pos, connected_positions: set, color: tuple, pulse_intensity: float):
        """連結線を描画"""
        x, y = current_pos.x, current_pos.y
        center_x = self.offset_x + x * self.puyo_size + self.puyo_size // 2
        center_y = self.offset_y + y * self.puyo_size + self.puyo_size // 2
        
        # 隣接する4方向をチェック
        directions = [(0, -1), (1, 0), (0, 1), (-1, 0)]
        
        for dx, dy in directions:
            neighbor_pos = PuyoPosition(x + dx, y + dy)
            
            if neighbor_pos in connected_positions:
                # 隣接ぷよの中心座標
                neighbor_center_x = self.offset_x + (x + dx) * self.puyo_size + self.puyo_size // 2
                neighbor_center_y = self.offset_y + (y + dy) * self.puyo_size + self.puyo_size // 2
                
                # パルス効果で線の太さを変化
                line_width = int(3 + 2 * pulse_intensity)
                
                # 連結線を描画
                pygame.draw.line(surface, color, 
                               (center_x, center_y), 
                               (neighbor_center_x, neighbor_center_y), 
                               line_width)
    
    def _render_border(self, surface: pygame.Surface):
        """グリッドの枠線を描画"""
        border_rect = pygame.Rect(
            self.offset_x - 2,
            self.offset_y - 2,
            self.width * self.puyo_size + 4,
            self.height * self.puyo_size + 4
        )
        
        pygame.draw.rect(surface, Colors.WHITE, border_rect, 3)
    
    def pixel_to_grid(self, pixel_x: int, pixel_y: int) -> Tuple[int, int]:
        """ピクセル座標をグリッド座標に変換"""
        grid_x = (pixel_x - self.offset_x) // self.puyo_size
        grid_y = (pixel_y - self.offset_y) // self.puyo_size
        return grid_x, grid_y
    
    def grid_to_pixel(self, grid_x: int, grid_y: int) -> Tuple[int, int]:
        """グリッド座標をピクセル座標に変換"""
        pixel_x = self.offset_x + grid_x * self.puyo_size
        pixel_y = self.offset_y + grid_y * self.puyo_size
        return pixel_x, pixel_y
    
    def __str__(self) -> str:
        """デバッグ用文字列表現"""
        lines = []
        for y in range(self.height):
            line = ""
            for x in range(self.width):
                puyo = self.get_puyo(x, y)
                if puyo == PuyoType.EMPTY:
                    line += "."
                else:
                    line += str(puyo.value)
            lines.append(line)
        return "\n".join(lines)


if __name__ == "__main__":
    # 簡単なテスト
    logging.basicConfig(level=logging.INFO)
    
    grid = PuyoGrid()
    
    # テスト用のぷよ配置
    grid.drop_puyo(0, PuyoType.RED)
    grid.drop_puyo(0, PuyoType.RED)
    grid.drop_puyo(0, PuyoType.RED)
    grid.drop_puyo(0, PuyoType.RED)
    
    grid.drop_puyo(1, PuyoType.BLUE)
    grid.drop_puyo(1, PuyoType.BLUE)
    grid.drop_puyo(1, PuyoType.BLUE)
    grid.drop_puyo(1, PuyoType.BLUE)
    
    print("Grid state:")
    print(grid)
    
    # 連鎖テスト
    score, eliminated = grid.execute_full_chain_sequence()
    print(f"\nChain result: Score={score}, Eliminated={eliminated}")
    
    # Test the new get_last_chain_positions method
    chain_positions = grid.get_last_chain_positions()
    print(f"Chain positions: {chain_positions}")
    
    # Test that positions are cleared after use
    chain_positions_2 = grid.get_last_chain_positions()
    print(f"Chain positions after second call (should be empty): {chain_positions_2}")
    
    print("\nGrid after chain:")
    print(grid)