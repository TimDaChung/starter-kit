---
name: game-develop
version: 1.0.0
description: |
  將原型升級為發行級單檔 HTML 遊戲：AI 生圖、平衡 polish、對白、QA。
  目標：高完成度 demo（itch.io 等級，不含金流帳號）。
  可獨立啟用、亦可接續 game-prototype 產出。
  主動調度子 skill / agent；沒對應工具的部分自己做。
  MANUAL TRIGGER ONLY：使用者輸入 /game-develop 才啟動。
allowed-tools:
  - Read
  - Write
  - Edit
  - Glob
  - Grep
  - Bash
  - AskUserQuestion
  - Skill
  - Agent
  - TaskCreate
  - TaskUpdate
  - TaskList
---

# /game-develop — 單檔 HTML 遊戲發行級升級

> **執行角色：工程（主導）**——依階段調度**美術 / 數值 / 敘事**角色對應的 skill 與 agent；每段產出回**顧問**視角整合，不直接轉貼 agent 全文。

把原型升級為高完成度 demo（itch.io / 個人上架等級）。**主動調度** imagen / sprite / map 系列生圖 skill、agents（balance / dialogue）與 `webapp-testing`（QA）。**沒對應工具的部分自己做**（音效 / 自訂特效 / 轉場動畫等）。

---

## 啟動：每次 invoke 第一步（Resume 偵測）

讀取：
1. 專案目錄內所有 `*.html`（Glob）
2. `GAME_SPEC.md`（如存在）
3. `GAME_TODO.md`（如存在）

判斷狀態：

| 狀態 | 動作 |
|------|------|
| 沒 HTML、沒 SPEC | **直接從 0 起跑**：先做 SPEC（brainstorm 玩法核心 + 寫 GAME_SPEC.md）→ 建專案目錄 → 建 HTML 骨架 → 進 Phase 1。**不要強迫先跑 `/game-prototype`**（除非 user 主動要求或玩法核心極不明確） |
| 有 HTML、沒 SPEC | 詢問 user：「要從現有 HTML 反推 SPEC 嗎？」 |
| HTML + SPEC，沒 TODO | 從 templates 複製 GAME_TODO.template.md → 進 Phase 1 |
| HTML + SPEC + TODO，TODO 有未完成 | **自動接續未完成清單，phase 連續推進到全完才回報**（不 AskUserQuestion） |
| HTML + SPEC + TODO，TODO 全 ✅ | 告訴 user：「develop 流程跑完，可手動 ship / 上架」 |

每次進場給一句狀態摘要：「上次做到 X / Y / Z 已完成，本次推進 A / B / C」即開工，不等 user 確認。

---

## 核心紀律（不可違反）

1. **整套 5 phases 一次跑完才回報**：phase 之間自動推進，不對 user check-in、不問「要繼續嗎」、不要每張生圖叫 user 看、**沒有 session batch 上限這回事**——同類別有 N 張就連續呼叫 N 次直到全部生完。**唯一例外**：碰到不可逆動作（破壞性檔案操作）或硬決策（玩法核心改動 / 數值範圍超出 SPEC）才停下來問。否則一路跑到 Phase 5.4 完才一次性給總結摘要
2. **不外包就自己做**：遇到對應 sub-skill / agent → invoke；沒對應的（音效 / 自訂特效 / 動效 / 粒子）→ 用原生 web 技術做（Web Audio API / CSS animation / Canvas）
3. **單檔不拆**：HTML 維持單檔。改動 100% 用 Edit + section marker，不重寫整檔
4. **每張生圖獨立 checkpoint**：Phase 3 每張生完立即更新 TODO（含路徑、版本、決策註解），但**不打擾 user**
5. **同類批次一致性**：呼叫生圖 sub-skill 前，把 SPEC 的 style-lock（風格代號 / 比例 / 視角 / 面向 / 光源）一併傳過去（規則：同類別資產 style-lock 一致）。同類別第 1 張 baseline 自我驗證通過後，剩餘張數**並行 background bash** 一次發完（generate.py 是 IO-bound，並行省時間）
6. **行數監控**：HTML 5000 行→提醒 grep marker；8000 行→提醒瘦身（不強制拆檔）
7. **section-by-section 整合**：Phase 4 每次 Edit 針對 single section，多 section 改動拆多次 Edit

---

## Phase 結構（彈性順序，建議從 0 起）

