"""
特殊ぷよシステム - オリジナリティのある特殊効果を持つぷよ
"""

import logging
import random
import math
from typing import Dict, List, Optional, Tuple
from enum import Enum
from dataclasses import dataclass

from ..core.constants import *

logger = logging.getLogger(__name__)


class SpecialPuyoType(Enum):
    """特殊ぷよの種類"""
    BOMB = "bomb"              # 爆弾ぷよ：周囲を破壊
    LIGHTNING = "lightning"    # 雷ぷよ：縦一列を破壊
    RAINBOW = "rainbow"        # 虹ぷよ：任意の色として消える
    MULTIPLIER = "multiplier"  # 倍率ぷよ：連鎖ダメージ倍率アップ
    FREEZE = "freeze"          # 氷ぷよ：敵の行動を遅延
    HEAL = "heal"              # 回復ぷよ：プレイヤーHP回復
    SHIELD = "shield"          # 盾ぷよ：ダメージ軽減
    POISON = "poison"          # 毒ぷよ：継続ダメージ
    WILD = "wild"              # ワイルドぷよ：隣接する色に変化
    CHAIN_STARTER = "chain_starter"  # 連鎖開始ぷよ：必ず連鎖を開始


@dataclass
class SpecialEffect:
    """特殊効果の定義"""
    effect_type: str           # 効果の種類
    power: int                 # 効果の強さ
    range: int = 1             # 効果範囲
    duration: float = 0.0      # 持続時間（0は即座）
    description: str = ""      # 効果の説明


