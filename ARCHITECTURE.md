# 🎮 Drop Puzzle × Roguelike Architecture

## 📋 システム構成

```
Dorp Puzzle X Rogeulike/
├── src/
│   ├── core/
│   │   ├── game_engine.py      # メインゲームループ & 状態管理
│   │   ├── constants.py        # ゲーム定数
│   │   └── utils.py           # ユーティリティ関数
│   ├── puzzle/
│   │   ├── puyo_grid.py       # ぷよグリッドシステム
│   │   ├── puyo_piece.py      # ぷよピース管理
│   │   ├── chain_system.py    # 連鎖検出・計算
│   │   └── falling_system.py  # 落下制御
│   ├── battle/
│   │   ├── battle_manager.py  # 戦闘管理
│   │   ├── damage_system.py   # ダメージ計算
│   │   └── enemy_system.py    # 敵システム
│   ├── cards/
│   │   ├── card_system.py     # カードシステム
│   │   ├── deck_manager.py    # デッキ管理
│   │   └── card_effects.py    # カード効果
│   ├── roguelike/
│   │   ├── dungeon.py         # ダンジョン生成
│   │   ├── progression.py     # 進行管理
│   │   └── rewards.py         # 報酬システム
│   └── ui/
│       ├── renderer.py        # 描画システム
│       ├── input_handler.py   # 入力処理
│       └── ui_components.py   # UIコンポーネント
├── assets/
│   ├── sprites/              # 画像ファイル
│   ├── sounds/               # 音声ファイル
│   └── fonts/                # フォントファイル
├── tests/
│   └── test_*.py            # テストファイル
├── main.py                  # エントリーポイント
└── requirements.txt         # 依存関係
```

## 🎯 開発フェーズ

### Phase 1: Core Systems (基礎システム)
1. **Game Engine** - メインループ、状態管理
2. **Puzzle Grid** - 6x12グリッド、ぷよ配置
3. **Basic Input** - キーボード操作
4. **Simple Renderer** - 基本描画

### Phase 2: Puzzle Mechanics (パズル機能)
1. **Falling System** - ぷよ落下制御
2. **Chain Detection** - 4個以上の同色検出
3. **Chain Calculation** - 連鎖倍率計算
4. **Animation System** - 基本アニメーション

### Phase 3: Battle Integration (戦闘統合)
1. **Battle Manager** - ターン制戦闘
2. **Damage System** - 連鎖ダメージ変換
3. **Enemy System** - 敵AI、攻撃パターン
4. **Health System** - HP管理

### Phase 4: Card System (カードシステム)
1. **Card Framework** - カード基本構造
2. **Deck Management** - デッキ構築
3. **Card Effects** - 特殊効果システム
4. **Card Integration** - パズル連携

### Phase 5: Roguelike Elements (ローグライク要素)
1. **Dungeon Generation** - マップ生成
2. **Progression System** - レベル進行
3. **Reward System** - 戦闘後報酬
4. **Permadeath** - ゲームオーバー処理

### Phase 6: Polish & Balance (調整・完成)
1. **UI Polish** - インターフェース改善
2. **Sound Integration** - 音響効果
3. **Balance Tuning** - ゲームバランス
4. **Performance Optimization** - 最適化

## 🏗️ 技術設計原則

### 1. **Modular Design (モジュラー設計)**
- 各システムは独立して動作
- 明確なインターフェース定義
- 疎結合アーキテクチャ

### 2. **Event-Driven Architecture (イベント駆動)**
- システム間通信はイベント経由
- 拡張性と保守性を重視
- デバッグしやすい構造

### 3. **Data-Driven Configuration (データ駆動設定)**
- ゲーム設定は外部ファイル
- バランス調整が容易
- ホットリロード対応

### 4. **Test-Driven Development (テスト駆動開発)**
- 各システムは単体テスト対応
- 自動テスト環境構築
- リグレッション防止

## 🎮 ゲームフロー

```
Title Screen
    ↓
New Game
    ↓
Dungeon Map
    ↓
Battle Start
    ↓
Puzzle Phase (ぷよぷよ)
    ↓
Damage Calculation
    ↓
Enemy Turn
    ↓
Battle Result
    ↓
Reward Selection (カード選択)
    ↓
Next Battle / Boss / Shop
    ↓
Game Clear / Game Over
```

## 📊 データ構造

### PuyoGrid
```python
class PuyoGrid:
    width: int = 6
    height: int = 12
    grid: List[List[Optional[PuyoType]]]
```

### Card
```python
class Card:
    id: str
    name: str
    cost: int
    effect: CardEffect
    rarity: Rarity
```

### Battle
```python
class BattleState:
    player_hp: int
    enemy_hp: int
    turn_count: int
    puzzle_grid: PuyoGrid
    current_deck: List[Card]
```