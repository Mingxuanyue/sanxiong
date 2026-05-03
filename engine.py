# -*- coding: utf-8 -*-
"""
三雄争锋 - 游戏逻辑引擎（无渲染依赖）
翻译自 三雄争锋v3.cpp，保留所有特殊机制
"""
import random
import time
from enum import Enum, auto
from dataclasses import dataclass, field
from typing import List, Optional, Tuple, Callable

# ====================================================================
# 枚举
# ====================================================================
class Suit(Enum):
    SPADE   = 0
    HEART   = 1
    CLUB    = 2
    DIAMOND = 3
    JOKER   = 4

class Rank(Enum):
    A  = 1;  R2 = 2;  R3 = 3;  R4 = 4;  R5 = 5
    R6 = 6;  R7 = 7;  R8 = 8;  R9 = 9;  R10= 10
    J  = 11; Q  = 12; K  = 13
    SMALL_JOKER = 100
    BIG_JOKER   = 101

class Rule(Enum):
    BIG_WINS   = 0
    SMALL_WINS = 1

# ====================================================================
# 常量字符串
# ====================================================================
RANK_STR = {
    Rank.A:'A', Rank.R2:'2', Rank.R3:'3', Rank.R4:'4', Rank.R5:'5',
    Rank.R6:'6', Rank.R7:'7', Rank.R8:'8', Rank.R9:'9', Rank.R10:'10',
    Rank.J:'J', Rank.Q:'Q', Rank.K:'K',
    Rank.SMALL_JOKER:'小王', Rank.BIG_JOKER:'大王',
}
SUIT_STR = {
    Suit.SPADE:'♠', Suit.HEART:'♥', Suit.CLUB:'♣',
    Suit.DIAMOND:'♦', Suit.JOKER:'',
}

# ====================================================================
# Card 数据类
# ====================================================================
@dataclass
class Card:
    suit: Suit
    rank: Rank
    is_returned: bool = False   # 被5号牌收回，下回合打出不触发连顺

    @property
    def is_joker(self) -> bool:
        return self.rank in (Rank.SMALL_JOKER, Rank.BIG_JOKER)

    def compare_value(self, rule: Rule) -> int:
        """返回比较值，用于判断大小。Joker永远最强。"""
        if self.rank == Rank.BIG_JOKER:
            return 2000 if rule == Rule.BIG_WINS else -2000
        if self.rank == Rank.SMALL_JOKER:
            return 1900 if rule == Rule.BIG_WINS else -1900
        v = self.rank.value
        # 比大：A最小(1)，K最大(13)
        # 比小：A最优(最小值1)，K最差(最大值13) — 统一用原始值，排序时反向
        return v

    @property
    def rank_str(self) -> str:
        return RANK_STR[self.rank]

    @property
    def suit_str(self) -> str:
        return SUIT_STR[self.suit]

    def __repr__(self):
        if self.is_joker:
            return self.rank_str
        return f"{self.suit_str}{self.rank_str}"

    def __eq__(self, other):
        if not isinstance(other, Card): return False
        return self.suit == other.suit and self.rank == other.rank

    def __hash__(self):
        return hash((self.suit, self.rank))


# ====================================================================
# Player 数据类
# ====================================================================
@dataclass
class Player:
    name: str
    is_human: bool
    is_strategic: bool = True    # True=策略AI，False=随机AI
    hand: List[Card] = field(default_factory=list)
    score: int = 0
    big_joker_uses: int = 0
    small_joker_uses: int = 0

    def add_card(self, c: Card):
        self.hand.append(c)

    def add_card_random(self, c: Card, rng: random.Random) -> int:
        """将新牌随机插入手牌，避免固定追加到末尾造成可预测性。"""
        if not self.hand:
            self.hand.append(c)
            return 0
        pos = rng.randint(0, len(self.hand))
        self.hand.insert(pos, c)
        return pos

    def remove_card(self, idx: int) -> Card:
        return self.hand.pop(idx)

    def remove_specific(self, c: Card) -> Optional[Card]:
        for i, h in enumerate(self.hand):
            if h.suit == c.suit and h.rank == c.rank:
                return self.hand.pop(i)
        return None

    def find_five(self, exclude_idx: int = -1) -> int:
        """返回第一张5号牌的索引，不存在返回-1"""
        for i, c in enumerate(self.hand):
            if i == exclude_idx:
                continue
            if not c.is_joker and c.rank == Rank.R5:
                return i
        return -1

    def has_big_joker(self) -> bool:
        return any(c.rank == Rank.BIG_JOKER for c in self.hand)

    def has_small_joker(self) -> bool:
        return any(c.rank == Rank.SMALL_JOKER for c in self.hand)

    def can_use_big_joker(self) -> bool:
        return self.has_big_joker() and self.big_joker_uses < 2

    def can_use_small_joker(self) -> bool:
        return self.has_small_joker() and self.small_joker_uses < 1

    def has_spade_a(self) -> bool:
        return any(c.rank == Rank.A and c.suit == Suit.SPADE for c in self.hand)

    def reset_joker_uses(self):
        self.big_joker_uses = 0
        self.small_joker_uses = 0


