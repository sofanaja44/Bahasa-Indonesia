# TASKS.md — BahasaKode: Rencana Pengerjaan

**Proyek:** BahasaKode — Bahasa Pemrograman Indonesia  
**Versi Target Awal:** v0.1 MVP  
**Metodologi:** Iteratif, dimulai dari yang paling sederhana

---

## Cara Membaca File Ini

- `[ ]` — Belum dikerjakan  
- `[~]` — Sedang dikerjakan  
- `[x]` — Selesai  
- **🔴 Blocker** — Harus selesai sebelum task lain bisa mulai  
- **🟡 Penting** — Prioritas tinggi  
- **🟢 Opsional** — Bisa dikerjakan belakangan  

---

## FASE 0 — Persiapan & Fondasi

### 0.1 Setup Repositori
- [ ] Buat repositori Git (GitHub / GitLab)
- [ ] Setup struktur folder proyek:
  ```
  bahasakode/
  ├── src/
  │   ├── lexer.py          # Tokenizer
  │   ├── parser.py         # Parser & AST
  │   ├── interpreter.py    # Interpreter utama
  │   ├── builtins.py       # Fungsi bawaan
  │   └── errors.py         # Pesan error Indonesia
  ├── tests/                # Unit test
  ├── contoh/               # Program contoh .bk
  ├── docs/                 # Dokumentasi
  ├── README.md
  └── requirements.txt
  ```
- [ ] Setup `README.md` awal
- [ ] Pilih bahasa implementasi (Rekomendasi: **Python 3.10+**)
- [ ] Setup environment virtual Python (`venv`)
- [ ] Setup testing framework (`pytest`)

### 0.2 Definisi Token & Kata Kunci
- [ ] Buat daftar lengkap semua kata kunci Bahasa Indonesia
- [ ] Buat file `kata_kunci.py` berisi mapping kata kunci ke token internal:
  ```python
  KATA_KUNCI = {
      "buat": "DEKLARASI",
      "tetap": "KONSTANTA",
      "jika": "JIKA",
      "atau jika": "ATAU_JIKA",
      "selainnya": "SELAINNYA",
      ...
  }
  ```
- [ ] Definisikan semua tipe token (ANGKA, TEKS, OPERATOR, dll)
- [ ] Dokumentasikan semua kata kunci dengan contoh penggunaan

---

## FASE 1 — Lexer (Tokenizer) 🔴 Blocker

> **Tujuan:** Ubah teks kode BahasaKode menjadi daftar token yang bisa diproses parser.

### 1.1 Tokenizer Dasar
- [ ] Implementasi fungsi `tokenisasi(kode_sumber)`
- [ ] Kenali karakter angka (integer dan desimal)
- [ ] Kenali string/teks yang diapit tanda kutip `"..."` dan `'...'`
- [ ] Kenali identifier (nama variabel/fungsi)
- [ ] Kenali semua operator: `+`, `-`, `*`, `/`, `%`, `**`, `=`, `==`, `!=`, `>`, `<`, `>=`, `<=`
- [ ] Kenali tanda baca: `:`, `(`, `)`, `[`, `]`, `{`, `}`, `,`, `.`

### 1.2 Kata Kunci Multi-Kata
- [ ] Handle kata kunci dua kata: `atau jika`, `untuk setiap`, `tidak sama dengan`, dll
- [ ] Prioritaskan pencocokan kata kunci panjang sebelum yang pendek

### 1.3 Komentar
- [ ] Skip komentar satu baris mulai `#`
- [ ] Skip komentar multi-baris `"""..."""`

### 1.4 Pelacakan Posisi
- [ ] Lacak nomor baris dan kolom setiap token (untuk pesan error)
- [ ] Simpan info posisi di setiap token object

### 1.5 Test Lexer
- [ ] Unit test: tokenisasi angka
- [ ] Unit test: tokenisasi teks/string
- [ ] Unit test: tokenisasi operator
- [ ] Unit test: tokenisasi kata kunci
- [ ] Unit test: tokenisasi kata kunci multi-kata
- [ ] Unit test: komentar diabaikan dengan benar
- [ ] Unit test: error pada karakter tidak dikenal

