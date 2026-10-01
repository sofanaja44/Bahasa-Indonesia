package mesin

import (
	"math"
	"math/big"
	"sort"
	"strconv"
	"strings"
	"unicode"
	"unicode/utf8"
)

// FungsiBawaan adalah fungsi yang ditulis dalam Go: fungsi bawaan, metode daftar/kamus/teks, dan isi modul.
type FungsiBawaan struct {
	Nama     string
	min, max int // jumlah argumen yang diterima; max < 0 berarti tidak dibatasi
	fn       func(m *Mesin, args []any) any
	terikat  any // pemilik metode daftar/kamus: dua metode sama bila pemilik dan namanya sama
}

func bawaan(nama string, min, max int, fn func(m *Mesin, args []any) any) *FungsiBawaan {
	return &FungsiBawaan{Nama: nama, min: min, max: max, fn: fn}
}

func galatTipe(pesan string) *Kesalahan  { return kesalahanTanpaLokasi(KTipe, pesan) }
func galatNilai(pesan string) *Kesalahan { return kesalahanTanpaLokasi(KNilai, pesan) }

// argumen: argumen ke-i, atau nilai bawaan bila tidak diberikan.
func argumen(args []any, i int, asal any) any {
	if i < len(args) {
		return args[i]
	}
	return asal
}

type pasanganBawaan struct {
	nama string
	fn   *FungsiBawaan
}

// daftarFungsiBawaan sama dengan daftar_fungsi_bawaan() di src/builtins.py.
func daftarFungsiBawaan() []pasanganBawaan {
	tampilkan := bawaan("tampilkan", 0, -1, fungsiTampilkan(true))
	kesalahan := bawaan("Kesalahan", 0, 1, func(m *Mesin, a []any) any { return keTeks(argumen(a, 0, "")) })
	return []pasanganBawaan{
		{"tampilkan", tampilkan},
		{"cetak", bawaan("cetak", 0, -1, fungsiTampilkan(false))},
		{"tulis", tampilkan},
		{"masukan", bawaan("masukan", 0, 1, func(m *Mesin, a []any) any { return m.bacaMasukan(argumen(a, 0, "")) })},
		{"masukan_angka", bawaan("masukan_angka", 0, 1, masukanAngka)},
		{"masukan_desimal", bawaan("masukan_desimal", 0, 1, masukanDesimal)},
		{"tanya", bawaan("tanya", 0, 1, func(m *Mesin, a []any) any { return m.tanya(argumen(a, 0, ""), "teks") })},
		{"ubah_angka", bawaan("ubah_angka", 1, 1, ubahAngka)},
		{"ubah_desimal", bawaan("ubah_desimal", 1, 1, ubahDesimal)},
		{"ubah_teks", bawaan("ubah_teks", 1, 1, func(m *Mesin, a []any) any { return keTeks(a[0]) })},
		{"ubah_logika", bawaan("ubah_logika", 1, 1, func(m *Mesin, a []any) any { return benarkah(a[0]) })},
		{"panjang", bawaan("panjang", 1, 1, panjang)},
		{"jenis", bawaan("jenis", 1, 1, func(m *Mesin, a []any) any { return jenisNilai(a[0]) })},
		{"rentang", bawaan("rentang", 0, -1, rentang)},
		{"mutlak", bawaan("mutlak", 1, 1, func(m *Mesin, a []any) any { return mutlak(pastikanAngka(a[0], "mutlak")) })},
		{"maksimum", bawaan("maksimum", 0, -1, ekstrem("maksimum", true))},
		{"minimum", bawaan("minimum", 0, -1, ekstrem("minimum", false))},
		{"jumlah", bawaan("jumlah", 1, 1, jumlah)},
		{"diurutkan", bawaan("diurutkan", 1, 1, diurutkan)},
		{"dibalik", bawaan("dibalik", 1, 1, dibalik)},
		{"tunggu", bawaan("tunggu", 1, 1, func(m *Mesin, a []any) any { m.tungguDetik(a[0], 1); return nil })},
		{"Kesalahan", kesalahan},
		{"Error", kesalahan},
	}
}

// ---- Validasi ----

