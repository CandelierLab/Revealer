"""PDF export for Revealer presentations.

reveal.js' built-in ``?print-pdf`` path does not cooperate with Revealer's
absolutely-positioned, JS-fitted content (it renders blank). Instead we render
one PNG per slide with headless Chrome — all fragments shown — and stitch the
images into a PDF with ``img2pdf``.

Requirements: a Chrome/Chromium binary and ``img2pdf`` on PATH.
"""

from __future__ import annotations

import os
import re
import shutil
import subprocess
import tempfile
from pathlib import Path

from .build import build as build_presentation

_CHROME_NAMES = (
    "google-chrome-stable",
    "google-chrome",
    "chromium",
    "chromium-browser",
    "chrome",
)


def _find_chrome() -> str | None:
    for name in _CHROME_NAMES:
        path = shutil.which(name)
        if path:
            return path
    return None


def _make_variant(html_path: Path) -> Path:
    """Write a sibling HTML with fragment gating disabled (all content shown)."""
    h = html_path.read_text()
    h = h.replace("center: false,", "center: false, fragments: false,")
    h = h.replace(
        "</head>",
        "<style>.fragment{opacity:1!important;visibility:visible!important;}</style></head>",
    )
    variant = html_path.with_name("._pdf_variant.html")
    variant.write_text(h)
    return variant


def _routes(html: str) -> list[tuple[int, int]]:
    """Return the (horizontal, vertical) index of every slide, in order."""
    marker = '<div class="slides">'
    if marker not in html:
        return [(0, 0)]
    body = html.split(marker, 1)[1]

    routes: list[tuple[int, int]] = []
    depth = 0
    top_start = 0
    h = -1
    for m in re.finditer(r"<section\b[^>]*>|</section>", body):
        if m.group().startswith("</"):
            depth -= 1
            if depth == 0:
                segment = body[top_start:m.end()]
                inner = len(re.findall(r"<section\b", segment)) - 1
                h += 1
                if inner <= 0:
                    routes.append((h, 0))
                else:
                    routes.extend((h, v) for v in range(inner))
            elif depth < 0:
                break
        else:
            if depth == 0:
                top_start = m.start()
            depth += 1
    return routes or [(0, 0)]


def export_pdf(pres_or_html: str, out: str | None = None, width: int = 1920, height: int = 1080, log=print) -> str:
    """Export a presentation to PDF. Accepts a ``.pres`` (built first) or ``.html``."""
    chrome = _find_chrome()
    if chrome is None:
        raise RuntimeError("No Chrome/Chromium found on PATH (needed for PDF export).")
    if shutil.which("img2pdf") is None:
        raise RuntimeError("img2pdf not found on PATH (install it for PDF export).")

    src = Path(pres_or_html).expanduser().resolve()
    if src.suffix == ".pres":
        html_path = Path(build_presentation(str(src)))
    else:
        html_path = src

    out_path = Path(out).expanduser().resolve() if out else html_path.with_suffix(".pdf")

    routes = _routes(html_path.read_text())
    variant = _make_variant(html_path)
    log("Rendering {0} slides to PDF...".format(len(routes)))

    pngs: list[str] = []
    try:
        with tempfile.TemporaryDirectory() as td:
            for i, (hh, vv) in enumerate(routes):
                png = os.path.join(td, "slide_{0:03d}.png".format(i))
                url = "file://{0}#/{1}/{2}".format(variant, hh, vv)
                subprocess.run(
                    [
                        chrome,
                        "--headless=new",
                        "--disable-gpu",
                        "--no-sandbox",
                        "--hide-scrollbars",
                        "--force-device-scale-factor=1",
                        "--window-size={0},{1}".format(width, height),
                        "--virtual-time-budget=9000",
                        "--run-all-compositor-stages-before-draw",
                        "--screenshot={0}".format(png),
                        url,
                    ],
                    check=True,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                )
                if os.path.exists(png):
                    pngs.append(png)
            if not pngs:
                raise RuntimeError("No slides were rendered.")
            subprocess.run(["img2pdf", "--output", str(out_path), *pngs], check=True)
    finally:
        try:
            variant.unlink()
        except OSError:
            pass

    log("Wrote {0}".format(out_path))
    return str(out_path)
