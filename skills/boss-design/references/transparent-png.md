# 灰底定稿轉透明 PNG（`fit_canvas.py --transparent`）

> 從 `SKILL.md` Step 5 拆出。驗收項見 `../boss設計法則.md` 第六節〈透明 PNG〉。

**要透明 PNG 時**（demo、簡報、cut-in 疊圖要單獨的 Boss）：同一張灰底定稿再跑一次 `--transparent`，交付時灰底版與透明版都給：

```sh
python ~/.claude/skills/boss-design/scripts/fit_canvas.py <定稿.png> <輸出_透明.png> --transparent [--margin 16]
```

- 取四角平均灰 → 色差轉 alpha（`--key-low` 以下全透明、`--key-high` 以上全不透明，預設 10／40）→ 內縮 1px＋輕微模糊（`--feather`，預設 1）→ 邊緣去灰 → 裁到主體外框（`--margin` 留邊距）。不縮放、不補 16:9
- **疊在深色與淺色底上各看一次再交**：主體有接近底灰的顏色（灰甲、灰白煙霧）會被挖空，中性灰的落地陰影會留成一塊灰。挖空時把 `--key-low` 調低；灰邊太多時把 `--key-high` 調低或 `--feather` 調小
- 這是「灰底轉透明」，跟 boss-demo 步驟 2 的 magenta 去背是兩條管線：已經有灰底定稿就用這支，不必為了去背重算一張 magenta 底
