#!/usr/bin/env python3
"""Job application tracker stored as an Excel file.

Location: --file PATH, else "tracker" in $CV_TAILOR_HOME/config.json, else $CV_TAILOR_HOME/lamaran.xlsx
($CV_TAILOR_HOME defaults to ~/.cv-tailor).

Commands:
  tracker.py add --company C --role R [--link URL] [--fit N] [--verdict TEXT] [--cov-before N]
                 [--cov-after N] [--gaps "A; B"] [--cv PATH] [--cover PATH] [--status S] [--notes TEXT]
      Adds a row, or updates the existing row with the same link (or same company+role if no link).
  tracker.py update ID [--status S] [--follow-up YYYY-MM-DD] [--notes TEXT] [--cv PATH] [--cover PATH] ...
  tracker.py list [--status S]
  tracker.py path
Statuses: see STATUSES below. Setting status "Dilamar" without a follow-up date sets one 7 days later.
"""
import argparse
import datetime as dt
import json
import os
import sys
from pathlib import Path

from openpyxl import Workbook, load_workbook
from openpyxl.formatting.rule import FormulaRule
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.utils import get_column_letter
from openpyxl.worksheet.datavalidation import DataValidation

SHEET = "Lamaran"
COLUMNS = [  # (header, key, width)
    ("ID", "id", 5), ("Tanggal", "date", 11), ("Perusahaan", "company", 22), ("Posisi", "role", 26),
    ("Link Lowongan", "link", 30), ("Fit Score", "fit", 9), ("Rekomendasi", "verdict", 16),
    ("Keyword Awal %", "cov_before", 10), ("Keyword Akhir %", "cov_after", 10), ("Gap Utama", "gaps", 34),
    ("File CV", "cv", 30), ("File Cover Letter", "cover", 30), ("Status", "status", 15),
    ("Tgl Follow-up", "follow_up", 12), ("Catatan", "notes", 34), ("Update Terakhir", "updated", 11),
]
KEYS = [c[1] for c in COLUMNS]
COL = {k: i + 1 for i, k in enumerate(KEYS)}
STATUSES = ["Siap dikirim", "Dilamar", "Screening", "Tes", "Interview", "Offer", "Diterima",
            "Ditolak", "Tidak dilanjut", "Skip"]
STATUS_COLORS = {"Dilamar": "DCE8F5", "Screening": "E6E0F3", "Tes": "FFF1CC", "Interview": "FFE3C4",
                 "Offer": "D5EFD9", "Diterima": "B9E4C1", "Ditolak": "F6D5D5", "Tidak dilanjut": "E7E7E7",
                 "Skip": "E7E7E7"}
ACCENT = "4A7A62"


def default_path():
    """$CV_TAILOR_HOME/config.json {"tracker": "..."} wins, else $CV_TAILOR_HOME/lamaran.xlsx."""
    home = Path(os.environ.get("CV_TAILOR_HOME", Path.home() / ".cv-tailor"))
    cfg = home / "config.json"
    if cfg.exists():
        tracker = json.loads(cfg.read_text(encoding="utf-8")).get("tracker")
        if tracker:
            return Path(tracker).expanduser()
    return home / "lamaran.xlsx"


def windows_path(p):
    """/mnt/c/Users/x -> C:\\Users\\x so links open from Windows Excel."""
    p = str(p)
    if p.startswith("/mnt/") and len(p) > 6 and p[6] in "/":
        return f"{p[5].upper()}:\\" + p[7:].replace("/", "\\")
    return p


def create(path):
    wb = Workbook()
    ws = wb.active
    ws.title = SHEET
    for i, (header, _, width) in enumerate(COLUMNS, 1):
        c = ws.cell(row=1, column=i, value=header)
        c.font = Font(bold=True, color="FFFFFF")
        c.fill = PatternFill("solid", fgColor=ACCENT)
        c.alignment = Alignment(vertical="center", wrap_text=True)
        ws.column_dimensions[get_column_letter(i)].width = width
    ws.row_dimensions[1].height = 30
    ws.freeze_panes = "D2"
    ws.auto_filter.ref = f"A1:{get_column_letter(len(COLUMNS))}1"

    status_col = get_column_letter(COL["status"])
    dv = DataValidation(type="list", formula1='"' + ",".join(STATUSES) + '"', allow_blank=True)
    dv.add(f"{status_col}2:{status_col}2000")
    ws.add_data_validation(dv)
    last = get_column_letter(len(COLUMNS))
    for status, color in STATUS_COLORS.items():
        ws.conditional_formatting.add(
            f"A2:{last}2000",
            FormulaRule(formula=[f'${status_col}2="{status}"'], fill=PatternFill("solid", fgColor=color)))

    s = wb.create_sheet("Ringkasan")
    s["A1"], s["B1"] = "Status", "Jumlah"
    for c in (s["A1"], s["B1"]):
        c.font = Font(bold=True, color="FFFFFF")
        c.fill = PatternFill("solid", fgColor=ACCENT)
    for i, st in enumerate(STATUSES, 2):
        s.cell(row=i, column=1, value=st)
        s.cell(row=i, column=2, value=f'=COUNTIF({SHEET}!{status_col}:{status_col},A{i})')
    n = len(STATUSES) + 2
    s.cell(row=n, column=1, value="Total").font = Font(bold=True)
    s.cell(row=n, column=2, value=f"=COUNTA({SHEET}!A:A)-1").font = Font(bold=True)
    fit_col = get_column_letter(COL["fit"])
    s.cell(row=n + 1, column=1, value="Rata-rata Fit Score")
    s.cell(row=n + 1, column=2, value=f'=IFERROR(ROUND(AVERAGE({SHEET}!{fit_col}:{fit_col}),0),"-")')
    s.column_dimensions["A"].width = 22
    path.parent.mkdir(parents=True, exist_ok=True)
    wb.save(path)


