/*
 * 三雄争锋 v3.0 (EasyX 图形界面版)
 * 编译: Dev-C++ 5.11, C++11
 * 依赖: 需先安装 EasyX 图形库 (https://easyx.cn)
 * 编译选项: -std=c++11
 * 字符编码: ANSI/GBK
 */
// 忋略 IntelliSense 宽字符警告，编译器实际使用 MBCS 模式
#ifndef _MBCS
#define _MBCS
#endif
#ifdef UNICODE
#undef UNICODE
#endif
#include <graphics.h>
#include <conio.h>
#include <iostream>
#include <vector>
#include <string>
#include <algorithm>
#include <random>
#include <chrono>
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
const COLORREF C_TABLE    = RGB(18, 26, 48);
const COLORREF C_TABLE_D  = RGB(11, 16, 32);
const COLORREF C_CARD_W   = RGB(255, 252, 244);
const COLORREF C_CARD_B   = RGB(20, 40, 110);
const COLORREF C_RED_S    = RGB(200, 28, 28);
const COLORREF C_BLK_S    = RGB(14, 14, 14);
const COLORREF C_GOLD     = RGB(255, 208, 0);
const COLORREF C_SILVER   = RGB(175, 188, 200);
const COLORREF C_PANEL    = RGB(24, 36, 68);
const COLORREF C_PANEL_D  = RGB(13, 20, 42);
const COLORREF C_SEL      = RGB(255, 232, 50);
const COLORREF C_BTN_N    = RGB(38, 90, 158);
const COLORREF C_BTN_H    = RGB(58, 138, 220);
const COLORREF C_BTN_DIS  = RGB(55, 65, 80);
const COLORREF C_WHITE    = RGB(255, 255, 255);
const COLORREF C_TEXT     = RGB(228, 228, 228);
const COLORREF C_DIM      = RGB(100, 118, 145);
const COLORREF C_WARN     = RGB(255, 168, 32);
const COLORREF C_RED_T    = RGB(218, 80, 80);
const COLORREF C_BLUE_T   = RGB(90, 168, 248);
const COLORREF C_GREEN_T  = RGB(88, 218, 128);
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
    // 深蓝主色 + 内层边框 + 精致花纹
    fillRR(x,y,w,h,8,RGB(15,32,90),RGB(80,110,180),2);
    // 内层白色细边框
    setlinecolor(RGB(200,210,240));
    setlinestyle(PS_SOLID,1);
    roundrect(x+5,y+5,x+w-5,y+h-5,5,5);
    // 中央菱形十字纹
    int cx=x+w/2, cy=y+h/2;
    int rx=w/2-10, ry=h/2-10;
    setlinecolor(RGB(90,130,210));
    // 菱形
    line(cx,y+8, x+w-8,cy);
    line(x+w-8,cy, cx,y+h-8);
    line(cx,y+h-8, x+8,cy);
    line(x+8,cy, cx,y+8);
    // 中央小装饰点
    setfillcolor(C_GOLD); setlinecolor(C_GOLD);
    fillcircle(cx,cy,4);
    // 四角小圆点
    setfillcolor(RGB(90,130,210)); setlinecolor(RGB(90,130,210));
    fillcircle(x+11,y+11,3);
    fillcircle(x+w-11,y+11,3);
    fillcircle(x+11,y+h-11,3);
    fillcircle(x+w-11,y+h-11,3);
}

// ===== Card前置（供绘制函数用）=====
struct Card;
void drawCard(int x,int y,int w,int h,const Card& c,bool faceUp,bool selected=false);


// ===== Card 类 =====
struct Card {
    Suit suit;
    Rank rank;
    bool isJoker;
    bool isReturned; // 被5号牌收回，下回合打出不触发连顺

    Card():suit(SPADE),rank(RANK_A),isJoker(false),isReturned(false){}
    Card(Suit s,Rank r,bool joker=false)
        :suit(s),rank(r),isJoker(joker),isReturned(false){}

    int getCompareValue(GameRule rule) const {
        if(isJoker){
            // 大王永远最强；小王比大比小均为次优
            if(rank==RANK_BIG_JOKER)  return (rule==BIG_WINS)? 2000:-2000;
            // 小王：比大次于大王(1900)；比小同样是最优(-1900)
            return (rule==BIG_WINS)? 1900:-1900;
        }
        int v=static_cast<int>(rank);
        if(rule==BIG_WINS){
            if(rank==RANK_A) return 1; // A最小
            return v;
        } else {
            // SMALL_WINS: A最优(1)，K最差(13)，其余按面値
            return v;
        }
    }
    // 用于正面绘制
    void draw(int x,int y,bool selected=false) const {
        drawCardFace(x,y,CARD_W,CARD_H,suit,rank,isJoker,selected,isReturned);
    }
    void drawBack(int x,int y) const {
        drawCardBack(x,y,CARD_W,CARD_H);
    }
};

// Card::draw 实现补丁（因为Card定义在drawCardFace之后，直接调用即可）
void drawCard(int x,int y,int w,int h,const Card& c,bool faceUp,bool selected){
    if(faceUp) drawCardFace(x,y,w,h,c.suit,c.rank,c.isJoker,selected,c.isReturned);
    else       drawCardBack(x,y,w,h);
}

// ===== Player 类 =====
class Player {
public:
    string name;
    vector<Card> hand;
    int score;
    bool isHuman;
    bool isStrategic;
    int bigJokerUses;
    int smallJokerUses;

    Player():score(0),isHuman(false),isStrategic(true),bigJokerUses(0),smallJokerUses(0){}

    void addCard(const Card& c){ hand.push_back(c); }
    void removeCard(int idx){
        if(idx>=0&&idx<(int)hand.size()) hand.erase(hand.begin()+idx);
    }
    void removeSpecificCard(const Card& c){
        for(int i=0;i<(int)hand.size();++i)
            if(hand[i].suit==c.suit&&hand[i].rank==c.rank&&hand[i].isJoker==c.isJoker){
                hand.erase(hand.begin()+i); return;
            }
    }
    void resetJokerUses(){ bigJokerUses=0; smallJokerUses=0; }
    bool canUseBigJoker()   const { return hasBigJoker()   && bigJokerUses<2; }
    bool canUseSmallJoker() const { return hasSmallJoker() && smallJokerUses<1; }
    bool hasBigJoker() const {
        for(auto& c:hand) if(c.isJoker&&c.rank==RANK_BIG_JOKER) return true;
        return false;
    }
    bool hasSmallJoker() const {
        for(auto& c:hand) if(c.isJoker&&c.rank==RANK_SMALL_JOKER) return true;
        return false;
    }
    bool hasSpadeA() const {
        for(auto& c:hand) if(c.suit==SPADE&&c.rank==RANK_A&&!c.isJoker) return true;
        return false;
    }
    // 找到手中一张5（排除 excludeIdx），返回索引或-1
    int findFiveCard(int excludeIdx=-1) const {
        for(int i=0;i<(int)hand.size();++i){
            if(i==excludeIdx) continue;
            if(!hand[i].isJoker && hand[i].rank==RANK_5) return i;
        }
        return -1;
    }
};

// ===== GameEngine 类声明 =====
class GameEngine {
public:
    Player players[3];
    vector<Card> deck;
    int round;
    GameRule currentRule;
    int gameMode;       // 0=单局 1=达标分
    int targetScore;
    bool consecutiveGame;
    int sceneCount;
    bool lastRoundTwoWayTie;
    bool skipModeSelect;
    bool quitToMenu;

    // 5号牌待归还
    bool fiveReturnPending[3];
    Card fiveReturnCard[3];

    // 本轮桌面牌（供渲染使用）
    vector<Card> tableCards;
    vector<int>  playedIdx;
    bool         tableRevealed;

    // 消息日志（显示在桌面区）
    vector<string> msgLog;

    mt19937 rng;

    GameEngine();

    // ===== 游戏逻辑 =====
    void initDeck();
    void shuffleDeck();
    void dealCards(int n=18);
    vector<int> computeScores(const vector<Card>& cards);
    bool isThreeConsecutive(const vector<Card>& cards, const vector<bool>& skip);
    void applyBonusScore(const vector<Card>& cards);
    void handleRuleFlip(const vector<Card>& cards);

    // AI
    int aiBlindChoice(int maxIdx);
    int strategicChoice(int pidx);
    int randomChoice(int pidx);          // 随机AI：仅随机选牌，特殊处理与策略AI相同
    GameRule aiSmartRuleChoice(int pidx); // AI智能选择比大/比小
    void strategicDiscard(Player& p, int count);

    // 特殊机制
    void processFiveReturns();
    bool check5CardActivation(int pIdx, int playedIdx, const vector<Card>& table);
    void perform5CardActivations(const vector<Card>& table,
        const vector<int>& pIdx, vector<bool>& activated);
    void perform10Mechanism(int tenPlayer);
    void performDrawSequence();
    int  performBigJokerDefense(int targetPlayer, int chosen);
    void performSmallJokerPeek(int fromPlayer, int targetPlayer);

    // 游戏流程
    void playRound();
    void playTiebreaker(vector<int>& tied, vector<int>& tbScoresOut);
    bool checkEndCondition(vector<int>& tied);
    void startNewGame();

    // ===== GUI渲染 =====
    void renderGameScreen();
    void renderInfoBar();
    void renderAIArea(int pidx, int x, int y, int w, int h);
    void renderTableArea();
    void renderHumanHand(int selIdx=-1);
    void renderActionBtns(vector<Btn>& btns);
    void addMsg(const string& s);

    // ===== GUI交互 =====
    int  guiSelectCard(int playerIdx, const string& prompt, bool canCancel=true);
    int  guiBlindSelect(int playerIdx, const string& prompt, int maxN);
    void guiInfo(const string& title, const string& body);
    bool guiYesNo(const string& title, const string& body);
    vector<int> guiSelectTwo(int playerIdx, const string& prompt);

    // ===== 菜单 =====
    void showMainMenu();
    void showRulesScreen();
    int  showModeSelect();
    int  showFinalRank(vector<int> tbScores={});
};

// 全局游戏引擎指针（供各屏幕函数访问）
GameEngine* g_eng = nullptr;


// ===== 构造 + 初始化 =====
GameEngine::GameEngine()
    :round(1),currentRule(BIG_WINS),gameMode(0),targetScore(60),
     consecutiveGame(false),sceneCount(1),lastRoundTwoWayTie(false),
     tableRevealed(false)
{
    unsigned seed=(unsigned)chrono::steady_clock::now().time_since_epoch().count();
    rng.seed(seed);
    for(int i=0;i<3;++i){ fiveReturnPending[i]=false; }
    skipModeSelect=false;
    // 玩家0是人类
    players[0].name="你";       players[0].isHuman=true;  players[0].isStrategic=false;
    players[1].name="玩家2(AI)"; players[1].isHuman=false; players[1].isStrategic=true;
    players[2].name="玩家3(AI)"; players[2].isHuman=false; players[2].isStrategic=true;
}

