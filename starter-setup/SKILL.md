---
name: starter-setup
description: Starter kit 健檢式安裝/升級精靈。開場先健檢(盤點 CLAUDE.md/skills/agents),沒有的 skills/agents 直接裝、CLAUDE.md 缺的規則直接併入;裝完做最終健檢(CLAUDE.md 肥胖/重複/衝突、近似 skills/agents),只列建議不刪。觸發詞(「starter」與「新手包」互通):「裝 starter kit」「裝新手包」「starter 安裝」「新手包安裝」「starter 升級」「新手包升級」「starter 健檢」「新手包健檢」「檢查 starter」「檢查新手包」。
---

# Starter Kit 安裝/升級精靈

口令中的「starter」與「新手包」完全互通,使用者用哪個都認。

核心原則:**新增不問、刪改必問。** 沒有的直接裝、缺的規則直接併,全程不打斷;任何刪除、覆蓋、衝突處理一律列出來等使用者決定。**絕不刪除使用者自己的東西。**

## 流程總覽

```
開場健檢 → 分類 → 自動安裝(新裝/升級/併入 CLAUDE.md) → 最終健檢(只建議) → 結算表
```

只在兩個時間點跟使用者對話:開場一句「健檢完,我會直接裝 N 支、併 M 條,自改過的 K 支不動」,以及最終健檢的建議清單。中間不逐項問。

---

## 1. 開場健檢

一次盤完,不分段:

- `~/.claude/CLAUDE.md` 存在?(存在就**整份讀完**,記行數)
- `~/.claude/skills/` 現有清單:名稱、是否 junction、junction 目標是否還存在
- `~/.claude/agents/` 現有清單
- `%USERPROFILE%\starter-kit` 已 clone?(已有就 `git pull`,記 CHANGELOG 新增段落)
- secretary(skills/secretary)→ 歸「自有」,本精靈完全不碰
- `skills/imagen/.env` 存在?(影響生圖類能不能用)

## 2. 分類(kit 的 15 支 skills + 3 支 agents 逐一比對)

| 分類 | 判定 | 動作 | 問不問 |
|---|---|---|---|
| **沒有** | 使用者無同名資產 | 直接裝 | 不問 |
| **舊版** | 有同名且內容是 kit 同源舊版(diff 只有 kit 後續更新) | 備份到 `~/.claude/skills-backup/<名>-<日期>` 後直接升級 | 不問,結算表列出 |
| **自改過** | 有同名但內容與 kit 新舊版都不同 | 不動;差異摘要進最終健檢 | 問 |
| **自有** | kit 沒有的資產 | 不動 | 不問,結算表列「保留」 |

## 3. 自動安裝

1. **Clone**(未 clone 過才做):
   ```
   git clone <repo網址> %USERPROFILE%\starter-kit
   ```
2. **Skills 用 junction**(每支「沒有」與「舊版」各一條;PowerShell):
   ```powershell
   New-Item -ItemType Junction -Path "$env:USERPROFILE\.claude\skills\<名>" -Target "$env:USERPROFILE\starter-kit\skills\<名>"
   ```
3. **Agents 用拷貝**(散檔無法 junction):複製「沒有」的 `agents/*.md` 到 `~/.claude/agents/`。`my-voice.example.md` 不裝,結算表提示一句。升級時 agents 有 diff → 歸「自改過」進最終健檢
4. **imagen 設定**:`.env` 不存在就把 `.env.example` 複製成 `.env`,結算表提醒去 https://aistudio.google.com/apikey 拿 key 填入

## 4. CLAUDE.md 併入

- **沒有 CLAUDE.md** → 直接拷 `CLAUDE.starter.md` 為 `~/.claude/CLAUDE.md`,結束本節
- **有** → 先備份到 `~/.claude/skills-backup/CLAUDE.md-<日期>`,再對照 `CLAUDE.starter.md` 逐條做**語意比對**(不是字串比對),分三類:

| 類別 | 判定 | 動作 |
|---|---|---|
| **缺** | 他沒有、也沒有等價表述 | **直接併入**:以他原有的格式風格插到最相近的段落;沒有相近段落就新增段落 |
| **已有** | 有等價或更嚴格的規則 | 跳過 |
| **衝突** | 他有相反或互斥的規則(例:他寫「一律直推 main」,starter 寫「協作 repo 不直推」) | **不併**,兩條並列進最終健檢 |

鐵則:**原有內容一字不刪、不改寫、不重排。** 只加。

