#!/usr/bin/env python3
"""
特殊ぷよの名前表示修正テスト
固有名前が正しく表示されるかの確認用
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

import pygame
pygame.init()

def test_special_puyo_names():
    print("=== TESTING SPECIAL PUYO NAME DISPLAY ===")
    
    try:
        from core.simple_special_puyo import SimpleSpecialType
        from core.game_engine import GameEngine
        from rewards.reward_system import RewardGenerator, RewardType
        
        print("1. Testing SimpleSpecialType display names...")
        
        # すべての特殊ぷよタイプをテスト
        expected_names = {
            SimpleSpecialType.HEAL: "ヒールぷよ",
            SimpleSpecialType.BOMB: "ボムぷよ",
            SimpleSpecialType.LIGHTNING: "サンダーぷよ",
            SimpleSpecialType.SHIELD: "シールドぷよ",
            SimpleSpecialType.MULTIPLIER: "パワーぷよ",
            SimpleSpecialType.POISON: "ポイズンぷよ"
        }
        
        for puyo_type, expected_name in expected_names.items():
            actual_name = puyo_type.get_display_name()
            if actual_name == expected_name:
                print(f"   [OK] {puyo_type.value} -> {actual_name}")
            else:
                print(f"   [FAIL] {puyo_type.value} -> Expected: {expected_name}, Got: {actual_name}")
                return False
        
        print("2. Testing descriptions...")
        expected_descriptions = {
            SimpleSpecialType.HEAL: "プレイヤーのHPを10回復",
            SimpleSpecialType.BOMB: "全ての敵に攻撃",
            SimpleSpecialType.LIGHTNING: "最強の敵1体に強力攻撃",
            SimpleSpecialType.SHIELD: "ダメージを15軽減",
            SimpleSpecialType.MULTIPLIER: "攻撃力を50%上昇",
            SimpleSpecialType.POISON: "全ての敵に継続ダメージ"
        }
        
        for puyo_type, expected_desc in expected_descriptions.items():
            actual_desc = puyo_type.get_description()
            if actual_desc == expected_desc:
                print(f"   [OK] {puyo_type.value} description correct")
            else:
                print(f"   [FAIL] {puyo_type.value} -> Expected: {expected_desc}, Got: {actual_desc}")
                return False
        
        print("3. Testing reward generation...")
        engine = GameEngine()
        reward_gen = RewardGenerator()
        
        # 特殊ぷよ報酬を生成してテスト
        for i in range(5):
            reward = reward_gen._generate_specific_reward(RewardType.SPECIAL_PUYO, 1)
            if reward:
                puyo_type = reward.value
                display_name = puyo_type.get_display_name()
                if display_name in expected_names.values():
                    print(f"   [OK] Generated reward: {reward.name} (type: {puyo_type.value})")
                else:
                    print(f"   [FAIL] Invalid reward name: {reward.name}")
                    return False
            else:
                print(f"   [WARNING] No reward generated on attempt {i+1}")
        
        print("4. Testing top UI bar effects...")
        from core.top_ui_bar import TopUIBar
        
        top_ui_bar = TopUIBar(engine.fonts)
        
        # 各特殊ぷよタイプのツールチップテスト
        for puyo_type in SimpleSpecialType:
            # hover_info をシミュレート
            top_ui_bar.hover_info = {
                'type': puyo_type.value,
                'rate': 0.3,
                'pos': (100, 100)
            }
            
            # 描画をテスト（エラーが起きないかチェック）
            test_surface = pygame.Surface((1920, 1080))
            try:
                top_ui_bar._draw_hover_tooltip(test_surface)
                print(f"   [OK] Tooltip for {puyo_type.value} renders without error")
            except Exception as e:
                print(f"   [FAIL] Tooltip error for {puyo_type.value}: {e}")
                return False
        
        return True
        
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_special_puyo_names()
    print(f"\nTest {'PASSED' if success else 'FAILED'}")
    sys.exit(0 if success else 1)