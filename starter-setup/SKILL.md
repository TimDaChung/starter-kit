---
name: starter-setup
description: Starter kit 健檢式安裝/升級精靈：盤點→直接裝缺的→併入 CLAUDE.md→最終健檢只建議不刪。觸發詞：(starter|新手包)×(安裝|升級|健檢)。
---

# Starter Kit 安裝/升級精靈

> **執行角色：顧問**——盤點、比對、只建議不刪；安裝動作切**工程**視角確認路徑與 junction 正確。

口令中的「starter」與「新手包」完全互通，使用者用哪個都認。

核心原則：**新增不問、刪改必問。** 沒有的直接裝、缺的規則直接併，全程不打斷；任何刪除、覆蓋、衝突處理一律列出來等使用者決定。**絕不刪除使用者自己的東西。**

## 流程總覽

```
開場健檢 → 分類 → 自動安裝(新裝/升級/併入 CLAUDE.md) → 最終健檢(只建議) → 結算表
```

只在兩個時間點跟使用者對話：開場一句「健檢完，我會直接裝 N 支、併 M 條，自改過的 K 支不動」，以及最終健檢的建議清單。中間不逐項問。

---

## 1. 開場健檢

一次盤完，不分段：

- `~/.claude/CLAUDE.md` 存在？（存在就**整份讀完**，記行數）
- `~/.claude/skills/` 現有清單：名稱、是否 junction、junction 目標是否還存在
- `~/.claude/agents/` 現有清單
- `%USERPROFILE%\starter-kit` 已 clone？（已有就 `git pull`，記 CHANGELOG 新增段落）
- secretary(skills/secretary)→ 歸「自有」，本精靈完全不碰
- `skills/imagen/.env` 存在？（影響生圖類能不能用）
- **環境依賴**（企劃 / 原型類 7 支不需要，只影響生圖、測試、試玩迴圈）：
  - `python --version` 有 3.10+？
  - `python -c "import PIL"`、`python -c "import playwright"` 各自過不過？
  - Playwright 的 Chromium：`%LOCALAPPDATA%\ms-playwright\chromium*` 目錄存在？
  - `claude mcp list` 有 `chrome-devtools`？`npx --version` 有 Node？

## 2. 分類（kit `skills/` 目錄內的每一支 skill + `agents/` 內每支 agent 逐一比對）

| 分類 | 判定 | 動作 | 問不問 |
|---|---|---|---|
| **沒有** | 使用者無同名資產 | 直接裝 | 不問 |
| **舊版** | 有同名且內容是 kit 同源舊版（diff 只有 kit 後續更新） | 備份到 `~/.claude/skills-backup/<名>-<日期>` 後直接升級 | 不問，結算表列出 |
| **自改過** | 有同名但內容與 kit 新舊版都不同 | 不動；進最終健檢的「換版評估」 | 問 |
| **近似** | 名稱不同但功能高度重疊（description / 觸發詞 / 流程相近） | 不動；進最終健檢的「換版評估」 | 問 |
| **自有** | kit 沒有的資產 | 不動 | 不問，結算表列「保留」 |
| **使用者略過** | 名字列在 `~/.claude/starter-skip.md` | 不裝、不升級 | 不問，結算表列「略過」，附「要裝就說『裝回 X』」 |

## 3. 自動安裝

1. **Clone**（未 clone 過才做）：
   ```
   git clone https://github.com/TimDaChung/starter-kit %USERPROFILE%\starter-kit
   ```
2. **Skills 用 junction**（每支「沒有」與「舊版」各一條；PowerShell）：
   ```powershell
   New-Item -ItemType Junction -Path "$env:USERPROFILE\.claude\skills\<名>" -Target "$env:USERPROFILE\starter-kit\skills\<名>"
   ```
3. **Agents 用拷貝**（散檔無法 junction）：複製「沒有」的 `agents/*.md` 到 `~/.claude/agents/`。`templates/my-voice.example.md` 是範本不是 agent，不裝，結算表提示一句。升級時 agents 有 diff → 歸「自改過」進最終健檢
4. **imagen 設定**：`.env` 不存在就把 `.env.example` 複製成 `.env`，結算表提醒去 https://aistudio.google.com/apikey 拿 key 填入
5. **略過清單**：使用者說「X 不要裝」「不要 X」→ 把 X 的名字寫進 `~/.claude/starter-skip.md`（一行一個，可加一句原因），之後安裝與升級都跳過它；說「裝回 X」→ 從檔案移除該行並立即裝。沒有這個檔就代表沒有略過任何東西
6. **環境依賴**（開場健檢有缺才做）：列一張「缺什麼 → 影響哪些 skill → 指令」的表，**問一次**「要不要我順手裝？」。這是 kit 檔案以外唯一會動到使用者環境（Python 套件、MCP 設定）的動作，所以不套「新增不問」；同意才依序執行，不同意或失敗就結算表列「未裝，影響 X」，不重試第三次。指令固定用這幾條：
   ```
   pip install -r %USERPROFILE%\starter-kit\requirements.txt
   python -m playwright install chromium
   claude mcp add --scope user chrome-devtools -- cmd /c npx chrome-devtools-mcp@latest --browser-url http://127.0.0.1:9222
   ```
   沒有 Python / Node 的人給 `winget install Python.Python.3.12` / `winget install OpenJS.NodeJS.LTS`，裝完請他重開終端再叫一次「starter 升級」，本精靈不自己裝 runtime。裝了 MCP 要提醒：Chrome 需以 `--remote-debugging-port=9222` 啟動 playtest-loop 才讀得到玩家分頁，且新 MCP 要重開 Claude Code 才生效

