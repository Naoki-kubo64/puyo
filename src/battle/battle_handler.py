"""
戦闘ハンドラー - ぷよぷよ × ローグライクのリアルタイム戦闘システム
"""

import pygame
import logging
import math
from typing import Optional, List

from core.constants import *
from core.game_engine import GameEngine, get_appropriate_font
from core.authentic_demo_handler import AuthenticDemoHandler
from core.background_renderer import BackgroundRenderer
from core.top_ui_bar import TopUIBar
from .enemy import Enemy, EnemyAction, EnemyGroup, create_enemy_group, ActionType
from .enemy_renderer import EnemyRenderer
from .enemy_intent_renderer import EnemyIntentRenderer
from .battle_ui_renderer import BattleUIRenderer
from special_puyo.special_puyo import special_puyo_manager
from rewards.reward_system import RewardGenerator, RewardSelectionHandler

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
        self.damage_flash_duration = DAMAGE_FLASH_DURATION
        
        # 特殊効果システム
        self.buffs = {}          # {buff_type: [value, duration]}
        self.debuffs = {}        # {debuff_type: [value, duration]}
        self.shields = {}        # {shield_type: [remaining_absorption, duration]}
        
        # 攻撃力修正
        self.attack_multiplier = 1.0
        
        # 反射効果
        self.reflect_active = False
        self.reflect_power = 0
        self.reflect_duration = 0.0
    
    def take_damage(self, damage: int) -> tuple[bool, int]:
        """ダメージを受ける（シールドや反射を考慮）"""
        if not self.is_alive:
            return False, 0
        
        original_damage = damage
        final_damage = damage
        reflected_damage = 0
        
        # 反射効果の処理
        if self.reflect_active:
            reflected_damage = int(final_damage * (self.reflect_power / 100))
            final_damage = final_damage - reflected_damage
            logger.info(f"Reflected {reflected_damage} damage back to enemy")
        
        # シールド効果の処理
        for shield_type in list(self.shields.keys()):
            remaining_absorption, duration = self.shields[shield_type]
            if remaining_absorption > 0:
                absorbed = min(final_damage, remaining_absorption)
                final_damage -= absorbed
                self.shields[shield_type][0] -= absorbed
                
                # 吸収シールドの場合はHPに変換
                if shield_type == "absorb":
                    self.heal(absorbed)
                
                logger.info(f"Shield absorbed {absorbed} damage, {self.shields[shield_type][0]} remaining")
                
                if self.shields[shield_type][0] <= 0:
                    del self.shields[shield_type]
                    logger.info(f"{shield_type} shield depleted")
                break
        
        # 最終ダメージを適用
        self.current_hp -= final_damage
        self.damage_flash_timer = self.damage_flash_duration
        
        logger.info(f"Player took {final_damage} damage (original: {original_damage}) ({self.current_hp}/{self.max_hp})")
        
        if self.current_hp <= 0:
            self.current_hp = 0
            self.is_alive = False
            logger.info("Player defeated!")
            return True, reflected_damage
        
        return False, reflected_damage
    
    def heal(self, amount: int):
        """回復"""
        self.current_hp = min(self.max_hp, self.current_hp + amount)
        logger.info(f"Player healed {amount} HP ({self.current_hp}/{self.max_hp})")
    
    def update(self, dt: float):
        """更新処理"""
        if self.damage_flash_timer > 0:
            self.damage_flash_timer -= dt
        
        # バフ・デバフの更新
        self._update_effects(dt)
    
    def _update_effects(self, dt: float):
        """バフ・デバフ効果を更新"""
        # バフの更新
        for buff_type in list(self.buffs.keys()):
            self.buffs[buff_type][1] -= dt
            if self.buffs[buff_type][1] <= 0:
                self._remove_buff(buff_type)
        
        # デバフの更新
        for debuff_type in list(self.debuffs.keys()):
            self.debuffs[debuff_type][1] -= dt
            if self.debuffs[debuff_type][1] <= 0:
                del self.debuffs[debuff_type]
        
        # シールドの更新
        for shield_type in list(self.shields.keys()):
            self.shields[shield_type][1] -= dt
            if self.shields[shield_type][1] <= 0:
                del self.shields[shield_type]
                logger.info(f"{shield_type} shield expired")
        
        # 反射効果の更新
        if self.reflect_active:
            self.reflect_duration -= dt
            if self.reflect_duration <= 0:
                self.reflect_active = False
                self.reflect_power = 0
                logger.info("Reflect effect expired")
        
        # 攻撃力修正の計算
        self._calculate_attack_multiplier()
    
    def _calculate_attack_multiplier(self):
        """攻撃力修正を計算"""
        multiplier = 1.0
        
        # バフによる攻撃力増加
        if "attack_buff" in self.buffs:
            boost = self.buffs["attack_buff"][0] / 100
            multiplier *= (1 + boost)
        
        # デバフによる攻撃力減少（将来の拡張用）
        if "attack_debuff" in self.debuffs:
            reduction = self.debuffs["attack_debuff"][0] / 100
            multiplier *= (1 - reduction)
        
        self.attack_multiplier = multiplier
    
    def _remove_buff(self, buff_type: str):
        """バフを削除"""
        if buff_type in self.buffs:
            del self.buffs[buff_type]
            logger.info(f"Player buff expired: {buff_type}")
    
    def apply_buff(self, buff_type: str, value: int, duration: float):
        """バフを適用"""
        self.buffs[buff_type] = [value, duration]
        logger.info(f"Player received buff: {buff_type} (+{value}%) for {duration}s")
    
    def apply_debuff(self, debuff_type: str, value: int, duration: float):
        """デバフを適用"""
        self.debuffs[debuff_type] = [value, duration]
        logger.info(f"Player received debuff: {debuff_type} (-{value}%) for {duration}s")
    
    def apply_shield(self, shield_type: str, absorption: int, duration: float):
        """シールドを適用"""
        self.shields[shield_type] = [absorption, duration]
        logger.info(f"Player received shield: {shield_type} (absorbs {absorption} damage) for {duration}s")
    
    def apply_reflect(self, power: int, duration: float):
        """反射効果を適用"""
        self.reflect_active = True
        self.reflect_power = power
        self.reflect_duration = duration
        logger.info(f"Player received reflect: {power}% reflection for {duration}s")


