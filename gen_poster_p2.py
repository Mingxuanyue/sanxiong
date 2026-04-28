# -*- coding: utf-8 -*-
"""gen_poster_p2.py — 海报第二层：游戏界面示意图 + 所有文字内容 -> 最终JPG"""
try:
    from PIL import Image, ImageDraw, ImageFont
    import os

    bg_path = r'd:\Users\ymx36\Desktop\三雄争锋游戏\_poster_bg.png'
    img = Image.open(bg_path).convert('RGB')
    draw = ImageDraw.Draw(img)
    W, H = img.size   # 1280 x 820

    # ── 字体 ──────────────────────────────────────────────────────────────
    font_paths = [
        r'C:\Windows\Fonts\msyh.ttc',
        r'C:\Windows\Fonts\simsun.ttc',
        r'C:\Windows\Fonts\simhei.ttf',
    ]
    def gf(size):
        for p in font_paths:
            if os.path.exists(p):
                try: return ImageFont.truetype(p, size)
                except: pass
        return ImageFont.load_default()

    # ══════════════════════════════════════════════════════════════════════
    # 左下：用实际游戏截图替换手绘示意图
    # ══════════════════════════════════════════════════════════════════════
    PX, PY, PW, PH = 18, 432, 574, 375

    scr_path = r'd:\Users\ymx36\Desktop\三雄争锋游戏\屏幕截图 2026-04-29 033532.png'
    scr = Image.open(scr_path).convert('RGB')
    sw, sh = scr.size

    # 允许裁掉最下面 1/25 高度
    crop_bottom = sh // 25
    scr = scr.crop((0, 0, sw, sh - crop_bottom))
    sw, sh = scr.size

    # 按比例缩放：整体塞进 PW x PH，保持比例（不再裁剪）
    scale = min(PW / sw, PH / sh)
    new_w, new_h = int(sw * scale), int(sh * scale)
    scr = scr.resize((new_w, new_h), Image.LANCZOS)

    # 居中粘贴到面板区域（上对齐，水平居中）
    paste_x = PX + (PW - new_w) // 2
    paste_y = PY + (PH - new_h) // 2
    img.paste(scr, (paste_x, paste_y))

    # 面板边框
    draw.rectangle([PX, PY, PX + PW, PY + PH], outline=(80, 130, 220), width=2)

    # ══════════════════════════════════════════════════════════════════════
    # 左上：团队合照（完整不裁，按比例缩放放入左上角）
    # ══════════════════════════════════════════════════════════════════════
    photo_path = r'd:\Users\ymx36\Desktop\三雄争锋游戏\dfa04211d212f6afc7ff802f0d5557b7.jpg'
    import os as _os
    if _os.path.exists(photo_path):
        from PIL import Image as _PIL2
        photo = _PIL2.open(photo_path).convert('RGB')
        pw, ph = photo.size
        # 可用区域：左上，x=18~592, y=20~390（避开顶金条和截图标签栏）
        max_pw, max_ph = 574, 368
        scale_p = min(max_pw / pw, max_ph / ph)
        nw, nh = int(pw * scale_p), int(ph * scale_p)
        photo = photo.resize((nw, nh), _PIL2.LANCZOS)
        # 左对齐，顶部留8px给金条后紧靠
        photo_x = 18 + (max_pw - nw) // 2
        photo_y = 20
        img.paste(photo, (photo_x, photo_y))
        # 边框
        draw.rectangle([photo_x-2, photo_y-2, photo_x+nw+1, photo_y+nh+1],
                        outline=(80, 130, 220), width=2)

        # ── 顶部标题：开发人员合影 ───────────────────────────────────────
        draw.rectangle([photo_x, photo_y, photo_x+nw, photo_y+28], fill=(10, 20, 60))
        draw.text((photo_x + nw//2, photo_y + 14), "开发人员合影",
                  font=gf(16), fill=(255, 215, 0), anchor='mm')

        # ── 人员姓名标注（各自实际站位位置） ──────────────────────────────
        # 雷浩阳：靠近左边缘，高度在照片中偏下（约55%处）
        # 岳明轩：中间偏右，底部附近
        # 郭晓磊：右侧1/3，底部附近
        per_w = nw // 3
        persons = [
            ("雷浩阳", photo_x + int(per_w * 0.15),       photo_y + int(nh * 0.55)),
            ("岳明轩", photo_x + per_w + per_w // 2,       photo_y + nh - 36),
            ("郭晓磊", photo_x + per_w * 2 + per_w // 2,  photo_y + nh - 36),
        ]
        for name, cx, name_y in persons:
            nb_w = len(name) * 14 + 16
            draw.rectangle([cx - nb_w//2, name_y - 2, cx + nb_w//2, name_y + 20],
                            fill=(6, 12, 40))
            draw.text((cx, name_y + 9), name, font=gf(14), fill=(255, 220, 80), anchor='mm')
            draw.line([(cx, name_y - 2), (cx, name_y - 16)], fill=(255, 220, 80), width=1)
            draw.polygon([(cx-4, name_y-16), (cx+4, name_y-16), (cx, name_y-24)],
                          fill=(255, 220, 80))

        # 标签贴在合照下方
        label_y = photo_y + nh + 4
        draw.rectangle([18, label_y, 18+max_pw, label_y+24], fill=(12, 24, 70))
        draw.text((18 + max_pw//2, label_y + 12),
                  "不知道叫啥小组  ·  开发团队合影  ·  2026",
                  font=gf(16), fill=(220, 185, 60), anchor='mm')



    # 左侧中间：版本/平台标签（y=370~415，紧贴游戏界面面板上方）
    draw.rectangle([8, 396, 590, 430], fill=(14, 24, 70))
    draw.line([(8, 396), (590, 396)], fill=(80, 130, 220), width=1)
    draw.line([(8, 430), (590, 430)], fill=(80, 130, 220), width=1)
    draw.text((299, 413), "▼  EasyX GUI 实际运行截图  ·  人机对战模式  ▼",
              font=gf(18), fill=(140, 180, 240), anchor='mm')

    # ══════════════════════════════════════════════════════════════════════
    # 右侧文字区
    # ══════════════════════════════════════════════════════════════════════
    rx = 622

    # ── 小组名称（顶部小字，右侧区域不再重复，与左侧标签互补） ────────────
    draw.text((rx, 14), "Card Battle  ·  C++  ·  v2.0", font=gf(17), fill=(120, 120, 120))

    # ── 主标题 ────────────────────────────────────────────────────────────
    draw.text((rx, 38), "三雄争锋", font=gf(72), fill=(255, 210, 0))
    draw.text((rx, 122), "San Xiong Zheng Feng  ·  Card Battle  v2.0",
              font=gf(17), fill=(155, 155, 155))

    draw.line([(rx, 152), (W - 28, 152)], fill=(200, 160, 0), width=2)

    # ── 游戏简介 ──────────────────────────────────────────────────────────
    draw.text((rx, 162), "【游戏简介】", font=gf(28), fill=(100, 200, 255))
    intros = [
        "· 三人纸牌对战，54张标准牌（含大小王）",
        "· 每人18张，共18局，积分决胜，支持加赛",
        "· 比大/比小规则局间动态切换",
    ]
    for i, t in enumerate(intros):
        draw.text((rx, 200 + i * 30), t, font=gf(21), fill=(215, 215, 215))

    # ── 面向人群 ──────────────────────────────────────────────────────────
    draw.text((rx, 298), "【面向人群】", font=gf(28), fill=(100, 200, 255))
    audiences = [
        "· 喜爱策略卡牌 / 休闲对战游戏的玩家",
        "· 对 C++ 游戏开发感兴趣的学习者",
    ]
    for i, t in enumerate(audiences):
        draw.text((rx, 335 + i * 30), t, font=gf(21), fill=(215, 215, 215))

    # ── 特色机制 ──────────────────────────────────────────────────────────
    draw.text((rx, 402), "【特色机制】", font=gf(28), fill=(100, 200, 255))
    features = [
        ("★", "10号牌 顺手牵羊 · 独占出牌，一招搅乱局势"),
        ("★", "5号牌 狸猫换太子 · 消耗撤回，神出鬼没"),
        ("★", "连顺触发抽牌 · 三连爆发随机获牌"),
        ("★", "大王防御 / 小王偷窥 · 王牌双效"),
        ("★", "平局追加补分 · 同点反转规则"),
        ("★", "加赛决胜 · 连续多场积分继承"),
    ]
    for i, (sym, txt) in enumerate(features):
        y = 440 + i * 31
        draw.text((rx,      y), sym, font=gf(20), fill=(255, 200, 50))
        draw.text((rx + 24, y), txt, font=gf(20), fill=(240, 240, 200))

    # ── 技术栈 ────────────────────────────────────────────────────────────
    draw.line([(rx, 632), (W - 28, 632)], fill=(50, 80, 150), width=1)
    draw.text((rx, 641), "技术栈:  C++11  |  Dev-C++ 5.11  |  Windows Console API  |  OOP",
              font=gf(17), fill=(120, 160, 200))

    # ── 下载链接 ──────────────────────────────────────────────────────────
    draw.line([(rx, 672), (W - 28, 672)], fill=(200, 160, 0), width=1)
    draw.text((rx, 682), "免费下载:", font=gf(20), fill=(255, 215, 0))
    draw.text((rx, 708), "github.com/Mingxuanyue/sanxiong",
              font=gf(19), fill=(100, 180, 255))
    draw.text((rx, 730), "Releases -> sanxiong.exe  直接双击运行，无需安装",
              font=gf(15), fill=(140, 140, 140))

    # ── 广告语 ────────────────────────────────────────────────────────────
    draw.line([(rx, 754), (W - 28, 754)], fill=(200, 160, 0), width=1)
    mid_x = (rx + W) // 2
    draw.text((mid_x, 776),
              "★  欢迎下载体验，与朋友一起三雄争锋！  ★",
              font=gf(24), fill=(255, 215, 0), anchor='mm')
    draw.text((mid_x, 803),
              "不知道叫啥小组  |  2026  |  v2.0",
              font=gf(16), fill=(120, 120, 120), anchor='mm')

    # ── NEW 徽章 ──────────────────────────────────────────────────────────
    draw.ellipse([W - 112, 20, W - 22, 110],
                 fill=(180, 30, 30), outline=(255, 215, 0), width=3)
    draw.text((W - 67, 65), "NEW", font=gf(25), fill=(255, 255, 255), anchor='mm')

    # ── 输出最终海报 ──────────────────────────────────────────────────────
    out = r'd:\Users\ymx36\Desktop\三雄争锋游戏\游戏海报.jpg'
    img.save(out, 'JPEG', quality=95)
    print("P2 OK - 最终海报已生成: " + out)

except Exception as e:
    import traceback
    print("P2 FAIL: " + str(e))
    traceback.print_exc()
