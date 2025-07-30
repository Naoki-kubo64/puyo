"""
シンプルな特殊ぷよシステム - 確実に動作する新システム
"""

import pygame
import random
import logging
from typing import Dict, Optional, Tuple
from enum import Enum

from .constants import *

logger = logging.getLogger(__name__)


class SimpleSpecialType(Enum):
    """シンプルな特殊ぷよタイプ"""
    HEAL = "heal"
    BOMB = "bomb"
    LIGHTNING = "lightning"    # 雷ぷよ：縦一列攻撃
    SHIELD = "shield"          # 盾ぷよ：ダメージバリア
    MULTIPLIER = "multiplier"  # 倍率ぷよ：連鎖ダメージ倍率アップ
    POISON = "poison"          # 毒ぷよ：敵に継続ダメージ
    
    def get_display_name(self) -> str:
        """特殊ぷよの固有表示名を取得"""
        try:
            names = {
                SimpleSpecialType.HEAL: "ヒールぷよ",
                SimpleSpecialType.BOMB: "ボムぷよ", 
                SimpleSpecialType.LIGHTNING: "サンダーぷよ",
                SimpleSpecialType.SHIELD: "シールドぷよ",
                SimpleSpecialType.MULTIPLIER: "パワーぷよ",
                SimpleSpecialType.POISON: "ポイズンぷよ"
            }
            return names.get(self, f"{self.value}ぷよ")
        except Exception as e:
            logger.warning(f"Error getting display name for {self}: {e}")
            return "特殊ぷよ"
    
    def get_description(self) -> str:
        """特殊ぷよの効果説明を取得"""
        try:
            descriptions = {
                SimpleSpecialType.HEAL: "プレイヤーのHPを10回復",
                SimpleSpecialType.BOMB: "全ての敵に攻撃",
                SimpleSpecialType.LIGHTNING: "最強の敵1体に強力攻撃", 
                SimpleSpecialType.SHIELD: "ダメージを15軽減",
                SimpleSpecialType.MULTIPLIER: "攻撃力を50%上昇",
                SimpleSpecialType.POISON: "全ての敵に継続ダメージ"
            }
            return descriptions.get(self, "特殊効果")
        except Exception as e:
            logger.warning(f"Error getting description for {self}: {e}")
            return "特殊効果"


class SimpleSpecialPuyo:
    """シンプルな特殊ぷよクラス"""
    
    def __init__(self, x: int, y: int, special_type: SimpleSpecialType):
        self.x = x
        self.y = y
        self.special_type = special_type
        self.icon_image = None
        self._load_icon()
    
    def _load_icon(self):
        """アイコン画像を読み込み"""
        try:
            if self.special_type == SimpleSpecialType.HEAL:
                self.icon_image = pygame.image.load("Picture/HEAL.png")
            elif self.special_type == SimpleSpecialType.BOMB:
                self.icon_image = pygame.image.load("Picture/BOMB.png")
            
            if self.icon_image:
                # 42x42にリサイズ
                self.icon_image = pygame.transform.scale(self.icon_image, (42, 42))
                logger.debug(f"Loaded special puyo icon: {self.special_type.value}")
        except Exception as e:
            logger.warning(f"Failed to load special puyo icon {self.special_type.value}: {e}")
    
    def render(self, surface: pygame.Surface, puyo_x: int, puyo_y: int, puyo_size: int):
        """特殊ぷよアイコンを描画"""
        if not self.icon_image:
            return
        
        # アイコンをぷよの中央に配置（70%サイズ）
        icon_size = int(puyo_size * 0.7)
        icon_offset = (puyo_size - icon_size) // 2
        
        icon_x = puyo_x + icon_offset
        icon_y = puyo_y + icon_offset
        
        # アイコンを描画
        scaled_icon = pygame.transform.scale(self.icon_image, (icon_size, icon_size))
        surface.blit(scaled_icon, (icon_x, icon_y))