func pastikanAngka(x any, nama string) any {
	if !adalahAngkaMurni(x) {
		panic(galatTipe("'" + nama + "' membutuhkan angka, bukan '" + keTeks(x) + "'"))
	}
	return x
}

func pastikanBulat(x any, nama string) any {
	switch x.(type) {
	case int, *big.Int:
		return x
	}
	panic(galatTipe("'" + nama + "' membutuhkan bilangan bulat, bukan '" + keTeks(x) + "'"))
}

// hurufHuruf memecah teks menjadi daftar huruf (list(teks) di Python).
func hurufHuruf(s string) []any {
	isi := make([]any, 0, len(s))
	for _, r := range s {
		isi = append(isi, string(r))
	}
	return isi
}

func isiKoleksi(x any, nama string) []any {
	if d, ok := x.(*Daftar); ok {
		return d.Elemen
	}
	if s, ok := teksDari(x); ok {
		return hurufHuruf(s)
	}
	panic(galatTipe("'" + nama + "' membutuhkan daftar, bukan '" + keTeks(x) + "'"))
}

// ---- Masukan & keluaran ----

func fungsiTampilkan(barisBaru bool) func(m *Mesin, args []any) any {
	return func(m *Mesin, args []any) any {
		var b strings.Builder
		for i, a := range args {
			if i > 0 {
				b.WriteByte(' ')
			}
			tulisTeks(&b, a, 0)
		}
		if barisBaru {
			b.WriteByte('\n')
		}
		m.io.Tulis(b.String())
		return nil
	}
}

func (m *Mesin) periksaBerhenti() {
	if m.io.Berhenti != nil && m.io.Berhenti() {
		panic(ErrDihentikan)
	}
}

// bacaMasukan sama dengan _baca_masukan().
func (m *Mesin) bacaMasukan(prompt any) string {
	teks := ""
	if benarkah(prompt) {
		teks = keTeks(prompt)
	}
	jawaban, ok := m.io.Baca(teks)
	m.periksaBerhenti()
	if !ok {
		panic(galatNilai("Tidak ada lagi masukan yang bisa dibaca"))
	}
	return jawaban
}

func masukanAngka(m *Mesin, a []any) any {
	teks := m.bacaMasukan(argumen(a, 0, ""))
	angka := teksKeAngka(teks)
	if f, ok := angka.(float64); ok && f == math.Trunc(f) {
		angka = floatKeBulat(f)
	}
	switch angka.(type) {
	case int, *big.Int:
		return angka
	}
	panic(galatNilai("Masukan '" + teks + "' bukan bilangan bulat"))
}

func masukanDesimal(m *Mesin, a []any) any {
	teks := m.bacaMasukan(argumen(a, 0, ""))
	angka := teksKeAngka(teks)
	if angka == nil {
		panic(galatNilai("Masukan '" + teks + "' bukan angka"))
	}
	f, _ := keFloat(angka)
	return f
}

// tanya: untuk angka, pertanyaan diulang sampai jawabannya benar-benar angka.
func (m *Mesin) tanya(pertanyaan any, jenis string) any {
	for {
		jawaban := m.bacaMasukan(pertanyaan)
		if jenis == "teks" {
			return jawaban
		}
		if angka := teksKeAngka(jawaban); angka != nil {
			return angka
		}
		m.io.Tulis("Tolong jawab dengan angka.\n")
	}
}

// tungguDetik sama dengan tunggu() di src/builtins.py.
func (m *Mesin) tungguDetik(lama any, faktor float64) {
	if !adalahAngkaMurni(lama) {
		panic(galatNilai("'tunggu' membutuhkan angka sebagai lamanya menunggu, bukan '" + keTeks(lama) + "'"))
	}
	if bandingAngka(lama, 0) == -1 {
		panic(galatNilai("Lama menunggu tidak boleh negatif"))
	}
	f, _ := keFloat(lama)
	detik := f * faktor
	if math.IsNaN(detik) {
		panic(galatPython{"ValueError"})
	}
	if detik > 9e9 { // time.sleep() menolak lama yang lebih dari ±292 tahun
		panic(galatPython{"OverflowError"})
	}
	m.io.Tidur(detik)
	m.periksaBerhenti()
}