void GameEngine::initDeck(){
    deck.clear();
    for(int s=0;s<4;++s)
        for(int r=1;r<=13;++r)
            deck.push_back(Card((Suit)s,(Rank)r));
    deck.push_back(Card(JOKER_SUIT,RANK_SMALL_JOKER,true));
    deck.push_back(Card(JOKER_SUIT,RANK_BIG_JOKER,true));
}
void GameEngine::shuffleDeck(){
    shuffle(deck.begin(),deck.end(),rng);
}
void GameEngine::dealCards(int n){
    for(int i=0;i<3;++i) players[i].hand.clear();
    int idx=0;
    for(int r=0;r<n;++r)
        for(int i=0;i<3;++i)
            if(idx<(int)deck.size()) players[i].addCard(deck[idx++]);
}

void GameEngine::addMsg(const string& s){
    msgLog.push_back(s);
    if((int)msgLog.size()>6) msgLog.erase(msgLog.begin());
}

// ===== 计分 =====
vector<int> GameEngine::computeScores(const vector<Card>& cards){
    vector<int> scores(3,0);
    int v[3]; for(int i=0;i<3;++i) v[i]=cards[i].getCompareValue(currentRule);
    int ord[3]={0,1,2};
    sort(ord,ord+3,[&](int a,int b){
        return currentRule==BIG_WINS ? v[a]>v[b] : v[a]<v[b];
    });
    if(v[0]==v[1]&&v[1]==v[2]) return scores; // 三张全同
    if(v[ord[0]]==v[ord[1]]){
        scores[ord[0]]=1; scores[ord[1]]=1;
    } else if(v[ord[1]]==v[ord[2]]){
        scores[ord[0]]=2;
    } else {
        scores[ord[0]]=2; scores[ord[1]]=1;
    }
    return scores;
}

// ===== 连顺判断 =====
bool GameEngine::isThreeConsecutive(const vector<Card>& cards, const vector<bool>& skip){
    for(int i=0;i<3;++i) if(cards[i].isJoker) return false;
    for(int i=0;i<3;++i) if(skip[i]) return false;
    vector<int> nums;
    for(int i=0;i<3;++i) nums.push_back(static_cast<int>(cards[i].rank));
    sort(nums.begin(),nums.end());
    return (nums[1]==nums[0]+1 && nums[2]==nums[1]+1);
}

// ===== 补分：两人或三人相同时，补给唯一最低分玩家 =====
void GameEngine::applyBonusScore(const vector<Card>& cards){
    int v[3]; for(int i=0;i<3;++i) v[i]=cards[i].getCompareValue(currentRule);
    bool hasTie=(v[0]==v[1]||v[1]==v[2]||v[0]==v[2]);
    if(!hasTie) return;
    bool allSame=(v[0]==v[1]&&v[1]==v[2]); // 三张全同补+2，两张同补+1
    int bonus=allSame?2:1;
    // 找唯一最低分玩家
    int minScore=players[0].score;
    for(int i=1;i<3;++i) if(players[i].score<minScore) minScore=players[i].score;
    vector<int> lowList;
    for(int i=0;i<3;++i) if(players[i].score==minScore) lowList.push_back(i);
    if((int)lowList.size()!=1) return; // 最低分不唯一，不补
    int lucky=lowList[0];
    players[lucky].score+=bonus;
    addMsg("[补分] "+players[lucky].name+" 补分+"+to_string(bonus)+"（唯一最低分）");
    BeginBatchDraw();
    renderGameScreen();
    char buf[64]; sprintf(buf,"[补分] %s 唯一最低分 +%d！",players[lucky].name.c_str(),bonus);
    dtC(WIN_W/2,WIN_H/2-60,buf,C_GOLD,24,true);
    EndBatchDraw();
    Sleep(1200);
}

// ===== 规则翻转 =====
void GameEngine::handleRuleFlip(const vector<Card>& cards){
    int v[3]; for(int i=0;i<3;++i) v[i]=cards[i].getCompareValue(currentRule);
    // 三张全同 → 永久反转规则
    if(v[0]==v[1]&&v[1]==v[2]){
        lastRoundTwoWayTie=false;
        currentRule=(currentRule==BIG_WINS)?SMALL_WINS:BIG_WINS;
        addMsg("[三同反转] 三张相同！规则永久反转为"+string(currentRule==BIG_WINS?"比大！":"比小！"));
        BeginBatchDraw(); renderGameScreen();
        dtC(WIN_W/2,WIN_H/2-60,
            (currentRule==BIG_WINS?"[三同反转！] 规则变为比大！":"[三同反转！] 规则变为比小！"),
            RGB(255,80,80),26,true);
        EndBatchDraw(); Sleep(1800);
        return;
    }
    // 两张相同（且非全同）：记录/翻转
    int cnt=0;
    if(v[0]==v[1]||v[1]==v[2]||v[0]==v[2]) cnt=2;
    if(cnt==2){
        if(lastRoundTwoWayTie){
            // 连续两次两张同 → 必然翻转规则
            currentRule=(currentRule==BIG_WINS)?SMALL_WINS:BIG_WINS;
            addMsg("[规则反转] 连续两次两张同！规则反转为"+
                string(currentRule==BIG_WINS?"比大！":"比小！"));
            BeginBatchDraw();
            renderGameScreen();
            dtC(WIN_W/2,WIN_H/2-60,
                (currentRule==BIG_WINS?"[规则反转！] 现在比大！":"[规则反转！] 现在比小！"),
                C_WARN,26,true);
            EndBatchDraw();
            Sleep(1500);
            lastRoundTwoWayTie=false;
        } else {
            lastRoundTwoWayTie=true;
        }
    } else {
        lastRoundTwoWayTie=false;
    }
}

// ===== AI =====
int GameEngine::aiBlindChoice(int maxIdx){
    if(maxIdx<=0) return 0;
    return rng()%maxIdx;
}

// ===== AI 策略核心 =====
// 返回当前玩家在三人中的名次（0=领先,1=中,2=垫底）
static int aiRank(const Player players[], int pidx){
    int s=players[pidx].score;
    int rank=0;
    for(int i=0;i<3;++i) if(i!=pidx && players[i].score>s) rank++;
    return rank;
}
int GameEngine::strategicChoice(int pidx){
    const Player& p=players[pidx];
    if(p.hand.empty()) return 0;
    int n=(int)p.hand.size();

    // 按比较值排序（值越小越优时小的排前面，BIG_WINS时大的排前面）
    // iv[0]=最弱, iv[n-1]=最强（比大时最大, 比小时最小）
    vector<pair<int,int>> iv;
    for(int i=0;i<n;++i)
        iv.push_back({p.hand[i].getCompareValue(currentRule),i});
    if(currentRule==BIG_WINS)
        sort(iv.begin(),iv.end());          // 升序：iv[n-1]最强
    else
        sort(iv.begin(),iv.end());          // 升序：iv[0]最强（值越小=A越优）

    // 求各分位索引
    auto atPct=[&](float pct)->int{
        int pos=(int)(pct*(n-1)+0.5f);
        return iv[max(0,min(n-1,pos))].second;
    };

    // 当前局面判断
    int myRank=aiRank(players,pidx);
    bool lateGame=(round>=13);
    bool veryLate=(round>=16);

    // 分差判断
    int myScore=p.score;
    int maxOpp=0; for(int i=0;i<3;++i) if(&players[i]!=&p && players[i].score>maxOpp) maxOpp=players[i].score;
    int gap=maxOpp-myScore;

    // ---- 大王策略：仅垫底且差距>=3分时出，或最后2局领先不超1分时出 ----
    for(int i=0;i<n;++i){
        if(p.hand[i].isJoker && p.hand[i].rank==RANK_BIG_JOKER){
            bool desperate=(myRank==2 && gap>=3);
            bool secureWin=(veryLate && gap<=-2); // 大幅领先也可出炸确保
            if(desperate||secureWin) return i;
        }
    }
    // ---- 小王策略（比小时有价值）：垫底且比小规则时，50%概率出小王 ----
    if(currentRule==SMALL_WINS){
        for(int i=0;i<n;++i){
            if(p.hand[i].isJoker && p.hand[i].rank==RANK_SMALL_JOKER){
                // 比小时小王是最差牌(14)，不适合出来争分，跳过
                break;
            }
        }
    }
    // ---- 出10策略：中盘(round 4-14)且有10时，评估是否用来偷牌 ----
    // 只在领先对手平均分>=2时不出10，其余情况按概率出10
    for(int i=0;i<n;++i){
        if(!p.hand[i].isJoker && p.hand[i].rank==RANK_10){
            if(round>=4 && round<=15){
                // 若处于垫底，高概率出10偷最高分对手的牌
                int prob=(myRank==2)?65:(myRank==1)?40:20;
                if((int)(rng()%100)<prob) return i;
            }
        }
    }
    // ---- 5号牌策略：若出5时自己不是最优则可以收回，仅在手小时考虑 ----
    // （5号牌逻辑主要由特效触发，这里不主动挑选）

    // ---- 主出牌策略：基于局面 ----
    // 加入5%随机防止完全可预测
    if((int)(rng()%100)<5) return iv[(int)(rng()%n)].second;

    if(currentRule==BIG_WINS){
        // 比大：值越大越强
        if(myRank==2){
            // 垫底：优先出强牌（前20%）追分
            if(lateGame) return atPct(0.85f);
            return atPct(0.75f+(int)(rng()%15)*0.01f);
        } else if(myRank==1){
            // 中位：出中上（40%-70%）
            return atPct(0.45f+(int)(rng()%30)*0.01f);
        } else {
            // 领先：出中档消耗（25%-55%），保留强牌
            if(veryLate) return atPct(0.6f); // 最后几局也要维持
            return atPct(0.25f+(int)(rng()%30)*0.01f);
        }
    } else {
        // 比小：值越小越强（A=1最优, K=13最差）
        // iv[0]最强（最小值）, iv[n-1]最弱（最大值）
        if(myRank==2){
            // 垫底：出最强牌（前15-25%）
            return atPct(lateGame?0.1f:0.15f+(int)(rng()%10)*0.01f);
        } else if(myRank==1){
            // 中位：出中上（20%-45%）
            return atPct(0.2f+(int)(rng()%25)*0.01f);
        } else {
            // 领先：中档牌（35%-60%），避免浪费优质小牌
            if(veryLate) return atPct(0.25f);
            return atPct(0.35f+(int)(rng()%25)*0.01f);
        }
    }
}

// 随机AI：一般回合完全随机出牌（特殊处理与策略AI相同）
int GameEngine::randomChoice(int pidx){
    int n=(int)players[pidx].hand.size();
    if(n==0) return 0;
    return (int)(rng()%n);
}

