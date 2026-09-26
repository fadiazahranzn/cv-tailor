---
name: cv-tailor
description: Job-application assistant — keeps the user's CV profile, checks how well they fit a job posting (link or pasted text) and whether it's worth applying, rewrites the CV truthfully to the posting's keywords, reports gaps with a learning plan, writes a matching cover letter, and logs every application in an Excel tracker. PDFs use the Reactive Resume "Bronzor" style. Use when the user shares a job/lowongan link, says "sesuaikan CV", "benerin CV", "tailor CV", "bikin CV/cover letter buat lowongan ini", "cek cocok nggak", "update status lamaran", "udah ngelamar ke mana aja", "update profil/CV gw", or invokes /cv-tailor.
---

# CV Tailor

Per job posting the user gets: a fit check → gap report + learning plan → tailored CV PDF → cover letter PDF →
a row in the Excel tracker. Everything must be truthful to the user's own profile.

## Language

- **Chat language**: the very first question of a new user (no saved profile) is
  "Bahasa / Language?  1) Bahasa Indonesia  2) English". Save it as `profile.json` → `"ui_lang": "id" | "en"` and use it
  for every reply, question, and report after that (translate the interview questions too). If a saved profile has
  `ui_lang`, don't ask again; the user can switch any time ("pakai bahasa Inggris aja" / "switch to Indonesian").
- **CV & cover letter language**: asked per job in Step 5 — default is the posting's language
  (`"lang": "en"` or `"lang": "id"`), options: posting language (Recommended) / Indonesia / English / both.
  "Both" = two CV PDFs and two cover letters, suffixed `_ID` and `_EN`.
- Keep the user's tone (casual "gw/lo" or "aku/kamu" is fine in Indonesian).

## Paths

- `<skill>` = the directory of this SKILL.md. Scripts: `<skill>/scripts/`. Schema example: `<skill>/references/example_cv.json`.
- `<home>` = `$CV_TAILOR_HOME` or `~/.cv-tailor/` — the user's own data, never inside the skill folder:
  - `profile.json` — the base CV (same schema as the CV JSON). Backups in `history/profile-YYYYMMDD-HHMM.json`.
  - `config.json` — `{"output_dir": "...", "tracker": ".../lamaran.xlsx"}` (both optional).
  - `lamaran.xlsx` — the tracker (default location).
  - `rencana_belajar.md` — running learning plan for gaps.
- `<out>` = output dir for PDFs: run `python3 <skill>/scripts/data_bundle.py where` — it resolves `config.json` →
  `output_dir`, else `/mnt/user-data/outputs` on claude.ai, else the current working directory.
- `<scratchpad>` = any temp folder (the session scratchpad in Claude Code; `/tmp/cvt` on claude.ai).

## Environment

**Any agent (Claude Code, Codex, Antigravity, Gemini CLI, claude.ai):** tool names in this file are Claude's. If a tool
isn't available, use your equivalent: no AskUserQuestion → ask in chat with numbered options and wait for the answer;
no WebFetch → use your web/browse tool, else ask the user to paste the posting. Use `python3`, or `python` on Windows.
Everything else (scripts, data home `~/.cv-tailor/`, output files) works the same.

This skill runs in two kinds of places. `data_bundle.py where` prints `claude_ai=True/False`.

**Claude Code (local)** — data in `<home>` persists between sessions. Best PDF quality via Chromium
(`npx playwright install chromium-headless-shell`). Python needs `openpyxl`, plus `jinja2` + `pymupdf` for the HTML engines/previews.

**claude.ai (web/desktop/mobile, incl. Free plan)** — the sandbox resets every conversation, so:
- **Session start:** run `data_bundle.py find`. If a `cv-tailor-data*.zip` was uploaded, `data_bundle.py unpack <zip>`
  and treat it as a saved profile. If none, ask the user to upload their `cv-tailor-data.zip` from last time — or
  their CV if this is their first time.
- **Session end (every time something changed):** `data_bundle.py pack <out>/cv-tailor-data.zip` and copy the tracker
  to `<out>/lamaran.xlsx`, then tell the user: "Simpan `cv-tailor-data.zip` — upload lagi di chat berikutnya biar
  profil & tracker kamu nyambung."
- No Chromium → `render_cv.py` falls back to WeasyPrint, then ReportLab (same layout, bundled fonts). Don't try to
  install a browser. If a Python package is missing, try `pip install` once; if there's no network, keep going with
  what's available.
- Ask questions in plain chat (numbered options) if AskUserQuestion isn't available. Uploaded files are usually in
  `/mnt/user-data/uploads/`.
- Free plans have tight usage limits: skip optional extras (previews of every iteration, long tables) and keep
  replies short; handle one job at a time unless the user asks for more.

