# cv-tailor

Asisten lamaran kerja untuk Claude. Kirim link atau teks lowongan, lalu kamu dapat:

- **Cek kecocokan**: fit score 0–100 dan saran *Lamar / Lamar dengan catatan / Pertimbangkan skip*
- **Laporan gap** dan **rencana belajar** (kursus + mini-project) untuk skill yang belum ada
- **CV PDF** yang disesuaikan dengan keyword lowongan, desain ala Reactive Resume "Bronzor"
- **Cover letter PDF** dengan desain yang sama
- **Tracker lamaran** dalam bentuk Excel (`lamaran.xlsx`)

Isi CV selalu diambil dari datamu sendiri. Skill ini tidak pernah menambahkan skill atau pengalaman yang tidak kamu punya.

## Pasang di claude.ai (bisa pakai akun Free)

1. Buka **Settings → Capabilities** dan pastikan **Code execution** aktif.
2. Buka **Customize → Skills → + → Upload a skill**, lalu upload `cv-tailor-skill.zip`.
3. Buka chat baru, upload CV kamu (PDF/DOCX), lalu tempel link lowongan.
   Contoh: "tolong sesuaikan CV aku buat lowongan ini: <link>"
4. Di akhir chat, **download `cv-tailor-data.zip`** dan simpan baik-baik. Di chat berikutnya, upload file itu lagi
   supaya profil, tracker, dan rencana belajar kamu tetap nyambung.

Catatan: situs seperti Glints, JobStreet, dan LinkedIn sering memblokir akses dari Claude. Kalau link-nya
tidak terbaca, copy-paste saja teks lowongannya.

## Pasang di Claude Code (butuh paket Pro/Max atau API key)

```bash
unzip cv-tailor-skill.zip -d ~/.claude/skills/
pip install jinja2 pymupdf openpyxl
npx playwright install chromium-headless-shell   # PDF paling rapi (opsional, ada fallback ReportLab)
```
Setelah itu jalankan `/cv-tailor <link lowongan>`. Data kamu tersimpan permanen di `~/.cv-tailor/`.

## Pasang di Codex, Antigravity, atau Gemini CLI

Formatnya sama (`SKILL.md`), cukup taruh folder `cv-tailor` di lokasi skill masing-masing:

| Tool | Lokasi folder |
|---|---|
| Codex | `~/.agents/skills/cv-tailor/` |
| Antigravity | `~/.gemini/antigravity/skills/cv-tailor/` (global) atau `<project>/.agents/skills/cv-tailor/` |
| Gemini CLI | `~/.gemini/skills/cv-tailor/` |

Lalu install library Python: `pip install jinja2 pymupdf openpyxl reportlab pypdf`.
Untuk PDF paling rapi, pakai Chrome atau Edge yang sudah terpasang (terdeteksi otomatis di Windows/macOS/Linux).
Kalau tidak ada, skill memakai ReportLab. Setelah itu minta ke agent-nya: "pakai skill cv-tailor, sesuaikan CV aku
untuk lowongan ini: <link>".

## Lisensi font

Source Serif 4 dan Inter dirilis di bawah SIL Open Font License 1.1 (lihat `assets/fonts/OFL-*.txt`).