// AI智能选择比大/比小：统计非Joker手牌的平均点数，高于中位则比大，否则比小
GameRule GameEngine::aiSmartRuleChoice(int pidx){
    const Player& p=players[pidx];
    int total=0, cnt=0;
    for(const Card& c:p.hand){
        if(!c.isJoker){ total+=c.rank; cnt++; }
    }
    if(cnt==0) return (GameRule)(rng()%2);
    float avg=(float)total/cnt;
    // 平均rank>7（偏大牌）→比大更有利；否则比小
    return (avg>7.0f)?BIG_WINS:SMALL_WINS;
}

void GameEngine::strategicDiscard(Player& p, int count){
    for(int k=0;k<count&&!p.hand.empty();++k){
        int n=(int)p.hand.size();
        // 找最弱牌的下标（比大时最小, 比小时最大非Joker优先丢弃）
        int wi=-1; int wv=0;
        // 先找非Joker、非10的最弱牌
        for(int i=0;i<n;++i){
            if(p.hand[i].isJoker) continue;
            if(p.hand[i].rank==RANK_10 && n>4) continue; // 手多时保留10
            int v=p.hand[i].getCompareValue(currentRule);
            bool weaker=(wi<0)||(currentRule==BIG_WINS?v<wv:v>wv);
            if(weaker){ wv=v; wi=i; }
        }
        // 若没找到（全是Joker或10），退而求其次找最弱的（可以是10但不能是Joker）
        if(wi<0){
            for(int i=0;i<n;++i){
                if(p.hand[i].isJoker) continue;
                int v=p.hand[i].getCompareValue(currentRule);
                bool weaker=(wi<0)||(currentRule==BIG_WINS?v<wv:v>wv);
                if(weaker){ wv=v; wi=i; }
            }
        }
        // 最后兜底
        if(wi<0) wi=0;
        p.hand.erase(p.hand.begin()+wi);
    }
}


// ===== 渲染：顶部信息栏 =====
void GameEngine::renderInfoBar(){
    fillArea(0,0,WIN_W,BAR_H,RGB(8,14,32),C_GOLD,0);
    // 顶部金色底线
    setlinecolor(C_GOLD); setlinestyle(PS_SOLID,2);
    line(0,BAR_H-2,WIN_W,BAR_H-2);
    // 第N局
    char buf[64];
    sprintf(buf,"第 %d / 18 局",round);
    dtL(14,14,buf,C_GOLD,22,true);
    // 规则
    const char* ruleStr=(currentRule==BIG_WINS)?"比大 (K最强)":"比小 (A最优)";
    COLORREF rc=(currentRule==BIG_WINS)?C_RED_T:C_GREEN_T;
    dtC(WIN_W/2,BAR_H/2,ruleStr,rc,20,true);
    // 积分（右侧三人）
    int sx=WIN_W-420;
    for(int i=0;i<3;++i){
        char sb[32]; sprintf(sb,"%s:%d",players[i].name.c_str(),players[i].score);
        COLORREF sc=(i==0)?C_BLUE_T:(i==1)?C_WARN:C_SILVER;
        dtL(sx+i*140,14,sb,sc,18,i==0);
    }
    // 分割线（由renderGameScreen中顶部bar绘制金线，这里不重复）
    setlinecolor(C_GOLD); setlinestyle(PS_SOLID,1);
    line(0,BAR_H-1,WIN_W,BAR_H-1);
}

// ===== 渲染：AI手牌区 =====
void GameEngine::renderAIArea(int pidx,int x,int y,int w,int h){
    fillArea(x,y,w,h,RGB(18,28,55),RGB(50,75,130));
    // 玩家名
    COLORREF nc=(pidx==1)?C_WARN:C_SILVER;
    dtL(x+10,y+6,players[pidx].name.c_str(),nc,16,true);
    char sb[16]; sprintf(sb,"(%d张)",(int)players[pidx].hand.size());
    dtL(x+10+textwidth(players[pidx].name.c_str())+4,y+8,sb,C_DIM,14,false);
    // 牌背（紧凑排列，最多显示18张）
    int n=(int)players[pidx].hand.size();
    if(n==0){ dtC(x+w/2,y+h/2,"（已无手牌）",C_DIM,15,false); return; }
    int cw=min(CARD_W,max(22,(w-20)/max(1,n)));
    int ch=min(CARD_H,h-30);
    int totalW=cw*(n-1)+CARD_W;
    if(totalW>w-20) totalW=w-20;
    int startX=x+(w-min(totalW,n*cw))/2;
    int cardY=y+(h-ch)/2+10;
    for(int i=0;i<n;++i){
        int cx2=startX+i*min(cw,max(20,(w-20-CARD_W)/max(1,n-1)));
        drawCardBack(cx2,cardY,CARD_W,ch);
    }
}

// ===== 渲染：桌面牌区 =====
void GameEngine::renderTableArea(){
    fillArea(TBL_X,TBL_Y,TBL_W,TBL_H,RGB(20,32,58),RGB(60,90,140),4);
    // 中心桑圆装饰
    setlinecolor(RGB(50,75,120));
    setlinestyle(PS_SOLID,1);
    int cx=TBL_X+TBL_W/2-200, cy=TBL_Y+TBL_H/2;
    int rx=280, ry=110;
    ellipse(cx-rx,cy-ry,cx+rx,cy+ry);
    // 中间区域显示本轮打出的牌
    if(tableRevealed && (int)tableCards.size()==3){
        int spacing=CARD_W+24;
        int totalW=3*spacing-24;
        int startX=TBL_X+(TBL_W-totalW)/2;
        int cardY=TBL_Y+(TBL_H-CARD_H)/2-10;
        for(int i=0;i<3;++i){
            if(playedIdx[i]<0) continue; // 未参与本局（加赛中未参赛方）不渲染
            drawCard(startX+i*spacing,cardY,CARD_W,CARD_H,tableCards[i],true,false);
            // 玩家名标签
            dtC(startX+i*spacing+CARD_W/2, cardY+CARD_H+14,
                players[i].name.c_str(),
                (i==0)?C_BLUE_T:(i==1)?C_WARN:C_SILVER, 14, true);
        }
    } else {
        dtC(TBL_X+TBL_W/2, TBL_Y+TBL_H/2-16, "[ 等待出牌... ]", C_DIM, 18, false);
    }
    // 消息日志（右侧）
    int logX=TBL_X+TBL_W-380, logY=TBL_Y+10;
    fillArea(logX,logY,370,TBL_H-20,RGB(13,20,44),RGB(40,60,100),4);
    dtL(logX+8,logY+6,"  游戏日志",C_GOLD,14,true);
    setlinecolor(RGB(40,65,100)); line(logX+6,logY+26,logX+364,logY+26);
    int ly=logY+32;
    for(int i=0;i<(int)msgLog.size();++i){
        // 截断超长消息
        string m=msgLog[i];
        if((int)m.size()>22) m=m.substr(0,22)+"...";
        COLORREF mc=(i==(int)msgLog.size()-1)?C_WHITE:C_DIM;
        dtL(logX+8,ly+i*24,m.c_str(),mc,13,i==(int)msgLog.size()-1);
    }
}

// ===== 渲染：人类手牌 =====
void GameEngine::renderHumanHand(int selIdx){
    fillArea(HND_X,HND_Y,HND_W,HND_H,RGB(16,28,56),RGB(55,85,140),6);
    dtL(HND_X+10,HND_Y+6,"你的手牌",C_BLUE_T,15,true);
    int n=(int)players[0].hand.size();
    if(n==0){ dtC(HND_X+HND_W/2,HND_Y+HND_H/2,"（手牌已空）",C_DIM,16,false); return; }
    // 自适应卡宽
    int maxCards=min(n,13);
    int overlap=max(CARD_W+6, (HND_W-20) / max(1,maxCards));
    overlap=min(overlap, CARD_W+10);
    int totalW=(n-1)*overlap+CARD_W;
    int startX=HND_X+(HND_W-min(totalW,HND_W-20))/2;
    int cardY=HND_Y+26;
    // 被选中的牌上移
    for(int i=0;i<n;++i){
        bool sel=(i==selIdx);
        int cx2=startX+i*min(overlap,(HND_W-20-CARD_W)/max(1,n-1));
        int cy2=cardY+(sel?-12:0);
        drawCard(cx2,cy2,CARD_W,CARD_H-10,players[0].hand[i],true,sel);
    }
}

// ===== 渲染：操作按钮区 =====
void GameEngine::renderActionBtns(vector<Btn>& btns){
    fillArea(ACT_X,ACT_Y,ACT_W,ACT_H,C_PANEL_D,RGB(25,40,80),6);
    // 按钮由调用者负责绘制
}

// ===== 全屏渲染 =====
void GameEngine::renderGameScreen(){
    // 深色背景：底色
    setfillcolor(C_TABLE); setlinecolor(C_TABLE);
    fillrectangle(0,0,WIN_W,WIN_H);
    // 微妙斤布纹理：断点花格
    setlinecolor(RGB(28,40,68));
    setlinestyle(PS_SOLID,1);
    for(int xx=0;xx<WIN_W;xx+=28) line(xx,0,xx,WIN_H);
    for(int yy=0;yy<WIN_H;yy+=28) line(0,yy,WIN_W,yy);
    // 对角暗晕角（四角深色渐变）
    for(int i=0;i<80;i+=4){
        int a=180-i*2;
        if(a<0) a=0;
        setlinecolor(RGB(8,12,26));
        setlinestyle(PS_SOLID,1);
        // left top
        line(0,i,i,0);
        // right bottom
        line(WIN_W-i,WIN_H,WIN_W,WIN_H-i);
    }
    renderInfoBar();
    renderAIArea(1,AI1_X,AI1_Y,AI1_W,AI1_H);
    renderAIArea(2,AI2_X,AI2_Y,AI2_W,AI2_H);
    renderTableArea();
    renderHumanHand();
}


