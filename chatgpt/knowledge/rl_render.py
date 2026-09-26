"""ReportLab fallback renderer for environments without Chromium or WeasyPrint (e.g. the claude.ai sandbox).

Mirrors the Bronzor layout of assets/cv.html.j2 and assets/cover_letter.html.j2 as closely as ReportLab allows.
Called from render_cv.py with the same context dict the HTML templates get.
"""
from pathlib import Path
from xml.sax.saxutils import escape

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_RIGHT
from reportlab.lib.pagesizes import A4, LETTER
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import BaseDocTemplate, Frame, PageTemplate, Paragraph, Spacer, Table, TableStyle

INK = colors.HexColor("#1f1f1d")
MUTED = colors.HexColor("#5b5b57")
FAMILIES = {"serif": "SourceSerif4", "sans": "Inter"}


BUILTIN = {"serif": {"Regular": "Times-Roman", "SemiBold": "Times-Bold", "Bold": "Times-Bold"},
           "sans": {"Regular": "Helvetica", "SemiBold": "Helvetica-Bold", "Bold": "Helvetica-Bold"}}


def register_fonts(font_dir, family):
    base = FAMILIES.get(family, "SourceSerif4")
    if not all((Path(font_dir) / f"{base}-{s}.ttf").exists() for s in ("Regular", "SemiBold", "Bold")):
        print(f"Font files for {base} not found in {font_dir} - using built-in PDF fonts instead.")
        return BUILTIN["sans" if family == "sans" else "serif"]
    names = {}
    for style in ("Regular", "SemiBold", "Bold"):
        name = f"{base}-{style}"
        if name not in pdfmetrics.getRegisteredFontNames():
            pdfmetrics.registerFont(TTFont(name, str(Path(font_dir) / f"{name}.ttf")))
        names[style] = name
    pdfmetrics.registerFontFamily(base, normal=names["Regular"], bold=names["Bold"],
                                  italic=names["Regular"], boldItalic=names["Bold"])
    return names


def t(s):
    return escape(str(s or ""))


