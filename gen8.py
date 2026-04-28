# -*- coding: utf-8 -*-
"""BP8: playRound 完整实现"""
code = r"""
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

"""
with open(r'd:\Users\ymx36\Desktop\三雄争锋游戏\三雄争锋v2.cpp','a',encoding='gbk') as f:
    f.write(code)
print("BP8 OK - playRound完整实现 写入完成")