// ===== GUI: 选择手中一张牌 =====
// canCancel=false 时强制必须选，不显示取消按钮
int GameEngine::guiSelectCard(int pidx, const string& prompt, bool canCancel){
    int sel=-1;
    int mx=0,my=0;
    Player& p=players[pidx];
    int n=(int)p.hand.size();
    if(n==0) return -1;
    int overlap=min(CARD_W+10, (HND_W-20)/max(1,n));
    int totalW=(n-1)*overlap+CARD_W;
    int startX=HND_X+(HND_W-min(totalW,HND_W-20))/2;
    int cardY=HND_Y+26;

    Btn bConfirm(ACT_X+8,ACT_Y+10,ACT_W-16,44,"确认",18,false);
    Btn bCancel (ACT_X+8,ACT_Y+60,ACT_W-16,44,"取消",18);
    vector<Btn> btns={bConfirm};
    if(canCancel) btns.push_back(bCancel);

    while(true){
        BeginBatchDraw();
        renderGameScreen();
        // 覆盖手牌区（含选中效果）
        fillArea(HND_X,HND_Y,HND_W,HND_H,C_PANEL,RGB(50,90,55),6);
        dtL(HND_X+10,HND_Y+6,"你的手牌",C_BLUE_T,15,true);
        for(int i=0;i<n;++i){
            bool s=(i==sel);
            int cx2=startX+i*min(overlap,(HND_W-20-CARD_W)/max(1,n-1));
            int cy2=cardY+(s?-12:0);
            drawCard(cx2,cy2,CARD_W,CARD_H-10,p.hand[i],true,s);
        }
        // 提示文字
        COLORREF pc=canCancel?C_GOLD:C_WARN; // 强制操作用警告色提示
        dtC(HND_X+HND_W/2,HND_Y+HND_H-18,prompt.c_str(),pc,15,true);
        if(!canCancel) dtC(HND_X+HND_W/2,HND_Y+HND_H-36,"（必须选择，不可跳过）",C_RED_T,13,false);
        // 操作按钮
        fillArea(ACT_X,ACT_Y,ACT_W,ACT_H,C_PANEL_D,RGB(25,40,80),6);
        btns[0].enabled=(sel>=0);
        for(auto& b:btns) b.draw(b.hit(mx,my));
        EndBatchDraw();

        ExMessage msg;
        while(peekmessage(&msg,EX_MOUSE)){
            mx=msg.x; my=msg.y;
            if(msg.message==WM_LBUTTONUP){
                // 检查牌点击
                for(int i=0;i<n;++i){
                    int cx2=startX+i*min(overlap,(HND_W-20-CARD_W)/max(1,n-1));
                    int cy2=cardY;
                    if(mx>=cx2&&mx<=cx2+CARD_W&&my>=cy2-14&&my<=cy2+CARD_H)
                        sel=(sel==i)?-1:i;
                }
                if(btns[0].hit(mx,my) && sel>=0) return sel;
                if(canCancel && btns.size()>1 && btns[1].hit(mx,my)) return -1;
            }
        }
        Sleep(16);
    }
}

// ===== GUI: 盲选1~N中一个编号 =====
int GameEngine::guiBlindSelect(int pidx, const string& prompt, int maxN){
    // 显示 maxN 张牌背，让玩家点击其中一张
    int sel=-1;
    int mx=0,my=0;
    int spacing=min(CARD_W+16,(TBL_W-100)/max(1,maxN));
    int totalW=(maxN-1)*spacing+CARD_W;
    int startX=TBL_X+(TBL_W-min(totalW,TBL_W-100))/2;
    int cardY=TBL_Y+(TBL_H-CARD_H)/2;

    Btn bConfirm(ACT_X+8,ACT_Y+10,ACT_W-16,44,"确认",18,false);
    vector<Btn> btns={bConfirm};

    while(true){
        BeginBatchDraw();
        renderGameScreen();
        // 覆盖桌面区显示牌背
        fillArea(TBL_X,TBL_Y,TBL_W,TBL_H,C_TABLE_D,RGB(30,50,90),4);
        dtC(TBL_X+TBL_W/2-200,TBL_Y+18,prompt.c_str(),C_GOLD,16,true);
        for(int i=0;i<maxN;++i){
            int cx2=startX+i*min(spacing,(TBL_W-100-CARD_W)/max(1,maxN-1));
            bool s=(i==sel);
            if(s){ fillRR(cx2-4,cardY-4,CARD_W+8,CARD_H+8,12,C_SEL,C_SEL,3); }
            drawCardBack(cx2,cardY,CARD_W,CARD_H);
            char num[4]; sprintf(num,"%d",i+1);
            dtC(cx2+CARD_W/2,cardY+CARD_H+14,num,s?C_GOLD:C_DIM,14,s);
        }
        fillArea(ACT_X,ACT_Y,ACT_W,ACT_H,C_PANEL_D,RGB(25,40,80),6);
        btns[0].enabled=(sel>=0);
        for(auto& b:btns) b.draw(b.hit(mx,my));
        EndBatchDraw();

        ExMessage msg;
        while(peekmessage(&msg,EX_MOUSE)){
            mx=msg.x; my=msg.y;
            if(msg.message==WM_LBUTTONUP){
                for(int i=0;i<maxN;++i){
                    int cx2=startX+i*min(spacing,(TBL_W-100-CARD_W)/max(1,maxN-1));
                    if(mx>=cx2&&mx<=cx2+CARD_W&&my>=cardY&&my<=cardY+CARD_H)
                        sel=(sel==i)?-1:i;
                }
                if(btns[0].hit(mx,my)&&sel>=0) return sel;
            }
        }
        Sleep(16);
    }
}

// guiInfo / guiYesNo 包装
void GameEngine::guiInfo(const string& title, const string& body){
    BeginBatchDraw();
    renderGameScreen();
    showMsgBox(title,body);
    EndBatchDraw();
}
bool GameEngine::guiYesNo(const string& title, const string& body){
    BeginBatchDraw();
    renderGameScreen();
    bool r=showYesNo(title,body);
    EndBatchDraw();
    return r;
}

// ===== 特殊机制：5号牌归还 =====
void GameEngine::processFiveReturns(){
    for(int i=0;i<3;++i){
        if(fiveReturnPending[i]){
            Card rc=fiveReturnCard[i]; rc.isReturned=true;
            players[i].addCard(rc);
            fiveReturnPending[i]=false;
            addMsg("[5号牌] "+players[i].name+" 收回了上回合的牌(*)");
        }
    }
}

// ===== 检查5号牌激活条件 =====
bool GameEngine::check5CardActivation(int pIdx,int pIdx2,const vector<Card>& table){
    int v[3]; for(int i=0;i<3;++i) v[i]=table[i].getCompareValue(currentRule);
    if(v[0]==v[1]||v[1]==v[2]||v[0]==v[2]) return false;
    int myV=v[pIdx];
    int best=(currentRule==BIG_WINS)?*max_element(v,v+3):*min_element(v,v+3);
    if(myV==best) return false;
    if(players[pIdx].findFiveCard(pIdx2)<0) return false;
    return true;
}

// ===== 5号牌激活（含GUI）=====
void GameEngine::perform5CardActivations(const vector<Card>& table,
    const vector<int>& pIdx, vector<bool>& activated){
    activated.assign(3,false);
    for(int i=0;i<3;++i){
        // 打出的牌已在Step5移出手牌，传-1表示不排除任何索引
        if(!check5CardActivation(i,-1,table)) continue;
        bool doIt=false;
        if(players[i].isHuman){
            char body[128];
            sprintf(body,"你打出的牌不是最优，且手中还有5可用。\n消耗一张5，将本轮出的牌收回？");
            doIt=guiYesNo("[5号牌] 激活？",body);
        } else {
            // AI：打出的牌有一定价值才激活
            int myV=table[i].getCompareValue(currentRule);
            int vals[3]; for(int j=0;j<3;++j) vals[j]=table[j].getCompareValue(currentRule);
            sort(vals,vals+3);
            doIt=(currentRule==BIG_WINS)?(myV>=vals[1]):(myV<=vals[1]);
        }
        if(doIt){
            // 注意：打出的牌在Step5已从手牌删除，直接找任意剩余的5（不需要排除索引）
            int fi=players[i].findFiveCard();
            if(fi<0) continue; // 理论上不会，findFiveCard()保证之前check通过
            players[i].removeCard(fi);
            fiveReturnPending[i]=true;
            fiveReturnCard[i]=table[i];
            activated[i]=true;
            addMsg("[5号牌] "+players[i].name+" 激活！下局收回出的牌");
            // 弹框通知（AI激活时让人类知情）
            BeginBatchDraw(); renderGameScreen();
            char finfo[96]; sprintf(finfo,"%s 使用了5号牌技能，将本轮出的牌收回！",players[i].name.c_str());
            showMsgBox("[5号牌] 狸猫换太子！",finfo);
            EndBatchDraw();
        }
    }
}

// ===== 出10机制（含GUI）=====
void GameEngine::perform10Mechanism(int tenPlayer){
    addMsg("[顺手牵羊] "+players[tenPlayer].name+" 出了10！");
    BeginBatchDraw();
    renderGameScreen();
    char title[64]; sprintf(title,"[顺手牵羊] %s 出了10！",players[tenPlayer].name.c_str());
    showMsgBox(title,"拿走另两人出的牌，然后自弃1张，下家再盲弃1张。");
    EndBatchDraw();

    // 拿走另两人的牌
    for(int i=0;i<3;++i) if(i!=tenPlayer) players[tenPlayer].addCard(tableCards[i]);
    players[tenPlayer].removeSpecificCard(tableCards[tenPlayer]);

    // 自弃1张（仅自己知，强制，不可取消）
    if(players[tenPlayer].isHuman){
        int di=guiSelectCard(tenPlayer,"[必须弃牌] 选择1张牌弃掉（仅你可见）",false);
        players[tenPlayer].removeCard(di); addMsg("[出10] 你悄悄弃了1张");
    } else {
        strategicDiscard(players[tenPlayer],1);
        addMsg("[出10] "+players[tenPlayer].name+" 弃了1张（未公开）");
    }
    BeginBatchDraw(); renderGameScreen(); EndBatchDraw();
    Sleep(400);

    // 下家盲弃1张（公开展示）
    int nextP=(tenPlayer+1)%3;
    int chosen;
    char pr[64]; sprintf(pr,"[盲弃] 从 %s 的%d张牌中选一编号",
        players[tenPlayer].name.c_str(),(int)players[tenPlayer].hand.size());
    // 小王偷窥机会（下家可先偷看 tenPlayer 手牌再选）
    performSmallJokerPeek(nextP, tenPlayer);
    if(players[nextP].isHuman){
        chosen=guiBlindSelect(nextP,pr,(int)players[tenPlayer].hand.size());
    } else {
        chosen=aiBlindChoice((int)players[tenPlayer].hand.size());
    }
    chosen=performBigJokerDefense(tenPlayer,chosen);
    // 公开展示被弃的牌
    Card shown=players[tenPlayer].hand[chosen];
    players[tenPlayer].removeCard(chosen);
    char info[64]; sprintf(info,"%s 选中了该牌并公开弃掉！",players[nextP].name.c_str());
    BeginBatchDraw();
    renderGameScreen();
    // 单张展示
    int sx=WIN_W/2-CARD_W/2, sy=WIN_H/2-CARD_H/2;
    drawCard(sx,sy,CARD_W,CARD_H,shown,true,false);
    dtC(WIN_W/2,sy+CARD_H+24,info,C_WARN,18,true);
    dtC(WIN_W/2,sy+CARD_H+52,"[ 点击继续 ]",C_DIM,14,false);
    EndBatchDraw();
    ExMessage mm;
    while(true){
        if(peekmessage(&mm,EX_MOUSE)&&mm.message==WM_LBUTTONUP) break;
        Sleep(16);
    }
    addMsg("[出10] "+players[nextP].name+" 公开弃了 "+string(rankStr(shown.rank)));
}


