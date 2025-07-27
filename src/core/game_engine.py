"""
ゲームエンジン - メインループと状態管理
Drop Puzzle × Roguelike のコアシステム
"""

import pygame
import sys
import logging
from typing import Dict, Optional
from dataclasses import dataclass, field
from enum import Enum

from .constants import *
from .sound_manager import get_sound_manager
from .player_data import PlayerData

# ログ設定
logging.basicConfig(level=LOG_LEVEL)
logger = logging.getLogger(__name__)


@dataclass
class GameData:
    """ゲーム全体のデータを管理するクラス"""
    
    # プレイヤー状態
    player_hp: int = PLAYER_INITIAL_HP
    player_max_hp: int = PLAYER_MAX_HP
    gold: int = 0
    floor: int = 1
    
    # 戦闘状態
    enemy_hp: int = 0
    enemy_max_hp: int = 0
    turn_count: int = 0
    
    # デッキ・カード状態
    deck: list = field(default_factory=list)
    hand: list = field(default_factory=list)
    
    # 統計情報
    total_score: int = 0
    battles_won: int = 0
    chains_made: int = 0
    
    def reset_battle(self):
        """戦闘開始時の初期化"""
        self.enemy_hp = ENEMY_BASE_HP + (self.floor - 1) * 10
        self.enemy_max_hp = self.enemy_hp
        self.turn_count = 0
        logger.info(f"Battle reset - Floor {self.floor}, Enemy HP: {self.enemy_hp}")
    
    def is_player_alive(self) -> bool:
        return self.player_hp > 0
    
    def is_enemy_alive(self) -> bool:
        return self.enemy_hp > 0


