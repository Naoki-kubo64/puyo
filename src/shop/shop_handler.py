"""
ショップハンドラー - アイテムとポーション購入システム
Drop Puzzle × Roguelike のショップ画面管理
"""

import pygame
import logging
import random
from typing import Dict, List, Optional, Union

from core.constants import *
from core.game_engine import GameEngine
from items.potions import Potion, create_random_potion, PotionType
from items.artifacts import Artifact, create_random_artifact
from inventory.player_inventory import ItemType, ItemRarity
from core.simple_special_puyo import SimpleSpecialType

logger = logging.getLogger(__name__)


class ShopItem:
    """ショップアイテムクラス"""
    
    def __init__(self, item: Union[Potion, Artifact, dict], price: int, slot_index: int):
        self.item = item
        self.price = price
        self.slot_index = slot_index
        self.sold = False
        self.item_type = self._determine_item_type()
    
    def get_name(self) -> str:
        if isinstance(self.item, dict):
            return self.item.get('name', 'Unknown Item')
        return self.item.name
    
    def get_description(self) -> str:
        if isinstance(self.item, dict):
            return self.item.get('description', 'No description')
        return self.item.description
    
    def get_color(self) -> tuple:
        if hasattr(self.item, 'color'):
            return self.item.color
        elif hasattr(self.item, 'rarity') and hasattr(self.item.rarity, 'color'):
            return self.item.rarity.color
        return Colors.WHITE
    
    def get_icon(self) -> str:
        if hasattr(self.item, 'icon'):
            return self.item.icon
        elif isinstance(self.item, dict) and 'icon' in self.item:
            return self.item['icon']
        return "🎁"
    
    def _determine_item_type(self) -> str:
        """アイテムタイプを判定"""
        if isinstance(self.item, Potion):
            return "potion"
        elif isinstance(self.item, Artifact):
            return "artifact"
        elif isinstance(self.item, dict) and 'type' in self.item:
            return self.item['type']
        return "unknown"


