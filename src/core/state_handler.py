"""
状態ハンドラー基底クラス
全てのゲーム状態ハンドラーの基底クラス
"""

import pygame
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .game_engine import GameEngine

class StateHandler(ABC):
    """ゲーム状態ハンドラーの基底クラス"""
    
    def __init__(self, engine: 'GameEngine'):
        """
        状態ハンドラーを初期化
        
        Args:
            engine: ゲームエンジンインスタンス
        """
        self.engine = engine
    
    @abstractmethod
    def handle_event(self, event: pygame.event.Event) -> bool:
        """
        イベントを処理
        
        Args:
            event: Pygameイベント
            
        Returns:
            bool: イベントが処理された場合True
        """
        pass
    
    @abstractmethod
    def update(self, dt: float):
        """
        状態を更新
        
        Args:
            dt: デルタタイム（秒）
        """
        pass
    
    @abstractmethod
    def render(self, screen: pygame.Surface):
        """
        画面に描画
        
        Args:
            screen: 描画対象のサーフェス
        """
        pass
    
    def on_enter(self, previous_state=None):
        """
        状態に入った時の処理
        
        Args:
            previous_state: 前の状態（オプション）
        """
        pass
    
    def on_exit(self):
        """
        状態から出る時の処理
        """
        pass