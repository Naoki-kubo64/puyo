"""
ダンジョンマップハンドラー - マップ画面の状態管理
Drop Puzzle × Roguelike のダンジョンマップ操作とゲーム状態遷移
"""

import pygame
import logging
from typing import Optional

from core.constants import *
from core.game_engine import GameEngine
from .dungeon_map import DungeonMap, DungeonNode, NodeType
from .map_renderer import MapRenderer

logger = logging.getLogger(__name__)


class DungeonMapHandler:
    """ダンジョンマップ画面の管理クラス"""
    
    def __init__(self, engine: GameEngine, dungeon_map: Optional[DungeonMap] = None):
        self.engine = engine
        
        # ダンジョンマップ（新規作成または既存使用）
        if dungeon_map is None:
            # エンジンに保存されているマップがあれば使用、なければ新規作成
            if hasattr(engine, 'persistent_dungeon_map') and engine.persistent_dungeon_map is not None:
                self.dungeon_map = engine.persistent_dungeon_map
                logger.info("Using existing dungeon map from engine")
            else:
                self.dungeon_map = DungeonMap(total_floors=15)
                # エンジンに保存
                engine.persistent_dungeon_map = self.dungeon_map
                logger.info("Created new dungeon map and saved to engine")
        else:
            self.dungeon_map = dungeon_map
            # エンジンに保存
            engine.persistent_dungeon_map = self.dungeon_map
        
        # レンダラー
        self.map_renderer = MapRenderer(self.dungeon_map)
        
        # 状態管理
        self.transition_pending = False
        self.selected_node: Optional[DungeonNode] = None
        
        # エンジンに確実に保存
        self.engine.persistent_dungeon_map = self.dungeon_map
        logger.info(f"Map handler initialized with {len(self.dungeon_map.nodes)} nodes")
        
        # 現在の進行に応じて適切な位置にスクロール
        self._auto_scroll_to_current_position()
        
        logger.info("DungeonMapHandler initialized")
    
    def on_enter(self, previous_state):
        """マップ画面開始時の処理"""
        logger.info("Entering dungeon map state")
        self.transition_pending = False
        self.selected_node = None
        
        # 最初の訪問なら開始ノードを選択可能にする
        if not self.dungeon_map.current_node:
            self._initialize_starting_position()
    
    def on_exit(self):
        """マップ画面終了時の処理"""
        logger.info("Exiting dungeon map state")
    
    def update(self, dt: float):
        """更新処理"""
        # 特に更新が必要な要素はないが、将来的にアニメーション等で使用
        pass
    
    def handle_event(self, event: pygame.event.Event):
        """イベント処理"""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                # メインメニューに戻る
                self.engine.change_state(GameState.MENU)
            elif event.key == pygame.K_i:
                # インベントリを開く
                self._open_inventory()
            elif event.key == pygame.K_UP:
                # 上スクロール
                self._scroll(-30)
            elif event.key == pygame.K_DOWN:
                # 下スクロール
                self._scroll(30)
        
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # 左クリック
                self._handle_left_click(event.pos)
            elif event.button == 4:  # マウスホイール上
                self._scroll(-30)
            elif event.button == 5:  # マウスホイール下
                self._scroll(30)
        
        elif event.type == pygame.MOUSEMOTION:
            # マウスホバー処理
            self.map_renderer.handle_mouse_motion(event.pos)
    
    def _scroll(self, delta_y: int):
        """マップをスクロール"""
        old_scroll = self.map_renderer.scroll_y
        new_scroll = max(0, min(self.map_renderer.max_scroll_y, old_scroll + delta_y))
        self.map_renderer.scroll_y = new_scroll
        
        if new_scroll != old_scroll:
            logger.debug(f"Scrolled: {old_scroll} -> {new_scroll}")
    
    def _auto_scroll_to_current_position(self):
        """現在の進行状況に基づいて適切な位置にスクロール"""
        if self.dungeon_map.current_node:
            # 現在のノードが見える位置にスクロール
            current_floor = self.dungeon_map.current_node.floor
        else:
            # 利用可能なノードの最も進んだフロアにスクロール
            available_nodes = self.dungeon_map.get_available_nodes()
            if available_nodes:
                current_floor = max(node.floor for node in available_nodes)
            else:
                current_floor = 0
        
        # 目標Y位置を計算
        target_y = self.map_renderer.map_area_y + (current_floor + 1) * self.map_renderer.node_spacing_y
        
        # スクロール位置を調整（ノードが中央付近に来るように）
        scroll_target = target_y - self.map_renderer.map_area_height // 2
        scroll_target = max(0, min(self.map_renderer.max_scroll_y, scroll_target))
        
        self.map_renderer.scroll_y = scroll_target
        logger.debug(f"Auto-scrolled to floor {current_floor}, scroll_y: {scroll_target}")
    
    def render(self, surface: pygame.Surface):
        """描画処理"""
        # 背景クリア
        surface.fill(Colors.BLACK)
        
        # マップを描画
        self.map_renderer.render(surface, self.engine.fonts)
        
        # 遷移中の場合はオーバーレイ表示
        if self.transition_pending:
            self._render_transition_overlay(surface)
    
    def _handle_left_click(self, pos):
        """左クリック処理"""
        clicked_node = self.map_renderer.handle_click(pos)
        
        if clicked_node is None:
            return
        
        logger.debug(f"Clicked node: {clicked_node.node_id}")
        
        # 選択可能なノードかチェック
        if not clicked_node.available:
            logger.info(f"Node {clicked_node.node_id} is not available")
            return
        
        # ノード選択
        self.selected_node = clicked_node
        self.map_renderer.set_selected_node(clicked_node)
        
        # ノードタイプに応じて遷移
        self._process_node_selection(clicked_node)
    
    def _process_node_selection(self, node: DungeonNode):
        """ノード選択処理"""
        # 戦闘前には何も変更しない！
        # 戦闘ハンドラーに現在選択中のノードを渡すだけ
        logger.info(f"Selected node for battle: {node.node_id}")
        
        # ノードタイプに応じて遷移
        if node.node_type == NodeType.BATTLE:
            self._transition_to_battle(node)
        elif node.node_type == NodeType.BOSS:
            self._transition_to_boss_battle(node)
        elif node.node_type == NodeType.ELITE:
            self._transition_to_elite_battle(node)
        elif node.node_type == NodeType.TREASURE:
            self._transition_to_treasure(node)
        elif node.node_type == NodeType.EVENT:
            self._transition_to_event(node)
        elif node.node_type == NodeType.REST:
            self._transition_to_rest(node)
        elif node.node_type == NodeType.SHOP:
            self._transition_to_shop(node)
        else:
            logger.warning(f"Unknown node type: {node.node_type}")
    
    def _transition_to_battle(self, node: DungeonNode):
        """通常戦闘への遷移"""
        logger.info(f"Transitioning to battle: {node.enemy_type}")
        self.transition_pending = True
        
        try:
            from battle.battle_handler import BattleHandler
            
            # 戦闘ハンドラーを作成（現在のノード情報を渡す）
            battle_handler = BattleHandler(self.engine, floor_level=node.floor + 1, current_node=node)
            
            # 戦闘状態に変更
            self.engine.register_state_handler(GameState.REAL_BATTLE, battle_handler)
            self.engine.change_state(GameState.REAL_BATTLE)
            
            logger.info(f"Successfully transitioned to battle on floor {node.floor}")
            
        except Exception as e:
            logger.error(f"Failed to transition to battle: {e}")
            # エラー時は戦闘シミュレーション
            logger.info("Battle simulation - returning to map")
        
        self.transition_pending = False
    
    def _transition_to_boss_battle(self, node: DungeonNode):
        """ボス戦への遷移"""
        logger.info(f"Transitioning to boss battle: {node.enemy_type}")
        self.transition_pending = True
        
        try:
            from battle.battle_handler import BattleHandler
            
            # ボス戦用の戦闘ハンドラーを作成（現在のノード情報を渡す）
            battle_handler = BattleHandler(self.engine, floor_level=node.floor + 1, current_node=node)
            
            # 戦闘状態に変更
            self.engine.register_state_handler(GameState.REAL_BATTLE, battle_handler)
            self.engine.change_state(GameState.REAL_BATTLE)
            
            logger.info(f"Successfully transitioned to boss battle on floor {node.floor}")
            
        except Exception as e:
            logger.error(f"Failed to transition to boss battle: {e}")
            logger.info("Boss battle simulation - returning to map")
        
        self.transition_pending = False
    
    def _transition_to_elite_battle(self, node: DungeonNode):
        """エリート戦への遷移"""
        logger.info(f"Transitioning to elite battle: {node.enemy_type}")
        self.transition_pending = True
        
        try:
            from battle.battle_handler import BattleHandler
            
            # エリート戦用の戦闘ハンドラーを作成（現在のノード情報を渡す）
            battle_handler = BattleHandler(self.engine, floor_level=node.floor + 1, current_node=node)
            
            # 戦闘状態に変更
            self.engine.register_state_handler(GameState.REAL_BATTLE, battle_handler)
            self.engine.change_state(GameState.REAL_BATTLE)
            
            logger.info(f"Successfully transitioned to elite battle on floor {node.floor}")
            
        except Exception as e:
            logger.error(f"Failed to transition to elite battle: {e}")
            logger.info("Elite battle simulation - returning to map")
        
        self.transition_pending = False
    
    def _transition_to_treasure(self, node: DungeonNode):
        """宝箱への遷移"""
        logger.info("Opening treasure chest")
        self.transition_pending = True
        
        try:
            from treasure.treasure_handler import TreasureHandler
            
            # 宝箱ハンドラーを作成
            treasure_handler = TreasureHandler(self.engine, current_node=node)
            
            # 宝箱状態に変更
            self.engine.register_state_handler(GameState.TREASURE, treasure_handler)
            self.engine.change_state(GameState.TREASURE)
            
            logger.info("Successfully transitioned to treasure chest")
            
        except Exception as e:
            logger.error(f"Failed to transition to treasure chest: {e}")
            # エラー時は簡易宝箱シミュレーション
            self._simulate_treasure()
        
        self.transition_pending = False
    
    def _simulate_treasure(self):
        """宝箱シミュレーション（フォールバック）"""
        # 簡易報酬獲得（新しいプレイヤーデータシステム使用）
        bonus_gold = random.randint(50, 100)
        self.engine.player.gain_gold(bonus_gold)
        
        # HP強化と回復
        hp_bonus = random.randint(10, 20)
        self.engine.player.level_up_skill("max_hp", hp_bonus)
        self.engine.player.heal(hp_bonus)
        
        # 統計情報更新
        self.engine.player.visit_room("treasure")
        
        logger.info(f"Treasure simulation: gained {bonus_gold} gold and {hp_bonus} max HP")
    
    def _transition_to_event(self, node: DungeonNode):
        """イベントへの遷移"""
        logger.info(f"Transitioning to event from node {node.node_id}")
        try:
            from event.event_handler import EventHandler
            event_handler = EventHandler(self.engine, current_node=node)
            self.engine.register_state_handler(GameState.EVENT, event_handler)
            self.engine.change_state(GameState.EVENT)
            node.visited = True
        except Exception as e:
            logger.error(f"Failed to create event handler: {e}")
            self._simulate_event()
            node.visited = True
    
    def _simulate_event(self):
        """イベントシステムのフォールバック - 簡単なランダムイベント"""
        import random
        
        # ランダムイベントのシミュレーション
        events = [
            ("幸運の発見", 30, 0, "道端で金貨を発見した！"),
            ("休憩", 0, 15, "静かな場所で休憩した。"),
            ("危険な罠", -20, -8, "罠にかかってしまった..."),
            ("商人との出会い", 50, 0, "親切な商人からボーナスを受け取った！"),
            ("謎の祝福", 0, 5, "謎の力により体力が向上した！")
        ]
        
        event_name, gold_change, hp_change, message = random.choice(events)
        
        # プレイヤーに効果を適用
        if gold_change != 0:
            self.engine.player.gold += gold_change
        if hp_change > 0:
            self.engine.player.heal(hp_change)
        elif hp_change < 0:
            self.engine.player.take_damage(abs(hp_change))
        
        logger.info(f"Random event: {event_name} - {message}")
    
    def _transition_to_rest(self, node: DungeonNode):
        """休憩所への遷移"""
        logger.info("Entering rest site")
        self.transition_pending = True
        
        try:
            from rest.rest_handler import RestHandler
            
            # 休憩所ハンドラーを作成
            rest_handler = RestHandler(self.engine, current_node=node)
            
            # 休憩所状態に変更
            self.engine.register_state_handler(GameState.REST, rest_handler)
            self.engine.change_state(GameState.REST)
            
            logger.info("Successfully transitioned to rest area")
            
        except Exception as e:
            logger.error(f"Failed to transition to rest area: {e}")
            # エラー時は簡易休憩所シミュレーション
            self._simulate_rest()
        
        self.transition_pending = False
    
    def _simulate_rest(self):
        """休憩所シミュレーション（フォールバック）"""
        # 簡易HP回復
        heal_amount = self.engine.game_data.player_max_hp // 3
        old_hp = self.engine.game_data.player_hp
        self.engine.game_data.player_hp = min(
            self.engine.game_data.player_max_hp,
            self.engine.game_data.player_hp + heal_amount
        )
        actual_heal = self.engine.game_data.player_hp - old_hp
        logger.info(f"Rest simulation: healed {actual_heal} HP")
    
    def _transition_to_shop(self, node: DungeonNode):
        """ショップへの遷移"""
        logger.info("Entering shop")
        self.transition_pending = True
        
        try:
            from shop.shop_handler import ShopHandler
            
            # ショップハンドラーを作成
            shop_handler = ShopHandler(self.engine, current_node=node)
            
            # ショップ状態に変更
            self.engine.register_state_handler(GameState.SHOP, shop_handler)
            self.engine.change_state(GameState.SHOP)
            
            logger.info("Successfully transitioned to shop")
            
        except Exception as e:
            logger.error(f"Failed to transition to shop: {e}")
            # エラー時は簡易ショップシミュレーション
            self._simulate_shop()
        
        self.transition_pending = False
    
    def _simulate_shop(self):
        """ショップシミュレーション（フォールバック）"""
        # 簡易ゴールド獲得
        if not hasattr(self.engine.game_data, 'gold'):
            self.engine.game_data.gold = 0
        bonus_gold = random.randint(20, 50)
        self.engine.game_data.gold += bonus_gold
        logger.info(f"Shop simulation: gained {bonus_gold} gold")
    
    def _initialize_starting_position(self):
        """開始位置を初期化"""
        available_nodes = self.dungeon_map.get_available_nodes()
        logger.info(f"Starting nodes available: {[n.node_id for n in available_nodes]}")
        
        if available_nodes:
            # デバッグ用：最初のノードの接続情報を確認
            first_node = available_nodes[0]
            logger.info(f"First node {first_node.node_id} connections: {first_node.connections}")
        else:
            logger.warning("No starting nodes available - this should not happen!")
    
    def _render_transition_overlay(self, surface: pygame.Surface):
        """遷移中のオーバーレイを描画"""
        # 半透明オーバーレイ
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(128)
        overlay.fill(Colors.BLACK)
        surface.blit(overlay, (0, 0))
        
        # 遷移中メッセージ
        font_large = self.engine.fonts['large']
        if self.selected_node:
            message = f"Entering {self.selected_node.node_type.value.title()}..."
        else:
            message = "Transitioning..."
        
        text = font_large.render(message, True, Colors.WHITE)
        text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        surface.blit(text, text_rect)
    
    def get_dungeon_map(self) -> DungeonMap:
        """ダンジョンマップを取得"""
        return self.dungeon_map
    
    def _open_inventory(self):
        """インベントリを開く"""
        try:
            from inventory.inventory_ui import InventoryUI
            inventory_ui = InventoryUI(self.engine)
            self.engine.register_state_handler(GameState.INVENTORY, inventory_ui)
            self.engine.change_state(GameState.INVENTORY)
        except Exception as e:
            logger.error(f"Failed to open inventory: {e}")
    
    def set_dungeon_map(self, dungeon_map: DungeonMap):
        """ダンジョンマップを設定"""
        self.dungeon_map = dungeon_map
        self.map_renderer = MapRenderer(dungeon_map)


if __name__ == "__main__":
    # テスト実行
    import sys
    import os
    
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
    
    pygame.init()
    from core.game_engine import GameEngine
    
    logging.basicConfig(level=logging.INFO)
    
    engine = GameEngine()
    handler = DungeonMapHandler(engine)
    
    print("DungeonMapHandler test completed")
    print(f"Total nodes: {len(handler.dungeon_map.nodes)}")
    print(f"Available nodes: {len(handler.dungeon_map.get_available_nodes())}")