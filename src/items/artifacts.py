"""
装飾品（アーティファクト）システム - Slay the Spire風の永続装備品
"""

import logging
import random
from typing import Dict, List, Optional, Set
from enum import Enum
from dataclasses import dataclass

from core.constants import *

logger = logging.getLogger(__name__)


class ArtifactType(Enum):
    """装飾品の種類"""
    # 戦闘関連
    POWER_RING = "power_ring"              # 攻撃力アップ
    DEFENSE_AMULET = "defense_amulet"      # 防御力アップ
    VAMPIRE_FANG = "vampire_fang"          # ダメージ吸収
    BERSERKER_MASK = "berserker_mask"      # 低HP時パワーアップ
    
    # ぷよぷよ関連
    SPEED_BOOTS = "speed_boots"            # ぷよ落下速度アップ
    CHAIN_CROWN = "chain_crown"            # 連鎖ダメージアップ
    COLOR_LENS = "color_lens"              # ぷよ色数減少
    LUCKY_CHARM = "lucky_charm"            # 特殊ぷよ出現率アップ
    RAINBOW_CRYSTAL = "rainbow_crystal"    # 虹ぷよ定期生成
    
    # ユーティリティ関連
    HEALING_PENDANT = "healing_pendant"    # 戦闘後回復
    ENERGY_CRYSTAL = "energy_crystal"      # エネルギー上限アップ
    POTION_BELT = "potion_belt"            # ポーション所持数アップ
    TREASURE_MAP = "treasure_map"          # 報酬増加
    
    # 特殊効果
    PHOENIX_FEATHER = "phoenix_feather"    # 死亡時復活
    TIME_SHARD = "time_shard"              # 敵行動遅延
    CURSE_SHIELD = "curse_shield"          # デバフ無効化
    DOUBLE_STRIKE = "double_strike"        # 連鎖が2回発動


@dataclass
class ArtifactEffect:
    """装飾品効果の定義"""
    effect_type: str                       # 効果の種類
    value: float                           # 効果値
    trigger: str = "passive"               # 発動条件（passive, battle_start, chain, etc）
    description: str = ""                  # 効果の説明