// ===== 大王防御 =====
int GameEngine::performBigJokerDefense(int targetPlayer, int chosen){
    // 有大王但次数已满 → 告知人类玩家
    if(players[targetPlayer].hasBigJoker() && !players[targetPlayer].canUseBigJoker()){
        if(players[targetPlayer].isHuman){
            BeginBatchDraw(); renderGameScreen();
            showMsgBox("[大王防御] 次数已用尽","大王防御已使用 2/2 次，本场无法再防御。");
            EndBatchDraw();
        } else {
            addMsg("[大王] "+players[targetPlayer].name+" 大王防御次数已满");
        }
    }
    if(!players[targetPlayer].canUseBigJoker()) return chosen;
    int handSize=(int)players[targetPlayer].hand.size();
    if(handSize<=1) return chosen; // 只剩1张，偏移无意义
    bool doDefend;
    if(players[targetPlayer].isHuman){
        char body[256];
        int remaining=2-players[targetPlayer].bigJokerUses;
        int offsetIdx=(chosen==0)?(handSize-1):(chosen-1);
        const char* chosenName=rankStr(players[targetPlayer].hand[chosen].rank);
        const char* offsetName=rankStr(players[targetPlayer].hand[offsetIdx].rank);
        sprintf(body,"对方选了 编号%d（%s）。\n可偏移至 编号%d（%s）\n（已用 %d/2 次，剩余 %d 次）",
            chosen+1, chosenName, offsetIdx+1, offsetName,
            players[targetPlayer].bigJokerUses, remaining);
        doDefend=guiYesNo("[大王防御] 触发？",body);
    } else {
        // AI：智能评估——被选中牌是中上/大牌且偏移后更弱时才防御
        int newCh=(chosen==0)?(handSize-1):(chosen-1);
        Card& chosenCard=players[targetPlayer].hand[chosen];
        Card& newCard=players[targetPlayer].hand[newCh];
        int chosenVal=chosenCard.getCompareValue(currentRule);
        int newVal=newCard.getCompareValue(currentRule);
        // 计算手牌中位值
        vector<int> hvals;
        for(auto& c:players[targetPlayer].hand) hvals.push_back(c.getCompareValue(currentRule));
        sort(hvals.begin(),hvals.end());
        int medianVal=hvals[handSize/2];
        // 被选中的牌是否"中上或大牌"（在当前规则下有价值）
        bool chosenValuable=(currentRule==BIG_WINS)?(chosenVal>=medianVal):(chosenVal<=medianVal);
        // 偏移后的牌是否更弱（更不值钱）
        bool newWeaker=(currentRule==BIG_WINS)?(newVal<chosenVal):(newVal>chosenVal);
        // 是否是特殊牌（10/5号牌有技能价值）
        bool chosenSpecial=(!chosenCard.isJoker&&(chosenCard.rank==RANK_10||chosenCard.rank==RANK_5));
        bool newSpecial=(!newCard.isJoker&&(newCard.rank==RANK_10||newCard.rank==RANK_5));
        if(chosenValuable && newWeaker){
            doDefend=true;           // 保护好牌并偏移到弱牌 → 必然防御
        } else if(chosenSpecial && !newSpecial){
            doDefend=((int)(rng()%100)<80); // 保护特殊牌偏移到普通牌 → 高概率
        } else if(newSpecial && !chosenSpecial){
            doDefend=false;          // 偏移会暴露特殊牌 → 不防御
        } else if(chosenValuable){
            doDefend=((int)(rng()%100)<30); // 好牌被选中但偏移也是好牌 → 低概率
        } else {
            doDefend=((int)(rng()%100)<15); // 弱牌被选中 → 通常不防御
        }
    }
    if(doDefend){
        players[targetPlayer].bigJokerUses++;
        int newChosen=(chosen==0)?(handSize-1):(chosen-1);
        addMsg("[大王防御] "+players[targetPlayer].name+" 偏移了目标！");
        BeginBatchDraw(); renderGameScreen();
        char info[128];
        const char* cName=rankStr(players[targetPlayer].hand[chosen].rank);
        const char* nName=rankStr(players[targetPlayer].hand[newChosen].rank);
        sprintf(info,"防御成功！编号%d（%s）→ 编号%d（%s）\n（已用 %d/2 次）",
            chosen+1,cName,newChosen+1,nName,players[targetPlayer].bigJokerUses);
        showMsgBox("[大王防御！]",info);
        EndBatchDraw();
        return newChosen;
    }
    return chosen;
}

// ===== 小王偷窥 =====
void GameEngine::performSmallJokerPeek(int fromPlayer, int targetPlayer){
    // 有小王但次数已满 → 告知人类玩家
    if(players[fromPlayer].hasSmallJoker() && !players[fromPlayer].canUseSmallJoker()){
        if(players[fromPlayer].isHuman){
            BeginBatchDraw(); renderGameScreen();
            showMsgBox("[小王偷窥] 次数已用尽","小王偷窥已使用 1/1 次，本场无法再偷窥。");
            EndBatchDraw();
        } else {
            addMsg("[小王] "+players[fromPlayer].name+" 小王偷窥次数已满");
        }
        return;
    }
    if(!players[fromPlayer].canUseSmallJoker()) return;
    bool doPeek;
    if(players[fromPlayer].isHuman){
        char body[128];
        sprintf(body,"你持有小王（已用 %d/1 次）\n可偷窥 %s 的手牌（仅你可见）",
            players[fromPlayer].smallJokerUses, players[targetPlayer].name.c_str());
        doPeek=guiYesNo("[小王偷窥] 触发？",body);
    } else {
        doPeek=((int)(rng()%100)<60);
    }
    if(!doPeek) return;
    players[fromPlayer].smallJokerUses++;
    addMsg("[小王偷窥] "+players[fromPlayer].name+" 偷窥了 "+players[targetPlayer].name);
    // 无论谁偷窥，若目标或场上有人类，均提示
    if(!players[fromPlayer].isHuman){
        // AI偷窥，通知人类（无论是否是被窥对象，都知情）
        BeginBatchDraw(); renderGameScreen();
        char ninfo[96]; sprintf(ninfo,"%s 使用了小王偷窥技能！",players[fromPlayer].name.c_str());
        showMsgBox("[小王偷窥触发！]",ninfo);
        EndBatchDraw();
    }
    if(players[fromPlayer].isHuman){
        // 展示目标手牌给人类玩家看
        int n=(int)players[targetPlayer].hand.size();
        int spacing=min(CARD_W+10,(TBL_W-100)/max(1,n));
        int totalW=(n-1)*spacing+CARD_W;
        int startX=TBL_X+(TBL_W-min(totalW,TBL_W-80))/2;
        int cardY=TBL_Y+(TBL_H-CARD_H)/2;
        BeginBatchDraw();
        renderGameScreen();
        fillArea(TBL_X,TBL_Y,TBL_W,TBL_H,C_TABLE_D,RGB(30,50,90),4);
        char title[64]; sprintf(title,"[小王偷窥] %s 的手牌（已用1/1次，仅你可见）",
            players[targetPlayer].name.c_str());
        dtC(TBL_X+TBL_W/2-200,TBL_Y+16,title,C_GOLD,16,true);
        for(int i=0;i<n;++i){
            int cx2=startX+i*min(spacing,(TBL_W-80-CARD_W)/max(1,n-1));
            drawCard(cx2,cardY,CARD_W,CARD_H,players[targetPlayer].hand[i],true,false);
        }
        dtC(TBL_X+TBL_W/2-200,TBL_Y+TBL_H-24,"[ 点击继续（AI看不见） ]",C_DIM,14,false);
        EndBatchDraw();
        ExMessage mm;
        while(true){ if(peekmessage(&mm,EX_MOUSE)&&mm.message==WM_LBUTTONUP) break; Sleep(16); }
    }
}

// ===== 连顺抽牌 =====
void GameEngine::performDrawSequence(){
    addMsg("[连顺抽牌] 三张连续！各从下家盲抽1张！");
    BeginBatchDraw(); renderGameScreen();
    showMsgBox("[连顺触发！]","三张牌点数连续！各玩家从顺时针下家手中盲抽1张！");
    EndBatchDraw();

    // 按当前积分由高到低先行
    int order[3]={0,1,2};
    sort(order,order+3,[this](int a,int b){ return players[a].score>players[b].score; });

    vector<Card> drawn(3); vector<bool> hasDrawn(3,false);

    for(int k=0;k<3;++k){
        int from=order[k];
        int target=(from+1)%3;
        if(players[target].hand.empty()){
            addMsg(players[target].name+" 手牌空，跳过");
            continue;
        }
        // 小王偷窥机会
        performSmallJokerPeek(from,target);

        int chosen;
        int tSize=(int)players[target].hand.size();
        char pr[80]; sprintf(pr,"从 %s 的%d张手牌中盲选1张",players[target].name.c_str(),tSize);
        if(players[from].isHuman){
            chosen=guiBlindSelect(from,pr,tSize);
        } else {
            chosen=aiBlindChoice(tSize);
        }
        chosen=performBigJokerDefense(target,chosen);

        drawn[from]=players[target].hand[chosen];
        players[target].hand.erase(players[target].hand.begin()+chosen);
        hasDrawn[from]=true;

        // 可见性：抽取方（人类）看到自己抽到了什么
        if(players[from].isHuman){
            BeginBatchDraw();
            renderGameScreen();
            fillArea(TBL_X,TBL_Y,TBL_W,TBL_H,C_TABLE_D,RGB(30,50,90),4);
            dtC(TBL_X+TBL_W/2-200,TBL_Y+20,"[连顺抽牌] 你抽到了：",C_GOLD,18,true);
            int sx=TBL_X+TBL_W/2-200-CARD_W/2;
            drawCard(sx,TBL_Y+60,CARD_W,CARD_H,drawn[from],true,false);
            dtC(TBL_X+TBL_W/2-200,TBL_Y+TBL_H-24,"[ 点击继续（仅你可见） ]",C_DIM,14,false);
            EndBatchDraw();
            ExMessage mm;
            while(true){ if(peekmessage(&mm,EX_MOUSE)&&mm.message==WM_LBUTTONUP) break; Sleep(16); }
        } else {
            addMsg(players[from].name+" 从 "+players[target].name+" 处抽1张");
            BeginBatchDraw(); renderGameScreen(); EndBatchDraw();
            Sleep(600);
        }
        // 被抽方（人类）得到通知
        if(players[target].isHuman){
            char info[64]; sprintf(info,"你的 %s 被 %s 抽走了！",
                rankStr(drawn[from].rank),players[from].name.c_str());
            BeginBatchDraw(); renderGameScreen();
            showMsgBox("[连顺抽牌] 你的牌被抽走了！",info);
            EndBatchDraw();
        }
    }
    for(int i=0;i<3;++i) if(hasDrawn[i]) players[i].addCard(drawn[i]);
    addMsg("[连顺] 抽牌完毕");
}


