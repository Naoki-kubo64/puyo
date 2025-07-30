"""
報酬選択システム - Slay the Spire風の戦闘後報酬選択
"""

import logging
import random
import pygame
from typing import Dict, List, Optional, Union
from enum import Enum
from dataclasses import dataclass

from core.constants import *
from inventory.player_inventory import create_item, ItemRarity
import pygame.font

logger = logging.getLogger(__name__)


class RewardType(Enum):
    """報酬の種類"""
    GOLD = "gold"                    # ゴールド
    POTION = "potion"               # ポーション
    ARTIFACT = "artifact"           # 装飾品
    HP_UPGRADE = "hp_upgrade"       # 最大HP増加
    ENERGY_UPGRADE = "energy_upgrade"  # エネルギー増加（削除済み）
    CHAIN_UPGRADE = "chain_upgrade"    # 連鎖ダメージアップ
    SPECIAL_PUYO = "special_puyo"  # 特殊ぷよ獲得


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
            rarity=ItemRarity.COMMON
        ))
        
        # 選択肢数を決定
        choice_count = 3 if not is_boss else 4
        
        # 報酬の種類を決定
        available_types = [
            (RewardType.POTION, 0.3),
            (RewardType.ARTIFACT, 0.2),
            (RewardType.HP_UPGRADE, 0.15),
            (RewardType.CHAIN_UPGRADE, 0.15),
            (RewardType.SPECIAL_PUYO, 0.2),  # 5% → 20%に大幅アップ
        ]
        
        # ボス戦では装飾品の確率アップ
        if is_boss:
            available_types = [
                (RewardType.ARTIFACT, 0.4),
                (RewardType.POTION, 0.2),
                (RewardType.HP_UPGRADE, 0.15),
                (RewardType.CHAIN_UPGRADE, 0.1),
                (RewardType.SPECIAL_PUYO, 0.15),  # 2% → 15%に大幅アップ
            ]
        
        # 報酬選択肢を生成（必ず特殊ぷよを1つ含む）
        
        # まず特殊ぷよ報酬を必ず1つ追加
        special_puyo_reward = self._generate_specific_reward(RewardType.SPECIAL_PUYO, floor_level)
        if special_puyo_reward:
            rewards.append(special_puyo_reward)
        
        # 残りの選択肢を通常の確率で生成
        other_types = [(t[0], t[1]) for t in available_types if t[0] != RewardType.SPECIAL_PUYO]
        
        for _ in range(choice_count - 1):  # 特殊ぷよ分を引く
            if other_types:  # 他のタイプがある場合のみ
                reward_types = [t[0] for t in other_types]
                weights = [t[1] for t in other_types]
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
            # ポーション報酬の簡易実装
            potions = ["health_potion_small", "health_potion_medium", "energy_potion"]
            potion_id = random.choice(potions)
            
            names = {
                "health_potion_small": "小さな体力ポーション",
                "health_potion_medium": "体力ポーション", 
                "energy_potion": "エネルギーポーション"
            }
            
            return Reward(
                reward_type=RewardType.POTION,
                value=potion_id,
                name=names.get(potion_id, "ポーション"),
                description="クリックで獲得",
                rarity=ItemRarity.COMMON
            )
        
        elif reward_type == RewardType.ARTIFACT:
            # アーティファクト報酬の簡易実装
            artifacts = ["lucky_coin", "vitality_amulet", "power_ring", "merchants_badge"]
            artifact_id = random.choice(artifacts)
            
            names = {
                "lucky_coin": "幸運のコイン",
                "vitality_amulet": "活力のお守り",
                "power_ring": "力の指輪",
                "merchants_badge": "商人の徽章"
            }
            
            return Reward(
                reward_type=RewardType.ARTIFACT,
                value=artifact_id,
                name=names.get(artifact_id, "アーティファクト"),
                description="永続効果アイテム",
                rarity=ItemRarity.UNCOMMON
            )
        
        elif reward_type == RewardType.HP_UPGRADE:
            hp_amount = random.randint(8, 15) + floor_level
            return Reward(
                reward_type=RewardType.HP_UPGRADE,
                value=hp_amount,
                name=f"最大HP +{hp_amount}",
                description="最大体力が永続的に増加",
                rarity=ItemRarity.UNCOMMON
            )
        
        elif reward_type == RewardType.CHAIN_UPGRADE:
            chain_bonus = random.randint(10, 20)
            return Reward(
                reward_type=RewardType.CHAIN_UPGRADE,
                value=chain_bonus,
                name=f"連鎖ダメージ+{chain_bonus}%",
                description="連鎖攻撃の威力が永続的に向上",
                rarity=ItemRarity.RARE
            )
        
        elif reward_type == RewardType.ENERGY_UPGRADE:
            # エネルギーシステムは削除済み - 何も返さない
            return None
            
        elif reward_type == RewardType.SPECIAL_PUYO:
            # ランダムな特殊ぷよタイプを選択（新しいSimpleSpecialTypeシステム）
            from core.simple_special_puyo import SimpleSpecialType
            available_types = list(SimpleSpecialType)
            selected_type = random.choice(available_types)
            
            # SimpleSpecialTypeのメソッドを安全に使用
            try:
                name = selected_type.get_display_name()
                base_description = selected_type.get_description()
                
                # より詳細な効果説明を追加
                detailed_descriptions = {
                    SimpleSpecialType.HEAL: "プレイヤーのHPを10回復する",
                    SimpleSpecialType.BOMB: "全ての敵に攻撃ダメージを与える",
                    SimpleSpecialType.LIGHTNING: "最強の敵1体に強力な攻撃",
                    SimpleSpecialType.SHIELD: "次に受けるダメージを15軽減",
                    SimpleSpecialType.MULTIPLIER: "攻撃力を50%アップする",
                    SimpleSpecialType.POISON: "全ての敵に継続ダメージ",
                }
                
                description = detailed_descriptions.get(selected_type, base_description)
                
            except Exception as e:
                logger.warning(f"Error getting special puyo info for {selected_type}: {e}")
                name = f"{selected_type.value}ぷよ"
                description = "特殊効果"
            
            return Reward(
                reward_type=RewardType.SPECIAL_PUYO,
                value=selected_type,
                name=name,
                description=f"{description}\n(出現率+5%)",
                rarity=ItemRarity.RARE
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
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
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
        
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            # マウスクリックで報酬選択
            clicked_index = self._get_clicked_reward_index(event.pos)
            if clicked_index is not None:
                self.selected_index = clicked_index
                self._select_reward()
        
        elif event.type == pygame.MOUSEMOTION:
            # マウスホバーで選択インデックス更新
            hovered_index = self._get_clicked_reward_index(event.pos)
            if hovered_index is not None:
                self.selected_index = hovered_index
    
    def _get_clicked_reward_index(self, mouse_pos: tuple) -> Optional[int]:
        """クリックされた報酬のインデックスを取得"""
        mouse_x, mouse_y = mouse_pos
        
        for i in range(len(self.rewards)):
            x = self.start_x + i * (self.reward_width + self.reward_spacing)
            y = self.start_y
            
            card_rect = pygame.Rect(x, y, self.reward_width, self.reward_height)
            if card_rect.collidepoint(mouse_x, mouse_y):
                return i
        
        return None
    
    def _select_reward(self):
        """報酬を選択"""
        if 0 <= self.selected_index < len(self.rewards):
            self.selected_reward = self.rewards[self.selected_index]
            self.selection_made = True
            logger.info(f"Selected reward: {self.selected_reward.name}")
    
    def _return_to_dungeon_map(self):
        """ダンジョンマップに戻る"""
        try:
            # 選択された報酬を適用
            if self.selected_reward:
                self._apply_selected_reward(self.selected_reward)
            
            from dungeon.map_handler import DungeonMapHandler
            
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
    
    def _apply_selected_reward(self, reward: Reward):
        """選択された報酬を適用"""
        try:
            player = self.engine.player
            
            if reward.reward_type == RewardType.GOLD:
                player.add_gold(reward.value)
                logger.info(f"Applied gold reward: +{reward.value} gold")
            
            elif reward.reward_type == RewardType.HP_UPGRADE:
                player.increase_max_hp(reward.value)
                logger.info(f"Applied HP upgrade: +{reward.value} max HP")
            
            elif reward.reward_type == RewardType.POTION:
                player.add_potion(reward.value)
                logger.info(f"Applied potion reward: {reward.value}")
            
            elif reward.reward_type == RewardType.ARTIFACT:
                player.add_artifact(reward.value)
                logger.info(f"Applied artifact reward: {reward.value}")
            
            elif reward.reward_type == RewardType.CHAIN_UPGRADE:
                player.increase_chain_damage_multiplier(0.1)  # 10%アップ
                logger.info(f"Applied chain upgrade: +10% chain damage")
            
            elif reward.reward_type == RewardType.SPECIAL_PUYO:
                # 特殊ぷよの出現率を上昇（プレイヤーデータ経由で永続化）
                special_type = reward.value
                new_rate = player.increase_special_puyo_rate(special_type.value, 0.05)  # 5%上昇
                logger.info(f"Applied special puyo reward: {special_type.value} rate increased to {new_rate*100:.0f}%")
            
            else:
                logger.warning(f"Unknown reward type: {reward.reward_type}")
                
        except Exception as e:
            logger.error(f"Failed to apply reward {reward.name}: {e}")
    
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
        title_font = font_title
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
        
        # デバッグ情報
        logger.debug(f"Rendering reward: type={reward.reward_type}, value_type={type(reward.value)}, value={reward.value}")
        
        # アイコン/値の表示
        icon_y = card_rect.y + 20
        
        if reward.reward_type == RewardType.GOLD:
            # ゴールドアイコン
            icon_text = font_medium.render("G", True, Colors.YELLOW)
            icon_rect = icon_text.get_rect(center=(card_rect.centerx, icon_y + 20))
            surface.blit(icon_text, icon_rect)
            
            # 金額
            value_text = font_medium.render(str(reward.value), True, Colors.YELLOW)
            value_rect = value_text.get_rect(center=(card_rect.centerx, icon_y + 60))
            surface.blit(value_text, value_rect)
        
        elif reward.reward_type == RewardType.POTION:
            # ポーションアイコン
            if hasattr(reward.value, 'icon') and hasattr(reward.value, 'color'):
                try:
                    icon_text = font_medium.render(reward.value.icon, True, reward.value.color)
                except (UnicodeEncodeError, AttributeError):
                    icon_text = font_medium.render("P", True, Colors.BLUE)
            else:
                # フォールバック：文字列の場合は薬瓶アイコン
                icon_text = font_medium.render("P", True, Colors.BLUE)
            icon_rect = icon_text.get_rect(center=(card_rect.centerx, icon_y + 30))
            surface.blit(icon_text, icon_rect)
        
        elif reward.reward_type == RewardType.ARTIFACT:
            # 装飾品アイコン
            if hasattr(reward.value, 'icon') and hasattr(reward.value, 'color'):
                try:
                    icon_text = font_medium.render(reward.value.icon, True, reward.value.color)
                except (UnicodeEncodeError, AttributeError):
                    icon_text = font_medium.render("A", True, Colors.PURPLE)
            else:
                # フォールバック：文字列の場合は装飾品アイコン
                icon_text = font_medium.render("A", True, Colors.PURPLE)
            icon_rect = icon_text.get_rect(center=(card_rect.centerx, icon_y + 30))
            surface.blit(icon_text, icon_rect)
        
        elif reward.reward_type == RewardType.HP_UPGRADE:
            # HPアイコン
            icon_text = font_medium.render("H", True, Colors.RED)
            icon_rect = icon_text.get_rect(center=(card_rect.centerx, icon_y + 20))
            surface.blit(icon_text, icon_rect)
            
            # HP増加量
            value_text = font_medium.render(f"+{reward.value}", True, Colors.RED)
            value_rect = value_text.get_rect(center=(card_rect.centerx, icon_y + 60))
            surface.blit(value_text, value_rect)
        
        elif reward.reward_type == RewardType.SPECIAL_PUYO:
            # 特殊ぷよアイコン（SimpleSpecialType対応）
            from core.simple_special_puyo import SimpleSpecialType
            
            # タイプに応じたアイコンと色を選択
            icon_map = {
                SimpleSpecialType.HEAL: ("H", Colors.GREEN),
                SimpleSpecialType.BOMB: ("B", Colors.RED),
                SimpleSpecialType.LIGHTNING: ("L", Colors.YELLOW),
                SimpleSpecialType.SHIELD: ("S", Colors.BLUE),
                SimpleSpecialType.MULTIPLIER: ("M", Colors.PURPLE),
                SimpleSpecialType.POISON: ("P", Colors.GREEN),
            }
            
            icon_char, color = icon_map.get(reward.value, ("*", Colors.WHITE))
            
            # アイコン描画
            icon_text = font_medium.render(icon_char, True, color)
            icon_rect = icon_text.get_rect(center=(card_rect.centerx, icon_y + 20))
            surface.blit(icon_text, icon_rect)
            
            # 特殊ぷよの表示名を取得
            try:
                display_name = reward.value.get_display_name()
                # 「ぷよ」を削除してコンパクトに表示
                if display_name.endswith("ぷよ"):
                    display_name = display_name[:-2]
            except Exception:
                display_name = reward.value.value.upper()
            
            # 名前を描画
            name_text = font_small.render(display_name, True, color)
            name_rect = name_text.get_rect(center=(card_rect.centerx, icon_y + 60))
            surface.blit(name_text, name_rect)
        
        elif reward.reward_type == RewardType.CHAIN_UPGRADE:
            # 連鎖アイコン
            icon_text = font_medium.render("🔗", True, Colors.PURPLE)
            icon_rect = icon_text.get_rect(center=(card_rect.centerx, icon_y + 20))
            surface.blit(icon_text, icon_rect)
            
            # ダメージ増加量
            value_text = font_medium.render(f"+{reward.value}%", True, Colors.PURPLE)
            value_rect = value_text.get_rect(center=(card_rect.centerx, icon_y + 60))
            surface.blit(value_text, value_rect)
        
        else:
            # その他のアイコン
            icon_text = font_medium.render("?", True, reward.get_color())
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