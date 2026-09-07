#!/usr/bin/env python3
"""원두 정보 JSON -> 라벨 링크 + 미리보기 PNG"""
import sys, json, base64, os
from playwright.sync_api import sync_playwright

BASE = "https://odc1966-dev.github.io/-/tools/bean-label-maker/pwa/"
APP  = os.path.join(os.path.dirname(os.path.abspath(__file__)), "pwa", "index.html")

def link(d):
    raw = json.dumps(d, ensure_ascii=False, separators=(",", ":")).encode()
    return BASE + "?d=" + base64.urlsafe_b64encode(raw).decode().rstrip("=")

def preview(d, design="basic", out="label_preview"):
    with sync_playwright() as p:
        b = p.chromium.launch(executable_path="/opt/pw-browsers/chromium-1194/chrome-linux/chrome",
                              args=["--no-sandbox"])
        pg = b.new_page(); pg.goto("file://" + APP)
        pg.evaluate("""o=>{const s=(i,v)=>{const e=document.getElementById(i); e.value=v||'';};
            s('brand',o.brand); s('origin',o.origin); s('region',o.region); s('farm',o.farm);
            s('process',o.process); s('roasted',o.roasted);
            const n=(o.notes||[]); s('n1',n[0]); s('n2',n[1]); s('n3',n[2]);}""", d)
        files = []
        for w, tag in [(960, "600dpi"), (320, "203dpi")]:
            u = pg.evaluate("a=>{drawLabel(a[0],a[1]);return cv.toDataURL('image/png');}", [w, design])
            f = f"{out}_{tag}.png"; open(f, "wb").write(base64.b64decode(u.split(",")[1])); files.append(f)
        b.close()
        return files

if __name__ == "__main__":
    d = json.loads(sys.argv[1])
    design = sys.argv[2] if len(sys.argv) > 2 else "basic"
    print(link(d))
    print("\n".join(preview(d, design)))
