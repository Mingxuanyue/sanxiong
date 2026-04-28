# -*- coding: utf-8 -*-
"""BP6: 5号牌机制 + 连顺抽牌（修正可见性）"""
code = r"""
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

"""
with open(r'd:\Users\ymx36\Desktop\三雄争锋游戏\三雄争锋v2.cpp','a',encoding='gbk') as f:
    f.write(code)
print("BP6 OK - 5号牌机制/连顺抽牌 写入完成")
