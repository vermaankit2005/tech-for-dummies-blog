#!/usr/bin/env python3
"""
Publish a Medium-ready HTML file to Medium as a draft.

Usage:
    python scripts/publish_to_medium.py <html_file> "<title>" [<canonical_url>]

Requires MEDIUM_INTEGRATION_TOKEN in .env
Get your token: medium.com/me/settings → Integration tokens

What this script does:
  1. Finds <!-- DIAGRAM_START ... DIAGRAM_END --> blocks in the HTML
  2. Base64-encodes the Mermaid code inside each block
  3. Replaces the block (+ fallback text line) with a mermaid.ink <img> tag
  4. POSTs the cleaned HTML to the Medium API as a draft
  5. Prints the draft URL so the user can open it in the Medium app
"""

import sys
import os
import json
import base64
import re
import urllib.request
import urllib.error
from pathlib import Path


def load_env():
    env_path = Path(__file__).parent.parent / ".env"
    if not env_path.exists():
        return
    for line in env_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, v = line.split("=", 1)
            os.environ.setdefault(k.strip(), v.strip())


def get_user_id(token):
    req = urllib.request.Request(
        "https://api.medium.com/v1/me",
        headers={
            "Authorization": f"Bearer {token}",
            "Accept": "application/json",
        },
    )
    try:
        with urllib.request.urlopen(req) as r:
            return json.loads(r.read())["data"]["id"]
    except urllib.error.HTTPError as e:
        body = e.read().decode()
        raise SystemExit(f"Medium API auth failed ({e.code}): {body}")


def mermaid_to_ink_url(mermaid_code):
    # mermaid.ink accepts base64url-encoded Mermaid syntax at /img/<base64>
    encoded = base64.urlsafe_b64encode(mermaid_code.strip().encode("utf-8")).decode("utf-8")
    return f"https://mermaid.ink/img/{encoded}"


def convert_diagrams(html):
    """Replace <!-- DIAGRAM_START ... DIAGRAM_END --> blocks with mermaid.ink img tags.

    The comment block is immediately followed by a fallback <p> line which
    is also removed, leaving only the image.
    """
    pattern = re.compile(
        r"<!--\s*DIAGRAM_START\s*\n(.*?)\nDIAGRAM_END\s*-->\s*\n\s*<p><em>\[Diagram:[^\]]*\]</em></p>",
        re.DOTALL,
    )

    def replace(match):
        mermaid_code = match.group(1)
        url = mermaid_to_ink_url(mermaid_code)
        return f'<img src="{url}" alt="diagram" />'

    return pattern.sub(replace, html)


def publish_draft(user_id, token, title, html_content, canonical_url=None):
    payload = {
        "title": title,
        "contentFormat": "html",
        "content": html_content,
        "publishStatus": "draft",
    }
    if canonical_url:
        payload["canonicalUrl"] = canonical_url

    body = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        f"https://api.medium.com/v1/users/{user_id}/posts",
        data=body,
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        },
    )
    try:
        with urllib.request.urlopen(req) as r:
            data = json.loads(r.read())
        return data["data"]["url"]
    except urllib.error.HTTPError as e:
        body = e.read().decode()
        raise SystemExit(f"Medium API publish failed ({e.code}): {body}")


def main():
    if len(sys.argv) < 3:
        print("Usage: publish_to_medium.py <html_file> <title> [canonical_url]")
        sys.exit(1)

    load_env()

    token = os.environ.get("MEDIUM_INTEGRATION_TOKEN")
    if not token or token == "your_token_here":
        raise SystemExit(
            "Error: MEDIUM_INTEGRATION_TOKEN not set.\n"
            "Get yours at medium.com/me/settings → Integration tokens\n"
            "Then add it to .env"
        )

    html_file = sys.argv[1]
    title = sys.argv[2]
    canonical_url = sys.argv[3] if len(sys.argv) > 3 else None

    html_path = Path(html_file)
    if not html_path.exists():
        raise SystemExit(f"Error: file not found: {html_file}")

    content = html_path.read_text(encoding="utf-8")
    content = convert_diagrams(content)

    user_id = get_user_id(token)
    draft_url = publish_draft(user_id, token, title, content, canonical_url)

    print(f"\nDraft published to Medium: {draft_url}")
    print("Open the Medium app → Your profile → Drafts → review and tap Publish.")


if __name__ == "__main__":
    main()
