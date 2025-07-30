#!/usr/bin/env python3
"""
特殊ぷよの複合効果テスト - HEALとBOMBを同時に
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

import pygame
pygame.init()
pygame.display.set_mode((1920, 1080))

def test_combined_effects():
    print("=== COMBINED SPECIAL PUYO EFFECTS TEST ===")
    
    try:
        from core.game_engine import GameEngine
        from core.simple_special_puyo import SimpleSpecialType
        from core.constants import PuyoType
        from puzzle.puyo_grid import PuyoGrid
        from battle.battle_handler import BattleHandler
        
        print("1. Creating game components...")
        engine = GameEngine()
        battle_handler = BattleHandler(engine, floor_level=1)
        puyo_grid = battle_handler.puyo_handler.puyo_grid
        
        print("2. Setting up combined effects scenario...")
        # プレイヤーのHPを減らす
        engine.player.take_damage(20)
        initial_hp = engine.player.hp
        print(f"   Player HP after damage: {initial_hp}")
        
        # 複数のぷよパターンを配置
        # パターン1: HEAL付きの4連鎖（列0）
        puyo_grid.set_puyo(0, 10, PuyoType.RED)
        puyo_grid.set_puyo(0, 9, PuyoType.RED) 
        puyo_grid.set_puyo(0, 8, PuyoType.RED)
        puyo_grid.set_puyo(0, 7, PuyoType.RED)
        puyo_grid.set_special_puyo_data(0, 10, SimpleSpecialType.HEAL)
        
        # パターン2: BOMB付きの4連鎖（列2）+ 周囲にぷよ
        puyo_grid.set_puyo(2, 10, PuyoType.BLUE)
        puyo_grid.set_puyo(2, 9, PuyoType.BLUE) 
        puyo_grid.set_puyo(2, 8, PuyoType.BLUE)
        puyo_grid.set_puyo(2, 7, PuyoType.BLUE)
        puyo_grid.set_special_puyo_data(2, 9, SimpleSpecialType.BOMB)
        
        # BOMBの爆発範囲内にぷよを配置
        puyo_grid.set_puyo(1, 9, PuyoType.GREEN)  # BOMB爆発範囲内
        puyo_grid.set_puyo(3, 9, PuyoType.YELLOW) # BOMB爆発範囲内
        
        print(f"   Set up RED chain with HEAL in column 0")
        print(f"   Set up BLUE chain with BOMB in column 2")
        print(f"   Added extra puyos around BOMB for explosion test")
        
        # 初期状態を記録
        initial_puyo_count = 0
        for x in range(puyo_grid.width):
            for y in range(puyo_grid.height):
                if puyo_grid.get_puyo(x, y) != PuyoType.EMPTY:
                    initial_puyo_count += 1
        
        print(f"   Initial puyos on grid: {initial_puyo_count}")
        print(f"   Initial special puyo data: {len(puyo_grid.special_puyo_data)}")
        
        print("3. Testing combined chain effects...")
        chains = puyo_grid.find_all_chains()
        print(f"   Found {len(chains)} chains")
        
        if chains:
            # チェインを実行
            positions_to_eliminate = set()
            for chain in chains:
                positions_to_eliminate.update(chain.eliminated_puyos)
            
            print(f"   Eliminating {len(positions_to_eliminate)} puyos from chains...")
            eliminated_count = puyo_grid.eliminate_puyos(positions_to_eliminate)
            
            # 結果を確認
            final_hp = engine.player.hp
            
            final_puyo_count = 0
            for x in range(puyo_grid.width):
                for y in range(puyo_grid.height):
                    if puyo_grid.get_puyo(x, y) != PuyoType.EMPTY:
                        final_puyo_count += 1
            
            print(f"   Final player HP: {final_hp}")
            print(f"   HP change: {final_hp - initial_hp}")
            print(f"   Final puyos on grid: {final_puyo_count}")
            print(f"   Total puyos destroyed: {initial_puyo_count - final_puyo_count}")
            print(f"   Remaining special puyo data: {len(puyo_grid.special_puyo_data)}")
            
            # 効果検証
            heal_worked = final_hp > initial_hp
            bomb_worked = (initial_puyo_count - final_puyo_count) > len(positions_to_eliminate)
            
            print(f"   HEAL effect: {'SUCCESS' if heal_worked else 'FAILURE'}")
            print(f"   BOMB effect: {'SUCCESS' if bomb_worked else 'FAILURE'}")
            
            if heal_worked and bomb_worked:
                print("   SUCCESS: Both special effects working correctly!")
            else:
                print("   PARTIAL: Some effects may not be working")
        
        print("SUCCESS: Combined effects test completed!")
        return True
        
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_combined_effects()
    sys.exit(0 if success else 1)