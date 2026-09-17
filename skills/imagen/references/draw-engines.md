# Draw Engine Routing

Shared engine-selection rules for the five image-generation skills in this kit: `imagen`, `imagen-portrait`, `imagen-ui`, `generate2dsprite`, `generate2dmap`. Cite as「draw-engines.md §N」.

| § | Section | Read when |
|---|---------|-----------|
| 1 | Engines | once per task, before generating anything |
| 2 | Routing & engine lock | picking the line for this task/batch |
| 3 | GPT line call contract | the GPT line was picked |
| 4 | Failure handling | a GPT-line batch did not fully succeed |

---

## 1. Engines

- **GPT line (preferred)** — the `image-studio` skill: `~/.claude/skills/image-studio/scripts/image-studio-client.py`, one `POST /draw` per call. **Distributed separately by the team lead, never bundled in this kit** (its credentials are personal). Every kit user is expected to have it. Usable only when that skill directory exists AND `~/.config/image-studio/credentials.json` is present with `expiresAt` in the future — if missing or expired, tell the user once that the GPT line is unavailable (installer/credentials come from the team lead; expired quarterly keys refresh from the Image Studio `/agent-api` page), then proceed on the Gemini line.
- **Gemini line (fallback)** — `~/.claude/skills/imagen/bin/generate.py` (Nano Banana Pro), exactly as each SKILL.md already documents it, including API/Prompt mode determination (common.md §9) and any postprocess scripts.

## 2. Routing & engine lock

1. Determine availability **once per task**, before common.md §9 mode determination. GPT line available → use it for **every** style and asset type (mihoyo/arknights cel-shaded included). Unavailable → Gemini line. Either way, state which line was used when reporting results.
2. **Engine lock across batches**: the project's `docs/STYLE_BIBLE.md` records an `engine` field (`gpt` / `gemini`, set when the first approved batch lands). Second batch onward in the same project uses the bible's engine, even if the other line is available. A user-approved line switch updates the field.
3. **Default count: 1** — every generation run produces a single image on either line, unless the user explicitly states a count（「畫 4 張」「來 3 個版本」）. Never generate extra candidates or variants on your own initiative.
4. **Never mix engines within one batch** — a batch's images must all come from the same line.

## 3. GPT line call contract

```sh
python ~/.claude/skills/image-studio/scripts/image-studio-client.py draw \
  --count <1..10> --prompt '<final English prompt>' \
  [--reference <img>]... [--remove-background] [--output <dir>]
```

- The client has **no** `--ratio` / `--size` flags: write aspect-ratio and resolution requirements into the prompt text.
- Reuse the confirmed final English prompt from the host skill. Keep boilerplates per-engine — do not port Gemini-specific technical blocks (e.g. `generate.py` flag values) into GPT prompts.
- **Transparency**: use `--remove-background` for direct transparent PNG output (on the Gemini line, transparency stays chroma-key postprocess as before). Sheet slicing and other postprocess steps still apply to GPT output where the host skill uses them.
- Exactly one POST per batch; never auto-retry (a repeated POST may create a duplicate job). Default timeout 1800 s. Use `--output` to target the host skill's asset directory; filenames are client-generated (`image-studio-tab-*.png`) — rename to the host skill's naming convention after saving.

## 4. Failure handling (the user decides fallback)

- **Batch verdict**: a batch of N counts as failed ONLY when **0** images were saved. Exit code 1 with a non-empty `files` list = partial success → report how many were saved vs. requested and **ask the user** whether to top up the missing count (still on the GPT line). Never re-request on your own — a repeated shortfall could loop forever.
- **Full batch failure (0 saved)** → STOP. Diagnose the cause from the client's stderr / response JSON, then report it **with a recommendation and a concrete question** — the user always decides, never fall back automatically:

  | Diagnosed cause | Report + recommend |
  |---|---|
  | Content filter / copyright / prompt problem (policy rejection, filtered results, named IP or real person in the prompt) | Say which prompt element likely triggered it and propose a revised prompt — switching engines rarely helps here; offer the prompt fix first |
  | Quota / usage exhausted (e.g. HTTP 429 or a quota message) | Ask directly: "GPT 用量用完了，這批要不要換 Gemini 線試試？" |
  | HTTP 401 | Quarterly key expired → refresh from the Image Studio `/agent-api` page (Gemini as the stopgap if the user wants the batch now) |
  | Unknown / other (timeout, 5xx, connection loss) | Ask: "要在 GPT 線重跑一次，還是換 Gemini 線試試？" For connection loss, first check the user's Image Studio web tabs before any resubmit — accepted work may still be running and a repeated POST creates a duplicate job |
- User approves the switch → regenerate the **whole batch** on the Gemini line, and record/update the bible's `engine` field accordingly.