---

## FASE 2 — Parser & AST 🔴 Blocker

> **Tujuan:** Ubah daftar token menjadi Abstract Syntax Tree (AST) yang merepresentasikan struktur program.

### 2.1 Definisi Node AST
- [ ] Buat kelas-kelas node AST:
  - `NodeProgram` — root program
  - `NodeDeklarasiVariabel` — `buat x = 5`
  - `NodeKonstanta` — `tetap PI = 3.14`
  - `NodePenugasan` — `x = 10`
  - `NodeAngka` — literal angka
  - `NodeTeks` — literal string
  - `NodeLogika` — `benar` / `salah`
  - `NodeKosong` — nilai null
  - `NodeIdentifier` — nama variabel/fungsi
  - `NodeOperasiBiner` — `a + b`, `x == y`
  - `NodeOperasiUnari` — `bukan x`, `-5`
  - `NodeBlokKode` — blok indentasi
  - `NodeJika` — kondisi if/else
  - `NodePilih` — switch/case
  - `NodeSelama` — while loop
  - `NodeUntuk` — for range loop
  - `NodeUntukSetiap` — for each loop
  - `NodeUlangi` — do-while loop
  - `NodeFungsi` — definisi fungsi
  - `NodePanggilFungsi` — pemanggilan fungsi
  - `NodeKembalikan` — return statement
  - `NodeBerhenti` — break
  - `NodeLewati` — continue
  - `NodeDaftar` — list/array literal
  - `NodeKamus` — dictionary literal
  - `NodeAksesDaftar` — `daftar[0]`
  - `NodeAksesAtribut` — `obj.atribut`
  - `NodeKelas` — definisi kelas
  - `NodeImpor` — import modul
  - `NodeTampilkan` — print statement
  - `NodeMasukan` — input statement
  - `NodeCoba` — try/except
  - `NodeLempar` — throw/raise

### 2.2 Parser Ekspresi
- [ ] Parse literal: angka, teks, benar/salah, kosong
- [ ] Parse identifier (nama variabel)
- [ ] Parse ekspresi dalam kurung `(a + b)`
- [ ] Parse operasi aritmatika dengan preseden operator yang benar (kali/bagi sebelum tambah/kurang)
- [ ] Parse operasi perbandingan (`==`, `!=`, `>`, `<`, `>=`, `<=`)
- [ ] Parse operasi logika (`dan`, `atau`, `bukan`)
- [ ] Parse pemanggilan fungsi `nama_fungsi(arg1, arg2)`
- [ ] Parse akses daftar `daftar[indeks]`
- [ ] Parse akses atribut `objek.atribut`
- [ ] Parse ekspresi format teks `f"Halo {nama}"`
- [ ] Parse literal daftar `[1, 2, 3]`
- [ ] Parse literal kamus `{"kunci": "nilai"}`

### 2.3 Parser Pernyataan (Statement)
- [ ] Parse deklarasi variabel `buat x = ekspresi`
- [ ] Parse konstanta `tetap X = ekspresi`
- [ ] Parse penugasan `x = ekspresi`
- [ ] Parse penugasan gabungan `x += 1`, `x -= 1`, dll
- [ ] Parse blok kode berbasis indentasi
- [ ] Parse `jika / atau jika / selainnya`
- [ ] Parse `pilih / ketika / bawaan`
- [ ] Parse `selama` (while)
- [ ] Parse `untuk ... dari ... sampai` (for range)
- [ ] Parse `untuk setiap ... dalam` (for each)
- [ ] Parse `ulangi ... selama` (do-while)
- [ ] Parse `berhenti` dan `lewati`
- [ ] Parse definisi fungsi `fungsi nama(param): ...`
- [ ] Parse `kembalikan ekspresi`
- [ ] Parse definisi kelas `kelas Nama: ...`
- [ ] Parse pewarisan `kelas Anak mewarisi Induk`
- [ ] Parse `impor` dan `dari ... impor`
- [ ] Parse `tampilkan`, `cetak`, `tulis`
- [ ] Parse `masukan`, `masukan_angka`, `masukan_desimal`
- [ ] Parse `coba / tangkap / akhirnya`
- [ ] Parse `lempar`
- [ ] Parse `ada dalam` (in operator)

