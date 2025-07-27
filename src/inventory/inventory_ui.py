import pygame
from typing import List, Optional
from ..core.state_handler import StateHandler
from ..core.constants import GameState, Colors
from ..core.game_engine import GameEngine
from .player_inventory import PlayerInventory, Item, ItemType, ItemRarity

class InventoryUI(StateHandler):
    def __init__(self, engine: GameEngine):
        super().__init__(engine)
        self.inventory: PlayerInventory = engine.player.inventory
        self.font_large = pygame.font.Font(None, 48)
        self.font_medium = pygame.font.Font(None, 36)
        self.font_small = pygame.font.Font(None, 28)
        
        self.selected_item: Optional[Item] = None
        self.hovered_item: Optional[Item] = None
        self.item_rects: List[pygame.Rect] = []
        self.scroll_offset = 0
        self.max_scroll = 0
        
        # フィルター設定
        self.current_filter = None  # None = すべて表示
        self.filter_buttons = []
        
    def handle_event(self, event: pygame.event.Event) -> bool:
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE or event.key == pygame.K_i:
                # インベントリを閉じる
                self.engine.change_state(GameState.DUNGEON_MAP)
                return True
            elif event.key == pygame.K_UP:
                self._scroll(-30)
            elif event.key == pygame.K_DOWN:
                self._scroll(30)
        
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # 左クリック
                self._handle_left_click(event.pos)
            elif event.button == 4:  # マウスホイール上
                self._scroll(-30)
            elif event.button == 5:  # マウスホイール下
                self._scroll(30)
        
        elif event.type == pygame.MOUSEMOTION:
            self._handle_mouse_hover(event.pos)
        
        return False
    
    def _handle_left_click(self, pos: tuple):
        """左クリック処理"""
        # フィルターボタンのチェック
        for i, rect in enumerate(self.filter_buttons):
            if rect.collidepoint(pos):
                filter_types = [None, ItemType.ARTIFACT, ItemType.POTION, ItemType.MATERIAL, ItemType.CARD]
                self.current_filter = filter_types[i]
                return
        
        # アイテムのクリック処理
        for i, rect in enumerate(self.item_rects):
            if rect.collidepoint(pos):
                items = self._get_filtered_items()
                if i < len(items):
                    item = items[i]
                    self.selected_item = item
                    self._use_item(item)
                return
    
    def _handle_mouse_hover(self, pos: tuple):
        """マウスホバー処理"""
        self.hovered_item = None
        for i, rect in enumerate(self.item_rects):
            if rect.collidepoint(pos):
                items = self._get_filtered_items()
                if i < len(items):
                    self.hovered_item = items[i]
                break
    
    def _use_item(self, item: Item):
        """アイテム使用"""
        if item.consumable:
            # 消耗品の使用
            if item.item_type == ItemType.POTION:
                if "health" in item.id:
                    # 体力ポーション
                    if self.engine.player.hp < self.engine.player.max_hp:
                        used_item = self.inventory.use_consumable(item.id)
                        if used_item:
                            self.engine.player.heal(used_item.effect_value)
                            self._show_message(f"{used_item.name}を使用！HP{used_item.effect_value}回復")\n                elif "energy" in item.id:
                    # エネルギーポーション
                    used_item = self.inventory.use_consumable(item.id)
                    if used_item:
                        self.engine.player.energy += used_item.effect_value
                        self._show_message(f"{used_item.name}を使用！エネルギー{used_item.effect_value}増加")
    
    def _show_message(self, message: str):
        """メッセージ表示（簡易実装）"""
        print(f"[インベントリ] {message}")  # 後でUI表示に変更
    
    def _scroll(self, amount: int):
        """スクロール処理"""
        self.scroll_offset += amount
        self.scroll_offset = max(0, min(self.scroll_offset, self.max_scroll))
    
    def _get_filtered_items(self) -> List[Item]:
        """フィルター適用後のアイテムリスト"""
        if self.current_filter is None:
            return self.inventory.items
        return self.inventory.get_items_by_type(self.current_filter)
    
    def update(self, dt: float):
        pass
    
    def render(self, screen: pygame.Surface):
        # 背景
        screen.fill(Colors.DARK_BLUE)
        
        # タイトル
        title_text = self.font_large.render("インベントリ", True, Colors.GOLD)
        title_rect = title_text.get_rect(center=(screen.get_width() // 2, 50))
        screen.blit(title_text, title_rect)
        
        # 統計情報
        self._render_stats(screen)
        
        # フィルターボタン
        self._render_filter_buttons(screen)
        
        # アイテムリスト
        self._render_item_list(screen)
        
        # アイテム詳細（選択またはホバー時）
        if self.hovered_item or self.selected_item:
            self._render_item_details(screen, self.hovered_item or self.selected_item)
        
        # 操作説明
        self._render_controls(screen)
    
    def _render_stats(self, screen: pygame.Surface):
        """統計情報表示"""
        y_offset = 100
        
        # アイテム数
        item_count_text = f"アイテム: {len(self.inventory.items)}/{self.inventory.max_items}"
        item_count_surface = self.font_small.render(item_count_text, True, Colors.WHITE)
        screen.blit(item_count_surface, (20, y_offset))
        
        # 総価値
        total_value = self.inventory.get_total_value()
        value_text = f"総価値: {total_value}G"
        value_surface = self.font_small.render(value_text, True, Colors.GOLD)
        screen.blit(value_surface, (200, y_offset))
        
        # アクティブ効果
        effects = self.inventory.get_artifact_effects()
        if effects:
            effect_text = "アクティブ効果: "
            if "shop_discount" in effects:
                effect_text += f"ショップ割引{effects['shop_discount']}% "
            if "damage_bonus" in effects:
                effect_text += f"ダメージ+{effects['damage_bonus']}% "
            if "max_hp_bonus" in effects:
                effect_text += f"最大HP+{effects['max_hp_bonus']} "
            
            effect_surface = self.font_small.render(effect_text, True, Colors.GREEN)
            screen.blit(effect_surface, (400, y_offset))
    
    def _render_filter_buttons(self, screen: pygame.Surface):
        """フィルターボタン表示"""
        self.filter_buttons.clear()
        y_offset = 140
        
        filters = [
            ("すべて", None),
            ("アーティファクト", ItemType.ARTIFACT),
            ("ポーション", ItemType.POTION),
            ("材料", ItemType.MATERIAL),
            ("カード", ItemType.CARD)
        ]
        
        x_offset = 20
        for i, (name, filter_type) in enumerate(filters):
            button_width = 120
            button_height = 30
            button_rect = pygame.Rect(x_offset, y_offset, button_width, button_height)
            self.filter_buttons.append(button_rect)
            
            # ボタンの色
            if self.current_filter == filter_type:
                button_color = Colors.GOLD
                text_color = Colors.BLACK
            else:
                button_color = Colors.GRAY
                text_color = Colors.WHITE
            
            pygame.draw.rect(screen, button_color, button_rect)
            pygame.draw.rect(screen, Colors.WHITE, button_rect, 2)
            
            # ボタンテキスト
            button_text = self.font_small.render(name, True, text_color)
            text_rect = button_text.get_rect(center=button_rect.center)
            screen.blit(button_text, text_rect)
            
            x_offset += button_width + 10
    
    def _render_item_list(self, screen: pygame.Surface):
        """アイテムリスト表示"""
        self.item_rects.clear()
        items = self._get_filtered_items()
        
        list_start_y = 200
        item_height = 60
        visible_height = screen.get_height() - list_start_y - 100
        visible_items = visible_height // item_height
        
        # スクロール計算
        start_index = self.scroll_offset // item_height
        end_index = min(start_index + visible_items, len(items))
        self.max_scroll = max(0, (len(items) - visible_items) * item_height)
        
        for i in range(start_index, end_index):
            item = items[i]
            y_pos = list_start_y + (i - start_index) * item_height - (self.scroll_offset % item_height)
            
            # アイテムの矩形
            item_rect = pygame.Rect(20, y_pos, screen.get_width() - 300, item_height - 5)
            self.item_rects.append(item_rect)
            
            # ホバー効果
            if item == self.hovered_item:
                pygame.draw.rect(screen, Colors.DARK_GRAY, item_rect)
            
            # レアリティの枠線
            pygame.draw.rect(screen, item.rarity.color, item_rect, 3)
            
            # アイテムアイコン（簡易）
            icon_rect = pygame.Rect(item_rect.x + 5, item_rect.y + 5, 40, 40)
            pygame.draw.rect(screen, item.rarity.color, icon_rect)
            
            # アイテム名
            name_text = self.font_medium.render(item.get_display_name(), True, Colors.WHITE)
            screen.blit(name_text, (item_rect.x + 55, item_rect.y + 5))
            
            # アイテム説明
            desc_text = self.font_small.render(item.description, True, Colors.LIGHT_GRAY)
            screen.blit(desc_text, (item_rect.x + 55, item_rect.y + 30))
            
            # 価値
            value_text = self.font_small.render(f"{item.get_value()}G", True, Colors.GOLD)
            screen.blit(value_text, (item_rect.right - 100, item_rect.y + 20))
    
    def _render_item_details(self, screen: pygame.Surface, item: Item):
        """アイテム詳細表示"""
        detail_x = screen.get_width() - 280
        detail_y = 200
        detail_width = 260
        detail_height = 300
        
        # 詳細パネル
        detail_rect = pygame.Rect(detail_x, detail_y, detail_width, detail_height)
        pygame.draw.rect(screen, Colors.BLACK, detail_rect)
        pygame.draw.rect(screen, item.rarity.color, detail_rect, 3)
        
        y_offset = detail_y + 20
        
        # アイテム名
        name_text = self.font_medium.render(item.name, True, item.rarity.color)
        screen.blit(name_text, (detail_x + 10, y_offset))
        y_offset += 40
        
        # レアリティ
        rarity_text = self.font_small.render(f"レアリティ: {item.rarity.display_name}", True, item.rarity.color)
        screen.blit(rarity_text, (detail_x + 10, y_offset))
        y_offset += 30
        
        # タイプ
        type_text = self.font_small.render(f"タイプ: {item.item_type.value}", True, Colors.WHITE)
        screen.blit(type_text, (detail_x + 10, y_offset))
        y_offset += 30
        
        # 説明（複数行対応）
        desc_lines = self._wrap_text(item.description, detail_width - 20)
        for line in desc_lines:
            desc_text = self.font_small.render(line, True, Colors.LIGHT_GRAY)
            screen.blit(desc_text, (detail_x + 10, y_offset))
            y_offset += 25
        
        y_offset += 10
        
        # 効果値（該当する場合）
        if item.effect_value > 0:
            effect_text = self.font_small.render(f"効果: {item.effect_value}", True, Colors.GREEN)
            screen.blit(effect_text, (detail_x + 10, y_offset))
            y_offset += 25
        
        # 価値
        value_text = self.font_small.render(f"価値: {item.get_value()}G", True, Colors.GOLD)
        screen.blit(value_text, (detail_x + 10, y_offset))
        y_offset += 25
        
        # 使用可能かどうか
        if item.consumable:
            use_text = self.font_small.render("クリックで使用", True, Colors.GREEN)
            screen.blit(use_text, (detail_x + 10, y_offset))
    
    def _wrap_text(self, text: str, max_width: int) -> List[str]:
        """テキストを指定幅で折り返し"""
        words = text.split(' ')
        lines = []
        current_line = ""
        
        for word in words:
            test_line = current_line + (" " if current_line else "") + word
            test_width = self.font_small.size(test_line)[0]
            
            if test_width <= max_width:
                current_line = test_line
            else:
                if current_line:
                    lines.append(current_line)
                current_line = word
        
        if current_line:
            lines.append(current_line)
        
        return lines
    
    def _render_controls(self, screen: pygame.Surface):
        """操作説明表示"""
        controls_y = screen.get_height() - 60
        
        controls = [
            "ESC/I: 閉じる",
            "↑↓: スクロール",
            "クリック: アイテム使用",
            "ホイール: スクロール"
        ]
        
        x_offset = 20
        for control in controls:
            control_text = self.font_small.render(control, True, Colors.LIGHT_GRAY)
            screen.blit(control_text, (x_offset, controls_y))
            x_offset += control_text.get_width() + 30