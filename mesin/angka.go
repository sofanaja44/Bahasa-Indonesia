package mesin

import (
	"math"
	"math/big"
	"math/bits"
	"strconv"
	"strings"
	"unicode"
)

// Bilangan bulat disimpan sebagai int bila muat di 64 bit, selain itu *big.Int (seperti int Python).

// normalBulat mengubah *big.Int menjadi int bila muat.
func normalBulat(b *big.Int) any {
	if b.IsInt64() {
		return int(b.Int64())
	}
	return b
}

func keBig(v any) *big.Int {
	switch x := v.(type) {
	case int:
		return big.NewInt(int64(x))
	case bool:
		if x {
			return big.NewInt(1)
		}
		return big.NewInt(0)
	case *big.Int:
		return x
	}
	return nil
}

// adalahBulat: int, *big.Int, atau logika (bool adalah turunan int di Python).
func adalahBulat(v any) bool {
	switch v.(type) {
	case int, *big.Int, bool:
		return true
	}
	return false
}

// adalahAngka: bilangan bulat, desimal, atau logika.
func adalahAngkaNilai(v any) bool {
	switch v.(type) {
	case int, *big.Int, bool, float64:
		return true
	}
	return false
}

// adalahAngkaMurni: angka tetapi bukan logika (isinstance(x, (int, float)) and not bool).
func adalahAngkaMurni(v any) bool {
	switch v.(type) {
	case int, *big.Int, float64:
		return true
	}
	return false
}

func bulatKeInt(v any) (int, bool) {
	switch x := v.(type) {
	case int:
		return x, true
	case bool:
		if x {
			return 1, true
		}
		return 0, true
	}
	return 0, false
}

var errTerlaluBesar = kesalahanTanpaLokasi(KNilai, "Hasil perhitungan terlalu besar")

// keFloat mengubah angka menjadi float64 seperti float() Python (OverflowError bila terlalu besar).
func keFloat(v any) (float64, bool) {
	switch x := v.(type) {
	case float64:
		return x, true
	case int:
		return float64(x), true
	case bool:
		if x {
			return 1, true
		}
		return 0, true
	case *big.Int:
		f, _ := new(big.Float).SetInt(x).Float64()
		if math.IsInf(f, 0) {
			panic(galatPython{"OverflowError"})
		}
		return f, true
	}
	return 0, false
}

// galatPython menandai kesalahan yang di Python berupa exception bawaan (TypeError, ...);
// VM menerjemahkannya menjadi pesan berbahasa Indonesia sesuai tempat terjadinya.
type galatPython struct{ jenis string }

// ---- Tampilan ----

// reprFloat sama dengan repr(float) di Python.
func reprFloat(x float64) string {
	switch {
	case math.IsNaN(x):
		return "nan"
	case math.IsInf(x, 1):
		return "inf"
	case math.IsInf(x, -1):
		return "-inf"
	}
	tanda := ""
	if math.Signbit(x) {
		tanda = "-"
		x = -x
	}
	if x == 0 {
		return tanda + "0.0"
	}
	e := strconv.FormatFloat(x, 'e', -1, 64) // "d.ddde±XX"
	iE := strings.IndexByte(e, 'e')
	digit := strings.Replace(e[:iE], ".", "", 1)
	eksp, _ := strconv.Atoi(e[iE+1:])
	titik := eksp + 1 // posisi titik desimal relatif terhadap digit
	if titik <= -4 || titik > 16 {
		m := digit[:1]
		if len(digit) > 1 {
			m += "." + digit[1:]
		}
		s := "+"
		if eksp < 0 {
			s, eksp = "-", -eksp
		}
		es := strconv.Itoa(eksp)
		if len(es) < 2 {
			es = "0" + es
		}
		return tanda + m + "e" + s + es
	}
	switch {
	case titik <= 0:
		return tanda + "0." + strings.Repeat("0", -titik) + digit
	case titik >= len(digit):
		return tanda + digit + strings.Repeat("0", titik-len(digit)) + ".0"
	default:
		return tanda + digit[:titik] + "." + digit[titik:]
	}
}

