"""
ダンジョンマップレンダラー - Slay the Spire風のビジュアルマップ
Drop Puzzle × Roguelike のダンジョンマップ描画システム
"""

import pygame
import math
import logging
import os
from typing import Dict, List, Optional, Tuple

from core.constants import *
from .dungeon_map import DungeonMap, DungeonNode, NodeType

logger = logging.getLogger(__name__)


class MapRenderer:
    """ダンジョンマップの描画を担当するクラス"""
    
    def __init__(self, dungeon_map: DungeonMap):
        self.dungeon_map = dungeon_map
        
        # 描画設定 - 改善されたレイアウト（ステータス表示のため上部余白を増加）
        self.map_area_x = 80
        self.map_area_y = 150  # ステータス表示のため上部余白を増加
        self.map_area_width = SCREEN_WIDTH - 160
        self.map_area_height = SCREEN_HEIGHT - 200
        
        # 画像ファイルのロード
        self.node_images = self._load_node_images()
        self.background_image = self._load_background_image()
        
        # ステータスアイコンを初期化
        self.hp_icon = None
        self.gold_icon = None
        self._load_status_icons()
        
        # 特殊ぷよ画像を初期化
        self.special_puyo_images = {}
        self._load_special_puyo_images()
        
        # マウスオーバー用
        self.hover_info = None
        self.special_puyo_hover_areas = []
        
        # スクロール機能
        self.scroll_y = 0
        self.max_scroll_y = 0
        
        # ノード描画設定 - より大きく、見やすく
        self.node_radius = 35
        self.node_spacing_x = self.map_area_width // 8
        self.node_spacing_y = 140  # 固定の縦間隔（余裕のある広さ）
        
        # 実際のマップの総高さを計算
        self.total_map_height = (self.dungeon_map.total_floors + 1) * self.node_spacing_y
        
        # スクロール可能な最大値を設定
        self.max_scroll_y = max(0, self.total_map_height - self.map_area_height)
        
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
        
        # ノードアイコン用シンボル（絵文字対応なし環境でも表示可能）
        self.node_icons = {
            NodeType.BATTLE: "B",
            NodeType.TREASURE: "T", 
            NodeType.EVENT: "?",
            NodeType.REST: "R",
            NodeType.SHOP: "S",
            NodeType.BOSS: "BOSS",
            NodeType.ELITE: "E",
        }
        
        # UI要素
        self.selected_node: Optional[DungeonNode] = None
        self.hovered_node: Optional[DungeonNode] = None
        
        logger.info("MapRenderer initialized")
    
    def _load_node_images(self) -> Dict[NodeType, pygame.Surface]:
        """ノードタイプ別の画像を読み込み"""
        images = {}
        
        # プロジェクトルートディレクトリを取得
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        
        # 画像ファイルのマッピング
        image_files = {
            NodeType.BATTLE: "雑魚.png",
            NodeType.ELITE: "エリート.png", 
            NodeType.TREASURE: "宝箱.png",
            NodeType.SHOP: "ショップ.png",
            NodeType.BOSS: "ボス.png",
            NodeType.EVENT: "ランダム.png",
            NodeType.REST: "休憩所.png",
        }
        
        # 各画像を読み込み
        for node_type, filename in image_files.items():
            try:
                image_path = os.path.join(project_root, filename)
                if os.path.exists(image_path):
                    original_image = pygame.image.load(image_path)
                    # ノードサイズに合わせてスケール（通常ノードは96x96、大きいノードは128x128）
                    if node_type in [NodeType.BOSS, NodeType.ELITE]:
                        scaled_image = pygame.transform.scale(original_image, (128, 128))
                    else:
                        scaled_image = pygame.transform.scale(original_image, (96, 96))
                    images[node_type] = scaled_image
                    logger.info(f"Loaded image for {node_type.value}: {filename}")
                else:
                    logger.warning(f"Image file not found: {image_path}")
                    # フォールバック用の空画像
                    if node_type in [NodeType.BOSS, NodeType.ELITE]:
                        images[node_type] = pygame.Surface((128, 128))
                    else:
                        images[node_type] = pygame.Surface((96, 96))
                    images[node_type].fill((100, 100, 100))
            except Exception as e:
                logger.error(f"Failed to load image for {node_type.value}: {e}")
                # エラー時のフォールバック
                if node_type in [NodeType.BOSS, NodeType.ELITE]:
                    images[node_type] = pygame.Surface((128, 128))
                else:
                    images[node_type] = pygame.Surface((96, 96))
                images[node_type].fill((100, 100, 100))
        
        return images
    
    def _load_status_icons(self):
        """ステータスアイコンを読み込み"""
        try:
            # プロジェクトルートからのパス
            base_path = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
            
            # HP.pngを読み込み
            hp_path = os.path.join(base_path, "HP.png")
            if os.path.exists(hp_path):
                self.hp_icon = pygame.image.load(hp_path).convert_alpha()
                # サイズを調整（30x30ピクセル）
                self.hp_icon = pygame.transform.scale(self.hp_icon, (30, 30))
                logger.info("Loaded HP icon for map status")
            
            # gold.pngを読み込み
            gold_path = os.path.join(base_path, "gold.png")
            if os.path.exists(gold_path):
                self.gold_icon = pygame.image.load(gold_path).convert_alpha()
                # サイズを調整（30x30ピクセル）
                self.gold_icon = pygame.transform.scale(self.gold_icon, (30, 30))
                logger.info("Loaded Gold icon for map status")
                
        except Exception as e:
            logger.warning(f"Could not load status icons: {e}")
    
    def _load_special_puyo_images(self):
        """特殊ぷよの画像を読み込み（SimpleSpecialTypeシステム対応）"""
        try:
            # Pictureフォルダから特殊ぷよ画像を読み込み
            base_path = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
            
            # SimpleSpecialTypeシステムに対応した画像マッピング（バトル画面と同じ）
            image_mapping = {
                "heal": "HEAL.png",
                "bomb": "BOMB.png",
                "lightning": "LIGHTNING.png",
                "shield": "SHIELD.png",
                "multiplier": "Multiplier.png",
                "poison": "POISON.png"
            }
            
            for puyo_type, filename in image_mapping.items():
                try:
                    image_path = os.path.join(base_path, "Picture", filename)
                    if os.path.exists(image_path):
                        image = pygame.image.load(image_path).convert_alpha()
                        # ヘッダー用に小さくスケール（25x25ピクセル）
                        self.special_puyo_images[puyo_type] = pygame.transform.scale(image, (25, 25))
                        logger.debug(f"Loaded special puyo image for map header: {filename}")
                    else:
                        logger.warning(f"Special puyo image not found: {image_path}")
                except Exception as e:
                    logger.warning(f"Failed to load special puyo image {filename}: {e}")
                    
        except Exception as e:
            logger.warning(f"Could not load special puyo images: {e}")
    
    def _load_background_image(self) -> Optional[pygame.Surface]:
        """背景画像を読み込み"""
        try:
            # プロジェクトルートディレクトリを取得
            project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
            image_path = os.path.join(project_root, "map2.png")
            
            if os.path.exists(image_path):
                background_image = pygame.image.load(image_path)
                # 画面サイズに合わせてスケール
                scaled_background = pygame.transform.scale(background_image, (SCREEN_WIDTH, SCREEN_HEIGHT))
                logger.info(f"Loaded background image: map2.png")
                return scaled_background
            else:
                logger.warning(f"Background image not found: {image_path}")
                return None
        except Exception as e:
            logger.error(f"Failed to load background image: {e}")
            return None
    
    def render(self, surface: pygame.Surface, fonts: Dict[str, pygame.font.Font]):
        """マップ全体を描画"""
        # フォント情報を保存（スクロールバーで使用）
        self._last_fonts = fonts
        
        # 背景
        self._render_background(surface)
        
        # マップ領域のクリッピングを設定
        clip_rect = pygame.Rect(self.map_area_x, self.map_area_y, 
                               self.map_area_width, self.map_area_height)
        original_clip = surface.get_clip()
        surface.set_clip(clip_rect)
        
        # 接続線を先に描画
        self._render_connections(surface)
        
        # ノードを描画
        self._render_nodes(surface, fonts)
        
        # クリッピングを元に戻す
        surface.set_clip(original_clip)
        
        # UI要素（クリッピング外）
        self._render_ui(surface, fonts)
        
        # ステータス表示（新規追加）
        self._render_status_bar(surface, fonts)
        
        # スクロールバーを描画
        self._render_scrollbar(surface)
        
        # ノード詳細情報
        if self.hovered_node:
            self._render_node_tooltip(surface, fonts, self.hovered_node)
    
    def _render_scrollbar(self, surface: pygame.Surface):
        """スクロールバーを描画"""
        if self.max_scroll_y <= 0:
            return  # スクロール不要
        
        # スクロールバーの位置とサイズ
        scrollbar_x = self.map_area_x + self.map_area_width + 10
        scrollbar_y = self.map_area_y
        scrollbar_width = 10
        scrollbar_height = self.map_area_height
        
        # スクロールバー背景
        scrollbar_bg = pygame.Rect(scrollbar_x, scrollbar_y, scrollbar_width, scrollbar_height)
        pygame.draw.rect(surface, (40, 40, 40), scrollbar_bg)
        
        # スクロールバーハンドル
        handle_height = max(20, int((self.map_area_height / self.total_map_height) * scrollbar_height))
        handle_y = scrollbar_y + int((self.scroll_y / self.max_scroll_y) * (scrollbar_height - handle_height))
        
        handle_rect = pygame.Rect(scrollbar_x, handle_y, scrollbar_width, handle_height)
        pygame.draw.rect(surface, (150, 150, 150), handle_rect)
        
        # スクロール情報表示
        scroll_info = f"{int(self.scroll_y)}/{int(self.max_scroll_y)}"
        if hasattr(self, '_last_fonts') and 'small' in self._last_fonts:
            font = self._last_fonts['small']
            text = font.render(scroll_info, True, Colors.WHITE)
            surface.blit(text, (scrollbar_x - 50, scrollbar_y - 25))
    
    def _render_background(self, surface: pygame.Surface):
        """背景画像を描画"""
        if self.background_image:
            # 背景画像を描画
            surface.blit(self.background_image, (0, 0))
        else:
            # フォールバック：グラデーション背景
            for y in range(SCREEN_HEIGHT):
                # 上から下へのグラデーション（暗い青から黒へ）
                ratio = y / SCREEN_HEIGHT
                r = int(20 * (1 - ratio))
                g = int(30 * (1 - ratio)) 
                b = int(50 * (1 - ratio))
                color = (r, g, b)
                pygame.draw.line(surface, color, (0, y), (SCREEN_WIDTH, y))
        
        # マップエリアの半透明オーバーレイ（背景画像がある場合のみ）
        if self.background_image:
            map_rect = pygame.Rect(
                self.map_area_x - 10, self.map_area_y - 10,
                self.map_area_width + 20, self.map_area_height + 20
            )
            
            # 半透明の暗いオーバーレイでマップエリアを見やすくする
            overlay_surface = pygame.Surface((self.map_area_width + 20, self.map_area_height + 20))
            overlay_surface.set_alpha(120)
            overlay_surface.fill((0, 0, 0))
            surface.blit(overlay_surface, (self.map_area_x - 10, self.map_area_y - 10))
            
            # 美しい境界線
            pygame.draw.rect(surface, (150, 150, 150), map_rect, 2)
        else:
            # フォールバック：従来の枠デザイン
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
                    # 選択可能な経路 - より目立つ効果
                    if x_diff == 0:
                        color = (255, 255, 100)  # 明るい黄色（真っ直ぐ）
                        width = 5
                        # グロウ効果
                        glow_color = (255, 255, 150, 128)
                    else:
                        color = (255, 165, 0)  # オレンジ（分岐）
                        width = 4
                        glow_color = (255, 200, 100, 128)
                    
                    # グロウ効果のための太い線を先に描画
                    pygame.draw.line(surface, glow_color[:3], start_pos, end_pos, width + 2)
                    
                elif node.visited:
                    # 訪問済み
                    color = (150, 150, 150)  
                    width = 2
                else:
                    # 未訪問 - より薄く
                    color = (80, 80, 90)  
                    width = 1
                
                # メイン線を描画
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
        """単一ノードをアイコン画像で描画"""
        pos = self._get_node_position(node)
        
        # ホバー効果 - グロウ
        if self.hovered_node == node:
            # アウターグロウ（アイコンの周りに光る効果）
            for i in range(6):
                glow_radius = 70 + i * 8
                glow_alpha = 50 - i * 8
                if glow_alpha > 0:
                    glow_surface = pygame.Surface((glow_radius * 2, glow_radius * 2))
                    glow_surface.set_alpha(glow_alpha)
                    glow_surface.fill((0, 0, 0))
                    glow_surface.set_colorkey((0, 0, 0))
                    pygame.draw.circle(glow_surface, (255, 255, 100), 
                                     (glow_radius, glow_radius), glow_radius - 8)
                    surface.blit(glow_surface, 
                               (pos[0] - glow_radius, pos[1] - glow_radius))
        
        # 選択効果 - 輝くリング
        if self.selected_node == node:
            for i in range(4):
                ring_radius = 60 + i * 8
                ring_alpha = 120 - i * 25
                if ring_alpha > 0:
                    ring_surface = pygame.Surface((ring_radius * 2, ring_radius * 2))
                    ring_surface.set_alpha(ring_alpha)
                    ring_surface.fill((0, 0, 0))
                    ring_surface.set_colorkey((0, 0, 0))
                    pygame.draw.circle(ring_surface, (255, 255, 0), 
                                     (ring_radius, ring_radius), ring_radius, 4)
                    surface.blit(ring_surface, 
                               (pos[0] - ring_radius, pos[1] - ring_radius))
        
        # 選択可能ノードのパルス効果
        if node.available and not node.visited:
            pulse = abs(math.sin(pygame.time.get_ticks() * 0.003)) * 0.4 + 0.6
            pulse_radius = int(80 * pulse)
            pulse_alpha = int(60 * (1 - pulse))
            if pulse_alpha > 0:
                pulse_surface = pygame.Surface((pulse_radius * 2, pulse_radius * 2))
                pulse_surface.set_alpha(pulse_alpha)
                pulse_surface.fill((0, 0, 0))
                pulse_surface.set_colorkey((0, 0, 0))
                pygame.draw.circle(pulse_surface, (255, 255, 255), 
                                 (pulse_radius, pulse_radius), pulse_radius, 3)
                surface.blit(pulse_surface, 
                           (pos[0] - pulse_radius, pos[1] - pulse_radius))
        
        # アイコン画像を描画
        self._render_node_icon(surface, font, node, pos)
    
    
    def _render_node_icon(self, surface: pygame.Surface, font: pygame.font.Font, 
                         node: DungeonNode, pos: Tuple[int, int]):
        """ノードタイプに応じた画像アイコンを描画"""
        # 画像が利用可能な場合は画像を使用
        if node.node_type in self.node_images:
            image = self.node_images[node.node_type]
            
            # 選択可能なノードは1.3倍に拡大して目立たせる
            if node.available and not node.visited:
                # 1.3倍に拡大
                enlarged_size = (int(image.get_width() * 1.3), int(image.get_height() * 1.3))
                enlarged_image = pygame.transform.scale(image, enlarged_size)
                image_rect = enlarged_image.get_rect(center=pos)
                surface.blit(enlarged_image, image_rect)
            elif node.visited:
                # 訪問済みは暗くする
                darkened_image = image.copy()
                darkened_image.set_alpha(128)
                image_rect = darkened_image.get_rect(center=pos)
                surface.blit(darkened_image, image_rect)
            else:
                # 選択不可はグレースケール
                grayscale_image = image.copy()
                # シンプルなグレースケール変換
                grayscale_image.set_alpha(80)
                image_rect = grayscale_image.get_rect(center=pos)
                surface.blit(grayscale_image, image_rect)
                
            # ボスノードには追加でテキスト表示
            if node.node_type == NodeType.BOSS:
                small_font = pygame.font.Font(None, 24)
                if node.visited:
                    text_color = (160, 160, 160)
                elif node.available:
                    text_color = (255, 255, 255)
                else:
                    text_color = (100, 100, 100)
                boss_text = small_font.render("BOSS", True, text_color)
                # 選択可能なボスノードは少し下にずらす（拡大されるため）
                y_offset = 85 if (node.available and not node.visited) else 75
                text_rect = boss_text.get_rect(center=(pos[0], pos[1] + y_offset))
                surface.blit(boss_text, text_rect)
        else:
            # フォールバック：テキストアイコンを使用
            icon = self.node_icons.get(node.node_type, "?")
            
            # アイコンの色を決定
            if node.visited:
                text_color = (160, 160, 160)
            elif node.available:
                text_color = (255, 255, 255)
            else:
                text_color = (100, 100, 100)
            
            medium_font = pygame.font.Font(None, 64)
            icon_text = medium_font.render(icon, True, text_color)
            text_rect = icon_text.get_rect(center=pos)
            surface.blit(icon_text, text_rect)
    
    def _render_ui(self, surface: pygame.Surface, fonts: Dict[str, pygame.font.Font]):
        """UI要素を描画"""
        font_medium = fonts.get('medium', pygame.font.Font(None, 24))
        font_large = fonts.get('large', pygame.font.Font(None, 32))
        
        # タイトル（シンボル付き）
        title = font_large.render("♦ DUNGEON MAP ♦", True, Colors.WHITE)
        surface.blit(title, (self.map_area_x, 20))
        
        # 進行状況（シンボル付き）
        current, total = self.dungeon_map.get_current_floor_progress()
        progress_text = font_medium.render(f"● Floor: {current} / {total}", True, Colors.WHITE)
        surface.blit(progress_text, (self.map_area_x + self.map_area_width - 160, 20))
        
        # 現在のノード情報（シンボル付き）
        if self.dungeon_map.current_node:
            node_icon = self.node_icons.get(self.dungeon_map.current_node.node_type, "?")
            current_info = f"{node_icon} Current: {self.dungeon_map.current_node.node_type.value.title()}"
            info_text = font_medium.render(current_info, True, Colors.YELLOW)
            surface.blit(info_text, (self.map_area_x, self.map_area_y + self.map_area_height + 10))
        
        # 操作説明（シンボル付き）
        instructions = [
            "► Click on yellow-bordered nodes to move",
            "↑↓ Keys or Mouse Wheel to Scroll",
            "◄ ESC - Return to menu",
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
        
        # ツールチップの内容（シンボル付き）
        node_icon = self.node_icons.get(node.node_type, "?")
        lines = [
            f"{node_icon} Type: {node.node_type.value.title()}",
            f"▲ Floor: {node.floor + 1}",
        ]
        
        if node.enemy_type:
            lines.append(f"♦ Enemy: {node.enemy_type}")
        
        if node.visited:
            lines.append("● Status: Visited")
        elif node.available:
            lines.append("○ Status: Available")
        else:
            lines.append("■ Status: Locked")
        
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
        """ノードの描画位置を計算（スクロール考慮）"""
        x = self.map_area_x + (node.x + 1) * self.node_spacing_x
        y = self._get_node_y(node.floor)
        return (int(x), int(y))
    
    def _get_node_y(self, floor: int) -> int:
        """フロアのY座標を計算（スクロール考慮）"""
        # 上から下への順序（フロア0が上）
        base_y = self.map_area_y + (floor + 1) * self.node_spacing_y
        return int(base_y - self.scroll_y)
    
    def handle_click(self, pos: Tuple[int, int]) -> Optional[DungeonNode]:
        """クリック処理 - クリックされたノードを返す（アイコン画像基準）"""
        for node in self.dungeon_map.nodes.values():
            node_pos = self._get_node_position(node)
            
            # 画像のサイズを基準にクリック判定
            if node.node_type in self.node_images:
                image = self.node_images[node.node_type]
                
                # 選択可能なノードは1.3倍拡大されているのでクリック判定も調整
                if node.available and not node.visited:
                    enlarged_size = (int(image.get_width() * 1.3), int(image.get_height() * 1.3))
                    image_rect = pygame.Rect(0, 0, enlarged_size[0], enlarged_size[1])
                    image_rect.center = node_pos
                else:
                    image_rect = image.get_rect(center=node_pos)
                
                # 画像の範囲内でクリック判定
                if image_rect.collidepoint(pos):
                    return node
            else:
                # フォールバック：従来の円形判定
                distance = math.sqrt((pos[0] - node_pos[0])**2 + (pos[1] - node_pos[1])**2)
                if distance <= 60:  # デフォルトサイズをさらに大きく
                    return node
        
        return None
    
    def handle_mouse_motion(self, pos: Tuple[int, int]):
        """マウス移動処理 - ホバー状態を更新（アイコン画像基準）"""
        self.hovered_node = None
        self.hover_info = None  # ホバー情報をクリア
        
        for node in self.dungeon_map.nodes.values():
            node_pos = self._get_node_position(node)
            
            # 画像のサイズを基準にホバー判定
            if node.node_type in self.node_images:
                image = self.node_images[node.node_type]
                
                # 選択可能なノードは1.3倍拡大されているのでホバー判定も調整
                if node.available and not node.visited:
                    enlarged_size = (int(image.get_width() * 1.3), int(image.get_height() * 1.3))
                    image_rect = pygame.Rect(0, 0, enlarged_size[0], enlarged_size[1])
                    image_rect.center = node_pos
                else:
                    image_rect = image.get_rect(center=node_pos)
                
                # 画像の範囲内でホバー判定
                if image_rect.collidepoint(pos):
                    self.hovered_node = node
                    break
            else:
                # フォールバック：従来の円形判定
                distance = math.sqrt((pos[0] - node_pos[0])**2 + (pos[1] - node_pos[1])**2)
                if distance <= 60:  # デフォルトサイズをさらに大きく
                    self.hovered_node = node
                    break
    
    def set_selected_node(self, node: Optional[DungeonNode]):
        """選択ノードを設定"""
        self.selected_node = node
    
    def _render_status_bar(self, surface: pygame.Surface, fonts: Dict[str, pygame.font.Font]):
        """マップ上部にステータス情報を表示"""
        # エンジンが参照できない場合はスキップ
        if not hasattr(self.dungeon_map, 'engine'):
            return
        
        # 背景バー
        status_bg_rect = pygame.Rect(0, 0, SCREEN_WIDTH, 100)
        pygame.draw.rect(surface, (20, 20, 30), status_bg_rect)
        pygame.draw.rect(surface, Colors.GOLD, status_bg_rect, 2)
        
        # フォント設定
        font_small = fonts.get('small', pygame.font.Font(None, 24))
        font_medium = fonts.get('medium', pygame.font.Font(None, 28))
        
        # ステータステキストを用意
        try:
            player = self.dungeon_map.engine.player
            
            # 基本ステータス
            hp_text = f"{player.hp}/{player.max_hp}"
            gold_text = f"{player.gold}"
            
            # アイテム情報
            potion_count = 0
            artifact_count = 0
            
            if hasattr(player, 'inventory') and hasattr(player.inventory, 'items'):
                for item in player.inventory.items:
                    if hasattr(item, 'item_type') and hasattr(item, 'quantity'):
                        try:
                            item_type_str = item.item_type.value if hasattr(item.item_type, 'value') else str(item.item_type)
                            if item_type_str == 'potion':
                                potion_count += item.quantity
                            elif item_type_str == 'artifact':
                                artifact_count += item.quantity
                        except:
                            continue
            
            # 特殊ぷよの出現率情報
            special_puyo_rates = getattr(player, 'special_puyo_rates', {})
            
            potion_text = f"Potions: {potion_count}"
            artifact_text = f"Artifacts: {artifact_count}"
            
            # アイコン付きでHPとゴールドを描画
            y_pos = 35
            x_positions = [50, 200, 350, 500, 650]
            
            # HP表示（アイコン付き）
            if self.hp_icon:
                surface.blit(self.hp_icon, (x_positions[0], y_pos - 5))
                hp_text_surface = font_medium.render(hp_text, True, Colors.GREEN if player.hp > player.max_hp * 0.3 else Colors.RED)
                surface.blit(hp_text_surface, (x_positions[0] + 35, y_pos))
            else:
                # フォールバック
                hp_text_full = f"HP: {hp_text}"
                hp_text_surface = font_medium.render(hp_text_full, True, Colors.GREEN if player.hp > player.max_hp * 0.3 else Colors.RED)
                surface.blit(hp_text_surface, (x_positions[0], y_pos))
            
            # ゴールド表示（アイコン付き）
            if self.gold_icon:
                surface.blit(self.gold_icon, (x_positions[1], y_pos - 5))
                gold_text_surface = font_medium.render(gold_text, True, Colors.YELLOW)
                surface.blit(gold_text_surface, (x_positions[1] + 35, y_pos))
            else:
                # フォールバック
                gold_text_full = f"Gold: {gold_text}"
                gold_text_surface = font_medium.render(gold_text_full, True, Colors.YELLOW)
                surface.blit(gold_text_surface, (x_positions[1], y_pos))
            
            # 特殊ぷよ表示（アイコン付き、バトル画面と同じ仕様）
            special_x = x_positions[2]
            special_label = font_small.render("Special:", True, Colors.LIGHT_GRAY)
            surface.blit(special_label, (special_x, y_pos - 15))
            
            icon_x = special_x
            displayed_special_count = 0
            
            # マウスオーバーエリアをクリア
            self.special_puyo_hover_areas = []
            
            for puyo_type, rate in special_puyo_rates.items():
                # 出現率が0%より大きい特殊ぷよのみ表示（バトル画面と同じ仕様）
                if rate > 0.0 and puyo_type in self.special_puyo_images:
                    # アイコンを描画
                    icon = self.special_puyo_images[puyo_type]
                    icon_rect = pygame.Rect(icon_x, y_pos, 25, 25)
                    surface.blit(icon, icon_rect)
                    
                    # 出現率を描画
                    rate_text = f"{rate*100:.0f}%"
                    rate_surface = font_small.render(rate_text, True, Colors.WHITE)
                    surface.blit(rate_surface, (icon_x, y_pos + 25))
                    
                    # マウスオーバー検出エリアを記録
                    hover_rect = pygame.Rect(icon_x - 5, y_pos - 5, 35, 35)
                    self.special_puyo_hover_areas.append((hover_rect, puyo_type, rate))
                    
                    # マウスオーバー検出
                    mouse_pos = pygame.mouse.get_pos()
                    if hover_rect.collidepoint(mouse_pos):
                        self._set_special_puyo_hover_info(puyo_type, rate, mouse_pos)
                    
                    icon_x += 40
                    displayed_special_count += 1
            
            # 特殊ぷよを持っていない場合は「なし」と表示（バトル画面と同じ）
            if displayed_special_count == 0:
                no_special_text = font_small.render("なし", True, Colors.GRAY)
                surface.blit(no_special_text, (icon_x, y_pos + 10))
            
            # その他のステータス（テキストのみ）
            other_texts = [potion_text, artifact_text]
            other_colors = [Colors.PURPLE, Colors.ORANGE]
            
            for i, (text, color) in enumerate(zip(other_texts, other_colors), start=3):
                if i < len(x_positions):
                    text_surface = font_medium.render(text, True, color)
                    surface.blit(text_surface, (x_positions[i], y_pos))
                    
            # タイトル
            title_text = font_medium.render("Status", True, Colors.WHITE)
            surface.blit(title_text, (10, 5))
            
        except Exception as e:
            # エラー時はシンプルな表示
            try:
                error_text = font_small.render("Status info loading...", True, Colors.LIGHT_GRAY)
                surface.blit(error_text, (50, 25))
            except:
                pass  # フォントがない場合は何も表示しない
        
        # 特殊ぷよのマウスオーバー詳細表示
        if self.hover_info:
            self._render_special_puyo_tooltip(surface, fonts)
    
    def _set_special_puyo_hover_info(self, puyo_type: str, rate: float, mouse_pos: tuple):
        """特殊ぷよのホバー情報を設定"""
        try:
            from core.simple_special_puyo import SimpleSpecialType
            
            # puyo_typeが文字列の場合、SimpleSpecialTypeに変換
            if isinstance(puyo_type, str):
                for special_type in SimpleSpecialType:
                    if special_type.value == puyo_type:
                        puyo_enum = special_type
                        break
                else:
                    puyo_enum = None
            else:
                puyo_enum = puyo_type
            
            if puyo_enum:
                display_name = puyo_enum.get_display_name()
                description = puyo_enum.get_description()
                
                self.hover_info = {
                    'type': 'special_puyo',
                    'name': display_name,
                    'description': description,
                    'rate': rate,
                    'pos': (mouse_pos[0] + 10, mouse_pos[1] - 60)
                }
        except Exception as e:
            logger.warning(f"Error setting special puyo hover info: {e}")
    
    def _render_special_puyo_tooltip(self, surface: pygame.Surface, fonts: Dict[str, pygame.font.Font]):
        """特殊ぷよツールチップを描画"""
        if not self.hover_info or self.hover_info['type'] != 'special_puyo':
            return
        
        try:
            from core.game_engine import get_appropriate_font
            
            name = self.hover_info['name']
            description = self.hover_info['description']
            rate = self.hover_info['rate']
            pos = self.hover_info['pos']
            
            # ツールチップテキスト
            lines = [
                name,
                description,
                f"出現率: {rate*100:.0f}%"
            ]
            
            # フォントサイズを計算
            font_small = fonts.get('small', pygame.font.Font(None, 16))
            
            # ツールチップサイズを計算
            max_width = 0
            line_height = 20
            rendered_lines = []
            
            for line in lines:
                try:
                    font = get_appropriate_font(fonts, line, 'small')
                    rendered = font.render(line, True, Colors.WHITE)
                    rendered_lines.append(rendered)
                    max_width = max(max_width, rendered.get_width())
                except:
                    # フォールバック
                    rendered = font_small.render(line, True, Colors.WHITE)
                    rendered_lines.append(rendered)
                    max_width = max(max_width, rendered.get_width())
            
            tooltip_width = max_width + 20
            tooltip_height = len(lines) * line_height + 10
            
            # 画面境界チェック
            tooltip_x, tooltip_y = pos
            if tooltip_x + tooltip_width > SCREEN_WIDTH:
                tooltip_x = pos[0] - tooltip_width - 20
            if tooltip_y < 0:
                tooltip_y = 10
            elif tooltip_y + tooltip_height > SCREEN_HEIGHT:
                tooltip_y = SCREEN_HEIGHT - tooltip_height - 10
            
            # ツールチップ背景
            tooltip_rect = pygame.Rect(tooltip_x, tooltip_y, tooltip_width, tooltip_height)
            pygame.draw.rect(surface, (40, 40, 40), tooltip_rect)
            pygame.draw.rect(surface, (120, 120, 120), tooltip_rect, 2)
            
            # テキストを描画
            for i, rendered_line in enumerate(rendered_lines):
                surface.blit(rendered_line, (tooltip_x + 10, tooltip_y + 5 + i * line_height))
                
        except Exception as e:
            logger.warning(f"Error rendering special puyo tooltip: {e}")


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