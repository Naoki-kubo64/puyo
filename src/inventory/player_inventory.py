from typing import List, Dict, Optional
from dataclasses import dataclass
from enum import Enum
import pygame

class ItemType(Enum):
    ARTIFACT = "artifact"
    POTION = "potion"
    MATERIAL = "material"
    CARD = "card"

class ItemRarity(Enum):
    COMMON = ("common", (169, 169, 169))    # Gray
    UNCOMMON = ("uncommon", (30, 144, 255))  # Blue
    RARE = ("rare", (128, 0, 128))          # Purple
    EPIC = ("epic", (255, 215, 0))          # Gold
    LEGENDARY = ("legendary", (255, 69, 0))  # Red

    def __init__(self, name: str, color: tuple):
        self.display_name = name
        self.color = color

@dataclass
class Item:
    id: str
    name: str
    description: str
    item_type: ItemType
    rarity: ItemRarity
    quantity: int = 1
    consumable: bool = False
    effect_value: int = 0
    
    def get_display_name(self) -> str:
        if self.quantity > 1:
            return f"{self.name} x{self.quantity}"
        return self.name
    
    def get_value(self) -> int:
        """アイテムの価値を計算"""
        base_values = {
            ItemRarity.COMMON: 10,
            ItemRarity.UNCOMMON: 25,
            ItemRarity.RARE: 60,
            ItemRarity.EPIC: 120,
            ItemRarity.LEGENDARY: 250
        }
        base_value = base_values.get(self.rarity, 10)
        return base_value * self.quantity

class PlayerInventory:
    def __init__(self):
        self.items: List[Item] = []
        self.max_items = 20
        
        # 初期アイテムを追加
        self._add_starting_items()
    
    def _add_starting_items(self):
        """初期アイテムを追加"""
        starting_items = [
            Item("health_potion_small", "小さな体力ポーション", "HP20回復", 
                 ItemType.POTION, ItemRarity.COMMON, quantity=2, consumable=True, effect_value=20),
            Item("lucky_coin", "幸運のコイン", "ショップで5%割引", 
                 ItemType.ARTIFACT, ItemRarity.UNCOMMON, effect_value=5),
        ]
        
        for item in starting_items:
            self.add_item(item)
    
    def add_item(self, item: Item) -> bool:
        """アイテムを追加（スタック可能なアイテムは統合）"""
        # 同じIDのアイテムがあるかチェック
        for existing_item in self.items:
            if existing_item.id == item.id:
                existing_item.quantity += item.quantity
                return True
        
        # 新しいアイテムとして追加
        if len(self.items) < self.max_items:
            self.items.append(item)
            return True
        else:
            return False  # インベントリ満杯
    
    def remove_item(self, item_id: str, quantity: int = 1) -> bool:
        """アイテムを削除"""
        for item in self.items:
            if item.id == item_id:
                if item.quantity >= quantity:
                    item.quantity -= quantity
                    if item.quantity <= 0:
                        self.items.remove(item)
                    return True
                else:
                    return False
        return False
    
    def has_item(self, item_id: str, quantity: int = 1) -> bool:
        """アイテムを持っているかチェック"""
        for item in self.items:
            if item.id == item_id and item.quantity >= quantity:
                return True
        return False
    
    def get_item(self, item_id: str) -> Optional[Item]:
        """アイテムを取得"""
        for item in self.items:
            if item.id == item_id:
                return item
        return None
    
    def get_items_by_type(self, item_type: ItemType) -> List[Item]:
        """タイプ別にアイテムを取得"""
        return [item for item in self.items if item.item_type == item_type]
    
    def get_total_value(self) -> int:
        """インベントリの総価値"""
        return sum(item.get_value() for item in self.items)
    
    def get_artifact_effects(self) -> Dict[str, int]:
        """アーティファクトの効果を集計"""
        effects = {}
        for item in self.items:
            if item.item_type == ItemType.ARTIFACT:
                # アーティファクトの効果をIDベースで集計
                if "discount" in item.id:
                    effects["shop_discount"] = effects.get("shop_discount", 0) + item.effect_value
                elif "damage" in item.id:
                    effects["damage_bonus"] = effects.get("damage_bonus", 0) + item.effect_value
                elif "health" in item.id:
                    effects["max_hp_bonus"] = effects.get("max_hp_bonus", 0) + item.effect_value
                elif "energy" in item.id:
                    effects["energy_bonus"] = effects.get("energy_bonus", 0) + item.effect_value
                elif "gold" in item.id:
                    effects["gold_bonus"] = effects.get("gold_bonus", 0) + item.effect_value
        return effects
    
    def use_consumable(self, item_id: str) -> Optional[Item]:
        """消耗品を使用"""
        item = self.get_item(item_id)
        if item and item.consumable:
            if self.remove_item(item_id, 1):
                return item
        return None

