package mesin

import "strings"

// TipeToken sama dengan TokenType di src/token_types.py.
type TipeToken int

const (
	ANGKA TipeToken = iota
	DESIMAL
	TEKS
	TEKS_FORMAT
	IDENTIFIER
	WAKTU_SEKARANG
	ANGKA_ACAK
	BUAT
	TETAP
	ADALAH
	BILANGAN
	DESIMAL_TIPE
	TEKS_TIPE
	LOGIKA_TIPE
	BENAR
	SALAH
	KOSONG
	JIKA
	ATAU_JIKA
	SELAINNYA
	PILIH
	KETIKA
	BAWAAN
	MAKA
	SELAMA
	UNTUK
	UNTUK_SETIAP
	DARI
	SAMPAI
	LANGKAH
	DALAM
	ULANGI
	BERHENTI
	LEWATI
	LAKUKAN
	FUNGSI
	KEMBALIKAN
	KELAS
	MEWARISI
	DIRI
	SUPER
	PRIBADI
	STATIS
	IMPOR
	SEBAGAI
	COBA
	TANGKAP
	AKHIRNYA
	LEMPAR
	TAMPILKAN
	MASUKAN
	MASUKAN_ANGKA
	MASUKAN_DESIMAL
	DAN
	ATAU
	BUKAN
	ADA
	TIDAK_ADA
	SAMA_DENGAN_OP
	TIDAK_SAMA_OP
	LEBIH_DARI
	KURANG_DARI
	TIDAK_KURANG_DARI
	TIDAK_LEBIH_DARI
	SISA_BAGI
	HABIS_DIBAGI
	TIDAK_HABIS_DIBAGI
	PANGKAT_KK
	DITAMBAH
	DIKURANG
	DIKALI
	DIBAGI
	TAMBAH
	KURANG
	KALI
	BAGI
	MODULO
	PANGKAT
	SAMA_DENGAN
	TAMBAH_SAMA
	KURANG_SAMA
	KALI_SAMA
	BAGI_SAMA
	MODULO_SAMA
	SAMA
	TIDAK_SAMA
	LEBIH_BESAR
	LEBIH_KECIL
	LEBIH_BESAR_SAMA
	LEBIH_KECIL_SAMA
	TITIK_DUA
	KOMA
	TITIK
	KURUNG_BUKA
	KURUNG_TUTUP
	SIKU_BUKA
	SIKU_TUTUP
	KURAWAL_BUKA
	KURAWAL_TUTUP
	INDENT
	DEDENT
	BARIS_BARU
	EOF
)

type pasanganKata struct {
	kata string
	tipe TipeToken
}

// urutanKataKunci berurutan seperti KATA_KUNCI di Python (urutan ini menentukan jelaskanTipe).
var urutanKataKunci = []pasanganKata{
	{"buat", BUAT}, {"tetap", TETAP}, {"adalah", ADALAH},
	{"bilangan", BILANGAN}, {"teks", TEKS_TIPE}, {"logika", LOGIKA_TIPE},
	{"benar", BENAR}, {"salah", SALAH}, {"kosong", KOSONG},
	{"jika", JIKA}, {"kalau", JIKA}, {"selainnya", SELAINNYA}, {"pilih", PILIH},
	{"ketika", KETIKA}, {"bawaan", BAWAAN}, {"maka", MAKA},
	{"selama", SELAMA}, {"untuk", UNTUK}, {"dari", DARI}, {"sampai", SAMPAI},
	{"langkah", LANGKAH}, {"dalam", DALAM}, {"ulangi", ULANGI}, {"berhenti", BERHENTI},
	{"lewati", LEWATI}, {"lakukan", LAKUKAN},
	{"fungsi", FUNGSI}, {"kembalikan", KEMBALIKAN},
	{"kelas", KELAS}, {"mewarisi", MEWARISI}, {"diri", DIRI}, {"super", SUPER},
	{"pribadi", PRIBADI}, {"statis", STATIS},
	{"impor", IMPOR}, {"sebagai", SEBAGAI},
	{"coba", COBA}, {"tangkap", TANGKAP}, {"akhirnya", AKHIRNYA}, {"lempar", LEMPAR},
	{"tampilkan", TAMPILKAN}, {"cetak", TAMPILKAN}, {"tulis", TAMPILKAN},
	{"masukan", MASUKAN}, {"masukan_angka", MASUKAN_ANGKA}, {"masukan_desimal", MASUKAN_DESIMAL},
	{"dan", DAN}, {"atau", ATAU}, {"bukan", BUKAN}, {"tidak", BUKAN},
	{"ada", ADA},
	{"ditambah", DITAMBAH}, {"dikurang", DIKURANG}, {"dikurangi", DIKURANG},
	{"dikali", DIKALI}, {"dikalikan", DIKALI}, {"dibagi", DIBAGI},
	{"pangkat", PANGKAT_KK}, {"dipangkatkan", PANGKAT_KK},
	{"desimal", DESIMAL_TIPE},
}

