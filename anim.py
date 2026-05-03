# -*- coding: utf-8 -*-
"""
三雄争锋 - 动画系统
提供：SlideAnim（牌滑动）、FlipAnim（翻牌）、FloatTextAnim（浮字）
统一由 AnimQueue 管理：入队 → 按顺序/并行播放 → 回调通知完成
"""
import pygame
import math
from typing import Callable, List, Optional, Tuple
from engine import Card
import render as R

# ====================================================================
# 缓动函数
# ====================================================================
def ease_out_cubic(t: float) -> float:
    return 1 - (1 - t) ** 3

def ease_in_out_quad(t: float) -> float:
    if t < 0.5:
        return 2 * t * t
    return 1 - (-2 * t + 2) ** 2 / 2

def ease_out_back(t: float, s: float = 1.70158) -> float:
    return 1 + (s + 1) * (t - 1) ** 3 + s * (t - 1) ** 2


# ====================================================================
# 基类
# ====================================================================
class BaseAnim:
    def __init__(self, duration: float, on_done: Optional[Callable] = None,
                 parallel: bool = False):
        """
        duration: 秒
        on_done:  完成回调
        parallel: True=与下一个动画同时执行；False=排队等待
        """
        self.duration = duration
        self.on_done = on_done
        self.parallel = parallel
        self._elapsed = 0.0
        self.done = False

    @property
    def progress(self) -> float:
        return min(1.0, self._elapsed / self.duration) if self.duration > 0 else 1.0

    def update(self, dt: float):
        if self.done:
            return
        self._elapsed += dt
        if self._elapsed >= self.duration:
            self._elapsed = self.duration
            self.done = True
            if self.on_done:
                self.on_done()

    def draw(self, surf: pygame.Surface):
        """子类覆盖"""
        pass


# ====================================================================
# SlideAnim — 一张牌从 src 滑向 dst
# arc   : 飞行弧线高度（像素），正值=向上隆起，使飞行轨迹更自然
# rotate: 飞行中最大旋转角度（度），牌在中途略微倾斜
# ====================================================================
class SlideAnim(BaseAnim):
    def __init__(self, card: Card,
                 src: Tuple[int, int], dst: Tuple[int, int],
                 duration: float = 0.35,
                 facedown: bool = True,
                 arc: int = 0,
                 rotate: float = 0.0,
                 card_w: int = R.CARD_W, card_h: int = R.CARD_H,
                 on_done: Optional[Callable] = None,
                 parallel: bool = False):
        super().__init__(duration, on_done, parallel)
        self.card = card
        self.src = src
        self.dst = dst
        self.facedown = facedown
        self.arc = arc
        self.rotate = rotate
        self.card_w = card_w
        self.card_h = card_h

    def current_pos(self) -> Tuple[int, int]:
        t = ease_out_cubic(self.progress)
        x = self.src[0] + (self.dst[0] - self.src[0]) * t
        y = self.src[1] + (self.dst[1] - self.src[1]) * t
        # 弧线：正弦曲线在中途向上隆起，给飞牌一种抛物线感
        if self.arc != 0:
            arc_offset = self.arc * math.sin(math.pi * self.progress)
            y -= arc_offset
        return int(x), int(y)

    def draw(self, surf: pygame.Surface):
        if self.done:
            return
        cx, cy = self.current_pos()
        if self.rotate != 0:
            # 飞行中途旋转，正弦曲线使牌在起点/终点不倾斜
            angle = self.rotate * math.sin(math.pi * self.progress)
            tmp = pygame.Surface((self.card_w, self.card_h), pygame.SRCALPHA)
            tmp.fill((0, 0, 0, 0))
            R.draw_card(tmp, self.card, 0, 0,
                        facedown=self.facedown,
                        width=self.card_w, height=self.card_h)
            rotated = pygame.transform.rotate(tmp, angle)
            # src/dst/current_pos 使用牌中心坐标，旋转后仍以中心对齐。
            ox = cx - rotated.get_width() // 2
            oy = cy - rotated.get_height() // 2
            surf.blit(rotated, (ox, oy))
        else:
            R.draw_card(surf, self.card,
                        cx - self.card_w // 2,
                        cy - self.card_h // 2,
                        facedown=self.facedown,
                        width=self.card_w, height=self.card_h)


