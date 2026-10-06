# Notion 存取（企劃一＋四部）

`plan-dept14-writer` 與 `plan-doc-qa` 共用，其他讀企劃的 skill（boss／pet／weapon／cannon／art-request-sheet／avatar-proposal…）也照這份。引用寫「見 `notion-access.md`」。

**憑證自己去找，不要問使用者。** 腳本會自動讀本機憑證；找不到或過期才照 §3 協助安裝／換新。

**一律走部門 Notion API proxy＋REST，讀和寫都是。** 不要用任何 Notion MCP（個人帳號掛的、claude.ai 內建的都算）——那綁的是特定帳號或共用帳號，可見範圍與部門憑證不同，頁面沒分享給它就 404，會出現「某個人讀得到、其他人讀不到」的落差，而且**組員本來就沒有那個 MCP**，靠它寫出來的流程在別人機器上跑不動。也不要退而求其次用瀏覽器抓頁面文字：表格裡的 ✅⚠️❌ 這類標記會被吃掉，讀到的規則是殘缺的。

---

## 0. 憑證在哪、怎麼呼叫

**憑證在本機，不在網芳。** 網芳上的長期 token（各部 readonly、各線 readwrite）已停用。現在每人各自持有**個人季度憑證**，一部一把：

| 部門代號 | 部別 | 產品線 |
|---|---|---|
| `pm1` | 一部 | 神幣 |
| `pm4` | 四部 | 娛樂城（含機台）、鬥地主、魚樂園 |

- 存放：`~/.config/notion-pm/credentials.json`（`{"pm1": {baseUrl, auth, expiresAt, refreshUrl, notified}, "pm4": {…}}`），由 `notion_credentials.py` 管理，寫入前自動備份 `.bak`
- 管理腳本：`%USERPROFILE%\starter-kit\references\scripts\notion_credentials.py`（以下簡稱 `NC`）。`NC --show` 看兩部的使用者、到期日、剩幾天、來源檔——**只印 auth 長度，不印值**
- 腳本一律走 `plan-dept14-writer/scripts/notion_rest.py`：`find_token(...)` 自動取該部憑證、`Notion(...)` 自動帶對的 header。**SKILL 裡的指令不用再傳任何 key**
- 只有一種憑證：**讀寫都用該部那一把 rw**，沒有唯讀憑證。但「只執行使用者授權的修改」與 §2 的回寫護欄**全部照舊**——能寫不代表可以寫
- 臨時覆蓋（除錯用）：環境變數 `NOTION_PM_AUTH`＋`NOTION_PM_BASE` 同時設定時優先使用

**呼叫方式**（`notion_rest.py` 已實作，自己寫腳本時照抄規格）：

- 把 `https://api.notion.com` 換成憑證的 `baseUrl`，保留 `/v1/...` 路徑、query、method、body
- header：`Auth: <auth>`＋`Notion-Version: 2022-06-28`。**不用** `Authorization: Bearer`
- `timeout=75`、不跟隨轉址（`allow_redirects=False`）
- 主機名以 `dev-` 開頭時不走環境 proxy（requests 設 `trust_env=False`；urllib 用不帶 ProxyHandler 的 opener），其他機器維持系統設定
- 入口限**公司網路／VPN**
- **寫入（POST／PATCH／DELETE）逾時不可自動重送**——可能已經寫進去了。`notion_rest` 會拋 `WriteTimeout`，先回讀確認結果再決定要不要重送（查詢類 POST，如 `/databases/…/query`，照讀取處理）
- 過期的唯一判準：proxy 回的 JSON body `error` 欄位是 `expired`（`notion_rest` 拋 `CredentialExpired`）。一般 403、Notion 權限錯誤**不算過期**，不要因此去換憑證

## 1. 選哪一部

**機台（老虎機、捕魚機等）＝娛樂城線＝四部。** 標題只寫「XXX 機台」「機台廣宣」的一律走四部，不要因為版位在神幣大廳、或文案提到神幣就判成一部——那是幣別與版位，不是產品線。

