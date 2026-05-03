# -*- coding: utf-8 -*-
"""
三雄争锋 - 渲染模块
程序化绘制：牌面、桌面背景、玩家区域、手牌、信息栏、按钮
"""
import pygame
import math
from typing import List, Optional, Tuple
from engine import Card, Rank, Suit, Rule, Player

# ====================================================================
# 颜色常量
# ====================================================================
# === 色彩方案（与 v3.cpp 一致，深蓝海军主题）===
C_TABLE        = (18,  26,  48)    # 主桌面背景
C_TABLE_D      = (11,  16,  32)    # 深色边角
C_PANEL        = (24,  36,  68)    # 卡牌区域面板
C_PANEL_D      = (13,  20,  42)    # 更深面板
C_BTN_N        = (38,  90, 158)    # 按钮普通蓝
C_BTN_H        = (58, 138, 220)    # 按钮悬停蓝
C_CARD_W       = (255, 252, 244)   # 牌面乳白
C_CARD_B       = (20,  40, 110)    # 牌背蓝
C_WHITE        = (255, 255, 255)
C_BLACK        = (0,   0,   0)
C_RED_S        = (200,  28,  28)   # 红色花色
C_BLK_S        = (14,  14,  14)    # 黑色花色
C_GOLD         = (255, 208,   0)   # 金色
C_SILVER       = (175, 188, 200)   # 银色
C_GRAY         = (160, 160, 160)
C_GRAY_DARK    = ( 80,  80,  80)
C_TEXT         = (228, 228, 228)   # 常规文字
C_DIM          = (100, 118, 145)   # 暗淡文字
C_WARN         = (255, 168,  32)   # 警告橙
C_JOKER_R      = (198,  28,  28)   # 大王红
C_JOKER_B      = ( 58,  58, 198)   # 小王蓝
C_SEL          = (255, 232,  50)   # 选中黄
# 兼容别名
C_GREEN_DARK   = C_TABLE
C_GREEN_FELT   = C_PANEL
C_GREEN_LIGHT  = (50, 75, 130)
C_RED          = C_RED_S
C_BLUE         = C_BTN_N
C_ALPHA_HALF   = (0, 0, 0, 128)

SUIT_COLOR = {
    Suit.SPADE:   C_BLK_S,
    Suit.CLUB:    C_BLK_S,
    Suit.HEART:   C_RED_S,
    Suit.DIAMOND: C_RED_S,
    Suit.JOKER:   C_GOLD,
}

SUIT_GLYPH = {
    Suit.SPADE: '♠', Suit.HEART: '♥',
    Suit.CLUB:  '♣', Suit.DIAMOND: '♦',
    Suit.JOKER: '★',
}


