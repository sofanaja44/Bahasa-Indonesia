package mesin

import (
	"errors"
	"io/fs"
	"math"
	"math/big"
	"os"
	"path"
	"runtime"
	"strconv"
	"strings"
	"syscall"
	"unicode/utf8"
)

// Pustaka standar: modul yang dimuat dengan 'impor' (src/pustaka.py).

type pasanganIsi struct {
	nama  string
	nilai any
}

func modulBaru(nama string, isi []pasanganIsi) *Modul {
	m := &Modul{Nama: nama, Isi: map[string]any{}}
	for _, p := range isi {
		m.Isi[p.nama] = p.nilai
		m.Urutan = append(m.Urutan, p.nama)
	}
	return m
}

var urutanModul = []string{"matematika", "acak", "waktu", "berkas"}

func (m *Mesin) muatModul(nama string, ins *instruksi) *Modul {
	switch nama {
	case "matematika":
		return modulMatematika()
	case "acak":
		return modulAcak()
	case "waktu":
		return modulWaktu()
	case "berkas":
		return modulBerkas()
	}
	panic(galatDi(KNama, "Modul '"+nama+"' tidak ada."+saranNama(nama, urutanModul)+
		" Modul yang tersedia: "+strings.Join(urutanModul, ", "), ins))
}

func isiModul(modul *Modul, nama string, ins *instruksi) any {
	if v, ada := modul.Isi[nama]; ada {
		return v
	}
	panic(galatDi(KNama, "Modul '"+modul.Nama+"' tidak memiliki '"+nama+"'."+saranNama(nama, modul.Urutan), ins))
}

// impor sama dengan _eval_impor(): impor matematika / impor matematika sebagai m /
// impor matematika.akar sebagai akar.
func (m *Mesin) impor(f *bingkai, jalur, alias string, ins *instruksi) {
	bagian := strings.Split(jalur, ".")
	var nilai any = m.muatModul(bagian[0], ins)
	for i := 1; i < len(bagian); i++ {
		modul, ok := nilai.(*Modul)
		if !ok {
			panic(galatDi(KNama, "'"+bagian[i-1]+"' bukan modul, jadi tidak punya '"+bagian[i]+"'", ins))
		}
		nilai = isiModul(modul, bagian[i], ins)
	}
	nama := bagian[0]
	if alias != "" {
		nama = alias
	} else if len(bagian) > 1 {
		nama = bagian[len(bagian)-1]
	}
	m.definisikan(f, m.simbolUntuk(nama), nilai, false)
}

// ---- matematika ----

// rapikan sama dengan _rapikan(): round(x, 12) + 0.0.
func rapikan(x float64) float64 {
	if math.IsNaN(x) || math.IsInf(x, 0) {
		return x
	}
	hasil, _ := strconv.ParseFloat(strconv.FormatFloat(x, 'f', 12, 64), 64)
	return hasil + 0.0
}

const derajatKeRadian = float64(math.Pi) / 180 // sama dengan math.radians(1)

func radian(x any) float64 {
	f, _ := keFloat(x)
	return f * derajatKeRadian
}

func lantaiAtap(x any, atas bool) any {
	f, ok := x.(float64)
	if !ok {
		return x // bilangan bulat
	}
	if atas {
		return floatKeBulatPython(math.Ceil(f))
	}
	return floatKeBulatPython(math.Floor(f))
}

// logPython sama dengan math.log(x) untuk x > 0, termasuk bilangan bulat yang sangat besar.
func logPython(x any) float64 {
	if b, ok := x.(*big.Int); ok {
		if f, _ := new(big.Float).SetInt(b).Float64(); !math.IsInf(f, 0) {
			return lnTepat(f)
		}
		mant := new(big.Float)
		e := new(big.Float).SetInt(b).MantExp(mant)
		m, _ := mant.Float64()
		return lnTepat(m) + lnTepat(2.0)*float64(e)
	}
	f, _ := keFloat(x)
	if math.IsInf(f, 1) || math.IsNaN(f) {
		return f
	}
	return lnTepat(f)
}

