# -*- coding: utf-8 -*-
"""BP5: 出10机制（新版）"""
code = r"""
// ==================== 出10机制（新版）====================
// 效果：出10者拿走另两人的牌；出10者自弃1张；顺时针下家盲弃出10者的1张
// 大王可在被盲弃时触发防御（N→N-1）
void GameEngine::perform10Mechanism(int tenPlayer,
        vector<Card>& tableCards, vector<int>& playedIdx) {

    cprint("\n  >>> [顺路拐带] "+players[tenPlayer].name+" 出了10，触发拐带！\n",14);

    // Step1: 出10者拿走另两人出的牌
    for(int i=0;i<3;++i){
        if(i!=tenPlayer) players[tenPlayer].addCard(tableCards[i]);
    }
    // 移除出10者自己的10
    players[tenPlayer].removeSpecificCard(tableCards[tenPlayer]);
    // 另外两人的牌已由tableCards记录，稍后主循环会从hand中删除（仅针对非tenPlayer）

    cprint("  "+players[tenPlayer].name+" 已获得另外两人的出牌。\n",11);

    // Step2: 出10者自弃1张（只有自己知道）
    cprint("\n  [Step 2] "+players[tenPlayer].name+" 需自选弃掉1张牌\n",11);
    if(players[tenPlayer].isHuman){
        int di=getDiscardChoice(players[tenPlayer],"请选择要弃掉的1张牌（仅你可见）");
        players[tenPlayer].removeCard(di);
        cprint("  自弃完成。（他人看不见弃了什么）\n",8);
    } else {
        // AI弃牌（弃最差的）
        strategicDiscard(players[tenPlayer],1);
        cprint("  "+players[tenPlayer].name+" 已弃掉1张牌。\n",8);
    }

    // Step3: 顺时针下家盲弃出10者的1张
    int nextPlayer=(tenPlayer+1)%3;
    cprint("\n  [Step 3] "+players[nextPlayer].name+" 需盲选一个编号，弃掉 "+
           players[tenPlayer].name+" 的1张牌\n",11);
    cprint("  （"+players[nextPlayer].name+" 看不见对方手牌，只知道有 "+
           to_string((int)players[tenPlayer].hand.size())+" 张）\n",8);

    int chosen=-1;
    if(players[nextPlayer].isHuman){
        // 人类盲选：不显示tenPlayer手牌
        setColor(11);
        cout<<"  请输入1~"<<players[tenPlayer].hand.size()<<" 中任意编号（盲选）: ";
        resetColor();
        chosen=getMenuChoice(1,(int)players[tenPlayer].hand.size())-1;
    } else {
        chosen=aiBlindChoice((int)players[tenPlayer].hand.size());
        cprint("  "+players[nextPlayer].name+" 盲选了一个编号...\n",8);
    }

    // 大王防御：检查tenPlayer是否可触发大王防御
    chosen=performBigJokerDefense(tenPlayer, chosen);

    // 公开展示被弃的牌（被人操作的弃牌需全员可见）
    Card discardCard=players[tenPlayer].hand[chosen];
    cprint("\n  >>> [公开弃牌] ",14);
    discardCard.printColored();
    cprint(" 被 "+players[nextPlayer].name+" 选中弃掉！（全员可见）\n",11);
    players[tenPlayer].removeCard(chosen);
    cprint("  弃牌完成。\n",8);
}

"""
with open(r'd:\Users\ymx36\Desktop\三雄争锋游戏\三雄争锋v2.cpp','a',encoding='gbk') as f:
    f.write(code)
print("BP5 OK - 出10机制 写入完成")
