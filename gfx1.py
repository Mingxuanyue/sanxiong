# -*- coding: utf-8 -*-
"""GFX1: 文件头 + 全局常量 + 字体/绘图工具 + Btn + 事件循环"""
code = r"""/*
 * 三雄争锋 v3.0 (EasyX 图形界面版)
 * 编译: Dev-C++ 5.11, C++11
 * 依赖: 需先安装 EasyX 图形库 (https://easyx.cn)
 * 编译选项: -std=c++11
 * 字符编码: ANSI/GBK
 */
#include <graphics.h>
#include <conio.h>
#include <iostream>
#include <vector>
#include <string>
#include <algorithm>
#include <random>
#include <ctime>
#include <windows.h>
#include <functional>
#include <sstream>
#include <iomanip>
using namespace std;

// ===== 窗口尺寸 =====
const int WIN_W = 1280;
const int WIN_H = 800;
const int CARD_W = 78;
const int CARD_H = 108;

// ===== 颜色常量 =====
const COLORREF C_TABLE    = RGB(22, 100, 52);
const COLORREF C_TABLE_D  = RGB(14, 72, 36);
const COLORREF C_CARD_W   = RGB(255, 252, 244);
const COLORREF C_CARD_B   = RGB(32, 62, 148);
const COLORREF C_RED_S    = RGB(200, 28, 28);
const COLORREF C_BLK_S    = RGB(14, 14, 14);
const COLORREF C_GOLD     = RGB(255, 208, 0);
const COLORREF C_SILVER   = RGB(175, 188, 200);
const COLORREF C_PANEL    = RGB(10, 52, 26);
const COLORREF C_PANEL_D  = RGB(6, 38, 18);
const COLORREF C_SEL      = RGB(255, 232, 50);
const COLORREF C_BTN_N    = RGB(28, 108, 62);
const COLORREF C_BTN_H    = RGB(48, 158, 82);
const COLORREF C_BTN_DIS  = RGB(70, 80, 74);
const COLORREF C_WHITE    = RGB(255, 255, 255);
const COLORREF C_TEXT     = RGB(228, 228, 228);
const COLORREF C_DIM      = RGB(118, 118, 118);
const COLORREF C_WARN     = RGB(255, 158, 28);
const COLORREF C_RED_T    = RGB(218, 55, 55);
const COLORREF C_BLUE_T   = RGB(78, 158, 238);
const COLORREF C_GREEN_T  = RGB(78, 198, 98);
const COLORREF C_JOKER_R  = RGB(198, 28, 28);
const COLORREF C_JOKER_B  = RGB(58, 58, 198);

// ===== 布局区域 =====
// 顶部信息栏
const int BAR_H  = 56;
// AI1 区 (players[1]) - 顶部左
const int AI1_X = 10,  AI1_Y = BAR_H+4,  AI1_W = 580, AI1_H = 148;
// AI2 区 (players[2]) - 顶部右
const int AI2_X = 598, AI2_Y = BAR_H+4,  AI2_W = 674, AI2_H = 148;
// 桌面区 - 中央（打出的牌 + 消息）
const int TBL_X = 10,  TBL_Y = BAR_H+158, TBL_W = 1262, TBL_H = 310;
// 人类手牌区 - 底部
const int HND_X = 10,  HND_Y = BAR_H+474, HND_W = 1082, HND_H = 186;
// 操作按钮区 - 右下
const int ACT_X = 1098,ACT_Y = BAR_H+474, ACT_W = 174,  ACT_H = 186;

// ===== 字体工具 =====
void setFont(int sz, bool bold=false, const char* face="微软雅黑"){
    LOGFONT lf={};
    lf.lfHeight=sz;
    lf.lfWeight=bold?FW_BOLD:FW_NORMAL;
    lf.lfQuality=CLEARTYPE_QUALITY;
    strcpy(lf.lfFaceName, face);
    settextstyle(&lf);
    setbkmode(TRANSPARENT);
}
void dtC(int cx,int cy,const char* t,COLORREF c,int sz=18,bool b=false){
    setFont(sz,b); settextcolor(c);
    int tw=textwidth(t),th=textheight(t);
    outtextxy(cx-tw/2,cy-th/2,t);
}
void dtL(int x,int y,const char* t,COLORREF c,int sz=18,bool b=false){
    setFont(sz,b); settextcolor(c); outtextxy(x,y,t);
}
void dtR(int rx,int y,const char* t,COLORREF c,int sz=18,bool b=false){
    setFont(sz,b); settextcolor(c); outtextxy(rx-textwidth(t),y,t);
}

// ===== 绘图工具 =====
void fillRR(int x,int y,int w,int h,int r,COLORREF f,COLORREF lc=RGB(0,0,0),int lw=1){
    setfillcolor(f); setlinecolor(lc); setlinestyle(PS_SOLID,lw);
    fillroundrect(x,y,x+w,y+h,r,r);
}
void drawRR(int x,int y,int w,int h,int r,COLORREF lc,int lw=2){
    setlinecolor(lc); setlinestyle(PS_SOLID,lw);
    setfillcolor(NULLBRUSH);
    roundrect(x,y,x+w,y+h,r,r);
}
// 区域填充（矩形背景）
void fillArea(int x,int y,int w,int h,COLORREF f,COLORREF lc=RGB(0,0,0),int r=6){
    fillRR(x,y,w,h,r,f,lc);
}

// ===== 按钮 =====
struct Btn {
    int x,y,w,h;
    string label;
    int fs;
    bool enabled;
    Btn()=default;
    Btn(int x,int y,int w,int h,const string& l,int fs=19,bool en=true)
        :x(x),y(y),w(w),h(h),label(l),fs(fs),enabled(en){}
    bool hit(int mx,int my) const {
        return enabled && mx>=x && mx<=x+w && my>=y && my<=y+h;
    }
    void draw(bool hov=false) const {
        if(!enabled){
            fillRR(x,y,w,h,8,C_BTN_DIS,RGB(80,85,80));
            dtC(x+w/2,y+h/2,label.c_str(),C_DIM,fs,false);
            return;
        }
        if(hov){
            fillRR(x-2,y-2,w+4,h+4,10,C_GOLD,C_GOLD,2);
        }
        COLORREF bg=hov?C_BTN_H:C_BTN_N;
        COLORREF border=hov?C_GOLD:RGB(55,138,75);
        fillRR(x,y,w,h,8,bg,border,2);
        dtC(x+w/2,y+h/2,label.c_str(),C_WHITE,fs,true);
    }
};

// ===== 标准消息弹窗（模态覆盖层）=====
void showMsgBox(const string& title, const string& body, int bw=520, int bh=220){
    int bx=(WIN_W-bw)/2, by=(WIN_H-bh)/2;
    // 半透明遮罩
    setlinecolor(RGB(0,0,0));
    setfillcolor(RGB(0,0,0));
    for(int yy=0;yy<WIN_H;yy+=3) line(0,yy,WIN_W,yy);
    fillRR(bx,by,bw,bh,12,C_PANEL_D,C_GOLD,2);
    dtC(bx+bw/2, by+40, title.c_str(), C_GOLD, 22, true);
    // 分割线
    setlinecolor(C_GOLD);
    line(bx+20,by+65,bx+bw-20,by+65);
    dtC(bx+bw/2, by+bh/2+10, body.c_str(), C_TEXT, 18, false);
    dtC(bx+bw/2, by+bh-36, "[ 点击任意处继续 ]", C_DIM, 15, false);
    FlushBatchDraw();
    // 等待点击
    ExMessage msg;
    while(true){
        if(peekmessage(&msg,EX_MOUSE) && msg.message==WM_LBUTTONUP) break;
        Sleep(16);
    }
}

// 是/否对话框，返回 true=是
bool showYesNo(const string& title, const string& body){
    int bw=540, bh=220, bx=(WIN_W-bw)/2, by=(WIN_H-bh)/2;
    setlinecolor(RGB(0,0,0)); setfillcolor(RGB(0,0,0));
    for(int yy=0;yy<WIN_H;yy+=3) line(0,yy,WIN_W,yy);
    fillRR(bx,by,bw,bh,12,C_PANEL_D,C_GOLD,2);
    dtC(bx+bw/2, by+40, title.c_str(), C_GOLD, 22, true);
    setlinecolor(C_GOLD); line(bx+20,by+65,bx+bw-20,by+65);
    dtC(bx+bw/2, by+bh/2-10, body.c_str(), C_TEXT, 18, false);
    Btn bYes(bx+60, by+bh-58, 160, 40, "是 (激活)", 18);
    Btn bNo (bx+bw-220, by+bh-58, 160, 40, "否 (放弃)", 18);
    int mx=0,my=0;
    while(true){
        BeginBatchDraw();
        // re-draw box bg (no full redraw needed, box is on top)
        fillRR(bx,by,bw,bh,12,C_PANEL_D,C_GOLD,2);
        dtC(bx+bw/2, by+40, title.c_str(), C_GOLD, 22, true);
        setlinecolor(C_GOLD); line(bx+20,by+65,bx+bw-20,by+65);
        dtC(bx+bw/2, by+bh/2-10, body.c_str(), C_TEXT, 18, false);
        bYes.draw(bYes.hit(mx,my)); bNo.draw(bNo.hit(mx,my));
        EndBatchDraw();
        ExMessage msg;
        while(peekmessage(&msg,EX_MOUSE)){
            mx=msg.x; my=msg.y;
            if(msg.message==WM_LBUTTONUP){
                if(bYes.hit(mx,my)) return true;
                if(bNo.hit(mx,my))  return false;
            }
        }
        Sleep(16);
    }
}

// 通用按钮等待（传入背景重绘函数）
int waitBtns(vector<Btn>& btns, function<void()> bg){
    int mx=0,my=0;
    while(true){
        BeginBatchDraw();
        bg();
        int hov=-1;
        for(int i=0;i<(int)btns.size();++i) if(btns[i].hit(mx,my)) hov=i;
        for(int i=0;i<(int)btns.size();++i) btns[i].draw(i==hov);
        EndBatchDraw();
        ExMessage msg;
        while(peekmessage(&msg,EX_MOUSE)){
            mx=msg.x; my=msg.y;
            if(msg.message==WM_LBUTTONUP)
                for(int i=0;i<(int)btns.size();++i)
                    if(btns[i].hit(mx,my)) return i;
        }
        Sleep(16);
    }
}
"""
with open(r'd:\Users\ymx36\Desktop\三雄争锋游戏\三雄争锋v3.cpp','w',encoding='gbk') as f:
    f.write(code)
print("GFX1 OK - 基础设施写入完成")
