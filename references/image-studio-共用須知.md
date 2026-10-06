# image-studio 共用須知

> 所有走 image-studio 產圖的 skill 共用這一份（`imagen` 系列、`generate2d` 系列、`cannon-wing`、`cannon-parts` …）。
> 這裡只記**平台與流程層面**的通則；各 skill 自己的版型與提示詞寫在各自的檔案。
>
> ⚠️ **不要把這些內容寫進 `~/.claude/skills/image-studio/`**——那是官方 skill，重新安裝會覆蓋掉。

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

`~/.config/image-studio/credentials.json` 裡的 `expiresAt` 就是到期時間。過期後一律 401、生不了圖。

- **不要提前換**：新一季的憑證要等舊的失效才會發布，提早抓只會拿到同一份
- kit 不含任何憑證；新一季的 setup prompt 自己沒有管道拿就**找主任拿**

### 換季只換憑證：用 kit 的腳本裝，不跑官方安裝程式

client 程式沒改的季度，換季只需要覆寫 `credentials.json`（`baseUrl`／`token`／`expiresAt` 三欄）。**不要每季都跑官方 `agent-install.py`**——Claude Code 開 auto mode 時，「下載外部程式再執行」會被安全機制擋下，而且加 allow 規則也沒用（組員 2026-10-06 實測兩次）。

1. 把新一季的 setup prompt **整段存成一個 txt 檔**（例：`Downloads\image-studio-setup.txt`）。**不要貼進對話**——裡面有 token，貼了就進 session 紀錄
2. 請 Claude 跑（或自己在提示列用 `!` 開頭跑）：

   ```
   py -3 %USERPROFILE%\starter-kit\references\scripts\refresh_credentials.py --from-file %USERPROFILE%\Downloads\image-studio-setup.txt
   ```

3. 腳本會：抽出那段 JSON（三欄缺一就報錯不寫）→ 拒裝已過期的憑證 → 舊檔備份成 `credentials.json.bak` → 寫入新檔 → **刪掉來源 txt**（加 `--keep-source` 才保留）→ 印出不含 token 的摘要（網址、到期日、剩幾天）
4. 只想查目前憑證幾天後到期：`--show`

**什麼時候還是要跑官方安裝程式**：官方發布說明有提到 client 或 SKILL.md 改版、或 `~/.claude/skills/image-studio/` 根本不存在（新裝）。這時被 auto mode 擋下，請使用者自己在提示列用 `!` 跑那支安裝程式；**不要把含 token 的 JSON 寫在 `!` 指令裡**，改成先存檔。

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
