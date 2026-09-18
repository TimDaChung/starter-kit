# Draw Engine

Shared engine rules for the five image-generation skills in this kit: `imagen`, `imagen-portrait`, `imagen-ui`, `generate2dsprite`, `generate2dmap`. Cite as「draw-engines.md §N」.

| § | Section | Read when |
|---|---------|-----------|
| 1 | The only engine | once per task, before generating anything |
| 2 | Generation rules | every batch |
| 3 | Call contract | writing the command |
| 4 | Failure handling | a batch did not fully succeed |
| 5 | Why there is no second engine | someone proposes adding a fallback |

---

## 1. The only engine

**GPT line — the `image-studio` skill**: `~/.claude/skills/image-studio/scripts/image-studio-client.py`, one `POST /draw` per call. Distributed separately by the team lead, never bundled in this kit (its credentials are personal). Every kit user is expected to have it.

Usable only when that skill directory exists AND `~/.config/image-studio/credentials.json` is present with `expiresAt` in the future.

**There is no fallback line.** If the GPT line is missing or its credentials expired, image generation **stops**: tell the user that the five image skills cannot run until the installer and credentials are obtained from the team lead, and do not attempt any other generation route. Everything else in the host skill (prompt writing, postprocess scripts, QC, style bible) still works on images the user already has.

## 2. Generation rules

1. **Default count: 1** — every generation run produces a single image, unless the user explicitly states a count（「畫 4 張」「來 3 個版本」）. Never generate extra candidates or variants on your own initiative.
2. Check engine availability **once per task**, before prompt work. Unavailable → stop and report per §1; never silently degrade.
3. `docs/STYLE_BIBLE.md` may carry an `engine` field from older projects. New bibles record `gpt`; a bible that still says `gemini` is a historical record — regenerate on the GPT line and update the field, matching the old batch by prompt and reference instead.

## 3. Call contract

```sh
python ~/.claude/skills/image-studio/scripts/image-studio-client.py draw \
  --count <1..10> --prompt '<final English prompt>' \
  [--reference <img>]... [--remove-background] [--output <dir>]
```

- The client has **no** `--ratio` / `--size` flags: write aspect-ratio and resolution requirements into the prompt text.
- AI-generated image as `--reference` → apply consistency-rules.md §5 (gen-0 only, moderate downscale, role-split prompt) — GPT compounds reference micro-noise fast.
- **Transparency**: `--remove-background` gives a transparent PNG directly. Sheets that need per-frame cutting still go through the host skill's magenta chroma-key and slicing scripts as documented there.
- Exactly one POST per batch; never auto-retry (a repeated POST may create a duplicate job). Default timeout 1800 s. Use `--output` to target the host skill's asset directory; filenames are client-generated (`image-studio-tab-*.png`) — rename to the host skill's naming convention after saving.

## 4. Failure handling

- **Batch verdict**: a batch of N counts as failed ONLY when **0** images were saved. Exit code 1 with a non-empty `files` list = partial success → report how many were saved vs. requested and **ask the user** whether to top up the missing count. Never re-request on your own — a repeated shortfall could loop forever.
- **Full batch failure (0 saved)** → STOP. Diagnose the cause from the client's stderr / response JSON and report it with a recommendation. There is no engine to fall back to, so every route below stays on the GPT line:

  | Diagnosed cause | Report + recommend |
  |---|---|
  | Content filter / copyright / prompt problem (policy rejection, filtered results, named IP or real person in the prompt) | Say which prompt element likely triggered it and propose a revised prompt; ask before regenerating |
  | Quota / usage exhausted (e.g. HTTP 429 or a quota message) | Report that the quota is out and generation must wait or the team lead must raise it — do not look for another generator |
  | HTTP 401 | Quarterly credentials expired → ask the team lead for the new setup; generation is blocked until then |
  | Unknown / other (timeout, 5xx, connection loss) | Ask whether to retry once on the GPT line. For connection loss, first check the user's Image Studio web tabs before any resubmit — accepted work may still be running and a repeated POST creates a duplicate job |

## 5. Why there is no second engine

This kit used to carry a Gemini (Nano Banana Pro) line via `imagen/bin/generate.py` with a personal `GEMINI_API_KEY`. **It was removed in v2.6.0 after a colleague's key was stolen**: that API is metered per request with no spending cap, so a leaked key is an open-ended bill. Every trace of it — the wrapper, `.env`, the key checks — is gone on purpose.

**Do not reintroduce a per-request-billed image API, and do not restore `generate.py` from git history**, even when the GPT line is down and the user is in a hurry. If a second engine is ever wanted, it needs a hard spending cap and a team-lead decision first — raise it, don't implement it.
