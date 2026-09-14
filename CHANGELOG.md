# CHANGELOG

## v1.9.0 (2026-09-15)

乾淨機器審查修復：模擬同事照安裝說明裝完，找出「裝了但一用就壞」的項目全修。

- **starter-setup 搬進 `skills/`**：原本放 repo 根目錄，永遠不會被 junction 進 `~/.claude/skills/`，連 Tim 本機都沒有，「starter 升級 / 健檢」口令裝完後沒有 skill 可觸發。現在和其他 skill 一起裝；README 貼給 Claude 的路徑同步改
- **精靈加依賴表**：imagen-ui→generate2dsprite、五支生圖→imagen、game-prototype→game-develop、game-develop→七支、playtest-loop→兩支 agent。略過 X 前先警告連帶影響；最終健檢加「依賴斷裂」一條
- **with_server.py Windows 修復**：`shell=True` + `terminate()` 只殺 cmd.exe，server 變孤兒繼續占 port，下次測到舊版；stdout/stderr 接 PIPE 不讀，長測試卡死。改 Windows 走 `taskkill /T /F`、POSIX 走 process group；輸出預設 DEVNULL、加 `--log-dir`；啟動前先查 port 被占直接報錯。CLI 介面不變，實測 port 釋放乾淨
- **generate.py stdout 改 UTF-8**：Windows pipe 下 cp950，模型回傳含 emoji 就 UnicodeEncodeError，圖已存但 exit 非 0 讓 Claude 誤判重跑燒 quota
- **data-report-builder 不是零依賴**：生成的報表 skill 要 pandas + plotnine。requirements.txt 加註解、SKILL.md 試跑前檢查、安裝說明「7 支免依賴」改 6 支
- **game-develop 第 188 行**：叫 Claude 呼叫 sub-skill 自己的 generate.py，但那三支沒有這個檔。改成一律呼叫 imagen 的，後製才用各自 scripts/
- **相對路徑改絕對**：product-planning 的 template 引用、webapp-testing 五處 `scripts/with_server.py`、generate2dsprite 的 process 指令，原本從專案 cwd 都解析不到
- playtest-loop「殺同 port 舊行程」補 netstat + taskkill；game-balance-auditor tools 加 Write，暫存腳本寫 temp 或 `.tmp/`；安裝說明 Python / Pillow 影響清單補 game-develop
- 排除：allowed-tools 用 YAML 陣列經官方文件確認合法，不改

## v1.8.0 (2026-09-15)

環境依賴補齊：乾淨機器裝完能立刻跑的原本只有企劃 / 原型類 7 支，其餘要 Python 套件或 MCP 卻沒寫、沒檢查。

- **新增 `requirements.txt`**（Pillow、playwright）；imagen 的 generate.py 只用標準庫，不需 google SDK
- **安裝說明前置表**：Python 3.10+、pip 套件、Playwright Chromium、Node + chrome-devtools MCP、Gemini key 各影響哪些 skill 與安裝指令；常見卡點加 ModuleNotFoundError 與 playtest-loop 找不到分頁兩條
- **安裝精靈加環境健檢**：開場健檢查 Python / Pillow / playwright / Chromium / chrome-devtools MCP；缺的列表**問一次**要不要順手裝，同意才動使用者的 Python 環境與 MCP 設定（kit 檔案以外唯一例外，鐵則補寫）；最終健檢加「環境」節列仍缺的依賴與 fallback；結算表加 🧰 一行
- **playtest-loop 加前置節**：需 chrome-devtools MCP + Chrome 以 `--remote-debugging-port=9222` 啟動，缺就退手貼 `exportDevNotes()` 模式
- 安裝說明加「Chrome 開遠端偵錯」四步（改捷徑目標、完全關閉重開、用 `/json/version` 驗證）；維持 `--browser-url 9222` 寫法不改成讓 MCP 自開瀏覽器，因為 playtest-loop 要讀玩家分頁的 localStorage
- README 測試列標註需 Python + Playwright，升級節前補一句誰需要額外依賴
- **Claude in Chrome 選配**：安裝說明加三步（Web Store 連結、`/chrome` 設預設、確認 Installed）；精靈開場健檢偵測擴充功能目錄、結算表加 🧩 一行給連結，不代裝（Chrome 擴充功能沒有指令安裝途徑）

## v1.7.0 (2026-09-14)

健檢第四批：一致性收尾。

