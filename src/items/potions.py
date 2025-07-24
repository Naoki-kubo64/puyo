"""
ポーションシステム - Slay the Spire風の消耗品アイテム
"""

import logging
import random
from typing import Dict, List, Optional, Callable, Any
from enum import Enum
from dataclasses import dataclass

from ..core.constants import *

logger = logging.getLogger(__name__)


class PotionType(Enum):
    """ポーションの種類"""
    HEALTH = "health"              # 体力回復
    ENERGY = "energy"              # エネルギー回復
    STRENGTH = "strength"          # 攻撃力強化
    DEFENSE = "defense"            # 防御力強化
    SPEED = "speed"                # ぷよ落下速度アップ
    CHAIN_POWER = "chain_power"    # 連鎖威力アップ
    COLOR_FOCUS = "color_focus"    # ぷよ色数減少
    SPECIAL_BOOST = "special_boost" # 特殊ぷよ出現率アップ
    FREEZE_TIME = "freeze_time"    # 敵行動停止
    POISON = "poison"              # 敵に毒付与
    EXPLOSIVE = "explosive"        # 爆発ダメージ
    RAINBOW = "rainbow"            # 虹ぷよ生成


@dataclass
class PotionEffect:
    """ポーション効果の定義"""
    effect_type: str               # 効果の種類
    value: float                   # 効果値
    duration: float = 0.0          # 持続時間（0は即座）
    description: str = ""          # 効果の説明


