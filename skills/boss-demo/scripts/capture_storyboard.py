"""Turn a finished boss-demo into plan storyboards: capture every candidate frame, then keep the distinct ones.

Two steps, so frames can be reviewed before the sheet is made:

  capture   force-play each scenario, pause every phase at each --at point,
            screenshot the #stage element, save candidates + candidates.json.
  compose   keep the frames that differ visibly (any number), stitch them with
            "圖N  <what happens>" tags and write a Markdown skeleton for the plan.

There is no fixed frame count. Drop candidates that look nearly the same as a
kept neighbour or show no visible change; keep every distinct beat. compose
always writes 候選_<name>.png, a numbered contact sheet of every candidate, to
pick from with --pick. Without --pick an automatic dedupe (drop frames whose
mean pixel difference from the previous kept frame is below --min-diff) gives a
starting point only.

Tags on the sheet carry what the frame shows (--captions), not seconds: the
seconds live in the plan text and in the demo. The Markdown skeleton follows
動態描述規範.md (one numbered step per storyboard, seconds at the end of the
line, 〔圖N〕 pointing at the sheet, then placeholders for the rules the spec
asks for: stage variants, sync points, layers, collision/countdown). In ratios
mode each step's seconds = total duration of the phases it stands for (from its
phase up to the next kept frame's phase), which adds up to the demo total.

The demo must expose the capture contract (see SKILL.md, 「分鏡擷取介面」):
    window.DEMO_API = { scenarios: [{id, name}], play(id) -> Promise, pause(), resume() }
    window.dispatchEvent(new CustomEvent('demo:phase', {detail: {name, ms}}))  // at each phase start
Older demos can be driven with --shim <js> (injected after load). Elements with
class "demo-ui" are hidden while capturing; --hide adds more selectors.

Usage:
    python capture_storyboard.py capture <demo_dir> <out_dir> [--scenarios 0,1] [--at 0.35,0.75]
                                 [--shim shim.js] [--hide "#btnrow"] [--skip-phases 轉場]
    python capture_storyboard.py compose <out_dir> --scenario 0 [--pick 1,3,5,6] [--captions "a|b|c|d"]

The demo directory is served over a local HTTP server (file:// breaks on
non-ASCII paths and blocks some assets).
"""
import argparse
import functools
import http.server
import json
import re
import pathlib
import threading

from PIL import Image, ImageChops, ImageDraw, ImageFont, ImageStat

FONT_CANDIDATES = [
    "C:/Windows/Fonts/msjhbd.ttc",
    "C:/Windows/Fonts/msjh.ttc",
    "/System/Library/Fonts/PingFang.ttc",
    "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc",
]

# Records every phase, and stops for a screenshot either at each demo:beat (the
# demo author marks key moments) or, for demos without beats, at fixed ratios of
# each phase. Page timers keep running while the demo is paused, so the next
# ratio stop is only scheduled after Python resumes, and paused time is
# subtracted from beat offsets.
HOOK_JS = """
({ ratios, useBeats }) => {
  const cap = window.__cap = { ready: false, shot: null, phases: [], pending: null,
                              phaseStart: 0, pausedAt: 0, pausedTotal: 0 };
  const offset = () => performance.now() - cap.phaseStart - cap.pausedTotal;
  const stop = (extra) => {
    window.DEMO_API.pause();
    cap.pausedAt = performance.now();
    const ph = cap.phases[cap.phases.length - 1];
    cap.shot = { phase: cap.phases.length - 1, name: ph.name, ms: ph.ms, offset: offset(), ...extra };
    requestAnimationFrame(() => requestAnimationFrame(() => { cap.ready = true; }));
  };
  const stopAt = (phaseIdx, k) => {
    const ms = cap.phases[phaseIdx].ms;
    cap.pending = setTimeout(() => {
      if (cap.phases.length - 1 !== phaseIdx) return;
      stop({ k });
    }, ms * (ratios[k] - (k ? ratios[k - 1] : 0)));
  };
  cap.next = () => {
    const s = cap.shot;
    cap.ready = false;
    cap.pausedTotal += performance.now() - cap.pausedAt;
    window.DEMO_API.resume();
    if (!useBeats && s.k + 1 < ratios.length) stopAt(s.phase, s.k + 1);
  };
  window.addEventListener('demo:phase', (e) => {
    clearTimeout(cap.pending);
    cap.phases.push({ name: e.detail.name, ms: e.detail.ms });
    cap.phaseStart = performance.now();
    cap.pausedTotal = 0;
    if (!useBeats) stopAt(cap.phases.length - 1, 0);
  });
  if (useBeats) window.addEventListener('demo:beat', (e) => stop({ caption: e.detail.caption }));
}
"""


def quiet_handler(directory: pathlib.Path) -> type:
    class Handler(http.server.SimpleHTTPRequestHandler):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, directory=str(directory), **kwargs)

        def log_message(self, *args) -> None:
            pass

    return Handler