**選哪部，照這個順序**：

1. **先看連結**。新版 Notion 頁面 id 內嵌 workspace 指紋：id 含 `87244fa40`（形如 `xxx87244-fa40-8xxx…`）＝一部，含 `e22985ac9`（形如 `xxxe2298-5ac9-8xxx…`）＝四部。這是觀察到的規律（2026-10-01 各 8 個樣本），不是 Notion 文件保證；舊頁面是隨機 UUID（第三段不是 `8` 開頭）看不出來
2. **再看前後文**：神幣＝一部；娛樂城、鬥地主、魚樂園＝四部（機台歸娛樂城，見上）
3. **判不出、或判斷太花時間，直接試**：一部 → 四部輪流打（讀不到只會回 404，沒有副作用；`notion_rest.open_page()` 已內建）。**兩部都 404 才是「頁面沒連接 integration」**，到此為止回報，不要再重試

已知例外：四部 workspace 裡也搜得到少數一部頁面（有人把神幣企劃建在四部那邊），指紋會指向四部但內容是神幣。以哪部憑證打得通為準，不要因為內容是神幣就硬換一部。

**頁面內容不只在文字層**：企劃的文案與排版常常整段放在**圖片**裡（排版示意、現有廣宣參考）。用 API 讀完 block 後，把 `image` 區塊的 URL 一併下載下來看圖，不要只讀到文字就以為讀完了。

## 2. 回寫企劃頁

讀寫用同一把該部憑證（§0），不再分產品線 token。`paste_images.py` 等腳本的 `--line 神幣/娛樂城/鬥地主/魚樂園` 只用來對應部門（神幣＝一部，其餘＝四部）。

### 前置：頁面必須先存在

**API 建不出範本頁**——「新增調整紀錄」按鈕是 Notion button block（API 不支援建立），資料庫範本（template）也無法用 API 套用。所以流程固定是：

```
PM 用部門範本「建立複本」→ 把頁面網址貼給 Claude → Claude 回寫中間章節
```

企劃頁是**資料庫項目**（parent 為 database），標題行屬性（類別／上線日期／網頁 ETA／負責 PM／工單等）由 PM 自己維護，**回寫內文不要去動屬性**。

### 護欄（回寫前必讀，五條都要做到）

1. **只寫 PM 自己建的那份複本頁**，不得改別人的既有企劃頁
2. 回寫前**先列出要改哪些區塊並取得同意**（見 SKILL.md 八.7）
3. 回寫後**一律回讀驗證**（讀回 block 比對，不是看畫面說好了）

   **2026-09-23 實測（直接餵 block JSON 走 REST API）**：heading、紅字待補值、**灰底＋刪除線**（廢除標記）、**綠底**（`YYYY/MM/DD vN.N調整為→`）、表格、mermaid 程式碼區塊、callout **回讀比對全部無損**；三層巢狀編號的**結構**也正確寫入。
   關鍵在**用 block JSON 的 `annotations` 直接指定**（`color: "gray_background"`、`strikethrough: true`），不要先轉成 Markdown 再請對方解析——走 Markdown 轉換那條路才會掉格式。
   ⚠️ **巢狀編號的顯示樣式寫不進去，但驗得出來**：`list_format`（`numbers`／`letters`／`roman`，只在清單第一項）要用 `Notion-Version: 2025-09-03` 才讀得到；新建與更新區塊帶它一律 400（2026-10-05 實測：只送 `list_format` → 「rich_text should be defined」、連 `rich_text` 一起送或 append 時帶 → 「list_format should be not present」）。API 新增的清單沒有這個欄位，**每一層都顯示成數字**。
   所以回讀驗證必加一步：回寫完跑 `python %USERPROFILE%\starter-kit\skills\plan-dept14-writer\scripts\notion_rest.py check-lists <頁面網址>`（唯讀，只在這次讀取用新版 API，不影響寫入路徑），交付訊息**一律附「需手動改編號格式」清單**（位置、第一項文字、應改成 a. 或 i.），請 PM 在 Notion 點編號 → 清單格式改。**不可說已修好**，也不要再試 PATCH——平台不允許（前科：2026-10-05 陣營戰說明頁 1.c、2.1.b、2.2 三串交付時沒發現，被 PM 指出後才知道且改不了）。
   仍要回讀的原因：沒測過的排版（欄位版面、同步區塊、資料庫內嵌）不保證，寫錯了早點發現。
