"""
敵システム - ローグライクバトルの敵キャラクター
"""

import logging
import random
from typing import Dict, Optional, List
from enum import Enum
from dataclasses import dataclass

from core.constants import *

logger = logging.getLogger(__name__)


class EnemyType(Enum):
    """敵のタイプ"""
    SLIME = "slime"          # 分裂・再生能力
    GOBLIN = "goblin"        # 素早い攻撃・逃走
    ORC = "orc"              # 怒り・強力攻撃
    GOLEM = "golem"          # 防御・カウンター
    MAGE = "mage"            # バフ・魔法攻撃
    DRAGON = "dragon"        # 威嚇・火炎ブレス
    BOSS_DEMON = "boss_demon" # 多彩な能力


class EnemyAI(Enum):
    """敵のAIパターン"""
    AGGRESSIVE = "aggressive"  # 積極的攻撃
    DEFENSIVE = "defensive"    # 防御重視
    BERSERKER = "berserker"   # 狂戦士
    TACTICAL = "tactical"     # 戦術的


@dataclass
class ActionType(Enum):
    """行動の種類"""
    ATTACK = "attack"       # 通常攻撃
    GUARD = "guard"         # ガード
    SPECIAL = "special"     # 特殊行動
    HEAL = "heal"          # 回復
    BUFF = "buff"          # 強化
    DEBUFF = "debuff"      # 弱体化


@dataclass
class EnemyAction:
    """敵の行動"""
    name: str
    action_type: ActionType
    damage: int = 0
    description: str = ""
    cooldown: float = 0.0
    effect_value: int = 0    # 回復量、バフ値など
    target_type: str = "player"  # player, self, all_enemies