// ---- Konversi ----

// floatKeBulat: int(x) untuk desimal yang terhingga.
func floatKeBulat(f float64) any {
	f = math.Trunc(f)
	if math.Abs(f) < 1<<62 {
		return int(f)
	}
	b, _ := new(big.Float).SetFloat64(f).Int(nil)
	return normalBulat(b)
}

// floatKeBulatPython sama dengan int(float) Python, termasuk kesalahannya.
func floatKeBulatPython(f float64) any {
	if math.IsNaN(f) {
		panic(galatPython{"ValueError"})
	}
	if math.IsInf(f, 0) {
		panic(galatPython{"OverflowError"})
	}
	return floatKeBulat(f)
}

func ubahAngka(m *Mesin, a []any) any {
	x := a[0]
	switch v := x.(type) {
	case bool, int, *big.Int:
		return normalBulat(keBig(v))
	case float64:
		return floatKeBulatPython(v)
	}
	if s, ok := teksDari(x); ok {
		switch angka := teksKeAngka(s).(type) {
		case int, *big.Int:
			return angka
		case float64:
			panic(galatNilai("'" + s + "' bukan bilangan bulat; gunakan ubah_desimal"))
		}
	}
	panic(galatNilai("Tidak bisa mengubah '" + keTeks(x) + "' menjadi bilangan"))
}

func ubahDesimal(m *Mesin, a []any) any {
	x := a[0]
	if adalahAngkaNilai(x) {
		f, _ := keFloat(x)
		return f
	}
	if s, ok := teksDari(x); ok {
		if angka := teksKeAngka(s); angka != nil {
			f, _ := keFloat(angka)
			return f
		}
	}
	panic(galatNilai("Tidak bisa mengubah '" + keTeks(x) + "' menjadi angka desimal"))
}

// ---- Utilitas ----

func panjang(m *Mesin, a []any) any {
	switch v := a[0].(type) {
	case *Daftar:
		return len(v.Elemen)
	case *Kamus:
		return v.Panjang()
	}
	if s, ok := teksDari(a[0]); ok {
		return utf8.RuneCountInString(s)
	}
	panic(galatTipe("Tidak bisa menghitung panjang " + jenisNilai(a[0])))
}

const batasPanjangDaftar = 1 << 25 // daftar yang lebih panjang dianggap kehabisan memori

func rentang(m *Mesin, args []any) any {
	if len(args) < 1 || len(args) > 3 {
		panic(galatNilai("rentang membutuhkan 1 sampai 3 angka, mis. rentang(1, 10)"))
	}
	for _, a := range args {
		switch a.(type) {
		case int, *big.Int:
		default:
			panic(galatTipe("rentang membutuhkan bilangan bulat, bukan '" + keTeks(a) + "'"))
		}
	}
	if len(args) == 3 && samaDengan(args[2], 0) {
		panic(galatNilai("Langkah rentang tidak boleh nol"))
	}
	var mulai, akhir, langkah any = 0, args[0], 1
	if len(args) >= 2 {
		mulai, akhir = args[0], args[1]
	}
	if len(args) == 3 {
		langkah = args[2]
	}
	// Panjang seperti range(): (akhir - mulai - 1) // langkah + 1 bila arahnya benar.
	jarak := kurangBulat(akhir, mulai)
	var n *big.Int
	if bandingAngka(langkah, 0) == 1 {
		if bandingAngka(jarak, 0) != 1 {
			return &Daftar{}
		}
		n = new(big.Int).Div(keBig(kurangBulat(jarak, 1)), keBig(langkah))
	} else {
		if bandingAngka(jarak, 0) != -1 {
			return &Daftar{}
		}
		n = new(big.Int).Div(new(big.Int).Neg(keBig(tambahBulat(jarak, 1))), new(big.Int).Neg(keBig(langkah)))
	}
	n.Add(n, big.NewInt(1))
	if !n.IsInt64() || n.Int64() > batasPanjangDaftar {
		panic(galatPython{"MemoryError"})
	}
	jumlah := int(n.Int64())
	isi := make([]any, jumlah)
	// Jalur cepat bila semua nilainya muat di 64 bit (nilai pertama & terakhir muat).
	x, ok1 := mulai.(int)
	l, ok2 := langkah.(int)
	if ok1 && ok2 {
		if geser, ok := kaliBulat(l, jumlah-1).(int); ok {
			if _, ok := tambahBulat(x, geser).(int); ok {
				for i := range isi {
					isi[i] = x + i*l
				}
				return &Daftar{isi}
			}
		}
	}
	nilai := mulai
	for i := range isi {
		isi[i] = nilai
		nilai = tambahBulat(nilai, langkah)
	}
	return &Daftar{isi}
}

