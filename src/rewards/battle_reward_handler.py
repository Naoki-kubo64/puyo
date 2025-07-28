"""
戦闘後の詳細報酬システム
Slay the Spire風の報酬選択画面
"""

import pygame
import random
from typing import List, Optional
from core.state_handler import StateHandler
from core.constants import GameState, Colors
from core.game_engine import GameEngine
from inventory.player_inventory import create_item, ItemRarity
from .reward_system import Reward, RewardType

class BattleRewardHandler(StateHandler):
    def __init__(self, engine: GameEngine, enemy_type: str = "normal", floor: int = 1):
        super().__init__(engine)
        self.enemy_type = enemy_type
        self.floor = floor
        self.font_large = pygame.font.Font(None, 48)
        self.font_medium = pygame.font.Font(None, 36)
        self.font_small = pygame.font.Font(None, 28)
        
        self.rewards: List[Reward] = []
        self.reward_rects: List[pygame.Rect] = []
        self.hovered_reward = -1
        self.selected_rewards: List[bool] = []
        
        # 報酬生成
        self._generate_rewards()
    
    def _generate_rewards(self):
        """敵タイプと階層に応じて報酬を生成"""
        self.rewards.clear()
        
        # 基本ゴールド報酬（必須）
        base_gold = self._calculate_base_gold()
        self.rewards.append(Reward(
            reward_type=RewardType.GOLD,
            value=base_gold,
            name=f"{base_gold}ゴールド",
            description="戦闘勝利の報酬",
            rarity=ItemRarity.COMMON
        ))
        
        # 追加報酬の数を決定
        additional_rewards = 2
        if self.enemy_type == "elite":
            additional_rewards = 3
        elif self.enemy_type == "boss":
            additional_rewards = 4
        
        # 追加報酬を生成
        for _ in range(additional_rewards):
            reward = self._generate_random_reward()
            if reward:
                self.rewards.append(reward)
        
        # 選択状態初期化
        self.selected_rewards = [False] * len(self.rewards)
        # ゴールドは自動選択
        if self.rewards:
            self.selected_rewards[0] = True
    
    def _calculate_base_gold(self) -> int:
        """基本ゴールド報酬を計算"""
        base = 15
        if self.enemy_type == "elite":
            base = 25
        elif self.enemy_type == "boss":
            base = 40
        
        # 階層ボーナス
        floor_bonus = self.floor * 2
        
        # ランダム要素
        variation = random.randint(-5, 5)
        
        return max(10, base + floor_bonus + variation)
    
    def _generate_random_reward(self) -> Optional[Reward]:
        """ランダム報酬を生成"""
        reward_types = [
            (RewardType.POTION, 30),
            (RewardType.ARTIFACT, 20),
            (RewardType.HP_UPGRADE, 25),
            (RewardType.ENERGY_UPGRADE, 10),
            (RewardType.CHAIN_UPGRADE, 15)
        ]
        
        # エリートとボスは高品質報酬の確率が高い
        if self.enemy_type in ["elite", "boss"]:
            reward_types = [
                (RewardType.POTION, 20),
                (RewardType.ARTIFACT, 35),
                (RewardType.HP_UPGRADE, 20),
                (RewardType.ENERGY_UPGRADE, 15),
                (RewardType.CHAIN_UPGRADE, 10)
            ]
        
        # 重み付きランダム選択
        total_weight = sum(weight for _, weight in reward_types)
        roll = random.randint(1, total_weight)
        
        cumulative = 0
        for reward_type, weight in reward_types:
            cumulative += weight
            if roll <= cumulative:
                return self._create_specific_reward(reward_type)
        
        return None
    
    def _create_specific_reward(self, reward_type: RewardType) -> Reward:
        """特定タイプの報酬を作成"""
        if reward_type == RewardType.POTION:
            return self._create_potion_reward()
        elif reward_type == RewardType.ARTIFACT:
            return self._create_artifact_reward()
        elif reward_type == RewardType.HP_UPGRADE:
            return self._create_hp_upgrade_reward()
        elif reward_type == RewardType.ENERGY_UPGRADE:
            return self._create_energy_upgrade_reward()
        elif reward_type == RewardType.CHAIN_UPGRADE:
            return self._create_chain_upgrade_reward()
        
        return None
    
    def _create_potion_reward(self) -> Reward:
        """ポーション報酬を作成"""
        potions = [
            ("health_potion_small", "小さな体力ポーション", ItemRarity.COMMON),
            ("health_potion_medium", "体力ポーション", ItemRarity.UNCOMMON),
            ("energy_potion", "エネルギーポーション", ItemRarity.UNCOMMON)
        ]
        
        # 階層とエネミータイプで確率調整
        if self.floor >= 5 or self.enemy_type in ["elite", "boss"]:
            potions.append(("health_potion_large", "大きな体力ポーション", ItemRarity.RARE))
        
        potion_id, name, rarity = random.choice(potions)
        
        return Reward(
            reward_type=RewardType.POTION,
            value=potion_id,
            name=name,
            description="クリックで獲得",
            rarity=rarity
        )
    
    def _create_artifact_reward(self) -> Reward:
        """アーティファクト報酬を作成"""
        artifacts = [
            ("lucky_coin", "幸運のコイン", ItemRarity.UNCOMMON),
            ("vitality_amulet", "活力のお守り", ItemRarity.UNCOMMON),
            ("power_ring", "力の指輪", ItemRarity.RARE),
            ("merchants_badge", "商人の徽章", ItemRarity.RARE)
        ]
        
        # 高階層・強敵では高品質アーティファクト
        if self.floor >= 7 or self.enemy_type == "boss":
            artifacts.extend([
                ("energy_crystal", "エネルギークリスタル", ItemRarity.EPIC),
                ("golden_scarab", "黄金のスカラベ", ItemRarity.EPIC)
            ])
        
        artifact_id, name, rarity = random.choice(artifacts)
        
        return Reward(
            reward_type=RewardType.ARTIFACT,
            value=artifact_id,
            name=name,
            description="永続効果アイテム",
            rarity=rarity
        )
    
    def _create_hp_upgrade_reward(self) -> Reward:
        """HP強化報酬を作成"""
        hp_gain = random.randint(8, 15)
        if self.enemy_type in ["elite", "boss"]:
            hp_gain = random.randint(12, 20)
        
        return Reward(
            reward_type=RewardType.HP_UPGRADE,
            value=hp_gain,
            name=f"最大HP+{hp_gain}",
            description="最大HPが永続的に増加",
            rarity=ItemRarity.UNCOMMON
        )
    
    def _create_energy_upgrade_reward(self) -> Reward:
        """エネルギー強化報酬を作成"""
        return Reward(
            reward_type=RewardType.ENERGY_UPGRADE,
            value=1,
            name="最大エネルギー+1",
            description="戦闘で使えるエネルギーが増加",
            rarity=ItemRarity.RARE
        )
    
    def _create_chain_upgrade_reward(self) -> Reward:
        """連鎖強化報酬を作成"""
        chain_bonus = random.randint(10, 20)
        if self.enemy_type in ["elite", "boss"]:
            chain_bonus = random.randint(15, 25)
        
        return Reward(
            reward_type=RewardType.CHAIN_UPGRADE,
            value=chain_bonus,
            name=f"連鎖ダメージ+{chain_bonus}%",
            description="連鎖攻撃の威力が永続的に向上",
            rarity=ItemRarity.RARE
        )
    
    def handle_event(self, event: pygame.event.Event) -> bool:
        if event.type == pygame.MOUSEMOTION:
            self.hovered_reward = -1
            mouse_pos = pygame.mouse.get_pos()
            for i, rect in enumerate(self.reward_rects):
                if rect.collidepoint(mouse_pos):
                    self.hovered_reward = i
                    break
        
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left click
                mouse_pos = pygame.mouse.get_pos()
                for i, rect in enumerate(self.reward_rects):
                    if rect.collidepoint(mouse_pos) and not self.selected_rewards[i]:
                        self._select_reward(i)
                        return True
        
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE or event.key == pygame.K_RETURN:
                # 全ての選択された報酬を確定して次に進む
                self._finalize_rewards()
                return True
            elif event.key == pygame.K_ESCAPE:
                # 報酬をスキップしてマップに戻る
                self.engine.change_state(GameState.DUNGEON_MAP)
                return True
        
        return False
    
    def _select_reward(self, index: int):
        """報酬を選択"""
        if index < len(self.rewards):
            reward = self.rewards[index]
            self.selected_rewards[index] = True
            
            # 報酬を実際に適用
            self._apply_reward(reward)
    
    def _apply_reward(self, reward: Reward):
        """報酬をプレイヤーに適用"""
        if reward.reward_type == RewardType.GOLD:
            self.engine.player.gain_gold(reward.value)
        
        elif reward.reward_type == RewardType.POTION or reward.reward_type == RewardType.ARTIFACT:
            # アイテムをインベントリに追加
            item = create_item(reward.value)
            if item:
                success = self.engine.player.inventory.add_item(item)
                if not success:
                    # インベントリ満杯の場合の処理
                    pass
        
        elif reward.reward_type == RewardType.HP_UPGRADE:
            self.engine.player.level_up_skill("max_hp", reward.value)
            self.engine.player.heal(reward.value)  # 即座に回復も
        
        elif reward.reward_type == RewardType.ENERGY_UPGRADE:
            # エネルギーシステムは削除済み - 何もしない
            pass
            
        elif reward.reward_type == RewardType.SPECIAL_PUYO_BOOST:
            # 特殊ぷよ出現率を永続的に増加
            from special_puyo.special_puyo import special_puyo_manager
            boost_multiplier = 1.0 + (reward.value / 100.0)  # パーセントを倍率に変換
            special_puyo_manager.spawn_chance = min(0.5, special_puyo_manager.spawn_chance * boost_multiplier)
            print(f"特殊ぷよ出現率が{reward.value}%アップ！現在の出現率: {special_puyo_manager.spawn_chance:.1%}")
            
        elif reward.reward_type == RewardType.CHAIN_UPGRADE:
            # 連鎖ダメージ倍率を上昇
            self.engine.player.chain_damage_multiplier += reward.value / 100.0
            print(f"連鎖ダメージが{reward.value}%アップ！現在の倍率: {self.engine.player.chain_damage_multiplier:.1f}x")
    
    def _finalize_rewards(self):
        """報酬選択を確定してマップに戻る"""
        # 選択されていない報酬は無視
        self.engine.change_state(GameState.DUNGEON_MAP)
    
    def update(self, dt: float):
        pass
    
    def render(self, screen: pygame.Surface):
        screen.fill(Colors.DARK_BLUE)
        
        # タイトル
        title_text = "戦闘勝利！"
        if self.enemy_type == "elite":
            title_text = "エリート撃破！"
        elif self.enemy_type == "boss":
            title_text = "ボス撃破！"
        
        title_surface = self.font_large.render(title_text, True, Colors.GOLD)
        title_rect = title_surface.get_rect(center=(screen.get_width() // 2, 80))
        screen.blit(title_surface, title_rect)
        
        # 報酬選択説明
        instruction_text = "報酬をクリックして獲得 (SPACEで完了)"
        instruction_surface = self.font_small.render(instruction_text, True, Colors.WHITE)
        instruction_rect = instruction_surface.get_rect(center=(screen.get_width() // 2, 120))
        screen.blit(instruction_surface, instruction_rect)
        
        # 報酬カード
        self._render_reward_cards(screen)
        
        # プレイヤー情報
        self._render_player_info(screen)
    
    def _render_reward_cards(self, screen: pygame.Surface):
        """報酬カードを描画"""
        self.reward_rects.clear()
        
        card_width = 180
        card_height = 220
        spacing = 20
        total_width = len(self.rewards) * card_width + (len(self.rewards) - 1) * spacing
        start_x = (screen.get_width() - total_width) // 2
        start_y = 200
        
        for i, reward in enumerate(self.rewards):
            x = start_x + i * (card_width + spacing)
            y = start_y
            
            card_rect = pygame.Rect(x, y, card_width, card_height)
            self.reward_rects.append(card_rect)
            
            # カードの背景
            if self.selected_rewards[i]:
                # 選択済み
                pygame.draw.rect(screen, Colors.GREEN, card_rect)
                pygame.draw.rect(screen, Colors.WHITE, card_rect, 3)
            elif i == self.hovered_reward:
                # ホバー中
                pygame.draw.rect(screen, Colors.DARK_GRAY, card_rect)
                pygame.draw.rect(screen, reward.get_color(), card_rect, 3)
            else:
                # 通常
                pygame.draw.rect(screen, Colors.BLACK, card_rect)
                pygame.draw.rect(screen, reward.get_color(), card_rect, 2)
            
            # レアリティ表示
            rarity_color = reward.rarity.color
            rarity_rect = pygame.Rect(x + 5, y + 5, card_width - 10, 20)
            pygame.draw.rect(screen, rarity_color, rarity_rect)
            
            # 報酬名
            name_text = self.font_medium.render(reward.name, True, Colors.WHITE)
            name_rect = name_text.get_rect(center=(x + card_width // 2, y + 50))
            screen.blit(name_text, name_rect)
            
            # 報酬説明
            desc_lines = reward.get_display_text()[1:]  # 名前を除く
            y_offset = y + 80
            for line in desc_lines:
                desc_text = self.font_small.render(line, True, Colors.LIGHT_GRAY)
                desc_rect = desc_text.get_rect(center=(x + card_width // 2, y_offset))
                screen.blit(desc_text, desc_rect)
                y_offset += 25
            
            # 選択状態表示
            if self.selected_rewards[i]:
                check_text = self.font_medium.render("✓", True, Colors.WHITE)
                check_rect = check_text.get_rect(center=(x + card_width // 2, y + card_height - 30))
                screen.blit(check_text, check_rect)
    
    def _render_player_info(self, screen: pygame.Surface):
        """プレイヤー情報を表示"""
        info_y = screen.get_height() - 80
        
        # HP
        hp_text = f"HP: {self.engine.player.hp}/{self.engine.player.max_hp}"
        hp_surface = self.font_small.render(hp_text, True, Colors.RED)
        screen.blit(hp_surface, (20, info_y))
        
        # ゴールド
        gold_text = f"ゴールド: {self.engine.player.gold}"
        gold_surface = self.font_small.render(gold_text, True, Colors.GOLD)
        screen.blit(gold_surface, (200, info_y))
        
        # フロア
        floor_text = f"フロア: {self.engine.player.current_floor}"
        floor_surface = self.font_small.render(floor_text, True, Colors.WHITE)
        screen.blit(floor_surface, (380, info_y))
        
        # 操作説明
        controls_text = "ESC: スキップ  SPACE: 完了"
        controls_surface = self.font_small.render(controls_text, True, Colors.LIGHT_GRAY)
        controls_rect = controls_surface.get_rect(center=(screen.get_width() // 2, info_y + 30))
        screen.blit(controls_surface, controls_rect)