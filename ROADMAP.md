# Peta Jalan (Roadmap) Bahasa Pemrograman Indonesia

**Tujuan akhir:** bahasa pemrograman berbahasa Indonesia yang cukup lengkap untuk membuat program sungguhan, bisa dijalankan tanpa memasang Python, dan mudah dipakai anak-anak Indonesia — termasuk dari HP.

Dokumen ini melengkapi [PRD.md](PRD.md) (spesifikasi awal) dan [TASKS.md](TASKS.md) (daftar tugas rinci).

---

## Kondisi saat ini (Oktober 2026)

Yang sudah ada:
- Bahasa dengan gaya penulisan **natural** (`buat umur adalah 17`, `jika tidak, ...`, `tambahkan 1 ke skor`) dan **simbolik** (`buat umur = 17`).
- [Mesin utama dalam Go](mesin/README.md): *bytecode virtual machine* yang menjadi aplikasi satu berkas (±3 MB) dan WebAssembly untuk editor web, 8–65× lebih cepat dari interpreter Python. Interpreter Python (`src/`) tetap ada sebagai acuan perilaku.
- Pustaka standar (`matematika`, `acak`, `waktu`, `berkas`), metode teks, dan kosakata natural seperti `angka acak dari 1 sampai 6` dan `tanya "Siapa namamu?"`.
- Pesan error berbahasa Indonesia yang menunjuk baris dan kolom, lengkap dengan saran perbaikan.
- Tes otomatis (termasuk [tes kesesuaian](tes_kesesuaian/README.md)) yang berjalan di GitHub untuk Windows, macOS, dan Linux.
- [Editor di browser](web/README.md) yang bisa dipakai dari HP, juga tanpa internet; aplikasi unduhan satu berkas untuk Windows, macOS, dan Linux; serta [ekstensi VS Code](vscode/README.md).

Temuan pengujian yang menjadi dasar Tahap 1:

| Temuan | Dampak | Status |
|---|---|---|
| `impor` belum berfungsi; belum ada pustaka `acak`, `matematika`, `berkas` | Anak belum bisa membuat permainan "tebak angka" | ✅ Selesai |
| Teks belum punya metode (`huruf_besar`, `belah`, ...) | Pengolahan teks harus ditulis manual | ✅ Selesai |
| Rekursi hanya kuat ±197 tingkat; `faktorial(200)` berhenti dengan error Python berbahasa Inggris | Soal sekolah yang umum gagal dijalankan | ✅ Selesai (3.000 tingkat) |
| Salah ketik tidak diberi saran; `Jika` berhuruf besar menghasilkan pesan yang membingungkan | Pemula sulit memperbaiki kesalahannya sendiri | ✅ Selesai |
| Perulangan 1 juta kali butuh ±2,8 detik (±38× lebih lambat dari Python); pemanggilan fungsi ±215× lebih lambat | Berat untuk permainan dan animasi | ✅ Tahap 3 (mesin Go: 0,1 detik) |
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

- [x] **Editor di browser** ([web/](web/README.md)). Menulis dan menjalankan program langsung dari HP atau komputer lab sekolah, tanpa memasang apa pun. Mula-mula interpreter Python dijalankan lewat Pyodide; sejak Tahap 3 memakai mesin Go dalam WebAssembly, di dalam Web Worker.
  - `tanya`, `tunggu`, dan tombol Hentikan lewat saluran service worker, jadi bisa diterbitkan di GitHub Pages.
  - Contoh program, tombol berbagi (program di dalam tautan), draf tersimpan otomatis, dan penanda baris yang salah.
  - Bisa dibuka tanpa internet dan dipasang di layar utama HP.
  - Semua tes kesesuaian dan korpus pembanding juga dijalankan di mesin WebAssembly, ditambah 20 uji editor di Chromium.