// ===== 主回合（GUI版）=====
void GameEngine::playRound(){
    msgLog.clear();
    tableCards.clear(); tableCards.resize(3);
    playedIdx.assign(3,-1);
    tableRevealed=false;

    // Step 0: 5号牌归还
    processFiveReturns();

    // Step 1: 出牌阶段
    // AI先出（静默），人类交互出
    vector<bool> hasCanceled(3,false);
    for(int i=1;i<3;++i){
        // 玩家B(1)：策略AI；玩家C(2)：随机AI（特殊处理相同，仅一般出牌随机）
        int c=(i==2)?randomChoice(i):strategicChoice(i);
        playedIdx[i]=c;
        tableCards[i]=players[i].hand[c];
    }

    // 人类出牌
    int humanSel=-1;
    int mx=0,my=0;
    int n=(int)players[0].hand.size();
    int overlap=min(CARD_W+10,(HND_W-20)/max(1,n));
    int startX=HND_X+(HND_W-min((n-1)*overlap+CARD_W,HND_W-20))/2;
    int cardY=HND_Y+26;

    Btn bPlay  (ACT_X+8, ACT_Y+8,  ACT_W-16, 40, "出牌",   18, false);
    Btn bRule  (ACT_X+8, ACT_Y+54, ACT_W-16, 36, "查看规则",14);
    Btn bHint  (ACT_X+8, ACT_Y+96, ACT_W-16, 36, "提示",   14);
    Btn bQuit  (ACT_X+8, ACT_Y+138,ACT_W-16, 36, "退出游戏",14);
    vector<Btn> actionBtns={bPlay,bRule,bHint,bQuit};

    bool _confirmed=false;
    while(!_confirmed){
        BeginBatchDraw();
        renderGameScreen();
        // 覆盖手牌区（含选中）
        fillArea(HND_X,HND_Y,HND_W,HND_H,C_PANEL,RGB(50,90,55),6);
        dtL(HND_X+10,HND_Y+6,"你的手牌  ← 点击选牌，再点出牌按钮确认",C_BLUE_T,14,true);
        for(int i=0;i<n;++i){
            bool s=(i==humanSel);
            int cx2=startX+i*min(overlap,(HND_W-20-CARD_W)/max(1,n-1));
            int cy2=cardY+(s?-12:0);
            drawCard(cx2,cy2,CARD_W,CARD_H-10,players[0].hand[i],true,s);
        }
        fillArea(ACT_X,ACT_Y,ACT_W,ACT_H,C_PANEL_D,RGB(25,40,80),6);
        actionBtns[0].enabled=(humanSel>=0);
        for(auto& b:actionBtns) b.draw(b.hit(mx,my));
        EndBatchDraw();

        ExMessage msg;
        while(peekmessage(&msg,EX_MOUSE)){
            mx=msg.x; my=msg.y;
            if(msg.message==WM_LBUTTONUP){
                // 点牌
                for(int i=0;i<n;++i){
                    int cx2=startX+i*min(overlap,(HND_W-20-CARD_W)/max(1,n-1));
                    if(mx>=cx2&&mx<=cx2+CARD_W&&my>=cardY-14&&my<=cardY+CARD_H)
                        humanSel=(humanSel==i)?-1:i;
                }
                // 出牌按钮
                if(actionBtns[0].hit(mx,my)&&humanSel>=0){ _confirmed=true; break; }
                // 规则按钮
                if(actionBtns[1].hit(mx,my)){
                    BeginBatchDraw(); renderGameScreen();
                    showMsgBox("游戏规则","比大:K最大A最小 | 比小:A最优K最差\n出10拿走他人牌 | 5号牌收回自己的牌\n连顺触发随机抽牌 | 大王防御\n小王偷窥（连顺抓牌/出10下家盲弃）");
                    EndBatchDraw();
                }
                // 提示按钮
                if(actionBtns[2].hit(mx,my)){
                    int hint=strategicChoice(0);
                    humanSel=hint;
                }
                // 退出按钮
                if(actionBtns[3].hit(mx,my)){
                    BeginBatchDraw(); renderGameScreen();
                    bool confirm=guiYesNo("[退出] 确认返回主界面？","当前游戏进度将不保存。\n确定要返回主界面吗？");
                    EndBatchDraw();
                    if(confirm){ quitToMenu=true; return; }
                }
            }
        }
        Sleep(16);
    }
    playedIdx[0]=humanSel;
    tableCards[0]=players[0].hand[humanSel];

    // Step 2: 动画亮牌
    tableRevealed=true;
    addMsg("[亮牌] 三人同时亮牌");
    // 逐张翻牌动效（简化：先背面0.3秒后正面）
    for(int reveal=0;reveal<3;++reveal){
        BeginBatchDraw();
        renderGameScreen();
        // 提前高亮刚亮的牌
        if(reveal<3){
            int spacing=CARD_W+24;
            int totalW=3*spacing-24;
            int sx2=TBL_X+(TBL_W-totalW)/2;
            int sy2=TBL_Y+(TBL_H-CARD_H)/2-10;
            for(int i=0;i<3;++i){
                if(i<=reveal) drawCard(sx2+i*spacing,sy2,CARD_W,CARD_H,tableCards[i],true,false);
                else          drawCardBack(sx2+i*spacing,sy2,CARD_W,CARD_H);
            }
        }
        EndBatchDraw();
        Sleep(260);
    }
    BeginBatchDraw(); renderGameScreen(); EndBatchDraw();
    Sleep(300);

    // Step 3: 大王/小王同台提示
    bool hasBig=false, hasSmall=false;
    for(int i=0;i<3;++i){
        if(tableCards[i].isJoker){
            if(tableCards[i].rank==RANK_BIG_JOKER) hasBig=true;
            else hasSmall=true;
        }
    }
    if(hasBig&&hasSmall){
        addMsg("[大小王同台] 双王出现！");
        BeginBatchDraw(); renderGameScreen();
        showMsgBox("[大小王同台！]","大王与小王同时出现！两者均视为最优，本局计分不变。");
        EndBatchDraw();
    }

    // Step 4: 出10检查（优先）——必须唯一出10才触发
    int tenCount=0, tenPlayer=-1;
    for(int i=0;i<3;++i)
        if(!tableCards[i].isJoker && tableCards[i].rank==RANK_10){ tenCount++; tenPlayer=i; }
    bool hasTen=(tenCount==1); // 唯一一个人出10才触发顺手牧羊

    // Step 5: 从手中移除打出的牌（出10方稍后特殊处理）
    for(int i=0;i<3;++i){
        if(hasTen && i==tenPlayer) continue; // 出10方的牌后面在perform10里处理
        if(playedIdx[i]>=0 && playedIdx[i]<(int)players[i].hand.size())
            players[i].hand.erase(players[i].hand.begin()+playedIdx[i]);
    }

    if(hasTen){
        perform10Mechanism(tenPlayer);
        // 若出10的同时三张构成顺子，顺手牵羊结束后也触发连顺抽牌
        {
            vector<bool> skipMask10(3,false);
            for(int i=0;i<3;++i) skipMask10[i]=tableCards[i].isReturned;
            if(isThreeConsecutive(tableCards,skipMask10)){
                addMsg("[出10+连顺] 出10同时构成顺子，额外触发连顺抽牌！");
                BeginBatchDraw(); renderGameScreen();
                showMsgBox("[出10+连顺！]","出10构成顺子！顺手牵羊完成后，各玩家再从顺时针下家盲抽1张！");
                EndBatchDraw();
                performDrawSequence();
            }
        }
        addMsg("[出10局] 本局不计分");
        BeginBatchDraw(); renderGameScreen();
        showMsgBox("[出10] 本局不计分","顺手牵羊机制触发，本局积分跳过。");
        EndBatchDraw();
    } else {
        // Step 5b: 出10方正常移除
        // (已在上面处理非tenPlayer，tenPlayer==-1时全部处理完)

        // Step 6: 连顺检查（非第18局）
        vector<bool> skipMask(3,false);
        for(int i=0;i<3;++i) skipMask[i]=tableCards[i].isReturned;
        bool consecutive=(round<18) && isThreeConsecutive(tableCards,skipMask);

        // Step 7: 5号牌激活（无连顺+无出10时）
        vector<bool> activated;
        if(!consecutive){
            perform5CardActivations(tableCards,playedIdx,activated);
        }

        // Step 8: 连顺抽牌（无5号牌激活时）
        bool anyActivated=false;
        for(bool a:activated) if(a) anyActivated=true;
        if(consecutive && !anyActivated){
            performDrawSequence();
        }

        // Step 9: 计分
        vector<int> scores=computeScores(tableCards);
        for(int i=0;i<3;++i) players[i].score+=scores[i];
        {
            string smsg="[计分] ";
            for(int i=0;i<3;++i){
                smsg+=players[i].name+":+"+to_string(scores[i])+" ";
            }
            addMsg(smsg);
        }

        // Step 10: 补分（两人或三人相同时，补给唯一最低分）
        applyBonusScore(tableCards);

        // Step 11: 规则翻转判断
        handleRuleFlip(tableCards);

        // Step 12: 本局结果展示
        BeginBatchDraw();
        renderGameScreen();
        // 结果面板
        int pw=440, ph=200;
        int px=(WIN_W-pw)/2, py=(WIN_H-ph)/2+60;
        fillRR(px,py,pw,ph,12,C_PANEL_D,C_GOLD,2);
        dtC(px+pw/2,py+28,"本局结果",C_GOLD,20,true);
        setlinecolor(C_GOLD); line(px+16,py+50,px+pw-16,py+50);
        for(int i=0;i<3;++i){
            char buf[64]; sprintf(buf,"%s  +%d分  (总:%d)",
                players[i].name.c_str(),scores[i],players[i].score);
            COLORREF tc=(scores[i]==2)?C_GOLD:(scores[i]==1)?C_GREEN_T:C_DIM;
            dtC(px+pw/2, py+72+i*38, buf, tc, 17, scores[i]==2);
        }
        dtC(px+pw/2,py+ph-28,"[ 点击继续 ]",C_DIM,14,false);
        EndBatchDraw();
        ExMessage mm;
        while(true){ if(peekmessage(&mm,EX_MOUSE)&&mm.message==WM_LBUTTONUP) break; Sleep(16); }
    }
    // 清空桌面
    tableRevealed=false; tableCards.clear(); tableCards.resize(3);
}


