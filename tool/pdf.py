"""HTML -> PDF via headless Chromium (Playwright). Usage: python tool/pdf.py in.html out.pdf "Footer title" """
import sys
from pathlib import Path

from playwright.sync_api import sync_playwright

src, out, title = Path(sys.argv[1]).resolve(), sys.argv[2], sys.argv[3]
footer = (f'<div style="font-size:7px;width:100%;padding:0 14mm;color:#5b6675;display:flex;justify-content:space-between">'
          f'<span>{title} · Smithfield Foods NA warehousing &amp; logistics</span>'
          '<span>Page <span class="pageNumber"></span> / <span class="totalPages"></span></span></div>')
with sync_playwright() as p:
    b = p.chromium.launch()
    pg = b.new_page()
    pg.goto(src.as_uri(), wait_until="networkidle")
    pg.pdf(path=out, format="Letter", print_background=True, display_header_footer=True,
           header_template="<span></span>", footer_template=footer,
           margin={"top": "14mm", "bottom": "16mm", "left": "0", "right": "0"})
    b.close()
print("wrote", out)
