---
name: card-game
description: >
  建立卡牌遊戲：卡牌資料、deck / hand / discard 區域、抽牌 / 洗牌 / 重洗、回合結構、費用與效果結算。
  適用於 deckbuilder、TCG / CCG 或 roguelike deckbuilder。
  觸發詞：卡牌、抽卡、牌組、卡牌遊戲、deckbuilder。搭配 /game-prototype 使用（規則設計在此，
  單檔 HTML 實作走 game-prototype）。
---

# 卡牌遊戲（card-game）

> **執行角色：企劃 → 工程**——規則與效果結算先以企劃視角定案，實作以工程視角（狀態機、邊界條件）；完成後切**數值**視角看平衡。

卡牌遊戲的作法手冊——卡牌資料、deck / hand / discard 區域、回合結構，以及卡牌效果如何結算。
這是一個**組合型** skill：把卡牌建模為資料並接上 UI。它不重複教資料資產或 UI 節點；
它定義區域模型、抽牌機制，以及讓卡牌遊戲保持正確、無 bug 的效果結算規則。

## 適用時機

- 當遊戲的核心物件是在區域之間移動的**卡牌**（deck → hand → play → discard）時使用：
  deckbuilder、TCG / CCG、接龍（solitaire）、roguelike deckbuilder。
- 當要設計抽牌 / 洗牌 / 重洗、回合結構、卡牌費用，或效果如何結算時使用。

**不適用時機：**遊戲並非以卡牌為中心（棋盤 / 方塊配對、只附帶卡牌戰鬥的 RPG）→ 直接從
`game-prototype` 開始，只在出現卡牌子系統時借用下方的區域 / 效果模式。本 skill 定義規則與
資料形狀，不負責建構 HTML——實作一律走 `game-prototype`。

**實作路徑（kit 預設）：**單檔 HTML。實作走 `game-prototype` 的
`JS-STATE`（zones、deck、hand、discard、resources 放在 `state`）/ `JS-LOGIC`（draw、shuffle、
play、resolve_effect、phase machine）section；UI 走 `JS-RENDER` / `JS-EVENTS`。不使用 Godot / Unity。

## 核心循環

**抽牌到手牌 → 花費資源打出卡牌 → 效果結算並改變場面 → 結束回合（清理 / 棄牌）→
對手 / 下一階段 → 重複直到達成勝利條件。**深度來自一手牌所允許的*組合*；引擎的職責是
毫無歧義地結算它們。

## 必備系統

1. **卡牌資料**——id、name、cost、type、text，以及效果規格（是資料，不是程式碼）。
2. **區域（zones）**——deck（draw pile）、hand、play / board、discard、exile / removed；每張卡牌只存在於其中一個區域。
3. **抽牌 + 洗牌 + 重洗**——從 deck 抽到 hand；deck 空了就把 discard pile 重洗回 deck。
4. **回合結構**——階段（untap / draw / main / combat / end）以 state machine 實作。
5. **資源系統**——mana / 能量 / 行動點，限制每回合能做多少事。
6. **效果結算**——依既定順序套用卡牌效果；處理目標與觸發。
7. **勝負條件**——生命總值、deck-out、目標達成。
8. **UI**——手牌排版、拖放或點擊出牌、區域數量顯示、選取目標的操作提示。

## 設計參數

| 參數 | 影響 | 備註 |
|------|------|------|
| 起手牌數 / 每回合抽牌數 | 節奏、穩定性 | 抽得越多，變異越小。 |
| 手牌上限 | 囤牌 vs. 使用 | 回合結束時棄到上限。 |
| 牌組張數（最小值） | 穩定性 | 越小，combo 越可靠。 |
| 資源曲線 | 何時能打出什麼 | 「mana curve」控制強度節奏。 |
| 卡牌稀有度 / 強度預算 | 平衡 | 越強的卡費用越高 / 越稀有。 |
| 確定性 vs. 隨機性 | 技術 vs. 翻盤 | 洗牌 + 隨機效果增加變異。 |
| 重洗規則 | deck-out、疲勞 | 重洗 discard pile，或懲罰空牌庫。 |
| 解牌 / 應對手段 | 反制 | 卡池中每個威脅都要有解。 |

## 模式

