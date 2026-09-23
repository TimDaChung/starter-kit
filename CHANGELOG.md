# CHANGELOG

## v3.4.0 (2026-09-23)

- **`imagen-banner` 預設比例改 16:9**（部門統一規格）：Phase 1 版位欄與 `[SPEC]` 段都改為預設 `16:9 aspect ratio, 2K resolution`，版位另有規定才覆蓋；`references/prompt-examples.md` 的三組 prompt 同步改成 16:9
  - ⚠️ **16:9 尚未實測**：改比例當下生圖引擎配額用罄（HTTP 429，Codex weekly 79%），範例檔已標註「實測跑的是 21:9」。16:9 版面較高，主角與文字的相對關係會變，第一次用要特別看縱向留白與 CTA 位置
- **`plan-dept14-writer` 八.6 / `plan-doc-qa` 新增 Notion 金鑰紀律**（只寫規矩，不寫金鑰也不寫路徑）：
  - 兩種金鑰：**唯讀**（讀企劃頁與範本庫）、**讀寫**（回寫企劃頁）
  - **讀寫金鑰不發放**，只有主任持有；要回寫 Notion 請交主任處理，不要自己找路子。`plan-doc-qa` 的「要我直接幫你改嗎」在只有唯讀金鑰時改成輸出可貼上的修正片段
  - 唯讀金鑰的**實際路徑與金鑰值一律向主任索取**——本 kit 是公開 repo，兩者都不寫進來（比照 image-studio 安裝包的處理方式）
  - token 一律走環境變數（如 `NOTION_KEY`），不得進腳本 / 設定檔 / 文件 / commit 訊息
  - `plan-doc-qa` 另補：Notion 讀不到（404／無權限）要停下回報請 PM 分享或貼內容，**不得從標題或殘缺片段推測就開始審**

⚙️ **升級動作**：`git pull` 即生效，無設定變更

## v3.3.0 (2026-09-23)

- **`imagen-banner` 可以直接吃企劃了**。新增 Phase 0「有企劃就先吃企劃」：企劃本來就寫好**文案**與**想要的元素**，正是 prompt 最關鍵的兩段，有企劃就先讀完，不要一上來丟問題清單；Phase 1 降級成「補問企劃沒寫的」
  - 三種來源：Notion 連結（用環境裡的 Notion MCP 讀）、本機檔 / 截圖（Read）、直接貼上的文字
  - **讀不到就停**：Notion 常見 404 是該頁沒分享給 integration、或不在 MCP 認證的同一個 workspace。回報實際錯誤請對方分享或貼內容，**絕不從標題猜內容**
  - 附「企劃欄位 → prompt 段落」對照表：主標→Level 1、賣點句→Level 2、按鈕文字→Level 3、優惠數字→Level 2 或王者、**想要的元素清單→HERO / MASCOT / WEALTH / BACKGROUND**、檔期→節慶識別碼、版位→SPEC ＋ UI 疊圖區、參考圖→`--reference`
  - **三條紀律**：文案逐字照抄（有錯字照抄但回報）、**企劃列的元素不得自行刪減**（塞不下要先講並取得同意）、企劃寫了的不要再問一遍
- **移除 `allowed-tools` 宣告**：原本鎖成 Bash / Read / Write / Glob / AskUserQuestion，等於連 Notion MCP 與 WebFetch 都不能用，**企劃在 Notion 就根本讀不到**。改為不宣告（與 `plan-dept14-writer` 等讀企劃的 skill 一致）——各人環境的 MCP server 名稱不同，kit 不寫死

⚙️ **升級動作**：`git pull` 即生效。企劃放 Notion 的話，該頁要先分享給你的 Notion integration，否則 skill 讀不到（會明確報錯，不會亂猜）

## v3.2.1 (2026-09-22)

