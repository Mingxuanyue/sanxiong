# -*- coding: utf-8 -*-
"""
三雄争锋 - 音效与背景音乐模块
用 numpy 程序化生成所有音效；加载用户提供的 MP3 作背景音乐
"""
import numpy as np
import pygame
import os

# 采样率与帧大小
_SR = 44100
_CHANNELS = 2
_SAMPLE_SIZE = -16       # signed 16-bit
_BUFFER = 512

_initialized = False


def init_audio(music_path: str = ""):
    """初始化pygame音频；可选传入背景音乐路径"""
    global _initialized
    # 若 mixer 已由 pygame.mixer.pre_init() + pygame.init() 初始化，直接使用
    # 避免 quit/re-init 导致 pre_init 设置失效及音乐停止
    if not pygame.mixer.get_init():
        pygame.mixer.init(_SR, _SAMPLE_SIZE, _CHANNELS, _BUFFER)
    _initialized = True
    if music_path and os.path.exists(music_path):
        try:
            pygame.mixer.music.load(music_path)
            pygame.mixer.music.set_volume(0.45)
            pygame.mixer.music.play(-1)   # 循环
        except Exception:
            pass   # 音乐文件加载失败时静默忽略


def _make_sound(samples: np.ndarray) -> pygame.mixer.Sound:
    """将 float32 mono → int16 stereo Sound"""
    s16 = np.clip(samples * 32767, -32768, 32767).astype(np.int16)
    stereo = np.column_stack([s16, s16])   # shape (N, 2)
    return pygame.sndarray.make_sound(np.ascontiguousarray(stereo))


def _envelope(n: int, attack: float = 0.01, release: float = 0.15) -> np.ndarray:
    env = np.ones(n, dtype=np.float32)
    atk = int(attack * _SR)
    rel = int(release * _SR)
    if atk > 0:
        env[:atk] = np.linspace(0, 1, atk)
    if rel > 0 and rel <= n:
        env[-rel:] = np.linspace(1, 0, rel)
    return env


# ----------------------------------------------------------------
# 出牌声：快速下扫频 sweep（约0.12s）
# ----------------------------------------------------------------
def make_play_sound() -> pygame.mixer.Sound:
    dur = 0.12
    n = int(dur * _SR)
    t = np.linspace(0, dur, n, dtype=np.float32)
    f = np.linspace(900, 350, n)             # 高→低扫频
    phase = np.cumsum(2 * np.pi * f / _SR)
    wave = 0.35 * np.sin(phase) * _envelope(n, 0.003, 0.05)
    return _make_sound(wave)


# ----------------------------------------------------------------
# 开牌声：轻脆短 click（约0.08s）
# ----------------------------------------------------------------
def make_reveal_sound() -> pygame.mixer.Sound:
    dur = 0.08
    n = int(dur * _SR)
    t = np.linspace(0, dur, n, dtype=np.float32)
    wave = 0.4 * np.sin(2 * np.pi * 1200 * t) * _envelope(n, 0.001, 0.04)
    # 叠加噪声点击感
    noise = 0.12 * (np.random.rand(n).astype(np.float32) * 2 - 1)
    noise *= _envelope(n, 0.001, 0.03)
    return _make_sound(wave + noise)


# ----------------------------------------------------------------
# 得分声：明亮上升 ding（约0.35s）
# ----------------------------------------------------------------
def make_score_sound() -> pygame.mixer.Sound:
    dur = 0.35
    n = int(dur * _SR)
    t = np.linspace(0, dur, n, dtype=np.float32)
    f1, f2 = 880, 1100
    w = (0.5 * np.sin(2 * np.pi * f1 * t) +
         0.25 * np.sin(2 * np.pi * f2 * t)) * _envelope(n, 0.005, 0.20)
    return _make_sound(w.astype(np.float32))


