#!/usr/bin/env python3
"""
Download diagram PNGs for a post's Markdown file.

Usage:
    python scripts/make_diagrams.py output/<slug>.md

What it does:
  1. Reads <slug>.md and finds every [DIAGRAM_PLACEHOLDER: description] line
  2. Reads the matching [MERMAID: ...] blocks from the story draft in the
     same directory (looks for a .draft file) or inline in the .md itself
  3. For each diagram, encodes the Mermaid code as base64 and downloads the
     PNG from mermaid.ink into output/images/<slug>/diagram-N.png
  4. Replaces each [DIAGRAM_PLACEHOLDER: ...] line in the .md with a
     proper Markdown image reference pointing to the saved PNG

After this runs, the .md file has real image links that GitHub renders
inline — open the file in GitHub on your phone to see and save the diagrams.
"""

import sys
import re
import base64
import os
import urllib.request
import urllib.error
from pathlib import Path


MERMAID_INK = "https://mermaid.ink/img/{encoded}?type=png"
PLACEHOLDER_RE = re.compile(r"^\[DIAGRAM_PLACEHOLDER:\s*(.+?)\]\s*$", re.MULTILINE)
MERMAID_BLOCK_RE = re.compile(r"\[MERMAID:\s*\n(.*?)\n\]", re.DOTALL)


def encode_mermaid(code: str) -> str:
    return base64.urlsafe_b64encode(code.strip().encode("utf-8")).decode("utf-8")


def download_png(mermaid_code: str, dest: Path) -> bool:
    url = MERMAID_INK.format(encoded=encode_mermaid(mermaid_code))
    try:
        urllib.request.urlretrieve(url, dest)
        return True
    except urllib.error.URLError as e:
        print(f"  Warning: could not download diagram ({e}). Placeholder kept.")
        return False


def find_mermaid_blocks(draft_path: Path):
    """Return list of Mermaid code strings from a draft file."""
    if not draft_path.exists():
        return []
    text = draft_path.read_text(encoding="utf-8")
    return [m.group(1).strip() for m in MERMAID_BLOCK_RE.finditer(text)]


def main():
    if len(sys.argv) < 2:
        print("Usage: make_diagrams.py <markdown_file>")
        sys.exit(1)

    md_path = Path(sys.argv[1])
    if not md_path.exists():
        print(f"Error: {md_path} not found")
        sys.exit(1)

    slug = md_path.stem
    images_dir = md_path.parent / "images" / slug
    images_dir.mkdir(parents=True, exist_ok=True)

    # Find the story draft — agent saves it as <slug>.draft alongside the .md
    draft_path = md_path.with_suffix(".draft")
    mermaid_blocks = find_mermaid_blocks(draft_path)

    md_text = md_path.read_text(encoding="utf-8")
    placeholders = PLACEHOLDER_RE.findall(md_text)

    if not placeholders:
        print("No diagram placeholders found — nothing to do.")
        return

    if len(mermaid_blocks) < len(placeholders):
        print(
            f"Warning: {len(placeholders)} placeholder(s) but only "
            f"{len(mermaid_blocks)} MERMAID block(s) found in draft. "
            "Missing diagrams will keep their placeholder text."
        )

    print(f"Processing {len(placeholders)} diagram(s) for '{slug}'...")

    def replace_placeholder(match):
        nonlocal diagram_index
        description = match.group(1).strip()
        n = diagram_index
        diagram_index += 1

        img_filename = f"diagram-{n}.png"
        img_path = images_dir / img_filename
        rel_path = f"output/images/{slug}/{img_filename}"

        if n - 1 < len(mermaid_blocks):
            code = mermaid_blocks[n - 1]
            print(f"  Diagram {n}: downloading → {rel_path}")
            ok = download_png(code, img_path)
            if ok:
                return f"![{description}]({rel_path})"

        # Fallback: keep placeholder if download failed or no MERMAID block
        return match.group(0)

    diagram_index = 1
    updated = PLACEHOLDER_RE.sub(replace_placeholder, md_text)
    md_path.write_text(updated, encoding="utf-8")
    print("Done.")


if __name__ == "__main__":
    main()
