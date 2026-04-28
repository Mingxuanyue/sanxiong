# -*- coding: utf-8 -*-
"""GFX8: playRound - 完整GUI回合主循环"""
code = r"""
// ===== 主回合（GUI版）=====
void GameEngine::playRound(){
    msgLog.clear();
    tableCards.clear(); tableCards.resize(3);
    playedIdx.assign(3,-1);
    tableRevealed=false;

    // Step 0: 5号牌归还
    processFiveReturns();

    // Step 1: 出牌阶段
    // AI先出（静默），人类交互出
    vector<bool> hasCanceled(3,false);
    for(int i=1;i<3;++i){
        int c=strategicChoice(players[i]);
        playedIdx[i]=c;
        tableCards[i]=players[i].hand[c];
    }

    // 人类出牌
    int humanSel=-1;
    int mx=0,my=0;
    int n=(int)players[0].hand.size();
    int overlap=min(CARD_W+10,(HND_W-20)/max(1,n));
    int startX=HND_X+(HND_W-min((n-1)*overlap+CARD_W,HND_W-20))/2;
    int cardY=HND_Y+26;

    Btn bPlay  (ACT_X+8, ACT_Y+8,  ACT_W-16, 46, "出牌",   19, false);
    Btn bRule  (ACT_X+8, ACT_Y+60, ACT_W-16, 40, "查看规则",15);
    Btn bHint  (ACT_X+8, ACT_Y+106,ACT_W-16, 40, "提示",   15);
    vector<Btn> actionBtns={bPlay,bRule,bHint};

    while(humanSel<0 || (humanSel>=0&&false)){
        BeginBatchDraw();
        renderGameScreen();
        // 覆盖手牌区（含选中）
        fillArea(HND_X,HND_Y,HND_W,HND_H,C_PANEL,RGB(50,90,55),6);
        dtL(HND_X+10,HND_Y+6,"你的手牌  ← 点击选牌，再点出牌按钮确认",C_BLUE_T,14,true);
        for(int i=0;i<n;++i){
            bool s=(i==humanSel);
            int cx2=startX+i*min(overlap,(HND_W-20-CARD_W)/max(1,n-1));
            int cy2=cardY+(s?-12:0);
            drawCard(cx2,cy2,CARD_W,CARD_H-10,players[0].hand[i],true,s);
        }
        fillArea(ACT_X,ACT_Y,ACT_W,ACT_H,C_PANEL_D,RGB(30,60,30),6);
        actionBtns[0].enabled=(humanSel>=0);
        for(auto& b:actionBtns) b.draw(b.hit(mx,my));
        EndBatchDraw();

        ExMessage msg;
        while(peekmessage(&msg,EX_MOUSE)){
            mx=msg.x; my=msg.y;
            if(msg.message==WM_LBUTTONUP){
                // 点牌
                for(int i=0;i<n;++i){
                    int cx2=startX+i*min(overlap,(HND_W-20-CARD_W)/max(1,n-1));
                    if(mx>=cx2&&mx<=cx2+CARD_W&&my>=cardY-14&&my<=cardY+CARD_H)
                        humanSel=(humanSel==i)?-1:i;
                }
                // 出牌按钮
                if(actionBtns[0].hit(mx,my)&&humanSel>=0) goto play_confirmed;
                // 规则按钮
                if(actionBtns[1].hit(mx,my)){
                    BeginBatchDraw(); renderGameScreen();
                    showMsgBox("游戏规则","比大:K最大A最小 | 比小:A最优K最差\n出10拿走他人牌 | 5号牌收回自己的牌\n连顺触发随机抽牌 | 大王防御 小王偷窥");
                    EndBatchDraw();
                }
                // 提示按钮
                if(actionBtns[2].hit(mx,my)){
                    int hint=strategicChoice(players[0]);
                    humanSel=hint;
                }
            }
        }
        Sleep(16);
    }
    play_confirmed:
    playedIdx[0]=humanSel;
    tableCards[0]=players[0].hand[humanSel];

    // Step 2: 动画亮牌
    tableRevealed=true;
    addMsg("[亮牌] 三人同时亮牌");
    // 逐张翻牌动效（简化：先背面0.3秒后正面）
    for(int reveal=0;reveal<3;++reveal){
        BeginBatchDraw();
        renderGameScreen();
        // 提前高亮刚亮的牌
        if(reveal<3){
            int spacing=CARD_W+24;
            int totalW=3*spacing-24;
            int sx2=TBL_X+(TBL_W-totalW)/2;
            int sy2=TBL_Y+(TBL_H-CARD_H)/2-10;
            for(int i=0;i<3;++i){
                if(i<=reveal) drawCard(sx2+i*spacing,sy2,CARD_W,CARD_H,tableCards[i],true,false);
                else          drawCardBack(sx2+i*spacing,sy2,CARD_W,CARD_H);
            }
        }
        EndBatchDraw();
        Sleep(260);
    }
    BeginBatchDraw(); renderGameScreen(); EndBatchDraw();
    Sleep(300);

    // Step 3: 大王/小王同台提示
    bool hasBig=false, hasSmall=false;
    for(int i=0;i<3;++i){
        if(tableCards[i].isJoker){
            if(tableCards[i].rank==RANK_BIG_JOKER) hasBig=true;
            else hasSmall=true;
        }
    }
    if(hasBig&&hasSmall){
        addMsg("[大小王同台] 双王出现！");
        BeginBatchDraw(); renderGameScreen();
        showMsgBox("[大小王同台！]","大王与小王同时出现！两者均视为最优，本局计分不变。");
        EndBatchDraw();
    }

    // Step 4: 出10检查（优先）
    int tenPlayer=-1;
    for(int i=0;i<3;++i)
        if(!tableCards[i].isJoker && tableCards[i].rank==RANK_10){ tenPlayer=i; break; }
    // 多人出10时只取最先（玩家0优先）
    bool hasTen=(tenPlayer>=0);

    // Step 5: 从手中移除打出的牌（出10方稍后特殊处理）
    for(int i=0;i<3;++i){
        if(i==tenPlayer) continue; // 出10方的牌后面在perform10里处理
        if(playedIdx[i]>=0 && playedIdx[i]<(int)players[i].hand.size())
            players[i].hand.erase(players[i].hand.begin()+playedIdx[i]);
    }

    if(hasTen){
        perform10Mechanism(tenPlayer);
        addMsg("[出10局] 本局不计分");
        BeginBatchDraw(); renderGameScreen();
        showMsgBox("[出10] 本局不计分","顺手牵羊机制触发，本局积分跳过。");
        EndBatchDraw();
    } else {
        // Step 5b: 出10方正常移除
        // (已在上面处理非tenPlayer，tenPlayer==-1时全部处理完)

        // Step 6: 连顺检查
        vector<bool> skipMask(3,false);
        for(int i=0;i<3;++i) skipMask[i]=tableCards[i].isReturned;
        bool consecutive=isThreeConsecutive(tableCards,skipMask);

        // Step 7: 5号牌激活（无连顺+无出10时）
        vector<bool> activated;
        if(!consecutive){
            perform5CardActivations(tableCards,playedIdx,activated);
        }

        // Step 8: 连顺抽牌（无5号牌激活时）
        bool anyActivated=false;
        for(bool a:activated) if(a) anyActivated=true;
        if(consecutive && !anyActivated){
            performDrawSequence();
        }

        // Step 9: 计分
        vector<int> scores=computeScores(tableCards);
        for(int i=0;i<3;++i) players[i].score+=scores[i];
        {
            string smsg="[计分] ";
            for(int i=0;i<3;++i){
                smsg+=players[i].name+":+"+to_string(scores[i])+" ";
            }
            addMsg(smsg);
        }

        // Step 10: 小概率补分
        applyBonusScore();

        // Step 11: 规则翻转判断
        handleRuleFlip(tableCards);

        // Step 12: 本局结果展示
        BeginBatchDraw();
        renderGameScreen();
        // 结果面板
        int pw=440, ph=200;
        int px=(WIN_W-pw)/2, py=(WIN_H-ph)/2+60;
        fillRR(px,py,pw,ph,12,C_PANEL_D,C_GOLD,2);
        dtC(px+pw/2,py+28,"本局结果",C_GOLD,20,true);
        setlinecolor(C_GOLD); line(px+16,py+50,px+pw-16,py+50);
        for(int i=0;i<3;++i){
            char buf[64]; sprintf(buf,"%s  +%d分  (总:%d)",
                players[i].name.c_str(),scores[i],players[i].score);
            COLORREF tc=(scores[i]==2)?C_GOLD:(scores[i]==1)?C_GREEN_T:C_DIM;
            dtC(px+pw/2, py+72+i*38, buf, tc, 17, scores[i]==2);
        }
        dtC(px+pw/2,py+ph-28,"[ 点击继续 ]",C_DIM,14,false);
        EndBatchDraw();
        ExMessage mm;
        while(true){ if(peekmessage(&mm,EX_MOUSE)&&mm.message==WM_LBUTTONUP) break; Sleep(16); }
    }
    // 清空桌面
    tableRevealed=false; tableCards.clear(); tableCards.resize(3);
}
"""
with open(r'd:\Users\ymx36\Desktop\三雄争锋游戏\三雄争锋v3.cpp','a',encoding='gbk') as f:
    f.write(code)
print("GFX8 OK - playRound GUI主循环写入完成")
