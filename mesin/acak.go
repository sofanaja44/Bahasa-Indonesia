package mesin

import (
	crand "crypto/rand"
	"crypto/sha512"
	"encoding/binary"
	"math"
	"math/big"
	"math/bits"
	"time"
)

// acakPython adalah Mersenne Twister (MT19937) dengan algoritma modul random Python, sehingga
// 'acak.atur_benih(42)' menghasilkan deret angka yang sama persis dengan versi Python.
type acakPython struct {
	mt     [624]uint32
	indeks int
}

func acakBaru() *acakPython {
	r := &acakPython{}
	r.benihAcak()
	return r
}

// benihAcak sama dengan random.seed(None): benih dari sumber acak sistem.
func (r *acakPython) benihAcak() {
	var b [624 * 4]byte
	kunci := make([]uint32, 624)
	if _, err := crand.Read(b[:]); err == nil {
		for i := range kunci {
			kunci[i] = binary.LittleEndian.Uint32(b[4*i:])
		}
	} else {
		t := uint64(time.Now().UnixNano())
		kunci = []uint32{uint32(t), uint32(t >> 32)}
	}
	r.initByArray(kunci)
}

func (r *acakPython) initGenrand(s uint32) {
	r.mt[0] = s
	for i := 1; i < 624; i++ {
		r.mt[i] = 1812433253*(r.mt[i-1]^(r.mt[i-1]>>30)) + uint32(i)
	}
	r.indeks = 624
}

func (r *acakPython) initByArray(kunci []uint32) {
	r.initGenrand(19650218)
	i, j := 1, 0
	k := 624
	if len(kunci) > k {
		k = len(kunci)
	}
	for ; k > 0; k-- {
		r.mt[i] = (r.mt[i] ^ ((r.mt[i-1] ^ (r.mt[i-1] >> 30)) * 1664525)) + kunci[j] + uint32(j)
		i++
		j++
		if i >= 624 {
			r.mt[0] = r.mt[623]
			i = 1
		}
		if j >= len(kunci) {
			j = 0
		}
	}
	for k = 623; k > 0; k-- {
		r.mt[i] = (r.mt[i] ^ ((r.mt[i-1] ^ (r.mt[i-1] >> 30)) * 1566083941)) - uint32(i)
		i++
		if i >= 624 {
			r.mt[0] = r.mt[623]
			i = 1
		}
	}
	r.mt[0] = 0x80000000
}

func (r *acakPython) genrand() uint32 {
	const n, m = 624, 397
	mag01 := [2]uint32{0, 0x9908b0df}
	if r.indeks >= n {
		kk := 0
		for ; kk < n-m; kk++ {
			y := (r.mt[kk] & 0x80000000) | (r.mt[kk+1] & 0x7fffffff)
			r.mt[kk] = r.mt[kk+m] ^ (y >> 1) ^ mag01[y&1]
		}
		for ; kk < n-1; kk++ {
			y := (r.mt[kk] & 0x80000000) | (r.mt[kk+1] & 0x7fffffff)
			r.mt[kk] = r.mt[kk+(m-n)] ^ (y >> 1) ^ mag01[y&1]
		}
		y := (r.mt[n-1] & 0x80000000) | (r.mt[0] & 0x7fffffff)
		r.mt[n-1] = r.mt[m-1] ^ (y >> 1) ^ mag01[y&1]
		r.indeks = 0
	}
	y := r.mt[r.indeks]
	r.indeks++
	y ^= y >> 11
	y ^= (y << 7) & 0x9d2c5680
	y ^= (y << 15) & 0xefc60000
	y ^= y >> 18
	return y
}

// benihBulat sama dengan random.seed(n) untuk bilangan bulat: memakai nilai mutlaknya.
func (r *acakPython) benihBulat(n *big.Int) {
	b := new(big.Int).Abs(n).Bytes() // big-endian
	jumlah := (len(b) + 3) / 4
	if jumlah == 0 {
		jumlah = 1
	}
	kunci := make([]uint32, jumlah)
	for i := 0; i < len(b); i++ {
		kunci[i/4] |= uint32(b[len(b)-1-i]) << (8 * (i % 4))
	}
	r.initByArray(kunci)
}