- **修正 v3.2.0 的「文字一律留位」——改為預設連字一起生**。原規則把字全部留白後製，等於抽掉兩條鐵則：S2 要求 Logo 做成 Graphic Asset（字體造型＋描邊＋厚度＋漸層），F1 更直接把優惠數字當節慶圖的視覺王者。字體、顏色、位置本來就是構圖的一部分，留白出來的圖沒辦法評層級、也看不出 Logo 設計對不對
- `[LAYOUT]` 段改成 `[TYPOGRAPHY]`：要寫明每一級的**實際字樣＋造型方向＋位置**，附完整範例
- **不分級，長句與繁中都照生**（草稿版本曾寫「5 字以上會崩要留白」，實測推翻後移除）：2026-09-22 在 GPT 線跑 6 張實測——45 字元的英文 Selling Line 兩張全對、`200%` 四張全對無錯位數、**繁體中文四字標題 1:1 檢視筆畫正確且無簡體假字**
- **新增 `references/prompt-examples.md`**：三組實測過的完整 prompt 骨架（機台 Hero 當王 / 節慶數字當王 / 繁中節慶），含出圖結果與小瑕疵的修法。繁中的關鍵是 `[TYPOGRAPHY]` 明寫 TRADITIONAL CHINESE + correct stroke shapes，`[EXCLUSION]` 排除 kana / 簡體 / gibberish
- **驗收加「逐字核對」步驟**：放大原圖對每個字元——n=6 不等於 100%，且優惠數字與日期錯一位就是事故。原圖那格的檢查項也加上「Logo 是否被當 Graphic Asset 設計，還是只是打了一行字」
- 留白模式保留為選項，但理由改成**業務面**（文案未定、同底圖套多組數字 / 多語系、大段法遵字樣、美術要自己上字），不再是「AI 寫不好」；`[EXCLUSION]` 不再無條件排除文字
- Phase 1 需求收斂改為必須拿到三級的實際字樣與字體 / 配色方向

⚙️ **升級動作**：`git pull` 即生效，無設定變更

## v3.2.0 (2026-09-22)

- **新增 `imagen-banner`（第 6 支生圖 skill）**：廣宣 / banner 專用，涵蓋機台宣傳、節慶促銷、改版活動三類。內容是 20 條廣宣鐵則（共用 8 條＋機台 2 條＋節慶 2 條與 3 條節慶特化），出自公司內部美術教育訓練，整理成可執行條文放 `references/rules.md`
  - **三模式**：生成（prompt 按鐵則分段）、驗收（給圖跑檢查）、提案（**只限改版活動且對方沒給企劃**；有企劃一律照企劃做，不改王者、不自行簡化）
  - **文字一律留位不讓 AI 生字**：原規範假設美術用 PS 上字；AI 生圖會拼錯字、錯位數，因此 prompt 只描述留白區，Logo / Selling Line / CTA / 優惠數字全部後製上字（優惠數字錯一位數是事故）
  - **`scripts/banner_check.py`**：出四聯圖（原圖 / lobby 縮圖 / 灰階 / 模糊）＋亮度重心、最亮區塊、高飽和占比與主色收斂度。灰階那格專抓「只靠色相撐、明度對比不足的 CTA」。**只吃 Pillow，沒有生圖引擎也能跑**
- **鐵則有明確射程，不得外溢**：只約束廣宣 / banner 圖。立繪、UI 元件、世界觀插畫、藝術風插圖**不受這 20 條約束**，引用時只能當參考、不能當驗收標準打回稿。`consistency-rules.md`、`common.md`、`art-style-guard` 的交棒清單都寫明這條
- **`imagen-ui` 補分界**：它的 `banner` 元件 = 會被文字蓋上的**裝飾底板**；本身就是完整廣告（含主角 / Logo / 利益訊息 / CTA）的宣傳圖走 `imagen-banner`。兩邊互指，避免選錯 skill
- 連帶同步：README、功能說明、安裝說明（生圖 5 支 → 6 支）、starter-setup 的引擎缺件提醒與依賴表、`art-style-guard` 交棒清單（5 → 6 支）、README 的 skill 總數（15 → 20，先前未隨 kit 成長更新）

⚙️ **升級動作**：`git pull` 後跑「starter 升級」即自動 junction 裝上（精靈會掃出 kit 有、本機沒有的 skill）。依賴 Pillow，`requirements.txt` 原本就有、不必補裝。無新 scope、無額度增量

## v3.1.0 (2026-09-18)

組員異常回報收單（5 條，感謝實測與根因定位）。前兩條是結構性的，不修會持續產生損害。

