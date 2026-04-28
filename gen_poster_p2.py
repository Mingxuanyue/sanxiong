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
    # 左下：游戏主界面示意图（在P1预留的面板上绘制内容）
    # ══════════════════════════════════════════════════════════════════════
    PX, PY, PW, PH = 18, 432, 574, 375

    # 面板标题
    draw.text((PX + PW // 2, PY + 16), "<<  游戏主界面  >>",
              font=gf(18), fill=(160, 200, 255), anchor='mm')

    # ── 绘制牌的辅助函数 ─────────────────────────────────────────────────
    def draw_card(x, y, suit, num, col):
        draw.rectangle([x, y, x+33, y+45], fill=(245, 245, 245), outline=(140, 140, 140), width=1)
        draw.text((x + 3, y + 2), suit, font=gf(12), fill=col)
        draw.text((x + 3, y + 14), num, font=gf(14), fill=col)

    def draw_back(x, y):
        draw.rectangle([x, y, x+33, y+45], fill=(25, 55, 140), outline=(80, 120, 200), width=1)
        draw.rectangle([x+4, y+4, x+29, y+41], fill=(18, 40, 110), outline=(60, 100, 180), width=1)

    RED = (210, 40, 40)
    BLK = (30, 30, 30)

    # AI玩家1 行
    ay1 = PY + 42
    draw.text((PX + 6, ay1 + 13), "电脑1", font=gf(15), fill=(140, 200, 140))
    for i in range(7):
        draw_back(PX + 52 + i * 38, ay1)

    # AI玩家2 行
    ay2 = PY + 100
    draw.text((PX + 6, ay2 + 13), "电脑2", font=gf(15), fill=(140, 200, 140))
    for i in range(7):
        draw_back(PX + 52 + i * 38, ay2)

    # 规则/进度条
    ry = PY + 156
    draw.rectangle([PX + 4, ry, PX + PW - 4, ry + 26], fill=(14, 28, 75))
    draw.text((PX + PW // 2, ry + 13),
              "当前规则: 比大  |  第 5 局 / 18  |  得分  电脑1:2  电脑2:1  你:3",
              font=gf(14), fill=(255, 215, 0), anchor='mm')

    # 桌面出牌
    ty = PY + 192
    draw.text((PX + 6, ty + 13), "桌面:", font=gf(15), fill=(180, 180, 180))
    table = [("♠", "A", BLK), ("♥", "K", RED), ("♦", "7", RED)]
    for i, (s, n, c) in enumerate(table):
        draw_card(PX + 58 + i * 42, ty, s, n, c)
    draw.text((PX + 60, ty - 14), "独占", font=gf(12), fill=(255, 140, 0))

    # 分隔线
    draw.line([(PX + 4, PY + 248), (PX + PW - 4, PY + 248)],
              fill=(50, 80, 150), width=1)

    # 你的手牌
    hy = PY + 258
    draw.text((PX + 6, hy), "你的手牌:", font=gf(15), fill=(255, 215, 0))
    hand = [("♠","3",BLK), ("♥","5",RED), ("♣","10",BLK),
            ("♦","J",RED), ("♠","Q",BLK), ("♥","K",RED), ("♣","A",BLK)]
    for i, (s, n, c) in enumerate(hand):
        draw_card(PX + 6 + i * 80, hy + 24, s, n, c)
    draw.text((PX + 6 + 82, hy + 24 - 14), "撤回", font=gf(12), fill=(100, 220, 255))

    # 操作按钮示意
    by = PY + PH - 42
    btns = [("出  牌", (30, 90, 50), (80, 200, 100)),
            ("查看规则", (80, 50, 10), (220, 160, 50)),
            ("使用特殊牌", (90, 20, 20), (200, 70, 70))]
    bx = PX + 4
    for label, bg_c, fg_c in btns:
        bw = len(label) * 13 + 20
        draw.rectangle([bx, by, bx + bw, by + 28], fill=bg_c, outline=fg_c, width=1)
        draw.text((bx + bw // 2, by + 14), label, font=gf(14), fill=fg_c, anchor='mm')
        bx += bw + 12

    # ══════════════════════════════════════════════════════════════════════
    # 左侧上半：合照区标注（填补左上空白，叠加半透明条）
    # ══════════════════════════════════════════════════════════════════════
    from PIL import Image as _PIL
    # 顶部左侧标签条（y=8~48）
    tag_ov = _PIL.new('RGBA', (W, H), (0, 0, 0, 0))
    td = ImageDraw.Draw(tag_ov)
    td.rectangle([8, 8, 590, 50], fill=(6, 10, 28, 180))
    td.rectangle([8, 8, 590, 50], outline=(80, 130, 220, 180))
    img_rgba3 = img.convert('RGBA')
    img_rgba3 = _PIL.alpha_composite(img_rgba3, tag_ov)
    img = img_rgba3.convert('RGB')
    draw = ImageDraw.Draw(img)
    draw.text((20, 29), "不知道叫啥小组  ·  开发团队合影  ·  2026",
              font=gf(20), fill=(220, 185, 60), anchor='lm')

    # 左侧中间：版本/平台标签（y=370~415，紧贴游戏界面面板上方）
    draw.rectangle([8, 396, 590, 430], fill=(14, 24, 70))
    draw.line([(8, 396), (590, 396)], fill=(80, 130, 220), width=1)
    draw.line([(8, 430), (590, 430)], fill=(80, 130, 220), width=1)
    draw.text((299, 413), "▼  游戏运行截图  ·  Windows  ·  人机对战模式  ▼",
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
        ("★", "小概率动态补分 · 规则随机反转"),
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