def render(ctx, out_path, font_dir, is_letter):
    accent = colors.HexColor(ctx["accent"])
    paper = colors.HexColor(ctx["paper"])
    f = register_fonts(font_dir, "sans" if "Inter" in ctx["font_stack"].split(",")[0] else "serif")
    page = LETTER if str(ctx["page_size"]).lower() == "letter" else A4
    side, top = 16 * mm, 13 * mm
    width = page[0] - 2 * side

    def st(name, **kw):
        base = dict(fontName=f["Regular"], fontSize=9.6, leading=13.2, textColor=INK)
        base.update(kw)
        return ParagraphStyle(name, **base)

    S = {
        "name": st("name", fontName=f["Bold"], fontSize=25, leading=28, alignment=TA_CENTER),
        "headline": st("headline", fontSize=11.5, leading=14, textColor=MUTED, alignment=TA_CENTER, spaceBefore=3),
        "contact": st("contact", fontSize=8.4, leading=11, textColor=MUTED, alignment=TA_CENTER, spaceBefore=4),
        "h2": st("h2", fontName=f["Bold"], fontSize=11.5, leading=14, textColor=accent),
        "body": st("body"),
        "title": st("title", fontName=f["Bold"], fontSize=10, leading=13),
        "sub": st("sub", fontName=f["SemiBold"], fontSize=9.4, leading=12.5),
        "meta": st("meta", fontSize=8.4, leading=12, textColor=MUTED, alignment=TA_RIGHT),
        "bullet": st("bullet", leftIndent=4.2 * mm, bulletIndent=0.6 * mm, bulletColor=accent,
                     bulletFontName=f["Bold"], spaceBefore=1),
        "group": st("group", fontName=f["Bold"]),
    }

    b = ctx["basics"]
    contact = [t(b.get("location")), t(b.get("phone"))]
    if b.get("email"):
        contact.append(f'<a href="mailto:{t(b["email"])}">{t(b["email"])}</a>')
    for link in b.get("links") or []:
        contact.append(f'<a href="{t(link.get("url"))}">{t(link.get("label"))}</a>')
    story = [Paragraph(t(b["name"]), S["name"])]
    if b.get("headline"):
        story.append(Paragraph(t(b["headline"]), S["headline"]))
    story += [Paragraph("&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;".join(c for c in contact if c), S["contact"]),
              Spacer(1, 5 * mm)]

    left, gap = 38 * mm, 5 * mm
    right = width - left - gap

    def head_row(title, meta, title_style):
        meta_w = pdfmetrics.stringWidth(str(meta or ""), f["Regular"], 8.4) + 3 * mm if meta else 0
        cells = [[Paragraph(t(title), title_style), Paragraph(t(meta), S["meta"]) if meta else Spacer(0, 0)]]
        tbl = Table(cells, colWidths=[right - meta_w, meta_w])
        tbl.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "BOTTOM"), ("LEFTPADDING", (0, 0), (-1, -1), 0),
                                 ("RIGHTPADDING", (0, 0), (-1, -1), 0), ("TOPPADDING", (0, 0), (-1, -1), 0),
                                 ("BOTTOMPADDING", (0, 0), (-1, -1), 0)]))
        return tbl

    def item_flowables(e):
        fl = [head_row(e.get("title"), e.get("date"), S["title"])]
        if e.get("subtitle") or e.get("location"):
            fl.append(head_row(e.get("subtitle"), e.get("location"), S["sub"]))
        if e.get("description"):
            fl.append(Paragraph(t(e["description"]), S["body"]))
        for bl in e.get("bullets") or []:
            fl.append(Paragraph(t(bl), S["bullet"], bulletText="•"))
        return fl

    def section(label, rows):
        data = [[Paragraph(t(label) if i == 0 else "", S["h2"]), r] for i, r in enumerate(rows)]
        tbl = Table(data, colWidths=[left + gap, right])
        style = [("VALIGN", (0, 0), (-1, -1), "TOP"), ("LEFTPADDING", (0, 0), (-1, -1), 0),
                 ("RIGHTPADDING", (0, 0), (-1, -1), 0), ("TOPPADDING", (0, 0), (-1, -1), 0),
                 ("BOTTOMPADDING", (0, 0), (-1, -1), 2.6 * mm),
                 ("LINEABOVE", (0, 0), (-1, 0), 0.8, accent), ("TOPPADDING", (0, 0), (-1, 0), 3 * mm),
                 ("BOTTOMPADDING", (0, -1), (-1, -1), 2.2 * mm)]
        tbl.setStyle(TableStyle(style))
        return tbl

    if is_letter:
        L = ctx["letter"]
        rule = Table([[""]], colWidths=[width], rowHeights=[1])
        rule.setStyle(TableStyle([("LINEABOVE", (0, 0), (-1, 0), 0.8, accent)]))
        body = st("letter", fontSize=10.3, leading=16, spaceAfter=3.5 * mm)
        story += [rule, Spacer(1, 5 * mm)]
        if L.get("date"):
            story += [Paragraph(t(L["date"]), st("d", fontSize=10.3, leading=16, textColor=MUTED)), Spacer(1, 5 * mm)]
        for i, line in enumerate(L.get("recipient") or []):
            story.append(Paragraph(t(line), st(f"r{i}", fontSize=10.3, leading=16,
                                               fontName=f["Bold"] if i == 0 else f["Regular"])))
        story.append(Spacer(1, 5 * mm))
        if L.get("subject"):
            story += [Paragraph(t(L["subject"]), st("s", fontName=f["Bold"], fontSize=10.3, leading=16,
                                                    textColor=accent)), Spacer(1, 4 * mm)]
        if L.get("greeting"):
            story.append(Paragraph(t(L["greeting"]), body))
        story += [Paragraph(t(p), body) for p in L.get("paragraphs") or []]
        story += [Spacer(1, 3 * mm), Paragraph(t(L.get("closing") or "Sincerely,"), body), Spacer(1, 9 * mm),
                  Paragraph(t(b["name"]), st("sig", fontName=f["Bold"], fontSize=10.3))]
    else:
        labels = ctx["labels"]
        for sid in ctx["section_order"]:
            label = labels.get(sid, sid.replace("_", " ").title())
            if sid == "summary" and ctx.get("summary"):
                story.append(section(label, [Paragraph(t(ctx["summary"]), S["body"])]))
            elif sid == "skills" and ctx.get("skills"):
                groups = [[Paragraph(t(g.get("group")), S["group"]) if g.get("group") else Spacer(0, 0),
                           Paragraph(t(", ".join(g.get("items", []))), S["body"])] for g in ctx["skills"]]
                cols = 1 if ctx.get("skills_layout") == "single" else 2
                cw = (right - (cols - 1) * 6 * mm) / cols
                cells = []
                for i in range(0, len(groups), cols):
                    row = [g for g in groups[i:i + cols]]
                    row += [[Spacer(0, 0)]] * (cols - len(row))
                    cells.append(row)
                grid = Table(cells, colWidths=[cw + (6 * mm if c < cols - 1 else 0) for c in range(cols)])
                grid.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP"), ("LEFTPADDING", (0, 0), (-1, -1), 0),
                                          ("RIGHTPADDING", (0, 0), (-1, -1), 6 * mm),
                                          ("TOPPADDING", (0, 0), (-1, -1), 0),
                                          ("BOTTOMPADDING", (0, 0), (-1, -1), 2 * mm)]))
                story.append(section(label, [grid]))
            elif ctx["entries"].get(sid):
                story.append(section(label, [item_flowables(e) for e in ctx["entries"][sid]]))

    def background(canvas, doc):
        canvas.saveState()
        canvas.setFillColor(paper)
        canvas.rect(0, 0, page[0], page[1], stroke=0, fill=1)
        canvas.restoreState()

    doc = BaseDocTemplate(str(out_path), pagesize=page, title=f'{b["name"]} - CV', author=b["name"])
    frame = Frame(side, top, width, page[1] - 2 * top, leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=0)
    doc.addPageTemplates([PageTemplate(id="page", frames=[frame], onPage=background)])
    doc.build(story)