def load_font(size: int) -> ImageFont.FreeTypeFont:
    for path in FONT_CANDIDATES:
        if pathlib.Path(path).exists():
            return ImageFont.truetype(path, size)
    raise SystemExit("no CJK font found; add one to FONT_CANDIDATES")


def seconds_text(ms: float) -> str:
    return f"{ms / 1000:.2f}".rstrip("0").rstrip(".") + "秒"


def figure_tag(numbers: list[int]) -> str:
    """〔圖3〕, 〔圖3–5〕 for a contiguous run, 〔圖3、5〕 otherwise; empty when no figure."""
    if not numbers:
        return ""
    if len(numbers) > 1 and numbers == list(range(numbers[0], numbers[-1] + 1)):
        return f"〔圖{numbers[0]}–{numbers[-1]}〕"
    return "〔圖" + "、".join(str(n) for n in numbers) + "〕"


# Rules 動態描述規範.md asks every performance section to state; the PM fills them in.
SPEC_PLACEHOLDERS = [
    "階段差異：〔待補：各階段各一套／全階共用一套〕",
    "同步點：〔待補：血條、彩金欄、獎圈、造型更換落在第幾個分鏡；沒有就刪〕",
    "圖層：〔待補：有疊在 Boss 上的特效才寫，例：Boss本體<特效<飛入物件；沒有就刪〕",
    "表演期間：〔待補：移除碰撞區／禁止發炮／禁用道具卡；倒數照常或暫停〕",
    "機制與數值詳見〔4.x〕",
]


Step = tuple[str, float, list[int], list[str], str]


def plan_section(name: str, total_ms: float, steps: list[Step], sheet_name: str) -> str:
    """Render a 3.3.x section in the 動態描述規範 layout.

    steps: (title, ms, figure numbers, sub-lines, note). A step with exactly one sub-line
    is written on one line; more sub-lines become children sharing the step's seconds.
    note, if any, goes on its own indented line (working info the PM deletes).
    """
    md = [f"### {name}（共 {seconds_text(total_ms)}）", "1. 觸發時機：〔待補〕", "2. 分鏡："]
    for n, (title, ms, figures, subs, note) in enumerate(steps, 1):
        head = f"分鏡{n}：{title}"
        if len(subs) == 1:
            head += f"——{subs[0]}"
        md.append(f"    {n}. {head}，{seconds_text(ms)}{figure_tag(figures)}")
        if len(subs) > 1:
            md.extend(f"        {k}. {sub}" for k, sub in enumerate(subs, 1))
        if note:
            md.append(f"        {note}")
    md.extend(f"{k}. {line}" for k, line in enumerate(SPEC_PLACEHOLDERS, 3))
    md.append(f"\n[右欄：{sheet_name}，caption《{name}分鏡示意圖》]\n")
    return "\n".join(md)


# ---------- capture ----------

def capture_scenario(page, scenario: dict, frames_dir: pathlib.Path, skip: list[str]) -> tuple[list[dict], list[dict]]:
    shots: list[dict] = []
    page.evaluate("id => { window.__cap.phases = []; window.__done = false;"
                  " window.DEMO_API.play(id).then(() => window.__done = true); }", scenario["id"])
    while True:
        page.wait_for_function("window.__cap.ready || window.__done", timeout=120_000)
        if page.evaluate("window.__done && !window.__cap.ready"):
            break
        shot = page.evaluate("window.__cap.shot")
        if not any(word in shot["name"] for word in skip):
            path = frames_dir / f"{scenario['id']}_{len(shots) + 1:02d}.png"
            page.locator("#stage").screenshot(path=str(path))
            shots.append({"n": len(shots) + 1, "phase": shot["phase"], "offset_ms": round(shot["offset"]),
                          "caption": shot.get("caption", ""), "file": path.name})
        page.evaluate("window.__cap.next()")
    return page.evaluate("window.__cap.phases"), shots