## 4. CLAUDE.md 併入

- **沒有 CLAUDE.md** → 直接拷 `CLAUDE.starter.md` 為 `~/.claude/CLAUDE.md`，結束本節
- **有** → 先備份到 `~/.claude/skills-backup/CLAUDE.md-<日期>`，再對照 `CLAUDE.starter.md` 逐條做**語意比對**（不是字串比對），分三類：

| 類別 | 判定 | 動作 |
|---|---|---|
| **缺** | 他沒有、也沒有等價表述 | **直接併入**：以他原有的格式風格插到最相近的段落；沒有相近段落就新增段落 |
| **已有** | 有等價或更嚴格的規則 | 跳過 |
| **衝突** | 他有相反或互斥的規則（例：他寫「一律直推 main」，starter 寫「協作 repo 不直推」） | **不併**，兩條並列進最終健檢 |

鐵則：**原有內容一字不刪、不改寫、不重排。** 只加。

## 5. 最終健檢（只列建議，不動手）

裝完後跑一輪，產出一張「建議清單」，每項附一句理由與建議動作。**使用者明確說「刪 X」「合併 Y」「照建議做」才執行**，刪除/覆蓋前一律備份。

### CLAUDE.md

- **肥胖**：行數 > 180 或規則條目 > 60 → 警示，並指出最長的段落與低頻專用段（例：只在特定領域用到的整段）可搬去 skill 觸發式載入
- **重複 / 衝突**：語意重複或相反的規則對（含剛併入的與原有的、第 4 節列出的衝突）→ 進「換版評估」逐對比較
- **舊版 starter**：使用者的 CLAUDE.md 整份或大段是舊版 `CLAUDE.starter.md` 的複本 → 列出 kit 後續改動的 diff 摘要，進「換版評估」
- **死規則**：引用不存在的工具 / MCP / skill / 路徑 → 列出
- **瘦身的邊界**：只建議動重複、死引用、過時路徑；使用者的角色定位句、原則句、meta 規則一律不列為瘦身對象，「這個工具他還沒接上」不是刪句子的理由

### 環境

- **仍缺的依賴**：第 3 節第 6 步沒裝或裝失敗的 → 逐項列「缺 X → Y skill 不能跑 / 退到 Z fallback」（例：缺 chrome-devtools MCP → playtest-loop 退到手貼 `exportDevNotes()`；缺 playwright → webapp-testing 不能跑，game-develop 的玩法 QA 走 chrome-devtools fallback）
- **僅健檢模式**（第 1 節 + 第 5 節）：一樣列出來，附指令，不裝

### skills

- **近似 / 自改過**（第 2 節）：每一對進「換版評估」
- **自有對自有近似**：使用者自己兩支功能重疊 → 列出，建議合併或刪其一（不做換版評估，kit 沒有對應版本）
- **失效**：junction 目標不存在、資料夾沒有 SKILL.md、frontmatter 缺 name/description → 列出
- **缺角色標頭**：SKILL.md 的 H1 之後沒有 `> **執行角色：X**` 一行 → 列出，建議補（kit 的 skill 不會缺；自有 skill 缺的話附一句建議寫法）

### agents

- **職責重疊**：description 高度相近 → 使用者 agent 對 kit agent 進「換版評估」；自有對自有只列出
- **孤兒**：CLAUDE.md 與任何 skill 都沒提到、也沒有觸發描述 → 提示「這支目前只能手動叫」

### 換版評估（同名自改過 / 近似 skill / agent 重疊 / CLAUDE.md 重複、衝突、舊版）

目的：幫使用者決定**要不要改用 kit 版**，不是幫他保留現狀。每一對（他的 X vs kit 的 Y）都跑：

1. **兩份整份讀完**，不憑名稱或 description 猜
2. **列比較表**，欄位固定：觸發詞覆蓋、流程完整度、死引用 / 失效路徑數、與 kit 其他 skill / agent 的銜接、角色標頭、行數（約略 token）、他的客製內容（他自己加的規則與案例，逐條列）
3. **三選一建議，附一句理由**：
   - **A 改用 kit 版**：他沒有客製，或客製已被 kit 版涵蓋
   - **B 保留他的**：他的版本更完整、綁定部門流程，或客製量大到搬不動（例：部門 house-style 企劃 skill 對 kit 的 product-planning）
   - **C kit 版為底 + 搬客製**：kit 版功能較新，他有幾條值得留的客製