class Artifact:
    """装飾品クラス"""
    
    def __init__(self, artifact_type: ArtifactType, rarity: Rarity = Rarity.UNCOMMON):
        self.artifact_type = artifact_type
        self.rarity = rarity
        self.name = self._get_name()
        self.description = self._get_description()
        self.effects = self._get_effects()
        self.equipped = False
        
        # 内部状態
        self.charges = self._get_max_charges()
        self.max_charges = self.charges
        self.cooldown = 0.0
        self.active = True
        
        # 視覚効果
        self.color = self._get_color()
        self.icon = self._get_icon()
        
        logger.debug(f"Created artifact: {self.name}")
    
    def _get_name(self) -> str:
        """装飾品名を取得"""
        names = {
            ArtifactType.POWER_RING: "力の指輪",
            ArtifactType.DEFENSE_AMULET: "守りのお守り",
            ArtifactType.VAMPIRE_FANG: "吸血鬼の牙",
            ArtifactType.BERSERKER_MASK: "狂戦士の仮面",
            ArtifactType.SPEED_BOOTS: "俊足のブーツ",
            ArtifactType.CHAIN_CROWN: "連鎖の王冠",
            ArtifactType.COLOR_LENS: "色彩のレンズ",
            ArtifactType.LUCKY_CHARM: "幸運のお守り",
            ArtifactType.RAINBOW_CRYSTAL: "虹色の水晶",
            ArtifactType.HEALING_PENDANT: "癒しのペンダント",
            ArtifactType.ENERGY_CRYSTAL: "エネルギークリスタル",
            ArtifactType.POTION_BELT: "ポーションベルト",
            ArtifactType.TREASURE_MAP: "宝の地図",
            ArtifactType.PHOENIX_FEATHER: "不死鳥の羽根",
            ArtifactType.TIME_SHARD: "時の欠片",
            ArtifactType.CURSE_SHIELD: "呪い除けの盾",
            ArtifactType.DOUBLE_STRIKE: "二重撃の腕輪",
        }
        
        base_name = names.get(self.artifact_type, "不明な装飾品")
        
        # レアリティに応じた接頭辞
        if self.rarity == Rarity.RARE:
            return f"高級{base_name}"
        elif self.rarity == Rarity.EPIC:
            return f"伝説の{base_name}"
        elif self.rarity == Rarity.LEGENDARY:
            return f"神話の{base_name}"
        
        return base_name
    
    def _get_description(self) -> str:
        """装飾品の説明を取得"""
        descriptions = {
            ArtifactType.POWER_RING: "全てのダメージが増加する",
            ArtifactType.DEFENSE_AMULET: "受けるダメージが減少する",
            ArtifactType.VAMPIRE_FANG: "与えたダメージの一部でHP回復",
            ArtifactType.BERSERKER_MASK: "HPが低いほど攻撃力が上昇",
            ArtifactType.SPEED_BOOTS: "ぷよの落下速度が上昇",
            ArtifactType.CHAIN_CROWN: "連鎖によるダメージが増加",
            ArtifactType.COLOR_LENS: "ぷよの色数が減少",
            ArtifactType.LUCKY_CHARM: "特殊ぷよの出現率が上昇",
            ArtifactType.RAINBOW_CRYSTAL: "定期的に虹ぷよが出現",
            ArtifactType.HEALING_PENDANT: "戦闘勝利時にHP回復",
            ArtifactType.ENERGY_CRYSTAL: "エネルギー上限が増加",
            ArtifactType.POTION_BELT: "ポーション所持数が増加",
            ArtifactType.TREASURE_MAP: "戦闘報酬が増加",
            ArtifactType.PHOENIX_FEATHER: "死亡時に一度だけ復活",
            ArtifactType.TIME_SHARD: "敵の行動間隔が延長",
            ArtifactType.CURSE_SHIELD: "デバフ効果を無効化",
            ArtifactType.DOUBLE_STRIKE: "連鎖が2回発動する",
        }
        
        return descriptions.get(self.artifact_type, "不明な効果")
    
    def _get_effects(self) -> List[ArtifactEffect]:
        """装飾品効果を取得"""
        # レアリティによる効果倍率
        rarity_multiplier = {
            Rarity.UNCOMMON: 1.0,
            Rarity.RARE: 1.4,
            Rarity.EPIC: 1.8,
            Rarity.LEGENDARY: 2.5,
        }.get(self.rarity, 1.0)
        
        base_effects = {
            ArtifactType.POWER_RING: [
                ArtifactEffect(
                    effect_type="damage_boost",
                    value=15 * rarity_multiplier,
                    trigger="passive",
                    description=f"全ダメージ+{int(15 * rarity_multiplier)}%"
                )
            ],
            ArtifactType.DEFENSE_AMULET: [
                ArtifactEffect(
                    effect_type="damage_reduction",
                    value=12 * rarity_multiplier,
                    trigger="passive",
                    description=f"被ダメージ-{int(12 * rarity_multiplier)}%"
                )
            ],
            ArtifactType.VAMPIRE_FANG: [
                ArtifactEffect(
                    effect_type="lifesteal",
                    value=20 * rarity_multiplier,
                    trigger="on_damage",
                    description=f"与ダメージの{int(20 * rarity_multiplier)}%でHP回復"
                )
            ],
            ArtifactType.BERSERKER_MASK: [
                ArtifactEffect(
                    effect_type="low_hp_damage_boost",
                    value=2 * rarity_multiplier,
                    trigger="passive",
                    description=f"HP1%毎にダメージ+{rarity_multiplier:.1f}%"
                )
            ],
            ArtifactType.SPEED_BOOTS: [
                ArtifactEffect(
                    effect_type="puyo_speed_boost",
                    value=30 * rarity_multiplier,
                    trigger="passive",
                    description=f"ぷよ速度+{int(30 * rarity_multiplier)}%"
                )
            ],
            ArtifactType.CHAIN_CROWN: [
                ArtifactEffect(
                    effect_type="chain_damage_boost",
                    value=25 * rarity_multiplier,
                    trigger="passive",
                    description=f"連鎖ダメージ+{int(25 * rarity_multiplier)}%"
                )
            ],
            ArtifactType.COLOR_LENS: [
                ArtifactEffect(
                    effect_type="color_reduction",
                    value=1 if rarity_multiplier < 2.0 else 2,
                    trigger="passive",
                    description=f"ぷよ色数-{int(1 if rarity_multiplier < 2.0 else 2)}"
                )
            ],
            ArtifactType.LUCKY_CHARM: [
                ArtifactEffect(
                    effect_type="special_puyo_rate_boost",
                    value=100 * rarity_multiplier,
                    trigger="passive",
                    description=f"特殊ぷよ出現率+{int(100 * rarity_multiplier)}%"
                )
            ],
            ArtifactType.RAINBOW_CRYSTAL: [
                ArtifactEffect(
                    effect_type="rainbow_puyo_spawn",
                    value=1,
                    trigger="periodic",
                    description="20秒毎に虹ぷよ生成"
                )
            ],
            ArtifactType.HEALING_PENDANT: [
                ArtifactEffect(
                    effect_type="battle_victory_heal",
                    value=20 * rarity_multiplier,
                    trigger="battle_end",
                    description=f"戦闘勝利時HP+{int(20 * rarity_multiplier)}"
                )
            ],
            ArtifactType.ENERGY_CRYSTAL: [
                ArtifactEffect(
                    effect_type="max_energy_boost",
                    value=1 + int(rarity_multiplier / 2),
                    trigger="passive",
                    description=f"エネルギー上限+{int(1 + rarity_multiplier / 2)}"
                )
            ],
            ArtifactType.POTION_BELT: [
                ArtifactEffect(
                    effect_type="potion_capacity_boost",
                    value=1 + int(rarity_multiplier / 2),
                    trigger="passive",
                    description=f"ポーション所持数+{int(1 + rarity_multiplier / 2)}"
                )
            ],
            ArtifactType.TREASURE_MAP: [
                ArtifactEffect(
                    effect_type="reward_boost",
                    value=30 * rarity_multiplier,
                    trigger="passive",
                    description=f"報酬+{int(30 * rarity_multiplier)}%"
                )
            ],
            ArtifactType.PHOENIX_FEATHER: [
                ArtifactEffect(
                    effect_type="revive",
                    value=50 * rarity_multiplier,
                    trigger="on_death",
                    description=f"死亡時{int(50 * rarity_multiplier)}%HPで復活"
                )
            ],
            ArtifactType.TIME_SHARD: [
                ArtifactEffect(
                    effect_type="enemy_speed_reduction",
                    value=20 * rarity_multiplier,
                    trigger="passive",
                    description=f"敵行動速度-{int(20 * rarity_multiplier)}%"
                )
            ],
            ArtifactType.CURSE_SHIELD: [
                ArtifactEffect(
                    effect_type="debuff_immunity",
                    value=int(2 * rarity_multiplier),
                    trigger="on_debuff",
                    description=f"{int(2 * rarity_multiplier)}回デバフ無効"
                )
            ],
            ArtifactType.DOUBLE_STRIKE: [
                ArtifactEffect(
                    effect_type="chain_double_trigger",
                    value=1,
                    trigger="on_chain",
                    description="連鎖が2回発動"
                )
            ],
        }
        
        return base_effects.get(self.artifact_type, [])
    
    def _get_max_charges(self) -> int:
        """最大チャージ数を取得"""
        charge_based = {
            ArtifactType.PHOENIX_FEATHER: 1,
            ArtifactType.CURSE_SHIELD: int(2 * (1 + self.rarity.value * 0.5)),
        }
        
        return charge_based.get(self.artifact_type, 0)
    
    def _get_color(self) -> tuple:
        """装飾品の色を取得"""
        colors = {
            ArtifactType.POWER_RING: Colors.RED,
            ArtifactType.DEFENSE_AMULET: Colors.BLUE,
            ArtifactType.VAMPIRE_FANG: Colors.DARK_GRAY,
            ArtifactType.BERSERKER_MASK: Colors.ORANGE,
            ArtifactType.SPEED_BOOTS: Colors.GREEN,
            ArtifactType.CHAIN_CROWN: Colors.YELLOW,
            ArtifactType.COLOR_LENS: Colors.PURPLE,
            ArtifactType.LUCKY_CHARM: Colors.WHITE,
            ArtifactType.RAINBOW_CRYSTAL: Colors.CYAN,
            ArtifactType.HEALING_PENDANT: Colors.GREEN,
            ArtifactType.ENERGY_CRYSTAL: Colors.YELLOW,
            ArtifactType.POTION_BELT: Colors.ORANGE,
            ArtifactType.TREASURE_MAP: Colors.YELLOW,
            ArtifactType.PHOENIX_FEATHER: Colors.RED,
            ArtifactType.TIME_SHARD: Colors.CYAN,
            ArtifactType.CURSE_SHIELD: Colors.WHITE,
            ArtifactType.DOUBLE_STRIKE: Colors.PURPLE,
        }
        
        return colors.get(self.artifact_type, Colors.GRAY)
    
    def _get_icon(self) -> str:
        """装飾品のアイコンを取得"""
        icons = {
            ArtifactType.POWER_RING: "💍",
            ArtifactType.DEFENSE_AMULET: "🔮",
            ArtifactType.VAMPIRE_FANG: "🧛",
            ArtifactType.BERSERKER_MASK: "😡",
            ArtifactType.SPEED_BOOTS: "👢",
            ArtifactType.CHAIN_CROWN: "👑",
            ArtifactType.COLOR_LENS: "🔍",
            ArtifactType.LUCKY_CHARM: "🍀",
            ArtifactType.RAINBOW_CRYSTAL: "💎",
            ArtifactType.HEALING_PENDANT: "❤",
            ArtifactType.ENERGY_CRYSTAL: "⚡",
            ArtifactType.POTION_BELT: "🎒",
            ArtifactType.TREASURE_MAP: "🗺",
            ArtifactType.PHOENIX_FEATHER: "🪶",
            ArtifactType.TIME_SHARD: "⏳",
            ArtifactType.CURSE_SHIELD: "🛡",
            ArtifactType.DOUBLE_STRIKE: "⚔",
        }
        
        return icons.get(self.artifact_type, "🔧")
    
    def trigger_effect(self, trigger_type: str, context: Dict = None) -> List[Dict]:
        """効果を発動"""
        if not self.active:
            return []
        
        triggered_effects = []
        
        for effect in self.effects:
            if effect.trigger == trigger_type or effect.trigger == "passive":
                # チャージ系アーティファクトの処理
                if self.max_charges > 0:
                    if self.charges <= 0:
                        continue
                    self.charges -= 1
                    if self.charges <= 0:
                        self.active = False
                
                effect_result = {
                    'type': effect.effect_type,
                    'value': effect.value,
                    'description': effect.description,
                    'artifact_name': self.name
                }
                
                triggered_effects.append(effect_result)
                logger.info(f"Triggered artifact effect: {self.name} - {effect.description}")
        
        return triggered_effects
    
    def get_rarity_color(self) -> tuple:
        """レアリティ色を取得"""
        return RARITY_COLORS.get(self.rarity, Colors.WHITE)
    
    def is_consumable(self) -> bool:
        """消耗品かどうか"""
        return self.max_charges > 0
    
    def get_status_text(self) -> str:
        """状態テキストを取得"""
        if not self.active:
            return "（使用済み）"
        elif self.max_charges > 0:
            return f"（{self.charges}/{self.max_charges}）"
        else:
            return ""