// teksDesimal sama dengan _teks_desimal(): 5.0 tampil "5", 0.1 + 0.2 tampil "0.3".
func teksDesimal(x float64) string {
	if math.IsNaN(x) || math.IsInf(x, 0) {
		return reprFloat(x)
	}
	x, _ = strconv.ParseFloat(strconv.FormatFloat(x, 'g', 12, 64), 64)
	if x == math.Trunc(x) {
		if math.Abs(x) < 1e18 {
			return strconv.FormatInt(int64(x), 10)
		}
		b, _ := new(big.Float).SetFloat64(x).Int(nil)
		return b.String()
	}
	return reprFloat(x)
}

// reprNilai: str() Python untuk angka (dipakai di beberapa pesan kesalahan).
func reprNilai(v any) string {
	switch x := v.(type) {
	case int:
		return strconv.Itoa(x)
	case *big.Int:
		return x.String()
	case float64:
		return reprFloat(x)
	case bool:
		if x {
			return "True"
		}
		return "False"
	case nil:
		return "None"
	case string:
		return x
	}
	return keTeks(v)
}

// ---- Membaca angka dari teks (int() dan float() Python) ----

func adalahSpasiPython(r rune) bool {
	switch r {
	case ' ', '\t', '\n', '\v', '\f', '\r', 0x1c, 0x1d, 0x1e, 0x1f, 0x85, 0xa0, 0x1680,
		0x2028, 0x2029, 0x202f, 0x205f, 0x3000:
		return true
	}
	return r >= 0x2000 && r <= 0x200a
}

func potongSpasi(s string) string { return strings.TrimFunc(s, adalahSpasiPython) }

// digitDenganGarisBawah: "1_000" → "1000"; false bila garis bawah tidak di antara digit.
func digitDenganGarisBawah(s string) (string, bool) {
	if s == "" {
		return "", false
	}
	var b strings.Builder
	sebelumnyaDigit := false
	for _, r := range s {
		switch {
		case unicode.IsDigit(r):
			b.WriteRune('0' + nilaiDigit(r))
			sebelumnyaDigit = true
		case r == '_' && sebelumnyaDigit:
			sebelumnyaDigit = false
		default:
			return "", false
		}
	}
	if !sebelumnyaDigit {
		return "", false
	}
	return b.String(), true
}

// intDariTeks sama dengan int(teks) Python (basis 10).
func intDariTeks(teks string) (any, bool) {
	t := potongSpasi(teks)
	tanda := ""
	if strings.HasPrefix(t, "+") || strings.HasPrefix(t, "-") {
		if t[0] == '-' {
			tanda = "-"
		}
		t = t[1:]
	}
	digit, ok := digitDenganGarisBawah(t)
	if !ok {
		return nil, false
	}
	return bulatDariTeks(tanda + digit), true
}

// floatDariTeks sama dengan float(teks) Python.
func floatDariTeks(teks string) (float64, bool) {
	t := potongSpasi(teks)
	tanda := 1.0
	if strings.HasPrefix(t, "+") || strings.HasPrefix(t, "-") {
		if t[0] == '-' {
			tanda = -1
		}
		t = t[1:]
	}
	switch strings.ToLower(t) {
	case "inf", "infinity":
		return tanda * math.Inf(1), true
	case "nan":
		return math.NaN(), true
	}
	mantisa, eksponen := t, ""
	if i := strings.IndexAny(t, "eE"); i >= 0 {
		mantisa, eksponen = t[:i], t[i+1:]
	}
	bulat, pecahan := mantisa, ""
	adaTitik := false
	if i := strings.IndexByte(mantisa, '.'); i >= 0 {
		bulat, pecahan, adaTitik = mantisa[:i], mantisa[i+1:], true
	}
	if bulat == "" && pecahan == "" {
		return 0, false
	}
	var b strings.Builder
	if bulat != "" {
		d, ok := digitDenganGarisBawah(bulat)
		if !ok {
			return 0, false
		}
		b.WriteString(d)
	} else {
		b.WriteString("0")
	}
	if adaTitik {
		b.WriteString(".")
		if pecahan != "" {
			d, ok := digitDenganGarisBawah(pecahan)
			if !ok {
				return 0, false
			}
			b.WriteString(d)
		} else {
			b.WriteString("0")
		}
	}
	if eksponen != "" || strings.ContainsAny(t, "eE") {
		s := ""
		if strings.HasPrefix(eksponen, "+") || strings.HasPrefix(eksponen, "-") {
			s, eksponen = eksponen[:1], eksponen[1:]
		}
		d, ok := digitDenganGarisBawah(eksponen)
		if !ok {
			return 0, false
		}
		b.WriteString("e" + s + d)
	}
	f, err := strconv.ParseFloat(b.String(), 64)
	if err != nil && !strings.Contains(err.Error(), "range") {
		return 0, false
	}
	return tanda * f, true
}

