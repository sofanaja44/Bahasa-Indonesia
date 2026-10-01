//go:build js && wasm

// Perintah wasm adalah mesin Bahasa Indonesia untuk editor web: WebAssembly yang berjalan di
// Web Worker (web/pekerja.js).
//
//	GOOS=js GOARCH=wasm go build -o mesin.wasm ./cmd/wasm
//
// Setelah dimuat, ia mendaftarkan fungsi global JavaScript:
//
//	jalankanIndonesia(kode[, opsi]) → teks JSON: {} bila berhasil, {"jenis", "pesan", "baris",
//	"kolom"} bila program berhenti karena kesalahan, {"jenis": "dihentikan"}, atau
//	{"jenis": "internal", "pesan"}. opsi (teks JSON, hanya untuk pengujian) boleh berisi
//	"benih" (benih acak), "sekarang" (jam tetap, mis. "2026-10-01T14:30:45"), "berkasBaru"
//	(sistem berkas kosong), dan "repl" (hasil juga memuat "hasil": nilai ekspresi terakhir).
//	versiIndonesia → nomor versi mesin.
//
// dan memakai fungsi yang disediakan pekerja.js:
//
//	tulisKeluaran(saluran, teks) → bool   benar bila tombol Hentikan ditekan
//	mintaMasukan() → teks JSON            {"teks"}, {"berhenti": true}, atau {"gagal": pesan}
//	tidur(milidetik) → bool               benar bila tombol Hentikan ditekan
//	periksaBerhenti() → bool              benar bila tombol Hentikan ditekan
package main

import (
	"encoding/json"
	"errors"
	"syscall/js"
	"time"

	"github.com/sofanaja44/Bahasa-Indonesia/mesin"
)

// Berkas yang ditulis program tetap ada selama halaman editor terbuka.
var berkas = mesin.NewBerkasMemori()

type opsiUji struct {
	Benih      *int64 `json:"benih"`
	Sekarang   string `json:"sekarang"`
	BerkasBaru bool   `json:"berkasBaru"`
	REPL       bool   `json:"repl"`
}

type hasilJalan struct {
	Jenis string  `json:"jenis,omitempty"`
	Pesan string  `json:"pesan,omitempty"`
	Baris *int    `json:"baris,omitempty"`
	Kolom *int    `json:"kolom,omitempty"`
	Hasil *string `json:"hasil,omitempty"`
}

func posisi(n int) *int {
	if n < 0 {
		return nil // tidak diketahui (None di Python)
	}
	return &n
}

func jalankan(kode string, opsi opsiUji) hasilJalan {
	global := js.Global()
	berhenti := false
	terakhirDiperiksa := time.Now()
	tulis := func(teks string) {
		if global.Call("tulisKeluaran", "keluaran", teks).Bool() {
			berhenti = true
		}
	}
	io := mesin.IO{
		Tulis: tulis,
		Baca: func(prompt string) (string, bool) {
			if prompt != "" {
				tulis(prompt)
			}
			if berhenti {
				return "", true // mesin memeriksa Berhenti() sesudah membaca
			}
			var jawaban struct {
				Teks     *string `json:"teks"`
				Berhenti bool    `json:"berhenti"`
				Gagal    *string `json:"gagal"`
			}
			if err := json.Unmarshal([]byte(global.Call("mintaMasukan").String()), &jawaban); err != nil {
				panic(mesin.BuatKesalahan(mesin.KNilai, "Masukan tidak bisa dibaca"))
			}
			switch {
			case jawaban.Berhenti:
				berhenti = true
				return "", true
			case jawaban.Gagal != nil:
				panic(mesin.BuatKesalahan(mesin.KNilai, *jawaban.Gagal))
			case jawaban.Teks == nil:
				return "", false
			}
			return *jawaban.Teks, true
		},
		Tidur: func(detik float64) {
			if global.Call("tidur", detik*1000).Bool() {
				berhenti = true
			}
		},
		// Diperiksa mesin setiap ±1.000 instruksi; saluran ke service worker cukup ditanya
		// paling sering tiap 50 ms, sehingga perulangan tanpa keluaran pun bisa dihentikan.
		Berhenti: func() bool {
			if !berhenti && time.Since(terakhirDiperiksa) > 50*time.Millisecond {
				terakhirDiperiksa = time.Now()
				berhenti = global.Call("periksaBerhenti").Bool()
			}
			return berhenti
		},
		Berkas: berkas,
	}
	if opsi.Sekarang != "" {
		if t, err := time.ParseInLocation("2006-01-02T15:04:05", opsi.Sekarang, time.Local); err == nil {
			io.Sekarang = func() time.Time { return t }
		}
	}
	if opsi.BerkasBaru {
		io.Berkas = mesin.NewBerkasMemori()
	}
	m := mesin.Baru(io)
	if opsi.Benih != nil {
		m.AturBenih(*opsi.Benih)
	}
	nilai, ada, err := m.JalankanREPL(kode)
	var k *mesin.Kesalahan
	switch {
	case err == nil:
		if opsi.REPL && ada && nilai != nil {
			teks := mesin.KeTeks(nilai)
			return hasilJalan{Hasil: &teks}
		}
		return hasilJalan{}
	case errors.As(err, &k):
		return hasilJalan{Jenis: k.Jenis, Pesan: k.Teks(), Baris: posisi(k.Baris), Kolom: posisi(k.Kolom)}
	case errors.Is(err, mesin.ErrDihentikan):
		return hasilJalan{Jenis: "dihentikan"}
	}
	return hasilJalan{Jenis: "internal", Pesan: err.Error()}
}

func main() {
	js.Global().Set("versiIndonesia", mesin.Versi)
	js.Global().Set("jalankanIndonesia", js.FuncOf(func(this js.Value, args []js.Value) any {
		var opsi opsiUji
		if len(args) > 1 && args[1].Type() == js.TypeString {
			_ = json.Unmarshal([]byte(args[1].String()), &opsi)
		}
		hasil, _ := json.Marshal(jalankan(args[0].String(), opsi))
		return string(hasil)
	}))
	select {} // tetap hidup agar jalankanIndonesia bisa dipanggil berkali-kali
}
