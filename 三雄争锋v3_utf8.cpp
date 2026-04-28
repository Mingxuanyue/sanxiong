/*
 * 锟斤拷锟斤拷锟斤拷锟斤拷 v3.0 (EasyX 图锟轿斤拷锟斤拷锟?
 * 锟斤拷锟斤拷: Dev-C++ 5.11, C++11
 * 锟斤拷锟斤拷: 锟斤拷锟饺帮拷装 EasyX 图锟轿匡拷 (https://easyx.cn)
 * 锟斤拷锟斤拷选锟斤拷: -std=c++11
 * 锟街凤拷锟斤拷锟斤拷: ANSI/GBK
 */
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

// ===== 锟斤拷锟节尺达拷 =====
const int WIN_W = 1280;
const int WIN_H = 800;
const int CARD_W = 78;
const int CARD_H = 108;

// ===== 锟斤拷色锟斤拷锟斤拷 =====
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

// ===== 锟斤拷锟斤拷锟斤拷锟斤拷 =====
// 锟斤拷锟斤拷锟斤拷息锟斤拷
const int BAR_H  = 56;
// AI1 锟斤拷 (players[1]) - 锟斤拷锟斤拷锟斤拷
const int AI1_X = 10,  AI1_Y = BAR_H+4,  AI1_W = 580, AI1_H = 148;
// AI2 锟斤拷 (players[2]) - 锟斤拷锟斤拷锟斤拷
const int AI2_X = 598, AI2_Y = BAR_H+4,  AI2_W = 674, AI2_H = 148;
// 锟斤拷锟斤拷锟斤拷 - 锟斤拷锟诫（锟斤拷锟斤拷锟斤拷锟?+ 锟斤拷息锟斤拷
const int TBL_X = 10,  TBL_Y = BAR_H+158, TBL_W = 1262, TBL_H = 310;
// 锟斤拷锟斤拷锟斤拷锟斤拷锟斤拷 - 锟阶诧拷
const int HND_X = 10,  HND_Y = BAR_H+474, HND_W = 1082, HND_H = 186;
// 锟斤拷锟斤拷锟斤拷钮锟斤拷 - 锟斤拷锟斤拷
const int ACT_X = 1098,ACT_Y = BAR_H+474, ACT_W = 174,  ACT_H = 186;

