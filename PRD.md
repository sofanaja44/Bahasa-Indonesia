# PRD — BahasaKode (Bahasa Pemrograman Indonesia)

**Versi:** 1.0  
**Tanggal:** Maret 2026  
**Status:** Draft Awal

---

## 1. Ringkasan Eksekutif

**BahasaKode** adalah bahasa pemrograman berbasis Bahasa Indonesia yang dirancang agar siapapun yang bisa membaca dan menulis Bahasa Indonesia dapat langsung belajar pemrograman tanpa hambatan bahasa. Sintaksnya murni menggunakan kata-kata Bahasa Indonesia sehari-hari, bebas dari istilah teknis asing, dan terasa seperti menulis kalimat biasa.

**Misi:** *"Buat kode seperti kamu bicara — dalam Bahasa Indonesia."*

---

## 2. Latar Belakang & Masalah

- Mayoritas bahasa pemrograman menggunakan kata kunci Bahasa Inggris (`if`, `else`, `while`, `function`, dll), yang menjadi hambatan bagi pemula Indonesia.
- Banyak pelajar Indonesia yang berhenti belajar coding bukan karena tidak mampu berpikir logis, tapi karena terhalang kosakata asing.
- Belum ada bahasa pemrograman yang benar-benar menggunakan Bahasa Indonesia secara penuh dan natural sebagai sintaks utamanya.

---

## 3. Target Pengguna

| Segmen | Deskripsi |
|--------|-----------|
| Pelajar SD–SMA | Anak-anak yang baru mengenal pemrograman |
| Mahasiswa non-IT | Jurusan ekonomi, sosial, hukum yang perlu belajar dasar coding |
| Guru & Dosen | Yang ingin mengajar logika pemrograman tanpa hambatan bahasa |
| Pemula dewasa | Orang dewasa yang ingin belajar coding dari nol |
| Developer Indonesia | Yang ingin menulis skrip/otomasi dengan lebih intuitif |

---

## 4. Tujuan Produk

1. Menurunkan kurva belajar pemrograman bagi orang Indonesia secara drastis.
2. Membuat sintaks yang terasa seperti menulis kalimat Bahasa Indonesia biasa.
3. Mendukung fitur-fitur pemrograman modern: variabel, kondisi, perulangan, fungsi, array, kelas, dan I/O.
4. Menyediakan pesan error dalam Bahasa Indonesia yang mudah dipahami.
5. Memiliki interpreter atau compiler yang ringan dan mudah dijalankan.

---

## 5. Spesifikasi Bahasa

### 5.1 Filosofi Desain

- **Kata kunci = Bahasa Indonesia sehari-hari** — tidak ada campuran Inggris sama sekali.
- **Satu cara, satu arti** — setiap konsep memiliki satu kata kunci yang jelas.
- **Mudah dibaca keras** — kode harus bisa dibacakan seperti membaca cerita.
- **Toleran terhadap variasi** — mendukung beberapa sinonim untuk kata kunci yang sama (misal: `tampilkan` = `cetak` = `tulis`).

---

### 5.2 Tipe Data

| Tipe | Kata Kunci | Contoh |
|------|-----------|--------|
| Bilangan bulat | `bilangan` | `bilangan umur = 17` |
| Bilangan desimal | `desimal` | `desimal harga = 9500.50` |
| Teks | `teks` | `teks nama = "Budi"` |
| Benar/Salah | `logika` | `logika aktif = benar` |
| Tidak ada nilai | `kosong` | `kosong` |
| Otomatis | `buat` | `buat x = 10` (tipe ditebak otomatis) |

---

### 5.3 Variabel

```
buat nama = "Budi"
buat umur = 20
buat tinggi = 170.5
buat sudahMakan = benar
```

Deklarasi eksplisit:
```
teks nama = "Siti"
bilangan nilai = 85
desimal berat = 60.5
logika aktif = salah
```

Konstanta (tidak bisa diubah):
```
tetap PI = 3.14159
tetap NAMA_SEKOLAH = "SMA Nusantara"
```

---