func mutlak(x any) any {
	switch v := x.(type) {
	case int:
		if v < 0 {
			return negasiBulat(v)
		}
		return v
	case *big.Int:
		return normalBulat(new(big.Int).Abs(v))
	case float64:
		return math.Abs(v)
	}
	return x
}

func negasiBulat(v int) any {
	if v == math.MinInt64 {
		return new(big.Int).Neg(big.NewInt(int64(v)))
	}
	return -v
}

// ekstrem: maksimum(3, 7) / maksimum([3, 7]). Seperti max() Python, nilai pertama menang bila seri.
func ekstrem(nama string, cariMaks bool) func(m *Mesin, args []any) any {
	return func(m *Mesin, args []any) any {
		isi := args
		if len(isi) == 1 {
			if d, ok := isi[0].(*Daftar); ok {
				isi = d.Elemen
			}
		}
		if len(isi) == 0 {
			panic(galatNilai("'" + nama + "' membutuhkan paling sedikit satu nilai"))
		}
		hasil := isi[0]
		for _, x := range isi[1:] {
			c, ok := banding(x, hasil)
			if !ok {
				panic(galatTipe("'" + nama + "' tidak bisa membandingkan nilai yang jenisnya berbeda-beda"))
			}
			if (cariMaks && c == 1) || (!cariMaks && c == -1) {
				hasil = x
			}
		}
		return hasil
	}
}

func jumlah(m *Mesin, a []any) any {
	isi := isiKoleksi(a[0], "jumlah")
	for _, e := range isi {
		pastikanAngka(e, "jumlah")
	}
	return jumlahPython(isi)
}

// jumlahPython sama dengan sum() Python 3.12+: bilangan bulat dijumlahkan tepat, desimal dengan
// penjumlahan Neumaier (sum([0.1] * 10) tepat 1.0).
func jumlahPython(isi []any) any {
	i, total := 0, 0
	for ; i < len(isi); i++ {
		x, ok := isi[i].(int)
		if !ok {
			break
		}
		s := total + x
		if (s > total) != (x > 0) && x != 0 {
			break // melewati batas 64 bit
		}
		total = s
	}
	if i == len(isi) {
		return total
	}
	var hasil any = tambahAngka(total, isi[i])
	i++
	if f, ok := hasil.(float64); ok {
		c := 0.0
	desimal:
		for ; i < len(isi); i++ {
			switch x := isi[i].(type) {
			case float64:
				t := f + x
				if math.Abs(f) >= math.Abs(x) {
					c += (f - t) + x
				} else {
					c += (x - t) + f
				}
				f = t
			case int:
				f += float64(x)
			default:
				break desimal
			}
		}
		if c != 0 && !math.IsInf(c, 0) && !math.IsNaN(c) {
			f += c
		}
		hasil = f
	}
	for ; i < len(isi); i++ {
		hasil = tambahAngka(hasil, isi[i])
	}
	return hasil
}

// urutkanPython mengurutkan seperti sorted() Python (stabil, memakai <). false bila isinya tidak
// bisa dibandingkan satu sama lain (TypeError di Python).
func urutkanPython(isi []any) bool {
	if len(isi) < 2 {
		return true
	}
	angka, teks := 0, 0
	for _, e := range isi {
		switch {
		case adalahAngkaNilai(e):
			angka++
		default:
			if _, ok := teksDari(e); !ok {
				return false
			}
			teks++
		}
	}
	if angka > 0 && teks > 0 {
		return false
	}
	sort.SliceStable(isi, func(i, j int) bool {
		c, _ := banding(isi[i], isi[j])
		return c == -1
	})
	return true
}