// teksKeAngka sama dengan teks_ke_angka(): "12" → 12, "3,5" → 3.5, selain angka → nil.
func teksKeAngka(teks string) any {
	t := potongSpasi(teks)
	if strings.Contains(t, ",") && !strings.Contains(t, ".") {
		t = strings.ReplaceAll(t, ",", ".") // koma desimal ala Indonesia
	}
	if n, ok := intDariTeks(t); ok {
		return n
	}
	x, ok := floatDariTeks(t)
	if !ok || math.IsNaN(x) || math.IsInf(x, 0) {
		return nil
	}
	return x
}

// ---- Aritmetika ----

func tambahBulat(a, b any) any {
	x, ok1 := bulatKeInt(a)
	y, ok2 := bulatKeInt(b)
	if ok1 && ok2 {
		s := x + y
		if (s > x) == (y > 0) {
			return s
		}
	}
	return normalBulat(new(big.Int).Add(keBig(a), keBig(b)))
}

func kurangBulat(a, b any) any {
	x, ok1 := bulatKeInt(a)
	y, ok2 := bulatKeInt(b)
	if ok1 && ok2 {
		s := x - y
		if (s < x) == (y > 0) {
			return s
		}
	}
	return normalBulat(new(big.Int).Sub(keBig(a), keBig(b)))
}

func kaliBulat(a, b any) any {
	x, ok1 := bulatKeInt(a)
	y, ok2 := bulatKeInt(b)
	if ok1 && ok2 {
		if x == 0 || y == 0 {
			return 0
		}
		hi, lo := bits.Mul64(uint64(absInt(x)), uint64(absInt(y)))
		if hi == 0 && lo <= math.MaxInt64 && x != math.MinInt64 && y != math.MinInt64 {
			if (x < 0) != (y < 0) {
				return -int(lo)
			}
			return int(lo)
		}
	}
	return normalBulat(new(big.Int).Mul(keBig(a), keBig(b)))
}

func absInt(x int) int {
	if x < 0 {
		return -x
	}
	return x
}

// modBulat: modulo Python (tanda hasil mengikuti pembagi). b != 0.
func modBulat(a, b any) any {
	x, ok1 := bulatKeInt(a)
	y, ok2 := bulatKeInt(b)
	if ok1 && ok2 && !(x == math.MinInt64 && y == -1) {
		r := x % y
		if r != 0 && (r < 0) != (y < 0) {
			r += y
		}
		return r
	}
	bb := keBig(b)
	r := new(big.Int).Rem(keBig(a), bb)
	if r.Sign() != 0 && (r.Sign() < 0) != (bb.Sign() < 0) {
		r.Add(r, bb)
	}
	return normalBulat(r)
}

// modFloat: float % float Python. b != 0.
func modFloat(a, b float64) float64 {
	m := math.Mod(a, b)
	if m != 0 {
		if (b < 0) != (m < 0) {
			m += b
		}
	} else {
		m = math.Copysign(0, b)
	}
	return m
}

// bagiBenar: pembagian / Python (hasilnya selalu desimal). b != 0.
func bagiBenar(a, b any) float64 {
	if adalahBulat(a) && adalahBulat(b) {
		x, ok1 := bulatKeInt(a)
		y, ok2 := bulatKeInt(b)
		const batas = 1 << 53
		if ok1 && ok2 && absInt(x) <= batas && absInt(y) <= batas {
			return float64(x) / float64(y)
		}
		f, _ := new(big.Rat).SetFrac(keBig(a), keBig(b)).Float64()
		if math.IsInf(f, 0) {
			panic(galatPython{"OverflowError"})
		}
		return f
	}
	x, _ := keFloat(a)
	y, _ := keFloat(b)
	return x / y
}

