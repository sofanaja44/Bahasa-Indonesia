# Editor Web Bahasa Indonesia

Editor di browser untuk menulis dan menjalankan program Bahasa Indonesia **tanpa memasang apa pun**, juga dari HP. Mesinnya sama persis dengan aplikasi komputer: [mesin Go](../mesin/README.md) yang dikompilasi ke WebAssembly (`mesin.wasm`, ±1,4 MB setelah dimampatkan).

Fitur:
- Pewarnaan kode yang mengikuti kosakata bahasa (dibuat dari `src/token_types.py`)
- `tanya` dijawab lewat kotak di panel keluaran; `tunggu` benar-benar menunggu
- Tombol **Hentikan**, juga untuk perulangan yang tidak pernah berhenti atau tidak menampilkan apa pun
- Baris yang salah ditandai, dengan tombol untuk melompat ke baris itu
- Contoh program dari folder `contoh/`
- Tombol **Bagikan**: program dimampatkan ke dalam tautan (`#z=...`), siap dikirim lewat WhatsApp
- Draf tersimpan otomatis di browser
- Tetap bisa dibuka **tanpa internet** setelah kunjungan pertama, dan bisa dipasang di layar utama HP

## Membangun dan mencoba

```bash
python web/bangun.py --sajikan     # lalu buka http://localhost:8000
```

`bangun.py` butuh Python dan [Go](https://go.dev/dl/) 1.22+: mesin dikompilasi dengan `GOOS=js GOARCH=wasm`, dan `wasm_exec.js` (penghubung WebAssembly milik Go) disalin dari instalasi Go. Hasilnya ada di `web/situs/` (tidak masuk git).

Setiap perubahan di `main` diterbitkan otomatis ke GitHub Pages oleh `.github/workflows/situs.yml`.

## Tes

```bash
cd web && npm ci                 # Playwright, hanya untuk tes
node tes/tes_mesin.mjs           # tes kesesuaian + korpus pembanding, di mesin WebAssembly
node --test tes/tes_editor.mjs   # editor diuji di Chromium sungguhan
```

## Cara kerjanya

| Berkas | Tugas |
|---|---|
| `index.html`, `gaya.css` | Tampilan |
| `aplikasi.js` | Editor, panel keluaran, contoh, tautan berbagi |
| `sorotan.js` | Pewarnaan kode |
| `pekerja.js` | Web Worker: memuat `mesin.wasm` dan menjalankan program, sehingga halaman tetap lancar. Menyediakan fungsi keluaran, `tanya`, `tunggu`, dan pemeriksaan tombol Hentikan untuk mesin ([`mesin/cmd/wasm`](../mesin/cmd/wasm/main.go)) |
| `sw.js` | Service worker: saluran untuk `tanya`/`tunggu`/Hentikan, dan cache untuk mode tanpa internet |
| `bangun.py` | Menyusun semuanya ke `web/situs/` |

Program berjalan **sinkron** di Web Worker, jadi selama program berjalan pekerja tidak bisa menerima pesan biasa. Karena itu, `tanya`, `tunggu`, dan pemeriksaan tombol Hentikan memakai permintaan XHR sinkron ke alamat `__saluran__/...`. Permintaan itu ditahan oleh service worker sampai halaman mengirim jawaban, waktunya habis, atau tombol Hentikan ditekan. Cara ini tidak membutuhkan header khusus (COOP/COEP), sehingga bisa diterbitkan di GitHub Pages.

Mesin memeriksa tombol Hentikan sendiri setiap ±1.000 instruksi (paling sering tiap 50 ms bertanya ke saluran), jadi perulangan yang tidak menampilkan apa pun juga berhenti seketika. Bila mesin tidak menjawab dalam 1,5 detik (mis. sedang menghitung `faktorial` dari bilangan raksasa), pekerjanya dihentikan paksa lalu mesin dimuat ulang dari cache.

Semua berkas aplikasi diberi versi yang sama (`?v=...`, dihitung dari isinya), sehingga pembaruan situs selalu berganti serentak. `mesin.wasm` punya versi dan cache sendiri, jadi hanya diunduh ulang bila mesinnya berubah.
