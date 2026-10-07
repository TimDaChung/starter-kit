# image-studio 共用須知

> 所有走 image-studio 產圖的 skill 共用這一份（`imagen` 系列、`generate2d` 系列、`cannon-wing`、`cannon-parts` …）。
> 這裡只記**平台與流程層面**的通則；各 skill 自己的版型與提示詞寫在各自的檔案。
>
> ⚠️ **不要把這些內容寫進 `~/.claude/skills/image-studio/`**——那是官方 skill，重新安裝會覆蓋掉。

---

## 零、送出前先算張數：每小時配額與素材表

**配額是每人每小時 30 張**（滿了平台回 HTTP 429 `hourly_limit 30/30`，要等整點後一小時重置）。組上多人各自有配額，但一個人一次送太多一樣會撞牆。

- **送出前先算總張數**：這批要幾件 × 每件幾張。超過 15 張就先想能不能合併
- **並行不要超過 2–3 個請求**：一口氣送十幾個請求，容易整批 `IncompleteRead`，而且**配額照扣、一張都拿不到**（組員 2026-10 實測：15 個請求、30 張，全滅）
- **同風格的小素材合併成一張素材表一次產**，再自己按格裁切：
  - 適用：頭像、道具、icon、小特效這類**版型相同、單件不需要滿版解析度**的東西
  - 不適用：需要滿版解析度的（背景、布幕、分鏡）、版型差異大的（橫幅配小 icon）——這類各自一張。cannon-parts「版型差異大的不要塞同一張」是同一條規則的反面，兩條一起看
  - 實例：Boss demo 要 8 個妖怪頭像＋6 件道具＋3 張布幕，逐件送要 30 張；改成妖怪 4×2 一張、道具 4＋2 一張（都加 `--remove-background`）、布幕各一張，**7 張全部到手**，品質跟單張產沒差
- **素材表的提示詞**要寫明：`16:9、N 欄 × M 列、每格一件、逐格列出內容、格與格之間大片留白、無格線、無文字`。**格間留白是必要條件**——物件彼此碰到，裁切時會被當成同一件
- **裁切用 kit 的共用腳本**（`--remove-background` 產的透明素材表）：

  ```
  py -3 %USERPROFILE%\starter-kit\references\scripts\sheet_cut.py <素材表.png> <輸出資料夾> --cols 4 --rows 2 [--last-row 2] [--names a,b,c,...]
  ```

  不照固定格線切，而是把每個不透明的物件歸給「重心所在的那一格」，所以**物件超出自己的格子也會整件切出來、不會把殘片切進隔壁格**（組員踩過：丹爐的腳超過中線，被切進下一列的雲和眼睛裡）。小於一格 0.2% 的雜點會丟掉；空格會警告。
- **切完一定要看 `_check_dark.png`**：每件放在深色底上排一張，用來檢查白邊、殘片、被切掉的邊緣。沒看過不交付

---

## 一、算圖中斷時怎麼辦

算圖偶爾會以 `IncompleteRead` 之類的連線錯誤收場。

**不要直接重送。** 平台那邊的工作可能還在跑，重送會產生重複任務、多燒一次額度。

先查平台分頁狀態：

```python
import json, pathlib, urllib.request
d = json.loads((pathlib.Path.home()/'.config'/'image-studio'/'credentials.json').read_text())
base, tok = d['baseUrl'].rstrip('/'), d['token']
req = urllib.request.Request(base + '/api/tabs', headers={'Authorization': 'Bearer ' + tok})
with urllib.request.urlopen(req, timeout=30) as r:
    tabs = json.loads(r.read().decode()).get('tabs', [])
for t in tabs[-8:]:
    print(t.get('id'), t.get('status'), bool(t.get('lastImageSrc')))
```

判讀：

| status | 有無圖 | 意思 |
|---|---|---|
| `running` | — | **還在跑，繼續等**，不要重送 |
| `idle` | 有 | 已完成，圖在平台上，可直接取用 |
| `idle` | 無 | **該張失敗了**，可以安全重送 |

