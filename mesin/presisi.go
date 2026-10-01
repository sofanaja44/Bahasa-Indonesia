package mesin

import (
	"math"
	"math/big"
	"sync"
)

// Pangkat dan logaritma yang dibulatkan dengan tepat (correctly rounded): hasilnya selalu desimal
// float64 yang paling dekat dengan nilai sebenarnya, seperti pow() dan log() pustaka C yang dipakai
// Python. math.Pow dan math.Log milik Go kadang meleset 1 ulp (mis. 10.0 ** 300), sehingga hasil
// perhitungan bisa berbeda dari Python di digit terakhir.

// ---- Aritmetika double-double (±106 bit) untuk jalur cepat ----
//
// Penting: di ARM64, kompilator Go boleh menggabungkan x*y + z menjadi satu instruksi FMA, juga
// melintasi pernyataan. Itu merusak trik "jumlah tanpa galat" di bawah, yang mengandalkan setiap
// hasil kali dibulatkan lebih dulu. Konversi float64(...) yang eksplisit mencegah penggabungan itu.

type dd struct{ hi, lo float64 }

func ddKali(x, y dd) dd {
	p := float64(x.hi * y.hi)
	e := math.FMA(x.hi, y.hi, -p) // galat perkalian, tepat
	e += x.hi*y.lo + x.lo*y.hi
	s := p + e
	return dd{s, e - (s - p)}
}

// ddNormal menjaga hi di [0.5, 1) agar tidak meluap; eksponennya dikumpulkan di e.
func ddNormal(x dd, e *int64) dd {
	_, k := math.Frexp(x.hi)
	*e += int64(k)
	return dd{math.Ldexp(x.hi, -k), math.Ldexp(x.lo, -k)}
}

// pangkatBulatCepat menghitung x^n (x > 0 terhingga, n >= 1) dengan double-double; bila negatif,
// hasilnya 1/x^n. ok=false bila hasilnya terlalu dekat ke titik tengah dua float64 (pembulatannya
// meragukan) atau berada di wilayah subnormal; pemanggil lalu memakai perhitungan tepat.
func pangkatBulatCepat(x float64, n uint64, negatif bool) (float64, bool) {
	m, ex := math.Frexp(x) // x = m·2^ex
	var eh, eb int64       // hasil = h·2^eh, basis = b·2^eb
	h, b := dd{1, 0}, dd{m, 0}
	for k := n; k > 0; k >>= 1 {
		if k&1 == 1 {
			h = ddKali(h, b)
			eh += eb
			h = ddNormal(h, &eh)
		}
		if k > 1 {
			b = ddKali(b, b)
			eb *= 2
			b = ddNormal(b, &eb)
		}
	}
	total := eh + int64(ex)*int64(n) // x^n = h·2^total, h di [0.5, 1)
	batas := float64(n) * 0x1p-100   // perkiraan galat relatif yang aman
	if negatif {
		q1 := 1 / h.hi
		r := math.FMA(-q1, h.hi, 1) - q1*h.lo
		q2 := float64(r * q1)
		s := q1 + q2
		var eq int64
		h = ddNormal(dd{s, q2 - (s - q1)}, &eq) // 1/(h·2^t) = (1/h)·2^-t
		total = eq - total
		batas += 0x1p-100
	}
	if total < -1020 || h.hi == 0.5 {
		return 0, false
	}
	if math.Abs(math.Abs(h.lo)-0x1p-54) <= batas {
		return 0, false
	}
	return math.Ldexp(h.hi, int(total)), true
}

// ---- Presisi tinggi dengan big.Float ----

var (
	kunciLn2  sync.Mutex
	simpanLn2 = map[uint]*big.Float{}
)

func bigF(prec uint) *big.Float { return new(big.Float).SetPrec(prec) }

// atanh2 menghitung 2·atanh(z) = 2 Σ z^(2k+1)/(2k+1), untuk |z| kecil.
func atanh2(z *big.Float, prec uint) *big.Float {
	z2 := bigF(prec).Mul(z, z)
	suku := bigF(prec).Set(z)
	jumlah := bigF(prec).Set(z)
	t := bigF(prec)
	pembagi := bigF(prec)
	for k := int64(1); ; k++ {
		suku.Mul(suku, z2)
		t.Quo(suku, pembagi.SetInt64(2*k+1))
		jumlah.Add(jumlah, t)
		if t.Sign() == 0 || t.MantExp(nil) < jumlah.MantExp(nil)-int(prec)-8 {
			break
		}
	}
	return jumlah.SetMantExp(jumlah, 1)
}

// ln2Big: ln 2 = 2·atanh(1/3).
func ln2Big(prec uint) *big.Float {
	kunciLn2.Lock()
	defer kunciLn2.Unlock()
	if v, ada := simpanLn2[prec]; ada {
		return v
	}
	sepertiga := bigF(prec+16).Quo(big.NewFloat(1), big.NewFloat(3))
	v := bigF(prec).Set(atanh2(sepertiga, prec+16))
	simpanLn2[prec] = v
	return v
}