// ===== 显示最终排名 =====
int GameEngine::showFinalRank(vector<int> tbScores){
    bool hasTb=false; for(int s:tbScores) if(s>0) hasTb=true;
    int ord[3]={0,1,2};
    // 主分降序；主分相同时加赛分高者优先
    sort(ord,ord+3,[this,&tbScores](int a,int b){
        if(players[a].score!=players[b].score) return players[a].score>players[b].score;
        return tbScores[a]>tbScores[b];
    });
    const char* medals[3]={"冠军","亚军","季军"};
    COLORREF cols[3]={C_GOLD,C_SILVER,RGB(180,100,50)};

    auto drawContent=[&](int px,int py,int pw,int ph){
        setlinecolor(RGB(0,0,0)); setfillcolor(RGB(0,0,0));
        for(int yy=0;yy<WIN_H;yy+=3) line(0,yy,WIN_W,yy);
        fillRR(px,py,pw,ph,14,C_PANEL_D,C_GOLD,3);
        dtC(px+pw/2,py+32,"游戏结束！最终排名",C_GOLD,24,true);
        setlinecolor(C_GOLD); line(px+20,py+58,px+pw-20,py+58);
        for(int k=0;k<3;++k){
            int i=ord[k];
            char buf[80];
            if(hasTb&&tbScores[i]>0)
                sprintf(buf,"%s  %s   %d 分  (加赛%d分)",medals[k],players[i].name.c_str(),players[i].score,tbScores[i]);
            else
                sprintf(buf,"%s  %s   %d 分",medals[k],players[i].name.c_str(),players[i].score);
            dtC(px+pw/2, py+90+k*60, buf, cols[k], 20, k==0);
        }
        dtC(px+pw/2,py+ph-80,"感谢游玩《三雄争锋》！",C_TEXT,16,false);
    };

    int pw=580, ph=420, px=(WIN_W-pw)/2, py=(WIN_H-ph)/2;
    if(gameMode==1){
        Btn bAgain(px+40,py+ph-52,pw/2-50,38,"再来一局（同设置）",16);
        Btn bMenu (px+pw/2+10,py+ph-52,pw/2-50,38,"返回主菜单",16);
        int mx=0,my=0,res=-1;
        while(res<0){
            BeginBatchDraw();
            renderGameScreen();
            drawContent(px,py,pw,ph);
            for(auto& b:{bAgain,bMenu}) b.draw(b.hit(mx,my));
            EndBatchDraw();
            ExMessage msg;
            while(peekmessage(&msg,EX_MOUSE)){
                mx=msg.x; my=msg.y;
                if(msg.message==WM_LBUTTONUP){
                    if(bAgain.hit(mx,my)) res=0;
                    if(bMenu.hit(mx,my))  res=1;
                }
            }
            Sleep(16);
        }
        return res;
    } else {
        BeginBatchDraw();
        renderGameScreen();
        drawContent(px,py,pw,ph);
        dtC(px+pw/2,py+ph-18,"[ 点击返回主菜单 ]",C_DIM,13,false);
        EndBatchDraw();
        ExMessage mm;
        while(true){ if(peekmessage(&mm,EX_MOUSE)&&mm.message==WM_LBUTTONUP) break; Sleep(16); }
        return 1;
    }
}

// ===== 加赛 =====
void GameEngine::playTiebreaker(vector<int>& tied, vector<int>& tbScoresOut){
    tbScoresOut.assign(3,0);
    while(true){
        // 发5张
        for(int i:tied) players[i].hand.clear();
        initDeck(); shuffleDeck();
        int ci=0;
        for(int r=0;r<5;++r) for(int i:tied) players[i].addCard(deck[ci++]);

        vector<int> tbScore(3,0);
        for(int tb=1;tb<=5;++tb){
            tableCards.clear(); tableCards.resize(3);
            playedIdx.assign(3,-1);
            tableRevealed=false;

            // AI出牌
            for(int i:tied) if(!players[i].isHuman){
                int c=(int)(rng()%players[i].hand.size());
                playedIdx[i]=c; tableCards[i]=players[i].hand[c];
            }
            // 人类出牌
            bool humanIn=false; for(int i:tied) if(players[i].isHuman) humanIn=true;
            if(humanIn){
                // 加赛出牌强制，不可取消
                int h=guiSelectCard(0,"[加赛第"+to_string(tb)+"/5局] 请选择出牌",false);
                playedIdx[0]=h; tableCards[0]=players[0].hand[h];
            }
            // 亮牌
            tableRevealed=true;
            BeginBatchDraw(); renderGameScreen(); EndBatchDraw(); Sleep(400);

            // 计分（仅参与者）
            if((int)tied.size()==2){
                int a=tied[0],b=tied[1];
                int va=tableCards[a].getCompareValue(currentRule);
                int vb=tableCards[b].getCompareValue(currentRule);
                bool aWin=(currentRule==BIG_WINS)?va>vb:va<vb;
                if(va==vb){ tbScore[a]++; tbScore[b]++; }
                else if(aWin) tbScore[a]+=2;
                else tbScore[b]+=2;
            } else {
                auto sc=computeScores(tableCards);
                for(int i:tied) tbScore[i]+=sc[i];
            }
            // 移除打出的牌
            for(int i:tied)
                if(playedIdx[i]>=0&&playedIdx[i]<(int)players[i].hand.size())
                    players[i].hand.erase(players[i].hand.begin()+playedIdx[i]);

            addMsg("[加赛"+to_string(tb)+"/5] 本局结束");
            BeginBatchDraw(); renderGameScreen(); EndBatchDraw(); Sleep(600);
            tableRevealed=false;
        }
        // 判断
        int maxTb=0; for(int i:tied) if(tbScore[i]>maxTb) maxTb=tbScore[i];
        vector<int> still;
        for(int i:tied) if(tbScore[i]==maxTb) still.push_back(i);
        if((int)still.size()==1){ tied=still; tbScoresOut=tbScore; break; }
        tied=still;
        BeginBatchDraw(); renderGameScreen();
        showMsgBox("[加赛平局]","仍然平局，继续加赛！");
        EndBatchDraw();
    }
}

// ===== 检查达标结束 =====
bool GameEngine::checkEndCondition(vector<int>& tied){
    if(gameMode==0) return false;
    bool any=false;
    for(int i=0;i<3;++i) if(players[i].score>=targetScore){ any=true; break; }
    if(!any) return false;
    int maxS=0; for(int i=0;i<3;++i) if(players[i].score>maxS) maxS=players[i].score;
    vector<int> top;
    for(int i=0;i<3;++i) if(players[i].score==maxS) top.push_back(i);
    if((int)top.size()==1) return true;
    tied=top; return true;
}

// ===== 开始新游戏 =====
void GameEngine::startNewGame(){
    // 达标分模式再来一局时跳过模式和分数选择
    if(!skipModeSelect){
        gameMode=showModeSelect();
        if(gameMode==1){
            int bw=440, bh=290, bx=(WIN_W-bw)/2, by=(WIN_H-bh)/2;
            Btn b30(bx+30,by+80,bw-60,44,"30 分",19);
            Btn b60(bx+30,by+132,bw-60,44,"60 分",19);
            Btn b100(bx+30,by+184,bw-60,44,"100 分",19);
            Btn b150(bx+30,by+236,bw-60,44,"150 分",19);
            vector<Btn> tbBtns={b30,b60,b100,b150};
            int tscores[]={30,60,100,150};
            int chosen=waitBtns(tbBtns,[&](){
                setfillcolor(C_TABLE); fillrectangle(0,0,WIN_W,WIN_H);
                fillRR(bx,by,bw,bh,12,C_PANEL_D,C_GOLD,2);
                dtC(bx+bw/2,by+40,"选择目标分",C_GOLD,22,true);
            });
            targetScore=tscores[chosen];
        }
    }
    skipModeSelect=false;

    if(!consecutiveGame){
        for(int i=0;i<3;++i){ players[i].score=0; players[i].resetJokerUses(); }
        sceneCount=1;
    }
    for(int i=0;i<3;++i) players[i].hand.clear();
    round=1; lastRoundTwoWayTie=false;
    for(int i=0;i<3;++i) fiveReturnPending[i]=false;
    initDeck(); shuffleDeck(); dealCards(18);

    // 发牌后先展示人类手牌，再让黑桃A选规则
    {
        BeginBatchDraw();
        setfillcolor(C_TABLE); fillrectangle(0,0,WIN_W,WIN_H);
        renderInfoBar();
        renderHumanHand();
        dtC(WIN_W/2,WIN_H/2-100,"发牌完成！请先查看你的手牌",C_GOLD,22,true);
        dtC(WIN_W/2,WIN_H/2-60,"（点击继续选择规则）",C_DIM,16,false);
        EndBatchDraw();
        ExMessage mm;
        while(true){ if(peekmessage(&mm,EX_MOUSE)&&mm.message==WM_LBUTTONUP) break; Sleep(16); }
    }

    // 黑桃A选规则
    int chooser=-1;
    for(int i=0;i<3;++i) if(players[i].hasSpadeA()){ chooser=i; break; }
    if(!consecutiveGame){
        if(chooser==0){
            int bw=480,bh=240,bx=(WIN_W-bw)/2,by=BAR_H+20;
            Btn bBig  (bx+30,by+110,bw-60,52,"比大 (K最大，A最小)",18);
            Btn bSmall(bx+30,by+172,bw-60,52,"比小 (A最优，K最差)",18);
            vector<Btn> rBtns={bBig,bSmall};
            int r=waitBtns(rBtns,[&](){
                // 背景：渲染信息栏+手牌区，让玩家能看到自己持有的牌
                setfillcolor(C_TABLE); fillrectangle(0,0,WIN_W,WIN_H);
                renderInfoBar();
                renderHumanHand();
                // 叠加半透明遮罩（深色矩形）让弹框更清晰
                setfillcolor(RGB(8,14,32)); setlinecolor(RGB(8,14,32));
                solidrectangle(0,0,WIN_W,BAR_H+158); // 遮住AI区和桌面区
                // 弹框
                fillRR(bx,by,bw,bh,12,C_PANEL_D,C_GOLD,2);
                dtC(bx+bw/2,by+28,"你持有黑桃A，选择初始规则",C_GOLD,20,true);
                dtC(bx+bw/2,by+58,"（下方手牌可供参考）",C_DIM,14,false);
            });
            currentRule=(r==0)?BIG_WINS:SMALL_WINS;
        } else {
            currentRule=aiSmartRuleChoice(chooser);
            BeginBatchDraw(); renderGameScreen();
            char info[64]; sprintf(info,"%s 持有黑桃A，选择了：%s",
                (chooser>=0)?players[chooser].name.c_str():"系统",
                currentRule==BIG_WINS?"比大":"比小");
            showMsgBox("初始规则确定",info);
            EndBatchDraw();
        }
    } else {
        if(chooser>=0){
            players[chooser].score++;
            char info[64]; sprintf(info,"%s 持有黑桃A，续场奖励+1分",players[chooser].name.c_str());
            BeginBatchDraw(); renderGameScreen();
            showMsgBox("续场开始",info);
            EndBatchDraw();
        }
    }
    consecutiveGame=false;

    quitToMenu=false;
    // 主循环
    for(;round<=18;++round){
        playRound();
        if(quitToMenu){ showMainMenu(); return; }
        if(gameMode==1){
            vector<int> tied;
            if(checkEndCondition(tied)){
                if(tied.empty()){
                    int fr=showFinalRank();
                    if(fr==0){ skipModeSelect=true; for(int i=0;i<3;++i){ players[i].score=0; players[i].resetJokerUses(); } startNewGame(); }
                    return;
                }
                BeginBatchDraw(); renderGameScreen();
                showMsgBox("达标！进入加赛","有玩家达标但分数并列，进行加赛！");
                EndBatchDraw();
                vector<int> tbS;
                playTiebreaker(tied,tbS);
                int fr=showFinalRank(tbS);
                if(fr==0){ skipModeSelect=true; for(int i=0;i<3;++i){ players[i].score=0; players[i].resetJokerUses(); } startNewGame(); }
                return;
            }
        }
        if(round==18) break;
    }
    // 18局结束
    if(gameMode==0){
        // 单局模式：检查是否并列第一，并列则加赛
        int maxS=0; for(int i=0;i<3;++i) if(players[i].score>maxS) maxS=players[i].score;
        vector<int> top; for(int i=0;i<3;++i) if(players[i].score==maxS) top.push_back(i);
        if((int)top.size()>=2){
            BeginBatchDraw(); renderGameScreen();
            showMsgBox("平局！进入加赛","18局结束，最高分并列！\n进行加赛决出冠军！");
            EndBatchDraw();
            vector<int> tbS;
            playTiebreaker(top,tbS);
            showFinalRank(tbS);
        } else {
            showFinalRank();
        }
    } else {
        // 达标分模式18局结束且无人达标：让玩家选择继续或退出，不重选模式
        int bw=500,bh=220,bx=(WIN_W-bw)/2,by=(WIN_H-bh)/2;
        Btn bCont(bx+30,by+100,bw-60,48,"继续游戏（积分继承，同设置）",17);
        Btn bBack(bx+30,by+158,bw-60,44,"返回主界面",17);
        vector<Btn> endBtns={bCont,bBack};
        int choice=waitBtns(endBtns,[&](){
            setfillcolor(C_TABLE); fillrectangle(0,0,WIN_W,WIN_H);
            fillRR(bx,by,bw,bh,12,C_PANEL_D,C_GOLD,2);
            dtC(bx+bw/2,by+36,"18局结束！尚无人达标",C_GOLD,20,true);
            dtC(bx+bw/2,by+68,"积分继承，重新发牌，无需重选模式",C_TEXT,15,false);
        });
        if(choice==0){
            sceneCount++;
            consecutiveGame=true;
            skipModeSelect=true; // 不重新选模式和分数
            for(int i=0;i<3;++i) players[i].resetJokerUses();
            startNewGame();
        }
        // choice==1 → 自然 return，回到主菜单
    }
}


