# -*- coding: utf-8 -*-
"""GFX2: 牌面渲染（几何花色 + 牌面 + 牌背 + 手牌行）"""
code = r"""
// ===== 枚举前置声明（供牌面渲染使用）=====
enum Suit  { SPADE=0, HEART, CLUB, DIAMOND, JOKER_SUIT };
enum Rank  {
    RANK_A=1,RANK_2,RANK_3,RANK_4,RANK_5,RANK_6,
    RANK_7,RANK_8,RANK_9,RANK_10,RANK_J,RANK_Q,RANK_K,
    RANK_SMALL_JOKER=100, RANK_BIG_JOKER=101
};
enum GameRule { BIG_WINS, SMALL_WINS };

// ===== 花色几何绘制 =====
void drawSuit(int cx,int cy,int r,Suit s){
    if(s==SPADE||s==CLUB) setfillcolor(C_BLK_S);
    else                   setfillcolor(C_RED_S);
    setlinecolor(RGB(0,0,0));
    switch(s){
        case SPADE:{
            // 主体：倒三角 + 两侧圆弧
            int rr=(int)(r*0.48);
            fillcircle(cx-(int)(r*0.38),cy-(int)(r*0.05),rr);
            fillcircle(cx+(int)(r*0.38),cy-(int)(r*0.05),rr);
            POINT body[3]={{cx,cy-r},{cx+r,cy+(int)(r*0.4)},{cx-r,cy+(int)(r*0.4)}};
            fillpolygon(body,3);
            // 柄
            POINT stem[4]={{cx-r/4,cy+(int)(r*0.4)},{cx+r/4,cy+(int)(r*0.4)},
                           {cx+r/3,cy+r},{cx-r/3,cy+r}};
            fillpolygon(stem,4);
            break;
        }
        case HEART:{
            int rr=(int)(r*0.55);
            fillcircle(cx-(int)(r*0.48),cy-(int)(r*0.1),rr);
            fillcircle(cx+(int)(r*0.48),cy-(int)(r*0.1),rr);
            POINT body[3]={{cx-(int)(r*0.95),cy+(int)(r*0.2)},
                           {cx,cy+r},{cx+(int)(r*0.95),cy+(int)(r*0.2)}};
            fillpolygon(body,3);
            break;
        }
        case CLUB:{
            int rr=(int)(r*0.42);
            fillcircle(cx,cy-(int)(r*0.35),rr);
            fillcircle(cx-(int)(r*0.42),cy+(int)(r*0.18),rr);
            fillcircle(cx+(int)(r*0.42),cy+(int)(r*0.18),rr);
            POINT stem[4]={{cx-r/4,cy+(int)(r*0.42)},{cx+r/4,cy+(int)(r*0.42)},
                           {cx+r/3,cy+r},{cx-r/3,cy+r}};
            fillpolygon(stem,4);
            break;
        }
        case DIAMOND:{
            POINT pts[4]={{cx,cy-r},{cx+r,cy},{cx,cy+r},{cx-r,cy}};
            fillpolygon(pts,4);
            break;
        }
        default: break;
    }
}

// ===== 点数字符串 =====
const char* rankStr(Rank r){
    switch(r){
        case RANK_A:  return "A";
        case RANK_2:  return "2";  case RANK_3: return "3";
        case RANK_4:  return "4";  case RANK_5: return "5";
        case RANK_6:  return "6";  case RANK_7: return "7";
        case RANK_8:  return "8";  case RANK_9: return "9";
        case RANK_10: return "10";
        case RANK_J:  return "J";  case RANK_Q: return "Q";
        case RANK_K:  return "K";
        case RANK_SMALL_JOKER: return "小王";
        case RANK_BIG_JOKER:   return "大王";
        default: return "?";
    }
}

// ===== 绘制正面牌 =====
void drawCardFace(int x,int y,int w,int h,Suit s,Rank r,bool isJoker,bool selected=false,bool returned=false){
    // 选中高亮外框
    if(selected){
        fillRR(x-4,y-4,w+8,h+8,12,C_SEL,C_SEL,3);
    }
    // 牌面底色
    COLORREF cardBg = C_CARD_W;
    fillRR(x,y,w,h,8,cardBg,selected?C_SEL:RGB(190,185,178),selected?2:1);

    if(isJoker){
        COLORREF jc=(r==RANK_BIG_JOKER)?C_JOKER_R:C_JOKER_B;
        COLORREF jc2=(r==RANK_BIG_JOKER)?RGB(255,180,0):RGB(120,120,240);
        dtC(x+w/2,y+h/2-12,rankStr(r),jc,19,true);
        // 小装饰
        setfillcolor(jc2); setlinecolor(jc2);
        fillcircle(x+12,y+12,5); fillcircle(x+w-12,y+h-12,5);
        return;
    }
    COLORREF suitC=(s==HEART||s==DIAMOND)?C_RED_S:C_BLK_S;
    // 左上角点数
    dtL(x+5,y+4, rankStr(r), suitC, 15, true);
    // 中央花色
    drawSuit(x+w/2,y+h/2, w/5, s);
    // 右下角点数（小）
    dtR(x+w-5,y+h-20, rankStr(r), suitC, 13, false);
    // 收回标记
    if(returned){
        setlinecolor(C_WARN);
        setlinestyle(PS_DOT,1);
        roundrect(x+2,y+2,x+w-2,y+h-2,6,6);
        dtC(x+w-10,y+10,"*",C_WARN,11,true);
    }
}

// ===== 绘制牌背 =====
void drawCardBack(int x,int y,int w,int h){
    fillRR(x,y,w,h,8,C_CARD_B,RGB(20,45,100),2);
    // 内部菱形花纹
    int inset=8;
    COLORREF pat=RGB(45,85,175);
    setlinecolor(pat);
    setlinestyle(PS_SOLID,1);
    line(x+inset,y+h/2, x+w/2,y+inset);
    line(x+w/2,y+inset, x+w-inset,y+h/2);
    line(x+w-inset,y+h/2, x+w/2,y+h-inset);
    line(x+w/2,y+h-inset, x+inset,y+h/2);
}

// ===== Card前置（供绘制函数用）=====
struct Card;
void drawCard(int x,int y,int w,int h,const Card& c,bool faceUp,bool selected=false);
"""
with open(r'd:\Users\ymx36\Desktop\三雄争锋游戏\三雄争锋v3.cpp','a',encoding='gbk') as f:
    f.write(code)
print("GFX2 OK - 牌面渲染写入完成")