class Enemy:
    """敵キャラクタークラス"""
    
    def __init__(self, enemy_type: EnemyType, level: int = 1):
        self.enemy_type = enemy_type
        self.level = level
        
        # 基本ステータス
        self.max_hp = self._calculate_max_hp()
        self.current_hp = self.max_hp
        self.base_damage = self._calculate_base_damage()
        
        # 戦闘状態
        self.is_alive = True
        self.is_stunned = False
        self.stun_duration = 0.0
        self.is_guarding = False
        self.guard_reduction = 0.5  # ガード時のダメージ軽減率
        
        # バフ・デバフ
        self.buffs = {}  # {buff_type: [value, duration]}
        self.debuffs = {}  # {debuff_type: [value, duration]}
        
        # 行動パターン
        self.action_queue = []  # 予定行動のキュー
        self.action_pattern_index = 0
        self.next_action_preview = None  # 次の行動の予告
        
        # 攻撃システム
        self.attack_timer = 0.0
        self.attack_interval = self._get_attack_interval()
        self.next_action: Optional[EnemyAction] = None
        
        # AI設定
        self.ai_type = self._get_ai_type()
        self.actions = self._get_available_actions()
        self.action_patterns = self._get_action_patterns()
        
        # 位置情報（複数敵用）
        self.position_index = 0  # 敵グループ内での位置
        self.is_targeted = False  # プレイヤーのターゲットかどうか
        
        # 視覚的効果
        self.damage_flash_timer = 0.0
        self.damage_flash_duration = 0.3
        
        # 初期化時に最初の行動予告を設定
        self._update_action_preview()
        
        logger.info(f"Created {enemy_type.value} (Level {level}): {self.current_hp}/{self.max_hp} HP")
    
    def _calculate_max_hp(self) -> int:
        """最大HPを計算（新しいスケーリングシステム）"""
        # 敵タイプごとの基本HP倍率
        hp_multipliers = {
            EnemyType.SLIME: 0.8,      # 弱い敵
            EnemyType.GOBLIN: 1.0,     # 標準
            EnemyType.ORC: 1.5,        # やや強い
            EnemyType.GOLEM: 2.0,      # 硬い敵
            EnemyType.MAGE: 1.2,       # 魔法使い
            EnemyType.DRAGON: 3.0,     # 強敵
            EnemyType.BOSS_DEMON: 5.0, # ボス
        }
        
        multiplier = hp_multipliers.get(self.enemy_type, 1.0)
        base_hp = int(ENEMY_BASE_HP * multiplier)
        
        # フロアレベルによるスケーリング（新しいシステム）
        return int(base_hp * (FLOOR_SCALING_HP ** (self.level - 1)))
    
    def _calculate_base_damage(self) -> int:
        """基本ダメージを計算（新しいスケーリングシステム）"""
        # 敵タイプごとの基本ダメージ倍率
        damage_multipliers = {
            EnemyType.SLIME: 0.7,      # 弱い敵
            EnemyType.GOBLIN: 1.0,     # 標準
            EnemyType.ORC: 1.3,        # やや強い
            EnemyType.GOLEM: 0.9,      # 硬いが攻撃は控えめ
            EnemyType.MAGE: 1.1,       # 魔法使い
            EnemyType.DRAGON: 1.8,     # 強敵
            EnemyType.BOSS_DEMON: 2.5, # ボス
        }
        
        multiplier = damage_multipliers.get(self.enemy_type, 1.0)
        base_damage = int(ENEMY_ATTACK_DAMAGE * multiplier)
        
        # フロアレベルによるスケーリング（新しいシステム）
        return int(base_damage * (FLOOR_SCALING_DAMAGE ** (self.level - 1)))
    
    def _get_attack_interval(self) -> float:
        """攻撃間隔を取得（新しいスケーリングシステム）"""
        # 敵タイプごとの基本攻撃間隔倍率
        interval_multipliers = {
            EnemyType.SLIME: 1.2,      # やや遅い
            EnemyType.GOBLIN: 0.8,     # 速い
            EnemyType.ORC: 1.0,        # 標準
            EnemyType.GOLEM: 1.5,      # 遅い
            EnemyType.MAGE: 1.3,       # やや遅い
            EnemyType.DRAGON: 1.1,     # やや速い
            EnemyType.BOSS_DEMON: 0.7, # とても速い
        }
        
        multiplier = interval_multipliers.get(self.enemy_type, 1.0)
        base_interval = ENEMY_ATTACK_INTERVAL * multiplier
        
        # フロアレベルによるスケーリング（攻撃が速くなる）
        return base_interval * (FLOOR_SCALING_SPEED ** (self.level - 1))
    
    def _get_ai_type(self) -> EnemyAI:
        """AIタイプを決定"""
        ai_mapping = {
            EnemyType.SLIME: EnemyAI.AGGRESSIVE,
            EnemyType.GOBLIN: EnemyAI.TACTICAL,
            EnemyType.ORC: EnemyAI.BERSERKER,
            EnemyType.GOLEM: EnemyAI.DEFENSIVE,
            EnemyType.MAGE: EnemyAI.TACTICAL,
            EnemyType.DRAGON: EnemyAI.AGGRESSIVE,
            EnemyType.BOSS_DEMON: EnemyAI.TACTICAL,
        }
        
        return ai_mapping.get(self.enemy_type, EnemyAI.AGGRESSIVE)
    
    def _get_available_actions(self) -> List[EnemyAction]:
        """利用可能な行動を取得"""
        actions = []
        
        # 基本攻撃
        actions.append(EnemyAction(
            name="基本攻撃",
            action_type=ActionType.ATTACK,
            damage=self.base_damage,
            description=f"{self.base_damage}ダメージを与える"
        ))
        
        # ガード行動
        actions.append(EnemyAction(
            name="ガード",
            action_type=ActionType.GUARD,
            description="次のターンまでダメージを50%軽減",
            target_type="self"
        ))
        
        # 敵タイプ別の特殊能力
        if self.enemy_type == EnemyType.SLIME:
            # スライム: 分裂・再生
            actions.append(EnemyAction(
                name="分裂攻撃",
                action_type=ActionType.ATTACK,
                damage=int(self.base_damage * 0.8),
                description="分裂して攻撃"
            ))
            actions.append(EnemyAction(
                name="再生",
                action_type=ActionType.HEAL,
                effect_value=int(self.max_hp * 0.2),
                description="最大HPの20%回復",
                target_type="self"
            ))
        
        elif self.enemy_type == EnemyType.GOBLIN:
            # ゴブリン: 素早い攻撃・逃走
            actions.append(EnemyAction(
                name="素早い一撃",
                action_type=ActionType.ATTACK,
                damage=int(self.base_damage * 0.7),
                description="素早い連続攻撃"
            ))
            actions.append(EnemyAction(
                name="回避態勢",
                action_type=ActionType.BUFF,
                effect_value=30,
                description="次のダメージを30%軽減",
                target_type="self"
            ))
        
        elif self.enemy_type == EnemyType.ORC:
            # オーク: 怒り・強力攻撃
            actions.append(EnemyAction(
                name="強打",
                action_type=ActionType.SPECIAL,
                damage=int(self.base_damage * 1.6),
                description="強力な一撃"
            ))
            actions.append(EnemyAction(
                name="怒り",
                action_type=ActionType.BUFF,
                effect_value=40,
                description="攻撃力40%アップ",
                target_type="self"
            ))
        
        elif self.enemy_type == EnemyType.GOLEM:
            # ゴーレム: 防御・カウンター
            actions.append(EnemyAction(
                name="岩石投げ",
                action_type=ActionType.ATTACK,
                damage=int(self.base_damage * 1.3),
                description="重い岩を投げつける"
            ))
            actions.append(EnemyAction(
                name="鉄壁の守り",
                action_type=ActionType.BUFF,
                effect_value=50,
                description="大幅にダメージ軽減",
                target_type="self"
            ))
        
        elif self.enemy_type == EnemyType.MAGE:
            # 魔導士: バフ・魔法攻撃
            actions.append(EnemyAction(
                name="魔法の矢",
                action_type=ActionType.SPECIAL,
                damage=int(self.base_damage * 1.2),
                description="魔法による貫通攻撃"
            ))
            actions.append(EnemyAction(
                name="魔力増幅",
                action_type=ActionType.BUFF,
                effect_value=30,
                description="魔法攻撃力増加",
                target_type="self"
            ))
            actions.append(EnemyAction(
                name="シールド",
                action_type=ActionType.BUFF,
                effect_value=35,
                description="魔法の盾を展開",
                target_type="self"
            ))
        
        elif self.enemy_type == EnemyType.DRAGON:
            # ドラゴン: 威嚇・火炎ブレス
            actions.append(EnemyAction(
                name="火炎ブレス",
                action_type=ActionType.SPECIAL,
                damage=int(self.base_damage * 1.4),
                description="強力な炎の攻撃"
            ))
            actions.append(EnemyAction(
                name="威嚇",
                action_type=ActionType.DEBUFF,
                effect_value=25,
                description="プレイヤーを威嚇"
            ))
            actions.append(EnemyAction(
                name="竜の怒り",
                action_type=ActionType.BUFF,
                effect_value=50,
                description="ドラゴンが激怒状態に",
                target_type="self"
            ))
        
        elif self.enemy_type == EnemyType.BOSS_DEMON:
            # ボス魔王: 多彩な能力
            actions.append(EnemyAction(
                name="魔力弾",
                action_type=ActionType.SPECIAL,
                damage=int(self.base_damage * 1.3),
                description="強力な魔法攻撃"
            ))
            actions.append(EnemyAction(
                name="地獄の炎",
                action_type=ActionType.SPECIAL,
                damage=int(self.base_damage * 1.8),
                description="灼熱の地獄の炎"
            ))
            actions.append(EnemyAction(
                name="ダークヒール",
                action_type=ActionType.HEAL,
                effect_value=int(self.max_hp * 0.25),
                description="闇の力で大回復",
                target_type="self"
            ))
            actions.append(EnemyAction(
                name="魔王の威光",
                action_type=ActionType.DEBUFF,
                effect_value=40,
                description="プレイヤーを大幅弱体化"
            ))
        
        return actions
    
    def _get_action_patterns(self) -> List[List[str]]:
        """行動パターンを取得"""
        patterns = {
            EnemyType.SLIME: [
                ["基本攻撃", "分裂攻撃", "再生"],
                ["基本攻撃", "基本攻撃", "ガード"],
            ],
            EnemyType.GOBLIN: [
                ["素早い一撃", "基本攻撃", "回避態勢"],
                ["基本攻撃", "素早い一撃", "ガード"],
            ],
            EnemyType.ORC: [
                ["基本攻撃", "強打", "ガード"],
                ["怒り", "基本攻撃", "強打"],
            ],
            EnemyType.GOLEM: [
                ["ガード", "岩石投げ", "鉄壁の守り"],
                ["基本攻撃", "ガード", "岩石投げ"],
            ],
            EnemyType.MAGE: [
                ["魔力増幅", "魔法の矢", "シールド"],
                ["基本攻撃", "魔法の矢", "ガード"],
            ],
            EnemyType.DRAGON: [
                ["威嚇", "火炎ブレス", "ガード"],
                ["基本攻撃", "竜の怒り", "火炎ブレス"],
            ],
            EnemyType.BOSS_DEMON: [
                ["基本攻撃", "魔力弾", "ガード"],
                ["地獄の炎", "ダークヒール", "基本攻撃"],
                ["魔王の威光", "魔力弾", "地獄の炎"],
            ],
        }
        
        return patterns.get(self.enemy_type, [["基本攻撃", "ガード"]])
    
    def update(self, dt: float, player_hp: int) -> Optional[EnemyAction]:
        """敵の更新処理"""
        if not self.is_alive:
            return None
        
        # スタン処理
        if self.is_stunned:
            self.stun_duration -= dt
            if self.stun_duration <= 0:
                self.is_stunned = False
                logger.debug(f"{self.enemy_type.value} recovered from stun")
        
        # ダメージフラッシュ
        if self.damage_flash_timer > 0:
            self.damage_flash_timer -= dt
        
        # バフ・デバフの更新
        self._update_effects(dt)
        
        # ガード状態の更新
        self.is_guarding = False  # 毎フレームリセット
        
        # 攻撃タイマー
        if not self.is_stunned:
            self.attack_timer += dt
            
            if self.attack_timer >= self.attack_interval:
                action = self._get_next_pattern_action()
                self.attack_timer = 0.0
                # 次の行動予告を更新
                self._update_action_preview()
                return action
        
        return None
    
    def _update_effects(self, dt: float):
        """バフ・デバフ効果を更新"""
        # バフの更新
        for buff_type in list(self.buffs.keys()):
            self.buffs[buff_type][1] -= dt
            if self.buffs[buff_type][1] <= 0:
                del self.buffs[buff_type]
        
        # デバフの更新
        for debuff_type in list(self.debuffs.keys()):
            self.debuffs[debuff_type][1] -= dt
            if self.debuffs[debuff_type][1] <= 0:
                del self.debuffs[debuff_type]
    
    def _get_next_pattern_action(self) -> EnemyAction:
        """パターンに基づいて次の行動を取得"""
        if not self.action_patterns:
            return self._decide_action(0)  # フォールバック
        
        # 現在のパターンを取得
        current_pattern = random.choice(self.action_patterns)
        action_name = current_pattern[self.action_pattern_index % len(current_pattern)]
        
        # パターンインデックスを進める
        self.action_pattern_index += 1
        
        # 行動名から実際の行動を取得
        for action in self.actions:
            if action.name == action_name:
                return action
        
        # 見つからない場合は基本攻撃
        return self.actions[0]
    
    def _update_action_preview(self):
        """次の行動予告を更新"""
        if not self.action_patterns:
            self.next_action_preview = self.actions[0] if self.actions else None
            return
        
        # 現在のパターンから次の行動を取得
        current_pattern = random.choice(self.action_patterns)
        next_action_name = current_pattern[self.action_pattern_index % len(current_pattern)]
        
        # 行動名から実際の行動を取得
        for action in self.actions:
            if action.name == next_action_name:
                self.next_action_preview = action
                return
        
        # 見つからない場合は基本攻撃
        self.next_action_preview = self.actions[0] if self.actions else None
    
    def _decide_action(self, player_hp: int) -> EnemyAction:
        """行動を決定"""
        available_actions = [action for action in self.actions]
        
        # AIタイプによる行動選択
        if self.ai_type == EnemyAI.AGGRESSIVE:
            # 常に最大ダメージを狙う
            return max(available_actions, key=lambda a: a.damage)
        
        elif self.ai_type == EnemyAI.BERSERKER:
            # HPが低いほど強い攻撃を使う
            hp_ratio = self.current_hp / self.max_hp
            if hp_ratio < 0.3:
                # 瀕死時は最強攻撃
                return max(available_actions, key=lambda a: a.damage)
            else:
                # 通常時はランダム
                return random.choice(available_actions)
        
        elif self.ai_type == EnemyAI.TACTICAL:
            # プレイヤーのHPに応じて戦術を変更
            if player_hp < 30:
                # プレイヤーが弱っている時は積極的
                return max(available_actions, key=lambda a: a.damage)
            else:
                # 通常時はバランス良く
                return random.choice(available_actions)
        
        else:  # DEFENSIVE
            # 基本攻撃を多用
            basic_attacks = [a for a in available_actions if "基本" in a.name]
            if basic_attacks:
                return random.choice(basic_attacks)
            return random.choice(available_actions)
    
    def take_damage(self, damage: int) -> bool:
        """ダメージを受ける"""
        if not self.is_alive:
            return False
        
        # ガード時のダメージ軽減
        final_damage = damage
        if self.is_guarding:
            final_damage = int(damage * (1 - self.guard_reduction))
            logger.info(f"{self.enemy_type.value} guarded! {damage} -> {final_damage}")
        
        # バフ・デバフによるダメージ修正
        if "defense_buff" in self.buffs:
            reduction = self.buffs["defense_buff"][0] / 100
            final_damage = int(final_damage * (1 - reduction))
        
        self.current_hp -= final_damage
        self.damage_flash_timer = self.damage_flash_duration
        
        logger.info(f"{self.enemy_type.value} took {final_damage} damage ({self.current_hp}/{self.max_hp})")
        
        if self.current_hp <= 0:
            self.current_hp = 0
            self.is_alive = False
            logger.info(f"{self.enemy_type.value} defeated!")
            return True  # 敵が倒された
        
        return False
    
    def apply_stun(self, duration: float):
        """スタンを適用"""
        self.is_stunned = True
        self.stun_duration = max(self.stun_duration, duration)
        logger.debug(f"{self.enemy_type.value} stunned for {duration}s")
    
    def apply_buff(self, buff_type: str, value: int, duration: float):
        """バフを適用"""
        self.buffs[buff_type] = [value, duration]
        logger.debug(f"{self.enemy_type.value} received buff: {buff_type} (+{value}) for {duration}s")
    
    def apply_debuff(self, debuff_type: str, value: int, duration: float):
        """デバフを適用"""
        self.debuffs[debuff_type] = [value, duration]
        logger.debug(f"{self.enemy_type.value} received debuff: {debuff_type} (-{value}) for {duration}s")
    
    def heal(self, amount: int):
        """回復"""
        if not self.is_alive:
            return
        
        old_hp = self.current_hp
        self.current_hp = min(self.max_hp, self.current_hp + amount)
        healed = self.current_hp - old_hp
        
        if healed > 0:
            logger.info(f"{self.enemy_type.value} healed {healed} HP ({self.current_hp}/{self.max_hp})")
    
    def execute_action(self, action: EnemyAction, target=None):
        """行動を実行"""
        if action.action_type == ActionType.GUARD:
            self.is_guarding = True
        elif action.action_type == ActionType.HEAL:
            self.heal(action.effect_value)
        elif action.action_type == ActionType.BUFF:
            self.apply_buff("attack_buff", action.effect_value, 10.0)
        elif action.action_type == ActionType.DEBUFF and target:
            target.apply_debuff("attack_debuff", action.effect_value, 8.0)
    
    def get_display_name(self) -> str:
        """表示名を取得"""
        names = {
            EnemyType.SLIME: "スライム",
            EnemyType.GOBLIN: "ゴブリン",
            EnemyType.ORC: "オーク",
            EnemyType.GOLEM: "ゴーレム",
            EnemyType.MAGE: "魔導士",
            EnemyType.DRAGON: "ドラゴン",
            EnemyType.BOSS_DEMON: "魔王",
        }
        
        name = names.get(self.enemy_type, "敵")
        return f"{name} Lv.{self.level}"
    
    def get_status_color(self) -> tuple:
        """ステータスに応じた色を取得"""
        if not self.is_alive:
            return Colors.GRAY
        elif self.is_stunned:
            return Colors.CYAN
        elif self.is_guarding:
            return Colors.BLUE
        elif self.damage_flash_timer > 0:
            return Colors.RED
        elif "attack_buff" in self.buffs:
            return Colors.ORANGE
        else:
            hp_ratio = self.current_hp / self.max_hp
            if hp_ratio > 0.7:
                return Colors.GREEN
            elif hp_ratio > 0.3:
                return Colors.YELLOW
            else:
                return Colors.RED
    
    def get_status_text(self) -> List[str]:
        """状態テキストを取得"""
        status = []
        
        if self.is_stunned:
            status.append(f"スタン ({self.stun_duration:.1f}s)")
        if self.is_guarding:
            status.append("ガード中")
        if "attack_buff" in self.buffs:
            value, duration = self.buffs["attack_buff"]
            status.append(f"攻撃力+{value}% ({duration:.1f}s)")
        if "defense_buff" in self.buffs:
            value, duration = self.buffs["defense_buff"]
            status.append(f"防御+{value}% ({duration:.1f}s)")
        
        return status
    
    def get_action_icon(self, action: EnemyAction) -> str:
        """行動のアイコンを取得"""
        if action.action_type == ActionType.ATTACK:
            return "A"
        elif action.action_type == ActionType.SPECIAL:
            return "S"
        elif action.action_type == ActionType.GUARD:
            return "G"
        elif action.action_type == ActionType.HEAL:
            return "H"
        elif action.action_type == ActionType.BUFF:
            return "B"
        elif action.action_type == ActionType.DEBUFF:
            return "D"
        else:
            return "?"
    
    def get_next_action_info(self) -> dict:
        """次の行動の詳細情報を取得"""
        if not self.next_action_preview:
            return {}
        
        action = self.next_action_preview
        info = {
            'name': action.name,
            'icon': self.get_action_icon(action),
            'description': action.description,
            'type': action.action_type,  # ActionType列挙型のまま渡す
        }
        
        if action.action_type == ActionType.ATTACK or action.action_type == ActionType.SPECIAL:
            # バフによるダメージ計算
            damage = action.damage
            if "attack_buff" in self.buffs:
                boost = self.buffs["attack_buff"][0] / 100
                damage = int(damage * (1 + boost))
            info['damage'] = damage
        
        elif action.action_type == ActionType.HEAL:
            info['heal_amount'] = action.effect_value
        
        elif action.action_type == ActionType.BUFF or action.action_type == ActionType.DEBUFF:
            info['effect_value'] = action.effect_value
        
        return info


