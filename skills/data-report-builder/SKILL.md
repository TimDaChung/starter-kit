---
name: data-report-builder
description: 產生「定期分析某個報表 / 後台 / 指標」的專屬 skill。一輪訪談問清資料來源、指標定義、比較基準、異常門檻、產出格式,然後在 ~/.claude/skills/report-<slug>/ 生成可直接用的分析 skill(含指標字典、報告模板、選配 Python 載入腳本),試跑一次確認。觸發詞:「幫我做一個分析 XX 的 skill」「我要定期看 XX 報表」「建一個 XX 指標的分析」「報表 skill」「data report builder」。
---

# Data Report Builder

> **執行角色：企劃**——關注指標定義是否可驗證、比較基準是否公平、結論是否能導出行動；統計方法依 `templates/report-skill.template.md` 的「統計規範」小節。生成的 skill 跑起來時切**數值 / QA** 視角查資料品質。

這是一支 **meta skill**:它不分析資料,它產生「會分析某份特定報表」的 skill。每份報表一支,名稱 `report-<slug>`,放在 `~/.claude/skills/`,屬於使用者自有資產,不進任何 kit。

## 核心原則

- **指標定義不猜**:分子、分母、時間窗、排除條件全部問到,問不到就標「暫定」寫進指標字典
- **比較基準先定**:沒有基準的數字不是分析。至少一種:前期 / 去年同期 / 目標值 / 對照組
- **結論要能行動**:每個發現後面接「所以建議…」或「需要再查…」,沒有就不寫
- **憑證不進 skill**:後台帳密、API key 一律走環境變數或 `.env`(gitignore),SKILL.md 只寫變數名
- **生成的 skill 也遵守 meta 規則**:分析被糾正的事寫回該 skill 的 SKILL.md

## 流程

### 1. 一輪訪談(所有問題一次列出,不擠牙膏)

用 AskUserQuestion 或條列一次問完,使用者說「先假設」的自行補上並標「暫定」:

| 面向 | 要問到 |
|---|---|
| **報表身分** | 名稱、是哪個產品 / 系統的、誰在看 |
| **資料來源** | 類型:CSV / Excel 匯出、Google Sheets、SQL、API、後台網頁(截圖或 Chrome 代操作);存取方式與憑證放哪 |
| **資料形狀** | 欄位清單、一列代表什麼(一天 / 一個玩家 / 一筆訂單)、時間欄位、更新頻率 |
| **關鍵指標** | 每個指標的公式(分子 / 分母 / 時間窗 / 排除條件)、單位、正常範圍 |
| **比較基準** | 前期、同期、目標、對照組,哪幾種 |
| **異常門檻** | 什麼變化幅度算「要提醒」(例:D1 留存掉 3 個百分點) |
| **分群** | 常看的切法:平台 / 地區 / 渠道 / 版本 / 付費層級 |
| **產出** | 讀者是誰、要多長、要不要圖、要不要進 Notion、口令叫什麼 |
| **週期** | 每天 / 每週 / 每月 / 手動;要不要排程 |

### 2. 生成 skill

在 `~/.claude/skills/report-<slug>/` 建立:

```
report-<slug>/
├── SKILL.md              # 依 templates/report-skill.template.md 填
├── references/
│   └── metrics.md        # 指標字典:名稱 / 公式 / 單位 / 正常範圍 / 異常門檻 / 備註
├── templates/
│   └── report.md         # 報告模板(Notion-ready Markdown)
├── scripts/              # 選配:資料來源是檔案或 SQL 時才建
│   └── load.py           # 載入 + 清洗 + 基本驗證;完整 type hints;pytest 測試
├── state/
│   └── last_run.md       # 上次分析的日期 / 關鍵數值 / 留給下期的觀察(首次由 skill 建立)
└── .env.example          # 有憑證時才建;列變數名,不放值
```

SKILL.md 必含:
- frontmatter `name` / `description`(description 含使用者指定的口令)
- 執行角色標頭(企劃;資料品質檢查切數值 / QA)
- **資料取得**:一步一步,含失敗時怎麼辦
- **分析 checklist**:總覽 → 趨勢 → 基準比較 → 分群 → 異常 → 結論與行動
- **統計規範**:照 `templates/report-skill.template.md` 的「統計規範」小節原樣帶入(四條規則寫在那裡,不在此重複)
- **產出格式**:指向 templates/report.md
- **異常門檻**:指向 references/metrics.md
- **被糾正寫回**:本 skill 的 meta 規則

### 3. 試跑一次

- 有資料就用最近一期真資料跑完整流程;沒有就用使用者給的樣本或自造 10 列假資料跑到報告模板
- 對照 checklist 逐項確認有產出
- 圖表確認中文字型沒變方塊
- 把試跑時使用者糾正的事寫回生成的 SKILL.md

### 4. 排程建議(使用者要定期跑才給)

| 需求 | 建議 |
|---|---|
| 開著 Claude Code 時定時跑 | `/loop <間隔> <口令>` |
| 不開電腦也要跑 | `/schedule` 建 cloud routine(需資料來源可從雲端存取) |
| 不確定 | 先手動跑兩週,確定報告格式穩了再排程 |

### 5. 收尾

```
✅ 生成:~/.claude/skills/report-<slug>/(SKILL.md、metrics.md、report.md[、load.py、.env.example])
🧪 試跑:用 <日期> 資料跑過,checklist N/N 項有產出
🔑 憑證:<變數名> 請填入 .env(未填前只能用匯出檔)
🗣️ 口令:「<使用者指定口令>」
📅 排程:<建議或「先手動」>
📝 暫定項:<標「暫定」的指標定義,請使用者確認>
```

## 生成的 skill 品質標準

- 第一次跑就能出報告,不需要再問使用者任何定義問題
- 報告第一段是結論與建議行動,數字放表格,不放進句子
- 每個異常都附「跟什麼比、差多少、可能原因、建議動作」四項
- 分群比較先看樣本量,小於 30 的群標「樣本不足」不下結論

## 資源

- `templates/report-skill.template.md`:生成 SKILL.md 用的模板
- `templates/metrics.template.md`:指標字典模板
- `templates/report.template.md`:報告模板

## 銜接

- 企劃書要附成功指標 → `product-planning` 寫企劃時可呼叫本 skill 定義指標
- 數值模擬(非真實數據)→ 派 `game-balance-auditor`
- 報表在後台網頁只能看不能匯出 → 用 Chrome DevTools MCP 代操作抓數字,生成的 skill 寫明抓哪幾個元素