const pesanTidakBisaDiurutkan = "Isi daftar tidak bisa diurutkan karena jenis datanya berbeda-beda"

func diurutkan(m *Mesin, a []any) any {
	isi := append([]any(nil), isiKoleksi(a[0], "diurutkan")...)
	if !urutkanPython(isi) {
		panic(galatTipe(pesanTidakBisaDiurutkan))
	}
	return &Daftar{isi}
}

func dibalik(m *Mesin, a []any) any {
	isi := isiKoleksi(a[0], "dibalik")
	hasil := make([]any, len(isi))
	for i, e := range isi {
		hasil[len(isi)-1-i] = e
	}
	return &Daftar{hasil}
}

// ---- Waktu ----

var namaHari = []string{"Senin", "Selasa", "Rabu", "Kamis", "Jumat", "Sabtu", "Minggu"}
var namaBulan = []string{"Januari", "Februari", "Maret", "April", "Mei", "Juni",
	"Juli", "Agustus", "September", "Oktober", "November", "Desember"}

// bacaWaktu sama dengan baca_waktu(): jam/menit/detik/tahun → angka, sisanya teks.
func (m *Mesin) bacaWaktu(bagian string) any {
	t := m.io.Sekarang()
	switch bagian {
	case "jam":
		return t.Hour()
	case "menit":
		return t.Minute()
	case "detik":
		return t.Second()
	case "hari":
		return namaHari[(int(t.Weekday())+6)%7]
	case "tanggal":
		return strconv.Itoa(t.Day()) + " " + namaBulan[t.Month()-1] + " " + strconv.Itoa(t.Year())
	case "bulan":
		return namaBulan[t.Month()-1]
	case "tahun":
		return t.Year()
	}
	return t.Format("15:04:05")
}

// ---- Metode daftar, kamus, dan teks ----

type metode struct {
	min, max int
	fn       func(m *Mesin, diri any, a []any) any
}

func hapusIndeks(d *Daftar, i int) {
	copy(d.Elemen[i:], d.Elemen[i+1:])
	d.Elemen[len(d.Elemen)-1] = nil
	d.Elemen = d.Elemen[:len(d.Elemen)-1]
}

func pastikanPosisi(x any) any {
	switch x.(type) {
	case int, *big.Int:
		return x
	}
	panic(galatTipe("Posisi harus bilangan bulat, bukan '" + keTeks(x) + "'"))
}

var metodeDaftar = map[string]metode{
	"tambahkan": {1, 1, func(m *Mesin, diri any, a []any) any {
		d := diri.(*Daftar)
		d.Elemen = append(d.Elemen, a[0])
		return nil
	}},
	"hapus": {1, 1, func(m *Mesin, diri any, a []any) any {
		d := diri.(*Daftar)
		for i, e := range d.Elemen {
			if samaDengan(e, a[0]) {
				hapusIndeks(d, i)
				return nil
			}
		}
		panic(galatNilai("'" + keTeks(a[0]) + "' tidak ada di dalam daftar"))
	}},
	"hapusPosisi": {1, 1, func(m *Mesin, diri any, a []any) any {
		d := diri.(*Daftar)
		idx := pastikanPosisi(a[0])
		i, ok := indeksPython(idx, len(d.Elemen))
		if !ok {
			panic(kesalahanTanpaLokasi(KIndeks, "Posisi "+reprNilai(idx)+" di luar batas daftar (panjangnya "+
				strconv.Itoa(len(d.Elemen))+")"))
		}
		v := d.Elemen[i]
		hapusIndeks(d, i)
		return v
	}},
	"sisipkan": {2, 2, func(m *Mesin, diri any, a []any) any {
		d := diri.(*Daftar)
		i, ok := bulatKeInt(pastikanPosisi(a[0]))
		if !ok {
			panic(galatPython{"OverflowError"})
		}
		n := len(d.Elemen)
		if i < 0 {
			i += n
			if i < 0 {
				i = 0
			}
		}
		if i > n {
			i = n
		}
		d.Elemen = append(d.Elemen, nil)
		copy(d.Elemen[i+1:], d.Elemen[i:])
		d.Elemen[i] = a[1]
		return nil
	}},
	"panjang": {0, 0, func(m *Mesin, diri any, a []any) any { return len(diri.(*Daftar).Elemen) }},
	"urutkan": {0, 0, func(m *Mesin, diri any, a []any) any {
		d := diri.(*Daftar)
		isi := append([]any(nil), d.Elemen...)
		if !urutkanPython(isi) {
			panic(galatTipe(pesanTidakBisaDiurutkan))
		}
		copy(d.Elemen, isi)
		return nil
	}},
	"balik": {0, 0, func(m *Mesin, diri any, a []any) any {
		e := diri.(*Daftar).Elemen
		for i, j := 0, len(e)-1; i < j; i, j = i+1, j-1 {
			e[i], e[j] = e[j], e[i]
		}
		return nil
	}},
	"cari": {1, 1, func(m *Mesin, diri any, a []any) any {
		for i, e := range diri.(*Daftar).Elemen {
			if samaDengan(e, a[0]) {
				return i
			}
		}
		return -1
	}},
	"salin": {0, 0, func(m *Mesin, diri any, a []any) any {
		return &Daftar{append([]any(nil), diri.(*Daftar).Elemen...)}
	}},
	"kosongkan": {0, 0, func(m *Mesin, diri any, a []any) any {
		diri.(*Daftar).Elemen = nil
		return nil
	}},
	"gabung": {0, 1, func(m *Mesin, diri any, a []any) any {
		pemisah := keTeks(argumen(a, 0, " "))
		e := diri.(*Daftar).Elemen
		bagian := make([]string, len(e))
		for i, x := range e {
			bagian[i] = keTeks(x)
		}
		return strings.Join(bagian, pemisah)
	}},
}

