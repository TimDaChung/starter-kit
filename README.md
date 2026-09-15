# Claude Code Starter Kit

給團隊的 Claude Code 起手包:一份會自己長大的全域設定 + 15 支實戰 skills + 3 支品管 agents。
不含 Slack 秘書——要秘書另裝 [secretary-kit](https://github.com/TimDaChung/secretary-kit)。

## 最快安裝法

把下面整段貼給你的 Claude Code:

```
幫我安裝這個 starter kit:https://github.com/TimDaChung/starter-kit
步驟:1. git clone 到 %USERPROFILE%\starter-kit
2. 讀 starter-kit\skills\starter-setup\SKILL.md,照裡面的健檢式流程執行:
   先健檢我現有的 CLAUDE.md/skills/agents;我沒有的 skills/agents 直接裝、
   CLAUDE.md 缺的規則直接併入(原內容不動);我自己改過的東西不要碰。
   裝完做最終健檢,有重複/衝突/太肥的只列建議給我決定,不要自己刪。
```

流程:開場健檢 → 自動裝 → 最終健檢(只建議)→ 結算表。中間不會逐項問你。
裝完重開 Claude Code 一次(讓新 agents 生效)。

## 包內容

| 類別 | 內容 |
|---|---|
| 全域設定種子 | `CLAUDE.starter.md`(含最重要的 meta 規則:被糾正的事寫回檔案) |
| 企劃 | plan-dept1-writer(一部 house style 八章骨架,寫/改)、plan-doc-qa(一致性審查)、product-planning(通用版,跨部門/無範本/反寫 demo 的 fallback)、data-report-builder(一輪訪談→生成「定期分析某報表」的專屬 skill) |
| 遊戲開發 | game-prototype、game-develop、playtest-loop、card-game |
| 美術生圖 | imagen、imagen-portrait、imagen-ui、generate2dsprite(像素 / HD / cel-shaded chibi 用 art_style 切)、generate2dmap、image-to-prompt、batch-image-brief、art-style-guard(需自備 Gemini API key) |
| 測試 | webapp-testing(需 Python + Playwright) |
| 異常處理 | issue-triage(回報模式:標準異常回報;收單模式:維護端驗證修復 SOP) |
| Agents | dialogue-writer(對白)、game-balance-auditor(數值模擬)、planning-doc-auditor(企劃vs實作對照)、my-voice 範本(自己的分身自己建) |

企劃與遊戲原型類裝完即用;生圖、測試、playtest-loop 另需 Python 套件或 chrome-devtools MCP,安裝精靈會偵測缺什麼並問你要不要順手裝(細節見 `安裝說明.md` 前置表)。

## 升級

對 Claude 說「**starter 升級**」= git pull + 摘要更新內容 + 重跑健檢式流程(新 skill 直接裝、新規則直接併)。
對 Claude 說「**starter 健檢**」= 只健檢不安裝,定期整理 CLAUDE.md 與 skills 用。
口令裡的「starter」都可以換成「**新手包**」(「新手包升級」「新手包健檢」)。
你的 CLAUDE.md 原有內容、imagen 的 .env、你自己加的 skills/agents 永遠不會被升級動到。

## 已經拿過舊版 skills 的人

照常跑安裝——健檢會認出「Tim 以前給過的舊版」,備份後直接升級。
你自己改過的、或名字不同但功能相近的 skill / agent,以及 CLAUDE.md 裡跟 starter 重疊或衝突的規則,
最終健檢會逐對比較(觸發詞、流程完整度、死引用、你的客製內容),給「改用 kit 版 / 保留你的 / kit 版為底搬客製」三選一建議與理由,
你選了才動,動之前一定備份。
