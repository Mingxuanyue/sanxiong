# -*- coding: utf-8 -*-
"""BP3: 构造函数 + 发牌 + showHeader/showStatus/showRules"""
code = r"""
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

"""
with open(r'd:\Users\ymx36\Desktop\三雄争锋游戏\三雄争锋v2.cpp','a',encoding='gbk') as f:
    f.write(code)
print("BP3 OK - 构造/发牌/showHeader/showStatus/showRules 写入完成")
