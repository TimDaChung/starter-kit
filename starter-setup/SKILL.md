---
name: starter-setup
description: Starter kit 診斷式安裝/升級精靈。盤點使用者現有的 CLAUDE.md/skills/agents,對照 kit 內容分類(沒有→裝、舊版→升級、自改過→問、自有→不碰),合併不覆蓋。觸發詞:「裝 starter kit」「starter 安裝」「starter 升級」「檢查 starter」。
---

# Starter Kit 安裝/升級精靈

核心原則:**先盤點、再分類、經確認、才動手;絕不覆蓋或刪除使用者自己的東西。**

## 流程

### 1. 盤點現況

- `~/.claude/CLAUDE.md` 存在?(存在就**整份讀完**)
- `~/.claude/skills/` 現有清單(名稱+是否 junction)
- `~/.claude/agents/` 現有清單
- 已裝 secretary(skills/secretary)→ 歸「自有資產」,本精靈完全不碰(它有自己的 kit 與升級口令)

### 2. 對照分類(kit 的 15 支 skills + 3 支 agents 逐一比對)

| 分類 | 判定 | 動作 |
|---|---|---|
| **沒有** | 使用者無同名資產 | 建議新裝(junction) |
| **舊版** | 有同名且內容是 kit 同源舊版(diff 只有 kit 後續更新) | 列差異摘要,建議升級:刪舊資料夾改建 junction(先備份到 `~/.claude/skills-backup/<名>-<日期>`) |
| **自改過** | 有同名但內容與 kit 新舊版都不同 | 列出他的客製段落,問:「保留你的改動合併新版 / 整個不動」,選合併才動手 |
| **自有** | kit 沒有的資產 | 完全不碰,結算表列「保留」 |

### 3. 安裝動作

1. **Clone**(未 clone 過才做):
   ```
   git clone <repo網址> %USERPROFILE%\starter-kit
   ```
2. **Junction**(每支核可的 skill 一條;PowerShell):
   ```powershell
   New-Item -ItemType Junction -Path "$env:USERPROFILE\.claude\skills\<名>" -Target "$env:USERPROFILE\starter-kit\skills\<名>"
   ```
3. **Agents 用拷貝**(agents 是散檔無法 junction 單檔):複製 `agents/*.md` 到 `~/.claude/agents/`;升級時 diff 有變才問過再覆蓋。`my-voice.example.md` 只提示「想要個人分身就複製改名 my-voice.md 再客製」,不主動裝
4. **imagen 設定**:`skills/imagen/.env.example` → 引導使用者去 https://aistudio.google.com/apikey 拿 key,複製成 `.env` 填入(此檔 gitignore,不會被升級動到)
5. **新 agents 要重開 Claude Code 才會被認得**——裝完提醒

### 4. CLAUDE.md 語意合併(有既有檔才走,否則直接拷 CLAUDE.starter.md)

1. 整份讀完使用者的 CLAUDE.md
2. 對照 CLAUDE.starter.md,逐條找「他沒有、而且對他有價值」的規則,列清單附一句理由
3. 使用者勾選 → 只把勾選的條目**以他原有的格式風格**插入適當段落;**原有內容一字不刪、不改寫**
4. 特別推薦 meta 規則(「被糾正過的事寫回這份檔案」)——這是整包最有長期價值的一條

### 5. 結算表收尾

```
✅ 新裝:product-planning、imagen …(junction)
⬆️ 升級:game-prototype(舊版→v1.x,原版備份於 skills-backup/)
✋ 保留不動:你的 my-analyzer、secretary
📝 CLAUDE.md:併入 3 條(你勾的),原內容未動
⏭️ 你跳過:card-game
提醒:agents 新裝/更新要重開 Claude Code;imagen 要填 .env
```

結算表後補一句選配指引(已裝 secretary 的人跳過):
「另有 Slack 秘書(自動掃待回覆+行程提醒),要裝的話把這個網址貼給我:
https://github.com/TimDaChung/secretary-kit」

## 升級(「starter 升級」)

1. `git -C %USERPROFILE%\starter-kit pull`
2. 摘要 CHANGELOG 新增段落
3. 重跑第 2 步的分類診斷(junction 裝的自動生效;拷貝制的 agents 有 diff 才問)

## 鐵則

- 每個動作前先講要做什麼,批次徵求同意後才執行
- 任何刪除/覆蓋前先備份到 `~/.claude/skills-backup/`
- 不碰 settings.json、memory、與 kit 無關的任何檔案
- 同一步卡兩次 → 停止重試,整理錯誤請使用者找 Tim
