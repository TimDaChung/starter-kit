# CHANGELOG

> **怎麼讀**：本檔是版本歷史，含後來被推翻的決定。**現行規則一律以各 skill 的 `SKILL.md` 為準**；已被後續版本推翻的條目會就地標成 ~~刪除線~~ 並附「已於 vX.Y.Z 推翻」。

## v3.18.4 (2026-10-02)

- **`imagen-banner` 機台廣宣在地化補第 0 步**：開工先問一句「直接用企劃 2.2《wow現有廣宣》那張翻，還是你會另外給我圖？」——使用者可能手上有更新或不同版位的原圖。給圖就以他的圖當 reference，企劃那張只當對照（Tim 定）。`plan-dept14-writer/references/image-slots.md` 對照表同步
- ⚙️ **升級動作**：`git pull` 即生效，無設定變更

## v3.18.3 (2026-10-02)

- **`plan-dept14-writer` 新增「貼圖模式」（第十一節）**：負責把示意圖、美術稿貼進 Notion 企劃對應章節。PM 給目標頁網址 → `scripts/paste_images.py list` 列出章節、右欄 column、卡位、synced_block 原件 → 報清單取得同意 → `insert`／`replace`（`split` 把整張分鏡切成一格一張）→ 回讀。寫入要該線讀寫 token（`--line`，Tim 持有）
- **新增 `references/image-slots.md`**：2026-10-02 實讀一部 24 頁、四部 39 頁＋兩份編寫手冊整理的放圖規則——兩部都是左文右圖；圖名一部寫在圖上方《n.圖名》（caption 空）、四部寫在 caption《圖名》；各範本卡位（「窩是示意圖」佔位圖、「圖片放置區」、《圖片待補》、【待補】）怎麼處理；魚樂園要貼進物件頁的 synced_block 原件；**每支生圖 skill 的產出對到哪個 DB、哪一節**；不准動的圖與企劃裡還沒有圖位的產出
- 第五節第 4 條修正：原本寫「不做序號命名、未提供寫圖後補」，與手冊和範本實況不符 → 改成照部別的圖名寫法、卡位用語跟隨範本
- **14 支生圖 skill 結尾補「貼回企劃」段**（boss-design／props／scene／demo、cannon-wing／parts／storyboard、pet-evolution／parts、weapon-design／parts、imagen、imagen-banner、avatar-proposal），寫明自己的產出落點並指向貼圖模式。Tim 同日定案的四條一起落地：
  - **分鏡整張一張圖**：boss-demo、cannon-storyboard 的分鏡文字寫在同一個小標題左欄、整張圖貼右欄，不切圖（舊頁一分鏡一圖是過去寫法）
  - **weapon-design 讀取來源更正**：外觀企劃以**道具之書武具頁**（道具大類 33；雙龍劍 279e…、神機弩 2d1e…、伏煞盾 374e…）為準，登場動畫與效果池仍在功能之書〈武具系統〉§2.9／§3.5，兩頁都抓；`參考素材索引.md` 同步更正
  - **ICON 企劃沒圖位就不出圖**：cannon-wing 套裝 ICON（Step 9.5）、pet-parts／weapon-parts 道具 ICON 改成「企劃有 ICON 圖位才做」，目前三類頁面都沒有，預設跳過
  - **imagen-banner 新增「機台廣宣在地化」**：娛樂城網頁之書機台廣宣 `2.2 畫面呈現` 右欄《wow現有廣宣》是英文原圖（輸入、不准動），《內文排版示意》是成品——以原圖為 reference 只換字（中文標題字、角標、標語、按鈕、注意文字照企劃文案，一字不改），多版本各一張，`replace` 換回《內文排版示意》
- Notion REST 共用模組移到 `plan-dept14-writer/scripts/notion_rest.py`（加上部門指紋判斷、網址取 id、各線讀寫 token），`avatar-proposal/scripts/notion_api.py` 改為轉接
- ⚙️ **升級動作**：`git pull` 即生效，無設定變更

## v3.18.2 (2026-10-02)

- **`avatar-proposal` 新增 `fill` 模式，並定為正式流程預設**（Tim 定）：使用者先用 Notion 範本建好頁、把網址貼來，`build_notion.py fill` 把內容插在範本「調整紀錄」標題之前——範本的目錄與「新增調整紀錄」按鈕（API 建不出來）原樣保留，也不用再問 workspace 與父頁。範本已放卡位圖（圖說「示意圖｜<組別>」）就用 `swap` 原地換。**`new` 只在使用者口頭明說「你幫我建」時用**。找不到調整紀錄標題會改附加到頁尾並警告；調整紀錄是頁面第一個 block 時直接停（API 無法插在第一個 block 之前）
- 已用模擬範本頁（目錄＋調整紀錄）實測：24 個 block 落在兩者之間，骨架未動
- ⚙️ **升級動作**：`git pull` 即生效，無設定變更

## v3.18.1 (2026-10-02)

- **`CLAUDE.starter.md` 新增「Slack 代發的 tag 要用原生語法，發完讀回驗證」**（緊接「對外發送先鎖定目標」）：實測 Slack 工具不會把純文字 `@here`／`@組別 tag`／`@名字` 轉成通知，存進去就是幾個字。要通知必須寫 `<!here>`、`<!channel>`、`<@使用者ID>`、`<!subteam^群組ID>`；群組 ID 從同事手打過 tag 的訊息讀回取得。發完讀回那則訊息，看到純 `@here` 就是失敗。前科：v3.15.0 在捕魚組群的 `@pm.4_2` 公告、v3.17.0 在一四部大群的 `@here` 公告都是純文字，兩次都沒人收到通知，發送端卻回報成功
- ⚙️ **升級動作**：

