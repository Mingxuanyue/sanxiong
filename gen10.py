# -*- coding: utf-8 -*-
"""BP10: mainMenu + main"""
code = r"""
// ==================== mainMenu ====================
void GameEngine::mainMenu() {
    while(true){
        CLEAR_SCREEN;
        showHeader();
        printDSep();
        cprint("              主菜单\n\n",14);
        cprint("        1. 开始新游戏\n",15);
        cprint("        2. 查看游戏规则\n",15);
        cprint("        0. 退出游戏\n\n",8);
        printDSep();
        cprint("  请选择: ",11);
        int c=getMenuChoice(0,2);
        if(c==0){
            CLEAR_SCREEN; showHeader();
            cprint("  感谢游玩《三雄争锋》！再见！\n",14);
            break;
        } else if(c==1){
            consecutiveGame=false;
            startNewGame();
        } else {
            showRules();
        }
    }
}

// ==================== main ====================
int main(){
#ifdef _WIN32
    SetConsoleOutputCP(936);
    SetConsoleCP(936);
    // 设置控制台窗口大小
    system("mode con cols=70 lines=40");
#endif
    hideCursor(true);
    GameEngine game;
    game.mainMenu();
    hideCursor(false);
    return 0;
}
"""
with open(r'd:\Users\ymx36\Desktop\三雄争锋游戏\三雄争锋v2.cpp','a',encoding='gbk') as f:
    f.write(code)
print("BP10 OK - mainMenu/main 写入完成")
print("=== 所有C++代码部分写入完成 ===")
