---
name: art-style-guard
description: 遊戲美術風格一致性守門。Use when 遊戲/demo 專案批次生圖後要併入既有素材、使用者說「風格不一致」「跟之前的不像」「重畫」、或同一專案第二批以後的任何生圖任務開始前。
---

# art-style-guard

## 核心原則

**新素材給使用者看之前，先跟既有素材並排自檢過。** 使用者的時間只花在「挑過關候選」，不花在「抓風格不一致」。

## Style Bible（每專案一份）

首批素材被使用者核准後，立刻在專案 `docs/STYLE_BIBLE.md` 落地：

- 畫風關鍵詞（含使用者的原話定義，例：「留白＝筆觸之間的小空隙，不是白色」）
- 色板（hex）、線條粗細、上色法、光源方向
- 3–5 張核准素材路徑當黃金樣本
- 禁忌清單（被打回過的方向逐條記錄）

之後每批生圖 prompt **從 bible 組裝**，不憑記憶重寫風格詞。使用者口頭糾正風格 → 當場更新 bible。

## 每批生圖後的 QC 流程

1. 拼 contact sheet（新素材 vs 黃金樣本並排）：
   ```python
   from PIL import Image
   imgs = [Image.open(p).resize((256, 256)) for p in paths]  # golden first, then new
   sheet = Image.new("RGB", (256 * len(imgs), 256), "white")
   for i, im in enumerate(imgs): sheet.paste(im, (256 * i, 0))
   sheet.save(out_path)
   ```
2. Read contact sheet，逐項自檢：線條粗細一致？上色法同款？飽和度同區間？光源方向同側？輪廓複雜度同級？
3. 不合格 → 修 prompt 重生，**上限 2 輪**；仍不合格就把 contact sheet 連同差異分析給使用者拍板，不硬燒 quota。
4. 過關才回報，附 contact sheet 讓使用者一眼驗收。

## 委派判斷（subagent）

- 批次生圖（>3 張）→ 派背景 agent 跑 `~/.claude/skills/imagen/bin/generate.py`，prompt 由本終端從 bible 組好塞進 agent prompt。
- Contact sheet 判讀＝本終端親自 Read 看圖，不委派（風格判斷是主觀瓶頸，agent 回報文字會失真）。
- 多角色/多批並行 → 每 agent 只寫自己的輸出資料夾，不重疊。

## 常見錯誤

| 錯誤 | 後果／修法 |
|---|---|
| 只看單張新圖就交付 | 單張好看≠融入整體。一律並排黃金樣本看 |
| 風格詞每批口頭重講 | 版本漂移。從 STYLE_BIBLE.md 組裝 |
| 使用者糾正只改當批 prompt | 下批又犯。同步寫進 bible 禁忌清單 |
| 無上限自動重生 | 燒 quota 燒時間。2 輪不過就升級給使用者 |
| 首批就跑 QC 流程 | 沒有黃金樣本可比。首批＝定調批，直接給使用者挑 |