1. `~/.claude/CLAUDE.md` 若尚無含 `<!here>` 字樣的規則 → 自動併入 kit 新版「Slack 代發的 tag 要用原生語法」該條，放在「對外發送先鎖定目標」那條之後（冪等：已含 `<!here>` 即跳過；使用者自寫過類似規則但措辭不同時，列對照提醒不動手）
2. 自建的分身 agent（`~/.claude/agents/my-voice.md` 等）若會直接用 Slack 工具送訊，提醒使用者把同一條規則抄進該 agent 的送訊段——agent 不一定會讀到 CLAUDE.md 的這條

## v3.18.0 (2026-10-02)

- **新增 `avatar-proposal`**：神幣「神娃＋人物」每月大活動的人物設定提案（SOP 步驟一）。流程：`scripts/fetch_themes.py` 讀 Notion「大活動歷屆主題」庫查重（主要類別＋要素近 12 個月組合，不比字串）→ 出 3 個主題提案（每案六組×男女小主題、主色、前景背景）→ 拍板 → 寫 `proposal.json` → `scripts/gen_sheets.py` 用 image-studio 算示意圖（**每組男女一張、前景畫在人物框四角、背景畫在另一側滿版；一次一個 job、每組一張**）→ `scripts/build_notion.py` 建 Notion 分欄頁（左文右圖；部件勾選表依 SOP 規則自動產，✅／—／橘字覆寫）或在範本頁原地換掉卡位圖（`swap`，認圖說「示意圖｜<組別>」）
  - 版面與畫風錨＝九月成品五張（美術網芳 Avatar魔鬼營 202609 靜態平面），腳本自動抓、不進 kit；固定用這五張不每月換
  - 規則來源：SOP 步驟一部件需求表（五級標記）、Avatar Q&A 禁忌（書／鐘／蛇／宗教／殘破／綠帽／女性重甲與裸露），完成品踩線處預設擋並提替代
  - Notion 側實測：File Upload API 可直接上傳圖片；**原地換圖 `PATCH /blocks/{id}` body 不帶 `image.type`**；分欄裡放表格是三層巢狀，建頁只能帶兩層，所以建頁只帶第一個 block、其餘 append
  - 建頁與換圖要一部 readwrite token（Tim 持有），`notion_api.find_token("readwrite")` 拿不到會停下提示找 Tim；讀取走 readonly 自動到網芳拿
  - `scripts/ppt2notion.py`：舊的 20 頁人物設定 pptx 整份轉 Notion（文字、勾選表、60 張圖），遷移歷史企劃用
  - 首跑：2612 候選案「百鬼夜宴」五組示意圖一次過（儲值組測試略過），Tim 定稿分欄版格式
- ⚙️ **升級動作**：`git pull` 後建立 `~/.claude/skills/avatar-proposal` junction 指向 kit 的 `skills/avatar-proposal`（照既有 skill 裝法）；無設定變更

## v3.17.0 (2026-10-02)

- **`issue-triage` 新增 C 建議模式**：kit 原本只有「異常走 SOP」一條回報線，要求最小重現與根因行號，組員若只是覺得某支 skill 不順手（流程多一步、觸發詞叫不到、輸出格式不合用、想加功能）沒有管道，又被禁止改 junction 內的檔，意見會悶在自己機器上。現在「這支 skill 想改」「對 skill 有意見」→ 四欄輕量建議單（哪支哪步／現況 vs 希望／理由／影響範圍，加一欄「我試過的改法」），不用重現步驟，一樣轉給主任
- 收單端補建議單的簡化路徑：跳過重現，直接判採納／部分採納／不採納，**不採納也要回覆理由**；採納的 CHANGELOG 註明「組員建議」
- `CLAUDE.starter.md` 的「異常走 SOP」改為「異常與建議都走 SOP」，`README.md`／`功能說明.md` 同步
- 順手修 `imagen` SKILL.md Phase 5 殘留的「預設一次 1 張」（v3.15.0 統一為 2 張時漏改；dry run 建議模式時測試員對照文件抓到）
- ⚙️ **升級動作**：`git pull` 即生效，無設定變更

## v3.16.2 (2026-10-01)

- **`notion-access.md` 補「選哪支 token」的順序**（Tim 定）：① 先看連結——新版頁面 id 內嵌 workspace 指紋，含 `87244fa40` ＝一部、含 `e22985ac9` ＝四部（觀察規律，舊頁隨機 UUID 看不出）；② 再看前後文產品線；③ 判不出或不想花時間就一部→四部輪流打，**兩支都 404 才算「頁面沒連接 integration」，到此停**。原本只有「判產品線」與「真的判不出才兩支都試」，缺指紋這一步，也沒寫 404 的停損
- MCP 禁令改成「讀和寫都走部門金鑰＋REST」，明列 claude.ai 內建的 Notion MCP 也不用；補一句不要退而用瀏覽器抓文字（表格裡 ✅⚠️❌ 標記會被吃掉）。前科：2026-10-01 讀神娃 SOP 先打 claude.ai Notion MCP 404、再繞瀏覽器讀到殘缺表格，被 Tim 點出才回 REST
- 404 排障列補「先確認兩支都試過」與「請頁面擁有者 ⋯ → 連接」的具體動作
- ⚙️ **升級動作**：`git pull` 即生效，無設定變更

## v3.16.1 (2026-10-01)

