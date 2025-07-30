/*
 * PUYO ROGUE - セットアップガイド
 * 
 * このファイルはセットアップ手順を記載したコメントファイルです。
 * 実際のゲームには不要ですが、開発の参考として残しています。
 */

/*
【Unityでの最小構成セットアップ】

1. 新しい2Dプロジェクトを作成

2. 以下のGameObjectを作成:

   ■ GameManager (Empty GameObject)
     - BattleManager.cs をアタッチ
     - Player.cs をアタッチ  
     - Enemy.cs をアタッチ

   ■ PuzzleSystem (Empty GameObject)
     - PuzzleGrid.cs をアタッチ
     - PuzzleManager.cs をアタッチ

   ■ UI Canvas
     - BattleUI.cs をアタッチ
     - 以下のUIエレメントを子オブジェクトとして配置:
       * PlayerHealthBar (Slider)
       * EnemyHealthBar (Slider) 
       * EnemyTimer (Text - TextMeshPro)
       * ChainInfo (Text - TextMeshPro)
       * DamageText (Text - TextMeshPro)

3. プレハブ作成:
   
   ■ Puyo Prefab
     - Sphere プリミティブから作成
     - Collider不要なら削除

   ■ FallingPuyo Prefab  
     - Empty GameObjectに FallingPuyo.cs をアタッチ

4. GameConfig作成:
   - Assets右クリック → Create → Puyo Rogue → Game Config

5. 参照を設定:
   - BattleManager: すべてのコンポーネント参照を設定
   - PuzzleGrid: puyoPrefab と GameConfig を設定
   - PuzzleManager: grid, fallingPuyoPrefab, GameConfig を設定
   - BattleUI: 各UIエレメント参照を設定

【最小テスト用設定値】
- Grid: 6x12
- セルサイズ: 1.0
- 落下速度: 2.0
- 連鎖最小: 4個
- プレイヤーHP: 100
- 敵HP: 80
- 敵攻撃間隔: 3秒

【操作テスト】
矢印キーでぷよを操作し、4個以上つなげて連鎖を発生させる
連鎖によって敵にダメージが入り、敵は時間経過で攻撃してくる

【トラブルシューティング】
- NullReferenceError → 参照設定を確認
- ぷよが表示されない → puyoPrefab設定を確認  
- UIが動かない → Canvas設定とUI参照を確認
- 連鎖が発生しない → minimumChainLength設定を確認
*/