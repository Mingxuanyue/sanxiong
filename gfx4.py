# -*- coding: utf-8 -*-
"""GFX4: GameEngine构造 + 牌堆 + AI + 计分 + 规则"""
code = r"""
// ===== 构造 + 初始化 =====
GameEngine::GameEngine()
    :round(1),currentRule(BIG_WINS),gameMode(0),targetScore(60),
     consecutiveGame(false),sceneCount(1),lastRoundTwoWayTie(false),
     tableRevealed(false)
{
    unsigned seed=(unsigned)chrono::steady_clock::now().time_since_epoch().count();
    rng.seed(seed);
    for(int i=0;i<3;++i){ fiveReturnPending[i]=false; }
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

// ===== 小概率动态补分 =====
void GameEngine::applyBonusScore(){
    // 约12%概率触发
    if((int)(rng()%100)<12){
        int lucky=(int)(rng()%3);
        players[lucky].score++;
        addMsg("[动态补分] "+players[lucky].name+" 获得随机+1分奖励！");
        // 视觉提示
        BeginBatchDraw();
        renderGameScreen();
        dtC(WIN_W/2,WIN_H/2-60,"[动态补分] 随机+1分！",C_GOLD,26,true);
        EndBatchDraw();
        Sleep(1200);
    }
}

// ===== 规则翻转 =====
void GameEngine::handleRuleFlip(const vector<Card>& cards){
    // 三张全同：清除翻转标记
    int v[3]; for(int i=0;i<3;++i) v[i]=cards[i].getCompareValue(currentRule);
    if(v[0]==v[1]&&v[1]==v[2]){ lastRoundTwoWayTie=false; return; }
    // 两张相同（且非全同）：记录/翻转
    int cnt=0;
    if(v[0]==v[1]||v[1]==v[2]||v[0]==v[2]) cnt=2;
    if(cnt==2){
        if(lastRoundTwoWayTie){
            // 连续两次两张同 → 规则翻转，小概率
            if((int)(rng()%100)<35){
                currentRule=(currentRule==BIG_WINS)?SMALL_WINS:BIG_WINS;
                addMsg("[规则反转] 连续两次两张同！规则变为"+
                    string(currentRule==BIG_WINS?"比大":"比小")+"！");
                BeginBatchDraw();
                renderGameScreen();
                dtC(WIN_W/2,WIN_H/2-60,
                    (currentRule==BIG_WINS?"[规则反转] 现在比大！":"[规则反转] 现在比小！"),
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
    // 中盘考虑出10
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
"""
with open(r'd:\Users\ymx36\Desktop\三雄争锋游戏\三雄争锋v3.cpp','a',encoding='gbk') as f:
    f.write(code)
print("GFX4 OK - 游戏逻辑核心写入完成")