class ShopHandler:
    """ショップ画面の管理クラス"""
    
    def __init__(self, engine: GameEngine, current_node=None):
        self.engine = engine
        self.current_node = current_node
        
        # ショップの状態
        self.selected_index = 0
        self.purchase_completed = False
        self.last_purchased_item = None
        
        # プレイヤーのゴールド
        self.player_gold = self.engine.player.gold
        
        # UI設定
        self.background_color = (25, 15, 35)  # 紫がかった暗い色
        self.item_width = 180
        self.item_height = 200
        self.item_spacing = 20
        
        # ショップアイテムを生成
        self.shop_items = self._generate_shop_items()
        
        # レイアウト計算
        self.start_x = (SCREEN_WIDTH - (len(self.shop_items) * self.item_width + 
                       (len(self.shop_items) - 1) * self.item_spacing)) // 2
        self.start_y = 250
        
        logger.info(f"ShopHandler initialized with {len(self.shop_items)} items")
    
    def _generate_shop_items(self) -> List[ShopItem]:
        """ショップアイテムを生成（バランス調整済み）"""
        items = []
        
        # フロアレベルを取得（ダンジョンマップから）
        floor_level = 1
        if (hasattr(self.engine, 'persistent_dungeon_map') and 
            self.engine.persistent_dungeon_map and 
            self.current_node):
            floor_level = self.current_node.floor + 1
        
        # ポーション 2-3個（安価なアイテム）
        potion_count = random.randint(2, 3)
        for i in range(potion_count):
            potion = create_random_potion(floor_level)
            price = self._calculate_potion_price(potion)
            items.append(ShopItem(potion, price, len(items)))
        
        # 特殊ぷよ 1-2個（中価格のアイテム）- 新システム対応
        special_puyo_count = random.randint(1, 2)
        for i in range(special_puyo_count):
            special_puyo_item = self._create_special_puyo_item_new(floor_level)
            price = self._calculate_special_puyo_price_new(special_puyo_item)
            items.append(ShopItem(special_puyo_item, price, len(items)))
        
        # アーティファクト 1個（高価なアイテム）
        artifact = create_random_artifact(floor_level)
        price = self._calculate_artifact_price(artifact)
        items.append(ShopItem(artifact, price, len(items)))
        
        # HP回復ポーション（常に1個、安価）
        heal_potion = self._create_heal_potion()
        heal_price = self._calculate_potion_price(heal_potion)
        items.append(ShopItem(heal_potion, heal_price, len(items)))
        
        return items
    
    def _calculate_potion_price(self, potion: Potion) -> int:
        """ポーションの価格を計算（20円前後の相場）"""
        from inventory.player_inventory import ItemRarity
        
        base_prices = {
            ItemRarity.COMMON: 15,
            ItemRarity.UNCOMMON: 22,
            ItemRarity.RARE: 30,
            ItemRarity.EPIC: 40,
            ItemRarity.LEGENDARY: 55
        }
        base_price = base_prices.get(potion.rarity, 15)
        
        # ±20%のランダム要素
        variation = random.uniform(0.8, 1.2)
        return int(base_price * variation)
    
    def _calculate_artifact_price(self, artifact: Artifact) -> int:
        """アーティファクトの価格を計算（高級アイテム）"""
        from inventory.player_inventory import ItemRarity
        
        base_prices = {
            ItemRarity.COMMON: 45,
            ItemRarity.UNCOMMON: 65,
            ItemRarity.RARE: 90,
            ItemRarity.EPIC: 120,
            ItemRarity.LEGENDARY: 180
        }
        base_price = base_prices.get(artifact.rarity, 45)
        
        # ±15%のランダム要素
        variation = random.uniform(0.85, 1.15)
        return int(base_price * variation)
    
    def _create_special_puyo_item_new(self, floor_level: int) -> dict:
        """特殊ぷよアイテムを作成（新SimpleSpecialTypeシステム対応）"""
        # 全ての特殊ぷよタイプから選択
        available_types = list(SimpleSpecialType)
        selected_type = random.choice(available_types)
        
        # レアリティを決定
        rarity_weights = {
            ItemRarity.COMMON: 0.6,
            ItemRarity.UNCOMMON: 0.3,
            ItemRarity.RARE: 0.08,
            ItemRarity.EPIC: 0.02
        }
        
        rarities = list(rarity_weights.keys())
        weights = list(rarity_weights.values())
        rarity = random.choices(rarities, weights=weights)[0]
        
        # SimpleSpecialTypeから名前と説明を取得
        try:
            name = selected_type.get_display_name()
            description = selected_type.get_description()
        except:
            name = f"{selected_type.value.title()}ぷよ"
            description = "特殊効果"
        
        # アイコンを設定（ASCII文字）
        icons = {
            SimpleSpecialType.HEAL: "H",
            SimpleSpecialType.BOMB: "B",
            SimpleSpecialType.LIGHTNING: "L",
            SimpleSpecialType.SHIELD: "S",
            SimpleSpecialType.MULTIPLIER: "M",
            SimpleSpecialType.POISON: "P"
        }
        
        return {
            'type': 'special_puyo',
            'puyo_type': selected_type,
            'name': name,
            'description': description,
            'rarity': rarity,
            'icon': icons.get(selected_type, "*"),
            'color': rarity.color if hasattr(rarity, 'color') else Colors.WHITE
        }
    
    def _calculate_special_puyo_price_new(self, special_puyo_item: dict) -> int:
        """特殊ぷよの価格を計算（新システム対応）"""
        from inventory.player_inventory import ItemRarity
        
        base_prices = {
            ItemRarity.COMMON: 18,
            ItemRarity.UNCOMMON: 25,
            ItemRarity.RARE: 35,
            ItemRarity.EPIC: 50,
            ItemRarity.LEGENDARY: 70
        }
        rarity = special_puyo_item.get('rarity', ItemRarity.COMMON)
        base_price = base_prices.get(rarity, 18)
        
        # ±15%のランダム要素
        variation = random.uniform(0.85, 1.15)
        return int(base_price * variation)
    
    def _create_heal_potion(self) -> Potion:
        """基本的な回復ポーションを作成"""
        from inventory.player_inventory import ItemRarity
        return Potion(PotionType.HEALTH, ItemRarity.COMMON)
    
    def on_enter(self, previous_state):
        """ショップ画面開始"""
        logger.info("Entering shop")
        self.selected_index = 0
        self.purchase_completed = False
        self.last_purchased_item = None
        
        # プレイヤーのゴールドを更新
        self.player_gold = self.engine.player.gold
    
    def handle_event(self, event: pygame.event.Event):
        """イベント処理"""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:
                self.selected_index = (self.selected_index - 1) % len(self.shop_items)
            elif event.key == pygame.K_RIGHT:
                self.selected_index = (self.selected_index + 1) % len(self.shop_items)
            elif event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                self._attempt_purchase()
            elif event.key == pygame.K_ESCAPE:
                # ショップを離れる
                self._leave_shop()
        
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            # マウスクリックでアイテム購入
            clicked_index = self._get_clicked_item_index(event.pos)
            if clicked_index is not None:
                self.selected_index = clicked_index
                self._attempt_purchase()
        
        elif event.type == pygame.MOUSEMOTION:
            # マウスホバーで選択インデックス更新
            hovered_index = self._get_clicked_item_index(event.pos)
            if hovered_index is not None:
                self.selected_index = hovered_index
    
    def _get_clicked_item_index(self, mouse_pos: tuple) -> Optional[int]:
        """クリックされたアイテムのインデックスを取得"""
        mouse_x, mouse_y = mouse_pos
        
        for i in range(len(self.shop_items)):
            x = self.start_x + i * (self.item_width + self.item_spacing)
            y = self.start_y
            
            item_rect = pygame.Rect(x, y, self.item_width, self.item_height)
            if item_rect.collidepoint(mouse_x, mouse_y):
                return i
        
        return None
    
    def _attempt_purchase(self):
        """購入を試行"""
        if 0 <= self.selected_index < len(self.shop_items):
            shop_item = self.shop_items[self.selected_index]
            
            if shop_item.sold:
                logger.info("Item already sold")
                return
            
            if self.player_gold >= shop_item.price:
                # 購入成功
                self.player_gold -= shop_item.price
                shop_item.sold = True
                self.last_purchased_item = shop_item
                
                # プレイヤーのインベントリに追加
                self._add_item_to_inventory(shop_item.item)
                
                # プレイヤーデータのゴールドを更新
                self.engine.player.gold = self.player_gold
                
                logger.info(f"Purchased {shop_item.get_name()} for {shop_item.price} gold")
            else:
                logger.info(f"Not enough gold: need {shop_item.price}, have {self.player_gold}")
    
    def _add_item_to_inventory(self, item: Union[Potion, Artifact, dict]):
        """アイテムをインベントリに追加（新システム対応）"""
        if isinstance(item, Potion):
            # ポーションの効果を直接適用（既存の動作を維持）
            if item.potion_type == PotionType.HEALTH:
                self._apply_healing_effect(item)
                logger.info(f"Applied healing potion: {item.name}")
            else:
                # 他のポーションもプレイヤーインベントリに追加
                from inventory.player_inventory import create_item
                # 対応するアイテムIDを決定
                potion_mapping = {
                    PotionType.HEALTH: "health_potion_small",
                    PotionType.STRENGTH: "energy_potion",  # フォールバック
                }
                item_id = potion_mapping.get(item.potion_type, "health_potion_small")
                potion_item = create_item(item_id, quantity=1)
                if potion_item and self.engine.player.inventory.add_item(potion_item):
                    logger.info(f"Added potion to inventory: {item.name}")
                else:
                    logger.warning(f"Failed to add potion to inventory: {item.name}")
        elif isinstance(item, Artifact):
            # アーティファクト効果を直接適用
            self._apply_artifact_effect(item)
            # インベントリにも追加
            from inventory.player_inventory import create_item
            artifact_mapping = {
                "power": "power_ring",
                "vitality": "vitality_amulet",
                "luck": "lucky_coin",
                "merchant": "merchants_badge",
            }
            # アーティファクトIDを推測
            artifact_id = getattr(item, 'artifact_id', 'lucky_coin')
            if artifact_id not in ["power_ring", "vitality_amulet", "lucky_coin", "merchants_badge"]:
                artifact_id = "lucky_coin"
            
            artifact_item = create_item(artifact_id, quantity=1)
            if artifact_item and self.engine.player.inventory.add_item(artifact_item):
                logger.info(f"Added artifact to inventory: {item.name}")
            else:
                logger.warning(f"Failed to add artifact to inventory: {item.name}")
        elif isinstance(item, dict) and item.get('type') == 'special_puyo':
            # 特殊ぷよをプレイヤーに追加
            self._add_special_puyo_to_player(item)
            logger.info(f"Added special puyo: {item['name']}")
    
    def _apply_healing_effect(self, potion: Potion):
        """回復ポーションの効果を適用"""
        if potion.potion_type == PotionType.HEALTH:
            # プレイヤーのHPを回復（最大HPを超えないように）
            heal_amount = int(potion.effect.value)
            old_hp = self.engine.player.hp
            self.engine.player.hp = min(self.engine.player.hp + heal_amount, self.engine.player.max_hp)
            actual_heal = self.engine.player.hp - old_hp
            logger.info(f"Healed {actual_heal} HP. Current HP: {self.engine.player.hp}/{self.engine.player.max_hp}")
    
    def _apply_artifact_effect(self, artifact: Artifact):
        """アーティファクトの効果を適用"""
        # アーティファクトの効果をプレイヤーに適用
        if hasattr(artifact, 'effect_type') and hasattr(artifact, 'effect_value'):
            if artifact.effect_type == "max_hp":
                self.engine.player.max_hp += artifact.effect_value
                self.engine.player.hp += artifact.effect_value  # 現在HPも増加
            elif artifact.effect_type == "damage":
                # ダメージボーナスを適用
                if hasattr(self.engine.player, 'chain_damage_multiplier'):
                    self.engine.player.chain_damage_multiplier += artifact.effect_value / 100
            elif artifact.effect_type == "chain":
                # 連鎖ボーナスを適用
                if hasattr(self.engine.player, 'chain_damage_multiplier'):
                    self.engine.player.chain_damage_multiplier += artifact.effect_value / 100
            
            logger.info(f"Applied artifact effect: {artifact.effect_type} +{artifact.effect_value}")
        else:
            logger.warning(f"Unknown artifact type: {artifact}")
    
    def _add_special_puyo_to_player(self, special_puyo_item: dict):
        """特殊ぷよをプレイヤーに追加（新システム対応）"""
        puyo_type = special_puyo_item['puyo_type']
        
        # プレイヤーの特殊ぷよ出現率を5%上昇
        new_rate = self.engine.player.increase_special_puyo_rate(puyo_type.value, 0.05)
        logger.info(f"Special puyo {puyo_type.value} rate increased to {new_rate*100:.0f}%")
    
    def _leave_shop(self):
        """ショップを離れてマップに戻る"""
        try:
            from dungeon.map_handler import DungeonMapHandler
            
            # マップ進行処理
            if (hasattr(self.engine, 'persistent_dungeon_map') and self.engine.persistent_dungeon_map and 
                self.current_node):
                
                dungeon_map = self.engine.persistent_dungeon_map
                
                logger.info(f"Processing map progression after shop for node: {self.current_node.node_id}")
                
                # ノードを選択して次の階層を解放
                success = dungeon_map.select_node(self.current_node.node_id)
                if success:
                    available_nodes = dungeon_map.get_available_nodes()
                    logger.info(f"Map progression completed: {self.current_node.node_id} -> Available: {[n.node_id for n in available_nodes]}")
                else:
                    logger.error(f"Failed to progress map for node: {self.current_node.node_id}")
            
            # ダンジョンマップハンドラーを作成
            map_handler = DungeonMapHandler(self.engine)
            
            # ダンジョンマップ状態に変更
            self.engine.register_state_handler(GameState.DUNGEON_MAP, map_handler)
            self.engine.change_state(GameState.DUNGEON_MAP)
            
            logger.info("Returned to dungeon map after shop visit")
            
        except Exception as e:
            logger.error(f"Failed to return to dungeon map: {e}")
            # フォールバック: メニューに戻る
            self.engine.change_state(GameState.MENU)
    
    def render(self, surface: pygame.Surface):
        """描画処理"""
        # 背景
        surface.fill(self.background_color)
        
        # 背景装飾
        self._render_shop_atmosphere(surface)
        
        # タイトルとゴールド表示
        self._render_header(surface)
        
        # ショップアイテム
        self._render_shop_items(surface)
        
        # 購入完了メッセージ
        if self.last_purchased_item:
            self._render_purchase_message(surface)
        
        # 操作説明
        self._render_instructions(surface)
    
    def _render_shop_atmosphere(self, surface: pygame.Surface):
        """ショップの雰囲気を演出"""
        # 薄い紫の光の効果
        for i in range(3):
            light_radius = 200 + i * 100
            light_alpha = 20 - i * 5
            if light_alpha > 0:
                light_surface = pygame.Surface((light_radius * 2, light_radius * 2))
                light_surface.set_alpha(light_alpha)
                light_surface.fill((0, 0, 0))
                light_surface.set_colorkey((0, 0, 0))
                pygame.draw.circle(light_surface, (150, 100, 200), (light_radius, light_radius), light_radius)
                surface.blit(light_surface, (SCREEN_WIDTH // 2 - light_radius, SCREEN_HEIGHT // 2 - light_radius))
    
    def _render_header(self, surface: pygame.Surface):
        """ヘッダー情報を描画"""
        font_title = self.engine.fonts['title']
        font_large = self.engine.fonts['large']
        
        # ショップタイトル
        title_text = font_title.render("🛒 SHOP 🛒", True, Colors.WHITE)
        title_rect = title_text.get_rect(center=(SCREEN_WIDTH // 2, 80))
        surface.blit(title_text, title_rect)
        
        # ゴールド表示（アイコン付き）
        gold_text = font_large.render(f"💰 {self.player_gold} Gold", True, Colors.YELLOW)
        gold_rect = gold_text.get_rect(center=(SCREEN_WIDTH // 2, 130))
        surface.blit(gold_text, gold_rect)
    
    def _render_shop_items(self, surface: pygame.Surface):
        """ショップアイテムを描画"""
        font_medium = self.engine.fonts['medium']
        font_small = self.engine.fonts['small']
        
        for i, shop_item in enumerate(self.shop_items):
            x = self.start_x + i * (self.item_width + self.item_spacing)
            y = self.start_y
            
            # アイテム背景
            item_rect = pygame.Rect(x, y, self.item_width, self.item_height)
            
            # 売り切れまたは購入不可の場合の表示
            if shop_item.sold:
                bg_color = (40, 40, 40)  # グレーアウト
                border_color = Colors.GRAY
                text_alpha = 128
            elif self.player_gold < shop_item.price:
                bg_color = (60, 30, 30)  # 赤みがかった暗い色
                border_color = Colors.DARK_RED
                text_alpha = 180
            else:
                bg_color = (50, 30, 60)  # 通常の背景
                border_color = shop_item.get_color()
                text_alpha = 255
            
            # 選択中のアイテムはハイライト
            if i == self.selected_index and not shop_item.sold:
                pygame.draw.rect(surface, Colors.YELLOW, item_rect, 4)
            elif shop_item.sold:
                # 売り切れの場合はグレーボーダー
                pygame.draw.rect(surface, Colors.GRAY, item_rect, 2)
            
            pygame.draw.rect(surface, bg_color, item_rect)
            pygame.draw.rect(surface, border_color, item_rect, 2)
            
            if shop_item.sold:
                # 売り切れスタンプ
                sold_text = font_medium.render("SOLD", True, Colors.RED)
                sold_rect = sold_text.get_rect(center=(x + self.item_width // 2, y + self.item_height // 2))
                surface.blit(sold_text, sold_rect)
            else:
                # アイテムアイコン
                icon_text = font_medium.render(shop_item.get_icon(), True, shop_item.get_color())
                icon_rect = icon_text.get_rect(center=(x + self.item_width // 2, y + 40))
                surface.blit(icon_text, icon_rect)
                
                # アイテム名（レアリティ色で表示）
                item_name = shop_item.get_name()
                if len(item_name) > 15:
                    item_name = item_name[:12] + "..."
                
                # アイテム名をレアリティ色で表示
                name_color = shop_item.get_color() if not shop_item.sold else Colors.GRAY
                name_text = font_small.render(item_name, True, name_color)
                if text_alpha != 255:
                    name_text.set_alpha(text_alpha)
                name_rect = name_text.get_rect(center=(x + self.item_width // 2, y + 80))
                surface.blit(name_text, name_rect)
                
                # 価格表示
                price_color = Colors.YELLOW if self.player_gold >= shop_item.price else Colors.RED
                price_text = font_medium.render(f"{shop_item.price}G", True, price_color)
                if text_alpha != 255:
                    price_text.set_alpha(text_alpha)
                price_rect = price_text.get_rect(center=(x + self.item_width // 2, y + self.item_height - 30))
                surface.blit(price_text, price_rect)
                
                # アイテム説明
                desc_text = shop_item.get_description()
                if len(desc_text) > 25:
                    desc_text = desc_text[:22] + "..."
                desc_render = font_small.render(desc_text, True, Colors.LIGHT_GRAY)
                if text_alpha != 255:
                    desc_render.set_alpha(text_alpha)
                desc_rect = desc_render.get_rect(center=(x + self.item_width // 2, y + 110))
                surface.blit(desc_render, desc_rect)
    
    def _render_purchase_message(self, surface: pygame.Surface):
        """購入完了メッセージを描画"""
        font_medium = self.engine.fonts['medium']
        
        message = f"Purchased {self.last_purchased_item.get_name()}!"
        message_text = font_medium.render(message, True, Colors.GREEN)
        message_rect = message_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 120))
        surface.blit(message_text, message_rect)
    
    def _render_instructions(self, surface: pygame.Surface):
        """操作説明を描画"""
        font_small = self.engine.fonts['small']
        
        instructions = [
            "← → - Select item",
            "Enter/Space - Purchase",
            "ESC - Leave shop"
        ]
        
        for i, instruction in enumerate(instructions):
            text = font_small.render(instruction, True, Colors.LIGHT_GRAY)
            text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 80 + i * 20))
            surface.blit(text, text_rect)
    
    def update(self, dt: float):
        """更新処理"""
        pass