def draw_suit(surf: pygame.Surface, cx: int, cy: int, r: int, suit, color):
    """几何方式绘制花色（♠♥♦♣），不依赖 Unicode 字形，与 v3.cpp drawSuit 逻辑一致"""
    cx, cy, r = int(cx), int(cy), max(3, int(r))
    if suit == Suit.SPADE:
        br = max(2, r * 6 // 10)
        pygame.draw.circle(surf, color, (cx - r * 4 // 10, cy - r // 8), br)
        pygame.draw.circle(surf, color, (cx + r * 4 // 10, cy - r // 8), br)
        pts = [(cx, cy - r), (cx + r, cy + r * 4 // 10), (cx - r, cy + r * 4 // 10)]
        pygame.draw.polygon(surf, color, pts)
        stem = [(cx - r // 4, cy + r * 4 // 10), (cx + r // 4, cy + r * 4 // 10),
                (cx + r // 3, cy + r), (cx - r // 3, cy + r)]
        pygame.draw.polygon(surf, color, stem)
    elif suit == Suit.HEART:
        hr = max(2, r * 55 // 100)
        pygame.draw.circle(surf, color, (cx - r // 2, cy - r // 10), hr)
        pygame.draw.circle(surf, color, (cx + r // 2, cy - r // 10), hr)
        pts = [(cx - r, cy + r // 5), (cx, cy + r), (cx + r, cy + r // 5)]
        pygame.draw.polygon(surf, color, pts)
    elif suit == Suit.DIAMOND:
        pts = [(cx, cy - r), (cx + r, cy), (cx, cy + r), (cx - r, cy)]
        pygame.draw.polygon(surf, color, pts)
    elif suit == Suit.CLUB:
        cr = max(2, r * 42 // 100)
        pygame.draw.circle(surf, color, (cx, cy - r // 3), cr)
        pygame.draw.circle(surf, color, (cx - r // 2, cy + r // 5), cr)
        pygame.draw.circle(surf, color, (cx + r // 2, cy + r // 5), cr)
        stem = [(cx - r // 4, cy + r // 2), (cx + r // 4, cy + r // 2),
                (cx + r // 3, cy + r), (cx - r // 3, cy + r)]
        pygame.draw.polygon(surf, color, stem)


# ====================================================================
# 字体缓存（按 (name, size) 懒加载）
# ====================================================================
_font_cache: dict = {}

def _font(size: int, bold: bool = False) -> pygame.font.Font:
    key = (size, bold)
    if key not in _font_cache:
        try:
            # 优先用系统中文字体（多选一）
            for fname in ("microsoftyahei", "microsoftyaheiui", "simhei", "simsun"):
                f = pygame.font.SysFont(fname, size, bold=bold)
                if f:
                    break
        except Exception:
            f = pygame.font.Font(None, size)
        _font_cache[key] = f
    return _font_cache[key]


def _render_text(surf: pygame.Surface, text: str, size: int,
                 color, pos, bold=False, anchor="topleft"):
    f = _font(size, bold)
    t = f.render(text, True, color)
    r = t.get_rect(**{anchor: pos})
    surf.blit(t, r)
    return r


# ====================================================================
# 圆角矩形工具
# ====================================================================
def draw_rounded_rect(surf: pygame.Surface, color, rect: pygame.Rect,
                      radius: int, border=0, border_color=None):
    pygame.draw.rect(surf, color, rect, border_radius=radius)
    if border > 0 and border_color:
        pygame.draw.rect(surf, border_color, rect, border, border_radius=radius)


# ====================================================================
# 桌面背景（专业扑克毡布效果）
# ====================================================================
_bg_cache: Optional[pygame.Surface] = None

def draw_background(surf: pygame.Surface):
    """深蓝海军主题背景（与 v3.cpp C_TABLE 风格一致）"""
    global _bg_cache
    w, h = surf.get_size()
    if _bg_cache is None or _bg_cache.get_size() != (w, h):
        bg = pygame.Surface((w, h))
        bg.fill(C_TABLE_D)              # 深色底基
        # 微妙网格纹理（28px 间距淡线，模拟 v3.cpp 斤布纹理）
        for xx in range(0, w, 28):
            pygame.draw.line(bg, (28, 40, 68), (xx, 0), (xx, h), 1)
        for yy in range(0, h, 28):
            pygame.draw.line(bg, (28, 40, 68), (0, yy), (w, yy), 1)
        # 主桌面区域（略亮）
        cx, cy = w // 2, h // 2
        for i in range(12, 0, -1):
            t = i / 12
            r = int(C_TABLE_D[0] + t * (C_TABLE[0] - C_TABLE_D[0]))
            g = int(C_TABLE_D[1] + t * (C_TABLE[1] - C_TABLE_D[1]))
            b = int(C_TABLE_D[2] + t * (C_TABLE[2] - C_TABLE_D[2]))
            ew = int(w * (0.3 + t * 0.7))
            eh = int(h * (0.3 + t * 0.7))
            pygame.draw.ellipse(bg, (r, g, b),
                                pygame.Rect(cx - ew // 2, cy - eh // 2, ew, eh))
        # 四角暗晕
        for i in range(0, 80, 4):
            c = C_TABLE_D
            pygame.draw.line(bg, c, (0, i), (i, 0))
            pygame.draw.line(bg, c, (w - i, h), (w, h - i))
        # 金色装饰椭圆描边
        border_rect = pygame.Rect(50, 35, w - 100, h - 70)
        pygame.draw.ellipse(bg, (255, 208, 0), border_rect, 1)
        _bg_cache = bg
    surf.blit(_bg_cache, (0, 0))


# ====================================================================
# 单张牌面绘制
# ====================================================================
CARD_W = 82
CARD_H = 116

def draw_card(surf: pygame.Surface, card: Card, x: int, y: int,
              selected: bool = False, facedown: bool = False,
              width=CARD_W, height=CARD_H):
    """在 (x, y) 处绘制一张牌（含阴影）"""
    # 阴影（深绿偏移块，模拟投影）
    shadow_color = (5, 10, 20)
    pygame.draw.rect(surf, shadow_color,
                     pygame.Rect(x + 3, y + 5, width, height), border_radius=9)

    rect = pygame.Rect(x, y, width, height)

    if selected:
        glow = pygame.Rect(x - 4, y - 4, width + 8, height + 8)
        pygame.draw.rect(surf, C_SEL, glow, 3, border_radius=11)

    if facedown:
        _draw_card_back(surf, rect)
        return

    # 卡面（乳白色，与 v3.cpp C_CARD_W 一致）
    pygame.draw.rect(surf, C_CARD_W, rect, border_radius=8)
    pygame.draw.rect(surf, (50, 50, 50), rect, 1, border_radius=8)

    if card.is_joker:
        _draw_joker_face(surf, card, rect)
    else:
        _draw_normal_face(surf, card, rect, width, height)


def _draw_card_back(surf: pygame.Surface, rect: pygame.Rect):
    """牌背：深蓝底+点阵+金色圆圈装饰（与 v3.cpp drawCardBack 一致）"""
    pygame.draw.rect(surf, (15, 32, 90), rect, border_radius=8)
    pygame.draw.rect(surf, (80, 110, 180), rect, 2, border_radius=8)
    inner = rect.inflate(-8, -8)
    pygame.draw.rect(surf, (30, 52, 138), inner, border_radius=6)
    # 点阵纹理
    for dy in range(5, inner.height, 7):
        for dx in range(5, inner.width, 7):
            pygame.draw.circle(surf, (42, 68, 162),
                               (inner.x + dx, inner.y + dy), 2)
    # 中心装饰圆
    cx, cy = rect.centerx, rect.centery
    pygame.draw.circle(surf, (155, 118, 18), (cx, cy), rect.height // 5, 2)
    pygame.draw.circle(surf, (155, 118, 18), (cx, cy), rect.height // 9, 2)
    pygame.draw.circle(surf, (155, 118, 18), (cx, cy), rect.height // 14, 2)
    # 金色外框
    pygame.draw.rect(surf, (155, 118, 18), rect, 2, border_radius=8)


def _draw_normal_face(surf: pygame.Surface, card: Card, rect: pygame.Rect, w, h):
    """绘制普通牌正面：左上角点数 + 中央几何花色 + 右下角点数（与 v3.cpp 一致）"""
    color = SUIT_COLOR[card.suit]
    rank_s = card.rank_str

    # JQK 彩色背景条
    _FACE_TINTS = {
        Rank.J: (208, 242, 215),
        Rank.Q: (255, 210, 210),
        Rank.K: (210, 215, 255),
    }
    if card.rank in _FACE_TINTS:
        tint = _FACE_TINTS[card.rank]
        strip_h = h // 4
        pygame.draw.rect(surf, tint,
                         pygame.Rect(rect.x + 1, rect.y + 1, w - 2, strip_h),
                         border_radius=7)
        pygame.draw.rect(surf, tint,
                         pygame.Rect(rect.x + 1, rect.bottom - strip_h - 1, w - 2, strip_h),
                         border_radius=7)

    # 左上角点数
    rsize = max(14, h // 8)
    _render_text(surf, rank_s, rsize, color, (rect.x + 5, rect.y + 4), bold=True)

    # 右下角点数（旋转180°）
    rf = _font(rsize - 1, bold=False)
    rs = rf.render(rank_s, True, color)
    rs_rot = pygame.transform.rotate(rs, 180)
    surf.blit(rs_rot, (rect.right - 5 - rs_rot.get_width(),
                       rect.bottom - 4 - rs_rot.get_height()))

    # 中央大花色（几何绘制，不依赖字体，与 v3.cpp drawSuit 相同逻辑）
    suit_r = max(10, w * 2 // 9)
    draw_suit(surf, rect.centerx, rect.centery, suit_r, card.suit, color)


def _draw_joker_face(surf: pygame.Surface, card: Card, rect: pygame.Rect):
    """大/小王：纯色渐变背景 + 中文大字 + 四角星星"""
    is_big = (card.rank == Rank.BIG_JOKER)

    # 背景色（垂直渐变：上深下浅）
    col_top = (198,  28,  28) if is_big else (58,  58, 198)   # 与 v3 C_JOKER_R/B 一致
    col_bot = (230, 185,  40) if is_big else (70, 145, 235)
    for i in range(rect.height):
        t = i / rect.height
        c = tuple(int(col_top[j] * (1 - t) + col_bot[j] * t) for j in range(3))
        # 仅画矩形内部（简单实现，后面用border覆盖角落）
        pygame.draw.line(surf, c,
                         (rect.x, rect.y + i), (rect.right - 1, rect.y + i))
    # 覆盖黑色圆角边框
    pygame.draw.rect(surf, (40, 40, 40), rect, 1, border_radius=8)

    txt_col  = (255, 245, 60) if is_big else (220, 240, 255)
    star_col = (255,  80, 20) if is_big else (100, 220, 255)

    # 四角小星
    for sx, sy in [(rect.x+5, rect.y+4), (rect.right-16, rect.y+4),
                   (rect.x+5, rect.bottom-18), (rect.right-16, rect.bottom-18)]:
        _render_text(surf, "★", 11, star_col, (sx, sy))

    # 中央大字
    ch = rect.height // 5
    _render_text(surf, "大" if is_big else "小", ch, txt_col,
                 (rect.centerx, rect.centery - ch - 2),
                 bold=True, anchor="center")
    _render_text(surf, "王", ch, txt_col,
                 (rect.centerx, rect.centery + 2),
                 bold=True, anchor="center")


# ====================================================================
# 手牌区绘制（水平排列，有选中高亮）
# ====================================================================
HAND_OVERLAP = 30   # 牌之间的水平重叠（18张牌：82+52*17=966px，刚好适配1080px）

def draw_hand(surf: pygame.Surface, cards: List[Card],
              cx: int, cy: int,
              selected_idx: int = -1,
              facedown: bool = False,
              card_w: int = CARD_W, card_h: int = CARD_H,
              max_x: Optional[int] = None) -> List[pygame.Rect]:
    """
    在 (cx, cy) 为中心水平绘制一组手牌。
    max_x: 手牌区右边界（超出则压缩步距），避免与按钮区重叠。
    返回每张牌的 Rect 列表（用于点击检测）。
    """
    n = len(cards)
    if n == 0:
        return []

    step = card_w - HAND_OVERLAP
    total_w = card_w + step * (n - 1)
    x0 = cx - total_w // 2

    # 若超出右边界，压缩步距
    if max_x is not None and x0 + total_w > max_x:
        total_w = max_x - max(8, x0)
        total_w = max(card_w, total_w)
        step = max(8, (total_w - card_w) // max(1, n - 1))
        x0 = max(8, cx - total_w // 2)

    rects = []
    for k, card in enumerate(cards):
        xk = x0 + k * step
        yk = cy - card_h // 2
        if k == selected_idx:
            yk -= 15   # 选中牌上移
        draw_card(surf, card, xk, yk,
                  selected=(k == selected_idx),
                  facedown=facedown,
                  width=card_w, height=card_h)
        rects.append(pygame.Rect(xk, yk, card_w, card_h))
    return rects


# ====================================================================
# 桌面比较区（三张牌横排居中）
# ====================================================================
TABLE_SLOT_W = CARD_W + 20
TABLE_SLOT_H = CARD_H + 20

def draw_table_area(surf: pygame.Surface,
                    cards: List[Optional[Card]],
                    revealed: List[bool],
                    cx: int, cy: int,
                    anim_rects: Optional[List[Optional[pygame.Rect]]] = None):
    """
    绘制比较区三个槽位
    anim_rects: 如果动画覆盖了某张牌位置，用该 rect 替换默认位置
    """
    n = 3
    spacing = TABLE_SLOT_W + 15
    x0 = cx - spacing * (n - 1) // 2

    for i in range(n):
        xi = x0 + i * spacing
        yi = cy

        # 槽位背景
        slot = pygame.Rect(xi - TABLE_SLOT_W // 2, yi - TABLE_SLOT_H // 2,
                           TABLE_SLOT_W, TABLE_SLOT_H)
        draw_rounded_rect(surf, C_PANEL, slot, 8,
                          border=2, border_color=C_GOLD)

        if cards[i] is None:
            continue

        # 如果动画指定了位置，用动画位置
        if anim_rects and anim_rects[i]:
            ar = anim_rects[i]
            draw_card(surf, cards[i], ar.x, ar.y,
                      facedown=not revealed[i],
                      width=ar.width, height=ar.height)
        else:
            draw_card(surf, cards[i],
                      xi - CARD_W // 2, yi - CARD_H // 2,
                      facedown=not revealed[i])


# ====================================================================
# 信息栏 — 规则/分数/消息
# ====================================================================
def draw_info_bar(surf: pygame.Surface,
                  players: List[Player],
                  rule: Rule,
                  round_num: int,
                  msg_log: List[str],
                  bar_rect: pygame.Rect):
    pygame.draw.rect(surf, C_PANEL_D, bar_rect)
    pygame.draw.line(surf, C_GOLD, bar_rect.topleft, bar_rect.topright, 2)

    x, y = bar_rect.x + 10, bar_rect.y + 6

    # 规则标签
    rule_text = "【比大】" if rule == Rule.BIG_WINS else "【比小】"
    _render_text(surf, rule_text, 18, C_GOLD, (x, y), bold=True)

    # 回合
    _render_text(surf, f"第 {round_num}/18 局", 16, C_WHITE, (x + 85, y + 2))

    # 分数
    px = bar_rect.right - 260
    for i, p in enumerate(players):
        label = f"{p.name}: {p.score}分"
        col = C_GOLD if i == 0 else C_WHITE
        _render_text(surf, label, 15, col, (px + i * 88, y + 2))

    # 消息日志（最近2条）
    if msg_log:
        my = bar_rect.y + 28
        for msg in msg_log[-2:]:
            _render_text(surf, msg[:52], 13, (200, 230, 200), (x, my))
            my += 17


# ====================================================================
# 按钮
# ====================================================================
class Button:
    def __init__(self, text: str, rect: pygame.Rect,
                 color=(38, 90, 158), hover_color=(58, 138, 220),
                 text_color=C_WHITE, font_size=18):
        self.text = text
        self.rect = rect
        self.color = color
        self.hover_color = hover_color
        self.text_color = text_color
        self.font_size = font_size
        self.hovered = False
        self.enabled = True

    def update(self, mouse_pos: Tuple[int, int]):
        self.hovered = self.rect.collidepoint(mouse_pos) and self.enabled

    def draw(self, surf: pygame.Surface):
        c = self.hover_color if self.hovered else self.color
        if not self.enabled:
            c = C_GRAY_DARK
        draw_rounded_rect(surf, c, self.rect, 8, border=1, border_color=C_GOLD)
        _render_text(surf, self.text, self.font_size, self.text_color,
                     self.rect.center, bold=True, anchor="center")

    def is_clicked(self, event: pygame.event.Event) -> bool:
        """使用 event.pos 精确判断点击（不依赖可能滞后的 hovered 状态）"""
        return (self.enabled and
                event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and
                self.rect.collidepoint(event.pos))


# ====================================================================
# 弹框（确认/选择）
# ====================================================================
def draw_modal(surf: pygame.Surface,
               title: str,
               lines: List[str],
               buttons: List[Button],
               width: int = 480, height: int = 240):
    """居中绘制半透明模态框，返回 Rect"""
    sw, sh = surf.get_size()
    rx = (sw - width) // 2
    ry = (sh - height) // 2
    rect = pygame.Rect(rx, ry, width, height)

    # 半透明背景
    overlay = pygame.Surface((width, height), pygame.SRCALPHA)
    overlay.fill((13, 20, 42, 215))
    surf.blit(overlay, (rx, ry))
    pygame.draw.rect(surf, C_GOLD, rect, 2, border_radius=12)

    # 标题
    _render_text(surf, title, 22, C_GOLD,
                 (rx + width // 2, ry + 18), bold=True, anchor="midtop")

    # 正文行
    ty = ry + 55
    for line in lines:
        _render_text(surf, line, 16, C_WHITE,
                     (rx + width // 2, ty), anchor="midtop")
        ty += 22

    # 按钮
    for btn in buttons:
        btn.draw(surf)

    return rect


# ====================================================================
# 玩家名牌（显示在手牌上方）
# ====================================================================
def draw_player_label(surf: pygame.Surface, player: Player,
                      cx: int, y: int, is_active: bool = False):
    label = f"  {player.name}  {player.score}分  "
    color = C_GOLD if is_active else C_WHITE
    bg = C_BTN_N if is_active else C_PANEL
    f = _font(16, bold=is_active)
    ts = f.render(label, True, color)
    tw, th = ts.get_size()
    rect = pygame.Rect(cx - tw // 2 - 4, y - 2, tw + 8, th + 4)
    draw_rounded_rect(surf, bg, rect, 6, border=1, border_color=color)
    surf.blit(ts, (cx - tw // 2, y))


# ====================================================================
# 倒计时圆环
# ====================================================================
def draw_countdown(surf: pygame.Surface, cx: int, cy: int,
                   remain: float, total: float, radius: int = 28):
    pygame.draw.circle(surf, C_GRAY_DARK, (cx, cy), radius, 4)
    if remain > 0:
        angle = 360 * (remain / total)
        # pygame.draw.arc 使用 radians
        start_a = math.pi / 2  # 从顶部开始
        end_a = start_a + math.radians(angle)
        pygame.draw.arc(surf, C_GOLD,
                        (cx - radius, cy - radius, radius * 2, radius * 2),
                        start_a, end_a, 4)
    text = f"{int(math.ceil(remain))}"
    _render_text(surf, text, 20, C_WHITE, (cx, cy), bold=True, anchor="center")


# ====================================================================
# 本局结果面板（v3.cpp Step12 对应）
# ====================================================================
def draw_result_panel(surf: pygame.Surface,
                      scores: list, players: list, round_num: int,
                      surf_w: int = 1080, surf_h: int = 720):
    """绘制本局结果面板，v3.cpp风格：面板+三行分数+点击继续"""
    pw, ph = 460, 230
    px = (surf_w - pw) // 2
    py = (surf_h - ph) // 2 + 50

    overlay = pygame.Surface((pw, ph), pygame.SRCALPHA)
    overlay.fill((*C_PANEL_D, 245))
    surf.blit(overlay, (px, py))
    pygame.draw.rect(surf, C_GOLD, pygame.Rect(px, py, pw, ph), 2, border_radius=12)

    _render_text(surf, f"第 {round_num} 局结果", 20, C_GOLD,
                 (px + pw // 2, py + 28), bold=True, anchor="center")
    pygame.draw.line(surf, C_GOLD, (px + 18, py + 52), (px + pw - 18, py + 52), 1)

    for i in range(3):
        s = scores[i] if i < len(scores) else 0
        total_s = players[i].score if i < len(players) else 0
        buf = f"{players[i].name}   +{s}分   (总: {total_s}分)"
        if s == 2:
            col = C_GOLD
        elif s == 1:
            col = (88, 218, 128)
        else:
            col = C_DIM
        _render_text(surf, buf, 17, col,
                     (px + pw // 2, py + 72 + i * 38),
                     bold=(s == 2), anchor="center")

    _render_text(surf, "[ 点击任意处继续 ]", 14, C_DIM,
                 (px + pw // 2, py + ph - 22), anchor="center")


# ====================================================================
# 通用信息提示框
# ====================================================================
def draw_info_popup(surf: pygame.Surface, title: str, body: str,
                    sub: str = "",
                    surf_w: int = 1080, surf_h: int = 720,
                    card=None):
    """类似 v3.cpp showMsgBox：深蓝面板+金色边框+标题+内容+点击继续"""
    pw, ph = 540, 240
    if card is not None:
        ph = 320
    px = (surf_w - pw) // 2
    py = (surf_h - ph) // 2

    # 半透明遮罩
    mask = pygame.Surface((surf_w, surf_h), pygame.SRCALPHA)
    mask.fill((0, 0, 0, 140))
    surf.blit(mask, (0, 0))

    overlay = pygame.Surface((pw, ph), pygame.SRCALPHA)
    overlay.fill((*C_PANEL_D, 250))
    surf.blit(overlay, (px, py))
    pygame.draw.rect(surf, C_GOLD, pygame.Rect(px, py, pw, ph), 2, border_radius=12)

    _render_text(surf, title, 22, C_GOLD,
                 (px + pw // 2, py + 36), bold=True, anchor="center")
    pygame.draw.line(surf, C_GOLD, (px + 18, py + 62), (px + pw - 18, py + 62), 1)

    _render_text(surf, body, 17, C_TEXT,
                 (px + pw // 2, py + ph // 2 - 10),
                 anchor="center")
    if sub:
        _render_text(surf, sub, 14, C_DIM,
                     (px + pw // 2, py + ph // 2 + 18),
                     anchor="center")

    # 如果传入card则展示在中央
    if card is not None:
        draw_card(surf, card, px + pw // 2 - CARD_W // 2,
                  py + ph // 2 - CARD_H // 2 + 10)

    _render_text(surf, "[ 点击任意处继续 ]", 14, C_DIM,
                 (px + pw // 2, py + ph - 24), anchor="center")