// random() sama dengan random.random(): desimal 53 bit dalam [0, 1).
func (r *acakPython) random() float64 {
	a := r.genrand() >> 5
	b := r.genrand() >> 6
	return (float64(a)*67108864.0 + float64(b)) * (1.0 / 9007199254740992.0)
}

// bitAcakKecil sama dengan getrandbits(k) untuk 1 <= k <= 64.
func (r *acakPython) bitAcakKecil(k int) uint64 {
	if k <= 32 {
		return uint64(r.genrand() >> (32 - k))
	}
	lo := uint64(r.genrand())
	hi := uint64(r.genrand() >> (64 - k))
	return hi<<32 | lo
}

// bitAcakBesar sama dengan getrandbits(k) untuk k berapa pun.
func (r *acakPython) bitAcakBesar(k int) *big.Int {
	jumlah := (k-1)/32 + 1
	b := make([]byte, jumlah*4)
	for i := 0; i < jumlah; i, k = i+1, k-32 {
		x := r.genrand()
		if k < 32 {
			x >>= 32 - k
		}
		binary.BigEndian.PutUint32(b[(jumlah-1-i)*4:], x)
	}
	return new(big.Int).SetBytes(b)
}

// bawah sama dengan _randbelow(n): bilangan bulat acak dalam [0, n), n > 0.
func (r *acakPython) bawah(n any) any {
	if x, ok := n.(int); ok {
		k := bits.Len64(uint64(x))
		for {
			if v := r.bitAcakKecil(k); v < uint64(x) {
				return int(v)
			}
		}
	}
	nb := keBig(n)
	k := nb.BitLen()
	for {
		if v := r.bitAcakBesar(k); v.Cmp(nb) < 0 {
			return normalBulat(v)
		}
	}
}

// randint sama dengan random.randint(a, b).
func (r *acakPython) randint(a, b any) any {
	lebar := tambahBulat(kurangBulat(b, a), 1)
	return tambahBulat(a, r.bawah(lebar))
}

func (r *acakPython) kocok(isi []any) {
	for i := len(isi) - 1; i >= 1; i-- {
		j := r.bawah(i + 1).(int)
		isi[i], isi[j] = isi[j], isi[i]
	}
}

// hashDesimal sama dengan hash(float) Python (dipakai random.seed untuk desimal).
func hashDesimal(v float64) int64 {
	if math.IsInf(v, 1) {
		return 314159
	}
	if math.IsInf(v, -1) {
		return -314159
	}
	if math.IsNaN(v) {
		return 0 // di Python bergantung pada alamat objek
	}
	const bitHash = 61
	const modulus = (1 << bitHash) - 1
	m, e := math.Frexp(v)
	tanda := int64(1)
	if m < 0 {
		tanda, m = -1, -m
	}
	var x uint64
	for m != 0 {
		x = ((x << 28) & modulus) | x>>(bitHash-28)
		m *= 268435456.0
		e -= 28
		y := uint64(m)
		m -= float64(y)
		x += y
		if x >= modulus {
			x -= modulus
		}
	}
	if e >= 0 {
		e %= bitHash
	} else {
		e = bitHash - 1 - ((-1 - e) % bitHash)
	}
	x = ((x << uint(e)) & modulus) | x>>(bitHash-uint(e))
	h := int64(x) * tanda
	if h == -1 {
		h = -2
	}
	return h
}

// aturBenih sama dengan random.seed(benih).
func (r *acakPython) aturBenih(benih any) {
	switch v := benih.(type) {
	case nil:
		r.benihAcak()
	case bool, int, *big.Int:
		r.benihBulat(keBig(v))
	case float64:
		r.benihBulat(new(big.Int).SetUint64(uint64(hashDesimal(v))))
	default:
		s, ok := teksDari(v)
		if !ok {
			panic(galatPython{"TypeError"})
		}
		b := []byte(s)
		h := sha512.Sum512(b)
		r.benihBulat(new(big.Int).SetBytes(append(b, h[:]...)))
	}
}
