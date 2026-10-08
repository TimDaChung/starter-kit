---
name: boss-demo
description: "捕魚機 boss 捕獲表演驗證 demo 產生器。讀 boss 企劃（或無企劃從零設計：先產 mini 企劃拍板再做）→ 產出單檔 HTML：兩種模式——獎級權重型（依權重 roll 獎級播該級表演）／最終倍數拆解型（先抽最終倍數→判定演到第幾關→拆成各段倍數）；分段秒數即時調、強制播、RNG 批次模擬驗證分布。觸發：「boss 表演 demo」「捕獲表演 demo」「獎級表演驗證」「表演權重 demo」「/boss-demo」。Boss 外觀設計走 boss-design，外觀定案後再來這支做表演驗證；demo 定稿後從 demo 截分鏡圖、寫回企劃（「截分鏡」「demo 定稿了」）。"
---

# Boss-Demo

> **執行角色：企劃（數值驗證）**——關注獎級權重分布、表演節奏秒數是否符合企劃預期；demo 是驗證工具不是成品。

捕魚類遊戲的 **boss 捕獲後表演驗證工具**。目的：讓使用者實際體驗「各獎級表演的出現權重」與「分段秒數的節奏手感」是否符合企劃預期。定位是**內部驗證工具**，debug 面板常駐，polish 適中即可。

不是完整捕魚遊戲——**按鈕直接觸發捕獲**，不做射擊 loop。

## 輸入（兩種模式）

**A. 有企劃**：boss 企劃（文件路徑或貼文；可能附 boss 圖）— 獎級數量/名稱/權重/倍率/表演描述**一律以企劃為準**；缺漏欄位用「預設四級模板」補，並**明確回報使用者哪些值是預設補的**。

**B. 無企劃（設計模式）**：使用者只給主題或什麼都沒給 → 走「步驟 0 從零設計」，先產 mini 企劃拍板，再接回一般流程。**Boss 的外觀還沒定時，先導去 `boss-design` 定外觀**，這支只補數值與表演結構。

## 兩種 demo 模式（步驟 1 判斷）

| 模式 | 企劃怎麼抽獎 | 表演怎麼演 | 例 |
|---|---|---|---|
| **獎級權重型**（`mode: 'tiers'`） | 抽**獎級**（小／中／大／特） | 播該級的固定表演，倍數由該級決定 | 戰神賽特 |
| **最終倍數拆解型**（`mode: 'split'`） | server 先抽**最終倍數** | client 依倍數區間判定結局（演到第幾關）→ 把最終倍數拆成每一段的倍數，逐段演出 | 多關卡、一路累加到結算的表演 |

兩種模式共用舞台、面板、變更管理、分鏡擷取；差在 CONFIG、抽獎、強制播與模擬報告（各步驟分開寫）。

## Workflow

### 0. 從零設計（僅無企劃模式）

1. **問 2–3 個定位問題**（AskUserQuestion）：boss 主題/世界觀、最大賠率與 EV 目標（或指定參考某隻既有 boss 的數值骨架，如戰神賽特 max 1200 / EV ~415）、表演媒介偏好（打罐子/開寶箱/轉盤等）。其餘自行補專業判斷，不逐項追問
2. **產 mini 企劃 md**（存進 demo 專案資料夾，章節照噬魂劍魔企劃骨架，見 `plan-dept14-writer/references/notion-templates.md` Boss 列；分鏡圖仍整張一張）：
   - 基本資訊（名稱、最大賠率、計算用賠率）
   - Boss 造型概念（配色、輪廓、持有物、姿勢——之後直接當生圖 prompt 素材）
   - 玩法大綱與表演流程（捕獲→轉場→彩金表演→結算）
   - 小/中/大獎表演分鏡（每分鏡含秒數，總長標題與分鏡加總**必須一致**）；被捕獲、待機等動態一併寫。**寫法照 `動態描述規範.md`**（每步「主體＋動作＋特效＋位置，N秒」、階段差異、表演期間碰撞／倒數）
   - 賠率權重表（定 EV → 拆 tier 分布 → 配權重 → **驗證每檔賠率可依演出規則分解**）＋翻盤機制
   - 數值拿不準時派 `game-balance-auditor` 模擬驗 EV/變異數
