package mesin

import (
	"strconv"
	"strings"
)

// Jenis-jenis kesalahan; sama dengan kelas di src/errors.py.
const (
	KSintaks    = "KesalahanSintaks"
	KNama       = "KesalahanNama"
	KTipe       = "KesalahanTipe"
	KIndeks     = "KesalahanIndeks"
	KBagiNol    = "KesalahanBagiNol"
	KBerkas     = "KesalahanBerkas"
	KKunci      = "KesalahanKunci"
	KNilai      = "KesalahanNilai"
	KTumpukan   = "KesalahanTumpukan"
	tanpaPosisi = -1 // baris/kolom tidak diketahui (None di Python)
)

// semuaJenisKesalahan berurutan seperti KesalahanIndonesia.__subclasses__().
var semuaJenisKesalahan = []string{KSintaks, KNama, KTipe, KIndeks, KBagiNol, KBerkas, KKunci, KNilai, KTumpukan}

// Kesalahan adalah kesalahan berbahasa Indonesia yang ditampilkan kepada pengguna.
type Kesalahan struct {
	Jenis        string
	Pesan        string
	Baris        int // tanpaPosisi bila tidak diketahui
	Kolom        int // tanpaPosisi bila tidak diketahui
	BarisKode    string
	AdaBarisKode bool
	// BelumSelesai: kesalahan sintaks di akhir masukan, artinya kode belum selesai ditulis (REPL).
	BelumSelesai bool
}

func kesalahan(jenis, pesan string, baris, kolom int) *Kesalahan {
	return &Kesalahan{Jenis: jenis, Pesan: pesan, Baris: baris, Kolom: kolom}
}

// kesalahanTanpaLokasi dipakai fungsi bawaan; VM menambahkan lokasi pemanggilnya.
func kesalahanTanpaLokasi(jenis, pesan string) *Kesalahan {
	return kesalahan(jenis, pesan, tanpaPosisi, tanpaPosisi)
}

func (k *Kesalahan) Error() string { return k.Teks() }

// Teks sama dengan KesalahanIndonesia.format_pesan().
func (k *Kesalahan) Teks() string {
	var b strings.Builder
	b.WriteString("❌ ")
	b.WriteString(k.Jenis)
	if k.Baris != tanpaPosisi {
		b.WriteString(" pada baris ")
		b.WriteString(strconv.Itoa(k.Baris))
		if k.Kolom != tanpaPosisi {
			b.WriteString(", kolom ")
			b.WriteString(strconv.Itoa(k.Kolom))
		}
	}
	b.WriteString(":\n\n")
	if k.AdaBarisKode {
		b.WriteString("    ")
		b.WriteString(k.BarisKode)
		b.WriteString("\n")
		if k.Kolom != tanpaPosisi && k.Kolom > 0 {
			b.WriteString("    ")
			b.WriteString(strings.Repeat(" ", k.Kolom-1))
			b.WriteString("^\n")
		}
		b.WriteString("\n")
	}
	b.WriteString("  ")
	b.WriteString(k.Pesan)
	return b.String()
}

// denganLokasi menambahkan baris & kolom bila kesalahan belum punya lokasi (_dengan_lokasi).
func (k *Kesalahan) denganLokasi(baris, kolom int) *Kesalahan {
	if k.Baris != tanpaPosisi || k == errBersarang {
		return k
	}
	return kesalahan(k.Jenis, k.Pesan, baris, kolom)
}

// ---- Nama jenis kesalahan untuk 'tangkap NAMA' ----

var padananPython = map[string]string{
	KSintaks: "SyntaxError", KNama: "NameError", KTipe: "TypeError", KIndeks: "IndexError",
	KBagiNol: "ZeroDivisionError", KBerkas: "FileNotFoundError", KKunci: "KeyError",
	KNilai: "ValueError", KTumpukan: "RecursionError",
}

var namaSemuaKesalahan = []string{"kesalahan", "kesalahanindonesia", "error", "exception"}

func adalahNamaSemuaKesalahan(nama string) bool {
	for _, n := range namaSemuaKesalahan {
		if n == nama {
			return true
		}
	}
	return false
}

// cocokTangkap: apakah 'tangkap nama' menangkap kesalahan berjenis ini (nama_tangkap).
func cocokTangkap(jenis, nama string) bool {
	nama = strings.ToLower(nama)
	if adalahNamaSemuaKesalahan(nama) {
		return true
	}
	return nama == strings.ToLower(jenis) || nama == strings.ToLower(padananPython[jenis])
}

// semuaNamaTangkap: huruf kecil → penulisan baku, untuk memeriksa 'tangkap NAMA' saat parsing.
func semuaNamaTangkap() map[string]string {
	hasil := map[string]string{}
	for _, n := range namaSemuaKesalahan {
		hasil[n] = "Kesalahan"
	}
	for _, j := range semuaJenisKesalahan {
		hasil[strings.ToLower(j)] = j
		hasil[strings.ToLower(padananPython[j])] = padananPython[j]
	}
	return hasil
}