### 5.4 Operasi Matematika

| Operasi | Simbol | Contoh |
|---------|--------|--------|
| Tambah | `+` | `buat hasil = 5 + 3` |
| Kurang | `-` | `buat sisa = 10 - 4` |
| Kali | `*` | `buat luas = panjang * lebar` |
| Bagi | `/` | `buat rata = total / jumlah` |
| Sisa bagi | `%` | `buat sisa = 10 % 3` |
| Pangkat | `**` | `buat kuadrat = 5 ** 2` |

---

### 5.5 Operasi Perbandingan

| Perbandingan | Simbol | Alternatif kata |
|-------------|--------|----------------|
| Sama dengan | `==` | `sama dengan` |
| Tidak sama | `!=` | `tidak sama dengan` |
| Lebih besar | `>` | `lebih besar dari` |
| Lebih kecil | `<` | `lebih kecil dari` |
| Lebih besar/sama | `>=` | `lebih besar sama dengan` |
| Lebih kecil/sama | `<=` | `lebih kecil sama dengan` |

---

### 5.6 Operasi Logika

| Operasi | Kata Kunci |
|---------|-----------|
| DAN | `dan` |
| ATAU | `atau` |
| BUKAN | `bukan` |

Contoh:
```
jika umur >= 17 dan punya_ktp == benar:
    tampilkan "Boleh masuk"
```

---

### 5.7 Pengkondisian (if/else)

**Bentuk dasar:**
```
jika nilai >= 90:
    tampilkan "Nilai A"
atau jika nilai >= 80:
    tampilkan "Nilai B"
atau jika nilai >= 70:
    tampilkan "Nilai C"
selainnya:
    tampilkan "Perlu belajar lebih giat"
```

**Bentuk satu baris:**
```
jika umur >= 18: tampilkan "Dewasa"
```

**Kata kunci kondisi:**
| Fungsi | Kata Kunci |
|--------|-----------|
| if | `jika` |
| else if | `atau jika` |
| else | `selainnya` |
| switch/match | `pilih` |
| case | `ketika` |
| default | `bawaan` |

**Contoh pilih/ketika:**
```
pilih hari:
    ketika "Senin":
        tampilkan "Awal pekan"
    ketika "Sabtu":
        tampilkan "Akhir pekan"
    ketika "Minggu":
        tampilkan "Hari libur"
    bawaan:
        tampilkan "Hari biasa"
```

---

### 5.8 Perulangan (Loop)

**Selama (while):**
```
buat angka = 1
selama angka <= 10:
    tampilkan angka
    angka = angka + 1
```

**Untuk (for range):**
```
untuk i dari 1 sampai 10:
    tampilkan i
```

**Untuk setiap (for each):**
```
untuk setiap buah dalam daftar_buah:
    tampilkan buah
```

**Untuk dengan langkah:**
```
untuk i dari 0 sampai 100 langkah 5:
    tampilkan i
```

**Ulangi (do-while):**
```
ulangi:
    tampilkan "Coba lagi"
    buat jawaban = masukan("Apakah benar? ")
selama jawaban != "ya"
```

**Hentikan perulangan:**
```
untuk i dari 1 sampai 100:
    jika i == 50:
        berhenti         # break
    jika i % 2 == 0:
        lewati           # continue
    tampilkan i
```

**Kata kunci perulangan:**
| Fungsi | Kata Kunci |
|--------|-----------|
| while | `selama` |
| for range | `untuk ... dari ... sampai` |
| for each | `untuk setiap ... dalam` |
| do-while | `ulangi ... selama` |
| break | `berhenti` |
| continue | `lewati` |

---

### 5.9 Fungsi

**Definisi fungsi:**
```
fungsi sapa(nama):
    tampilkan "Halo, " + nama + "!"
```

**Fungsi dengan nilai kembalian:**
```
fungsi tambah(a, b):
    kembalikan a + b

buat hasil = tambah(5, 3)
tampilkan hasil
```

**Fungsi dengan nilai default:**
```
fungsi perkenalan(nama, kota = "Jakarta"):
    tampilkan nama + " dari " + kota
```