class Potion:
    """ポーションクラス"""
    
    def __init__(self, potion_type: PotionType, rarity: Rarity = Rarity.COMMON):
        self.potion_type = potion_type
        self.rarity = rarity
        self.name = self._get_name()
        self.description = self._get_description()
        self.effect = self._get_effect()
        self.used = False
        
        # 視覚効果
        self.color = self._get_color()
        self.icon = self._get_icon()
        
        logger.debug(f"Created potion: {self.name}")
    
    def _get_name(self) -> str:
        """ポーション名を取得"""
        names = {
            PotionType.HEALTH: "体力回復ポーション",
            PotionType.ENERGY: "エネルギーポーション",
            PotionType.STRENGTH: "力のポーション",
            PotionType.DEFENSE: "守りのポーション",
            PotionType.SPEED: "俊敏のポーション",
            PotionType.CHAIN_POWER: "連鎖強化ポーション",
            PotionType.COLOR_FOCUS: "集中のポーション",
            PotionType.SPECIAL_BOOST: "奇跡のポーション",
            PotionType.FREEZE_TIME: "氷結のポーション",
            PotionType.POISON: "毒のポーション",
            PotionType.EXPLOSIVE: "爆発のポーション",
            PotionType.RAINBOW: "虹のポーション",
        }
        
        base_name = names.get(self.potion_type, "不明なポーション")
        
        # レアリティに応じた接頭辞
        if self.rarity == Rarity.UNCOMMON:
            return f"上質な{base_name}"
        elif self.rarity == Rarity.RARE:
            return f"高級な{base_name}"
        elif self.rarity == Rarity.EPIC:
            return f"伝説の{base_name}"
        elif self.rarity == Rarity.LEGENDARY:
            return f"神話の{base_name}"
        
        return base_name
    
    def _get_description(self) -> str:
        """ポーションの説明を取得"""
        descriptions = {
            PotionType.HEALTH: "HPを回復する",
            PotionType.ENERGY: "戦闘でのエネルギーを回復",
            PotionType.STRENGTH: "一定時間攻撃力を強化",
            PotionType.DEFENSE: "一定時間防御力を強化",
            PotionType.SPEED: "一定時間ぷよの落下速度アップ",
            PotionType.CHAIN_POWER: "一定時間連鎖ダメージアップ",
            PotionType.COLOR_FOCUS: "一定時間ぷよの色数を減少",
            PotionType.SPECIAL_BOOST: "一定時間特殊ぷよ出現率アップ",
            PotionType.FREEZE_TIME: "敵の行動を一時停止",
            PotionType.POISON: "敵に毒ダメージを与える",
            PotionType.EXPLOSIVE: "即座に爆発ダメージを与える",
            PotionType.RAINBOW: "虹ぷよを生成する",
        }
        
        return descriptions.get(self.potion_type, "不明な効果")
    
    def _get_effect(self) -> PotionEffect:
        """ポーション効果を取得"""
        # レアリティによる効果倍率
        rarity_multiplier = {
            Rarity.COMMON: 1.0,
            Rarity.UNCOMMON: 1.3,
            Rarity.RARE: 1.6,
            Rarity.EPIC: 2.0,
            Rarity.LEGENDARY: 2.5,
        }.get(self.rarity, 1.0)
        
        base_effects = {
            PotionType.HEALTH: PotionEffect(
                effect_type="heal",
                value=30 * rarity_multiplier,
                description=f"{int(30 * rarity_multiplier)}HP回復"
            ),
            PotionType.ENERGY: PotionEffect(
                effect_type="energy_gain",
                value=2 * rarity_multiplier,
                description=f"エネルギー+{int(2 * rarity_multiplier)}"
            ),
            PotionType.STRENGTH: PotionEffect(
                effect_type="damage_boost",
                value=25 * rarity_multiplier,
                duration=30.0,
                description=f"30秒間ダメージ+{int(25 * rarity_multiplier)}%"
            ),
            PotionType.DEFENSE: PotionEffect(
                effect_type="damage_reduction",
                value=20 * rarity_multiplier,
                duration=30.0,
                description=f"30秒間被ダメージ-{int(20 * rarity_multiplier)}%"
            ),
            PotionType.SPEED: PotionEffect(
                effect_type="puyo_speed_boost",
                value=50 * rarity_multiplier,
                duration=20.0,
                description=f"20秒間ぷよ速度+{int(50 * rarity_multiplier)}%"
            ),
            PotionType.CHAIN_POWER: PotionEffect(
                effect_type="chain_damage_boost",
                value=30 * rarity_multiplier,
                duration=25.0,
                description=f"25秒間連鎖ダメージ+{int(30 * rarity_multiplier)}%"
            ),
            PotionType.COLOR_FOCUS: PotionEffect(
                effect_type="color_reduction",
                value=1 if rarity_multiplier < 2.0 else 2,
                duration=15.0,
                description=f"15秒間ぷよ色数-{int(1 if rarity_multiplier < 2.0 else 2)}"
            ),
            PotionType.SPECIAL_BOOST: PotionEffect(
                effect_type="special_puyo_rate_boost",
                value=200 * rarity_multiplier,
                duration=20.0,
                description=f"20秒間特殊ぷよ出現率+{int(200 * rarity_multiplier)}%"
            ),
            PotionType.FREEZE_TIME: PotionEffect(
                effect_type="freeze_enemy",
                value=3 * rarity_multiplier,
                description=f"敵を{int(3 * rarity_multiplier)}秒間停止"
            ),
            PotionType.POISON: PotionEffect(
                effect_type="poison_enemy",
                value=8 * rarity_multiplier,
                duration=15.0,
                description=f"15秒間毎秒{int(8 * rarity_multiplier)}毒ダメージ"
            ),
            PotionType.EXPLOSIVE: PotionEffect(
                effect_type="direct_damage",
                value=40 * rarity_multiplier,
                description=f"即座に{int(40 * rarity_multiplier)}ダメージ"
            ),
            PotionType.RAINBOW: PotionEffect(
                effect_type="spawn_rainbow_puyo",
                value=2 + int(rarity_multiplier),
                description=f"虹ぷよを{int(2 + rarity_multiplier)}個生成"
            ),
        }
        
        return base_effects.get(self.potion_type, PotionEffect("unknown", 0))
    
    def _get_color(self) -> tuple:
        """ポーションの色を取得"""
        colors = {
            PotionType.HEALTH: Colors.RED,
            PotionType.ENERGY: Colors.YELLOW,
            PotionType.STRENGTH: Colors.ORANGE,
            PotionType.DEFENSE: Colors.BLUE,
            PotionType.SPEED: Colors.GREEN,
            PotionType.CHAIN_POWER: Colors.PURPLE,
            PotionType.COLOR_FOCUS: Colors.CYAN,
            PotionType.SPECIAL_BOOST: Colors.WHITE,
            PotionType.FREEZE_TIME: Colors.CYAN,
            PotionType.POISON: Colors.DARK_GRAY,
            PotionType.EXPLOSIVE: Colors.ORANGE,
            PotionType.RAINBOW: Colors.WHITE,
        }
        
        return colors.get(self.potion_type, Colors.GRAY)
    
    def _get_icon(self) -> str:
        """ポーションのアイコンを取得"""
        icons = {
            PotionType.HEALTH: "♥",
            PotionType.ENERGY: "⚡",
            PotionType.STRENGTH: "💪",
            PotionType.DEFENSE: "🛡",
            PotionType.SPEED: "💨",
            PotionType.CHAIN_POWER: "🔗",
            PotionType.COLOR_FOCUS: "🎯",
            PotionType.SPECIAL_BOOST: "✨",
            PotionType.FREEZE_TIME: "❄",
            PotionType.POISON: "☠",
            PotionType.EXPLOSIVE: "💥",
            PotionType.RAINBOW: "🌈",
        }
        
        return icons.get(self.potion_type, "🧪")
    
    def use(self, battle_context=None, player=None) -> Dict:
        """ポーションを使用"""
        if self.used:
            return {}
        
        self.used = True
        effect_result = {
            'type': self.effect.effect_type,
            'value': self.effect.value,
            'duration': self.effect.duration,
            'description': self.effect.description,
            'potion_name': self.name
        }
        
        logger.info(f"Used potion: {self.name} - {self.effect.description}")
        return effect_result
    
    def get_rarity_color(self) -> tuple:
        """レアリティ色を取得"""
        return RARITY_COLORS.get(self.rarity, Colors.WHITE)


