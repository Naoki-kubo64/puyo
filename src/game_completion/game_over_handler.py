"""
ゲームオーバー画面システム
プレイヤーの死亡時に表示される詳細統計とリスタート機能
"""

import pygame
from typing import Dict
from ..core.state_handler import StateHandler
from ..core.constants import GameState, Colors
from ..core.game_engine import GameEngine

class GameOverHandler(StateHandler):
    def __init__(self, engine: GameEngine, death_cause: str = "戦闘で力尽きた"):
        super().__init__(engine)
        self.death_cause = death_cause
        self.font_large = pygame.font.Font(None, 72)
        self.font_medium = pygame.font.Font(None, 48)
        self.font_small = pygame.font.Font(None, 32)
        self.font_tiny = pygame.font.Font(None, 24)
        
        self.stats = self._collect_final_stats()
        self.button_rects = {}
        self.hovered_button = None
        
        # フェードイン効果
        self.fade_alpha = 0
        self.fade_speed = 2
    
    def _collect_final_stats(self) -> Dict[str, str]:
        """最終統計情報を収集"""
        player = self.engine.player
        
        return {
            "到達フロア": f"{player.current_floor}",
            "総戦闘数": f"{player.stats.total_battles}",
            "勝利数": f"{player.stats.battles_won}",
            "敗北数": f"{player.stats.battles_lost}",
            "勝率": f"{player.stats.get_win_rate():.1f}%",
            "総ダメージ": f"{player.stats.total_damage_dealt:,}",
            "総連鎖数": f"{player.stats.total_chains_made}",
            "最高連鎖": f"{player.stats.highest_chain}",
            "平均連鎖": f"{player.stats.get_average_chain():.1f}",
            "獲得ゴールド": f"{player.stats.total_gold_earned:,}",
            "消費ゴールド": f"{player.stats.total_gold_spent:,}",
            "訪問部屋数": f"{player.stats.rooms_visited}",
            "エリート戦": f"{player.stats.elite_battles}",
            "ボス戦": f"{player.stats.boss_battles}",
            "イベント": f"{player.stats.events_encountered}",
            "休憩回数": f"{player.stats.rest_sites_used}",
            "宝箱発見": f"{player.stats.treasures_found}",
            "アイテム購入": f"{player.stats.items_purchased}",
            "所持アイテム": f"{len(player.inventory.items)}",
            "インベントリ価値": f"{player.inventory.get_total_value():,}G"
        }
    
    def handle_event(self, event: pygame.event.Event) -> bool:
        if event.type == pygame.MOUSEMOTION:
            self.hovered_button = None
            mouse_pos = pygame.mouse.get_pos()
            for button_name, rect in self.button_rects.items():
                if rect.collidepoint(mouse_pos):
                    self.hovered_button = button_name
                    break
        
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left click
                mouse_pos = pygame.mouse.get_pos()
                for button_name, rect in self.button_rects.items():
                    if rect.collidepoint(mouse_pos):
                        self._handle_button_click(button_name)
                        return True
        
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_r:
                # リスタート
                self._restart_game()
                return True
            elif event.key == pygame.K_m or event.key == pygame.K_ESCAPE:
                # メニューに戻る
                self._return_to_menu()
                return True
            elif event.key == pygame.K_q:
                # ゲーム終了
                self._quit_game()
                return True
        
        return False
    
    def _handle_button_click(self, button_name: str):
        """ボタンクリック処理"""
        if button_name == "restart":
            self._restart_game()
        elif button_name == "menu":
            self._return_to_menu()
        elif button_name == "quit":
            self._quit_game()
    
    def _restart_game(self):
        """ゲームを再開"""
        # プレイヤーデータをリセット
        from ..core.player_data import PlayerData
        self.engine.player = PlayerData()
        
        # ゲームデータをリセット
        from ..core.game_engine import GameData
        self.engine.game_data = GameData()
        
        # ダンジョンマップをリセット
        self.engine.persistent_dungeon_map = None
        
        # ダンジョンマップ画面に遷移
        self.engine.change_state(GameState.DUNGEON_MAP)
    
    def _return_to_menu(self):
        """メインメニューに戻る"""
        # プレイヤーデータをリセット
        from ..core.player_data import PlayerData
        self.engine.player = PlayerData()
        
        # ゲームデータをリセット
        from ..core.game_engine import GameData
        self.engine.game_data = GameData()
        
        # ダンジョンマップをリセット
        self.engine.persistent_dungeon_map = None
        
        # メニューに遷移
        self.engine.change_state(GameState.MENU)
    
    def _quit_game(self):
        """ゲームを終了"""
        self.engine.running = False
    
    def update(self, dt: float):
        # フェードイン効果
        if self.fade_alpha < 255:
            self.fade_alpha = min(255, self.fade_alpha + self.fade_speed * dt * 60)
    
    def render(self, screen: pygame.Surface):
        # 暗い背景
        screen.fill(Colors.BLACK)
        
        # フェードインオーバーレイ
        if self.fade_alpha < 255:
            fade_surface = pygame.Surface(screen.get_size())
            fade_surface.fill(Colors.BLACK)
            fade_surface.set_alpha(255 - self.fade_alpha)
            screen.blit(fade_surface, (0, 0))
        
        # ゲームオーバータイトル
        self._render_title(screen)
        
        # 死因
        self._render_death_cause(screen)
        
        # 統計情報
        self._render_statistics(screen)
        
        # ボタン
        self._render_buttons(screen)
        
        # 操作説明
        self._render_controls(screen)
    
    def _render_title(self, screen: pygame.Surface):
        """ゲームオーバータイトル"""
        title_text = self.font_large.render("GAME OVER", True, Colors.RED)
        title_rect = title_text.get_rect(center=(screen.get_width() // 2, 80))
        screen.blit(title_text, title_rect)
        
        # 影効果
        shadow_text = self.font_large.render("GAME OVER", True, Colors.DARK_RED)
        shadow_rect = shadow_text.get_rect(center=(screen.get_width() // 2 + 3, 83))
        screen.blit(shadow_text, shadow_rect)
        screen.blit(title_text, title_rect)  # 再描画で前面に
    
    def _render_death_cause(self, screen: pygame.Surface):
        """死因の表示"""
        cause_text = self.font_medium.render(self.death_cause, True, Colors.WHITE)
        cause_rect = cause_text.get_rect(center=(screen.get_width() // 2, 140))
        screen.blit(cause_text, cause_rect)
    
    def _render_statistics(self, screen: pygame.Surface):
        """統計情報の表示"""
        # 統計セクションタイトル
        stats_title = self.font_medium.render("冒険の記録", True, Colors.GOLD)
        stats_title_rect = stats_title.get_rect(center=(screen.get_width() // 2, 200))
        screen.blit(stats_title, stats_title_rect)
        
        # 統計を複数列で表示
        col1_stats = list(self.stats.items())[:10]  # 最初の10項目
        col2_stats = list(self.stats.items())[10:]   # 残りの項目
        
        # 左列
        self._render_stats_column(screen, col1_stats, screen.get_width() // 4, 250)
        
        # 右列
        self._render_stats_column(screen, col2_stats, 3 * screen.get_width() // 4, 250)
    
    def _render_stats_column(self, screen: pygame.Surface, stats: list, center_x: int, start_y: int):
        """統計の列を描画"""
        y_offset = start_y
        
        for stat_name, stat_value in stats:
            # 統計名
            name_text = self.font_small.render(f"{stat_name}:", True, Colors.LIGHT_GRAY)
            name_rect = name_text.get_rect(centerx=center_x - 50, y=y_offset)
            screen.blit(name_text, name_rect)
            
            # 統計値
            value_text = self.font_small.render(stat_value, True, Colors.WHITE)
            value_rect = value_text.get_rect(centerx=center_x + 50, y=y_offset)
            screen.blit(value_text, value_rect)
            
            y_offset += 30
    
    def _render_buttons(self, screen: pygame.Surface):
        """ボタンの描画"""
        self.button_rects.clear()
        
        button_width = 200
        button_height = 50
        button_spacing = 20
        buttons = [
            ("restart", "もう一度挑戦", Colors.GREEN),
            ("menu", "メインメニュー", Colors.BLUE),
            ("quit", "ゲーム終了", Colors.RED)
        ]
        
        total_width = len(buttons) * button_width + (len(buttons) - 1) * button_spacing
        start_x = (screen.get_width() - total_width) // 2
        button_y = screen.get_height() - 120
        
        for i, (button_id, button_text, button_color) in enumerate(buttons):
            x = start_x + i * (button_width + button_spacing)
            button_rect = pygame.Rect(x, button_y, button_width, button_height)
            self.button_rects[button_id] = button_rect
            
            # ボタンの色
            if self.hovered_button == button_id:
                color = Colors.WHITE
                text_color = Colors.BLACK
            else:
                color = button_color
                text_color = Colors.WHITE
            
            # ボタン描画
            pygame.draw.rect(screen, color, button_rect)
            pygame.draw.rect(screen, Colors.WHITE, button_rect, 2)
            
            # ボタンテキスト
            text_surface = self.font_small.render(button_text, True, text_color)
            text_rect = text_surface.get_rect(center=button_rect.center)
            screen.blit(text_surface, text_rect)
    
    def _render_controls(self, screen: pygame.Surface):
        """操作説明"""
        controls = [
            "R: もう一度挑戦",
            "M: メインメニュー",
            "Q: ゲーム終了"
        ]
        
        y_offset = screen.get_height() - 50
        for control in controls:
            control_text = self.font_tiny.render(control, True, Colors.LIGHT_GRAY)
            control_rect = control_text.get_rect(center=(screen.get_width() // 2, y_offset))
            screen.blit(control_text, control_rect)
            y_offset += 20