"""
宝箱ハンドラー - 自動報酬獲得システム  
Drop Puzzle × Roguelike の宝箱画面管理
"""

import pygame
import logging
import random
from typing import Dict, List, Optional, Union

from core.constants import *
from core.game_engine import GameEngine
from items.potions import Potion, create_random_potion
from items.artifacts import Artifact, create_random_artifact
from rewards.reward_system import RewardGenerator, RewardType, Reward
from inventory.player_inventory import create_item

logger = logging.getLogger(__name__)


class TreasureHandler:
    """宝箱画面の管理クラス"""
    
    def __init__(self, engine: GameEngine, current_node=None):
        self.engine = engine
        self.current_node = current_node
        
        # 宝箱の状態
        self.chest_opened = False
        self.treasure_revealed = False
        self.animation_timer = 0.0
        self.reveal_delay = 1.5  # 宝箱開封アニメーション時間
        
        # 宝箱から獲得する報酬
        self.treasure_rewards = self._generate_treasure_rewards()
        
        # UI設定
        self.background_color = (15, 25, 35)  # 深い青色
        
        logger.info(f"TreasureHandler initialized with {len(self.treasure_rewards)} rewards")
    
    def _generate_treasure_rewards(self) -> List[Reward]:
        """宝箱の報酬を生成"""
        rewards = []
        
        # フロアレベルを取得
        floor_level = 1
        if (hasattr(self.engine, 'persistent_dungeon_map') and 
            self.engine.persistent_dungeon_map and 
            self.current_node):
            floor_level = self.current_node.floor + 1
        
        # 宝箱は通常より良い報酬を提供
        reward_generator = RewardGenerator()
        
        # 必ずゴールドを多めに獲得
        gold_amount = random.randint(40, 80) + floor_level * 10
        rewards.append(Reward(
            reward_type=RewardType.GOLD,
            value=gold_amount,
            name=f"{gold_amount} ゴールド",
            description="宝箱から見つけた金貨",
            rarity=Rarity.COMMON
        ))
        
        # 高確率で装飾品またはレアポーション
        treasure_type = random.choices(
            [RewardType.ARTIFACT, RewardType.POTION, RewardType.HP_UPGRADE],
            weights=[50, 30, 20]
        )[0]
        
        if treasure_type == RewardType.ARTIFACT:
            # より高いレアリティの装飾品
            artifact = self._create_treasure_artifact(floor_level)
            rewards.append(Reward(
                reward_type=RewardType.ARTIFACT,
                value=artifact,
                name=artifact.name,
                description=artifact.description,
                rarity=artifact.rarity
            ))
        elif treasure_type == RewardType.POTION:
            # より高いレアリティのポーション
            potion = self._create_treasure_potion(floor_level)
            rewards.append(Reward(
                reward_type=RewardType.POTION,
                value=potion,
                name=potion.name,
                description=potion.description,
                rarity=potion.rarity
            ))
        else:
            # 大きなHP増加
            hp_amount = random.randint(15, 25) + floor_level * 2
            rewards.append(Reward(
                reward_type=RewardType.HP_UPGRADE,
                value=hp_amount,
                name=f"最大HP +{hp_amount}",
                description="古代の生命力が宿る宝石",
                rarity=Rarity.RARE
            ))
        
        return rewards
    
    def _create_treasure_artifact(self, floor_level: int):
        """宝箱用の高品質装飾品を作成（簡易版）"""
        # レアリティを底上げ
        rarity_weights = {
            Rarity.UNCOMMON: 20,
            Rarity.RARE: 40,
            Rarity.EPIC: 30,
            Rarity.LEGENDARY: 10
        }
        
        chosen_rarity = random.choices(
            list(rarity_weights.keys()),
            weights=list(rarity_weights.values())
        )[0]
        
        # 宝箱専用の特別な装飾品（簡易オブジェクト）
        treasure_artifacts = [
            {
                'name': 'Ancient Amulet',
                'description': 'Increases max HP by 20 and chain damage by 15%',
                'effect_type': 'hybrid',
                'hp_bonus': 20,
                'chain_bonus': 15,
                'rarity': chosen_rarity,
                'icon': 'A',
                'color': Colors.PURPLE
            },
            {
                'name': 'Golden Ring',
                'description': 'Gain 10 gold after each battle',
                'effect_type': 'gold_per_battle',
                'effect_value': 10,
                'rarity': chosen_rarity,
                'icon': 'R',
                'color': Colors.YELLOW
            },
            {
                'name': 'Crystal Heart',
                'description': 'Heal 5 HP at the start of each battle',
                'effect_type': 'heal_per_battle',
                'effect_value': 5,
                'rarity': chosen_rarity,
                'icon': 'C',
                'color': Colors.CYAN
            }
        ]
        
        artifact_data = random.choice(treasure_artifacts)
        
        # 簡易的なArtifactオブジェクトを作成
        class SimpleArtifact:
            def __init__(self, data):
                self.name = data['name']
                self.description = data['description']
                self.effect_type = data['effect_type']
                self.effect_value = data.get('effect_value', 0)
                self.hp_bonus = data.get('hp_bonus', 0)
                self.chain_bonus = data.get('chain_bonus', 0)
                self.rarity = data['rarity']
                self.icon = data['icon']
                self.color = data['color']
        
        return SimpleArtifact(artifact_data)
    
    def _create_treasure_potion(self, floor_level: int):
        """宝箱用の高品質ポーションを作成（簡易版）"""
        # レアリティを底上げ
        rarity_weights = {
            Rarity.UNCOMMON: 30,
            Rarity.RARE: 40,
            Rarity.EPIC: 25,
            Rarity.LEGENDARY: 5
        }
        
        chosen_rarity = random.choices(
            list(rarity_weights.keys()),
            weights=list(rarity_weights.values())
        )[0]
        
        # 宝箱専用の特別なポーション（簡易オブジェクト）
        treasure_potions = [
            {
                'name': 'Elixir of Power',
                'description': 'Double damage for next 5 chains',
                'effect_type': 'damage_boost',
                'effect_value': 100,  # 100%ダメージ増加
                'duration': 5,
                'rarity': chosen_rarity,
                'icon': 'E',
                'color': Colors.YELLOW
            },
            {
                'name': 'Healing Nectar',
                'description': 'Restore 50 HP immediately',
                'effect_type': 'heal',
                'effect_value': 50,
                'rarity': chosen_rarity,
                'icon': 'H',
                'color': Colors.GREEN
            },
            {
                'name': 'Mystic Brew',
                'description': 'Next 3 battles start with extra energy',
                'effect_type': 'chain_power_boost',
                'effect_value': 3,
                'rarity': chosen_rarity,
                'icon': 'M',
                'color': Colors.PURPLE
            }
        ]
        
        potion_data = random.choice(treasure_potions)
        
        # 簡易的なPotionオブジェクトを作成
        class SimplePotion:
            def __init__(self, data):
                self.name = data['name']
                self.description = data['description']
                self.effect_type = data['effect_type']
                self.effect_value = data['effect_value']
                self.duration = data.get('duration', 1)
                self.rarity = data['rarity']
                self.icon = data['icon']
                self.color = data['color']
        
        return SimplePotion(potion_data)
    
    def on_enter(self, previous_state):
        """宝箱画面開始"""
        logger.info("Entering treasure chest")
        self.chest_opened = False
        self.treasure_revealed = False
        self.animation_timer = 0.0
        
        # 自動で宝箱を開ける
        self.chest_opened = True
    
    def handle_event(self, event: pygame.event.Event):
        """イベント処理"""
        if self.treasure_revealed:
            # 報酬確認後はマップに戻る
            if event.type == pygame.KEYDOWN and (event.key == pygame.K_RETURN or event.key == pygame.K_ESCAPE):
                self._collect_treasure()
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                self._collect_treasure()
        else:
            # 宝箱開封中はスペースキーまたはクリックで即座に表示
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                self.treasure_revealed = True
                self.animation_timer = self.reveal_delay
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                self.treasure_revealed = True
                self.animation_timer = self.reveal_delay
    
    def _collect_treasure(self):
        """宝箱の報酬を回収してマップに戻る"""
        # 宝箱訪問統計を更新
        self.engine.player.visit_room("treasure")
        
        # 報酬を適用
        for reward in self.treasure_rewards:
            self._apply_reward(reward)
        
        try:
            from dungeon.map_handler import DungeonMapHandler
            
            # マップ進行処理
            if (hasattr(self.engine, 'persistent_dungeon_map') and self.engine.persistent_dungeon_map and 
                self.current_node):
                
                dungeon_map = self.engine.persistent_dungeon_map
                
                logger.info(f"Processing map progression after treasure for node: {self.current_node.node_id}")
                
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
            
            logger.info("Returned to dungeon map after treasure collection")
            
        except Exception as e:
            logger.error(f"Failed to return to dungeon map: {e}")
            # フォールバック: メニューに戻る
            self.engine.change_state(GameState.MENU)
    
    def _apply_reward(self, reward: Reward):
        """報酬を適用"""
        if reward.reward_type == RewardType.GOLD:
            self.engine.player.gain_gold(reward.value)
            logger.info(f"Gained {reward.value} gold")
        
        elif reward.reward_type == RewardType.HP_UPGRADE:
            self.engine.player.max_hp += reward.value
            self.engine.player.hp += reward.value  # 現在HPも増加
            logger.info(f"Max HP increased by {reward.value}")
        
        elif reward.reward_type == RewardType.POTION:
            # Convert Potion object to inventory item
            potion_item = self._convert_potion_to_item(reward.value)
            if potion_item:
                self.engine.player.inventory.add_item(potion_item)
                logger.info(f"Gained potion: {reward.value.name}")
        
        elif reward.reward_type == RewardType.ARTIFACT:
            # Convert Artifact object to inventory item
            artifact_item = self._convert_artifact_to_item(reward.value)
            if artifact_item:
                self.engine.player.inventory.add_item(artifact_item)
                self._apply_artifact_effect(reward.value)
                logger.info(f"Gained artifact: {reward.value.name}")
        
        elif reward.reward_type == RewardType.SPECIAL_PUYO_BOOST:
            # 特殊ぷよ出現率を永続的に増加
            from special_puyo.special_puyo import special_puyo_manager
            boost_multiplier = 1.0 + (reward.value / 100.0)  # パーセントを倍率に変換
            special_puyo_manager.spawn_chance = min(0.5, special_puyo_manager.spawn_chance * boost_multiplier)
            logger.info(f"Special puyo spawn rate increased by {reward.value}%! Current rate: {special_puyo_manager.spawn_chance:.1%}")
        
        elif reward.reward_type == RewardType.CHAIN_UPGRADE:
            # 連鎖ダメージ倍率を上昇
            self.engine.player.chain_damage_multiplier += reward.value / 100.0
            logger.info(f"Chain damage increased by {reward.value}%! Current multiplier: {self.engine.player.chain_damage_multiplier:.1f}x")
    
    def _apply_artifact_effect(self, artifact: Artifact):
        """装飾品の効果を適用"""
        if artifact.effect_type == "hybrid":
            # 複合効果
            if hasattr(artifact, 'hp_bonus'):
                self.engine.player.max_hp += artifact.hp_bonus
                self.engine.player.hp += artifact.hp_bonus
            if hasattr(artifact, 'chain_bonus'):
                self.engine.player.chain_damage_multiplier += artifact.chain_bonus / 100.0
        elif artifact.effect_type == "max_hp":
            self.engine.player.max_hp += artifact.effect_value
            self.engine.player.hp += artifact.effect_value
        elif artifact.effect_type == "damage":
            self.engine.player.skills.attack_power += artifact.effect_value
        # その他の効果は戦闘時に処理
        
        # アーティファクト効果を再計算
        self.engine.player.apply_artifact_effects()
    
    def _convert_potion_to_item(self, potion: Potion):
        """Potion object を inventory Item に変換"""
        from inventory.player_inventory import Item, ItemType, ItemRarity
        
        # レアリティ変換
        rarity_mapping = {
            Rarity.COMMON: ItemRarity.COMMON,
            Rarity.UNCOMMON: ItemRarity.UNCOMMON,
            Rarity.RARE: ItemRarity.RARE,
            Rarity.EPIC: ItemRarity.EPIC,
            Rarity.LEGENDARY: ItemRarity.LEGENDARY
        }
        
        # 効果値を取得
        effect_value = 0
        if hasattr(potion, 'effect') and hasattr(potion.effect, 'value'):
            effect_value = int(potion.effect.value)
        
        return Item(
            id=f"treasure_potion_{hash(potion.name) % 10000}",
            name=potion.name,
            description=potion.description,
            item_type=ItemType.POTION,
            rarity=rarity_mapping.get(potion.rarity, ItemRarity.COMMON),
            quantity=1,
            consumable=True,
            effect_value=effect_value
        )
    
    def _convert_artifact_to_item(self, artifact: Artifact):
        """Artifact object を inventory Item に変換"""
        from inventory.player_inventory import Item, ItemType, ItemRarity
        
        # レアリティ変換
        rarity_mapping = {
            Rarity.COMMON: ItemRarity.COMMON,
            Rarity.UNCOMMON: ItemRarity.UNCOMMON,
            Rarity.RARE: ItemRarity.RARE,
            Rarity.EPIC: ItemRarity.EPIC,
            Rarity.LEGENDARY: ItemRarity.LEGENDARY
        }
        
        # 効果値を取得
        effect_value = 0
        if hasattr(artifact, 'effect_value'):
            effect_value = artifact.effect_value
        
        return Item(
            id=f"treasure_artifact_{hash(artifact.name) % 10000}",
            name=artifact.name,
            description=artifact.description,
            item_type=ItemType.ARTIFACT,
            rarity=rarity_mapping.get(artifact.rarity, ItemRarity.COMMON),
            quantity=1,
            consumable=False,
            effect_value=effect_value
        )
    
    def render(self, surface: pygame.Surface):
        """描画処理"""
        # 背景
        surface.fill(self.background_color)
        
        # 神秘的な背景効果
        self._render_mystical_atmosphere(surface)
        
        if not self.treasure_revealed:
            # 宝箱開封アニメーション
            self._render_chest_opening(surface)
        else:
            # 報酬表示
            self._render_treasure_rewards(surface)
        
        # 操作説明
        self._render_instructions(surface)
    
    def _render_mystical_atmosphere(self, surface: pygame.Surface):
        """神秘的な雰囲気を演出"""
        # 金色の光の効果
        center_x = SCREEN_WIDTH // 2
        center_y = SCREEN_HEIGHT // 2
        
        for i in range(4):
            light_radius = 150 + i * 50
            light_alpha = 40 - i * 8
            if light_alpha > 0:
                light_surface = pygame.Surface((light_radius * 2, light_radius * 2))
                light_surface.set_alpha(light_alpha)
                light_surface.fill((0, 0, 0))
                light_surface.set_colorkey((0, 0, 0))
                pygame.draw.circle(light_surface, (255, 215, 0), (light_radius, light_radius), light_radius)
                surface.blit(light_surface, (center_x - light_radius, center_y - light_radius))
    
    def _render_chest_opening(self, surface: pygame.Surface):
        """宝箱開封アニメーションを描画"""
        font_title = self.engine.fonts['title']
        font_large = self.engine.fonts['large']
        
        # 宝箱アイコン
        chest_icon = "T" if not self.chest_opened else "T"
        chest_text = font_title.render(chest_icon, True, Colors.YELLOW)
        chest_rect = chest_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50))
        surface.blit(chest_text, chest_rect)
        
        # メッセージ
        if not self.chest_opened:
            message = "Discovering treasure..."
        else:
            message = "Opening chest..."
        
        message_text = font_large.render(message, True, Colors.WHITE)
        message_rect = message_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50))
        surface.blit(message_text, message_rect)
        
        # プログレスバー風の演出
        bar_width = 300
        bar_height = 20
        bar_x = SCREEN_WIDTH // 2 - bar_width // 2
        bar_y = SCREEN_HEIGHT // 2 + 100
        
        # 背景バー
        pygame.draw.rect(surface, Colors.DARK_GRAY, (bar_x, bar_y, bar_width, bar_height))
        
        # 進行バー
        progress = min(1.0, self.animation_timer / self.reveal_delay)
        progress_width = int(bar_width * progress)
        pygame.draw.rect(surface, Colors.YELLOW, (bar_x, bar_y, progress_width, bar_height))
    
    def _render_treasure_rewards(self, surface: pygame.Surface):
        """宝箱の報酬を描画"""
        font_title = self.engine.fonts['title']
        font_large = self.engine.fonts['large']
        font_medium = self.engine.fonts['medium']
        
        # タイトル
        title_text = font_title.render("TREASURE FOUND!", True, Colors.YELLOW)
        title_rect = title_text.get_rect(center=(SCREEN_WIDTH // 2, 150))
        surface.blit(title_text, title_rect)
        
        # 報酬リスト
        start_y = 250
        for i, reward in enumerate(self.treasure_rewards):
            y = start_y + i * 80
            
            # 報酬アイコン
            if reward.reward_type == RewardType.GOLD:
                icon = "G"
                color = Colors.YELLOW
            elif reward.reward_type == RewardType.ARTIFACT:
                icon = reward.value.icon
                color = reward.value.color
            elif reward.reward_type == RewardType.POTION:
                icon = reward.value.icon
                color = reward.value.color
            else:
                icon = "H"
                color = Colors.RED
            
            icon_text = font_large.render(icon, True, color)
            icon_rect = icon_text.get_rect(center=(SCREEN_WIDTH // 2 - 150, y))
            surface.blit(icon_text, icon_rect)
            
            # 報酬名
            name_text = font_medium.render(reward.name, True, Colors.WHITE)
            name_rect = name_text.get_rect(center=(SCREEN_WIDTH // 2 + 50, y - 15))
            surface.blit(name_text, name_rect)
            
            # 報酬説明
            desc_text = self.engine.fonts['small'].render(reward.description, True, Colors.LIGHT_GRAY)
            desc_rect = desc_text.get_rect(center=(SCREEN_WIDTH // 2 + 50, y + 15))
            surface.blit(desc_text, desc_rect)
    
    def _render_instructions(self, surface: pygame.Surface):
        """操作説明を描画"""
        font_small = self.engine.fonts['small']
        
        if not self.treasure_revealed:
            instructions = ["Space - Skip animation"]
        else:
            instructions = ["Enter/ESC - Collect treasure and continue"]
        
        for i, instruction in enumerate(instructions):
            text = font_small.render(instruction, True, Colors.LIGHT_GRAY)
            text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 60 + i * 20))
            surface.blit(text, text_rect)
    
    def update(self, dt: float):
        """更新処理"""
        if self.chest_opened and not self.treasure_revealed:
            self.animation_timer += dt
            if self.animation_timer >= self.reveal_delay:
                self.treasure_revealed = True