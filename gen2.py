# -*- coding: utf-8 -*-
"""BP2: Player类 + GameEngine成员声明"""
code = r"""
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

"""
with open(r'd:\Users\ymx36\Desktop\三雄争锋游戏\三雄争锋v2.cpp','a',encoding='gbk') as f:
    f.write(code)
print("BP2 OK - Player类/GameEngine声明 写入完成")
