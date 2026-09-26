# CV Tailor untuk Gemini (Gem)

Gemini bisa melakukan cek kecocokan, laporan gap, rencana belajar, dan menulis CV serta cover letter. Bedanya
dengan versi Claude/ChatGPT: Gemini **tidak membuat file PDF sendiri**. Gemini mengisi template CV (HTML) di
Canvas, lalu kamu klik **Save as PDF**. Desainnya tetap sama (Bronzor).

## Bikin Gem-nya (sekali saja)

1. Buka **gemini.google.com → Gems (Explore Gems) → New Gem**.
2. **Name:** `CV Tailor`.
3. **Instructions:** copy-paste seluruh isi `GEM_INSTRUCTIONS.txt`.
4. **Knowledge → tambah file:**
   - `WORKFLOW.md`
   - `cv-template.html`. Kalau file `.html` ditolak, pakai `cv-template.txt` (isinya sama).
   - **CV kamu sendiri** (PDF), supaya tidak perlu upload ulang tiap chat. Tambahkan hanya kalau Gem ini untuk
     dipakai sendiri.
   - (Opsional) Google Doc kosong bernama **"profil tambahan"**. Isi dengan fakta baru yang dikonfirmasi ke Gemini
     (skill, project, kursus) supaya Gemini ingat di chat berikutnya.
5. **Save.** Kalau mau dibagikan, gunakan fitur share Gem. Jangan sertakan CV pribadi kalau Gem-nya dibagikan.

## Belum punya CV?

Pilih **"Belum, bantu bikin dari nol"**. Gemini akan menanyakan 7 langkah singkat (target, data diri, pendidikan,
pengalaman, organisasi, project/sertifikat, skill). Di akhir, Gemini memberi teks **"PROFIL CV — simpan ini"**.
Copy teks itu, simpan sebagai `profil.txt`, lalu upload ke Gem (**Edit Gem → Informasi → +**) supaya di chat
berikutnya kamu tidak perlu diwawancara lagi.

## Cara pakai

1. Buka Gem **CV Tailor** dan tempel link lowongan. Kalau link-nya diblokir, copy-paste teks lowongan atau kirim
   screenshot.
2. Jawab pertanyaan konfirmasi skill.
3. Gemini membuka **CV di Canvas**. Klik **Save as PDF** di preview (atau Ctrl+P), lalu:
   - Destination: **Save as PDF**
   - Centang **Background graphics**
   - Matikan **Headers and footers**

   Kalau print dari Canvas tidak jalan, download atau copy kodenya, simpan sebagai `cv.html`, buka di Chrome/Edge,
   lalu klik **Save as PDF**.
4. Lakukan hal yang sama untuk **cover letter**.
5. **Tracker:** Gemini memberi satu baris tabel. Klik **Export to Sheets**, atau paste ke Google Sheet
   "Lamaran" milikmu. Kolomnya sudah disiapkan sama dengan versi Excel.

## Keterbatasan

- PDF dibuat lewat print browser. Hasilnya bisa sedikit beda antar browser; Chrome/Edge paling mirip.
- Tracker tidak otomatis tersimpan. Kamu yang menempelkan barisnya ke Google Sheet.
- Link lowongan sering tidak bisa dibuka Gemini, jadi siapkan teksnya.
