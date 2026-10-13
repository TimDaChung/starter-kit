# 提案簡報（Step 10：使用者要做 Boss 提案簡報時）

> 從 `SKILL.md` Step 10 拆出。

簡報固定 10 頁架構，素材從規格（企劃／mini 企劃）與定稿圖來：

1. 封面（Boss 名、定稿主視覺）
2. 簡介＋特色（一句話宣傳、賣點）
3. 造型（各階段定稿，透明版用 `fit_canvas.py --transparent`）
4. 核心機制
5. 流程圖
6. 畫面配置
7. 技能（Step 9.5 的 cut-in，招式名在簡報裡疊字）
8. 關卡主題（背景，`boss-scene`）
9. 結算
10. 附錄

- 目前**沒有自動產 pptx 的腳本**，架構照上面手做或交給 pptx skill；自動產的腳本待組員提供去識別化版本後評估
- ⚠️ 用 pptxgenjs 產時：**菱形（diamond）不能帶 `rectRadius`**——schema 驗證會過，PowerPoint 卻打不開整份檔。圓角只給矩形用（組員回報，2026-10）
