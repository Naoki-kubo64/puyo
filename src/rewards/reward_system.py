"""
報酬選択システム - Slay the Spire風の戦闘後報酬選択
"""

import logging
import random
import pygame
from typing import Dict, List, Optional, Union
from enum import Enum
from dataclasses import dataclass

from ..core.constants import *
from ..inventory.player_inventory import create_item, ItemRarity
import pygame.font

logger = logging.getLogger(__name__)


class RewardType(Enum):
    """報酬の種類"""
    GOLD = "gold"                    # ゴールド
    POTION = "potion"               # ポーション
    ARTIFACT = "artifact"           # 装飾品
    HP_UPGRADE = "hp_upgrade"       # 最大HP増加
    ENERGY_UPGRADE = "energy_upgrade"  # エネルギー増加
    CHAIN_UPGRADE = "chain_upgrade"    # 連鎖ダメージアップ


@dataclass
class Reward:
    """報酬クラス"""
    reward_type: RewardType
    value: Union[int, str]
    name: str
    description: str
    rarity: ItemRarity = ItemRarity.COMMON
    
    def get_display_text(self) -> List[str]:
        """表示用テキストを取得"""
        lines = [self.name]
        
        # 説明文を適切な長さで分割
        desc_words = self.description.split()
        current_line = ""
        
        for word in desc_words:
            if len(current_line + " " + word) <= 25:
                current_line += (" " if current_line else "") + word
            else:
                if current_line:
                    lines.append(current_line)
                current_line = word
        
        if current_line:
            lines.append(current_line)
        
        return lines
    
    def get_color(self) -> tuple:
        """報酬の色を取得"""
        if self.reward_type == RewardType.GOLD:
            return Colors.GOLD
        elif self.reward_type == RewardType.POTION:
            return Colors.GREEN
        elif self.reward_type == RewardType.ARTIFACT:
            return self.rarity.color
        elif self.reward_type == RewardType.HP_UPGRADE:
            return Colors.RED
        elif self.reward_type == RewardType.ENERGY_UPGRADE:
            return Colors.BLUE
        elif self.reward_type == RewardType.CHAIN_UPGRADE:
            return Colors.PURPLE
        
        return Colors.WHITE
    
    def get_rarity_color(self) -> tuple:
        """レアリティ色を取得"""
        return RARITY_COLORS.get(self.rarity, Colors.WHITE)