| Phase | 工作 | 主要外包 | 完成標準 |
|-------|------|---------|---------|
| **0** | 診斷 + 對齊（每次 invoke 跑） | — | 讀完兩檔 + 確認本次推進項目 |
| **1** | Design system 建立 | —（skill 自己用 CSS variables 規劃） | CSS variables 內嵌 + DESIGN.md 完成 |
| **2** | 素材清單規劃 | — | TODO「素材」分區建立 |
| **3** | 批次生圖 | imagen-portrait / imagen-ui / generate2dsprite / generate2dmap / imagen | 每張：路徑寫進 TODO，標 ✅ |
| **4** | 素材整合（emoji → 真圖） | — | section-by-section 替換 + 不破 layout |
| **5** | Polish | game-balance-auditor / dialogue-writer / self-walkthrough（chrome-devtools MCP）/ `webapp-testing` | 平衡達標 + 對白 + 視覺 + 玩法 QA 全過 |

---

## Phase 1：Design System 建立

**做法**：skill 自己用 CSS variables 規劃（配色 / 字級 / 間距 / 圓角 / 陰影），依 SPEC 風格代號定案；user 已有設計方向時直接沿用。

**產出**：
- HTML 內 `/* === SECTION: CSS-VARIABLES === */` 區塊更新（用 Edit）
- DESIGN.md（記錄風格代號、色票、字級階、元件規則，供 Phase 3 生圖 style-lock 引用）

完成後標 TODO Phase 1 ✅，並把跳過理由寫進 TODO inline 註解（`└ 理由：...`）。

---

## Phase 2：素材清單規劃

從 GAME_SPEC.md 的 emoji 對照表反推：

**Sub-skill 強制對應表**（按用途選，不要憑感覺挑）：

| 素材用途 | 強制使用 | 為什麼 |
|---------|---------|--------|
| **角色 / 物件，遊戲中會動或需要狀態切換**（揮棒、投球、走路、待機、被擊中、攻擊…）| **`generate2dsprite`**（chibi 風用 `art_style=cel_shaded_chibi`）| 內建 magenta chroma key + processor，產出真透明 PNG + 多 frame sheet |
| **小物件 sprite**（球、子彈、道具、特效粒子）| **`generate2dsprite`** | 同上，要透明背景才能疊在背景上 |
| **背景 / 地圖 / 場景**（球場、戰鬥背景、村莊、戰場）| **`generate2dmap`** | 場景專用 pipeline，比例 / 透視 / 圖層處理對 |
| **UI 元件**（button / icon / frame / banner / popup / coin / chip）| **`imagen-ui`** | imagen-ui 產出 magenta 背景，用 generate2dsprite 的 processor 去背，得到真透明 PNG |
| **靜態角色立繪**（封面圖、選角畫面，純單張無動畫）| `imagen-portrait` | 半身 / 全身大圖，內建後製 |
| **通用單張插圖**（splash art、敘事插畫、無 alpha 需求）| `imagen` | **僅限**真的不需要透明背景的場合 |

**反模式**：
- ❌ 用 `imagen` 生「透明背景 PNG」——`imagen` 不跑後製，prompt 寫 transparent 也沒用，會出 RGB 圖
- ❌ 用 `imagen` 生會動的角色——沒有 frame sheet 邏輯，只能拿到單張靜態
- ❌ 信任 sub-agent 回報「透明背景 PNG」就算數——必須跑 alpha 驗證（見 Phase 3 驗證步驟）

寫進 GAME_TODO.md「素材」分區，每項標：尺寸 / 風格 / 優先級 / **對應 skill（依上表強制）/ 動畫 frame 清單（如有）**。

---

## Phase 3：批次生圖

### 呼叫 sub-skill 前的標準資訊包（每張都要傳）

從 SPEC / DESIGN.md 取出並傳給 sub-skill：
- **風格代號**（例：「米哈遊風 / 暗黑奇幻 / 像素 retro」）
- **比例 / 尺寸**
- **視角**（半身 / 全身 / 側面 / 俯視）
- **面向方向**
- **光源方向**
- **配色提示**（accent / danger / 中性色）
- **角色 / 物件描述**

### 標準執行順序（同類別所有張數一次跑完）

1. **第 1 張當 baseline**：序列跑 1 張、Read 看圖、自我驗證風格 OK（user 已授權審美決策時）
2. **剩餘張數並行跑**：寫好所有 prompt.txt → 全部 `run_in_background=true` 同時送 → 等通知收齊
3. **逐張 Read 驗證 + 更新 TODO**：每張寫路徑 + 版本，標 ✅；明顯失敗的當場 retake
4. **同類別全完才接下一類**（立繪→sprite→賽道→UI 順序可調）
5. **跑驗證 step（必做）→ 通過才接 Phase 4**

### Phase 3 驗證 step（每張都要跑，不能信 sub-agent 自報）

**Alpha channel 驗證**（凡是用在「需透明背景」的 sprite / icon / button）：