### 2.4 Test Parser
- [ ] Unit test setiap jenis node AST
- [ ] Unit test preseden operator
- [ ] Unit test nested conditions
- [ ] Unit test nested loops
- [ ] Unit test definisi kelas dengan pewarisan
- [ ] Unit test pesan error untuk sintaks tidak valid

---

## FASE 3 — Interpreter 🔴 Blocker

> **Tujuan:** Jalan-kan AST dengan mengeksekusi setiap node secara rekursif.

### 3.1 Environment & Scope
- [ ] Implementasi kelas `Lingkungan` (Environment/Scope)
- [ ] Support nested scope (scope dalam fungsi, kelas, dll)
- [ ] Implementasi pencarian variabel dari scope terdalam ke terluar
- [ ] Implementasi scope global vs lokal

### 3.2 Evaluasi Ekspresi
- [ ] Evaluasi literal (angka, teks, logika, kosong)
- [ ] Evaluasi identifier (lookup variabel)
- [ ] Evaluasi operasi aritmatika
- [ ] Evaluasi operasi perbandingan
- [ ] Evaluasi operasi logika (`dan`, `atau`, `bukan`)
- [ ] Evaluasi pemanggilan fungsi
- [ ] Evaluasi akses daftar dengan indeks (positif dan negatif)
- [ ] Evaluasi akses atribut
- [ ] Evaluasi format teks `f"...{ekspresi}..."`
- [ ] Evaluasi literal daftar
- [ ] Evaluasi literal kamus
- [ ] Evaluasi operator `ada dalam`

### 3.3 Eksekusi Pernyataan
- [ ] Eksekusi deklarasi variabel
- [ ] Eksekusi penugasan
- [ ] Eksekusi blok kode
- [ ] Eksekusi kondisi `jika/atau jika/selainnya`
- [ ] Eksekusi `pilih/ketika/bawaan`
- [ ] Eksekusi `selama`
- [ ] Eksekusi `untuk ... dari ... sampai` (with langkah optional)
- [ ] Eksekusi `untuk setiap ... dalam`
- [ ] Eksekusi `ulangi ... selama`
- [ ] Handle `berhenti` (break) — keluar dari loop
- [ ] Handle `lewati` (continue) — lanjut ke iterasi berikutnya
- [ ] Eksekusi definisi fungsi (simpan ke environment)
- [ ] Eksekusi pemanggilan fungsi dengan argument
- [ ] Handle nilai default parameter fungsi
- [ ] Eksekusi `kembalikan`
- [ ] Eksekusi definisi kelas
- [ ] Eksekusi instansiasi kelas (`buat obj = NamaKelas(...)`)
- [ ] Eksekusi `impor` — muat modul
- [ ] Eksekusi `coba/tangkap/akhirnya`
- [ ] Eksekusi `lempar`

### 3.4 Tipe Data Native
- [ ] Implementasi tipe `Daftar` dengan semua method:
  - `tambahkan(item)` — append
  - `hapus(item)` — remove by value
  - `hapusPosisi(indeks)` — remove by index
  - `sisipkan(indeks, item)` — insert
  - `panjang()` — len
  - `urutkan()` — sort
  - `balik()` — reverse
  - `cari(item)` — index of
  - `salin()` — copy
  - `kosongkan()` — clear
- [ ] Implementasi tipe `Kamus` dengan semua method:
  - `kunci()` — keys
  - `nilai()` — values
  - `pasang()` — items
  - `adaKunci(kunci)` — contains key
  - `hapusKunci(kunci)` — pop/delete key
  - `dapatkan(kunci, default)` — get with default
- [ ] Implementasi operasi slice daftar `[awal:akhir]`
- [ ] Implementasi konkatenasi string (`+` antar teks)
- [ ] Implementasi penggandaan string (`teks * angka`)

