#!/usr/bin/env python3
"""
ゲームバランス調整案とテスト
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

import pygame
pygame.init()

import math

class BalanceProposal:
    """ゲームバランス調整提案"""
    
    def __init__(self):
        # 現在の設定値
        self.current_hp_scale = 1.25
        self.current_dmg_scale = 1.15
        self.current_speed_scale = 0.92
        
        # 調整案の設定値
        self.proposed_hp_scale = 1.15    # より緩やかな成長
        self.proposed_dmg_scale = 1.10   # より緩やかな成長
        self.proposed_speed_scale = 0.95 # より緩やかな加速
        
        # 基本値
        self.base_hp = 20
        self.base_dmg = 8
        self.base_interval = 6.0
        
        # プレイヤー設定
        self.player_max_hp = 100
    
    def calculate_enemy_stats(self, floor, use_proposed=False):
        """フロアレベルに応じた敵ステータス計算"""
        if use_proposed:
            hp_scale = self.proposed_hp_scale
            dmg_scale = self.proposed_dmg_scale
            speed_scale = self.proposed_speed_scale
        else:
            hp_scale = self.current_hp_scale
            dmg_scale = self.current_dmg_scale
            speed_scale = self.current_speed_scale
        
        # フロア1からスケーリング開始
        scale_factor = floor - 1
        
        hp = int(self.base_hp * (hp_scale ** scale_factor))
        dmg = int(self.base_dmg * (dmg_scale ** scale_factor))
        interval = self.base_interval * (speed_scale ** scale_factor)
        
        return hp, dmg, interval
    
    def calculate_survival_time(self, enemy_dmg, enemy_interval):
        """プレイヤーの生存時間計算"""
        attacks_to_kill = math.ceil(self.player_max_hp / enemy_dmg)
        return attacks_to_kill * enemy_interval
    
    def analyze_balance(self, max_floor=10):
        """バランス分析"""
        print("=== BALANCE COMPARISON ===\\n")
        
        print("Floor | Current Stats        | Proposed Stats       | Survival Time Comparison")
        print("------|---------------------|----------------------|-------------------------")
        
        for floor in range(1, max_floor + 1):
            # 現在の設定
            current_hp, current_dmg, current_interval = self.calculate_enemy_stats(floor, False)
            current_survival = self.calculate_survival_time(current_dmg, current_interval)
            
            # 提案の設定
            proposed_hp, proposed_dmg, proposed_interval = self.calculate_enemy_stats(floor, True)
            proposed_survival = self.calculate_survival_time(proposed_dmg, proposed_interval)
            
            print(f"  {floor:2d}  | HP:{current_hp:3d} DMG:{current_dmg:2d} I:{current_interval:4.1f} | HP:{proposed_hp:3d} DMG:{proposed_dmg:2d} I:{proposed_interval:4.1f} | {current_survival:5.1f}s -> {proposed_survival:5.1f}s")
    
    def analyze_chain_effectiveness(self):
        """連鎖効果の分析"""
        print("\\n=== CHAIN EFFECTIVENESS ANALYSIS ===\\n")
        
        # 連鎖ダメージ設定（実際のゲームから）
        chain_damages = [4, 8, 12, 20, 30, 50]
        chain_names = ["2連鎖", "3連鎖", "4連鎖", "5連鎖", "6連鎖", "7連鎖+"]
        
        print("Floor | Enemy HP | Hits needed for each chain type")
        print("------|----------|", end="")
        for name in chain_names:
            print(f" {name:6s}", end="")
        print()
        
        for floor in [1, 3, 5, 7, 10]:
            proposed_hp, _, _ = self.calculate_enemy_stats(floor, True)
            print(f"  {floor:2d}  |   {proposed_hp:3d}    |", end="")
            
            for damage in chain_damages:
                hits_needed = math.ceil(proposed_hp / damage)
                print(f"   {hits_needed:2d}  ", end="")
            print()
    
    def evaluate_improvements(self):
        """改善点の評価"""
        print("\\n=== IMPROVEMENT EVALUATION ===\\n")
        
        # フロア10での比較
        current_hp, current_dmg, current_interval = self.calculate_enemy_stats(10, False)
        proposed_hp, proposed_dmg, proposed_interval = self.calculate_enemy_stats(10, True)
        
        current_survival = self.calculate_survival_time(current_dmg, current_interval)
        proposed_survival = self.calculate_survival_time(proposed_dmg, proposed_interval)
        
        print(f"Floor 10 比較:")
        print(f"  現在設定:   HP={current_hp:3d}, DMG={current_dmg:2d}, 生存時間={current_survival:5.1f}秒")
        print(f"  調整案:     HP={proposed_hp:3d}, DMG={proposed_dmg:2d}, 生存時間={proposed_survival:5.1f}秒")
        print()
        
        # 改善ポイント
        hp_reduction = (current_hp - proposed_hp) / current_hp * 100
        dmg_reduction = (current_dmg - proposed_dmg) / current_dmg * 100
        survival_improvement = (proposed_survival - current_survival) / current_survival * 100
        
        print(f"改善効果:")
        print(f"  - 敵HP: {hp_reduction:5.1f}% 削減")
        print(f"  - 敵攻撃力: {dmg_reduction:5.1f}% 削減")
        print(f"  - 生存時間: {survival_improvement:5.1f}% 改善")
        
        # 連鎖の実用性評価
        print(f"\\n連鎖の実用性:")
        for damage, name in zip([4, 8, 12, 20], ["小連鎖", "中連鎖", "大連鎖", "巨大連鎖"]):
            current_hits = math.ceil(current_hp / damage)
            proposed_hits = math.ceil(proposed_hp / damage)
            print(f"  {name:6s}: {current_hits:2d}回 -> {proposed_hits:2d}回 ({current_hits-proposed_hits:+d})")

def main():
    """メイン関数"""
    balancer = BalanceProposal()
    
    print("GAME BALANCE ADJUSTMENT PROPOSAL")
    print("=" * 50)
    
    balancer.analyze_balance()
    balancer.analyze_chain_effectiveness()
    balancer.evaluate_improvements()
    
    print("\\n=== RECOMMENDATION ===")
    print("提案するスケーリング調整:")
    print(f"  - HP成長率: {balancer.current_hp_scale} -> {balancer.proposed_hp_scale} (より緩やか)")
    print(f"  - 攻撃力成長率: {balancer.current_dmg_scale} -> {balancer.proposed_dmg_scale} (より緩やか)")
    print(f"  - 攻撃速度成長率: {balancer.current_speed_scale} -> {balancer.proposed_speed_scale} (より緩やか)")
    print()
    print("期待される効果:")
    print("  - 後半フロアでも連鎖戦略が有効")
    print("  - プレイヤーに十分な思考時間を提供")
    print("  - 段階的な難易度上昇でスキル成長を促進")

if __name__ == "__main__":
    main()