"""
勝利画面システム
ゲームクリア時の祝福画面と最終統計表示
"""

import pygame
from typing import Dict, List
from core.state_handler import StateHandler
from core.constants import GameState, Colors
from core.game_engine import GameEngine

class VictoryHandler(StateHandler):
    def __init__(self, engine: GameEngine, victory_type: str = "ダンジョン制覇"):
        super().__init__(engine)
        self.victory_type = victory_type
        # フォント初期化（初期化されていない場合）
        if not pygame.font.get_init():
            pygame.font.init()
            
        self.font_huge = pygame.font.Font(None, 96)
        self.font_large = pygame.font.Font(None, 64)
        self.font_medium = pygame.font.Font(None, 48)
        self.font_small = pygame.font.Font(None, 32)
        self.font_tiny = pygame.font.Font(None, 24)
        
        self.stats = self._collect_victory_stats()
        self.achievements = self._calculate_achievements()
        self.button_rects = {}
        self.hovered_button = None
        
        # アニメーション効果
        self.animation_time = 0.0
        self.particle_effects = []
        self._generate_victory_particles()
    
    def _collect_victory_stats(self) -> Dict[str, str]:
        """勝利統計を収集"""
        player = self.engine.player
        
        return {
            "制覇フロア": f"{player.current_floor}",
            "総戦闘数": f"{player.stats.total_battles}",
            "勝率": f"{player.stats.get_win_rate():.1f}%",
            "総ダメージ": f"{player.stats.total_damage_dealt:,}",
            "最高連鎖": f"{player.stats.highest_chain}",
            "獲得ゴールド": f"{player.stats.total_gold_earned:,}",
            "最終ゴールド": f"{player.gold:,}",
            "最終HP": f"{player.hp}/{player.max_hp}",
            "エネルギー": f"{player.energy}",
            "連鎖倍率": f"{player.chain_damage_multiplier:.1f}x",
            "エリート撃破": f"{player.stats.elite_battles}",
            "ボス撃破": f"{player.stats.boss_battles}",
            "イベント参加": f"{player.stats.events_encountered}",
            "所持アイテム": f"{len(player.inventory.items)}",
            "プレイタイム": self._calculate_playtime()
        }
    
    def _calculate_playtime(self) -> str:
        """プレイ時間を計算（簡易版）"""
        # 実際の実装では開始時刻からの経過時間を計算
        return "データなし"
    
    def _calculate_achievements(self) -> List[str]:
        """実績を計算"""
        achievements = []
        player = self.engine.player
        
        # 基本実績
        achievements.append("ダンジョン制覇")
        
        # 戦闘実績
        if player.stats.get_win_rate() >= 90.0:
            achievements.append("戦闘マスター (勝率90%以上)")
        
        if player.stats.highest_chain >= 10:
            achievements.append("連鎖の達人 (最高連鎖10以上)")
        
        if player.chain_damage_multiplier >= 2.0:
            achievements.append("破壊者 (連鎖倍率2.0x以上)")
        
        # 探索実績
        if player.stats.elite_battles >= 5:
            achievements.append("エリートハンター")
        
        if player.stats.events_encountered >= 10:
            achievements.append("冒険者 (イベント10回以上)")
        
        # 経済実績
        if player.gold >= 500:
            achievements.append("富豪 (500ゴールド以上)")
        
        if player.stats.total_gold_earned >= 2000:
            achievements.append("商売人 (総獲得2000ゴールド以上)")
        
        # コレクション実績
        if len(player.inventory.items) >= 15:
            achievements.append("コレクター (15アイテム以上)")
        
        # 特殊実績
        if player.hp == player.max_hp:
            achievements.append("完璧主義者 (フルHP制覇)")
        
        if player.stats.battles_lost == 0:
            achievements.append("無敗の英雄 (一度も敗北せず)")
        
        return achievements
    
    def _generate_victory_particles(self):
        """勝利パーティクルを生成"""
        import random
        
        for _ in range(50):
            particle = {
                'x': random.randint(0, 1200),
                'y': random.randint(600, 800),
                'vx': random.uniform(-2, 2),
                'vy': random.uniform(-5, -2),
                'size': random.randint(3, 8),
                'color': random.choice([Colors.GOLD, Colors.YELLOW, Colors.WHITE, Colors.ORANGE]),
                'life': random.uniform(3.0, 6.0),
                'max_life': random.uniform(3.0, 6.0)
            }
            self.particle_effects.append(particle)
    
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
            if event.key == pygame.K_n:
                # 新しいゲーム
                self._new_game()
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
        if button_name == "new_game":
            self._new_game()
        elif button_name == "menu":
            self._return_to_menu()
        elif button_name == "quit":
            self._quit_game()
    
    def _new_game(self):
        """新しいゲームを開始"""
        # プレイヤーデータをリセット
        from core.player_data import PlayerData
        self.engine.player = PlayerData()
        
        # ゲームデータをリセット
        from core.game_engine import GameData
        self.engine.game_data = GameData()
        
        # ダンジョンマップをリセット
        self.engine.persistent_dungeon_map = None
        
        # ダンジョンマップ画面に遷移
        self.engine.change_state(GameState.DUNGEON_MAP)
    
    def _return_to_menu(self):
        """メインメニューに戻る"""
        # プレイヤーデータをリセット
        from core.player_data import PlayerData
        self.engine.player = PlayerData()
        
        # ゲームデータをリセット
        from core.game_engine import GameData
        self.engine.game_data = GameData()
        
        # ダンジョンマップをリセット
        self.engine.persistent_dungeon_map = None
        
        # メニューに遷移
        self.engine.change_state(GameState.MENU)
    
    def _quit_game(self):
        """ゲームを終了"""
        self.engine.running = False
    
    def update(self, dt: float):
        self.animation_time += dt
        
        # パーティクル更新
        for particle in self.particle_effects[:]:
            particle['x'] += particle['vx']
            particle['y'] += particle['vy']
            particle['vy'] += 0.1  # 重力
            particle['life'] -= dt
            
            if particle['life'] <= 0:
                self.particle_effects.remove(particle)
        
        # パーティクル補充
        if len(self.particle_effects) < 30:
            import random
            for _ in range(5):
                particle = {
                    'x': random.randint(0, 1200),
                    'y': 800,
                    'vx': random.uniform(-2, 2),
                    'vy': random.uniform(-5, -2),
                    'size': random.randint(3, 8),
                    'color': random.choice([Colors.GOLD, Colors.YELLOW, Colors.WHITE]),
                    'life': random.uniform(3.0, 6.0),
                    'max_life': random.uniform(3.0, 6.0)
                }
                self.particle_effects.append(particle)
    
    def render(self, screen: pygame.Surface):
        # グラデーション背景
        self._render_gradient_background(screen)
        
        # パーティクル効果
        self._render_particles(screen)
        
        # 勝利タイトル
        self._render_victory_title(screen)
        
        # 実績
        self._render_achievements(screen)
        
        # 統計情報
        self._render_statistics(screen)
        
        # ボタン
        self._render_buttons(screen)
        
        # 操作説明
        self._render_controls(screen)
    
    def _render_gradient_background(self, screen: pygame.Surface):
        """グラデーション背景"""
        for y in range(screen.get_height()):
            ratio = y / screen.get_height()
            # 深い青から紫のグラデーション
            r = int(25 + ratio * 50)
            g = int(25 + ratio * 25)
            b = int(75 + ratio * 100)
            color = (r, g, b)
            pygame.draw.line(screen, color, (0, y), (screen.get_width(), y))
    
    def _render_particles(self, screen: pygame.Surface):
        """パーティクル効果"""
        for particle in self.particle_effects:
            alpha = int(255 * (particle['life'] / particle['max_life']))
            if alpha > 0:
                # パーティクルサーフェスを作成
                particle_surf = pygame.Surface((particle['size'] * 2, particle['size'] * 2))
                particle_surf.set_alpha(alpha)
                particle_surf.fill(particle['color'])
                
                # 円形に描画
                pygame.draw.circle(particle_surf, particle['color'], 
                                 (particle['size'], particle['size']), particle['size'])
                
                screen.blit(particle_surf, (int(particle['x']), int(particle['y'])))
    
    def _render_victory_title(self, screen: pygame.Surface):
        """勝利タイトル"""
        # メインタイトル（アニメーション付き）
        scale = 1.0 + 0.1 * abs(pygame.math.Vector2(0, 1).rotate(self.animation_time * 180).y)
        
        title_text = "VICTORY!"
        title_surface = self.font_huge.render(title_text, True, Colors.GOLD)
        
        # スケール適用
        scaled_size = (int(title_surface.get_width() * scale), 
                      int(title_surface.get_height() * scale))
        scaled_surface = pygame.transform.scale(title_surface, scaled_size)
        
        title_rect = scaled_surface.get_rect(center=(screen.get_width() // 2, 100))
        
        # 光る効果（複数回描画）
        for offset in [(2, 2), (-2, -2), (2, -2), (-2, 2)]:
            shadow_rect = title_rect.copy()
            shadow_rect.center = (title_rect.centerx + offset[0], title_rect.centery + offset[1])
            shadow_surface = self.font_huge.render(title_text, True, Colors.YELLOW)
            shadow_surface = pygame.transform.scale(shadow_surface, scaled_size)
            shadow_surface.set_alpha(100)
            screen.blit(shadow_surface, shadow_rect)
        
        screen.blit(scaled_surface, title_rect)
        
        # サブタイトル
        subtitle_surface = self.font_medium.render(self.victory_type, True, Colors.WHITE)
        subtitle_rect = subtitle_surface.get_rect(center=(screen.get_width() // 2, 160))
        screen.blit(subtitle_surface, subtitle_rect)
    
    def _render_achievements(self, screen: pygame.Surface):
        """実績表示"""
        achievements_title = self.font_medium.render("実績", True, Colors.GOLD)
        achievements_rect = achievements_title.get_rect(center=(screen.get_width() // 4, 220))
        screen.blit(achievements_title, achievements_rect)
        
        y_offset = 260
        for achievement in self.achievements:
            achievement_surface = self.font_small.render(achievement, True, Colors.WHITE)
            achievement_rect = achievement_surface.get_rect(centerx=screen.get_width() // 4, y=y_offset)
            screen.blit(achievement_surface, achievement_rect)
            y_offset += 35
    
    def _render_statistics(self, screen: pygame.Surface):
        """統計情報表示"""
        stats_title = self.font_medium.render("📊 最終記録", True, Colors.GOLD)
        stats_rect = stats_title.get_rect(center=(3 * screen.get_width() // 4, 220))
        screen.blit(stats_title, stats_rect)
        
        y_offset = 260
        for stat_name, stat_value in self.stats.items():
            # 統計名
            name_surface = self.font_small.render(f"{stat_name}:", True, Colors.LIGHT_GRAY)
            name_rect = name_surface.get_rect(centerx=3 * screen.get_width() // 4 - 60, y=y_offset)
            screen.blit(name_surface, name_rect)
            
            # 統計値
            value_surface = self.font_small.render(stat_value, True, Colors.WHITE)
            value_rect = value_surface.get_rect(centerx=3 * screen.get_width() // 4 + 60, y=y_offset)
            screen.blit(value_surface, value_rect)
            
            y_offset += 30
    
    def _render_buttons(self, screen: pygame.Surface):
        """ボタン描画"""
        self.button_rects.clear()
        
        button_width = 200
        button_height = 50
        button_spacing = 20
        buttons = [
            ("new_game", "新しいゲーム", Colors.GREEN),
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
            
            # ボタンの色（ホバー効果）
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
            "N: 新しいゲーム",
            "M: メインメニュー", 
            "Q: ゲーム終了"
        ]
        
        y_offset = screen.get_height() - 50
        for control in controls:
            control_text = self.font_tiny.render(control, True, Colors.LIGHT_GRAY)
            control_rect = control_text.get_rect(center=(screen.get_width() // 2, y_offset))
            screen.blit(control_text, control_rect)
            y_offset += 20