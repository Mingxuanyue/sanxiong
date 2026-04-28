/*
 * 游戏名称：三雄争锋
 * 编译环境：Dev-C++ 5.11 (需开启 C++11 支持：工具->编译选项->加入 -std=c++11)
 * 字符编码：ANSI / GBK
 */

#include <iostream>
#include <vector>
#include <string>
#include <algorithm>
#include <random>
#include <ctime>
#include <cstdlib>
#include <limits>
#include <chrono>

#ifdef _WIN32
#include <windows.h>
#define CLEAR_SCREEN "cls"
#else
#define CLEAR_SCREEN "clear"
#endif

using namespace std;

// -------------------- 枚举定义 --------------------
enum Suit { SPADE = 0, HEART, CLUB, DIAMOND, JOKER };
enum Rank {
    RANK_A = 1, RANK_2, RANK_3, RANK_4, RANK_5, RANK_6,
    RANK_7, RANK_8, RANK_9, RANK_10, RANK_J, RANK_Q, RANK_K,
    RANK_SMALL_JOKER = 100, RANK_BIG_JOKER = 101
};
enum GameRule { BIG_WINS, SMALL_WINS };

// -------------------- 扑克牌类 --------------------
class Card {
public:
    Suit suit;
    Rank rank;
    bool isJoker;

    Card() : suit(SPADE), rank(RANK_A), isJoker(false) {}
    Card(Suit s, Rank r, bool joker = false) : suit(s), rank(r), isJoker(joker) {}

    int getCompareValue(GameRule rule) const {
        if (isJoker) {
            if (rule == BIG_WINS) {
                if (rank == RANK_BIG_JOKER) return 1000;
                else return 900;
            } else {
                if (rank == RANK_BIG_JOKER) return -1000;
                else return -900;
            }
        }
        return static_cast<int>(rank);
    }

    string rankString() const {
        if (isJoker) {
            if (rank == RANK_BIG_JOKER) return "大王";
            else return "小王";
        }
        switch (rank) {
        case RANK_A: return "A";
        case RANK_J: return "J";
        case RANK_Q: return "Q";
        case RANK_K: return "K";
        default: return to_string(static_cast<int>(rank));
        }
    }

    string suitString() const {
        if (isJoker) return "";
        switch (suit) {
        case SPADE: return "黑桃";
        case HEART: return "红桃";
        case CLUB: return "梅花";
        case DIAMOND: return "方块";
        default: return "";
        }
    }

    string toString() const {
        if (isJoker) return rankString();
        return suitString() + rankString();
    }

    bool isTen() const { return !isJoker && rank == RANK_10; }
    bool isSpadeA() const { return !isJoker && suit == SPADE && rank == RANK_A; }

    bool equals(const Card& other) const {
        if (isJoker != other.isJoker) return false;
        if (isJoker) return rank == other.rank;
        return suit == other.suit && rank == other.rank;
    }
};

// -------------------- 玩家类 --------------------
class Player {
public:
    string name;
    vector<Card> hand;
    int score;
    bool isHuman;
    bool isStrategic;

    Player(string n, bool human = false, bool strategic = false)
        : name(n), score(0), isHuman(human), isStrategic(strategic) {}

    void addCard(const Card& c) { hand.push_back(c); }

    Card removeCard(int index) {
        Card c = hand[index];
        hand.erase(hand.begin() + index);
        return c;
    }

    Card removeRandomCard(mt19937& rng) {
        if (hand.empty()) return Card();
        int idx = rng() % hand.size();
        return removeCard(idx);
    }

    void showHand() const {
        for (size_t i = 0; i < hand.size(); ++i) {
            cout << "[" << i + 1 << "] " << hand[i].toString() << "  ";
            if ((i + 1) % 6 == 0) cout << endl;
        }
        if (hand.size() % 6 != 0) cout << endl;
    }

    bool hasSpadeA() const {
        for (size_t i = 0; i < hand.size(); ++i) {
            if (hand[i].isSpadeA()) return true;
        }
        return false;
    }