class ArtifactCollection:
    """装飾品コレクション"""
    
    def __init__(self, max_artifacts: int = 10):
        self.max_artifacts = max_artifacts
        self.artifacts: List[Artifact] = []
        
        logger.info(f"ArtifactCollection initialized (max: {max_artifacts})")
    
    def add_artifact(self, artifact: Artifact) -> bool:
        """装飾品を追加"""
        if len(self.artifacts) >= self.max_artifacts:
            logger.warning("Artifact collection is full")
            return False
        
        # 同じタイプの装飾品は重複不可（レアリティが高い方を優先）
        existing = self.find_artifact_by_type(artifact.artifact_type)
        if existing:
            if artifact.rarity.value > existing.rarity.value:
                self.artifacts.remove(existing)
                self.artifacts.append(artifact)
                logger.info(f"Upgraded artifact: {existing.name} -> {artifact.name}")
                return True
            else:
                logger.info(f"Artifact already exists with higher rarity: {existing.name}")
                return False
        
        self.artifacts.append(artifact)
        artifact.equipped = True
        logger.info(f"Added artifact: {artifact.name}")
        return True
    
    def remove_artifact(self, artifact: Artifact) -> bool:
        """装飾品を削除"""
        if artifact in self.artifacts:
            self.artifacts.remove(artifact)
            artifact.equipped = False
            logger.info(f"Removed artifact: {artifact.name}")
            return True
        return False
    
    def find_artifact_by_type(self, artifact_type: ArtifactType) -> Optional[Artifact]:
        """タイプで装飾品を検索"""
        for artifact in self.artifacts:
            if artifact.artifact_type == artifact_type:
                return artifact
        return None
    
    def get_active_artifacts(self) -> List[Artifact]:
        """アクティブな装飾品を取得"""
        return [a for a in self.artifacts if a.active]
    
    def trigger_effects(self, trigger_type: str, context: Dict = None) -> List[Dict]:
        """条件に合う効果を発動"""
        all_effects = []
        
        for artifact in self.get_active_artifacts():
            effects = artifact.trigger_effect(trigger_type, context)
            all_effects.extend(effects)
        
        return all_effects
    
    def get_passive_bonuses(self) -> Dict[str, float]:
        """パッシブボーナスの合計を取得"""
        bonuses = {}
        
        for artifact in self.get_active_artifacts():
            for effect in artifact.effects:
                if effect.trigger == "passive":
                    if effect.effect_type in bonuses:
                        bonuses[effect.effect_type] += effect.value
                    else:
                        bonuses[effect.effect_type] = effect.value
        
        return bonuses
    
    def get_artifact_count(self) -> int:
        """装飾品数を取得"""
        return len(self.artifacts)
    
    def is_full(self) -> bool:
        """コレクションが満杯かチェック"""
        return len(self.artifacts) >= self.max_artifacts