func modulMatematika() *Modul {
	bawah := bawaan("bulatkan_bawah", 1, 1, func(m *Mesin, a []any) any {
		return lantaiAtap(pastikanAngka(a[0], "bulatkan_bawah"), false)
	})
	atas := bawaan("bulatkan_atas", 1, 1, func(m *Mesin, a []any) any {
		return lantaiAtap(pastikanAngka(a[0], "bulatkan_atas"), true)
	})
	sudut := func(nama string, fn func(float64) float64) *FungsiBawaan {
		return bawaan(nama, 1, 1, func(m *Mesin, a []any) any {
			r := radian(pastikanAngka(a[0], nama))
			if math.IsInf(r, 0) {
				panic(galatPython{"ValueError"}) // math domain error
			}
			return rapikan(fn(r))
		})
	}
	return modulBaru("matematika", []pasanganIsi{
		{"pi", math.Pi},
		{"e", math.E},
		{"akar", bawaan("akar", 1, 1, func(m *Mesin, a []any) any {
			x := pastikanAngka(a[0], "akar")
			if bandingAngka(x, 0) == -1 {
				panic(galatNilai("Tidak bisa menghitung akar dari bilangan negatif"))
			}
			f, _ := keFloat(x)
			return math.Sqrt(f)
		})},
		{"pangkat", bawaan("pangkat", 2, 2, func(m *Mesin, a []any) any {
			x := pastikanAngka(a[0], "pangkat")
			n := pastikanAngka(a[1], "pangkat")
			defer func() {
				if r := recover(); r != nil {
					if g, ok := r.(galatPython); ok && g.jenis == "complex" {
						panic(galatNilai("Pangkat pecahan dari bilangan negatif tidak bisa dihitung"))
					}
					panic(r)
				}
			}()
			return pangkat(x, n)
		})},
		{"mutlak", bawaan("mutlak", 1, 1, func(m *Mesin, a []any) any { return mutlak(pastikanAngka(a[0], "mutlak")) })},
		{"bulatkan", bawaan("bulatkan", 1, 2, func(m *Mesin, a []any) any {
			x := pastikanAngka(a[0], "bulatkan")
			digit := pastikanBulat(argumen(a, 1, 0), "bulatkan")
			return bulatkan(x, digit)
		})},
		{"bulatkan_bawah", bawah},
		{"bulatkan_atas", atas},
		{"lantai", bawah},
		{"langit", atas},
		{"sinus", sudut("sinus", math.Sin)},
		{"kosinus", sudut("kosinus", math.Cos)},
		{"tangen", bawaan("tangen", 1, 1, func(m *Mesin, a []any) any {
			x := pastikanAngka(a[0], "tangen")
			r := radian(x)
			if math.IsInf(r, 0) {
				panic(galatPython{"ValueError"})
			}
			if math.Abs(math.Cos(r)) < 1e-12 {
				panic(galatNilai("Tangen " + keTeks(x) + " derajat tidak terdefinisi"))
			}
			return rapikan(math.Tan(r))
		})},
		{"logaritma", bawaan("logaritma", 1, 2, func(m *Mesin, a []any) any {
			x := pastikanAngka(a[0], "logaritma")
			basis := pastikanAngka(argumen(a, 1, 10), "logaritma")
			if c := bandingAngka(x, 0); c == -1 || c == 0 {
				panic(galatNilai("Logaritma hanya untuk bilangan lebih dari 0"))
			}
			if c := bandingAngka(basis, 0); c == -1 || c == 0 || samaDengan(basis, 1) {
				panic(galatNilai("Basis logaritma harus lebih dari 0 dan bukan 1"))
			}
			return rapikan(logPython(x) / logPython(basis))
		})},
		{"ln", bawaan("ln", 1, 1, func(m *Mesin, a []any) any {
			x := pastikanAngka(a[0], "ln")
			if c := bandingAngka(x, 0); c == -1 || c == 0 {
				panic(galatNilai("Logaritma hanya untuk bilangan lebih dari 0"))
			}
			return logPython(x)
		})},
		{"faktorial", bawaan("faktorial", 1, 1, func(m *Mesin, a []any) any {
			n := pastikanBulat(a[0], "faktorial")
			if bandingAngka(n, 0) == -1 {
				panic(galatNilai("Faktorial hanya untuk bilangan 0 atau lebih"))
			}
			k, ok := bulatKeInt(n)
			if !ok {
				panic(galatPython{"OverflowError"})
			}
			if k > 1_000_000 {
				panic(galatPython{"MemoryError"})
			}
			return normalBulat(new(big.Int).MulRange(1, int64(k)))
		})},
		{"fpb", bawaan("fpb", 0, -1, fpbKpk("fpb", false))},
		{"kpk", bawaan("kpk", 0, -1, fpbKpk("kpk", true))},
	})
}

