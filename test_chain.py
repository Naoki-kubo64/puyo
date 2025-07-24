"""
連鎖システムのテスト用スクリプト
"""

import sys
import os
import logging

# パス設定
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.puzzle.puyo_grid import PuyoGrid, PuyoType

def test_basic_chain():
    """基本的な連鎖をテスト"""
    print("=== 基本連鎖テスト ===")
    
    grid = PuyoGrid()
    
    # 4個の赤ぷよで基本連鎖を作成
    grid.set_puyo(0, 11, PuyoType.RED)  # 底
    grid.set_puyo(0, 10, PuyoType.RED)
    grid.set_puyo(0, 9, PuyoType.RED)
    grid.set_puyo(1, 11, PuyoType.RED)  # 横に1個
    
    print("設置前のグリッド:")
    print_grid(grid)
    
    # 連鎖実行
    score, eliminated = grid.execute_full_chain_sequence()
    
    print(f"結果: スコア={score}, 消去数={eliminated}")
    print("連鎖後のグリッド:")
    print_grid(grid)
    print()

def test_two_level_chain():
    """2連鎖をテスト"""
    print("=== 2連鎖テスト ===")
    
    grid = PuyoGrid()
    
    # 正しい2連鎖パターンを作成
    # 底層に青4個（これが最初に消える）
    grid.set_puyo(0, 11, PuyoType.BLUE)
    grid.set_puyo(1, 11, PuyoType.BLUE)
    grid.set_puyo(2, 11, PuyoType.BLUE)
    grid.set_puyo(3, 11, PuyoType.BLUE)
    
    # その上に赤3個（青が消えると下に落ちる）
    grid.set_puyo(0, 10, PuyoType.RED)
    grid.set_puyo(1, 10, PuyoType.RED)
    grid.set_puyo(2, 10, PuyoType.RED)
    
    # さらに上に赤1個（落下すると4個になって連鎖）
    grid.set_puyo(3, 10, PuyoType.RED)
    
    # 分離のために別の場所に緑を配置
    grid.set_puyo(4, 11, PuyoType.GREEN)
    grid.set_puyo(5, 11, PuyoType.GREEN)
    
    print("設置前のグリッド:")
    print_grid(grid)
    
    # 段階的にテスト
    print("連鎖検出テスト:")
    chains = grid.find_all_chains() 
    print(f"発見された連鎖数: {len(chains)}")
    for i, chain in enumerate(chains):
        print(f"  連鎖{i+1}: {chain.chain_type.name}, 個数: {chain.puyo_count}")
    
    # 手動で段階的にテスト
    print("\n段階的連鎖テスト:")
    
    # 1段階目
    print("1段階目実行前:")
    print_grid(grid)
    
    score1, elim1 = grid.execute_chain_elimination()
    print(f"1段階目結果: スコア={score1}, 消去数={elim1}")
    print("1段階目実行後:")
    print_grid(grid)
    
    # 手動で重力テスト
    print("\n手動重力テスト:")
    gravity_applied = grid.apply_gravity()
    print(f"重力適用結果: {gravity_applied}")
    print("重力適用後:")
    print_grid(grid)
    
    # 2段階目 
    print("\n2段階目実行前:")
    chains2 = grid.find_all_chains()
    print(f"発見された連鎖数: {len(chains2)}")
    for i, chain in enumerate(chains2):
        print(f"  連鎖{i+1}: {chain.chain_type.name}, 個数: {chain.puyo_count}")
    
    if chains2:
        score2, elim2 = grid.execute_chain_elimination()
        print(f"2段階目結果: スコア={score2}, 消去数={elim2}")
        print("2段階目実行後:")
        print_grid(grid)
    print()

def print_grid(grid: PuyoGrid):
    """グリッドを視覚的に表示"""
    type_chars = {
        PuyoType.EMPTY: '.',
        PuyoType.RED: 'R',
        PuyoType.BLUE: 'B',
        PuyoType.GREEN: 'G',
        PuyoType.YELLOW: 'Y',
        PuyoType.PURPLE: 'P',
        PuyoType.ORANGE: 'O',
        PuyoType.CYAN: 'C',
        PuyoType.GARBAGE: 'X',
    }
    
    for y in range(grid.height):
        row = []
        for x in range(grid.width):
            puyo_type = grid.get_puyo(x, y)
            row.append(type_chars[puyo_type])
        print(''.join(row))

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    test_basic_chain()
    test_two_level_chain()
    
    print("連鎖テスト完了!")