3. **使用者拍板 mini 企劃後**才進入步驟 1——機制取捨是使用者的決定權，不跳過
4. 之後流程與有企劃模式完全相同（mini 企劃就是企劃）；demo 調完參數用「變更區段 Markdown 匯出」回寫 mini 企劃，形成設計→體驗→修數值→回寫的閉環

### 1. 讀企劃、抽表演結構

**先判斷模式**：企劃的權重表是「獎級 → 權重」就是獎級權重型；是「最終倍數 → 權重」，再加上「倍數落在哪個區間演到第幾關」或「每關倍數範圍」就是最終倍數拆解型。兩種都像（例：獎級表又寫每關累加）→ 問使用者 server 實際抽的是什麼，**以 server 抽的東西為準**。

**最終倍數拆解型**抽三張表：

- **最終倍數權重表**：每個最終倍數與權重
- **結局判定表**：倍數區間 → 演到第幾關（例：10–59 演到第一關、60–199 演到第二關）
- **各段倍數的允許區間**：每一關（段）可以拿的倍數範圍與跳階（例：第二擊 10–80、每 5 一階）；各段的 phases 照下面的分段規則拆

**獎級權重型**從企劃抽出每個獎級的：`name`（繁中）、`weight`、`multiplier`、表演描述。每級表演拆成 **phases 分段**（各段獨立秒數），標準分段：

- 一般級：`登場(anticipation)` → `爆分(payout)` → `結算(settle)`
- 最高級：`暗場` → `聚光登場` → `連環爆分` → `結算`

企劃有寫具體演出（如轉盤、倍率跳數、boss 特寫）就照企劃拆段，不硬套模板。

### 1.5 企劃一致性預檢（必做，動工前回報）

抽完結構先核對，矛盾列成清單回報使用者：

- 各表演**標題總秒數 vs 分鏡秒數加總**（戰神賽特首發即抓到 11.5s vs 12.5s）
- 機率加總是否 = 100%（賠率權重表、演出機率、翻盤機率）
- 每檔賠率是否能依演出規則分解出合法組合（如罐子 2+2+4、第三擊 ≥ 前兩擊）
- 分鏡編號/名稱筆誤

**最終倍數拆解型多查：**

- 結局判定表的區間**有沒有斷層或重疊**：所有最終倍數都要剛好落進一個結局（例：59 跟 60 之間沒有洞、60 不能同時屬於兩關）
- 權重表的每個最終倍數，**用該結局會演的各段區間組不組得出**：各段最小值加總 ≤ 最終倍數 ≤ 各段最大值加總，且跳階對得上。組不出的列名單
- 期望值：Σ 最終倍數 × 機率，對照企劃寫的 EV／計算用賠率

矛盾**不擋工**：demo 照分鏡逐段值忠實還原，**舞台下方狀態列**註記矛盾點，讓使用者拿去跟企劃 PM 對。

### 2. Boss 素材（生圖去背）