class SpecialPuyo:
    """特殊ぷよクラス"""
    
    def __init__(self, special_type: SpecialPuyoType, x: int, y: int):
        self.special_type = special_type
        self.x = x
        self.y = y
        self.active = True
        self.trigger_timer = 0.0
        
        # 特殊効果の定義
        self.effect = self._get_effect_definition()
        
        # 視覚効果
        self.animation_timer = 0.0
        self.pulse_intensity = 0.0
        
        logger.debug(f"Created special puyo: {special_type.value} at ({x}, {y})")
    
    def _get_effect_definition(self) -> SpecialEffect:
        """特殊効果の定義を取得"""
        effects = {
            SpecialPuyoType.BOMB: SpecialEffect(
                effect_type="explosion",
                power=20,
                range=2,
                description="周囲2マスのぷよを破壊し、20ダメージ"
            ),
            SpecialPuyoType.LIGHTNING: SpecialEffect(
                effect_type="lightning_strike",
                power=15,
                range=12,  # 縦一列全体
                description="縦一列のぷよを破壊し、15ダメージ"
            ),
            SpecialPuyoType.RAINBOW: SpecialEffect(
                effect_type="color_match",
                power=0,
                description="任意の色として連鎖に参加"
            ),
            SpecialPuyoType.MULTIPLIER: SpecialEffect(
                effect_type="damage_multiplier",
                power=150,  # 1.5倍
                description="連鎖ダメージを1.5倍にする"
            ),
            SpecialPuyoType.FREEZE: SpecialEffect(
                effect_type="freeze_enemy",
                power=2,  # 2秒
                description="敵の行動を2秒遅延させる"
            ),
            SpecialPuyoType.HEAL: SpecialEffect(
                effect_type="heal_player",
                power=15,
                description="プレイヤーのHPを15回復"
            ),
            SpecialPuyoType.SHIELD: SpecialEffect(
                effect_type="damage_reduction",
                power=50,  # 50%カット
                duration=5.0,
                description="5秒間ダメージを50%軽減"
            ),
            SpecialPuyoType.POISON: SpecialEffect(
                effect_type="poison_enemy",
                power=5,  # 毎秒5ダメージ
                duration=10.0,
                description="10秒間毎秒5ダメージの毒"
            ),
            SpecialPuyoType.WILD: SpecialEffect(
                effect_type="color_adaptation",
                power=0,
                description="隣接するぷよの色に変化"
            ),
            SpecialPuyoType.CHAIN_STARTER: SpecialEffect(
                effect_type="force_chain",
                power=4,  # 4個扱い
                description="必ず連鎖を開始（4個分として扱う）"
            ),
        }
        
        return effects.get(self.special_type, SpecialEffect("unknown", 0))
    
    def update(self, dt: float):
        """更新処理"""
        self.animation_timer += dt
        self.pulse_intensity = (math.sin(self.animation_timer * 4) + 1) / 2
        
        if self.trigger_timer > 0:
            self.trigger_timer -= dt
    
    def trigger_effect(self, battle_context=None, puyo_grid=None) -> Dict:
        """特殊効果を発動"""
        if not self.active:
            return {}
        
        effect_result = {
            'type': self.effect.effect_type,
            'power': self.effect.power,
            'range': self.effect.range,
            'duration': self.effect.duration,
            'position': (self.x, self.y),
            'description': self.effect.description
        }
        
        logger.info(f"Triggered special effect: {self.special_type.value} - {self.effect.description}")
        
        # 効果に応じた処理
        if self.special_type == SpecialPuyoType.BOMB:
            effect_result['affected_positions'] = self._get_explosion_range()
        
        elif self.special_type == SpecialPuyoType.LIGHTNING:
            effect_result['affected_positions'] = self._get_lightning_range()
        
        elif self.special_type == SpecialPuyoType.WILD and puyo_grid:
            effect_result['new_color'] = self._determine_wild_color(puyo_grid)
        
        # 効果発動後は非アクティブに
        self.active = False
        
        return effect_result
    
    def _get_explosion_range(self) -> List[Tuple[int, int]]:
        """爆発範囲を取得"""
        positions = []
        range_val = self.effect.range
        
        for dx in range(-range_val, range_val + 1):
            for dy in range(-range_val, range_val + 1):
                if dx == 0 and dy == 0:
                    continue
                
                x, y = self.x + dx, self.y + dy
                if 0 <= x < GRID_WIDTH and 0 <= y < GRID_HEIGHT:
                    positions.append((x, y))
        
        return positions
    
    def _get_lightning_range(self) -> List[Tuple[int, int]]:
        """雷の範囲を取得（縦一列）"""
        positions = []
        
        for y in range(GRID_HEIGHT):
            if y != self.y:  # 自分以外
                positions.append((self.x, y))
        
        return positions
    
    def _determine_wild_color(self, puyo_grid) -> PuyoType:
        """ワイルドぷよの色を決定"""
        # 隣接するぷよの色を調査
        adjacent_colors = []
        
        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nx, ny = self.x + dx, self.y + dy
            if 0 <= nx < GRID_WIDTH and 0 <= ny < GRID_HEIGHT:
                color = puyo_grid.get_puyo(nx, ny)
                if color != PuyoType.EMPTY and color != PuyoType.GARBAGE:
                    adjacent_colors.append(color)
        
        # 最も多い色を選択、なければランダム
        if adjacent_colors:
            return max(set(adjacent_colors), key=adjacent_colors.count)
        else:
            return random.choice([PuyoType.RED, PuyoType.BLUE, PuyoType.GREEN, PuyoType.YELLOW])
    
    def get_display_color(self) -> tuple:
        """表示色を取得"""
        base_colors = {
            SpecialPuyoType.BOMB: Colors.ORANGE,
            SpecialPuyoType.LIGHTNING: Colors.YELLOW,
            SpecialPuyoType.RAINBOW: Colors.WHITE,
            SpecialPuyoType.MULTIPLIER: Colors.PURPLE,
            SpecialPuyoType.FREEZE: Colors.CYAN,
            SpecialPuyoType.HEAL: Colors.GREEN,
            SpecialPuyoType.SHIELD: Colors.BLUE,
            SpecialPuyoType.POISON: Colors.DARK_GRAY,
            SpecialPuyoType.WILD: Colors.LIGHT_GRAY,
            SpecialPuyoType.CHAIN_STARTER: Colors.RED,
        }
        
        base_color = base_colors.get(self.special_type, Colors.WHITE)
        
        # パルス効果で明度を変更
        intensity = int(100 + 155 * self.pulse_intensity)
        return tuple(min(255, max(0, c + intensity - 100)) for c in base_color)
    
    def get_icon_char(self) -> str:
        """アイコン文字を取得"""
        icons = {
            SpecialPuyoType.BOMB: "💣",
            SpecialPuyoType.LIGHTNING: "⚡",
            SpecialPuyoType.RAINBOW: "🌈",
            SpecialPuyoType.MULTIPLIER: "×",
            SpecialPuyoType.FREEZE: "❄",
            SpecialPuyoType.HEAL: "♥",
            SpecialPuyoType.SHIELD: "🛡",
            SpecialPuyoType.POISON: "☠",
            SpecialPuyoType.WILD: "?",
            SpecialPuyoType.CHAIN_STARTER: "⭐",
        }
        
        return icons.get(self.special_type, "S")