- **skill map 與健檢日期改存固定路徑 `~/.claude/starter-skill-map.md`**（原本寫進「當前 session 的 memory 目錄」）：Claude Code 的 memory 是 **per-project** 的（`~/.claude/projects/<cwd-slug>/memory/`，**沒有全域層**），換個專案開 session 就讀不到前一份 → 第 5 節對帳判定「沒有這張表」再生一份，**自我繁殖**；`CLAUDE.starter.md` 的「超過 30 天主動提議健檢」也因此在多數專案不會觸發。最壞情境是 session 未開專案資料夾啟動，落點是一次性臨時工作目錄，事後被清掉 → 檔案還在但永遠讀不到（實測回報者與維護者本機都中，維護者本機另有 30 個 memory 檔分散在讀不到的 slug）
- **CLAUDE.starter 同步兩條**：「教訓歸 memory」加註 per-project 的射程限制——**跨專案恆真的鐵則寫 CLAUDE.md，只有綁該專案的脈絡才寫 memory**，並提醒固定在同一資料夾開 session；新增「工具地圖」條指路 `starter-skill-map.md`（原本靠 MEMORY.md 自動載入才會被看見，搬家後需明文指路）
- **升級流程補「同步 gitignore 排除區」**：設定資產版控的排除行是裝機當下依現況寫入的，kit 的 gitignore 範本本身不含 skill 名 → v2.4.0 的 `plan-dept1-writer` → `plan-dept14-writer` 更名後，舊名沒機制更新、新名沒被加入，該 skill 被使用者 repo 追蹤。**補排除行救不了已被追蹤的檔案**（gitignore 對已追蹤檔無效），升級時一併對 junction 路徑跑 `git rm --cached`。只處理 kit 來源的 junction，自有 skill 一律不碰
- **備份前先判斷是否已版控**：`~/.claude` 已開 git 時，CLAUDE.md 併入與換版評估不再無條件複製一份到 `skills-backup/`（已版控者靠 commit 留歷史），結算表註明
- **健檢不再要求第三方 skill 補角色標頭**：非 kit 來源、由上游發佈的 skill（如 Anthropic 官方 skill、主任另行發放的 image-studio）改了下次換版會被覆蓋，等於每次健檢都報一條沒人能修的建議；改為結算表中性一行帶過。使用者自寫的 skill 缺標頭仍會列
- **image-studio 憑證到期預警**（回報者在附註提出但自評不列入，維護端判斷該做）：v3.0.0 移除 fallback 後憑證過期＝五支生圖 skill 硬停，原本只在「已過期」才報，等於使用者一定是在要生圖的當下才發現不能用，而換憑證要等主任發、不是自己能立刻解決的。改為**剩 ≤14 天就在結算表提醒**，第 1 節與第 5 節都加（健檢模式只跑這兩節），三個口令的執行路徑都涵蓋
- **gitignore 範本兩項**：新增 `!/starter-skill-map.md` 白名單（工具地圖是使用者級資產，換電腦該還原）；密鑰排除從寫死的 `/skills/imagen/.env` 改為 `**/.env` 與 `**/credentials.json`（任何位置都擋，不必為每支 skill 補一行）
- draw-engines.md §5 封印條款的版號更正為 v3.0.0（撰寫時暫定 v2.6.0，發版改 major bump 後未同步）

### ⚙️ 升級動作

1. **skill map 搬家**（冪等）：若 `~/.claude/starter-skill-map.md` 不存在，而任一 `~/.claude/projects/*/memory/reference_skill_map.md` 存在 → 取**最後修改時間最新**的那份搬過去（原檔保留不刪，避免動到使用者的 memory），並把健檢日期一併寫進新檔頂部；若多份內容分歧，結算表列出來源路徑與日期讓使用者知道採用了哪份
2. **gitignore 同步**（僅當 `~/.claude` 是 git repo）：比對 `.gitignore` 排除區與 `~/.claude/skills/` 實際 junction 清單，缺的補、指向已不存在 kit skill 的移除；接著對每個 junction 路徑檢查 `git -C ~/.claude ls-files 'skills/<名>'`，有輸出就跑 `git rm --cached -r --quiet 'skills/<名>'`（只退出索引，不刪檔）。**自有 skill 不在此列，一律不碰**；做完提醒使用者 commit 一次
3. `~/.claude/CLAUDE.md` 若含舊條「**月度健檢**：MEMORY.md 頂部記…」——**完全同文才改**——替換為指向 `starter-skill-map.md` 的新版；並檢查「教訓歸 memory」條是否已含 per-project 警語、以及有無「工具地圖」條，缺的併入（冪等：已含「per-project」／「工具地圖」字樣即跳過）
4. `~/.claude/.gitignore` 若存在且缺 `!/starter-skill-map.md` → 補上（否則搬過去的工具地圖不會進版控）；密鑰排除若仍是寫死的 `/skills/imagen/.env` → 換成 `**/.env` 與 `**/credentials.json`

