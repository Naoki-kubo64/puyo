"""
ゲーム定数定義
Drop Puzzle × Roguelike の全定数を管理
"""

from enum import Enum
from dataclasses import dataclass
from typing import Tuple

# ============================================================================
# 画面・描画関連
# ============================================================================

# 画面サイズ
SCREEN_WIDTH = 1920
SCREEN_HEIGHT = 1080
FPS = 60

# 色定義 (R, G, B)
class Colors:
    BLACK = (0, 0, 0)
    WHITE = (255, 255, 255)
    GRAY = (128, 128, 128)
    DARK_GRAY = (64, 64, 64)
    LIGHT_GRAY = (192, 192, 192)
    
    # ぷよの色
    RED = (255, 100, 100)
    BLUE = (100, 150, 255)
    GREEN = (100, 255, 100)
    YELLOW = (255, 255, 100)
    PURPLE = (200, 100, 255)
    ORANGE = (255, 180, 100)
    CYAN = (100, 255, 255)
    
    # 追加色（ダンジョンマップ用）
    DARK_RED = (180, 50, 50)
    
    # UI色
    UI_BACKGROUND = (40, 40, 60)
    UI_BORDER = (100, 100, 120)
    UI_TEXT = (240, 240, 240)
    UI_HIGHLIGHT = (120, 180, 255)

# ============================================================================
# ぷよぷよ関連
# ============================================================================

# グリッドサイズ
GRID_WIDTH = 6
GRID_HEIGHT = 12
PUYO_SIZE = 60  # ピクセル（40から60に拡大）

# グリッド描画位置（上部UIバーの下に配置）
GRID_OFFSET_X = 200  # より右に配置
GRID_OFFSET_Y = 200  # より下に配置

# ぷよタイプ
class PuyoType(Enum):
    EMPTY = 0
    RED = 1
    BLUE = 2
    GREEN = 3
    YELLOW = 4
    PURPLE = 5
    ORANGE = 6
    CYAN = 7
    GARBAGE = 8  # おじゃまぷよ

# ぷよ色マッピング
PUYO_COLORS = {
    PuyoType.EMPTY: Colors.BLACK,
    PuyoType.RED: Colors.RED,
    PuyoType.BLUE: Colors.BLUE,
    PuyoType.GREEN: Colors.GREEN,
    PuyoType.YELLOW: Colors.YELLOW,
    PuyoType.PURPLE: Colors.PURPLE,
    PuyoType.ORANGE: Colors.ORANGE,
    PuyoType.CYAN: Colors.CYAN,
    PuyoType.GARBAGE: Colors.GRAY,
}

# 落下速度 (秒)
FALL_SPEED = 0.8  # 少し高速化
FAST_FALL_SPEED = 0.05  # より高速に

# 連鎖設定
MIN_CHAIN_LENGTH = 4  # 連鎖に必要な最小個数
CHAIN_SCORE_BASE = 10   # 基本スコア（ダメージ計算用、10分の1に削減）
CHAIN_MULTIPLIER = 1.5  # 連鎖倍率

# ============================================================================
# 戦闘関連
# ============================================================================

# プレイヤー初期値
PLAYER_MAX_HP = 100
PLAYER_INITIAL_HP = 100

# 敵初期値
ENEMY_BASE_HP = 20  # 初期敵HP（ダンジョン進行で強化される前提）
ENEMY_ATTACK_DAMAGE = 8   # 初期敵攻撃力（ダンジョン進行で強化される前提）
ENEMY_ATTACK_INTERVAL = 6.0  # 秒（初心者に優しい間隔、後で短縮）

# ダメージ計算
DAMAGE_PER_PUYO = 10
CHAIN_DAMAGE_MULTIPLIER = 1.2

# ダンジョン進行システム
FLOOR_SCALING_HP = 1.25     # フロアごとの敵HP倍率（より緩やか）
FLOOR_SCALING_DAMAGE = 1.15 # フロアごりの敵攻撃力倍率（より緩やか）
FLOOR_SCALING_SPEED = 0.92  # フロアごとの敵攻撃間隔倍率（短縮をより緩やか）

# ============================================================================
# カードシステム関連
# ============================================================================

# カードレアリティ
class Rarity(Enum):
    COMMON = 1      # 白
    UNCOMMON = 2    # 緑
    RARE = 3        # 青
    EPIC = 4        # 紫
    LEGENDARY = 5   # 金

