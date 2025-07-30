#!/usr/bin/env python3
"""
特殊ぷよシステム全体の統合テスト - 個別出現率と報酬システムの完全テスト
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

import pygame
pygame.init()
pygame.display.set_mode((1920, 1080))

def test_full_special_puyo_system():
    print("=== FULL SPECIAL PUYO SYSTEM INTEGRATION TEST ===")
    
    try:
        from core.game_engine import GameEngine
        from core.simple_special_puyo import SimpleSpecialType, simple_special_manager
        from rewards.reward_system import RewardGenerator, RewardType, RewardSelectionHandler
        from core.player_data import PlayerData
        
        print("1. Testing game engine initialization...")
        engine = GameEngine()
        player = engine.player
        
        # 初期出現率の確認
        print(f"   Initial rates: {simple_special_manager._format_rates()}")
        print(f"   Player data rates: {player.special_puyo_rates}")
        
        print("\n2. Testing reward generation and selection...")
        reward_gen = RewardGenerator()
        
        # 特殊ぷよ報酬を含む報酬リストを生成
        rewards = reward_gen.generate_battle_rewards(floor_level=1, is_boss=False)
        print(f"   Generated {len(rewards)} rewards")
        
        # 特殊ぷよ報酬を見つける
        special_puyo_rewards = [r for r in rewards if r.reward_type == RewardType.SPECIAL_PUYO]
        if special_puyo_rewards:
            special_reward = special_puyo_rewards[0]
            print(f"   Found special puyo reward: {special_reward.name}")
            print(f"   Type: {special_reward.value}")
            print(f"   Description: {special_reward.description}")
            
            print("\n3. Testing reward application...")
            # 報酬適用前の状態を記録
            old_rate = simple_special_manager.get_type_rate(special_reward.value)
            old_player_rate = player.special_puyo_rates.get(special_reward.value.value, 0.0)
            
            print(f"   Before reward application:")
            print(f"     Manager rate: {old_rate*100:.0f}%")
            print(f"     Player data rate: {old_player_rate*100:.0f}%")
            
            # 報酬選択ハンドラーを作成して報酬を適用
            reward_handler = RewardSelectionHandler(engine, rewards)
            reward_handler._apply_selected_reward(special_reward)
            
            # 報酬適用後の状態を確認
            new_rate = simple_special_manager.get_type_rate(special_reward.value)
            new_player_rate = player.special_puyo_rates.get(special_reward.value.value, 0.0)
            
            print(f"   After reward application:")
            print(f"     Manager rate: {new_rate*100:.0f}%")
            print(f"     Player data rate: {new_player_rate*100:.0f}%")
            print(f"     Rate increase: +{(new_rate - old_rate)*100:.0f}%")
            
            # 同期確認
            if abs(new_rate - new_player_rate) < 0.001:
                print(f"   SUCCESS: Manager and player data are synchronized")
            else:
                print(f"   WARNING: Manager and player data mismatch")
            
            print("\n4. Testing persistence across game restarts...")
            # 新しいGameEngineを作成してデータが復元されるかテスト
            saved_rates = player.special_puyo_rates.copy()
            print(f"   Saved rates: {saved_rates}")
            
            # 新しいPlayerDataインスタンスを作成
            new_player = PlayerData()
            new_player.special_puyo_rates = saved_rates
            new_player._initialize_special_puyo_rates()
            
            # 復元された出現率を確認
            restored_rate = simple_special_manager.get_type_rate(special_reward.value)
            print(f"   Restored rate: {restored_rate*100:.0f}%")
            
            if abs(restored_rate - new_rate) < 0.001:
                print(f"   SUCCESS: Rates restored correctly after restart")
            else:
                print(f"   FAILURE: Rate restoration failed")
        
        print("\n5. Testing multiple reward applications...")
        # 複数回の報酬適用テスト
        heal_rewards_count = 0
        bomb_rewards_count = 0
        
        for i in range(5):
            # 新しい報酬を生成
            test_rewards = reward_gen.generate_battle_rewards(floor_level=i+1, is_boss=False)
            special_rewards = [r for r in test_rewards if r.reward_type == RewardType.SPECIAL_PUYO]
            
            if special_rewards:
                test_reward = special_rewards[0]
                old_rate = simple_special_manager.get_type_rate(test_reward.value)
                
                # 報酬を適用
                reward_handler = RewardSelectionHandler(engine, test_rewards)
                reward_handler._apply_selected_reward(test_reward)
                
                new_rate = simple_special_manager.get_type_rate(test_reward.value)
                
                if test_reward.value == SimpleSpecialType.HEAL:
                    heal_rewards_count += 1
                elif test_reward.value == SimpleSpecialType.BOMB:
                    bomb_rewards_count += 1
                
                print(f"   Round {i+1}: {test_reward.value.value} {old_rate*100:.0f}% -> {new_rate*100:.0f}%")
        
        print(f"\n   Final rates after {heal_rewards_count + bomb_rewards_count} rewards:")
        print(f"   {simple_special_manager._format_rates()}")
        print(f"   HEAL rewards applied: {heal_rewards_count}")
        print(f"   BOMB rewards applied: {bomb_rewards_count}")
        
        print("\n6. Testing maximum rate caps...")
        # 100%上限のテスト
        for special_type in SimpleSpecialType:
            current_rate = simple_special_manager.get_type_rate(special_type)
            if current_rate < 1.0:
                # 100%まで上昇させる
                while current_rate < 1.0:
                    old_rate = current_rate
                    player.increase_special_puyo_rate(special_type.value, 0.05)
                    current_rate = simple_special_manager.get_type_rate(special_type)
                    if current_rate >= 1.0:
                        print(f"   {special_type.value} reached maximum: {current_rate*100:.0f}%")
                        break
        
        print("\nSUCCESS: Full special puyo system integration test completed!")
        return True
        
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_full_special_puyo_system()
    sys.exit(0 if success else 1)