**Fungsi anonim / lambda:**
```
buat kuadrat = fungsi(x): kembalikan x * x
buat hasil = kuadrat(4)
```

**Kata kunci fungsi:**
| Fungsi | Kata Kunci |
|--------|-----------|
| function | `fungsi` |
| return | `kembalikan` |
| void (no return) | *(tidak perlu kata kunci)* |

---

### 5.10 Array / Daftar

**Buat daftar:**
```
buat buah = ["apel", "mangga", "jeruk"]
buat angka = [1, 2, 3, 4, 5]
buat campur = [1, "dua", benar, 3.5]
```

**Akses elemen:**
```
tampilkan buah[0]        # apel
tampilkan buah[1]        # mangga
tampilkan buah[-1]       # jeruk (dari belakang)
```

**Operasi daftar:**
```
buah.tambahkan("durian")         # push/append
buah.hapus("mangga")             # remove by value
buah.hapusPosisi(0)              # remove by index
buah.sisipkan(1, "semangka")     # insert at index
buat panjang = buah.panjang()    # length
buah.urutkan()                   # sort ascending
buah.balik()                     # reverse
```

**Irisan daftar (slice):**
```
buat sebagian = buah[1:3]        # indeks 1 sampai 2
buat awal = buah[:2]             # dari awal sampai indeks 1
buat akhir = buah[2:]            # dari indeks 2 sampai akhir
```

**Cek keberadaan:**
```
jika "apel" ada dalam buah:
    tampilkan "Ada apel!"
```

---

### 5.11 Kamus / Peta Data (Dictionary/Map)

**Buat kamus:**
```
buat mahasiswa = {
    "nama": "Budi",
    "umur": 20,
    "jurusan": "Informatika"
}
```

**Akses dan ubah:**
```
tampilkan mahasiswa["nama"]
mahasiswa["umur"] = 21
mahasiswa["ipk"] = 3.75
```

**Operasi kamus:**
```
mahasiswa.hapusKunci("ipk")
buat adaKunci = mahasiswa.adaKunci("nama")
buat semua_kunci = mahasiswa.kunci()
buat semua_nilai = mahasiswa.nilai()
```

---

### 5.12 Input dan Output

**Output (tampilkan):**
```
tampilkan "Halo Dunia!"
tampilkan "Nama saya adalah " + nama
tampilkan nilai, nama, umur        # cetak banyak nilai
cetak "Tanpa baris baru"           # tanpa newline
tulis "Sama seperti tampilkan"     # sinonim
```

**Input:**
```
buat nama = masukan("Siapa nama kamu? ")
buat umur = masukan_angka("Berapa umurmu? ")
buat nilai = masukan_desimal("Nilai kamu? ")
```

**Format teks:**
```
tampilkan f"Halo {nama}, umurmu {umur} tahun"
tampilkan f"Total: {harga * jumlah} rupiah"
```

---

### 5.13 Kelas (Class / OOP)

**Definisi kelas:**
```
kelas Hewan:
    buat nama = ""
    buat suara = ""
    
    fungsi inisialisasi(nama, suara):
        diri.nama = nama
        diri.suara = suara
    
    fungsi bersuara():
        tampilkan diri.nama + " berkata: " + diri.suara
```

**Instansiasi:**
```
buat kucing = Hewan("Kucing", "Meow")
kucing.bersuara()
```

**Pewarisan:**
```
kelas Anjing mewarisi Hewan:
    fungsi inisialisasi(nama):
        super.inisialisasi(nama, "Guk!")
    
    fungsi ambilBola():
        tampilkan diri.nama + " mengambil bola!"
```

**Kata kunci OOP:**
| Fungsi | Kata Kunci |
|--------|-----------|
| class | `kelas` |
| self/this | `diri` |
| __init__ | `fungsi inisialisasi` |
| extends/inherits | `mewarisi` |
| super | `super` |
| public (default) | *(tidak perlu)* |
| private | `pribadi` |
| static | `statis` |

---

