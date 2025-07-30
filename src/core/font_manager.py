"""
フォント管理クラス - フォント読み込みロジックの分離と改善
"""

import pygame
import logging
import os
import platform
from typing import Dict, List, Optional
from core.constants import *

logger = logging.getLogger(__name__)


class FontManager:
    """フォント読み込みと管理を担当するクラス"""
    
    def __init__(self):
        self.loaded_fonts: Dict[str, pygame.font.Font] = {}
        self.font_cache: Dict[tuple, pygame.font.Font] = {}
        
    def load_all_fonts(self) -> Dict[str, pygame.font.Font]:
        """すべてのフォントサイズを読み込み"""
        try:
            base_font = self._load_primary_font()
            if not base_font:
                logger.warning("Primary font loading failed, using fallback")
                base_font = self._load_fallback_font()
            
            # 各サイズのフォントを生成
            fonts = self._create_font_set(base_font)
            self.loaded_fonts = fonts
            
            logger.info(f"Successfully loaded {len(fonts)} font sizes")
            return fonts
            
        except Exception as e:
            logger.error(f"Critical font loading error: {e}")
            return self._create_emergency_fonts()
    
    def _load_primary_font(self) -> Optional[pygame.font.Font]:
        """プライマリフォントを読み込み"""
        if platform.system() == "Windows":
            return self._load_windows_fonts()
        else:
            return self._load_system_fonts()
    
    def _load_windows_fonts(self) -> Optional[pygame.font.Font]:
        """Windows用フォントを読み込み"""
        font_paths = [
            "C:/Windows/Fonts/seguiemj.ttf",      # 絵文字対応フォント（優先）
            "C:/Windows/Fonts/NotoColorEmoji.ttf", # Google絵文字フォント
            "C:/Windows/Fonts/msgothic.ttc",       # MSゴシック
            "C:/Windows/Fonts/msmincho.ttc",       # MS明朝
            "C:/Windows/Fonts/YuGothM.ttc",        # 游ゴシック
            "C:/Windows/Fonts/meiryo.ttc",         # メイリオ
        ]
        
        for font_path in font_paths:
            try:
                font = self._try_load_font(font_path)
                if font and self._validate_font(font):
                    logger.info(f"Loaded Windows font: {font_path}")
                    return font
            except (pygame.error, FileNotFoundError) as e:
                logger.debug(f"Failed to load font {font_path}: {e}")
            except OSError as e:
                logger.warning(f"System error loading font {font_path}: {e}")
        
        return None
    
    def _load_system_fonts(self) -> Optional[pygame.font.Font]:
        """システムフォントを読み込み"""
        system_fonts = [
            "NotoSansCJK-Regular",
            "DejaVuSans", 
            "Liberation Sans",
            "Arial"
        ]
        
        for font_name in system_fonts:
            try:
                font = pygame.font.SysFont(font_name, FONT_SIZE_MEDIUM)
                if self._validate_font(font):
                    logger.info(f"Loaded system font: {font_name}")
                    return font
            except pygame.error as e:
                logger.debug(f"Failed to load system font {font_name}: {e}")
        
        return None
    
    def _try_load_font(self, font_path: str) -> Optional[pygame.font.Font]:
        """個別のフォントファイルを読み込み"""
        if not os.path.exists(font_path):
            return None
            
        return pygame.font.Font(font_path, FONT_SIZE_MEDIUM)
    
    def _validate_font(self, font: pygame.font.Font) -> bool:
        """フォントが正常に使用できるかテスト"""
        try:
            # 日本語テスト
            japanese_surface = font.render("ゴブリン", True, Colors.WHITE)
            english_surface = font.render("Goblin", True, Colors.WHITE)
            
            return (japanese_surface.get_width() > 0 and 
                   english_surface.get_width() > 0)
        except Exception as e:
            logger.debug(f"Font validation failed: {e}")
            return False
    
    def _load_fallback_font(self) -> pygame.font.Font:
        """フォールバックフォントを読み込み"""
        try:
            # pygame デフォルトフォント
            return pygame.font.Font(None, FONT_SIZE_MEDIUM)
        except Exception as e:
            logger.error(f"Fallback font loading failed: {e}")
            raise RuntimeError("No usable fonts available")
    
    def _create_font_set(self, base_font: pygame.font.Font) -> Dict[str, pygame.font.Font]:
        """ベースフォントから各サイズのフォントセットを作成"""
        font_info = base_font.get_height()  # フォント情報を取得
        font_path = None
        
        # フォントパスを取得（可能であれば）
        if hasattr(base_font, 'get_ascent'):
            try:
                # ベースフォントから情報を取得してパスを推定
                pass  # 実際のパス取得は困難なので、代替手段を使用
            except:
                pass
        
        try:
            fonts = {}
            sizes = {
                'small': FONT_SIZE_SMALL,
                'medium': FONT_SIZE_MEDIUM, 
                'large': FONT_SIZE_LARGE,
                'title': FONT_SIZE_TITLE
            }
            
            for size_name, size_value in sizes.items():
                if size_value == FONT_SIZE_MEDIUM:
                    fonts[size_name] = base_font
                else:
                    # 新しいサイズでフォントを作成
                    fonts[size_name] = self._create_sized_font(base_font, size_value)
            
            return fonts
            
        except Exception as e:
            logger.error(f"Font set creation failed: {e}")
            return self._create_emergency_fonts()
    
    def _create_sized_font(self, base_font: pygame.font.Font, size: int) -> pygame.font.Font:
        """指定サイズでフォントを作成"""
        try:
            # 可能であればbase_fontと同じファイルから新しいサイズを作成
            # そうでなければデフォルトフォントを使用
            return pygame.font.Font(None, size)
        except Exception:
            return pygame.font.Font(None, size)
    
    def _create_emergency_fonts(self) -> Dict[str, pygame.font.Font]:
        """緊急時用の最小限フォントセット"""
        logger.warning("Creating emergency font set")
        try:
            return {
                'small': pygame.font.Font(None, FONT_SIZE_SMALL),
                'medium': pygame.font.Font(None, FONT_SIZE_MEDIUM),
                'large': pygame.font.Font(None, FONT_SIZE_LARGE),
                'title': pygame.font.Font(None, FONT_SIZE_TITLE)
            }
        except Exception as e:
            logger.critical(f"Emergency font creation failed: {e}")
            raise RuntimeError("Critical font system failure")
    
    def get_appropriate_font(self, text: str, size_name: str = 'medium') -> pygame.font.Font:
        """テキストに適したフォントを取得"""
        if size_name not in self.loaded_fonts:
            logger.warning(f"Font size '{size_name}' not found, using medium")
            size_name = 'medium'
        
        return self.loaded_fonts[size_name]
    
    def clear_cache(self):
        """フォントキャッシュをクリア"""
        self.font_cache.clear()
        logger.debug("Font cache cleared")