```bash
python -X utf8 -c "
from PIL import Image
import sys
for p in sys.argv[1:]:
    im = Image.open(p)
    if im.mode != 'RGBA':
        print(f'[FAIL] {p}: mode={im.mode}, NO ALPHA'); continue
    a = im.split()[-1]
    amin, amax = a.getextrema()
    if amax == 0 or amin == 255:
        print(f'[FAIL] {p}: alpha 全透或全不透 [{amin},{amax}]'); continue
    print(f'[OK]   {p}: RGBA alpha [{amin},{amax}]')
" assets/path/to/img1.png assets/path/to/img2.png
```

驗證規則：
- **角色 / sprite / 透明 UI 元件**：mode 必須是 RGBA，alpha range 必須跨越 0~255
- **單張靜態插圖（splash / 純背景）**：可以 RGB，不強制 alpha
- 任何「需要疊在別的 layer 上」的素材 → 強制 RGBA + alpha 跨 0~255
- **Sub-agent 回報「透明背景 PNG」≠ 真有 alpha**——一律當未驗證，必跑上面的 PIL 檢查

驗證失敗 → 直接 retake（不要試圖手動 chroma key 救，原圖很可能不是 magenta 底）。

**動畫 frame 完整度驗證**（用 generate2dsprite 的角色）：
- 檢查 frame sheet 是否含 SPEC 列出的所有 frame（idle / windup / swing / hit ...）
- 缺 frame → retake 該角色

### 並行範例

```bash
# Two portraits in parallel: prompts prepared beforehand in prompts/*.txt, Bash call run_in_background=true.
cd "<project-dir>" && \
python ~/.claude/skills/imagen/bin/generate.py --prompt "$(cat prompts/hero_a.txt)" --ratio 3:4 --output assets/portrait/hero_a.png & \
python ~/.claude/skills/imagen/bin/generate.py --prompt "$(cat prompts/hero_b.txt)" --ratio 3:4 --output assets/portrait/hero_b.png & \
wait
```

（sprite / UI / map 類改呼叫對應 sub-skill 的 generate.py，參數以各自 `--help` 為準。）完成通知收齊後一次 Read 所有張數驗證。

generate.py 一次 60–90 秒，並行 5 張 ≈ 串行 1 張的時間。**不要序列跑同類別**。

---

## Phase 4：素材整合（emoji → 真圖）

**section-by-section** 替換流程：

1. 從 TODO 的「Phase 4 整合」分區找下一個未做項
2. `grep` HTML 內對應 emoji 的所有出現位置
3. 用 Edit 把該 section 內的 emoji → `<img src="...">` 或 CSS background
4. 用 chrome-devtools MCP 跑一輪確認 layout 沒破
5. TODO 該項標 ✅

### 遇到 layout 不合（圖太大 / 比例怪）

逐輪嘗試：
1. 第一輪：調 CSS（width / max-width / object-fit）
2. 第二輪：調容器 / 元件結構（aspect-ratio 容器、grid 欄寬、圖層順序）
3. 第三輪：retake 圖（標記 TODO 該項回到 Phase 3）

---

## Phase 5：Polish（順序固定）

**強制順序**：balance → dialogue → design review（self-walkthrough）→ qa（webapp-testing）

理由：數值不對美化沒意義；對白可能影響 UI 文字長度；視覺 QA 需要對白完成；玩法 QA 是 end-to-end 最後關卡。

### 5.1 Balance（呼叫 game-balance-auditor agent）

把 SPEC 的「平衡假設」傳給 agent：
```
請依 GAME_SPEC.md 的「平衡假設」段，跑 simulation：
- 各角色 / 職業勝率分布
- 數值平衡（HP / 攻擊力 / 機率分布）
- 變異數 / 期望值
回報：哪些參數需要調整、調整方向、預期影響。
```

收 agent report 後，由主對話決定要不要動 HTML 內參數。

**沒呼叫 agent 時的 fallback**：skill 自己用 Bash + python（或 node）跑簡易 simulation 1000 場，輸出勝率分布。

完成後標 TODO Phase 5.1 ✅，inline 註解寫結果摘要。

### 5.2 Dialogue（呼叫 dialogue-writer agent）

把 SPEC 的「角色 persona」段傳給 agent：
```
請依 GAME_SPEC.md「角色 persona」段，為以下情境寫對白多版草稿：
- {遊戲場景 / 事件}
每段給 2-3 版讓我挑。
```

主對話收 agent 多版草稿後**自行從每組挑最貼 persona 的一版貼進 HTML**（不打擾 user）；最終回報時把所有採用版本+備案列在摘要供 user 一次調整。

**沒呼叫 agent 時的 fallback**：skill 自己依 persona 寫對白。

完成後標 TODO Phase 5.2 ✅。

### 5.3 Design review（自行 self-walkthrough）

自行 self-walkthrough：用 chrome-devtools MCP 截圖逐畫面檢查（`navigate_page` 開 HTML → 每個畫面 `take_screenshot` → Read 看圖），對照 DESIGN.md 查邊距 / 對齊 / 字級 / 色票一致性，發現 issue 直接 Edit 修。修完後 TODO 標 ✅，inline 註解列發現的 issue 與修法。

