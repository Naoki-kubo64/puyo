"""
ダンジョンマップシステム - Slay the Spire風の分岐マップ
Drop Puzzle × Roguelike のダンジョンマップ構造と進行管理
"""

import random
import logging
from typing import Dict, List, Optional, Tuple
from enum import Enum
from dataclasses import dataclass

logger = logging.getLogger(__name__)


class NodeType(Enum):
    """ダンジョンノードタイプ"""
    BATTLE = "battle"         # 戦闘
    TREASURE = "treasure"     # 宝箱
    EVENT = "event"          # ランダムイベント
    REST = "rest"            # 休憩所（HP回復）
    SHOP = "shop"            # ショップ
    BOSS = "boss"            # ボス戦
    ELITE = "elite"          # エリート戦


@dataclass
class DungeonNode:
    """ダンジョンノード（マップ上の各地点）"""
    node_id: str
    node_type: NodeType
    floor: int
    x: int  # マップ上のX座標（0-6の範囲）
    y: int  # マップ上のY座標（フロア番号）
    
    # 接続情報
    connections: List[str]  # 接続されているnode_idのリスト
    visited: bool = False
    available: bool = False  # 現在選択可能かどうか
    
    # 報酬・敵情報
    enemy_type: Optional[str] = None
    reward_seed: Optional[int] = None
    
    def __post_init__(self):
        """初期化後処理"""
        if not self.node_id:
            self.node_id = f"{self.node_type.value}_{self.floor}_{self.x}"