- [x] **Aplikasi unduhan.** Satu berkas untuk Windows, macOS, dan Linux, dibuat oleh GitHub Actions ([rilis.yml](.github/workflows/rilis.yml)): mula-mula interpreter Python yang dibungkus PyInstaller, sejak Tahap 3 perintah `indonesia` dari mesin Go. Setiap aplikasi diuji dengan semua tes kesesuaian dan tes CLI sebelum terbit di halaman Releases.
- [x] **Ekstensi VS Code** ([vscode/](vscode/README.md)): pewarnaan kode, potongan kode, jorokan otomatis, dan tombol Jalankan. Grammarnya dibuat dari kosakata bahasa (`src/kosakata.py`), sama seperti pewarnaan di editor web.

Langkah yang perlu dilakukan pemilik repositori:

1. Aktifkan GitHub Pages: *Settings → Pages → Build and deployment → Source: GitHub Actions*. Editor lalu terbit di https://sofanaja44.github.io/Bahasa-Indonesia/ setiap kali `main` berubah.
2. Rilis pertama: samakan `Versi` di `mesin/api.go` (dan `VERSI` di `indonesia.py`), lalu dorong tag-nya (mis. `v0.4.0`).
3. (Pilihan) Terbitkan ekstensi di VS Code Marketplace dan Open VSX; keduanya butuh akun penerbit `sofanaja44`.

Yang bisa menyusul: ekstensi yang menjalankan program tanpa memasang aplikasi (memakai `mesin.wasm` yang sama dengan editor web), dan penandatanganan aplikasi agar Windows/macOS tidak menampilkan peringatan.

---

## Tahap 3 — Mesin mandiri, lepas dari Python

Mesin ditulis ulang dalam **Go** sebagai *bytecode virtual machine* ([mesin/](mesin/README.md)). Go dipilih karena lebih mudah dipelajari daripada Rust dan banyak dipakai di industri teknologi Indonesia, sehingga kontributor lebih mudah dicari.

- [x] **Mesin Go**: lexer, parser, kompiler *bytecode*, dan VM berbasis tumpukan. Pesan kesalahan, saran "Maksud Anda ...?", aturan angka (bilangan bulat tanpa batas, tampilan desimal), pustaka standar, sampai deret angka `acak.atur_benih` dibuat sama persis dengan interpreter Python.
- [x] **Satu file program kecil** (±3 MB) untuk Windows, macOS, dan Linux (x64 dan ARM), tanpa perlu memasang Python. Perintahnya sama: berkas, `-e`, REPL multi-baris, Ctrl+C.
- [x] **Mesin yang sama di browser**: dikompilasi ke WebAssembly untuk editor web, menggantikan Pyodide. Ukurannya jauh lebih kecil, dimuat lebih cepat, dan tombol Hentikan kini juga bekerja untuk perulangan yang tidak menampilkan apa pun.
- [x] **Jauh lebih cepat**: pemanggilan fungsi ±65×, perulangan ±26× lebih cepat dari interpreter Python ([tabel lengkap](mesin/README.md#kecepatan)). Rekursi tetap dibatasi 3.000 tingkat seperti sebelumnya, tetapi tidak lagi bergantung pada tumpukan Python.
- [x] **Terbukti sama dengan acuannya**:
  - lulus semua tes kesesuaian dan tes CLI, sebagai aplikasi maupun WebAssembly;
  - korpus pembanding 904 program (semua potongan kode dari tes Python, contoh, dan kasus tepi) yang hasilnya harus sama persis;
  - ±25.000 program acak (ekspresi dan alur kontrol) yang dibandingkan dengan interpreter Python.

Bahasa ini belum dibekukan di versi 1.0, jadi interpreter Python tetap disimpan sebagai **acuan**: perubahan perilaku dikerjakan di keduanya, dan CI gagal bila korpus pembanding tidak lagi sesuai. Beberapa perbedaan disengaja, misalnya pangkat yang selalu dibulatkan tepat dan pesan berbahasa Indonesia di tempat interpreter Python membocorkan exception mentah; daftarnya ada di [mesin/README.md](mesin/README.md#perbedaan-yang-disengaja-dengan-interpreter-python).

Yang bisa menyusul: setelah versi 1.0, interpreter Python bisa dipensiunkan dan mesin Go menjadi satu-satunya acuan.

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