- **`starter-setup` 升級節：skill map 更新改為明列的收尾必跑項**。原本埋在「重跑第 1 到 6 節」裡（第 3 節第 6 步），升級時容易裝完 skill 就收工、map 沒跟上，組員之後查工具地圖就找不到新 skill（例：`data-report-builder` 已在 kit 卻不一定在個人 map 上）。現在第 4 步明寫：把 `~/.claude/starter-skill-map.md` 對到裝完實況、日期改今天、結算表列出 map 增刪了哪幾行
- ⚙️ **升級動作**：`git pull` 即生效，無設定變更；本次升級精靈照新規定會順手更新你的 skill map

## v3.16.0 (2026-09-30)

- **3D 生圖畫風改「魚樂園低模手繪風」**（weapon-design 首次實測定案，pet-evolution／pet-parts 同步）：舊寫法「成品渲染、立體、體積感強、材質分明」出來是寫實 3A／精緻 CG 質感；改寫「低面數、塊面大而簡潔、輪廓誇張、手繪風貼圖、自發光（武具）／毛髮畫成色塊（寵物）」後回到線上道具的質感，且裝飾沒被砍。寵物線的「已知未解：四輪都是精緻 CG」由此解掉，但寵物本身尚未用新寫法實測
- **新增武具線兩支**（魚樂園陣營戰武具，結構比照 pet-evolution → pet-parts）：
  - **`weapon-design`**：讀功能之書〈武具系統〉§2.7／§2.9 的既有武具、或從零發想並先提案＋產 mini 道具企劃拍板 → 算一張 3D 成品感示意圖（3/4 視角、無角色、無 UI、無文字）→ `boss-design/scripts/fit_canvas.py --height 0.6 --max-width 0.7` 補成 16:9 灰底 → 驗收。**招牌部位要能成為登場動畫的動作來源**（企劃四把的動畫都圍繞一個部位：扇面旋轉、麒麟眼電光、盾面展開、雙劍交叉）。`參考素材索引.md` 記既有 4 把（只有玄暝雙龍劍有 wid 3300001，其餘三把企劃標「暫放」）與已知企劃問題（3 把無 wid 與屬性、2D／3D 未寫明）
  - **`weapon-parts`**（下游，全部以定稿為參考圖）：外觀 → 登場動畫分鏡（4 格）＋3 星金閃版；追擊提示格選做。分鏡一張 2×2，**格序固定：中間出現 → 招牌動作 A → 招牌動作 B → 統一發光**（企劃 §2.9 PM 註記），`pet-parts/scripts/label_frames.py --cols 2 --rows 2` 加標籤；金閃版閃點路徑依招牌部位，參考圖直接用外觀定稿、可與分鏡並行送（首跑實證）；追擊提示格的「追擊效果觸發」字樣後製不交給 AI
  - **道具 ICON 一律後製**（新腳本 `pet-parts/scripts/item_icon.py`，三條線共用：從外觀定稿裁主體、去灰底、疊深色圓角底板，程式出 512 主圖＋256／128／64 預覽；碎片版＝同圖左上疊碎片角標）。**不再用 image-studio 生道具 ICON**（Tim 定案）；**技能 ICON 不在此限**——那是技能圖示，pet-parts 照原生圖流程。三線取圖：武具單張 16:9 灰底定稿直接吃；炮台翅膀 `--grid 3x3 --cell 3,1 --grid-bottom 0.06` 取總覽圖左下格（lv0 組合）；寵物 `--half left`／`--half right` 一階二階各一。**碎片角標素材不進 repo**（線上 UI 素材裁切、kit 是公開 repo）：放網芳 `X:\grp.product.pm1\2. 產品改造\一四部企劃範本\kit-assets\fragment_badge.png`（X 讀不到換 Y:），腳本沒給 `--badge` 就自動去讀，讀不到只出主圖並提示；`--no-badge` 可關。首版曾用生圖出武具 ICON 與碎片 ICON（`scripts/fragment_badge.py`＋`assets/` 角標），同日收斂時已移除
  - **與寵物線的差別**：武具升星不改外觀，**沒有兩階**、一張定稿、不埋伏筆；分鏡不是照企劃動態拆 3–4 格，而是固定 4 步
  - 玄暝雙龍劍首跑已實測：分鏡與金閃版一次全過，前科表已回寫
- `starter-setup` 依賴表補 weapon 線：共用 `pet-evolution/scripts/fetch_plan.py`、`boss-design/scripts/fit_canvas.py`、`pet-parts/scripts/label_frames.py`；三條生圖線共用 `pet-parts/scripts/item_icon.py`（道具 ICON 後製，只吃 Pillow）
- ⚙️ **升級動作**：`git pull` 後建立 `~/.claude/skills/weapon-design`、`~/.claude/skills/weapon-parts` 兩條 junction 指向 kit 的 `skills/weapon-design`、`skills/weapon-parts`（新 skill，照既有 skill 的裝法）；無設定變更

## v3.15.0 (2026-09-30)

第二輪 prompt 審查（對照 Opus 5.5），修「兩份檔案對同一件事說法不同」與過度規定：

