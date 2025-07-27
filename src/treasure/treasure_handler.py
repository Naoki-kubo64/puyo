"""
宝箱ハンドラー - 自動報酬獲得システム  
Drop Puzzle × Roguelike の宝箱画面管理
"""

import pygame
import logging
import random
from typing import Dict, List, Optional, Union

from ..core.constants import *
from ..core.game_engine import GameEngine
from ..items.potions import Potion, create_random_potion
from ..items.artifacts import Artifact, create_random_artifact
from ..rewards.reward_system import RewardGenerator, RewardType, Reward

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
    
    def _create_treasure_artifact(self, floor_level: int) -> Artifact:
        """宝箱用の高品質装飾品を作成"""
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
        
        # 宝箱専用の特別な装飾品
        treasure_artifacts = [
            {
                'name': 'Ancient Amulet',
                'description': 'Increases max HP by 20 and chain damage by 15%',
                'effect_type': 'hybrid',
                'hp_bonus': 20,
                'chain_bonus': 15,
                'rarity': Rarity.EPIC,
                'icon': '🔮',
                'color': Colors.PURPLE
            },
            {
                'name': 'Golden Ring',
                'description': 'Gain 10 gold after each battle',
                'effect_type': 'gold_per_battle',
                'effect_value': 10,
                'rarity': Rarity.RARE,
                'icon': '💍',
                'color': Colors.YELLOW
            },
            {
                'name': 'Crystal Heart',
                'description': 'Heal 5 HP at the start of each battle',
                'effect_type': 'heal_per_battle',
                'effect_value': 5,
                'rarity': Rarity.UNCOMMON,
                'icon': '💎',
                'color': Colors.CYAN
            }
        ]
        
        artifact_data = random.choice(treasure_artifacts)
        
        return Artifact(
            name=artifact_data['name'],
            description=artifact_data['description'],
            rarity=chosen_rarity,
            effect_type=artifact_data['effect_type'],
            effect_value=artifact_data.get('effect_value', 0),
            icon=artifact_data['icon'],
            color=artifact_data['color']
        )
    
    def _create_treasure_potion(self, floor_level: int) -> Potion:
        """宝箱用の高品質ポーションを作成"""
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
        
        # 宝箱専用の特別なポーション
        treasure_potions = [
            {
                'name': 'Elixir of Power',
                'description': 'Double damage for next 5 chains',
                'effect_type': 'damage_boost',
                'effect_value': 100,  # 100%ダメージ増加
                'duration': 5,
                'rarity': Rarity.EPIC,
                'icon': '⚡',
                'color': Colors.YELLOW
            },
            {
                'name': 'Healing Nectar',
                'description': 'Restore 50 HP immediately',
                'effect_type': 'heal',
                'effect_value': 50,
                'rarity': Rarity.RARE,
                'icon': '🍯',
                'color': Colors.GREEN
            },
            {
                'name': 'Mystic Brew',
                'description': 'Next 3 battles start with extra energy',
                'effect_type': 'energy_boost',
                'effect_value': 3,
                'rarity': Rarity.UNCOMMON,
                'icon': '🧪',
                'color': Colors.PURPLE
            }
        ]
        
        potion_data = random.choice(treasure_potions)
        
        return Potion(
            name=potion_data['name'],
            description=potion_data['description'],
            rarity=chosen_rarity,
            effect_type=potion_data['effect_type'],
            effect_value=potion_data['effect_value'],
            icon=potion_data['icon'],
            color=potion_data['color']
        )
    
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
        else:
            # 宝箱開封中はスペースキーで即座に表示
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                self.treasure_revealed = True
                self.animation_timer = self.reveal_delay
    
    def _collect_treasure(self):
        """宝箱の報酬を回収してマップに戻る"""
        # 報酬を適用
        for reward in self.treasure_rewards:
            self._apply_reward(reward)
        
        try:
            from ..dungeon.map_handler import DungeonMapHandler
            
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
            if not hasattr(self.engine.game_data, 'gold'):
                self.engine.game_data.gold = 0
            self.engine.game_data.gold += reward.value
            logger.info(f"Gained {reward.value} gold")
        
        elif reward.reward_type == RewardType.HP_UPGRADE:
            self.engine.game_data.player_max_hp += reward.value
            self.engine.game_data.player_hp += reward.value  # 現在HPも増加
            logger.info(f"Max HP increased by {reward.value}")
        
        elif reward.reward_type == RewardType.POTION:
            if not hasattr(self.engine.game_data, 'potions'):
                self.engine.game_data.potions = []
            self.engine.game_data.potions.append(reward.value)
            logger.info(f"Gained potion: {reward.value.name}")
        
        elif reward.reward_type == RewardType.ARTIFACT:
            if not hasattr(self.engine.game_data, 'artifacts'):
                self.engine.game_data.artifacts = []
            self.engine.game_data.artifacts.append(reward.value)
            self._apply_artifact_effect(reward.value)
            logger.info(f"Gained artifact: {reward.value.name}")
    
    def _apply_artifact_effect(self, artifact: Artifact):
        """装飾品の効果を適用"""
        if artifact.effect_type == "hybrid":
            # 複合効果
            if hasattr(artifact, 'hp_bonus'):
                self.engine.game_data.player_max_hp += artifact.hp_bonus
                self.engine.game_data.player_hp += artifact.hp_bonus
            if hasattr(artifact, 'chain_bonus'):
                if not hasattr(self.engine.game_data, 'chain_damage_bonus'):
                    self.engine.game_data.chain_damage_bonus = 0
                self.engine.game_data.chain_damage_bonus += artifact.chain_bonus
        elif artifact.effect_type == "max_hp":
            self.engine.game_data.player_max_hp += artifact.effect_value
            self.engine.game_data.player_hp += artifact.effect_value
        elif artifact.effect_type == "damage":
            if not hasattr(self.engine.game_data, 'damage_bonus'):
                self.engine.game_data.damage_bonus = 0
            self.engine.game_data.damage_bonus += artifact.effect_value
        # その他の効果は戦闘時に処理
    
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
        chest_icon = "📦" if not self.chest_opened else "💎"
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
        title_text = font_title.render("💎 TREASURE FOUND! 💎", True, Colors.YELLOW)
        title_rect = title_text.get_rect(center=(SCREEN_WIDTH // 2, 150))
        surface.blit(title_text, title_rect)
        
        # 報酬リスト
        start_y = 250
        for i, reward in enumerate(self.treasure_rewards):
            y = start_y + i * 80
            
            # 報酬アイコン
            if reward.reward_type == RewardType.GOLD:
                icon = "💰"
                color = Colors.YELLOW
            elif reward.reward_type == RewardType.ARTIFACT:
                icon = reward.value.icon
                color = reward.value.color
            elif reward.reward_type == RewardType.POTION:
                icon = reward.value.icon
                color = reward.value.color
            else:
                icon = "❤"
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