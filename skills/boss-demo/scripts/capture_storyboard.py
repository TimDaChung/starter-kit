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
seconds live in the plan text and in the demo. The Markdown skeleton still
lists each frame's seconds = total duration of the phases it stands for (from
its phase up to the next kept frame's phase), which adds up to the demo total.

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
import pathlib
import threading

from PIL import Image, ImageChops, ImageDraw, ImageFont, ImageStat

FONT_CANDIDATES = [
    "C:/Windows/Fonts/msjhbd.ttc",
    "C:/Windows/Fonts/msjh.ttc",
    "/System/Library/Fonts/PingFang.ttc",
    "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc",
]

# Pauses each phase at every ratio in turn. Page timers keep running while the
# demo is paused, so the next stop is only scheduled after Python resumes.
HOOK_JS = """
(ratios) => {
  const cap = window.__cap = { ready: false, shot: null, phaseNo: 0, pending: null };
  const stopAt = (phaseNo, name, ms, k) => {
    const wait = ms * (ratios[k] - (k ? ratios[k - 1] : 0));
    cap.pending = setTimeout(() => {
      if (cap.phaseNo !== phaseNo) return;
      window.DEMO_API.pause();
      cap.shot = { phaseNo, name, ms, k };
      cap.ready = true;
    }, wait);
  };
  cap.next = () => {
    const s = cap.shot;
    cap.ready = false;
    window.DEMO_API.resume();
    if (s.k + 1 < ratios.length) stopAt(s.phaseNo, s.name, s.ms, s.k + 1);
  };
  window.addEventListener('demo:phase', (e) => {
    clearTimeout(cap.pending);
    cap.phaseNo += 1;
    stopAt(cap.phaseNo, e.detail.name, e.detail.ms, 0);
  });
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


# ---------- capture ----------

def capture_scenario(page, scenario: dict, frames_dir: pathlib.Path, skip: list[str]) -> list[dict]:
    phases: list[dict] = []
    shots: list[dict] = []
    page.evaluate("id => { window.__done = false; window.DEMO_API.play(id).then(() => window.__done = true); }", scenario["id"])
    while True:
        page.wait_for_function("window.__cap.ready || window.__done", timeout=120_000)
        if page.evaluate("window.__done && !window.__cap.ready"):
            break
        shot = page.evaluate("window.__cap.shot")
        if not phases or phases[-1]["no"] != shot["phaseNo"]:
            phases.append({"no": shot["phaseNo"], "name": shot["name"], "ms": shot["ms"]})
        if not any(word in shot["name"] for word in skip):
            path = frames_dir / f"{scenario['id']}_{len(shots) + 1:02d}.png"
            page.locator("#stage").screenshot(path=str(path))
            shots.append({"n": len(shots) + 1, "phase": len(phases) - 1, "file": path.name})
        page.evaluate("window.__cap.next()")
    return [{"name": p["name"], "ms": p["ms"]} for p in phases], shots


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
            page.evaluate(HOOK_JS, ratios)
            wanted = [s for s in args.scenarios.split(",") if s]
            for scenario in page.evaluate("window.DEMO_API.scenarios"):
                if wanted and scenario["id"] not in wanted:
                    continue
                phases, shots = capture_scenario(page, scenario, frames_dir, skip)
                result[scenario["id"]] = {"name": scenario["name"], "phases": phases, "shots": shots}
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
    picked = [int(n) - 1 for n in args.pick.split(",")] if args.pick else auto_dedupe(images, args.min_diff)
    captions = [c.strip() for c in args.captions.split("|")] if args.captions else []
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

    total = sum(s[2] for s in spans)
    md = [f"### {data['name']}（共 {seconds_text(total)}）\n"]
    for j, (start, end, ms) in enumerate(spans, 1):
        names = "＋".join(p["name"] for p in phases[start:end])
        caption = captions[j - 1] if captions else "畫面描述待補"
        md.append(f"分鏡{j}（{caption}，{seconds_text(ms)}）")
        md.append(f"  涵蓋 demo 分段：{names}\n")
    md.append(f"[分鏡圖：{sheet_path.name}]\n")
    md_path = out_dir / f"分鏡_{data['name']}_企劃草稿.md"
    md_path.write_text("\n".join(md), encoding="utf-8")
    print(f"kept candidates {[i + 1 for i in picked]} of {len(shots)} -> {sheet_path.name} ({cols}x{rows}, total {seconds_text(total)})")
    if not args.pick:
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
    cap.add_argument("--at", default="0.35,0.75", help="pause points within each phase (0-1), comma list")
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