## Step 0 — Route the request

- New job link(s) / pasted posting → Steps 1–8.
- "Update status lamaran", "udah dipanggil interview", "ditolak" → `tracker.py update ID --status ...`
  (run `tracker.py list` first to find the ID). Done.
- "Udah ngelamar ke mana aja", "mana yang perlu di-follow-up" → `tracker.py list` and summarize
  (highlight rows marked FOLLOW-UP; offer to draft a short follow-up message).
- "Update profil", "gw udah selesai kursus X / bikin project Y" → Step 1 profile update only.
- "Mau cover letter aja" for a job already in the tracker → Step 7 only.

## Step 1 — Profile (base CV)

On claude.ai, first restore uploaded data (see Environment). Then check `<home>/profile.json`.

**Profile exists** → AskUserQuestion: "Pakai profil tersimpan (<name>, update terakhir <mtime>)?"
1. Pakai profil tersimpan (Recommended)
2. Upload CV baru (replaces/merges into the profile)
3. Bikin dari nol

**No profile** → always ask first, before anything else (AskUserQuestion, or numbered options in plain chat) —
in the same AskUserQuestion call: the chat language ("Bahasa / Language?") and
"Kamu sudah punya CV?" / "Do you have a CV?"  1. Sudah, saya upload  2. Belum, bantu bikin dari nol  3. Punya LinkedIn (export PDF)

In the same AskUserQuestion call, if not already known, ask the job link(s) and — first run only — the theme
(color green/purple/orange, typeface serif (Source Serif 4) / sans (Inter); saved into `profile.json` → `theme`). Under WSL
(`/mnt/c` exists, Claude Code only) on first run, also ask whether to keep the tracker and PDFs in a Windows folder
(e.g. `/mnt/c/Users/<user>/Documents/Lamaran`) so they open from Windows Excel/Explorer; save the answer in `config.json`.

**Upload**: copy the file into `<scratchpad>` (in Claude Code the Read tool may be blocked outside the project), then extract:
PDF → `python3 -c "import pymupdf,sys; print(''.join(p.get_text() for p in pymupdf.open(sys.argv[1])))" FILE`
(no pymupdf → `python3 -c "import pypdf,sys; print(''.join(p.extract_text() for p in pypdf.PdfReader(sys.argv[1]).pages))" FILE`);
DOCX → `python3 -c "import docx,sys; print('\n'.join(p.text for p in docx.Document(sys.argv[1]).paragraphs))" FILE`
(or `pandoc FILE -t plain`). Windows paths `C:\Users\...` → `/mnt/c/Users/...`.
Convert faithfully to the schema (keep wording, dates, numbers; fix only obvious typos). Ask once about anything
suspicious (future end dates, overlaps, missing dates). If a profile already exists, show a short diff and ask
replace vs. merge.

**From scratch**: follow `<skill>/references/guided_cv_interview.md` — a 7-step guided interview (target, contact,
education, work, organizations, projects/courses, skills), one step per message with examples, every step skippable,
then a summary + rewritten bullets for the user to approve before saving. Never fill gaps with guesses.
**LinkedIn**: the user exports their profile (LinkedIn → profile → More → Save to PDF) and uploads it; treat it like
an uploaded CV and use the interview steps only for what's missing.