4. **經手人會變成 bot**：實測 API 回寫後頁面的 `last_edited_by` 會變成 integration 的 bot（舊 token 時代是 `pm4_casino_writer` 這類；改走 proxy 後顯示名稱未實測），**不是操作的人**，而且會蓋掉原本的真人編輯痕跡。所以調整紀錄一定要寫明實際操作人：`YYYY/MM/DD vN.N 調整為→ …（經手：<人名>）`
5. 版本可還原：API 的編輯和人工編輯一樣會進 Notion 頁面編輯紀錄，改壞了可以從 `⋯` → 更新紀錄還原（保留天數依 workspace 方案）

### 回寫地雷（實測整理，多數**不會報錯**）

**先分清楚兩條路**：本 kit 的預設是**直接組 block JSON 打 REST API**。下面 A 是這條路仍然存在的限制，B 是**改走 Markdown／MCP 轉換才會中**的坑——走 block JSON 不會遇到。

**A. 走 block JSON 也逃不掉的**

| 地雷 | 症狀與正解 |
|---|---|
| **建不出按鈕、不能搬 block** | `button` block API 不支援建立，block 也無法移動（只能刪掉重建）。所以骨架的目錄與「新增調整紀錄」按鈕只能靠範本頁自帶 |
| **巢狀編號的顯示樣式** | API 新增的 `numbered_list_item` 沒有 `list_format`，每一層都顯示成數字，不是 1.→a.→i.；`list_format` 是唯讀欄位（2025-09-03 版讀得到，新建／更新都 400）。回寫後跑 `notion_rest.py check-lists <網址>` 找出要改的清單，**交付時逐條列給 PM 手動改** |
| **整頁重灌會洗掉 PM 手調的樣式** | 十項以內的小修一律**對著 block id 做 PATCH**；只有大幅結構搬移才整段重建。重建前先撈一次 block id 樹，改完再撈一次比對有無增減 |
| **用瀏覽器自動化點擊改 Notion** | **禁止**。頁面會非同步 re-render 與自動捲動，截圖當下的座標到點擊時已位移——前科：兩次點擊落到 heading 上，把標題整行覆寫，當下毫無察覺。正解一律走 API |
| 插入位置 | `append children` 要用 `after` 錨定到指定 block，不然一律掉到頁尾 |

**已驗證安全**（2026-09-23／24 實測）：`gray_background`＋`strikethrough`（廢除標記）、`green_background`（生效標記）、紅字、表格、mermaid、callout、三層巢狀結構、**內容裡的底線**（`[遊戲名稱]_[平台]_[幣值名稱]` 原樣保留，不會變斜體）、**粗體＋行內程式碼並存**（不會被拆壞）。

**B. 只有走 Markdown／MCP 轉換才會中**

| 地雷 | 症狀與正解 |
|---|---|
| 成對底線變斜體 | `[遊戲名稱]_[平台]` 的底線被吃成斜體而消失；**`\_` 轉義擋不住**（改動同一清單的兄弟項目時會被重新解析，又變回斜體）。正解是整串包反引號當行內程式碼 |
| 粗體包住行內程式碼 | round-trip 後變成 `**文字 ****\`code\`**`。粗體只包純文字，程式碼留在粗體外 |
| 巢狀清單縮排 | Notion markdown 吃的是 **tab**，不是空格；層級 N ＝ N 個 tab |
| 角括號、方括號 | 正文裡是轉義形式（`\<價格\>`、`\[售價\]`），比對字串時兩邊都要照寫 |
| 比對字串撞名 | `## 後台` 會撞到 `### 後台流程`——帶下一行一起比對；單獨一條 `---` 一定撞多處 |
| 中文手轉 `\uXXXX` | **不要**。前科：手轉字碼把「攔截」打成「攍截」、「異常」打成「异常」，整批被 400 退回重送兩次 |