**chrome-devtools 不可用時的 fallback**：grep HTML 逐 section 靜態檢查 CSS variables 是否被 hard-code 色值繞過、字級是否落在 DESIGN.md 階梯內。

### 5.4 QA（呼叫 `webapp-testing` skill，Playwright）

```
Skill: webapp-testing
```

流程：
1. 依 SPEC 的 state machine，把每條路徑（Title → Setup → Round → Resolve → End、重玩、異常輸入）列成測試案例
2. 依 `webapp-testing` 寫 Playwright 腳本（`file://` 開單檔 HTML，見其 `examples/static_html_automation.py`），每案例斷言關鍵 DOM 狀態 + 收 console error（見 `examples/console_logging.py`）
3. 跑腳本 → 失敗案例逐條 Edit 修 → 重跑到全過
4. 腳本存 `<project-dir>/tests/`，TODO 標 ✅ 並列 bug 清單 + fix

**Playwright 不可用時的 fallback**：用 chrome-devtools MCP（`navigate_page` / `click` / `evaluate_script`）依 state machine 路徑逐條手動走。

---

## 整合 map（總表）

| 工作 | 外包 | Phase | 沒外包時 fallback |
|------|------|-------|-------------------|
| Design system | 無外包 | 1 | skill 用 CSS variables 自己規劃 |
| **角色 / 物件 sprite（含動畫 frame）** | **`generate2dsprite`**（chibi 風用 `art_style=cel_shaded_chibi`）| 3 | — |
| **小物件 sprite（球、子彈、特效等）** | **`generate2dsprite`** | 3 | — |
| **背景 / 地圖 / 場景** | **`generate2dmap`** | 3 | — |
| **UI 元件**（button / icon / frame / banner）| **`imagen-ui`** | 3 | — |
| 靜態角色立繪（無動畫，純單張）| `imagen-portrait` | 3 | — |
| 通用單張插圖（splash / 不需 alpha）| `imagen` | 3 | **僅限**不需透明背景的場合 |
| Balance | `game-balance-auditor` agent | 5 | skill 跑簡易 sim（Bash+python） |
| 對白 | `dialogue-writer` agent | 5 | skill 自己寫 |
| 視覺 QA | 無外包（self-walkthrough：chrome-devtools MCP 截圖逐畫面檢查） | 5 | grep 靜態檢查 |
| 玩法 QA | `webapp-testing`（Playwright） | 5 | skill 用 chrome-devtools MCP 跑互動測試 |
| **動效 / 音效 / 特效 / 粒子** | **無外包** | 任何 | **skill 自己做（CSS animation / Web Audio API / Canvas）** |

---

## 工作量切分（內部追蹤，不切 session）

任務要動 5+ 處或寫 500+ 行時：
1. 先把任務拆成「子任務清單」寫進 GAME_TODO.md
2. 本 session 內**逐項做完**（用並行 / 連續 Edit / 連續 Bash 推進），每完成一項標 ✅
3. 全完才回報——**不在中途切 session、不要求 user 下次 invoke 接續**

session 內部的 task tracker（TaskCreate / TodoWrite）可用來追蹤本次推進的子項，但不影響「一次做完」原則。

---

## 行數監控（提醒 only）

- HTML 5000 行：提醒「未來改動建議用 grep marker 精準定位」
- HTML 8000 行：提醒「考慮哪些 section 可以瘦身（例如 emoji 對照表搬到 SPEC）」

**不強制拆檔**——user 偏好單檔分配給別人方便。

---

## 最終回報模板（Phase 5.4 完才送）

整套 5 phases 跑完才送一次性摘要，格式：

```
== Develop 全跑完摘要 ==

Phase 1 ✅ Design system：[CSS variables / DESIGN.md 路徑]
Phase 2 ✅ 素材清單：N 項
Phase 3 ✅ 生圖：[N 張，路徑列表 + 每張版本 + 關鍵決策]
Phase 4 ✅ 整合：[替換清單 + layout 調整]
Phase 5.1 ✅ Balance：[RTP / 勝率 / 數值微調]
Phase 5.2 ✅ Dialogue：[對白採用版 + 備案]
Phase 5.3 ✅ Design review：[發現的視覺 issue + 修法]
Phase 5.4 ✅ QA：[bug 清單 + fix]

== 已 flag 給 user 看的 ==
- [需要 user 主觀決策的項目，例：「破產率 18.7% 偏高，要更友善請說」]

== 已知限制（沒辦法做完的） ==
- [例：「chrome-devtools MCP 不可用，視覺 QA 改跑 grep 靜態檢查 fallback」]

檔案位置：[專案根目錄]
建議下一步：[例：「邀人試玩 / ship 上 itch.io」]
```

---

**End of skill.**