# ====================================================================
# FlipAnim — 翻牌动画（水平压扁再展开）
# ====================================================================
class FlipAnim(BaseAnim):
    def __init__(self, card: Card,
                 pos: Tuple[int, int],
                 duration: float = 0.45,
                 card_w: int = R.CARD_W, card_h: int = R.CARD_H,
                 on_done: Optional[Callable] = None,
                 parallel: bool = True):
        super().__init__(duration, on_done, parallel)
        self.card = card
        self.pos = pos
        self.card_w = card_w
        self.card_h = card_h

    def draw(self, surf: pygame.Surface):
        if self.done:
            R.draw_card(surf, self.card, self.pos[0], self.pos[1],
                        facedown=False, width=self.card_w, height=self.card_h)
            return
        t = self.progress
        # 前半段显示牌背（压扁），后半段显示正面（展开）
        half = 0.5
        if t < half:
            scale_x = 1.0 - 2 * t     # 1→0
            facedown = True
        else:
            scale_x = 2 * (t - half)  # 0→1
            facedown = False

        scale_x = max(0.01, scale_x)
        cw = int(self.card_w * scale_x)
        ch = self.card_h

        tmp = pygame.Surface((self.card_w, ch), pygame.SRCALPHA)
        tmp.fill((0, 0, 0, 0))
        R.draw_card(tmp, self.card, 0, 0, facedown=facedown,
                    width=self.card_w, height=ch)

        scaled = pygame.transform.scale(tmp, (max(1, cw), ch))
        ox = self.pos[0] + (self.card_w - cw) // 2
        surf.blit(scaled, (ox, self.pos[1]))


# ====================================================================
# FloatTextAnim — 浮字（分数/提示从某点向上飘散淡出）
# ====================================================================
class FloatTextAnim(BaseAnim):
    def __init__(self, text: str,
                 pos: Tuple[int, int],
                 color=(255, 220, 50),
                 font_size: int = 22,
                 duration: float = 1.2,
                 rise: int = 50,
                 on_done: Optional[Callable] = None,
                 parallel: bool = True):
        super().__init__(duration, on_done, parallel)
        self.text = text
        self.pos = pos
        self.color = color
        self.font_size = font_size
        self.rise = rise

    def draw(self, surf: pygame.Surface):
        t = self.progress
        if t >= 1.0:
            return
        alpha = int(255 * (1 - ease_out_cubic(t)))
        dy = int(self.rise * ease_out_cubic(t))

        f = R._font(self.font_size, bold=True)
        ts = f.render(self.text, True, self.color)
        ts_alpha = ts.copy()
        ts_alpha.set_alpha(alpha)
        x = self.pos[0] - ts.get_width() // 2
        y = self.pos[1] - dy
        surf.blit(ts_alpha, (x, y))


# ====================================================================
# ShakeAnim — 震动效果（用于大王防御等）
# ====================================================================
class ShakeAnim(BaseAnim):
    def __init__(self, card: Card,
                 center: Tuple[int, int],
                 duration: float = 0.5,
                 intensity: int = 8,
                 card_w: int = R.CARD_W, card_h: int = R.CARD_H,
                 on_done: Optional[Callable] = None,
                 parallel: bool = True):
        super().__init__(duration, on_done, parallel)
        self.card = card
        self.center = center
        self.intensity = intensity
        self.card_w = card_w
        self.card_h = card_h

    def draw(self, surf: pygame.Surface):
        if self.done:
            R.draw_card(surf, self.card,
                        self.center[0] - self.card_w // 2,
                        self.center[1] - self.card_h // 2)
            return
        t = self.progress
        decay = 1 - t
        dx = int(self.intensity * decay *
                 math.sin(t * math.pi * 8))
        x = self.center[0] - self.card_w // 2 + dx
        y = self.center[1] - self.card_h // 2
        R.draw_card(surf, self.card, x, y,
                    width=self.card_w, height=self.card_h)


# ====================================================================
# WaitAnim — 纯等待（可选可视反馈，用于开牌前倒计时）
# ====================================================================
class WaitAnim(BaseAnim):
    """等待指定时长，可选传入 draw_fn(surf, progress) 绘制视觉反馈"""
    def __init__(self, duration: float,
                 draw_fn=None,
                 on_done: Optional[Callable] = None,
                 parallel: bool = False):
        super().__init__(duration, on_done, parallel)
        self._draw_fn = draw_fn

    def draw(self, surf: pygame.Surface):
        if self.done or self._draw_fn is None:
            return
        self._draw_fn(surf, self.progress)


# ====================================================================
# AnimQueue — 动画队列管理器
# ====================================================================
class AnimQueue:
    def __init__(self):
        self._queue: List[BaseAnim] = []
        self._active: List[BaseAnim] = []  # 当前并行组

    def push(self, anim: BaseAnim):
        """入队一个动画"""
        self._queue.append(anim)

    def push_many(self, anims: List[BaseAnim]):
        for a in anims:
            self._queue.append(a)

    @property
    def busy(self) -> bool:
        """是否有动画正在播放或排队"""
        return bool(self._active or self._queue)

    def _load_next_group(self):
        """从队列头部加载下一个「并行组」到 active"""
        if not self._queue:
            return
        group = [self._queue.pop(0)]
        # 连续 parallel=True 的动画一起加入
        while self._queue and self._queue[0].parallel:
            group.append(self._queue.pop(0))
        self._active = group

    def update(self, dt: float):
        if not self._active and self._queue:
            self._load_next_group()

        for a in self._active:
            a.update(dt)

        self._active = [a for a in self._active if not a.done]

    def draw(self, surf: pygame.Surface):
        for a in self._active:
            a.draw(surf)

    def clear(self):
        self._queue.clear()
        self._active.clear()

    def wait_done(self):
        """同步等待（仅CLI测试用，实际不调用）"""
        pass