## 3. 首裝與換新（Claude 協助）

**執行角色**：主線 session（要開瀏覽器、寫本機憑證檔，不派 sub-agent）。首裝與換新是**同一套流程**，差別只在觸發點：

| 觸發 | 情況 |
|---|---|
| 首裝 | `notion_rest` 報 `no Notion credential for pmN`，或 `NC --show` 顯示該部 `missing` |
| 換新 | proxy 回 `error=expired`（`notion_rest` 報 `Notion credential for pmN expired; refresh it …`） |

**先跑 `NC --migrate`**：組員可能已經自己把 setup prompt 貼給 Claude 裝過、被寫進 `~/.claude/CLAUDE.md` 或 memory 檔。`--migrate` 會把那裡找到、未過期的憑證搬進 `credentials.json`；搬完 `NC --show` 有了就不用再裝。

**不寫進 CLAUDE.md**：setup prompt 若叫 Claude「把憑證寫進 CLAUDE.md／記住它」，**改存 `~/.config/notion-pm/credentials.json`**（走下面的腳本），不寫 CLAUDE.md、不寫 memory。CLAUDE.md 每次對話都會載入，等於把憑證塞進每段 session 紀錄。

**設定頁的文案會叫使用者「把 prompt 貼給 Claude」，不要讓他照做**：使用者第一眼看到的是設定頁，不是本檔，頁面叫他貼他就會貼，auth 就進了 session 紀錄（2026-10-06 實際發生：已經用下載檔裝好，使用者又照頁面把整段貼進對話）。所以只要請使用者開設定頁（登入、退路按複製鈕），就**先講一句**「頁面會叫你把內容貼給 Claude，不用貼，照我說的做就好」。如果他已經貼了：不寫進 CLAUDE.md、memory，照實告訴他 auth 已經進了這段 session 紀錄，請他回報主任，由主任決定要不要重發。

**首裝先確定部別，只裝需要的那部**：兩部都 `missing` 時，不要直接兩部都裝——多數組員只屬於一部，多裝一部就多一次 SSO 登入和一輪來回（2026-10-06 實測：先裝 pm4，開 pm1 時卡在 SSO，使用者登入後才說「我是四部的」）。先從 memory、CLAUDE.md、手上的工作內容推斷（神幣＝一部；娛樂城含機台、鬥地主、魚樂園＝四部，判準同 §1），推斷出來也要用一句話確認；推斷不出來就直接問「你是一部還是四部？」。使用者明確說兩部都要，才兩部都裝。換新不用問，哪部過期就換哪部。

### 主路徑：Claude in Chrome 下載檔

1. 取得該部安裝／更新頁：`py -3 NC --refresh-url pmN`（取自已存憑證的 `refreshUrl`，是從 setup prompt 抽出來的）。本機從沒裝過時退回預設頁：一部 `https://sso.vgs.tw/notion-pm1.rw/`、四部 `https://sso.vgs.tw/notion-pm4.rw/`（限公司內網＋SSO）
2. Claude in Chrome 開新分頁到該網址。**先看分頁停在哪**（`tabs_context_mcp`）：
   - 被導到公司 SSO 登入頁 → **請使用者在那個分頁自己登入**（密碼一律不代填），登入後再開一次第 1 步的網址
