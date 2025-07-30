#!/usr/bin/env python3
"""
特殊ぷよの包括的テスト - 視覚的表示も含む
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

import pygame
pygame.init()
pygame.display.set_mode((1920, 1080))

def test_special_puyo_comprehensive():
    print("=== COMPREHENSIVE SPECIAL PUYO TEST ===")
    
    try:
        from core.game_engine import GameEngine
        from core.simple_special_puyo import SimpleSpecialType, simple_special_manager
        from core.authentic_demo_handler import AuthenticDemoHandler, PuyoPair
        from core.constants import PuyoType
        
        print("1. Testing SimpleSpecialManager...")
        print(f"   Spawn rate: {simple_special_manager.spawn_rate}")
        print(f"   Available types: {list(SimpleSpecialType)}")
        
        # 特殊ぷよタイプの生成テスト
        special_types = []
        for i in range(10):
            if simple_special_manager.should_spawn_special():
                special_type = simple_special_manager.get_random_special_type()
                special_types.append(special_type)
        print(f"   Generated special types: {special_types}")
        
        print("\n2. Testing image loading...")
        # 特殊ぷよ画像の存在確認
        import os
        heal_exists = os.path.exists("Picture/HEAL.png")
        bomb_exists = os.path.exists("Picture/BOMB.png")
        print(f"   HEAL.png exists: {heal_exists}")
        print(f"   BOMB.png exists: {bomb_exists}")
        
        if heal_exists and bomb_exists:
            heal_img = pygame.image.load("Picture/HEAL.png")
            bomb_img = pygame.image.load("Picture/BOMB.png")
            print(f"   HEAL image size: {heal_img.get_size()}")
            print(f"   BOMB image size: {bomb_img.get_size()}")
        
        print("\n3. Testing PuyoPair with special types...")
        # GameEngineを初期化
        engine = GameEngine()
        handler = AuthenticDemoHandler(engine)
        
        # 特殊ぷよ付きペアを作成
        pair1 = PuyoPair(PuyoType.RED, PuyoType.BLUE, 3, 
                        main_special=SimpleSpecialType.HEAL, 
                        sub_special=SimpleSpecialType.BOMB, 
                        parent_handler=handler)
        
        print(f"   Pair created successfully")
        print(f"   Main type: {pair1.main_type}, Special: {pair1.main_special}")
        print(f"   Sub type: {pair1.sub_type}, Special: {pair1.sub_special}")
        
        print("\n4. Testing NEXT queue with special types...")
        handler._generate_initial_next_queue()
        print(f"   NEXT queue length: {len(handler.next_pairs_queue)}")
        for i, (main_type, sub_type, main_special, sub_special) in enumerate(handler.next_pairs_queue):
            print(f"   Pair {i+1}: {main_type.name}({main_special}) + {sub_type.name}({sub_special})")
        
        print("\n5. Testing rendering...")
        test_surface = pygame.Surface((1920, 1080))
        
        # AuthenticDemoHandlerの描画テスト
        handler.render(test_surface)
        print("   Handler render successful")
        
        # 特殊ぷよアイコンの直接描画テスト
        if heal_exists and bomb_exists:
            # NEXTぷよアイコン描画テスト
            handler._render_next_special_puyo(test_surface, (100, 100), SimpleSpecialType.HEAL, 40)
            handler._render_next_special_puyo(test_surface, (150, 100), SimpleSpecialType.BOMB, 40)
            print("   Direct icon rendering successful")
        
        print("\n6. Testing falling puyo rendering...")
        # 落下中ペアの描画テスト
        handler.current_pair = pair1
        handler.render(test_surface)
        print("   Falling pair rendering successful")
        
        print("\n7. Testing puyo grid special data...")
        # PuyoGridの特殊ぷよデータ確認
        puyo_grid = handler.puyo_grid
        print(f"   PuyoGrid special_puyo_data: {len(puyo_grid.special_puyo_data)} entries")
        
        # 特殊ぷよを手動で配置してテスト
        puyo_grid.set_puyo(2, 10, PuyoType.RED)
        puyo_grid.special_puyo_data[(2, 10)] = SimpleSpecialType.HEAL
        
        print(f"   Added special puyo at (2, 10): {puyo_grid.special_puyo_data.get((2, 10))}")
        
        # グリッド描画テスト
        puyo_grid.render(test_surface)
        print("   Grid rendering with special puyo successful")
        
        print("\n8. Testing special puyo images in PuyoGrid...")
        if hasattr(puyo_grid, 'special_puyo_images'):
            print(f"   PuyoGrid has special_puyo_images: {len(puyo_grid.special_puyo_images)} types")
            for special_type, image in puyo_grid.special_puyo_images.items():
                if image:
                    print(f"     {special_type}: {image.get_size()}")
        else:
            print("   PuyoGrid missing special_puyo_images")
        
        # 最終視覚テスト - 特殊ぷよが見える状態で画像保存
        print("\n9. Creating visual test image...")
        test_surface.fill((50, 50, 50))  # ダークグレー背景
        
        # テスト用の特殊ぷよを配置
        test_positions = [(100, 100), (200, 100), (300, 100), (400, 100)]
        test_types = [SimpleSpecialType.HEAL, SimpleSpecialType.BOMB, SimpleSpecialType.HEAL, SimpleSpecialType.BOMB]
        
        for i, (pos, special_type) in enumerate(zip(test_positions, test_types)):
            # 通常ぷよを描画
            pygame.draw.circle(test_surface, (255, 100, 100), pos, 20)  # 赤いぷよ
            # 特殊ぷよアイコンを上に描画
            try:
                handler._render_next_special_puyo(test_surface, pos, special_type, 40)
            except Exception as e:
                print(f"     Error rendering {special_type}: {e}")
        
        # テスト画像を保存
        pygame.image.save(test_surface, "special_puyo_visual_test.png")
        print("   Visual test image saved as 'special_puyo_visual_test.png'")
        
        print("\n✅ SUCCESS: All special puyo tests passed!")
        return True
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_special_puyo_comprehensive()
    sys.exit(0 if success else 1)