def create_random_enemy(floor_level: int) -> Enemy:
    """フロアレベルに応じたランダムな敵を生成"""
    if floor_level <= 2:
        enemy_types = [EnemyType.SLIME, EnemyType.GOBLIN]
    elif floor_level <= 4:
        enemy_types = [EnemyType.GOBLIN, EnemyType.ORC, EnemyType.GOLEM]
    elif floor_level <= 6:
        enemy_types = [EnemyType.ORC, EnemyType.GOLEM, EnemyType.MAGE]
    elif floor_level <= 8:
        enemy_types = [EnemyType.GOLEM, EnemyType.MAGE, EnemyType.DRAGON]
    else:
        enemy_types = [EnemyType.DRAGON, EnemyType.BOSS_DEMON]
    
    enemy_type = random.choice(enemy_types)
    
    # ボスフロア（5の倍数）ではボス敵を強制
    if floor_level % 5 == 0:
        if floor_level <= 5:
            enemy_type = EnemyType.ORC
        elif floor_level <= 10:
            enemy_type = EnemyType.DRAGON
        else:
            enemy_type = EnemyType.BOSS_DEMON
    
    # レベルはフロアレベル±1
    enemy_level = max(1, floor_level + random.randint(-1, 1))
    
    return Enemy(enemy_type, enemy_level)