- 走 `generate2dsprite` 管線：image-studio client 生圖（solid `#FF00FF` 背景，引擎規則見 `imagen/references/draw-engines.md`）→ `generate2dsprite.py process` 去背
- 企劃附 boss 圖 → 先 Read 看圖，再以 `--reference` 傳入，preserve identity
- **有 `boss-design`／`boss-scene`／`boss-props` 的定稿就直接用**，不重新生圖：Boss 定稿去背當本體（灰底定稿用 `boss-design/scripts/fit_canvas.py --transparent` 轉透明，不必為了去背重算 magenta 底）、表演背景當場景、道具等級圖切件當表演元件。缺的才生圖或用佔位
- **預設只生 1 張 boss 本體大圖**（idle 姿態、3/4 或 side view）——表演動態用 CSS transform（浮動/震動/翻肚/拉近特寫）做，夠驗證節奏。使用者看完想要真動畫幀再升級 sprite sheet，不預先做
- 遵守 `generate2dsprite` 的 Default visual rules 與 project asset inheritance
- **處理參數**：boss 大圖去背用 `--cell-size 1200 --fit-scale 0.97`（processor 預設 cell 128 會把 2K 圖縮成縮圖）
- **已知坑**：半透明發光物（光環、光暈、電光邊緣）chroma-key 後會被 magenta 染成粉紅。prompt 階段就要求光效「compact、緊貼身體、實心不暈開」；仍染色時屬內部驗證可接受瑕疵，對外展示前才重生修正
- **企劃示意圖當背景前先目視確認**：示意圖常混入 UI mockup、佔位角色（戰神賽特案例：漁場示意含整套假 UI、彩金示意中央有火箭狗）。乾淨的直接壓 jpg 用；不乾淨的以示意為 --ref 重生「無角色無 UI 全幅背景」
- **小件同風格素材合併成素材表一次產再裁切**（獎圖、道具、特效件、頭像這類單件不需滿版解析度的）：規則、提示詞寫法與裁切腳本照 kit `references/image-studio-共用須知.md` 第零節（`references/scripts/sheet_cut.py`），**切完看 `_check_dark.png`**。組員實測：15 件從 30 張降到 7 張。背景、布幕這類要滿版解析度的仍各自一張
- **同色系多等級元件（如罐子五色）**：只生一套中間色基底（如藍），等級用 CSS `sepia(1) saturate(N) hue-rotate(θ)` 染色——一次生成、五色共用，改倍率結構也不用重生素材

### 3. 特效小元件

**預設 emoji + Canvas 粒子**（金幣 🪙💰、閃光 ✨、爆炸 💥、星星 ⭐），配合縮放/重力/淡出的粒子運動。理由：迭代秒數手感時 emoji 已足夠，且改參數快。

**升級原則**：初版一律 emoji 先行；**使用者指名升級某段表演或某個元件時，用算圖去背局部升級該部分**，不整批重做、不主動升級沒被點名的元件。

### 4. 產出單檔 HTML demo

**硬性規格：**

- 橫式舞台（16:9，設計基準 1280×720，responsive 縮放），單檔 HTML，boss 圖 base64 內嵌
- **舞台以視窗高度為上限**：`width: min(100%, calc((100vh - padding) * 16 / 9))`——視窗再寬、頁面再放大，舞台＋下方狀態列＋捕獲／播放控制都必須一屏內可見，不得出現垂直捲動
- **舞台裡只放玩家看得到的正式畫面元素**：分鏡名稱、倒數、矛盾警示、組不出警示等測試資訊一律放**舞台下方的狀態列**，捕獲與播放控制按鈕也在舞台外。審核者會把舞台畫面當成要做的 UI，混進測試資訊就會被當成需求
- **震動(shake)等 transform 動畫必須與縮放共存**：舞台縮放存 CSS 變數（`transform: scale(var(--s))`），keyframes 每一格都要寫 `scale(var(--s)) translate(...)`——CSS 動畫會整個覆蓋 transform，漏掉 scale 會讓舞台在震動瞬間跳回原始尺寸
- **base64 只嵌一份**：圖寫進 JS const（`IMG_IDLE`/`IMG_CAUGHT`），所有 `<img>` runtime 指派 src——同圖直嵌多個 `<img>` 會讓檔案倍增
- **維護 `index.template.html`**（含 `%%IDLE%%`/`%%CAUGHT%%` 等 placeholder）：改 code 一律改 template，不直接編輯成品檔。素材 ≤2 個時可用單行 PowerShell replace；**升級算圖後素材一多（戰神賽特 v4 有 13 個 placeholder）就建 `build.ps1`**——placeholder→檔案路徑映射表＋未替換殘留檢查，一行重建
- **全幅背景（漁場/表演場景/轉場牆）不走去背**：壓成 jpg（1600 寬、quality ~82）直接內嵌，體積只有 png 去背的零頭
- 所有可調參數集中在一個 `CONFIG` 物件（檔案頂部）：
  ```js
  // tiers mode
  const CONFIG = { mode: 'tiers', tiers: [ { id, name, weight, multiplier,
    phases: [ { name, duration_ms } ] } ] };
  // split mode
  const CONFIG = { mode: 'split',
    finals:  [ { mult: 30, weight: 40 }, { mult: 120, weight: 8 } ],      // final multiplier weight table
    endings: [ { id: 'e1', name: '第一關結束', min: 10, max: 59,  stages: ['s1'] },
               { id: 'e2', name: '第二關結束', min: 60, max: 199, stages: ['s1', 's2'] } ], // range -> how far it plays
    stages:  { s1: { name: '第一擊', min: 2,  max: 20, step: 1, phases: [ { name, duration_ms } ] },
               s2: { name: '第二擊', min: 10, max: 80, step: 5, phases: [ /* ... */ ] } } }; // allowed range per stage
  ```
