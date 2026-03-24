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

# Kondisi
jika umur >= 18:
    tampilkan f"{nama} sudah dewasa"
selainnya:
    tampilkan f"{nama} masih anak-anak"

# Fungsi
fungsi sapa(nama):
    tampilkan "Halo, " + nama + "!"

sapa("Siti")
```

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