### 3.5 Fungsi Bawaan (Built-in)
- [ ] `tampilkan(*args)` — print ke stdout
- [ ] `cetak(*args)` — print tanpa newline
- [ ] `tulis(*args)` — sinonim tampilkan
- [ ] `masukan(prompt)` — input string
- [ ] `masukan_angka(prompt)` — input integer
- [ ] `masukan_desimal(prompt)` — input float
- [ ] `panjang(x)` — len
- [ ] `jenis(x)` — type name dalam Bahasa Indonesia
- [ ] `ubah_angka(x)` — int()
- [ ] `ubah_desimal(x)` — float()
- [ ] `ubah_teks(x)` — str()
- [ ] `ubah_logika(x)` — bool()
- [ ] `rentang(awal, akhir, langkah)` — range
- [ ] `mutlak(x)` — abs()
- [ ] `maksimum(*args)` — max()
- [ ] `minimum(*args)` — min()
- [ ] `jumlah(daftar)` — sum()
- [ ] `diurutkan(daftar)` — sorted()
- [ ] `dibalik(daftar)` — reversed()

### 3.6 Test Interpreter
- [ ] Integration test: program "Halo Dunia"
- [ ] Integration test: kalkulator sederhana
- [ ] Integration test: fibonacci dengan loop
- [ ] Integration test: operasi daftar
- [ ] Integration test: operasi kamus
- [ ] Integration test: fungsi rekursif
- [ ] Integration test: OOP sederhana
- [ ] Integration test: penanganan error

---

## FASE 4 — Pesan Error Bahasa Indonesia

> **Tujuan:** Semua pesan error harus dalam Bahasa Indonesia yang ramah dan informatif.

### 4.1 Kelas Error
- [ ] `KesalahanSintaks` — SyntaxError
- [ ] `KesalahanNama` — NameError (variabel tidak ditemukan)
- [ ] `KesalahanTipe` — TypeError
- [ ] `KesalahanIndeks` — IndexError
- [ ] `KesalahanBagiNol` — ZeroDivisionError
- [ ] `KesalahanBerkas` — FileNotFoundError
- [ ] `KesalahanKunci` — KeyError
- [ ] `KesalahanNilai` — ValueError
- [ ] `KesalahanTumpukan` — StackOverflowError (rekursi terlalu dalam)

### 4.2 Format Pesan Error
- [ ] Setiap error harus menampilkan:
  - Nomor baris dan kolom
  - Potongan kode yang bermasalah
  - Penjelasan masalah dalam Bahasa Indonesia
  - Saran perbaikan (jika memungkinkan)
- [ ] Contoh format:
  ```
  ❌ Kesalahan Sintaks pada baris 5, kolom 3:
     
     buat hasil = 10 /
                     ^
  Tanda '/' membutuhkan nilai di sebelah kanannya.
  Saran: Tambahkan angka atau variabel setelah tanda '/'.
  ```

### 4.3 Test Pesan Error
- [ ] Test setiap jenis error menghasilkan pesan Bahasa Indonesia
- [ ] Test format error menampilkan baris yang benar

---

## FASE 5 — Modul Standar

### 5.1 Modul `matematika`
- [ ] `matematika.pi` — nilai π
- [ ] `matematika.e` — bilangan Euler
- [ ] `matematika.akar(x)` — sqrt
- [ ] `matematika.pangkat(x, n)` — power
- [ ] `matematika.mutlak(x)` — abs
- [ ] `matematika.lantai(x)` — floor
- [ ] `matematika.langit(x)` — ceil
- [ ] `matematika.bulatkan(x, n)` — round
- [ ] `matematika.sinus(x)`, `matematika.kosinus(x)`, `matematika.tangen(x)`
- [ ] `matematika.logaritma(x)`, `matematika.log10(x)`
- [ ] `matematika.faktorial(n)`

### 5.2 Modul `acak`
- [ ] `acak.angka()` — random float 0-1
- [ ] `acak.bilangan(min, maks)` — random int
- [ ] `acak.pilih(daftar)` — random choice
- [ ] `acak.kocok(daftar)` — shuffle
- [ ] `acak.atur_benih(n)` — seed