def rows(ws):
    for r in range(2, ws.max_row + 1):
        if ws.cell(row=r, column=1).value is not None:
            yield r, {k: ws.cell(row=r, column=COL[k]).value for k in KEYS}


def write(ws, r, data):
    for k, v in data.items():
        if v is None or k not in COL:
            continue
        c = ws.cell(row=r, column=COL[k], value=v)
        c.alignment = Alignment(vertical="top", wrap_text=k in ("gaps", "notes", "role", "company"))
        if k in ("link", "cv", "cover") and v:
            c.hyperlink = v if k == "link" else windows_path(v)
            c.font = Font(color="1F5FAF", underline="single")
        if k in ("date", "follow_up", "updated") and isinstance(v, dt.date):
            c.number_format = "yyyy-mm-dd"
    if data.get("status") == "Dilamar" and not ws.cell(row=r, column=COL["follow_up"]).value:
        c = ws.cell(row=r, column=COL["follow_up"], value=dt.date.today() + dt.timedelta(days=7))
        c.number_format = "yyyy-mm-dd"
    c = ws.cell(row=r, column=COL["updated"], value=dt.date.today())
    c.number_format = "yyyy-mm-dd"


def save(wb, path):
    try:
        wb.save(path)
    except PermissionError:
        sys.exit(f"Tidak bisa menulis {path} - tutup dulu file Excel-nya lalu coba lagi.")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["add", "update", "list", "path"])
    ap.add_argument("id", nargs="?", type=int)
    ap.add_argument("--file")
    for k in ("company", "role", "link", "verdict", "gaps", "cv", "cover", "status", "notes", "follow-up"):
        ap.add_argument(f"--{k}")
    for k in ("fit", "cov-before", "cov-after"):
        ap.add_argument(f"--{k}", type=int)
    a = ap.parse_args()

    path = Path(a.file) if a.file else default_path()
    if a.cmd == "path":
        print(path)
        return
    if a.status and a.status not in STATUSES:
        sys.exit(f"Status harus salah satu dari: {', '.join(STATUSES)}")
    if not path.exists():
        create(path)
    wb = load_workbook(path)
    ws = wb[SHEET]

    data = {"company": a.company, "role": a.role, "link": a.link, "fit": a.fit, "verdict": a.verdict,
            "cov_before": a.cov_before, "cov_after": a.cov_after, "gaps": a.gaps, "cv": a.cv,
            "cover": a.cover, "status": a.status, "notes": a.notes,
            "follow_up": dt.date.fromisoformat(a.follow_up) if a.follow_up else None}
    for k in ("cv", "cover"):
        if data[k]:
            data[k] = str(Path(data[k]).expanduser().resolve())

    if a.cmd == "add":
        if not (a.company and a.role):
            sys.exit("add butuh --company dan --role")
        existing = None
        for r, row in rows(ws):
            same_link = a.link and row["link"] == a.link
            same_job = not a.link and (row["company"] or "").lower() == a.company.lower() \
                and (row["role"] or "").lower() == a.role.lower()
            if same_link or same_job:
                existing = (r, row["id"])
        if existing:
            r, rid = existing
            write(ws, r, data)
            print(f"Updated row ID {rid} in {path}")
        else:
            ids = [row["id"] for _, row in rows(ws)]
            rid = max(ids, default=0) + 1
            r = ws.max_row + 1 if ws.cell(row=ws.max_row, column=1).value is not None else ws.max_row
            data.update(id=rid, date=dt.date.today(), status=a.status or "Siap dikirim")
            write(ws, r, data)
            print(f"Added row ID {rid} to {path}")
        save(wb, path)

    elif a.cmd == "update":
        if a.id is None:
            sys.exit("update butuh ID baris")
        for r, row in rows(ws):
            if row["id"] == a.id:
                write(ws, r, {k: v for k, v in data.items() if v is not None})
                save(wb, path)
                print(f"Updated row ID {a.id}")
                return
        sys.exit(f"ID {a.id} tidak ditemukan")

    elif a.cmd == "list":
        today = dt.date.today()
        for _, row in rows(ws):
            if a.status and row["status"] != a.status:
                continue
            fu = row["follow_up"]
            fu = fu.date() if isinstance(fu, dt.datetime) else fu
            due = " <- FOLLOW-UP" if fu and fu <= today and row["status"] in ("Dilamar", "Screening") else ""
            print(f"[{row['id']}] {row['company']} | {row['role']} | fit {row['fit']} | {row['status']}"
                  f" | follow-up {fu or '-'}{due}")
        print(f"File: {path}")


if __name__ == "__main__":
    main()