def cmd_capture(args: argparse.Namespace) -> None:
    from playwright.sync_api import sync_playwright

    demo_dir = pathlib.Path(args.demo_dir).resolve()
    out_dir = pathlib.Path(args.out_dir).resolve()
    frames_dir = out_dir / "frames"
    frames_dir.mkdir(parents=True, exist_ok=True)
    ratios = sorted(float(r) for r in args.at.split(","))
    skip = [w for w in args.skip_phases.split(",") if w]
    server = http.server.ThreadingHTTPServer(("127.0.0.1", 0), quiet_handler(demo_dir))
    threading.Thread(target=server.serve_forever, daemon=True).start()
    result: dict = {}
    try:
        with sync_playwright() as pw:
            browser = pw.chromium.launch()
            page = browser.new_page(viewport={"width": 1600, "height": 1000})
            page.goto(f"http://127.0.0.1:{server.server_address[1]}/{args.page}")
            if args.shim:
                page.add_script_tag(content=pathlib.Path(args.shim).read_text(encoding="utf-8"))
            page.wait_for_function("window.DEMO_API && window.DEMO_API.scenarios")
            hidden = ",".join([".demo-ui"] + [s for s in args.hide.split(",") if s])
            page.add_style_tag(content=f"{hidden} {{ visibility: hidden !important; }}")
            has_beats = page.evaluate("!!window.DEMO_API.beats")
            use_beats = args.mode == "beats" or (args.mode == "auto" and has_beats)
            if args.mode == "beats" and not has_beats:
                raise SystemExit("--mode beats but the demo does not declare DEMO_API.beats = true")
            print(f"mode: {'beats (demo-marked key frames)' if use_beats else 'ratios ' + args.at}")
            page.evaluate(HOOK_JS, {"ratios": ratios, "useBeats": use_beats})
            wanted = [s for s in args.scenarios.split(",") if s]
            for scenario in page.evaluate("window.DEMO_API.scenarios"):
                if wanted and scenario["id"] not in wanted:
                    continue
                phases, shots = capture_scenario(page, scenario, frames_dir, skip)
                result[scenario["id"]] = {"name": scenario["name"], "mode": "beats" if use_beats else "ratios",
                                          "phases": phases, "shots": shots}
                total = sum(p["ms"] for p in phases)
                print(f"[{scenario['id']}] {scenario['name']}: {len(phases)} phases, {len(shots)} candidates, total {seconds_text(total)}")
            browser.close()
    finally:
        server.shutdown()
    (out_dir / "candidates.json").write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"candidates in {frames_dir}; next: compose <out_dir> --scenario <id>")


# ---------- compose ----------

def difference(a: Image.Image, b: Image.Image) -> float:
    return sum(ImageStat.Stat(ImageChops.difference(a, b)).mean) / 3


def auto_dedupe(frames: list[Image.Image], min_diff: float) -> list[int]:
    small = [f.convert("RGB").resize((160, 90)) for f in frames]
    keep = [0]
    for i in range(1, len(frames)):
        if difference(small[keep[-1]], small[i]) >= min_diff:
            keep.append(i)
    return keep


