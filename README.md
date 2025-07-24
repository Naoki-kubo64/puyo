# Puyo Rogue - ぷよぷよ×Slay the Spire風ローグライクゲーム

## 概要
ぷよぷよ風の落ち物パズルとSlay the Spireのようなローグライク要素を組み合わせたゲームです。
プレイヤーは連鎖を組んで敵を倒し、報酬を得ながらダンジョンを進んでいきます。

## 実装済み機能

### コア戦闘システム
- ✅ 6x12グリッドのぷよぷよ風パズル
- ✅ 2個組みぷよの落下・操作（←→↑↓キー）
- ✅ 連鎖判定システム（4個以上で消去）
- ✅ 重力処理と連続連鎖
- ✅ リアルタイム敵攻撃システム

### 戦闘システム
- ✅ プレイヤー・敵のHP管理
- ✅ 連鎖によるダメージ計算
- ✅ 敵の時間制攻撃（設定可能間隔）
- ✅ 戦闘勝利/敗北判定

### UI システム
- ✅ プレイヤー/敵のHPバー
- ✅ 敵の攻撃タイマー表示
- ✅ 連鎖情報表示
- ✅ ダメージ表示アニメーション

## Unityでのセットアップ手順

### 1. プロジェクト作成
1. Unity 2022.3 LTS以降で新しい2Dプロジェクトを作成
2. プロジェクト名: "PuyoRogue"

### 2. スクリプト配置
1. 生成されたScriptsフォルダをUnityプロジェクトのAssetsフォルダにコピー
2. Scripts以下の構造:
   ```
   Scripts/
   ├── Battle/
   │   ├── BattleManager.cs
   │   ├── DamageCalculator.cs
   │   ├── FallingPuyo.cs
   │   ├── PuzzleGrid.cs
   │   └── PuzzleManager.cs
   ├── Core/
   │   ├── GameConfig.cs
   │   └── PuyoType.cs
   ├── Enemy/
   │   └── Enemy.cs
   ├── Player/
   │   └── Player.cs
   └── UI/
       └── BattleUI.cs
   ```

### 3. GameConfig作成
1. Project窓で右クリック → Create → Puyo Rogue → Game Config
2. 作成されたGameConfigアセットの設定を調整

### 4. シーン構築

#### 基本オブジェクト構成
```
BattleScene
├── Main Camera
├── Canvas (UI)
│   ├── PlayerHealthBar (Slider)
│   ├── EnemyHealthBar (Slider)
│   ├── EnemyTimer (Text)
│   ├── ChainInfo (Text)
│   └── DamageText (Text)
├── GameManager (Empty GameObject)
│   ├── BattleManager.cs
│   ├── Player.cs
│   └── Enemy.cs
├── PuzzleGrid (Empty GameObject)
│   └── PuzzleGrid.cs
├── PuzzleManager (Empty GameObject)
│   └── PuzzleManager.cs
└── UI (Empty GameObject)
    └── BattleUI.cs
```

### 5. プレハブ作成

#### ぷよプレハブ
1. Sphere or Cubeプリミティブを作成
2. 名前を"Puyo"に変更
3. Prefabsフォルダに保存

#### FallingPuyoプレハブ
1. 空のGameObjectを作成
2. FallingPuyo.csをアタッチ
3. Prefabsフォルダに保存

### 6. 参照設定
各コンポーネントで必要な参照を設定:
- BattleManager: Player, Enemy, PuzzleManager, BattleUI, GameConfig
- PuzzleGrid: puyoPrefab, GameConfig
- PuzzleManager: grid, fallingPuyoPrefab, GameConfig
- BattleUI: 各UIエレメント

## 操作方法
- ←→: ぷよ移動
- ↑: ぷよ回転
- ↓: 高速落下

## ダメージ計算
- 基本ダメージ = 基準値 × 消去数
- 連鎖ボーナス = 連鎖倍率^(連鎖数-1)
- 最終ダメージ = 基本ダメージ × 連鎖ボーナス

## 今後の拡張予定
- [ ] 報酬選択システム
- [ ] 特殊ぷよ（爆発、回復、毒など）
- [ ] アクセサリ・装備システム
- [ ] マップ選択システム
- [ ] ローグライク要素（ランダム生成）
- [ ] 音響・エフェクト

## 技術的な特徴
- モジュラー設計で機能追加が容易
- イベント駆動アーキテクチャ
- ScriptableObjectによる設定管理
- コルーチンによる非同期処理