# ----------------------------------------------------------------
# 规则翻转声：双音颤（约0.30s）
# ----------------------------------------------------------------
def make_flip_sound() -> pygame.mixer.Sound:
    dur = 0.30
    n = int(dur * _SR)
    t = np.linspace(0, dur, n, dtype=np.float32)
    # LFO 颤音
    lfo = np.sin(2 * np.pi * 12 * t)
    f_mod = 600 + 80 * lfo
    phase = np.cumsum(2 * np.pi * f_mod / _SR)
    w = 0.45 * np.sin(phase) * _envelope(n, 0.01, 0.12)
    return _make_sound(w.astype(np.float32))


# ----------------------------------------------------------------
# 特殊机制声：出10/抽牌 — 低沉短 thud（约0.15s）
# ----------------------------------------------------------------
def make_special_sound() -> pygame.mixer.Sound:
    dur = 0.15
    n = int(dur * _SR)
    t = np.linspace(0, dur, n, dtype=np.float32)
    f = np.linspace(200, 80, n)
    phase = np.cumsum(2 * np.pi * f / _SR)
    w = 0.55 * np.sin(phase) * _envelope(n, 0.002, 0.08)
    noise = 0.08 * (np.random.rand(n).astype(np.float32) * 2 - 1)
    return _make_sound((w + noise).astype(np.float32))


# ----------------------------------------------------------------
# 弃牌声：低软 whoosh（约0.10s）
# ----------------------------------------------------------------
def make_discard_sound() -> pygame.mixer.Sound:
    dur = 0.10
    n = int(dur * _SR)
    t = np.linspace(0, dur, n, dtype=np.float32)
    noise = np.random.rand(n).astype(np.float32) * 2 - 1
    f = np.linspace(500, 150, n)
    phase = np.cumsum(2 * np.pi * f / _SR)
    sweep = np.sin(phase)
    w = 0.3 * (noise * 0.4 + sweep * 0.6) * _envelope(n, 0.005, 0.06)
    return _make_sound(w)


# ----------------------------------------------------------------
# 加赛开始声：短促告警音（约0.25s）
# ----------------------------------------------------------------
def make_tiebreaker_sound() -> pygame.mixer.Sound:
    dur = 0.25
    n = int(dur * _SR)
    t = np.linspace(0, dur, n, dtype=np.float32)
    # 三连击
    w = np.zeros(n, dtype=np.float32)
    seg = n // 3
    for k in range(3):
        s, e = k * seg, (k + 1) * seg
        tt = np.linspace(0, dur / 3, e - s, dtype=np.float32)
        w[s:e] = 0.5 * np.sin(2 * np.pi * (700 + k * 150) * tt) * \
                 _envelope(e - s, 0.005, 0.05)
    return _make_sound(w)


# ----------------------------------------------------------------
# SoundBank — 预生成所有音效，统一管理音量
# ----------------------------------------------------------------
class SoundBank:
    def __init__(self, music_path: str = ""):
        init_audio(music_path)
        self._sounds = {
            'play':        make_play_sound(),
            'reveal':      make_reveal_sound(),
            'score':       make_score_sound(),
            'flip':        make_flip_sound(),
            'special':     make_special_sound(),
            'discard':     make_discard_sound(),
            'tiebreaker':  make_tiebreaker_sound(),
        }
        for s in self._sounds.values():
            s.set_volume(0.7)

    def play(self, name: str):
        """播放指定音效，name 不存在时静默"""
        s = self._sounds.get(name)
        if s:
            s.play()

    def set_sfx_volume(self, vol: float):
        for s in self._sounds.values():
            s.set_volume(max(0.0, min(1.0, vol)))

    def set_music_volume(self, vol: float):
        pygame.mixer.music.set_volume(max(0.0, min(1.0, vol)))

    def toggle_music(self):
        if pygame.mixer.music.get_busy():
            pygame.mixer.music.pause()
        else:
            pygame.mixer.music.unpause()
