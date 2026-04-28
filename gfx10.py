# -*- coding: utf-8 -*-
"""GFX10: 主菜单 + 规则界面 + 模式选择 + main()"""
code = r"""
// ===== 规则界面 =====
void GameEngine::showRulesScreen(){
    struct RuleItem{ const char* icon; const char* title; const char* desc; };
    RuleItem items[]={
        {"[基础]","三人对战 54张","每人18张，共18局，积分制（第1名+2, 第2名+1, 第3名+0）"},
        {"[比大]","K最大A最小","比大模式：K>Q>...>2>A，大王/小王均为最优"},
        {"[比小]","A最优K最差","比小模式：A>2>...>K，大王/小王均为最优"},
        {"[出10]","顺手牵羊","唯一出10: 拿走他人出的牌，自弃1张，下家再盲弃1张"},
        {"[5号]","狸猫换太子","三张各不同且你非最优: 消耗额外5将本轮出的牌收回"},
        {"[连顺]","连续点数抽牌","三张点数连续（非收回牌）: 各从顺时针下家手中盲抽1张"},
        {"[大王]","防御偏移","被选中时可偏移 N->N-1（每场限2次）"},
        {"[小王]","偷窥手牌","连顺抽牌前可偷窥目标手牌（每场限1次）"},
        {"[翻转]","规则动态变化","连续两次两张同: 小概率触发规则翻转（比大<->比小）"},
        {"[补分]","随机奖励","每局约12%概率随机给一名玩家+1分"},
        {"[加赛]","决胜机制","达标分模式+并列达标: 进行5张5局加赛直到分出高下"},
    };
    int n=sizeof(items)/sizeof(items[0]);
    int scroll=0;
    int perPage=7;

    Btn bBack(WIN_W/2-80,WIN_H-52,160,40,"返回主菜单",17);
    Btn bUp  (WIN_W-70,100,56,36,"▲",16);
    Btn bDown(WIN_W-70,Win_H-100,56,36,"▼",16);
    vector<Btn> navBtns={bBack};

    int mx=0,my=0;
    while(true){
        BeginBatchDraw();
        setfillcolor(C_TABLE); fillrectangle(0,0,WIN_W,WIN_H);
        fillRR(30,10,WIN_W-60,WIN_H-20,12,C_PANEL_D,C_GOLD,2);
        dtC(WIN_W/2,46,"《三雄争锋》游戏规则",C_GOLD,26,true);
        setlinecolor(C_GOLD); line(50,72,WIN_W-50,72);
        // 规则条目
        for(int k=0;k<perPage&&(k+scroll)<n;++k){
            int i=k+scroll;
            int ry=86+k*82;
            fillRR(50,ry,WIN_W-100,74,8,C_PANEL,RGB(40,80,45));
            dtL(62,ry+8, items[i].icon, C_GOLD, 14, true);
            dtL(62,ry+30, items[i].title, C_WHITE, 17, true);
            dtL(180,ry+14, items[i].desc, C_TEXT, 14, false);
        }
        // 滚动提示
        if(scroll>0)    dtC(WIN_W-40,90,"▲",C_GOLD,16,true);
        if(scroll+perPage<n) dtC(WIN_W-40,WIN_H-90,"▼",C_GOLD,16,true);
        for(auto& b:navBtns) b.draw(b.hit(mx,my));
        EndBatchDraw();

        ExMessage msg;
        while(peekmessage(&msg,EX_MOUSE)){
            mx=msg.x; my=msg.y;
            if(msg.message==WM_MOUSEWHEEL){
                if((short)HIWORD(msg.wheel)>0) scroll=max(0,scroll-1);
                else scroll=min(n-perPage,scroll+1);
            }
            if(msg.message==WM_LBUTTONUP){
                if(navBtns[0].hit(mx,my)) goto rules_back;
                // 滚动箭头区域
                if(mx>=WIN_W-64&&mx<=WIN_W-16&&my>=80&&my<=120) scroll=max(0,scroll-1);
                if(mx>=WIN_W-64&&mx<=WIN_W-16&&my>=WIN_H-120&&my<=WIN_H-80) scroll=min(n-perPage,scroll+1);
            }
        }
        Sleep(16);
    }
    rules_back:;
}

// ===== 模式选择 =====
int GameEngine::showModeSelect(){
    int bw=520,bh=280,bx=(WIN_W-bw)/2,by=(WIN_H-bh)/2;
    Btn bSingle(bx+30,by+90, bw-60,54,"单局模式（18局，按总分排名）",18);
    Btn bTarget(bx+30,by+154,bw-60,54,"达标分模式（先达目标分者胜）",18);
    vector<Btn> btns={bSingle,bTarget};
    return waitBtns(btns,[&](){
        setfillcolor(C_TABLE); fillrectangle(0,0,WIN_W,WIN_H);
        fillRR(bx,by,bw,bh,12,C_PANEL_D,C_GOLD,2);
        dtC(bx+bw/2,by+44,"选择游戏模式",C_GOLD,22,true);
        setlinecolor(C_GOLD); line(bx+20,by+68,bx+bw-20,by+68);
    });
}

// ===== 主菜单 =====
void GameEngine::showMainMenu(){
    Btn bStart (WIN_W/2-130,340,260,58,"开始游戏",22);
    Btn bRules (WIN_W/2-130,414,260,52,"游戏规则",19);
    Btn bExit  (WIN_W/2-130,482,260,52,"退出游戏",19);
    vector<Btn> btns={bStart,bRules,bExit};

    int mx=0,my=0;
    while(true){
        BeginBatchDraw();
        // 渐变背景
        for(int y=0;y<WIN_H;++y){
            int r=max(0,22-(int)(y*8/WIN_H));
            int g=max(0,100-(int)(y*28/WIN_H));
            int b=max(0,52-(int)(y*14/WIN_H));
            setlinecolor(RGB(r,g,b));
            line(0,y,WIN_W,y);
        }
        // 标题装饰背景块
        fillRR(WIN_W/2-300,60,600,240,16,RGB(8,45,22),C_GOLD,2);
        // 主标题
        dtC(WIN_W/2,140,"三 雄 争 锋",C_GOLD,64,true);
        dtC(WIN_W/2,218,"San Xiong Zheng Feng  ·  Card Battle v3.0",C_DIM,16,false);
        setlinecolor(C_GOLD); line(WIN_W/2-220,248,WIN_W/2+220,248);
        dtC(WIN_W/2,275,"三人对战  |  54张牌  |  EasyX 图形界面",C_SILVER,16,false);
        // 按钮
        for(auto& b:btns) b.draw(b.hit(mx,my));
        // 版权
        dtC(WIN_W/2,WIN_H-24,"欢迎游玩，祝旗开得胜！",C_DIM,13,false);
        EndBatchDraw();

        ExMessage msg;
        while(peekmessage(&msg,EX_MOUSE)){
            mx=msg.x; my=msg.y;
            if(msg.message==WM_LBUTTONUP){
                if(btns[0].hit(mx,my)){
                    consecutiveGame=false;
                    startNewGame();
                } else if(btns[1].hit(mx,my)){
                    showRulesScreen();
                } else if(btns[2].hit(mx,my)){
                    closegraph(); exit(0);
                }
            }
        }
        Sleep(16);
    }
}

// ===== main =====
int main(){
    SetConsoleOutputCP(936);
    initgraph(WIN_W, WIN_H, EW_SHOWCONSOLE^EW_SHOWCONSOLE); // 不显示控制台
    SetWindowText(GetHWnd(),"三雄争锋 v3.0");
    setbkcolor(C_TABLE);
    BeginBatchDraw();
    GameEngine eng;
    g_eng=&eng;
    eng.showMainMenu();
    EndBatchDraw();
    closegraph();
    return 0;
}
"""
with open(r'd:\Users\ymx36\Desktop\三雄争锋游戏\三雄争锋v3.cpp','a',encoding='gbk') as f:
    f.write(code)
print("GFX10 OK - 主菜单+main写入完成")
print("=== 所有GFX部分写入完成 ===")