4. **預設偏向 A / C**，理由要講：kit 版會隨「starter 升級」持續更新，自有版不會；junction 裝的 kit 版不占他的維護成本
5. **客製內容的落點**（選 C 時）：通用的 → 建議回饋給 Tim 進 kit；個人的 → 寫進他的 CLAUDE.md 對應段落（永遠載入，效果等同寫在 skill 裡）；不想動 CLAUDE.md → 保留自有複本不裝 junction，結算表標「放棄自動升級」
6. **CLAUDE.md 的規則對**同樣三選一：留他的 / 換 starter 的 / 改寫成一條；判準：更具體、附案例、較新的優先
7. 使用者選了才動；改用或覆蓋前備份到 `~/.claude/skills-backup/`；選 B 的在結算表標「保留自有，不升級」

輸出格式：每對一小節，「比較表 → 建議 A/B/C + 理由 → 選 C 時客製怎麼搬」，不超過 15 行。

沒有任何發現就寫一句「健檢無異常」，不硬湊。

## 6. 結算表

```
🩺 開場健檢:CLAUDE.md 96 行 / skills 0 / agents 0 / secretary 無
🧰 環境:Python 3.13 ✔ / Pillow ✔ / Playwright ✔(本次裝) / chrome-devtools MCP ✘(你說先不裝→playtest-loop 退手貼模式) / Gemini key ✘(.env 待填)
✅ 新裝 skills(N,junction):product-planning、imagen …
✅ 新裝 agents(3):dialogue-writer、game-balance-auditor、planning-doc-auditor
⬆️ 升級:game-prototype(舊版→v1.1,原版備份於 skills-backup/)
📝 CLAUDE.md:併入 5 條(meta 規則、UI 繁中 …),原內容未動,備份於 skills-backup/
✋ 保留不動:你的 my-analyzer、secretary
⏭️ 未裝:templates/my-voice.example.md(想要個人分身就複製成 ~/.claude/agents/my-voice.md 再客製)
⛔ 略過(依 starter-skip.md):generate2dmap、imagen-ui(要裝就說「裝回 X」)

🩺 最終健檢建議(不動手,你決定):
  1. CLAUDE.md「資料分析」段 12 行只在統計任務用到 → 可搬成 skill,省 12 行
  2. 換版:你的 my-imagen vs kit imagen → 建議 C(kit 版為底 + 你的 2 條客製寫進 CLAUDE.md);理由:kit 版觸發詞多 3 組、有 magenta 去背流程且會升級
  3. 換版:你的 CLAUDE.md「絕不推 main」vs starter「協作 repo 不直推」→ 建議換 starter 的;理由:更具體,solo repo 不受限
提醒:agents 新裝要重開 Claude Code;imagen 要填 .env
```

結算表後補一句選配指引（已裝 secretary 的人跳過）：
「另有 Slack 秘書（自動掃待回覆+行程提醒），要裝的話把這個網址貼給我：
https://github.com/TimDaChung/secretary-kit」

**zip 備援**：沒有 git 也能裝——跟 Tim 拿最新 zip，解壓後把 `skills/` 內要用的資料夾複製到 `~/.claude/skills/`、agents 照拷，CLAUDE.md 併入與最終健檢流程相同；差別是不能「starter 升級」，更新要重新拿 zip。

---

## 升級（「starter 升級」/「新手包升級」）

1. `git -C %USERPROFILE%\starter-kit pull`
2. 摘要 CHANGELOG 新增段落
3. 重跑第 1 到 6 節：junction 裝的自動生效；新出現的、以及使用者先前沒裝的 skills/agents 直接補裝（`starter-skip.md` 內的除外）；CLAUDE.starter.md 新增的規則直接併；agents 有 diff 進最終健檢
4. **kit 已移除的 skill**（junction 目標消失，例：v1.3.0 把 generate2dsprite-chibi 併入 generate2dsprite）→ 歸「失效」進最終健檢，建議刪 junction 並說明併去哪裡；使用者同意才刪

## 健檢（「starter 健檢」/「新手包健檢」）

只跑第 1 節與第 5 節，不裝任何東西。給已裝完一陣子的人定期整理用。

---

## 鐵則

- **新增不問**：新裝 skills/agents、併入 CLAUDE.md 缺的規則，直接做，結算表交代
- **刪改必問**：刪除、覆蓋、衝突處理、自改過的合併，列建議等使用者說了才動
- 任何刪除/覆蓋前先備份到 `~/.claude/skills-backup/`
- CLAUDE.md 原有內容一字不刪、不改寫、不重排
- 不碰 settings.json、memory、與 kit 無關的任何檔案；Python 套件與 MCP 設定是唯一例外，且**問過才裝**（第 3 節第 6 步）
- 同一步卡兩次 → 停止重試，整理錯誤請使用者找 Tim