    bool removeSpecificCard(const Card& target) {
        for (vector<Card>::iterator it = hand.begin(); it != hand.end(); ++it) {
            if (it->equals(target)) {
                hand.erase(it);
                return true;
            }
        }
        return false;
    }
};

// 仿函数：用于比大排序
struct CompareBig {
    const vector<Card>& cards;
    GameRule rule;
    CompareBig(const vector<Card>& c, GameRule r) : cards(c), rule(r) {}
    bool operator()(int a, int b) const {
        return cards[a].getCompareValue(rule) > cards[b].getCompareValue(rule);
    }
};

// 仿函数：用于比小排序
struct CompareSmall {
    const vector<Card>& cards;
    GameRule rule;
    CompareSmall(const vector<Card>& c, GameRule r) : cards(c), rule(r) {}
    bool operator()(int a, int b) const {
        return cards[a].getCompareValue(rule) < cards[b].getCompareValue(rule);
    }
};

// -------------------- 游戏引擎类 --------------------
class GameEngine {
private:
    vector<Player> players;
    GameRule currentRule;
    int round;
    vector<Card> deck;
    mt19937 rng;

    void initDeck() {
        deck.clear();
        for (int s = SPADE; s <= DIAMOND; ++s) {
            for (int r = RANK_A; r <= RANK_K; ++r) {
                deck.push_back(Card(static_cast<Suit>(s), static_cast<Rank>(r), false));
            }
        }
        deck.push_back(Card(JOKER, RANK_SMALL_JOKER, true));
        deck.push_back(Card(JOKER, RANK_BIG_JOKER, true));
    }

    void shuffleDeck() {
        shuffle(deck.begin(), deck.end(), rng);
    }

    void dealCards() {
        for (int i = 0; i < 54; ++i) {
            players[i % 3].addCard(deck[i]);
        }
    }

    void showHeader() const {
        cout << "==================================================" << endl;
        cout << "                三 雄 争 锋                       " << endl;
        cout << "==================================================" << endl;
    }

    void showStatus() const {
        cout << "            第 [ " << round << " / 18 ] 回合" << endl;
        cout << "--------------------------------------------------" << endl;
        cout << "  [当前规则] ";
        if (currentRule == BIG_WINS) cout << "比大 (K最大, A最小)";
        else cout << "比小 (A最大, K最小)";
        cout << endl;
        cout << "--------------------------------------------------" << endl;
        cout << "  [积分榜]" << endl;
        for (int i = 0; i < 3; ++i) {
            cout << "  " << players[i].name << " : " << players[i].score << " 分" << endl;
        }
        cout << "--------------------------------------------------" << endl;
    }

    int getHumanChoice(int maxIdx) {
        int choice;
        while (true) {
            cout << "请输入要打出的手牌序号 (1~" << maxIdx << "): ";
            cin >> choice;
            if (cin.fail() || choice < 1 || choice > maxIdx) {
                cin.clear();
                cin.ignore(numeric_limits<streamsize>::max(), '\n');
                cout << "输入无效，请重新输入。" << endl;
            } else {
                cin.ignore(numeric_limits<streamsize>::max(), '\n');
                return choice - 1;
            }
        }
    }

    vector<int> getDiscardChoices(Player& p) {
        vector<int> indices;
        cout << "你需要弃置两张牌：" << endl;
        p.showHand();
        while (indices.size() < 2) {
            int idx;
            cout << "请选择第 " << indices.size() + 1 << " 张要弃置的牌序号 (1~" << p.hand.size() << "): ";
            cin >> idx;
            if (cin.fail() || idx < 1 || idx > (int)p.hand.size()) {
                cin.clear();
                cin.ignore(numeric_limits<streamsize>::max(), '\n');
                cout << "输入无效。" << endl;
                continue;
            }
            idx--;
            bool already = false;
            for (size_t i = 0; i < indices.size(); ++i) {
                if (indices[i] == idx) { already = true; break; }
            }
            if (already) {
                cout << "不能重复选择同一张牌。" << endl;
                continue;
            }
            indices.push_back(idx);
            cin.ignore(numeric_limits<streamsize>::max(), '\n');
        }
        sort(indices.begin(), indices.end(), greater<int>());
        return indices;
    }

