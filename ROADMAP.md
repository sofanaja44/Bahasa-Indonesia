# Peta Jalan (Roadmap) Bahasa Pemrograman Indonesia

**Tujuan akhir:** bahasa pemrograman berbahasa Indonesia yang cukup lengkap untuk membuat program sungguhan, bisa dijalankan tanpa memasang Python, dan mudah dipakai anak-anak Indonesia — termasuk dari HP.

Dokumen ini melengkapi [PRD.md](PRD.md) (spesifikasi awal) dan [TASKS.md](TASKS.md) (daftar tugas rinci).

---

## Kondisi saat ini (Oktober 2026)

Yang sudah ada:
- Interpreter di Python 3.11+ (lexer → parser → interpreter) dengan gaya penulisan **natural** (`buat umur adalah 17`, `jika tidak, ...`, `tambahkan 1 ke skor`) dan **simbolik** (`buat umur = 17`).
- Pustaka standar (`matematika`, `acak`, `waktu`, `berkas`), metode teks, dan kosakata natural seperti `angka acak dari 1 sampai 6` dan `tanya "Siapa namamu?"`.
- Pesan error berbahasa Indonesia yang menunjuk baris dan kolom, lengkap dengan saran perbaikan.
- Tes otomatis (termasuk [tes kesesuaian](tes_kesesuaian/README.md)) yang berjalan di GitHub untuk Windows, macOS, dan Linux.

Temuan pengujian yang menjadi dasar Tahap 1:

| Temuan | Dampak | Status |
|---|---|---|
| `impor` belum berfungsi; belum ada pustaka `acak`, `matematika`, `berkas` | Anak belum bisa membuat permainan "tebak angka" | ✅ Selesai |
| Teks belum punya metode (`huruf_besar`, `belah`, ...) | Pengolahan teks harus ditulis manual | ✅ Selesai |
| Rekursi hanya kuat ±197 tingkat; `faktorial(200)` berhenti dengan error Python berbahasa Inggris | Soal sekolah yang umum gagal dijalankan | ✅ Selesai (3.000 tingkat) |
| Salah ketik tidak diberi saran; `Jika` berhuruf besar menghasilkan pesan yang membingungkan | Pemula sulit memperbaiki kesalahannya sendiri | ✅ Selesai |
| Perulangan 1 juta kali butuh ±2,8 detik (±38× lebih lambat dari Python); pemanggilan fungsi ±215× lebih lambat | Berat untuk permainan dan animasi | ⏳ Tahap 3 |
| README menyebut lisensi MIT tetapi file `LICENSE` belum ada; belum ada tes otomatis di GitHub | Menghambat adopsi oleh sekolah dan kontributor | ✅ Selesai |

---

## Tahap 1 — Lengkapi bahasanya (masih di Python)

Selama tata bahasa masih sering berubah, Python adalah tempat paling cepat untuk bereksperimen.

- [x] **Pustaka standar** dan `impor` yang benar-benar memuat modul: `matematika`, `acak`, `waktu`, `berkas`, serta metode teks.
- [x] **Batas rekursi**: rekursi dalam tidak lagi berhenti di ±197 tingkat; rekursi tak berujung menghasilkan pesan berbahasa Indonesia.
- [x] **Tidak ada lagi error Python mentah**: semua kesalahan tampil dalam bahasa Indonesia.
- [x] **Pesan error yang membimbing**: saran "Maksud Anda 'nama'?", petunjuk bahwa kata kunci ditulis huruf kecil, petunjuk memakai `buat`.
- [x] **REPL multi-baris**: mode interaktif bisa menerima blok `jika`, `selama`, `fungsi`.
- [x] **Keputusan desain** yang sudah disepakati (lihat bagian Keputusan Desain).
- [x] **File `LICENSE`** dan **tes otomatis di GitHub** (Windows, macOS, Linux).
- [x] **Tes kesesuaian**: pasangan program `.id` dan keluaran yang diharapkan, tidak bergantung pada Python. Ini menjadi spesifikasi resmi bahasa untuk Tahap 3. Perlu terus ditambah seiring fitur baru.
- [x] **Contoh permainan** "tebak angka" (`contoh/tebak_angka.id`).

Selesai bila: semua butir di atas tercentang dan bahasa diberi versi **1.0** (tata bahasa dibekukan; perubahan selanjutnya harus kompatibel). Semua butir sudah selesai; yang tersisa adalah keputusan kapan menetapkan versi 1.0.