# 事前定義アイテム
PREDEFINED_ITEMS = {
    # ポーション
    "health_potion_small": Item("health_potion_small", "小さな体力ポーション", "HP20回復", 
                               ItemType.POTION, ItemRarity.COMMON, consumable=True, effect_value=20),
    "health_potion_medium": Item("health_potion_medium", "体力ポーション", "HP40回復", 
                                ItemType.POTION, ItemRarity.UNCOMMON, consumable=True, effect_value=40),
    "health_potion_large": Item("health_potion_large", "大きな体力ポーション", "HP70回復", 
                               ItemType.POTION, ItemRarity.RARE, consumable=True, effect_value=70),
    "energy_potion": Item("energy_potion", "エネルギーポーション", "エネルギー+1", 
                         ItemType.POTION, ItemRarity.UNCOMMON, consumable=True, effect_value=1),
    
    # アーティファクト
    "lucky_coin": Item("lucky_coin", "幸運のコイン", "ショップで5%割引", 
                      ItemType.ARTIFACT, ItemRarity.UNCOMMON, effect_value=5),
    "merchants_badge": Item("merchants_badge", "商人の徽章", "ショップで10%割引", 
                           ItemType.ARTIFACT, ItemRarity.RARE, effect_value=10),
    "power_ring": Item("power_ring", "力の指輪", "連鎖ダメージ+15%", 
                      ItemType.ARTIFACT, ItemRarity.RARE, effect_value=15),
    "vitality_amulet": Item("vitality_amulet", "活力のお守り", "最大HP+15", 
                           ItemType.ARTIFACT, ItemRarity.UNCOMMON, effect_value=15),
    "energy_crystal": Item("energy_crystal", "エネルギークリスタル", "最大エネルギー+1", 
                          ItemType.ARTIFACT, ItemRarity.EPIC, effect_value=1),
    "golden_scarab": Item("golden_scarab", "黄金のスカラベ", "戦闘後ゴールド+50%", 
                         ItemType.ARTIFACT, ItemRarity.EPIC, effect_value=50),
    
    # 材料
    "iron_ore": Item("iron_ore", "鉄鉱石", "クラフト材料", 
                    ItemType.MATERIAL, ItemRarity.COMMON, effect_value=0),
    "gem_fragment": Item("gem_fragment", "宝石の欠片", "貴重なクラフト材料", 
                        ItemType.MATERIAL, ItemRarity.RARE, effect_value=0),
    "mystic_essence": Item("mystic_essence", "神秘のエッセンス", "伝説的なクラフト材料", 
                          ItemType.MATERIAL, ItemRarity.LEGENDARY, effect_value=0),
}

def create_item(item_id: str, quantity: int = 1) -> Optional[Item]:
    """事前定義アイテムから新しいアイテムインスタンスを作成"""
    if item_id in PREDEFINED_ITEMS:
        template = PREDEFINED_ITEMS[item_id]
        return Item(
            id=template.id,
            name=template.name,
            description=template.description,
            item_type=template.item_type,
            rarity=template.rarity,
            quantity=quantity,
            consumable=template.consumable,
            effect_value=template.effect_value
        )
    return None