### 5.3 Modul `waktu`
- [ ] `waktu.sekarang()` — current datetime
- [ ] `waktu.hari_ini()` — current date
- [ ] `waktu.timestamp()` — unix timestamp
- [ ] `waktu.tidur(detik)` — sleep
- [ ] `waktu.format(waktu, format)` — format datetime

### 5.4 Modul `berkas`
- [ ] `berkas.baca(nama_file)` — read file
- [ ] `berkas.tulis(nama_file, isi)` — write file
- [ ] `berkas.tambah(nama_file, isi)` — append to file
- [ ] `berkas.ada(nama_file)` — file exists
- [ ] `berkas.hapus(nama_file)` — delete file
- [ ] `berkas.daftar_isi(folder)` — list directory

### 5.5 Modul `teks`
- [ ] `teks.huruf_besar(t)` — upper
- [ ] `teks.huruf_kecil(t)` — lower
- [ ] `teks.potong_spasi(t)` — strip
- [ ] `teks.belah(t, pemisah)` — split
- [ ] `teks.gabung(pemisah, daftar)` — join
- [ ] `teks.ganti(t, lama, baru)` — replace
- [ ] `teks.mulai_dengan(t, awalan)` — startswith
- [ ] `teks.akhir_dengan(t, akhiran)` — endswith
- [ ] `teks.ada_dalam(t, sub)` — contains
- [ ] `teks.panjang(t)` — len
- [ ] `teks.temukan(t, sub)` — find/index

### 5.6 Modul `json`
- [ ] `json.urai(teks_json)` — parse JSON string
- [ ] `json.encode(objek)` — encode to JSON string
- [ ] `json.baca_berkas(nama_file)` — read JSON file
- [ ] `json.tulis_berkas(nama_file, objek)` — write JSON file

---

## FASE 6 — CLI (Command Line Interface)

### 6.1 Perintah `bk`
- [ ] `bk namafile.bk` — jalankan file
- [ ] `bk repl` — masuk mode interaktif
- [ ] `bk bantu` — tampilkan bantuan
- [ ] `bk versi` — tampilkan versi
- [ ] `bk periksa namafile.bk` — cek sintaks tanpa jalankan
- [ ] `bk buat proyek nama` — scaffold proyek baru

### 6.2 Mode REPL
- [ ] Prompt interaktif `>> `
- [ ] Evaluasi ekspresi satu baris langsung
- [ ] Handle input multi-baris (blok kode)
- [ ] History perintah (up/down arrow)
- [ ] Perintah khusus REPL: `.keluar`, `.bersih`, `.bantu`
- [ ] Tampilkan hasil ekspresi secara otomatis

### 6.3 Test CLI
- [ ] Test jalankan file `.bk`
- [ ] Test deteksi file tidak ditemukan
- [ ] Test flag `--bantu`
- [ ] Test flag `--versi`

---

## FASE 7 — Dokumentasi

### 7.1 Dokumentasi Bahasa
- [ ] Panduan memulai (Getting Started) — 5 menit pertama
- [ ] Referensi semua kata kunci
- [ ] Referensi semua tipe data
- [ ] Referensi semua operator
- [ ] Referensi semua fungsi bawaan
- [ ] Referensi semua modul standar
- [ ] Panduan OOP
- [ ] Panduan penanganan error
- [ ] FAQ dalam Bahasa Indonesia

### 7.2 Contoh Program
- [ ] Halo Dunia
- [ ] Kalkulator
- [ ] Konversi suhu (Celsius ke Fahrenheit)
- [ ] FizzBuzz
- [ ] Fibonacci
- [ ] Faktorial (rekursif dan iteratif)
- [ ] Cek bilangan prima
- [ ] Daftar belanja interaktif
- [ ] Buku nilai siswa
- [ ] Permainan tebak angka
- [ ] Sorting sederhana
- [ ] Manajemen data dengan kamus
- [ ] Kelas Mahasiswa sederhana
- [ ] Baca dan tulis file
- [ ] Mini kalkulator OOP