// fpbKpk: FPB (math.gcd) atau KPK (math.lcm) dari dua bilangan atau lebih.
func fpbKpk(nama string, kpk bool) func(m *Mesin, a []any) any {
	return func(m *Mesin, a []any) any {
		if len(a) < 2 {
			panic(galatNilai(nama + " membutuhkan paling sedikit dua bilangan"))
		}
		for _, x := range a {
			pastikanBulat(x, nama)
		}
		hasil := new(big.Int).Abs(keBig(a[0]))
		for _, x := range a[1:] {
			y := new(big.Int).Abs(keBig(x))
			if !kpk {
				hasil.GCD(nil, nil, hasil, y)
				continue
			}
			if hasil.Sign() == 0 || y.Sign() == 0 {
				hasil.SetInt64(0)
				continue
			}
			g := new(big.Int).GCD(nil, nil, hasil, y)
			hasil.Mul(hasil.Div(hasil, g), y)
		}
		return normalBulat(hasil)
	}
}

// Batas konteks decimal Python (bawaan): presisi 28 digit, Emax 999999, Etiny -1000026.
const (
	presisiDesimal = 28
	emaxDesimal    = 999999
	etinyDesimal   = -1000026
)

// bulatkan sama dengan _bulatkan(): Decimal(str(x)).quantize(10**-digit, ROUND_HALF_UP).
func bulatkan(x any, digit any) any {
	gagal := func() any { panic(galatPython{"InvalidOperation"}) }
	d, ok := bulatKeInt(digit)
	if !ok || d > 2000054 || d < -2000054 {
		return gagal()
	}
	tujuan := -d // eksponen hasil
	if tujuan > emaxDesimal {
		return gagal() // Decimal(1).scaleb(-digit) melampaui Emax
	}
	if tujuan < etinyDesimal {
		tujuan = etinyDesimal
	}
	// Uraikan str(x) menjadi tanda, koefisien, dan eksponen.
	var teks string
	if f, ok := x.(float64); ok {
		switch {
		case math.IsInf(f, 0):
			return gagal()
		case math.IsNaN(f):
			if d <= 0 {
				panic(galatPython{"ValueError"}) // int(Decimal('NaN'))
			}
			return math.NaN()
		}
		teks = reprFloat(f)
	} else {
		teks = keBig(x).String()
	}
	negatif := strings.HasPrefix(teks, "-")
	teks = strings.TrimPrefix(teks, "-")
	eksponen := 0
	if i := strings.IndexByte(teks, 'e'); i >= 0 {
		eksponen, _ = strconv.Atoi(teks[i+1:])
		teks = teks[:i]
	}
	if i := strings.IndexByte(teks, '.'); i >= 0 {
		eksponen -= len(teks) - i - 1
		teks = teks[:i] + teks[i+1:]
	}
	koef, _ := new(big.Int).SetString(teks, 10)
	if koef.Sign() != 0 {
		digitKoef := len(koef.String())
		if digitKoef+eksponen-tujuan > presisiDesimal {
			return gagal()
		}
		if eksponen >= tujuan {
			koef.Mul(koef, new(big.Int).Exp(big.NewInt(10), big.NewInt(int64(eksponen-tujuan)), nil))
		} else {
			pembagi := new(big.Int).Exp(big.NewInt(10), big.NewInt(int64(tujuan-eksponen)), nil)
			sisa := new(big.Int)
			koef.QuoRem(koef, pembagi, sisa)
			if sisa.Lsh(sisa, 1).Cmp(pembagi) >= 0 { // ROUND_HALF_UP
				koef.Add(koef, big.NewInt(1))
			}
		}
		n := len(koef.String())
		if koef.Sign() != 0 && (n > presisiDesimal || tujuan+n-1 > emaxDesimal) {
			return gagal()
		}
	}
	if d <= 0 {
		hasil := koef.Mul(koef, new(big.Int).Exp(big.NewInt(10), big.NewInt(int64(tujuan)), nil))
		if negatif {
			hasil.Neg(hasil)
		}
		return normalBulat(hasil)
	}
	f, _ := strconv.ParseFloat(koef.String()+"e"+strconv.Itoa(tujuan), 64)
	if negatif {
		f = -f
	}
	return f
}