- **生圖預設張數統一為 2**：`draw-engines.md`（09-18 寫預設 1、不多抽）與 `image-studio-共用須知` §三（09-29 寫每輪至少 2 張、平台偶發失敗挑較好的一張）打架，`common.md` §9、`imagen-banner` 也各說各的。以較新的共用須知為準：預設 2、驗收挑一張；使用者指定張數照指定，不自行加抽。`generate2dsprite`／`generate2dmap` 的範例指令仍是 `--count 1`（sprite sheet 與地圖一張通常夠）
- **imagen／imagen-portrait／imagen-ui 改「缺什麼問什麼」**：原本「每次都問」＋兩輪問答→建議→確認框→生成後再問，spec 給全了照樣問四輪。現在使用者講明的不再問、缺的一次問完；說「直接生」就跳過建議與確認框，改附在結果一起回報（`imagen-banner` 09-23 已是這個寫法，三支補齊）
- **憑證到期指引統一**：`starter-setup` 原本「剩 ≤14 天先去要新的」，但新一季憑證要等舊的失效才發、提前要不到；改成「到期當天再找主任拿、那天別排生圖」。`共用須知`、`boss-design`／`boss-scene`／`cannon-wing`／`pet-evolution` 原本指向 `image-studio/references/refresh-credentials.md`——那是維護者本機自建檔、kit 與官方 image-studio 都沒有，在組員機器上是死連結；一律改為「401 → 找主任拿」
- **`playtest-loop` 死分支**：頻道偵測與 curate 流程引用 `exportLearned`／`learned_script`，但 kit 標準頻道 `dev-notes-channel.js` 沒有這兩個；改為只認 `exportDevNotes`，`learned_script` 只在專案自己另建時才走
- **`plan-doc-qa` 讀企劃要下載圖來看**：原本只讀「圖片替代文字」，但文案與版面常整段放在圖裡（`notion-access.md` §1 已寫）
- `starter-setup` 環境依賴說明「企劃／原型類 6 支」數字已失真，改為類別描述
- **`data-report-builder` 生成的報告改「結論先行」**：前三節固定「結論 → 建議行動 → 為什麼這樣說」，之後才是總覽與明細表；正文只留支撐結論的 2–3 個關鍵數字，不把所有比較過程全部列出。**建議行動不可為空**——沒異常也要寫下一個該確認的數字，或「觀察什麼、N 期後回看」；寫不出行動就是還沒分析完，不交。既有用此 skill 生成的報表 skill 不會自動更新，重跑一次 builder 或手動照 `templates/report.template.md` 改
- ⚙️ **升級動作**：`git pull` 即生效，無設定變更。組員若習慣「畫一張」，現在會拿到兩張供挑；要固定一張就講「畫 1 張」

## v3.14.1 (2026-09-30)

- **全 kit prompt 審查**（對照 Opus 5.5）：修掉引擎換線後的過時說明（imagen-ui「一律 magenta」改成單件 `--remove-background`、生圖 skill 數量、已刪的 prompt-builder）、錯誤指令（imagen-ui 多件切圖 `--rows 1 --cols 1`、cannon-storyboard 不存在的 `--equal`）、同檔矛盾（cannon-parts 雷射批次改回直式單張、cannon-storyboard 5 格殘留與攻擊格數、cannon-wing 驗收「鎏金」vs「不限金色」、pet-evolution 參考圖規則）、失效引用與相對路徑（pet-* 腳本改絕對路徑）
- **移除 cannon-art 的所有引用**：該 skill 已刪除，cannon-wing 改成自己說明流程設計理由
- `starter-setup` 依賴表補上 cannon／boss／pet 系列的上下游關係，生圖 skill 清單更新
- `plan-doc-qa` 讀 Notion 統一走部門金鑰 REST
- ⚙️ **升級動作**：`git pull` 即生效，無設定變更

## v3.14.0 (2026-09-30)

- **新增 `pet-parts`**（寵物配件，`pet-evolution` 的下游）：以兩階定稿為參考延伸
  - **動畫分鏡**：一般／上陣／虛弱**每個動畫一張 3–4 格**，一階二階各一套。**動作照企劃原文逐字拆格、不增不減**，循環動作每個姿勢各一格；企劃只寫靜態狀態時先把拆法給使用者確認。`scripts/label_frames.py` 加「圖N＋這格在做什麼」標籤，並擋下沒分格的失敗圖
  - **技能 ICON**：技能 1、2 同張畫、`scripts/icon_check.py` 切正方形並產 256／128／64px 預覽，64px 看不懂就重抽
  - **專屬背景**：16:9 滿版，中央留給寵物、下方 1/4 留給 UI
  - 神弓手霍克實測：三批第一輪成功
- **定稿後主動接續下游**：`pet-evolution`（新增 Step 8）→ `pet-parts`；`boss-design`（Step 10 改成表格）→ `boss-scene`／`boss-props` → `boss-demo`；`cannon-parts` ↔ `cannon-storyboard` 交付後互相提醒。**下游一律以前面的定稿延伸**，不重新發想
- `boss-demo` 素材優先用 boss-design／scene／props 的定稿，缺的才生圖
- ⚙️ **升級動作**：建立 `~/.claude/skills/pet-parts` junction 指向 kit 的 `skills/pet-parts`

## v3.13.0 (2026-09-30)

- **新增 `boss-props`**（Boss 表演道具與等級系列，`boss-design` 的配套）：捕獲／彩金表演裡玩法用到的道具（幻石、罐子、老虎機、轉盤…）
  - **等級差異用累加法**：每升一級在上一級基礎上多一個看得見的新元素、剪影跟著變複雜；高級飾件取自 Boss 的招牌部位，最高級要有質變（彩虹、通透、光暈）。對應幻狐企劃「顏色以外，外觀也要看得出等級差異」
  - 一個系列畫在同一張 16:9 灰底圖；`scripts/lineup.py` 找出每件、`--equalize` 統一大小（模型會自己把高級畫大）、加上等級名稱
  - 熾影幻狐 5 級幻石首次實測，兩張都成功
- **`boss-design` 外觀之前先談包裝、表演、玩法**：企劃有寫照企劃，沒寫就提 2–3 案附理由跟使用者討論；提案與 mini 企劃新增〈包裝〉〈表演與玩法〉段落，要求**外觀的招牌部位成為表演與玩法的動作來源**（玩法跟外觀無關的提案要重想）。只談到概念層級，數值與秒數交 `boss-demo`、道具交 `boss-props`
- ⚙️ **升級動作**：建立 `~/.claude/skills/boss-props` junction 指向 kit 的 `skills/boss-props`

