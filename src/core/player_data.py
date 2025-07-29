"""
プレイヤーデータ管理システム
プレイヤーの統計、スキル、インベントリを統合管理
"""

from dataclasses import dataclass, field
from typing import Dict, List
import logging

from core.constants import PLAYER_INITIAL_HP, PLAYER_MAX_HP
from inventory.player_inventory import PlayerInventory

logger = logging.getLogger(__name__)

@dataclass
class PlayerStats:
    """プレイヤー統計情報"""
    # 基本統計
    total_battles: int = 0
    battles_won: int = 0
    battles_lost: int = 0
    
    # 戦闘統計
    total_damage_dealt: int = 0
    total_chains_made: int = 0
    highest_chain: int = 0
    
    # 探索統計
    floors_cleared: int = 0
    rooms_visited: int = 0
    elite_battles: int = 0
    boss_battles: int = 0
    
    # 経済統計
    total_gold_earned: int = 0
    total_gold_spent: int = 0
    items_purchased: int = 0
    
    # イベント統計
    events_encountered: int = 0
    rest_sites_used: int = 0
    treasures_found: int = 0
    
    def get_win_rate(self) -> float:
        """勝率を計算"""
        if self.total_battles == 0:
            return 0.0
        return self.battles_won / self.total_battles * 100.0
    
    def get_average_chain(self) -> float:
        """平均連鎖数を計算"""
        if self.total_battles == 0:
            return 0.0
        return self.total_chains_made / self.total_battles

@dataclass
class PlayerSkills:
    """プレイヤースキル・能力値"""
    # 基本能力値
    max_hp: int = PLAYER_MAX_HP
    chain_damage_multiplier: float = 1.0
    
    # 戦闘スキル
    attack_power: int = 100
    defense: int = 0
    critical_chance: float = 0.0
    critical_multiplier: float = 1.5
    
    # 特殊スキル
    gold_find_bonus: float = 0.0
    exp_bonus: float = 0.0
    shop_discount: float = 0.0
    healing_bonus: float = 0.0
    
    def apply_artifact_effects(self, effects: Dict[str, int]):
        """アーティファクト効果を適用"""
        if "max_hp_bonus" in effects:
            self.max_hp += effects["max_hp_bonus"]
        if "damage_bonus" in effects:
            self.chain_damage_multiplier += effects["damage_bonus"] / 100.0
        if "shop_discount" in effects:
            self.shop_discount += effects["shop_discount"] / 100.0
        if "gold_bonus" in effects:
            self.gold_find_bonus += effects["gold_bonus"] / 100.0

