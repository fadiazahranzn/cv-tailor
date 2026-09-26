#!/usr/bin/env python3
"""Check which job keywords appear in a CV (PDF or JSON) and compute a fit score.

Usage:
  keyword_check.py CV(.pdf|.json) keywords.txt [--json]

keywords.txt: one keyword per line.
  - Prefix "!" marks a must-have (weight 2); others are nice-to-have (weight 1).
  - Aliases on the same line separated by "|" (e.g. "!Power BI|PowerBI").
  - Lines starting with "#" are ignored.

Output: literal coverage (all keywords), must-have coverage, weighted fit score, matched/missing lists.
The fit score is only literal matching - the skill adjusts it with judgment (reframeable skills, blockers).
"""
import json
import re
import sys
from pathlib import Path


def cv_text(path):
    p = Path(path)
    if p.suffix.lower() == ".pdf":
        try:
            import pymupdf
            return "\n".join(page.get_text() for page in pymupdf.open(p))
        except ImportError:
            from pypdf import PdfReader
            return "\n".join(page.extract_text() or "" for page in PdfReader(str(p)).pages)
    data = json.loads(p.read_text(encoding="utf-8"))
    keep = {k: v for k, v in data.items() if not k.startswith("_")}
    return json.dumps(keep, ensure_ascii=False)


def found(term, text):
    t = re.escape(term.strip().lower())
    return re.search(rf"(?<![a-z0-9]){t}(?![a-z0-9])", text) is not None


def pct(a, b):
    return round(a * 100 / b) if b else 0


def main():
    args = [a for a in sys.argv[1:] if a != "--json"]
    if len(args) != 2:
        sys.exit(__doc__)
    text = re.sub(r"\s+", " ", cv_text(args[0]).lower())
    lines = [l.strip() for l in Path(args[1]).read_text(encoding="utf-8").splitlines()]
    kws = [l for l in lines if l and not l.startswith("#")]

    rows = []
    for k in kws:
        must = k.startswith("!")
        aliases = k.lstrip("!").split("|")
        rows.append({"keyword": aliases[0].strip(), "must": must,
                     "hit": any(found(a, text) for a in aliases)})

    must = [r for r in rows if r["must"]]
    weight = sum(2 if r["must"] else 1 for r in rows)
    got = sum(2 if r["must"] else 1 for r in rows if r["hit"])
    result = {
        "coverage": pct(sum(r["hit"] for r in rows), len(rows)),
        "must_coverage": pct(sum(r["hit"] for r in must), len(must)),
        "fit_score": pct(got, weight),
        "matched": [r["keyword"] for r in rows if r["hit"]],
        "missing_must": [r["keyword"] for r in rows if r["must"] and not r["hit"]],
        "missing_nice": [r["keyword"] for r in rows if not r["must"] and not r["hit"]],
    }
    if "--json" in sys.argv:
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return
    print(f"Coverage: {sum(r['hit'] for r in rows)}/{len(rows)} ({result['coverage']}%)")
    print(f"Must-have coverage: {result['must_coverage']}%   Weighted fit score: {result['fit_score']}")
    print("Matched: " + ", ".join(result["matched"]))
    print("Missing (must): " + ", ".join(result["missing_must"]))
    print("Missing (nice): " + ", ".join(result["missing_nice"]))


if __name__ == "__main__":
    main()
