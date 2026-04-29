# -*- coding: utf-8 -*-
"""
三雄争锋 - 主程序
状态机 + 主循环 + 所有交互弹框 + 特殊机制 UI 流程
"""
import os, sys, threading, time
import pygame
from typing import Optional, List, Dict, Any

from engine import (GameEngine, EvType, GameEvent, Rule, Rank, Suit,
                    Card, Player)
import render as R
from render import Button, draw_modal, draw_background
from anim import (AnimQueue, SlideAnim, FlipAnim, FloatTextAnim, ShakeAnim,
                  WaitAnim)
from audio import SoundBank

# ====================================================================
# 窗口尺寸 & 布局
# ====================================================================
WIN_W, WIN_H = 1080, 720

# 玩家区域 Y 中心
HUMAN_CY    = 640          # 人类手牌 Y（屏幕底部）
AI2_CY      = 80           # 玩家3(AI) 手牌 Y（顶部）
AI1_CX      = 120          # 玩家2(AI) 手牌 X（左侧竖排）
TABLE_CX    = WIN_W // 2   # 比较区中心 X
TABLE_CY    = 340           # 比较区中心 Y
INFO_RECT   = pygame.Rect(0, WIN_H - 80, WIN_W, 80)  # 底部信息栏

# 手牌区中心 X
HUMAN_CX  = WIN_W // 2
AI2_CX    = WIN_W // 2
AI1_CY    = WIN_H // 2

# ====================================================================
# 游戏状态
# ====================================================================
class State:
    MENU         = "menu"
    DEALING      = "dealing"
    PLAYER_TURN  = "player_turn"       # 等待人类选牌
    ANIMATING    = "animating"         # 动画播放中（引擎阻塞）
    DIALOG       = "dialog"            # 弹框等待确认
    REVEAL       = "reveal"            # 开牌动画
    SCORING      = "scoring"           # 计分浮字
    SPECIAL      = "special"           # 特殊机制流程
    TIEBREAKER   = "tiebreaker"
    FINAL_RANK   = "final_rank"
    QUIT         = "quit"


