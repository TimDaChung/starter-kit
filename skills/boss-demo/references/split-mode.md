# 最終倍數拆解型（`mode: 'split'`）專屬規則

> 從 `SKILL.md` 拆出的拆解型專屬段落；模式判斷與對照表仍在 `SKILL.md`〈兩種 demo 模式〉。各節對應 SKILL.md 的步驟標在標題。

## 一、讀企劃要抽的三張表（步驟 1）

**最終倍數拆解型**抽三張表：

- **最終倍數權重表**：每個最終倍數與權重
- **結局判定表**：倍數區間 → 演到第幾關（例：10–59 演到第一關、60–199 演到第二關）
- **各段倍數的允許區間**：每一關（段）可以拿的倍數範圍與跳階（例：第二擊 10–80、每 5 一階）；各段的 phases 照下面的分段規則拆

## 二、預檢多查的項目（步驟 1.5）

**最終倍數拆解型多查：**

- 結局判定表的區間**有沒有斷層或重疊**：所有最終倍數都要剛好落進一個結局（例：59 跟 60 之間沒有洞、60 不能同時屬於兩關）
- 權重表的每個最終倍數，**用該結局會演的各段區間組不組得出**：各段最小值加總 ≤ 最終倍數 ≤ 各段最大值加總，且跳階對得上。組不出的列名單
- 期望值：Σ 最終倍數 × 機率，對照企劃寫的 EV／計算用賠率

## 三、CONFIG 寫法（步驟 4）

```js
  // split mode
  const CONFIG = { mode: 'split',
    finals:  [ { mult: 30, weight: 40 }, { mult: 120, weight: 8 } ],      // final multiplier weight table
    endings: [ { id: 'e1', name: '第一關結束', min: 10, max: 59,  stages: ['s1'] },
               { id: 'e2', name: '第二關結束', min: 60, max: 199, stages: ['s1', 's2'] } ], // range -> how far it plays
    stages:  { s1: { name: '第一擊', min: 2,  max: 20, step: 1, phases: [ { name, duration_ms } ] },
               s2: { name: '第二擊', min: 10, max: 80, step: 5, phases: [ /* ... */ ] } } }; // allowed range per stage
```

## 四、最終倍數拆解規則與 `splitMultiplier` 範例（步驟 4）

- **最終倍數拆解（拆解型）**：各段**由大到小**分配（允許上限大的段先拿），每段在「自己的區間 ∩ 剩下的段還補得起的範圍」內**有限隨機**，最小的段吸收剩餘；重試幾次仍組不出時，各段取最小值、**末項吸收差值**，倍數加總仍精準等於最終倍數，並在狀態列警示「組不出：末項超出區間」、計入模擬報告。最小範例：
  ```js
  // stages: this ending's stages in play order, each { min, max, step }
  function splitMultiplier(total, stages, rng = Math.random, tries = 30) {
    const order = stages.map((s, i) => i).sort((a, b) => stages[b].max - stages[a].max);
    for (let t = 0; t < tries; t++) {
      const parts = new Array(stages.length);
      let left = total, ok = true;
      for (let k = 0; k < order.length - 1; k++) {
        const s = stages[order[k]], rest = order.slice(k + 1).map(i => stages[i]);
        const restMin = rest.reduce((a, r) => a + r.min, 0);
        const restMax = rest.reduce((a, r) => a + r.max, 0);
        const step = s.step || 1;
        const lo = Math.ceil(Math.max(s.min, left - restMax) / step) * step;
        const hi = Math.floor(Math.min(s.max, left - restMin) / step) * step;
        if (lo > hi) { ok = false; break; }
        parts[order[k]] = lo + step * Math.floor(rng() * ((hi - lo) / step + 1)); // bounded random
        left -= parts[order[k]];
      }
      const last = stages[order[order.length - 1]];
      if (ok && left >= last.min && left <= last.max && left % (last.step || 1) === 0) {
        parts[order[order.length - 1]] = left;
        return { parts, ok: true };
      }
    }
    // cannot be composed: every stage takes its min, the smallest stage absorbs the rest
    const parts = stages.map(s => s.min), absorb = order[order.length - 1];
    parts[absorb] = total - parts.reduce((a, v, i) => (i === absorb ? a : a + v), 0);
    return { parts, ok: false }; // caller warns in the status bar and counts it in the simulation
  }
  ```
  （kit 以 node 跑 1 萬次驗過：加總恆等於最終倍數、組得出時各段都在區間與跳階內）

## 五、Debug 面板的拆解型專屬項（步驟 4）

  - **拆解型另有**：最終倍數權重表、結局判定表、各段區間都可調；每個結局一顆「強制播」；**「指定最終倍數播放」**輸入框＋按鈕——可輸入表外的值，專門測區間邊界（59／60、各段最小值加總、組不出的值）

## 六、模擬報告的拆解型專屬項（步驟 4）

  - **拆解型的模擬報告多兩項**：**組不出率**（總計＋各最終倍數，> 0 就標紅並列出是哪幾個值）、**各結局表演長度最短／最長**（同一結局各段倍數不同時，跳數、噴金幣量等隨倍數變動的分段秒數也會變，報最短與最長讓企劃看節奏上下限）