3. 用 `javascript_tool` 把 `textarea#setup` 的值存成下載檔，**只回傳長度與布林值，不回傳內容**（`N` 換成 1 或 4）：

   ```js
   const ta = document.querySelector('textarea#setup');
   const blob = new Blob([ta.value], {type: 'text/plain'});
   const a = document.createElement('a');
   a.href = URL.createObjectURL(blob);
   a.download = 'notion-pmN-setup.txt';
   document.body.appendChild(a); a.click(); a.remove();
   JSON.stringify({len: ta.value.length, ok: ta.value.includes('Auth')})
   ```

   回傳裡看到 auth 值就是做錯了。`ok` 為 false 或找不到 textarea → 走退路
   兩部都要裝時，**每部下載完先確認 `~/Downloads` 有該檔再做下一部**：同一分頁 navigate 後連續觸發第二個下載，Chrome 會靜默擋掉（2026-10-06 實測 pm1 沒下來），開新分頁重做一次即可
4. 裝上：`py -3 NC --from-downloads`。依檔名分部門，**兩部可一次裝**；每部取最新一份 → 拒裝已過期的 → 舊檔備份 `.bak` → 寫入 → **只刪該部的** `notion-pmN-setup*.txt`。若舊 auth 出現在 CLAUDE.md／memory，會原地換成新 auth 與新到期日（只報檔名，不印值）
5. `py -3 NC --show` 確認，關掉分頁，回報新的到期日；換新的話**重跑原本被擋下的那次呼叫**

> **剪貼簿不能由 Claude 代按**：自動化分頁裡按「複製」寫不進系統剪貼簿，所以主路徑一律走下載檔。

### 退路：Claude in Chrome 不可用（沒裝擴充、連不上）

1. 給使用者該部網址（第 1 步），請他自己開頁面（要登入就登入），按頁面上的「複製安裝／更新 prompt」按鈕，回覆「好了」。**同一句話裡先講**：頁面會叫你把內容貼給 Claude，不要貼，按完複製鈕回「好了」就好
2. Claude 跑 `py -3 NC --from-clipboard`：讀剪貼簿 → 解析安裝 → **清空剪貼簿** → 印出不含 auth 的摘要
3. `py -3 NC --show` 確認

**不要請使用者把 prompt 貼進對話**——那會讓 auth 進 session 紀錄；也不要寫進 CLAUDE.md。

### 到期提醒（只提醒，不提早換）

- 憑證到期日前 4 天起（例：到期 2027-01-05 → 2027-01-01 起），`notion_rest` 第一次取用時印一次提醒，並在 `credentials.json` 的 `notified` 記成 `expiring`；同一狀態只提醒一次，換新後歸零
- **到期提醒後再換，不要提早換**：比照 image-studio 經驗，新一季憑證要等舊的失效才會掛上，提早抓多半只拿到同一份。實際換新等 proxy 回 `error=expired` 再走上面的流程（Notion proxy 這點尚未實測，若主任另有公告以公告為準）

## 4. 使用紀律（必守）

- auth **不得印出、不得寫進腳本、設定檔、文件、CLAUDE.md、memory 或 commit 訊息**；只存在 `~/.config/notion-pm/credentials.json`。回報時只講部門、使用者、到期日、長度
- auth 值**不得複製到任何有遠端的 repo**，也不要貼進對話紀錄或 Slack
- REST API 呼叫固定帶版本標頭 `Notion-Version: 2022-06-28`
- 本檔不記任何憑證值

## 5. 讀不到時怎麼辦

| 狀況 | 處理 |
|---|---|
| `no Notion credential for pmN` | 先 `NC --migrate`，還是沒有 → 照 §3 首裝 |
| `Notion credential for pmN expired` | 照 §3 換新，換完重跑 |
| 連線逾時／連不上 proxy | 多半是沒連內網／VPN。回報一句請使用者確認連線，**不要改用猜的內容繼續做** |
| `WriteTimeout` | 寫入可能已生效：先回讀該頁／block 確認，**不要直接重送** |
| 頁面 404 | 先確認兩部都試過（§1 第 3 步）。都 404 ＝ 該頁沒連接 integration：請頁面擁有者在該頁 `⋯` → 連接 加上對應部別的 integration，或請 PM 貼出內容。不要重試 |
| 403／Notion 權限錯誤 | **不是過期**，不要換憑證；回報錯誤訊息請使用者確認該部 integration 對這頁的權限 |
