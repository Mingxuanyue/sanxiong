/*
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


// ==================== Player 类 ====================
class Player {
public:
    string name;
    vector<Card> hand;
    int score;
    bool isHuman;
    bool isStrategic;
    int bigJokerUses;   // 大王技能已用次数（跟人走，每场上限2）
    int smallJokerUses; // 小王技能已用次数（跟人走，每场上限1）

    Player(string n, bool human=false, bool strategic=false)
        : name(n), score(0), isHuman(human), isStrategic(strategic),
          bigJokerUses(0), smallJokerUses(0) {}

    void resetJokerUses() { bigJokerUses=0; smallJokerUses=0; }

    bool hasBigJoker()   const { for(auto&c:hand) if(c.isBigJoker())   return true; return false; }
    bool hasSmallJoker() const { for(auto&c:hand) if(c.isSmallJoker()) return true; return false; }
    bool canUseBigJoker()   const { return hasBigJoker()   && bigJokerUses<2; }
    bool canUseSmallJoker() const { return hasSmallJoker() && smallJokerUses<1; }

    int findBigJoker() const {
        for(int i=0;i<(int)hand.size();++i) if(hand[i].isBigJoker()) return i;
        return -1;
    }
    int findSmallJoker() const {
        for(int i=0;i<(int)hand.size();++i) if(hand[i].isSmallJoker()) return i;
        return -1;
    }
    int findFiveCard(int excludeIdx=-1) const {
        for(int i=0;i<(int)hand.size();++i)
            if(i!=excludeIdx && hand[i].isFive()) return i;
        return -1;
    }
    void addCard(const Card& c) { hand.push_back(c); }
    Card removeCard(int idx) {
        Card c=hand[idx]; hand.erase(hand.begin()+idx); return c;
    }
    bool removeSpecificCard(const Card& t) {
        for(auto it=hand.begin();it!=hand.end();++it)
            if(it->equals(t)){ hand.erase(it); return true; }
        return false;
    }
    bool hasSpadeA() const { for(auto&c:hand) if(c.isSpadeA()) return true; return false; }
    void showHand() const {
        for(size_t i=0;i<hand.size();++i){
            setColor(11); cout<<"["<<setw(2)<<i+1<<"] "; resetColor();
            hand[i].printColored();
            if(hand[i].isReturned){ setColor(8); cout<<"*"; resetColor(); }
            cout<<"  ";
            if((i+1)%6==0) cout<<endl;
        }
        if(hand.size()%6!=0) cout<<endl;
    }
};

// ==================== GameEngine 类 ====================
class GameEngine {
private:
    vector<Player> players;
    GameRule currentRule;
    int round;
    vector<Card> deck;
    mt19937 rng;

    // 状态变量
    bool lastRoundTwoWayTie; // 上回合是否两张同（连续两次翻转用）
    int  gameMode;           // 0=单局, 1=达标分
    int  targetScore;        // 目标分
    bool consecutiveGame;    // 是否连续开局（续场）
    int  sceneCount;         // 当前是第几场

    // 5号牌待归还状态（下回合开始前执行）
    bool fiveReturnPending[3];
    Card fiveReturnCard[3];

    // ---- 工具 ----
    void initDeck();
    void shuffleDeck();
    void dealCards(int n=18);

    // ---- 显示 ----
    void showHeader();
    void showStatus();
    void showRules();
    void showFinalRank();

    // ---- 输入 ----
    int  getHumanChoice(int maxIdx, const string& prompt="请选择编号");
    int  getMenuChoice(int mn, int mx);
    bool getYesNo(const string& prompt);
    int  getDiscardChoice(Player& p, const string& prompt);
    vector<int> getTwoDiscardChoices(Player& p);

    // ---- AI ----
    int  strategicChoice(const Player& p);
    void strategicDiscard(Player& p, int count);
    int  aiBlindChoice(int maxIdx);

    // ---- 计分 ----
    vector<int> computeScores(const vector<Card>& cards);
    bool isThreeConsecutive(const vector<Card>& cards, const vector<bool>& skipMask);
    void applyBonusScore(bool twoTie, bool threeTie);
    void handleRuleFlip(bool threeTie, bool twoTie);

    // ---- 特殊机制 ----
    void perform10Mechanism(int tenPlayer, vector<Card>& tableCards, vector<int>& playedIdx);
    void processFiveReturns();
    bool check5CardActivation(int pIdx, int playedIdx, const vector<Card>& table);
    void perform5CardActivations(const vector<Card>& table, const vector<int>& playedIdx,
                                  vector<bool>& activated);
    void performDrawSequence();
    int  performBigJokerDefense(int targetPlayer, int chosenIdx); // 返回实际idx
    void performSmallJokerPeek(int peekPlayer, int targetPlayer);

    // ---- 对局流程 ----
    void playRound();
    void playTiebreaker(vector<int>& tied);
    bool checkEndCondition(vector<int>& tied);

public:
    GameEngine();
    void startNewGame();
    void mainMenu();
};


// ==================== 构造函数 ====================
GameEngine::GameEngine()
    : rng(chrono::steady_clock::now().time_since_epoch().count()),
      currentRule(BIG_WINS), round(1),
      lastRoundTwoWayTie(false), gameMode(0), targetScore(0),
      consecutiveGame(false), sceneCount(1) {
    srand((unsigned)time(NULL));
    players.push_back(Player("玩家 A (你)", true, false));
    players.push_back(Player("玩家 B (AI策略)", false, true));
    players.push_back(Player("玩家 C (AI随机)", false, false));
    for(int i=0;i<3;++i){ fiveReturnPending[i]=false; }
}

// ==================== 发牌 ====================
void GameEngine::initDeck() {
    deck.clear();
    for(int s=SPADE;s<=DIAMOND;++s)
        for(int r=RANK_A;r<=RANK_K;++r)
            deck.push_back(Card((Suit)s,(Rank)r,false));
    deck.push_back(Card(JOKER_SUIT,RANK_SMALL_JOKER,true));
    deck.push_back(Card(JOKER_SUIT,RANK_BIG_JOKER,true));
}
void GameEngine::shuffleDeck() { shuffle(deck.begin(),deck.end(),rng); }
void GameEngine::dealCards(int n) {
    for(int i=0;i<(int)players.size()*n;++i)
        players[i%(int)players.size()].addCard(deck[i]);
}

// ==================== showHeader ====================
void GameEngine::showHeader() {
    setColor(14,1);
    cout<<"  +==================================================+"<<endl;
    cout<<"  |                                                  |"<<endl;
    setColor(15,1);
    cout<<"  |    ";
    setColor(14,1); cout<<"** ";
    setColor(12,1); cout<<"三";
    setColor(14,1); cout<<"** ";
    setColor(12,1); cout<<"雄";
    setColor(14,1); cout<<"** ";
    setColor(12,1); cout<<"争";
    setColor(14,1); cout<<"** ";
    setColor(12,1); cout<<"锋";
    setColor(14,1); cout<<"** ";
    setColor(15,1); cout<<"        v2.0          |"<<endl;
    cout<<"  |                                                  |"<<endl;
    cout<<"  +==================================================+"<<endl;
    resetColor();
    cout<<endl;
}

// ==================== showStatus ====================
void GameEngine::showStatus() {
    // 回合进度
    setColor(11);
    cout<<"  +-------------------------------------------------+"<<endl;
    cout<<"  |  第 ";
    setColor(14); cout<<round;
    setColor(11); cout<<" / 18 局";
    if(consecutiveGame){ setColor(8); cout<<"  (第"<<sceneCount<<"场)"; }
    cout<<"        规则: ";
    if(currentRule==BIG_WINS){ setColor(12); cout<<"比大 (K最大,A最小)"; }
    else { setColor(10); cout<<"比小 (A最优,K最差)"; }
    setColor(11); cout<<"  |"<<endl;
    cout<<"  +-------------------------------------------------+"<<endl;
    // 回合进度条
    cout<<"  |  进度: [";
    setColor(10);
    for(int i=0;i<round-1;++i) cout<<"#";
    setColor(8);
    for(int i=round-1;i<18;++i) cout<<"-";
    setColor(11); cout<<"]  |"<<endl;
    cout<<"  +-------------------------------------------------+"<<endl;
    // 积分
    cout<<"  |  积分板:"<<endl;
    string rankSyms[3]={"  |  > ","  |    ","  |    "};
    // 排序名次
    int ord[3]={0,1,2};
    for(int i=0;i<2;++i) for(int j=i+1;j<3;++j)
        if(players[ord[i]].score<players[ord[j]].score) swap(ord[i],ord[j]);
    for(int k=0;k<3;++k){
        int i=ord[k];
        cout<<"  |    ";
        int col=(k==0)?14:(k==1)?11:8;
        setColor(col);
        cout<<players[i].name<<" : "<<players[i].score<<" 分";
        if(gameMode==1 && targetScore>0){
            int rem=targetScore-players[i].score;
            if(rem>0){ setColor(8); cout<<" (距目标还差"<<rem<<"分)"; }
            else { setColor(10); cout<<" ★达标★"; }
        }
        resetColor(); setColor(11);
        cout<<endl;
    }
    cout<<"  +-------------------------------------------------+"<<endl;
    resetColor();
    cout<<endl;
}

// ==================== showRules ====================
void GameEngine::showRules() {
    CLEAR_SCREEN;
    showHeader();
    printDSep();
    cprint("  《三雄争锋》游戏规则\n\n",14);
    cprint("  【基础规则】\n",11);
    cout<<"  1. 3人对战，每人18张牌（54张标准牌含大小王），共18局\n";
    cout<<"  2. 持黑桃A者选择首场规则：比大（K最大）或比小（A最优）\n";
    cout<<"  3. 每局各出1张牌，按规则比大小：第1名+2，第2名+1，第3名+0\n";
    cout<<"  4. 大王/小王无论比大比小均为最优牌，大王>小王>所有普通牌\n\n";
    cprint("  【特殊机制】\n",11);
    cout<<"  ★ 出10（唯一）: 取走另两人出的牌，自弃1张，下家盲弃1张，本局不计分\n";
    cout<<"  ★ 5号牌: 三张各不同且你非最大时可激活，消耗手中一张5将本轮出的牌收回\n";
    cout<<"  ★ 连顺: 三张点数连续触发抽牌，每人从下家盲选1张（抽取人看不见）\n";
    cout<<"  ★ 大王: 被操作时可将对方选的N号偏移为N-1（每场限2次）\n";
    cout<<"  ★ 小王: 连顺抽牌时可偷窥对方手牌（每场限1次）\n\n";
    cprint("  【规则翻转】\n",11);
    cout<<"  * 三张点数完全相同：均不计分，规则翻转，补分+2\n";
    cout<<"  * 连续两局均出现两张同点数：第二局不计分，规则翻转，补分+1\n\n";
    cprint("  【补分】出现平局时，当前唯一最低分者额外获得补分\n",11);
    cprint("  【加赛】达标分模式下有人达标且同分时，重新发5张决出名次\n",11);
    printDSep();
    pauseEnter();
}

// ==================== showFinalRank ====================
void GameEngine::showFinalRank() {
    printDSep();
    cprint("  ========== 最终排名 ==========\n",14);
    int ord[3]={0,1,2};
    for(int i=0;i<2;++i) for(int j=i+1;j<3;++j)
        if(players[ord[i]].score<players[ord[j]].score) swap(ord[i],ord[j]);
    string medals[3]={"1st","2nd","3rd"};
    string fallback[3]={"第一名","第二名","第三名"};
    for(int k=0;k<3;++k){
        int i=ord[k];
        int col=(k==0)?14:(k==1)?11:8;
        setColor(col);
        cout<<"  "<<fallback[k]<<": "<<players[i].name<<" - "<<players[i].score<<" 分"<<endl;
        resetColor();
    }
    // 胜者
    if(players[ord[0]].score!=players[ord[1]].score){
        cprint("\n  ★ 胜者: "+players[ord[0]].name+" ★\n",14);
    } else {
        cprint("\n  平局！最高分并列。\n",11);
    }
    printDSep();
}


// ==================== 输入方法 ====================
int GameEngine::getHumanChoice(int maxIdx, const string& prompt) {
    int c;
    while(true){
        setColor(11); cout<<"  "<<prompt<<" (1~"<<maxIdx<<"): "; resetColor();
        cin>>c;
        if(cin.fail()||c<1||c>maxIdx){
            cin.clear(); cin.ignore(numeric_limits<streamsize>::max(),'\n');
            cprint("  输入无效，请重新输入。\n",12);
        } else { cin.ignore(numeric_limits<streamsize>::max(),'\n'); return c-1; }
    }
}
int GameEngine::getMenuChoice(int mn, int mx) {
    int c;
    while(true){
        cin>>c;
        if(cin.fail()||c<mn||c>mx){
            cin.clear(); cin.ignore(numeric_limits<streamsize>::max(),'\n');
            cprint("  输入无效，请重新选择: ",12);
        } else { cin.ignore(numeric_limits<streamsize>::max(),'\n'); return c; }
    }
}
bool GameEngine::getYesNo(const string& prompt) {
    setColor(11); cout<<"  "<<prompt<<" (1=是 / 0=否): "; resetColor();
    int c=getMenuChoice(0,1);
    return c==1;
}
int GameEngine::getDiscardChoice(Player& p, const string& prompt) {
    cout<<endl;
    cprint("  "+prompt+"\n",11);
    p.showHand();
    return getHumanChoice((int)p.hand.size(),"请选择编号");
}
vector<int> GameEngine::getTwoDiscardChoices(Player& p) {
    vector<int> idxs;
    cout<<endl;
    cprint("  请选择要弃掉的2张牌：\n",11);
    p.showHand();
    while((int)idxs.size()<2){
        int idx=getHumanChoice((int)p.hand.size(),
            "选第"+to_string((int)idxs.size()+1)+"张弃牌编号");
        bool dup=false;
        for(int x:idxs) if(x==idx){ dup=true; break; }
        if(dup){ cprint("  不能重复选同一张。\n",12); continue; }
        idxs.push_back(idx);
    }
    sort(idxs.begin(),idxs.end(),greater<int>());
    return idxs;
}

// ==================== AI ====================
int GameEngine::aiBlindChoice(int maxIdx) {
    if(maxIdx<=0) return 0;
    return rng()%maxIdx;
}
int GameEngine::strategicChoice(const Player& p) {
    if(p.hand.empty()) return 0;
    // 15% 随机防止被读牌
    if((int)(rng()%100)<15) return rng()%p.hand.size();
    // 优先考虑打出10（中盘触发顺路拐带抢牌，45%概率）
    for(size_t i=0;i<p.hand.size();++i){
        if(p.hand[i].rank==RANK_10 && !p.hand[i].isJoker){
            if(round>=4 && round<=14 && (int)(rng()%100)<45){
                return (int)i;
            }
        }
    }
    vector<pair<int,int>> iv;
    for(size_t i=0;i<p.hand.size();++i)
        iv.push_back({p.hand[i].getCompareValue(currentRule),(int)i});
    sort(iv.begin(),iv.end());
    int n=(int)p.hand.size();
    if(currentRule==BIG_WINS){
        // 前期（1-6局）: 打中高牌，保留最优
        // 中期（7-12局）: 打高牌，积极抢分
        // 后期（13-18局）: 打最强牌冲刺
        int topRange;
        if(round<=6)      topRange=max(1,n*2/5);
        else if(round<=12) topRange=max(1,n/3);
        else               topRange=max(1,n/5);
        int pos=n-1-(int)(rng()%topRange);
        return iv[max(0,pos)].second;
    } else {
        // SMALL_WINS: 打最小（最优）牌，保留大牌等待规则翻转
        if((int)(rng()%100)<70) return iv[0].second;
        return iv[(int)(rng()%max(1,n/4))].second;
    }
}
void GameEngine::strategicDiscard(Player& p, int count) {
    for(int k=0;k<count&&!p.hand.empty();++k){
        // 弃最差的牌；手牌较少时优先保留中间值，避免手牌失衡
        int wi=0; int wv=p.hand[0].getCompareValue(currentRule);
        bool bigHand=(int)p.hand.size()>4;
        for(size_t i=1;i<p.hand.size();++i){
            int v=p.hand[i].getCompareValue(currentRule);
            // 大手牌直接弃最差；小手牌同样弃最差（简单可靠）
            if((currentRule==BIG_WINS&&v<wv)||(currentRule==SMALL_WINS&&v>wv)){
                wv=v; wi=(int)i;
            }
        }
        // 如果手牌多且有10，跳过10（可能用于拐带）
        if(bigHand && p.hand[wi].rank==RANK_10 && !p.hand[wi].isJoker){
            // 再找次差的弃
            int wi2=-1; int wv2=INT_MAX;
            for(size_t i=0;i<p.hand.size();++i){
                if((int)i==wi) continue;
                int v=p.hand[i].getCompareValue(currentRule);
                if(wi2<0||(currentRule==BIG_WINS&&v<wv2)||(currentRule==SMALL_WINS&&v>wv2)){
                    wv2=v; wi2=(int)i;
                }
            }
            if(wi2>=0) wi=wi2;
        }
        p.hand.erase(p.hand.begin()+wi);
    }
}

// ==================== 计分 ====================
vector<int> GameEngine::computeScores(const vector<Card>& cards) {
    vector<int> scores(3,0);
    int v[3]; for(int i=0;i<3;++i) v[i]=cards[i].getCompareValue(currentRule);
    int ord[3]={0,1,2};
    sort(ord,ord+3,[&](int a,int b){
        return currentRule==BIG_WINS ? v[a]>v[b] : v[a]<v[b];
    });
    // 三张全同
    if(v[0]==v[1]&&v[1]==v[2]) return scores;
    if(v[ord[0]]==v[ord[1]]&&v[ord[1]]==v[ord[2]]) return scores;
    if(v[ord[0]]==v[ord[1]]){
        scores[ord[0]]=1; scores[ord[1]]=1;
    } else if(v[ord[1]]==v[ord[2]]){
        scores[ord[0]]=2;
    } else {
        scores[ord[0]]=2; scores[ord[1]]=1;
    }
    return scores;
}

// ==================== 连顺判断 ====================
// skipMask: 某玩家的牌被标记为isReturned则跳过连顺检查
bool GameEngine::isThreeConsecutive(const vector<Card>& cards, const vector<bool>& skipMask) {
    for(int i=0;i<3;++i) if(cards[i].isJoker) return false;
    for(int i=0;i<3;++i) if(skipMask[i]) return false; // 有收回牌则不触发
    vector<int> nums;
    for(int i=0;i<3;++i) nums.push_back(static_cast<int>(cards[i].rank));
    sort(nums.begin(),nums.end());
    if(nums[1]==nums[0]+1&&nums[2]==nums[1]+1) return true;
    return false;
}

// ==================== 补分 ====================
void GameEngine::applyBonusScore(bool twoTie, bool threeTie) {
    if(!twoTie&&!threeTie) return;
    int minS=players[0].score;
    for(int i=1;i<3;++i) if(players[i].score<minS) minS=players[i].score;
    int minCount=0, minIdx=-1;
    for(int i=0;i<3;++i) if(players[i].score==minS){ minCount++; minIdx=i; }
    if(minCount==1){
        int bonus=threeTie?2:1;
        players[minIdx].score+=bonus;
        cprint("  >>> [追加补分] "+players[minIdx].name+" 是唯一最低分者，额外 +"+to_string(bonus)+" 分\n",10);
    } else {
        cprint("  >>> [补分] 最低分并列，无人获得追加分\n",8);
    }
}

// ==================== 规则翻转 ====================
void GameEngine::handleRuleFlip(bool threeTie, bool twoTie) {
    bool doFlip=false;
    if(threeTie){
        doFlip=true;
        lastRoundTwoWayTie=false;
        cprint("  >>> [乾坤翻转] 三张同点！规则即将翻转！\n",14);
    } else if(twoTie&&lastRoundTwoWayTie){
        doFlip=true;
        lastRoundTwoWayTie=false;
        cprint("  >>> [连续两局两张同] 规则翻转！\n",14);
    } else {
        if(twoTie) lastRoundTwoWayTie=true;
        else        lastRoundTwoWayTie=false;
    }
    if(doFlip){
        currentRule=(currentRule==BIG_WINS)?SMALL_WINS:BIG_WINS;
        string newRule=(currentRule==BIG_WINS)?"【比大】":"【比小】";
        cprint("  >>> 新规则: "+newRule+"\n",14);
    }
}


// ==================== 出10机制（新版）====================
// 效果：出10者拿走另两人的牌；出10者自弃1张；顺时针下家盲弃出10者的1张
// 大王可在被盲弃时触发防御（N→N-1）
void GameEngine::perform10Mechanism(int tenPlayer,
        vector<Card>& tableCards, vector<int>& playedIdx) {

    cprint("\n  >>> [顺路拐带] "+players[tenPlayer].name+" 出了10，触发拐带！\n",14);

    // Step1: 出10者拿走另两人出的牌
    for(int i=0;i<3;++i){
        if(i!=tenPlayer) players[tenPlayer].addCard(tableCards[i]);
    }
    // 移除出10者自己的10
    players[tenPlayer].removeSpecificCard(tableCards[tenPlayer]);
    // 另外两人的牌已由tableCards记录，稍后主循环会从hand中删除（仅针对非tenPlayer）

    cprint("  "+players[tenPlayer].name+" 已获得另外两人的出牌。\n",11);

    // Step2: 出10者自弃1张（只有自己知道）
    cprint("\n  [Step 2] "+players[tenPlayer].name+" 需自选弃掉1张牌\n",11);
    if(players[tenPlayer].isHuman){
        int di=getDiscardChoice(players[tenPlayer],"请选择要弃掉的1张牌（仅你可见）");
        players[tenPlayer].removeCard(di);
        cprint("  自弃完成。（他人看不见弃了什么）\n",8);
    } else {
        // AI弃牌（弃最差的）
        strategicDiscard(players[tenPlayer],1);
        cprint("  "+players[tenPlayer].name+" 已弃掉1张牌。\n",8);
    }

    // Step3: 顺时针下家盲弃出10者的1张
    int nextPlayer=(tenPlayer+1)%3;
    cprint("\n  [Step 3] "+players[nextPlayer].name+" 需盲选一个编号，弃掉 "+
           players[tenPlayer].name+" 的1张牌\n",11);
    cprint("  （"+players[nextPlayer].name+" 看不见对方手牌，只知道有 "+
           to_string((int)players[tenPlayer].hand.size())+" 张）\n",8);

    int chosen=-1;
    if(players[nextPlayer].isHuman){
        // 人类盲选：不显示tenPlayer手牌
        setColor(11);
        cout<<"  请输入1~"<<players[tenPlayer].hand.size()<<" 中任意编号（盲选）: ";
        resetColor();
        chosen=getMenuChoice(1,(int)players[tenPlayer].hand.size())-1;
    } else {
        chosen=aiBlindChoice((int)players[tenPlayer].hand.size());
        cprint("  "+players[nextPlayer].name+" 盲选了一个编号...\n",8);
    }

    // 大王防御：检查tenPlayer是否可触发大王防御
    chosen=performBigJokerDefense(tenPlayer, chosen);

    // 公开展示被弃的牌（被人操作的弃牌需全员可见）
    Card discardCard=players[tenPlayer].hand[chosen];
    cprint("\n  >>> [公开弃牌] ",14);
    discardCard.printColored();
    cprint(" 被 "+players[nextPlayer].name+" 选中弃掉！（全员可见）\n",11);
    players[tenPlayer].removeCard(chosen);
    cprint("  弃牌完成。\n",8);
}


// ==================== 5号牌：归还待处理 ====================
void GameEngine::processFiveReturns() {
    for(int i=0;i<3;++i){
        if(fiveReturnPending[i]){
            // 将收回的牌标记为isReturned后加入手牌
            Card rc=fiveReturnCard[i];
            rc.isReturned=true;
            players[i].addCard(rc);
            fiveReturnPending[i]=false;
            cprint("  >>> [5号牌收回] "+players[i].name+" 收回了上回合打出的牌（标记为*，打出后不触发连顺）\n",10);
        }
    }
}

// ==================== 5号牌：检查单人激活条件 ====================
// pIdx: 玩家索引, playedIdx: 该玩家本轮打出的牌在hand中的原始索引（打出前的索引）
// table: 本轮三张桌面牌
bool GameEngine::check5CardActivation(int pIdx, int playedIdx, const vector<Card>& table) {
    // 条件1: 三张各不同
    int v[3]; for(int i=0;i<3;++i) v[i]=table[i].getCompareValue(currentRule);
    if(v[0]==v[1]||v[1]==v[2]||v[0]==v[2]) return false;
    // 条件2: 该玩家不是最大
    int myV=v[pIdx];
    int maxV=*max_element(v,v+3);
    if(currentRule==SMALL_WINS) maxV=*min_element(v,v+3); // 比小时"最优"是最小值
    if(myV==maxV) return false; // 是最优者，不能激活
    // 条件3: 手中有额外的5可用（本轮打出的牌本身可以是5，但需另有一张5）
    // 注意：打出的牌已从hand中记录为tableCards，此时hand中如果有5则可用
    // 我们在playRound中调用时，打出的牌还未从hand删除（只是记录了index）
    // 所以需要排除打出的那张的index
    int fiveIdx=players[pIdx].findFiveCard(playedIdx);
    if(fiveIdx<0) return false;
    // 条件4: 大王/小王持有者不能激活（已通过maxV判断，joker compare value极大/极小必为最优）
    return true;
}

void GameEngine::perform5CardActivations(const vector<Card>& table,
        const vector<int>& playedIdx, vector<bool>& activated) {
    activated.assign(3,false);
    for(int i=0;i<3;++i){
        if(!check5CardActivation(i,playedIdx[i],table)) continue;
        // 询问是否激活
        bool doActivate=false;
        if(players[i].isHuman){
            cout<<endl;
            cprint("  [5号牌] 你满足激活条件！你本轮打出了 ",11);
            table[i].printColored();
            cprint("，手中有额外的5可消耗。\n",11);
            doActivate=getYesNo("是否激活5号牌，消耗一张5，将本轮打出的牌收回？");
        } else {
            // AI策略：若打出的牌比较值在前1/3（有价值），则激活
            int myV=table[i].getCompareValue(currentRule);
            int allV[3]; for(int j=0;j<3;++j) allV[j]=table[j].getCompareValue(currentRule);
            sort(allV,allV+3);
            int threshold=allV[2]; // 最大值
            // 策略AI：打出的牌是最差的1/3时不激活（没必要救）
            if(players[i].isStrategic){
                doActivate=(currentRule==BIG_WINS)?(myV>=allV[1]):(myV<=allV[1]);
            }
            if(doActivate) cprint("  >>> "+players[i].name+" 激活了5号牌！\n",10);
        }
        if(doActivate){
            // 消耗手中的5（排除打出的那张）
            int fiveIdx=players[i].findFiveCard(playedIdx[i]);
            players[i].removeCard(fiveIdx);
            // 记录待归还（下回合开始前归还）
            fiveReturnPending[i]=true;
            fiveReturnCard[i]=table[i];
            activated[i]=true;
            cprint("  >>> [5号牌] "+players[i].name+" 消耗了5号牌，本轮打出的牌将于下回合开始前收回。\n",10);
        }
    }
}

// ==================== 连顺抽牌 ====================
// 可见性规则：
//   抽取人：看不见对方手牌，只知道张数，盲选编号
//   被抽人：能看见自己被拿走了哪张
//   旁观者：只知道动作发生，不知道内容
void GameEngine::performDrawSequence() {
    cprint("\n  >>> [连顺抽牌] 三张连续！各从下家手中盲选1张！\n",14);

    // 起手顺序：当前总分最高者先行
    int startIdx=0; int maxScore=-999;
    for(int i=0;i<3;++i)
        if(players[i].score>maxScore){ maxScore=players[i].score; startIdx=i; }

    vector<Card> drawnCards(3);
    vector<bool> hasDrawn(3,false);

    for(int k=0;k<3;++k){
        int fromIdx=(startIdx+k)%3;
        int targetIdx=(fromIdx+1)%3;
        if(players[targetIdx].hand.empty()){
            cprint("  "+players[targetIdx].name+" 手牌为空，跳过抽牌。\n",8);
            continue;
        }

        // 小王：抽取人可以偷窥
        performSmallJokerPeek(fromIdx, targetIdx);

        int chosen=-1;
        int targetSize=(int)players[targetIdx].hand.size();

        if(players[fromIdx].isHuman){
            setColor(11);
            cout<<"  你从 "<<players[targetIdx].name
                <<" 的手牌中盲选1张（共 "<<targetSize<<" 张，背面朝下）"<<endl;
            resetColor();
            chosen=getHumanChoice(targetSize,"请输入编号盲选");
        } else {
            chosen=aiBlindChoice(targetSize);
            cprint("  "+players[fromIdx].name+" 盲选了一个编号...\n",8);
        }

        // 大王防御：目标玩家可触发
        chosen=performBigJokerDefense(targetIdx, chosen);

        // 执行抽牌
        drawnCards[fromIdx]=players[targetIdx].hand[chosen];
        players[targetIdx].hand.erase(players[targetIdx].hand.begin()+chosen);
        hasDrawn[fromIdx]=true;

        // 可见性规则：
        //   抽取人若为人类 → 告知自己抽到了什么（仅本人可见）
        //   被抽人若为人类 → 告知被拿走了什么（仅本人可见）
        //   旁观者 → 只知道谁从谁那里抽了一张（内容不公开）
        if(players[fromIdx].isHuman){
            cprint("  >>> 你从 "+players[targetIdx].name+" 处抽到了: ",11);
            drawnCards[fromIdx].printColored();
            cprint(" （仅你可见）\n",11);
        } else {
            cprint("  >>> "+players[fromIdx].name+" 从 "+players[targetIdx].name+" 处抽走了1张。",8);
            cout<<endl;
        }
        if(players[targetIdx].isHuman){
            cprint("  >>> 你的 ",12);
            drawnCards[fromIdx].printColored();
            cprint(" 被 "+players[fromIdx].name+" 抽走了。\n",12);
        }
    }

    // 统一加入手牌
    for(int i=0;i<3;++i)
        if(hasDrawn[i]) players[i].addCard(drawnCards[i]);

    cprint("  >>> 抽牌完毕，各自将牌加入手中。\n",10);
}


// ==================== 大王防御（N→N-1）====================
// targetPlayer: 被操作的玩家, chosenIdx: 对方选择的0-based索引
// 返回实际生效的索引（可能被偏移）
int GameEngine::performBigJokerDefense(int targetPlayer, int chosenIdx) {
    if(!players[targetPlayer].canUseBigJoker()) return chosenIdx;
    int sz=(int)players[targetPlayer].hand.size();
    if(sz<=1) return chosenIdx; // 只剩1张无法偏移

    bool doDefense=false;
    if(players[targetPlayer].isHuman){
        int displayChosen=chosenIdx+1; // 转为1-based显示
        cprint("\n  [大王] 对方选择了你手牌中的第"+to_string(displayChosen)+
               "号（你已用"+to_string(players[targetPlayer].bigJokerUses)+"/2次大王技能）\n",14);
        doDefense=getYesNo("是否使用大王将目标偏移为第"+
            to_string(chosenIdx==0?(int)sz:chosenIdx)+"号？");
    } else {
        // AI：50%概率使用大王
        doDefense=(rng()%2==0);
        if(doDefense) cprint("  "+players[targetPlayer].name+" 使用了大王防御！\n",14);
    }

    if(doDefense){
        players[targetPlayer].bigJokerUses++;
        int newIdx=(chosenIdx==0)?(sz-1):(chosenIdx-1);
        cprint("  >>> [大王] 目标偏移：第"+to_string(chosenIdx+1)+"号 → 第"+
               to_string(newIdx+1)+"号\n",14);
        return newIdx;
    }
    return chosenIdx;
}

// ==================== 小王偷窥 ====================
// peekPlayer: 抽取人（手持小王）, targetPlayer: 被抽的人
void GameEngine::performSmallJokerPeek(int peekPlayer, int targetPlayer) {
    if(!players[peekPlayer].canUseSmallJoker()) return;

    bool doPeek=false;
    if(players[peekPlayer].isHuman){
        cprint("  [小王] 你持有小王（已用"+to_string(players[peekPlayer].smallJokerUses)+
               "/1次）\n",14);
        doPeek=getYesNo("是否使用小王偷窥 "+players[targetPlayer].name+" 的手牌？");
    } else {
        // 策略AI：总是使用小王偷窥
        doPeek=players[peekPlayer].isStrategic;
        if(doPeek) cprint("  "+players[peekPlayer].name+" 使用了小王偷窥！\n",14);
    }

    if(doPeek){
        players[peekPlayer].smallJokerUses++;
        if(players[peekPlayer].isHuman){
            cprint("\n  [小王偷窥] "+players[targetPlayer].name+" 的手牌（共"+
                   to_string((int)players[targetPlayer].hand.size())+"张）：\n",14);
            players[targetPlayer].showHand();
            cprint("  （看完后请记住，选择编号后这些信息不再显示）\n",8);
            pauseEnter();
        }
    }
}


// ==================== playRound ====================
void GameEngine::playRound() {
    CLEAR_SCREEN;
    showHeader();
    showStatus();

    // Step0: 处理5号牌待归还
    processFiveReturns();

    // Step1: 各玩家出牌
    vector<Card> tableCards(3);
    vector<int>  playedIdx(3);

    for(int i=0;i<3;++i){
        if(players[i].isHuman){
            cprint("  === 你的手牌 ===\n",11);
            players[i].showHand();
            int idx=getHumanChoice((int)players[i].hand.size(),"请选择出哪张牌");
            playedIdx[i]=idx;
            tableCards[i]=players[i].hand[idx];
        }
    }
    for(int i=0;i<3;++i){
        if(!players[i].isHuman){
            int idx=players[i].isStrategic?strategicChoice(players[i])
                                           :(int)(rng()%players[i].hand.size());
            playedIdx[i]=idx;
            tableCards[i]=players[i].hand[idx];
        }
    }

    // Step2: 亮牌
    cout<<endl; printDSep();
    cprint("  === 亮牌 ===\n",14);
    for(int i=0;i<3;++i){
        setColor(11); cout<<"  "<<players[i].name<<" 出了: "; resetColor();
        tableCards[i].printColored();
        setColor(8); cout<<"  (比较值: "<<tableCards[i].getCompareValue(currentRule)<<")";
        resetColor(); cout<<endl;
    }
    printDSep();

    // Step3: 检查大小王同台
    bool hasBig=false, hasSml=false;
    for(int i=0;i<3;++i){
        if(tableCards[i].isBigJoker()) hasBig=true;
        if(tableCards[i].isSmallJoker()) hasSml=true;
    }
    if(hasBig&&hasSml) cprint("  >>> [乾坤大挪移] 大王小王同台！气氛异常紧张...\n",14);

    // Step4: 检查出10（优先级最高）
    int tenCount=0, tenPlayer=-1;
    for(int i=0;i<3;++i) if(tableCards[i].isTen()){ tenCount++; tenPlayer=i; }

    bool scoreSkipped=false;
    if(tenCount==1){
        perform10Mechanism(tenPlayer, tableCards, playedIdx);
        scoreSkipped=true;
    }

    // Step5: 从手牌移除打出的牌
    // tenPlayer的牌在perform10里已处理（removeSpecificCard了10，并弃了2张）
    // 其余玩家或tenPlayer==0时：移除对应hand中的牌
    for(int i=0;i<3;++i){
        if(tenCount==1 && i==tenPlayer) continue; // tenPlayer已在函数里处理
        // 注意playedIdx[i]可能因手牌变化(5号牌归还在round开始前)而偏移，
        // 但5号牌归还是在出牌前完成的，所以此时索引仍有效
        if(playedIdx[i]<(int)players[i].hand.size()){
            players[i].hand.erase(players[i].hand.begin()+playedIdx[i]);
        }
    }

    // Step6: 检查连顺（仅非第18局）
    // skipMask: 若tableCards[i].isReturned则跳过（5号牌收回的牌不触发连顺）
    vector<bool> skipMask(3,false);
    for(int i=0;i<3;++i) skipMask[i]=tableCards[i].isReturned;

    bool consecutiveTriggered=false;
    if(round!=18 && isThreeConsecutive(tableCards,skipMask)){
        consecutiveTriggered=true;
    }

    // Step7: 检查5号牌激活（仅在无连顺、无出10时可激活）
    vector<bool> fiveActivated(3,false);
    if(!scoreSkipped && !consecutiveTriggered){
        perform5CardActivations(tableCards, playedIdx, fiveActivated);
    }

    // Step8: 执行连顺抽牌（出10后也可触发；5号牌激活时不触发）
    bool anyFiveActivated=false;
    for(int i=0;i<3;++i) if(fiveActivated[i]){ anyFiveActivated=true; break; }
    if(consecutiveTriggered && !anyFiveActivated){
        performDrawSequence();
    }

    // Step9: 计分（出10触发局不计分）
    vector<int> roundScores(3,0);
    bool threeWayTie=false, twoWayTie=false;
    if(!scoreSkipped){
        roundScores=computeScores(tableCards);
        for(int i=0;i<3;++i) players[i].score+=roundScores[i];
        // 判断平局类型
        int r0=tableCards[0].getCompareValue(currentRule);
        int r1=tableCards[1].getCompareValue(currentRule);
        int r2=tableCards[2].getCompareValue(currentRule);
        if(r0==r1&&r1==r2) threeWayTie=true;
        else if(r0==r1||r1==r2||r0==r2) twoWayTie=true;
    }

    // Step10: 补分（出10局不触发）
    if(!scoreSkipped){
        applyBonusScore(twoWayTie, threeWayTie);
    }

    // Step11: 规则翻转
    if(!scoreSkipped){
        handleRuleFlip(threeWayTie, twoWayTie);
    }

    // Step12: 本局积分显示
    cout<<endl; printSep();
    cprint("  本局积分: ",11);
    for(int i=0;i<3;++i){
        setColor(14); cout<<players[i].name; resetColor();
        cout<<" "; setColor(10); cout<<"+"<<roundScores[i]; resetColor();
        cout<<"  ";
    }
    if(scoreSkipped) cprint("（本局不计分）",8);
    cout<<endl;
    cprint("  当前总分: ",11);
    for(int i=0;i<3;++i){
        setColor(14); cout<<players[i].name; resetColor();
        cout<<" "; setColor(11); cout<<players[i].score; resetColor();
        cout<<"  ";
    }
    cout<<endl; printSep();

    pauseEnter();
}


// ==================== 加赛 ====================
// 参与者重新发5张牌，禁用所有特殊效果，积分独立结算
void GameEngine::playTiebreaker(vector<int>& tied) {
    CLEAR_SCREEN;
    showHeader();
    cprint("  ══════════ 加赛开始！ ══════════\n",14);
    cprint("  参与加赛: ",11);
    for(int i:tied){ setColor(14); cout<<players[i].name<<"  "; resetColor(); }
    cout<<endl;
    cprint("  规则：每人5张，继承当前比大/比小，禁用所有特殊效果\n",8);
    cout<<endl;

    while(true){
        // 保存并重置加赛积分
        vector<int> tbScore(3,0); // 加赛小分

        // 发5张牌
        for(int i:tied) players[i].hand.clear();
        initDeck(); shuffleDeck();
        int cardIdx=0;
        for(int r=0;r<5;++r)
            for(int i:tied)
                players[i].addCard(deck[cardIdx++]);

        // 加赛5局
        for(int tb=1;tb<=5;++tb){
            CLEAR_SCREEN;
            showHeader();
            cprint("  [加赛] 第"+to_string(tb)+"/5局   规则: ",11);
            if(currentRule==BIG_WINS) cprint("比大\n",12);
            else                      cprint("比小\n",10);
            cprint("  加赛积分: ",11);
            for(int i:tied){
                setColor(14); cout<<players[i].name; resetColor();
                cout<<" "; setColor(11); cout<<tbScore[i]; resetColor();
                cout<<"  ";
            }
            cout<<endl<<endl;

            // 出牌
            vector<Card>  tbTable(3);
            vector<int>   tbIdx(3,-1);
            for(int i:tied){
                if(players[i].isHuman){
                    cprint("  === 你的手牌 ===\n",11);
                    players[i].showHand();
                    int c=getHumanChoice((int)players[i].hand.size(),"请选择出哪张牌");
                    tbIdx[i]=c; tbTable[i]=players[i].hand[c];
                } else {
                    int c=(int)(rng()%players[i].hand.size());
                    tbIdx[i]=c; tbTable[i]=players[i].hand[c];
                }
            }
            // 亮牌
            cout<<endl; printDSep();
            cprint("  === 亮牌 ===\n",14);
            for(int i:tied){
                setColor(11); cout<<"  "<<players[i].name<<": "; resetColor();
                tbTable[i].printColored(); cout<<endl;
            }
            printDSep();

            // 计分（仅参与加赛的玩家之间，其余补0）
            vector<Card> allTable(3);
            for(int i:tied) allTable[i]=tbTable[i];
            // 未参与的玩家用中性牌填充（不影响）
            vector<int> scoresThisRound(3,0);
            if(tied.size()==2){
                int a=tied[0],b=tied[1];
                int va=tbTable[a].getCompareValue(currentRule);
                int vb=tbTable[b].getCompareValue(currentRule);
                if(va==vb){ scoresThisRound[a]=1; scoresThisRound[b]=1; }
                else if((currentRule==BIG_WINS&&va>vb)||(currentRule==SMALL_WINS&&va<vb)){
                    scoresThisRound[a]=2;
                } else {
                    scoresThisRound[b]=2;
                }
            } else if(tied.size()==3){
                scoresThisRound=computeScores(tbTable);
            }
            for(int i:tied) tbScore[i]+=scoresThisRound[i];

            // 移除打出的牌
            for(int i:tied)
                if(tbIdx[i]<(int)players[i].hand.size())
                    players[i].hand.erase(players[i].hand.begin()+tbIdx[i]);

            // 显示本局结果
            cprint("  本局: ",11);
            for(int i:tied){
                setColor(14); cout<<players[i].name; resetColor();
                cout<<" "; setColor(10); cout<<"+"<<scoresThisRound[i]; resetColor();
                cout<<"  ";
            }
            cout<<endl;
            pauseEnter();
        }

        // 加赛5局结束，检查加赛积分
        CLEAR_SCREEN;
        showHeader();
        cprint("  [加赛结果]\n",14);
        int maxTb=-1;
        for(int i:tied) if(tbScore[i]>maxTb) maxTb=tbScore[i];
        vector<int> stillTied;
        for(int i:tied) if(tbScore[i]==maxTb) stillTied.push_back(i);

        for(int i:tied){
            setColor(14); cout<<"  "<<players[i].name; resetColor();
            cout<<" 加赛小分: "; setColor(11); cout<<tbScore[i]; resetColor(); cout<<endl;
        }

        if(stillTied.size()==1){
            cprint("  >>> 加赛胜者: "+players[stillTied[0]].name+"\n",14);
            // 更新tied为已决出的
            tied=stillTied;
            pauseEnter();
            break;
        } else {
            cprint("  >>> 仍然平局，继续加赛！\n",12);
            tied=stillTied;
            pauseEnter();
        }
    }
}

// ==================== 检查结束条件 ====================
bool GameEngine::checkEndCondition(vector<int>& tied) {
    if(gameMode==0) return false; // 单局模式不在中途检查
    // 检查是否有人达标
    bool anyReached=false;
    for(int i=0;i<3;++i) if(players[i].score>=targetScore){ anyReached=true; break; }
    if(!anyReached) return false;

    // 有人达标，检查同分
    int maxS=players[0].score;
    for(int i=1;i<3;++i) if(players[i].score>maxS) maxS=players[i].score;
    vector<int> topPlayers;
    for(int i=0;i<3;++i) if(players[i].score==maxS) topPlayers.push_back(i);

    if(topPlayers.size()==1) return true; // 唯一最高分，直接结束
    // 并列最高，需加赛
    tied=topPlayers;
    return true;
}

// ==================== startNewGame ====================
void GameEngine::startNewGame() {
    // 模式选择
    CLEAR_SCREEN; showHeader();
    cprint("  请选择游戏模式：\n",11);
    cout<<"  1. 单局模式（18局，按总分排名）\n";
    cout<<"  2. 达标分模式（先达到目标分者结算）\n";
    cprint("  请输入 (1/2): ",11);
    gameMode=getMenuChoice(1,2)-1;

    if(gameMode==1){
        CLEAR_SCREEN; showHeader();
        cprint("  请选择目标分：\n",11);
        cout<<"  1. 30 分\n  2. 60 分\n  3. 100 分\n  4. 150 分\n";
        cprint("  请输入 (1~4): ",11);
        int tc=getMenuChoice(1,4);
        int tscores[]={30,60,100,150};
        targetScore=tscores[tc-1];
        cprint("  目标分设定为: "+to_string(targetScore)+" 分\n",14);
        pauseEnter();
    }

    // 初始化（非续场才清零积分）
    if(!consecutiveGame){
        for(int i=0;i<3;++i){ players[i].score=0; players[i].resetJokerUses(); }
        sceneCount=1;
    }
    for(int i=0;i<3;++i) players[i].hand.clear();
    round=1; lastRoundTwoWayTie=false;
    for(int i=0;i<3;++i) fiveReturnPending[i]=false;
    initDeck(); shuffleDeck(); dealCards(18);

    // 发牌后先让人类玩家查看所有手牌，再选规则
    CLEAR_SCREEN; showHeader();
    cprint("  === 发牌完成！请先查看您的手牌，再决定规则 ===\n",14);
    for(int i=0;i<3;++i){
        if(players[i].isHuman){
            cout<<endl;
            cprint("  "+players[i].name+" 的初始手牌（共"+to_string((int)players[i].hand.size())+"张）：\n",11);
            players[i].showHand();
        }
    }
    pauseEnter();

    // 黑桃A选规则（续场跳过，补分）
    int chooser=-1;
    for(int i=0;i<3;++i) if(players[i].hasSpadeA()){ chooser=i; break; }

    CLEAR_SCREEN; showHeader();
    if(!consecutiveGame){
        if(chooser==0){
            cprint("  你持有黑桃A，请选择初始规则：\n",11);
            cout<<"  1. 比大（K最大，A最小）\n  2. 比小（A最优，K最大）\n";
            cprint("  请输入 (1/2): ",11);
            int c=getMenuChoice(1,2);
            currentRule=(c==1)?BIG_WINS:SMALL_WINS;
        } else {
            currentRule=(GameRule)(rng()%2);
            cprint("  "+players[chooser].name+" 持有黑桃A，随机选择了: ",11);
            cprint((currentRule==BIG_WINS)?"比大\n":"比小\n",14);
            pauseEnter();
        }
    } else {
        // 续场：黑桃A持有者+1分
        if(chooser>=0){
            players[chooser].score++;
            cprint("  续场："+players[chooser].name+" 持有黑桃A，获得 +1 分补偿（无规则选择权）\n",10);
            pauseEnter();
        }
    }

    consecutiveGame=false; // 下次默认非续场，由mainMenu逻辑控制

    // 主游戏循环
    for(; round<=18; ++round){
        playRound();
        // 达标分模式：每局后检查
        if(gameMode==1){
            vector<int> tied;
            if(checkEndCondition(tied)){
                CLEAR_SCREEN; showHeader();
                if(tied.empty()){
                    cprint("  ★ 有玩家达标！游戏结束！\n",14);
                    showFinalRank();
                } else {
                    cprint("  ★ 有玩家达标但分数并列，进入加赛！\n",14);
                    pauseEnter();
                    playTiebreaker(tied);
                    cprint("  加赛结束！\n",14);
                    showFinalRank();
                }
                pauseEnter();
                return;
            }
        }
        if(round==18) break;
    }

    // 18局结束
    CLEAR_SCREEN; showHeader();
    if(gameMode==0){
        cprint("  ══ 单局结束 ══\n",14);
        showFinalRank();
        pauseEnter();
    } else {
        // 达标分模式：18局内无人达标，继续下一场
        cprint("  18局结束，尚无人达标，继续下一场！\n",11);
        cprint("  积分与规则继承，重新发牌。\n",8);
        pauseEnter();
        sceneCount++;
        consecutiveGame=true;
        for(int i=0;i<3;++i) players[i].resetJokerUses();
        startNewGame();
    }
}


// ==================== mainMenu ====================
void GameEngine::mainMenu() {
    while(true){
        CLEAR_SCREEN;
        showHeader();
        printDSep();
        cprint("              主菜单\n\n",14);
        cprint("        1. 开始新游戏\n",15);
        cprint("        2. 查看游戏规则\n",15);
        cprint("        0. 退出游戏\n\n",8);
        printDSep();
        cprint("  请选择: ",11);
        int c=getMenuChoice(0,2);
        if(c==0){
            CLEAR_SCREEN; showHeader();
            cprint("  感谢游玩《三雄争锋》！再见！\n",14);
            break;
        } else if(c==1){
            consecutiveGame=false;
            startNewGame();
        } else {
            showRules();
        }
    }
}

// ==================== main ====================
int main(){
#ifdef _WIN32
    SetConsoleOutputCP(936);
    SetConsoleCP(936);
    // 设置控制台窗口大小
    system("mode con cols=70 lines=40");
#endif
    hideCursor(true);
    GameEngine game;
    game.mainMenu();
    hideCursor(false);
    return 0;
}
