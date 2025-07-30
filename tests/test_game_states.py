#!/usr/bin/env python3
"""
ゲーム状態テスト - エラーを捕捉
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

import pygame
import traceback

def test_game_initialization():
    """ゲーム初期化をテスト"""
    print("=== TESTING GAME INITIALIZATION ===")
    
    try:
        pygame.init()
        
        from core.game_engine import GameEngine
        from core.constants import GameState
        from core.menu_handler import MenuHandler
        
        print("[OK] Imports successful")
        
        # GameEngineを作成
        engine = GameEngine()
        print("[OK] GameEngine created")
        
        # MenuHandlerを作成
        menu_handler = MenuHandler(engine)
        print("[OK] MenuHandler created")
        
        # 状態ハンドラーを登録
        engine.register_state_handler(GameState.MENU, menu_handler)
        print("[OK] MenuHandler registered")
        
        return True
        
    except Exception as e:
        print(f"[FAIL] Game initialization error: {e}")
        traceback.print_exc()
        return False

def test_battle_initialization():
    """戦闘初期化をテスト"""
    print("\n=== TESTING BATTLE INITIALIZATION ===")
    
    try:
        from core.game_engine import GameEngine
        from battle.battle_handler import BattleHandler
        
        engine = GameEngine()
        print("[OK] GameEngine created")
        
        # BattleHandlerを作成
        battle_handler = BattleHandler(engine, floor_level=1)
        print("[OK] BattleHandler created")
        
        # メソッドの存在確認
        methods_to_check = ['_check_battle_result', 'handle_event', 'update', 'render']
        for method in methods_to_check:
            if hasattr(battle_handler, method):
                print(f"[OK] Method {method} exists")
            else:
                print(f"[FAIL] Method {method} missing")
                return False
        
        return True
        
    except Exception as e:
        print(f"[FAIL] Battle initialization error: {e}")
        traceback.print_exc()
        return False

def test_special_puyo_integration():
    """特殊ぷよ統合をテスト"""
    print("\n=== TESTING SPECIAL PUYO INTEGRATION ===")
    
    try:
        from core.game_engine import GameEngine
        from core.simple_special_puyo import SimpleSpecialType, simple_special_manager
        
        engine = GameEngine()
        print("[OK] GameEngine with special puyo system created")
        
        # プレイヤーの特殊ぷよデータを確認
        special_rates = engine.player.special_puyo_rates
        print(f"[OK] Player special puyo rates: {len(special_rates)} types")
        
        # 各特殊ぷよタイプの名前を取得
        for puyo_type in SimpleSpecialType:
            try:
                name = puyo_type.get_display_name()
                print(f"[OK] {puyo_type.value} -> {name}")
            except Exception as e:
                print(f"[FAIL] Error getting name for {puyo_type.value}: {e}")
                return False
        
        return True
        
    except Exception as e:
        print(f"[FAIL] Special puyo integration error: {e}")
        traceback.print_exc()
        return False

def test_reward_integration():
    """報酬統合をテスト"""
    print("\n=== TESTING REWARD INTEGRATION ===")
    
    try:
        from rewards.reward_system import RewardGenerator, RewardType
        from rewards.battle_reward_handler import BattleRewardHandler
        from core.game_engine import GameEngine
        
        engine = GameEngine()
        reward_gen = RewardGenerator()
        print("[OK] Systems created")
        
        # 特殊ぷよ報酬を生成
        reward = reward_gen._generate_specific_reward(RewardType.SPECIAL_PUYO, 1)
        if reward:
            print(f"[OK] Generated reward: {reward.name}")
            print(f"[OK] Reward type: {type(reward.value)}")
            
            # BattleRewardHandlerでの処理をテスト
            reward_handler = BattleRewardHandler(engine)
            
            # _apply_rewardメソッドが存在するかチェック（プライベートメソッド）
            if hasattr(reward_handler, '_apply_reward'):
                print("[OK] _apply_reward method exists")
                
                # 実際に適用してみる（安全にテスト）
                try:
                    # 報酬適用をテスト（実際には適用しない、表示名の確認のみ）
                    puyo_type = reward.value
                    display_name = puyo_type.get_display_name()
                    print(f"[OK] Would apply reward: {display_name}")
                except Exception as e:
                    print(f"[FAIL] Error in reward application: {e}")
                    return False
            else:
                print("[FAIL] _apply_reward method missing")
                return False
        else:
            print("[WARNING] No reward generated")
        
        return True
        
    except Exception as e:
        print(f"[FAIL] Reward integration error: {e}")
        traceback.print_exc()
        return False

def main():
    """メイン実行"""
    print("Starting game state testing...")
    
    success = True
    success &= test_game_initialization()
    success &= test_battle_initialization()
    success &= test_special_puyo_integration()
    success &= test_reward_integration()
    
    print(f"\n=== FINAL RESULT ===")
    if success:
        print("All game state tests passed!")
    else:
        print("Some tests failed - errors detected!")
    
    return success

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\nTest interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"CRITICAL TEST ERROR: {e}")
        traceback.print_exc()
        sys.exit(1)