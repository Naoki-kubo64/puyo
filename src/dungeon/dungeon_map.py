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
        
        # エリートの最低出現保証
        self._ensure_minimum_elite_spawns()
        
        # 全ルートでエリート必須の保証
        self._ensure_elite_on_all_routes()
        
        # すべてのノードを最初は選択不可にする
        for node in self.nodes.values():
            node.available = False
            node.visited = False
        
        # 最初のフロア（フロア0）のノードのみを選択可能にする
        if 0 in self.floor_nodes:
            for node in self.floor_nodes[0]:
                node.available = True
                logger.info(f"Initial node made available: {node.node_id}")
        
        # 初期状態での利用可能ノードを確認
        initial_available = [n.node_id for n in self.nodes.values() if n.available]
        logger.info(f"Initial available nodes: {initial_available}")
        
        # デバッグ：全ノードの状態確認
        for floor in range(min(3, self.total_floors)):
            floor_nodes = self.get_nodes_by_floor(floor)
            available_in_floor = [n.node_id for n in floor_nodes if n.available]
            logger.debug(f"Floor {floor} available nodes: {available_in_floor}")
    
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
        else:
            # 通常フロア：新しいルールでノード生成（エリート戦を含む）
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
        
        # エリート戦は3マス目以降にランダム確率で出現（低確率）
        elite_nodes = []
        if floor >= 2:  # 3マス目は floor == 2
            elite_nodes = [NodeType.ELITE]
        
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
            
            # エリート戦追加（3マス目以降、低確率）
            if elite_nodes:
                available_types.extend(elite_nodes)
            
            # 重み付き選択（フロア情報を渡す）
            weights = self._get_node_weights(available_types, floor)
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
    
    def _check_recent_elite_battles(self, current_floor: int) -> bool:
        """最近のエリート戦をチェック（連続出現防止）"""
        # 前3フロア以内にエリート戦があったかチェック
        for check_floor in range(max(0, current_floor - 3), current_floor):
            if check_floor in self.floor_nodes:
                for node in self.floor_nodes[check_floor]:
                    if node.node_type == NodeType.ELITE:
                        logger.debug(f"Recent elite found at floor {check_floor}, blocking elite at floor {current_floor}")
                        return True
        return False
    
    def _ensure_minimum_elite_spawns(self):
        """エリートの最低出現回数を保証（1ルート1回以上）"""
        # 現在のエリート数をチェック
        total_elites = 0
        elite_floors = []
        
        for floor in range(2, self.total_floors - 1):  # フロア2〜13のみ対象
            floor_nodes = self.floor_nodes.get(floor, [])
            for node in floor_nodes:
                if node.node_type == NodeType.ELITE:
                    total_elites += 1
                    elite_floors.append(floor)
        
        logger.info(f"Current elite count: {total_elites}, on floors: {elite_floors}")
        
        # エリートが0個の場合、強制的に1個追加
        if total_elites == 0:
            # 中間フロア（5-10）からランダムに選択して1つを戦闘→エリートに変更
            candidate_floors = list(range(5, 11))  # フロア5-10
            
            for floor in candidate_floors:
                floor_nodes = self.floor_nodes.get(floor, [])
                battle_nodes = [node for node in floor_nodes if node.node_type == NodeType.BATTLE]
                
                if battle_nodes:
                    # 最初の戦闘ノードをエリートに変更
                    chosen_node = battle_nodes[0]
                    chosen_node.node_type = NodeType.ELITE
                    chosen_node.enemy_type = self._assign_enemy_type(NodeType.ELITE, floor)
                    # ノードIDも更新
                    old_id = chosen_node.node_id
                    new_id = f"elite_{floor}_{chosen_node.x}"
                    chosen_node.node_id = new_id
                    
                    # ノード辞書のキーも更新
                    if old_id in self.nodes:
                        del self.nodes[old_id]
                        self.nodes[new_id] = chosen_node
                    
                    # 他のノードの接続情報も更新
                    for other_node in self.nodes.values():
                        if old_id in other_node.connections:
                            other_node.connections = [new_id if conn_id == old_id else conn_id 
                                                    for conn_id in other_node.connections]
                    
                    logger.info(f"Added guaranteed elite at floor {floor}: {old_id} -> {new_id}")
                    break
    
    def _ensure_elite_on_all_routes(self):
        """全ルートでエリートとの戦闘を保証"""
        logger.info("Ensuring elites on all possible routes with bottleneck strategy")
        
        # ボトルネック戦略：全ルートが通る必須フロアにエリートを配置
        mandatory_elite_floors = [6, 8, 10]  # フロア6, 8, 10に必ずエリートを配置
        
        for floor in mandatory_elite_floors:
            if floor in self.floor_nodes:
                floor_nodes = self.floor_nodes[floor]
                battle_nodes = [node for node in floor_nodes if node.node_type == NodeType.BATTLE]
                
                if battle_nodes:
                    # 全ての戦闘ノードをエリートに変換（このフロアを通るすべてのルートがエリートと遭遇）
                    for battle_node in battle_nodes:
                        self._convert_battle_to_elite(battle_node)
                        logger.info(f"Converted battle to elite at floor {floor}: {battle_node.node_id}")
                
                # 戦闘ノードがない場合、他のノードタイプを戦闘に変換してからエリートに
                elif floor_nodes:
                    # 宝箱やイベントノードを戦闘ノードに変換してからエリートに
                    for node in floor_nodes:
                        if node.node_type in [NodeType.TREASURE, NodeType.EVENT]:
                            # 一旦戦闘ノードに変換してからエリートに
                            node.node_type = NodeType.BATTLE
                            node.enemy_type = self._assign_enemy_type(NodeType.BATTLE, floor)
                            self._convert_battle_to_elite(node)
                            logger.info(f"Converted {node.node_type.value} to elite at floor {floor}: {node.node_id}")
                            break  # 1つだけ変換
    
    def _find_reachable_elites_from_node(self, start_node: DungeonNode) -> List[DungeonNode]:
        """指定ノードから到達可能なエリートノードを見つける"""
        visited = set()
        reachable_elites = []
        
        def dfs_find_elites(current_node):
            if current_node.node_id in visited:
                return
            visited.add(current_node.node_id)
            
            # 現在のノードがエリートなら追加
            if current_node.node_type == NodeType.ELITE:
                reachable_elites.append(current_node)
            
            # 接続先を探索
            for connection_id in current_node.connections:
                if connection_id in self.nodes:
                    next_node = self.nodes[connection_id]
                    dfs_find_elites(next_node)
        
        dfs_find_elites(start_node)
        return reachable_elites
    
    def _add_elite_to_route(self, start_node: DungeonNode):
        """指定ルートにエリートを追加"""
        # このルートの主要パスを特定
        route_path = self._trace_primary_route(start_node)
        
        # 中間フロア（4-9）で戦闘ノードをエリートに変換
        for floor in range(4, 10):
            floor_nodes_in_route = [node for node in route_path if node.floor == floor]
            
            # このフロアのルート上の戦闘ノードを探す
            battle_nodes_in_route = [node for node in floor_nodes_in_route 
                                   if node.node_type == NodeType.BATTLE]
            
            if battle_nodes_in_route:
                # 最初の戦闘ノードをエリートに変換
                chosen_node = battle_nodes_in_route[0]
                self._convert_battle_to_elite(chosen_node)
                logger.info(f"Added elite to route from {start_node.node_id} at floor {floor}: {chosen_node.node_id}")
                break
    
    def _trace_primary_route(self, start_node: DungeonNode) -> List[DungeonNode]:
        """開始ノードからの主要ルートをトレース"""
        route = []
        current_node = start_node
        visited = set()
        
        while current_node and current_node.node_id not in visited:
            route.append(current_node)
            visited.add(current_node.node_id)
            
            # 次のノードを選択（真っ直ぐ進むものを優先）
            next_node = None
            min_x_diff = float('inf')
            
            for connection_id in current_node.connections:
                if connection_id in self.nodes:
                    candidate = self.nodes[connection_id]
                    x_diff = abs(candidate.x - current_node.x)
                    
                    # より真っ直ぐなパスを優先
                    if x_diff < min_x_diff:
                        min_x_diff = x_diff
                        next_node = candidate
            
            current_node = next_node
        
        return route
    
    def _convert_battle_to_elite(self, node: DungeonNode):
        """戦闘ノードをエリートノードに変換"""
        if node.node_type != NodeType.BATTLE:
            return
        
        old_id = node.node_id
        node.node_type = NodeType.ELITE
        node.enemy_type = self._assign_enemy_type(NodeType.ELITE, node.floor)
        
        # ノードIDを更新
        new_id = f"elite_{node.floor}_{node.x}"
        node.node_id = new_id
        
        # ノード辞書のキーを更新
        if old_id in self.nodes:
            del self.nodes[old_id]
            self.nodes[new_id] = node
        
        # 他のノードの接続情報を更新
        for other_node in self.nodes.values():
            if old_id in other_node.connections:
                other_node.connections = [new_id if conn_id == old_id else conn_id 
                                        for conn_id in other_node.connections]
    
    def _get_node_weights(self, available_types: List[NodeType], floor: int = 0) -> List[int]:
        """ノードタイプの重みを取得（フロアに応じて動的調整）"""
        weights = []
        
        # エリートの出現率を大幅に削減し、連続出現をチェック
        elite_base_weight = 2  # 基本重みを更に削減（8→3→2）
        
        # 連続エリート出現をチェック
        recent_elite = self._check_recent_elite_battles(floor)
        if recent_elite:
            elite_weight = 0  # 最近エリートがあった場合は出現させない
        else:
            # 後半フロアでエリートの出現率を段階的に上げる（控えめに）
            if floor >= 12:  # 13フロア目以降
                elite_weight = elite_base_weight + 2  # 4
            elif floor >= 8:   # 9フロア目以降
                elite_weight = elite_base_weight + 1  # 3
            elif floor >= 5:   # 6フロア目以降
                elite_weight = elite_base_weight + 1  # 3
            else:
                elite_weight = elite_base_weight  # 2
        
        for node_type in available_types:
            if node_type == NodeType.BATTLE:
                weights.append(50)  # 通常戦闘の重みを増加
            elif node_type == NodeType.TREASURE:
                weights.append(25)
            elif node_type == NodeType.EVENT:
                weights.append(20)
            elif node_type == NodeType.SHOP:
                weights.append(8)
            elif node_type == NodeType.REST:
                weights.append(12)  # 休憩所を少し増やす
            elif node_type == NodeType.ELITE:
                weights.append(elite_weight)  # フロアに応じて動的に調整（連続出現防止付き）
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
        """Slay the Spire風の接続を生成：すべてのノードが到達可能"""
        for floor in range(self.total_floors - 1):
            current_floor_nodes = self.floor_nodes.get(floor, [])
            next_floor_nodes = self.floor_nodes.get(floor + 1, [])
            
            if not current_floor_nodes or not next_floor_nodes:
                continue
            
            # ステップ1: 各ノードに基本的な接続を保証
            self._ensure_basic_connections(current_floor_nodes, next_floor_nodes)
            
            # ステップ2: 逆方向から到達可能性を確認し、孤立ノードを修正
            self._fix_isolated_nodes(current_floor_nodes, next_floor_nodes)
            
            # ステップ3: 分岐を適度に追加（ただし複雑にしすぎない）
            self._add_strategic_branches(current_floor_nodes, next_floor_nodes)
            
            # デバッグ情報
            for node in current_floor_nodes:
                logger.debug(f"Node {node.node_id} connects to: {node.connections}")
        
        # 最終確認：全ノードの到達可能性を検証
        self._verify_all_nodes_reachable()
    
    def _find_valid_connections(self, current_node: DungeonNode, 
                              next_floor_nodes: List[DungeonNode],
                              reduce_branch_chance: bool = False) -> List[DungeonNode]:
        """Slay the Spire風の接続を生成：基本は真っ直ぐ、たまに分岐"""
        import random
        
        valid_connections = []
        current_x = current_node.x
        
        # 基本接続：同じX座標または隣接する位置
        primary_targets = []
        secondary_targets = []
        
        for next_node in next_floor_nodes:
            x_diff = abs(current_node.x - next_node.x)
            
            if x_diff == 0:
                # 真っ直ぐ進む（最優先）
                primary_targets.append(next_node)
            elif x_diff == 1:
                # 隣接位置（分岐候補）
                secondary_targets.append(next_node)
        
        # 基本接続：真っ直ぐ進む
        if primary_targets:
            valid_connections.extend(primary_targets)
            logger.debug(f"Node {current_node.node_id} connects straight to: {[n.node_id for n in primary_targets]}")
        
        # 分岐の確率的追加（連続分岐を制限）
        branch_chance = 0.15 if reduce_branch_chance else 0.3
        if secondary_targets and random.random() < branch_chance:
            # 分岐は最大1つまで
            branch_target = random.choice(secondary_targets)
            valid_connections.append(branch_target)
            logger.debug(f"Node {current_node.node_id} has branch to: {branch_target.node_id}")
        
        # 接続がない場合の保証処理
        if not valid_connections:
            # 最も近いノードに強制接続
            closest_node = min(next_floor_nodes, 
                             key=lambda n: abs(n.x - current_node.x))
            valid_connections = [closest_node]
            logger.debug(f"Node {current_node.node_id} forced connection to: {closest_node.node_id}")
        
        return valid_connections
    
    def _ensure_basic_connections(self, current_floor_nodes, next_floor_nodes):
        """各ノードに基本的な接続を保証"""
        for current_node in current_floor_nodes:
            current_node.connections = []
            
            # 最も近いノードに接続（真っ直ぐ優先）
            best_targets = []
            min_distance = float('inf')
            
            for next_node in next_floor_nodes:
                distance = abs(current_node.x - next_node.x)
                if distance < min_distance:
                    min_distance = distance
                    best_targets = [next_node]
                elif distance == min_distance:
                    best_targets.append(next_node)
            
            # 最良の接続先を選択
            if best_targets:
                # 真っ直ぐ進む場合は全て接続、そうでなければ1つだけ
                if min_distance == 0:
                    for target in best_targets:
                        current_node.connections.append(target.node_id)
                else:
                    # 斜めの場合は1つだけ選択
                    import random
                    chosen = random.choice(best_targets)
                    current_node.connections.append(chosen.node_id)
    
    def _fix_isolated_nodes(self, current_floor_nodes, next_floor_nodes):
        """孤立ノードを修正"""
        # 次フロアの各ノードに到達する経路があるかチェック
        reachable_next_nodes = set()
        for current_node in current_floor_nodes:
            for connection_id in current_node.connections:
                reachable_next_nodes.add(connection_id)
        
        # 到達できないノードがある場合、最寄りの現在フロアノードから接続
        for next_node in next_floor_nodes:
            if next_node.node_id not in reachable_next_nodes:
                # 最も近い現在フロアのノードを見つけて接続
                closest_current = min(current_floor_nodes, 
                                    key=lambda n: abs(n.x - next_node.x))
                if next_node.node_id not in closest_current.connections:
                    closest_current.connections.append(next_node.node_id)
                    logger.info(f"Fixed isolation: {closest_current.node_id} -> {next_node.node_id}")
    
    def _add_strategic_branches(self, current_floor_nodes, next_floor_nodes):
        """戦略的な分岐を適度に追加"""
        import random
        
        for current_node in current_floor_nodes:
            # 既に複数の接続がある場合はスキップ
            if len(current_node.connections) > 1:
                continue
            
            # 20%の確率で分岐を追加
            if random.random() < 0.2:
                # 隣接するノードで、まだ接続していないものを探す
                for next_node in next_floor_nodes:
                    if (next_node.node_id not in current_node.connections and
                        abs(current_node.x - next_node.x) == 1):
                        current_node.connections.append(next_node.node_id)
                        logger.debug(f"Added branch: {current_node.node_id} -> {next_node.node_id}")
                        break  # 1つだけ追加
    
    def _verify_all_nodes_reachable(self):
        """全ノードが到達可能かを検証"""
        # フロア0から開始して到達可能なノードを追跡
        reachable = set()
        
        # 最初のフロアのノードは全て到達可能
        if 0 in self.floor_nodes:
            for node in self.floor_nodes[0]:
                reachable.add(node.node_id)
        
        # 各フロアを順番に処理
        for floor in range(self.total_floors - 1):
            if floor not in self.floor_nodes:
                continue
                
            for current_node in self.floor_nodes[floor]:
                if current_node.node_id in reachable:
                    # このノードから接続先も到達可能になる
                    for connection_id in current_node.connections:
                        reachable.add(connection_id)
        
        # 到達不可能なノードをレポート
        total_nodes = len(self.nodes)
        reachable_count = len(reachable)
        
        if reachable_count < total_nodes:
            unreachable = []
            for node_id, node in self.nodes.items():
                if node_id not in reachable:
                    unreachable.append(node_id)
            logger.warning(f"Unreachable nodes detected: {unreachable}")
        else:
            logger.info(f"All {total_nodes} nodes are reachable")
    
    def get_available_nodes(self) -> List[DungeonNode]:
        """現在選択可能なノードを取得"""
        return [node for node in self.nodes.values() if node.available]
    
    def select_node(self, node_id: str) -> bool:
        """ノードを選択して移動"""
        if node_id not in self.nodes:
            logger.warning(f"Invalid node_id: {node_id}")
            return False
        
        node = self.nodes[node_id]
        
        # 既に訪問済みの場合はスキップ
        if node.visited:
            logger.info(f"Node {node_id} already visited, skipping")
            return True
        
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
        logger.info(f"Available nodes after move: {[n.node_id for n in self.get_available_nodes()]}")
        return True
    
    def _update_available_nodes(self):
        """選択可能なノードを更新"""
        # すべてのノードを選択不可にする
        for node in self.nodes.values():
            node.available = False
        
        # 現在のノードからの接続先を選択可能にする
        if self.current_node:
            logger.info(f"Updating available nodes from current: {self.current_node.node_id}")
            logger.info(f"Current node connections: {self.current_node.connections}")
            
            for connection_id in self.current_node.connections:
                if connection_id in self.nodes:
                    connected_node = self.nodes[connection_id]
                    if not connected_node.visited:
                        connected_node.available = True
                        logger.info(f"Made node {connection_id} available")
                    else:
                        logger.info(f"Node {connection_id} already visited, skipping")
                else:
                    logger.warning(f"Connection {connection_id} not found in nodes")
            
            # 利用可能なノード一覧を出力
            available = [n.node_id for n in self.nodes.values() if n.available]
            logger.info(f"Final available nodes: {available}")
        else:
            logger.warning("No current_node set, cannot update available nodes")
    
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