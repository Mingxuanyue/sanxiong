# -*- coding: utf-8 -*-
"""BP9: 加赛 + checkEndCondition + startNewGame"""
code = r"""
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

"""
with open(r'd:\Users\ymx36\Desktop\三雄争锋游戏\三雄争锋v2.cpp','a',encoding='gbk') as f:
    f.write(code)
print("BP9 OK - 加赛/checkEnd/startNewGame 写入完成")
