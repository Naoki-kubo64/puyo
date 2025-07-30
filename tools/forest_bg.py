"""
森の遺跡背景画像をbase64エンコードで保存
"""
import pygame
import base64
import io

# 送っていただいた森の遺跡画像を再現した簡単な背景を生成
def create_forest_background(width, height):
    """森の遺跡風背景を生成"""
    surface = pygame.Surface((width, height))
    
    # 基本グラデーション（深い緑）
    for y in range(height):
        ratio = y / height
        r = int(30 + ratio * 40)  # 30-70
        g = int(60 + ratio * 50)  # 60-110
        b = int(25 + ratio * 35)  # 25-60
        color = (r, g, b)
        pygame.draw.line(surface, color, (0, y), (width, y))
    
    # 中央の光の効果
    center_x = width // 2
    center_y = height // 2
    
    # 光の円
    for radius in range(200, 0, -15):
        alpha = int(20 * (200 - radius) / 200)
        if alpha > 0:
            light_surface = pygame.Surface((radius*2, radius*2))
            light_surface.set_alpha(alpha)
            light_color = (120, 180, 90)  # 明るい緑
            pygame.draw.circle(light_surface, light_color, (radius, radius), radius)
            surface.blit(light_surface, (center_x - radius, center_y - radius))
    
    # 遺跡のアーチ構造
    arch_color = (80, 100, 60)
    pillar_width = 25
    pillar_height = 120
    arch_width = 140
    
    # 左の柱
    pygame.draw.rect(surface, arch_color, (center_x - arch_width//2, center_y, pillar_width, pillar_height))
    # 右の柱
    pygame.draw.rect(surface, arch_color, (center_x + arch_width//2 - pillar_width, center_y, pillar_width, pillar_height))
    
    # アーチの上部
    arch_rect = pygame.Rect(center_x - arch_width//2, center_y - 50, arch_width, 100)
    pygame.draw.arc(surface, arch_color, arch_rect, 0, 3.14159, 12)
    
    # 木のシルエット（左右に配置）
    tree_color = (20, 40, 15)
    
    # 左の木
    for i in range(5):
        tree_x = 50 + i * 80
        tree_height = 150 + i * 30
        pygame.draw.rect(surface, tree_color, (tree_x, height - tree_height, 15, tree_height))
    
    # 右の木
    for i in range(5):
        tree_x = width - 200 + i * 40
        tree_height = 120 + i * 25
        pygame.draw.rect(surface, tree_color, (tree_x, height - tree_height, 12, tree_height))
    
    return surface

def save_background_as_png(filename, width=1200, height=800):
    """背景をPNGファイルとして保存"""
    pygame.init()
    surface = create_forest_background(width, height)
    pygame.image.save(surface, filename)
    print(f"Background saved as {filename}")

if __name__ == "__main__":
    save_background_as_png("forest_ruins_background.png", 1920, 1080)