## 5. 最終健檢(只列建議,不動手)

裝完後跑一輪,產出一張「建議清單」,每項附一句理由與建議動作。**使用者明確說「刪 X」「合併 Y」「照建議做」才執行**,刪除/覆蓋前一律備份。

### CLAUDE.md

- **肥胖**:行數 > 180 或規則條目 > 60 → 警示,並指出最長的段落與低頻專用段(例:只在特定領域用到的整段)可搬去 skill 觸發式載入
- **重複**:語意重複或高度相近的規則(含剛併入的與原有的)→ 列出對照,建議保留哪條
- **衝突**:第 4 節列出的衝突對 → 建議留哪條或如何改寫成一條
- **死規則**:引用不存在的工具 / MCP / skill / 路徑 → 列出

### skills

- **近似**:名稱或 description 高度相近的兩支(kit 對自有、自有對自有都看)→ 列出,建議合併或刪其一
- **失效**:junction 目標不存在、資料夾沒有 SKILL.md、frontmatter 缺 name/description → 列出
- **自改過**(第 2 節):列客製段落摘要,問「保留你的改動合併新版 / 整個不動」

### agents

- **職責重疊**:description 高度相近 → 列出
- **孤兒**:CLAUDE.md 與任何 skill 都沒提到、也沒有觸發描述 → 提示「這支目前只能手動叫」

沒有任何發現就寫一句「健檢無異常」,不硬湊。

## 6. 結算表

```
🩺 開場健檢:CLAUDE.md 96 行 / skills 0 / agents 0 / secretary 無
✅ 新裝 skills(15,junction):product-planning、imagen …
✅ 新裝 agents(3):dialogue-writer、game-balance-auditor、planning-doc-auditor
⬆️ 升級:game-prototype(舊版→v1.1,原版備份於 skills-backup/)
📝 CLAUDE.md:併入 5 條(meta 規則、UI 繁中 …),原內容未動,備份於 skills-backup/
✋ 保留不動:你的 my-analyzer、secretary
⏭️ 未裝:my-voice.example.md(想要個人分身就複製成 agents/my-voice.md 再客製)

🩺 最終健檢建議(不動手,你決定):
  1. CLAUDE.md「資料分析」段 12 行只在統計任務用到 → 可搬成 skill,省 12 行
  2. skills/my-imagen 與 kit 的 imagen 功能重疊 → 建議刪其一或合併
  3. 衝突:你的「絕不推 main」vs starter「協作 repo 不直推」→ 建議改成後者
提醒:agents 新裝要重開 Claude Code;imagen 要填 .env
```

結算表後補一句選配指引(已裝 secretary 的人跳過):
「另有 Slack 秘書(自動掃待回覆+行程提醒),要裝的話把這個網址貼給我:
https://github.com/TimDaChung/secretary-kit」

**zip 備援**:沒有 git 也能裝——跟 Tim 拿最新 zip,解壓後把 `skills/` 內要用的資料夾複製到 `~/.claude/skills/`、agents 照拷,CLAUDE.md 併入與最終健檢流程相同;差別是不能「starter 升級」,更新要重新拿 zip。

---

## 升級(「starter 升級」/「新手包升級」)

1. `git -C %USERPROFILE%\starter-kit pull`
2. 摘要 CHANGELOG 新增段落
3. 重跑第 1 到 6 節:junction 裝的自動生效;新出現的 skills/agents 直接裝;CLAUDE.starter.md 新增的規則直接併;agents 有 diff 進最終健檢
4. **kit 已移除的 skill**(junction 目標消失,例:v1.3.0 把 generate2dsprite-chibi 併入 generate2dsprite)→ 歸「失效」進最終健檢,建議刪 junction 並說明併去哪裡;使用者同意才刪

## 健檢(「starter 健檢」/「新手包健檢」)

只跑第 1 節與第 5 節,不裝任何東西。給已裝完一陣子的人定期整理用。

---

## 鐵則

- **新增不問**:新裝 skills/agents、併入 CLAUDE.md 缺的規則,直接做,結算表交代
- **刪改必問**:刪除、覆蓋、衝突處理、自改過的合併,列建議等使用者說了才動
- 任何刪除/覆蓋前先備份到 `~/.claude/skills-backup/`
- CLAUDE.md 原有內容一字不刪、不改寫、不重排
- 不碰 settings.json、memory、與 kit 無關的任何檔案
- 同一步卡兩次 → 停止重試,整理錯誤請使用者找 Tim
