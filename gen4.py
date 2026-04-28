# -*- coding: utf-8 -*-
"""BP4: 输入方法 + AI + 计分 + 连顺判断"""
code = r"""
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

"""
with open(r'd:\Users\ymx36\Desktop\三雄争锋游戏\三雄争锋v2.cpp','a',encoding='gbk') as f:
    f.write(code)
print("BP4 OK - 输入/AI/计分/连顺/补分/翻转 写入完成")