class PotionInventory:
    """ポーション所持システム"""
    
    def __init__(self, max_potions: int = 3):
        self.max_potions = max_potions
        self.potions: List[Potion] = []
        
        logger.info(f"PotionInventory initialized (max: {max_potions})")
    
    def add_potion(self, potion: Potion) -> bool:
        """ポーションを追加"""
        if len(self.potions) >= self.max_potions:
            logger.warning("Potion inventory is full")
            return False
        
        self.potions.append(potion)
        logger.info(f"Added potion: {potion.name}")
        return True
    
    def use_potion(self, index: int, battle_context=None, player=None) -> Optional[Dict]:
        """ポーションを使用"""
        if 0 <= index < len(self.potions):
            potion = self.potions[index]
            effect = potion.use(battle_context, player)
            
            if effect:
                # 使用済みポーションを削除
                self.potions.pop(index)
                return effect
        
        return None
    
    def remove_potion(self, index: int) -> bool:
        """ポーションを削除"""
        if 0 <= index < len(self.potions):
            removed = self.potions.pop(index)
            logger.info(f"Removed potion: {removed.name}")
            return True
        return False
    
    def get_potion_count(self) -> int:
        """ポーション数を取得"""
        return len(self.potions)
    
    def is_full(self) -> bool:
        """インベントリが満杯かチェック"""
        return len(self.potions) >= self.max_potions
    
    def get_potions(self) -> List[Potion]:
        """全ポーションを取得"""
        return self.potions.copy()


def create_random_potion(floor_level: int = 1) -> Potion:
    """フロアレベルに応じたランダムポーションを生成"""
    # フロアレベルに応じたレアリティ重み
    if floor_level <= 2:
        rarity_weights = {
            Rarity.COMMON: 0.8,
            Rarity.UNCOMMON: 0.2,
        }
    elif floor_level <= 5:
        rarity_weights = {
            Rarity.COMMON: 0.6,
            Rarity.UNCOMMON: 0.3,
            Rarity.RARE: 0.1,
        }
    elif floor_level <= 8:
        rarity_weights = {
            Rarity.COMMON: 0.4,
            Rarity.UNCOMMON: 0.35,
            Rarity.RARE: 0.2,
            Rarity.EPIC: 0.05,
        }
    else:
        rarity_weights = {
            Rarity.COMMON: 0.3,
            Rarity.UNCOMMON: 0.3,
            Rarity.RARE: 0.25,
            Rarity.EPIC: 0.13,
            Rarity.LEGENDARY: 0.02,
        }
    
    # レアリティ選択
    rarities = list(rarity_weights.keys())
    weights = list(rarity_weights.values())
    selected_rarity = random.choices(rarities, weights=weights)[0]
    
    # ポーションタイプ選択
    potion_type = random.choice(list(PotionType))
    
    return Potion(potion_type, selected_rarity)


def get_starter_potions() -> List[Potion]:
    """スタート時のポーションを取得"""
    return [
        Potion(PotionType.HEALTH, Rarity.COMMON),
        Potion(PotionType.ENERGY, Rarity.COMMON),
    ]