## v3.12.0 (2026-09-30)

- **新增 `boss-scene`**（Boss 專屬背景，`boss-design` 的配套）：兩種背景
  - **A 漁場邊框**：Boss 事件期間疊在漁場底圖上的四邊主題裝飾。**中央 70% 留給魚群**（提示詞最高優先），灰色中央由 `scripts/frame_alpha.py` 轉透明，並量中央不透明比例（>5% 警告重抽）；有底圖時可 `--preview` 疊上去看效果。對應企劃「半透明疊層、四個底台共用」的做法
  - **B 表演背景**：捕獲／彩金表演、小遊戲的 16:9 滿版場景；中央留舞台、下方 1/5 留給 UI、不畫 Boss 本體（牆上火影這類場景化暗示可以）
  - 首次實測（晶龍晶礦邊框、幻狐古代祭壇）第一輪就成功，中央不透明 0.2–1%
- `boss-design/scripts/fit_canvas.py` 新增 `--cover`（裁切填滿 16:9，給滿版背景用）
- **`boss-demo` 新增步驟 6「定稿後擷取分鏡、寫回企劃」**：表演分鏡**從 demo 截，不另外生圖**（動畫太複雜，AI 靜態示意畫不準）。`scripts/capture_storyboard.py` 分兩步：`capture` 用 Playwright 強制播每種表演、每個分鏡在 35%／75% 處各截一張當候選；`compose` **不限格數**：看過候選總覽後刪掉太接近、看不出差別的，留下每個有變化的瞬間，拼成分鏡圖。**標籤寫「這格在演什麼」、不寫秒數**（秒數留在企劃文字與 demo）；企劃草稿列出每格的描述、秒數與涵蓋的 demo 分段
  - **關鍵格由 demo 自己標**：做表演程式時，在每個值得入鏡的瞬間（出手、命中、爆開、特寫、結算）發出 `demo:beat`＋描述。截圖停在那一刻、標籤直接用描述，企劃草稿依分鏡寫出細拆秒數（例：「分鏡2（第一擊，2秒）0.6秒：閃電擊中右側 2 罐〔圖3〕」）——表演是自己寫的，不必事後猜哪格重要
  - 新 demo 必須提供截圖介面 `window.DEMO_API`（含 `beats: true`）＋`demo:phase`／`demo:beat` 事件，舞台內的 debug 元素加 `class="demo-ui"`；舊 demo 沒有關鍵格時，用 `--shim` 注入轉接並改成「截全部候選 → 人工刪近似格」（附戰神賽特的範例）
  - 以戰神賽特 demo 實測：小獎 14 張候選刪掉 5 張近似的，留 9 格（3×3），秒數加總與 demo 一致；自動去重會誤刪小範圍變化，一定要人看過再挑
  - 表演設計要符合 Spine 限制（引用 `boss-design` 法則第四節）
- ⚙️ **升級動作**：建立 `~/.claude/skills/boss-scene` junction 指向 kit 的 `skills/boss-scene`

## v3.11.0 (2026-09-30)

- **新增 `boss-design`**（捕魚機 Boss 外觀設計圖）：讀魚類之書的 Boss 企劃、或從零發想（必走提案＋拍板）→ 每階段一張 **16:9 灰底**外觀圖。**只做外觀**，表演交給 `boss-demo`
  - **Boss 大小與 16:9 由 `scripts/fit_canvas.py` 保證**：實測模型不照比例畫（同一份提示詞一張 95%、一張 65%），改成偵測主體外框 → 縮放到指定畫面高度佔比（預設 55%，寬度上限 50%）→ 羽化合成到 1920×1080 灰底
  - **Spine 限制對照表**（`boss設計法則.md` 第四節，`boss-demo` 設計表演時引用）：不轉身、不做斜線或弧線的旋轉衝刺、不做流暢跳躍、飾物不繞到身後、會轉的光環是平面正圓；附既有企劃的好寫法當範例
  - **不修改既有企劃**：7 份 Boss 企劃的錯字、矛盾、做不到的動作描述整理在 `參考素材索引.md`，只列給使用者看
  - 不做 Boss 專屬背景（配套 skill 規劃中）、UI、Spine 分件
- **`boss-demo` 收進新手包**：原本只在主任本機。觸發詞改成「捕獲表演 demo」，跟 boss-design 的表演示意圖區隔；外觀還沒定時先導去 boss-design
- `pet-evolution/scripts/fetch_plan.py` 改成兩支共用：`--list pets`／`--list bosses`
- ⚙️ **升級動作**：建立 `~/.claude/skills/boss-design`、`~/.claude/skills/boss-demo` 兩個 junction 指向 kit 的 `skills/` 同名資料夾。**已有本機版 `boss-demo`（非 junction）的人**：先比對內容，沒自改過就刪掉換成 junction，自改過就問

## v3.10.0 (2026-09-30)