// ===== 规则界面 =====
void GameEngine::showRulesScreen(){
    struct RuleItem{ const char* icon; const char* title; const char* desc; };
    RuleItem items[]={
        {"[基础]","三人对战 54张·18局","每人18张，共18局。积分：第1名+2，第2名+1，第3名+0"},
        {"[比大]","K最大 A最小","比大模式：K>Q>J>10>...>3>2>A，大王/小王均为最优"},
        {"[比小]","A最优 K最差","比小模式：A>2>3>...>Q>K，大王/小王均为最优"},
        {"[出10]","顺手牵羊（本局不计分）","唯一出10：拿走另两人出的牌，自弃1张，顺时针下家盲弃1张"},
        {"[5号]","狸猫换太子","三张各不同且你非最优：消耗额外奋同（+5）可将本局出的牌收回"},
        {"[连顺]","乱武抽牌","三张点数连续（非被收回牌）：各从顺时针下家手中盲抽1张；出10同时构成顺子也会触发"},
        {"[大王]","防御偏移","被下家选中盲弃时，可将目标编号偏移一位（每场限用2次）"},
        {"[小王]","偷窥手牌","连顺抽牌前，可偷窥任意对手手牌，仅自己可见（每场限用1次）"},
        {"[反转一]","三张全同必然反转","三人出牌点数完全相同：本局得分均为0，规则立即永久反转"},
        {"[反转二]","连续两次两张同必反转","连续两局都恰好有两张牌相同（非全同）：规则立即反转一次"},
        {"[补分]","落后追分","本局有两/三人出牌相同：唯一最低分玩家额外+1分（平分则不补）"},
        {"[加赛]","并列达标决胜","达标分模式下并列达标：进行5张5局加赛，连续加赛直到分出高下"},
    };
    int n=sizeof(items)/sizeof(items[0]);
    int scroll=0;
    int perPage=7;

    Btn bBack(WIN_W/2-80,WIN_H-52,160,40,"返回主菜单",17);
    vector<Btn> navBtns={bBack};

    int mx=0,my=0;
    while(true){
        BeginBatchDraw();
        setfillcolor(C_TABLE); fillrectangle(0,0,WIN_W,WIN_H);
        fillRR(30,10,WIN_W-60,WIN_H-20,12,C_PANEL_D,C_GOLD,2);
        dtC(WIN_W/2,46,"《三雄争锋》游戏规则总览",C_GOLD,26,true);
        setlinecolor(C_GOLD); line(50,72,WIN_W-50,72);
        // 规则条目
        for(int k=0;k<perPage&&(k+scroll)<n;++k){
            int i=k+scroll;
            int ry=86+k*82;
            fillRR(50,ry,WIN_W-100,74,8,C_PANEL,RGB(28,50,98));
            setlinecolor(RGB(55,90,160)); rectangle(50,ry,50+WIN_W-100,ry+74);
            dtL(62,ry+8, items[i].icon, C_GOLD, 14, true);
            dtL(62,ry+30, items[i].title, C_WHITE, 17, true);
            dtL(175,ry+14, items[i].desc, C_TEXT, 14, false);
        }
        // 滚动提示
        if(scroll>0)    dtC(WIN_W-44,90,"▲",C_GOLD,16,true);
        if(scroll+perPage<n) dtC(WIN_W-44,WIN_H-90,"▼",C_GOLD,16,true);
        // 底部提示
        dtC(WIN_W/2,WIN_H-72,"详细规则参见《游戏设计文档v2》及《游戏用户文档v2》",C_SILVER,13,false);
        for(auto& b:navBtns) b.draw(b.hit(mx,my));
        EndBatchDraw();

        ExMessage msg;
        while(peekmessage(&msg,EX_MOUSE)){
            mx=msg.x; my=msg.y;
            if(msg.message==WM_MOUSEWHEEL){
                if((short)HIWORD(msg.wheel)>0) scroll=max(0,scroll-1);
                else scroll=min(n-perPage,scroll+1);
            }
            if(msg.message==WM_LBUTTONUP){
                if(navBtns[0].hit(mx,my)) goto rules_back;
                if(mx>=WIN_W-64&&mx<=WIN_W-16&&my>=80&&my<=120) scroll=max(0,scroll-1);
                if(mx>=WIN_W-64&&mx<=WIN_W-16&&my>=WIN_H-120&&my<=WIN_H-80) scroll=min(n-perPage,scroll+1);
            }
        }
        Sleep(16);
    }
    rules_back:;
}

// ===== 模式选择 =====
int GameEngine::showModeSelect(){
    int bw=520,bh=280,bx=(WIN_W-bw)/2,by=(WIN_H-bh)/2;
    Btn bSingle(bx+30,by+90, bw-60,54,"单局模式（18局，按总分排名）",18);
    Btn bTarget(bx+30,by+154,bw-60,54,"达标分模式（先达目标分者胜）",18);
    vector<Btn> btns={bSingle,bTarget};
    return waitBtns(btns,[&](){
        setfillcolor(C_TABLE); fillrectangle(0,0,WIN_W,WIN_H);
        fillRR(bx,by,bw,bh,12,C_PANEL_D,C_GOLD,2);
        dtC(bx+bw/2,by+44,"选择游戏模式",C_GOLD,22,true);
        setlinecolor(C_GOLD); line(bx+20,by+68,bx+bw-20,by+68);
    });
}

// ===== 主菜单 =====
void GameEngine::showMainMenu(){
    Btn bStart (WIN_W/2-130,340,260,58,"开始游戏",22);
    Btn bRules (WIN_W/2-130,414,260,52,"游戏规则",19);
    Btn bExit  (WIN_W/2-130,482,260,52,"退出游戏",19);
    vector<Btn> btns={bStart,bRules,bExit};

    int mx=0,my=0;
    while(true){
        BeginBatchDraw();
        // 渐变背景
        for(int y=0;y<WIN_H;++y){
            int r=max(0,22-(int)(y*8/WIN_H));
            int g=max(0,100-(int)(y*28/WIN_H));
            int b=max(0,52-(int)(y*14/WIN_H));
            setlinecolor(RGB(r,g,b));
            line(0,y,WIN_W,y);
        }
        // 标题装饰背景块
        fillRR(WIN_W/2-300,60,600,240,16,RGB(8,45,22),C_GOLD,2);
        // 主标题
        dtC(WIN_W/2,140,"三 雄 争 锋",C_GOLD,64,true);
        dtC(WIN_W/2,218,"San Xiong Zheng Feng  ·  Card Battle v3.0",C_DIM,16,false);
        setlinecolor(C_GOLD); line(WIN_W/2-220,248,WIN_W/2+220,248);
        dtC(WIN_W/2,275,"三人对战  |  54张牌  |  EasyX 图形界面",C_SILVER,16,false);
        // 按钮
        for(auto& b:btns) b.draw(b.hit(mx,my));
        // 版权
        dtC(WIN_W/2,WIN_H-24,"欢迎游玩，祝旗开得胜！",C_DIM,13,false);
        EndBatchDraw();

        ExMessage msg;
        while(peekmessage(&msg,EX_MOUSE)){
            mx=msg.x; my=msg.y;
            if(msg.message==WM_LBUTTONUP){
                if(btns[0].hit(mx,my)){
                    consecutiveGame=false;
                    startNewGame();
                } else if(btns[1].hit(mx,my)){
                    showRulesScreen();
                } else if(btns[2].hit(mx,my)){
                    closegraph(); exit(0);
                }
            }
        }
        Sleep(16);
    }
}

// ===== main =====
int main(){
    SetConsoleOutputCP(936);
    initgraph(WIN_W, WIN_H); // 显示图形窗口
    SetWindowTextA(GetHWnd(),"三雄争锋 v3.0");
    setbkcolor(C_TABLE);
    BeginBatchDraw();
    GameEngine eng;
    g_eng=&eng;
    eng.showMainMenu();
    EndBatchDraw();
    closegraph();
    return 0;
}
