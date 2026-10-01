package mesin

import (
	"math"
	"math/big"
	"math/rand"
	"strconv"
	"testing"
)

// pangkatTepatAcuan menghitung x^n persis dengan pecahan (big.Rat) lalu membulatkannya.
func pangkatTepatAcuan(x float64, n int) float64 {
	r := new(big.Rat).SetFloat64(x)
	hasil := big.NewRat(1, 1)
	for i := 0; i < abs(n); i++ {
		hasil.Mul(hasil, r)
	}
	if n < 0 {
		hasil.Inv(hasil)
	}
	f, _ := hasil.Float64()
	return f
}

func abs(n int) int {
	if n < 0 {
		return -n
	}
	return n
}

func TestPangkatBulatDibulatkanTepat(t *testing.T) {
	r := rand.New(rand.NewSource(1))
	for i := 0; i < 3000; i++ {
		x := r.Float64() * 10
		if i%3 == 0 {
			x = 0.5 + r.Float64()
		}
		n := r.Intn(61) - 30
		if x == 0 || n == 0 {
			continue
		}
		if got, want := pangkatFloat(x, float64(n)), pangkatTepatAcuan(x, n); got != want {
			t.Fatalf("%v ** %d = %v, seharusnya %v", x, n, got, want)
		}
	}
}

func TestPangkatSepertiPython(t *testing.T) {
	// Nilai dari Python (pow() pustaka C); math.Pow Go memberi hasil yang berbeda 1 ulp.
	kasus := []struct{ x, y, hasil string }{
		{"0x1.4p+3", "0x1.2cp+8", "0x1.7e43c8800759cp+996"}, // 10.0 ** 300 == 1e300
		{"0x1.8p+0", "0x1.4p+1", "0x1.60b9fd68a4554p+1"},    // 1.5 ** 2.5
		{"0x1.0cccccccccccdp+0", "0x1.4p+3", "0x1.a0ff3cfea3a53p+0"},
		{"0x1.199999999999ap+0", "0x1.3333333333333p-2", "0x1.076cebe41bf7ap+0"},
		{"0x1.8p+0", "-0x1.c2p+10", "0x0.0000000218862p-1022"},           // subnormal
		{"0x1.000001ad7f29bp+0", "0x1.312dp+23", "0x1.5bf0a790ce6f2p+1"}, // 1.0000001 ** 10000000
	}
	for _, k := range kasus {
		x, _ := strconv.ParseFloat(k.x, 64)
		y, _ := strconv.ParseFloat(k.y, 64)
		want, _ := strconv.ParseFloat(k.hasil, 64)
		if got := pangkatFloat(x, y); got != want {
			t.Errorf("%s ** %s = %s, seharusnya %s", k.x, k.y, strconv.FormatFloat(got, 'x', -1, 64), k.hasil)
		}
	}
	// pow() glibc tidak selalu dibulatkan tepat: Python memberi ...3d3p+3 di sini. Mesin ini memilih
	// hasil yang dibulatkan tepat, sama dengan x * x.
	x, _ := strconv.ParseFloat("0x1.df1903d86aee0p+1", 64)
	if got := pangkatFloat(x, 2); got != x*x {
		t.Errorf("x ** 2 = %v, seharusnya x * x = %v", got, x*x)
	}
}

func TestLogaritmaDibulatkanTepat(t *testing.T) {
	for _, x := range []float64{2, 10, 0.1, 1e-300, 1e300, math.E, 7.5} {
		if got, want := lnTepat(x), math.Log(x); math.Abs(got-want) > 2e-16*math.Abs(want) {
			t.Errorf("ln(%v) = %v, jauh dari %v", x, got, want)
		}
	}
	if lnTepat(10) != 2.302585092994046 || lnTepat(2) != 0.6931471805599453 {
		t.Error("ln(10) atau ln(2) berbeda dari Python")
	}
}