### 7.3 README Proyek
- [ ] Deskripsi proyek
- [ ] Cara instalasi
- [ ] Quick start guide
- [ ] Contoh kode singkat
- [ ] Link ke dokumentasi lengkap
- [ ] Cara berkontribusi

---

## FASE 8 — Testing & QA

### 8.1 Unit Test
- [ ] Coverage lexer minimal 90%
- [ ] Coverage parser minimal 90%
- [ ] Coverage interpreter minimal 85%
- [ ] Coverage modul standar minimal 80%

### 8.2 Integration Test
- [ ] Jalankan semua contoh program — harus sukses tanpa error
- [ ] Test semua pesan error muncul dengan benar
- [ ] Test edge cases: string kosong, daftar kosong, angka negatif, dll
- [ ] Test program besar (>100 baris)

### 8.3 Compatibility Test
- [ ] Test di Windows
- [ ] Test di macOS
- [ ] Test di Linux

---

## FASE 9 — Rilis v0.1

- [ ] Finalisasi semua fitur MVP
- [ ] Semua test lulus
- [ ] Dokumentasi dasar lengkap
- [ ] Buat release package (installer/pip package)
- [ ] Upload ke GitHub dengan release notes
- [ ] Buat demo video singkat

---

## FASE 10 — Fitur Lanjutan (Post-MVP)

### Editor Online 🟡
- [ ] Web-based IDE dengan syntax highlighting
- [ ] Run kode langsung di browser
- [ ] Simpan dan share kode
- [ ] Contoh program yang bisa dicoba langsung

### VS Code Extension 🟡
- [ ] Syntax highlighting untuk `.bk`
- [ ] Autocomplete kata kunci
- [ ] Error squiggles
- [ ] Code snippets untuk konstruk umum
- [ ] Run file dari VS Code

### Paket/Library Manager 🟢
- [ ] Sistem paket sederhana
- [ ] Repositori paket komunitas
- [ ] Perintah `bk pasang nama-paket`

### Compiler ke Bytecode 🟢
- [ ] Desain format bytecode
- [ ] Implementasi compiler AST → bytecode
- [ ] Implementasi virtual machine
- [ ] Optimasi performa

### Transpiler ke Python 🟢
- [ ] Ubah kode `.bk` menjadi kode Python yang valid
- [ ] Berguna untuk integrasi dengan ekosistem Python yang sudah ada

---

## Catatan Pengembangan

### Keputusan Teknis Penting
1. **Indentasi** — gunakan 4 spasi (seperti Python), bukan tab
2. **Case sensitivity** — nama variabel bersifat case-sensitive (`Nama` ≠ `nama`)
3. **Encoding** — wajib UTF-8 untuk mendukung karakter Indonesia
4. **Komentar** — gunakan `#` (konsisten dengan Python)
5. **Akhir baris** — tidak perlu titik koma `;`

### Aturan Sinonim Kata Kunci
Beberapa kata kunci memiliki sinonim yang semuanya valid:
| Fungsi | Kata Kunci Utama | Sinonim |
|--------|-----------------|---------|
| print | `tampilkan` | `cetak`, `tulis` |
| input | `masukan` | — |
| True | `benar` | — |
| False | `salah` | — |
| None | `kosong` | — |
| and | `dan` | — |
| or | `atau` | — |
| not | `bukan` | — |
| in | `ada dalam` | `dalam` |

### Prioritas Task Saat Ini
1. 🔴 Selesaikan Lexer (Fase 1) terlebih dahulu
2. 🔴 Lanjut ke Parser (Fase 2)
3. 🔴 Lanjut ke Interpreter dasar (Fase 3.1–3.3)
4. 🟡 Fungsi bawaan dasar (Fase 3.5)
5. 🟡 Pesan error Bahasa Indonesia (Fase 4)
6. 🟡 CLI dasar (Fase 6.1–6.2)
7. 🟢 Modul standar (Fase 5)
8. 🟢 Dokumentasi (Fase 7)
