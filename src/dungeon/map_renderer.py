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
        
        # 描画設定
        self.map_area_x = 50
        self.map_area_y = 80
        self.map_area_width = SCREEN_WIDTH - 100
        self.map_area_height = SCREEN_HEIGHT - 160
        
        # ノード描画設定
        self.node_radius = 25
        self.node_spacing_x = self.map_area_width // 8  # 7列+余白
        self.node_spacing_y = self.map_area_height // (self.dungeon_map.total_floors + 1)
        
        # カラーパレット
        self.colors = {
            NodeType.BATTLE: Colors.RED,
            NodeType.TREASURE: Colors.YELLOW,
            NodeType.EVENT: Colors.BLUE,
            NodeType.REST: Colors.GREEN,
            NodeType.SHOP: Colors.PURPLE,
            NodeType.BOSS: Colors.DARK_RED,
            NodeType.ELITE: Colors.ORANGE,
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
        """背景を描画"""
        # マップエリアの背景
        map_rect = pygame.Rect(
            self.map_area_x, self.map_area_y,
            self.map_area_width, self.map_area_height
        )
        pygame.draw.rect(surface, Colors.DARK_GRAY, map_rect)
        pygame.draw.rect(surface, Colors.WHITE, map_rect, 2)
        
        # フロア区切り線
        for floor in range(1, self.dungeon_map.total_floors):
            y = self._get_node_y(floor) - self.node_spacing_y // 2
            pygame.draw.line(
                surface, Colors.GRAY,
                (self.map_area_x, y),
                (self.map_area_x + self.map_area_width, y),
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
                
                # 線の色を決定
                if node.visited and connected_node.available:
                    color = Colors.YELLOW  # 選択可能な経路
                    width = 3
                elif node.visited:
                    color = Colors.LIGHT_GRAY  # 訪問済み
                    width = 2
                else:
                    color = Colors.GRAY  # 未訪問
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
        """単一ノードを描画"""
        pos = self._get_node_position(node)
        
        # ノードの状態に応じて色を決定
        if node.visited:
            color = self.colors[node.node_type]
            border_color = Colors.WHITE
            border_width = 3
        elif node.available:
            color = self.colors[node.node_type]
            border_color = Colors.YELLOW
            border_width = 4
        else:
            color = Colors.GRAY
            border_color = Colors.DARK_GRAY
            border_width = 2
        
        # ホバー効果
        if self.hovered_node == node:
            border_color = Colors.CYAN
            border_width = 5
        
        # 選択効果
        if self.selected_node == node:
            # 選択オーラを描画
            for i in range(3):
                pygame.draw.circle(surface, Colors.YELLOW, pos, self.node_radius + 5 + i, 2)
        
        # ノード本体を描画
        pygame.draw.circle(surface, color, pos, self.node_radius)
        pygame.draw.circle(surface, border_color, pos, self.node_radius, border_width)
        
        # ノードタイプアイコン/文字
        self._render_node_icon(surface, font, node, pos)
    
    def _render_node_icon(self, surface: pygame.Surface, font: pygame.font.Font, 
                         node: DungeonNode, pos: Tuple[int, int]):
        """ノードタイプに応じたアイコンを描画"""
        icon_map = {
            NodeType.BATTLE: "⚔",
            NodeType.TREASURE: "💰",
            NodeType.EVENT: "?",
            NodeType.REST: "🛏",
            NodeType.SHOP: "🏪",
            NodeType.BOSS: "👑",
            NodeType.ELITE: "⭐",
        }
        
        icon = icon_map.get(node.node_type, "?")
        
        # フォントでアイコンを描画（フォールバック）
        if icon in ["⚔", "👑", "⭐", "💰", "🛏", "🏪"]:
            # Unicode文字の場合、シンプルな文字に置き換え
            simple_icons = {
                "⚔": "B",  # Battle
                "💰": "T",  # Treasure
                "🛏": "R",  # Rest
                "🏪": "S",  # Shop
                "👑": "BOSS",  # Boss
                "⭐": "E",  # Elite
            }
            icon = simple_icons.get(icon, icon)
        
        text_color = Colors.WHITE if node.visited or node.available else Colors.LIGHT_GRAY
        
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
            
            if distance <= self.node_radius:
                return node
        
        return None
    
    def handle_mouse_motion(self, pos: Tuple[int, int]):
        """マウス移動処理 - ホバー状態を更新"""
        self.hovered_node = None
        
        for node in self.dungeon_map.nodes.values():
            node_pos = self._get_node_position(node)
            distance = math.sqrt((pos[0] - node_pos[0])**2 + (pos[1] - node_pos[1])**2)
            
            if distance <= self.node_radius:
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