**Save**: before overwriting, back up the old profile to `<home>/history/`. Then write `<home>/profile.json`.
If the profile was just built (interview or upload) and the user has no job posting yet, offer a general CV
("CV umum"): render `profile.json` directly with `render_cv.py` (headline = target role) into `<out>`.
Tell the user where it lives and that it's reused next time
(on claude.ai: that it's inside `cv-tailor-data.zip`, which they must re-upload next time).

**Profile updates** (new course, project, job, finished learning item): add the entry with the evidence the user
gives, back up, save. If it closes a gap in `rencana_belajar.md`, tick it there.

## Step 2 — Read the job posting

- WebFetch each link. If it's blocked (403 / firewall page — common on Glints, JobStreet, Kalibrr), render it with
  headless Chromium and strip the HTML:
  `<chrome> --headless=new --no-sandbox --virtual-time-budget=15000 --user-agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0 Safari/537.36" --dump-dom URL`
  (`<chrome>` = the full Chromium, e.g. `~/.cache/ms-playwright/chromium-*/chrome-linux64/chrome` — verified on Glints).
  On claude.ai there is no Chromium: use the web fetch tool; if blocked, ask the user to paste the posting text
  (or a screenshot). LinkedIn usually needs login everywhere — ask for the text. Never guess requirements.
- Extract: company, role, level, location/work type, posting language, deadline if stated, and keywords grouped as
  hard skills/tools, domain knowledge, responsibilities, qualifications (degree, years, certs), soft skills.
- Write `<scratchpad>/keywords_<company>.txt`: one per line, `!` prefix for must-haves, aliases with `|`
  (e.g. `!Power BI|PowerBI`). Use the employer's exact wording.

## Step 3 — Fit check (before writing anything)

Run: `python3 <skill>/scripts/keyword_check.py <home>/profile.json <scratchpad>/keywords_<company>.txt`

Then judge each keyword (the script only matches literally):
- ✅ **Match** — clearly evidenced.
- 🟡 **Reframe** — evidence exists under another name (JD "data visualization", CV "Looker Studio").
- ❌ **Gap** — no evidence.

Fit score (0–100): start from the script's weighted score, count 🟡 as matched, then subtract for hard blockers
(required years of experience clearly unmet, mandatory degree/certification/license missing, language requirement,
location/work-permit mismatch) — ~15 each.

Verdict:
- **≥ 70 — Lamar** 
- **50–69 — Lamar dengan catatan** (say what to emphasize and what the risk is)
- **< 50 or a hard blocker — Pertimbangkan skip** (explain why; the user can still choose to proceed)

Show: a compact table (keyword · must/nice · ✅/🟡/❌ · evidence), fit score, verdict, blockers.
Ask "Ada skill di daftar gap yang sebenarnya kamu punya?" — if yes, add it to the profile (Step 1 update) and re-score.

**Several links at once**: fetch and fit-check all of them first, show one ranked table
(company · role · fit · verdict · top gaps), then ask via AskUserQuestion (multiSelect) which ones to generate.
Log skipped ones in the tracker with status `Skip`.

If the user decides to skip a job: log it (`--status Skip`) and stop for that job.

## Step 4 — Learning plan for gaps

For each ❌ gap (must-haves first), give one concrete way to close it:
- a specific free or low-cost resource (Dicoding, Kaggle Learn, Google/Microsoft Learn, freeCodeCamp, Coursera audit,
  official docs, YouTube course) — only name resources you're confident exist; use WebSearch when unsure, and never
  invent URLs;
- a 3–7 day mini project that produces evidence for the CV (e.g. "bikin dashboard Tableau Public dari dataset
  penjualan Kaggle, taruh link-nya di CV");
- a rough time estimate.

Append/update `<home>/rencana_belajar.md`: one checklist line per skill with which jobs asked for it, e.g.
`- [ ] Tableau — diminta: Tokopedia (Data Analyst), Shopee (BI Intern) — Kaggle Learn Data Viz + dashboard Tableau Public (~5 hari)`.
If the skill already has a line, add the new job to it instead of duplicating. Skills requested by several jobs go to
the top — tell the user when a gap keeps recurring ("SQL udah diminta 4 lowongan, ini prioritas").

## Step 5 — Write the tailored CV JSON

Copy `profile.json` to `<scratchpad>/cv_<company>.json` and edit it.

**Language**: ask (can be in the same question as the Step 3 gap confirmation) "CV & cover letter mau bahasa apa?"
1) Ikut bahasa lowongan (Recommended — say which one it is)  2) Bahasa Indonesia  3) English  4) Dua-duanya.
Set `"lang"` accordingly; section titles switch automatically. Translate content faithfully — same facts, no additions.

**Truthfulness (non-negotiable)**: never invent employers, titles, dates, numbers, tools, or results; rephrase only
what the profile supports. ❌ gaps never appear in the CV. "Familiar with / exposure to" only with real training or
project evidence. Keep dates exactly as in the profile.

**Tailoring**
- `basics.headline` = the target role title as written in the posting (or the closest honest variant).
- `summary` (3–4 sentences, ~60–80 words): role identity → strongest matching evidence with numbers →
  3–5 top must-have keywords → what they bring to *this* company.
