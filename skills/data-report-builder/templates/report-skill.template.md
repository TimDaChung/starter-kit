---
name: report-{{slug}}
description: 定期分析「{{report_name}}」（{{product}}）。資料來源：{{source_type}}。指標：{{metric_list}}。觸發詞：「{{trigger_phrases}}」。
---

# {{report_name}} 分析

> **執行角色：企劃**——關注指標變化能否導出行動；資料載入與品質檢查切**數值 / QA** 視角。統計方法見下方「統計規範」。

讀者：{{audience}}。週期：{{cadence}}。上次分析：見 `state/last_run.md`（沒有就是第一次）。

## 1. 資料取得

{{data_access_steps}}

失敗時：{{failure_fallback}}

憑證：{{credential_vars}}（放 `.env`，不寫進本檔）

## 2. 資料品質檢查（數值 / QA 視角）

- 列數與上期比，差超過 {{row_count_tolerance}} 先問是不是資料不完整
- 時間欄位連續、無重複日期
- 關鍵指標欄位無空值；有空值列出比例
- 分群欄位的類別跟 `references/metrics.md` 列的一致，出現新類別要提示

## 3. 分析 checklist（依序，每項都要有產出）

1. **總覽**：本期各指標數值，表格
2. **趨勢**：近 {{trend_window}} 走勢，plotnine 折線（字型設定見「統計規範」）
3. **基準比較**：{{comparison_bases}}；差異同時給絕對值與百分比
4. **分群**：{{segments}}；樣本量 < 30 的群標「樣本不足」不下結論
5. **異常**：對照 `references/metrics.md` 門檻；每個異常附「跟什麼比 / 差多少 / 可能原因 / 建議動作」
6. **結論與行動**：三條以內，每條接「所以建議…」或「需要再查…」

### 統計規範

- 視覺化優先 plotnine（ggplot 風格）
- 圖表含中文時先設 `plt.rcParams["font.family"] = "Microsoft JhengHei"`
- 統計檢定（分群比較、A/B）前先查常態性 / 同質變異 / 獨立性，不直接套公式
- 結果同時給 effect size + p-value，不只看顯著性
- Python 依專案規範：4 空格、type hints、f-string、pytest

## 4. 產出

依 `templates/report.md` 填，Notion-ready Markdown。第一段是結論，數字進表格。
產出後更新 `state/last_run.md`（日期、本期關鍵數值、留給下期的觀察）。

## 5. 被糾正寫回

分析方式、指標定義、報告格式被使用者糾正時，把具體規則（含當時案例一句話）寫回本檔對應段落或 `references/metrics.md`。
