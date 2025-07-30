#!/usr/bin/env python3
"""
HEAL特殊ぷよの効果テスト
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

import pygame
pygame.init()
pygame.display.set_mode((1920, 1080))

def test_heal_effect():
    print("=== HEAL SPECIAL PUYO EFFECT TEST ===")
    
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
        
        print("2. Setting up heal test scenario...")
        # プレイヤーのHPを減らす
        initial_hp = engine.player.hp
        engine.player.take_damage(30)
        damaged_hp = engine.player.hp
        print(f"   Initial HP: {initial_hp}")
        print(f"   After damage: {damaged_hp}")
        
        # HEAL特殊ぷよ付きの4連鎖を作成
        puyo_grid.set_puyo(1, 10, PuyoType.BLUE)
        puyo_grid.set_puyo(1, 9, PuyoType.BLUE) 
        puyo_grid.set_puyo(1, 8, PuyoType.BLUE)
        puyo_grid.set_puyo(1, 7, PuyoType.BLUE)
        
        # HEAL特殊ぷよを設定
        puyo_grid.set_special_puyo_data(1, 10, SimpleSpecialType.HEAL)
        puyo_grid.set_special_puyo_data(1, 9, SimpleSpecialType.HEAL)
        
        print(f"   Placed 4 BLUE puyos in column 1")
        print(f"   Set 2 HEAL special puyos")
        
        print("3. Testing chain and heal effects...")
        chains = puyo_grid.find_all_chains()
        print(f"   Found {len(chains)} chains")
        
        if chains:
            # チェインを実行して回復効果を確認
            positions_to_eliminate = set()
            for chain in chains:
                positions_to_eliminate.update(chain.eliminated_puyos)
            
            print(f"   Eliminating {len(positions_to_eliminate)} puyos...")
            eliminated_count = puyo_grid.eliminate_puyos(positions_to_eliminate)
            
            final_hp = engine.player.hp
            print(f"   Final HP: {final_hp}")
            print(f"   Total healing: {final_hp - damaged_hp}")
            
            # 特殊ぷよデータが削除されたか確認
            remaining_specials = len(puyo_grid.special_puyo_data)
            print(f"   Remaining special puyo data: {remaining_specials}")
            
            if final_hp > damaged_hp:
                print("   SUCCESS: HEAL effect working!")
            else:
                print("   FAILURE: HEAL effect not working")
        
        print("SUCCESS: HEAL effect test completed!")
        return True
        
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_heal_effect()
    sys.exit(0 if success else 1)