class SimpleSpecialManager:
    """シンプルな特殊ぷよマネージャー - 個別出現率対応"""
    
    def __init__(self):
        self.special_puyos: Dict[Tuple[int, int], SimpleSpecialPuyo] = {}
        self.base_spawn_rate = 0.50  # 基本50%の確率で特殊ぷよ生成
        
        # 各特殊ぷよタイプの個別出現率（初期値：0%、報酬で獲得）
        self.type_rates: Dict[SimpleSpecialType, float] = {
            SimpleSpecialType.HEAL: 0.0,       # 0% - 報酬で獲得
            SimpleSpecialType.BOMB: 0.0,       # 0% - 報酬で獲得
            SimpleSpecialType.LIGHTNING: 0.0,  # 0% - 報酬で獲得
            SimpleSpecialType.SHIELD: 0.0,     # 0% - 報酬で獲得
            SimpleSpecialType.MULTIPLIER: 0.0, # 0% - 報酬で獲得
            SimpleSpecialType.POISON: 0.0,     # 0% - 報酬で獲得
        }
        
        logger.info(f"SimpleSpecialManager initialized with rates: {self._format_rates()}")
    
    def _format_rates(self) -> str:
        """出現率を文字列で表示"""
        return ", ".join([f"{t.value}: {r*100:.0f}%" for t, r in self.type_rates.items()])
    
    def should_spawn_special(self) -> bool:
        """特殊ぷよを生成するかどうか判定"""
        return random.random() < self.base_spawn_rate
    
    def get_random_special_type(self) -> Optional[SimpleSpecialType]:
        """確率に基づいてランダムな特殊ぷよタイプを取得"""
        # 各タイプの出現率に基づいて重み付き選択
        types = list(self.type_rates.keys())
        weights = list(self.type_rates.values())
        
        # 重みがすべて0の場合はNoneを返す（特殊ぷよなし）
        if sum(weights) == 0:
            return None
        
        return random.choices(types, weights=weights)[0]
    
    def increase_type_rate(self, special_type: SimpleSpecialType, increase_amount: float = 0.05):
        """特定タイプの出現率を上昇（デフォルト5%）"""
        old_rate = self.type_rates[special_type]
        self.type_rates[special_type] = min(1.0, old_rate + increase_amount)  # 最大100%
        new_rate = self.type_rates[special_type]
        
        logger.info(f"Increased {special_type.value} rate: {old_rate*100:.0f}% -> {new_rate*100:.0f}%")
        return new_rate
    
    def get_type_rate(self, special_type: SimpleSpecialType) -> float:
        """特定タイプの現在の出現率を取得"""
        return self.type_rates.get(special_type, 0.0)
    
    def get_all_rates(self) -> Dict[SimpleSpecialType, float]:
        """全タイプの出現率を取得"""
        return self.type_rates.copy()
    
    def add_special_puyo(self, x: int, y: int, special_type: SimpleSpecialType):
        """特殊ぷよを追加"""
        key = (x, y)
        self.special_puyos[key] = SimpleSpecialPuyo(x, y, special_type)
        logger.debug(f"Added simple special puyo: {special_type.value} at ({x}, {y})")
    
    def remove_special_puyo(self, x: int, y: int):
        """特殊ぷよを削除"""
        key = (x, y)
        if key in self.special_puyos:
            removed = self.special_puyos.pop(key)
            logger.debug(f"Removed special puyo: {removed.special_type.value} at ({x}, {y})")
    
    def get_special_puyo(self, x: int, y: int) -> Optional[SimpleSpecialPuyo]:
        """指定位置の特殊ぷよを取得"""
        return self.special_puyos.get((x, y))
    
    def render_all_icons(self, surface: pygame.Surface, grid_offset_x: int, grid_offset_y: int, puyo_size: int):
        """全ての特殊ぷよアイコンを描画"""
        for special_puyo in self.special_puyos.values():
            puyo_x = grid_offset_x + special_puyo.x * puyo_size
            puyo_y = grid_offset_y + special_puyo.y * puyo_size
            special_puyo.render(surface, puyo_x, puyo_y, puyo_size)
    
    def clear_all(self):
        """全ての特殊ぷよをクリア"""
        self.special_puyos.clear()
        logger.debug("Cleared all special puyos")


# グローバルインスタンス
simple_special_manager = SimpleSpecialManager()