// ---- acak ----

// bilanganAcak sama dengan bilangan_acak(): bilangan bulat acak dari minimum sampai maksimum.
func (m *Mesin) bilanganAcak(minimum, maksimum any) any {
	pastikanBulat(minimum, "bilangan acak")
	pastikanBulat(maksimum, "bilangan acak")
	if bandingAngka(minimum, maksimum) == 1 {
		panic(galatNilai("Batas bawah (" + reprNilai(minimum) + ") tidak boleh lebih besar dari batas atas (" +
			reprNilai(maksimum) + ")"))
	}
	return m.acak.randint(minimum, maksimum)
}

func modulAcak() *Modul {
	return modulBaru("acak", []pasanganIsi{
		{"bilangan", bawaan("bilangan", 2, 2, func(m *Mesin, a []any) any { return m.bilanganAcak(a[0], a[1]) })},
		{"angka", bawaan("angka", 0, 0, func(m *Mesin, a []any) any { return m.acak.random() })},
		{"pilih", bawaan("pilih", 1, 1, func(m *Mesin, a []any) any {
			var isi []any
			if d, ok := a[0].(*Daftar); ok {
				isi = d.Elemen
			} else if s, ok := teksDari(a[0]); ok {
				isi = hurufHuruf(s)
			} else {
				panic(galatTipe("'pilih' membutuhkan daftar atau teks, bukan '" + keTeks(a[0]) + "'"))
			}
			if len(isi) == 0 {
				panic(galatNilai("Tidak bisa memilih dari daftar yang kosong"))
			}
			return isi[m.acak.bawah(len(isi)).(int)]
		})},
		{"kocok", bawaan("kocok", 1, 1, func(m *Mesin, a []any) any {
			d, ok := a[0].(*Daftar)
			if !ok {
				panic(galatTipe("'kocok' membutuhkan daftar, bukan '" + keTeks(a[0]) + "'"))
			}
			m.acak.kocok(d.Elemen)
			return nil
		})},
		{"atur_benih", bawaan("atur_benih", 1, 1, func(m *Mesin, a []any) any {
			m.acak.aturBenih(a[0])
			return nil
		})},
	})
}

// ---- waktu ----

func modulWaktu() *Modul {
	baca := func(nama, bagian string) *FungsiBawaan {
		return bawaan(nama, 0, 0, func(m *Mesin, a []any) any { return m.bacaWaktu(bagian) })
	}
	return modulBaru("waktu", []pasanganIsi{
		{"jam", baca("jam", "jam")},
		{"menit", baca("menit", "menit")},
		{"detik", baca("detik", "detik")},
		{"sekarang", baca("sekarang", "waktu")},
		{"hari", baca("hari", "hari")},
		{"tanggal_lengkap", bawaan("tanggal_lengkap", 0, 0, func(m *Mesin, a []any) any {
			return m.bacaWaktu("hari").(string) + ", " + m.bacaWaktu("tanggal").(string)
		})},
		{"nama_bulan", baca("nama_bulan", "bulan")},
		{"tahun", baca("tahun", "tahun")},
		{"tunggu", bawaan("tunggu", 1, 1, func(m *Mesin, a []any) any { m.tungguDetik(a[0], 1); return nil })},
	})
}

// ---- berkas ----

// SistemBerkas adalah tempat modul 'berkas' membaca dan menulis. Bawaannya berkas di komputer;
// editor di browser memakai BerkasMemori.
type SistemBerkas interface {
	Baca(nama string) ([]byte, error)
	Tulis(nama string, isi []byte, tambah bool) error
	AdaBerkas(nama string) bool
	Hapus(nama string) error
}

