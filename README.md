# 🇮🇩 Indonesia — Bahasa Pemrograman Indonesia

**Indonesia** adalah bahasa pemrograman dengan sintaks 100% Bahasa Indonesia. Dirancang agar siapapun yang bisa membaca dan menulis Bahasa Indonesia dapat langsung belajar pemrograman tanpa hambatan bahasa.

> *"Buat kode seperti kamu bicara — dalam Bahasa Indonesia."*

## Contoh Kode

```
# Program pertama
tampilkan "Halo Dunia!"

# Variabel
buat nama = "Budi"
buat umur = 20

# Kondisi (Cara Standar/Simbol)
jika umur >= 18:
    tampilkan format"{nama} sudah dewasa"

# Kondisi (Cara Natural/Bahasa)
# Anda bebas memakai kata-kata agar kode terbaca seperti cerita!
atau jika umur tidak kurang dari 18:
    tampilkan format"{nama} sudah dewasa"
selainnya:
    tampilkan format"{nama} masih anak-anak"

# Fungsi & Aritmatika Natural
fungsi sapa(nama):
    tampilkan "Halo, " ditambah nama ditambah "!"

sapa("Siti")
```

### Opsi Penulisan Kode Fleksibel
Bahasa Indonesia mendukung **Dua Gaya Penulisan**:
1. **Gaya Simbolik (Matematis)**: Menggunakan `+`, `-`, `*`, `/`, `==`, `>=`, `<=`, dsb. Cocok bagi yang sudah terbiasa dengan bahasa pemrograman konvensional.
2. **Gaya Natural (Bercerita)**: Menggunakan kata hubung seperti `ditambah`, `dikurang`, `dikali`, `dibagi`, `sama dengan`, `tidak kurang dari`, `sisa bagi`, dan `pangkat`. Format *string* juga menggunakan `format"..."` alih-alih `f"..."`. Sangat cocok digunakan untuk mengajar murid pemula agar logikanya lebih mudah dicerna.

## Menjalankan

```bash
# Jalankan file .id
python indonesia.py contoh/halo_dunia.id

# Mode REPL interaktif
python indonesia.py repl

# Bantuan
python indonesia.py bantu
```

## Struktur Proyek

```
indonesia-v1/
├── src/              # Kode sumber interpreter
├── tests/            # Unit test
├── contoh/           # Program contoh .id
├── indonesia.py      # CLI entry point
└── requirements.txt
```

## Pengembangan

```bash
# Install dependencies
pip install -r requirements.txt

# Jalankan test
python -m pytest tests/ -v
```

## Status

🚧 **v0.1 MVP** — Dalam pengembangan aktif

## Lisensi

MIT