---

## 二、憑證到期

`~/.config/image-studio/credentials.json` 裡的 `expiresAt` 就是到期時間。過期後算圖一律回 **HTTP 401**（client 報 `API key expired/invalid`）。

- **不要提前換**：新一季的憑證要等舊的失效才會發布，提早抓只會拿到同一份。**只在撞到 401 之後換**
- **token 全程不得出現在對話、log、commit、Slack**。以下流程刻意讓 token 只走「瀏覽器 → 下載檔 → 腳本 → `credentials.json`」
- 換季只換憑證，**不要每季都跑官方 `agent-install.py`**——Claude Code 開 auto mode 時「下載外部程式再執行」會被擋，加 allow 規則也沒用（組員 2026-10-06 實測兩次）

腳本：`%USERPROFILE%\starter-kit\references\scripts\refresh_credentials.py`（以下簡稱 `RC`）

### 撞到 401 時，Claude 自己換（主路徑，使用者不用動手）

**執行角色**：主線 session（要開瀏覽器、寫本機憑證檔，不派 sub-agent）。需要 Claude in Chrome 已連線。

1. 取得憑證頁位址（有本機憑證時由 `baseUrl` 組出；沒裝過時印預設 `https://image-studio.vgs.tw/agent-api`）：`py -3 RC --page-url`
2. Claude in Chrome 開新分頁到該位址。**先看分頁停在哪**（`tabs_context_mcp`）：
   - 被導到公司 SSO 登入頁 → **請使用者在那個分頁登入**（密碼一律不代填），登入後再開一次第 1 步的位址
   - 分頁自己跳回 `chrome://newtab`、JS 無法執行 → 多半也是 SSO 過期，改開 `baseUrl` 首頁確認，會停在登入頁
3. 用 `javascript_tool` 把頁面 textarea 裡的 setup prompt 存成下載檔，**只回傳長度與布林值，不回傳內容**：

   ```js
   const ta = document.querySelector('textarea');
   const blob = new Blob([ta.value], {type: 'text/plain'});
   const a = document.createElement('a');
   a.href = URL.createObjectURL(blob);
   a.download = 'image-studio-setup.txt';
   document.body.appendChild(a); a.click(); a.remove();
   JSON.stringify({len: ta.value.length, ok: ta.value.includes('credentials.json')})
   ```

   回傳裡看到 token 就是做錯了。`ok` 為 false 或找不到 textarea → 走下面的退路
4. 裝上：`py -3 RC --from-downloads`。腳本會抽出 JSON（三欄缺一就報錯不寫）→ 拒裝已過期的 → 舊檔備份成 `credentials.json.bak` → 寫入新檔 → **刪掉下載資料夾裡所有 `image-studio-setup*.txt`** → 印出不含 token 的摘要
5. 關掉分頁，回報新的到期日，**重跑原本被 401 擋下的那次算圖**

> **剪貼簿路線不可用**：憑證頁的「複製」按鈕在自動化分頁裡按下去寫不進系統剪貼簿，一律走上面的下載檔。

### 退路（照順序退，不跳級）

| 狀況 | 怎麼辦 |
|---|---|
| Claude in Chrome 沒連上 | 請使用者自己開憑證頁（`--page-url` 印出的位址），把 setup prompt 整段存成 `Downloads\image-studio-setup.txt`，再由 Claude 跑第 4 步 |
| 頁面結構變了（找不到 textarea） | 同上 |
| `--page-url` 印出預設網址、`--show` 報 no credential | 本機從沒裝過 image-studio，不是換季——走下面〈首裝流程〉 |

### 首裝流程（本機從沒裝過；未實測）

1. 開 image-studio 設定頁`https://image-studio.vgs.tw/agent-api`（`py -3 RC --page-url` 也會印這個）。被導到公司 SSO 登入頁 → 請使用者在該分頁自己登入（密碼不代填）
2. 該頁的 prompt 是**完整安裝**（含下載並執行官方 `agent-install.py`），不是只有憑證
3. Claude Code auto mode 會擋「下載外部程式再執行」（組員 2026-10-06 實測，加 allow 規則也沒用）。所以請使用者**先按 Shift+Tab 切離 auto mode**（切到預設模式，逐步批准），再把 prompt 交給 Claude 照做；裝完再切回 auto mode
4. 裝好後之後的換季一律走上面的換季流程（`RC`），不用再跑官方安裝程式