- **捕獲按鈕**：獎級權重型 → weighted roll 獎級 → 播該級表演；最終倍數拆解型 → weighted roll 最終倍數 → 查結局判定表 → 拆成各段倍數 → 依序演。表演中鎖按鈕
- **最終倍數拆解（拆解型）**：各段**由大到小**分配（允許上限大的段先拿），每段在「自己的區間 ∩ 剩下的段還補得起的範圍」內**有限隨機**，最小的段吸收剩餘；重試幾次仍組不出時，各段取最小值、**末項吸收差值**，倍數加總仍精準等於最終倍數，並在狀態列警示「組不出：末項超出區間」、計入模擬報告。最小範例：
  ```js
  // stages: this ending's stages in play order, each { min, max, step }
  function splitMultiplier(total, stages, rng = Math.random, tries = 30) {
    const order = stages.map((s, i) => i).sort((a, b) => stages[b].max - stages[a].max);
    for (let t = 0; t < tries; t++) {
      const parts = new Array(stages.length);
      let left = total, ok = true;
      for (let k = 0; k < order.length - 1; k++) {
        const s = stages[order[k]], rest = order.slice(k + 1).map(i => stages[i]);
        const restMin = rest.reduce((a, r) => a + r.min, 0);
        const restMax = rest.reduce((a, r) => a + r.max, 0);
        const step = s.step || 1;
        const lo = Math.ceil(Math.max(s.min, left - restMax) / step) * step;
        const hi = Math.floor(Math.min(s.max, left - restMin) / step) * step;
        if (lo > hi) { ok = false; break; }
        parts[order[k]] = lo + step * Math.floor(rng() * ((hi - lo) / step + 1)); // bounded random
        left -= parts[order[k]];
      }
      const last = stages[order[order.length - 1]];
      if (ok && left >= last.min && left <= last.max && left % (last.step || 1) === 0) {
        parts[order[order.length - 1]] = left;
        return { parts, ok: true };
      }
    }
    // cannot be composed: every stage takes its min, the smallest stage absorbs the rest
    const parts = stages.map(s => s.min), absorb = order[order.length - 1];
    parts[absorb] = total - parts.reduce((a, v, i) => (i === absorb ? a : a + v), 0);
    return { parts, ok: false }; // caller warns in the status bar and counts it in the simulation
  }
  ```
  （kit 以 node 跑 1 萬次驗過：加總恆等於最終倍數、組得出時各段都在區間與跳階內）
- **Debug 面板（常駐右側）**：
  - 賠率表可調欄位：**賠率值、權重、獎級**（即時生效）；機率為權重換算的**純顯示值**（帶兩位小數、欄寬要放得下）。賠率改到無法依演出規則組出合法組合（如罐子 2+2+4）→ 標紅警示，表演用最接近組合近似、**倍數欄數字仍精準落在賠率值**（末擊吸收差值）
  - 每級每 phase 的秒數輸入（即時生效）：**以「秒」為單位**，最多兩位小數、尾零不顯示（2、1.5、2.25）；內部一律存 ms，僅顯示層換算
  - 每級「強制播」按鈕（跳過 roll，直接播該級——調表演不用靠運氣）
  - **拆解型另有**：最終倍數權重表、結局判定表、各段區間都可調；每個結局一顆「強制播」；**「指定最終倍數播放」**輸入框＋按鈕——可輸入表外的值，專門測區間邊界（59／60、各段最小值加總、組不出的值）
