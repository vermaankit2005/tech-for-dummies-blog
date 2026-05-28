#!/usr/bin/env python3
"""
Inject the phone-friendly diagram-export snippet into post HTML files.

Usage:
    python scripts/add_diagram_export.py               # patch all output/*.html
    python scripts/add_diagram_export.py output/foo.html ...   # specific files

Idempotent: skips files that already contain the snippet. The snippet is read
from scripts/diagram_export_snippet.html and inserted just before </body>.
"""

import sys
import glob
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SNIPPET_PATH = ROOT / "scripts" / "diagram_export_snippet.html"
MARKER = "dexport-bar"  # presence means already patched


def patch(path: Path, snippet: str) -> str:
    html = path.read_text(encoding="utf-8")
    if MARKER in html:
        return "skip (already patched)"
    if "</body>" not in html:
        return "ERROR: no </body> found"
    html = html.replace("</body>", snippet.rstrip() + "\n</body>", 1)
    path.write_text(html, encoding="utf-8")
    return "patched"


def main() -> None:
    snippet = SNIPPET_PATH.read_text(encoding="utf-8")
    args = sys.argv[1:]
    files = [Path(a) for a in args] if args else [Path(p) for p in glob.glob(str(ROOT / "output" / "*.html"))]
    if not files:
        print("no HTML files found")
        return
    for f in sorted(files):
        print(f"{f.name}: {patch(f, snippet)}")


if __name__ == "__main__":
    main()
