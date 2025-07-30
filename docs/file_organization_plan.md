# ファイル整理計画

## 現在の問題
- 直下フォルダに80以上のファイルが散乱
- テストファイル、デバッグファイル、アセット、分析スクリプトが混在
- プロジェクト構造が不明瞭

## 新しいフォルダ構造

### tests/
- すべてのtest_*.pyファイル
- テスト関連のスクリプト

### debug/
- debug_*.py, debug_*.png
- デバッグ用の分析ファイル

### assets/
- 画像ファイル（.png, .jpg）
- 音声ファイル（.mp3）
- 既存のassetsフォルダと統合

### docs/
- ドキュメントファイル（.md, .pdf）
- 既存のドキュメントをここに統合

### tools/
- 分析スクリプト（analyze_*.py）
- ユーティリティスクリプト

### legacy/
- 古いUnity関連ファイル（Scripts/, Scenes/, Prefabs/）
- main_complete.py等の旧バージョン

### temp/
- 一時ファイル
- UUIDファイル名のもの

## 移動対象ファイル一覧

### tests/ フォルダへ移動
- test_*.py (約40ファイル)

### debug/ フォルダへ移動  
- debug_*.py, debug_*.png
- quick_game_test.py

### assets/ フォルダへ移動
- *.png, *.mp3 (画像・音声ファイル)
- 既存のPicture/, SE/フォルダの内容も統合

### docs/ フォルダへ移動
- *.md, *.pdf
- ARCHITECTURE.md, README*.md, PLAYTEST_GUIDE.md

### tools/ フォルダへ移動
- analyze_*.py
- balance_adjustment_proposal.py
- font_test*.py

### legacy/ フォルダへ移動
- Scripts/, Scenes/, Prefabs/, Materials/
- main_complete.py

## 保持するファイル（直下）
- main.py
- requirements.txt
- CLAUDE.md
- src/ フォルダ