// lnBig menghitung ln(x) untuk x > 0.
func lnBig(x *big.Float, prec uint) *big.Float {
	kerja := prec + 32
	m := bigF(kerja)
	e := x.MantExp(m) // x = m·2^e, m di [0.5, 1)
	if m.Cmp(big.NewFloat(math.Sqrt2/2)) < 0 {
		m.SetMantExp(m, 1)
		e--
	}
	satu := big.NewFloat(1)
	z := bigF(kerja).Quo(bigF(kerja).Sub(m, satu), bigF(kerja).Add(m, satu))
	hasil := atanh2(z, kerja)
	if e != 0 {
		hasil.Add(hasil, bigF(kerja).Mul(ln2Big(kerja), bigF(kerja).SetInt64(int64(e))))
	}
	return hasil
}

// expBig menghitung e^t untuk |t| < 800.
func expBig(t *big.Float, prec uint) *big.Float {
	const paruh = 24 // r dibagi 2^24 lalu hasilnya dikuadratkan 24 kali
	kerja := prec + paruh + 32
	ln2 := ln2Big(kerja)
	q, _ := bigF(kerja).Quo(t, ln2).Float64()
	k := int64(math.Round(q))
	r := bigF(kerja).Sub(t, bigF(kerja).Mul(ln2, bigF(kerja).SetInt64(k)))
	r.SetMantExp(r, -paruh)
	jumlah := bigF(kerja).SetInt64(1)
	suku := bigF(kerja).SetInt64(1)
	pembagi := bigF(kerja)
	for n := int64(1); ; n++ {
		suku.Mul(suku, r)
		suku.Quo(suku, pembagi.SetInt64(n))
		jumlah.Add(jumlah, suku)
		if suku.Sign() == 0 || suku.MantExp(nil) < -int(kerja)-8 {
			break
		}
	}
	for i := 0; i < paruh; i++ {
		jumlah.Mul(jumlah, jumlah)
	}
	return jumlah.SetMantExp(jumlah, int(k))
}

// bulatkanTepat: hitung(prec) memberi nilai dengan galat relatif < 2^-prec. Presisi dinaikkan
// sampai kedua ujung selang galat dibulatkan ke float64 yang sama.
func bulatkanTepat(hitung func(prec uint) *big.Float) float64 {
	for prec := uint(96); prec <= 3072; prec *= 2 {
		v := hitung(prec)
		galat := bigF(prec+8).SetMantExp(bigF(prec+8).Abs(v), -int(prec))
		bawah, _ := bigF(prec+8).Sub(v, galat).Float64()
		atas, _ := bigF(prec+8).Add(v, galat).Float64()
		if bawah == atas {
			return bawah
		}
	}
	f, _ := hitung(6144).Float64()
	return f
}

// lnTepat: ln(x) yang dibulatkan tepat, untuk x > 0 terhingga.
func lnTepat(x float64) float64 {
	if x == 1 {
		return 0
	}
	bx := new(big.Float).SetFloat64(x)
	return bulatkanTepat(func(prec uint) *big.Float { return lnBig(bx, prec) })
}

// powTepat: x^y yang dibulatkan tepat, untuk x > 0 terhingga, x != 1, dan y terhingga bukan 0.
// Hasilnya bisa +Inf (meluap) atau 0/subnormal.
func powTepat(x, y float64) float64 {
	// Perkiraan kasar untuk meluap/menyusut jauh di luar jangkauan float64.
	if perkiraan := y * math.Log(x); perkiraan > 712 {
		return math.Inf(1)
	} else if perkiraan < -748 {
		return 0
	}
	if y == math.Trunc(y) && math.Abs(y) <= 1<<16 {
		return pangkatBulatTepat(x, int64(y))
	}
	bx := new(big.Float).SetFloat64(x)
	by := new(big.Float).SetFloat64(y)
	return bulatkanTepat(func(prec uint) *big.Float {
		kerja := prec + 24
		t := bigF(kerja).Mul(by, lnBig(bx, kerja))
		return expBig(t, prec+8)
	})
}

// pangkatBulatTepat: x^n untuk bilangan bulat n, dihitung tepat dengan big.Float lalu dibulatkan.
func pangkatBulatTepat(x float64, n int64) float64 {
	if n == 1 {
		return x
	}
	if n == -1 {
		return 1 / x
	}
	if n == 2 {
		return x * x
	}
	k := n
	if k < 0 {
		k = -k
	}
	if f, ok := pangkatBulatCepat(x, uint64(k), n < 0); ok {
		return f
	}
	// x punya paling banyak 53 bit, jadi x^k punya paling banyak 53·k bit: presisi ini tepat.
	tepat := uint(53*k + 64)
	if tepat > 1<<20 {
		tepat = 1 << 20
	}
	pangkat := bigF(tepat).SetInt64(1)
	basis := bigF(tepat).SetFloat64(x)
	for e := k; e > 0; e >>= 1 {
		if e&1 == 1 {
			pangkat.Mul(pangkat, basis)
		}
		if e > 1 {
			basis.Mul(basis, basis)
		}
	}
	if n > 0 {
		f, _ := pangkat.Float64()
		return f
	}
	return bulatkanTepat(func(prec uint) *big.Float {
		return bigF(prec+8).Quo(big.NewFloat(1), pangkat)
	})
}
