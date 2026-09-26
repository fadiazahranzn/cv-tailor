# Guided interview — building a CV from scratch

Use when the user has no CV. Goal: a complete, honest profile without overwhelming them.
Many users here are students, fresh graduates, or career switchers who think they "have nothing to write" —
your job is to draw out real experience (organizations, projects, part-time work) and phrase it well.

## Rules

- One round per message, at most ~5 short questions, each with a concrete example answer.
- Say which round they're on ("Langkah 2 dari 7") so they know how long it takes.
- Every round can be skipped ("skip" / "nggak ada"). Never make them feel bad about an empty section.
- Accept rough answers (bullet fragments, Indonesian, typos). You turn them into good CV wording later —
  but never add facts, numbers, tools, or results they didn't give. If a number would help, ask for it.
- Ask in the user's chosen chat language (the examples below are in Indonesian — translate them for English users);
  keep your messages short.
- If they have a LinkedIn profile, offer a shortcut first: LinkedIn → profile → "More/Lainnya" → "Save to PDF",
  then upload that PDF and treat it like an uploaded CV (only fill the gaps with the rounds below).

## Rounds

**Langkah 1 — Target**
- Posisi apa yang mau dilamar? (contoh: Data Analyst, Admin, QA, Marketing)
- Status sekarang: mahasiswa / fresh graduate / sudah kerja / pindah bidang?
- CV-nya mau bahasa Indonesia, Inggris, atau dua-duanya? (default: ikut bahasa lowongan)

**Langkah 2 — Data diri**
- Nama lengkap, kota domisili, nomor HP, email.
- LinkedIn / portofolio / GitHub (opsional).
- Don't ask for photo, date of birth, religion, marital status, or address details.

**Langkah 3 — Pendidikan**
- Kampus/sekolah, jurusan, tahun masuk – lulus (atau perkiraan lulus).
- IPK (opsional — only include in the CV if ≥ 3.00 or the posting asks for it).
- Mata kuliah / skripsi / tugas akhir yang nyambung dengan posisi target (opsional).

**Langkah 4 — Pengalaman kerja, magang, freelance, part-time**
For each one: tempat, posisi, bulan & tahun mulai – selesai, 2–3 hal yang dikerjakan, dan hasilnya.
Helper prompts when answers are thin:
- "Tools/aplikasi apa yang dipakai?" (Excel, Canva, POS, SQL…)
- "Seberapa banyak/sering?" (berapa pelanggan per hari, berapa data, berapa laporan per minggu)
- "Ada yang jadi lebih baik karena kamu?" (lebih cepat, lebih rapi, komplain turun)
If none: "Nggak apa-apa — banyak CV fresh graduate kuat dari organisasi dan project. Lanjut ya."

**Langkah 5 — Organisasi, kepanitiaan, volunteer**
Nama organisasi/acara, peran, periode, apa yang kamu tangani, hasilnya (jumlah peserta, dana, sponsor, dll.).

**Langkah 6 — Project, lomba, bootcamp, sertifikat**
- Project kuliah/pribadi/lomba: nama, apa yang dibuat, tools, hasil/peringkat, link kalau ada.
- Kursus/bootcamp/sertifikat: nama, penyelenggara, tahun.
- Prestasi/penghargaan.

**Langkah 7 — Skill & bahasa**
- Hard skill/tools yang benar-benar pernah dipakai — and where (links each to evidence from rounds 3–6).
- Bahasa: Indonesia, Inggris (level: dasar / menengah / lancar), lainnya.
- 3–5 soft skills, each backed by something from earlier rounds.

## After the rounds

1. Show a short summary per section and ask "Ada yang salah atau kurang?" — fix before saving.
2. Rewrite their answers into CV wording (strong verb first, numbers they gave, tools named) and show the
   rewritten bullets for approval — they must recognize every line as true.
3. Save it as the profile (same JSON schema as the CV) and ask the theme (color + font) if not asked yet.
4. Offer a general CV first ("CV umum" without a specific job), or go straight to tailoring for their job link.

## Ordering tips for thin profiles

- Students / fresh graduates: summary → education → projects → organizations → experience → skills → certifications.
- Career switchers: summary → skills → projects/courses in the new field → experience (framed on transferable skills).
