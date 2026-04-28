# -*- coding: utf-8 -*-
"""GFX7: 连顺抽牌 + 大/小王效果"""
code = r"""
// ===== 大王防御 =====
int GameEngine::performBigJokerDefense(int targetPlayer, int chosen){
    if(!players[targetPlayer].canUseBigJoker()) return chosen;
    int handSize=(int)players[targetPlayer].hand.size();
    if(handSize<=1) return chosen; // 只剩1张，偏移无意义
    bool doDefend;
    if(players[targetPlayer].isHuman){
        char body[128];
        sprintf(body,"对方选了编号 %d。\n你持有大王，可将选择偏移为 %d（已用%d/2次）",
            chosen+1, (chosen==0)?handSize:chosen, players[targetPlayer].bigJokerUses);
        doDefend=guiYesNo("[大王防御] 触发？",body);
    } else {
        // AI：有50%概率使用，且保留至少1次给关键时刻
        doDefend=(players[targetPlayer].bigJokerUses<1)&&((int)(rng()%100)<50);
    }
    if(doDefend){
        players[targetPlayer].bigJokerUses++;
        int newChosen=(chosen==0)?(handSize-1):(chosen-1);
        addMsg("[大王防御] "+players[targetPlayer].name+" 偏移了目标！");
        BeginBatchDraw(); renderGameScreen();
        char info[64]; sprintf(info,"防御成功！编号 %d -> %d",chosen+1,newChosen+1);
        showMsgBox("[大王防御！]",info);
        EndBatchDraw();
        return newChosen;
    }
    return chosen;
}

// ===== 小王偷窥 =====
void GameEngine::performSmallJokerPeek(int fromPlayer, int targetPlayer){
    if(!players[fromPlayer].canUseSmallJoker()) return;
    bool doPeek;
    if(players[fromPlayer].isHuman){
        char body[64];
        sprintf(body,"你持有小王，可偷窥 %s 的手牌（每场限1次）",
            players[targetPlayer].name.c_str());
        doPeek=guiYesNo("[小王偷窥] 触发？",body);
    } else {
        doPeek=((int)(rng()%100)<60);
    }
    if(!doPeek) return;
    players[fromPlayer].smallJokerUses++;
    addMsg("[小王偷窥] "+players[fromPlayer].name+" 偷窥了 "+players[targetPlayer].name);
    if(players[fromPlayer].isHuman){
        // 展示目标手牌给人类玩家看
        int n=(int)players[targetPlayer].hand.size();
        int spacing=min(CARD_W+10,(TBL_W-100)/max(1,n));
        int totalW=(n-1)*spacing+CARD_W;
        int startX=TBL_X+(TBL_W-min(totalW,TBL_W-80))/2;
        int cardY=TBL_Y+(TBL_H-CARD_H)/2;
        BeginBatchDraw();
        renderGameScreen();
        fillArea(TBL_X,TBL_Y,TBL_W,TBL_H,C_TABLE_D,RGB(10,60,30),4);
        char title[64]; sprintf(title,"[小王偷窥] %s 的手牌（仅你可见）",
            players[targetPlayer].name.c_str());
        dtC(TBL_X+TBL_W/2-200,TBL_Y+16,title,C_GOLD,16,true);
        for(int i=0;i<n;++i){
            int cx2=startX+i*min(spacing,(TBL_W-80-CARD_W)/max(1,n-1));
            drawCard(cx2,cardY,CARD_W,CARD_H,players[targetPlayer].hand[i],true,false);
        }
        dtC(TBL_X+TBL_W/2-200,TBL_Y+TBL_H-24,"[ 点击继续（AI看不见） ]",C_DIM,14,false);
        EndBatchDraw();
        ExMessage mm;
        while(true){ if(peekmessage(&mm,EX_MOUSE)&&mm.message==WM_LBUTTONUP) break; Sleep(16); }
    }
}

// ===== 连顺抽牌 =====
void GameEngine::performDrawSequence(){
    addMsg("[连顺抽牌] 三张连续！各从下家盲抽1张！");
    BeginBatchDraw(); renderGameScreen();
    showMsgBox("[连顺触发！]","三张牌点数连续！各玩家从顺时针下家手中盲抽1张！");
    EndBatchDraw();

    // 按当前积分由高到低先行
    int order[3]={0,1,2};
    sort(order,order+3,[this](int a,int b){ return players[a].score>players[b].score; });

    vector<Card> drawn(3); vector<bool> hasDrawn(3,false);

    for(int k=0;k<3;++k){
        int from=order[k];
        int target=(from+1)%3;
        if(players[target].hand.empty()){
            addMsg(players[target].name+" 手牌空，跳过");
            continue;
        }
        // 小王偷窥机会
        performSmallJokerPeek(from,target);

        int chosen;
        int tSize=(int)players[target].hand.size();
        char pr[80]; sprintf(pr,"从 %s 的%d张手牌中盲选1张",players[target].name.c_str(),tSize);
        if(players[from].isHuman){
            chosen=guiBlindSelect(from,pr,tSize);
        } else {
            chosen=aiBlindChoice(tSize);
        }
        chosen=performBigJokerDefense(target,chosen);

        drawn[from]=players[target].hand[chosen];
        players[target].hand.erase(players[target].hand.begin()+chosen);
        hasDrawn[from]=true;

        // 可见性：抽取方（人类）看到自己抽到了什么
        if(players[from].isHuman){
            BeginBatchDraw();
            renderGameScreen();
            fillArea(TBL_X,TBL_Y,TBL_W,TBL_H,C_TABLE_D,RGB(10,60,30),4);
            dtC(TBL_X+TBL_W/2-200,TBL_Y+20,"[连顺抽牌] 你抽到了：",C_GOLD,18,true);
            int sx=TBL_X+TBL_W/2-200-CARD_W/2;
            drawCard(sx,TBL_Y+60,CARD_W,CARD_H,drawn[from],true,false);
            dtC(TBL_X+TBL_W/2-200,TBL_Y+TBL_H-24,"[ 点击继续（仅你可见） ]",C_DIM,14,false);
            EndBatchDraw();
            ExMessage mm;
            while(true){ if(peekmessage(&mm,EX_MOUSE)&&mm.message==WM_LBUTTONUP) break; Sleep(16); }
        } else {
            addMsg(players[from].name+" 从 "+players[target].name+" 处抽1张");
            BeginBatchDraw(); renderGameScreen(); EndBatchDraw();
            Sleep(600);
        }
        // 被抽方（人类）得到通知
        if(players[target].isHuman){
            char info[64]; sprintf(info,"你的 %s 被 %s 抽走了！",
                rankStr(drawn[from].rank),players[from].name.c_str());
            BeginBatchDraw(); renderGameScreen();
            showMsgBox("[连顺抽牌] 你的牌被抽走了！",info);
            EndBatchDraw();
        }
    }
    for(int i=0;i<3;++i) if(hasDrawn[i]) players[i].addCard(drawn[i]);
    addMsg("[连顺] 抽牌完毕");
}
"""
with open(r'd:\Users\ymx36\Desktop\三雄争锋游戏\三雄争锋v3.cpp','a',encoding='gbk') as f:
    f.write(code)
print("GFX7 OK - 连顺+大小王写入完成")