## v3.0.0 (2026-09-18)

> **資安事件應對＋breaking change：Gemini 生圖線全面移除，生圖只剩 image-studio（GPT 線）一條。**

起因：有同事的 Gemini API key 被盜。該 API **按件計費、無上限**，key 一旦外流就是開放式帳單，風險不可接受。

- **刪除** `skills/imagen/bin/generate.py`（Gemini/Nano Banana Pro 呼叫端）與 `skills/imagen/.env.example`。kit 內不再有任何需要個人 API key 的生圖途徑
- **`draw-engines.md` 由雙引擎路由改為單引擎**：唯一引擎 = image-studio；**沒有 fallback**——沒裝或憑證過期就是生圖停工、請使用者找主任拿安裝包，不得改走其他生圖途徑。失敗處理表移除所有「換 Gemini」選項（改 prompt／等額度／找主任換憑證／問要不要重跑，全留在 GPT 線）
- **新增封印條款（draw-engines.md §5）**：載明移除原因，明文禁止未來把按件計費無上限的生圖 API 加回來、禁止從 git 歷史還原 `generate.py`；真要加第二引擎必須先有硬性額度上限與主任決策
- 五支生圖 skill＋art-style-guard／game-develop／image-to-prompt 全面改寫：移除 generate.py 呼叫、`--ratio`／`--size`／`--ref` flag（改用 client 契約，長寬比寫進 prompt 文字）、`.env` 與 key 檢查、以及 Nano Banana Pro 專屬的模型特性段（只出 JPEG、IMAGE_RECITATION、畫格線、painterly bias 等，對 GPT 線不成立）
- **common.md 的 API mode／Prompt mode 雙模式判定移除**：那套判定的本質是「有沒有 Gemini key」，已無意義
- **art-style-guard 的 STYLE_BIBLE `engine` 欄**：新專案一律 `gpt`；舊 bible 若寫 `gemini` 視為歷史紀錄，改走 GPT 線重生並更新欄位（跨批一致性靠 prompt 與參考圖比對）
- starter-setup：移除 `.env` 建立步驟與 Gemini key 健檢；image-studio 檢查的措辭從「缺就走 Gemini，功能不受影響」改為「**缺就五支生圖 skill 完全不能用**」。維持只偵測不代裝、kit 內不寫安裝路徑與憑證細節
- 後製能力**完全不受影響**：chroma-key 去背、sheet 切割、shared-scale、GIF 匯出、QC、風格守則、prompt 規則全部保留
- **plan-dept14-writer §八 去 API 化**（同批追加）：原「Notion 技術注意」整節是 API／MCP 回寫的操作細節（`update_content`／`replace_content` 參數、block 型別限制、巢狀編號成因等），組員手上沒有回寫通道、讀了也用不到，已移出 kit。改為 §八「交付與貼上 Notion」：產出一律本地 Markdown 由 PM 自行貼上，保留真正影響產出的三條——**md 不寫「目錄」章與「調整紀錄」章**（用範本頁自帶）、標題行屬性由 PM 手動補、上色與兩欄語法；貼上後自檢巢狀編號／表格／標記。無升級動作

### ⚙️ 升級動作

