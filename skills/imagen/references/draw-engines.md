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

- **GPT line (preferred)** — the personal `image-studio` skill: `~/.claude/skills/image-studio/scripts/image-studio-client.py`, one `POST /draw` per call. **Not part of this kit.** Available only when that skill directory exists AND `~/.config/image-studio/credentials.json` is present with `expiresAt` in the future. If unavailable, skip this file entirely — the host SKILL.md's existing Gemini flow applies unchanged.
- **Gemini line (fallback)** — `~/.claude/skills/imagen/bin/generate.py` (Nano Banana Pro), exactly as each SKILL.md already documents it, including API/Prompt mode determination (common.md §9) and any postprocess scripts.

## 2. Routing & engine lock

1. Determine availability **once per task**, before common.md §9 mode determination. GPT line available → use it for **every** style and asset type (mihoyo/arknights cel-shaded included). Unavailable → Gemini line. Either way, state which line was used when reporting results.
2. **Engine lock across batches**: the project's `docs/STYLE_BIBLE.md` records an `engine` field (`gpt` / `gemini`, set when the first approved batch lands). Second batch onward in the same project uses the bible's engine, even if the other line is available. A user-approved line switch updates the field.
3. **Never mix engines within one batch** — a batch's images must all come from the same line.

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

- **Batch verdict**: a batch of N counts as failed ONLY when **0** images were saved. Exit code 1 with a non-empty `files` list = partial success → stay on the GPT line and re-request just the missing count.
- **Full batch failure (0 saved)** → STOP. Report the cause to the user first (HTTP status / timeout / content filter; HTTP 401 = quarterly key expired → refresh from the Image Studio `/agent-api` page). **The user decides** whether to rerun on the Gemini line — never fall back automatically.
- User approves the switch → regenerate the **whole batch** on the Gemini line, and record/update the bible's `engine` field accordingly.