- **統計區**：實際 roll 分布 vs 理論機率對照表；「模擬 ×1000」按鈕（純 RNG 不播動畫，驗證權重實作沒偏）；歸零按鈕
  - **拆解型的模擬報告多兩項**：**組不出率**（總計＋各最終倍數，> 0 就標紅並列出是哪幾個值）、**各結局表演長度最短／最長**（同一結局各段倍數不同時，跳數、噴金幣量等隨倍數變動的分段秒數也會變，報最短與最長讓企劃看節奏上下限）
- **時長總覽**：各演出類型「表演段／完整流程」總秒數即時重算，附企劃基準對照
- **變更管理**：改過的欄位橘框＋顯示原值；「全部改回企劃預設」；「產出變更區段 Markdown」——依企劃原格式只輸出有改動的區段，每段標示【貼到企劃 X.X.X】方便人手貼回
- **參數保存**（試玩者在自己瀏覽器調參，Claude 讀不到那個分頁；重新整理就全沒）：
  - 每次改欄位就自動存 `localStorage`，開檔時自動載入；**讀寫都包 try/catch**（隱私視窗、file:// 被封鎖時會丟錯，失敗就當沒存，demo 照常跑）
  - key 帶 demo 名與版號（例：`boss-demo:<boss名>:v3`），不同 demo、不同版不互蓋；升版後舊設定不自動套用
  - 「匯出設定」下載 JSON 檔、「匯入設定」可選檔或貼上 JSON 文字；匯入前驗欄位，不認得的欄位略過並提示
  - 「全部改回企劃預設」同時清掉 localStorage。變更區段 Markdown 照樣保留：回寫企劃靠它，設定 JSON 是給人帶著走、傳回給 Claude 重現用
- **播放控制**：暫停（凍結分鏡進度與狀態列倒數）／下一分鏡（跳段）／**結束**（停掉剩餘分鏡，直接跳到結算結果，顯示該次倍數）
- **不做耗時 log**：引擎 sleep 即設定值，實測必然貼設定，記錄無資訊量（首發做過後由使用者裁掉）；秒數判讀靠狀態列倒數＋時長總覽
- UI 文案繁中；code（變數/註解/log）一律英文
- **分鏡擷取介面（必做，步驟 6 要用）**：
  ```js
  window.DEMO_API = {
    beats: true,                 // 宣告這個 demo 會發 demo:beat
    scenarios: [{ id, name }],   // 每種可強制播的表演：小獎／中獎／大獎／翻盤…（拆解型：每個結局）
    play(id),                    // 強制播，回傳 Promise，表演結束時 resolve
    pause(), resume(),
    advance(ms),                 // 選配：手動推進虛擬時鐘（預覽視窗 rAF 被節流時快轉驗證用，見步驟 5）
  };
  // 每個分鏡開始時發出（name 用企劃的分鏡名稱，例：「分鏡2 第一擊」）：
  window.dispatchEvent(new CustomEvent('demo:phase', { detail: { name, ms } }));
  // 分鏡內每個值得入鏡的瞬間，由表演程式在那一刻發出：
  window.dispatchEvent(new CustomEvent('demo:beat', { detail: { caption: '閃電擊中右側 2 罐' } }));
  ```
  舞台元素的 id 一律是 `stage`，裡面只有正式畫面元素；舞台下方狀態列與其他測試用元素一律加 `class="demo-ui"`（截圖時自動隱藏，萬一放進舞台也不會入鏡）
