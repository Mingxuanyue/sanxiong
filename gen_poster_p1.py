# -*- coding: utf-8 -*-
"""gen_poster_p1.py — 海报第一层：合照铺满全背景 + 右侧深色蒙版"""
try:
    from PIL import Image, ImageDraw
    import os

    W, H = 1280, 820

    # ── 建立画布（深色兜底，万一照片不存在） ──────────────────────────────
    img = Image.new('RGB', (W, H), (8, 12, 30))
    draw = ImageDraw.Draw(img)

    photo_path = r'd:\Users\ymx36\Desktop\三雄争锋游戏\dfa04211d212f6afc7ff802f0d5557b7.jpg'
    if os.path.exists(photo_path):
        photo = Image.open(photo_path).convert('RGB')
        pw, ph = photo.size
        # 等比缩放：让宽度恰好铺满 W，高度等比变化
        new_w = W
        new_h = int(ph * W / pw)
        photo = photo.resize((new_w, new_h), Image.LANCZOS)
        # 垂直裁剪：从顶部保留（保住脸部），超出部分从底部截去
        if new_h > H:
            photo = photo.crop((0, 0, W, H))
        # 若高度不足则居中粘贴，上下补黑
        paste_y = max(0, (H - new_h) // 2)
        img.paste(photo, (0, paste_y))
        print("合照已铺满背景 (原始尺寸 %dx%d -> 缩放到 %dx%d)" % (pw, ph, new_w, new_h))
    else:
        # 占位渐变背景
        for y in range(H):
            r = int(8  + y/H * 30)
            g = int(12 + y/H * 20)
            b = int(30 + y/H * 45)
            draw.line([(0, y), (W, y)], fill=(r, g, b))
        print("警告：合照文件不存在，使用渐变占位背景")

    # ── 右半深色渐变蒙版（x=500~1280），保证文字可读 ──────────────────────
    overlay = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    od = ImageDraw.Draw(overlay)
    # 渐变蒙版：x=500 透明度0 -> x=700 透明度150 -> x=1280 透明度210
    for x in range(W):
        if x < 500:
            alpha = 0
        elif x < 700:
            alpha = int((x - 500) / 200 * 150)
        else:
            alpha = int(150 + (x - 700) / 580 * 60)
        od.line([(x, 0), (x, H)], fill=(5, 8, 28, alpha))
    img_rgba = img.convert('RGBA')
    img_rgba = Image.alpha_composite(img_rgba, overlay)
    img = img_rgba.convert('RGB')
    draw = ImageDraw.Draw(img)

    # ── 左下：游戏界面示意图面板（半透明深色蒙版） ─────────────────────────
    PX, PY, PW, PH = 18, 432, 574, 375
    panel_ov = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    pd = ImageDraw.Draw(panel_ov)
    pd.rectangle([PX, PY, PX+PW, PY+PH], fill=(6, 10, 28, 210))
    pd.rectangle([PX, PY, PX+PW, PY+PH], outline=(60, 100, 200, 255))
    img_rgba2 = img.convert('RGBA')
    img_rgba2 = Image.alpha_composite(img_rgba2, panel_ov)
    img = img_rgba2.convert('RGB')
    draw = ImageDraw.Draw(img)
    # 面板头部条
    draw.rectangle([PX, PY, PX+PW, PY+32], fill=(18, 38, 100))
    draw.line([(PX, PY+32), (PX+PW, PY+32)], fill=(80, 130, 220), width=1)

    # 顶部/底部金色装饰条 ─────────────────────────────────────────────────
    draw.rectangle([0, 0, W, 7],   fill=(200, 160, 0))
    draw.rectangle([0, H-7, W, H], fill=(200, 160, 0))

    # ── 保存中间层（供P2叠加文字）────────────────────────────────────────
    out = r'd:\Users\ymx36\Desktop\三雄争锋游戏\_poster_bg.png'
    img.save(out, 'PNG')
    print("P1 OK - 背景层已保存: " + out)

except Exception as e:
    print("P1 FAIL: " + str(e))
