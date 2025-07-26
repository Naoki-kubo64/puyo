"""
ダンジョンマップレンダラー - Slay the Spire風のビジュアルマップ
Drop Puzzle × Roguelike のダンジョンマップ描画システム
"""

import pygame
import math
import logging
from typing import Dict, List, Optional, Tuple

from ..core.constants import *
from .dungeon_map import DungeonMap, DungeonNode, NodeType

logger = logging.getLogger(__name__)


class MapRenderer:
    """ダンジョンマップの描画を担当するクラス"""
    
    def __init__(self, dungeon_map: DungeonMap):
        self.dungeon_map = dungeon_map
        
        # 描画設定 - 改善されたレイアウト
        self.map_area_x = 80
        self.map_area_y = 100
        self.map_area_width = SCREEN_WIDTH - 160
        self.map_area_height = SCREEN_HEIGHT - 200
        
        # ノード描画設定 - より大きく、見やすく
        self.node_radius = 35
        self.node_spacing_x = self.map_area_width // 8
        self.node_spacing_y = self.map_area_height // (self.dungeon_map.total_floors + 2)
        
        # 美しいカラーパレット - Slay the Spire風
        self.colors = {
            NodeType.BATTLE: (220, 50, 50),      # 明るい赤
            NodeType.TREASURE: (255, 215, 0),    # ゴールド
            NodeType.EVENT: (70, 130, 255),      # 明るい青
            NodeType.REST: (50, 200, 50),        # 明るい緑
            NodeType.SHOP: (160, 50, 200),       # 紫
            NodeType.BOSS: (150, 0, 0),          # 暗い赤
            NodeType.ELITE: (255, 140, 0),       # オレンジ
        }
        
        # ノードサイズ設定（特別なノードは大きく）
        self.node_sizes = {
            NodeType.BATTLE: 35,
            NodeType.TREASURE: 35,
            NodeType.EVENT: 35,
            NodeType.REST: 35,
            NodeType.SHOP: 35,
            NodeType.BOSS: 50,      # ボスは特大
            NodeType.ELITE: 42,     # エリートは大きめ
        }
        
        # ノードアイコン用文字
        self.node_icons = {
            NodeType.BATTLE: "⚔",
            NodeType.TREASURE: "♦", 
            NodeType.EVENT: "?",
            NodeType.REST: "♨",
            NodeType.SHOP: "$",
            NodeType.BOSS: "👑",
            NodeType.ELITE: "★",
        }
        
        # UI要素
        self.selected_node: Optional[DungeonNode] = None
        self.hovered_node: Optional[DungeonNode] = None
        
        logger.info("MapRenderer initialized")
    
    def render(self, surface: pygame.Surface, fonts: Dict[str, pygame.font.Font]):
        """マップ全体を描画"""
        # 背景
        self._render_background(surface)
        
        # 接続線を先に描画
        self._render_connections(surface)
        
        # ノードを描画
        self._render_nodes(surface, fonts)
        
        # UI要素
        self._render_ui(surface, fonts)
        
        # ノード詳細情報
        if self.hovered_node:
            self._render_node_tooltip(surface, fonts, self.hovered_node)
    
    def _render_background(self, surface: pygame.Surface):
        """美しい背景を描画 - Slay the Spire風"""
        # 全体背景のグラデーション
        for y in range(SCREEN_HEIGHT):
            # 上から下へのグラデーション（暗い青から黒へ）
            ratio = y / SCREEN_HEIGHT
            r = int(20 * (1 - ratio))
            g = int(30 * (1 - ratio)) 
            b = int(50 * (1 - ratio))
            color = (r, g, b)
            pygame.draw.line(surface, color, (0, y), (SCREEN_WIDTH, y))
        
        # マップエリアの美しい枠
        map_rect = pygame.Rect(
            self.map_area_x - 10, self.map_area_y - 10,
            self.map_area_width + 20, self.map_area_height + 20
        )
        
        # 内側の半透明背景
        inner_surface = pygame.Surface((self.map_area_width + 20, self.map_area_height + 20))
        inner_surface.set_alpha(180)
        inner_surface.fill((15, 25, 40))
        surface.blit(inner_surface, (self.map_area_x - 10, self.map_area_y - 10))
        
        # 美しい境界線
        pygame.draw.rect(surface, (100, 150, 200), map_rect, 3)
        pygame.draw.rect(surface, (200, 200, 200), map_rect, 1)
        
        # フロア区切り線を美しく
        for floor in range(1, self.dungeon_map.total_floors):
            y = self._get_node_y(floor) - self.node_spacing_y // 2
            
            # メインライン
            pygame.draw.line(
                surface, (80, 80, 120),
                (self.map_area_x, y),
                (self.map_area_x + self.map_area_width, y),
                2
            )
            
            # グロウ効果
            pygame.draw.line(
                surface, (40, 40, 60),
                (self.map_area_x, y - 1),
                (self.map_area_x + self.map_area_width, y - 1),
                1
            )
            pygame.draw.line(
                surface, (40, 40, 60),
                (self.map_area_x, y + 1),
                (self.map_area_x + self.map_area_width, y + 1),
                1
            )
    
    def _render_connections(self, surface: pygame.Surface):
        """ノード間の接続線を描画"""
        for node in self.dungeon_map.nodes.values():
            if not node.connections:
                continue
            
            start_pos = self._get_node_position(node)
            
            for connection_id in node.connections:
                connected_node = self.dungeon_map.get_node_by_id(connection_id)
                if not connected_node:
                    continue
                
                end_pos = self._get_node_position(connected_node)
                
                # 線の色を決定（接続タイプに応じて）
                x_diff = abs(node.x - connected_node.x)
                
                if node.visited and connected_node.available:
                    # 選択可能な経路
                    if x_diff == 0:
                        color = Colors.YELLOW  # 真っ直ぐの経路（黄色）
                        width = 4
                    else:
                        color = (255, 165, 0)  # 分岐経路（オレンジ）
                        width = 3
                elif node.visited:
                    # 訪問済み
                    color = Colors.LIGHT_GRAY  
                    width = 2
                else:
                    # 未訪問
                    color = Colors.GRAY  
                    width = 1
                
                pygame.draw.line(surface, color, start_pos, end_pos, width)
    
    def _render_nodes(self, surface: pygame.Surface, fonts: Dict[str, pygame.font.Font]):
        """ノードを描画"""
        font_small = fonts.get('small', pygame.font.Font(None, 16))
        
        # フロア順に描画（手前から奥へ）
        for floor in range(self.dungeon_map.total_floors):
            nodes = self.dungeon_map.get_nodes_by_floor(floor)
            
            for node in nodes:
                self._render_single_node(surface, font_small, node)
    
    def _render_single_node(self, surface: pygame.Surface, font: pygame.font.Font, node: DungeonNode):
        """単一ノードを美しく描画 - Slay the Spire風"""
        pos = self._get_node_position(node)
        
        # ノードタイプに応じたサイズを取得
        node_radius = self.node_sizes.get(node.node_type, self.node_radius)
        
        # ノードの状態に応じてスタイルを決定
        if node.visited:
            # 訪問済み - 暗く表示
            main_color = tuple(c // 2 for c in self.colors[node.node_type])
            border_color = (100, 100, 100)
            border_width = 2
            alpha = 160
        elif node.available:
            # 選択可能 - 明るく表示、グロウ効果
            main_color = self.colors[node.node_type]
            border_color = (255, 255, 255)
            border_width = 4
            alpha = 255
            
            # パルス効果
            pulse = abs(math.sin(pygame.time.get_ticks() * 0.005)) * 0.3 + 0.7
            main_color = tuple(int(c * pulse) for c in main_color)
        else:
            # 選択不可 - グレーアウト
            main_color = (80, 80, 80)
            border_color = (60, 60, 60)  
            border_width = 1
            alpha = 120
        
        # ホバー効果 - 美しいグロウ
        if self.hovered_node == node:
            # アウターグロウ
            for i in range(6):
                glow_radius = node_radius + 15 - i * 2
                glow_alpha = 40 - i * 6
                glow_color = (*border_color, glow_alpha)
                
                # 半透明サーフェスでグロウ描画
                glow_surface = pygame.Surface((glow_radius * 2 + 4, glow_radius * 2 + 4))
                glow_surface.set_alpha(glow_alpha)
                glow_surface.fill((0, 0, 0))
                glow_surface.set_colorkey((0, 0, 0))
                pygame.draw.circle(glow_surface, border_color, 
                                 (glow_radius + 2, glow_radius + 2), glow_radius)
                surface.blit(glow_surface, 
                           (pos[0] - glow_radius - 2, pos[1] - glow_radius - 2))
        
        # 選択効果 - 輝くリング
        if self.selected_node == node:
            for i in range(4):
                ring_radius = node_radius + 8 + i * 3
                ring_alpha = 100 - i * 20
                ring_surface = pygame.Surface((ring_radius * 2 + 4, ring_radius * 2 + 4))
                ring_surface.set_alpha(ring_alpha)
                ring_surface.fill((0, 0, 0))
                ring_surface.set_colorkey((0, 0, 0))
                pygame.draw.circle(ring_surface, (255, 255, 0), 
                                 (ring_radius + 2, ring_radius + 2), ring_radius, 3)
                surface.blit(ring_surface, 
                           (pos[0] - ring_radius - 2, pos[1] - ring_radius - 2))
        
        # ノード本体を3D風に描画
        # 影
        shadow_offset = 3
        pygame.draw.circle(surface, (20, 20, 20), 
                         (pos[0] + shadow_offset, pos[1] + shadow_offset), 
                         node_radius)
        
        # メインボディ
        pygame.draw.circle(surface, main_color, pos, node_radius)
        
        # ハイライト（上部）
        highlight_color = tuple(min(255, c + 60) for c in main_color)
        pygame.draw.circle(surface, highlight_color, 
                         (pos[0], pos[1] - 5), node_radius - 8)
        
        # ボーダー
        pygame.draw.circle(surface, border_color, pos, node_radius, border_width)
        pygame.draw.circle(surface, border_color, pos, node_radius, border_width)
        
        # 特殊ノードの追加効果
        self._render_special_node_effects(surface, node, pos, node_radius)
        
        # ノードタイプアイコン/文字
        self._render_node_icon(surface, font, node, pos)
    
    def _render_special_node_effects(self, surface: pygame.Surface, node: DungeonNode, 
                                   pos: Tuple[int, int], node_radius: int):
        """特殊ノード（ボス・エリート）の追加視覚効果"""
        
        if node.node_type == NodeType.BOSS:
            # ボスノードには炎のような効果
            for i in range(3):
                flame_radius = node_radius + 20 + i * 5
                flame_alpha = 30 - i * 8
                
                # 炎の色（赤からオレンジのグラデーション）
                flame_colors = [(255, 100, 0), (255, 150, 0), (255, 200, 50)]
                flame_color = flame_colors[i % len(flame_colors)]
                
                # 波のような動きを追加
                wave_offset = math.sin(pygame.time.get_ticks() * 0.01 + i) * 3
                flame_pos = (pos[0], pos[1] + int(wave_offset))
                
                flame_surface = pygame.Surface((flame_radius * 2, flame_radius * 2))
                flame_surface.set_alpha(flame_alpha)
                flame_surface.fill((0, 0, 0))
                flame_surface.set_colorkey((0, 0, 0))
                pygame.draw.circle(flame_surface, flame_color, 
                                 (flame_radius, flame_radius), flame_radius - 5)
                surface.blit(flame_surface, 
                           (flame_pos[0] - flame_radius, flame_pos[1] - flame_radius))
        
        elif node.node_type == NodeType.ELITE:
            # エリートノードには星の効果
            star_count = 6
            star_distance = node_radius + 15
            
            for i in range(star_count):
                angle = (i * 2 * math.pi / star_count) + (pygame.time.get_ticks() * 0.003)
                star_x = pos[0] + int(star_distance * math.cos(angle))
                star_y = pos[1] + int(star_distance * math.sin(angle))
                
                # 小さな星を描画
                star_size = 3
                star_color = (255, 255, 150)
                pygame.draw.circle(surface, star_color, (star_x, star_y), star_size)
                
                # 輝きを追加
                if i % 2 == 0:
                    pygame.draw.circle(surface, (255, 255, 255), (star_x, star_y), star_size + 1, 1)
    
    def _render_node_icon(self, surface: pygame.Surface, font: pygame.font.Font, 
                         node: DungeonNode, pos: Tuple[int, int]):
        """ノードタイプに応じたアイコンを描画"""
        # シンプルで分かりやすいアイコン文字
        icon_map = {
            NodeType.BATTLE: "B",
            NodeType.TREASURE: "T", 
            NodeType.EVENT: "?",
            NodeType.REST: "R",
            NodeType.SHOP: "S",
            NodeType.BOSS: "BOSS",
            NodeType.ELITE: "E",
        }
        
        icon = icon_map.get(node.node_type, "?")
        
        # アイコンの色を決定
        if node.visited:
            text_color = (160, 160, 160)
        elif node.available:
            text_color = (255, 255, 255)
        else:
            text_color = (100, 100, 100)
        
        # ボスノードは特別扱い
        if node.node_type == NodeType.BOSS:
            boss_text = font.render("BOSS", True, text_color)
            text_rect = boss_text.get_rect(center=pos)
            surface.blit(boss_text, text_rect)
        else:
            icon_text = font.render(icon, True, text_color)
            text_rect = icon_text.get_rect(center=pos)
            surface.blit(icon_text, text_rect)
    
    def _render_ui(self, surface: pygame.Surface, fonts: Dict[str, pygame.font.Font]):
        """UI要素を描画"""
        font_medium = fonts.get('medium', pygame.font.Font(None, 24))
        font_large = fonts.get('large', pygame.font.Font(None, 32))
        
        # タイトル
        title = font_large.render("DUNGEON MAP", True, Colors.WHITE)
        surface.blit(title, (self.map_area_x, 20))
        
        # 進行状況
        current, total = self.dungeon_map.get_current_floor_progress()
        progress_text = font_medium.render(f"Floor: {current} / {total}", True, Colors.WHITE)
        surface.blit(progress_text, (self.map_area_x + self.map_area_width - 150, 20))
        
        # 現在のノード情報
        if self.dungeon_map.current_node:
            current_info = f"Current: {self.dungeon_map.current_node.node_type.value.title()}"
            info_text = font_medium.render(current_info, True, Colors.YELLOW)
            surface.blit(info_text, (self.map_area_x, self.map_area_y + self.map_area_height + 10))
        
        # 操作説明
        instructions = [
            "Click on yellow-bordered nodes to move",
            "ESC - Return to menu",
        ]
        
        for i, instruction in enumerate(instructions):
            instruction_text = fonts.get('small', pygame.font.Font(None, 16)).render(
                instruction, True, Colors.LIGHT_GRAY
            )
            surface.blit(instruction_text, (
                self.map_area_x + self.map_area_width - 300,
                self.map_area_y + self.map_area_height + 10 + i * 20
            ))
    
    def _render_node_tooltip(self, surface: pygame.Surface, fonts: Dict[str, pygame.font.Font], 
                           node: DungeonNode):
        """ノードの詳細情報をツールチップで表示"""
        font_small = fonts.get('small', pygame.font.Font(None, 16))
        
        # ツールチップの内容
        lines = [
            f"Type: {node.node_type.value.title()}",
            f"Floor: {node.floor + 1}",
        ]
        
        if node.enemy_type:
            lines.append(f"Enemy: {node.enemy_type}")
        
        if node.visited:
            lines.append("Status: Visited")
        elif node.available:
            lines.append("Status: Available")
        else:
            lines.append("Status: Locked")
        
        # ツールチップサイズ計算
        max_width = max(font_small.size(line)[0] for line in lines)
        tooltip_width = max_width + 20
        tooltip_height = len(lines) * 20 + 10
        
        # マウス位置を取得してツールチップ位置を決定
        mouse_x, mouse_y = pygame.mouse.get_pos()
        tooltip_x = mouse_x + 15
        tooltip_y = mouse_y - tooltip_height // 2
        
        # 画面境界チェック
        if tooltip_x + tooltip_width > SCREEN_WIDTH:
            tooltip_x = mouse_x - tooltip_width - 15
        if tooltip_y < 0:
            tooltip_y = 0
        elif tooltip_y + tooltip_height > SCREEN_HEIGHT:
            tooltip_y = SCREEN_HEIGHT - tooltip_height
        
        # ツールチップ背景
        tooltip_rect = pygame.Rect(tooltip_x, tooltip_y, tooltip_width, tooltip_height)
        pygame.draw.rect(surface, Colors.BLACK, tooltip_rect)
        pygame.draw.rect(surface, Colors.WHITE, tooltip_rect, 2)
        
        # ツールチップテキスト
        for i, line in enumerate(lines):
            text = font_small.render(line, True, Colors.WHITE)
            surface.blit(text, (tooltip_x + 10, tooltip_y + 5 + i * 20))
    
    def _get_node_position(self, node: DungeonNode) -> Tuple[int, int]:
        """ノードの描画位置を計算"""
        x = self.map_area_x + (node.x + 1) * self.node_spacing_x
        y = self._get_node_y(node.floor)
        return (int(x), int(y))
    
    def _get_node_y(self, floor: int) -> int:
        """フロアのY座標を計算"""
        # 上から下への順序（フロア0が上）
        return int(self.map_area_y + (floor + 1) * self.node_spacing_y)
    
    def handle_click(self, pos: Tuple[int, int]) -> Optional[DungeonNode]:
        """クリック処理 - クリックされたノードを返す"""
        for node in self.dungeon_map.nodes.values():
            node_pos = self._get_node_position(node)
            distance = math.sqrt((pos[0] - node_pos[0])**2 + (pos[1] - node_pos[1])**2)
            
            # ノードタイプに応じたサイズでクリック判定
            node_radius = self.node_sizes.get(node.node_type, self.node_radius)
            if distance <= node_radius:
                return node
        
        return None
    
    def handle_mouse_motion(self, pos: Tuple[int, int]):
        """マウス移動処理 - ホバー状態を更新"""
        self.hovered_node = None
        
        for node in self.dungeon_map.nodes.values():
            node_pos = self._get_node_position(node)
            distance = math.sqrt((pos[0] - node_pos[0])**2 + (pos[1] - node_pos[1])**2)
            
            # ノードタイプに応じたサイズでホバー判定
            node_radius = self.node_sizes.get(node.node_type, self.node_radius)
            if distance <= node_radius:
                self.hovered_node = node
                break
    
    def set_selected_node(self, node: Optional[DungeonNode]):
        """選択ノードを設定"""
        self.selected_node = node


if __name__ == "__main__":
    # テスト用の簡単な実行
    import sys
    import os
    
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
    
    pygame.init()
    from .dungeon_map import DungeonMap
    
    # テスト用ダンジョンマップ
    dungeon = DungeonMap(total_floors=5)
    renderer = MapRenderer(dungeon)
    
    print("MapRenderer test completed")
    print(f"Map area: {renderer.map_area_width}x{renderer.map_area_height}")
    print(f"Node spacing: {renderer.node_spacing_x}x{renderer.node_spacing_y}")