# Publishing a post to Medium (in the HTML format)

## Why markdown paste fails

The diagrams in each post's HTML aren't images — they're `<div class="diagram">`
blocks drawn with CSS. They look right in a browser, but Medium is **not** HTML:
on paste *or* URL-import it strips all custom CSS/HTML and keeps only headings,
bold/italic, links, blockquotes, lists, code blocks, and **real image files**.
So a CSS diagram can never survive into Medium as-is — it has to become an image
first. That's the whole problem.

## The workflow (phone)

Every post's HTML now has a baked-in helper. Steps:

1. **Open the post's `.html` in your phone browser.**
   (From GitHub mobile: open the file → "View raw"/download, or use a Pages URL
   if you publish one. Anything that renders the page in a browser works.)
2. **Tap the floating button** at the bottom: **"⬇ turn diagrams into images"**.
   Every CSS diagram is rendered to a PNG right there in the page.
3. **Long-press each diagram image → "Save to Photos".**
4. **In Medium:** Select-all the *text* in the browser, copy, paste into the
   Medium editor (headline, subheads, bold, quotes all carry over). Then place
   your cursor where each diagram goes and **insert the saved image** from Photos.

That's it: text via paste, diagrams via long-press-save. No scripts to run.

## How the helper gets there

- The snippet lives in `scripts/diagram_export_snippet.html`.
- It's auto-injected before `</body>` by `scripts/add_diagram_export.py`
  (idempotent — safe to re-run):

  ```
  python scripts/add_diagram_export.py            # all output/*.html
  python scripts/add_diagram_export.py output/<slug>.html
  ```

- It renders client-side via `html-to-image` (CDN), so it needs a network
  connection when you open the page on your phone.

## For every new post

After writing a post's HTML, run the patcher (or paste the snippet from
`scripts/diagram_export_snippet.html` just before `</body>`) so the new post
also gets the "turn diagrams into images" button.