type pasanganFrasa struct {
	kata []string
	tipe TipeToken
}

func frasa(teks string, tipe TipeToken) pasanganFrasa {
	return pasanganFrasa{strings.Fields(teks), tipe}
}

// urutanFrasa berurutan seperti FRASA_KATA_KUNCI (termasuk varian "daripada").
var urutanFrasa = func() []pasanganFrasa {
	dasar := []pasanganFrasa{
		frasa("atau jika", ATAU_JIKA), frasa("atau kalau", ATAU_JIKA),
		frasa("untuk setiap", UNTUK_SETIAP), frasa("di dalam", DALAM),
		frasa("tidak ada", TIDAK_ADA),
		frasa("jam sekarang", WAKTU_SEKARANG), frasa("menit sekarang", WAKTU_SEKARANG),
		frasa("detik sekarang", WAKTU_SEKARANG), frasa("waktu sekarang", WAKTU_SEKARANG),
		frasa("hari ini", WAKTU_SEKARANG), frasa("tanggal hari ini", WAKTU_SEKARANG),
		frasa("bulan ini", WAKTU_SEKARANG), frasa("tahun ini", WAKTU_SEKARANG),
		frasa("angka acak", ANGKA_ACAK),
		frasa("sisa bagi", SISA_BAGI), frasa("habis dibagi", HABIS_DIBAGI),
		frasa("tidak habis dibagi", TIDAK_HABIS_DIBAGI),
		frasa("sama dengan", SAMA_DENGAN_OP), frasa("tidak sama", TIDAK_SAMA_OP),
		frasa("tidak sama dengan", TIDAK_SAMA_OP),
		frasa("paling sedikit", TIDAK_KURANG_DARI), frasa("paling banyak", TIDAK_LEBIH_DARI),
		frasa("lebih besar atau sama dengan", TIDAK_KURANG_DARI),
		frasa("lebih kecil atau sama dengan", TIDAK_LEBIH_DARI),
		frasa("lebih besar sama dengan", TIDAK_KURANG_DARI),
		frasa("lebih kecil sama dengan", TIDAK_LEBIH_DARI),
	}
	denganDari := []pasanganFrasa{
		frasa("lebih dari", LEBIH_DARI), frasa("lebih besar dari", LEBIH_DARI),
		frasa("kurang dari", KURANG_DARI), frasa("lebih kecil dari", KURANG_DARI),
		frasa("tidak kurang dari", TIDAK_KURANG_DARI), frasa("tidak lebih dari", TIDAK_LEBIH_DARI),
		frasa("lebih dari atau sama dengan", TIDAK_KURANG_DARI),
		frasa("lebih besar dari atau sama dengan", TIDAK_KURANG_DARI),
		frasa("kurang dari atau sama dengan", TIDAK_LEBIH_DARI),
		frasa("lebih kecil dari atau sama dengan", TIDAK_LEBIH_DARI),
	}
	for _, f := range denganDari {
		dasar = append(dasar, f)
		varian := make([]string, len(f.kata))
		for i, k := range f.kata {
			if k == "dari" {
				k = "daripada"
			}
			varian[i] = k
		}
		dasar = append(dasar, pasanganFrasa{varian, f.tipe})
	}
	return dasar
}()

// Peta-peta ini dihitung saat deklarasi (bukan di init()) agar variabel lain yang memakainya,
// mis. kataPerintah di parser.go, diinisialisasi sesudahnya.
var kataKunci = func() map[string]TipeToken {
	m := map[string]TipeToken{}
	for _, p := range urutanKataKunci {
		m[p.kata] = p.tipe
	}
	return m
}()

