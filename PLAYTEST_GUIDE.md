# プレイテストガイド

## 1. Unityプロジェクトセットアップ

### Step 1: 新しいUnityプロジェクト作成
1. Unity Hub を開く
2. 「新規作成」→「2D (Core)」テンプレートを選択
3. プロジェクト名: "PuyoRogue"
4. 保存場所を選択して「作成」

**重要**: Unity 2022.3 LTS以降を使用してください（新しいAPIに対応済み）

### Step 2: スクリプトファイルをインポート
1. Unityプロジェクトの `Assets` フォルダを開く
2. 生成された `Scripts` フォルダ全体を `Assets` フォルダにコピー
3. Unityエディタで自動的にスクリプトがコンパイルされるのを待つ

**注意**: 新しいUnityバージョンでの警告・エラーは修正済みです。

## 2. ゲームオブジェクト作成

### Step 3: GameConfigアセット作成
1. Project窓で右クリック
2. `Create` → `Puyo Rogue` → `Game Config`
3. 名前を "MainGameConfig" に変更

### Step 4: 基本シーン構築

#### A. GameManager作成
1. Hierarchy で右クリック → `Create Empty`
2. 名前を "GameManager" に変更
3. 以下のコンポーネントを追加:
   - `BattleManager`
   - `Player` 
   - `Enemy`

#### B. PuzzleSystem作成
1. Hierarchy で右クリック → `Create Empty`
2. 名前を "PuzzleSystem" に変更
3. 子オブジェクトとして2つのEmpty GameObjectを作成:
   - "Grid" (PuzzleGrid.cs をアタッチ)
   - "Manager" (PuzzleManager.cs をアタッチ)

#### C. UI Canvas作成
1. Hierarchy で右クリック → `UI` → `Canvas`
2. Canvas に `BattleUI` コンポーネントを追加
3. Canvas の子オブジェクトとして以下を作成:
   - `UI` → `Slider` (名前: PlayerHealthBar)
   - `UI` → `Slider` (名前: EnemyHealthBar)  
   - `UI` → `Text - TextMeshPro` (名前: EnemyTimer)
   - `UI` → `Text - TextMeshPro` (名前: ChainInfo)
   - `UI` → `Text - TextMeshPro` (名前: DamageText)

## 3. プレハブ作成

### Step 5: Puyoプレハブ
1. Hierarchy で右クリック → `3D Object` → `Sphere`
2. 名前を "Puyo" に変更
3. Transform をリセット (Position: 0,0,0)
4. Sphere Collider コンポーネントを削除（不要）
5. Project窓に新しいフォルダ "Prefabs" を作成
6. Puyo オブジェクトを Prefabs フォルダにドラッグしてプレハブ化
7. Hierarchy の Puyo オブジェクトを削除

### Step 6: FallingPuyoプレハブ
1. Hierarchy で右クリック → `Create Empty`
2. 名前を "FallingPuyo" に変更
3. `FallingPuyo` コンポーネントを追加
4. Prefabs フォルダにドラッグしてプレハブ化
5. Hierarchy の FallingPuyo オブジェクトを削除

## 4. コンポーネント設定

### Step 7: 参照設定

#### BattleManager設定
1. GameManager を選択
2. BattleManager コンポーネントで以下を設定:
   - Player: GameManager 自身
   - Enemy: GameManager 自身  
   - Puzzle Manager: PuzzleSystem/Manager
   - Battle UI: Canvas
   - Config: MainGameConfig

#### PuzzleGrid設定
1. PuzzleSystem/Grid を選択
2. PuzzleGrid コンポーネントで以下を設定:
   - Config: MainGameConfig
   - Grid Parent: PuzzleSystem/Grid 自身
   - Puyo Prefab: Prefabs/Puyo

#### PuzzleManager設定
1. PuzzleSystem/Manager を選択
2. PuzzleManager コンポーネントで以下を設定:
   - Grid: PuzzleSystem/Grid
   - Falling Puyo Prefab: Prefabs/FallingPuyo
   - Config: MainGameConfig

#### BattleUI設定
1. Canvas を選択
2. BattleUI コンポーネントで以下を設定:
   - Player Health Bar: PlayerHealthBar
   - Player Health Text: PlayerHealthBar/Handle Slide Area/Handle 下のText
   - Enemy Health Bar: EnemyHealthBar
   - Enemy Health Text: EnemyHealthBar/Handle Slide Area/Handle 下のText
   - Enemy Attack Timer: EnemyTimer
   - Chain Count Text: ChainInfo
   - Damage Text: DamageText

## 5. カメラ位置調整

### Step 8: Main Camera設定
1. Main Camera を選択
2. Transform コンポーネントで Position を (3, 6, -10) に設定
3. ゲームビューでグリッド全体が見えるように調整

## 6. プレイテスト実行

### Step 9: ぷよを見えるようにする（重要！）
1. Unity メニューバー → `Puyo Rogue` → `Create Puyo Materials`
2. 「Create All Puyo Materials」をクリック
3. 「Update Puyo Prefab with Red Material」をクリック

### Step 10: ゲーム開始
1. Unity エディタで Play ボタンを押す
2. **カラフルな球体（ぷよ）**が上から落下開始

### Step 11: 操作テスト
- **左右矢印キー**: ぷよを左右に移動
- **上矢印キー**: ぷよを回転
- **下矢印キー**: ぷよを高速落下

### Step 12: 連鎖テスト
1. 同じ色のぷよを4個以上隣接させる
2. ぷよが消えて敵にダメージが入ることを確認
3. 連続で連鎖が発生することを確認

## 7. 確認項目チェックリスト

### ✅ 基本動作
- [ ] ぷよが2個組みで落下する
- [ ] 矢印キーで操作できる
- [ ] グリッドの底で着地する
- [ ] 新しいぷよが次々と生成される

### ✅ パズル機能
- [ ] 同色4個以上で消去される
- [ ] 重力で上のぷよが落下する
- [ ] 連続連鎖が発生する
- [ ] グリッド上部まで積み上がるとゲームオーバー

### ✅ 戦闘システム
- [ ] 連鎖でダメージが敵に入る
- [ ] 敵が時間経過で攻撃してくる
- [ ] プレイヤーのHPが減る
- [ ] 敵を倒すと勝利

### ✅ UI表示
- [ ] プレイヤーHPバーが正しく表示
- [ ] 敵HPバーが正しく表示
- [ ] 敵の攻撃タイマーが表示
- [ ] 連鎖情報が表示
- [ ] ダメージ数値が表示

## 8. トラブルシューティング

### よくある問題と解決方法

#### ぷよが表示されない
- Puyo プレハブの参照が正しく設定されているか確認
- Material が設定されているか確認
- カメラの位置を調整

#### 操作が効かない
- FallingPuyo スクリプトが正しくアタッチされているか確認
- Input System の設定を確認

#### UIが表示されない
- Canvas の Render Mode が "Screen Space - Overlay" になっているか確認
- UI要素の参照が正しく設定されているか確認

#### 連鎖が発生しない
- GameConfig の minimumChainLength が 4 に設定されているか確認
- PuzzleGrid の参照が正しく設定されているか確認

#### NullReferenceException
- 各コンポーネントの参照設定をすべて確認
- GameConfig アセットが作成・設定されているか確認

## 9. デバッグ用Console確認

Play中にConsole窓で以下のメッセージが表示されるか確認:
- "Battle started - Stage 1"
- "Chain completed: ..."
- "Player took X damage. HP: ..."
- "Enemy took X damage. HP: ..."

これらが表示されていれば、システムは正常に動作しています。