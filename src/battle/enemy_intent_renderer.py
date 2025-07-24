"""
敵の行動予告ビジュアルシステム
敵の上に美しいアイコンで次の行動を表示
"""

import pygame
import math
from typing import Dict, Optional
from ..core.constants import Colors
from .enemy import ActionType

class EnemyIntentRenderer:
    """敵の行動予告の描画を担当するクラス"""
    
    def __init__(self):
        """行動予告レンダラーを初期化"""
        self.animation_time = 0
        self.pulse_intensity = 0
    
    def update(self, dt: float):
        """アニメーションを更新"""
        self.animation_time += dt
        self.pulse_intensity = abs(math.sin(self.animation_time * 3))
    
    def draw_intent(self, surface: pygame.Surface, x: int, y: int, 
                    action_info: Dict, fonts: Dict[str, pygame.font.Font]):
        """敵の行動予告を敵の上に描画"""
        print(f"DEBUG: draw_intent called with action_info: {action_info}")
        
        if not action_info:
            print("DEBUG: No action_info, returning")
            return
        
        action_type = action_info.get('type', ActionType.ATTACK)
        damage = action_info.get('damage', 0)
        name = action_info.get('name', '不明')
        
        print(f"DEBUG: action_type = {action_type}, damage = {damage}, name = {name}")
        
        # より大きなインテントボックス
        intent_x = x - 40
        intent_y = y - 60
        intent_width = 80
        intent_height = 50
        
        # インテントの背景（明確に見えるように）
        pygame.draw.rect(surface, (100, 0, 0), (intent_x, intent_y, intent_width, intent_height))
        pygame.draw.rect(surface, (255, 255, 255), (intent_x, intent_y, intent_width, intent_height), 3)
        
        # アクションアイコン（大きく、明確に）
        icon_x = intent_x + intent_width // 2
        icon_y = intent_y + intent_height // 2
        
        print(f"DEBUG: Drawing icon at ({icon_x}, {icon_y}) for action_type {action_type}")
        
        # 直接ここでアイコンを描画
        if action_type == ActionType.ATTACK:
            # 剣：太い白い十字
            pygame.draw.line(surface, (255, 255, 255), (icon_x, icon_y - 15), (icon_x, icon_y + 15), 5)
            pygame.draw.line(surface, (255, 255, 255), (icon_x - 10, icon_y), (icon_x + 10, icon_y), 5)
        elif action_type == ActionType.GUARD:
            # 盾：白い円
            pygame.draw.circle(surface, (255, 255, 255), (icon_x, icon_y), 12, 4)
        else:
            # デフォルト：白い四角
            pygame.draw.rect(surface, (255, 255, 255), (icon_x - 8, icon_y - 8, 16, 16))
        
        # ダメージ数値（攻撃の場合）
        if action_type == ActionType.ATTACK and damage > 0:
            self._draw_damage_number(surface, icon_x, intent_y + intent_height + 10, damage, fonts)
    
    def _draw_intent_background(self, surface: pygame.Surface, x: int, y: int, 
                                width: int, height: int, action_type: ActionType):
        """インテント背景を描画"""
        # アクションタイプ別の色
        if action_type == ActionType.ATTACK:
            bg_color = (150, 50, 50)  # 赤系
            border_color = (200, 80, 80)
        elif action_type == ActionType.GUARD:
            bg_color = (50, 100, 150)  # 青系
            border_color = (80, 130, 200)
        elif action_type == ActionType.HEAL:
            bg_color = (50, 150, 50)  # 緑系
            border_color = (80, 200, 80)
        elif action_type == ActionType.BUFF:
            bg_color = (150, 100, 50)  # オレンジ系
            border_color = (200, 130, 80)
        elif action_type == ActionType.DEBUFF:
            bg_color = (100, 50, 150)  # 紫系
            border_color = (130, 80, 200)
        else:
            bg_color = (100, 100, 100)  # グレー
            border_color = (150, 150, 150)
        
        # パルス効果
        pulse_offset = int(self.pulse_intensity * 2)
        
        # 背景の六角形風ボックス
        points = [
            (x + 5, y),
            (x + width - 5, y),
            (x + width, y + height // 2),
            (x + width - 5, y + height),
            (x + 5, y + height),
            (x, y + height // 2)
        ]
        
        # 影
        shadow_points = [(px + 2, py + 2) for px, py in points]
        pygame.draw.polygon(surface, (20, 20, 20), shadow_points)
        
        # メイン背景
        pygame.draw.polygon(surface, bg_color, points)
        
        # 光る縁
        border_width = 2 + pulse_offset
        pygame.draw.polygon(surface, border_color, points, border_width)
        
        # 内側のハイライト
        inner_points = [(px + 3, py + 3) if i < 3 else (px - 3, py - 3) for i, (px, py) in enumerate(points)]
        pygame.draw.polygon(surface, (min(255, bg_color[0] + 30), 
                                    min(255, bg_color[1] + 30), 
                                    min(255, bg_color[2] + 30)), inner_points, 1)
    
    def _draw_action_icon(self, surface: pygame.Surface, x: int, y: int, action_type: ActionType):
        """アクションアイコンを描画"""
        icon_size = 20  # 固定の大きなサイズ
        
        if action_type == ActionType.ATTACK:
            # 攻撃：シンプルな剣
            self._draw_simple_sword(surface, x, y, icon_size, Colors.WHITE)
        elif action_type == ActionType.GUARD:
            # 防御：シンプルな盾
            self._draw_simple_shield(surface, x, y, icon_size, Colors.WHITE)
        elif action_type == ActionType.HEAL:
            # 回復：プラス記号
            self._draw_simple_plus(surface, x, y, icon_size, Colors.WHITE)
        elif action_type == ActionType.BUFF:
            # バフ：上矢印
            self._draw_simple_arrow_up(surface, x, y, icon_size, Colors.WHITE)
        elif action_type == ActionType.DEBUFF:
            # デバフ：下矢印
            self._draw_simple_arrow_down(surface, x, y, icon_size, Colors.WHITE)
        elif action_type == ActionType.SPECIAL:
            # 特殊：星
            self._draw_simple_star(surface, x, y, icon_size, Colors.WHITE)
        else:
            # デフォルト：疑問符
            self._draw_simple_question(surface, x, y, icon_size, Colors.WHITE)
    
    def _draw_sword_icon(self, surface: pygame.Surface, x: int, y: int, size: int, color: tuple):
        """剣のアイコンを描画"""
        # より見やすいサイズに調整
        actual_size = max(size, 15)
        
        # 剣の刃（太い縦線）
        blade_start = (x, y - actual_size//2)
        blade_end = (x, y + actual_size//3)
        pygame.draw.line(surface, color, blade_start, blade_end, 4)
        
        # 剣の鍔（横線）
        guard_start = (x - actual_size//3, y + actual_size//4)
        guard_end = (x + actual_size//3, y + actual_size//4)
        pygame.draw.line(surface, color, guard_start, guard_end, 3)
        
        # 剣の柄
        handle_start = (x, y + actual_size//4)
        handle_end = (x, y + actual_size//2)
        pygame.draw.line(surface, color, handle_start, handle_end, 2)
    
    def _draw_shield_icon(self, surface: pygame.Surface, x: int, y: int, size: int, color: tuple):
        """盾のアイコンを描画"""
        actual_size = max(size, 12)
        
        # 盾の形（楕円）
        shield_rect = pygame.Rect(x - actual_size//2, y - actual_size//2, actual_size, actual_size)
        pygame.draw.ellipse(surface, color, shield_rect, 3)
        
        # 盾の中央の十字
        pygame.draw.line(surface, color, (x, y - actual_size//3), (x, y + actual_size//3), 2)
        pygame.draw.line(surface, color, (x - actual_size//3, y), (x + actual_size//3, y), 2)
    
    def _draw_plus_icon(self, surface: pygame.Surface, x: int, y: int, size: int, color: tuple):
        """プラスのアイコンを描画"""
        # 縦線
        pygame.draw.line(surface, color, (x, y - size), (x, y + size), 3)
        # 横線
        pygame.draw.line(surface, color, (x - size, y), (x + size, y), 3)
    
    def _draw_arrow_up_icon(self, surface: pygame.Surface, x: int, y: int, size: int, color: tuple):
        """上矢印のアイコンを描画"""
        arrow_points = [
            (x, y - size),
            (x - size, y + size//2),
            (x - size//2, y + size//2),
            (x - size//2, y + size),
            (x + size//2, y + size),
            (x + size//2, y + size//2),
            (x + size, y + size//2)
        ]
        pygame.draw.polygon(surface, color, arrow_points)
    
    def _draw_arrow_down_icon(self, surface: pygame.Surface, x: int, y: int, size: int, color: tuple):
        """下矢印のアイコンを描画"""
        arrow_points = [
            (x, y + size),
            (x - size, y - size//2),
            (x - size//2, y - size//2),
            (x - size//2, y - size),
            (x + size//2, y - size),
            (x + size//2, y - size//2),
            (x + size, y - size//2)
        ]
        pygame.draw.polygon(surface, color, arrow_points)
    
    def _draw_star_icon(self, surface: pygame.Surface, x: int, y: int, size: int, color: tuple):
        """星のアイコンを描画"""
        # 5つ星
        angle_offset = -math.pi / 2  # 上向き
        star_points = []
        
        for i in range(10):  # 外側と内側の点を交互に
            angle = (i * math.pi / 5) + angle_offset
            if i % 2 == 0:
                # 外側の点
                r = size
            else:
                # 内側の点
                r = size // 2
            
            point_x = x + r * math.cos(angle)
            point_y = y + r * math.sin(angle)
            star_points.append((point_x, point_y))
        
        pygame.draw.polygon(surface, color, star_points)
        pygame.draw.polygon(surface, (255, 255, 150), star_points, 1)
    
    def _draw_damage_number(self, surface: pygame.Surface, x: int, y: int, 
                            damage: int, fonts: Dict[str, pygame.font.Font]):
        """ダメージ数値を描画"""
        damage_text = str(damage)
        font = fonts.get('small', fonts.get('medium'))
        
        # 文字の影
        shadow_surface = font.render(damage_text, True, (0, 0, 0))
        surface.blit(shadow_surface, (x - shadow_surface.get_width()//2 + 1, y + 1))
        
        # メイン文字
        text_surface = font.render(damage_text, True, (255, 255, 255))
        surface.blit(text_surface, (x - text_surface.get_width()//2, y))
    
    def _draw_action_tooltip(self, surface: pygame.Surface, x: int, y: int, 
                             name: str, fonts: Dict[str, pygame.font.Font]):
        """アクション名のツールチップを描画"""
        if not name or name == '不明':
            return
        
        font = fonts.get('small', fonts.get('medium'))
        text_surface = font.render(name, True, Colors.WHITE)
        text_width = text_surface.get_width()
        text_height = text_surface.get_height()
        
        # ツールチップ背景
        tooltip_rect = pygame.Rect(x - text_width//2 - 5, y - text_height - 5, 
                                  text_width + 10, text_height + 10)
        pygame.draw.rect(surface, (40, 40, 40), tooltip_rect)
        pygame.draw.rect(surface, (120, 120, 120), tooltip_rect, 1)
        
        # テキスト
        surface.blit(text_surface, (x - text_width//2, y - text_height))
    
    def _draw_magic_icon(self, surface: pygame.Surface, x: int, y: int, size: int, color: tuple):
        """魔法のアイコンを描画"""
        actual_size = max(size, 12)
        
        # 魔法の杖
        staff_start = (x, y + actual_size//2)
        staff_end = (x, y - actual_size//3)
        pygame.draw.line(surface, color, staff_start, staff_end, 3)
        
        # 魔法の珠（上部）
        pygame.draw.circle(surface, color, (x, y - actual_size//3), actual_size//4, 2)
        
        # 魔法のエフェクト（星形）
        star_points = [
            (x - actual_size//4, y - actual_size//2),
            (x, y - actual_size//2 - actual_size//4),
            (x + actual_size//4, y - actual_size//2),
            (x + actual_size//6, y - actual_size//3),
            (x - actual_size//6, y - actual_size//3)
        ]
        pygame.draw.polygon(surface, color, star_points)
    
    # シンプルなアイコン描画メソッド群
    def _draw_simple_sword(self, surface: pygame.Surface, x: int, y: int, size: int, color: tuple):
        """シンプルな剣アイコン"""
        # 太い縦線（刃）
        pygame.draw.line(surface, color, (x, y - size//2), (x, y + size//3), 6)
        # 横線（鍔）
        pygame.draw.line(surface, color, (x - size//3, y), (x + size//3, y), 4)
    
    def _draw_simple_shield(self, surface: pygame.Surface, x: int, y: int, size: int, color: tuple):
        """シンプルな盾アイコン"""
        # 大きな円
        pygame.draw.circle(surface, color, (x, y), size//2, 4)
        # 中央の十字
        pygame.draw.line(surface, color, (x, y - size//3), (x, y + size//3), 3)
        pygame.draw.line(surface, color, (x - size//3, y), (x + size//3, y), 3)
    
    def _draw_simple_plus(self, surface: pygame.Surface, x: int, y: int, size: int, color: tuple):
        """シンプルなプラスアイコン"""
        # 太い十字
        pygame.draw.line(surface, color, (x, y - size//2), (x, y + size//2), 6)
        pygame.draw.line(surface, color, (x - size//2, y), (x + size//2, y), 6)
    
    def _draw_simple_arrow_up(self, surface: pygame.Surface, x: int, y: int, size: int, color: tuple):
        """シンプルな上矢印アイコン"""
        # 三角形
        points = [
            (x, y - size//2),
            (x - size//2, y + size//3),
            (x + size//2, y + size//3)
        ]
        pygame.draw.polygon(surface, color, points)
    
    def _draw_simple_arrow_down(self, surface: pygame.Surface, x: int, y: int, size: int, color: tuple):
        """シンプルな下矢印アイコン"""
        # 三角形
        points = [
            (x, y + size//2),
            (x - size//2, y - size//3),
            (x + size//2, y - size//3)
        ]
        pygame.draw.polygon(surface, color, points)
    
    def _draw_simple_star(self, surface: pygame.Surface, x: int, y: int, size: int, color: tuple):
        """シンプルな星アイコン"""
        # 4つの放射線
        pygame.draw.line(surface, color, (x, y - size//2), (x, y + size//2), 4)
        pygame.draw.line(surface, color, (x - size//2, y), (x + size//2, y), 4)
        pygame.draw.line(surface, color, (x - size//3, y - size//3), (x + size//3, y + size//3), 3)
        pygame.draw.line(surface, color, (x + size//3, y - size//3), (x - size//3, y + size//3), 3)
    
    def _draw_simple_question(self, surface: pygame.Surface, x: int, y: int, size: int, color: tuple):
        """シンプルな疑問符アイコン"""
        # 大きな円
        pygame.draw.circle(surface, color, (x, y), size//2, 4)