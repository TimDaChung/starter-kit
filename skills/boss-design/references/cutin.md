# Step 9.5 — 絕招／技能 cut-in 特寫（選做）

> 從 `SKILL.md` 拆出。提示詞模板見 `../prompt模板.md` 第三節；驗收項見 `../boss設計法則.md` 第六節〈cut-in 特寫〉。

企劃或提案簡報需要「放絕招時的角色特寫」才做；沒要就跳過。**外觀定稿後才做**，每招一張。

1. 照 `prompt模板.md` 第三節組提示詞：**共用前言一段＋每招一段描述**，每招存一個檔 `_工作暫存/prompt_<Boss名>_cutin_<招名>.txt`
2. 算圖：外觀定稿當 `--reference`，每招 `--count 2`，**不加 `--remove-background`**

   ```sh
   python3 ~/.claude/skills/image-studio/scripts/image-studio-client.py draw      --count 2 --prompt-file <prompt_cutin_招名.txt> --output <_工作暫存/Boss名/cutin> --reference <外觀定稿.png>
   ```

   招數多時先照 kit `references/image-studio-共用須知.md` 第零節算總張數（4 招 × 2 張＝8 張）
3. 規則：
   - **16:9，角色佔畫面左側約六成，右側留白給標題字**
   - **圖上不畫任何文字**：招式名、標題一律在簡報或引擎裡疊字。AI 寫中文常錯字、缺筆，畫進圖裡就整張重來
   - 造型與配色以定稿為準，只改表情、姿勢、特效；畫風一致
4. 挑圖：右側有沒有留白、有沒有冒出文字或假字、造型有沒有跑掉（多了或少了部件）——有字或右側被佔滿就重抽

> 未實測：組員回報 4 招各算 2 張，都一次成功（2026-10）。第一次正式用時把結果回寫 `boss設計法則.md` 第七節。