class BattleHandler:
    """リアルタイム戦闘ハンドラー"""
    
    def __init__(self, engine: GameEngine, floor_level: int = 1, current_node=None):
        self.engine = engine
        self.floor_level = floor_level
        self.current_node = current_node  # マップノード情報を保持
        
        # current_nodeが設定されていることを確認
        if self.current_node:
            logger.info(f"Battle handler initialized for node: {self.current_node.node_id}")
        else:
            logger.warning("Battle handler initialized without current_node!")
        
        # プレイヤー (統合されたプレイヤーデータを使用)
        self.player = self.engine.player  # ゲームエンジンの統合プレイヤーデータを使用
        self.battle_player = Player()  # 戦闘固有の機能用（バフ・デバフなど）
        
        # 戦闘開始時に battle_player の HP を PlayerData と同期
        self.battle_player.max_hp = self.player.max_hp
        self.battle_player.current_hp = self.player.hp
        self.battle_player.is_alive = self.player.hp > 0
        
        # 敵グループ
        enemies = create_enemy_group(floor_level)
        self.enemy_group = EnemyGroup(enemies)
        
        # ぷよぷよシステム（AuthenticDemoHandlerをベースに使用）
        self.puyo_handler = AuthenticDemoHandler(engine, parent_battle_handler=self)
        
        # 戦闘状態
        self.battle_active = True
        self.battle_result = None  # None, "victory", "defeat"
        
        # デバッグコマンド用
        self.debug_input = ""
        self.debug_mode = True  # デバッグモードを有効にする
        
        # ダメージ計算はPlayerData.chain_damage_multiplierを使用
        
        # 報酬システム
        self.reward_generator = RewardGenerator()
        self.reward_handler = None
        self.victory_rewards_generated = False
        
        # バトル開始カウントダウンシステム
        self.countdown_active = True
        self.countdown_timer = BATTLE_COUNTDOWN_DURATION
        self.countdown_start_time = BATTLE_COUNTDOWN_DURATION
        
        # UI位置 - 敵情報をぷよエリアの右下に配置
        # ぷよエリアの右側、ぷよエリアの下端に合わせる
        puyo_area_right = GRID_OFFSET_X + GRID_WIDTH * PUYO_SIZE + 80
        puyo_area_bottom = GRID_OFFSET_Y + GRID_HEIGHT * PUYO_SIZE
        available_width = SCREEN_WIDTH - puyo_area_right - 100  # 右端マージン
        self.battle_ui_x = puyo_area_right + int(available_width * BATTLE_UI_POSITION_OFFSET_RATIO)  # より右に配置
        self.battle_ui_y = puyo_area_bottom - 150  # より下に配置
        
        # エフェクト
        self.damage_numbers = []  # ダメージ数値表示
        
        # 新しいビジュアルシステム
        self.background_renderer = BackgroundRenderer()
        self.top_ui_bar = TopUIBar(self.engine.fonts)
        self.intent_renderer = EnemyIntentRenderer()
        self.ui_renderer = BattleUIRenderer(self.engine.fonts, self.battle_ui_x, self.battle_ui_y)
        
        enemy_names = [e.get_display_name() for e in self.enemy_group.enemies]
        logger.info(f"Battle started: Floor {floor_level} vs {', '.join(enemy_names)}")
    
    def _sync_player_hp(self):
        """PlayerDataとbattle_playerのHPを同期"""
        self.player.hp = self.battle_player.current_hp
        self.battle_player.max_hp = self.player.max_hp
        
        # 死亡状態を確認
        if self.player.hp <= 0:
            self.battle_player.is_alive = False
            self.player.hp = 0
        else:
            self.battle_player.is_alive = True
    
    def _finalize_battle_stats(self):
        """battle_playerの統計をPlayerData.statsに反映"""
        # 戦闘終了時にHPを同期
        self._sync_player_hp()
        
        # 戦闘結果をPlayerDataに記録
        won = (self.battle_result == "victory")
        self.player.update_combat_stats(
            damage_dealt=0,  # すでに連鎖ごとに加算済み
            chains_made=0,   # すでに連鎖ごとに加算済み  
            won=won
        )
        
        logger.info(f"Battle finalized: {self.battle_result}, HP: {self.player.hp}/{self.player.max_hp}")
    
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
        
        # カウントダウン処理
        if self.countdown_active:
            self.countdown_timer -= dt
            if self.countdown_timer <= 0:
                self.countdown_active = False
                logger.info("Battle countdown finished - combat started!")
            else:
                # カウントダウン中は制限された更新のみ
                self.background_renderer.update(dt)
                self.top_ui_bar.update(dt)
                # NEXTぷよなどの読み込みは継続
                if hasattr(self.puyo_handler, '_generate_initial_next_queue'):
                    pass  # NEXTキューの準備は継続
                return
        
        # プレイヤー更新（戦闘固有の機能のみ）
        self.battle_player.update(dt)
        
        # ぷよぷよシステム更新
        self.puyo_handler.update(dt)
        
        # 特殊ぷよシステム更新
        timed_effects = special_puyo_manager.update(dt)
        for effect in timed_effects:
            self._apply_special_effect(effect)
        
        # 連鎖によるダメージ処理
        self._check_chain_damage()
        
        # 敵グループの更新と攻撃（カウントダウン終了後のみ）
        enemy_actions = self.enemy_group.update(dt, self.player.hp)
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
        
        # 常に連鎖スコアをログ出力（デバッグ用）
        logger.debug(f"Checking chain damage - last_score: {last_score}")
        
        # デバッグ情報を追加
        if last_score > 0:
            logger.info(f"Chain detected! Score: {last_score}")
        
        if last_score > 0:
            # スコアをダメージに変換
            base_damage = max(1, last_score // CHAIN_SCORE_BASE)  # 最低1ダメージ保証
            
            # プレイヤーの攻撃力修正を適用（PlayerData + battle_playerのバフを組み合わせ）
            total_attack_multiplier = self.battle_player.attack_multiplier * self.player.chain_damage_multiplier
            modified_damage = int(base_damage * total_attack_multiplier)
            
            # 特殊ぷよによる連鎖の処理
            chain_positions = self.puyo_handler.puyo_grid.get_last_chain_positions()
            special_effects = special_puyo_manager.trigger_chain_effects(
                chain_positions, 
                battle_context=self, 
                puyo_grid=self.puyo_handler.puyo_grid
            )
            
            # 特殊効果の適用
            for effect in special_effects:
                self._apply_special_effect(effect)
                
                # ダメージ倍率効果
                if effect.get('type') == 'damage_multiplier':
                    multiplier = effect['power'] / 100
                    modified_damage = int(modified_damage * multiplier)
                    logger.info(f"Damage multiplied by {multiplier}x to {modified_damage}")
            
            # 最低ダメージ保証（テスト用）
            if modified_damage <= 0:
                modified_damage = 1
                logger.warning(f"Damage was <= 0, set to 1 for testing")
            
            # 選択中の敵にダメージ
            target = self.enemy_group.get_selected_target()
            if target:
                defeated = target.take_damage(modified_damage)
                # 統計情報の安全な更新
                if hasattr(self.player, 'stats') and self.player.stats:
                    self.player.stats.total_damage_dealt += modified_damage
                    self.player.stats.total_chains_made += 1
                
                # ダメージ数値表示
                target_pos = self._get_enemy_display_position(target)
                self._add_damage_number(modified_damage, Colors.YELLOW, target_pos)
                
                logger.info(f"Chain dealt {modified_damage} damage to {target.enemy_type} (HP: {target.current_hp}/{target.max_hp})")
                
                # 全敵が倒されたかチェック
                if self.enemy_group.is_all_defeated():
                    self._handle_victory()
                    logger.info("All enemies defeated - Victory!")
            else:
                logger.warning("No target selected for chain damage!")
            
            # スコアをリセット（重複処理を防ぐ）
            self.puyo_handler.puyo_grid.last_chain_score = 0
            
            logger.info(f"Chain attack: {last_score} score -> {base_damage} base damage -> {modified_damage} final damage")
    
    def _execute_enemy_action(self, enemy: Enemy, action: EnemyAction):
        """敵の行動を実行"""
        if action.action_type == ActionType.ATTACK or action.action_type == ActionType.SPECIAL:
            # プレイヤーにダメージ
            final_damage = action.damage
            
            # バフによるダメージ増加
            if "attack_buff" in enemy.buffs:
                boost = enemy.buffs["attack_buff"][0] / 100
                final_damage = int(final_damage * (1 + boost))
            
            # 呪い効果による敵攻撃力減少
            if "curse_debuff" in enemy.debuffs:
                reduction = enemy.debuffs["curse_debuff"][0] / 100
                final_damage = int(final_damage * (1 - reduction))
                logger.info(f"Enemy attack reduced by curse: {action.damage} -> {final_damage}")
            
            defeated, reflected_damage = self.battle_player.take_damage(final_damage)
            
            # HPを同期
            self._sync_player_hp()
            
            # 死亡状態を確認
            if self.player.hp <= 0:
                defeated = True
            
            # 反射ダメージを敵に与える
            if reflected_damage > 0:
                enemy_defeated = enemy.take_damage(reflected_damage)
                self._add_damage_number(reflected_damage, Colors.ORANGE, self._get_enemy_display_position(enemy))
                logger.info(f"Reflected {reflected_damage} damage to {enemy.get_display_name()}")
                
                if enemy_defeated and self.enemy_group.is_all_defeated():
                    self._handle_victory()
            
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
    
    def _apply_special_effect(self, effect: dict):
        """特殊ぷよの効果を適用"""
        effect_type = effect.get('effect_type', '')
        power = effect.get('power', 0)
        duration = effect.get('duration', 0.0)
        
        if effect_type == 'attack_buff':
            # バフぷよ：攻撃力上昇
            self.battle_player.apply_buff('attack_buff', power, duration)
            
        elif effect_type == 'heal_player':
            # 回復ぷよ：HP回復（PlayerDataとbattle_player両方を更新）
            healed = self.player.heal(power)
            self._sync_player_hp()
            
        elif effect_type == 'damage_reduction':
            # シールドぷよ：ダメージ軽減シールド
            self.battle_player.apply_shield('damage_reduction', power, duration)
            
        elif effect_type == 'absorb_barrier':
            # 吸収シールドぷよ：ダメージを吸収してHP変換
            self.battle_player.apply_shield('absorb', power, duration)
            
        elif effect_type == 'damage_reflect':
            # 反射ぷよ：ダメージ反射
            self.battle_player.apply_reflect(power, duration)
            
        elif effect_type == 'freeze_enemy':
            # 氷ぷよ：敵の行動遅延
            target = self.enemy_group.get_selected_target()
            if target:
                target.apply_stun(power)
                logger.info(f"Frozen {target.get_display_name()} for {power}s")
            
        elif effect_type == 'enemy_curse':
            # 呪いぷよ：敵の攻撃力減少
            target = self.enemy_group.get_selected_target()
            if target:
                target.apply_debuff('curse_debuff', power, duration)
                logger.info(f"Cursed {target.get_display_name()}: -{power}% attack for {duration}s")
            
        elif effect_type == 'poison_enemy':
            # 毒ぷよ：敵に継続ダメージ
            target = self.enemy_group.get_selected_target()
            if target:
                # 即座にダメージを与える（簡易実装）
                target.take_damage(power)
                logger.info(f"Poisoned {target.get_display_name()} for {power} damage")
                
        elif effect_type == 'delayed_poison':
            # 時限毒ぷよ：遅延毒ダメージ
            target = self.enemy_group.get_selected_target()
            if target:
                target.take_damage(power)
                logger.info(f"Timed poison dealt {power} damage to {target.get_display_name()}")
                
        elif effect_type == 'explosion' or effect_type == 'lightning_strike':
            # 爆弾・雷ぷよ：直接ダメージ
            target = self.enemy_group.get_selected_target()
            if target:
                target.take_damage(power)
                logger.info(f"Special attack dealt {power} damage to {target.get_display_name()}")
        
        # 効果の視覚的フィードバック
        if effect.get('description'):
            logger.info(f"Special effect activated: {effect['description']}")
    
    def _generate_victory_rewards(self):
        """勝利時の報酬を生成"""
        if self.victory_rewards_generated:
            return
        
        # ボス戦かどうかを判定（敵が1体で強力な場合）
        is_boss = len(self.enemy_group.enemies) == 1 and self.enemy_group.enemies[0].max_hp > 50
        
        # 敵のタイプを取得
        enemy_type = self.enemy_group.enemies[0].enemy_type.value if self.enemy_group.enemies else "normal"
        
        # 報酬を生成
        rewards = self.reward_generator.generate_battle_rewards(
            floor_level=self.floor_level,
            enemy_type=enemy_type,
            is_boss=is_boss
        )
        
        # 報酬選択ハンドラーを初期化（戦闘ハンドラー情報を渡す）
        self.reward_handler = RewardSelectionHandler(self.engine, rewards, battle_handler=self)
        self.victory_rewards_generated = True
        
        logger.info(f"Generated {len(rewards)} victory rewards for floor {self.floor_level}")
    
    def get_victory_rewards(self):
        """勝利報酬を取得（外部からアクセス用）"""
        return self.reward_handler if self.victory_rewards_generated else None
    
    def _return_to_dungeon_map(self):
        """ダンジョンマップに戻る"""
        try:
            from dungeon.map_handler import DungeonMapHandler
            
            # 戦闘勝利時：マップの進行状態を更新
            if self.battle_result == "victory" and hasattr(self.engine, 'persistent_dungeon_map') and self.engine.persistent_dungeon_map:
                dungeon_map = self.engine.persistent_dungeon_map
                
                logger.info(f"Battle victory! Current node: {self.current_node.node_id if self.current_node else 'None'}")
                logger.info(f"Map current node: {dungeon_map.current_node.node_id if dungeon_map.current_node else 'None'}")
                
                # 戦闘したノードを選択して次に進む
                target_node = self.current_node or dungeon_map.current_node
                
                if target_node:
                    logger.info(f"Processing battle victory for node: {target_node.node_id}")
                    
                    # select_nodeを使用して正しく進行
                    success = dungeon_map.select_node(target_node.node_id)
                    
                    if success:
                        available_nodes = dungeon_map.get_available_nodes()
                        logger.info(f"Battle victory: {target_node.node_id} completed -> Available: {[n.node_id for n in available_nodes]}")
                        
                        # デバッグ：次フロアの状態確認
                        next_floor = target_node.floor + 1
                        if next_floor < dungeon_map.total_floors:
                            next_floor_nodes = dungeon_map.get_nodes_by_floor(next_floor)
                            next_available = [n.node_id for n in next_floor_nodes if n.available]
                            logger.info(f"Next floor {next_floor} available nodes: {next_available}")
                    else:
                        logger.error(f"Failed to select node {target_node.node_id} after battle victory")
                        
                else:
                    logger.warning("No target node found for battle progression!")
                    # 最初から開始
                    floor_0_nodes = dungeon_map.get_nodes_by_floor(0)
                    if floor_0_nodes:
                        first_node = floor_0_nodes[0]
                        success = dungeon_map.select_node(first_node.node_id)
                        if success:
                            logger.info(f"Reset to initial position: {first_node.node_id}")
                        
                logger.info("Map progression updated after battle victory")
            
            # ダンジョンマップハンドラーを作成（既存のマップ状態を使用）
            map_handler = DungeonMapHandler(self.engine)
            
            # ダンジョンマップ状態に変更
            self.engine.register_state_handler(GameState.DUNGEON_MAP, map_handler)
            self.engine.change_state(GameState.DUNGEON_MAP)
            
            logger.info("Returned to dungeon map after battle")
            
        except Exception as e:
            logger.error(f"Failed to return to dungeon map: {e}")
            # フォールバック: メニューに戻る
            self.engine.change_state(GameState.MENU)
    
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
        
        if self.player.hp <= 0 or not self.battle_player.is_alive:
            self.battle_result = "defeat"
            self.battle_active = False
            self._finalize_battle_stats()
        elif self.enemy_group.is_all_defeated():
            self._handle_victory()
            self._finalize_battle_stats()
    
    def handle_event(self, event: pygame.event.Event):
        """イベント処理"""
        # マウス移動イベント処理（TopUIBarのホバー効果用）
        if event.type == pygame.MOUSEMOTION:
            self.top_ui_bar.handle_mouse_motion(event.pos)
        
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1 and self.battle_active:  # 左クリック
                # ポーションクリック処理
                if self.top_ui_bar.handle_potion_click(event.pos, self.player.inventory, self.player):
                    return
                
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
            
            elif event.key == pygame.K_k and self.battle_active:
                # デバッグ用：Kキーで敵を即座に倒す
                logger.info("Debug: Kill command activated - defeating all enemies")
                for enemy in self.enemy_group.enemies:
                    enemy.current_hp = 0
                self._check_battle_result()
                return
            
            elif event.key == pygame.K_RETURN and not self.battle_active:
                if self.battle_result == "victory" and self.reward_handler:
                    # 勝利時は報酬選択画面へ
                    self.engine.register_state_handler(GameState.REWARD_SELECT, self.reward_handler)
                    self.engine.change_state(GameState.REWARD_SELECT)
                elif self.battle_result == "victory":
                    # 報酬がない場合は直接ダンジョンマップへ
                    self._return_to_dungeon_map()
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
            
            # デバッグコマンド入力処理
            elif self.debug_mode and self.battle_active:
                if event.key == pygame.K_BACKSPACE:
                    # バックスペースで文字削除
                    self.debug_input = self.debug_input[:-1]
                    return  # デバッグ入力処理後は他の処理をスキップ
                elif event.key == pygame.K_RETURN:
                    # エンターでコマンド実行
                    self._execute_debug_command(self.debug_input.lower())
                    self.debug_input = ""
                    return  # デバッグコマンド実行後は他の処理をスキップ
                elif event.unicode.isprintable() and len(self.debug_input) < 10:
                    # 文字入力
                    self.debug_input += event.unicode
                    return  # デバッグ入力中は他の処理をスキップ
        
        # ぷよぷよの操作は戦闘中のみ
        if self.battle_active:
            self.puyo_handler.handle_event(event)
    
    def _execute_debug_command(self, command: str):
        """デバッグコマンドを実行"""
        if command == "kill":
            # 全ての敵を一撃で倒す
            for enemy in self.enemy_group.enemies:
                if enemy.is_alive:
                    enemy.current_hp = 0
                    enemy.is_alive = False
                    logger.info(f"Debug: Killed {enemy.get_display_name()}")
            
            # 戦闘終了チェック
            if self.enemy_group.is_all_defeated():
                self._handle_victory()
                logger.info("Debug: All enemies killed - Victory!")
        
        elif command == "heal":
            # プレイヤーのHPを全回復
            self.battle_player.current_hp = self.battle_player.max_hp
            self.player.hp = self.player.max_hp
            logger.info("Debug: Player fully healed")
        
        elif command == "damage":
            # 敵に1000ダメージ
            target = self.enemy_group.get_selected_target()
            if target and target.is_alive:
                damage = min(1000, target.current_hp)
                target.take_damage(damage)
                logger.info(f"Debug: Dealt {damage} damage to {target.get_display_name()}")
                
                if target.current_hp <= 0:
                    target.is_alive = False
                    if self.enemy_group.is_all_defeated():
                        self._handle_victory()
        
        else:
            logger.info(f"Debug: Unknown command '{command}'. Available: kill, heal, damage")
    
    def _handle_victory(self):
        """勝利処理"""
        self.battle_result = "victory"
        self.battle_active = False
        
        # 報酬を生成
        self._generate_victory_rewards()
        
        logger.info("Victory achieved!")
    
    def render(self, surface: pygame.Surface):
        """描画処理"""
        # 美しいダンジョン背景を描画
        logger.debug("Drawing background...")
        self.background_renderer.draw_background(surface)
        
        # 上部UIバーを描画
        # プレイヤーのダメージを受けた時のフラッシュ効果
        if self.battle_player.damage_flash_timer > 0:
            self.top_ui_bar.trigger_damage_flash()
        
        logger.debug("Drawing top UI bar...")
        # 特殊ぷよの出現率データを取得
        special_puyo_rates = self.player.special_puyo_rates if hasattr(self.player, 'special_puyo_rates') else {}
        
        self.top_ui_bar.draw_top_bar(
            surface,
            self.player.hp, self.player.max_hp,
            self.player.gold,   # ゴールド
            self.floor_level,
            special_puyo_rates,  # 特殊ぷよ出現率
            self.player.inventory  # プレイヤーインベントリ
        )
        
        # ぷよぷよフィールド描画（背景の上に）
        self.puyo_handler.render(surface)
        
        # プレイヤーダメージフラッシュ
        if self.battle_player.damage_flash_timer > 0:
            flash_alpha = int(128 * (self.battle_player.damage_flash_timer / self.battle_player.damage_flash_duration))
            flash_surface = pygame.Surface((GRID_WIDTH * PUYO_SIZE, GRID_HEIGHT * PUYO_SIZE))
            flash_surface.set_alpha(flash_alpha)
            flash_surface.fill(Colors.RED)
            surface.blit(flash_surface, (GRID_OFFSET_X, GRID_OFFSET_Y))
        
        # 敵とその行動予告を描画
        self._render_enemies_with_intents(surface)
        
        # ダメージ数値描画
        self._render_damage_numbers(surface)
        
        # AOE攻撃インジケーターを表示
        self._render_aoe_indicator(surface)
        
        # カウントダウンオーバーレイ（最前面に描画）
        if self.countdown_active:
            self._render_countdown_overlay(surface)
        
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
        enemy_size = ENEMY_DISPLAY_SIZE  # スライム単体のサイズ
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
        player_stats = getattr(self.player, 'stats', None)
        total_damage = player_stats.total_damage_dealt if player_stats else 0
        
        stats = [
            f"与えたダメージ: {total_damage}",
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
        player_hp_text = font_medium.render(f"Player HP: {self.player.hp}/{self.player.max_hp}", True, Colors.WHITE)
        surface.blit(player_hp_text, (GRID_OFFSET_X, GRID_OFFSET_Y - 40))
        
        # プレイヤーHPバー
        hp_bar_width = 200
        hp_bar_height = 20
        hp_ratio = self.player.hp / self.player.max_hp
        
        # HPバー背景
        hp_bg_rect = pygame.Rect(GRID_OFFSET_X, GRID_OFFSET_Y - 20, hp_bar_width, hp_bar_height)
        pygame.draw.rect(surface, Colors.DARK_GRAY, hp_bg_rect)
        
        # HPバー
        hp_fg_rect = pygame.Rect(GRID_OFFSET_X, GRID_OFFSET_Y - 20, int(hp_bar_width * hp_ratio), hp_bar_height)
        hp_color = Colors.GREEN if hp_ratio > 0.5 else Colors.YELLOW if hp_ratio > 0.2 else Colors.RED
        pygame.draw.rect(surface, hp_color, hp_fg_rect)
        
        # プレイヤーダメージフラッシュ
        if self.battle_player.damage_flash_timer > 0:
            flash_alpha = int(128 * (self.battle_player.damage_flash_timer / self.battle_player.damage_flash_duration))
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
        
        # 統計データの安全な取得
        player_stats = getattr(self.player, 'stats', None)
        total_damage = player_stats.total_damage_dealt if player_stats else 0
        
        stats = [
            f"与えたダメージ: {total_damage}",
            f"連鎖数: {self.puyo_handler.total_chains}",
            f"現在スコア: {self.puyo_handler.total_score}",
        ]
        
        for i, stat in enumerate(stats):
            stat_font = get_appropriate_font(self.engine.fonts, stat, 'small')
            stat_text = stat_font.render(stat, True, Colors.LIGHT_GRAY)
            surface.blit(stat_text, (self.battle_ui_x, stats_y + i * 20))
    
    def _render_enemies_info(self, surface: pygame.Surface):
        """敵情報を描画"""
        logger.debug(f"Rendering {len(self.enemy_group.alive_enemies)} enemies")
        
        # 敵の配置設定
        enemy_width = 260
        enemy_height = 160
        enemy_spacing = 10
        start_x = self.battle_ui_x
        start_y = self.battle_ui_y
        
        for i, enemy in enumerate(self.enemy_group.alive_enemies):
            # 敵の表示位置 - 縦一列配置
            x = start_x
            y = start_y + i * (enemy_height + enemy_spacing)
            is_selected = (enemy == self.enemy_group.get_selected_target())
            
            # 敵情報パネルを描画
            self.ui_renderer.render_enemy_info_panel(
                surface, enemy, x, y, enemy_width, enemy_height, is_selected
            )
            
            # 行動予告を描画
            self.ui_renderer.render_enemy_action_preview(
                surface, enemy, x, y, enemy_width, enemy_height
            )
    
    def _get_all_enemy_positions(self) -> List[tuple]:
        """全敵の表示位置を取得（クリック判定用）"""
        positions = []
        enemy_size = ENEMY_DISPLAY_SIZE  # スライム単体のサイズ
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
        enemy_size = ENEMY_DISPLAY_SIZE  # スライム単体のサイズ
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
    
    def _render_aoe_indicator(self, surface: pygame.Surface):
        """AOE攻撃インジケーターを描画"""
        # 複数色の同時消去をチェック
        if hasattr(self.puyo_handler.puyo_grid, 'detect_multi_color_elimination'):
            is_aoe = self.puyo_handler.puyo_grid.detect_multi_color_elimination()
        else:
            return
        
        if is_aoe:
            # AOE攻撃可能状態を表示
            font_medium = self.engine.fonts['medium']
            aoe_text = font_medium.render("AOE READY!", True, Colors.ORANGE)
            
            # 画面右上に表示
            text_rect = aoe_text.get_rect()
            text_rect.topright = (SCREEN_WIDTH - 20, 100)
            
            # 背景
            bg_rect = text_rect.inflate(20, 10)
            pygame.draw.rect(surface, Colors.DARK_GRAY, bg_rect, border_radius=5)
            pygame.draw.rect(surface, Colors.ORANGE, bg_rect, 3, border_radius=5)
            
            surface.blit(aoe_text, text_rect)
    
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
        player_stats = getattr(self.player, 'stats', None)
        total_damage = player_stats.total_damage_dealt if player_stats else 0
        
        stats = [
            f"与えたダメージ: {total_damage}",
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
            "ESC-逃げる",
            "デバッグ: killコマンドで敵を一撃で倒す"
        ]
        
        for i, instruction in enumerate(battle_instructions):
            inst_font = get_appropriate_font(self.engine.fonts, instruction, 'small')
            inst_text = inst_font.render(instruction, True, Colors.LIGHT_GRAY)
            inst_rect = inst_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 80 + i * 20))
            surface.blit(inst_text, inst_rect)
        
        # デバッグ入力表示
        if self.debug_mode and self.debug_input:
            debug_font = get_appropriate_font(self.engine.fonts, f"Debug: {self.debug_input}", 'small')
            debug_text = debug_font.render(f"Debug: {self.debug_input}", True, Colors.YELLOW)
            debug_rect = debug_text.get_rect(bottomleft=(10, SCREEN_HEIGHT - 10))
            surface.blit(debug_text, debug_rect)
    
    def _render_countdown_overlay(self, surface: pygame.Surface):
        """バトル開始カウントダウンオーバーレイを描画"""
        # 半透明の背景オーバーレイ
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(150)
        overlay.fill(Colors.BLACK)
        surface.blit(overlay, (0, 0))
        
        # カウントダウン表示の計算
        remaining_time = self.countdown_timer
        
        if remaining_time > 2.0:
            # 3秒台: "3"
            countdown_text = "3"
            color = Colors.RED
        elif remaining_time > 1.0:
            # 2秒台: "2"
            countdown_text = "2"
            color = Colors.YELLOW
        elif remaining_time > 0.0:
            # 1秒台: "1"
            countdown_text = "1"
            color = Colors.GREEN
        else:
            # 0秒: "START"
            countdown_text = "START"
            color = Colors.WHITE
        
        # 大きなフォントでカウントダウンを描画
        font_size = 120 if countdown_text != "START" else 80
        
        # フォントを取得（大きなサイズ用）
        try:
            countdown_font = pygame.font.Font(None, font_size)
        except:
            countdown_font = self.engine.fonts['large']
        
        # テキストを描画
        text_surface = countdown_font.render(countdown_text, True, color)
        text_rect = text_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        
        # 影効果
        shadow_surface = countdown_font.render(countdown_text, True, Colors.BLACK)
        shadow_rect = shadow_surface.get_rect(center=(SCREEN_WIDTH // 2 + 3, SCREEN_HEIGHT // 2 + 3))
        surface.blit(shadow_surface, shadow_rect)
        
        # メインテキスト
        surface.blit(text_surface, text_rect)
        
        # "BATTLE START" サブテキスト
        if countdown_text == "START":
            sub_font = self.engine.fonts['medium']
            sub_text = sub_font.render("BATTLE START", True, Colors.LIGHT_GRAY)
            sub_rect = sub_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 60))
            surface.blit(sub_text, sub_rect)