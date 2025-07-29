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
    """シンプルな特殊ぷよマネージャー"""
    
    def __init__(self):
        self.special_puyos: Dict[Tuple[int, int], SimpleSpecialPuyo] = {}
        self.spawn_rate = 0.50  # 50%の確率で特殊ぷよ生成
        logger.info("SimpleSpecialManager initialized")
    
    def should_spawn_special(self) -> bool:
        """特殊ぷよを生成するかどうか判定"""
        return random.random() < self.spawn_rate
    
    def get_random_special_type(self) -> SimpleSpecialType:
        """ランダムな特殊ぷよタイプを取得"""
        return random.choice(list(SimpleSpecialType))
    
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