# 🎮 Drop Puzzle × Roguelike (Python版)

**ぷよぷよ × Slay the Spire** 風のローグライクパズルゲーム

## 🚀 クイックスタート

### 1. 環境準備
```bash
# Python 3.7+ が必要
pip install -r requirements.txt
```

### 2. ゲーム実行
```bash
python main.py
```

## 🎯 現在の機能

### ✅ Phase 1: Core Systems (完成)
- **Game Engine** - メインループ、状態管理、FPS制御
- **Puyo Grid** - 6x12グリッド、ぷよ配置システム
- **Chain Detection** - 4個以上の同色連鎖検出
- **Renderer** - 美しいぷよ描画、UI表示

### 🎮 操作方法
- **ESC** - ゲーム終了
- **R** - グリッドリセット
- **SPACE** - 手動ぷよドロップ
- **C** - 連鎖実行
- **左クリック** - 指定位置にぷよ配置
- **F1** - デバッグモード切り替え
- **F2** - FPS表示切り替え

### 🎨 ゲームの特徴
- **自動ぷよドロップ** - 2秒間隔で自動的にランダムぷよが落下
- **リアルタイム連鎖** - 4個以上の同色ぷよが自動で消える
- **連鎖スコア計算** - 連鎖レベルによるボーナススコア
- **視覚的フィードバック** - 美しいぷよ描画とハイライト効果

## 🏗️ アーキテクチャ

```
Drop Puzzle X Roguelike/
├── src/
│   ├── core/
│   │   ├── game_engine.py      # ✅ メインゲームループ
│   │   ├── constants.py        # ✅ ゲーム定数
│   │   └── utils.py           # 🔄 ユーティリティ関数
│   ├── puzzle/
│   │   ├── puyo_grid.py       # ✅ ぷよグリッドシステム
│   │   ├── puyo_piece.py      # 🔄 落下ぷよ管理
│   │   ├── chain_system.py    # 🔄 高度な連鎖システム
│   │   └── falling_system.py  # 🔄 落下制御
│   ├── battle/
│   │   ├── battle_manager.py  # ⏳ 戦闘管理
│   │   ├── damage_system.py   # ⏳ ダメージ計算
│   │   └── enemy_system.py    # ⏳ 敵システム
│   └── cards/
│       ├── card_system.py     # ⏳ カードシステム
│       └── deck_manager.py    # ⏳ デッキ管理
├── main.py                    # ✅ エントリーポイント
└── requirements.txt           # ✅ 依存関係
```

**凡例**: ✅完成 | 🔄進行中 | ⏳未実装

## 🎨 スクリーンショット機能

### ゲーム画面
- **左側**: 6x12ぷよぷよグリッド
- **右側**: ゲーム情報（チェイン数、スコア、操作説明）
- **自動ドロップ**: 2秒間隔でランダムぷよが落下
- **連鎖システム**: 4個以上で自動消去、重力適用

### デバッグ機能
- **F1**: デバッグ情報表示（状態、HP、フロア情報）
- **F2**: FPS表示
- **コンソールログ**: 詳細なゲームイベント記録

## 🎯 次の開発段階

### Phase 2: Puzzle Mechanics
- [ ] **Falling System** - プレイヤー操作でぷよ制御
- [ ] **Advanced Chains** - より複雑な連鎖パターン
- [ ] **Special Puyos** - 特殊効果のぷよ

### Phase 3: Battle Integration  
- [ ] **Battle Manager** - ターン制戦闘システム
- [ ] **Damage System** - 連鎖ダメージの戦闘への変換
- [ ] **Enemy System** - 敵AI、攻撃パターン

### Phase 4: Card System
- [ ] **Card Framework** - カード基本構造
- [ ] **Deck Management** - デッキ構築システム
- [ ] **Card Effects** - 特殊効果システム

## 🐛 トラブルシューティング

### よくある問題

**Q: 「pygame is not installed」エラー**
```bash
pip install pygame
```

**Q: 画面が表示されない**
- グラフィックドライバーを確認
- Python 3.7以上を使用

**Q: フォントエラー**
- システムフォントが自動的に使用されます
- 日本語表示に問題がある場合はOSの言語設定を確認

### デバッグモード
```bash
# ログレベル変更
export LOG_LEVEL=DEBUG
python main.py
```

## 🎮 ゲームデザイン思想

### ぷよぷよ要素
- **6x12グリッド** - 標準的なぷよぷよサイズ
- **4個連鎖** - 同色4個以上で消去
- **連鎖ボーナス** - 連続連鎖で高スコア
- **重力システム** - 消去後の自然な落下

### ローグライク要素（予定）
- **ダンジョン進行** - フロア制の進行システム
- **戦闘統合** - 連鎖ダメージで敵を攻撃
- **カード収集** - 戦闘後の報酬システム
- **永続進行** - 死亡時のリセット

### Slay the Spire要素（予定）
- **デッキ構築** - 戦闘後のカード選択
- **レリック効果** - 永続的な特殊効果
- **多様な戦略** - カードとぷよの組み合わせ

## 📊 技術仕様

- **言語**: Python 3.7+
- **ライブラリ**: Pygame 2.5+, NumPy
- **解像度**: 1200x800 (可変対応)
- **FPS**: 60fps固定
- **アーキテクチャ**: モジュラー設計、イベント駆動

## 🤝 開発者向け情報

### コード規約
- **PEP 8** 準拠
- **Type Hints** 使用推奨
- **Docstring** 必須
- **ログ出力** 適切なレベル設定

### テスト実行
```bash
# 各モジュール単体テスト
python -m src.puzzle.puyo_grid
python -m src.core.game_engine

# 統合テスト
python main.py
```

### 拡張方法
1. `src/` 下に新しいモジュール作成
2. `constants.py` に必要な定数追加
3. `game_engine.py` にハンドラー登録
4. 適切なログ出力とエラーハンドリング

---

**🎉 現在プレイ可能！ `python main.py` でお試しください！**