    int getMenuChoice(int min, int max) {
        int c;
        while (true) {
            cin >> c;
            if (cin.fail() || c < min || c > max) {
                cin.clear();
                cin.ignore(numeric_limits<streamsize>::max(), '\n');
                cout << "输入无效，请重新输入: ";
            } else {
                cin.ignore(numeric_limits<streamsize>::max(), '\n');
                return c;
            }
        }
    }

    void showRules() const {
        system(CLEAR_SCREEN);
        showHeader();
        cout << "【游戏规则简介】" << endl;
        cout << "1. 3人游戏，每人18张牌，共54张（含大小王）。" << endl;
        cout << "2. 开局由持有黑桃A的玩家选择比大或比小。" << endl;
        cout << "3. 每回合各出一张牌，按规则比较大小计分。" << endl;
        cout << "4. 仅一人出10：没收另两张牌（包括大小王），再弃两张牌（本回合不得分）。" << endl;
        cout << "5. 打出任意三连顺（如A23, 234, ..., JQK）：本回合正常结算，结束后触发顺时针抽牌。" << endl;
        cout << "6. 三人同点：反转比大小规则！" << endl;
        cout << "7. 平局时，唯一总分最低者获得额外加分（两人平+1，三人平+2）。" << endl;
        cout << "8. 大小王同时出现有特殊剧情彩蛋（不影响结算）。" << endl;
        cout << "9. 18回合后总分最高者胜。" << endl;
        cout << "--------------------------------------------------" << endl;
        cout << "按回车键返回主菜单...";
        cin.get();
    }

    // 策略型AI出牌
    int strategicChoice(const Player& p) {
        if (p.hand.empty()) return 0;
        if (rng() % 100 < 30) return rng() % p.hand.size();

        vector<pair<int, int> > indexed;
        for (size_t i = 0; i < p.hand.size(); ++i) {
            indexed.push_back(make_pair(p.hand[i].getCompareValue(currentRule), i));
        }
        // 简单冒泡排序
        for (size_t i = 0; i < indexed.size(); ++i) {
            for (size_t j = i+1; j < indexed.size(); ++j) {
                if (indexed[i].first > indexed[j].first) {
                    swap(indexed[i], indexed[j]);
                }
            }
        }
        int n = p.hand.size();
        int idx;
        if (currentRule == BIG_WINS) {
            int pos = n - 1 - (rng() % max(1, n/3));
            idx = indexed[pos].second;
        } else {
            idx = indexed[rng() % max(1, n/3)].second;
        }
        return idx;
    }

    void strategicDiscard(Player& p, int count) {
        for (int k = 0; k < count && !p.hand.empty(); ++k) {
            int worstIdx = 0;
            int worstVal = p.hand[0].getCompareValue(currentRule);
            for (size_t i = 1; i < p.hand.size(); ++i) {
                int v = p.hand[i].getCompareValue(currentRule);
                if ((currentRule == BIG_WINS && v < worstVal) ||
                    (currentRule == SMALL_WINS && v > worstVal)) {
                    worstVal = v;
                    worstIdx = i;
                }
            }
            p.hand.erase(p.hand.begin() + worstIdx);
        }
    }

    vector<int> computeScores(const vector<Card>& cards) {
        vector<int> values(3);
        for (int i = 0; i < 3; ++i) values[i] = cards[i].getCompareValue(currentRule);

        vector<int> order(3);
        for (int i = 0; i < 3; ++i) order[i] = i;
        if (currentRule == BIG_WINS) {
            CompareBig cmp(cards, currentRule);
            sort(order.begin(), order.end(), cmp);
        } else {
            CompareSmall cmp(cards, currentRule);
            sort(order.begin(), order.end(), cmp);
        }

        vector<int> scores(3, 0);
        if (cards[0].rank == cards[1].rank && cards[1].rank == cards[2].rank) {
            return scores;
        }
        if (values[order[0]] == values[order[1]] && values[order[1]] == values[order[2]]) {
            return scores;
        } else if (values[order[0]] == values[order[1]]) {
            scores[order[0]] = 1; scores[order[1]] = 1; scores[order[2]] = 0;
        } else if (values[order[1]] == values[order[2]]) {
            scores[order[0]] = 2; scores[order[1]] = 0; scores[order[2]] = 0;
        } else {
            scores[order[0]] = 2; scores[order[1]] = 1; scores[order[2]] = 0;
        }
        return scores;
    }