# ====================================================================
# 游戏事件类型（供渲染层使用）
# ====================================================================
class EvType(Enum):
    MSG            = auto()   # 普通消息日志
    ROUND_START    = auto()   # 回合开始
    FIVE_RETURN    = auto()   # 5号牌归还 data=(pidx, card)
    AI_PLAYED      = auto()   # AI出牌完成 data=(pidx, card_idx)
    HUMAN_PLAY_REQ = auto()   # 请求人类出牌
    REVEAL_CARDS   = auto()   # 同时开牌 data=table_cards[3]
    SCORE_UPDATE   = auto()   # 计分 data=scores[3]
    BONUS_SCORE    = auto()   # 补分 data=(pidx, bonus)
    RULE_FLIP      = auto()   # 规则翻转 data=new_rule
    CONSECUTIVE    = auto()   # 连顺触发
    TEN_MECHANISM  = auto()   # 出10触发
    TEN_TAKE_CARD  = auto()   # 出10方收走别人的牌 data={'from':i,'to':tp,'card':c}
    TEN_SELF_DISCARD=auto()   # 出10方自弃 data={'pidx':p,'card':c,'facedown':True}
    TEN_BLIND_DISCARD=auto()  # 出10下家盲弃 data={'pidx':p,'target':tp,'card':c,'facedown':False}
    FIVE_ACTIVATE  = auto()   # 5号牌激活 data=pidx
    DRAW_START     = auto()   # 连顺抽牌开始
    DRAW_ACTION    = auto()   # 单次抽牌 data=(from_pidx, target_pidx, card or None)
    PEEK_REQ       = auto()   # 小王偷窥请求 data=(from_pidx, target_pidx)
    PEEK_RESULT    = auto()   # 偷窥结果（仅人类触发时）data=(from_pidx, cards)
    DEFEND_REQ     = auto()   # 大王防御请求 data=(target_pidx, chosen, offset)
    DEFEND_RESULT  = auto()   # 大王防御结果 data=(did_defend, new_chosen)
    TIEBREAKER     = auto()   # 进入加赛
    GAME_OVER      = auto()   # 游戏结束
    SHOW_RESULT    = auto()   # 本局结果面板（阻塞，等待点击）data={'scores':[3], 'round':n}
    SHOW_INFO      = auto()   # 信息提示框（阻塞，等待点击）data={'type':str, ...}
    WAIT_ANIM      = auto()   # 等待动画播完后自动继续（无需玩家点击）

@dataclass
class GameEvent:
    type: EvType
    data: object = None
    msg: str = ""


