# -*- coding: utf-8 -*-
"""GFX3: Card类 + Player类 + GameEngine类声明"""
code = r"""
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
        if(isJoker) return (rank==RANK_BIG_JOKER)?2000:1900;
        int v=static_cast<int>(rank);
        if(rule==BIG_WINS){
            // A最小K最大
            if(rank==RANK_A) return 1;
            return v;
        } else {
            // SMALL_WINS: A最优(最小比较值)，K最大(最差)
            if(rank==RANK_A) return 1;
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
    void applyBonusScore();
    void handleRuleFlip(const vector<Card>& cards);

    // AI
    int aiBlindChoice(int maxIdx);
    int strategicChoice(const Player& p);
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
    void playTiebreaker(vector<int>& tied);
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
    int  guiSelectCard(int playerIdx, const string& prompt);
    int  guiBlindSelect(int playerIdx, const string& prompt, int maxN);
    void guiInfo(const string& title, const string& body);
    bool guiYesNo(const string& title, const string& body);
    vector<int> guiSelectTwo(int playerIdx, const string& prompt);

    // ===== 菜单 =====
    void showMainMenu();
    void showRulesScreen();
    int  showModeSelect();
};

// 全局游戏引擎指针（供各屏幕函数访问）
GameEngine* g_eng = nullptr;
"""
with open(r'd:\Users\ymx36\Desktop\三雄争锋游戏\三雄争锋v3.cpp','a',encoding='gbk') as f:
    f.write(code)
print("GFX3 OK - 数据结构+类声明写入完成")
