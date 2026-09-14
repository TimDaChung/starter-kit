# CHANGELOG

## v1.5.1 (2026-09-14)

- **安裝精靈最終健檢加「換版評估」**:同名自改過的 skill、名稱不同但功能近似的 skill、agent 職責重疊、CLAUDE.md 重複 / 衝突 / 舊版 starter 複本,每一對都整份讀完 → 固定欄位比較表(觸發詞、流程完整度、死引用、銜接、角色標頭、行數、客製內容)→ 三選一建議附理由(A 改用 kit 版 / B 保留自有 / C kit 版為底 + 搬客製)。預設偏向 A / C,理由是 kit 版會隨升級更新;客製內容的落點(回饋進 kit / 寫進 CLAUDE.md / 保留複本放棄升級)明寫。使用者選了才動,動前備份
- 分類表加「近似」一類;README 同步

## v1.5.0 (2026-09-14)

全 kit 健檢後的第一、二批修復(41 檔)。目標:每支 skill 第一次用就能跑。

**首次使用會失敗的問題**
- `imagen/bin/generate.py`:比例與尺寸依官方文件改為 Pro 模型實際支援的清單(1:1、2:3、3:2、3:4、4:3、4:5、5:4、9:16、16:9、21:9;1K / 2K / 4K),移除 Flash 專用的 512 與 1:4 / 1:8 / 4:1 / 8:1;API key 改走 `x-goog-api-key` header;`.env` 值去引號;未知參考圖副檔名明確報錯;全檔英文化並補齊 type hints
- `imagen-ui`:boilerplate 從「透明背景」改為 magenta 背景 + generate2dsprite processor 去背(Gemini 輸出本來就沒有 alpha);button / tab / progress_bar / divider 改「生 21:9 再裁」;補工程視角 QC
- `imagen`:Phase 5 改呼叫 `bin/generate.py`,刪手刻 curl;API / Prompt 模式改以 `.env` 或 `GEMINI_API_KEY` 存在與否判定
- `generate2dmap` 與 references:6 處 `lib/gen_image.py` 改為 `imagen/bin/generate.py`;單 prop 處理改走 `extract_prop_pack.py --rows 1 --cols 1`(原指令不會產出 `prop.png`)
- `game-balance-auditor`:模擬腳本從 `/tmp` 改到專案 `.claude/scratch/`
- `webapp-testing`:examples 硬編的 `/mnt/user-data/outputs` 與 `/tmp` 改相對 `./output/`;`with_server.py` 補 type hints
- `data-report-builder`:目錄樹補 `state/last_run.md`;統計規範內嵌進 template,不再依賴使用者 CLAUDE.md 有「資料分析」段
- `starter-setup`:補角色標頭;clone 指令填入實際 URL;skill 數量改以目錄為準
- `card-game`:刪 12 個不存在的 Godot / Unity skill 引用,實作路徑改指向 game-prototype 的單檔 HTML;description 補中文觸發詞
- `product-planning`:修鐵則語句;加「有部門專屬企劃 skill 時優先走它」
- `playtest-loop`:新增 `references/dev-notes-channel.js`(開發者回饋頻道注入碼);工具名統一為 chrome-devtools MCP
- `my-voice.example.md` 從 `agents/` 搬到 `templates/`,name 改 `my-voice-TEMPLATE`,避免直接 clone 的人多出一支佔位 agent

**死引用清除**
- `generate2dsprite-chibi` 殘留 6 處、不存在的 memory 檔 9 處、不存在的 skill(design-consultation / frontend-design / design-review / qa / generate2dgamepack)全部改指向 kit 內對應資產;game-develop 的 QA 階段正式接上 webapp-testing
- 三支 imagen 的 `imagen_history.md` 統一路徑 `<project-dir>/docs/imagen_history.md` 與欄位;參考圖上限統一 6 張;存檔位置統一「先問,fallback `<cwd>/<skill 名>/`」
- 瀏覽器工具名統一為 chrome-devtools MCP(原 browse / claude-in-chrome / javascript_tool)

**一致性**
- 三支 agents 的 description 標明角色(【敘事】【數值 / QA】【企劃複核】),balance 與 planning 兩支加分工邊界句
- generate2dsprite 角色標頭補「完成後切企劃視角複核」;prompt-rules 的像素預設去掉與規則矛盾的 16-bit / chunky 措辭
- 「默認」→「預設」、歷史註記(2026-05-07 等)清除、imagen 三支 frontmatter 移除未用的 allowed-tools
- 安裝說明第 21 行藏有兩個 bell 控制字元(`\a` 跳脫),已修
- `.gitignore` 加 `__pycache__/`

## v1.4.0 (2026-09-14)

- **新 skill `data-report-builder`**(meta skill):一輪訪談(資料來源 / 指標公式 / 比較基準 / 異常門檻 / 分群 / 產出 / 週期)→ 在 `~/.claude/skills/report-<slug>/` 生成專屬的定期報表分析 skill(SKILL.md + 指標字典 + 報告模板 + 選配 load.py)→ 試跑一次 → 給排程建議。生成的 skill 屬使用者自有,不進 kit。附三個模板
- **企劃角色加數據能力**:CLAUDE.starter.md 專案角色表,企劃關注點加「KPI 定義、A/B 假設驗證」,產出加「指標定義表、數據解讀報告」,對應 skill 加 data-report-builder
- kit 回到 15 支 skills
- **規則:新建 skill / agent 必標執行角色**(CLAUDE.starter.md 專案角色段);安裝精靈最終健檢加「缺角色標頭」檢查項

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
