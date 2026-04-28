# -*- coding: utf-8 -*-
"""生成游戏海报 JPG"""
try:
    from PIL import Image, ImageDraw, ImageFont
    import os

    W, H = 1200, 800
    img = Image.new('RGB', (W, H), (10, 15, 35))
    draw = ImageDraw.Draw(img)

    # 尝试加载中文字体
    font_paths = [
        r'C:\Windows\Fonts\msyh.ttc',
        r'C:\Windows\Fonts\simsun.ttc',
        r'C:\Windows\Fonts\simhei.ttf',
        r'C:\Windows\Fonts\STZHONGS.TTF',
    ]
    def get_font(size):
        for p in font_paths:
            if os.path.exists(p):
                try: return ImageFont.truetype(p, size)
                except: pass
        return ImageFont.load_default()

    fnt_huge  = get_font(96)
    fnt_large = get_font(48)
    fnt_med   = get_font(32)
    fnt_small = get_font(24)
    fnt_tiny  = get_font(20)

    # 背景渐变效果（简单横向条纹）
    for y in range(H):
        alpha = int(y / H * 40)
        draw.line([(0,y),(W,y)], fill=(10+alpha//3, 15+alpha//2, 35+alpha))

    # 顶部装饰条
    draw.rectangle([0,0,W,8], fill=(220,180,0))
    draw.rectangle([0,H-8,W,H], fill=(220,180,0))

    # 标题
    draw.text((W//2, 70), "三雄争锋", font=fnt_huge,
              fill=(255, 215, 0), anchor='mm')
    draw.text((W//2, 160), "San Xiong Zheng Feng  ·  Card Battle Game v2.0",
              font=fnt_small, fill=(180,180,180), anchor='mm')

    # 分隔线
    draw.line([(60,195),(W-60,195)], fill=(220,180,0), width=2)

    # 左列：游戏简介 + 功能
    lx = 80
    draw.text((lx, 220), "【游戏简介】", font=fnt_med, fill=(100,200,255))
    items = [
        "· 三人纸牌对战，54张标准牌",
        "· 每人18张，共18局，积分制胜",
        "· 比大/比小规则动态切换",
        "· 支持人机对战 & 单人挑战",
    ]
    for i,t in enumerate(items):
        draw.text((lx, 265+i*38), t, font=fnt_small, fill=(220,220,220))

    draw.text((lx, 440), "【主要特色】", font=fnt_med, fill=(100,200,255))
    features = [
        "★  5号牌狸猫换太子机制",
        "★  大王防御 / 小王偷窥",
        "★  连顺触发随机抽牌",
        "★  连续开局·积分继承",
        "★  加赛决胜制",
        "★  彩色控制台图形界面",
    ]
    for i,t in enumerate(features):
        draw.text((lx, 485+i*38), t, font=fnt_small, fill=(255,230,100))

    # 中间分隔
    draw.line([(W//2-10, 210),(W//2-10, H-30)], fill=(50,80,120), width=2)

    # 右列：技术栈 + 目标人群 + 下载
    rx = W//2 + 30
    draw.text((rx, 220), "【技术栈】", font=fnt_med, fill=(100,200,255))
    tech = [
        "· C++11  /  Dev-C++ 5.11",
        "· Windows Console API",
        "· STL (vector / random / chrono)",
        "· OOP 面向对象设计",
    ]
    for i,t in enumerate(tech):
        draw.text((rx, 265+i*38), t, font=fnt_small, fill=(200,230,200))

    draw.text((rx, 440), "【面向人群】", font=fnt_med, fill=(100,200,255))
    audience = [
        "· 喜爱策略卡牌的玩家",
        "· 3人聚会休闲娱乐",
        "· 程序设计课程学习参考",
    ]
    for i,t in enumerate(audience):
        draw.text((rx, 485+i*38), t, font=fnt_small, fill=(220,220,220))

    # 底部广告语
    draw.line([(60,680),(W-60,680)], fill=(220,180,0), width=2)
    draw.text((W//2, 710), "★  欢迎下载体验，与朋友一起三雄争锋！  ★",
              font=fnt_med, fill=(255,215,0), anchor='mm')
    draw.text((W//2, 755), "下载地址: github.com/yourname/sanxiong  |  开发团队: XXXXX组",
              font=fnt_tiny, fill=(150,150,150), anchor='mm')

    # 右上角小徽章
    draw.ellipse([W-120, 20, W-20, 120], fill=(180,30,30), outline=(255,215,0), width=3)
    draw.text((W-70, 70), "NEW", font=get_font(28), fill=(255,255,255), anchor='mm')

    out_path = r'd:\Users\ymx36\Desktop\三雄争锋游戏\游戏海报.jpg'
    img.save(out_path, 'JPEG', quality=95)
    print("海报 OK - 已生成: " + out_path)

except ImportError:
    print("Pillow未安装，正在安装...")
    import subprocess
    subprocess.call(['pip','install','pillow'])
    print("请重新运行 gen_poster.py")
except Exception as e:
    print("海报生成失败: " + str(e))