def create_random_artifact(floor_level: int = 1) -> Artifact:
    """フロアレベルに応じたランダム装飾品を生成"""
    # フロアレベルに応じたレアリティ重み
    if floor_level <= 3:
        rarity_weights = {
            Rarity.UNCOMMON: 0.8,
            Rarity.RARE: 0.2,
        }
    elif floor_level <= 6:
        rarity_weights = {
            Rarity.UNCOMMON: 0.6,
            Rarity.RARE: 0.3,
            Rarity.EPIC: 0.1,
        }
    else:
        rarity_weights = {
            Rarity.UNCOMMON: 0.4,
            Rarity.RARE: 0.35,
            Rarity.EPIC: 0.2,
            Rarity.LEGENDARY: 0.05,
        }
    
    # レアリティ選択
    rarities = list(rarity_weights.keys())
    weights = list(rarity_weights.values())
    selected_rarity = random.choices(rarities, weights=weights)[0]
    
    # 装飾品タイプ選択
    artifact_type = random.choice(list(ArtifactType))
    
    return Artifact(artifact_type, selected_rarity)


def get_starter_artifacts() -> List[Artifact]:
    """スタート時の装飾品を取得"""
    return [
        Artifact(ArtifactType.HEALING_PENDANT, Rarity.UNCOMMON),
    ]