- **新增 `pet-evolution`**（魚樂園寵物進化對照圖）：讀道具之書的寵物企劃、或從零發想 → 算一張一階／二階並排的 3D 成品感示意圖。目前只管**史詩級（兩階）**
  - 設計理念對齊寶可夢進化：兩階差異要大到**換體型、換主色**（可達鴨 → 哥達鴨的等級），只留 2–3 個錨點；一階埋伏筆、二階長成；二階至少一處身體結構改變；**二階保留一個呆萌點**（杉森建：太帥的設計反而記不住）
  - **裝飾量照企劃走，不刻意減**——判準是每件都連得回概念。試作時把「瘦身」誤用成減裝飾，二階變很素
  - **一階不給舊參考圖**：參考圖與文字衝突時參考圖會贏，一階會被拉回舊設定
  - 從零發想**必走提案＋拍板**，提案附設計理由
  - 為傳說級預留空間：史詩級二階不做成人形；並記下寶可夢御三家類人化被批評的教訓，傳說級第三階不預設只能變人形
  - `scripts/fetch_plan.py`：撈寵物清單（撞題檢查）、讀企劃全文並即時下載企劃圖
  - 已知未解：3D 成品感仍偏「精緻 CG 渲染」，與遊戲內模型質感有差距
- ⚙️ **升級動作**：建立 `~/.claude/skills/pet-evolution` junction 指向 kit 的 `skills/pet-evolution`（新 skill，照既有 skill 的裝法）

## v3.9.2 (2026-09-30)

- **`cannon-wing`、`cannon-storyboard` 的從零發想提案新增必填「設計理由」**（2–3 句）：為什麼選這個題材、元件之間怎麼呼應、升級或演出靠什麼長出來。原本提案只有名稱、意象、配色、形體，使用者只能看名字挑，無從判斷。**沒有理由的提案不交**
- ⚙️ **升級動作**：`git pull` 即生效，無設定變更

## v3.9.1 (2026-09-30)

- **修復 `CLAUDE.starter.md` 角色表格被切斷**：「走 image-studio 產圖時」說明插在表格「美術」列與「數值／QA」列之間，表格斷成兩段，「數值／QA」「敘事」兩列顯示不出來。說明已移到表格後方
- ⚙️ **升級動作**：檢查角色表格，把 image-studio 說明移到表格後方

## v3.9.0 (2026-09-30)

`cannon-storyboard` 實跑九輪後的收斂。**推翻 v3.8.0 的多項規格**，改動較大，做分鏡前請重讀 `分鏡規格.md`。

- **格數改由稀有度決定**，不再從企劃的分鏡段數推導：

  | 稀有度 | 格數 | 排列 | 整張總比例 | 內容 |
  |---|---|---|---|---|
  | 史詩級 | **4** | 2×2 | 32:18 | 攻擊 2 ＋ 噴錢 ＋ 結算 |
  | 傳說級 | **6** | 2×3 | 48:18 | 攻擊 4 ＋ 噴錢 ＋ 結算 |
  | 演出極簡單 | 3 | 1×3 | 48:9 | 攻擊 1 ＋ 噴錢 ＋ 結算 |

  **只做 3／4／6 三種版型，不做 5 格**——三者都是填滿的矩形；5 格要在右下壓一個空格，是逆著模型「填滿版面」的傾向寫規則。企劃段數對不上就往預設靠攏（多的合併、少的拆格，最好用的一刀是把「攻擊結束的餘波」從噴錢格獨立出來）
- **整張總比例必須明寫進提示詞**（根因）：原本只寫「每格 16:9」。2×2 剛好不寫也會對，所以四格版一直沒出事；換成 2×3 就塌成方格。補上後 2×3 四張全落在 2.667、2×2 兩張全落在 1.777。**那條規格本來就寫在 `分鏡規格.md` 的排版表裡，只是沒被填進提示詞——規格檔寫對，不等於執行時讀得到**
- **結算格改為兩層**：藍色圓角數字框／**套裝翅膀本人＋技能名白字直接壓在翅膀上**。技能名底下**沒有底板、橫幅或色塊**——先前誤把公版描述裡的「黃綠漸層」當成技能名的底板，多做了一層不存在的 UI；那條橫幅還連帶把整組撐寬到炮台的 1.5~1.6 倍，拿掉後自然收到 1.1~1.3 倍
- **噴錢格**：獎勵物是**成團的金幣不是錢袋**；數量照企劃，**每團約炮台的 0.3 倍大**，並要明寫「各自堆成一團」（只給尺寸會被光弧拉成一長串）
- **整張交付，不切格**（v3.8.0 的程式等分切格作廢）
- **提示詞寫法的通則（本輪最大收穫）**：**形容詞式的要求，模型一律打折**。「跟參考圖一模一樣」「保持完整」「與炮台垂直對齊」「不要太大」全部無效；換成**列舉構造＋缺一不可**／**指名邊界座標**／**給倍數**才照做。下筆前先問：這句話能不能被量或被數？
- 其他寫進規格的前科：同一元件的尺寸／位置／內部結構要**分段寫**（混一句必定顧此失彼）；**改提示詞改不動的數字，先回頭檢查是不是自己的結構寫錯**，不要急著歸因成模型限制；**挑圖要整張重驗**，新要求會排擠掉先前已穩定的項目
- 修復 `分鏡規格.md` 被區塊替換切壞的重複與殘留段落（同一份文件一度並存三種互相矛盾的說法）

## v3.8.0 (2026-09-29)