- **關鍵格（`demo:beat`）要在寫表演程式時就標好**——表演是自己寫的，哪一刻發生什麼最清楚，不要事後再猜。標的原則：
  - **要標**：每個看得出變化的瞬間——攻擊出手、命中、爆開、噴金幣、特寫高峰、表情轉變、場景切換、結算數字跳完
  - **不標**：同一個動作的中間過程、跟上一個關鍵格看起來一樣的瞬間、全畫面遮罩的轉場
  - **重複的動作每次都標**（第一擊、第二擊各自的命中），截圖後再決定企劃要不要全放
  - `caption` 就是分鏡圖上的標籤與企劃的細拆描述，**寫「這一刻畫面上在演什麼」**，一句話；點名部位或物件、用看得見的動作，不寫「感覺」「氛圍」（`動態描述規範.md` 第二節第 2 條）
- **關鍵格時間點要準（產 HTML 時就做，事後補很難）**——不處理時截到的關鍵格會晚 100–400ms，組員改完這四點偏差約 ±20ms：
  1. **自製虛擬時鐘每幀的 dt 不設上限**（不要寫 `Math.min(dt, 50)` 這類截斷）：CSS 動畫與 WAAPI 照真實時間走，時鐘被截斷就落後，beat 跟畫面對不上
  2. **所有圖片啟動時先 `await img.decode()`**，全部解碼完才開放捕獲按鈕與 `DEMO_API.play`：第一次解碼大圖會卡一幀（例：布幕合起時中間留一條縫）
  3. **emoji 粒子預先畫成 sprite**（啟動時用 offscreen canvas 每種 fillText 一次），每幀只 `drawImage`：每幀幾十次 `fillText` 在無頭瀏覽器會卡幾百 ms
  4. **beat 不要跟全螢幕白閃同一刻**：發在白閃之前，或白閃退掉之後，不然截到一片白
- **表演動作要是 Spine 做得到的**（Boss 是全 2D Spine）：不轉身、不做斜線或弧線的旋轉衝刺、不做流暢跳躍、飾物不繞到身後、會轉的光環是平面正圓。完整對照表見 `boss-design/boss設計法則.md` 第四節。demo 裡做得出不代表美術做得出
- 表演張力階梯要拉開：低級快進快出、高級要有 anticipation 停頓與全屏效果，讓權重手感差異體感明顯

### 5. 驗證與交付