class PlayerData:
    """プレイヤーデータ統合管理クラス"""
    
    def __init__(self):
        # 基本状態
        self.hp: int = PLAYER_INITIAL_HP
        self.max_hp: int = PLAYER_MAX_HP
        self.gold: int = 50  # 初期ゴールド
        self.chain_damage_multiplier: float = 1.0
        
        # 戦闘中の状態
        self.current_chain_count: int = 1  # 現在の連鎖数（デフォルト1）
        
        # 統計情報
        self.stats = PlayerStats()
        
        # スキル・能力値
        self.skills = PlayerSkills()
        
        # インベントリ
        self.inventory = PlayerInventory()
        
        # 現在の状態効果
        self.buffs: Dict[str, float] = {}
        self.debuffs: Dict[str, float] = {}
        
        # 特殊ぷよ所持状況（初期は基本的な特殊ぷよを所持）
        self.owned_special_puyos: set = set()
        # 新しいSimpleSpecialTypeシステムの出現率データ
        self.special_puyo_rates: Dict[str, float] = {}
        self._initialize_special_puyos()
        self._initialize_special_puyo_rates()
        
        # プレイデータ
        self.current_floor: int = 1
        self.current_run_id: str = ""
        
        logger.info("Player data initialized")
    
    def heal(self, amount: int) -> int:
        """HPを回復"""
        old_hp = self.hp
        self.hp = min(self.hp + amount, self.max_hp)
        healed = self.hp - old_hp
        logger.info(f"Player healed for {healed} HP ({old_hp} -> {self.hp})")
        return healed
    
    def set_chain_count(self, chain_count: int):
        """現在の連鎖数を設定"""
        self.current_chain_count = max(1, chain_count)  # 最低1チェイン
        logger.debug(f"Chain count set to: {self.current_chain_count}")
    
    def reset_chain_count(self):
        """連鎖数をリセット"""
        self.current_chain_count = 1
        logger.debug("Chain count reset to 1")
    
    def take_damage(self, damage: int) -> bool:
        """ダメージを受ける"""
        old_hp = self.hp
        self.hp = max(0, self.hp - damage)
        actual_damage = old_hp - self.hp
        
        logger.info(f"Player took {actual_damage} damage ({old_hp} -> {self.hp})")
        
        if self.hp <= 0:
            self.stats.battles_lost += 1
            logger.info("Player died!")
            return False  # 死亡
        
        return True  # 生存
    
    def spend_gold(self, amount: int) -> bool:
        """ゴールドを消費"""
        if self.gold >= amount:
            self.gold -= amount
            self.stats.total_gold_spent += amount
            logger.info(f"Spent {amount} gold (remaining: {self.gold})")
            return True
        return False
    
    def gain_gold(self, amount: int):
        """ゴールドを獲得"""
        # ゴールド獲得ボーナスを適用
        bonus_multiplier = 1.0 + self.skills.gold_find_bonus
        actual_amount = int(amount * bonus_multiplier)
        
        self.gold += actual_amount
        self.stats.total_gold_earned += actual_amount
        logger.info(f"Gained {actual_amount} gold (total: {self.gold})")
    
    def add_special_puyo(self, special_puyo_type):
        """特殊ぷよを所持リストに追加"""
        from special_puyo.special_puyo import SpecialPuyoType
        if isinstance(special_puyo_type, SpecialPuyoType):
            self.owned_special_puyos.add(special_puyo_type)
            logger.info(f"Added special puyo: {special_puyo_type.value}")
    
    def has_special_puyo(self, special_puyo_type):
        """特殊ぷよを所持しているかチェック"""
        return special_puyo_type in self.owned_special_puyos
    
    def has_any_special_puyo(self) -> bool:
        """何らかの特殊ぷよを所持しているかチェック"""
        return len(self.owned_special_puyos) > 0
    
    def _initialize_special_puyos(self):
        """初期特殊ぷよを設定"""
        from special_puyo.special_puyo import SpecialPuyoType
        # 基本的な特殊ぷよを最初から所持
        initial_puyos = [
            SpecialPuyoType.HEAL,
            SpecialPuyoType.BOMB
        ]
        for puyo_type in initial_puyos:
            self.owned_special_puyos.add(puyo_type)
        logger.info(f"Initialized with special puyos: {[p.value for p in initial_puyos]}")
    
    def _initialize_special_puyo_rates(self):
        """特殊ぷよの出現率を初期化"""
        from core.simple_special_puyo import SimpleSpecialType, simple_special_manager
        
        # プレイヤーデータに保存された出現率をマネージャーに復元
        if self.special_puyo_rates:
            for special_type in SimpleSpecialType:
                rate_key = special_type.value
                if rate_key in self.special_puyo_rates:
                    simple_special_manager.type_rates[special_type] = self.special_puyo_rates[rate_key]
            logger.info(f"Restored special puyo rates from player data")
        else:
            # 初回起動時は現在の設定を保存
            self.save_special_puyo_rates()
            logger.info(f"Initialized special puyo rates in player data")
    
    def save_special_puyo_rates(self):
        """現在の特殊ぷよ出現率をプレイヤーデータに保存"""
        from core.simple_special_puyo import SimpleSpecialType, simple_special_manager
        
        for special_type in SimpleSpecialType:
            rate_key = special_type.value
            self.special_puyo_rates[rate_key] = simple_special_manager.get_type_rate(special_type)
        
        logger.debug(f"Saved special puyo rates to player data: {self.special_puyo_rates}")
    
    def increase_special_puyo_rate(self, special_type_str: str, increase_amount: float = 0.05):
        """特殊ぷよの出現率を上昇させ、プレイヤーデータに保存"""
        from core.simple_special_puyo import SimpleSpecialType, simple_special_manager
        
        # 文字列からSimpleSpecialTypeを取得
        special_type = None
        for st in SimpleSpecialType:
            if st.value == special_type_str:
                special_type = st
                break
        
        if special_type:
            # マネージャーで出現率を上昇
            new_rate = simple_special_manager.increase_type_rate(special_type, increase_amount)
            # プレイヤーデータに保存
            self.special_puyo_rates[special_type_str] = new_rate
            logger.info(f"Player data: Increased {special_type_str} rate to {new_rate*100:.0f}%")
            return new_rate
        else:
            logger.warning(f"Unknown special puyo type: {special_type_str}")
            return 0.0
    
    def level_up_skill(self, skill_name: str, amount: float = 1.0):
        """スキルレベルアップ"""
        if skill_name == "max_hp":
            self.max_hp += int(amount)
            self.skills.max_hp += int(amount)
        elif skill_name == "chain_damage":
            self.chain_damage_multiplier += amount
            self.skills.chain_damage_multiplier += amount
        elif skill_name == "attack_power":
            self.skills.attack_power += int(amount)
        elif skill_name == "defense":
            self.skills.defense += int(amount)
        
        logger.info(f"Skill '{skill_name}' improved by {amount}")
    
    def update_combat_stats(self, damage_dealt: int, chains_made: int, won: bool):
        """戦闘統計を更新"""
        self.stats.total_battles += 1
        self.stats.total_damage_dealt += damage_dealt
        self.stats.total_chains_made += chains_made
        self.stats.highest_chain = max(self.stats.highest_chain, chains_made)
        
        if won:
            self.stats.battles_won += 1
        else:
            self.stats.battles_lost += 1
        
        logger.info(f"Combat stats updated - Won: {won}, Damage: {damage_dealt}, Chains: {chains_made}")
    
    def visit_room(self, room_type: str):
        """部屋訪問統計を更新"""
        self.stats.rooms_visited += 1
        
        if room_type == "elite":
            self.stats.elite_battles += 1
        elif room_type == "boss":
            self.stats.boss_battles += 1
        elif room_type == "event":
            self.stats.events_encountered += 1
        elif room_type == "rest":
            self.stats.rest_sites_used += 1
        elif room_type == "treasure":
            self.stats.treasures_found += 1
    
    def advance_floor(self):
        """次の階に進む"""
        self.current_floor += 1
        self.stats.floors_cleared += 1
        logger.info(f"Advanced to floor {self.current_floor}")
    
    def apply_artifact_effects(self):
        """アーティファクト効果を再計算・適用"""
        effects = self.inventory.get_artifact_effects()
        
        # スキル値をリセットしてから再適用
        self.skills = PlayerSkills()
        self.skills.max_hp = self.max_hp
        self.skills.chain_damage_multiplier = self.chain_damage_multiplier
        
        # アーティファクト効果を適用
        self.skills.apply_artifact_effects(effects)
        
        # 実際の値に反映
        self.max_hp = self.skills.max_hp
        self.chain_damage_multiplier = self.skills.chain_damage_multiplier
    
    def get_effective_hp_ratio(self) -> float:
        """現在のHP比率"""
        return self.hp / self.max_hp if self.max_hp > 0 else 0.0
    
    def get_display_stats(self) -> Dict[str, str]:
        """表示用統計情報"""
        return {
            "HP": f"{self.hp}/{self.max_hp}",
            "ゴールド": f"{self.gold}",
            "フロア": f"{self.current_floor}",
            "連鎖倍率": f"{self.chain_damage_multiplier:.1f}x",
            "勝率": f"{self.stats.get_win_rate():.1f}%",
            "総戦闘": f"{self.stats.total_battles}",
            "アイテム": f"{len(self.inventory.items)}/{self.inventory.max_items}"
        }
    
    def save_to_dict(self) -> Dict:
        """データを辞書形式で保存用に変換"""
        return {
            "hp": self.hp,
            "max_hp": self.max_hp,
            "gold": self.gold,
            "chain_damage_multiplier": self.chain_damage_multiplier,
            "current_floor": self.current_floor,
            "stats": self.stats.__dict__,
            "skills": self.skills.__dict__,
            "inventory_items": [item.__dict__ for item in self.inventory.items]
        }
    
    def load_from_dict(self, data: Dict):
        """辞書からデータを復元"""
        self.hp = data.get("hp", PLAYER_INITIAL_HP)
        self.max_hp = data.get("max_hp", PLAYER_MAX_HP)
        self.gold = data.get("gold", 50)
        self.chain_damage_multiplier = data.get("chain_damage_multiplier", 1.0)
        self.current_floor = data.get("current_floor", 1)
        
        # 統計情報の復元
        if "stats" in data:
            for key, value in data["stats"].items():
                setattr(self.stats, key, value)
        
        # スキル情報の復元
        if "skills" in data:
            for key, value in data["skills"].items():
                setattr(self.skills, key, value)
        
        logger.info("Player data loaded from save")