1. **刪除 `~/.claude/skills/imagen/.env`**（若存在）——裡面是明文 Gemini key，且已無任何 skill 會讀它
2. 刪除後**一定要提醒使用者**（這步不可省略，檔案刪掉不等於 key 失效）：
   「你本機那把 Gemini API key 已從硬碟移除，但**雲端那把還有效**。請立刻到 https://aistudio.google.com/apikey 把它 revoke／刪除；若該 key 綁的是 Google Cloud 專案，順便去帳單設定確認有無異常用量與支出上限。」
3. 若使用者的環境變數（`GEMINI_API_KEY`）或 shell profile 有設過這把 key，一併提醒清除（`setx GEMINI_API_KEY ""` 或到系統環境變數移除）
4. 檢查 image-studio 是否已安裝（`~/.claude/skills/image-studio/` 與 `~/.config/image-studio/credentials.json`）——沒裝就提醒：**現在沒有備用生圖線了**，生圖 5 支在裝好前不能運作,安裝包向主任索取

## v2.5.5 (2026-09-17)

- **CLAUDE.starter Git 基本盤新增「禁推機密」**：含 token / API key / 密碼的內容一律不得 commit 進有遠端的 repo；push 前掃金鑰特徵；已進歷史視同外洩（revoke 換新→清歷史）。全域與 kit 同步收錄
- **plan-dept14-writer 八、新增 Notion 頁面容器規則**：API 建不出按鈕 block、不能移動 block → 新建企劃頁一律由範本「建立複本」產生（目錄與「新增調整紀錄」按鈕用骨架自帶），Claude 只灌中間章節、不自產目錄與調整紀錄章，插入用 append `after` 錨定；本地 md 產出同步不寫目錄/調整紀錄章；調整舊頁直接改對應位置不整頁重灌（skills 為 junction 制，pull 即生效）

### ⚙️ 升級動作

1. `~/.claude/CLAUDE.md` 的 Git 段若尚無「禁推機密」條 → 自動併入 kit 新版該條（冪等：已含「禁推機密」字樣即跳過；使用者自寫過類似規則但措辭不同時，列對照提醒不動手）

## v2.5.4 (2026-09-17)

- **修正 game-balance-auditor 圖表中文字體**（感謝組員異常回報實測）：原指定的 `Noto Serif CJK JP` 是 Linux／容器常見的全字集包，Windows 繁中裝的是分地區版（實測只有 Microsoft JhengHei 與 Noto TC/HK），matplotlib 找不到只出 warning 不中斷 → 圖表中文**靜默**變豆腐。改為從跨平台候選清單 `["Microsoft JhengHei", "Noto Serif TC", "Noto Sans TC", "Noto Serif CJK TC"]` 挑第一個系統有的再設（實測整串直接塞 `font.family` 會對缺的字體刷 findfont warning；matplotlib 只認英文名，不認 `Microsoft JhengHei UI` 與「微軟正黑體」）。已於 Windows 繁中實機渲染驗證中文正常
- **CLAUDE.starter.md 三處補同步歷史 skill 異動**（同一份回報指出）：企劃書路由改部門版優先（`plan-dept14-writer`＋`plan-doc-qa`，`product-planning` 降通用 fallback——v2.1.0 的既定方向，範本漏改）；角色表企劃列補 plan-dept14-writer／plan-doc-qa、數值/QA 列補 issue-triage
- 維護慣例補課：之後**新增／更名／降級 skill 時必同步 CLAUDE.starter.md**（路由句與角色表），列入發版檢查

### ⚙️ 升級動作

1. `~/.claude/agents/game-balance-auditor.md` 若仍含字串 `Noto Serif CJK JP` → 把該 bullet 替換為 kit 新版的字體段（agents 是拷貝制，pull 不會自動生效；只動這一段，檔內其他自改內容不碰）
2. `~/.claude/CLAUDE.md` 若含舊條「企劃書的寫/反寫/審修走 `product-planning` skill（裝了 starter kit 就有）」——**完全同文才改**——替換為新版路由句；角色表企劃列／數值/QA 列同理（完全同文才替換；使用者自改過的只列出對照提醒，不動手）
3. 使用者若曾自行在 CLAUDE.md 寫字體繞法（如語言段的全域覆寫）→ 不自動改，提醒一句「kit 已修正，繞法可移除」即可