def create_enemy_group(floor_level: int) -> List[Enemy]:
    """フロアレベルに応じた敵グループを生成（1〜3体）"""
    # 敵の数を決定
    if floor_level <= 2:
        enemy_count = random.choices([1, 2], weights=[0.8, 0.2])[0]
    elif floor_level <= 5:
        enemy_count = random.choices([1, 2, 3], weights=[0.5, 0.4, 0.1])[0]
    else:
        enemy_count = random.choices([1, 2, 3], weights=[0.3, 0.5, 0.2])[0]
    
    enemies = []
    
    # ボスフロアは単体
    if floor_level % 5 == 0:
        enemy_count = 1
    
    for i in range(enemy_count):
        enemy = create_random_enemy(floor_level)
        enemy.position_index = i
        enemies.append(enemy)
    
    # 複数敵の場合は少し弱くする
    if len(enemies) > 1:
        for enemy in enemies:
            enemy.max_hp = int(enemy.max_hp * 0.8)
            enemy.current_hp = enemy.max_hp
            enemy.base_damage = int(enemy.base_damage * 0.9)
    
    logger.info(f"Created enemy group with {len(enemies)} enemies for floor {floor_level}")
    return enemies


class EnemyGroup:
    """敵グループ管理クラス"""
    
    def __init__(self, enemies: List[Enemy]):
        self.enemies = enemies
        self.alive_enemies = enemies.copy()
        self.selected_target_index = 0  # プレイヤーが選択している攻撃対象
        
        logger.info(f"EnemyGroup created with {len(enemies)} enemies")
    
    def update(self, dt: float, player_hp: int) -> List[EnemyAction]:
        """グループ全体の更新処理"""
        actions = []
        
        # 生存敵のリストを更新
        self.alive_enemies = [e for e in self.enemies if e.is_alive]
        
        # 選択対象が死んでいる場合は次の敵に変更
        if self.selected_target_index >= len(self.alive_enemies):
            self.selected_target_index = 0
        
        # 各敵の更新
        for enemy in self.alive_enemies:
            action = enemy.update(dt, player_hp)
            if action:
                actions.append((enemy, action))
        
        return actions
    
    def get_selected_target(self) -> Optional[Enemy]:
        """選択中のターゲットを取得"""
        if 0 <= self.selected_target_index < len(self.alive_enemies):
            return self.alive_enemies[self.selected_target_index]
        return None
    
    def select_next_target(self):
        """次の敵をターゲット"""
        if len(self.alive_enemies) > 1:
            self.selected_target_index = (self.selected_target_index + 1) % len(self.alive_enemies)
    
    def select_previous_target(self):
        """前の敵をターゲット"""
        if len(self.alive_enemies) > 1:
            self.selected_target_index = (self.selected_target_index - 1) % len(self.alive_enemies)
    
    def select_target_by_click(self, click_x: int, click_y: int, enemy_positions: List[tuple]) -> bool:
        """クリック位置で敵をターゲット選択"""
        for i, (x, y, width, height) in enumerate(enemy_positions):
            if x <= click_x <= x + width and y <= click_y <= y + height:
                if i < len(self.alive_enemies):
                    self.selected_target_index = i
                    logger.info(f"Target selected by click: {self.alive_enemies[i].get_display_name()}")
                    return True
        return False
    
    def is_all_defeated(self) -> bool:
        """全敵が倒されたかチェック"""
        return len(self.alive_enemies) == 0
    
    def get_enemy_count(self) -> int:
        """生存敵数を取得"""
        return len(self.alive_enemies)