# -*- coding: utf-8 -*-
"""gen_poster_p1.py — 海报第一层：设计感背景（暗蓝几何 + 卡牌花色装饰）"""
try:
    from PIL import Image, ImageDraw
    import math, random

    W, H = 1280, 820
    img = Image.new('RGB', (W, H), (8, 12, 30))
    draw = ImageDraw.Draw(img)

    # ── 垂直渐变背景 ──────────────────────────────────────────────────────
    for y in range(H):
        t = y / H
        r = int(8  + t * 10)
        g = int(12 + t * 8)
        b = int(30 + t * 28)
        draw.line([(0, y), (W, y)], fill=(r, g, b))

    # ── 斜线网格（低透明度几何感） ──────────────────────────────────────────
    ov_grid = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    gd = ImageDraw.Draw(ov_grid)
    step = 72
    for i in range(-H // step, (W + H) // step + 2):
        x0 = i * step
        gd.line([(x0, 0), (x0 + H, H)], fill=(60, 100, 180, 18), width=1)
        gd.line([(x0 + H, 0), (x0, H)], fill=(60, 100, 180, 14), width=1)
    img = Image.alpha_composite(img.convert('RGBA'), ov_grid).convert('RGB')
    draw = ImageDraw.Draw(img)

    # ── 发光圆斑（模拟光晕） ──────────────────────────────────────────────
    ov_glow = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    gw = ImageDraw.Draw(ov_glow)
    glows = [
        (960, 160, 260, (80, 40, 140, 40)),
        (200, 640, 180, (20, 60, 160, 35)),
        (1100, 680, 200, (40, 20, 100, 30)),
        (550, 300, 140, (30, 80, 180, 25)),
    ]
    for (cx, cy, radius, col) in glows:
        for dr in range(radius, 0, -6):
            a = int(col[3] * (1 - dr / radius) * 2)
            gw.ellipse([cx-dr, cy-dr, cx+dr, cy+dr], fill=(col[0], col[1], col[2], min(a, 80)))
    img = Image.alpha_composite(img.convert('RGBA'), ov_glow).convert('RGB')
    draw = ImageDraw.Draw(img)

    # ── 散布卡牌花色装饰符号（低透明度） ─────────────────────────────────
    try:
        from PIL import ImageFont
        font_paths = [r'C:\Windows\Fonts\seguisym.ttf', r'C:\Windows\Fonts\wingding.ttf']
        suit_font = None
        for fp in font_paths:
            import os
            if os.path.exists(fp):
                try:
                    suit_font = ImageFont.truetype(fp, 64)
                    break
                except: pass
    except: suit_font = None

    ov_suits = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    sd = ImageDraw.Draw(ov_suits)
    suits_data = [
        (120, 80,  '♠', (180, 180, 220, 22)),
        (520, 200, '♥', (220, 80,  80,  20)),
        (380, 700, '♣', (160, 200, 160, 18)),
        (700, 560, '♦', (220, 120, 80,  20)),
        (80,  500, '♠', (150, 160, 210, 16)),
        (460, 400, '♥', (200, 70,  70,  15)),
        (300, 300, '♦', (200, 120, 80,  14)),
        (550, 720, '♣', (140, 190, 140, 18)),
    ]
    if suit_font:
        for (sx, sy, ch, col) in suits_data:
            sd.text((sx, sy), ch, font=suit_font, fill=col)
    else:
        # 无符号字体时用小圆圈替代
        for (sx, sy, ch, col) in suits_data:
            r2 = 22
            sd.ellipse([sx, sy, sx+r2*2, sy+r2*2], fill=col)
    img = Image.alpha_composite(img.convert('RGBA'), ov_suits).convert('RGB')
    draw = ImageDraw.Draw(img)

    # ── 右半深色渐变蒙版（x=600~1280），保证文字可读 ──────────────────────
    overlay = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    od = ImageDraw.Draw(overlay)
    for x in range(W):
        if x < 600:
            alpha = 0
        elif x < 760:
            alpha = int((x - 600) / 160 * 140)
        else:
            alpha = int(140 + (x - 760) / 520 * 70)
        od.line([(x, 0), (x, H)], fill=(5, 8, 22, alpha))
    img = Image.alpha_composite(img.convert('RGBA'), overlay).convert('RGB')
    draw = ImageDraw.Draw(img)

    # ── 左下游戏截图面板（半透明深色蒙版） ───────────────────────────────
    PX, PY, PW, PH = 18, 432, 574, 375
    panel_ov = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    pd = ImageDraw.Draw(panel_ov)
    pd.rectangle([PX, PY, PX+PW, PY+PH], fill=(6, 10, 28, 200))
    pd.rectangle([PX, PY, PX+PW, PY+PH], outline=(60, 100, 200, 255))
    img = Image.alpha_composite(img.convert('RGBA'), panel_ov).convert('RGB')
    draw = ImageDraw.Draw(img)
    draw.rectangle([PX, PY, PX+PW, PY+32], fill=(18, 38, 100))
    draw.line([(PX, PY+32), (PX+PW, PY+32)], fill=(80, 130, 220), width=1)

    # ── 顶部/底部金色装饰条 ───────────────────────────────────────────────
    draw.rectangle([0, 0, W, 7],   fill=(200, 160, 0))
    draw.rectangle([0, H-7, W, H], fill=(200, 160, 0))

    # ── 保存中间层（供P2叠加）────────────────────────────────────────────
    out = r'd:\Users\ymx36\Desktop\三雄争锋游戏\_poster_bg.png'
    img.save(out, 'PNG')
    print("P1 OK - 背景层已保存: " + out)

except Exception as e:
    import traceback
    print("P1 FAIL: " + str(e))
    traceback.print_exc()