class DungeonMap:
    """ダンジョンマップ管理クラス"""
    
    def __init__(self, total_floors: int = 15):
        self.total_floors = total_floors
        self.current_floor = 0
        self.current_node: Optional[DungeonNode] = None
        
        # マップ構造
        self.nodes: Dict[str, DungeonNode] = {}
        self.floor_nodes: Dict[int, List[DungeonNode]] = {}
        
        # 進行状態
        self.path_history: List[str] = []  # 訪問したノードの履歴
        
        # マップ生成
        self.generate_map()
        
        logger.info(f"DungeonMap generated: {total_floors} floors, {len(self.nodes)} nodes")
    
    def generate_map(self):
        """ダンジョンマップを生成"""
        self.nodes.clear()
        self.floor_nodes.clear()
        
        # 各フロアごとにノードを生成
        for floor in range(self.total_floors):
            self._generate_floor(floor)
        
        # 接続を生成
        self._generate_connections()
        
        # 最初のフロア（フロア0）を選択可能にする
        if 0 in self.floor_nodes:
            for node in self.floor_nodes[0]:
                node.available = True
    
    def _generate_floor(self, floor: int):
        """指定フロアのノードを生成"""
        nodes_this_floor = []
        
        if floor == 0:
            # 1マス目：必ず戦闘のみ
            node_count = 3
            node_types = [NodeType.BATTLE] * node_count
        elif floor == self.total_floors - 1:
            # 最終フロア：ボスのみ
            node_count = 1
            node_types = [NodeType.BOSS]
        elif floor % 5 == 4:
            # 5フロアごとにエリート戦
            node_count = 2
            node_types = [NodeType.ELITE, NodeType.REST]
        else:
            # 通常フロア：新しいルールでノード生成
            node_count = random.randint(3, 6)
            node_types = self._generate_floor_nodes(floor, node_count)
        
        # ノードを配置
        x_positions = self._calculate_x_positions(node_count)
        
        for i, (node_type, x_pos) in enumerate(zip(node_types, x_positions)):
            node = DungeonNode(
                node_id=f"{node_type.value}_{floor}_{x_pos}",
                node_type=node_type,
                floor=floor,
                x=x_pos,
                y=floor,
                connections=[]
            )
            
            # 敵タイプを設定
            if node_type in [NodeType.BATTLE, NodeType.ELITE, NodeType.BOSS]:
                node.enemy_type = self._assign_enemy_type(node_type, floor)
            
            # 報酬シードを設定
            node.reward_seed = random.randint(1000, 99999)
            
            self.nodes[node.node_id] = node
            nodes_this_floor.append(node)
        
        self.floor_nodes[floor] = nodes_this_floor
        logger.debug(f"Floor {floor}: {[n.node_type.value for n in nodes_this_floor]}")
    
    def _generate_floor_nodes(self, floor: int, count: int) -> List[NodeType]:
        """新しいルールに基づいてフロアのノードタイプを生成"""
        types = []
        
        # 基本ノードプール（戦闘・宝箱）
        base_nodes = [NodeType.BATTLE, NodeType.TREASURE]
        
        # ショップと休憩所は3マス目（floor 2）以降に出現可能
        special_nodes = []
        if floor >= 2:
            special_nodes = [NodeType.SHOP, NodeType.REST]
        
        # ランダムイベントは1マス目以外（floor 1以降）に出現可能
        event_nodes = []
        if floor >= 1:
            event_nodes = [NodeType.EVENT]
        
        # 前フロアの情報を取得してショップ・休憩所の連続配置をチェック
        prev_special_positions = self._get_recent_special_positions(floor)
        
        # このフロアで既に配置された特殊ノード（同フロア内重複防止）
        floor_special_used = set()
        
        for i in range(count):
            # ノードタイプを決定
            available_types = base_nodes[:]
            
            # ショップ・休憩所の連続配置チェック
            if special_nodes and floor >= 2:
                available_special = []
                for special_type in special_nodes:
                    # 同フロア内重複チェック
                    if special_type in floor_special_used:
                        continue
                    
                    # 連続配置チェック
                    if self._can_place_special_node_type(floor, i, prev_special_positions, special_type):
                        available_special.append(special_type)
                
                available_types.extend(available_special)
            
            # ランダムイベント追加（1マス目以外）
            if event_nodes:
                available_types.extend(event_nodes)
            
            # 重み付き選択
            weights = self._get_node_weights(available_types)
            chosen_type = random.choices(available_types, weights=weights)[0]
            types.append(chosen_type)
            
            # ショップ・休憩所が選ばれた場合、記録
            if chosen_type in [NodeType.SHOP, NodeType.REST]:
                prev_special_positions[chosen_type] = (floor, i)
                floor_special_used.add(chosen_type)
        
        return types
    
    def _get_recent_special_positions(self, current_floor: int) -> Dict[NodeType, Tuple[int, int]]:
        """最近のショップ・休憩所の位置を取得"""
        special_positions = {}
        
        # 前2フロア分をチェック
        for check_floor in range(max(0, current_floor - 2), current_floor):
            if check_floor in self.floor_nodes:
                for node in self.floor_nodes[check_floor]:
                    if node.node_type in [NodeType.SHOP, NodeType.REST]:
                        # より最近の位置を優先
                        if (node.node_type not in special_positions or 
                            check_floor > special_positions[node.node_type][0]):
                            special_positions[node.node_type] = (check_floor, node.x)
        
        return special_positions
    
    def _can_place_special_node_type(self, floor: int, position: int, 
                                    prev_special_positions: Dict[NodeType, Tuple[int, int]], 
                                    node_type: NodeType) -> bool:
        """特定のショップ・休憩所タイプを配置可能かチェック"""
        if node_type not in prev_special_positions:
            return True
            
        prev_floor, prev_pos = prev_special_positions[node_type]
        floor_diff = floor - prev_floor
        
        # 2フロア以内の連続配置を防ぐ
        if floor_diff <= 2:
            if floor_diff == 1:
                # 隣接フロア：同じタイプは配置しない
                return False
            elif floor_diff == 2:
                # 2フロア離れている：X座標の距離をチェック
                if abs(position - prev_pos) <= 2:
                    return False
        
        return True
    
    def _get_node_weights(self, available_types: List[NodeType]) -> List[int]:
        """ノードタイプの重みを取得"""
        weights = []
        for node_type in available_types:
            if node_type == NodeType.BATTLE:
                weights.append(50)
            elif node_type == NodeType.TREASURE:
                weights.append(25)
            elif node_type == NodeType.EVENT:
                weights.append(15)
            elif node_type == NodeType.SHOP:
                weights.append(7)
            elif node_type == NodeType.REST:
                weights.append(8)
            else:
                weights.append(5)
        
        return weights
    
    def _calculate_x_positions(self, count: int) -> List[int]:
        """ノードのX座標を計算（0-6の範囲で均等配置）"""
        if count == 1:
            return [3]  # 中央
        elif count == 2:
            return [1, 5]
        elif count == 3:
            return [1, 3, 5]
        elif count == 4:
            return [0, 2, 4, 6]
        elif count == 5:
            return [0, 1, 3, 5, 6]
        elif count == 6:
            return [0, 1, 2, 4, 5, 6]
        else:
            # 7個以上の場合は重複を許可
            positions = list(range(7))
            random.shuffle(positions)
            return positions[:count]
    
    def _assign_enemy_type(self, node_type: NodeType, floor: int) -> str:
        """ノードタイプとフロアに基づいて敵タイプを決定"""
        if node_type == NodeType.BOSS:
            return f"boss_floor_{floor}"
        elif node_type == NodeType.ELITE:
            return f"elite_floor_{floor}"
        else:
            # 通常戦闘
            enemy_pool = ["goblin", "orc", "skeleton", "slime", "spider"]
            return random.choice(enemy_pool)
    
    def _generate_connections(self):
        """フロア間の接続を生成"""
        for floor in range(self.total_floors - 1):
            current_floor_nodes = self.floor_nodes.get(floor, [])
            next_floor_nodes = self.floor_nodes.get(floor + 1, [])
            
            if not current_floor_nodes or not next_floor_nodes:
                continue
            
            # 各ノードから次フロアのノードへの接続を生成
            for current_node in current_floor_nodes:
                connections = self._find_valid_connections(current_node, next_floor_nodes)
                current_node.connections = [node.node_id for node in connections]
    
    def _find_valid_connections(self, current_node: DungeonNode, 
                              next_floor_nodes: List[DungeonNode]) -> List[DungeonNode]:
        """現在ノードから次フロアへの有効な接続を検索"""
        valid_connections = []
        
        for next_node in next_floor_nodes:
            # X座標の差が3以下なら接続可能
            x_diff = abs(current_node.x - next_node.x)
            if x_diff <= 3:
                valid_connections.append(next_node)
        
        # 最低1つは接続を保証
        if not valid_connections and next_floor_nodes:
            # 最も近いノードに接続
            closest_node = min(next_floor_nodes, 
                             key=lambda n: abs(n.x - current_node.x))
            valid_connections = [closest_node]
        
        return valid_connections
    
    def get_available_nodes(self) -> List[DungeonNode]:
        """現在選択可能なノードを取得"""
        return [node for node in self.nodes.values() if node.available]
    
    def select_node(self, node_id: str) -> bool:
        """ノードを選択して移動"""
        if node_id not in self.nodes:
            logger.warning(f"Invalid node_id: {node_id}")
            return False
        
        node = self.nodes[node_id]
        if not node.available:
            logger.warning(f"Node {node_id} is not available")
            return False
        
        # 現在のノードを更新
        self.current_node = node
        node.visited = True
        node.available = False
        self.path_history.append(node_id)
        
        # フロアを更新
        self.current_floor = node.floor
        
        # 次に選択可能なノードを更新
        self._update_available_nodes()
        
        logger.info(f"Moved to node: {node_id} (floor {node.floor}, type: {node.node_type.value})")
        return True
    
    def _update_available_nodes(self):
        """選択可能なノードを更新"""
        # すべてのノードを選択不可にする
        for node in self.nodes.values():
            node.available = False
        
        # 現在のノードからの接続先を選択可能にする
        if self.current_node:
            for connection_id in self.current_node.connections:
                if connection_id in self.nodes:
                    connected_node = self.nodes[connection_id]
                    if not connected_node.visited:
                        connected_node.available = True
    
    def get_current_floor_progress(self) -> Tuple[int, int]:
        """現在のフロア進行状況を取得"""
        return (self.current_floor + 1, self.total_floors)
    
    def is_completed(self) -> bool:
        """ダンジョンが完了したかチェック"""
        return (self.current_node is not None and 
                self.current_node.node_type == NodeType.BOSS and 
                self.current_node.visited)
    
    def get_node_by_id(self, node_id: str) -> Optional[DungeonNode]:
        """ノードIDでノードを取得"""
        return self.nodes.get(node_id)
    
    def get_nodes_by_floor(self, floor: int) -> List[DungeonNode]:
        """指定フロアのノードを取得"""
        return self.floor_nodes.get(floor, [])


if __name__ == "__main__":
    # テスト実行
    logging.basicConfig(level=logging.DEBUG)
    
    dungeon = DungeonMap(total_floors=15)
    
    print("=== Dungeon Map Test ===")
    print(f"Total floors: {dungeon.total_floors}")
    print(f"Total nodes: {len(dungeon.nodes)}")
    
    # 最初の数フロアを表示
    for floor in range(min(5, dungeon.total_floors)):
        nodes = dungeon.get_nodes_by_floor(floor)
        print(f"Floor {floor}: {[f'{n.node_type.value}({n.x})' for n in nodes]}")
    
    # 選択可能なノードを表示
    available = dungeon.get_available_nodes()
    print(f"Available nodes: {[n.node_id for n in available]}")