# ====================================================================
# 游戏引擎核心
# ====================================================================
class GameEngine:
    """
    纯逻辑引擎，不含任何渲染代码。
    所有需要人类交互的地方调用 self._ask_human(event)，
    渲染层通过设置 on_event / ask_human 回调来接收/处理。
    """

    def __init__(self):
        self.players: List[Player] = [
            Player("你",       is_human=True,  is_strategic=False),
            Player("玩家2(AI)", is_human=False, is_strategic=True),
            Player("玩家3(AI)", is_human=False, is_strategic=False),
        ]
        self.deck: List[Card] = []
        self.rule = Rule.BIG_WINS
        self.round_num = 1
        self.game_mode = 0        # 0=单局 1=达标分
        self.target_score = 60
        self.consecutive_game = False
        self.scene_count = 1
        self.last_two_way_tie = False
        self.skip_mode_select = False
        self.quit_to_menu = False

        # 5号牌待归还
        self.five_return_pending: List[bool] = [False, False, False]
        self.five_return_card: List[Optional[Card]] = [None, None, None]

        # 本轮桌面牌（供渲染层读取）
        self.table_cards: List[Optional[Card]] = [None, None, None]
        self.played_idx: List[int] = [-1, -1, -1]
        self.table_revealed: bool = False

        # 消息日志
        self.msg_log: List[str] = []

        self._rng = random.Random(int(time.time()))

        # ---- 回调钩子（渲染层注入）----
        # on_event(GameEvent) -> None   — 渲染层处理事件（动画/音效/UI刷新）
        # ask_human(GameEvent) -> int/bool — 渲染层处理需要人类输入的请求，返回结果
        self.on_event: Callable[[GameEvent], None] = lambda e: None
        self.ask_human: Callable[[GameEvent], object] = lambda e: None

    # ----------------------------------------------------------------
    # 内部辅助
    # ----------------------------------------------------------------
    def _emit(self, ev_type: EvType, data=None, msg=""):
        e = GameEvent(ev_type, data, msg)
        if msg:
            self.msg_log.append(msg)
            if len(self.msg_log) > 8:
                self.msg_log.pop(0)
        self.on_event(e)

    def _ask(self, ev_type: EvType, data=None) -> object:
        """向渲染层请求人类输入，阻塞直到返回结果"""
        return self.ask_human(GameEvent(ev_type, data))

    # ----------------------------------------------------------------
    # 牌组操作
    # ----------------------------------------------------------------
    def init_deck(self):
        self.deck = []
        for s in [Suit.SPADE, Suit.HEART, Suit.CLUB, Suit.DIAMOND]:
            for r in [Rank.A, Rank.R2, Rank.R3, Rank.R4, Rank.R5,
                      Rank.R6, Rank.R7, Rank.R8, Rank.R9, Rank.R10,
                      Rank.J, Rank.Q, Rank.K]:
                self.deck.append(Card(s, r))
        self.deck.append(Card(Suit.JOKER, Rank.SMALL_JOKER))
        self.deck.append(Card(Suit.JOKER, Rank.BIG_JOKER))

    def shuffle_deck(self):
        self._rng.shuffle(self.deck)

    def deal_cards(self, n: int = 18):
        for p in self.players:
            p.hand.clear()
        idx = 0
        for _ in range(n):
            for p in self.players:
                if idx < len(self.deck):
                    p.add_card(self.deck[idx])
                    idx += 1

    # ----------------------------------------------------------------
    # 计分逻辑（完全翻译自C++）
    # ----------------------------------------------------------------
    def compute_scores(self, table: List[Card]) -> List[int]:
        scores = [0, 0, 0]
        v = [c.compare_value(self.rule) for c in table]
        order = sorted(range(3), key=lambda i: v[i],
                       reverse=(self.rule == Rule.BIG_WINS))
        if v[0] == v[1] == v[2]:
            return scores
        if v[order[0]] == v[order[1]]:
            scores[order[0]] = 1
            scores[order[1]] = 1
        elif v[order[1]] == v[order[2]]:
            scores[order[0]] = 2
        else:
            scores[order[0]] = 2
            scores[order[1]] = 1
        return scores

    def apply_bonus_score(self, table: List[Card]) -> Optional[Tuple[int, int]]:
        """并列时补分给唯一最低分玩家，返回(pidx, bonus)或None"""
        v = [c.compare_value(self.rule) for c in table]
        has_tie = (v[0]==v[1] or v[1]==v[2] or v[0]==v[2])
        if not has_tie:
            return None
        all_same = (v[0] == v[1] == v[2])
        bonus = 2 if all_same else 1
        min_score = min(p.score for p in self.players)
        lows = [i for i in range(3) if self.players[i].score == min_score]
        if len(lows) != 1:
            return None
        lucky = lows[0]
        self.players[lucky].score += bonus
        self._emit(EvType.BONUS_SCORE, (lucky, bonus))   # 不加msg，避免小字副题剑透
        self._ask(EvType.SHOW_INFO, {
            'type': 'bonus_score', 'auto_dismiss': True, 'duration': 1.5,
            'pidx': lucky, 'name': self.players[lucky].name, 'bonus': bonus,
            'reason': 'all_same' if all_same else 'pair_tie',
        })
        return (lucky, bonus)

    def handle_rule_flip(self, table: List[Card]) -> Optional[Rule]:
        """规则翻转，返回新规则（如果翻转）或None"""
        v = [c.compare_value(self.rule) for c in table]
        all_same = (v[0] == v[1] == v[2])
        if all_same:
            self.last_two_way_tie = False
            self.rule = Rule.SMALL_WINS if self.rule == Rule.BIG_WINS else Rule.BIG_WINS
            self._emit(EvType.RULE_FLIP, self.rule)   # 不加msg，避免小字剥透
            self._ask(EvType.SHOW_INFO, {'type': 'rule_flip', 'rule': self.rule, 'all_same': True})
            return self.rule
        two_way = (v[0]==v[1] or v[1]==v[2] or v[0]==v[2])
        if two_way:
            if self.last_two_way_tie:
                self.rule = Rule.SMALL_WINS if self.rule == Rule.BIG_WINS else Rule.BIG_WINS
                self.last_two_way_tie = False
                self._emit(EvType.RULE_FLIP, self.rule)   # 不加msg
                self._ask(EvType.SHOW_INFO, {'type': 'rule_flip', 'rule': self.rule, 'all_same': False})
                return self.rule
            else:
                self.last_two_way_tie = True
        else:
            self.last_two_way_tie = False
        return None

    # ----------------------------------------------------------------
    # 连顺判断
    # ----------------------------------------------------------------
    def is_three_consecutive(self, table: List[Card]) -> bool:
        if any(c.is_joker for c in table):
            return False
        nums = sorted(c.rank.value for c in table)
        return nums[1] == nums[0]+1 and nums[2] == nums[1]+1

    # ----------------------------------------------------------------
    # 5号牌归还
    # ----------------------------------------------------------------
    def process_five_returns(self):
        for i in range(3):
            if self.five_return_pending[i] and self.five_return_card[i]:
                c = self.five_return_card[i]
                c.is_returned = True
                self.players[i].add_card_random(c, self._rng)
                self.five_return_pending[i] = False
                self.five_return_card[i] = None
                self._emit(EvType.FIVE_RETURN, (i, c),
                           f"[5号牌] {self.players[i].name} 收回了上回合的牌(*)")

    # ----------------------------------------------------------------
    # 5号牌激活条件
    # ----------------------------------------------------------------
    def _check_five_activation(self, pidx: int, table: List[Card]) -> bool:
        v = [c.compare_value(self.rule) for c in table]
        if v[0]==v[1] or v[1]==v[2] or v[0]==v[2]:
            return False
        my_v = v[pidx]
        best = max(v) if self.rule == Rule.BIG_WINS else min(v)
        if my_v == best:
            return False
        return self.players[pidx].find_five() >= 0

    def perform_five_activations(self, table: List[Card]) -> List[bool]:
        """处理5号牌激活，返回各玩家是否激活的列表"""
        activated = [False, False, False]
        for i in range(3):
            if not self._check_five_activation(i, table):
                continue
            if self.players[i].is_human:
                do_it = self._ask(EvType.FIVE_ACTIVATE, {
                    'pidx': i, 'table': table
                })
            else:
                # AI：出的牌在中间或偏强时激活
                v = [c.compare_value(self.rule) for c in table]
                vals = sorted(v)
                my_v = v[i]
                do_it = (my_v >= vals[1] if self.rule == Rule.BIG_WINS
                         else my_v <= vals[1])
            if do_it:
                fi = self.players[i].find_five()
                if fi < 0:
                    continue
                five_card = self.players[i].hand[fi]   # 先保存再移除
                self.players[i].remove_card(fi)
                # 立即收回本轮打出的牌（不再延迟到下局）
                saved_idx = self.players[i].add_card_random(table[i], self._rng)
                activated[i] = True
                self._emit(EvType.FIVE_ACTIVATE,
                           {
                               'pidx': i,
                               'five_card': five_card,
                               'saved_card': table[i],
                               'saved_idx': saved_idx,
                               'saved_size': len(self.players[i].hand),
                           },
                           f"[5号牌] {self.players[i].name} 激活！收回本轮出的牌")
                if not self.players[i].is_human:
                    self._ask(EvType.SHOW_INFO, {
                        'type': 'five_ai', 'pidx': i,
                        'name': self.players[i].name,
                        'auto_dismiss': True, 'duration': 1.5,
                        'card_name': table[i].rank_str,
                    })
        return activated

    def _ai_choose_from_visible(self, cards: List[Card], purpose: str) -> int:
        """AI在已知目标手牌时的选择：purpose='draw' 或 'discard_target'."""
        if not cards:
            return 0

        def key_draw(c: Card):
            # 抽牌：优先对自己最有价值
            return c.compare_value(self.rule)

        def key_discard(c: Card):
            # 弃对方牌：优先丢掉对方最有价值的牌
            base = c.compare_value(self.rule)
            special = 2 if (not c.is_joker and c.rank in (Rank.R10, Rank.R5)) else 0
            joker = 3 if c.rank == Rank.BIG_JOKER else (2 if c.rank == Rank.SMALL_JOKER else 0)
            return (joker, special, abs(base), base)

        if purpose == 'draw':
            if self.rule == Rule.BIG_WINS:
                best = max(range(len(cards)), key=lambda i: key_draw(cards[i]))
            else:
                best = min(range(len(cards)), key=lambda i: key_draw(cards[i]))
            return best

        best = max(range(len(cards)), key=lambda i: key_discard(cards[i]))
        return best

    # ----------------------------------------------------------------
    # 出10机制
    # ----------------------------------------------------------------
    def perform_ten_mechanism(self, ten_player: int):
        tp_name = self.players[ten_player].name
        self._emit(EvType.TEN_MECHANISM, ten_player,
                   f"[顺手牵羊] {tp_name} 出了10！")
        self._ask(EvType.SHOW_INFO, {
            'type': 'ten_trigger', 'auto_dismiss': True,
            'duration': 1.5, 'name': tp_name,
        })
        # 拿走另两人的牌（emit动画事件：两张明牌飞向10方）
        for i in range(3):
            if i != ten_player:
                ins_idx = self.players[ten_player].add_card_random(self.table_cards[i], self._rng)
                self._emit(EvType.TEN_TAKE_CARD, {
                    'from': i, 'to': ten_player,
                    'card': self.table_cards[i],
                    'to_idx': ins_idx,
                    'to_size': len(self.players[ten_player].hand),
                }, f"[出10] {tp_name} 拿走 {self.players[i].name} 的牌")
        self.players[ten_player].remove_specific(self.table_cards[ten_player])
        self._ask(EvType.WAIT_ANIM, {'gap': 2.0})  # 等收牌动画 + 停顿

        # 自弃1张（强制，暗牌）
        if self.players[ten_player].is_human:
            idx = self._ask(EvType.TEN_SELF_DISCARD, {'pidx': ten_player})
        else:
            self._ask(EvType.SHOW_INFO, {
                'type': 'ai_action', 'auto_dismiss': True, 'duration': 0.75,
                'text': f"{tp_name} 正在选择自弃牌...",
            })
            idx = self._strategic_discard(ten_player)
        discarded = self.players[ten_player].hand[idx]
        self.players[ten_player].remove_card(idx)
        self._emit(EvType.TEN_SELF_DISCARD, {
            'pidx': ten_player, 'card': discarded, 'facedown': True,
        }, f"[出10] {tp_name} 悄悄弃了1张")
        self._ask(EvType.WAIT_ANIM, {'gap': 2.0})  # 等弃牌动画 + 停顿
        if not self.players[ten_player].is_human:
            self._ask(EvType.SHOW_INFO, {
                'type': 'ten_self_discard_ai', 'auto_dismiss': True,
                'duration': 1.0, 'name': tp_name,
            })

        # 下家盲弃1张（先允许小王偷窥）
        next_p = (ten_player + 1) % 3
        next_name = self.players[next_p].name
        peek_cards = self.perform_small_joker_peek(next_p, ten_player)

        if self.players[next_p].is_human:
            chosen = self._ask(EvType.TEN_BLIND_DISCARD, {
                'pidx': next_p, 'target': ten_player,
                'n': len(self.players[ten_player].hand)
            })
        else:
            self._ask(EvType.SHOW_INFO, {
                'type': 'ai_action', 'auto_dismiss': True, 'duration': 0.75,
                'text': f"{next_name} 正在盲选弃牌目标...",
            })
            if peek_cards:
                chosen = self._ai_choose_from_visible(peek_cards, 'discard_target')
            else:
                chosen = self._ai_blind_choice(len(self.players[ten_player].hand))

        chosen = self.perform_big_joker_defense(ten_player, chosen, selected_by=next_p)
        shown = self.players[ten_player].remove_card(chosen)
        self._emit(EvType.TEN_BLIND_DISCARD, {
            'pidx': next_p, 'target': ten_player,
            'card': shown, 'facedown': False,
        }, f"[出10] {next_name} 公开弃了 {shown.rank_str}")
        self._ask(EvType.WAIT_ANIM, {'gap': 2.0})  # 等明牌弃牌动画 + 停顿
        # 明牌展示通知（所有人都看到）
        self._ask(EvType.SHOW_INFO, {
            'type': 'ten_blind_discard_result',
            'auto_dismiss': True,
            'duration': 2.0,
            'name': next_name,
            'target_name': tp_name,
            'card_name': shown.rank_str,
        })

    # ----------------------------------------------------------------
    # 大王防御
    # ----------------------------------------------------------------
    def perform_big_joker_defense(self, target: int, chosen: int,
                                  selected_by: Optional[int] = None) -> int:
        p = self.players[target]
        if p.has_big_joker() and not p.can_use_big_joker():
            self._emit(EvType.DEFEND_REQ, {'exhausted': True, 'target': target})
            return chosen
        if not p.can_use_big_joker():
            return chosen
        n = len(p.hand)
        if n <= 1:
            return chosen
        offset = (n - 1) if chosen == 0 else (chosen - 1)

        if p.is_human:
            do_defend = self._ask(EvType.DEFEND_REQ, {
                'target': target, 'chosen': chosen, 'offset': offset,
                'chosen_name': p.hand[chosen].rank_str,
                'offset_name': p.hand[offset].rank_str,
                'uses': p.big_joker_uses,
            })
        else:
            chosen_val = p.hand[chosen].compare_value(self.rule)
            offset_val = p.hand[offset].compare_value(self.rule)
            vals = sorted(c.compare_value(self.rule) for c in p.hand)
            median = vals[n // 2]
            chosen_valuable = (chosen_val >= median if self.rule == Rule.BIG_WINS
                               else chosen_val <= median)
            new_weaker = (offset_val < chosen_val if self.rule == Rule.BIG_WINS
                          else offset_val > chosen_val)
            chosen_special = (not p.hand[chosen].is_joker and
                              p.hand[chosen].rank in (Rank.R10, Rank.R5))
            offset_special = (not p.hand[offset].is_joker and
                              p.hand[offset].rank in (Rank.R10, Rank.R5))
            # 避免把目标偏移到大王，造成反向血亏
            if p.hand[offset].rank == Rank.BIG_JOKER and p.hand[chosen].rank != Rank.BIG_JOKER:
                do_defend = False
            else:
                if chosen_valuable and new_weaker:         prob = 1.0
                elif chosen_special and not offset_special: prob = 0.8
                elif offset_special and not chosen_special: prob = 0.0
                elif chosen_valuable:                       prob = 0.3
                else:                                       prob = 0.15
                do_defend = self._rng.random() < prob

        if do_defend:
            p.big_joker_uses += 1
            new_chosen = offset
            by_name = self.players[selected_by].name if selected_by is not None else "对手"
            self._emit(EvType.DEFEND_RESULT, {
                'did': True, 'chosen': chosen, 'new': new_chosen,
                'chosen_name': p.hand[chosen].rank_str,
                'new_name': p.hand[new_chosen].rank_str,
                'uses': p.big_joker_uses,
            }, f"[大王防御] {p.name} 偏移了目标！")
            if p.is_human:
                self._ask(EvType.SHOW_INFO, {
                    'type': 'defend_success_private',
                    'auto_dismiss': True,
                    'duration': 1.0,
                    'name': p.name,
                    'by_name': by_name,
                })
            else:
                self._ask(EvType.SHOW_INFO, {
                    'type': 'defend_ai', 'auto_dismiss': True,
                    'name': p.name,
                    'by_name': by_name,
                    'duration': 1.0,
                })
            return new_chosen
        self._emit(EvType.DEFEND_RESULT, {'did': False})
        return chosen

    # ----------------------------------------------------------------
    # 小王偷窥
    # ----------------------------------------------------------------
    def perform_small_joker_peek(self, from_p: int, target: int) -> Optional[List[Card]]:
        p = self.players[from_p]
        if p.has_small_joker() and not p.can_use_small_joker():
            self._emit(EvType.PEEK_REQ, {'exhausted': True, 'from': from_p})
            return None
        if not p.can_use_small_joker():
            return None

        if p.is_human:
            do_peek = self._ask(EvType.PEEK_REQ, {
                'from': from_p, 'target': target, 'uses': p.small_joker_uses
            })
        else:
            do_peek = self._rng.random() < 0.6

        if not do_peek:
            return None
        p.small_joker_uses += 1
        visible_cards = list(self.players[target].hand)
        self._emit(EvType.PEEK_RESULT, {
            'from': from_p, 'target': target,
            'cards': visible_cards,
            'human_is_from': p.is_human,
        }, f"[小王偷窥] {p.name} 偷窥了 {self.players[target].name}")
        if p.is_human:
            self._ask(EvType.SHOW_INFO, {
                'type': 'peek_result',
                'auto_dismiss': True,
                'duration': 5.0,
                'target_name': self.players[target].name,
                'cards': visible_cards,
            })
        else:
            self._ask(EvType.SHOW_INFO, {
                'type': 'peek_ai', 'auto_dismiss': True, 'duration': 1.0,
                'name': p.name,
            })
        return visible_cards

    # ----------------------------------------------------------------
    # 连顺抽牌
    # ----------------------------------------------------------------
    def perform_draw_sequence(self):
        self._emit(EvType.DRAW_START, None, "[连顺抽牌] 三张连续！各从下家盲抽1张！")
        self._ask(EvType.SHOW_INFO, {'type': 'draw_start_notify', 'auto_dismiss': True, 'duration': 1.5})
        order = sorted(range(3), key=lambda i: self.players[i].score, reverse=True)

        for k in range(3):
            frm = order[k]
            tgt = (frm + 1) % 3
            if not self.players[tgt].hand:
                self._emit(EvType.MSG, None, f"{self.players[tgt].name} 手牌空，跳过")
                continue
            # 小王偷窥机会
            peek_cards = self.perform_small_joker_peek(frm, tgt)

            n = len(self.players[tgt].hand)
            if self.players[frm].is_human:
                chosen = self._ask(EvType.DRAW_ACTION, {
                    'from': frm, 'target': tgt, 'n': n
                })
            else:
                self._ask(EvType.SHOW_INFO, {
                    'type': 'ai_action', 'auto_dismiss': True, 'duration': 0.75,
                    'text': f"{self.players[frm].name} 正在选择抽取位置...",
                })
                if peek_cards:
                    chosen = self._ai_choose_from_visible(peek_cards, 'draw')
                else:
                    chosen = self._ai_blind_choice(n)

            chosen = self.perform_big_joker_defense(tgt, chosen, selected_by=frm)
            card = self.players[tgt].remove_card(chosen)
            # 立刻入手牌，保证飞牌结束后本回合就能在手牌区看到。
            to_idx = self.players[frm].add_card_random(card, self._rng)
            # 通知动画层：谁从谁那抽了牌（facedown=AI-AI，faceup=人类相关）
            human_involved = self.players[frm].is_human or self.players[tgt].is_human
            self._emit(EvType.DRAW_ACTION, {
                'from': frm, 'target': tgt, 'card': card,
                'faceup': human_involved,
                'to_idx': to_idx,
                'to_size': len(self.players[frm].hand),
            }, f"{self.players[frm].name} 从 {self.players[tgt].name} 抽1张")
            self._ask(EvType.WAIT_ANIM, {'gap': 2.0})  # 等飞牌动画播完 + 停顿

            frm_name = self.players[frm].name
            tgt_name = self.players[tgt].name
            if self.players[frm].is_human:
                # 人类抄到了，明牌展示（2s自动关）
                self._ask(EvType.SHOW_INFO, {
                    'type': 'draw_result', 'card': card,
                    'card_name': card.rank_str, 'target_name': tgt_name,
                    'auto_dismiss': True, 'duration': 2.0,
                })
            elif self.players[tgt].is_human:
                # 人类的牌被抗走，明牌通知（2s自动关）
                self._ask(EvType.SHOW_INFO, {
                    'type': 'card_stolen', 'card': card,
                    'card_name': card.rank_str, 'from_name': frm_name,
                    'auto_dismiss': True, 'duration': 2.0,
                })
            else:
                # AI-AI 互抽：1s自动关闭弹窗告知玩家动作
                self._ask(EvType.SHOW_INFO, {
                    'type': 'ai_draw', 'auto_dismiss': True,
                    'duration': 1.5,
                    'from_name': frm_name, 'target_name': tgt_name,
                })
        self._emit(EvType.MSG, None, "[连顺] 抽牌完毕")

    # ----------------------------------------------------------------
    # AI 逻辑
    # ----------------------------------------------------------------
    def _ai_rank(self, pidx: int) -> int:
        """返回该玩家当前名次：0=领先 1=中间 2=垫底"""
        s = self.players[pidx].score
        return sum(1 for i in range(3) if i != pidx and self.players[i].score > s)

    def strategic_choice(self, pidx: int) -> int:
        """
        AI说明（仅说明，不直接改变规则结算）：
        1) 普通牌：按当前名次、回合阶段和比大/比小规则，动态选择偏强/偏弱分位。
        2) 特殊牌（10、5）：
            - 10号在中局优先，落后时更积极触发顺手牵羊。
            - 5号不在这里直接强出，主要在结算阶段由 5号激活逻辑判断是否“救牌”。
        3) 技能牌（小王、大王）：
            - 小王用于“盲选前信息获取”，AI在抽牌/盲弃前会根据可见牌改为定向选择。
            - 大王用于“被选中后的防御偏移”，AI会评估被选牌价值、偏移后风险再决定是否防御。
        4) 王牌（大小王）与普通牌区分：
            - 出牌阶段会在特定局势优先考虑大王；
            - 其余情形仍按普通牌分位策略择牌，避免无脑交王牌。
        """
        p = self.players[pidx]
        if not p.hand:
            return 0
        n = len(p.hand)
        iv = [(c.compare_value(self.rule), i) for i, c in enumerate(p.hand)]
        iv.sort(key=lambda x: x[0])

        def at_pct(pct: float) -> int:
            pos = int(pct * (n - 1) + 0.5)
            pos = max(0, min(n - 1, pos))
            return iv[pos][1]

        rank = self._ai_rank(pidx)
        late = self.round_num >= 13
        very_late = self.round_num >= 16
        my_score = p.score
        max_opp = max((self.players[j].score for j in range(3) if j != pidx), default=0)
        gap = max_opp - my_score

        for i, c in enumerate(p.hand):
            if c.rank == Rank.BIG_JOKER:
                desperate = (rank == 2 and gap >= 3)
                secure_win = (very_late and gap <= -2)
                if desperate or secure_win:
                    return i

        if self.rule == Rule.SMALL_WINS:
            for i, c in enumerate(p.hand):
                if c.rank == Rank.SMALL_JOKER:
                    break

        for i, c in enumerate(p.hand):
            if not c.is_joker and c.rank == Rank.R10:
                if 4 <= self.round_num <= 15:
                    prob = 65 if rank == 2 else (40 if rank == 1 else 20)
                    if self._rng.randrange(100) < prob:
                        return i

        if self._rng.randrange(100) < 5:
            return iv[self._rng.randrange(n)][1]

        if self.rule == Rule.BIG_WINS:
            if rank == 2:
                if late:
                    return at_pct(0.85)
                return at_pct(0.75 + self._rng.randrange(15) * 0.01)
            elif rank == 1:
                return at_pct(0.45 + self._rng.randrange(30) * 0.01)
            else:
                if very_late:
                    return at_pct(0.60)
                return at_pct(0.25 + self._rng.randrange(30) * 0.01)
        else:
            if rank == 2:
                return at_pct(0.10 if late else 0.15 + self._rng.randrange(10) * 0.01)
            elif rank == 1:
                return at_pct(0.20 + self._rng.randrange(25) * 0.01)
            else:
                if very_late:
                    return at_pct(0.25)
                return at_pct(0.35 + self._rng.randrange(25) * 0.01)

    def random_choice(self, pidx: int) -> int:
        n = len(self.players[pidx].hand)
        return self._rng.randint(0, n - 1) if n > 0 else 0

    def ai_smart_rule_choice(self, pidx: int) -> Rule:
        hand = [c for c in self.players[pidx].hand if not c.is_joker]
        if not hand:
            return Rule.BIG_WINS
        avg = sum(c.rank.value for c in hand) / len(hand)
        return Rule.BIG_WINS if avg > 7 else Rule.SMALL_WINS

    def _ai_blind_choice(self, max_n: int) -> int:
        return self._rng.randint(0, max_n - 1) if max_n > 0 else 0

    def _strategic_discard(self, pidx: int) -> int:
        """AI弃最弱的非Joker牌，返回索引"""
        p = self.players[pidx]
        best_i, best_v = -1, None
        for i, c in enumerate(p.hand):
            if c.is_joker:
                continue
            v = c.compare_value(self.rule)
            if best_i == -1:
                best_i, best_v = i, v
            elif self.rule == Rule.BIG_WINS and v < best_v:
                best_i, best_v = i, v
            elif self.rule == Rule.SMALL_WINS and v > best_v:
                best_i, best_v = i, v
        return best_i if best_i >= 0 else 0

    # ----------------------------------------------------------------
    # 主回合
    # ----------------------------------------------------------------
    def play_round(self):
        self.msg_log.clear()
        self.table_cards = [None, None, None]
        self.played_idx = [-1, -1, -1]
        self.table_revealed = False

        self._emit(EvType.ROUND_START, self.round_num)

        # Step 0: 5号牌归还
        self.process_five_returns()

        # Step 1: AI出牌（逐个，动画播完即进入下一个，不额外停顿）
        for i in range(1, 3):
            c = self.random_choice(i) if not self.players[i].is_strategic else self.strategic_choice(i)
            self.played_idx[i] = c
            self.table_cards[i] = self.players[i].hand[c]
            self._ask(EvType.SHOW_INFO, {
                'type': 'ai_action', 'auto_dismiss': True, 'duration': 0.75,
                'text': f"{self.players[i].name} 正在出牌...",
            })
            self._emit(EvType.AI_PLAYED, (i, c))
            self._ask(EvType.WAIT_ANIM, None)   # 动画完即进入下一个

        # Step 2: 人类出牌（阻塞等待）
        human_sel = self._ask(EvType.HUMAN_PLAY_REQ, None)
        if self.quit_to_menu or human_sel is None:
            return   # 用户中途退出，提前结束本局
        self.played_idx[0] = human_sel
        self.table_cards[0] = self.players[0].hand[human_sel]

        # Step 3: 开牌动画
        self.table_revealed = True
        self._emit(EvType.REVEAL_CARDS, list(self.table_cards))
        # 等待翻牌动画全部完成，然后留2s空档
        self._ask(EvType.WAIT_ANIM, {'gap': 2.0})

        # Step 4: 大小王同台提示
        has_big = any(c.rank == Rank.BIG_JOKER for c in self.table_cards)
        has_small = any(c.rank == Rank.SMALL_JOKER for c in self.table_cards)
        if has_big and has_small:
            self._ask(EvType.SHOW_INFO, {'type': 'both_jokers',
                                         'auto_dismiss': True, 'duration': 2.0})

        # Step 5: 出10检查
        ten_count = sum(1 for c in self.table_cards
                        if not c.is_joker and c.rank == Rank.R10)
        ten_player = next((i for i, c in enumerate(self.table_cards)
                           if not c.is_joker and c.rank == Rank.R10), -1)
        has_ten = (ten_count == 1)

        if ten_count >= 2:
            self._ask(EvType.SHOW_INFO, {
                'type': 'ten_clash', 'auto_dismiss': True, 'duration': 1.5,
            })

        # Step 6: 从手中移除打出的牌（出10方后处理）
        for i in range(3):
            if has_ten and i == ten_player:
                continue
            if 0 <= self.played_idx[i] < len(self.players[i].hand):
                self.players[i].remove_card(self.played_idx[i])

        if has_ten:
            self.perform_ten_mechanism(ten_player)
            # 出10+连顺同时触发
            if self.is_three_consecutive(self.table_cards):
                self._emit(EvType.CONSECUTIVE, None, "[出10+连顺] 额外触发连顺抽牌！")
                self.perform_draw_sequence()
            if not self.quit_to_menu:
                self._ask(EvType.SHOW_INFO, {'type': 'ten_no_score',
                                             'auto_dismiss': True, 'duration': 1.5})
        else:
            # Step 7: 连顺检查（非第18局）
            consecutive = (self.round_num < 18 and
                           self.is_three_consecutive(self.table_cards))

            # Step 8: 5号牌激活（无连顺时）
            activated = [False, False, False]
            if not consecutive:
                activated = self.perform_five_activations(self.table_cards)

            # Step 9: 连顺抽牌（无5号牌激活时）
            if consecutive and not any(activated):
                self._ask(EvType.SHOW_INFO, {'type': 'consecutive',
                                             'auto_dismiss': True, 'duration': 1.5})
                self.perform_draw_sequence()

            # Step 10: 计分
            scores = self.compute_scores(self.table_cards)
            for i in range(3):
                self.players[i].score += scores[i]
            self._emit(EvType.SCORE_UPDATE, scores,
                       "[计分] " + " ".join(
                           f"{self.players[i].name}:+{scores[i]}" for i in range(3)))

            # Step 11: 补分
            self.apply_bonus_score(self.table_cards)

            # Step 12: 规则翻转
            self.handle_rule_flip(self.table_cards)
            # Step 13: 本局结果面板（阻塞，等待玩家点击确认）
            if not self.quit_to_menu:
                self._ask(EvType.SHOW_RESULT, {
                    'scores': scores, 'round': self.round_num
                })
        self.table_revealed = False
        self.table_cards = [None, None, None]

    # ----------------------------------------------------------------
    # 加赛
    # ----------------------------------------------------------------
    def play_tiebreaker(self, tied: List[int]) -> Tuple[List[int], List[int]]:
        """加赛，返回 (winner_list, tb_scores[3])"""
        # --- 加赛开场背景提示 ---
        bystanders = [i for i in range(3) if i not in tied]
        if len(tied) >= 3:
            self._ask(EvType.SHOW_INFO, {
                'type': 'tiebreaker_announce',
                'sub': 'three_way',
                'names': [self.players[i].name for i in tied],
                'auto_dismiss': True,
                'duration': 3.5,
            })
        else:  # 两人加赛
            if bystanders:
                bystander = bystanders[0]
                b_score = self.players[bystander].score
                t_score = self.players[tied[0]].score
                if b_score > t_score:
                    bystander_rank = '冠军'
                    rank_contested = '亚军和季军'
                else:
                    bystander_rank = '季军'
                    rank_contested = '冠军和亚军'
                self._ask(EvType.SHOW_INFO, {
                    'type': 'tiebreaker_announce',
                    'sub': 'two_way',
                    'bystander_name': self.players[bystander].name,
                    'bystander_rank': bystander_rank,
                    'tied_names': [self.players[i].name for i in tied],
                    'rank_contested': rank_contested,
                    'auto_dismiss': True,
                    'duration': 4.0,
                })
        tb_scores = [0, 0, 0]
        while True:
            for i in tied:
                self.players[i].hand.clear()

            # 两人加赛：发完全相同的牌组（每个点数最多2张），并禁用特殊技能
            if len(tied) == 2:
                self.init_deck()
                self.shuffle_deck()
                base_hand: List[Card] = []
                rank_cnt = {}
                for c in self.deck:
                    cnt = rank_cnt.get(c.rank, 0)
                    if cnt >= 2:
                        continue
                    base_hand.append(Card(c.suit, c.rank))
                    rank_cnt[c.rank] = cnt + 1
                    if len(base_hand) == 5:
                        break
                for i in tied:
                    self.players[i].hand = [Card(c.suit, c.rank) for c in base_hand]
                self._ask(EvType.SHOW_INFO, {
                    'type': 'tiebreaker_duel',
                    'auto_dismiss': True,
                    'duration': 2.0,
                    'a_name': self.players[tied[0]].name,
                    'b_name': self.players[tied[1]].name,
                })
            else:
                self.init_deck()
                self.shuffle_deck()
                ci = 0
                for _ in range(5):
                    for i in tied:
                        self.players[i].add_card(self.deck[ci])
                        ci += 1

            round_tb = [0, 0, 0]
            for tb in range(1, 6):
                self.table_cards = [None, None, None]
                self.played_idx = [-1, -1, -1]
                self.table_revealed = False
                round_gain = [0, 0, 0]

                for i in tied:
                    if not self.players[i].is_human:
                        self._ask(EvType.SHOW_INFO, {
                            'type': 'ai_action', 'auto_dismiss': True, 'duration': 1.5,
                            'text': f"{self.players[i].name}（加赛）正在出牌...",
                        })
                        c = self._rng.randint(0, len(self.players[i].hand) - 1)
                        self.played_idx[i] = c
                        self.table_cards[i] = self.players[i].hand[c]

                if any(self.players[i].is_human for i in tied):
                    h = self._ask(EvType.HUMAN_PLAY_REQ, {'tiebreaker': tb})
                    self.played_idx[0] = h
                    self.table_cards[0] = self.players[0].hand[h]

                self.table_revealed = True
                self._emit(EvType.REVEAL_CARDS, list(self.table_cards))
                self._ask(EvType.WAIT_ANIM, {'gap': 1.5})

                # 计分（仅参与者）
                if len(tied) == 2:
                    a, b = tied[0], tied[1]
                    va = self.table_cards[a].compare_value(self.rule)
                    vb = self.table_cards[b].compare_value(self.rule)
                    if va == vb:
                        round_tb[a] += 1; round_tb[b] += 1
                        round_gain[a] = 1; round_gain[b] = 1
                    elif (va > vb) == (self.rule == Rule.BIG_WINS):
                        round_tb[a] += 2
                        round_gain[a] = 2
                    else:
                        round_tb[b] += 2
                        round_gain[b] = 2
                else:
                    sc = self.compute_scores(self.table_cards)
                    for i in tied:
                        round_tb[i] += sc[i]
                        round_gain[i] = sc[i]

                for i in tied:
                    if 0 <= self.played_idx[i] < len(self.players[i].hand):
                        self.players[i].remove_card(self.played_idx[i])

                self._emit(EvType.SCORE_UPDATE, round_gain,
                           f"[加赛{tb}/5] 本局结束")

            # 判断胜者
            max_tb = max(round_tb[i] for i in tied)
            still = [i for i in tied if round_tb[i] == max_tb]
            tb_scores = round_tb
            if len(still) == 1:
                return still, tb_scores
            tied = still
            self._emit(EvType.MSG, 'tb_draw', "[加赛平局] 仍然平局，继续加赛！")

    # ----------------------------------------------------------------
    # 检查达标结束
    # ----------------------------------------------------------------
    def check_end_condition(self) -> Tuple[bool, List[int]]:
        """返回 (结束?, 并列玩家列表)"""
        if self.game_mode == 0:
            return False, []
        any_reached = any(p.score >= self.target_score for p in self.players)
        if not any_reached:
            return False, []
        max_s = max(p.score for p in self.players)
        top = [i for i in range(3) if self.players[i].score == max_s]
        # 冠军并列：冠军加赛
        if len(top) > 1:
            return True, top
        # 冠军唯一，但亚军/季军并列：也触发加赛，保证名次完整
        champion = top[0]
        others = [i for i in range(3) if i != champion]
        if len(others) == 2 and self.players[others[0]].score == self.players[others[1]].score:
            return True, others
        return True, []

    # ----------------------------------------------------------------
    # 开始新游戏（主流程）
    # ----------------------------------------------------------------
    def start_new_game(self):
        self.quit_to_menu = False

        if not self.skip_mode_select:
            # 渲染层处理模式选择
            result = self._ask(EvType.MSG, 'select_mode')
            self.game_mode = result.get('mode', 0)
            if self.game_mode == 1:
                self.target_score = result.get('target', 60)
        self.skip_mode_select = False

        if not self.consecutive_game:
            for p in self.players:
                p.score = 0
                p.reset_joker_uses()
            self.scene_count = 1

        for p in self.players:
            p.hand.clear()
        self.round_num = 1
        self.last_two_way_tie = False
        for i in range(3):
            self.five_return_pending[i] = False
            self.five_return_card[i] = None

        self.init_deck()
        self.shuffle_deck()
        self.deal_cards(18)

        # 发牌后展示手牌
        self._emit(EvType.MSG, 'deal_done')

        # 黑桃A选规则
        chooser = next((i for i in range(3) if self.players[i].has_spade_a()), -1)
        if not self.consecutive_game:
            if chooser == 0:  # 人类持有
                rule_choice = self._ask(EvType.MSG, 'select_rule')
                self.rule = Rule.BIG_WINS if rule_choice == 0 else Rule.SMALL_WINS
            elif chooser >= 0:
                self.rule = self.ai_smart_rule_choice(chooser)
                rule_str = '比大' if self.rule == Rule.BIG_WINS else '比小'
                self._ask(EvType.SHOW_INFO, {
                    'type': 'ai_rule', 'chooser': chooser,
                    'rule': self.rule, 'rule_str': rule_str,
                    'name': self.players[chooser].name,
                    'auto_dismiss': True, 'duration': 2.0,
                })
        else:
            if chooser >= 0:
                self.players[chooser].score += 1
                self._emit(EvType.MSG, {
                    'type': 'consecutive_bonus', 'chooser': chooser
                })
                self._ask(EvType.SHOW_INFO, {
                    'type': 'consecutive_bonus',
                    'name': self.players[chooser].name,
                    'auto_dismiss': True,
                    'duration': 1.8,
                })
        self.consecutive_game = False

        # 主循环
        for self.round_num in range(1, 19):
            self.play_round()
            if self.quit_to_menu:
                return {'action': 'menu'}

            if self.game_mode == 1:
                ended, tied = self.check_end_condition()
                if ended:
                    if not tied:
                        return {'action': 'final', 'tb_scores': [0,0,0]}
                    winner, tb_scores = self.play_tiebreaker(tied)
                    return {'action': 'final', 'tb_scores': tb_scores}

        # 18局结束
        if self.game_mode == 0:
            # 单局模式：若出现并列，按分数从高到低选第一组并列进入加赛。
            score_groups = {}
            for i, p in enumerate(self.players):
                score_groups.setdefault(p.score, []).append(i)
            tied_group: List[int] = []
            for s in sorted(score_groups.keys(), reverse=True):
                group = score_groups[s]
                if len(group) >= 2:
                    tied_group = group
                    break
            if tied_group:
                self._emit(EvType.TIEBREAKER, tied_group, "[平局] 18局结束，出现并列！进入加赛！")
                winner, tb_scores = self.play_tiebreaker(tied_group)
                return {'action': 'final', 'tb_scores': tb_scores}
            return {'action': 'final', 'tb_scores': [0,0,0]}
        else:
            # 达标分模式18局无人达标
            return {'action': 'continue_or_end'}