    bool isThreeConsecutive(const vector<Card>& cards) {
        for (int i = 0; i < 3; ++i) if (cards[i].isJoker) return false;
        vector<int> nums;
        for (int i = 0; i < 3; ++i) nums.push_back(static_cast<int>(cards[i].rank));
        sort(nums.begin(), nums.end());
        if (nums[1] == nums[0] + 1 && nums[2] == nums[1] + 1) return true;
        if (nums[0] == 1 && nums[1] == 2 && nums[2] == 3) return true;
        return false;
    }

    void performDrawSequence() {
        int startIdx = 0, maxScore = -1;
        for (int i = 0; i < 3; ++i) {
            if (players[i].score > maxScore) {
                maxScore = players[i].score;
                startIdx = i;
            }
        }
        vector<Card> drawnCards(3);
        vector<bool> hasDrawn(3, false);
        bool computerDrewFromHuman = false; // 标记是否有电脑抽了人类
        for (int i = 0; i < 3; ++i) {
            int fromIdx = (startIdx + i) % 3;
            int targetIdx = (fromIdx + 1) % 3;
            if (!players[targetIdx].hand.empty()) {
                if (players[fromIdx].isHuman) {
                    cout << "你可以从 " << players[targetIdx].name << " 的手牌中抽取一张（对方有 "
                         << players[targetIdx].hand.size() << " 张牌）。" << endl;
                    int idx = getHumanChoice(players[targetIdx].hand.size());
                    drawnCards[fromIdx] = players[targetIdx].hand[idx];
                    players[targetIdx].hand.erase(players[targetIdx].hand.begin() + idx);
                    cout << "你抽到了 " << drawnCards[fromIdx].toString() << "。" << endl;
                } else {
                    int randIdx = rng() % players[targetIdx].hand.size();
                    drawnCards[fromIdx] = players[targetIdx].hand[randIdx];
                    players[targetIdx].hand.erase(players[targetIdx].hand.begin() + randIdx);
                    if (players[targetIdx].isHuman) {
                        // 电脑抽人类：显示具体牌
                        cout << players[fromIdx].name << " 从你手中抽走了 " << drawnCards[fromIdx].toString() << "。" << endl;
                        computerDrewFromHuman = true;
                    }
                    // 电脑之间互抽：不显示具体牌，稍后统一给一句氛围播报
                }
                hasDrawn[fromIdx] = true;
            }
        }
        // 如果发生了电脑互抽（即非人类参与且未播报细节），增加一句提示
        bool anyComputerToComputer = false;
        for (int i = 0; i < 3; ++i) {
            int fromIdx = (startIdx + i) % 3;
            int targetIdx = (fromIdx + 1) % 3;
            if (!players[fromIdx].isHuman && !players[targetIdx].isHuman && hasDrawn[fromIdx]) {
                anyComputerToComputer = true;
                break;
            }
        }
        if (anyComputerToComputer) {
            cout << ">>> 电脑之间暗流涌动，互相交换了手牌..." << endl;
        }

        for (int i = 0; i < 3; ++i) {
            if (hasDrawn[i]) players[i].hand.push_back(drawnCards[i]);
        }
        cout << ">>> [乱武] 三连顺现世，天下大乱！手牌异动完成。" << endl;
    }