var tipeKataKunci = func() map[TipeToken]bool {
	m := map[TipeToken]bool{}
	for _, p := range urutanKataKunci {
		m[p.tipe] = true
	}
	return m
}()

// frasaKataKunci: kata-kata frasa digabung dengan spasi tunggal.
var frasaKataKunci = func() map[string]TipeToken {
	m := map[string]TipeToken{}
	for _, f := range urutanFrasa {
		m[strings.Join(f.kata, " ")] = f.tipe
	}
	return m
}()

var awalanFrasa = func() map[string]bool {
	m := map[string]bool{}
	for _, f := range urutanFrasa {
		m[f.kata[0]] = true
	}
	return m
}()

var panjangFrasaMax = func() int {
	n := 0
	for _, f := range urutanFrasa {
		n = max(n, len(f.kata))
	}
	return n
}()

// operator2 & operator1 sama dengan OPERATORS (dua karakter dicoba lebih dulu).
var operator2 = map[string]TipeToken{
	"**": PANGKAT, "+=": TAMBAH_SAMA, "-=": KURANG_SAMA, "*=": KALI_SAMA, "/=": BAGI_SAMA,
	"%=": MODULO_SAMA, "==": SAMA, "!=": TIDAK_SAMA, ">=": LEBIH_BESAR_SAMA, "<=": LEBIH_KECIL_SAMA,
}

var operator1 = map[rune]TipeToken{
	'>': LEBIH_BESAR, '<': LEBIH_KECIL, '+': TAMBAH, '-': KURANG, '*': KALI, '/': BAGI,
	'%': MODULO, '=': SAMA_DENGAN,
}

var tandaBaca = map[rune]TipeToken{
	':': TITIK_DUA, ',': KOMA, '.': TITIK, '(': KURUNG_BUKA, ')': KURUNG_TUTUP,
	'[': SIKU_BUKA, ']': SIKU_TUTUP, '{': KURAWAL_BUKA, '}': KURAWAL_TUTUP,
}

var deskripsiKhusus = map[TipeToken]string{
	IDENTIFIER: "nama (variabel/fungsi)", ANGKA: "angka", DESIMAL: "angka desimal",
	TEKS: "teks", TEKS_FORMAT: "teks format", INDENT: "blok baru yang menjorok ke dalam",
	DEDENT: "akhir blok", BARIS_BARU: "akhir baris", EOF: "akhir program",
}

var simbolUntukTipe = func() map[TipeToken]string {
	m := map[TipeToken]string{}
	for s, t := range operator2 {
		m[t] = s
	}
	for r, t := range operator1 {
		m[t] = string(r)
	}
	for r, t := range tandaBaca {
		m[t] = string(r)
	}
	return m
}()

var kataUntukTipe = func() map[TipeToken]string {
	m := map[TipeToken]string{}
	for _, p := range urutanKataKunci {
		if _, ada := m[p.tipe]; !ada {
			m[p.tipe] = p.kata
		}
	}
	for _, f := range urutanFrasa {
		if _, ada := m[f.tipe]; !ada {
			m[f.tipe] = strings.Join(f.kata, " ")
		}
	}
	return m
}()

// jelaskanTipe: nama tipe token dalam bahasa sehari-hari, mis. TITIK_DUA → "tanda ':'".
func jelaskanTipe(t TipeToken) string {
	if d, ada := deskripsiKhusus[t]; ada {
		return d
	}
	if s, ada := simbolUntukTipe[t]; ada {
		return "tanda '" + s + "'"
	}
	if k, ada := kataUntukTipe[t]; ada {
		return "kata '" + k + "'"
	}
	return "?"
}

// Token adalah satu potongan kode hasil lexer.
type Token struct {
	Tipe  TipeToken
	Nilai any // string, int, *big.Int, float64, atau nil
	Baris int
	Kolom int
}

// teksNilai: nilai token sebagai teks (untuk kata kunci, nama, dan operator).
func (t Token) teksNilai() string {
	if s, ok := t.Nilai.(string); ok {
		return s
	}
	return ""
}