class SpecialPuyoManager:
    """特殊ぷよ管理システム"""
    
    def __init__(self):
        self.special_puyos: Dict[Tuple[int, int], SpecialPuyo] = {}
        self.spawn_chance = 0.05  # 5%の確率で特殊ぷよ生成
        self.rarity_weights = {
            SpecialPuyoType.HEAL: 0.25,
            SpecialPuyoType.BOMB: 0.20,
            SpecialPuyoType.LIGHTNING: 0.15,
            SpecialPuyoType.SHIELD: 0.12,
            SpecialPuyoType.FREEZE: 0.10,
            SpecialPuyoType.WILD: 0.08,
            SpecialPuyoType.POISON: 0.05,
            SpecialPuyoType.MULTIPLIER: 0.03,
            SpecialPuyoType.RAINBOW: 0.015,
            SpecialPuyoType.CHAIN_STARTER: 0.005,
        }
        
        logger.info("SpecialPuyoManager initialized")
    
    def should_spawn_special_puyo(self) -> bool:
        """特殊ぷよを生成するかどうか判定"""
        return random.random() < self.spawn_chance
    
    def get_random_special_type(self) -> SpecialPuyoType:
        """ランダムな特殊ぷよタイプを取得"""
        types = list(self.rarity_weights.keys())
        weights = list(self.rarity_weights.values())
        return random.choices(types, weights=weights)[0]
    
    def add_special_puyo(self, x: int, y: int, special_type: Optional[SpecialPuyoType] = None):
        """特殊ぷよを追加"""
        if special_type is None:
            special_type = self.get_random_special_type()
        
        special_puyo = SpecialPuyo(special_type, x, y)
        self.special_puyos[(x, y)] = special_puyo
        
        logger.debug(f"Added special puyo: {special_type.value} at ({x}, {y})")
    
    def remove_special_puyo(self, x: int, y: int):
        """特殊ぷよを削除"""
        if (x, y) in self.special_puyos:
            del self.special_puyos[(x, y)]
    
    def get_special_puyo(self, x: int, y: int) -> Optional[SpecialPuyo]:
        """位置の特殊ぷよを取得"""
        return self.special_puyos.get((x, y))
    
    def update(self, dt: float):
        """更新処理"""
        for special_puyo in self.special_puyos.values():
            special_puyo.update(dt)
    
    def trigger_chain_effects(self, chain_positions: List[Tuple[int, int]], battle_context=None, puyo_grid=None) -> List[Dict]:
        """連鎖に含まれる特殊ぷよの効果を発動"""
        effects = []
        
        for x, y in chain_positions:
            special_puyo = self.get_special_puyo(x, y)
            if special_puyo and special_puyo.active:
                effect = special_puyo.trigger_effect(battle_context, puyo_grid)
                if effect:
                    effects.append(effect)
        
        return effects
    
    def clear_all(self):
        """全ての特殊ぷよをクリア"""
        self.special_puyos.clear()
    
    def get_all_positions(self) -> List[Tuple[int, int]]:
        """全ての特殊ぷよの位置を取得"""
        return list(self.special_puyos.keys())


# グローバル特殊ぷよマネージャー
special_puyo_manager = SpecialPuyoManager()


def increase_special_puyo_chance(multiplier: float):
    """特殊ぷよ出現率を増加"""
    special_puyo_manager.spawn_chance = min(0.5, special_puyo_manager.spawn_chance * multiplier)
    logger.info(f"Special puyo spawn chance increased to {special_puyo_manager.spawn_chance:.2%}")


def reset_special_puyo_chance():
    """特殊ぷよ出現率をリセット"""
    special_puyo_manager.spawn_chance = 0.05
    logger.info("Special puyo spawn chance reset to 5%")