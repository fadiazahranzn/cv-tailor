# CV Tailor untuk ChatGPT

Hasilnya sama dengan versi Claude: cek kecocokan, laporan gap + rencana belajar, CV PDF, cover letter PDF, dan
tracker Excel. Semua file dibuat langsung oleh ChatGPT lewat Code Interpreter.

## Pilihan A — akun ChatGPT gratis: pakai Proyek

1. Di sidebar ChatGPT klik **Proyek → Proyek baru**, beri nama `CV Tailor`.
2. Buka menu **"…"** di pojok kanan atas proyek → **Instruksi** → copy-paste seluruh isi `INSTRUKSI-PROYEK.txt` → simpan.
3. Tab **Sumber → Tambahkan sumber**, lalu upload `cv-tailor-kit.zip` dan `knowledge/WORKFLOW.md`.
4. Mulai chat di dalam proyek, upload CV kamu (atau `cv-tailor-data.zip` dari sesi sebelumnya), lalu tempel link lowongan.
   Kalau ChatGPT bilang `cv-tailor-kit.zip` tidak ditemukan, upload juga zip itu langsung di chat.

## Pilihan B — akun berbayar: bikin Custom GPT (sekali saja)

> Membuat Custom GPT biasanya butuh akun ChatGPT berbayar. Pengguna akun gratis tetap bisa **memakai** GPT yang
> dibagikan lewat link (dengan batas pemakaian). Cek ketentuan terbaru di ChatGPT.

1. Buka **chatgpt.com → Explore GPTs → + Create → Configure**.
2. **Name:** `CV Tailor`. **Description:** "Sesuaikan CV & cover letter dengan lowongan, cek kecocokan, dan catat lamaran."
3. **Instructions:** copy-paste seluruh isi `INSTRUCTIONS.txt`.
4. **Knowledge → Upload files**, upload semua file di folder `knowledge/`:
   - `WORKFLOW.md`, `example_cv.json`
   - `render_cv.py`, `rl_render.py`, `keyword_check.py`, `tracker.py`, `data_bundle.py`
   - `SourceSerif4-*.ttf`, `Inter-*.ttf`. Kalau file `.ttf` ditolak, lewati saja: PDF tetap jadi, hanya fontnya
     berganti ke Times/Helvetica.
5. **Capabilities:** nyalakan **Code Interpreter & Data Analysis** (wajib) dan **Web Search**.
6. **Conversation starters** (opsional):
   - "Sesuaikan CV aku buat lowongan ini: "
   - "Aku belum punya CV, bantu bikin dari nol"
   - "Udah ngelamar ke mana aja?"
7. **Create →** pilih siapa yang bisa akses. Pilih **Anyone with the link** kalau mau dibagikan.

Jangan upload CV pribadi ke Knowledge kalau GPT-nya dibagikan, karena semua pengguna GPT bisa mengaksesnya.

## Cara pakai

1. Buka GPT-nya dan mulai chat baru.
2. Upload CV (PDF/DOCX), atau file `cv-tailor-data.zip` dari sesi sebelumnya.
3. Tempel link lowongan. Kalau link-nya diblokir, copy-paste teks lowongannya.
4. Jawab pertanyaan konfirmasi skill, lalu download hasilnya: CV, cover letter, `lamaran.xlsx`, dan
   **`cv-tailor-data.zip`**. Simpan zip itu dan upload lagi di chat berikutnya supaya profil dan tracker nyambung.

## Kalau ada masalah

- **GPT tidak menjalankan script / bilang file tidak ada:** pastikan Code Interpreter aktif, lalu minta
  "jalankan render_cv.py dari /mnt/data".
- **Link lowongan tidak terbaca:** paste teksnya atau kirim screenshot.
