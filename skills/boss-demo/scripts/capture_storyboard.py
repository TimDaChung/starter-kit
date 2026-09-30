"""Capture key frames from a finished boss-demo and compose them into storyboard sheets.

Flow per scenario: force-play it, pause each phase at --at of its duration,
screenshot the #stage element, resume. Then stitch the frames into one sheet
per scenario with "圖N  X秒" tags (house style of existing boss plans), and
write a Markdown skeleton listing every frame for the plan write-up.

The demo must expose the capture contract (see SKILL.md, 「分鏡擷取介面」):
    window.DEMO_API = { scenarios: [{id, name}], play(id) -> Promise, pause(), resume() }
    window.dispatchEvent(new CustomEvent('demo:phase', {detail: {name, ms}}))  // at each phase start
Older demos without it can be driven with --shim <js> (injected after load).

Usage:
    python capture_storyboard.py <demo_dir> <out_dir> [--scenarios small,mid] [--at 0.6]
                                 [--shim shim.js] [--skip-phases 被捕獲,轉場] [--cell-width 640]
                                 [--hide "#btnrow,#phase-hud"]

Elements with class "demo-ui" are always hidden while capturing (debug HUD,
buttons); --hide adds more selectors for demos that predate that convention.

The demo directory is served over a local HTTP server (file:// breaks on
non-ASCII paths and blocks some assets).
"""
import argparse
import functools
import http.server
import json
import pathlib
import threading

from PIL import Image, ImageDraw, ImageFont
from playwright.sync_api import sync_playwright

FONT_CANDIDATES = [
    "C:/Windows/Fonts/msjhbd.ttc",
    "C:/Windows/Fonts/msjh.ttc",
    "/System/Library/Fonts/PingFang.ttc",
    "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc",
]

HOOK_JS = """
(ratio) => {
  window.__cap = { ready: false, phase: null, count: 0 };
  window.addEventListener('demo:phase', (e) => {
    const { name, ms } = e.detail;
    window.__cap.count += 1;
    const n = window.__cap.count;
    setTimeout(() => {
      if (window.__cap.count !== n) return;  // phase already ended (skipped)
      window.DEMO_API.pause();
      window.__cap.phase = { name, ms, n };
      window.__cap.ready = true;
    }, ms * ratio);
  });
}
"""


def QuietHandler(partial: functools.partial) -> type:
    class Handler(partial.func):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, directory=partial.keywords["directory"], **kwargs)

        def log_message(self, *args) -> None:
            pass

    return Handler


def serve(directory: pathlib.Path) -> tuple[http.server.ThreadingHTTPServer, int]:
    handler = functools.partial(http.server.SimpleHTTPRequestHandler, directory=str(directory))
    server = http.server.ThreadingHTTPServer(("127.0.0.1", 0), QuietHandler(handler))
    threading.Thread(target=server.serve_forever, daemon=True).start()
    return server, server.server_address[1]


def load_font(size: int) -> ImageFont.FreeTypeFont:
    for path in FONT_CANDIDATES:
        if pathlib.Path(path).exists():
            return ImageFont.truetype(path, size)
    raise SystemExit("no CJK font found; add one to FONT_CANDIDATES")


def seconds_text(ms: float) -> str:
    return f"{ms / 1000:.2f}".rstrip("0").rstrip(".") + "秒"


