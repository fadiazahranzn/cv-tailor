#!/usr/bin/env python3
"""Render a CV or cover-letter JSON file to PDF using the Bronzor-style template.

Usage:
  render_cv.py cv.json out.pdf [--png-dir DIR] [--html out.html] [--engine auto|chrome|weasyprint|reportlab]

Engines (auto tries them in this order): headless Chromium (best fidelity), WeasyPrint, ReportLab
(pure-Python fallback for sandboxes such as claude.ai; see rl_render.py).

A JSON with "type": "cover_letter" renders assets/cover_letter.html.j2, otherwise assets/cv.html.j2.

--png-dir writes page previews (page-1.png, ...) so the result can be checked visually.
Prints the page count and flags pages that are almost empty.
"""
import argparse
import glob
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(Path(__file__).resolve().parent))

ACCENTS = {"green": "#4a7a62", "purple": "#7b5ea7", "orange": "#b86a45"}
FONTS = {
    "serif": "'Source Serif 4', 'Source Serif Pro', Georgia, 'DejaVu Serif', serif",
    "sans": "'Inter', 'Liberation Sans', Arial, sans-serif",
}
DEFAULT_ORDER = ["summary", "skills", "experience", "projects", "education",
                 "certifications", "awards", "publications", "languages"]
DEFAULT_LABELS = {
    "en": {"summary": "About me", "skills": "Skills", "experience": "Experience",
           "projects": "Projects", "education": "Education", "certifications": "Certifications",
           "awards": "Achievements", "publications": "Publication", "languages": "Languages",
           "training": "Training", "volunteer": "Organization"},
    "id": {"summary": "Tentang saya", "skills": "Keahlian", "experience": "Pengalaman",
           "projects": "Proyek", "education": "Pendidikan", "certifications": "Sertifikasi",
           "awards": "Prestasi", "publications": "Publikasi", "languages": "Bahasa",
           "training": "Pelatihan", "volunteer": "Organisasi"},
}


def find_chrome():
    for env in ("CV_CHROME",):
        if os.environ.get(env):
            return os.environ[env]
    home = Path.home()
    candidates = sorted(glob.glob(str(home / ".cache/ms-playwright/chromium_headless_shell-*/*/chrome-headless-shell")), reverse=True)
    candidates += sorted(glob.glob(str(home / ".cache/ms-playwright/chromium-*/*/chrome")), reverse=True)
    for name in ("chromium", "chromium-browser", "google-chrome", "google-chrome-stable", "chrome", "msedge"):
        p = shutil.which(name)
        if p:
            candidates.append(p)
    if os.name == "nt":  # Windows: installed Chrome / Edge also print to PDF headlessly
        for base in (os.environ.get("PROGRAMFILES", r"C:\Program Files"),
                     os.environ.get("PROGRAMFILES(X86)", r"C:\Program Files (x86)"),
                     os.environ.get("LOCALAPPDATA", "")):
            candidates += [os.path.join(base, r"Google\Chrome\Application\chrome.exe"),
                           os.path.join(base, r"Microsoft\Edge\Application\msedge.exe")]
    elif sys.platform == "darwin":
        candidates += ["/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
                       "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge"]
    for c in candidates:
        if c and os.path.isfile(c) and os.access(c, os.X_OK):
            return c
    return None


def font_dir():
    """assets/fonts in the skill layout; the script's own folder when files are flat (e.g. ChatGPT /mnt/data)."""
    for d in (SKILL_DIR / "assets" / "fonts", Path(__file__).resolve().parent):
        if (d / "SourceSerif4-Regular.ttf").exists():
            return d
    return SKILL_DIR / "assets" / "fonts"


def build_context(cv):
    theme = cv.get("theme", {})
    lang = cv.get("lang", "en")
    labels = dict(DEFAULT_LABELS.get(lang, DEFAULT_LABELS["en"]))
    labels.update(cv.get("labels", {}))
    color = theme.get("color", "green")
    entries = {k: v for k, v in cv.items() if isinstance(v, list) and v and isinstance(v[0], dict) and "title" in v[0]}
    return {
        "lang": lang,
        "basics": cv["basics"],
        "summary": cv.get("summary"),
        "skills": cv.get("skills", []),
        "skills_layout": theme.get("skills_layout", "two-column"),
        "entries": entries,
        "section_order": cv.get("section_order", DEFAULT_ORDER),
        "labels": labels,
        "accent": ACCENTS.get(color, color),
        "paper": theme.get("paper", "#faf9f5"),
        "font_stack": FONTS.get(theme.get("font", "serif"), theme.get("font")),
        "page_size": theme.get("page_size", "A4"),
        "font_dir": font_dir().as_uri(),
        "letter": cv.get("letter", {}),
    }