class GameEngine:
    """メインゲームエンジン - 状態管理とメインループを担当"""
    
    def __init__(self):
        """ゲームエンジン初期化"""
        logger.info("Initializing Game Engine...")
        
        # Pygame初期化
        pygame.init()
        pygame.mixer.init()
        
        # 画面設定
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Drop Puzzle × Roguelike")
        self.clock = pygame.time.Clock()
        
        # フォント設定
        self.fonts = self._load_fonts()
        
        # サウンドシステム初期化
        self.sound_manager = get_sound_manager()
        
        # ゲーム状態
        self.current_state = GameState.MENU
        self.running = True
        self.paused = False
        
        # ゲームデータ
        self.game_data = GameData()
        
        # プレイヤーデータ
        self.player = PlayerData()
        
        # ゲーム終了条件管理
        from ..game_completion.game_conditions import GameConditionManager
        self.condition_manager = GameConditionManager(self)
        
        # 状態管理システム
        self.state_handlers = {}
        self.state_systems = {}
        
        # 永続データ
        self.persistent_dungeon_map = None  # ダンジョンマップの状態を保持
        
        # デバッグ情報
        self.debug_mode = DEBUG_MODE
        self.show_fps = SHOW_FPS
        
        # パフォーマンス計測
        self.frame_count = 0
        self.fps_counter = 0
        
        logger.info("Game Engine initialized successfully")
    
    def _load_fonts(self) -> Dict[str, pygame.font.Font]:
        """フォントを読み込み"""
        fonts = {}
        try:
            # Windows用日本語フォント直接読み込み
            import os
            import platform
            
            japanese_font = None
            
            # Windows環境での日本語・絵文字対応フォント読み込み
            if platform.system() == "Windows":
                windows_font_paths = [
                    "C:/Windows/Fonts/seguiemj.ttf",  # 絵文字対応フォント（優先）
                    "C:/Windows/Fonts/NotoColorEmoji.ttf",  # Google絵文字フォント
                    "C:/Windows/Fonts/msgothic.ttc",
                    "C:/Windows/Fonts/msmincho.ttc", 
                    "C:/Windows/Fonts/YuGothM.ttc",
                    "C:/Windows/Fonts/meiryo.ttc",
                ]
                
                for font_path in windows_font_paths:
                    if os.path.exists(font_path):
                        try:
                            test_font = pygame.font.Font(font_path, FONT_SIZE_MEDIUM)
                            # 日本語と絵文字テスト
                            test_japanese = test_font.render("ゴブリン", True, (255, 255, 255))
                            test_emoji = test_font.render("⚔️", True, (255, 255, 255))
                            if ((test_japanese and test_japanese.get_width() > 0) or 
                                (test_emoji and test_emoji.get_width() > 0)):
                                japanese_font = test_font
                                logger.info(f"Successfully loaded font (Japanese/Emoji) from: {font_path}")
                                break
                        except Exception as e:
                            logger.debug(f"Failed to load font from {font_path}: {e}")
                            continue
            
            # システムフォントでの試行（フォールバック）
            if not japanese_font:
                japanese_font_names = [
                    'Segoe UI Emoji',     # Windows絵文字フォント
                    'Noto Color Emoji',   # Google絵文字フォント
                    'MS Gothic',
                    'MS UI Gothic', 
                    'Yu Gothic',
                    'Meiryo',
                    'msgothic',
                    'meiryo'
                ]
                
                for font_name in japanese_font_names:
                    try:
                        test_font = pygame.font.SysFont(font_name, FONT_SIZE_MEDIUM)
                        # 日本語と絵文字テスト
                        test_japanese = test_font.render("ゴブリン", True, (255, 255, 255))
                        test_emoji = test_font.render("⚔️", True, (255, 255, 255))
                        if ((test_japanese and test_japanese.get_width() > 0) or 
                            (test_emoji and test_emoji.get_width() > 0)):
                            japanese_font = test_font
                            logger.info(f"Successfully loaded system font (Japanese/Emoji): {font_name}")
                            break
                    except Exception as e:
                        logger.debug(f"Failed to load system font {font_name}: {e}")
                        continue
            
            if japanese_font:
                # 日本語フォントで全サイズ作成
                try:
                    # TTCフォントの場合、直接パスから作成
                    if hasattr(japanese_font, '_pygame_font_path'):
                        font_path = japanese_font._pygame_font_path
                        fonts['small'] = pygame.font.Font(font_path, FONT_SIZE_SMALL)
                        fonts['medium'] = pygame.font.Font(font_path, FONT_SIZE_MEDIUM) 
                        fonts['large'] = pygame.font.Font(font_path, FONT_SIZE_LARGE)
                        fonts['title'] = pygame.font.Font(font_path, FONT_SIZE_TITLE)
                        fonts['japanese'] = japanese_font
                    else:
                        # システムフォントの場合
                        font_family = japanese_font.get_family()[0] if japanese_font.get_family() else 'MS Gothic'
                        fonts['small'] = pygame.font.SysFont(font_family, FONT_SIZE_SMALL)
                        fonts['medium'] = pygame.font.SysFont(font_family, FONT_SIZE_MEDIUM)
                        fonts['large'] = pygame.font.SysFont(font_family, FONT_SIZE_LARGE)
                        fonts['title'] = pygame.font.SysFont(font_family, FONT_SIZE_TITLE)
                        fonts['japanese'] = japanese_font
                except:
                    # システムフォント方式にフォールバック
                    fonts['small'] = pygame.font.SysFont('MS Gothic', FONT_SIZE_SMALL)
                    fonts['medium'] = pygame.font.SysFont('MS Gothic', FONT_SIZE_MEDIUM)
                    fonts['large'] = pygame.font.SysFont('MS Gothic', FONT_SIZE_LARGE)
                    fonts['title'] = pygame.font.SysFont('MS Gothic', FONT_SIZE_TITLE)
                    fonts['japanese'] = pygame.font.SysFont('MS Gothic', FONT_SIZE_MEDIUM)
            else:
                # 最終フォールバック
                logger.error("No Japanese font found! Using system default.")
                fonts['small'] = pygame.font.SysFont('MS Gothic', FONT_SIZE_SMALL)
                fonts['medium'] = pygame.font.SysFont('MS Gothic', FONT_SIZE_MEDIUM)
                fonts['large'] = pygame.font.SysFont('MS Gothic', FONT_SIZE_LARGE)
                fonts['title'] = pygame.font.SysFont('MS Gothic', FONT_SIZE_TITLE)
                fonts['japanese'] = pygame.font.SysFont('MS Gothic', FONT_SIZE_MEDIUM)
                
        except Exception as e:
            logger.error(f"Font loading error: {e}. Using emergency fallback.")
            # 緊急フォールバック - MS Gothicを強制使用
            try:
                fonts['small'] = pygame.font.SysFont('MS Gothic', FONT_SIZE_SMALL)
                fonts['medium'] = pygame.font.SysFont('MS Gothic', FONT_SIZE_MEDIUM)
                fonts['large'] = pygame.font.SysFont('MS Gothic', FONT_SIZE_LARGE)
                fonts['title'] = pygame.font.SysFont('MS Gothic', FONT_SIZE_TITLE)
                fonts['japanese'] = pygame.font.SysFont('MS Gothic', FONT_SIZE_MEDIUM)
            except:
                # 最終手段
                default_font = pygame.font.Font(None, 24)
                for key in ['small', 'medium', 'large', 'title', 'japanese']:
                    fonts[key] = default_font
        
        return fonts
    
    def register_state_handler(self, state: GameState, handler):
        """状態ハンドラーを登録"""
        self.state_handlers[state] = handler
        logger.info(f"Registered handler for state: {state}")
    
    def register_state_system(self, state: GameState, system):
        """状態システムを登録"""
        self.state_systems[state] = system
        logger.info(f"Registered system for state: {state}")
    
    def change_state(self, new_state: GameState):
        """ゲーム状態を変更"""
        if self.current_state != new_state:
            logger.info(f"State change: {self.current_state} -> {new_state}")
            
            # 現在の状態を終了
            if self.current_state in self.state_handlers:
                handler = self.state_handlers[self.current_state]
                if hasattr(handler, 'on_exit'):
                    handler.on_exit()
            
            # 新しい状態を開始
            old_state = self.current_state
            self.current_state = new_state
            
            if new_state in self.state_handlers:
                handler = self.state_handlers[new_state]
                if hasattr(handler, 'on_enter'):
                    handler.on_enter(old_state)
    
    def handle_global_events(self, event: pygame.event.Event) -> bool:
        """グローバルイベント処理（全状態で共通）"""
        if event.type == pygame.QUIT:
            self.quit_game()
            return True
        
        elif event.type == pygame.KEYDOWN:
            # デバッグモード切り替え
            if event.key == pygame.K_F1:
                self.debug_mode = not self.debug_mode
                logger.info(f"Debug mode: {self.debug_mode}")
                return True
            
            # FPS表示切り替え
            elif event.key == pygame.K_F2:
                self.show_fps = not self.show_fps
                return True
            
            # ポーズ切り替え
            elif event.key == pygame.K_p:
                self.toggle_pause()
                return True
            
            # 強制終了
            elif event.key == pygame.K_F4 and pygame.key.get_pressed()[pygame.K_LALT]:
                self.quit_game()
                return True
        
        return False
    
    def toggle_pause(self):
        """ポーズ状態を切り替え"""
        if self.current_state != GameState.MENU:
            self.paused = not self.paused
            logger.info(f"Game paused: {self.paused}")
    
    def update(self, dt: float):
        """ゲーム状態更新"""
        if self.paused:
            return
        
        # ゲーム終了条件チェック（ゲーム中のみ）
        if self.current_state in [GameState.DUNGEON_MAP, GameState.BATTLE, GameState.REAL_BATTLE]:
            self.condition_manager.check_game_conditions()
        
        # 現在の状態のシステムを更新
        if self.current_state in self.state_systems:
            system = self.state_systems[self.current_state]
            if hasattr(system, 'update'):
                system.update(dt)
        
        # 現在の状態のハンドラーを更新
        if self.current_state in self.state_handlers:
            handler = self.state_handlers[self.current_state]
            if hasattr(handler, 'update'):
                handler.update(dt)
        
        # フレームカウント更新
        self.frame_count += 1
    
    def render(self):
        """画面描画"""
        # 背景クリア
        self.screen.fill(Colors.UI_BACKGROUND)
        
        # 現在の状態を描画
        if self.current_state in self.state_handlers:
            handler = self.state_handlers[self.current_state]
            if hasattr(handler, 'render'):
                handler.render(self.screen)
        
        # デバッグ情報描画
        if self.debug_mode:
            self._render_debug_info()
        
        # FPS表示
        if self.show_fps:
            self._render_fps()
        
        # ポーズ画面
        if self.paused:
            self._render_pause_overlay()
        
        # 画面更新
        pygame.display.flip()
    
    def _render_debug_info(self):
        """デバッグ情報を描画"""
        debug_info = [
            f"State: {self.current_state.value}",
            f"Frame: {self.frame_count}",
            f"Player HP: {self.game_data.player_hp}/{self.game_data.player_max_hp}",
            f"Floor: {self.game_data.floor}",
            f"Gold: {self.game_data.gold}",
        ]
        
        y_offset = 10
        for info in debug_info:
            text_surface = self.fonts['small'].render(info, True, Colors.WHITE)
            self.screen.blit(text_surface, (10, y_offset))
            y_offset += 20
    
    def _render_fps(self):
        """FPS表示"""
        fps = self.clock.get_fps()
        fps_text = f"FPS: {fps:.1f}"
        text_surface = self.fonts['small'].render(fps_text, True, Colors.WHITE)
        text_rect = text_surface.get_rect()
        text_rect.topright = (SCREEN_WIDTH - 10, 10)
        self.screen.blit(text_surface, text_rect)
    
    def _render_pause_overlay(self):
        """ポーズ画面オーバーレイ"""
        # 半透明背景
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(128)
        overlay.fill(Colors.BLACK)
        self.screen.blit(overlay, (0, 0))
        
        # PAUSED テキスト
        pause_text = self.fonts['title'].render("PAUSED", True, Colors.WHITE)
        text_rect = pause_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        self.screen.blit(pause_text, text_rect)
        
        # 指示テキスト
        instruction = self.fonts['medium'].render("Press P to resume", True, Colors.LIGHT_GRAY)
        instruction_rect = instruction.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50))
        self.screen.blit(instruction, instruction_rect)
    
    def handle_events(self):
        """イベント処理"""
        for event in pygame.event.get():
            # グローバルイベント処理
            if self.handle_global_events(event):
                continue
            
            # ポーズ中はイベント処理をスキップ
            if self.paused:
                continue
            
            # 現在の状態のイベント処理
            if self.current_state in self.state_handlers:
                handler = self.state_handlers[self.current_state]
                if hasattr(handler, 'handle_event'):
                    handler.handle_event(event)
    
    def run(self):
        """メインゲームループ"""
        logger.info("Starting main game loop...")
        
        last_time = pygame.time.get_ticks()
        
        while self.running:
            # 時間計算
            current_time = pygame.time.get_ticks()
            dt = (current_time - last_time) / 1000.0  # 秒単位
            last_time = current_time
            
            # イベント処理
            self.handle_events()
            
            # 更新
            self.update(dt)
            
            # 描画
            self.render()
            
            # FPS制限
            self.clock.tick(FPS)
        
        logger.info("Game loop ended")
        self.cleanup()
    
    def quit_game(self):
        """ゲーム終了"""
        logger.info("Quitting game...")
        self.running = False
    
    def cleanup(self):
        """リソース解放"""
        logger.info("Cleaning up resources...")
        
        # Pygame終了
        pygame.mixer.quit()
        pygame.quit()
        
        logger.info("Cleanup complete")


