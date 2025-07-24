"""
戦闘ハンドラー - ぷよぷよ × ローグライクのリアルタイム戦闘システム
"""

import pygame
import logging
import math
from typing import Optional, List

from ..core.constants import *
from ..core.game_engine import GameEngine, get_appropriate_font
from ..core.authentic_demo_handler import AuthenticDemoHandler
from ..core.background_renderer import BackgroundRenderer
from ..core.top_ui_bar import TopUIBar
from .enemy import Enemy, EnemyAction, EnemyGroup, create_enemy_group, ActionType
from .enemy_renderer import EnemyRenderer
from .enemy_intent_renderer import EnemyIntentRenderer

logger = logging.getLogger(__name__)


class Player:
    """プレイヤー情報クラス"""
    
    def __init__(self):
        self.max_hp = PLAYER_MAX_HP
        self.current_hp = PLAYER_INITIAL_HP
        self.is_alive = True
        
        # 戦闘統計
        self.total_damage_dealt = 0
        self.total_chains_made = 0
        
        # 視覚効果
        self.damage_flash_timer = 0.0
        self.damage_flash_duration = 0.5
    
    def take_damage(self, damage: int) -> bool:
        """ダメージを受ける"""
        if not self.is_alive:
            return False
        
        self.current_hp -= damage
        self.damage_flash_timer = self.damage_flash_duration
        
        logger.info(f"Player took {damage} damage ({self.current_hp}/{self.max_hp})")
        
        if self.current_hp <= 0:
            self.current_hp = 0
            self.is_alive = False
            logger.info("Player defeated!")
            return True
        
        return False
    
    def heal(self, amount: int):
        """回復"""
        self.current_hp = min(self.max_hp, self.current_hp + amount)
        logger.info(f"Player healed {amount} HP ({self.current_hp}/{self.max_hp})")
    
    def update(self, dt: float):
        """更新処理"""
        if self.damage_flash_timer > 0:
            self.damage_flash_timer -= dt