var (
	ErrBerkasTidakAda = errors.New("berkas tidak ditemukan")
	ErrBerkasFolder   = errors.New("berupa folder")
	ErrBerkasIzin     = errors.New("tidak punya izin")
)

type berkasOS struct{}

func petakanGalatOS(err error) error {
	switch {
	case err == nil:
		return nil
	case errors.Is(err, fs.ErrNotExist):
		return ErrBerkasTidakAda
	case errors.Is(err, fs.ErrPermission):
		return ErrBerkasIzin
	case errors.Is(err, syscall.EISDIR):
		return ErrBerkasFolder
	}
	return err
}

func adalahFolder(nama string) bool {
	info, err := os.Stat(nama)
	return err == nil && info.IsDir()
}

func (berkasOS) Baca(nama string) ([]byte, error) {
	if adalahFolder(nama) {
		return nil, ErrBerkasFolder
	}
	b, err := os.ReadFile(nama)
	return b, petakanGalatOS(err)
}

func (berkasOS) Tulis(nama string, isi []byte, tambah bool) error {
	if adalahFolder(nama) {
		return ErrBerkasFolder
	}
	mode := os.O_WRONLY | os.O_CREATE | os.O_TRUNC
	if tambah {
		mode = os.O_WRONLY | os.O_CREATE | os.O_APPEND
	}
	f, err := os.OpenFile(nama, mode, 0o666)
	if err != nil {
		return petakanGalatOS(err)
	}
	_, err = f.Write(isi)
	if errTutup := f.Close(); err == nil {
		err = errTutup
	}
	return petakanGalatOS(err)
}

func (berkasOS) AdaBerkas(nama string) bool {
	info, err := os.Stat(nama)
	return err == nil && info.Mode().IsRegular()
}

func (berkasOS) Hapus(nama string) error {
	info, err := os.Lstat(nama)
	if err != nil {
		return petakanGalatOS(err)
	}
	if info.IsDir() {
		return ErrBerkasFolder // os.remove() Python tidak menghapus folder
	}
	return petakanGalatOS(os.Remove(nama))
}

// BerkasMemori menyimpan berkas di memori, seperti sistem berkas Pyodide di editor browser.
type BerkasMemori struct{ isi map[string][]byte }

func NewBerkasMemori() *BerkasMemori { return &BerkasMemori{isi: map[string][]byte{}} }

func (b *BerkasMemori) jalur(nama string) (string, error) {
	if nama == "" {
		return "", ErrBerkasTidakAda
	}
	j := path.Clean(nama)
	if j == "." || j == "/" || j == ".." || strings.HasSuffix(nama, "/") {
		return "", ErrBerkasFolder
	}
	return j, nil
}

func (b *BerkasMemori) Baca(nama string) ([]byte, error) {
	j, err := b.jalur(nama)
	if err != nil {
		return nil, err
	}
	isi, ada := b.isi[j]
	if !ada {
		return nil, ErrBerkasTidakAda
	}
	return append([]byte(nil), isi...), nil
}

func (b *BerkasMemori) Tulis(nama string, isi []byte, tambah bool) error {
	j, err := b.jalur(nama)
	if err != nil {
		return err
	}
	if tambah {
		b.isi[j] = append(b.isi[j], isi...)
	} else {
		b.isi[j] = append([]byte(nil), isi...)
	}
	return nil
}

func (b *BerkasMemori) AdaBerkas(nama string) bool {
	j, err := b.jalur(nama)
	if err != nil {
		return false
	}
	_, ada := b.isi[j]
	return ada
}

func (b *BerkasMemori) Hapus(nama string) error {
	j, err := b.jalur(nama)
	if err != nil {
		return err
	}
	if _, ada := b.isi[j]; !ada {
		return ErrBerkasTidakAda
	}
	delete(b.isi, j)
	return nil
}

func (m *Mesin) sistemBerkas() SistemBerkas {
	if m.io.Berkas != nil {
		return m.io.Berkas
	}
	return berkasOS{}
}

