"""
休憩所ハンドラー - HP回復とプレイヤー強化システム
Drop Puzzle × Roguelike の休憩所画面管理
"""

import pygame
import logging
from typing import Dict, List, Optional
from enum import Enum

from core.constants import *
from core.game_engine import GameEngine

logger = logging.getLogger(__name__)


class RestAction(Enum):
    """休憩所で選択可能なアクション"""
    HEAL = "heal"           # HP回復
    UPGRADE = "upgrade"     # 能力強化
    MEDITATE = "meditate"   # 瞑想（特殊効果）


class RestHandler:
    """休憩所画面の管理クラス"""
    
    def __init__(self, engine: GameEngine, current_node=None):
        self.engine = engine
        self.current_node = current_node
        
        # 休憩所の状態
        self.selected_action = None
        self.action_completed = False
        self.heal_amount = 0
        
        # UI設定
        self.background_color = (40, 25, 15)  # 温かい茶色
        self.card_width = 200
        self.card_height = 280
        self.card_spacing = 50
        
        # 利用可能なアクション
        self.available_actions = self._generate_available_actions()
        
        # レイアウト計算
        self.start_x = (SCREEN_WIDTH - (len(self.available_actions) * self.card_width + 
                       (len(self.available_actions) - 1) * self.card_spacing)) // 2
        self.start_y = 200
        
        self.selected_index = 0
        
        logger.info(f"RestHandler initialized with {len(self.available_actions)} actions")
    
    def _generate_available_actions(self) -> List[Dict]:
        """利用可能なアクションを生成"""
        actions = []
        
        # HP回復は常に利用可能（満タンでない場合）
        if self.engine.player.hp < self.engine.player.max_hp:
            heal_amount = min(
                self.engine.player.max_hp - self.engine.player.hp,
                self.engine.player.max_hp // 3  # 最大HPの1/3回復
            )
            actions.append({
                'type': RestAction.HEAL,
                'name': 'Rest and Heal',
                'description': f'Recover {heal_amount} HP',
                'icon': '♨',
                'color': (50, 200, 50),
                'heal_amount': heal_amount
            })
        
        # 能力強化（プレイヤーレベルに応じて）
        actions.append({
            'type': RestAction.UPGRADE,
            'name': 'Train Skills',
            'description': 'Increase max HP by 5\\nand chain damage by 10%',
            'icon': '⚡',
            'color': (200, 150, 50),
            'hp_bonus': 5,
            'damage_bonus': 10
        })
        
        # 瞑想（特殊効果）
        actions.append({
            'type': RestAction.MEDITATE,
            'name': 'Meditate',
            'description': 'Gain energy boost\\nfor next 3 battles',
            'icon': '🧘',
            'color': (100, 100, 255),
            'energy_boost': 3
        })
        
        return actions
    
    def on_enter(self, previous_state):
        """休憩所画面開始"""
        logger.info("Entering rest area")
        self.selected_action = None
        self.action_completed = False
        self.selected_index = 0
    
    def handle_event(self, event: pygame.event.Event):
        """イベント処理"""
        if self.action_completed:
            # アクション完了後はマップに戻る
            if event.type == pygame.KEYDOWN and (event.key == pygame.K_RETURN or event.key == pygame.K_ESCAPE):
                self._return_to_map()
            return
        
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:
                self.selected_index = (self.selected_index - 1) % len(self.available_actions)
            elif event.key == pygame.K_RIGHT:
                self.selected_index = (self.selected_index + 1) % len(self.available_actions)
            elif event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                self._execute_action()
            elif event.key == pygame.K_ESCAPE:
                # 何もせずに戻る
                self._return_to_map()
    
    def _execute_action(self):
        """選択されたアクションを実行"""
        if 0 <= self.selected_index < len(self.available_actions):
            action = self.available_actions[self.selected_index]
            action_type = action['type']
            
            if action_type == RestAction.HEAL:
                self._execute_heal(action)
            elif action_type == RestAction.UPGRADE:
                self._execute_upgrade(action)
            elif action_type == RestAction.MEDITATE:
                self._execute_meditate(action)
            
            self.selected_action = action
            self.action_completed = True
            logger.info(f"Executed rest action: {action_type.value}")
    
    def _execute_heal(self, action):
        """HP回復を実行"""
        heal_amount = action['heal_amount']
        old_hp = self.engine.player.hp
        self.engine.player.hp = min(
            self.engine.player.max_hp,
            self.engine.player.hp + heal_amount
        )
        self.heal_amount = self.engine.player.hp - old_hp
        logger.info(f"Healed {self.heal_amount} HP: {old_hp} -> {self.engine.player.hp}")
    
    def _execute_upgrade(self, action):
        """能力強化を実行"""
        hp_bonus = action['hp_bonus']
        damage_bonus = action['damage_bonus']
        
        # 最大HP増加
        self.engine.player.max_hp += hp_bonus
        self.engine.player.hp += hp_bonus  # 現在HPも同じ分増加
        
        # ダメージボーナス（プレイヤーデータに追加）
        if not hasattr(self.engine.player, 'chain_damage_bonus'):
            self.engine.player.chain_damage_bonus = 0
        self.engine.player.chain_damage_bonus += damage_bonus
        
        logger.info(f"Upgraded: +{hp_bonus} max HP, +{damage_bonus}% chain damage")
    
    def _execute_meditate(self, action):
        """瞑想を実行"""
        energy_boost = action['energy_boost']
        
        # エネルギーブースト効果（プレイヤーデータに追加）
        if not hasattr(self.engine.player, 'energy_boost_remaining'):
            self.engine.player.energy_boost_remaining = 0
        self.engine.player.energy_boost_remaining += energy_boost
        
        logger.info(f"Meditated: +{energy_boost} energy boost for next battles")
    
    def _return_to_map(self):
        """ダンジョンマップに戻る"""
        try:
            from dungeon.map_handler import DungeonMapHandler
            
            # マップ進行処理
            if (hasattr(self.engine, 'persistent_dungeon_map') and self.engine.persistent_dungeon_map and 
                self.current_node):
                
                dungeon_map = self.engine.persistent_dungeon_map
                
                logger.info(f"Processing map progression after rest for node: {self.current_node.node_id}")
                
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
            
            logger.info("Returned to dungeon map after rest")
            
        except Exception as e:
            logger.error(f"Failed to return to dungeon map: {e}")
            # フォールバック: メニューに戻る
            self.engine.change_state(GameState.MENU)
    
    def render(self, surface: pygame.Surface):
        """描画処理"""
        # 背景
        surface.fill(self.background_color)
        
        # 温かい光の効果
        self._render_ambient_light(surface)
        
        # タイトル
        self._render_title(surface)
        
        # アクションカード
        if not self.action_completed:
            self._render_action_cards(surface)
        else:
            self._render_action_result(surface)
        
        # 操作説明
        self._render_instructions(surface)
    
    def _render_ambient_light(self, surface: pygame.Surface):
        """温かい光の効果を描画"""
        # 中央から放射状の光
        center_x = SCREEN_WIDTH // 2
        center_y = SCREEN_HEIGHT // 2 - 50
        
        for i in range(5):
            radius = 150 + i * 50
            alpha = 30 - i * 5
            if alpha > 0:
                light_surface = pygame.Surface((radius * 2, radius * 2))
                light_surface.set_alpha(alpha)
                light_surface.fill((0, 0, 0))
                light_surface.set_colorkey((0, 0, 0))
                pygame.draw.circle(light_surface, (255, 200, 100), (radius, radius), radius)
                surface.blit(light_surface, (center_x - radius, center_y - radius))
    
    def _render_title(self, surface: pygame.Surface):
        """タイトルを描画"""
        font_title = self.engine.fonts['title']
        title_text = font_title.render("♨ REST AREA ♨", True, Colors.WHITE)
        title_rect = title_text.get_rect(center=(SCREEN_WIDTH // 2, 80))
        surface.blit(title_text, title_rect)
        
        # サブタイトル
        font_medium = self.engine.fonts['medium']
        subtitle_text = font_medium.render("Choose how to spend your time...", True, Colors.LIGHT_GRAY)
        subtitle_rect = subtitle_text.get_rect(center=(SCREEN_WIDTH // 2, 120))
        surface.blit(subtitle_text, subtitle_rect)
    
    def _render_action_cards(self, surface: pygame.Surface):
        """アクションカードを描画"""
        font_large = self.engine.fonts['large']
        font_medium = self.engine.fonts['medium']
        font_small = self.engine.fonts['small']
        
        for i, action in enumerate(self.available_actions):
            x = self.start_x + i * (self.card_width + self.card_spacing)
            y = self.start_y
            
            # カード背景
            card_rect = pygame.Rect(x, y, self.card_width, self.card_height)
            
            # 選択中のカードはハイライト
            if i == self.selected_index:
                pygame.draw.rect(surface, Colors.YELLOW, card_rect, 4)
                bg_color = (60, 45, 35)  # より明るい茶色
            else:
                bg_color = (30, 20, 10)  # 暗い茶色
            
            pygame.draw.rect(surface, bg_color, card_rect)
            pygame.draw.rect(surface, action['color'], card_rect, 2)
            
            # アイコン
            icon_text = font_large.render(action['icon'], True, action['color'])
            icon_rect = icon_text.get_rect(center=(x + self.card_width // 2, y + 60))
            surface.blit(icon_text, icon_rect)
            
            # アクション名
            name_text = font_medium.render(action['name'], True, Colors.WHITE)
            name_rect = name_text.get_rect(center=(x + self.card_width // 2, y + 120))
            surface.blit(name_text, name_rect)
            
            # 説明文
            desc_lines = action['description'].split('\\n')
            for j, line in enumerate(desc_lines):
                desc_text = font_small.render(line, True, Colors.LIGHT_GRAY)
                desc_rect = desc_text.get_rect(center=(x + self.card_width // 2, y + 160 + j * 20))
                surface.blit(desc_text, desc_rect)
    
    def _render_action_result(self, surface: pygame.Surface):
        """アクション実行結果を描画"""
        font_large = self.engine.fonts['large']
        font_medium = self.engine.fonts['medium']
        
        if not self.selected_action:
            return
        
        action = self.selected_action
        
        # 結果メッセージ
        if action['type'] == RestAction.HEAL:
            result_text = f"Recovered {self.heal_amount} HP!"
            result_color = Colors.GREEN
        elif action['type'] == RestAction.UPGRADE:
            result_text = "Skills Enhanced!"
            result_color = Colors.YELLOW
        elif action['type'] == RestAction.MEDITATE:
            result_text = "Mind Focused!"
            result_color = Colors.CYAN
        else:
            result_text = "Action Completed!"
            result_color = Colors.WHITE
        
        # 大きなアイコン
        icon_text = font_large.render(action['icon'], True, result_color)
        icon_rect = icon_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50))
        surface.blit(icon_text, icon_rect)
        
        # 結果テキスト
        result = font_large.render(result_text, True, result_color)
        result_rect = result.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 20))
        surface.blit(result, result_rect)
        
        # 詳細情報
        if action['type'] == RestAction.UPGRADE:
            detail_text = f"Max HP: {self.engine.player.max_hp} (+{action['hp_bonus']})"
            detail = font_medium.render(detail_text, True, Colors.WHITE)
            detail_rect = detail.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 60))
            surface.blit(detail, detail_rect)
    
    def _render_instructions(self, surface: pygame.Surface):
        """操作説明を描画"""
        font_small = self.engine.fonts['small']
        
        if not self.action_completed:
            instructions = [
                "← → - Select action",
                "Enter/Space - Confirm",
                "ESC - Leave without resting"
            ]
        else:
            instructions = [
                "Enter/ESC - Return to map"
            ]
        
        for i, instruction in enumerate(instructions):
            text = font_small.render(instruction, True, Colors.LIGHT_GRAY)
            text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 80 + i * 20))
            surface.blit(text, text_rect)
    
    def update(self, dt: float):
        """更新処理"""
        pass