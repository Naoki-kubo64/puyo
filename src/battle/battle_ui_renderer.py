"""
戦闘UI描画クラス - BattleHandlerから描画ロジックを分離
"""

import pygame
import logging
from typing import List, Dict, Any
from core.constants import *
from .enemy import Enemy, EnemyGroup

logger = logging.getLogger(__name__)


class BattleUIRenderer:
    """戦闘UI専用描画クラス"""
    
    def __init__(self, fonts: Dict[str, pygame.font.Font], battle_ui_x: int, battle_ui_y: int):
        self.fonts = fonts
        self.battle_ui_x = battle_ui_x
        self.battle_ui_y = battle_ui_y
        
    def render_enemy_info_panel(self, surface: pygame.Surface, enemy: Enemy, x: int, y: int, 
                               enemy_width: int, enemy_height: int, is_selected: bool):
        """単一敵の情報パネルを描画"""
        font_large = self.fonts['large']
        font_medium = self.fonts['medium']
        font_small = self.fonts['small']
        
        # 背景
        bg_rect = pygame.Rect(x, y, enemy_width, enemy_height)
        pygame.draw.rect(surface, Colors.UI_BACKGROUND, bg_rect)
        pygame.draw.rect(surface, Colors.UI_BORDER, bg_rect, 2)
        
        # 敵名
        name_text = font_medium.render(enemy.get_display_name(), True, Colors.UI_TEXT)
        surface.blit(name_text, (x + 10, y + 10))
        
        # HP表示
        hp_text = f"{enemy.current_hp}/{enemy.max_hp} HP"
        hp_surface = font_small.render(hp_text, True, Colors.UI_TEXT)
        surface.blit(hp_surface, (x + 10, y + 40))
        
        # HPバー
        bar_width = enemy_width - 20
        bar_height = 10
        bar_x = x + 10
        bar_y = y + 65
        
        # HPバー背景
        pygame.draw.rect(surface, Colors.GRAY, (bar_x, bar_y, bar_width, bar_height))
        
        # HPバー（現在HP）
        if enemy.max_hp > 0:
            hp_ratio = enemy.current_hp / enemy.max_hp
            current_bar_width = int(bar_width * hp_ratio)
            hp_color = self._get_hp_color(hp_ratio)
            pygame.draw.rect(surface, hp_color, (bar_x, bar_y, current_bar_width, bar_height))
        
        # 状態表示
        status_y = y + 85
        status_texts = enemy.get_status_text()
        for i, status in enumerate(status_texts[:3]):  # 最大3つまで表示
            status_surface = font_small.render(status, True, Colors.CYAN)
            surface.blit(status_surface, (x + 10, status_y + i * 15))
    
    def render_enemy_action_preview(self, surface: pygame.Surface, enemy: Enemy, x: int, y: int,
                                  enemy_width: int, enemy_height: int):
        """敵の行動予告を描画"""
        font_small = self.fonts['small']
        
        # 次の行動予告
        action_info = enemy.get_next_action_info()
        if action_info:
            # 行動予告背景
            intent_y = y + enemy_height - 40
            intent_rect = pygame.Rect(x + 5, intent_y, enemy_width - 10, 30)
            pygame.draw.rect(surface, Colors.DARK_GRAY, intent_rect)
            pygame.draw.rect(surface, Colors.YELLOW, intent_rect, 1)
            
            # 行動内容テキスト
            if 'damage' in action_info:
                intent_text = f"次の行動: {action_info['name']} ({action_info['damage']}ダメージ)"
            else:
                intent_text = f"次の行動: {action_info['name']}"
            
            intent_surface = font_small.render(intent_text, True, Colors.YELLOW)
            surface.blit(intent_surface, (x + 10, intent_y + 5))
    
    def render_battle_stats(self, surface: pygame.Surface, player, battle_stats: Dict[str, Any]):
        """戦闘統計を描画"""
        font_small = self.fonts['small']
        
        # 戦闘統計表示
        stats_y = self.battle_ui_y + 400
        stats = [
            f"与えたダメージ: {player.total_damage_dealt}",
            f"作った連鎖: {player.total_chains_made}",
            f"時間: {battle_stats.get('battle_time', 0):.1f}秒"
        ]
        
        for i, stat in enumerate(stats):
            stat_text = font_small.render(stat, True, Colors.UI_TEXT)
            surface.blit(stat_text, (self.battle_ui_x, stats_y + i * 20))
    
    def _get_hp_color(self, hp_ratio: float) -> tuple:
        """HP比率に応じた色を取得"""
        if hp_ratio > 0.7:
            return Colors.GREEN
        elif hp_ratio > 0.3:
            return Colors.YELLOW
        else:
            return Colors.RED