### 1. 區域 + 自動重洗的抽牌

```python
# Pseudocode. A card is in exactly one zone at a time; moving = remove here, add there.
def draw(n):
    for _ in range(n):
        if not deck:
            if not discard:          # truly empty: deck-out (lose, or take fatigue)
                on_deck_out(); return
            deck.extend(discard)     # reshuffle discard into deck
            discard.clear()
            shuffle(deck, rng)       # use a seeded RNG so runs can be replayed
        hand.append(deck.pop())
```

### 2. 卡牌即資料 + 效果結算

```python
# Pseudocode. Effects are a data list interpreted by the engine — not bespoke code per card.
card = {
    "id": "fireball", "cost": 3, "type": "spell",
    "effects": [ {"op": "damage", "amount": 6, "target": "chosen_enemy"} ],
}
def play(card, caster):
    if resources[caster] < card.cost: return False     # can't afford
    resources[caster] -= card.cost
    move(card, from_zone=hand, to_zone=play_or_discard(card))
    for fx in card.effects:
        resolve_effect(fx, caster)                      # one interpreter handles every card
    return True
```

### 3. 以階段機（phase machine）實作回合結構

```python
# Pseudocode. Fixed phases keep timing windows (triggers, priority) unambiguous.
PHASES = ["untap", "draw", "main", "combat", "end"]
def take_turn(player):
    for phase in PHASES:
        enter_phase(player, phase)        # fire "on_phase" triggers here
        if phase == "draw":   draw(1)
        if phase == "main":   await player_plays_cards()
        if phase == "combat": resolve_combat()
        if phase == "end":    discard_to_hand_limit(player); clear_temporary_effects()
```

## 陷阱 / 失敗模式

- **一張卡牌同時存在於兩個區域**→ 複製 / 遺失 bug。強制「恰好一個區域」；
  移動 = 先移除再加入，並 assert 沒有卡牌重複出現。
- **忘記重洗**→ 抽牌靜默失敗，或在空牌庫時 crash。重洗 discard pile，
  或明確定義 deck-out / 疲勞（模式 1）。
- **每張卡一個函數**→ 無法維護、無法測試。把效果做成**資料**，
  由一小組操作來解譯（模式 2）。
- **效果順序不明確 / 同時觸發**→ 結果不確定。依既定順序結算（queue 或 stack）；
  記錄採用 LIFO 還是 FIFO（見 refs）。
- **需要 replay / undo 的遊戲卻用未設 seed 的洗牌**→ 無法重現。使用有 seed 的 RNG。
- **沒有手牌上限 / 沒有解牌**→ 退化成囤牌，或出現無法擊敗的威脅。加上手牌上限，
  並確保每種威脅原型都有對應的解。
- **選取目標的狀態外漏**→ 取消出牌後，場面停在選目標中途。讓出牌具原子性：
  先驗證費用 + 目標，再提交。

## 組合（用這些 kit skills / agents 組出來）

- **卡牌狀態 + 邏輯：**`game-prototype`——卡牌以純 JS 物件放在 `JS-STATE`；抽牌 /
  洗牌 / 出牌 / 效果解譯器 / phase machine 放在 `JS-LOGIC`；手牌排版、點擊出牌、
  區域數量與選目標提示放在 `JS-RENDER` / `JS-EVENTS`。以 emoji 代替美術。
- **打磨：**`game-develop`——卡面美術（透過其 Phase 3 的 `imagen-portrait` / `imagen-ui`）、
  卡牌移動動畫（CSS animation / Canvas）、音效提示（Web Audio API）、QA。
- **平衡：**`game-balance-auditor` agent——模擬抽牌機率、資源曲線、各原型間的勝率；
  回饋到上方的設計參數。
- **持久化 / replay：**單檔內用 `localStorage` + 有 seed 的 RNG；
  不使用外部存檔系統。
- **對手 AI：**寫在 `JS-LOGIC`——依效果列表為每張可出的牌評分並挑選目標；
  和卡牌一樣保持資料驅動。

## 參考資料

- 效果 queue / stack、關鍵字 / 觸發、選取目標、deckbuilder vs. constructed 原型，
  以及洗牌公平性，請讀 `references/effect-resolution.md`。
