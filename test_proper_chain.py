"""
真の連鎖システムのテスト - 段階的連鎖
"""

import sys
import os
import logging

# パス設定
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.puzzle.puyo_grid import PuyoGrid, PuyoType

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

def test_true_two_chain():
    """真の2連鎖をテスト"""
    print("=== 真の2連鎖テスト ===")
    
    grid = PuyoGrid()
    
    # 簡単な縦2連鎖パターン
    # 底層: 青4個（横に並べる）
    grid.set_puyo(1, 11, PuyoType.BLUE)
    grid.set_puyo(2, 11, PuyoType.BLUE)
    grid.set_puyo(3, 11, PuyoType.BLUE)
    grid.set_puyo(4, 11, PuyoType.BLUE)
    
    # その上: 赤3個（青が消えると落下）
    grid.set_puyo(1, 10, PuyoType.RED)
    grid.set_puyo(2, 10, PuyoType.RED)
    grid.set_puyo(3, 10, PuyoType.RED)
    
    # さらに上: 赤1個（落下すると縦4個になって連鎖）
    grid.set_puyo(1, 9, PuyoType.RED)
    
    # 邪魔ぷよ（連鎖を分離するため）
    grid.set_puyo(0, 11, PuyoType.GREEN)
    grid.set_puyo(5, 11, PuyoType.GREEN)
    
    print("設置前のグリッド:")
    print_grid(grid)
    print()
    
    # 段階的実行
    total_score = 0
    chain_level = 0
    
    while True:
        # 重力適用
        gravity_applied = grid.apply_gravity()
        print(f"重力適用: {gravity_applied}")
        if gravity_applied:
            print("重力適用後:")
            print_grid(grid)
            print()
        
        # 連鎖検出
        chains = grid.find_all_chains()
        if not chains:
            print("連鎖終了")
            break
        
        chain_level += 1
        print(f"=== 連鎖レベル {chain_level} ===")
        print(f"発見された連鎖数: {len(chains)}")
        for i, chain in enumerate(chains):
            print(f"  連鎖{i+1}: {chain.chain_type.name}, 個数: {chain.puyo_count}")
        
        # 連鎖実行
        level_score = 0
        level_eliminated = 0
        
        for chain in chains:
            eliminated_count = grid.eliminate_puyos(chain.eliminated_puyos)
            level_score += chain.score
            level_eliminated += eliminated_count
            print(f"消去: {eliminated_count} {chain.chain_type.name} puyos")
        
        # 連鎖倍率適用
        from src.core.constants import CHAIN_MULTIPLIER
        chain_bonus = int(level_score * (CHAIN_MULTIPLIER ** (chain_level - 1)))
        total_score += chain_bonus
        
        print(f"レベル {chain_level} スコア: {chain_bonus}")
        print("消去後:")
        print_grid(grid)
        print()
    
    print(f"最終結果 - 総スコア: {total_score}, 連鎖レベル: {chain_level}")

if __name__ == "__main__":
    logging.basicConfig(level=logging.WARNING)  # ログを抑制
    
    test_true_two_chain()
    
    print("真の連鎖テスト完了!")