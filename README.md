<div align="center">
  <h1>🇮🇩 Bahasa Indonesia Programming Language</h1>
  <p><strong>Bahasa pemrograman berasaskan 100% Bahasa Indonesia</strong></p>
  
  [![Status](https://img.shields.io/badge/Status-Aktif%20%28v0.3%29-success?style=for-the-badge)]()
  [![Lisensi](https://img.shields.io/badge/Lisensi-MIT-blue?style=for-the-badge)]()
  [![Python](https://img.shields.io/badge/Python-3.11%2B-yellow?style=for-the-badge&logo=python&logoColor=white)]()
  
  <p><em>"Buat kode seperti kamu bicara — sepenuhnya dalam Bahasa Indonesia."</em></p>

  <p><strong>▶️ <a href="https://sofanaja44.github.io/Bahasa-Indonesia/">Coba langsung di browser</a></strong> — tanpa memasang apa pun, juga dari HP.</p>
</div>

---

## 🌟 Mengapa Memilih Bahasa Indonesia?

**Indonesia** adalah bahasa pemrograman edukasional yang dirancang secara khusus untuk mematahkan tembok (hambatan) bahasa dalam belajar *coding*. Siapa saja yang bisa membaca dan menulis Bahasa Indonesia kini dapat memahami logika pemrograman dalam hitungan menit tanpa harus pusing memikirkan sintaks asing atau istilah Bahasa Inggris!

✨ **Fitur Utama:**
- 🗣️ **Murni Bahasa Indonesia**: Keyword, operator teks, dan fungsi dasar telah diterjemahkan secara natif.
- 🎓 **Ramah Pemula**: Sangat cocok digunakan sebagai kurikulum pertama pemrograman untuk mengenalkan konsep Logika kepada pelajar.
- 🐍 **Terinspirasi dari Python**: Mudah dikembangkan, sintaks yang bersih (clean syntax) namun amat kuat dipelajari.
- 🤝 **Dua Gaya Penulisan**: Mendukung penulisan gaya Simbolik/Matematis konvensional maupun Gaya Natural berbasis tata bahasa lisan.

---

## 💻 Sekilas Sintaks

### Opsi 1: Gaya Natural (Bercerita) 🎨
Dirancang agar penulisan program dan aplikasinya sangat alami dan mengalir bak cerita.

```id
# Program Pertama
tampilkan "Halo Dunia!"

# Mengisi nilai: "adalah" artinya sama dengan "="
buat nama adalah "Budi"
buat umur adalah 17
buat keranjang adalah ["apel", "jeruk"]

# Percabangan yang terbaca seperti kalimat
jika umur paling sedikit 17, maka tampilkan format"{nama} sudah boleh membuat KTP."
jika tidak, tampilkan format"{nama} belum boleh membuat KTP."

# Kalimat perintah
tambahkan "mangga" ke keranjang
ubah umur menjadi umur ditambah 1

# Perulangan
ulangi 3 kali, tampilkan "Hore!"

untuk setiap buah dalam keranjang, lakukan:
    tampilkan format"{nama} membeli {buah}."

jika "durian" tidak ada dalam keranjang, maka tampilkan "Durian sedang habis."
```

Program cerita yang lebih lengkap ada di [`contoh/cerita.id`](contoh/cerita.id).

### Opsi 2: Gaya Simbolik (Pengembang Modern) 🚀
Lebih ringkas dan tepat guna bagi mereka yang sudah pernah dan terbiasa mengenal pemgrograman sebelumnya.

```id
buat a = 15
buat b = 4

tampilkan format"{a} + {b} = {a + b}"
tampilkan format"{a} ** {b} = {a ** b}"

# Kondisi
jika a >= 10:
    tampilkan "Aritmatika berhasil"
```

---

## 📖 Kamus Gaya Natural

Setiap bentuk natural di bawah ini setara dengan pasangan simbolisnya, dan kedua gaya boleh dicampur dalam satu program. Kata kunci selalu ditulis dengan huruf kecil.

### Mengisi & mengubah nilai

| Gaya natural | Gaya simbolik | Catatan |
|---|---|---|
| `buat umur adalah 17` | `buat umur = 17` | Juga untuk `tetap` dan deklarasi bertipe (`bilangan umur adalah 17`) |
| `umur adalah 18` · `ubah umur menjadi 18` | `umur = 18` | `ubah ... jadi ...` juga boleh |
| `tambahkan 5 ke skor` | `skor += 5` | Jika `skor` sebuah daftar, nilainya dimasukkan ke daftar |
| `kurangi nyawa dengan 1` · `kurangi 1 dari nyawa` | `nyawa -= 1` | |
| `kalikan harga dengan 2` | `harga *= 2` | |
| `bagi total dengan 4` | `total /= 4` | |

> **Aturan `adalah`:** di awal kalimat, `adalah` berarti *mengisi nilai* (`umur adalah 18`). Di dalam kondisi, `adalah` berarti *membandingkan* (`jika umur adalah 18`), persis seperti bahasa sehari-hari.

### Perbandingan

| Gaya natural | Simbol |
|---|---|
| `adalah` · `sama dengan` | `==` |
| `bukan` · `tidak sama dengan` | `!=` |
| `lebih dari` · `lebih besar dari` | `>` |
| `kurang dari` · `lebih kecil dari` | `<` |
| `paling sedikit` · `tidak kurang dari` · `lebih dari atau sama dengan` | `>=` |
| `paling banyak` · `tidak lebih dari` · `kurang dari atau sama dengan` | `<=` |
| `angka habis dibagi 3` · `angka tidak habis dibagi 3` | `angka % 3 == 0` · `angka % 3 != 0` |
| `"apel" ada dalam keranjang` · `"apel" tidak ada dalam keranjang` | anggota / bukan anggota |

Kata `dari` juga boleh ditulis `daripada` (`lebih besar daripada`), dan `dalam` boleh ditulis `di dalam`.

### Aritmatika & logika

| Gaya natural | Simbol |
|---|---|
| `ditambah` | `+` |
| `dikurangi` · `dikurang` | `-` |
| `dikali` · `dikalikan` | `*` |
| `dibagi` | `/` |
| `sisa bagi` | `%` |
| `pangkat` · `dipangkatkan` | `**` |
| `dan` · `atau` · `bukan` / `tidak` | logika |

### Waktu

| Gaya natural | Arti |
|---|---|
| `jam sekarang` · `menit sekarang` · `detik sekarang` | angka waktu saat ini, mis. `jika jam sekarang kurang dari 11` |
| `waktu sekarang` | teks jam digital, mis. `"09:35:38"` |
| `hari ini` · `tanggal hari ini` · `bulan ini` · `tahun ini` | `"Kamis"` · `"1 Oktober 2026"` · `"Oktober"` · `2026` |
| `tunggu 1 detik` · `tunggu 500 milidetik` · `tunggu 2 menit` | berhenti sejenak (tanpa satuan berarti detik) |

### Masukan, keluaran & angka acak

| Gaya natural | Arti |
|---|---|
| `tampilkan "Halo"` | tampilkan lalu pindah baris (`tulis` juga boleh) |
| `cetak "Memuat..."` | tampilkan tanpa pindah baris |
| `buat nama adalah tanya "Siapa namamu? "` | tanyakan sesuatu kepada pengguna |
| `buat umur adalah tanya angka "Berapa umurmu? "` | tanyakan angka; diulang sampai jawabannya angka (`3,5` juga diterima) |
| `buat dadu adalah angka acak dari 1 sampai 6` | bilangan bulat acak, kedua batas termasuk |

### Alur program

| Gaya natural | Arti |
|---|---|
| `jika ... maka ...` · `kalau ...` | jika (if) |
| `atau jika ...` · `atau kalau ...` | jika tidak, periksa kondisi lain (else if) |
| `jika tidak` · `kalau tidak` · `selainnya` | selain itu (else) |
| `selama ... lakukan:` | ulangi selama kondisi benar (while) |
| `ulangi 3 kali:` | ulangi sebanyak N kali |
| `ulangi:` ... `sampai kondisi` | ulangi sampai kondisi terpenuhi |
| `untuk setiap buah dalam keranjang, lakukan:` | telusuri setiap isi daftar, kamus, atau teks |
| `pilih hari:` ... `ketika "Sabtu" atau "Minggu":` | cocok dengan salah satu nilai (untuk angka/teks boleh pakai koma: `ketika 1, 2:`) |
| `induk.inisialisasi(...)` | panggil metode kelas induk (`super` juga boleh) |

Tanda `:` di akhir kepala blok boleh diganti atau dilengkapi dengan `maka` / `lakukan`, boleh didahului koma, dan perintah yang pendek boleh ditulis di baris yang sama:

```id
buat hujan adalah benar
jika hujan, maka tampilkan "Bawa payung"
jika tidak, tampilkan "Pakai topi"

buat nyawa adalah 3
selama nyawa lebih dari 0, lakukan:
    kurangi nyawa dengan 1
```

Angka desimal yang bulat ditampilkan tanpa `.0` (`10 dibagi 2` tampil `5`), dan galat pembulatan kecil disembunyikan (`0.1 ditambah 0.2` tampil `0.3`).

### Menangani kesalahan

```id
coba:
    buat hasil adalah 10 dibagi 0
tangkap KesalahanBagiNol:
    tampilkan "Tidak bisa dibagi nol!"
tangkap kesalahan:
    tampilkan "Ups:", kesalahan
akhirnya:
    tampilkan "Selesai"
```

| Penulisan | Arti |
|---|---|
| `tangkap:` | tangkap kesalahan jenis apa pun |
| `tangkap kesalahan:` | sama, dan pesannya bisa dipakai lewat variabel `kesalahan` |
| `tangkap sebagai e:` | pesannya disimpan di `e`; `e.jenis` berisi jenisnya, mis. `KesalahanNama` |
| `tangkap KesalahanBagiNol:` | hanya jenis tertentu; nama Python seperti `ZeroDivisionError` juga dikenali |
| `lempar "Umur tidak boleh negatif"` | buat kesalahan sendiri (jenisnya `KesalahanNilai`) |

Jenis kesalahan: `KesalahanSintaks`, `KesalahanNama`, `KesalahanTipe`, `KesalahanIndeks`, `KesalahanBagiNol`, `KesalahanKunci`, `KesalahanNilai`, `KesalahanBerkas`, `KesalahanTumpukan`.

---

## 📚 Pustaka Standar

Modul dimuat dengan `impor`:

```id
impor matematika
tampilkan matematika.akar(16)          # 4

dari acak impor bilangan sebagai dadu
tampilkan dadu(1, 6)
```

| Modul | Isi |
|---|---|
| `matematika` | `pi`, `e`, `akar`, `pangkat`, `mutlak`, `bulatkan(x, digit)` (pembulatan seperti di sekolah: 2.5 → 3), `bulatkan_bawah`, `bulatkan_atas`, `sinus`/`kosinus`/`tangen` (dalam **derajat**), `logaritma(x, basis=10)`, `ln`, `faktorial`, `fpb`, `kpk` |
| `acak` | `bilangan(min, maks)`, `angka()` (0 sampai di bawah 1), `pilih(daftar)`, `kocok(daftar)`, `atur_benih(n)` |
| `waktu` | `jam()`, `menit()`, `detik()`, `sekarang()`, `hari()`, `nama_bulan()`, `tahun()`, `tanggal_lengkap()`, `tunggu(detik)` |
| `berkas` | `baca(nama)`, `baca_baris(nama)`, `tulis(nama, isi)`, `tambahkan(nama, isi)`, `ada(nama)`, `hapus(nama)` |

Nama yang juga kata kunci perlu nama lain saat diimpor langsung: `dari acak impor pilih sebagai pilih_acak` (atau cukup `acak.pilih(...)`).

**Metode teks:** `panjang()`, `huruf_besar()`, `huruf_kecil()`, `huruf_awal_besar()`, `potong_spasi()`, `belah(pemisah)`, `ganti(lama, baru)`, `berisi(x)`, `diawali(x)`, `diakhiri(x)`, `cari(x)`, `balik()`, `berupa_angka()`.

**Metode daftar:** `tambahkan`, `hapus`, `hapusPosisi`, `sisipkan`, `panjang`, `urutkan`, `balik`, `cari`, `salin`, `kosongkan`, `gabung(pemisah)`.

**Metode kamus:** `kunci`, `nilai`, `pasang`, `adaKunci`, `hapusKunci`, `dapatkan(kunci, bawaan)`.

**Fungsi bawaan:** `panjang`, `jenis`, `ubah_angka`, `ubah_desimal`, `ubah_teks`, `ubah_logika`, `rentang`, `mutlak`, `maksimum`, `minimum`, `jumlah`, `diurutkan`, `dibalik`, `masukan`, `tunggu`, `Kesalahan`.

---

## 🚀 Cara Menjalankan

### 1. Langsung di browser, tanpa memasang apa pun 🌐

Buka **[editor Bahasa Indonesia](https://sofanaja44.github.io/Bahasa-Indonesia/)** di HP atau komputer, tulis program, lalu tekan **▶ Jalankan**.

- Contoh program tersedia di menu, termasuk permainan tebak angka dan jam digital.
- Program bisa dibagikan lewat tautan, misalnya ke WhatsApp.
- Setelah kunjungan pertama, editor tetap bisa dibuka tanpa internet, dan di HP bisa dipasang di layar utama.

### 2. Aplikasi untuk komputer, tanpa Python 💻

Unduh aplikasinya dari [halaman Releases](https://github.com/sofanaja44/Bahasa-Indonesia/releases). Satu berkas kecil (±3 MB), tidak perlu memasang apa pun, dan puluhan kali lebih cepat dari versi Python ([mesin Go](mesin/README.md)):

| Sistem | Berkas | Menjalankan program |
|---|---|---|
| Windows | `indonesia-windows-x64.exe` (`-arm64.exe` untuk laptop ARM) | `indonesia-windows-x64.exe program.id` |
| macOS (Apple Silicon) | `indonesia-macos-arm64` (`-x64` untuk Mac Intel) | `chmod +x indonesia-macos-arm64`, lalu `./indonesia-macos-arm64 program.id` |
| Linux | `indonesia-linux-x64` (`-arm64` untuk Raspberry Pi 64-bit) | `chmod +x indonesia-linux-x64`, lalu `./indonesia-linux-x64 program.id` |

- Tanpa nama berkas, aplikasinya membuka mode interaktif.
- Agar bisa dipanggil dari folder mana saja (dan dipakai ekstensi VS Code), ganti namanya menjadi `indonesia` (`indonesia.exe` di Windows) dan letakkan di folder yang ada di PATH.
- Aplikasinya belum ditandatangani, sehingga bisa muncul peringatan:
  - Windows: klik *More info → Run anyway*.
  - macOS: jalankan sekali `xattr -d com.apple.quarantine indonesia-macos-arm64`.

**VS Code:** ekstensi `bahasa-indonesia.vsix` (juga di halaman Releases) menambahkan pewarnaan kode, potongan kode, dan tombol ▶ Jalankan. Pasang lewat *Extensions → ⋯ → Install from VSIX...*

### 3. Dari kode sumber

**Dengan Go 1.22+** (mesin utama):
```bash
cd mesin && go build -o bin/ ./cmd/indonesia
bin/indonesia ../contoh/tebak_angka.id
```

**Dengan Python 3.11+** (interpreter acuan, perilakunya sama):

1. **Jalankan program dari file `.id`:**
```bash
python indonesia.py contoh/demo_lengkap.id
python indonesia.py contoh/cerita.id      # program bergaya bercerita
python indonesia.py contoh/jam_digital.id # jam digital yang berdetak setiap detik
python indonesia.py contoh/tebak_angka.id # permainan tebak angka
```

2. **Gunakan Mode Interaktif (REPL) langsung di Terminal:**
```bash
python indonesia.py repl
```
Blok seperti `jika`, `selama`, atau `fungsi` boleh ditulis beberapa baris; akhiri dengan baris kosong.

3. **Lihat Menu Bantuan Lainnya:**
```bash
python indonesia.py bantu
```

---

## 📂 Struktur Repositori Terorganisasi

Proyek ini tertata rapi agar sistem dapat dirombak dan dibaca oleh para kontributor secara mudah.

```
indonesia-v1/
├── mesin/            # Mesin utama dalam Go: VM bytecode, perintah indonesia, WebAssembly (mesin/README.md)
├── src/              # Interpreter acuan dalam Python (Lexer, Parser, Ast, Evaluate, pustaka standar)
├── web/              # Editor di browser (mesin Go dalam WebAssembly), lihat web/README.md
├── vscode/           # Ekstensi VS Code
├── tests/            # Unit test dengan `pytest`
├── tes_kesesuaian/   # Spesifikasi bahasa yang bisa dijalankan (program .id + keluaran yang diharapkan)
├── contoh/           # Himpunan program-program contoh (File berekstensi .id) 
├── indonesia.py      # Entry point CLI Utama (Pengeksekusi kode program)
├── ROADMAP.md        # Rencana pengembangan
└── requirements.txt  # Dependencies eksternal yang dibutuhkan
```

---

## 🛠️ Pengembangan (Untuk Developer)

Tertarik dalam mengembangkan dan berkontribusi terhadap arsitektur bahasanya? Prosedur tes perubahannya sangat mutakhir!

```bash
# Clone proyek dan masuk ke dalam folder repositori
git clone https://github.com/sofanaja44/Bahasa-Indonesia.git
cd Bahasa-Indonesia

# Install dependencies yang esensial (seperti pytest)
pip install -r requirements.txt

# Pastikan modifikasi Anda telah aman dengan menjalankan tes hingga Passed
python -m pytest tests/ -v
```

Perilaku bahasa dijaga oleh [tes kesesuaian](tes_kesesuaian/README.md); fitur baru sebaiknya disertai tes di sana. Rencana pengembangan ada di [ROADMAP.md](ROADMAP.md).

```bash
# Mesin Go (butuh Go 1.22+): tes unit dan korpus pembanding dengan interpreter Python
cd mesin && go test ./...
go build -o bin/ ./cmd/indonesia && cd ..
MESIN_INDONESIA=mesin/bin/indonesia python -m pytest tests/test_kesesuaian.py tests/test_cli.py

# Editor web (butuh Go): bangun, lalu buka http://localhost:8000
python web/bangun.py --sajikan

# Tes editor web dan ekstensi VS Code (butuh Node.js)
cd web && npm ci && node tes/tes_mesin.mjs && node --test tes/tes_editor.mjs
cd vscode && npm ci && node --test tes/tes_grammar.mjs
```

- **Mengubah perilaku bahasa:** ubah interpreter acuan (`src/`) dan mesin Go (`mesin/`) bersama-sama, lalu jalankan `python mesin/testdata/buat_korpus.py` untuk memperbarui korpus pembanding. Tes Go gagal bila keduanya berbeda. Penjelasannya ada di [mesin/README.md](mesin/README.md).
- **Setelah mengubah kata kunci** di `src/token_types.py`, jalankan `python vscode/bangun.py` agar pewarnaan di VS Code ikut berubah. Tesnya akan mengingatkan bila lupa. Editor web mengikutinya otomatis.
- **Rilis baru:** samakan `Versi` di `mesin/api.go` (dan `VERSI` di `indonesia.py`), lalu dorong tag-nya, misalnya `git tag v0.4.0 && git push origin v0.4.0`. GitHub Actions membuat aplikasi untuk Windows, macOS, dan Linux beserta ekstensi VS Code, mengujinya, lalu menerbitkannya di halaman Releases.
- **Editor web** diterbitkan otomatis ke GitHub Pages setiap kali `main` berubah. Sekali saja sebelumnya: *Settings → Pages → Source: GitHub Actions*.

---

## 📜 Lisensi & Kontribusi

Proyek ini disebarluaskan dengan Lisensi [MIT](LICENSE) secara 100% terbuka *(Open-Source)*. 
Kami **sangat menyambut** berbagai permintaan *Pull Request* kontribusi, perbaikan bug, penyempurnaan gramatika, pembuatan library standar, atau rekomendasi fitur demi mendorong pendidikan pemrograman bangsa ini kedepannya! 

<br>

> *Mari memajukan anak bangsa, dimulai dari menyusun barisan algoritma kode dalam bahasa negara mereka sendiri.* 🇮🇩