def compose(frames: list[dict], out: pathlib.Path, cell_w: int) -> tuple[int, int]:
    n = len(frames)
    cols = n if n <= 3 else 2 if n == 4 else 3
    rows = -(-n // cols)
    first = Image.open(frames[0]["file"])
    cell_h = round(cell_w * first.height / first.width)
    gap = round(cell_w * 0.02)
    sheet = Image.new("RGB", (cols * cell_w + (cols + 1) * gap, rows * cell_h + (rows + 1) * gap), (24, 24, 24))
    draw = ImageDraw.Draw(sheet)
    font = load_font(round(cell_h * 0.075))
    pad = round(cell_h * 0.025)
    for i, frame in enumerate(frames):
        row, col = divmod(i, cols)
        x, y = gap + col * (cell_w + gap), gap + row * (cell_h + gap)
        sheet.paste(Image.open(frame["file"]).resize((cell_w, cell_h), Image.LANCZOS), (x, y))
        text = f"圖{i + 1}  {seconds_text(frame['ms'])}"
        box = draw.textbbox((x + pad * 2, y + pad * 2), text, font=font)
        draw.rectangle((x + pad, y + pad, box[2] + pad, box[3] + pad), fill=(255, 196, 0))
        draw.text((x + pad * 2, y + pad * 2), text, font=font, fill=(0, 0, 0))
    sheet.save(out)
    return cols, rows


def capture(page, scenario: dict, out_dir: pathlib.Path, skip: list[str]) -> list[dict]:
    frames: list[dict] = []
    page.evaluate("id => { window.__done = false; window.DEMO_API.play(id).then(() => window.__done = true); }", scenario["id"])
    while True:
        page.wait_for_function("window.__cap.ready || window.__done", timeout=120_000)
        if page.evaluate("window.__done && !window.__cap.ready"):
            break
        phase = page.evaluate("window.__cap.phase")
        if not any(word in phase["name"] for word in skip):
            path = out_dir / f"{scenario['id']}_{len(frames) + 1:02d}.png"
            page.locator("#stage").screenshot(path=str(path))
            frames.append({"name": phase["name"], "ms": phase["ms"], "file": path})
        page.evaluate("window.__cap.ready = false; window.DEMO_API.resume();")
    return frames


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("demo_dir")
    parser.add_argument("out_dir")
    parser.add_argument("--page", default="index.html")
    parser.add_argument("--scenarios", default="", help="comma list of scenario ids; default all")
    parser.add_argument("--at", type=float, default=0.6, help="pause point within each phase (0-1)")
    parser.add_argument("--shim", default="", help="JS file injected after load for demos without DEMO_API")
    parser.add_argument("--skip-phases", default="", help="comma list: phases whose name contains any word are not captured")
    parser.add_argument("--cell-width", type=int, default=640)
    parser.add_argument("--hide", default="", help="extra CSS selectors hidden during capture")
    args = parser.parse_args()

    demo_dir = pathlib.Path(args.demo_dir).resolve()
    out_dir = pathlib.Path(args.out_dir).resolve()
    frames_dir = out_dir / "frames"
    frames_dir.mkdir(parents=True, exist_ok=True)
    skip = [w for w in args.skip_phases.split(",") if w]
    server, port = serve(demo_dir)
    summary: list[dict] = []
    try:
        with sync_playwright() as pw:
            browser = pw.chromium.launch()
            page = browser.new_page(viewport={"width": 1600, "height": 1000})
            page.goto(f"http://127.0.0.1:{port}/{args.page}")
            if args.shim:
                page.add_script_tag(content=pathlib.Path(args.shim).read_text(encoding="utf-8"))
            page.wait_for_function("window.DEMO_API && window.DEMO_API.scenarios")
            hidden = ",".join([".demo-ui"] + [s for s in args.hide.split(",") if s])
            page.add_style_tag(content=f"{hidden} {{ visibility: hidden !important; }}")
            page.evaluate(HOOK_JS, args.at)
            scenarios = page.evaluate("window.DEMO_API.scenarios")
            wanted = [s for s in args.scenarios.split(",") if s]
            for scenario in scenarios:
                if wanted and scenario["id"] not in wanted:
                    continue
                frames = capture(page, scenario, frames_dir, skip)
                if not frames:
                    print(f"{scenario['name']}: no frames captured")
                    continue
                sheet = out_dir / f"分鏡_{scenario['name']}.png"
                cols, rows = compose(frames, sheet, args.cell_width)
                total = sum(f["ms"] for f in frames)
                summary.append({"scenario": scenario, "sheet": sheet.name, "total_ms": total,
                                "frames": [{"name": f["name"], "ms": f["ms"], "file": f["file"].name} for f in frames]})
                print(f"{scenario['name']}: {len(frames)} frames, {cols}x{rows}, total {seconds_text(total)} -> {sheet.name}")
            browser.close()
    finally:
        server.shutdown()

    md = []
    for item in summary:
        md.append(f"### {item['scenario']['name']}（共 {seconds_text(item['total_ms'])}）\n")
        for i, f in enumerate(item["frames"], 1):
            md.append(f"分鏡{i}（{f['name']}，{seconds_text(f['ms'])}）")
            md.append("  （畫面描述：待補）\n")
        md.append(f"[分鏡圖：{item['sheet']}]\n")
    (out_dir / "分鏡_企劃草稿.md").write_text("\n".join(md), encoding="utf-8")
    (out_dir / "分鏡_summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"wrote {out_dir / '分鏡_企劃草稿.md'}")


if __name__ == "__main__":
    main()
