# CHANGELOG

## v1.4.0 (2026-09-14)

- **新 skill `data-report-builder`**(meta skill):一輪訪談(資料來源 / 指標公式 / 比較基準 / 異常門檻 / 分群 / 產出 / 週期)→ 在 `~/.claude/skills/report-<slug>/` 生成專屬的定期報表分析 skill(SKILL.md + 指標字典 + 報告模板 + 選配 load.py)→ 試跑一次 → 給排程建議。生成的 skill 屬使用者自有,不進 kit。附三個模板
- **企劃角色加數據能力**:CLAUDE.starter.md 專案角色表,企劃關注點加「KPI 定義、A/B 假設驗證」,產出加「指標定義表、數據解讀報告」,對應 skill 加 data-report-builder
- kit 回到 15 支 skills

## v1.3.0 (2026-09-14)

- **generate2dsprite-chibi 併入 generate2dsprite**:改用 `art_style = cel_shaded_chibi` 切換;chibi 專屬的頭身比鎖定、批次頭身 QC(5b)、風格區塊全部保留,標 **[chibi]** 只在該風格生效。原本兩支各帶一份完全相同的 processor 腳本與 modes.md,合併後只剩一份。kit 從 15 支變 14 支
- 已裝舊版 chibi 的人:「starter 升級」後 junction 目標會消失,最終健檢會列出建議刪除
- 安裝精靈升級節補「kit 已移除的 skill」處理
- CLAUDE.starter.md 瘦身:效率習慣的「派 sub-agent」併入專案角色的「重活派 agent」一條

## v1.2.0 (2026-09-14)

- **安裝精靈改健檢式流程**:開場健檢 → 自動安裝 → 最終健檢 → 結算表。原則改為「新增不問、刪改必問」:沒有的 skills/agents 直接裝、舊版備份後直接升級、CLAUDE.md 缺的規則直接併入(語意比對,衝突的不併改列出);中間不逐項問
- **新增最終健檢**:CLAUDE.md 肥胖(>180 行 / >60 條)、重複、衝突、死規則;skills 近似 / 失效 / 自改過;agents 職責重疊 / 孤兒。只列建議附理由,使用者說了才動
- **新口令「starter 健檢」**:只健檢不安裝,給已裝完的人定期整理用
- **口令「starter」與「新手包」互通**:「新手包安裝 / 升級 / 健檢」都認
- README 貼上指令、安裝說明同步更新

## v1.1.0 (2026-09-14)

- **15 支 skills 加執行角色標頭**:每支 SKILL.md 的 H1 之後加一行 `> **執行角色:X**`,標明該 skill 以企劃 / 工程 / 美術 / 數值 QA 哪個視角執行、關注什麼、完成後要切哪個視角複核。搭配 CLAUDE.md 的「專案角色」段落使用;沒有該段落也能獨立閱讀
- **CLAUDE.starter.md 加「專案角色」段落**:五個角色(企劃 / 工程 / 美術 / 數值 QA / 敘事)的關注點、產出、對應 skills 與 agents,加上切換與交接規則(自動切換、重活派 agent、跨角色審視、交接明講)。安裝精靈的 CLAUDE.md 語意合併會把這段列為候選

## v1.0.0 (2026-09-11)

首發:
- CLAUDE.starter.md 全域設定種子(含「被糾正就寫回」meta 規則)
- 15 支 skills:product-planning(新)、遊戲開發 4 支、生圖 8 支、webapp-testing
- 3 支 agents + my-voice 分身範本
- starter-setup 診斷式安裝精靈:盤點→分類(沒有/舊版/自改過/自有)→確認→動手,合併不覆蓋