---

## Tahap 2 — Bisa dipakai tanpa memasang Python

- [ ] **Aplikasi unduhan.** Interpreter dibungkus menjadi `indonesia.exe` (Windows) serta versi macOS dan Linux memakai PyInstaller, dibuat otomatis oleh GitHub Actions dan dipasang di halaman Releases. Pengguna cukup unduh dan jalankan.
- [ ] **Editor di browser.** Menulis dan menjalankan program langsung dari HP atau komputer lab sekolah, tanpa memasang apa pun. Interpreter yang ada dijalankan di browser lewat Pyodide (Python dalam WebAssembly). Dilengkapi contoh program dan tombol berbagi.
- [ ] **Ekstensi VS Code**: pewarnaan kode, potongan kode (snippet), dan tombol jalankan.

Prioritas utama tahap ini adalah editor di browser, karena banyak anak Indonesia belajar lewat HP.

---

## Tahap 3 — Mesin mandiri, lepas dari Python

Mesin ditulis ulang dalam **Go** sebagai *bytecode virtual machine*:

- Satu file program kecil untuk Windows, macOS, dan Linux.
- Mesin yang sama dikompilasi ke WebAssembly untuk editor di browser, sehingga desktop dan browser memakai satu mesin.
- Jauh lebih cepat dari interpreter Python saat ini, dan tanpa batas rekursi bawaan Python.
- Go lebih mudah dipelajari daripada Rust dan banyak dipakai di industri teknologi Indonesia, sehingga kontributor lebih mudah dicari.

Syarat memulai: bahasa sudah versi 1.0 dan tes kesesuaian dari Tahap 1 sudah lengkap. Mesin Go dianggap benar bila lulus semua tes kesesuaian yang sama. Jika ditulis ulang sebelum tata bahasa stabil, setiap fitur baru harus dikerjakan dua kali.

---

## Ekosistem untuk anak-anak

- [ ] **Mode gambar "kura-kura"** seperti Logo dan Scratch: `maju 100`, `belok kanan 90`, `ganti warna pena menjadi "merah"`. Hasilnya langsung terlihat dan cocok dengan gaya bercerita.
- [ ] **Pelajaran bertahap** dalam bahasa Indonesia, dari "Halo Dunia" sampai membuat permainan.
- [ ] **Kumpulan contoh permainan**: tebak angka, kuis, cerita interaktif, jam digital.
- [ ] **Panduan untuk guru** dan situs dokumentasi.
- [ ] **Komunitas**: GitHub Discussions dan panduan kontribusi (`CONTRIBUTING.md`).

---

## Keputusan desain

| Topik | Keputusan |
|---|---|
| `adalah` | Di awal kalimat berarti mengisi nilai (`umur adalah 18`); di dalam kondisi berarti membandingkan (`jika umur adalah 18`). |
| Kata kerja natural | `ubah`, `tambahkan`, `kurangi`, `kalikan`, `bagi`, `tunggu` tidak dicadangkan, sehingga tetap boleh menjadi nama fungsi atau variabel. |
| `ketika` dengan beberapa nilai | `ketika "Sabtu" atau "Minggu":` dan `ketika "Sabtu", "Minggu":` cocok dengan salah satu nilainya. |
| Tampilan angka desimal | Desimal bulat tampil tanpa `.0`: `10 dibagi 2` tampil `5`; `2.5` tetap `2.5`. Desimal ditampilkan sampai 12 angka penting, sehingga `0.1 ditambah 0.2` tampil `0.3`. |
| Masukan angka | `tanya angka` mengulang pertanyaan sampai jawabannya angka; koma desimal ala Indonesia (`3,5`) diterima. |
| Versi Python | Minimal Python 3.11: sejak versi ini, rekursi dalam tidak membebani tumpukan C, sehingga aman juga di Windows. |
| `cetak` | Mencetak tanpa pindah baris (sesuai PRD); `tampilkan` pindah baris. |
| Huruf besar pada kata kunci | Kata kunci tetap ditulis huruf kecil; pesan error memberi petunjuk bila tertulis `Jika` atau `Tampilkan`. |
| Batas rekursi | Paling dalam 3.000 panggilan fungsi bertumpuk; lebih dari itu dianggap rekursi tak berujung (`KesalahanTumpukan`). |
