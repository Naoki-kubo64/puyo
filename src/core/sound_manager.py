"""
サウンドマネージャー - SEとBGMの管理
Drop Puzzle × Roguelike のサウンドシステム
"""

import pygame
import logging
import os
from typing import Dict, Optional
from enum import Enum

logger = logging.getLogger(__name__)


class SoundType(Enum):
    """サウンドの種類"""
    MOVE = "move"          # ぷよの移動
    ROTATE = "rotate"      # ぷよの回転
    ELIMINATE = "eliminate" # ぷよの消去
    CHAIN = "chain"        # 連鎖
    DROP = "drop"          # ぷよが着地


class SoundManager:
    """サウンド管理クラス"""
    
    def __init__(self):
        """サウンドマネージャー初期化"""
        self.sounds: Dict[SoundType, pygame.mixer.Sound] = {}
        self.enabled = True
        self.volume = 0.7
        
        # pygameのミキサー初期化
        try:
            pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)
            logger.info("Sound system initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize sound system: {e}")
            self.enabled = False
            return
        
        # SEファイルを読み込み
        self._load_sounds()
    
    def _load_sounds(self):
        """SE音源を読み込み"""
        if not self.enabled:
            return
        
        # SEフォルダのパス
        se_folder = os.path.join(os.path.dirname(__file__), '..', '..', 'SE')
        
        # 音源ファイルのマッピング
        sound_files = {
            SoundType.MOVE: "移動.mp3",
            SoundType.ROTATE: "回転.mp3", 
            SoundType.ELIMINATE: "消え.mp3"
        }
        
        for sound_type, filename in sound_files.items():
            file_path = os.path.join(se_folder, filename)
            try:
                if os.path.exists(file_path):
                    sound = pygame.mixer.Sound(file_path)
                    sound.set_volume(self.volume)
                    self.sounds[sound_type] = sound
                    logger.info(f"Loaded sound: {filename}")
                else:
                    logger.warning(f"Sound file not found: {file_path}")
            except Exception as e:
                logger.error(f"Failed to load sound {filename}: {e}")
    
    def play_sound(self, sound_type: SoundType):
        """指定したSEを再生"""
        if not self.enabled or sound_type not in self.sounds:
            return
        
        try:
            self.sounds[sound_type].play()
            logger.debug(f"Played sound: {sound_type.value}")
        except Exception as e:
            logger.error(f"Failed to play sound {sound_type.value}: {e}")
    
    def set_volume(self, volume: float):
        """音量設定（0.0-1.0）"""
        self.volume = max(0.0, min(1.0, volume))
        
        if self.enabled:
            for sound in self.sounds.values():
                sound.set_volume(self.volume)
            logger.info(f"Volume set to {self.volume}")
    
    def set_enabled(self, enabled: bool):
        """サウンド有効/無効切り替え"""
        self.enabled = enabled
        logger.info(f"Sound {'enabled' if enabled else 'disabled'}")
    
    def stop_all(self):
        """全てのサウンドを停止"""
        if self.enabled:
            pygame.mixer.stop()
            logger.debug("All sounds stopped")


# グローバルサウンドマネージャーインスタンス
_sound_manager: Optional[SoundManager] = None


def get_sound_manager() -> SoundManager:
    """サウンドマネージャーのシングルトンインスタンスを取得"""
    global _sound_manager
    if _sound_manager is None:
        _sound_manager = SoundManager()
    return _sound_manager


def play_se(sound_type: SoundType):
    """SE再生のショートカット関数"""
    get_sound_manager().play_sound(sound_type)