### 5.14 Penanganan Error (Exception Handling)

```
coba:
    buat hasil = 10 / 0
tangkap ZeroDivisionError sebagai e:
    tampilkan "Error: Tidak bisa dibagi nol!"
tangkap sebagai e:
    tampilkan "Error tidak diketahui: " + e.pesan
akhirnya:
    tampilkan "Selesai dieksekusi"
```

**Lempar error manual:**
```
fungsi bagi(a, b):
    jika b == 0:
        lempar Error("Pembagi tidak boleh nol!")
    kembalikan a / b
```

**Kata kunci error:**
| Fungsi | Kata Kunci |
|--------|-----------|
| try | `coba` |
| except/catch | `tangkap` |
| finally | `akhirnya` |
| throw/raise | `lempar` |
| Error | `Error` |

---

### 5.15 Modul dan Impor

```
impor matematika
impor matematika.akar sebagai akar
dari waktu impor sekarang

tampilkan matematika.pi
tampilkan akar(16)
```

**Kata kunci modul:**
| Fungsi | Kata Kunci |
|--------|-----------|
| import | `impor` |
| from ... import | `dari ... impor` |
| as | `sebagai` |

---

### 5.16 Modul Standar Bawaan

| Modul | Fungsi |
|-------|--------|
| `matematika` | fungsi matematika (akar, sinus, kosinus, pi, dll) |
| `waktu` | tanggal dan waktu |
| `acak` | angka acak |
| `berkas` | baca/tulis file |
| `jaringan` | HTTP request dasar |
| `json` | parse dan encode JSON |
| `teks` | manipulasi string lanjutan |
| `sistem` | akses sistem operasi |

---

### 5.17 Komentar

```
# Ini komentar satu baris

## Ini juga komentar satu baris alternatif

"""
Ini komentar
yang panjang
bisa banyak baris
"""
```

---

### 5.18 Pesan Error dalam Bahasa Indonesia

Semua pesan error interpreter harus dalam Bahasa Indonesia:

| Error | Pesan |
|-------|-------|
| SyntaxError | `Kesalahan sintaks pada baris X: kata kunci tidak dikenali` |
| NameError | `Variabel 'X' belum dideklarasikan` |
| TypeError | `Tipe data tidak cocok: tidak bisa menggabungkan bilangan dengan teks` |
| IndexError | `Indeks X di luar batas daftar` |
| ZeroDivisionError | `Tidak bisa membagi dengan nol` |
| FileNotFoundError | `Berkas 'X' tidak ditemukan` |

---

## 6. Contoh Program Lengkap

### Kalkulator Sederhana
```
tampilkan "=== Kalkulator BahasaKode ==="

buat angka1 = masukan_angka("Masukkan angka pertama: ")
buat angka2 = masukan_angka("Masukkan angka kedua: ")
buat operasi = masukan("Pilih operasi (+, -, *, /): ")

pilih operasi:
    ketika "+":
        tampilkan f"Hasil: {angka1 + angka2}"
    ketika "-":
        tampilkan f"Hasil: {angka1 - angka2}"
    ketika "*":
        tampilkan f"Hasil: {angka1 * angka2}"
    ketika "/":
        jika angka2 == 0:
            tampilkan "Error: Tidak bisa dibagi nol!"
        selainnya:
            tampilkan f"Hasil: {angka1 / angka2}"
    bawaan:
        tampilkan "Operasi tidak dikenal"
```

### Daftar Belanja
```
buat daftar_belanja = []
buat lanjut = benar

selama lanjut:
    buat item = masukan("Tambah item (atau 'selesai' untuk berhenti): ")
    jika item == "selesai":
        lanjut = salah
    selainnya:
        daftar_belanja.tambahkan(item)
        tampilkan f"'{item}' ditambahkan ke daftar"

tampilkan "\n=== Daftar Belanja Kamu ==="
untuk setiap barang dalam daftar_belanja:
    tampilkan "- " + barang
tampilkan f"Total: {daftar_belanja.panjang()} item"
```