# ====================================================================
# 主应用
# ====================================================================
class App:
    def __init__(self):
        # 音频预初始化必须在 pygame.init() 之前
        pygame.mixer.pre_init(44100, -16, 2, 512)
        pygame.init()
        self.screen = pygame.display.set_mode((WIN_W, WIN_H))
        pygame.display.set_caption("三雄争锋")
        self.clock = pygame.time.Clock()

        # 找背景音乐（使用绝对路径）
        # 自动匹配目录中的 mp3 文件（文件名可能带 Lowtone Music 前缀）
        _base = os.path.dirname(os.path.abspath(__file__))
        music_path = ""
        for _f in os.listdir(_base):
            if _f.lower().endswith('.mp3') and not _f.endswith('.crdownload'):
                music_path = os.path.join(_base, _f)
                break
        self.sfx = SoundBank(music_path)

        self.anim_q = AnimQueue()
        self.engine = GameEngine()
        self._wire_engine()

        self.state = State.MENU
        self.selected_card = -1        # 人类当前选中的手牌索引
        self.hand_rects: List[pygame.Rect] = []
        self.revealed = [False, False, False]

        # 弹框系统
        self._dialog_result: Optional[Any] = None
        self._dialog_done = threading.Event()
        self._dialog_spec: Optional[Dict] = None   # 当前弹框描述

        # 引擎在后台线程运行
        self._engine_thread: Optional[threading.Thread] = None
        self._engine_result: Optional[Dict] = None

        # 菜单按钮
        self._menu_buttons = [
            Button("单局模式 (18局)", pygame.Rect(WIN_W//2-120, 320, 240, 50)),
            Button("达标分模式",      pygame.Rect(WIN_W//2-120, 390, 240, 50)),
        ]

        # 操作按钮（出牌 / 提示 / 返回，参照 v3.cpp 右下按钮区）
        _ABX, _ABW, _ABH = WIN_W - 130, 110, 44
        self._confirm_btn = Button("出牌", pygame.Rect(_ABX, HUMAN_CY - 56, _ABW, _ABH),
                                   color=(38, 90, 158))
        self._hint_btn    = Button("提示", pygame.Rect(_ABX, HUMAN_CY +  4, _ABW, _ABH),
                                   color=(30, 70, 130))
        self._back_btn    = Button("返回", pygame.Rect(_ABX, HUMAN_CY + 60, _ABW, _ABH),
                                   color=(90, 40, 40))
        # 引擎弹框状态
        self._pending_dialog = False   # 引擎是否正在等待我们的输入
        self._hint_card_idx  = -1      # 提示高亮的牌索引
        # 特殊机制按钮（动态创建）
        self._special_buttons: List[Button] = []
        self._special_payload: Optional[Dict] = None

        # 最终排名数据
        self._final_scores: List[int] = [0, 0, 0]
        self._final_tb:     List[int] = [0, 0, 0]
        self._final_game_mode: int = 0   # 记录游戏模式，排名页用
        self._menu_btn_final  = Button("返回菜单", pygame.Rect(WIN_W//2 + 10, 570, 155, 46),
                                       color=(80, 40, 40))
        self._again_btn_final = Button("再来一局",    pygame.Rect(WIN_W//2 - 165, 570, 155, 46),
                                       color=(38, 90, 158))

    # ----------------------------------------------------------------
    # 引擎事件接线
    # ----------------------------------------------------------------
    def _wire_engine(self):
        self.engine.on_event = self._on_engine_event
        self.engine.ask_human = self._ask_human_sync

    def _on_engine_event(self, ev: GameEvent):
        """在引擎线程中被调用；不能直接操作 pygame，入队动画/音效即可"""
        t = ev.type

        if t == EvType.ROUND_START:
            pass  # 主线程会在 PLAYER_TURN 前刷新

        elif t == EvType.AI_PLAYED:
            pidx, cidx = ev.data
            # AI 出牌动画：从 AI 位置滑向比较区槽位（扣着）
            src = self._player_hand_center(pidx)
            dst = self._table_slot_pos(pidx)
            self.anim_q.push(SlideAnim(
                self.engine.players[pidx].hand[cidx],
                src, dst, duration=0.30, facedown=True,
            ))
            self.sfx.play('play')

        elif t == EvType.REVEAL_CARDS:
            self.revealed = [False, False, False]
            cards = ev.data
            # 2 秒倒计时动画（显示圆环倒计时）
            def _cntdown(surf, progress,
                         _cx=TABLE_CX, _cy=TABLE_CY):
                remain = 2.0 * (1.0 - progress)
                R.draw_countdown(surf, _cx, _cy - 135, remain, 2.0, radius=32)
            self.anim_q.push(WaitAnim(2.0, draw_fn=_cntdown, parallel=False))
            # 三张牌同时翻开（parallel=True）
            for i, card in enumerate(cards):
                if card is None:
                    continue
                pos = self._table_slot_pos(i)
                pos = (pos[0] - R.CARD_W // 2, pos[1] - R.CARD_H // 2)
                self.anim_q.push(FlipAnim(card, pos, duration=0.45, parallel=True))
            self.sfx.play('reveal')

        elif t == EvType.SCORE_UPDATE:
            scores = ev.data
            for i in range(3):
                if scores and i < len(scores) and scores[i] > 0:
                    cx, cy = self._player_name_pos(i)
                    self.anim_q.push(FloatTextAnim(
                        f"+{scores[i]}分", (cx, cy - 30),
                        color=(255, 220, 50), duration=1.2, parallel=(i > 0)
                    ))
            self.sfx.play('score')

        elif t == EvType.RULE_FLIP:
            self.anim_q.push(FloatTextAnim(
                "规则翻转！", (WIN_W//2, TABLE_CY - 80),
                color=(255, 120, 50), font_size=28, duration=1.5
            ))
            self.sfx.play('flip')

        elif t == EvType.FIVE_ACTIVATE:
            pidx = ev.data
            cx, cy = self._player_name_pos(pidx)
            self.anim_q.push(FloatTextAnim("5号牌激活！", (cx, cy),
                                           color=(80, 200, 255), duration=1.2))
            self.sfx.play('special')

        elif t == EvType.TEN_MECHANISM:
            self.anim_q.push(FloatTextAnim(
                "顺手牵羊！", (WIN_W//2, TABLE_CY - 60),
                color=(255, 180, 30), font_size=26, duration=1.2
            ))
            self.sfx.play('special')

        elif t == EvType.DRAW_START:
            self.anim_q.push(FloatTextAnim(
                "连顺！各从下家抽牌！", (WIN_W//2, TABLE_CY - 60),
                color=(120, 220, 255), font_size=24, duration=1.5
            ))
            self.sfx.play('special')

        elif t == EvType.DRAW_ACTION:
            d = ev.data
            if isinstance(d, dict) and d.get('card'):
                frm, tgt, card = d['from'], d['target'], d['card']
                src = self._player_hand_center(tgt)
                dst = self._player_hand_center(frm)
                self.anim_q.push(SlideAnim(card, src, dst,
                                           duration=0.4, facedown=True))
            self.sfx.play('play')

        elif t == EvType.TIEBREAKER:
            self.anim_q.push(FloatTextAnim(
                "平局！进入加赛！", (WIN_W//2, WIN_H//2),
                color=(255, 80, 80), font_size=32, duration=2.0
            ))
            self.sfx.play('tiebreaker')

        elif t == EvType.TEN_BLIND_DISCARD:
            self.sfx.play('discard')

        elif t == EvType.BONUS_SCORE:
            pidx, bonus = ev.data
            cx, cy = self._player_name_pos(pidx)
            self.anim_q.push(FloatTextAnim(
                f"补分+{bonus}", (cx, cy - 50),
                color=(100, 255, 180), duration=1.0
            ))

    def _ask_human_sync(self, ev: GameEvent) -> Any:
        """
        引擎线程阻塞调用；向主线程发送弹框请求，等待结果。
        """
        self._dialog_done.clear()
        self._dialog_result = None
        self._dialog_spec = {'ev': ev}
        self._pending_dialog = True   # 通知主线程有新待处理弹框
        self._dialog_done.wait()   # 阻塞引擎线程直到主线程填入结果
        return self._dialog_result

    # ----------------------------------------------------------------
    # 坐标辅助
    # ----------------------------------------------------------------
    def _player_hand_center(self, pidx: int):
        if pidx == 0:  return (HUMAN_CX, HUMAN_CY)
        if pidx == 1:  return (AI1_CX,   AI1_CY)
        return              (AI2_CX,   AI2_CY)

    def _table_slot_pos(self, pidx: int):
        spacing = R.TABLE_SLOT_W + 15
        x0 = TABLE_CX - spacing * (3-1) // 2
        return (x0 + pidx * spacing, TABLE_CY)

    def _player_name_pos(self, pidx: int):
        cx, cy = self._player_hand_center(pidx)
        return (cx, cy - 80 if pidx == 0 else cy + 80)

    # ----------------------------------------------------------------
    # 主循环
    # ----------------------------------------------------------------
    def run(self):
        while self.state != State.QUIT:
            dt = self.clock.tick(60) / 1000.0
            self._handle_events()
            self._update(dt)
            self._draw()
            pygame.display.flip()
        pygame.quit()

    def _handle_events(self):
        mouse = pygame.mouse.get_pos()
        for btn in self._menu_buttons:
            btn.update(mouse)
        self._confirm_btn.update(mouse)
        self._hint_btn.update(mouse)
        self._back_btn.update(mouse)
        self._menu_btn_final.update(mouse)
        self._again_btn_final.update(mouse)
        for btn in self._special_buttons:
            btn.update(mouse)
        # 弹框/特殊框按钮也需要更新 hover 状态（否则 is_clicked 永远返回 False）
        if self._dialog_spec:
            for btn in self._dialog_spec.get('buttons', []):
                btn.update(mouse)

        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                self.state = State.QUIT
                return

            # --- 菜单 ---
            if self.state == State.MENU:
                if self._menu_buttons[0].is_clicked(ev):
                    self._start_game(mode=0)
                elif self._menu_buttons[1].is_clicked(ev):
                    self._start_game(mode=1)

            # --- 人类出牌 ---
            elif self.state == State.PLAYER_TURN:
                self._handle_player_turn_event(ev, mouse)

            # --- 弹框 ---
            elif self.state == State.DIALOG:
                self._handle_dialog_event(ev, mouse)

            # --- 特殊机制 ---
            elif self.state == State.SPECIAL:
                self._handle_special_event(ev, mouse)

            # --- 最终排名 ---
            elif self.state == State.FINAL_RANK:
                if self._menu_btn_final.is_clicked(ev):
                    self.state = State.MENU
                    self._engine_result = None
                elif self._again_btn_final.is_clicked(ev):
                    self._start_game(mode=self._final_game_mode)

            # ESC 返回菜单（游戏中）
            if ev.type == pygame.KEYDOWN and ev.key == pygame.K_ESCAPE:
                if self.state not in (State.MENU, State.QUIT, State.FINAL_RANK):
                    self._do_back_to_menu()

    def _handle_player_turn_event(self, ev, mouse):
        hand = self.engine.players[0].hand
        if ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
            # 点击手牌选择
            for i, rect in enumerate(self.hand_rects):
                if rect.collidepoint(mouse):
                    self.selected_card = i if self.selected_card != i else -1
                    self._hint_card_idx = -1   # 点牌时清除提示高亮
                    return
            # 点击出牌按钮
            if self._confirm_btn.is_clicked(ev) and self.selected_card >= 0:
                self._submit_human_play()
                return
            # 点击提示按钮
            if self._hint_btn.is_clicked(ev):
                self._hint_card_idx = self.engine.strategic_choice(0)
                return
            # 点击返回按钮
            if self._back_btn.is_clicked(ev):
                self._do_back_to_menu()

        elif ev.type == pygame.KEYDOWN:
            if ev.key in (pygame.K_RETURN, pygame.K_SPACE):
                if self.selected_card >= 0:
                    self._submit_human_play()
            elif ev.key == pygame.K_LEFT:
                n = len(hand)
                self.selected_card = (self.selected_card - 1) % n if n else -1
                self._hint_card_idx = -1
            elif ev.key == pygame.K_RIGHT:
                n = len(hand)
                self.selected_card = (self.selected_card + 1) % n if n else -1
                self._hint_card_idx = -1
            elif ev.key == pygame.K_h:
                self._hint_card_idx = self.engine.strategic_choice(0)

    def _do_back_to_menu(self):
        """中途返回主界面（ESC 或返回按钮）"""
        self.engine.quit_to_menu = True
        self._pending_dialog = False
        self._hint_card_idx = -1
        if not self._dialog_done.is_set():
            self._dialog_result = None
            self._dialog_done.set()
        self.state = State.MENU

    def _submit_human_play(self):
        """玩家确认出牌，向引擎线程返回选中索引"""
        idx = self.selected_card
        self.selected_card = -1
        self._hint_card_idx = -1
        # 出牌扳着滑动动画（与 AI 一致，一起手心朝下）
        if 0 <= idx < len(self.engine.players[0].hand):
            card = self.engine.players[0].hand[idx]
            src = self._player_hand_center(0)
            dst = self._table_slot_pos(0)
            self.anim_q.push(SlideAnim(card, src, dst,
                                       duration=0.30, facedown=True))
            self.sfx.play('play')
        # 解锁引擎线程
        self._dialog_result = idx
        self._dialog_done.set()
        self.state = State.ANIMATING

    def _handle_dialog_event(self, ev, mouse):
        """通用弹框事件处理"""
        if self._dialog_spec is None:
            return
        engine_ev: GameEvent = self._dialog_spec['ev']
        t = engine_ev.type

        if t == EvType.HUMAN_PLAY_REQ:
            # 弹框版出牌 — 转给 PLAYER_TURN 处理
            self.state = State.PLAYER_TURN

        elif t == EvType.MSG and engine_ev.data == 'select_mode':
            # 模式选择
            btns = self._dialog_spec.get('buttons', [])
            for btn in btns:
                if btn.is_clicked(ev):
                    mode = btns.index(btn)
                    self._dialog_result = {'mode': mode}
                    self._dialog_done.set()
                    self.state = State.ANIMATING

        elif t == EvType.MSG and engine_ev.data == 'select_rule':
            btns = self._dialog_spec.get('buttons', [])
            for i, btn in enumerate(btns):
                if btn.is_clicked(ev):
                    self._dialog_spec = None   # 先清除，防止重复触发
                    self._dialog_result = i
                    self._dialog_done.set()
                    self.state = State.ANIMATING

        elif t == EvType.MSG and engine_ev.data == 'select_mode':
            btns = self._dialog_spec.get('buttons', [])
            for btn in btns:
                if btn.is_clicked(ev):
                    mode = btns.index(btn)
                    self._dialog_spec = None
                    self._dialog_result = {'mode': mode}
                    self._dialog_done.set()
                    self.state = State.ANIMATING

        else:
            # 默认：有「确认」按钮
            btns = self._dialog_spec.get('buttons', [])
            for btn in btns:
                if btn.is_clicked(ev):
                    result = self._dialog_spec.get(f'result_{btn.text}', True)
                    self._dialog_spec = None
                    self._dialog_result = result
                    self._dialog_done.set()
                    self.state = State.ANIMATING

    def _handle_special_event(self, ev, mouse):
        if self._special_payload is None:
            return
        for btn in self._special_buttons:
            if btn.is_clicked(ev):
                result = self._special_payload.get(btn.text, btn.text)
                self._special_buttons.clear()
                self._special_payload = None
                self._dialog_spec = None   # 清除，防止 _resolve 重复触发
                self._dialog_result = result
                self._dialog_done.set()
                self.state = State.ANIMATING

    # ----------------------------------------------------------------
    # 更新
    # ----------------------------------------------------------------
    def _update(self, dt: float):
        self.anim_q.update(dt)

        # 动画播完后，若引擎在等待输入，切换到对应状态
        if self._pending_dialog and not self.anim_q.busy:
            if self.state not in (State.MENU, State.FINAL_RANK,
                                  State.DIALOG, State.SPECIAL):
                self._resolve_pending_dialog()

        # 检查引擎线程是否结束
        if (self._engine_thread and
                not self._engine_thread.is_alive() and
                self._engine_result is not None):
            result = self._engine_result
            self._engine_result = None
            self._engine_thread = None
            self._on_game_finished(result)

    def _resolve_pending_dialog(self):
        """根据待处理弹框类型，切换到合适状态让用户交互"""
        if not self._pending_dialog or self._dialog_spec is None:
            return
        self._pending_dialog = False   # 立即清除，防止重复触发
        ev: GameEvent = self._dialog_spec['ev']
        t = ev.type

        if t == EvType.HUMAN_PLAY_REQ:
            self._hint_card_idx = -1
            self.state = State.PLAYER_TURN

        elif t == EvType.FIVE_ACTIVATE:
            self._build_special_dialog_five(ev)
            self.state = State.SPECIAL

        elif t == EvType.DEFEND_REQ:
            self._build_special_dialog_defend(ev)
            self.state = State.SPECIAL

        elif t == EvType.PEEK_REQ:
            self._build_special_dialog_peek(ev)
            self.state = State.SPECIAL

        elif t == EvType.TEN_SELF_DISCARD:
            self.state = State.PLAYER_TURN   # 复用出牌交互选弃牌

        elif t == EvType.TEN_BLIND_DISCARD:
            self._build_special_dialog_blind(ev)
            self.state = State.SPECIAL

        elif t == EvType.DRAW_ACTION:
            self._build_special_dialog_blind(ev)
            self.state = State.SPECIAL

        elif t == EvType.MSG and ev.data == 'select_mode':
            self._build_mode_select_dialog()
            self.state = State.DIALOG

        elif t == EvType.MSG and ev.data == 'select_rule':
            self._build_rule_select_dialog()
            self.state = State.DIALOG

        else:
            # 默认给一个「确认」按钮
            self._dialog_spec['buttons'] = [
                Button("确认", pygame.Rect(WIN_W//2-50, WIN_H//2+60, 100, 40))
            ]
            self._dialog_spec['result_确认'] = True
            self.state = State.DIALOG

    # ----------------------------------------------------------------
    # 弹框构建器
    # ----------------------------------------------------------------
    def _build_mode_select_dialog(self):
        bx = WIN_W//2
        btns = [
            Button("单局模式", pygame.Rect(bx-130, WIN_H//2+40, 120, 44)),
            Button("达标分模式", pygame.Rect(bx+10,  WIN_H//2+40, 120, 44)),
        ]
        self._dialog_spec['buttons'] = btns

    def _build_rule_select_dialog(self):
        bx = WIN_W//2
        btns = [
            Button("比大", pygame.Rect(bx-130, WIN_H//2+40, 120, 44)),
            Button("比小", pygame.Rect(bx+10,  WIN_H//2+40, 120, 44)),
        ]
        self._dialog_spec['buttons'] = btns
        self._dialog_spec['result_比大'] = 0
        self._dialog_spec['result_比小'] = 1

    def _build_special_dialog_five(self, ev: GameEvent):
        d = ev.data
        bx, by = WIN_W//2, WIN_H//2 + 50
        self._special_buttons = [
            Button("激活", pygame.Rect(bx-130, by, 120, 44), color=(40,110,50)),
            Button("跳过", pygame.Rect(bx+10,  by, 120, 44), color=(100,50,50)),
        ]
        self._special_payload = {'激活': True, '跳过': False}

    def _build_special_dialog_defend(self, ev: GameEvent):
        d = ev.data if isinstance(ev.data, dict) else {}
        chosen_name = d.get('chosen_name', '?')
        offset_name = d.get('offset_name', '?')
        uses = d.get('uses', 0)
        bx, by = WIN_W//2, WIN_H//2 + 50
        self._special_buttons = [
            Button(f"偏移→{offset_name}",
                   pygame.Rect(bx-140, by, 140, 44), color=(160,100,20)),
            Button("不防御",
                   pygame.Rect(bx+10,  by, 120, 44), color=(80,40,40)),
        ]
        self._special_payload = {
            f"偏移→{offset_name}": True,
            '不防御': False,
        }

    def _build_special_dialog_peek(self, ev: GameEvent):
        bx, by = WIN_W//2, WIN_H//2 + 50
        self._special_buttons = [
            Button("偷窥", pygame.Rect(bx-130, by, 120, 44), color=(40,80,150)),
            Button("跳过", pygame.Rect(bx+10,  by, 120, 44), color=(80,40,40)),
        ]
        self._special_payload = {'偷窥': True, '跳过': False}

    def _build_special_dialog_blind(self, ev: GameEvent):
        """盲选：显示对方手牌数量，让玩家输入 1~N 的编号"""
        d = ev.data if isinstance(ev.data, dict) else {}
        n = d.get('n', len(self.engine.players[
            d.get('target', 1)].hand))
        bx = WIN_W//2 - (n * 55)//2
        by = WIN_H//2 + 40
        self._special_buttons = [
            Button(str(k+1), pygame.Rect(bx + k*55, by, 46, 44))
            for k in range(n)
        ]
        self._special_payload = {str(k+1): k for k in range(n)}

    # ----------------------------------------------------------------
    # 游戏启动
    # ----------------------------------------------------------------
    def _start_game(self, mode: int = 0):
        self.engine.game_mode = mode
        self.engine.skip_mode_select = True  # 我们自己处理了模式选择
        self.engine.consecutive_game = False
        self.selected_card = -1
        self.anim_q.clear()
        self._dialog_spec = None
        self._pending_dialog = False
        self._hint_card_idx = -1
        self._dialog_done.clear()
        self._engine_result = None

        self._engine_thread = threading.Thread(
            target=self._run_engine, daemon=True)
        self._engine_thread.start()
        self.state = State.ANIMATING

    def _run_engine(self):
        try:
            result = self.engine.start_new_game()
            self._engine_result = result or {'action': 'final', 'tb_scores': [0,0,0]}
        except Exception as e:
            self._engine_result = {'action': 'error', 'msg': str(e)}

    def _on_game_finished(self, result: dict):
        action = result.get('action', 'menu')
        if action == 'menu' or action == 'error':
            self.state = State.MENU
        elif action == 'final' or action == 'continue_or_end':
            self._final_scores = [p.score for p in self.engine.players]
            self._final_tb = result.get('tb_scores', [0, 0, 0])
            self._final_game_mode = self.engine.game_mode
            self.state = State.FINAL_RANK

    # ----------------------------------------------------------------
    # 绘制
    # ----------------------------------------------------------------
    def _draw(self):
        draw_background(self.screen)

        if self.state == State.MENU:
            self._draw_menu()
        elif self.state == State.FINAL_RANK:
            self._draw_final_rank()
        else:
            self._draw_game()

        # 动画层（最上层）
        self.anim_q.draw(self.screen)

    def _draw_menu(self):
        surf = self.screen
        R._render_text(surf, "三  雄  争  锋", 56, R.C_GOLD,
                       (WIN_W//2, 160), bold=True, anchor="center")
        R._render_text(surf, "三人对战纸牌游戏", 22, R.C_WHITE,
                       (WIN_W//2, 230), anchor="center")
        R._render_text(surf, "← → 选牌  Enter/空格 确认  ESC 返回菜单", 14,
                       R.C_GRAY, (WIN_W//2, WIN_H-30), anchor="center")
        for btn in self._menu_buttons:
            btn.draw(surf)

    def _draw_game(self):
        surf = self.screen
        eng = self.engine

        # --- AI2 手牌（顶部，扣着）---
        ai2_cards = eng.players[2].hand
        R.draw_player_label(surf, eng.players[2], AI2_CX, AI2_CY - 70)
        R.draw_hand(surf, ai2_cards, AI2_CX, AI2_CY,
                    facedown=True, card_w=60, card_h=84)

        # --- AI1 手牌（左侧，扣着，纵向简化为横排）---
        ai1_cards = eng.players[1].hand
        R.draw_player_label(surf, eng.players[1], AI1_CX, AI1_CY - 80)
        R.draw_hand(surf, ai1_cards, AI1_CX, AI1_CY,
                    facedown=True, card_w=52, card_h=72)

        # --- 比较区 ---
        anim_over = [None, None, None]  # 动画正在覆盖某槽位时传入
        R.draw_table_area(surf,
                          eng.table_cards,
                          [eng.table_revealed] * 3,
                          TABLE_CX, TABLE_CY,
                          anim_rects=anim_over)

        # 回合/规则标签
        rule_str = "【比大】" if eng.rule == Rule.BIG_WINS else "【比小】"
        R._render_text(surf, f"第 {eng.round_num}/18 局  {rule_str}",
                       18, R.C_GOLD, (WIN_W//2, TABLE_CY - 90),
                       bold=True, anchor="center")

        # --- 消息日志 ---
        ly = TABLE_CY + R.CARD_H//2 + 20
        for msg in eng.msg_log[-3:]:
            R._render_text(surf, msg[:58], 14, (190, 230, 190),
                           (WIN_W//2, ly), anchor="midtop")
            ly += 18

        # --- 人类手牌 ---
        human = eng.players[0]
        R.draw_player_label(surf, human, HUMAN_CX, HUMAN_CY - 90,
                            is_active=(self.state == State.PLAYER_TURN))
        self.hand_rects = R.draw_hand(
            surf, human.hand, HUMAN_CX, HUMAN_CY,
            selected_idx=self.selected_card)

        # 操作按钮（出牌 / 提示 / 返回）
        if self.state == State.PLAYER_TURN:
            self._confirm_btn.enabled = (self.selected_card >= 0)
            self._confirm_btn.draw(surf)
            self._hint_btn.draw(surf)
            self._back_btn.draw(surf)
            R._render_text(surf, "← → 选牌  Enter 确认  H 提示",
                           13, R.C_DIM, (WIN_W // 2, WIN_H - 6), anchor="center")
            # 提示高亮（覆盖在手牌上方的警告色圆角矩形）
            if (self._hint_card_idx >= 0 and
                    self._hint_card_idx < len(self.hand_rects)):
                hr = self.hand_rects[self._hint_card_idx]
                pygame.draw.rect(surf, R.C_WARN,
                                 hr.inflate(6, 6), 3, border_radius=9)

        # --- 特殊弹框 ---
        if self.state == State.SPECIAL and self._dialog_spec:
            self._draw_special_dialog()

        elif self.state == State.DIALOG and self._dialog_spec:
            self._draw_generic_dialog()

    def _draw_special_dialog(self):
        if self._dialog_spec is None:
            return
        ev: GameEvent = self._dialog_spec['ev']
        t = ev.type
        d = ev.data if isinstance(ev.data, dict) else {}

        if t == EvType.FIVE_ACTIVATE:
            title = "5号牌激活！"
            lines = ["本局你落败，但手中有5号牌。",
                     "激活可在下局开始前收回本次打出的牌。"]
        elif t == EvType.DEFEND_REQ:
            chosen_name = d.get('chosen_name', '?')
            offset_name = d.get('offset_name', '?')
            uses = d.get('uses', 0)
            title = f"大王防御！（已用{uses}次，共2次）"
            lines = [f"对方选了 {chosen_name}，可偏移至 {offset_name}。",
                     "是否使用大王防御？"]
        elif t == EvType.PEEK_REQ:
            tgt = d.get('target', 1)
            title = "小王偷窥！"
            lines = [f"可偷看 {self.engine.players[tgt].name} 的手牌。",
                     f"（小王每局只能用1次）"]
        elif t in (EvType.TEN_BLIND_DISCARD, EvType.DRAW_ACTION):
            tgt = d.get('target', 1)
            n = d.get('n', len(self.engine.players[tgt].hand))
            title = "盲选一张牌"
            lines = [f"从 {self.engine.players[tgt].name} 的 {n} 张手牌中选一张。",
                     "点击编号选择："]
        else:
            title = "操作"
            lines = []

        btns = self._special_buttons
        draw_modal(self.screen, title, lines, btns,
                   width=500, height=220 + len(lines)*22)
        for btn in btns:
            btn.draw(self.screen)

        # 偷窥结果展示
        if t == EvType.PEEK_RESULT:
            cards = d.get('cards', [])
            cx = WIN_W//2 - (len(cards) * (R.CARD_W+8))//2
            cy = WIN_H//2 - 20
            for i, c in enumerate(cards):
                R.draw_card(self.screen, c, cx + i*(R.CARD_W+8), cy)

    def _draw_generic_dialog(self):
        if self._dialog_spec is None:
            return
        ev: GameEvent = self._dialog_spec['ev']
        d = ev.data
        btns = self._dialog_spec.get('buttons', [])

        if d == 'select_mode':
            title = "选择游戏模式"
            lines = ["单局模式：18局结束计分", "达标分模式：先到目标分获胜"]
        elif d == 'select_rule':
            title = "你持有黑桃A！请选择本局规则"
            lines = ["比大：点数越大越好（A最小、K最大）",
                     "比小：点数越小越好（A最好）"]
        else:
            title = str(ev.msg) if ev.msg else "提示"
            lines = [str(d)] if d else []

        draw_modal(self.screen, title, lines, btns,
                   width=480, height=200 + len(lines)*22)
        for btn in btns:
            btn.draw(self.screen)

    def _draw_final_rank(self):
        surf = self.screen
        scores = self._final_scores
        tb    = self._final_tb
        has_tb = any(s > 0 for s in tb)
        players = self.engine.players

        # 排序：主分降序，相同时加赛分高者优先
        order = sorted(range(3), key=lambda i: (scores[i], tb[i]), reverse=True)

        # 底部内容面板
        pw, ph = 600, 480
        px, py = (WIN_W - pw) // 2, (WIN_H - ph) // 2 - 20
        panel = pygame.Rect(px, py, pw, ph)
        overlay = pygame.Surface((pw, ph), pygame.SRCALPHA)
        overlay.fill((13, 20, 42, 230))
        surf.blit(overlay, (px, py))
        pygame.draw.rect(surf, R.C_GOLD, panel, 2, border_radius=14)

        # 标题
        R._render_text(surf, "游戏结束！最终排名",
                       26, R.C_GOLD, (WIN_W//2, py + 30),
                       bold=True, anchor="center")
        pygame.draw.line(surf, R.C_GOLD,
                         (px + 20, py + 60), (px + pw - 20, py + 60), 1)

        # 奖牌文字和颜色
        _medal_texts = ["冠军", "亚军", "季军"]
        _medal_colors = [R.C_GOLD, R.C_SILVER, (180, 100, 50)]

        for rank, pidx in enumerate(order):
            ry = py + 88 + rank * 96
            # 行背景面板
            row = pygame.Rect(px + 18, ry, pw - 36, 80)
            row_col = (40, 60, 110) if rank == 0 else (24, 36, 68)
            pygame.draw.rect(surf, row_col, row, border_radius=8)
            pygame.draw.rect(surf, _medal_colors[rank], row, 1, border_radius=8)

            mc = _medal_colors[rank]
            # 名次标志
            R._render_text(surf, _medal_texts[rank],
                           20, mc, (px + 52, ry + 28), bold=True, anchor="center")
            # 玩家名 + 主分
            score_txt = f"{players[pidx].name}   {scores[pidx]} 分"
            if has_tb and tb[pidx] > 0:
                score_txt += f"   (加赛 +{tb[pidx]})"
            R._render_text(surf, score_txt,
                           22 if rank == 0 else 18,
                           mc if rank == 0 else R.C_TEXT,
                           (px + 100, ry + 28), bold=(rank == 0), anchor="midleft")

        # 感谢文字
        R._render_text(surf, "感谢游玩《三雄争锋》！",
                       16, R.C_DIM, (WIN_W//2, py + ph - 88), anchor="center")

        # 按钮
        self._again_btn_final.draw(surf)
        self._menu_btn_final.draw(surf)


# ====================================================================
# 入口
# ====================================================================
if __name__ == "__main__":
    app = App()
    app.run()
