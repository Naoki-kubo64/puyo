"""
ダンジョンマップハンドラー - マップ画面の状態管理
Drop Puzzle × Roguelike のダンジョンマップ操作とゲーム状態遷移
"""

import pygame
import logging
from typing import Optional

from ..core.constants import *
from ..core.game_engine import GameEngine
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
        
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # 左クリック
                self._handle_left_click(event.pos)
        
        elif event.type == pygame.MOUSEMOTION:
            # マウスホバー処理
            self.map_renderer.handle_mouse_motion(event.pos)
    
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
            from ..battle.battle_handler import BattleHandler
            
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
            from ..battle.battle_handler import BattleHandler
            
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
            from ..battle.battle_handler import BattleHandler
            
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
        
        # 宝箱報酬の生成と表示
        # TODO: 宝箱報酬システムとの連携
        logger.info("Treasure opened - returning to map")
        self.transition_pending = False
    
    def _transition_to_event(self, node: DungeonNode):
        """イベントへの遷移"""
        logger.info("Entering random event")
        self.transition_pending = True
        
        # ランダムイベントの実行
        # TODO: イベントシステムとの連携
        logger.info("Event completed - returning to map")
        self.transition_pending = False
    
    def _transition_to_rest(self, node: DungeonNode):
        """休憩所への遷移"""
        logger.info("Entering rest site")
        self.transition_pending = True
        
        # HP回復とアップグレード選択
        # TODO: 休憩所システムとの連携
        logger.info("Rest completed - returning to map")
        self.transition_pending = False
    
    def _transition_to_shop(self, node: DungeonNode):
        """ショップへの遷移"""
        logger.info("Entering shop")
        self.transition_pending = True
        
        # ショップUIの表示
        # TODO: ショップシステムとの連携
        logger.info("Shop visit completed - returning to map")
        self.transition_pending = False
    
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
    from ..core.game_engine import GameEngine
    
    logging.basicConfig(level=logging.INFO)
    
    engine = GameEngine()
    handler = DungeonMapHandler(engine)
    
    print("DungeonMapHandler test completed")
    print(f"Total nodes: {len(handler.dungeon_map.nodes)}")
    print(f"Available nodes: {len(handler.dungeon_map.get_available_nodes())}")