// ===== 锟斤拷锟藉工锟斤拷 =====
void setFont(int sz, bool bold=false, const char* face="微锟斤拷锟脚猴拷"){
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

// ===== 锟斤拷图锟斤拷锟斤拷 =====
void fillRR(int x,int y,int w,int h,int r,COLORREF f,COLORREF lc=RGB(0,0,0),int lw=1){
    setfillcolor(f); setlinecolor(lc); setlinestyle(PS_SOLID,lw);
    fillroundrect(x,y,x+w,y+h,r,r);
}
void drawRR(int x,int y,int w,int h,int r,COLORREF lc,int lw=2){
    setlinecolor(lc); setlinestyle(PS_SOLID,lw);
    // outline only: keep last fill color (no NULLBRUSH in MinGW EasyX)
    roundrect(x,y,x+w,y+h,r,r);
}
// 锟斤拷锟斤拷锟斤拷洌拷锟斤拷伪锟斤拷锟斤拷锟?
void fillArea(int x,int y,int w,int h,COLORREF f,COLORREF lc=RGB(0,0,0),int r=6){
    fillRR(x,y,w,h,r,f,lc);
}

// ===== 锟斤拷钮 =====
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

// ===== 锟斤拷准锟斤拷息锟斤拷锟斤拷锟斤拷模态锟斤拷锟角层）=====
void showMsgBox(const string& title, const string& body, int bw=520, int bh=220){
    int bx=(WIN_W-bw)/2, by=(WIN_H-bh)/2;
    // 锟斤拷透锟斤拷锟斤拷锟斤拷
    setlinecolor(RGB(0,0,0));
    setfillcolor(RGB(0,0,0));
    for(int yy=0;yy<WIN_H;yy+=3) line(0,yy,WIN_W,yy);
    fillRR(bx,by,bw,bh,12,C_PANEL_D,C_GOLD,2);
    dtC(bx+bw/2, by+40, title.c_str(), C_GOLD, 22, true);
    // 锟街革拷锟斤拷
    setlinecolor(C_GOLD);
    line(bx+20,by+65,bx+bw-20,by+65);
    dtC(bx+bw/2, by+bh/2+10, body.c_str(), C_TEXT, 18, false);
    dtC(bx+bw/2, by+bh-36, "[ 锟斤拷锟斤拷锟斤拷獯︼拷锟斤拷锟?]", C_DIM, 15, false);
    FlushBatchDraw();
    // 锟饺达拷锟斤拷锟?
    ExMessage msg;
    while(true){
        if(peekmessage(&msg,EX_MOUSE) && msg.message==WM_LBUTTONUP) break;
        Sleep(16);
    }
}

// 锟斤拷/锟斤拷曰锟斤拷颍锟斤拷锟?true=锟斤拷
bool showYesNo(const string& title, const string& body){
    int bw=540, bh=220, bx=(WIN_W-bw)/2, by=(WIN_H-bh)/2;
    setlinecolor(RGB(0,0,0)); setfillcolor(RGB(0,0,0));
    for(int yy=0;yy<WIN_H;yy+=3) line(0,yy,WIN_W,yy);
    fillRR(bx,by,bw,bh,12,C_PANEL_D,C_GOLD,2);
    dtC(bx+bw/2, by+40, title.c_str(), C_GOLD, 22, true);
    setlinecolor(C_GOLD); line(bx+20,by+65,bx+bw-20,by+65);
    dtC(bx+bw/2, by+bh/2-10, body.c_str(), C_TEXT, 18, false);
    Btn bYes(bx+60, by+bh-58, 160, 40, "锟斤拷 (锟斤拷锟斤拷)", 18);
    Btn bNo (bx+bw-220, by+bh-58, 160, 40, "锟斤拷 (锟斤拷锟斤拷)", 18);
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

// 通锟矫帮拷钮锟饺达拷锟斤拷锟斤拷锟诫背锟斤拷锟截绘函锟斤拷锟斤拷
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

// ===== 枚锟斤拷前锟斤拷锟斤拷锟斤拷锟斤拷锟斤拷锟斤拷锟斤拷锟斤拷染使锟矫ｏ拷=====
enum Suit  { SPADE=0, HEART, CLUB, DIAMOND, JOKER_SUIT };
enum Rank  {
    RANK_A=1,RANK_2,RANK_3,RANK_4,RANK_5,RANK_6,
    RANK_7,RANK_8,RANK_9,RANK_10,RANK_J,RANK_Q,RANK_K,
    RANK_SMALL_JOKER=100, RANK_BIG_JOKER=101
};
enum GameRule { BIG_WINS, SMALL_WINS };

// ===== 锟斤拷色锟斤拷锟轿伙拷锟斤拷 =====
void drawSuit(int cx,int cy,int r,Suit s){
    if(s==SPADE||s==CLUB) setfillcolor(C_BLK_S);
    else                   setfillcolor(C_RED_S);
    setlinecolor(RGB(0,0,0));
    switch(s){
        case SPADE:{
            // 锟斤拷锟藉：锟斤拷锟斤拷锟斤拷 + 锟斤拷锟斤拷圆锟斤拷
            int rr=(int)(r*0.48);
            fillcircle(cx-(int)(r*0.38),cy-(int)(r*0.05),rr);
            fillcircle(cx+(int)(r*0.38),cy-(int)(r*0.05),rr);
            POINT body[3]={{cx,cy-r},{cx+r,cy+(int)(r*0.4)},{cx-r,cy+(int)(r*0.4)}};
            fillpolygon(body,3);
            // 锟斤拷
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

// ===== 锟斤拷锟斤拷锟街凤拷锟斤拷 =====
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
        case RANK_SMALL_JOKER: return "小锟斤拷";
        case RANK_BIG_JOKER:   return "锟斤拷锟斤拷";
        default: return "?";
    }
}

// ===== 锟斤拷锟斤拷锟斤拷锟斤拷锟斤拷 =====
void drawCardFace(int x,int y,int w,int h,Suit s,Rank r,bool isJoker,bool selected=false,bool returned=false){
    // 选锟叫革拷锟斤拷锟斤拷锟?
    if(selected){
        fillRR(x-4,y-4,w+8,h+8,12,C_SEL,C_SEL,3);
    }
    // 锟斤拷锟斤拷锟缴?
    COLORREF cardBg = C_CARD_W;
    fillRR(x,y,w,h,8,cardBg,selected?C_SEL:RGB(190,185,178),selected?2:1);

    if(isJoker){
        COLORREF jc=(r==RANK_BIG_JOKER)?C_JOKER_R:C_JOKER_B;
        COLORREF jc2=(r==RANK_BIG_JOKER)?RGB(255,180,0):RGB(120,120,240);
        dtC(x+w/2,y+h/2-12,rankStr(r),jc,19,true);
        // 小装锟斤拷
        setfillcolor(jc2); setlinecolor(jc2);
        fillcircle(x+12,y+12,5); fillcircle(x+w-12,y+h-12,5);
        return;
    }
    COLORREF suitC=(s==HEART||s==DIAMOND)?C_RED_S:C_BLK_S;
    // 锟斤拷锟较角碉拷锟斤拷
    dtL(x+5,y+4, rankStr(r), suitC, 15, true);
    // 锟斤拷锟诫花色
    drawSuit(x+w/2,y+h/2, w/5, s);
    // 锟斤拷锟铰角碉拷锟斤拷锟斤拷小锟斤拷
    dtR(x+w-5,y+h-20, rankStr(r), suitC, 13, false);
    // 锟秸回憋拷锟?
    if(returned){
        setlinecolor(C_WARN);
        setlinestyle(PS_DOT,1);
        roundrect(x+2,y+2,x+w-2,y+h-2,6,6);
        dtC(x+w-10,y+10,"*",C_WARN,11,true);
    }
}

// ===== 锟斤拷锟斤拷锟狡憋拷 =====
void drawCardBack(int x,int y,int w,int h){
    fillRR(x,y,w,h,8,C_CARD_B,RGB(20,45,100),2);
    // 锟节诧拷锟斤拷锟轿伙拷锟斤拷
    int inset=8;
    COLORREF pat=RGB(45,85,175);
    setlinecolor(pat);
    setlinestyle(PS_SOLID,1);
    line(x+inset,y+h/2, x+w/2,y+inset);
    line(x+w/2,y+inset, x+w-inset,y+h/2);
    line(x+w-inset,y+h/2, x+w/2,y+h-inset);
    line(x+w/2,y+h-inset, x+inset,y+h/2);
}

// ===== Card前锟矫ｏ拷锟斤拷锟斤拷锟狡猴拷锟斤拷锟矫ｏ拷=====
struct Card;
void drawCard(int x,int y,int w,int h,const Card& c,bool faceUp,bool selected=false);

// ===== Card 锟斤拷 =====
struct Card {
    Suit suit;
    Rank rank;
    bool isJoker;
    bool isReturned; // 锟斤拷5锟斤拷锟斤拷锟秸回ｏ拷锟铰回合达拷锟斤拷锟斤拷锟斤拷锟斤拷锟剿?

    Card():suit(SPADE),rank(RANK_A),isJoker(false),isReturned(false){}
    Card(Suit s,Rank r,bool joker=false)
        :suit(s),rank(r),isJoker(joker),isReturned(false){}

    int getCompareValue(GameRule rule) const {
        if(isJoker) return (rank==RANK_BIG_JOKER)?2000:1900;
        int v=static_cast<int>(rank);
        if(rule==BIG_WINS){
            // A锟斤拷小K锟斤拷锟?
            if(rank==RANK_A) return 1;
            return v;
        } else {
            // SMALL_WINS: A锟斤拷锟斤拷(锟斤拷小锟饺斤拷值)锟斤拷K锟斤拷锟?锟斤拷锟?
            if(rank==RANK_A) return 1;
            return v;
        }
    }
    // 锟斤拷锟斤拷锟斤拷锟斤拷锟斤拷锟?
    void draw(int x,int y,bool selected=false) const {
        drawCardFace(x,y,CARD_W,CARD_H,suit,rank,isJoker,selected,isReturned);
    }
    void drawBack(int x,int y) const {
        drawCardBack(x,y,CARD_W,CARD_H);
    }
};

// Card::draw 实锟街诧拷锟斤拷锟斤拷锟斤拷为Card锟斤拷锟斤拷锟斤拷drawCardFace之锟斤拷直锟接碉拷锟矫硷拷锟缴ｏ拷
void drawCard(int x,int y,int w,int h,const Card& c,bool faceUp,bool selected){
    if(faceUp) drawCardFace(x,y,w,h,c.suit,c.rank,c.isJoker,selected,c.isReturned);
    else       drawCardBack(x,y,w,h);
}

// ===== Player 锟斤拷 =====
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
    // 锟揭碉拷锟斤拷锟斤拷一锟斤拷5锟斤拷锟脚筹拷 excludeIdx锟斤拷锟斤拷锟斤拷锟斤拷锟斤拷锟斤拷锟斤拷-1
    int findFiveCard(int excludeIdx=-1) const {
        for(int i=0;i<(int)hand.size();++i){
            if(i==excludeIdx) continue;
            if(!hand[i].isJoker && hand[i].rank==RANK_5) return i;
        }
        return -1;
    }
};

// ===== GameEngine 锟斤拷锟斤拷锟斤拷 =====
class GameEngine {
public:
    Player players[3];
    vector<Card> deck;
    int round;
    GameRule currentRule;
    int gameMode;       // 0=锟斤拷锟斤拷 1=锟斤拷锟斤拷
    int targetScore;
    bool consecutiveGame;
    int sceneCount;
    bool lastRoundTwoWayTie;

    // 5锟斤拷锟狡达拷锟介还
    bool fiveReturnPending[3];
    Card fiveReturnCard[3];

    // 锟斤拷锟斤拷锟斤拷锟斤拷锟狡ｏ拷锟斤拷锟斤拷染使锟矫ｏ拷
    vector<Card> tableCards;
    vector<int>  playedIdx;
    bool         tableRevealed;

    // 锟斤拷息锟斤拷志锟斤拷锟斤拷示锟斤拷锟斤拷锟斤拷锟斤拷锟斤拷
    vector<string> msgLog;

    mt19937 rng;

    GameEngine();

    // ===== 锟斤拷戏锟竭硷拷 =====
    void initDeck();
    void shuffleDeck();
    void dealCards(int n=18);
    vector<int> computeScores(const vector<Card>& cards);
    bool isThreeConsecutive(const vector<Card>& cards, const vector<bool>& skip);
    void applyBonusScore();
    void handleRuleFlip(const vector<Card>& cards);

    // AI
    int aiBlindChoice(int maxIdx);
    int strategicChoice(const Player& p);
    void strategicDiscard(Player& p, int count);

    // 锟斤拷锟斤拷锟斤拷锟?
    void processFiveReturns();
    bool check5CardActivation(int pIdx, int playedIdx, const vector<Card>& table);
    void perform5CardActivations(const vector<Card>& table,
        const vector<int>& pIdx, vector<bool>& activated);
    void perform10Mechanism(int tenPlayer);
    void performDrawSequence();
    int  performBigJokerDefense(int targetPlayer, int chosen);
    void performSmallJokerPeek(int fromPlayer, int targetPlayer);

    // 锟斤拷戏锟斤拷锟斤拷
    void playRound();
    void playTiebreaker(vector<int>& tied);
    bool checkEndCondition(vector<int>& tied);
    void startNewGame();

    // ===== GUI锟斤拷染 =====
    void renderGameScreen();
    void renderInfoBar();
    void renderAIArea(int pidx, int x, int y, int w, int h);
    void renderTableArea();
    void renderHumanHand(int selIdx=-1);
    void renderActionBtns(vector<Btn>& btns);
    void addMsg(const string& s);

    // ===== GUI锟斤拷锟斤拷 =====
    int  guiSelectCard(int playerIdx, const string& prompt);
    int  guiBlindSelect(int playerIdx, const string& prompt, int maxN);
    void guiInfo(const string& title, const string& body);
    bool guiYesNo(const string& title, const string& body);
    vector<int> guiSelectTwo(int playerIdx, const string& prompt);

    // ===== 锟剿碉拷 =====
    void showMainMenu();
    void showRulesScreen();
    int  showModeSelect();
    void showFinalRank();
};

// 全锟斤拷锟斤拷戏锟斤拷锟斤拷指锟诫（锟斤拷锟斤拷锟斤拷幕锟斤拷锟斤拷锟斤拷锟绞ｏ拷
GameEngine* g_eng = nullptr;

// ===== 锟斤拷锟斤拷 + 锟斤拷始锟斤拷 =====
GameEngine::GameEngine()
    :round(1),currentRule(BIG_WINS),gameMode(0),targetScore(60),
     consecutiveGame(false),sceneCount(1),lastRoundTwoWayTie(false),
     tableRevealed(false)
{
    unsigned seed=(unsigned)chrono::steady_clock::now().time_since_epoch().count();
    rng.seed(seed);
    for(int i=0;i<3;++i){ fiveReturnPending[i]=false; }
    // 锟斤拷锟?锟斤拷锟斤拷锟斤拷
    players[0].name="锟斤拷";       players[0].isHuman=true;  players[0].isStrategic=false;
    players[1].name="锟斤拷锟?(AI)"; players[1].isHuman=false; players[1].isStrategic=true;
    players[2].name="锟斤拷锟?(AI)"; players[2].isHuman=false; players[2].isStrategic=true;
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

// ===== 锟狡凤拷 =====
vector<int> GameEngine::computeScores(const vector<Card>& cards){
    vector<int> scores(3,0);
    int v[3]; for(int i=0;i<3;++i) v[i]=cards[i].getCompareValue(currentRule);
    int ord[3]={0,1,2};
    sort(ord,ord+3,[&](int a,int b){
        return currentRule==BIG_WINS ? v[a]>v[b] : v[a]<v[b];
    });
    if(v[0]==v[1]&&v[1]==v[2]) return scores; // 锟斤拷锟斤拷全同
    if(v[ord[0]]==v[ord[1]]){
        scores[ord[0]]=1; scores[ord[1]]=1;
    } else if(v[ord[1]]==v[ord[2]]){
        scores[ord[0]]=2;
    } else {
        scores[ord[0]]=2; scores[ord[1]]=1;
    }
    return scores;
}

// ===== 锟斤拷顺锟叫讹拷 =====
bool GameEngine::isThreeConsecutive(const vector<Card>& cards, const vector<bool>& skip){
    for(int i=0;i<3;++i) if(cards[i].isJoker) return false;
    for(int i=0;i<3;++i) if(skip[i]) return false;
    vector<int> nums;
    for(int i=0;i<3;++i) nums.push_back(static_cast<int>(cards[i].rank));
    sort(nums.begin(),nums.end());
    return (nums[1]==nums[0]+1 && nums[2]==nums[1]+1);
}

// ===== 小锟斤拷锟绞讹拷态锟斤拷锟斤拷 =====
void GameEngine::applyBonusScore(){
    // 约12%锟斤拷锟绞达拷锟斤拷
    if((int)(rng()%100)<12){
        int lucky=(int)(rng()%3);
        players[lucky].score++;
        addMsg("[锟斤拷态锟斤拷锟斤拷] "+players[lucky].name+" 锟斤拷锟斤拷锟斤拷+1锟街斤拷锟斤拷锟斤拷");
        // 锟接撅拷锟斤拷示
        BeginBatchDraw();
        renderGameScreen();
        dtC(WIN_W/2,WIN_H/2-60,"[锟斤拷态锟斤拷锟斤拷] 锟斤拷锟?1锟街ｏ拷",C_GOLD,26,true);
        EndBatchDraw();
        Sleep(1200);
    }
}

// ===== 锟斤拷锟斤拷转 =====
void GameEngine::handleRuleFlip(const vector<Card>& cards){
    // 锟斤拷锟斤拷全同锟斤拷锟斤拷锟斤拷锟阶拷锟斤拷
    int v[3]; for(int i=0;i<3;++i) v[i]=cards[i].getCompareValue(currentRule);
    if(v[0]==v[1]&&v[1]==v[2]){ lastRoundTwoWayTie=false; return; }
    // 锟斤拷锟斤拷锟斤拷同锟斤拷锟揭凤拷全同锟斤拷锟斤拷锟斤拷录/锟斤拷转
    int cnt=0;
    if(v[0]==v[1]||v[1]==v[2]||v[0]==v[2]) cnt=2;
    if(cnt==2){
        if(lastRoundTwoWayTie){
            // 锟斤拷锟斤拷锟斤拷锟斤拷锟斤拷锟斤拷同 锟斤拷 锟斤拷锟斤拷转锟斤拷小锟斤拷锟斤拷
            if((int)(rng()%100)<35){
                currentRule=(currentRule==BIG_WINS)?SMALL_WINS:BIG_WINS;
                addMsg("[锟斤拷锟斤拷转] 锟斤拷锟斤拷锟斤拷锟斤拷锟斤拷锟斤拷同锟斤拷锟斤拷锟斤拷锟轿?+
                    string(currentRule==BIG_WINS?"锟饺达拷":"锟斤拷小")+"锟斤拷");
                BeginBatchDraw();
                renderGameScreen();
                dtC(WIN_W/2,WIN_H/2-60,
                    (currentRule==BIG_WINS?"[锟斤拷锟斤拷转] 锟斤拷锟节比达拷":"[锟斤拷锟斤拷转] 锟斤拷锟节憋拷小锟斤拷"),
                    C_WARN,26,true);
                EndBatchDraw();
                Sleep(1500);
            }
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
int GameEngine::strategicChoice(const Player& p){
    if(p.hand.empty()) return 0;
    if((int)(rng()%100)<15) return rng()%p.hand.size();
    // 锟斤拷锟教匡拷锟角筹拷10
    for(int i=0;i<(int)p.hand.size();++i)
        if(!p.hand[i].isJoker && p.hand[i].rank==RANK_10)
            if(round>=4&&round<=14&&(int)(rng()%100)<45) return i;
    vector<pair<int,int>> iv;
    for(int i=0;i<(int)p.hand.size();++i)
        iv.push_back({p.hand[i].getCompareValue(currentRule),i});
    sort(iv.begin(),iv.end());
    int n=(int)p.hand.size();
    if(currentRule==BIG_WINS){
        int topRange=(round<=6)?max(1,n*2/5):(round<=12)?max(1,n/3):max(1,n/5);
        int pos=n-1-(int)(rng()%topRange);
        return iv[max(0,pos)].second;
    } else {
        if((int)(rng()%100)<70) return iv[0].second;
        return iv[(int)(rng()%max(1,n/4))].second;
    }
}
void GameEngine::strategicDiscard(Player& p, int count){
    for(int k=0;k<count&&!p.hand.empty();++k){
        int wi=0; int wv=p.hand[0].getCompareValue(currentRule);
        bool bigHand=(int)p.hand.size()>4;
        for(int i=1;i<(int)p.hand.size();++i){
            int v=p.hand[i].getCompareValue(currentRule);
            if((currentRule==BIG_WINS&&v<wv)||(currentRule==SMALL_WINS&&v>wv)){ wv=v; wi=i; }
        }
        if(bigHand && p.hand[wi].rank==RANK_10 && !p.hand[wi].isJoker){
            int wi2=-1; int wv2=INT_MAX;
            for(int i=0;i<(int)p.hand.size();++i){
                if(i==wi) continue;
                int v=p.hand[i].getCompareValue(currentRule);
                if(wi2<0||(currentRule==BIG_WINS&&v<wv2)||(currentRule==SMALL_WINS&&v>wv2)){ wv2=v; wi2=i; }
            }
            if(wi2>=0) wi=wi2;
        }
        p.hand.erase(p.hand.begin()+wi);
    }
}

// ===== 锟斤拷染锟斤拷锟斤拷锟斤拷锟斤拷息锟斤拷 =====
void GameEngine::renderInfoBar(){
    fillArea(0,0,WIN_W,BAR_H,C_PANEL_D,C_GOLD,0);
    // 锟斤拷N锟斤拷
    char buf[64];
    sprintf(buf,"锟斤拷 %d / 18 锟斤拷",round);
    dtL(14,14,buf,C_GOLD,22,true);
    // 锟斤拷锟斤拷
    const char* ruleStr=(currentRule==BIG_WINS)?"锟饺达拷 (K锟斤拷强)":"锟斤拷小 (A锟斤拷锟斤拷)";
    COLORREF rc=(currentRule==BIG_WINS)?C_RED_T:C_GREEN_T;
    dtC(WIN_W/2,BAR_H/2,ruleStr,rc,20,true);
    // 锟斤拷锟街ｏ拷锟揭诧拷锟斤拷锟剿ｏ拷
    int sx=WIN_W-420;
    for(int i=0;i<3;++i){
        char sb[32]; sprintf(sb,"%s:%d",players[i].name.c_str(),players[i].score);
        COLORREF sc=(i==0)?C_BLUE_T:(i==1)?C_WARN:C_SILVER;
        dtL(sx+i*140,14,sb,sc,18,i==0);
    }
    // 锟街革拷锟斤拷
    setlinecolor(C_GOLD); setlinestyle(PS_SOLID,1);
    line(0,BAR_H-1,WIN_W,BAR_H-1);
}

// ===== 锟斤拷染锟斤拷AI锟斤拷锟斤拷锟斤拷 =====
void GameEngine::renderAIArea(int pidx,int x,int y,int w,int h){
    fillArea(x,y,w,h,C_PANEL,RGB(50,80,50));
    // 锟斤拷锟斤拷锟?
    COLORREF nc=(pidx==1)?C_WARN:C_SILVER;
    dtL(x+10,y+6,players[pidx].name.c_str(),nc,16,true);
    char sb[16]; sprintf(sb,"(%d锟斤拷)",(int)players[pidx].hand.size());
    dtL(x+10+textwidth(players[pidx].name.c_str())+4,y+8,sb,C_DIM,14,false);
    // 锟狡憋拷锟斤拷锟斤拷锟斤拷锟斤拷锟叫ｏ拷锟斤拷锟斤拷锟绞?8锟脚ｏ拷
    int n=(int)players[pidx].hand.size();
    if(n==0){ dtC(x+w/2,y+h/2,"锟斤拷锟斤拷锟斤拷锟斤拷锟狡ｏ拷",C_DIM,15,false); return; }
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

// ===== 锟斤拷染锟斤拷锟斤拷锟斤拷锟斤拷锟斤拷 =====
void GameEngine::renderTableArea(){
    fillArea(TBL_X,TBL_Y,TBL_W,TBL_H,C_TABLE_D,RGB(10,60,30),4);
    // 锟叫硷拷锟斤拷锟斤拷锟斤拷示锟斤拷锟街达拷锟斤拷锟斤拷锟?
    if(tableRevealed && (int)tableCards.size()==3){
        int spacing=CARD_W+24;
        int totalW=3*spacing-24;
        int startX=TBL_X+(TBL_W-totalW)/2;
        int cardY=TBL_Y+(TBL_H-CARD_H)/2-10;
        for(int i=0;i<3;++i){
            drawCard(startX+i*spacing,cardY,CARD_W,CARD_H,tableCards[i],true,false);
            // 锟斤拷锟斤拷锟斤拷锟角?
            dtC(startX+i*spacing+CARD_W/2, cardY+CARD_H+14,
                players[i].name.c_str(),
                (i==0)?C_BLUE_T:(i==1)?C_WARN:C_SILVER, 14, true);
        }
    } else {
        dtC(TBL_X+TBL_W/2, TBL_Y+TBL_H/2-16, "[ 锟饺达拷锟斤拷锟斤拷... ]", C_DIM, 18, false);
    }
    // 锟斤拷息锟斤拷志锟斤拷锟揭侧）
    int logX=TBL_X+TBL_W-380, logY=TBL_Y+10;
    fillArea(logX,logY,370,TBL_H-20,C_PANEL,RGB(30,60,30),4);
    dtL(logX+8,logY+6,"  锟斤拷戏锟斤拷志",C_GOLD,14,true);
    setlinecolor(RGB(40,80,40)); line(logX+6,logY+26,logX+364,logY+26);
    int ly=logY+32;
    for(int i=0;i<(int)msgLog.size();++i){
        // 锟截断筹拷锟斤拷锟斤拷息
        string m=msgLog[i];
        if((int)m.size()>22) m=m.substr(0,22)+"...";
        COLORREF mc=(i==(int)msgLog.size()-1)?C_WHITE:C_DIM;
        dtL(logX+8,ly+i*24,m.c_str(),mc,13,i==(int)msgLog.size()-1);
    }
}

// ===== 锟斤拷染锟斤拷锟斤拷锟斤拷锟斤拷锟斤拷 =====
void GameEngine::renderHumanHand(int selIdx){
    fillArea(HND_X,HND_Y,HND_W,HND_H,C_PANEL,RGB(50,90,55),6);
    dtL(HND_X+10,HND_Y+6,"锟斤拷锟斤拷锟斤拷锟?,C_BLUE_T,15,true);
    int n=(int)players[0].hand.size();
    if(n==0){ dtC(HND_X+HND_W/2,HND_Y+HND_H/2,"锟斤拷锟斤拷锟斤拷锟窖空ｏ拷",C_DIM,16,false); return; }
    // 锟斤拷锟斤拷应锟斤拷锟斤拷
    int maxCards=min(n,13);
    int overlap=max(CARD_W+6, (HND_W-20) / max(1,maxCards));
    overlap=min(overlap, CARD_W+10);
    int totalW=(n-1)*overlap+CARD_W;
    int startX=HND_X+(HND_W-min(totalW,HND_W-20))/2;
    int cardY=HND_Y+26;
    // 锟斤拷选锟叫碉拷锟斤拷锟斤拷锟斤拷
    for(int i=0;i<n;++i){
        bool sel=(i==selIdx);
        int cx2=startX+i*min(overlap,(HND_W-20-CARD_W)/max(1,n-1));
        int cy2=cardY+(sel?-12:0);
        drawCard(cx2,cy2,CARD_W,CARD_H-10,players[0].hand[i],true,sel);
    }
}

// ===== 锟斤拷染锟斤拷锟斤拷锟斤拷锟斤拷钮锟斤拷 =====
void GameEngine::renderActionBtns(vector<Btn>& btns){
    fillArea(ACT_X,ACT_Y,ACT_W,ACT_H,C_PANEL_D,RGB(30,60,30),6);
    // 锟斤拷钮锟缴碉拷锟斤拷锟竭革拷锟斤拷锟斤拷锟?
}

// ===== 全锟斤拷锟斤拷染 =====
void GameEngine::renderGameScreen(){
    // 锟斤拷锟斤拷
    setfillcolor(C_TABLE);
    setlinecolor(C_TABLE);
    fillrectangle(0,0,WIN_W,WIN_H);
    renderInfoBar();
    renderAIArea(1,AI1_X,AI1_Y,AI1_W,AI1_H);
    renderAIArea(2,AI2_X,AI2_Y,AI2_W,AI2_H);
    renderTableArea();
    renderHumanHand();
}

// ===== GUI: 选锟斤拷锟斤拷锟斤拷一锟斤拷锟斤拷 =====
int GameEngine::guiSelectCard(int pidx, const string& prompt){
    int sel=-1;
    int mx=0,my=0;
    Player& p=players[pidx];
    int n=(int)p.hand.size();
    if(n==0) return -1;
    int overlap=min(CARD_W+10, (HND_W-20)/max(1,n));
    int totalW=(n-1)*overlap+CARD_W;
    int startX=HND_X+(HND_W-min(totalW,HND_W-20))/2;
    int cardY=HND_Y+26;

    Btn bConfirm(ACT_X+8,ACT_Y+10,ACT_W-16,44,"确锟斤拷",18,false);
    Btn bCancel (ACT_X+8,ACT_Y+60,ACT_W-16,44,"取锟斤拷",18);
    vector<Btn> btns={bConfirm,bCancel};

    while(true){
        BeginBatchDraw();
        renderGameScreen();
        // 锟斤拷锟斤拷锟斤拷锟斤拷锟斤拷锟斤拷锟斤拷选锟斤拷效锟斤拷锟斤拷
        fillArea(HND_X,HND_Y,HND_W,HND_H,C_PANEL,RGB(50,90,55),6);
        dtL(HND_X+10,HND_Y+6,"锟斤拷锟斤拷锟斤拷锟?,C_BLUE_T,15,true);
        for(int i=0;i<n;++i){
            bool s=(i==sel);
            int cx2=startX+i*min(overlap,(HND_W-20-CARD_W)/max(1,n-1));
            int cy2=cardY+(s?-12:0);
            drawCard(cx2,cy2,CARD_W,CARD_H-10,p.hand[i],true,s);
        }
        // 锟斤拷示锟斤拷锟斤拷
        dtC(HND_X+HND_W/2,HND_Y+HND_H-18,prompt.c_str(),C_GOLD,15,true);
        // 锟斤拷锟斤拷锟斤拷钮
        fillArea(ACT_X,ACT_Y,ACT_W,ACT_H,C_PANEL_D,RGB(30,60,30),6);
        btns[0].enabled=(sel>=0);
        for(auto& b:btns) b.draw(b.hit(mx,my));
        EndBatchDraw();

        ExMessage msg;
        while(peekmessage(&msg,EX_MOUSE)){
            mx=msg.x; my=msg.y;
            if(msg.message==WM_LBUTTONUP){
                // 锟斤拷锟斤拷频锟斤拷
                for(int i=0;i<n;++i){
                    int cx2=startX+i*min(overlap,(HND_W-20-CARD_W)/max(1,n-1));
                    int cy2=cardY;
                    if(mx>=cx2&&mx<=cx2+CARD_W&&my>=cy2-14&&my<=cy2+CARD_H)
                        sel=(sel==i)?-1:i;
                }
                if(btns[0].hit(mx,my) && sel>=0) return sel;
                if(btns[1].hit(mx,my)) return -1;
            }
        }
        Sleep(16);
    }
}

// ===== GUI: 盲选1~N锟斤拷一锟斤拷锟斤拷锟?=====
int GameEngine::guiBlindSelect(int pidx, const string& prompt, int maxN){
    // 锟斤拷示 maxN 锟斤拷锟狡憋拷锟斤拷锟斤拷锟斤拷业锟斤拷锟斤拷锟斤拷一锟斤拷
    int sel=-1;
    int mx=0,my=0;
    int spacing=min(CARD_W+16,(TBL_W-100)/max(1,maxN));
    int totalW=(maxN-1)*spacing+CARD_W;
    int startX=TBL_X+(TBL_W-min(totalW,TBL_W-100))/2;
    int cardY=TBL_Y+(TBL_H-CARD_H)/2;

    Btn bConfirm(ACT_X+8,ACT_Y+10,ACT_W-16,44,"确锟斤拷",18,false);
    vector<Btn> btns={bConfirm};

    while(true){
        BeginBatchDraw();
        renderGameScreen();
        // 锟斤拷锟斤拷锟斤拷锟斤拷锟斤拷锟斤拷示锟狡憋拷
        fillArea(TBL_X,TBL_Y,TBL_W,TBL_H,C_TABLE_D,RGB(10,60,30),4);
        dtC(TBL_X+TBL_W/2-200,TBL_Y+18,prompt.c_str(),C_GOLD,16,true);
        for(int i=0;i<maxN;++i){
            int cx2=startX+i*min(spacing,(TBL_W-100-CARD_W)/max(1,maxN-1));
            bool s=(i==sel);
            if(s){ fillRR(cx2-4,cardY-4,CARD_W+8,CARD_H+8,12,C_SEL,C_SEL,3); }
            drawCardBack(cx2,cardY,CARD_W,CARD_H);
            char num[4]; sprintf(num,"%d",i+1);
            dtC(cx2+CARD_W/2,cardY+CARD_H+14,num,s?C_GOLD:C_DIM,14,s);
        }
        fillArea(ACT_X,ACT_Y,ACT_W,ACT_H,C_PANEL_D,RGB(30,60,30),6);
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

// guiInfo / guiYesNo 锟斤拷装
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

// ===== 锟斤拷锟斤拷锟斤拷疲锟?锟斤拷锟狡归还 =====
void GameEngine::processFiveReturns(){
    for(int i=0;i<3;++i){
        if(fiveReturnPending[i]){
            Card rc=fiveReturnCard[i]; rc.isReturned=true;
            players[i].addCard(rc);
            fiveReturnPending[i]=false;
            addMsg("[5锟斤拷锟斤拷] "+players[i].name+" 锟秸伙拷锟斤拷锟较回合碉拷锟斤拷(*)");
        }
    }
}

// ===== 锟斤拷锟?锟斤拷锟狡硷拷锟斤拷锟斤拷锟斤拷 =====
bool GameEngine::check5CardActivation(int pIdx,int pIdx2,const vector<Card>& table){
    int v[3]; for(int i=0;i<3;++i) v[i]=table[i].getCompareValue(currentRule);
    if(v[0]==v[1]||v[1]==v[2]||v[0]==v[2]) return false;
    int myV=v[pIdx];
    int best=(currentRule==BIG_WINS)?*max_element(v,v+3):*min_element(v,v+3);
    if(myV==best) return false;
    if(players[pIdx].findFiveCard(pIdx2)<0) return false;
    return true;
}

// ===== 5锟斤拷锟狡硷拷锟筋（锟斤拷GUI锟斤拷=====
void GameEngine::perform5CardActivations(const vector<Card>& table,
    const vector<int>& pIdx, vector<bool>& activated){
    activated.assign(3,false);
    for(int i=0;i<3;++i){
        if(!check5CardActivation(i,pIdx[i],table)) continue;
        bool doIt=false;
        if(players[i].isHuman){
            char body[128];
            sprintf(body,"锟斤拷锟斤拷锟斤拷锟狡诧拷锟斤拷锟斤拷锟脚ｏ拷锟斤拷锟斤拷锟叫伙拷锟斤拷5锟斤拷锟矫★拷\n锟斤拷锟斤拷一锟斤拷5锟斤拷锟斤拷锟斤拷锟街筹拷锟斤拷锟斤拷锟秸回ｏ拷");
            doIt=guiYesNo("[5锟斤拷锟斤拷] 锟斤拷锟筋？",body);
        } else {
            // AI锟斤拷锟斤拷锟斤拷锟斤拷锟斤拷锟揭伙拷锟斤拷锟街碉拷偶锟斤拷锟?
            int myV=table[i].getCompareValue(currentRule);
            int vals[3]; for(int j=0;j<3;++j) vals[j]=table[j].getCompareValue(currentRule);
            sort(vals,vals+3);
            doIt=(currentRule==BIG_WINS)?(myV>=vals[1]):(myV<=vals[1]);
        }
        if(doIt){
            int fi=players[i].findFiveCard(pIdx[i]);
            players[i].removeCard(fi);
            fiveReturnPending[i]=true;
            fiveReturnCard[i]=table[i];
            activated[i]=true;
            addMsg("[5锟斤拷锟斤拷] "+players[i].name+" 锟斤拷锟筋！锟铰撅拷锟秸回筹拷锟斤拷锟斤拷");
        }
    }
}

// ===== 锟斤拷10锟斤拷锟狡ｏ拷锟斤拷GUI锟斤拷=====
void GameEngine::perform10Mechanism(int tenPlayer){
    addMsg("[顺锟斤拷牵锟斤拷] "+players[tenPlayer].name+" 锟斤拷锟斤拷10锟斤拷");
    BeginBatchDraw();
    renderGameScreen();
    char title[64]; sprintf(title,"[顺锟斤拷牵锟斤拷] %s 锟斤拷锟斤拷10锟斤拷",players[tenPlayer].name.c_str());
    showMsgBox(title,"锟斤拷锟斤拷锟斤拷锟斤拷锟剿筹拷锟斤拷锟狡ｏ拷然锟斤拷锟斤拷锟斤拷1锟脚ｏ拷锟铰硷拷锟斤拷盲锟斤拷1锟脚★拷");
    EndBatchDraw();

    // 锟斤拷锟斤拷锟斤拷锟斤拷锟剿碉拷锟斤拷
    for(int i=0;i<3;++i) if(i!=tenPlayer) players[tenPlayer].addCard(tableCards[i]);
    players[tenPlayer].removeSpecificCard(tableCards[tenPlayer]);

    // 锟斤拷锟斤拷1锟脚ｏ拷锟斤拷锟皆硷拷知锟斤拷
    if(players[tenPlayer].isHuman){
        int di=guiSelectCard(tenPlayer,"[锟斤拷锟斤拷] 锟斤拷选锟斤拷要锟斤拷锟斤拷锟斤拷1锟斤拷锟狡ｏ拷锟斤拷锟斤拷杉锟斤拷锟?);
        if(di>=0){ players[tenPlayer].removeCard(di); addMsg("[锟斤拷10] 锟斤拷锟斤拷锟斤拷锟斤拷锟斤拷1锟斤拷"); }
    } else {
        strategicDiscard(players[tenPlayer],1);
        addMsg("[锟斤拷10] "+players[tenPlayer].name+" 锟斤拷锟斤拷1锟脚ｏ拷未锟斤拷锟斤拷锟斤拷");
    }
    BeginBatchDraw(); renderGameScreen(); EndBatchDraw();
    Sleep(400);

    // 锟铰硷拷盲锟斤拷1锟脚ｏ拷锟斤拷锟斤拷展示锟斤拷
    int nextP=(tenPlayer+1)%3;
    int chosen;
    char pr[64]; sprintf(pr,"[盲锟斤拷] 锟斤拷 %s 锟斤拷%d锟斤拷锟斤拷锟斤拷选一锟斤拷锟?,
        players[tenPlayer].name.c_str(),(int)players[tenPlayer].hand.size());
    if(players[nextP].isHuman){
        chosen=guiBlindSelect(nextP,pr,(int)players[tenPlayer].hand.size());
    } else {
        chosen=aiBlindChoice((int)players[tenPlayer].hand.size());
    }
    chosen=performBigJokerDefense(tenPlayer,chosen);
    // 锟斤拷锟斤拷展示锟斤拷锟斤拷锟斤拷锟斤拷
    Card shown=players[tenPlayer].hand[chosen];
    players[tenPlayer].removeCard(chosen);
    char info[64]; sprintf(info,"%s 选锟斤拷锟剿革拷锟狡诧拷锟斤拷锟斤拷锟斤拷锟斤拷锟斤拷",players[nextP].name.c_str());
    BeginBatchDraw();
    renderGameScreen();
    // 锟斤拷锟斤拷展示
    int sx=WIN_W/2-CARD_W/2, sy=WIN_H/2-CARD_H/2;
    drawCard(sx,sy,CARD_W,CARD_H,shown,true,false);
    dtC(WIN_W/2,sy+CARD_H+24,info,C_WARN,18,true);
    dtC(WIN_W/2,sy+CARD_H+52,"[ 锟斤拷锟斤拷锟斤拷锟?]",C_DIM,14,false);
    EndBatchDraw();
    ExMessage mm;
    while(true){
        if(peekmessage(&mm,EX_MOUSE)&&mm.message==WM_LBUTTONUP) break;
        Sleep(16);
    }
    addMsg("[锟斤拷10] "+players[nextP].name+" 锟斤拷锟斤拷锟斤拷锟斤拷 "+string(rankStr(shown.rank)));
}

// ===== 锟斤拷锟斤拷锟斤拷锟斤拷 =====
int GameEngine::performBigJokerDefense(int targetPlayer, int chosen){
    if(!players[targetPlayer].canUseBigJoker()) return chosen;
    int handSize=(int)players[targetPlayer].hand.size();
    if(handSize<=1) return chosen; // 只剩1锟脚ｏ拷偏锟斤拷锟斤拷锟斤拷锟斤拷
    bool doDefend;
    if(players[targetPlayer].isHuman){
        char body[128];
        sprintf(body,"锟皆凤拷选锟剿憋拷锟?%d锟斤拷\n锟斤拷锟斤拷写锟斤拷锟斤拷锟斤拷山锟窖★拷锟狡拷锟轿?%d锟斤拷锟斤拷锟斤拷%d/2锟轿ｏ拷",
            chosen+1, (chosen==0)?handSize:chosen, players[targetPlayer].bigJokerUses);
        doDefend=guiYesNo("[锟斤拷锟斤拷锟斤拷锟斤拷] 锟斤拷锟斤拷锟斤拷",body);
    } else {
        // AI锟斤拷锟斤拷50%锟斤拷锟斤拷使锟矫ｏ拷锟揭憋拷锟斤拷锟斤拷锟斤拷1锟轿革拷锟截硷拷时锟斤拷
        doDefend=(players[targetPlayer].bigJokerUses<1)&&((int)(rng()%100)<50);
    }
    if(doDefend){
        players[targetPlayer].bigJokerUses++;
        int newChosen=(chosen==0)?(handSize-1):(chosen-1);
        addMsg("[锟斤拷锟斤拷锟斤拷锟斤拷] "+players[targetPlayer].name+" 偏锟斤拷锟斤拷目锟疥！");
        BeginBatchDraw(); renderGameScreen();
        char info[64]; sprintf(info,"锟斤拷锟斤拷锟缴癸拷锟斤拷锟斤拷锟?%d -> %d",chosen+1,newChosen+1);
        showMsgBox("[锟斤拷锟斤拷锟斤拷锟斤拷锟斤拷]",info);
        EndBatchDraw();
        return newChosen;
    }
    return chosen;
}

// ===== 小锟斤拷偷锟斤拷 =====
void GameEngine::performSmallJokerPeek(int fromPlayer, int targetPlayer){
    if(!players[fromPlayer].canUseSmallJoker()) return;
    bool doPeek;
    if(players[fromPlayer].isHuman){
        char body[64];
        sprintf(body,"锟斤拷锟斤拷锟叫★拷锟斤拷锟斤拷锟酵碉拷锟?%s 锟斤拷锟斤拷锟狡ｏ拷每锟斤拷锟斤拷1锟轿ｏ拷",
            players[targetPlayer].name.c_str());
        doPeek=guiYesNo("[小锟斤拷偷锟斤拷] 锟斤拷锟斤拷锟斤拷",body);
    } else {
        doPeek=((int)(rng()%100)<60);
    }
    if(!doPeek) return;
    players[fromPlayer].smallJokerUses++;
    addMsg("[小锟斤拷偷锟斤拷] "+players[fromPlayer].name+" 偷锟斤拷锟斤拷 "+players[targetPlayer].name);
    if(players[fromPlayer].isHuman){
        // 展示目锟斤拷锟斤拷锟狡革拷锟斤拷锟斤拷锟斤拷铱锟?
        int n=(int)players[targetPlayer].hand.size();
        int spacing=min(CARD_W+10,(TBL_W-100)/max(1,n));
        int totalW=(n-1)*spacing+CARD_W;
        int startX=TBL_X+(TBL_W-min(totalW,TBL_W-80))/2;
        int cardY=TBL_Y+(TBL_H-CARD_H)/2;
        BeginBatchDraw();
        renderGameScreen();
        fillArea(TBL_X,TBL_Y,TBL_W,TBL_H,C_TABLE_D,RGB(10,60,30),4);
        char title[64]; sprintf(title,"[小锟斤拷偷锟斤拷] %s 锟斤拷锟斤拷锟狡ｏ拷锟斤拷锟斤拷杉锟斤拷锟?,
            players[targetPlayer].name.c_str());
        dtC(TBL_X+TBL_W/2-200,TBL_Y+16,title,C_GOLD,16,true);
        for(int i=0;i<n;++i){
            int cx2=startX+i*min(spacing,(TBL_W-80-CARD_W)/max(1,n-1));
            drawCard(cx2,cardY,CARD_W,CARD_H,players[targetPlayer].hand[i],true,false);
        }
        dtC(TBL_X+TBL_W/2-200,TBL_Y+TBL_H-24,"[ 锟斤拷锟斤拷锟斤拷锟斤拷锟紸I锟斤拷锟斤拷锟斤拷锟斤拷 ]",C_DIM,14,false);
        EndBatchDraw();
        ExMessage mm;
        while(true){ if(peekmessage(&mm,EX_MOUSE)&&mm.message==WM_LBUTTONUP) break; Sleep(16); }
    }
}

// ===== 锟斤拷顺锟斤拷锟斤拷 =====
void GameEngine::performDrawSequence(){
    addMsg("[锟斤拷顺锟斤拷锟斤拷] 锟斤拷锟斤拷锟斤拷锟斤拷锟斤拷锟斤拷锟斤拷锟铰硷拷盲锟斤拷1锟脚ｏ拷");
    BeginBatchDraw(); renderGameScreen();
    showMsgBox("[锟斤拷顺锟斤拷锟斤拷锟斤拷]","锟斤拷锟斤拷锟狡碉拷锟斤拷锟斤拷锟斤拷锟斤拷锟斤拷锟斤拷掖锟剿呈憋拷锟斤拷录锟斤拷锟斤拷锟矫わ拷锟?锟脚ｏ拷");
    EndBatchDraw();

    // 锟斤拷锟斤拷前锟斤拷锟斤拷锟缴高碉拷锟斤拷锟斤拷锟斤拷
    int order[3]={0,1,2};
    sort(order,order+3,[this](int a,int b){ return players[a].score>players[b].score; });

    vector<Card> drawn(3); vector<bool> hasDrawn(3,false);

    for(int k=0;k<3;++k){
        int from=order[k];
        int target=(from+1)%3;
        if(players[target].hand.empty()){
            addMsg(players[target].name+" 锟斤拷锟狡空ｏ拷锟斤拷锟斤拷");
            continue;
        }
        // 小锟斤拷偷锟斤拷锟斤拷锟斤拷
        performSmallJokerPeek(from,target);

        int chosen;
        int tSize=(int)players[target].hand.size();
        char pr[80]; sprintf(pr,"锟斤拷 %s 锟斤拷%d锟斤拷锟斤拷锟斤拷锟斤拷盲选1锟斤拷",players[target].name.c_str(),tSize);
        if(players[from].isHuman){
            chosen=guiBlindSelect(from,pr,tSize);
        } else {
            chosen=aiBlindChoice(tSize);
        }
        chosen=performBigJokerDefense(target,chosen);

        drawn[from]=players[target].hand[chosen];
        players[target].hand.erase(players[target].hand.begin()+chosen);
        hasDrawn[from]=true;

        // 锟缴硷拷锟皆ｏ拷锟斤拷取锟斤拷锟斤拷锟斤拷锟洁）锟斤拷锟斤拷锟皆硷拷锟介到锟斤拷什么
        if(players[from].isHuman){
            BeginBatchDraw();
            renderGameScreen();
            fillArea(TBL_X,TBL_Y,TBL_W,TBL_H,C_TABLE_D,RGB(10,60,30),4);
            dtC(TBL_X+TBL_W/2-200,TBL_Y+20,"[锟斤拷顺锟斤拷锟斤拷] 锟斤拷榈斤拷耍锟?,C_GOLD,18,true);
            int sx=TBL_X+TBL_W/2-200-CARD_W/2;
            drawCard(sx,TBL_Y+60,CARD_W,CARD_H,drawn[from],true,false);
            dtC(TBL_X+TBL_W/2-200,TBL_Y+TBL_H-24,"[ 锟斤拷锟斤拷锟斤拷锟斤拷锟斤拷锟斤拷锟缴硷拷锟斤拷 ]",C_DIM,14,false);
            EndBatchDraw();
            ExMessage mm;
            while(true){ if(peekmessage(&mm,EX_MOUSE)&&mm.message==WM_LBUTTONUP) break; Sleep(16); }
        } else {
            addMsg(players[from].name+" 锟斤拷 "+players[target].name+" 锟斤拷锟斤拷1锟斤拷");
            BeginBatchDraw(); renderGameScreen(); EndBatchDraw();
            Sleep(600);
        }
        // 锟斤拷锟介方锟斤拷锟斤拷锟洁）锟矫碉拷通知
        if(players[target].isHuman){
            char info[64]; sprintf(info,"锟斤拷锟?%s 锟斤拷 %s 锟斤拷锟斤拷锟剿ｏ拷",
                rankStr(drawn[from].rank),players[from].name.c_str());
            BeginBatchDraw(); renderGameScreen();
            showMsgBox("[锟斤拷顺锟斤拷锟斤拷] 锟斤拷锟斤拷票锟斤拷锟斤拷锟斤拷耍锟?,info);
            EndBatchDraw();
        }
    }
    for(int i=0;i<3;++i) if(hasDrawn[i]) players[i].addCard(drawn[i]);
    addMsg("[锟斤拷顺] 锟斤拷锟斤拷锟斤拷锟?);
}

// ===== 锟斤拷锟截合ｏ拷GUI锟芥）=====
void GameEngine::playRound(){
    msgLog.clear();
    tableCards.clear(); tableCards.resize(3);
    playedIdx.assign(3,-1);
    tableRevealed=false;

    // Step 0: 5锟斤拷锟狡归还
    processFiveReturns();

    // Step 1: 锟斤拷锟狡阶讹拷
    // AI锟饺筹拷锟斤拷锟斤拷默锟斤拷锟斤拷锟斤拷锟洁交锟斤拷锟斤拷
    vector<bool> hasCanceled(3,false);
    for(int i=1;i<3;++i){
        int c=strategicChoice(players[i]);
        playedIdx[i]=c;
        tableCards[i]=players[i].hand[c];
    }

    // 锟斤拷锟斤拷锟斤拷锟?
    int humanSel=-1;
    int mx=0,my=0;
    int n=(int)players[0].hand.size();
    int overlap=min(CARD_W+10,(HND_W-20)/max(1,n));
    int startX=HND_X+(HND_W-min((n-1)*overlap+CARD_W,HND_W-20))/2;
    int cardY=HND_Y+26;

    Btn bPlay  (ACT_X+8, ACT_Y+8,  ACT_W-16, 46, "锟斤拷锟斤拷",   19, false);
    Btn bRule  (ACT_X+8, ACT_Y+60, ACT_W-16, 40, "锟介看锟斤拷锟斤拷",15);
    Btn bHint  (ACT_X+8, ACT_Y+106,ACT_W-16, 40, "锟斤拷示",   15);
    vector<Btn> actionBtns={bPlay,bRule,bHint};

    while(humanSel<0 || (humanSel>=0&&false)){
        BeginBatchDraw();
        renderGameScreen();
        // 锟斤拷锟斤拷锟斤拷锟斤拷锟斤拷锟斤拷锟斤拷选锟叫ｏ拷
        fillArea(HND_X,HND_Y,HND_W,HND_H,C_PANEL,RGB(50,90,55),6);
        dtL(HND_X+10,HND_Y+6,"锟斤拷锟斤拷锟斤拷锟? 锟斤拷 锟斤拷锟窖★拷疲锟斤拷俚锟斤拷锟狡帮拷钮确锟斤拷",C_BLUE_T,14,true);
        for(int i=0;i<n;++i){
            bool s=(i==humanSel);
            int cx2=startX+i*min(overlap,(HND_W-20-CARD_W)/max(1,n-1));
            int cy2=cardY+(s?-12:0);
            drawCard(cx2,cy2,CARD_W,CARD_H-10,players[0].hand[i],true,s);
        }
        fillArea(ACT_X,ACT_Y,ACT_W,ACT_H,C_PANEL_D,RGB(30,60,30),6);
        actionBtns[0].enabled=(humanSel>=0);
        for(auto& b:actionBtns) b.draw(b.hit(mx,my));
        EndBatchDraw();

        ExMessage msg;
        while(peekmessage(&msg,EX_MOUSE)){
            mx=msg.x; my=msg.y;
            if(msg.message==WM_LBUTTONUP){
                // 锟斤拷锟斤拷
                for(int i=0;i<n;++i){
                    int cx2=startX+i*min(overlap,(HND_W-20-CARD_W)/max(1,n-1));
                    if(mx>=cx2&&mx<=cx2+CARD_W&&my>=cardY-14&&my<=cardY+CARD_H)
                        humanSel=(humanSel==i)?-1:i;
                }
                // 锟斤拷锟狡帮拷钮
                if(actionBtns[0].hit(mx,my)&&humanSel>=0) goto play_confirmed;
                // 锟斤拷锟斤拷钮
                if(actionBtns[1].hit(mx,my)){
                    BeginBatchDraw(); renderGameScreen();
                    showMsgBox("锟斤拷戏锟斤拷锟斤拷","锟饺达拷:K锟斤拷锟紸锟斤拷小 | 锟斤拷小:A锟斤拷锟斤拷K锟斤拷锟絓n锟斤拷10锟斤拷锟斤拷锟斤拷锟斤拷锟斤拷 | 5锟斤拷锟斤拷锟秸伙拷锟皆硷拷锟斤拷锟斤拷\n锟斤拷顺锟斤拷锟斤拷锟斤拷锟斤拷锟斤拷锟?| 锟斤拷锟斤拷锟斤拷锟斤拷 小锟斤拷偷锟斤拷");
                    EndBatchDraw();
                }
                // 锟斤拷示锟斤拷钮
                if(actionBtns[2].hit(mx,my)){
                    int hint=strategicChoice(players[0]);
                    humanSel=hint;
                }
            }
        }
        Sleep(16);
    }
    play_confirmed:
    playedIdx[0]=humanSel;
    tableCards[0]=players[0].hand[humanSel];

    // Step 2: 锟斤拷锟斤拷锟斤拷锟斤拷
    tableRevealed=true;
    addMsg("[锟斤拷锟斤拷] 锟斤拷锟斤拷同时锟斤拷锟斤拷");
    // 锟斤拷锟脚凤拷锟狡讹拷效锟斤拷锟津化ｏ拷锟饺憋拷锟斤拷0.3锟斤拷锟斤拷锟斤拷妫?
    for(int reveal=0;reveal<3;++reveal){
        BeginBatchDraw();
        renderGameScreen();
        // 锟斤拷前锟斤拷锟斤拷锟斤拷锟斤拷锟斤拷锟斤拷
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

    // Step 3: 锟斤拷锟斤拷/小锟斤拷同台锟斤拷示
    bool hasBig=false, hasSmall=false;
    for(int i=0;i<3;++i){
        if(tableCards[i].isJoker){
            if(tableCards[i].rank==RANK_BIG_JOKER) hasBig=true;
            else hasSmall=true;
        }
    }
    if(hasBig&&hasSmall){
        addMsg("[锟斤拷小锟斤拷同台] 双锟斤拷锟斤拷锟街ｏ拷");
        BeginBatchDraw(); renderGameScreen();
        showMsgBox("[锟斤拷小锟斤拷同台锟斤拷]","锟斤拷锟斤拷锟斤拷小锟斤拷同时锟斤拷锟街ｏ拷锟斤拷锟竭撅拷锟斤拷为锟斤拷锟脚ｏ拷锟斤拷锟街计分诧拷锟戒。");
        EndBatchDraw();
    }

    // Step 4: 锟斤拷10锟斤拷椋拷锟斤拷龋锟?
    int tenPlayer=-1;
    for(int i=0;i<3;++i)
        if(!tableCards[i].isJoker && tableCards[i].rank==RANK_10){ tenPlayer=i; break; }
    // 锟斤拷锟剿筹拷10时只取锟斤拷锟饺ｏ拷锟斤拷锟?锟斤拷锟饺ｏ拷
    bool hasTen=(tenPlayer>=0);

    // Step 5: 锟斤拷锟斤拷锟斤拷锟狡筹拷锟斤拷锟斤拷锟斤拷疲锟斤拷锟?0锟斤拷锟皆猴拷锟斤拷锟解处锟斤拷锟斤拷
    for(int i=0;i<3;++i){
        if(i==tenPlayer) continue; // 锟斤拷10锟斤拷锟斤拷锟狡猴拷锟斤拷锟斤拷perform10锟斤处锟斤拷
        if(playedIdx[i]>=0 && playedIdx[i]<(int)players[i].hand.size())
            players[i].hand.erase(players[i].hand.begin()+playedIdx[i]);
    }

    if(hasTen){
        perform10Mechanism(tenPlayer);
        addMsg("[锟斤拷10锟斤拷] 锟斤拷锟街诧拷锟狡凤拷");
        BeginBatchDraw(); renderGameScreen();
        showMsgBox("[锟斤拷10] 锟斤拷锟街诧拷锟狡凤拷","顺锟斤拷牵锟斤拷锟斤拷拼锟斤拷锟斤拷锟斤拷锟斤拷只锟斤拷锟斤拷锟斤拷锟斤拷锟?);
        EndBatchDraw();
    } else {
        // Step 5b: 锟斤拷10锟斤拷锟斤拷锟斤拷锟狡筹拷
        // (锟斤拷锟斤拷锟斤拷锟芥处锟斤拷锟斤拷tenPlayer锟斤拷tenPlayer==-1时全锟斤拷锟斤拷锟斤拷锟斤拷)

        // Step 6: 锟斤拷顺锟斤拷锟?
        vector<bool> skipMask(3,false);
        for(int i=0;i<3;++i) skipMask[i]=tableCards[i].isReturned;
        bool consecutive=isThreeConsecutive(tableCards,skipMask);

        // Step 7: 5锟斤拷锟狡硷拷锟筋（锟斤拷锟斤拷顺+锟睫筹拷10时锟斤拷
        vector<bool> activated;
        if(!consecutive){
            perform5CardActivations(tableCards,playedIdx,activated);
        }

        // Step 8: 锟斤拷顺锟斤拷锟狡ｏ拷锟斤拷5锟斤拷锟狡硷拷锟斤拷时锟斤拷
        bool anyActivated=false;
        for(bool a:activated) if(a) anyActivated=true;
        if(consecutive && !anyActivated){
            performDrawSequence();
        }

        // Step 9: 锟狡凤拷
        vector<int> scores=computeScores(tableCards);
        for(int i=0;i<3;++i) players[i].score+=scores[i];
        {
            string smsg="[锟狡凤拷] ";
            for(int i=0;i<3;++i){
                smsg+=players[i].name+":+"+to_string(scores[i])+" ";
            }
            addMsg(smsg);
        }

        // Step 10: 小锟斤拷锟绞诧拷锟斤拷
        applyBonusScore();

        // Step 11: 锟斤拷锟斤拷转锟叫讹拷
        handleRuleFlip(tableCards);

        // Step 12: 锟斤拷锟街斤拷锟秸故?
        BeginBatchDraw();
        renderGameScreen();
        // 锟斤拷锟斤拷锟斤拷
        int pw=440, ph=200;
        int px=(WIN_W-pw)/2, py=(WIN_H-ph)/2+60;
        fillRR(px,py,pw,ph,12,C_PANEL_D,C_GOLD,2);
        dtC(px+pw/2,py+28,"锟斤拷锟街斤拷锟?,C_GOLD,20,true);
        setlinecolor(C_GOLD); line(px+16,py+50,px+pw-16,py+50);
        for(int i=0;i<3;++i){
            char buf[64]; sprintf(buf,"%s  +%d锟斤拷  (锟斤拷:%d)",
                players[i].name.c_str(),scores[i],players[i].score);
            COLORREF tc=(scores[i]==2)?C_GOLD:(scores[i]==1)?C_GREEN_T:C_DIM;
            dtC(px+pw/2, py+72+i*38, buf, tc, 17, scores[i]==2);
        }
        dtC(px+pw/2,py+ph-28,"[ 锟斤拷锟斤拷锟斤拷锟?]",C_DIM,14,false);
        EndBatchDraw();
        ExMessage mm;
        while(true){ if(peekmessage(&mm,EX_MOUSE)&&mm.message==WM_LBUTTONUP) break; Sleep(16); }
    }
    // 锟斤拷锟斤拷锟斤拷锟?
    tableRevealed=false; tableCards.clear(); tableCards.resize(3);
}

// ===== 锟斤拷示锟斤拷锟斤拷锟斤拷锟斤拷 =====
void GameEngine::showFinalRank(){
    // 锟斤拷锟斤拷
    int ord[3]={0,1,2};
    sort(ord,ord+3,[this](int a,int b){ return players[a].score>players[b].score; });
    const char* medals[3]={"锟节撅拷","锟角撅拷","锟斤拷锟斤拷"};
    COLORREF cols[3]={C_GOLD,C_SILVER,RGB(180,100,50)};

    int pw=560, ph=360, px=(WIN_W-pw)/2, py=(WIN_H-ph)/2;
    BeginBatchDraw();
    renderGameScreen();
    setlinecolor(RGB(0,0,0)); setfillcolor(RGB(0,0,0));
    for(int yy=0;yy<WIN_H;yy+=3) line(0,yy,WIN_W,yy);
    fillRR(px,py,pw,ph,14,C_PANEL_D,C_GOLD,3);
    dtC(px+pw/2,py+32,"锟斤拷戏锟斤拷锟斤拷锟斤拷锟斤拷锟斤拷锟斤拷锟斤拷",C_GOLD,24,true);
    setlinecolor(C_GOLD); line(px+20,py+58,px+pw-20,py+58);
    for(int k=0;k<3;++k){
        int i=ord[k];
        char buf[64]; sprintf(buf,"%s  %s   %d 锟斤拷",medals[k],players[i].name.c_str(),players[i].score);
        dtC(px+pw/2, py+90+k*60, buf, cols[k], 22, k==0);
    }
    dtC(px+pw/2,py+ph-40,"锟斤拷谢锟斤拷锟芥《锟斤拷锟斤拷锟斤拷锟芥》锟斤拷",C_TEXT,16,false);
    dtC(px+pw/2,py+ph-18,"[ 锟斤拷锟斤拷锟斤拷锟斤拷锟斤拷说锟?]",C_DIM,13,false);
    EndBatchDraw();
    ExMessage mm;
    while(true){ if(peekmessage(&mm,EX_MOUSE)&&mm.message==WM_LBUTTONUP) break; Sleep(16); }
}

// ===== 锟斤拷锟斤拷 =====
void GameEngine::playTiebreaker(vector<int>& tied){
    while(true){
        // 锟斤拷5锟斤拷
        for(int i:tied) players[i].hand.clear();
        initDeck(); shuffleDeck();
        int ci=0;
        for(int r=0;r<5;++r) for(int i:tied) players[i].addCard(deck[ci++]);

        vector<int> tbScore(3,0);
        for(int tb=1;tb<=5;++tb){
            tableCards.clear(); tableCards.resize(3);
            playedIdx.assign(3,-1);
            tableRevealed=false;

            // AI锟斤拷锟斤拷
            for(int i:tied) if(!players[i].isHuman){
                int c=(int)(rng()%players[i].hand.size());
                playedIdx[i]=c; tableCards[i]=players[i].hand[c];
            }
            // 锟斤拷锟斤拷锟斤拷锟?
            bool humanIn=false; for(int i:tied) if(players[i].isHuman) humanIn=true;
            if(humanIn){
                // 锟斤拷锟斤拷锟斤拷guiSelectCard
                int h=guiSelectCard(0,"[锟斤拷锟斤拷锟斤拷"+to_string(tb)+"/5锟斤拷] 锟斤拷选锟斤拷锟斤拷锟?);
                if(h<0) h=0;
                playedIdx[0]=h; tableCards[0]=players[0].hand[h];
            }
            // 锟斤拷锟斤拷
            tableRevealed=true;
            BeginBatchDraw(); renderGameScreen(); EndBatchDraw(); Sleep(400);

            // 锟狡分ｏ拷锟斤拷锟斤拷锟斤拷锟竭ｏ拷
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
            // 锟狡筹拷锟斤拷锟斤拷锟斤拷锟?
            for(int i:tied)
                if(playedIdx[i]>=0&&playedIdx[i]<(int)players[i].hand.size())
                    players[i].hand.erase(players[i].hand.begin()+playedIdx[i]);

            addMsg("[锟斤拷锟斤拷"+to_string(tb)+"/5] 锟斤拷锟街斤拷锟斤拷");
            BeginBatchDraw(); renderGameScreen(); EndBatchDraw(); Sleep(600);
            tableRevealed=false;
        }
        // 锟叫讹拷
        int maxTb=0; for(int i:tied) if(tbScore[i]>maxTb) maxTb=tbScore[i];
        vector<int> still;
        for(int i:tied) if(tbScore[i]==maxTb) still.push_back(i);
        if((int)still.size()==1){ tied=still; break; }
        tied=still;
        BeginBatchDraw(); renderGameScreen();
        showMsgBox("[锟斤拷锟斤拷平锟斤拷]","锟斤拷然平锟街ｏ拷锟斤拷锟斤拷锟斤拷锟斤拷锟斤拷");
        EndBatchDraw();
    }
}

// ===== 锟斤拷锟斤拷锟斤拷锟斤拷 =====
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

// ===== 锟斤拷始锟斤拷锟斤拷戏 =====
void GameEngine::startNewGame(){
    // 模式选
    gameMode=showModeSelect();
    if(gameMode==1){
        // 目锟斤拷锟窖★拷锟?
        int bw=440, bh=290, bx=(WIN_W-bw)/2, by=(WIN_H-bh)/2;
        Btn b30(bx+30,by+80,bw-60,44,"30 锟斤拷",19);
        Btn b60(bx+30,by+132,bw-60,44,"60 锟斤拷",19);
        Btn b100(bx+30,by+184,bw-60,44,"100 锟斤拷",19);
        Btn b150(bx+30,by+236,bw-60,44,"150 锟斤拷",19);
        vector<Btn> tbBtns={b30,b60,b100,b150};
        int tscores[]={30,60,100,150};
        int chosen=waitBtns(tbBtns,[&](){
            setfillcolor(C_TABLE); fillrectangle(0,0,WIN_W,WIN_H);
            fillRR(bx,by,bw,bh,12,C_PANEL_D,C_GOLD,2);
            dtC(bx+bw/2,by+40,"选锟斤拷目锟斤拷锟?,C_GOLD,22,true);
        });
        targetScore=tscores[chosen];
    }

    if(!consecutiveGame){
        for(int i=0;i<3;++i){ players[i].score=0; players[i].resetJokerUses(); }
        sceneCount=1;
    }
    for(int i=0;i<3;++i) players[i].hand.clear();
    round=1; lastRoundTwoWayTie=false;
    for(int i=0;i<3;++i) fiveReturnPending[i]=false;
    initDeck(); shuffleDeck(); dealCards(18);

    // 锟斤拷锟狡猴拷锟斤拷展示锟斤拷锟斤拷锟斤拷锟狡ｏ拷锟斤拷锟矫猴拷锟斤拷A选锟斤拷锟斤拷
    {
        BeginBatchDraw();
        setfillcolor(C_TABLE); fillrectangle(0,0,WIN_W,WIN_H);
        renderInfoBar();
        renderHumanHand();
        dtC(WIN_W/2,WIN_H/2-100,"锟斤拷锟斤拷锟斤拷桑锟斤拷锟斤拷炔榭达拷锟斤拷锟斤拷锟斤拷",C_GOLD,22,true);
        dtC(WIN_W/2,WIN_H/2-60,"锟斤拷锟斤拷锟斤拷锟斤拷锟窖★拷锟斤拷锟斤拷",C_DIM,16,false);
        EndBatchDraw();
        ExMessage mm;
        while(true){ if(peekmessage(&mm,EX_MOUSE)&&mm.message==WM_LBUTTONUP) break; Sleep(16); }
    }

    // 锟斤拷锟斤拷A选锟斤拷锟斤拷
    int chooser=-1;
    for(int i=0;i<3;++i) if(players[i].hasSpadeA()){ chooser=i; break; }
    if(!consecutiveGame){
        if(chooser==0){
            int bw=480,bh=220,bx=(WIN_W-bw)/2,by=(WIN_H-bh)/2;
            Btn bBig  (bx+30,by+90,bw-60,48,"锟饺达拷 (K锟斤拷锟紸锟斤拷小)",18);
            Btn bSmall(bx+30,by+148,bw-60,48,"锟斤拷小 (A锟斤拷锟脚ｏ拷K锟斤拷锟?",18);
            vector<Btn> rBtns={bBig,bSmall};
            int r=waitBtns(rBtns,[&](){
                setfillcolor(C_TABLE); fillrectangle(0,0,WIN_W,WIN_H);
                fillRR(bx,by,bw,bh,12,C_PANEL_D,C_GOLD,2);
                dtC(bx+bw/2,by+50,"锟斤拷锟斤拷泻锟斤拷锟紸锟斤拷选锟斤拷锟绞硷拷锟斤拷锟?,C_GOLD,20,true);
            });
            currentRule=(r==0)?BIG_WINS:SMALL_WINS;
        } else {
            currentRule=(GameRule)(rng()%2);
            BeginBatchDraw(); renderGameScreen();
            char info[64]; sprintf(info,"%s 锟斤拷锟叫猴拷锟斤拷A锟斤拷锟斤拷锟窖★拷锟斤拷耍锟?s",
                (chooser>=0)?players[chooser].name.c_str():"系统",
                currentRule==BIG_WINS?"锟饺达拷":"锟斤拷小");
            showMsgBox("锟斤拷始锟斤拷锟斤拷确锟斤拷",info);
            EndBatchDraw();
        }
    } else {
        if(chooser>=0){
            players[chooser].score++;
            char info[64]; sprintf(info,"%s 锟斤拷锟叫猴拷锟斤拷A锟斤拷锟斤拷锟斤拷锟斤拷锟斤拷+1锟斤拷",players[chooser].name.c_str());
            BeginBatchDraw(); renderGameScreen();
            showMsgBox("锟斤拷锟斤拷锟斤拷始",info);
            EndBatchDraw();
        }
    }
    consecutiveGame=false;

    // 锟斤拷循锟斤拷
    for(;round<=18;++round){
        playRound();
        if(gameMode==1){
            vector<int> tied;
            if(checkEndCondition(tied)){
                if(tied.empty()){ showFinalRank(); return; }
                BeginBatchDraw(); renderGameScreen();
                showMsgBox("锟斤拷辏★拷锟斤拷锟斤拷锟斤拷","锟斤拷锟斤拷掖锟疥但锟斤拷锟斤拷锟斤拷锟叫ｏ拷锟斤拷锟叫硷拷锟斤拷锟斤拷");
                EndBatchDraw();
                playTiebreaker(tied); showFinalRank(); return;
            }
        }
        if(round==18) break;
    }
    // 18锟街斤拷锟斤拷
    if(gameMode==0){
        showFinalRank();
    } else {
        BeginBatchDraw(); renderGameScreen();
        showMsgBox("18锟街斤拷锟斤拷","锟斤拷锟斤拷锟剿达拷辏拷锟斤拷锟斤拷锟揭伙拷锟斤拷锟斤拷锟斤拷旨坛校锟斤拷锟斤拷路锟斤拷啤锟?);
        EndBatchDraw();
        sceneCount++;
        consecutiveGame=true;
        for(int i=0;i<3;++i) players[i].resetJokerUses();
        startNewGame();
    }
}

// ===== 锟斤拷锟斤拷锟斤拷锟?=====
void GameEngine::showRulesScreen(){
    struct RuleItem{ const char* icon; const char* title; const char* desc; };
    RuleItem items[]={
        {"[锟斤拷锟斤拷]","锟斤拷锟剿讹拷战 54锟斤拷","每锟斤拷18锟脚ｏ拷锟斤拷18锟街ｏ拷锟斤拷锟斤拷锟狡ｏ拷锟斤拷1锟斤拷+2, 锟斤拷2锟斤拷+1, 锟斤拷3锟斤拷+0锟斤拷"},
        {"[锟饺达拷]","K锟斤拷锟紸锟斤拷小","锟饺达拷模式锟斤拷K>Q>...>2>A锟斤拷锟斤拷锟斤拷/小锟斤拷锟斤拷为锟斤拷锟斤拷"},
        {"[锟斤拷小]","A锟斤拷锟斤拷K锟斤拷锟?,"锟斤拷小模式锟斤拷A>2>...>K锟斤拷锟斤拷锟斤拷/小锟斤拷锟斤拷为锟斤拷锟斤拷"},
        {"[锟斤拷10]","顺锟斤拷牵锟斤拷","唯一锟斤拷10: 锟斤拷锟斤拷锟斤拷锟剿筹拷锟斤拷锟狡ｏ拷锟斤拷锟斤拷1锟脚ｏ拷锟铰硷拷锟斤拷盲锟斤拷1锟斤拷"},
        {"[5锟斤拷]","锟斤拷猫锟斤拷太锟斤拷","锟斤拷锟脚革拷锟斤拷同锟斤拷锟斤拷锟斤拷锟斤拷锟? 锟斤拷锟侥讹拷锟斤拷5锟斤拷锟斤拷锟街筹拷锟斤拷锟斤拷锟秸伙拷"},
        {"[锟斤拷顺]","锟斤拷锟斤拷锟斤拷锟斤拷锟斤拷锟斤拷","锟斤拷锟脚碉拷锟斤拷锟斤拷锟斤拷锟斤拷锟斤拷锟秸伙拷锟狡ｏ拷: 锟斤拷锟斤拷顺时锟斤拷锟铰硷拷锟斤拷锟斤拷盲锟斤拷1锟斤拷"},
        {"[锟斤拷锟斤拷]","锟斤拷锟斤拷偏锟斤拷","锟斤拷选锟斤拷时锟斤拷偏锟斤拷 N->N-1锟斤拷每锟斤拷锟斤拷2锟轿ｏ拷"},
        {"[小锟斤拷]","偷锟斤拷锟斤拷锟斤拷","锟斤拷顺锟斤拷锟斤拷前锟斤拷偷锟斤拷目锟斤拷锟斤拷锟狡ｏ拷每锟斤拷锟斤拷1锟轿ｏ拷"},
        {"[锟斤拷转]","锟斤拷锟斤拷态锟戒化","锟斤拷锟斤拷锟斤拷锟斤拷锟斤拷锟斤拷同: 小锟斤拷锟绞达拷锟斤拷锟斤拷锟斤拷转锟斤拷锟饺达拷<->锟斤拷小锟斤拷"},
        {"[锟斤拷锟斤拷]","锟斤拷锟斤拷锟斤拷锟?,"每锟斤拷约12%锟斤拷锟斤拷锟斤拷锟斤拷锟揭伙拷锟斤拷锟斤拷+1锟斤拷"},
        {"[锟斤拷锟斤拷]","锟斤拷胜锟斤拷锟斤拷","锟斤拷锟斤拷模式+锟斤拷锟叫达拷锟? 锟斤拷锟斤拷5锟斤拷5锟街硷拷锟斤拷直锟斤拷锟街筹拷锟斤拷锟斤拷"},
    };
    int n=sizeof(items)/sizeof(items[0]);
    int scroll=0;
    int perPage=7;

    Btn bBack(WIN_W/2-80,WIN_H-52,160,40,"锟斤拷锟斤拷锟斤拷锟剿碉拷",17);
    Btn bUp  (WIN_W-70,100,56,36,"锟斤拷",16);
    Btn bDown(WIN_W-70,WIN_H-100,56,36,"锟斤拷",16);
    vector<Btn> navBtns={bBack};

    int mx=0,my=0;
    while(true){
        BeginBatchDraw();
        setfillcolor(C_TABLE); fillrectangle(0,0,WIN_W,WIN_H);
        fillRR(30,10,WIN_W-60,WIN_H-20,12,C_PANEL_D,C_GOLD,2);
        dtC(WIN_W/2,46,"锟斤拷锟斤拷锟斤拷锟斤拷锟芥》锟斤拷戏锟斤拷锟斤拷",C_GOLD,26,true);
        setlinecolor(C_GOLD); line(50,72,WIN_W-50,72);
        // 锟斤拷锟斤拷锟斤拷目
        for(int k=0;k<perPage&&(k+scroll)<n;++k){
            int i=k+scroll;
            int ry=86+k*82;
            fillRR(50,ry,WIN_W-100,74,8,C_PANEL,RGB(40,80,45));
            dtL(62,ry+8, items[i].icon, C_GOLD, 14, true);
            dtL(62,ry+30, items[i].title, C_WHITE, 17, true);
            dtL(180,ry+14, items[i].desc, C_TEXT, 14, false);
        }
        // 锟斤拷锟斤拷锟斤拷示
        if(scroll>0)    dtC(WIN_W-40,90,"锟斤拷",C_GOLD,16,true);
        if(scroll+perPage<n) dtC(WIN_W-40,WIN_H-90,"锟斤拷",C_GOLD,16,true);
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
                // 锟斤拷锟斤拷锟斤拷头锟斤拷锟斤拷
                if(mx>=WIN_W-64&&mx<=WIN_W-16&&my>=80&&my<=120) scroll=max(0,scroll-1);
                if(mx>=WIN_W-64&&mx<=WIN_W-16&&my>=WIN_H-120&&my<=WIN_H-80) scroll=min(n-perPage,scroll+1);
            }
        }
        Sleep(16);
    }
    rules_back:;
}

// ===== 模式选锟斤拷 =====
int GameEngine::showModeSelect(){
    int bw=520,bh=280,bx=(WIN_W-bw)/2,by=(WIN_H-bh)/2;
    Btn bSingle(bx+30,by+90, bw-60,54,"锟斤拷锟斤拷模式锟斤拷18锟街ｏ拷锟斤拷锟杰凤拷锟斤拷锟斤拷锟斤拷",18);
    Btn bTarget(bx+30,by+154,bw-60,54,"锟斤拷锟斤拷模式锟斤拷锟饺达拷目锟斤拷锟斤拷锟绞わ拷锟?,18);
    vector<Btn> btns={bSingle,bTarget};
    return waitBtns(btns,[&](){
        setfillcolor(C_TABLE); fillrectangle(0,0,WIN_W,WIN_H);
        fillRR(bx,by,bw,bh,12,C_PANEL_D,C_GOLD,2);
        dtC(bx+bw/2,by+44,"选锟斤拷锟斤拷戏模式",C_GOLD,22,true);
        setlinecolor(C_GOLD); line(bx+20,by+68,bx+bw-20,by+68);
    });
}

// ===== 锟斤拷锟剿碉拷 =====
void GameEngine::showMainMenu(){
    Btn bStart (WIN_W/2-130,340,260,58,"锟斤拷始锟斤拷戏",22);
    Btn bRules (WIN_W/2-130,414,260,52,"锟斤拷戏锟斤拷锟斤拷",19);
    Btn bExit  (WIN_W/2-130,482,260,52,"锟剿筹拷锟斤拷戏",19);
    vector<Btn> btns={bStart,bRules,bExit};

    int mx=0,my=0;
    while(true){
        BeginBatchDraw();
        // 锟斤拷锟戒背锟斤拷
        for(int y=0;y<WIN_H;++y){
            int r=max(0,22-(int)(y*8/WIN_H));
            int g=max(0,100-(int)(y*28/WIN_H));
            int b=max(0,52-(int)(y*14/WIN_H));
            setlinecolor(RGB(r,g,b));
            line(0,y,WIN_W,y);
        }
        // 锟斤拷锟斤拷装锟轿憋拷锟斤拷锟斤拷
        fillRR(WIN_W/2-300,60,600,240,16,RGB(8,45,22),C_GOLD,2);
        // 锟斤拷锟斤拷锟斤拷
        dtC(WIN_W/2,140,"锟斤拷 锟斤拷 锟斤拷 锟斤拷",C_GOLD,64,true);
        dtC(WIN_W/2,218,"San Xiong Zheng Feng  锟斤拷  Card Battle v3.0",C_DIM,16,false);
        setlinecolor(C_GOLD); line(WIN_W/2-220,248,WIN_W/2+220,248);
        dtC(WIN_W/2,275,"锟斤拷锟剿讹拷战  |  54锟斤拷锟斤拷  |  EasyX 图锟轿斤拷锟斤拷",C_SILVER,16,false);
        // 锟斤拷钮
        for(auto& b:btns) b.draw(b.hit(mx,my));
        // 锟斤拷权
        dtC(WIN_W/2,WIN_H-24,"锟斤拷迎锟斤拷锟芥，祝锟届开锟斤拷胜锟斤拷",C_DIM,13,false);
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
    initgraph(WIN_W, WIN_H); // 锟斤拷示图锟轿达拷锟斤拷
    SetWindowText(GetHWnd(),"锟斤拷锟斤拷锟斤拷锟斤拷 v3.0");
    setbkcolor(C_TABLE);
    BeginBatchDraw();
    GameEngine eng;
    g_eng=&eng;
    eng.showMainMenu();
    EndBatchDraw();
    closegraph();
    return 0;
}