class RewardGenerator:
    """報酬生成システム"""
    
    def __init__(self):
        self.floor_level = 1
        self.player_stats = {}
        
        logger.info("RewardGenerator initialized")
    
    def generate_battle_rewards(self, floor_level: int, enemy_type: str = "normal", is_boss: bool = False) -> List[Reward]:
        """戦闘後の報酬を生成"""
        self.floor_level = floor_level
        rewards = []
        
        # 必須報酬：ゴールド
        gold_amount = self._calculate_gold_reward(floor_level, is_boss)
        rewards.append(Reward(
            reward_type=RewardType.GOLD,
            value=gold_amount,
            name=f"{gold_amount} ゴールド",
            description="冒険に必要な通貨",
            rarity=Rarity.COMMON
        ))
        
        # 選択肢数を決定
        choice_count = 3 if not is_boss else 4
        
        # 報酬の種類を決定
        available_types = [
            (RewardType.POTION, 0.4),
            (RewardType.ARTIFACT, 0.25),
            (RewardType.HP_UPGRADE, 0.15),
            (RewardType.PUYO_UPGRADE, 0.15),
            (RewardType.SPECIAL_PUYO_UNLOCK, 0.05),
        ]
        
        # ボス戦では装飾品の確率アップ
        if is_boss:
            available_types = [
                (RewardType.ARTIFACT, 0.5),
                (RewardType.POTION, 0.25),
                (RewardType.HP_UPGRADE, 0.15),
                (RewardType.PUYO_UPGRADE, 0.08),
                (RewardType.SPECIAL_PUYO_UNLOCK, 0.02),
            ]
        
        # 報酬選択肢を生成
        for _ in range(choice_count):
            reward_types = [t[0] for t in available_types]
            weights = [t[1] for t in available_types]
            selected_type = random.choices(reward_types, weights=weights)[0]
            
            reward = self._generate_specific_reward(selected_type, floor_level)
            if reward:
                rewards.append(reward)
        
        logger.info(f"Generated {len(rewards)} rewards for floor {floor_level}")
        return rewards
    
    def _calculate_gold_reward(self, floor_level: int, is_boss: bool) -> int:
        """ゴールド報酬を計算"""
        base_gold = 15 + floor_level * 3
        
        if is_boss:
            base_gold *= 2
        
        # ±20%のランダム要素
        variation = random.uniform(0.8, 1.2)
        return int(base_gold * variation)
    
    def _generate_specific_reward(self, reward_type: RewardType, floor_level: int) -> Optional[Reward]:
        """特定の種類の報酬を生成"""
        
        if reward_type == RewardType.POTION:
            potion = create_random_potion(floor_level)
            return Reward(
                reward_type=RewardType.POTION,
                value=potion,
                name=potion.name,
                description=potion.description,
                rarity=potion.rarity
            )
        
        elif reward_type == RewardType.ARTIFACT:
            artifact = create_random_artifact(floor_level)
            return Reward(
                reward_type=RewardType.ARTIFACT,
                value=artifact,
                name=artifact.name,
                description=artifact.description,
                rarity=artifact.rarity
            )
        
        elif reward_type == RewardType.HP_UPGRADE:
            hp_amount = random.randint(8, 15) + floor_level
            return Reward(
                reward_type=RewardType.HP_UPGRADE,
                value=hp_amount,
                name=f"最大HP +{hp_amount}",
                description="最大体力が永続的に増加",
                rarity=Rarity.UNCOMMON
            )
        
        elif reward_type == RewardType.PUYO_UPGRADE:
            upgrades = [
                ("連鎖威力アップ", "連鎖によるダメージが10%増加", 10),
                ("落下速度アップ", "ぷよの落下速度が15%増加", 15),
                ("色彩集中", "出現するぷよの色数が1つ減少", 1),
                ("特殊ぷよ確率アップ", "特殊ぷよの出現率が50%増加", 50),
            ]
            
            upgrade_name, upgrade_desc, upgrade_value = random.choice(upgrades)
            return Reward(
                reward_type=RewardType.PUYO_UPGRADE,
                value=upgrade_value,
                name=upgrade_name,
                description=upgrade_desc,
                rarity=Rarity.RARE
            )
        
        elif reward_type == RewardType.SPECIAL_PUYO_UNLOCK:
            # まだ解放されていない特殊ぷよをランダム選択
            special_types = list(SpecialPuyoType)
            selected_type = random.choice(special_types)
            
            type_names = {
                # 既存の特殊ぷよ
                SpecialPuyoType.BOMB: "爆弾ぷよ",
                SpecialPuyoType.LIGHTNING: "雷ぷよ",
                SpecialPuyoType.RAINBOW: "虹ぷよ",
                SpecialPuyoType.MULTIPLIER: "倍率ぷよ",
                SpecialPuyoType.FREEZE: "氷ぷよ",
                SpecialPuyoType.HEAL: "回復ぷよ",
                SpecialPuyoType.SHIELD: "盾ぷよ",
                SpecialPuyoType.POISON: "毒ぷよ",
                SpecialPuyoType.WILD: "ワイルドぷよ",
                SpecialPuyoType.CHAIN_STARTER: "連鎖開始ぷよ",
                
                # 新しい特殊ぷよ
                SpecialPuyoType.BUFF: "バフぷよ",
                SpecialPuyoType.TIMED_POISON: "時限毒ぷよ",
                SpecialPuyoType.CHAIN_EXTEND: "連鎖拡張ぷよ",
                SpecialPuyoType.ABSORB_SHIELD: "吸収シールドぷよ",
                SpecialPuyoType.CURSE: "呪いぷよ",
                SpecialPuyoType.REFLECT: "反射ぷよ",
            }
            
            type_name = type_names.get(selected_type, "特殊ぷよ")
            
            return Reward(
                reward_type=RewardType.SPECIAL_PUYO_UNLOCK,
                value=selected_type.value,
                name=f"{type_name}解放",
                description=f"{type_name}の出現率が大幅に増加",
                rarity=Rarity.EPIC
            )
        
        return None


