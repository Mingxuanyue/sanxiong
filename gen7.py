# -*- coding: utf-8 -*-
"""BP7: 大王防御 + 小王偷窥"""
code = r"""
// ==================== 大王防御（N→N-1）====================
// targetPlayer: 被操作的玩家, chosenIdx: 对方选择的0-based索引
// 返回实际生效的索引（可能被偏移）
int GameEngine::performBigJokerDefense(int targetPlayer, int chosenIdx) {
    if(!players[targetPlayer].canUseBigJoker()) return chosenIdx;
    int sz=(int)players[targetPlayer].hand.size();
    if(sz<=1) return chosenIdx; // 只剩1张无法偏移

    bool doDefense=false;
    if(players[targetPlayer].isHuman){
        int displayChosen=chosenIdx+1; // 转为1-based显示
        cprint("\n  [大王] 对方选择了你手牌中的第"+to_string(displayChosen)+
               "号（你已用"+to_string(players[targetPlayer].bigJokerUses)+"/2次大王技能）\n",14);
        doDefense=getYesNo("是否使用大王将目标偏移为第"+
            to_string(chosenIdx==0?(int)sz:chosenIdx)+"号？");
    } else {
        // AI：50%概率使用大王
        doDefense=(rng()%2==0);
        if(doDefense) cprint("  "+players[targetPlayer].name+" 使用了大王防御！\n",14);
    }

    if(doDefense){
        players[targetPlayer].bigJokerUses++;
        int newIdx=(chosenIdx==0)?(sz-1):(chosenIdx-1);
        cprint("  >>> [大王] 目标偏移：第"+to_string(chosenIdx+1)+"号 → 第"+
               to_string(newIdx+1)+"号\n",14);
        return newIdx;
    }
    return chosenIdx;
}

// ==================== 小王偷窥 ====================
// peekPlayer: 抽取人（手持小王）, targetPlayer: 被抽的人
void GameEngine::performSmallJokerPeek(int peekPlayer, int targetPlayer) {
    if(!players[peekPlayer].canUseSmallJoker()) return;

    bool doPeek=false;
    if(players[peekPlayer].isHuman){
        cprint("  [小王] 你持有小王（已用"+to_string(players[peekPlayer].smallJokerUses)+
               "/1次）\n",14);
        doPeek=getYesNo("是否使用小王偷窥 "+players[targetPlayer].name+" 的手牌？");
    } else {
        // 策略AI：总是使用小王偷窥
        doPeek=players[peekPlayer].isStrategic;
        if(doPeek) cprint("  "+players[peekPlayer].name+" 使用了小王偷窥！\n",14);
    }

    if(doPeek){
        players[peekPlayer].smallJokerUses++;
        if(players[peekPlayer].isHuman){
            cprint("\n  [小王偷窥] "+players[targetPlayer].name+" 的手牌（共"+
                   to_string((int)players[targetPlayer].hand.size())+"张）：\n",14);
            players[targetPlayer].showHand();
            cprint("  （看完后请记住，选择编号后这些信息不再显示）\n",8);
            pauseEnter();
        }
    }
}

"""
with open(r'd:\Users\ymx36\Desktop\三雄争锋游戏\三雄争锋v2.cpp','a',encoding='gbk') as f:
    f.write(code)
print("BP7 OK - 大王防御/小王偷窥 写入完成")