def render_html(cv, ctx):
    from jinja2 import Environment, FileSystemLoader, select_autoescape
    env = Environment(loader=FileSystemLoader(SKILL_DIR / "assets"), autoescape=select_autoescape(["html", "j2"]))
    name = "cover_letter.html.j2" if cv.get("type") == "cover_letter" else "cv.html.j2"
    return env.get_template(name).render(**ctx)


def has_module(name):
    try:
        __import__(name)
        return True
    except Exception:
        return False


def pick_engine(requested):
    if requested != "auto":
        return requested
    if find_chrome() and has_module("jinja2"):
        return "chrome"
    if has_module("weasyprint") and has_module("jinja2"):
        return "weasyprint"
    return "reportlab"


def render(cv, out, engine, html_out=None):
    ctx = build_context(cv)
    if engine == "reportlab":
        from rl_render import render as rl
        rl(ctx, out, font_dir(), cv.get("type") == "cover_letter")
        return
    html = render_html(cv, ctx)
    if html_out:
        Path(html_out).write_text(html, encoding="utf-8")
    if engine == "weasyprint":
        import weasyprint
        weasyprint.HTML(string=html, base_url=str(SKILL_DIR / "assets")).write_pdf(str(out))
        return
    chrome = find_chrome()
    if not chrome:
        sys.exit("No Chromium found. Use --engine reportlab, or run: npx playwright install chromium-headless-shell")
    with tempfile.TemporaryDirectory() as tmp:
        html_path = Path(tmp) / "cv.html"
        html_path.write_text(html, encoding="utf-8")
        cmd = [chrome, "--headless", "--no-sandbox", "--disable-gpu", "--no-pdf-header-footer",
               "--virtual-time-budget=8000", f"--print-to-pdf={out}", html_path.resolve().as_uri()]
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        if not out.exists():
            sys.exit(f"PDF render failed:\n{r.stderr[-2000:]}")


def inspect(out, png_dir):
    """Print page count, warn on a nearly empty last page, and write PNG previews when possible."""
    try:
        import pymupdf
    except ImportError:
        pymupdf = None
    if pymupdf:
        doc = pymupdf.open(out)
        print(f"Pages: {len(doc)}")
        for i, page in enumerate(doc):
            blocks = [b for b in page.get_text("blocks") if b[4].strip()]
            fill = max((b[3] for b in blocks), default=0) / page.rect.height
            if i == len(doc) - 1 and fill < 0.25:
                print(f"WARNING: last page {i+1} is only {fill:.0%} filled - trim or rebalance content.")
            if png_dir:
                page.get_pixmap(dpi=90).save(Path(png_dir) / f"page-{i+1}.png")
        return
    try:
        from pypdf import PdfReader
        print(f"Pages: {len(PdfReader(str(out)).pages)}")
    except ImportError:
        pass
    if png_dir:
        try:
            import pypdfium2 as pdfium
            for i, page in enumerate(pdfium.PdfDocument(str(out))):
                page.render(scale=1.25).to_pil().save(Path(png_dir) / f"page-{i+1}.png")
        except ImportError:
            if shutil.which("pdftoppm"):
                subprocess.run(["pdftoppm", "-png", "-r", "90", str(out), str(Path(png_dir) / "page")])
            else:
                print("No PDF rasterizer available - previews skipped; check the PDF text instead.")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cv_json")
    ap.add_argument("out_pdf")
    ap.add_argument("--png-dir")
    ap.add_argument("--html")
    ap.add_argument("--engine", default="auto", choices=["auto", "chrome", "weasyprint", "reportlab"])
    a = ap.parse_args()

    cv = json.loads(Path(a.cv_json).read_text(encoding="utf-8"))
    out = Path(os.path.abspath(a.out_pdf))  # resolve() keeps relative paths on Windows py<3.10
    out.parent.mkdir(parents=True, exist_ok=True)
    engine = pick_engine(a.engine)
    render(cv, out, engine, a.html)
    print(f"PDF: {out}  (engine: {engine})")
    if a.png_dir:
        Path(a.png_dir).mkdir(parents=True, exist_ok=True)
    inspect(out, a.png_dir)
    if a.png_dir:
        print(f"Previews: {a.png_dir}/page-*.png")


if __name__ == "__main__":
    main()