- **新增 `cannon-storyboard`**（翅膀技能表演分鏡）：捕魚機三支炮台 skill 的最後一塊。讀翅膀頁 `2.3 翅膀技能`（或從零發想）→ 以炮台翅膀定稿為參考圖一次算出所有格 → 交付。~~程式等分切格~~（已於 v3.9.0 推翻：整張交付，不切格）
  - **版面**：每格 16:9。**背景用純灰色**，不畫實際漁場——這是示意圖，重點在演出內容。~~四格排 2×2，整張 32:18~~（已於 v3.9.0 推翻：格數由稀有度決定）
  - **炮台翅膀固定在每格左下角**，四格位置一致，用的是套裝版（炮台＋翅膀組合）
  - ~~**四格內容是固定結構**：① 攻擊起手 ② 攻擊展開／命中 ③ 錢袋飛向炮台 ④ 結算~~（已於 v3.9.0 推翻：格數由稀有度決定，且獎勵物是**成團的金幣不是錢袋**）。企劃只決定「用什麼視覺元素」表現
  - ~~**第 4 格的結算框有固定三層**：技能名稱 → 翅膀圖示 → 彩金框~~（已於 v3.9.0 推翻：**只有兩層**，技能名直接壓在翅膀上）。數字固定寫 `999,999,999`；這是唯一允許出現文字的一格
  - **攻擊範圍依稀有度**：史詩＝炮台那側的半個畫面、傳說＝全畫面。這會明顯改變前兩格的構圖
  - **模式 B 從零發想**：企劃沒寫技能時，依炮台翅膀與套裝的設計提案「技能名稱＋攻擊段的演出」，噴錢與結算是固定結構不必發想
- ~~**`slice.py` 新增 `--equal`**：分鏡等分切格~~（已於 v3.9.0 推翻：分鏡整張交付，不切格。`--equal` 本身仍保留可用）
- 三支炮台 skill 的分工定案：`cannon-wing`（3×3 總覽圖）→ `cannon-parts`（配件素材）→ `cannon-storyboard`（技能分鏡），由 `cannon-wing` 的 Step 10 串接

## v3.7.0 (2026-09-29)

- **新增 `cannon-parts`**（捕魚機炮台配件示意圖）：接在 `cannon-wing` 之後，炮台翅膀定稿後才做。三批交付——① 子彈＋一般彈紋＋專屬彈紋 ② 專屬獎圈 ③ 雷射子彈＋雷射彈紋。炮火、炮座、最終貫穿光束、各種 ICON 不做
  - **核心手法：拿炮台翅膀定稿當 `--reference`**，風格用參考圖鎖、提示詞只講「畫什麼」。雷射版還要再餵一張批 1 的成品，讓雷射子彈／彈紋與一般版維持同一家族
  - 附 `scripts/rotate.py`：批 1 改為**直式生成再程式轉 90°**。直接叫模型畫「橫躺朝右的彈紋」會把圓框撐成橢圓；改為事後轉向後不只解決變形，連帶因提示詞變短而讓配色自動正確
  - 規格重點：彈紋方向須與子彈同向、專屬彈紋與一般彈紋**等大**（不是放大強化，要換中間內容）、獎圈**中央必須透空**、雷射光束**只有前端沒有末端**、雷射彈紋要**比一般彈紋簡單**（持續顯示，太複雜會干擾畫面）
- **新增 `references/image-studio-共用須知.md`**：所有走 image-studio 的 skill 共用一份，各 skill 改為指路，不各寫一套。**不寫進官方 `image-studio` skill——重新安裝會覆蓋**
  - 算圖中斷的處置（查 `/api/tabs` 判 `running`／`idle` 有圖／`idle` 無圖，**不要盲目重送**，平台可能還在跑）
  - 憑證到期與換發紀律、平台偶發異常清單、模型固定偏誤（粒子必跑螢光黃綠、圓形物件中心會被填滿、傾向畫完整物件）
  - **提示詞的注意力是零和的**（附三版實測對照表）：加字修 A 就會從 B 扣，不要靠「規則寫越多越保險」
  - **能用程式保證的不要靠模型自律**：風格用參考圖、配色用後製色相位移、方向用後製轉向、版型與層序用程式合成
- **挑圖紀律寫進 SKILL**：`--count` 出來的候選**要全部看完再判斷**。兩張裡有一張正確，就代表提示詞沒問題、錯的那張是隨機變異，不要回頭改提示詞去追它
- ⚙️ **升級動作**：`pip install -r requirements.txt`（`numpy>=1.24`，v3.6.0 起需要）

## v3.6.0 (2026-09-24)

- **新增 `cannon-wing`**（捕魚機「炮台＋翅膀」套裝示意圖）：吃 Notion 道具之書的既有企劃、或從零發想先產一份 mini 企劃拍板，接著算**一張** 2×3 去背素材，再由程式切格、調色、疊合，產出 3×3 總覽圖（上排炮台、中排翅膀、下排組合，各 lv0／lv1／lv2）
  - **核心設計：能用程式保證的就不交給 AI。** AI 只畫 6 格素材，下排組合、版型、灰底、標籤全部程式合成。早期讓 AI 畫下排時翅膀會壓在炮台前面，改程式疊合後層序與素材一致性都不可能出錯
  - 附三支腳本：`slice.py`（依 alpha 投影找格線切格，支援 3×2 與 2×1 等版型）、`compose.py`（疊合下排＋拼版＋鋪底＋標籤）、`recolor.py`（特效色相位移）
  - **`prompt模板.md` 附「為什麼這樣寫」前科區**，記錄四組實測踩到的坑，改提示詞前務必先讀
- **`cannon-art` 停用**，僅保留作比對，不要再用
  - 它讓 AI 直接畫下排組合圖，層序會歪；階段規格漏了「lv2 要繼承 lv1 的特效」，產出的 lv2 會掉特效；視角寫死成「90 度俯視」，但參考庫 6 套實際上都是正面視角
- **實測結論：提示詞的注意力是零和的。** 同一份企劃只改提示詞，加強特效配色的敘述後，特效顏色修對了，但**造型精緻度垮掉、去背也跟著失敗**；把規則壓回精簡版，精緻度與去背都回來，特效顏色又跑掉
  - 所以**不要靠「規則寫越多越保險」**。模型對粒子特效有強烈的螢光黃綠偏好（四組全中），提示詞裡留一句輕量排除即可，真的跑掉就用 `recolor.py` 後製，不要回頭跟模型搶注意力
  - 再更激進的精簡版實測沒有提升（企劃內容就佔掉提示詞一半，規則區再砍也稀釋掉），已在模板標明「不要再往下精簡」
