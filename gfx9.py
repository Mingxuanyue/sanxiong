# -*- coding: utf-8 -*-
"""GFX9: 加赛 + checkEnd + startNewGame + showFinalRank"""
code = r"""
// ===== 显示最终排名 =====
void GameEngine::showFinalRank(){
    // 排序
    int ord[3]={0,1,2};
    sort(ord,ord+3,[this](int a,int b){ return players[a].score>players[b].score; });
    const char* medals[3]={"冠军","亚军","季军"};
    COLORREF cols[3]={C_GOLD,C_SILVER,RGB(180,100,50)};

    int pw=560, ph=360, px=(WIN_W-pw)/2, py=(WIN_H-ph)/2;
    BeginBatchDraw();
    renderGameScreen();
    setlinecolor(RGB(0,0,0)); setfillcolor(RGB(0,0,0));
    for(int yy=0;yy<WIN_H;yy+=3) line(0,yy,WIN_W,yy);
    fillRR(px,py,pw,ph,14,C_PANEL_D,C_GOLD,3);
    dtC(px+pw/2,py+32,"游戏结束！最终排名",C_GOLD,24,true);
    setlinecolor(C_GOLD); line(px+20,py+58,px+pw-20,py+58);
    for(int k=0;k<3;++k){
        int i=ord[k];
        char buf[64]; sprintf(buf,"%s  %s   %d 分",medals[k],players[i].name.c_str(),players[i].score);
        dtC(px+pw/2, py+90+k*60, buf, cols[k], 22, k==0);
    }
    dtC(px+pw/2,py+ph-40,"感谢游玩《三雄争锋》！",C_TEXT,16,false);
    dtC(px+pw/2,py+ph-18,"[ 点击返回主菜单 ]",C_DIM,13,false);
    EndBatchDraw();
    ExMessage mm;
    while(true){ if(peekmessage(&mm,EX_MOUSE)&&mm.message==WM_LBUTTONUP) break; Sleep(16); }
}

// ===== 加赛 =====
void GameEngine::playTiebreaker(vector<int>& tied){
    while(true){
        // 发5张
        for(int i:tied) players[i].hand.clear();
        initDeck(); shuffleDeck();
        int ci=0;
        for(int r=0;r<5;++r) for(int i:tied) players[i].addCard(deck[ci++]);

        vector<int> tbScore(3,0);
        for(int tb=1;tb<=5;++tb){
            tableCards.clear(); tableCards.resize(3);
            playedIdx.assign(3,-1);
            tableRevealed=false;

            // AI出牌
            for(int i:tied) if(!players[i].isHuman){
                int c=(int)(rng()%players[i].hand.size());
                playedIdx[i]=c; tableCards[i]=players[i].hand[c];
            }
            // 人类出牌
            bool humanIn=false; for(int i:tied) if(players[i].isHuman) humanIn=true;
            if(humanIn){
                // 简单重用guiSelectCard
                int h=guiSelectCard(0,"[加赛第"+to_string(tb)+"/5局] 请选择出牌");
                if(h<0) h=0;
                playedIdx[0]=h; tableCards[0]=players[0].hand[h];
            }
            // 亮牌
            tableRevealed=true;
            BeginBatchDraw(); renderGameScreen(); EndBatchDraw(); Sleep(400);

            // 计分（仅参与者）
            if((int)tied.size()==2){
                int a=tied[0],b=tied[1];
                int va=tableCards[a].getCompareValue(currentRule);
                int vb=tableCards[b].getCompareValue(currentRule);
                bool aWin=(currentRule==BIG_WINS)?va>vb:va<vb;
                if(va==vb){ tbScore[a]++; tbScore[b]++; }
                else if(aWin) tbScore[a]+=2;
                else tbScore[b]+=2;
            } else {
                auto sc=computeScores(tableCards);
                for(int i:tied) tbScore[i]+=sc[i];
            }
            // 移除打出的牌
            for(int i:tied)
                if(playedIdx[i]>=0&&playedIdx[i]<(int)players[i].hand.size())
                    players[i].hand.erase(players[i].hand.begin()+playedIdx[i]);

            addMsg("[加赛"+to_string(tb)+"/5] 本局结束");
            BeginBatchDraw(); renderGameScreen(); EndBatchDraw(); Sleep(600);
            tableRevealed=false;
        }
        // 判断
        int maxTb=0; for(int i:tied) if(tbScore[i]>maxTb) maxTb=tbScore[i];
        vector<int> still;
        for(int i:tied) if(tbScore[i]==maxTb) still.push_back(i);
        if((int)still.size()==1){ tied=still; break; }
        tied=still;
        BeginBatchDraw(); renderGameScreen();
        showMsgBox("[加赛平局]","仍然平局，继续加赛！");
        EndBatchDraw();
    }
}

// ===== 检查达标结束 =====
bool GameEngine::checkEndCondition(vector<int>& tied){
    if(gameMode==0) return false;
    bool any=false;
    for(int i=0;i<3;++i) if(players[i].score>=targetScore){ any=true; break; }
    if(!any) return false;
    int maxS=0; for(int i=0;i<3;++i) if(players[i].score>maxS) maxS=players[i].score;
    vector<int> top;
    for(int i=0;i<3;++i) if(players[i].score==maxS) top.push_back(i);
    if((int)top.size()==1) return true;
    tied=top; return true;
}

// ===== 开始新游戏 =====
void GameEngine::startNewGame(){
    // 模式选
    gameMode=showModeSelect();
    if(gameMode==1){
        // 目标分选择
        int bw=440, bh=290, bx=(WIN_W-bw)/2, by=(WIN_H-bh)/2;
        Btn b30(bx+30,by+80,bw-60,44,"30 分",19);
        Btn b60(bx+30,by+132,bw-60,44,"60 分",19);
        Btn b100(bx+30,by+184,bw-60,44,"100 分",19);
        Btn b150(bx+30,by+236,bw-60,44,"150 分",19);
        vector<Btn> tbBtns={b30,b60,b100,b150};
        int tscores[]={30,60,100,150};
        int chosen=waitBtns(tbBtns,[&](){
            setfillcolor(C_TABLE); fillrectangle(0,0,WIN_W,WIN_H);
            fillRR(bx,by,bw,bh,12,C_PANEL_D,C_GOLD,2);
            dtC(bx+bw/2,by+40,"选择目标分",C_GOLD,22,true);
        });
        targetScore=tscores[chosen];
    }

    if(!consecutiveGame){
        for(int i=0;i<3;++i){ players[i].score=0; players[i].resetJokerUses(); }
        sceneCount=1;
    }
    for(int i=0;i<3;++i) players[i].hand.clear();
    round=1; lastRoundTwoWayTie=false;
    for(int i=0;i<3;++i) fiveReturnPending[i]=false;
    initDeck(); shuffleDeck(); dealCards(18);

    // 发牌后先展示人类手牌，再让黑桃A选规则
    {
        BeginBatchDraw();
        setfillcolor(C_TABLE); fillrectangle(0,0,WIN_W,WIN_H);
        renderInfoBar();
        renderHumanHand();
        dtC(WIN_W/2,WIN_H/2-100,"发牌完成！请先查看你的手牌",C_GOLD,22,true);
        dtC(WIN_W/2,WIN_H/2-60,"（点击继续选择规则）",C_DIM,16,false);
        EndBatchDraw();
        ExMessage mm;
        while(true){ if(peekmessage(&mm,EX_MOUSE)&&mm.message==WM_LBUTTONUP) break; Sleep(16); }
    }

    // 黑桃A选规则
    int chooser=-1;
    for(int i=0;i<3;++i) if(players[i].hasSpadeA()){ chooser=i; break; }
    if(!consecutiveGame){
        if(chooser==0){
            int bw=480,bh=220,bx=(WIN_W-bw)/2,by=(WIN_H-bh)/2;
            Btn bBig  (bx+30,by+90,bw-60,48,"比大 (K最大，A最小)",18);
            Btn bSmall(bx+30,by+148,bw-60,48,"比小 (A最优，K最差)",18);
            vector<Btn> rBtns={bBig,bSmall};
            int r=waitBtns(rBtns,[&](){
                setfillcolor(C_TABLE); fillrectangle(0,0,WIN_W,WIN_H);
                fillRR(bx,by,bw,bh,12,C_PANEL_D,C_GOLD,2);
                dtC(bx+bw/2,by+50,"你持有黑桃A，选择初始规则",C_GOLD,20,true);
            });
            currentRule=(r==0)?BIG_WINS:SMALL_WINS;
        } else {
            currentRule=(GameRule)(rng()%2);
            BeginBatchDraw(); renderGameScreen();
            char info[64]; sprintf(info,"%s 持有黑桃A，随机选择了：%s",
                (chooser>=0)?players[chooser].name.c_str():"系统",
                currentRule==BIG_WINS?"比大":"比小");
            showMsgBox("初始规则确定",info);
            EndBatchDraw();
        }
    } else {
        if(chooser>=0){
            players[chooser].score++;
            char info[64]; sprintf(info,"%s 持有黑桃A，续场奖励+1分",players[chooser].name.c_str());
            BeginBatchDraw(); renderGameScreen();
            showMsgBox("续场开始",info);
            EndBatchDraw();
        }
    }
    consecutiveGame=false;

    // 主循环
    for(;round<=18;++round){
        playRound();
        if(gameMode==1){
            vector<int> tied;
            if(checkEndCondition(tied)){
                if(tied.empty()){ showFinalRank(); return; }
                BeginBatchDraw(); renderGameScreen();
                showMsgBox("达标！进入加赛","有玩家达标但分数并列，进行加赛！");
                EndBatchDraw();
                playTiebreaker(tied); showFinalRank(); return;
            }
        }
        if(round==18) break;
    }
    // 18局结束
    if(gameMode==0){
        showFinalRank();
    } else {
        BeginBatchDraw(); renderGameScreen();
        showMsgBox("18局结束","尚无人达标，继续下一场！积分继承，重新发牌。");
        EndBatchDraw();
        sceneCount++;
        consecutiveGame=true;
        for(int i=0;i<3;++i) players[i].resetJokerUses();
        startNewGame();
    }
}
"""
with open(r'd:\Users\ymx36\Desktop\三雄争锋游戏\三雄争锋v3.cpp','a',encoding='gbk') as f:
    f.write(code)
print("GFX9 OK - 加赛/流程/排名写入完成")