# カードレアリティ色
RARITY_COLORS = {
    Rarity.COMMON: Colors.WHITE,
    Rarity.UNCOMMON: Colors.GREEN,
    Rarity.RARE: Colors.BLUE,
    Rarity.EPIC: Colors.PURPLE,
    Rarity.LEGENDARY: Colors.YELLOW,
}

# デッキサイズ
MAX_DECK_SIZE = 30
INITIAL_DECK_SIZE = 10
HAND_SIZE = 5

# カードコスト
MAX_CARD_COST = 10

# ============================================================================
# ローグライク関連
# ============================================================================

# ダンジョン設定
DUNGEON_FLOORS = 10
BATTLES_PER_FLOOR = 3
BOSS_FLOOR_INTERVAL = 3  # 3階ごとにボス

# 報酬設定
REWARD_CARDS_COUNT = 3  # 戦闘後に選択できるカード数
GOLD_PER_BATTLE = 25
GOLD_PER_BOSS = 100

# ============================================================================
# UI関連
# ============================================================================

# フォントサイズ
FONT_SIZE_SMALL = 16
FONT_SIZE_MEDIUM = 24
FONT_SIZE_LARGE = 32
FONT_SIZE_TITLE = 48

# UI要素サイズ
BUTTON_WIDTH = 200
BUTTON_HEIGHT = 50
CARD_WIDTH = 120
CARD_HEIGHT = 180

# レイアウト
UI_MARGIN = 20
UI_PADDING = 10

# ============================================================================
# 入力関連
# ============================================================================

# キーバインド
class Keys:
    # ぷよ操作
    MOVE_LEFT = 'a'
    MOVE_RIGHT = 'd'
    MOVE_DOWN = 's'
    ROTATE_CW = 'space'        # 時計回り
    ROTATE_CCW = 'w'           # 反時計回り
    
    # UI操作
    CONFIRM = 'return'
    CANCEL = 'escape'
    PAUSE = 'p'
    
    # デバッグ
    DEBUG_TOGGLE = 'f1'
    GRID_TOGGLE = 'f2'

# ============================================================================
# ゲーム状態
# ============================================================================

class GameState(Enum):
    MENU = "menu"
    PLAYING = "playing"
    BATTLE = "battle"
    REAL_BATTLE = "real_battle"  # 新しい戦闘状態
    REWARD_SELECT = "reward_select"  # 報酬選択画面
    DUNGEON_MAP = "dungeon_map"  # ダンジョンマップ画面
    CARD_SELECT = "card_select"
    GAME_OVER = "game_over"
    VICTORY = "victory"
    PAUSE = "pause"

# ============================================================================
# デバッグ関連
# ============================================================================

DEBUG_MODE = True
SHOW_FPS = True
SHOW_GRID = True
SHOW_CHAIN_INFO = True

# ログレベル
import logging
LOG_LEVEL = logging.DEBUG if DEBUG_MODE else logging.INFO

# ============================================================================
# バランス調整用定数
# ============================================================================

@dataclass
class BalanceConfig:
    """ゲームバランス調整用の設定クラス"""
    
    # ぷよぷよ関連
    fall_speed: float = 1.0
    chain_bonus_multiplier: float = 1.5
    min_chain_for_damage: int = 4
    
    # 戦闘関連
    base_damage_per_puyo: int = 10
    chain_damage_scaling: float = 1.2
    enemy_hp_scaling: float = 1.1  # 階層ごとのHP増加率
    
    # カード関連
    card_draw_cost: int = 1
    max_hand_size: int = 7
    
    # 経済関連
    shop_refresh_cost: int = 2
    card_remove_cost: int = 50

# デフォルトバランス設定
DEFAULT_BALANCE = BalanceConfig()

# ============================================================================
# 数学関連ユーティリティ
# ============================================================================

# 方向ベクトル (グリッド座標用)
DIRECTIONS = [
    (0, -1),  # 上
    (1, 0),   # 右
    (0, 1),   # 下
    (-1, 0),  # 左
]

# 対角線方向も含む8方向
DIRECTIONS_8 = [
    (-1, -1), (0, -1), (1, -1),
    (-1,  0),          (1,  0),
    (-1,  1), (0,  1), (1,  1),
]