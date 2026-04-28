# -*- coding: utf-8 -*-
"""BP1: 头文件 + 颜色系统 + 枚举 + Card类"""
code = r"""/*
 * 三雄争锋 v2.0
 * 编译环境：Dev-C++ 5.11 (需启用 C++11，编译选项加 -std=c++11)
 * 字符编码：ANSI / GBK
 */
#include <iostream>
#include <vector>
#include <string>
#include <algorithm>
#include <random>
#include <ctime>
#include <cstdlib>
#include <limits>
#include <chrono>
#include <sstream>
#include <iomanip>
#ifdef _WIN32
#include <windows.h>
#define CLEAR_SCREEN system("cls")
#else
#define CLEAR_SCREEN system("clear")
#endif
using namespace std;

// ==================== 颜色工具 ====================
void setColor(int fg, int bg = 0) {
#ifdef _WIN32
    SetConsoleTextAttribute(GetStdHandle(STD_OUTPUT_HANDLE), (bg << 4) | fg);
#endif
}
void resetColor() { setColor(15, 0); }
void hideCursor(bool h) {
#ifdef _WIN32
    CONSOLE_CURSOR_INFO ci = {1, (BOOL)!h};
    SetConsoleCursorInfo(GetStdHandle(STD_OUTPUT_HANDLE), &ci);
#endif
}
void cprint(const string& s, int fg, int bg = 0) {
    setColor(fg, bg); cout << s; resetColor();
}
void printSep(char c = '-', int len = 56) {
    setColor(11);
    cout << "+"; for (int i=0;i<len-2;++i) cout<<c; cout<<"+"<<endl;
    resetColor();
}
void printDSep(int len = 56) {
    setColor(14);
    cout << "="; for (int i=0;i<len-2;++i) cout<<"="; cout<<"="<<endl;
    resetColor();
}
void pauseEnter() {
    cprint("  [ 按回车继续... ]", 8);
    cout << endl;
    cin.get();
}

// ==================== 枚举 ====================
enum Suit { SPADE=0, HEART, CLUB, DIAMOND, JOKER_SUIT };
enum Rank {
    RANK_A=1, RANK_2, RANK_3, RANK_4, RANK_5, RANK_6,
    RANK_7, RANK_8, RANK_9, RANK_10, RANK_J, RANK_Q, RANK_K,
    RANK_SMALL_JOKER=100, RANK_BIG_JOKER=101
};
enum GameRule { BIG_WINS, SMALL_WINS };

// ==================== Card 类 ====================
class Card {
public:
    Suit suit;
    Rank rank;
    bool isJoker;
    bool isReturned; // 被5号牌收回标记，打出后不触发连顺

    Card() : suit(SPADE), rank(RANK_A), isJoker(false), isReturned(false) {}
    Card(Suit s, Rank r, bool joker=false)
        : suit(s), rank(r), isJoker(joker), isReturned(false) {}

    int getCompareValue(GameRule rule) const {
        if (isJoker) {
            if (rule==BIG_WINS) return (rank==RANK_BIG_JOKER)?1000:900;
            else                return (rank==RANK_BIG_JOKER)?-1000:-900;
        }
        return static_cast<int>(rank);
    }
    string rankString() const {
        if (isJoker) return (rank==RANK_BIG_JOKER)?"大王":"小王";
        switch(rank){
            case RANK_A: return "A"; case RANK_J: return "J";
            case RANK_Q: return "Q"; case RANK_K: return "K";
            default: return to_string(static_cast<int>(rank));
        }
    }
    string suitString() const {
        if (isJoker) return "";
        switch(suit){
            case SPADE:   return "黑桃";
            case HEART:   return "红心";
            case CLUB:    return "梅花";
            case DIAMOND: return "方块";
            default: return "";
        }
    }
    string toString() const {
        if (isJoker) return rankString();
        return suitString()+rankString();
    }
    int getSuitColor() const {
        if (isJoker) return 14;
        if (suit==HEART||suit==DIAMOND) return 12;
        return 15;
    }
    void printColored() const {
        setColor(getSuitColor(),0);
        if (isJoker) cout<<"【"<<rankString()<<"】";
        else         cout<<"["<<suitString()<<rankString()<<"]";
        resetColor();
    }
    bool isTen()       const { return !isJoker && rank==RANK_10; }
    bool isFive()      const { return !isJoker && rank==RANK_5; }
    bool isSpadeA()    const { return !isJoker && suit==SPADE && rank==RANK_A; }
    bool isBigJoker()  const { return isJoker && rank==RANK_BIG_JOKER; }
    bool isSmallJoker()const { return isJoker && rank==RANK_SMALL_JOKER; }
    bool equals(const Card& o) const {
        if (isJoker!=o.isJoker) return false;
        if (isJoker) return rank==o.rank;
        return suit==o.suit && rank==o.rank;
    }
};

"""
with open(r'd:\Users\ymx36\Desktop\三雄争锋游戏\三雄争锋v2.cpp','w',encoding='gbk') as f:
    f.write(code)
print("BP1 OK - 头文件/颜色/Card类 写入完成")
