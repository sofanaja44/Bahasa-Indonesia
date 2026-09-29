<div align="center">
  <h1>🇮🇩 Bahasa Indonesia Programming Language</h1>
  <p><strong>Bahasa pemrograman berasaskan 100% Bahasa Indonesia</strong></p>
  
  [![Status](https://img.shields.io/badge/Status-Aktif%20%28v0.1%20MVP%29-success?style=for-the-badge)]()
  [![Lisensi](https://img.shields.io/badge/Lisensi-MIT-blue?style=for-the-badge)]()
  [![Python](https://img.shields.io/badge/Python-3.8%2B-yellow?style=for-the-badge&logo=python&logoColor=white)]()
  
  <p><em>"Buat kode seperti kamu bicara — sepenuhnya dalam Bahasa Indonesia."</em></p>
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

---

## 🚀 Cara Menjalankan

Interpretasi kode Bahasa Indonesia dieksekusi melalui mesin *backend* Python.

1. **Jalankan program dari file `.id`:**
```bash
python indonesia.py contoh/demo_lengkap.id
python indonesia.py contoh/cerita.id      # program bergaya bercerita
```

2. **Gunakan Mode Interaktif (REPL) langsung di Terminal:**
```bash
python indonesia.py repl
```

3. **Lihat Menu Bantuan Lainnya:**
```bash
python indonesia.py bantu
```

---

## 📂 Struktur Repositori Terorganisasi

Proyek ini tertata rapi agar sistem dapat dirombak dan dibaca oleh para kontributor secara mudah.

```
indonesia-v1/
├── src/              # Kode sumber interpreter (Lexer, Parser, Ast, Evaluate)
├── tests/            # Unit test dengan `pytest`
├── contoh/           # Himpunan program-program contoh (File berekstensi .id) 
├── indonesia.py      # Entry point CLI Utama (Pengeksekusi kode program)
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

---

## 📜 Lisensi & Kontribusi

Proyek ini disebarluaskan dengan Lisensi [MIT](LICENSE) secara 100% terbuka *(Open-Source)*. 
Kami **sangat menyambut** berbagai permintaan *Pull Request* kontribusi, perbaikan bug, penyempurnaan gramatika, pembuatan library standar, atau rekomendasi fitur demi mendorong pendidikan pemrograman bangsa ini kedepannya! 

<br>

> *Mari memajukan anak bangsa, dimulai dari menyusun barisan algoritma kode dalam bahasa negara mereka sendiri.* 🇮🇩