// pangkat sama dengan a ** b Python.
func pangkat(a, b any) any {
	if adalahBulat(a) && adalahBulat(b) {
		bb := keBig(b)
		if bb.Sign() >= 0 {
			ba := keBig(a)
			if ba.BitLen() > 1 && bb.BitLen() > 31 {
				panic(galatPython{"MemoryError"})
			}
			if bb.IsInt64() && int64(ba.BitLen())*bb.Int64() > 1<<25 && ba.BitLen() > 1 {
				panic(galatPython{"MemoryError"})
			}
			return normalBulat(new(big.Int).Exp(ba, bb, nil))
		}
	}
	x, _ := keFloat(a)
	y, _ := keFloat(b)
	return pangkatFloat(x, y)
}

// pangkatFloat sama dengan float_pow di CPython.
func pangkatFloat(x, y float64) float64 {
	if y == 0 {
		return 1
	}
	if math.IsNaN(x) {
		return x
	}
	if math.IsNaN(y) {
		if x == 1 {
			return 1
		}
		return y
	}
	if math.IsInf(y, 0) {
		ax := math.Abs(x)
		switch {
		case ax == 1:
			return 1
		case (ax > 1) == (y > 0):
			return math.Inf(1)
		default:
			return 0
		}
	}
	if math.IsInf(x, 0) {
		ganjil := math.Mod(math.Abs(y), 2) == 1
		if y > 0 {
			if ganjil {
				return x
			}
			return math.Abs(x)
		}
		if ganjil {
			return math.Copysign(0, x)
		}
		return 0
	}
	if x == 0 {
		if y < 0 {
			panic(galatPython{"ZeroDivisionError"})
		}
		if math.Mod(math.Abs(y), 2) == 1 {
			return x
		}
		return 0
	}
	if x < 0 && y != math.Floor(y) {
		panic(galatPython{"complex"}) // hasilnya bilangan kompleks
	}
	// Seperti float_pow CPython: hitung |x|^y lalu beri tanda minus bila y bilangan ganjil.
	negatif := x < 0 && math.Mod(math.Abs(y), 2) == 1
	x = math.Abs(x)
	var hasil float64
	switch {
	case x == 1:
		hasil = 1
	case y == 0.5:
		hasil = math.Sqrt(x)
	default:
		hasil = powTepat(x, y)
	}
	if math.IsInf(hasil, 0) {
		panic(galatPython{"OverflowError"})
	}
	if negatif {
		hasil = -hasil
	}
	return hasil
}

// ---- Perbandingan ----

// bandingAngka membandingkan dua angka secara tepat seperti Python: -1, 0, 1, atau 2 (NaN).
func bandingAngka(a, b any) int {
	fa, aFloat := a.(float64)
	fb, bFloat := b.(float64)
	switch {
	case !aFloat && !bFloat:
		x, ok1 := bulatKeInt(a)
		y, ok2 := bulatKeInt(b)
		if ok1 && ok2 {
			switch {
			case x < y:
				return -1
			case x > y:
				return 1
			}
			return 0
		}
		return keBig(a).Cmp(keBig(b))
	case aFloat && bFloat:
		switch {
		case math.IsNaN(fa) || math.IsNaN(fb):
			return 2
		case fa < fb:
			return -1
		case fa > fb:
			return 1
		}
		return 0
	case aFloat:
		return -bandingBulatFloat(b, fa)
	default:
		return bandingBulatFloat(a, fb)
	}
}

// bandingBulatFloat membandingkan bilangan bulat dengan desimal secara tepat.
func bandingBulatFloat(n any, f float64) int {
	if math.IsNaN(f) {
		return 2
	}
	if math.IsInf(f, 1) {
		return -1
	}
	if math.IsInf(f, -1) {
		return 1
	}
	if x, ok := bulatKeInt(n); ok && absInt(x) <= 1<<53 {
		g := float64(x)
		switch {
		case g < f:
			return -1
		case g > f:
			return 1
		}
		return 0
	}
	bf := new(big.Float).SetPrec(0).SetFloat64(f)
	bn := new(big.Float).SetPrec(uint(keBig(n).BitLen()) + 64).SetInt(keBig(n))
	return bn.Cmp(bf)
}
