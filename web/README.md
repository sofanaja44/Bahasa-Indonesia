# Editor Web Bahasa Indonesia

Editor di browser untuk menulis dan menjalankan program Bahasa Indonesia **tanpa memasang apa pun**, juga dari HP. Interpreter yang sama dengan versi komputer (`src/`) dijalankan di browser lewat [Pyodide](https://pyodide.org) (Python dalam WebAssembly).

Fitur:
- Pewarnaan kode yang mengikuti kosakata bahasa (dibuat dari `src/token_types.py`)
- `tanya` dijawab lewat kotak di panel keluaran; `tunggu` benar-benar menunggu
- Tombol **Hentikan**, juga untuk perulangan yang tidak pernah berhenti
- Baris yang salah ditandai, dengan tombol untuk melompat ke baris itu
- Contoh program dari folder `contoh/`
- Tombol **Bagikan**: program dimampatkan ke dalam tautan (`#z=...`), siap dikirim lewat WhatsApp
- Draf tersimpan otomatis di browser
- Tetap bisa dibuka **tanpa internet** setelah kunjungan pertama, dan bisa dipasang di layar utama HP

## Membangun dan mencoba

```bash
python web/bangun.py --sajikan     # lalu buka http://localhost:8000
```

`bangun.py` hanya butuh Python. Pyodide diunduh sekali dari registri npm, diperiksa sidik jarinya, lalu disimpan di `web/.cache/`. Hasilnya ada di `web/situs/` (tidak masuk git).

Setiap perubahan di `main` diterbitkan otomatis ke GitHub Pages oleh `.github/workflows/situs.yml`.

## Tes

```bash
cd web && npm ci                 # Playwright, hanya untuk tes
node tes/tes_pyodide.mjs         # semua tes kesesuaian, dijalankan di Pyodide
node --test tes/tes_editor.mjs   # editor diuji di Chromium sungguhan
```

## Cara kerjanya

| Berkas | Tugas |
|---|---|
| `index.html`, `gaya.css` | Tampilan |
| `aplikasi.js` | Editor, panel keluaran, contoh, tautan berbagi |
| `sorotan.js` | Pewarnaan kode |
| `pekerja.js` | Web Worker: memuat Pyodide dan menjalankan program, sehingga halaman tetap lancar |
| `jembatan.py` | Berjalan di Pyodide: mengalihkan keluaran, `tanya`, dan `tunggu` ke `pekerja.js` |
| `sw.js` | Service worker: saluran untuk `tanya`/`tunggu`/Hentikan, dan cache untuk mode tanpa internet |
| `bangun.py` | Menyusun semuanya ke `web/situs/` |

Program berjalan **sinkron** di Web Worker, jadi selama program berjalan pekerja tidak bisa menerima pesan biasa. Karena itu, `tanya`, `tunggu`, dan pemeriksaan tombol Hentikan memakai permintaan XHR sinkron ke alamat `__saluran__/...`. Permintaan itu ditahan oleh service worker sampai halaman mengirim jawaban, waktunya habis, atau tombol Hentikan ditekan. Cara ini tidak membutuhkan header khusus (COOP/COEP), sehingga bisa diterbitkan di GitHub Pages.

Program yang tidak pernah menampilkan atau menunggu apa pun (mis. `selama benar` tanpa isi) tidak sempat memeriksa tombol Hentikan. Pekerjanya dihentikan paksa lalu Pyodide dimuat ulang dari cache.

Semua berkas aplikasi diberi versi yang sama (`?v=...`, dihitung dari isinya), sehingga pembaruan situs selalu berganti serentak.