def grid(n: int) -> tuple[int, int]:
    cols = n if n <= 3 else 2 if n == 4 else 3 if n <= 9 else 4
    return cols, -(-n // cols)


def contact_sheet(images: list[Image.Image], shots: list[dict], phases: list[dict], out: pathlib.Path) -> None:
    cols, cell_w = 4, 400
    cell_h = round(cell_w * images[0].height / images[0].width)
    label_h = 28
    rows = -(-len(images) // cols)
    sheet = Image.new("RGB", (cols * cell_w, rows * (cell_h + label_h)), (24, 24, 24))
    draw = ImageDraw.Draw(sheet)
    font = load_font(18)
    for i, (img, shot) in enumerate(zip(images, shots)):
        x, y = (i % cols) * cell_w, (i // cols) * (cell_h + label_h)
        sheet.paste(img.convert("RGB").resize((cell_w, cell_h), Image.LANCZOS), (x, y + label_h))
        draw.text((x + 6, y + 4), f"#{shot['n']}  {phases[shot['phase']]['name']}", font=font, fill=(255, 196, 0))
    sheet.save(out)


def cmd_compose(args: argparse.Namespace) -> None:
    out_dir = pathlib.Path(args.out_dir).resolve()
    data = json.loads((out_dir / "candidates.json").read_text(encoding="utf-8"))[args.scenario]
    shots, phases = data["shots"], data["phases"]
    images = [Image.open(out_dir / "frames" / s["file"]) for s in shots]
    contact = out_dir / f"候選_{data['name']}.png"
    contact_sheet(images, shots, phases, contact)
    beats = data.get("mode") == "beats"
    if args.pick:
        picked = [int(n) - 1 for n in args.pick.split(",")]
    else:
        picked = list(range(len(shots))) if beats else auto_dedupe(images, args.min_diff)
    if args.captions:
        captions = [c.strip() for c in args.captions.split("|")]
    else:
        captions = [shots[i]["caption"] for i in picked] if beats else []
    if captions and len(captions) != len(picked):
        raise SystemExit(f"--captions has {len(captions)} entries, {len(picked)} frames picked")

    # seconds: a kept frame covers its own phase (shared evenly with other kept frames in the
    # same phase) plus every later phase up to the next kept frame's phase; phases before the
    # first kept frame go to the first one, so the total always equals the demo's
    starts = [shots[i]["phase"] for i in picked]
    per_phase = {p: starts.count(p) for p in set(starts)}
    spans = []
    for j, start in enumerate(starts):
        is_last_in_phase = j + 1 == len(starts) or starts[j + 1] != start
        end = (starts[j + 1] if j + 1 < len(starts) else len(phases)) if is_last_in_phase else start + 1
        ms = phases[start]["ms"] / per_phase[start] + sum(p["ms"] for p in phases[start + 1:end])
        first = 0 if j == 0 else start
        if j == 0:
            ms += sum(p["ms"] for p in phases[:start])
        spans.append((first, max(end, start + 1), ms))

    cols, rows = grid(len(picked))
    cell_w = args.cell_width
    cell_h = round(cell_w * images[0].height / images[0].width)
    gap = round(cell_w * 0.02)
    sheet = Image.new("RGB", (cols * cell_w + (cols + 1) * gap, rows * cell_h + (rows + 1) * gap), (24, 24, 24))
    draw = ImageDraw.Draw(sheet)
    font = load_font(round(cell_h * 0.06))
    pad = round(cell_h * 0.025)
    for j, i in enumerate(picked):
        row, col = divmod(j, cols)
        x, y = gap + col * (cell_w + gap), gap + row * (cell_h + gap)
        sheet.paste(images[i].convert("RGB").resize((cell_w, cell_h), Image.LANCZOS), (x, y))
        text = f"圖{j + 1}  {captions[j]}" if captions else f"圖{j + 1}"
        box = draw.textbbox((x + pad * 2, y + pad * 2), text, font=font)
        draw.rectangle((x + pad, y + pad, box[2] + pad, box[3] + pad), fill=(255, 196, 0))
        draw.text((x + pad * 2, y + pad * 2), text, font=font, fill=(0, 0, 0))
    sheet_path = out_dir / f"分鏡_{data['name']}.png"
    sheet.save(sheet_path)

    total = sum(p["ms"] for p in phases) if beats else sum(s[2] for s in spans)
    steps: list[Step] = []
    if beats:
        # one step per demo phase; every beat in it (picked or not) becomes a sub-line
        figure = {i: j + 1 for j, i in enumerate(picked)}
        for n, phase in enumerate(phases):
            title = re.sub(r"^分鏡\d+\s*", "", phase["name"]) or "畫面描述待補"
            in_phase = [i for i, shot in enumerate(shots) if shot["phase"] == n]
            subs = [captions[picked.index(i)] if i in figure else shots[i]["caption"] for i in in_phase]
            steps.append((title, phase["ms"], [figure[i] for i in in_phase if i in figure], subs, ""))
    else:
        # one step per kept frame; the demo phases it covers are noted for the PM to delete
        for j, (start, end, ms) in enumerate(spans, 1):
            names = "＋".join(p["name"] for p in phases[start:end])
            caption = captions[j - 1] if captions else "畫面描述待補"
            steps.append((caption, ms, [j], [], f"（demo 分段：{names}；貼企劃前刪）"))
    md_path = out_dir / f"分鏡_{data['name']}_企劃草稿.md"
    md_path.write_text(plan_section(data["name"], total, steps, sheet_path.name), encoding="utf-8")
    print(f"kept candidates {[i + 1 for i in picked]} of {len(shots)} -> {sheet_path.name} ({cols}x{rows}, total {seconds_text(total)})")
    if not args.pick and not beats:
        print(f"auto dedupe only: review {contact.name}, drop near-duplicates, rerun with --pick and --captions")
    print(f"wrote {md_path.name}")


def main() -> None:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="cmd", required=True)
    cap = sub.add_parser("capture")
    cap.add_argument("demo_dir")
    cap.add_argument("out_dir")
    cap.add_argument("--page", default="index.html")
    cap.add_argument("--scenarios", default="", help="comma list of scenario ids; default all")
    cap.add_argument("--mode", choices=["auto", "beats", "ratios"], default="auto",
                     help="beats: stop at the demo's demo:beat events; ratios: sample each phase; auto: beats if declared")
    cap.add_argument("--at", default="0.35,0.75", help="ratios mode: pause points within each phase (0-1)")
    cap.add_argument("--shim", default="")
    cap.add_argument("--hide", default="", help="extra CSS selectors hidden during capture")
    cap.add_argument("--skip-phases", default="", help="phases whose name contains any of these words are not captured")
    com = sub.add_parser("compose")
    com.add_argument("out_dir")
    com.add_argument("--scenario", required=True)
    com.add_argument("--pick", default="", help="1-based candidate numbers to keep, overrides auto dedupe")
    com.add_argument("--captions", default="", help="what each kept frame shows, separated by |")
    com.add_argument("--min-diff", type=float, default=3.0, help="auto dedupe threshold (mean pixel difference)")
    com.add_argument("--cell-width", type=int, default=640)
    args = parser.parse_args()
    cmd_capture(args) if args.cmd == "capture" else cmd_compose(args)


if __name__ == "__main__":
    main()