class RewardSelectionHandler:
    """報酬選択画面ハンドラー"""
    
    def __init__(self, engine, rewards: List[Reward], battle_handler=None):
        self.engine = engine
        self.rewards = rewards
        self.selected_index = 0
        self.selection_made = False
        self.selected_reward = None
        self.battle_handler = battle_handler  # 戦闘ハンドラーの参照を保存
        
        # レイアウト設定
        self.reward_width = 200
        self.reward_height = 250
        self.reward_spacing = 20
        self.start_x = (SCREEN_WIDTH - (len(rewards) * self.reward_width + (len(rewards) - 1) * self.reward_spacing)) // 2
        self.start_y = 200
        
        logger.info(f"RewardSelectionHandler initialized with {len(rewards)} rewards")
    
    def on_enter(self, previous_state):
        """報酬選択画面開始"""
        logger.info("Entering reward selection state")
        self.selected_index = 0
        self.selection_made = False
        self.selected_reward = None
    
    def handle_event(self, event: pygame.event.Event):
        """イベント処理"""
        if self.selection_made:
            # 選択完了後はダンジョンマップに戻る
            if event.type == pygame.KEYDOWN and (event.key == pygame.K_RETURN or event.key == pygame.K_ESCAPE):
                self._return_to_dungeon_map()
            return
        
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:
                self.selected_index = (self.selected_index - 1) % len(self.rewards)
            elif event.key == pygame.K_RIGHT:
                self.selected_index = (self.selected_index + 1) % len(self.rewards)
            elif event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                self._select_reward()
            elif event.key == pygame.K_ESCAPE:
                # 報酬選択をスキップ（ゴールドのみ獲得）
                gold_reward = next((r for r in self.rewards if r.reward_type == RewardType.GOLD), None)
                if gold_reward:
                    self.selected_reward = gold_reward
                self.selection_made = True
    
    def _select_reward(self):
        """報酬を選択"""
        if 0 <= self.selected_index < len(self.rewards):
            self.selected_reward = self.rewards[self.selected_index]
            self.selection_made = True
            logger.info(f"Selected reward: {self.selected_reward.name}")
    
    def _return_to_dungeon_map(self):
        """ダンジョンマップに戻る"""
        try:
            from ..dungeon.map_handler import DungeonMapHandler
            
            # 報酬選択完了時：戦闘勝利によるマップ進行処理を実行
            if (hasattr(self.engine, 'persistent_dungeon_map') and self.engine.persistent_dungeon_map and 
                self.battle_handler and hasattr(self.battle_handler, 'current_node') and self.battle_handler.current_node):
                
                dungeon_map = self.engine.persistent_dungeon_map
                current_node = self.battle_handler.current_node
                
                logger.info(f"Processing map progression after reward selection for node: {current_node.node_id}")
                
                # ノードを選択して次の階層を解放
                success = dungeon_map.select_node(current_node.node_id)
                if success:
                    available_nodes = dungeon_map.get_available_nodes()
                    logger.info(f"Map progression completed: {current_node.node_id} -> Available: {[n.node_id for n in available_nodes]}")
                else:
                    logger.error(f"Failed to progress map for node: {current_node.node_id}")
            else:
                logger.warning("Cannot process map progression - missing battle handler or current node")
            
            # ダンジョンマップハンドラーを作成（既存のマップ状態を使用）
            map_handler = DungeonMapHandler(self.engine)
            
            # ダンジョンマップ状態に変更
            self.engine.register_state_handler(GameState.DUNGEON_MAP, map_handler)
            self.engine.change_state(GameState.DUNGEON_MAP)
            
            logger.info("Returned to dungeon map after reward selection")
            
        except Exception as e:
            logger.error(f"Failed to return to dungeon map: {e}")
            # フォールバック: メニューに戻る
            self.engine.change_state(GameState.MENU)
    
    def render(self, surface: pygame.Surface):
        """描画処理"""
        # 背景
        surface.fill(Colors.UI_BACKGROUND)
        
        # タイトル
        font_title = self.engine.fonts['title']
        font_large = self.engine.fonts['large']
        font_medium = self.engine.fonts['medium']
        font_small = self.engine.fonts['small']
        
        title_str = "報酬を選択"
        title_font = get_appropriate_font(self.engine.fonts, title_str, 'title')
        title_text = title_font.render(title_str, True, Colors.WHITE)
        title_rect = title_text.get_rect(center=(SCREEN_WIDTH // 2, 100))
        surface.blit(title_text, title_rect)
        
        # 報酬カード描画
        for i, reward in enumerate(self.rewards):
            x = self.start_x + i * (self.reward_width + self.reward_spacing)
            y = self.start_y
            
            # カード背景
            card_rect = pygame.Rect(x, y, self.reward_width, self.reward_height)
            
            # 選択中のカードはハイライト
            if i == self.selected_index:
                pygame.draw.rect(surface, Colors.YELLOW, card_rect, 4)
                bg_color = Colors.UI_HIGHLIGHT
            else:
                bg_color = Colors.DARK_GRAY
            
            pygame.draw.rect(surface, bg_color, card_rect)
            pygame.draw.rect(surface, reward.get_rarity_color(), card_rect, 2)
            
            # 報酬内容描画
            self._render_reward_content(surface, reward, card_rect)
        
        # 操作説明
        instructions = [
            "← → - 選択移動",
            "Enter/Space - 決定",
            "ESC - スキップ（ゴールドのみ）"
        ]
        
        for i, instruction in enumerate(instructions):
            text = font_small.render(instruction, True, Colors.LIGHT_GRAY)
            text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 100 + i * 25))
            surface.blit(text, text_rect)
    
    def _render_reward_content(self, surface: pygame.Surface, reward: Reward, card_rect: pygame.Rect):
        """報酬カードの内容を描画"""
        font_medium = self.engine.fonts['medium']
        font_small = self.engine.fonts['small']
        
        # アイコン/値の表示
        icon_y = card_rect.y + 20
        
        if reward.reward_type == RewardType.GOLD:
            # ゴールドアイコン
            icon_text = font_medium.render("💰", True, Colors.YELLOW)
            icon_rect = icon_text.get_rect(center=(card_rect.centerx, icon_y + 20))
            surface.blit(icon_text, icon_rect)
            
            # 金額
            value_text = font_medium.render(str(reward.value), True, Colors.YELLOW)
            value_rect = value_text.get_rect(center=(card_rect.centerx, icon_y + 60))
            surface.blit(value_text, value_rect)
        
        elif reward.reward_type == RewardType.POTION:
            # ポーションアイコン
            icon_text = font_medium.render(reward.value.icon, True, reward.value.color)
            icon_rect = icon_text.get_rect(center=(card_rect.centerx, icon_y + 30))
            surface.blit(icon_text, icon_rect)
        
        elif reward.reward_type == RewardType.ARTIFACT:
            # 装飾品アイコン
            icon_text = font_medium.render(reward.value.icon, True, reward.value.color)
            icon_rect = icon_text.get_rect(center=(card_rect.centerx, icon_y + 30))
            surface.blit(icon_text, icon_rect)
        
        elif reward.reward_type == RewardType.HP_UPGRADE:
            # HPアイコン
            icon_text = font_medium.render("❤", True, Colors.RED)
            icon_rect = icon_text.get_rect(center=(card_rect.centerx, icon_y + 20))
            surface.blit(icon_text, icon_rect)
            
            # HP増加量
            value_text = font_medium.render(f"+{reward.value}", True, Colors.RED)
            value_rect = value_text.get_rect(center=(card_rect.centerx, icon_y + 60))
            surface.blit(value_text, value_rect)
        
        else:
            # その他のアイコン
            icon_text = font_medium.render("🎁", True, reward.get_color())
            icon_rect = icon_text.get_rect(center=(card_rect.centerx, icon_y + 30))
            surface.blit(icon_text, icon_rect)
        
        # 名前と説明
        text_y = card_rect.y + 120
        display_text = reward.get_display_text()
        
        for i, line in enumerate(display_text):
            if i == 0:  # 名前
                text = font_small.render(line, True, Colors.WHITE)
            else:  # 説明
                text = font_small.render(line, True, Colors.LIGHT_GRAY)
            
            text_rect = text.get_rect(center=(card_rect.centerx, text_y + i * 18))
            surface.blit(text, text_rect)
    
    def update(self, dt: float):
        """更新処理"""
        pass
    
    def is_complete(self) -> bool:
        """選択が完了したかチェック"""
        return self.selection_made
    
    def get_selected_reward(self) -> Optional[Reward]:
        """選択された報酬を取得"""
        return self.selected_reward


# グローバル報酬生成器
reward_generator = RewardGenerator()


def create_battle_rewards(floor_level: int, enemy_type: str = "normal", is_boss: bool = False) -> List[Reward]:
    """戦闘報酬を生成"""
    return reward_generator.generate_battle_rewards(floor_level, enemy_type, is_boss)