# -*- coding: utf-8 -*-
"""GFX6: GUI交互辅助 + 特殊机制（出10 + 5号牌）"""
code = r"""
// ===== GUI: 选择手中一张牌 =====
int GameEngine::guiSelectCard(int pidx, const string& prompt){
    int sel=-1;
    int mx=0,my=0;
    Player& p=players[pidx];
    int n=(int)p.hand.size();
    if(n==0) return -1;
    int overlap=min(CARD_W+10, (HND_W-20)/max(1,n));
    int totalW=(n-1)*overlap+CARD_W;
    int startX=HND_X+(HND_W-min(totalW,HND_W-20))/2;
    int cardY=HND_Y+26;

    Btn bConfirm(ACT_X+8,ACT_Y+10,ACT_W-16,44,"确认",18,false);
    Btn bCancel (ACT_X+8,ACT_Y+60,ACT_W-16,44,"取消",18);
    vector<Btn> btns={bConfirm,bCancel};

    while(true){
        BeginBatchDraw();
        renderGameScreen();
        // 覆盖手牌区（含选中效果）
        fillArea(HND_X,HND_Y,HND_W,HND_H,C_PANEL,RGB(50,90,55),6);
        dtL(HND_X+10,HND_Y+6,"你的手牌",C_BLUE_T,15,true);
        for(int i=0;i<n;++i){
            bool s=(i==sel);
            int cx2=startX+i*min(overlap,(HND_W-20-CARD_W)/max(1,n-1));
            int cy2=cardY+(s?-12:0);
            drawCard(cx2,cy2,CARD_W,CARD_H-10,p.hand[i],true,s);
        }
        // 提示文字
        dtC(HND_X+HND_W/2,HND_Y+HND_H-18,prompt.c_str(),C_GOLD,15,true);
        // 操作按钮
        fillArea(ACT_X,ACT_Y,ACT_W,ACT_H,C_PANEL_D,RGB(30,60,30),6);
        btns[0].enabled=(sel>=0);
        for(auto& b:btns) b.draw(b.hit(mx,my));
        EndBatchDraw();

        ExMessage msg;
        while(peekmessage(&msg,EX_MOUSE)){
            mx=msg.x; my=msg.y;
            if(msg.message==WM_LBUTTONUP){
                // 检查牌点击
                for(int i=0;i<n;++i){
                    int cx2=startX+i*min(overlap,(HND_W-20-CARD_W)/max(1,n-1));
                    int cy2=cardY;
                    if(mx>=cx2&&mx<=cx2+CARD_W&&my>=cy2-14&&my<=cy2+CARD_H)
                        sel=(sel==i)?-1:i;
                }
                if(btns[0].hit(mx,my) && sel>=0) return sel;
                if(btns[1].hit(mx,my)) return -1;
            }
        }
        Sleep(16);
    }
}

// ===== GUI: 盲选1~N中一个编号 =====
int GameEngine::guiBlindSelect(int pidx, const string& prompt, int maxN){
    // 显示 maxN 张牌背，让玩家点击其中一张
    int sel=-1;
    int mx=0,my=0;
    int spacing=min(CARD_W+16,(TBL_W-100)/max(1,maxN));
    int totalW=(maxN-1)*spacing+CARD_W;
    int startX=TBL_X+(TBL_W-min(totalW,TBL_W-100))/2;
    int cardY=TBL_Y+(TBL_H-CARD_H)/2;

    Btn bConfirm(ACT_X+8,ACT_Y+10,ACT_W-16,44,"确认",18,false);
    vector<Btn> btns={bConfirm};

    while(true){
        BeginBatchDraw();
        renderGameScreen();
        // 覆盖桌面区显示牌背
        fillArea(TBL_X,TBL_Y,TBL_W,TBL_H,C_TABLE_D,RGB(10,60,30),4);
        dtC(TBL_X+TBL_W/2-200,TBL_Y+18,prompt.c_str(),C_GOLD,16,true);
        for(int i=0;i<maxN;++i){
            int cx2=startX+i*min(spacing,(TBL_W-100-CARD_W)/max(1,maxN-1));
            bool s=(i==sel);
            if(s){ fillRR(cx2-4,cardY-4,CARD_W+8,CARD_H+8,12,C_SEL,C_SEL,3); }
            drawCardBack(cx2,cardY,CARD_W,CARD_H);
            char num[4]; sprintf(num,"%d",i+1);
            dtC(cx2+CARD_W/2,cardY+CARD_H+14,num,s?C_GOLD:C_DIM,14,s);
        }
        fillArea(ACT_X,ACT_Y,ACT_W,ACT_H,C_PANEL_D,RGB(30,60,30),6);
        btns[0].enabled=(sel>=0);
        for(auto& b:btns) b.draw(b.hit(mx,my));
        EndBatchDraw();

        ExMessage msg;
        while(peekmessage(&msg,EX_MOUSE)){
            mx=msg.x; my=msg.y;
            if(msg.message==WM_LBUTTONUP){
                for(int i=0;i<maxN;++i){
                    int cx2=startX+i*min(spacing,(TBL_W-100-CARD_W)/max(1,maxN-1));
                    if(mx>=cx2&&mx<=cx2+CARD_W&&my>=cardY&&my<=cardY+CARD_H)
                        sel=(sel==i)?-1:i;
                }
                if(btns[0].hit(mx,my)&&sel>=0) return sel;
            }
        }
        Sleep(16);
    }
}

// guiInfo / guiYesNo 包装
void GameEngine::guiInfo(const string& title, const string& body){
    BeginBatchDraw();
    renderGameScreen();
    showMsgBox(title,body);
    EndBatchDraw();
}
bool GameEngine::guiYesNo(const string& title, const string& body){
    BeginBatchDraw();
    renderGameScreen();
    bool r=showYesNo(title,body);
    EndBatchDraw();
    return r;
}

// ===== 特殊机制：5号牌归还 =====
void GameEngine::processFiveReturns(){
    for(int i=0;i<3;++i){
        if(fiveReturnPending[i]){
            Card rc=fiveReturnCard[i]; rc.isReturned=true;
            players[i].addCard(rc);
            fiveReturnPending[i]=false;
            addMsg("[5号牌] "+players[i].name+" 收回了上回合的牌(*)");
        }
    }
}

// ===== 检查5号牌激活条件 =====
bool GameEngine::check5CardActivation(int pIdx,int pIdx2,const vector<Card>& table){
    int v[3]; for(int i=0;i<3;++i) v[i]=table[i].getCompareValue(currentRule);
    if(v[0]==v[1]||v[1]==v[2]||v[0]==v[2]) return false;
    int myV=v[pIdx];
    int best=(currentRule==BIG_WINS)?*max_element(v,v+3):*min_element(v,v+3);
    if(myV==best) return false;
    if(players[pIdx].findFiveCard(pIdx2)<0) return false;
    return true;
}

// ===== 5号牌激活（含GUI）=====
void GameEngine::perform5CardActivations(const vector<Card>& table,
    const vector<int>& pIdx, vector<bool>& activated){
    activated.assign(3,false);
    for(int i=0;i<3;++i){
        if(!check5CardActivation(i,pIdx[i],table)) continue;
        bool doIt=false;
        if(players[i].isHuman){
            char body[128];
            sprintf(body,"你打出的牌不是最优，且手中还有5可用。\n消耗一张5，将本轮出的牌收回？");
            doIt=guiYesNo("[5号牌] 激活？",body);
        } else {
            // AI：打出的牌有一定价值才激活
            int myV=table[i].getCompareValue(currentRule);
            int vals[3]; for(int j=0;j<3;++j) vals[j]=table[j].getCompareValue(currentRule);
            sort(vals,vals+3);
            doIt=(currentRule==BIG_WINS)?(myV>=vals[1]):(myV<=vals[1]);
        }
        if(doIt){
            int fi=players[i].findFiveCard(pIdx[i]);
            players[i].removeCard(fi);
            fiveReturnPending[i]=true;
            fiveReturnCard[i]=table[i];
            activated[i]=true;
            addMsg("[5号牌] "+players[i].name+" 激活！下局收回出的牌");
        }
    }
}

// ===== 出10机制（含GUI）=====
void GameEngine::perform10Mechanism(int tenPlayer){
    addMsg("[顺手牵羊] "+players[tenPlayer].name+" 出了10！");
    BeginBatchDraw();
    renderGameScreen();
    char title[64]; sprintf(title,"[顺手牵羊] %s 出了10！",players[tenPlayer].name.c_str());
    showMsgBox(title,"拿走另两人出的牌，然后自弃1张，下家再盲弃1张。");
    EndBatchDraw();

    // 拿走另两人的牌
    for(int i=0;i<3;++i) if(i!=tenPlayer) players[tenPlayer].addCard(tableCards[i]);
    players[tenPlayer].removeSpecificCard(tableCards[tenPlayer]);

    // 自弃1张（仅自己知）
    if(players[tenPlayer].isHuman){
        int di=guiSelectCard(tenPlayer,"[自弃] 请选择要弃掉的1张牌（仅你可见）");
        if(di>=0){ players[tenPlayer].removeCard(di); addMsg("[出10] 你悄悄弃了1张"); }
    } else {
        strategicDiscard(players[tenPlayer],1);
        addMsg("[出10] "+players[tenPlayer].name+" 弃了1张（未公开）");
    }
    BeginBatchDraw(); renderGameScreen(); EndBatchDraw();
    Sleep(400);

    // 下家盲弃1张（公开展示）
    int nextP=(tenPlayer+1)%3;
    int chosen;
    char pr[64]; sprintf(pr,"[盲弃] 从 %s 的%d张牌中选一编号",
        players[tenPlayer].name.c_str(),(int)players[tenPlayer].hand.size());
    if(players[nextP].isHuman){
        chosen=guiBlindSelect(nextP,pr,(int)players[tenPlayer].hand.size());
    } else {
        chosen=aiBlindChoice((int)players[tenPlayer].hand.size());
    }
    chosen=performBigJokerDefense(tenPlayer,chosen);
    // 公开展示被弃的牌
    Card shown=players[tenPlayer].hand[chosen];
    players[tenPlayer].removeCard(chosen);
    char info[64]; sprintf(info,"%s 选中了该牌并公开弃掉！",players[nextP].name.c_str());
    BeginBatchDraw();
    renderGameScreen();
    // 单张展示
    int sx=WIN_W/2-CARD_W/2, sy=WIN_H/2-CARD_H/2;
    drawCard(sx,sy,CARD_W,CARD_H,shown,true,false);
    dtC(WIN_W/2,sy+CARD_H+24,info,C_WARN,18,true);
    dtC(WIN_W/2,sy+CARD_H+52,"[ 点击继续 ]",C_DIM,14,false);
    EndBatchDraw();
    ExMessage mm;
    while(true){
        if(peekmessage(&mm,EX_MOUSE)&&mm.message==WM_LBUTTONUP) break;
        Sleep(16);
    }
    addMsg("[出10] "+players[nextP].name+" 公开弃了 "+string(rankStr(shown.rank)));
}
"""
with open(r'd:\Users\ymx36\Desktop\三雄争锋游戏\三雄争锋v3.cpp','a',encoding='gbk') as f:
    f.write(code)
print("GFX6 OK - GUI交互+特殊机制写入完成")
