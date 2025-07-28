"""
上部UIバーシステム
Slay the Spireスタイルの美しい上部UI表示
"""

import pygame
import math
import os
from typing import Dict, Optional
from .constants import Colors, SCREEN_WIDTH, FONT_SIZE_SMALL, FONT_SIZE_MEDIUM
from .game_engine import get_appropriate_font

class TopUIBar:
    """上部UIバーの描画と管理を担当するクラス"""
    
    def __init__(self, fonts: Dict[str, pygame.font.Font]):
        """上部UIバーを初期化"""
        self.fonts = fonts
        self.bar_height = 60
        self.animation_time = 0
        
        # UI要素の位置
        self.hp_icon_pos = (20, 15)
        self.energy_icon_pos = (200, 15)
        self.gold_icon_pos = (380, 15)
        self.floor_icon_pos = (SCREEN_WIDTH - 120, 15)
        
        # アニメーション用
        self.hp_pulse = 0
        self.energy_pulse = 0
        self.damage_flash = 0
        
        # アイコン画像を読み込み
        self.hp_icon = None
        self.gold_icon = None
        self._load_icons()
    
    def update(self, dt: float):
        """UIアニメーションを更新"""
        self.animation_time += dt
        self.hp_pulse = abs(math.sin(self.animation_time * 2))
        self.energy_pulse = abs(math.sin(self.animation_time * 1.5))
        
        # ダメージフラッシュを減衰
        if self.damage_flash > 0:
            self.damage_flash -= dt * 3
    
    def _load_icons(self):
        """アイコン画像を読み込み"""
        try:
            # プロジェクトルートからのパス
            base_path = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
            
            # HP.pngを読み込み
            hp_path = os.path.join(base_path, "HP.png")
            if os.path.exists(hp_path):
                self.hp_icon = pygame.image.load(hp_path).convert_alpha()
                # サイズを調整（24x24ピクセル）
                self.hp_icon = pygame.transform.scale(self.hp_icon, (24, 24))
            
            # gold.pngを読み込み
            gold_path = os.path.join(base_path, "gold.png")
            if os.path.exists(gold_path):
                self.gold_icon = pygame.image.load(gold_path).convert_alpha()
                # サイズを調整（24x24ピクセル）
                self.gold_icon = pygame.transform.scale(self.gold_icon, (24, 24))
                
        except Exception as e:
            print(f"Warning: Could not load UI icons: {e}")
    
    def trigger_damage_flash(self):
        """ダメージを受けた時のフラッシュエフェクト"""
        self.damage_flash = 1.0
    
    def draw_top_bar(self, surface: pygame.Surface, player_hp: int, player_max_hp: int, 
                     energy: int, max_energy: int, gold: int, floor: int):
        """上部UIバーを描画"""
        # 背景バー
        self._draw_background_bar(surface)
        
        # HP表示
        self._draw_hp_display(surface, player_hp, player_max_hp)
        
        # エネルギー表示（削除済み）
        # self._draw_energy_display(surface, energy, max_energy)
        
        # ゴールド表示
        self._draw_gold_display(surface, gold)
        
        # フロア表示
        self._draw_floor_display(surface, floor)
        
        # 装飾エレメント
        self._draw_decorative_elements(surface)
    
    def _draw_background_bar(self, surface: pygame.Surface):
        """背景バーを描画"""
        # メインバー背景
        bar_rect = pygame.Rect(0, 0, SCREEN_WIDTH, self.bar_height)
        
        # まず背景をクリア
        pygame.draw.rect(surface, (25, 20, 35), bar_rect)
        
        # グラデーション背景
        for y in range(self.bar_height):
            ratio = y / self.bar_height
            r = int(35 + ratio * 20)
            g = int(25 + ratio * 15)
            b = int(45 + ratio * 15)
            color = (r, g, b)
            pygame.draw.line(surface, color, (0, y), (SCREEN_WIDTH, y))
        
        # 下部のハイライト
        pygame.draw.line(surface, (100, 90, 80), (0, self.bar_height - 2), (SCREEN_WIDTH, self.bar_height - 2), 2)
        
        # 上部のシャドウ
        pygame.draw.line(surface, (15, 10, 10), (0, 0), (SCREEN_WIDTH, 0), 2)
    
    def _draw_hp_display(self, surface: pygame.Surface, current_hp: int, max_hp: int):
        """HP表示を描画"""
        x, y = self.hp_icon_pos
        
        # HPアイコン（画像またはハート）
        if self.hp_icon:
            # HP.png画像を使用
            icon_rect = self.hp_icon.get_rect()
            icon_rect.x = x
            icon_rect.y = y + 8
            
            # ダメージフラッシュ効果
            if self.damage_flash > 0:
                # 赤色フラッシュ効果を適用
                flash_surface = self.hp_icon.copy()
                flash_surface.fill((255, 100, 100), special_flags=pygame.BLEND_MULT)
                surface.blit(flash_surface, icon_rect)
            else:
                surface.blit(self.hp_icon, icon_rect)
        else:
            # フォールバック：ハート描画
            heart_color = (200, 50, 50) if current_hp > max_hp * 0.3 else (255, 100, 100)
            if self.damage_flash > 0:
                flash_intensity = int(self.damage_flash * 255)
                heart_color = (255, flash_intensity, flash_intensity)
            
            heart_size = 12 + int(self.hp_pulse * 2)
            self._draw_heart(surface, x, y + 10, heart_size, heart_color)
        
        # HP数値
        hp_text = f"{current_hp}/{max_hp}"
        hp_font = get_appropriate_font(self.fonts, hp_text, 'medium')
        hp_surface = hp_font.render(hp_text, True, Colors.WHITE)
        surface.blit(hp_surface, (x + 30, y + 5))
        
        # HPバー
        bar_width = 100
        bar_height = 8
        bar_x = x + 30
        bar_y = y + 25
        
        # HPバー背景
        bar_bg_rect = pygame.Rect(bar_x, bar_y, bar_width, bar_height)
        pygame.draw.rect(surface, (60, 30, 30), bar_bg_rect)
        
        # HPバー前景
        hp_ratio = current_hp / max_hp if max_hp > 0 else 0
        hp_bar_width = int(bar_width * hp_ratio)
        
        if hp_ratio > 0.6:
            hp_color = (100, 200, 100)  # 緑
        elif hp_ratio > 0.3:
            hp_color = (200, 200, 100)  # 黄
        else:
            hp_color = (200, 100, 100)  # 赤
        
        if hp_bar_width > 0:
            hp_bar_rect = pygame.Rect(bar_x, bar_y, hp_bar_width, bar_height)
            pygame.draw.rect(surface, hp_color, hp_bar_rect)
        
        # HPバーの縁
        pygame.draw.rect(surface, (120, 100, 80), bar_bg_rect, 1)
    
    def _draw_energy_display(self, surface: pygame.Surface, current_energy: int, max_energy: int):
        """エネルギー表示を描画（削除済み）"""
        return  # エネルギーシステム削除のため無効化
        x, y = self.energy_icon_pos
        
        # エネルギーオーブ
        orb_size = 15 + int(self.energy_pulse * 2)
        orb_color = (100, 150, 255)
        
        # 外側の光
        for r in range(orb_size + 5, orb_size, -1):
            alpha = max(0, 50 - (r - orb_size) * 10)
            if alpha > 0:
                orb_surface = pygame.Surface((r*2, r*2))
                orb_surface.set_alpha(alpha)
                pygame.draw.circle(orb_surface, orb_color, (r, r), r)
                surface.blit(orb_surface, (x - r, y + 10 - r))
        
        # メインオーブ
        pygame.draw.circle(surface, orb_color, (x, y + 10), orb_size)
        pygame.draw.circle(surface, (150, 200, 255), (x - 3, y + 7), 5)
        
        # エネルギー数値
        energy_text = f"{current_energy}/{max_energy}"
        energy_font = get_appropriate_font(self.fonts, energy_text, 'medium')
        energy_surface = energy_font.render(energy_text, True, Colors.WHITE)
        surface.blit(energy_surface, (x + 25, y + 5))
        
        # エネルギーオーブ（小さい球）
        orb_y = y + 25
        for i in range(max_energy):
            orb_x = x + 25 + i * 15
            if i < current_energy:
                # 満杯のオーブ
                pygame.draw.circle(surface, (100, 150, 255), (orb_x, orb_y), 6)
                pygame.draw.circle(surface, (150, 200, 255), (orb_x - 2, orb_y - 2), 3)
            else:
                # 空のオーブ
                pygame.draw.circle(surface, (50, 70, 100), (orb_x, orb_y), 6)
                pygame.draw.circle(surface, (80, 100, 130), (orb_x, orb_y), 6, 1)
    
    def _draw_gold_display(self, surface: pygame.Surface, gold: int):
        """ゴールド表示を描画"""
        x, y = self.gold_icon_pos
        
        # ゴールドアイコン（画像またはコイン）
        if self.gold_icon:
            # gold.png画像を使用
            icon_rect = self.gold_icon.get_rect()
            icon_rect.x = x
            icon_rect.y = y + 8
            surface.blit(self.gold_icon, icon_rect)
        else:
            # フォールバック：コイン描画
            coin_color = (255, 215, 0)  # ゴールド色
            
            # コインの影
            pygame.draw.circle(surface, (100, 86, 0), (x + 2, y + 12), 12)
            
            # メインコイン
            pygame.draw.circle(surface, coin_color, (x, y + 10), 12)
            pygame.draw.circle(surface, (255, 255, 150), (x - 3, y + 7), 4)
            
            # コインの縁
            pygame.draw.circle(surface, (200, 170, 0), (x, y + 10), 12, 2)
        
        # ゴールド数値
        gold_text = str(gold)
        gold_font = get_appropriate_font(self.fonts, gold_text, 'medium')
        gold_surface = gold_font.render(gold_text, True, Colors.WHITE)
        surface.blit(gold_surface, (x + 25, y + 5))
        
        # "Gold" ラベル
        label_font = get_appropriate_font(self.fonts, "Gold", 'small')
        label_surface = label_font.render("Gold", True, Colors.LIGHT_GRAY)
        surface.blit(label_surface, (x + 25, y + 25))
    
    def _draw_floor_display(self, surface: pygame.Surface, floor: int):
        """フロア表示を描画"""
        x, y = self.floor_icon_pos
        
        # フロアアイコン（階段）
        stair_color = (120, 100, 80)
        
        # 階段の描画
        for i in range(3):
            step_y = y + 8 + i * 4
            step_width = 20 - i * 2
            step_rect = pygame.Rect(x - step_width // 2, step_y, step_width, 3)
            pygame.draw.rect(surface, stair_color, step_rect)
            pygame.draw.rect(surface, (150, 130, 110), step_rect, 1)
        
        # フロア数値
        floor_text = f"Floor {floor}"
        floor_font = get_appropriate_font(self.fonts, floor_text, 'medium')
        floor_surface = floor_font.render(floor_text, True, Colors.WHITE)
        floor_rect = floor_surface.get_rect()
        surface.blit(floor_surface, (x - floor_rect.width - 30, y + 5))
    
    def _draw_heart(self, surface: pygame.Surface, x: int, y: int, size: int, color: tuple):
        """ハートの形を描画"""
        # ハートの形を近似的に描画
        heart_points = []
        
        # ハートの上部（2つの円弧）
        for angle in range(0, 180, 10):
            rad = math.radians(angle)
            left_x = x - size//2 + math.cos(rad) * size//3
            left_y = y - size//4 + math.sin(rad) * size//3
            heart_points.append((left_x, left_y))
        
        # ハートの下部（尖った部分）
        heart_points.append((x, y + size//2))
        
        # 右側の円弧
        for angle in range(180, 0, -10):
            rad = math.radians(angle)
            right_x = x + size//2 + math.cos(rad) * size//3
            right_y = y - size//4 + math.sin(rad) * size//3
            heart_points.append((right_x, right_y))
        
        if len(heart_points) > 2:
            pygame.draw.polygon(surface, color, heart_points)
    
    def _draw_decorative_elements(self, surface: pygame.Surface):
        """装飾要素を描画"""
        # 分割線
        divider_color = (80, 70, 60)
        
        # HP/エネルギー間
        pygame.draw.line(surface, divider_color, (180, 10), (180, self.bar_height - 10), 1)
        
        # エネルギー/ゴールド間
        pygame.draw.line(surface, divider_color, (360, 10), (360, self.bar_height - 10), 1)
        
        # ゴールド/フロア間
        pygame.draw.line(surface, divider_color, (SCREEN_WIDTH - 140, 10), (SCREEN_WIDTH - 140, self.bar_height - 10), 1)
        
        # 装飾的な角
        corner_color = (100, 90, 80)
        corner_size = 8
        
        # 左上角
        pygame.draw.polygon(surface, corner_color, [
            (0, 0), (corner_size, 0), (0, corner_size)
        ])
        
        # 右上角
        pygame.draw.polygon(surface, corner_color, [
            (SCREEN_WIDTH, 0), (SCREEN_WIDTH - corner_size, 0), (SCREEN_WIDTH, corner_size)
        ])