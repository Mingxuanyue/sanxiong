# -*- coding: utf-8 -*-
"""GFX5: 游戏屏幕渲染函数（renderGameScreen及子函数）"""
code = r"""
// ===== 渲染：顶部信息栏 =====
void GameEngine::renderInfoBar(){
    fillArea(0,0,WIN_W,BAR_H,C_PANEL_D,C_GOLD,0);
    // 第N局
    char buf[64];
    sprintf(buf,"第 %d / 18 局",round);
    dtL(14,14,buf,C_GOLD,22,true);
    // 规则
    const char* ruleStr=(currentRule==BIG_WINS)?"比大 (K最强)":"比小 (A最优)";
    COLORREF rc=(currentRule==BIG_WINS)?C_RED_T:C_GREEN_T;
    dtC(WIN_W/2,BAR_H/2,ruleStr,rc,20,true);
    // 积分（右侧三人）
    int sx=WIN_W-420;
    for(int i=0;i<3;++i){
        char sb[32]; sprintf(sb,"%s:%d",players[i].name.c_str(),players[i].score);
        COLORREF sc=(i==0)?C_BLUE_T:(i==1)?C_WARN:C_SILVER;
        dtL(sx+i*140,14,sb,sc,18,i==0);
    }
    // 分割线
    setlinecolor(C_GOLD); setlinestyle(PS_SOLID,1);
    line(0,BAR_H-1,WIN_W,BAR_H-1);
}

// ===== 渲染：AI手牌区 =====
void GameEngine::renderAIArea(int pidx,int x,int y,int w,int h){
    fillArea(x,y,w,h,C_PANEL,RGB(50,80,50));
    // 玩家名
    COLORREF nc=(pidx==1)?C_WARN:C_SILVER;
    dtL(x+10,y+6,players[pidx].name.c_str(),nc,16,true);
    char sb[16]; sprintf(sb,"(%d张)",(int)players[pidx].hand.size());
    dtL(x+10+textwidth(players[pidx].name.c_str())+4,y+8,sb,C_DIM,14,false);
    // 牌背（紧凑排列，最多显示18张）
    int n=(int)players[pidx].hand.size();
    if(n==0){ dtC(x+w/2,y+h/2,"（已无手牌）",C_DIM,15,false); return; }
    int cw=min(CARD_W,max(22,(w-20)/max(1,n)));
    int ch=min(CARD_H,h-30);
    int totalW=cw*(n-1)+CARD_W;
    if(totalW>w-20) totalW=w-20;
    int startX=x+(w-min(totalW,n*cw))/2;
    int cardY=y+(h-ch)/2+10;
    for(int i=0;i<n;++i){
        int cx2=startX+i*min(cw,max(20,(w-20-CARD_W)/max(1,n-1)));
        drawCardBack(cx2,cardY,CARD_W,ch);
    }
}

// ===== 渲染：桌面牌区 =====
void GameEngine::renderTableArea(){
    fillArea(TBL_X,TBL_Y,TBL_W,TBL_H,C_TABLE_D,RGB(10,60,30),4);
    // 中间区域显示本轮打出的牌
    if(tableRevealed && (int)tableCards.size()==3){
        int spacing=CARD_W+24;
        int totalW=3*spacing-24;
        int startX=TBL_X+(TBL_W-totalW)/2;
        int cardY=TBL_Y+(TBL_H-CARD_H)/2-10;
        for(int i=0;i<3;++i){
            drawCard(startX+i*spacing,cardY,CARD_W,CARD_H,tableCards[i],true,false);
            // 玩家名标签
            dtC(startX+i*spacing+CARD_W/2, cardY+CARD_H+14,
                players[i].name.c_str(),
                (i==0)?C_BLUE_T:(i==1)?C_WARN:C_SILVER, 14, true);
        }
    } else {
        dtC(TBL_X+TBL_W/2, TBL_Y+TBL_H/2-16, "[ 等待出牌... ]", C_DIM, 18, false);
    }
    // 消息日志（右侧）
    int logX=TBL_X+TBL_W-380, logY=TBL_Y+10;
    fillArea(logX,logY,370,TBL_H-20,C_PANEL,RGB(30,60,30),4);
    dtL(logX+8,logY+6,"  游戏日志",C_GOLD,14,true);
    setlinecolor(RGB(40,80,40)); line(logX+6,logY+26,logX+364,logY+26);
    int ly=logY+32;
    for(int i=0;i<(int)msgLog.size();++i){
        // 截断超长消息
        string m=msgLog[i];
        if((int)m.size()>22) m=m.substr(0,22)+"...";
        COLORREF mc=(i==(int)msgLog.size()-1)?C_WHITE:C_DIM;
        dtL(logX+8,ly+i*24,m.c_str(),mc,13,i==(int)msgLog.size()-1);
    }
}

// ===== 渲染：人类手牌 =====
void GameEngine::renderHumanHand(int selIdx){
    fillArea(HND_X,HND_Y,HND_W,HND_H,C_PANEL,RGB(50,90,55),6);
    dtL(HND_X+10,HND_Y+6,"你的手牌",C_BLUE_T,15,true);
    int n=(int)players[0].hand.size();
    if(n==0){ dtC(HND_X+HND_W/2,HND_Y+HND_H/2,"（手牌已空）",C_DIM,16,false); return; }
    // 自适应卡宽
    int maxCards=min(n,13);
    int overlap=max(CARD_W+6, (HND_W-20) / max(1,maxCards));
    overlap=min(overlap, CARD_W+10);
    int totalW=(n-1)*overlap+CARD_W;
    int startX=HND_X+(HND_W-min(totalW,HND_W-20))/2;
    int cardY=HND_Y+26;
    // 被选中的牌上移
    for(int i=0;i<n;++i){
        bool sel=(i==selIdx);
        int cx2=startX+i*min(overlap,(HND_W-20-CARD_W)/max(1,n-1));
        int cy2=cardY+(sel?-12:0);
        drawCard(cx2,cy2,CARD_W,CARD_H-10,players[0].hand[i],true,sel);
    }
}

// ===== 渲染：操作按钮区 =====
void GameEngine::renderActionBtns(vector<Btn>& btns){
    fillArea(ACT_X,ACT_Y,ACT_W,ACT_H,C_PANEL_D,RGB(30,60,30),6);
    // 按钮由调用者负责绘制
}

// ===== 全屏渲染 =====
void GameEngine::renderGameScreen(){
    // 背景
    setfillcolor(C_TABLE);
    setlinecolor(C_TABLE);
    fillrectangle(0,0,WIN_W,WIN_H);
    renderInfoBar();
    renderAIArea(1,AI1_X,AI1_Y,AI1_W,AI1_H);
    renderAIArea(2,AI2_X,AI2_Y,AI2_W,AI2_H);
    renderTableArea();
    renderHumanHand();
}
"""
with open(r'd:\Users\ymx36\Desktop\三雄争锋游戏\三雄争锋v3.cpp','a',encoding='gbk') as f:
    f.write(code)
print("GFX5 OK - 屏幕渲染写入完成")
