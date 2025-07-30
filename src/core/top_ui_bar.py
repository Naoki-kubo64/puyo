"""
上部UIバーシステム
Slay the Spireスタイルの美しい上部UI表示
"""

import pygame
import math
import os
import logging
from typing import Dict, Optional
from .constants import Colors, SCREEN_WIDTH, FONT_SIZE_SMALL, FONT_SIZE_MEDIUM
from .game_engine import get_appropriate_font

logger = logging.getLogger(__name__)

class TopUIBar:
    """上部UIバーの描画と管理を担当するクラス"""
    
    def __init__(self, fonts: Dict[str, pygame.font.Font]):
        """上部UIバーを初期化"""
        self.fonts = fonts
        self.bar_height = 60
        self.animation_time = 0
        
        # UI要素の位置
        self.hp_icon_pos = (20, 15)
        self.gold_icon_pos = (380, 15)
        self.potion_pos = (530, 15)  # ポーション表示位置
        self.special_puyo_pos = (700, 15)  # 特殊ぷよ表示位置（右にずらす）
        self.floor_icon_pos = (SCREEN_WIDTH - 120, 15)
        
        # アニメーション用
        self.hp_pulse = 0
        self.damage_flash = 0
        
        # アイコン画像を読み込み
        self.hp_icon = None
        self.gold_icon = None
        self.special_puyo_icons = {}  # 特殊ぷよアイコン辞書
        self._load_icons()
        
        # マウスオーバー用
        self.hover_info = None
        self.last_mouse_pos = (0, 0)
    
    def update(self, dt: float):
        """UIアニメーションを更新"""
        self.animation_time += dt
        self.hp_pulse = abs(math.sin(self.animation_time * 2))
        
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
            
            # 特殊ぷよアイコンを読み込み
            picture_path = os.path.join(base_path, "assets")
            
            special_puyo_files = {
                "heal": "HEAL.png",
                "bomb": "BOMB.png",
                "lightning": "LIGHTNING.png",
                "shield": "SHIELD.png",
                "multiplier": "Multiplier.png",
                "poison": "POISON.png"
            }
            
            for puyo_type, filename in special_puyo_files.items():
                icon_path = os.path.join(picture_path, filename)
                if os.path.exists(icon_path):
                    icon = pygame.image.load(icon_path).convert_alpha()
                    # UIバー用に小さくリサイズ（20x20ピクセル）
                    self.special_puyo_icons[puyo_type] = pygame.transform.scale(icon, (20, 20))
                
        except Exception as e:
            print(f"Warning: Could not load UI icons: {e}")
    
    def trigger_damage_flash(self):
        """ダメージを受けた時のフラッシュエフェクト"""
        self.damage_flash = 1.0
    
    def draw_top_bar(self, surface: pygame.Surface, player_hp: int, player_max_hp: int, 
                     gold: int, floor: int, special_puyo_rates: dict = None, player_inventory=None):
        """上部UIバーを描画"""
        # 背景バー
        self._draw_background_bar(surface)
        
        # HP表示
        self._draw_hp_display(surface, player_hp, player_max_hp)
        
        # エネルギー表示（削除済み）
        # self._draw_energy_display(surface, energy, max_energy)
        
        # ゴールド表示
        self._draw_gold_display(surface, gold)
        
        # ポーション表示
        if player_inventory:
            self._draw_potion_display(surface, player_inventory)
        
        # 特殊ぷよ表示
        if special_puyo_rates:
            self._draw_special_puyo_display(surface, special_puyo_rates)
        
        # フロア表示
        self._draw_floor_display(surface, floor)
        
        # 装飾エレメント
        self._draw_decorative_elements(surface)
        
        # マウスオーバー情報表示
        if self.hover_info:
            self._draw_hover_tooltip(surface)
    
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
    
    def _draw_special_puyo_display(self, surface: pygame.Surface, special_puyo_rates: dict):
        """特殊ぷよ表示を描画"""
        x, y = self.special_puyo_pos
        
        # 特殊ぷよ表示処理開始
        
        # "Special Puyos" ラベル
        label_font = get_appropriate_font(self.fonts, "Special", 'small')
        label_surface = label_font.render("Special", True, Colors.LIGHT_GRAY)
        surface.blit(label_surface, (x, y - 5))
        
        # 特殊ぷよアイコンを横に並べて表示
        icon_spacing = 30
        current_x = x
        
        # 出現率が0%より大きい特殊ぷよのみ表示
        displayed_count = 0
        for puyo_type, rate in special_puyo_rates.items():
            if rate > 0.0 and puyo_type in self.special_puyo_icons:
                icon = self.special_puyo_icons[puyo_type]
                icon_rect = pygame.Rect(current_x, y + 12, 20, 20)
                
                # アイコンを描画
                surface.blit(icon, icon_rect)
                
                # 出現率をパーセントで表示
                rate_text = f"{rate*100:.0f}%"
                rate_font = get_appropriate_font(self.fonts, rate_text, 'small')
                rate_surface = rate_font.render(rate_text, True, Colors.WHITE)
                surface.blit(rate_surface, (current_x, y + 35))
                
                # マウスオーバー検出領域を記録
                hover_rect = pygame.Rect(current_x - 5, y + 10, 30, 30)
                mouse_pos = pygame.mouse.get_pos()
                if hover_rect.collidepoint(mouse_pos):
                    self.hover_info = {
                        'type': puyo_type,
                        'rate': rate,
                        'pos': (mouse_pos[0] + 10, mouse_pos[1] - 40)
                    }
                
                current_x += icon_spacing
                displayed_count += 1
        
        # 特殊ぷよを持っていない場合は「なし」と表示
        if displayed_count == 0:
            no_special_font = get_appropriate_font(self.fonts, "なし", 'small')
            no_special_surface = no_special_font.render("なし", True, Colors.GRAY)
            surface.blit(no_special_surface, (current_x, y + 20))
    
    def _draw_potion_display(self, surface: pygame.Surface, player_inventory):
        """ポーション表示を描画"""
        x, y = self.potion_pos
        
        # "Potions" ラベル（より明るくして視認性向上）
        label_font = get_appropriate_font(self.fonts, "Potions", 'small')
        label_surface = label_font.render("Potions", True, Colors.WHITE)
        surface.blit(label_surface, (x, y - 5))
        
        # ポーションを取得
        from inventory.player_inventory import ItemType
        potions = player_inventory.get_items_by_type(ItemType.POTION)
        
        # ポーションアイコンを横に並べて表示
        icon_spacing = 35
        current_x = x
        
        if potions:
            for i, potion in enumerate(potions[:4]):  # 最大4個まで表示
                if i >= 4:  # 4個以上は省略
                    break
                
                # ポーションアイコン（簡単な円で表現） - サイズを大きくして視認性向上
                potion_rect = pygame.Rect(current_x, y + 12, 28, 28)
                
                # レアリティに応じた色（視認性向上のため明るく調整）
                if hasattr(potion.rarity, 'color'):
                    base_color = potion.rarity.color
                    # 色を明るくして視認性を向上
                    potion_color = tuple(min(255, int(c * 1.5)) for c in base_color)
                else:
                    potion_color = (0, 255, 0)  # 明るい緑
                
                # 背景として暗い縁を描画（サイズ増加）
                pygame.draw.circle(surface, (50, 50, 50), potion_rect.center, 16)
                # メインのポーション円（サイズ増加）
                pygame.draw.circle(surface, potion_color, potion_rect.center, 14)
                # 白い縁（サイズ増加）
                pygame.draw.circle(surface, Colors.WHITE, potion_rect.center, 14, 2)
                
                # 数量表示
                if potion.quantity > 1:
                    qty_font = get_appropriate_font(self.fonts, str(potion.quantity), 'small')
                    qty_surface = qty_font.render(str(potion.quantity), True, Colors.WHITE)
                    surface.blit(qty_surface, (current_x + 18, y + 30))
                
                # クリック判定エリアを記録
                potion_click_rect = pygame.Rect(current_x - 5, y + 10, 30, 30)
                if hasattr(self, 'potion_click_areas'):
                    self.potion_click_areas.append((potion_click_rect, potion.id))
                else:
                    self.potion_click_areas = [(potion_click_rect, potion.id)]
                
                # マウスオーバー検出
                mouse_pos = pygame.mouse.get_pos()
                if potion_click_rect.collidepoint(mouse_pos):
                    self.hover_info = {
                        'type': 'potion',
                        'item': potion,
                        'pos': (mouse_pos[0] + 10, mouse_pos[1] - 40)
                    }
                
                current_x += icon_spacing
        else:
            # ポーションがない場合
            no_potion_font = get_appropriate_font(self.fonts, "なし", 'small')
            no_potion_surface = no_potion_font.render("なし", True, Colors.GRAY)
            surface.blit(no_potion_surface, (current_x, y + 20))
    
    def _draw_hover_tooltip(self, surface: pygame.Surface):
        """マウスオーバー時のツールチップを描画"""
        if not self.hover_info:
            return
        
        hover_type = self.hover_info['type']
        pos = self.hover_info['pos']
        
        if hover_type == 'potion':
            # ポーション情報
            potion = self.hover_info['item']
            effect_text = potion.description
            rate_text = f'クリックで使用 (x{potion.quantity})'
        else:
            # 特殊ぷよ情報
            puyo_type = hover_type
            rate = self.hover_info['rate']
            
            # 特殊ぷよの固有名前と効果説明
            effects = {
                'heal': 'ヒールぷよ: プレイヤーのHPを10回復',
                'bomb': 'ボムぷよ: 全ての敵に攻撃',
                'lightning': 'サンダーぷよ: 最強の敵1体に強力攻撃',
                'shield': 'シールドぷよ: ダメージを15軽減', 
                'multiplier': 'パワーぷよ: 攻撃力を50%上昇',
                'poison': 'ポイズンぷよ: 全ての敵に継続ダメージ'
            }
            
            effect_text = effects.get(puyo_type, '特殊効果')
            rate_text = f'出現率: {rate*100:.0f}%'
        
        # ツールチップの背景サイズを計算
        font = get_appropriate_font(self.fonts, effect_text, 'small')
        effect_surface = font.render(effect_text, True, Colors.WHITE)
        rate_surface = font.render(rate_text, True, Colors.WHITE)
        
        tooltip_width = max(effect_surface.get_width(), rate_surface.get_width()) + 20
        tooltip_height = 50
        
        # ツールチップの背景
        tooltip_rect = pygame.Rect(pos[0], pos[1], tooltip_width, tooltip_height)
        pygame.draw.rect(surface, (40, 40, 40), tooltip_rect)
        pygame.draw.rect(surface, (100, 100, 100), tooltip_rect, 1)
        
        # テキストを描画
        surface.blit(effect_surface, (pos[0] + 10, pos[1] + 5))
        surface.blit(rate_surface, (pos[0] + 10, pos[1] + 25))
    
    def handle_mouse_motion(self, mouse_pos: tuple):
        """マウス移動イベント処理"""
        self.last_mouse_pos = mouse_pos
        # hover_infoは_draw_special_puyo_displayや_draw_potion_displayで更新される
        self.hover_info = None
        # ポーションクリックエリアもクリア
        if hasattr(self, 'potion_click_areas'):
            self.potion_click_areas = []
    
    def handle_potion_click(self, mouse_pos: tuple, player_inventory, player_data):
        """ポーションクリック処理"""
        if not hasattr(self, 'potion_click_areas'):
            return False
        
        for click_rect, potion_id in self.potion_click_areas:
            if click_rect.collidepoint(mouse_pos):
                # ポーションを使用
                used_potion = player_inventory.use_consumable(potion_id)
                if used_potion:
                    self._apply_potion_effect(used_potion, player_data)
                    return True
        return False
    
    def _apply_potion_effect(self, potion, player_data):
        """ポーション効果を適用"""
        try:
            if "health" in potion.id:
                # HP回復ポーション
                heal_amount = potion.effect_value
                player_data.heal(heal_amount)
                logger.info(f"Used {potion.name}: Healed {heal_amount} HP")
            elif "strength" in potion.id:
                # 攻撃力強化ポーション
                bonus = potion.effect_value / 100.0  # %を小数に変換
                player_data.chain_damage_multiplier += bonus
                logger.info(f"Used {potion.name}: Damage +{potion.effect_value}%")
            else:
                logger.info(f"Used {potion.name}: {potion.description}")
        except Exception as e:
            logger.error(f"Error applying potion effect: {e}")