### Menghitung Nilai Rata-rata
```
fungsi hitung_rata(daftar_nilai):
    jika daftar_nilai.panjang() == 0:
        kembalikan 0
    buat total = 0
    untuk setiap nilai dalam daftar_nilai:
        total = total + nilai
    kembalikan total / daftar_nilai.panjang()

buat nilai_siswa = [75, 88, 92, 65, 78, 95, 82]
buat rata_rata = hitung_rata(nilai_siswa)
tampilkan f"Rata-rata nilai: {rata_rata}"

jika rata_rata >= 90:
    tampilkan "Predikat: Istimewa"
atau jika rata_rata >= 80:
    tampilkan "Predikat: Baik"
atau jika rata_rata >= 70:
    tampilkan "Predikat: Cukup"
selainnya:
    tampilkan "Predikat: Perlu Bimbingan"
```

---

## 7. Arsitektur Teknis

### 7.1 Komponen Utama

```
[Kode .bk / .bahasakode]
        ↓
[Lexer — Tokenisasi kata kunci Indonesia]
        ↓
[Parser — Bangun AST (Abstract Syntax Tree)]
        ↓
[Interpreter / Compiler]
        ↓
[Eksekusi / Bytecode]
```

### 7.2 Pilihan Implementasi

**Opsi A — Interpreter Python (Direkomendasikan untuk v1.0):**
- Bangun interpreter di atas Python.
- Cepat di-prototyping, mudah dikembangkan.
- Bisa transpile ke Python untuk performa lebih baik.

**Opsi B — Transpiler ke JavaScript:**
- Kode BahasaKode diterjemahkan ke JavaScript.
- Bisa dijalankan di browser tanpa install apapun.
- Cocok untuk editor online.

**Opsi C — Compiler ke Bytecode (v2.0+):**
- Bytecode sendiri + virtual machine ringan.
- Performa tinggi untuk produksi.

### 7.3 Ekstensi File

- `.bk` — BahasaKode (singkat)
- `.bahasakode` — alternatif eksplisit

---

## 8. Tools & Ekosistem

| Tool | Deskripsi |
|------|-----------|
| `bk` CLI | Jalankan file `.bk` dari terminal |
| `bk repl` | Mode interaktif (REPL) |
| `bk buat proyek` | Scaffold proyek baru |
| `bk bantu` | Bantuan perintah |
| Editor online | IDE berbasis web tanpa install |
| VS Code Extension | Syntax highlighting & autocomplete |
| Dokumentasi | Docs lengkap dalam Bahasa Indonesia |

---

## 9. Kriteria Sukses (MVP)

- [ ] Interpreter dapat menjalankan semua konstruk dasar (variabel, kondisi, loop, fungsi, daftar, kamus)
- [ ] Semua pesan error dalam Bahasa Indonesia
- [ ] Bisa dijalankan via `bk namafile.bk` di terminal
- [ ] Mode REPL interaktif berfungsi
- [ ] Dokumentasi dasar tersedia dalam Bahasa Indonesia
- [ ] Contoh program minimal 20 buah

---

## 10. Roadmap

| Fase | Fitur | Target |
|------|-------|--------|
| v0.1 MVP | Variabel, kondisi, loop, fungsi, I/O dasar | Bulan 1–2 |
| v0.2 | Daftar, kamus, string formatting | Bulan 3 |
| v0.3 | Kelas, OOP, penanganan error | Bulan 4 |
| v0.4 | Modul standar, impor | Bulan 5 |
| v1.0 | REPL, CLI stabil, dokumentasi | Bulan 6 |
| v1.1 | Editor online | Bulan 7–8 |
| v1.2 | VS Code extension | Bulan 9 |
| v2.0 | Compiler ke bytecode | Bulan 12+ |

---

## 11. Referensi & Inspirasi

- **Python** — filosofi kesederhanaan dan keterbacaan
- **Logo** — bahasa untuk anak-anak berbasis perintah natural
- **Scratch** — block coding untuk pemula
- **Bahasa** (Malaysia) — bahasa pemrograman Melayu (referensi historis)
