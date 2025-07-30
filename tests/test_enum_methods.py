#!/usr/bin/env python3
"""
Enumメソッドの詳細テスト
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_enum_methods():
    print("=== TESTING ENUM METHODS IN DETAIL ===")
    
    try:
        from core.simple_special_puyo import SimpleSpecialType
        
        # 個別にテスト
        test_type = SimpleSpecialType.HEAL
        print(f"Testing type: {test_type}")
        print(f"Type value: {test_type.value}")
        
        # メソッド呼び出しテスト
        try:
            display_name = test_type.get_display_name()
            print(f"Display name: {display_name}")
        except Exception as e:
            print(f"ERROR in get_display_name: {e}")
            import traceback
            traceback.print_exc()
            return False
        
        try:
            description = test_type.get_description()
            print(f"Description: {description}")
        except Exception as e:
            print(f"ERROR in get_description: {e}")
            import traceback
            traceback.print_exc()
            return False
        
        # すべてのタイプをテスト
        print("\nTesting all types:")
        for puyo_type in SimpleSpecialType:
            try:
                name = puyo_type.get_display_name()
                desc = puyo_type.get_description()
                print(f"  {puyo_type.value}: OK")
            except Exception as e:
                print(f"  {puyo_type.value}: ERROR - {e}")
                return False
        
        # 報酬システムでの使用をテスト
        print("\nTesting in reward context:")
        from rewards.reward_system import RewardGenerator, RewardType
        
        gen = RewardGenerator()
        
        # 複数回テスト
        for i in range(3):
            try:
                reward = gen._generate_specific_reward(RewardType.SPECIAL_PUYO, 1)
                if reward:
                    puyo_type = reward.value
                    print(f"  Generated: {puyo_type.value}")
                    print(f"  Name: {reward.name}")
                    print(f"  Using get_display_name(): {puyo_type.get_display_name()}")
                else:
                    print(f"  No reward generated on attempt {i+1}")
            except Exception as e:
                print(f"  ERROR in reward generation {i+1}: {e}")
                import traceback
                traceback.print_exc()
                return False
        
        return True
        
    except Exception as e:
        print(f"CRITICAL ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_enum_methods()
    print(f"\nResult: {'PASS' if success else 'FAIL'}")
    sys.exit(0 if success else 1)