- **starter-setup 開場健檢新增 image-studio 檢查**（生圖 GPT 線，主任另行發放）：偵測 skill 目錄與憑證是否存在／過期——只偵測不代裝、kit 不含安裝路徑；缺就結算表提醒「找主任拿，裝好前自動走 Gemini 不影響功能」
- draw-engines 的缺裝／401 提醒措辭統一為「找主任」，安裝與憑證細節一律不寫進 kit

## v2.5.2 (2026-09-17)

- **CLAUDE.starter 核心原則新增「對外發送先鎖定目標」**：使用者明講目標名稱→先搜完全同名,有就直接用;沒有完全符合才列候選、單獨問,不與版本/內容選擇混題。源自實際錯發案例(近似群名多,頻道確認被夾在版本選擇裡帶過)。既有裝機戶跑「starter 升級」會自動併入這條

## v2.5.1 (2026-09-17)

- **升級動作機制**：CHANGELOG 各版本下可掛「⚙️ 升級動作」區塊——「starter 升級」pull 完由精靈自動執行（冪等設計、`~/.claude/starter-kit-version.txt` 記進度；要使用者選擇的問一句才做）。與 secretary-kit 同一套慣例

## v2.5.0 (2026-09-17)

- **生圖雙引擎路由**：新增共用規則 `imagen/references/draw-engines.md`——GPT 線（`image-studio` skill，含個人憑證故**不隨 kit 發佈、由主任另行提供**，預期人人有裝）一律優先；沒裝或憑證過期會提醒一次再走原 Gemini 線（generate.py），既有流程不變
  - 失敗判定：一批 N 張 0 張成功才算整批失敗；≥1 張成功＝部分成功，回報成功張數並**問使用者要不要補**缺的張數（不自行默默補，避免永遠補不滿的迴圈）
  - 整批失敗**不自動 fallback**：先判斷原因並附建議再問——提示詞／版權觸發過濾→建議改 prompt（換線通常沒用）；用量用完→直接問要不要換 Gemini；401→換季度 key；未知原因→問「GPT 重跑還是換 Gemini」。由使用者拍板才換線；換線後整批重生，不混引擎
  - 引擎鎖：art-style-guard 的 STYLE_BIBLE 新增 `engine` 欄，同專案第二批以後鎖首批引擎
  - 去背：GPT 線 `--remove-background` 直出透明 PNG；Gemini 線維持 magenta chroma-key 後製
  - **預設張數 1**：兩線皆同，使用者明講張數（「畫 4 張」）才多算，不自行多生候選版本
- **參考圖衛生規則（consistency-rules.md 新增 §5）**：AI 產出當參考圖會複利放大高頻雜訊（白點／髮絲／碎花越畫越多）——身分走圖、風格走字；圖只用 gen-0 黃金樣本（絕不 N 代餵 N+1 代）、適度縮圖（768–1024px 長邊起手）、prompt 明寫「圖只給身分、風格聽文字」。兩線通用
- 五支生圖 skill（imagen / imagen-portrait / imagen-ui / generate2dmap / generate2dsprite）＋art-style-guard 的 SKILL.md 接上路由引用

## v2.4.1 (2026-09-15)

- **starter-setup 升級流程：失效 junction 改為自動刪除**——kit 已移除或更名的 skill，其 junction 目標消失即無功能，升級時直接刪不再問（結算表查 CHANGELOG 交代去向，例：plan-dept1-writer → 已更名 plan-dept14-writer）。同名實體資料夾（可能含自改內容）維持不自動刪、進最終健檢

## v2.4.0 (2026-09-15)

- **plan-dept1-writer 更名 `plan-dept14-writer`，升級為一＋四部雙部版**：
  - 產品線路由：神幣＝一部；娛樂城／鬥地主／魚樂園＝四部（線資料夾名已標部別）。先查使用者 memory 記的產品線→內容判斷（判得出直接推薦範本）→才問；首次確認寫入 memory，之後不再問
  - 範本庫終版結構：根目錄雙手冊（一部／四部）＋各線「◯◯空白範本／◯◯實例範本」成對子資料夾；空白＝骨架、實例＝結構與寫法權威（不一致以實例為準）
  - 調整標記帶時間＋版號：綠底新內容前綴「YYYY/MM/DD vN.N調整為→」、新增/(時間+版號新增)、刪除/(時間+版號後廢除)——已同步寫進一部手冊；四部另有黃底(QA期間)/紅底(移植差異)/表格三手法
  - 項目符號順序兩部統一 1→a→i（四部手冊已同步；舊文件的 a→i→1 視為歷史寫法）