func namaBerkas(x any) string {
	if s, ok := teksDari(x); ok {
		return s
	}
	panic(galatTipe("Nama berkas harus berupa teks, bukan '" + keTeks(x) + "'"))
}

// galatBerkas menerjemahkan kesalahan sistem berkas seperti _buka() dan _hapus_berkas().
func galatBerkas(err error, nama string, hapus bool) {
	switch {
	case err == ErrBerkasTidakAda:
		panic(kesalahanTanpaLokasi(KBerkas, "Berkas '"+nama+"' tidak ditemukan"))
	case hapus && (err == ErrBerkasFolder || err == ErrBerkasIzin):
		panic(kesalahanTanpaLokasi(KBerkas, "Berkas '"+nama+"' tidak bisa dihapus"))
	case err == ErrBerkasFolder:
		panic(kesalahanTanpaLokasi(KBerkas, "'"+nama+"' adalah folder, bukan berkas"))
	case err == ErrBerkasIzin:
		panic(kesalahanTanpaLokasi(KBerkas, "Tidak punya izin untuk membuka berkas '"+nama+"'"))
	}
	panic(galatPython{"OSError"})
}

func (m *Mesin) bacaBerkas(x any) string {
	nama := namaBerkas(x)
	b, err := m.sistemBerkas().Baca(nama)
	if err != nil {
		galatBerkas(err, nama, false)
	}
	if !utf8.Valid(b) {
		panic(kesalahanTanpaLokasi(KBerkas, "Berkas '"+nama+"' bukan berkas teks"))
	}
	// Mode teks Python: \r\n dan \r dibaca sebagai \n.
	teks := strings.ReplaceAll(string(b), "\r\n", "\n")
	return strings.ReplaceAll(teks, "\r", "\n")
}

func (m *Mesin) tulisBerkas(x, isi any, tambah bool) {
	nama := namaBerkas(x)
	teks := keTeks(isi)
	sb := m.sistemBerkas()
	if _, ok := sb.(berkasOS); ok && runtime.GOOS == "windows" {
		teks = strings.ReplaceAll(teks, "\n", "\r\n")
	}
	if err := sb.Tulis(nama, []byte(teks), tambah); err != nil {
		galatBerkas(err, nama, false)
	}
}

// belahBaris sama dengan str.splitlines().
func belahBaris(s string) []string {
	var hasil []string
	mulai := 0
	for i := 0; i < len(s); {
		r, n := utf8.DecodeRuneInString(s[i:])
		switch r {
		case '\n', '\r', '\v', '\f', 0x1c, 0x1d, 0x1e, 0x85, 0x2028, 0x2029:
			hasil = append(hasil, s[mulai:i])
			if r == '\r' && i+1 < len(s) && s[i+1] == '\n' {
				n = 2
			}
			i += n
			mulai = i
			continue
		}
		i += n
	}
	if mulai < len(s) {
		hasil = append(hasil, s[mulai:])
	}
	return hasil
}

func modulBerkas() *Modul {
	return modulBaru("berkas", []pasanganIsi{
		{"baca", bawaan("baca", 1, 1, func(m *Mesin, a []any) any { return m.bacaBerkas(a[0]) })},
		{"baca_baris", bawaan("baca_baris", 1, 1, func(m *Mesin, a []any) any {
			return teksDaftar(belahBaris(m.bacaBerkas(a[0])))
		})},
		{"tulis", bawaan("tulis", 2, 2, func(m *Mesin, a []any) any { m.tulisBerkas(a[0], a[1], false); return nil })},
		{"tambahkan", bawaan("tambahkan", 2, 2, func(m *Mesin, a []any) any { m.tulisBerkas(a[0], a[1], true); return nil })},
		{"ada", bawaan("ada", 1, 1, func(m *Mesin, a []any) any {
			s, ok := teksDari(a[0])
			return ok && m.sistemBerkas().AdaBerkas(s)
		})},
		{"hapus", bawaan("hapus", 1, 1, func(m *Mesin, a []any) any {
			nama := namaBerkas(a[0])
			if err := m.sistemBerkas().Hapus(nama); err != nil {
				galatBerkas(err, nama, true)
			}
			return nil
		})},
	})
}
