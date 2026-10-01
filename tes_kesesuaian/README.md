# Tes Kesesuaian

Folder ini adalah **spesifikasi yang bisa dijalankan** untuk bahasa pemrograman Indonesia. Setiap mesin (interpreter Python saat ini, atau mesin Go di Tahap 3 [ROADMAP](../ROADMAP.md)) dianggap benar bila lulus semua tes di sini.

Tes ini sengaja tidak bergantung pada detail interpreter Python: yang diperiksa hanya apa yang tampil di layar dan jenis kesalahannya.

## Format

Setiap tes adalah satu program `nama.id`, ditemani berkas lain dengan nama yang sama:

| Berkas | Wajib? | Isi |
|---|---|---|
| `nama.id` | ya | Program yang dijalankan. |
| `nama.keluaran` | salah satu | Semua yang tampil di layar, persis sama (termasuk baris baru di akhir). |
| `nama.kesalahan` | salah satu | Baris 1: nama kesalahan, mis. `KesalahanBagiNol`. Baris berikutnya (boleh tidak ada): potongan teks yang harus ada di pesan kesalahan. |
| `nama.masukan` | tidak | Jawaban untuk `tanya`/`masukan`, satu per baris. |

Aturan:

- Jika ada `.kesalahan`, program harus berhenti dengan kesalahan itu. Jika ada `.keluaran` juga, tampilan layar *sebelum* kesalahan harus sama persis.
- Jika tidak ada `.kesalahan`, program harus selesai tanpa kesalahan.
- Pertanyaan pada `tanya`/`masukan` ditulis ke layar tanpa pindah baris; jawaban dari `.masukan` tidak ikut tampil di layar.
- `tunggu` tidak perlu benar-benar menunggu saat tes.
- Hasil yang acak atau bergantung waktu diuji lewat sifatnya, mis. `tampilkan dadu paling sedikit 1`, bukan nilainya.
- Semua berkas memakai UTF-8 dan akhir baris LF.

## Menjalankan

```bash
python -m pytest tests/test_kesesuaian.py -v
```

## Menambah tes

1. Tulis program di subfolder yang sesuai, mis. `perulangan/ulangi_kali.id`.
2. Tulis keluaran yang **seharusnya** (berdasarkan aturan bahasa, bukan sekadar menyalin hasil interpreter) ke `perulangan/ulangi_kali.keluaran`.
3. Jalankan tesnya. Jika gagal, tentukan mana yang salah: interpreternya atau harapannya.