- 產出後自己先開瀏覽器過一次：每級（拆解型：每個結局＋幾個邊界倍數）強制播一遍確認無 JS error、模擬 ×1000 分布合理、拆解型組不出率跟步驟 1.5 預檢對得上
- **Claude 預覽視窗被隱藏時 rAF 會被節流**，乾等表演跑完很久、時間也不準：驗證改用「手動推進虛擬時鐘」快轉——`DEMO_API` 多給一個 `advance(ms)`（把虛擬時鐘往前推 ms，跑完這段該發生的分段與 beat），用它把整段表演跑完再 assert 結果（DOM 狀態、console 無錯），不要開著乾等
- 交給使用者試玩 → 後續調參迭代走 `playtest-loop`
- 輸出位置：使用者指定的專案資料夾；未指定 → `Desktop\<boss名>-reward-demo\`

**分享版打包**（要把 demo 傳給別人試玩時）：

- 新檔名帶**版號＋日期**（例：`<boss名>_demo_v3_20261008.html`），**不覆蓋舊版**——試玩者的回饋要對得回是哪一版
- 附**試玩說明**（`試玩說明.md`），至少寫：
  1. 怎麼開（雙擊用 Chrome／Edge 開，不需要網路）
  2. 每顆按鈕與面板區塊的用途（捕獲、強制播、指定最終倍數、暫停／下一分鏡／結束、模擬、匯出／匯入設定）
  3. **哪些是暫定值**（預設模板補的、企劃矛盾先照分鏡值的、佔位素材）
  4. 回饋怎麼給：調完按「匯出設定」把 JSON 傳回，或貼「變更區段 Markdown」
- HTML＋試玩說明一起壓成 zip（檔名同樣帶版號＋日期）

### 6. 定稿後：擷取分鏡圖、寫回企劃

**表演的分鏡圖從 demo 截，不另外生圖。** 動畫太複雜，先在 demo 裡把節奏和畫面調到定稿，再截圖，分鏡就是實際的樣子。使用者說「demo 定稿了」「要寫企劃了」「截分鏡」時做這步。

**截圖前先檢查**（沒做就先回步驟 4 補，不然關鍵格會晚 100–400ms）：虛擬時鐘 dt 沒有上限、圖片全部 `decode()` 過、emoji 粒子走 sprite、beat 沒跟全螢幕白閃同一刻；舞台裡沒有測試資訊（都在 `demo-ui` 狀態列）。截完 Read 分鏡圖，看關鍵格是不是那個瞬間——晚了一拍（命中前／爆開後）就回頭查這四點，不要靠改 caption 掩蓋。開發途中要驗證 beat 順序，用步驟 5 的 `advance(ms)` 快轉，不要開預覽視窗乾等

1. **截圖**：每種表演強制播一次，在每個 `demo:beat` 那一刻暫停截舞台；拆解型每個結局各播一次（用「指定最終倍數」挑該結局的代表值）

   ```sh
   python ~/.claude/skills/boss-demo/scripts/capture_storyboard.py capture <demo資料夾> <輸出資料夾> \
     [--scenarios <id,...>]
   ```

   - demo 宣告了 `beats: true` 就自動走關鍵格模式，同時記下每格在分鏡內的時間點
2. **組成分鏡圖＋企劃草稿**

   ```sh
   python ~/.claude/skills/boss-demo/scripts/capture_storyboard.py compose <輸出資料夾> --scenario <id> [--pick 1,2,4,…]
   ```

   - 預設**全部關鍵格都入圖**，標籤直接用 `caption`，不寫秒數（秒數在企劃文字與 demo 裡）
   - Read 分鏡圖檢查；企劃不需要全放時（例如重複的「噴金幣」只留一次）用 `--pick` 去掉
   - 企劃草稿**照 `動態描述規範.md` 的格式**：一個分鏡一步、秒數寫句尾、`〔圖N〕` 對回分鏡圖格號；同一分鏡多個關鍵格列成子項，共用該分鏡秒數。後面接規範要求的待補欄位（觸發時機、階段差異、同步點、圖層、表演期間碰撞／倒數、詳見 4.x）：

     ```
     1. 觸發時機：〔待補〕
     2. 分鏡：
         1. 分鏡1：舉杖——雙眼發光、高舉權杖，1.5秒〔圖1〕
         2. 分鏡2：第一擊，2秒〔圖2–3〕
             1. 閃電擊中右側 2 罐
             2. 罐子爆開噴金幣
     3. 階段差異：〔待補〕 …
     ```

   - 版面依格數自動排：≤3 格一列、4 格 2×2、5–9 格三欄、更多四欄

**舊 demo 沒有關鍵格時的備援**（例：戰神賽特 demo）：用 `--shim` 注入 `DEMO_API`（範例：`scripts/shims/seth-reward-demo.js`）、`--hide` 隱藏沒加 `demo-ui` 的按鈕、`--skip-phases` 排除轉場；capture 會改成每個分鏡在 35%／75% 處各截一張當候選，接著：

1. **刪掉太接近的，剩下的組成分鏡圖**：**不限格數**，把跟鄰格太像、看不出差別的候選刪掉，每個看得出變化的瞬間都留

   ```sh
   python ~/.claude/skills/boss-demo/scripts/capture_storyboard.py compose <輸出資料夾> \
     --scenario <id> --pick 1,3,5,6,7,9,11,12,14 \
     --captions "被捕獲：雙眼發光、高舉權杖放出閃電|轉場至海底神殿，石塊從上方墜落|…"
   ```

   - 一定要 Read `候選_<表演名>.png`（全部候選的編號總覽）自己挑。不給 `--pick` 時的自動去重只是起點，實測會把「罐子被擊中」這種小範圍變化誤刪
   - **要刪的**：跟前一格幾乎一樣的（同一分鏡的兩個時間點沒變化）、重複的動作（第二次噴金幣跟第一次一樣就留一次）、還在過渡中的（結算數字還在跳，留跳完的那張）
   - **要留的**：攻擊命中、爆開、特寫、表情轉變、場景切換——每個看得出變化的瞬間
   - **分鏡圖上的標籤寫「這格在演什麼」**（`--captions`，用 `|` 分隔），**不寫秒數**——秒數寫在企劃文字與 demo 裡
   - 版面依格數自動排：≤3 格一列、4 格 2×2、5–9 格三欄、更多四欄
   - 產出：`分鏡_<表演名>.png`、`分鏡_<表演名>_企劃草稿.md`（格式同上；每格一步：描述＋秒數，下一行註記涵蓋哪些 demo 分段，貼企劃前刪；同一分鏡留了多張時平分該分鏡的秒數，總秒數對得上 demo）
**之後兩種模式共用：**

3. **寫企劃段落**：以 `分鏡_<表演名>_企劃草稿.md` 為骨架，**照 `動態描述規範.md` 寫**——關鍵格模式的描述與秒數已經在草稿裡，看圖確認後改成「主體＋可見動作＋特效＋位置」（caption 是看圖的短句，不夠美術直接做）；備援模式要依截圖補描述。秒數用 demo 定稿值。〔待補〕欄位逐一填掉或刪掉，交付前跑規範第六節自查。每段標【貼到企劃 X.X.X】，跟「變更區段 Markdown」合在一起交給使用者
4. **寫回 Notion**：預設由使用者手動貼回（分鏡圖一起上傳）。**不自己改 live 企劃**，除非使用者明確要求

## 預設四級模板（企劃缺漏時補用）

| 獎級 | weight | 表演 | phases（ms） |
|---|---|---|---|
| 小獎 | 55 | boss 翻肚＋金幣小爆 | 登場 300 / 爆分 800 / 結算 400 |
| 中獎 | 30 | 金幣噴泉＋獎級橫幅 | 登場 600 / 爆分 1600 / 結算 800 |
| 大獎 | 12 | 全屏閃光＋boss 特寫拉近＋倍率跳數 | 登場 1200 / 爆分 2600 / 結算 1200 |
| 特獎 | 3 | Jackpot：暗場→聚光→連環爆分→結算 | 暗場 1000 / 聚光 1500 / 連環爆分 4000 / 結算 1500 |

## 銜接

- Boss 外觀設計（定稿圖）→ `boss-design`；定稿圖直接當步驟 2 的 `--reference`
- Boss 專屬背景（表演場景）→ `boss-scene`；可直接當 demo 的表演背景
- 特效素材生圖 → `generate2dsprite`（Q 版用 `art_style=cel_shaded_chibi`）
- 試玩迭代迴圈 → `playtest-loop`
- 要進茶會展示 → `demo-intake`（屆時再拉高 polish、debug 面板加收合）
- 權重/倍率的期望值驗算 → 派 `game-balance-auditor`

## 貼回企劃（2026-10-02 起）

定稿後要放進 Notion 企劃時，交給 `plan-dept14-writer` 的**貼圖模式**（第十一節，腳本 `plan-dept14-writer/scripts/paste_images.py`；落點總表 `plan-dept14-writer/references/image-slots.md`）。PM 給目標頁網址 → `list` 找右欄與卡位 → 報清單取得同意 → 貼 → 回讀。本 skill 產出的落點：

- 分鏡 → Boss 頁 `3.3 Boss動態 > 3.3.x <表演名>`：**分鏡細拆文字（照 `動態描述規範.md`）寫在同一個小標題的左欄，分鏡圖整張一張貼右欄，不切圖**（Tim 2026-10-02），caption《<表演名>分鏡示意圖》。舊頁面是一分鏡一張圖，新寫的照這條