- `skills`: 3–4 groups named after the JD's themes; matching items first, drop irrelevant ones.
- Bullets: strong verb first, JD keywords where true (🟡 items reworded to the JD's term), most relevant first,
  2–3 per job; unrelated jobs shrink to 1–2 bullets on transferable skills.
- Add `projects` when projects are the strongest evidence (students, career switchers, tech roles).
- Trim certifications/courses so the CV is **1–2 pages** (aim for 1 page for internship/entry level).
- `section_order`: most relevant first. Custom titles via `"labels": {"certifications": "Training & Certifications"}`.

### CV JSON schema
```json
{
  "lang": "en",
  "theme": {"color": "green|purple|orange|#hex", "font": "serif|sans", "page_size": "A4|Letter", "skills_layout": "two-column|single"},
  "basics": {"name": "", "headline": "", "location": "", "phone": "", "email": "", "links": [{"label": "", "url": ""}]},
  "summary": "",
  "skills": [{"group": "", "items": [""]}],
  "experience":     [{"title": "Company", "subtitle": "Position", "date": "", "location": "", "description": "", "bullets": [""]}],
  "projects":       [{"title": "", "subtitle": "", "date": "", "bullets": [""]}],
  "education":      [{"title": "Institution", "subtitle": "Degree", "date": "", "bullets": [""]}],
  "certifications": [{"title": "", "subtitle": "Issuer", "date": "", "bullets": [""]}],
  "awards":         [{"title": "", "subtitle": "", "date": "", "bullets": [""]}],
  "section_order": ["summary", "skills", "experience", "projects", "education", "certifications", "awards"]
}
```
Any other list of `{title, ...}` objects (`publications`, `training`, `volunteer`, `languages`, ...) renders the same
way when its key is in `section_order`; keys not listed there are not rendered.

## Step 6 — Render and verify the CV

```bash
python3 <skill>/scripts/render_cv.py <scratchpad>/cv_<company>.json \
  "<out>/<Full_Name>_CV_<Role>_<Company>.pdf" --png-dir <scratchpad>/preview_<company>
```
The script prints which engine it used (chrome → weasyprint → reportlab); `--engine` forces one.
- Underscored names, e.g. `Alex_Morgan_CV_Data_Analyst_Tokopedia.pdf`. Never overwrite without asking — use `_v2`.
- Read every `page-N.png`: nothing cut off, dates right-aligned, last page not nearly empty (the script warns).
  Trim and re-render as needed. If no previews could be made (no rasterizer), rely on the page count and warnings.
- Re-run `keyword_check.py` on the **PDF** for the final coverage.

## Step 7 — Cover letter

Generate by default for every job that isn't skipped (the user can say "tanpa cover letter").
Write `<scratchpad>/cl_<company>.json`:
```json
{
  "type": "cover_letter",
  "lang": "en",
  "theme": { "...": "same as the CV" },
  "basics": { "...": "same as the tailored CV (headline = target role)" },
  "letter": {
    "date": "25 September 2026",
    "recipient": ["Hiring Manager (or the named recruiter if the posting gives one)", "Company", "City"],
    "subject": "Application for <Role>",
    "greeting": "Dear Hiring Manager,",
    "paragraphs": ["...", "...", "..."],
    "closing": "Sincerely,"
  }
}
```
Indonesian version: `"Jakarta, 25 September 2026"`, subject `"Lamaran Posisi <Role>"`,
greeting `"Dengan hormat,"`, closing `"Hormat saya,"`.

Content (250–350 words, 3–4 paragraphs, must fit on one page):
1. The role, and one specific reason for *this* company (from the posting or company page — no generic flattery).
2. Two or three pieces of evidence mapped to the top must-haves, with numbers, taken from the profile.
3. Optional: address the biggest gap honestly and briefly with the learning-plan step
   ("I'm currently completing X and building Y") — only if the user is actually doing it or agrees to; otherwise leave it out.
4. Close with availability and a call to action.
Same truthfulness rules as the CV. Render with `render_cv.py` to
`<Full_Name>_Cover_Letter_<Role>_<Company>.pdf` and check the preview (exactly 1 page).

## Step 8 — Log to the tracker

```bash
python3 <skill>/scripts/tracker.py add --company "<Company>" --role "<Role>" --link "<url>" \
  --fit <score> --verdict "<Lamar|Lamar dengan catatan|Pertimbangkan skip>" \
  --cov-before <baseline %> --cov-after <final %> --gaps "<top gaps; separated>" \
  --cv "<cv pdf>" --cover "<cover letter pdf>" [--notes "deadline 10 Okt"]
```
On claude.ai, the tracker lives in `<home>`; after logging, copy it to `<out>/lamaran.xlsx` and re-pack the data zip
(see Environment → Session end).
A new row gets status `Siap dikirim`. Re-running for the same link updates the row instead of duplicating it.
Remind the user: once they've actually sent the application, say so, and you'll run
`tracker.py update <ID> --status Dilamar` (which sets a follow-up date 7 days later).
Statuses: Siap dikirim, Dilamar, Screening, Tes, Interview, Offer, Diterima, Ditolak, Tidak dilanjut, Skip.

## Step 9 — Report

Short, in the user's language:
1. Fit score + verdict.
2. File paths: CV (page count), cover letter, tracker (`tracker.py path`). On claude.ai: the downloadable files in
   `<out>`, including `cv-tailor-data.zip`, with a one-line reminder to keep it and upload it next time.
3. Keyword coverage before → after.
4. What changed in the CV (headline, summary angle, sections, keywords added).
5. Gaps + learning plan (and recurring gaps across applications).
6. Offer: other color/font, other language version, a short message to the recruiter.

Several jobs → one summary table at the end (company · role · fit · coverage after · files).