    void playRound() {
        system(CLEAR_SCREEN);
        showHeader();
        showStatus();

        vector<Card> tableCards(3);
        vector<int> playedIndices(3);

        for (int i = 0; i < 3; ++i) {
            if (players[i].isHuman) {
                cout << "【你的手牌】" << endl;
                players[i].showHand();
                playedIndices[i] = getHumanChoice(players[i].hand.size());
                tableCards[i] = players[i].hand[playedIndices[i]];
            }
        }
        for (int i = 0; i < 3; ++i) {
            if (!players[i].isHuman) {
                if (players[i].isStrategic) {
                    playedIndices[i] = strategicChoice(players[i]);
                } else {
                    playedIndices[i] = rng() % players[i].hand.size();
                }
                tableCards[i] = players[i].hand[playedIndices[i]];
            }
        }

        cout << "\n>>> 亮牌 <<<" << endl;
        for (int i = 0; i < 3; ++i) {
            cout << players[i].name << " 打出: " << tableCards[i].toString()
                 << " (比较值: " << tableCards[i].getCompareValue(currentRule) << ")" << endl;
        }

        bool consecutiveTriggered = false;
        if (round != 18 && isThreeConsecutive(tableCards)) consecutiveTriggered = true;

        bool bigJoker = false, smallJoker = false;
        for (int i = 0; i < 3; ++i) {
            if (tableCards[i].rank == RANK_BIG_JOKER) bigJoker = true;
            if (tableCards[i].rank == RANK_SMALL_JOKER) smallJoker = true;
        }

        int tenCount = 0, tenPlayer = -1;
        for (int i = 0; i < 3; ++i) if (tableCards[i].isTen()) { tenCount++; tenPlayer = i; }

        bool scoreSkipped = false;
        if (tenCount == 1) {
            cout << ">>> [牵羊] " << players[tenPlayer].name << " 发动 [顺手牵羊]！没收对局双牌。" << endl;
            for (int i = 0; i < 3; ++i) if (i != tenPlayer) players[tenPlayer].addCard(tableCards[i]);
            players[tenPlayer].removeSpecificCard(tableCards[tenPlayer]);
            cout << players[tenPlayer].name << " 需弃置两张牌。" << endl;
            if (players[tenPlayer].isHuman) {
                vector<int> discards = getDiscardChoices(players[tenPlayer]);
                players[tenPlayer].hand.erase(players[tenPlayer].hand.begin() + discards[0]);
                players[tenPlayer].hand.erase(players[tenPlayer].hand.begin() + discards[1]);
            } else {
                if (players[tenPlayer].isStrategic) {
                    strategicDiscard(players[tenPlayer], 2);
                } else {
                    for (int k = 0; k < 2 && !players[tenPlayer].hand.empty(); ++k) {
                        int idx = rng() % players[tenPlayer].hand.size();
                        players[tenPlayer].hand.erase(players[tenPlayer].hand.begin() + idx);
                    }
                }
            }
            scoreSkipped = true;
        }

        for (int i = 0; i < 3; ++i) {
            if (!(tenCount == 1 && i == tenPlayer)) {
                players[i].hand.erase(players[i].hand.begin() + playedIndices[i]);
            }
        }

        if (bigJoker && smallJoker) {
            cout << ">>> [至尊] 大王与小王同台登场！天地为之色变，众人屏息凝神..." << endl;
        }

        vector<int> roundScores(3, 0);
        bool threeWayTie = false, twoWayTie = false;
        if (!scoreSkipped) {
            roundScores = computeScores(tableCards);
            int r0 = static_cast<int>(tableCards[0].rank);
            int r1 = static_cast<int>(tableCards[1].rank);
            int r2 = static_cast<int>(tableCards[2].rank);
            if (r0 == r1 && r1 == r2) threeWayTie = true;
            else if (r0 == r1 || r1 == r2 || r0 == r2) twoWayTie = true;
            for (int i = 0; i < 3; ++i) players[i].score += roundScores[i];
        }

        if ((twoWayTie || threeWayTie) && !scoreSkipped) {
            cout << ">>> [平局结算] 当前总分："
                 << players[0].name << " " << players[0].score << "分, "
                 << players[1].name << " " << players[1].score << "分, "
                 << players[2].name << " " << players[2].score << "分。" << endl;
            int minScore = min(players[0].score, min(players[1].score, players[2].score));
            int minCount = 0, minIdx = -1;
            for (int i = 0; i < 3; ++i) if (players[i].score == minScore) { minCount++; minIdx = i; }
            if (minCount == 1) {
                int bonus = twoWayTie ? 1 : 2;
                players[minIdx].score += bonus;
                cout << ">>> [追分] " << players[minIdx].name << " 是唯一总分最低者，额外获得 " << bonus << " 分！" << endl;
            } else {
                cout << ">>> [平局] 总分最低者并列（" << minCount << "人），无人获得额外加分。" << endl;
            }
        }

        if (threeWayTie && !scoreSkipped) {
            currentRule = (currentRule == BIG_WINS) ? SMALL_WINS : BIG_WINS;
            cout << ">>> [惊变] 三人同点！乾坤倒转！下回合规则变更为 ";
            cout << (currentRule == BIG_WINS ? "[比大]！" : "[比小]！") << endl;
        }

        if (consecutiveTriggered) performDrawSequence();

        cout << "\n本回合得分: ";
        for (int i = 0; i < 3; ++i) cout << players[i].name << " +" << roundScores[i] << "  ";
        cout << endl << "按回车键继续...";
        cin.get();
    }

public:
    GameEngine() : rng(chrono::steady_clock::now().time_since_epoch().count()) {
        srand(static_cast<unsigned>(time(NULL)));
        players.push_back(Player("玩家 A (你)", true, false));
        players.push_back(Player("电脑 B (AI)", false, true));
        players.push_back(Player("电脑 C", false, false));
        currentRule = BIG_WINS;
        round = 1;
    }

