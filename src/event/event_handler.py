import pygame
import random
from typing import List, Dict, Callable, Optional
from core.state_handler import StateHandler
from core.constants import GameState, Colors, NodeType
from core.game_engine import GameEngine
from dungeon.dungeon_node import DungeonNode

class EventChoice:
    def __init__(self, text: str, effect: Callable, description: str = ""):
        self.text = text
        self.description = description
        self.effect = effect

class RandomEvent:
    def __init__(self, title: str, description: str, choices: List[EventChoice]):
        self.title = title
        self.description = description
        self.choices = choices

class EventHandler(StateHandler):
    def __init__(self, engine: GameEngine, current_node: Optional[DungeonNode] = None):
        super().__init__(engine)
        self.current_node = current_node
        self.current_event: Optional[RandomEvent] = None
        self.font_large = pygame.font.Font(None, 48)
        self.font_medium = pygame.font.Font(None, 36)
        self.font_small = pygame.font.Font(None, 28)
        self.choice_rects: List[pygame.Rect] = []
        self.hovered_choice = -1
        self.event_completed = False
        
        # Generate random event
        self._generate_event()
    
    def _generate_event(self):
        """Generate a random event with choices"""
        events = [
            self._create_mysterious_shrine_event(),
            self._create_wandering_merchant_event(),
            self._create_cursed_fountain_event(),
            self._create_ancient_library_event(),
            self._create_golden_idol_event()
        ]
        
        self.current_event = random.choice(events)
    
    def _create_mysterious_shrine_event(self) -> RandomEvent:
        """謎の祠イベント"""
        def pray_effect():
            # ランダムに HP回復 or スキル強化 or 呪い
            roll = random.randint(1, 3)
            if roll == 1:
                heal_amount = random.randint(15, 25)
                self.engine.player.heal(heal_amount)
                self._show_result(f"祠の力で {heal_amount} HP回復した！")
            elif roll == 2:
                self.engine.player.max_hp += 5
                self.engine.player.chain_damage_multiplier += 0.1
                self._show_result("祠の加護を受けた！最大HP+5、連鎖ダメージ+10%")
            else:
                curse_damage = random.randint(8, 12)
                self.engine.player.take_damage(curse_damage)
                self._show_result(f"祠の呪いを受けた... {curse_damage}ダメージ")
        
        def ignore_effect():
            # 何も起こらない
            self._show_result("何も起こらなかった。安全な選択だった。")
        
        def steal_effect():
            # 確実にダメージを受けるが、ゴールドを得る
            damage = random.randint(5, 10)
            gold = random.randint(80, 120)
            self.engine.player.take_damage(damage)
            self.engine.player.gold += gold
            self._show_result(f"祠の宝を盗んだ！{gold}ゴールドを得たが {damage}ダメージを受けた")
        
        return RandomEvent(
            "謎の祠",
            "古い祠を発見した。中央に光る宝珠があり、\n神秘的な力を感じる...",
            [
                EventChoice("祈りを捧げる", pray_effect, "祠に祈る（ランダム効果）"),
                EventChoice("立ち去る", ignore_effect, "何もせずに去る"),
                EventChoice("宝珠を盗む", steal_effect, "ダメージを受けるがゴールドを得る")
            ]
        )
    
    def _create_wandering_merchant_event(self) -> RandomEvent:
        """行商人イベント"""
        def buy_potion_effect():
            cost = 40
            if self.engine.player.gold >= cost:
                self.engine.player.gold -= cost
                self.engine.player.heal(30)
                self._show_result(f"ポーションを購入！30HP回復（-{cost}ゴールド）")
            else:
                self._show_result("ゴールドが足りない...")
        
        def buy_blessing_effect():
            cost = 60
            if self.engine.player.gold >= cost:
                self.engine.player.gold -= cost
                self.engine.player.max_hp += 8
                self._show_result(f"祝福を購入！最大HP+8（-{cost}ゴールド）")
            else:
                self._show_result("ゴールドが足りない...")
        
        def rob_effect():
            # 強盗を試みる：成功すればアイテム、失敗すればダメージ
            if random.random() < 0.4:  # 40%成功率
                gold = random.randint(60, 100)
                self.engine.player.gold += gold
                self._show_result(f"強盗成功！{gold}ゴールドを奪った！")
            else:
                damage = random.randint(12, 18)
                self.engine.player.take_damage(damage)
                self._show_result(f"強盗失敗！商人に反撃され {damage}ダメージ")
        
        return RandomEvent(
            "行商人",
            "親切そうな行商人に出会った。\n様々な品物を売っているようだ。",
            [
                EventChoice("体力ポーション(40G)", buy_potion_effect, "30HP回復"),
                EventChoice("祝福のお守り(60G)", buy_blessing_effect, "最大HP+8"),
                EventChoice("強盗する", rob_effect, "リスクを冒してゴールドを奪う")
            ]
        )
    
    def _create_cursed_fountain_event(self) -> RandomEvent:
        """呪いの泉イベント"""
        def drink_effect():
            # 50%で大回復、50%で毒
            if random.random() < 0.5:
                heal_amount = random.randint(25, 40)
                self.engine.player.heal(heal_amount)
                self._show_result(f"清浄な水だった！{heal_amount}HP回復")
            else:
                damage = random.randint(15, 20)
                self.engine.player.take_damage(damage)
                self._show_result(f"呪われた水だった... {damage}ダメージ")
        
        def purify_effect():
            # ゴールドを使って安全に浄化
            cost = 30
            if self.engine.player.gold >= cost:
                self.engine.player.gold -= cost
                heal_amount = 20
                self.engine.player.heal(heal_amount)
                self._show_result(f"泉を浄化！{heal_amount}HP回復（-{cost}ゴールド）")
            else:
                self._show_result("浄化に必要なゴールドが足りない...")
        
        def ignore_effect():
            self._show_result("泉を避けて通り過ぎた。")
        
        return RandomEvent(
            "呪いの泉",
            "不気味に光る泉を発見した。\n水面には邪悪な気配が漂っている...",
            [
                EventChoice("水を飲む", drink_effect, "ギャンブル（回復 or ダメージ）"),
                EventChoice("浄化する(30G)", purify_effect, "安全に回復する"),
                EventChoice("無視する", ignore_effect, "何もしない")
            ]
        )
    
    def _create_ancient_library_event(self) -> RandomEvent:
        """古代図書館イベント"""
        def study_effect():
            # 知識を得てスキル強化
            self.engine.player.chain_damage_multiplier += 0.15
            self.engine.player.energy += 1
            self._show_result("古代の知識を習得！連鎖ダメージ+15%、エネルギー+1")
        
        def rest_effect():
            # 読書で休憩
            heal_amount = random.randint(12, 18)
            self.engine.player.heal(heal_amount)
            self._show_result(f"静かな環境で休憩した。{heal_amount}HP回復")
        
        def search_effect():
            # 宝探し
            if random.random() < 0.7:  # 70%成功
                gold = random.randint(50, 80)
                self.engine.player.gold += gold
                self._show_result(f"隠された宝を発見！{gold}ゴールド獲得")
            else:
                damage = 8
                self.engine.player.take_damage(damage)
                self._show_result(f"罠にかかった！{damage}ダメージ")
        
        return RandomEvent(
            "古代図書館",
            "埃をかぶった古い図書館を発見した。\n貴重な知識が眠っているかもしれない。",
            [
                EventChoice("魔法書を研究", study_effect, "スキル強化を得る"),
                EventChoice("静かに休憩", rest_effect, "HP回復"),
                EventChoice("宝を探す", search_effect, "リスクありでゴールド獲得")
            ]
        )
    
    def _create_golden_idol_event(self) -> RandomEvent:
        """黄金の偶像イベント"""
        def take_effect():
            # 呪いと引き換えに大金
            gold = random.randint(120, 180)
            curse_damage = random.randint(10, 15)
            self.engine.player.gold += gold
            self.engine.player.take_damage(curse_damage)
            self.engine.player.max_hp -= 3  # 永続的な呪い
            self._show_result(f"偶像を奪った！{gold}ゴールド獲得したが呪いを受けた（-3最大HP、{curse_damage}ダメージ）")
        
        def worship_effect():
            # 偶像を崇拝して加護を得る
            self.engine.player.max_hp += 10
            heal_amount = 15
            self.engine.player.heal(heal_amount)
            self._show_result(f"偶像の加護を受けた！最大HP+10、{heal_amount}HP回復")
        
        def leave_effect():
            # 何もしない
            bonus_gold = 20  # 善行の報い
            self.engine.player.gold += bonus_gold
            self._show_result(f"偶像に手を触れずに立ち去った。善行の報いで{bonus_gold}ゴールド獲得")
        
        return RandomEvent(
            "黄金の偶像",
            "眩しく輝く黄金の偶像が祭壇に置かれている。\n莫大な価値がありそうだが、何か禍々しい気配も...",
            [
                EventChoice("偶像を奪う", take_effect, "大金を得るが呪いを受ける"),
                EventChoice("偶像を崇拝", worship_effect, "加護を受ける"),
                EventChoice("立ち去る", leave_effect, "何もしない")
            ]
        )
    
    def _show_result(self, message: str):
        """結果メッセージを表示して完了状態にする"""
        self.result_message = message
        self.event_completed = True
    
    def handle_event(self, event: pygame.event.Event) -> bool:
        if event.type == pygame.MOUSEMOTION:
            self.hovered_choice = -1
            mouse_pos = pygame.mouse.get_pos()
            for i, rect in enumerate(self.choice_rects):
                if rect.collidepoint(mouse_pos):
                    self.hovered_choice = i
                    break
        
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left click
                if self.event_completed:
                    # イベント完了後、マップに戻る
                    if hasattr(self.engine, 'change_state'):
                        self.engine.change_state(GameState.DUNGEON_MAP)
                    return True
                
                mouse_pos = pygame.mouse.get_pos()
                for i, rect in enumerate(self.choice_rects):
                    if rect.collidepoint(mouse_pos):
                        # 選択肢の効果を実行
                        if self.current_event and i < len(self.current_event.choices):
                            self.current_event.choices[i].effect()
                        return True
        
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                if hasattr(self.engine, 'change_state'):
                    self.engine.change_state(GameState.DUNGEON_MAP)
                return True
        
        return False
    
    def update(self, dt: float):
        pass
    
    def render(self, screen: pygame.Surface):
        screen.fill(Colors.DARK_BLUE)
        
        if not self.current_event:
            return
        
        # イベント完了後の結果表示
        if self.event_completed:
            self._render_result(screen)
            return
        
        # タイトル
        title_text = self.font_large.render(self.current_event.title, True, Colors.GOLD)
        title_rect = title_text.get_rect(center=(screen.get_width() // 2, 100))
        screen.blit(title_text, title_rect)
        
        # 説明文
        description_lines = self.current_event.description.split('\n')
        y_offset = 180
        for line in description_lines:
            desc_text = self.font_medium.render(line, True, Colors.WHITE)
            desc_rect = desc_text.get_rect(center=(screen.get_width() // 2, y_offset))
            screen.blit(desc_text, desc_rect)
            y_offset += 40
        
        # 選択肢
        self.choice_rects.clear()
        y_offset = 320
        
        for i, choice in enumerate(self.current_event.choices):
            # 選択肢のボタン
            button_width = 500
            button_height = 60
            button_x = (screen.get_width() - button_width) // 2
            button_y = y_offset
            
            button_rect = pygame.Rect(button_x, button_y, button_width, button_height)
            self.choice_rects.append(button_rect)
            
            # ホバー効果
            button_color = Colors.GOLD if i == self.hovered_choice else Colors.GRAY
            pygame.draw.rect(screen, button_color, button_rect)
            pygame.draw.rect(screen, Colors.WHITE, button_rect, 2)
            
            # 選択肢テキスト
            choice_text = self.font_medium.render(choice.text, True, Colors.BLACK)
            choice_rect = choice_text.get_rect(center=button_rect.center)
            screen.blit(choice_text, choice_rect)
            
            # 説明テキスト（小さく）
            if choice.description:
                desc_text = self.font_small.render(choice.description, True, Colors.LIGHT_GRAY)
                desc_rect = desc_text.get_rect(center=(button_rect.centerx, button_rect.bottom + 15))
                screen.blit(desc_text, desc_rect)
            
            y_offset += 100
        
        # プレイヤー情報表示
        self._render_player_info(screen)
    
    def _render_result(self, screen: pygame.Surface):
        """イベント結果画面"""
        # 背景
        overlay = pygame.Surface(screen.get_size())
        overlay.fill(Colors.BLACK)
        overlay.set_alpha(128)
        screen.blit(overlay, (0, 0))
        
        # 結果メッセージ
        result_lines = self.result_message.split('\n')
        y_offset = screen.get_height() // 2 - len(result_lines) * 20
        
        for line in result_lines:
            result_text = self.font_medium.render(line, True, Colors.GOLD)
            result_rect = result_text.get_rect(center=(screen.get_width() // 2, y_offset))
            screen.blit(result_text, result_rect)
            y_offset += 40
        
        # 続行指示
        continue_text = self.font_small.render("クリックして続ける", True, Colors.WHITE)
        continue_rect = continue_text.get_rect(center=(screen.get_width() // 2, screen.get_height() - 80))
        screen.blit(continue_text, continue_rect)
        
        # プレイヤー情報表示
        self._render_player_info(screen)
    
    def _render_player_info(self, screen: pygame.Surface):
        """プレイヤー情報を画面上部に表示"""
        info_y = 20
        
        # HP
        hp_text = f"HP: {self.engine.player.hp}/{self.engine.player.max_hp}"
        hp_surface = self.font_small.render(hp_text, True, Colors.RED)
        screen.blit(hp_surface, (20, info_y))
        
        # ゴールド
        gold_text = f"ゴールド: {self.engine.player.gold}"
        gold_surface = self.font_small.render(gold_text, True, Colors.GOLD)
        screen.blit(gold_surface, (200, info_y))
        
        # エネルギー
        energy_text = f"エネルギー: {self.engine.player.energy}"
        energy_surface = self.font_small.render(energy_text, True, Colors.BLUE)
        screen.blit(energy_surface, (380, info_y))