var metodeKamus = map[string]metode{
	"kunci": {0, 0, func(m *Mesin, diri any, a []any) any {
		return &Daftar{append([]any(nil), diri.(*Kamus).kunci...)}
	}},
	"nilai": {0, 0, func(m *Mesin, diri any, a []any) any {
		return &Daftar{append([]any(nil), diri.(*Kamus).nilai...)}
	}},
	"pasang": {0, 0, func(m *Mesin, diri any, a []any) any {
		k := diri.(*Kamus)
		isi := make([]any, len(k.kunci))
		for i := range k.kunci {
			isi[i] = &Daftar{[]any{k.kunci[i], k.nilai[i]}}
		}
		return &Daftar{isi}
	}},
	"adaKunci": {1, 1, func(m *Mesin, diri any, a []any) any { return diri.(*Kamus).Ada(a[0]) }},
	"hapusKunci": {1, 1, func(m *Mesin, diri any, a []any) any {
		if !diri.(*Kamus).Hapus(a[0]) {
			panic(kesalahanTanpaLokasi(KKunci, "Kunci '"+keTeks(a[0])+"' tidak ditemukan di kamus"))
		}
		return nil
	}},
	"dapatkan": {1, 2, func(m *Mesin, diri any, a []any) any {
		if v, ada := diri.(*Kamus).Ambil(a[0]); ada {
			return v
		}
		return argumen(a, 1, nil)
	}},
}

func pastikanTeks(x any, metode string) string {
	if s, ok := teksDari(x); ok {
		return s
	}
	panic(galatTipe("Metode teks '" + metode + "' membutuhkan teks, bukan '" + keTeks(x) + "'"))
}

// belahSpasi sama dengan str.split() tanpa pemisah.
func belahSpasi(s string) []string {
	return strings.FieldsFunc(s, adalahSpasiPython)
}

// hurufAwalBesar sama dengan string.capwords().
func hurufAwalBesar(s string) string {
	kata := belahSpasi(s)
	for i, k := range kata {
		r, n := utf8.DecodeRuneInString(k)
		kata[i] = string(unicode.ToTitle(r)) + strings.ToLower(k[n:])
	}
	return strings.Join(kata, " ")
}

// cariTeks sama dengan str.find(): posisi huruf (bukan byte), -1 bila tidak ada.
func cariTeks(s, bagian string) int {
	i := strings.Index(s, bagian)
	if i < 0 {
		return -1
	}
	return utf8.RuneCountInString(s[:i])
}

