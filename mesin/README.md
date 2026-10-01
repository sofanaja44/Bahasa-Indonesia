# Mesin Go Bahasa Indonesia

Mesin utama Bahasa Pemrograman Indonesia (Tahap 3 di [ROADMAP](../ROADMAP.md)): lexer, parser, kompiler *bytecode*, dan mesin virtual (VM) yang ditulis dalam Go. Dari kode yang sama dibuat:

- **perintah `indonesia`**, satu berkas kecil untuk Windows, macOS, dan Linux, tanpa perlu memasang Python;
- **`mesin.wasm`**, mesin yang sama dalam WebAssembly untuk [editor web](../web/README.md).

Interpreter Python di [`src/`](../src) tetap disimpan sebagai **acuan**: setiap perilaku mesin Go dibandingkan dengannya, sampai ke isi pesan kesalahan dan saran "Maksud Anda ...?".

## Membangun dan menjalankan

Butuh [Go](https://go.dev/dl/) 1.22 atau yang lebih baru; tidak ada dependensi lain.

```bash
cd mesin
go build -o bin/ ./cmd/indonesia
bin/indonesia ../contoh/halo_dunia.id   # jalankan berkas
bin/indonesia                           # mode interaktif (REPL)
bin/indonesia -e 'tampilkan 1 + 2'      # jalankan kode langsung
```

`mesin.wasm` untuk editor web dibangun oleh `python web/bangun.py` (perintahnya: `GOOS=js GOARCH=wasm go build ./cmd/wasm`).

## Tes

| Perintah | Yang diperiksa |
|---|---|
| `go test ./...` | Tes unit dan **korpus pembanding**: 904 program yang hasilnya (layar, pesan kesalahan, nilai terakhir) harus sama persis dengan interpreter Python |
| `MESIN_INDONESIA=mesin/bin/indonesia python -m pytest tests/test_kesesuaian.py tests/test_cli.py` | Tes kesesuaian dan tes perintah baris (termasuk REPL), dijalankan pada perintah `indonesia` |
| `node web/tes/tes_mesin.mjs` | Tes kesesuaian dan seluruh korpus pembanding di `mesin.wasm` |
| `go test -run XXX -bench .` | Tolok ukur kecepatan |

Korpus pembanding ([`testdata/korpus.json`](testdata/korpus.json)) dibuat dari interpreter Python oleh [`testdata/buat_korpus.py`](testdata/buat_korpus.py). Isinya: setiap potongan kode yang dijalankan tes Python, semua program di `contoh/` dan `tes_kesesuaian/`, serta program kecil di [`testdata/tambahan/`](testdata/tambahan) yang sengaja menguji kasus tepi (angka, teks Unicode, `coba`/`akhirnya`, kelas, pustaka, pesan sintaks, ...). Semuanya dijalankan dalam keadaan yang bisa diulang: benih acak, jam, dan jawaban `tanya` yang tetap.

```bash
python mesin/testdata/buat_korpus.py            # tulis ulang korpus setelah interpreter acuan berubah
python mesin/testdata/buat_korpus.py --periksa  # CI: gagal bila korpus sudah tidak sesuai

# Ribuan program acak, dibandingkan dengan interpreter Python
python mesin/testdata/program_acak.py 3000 /tmp/acak.json 1 ekspresi   # atau: kontrol
cd mesin && KORPUS=/tmp/acak.json go test -run TestKorpusPembanding .
```

Pembuat program acak punya dua mode: `ekspresi` (operator, fungsi bawaan, metode, dan kesalahannya) dan `kontrol` (blok bersarang dengan `berhenti`, `lewati`, `kembalikan`, `coba`/`tangkap`/`akhirnya`). Sekitar 25.000 program acak sudah dibandingkan tanpa beda, selain perbedaan yang disengaja di bawah.

## Susunan kode

| Berkas | Isi |
|---|---|
| `token.go`, `lexer.go` | Kata kunci, frasa (`lebih dari atau sama dengan`), indentasi → token |
| `parser.go`, `ast.go` | Tata bahasa natural dan simbolik → pohon sintaks (AST), dengan pesan kesalahan sintaks yang sama dengan Python |
| `kompiler.go`, `kode.go` | AST → *bytecode* |
| `vm.go` | Mesin virtual: tumpukan nilai, bingkai fungsi, lingkup variabel, `coba`/`tangkap`, pemanggilan |
| `nilai.go`, `angka.go`, `presisi.go` | Nilai, aturan angka Python (bilangan bulat tanpa batas, tampilan desimal), pangkat dan logaritma yang dibulatkan tepat |
| `bawaan.go`, `pustaka.go`, `acak.go` | Fungsi bawaan, metode daftar/kamus/teks, pustaka standar, Mersenne Twister yang sama dengan modul `random` Python |
| `kesalahan.go`, `difflib.go` | Pesan kesalahan dan saran "Maksud Anda ...?" (port `difflib.get_close_matches`) |
| `api.go` | API untuk program lain: `Baru`, `Jalankan`, `JalankanREPL`, `KeTeks`, ... |
| `cmd/indonesia` | Perintah baris (berkas, `-e`, REPL, Ctrl+C) |
| `cmd/wasm` | WebAssembly untuk editor web |

### Cara kerjanya

- **Bytecode dan tumpukan.** Program dikompilasi sekali menjadi instruksi sederhana, lalu dijalankan oleh VM berbasis tumpukan. Bingkai fungsi disimpan di memori biasa, bukan di tumpukan Go, sehingga rekursi dalam aman di komputer maupun di browser. Batasnya tetap 3.000 panggilan bertumpuk, sama dengan bahasa acuannya.
- **Lingkup variabel** meniru Python: setiap blok (dan setiap putaran perulangan) punya lingkup sendiri. Lingkup yang tidak mungkin ditangkap fungsi di dalamnya dipakai ulang, sehingga perulangan dan pemanggilan fungsi hampir tidak mengalokasikan memori.
- **`akhirnya`** disalin ke setiap jalan keluar blok `coba` (`berhenti`, `lewati`, `kembalikan`), ditambah penangan untuk jalur kesalahan.
- **Tombol Hentikan / Ctrl+C**: VM memeriksa `IO.Berhenti` setiap ±1.000 instruksi, jadi perulangan tanpa keluaran pun bisa dihentikan.
- **Masukan, keluaran, jam, dan berkas** lewat struct `IO`, sehingga perintah baris, editor web, dan tes memakai mesin yang sama.

## Kecepatan

Diukur dengan perintah `indonesia` dibandingkan `python indonesia.py` (Python 3.11, satu inti):

| Program | Python | Go | |
|---|---|---|---|
| `fib(25)`, 242.785 panggilan fungsi | 2,54 dtk | 0,04 dtk | 65× |
| Perulangan 1 juta kali | 2,71 dtk | 0,10 dtk | 26× |
| Bilangan prima sampai 60.000 | 10,73 dtk | 0,18 dtk | 59× |
| 200.000 teks format | 4,39 dtk | 0,12 dtk | 38× |
| 200.000 isi daftar dan kamus | 3,03 dtk | 0,39 dtk | 8× |
| Menyambung teks 100.000 kali (`s = s + "x"`) | 0,76 dtk | 0,93 dtk | ±1× |

## Perbedaan yang disengaja dengan interpreter Python

1. **Pangkat dan logaritma dibulatkan tepat.** `pow()` milik pustaka C (yang dipakai Python di Linux) meleset 1 digit biner di ±0,05% kasus, sehingga di Python `x ** 2` kadang tidak sama dengan `x * x`. Mesin Go selalu memberi hasil yang paling dekat dengan nilai sebenarnya, dan hasilnya sama di Windows, macOS, Linux, dan browser. Tampilan desimal (12 angka penting) tidak terpengaruh.
2. **Tidak ada exception Python mentah.** Di beberapa tempat interpreter Python membocorkan exception Python yang tidak bisa dibaca pemula, misalnya `rentang(10 ** 12)` (`MemoryError`), atau berhenti sangat lama, misalnya `7 ** (2 ** 64)`. Mesin Go memberi pesan berbahasa Indonesia: `'rentang' tidak bisa menghitung dengan nilai ini` dan `Hasil perhitungan terlalu besar`.
3. **Ekspresi yang bersarang sangat dalam** (lebih dari ±1.000 tingkat kurung) menjadi `KesalahanTumpukan`. Interpreter Python sudah gagal di sekitar 80 tingkat dengan "Kesalahan internal".
4. **Kelas induk yang bukan kelas** (`kelas K mewarisi 5:`) langsung ditolak saat kelas dibuat, bukan gagal belakangan dengan kesalahan internal.
5. **Perintah `indonesia`** mengabaikan tanda BOM di awal berkas (disimpan sebagian editor Windows) dan memberi pesan yang jelas bila yang dijalankan ternyata folder.
6. Huruf besar/kecil untuk segelintir huruf khusus Unicode (ß, İ, sigma Yunani di akhir kata) dan urutan `urutkan` pada daftar yang berisi `nan` bisa berbeda.