請使用者接手時講清楚：去哪一頁、複製哪段、存成什麼檔名，存好後 Claude 接手裝。**不要請使用者把 setup prompt 貼進對話**——那會讓 token 進 session 紀錄。

### 什麼時候還是要跑官方安裝程式

新裝 image-studio，或官方發布說明有提到 client／SKILL.md 改版。被 auto mode 擋下時請使用者自己在提示列用 `!` 跑；**不要把含 token 的 JSON 寫在 `!` 指令裡**，先存檔再讀。

## 三、平台會偶發異常

同一份提示詞跑兩次，可能一次正常、一次壞掉。已知的異常型態：

- 畫成**扁平貼紙風**（白色描邊＋投影）
- 背景出現**雜訊色塊**或**漸層**，而非要求的純色
- 每格被加上**圓形／橢圓形底色卡**（去背時整塊會被當成主體保留，**不可用**）
- 擅自加上**文字標籤**
- 產出與企劃明顯不符
- 出現**透視變形**（要求正投影時）

**對策是重抽，不是改提示詞。** 改提示詞去追隨機異常，只會把提示詞越寫越長、反而傷害品質（見第五節）。

因此**每輪至少 `--count 2`**，留備選。

---

## 四、模型的固定偏誤

- **粒子特效一律跑成螢光黃綠**，無論企劃指定什麼顏色。實測多組全中。
  - 提示詞裡放一句輕量排除（「不可畫成螢光綠或黃綠色」）即可，**不要寫成強調段落**
  - 真的跑掉就後製色相位移（`cannon-wing/scripts/recolor.py`），不要回頭跟模型搶注意力
- **傾向把圓形物件的中心填滿**。需要中空的環狀物件，要把「中央留空」寫成最高優先規則。
- **傾向把物件完整畫進畫面**。需要局部特寫時，要明講「看不到頭也看不到尾、兩端被畫面邊緣切斷」。

---

## 五、提示詞的注意力是零和的

**這是最重要的一條。** 加字去修 A 問題，就會從 B 扣。

實測序列（同一份企劃，只改提示詞）：

| 版本 | 精緻度 | 去背 | 特效顏色 |
|---|---|---|---|
| 原始 | 好 | OK | ✗ 偏色 |
| 加強配色敘述 | ✗ **垮掉** | ✗ **失敗** | ✅ 正確 |
| 壓回精簡 | ✅ 回來 | ✅ 修好 | ✗ 偏色 |

推論與對策：

1. **不要靠「規則寫越多越保險」**，那是錯的方向。
2. **結構性規格優先**（方向、尺寸、版型、中央留空——錯了就不能用），畫面品質次之，配色最後。
3. **能交給程式的就不要寫進提示詞**。每移走一項，畫面品質就拿回一份注意力。實測把「方向」從提示詞移到後製轉向後，連帶配色也自動正確了。

---

## 六、能用程式保證的，不要靠模型自律

這是所有生圖 skill 的共同原則。已驗證有效的程式化項目：

| 需求 | 別寫進提示詞 | 改用 |
|---|---|---|
| 風格與定稿一致 | 文字描述配色材質 | `--reference` 餵定稿圖 |
| 特效顏色 | 提示詞硬壓 | 事後色相位移 |
| 素材方向 | 叫模型畫橫躺／旋轉 | 生成時用模型最自然的方向，事後程式轉向 |
| 多件的相對位置與層序 | 叫模型排版 | 分件生成後程式合成 |
| 背景色、標籤、版位框 | 叫模型畫 | 程式鋪底加字 |

判準：**有唯一正確答案、可機械驗證的事，交給程式。** 模型只負責「畫什麼」。
