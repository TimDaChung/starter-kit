# Claude Code Starter Kit

給團隊的 Claude Code 起手包:一份會自己長大的全域設定 + 15 支實戰 skills + 3 支品管 agents。
不含 Slack 秘書——要秘書另裝 [secretary-kit](https://github.com/TimDaChung/secretary-kit)。

## 最快安裝法

把下面整段貼給你的 Claude Code:

```
幫我安裝這個 starter kit:https://github.com/TimDaChung/starter-kit
步驟:1. git clone 到 %USERPROFILE%\starter-kit
2. 讀 starter-kit\starter-setup\SKILL.md,照裡面的診斷流程執行:
   先盤點我現有的 CLAUDE.md/skills/agents,對照分類後經我確認才動手,
   不要覆蓋或刪除我自己的任何東西。
```

裝完重開 Claude Code 一次(讓新 agents 生效)。

## 包內容

| 類別 | 內容 |
|---|---|
| 全域設定種子 | `CLAUDE.starter.md`(含最重要的 meta 規則:被糾正的事寫回檔案) |
| 企劃 | product-planning(從零寫/從 demo 反寫/審修+Mermaid) |
| 遊戲開發 | game-prototype、game-develop、playtest-loop、card-game |
| 美術生圖 | imagen、imagen-portrait、imagen-ui、generate2dsprite(+chibi)、generate2dmap、image-to-prompt、batch-image-brief、art-style-guard(需自備 Gemini API key) |
| 測試 | webapp-testing |
| Agents | dialogue-writer(對白)、game-balance-auditor(數值模擬)、planning-doc-auditor(企劃vs實作對照)、my-voice 範本(自己的分身自己建) |

## 升級

對 Claude 說「**starter 升級**」= git pull + 摘要更新內容 + 重跑診斷。
你的 CLAUDE.md、imagen 的 .env、你自己加的 skills/agents 永遠不會被升級動到。

## 已經拿過舊版 skills 的人

照常跑安裝——診斷流程會認出「Tim 以前給過的舊版」,列出差異讓你決定要不要升級,
你自己改過的部分會被保留或經你確認才合併。