class BattleHandler:
    """リアルタイム戦闘ハンドラー"""
    
    def __init__(self, engine: GameEngine, floor_level: int = 1):
        self.engine = engine
        self.floor_level = floor_level
        
        # プレイヤー
        self.player = Player()
        
        # 敵グループ
        enemies = create_enemy_group(floor_level)
        self.enemy_group = EnemyGroup(enemies)
        
        # ぷよぷよシステム（AuthenticDemoHandlerをベースに使用）
        self.puyo_handler = AuthenticDemoHandler(engine)
        
        # 戦闘状態
        self.battle_active = True
        self.battle_result = None  # None, "victory", "defeat"
        
        # ダメージ計算
        self.chain_damage_multiplier = 1.0
        
        # UI位置 - 敵情報をぷよエリアの右下に配置
        # ぷよエリアの右側、ぷよエリアの下端に合わせる
        puyo_area_right = GRID_OFFSET_X + GRID_WIDTH * PUYO_SIZE + 80
        puyo_area_bottom = GRID_OFFSET_Y + GRID_HEIGHT * PUYO_SIZE
        available_width = SCREEN_WIDTH - puyo_area_right - 100  # 右端マージン
        self.battle_ui_x = puyo_area_right + available_width // 2  # より右に配置
        self.battle_ui_y = puyo_area_bottom - 150  # より下に配置
        
        # エフェクト
        self.damage_numbers = []  # ダメージ数値表示
        
        # 新しいビジュアルシステム
        self.background_renderer = BackgroundRenderer()
        self.top_ui_bar = TopUIBar(self.engine.fonts)
        self.intent_renderer = EnemyIntentRenderer()
        
        enemy_names = [e.get_display_name() for e in self.enemy_group.enemies]
        logger.info(f"Battle started: Floor {floor_level} vs {', '.join(enemy_names)}")
    
    def on_enter(self, previous_state):
        """戦闘開始"""
        self.puyo_handler.on_enter(previous_state)
        logger.info("Entering battle state")
    
    def on_exit(self):
        """戦闘終了"""
        self.puyo_handler.on_exit()
        logger.info("Exiting battle state")
    
    def update(self, dt: float):
        """更新処理"""
        if not self.battle_active:
            return
        
        # プレイヤー更新
        self.player.update(dt)
        
        # ぷよぷよシステム更新
        self.puyo_handler.update(dt)
        
        # 連鎖によるダメージ処理
        self._check_chain_damage()
        
        # 敵グループの更新と攻撃
        enemy_actions = self.enemy_group.update(dt, self.player.current_hp)
        for enemy, action in enemy_actions:
            self._execute_enemy_action(enemy, action)
        
        # ダメージ数値エフェクト更新
        self._update_damage_numbers(dt)
        
        # 新しいビジュアルシステム更新
        self.background_renderer.update(dt)
        self.top_ui_bar.update(dt)
        self.intent_renderer.update(dt)
        
        # 戦闘結果判定
        self._check_battle_result()
    
    def _check_chain_damage(self):
        """連鎖ダメージをチェック"""
        # 最後の連鎖スコアが更新されていたらダメージを与える
        last_score = self.puyo_handler.puyo_grid.last_chain_score
        
        if last_score > 0:
            # スコアをダメージに変換
            base_damage = last_score // CHAIN_SCORE_BASE
            chain_damage = int(base_damage * self.chain_damage_multiplier)
            
            if chain_damage > 0:
                # 選択中の敵にダメージ
                target = self.enemy_group.get_selected_target()
                if target:
                    defeated = target.take_damage(chain_damage)
                    self.player.total_damage_dealt += chain_damage
                    
                    # ダメージ数値表示
                    target_pos = self._get_enemy_display_position(target)
                    self._add_damage_number(chain_damage, Colors.YELLOW, target_pos)
                    
                    # 全敵が倒されたかチェック
                    if self.enemy_group.is_all_defeated():
                        self.battle_result = "victory"
                        self.battle_active = False
                
                # スコアをリセット（重複処理を防ぐ）
                self.puyo_handler.puyo_grid.last_chain_score = 0
                
                logger.info(f"Chain dealt {chain_damage} damage to enemy")
    
    def _execute_enemy_action(self, enemy: Enemy, action: EnemyAction):
        """敵の行動を実行"""
        if action.action_type == ActionType.ATTACK or action.action_type == ActionType.SPECIAL:
            # プレイヤーにダメージ
            final_damage = action.damage
            
            # バフによるダメージ増加
            if "attack_buff" in enemy.buffs:
                boost = enemy.buffs["attack_buff"][0] / 100
                final_damage = int(final_damage * (1 + boost))
            
            defeated = self.player.take_damage(final_damage)
            
            # ダメージ数値表示
            self._add_damage_number(final_damage, Colors.RED, target_player=True)
            
            # プレイヤーが倒されたかチェック
            if defeated:
                self.battle_result = "defeat"
                self.battle_active = False
            
            logger.info(f"{enemy.get_display_name()} used {action.name}: {final_damage} damage")
        
        elif action.action_type == ActionType.GUARD:
            enemy.is_guarding = True
            logger.info(f"{enemy.get_display_name()} is guarding")
        
        elif action.action_type == ActionType.HEAL:
            enemy.heal(action.effect_value)
            logger.info(f"{enemy.get_display_name()} healed {action.effect_value} HP")
        
        elif action.action_type == ActionType.BUFF:
            enemy.apply_buff("attack_buff", action.effect_value, 10.0)
            logger.info(f"{enemy.get_display_name()} gained attack buff")
        
        elif action.action_type == ActionType.DEBUFF:
            # プレイヤーにデバフ適用（今後実装）
            logger.info(f"{enemy.get_display_name()} attempted to debuff player")
    
    def _add_damage_number(self, damage: int, color: tuple, target_player: bool = False, position: tuple = None):
        """ダメージ数値を追加"""
        if target_player:
            # プレイヤー側（左側）
            x = GRID_OFFSET_X + 50
            y = GRID_OFFSET_Y + 100
        elif position:
            # 指定位置
            x, y = position
        else:
            # デフォルト敵側（右側）
            x = self.battle_ui_x + 100
            y = self.battle_ui_y - 50
        
        self.damage_numbers.append({
            'damage': damage,
            'color': color,
            'x': x,
            'y': y,
            'timer': 2.0,
            'float_speed': 30
        })
    
    def _update_damage_numbers(self, dt: float):
        """ダメージ数値エフェクトを更新"""
        for number in self.damage_numbers[:]:
            number['timer'] -= dt
            number['y'] -= number['float_speed'] * dt
            
            if number['timer'] <= 0:
                self.damage_numbers.remove(number)
    
    def _check_battle_result(self):
        """戦闘結果をチェック"""
        if not self.battle_active:
            return
        
        if not self.player.is_alive:
            self.battle_result = "defeat"
            self.battle_active = False
        elif self.enemy_group.is_all_defeated():
            self.battle_result = "victory"
            self.battle_active = False
    
    def handle_event(self, event: pygame.event.Event):
        """イベント処理"""
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1 and self.battle_active:  # 左クリック
                # 敵選択
                enemy_positions = self._get_all_enemy_positions()
                if self.enemy_group.select_target_by_click(event.pos[0], event.pos[1], enemy_positions):
                    return
        
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                if not self.battle_active:
                    # 戦闘終了後はメニューに戻る
                    self.engine.change_state(GameState.MENU)
                else:
                    # 戦闘から逃げる（敗北扱い）
                    self.battle_result = "defeat"
                    self.battle_active = False
                return
            
            elif event.key == pygame.K_RETURN and not self.battle_active:
                if self.battle_result == "victory":
                    # 勝利時は報酬選択画面へ
                    from ..rewards.reward_system import create_battle_rewards, RewardSelectionHandler
                    rewards = create_battle_rewards(self.floor_level, "normal", False)
                    reward_handler = RewardSelectionHandler(self.engine, rewards)
                    self.engine.register_state_handler(GameState.REWARD_SELECT, reward_handler)
                    self.engine.change_state(GameState.REWARD_SELECT)
                else:
                    # 敗北時はリトライ（新しい戦闘）
                    new_battle = BattleHandler(self.engine, self.floor_level)
                    self.engine.register_state_handler(GameState.REAL_BATTLE, new_battle)
                    self.engine.change_state(GameState.REAL_BATTLE)
                return
            
            elif event.key == pygame.K_TAB and self.battle_active:
                # TABキーで敵ターゲット切り替え
                self.enemy_group.select_next_target()
                target = self.enemy_group.get_selected_target()
                if target:
                    logger.info(f"Target switched to: {target.get_display_name()}")
                return
            
            elif event.key == pygame.K_q and self.battle_active:
                # Qキーで前の敵に切り替え
                self.enemy_group.select_previous_target()
                target = self.enemy_group.get_selected_target()
                if target:
                    logger.info(f"Target switched to: {target.get_display_name()}")
                return
        
        # ぷよぷよの操作は戦闘中のみ
        if self.battle_active:
            self.puyo_handler.handle_event(event)
    
    def render(self, surface: pygame.Surface):
        """描画処理"""
        # 美しいダンジョン背景を描画
        logger.debug("Drawing background...")
        self.background_renderer.draw_background(surface)
        
        # 上部UIバーを描画
        # プレイヤーのダメージを受けた時のフラッシュ効果
        if self.player.damage_flash_timer > 0:
            self.top_ui_bar.trigger_damage_flash()
        
        logger.debug("Drawing top UI bar...")
        self.top_ui_bar.draw_top_bar(
            surface,
            self.player.current_hp, self.player.max_hp,
            3, 3,  # エネルギー（固定値）
            150,   # ゴールド（固定値）
            self.floor_level
        )
        
        # ぷよぷよフィールド描画（背景の上に）
        self.puyo_handler.render(surface)
        
        # プレイヤーダメージフラッシュ
        if self.player.damage_flash_timer > 0:
            flash_alpha = int(128 * (self.player.damage_flash_timer / self.player.damage_flash_duration))
            flash_surface = pygame.Surface((GRID_WIDTH * PUYO_SIZE, GRID_HEIGHT * PUYO_SIZE))
            flash_surface.set_alpha(flash_alpha)
            flash_surface.fill(Colors.RED)
            surface.blit(flash_surface, (GRID_OFFSET_X, GRID_OFFSET_Y))
        
        # 敵とその行動予告を描画
        self._render_enemies_with_intents(surface)
        
        # ダメージ数値描画
        self._render_damage_numbers(surface)
        
        # 戦闘結果画面
        if not self.battle_active:
            self._render_battle_result(surface)
        else:
            # 戦闘統計を右下に表示
            self._render_battle_stats(surface)
    
    def _render_enemies_with_intents(self, surface: pygame.Surface):
        """敵とその行動予告を描画（シンプルなスライム表示）"""
        if not self.enemy_group.alive_enemies:
            return
        
        # 敵の配置設定 - さらに大きなサイズ
        enemy_size = 240  # スライム単体のサイズ（180から240に拡大）
        enemy_spacing = 30
        start_x = self.battle_ui_x
        start_y = self.battle_ui_y
        
        # 敵の数に応じて配置を調整
        num_enemies = len(self.enemy_group.alive_enemies)
        if num_enemies > 1:
            # 複数の敵：横並び配置
            total_width = num_enemies * enemy_size + (num_enemies - 1) * enemy_spacing
            start_x = self.battle_ui_x - total_width // 2 + enemy_size // 2
        
        for i, enemy in enumerate(self.enemy_group.alive_enemies):
            if num_enemies > 1:
                # 敵の表示位置 - 横一列配置
                x = start_x + i * (enemy_size + enemy_spacing)
                y = start_y
            else:
                # 単体の敵：中央配置
                x = start_x
                y = start_y
            
            # 選択中の敵判定
            is_selected = (enemy == self.enemy_group.get_selected_target())
            
            # 敵ビジュアル描画（単体スライム）
            hp_ratio = enemy.current_hp / enemy.max_hp
            EnemyRenderer.draw_enemy(
                surface, enemy.enemy_type, 
                x, y, enemy_size, enemy_size,
                hp_ratio, is_selected
            )
            
            # 選択時の視覚的フィードバック（スライムの周りを少し明るく）
            if is_selected:
                # 半透明の明るい円を描画
                select_surface = pygame.Surface((enemy_size + 20, enemy_size + 20))
                select_surface.set_alpha(60)
                pygame.draw.circle(select_surface, Colors.WHITE, 
                                 (enemy_size//2 + 10, enemy_size//2 + 10), enemy_size//2 + 10, 5)
                surface.blit(select_surface, (x - 10, y - 10))
            
            # 選択時の効果は削除（シンプルに）
            
            # HPバー（スライムの下に小さく表示）
            hp_bar_width = enemy_size - 10
            hp_bar_height = 8
            hp_bar_x = x + 5
            hp_bar_y = y + enemy_size + 5
            
            # HP背景
            hp_bg_rect = pygame.Rect(hp_bar_x, hp_bar_y, hp_bar_width, hp_bar_height)
            pygame.draw.rect(surface, (60, 30, 30), hp_bg_rect)
            
            # HP前景
            hp_fg_rect = pygame.Rect(hp_bar_x, hp_bar_y, int(hp_bar_width * hp_ratio), hp_bar_height)
            hp_color = enemy.get_status_color()
            pygame.draw.rect(surface, hp_color, hp_fg_rect)
            pygame.draw.rect(surface, (120, 100, 80), hp_bg_rect, 1)
            
            # HP数値（小さく表示）
            hp_text = f"{enemy.current_hp}/{enemy.max_hp}"
            hp_font = get_appropriate_font(self.engine.fonts, hp_text, 'small')
            hp_surface = hp_font.render(hp_text, True, Colors.WHITE)
            hp_rect = hp_surface.get_rect(centerx=x + enemy_size // 2, y=hp_bar_y + hp_bar_height + 2)
            surface.blit(hp_surface, hp_rect)
            
            # 攻撃タイマー表示（HPバーの下）
            attack_progress = enemy.attack_timer / enemy.attack_interval
            timer_bar_y = hp_bar_y + hp_bar_height + 20
            timer_rect = pygame.Rect(hp_bar_x, timer_bar_y, hp_bar_width, 6)
            pygame.draw.rect(surface, (60, 40, 30), timer_rect)
            
            timer_fg_rect = pygame.Rect(hp_bar_x, timer_bar_y, int(hp_bar_width * attack_progress), 6)
            pygame.draw.rect(surface, Colors.ORANGE, timer_fg_rect)
            pygame.draw.rect(surface, (120, 100, 80), timer_rect, 1)
            
            # タイマーラベル
            timer_text = f"攻撃まで: {enemy.attack_interval - enemy.attack_timer:.1f}s"
            timer_font = get_appropriate_font(self.engine.fonts, timer_text, 'small')
            timer_surface = timer_font.render(timer_text, True, Colors.LIGHT_GRAY)
            timer_text_rect = timer_surface.get_rect(centerx=x + enemy_size // 2, y=timer_bar_y + 8)
            surface.blit(timer_surface, timer_text_rect)
            
            # 敵の上に行動予告を描画
            next_action_info = enemy.get_next_action_info()
            if next_action_info:
                intent_center_x = x + enemy_size // 2
                intent_center_y = y - 20  # スライムの頭の上
                self.intent_renderer.draw_intent(surface, intent_center_x, intent_center_y, 
                                               next_action_info, self.engine.fonts)
    
    def _render_battle_stats(self, surface: pygame.Surface):
        """戦闘統計を右下に表示"""
        # 統計位置（右下角）
        stats_x = SCREEN_WIDTH - 250
        stats_y = SCREEN_HEIGHT - 120
        
        # 背景
        stats_bg = pygame.Rect(stats_x - 10, stats_y - 10, 240, 110)
        
        # 半透明背景
        bg_surface = pygame.Surface((240, 110))
        bg_surface.set_alpha(180)
        bg_surface.fill((20, 20, 30))
        surface.blit(bg_surface, (stats_x - 10, stats_y - 10))
        
        pygame.draw.rect(surface, (80, 70, 60), stats_bg, 2)
        
        # 統計データ
        stats = [
            f"与えたダメージ: {self.player.total_damage_dealt}",
            f"連鎖数: {self.puyo_handler.total_chains}",
            f"現在スコア: {self.puyo_handler.total_score}",
        ]
        
        for i, stat in enumerate(stats):
            stat_font = get_appropriate_font(self.engine.fonts, stat, 'small')
            stat_text = stat_font.render(stat, True, Colors.LIGHT_GRAY)
            surface.blit(stat_text, (stats_x, stats_y + i * 20))
    
    def _render_battle_ui(self, surface: pygame.Surface):
        """戦闘UI描画"""
        font_large = self.engine.fonts['large']
        font_medium = self.engine.fonts['medium']
        font_small = self.engine.fonts['small']
        
        # プレイヤーHP表示
        player_hp_text = font_medium.render(f"Player HP: {self.player.current_hp}/{self.player.max_hp}", True, Colors.WHITE)
        surface.blit(player_hp_text, (GRID_OFFSET_X, GRID_OFFSET_Y - 40))
        
        # プレイヤーHPバー
        hp_bar_width = 200
        hp_bar_height = 20
        hp_ratio = self.player.current_hp / self.player.max_hp
        
        # HPバー背景
        hp_bg_rect = pygame.Rect(GRID_OFFSET_X, GRID_OFFSET_Y - 20, hp_bar_width, hp_bar_height)
        pygame.draw.rect(surface, Colors.DARK_GRAY, hp_bg_rect)
        
        # HPバー
        hp_fg_rect = pygame.Rect(GRID_OFFSET_X, GRID_OFFSET_Y - 20, int(hp_bar_width * hp_ratio), hp_bar_height)
        hp_color = Colors.GREEN if hp_ratio > 0.5 else Colors.YELLOW if hp_ratio > 0.2 else Colors.RED
        pygame.draw.rect(surface, hp_color, hp_fg_rect)
        
        # プレイヤーダメージフラッシュ
        if self.player.damage_flash_timer > 0:
            flash_alpha = int(128 * (self.player.damage_flash_timer / self.player.damage_flash_duration))
            flash_surface = pygame.Surface((GRID_WIDTH * PUYO_SIZE, GRID_HEIGHT * PUYO_SIZE))
            flash_surface.set_alpha(flash_alpha)
            flash_surface.fill(Colors.RED)
            surface.blit(flash_surface, (GRID_OFFSET_X, GRID_OFFSET_Y))
        
        # 複数敵情報表示
        self._render_enemies_info(surface)
        
        # 戦闘統計 - 敵情報の下に配置
        enemy_count = len(self.enemy_group.alive_enemies)
        enemy_area_height = enemy_count * (160 + 10)  # enemy_height + spacing
        stats_y = self.battle_ui_y + enemy_area_height + 20
        
        stats = [
            f"与えたダメージ: {self.player.total_damage_dealt}",
            f"連鎖数: {self.puyo_handler.total_chains}",
            f"現在スコア: {self.puyo_handler.total_score}",
        ]
        
        for i, stat in enumerate(stats):
            stat_font = get_appropriate_font(self.engine.fonts, stat, 'small')
            stat_text = stat_font.render(stat, True, Colors.LIGHT_GRAY)
            surface.blit(stat_text, (self.battle_ui_x, stats_y + i * 20))
    
    def _render_enemies_info(self, surface: pygame.Surface):
        """敵情報を描画"""
        font_large = self.engine.fonts['large']
        font_medium = self.engine.fonts['medium']
        font_small = self.engine.fonts['small']
        
        # デバッグ: 敵の数を確認
        logger.debug(f"Rendering {len(self.enemy_group.alive_enemies)} enemies")
        
        # 敵の配置 - 画面右端に最適化
        available_width = 280  # 右端エリア固定幅
        enemy_width = 260  # 単一列表示に最適化
        enemy_height = 160
        enemy_spacing = 10
        start_x = self.battle_ui_x
        start_y = self.battle_ui_y
        
        for i, enemy in enumerate(self.enemy_group.alive_enemies):
            # 敵の表示位置 - 縦一列配置
            x = start_x
            y = start_y + i * (enemy_height + enemy_spacing)
            
            # 選択中の敵は枠で囲む
            is_selected = (enemy == self.enemy_group.get_selected_target())
            # 選択時の黄色い枠を削除
            
            # 背景
            bg_rect = pygame.Rect(x, y, enemy_width, enemy_height)
            pygame.draw.rect(surface, Colors.DARK_GRAY, bg_rect)
            pygame.draw.rect(surface, Colors.WHITE, bg_rect, 1)
            
            # 敵ビジュアル描画（背景の上部に）
            visual_area_height = 80
            hp_ratio = enemy.current_hp / enemy.max_hp
            EnemyRenderer.draw_enemy(
                surface, enemy.enemy_type, 
                x + 10, y + 5, enemy_width - 20, visual_area_height,
                hp_ratio, is_selected
            )
            
            # 敵名（ビジュアルの下に）
            enemy_name = enemy.get_display_name()
            name_font = get_appropriate_font(self.engine.fonts, enemy_name, 'small')
            name_text = name_font.render(enemy_name, True, Colors.WHITE)
            name_rect = name_text.get_rect(centerx=x + enemy_width // 2, y=y + visual_area_height + 5)
            surface.blit(name_text, name_rect)
            
            # HP表示（名前の下に）
            hp_text = font_small.render(f"{enemy.current_hp}/{enemy.max_hp}", True, Colors.WHITE)
            hp_rect = hp_text.get_rect(centerx=x + enemy_width // 2, y=y + visual_area_height + 20)
            surface.blit(hp_text, hp_rect)
            
            # HPバー（HPテキストの下に）
            hp_bar_width = enemy_width - 20
            hp_bar_height = 12
            
            hp_bg_rect = pygame.Rect(x + 10, y + visual_area_height + 35, hp_bar_width, hp_bar_height)
            pygame.draw.rect(surface, Colors.DARK_GRAY, hp_bg_rect)
            
            hp_fg_rect = pygame.Rect(x + 10, y + visual_area_height + 35, int(hp_bar_width * hp_ratio), hp_bar_height)
            hp_color = enemy.get_status_color()
            pygame.draw.rect(surface, hp_color, hp_fg_rect)
            
            # 状態表示（HPバーの下に）
            status_texts = enemy.get_status_text()
            status_y_offset = visual_area_height + 52
            for j, status in enumerate(status_texts[:1]):  # 最大1個まで（スペース節約）
                status_font = get_appropriate_font(self.engine.fonts, status, 'small')
                status_text = status_font.render(status, True, Colors.LIGHT_GRAY)
                surface.blit(status_text, (x + 5, y + status_y_offset + j * 15))
            
            # 次回行動予告表示
            next_action_info = enemy.get_next_action_info()
            if next_action_info:
                next_y = y + visual_area_height + 70
                
                # 次回行動アイコンと名前
                action_icon = next_action_info.get('icon', '❓')
                action_name = next_action_info.get('name', '不明')
                
                # アイコンを表示
                icon_text = font_small.render(action_icon, True, Colors.YELLOW)
                surface.blit(icon_text, (x + 5, next_y))
                
                # 行動名を表示
                action_font = get_appropriate_font(self.engine.fonts, action_name, 'small')
                name_text = action_font.render(action_name, True, Colors.YELLOW)
                surface.blit(name_text, (x + 25, next_y))
                
                # ダメージや効果値を表示
                if 'damage' in next_action_info:
                    damage_str = f"{next_action_info['damage']}ダメージ"
                    damage_font = get_appropriate_font(self.engine.fonts, damage_str, 'small')
                    damage_text = damage_font.render(damage_str, True, Colors.RED)
                    surface.blit(damage_text, (x + 5, next_y + 20))
                elif 'heal_amount' in next_action_info:
                    heal_str = f"{next_action_info['heal_amount']}回復"
                    heal_font = get_appropriate_font(self.engine.fonts, heal_str, 'small')
                    heal_text = heal_font.render(heal_str, True, Colors.GREEN)
                    surface.blit(heal_text, (x + 5, next_y + 20))
                elif 'effect_value' in next_action_info:
                    effect_str = f"効果: {next_action_info['effect_value']}%"
                    effect_font = get_appropriate_font(self.engine.fonts, effect_str, 'small')
                    effect_text = effect_font.render(effect_str, True, Colors.BLUE)
                    surface.blit(effect_text, (x + 5, next_y + 20))
            
            # 攻撃タイマー（最下部に配置）
            attack_progress = enemy.attack_timer / enemy.attack_interval
            timer_y = y + enemy_height - 20
            timer_rect = pygame.Rect(x + 10, timer_y, hp_bar_width, 6)
            pygame.draw.rect(surface, Colors.DARK_GRAY, timer_rect)
            
            timer_fg_rect = pygame.Rect(x + 10, timer_y, int(hp_bar_width * attack_progress), 6)
            pygame.draw.rect(surface, Colors.ORANGE, timer_fg_rect)
            
            # タイマーラベル（小さく）
            timer_label_str = "次の行動"
            timer_font = get_appropriate_font(self.engine.fonts, timer_label_str, 'small')
            timer_label = timer_font.render(timer_label_str, True, Colors.LIGHT_GRAY)
            surface.blit(timer_label, (x + 10, timer_y - 12))
    
    def _get_all_enemy_positions(self) -> List[tuple]:
        """全敵の表示位置を取得（クリック判定用）"""
        positions = []
        enemy_size = 240  # スライム単体のサイズ（180から240に拡大）
        enemy_spacing = 30
        start_x = self.battle_ui_x
        start_y = self.battle_ui_y
        
        # 敵の数に応じて配置を調整
        num_enemies = len(self.enemy_group.alive_enemies)
        if num_enemies > 1:
            # 複数の敵：横並び配置
            total_width = num_enemies * enemy_size + (num_enemies - 1) * enemy_spacing
            start_x = self.battle_ui_x - total_width // 2 + enemy_size // 2
        
        for i, enemy in enumerate(self.enemy_group.alive_enemies):
            if num_enemies > 1:
                # 横一列配置
                x = start_x + i * (enemy_size + enemy_spacing)
                y = start_y
            else:
                # 単体配置
                x = start_x
                y = start_y
            positions.append((x, y, enemy_size, enemy_size))
        
        return positions
    
    def _get_enemy_display_position(self, target_enemy: Enemy) -> tuple:
        """特定の敵の表示位置を取得（ダメージ数値用）"""
        enemy_size = 240  # スライム単体のサイズ（180から240に拡大）
        enemy_spacing = 30
        start_x = self.battle_ui_x
        start_y = self.battle_ui_y
        
        # 敵の数に応じて配置を調整
        num_enemies = len(self.enemy_group.alive_enemies)
        if num_enemies > 1:
            # 複数の敵：横並び配置
            total_width = num_enemies * enemy_size + (num_enemies - 1) * enemy_spacing
            start_x = self.battle_ui_x - total_width // 2 + enemy_size // 2
        
        for i, enemy in enumerate(self.enemy_group.alive_enemies):
            if enemy == target_enemy:
                if num_enemies > 1:
                    # 横一列配置
                    x = start_x + i * (enemy_size + enemy_spacing) + enemy_size // 2
                    y = start_y + 20
                else:
                    # 単体配置
                    x = start_x + enemy_size // 2
                    y = start_y + 20
                return (x, y)
        
        return (self.battle_ui_x + enemy_size // 2, self.battle_ui_y + 50)
    
    def _render_damage_numbers(self, surface: pygame.Surface):
        """ダメージ数値を描画"""
        font_large = self.engine.fonts['large']
        
        for number in self.damage_numbers:
            alpha = int(255 * (number['timer'] / 2.0))
            
            # 数値テキスト
            damage_text = font_large.render(str(number['damage']), True, number['color'])
            
            # 透明度適用
            damage_surface = pygame.Surface(damage_text.get_size())
            damage_surface.set_alpha(alpha)
            damage_surface.blit(damage_text, (0, 0))
            
            surface.blit(damage_surface, (number['x'], number['y']))
    
    def _render_battle_result(self, surface: pygame.Surface):
        """戦闘結果画面を描画"""
        # 半透明オーバーレイ
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(180)
        overlay.fill(Colors.BLACK)
        surface.blit(overlay, (0, 0))
        
        font_title = self.engine.fonts['title']
        font_large = self.engine.fonts['large']
        font_medium = self.engine.fonts['medium']
        
        # 結果表示
        if self.battle_result == "victory":
            result_text = font_title.render("VICTORY!", True, Colors.GREEN)
            enemy_count = len(self.enemy_group.enemies)
            if enemy_count == 1:
                subtitle_str = f"{self.enemy_group.enemies[0].get_display_name()} 撃破!"
                subtitle_font = get_appropriate_font(self.engine.fonts, subtitle_str, 'large')
                subtitle_text = subtitle_font.render(subtitle_str, True, Colors.WHITE)
            else:
                subtitle_str = f"{enemy_count}体の敵を撃破!"
                subtitle_font = get_appropriate_font(self.engine.fonts, subtitle_str, 'large')
                subtitle_text = subtitle_font.render(subtitle_str, True, Colors.WHITE)
        else:
            result_text = font_title.render("DEFEAT", True, Colors.RED)
            subtitle_str = "敗北..."
            subtitle_font = get_appropriate_font(self.engine.fonts, subtitle_str, 'large')
            subtitle_text = subtitle_font.render(subtitle_str, True, Colors.WHITE)
        
        result_rect = result_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 100))
        surface.blit(result_text, result_rect)
        
        subtitle_rect = subtitle_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50))
        surface.blit(subtitle_text, subtitle_rect)
        
        # 統計表示
        stats = [
            f"与えたダメージ: {self.player.total_damage_dealt}",
            f"作った連鎖: {self.puyo_handler.total_chains}",
            f"最終スコア: {self.puyo_handler.total_score}",
        ]
        
        for i, stat in enumerate(stats):
            stat_font = get_appropriate_font(self.engine.fonts, stat, 'medium')
            stat_text = stat_font.render(stat, True, Colors.LIGHT_GRAY)
            stat_rect = stat_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 20 + i * 30))
            surface.blit(stat_text, stat_rect)
        
        # 操作説明
        if self.battle_result == "victory":
            instruction_str = "Enter - 報酬選択へ  ESC - メニューへ"
            instruction_font = get_appropriate_font(self.engine.fonts, instruction_str, 'medium')
            instruction_text = instruction_font.render(instruction_str, True, Colors.YELLOW)
        else:
            instruction_str = "Enter - リトライ  ESC - メニューへ"
            instruction_font = get_appropriate_font(self.engine.fonts, instruction_str, 'medium')
            instruction_text = instruction_font.render(instruction_str, True, Colors.YELLOW)
        
        # 戦闘中の操作説明も追加
        if not instruction_text:  # 戦闘中
            battle_instructions = [
                "ぷよぷよ: A/D-移動 S-高速落下 Space-回転",
                "ターゲット: TAB-次の敵 Q-前の敵 クリック-選択",
                "ESC-逃げる"
            ]
            
            for i, instruction in enumerate(battle_instructions):
                inst_font = get_appropriate_font(self.engine.fonts, instruction, 'small')
                inst_text = inst_font.render(instruction, True, Colors.LIGHT_GRAY)
                inst_rect = inst_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 80 + i * 20))
                surface.blit(inst_text, inst_rect)
        
        instruction_rect = instruction_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 150))
        surface.blit(instruction_text, instruction_rect)
    
    def _render_battle_instructions(self, surface: pygame.Surface):
        """戦闘中の操作説明を描画"""
        battle_instructions = [
            "ぷよぷよ: A/D-移動 S-高速落下 Space-回転",
            "ターゲット: TAB-次の敵 Q-前の敵 クリック-選択",
            "敵情報: 黄色アイコン=次回行動予告 オレンジバー=行動タイマー",
            "ESC-逃げる"
        ]
        
        for i, instruction in enumerate(battle_instructions):
            inst_font = get_appropriate_font(self.engine.fonts, instruction, 'small')
            inst_text = inst_font.render(instruction, True, Colors.LIGHT_GRAY)
            inst_rect = inst_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 80 + i * 20))
            surface.blit(inst_text, inst_rect)