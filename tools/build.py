#!/usr/bin/env python3
"""Build every distributable package from the single sources in skill/ and shared/.

  python tools/build.py              sync chatgpt/ + gemini/ knowledge, build dist/*.zip, run the privacy check
  python tools/build.py --previews   also re-render docs/preview-*.png from the fictional example CV

Sources of truth:
  skill/cv-tailor/      the agent skill (scripts, templates, fonts, SKILL.md)
  shared/WORKFLOW.md    platform-neutral rules used by ChatGPT and Gemini
  shared/cv-template.html  standalone HTML template used by Gemini
"""
import json
import re
import shutil
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKILL = ROOT / "skill" / "cv-tailor"
SHARED = ROOT / "shared"
CHATGPT = ROOT / "chatgpt"
GEMINI = ROOT / "gemini"
DIST = ROOT / "dist"
DOCS = ROOT / "docs"

TEXT_EXT = {".md", ".txt", ".py", ".json", ".j2", ".html"}
# anything that looks like a real person's contact detail; the example CV uses example.com and a 0000 number
EMAIL = re.compile(r"[\w.+-]+@(?!example\.com)[A-Za-z0-9-]+(?:\.[A-Za-z0-9-]+)*\.[A-Za-z]{2,}")
PHONE = re.compile(r"(?<!\d)(?:\+62|62|0)8\d{8,11}(?!\d)")
ALLOWED_EMAILS = {"noreply@anthropic.com"}


def zip_dir(src, out, arc_root=None, flat=False):
    out.parent.mkdir(parents=True, exist_ok=True)
    if out.exists():
        out.unlink()
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
        for p in sorted(src.rglob("*")):
            if p.is_file() and "__pycache__" not in p.parts and p != out:
                name = p.name if flat else str(Path(arc_root or src.name) / p.relative_to(src))
                z.write(p, name)
    print(f"  {out.relative_to(ROOT)}  ({out.stat().st_size // 1024} KB)")


def sync_chatgpt():
    k = CHATGPT / "knowledge"
    if k.exists():
        shutil.rmtree(k)
    k.mkdir(parents=True)
    for f in (SKILL / "scripts").glob("*.py"):
        shutil.copy2(f, k)
    for f in (SKILL / "assets" / "fonts").glob("*.ttf"):
        shutil.copy2(f, k)
    shutil.copy2(SKILL / "references" / "example_cv.json", k)
    shutil.copy2(SHARED / "WORKFLOW.md", k)
    lic = CHATGPT / "licenses"
    lic.mkdir(exist_ok=True)
    for f in (SKILL / "assets" / "fonts").glob("OFL-*.txt"):
        shutil.copy2(f, lic)
    zip_dir(k, CHATGPT / "cv-tailor-kit.zip", flat=True)


def sync_gemini():
    k = GEMINI / "knowledge"
    if k.exists():
        shutil.rmtree(k)
    k.mkdir(parents=True)
    shutil.copy2(SHARED / "WORKFLOW.md", k)
    shutil.copy2(SHARED / "cv-template.html", k)
    shutil.copy2(SHARED / "cv-template.html", k / "cv-template.txt")  # for uploaders that reject .html


def privacy_check():
    problems = []
    for p in ROOT.rglob("*"):
        if (not p.is_file() or p.suffix not in TEXT_EXT or ".git" in p.parts
                or p.name in ("build.py", "private_terms.txt")):
            continue
        text = p.read_text(encoding="utf-8", errors="ignore")
        for m in EMAIL.findall(text):
            if m not in ALLOWED_EMAILS and not m.startswith("git@"):
                problems.append(f"{p.relative_to(ROOT)}: email {m}")
        for m in PHONE.findall(text):
            problems.append(f"{p.relative_to(ROOT)}: phone {m}")
    terms_file = ROOT / "tools" / "private_terms.txt"  # optional, git-ignored: your own name, employers, etc.
    terms = [t.strip().lower() for t in terms_file.read_text(encoding="utf-8").splitlines()
             if t.strip() and not t.startswith("#")] if terms_file.exists() else []
    for p in ROOT.rglob("*"):
        if (p.is_file() and p.suffix in TEXT_EXT and ".git" not in p.parts
                and p.name not in ("build.py", "private_terms.txt")):
            low = p.read_text(encoding="utf-8", errors="ignore").lower()
            problems += [f"{p.relative_to(ROOT)}: private term '{t}'" for t in terms if t in low]
    for bad in ("profile.json", "lamaran.xlsx", "rencana_belajar.md", "profil-tambahan.txt"):
        problems += [f"personal data file: {p.relative_to(ROOT)}" for p in ROOT.rglob(bad) if ".git" not in p.parts]
    problems += [f"personal data file: {p.relative_to(ROOT)}" for p in ROOT.rglob("cv-tailor-data*.zip")]
    if problems:
        print("PRIVACY CHECK FAILED:\n  " + "\n  ".join(problems))
        sys.exit(1)
    print("  privacy check passed (no real emails, phone numbers or personal data files)")


def previews():
    DOCS.mkdir(exist_ok=True)
    import pymupdf
    ex = json.loads((SKILL / "references" / "example_cv.json").read_text(encoding="utf-8"))
    letter = {"type": "cover_letter", "lang": "en", "theme": ex["theme"], "basics": ex["basics"], "letter": {
        "date": "1 October 2026", "recipient": ["Hiring Team", "Example Company", "Jakarta"],
        "subject": "Application for Data Analyst", "greeting": "Dear Hiring Team,",
        "paragraphs": [
            "I am applying for the Data Analyst role at Example Company. Your team's focus on data-driven retail "
            "decisions matches the work I enjoy most.",
            "At Northstar Retail I built Power BI dashboards used weekly by 40+ store managers, replacing six manual "
            "Excel reports, and wrote SQL models in BigQuery that reduced stock discrepancies by 15%.",
            "I would welcome the chance to discuss how I can support your analytics team. Thank you for your time."],
        "closing": "Sincerely,"}}
    with tempfile.TemporaryDirectory() as tmp:
        for name, data in (("cv", ex), ("cover-letter", letter)):
            src = Path(tmp) / f"{name}.json"
            src.write_text(json.dumps(data), encoding="utf-8")
            pdf = Path(tmp) / f"{name}.pdf"
            subprocess.run([sys.executable, str(SKILL / "scripts" / "render_cv.py"), str(src), str(pdf)], check=True,
                           capture_output=True)
            pymupdf.open(pdf)[0].get_pixmap(dpi=80).save(DOCS / f"preview-{name}.png")
            print(f"  docs/preview-{name}.png")


def main():
    print("Syncing platform packages...")
    sync_chatgpt()
    sync_gemini()
    print("Checking for personal data...")
    privacy_check()
    if "--previews" in sys.argv:
        print("Rendering previews...")
        previews()
    print("Building dist/ ...")
    zip_dir(SKILL, DIST / "cv-tailor-skill.zip", arc_root="cv-tailor")
    zip_dir(CHATGPT, DIST / "cv-tailor-chatgpt.zip", arc_root="cv-tailor-chatgpt")
    zip_dir(GEMINI, DIST / "cv-tailor-gemini.zip", arc_root="cv-tailor-gemini")
    print("Done.")


if __name__ == "__main__":
    main()