- **plan-doc-qa 升級雙部審查**：動工前判線（同 writer）；新增「結構排版對範本」（含符號套錯部算必改）與「調整標記格式」（含四部黃底殘留提醒）兩檢查類；範本庫讀不到降級為內部自洽並註明

## v2.3.0 (2026-09-15)

- **plan-dept1-writer 改為範本驅動版（497→184 行，-63%）**：結構與排版規則不再寫死於 SOP，開工前改讀網芳範本庫（X:\grp.product.pm1. 產品改造\一四部企劃範本，X 讀不到換 Y——在家 VPN 磁碟代號不同）——編寫手冊＝排版權威、空白範本＝結構權威、同線實例＝寫法參考。起因：原 SOP 的標題層級／分隔線／骨架／調整標記與部門實際範本六處矛盾，範本為準後 SOP 只留判斷型規則（可算門檻、狀態寫滿、連動檢查、逐畫面確認、mermaid 工法、Notion API 坑）
- 範本庫讀不到或缺對應範本 → 請使用者提供匯出，不硬寫；範本更新即全員生效，skill 不用改版

## v2.2.0 (2026-09-15)

- **新 skill：issue-triage 異常回報與收單 SOP**——A 回報模式(使用者:環境/最小重現/根因行號/影響鏈/建議修法的標準格式,鐵則:不自行修改 junction 內的 kit 檔)、B 收單模式(維護者:逐項驗證/實測重現含邊界/守設計約束修復/分層測試/教訓回寫 quirks/CHANGELOG 歸功/標準回覆)。範本取自 v2.1.1 那份實戰回報的規格
- CLAUDE.starter 持續優化段補「異常走 SOP」一行

## v2.1.1 (2026-09-15)

- **修正 imagen/bin/generate.py 兩個問題**（感謝組員裝機實測回報）：
  - 生圖失敗（如 IMAGE_RECITATION 被扣留）原本 exit 0 且不讀 finishReason → 下游可能靜默拿到磁碟上的舊檔。現在無圖即 exit 1，訊息帶 finishReason 與對應提示（recitation=換更具體的 prompt；safety=調內容）
  - `--output xxx.png` 實際存出 JPEG：實測確認**此模型 API 只支援 image/jpeg 輸出**（generateContent 與 interactions 端點都拒收 image/png），不做轉檔（維持零依賴），改為 mime 與副檔名不符時印警告
- generate2dsprite 的 Banana quirks 補兩條：JPEG 色度失真的去背參數對策（edge-clean-depth／threshold）、生圖失敗重試前先檢查輸出檔時間戳

## v2.1.0 (2026-09-15)

- **收編企劃一部雙 skill**:`plan-dept1-writer`(house style 八章骨架、逐畫面確認、調整標記)+`plan-doc-qa`(一致性審查、複查差異比對)。已含修正:Windows/容器雙環境渲染路徑(實測過)、house-style 優先自我宣告、角色標頭
- product-planning 定位改為通用 fallback(跨部門/無範本/反寫 demo);依賴表補 writer→qa

## v2.0.0 (2026-09-15)

- **自我優化層**：kit 從工具包升級成會自我成長的系統
  - CLAUDE.starter 的 meta 規則加配套三條：違規回寫（重犯 2 次 → 案例寫回規則旁）、教訓歸 memory 規則歸 CLAUDE.md 的分工、月度健檢（超過 30 天主動提議「starter 健檢」）
  - 安裝/升級收尾**自動生成個人 skill map**（memory reference 檔，情境→工具對照，健檢時對帳更新）
  - 選配**設定資產版控**：問一次要不要幫 `~/.claude` 開 git（whitelist gitignore 模板在 `templates/claude-config.gitignore`），改壞可回滾、換電腦可還原
  - 最終健檢加「memory / skill map」節：skill map 對帳、MEMORY.md 健康度、健檢日期標記

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
