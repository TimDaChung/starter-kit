# 流程圖慣例（mermaid 畫法、節點命名、渲染、語意自檢）

`plan-dept14-writer` 第七節「流程圖」的權威參考：使用者要 Claude 產流程圖時照這份畫。判斷節點的每條出口都要對得上規則章條號（第 5 條）。

部門慣例是貼圖＋附編輯檔連結（gitmind／whimsical／figma），圖由 PM 自己管；**使用者要 Claude 產流程圖時**用 mermaid 畫，**交付預設是 Notion 的 mermaid 程式碼區塊**（code block、`language: mermaid`，`notion_rest.code_block(src)`），PNG 只在本機渲染拿來自檢與存檔（v3.42.0 起，組員建議；之前是貼 PNG）。理由：PM 能直接在 Notion 改、原始碼不會只留在本機、`plan_lint.py` 與 plan-doc-qa 的流程圖語意對照**只認 mermaid 區塊**，貼 PNG 的圖審不到分支邏輯。Notion 端實測（2026-10-13）：classDef 六色票、`linkStyle` 虛線、init 的 `edgeLabelBackground` 都生效，`mainBkg` 不會改頁面底色（深色模式下圖底跟頁面走，節點淺色填色仍清楚）；**預設顯示「程式碼＋預覽」上下並排**，API 設不了顯示模式，要只看圖請 PM 在區塊右上角切成「預覽」——交付訊息講一句。使用者明講要圖檔才另貼 PNG：

1. **節點順序照系統實際判斷的先後**：玩家看到畫面前就要判斷的（資格、版本、活動是否開放…）畫在最前面，不套企劃正文的操作順序（SKILL.md 第九節第 7 條的例外）。玩家流程與後台流程的擺放位置照範本；未定數值標「後補」絕不捏造；圖與規則矛盾先指出確認；圖只畫動作與判斷，不寫介面上看得到的資訊；有門檻的節點寫「是否大於 XX？後台可調，預設 N」；**每一種結局各走各的路徑**；玩家可跳回前一步的捷徑用虛線畫
2. **語法**：`flowchart TD`、標籤全繁中、多行用 `<br/>`；`[方框]`＝頁面／狀態、`(圓角)`＝動作、`{"菱形"}`＝判斷；邊標籤＝使用者動作；顏色用固定 init 區塊＋classDef 六色票（起訖粉／判斷橙黃／動作藍／Dialog 紫／獎勵綠／頁面灰），fill、stroke、stroke-width、color 四項都給：

```
%%{init: {'theme':'base','themeVariables':{'fontSize':'14px','textColor':'#1a1a1a','lineColor':'#5c6570','edgeLabelBackground':'#ffffff','mainBkg':'#ffffff'}}}%%

classDef startEnd fill:#ffd6e0,stroke:#c2255c,stroke-width:2px,color:#1a1a1a
classDef decision fill:#ffe8a3,stroke:#c77700,stroke-width:2px,color:#1a1a1a
classDef action   fill:#c5e4ff,stroke:#1864ab,stroke-width:2px,color:#1a1a1a
classDef dialog   fill:#ded0ff,stroke:#5f3dc4,stroke-width:2px,color:#1a1a1a
classDef reward   fill:#c6f6cd,stroke:#2b8a3e,stroke-width:2px,color:#1a1a1a
classDef page     fill:#f1f3f5,stroke:#495057,stroke-width:2px,color:#1a1a1a
```

3. **排版靠宣告順序**：主線先宣告一次寫完、例外分支放最後；回頭迴圈用 `-.->` 配 linkStyle 灰色（比對式用 `-\.?->` 才抓得到），**linkStyle 索引＝邊的宣告順序從 0 起算，每次改圖重數**；回頭迴圈不要接到起始節點的下一格（接再下一格，最上面三格才會垂直對齊）；起始節點不得有 incoming edge；禁巢狀 subgraph；共用終點兩分支長短差很多時寧可讓短分支自成終點；重排宣告順序不算簡化流程，但節點文字與邊標籤一字不改
4. **先渲染再交付且自己看過圖**：Windows 本機 `npx -y @mermaid-js/mermaid-cli -i flow.mmd -o flow.png`（已裝 Playwright 可建 pptr.json 指向 `%LOCALAPPDATA%\ms-playwright\chromium-*\chrome-win*\chrome.exe`，目錄帶版本號先 dir 再填，不可寫死）；claude.ai 容器用 mmdc＋`find /opt/pw-browsers -name chrome -type f` 帶 `--no-sandbox`；都不行就只寫 Notion 區塊由頁面渲染、交付訊息註明「未本機自檢，請在 Notion 看圖」。渲染後檢查：主線是否一路往下、起始節點位置、出口線清晰、虛線接對、標籤無重疊
5. **語意自檢（交付前必做）**：每個判斷節點的每條出口，都要在規則章找得到對應條號且意思一致；做法是跑 `scripts/plan_lint.py <網址>` 取節點清單逐條對（未回寫 Notion 時對自己的 mermaid 原始碼逐條對）。語法、配色、排版全對但分支邏輯錯（例：圖上「全部方案都買完才開放後續獎勵」，規則卻是每個方案購買後各自開放）是最常見的漏網之魚
6. **修改禮儀**：只執行明確指到的修改；**絕不主動合併節點或簡化流程**（曾被 revert）；改完重渲染。改 Notion 上既有的 mermaid 區塊用 PATCH 換該 block 的 `code.rich_text`，不刪掉重建（位置與 PM 設的顯示模式才保得住）；頁面上還是舊 PNG 的圖，使用者要改圖時改成區塊並把 PNG 下移一格當備份，刪不刪 PNG 問 PM
7. **圖內無法上色**：區塊裡的「後補」不會變紅（第八節第 3 條）——待填節點文字照常寫「後補」，並在區塊正下方加一行紅字「流程圖待補：節點 A 的 X、節點 B 的 Y」，PM 填完一起刪
8. 使用者說「線沒接到」→ 先回頭核對原始碼（常是排版讓它看起來斷了），先說明事實再修排版