- ⚙️ **升級動作**：`pip install -r requirements.txt`（新增 `numpy>=1.24`，`cannon-wing` 的切格與調色需要）

## v3.5.0 (2026-09-24)

- **`notion-access.md` 新增「回寫地雷」段**：組員拿得到讀寫金鑰了，但原本沒有 API 行為的地雷圖，第一個回寫的人很可能踩到而且**不會報錯**。整理成兩類：
  - **A. 走 block JSON（kit 預設路線）也逃不掉的**：建不出按鈕 / 不能搬 block、巢狀編號顯示樣式（API 不回傳 `list_format`，驗不出來，要請 PM 手動調並主動告知）、整頁重灌會洗掉 PM 手調樣式（小修一律對 block id PATCH）、**禁止用瀏覽器自動化點擊改 Notion**（前科：點擊落到 heading 覆寫整行標題）、`append children` 要用 `after` 錨定
  - **B. 只有走 Markdown / MCP 轉換才會中**：成對底線變斜體（`\_` 擋不住，要包反引號）、粗體包行內程式碼 round-trip 壞掉、巢狀縮排要用 tab、角括號方括號轉義、比對字串撞名、中文手轉 `\uXXXX` 出錯
- **實測釐清一個長期誤解**：「Notion 回寫會吃格式」的元凶是 **Markdown 轉換那條路，不是 API 本身**。2026-09-24 實測 REST + `rich_text` 寫入：`[遊戲名稱]_[平台]_[幣值名稱]` 的底線原樣保留、粗體＋行內程式碼並存沒被拆壞。已驗證安全的清單一併寫進檔案

## v3.4.1 (2026-09-23)

- **8:5 已實測，拿掉「尚未重測」警語**：prompt 寫 `8:5 aspect ratio (800 x 500 px deliverable)`，引擎實際吐出 1586 × 992（比例正好 1.60），等比縮到 800 × 500、**裁切 0 px**
- **`prompt-examples.md` 新增第 4 組：機台廣宣・繁中在地化（照真實企劃、帶參考圖）**——來源《218 小惡魔轉盤︰機台廣宣》，示範企劃要求「照現有廣宣翻譯、排版與字色一致」時怎麼帶兩張參考圖（原版鎖版面配色＋排版示意鎖中文版面）。附出圖結果、驗收數據與**與企劃的落差要回報 PM** 的示範

## v3.4.0 (2026-09-23)

- **`imagen-banner` 交付尺寸改為「企劃優先，預設 800 × 500」**：企劃有寫尺寸就照企劃；沒寫就用部門預設 800 × 500 px（8:5）。Phase 1 版位欄、`[SPEC]` 段、`references/prompt-examples.md` 三組 prompt 全部同步
  - **Phase 4 加後製裁切**：引擎沒有 `--size` flag、不會剛好吐出交付尺寸，生成後一律用 Pillow 等比放大＋置中裁切到規格（腳本附在 SKILL.md）。連帶要求 prompt 把主角與文字放在**中央安全區**不要貼邊，且**驗收以裁切後的成品為準**
  - ~~⚠️ **8:5 尚未實測**：改比例當下生圖引擎配額用罄（HTTP 429，Codex weekly 79%），範例檔已標註「實測跑的是 21:9」。8:5 比 21:9 高得多，第一次用要看主角會不會被裁到、文字三級塞不塞得下、CTA 有沒有被擠出安全區~~ ⚠️ **已於 v3.4.1 實測通過**（引擎吐 1586 × 992，等比縮到 800 × 500 裁切 0 px），此警語失效
- **新增 `plan-dept14-writer/references/notion-access.md`**（`plan-dept14-writer` 與 `plan-doc-qa` 共用）：Notion 金鑰的**位置、取用流程、使用紀律**寫成一份參照檔
  - **唯讀金鑰自己去拿，不要問使用者**：與企劃範本庫同一處（X 槽讀不到換 Y 槽），依產品線判部別取對應的 token txt——神幣＝一部、娛樂城 / 鬥地主 / 魚樂園＝四部
  - **讀寫金鑰不發放**，只有主任持有；只有唯讀時不要嘗試回寫、也不要去翻其他資料夾找。`plan-doc-qa` 的「要我直接幫你改嗎」改成輸出可直接貼上的修正片段交 PM
  - 紀律：token 只走環境變數（如 `NOTION_KEY`），不得進腳本 / 設定檔 / 文件 / commit / Slack；**本檔只記位置，不記金鑰值，也不記申請 token 的操作網址**
  - 讀不到的三種狀況各有處理：網芳連不上（多半沒連內網／VPN）、頁面 404（沒分享給 integration）、只有唯讀被要求回寫
  - `plan-doc-qa` 另補：Notion 讀不到要停下回報請 PM 分享或貼內容，**不得從標題或殘缺片段推測就開始審**

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
  - ~~**文字一律留位不讓 AI 生字**：原規範假設美術用 PS 上字；AI 生圖會拼錯字、錯位數，因此 prompt 只描述留白區，Logo / Selling Line / CTA / 優惠數字全部後製上字（優惠數字錯一位數是事故）~~ ⚠️ **已於 v3.2.1 推翻**——實測長句、`200%`、繁中四字標題全對，現行規則是**預設連字一起生**，留白只用在四種業務情況（見 `imagen-banner/SKILL.md` Phase 3）
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
