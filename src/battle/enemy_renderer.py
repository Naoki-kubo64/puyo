"""
敵ビジュアル描画システム
pygame描画関数を使用して各敵タイプの見た目を作成
"""

import pygame
import math
from typing import Tuple
from .enemy import EnemyType
from core.constants import Colors

class EnemyRenderer:
    """敵の描画を担当するクラス"""
    
    @staticmethod
    def draw_enemy(surface: pygame.Surface, enemy_type: EnemyType, 
                   x: int, y: int, width: int, height: int, 
                   hp_ratio: float = 1.0, is_selected: bool = False):
        """敵を描画する"""
        
        # 中央座標計算
        center_x = x + width // 2
        center_y = y + height // 2
        
        # 選択時のエフェクトは削除（シンプルに）
        
        # HP低下時の赤みエフェクト
        damage_alpha = int((1.0 - hp_ratio) * 100)
        
        # 敵タイプ別描画
        if enemy_type == EnemyType.SLIME:
            EnemyRenderer._draw_slime(surface, center_x, center_y, hp_ratio, damage_alpha)
        elif enemy_type == EnemyType.GOBLIN:
            EnemyRenderer._draw_goblin(surface, center_x, center_y, hp_ratio, damage_alpha)
        elif enemy_type == EnemyType.ORC:
            EnemyRenderer._draw_orc(surface, center_x, center_y, hp_ratio, damage_alpha)
        elif enemy_type == EnemyType.GOLEM:
            EnemyRenderer._draw_golem(surface, center_x, center_y, hp_ratio, damage_alpha)
        elif enemy_type == EnemyType.MAGE:
            EnemyRenderer._draw_mage(surface, center_x, center_y, hp_ratio, damage_alpha)
        elif enemy_type == EnemyType.DRAGON:
            EnemyRenderer._draw_dragon(surface, center_x, center_y, hp_ratio, damage_alpha)
        elif enemy_type == EnemyType.BOSS_DEMON:
            EnemyRenderer._draw_boss_demon(surface, center_x, center_y, hp_ratio, damage_alpha)
    
    @staticmethod
    def _draw_slime(surface: pygame.Surface, center_x: int, center_y: int, 
                    hp_ratio: float, damage_alpha: int):
        """スライムを描画（画像使用）"""
        try:
            import os
            # slime.png画像を読み込み
            image_path = os.path.join(os.path.dirname(__file__), '..', '..', 'slime.png')
            slime_image = pygame.image.load(image_path)
            # 敵のサイズに合わせてスケール（240x240）
            slime_image = pygame.transform.scale(slime_image, (240, 240))
            
            # HPが低い場合は赤みがかった効果
            if hp_ratio < 0.5:
                # 赤いオーバーレイを作成
                red_overlay = pygame.Surface((240, 240))
                red_overlay.set_alpha(int((1.0 - hp_ratio) * 100))
                red_overlay.fill((255, 100, 100))
                slime_image.blit(red_overlay, (0, 0))
            
            # 中央に配置するため位置調整
            surface.blit(slime_image, (center_x - 120, center_y - 120))
            print(f"Slime image loaded successfully from {image_path}")
        except Exception as e:
            print(f"Failed to load slime image: {e}, using fallback drawing")
            # フォールバック：従来の描画方式
            # 本体（緑の円）
            body_color = (50, 200, 50) if hp_ratio > 0.3 else (200, 100, 50)
            pygame.draw.circle(surface, body_color, (center_x, center_y + 10), 35)
            
            # ハイライト（光沢感）
            pygame.draw.circle(surface, (100, 255, 100), (center_x - 10, center_y), 15)
            
            # 目
            pygame.draw.circle(surface, Colors.BLACK, (center_x - 12, center_y - 5), 6)
            pygame.draw.circle(surface, Colors.BLACK, (center_x + 12, center_y - 5), 6)
            pygame.draw.circle(surface, Colors.WHITE, (center_x - 10, center_y - 7), 3)
            pygame.draw.circle(surface, Colors.WHITE, (center_x + 14, center_y - 7), 3)
            
            # 口
            if hp_ratio > 0.5:
                # 元気な笑顔
                pygame.draw.arc(surface, Colors.BLACK, 
                              pygame.Rect(center_x - 10, center_y + 5, 20, 15), 
                              0, math.pi, 3)
            else:
                # ダメージ時の困った顔
                pygame.draw.arc(surface, Colors.BLACK, 
                              pygame.Rect(center_x - 10, center_y + 15, 20, 10), 
                              math.pi, 2 * math.pi, 3)
    
    @staticmethod
    def _draw_goblin(surface: pygame.Surface, center_x: int, center_y: int, 
                     hp_ratio: float, damage_alpha: int):
        """ゴブリンを描画（画像使用）"""
        try:
            import os
            # goblin.png画像を読み込み
            image_path = os.path.join(os.path.dirname(__file__), '..', '..', 'goblin.png')
            goblin_image = pygame.image.load(image_path)
            # ゴブリンをさらに大きく表示（280x280）
            goblin_image = pygame.transform.scale(goblin_image, (280, 280))
            
            # HPが低い場合は赤みがかった効果
            if hp_ratio < 0.5:
                # 赤いオーバーレイを作成（サイズ変更）
                red_overlay = pygame.Surface((280, 280))
                red_overlay.set_alpha(int((1.0 - hp_ratio) * 100))
                red_overlay.fill((255, 100, 100))
                goblin_image.blit(red_overlay, (0, 0))
            
            # 中央に配置するため位置調整（サイズ増加に合わせて）
            surface.blit(goblin_image, (center_x - 140, center_y - 140))
            print(f"Goblin image loaded successfully from {image_path}")
        except Exception as e:
            print(f"Failed to load goblin image: {e}, using fallback drawing")
            # フォールバック：従来の描画方式
            # 頭（緑の楕円）
            head_color = (80, 150, 80) if hp_ratio > 0.3 else (150, 100, 80)
            pygame.draw.ellipse(surface, head_color, 
                              pygame.Rect(center_x - 20, center_y - 30, 40, 35))
            
            # 体（小さい楕円）
            body_color = (100, 100, 60) if hp_ratio > 0.3 else (150, 100, 60)
            pygame.draw.ellipse(surface, body_color, 
                              pygame.Rect(center_x - 15, center_y - 5, 30, 40))
            
            # 耳（尖った三角）
            ear_color = head_color
            ear_points = [
                (center_x - 25, center_y - 20),
                (center_x - 35, center_y - 35),
                (center_x - 20, center_y - 25)
            ]
            pygame.draw.polygon(surface, ear_color, ear_points)
            
            ear_points2 = [
                (center_x + 25, center_y - 20),
                (center_x + 35, center_y - 35),
                (center_x + 20, center_y - 25)
            ]
            pygame.draw.polygon(surface, ear_color, ear_points2)
            
            # 目（赤い小さい円）
            pygame.draw.circle(surface, Colors.RED, (center_x - 8, center_y - 18), 4)
            pygame.draw.circle(surface, Colors.RED, (center_x + 8, center_y - 18), 4)
            
            # 武器（簡単な棒）
            weapon_color = (139, 69, 19)  # 茶色
            pygame.draw.line(surface, weapon_color, 
                            (center_x + 25, center_y - 10), 
                            (center_x + 35, center_y - 25), 4)
    
    @staticmethod
    def _draw_orc(surface: pygame.Surface, center_x: int, center_y: int, 
                  hp_ratio: float, damage_alpha: int):
        """オークを描画（画像使用）"""
        try:
            import os
            # オーク.png画像を読み込み
            image_path = os.path.join(os.path.dirname(__file__), '..', '..', 'オーク.png')
            orc_image = pygame.image.load(image_path)
            # 敵のサイズに合わせてスケール（240x240）
            orc_image = pygame.transform.scale(orc_image, (240, 240))
            
            # HPが低い場合は赤みがかった効果
            if hp_ratio < 0.5:
                # 赤いオーバーレイを作成
                red_overlay = pygame.Surface((240, 240))
                red_overlay.set_alpha(int((1.0 - hp_ratio) * 100))
                red_overlay.fill((255, 100, 100))
                orc_image.blit(red_overlay, (0, 0))
            
            # 中央に配置するため位置調整
            surface.blit(orc_image, (center_x - 120, center_y - 120))
            print(f"Orc image loaded successfully from {image_path}")
        except Exception as e:
            print(f"Failed to load orc image: {e}, using fallback drawing")
            # フォールバック：従来の描画方式
            # 頭（大きい緑の円）
            head_color = (60, 120, 60) if hp_ratio > 0.3 else (120, 80, 60)
            pygame.draw.circle(surface, head_color, (center_x, center_y - 15), 25)
        
        # 体（大きい長方形）
        body_color = (80, 80, 40) if hp_ratio > 0.3 else (120, 80, 40)
        pygame.draw.rect(surface, body_color, 
                        pygame.Rect(center_x - 20, center_y + 5, 40, 50))
        
        # 牙
        tusk_color = Colors.WHITE
        pygame.draw.polygon(surface, tusk_color, [
            (center_x - 8, center_y - 5),
            (center_x - 12, center_y + 5),
            (center_x - 5, center_y + 2)
        ])
        pygame.draw.polygon(surface, tusk_color, [
            (center_x + 8, center_y - 5),
            (center_x + 12, center_y + 5),
            (center_x + 5, center_y + 2)
        ])
        
        # 目（怒った赤い目）
        pygame.draw.circle(surface, Colors.RED, (center_x - 10, center_y - 20), 5)
        pygame.draw.circle(surface, Colors.RED, (center_x + 10, center_y - 20), 5)
        pygame.draw.circle(surface, Colors.BLACK, (center_x - 10, center_y - 20), 3)
        pygame.draw.circle(surface, Colors.BLACK, (center_x + 10, center_y - 20), 3)
        
        # 腕（筋肉質）
        arm_color = head_color
        pygame.draw.ellipse(surface, arm_color, 
                          pygame.Rect(center_x - 35, center_y + 10, 15, 30))
        pygame.draw.ellipse(surface, arm_color, 
                          pygame.Rect(center_x + 20, center_y + 10, 15, 30))
    
    @staticmethod
    def _draw_golem(surface: pygame.Surface, center_x: int, center_y: int, 
                    hp_ratio: float, damage_alpha: int):
        """ゴーレムを描画（画像使用）"""
        try:
            import os
            # ゴーレム.png画像を読み込み
            image_path = os.path.join(os.path.dirname(__file__), '..', '..', 'ゴーレム.png')
            golem_image = pygame.image.load(image_path)
            # 敵のサイズに合わせてスケール（240x240）
            golem_image = pygame.transform.scale(golem_image, (240, 240))
            
            # HPが低い場合は赤みがかった効果
            if hp_ratio < 0.5:
                # 赤いオーバーレイを作成
                red_overlay = pygame.Surface((240, 240))
                red_overlay.set_alpha(int((1.0 - hp_ratio) * 100))
                red_overlay.fill((255, 100, 100))
                golem_image.blit(red_overlay, (0, 0))
            
            # 中央に配置するため位置調整
            surface.blit(golem_image, (center_x - 120, center_y - 120))
            print(f"Golem image loaded successfully from {image_path}")
        except Exception as e:
            print(f"Failed to load golem image: {e}, using fallback drawing")
            # フォールバック：従来の描画方式
            # 本体（石っぽい灰色の四角）
            body_color = (120, 120, 120) if hp_ratio > 0.3 else (100, 100, 100)
            pygame.draw.rect(surface, body_color, 
                            pygame.Rect(center_x - 25, center_y - 20, 50, 60))
        
        # 石の質感（線）
        line_color = (80, 80, 80)
        for i in range(3):
            y_pos = center_y - 10 + i * 15
            pygame.draw.line(surface, line_color, 
                           (center_x - 20, y_pos), (center_x + 20, y_pos), 2)
        
        # 頭（小さい四角）
        head_color = body_color
        pygame.draw.rect(surface, head_color, 
                        pygame.Rect(center_x - 15, center_y - 35, 30, 20))
        
        # 目（光る青い点）
        pygame.draw.circle(surface, Colors.CYAN, (center_x - 8, center_y - 25), 4)
        pygame.draw.circle(surface, Colors.CYAN, (center_x + 8, center_y - 25), 4)
        pygame.draw.circle(surface, Colors.WHITE, (center_x - 8, center_y - 25), 2)
        pygame.draw.circle(surface, Colors.WHITE, (center_x + 8, center_y - 25), 2)
        
        # 腕（太い四角）
        pygame.draw.rect(surface, body_color, 
                        pygame.Rect(center_x - 40, center_y - 5, 15, 35))
        pygame.draw.rect(surface, body_color, 
                        pygame.Rect(center_x + 25, center_y - 5, 15, 35))
    
    @staticmethod
    def _draw_mage(surface: pygame.Surface, center_x: int, center_y: int, 
                   hp_ratio: float, damage_alpha: int):
        """魔導士を描画（画像使用）"""
        try:
            import os
            # mahou.png画像を読み込み
            image_path = os.path.join(os.path.dirname(__file__), '..', '..', 'mahou.png')
            mage_image = pygame.image.load(image_path)
            # 敵のサイズに合わせてスケール（240x240）
            mage_image = pygame.transform.scale(mage_image, (240, 240))
            
            # HPが低い場合は赤みがかった効果
            if hp_ratio < 0.5:
                # 赤いオーバーレイを作成
                red_overlay = pygame.Surface((240, 240))
                red_overlay.set_alpha(int((1.0 - hp_ratio) * 100))
                red_overlay.fill((255, 100, 100))
                mage_image.blit(red_overlay, (0, 0))
            
            # 中央に配置するため位置調整
            surface.blit(mage_image, (center_x - 120, center_y - 120))
            print(f"Mage image loaded successfully from {image_path}")
        except Exception as e:
            print(f"Failed to load mage image: {e}, using fallback drawing")
            # フォールバック：従来の描画方式
            # ローブ（青い三角形）
            robe_color = (50, 50, 200) if hp_ratio > 0.3 else (150, 50, 100)
            robe_points = [
                (center_x, center_y - 30),
                (center_x - 30, center_y + 40),
                (center_x + 30, center_y + 40)
            ]
            pygame.draw.polygon(surface, robe_color, robe_points)
        
        # 顔（肌色の円）
        face_color = (255, 220, 177)
        pygame.draw.circle(surface, face_color, (center_x, center_y - 15), 12)
        
        # 帽子（青い三角）
        hat_color = robe_color
        hat_points = [
            (center_x, center_y - 40),
            (center_x - 15, center_y - 25),
            (center_x + 15, center_y - 25)
        ]
        pygame.draw.polygon(surface, hat_color, hat_points)
        
        # 星（帽子の装飾）
        star_color = Colors.YELLOW
        pygame.draw.circle(surface, star_color, (center_x, center_y - 35), 3)
        
        # 目
        pygame.draw.circle(surface, Colors.BLACK, (center_x - 5, center_y - 18), 2)
        pygame.draw.circle(surface, Colors.BLACK, (center_x + 5, center_y - 18), 2)
        
        # 杖
        staff_color = (139, 69, 19)
        pygame.draw.line(surface, staff_color, 
                        (center_x + 20, center_y - 20), 
                        (center_x + 25, center_y + 30), 4)
        # 杖の先端（魔法の球）
        pygame.draw.circle(surface, Colors.PURPLE, (center_x + 22, center_y - 22), 6)
        pygame.draw.circle(surface, Colors.WHITE, (center_x + 22, center_y - 22), 3)
    
    @staticmethod
    def _draw_dragon(surface: pygame.Surface, center_x: int, center_y: int, 
                     hp_ratio: float, damage_alpha: int):
        """ドラゴンを描画（画像使用）"""
        try:
            import os
            # ドラゴン.png画像を読み込み
            image_path = os.path.join(os.path.dirname(__file__), '..', '..', 'ドラゴン.png')
            dragon_image = pygame.image.load(image_path)
            # 敵のサイズに合わせてスケール（240x240）
            dragon_image = pygame.transform.scale(dragon_image, (240, 240))
            
            # HPが低い場合は赤みがかった効果
            if hp_ratio < 0.5:
                # 赤いオーバーレイを作成
                red_overlay = pygame.Surface((240, 240))
                red_overlay.set_alpha(int((1.0 - hp_ratio) * 100))
                red_overlay.fill((255, 100, 100))
                dragon_image.blit(red_overlay, (0, 0))
            
            # 中央に配置するため位置調整
            surface.blit(dragon_image, (center_x - 120, center_y - 120))
            print(f"Dragon image loaded successfully from {image_path}")
        except Exception as e:
            print(f"Failed to load dragon image: {e}, using fallback drawing")
            # フォールバック：従来の描画方式
            # 体（大きい赤い楕円）
            body_color = (200, 50, 50) if hp_ratio > 0.3 else (150, 100, 100)
            pygame.draw.ellipse(surface, body_color, 
                              pygame.Rect(center_x - 30, center_y - 10, 60, 40))
        
        # 頭（三角っぽい形）
        head_points = [
            (center_x - 35, center_y - 5),
            (center_x - 50, center_y - 20),
            (center_x - 30, center_y - 25),
            (center_x - 20, center_y - 15)
        ]
        pygame.draw.polygon(surface, body_color, head_points)
        
        # 翼（大きい三角形）
        wing_color = (150, 30, 30)
        wing1_points = [
            (center_x - 10, center_y - 20),
            (center_x - 40, center_y - 40),
            (center_x + 10, center_y - 15)
        ]
        pygame.draw.polygon(surface, wing_color, wing1_points)
        
        wing2_points = [
            (center_x + 10, center_y - 20),
            (center_x + 40, center_y - 40),
            (center_x - 10, center_y - 15)
        ]
        pygame.draw.polygon(surface, wing_color, wing2_points)
        
        # 目（黄色い爬虫類の目）
        pygame.draw.circle(surface, Colors.YELLOW, (center_x - 35, center_y - 15), 6)
        pygame.draw.ellipse(surface, Colors.BLACK, 
                          pygame.Rect(center_x - 38, center_y - 18, 6, 12))
        
        # 尻尾
        tail_color = body_color
        pygame.draw.ellipse(surface, tail_color, 
                          pygame.Rect(center_x + 25, center_y + 10, 20, 10))
        
        # 火（息）
        if hp_ratio > 0.5:  # 元気なときのみ
            fire_colors = [Colors.RED, Colors.ORANGE, Colors.YELLOW]
            for i, color in enumerate(fire_colors):
                pygame.draw.circle(surface, color, 
                                 (center_x - 55 + i * 3, center_y - 10), 3 - i)
    
    @staticmethod
    def _draw_boss_demon(surface: pygame.Surface, center_x: int, center_y: int, 
                         hp_ratio: float, damage_alpha: int):
        """ボス魔王を描画（画像使用）"""
        try:
            import os
            # boss.png画像を読み込み
            image_path = os.path.join(os.path.dirname(__file__), '..', '..', 'boss.png')
            boss_image = pygame.image.load(image_path)
            # 敵のサイズに合わせてスケール（240x240）
            boss_image = pygame.transform.scale(boss_image, (240, 240))
            
            # HPが低い場合は赤みがかった効果
            if hp_ratio < 0.5:
                # 赤いオーバーレイを作成
                red_overlay = pygame.Surface((240, 240))
                red_overlay.set_alpha(int((1.0 - hp_ratio) * 100))
                red_overlay.fill((255, 100, 100))
                boss_image.blit(red_overlay, (0, 0))
            
            # 中央に配置するため位置調整
            surface.blit(boss_image, (center_x - 120, center_y - 120))
            print(f"Boss image loaded successfully from {image_path}")
        except Exception as e:
            print(f"Failed to load boss image: {e}, using fallback drawing")
            # フォールバック：従来の描画方式
            # 体（大きい黒い人型）
            body_color = (50, 0, 50) if hp_ratio > 0.3 else (100, 50, 50)
            pygame.draw.ellipse(surface, body_color, 
                              pygame.Rect(center_x - 25, center_y - 15, 50, 70))
            
            # 頭（角の生えた頭）
            head_color = (80, 0, 80)
            pygame.draw.circle(surface, head_color, (center_x, center_y - 20), 20)
            
            # 角
            horn_color = Colors.BLACK
            horn1_points = [
                (center_x - 15, center_y - 30),
                (center_x - 20, center_y - 45),
                (center_x - 10, center_y - 35)
            ]
            pygame.draw.polygon(surface, horn_color, horn1_points)
            
            horn2_points = [
                (center_x + 15, center_y - 30),
                (center_x + 20, center_y - 45),
                (center_x + 10, center_y - 35)
            ]
            pygame.draw.polygon(surface, horn_color, horn2_points)
            
            # 目（赤く光る）
            pygame.draw.circle(surface, Colors.RED, (center_x - 8, center_y - 25), 6)
            pygame.draw.circle(surface, Colors.RED, (center_x + 8, center_y - 25), 6)
            pygame.draw.circle(surface, Colors.WHITE, (center_x - 8, center_y - 25), 2)
            pygame.draw.circle(surface, Colors.WHITE, (center_x + 8, center_y - 25), 2)
            
            # 腕（太くて長い）
            arm_color = body_color
            pygame.draw.ellipse(surface, arm_color, 
                              pygame.Rect(center_x - 45, center_y - 5, 20, 40))
            pygame.draw.ellipse(surface, arm_color, 
                              pygame.Rect(center_x + 25, center_y - 5, 20, 40))
            
            # 邪悪なオーラ（紫の輪）
            if hp_ratio > 0.7:  # 元気なときのみ
                aura_color = (100, 0, 100, 100)  # 半透明紫
                pygame.draw.circle(surface, Colors.PURPLE, 
                                 (center_x, center_y), 60, 3)
                pygame.draw.circle(surface, Colors.PURPLE, 
                                 (center_x, center_y), 70, 2)