    void startNewGame() {
        for (int i = 0; i < 3; ++i) { players[i].hand.clear(); players[i].score = 0; }
        round = 1;
        initDeck(); shuffleDeck(); dealCards();

        int chooser = -1;
        for (int i = 0; i < 3; ++i) if (players[i].hasSpadeA()) { chooser = i; break; }

        system(CLEAR_SCREEN); showHeader();
        if (chooser == 0) {
            cout << "你持有黑桃A，请选择首回合规则：" << endl;
            cout << "1. 比大" << endl << "2. 比小" << endl;
            int c = getMenuChoice(1, 2);
            currentRule = (c == 1) ? BIG_WINS : SMALL_WINS;
        } else {
            cout << players[chooser].name << " 持有黑桃A，正在选择规则..." << endl;
            currentRule = (rng() % 2 == 0) ? BIG_WINS : SMALL_WINS;
            cout << players[chooser].name << " 选择了: " << (currentRule == BIG_WINS ? "比大" : "比小") << endl;
            cout << "按回车键继续..."; cin.get();
        }

        for (; round <= 18; ++round) {
            playRound();
            if (round == 18) break;
        }

        system(CLEAR_SCREEN); showHeader();
        cout << "==================== 游 戏 结 束 ====================" << endl;
        cout << "最终积分：" << endl;
        for (int i = 0; i < 3; ++i) cout << players[i].name << " : " << players[i].score << " 分" << endl;
        int maxScore = max(players[0].score, max(players[1].score, players[2].score));
        vector<string> winners;
        for (int i = 0; i < 3; ++i) if (players[i].score == maxScore) winners.push_back(players[i].name);
        cout << "--------------------------------------------------" << endl;
        if (winners.size() == 1) cout << "胜者: " << winners[0] << "！恭喜！" << endl;
        else cout << "平局！多人并列最高分。" << endl;
        cout << "==================================================" << endl;
        cout << "按回车键返回主菜单..."; cin.get();
    }

    void mainMenu() {
        while (true) {
            system(CLEAR_SCREEN); showHeader();
            cout << "          1. 开始新游戏" << endl;
            cout << "          2. 查看游戏规则简介" << endl;
            cout << "          0. 退出游戏" << endl;
            cout << "==================================================" << endl;
            cout << "请输入选项编号: ";
            int choice = getMenuChoice(0, 2);
            if (choice == 0) { cout << "感谢游玩，再见！" << endl; break; }
            else if (choice == 1) startNewGame();
            else if (choice == 2) showRules();
        }
    }
};

int main() {
#ifdef _WIN32
    SetConsoleOutputCP(936);
#endif
    GameEngine game;
    game.mainMenu();
    return 0;
}
