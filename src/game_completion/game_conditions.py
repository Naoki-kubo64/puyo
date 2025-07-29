"""
ゲーム勝利・敗北条件管理システム
プレイヤーの状態を監視し、適切な終了画面に遷移
"""

import logging
from core.game_engine import GameEngine
from core.constants import GameState

logger = logging.getLogger(__name__)

class GameConditionManager:
    """ゲーム終了条件を管理するクラス"""
    
    def __init__(self, engine: GameEngine):
        self.engine = engine
        self.victory_conditions = {
            "boss_defeat": False,      # ボス撃破
            "floor_15_clear": False,   # 15フロア制覇
            "special_ending": False    # 特殊エンディング条件
        }
        
        self.max_floors = 15  # ゲームクリアフロア数
        self.last_checked_floor = 0
    
    def check_game_conditions(self) -> bool:
        """ゲーム終了条件をチェック"""
        # 敗北条件チェック
        if self._check_defeat_conditions():
            return True
        
        # 勝利条件チェック
        if self._check_victory_conditions():
            return True
        
        return False
    
    def _check_defeat_conditions(self) -> bool:
        """敗北条件をチェック"""
        player = self.engine.player
        
        # HP0で死亡
        if player.hp <= 0:
            self._trigger_game_over("戦闘で力尽きた")
            return True
        
        # 特殊な敗北条件（将来的に追加可能）
        # 例：呪いによる死亡、時間制限など
        
        return False
    
    def _check_victory_conditions(self) -> bool:
        """勝利条件をチェック"""
        player = self.engine.player
        
        # フロア進行チェック
        if player.current_floor > self.last_checked_floor:
            self.last_checked_floor = player.current_floor
            
            # 最終フロア到達
            if player.current_floor >= self.max_floors:
                self._trigger_victory("ダンジョン制覇")
                return True
        
        # ボス撃破チェック
        if self._check_boss_defeat():
            self.victory_conditions["boss_defeat"] = True
            self._trigger_victory("ボス撃破")
            return True
        
        # 特殊勝利条件
        if self._check_special_victory_conditions():
            self.victory_conditions["special_ending"] = True
            self._trigger_victory("完全制覇")
            return True
        
        return False
    
    def _check_boss_defeat(self) -> bool:
        """ボス撃破をチェック"""
        player = self.engine.player
        
        # 10フロア以上でボス戦を複数回勝利
        if (player.current_floor >= 10 and 
            player.stats.boss_battles >= 2):
            return True
        
        return False
    
    def _check_special_victory_conditions(self) -> bool:
        """特殊勝利条件をチェック"""
        player = self.engine.player
        
        # 完全制覇条件：高フロア + 高勝率 + 豊富なアイテム
        perfect_victory = (
            player.current_floor >= self.max_floors and
            player.stats.get_win_rate() >= 90.0 and
            len(player.inventory.items) >= 15 and
            player.gold >= 500
        )
        
        if perfect_victory:
            return True
        
        return False
    
    def _trigger_game_over(self, death_cause: str):
        """ゲームオーバー画面に遷移"""
        logger.info(f"Game Over triggered: {death_cause}")
        
        try:
            from .game_over_handler import GameOverHandler
            game_over_handler = GameOverHandler(self.engine, death_cause)
            self.engine.register_state_handler(GameState.GAME_OVER, game_over_handler)
            self.engine.change_state(GameState.GAME_OVER)
        except Exception as e:
            logger.error(f"Failed to create game over handler: {e}")
            # フォールバック：メニューに戻る
            self.engine.change_state(GameState.MENU)
    
    def _trigger_victory(self, victory_type: str):
        """勝利画面に遷移"""
        logger.info(f"Victory triggered: {victory_type}")
        
        try:
            from .victory_handler import VictoryHandler
            victory_handler = VictoryHandler(self.engine, victory_type)
            self.engine.register_state_handler(GameState.VICTORY, victory_handler)
            self.engine.change_state(GameState.VICTORY)
        except Exception as e:
            logger.error(f"Failed to create victory handler: {e}")
            # フォールバック：メニューに戻る
            self.engine.change_state(GameState.MENU)
    
    def force_game_over(self, reason: str = "強制終了"):
        """強制的にゲームオーバーにする"""
        self._trigger_game_over(reason)
    
    def force_victory(self, victory_type: str = "特殊勝利"):
        """強制的に勝利にする（デバッグ用）"""
        self._trigger_victory(victory_type)
    
    def reset_conditions(self):
        """勝利条件をリセット"""
        self.victory_conditions = {
            "boss_defeat": False,
            "floor_15_clear": False,
            "special_ending": False
        }
        self.last_checked_floor = 0
        logger.info("Game conditions reset")
    
    def get_progress_info(self) -> dict:
        """進行状況情報を取得"""
        player = self.engine.player
        
        return {
            "current_floor": player.current_floor,
            "max_floors": self.max_floors,
            "progress_percent": min(100, (player.current_floor / self.max_floors) * 100),
            "boss_battles": player.stats.boss_battles,
            "win_rate": player.stats.get_win_rate(),
            "victory_conditions": self.victory_conditions.copy()
        }