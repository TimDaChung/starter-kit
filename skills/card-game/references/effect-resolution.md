# 卡牌效果結算與結構（深入）

`SKILL.md` 背後的細節。引擎中立的 pseudocode。描述卡牌效果如何結算、觸發如何堆疊，
以及牌組構築如何塑造遊戲。

## 1. 效果即資料 + 解譯器

定義一小組**操作（operations）**詞彙；每張卡牌就是一串操作。新增卡牌等於新增資料，
而不是新增程式碼。這讓卡牌可測試，也避免每張卡各寫一套的義大利麵程式碼。

```python
# A handful of ops cover most card games. Extend deliberately.
OPS = {
    "damage":     lambda fx, ctx: deal_damage(ctx.target(fx), fx["amount"]),
    "heal":       lambda fx, ctx: heal(ctx.target(fx), fx["amount"]),
    "draw":       lambda fx, ctx: ctx.owner.draw(fx["amount"]),
    "gain_res":   lambda fx, ctx: add_resource(ctx.owner, fx["amount"]),
    "summon":     lambda fx, ctx: summon(ctx.owner, fx["unit_id"]),
    "buff":       lambda fx, ctx: add_modifier(ctx.target(fx), fx["mod"]),
    "destroy":    lambda fx, ctx: move_to_discard(ctx.target(fx)),
}
def resolve_effect(fx, ctx):
    OPS[fx["op"]](fx, ctx)
```

## 2. 結算 queue / stack

當效果可能觸發其他效果時（例如「當生物死亡時，抽一張牌」），透過明確的結構結算，
讓順序具確定性：

- **Queue（FIFO）：**效果依加入順序結算。對簡單遊戲來說直觀。
- **Stack（LIFO）：**最後加入的效果最先結算——這是 TCG 對「回應」的建模方式
  （最後說的先發生）。選一種並記錄下來。

```python
# Stack model (pseudocode): pushing during resolution lets responses resolve first.
stack = []
def push_effect(fx, ctx): stack.append((fx, ctx))
def resolve_stack():
    while stack:
        fx, ctx = stack.pop()          # LIFO: last in resolves first
        resolve_effect(fx, ctx)        # may push more (triggers) -> they resolve next
```

事先決定同時性規則：多個觸發同時發生時，依固定規則排序（主動玩家優先，再依 timestamp），
讓結果可重現。

## 3. 觸發與關鍵字

- **觸發（Triggers）：**「當 X 發生時，做 Y」（出牌時、死亡時、抽牌時、回合開始 / 結束）。
  依事件註冊監聽器；事件發生時，把被觸發的效果推入 queue / stack。
- **關鍵字（Keywords）：**具名、可重用的能力（例如嘲諷 / 守護、吸血、中毒 / DoT、護盾）。
  每個關鍵字只以 modifier 或 trigger 實作一次，再在卡牌上打標籤——絕不逐卡重新實作。

```python
# Event bus (pseudocode): triggers subscribe; effects fire when the event is published.
on("creature_died", lambda ev: [push_effect(t, ctx_for(t)) for t in triggers_for("on_death", ev)])
```

## 4. 選取目標

- 在結算當下（或依你的規則在出牌時）決定目標並**驗證**——目標可能在效果結算前
  已離開區域或死亡；定義「fizzle」（效果落空）行為。
- 讓出牌具**原子性**：先驗證費用 + 合法目標，再付費並提交。取消或不合法的出牌
  必須讓各區域維持原狀。

## 5. Deckbuilder vs. constructed

| | Constructed（TCG / CCG） | Deckbuilder（局內） |
|---|---|---|
| 牌組建構時機 | 開局前，從收藏中組成 | 遊玩中（抽選 / 購買卡牌） |
| 變異來源 | 換牌（mulligan）、抽牌順序 | 每次「洗牌」時重洗不斷成長的牌組 |
| 強度成長 | 牌組固定 | 牌組變薄 / 變厚；combo 在局中浮現 |
| 持久化 | 收藏 + 牌表 | 局狀態（常見於 roguelike：以單局為範圍，死亡即重置） |

在 roguelike deckbuilder 中，牌組*就是* build：局中增減卡牌就是核心成長。把局狀態與任何
meta 收藏分開（單檔 HTML 中用兩個 `localStorage` key：`run_state` 與 `collection`）。

## 6. 洗牌公平性與穩定性

- 使用正確的 **Fisher–Yates** 洗牌（引擎 RNG）；天真的「依隨機值排序」有偏差。
- 若需要可重現的局、replay 或確定性 undo，就為 RNG 設 seed。
- 在數位遊戲中，玩家會覺得真隨機「很容易連續開出同樣結果」。有些遊戲採用*保底*/
  平滑機制（例如限制所需資源最多幾張內必出）。刻意決定；並記錄下來，
  讓平衡數值能納入考量。

```python
def shuffle(cards, rng):                 # Fisher–Yates
    for i in range(len(cards) - 1, 0, -1):
        j = rng.range(0, i + 1)          # 0..i inclusive
        cards[i], cards[j] = cards[j], cards[i]
```

## 7. Mana / 資源曲線

- **資源曲線**（到第 N 回合能花多少）控制強度節奏。前期打便宜的卡，後期收昂貴的回報。
- 牌組的**費用分佈**（它的「曲線」）決定穩定性：太偏高費就前期沒動作；太便宜就後繼無力。
  讓卡牌強度與費用相稱，使更高的費用可靠地買到更大影響，稀有卡則可打破這條規則。
