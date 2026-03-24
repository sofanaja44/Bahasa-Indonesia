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

# Deklarasi Variabel
buat nama = "Budi"
buat umur = 20

# Percabangan yang Mengalir
jika umur tidak kurang dari 18:
    tampilkan format"{nama} sudah dewasa"
selainnya:
    tampilkan format"{nama} masih anak-anak"

# Operasi Aritmatika menggunakan teks!
fungsi sapa(panggilan):
    tampilkan "Halo, " ditambah panggilan ditambah "!"

sapa(nama)
```

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

## 🚀 Cara Menjalankan

Interpretasi kode Bahasa Indonesia dieksekusi melalui mesin *backend* Python.

1. **Jalankan program dari file `.id`:**
```bash
python indonesia.py contoh/demo_lengkap.id
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