# ユーティリティ関数
def create_text_surface(font: pygame.font.Font, text: str, color: tuple, 
                       background: Optional[tuple] = None) -> pygame.Surface:
    """テキストサーフェスを作成"""
    if background:
        return font.render(text, True, color, background)
    else:
        return font.render(text, True, color)


def has_japanese_characters(text: str) -> bool:
    """テキストに日本語文字が含まれているかチェック"""
    for char in text:
        if ('\u3040' <= char <= '\u309F' or  # ひらがな
            '\u30A0' <= char <= '\u30FF' or  # カタカナ
            '\u4E00' <= char <= '\u9FAF'):   # 漢字
            return True
    return False


def get_appropriate_font(fonts: Dict[str, pygame.font.Font], text: str, size: str = 'medium') -> pygame.font.Font:
    """テキストに適したフォントを選択"""
    if has_japanese_characters(text):
        return fonts.get('japanese', fonts[size])
    return fonts[size]


def draw_rounded_rect(surface: pygame.Surface, color: tuple, rect: pygame.Rect, 
                     border_radius: int = 5):
    """角丸矩形を描画"""
    if border_radius <= 0:
        pygame.draw.rect(surface, color, rect)
    else:
        # 簡易的な角丸実装
        pygame.draw.rect(surface, color, rect.inflate(-2*border_radius, 0))
        pygame.draw.rect(surface, color, rect.inflate(0, -2*border_radius))
        
        # 角の円
        pygame.draw.circle(surface, color, rect.topleft, border_radius)
        pygame.draw.circle(surface, color, (rect.right-border_radius, rect.top+border_radius), border_radius)
        pygame.draw.circle(surface, color, (rect.left+border_radius, rect.bottom-border_radius), border_radius)
        pygame.draw.circle(surface, color, (rect.right-border_radius, rect.bottom-border_radius), border_radius)


def draw_border_rect(surface: pygame.Surface, color: tuple, rect: pygame.Rect, 
                    border_width: int = 2):
    """枠線付き矩形を描画"""
    pygame.draw.rect(surface, color, rect, border_width)


if __name__ == "__main__":
    # 簡単なテスト実行
    engine = GameEngine()
    
    # テスト用の空ハンドラー
    class TestHandler:
        def render(self, screen):
            font = pygame.font.Font(None, 48)
            text = font.render("Game Engine Test", True, Colors.WHITE)
            text_rect = text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2))
            screen.blit(text, text_rect)
        
        def handle_event(self, event):
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    engine.quit_game()
    
    engine.register_state_handler(GameState.MENU, TestHandler())
    engine.run()