- **card-game 全文翻成繁體中文**（SKILL.md + references/effect-resolution.md）：TCG 術語（deckbuilder、constructed、fizzle、保底）保留圈內慣用說法，code block 與識別字不動；description 保留既有中文觸發詞
- **半形標點統一為全形**：product-planning、data-report-builder（含三個模板）、starter-setup 六個檔，只動中文語境內的標點，code fence / inline code / URL / 路徑 / regex 觸發詞位元組不變；兩個原為 LF 的模板改 CRLF，kit 內文字檔換行全部一致
- **CLAUDE.starter.md**：效率習慣的唯一一條併入核心原則，少一個段落；語言段加「第三方或英文原生的 skill / 腳本文件保留原文，不硬翻」（webapp-testing、generate2dsprite、generate2dmap 因此不再與「文件繁中」衝突）；專案角色的「改不改由使用者決定」刪除，核心原則已涵蓋
- **安裝精靈健檢加「瘦身的邊界」**：只建議動重複、死引用、過時路徑；使用者的角色定位句、原則句、meta 規則不列為瘦身對象，「工具還沒接上」不是刪句子的理由（來自今天實際誤刪一次的教訓）

## v1.6.1 (2026-09-14)

- **略過清單**:使用者說「X 不要裝」→ 記進 `~/.claude/starter-skip.md`,之後安裝與升級都跳過;「裝回 X」→ 移除並立即裝。解決升級時把使用者刻意不要的 skill 裝回來的問題。分類表加「使用者略過」一類,結算表加 ⛔ 一行
- 升級節明寫:先前沒裝的也會補裝(略過清單內除外)

## v1.6.0 (2026-09-14)

健檢第三批:抽共用、砍 legacy、補測試。行為不變,結構收斂。

**共用檔(progressive disclosure)**
- 新增 `imagen/references/common.md`(9 節):三支 imagen skill 的預設視覺規則摘要、專案資產繼承路徑表、批次一致性、Prompt 確認框、參考圖規則、生成後循環、存檔與檔名、`imagen_history.md` schema、`generate.py` 標準指令與模式判定。各 SKILL.md 只留 2 到 4 行摘要 + 「見 common.md §N」
- 新增 `imagen/references/consistency-rules.md`(英文正文 + 繁中摘要):五支生圖 skill 共用的一致性三段 + 交棒 art-style-guard。generate2dsprite / generate2dmap 只留摘要與領域特有條目;art-style-guard 加銜接段列出五支交棒來源
- 行數:imagen 310→162、imagen-portrait 345→254、imagen-ui 366→292、generate2dsprite 273→188、generate2dmap 216→180

**Python 腳本**
- 新增 `imagen/bin/chroma_tools.py`(211 行):去背、裁邊、連通元件、bbox 等 8 個函式的唯一實作,generate2dsprite.py 與 extract_prop_pack.py 改 import(kit 內與 junction 安裝兩種路徑都解析得到)。兩支腳本各自的 CLI 預設值不變
- `generate2dsprite.py` 911→486 行:刪除 SKILL 明說不用的 `build-prompt` 子命令與其常數;`process` 在沒給 `--rows/--cols` 時驗證 `--mode`,亂填會明確報錯而不是靜默走單幀;numpy 改純 PIL,少一個依賴
- `extract_prop_pack.py` 337→209 行,移除兩個 `# type: ignore`
- 新增 pytest:`imagen/bin/tests/test_chroma_tools.py`(13)、`generate2dsprite/scripts/tests/test_process.py`(6,含端到端跑 process 與 extract_prop_pack)。重構前後對同一合成 sheet 輸出位元組相同

**文字去重**
- game-develop:三張生圖對應表合併為 Phase 2 唯一權威表(15 列,新增 image-to-prompt 與 art-style-guard 兩列);紀律 1 縮半;新增「工作量切分與行數監控」共用段,game-prototype 改指向它,兩支的 session 策略以雙列表明寫差異
- generate2dsprite:[chibi] 風格區塊只留 prompt-rules.md 一份;5b 頭身 QC 壓成 2 條 checklist;modes.md 刪 Legacy Compatibility 段
- 三支 agents 啟動流程各壓到 5 行,只留 agent 專屬檢查

**其他**
- `.gitignore` 加 `.pytest_cache/`
- 未動(留第四批):card-game 全文翻譯、半形標點統一、CLAUDE.md 瘦身四點

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