func teksDaftar(bagian []string) *Daftar {
	isi := make([]any, len(bagian))
	for i, b := range bagian {
		isi[i] = b
	}
	return &Daftar{isi}
}

var metodeTeks = map[string]metode{
	"panjang":     {0, 0, func(m *Mesin, diri any, a []any) any { return utf8.RuneCountInString(diri.(string)) }},
	"huruf_besar": {0, 0, func(m *Mesin, diri any, a []any) any { return strings.ToUpper(diri.(string)) }},
	"huruf_kecil": {0, 0, func(m *Mesin, diri any, a []any) any { return strings.ToLower(diri.(string)) }},
	"huruf_awal_besar": {0, 0, func(m *Mesin, diri any, a []any) any {
		return hurufAwalBesar(diri.(string))
	}},
	"potong_spasi": {0, 0, func(m *Mesin, diri any, a []any) any { return potongSpasi(diri.(string)) }},
	"belah": {0, 1, func(m *Mesin, diri any, a []any) any {
		p := argumen(a, 0, nil)
		if p == nil {
			return teksDaftar(belahSpasi(diri.(string)))
		}
		pemisah := pastikanTeks(p, "belah")
		if pemisah == "" {
			panic(galatPython{"ValueError"}) // empty separator
		}
		return teksDaftar(strings.Split(diri.(string), pemisah))
	}},
	"ganti": {2, 2, func(m *Mesin, diri any, a []any) any {
		return strings.ReplaceAll(diri.(string), pastikanTeks(a[0], "ganti"), keTeks(a[1]))
	}},
	"berisi": {1, 1, func(m *Mesin, diri any, a []any) any {
		return strings.Contains(diri.(string), pastikanTeks(a[0], "berisi"))
	}},
	"diawali": {1, 1, func(m *Mesin, diri any, a []any) any {
		return strings.HasPrefix(diri.(string), pastikanTeks(a[0], "diawali"))
	}},
	"diakhiri": {1, 1, func(m *Mesin, diri any, a []any) any {
		return strings.HasSuffix(diri.(string), pastikanTeks(a[0], "diakhiri"))
	}},
	"cari": {1, 1, func(m *Mesin, diri any, a []any) any {
		return cariTeks(diri.(string), pastikanTeks(a[0], "cari"))
	}},
	"balik": {0, 0, func(m *Mesin, diri any, a []any) any {
		r := []rune(diri.(string))
		for i, j := 0, len(r)-1; i < j; i, j = i+1, j-1 {
			r[i], r[j] = r[j], r[i]
		}
		return string(r)
	}},
	"berupa_angka": {0, 0, func(m *Mesin, diri any, a []any) any { return teksKeAngka(diri.(string)) != nil }},
	"mulai_dengan": {1, 1, func(m *Mesin, diri any, a []any) any {
		return strings.HasPrefix(diri.(string), pastikanTeks(a[0], "mulai_dengan"))
	}},
	"akhir_dengan": {1, 1, func(m *Mesin, diri any, a []any) any {
		return strings.HasSuffix(diri.(string), pastikanTeks(a[0], "akhir_dengan"))
	}},
	"temukan": {1, 1, func(m *Mesin, diri any, a []any) any {
		return cariTeks(diri.(string), pastikanTeks(a[0], "temukan"))
	}},
}

// ambilMetode: metode daftar/kamus/teks yang terikat pada obj. Bila tidak ada, kembalikan semua nama
// metode yang tersedia (untuk saran "Maksud Anda ...?").
func ambilMetode(obj any, nama string) (*FungsiBawaan, []string) {
	var tabel map[string]metode
	var terikat any
	diri := obj
	switch o := obj.(type) {
	case *Daftar:
		tabel, terikat = metodeDaftar, o
	case *Kamus:
		tabel, terikat = metodeKamus, o
	default:
		tabel = metodeTeks
		diri, _ = teksDari(obj)
	}
	md, ada := tabel[nama]
	if !ada {
		return nil, kunciUrut(tabel)
	}
	return &FungsiBawaan{Nama: nama, min: md.min, max: md.max, terikat: terikat,
		fn: func(m *Mesin, args []any) any { return md.fn(m, diri, args) }}, nil
}
