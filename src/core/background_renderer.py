"""
背景描画システム
Slay the Spireスタイルの美しいダンジョン背景を描画
"""

import pygame
import math
import random
from typing import List, Tuple
from .constants import Colors, SCREEN_WIDTH, SCREEN_HEIGHT

class BackgroundRenderer:
    """ダンジョン背景の描画を担当するクラス"""
    
    def __init__(self):
        """背景レンダラーを初期化"""
        self.time = 0
        
        # 背景画像を読み込み
        try:
            import os
            # プロジェクトルートの背景.pngを使用
            image_path = os.path.join(os.path.dirname(__file__), '..', '..', 'assets', '背景.png')
            self.background_image = pygame.image.load(image_path)
            # 画面サイズに合わせてスケール
            self.background_image = pygame.transform.scale(self.background_image, (SCREEN_WIDTH, SCREEN_HEIGHT))
            print(f"Background image loaded successfully from {image_path}")
        except Exception as e:
            print(f"Failed to load background image: {e}")
            # 画像が読み込めない場合は従来の描画方式
            self.background_image = None
            # パーティクル初期化
            self.floating_particles = []
            self._init_forest_particles()
    
    def _generate_forest_trees(self):
        """森の木々を生成"""
        for _ in range(12):
            tree = {
                'x': random.randint(-50, SCREEN_WIDTH + 50),
                'y': random.randint(SCREEN_HEIGHT // 2, SCREEN_HEIGHT - 100),
                'height': random.randint(200, 400),
                'width': random.randint(40, 80),
                'depth': random.uniform(0.3, 1.0)  # 奥行き感
            }
            self.trees.append(tree)
    
    def _generate_ancient_ruins(self):
        """古代遺跡の構造物を生成"""
        # 中央の大きなアーチ
        self.ruins.append({
            'type': 'arch',
            'x': SCREEN_WIDTH // 2,
            'y': SCREEN_HEIGHT // 2,
            'width': 120,
            'height': 150
        })
        
        # 小さな石柱や破片
        for _ in range(6):
            ruin = {
                'type': 'pillar',
                'x': random.randint(100, SCREEN_WIDTH - 100),
                'y': random.randint(SCREEN_HEIGHT // 2, SCREEN_HEIGHT - 50),
                'width': random.randint(20, 40),
                'height': random.randint(60, 120)
            }
            self.ruins.append(ruin)
    
    def _generate_light_rays(self):
        """森の光線を生成"""
        for _ in range(5):
            ray = {
                'x': random.randint(0, SCREEN_WIDTH),
                'y': 0,
                'angle': random.uniform(-0.3, 0.3),
                'width': random.randint(20, 40),
                'intensity': random.uniform(0.1, 0.3)
            }
            self.light_rays.append(ray)
    
    def _init_torch_flames(self):
        """松明の炎を初期化"""
        torch_positions = [
            (150, 80),
            (SCREEN_WIDTH - 150, 80),
            (300, 150),
            (SCREEN_WIDTH - 300, 150)
        ]
        
        for x, y in torch_positions:
            flame = {
                'x': x,
                'y': y,
                'particles': []
            }
            # 炎のパーティクルを作成
            for _ in range(15):
                particle = {
                    'x': x + random.uniform(-8, 8),
                    'y': y + random.uniform(0, 20),
                    'vx': random.uniform(-0.5, 0.5),
                    'vy': random.uniform(-2, -0.5),
                    'life': random.uniform(30, 60),
                    'max_life': 60,
                    'size': random.uniform(3, 8)
                }
                flame['particles'].append(particle)
            self.torch_flames.append(flame)
    
    def _init_particles(self):
        """環境パーティクル（埃など）を初期化"""
        for _ in range(20):
            particle = {
                'x': random.uniform(0, SCREEN_WIDTH),
                'y': random.uniform(0, SCREEN_HEIGHT),
                'vx': random.uniform(-0.2, 0.2),
                'vy': random.uniform(-0.1, 0.1),
                'size': random.uniform(1, 3),
                'alpha': random.uniform(20, 80),
                'life': random.uniform(200, 400)
            }
            self.particles.append(particle)
    
    def update(self, dt: float):
        """背景の更新"""
        self.time += dt
        
        # 画像背景の場合はパーティクル更新のみ
        if not self.background_image and hasattr(self, 'floating_particles'):
            self._update_forest_particles(dt)
    
    def _update_torch_flames(self, dt: float):
        """松明の炎を更新"""
        for flame in self.torch_flames:
            # 既存のパーティクルを更新
            for particle in flame['particles'][:]:
                particle['x'] += particle['vx']
                particle['y'] += particle['vy']
                particle['life'] -= dt * 60
                
                # 炎の上昇効果
                particle['vy'] -= 0.01
                particle['vx'] += random.uniform(-0.02, 0.02)
                
                if particle['life'] <= 0:
                    flame['particles'].remove(particle)
            
            # 新しいパーティクルを追加
            while len(flame['particles']) < 15:
                particle = {
                    'x': flame['x'] + random.uniform(-8, 8),
                    'y': flame['y'] + random.uniform(0, 20),
                    'vx': random.uniform(-0.5, 0.5),
                    'vy': random.uniform(-2, -0.5),
                    'life': random.uniform(30, 60),
                    'max_life': 60,
                    'size': random.uniform(3, 8)
                }
                flame['particles'].append(particle)
    
    def _update_particles(self, dt: float):
        """環境パーティクルを更新"""
        for particle in self.particles[:]:
            particle['x'] += particle['vx']
            particle['y'] += particle['vy']
            particle['life'] -= dt * 60
            
            # 画面外に出たら反対側に移動
            if particle['x'] < 0:
                particle['x'] = SCREEN_WIDTH
            elif particle['x'] > SCREEN_WIDTH:
                particle['x'] = 0
            
            if particle['y'] < 0:
                particle['y'] = SCREEN_HEIGHT
            elif particle['y'] > SCREEN_HEIGHT:
                particle['y'] = 0
            
            if particle['life'] <= 0:
                self.particles.remove(particle)
        
        # 新しいパーティクルを追加
        while len(self.particles) < 20:
            particle = {
                'x': random.uniform(0, SCREEN_WIDTH),
                'y': random.uniform(0, SCREEN_HEIGHT),
                'vx': random.uniform(-0.2, 0.2),
                'vy': random.uniform(-0.1, 0.1),
                'size': random.uniform(1, 3),
                'alpha': random.uniform(20, 80),
                'life': random.uniform(200, 400)
            }
            self.particles.append(particle)
    
    def draw_background(self, surface: pygame.Surface):
        """森の遺跡背景を描画"""
        if self.background_image:
            # 背景画像を描画
            surface.blit(self.background_image, (0, 0))
        else:
            # フォールバック：従来の描画方式
            self._draw_forest_background(surface)
            self._draw_forest_particles(surface)
    
    def _draw_base_background(self, surface: pygame.Surface):
        """ベース背景のグラデーション"""
        # ダークグラデーション
        for y in range(SCREEN_HEIGHT):
            ratio = y / SCREEN_HEIGHT
            # 上部は濃い青、下部は濃い茶色
            r = int(20 + ratio * 15)
            g = int(15 + ratio * 10)
            b = int(25 + ratio * 5)
            color = (r, g, b)
            pygame.draw.line(surface, color, (0, y), (SCREEN_WIDTH, y))
    
    def _draw_stone_walls(self, surface: pygame.Surface):
        """石壁のテクスチャ"""
        # 壁の石ブロック
        block_size = 60
        for x in range(0, SCREEN_WIDTH, block_size):
            for y in range(0, SCREEN_HEIGHT, block_size):
                # 石ブロックの輪郭
                offset_x = random.randint(-3, 3) if (x + y) % 120 == 0 else 0
                offset_y = random.randint(-3, 3) if (x + y) % 180 == 0 else 0
                
                block_rect = pygame.Rect(x + offset_x, y + offset_y, block_size - 2, block_size - 2)
                
                # ベース色（暗い灰色）
                base_color = (45, 40, 35)
                pygame.draw.rect(surface, base_color, block_rect)
                
                # ハイライト（上と左）
                highlight_color = (65, 60, 55)
                pygame.draw.line(surface, highlight_color, 
                               (block_rect.left, block_rect.top), 
                               (block_rect.right, block_rect.top), 1)
                pygame.draw.line(surface, highlight_color, 
                               (block_rect.left, block_rect.top), 
                               (block_rect.left, block_rect.bottom), 1)
                
                # シャドウ（下と右）
                shadow_color = (25, 20, 15)
                pygame.draw.line(surface, shadow_color, 
                               (block_rect.left, block_rect.bottom), 
                               (block_rect.right, block_rect.bottom), 1)
                pygame.draw.line(surface, shadow_color, 
                               (block_rect.right, block_rect.top), 
                               (block_rect.right, block_rect.bottom), 1)
    
    def _draw_torch_light(self, surface: pygame.Surface):
        """松明の光を描画"""
        for flame in self.torch_flames:
            # 光の円
            light_radius = 80 + math.sin(self.time * 3) * 10
            
            # グラデーション光
            for r in range(int(light_radius), 0, -5):
                alpha = max(0, int(30 * (1.0 - r / light_radius)))
                if alpha > 0:
                    # 光のサーフェス作成
                    light_surface = pygame.Surface((r*2, r*2))
                    light_surface.set_alpha(alpha)
                    light_color = (255, 180, 100)  # 暖かいオレンジ
                    pygame.draw.circle(light_surface, light_color, (r, r), r)
                    surface.blit(light_surface, (flame['x'] - r, flame['y'] - r))
    
    def _draw_wall_cracks(self, surface: pygame.Surface):
        """壁のひび割れを描画"""
        crack_color = (15, 10, 5)
        
        for crack in self.wall_cracks:
            start_x = crack['x']
            start_y = crack['y']
            
            # メインのひび割れ
            end_x = start_x + math.cos(crack['angle']) * crack['length']
            end_y = start_y + math.sin(crack['angle']) * crack['length']
            pygame.draw.line(surface, crack_color, (start_x, start_y), (end_x, end_y), 2)
            
            # 枝分かれ
            for i in range(crack['branches']):
                branch_angle = crack['angle'] + random.uniform(-0.5, 0.5)
                branch_length = crack['length'] * random.uniform(0.3, 0.7)
                branch_start_ratio = random.uniform(0.2, 0.8)
                
                branch_start_x = start_x + math.cos(crack['angle']) * crack['length'] * branch_start_ratio
                branch_start_y = start_y + math.sin(crack['angle']) * crack['length'] * branch_start_ratio
                branch_end_x = branch_start_x + math.cos(branch_angle) * branch_length
                branch_end_y = branch_start_y + math.sin(branch_angle) * branch_length
                
                pygame.draw.line(surface, crack_color, 
                               (branch_start_x, branch_start_y), 
                               (branch_end_x, branch_end_y), 1)
    
    def _draw_torch_flames(self, surface: pygame.Surface):
        """松明の炎を描画"""
        for flame in self.torch_flames:
            # 松明の柄
            torch_color = (60, 40, 20)
            torch_rect = pygame.Rect(flame['x'] - 3, flame['y'] + 10, 6, 30)
            pygame.draw.rect(surface, torch_color, torch_rect)
            
            # 炎のパーティクル
            for particle in flame['particles']:
                life_ratio = particle['life'] / particle['max_life']
                
                # 炎の色（赤→オレンジ→黄色）
                if life_ratio > 0.6:
                    color = (255, 100, 50)  # 赤
                elif life_ratio > 0.3:
                    color = (255, 150, 50)  # オレンジ
                else:
                    color = (255, 255, 100)  # 黄色
                
                # パーティクルサイズ
                size = int(particle['size'] * life_ratio)
                if size > 0:
                    pygame.draw.circle(surface, color, 
                                     (int(particle['x']), int(particle['y'])), size)
    
    def _draw_particles(self, surface: pygame.Surface):
        """環境パーティクル（埃）を描画"""
        for particle in self.particles:
            alpha = int(particle['alpha'])
            if alpha > 0:
                dust_color = (100, 90, 80)
                size = int(particle['size'])
                if size > 0:
                    # 半透明の埃
                    dust_surface = pygame.Surface((size*2, size*2))
                    dust_surface.set_alpha(alpha)
                    pygame.draw.circle(dust_surface, dust_color, (size, size), size)
                    surface.blit(dust_surface, (particle['x'] - size, particle['y'] - size))
    
    # 森の遺跡用描画メソッド
    def _draw_forest_background(self, surface: pygame.Surface):
        """森の遺跡背景（送っていただいた画像風）"""
        for y in range(SCREEN_HEIGHT):
            ratio = y / SCREEN_HEIGHT
            # 送っていただいた画像の色調：深い緑から暗い緑茶色へのグラデーション
            r = int(25 + ratio * 35)  # 25-60 (茶色っぽい要素)
            g = int(45 + ratio * 40)  # 45-85 (緑の主体)
            b = int(20 + ratio * 25)  # 20-45 (深い色調)
            color = (r, g, b)
            pygame.draw.line(surface, color, (0, y), (SCREEN_WIDTH, y))
        
        # 中央の明るい部分（遺跡への光）
        center_x = SCREEN_WIDTH // 2
        center_y = SCREEN_HEIGHT // 2
        for radius in range(150, 0, -10):
            alpha = int(15 * (150 - radius) / 150)
            if alpha > 0:
                light_surface = pygame.Surface((radius*2, radius*2))
                light_surface.set_alpha(alpha)
                light_color = (80, 120, 60)  # 薄い緑がかった光
                pygame.draw.circle(light_surface, light_color, (radius, radius), radius)
                surface.blit(light_surface, (center_x - radius, center_y - radius))
        
        # 石のアーチ風の構造物
        arch_color = (60, 80, 50)
        # 左の柱
        pygame.draw.rect(surface, arch_color, (center_x - 80, center_y, 20, 100))
        # 右の柱  
        pygame.draw.rect(surface, arch_color, (center_x + 60, center_y, 20, 100))
        # アーチ上部
        pygame.draw.arc(surface, arch_color, (center_x - 80, center_y - 40, 160, 80), 0, 3.14159, 8)
    
    def _draw_light_rays(self, surface: pygame.Surface):
        """森の光線を描画"""
        for ray in self.light_rays:
            # 光線の描画
            for i in range(ray['width']):
                alpha = int(ray['intensity'] * 255 * (1 - i / ray['width']))
                if alpha > 0:
                    ray_surface = pygame.Surface((3, SCREEN_HEIGHT))
                    ray_surface.set_alpha(alpha)
                    ray_surface.fill((200, 255, 150))
                    
                    x = ray['x'] + i - ray['width']//2 + int(ray['y'] * ray['angle'])
                    surface.blit(ray_surface, (x, 0))
    
    def _draw_background_trees(self, surface: pygame.Surface):
        """奥の木々を描画"""
        for tree in self.trees:
            if tree['depth'] < 0.6:  # 奥の木のみ
                alpha = int(80 * tree['depth'])
                tree_color = (30, 60, 25)
                
                # 木の幹
                trunk_rect = pygame.Rect(
                    tree['x'] - tree['width']//4,
                    tree['y'],
                    tree['width']//2,
                    tree['height']//3
                )
                
                tree_surface = pygame.Surface(trunk_rect.size)
                tree_surface.set_alpha(alpha)
                tree_surface.fill(tree_color)
                surface.blit(tree_surface, trunk_rect)
    
    def _draw_ancient_ruins(self, surface: pygame.Surface):
        """古代遺跡を描画"""
        for ruin in self.ruins:
            if ruin['type'] == 'arch':
                # アーチの描画
                arch_color = (80, 90, 70)
                
                # アーチの柱（左右）
                left_pillar = pygame.Rect(
                    ruin['x'] - ruin['width']//2,
                    ruin['y'],
                    ruin['width']//4,
                    ruin['height']
                )
                right_pillar = pygame.Rect(
                    ruin['x'] + ruin['width']//4,
                    ruin['y'],
                    ruin['width']//4,
                    ruin['height']
                )
                
                pygame.draw.rect(surface, arch_color, left_pillar)
                pygame.draw.rect(surface, arch_color, right_pillar)
                
                # アーチの上部
                pygame.draw.arc(surface, arch_color,
                              pygame.Rect(ruin['x'] - ruin['width']//2,
                                        ruin['y'] - ruin['height']//4,
                                        ruin['width'], ruin['height']//2),
                              0, 3.14159, 10)
            
            elif ruin['type'] == 'pillar':
                # 石柱の描画
                pillar_color = (70, 80, 60)
                pillar_rect = pygame.Rect(
                    ruin['x'] - ruin['width']//2,
                    ruin['y'] - ruin['height'],
                    ruin['width'],
                    ruin['height']
                )
                pygame.draw.rect(surface, pillar_color, pillar_rect)
    
    def _draw_foreground_trees(self, surface: pygame.Surface):
        """手前の木々を描画"""
        for tree in self.trees:
            if tree['depth'] >= 0.6:  # 手前の木のみ
                tree_color = (25, 50, 20)
                
                # 木の幹
                trunk_rect = pygame.Rect(
                    tree['x'] - tree['width']//3,
                    tree['y'],
                    tree['width']//1.5,
                    tree['height']//2
                )
                pygame.draw.rect(surface, tree_color, trunk_rect)
    
    def _init_forest_particles(self):
        """森のパーティクル初期化"""
        for _ in range(20):
            particle = {
                'x': random.uniform(0, SCREEN_WIDTH),
                'y': random.uniform(0, SCREEN_HEIGHT),
                'vx': random.uniform(-0.5, 0.5),
                'vy': random.uniform(-1, -0.2),
                'size': random.uniform(1, 3),
                'alpha': random.randint(30, 100),
                'life': random.uniform(300, 600)
            }
            self.floating_particles.append(particle)
    
    def _draw_forest_particles(self, surface: pygame.Surface):
        """森の浮遊パーティクル"""
        for particle in self.floating_particles:
            alpha = int(particle['alpha'])
            if alpha > 0:
                particle_color = (150, 200, 100)  # 薄緑
                size = int(particle['size'])
                if size > 0:
                    particle_surface = pygame.Surface((size*2, size*2))
                    particle_surface.set_alpha(alpha)
                    pygame.draw.circle(particle_surface, particle_color, (size, size), size)
                    surface.blit(particle_surface, (int(particle['x']) - size, int(particle['y']) - size))
    
    def _update_forest_particles(self, dt: float):
        """森のパーティクルを更新"""
        for particle in self.floating_particles:
            # パーティクルの移動
            particle['x'] += particle['vx'] * dt * 60
            particle['y'] += particle['vy'] * dt * 60
            particle['life'] -= dt * 60
            
            # 画面外に出たらリセット
            if particle['y'] < 0 or particle['life'] <= 0:
                particle['x'] = random.uniform(0, SCREEN_WIDTH)
                particle['y'] = SCREEN_HEIGHT + 10
                particle['life'] = random.uniform(300, 600)
                particle['alpha'] = random.randint(30, 100)
    
    def _update_light_rays(self, dt: float):
        """光線の揺らぎを更新"""
        for ray in self.light_rays:
            # 光線の強度を時間で変化させる
            ray['intensity'] = 0.1 + 0.2 * abs(math.sin(self.time * 0.5 + ray['x'] * 0.01))