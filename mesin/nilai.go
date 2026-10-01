package mesin

import (
	"math"
	"math/big"
	"strconv"
	"strings"
)

// Nilai dalam bahasa ini direpresentasikan sebagai `any`:
//   nil (kosong), bool (logika), int / *big.Int (bilangan), float64 (desimal), string (teks),
//   *TeksKesalahan, *Daftar, *Kamus, *Fungsi, *FungsiBawaan, *Kelas, *Instansi,
//   *MetodeTerikat, *Induk, *Modul.

// TeksKesalahan: isi variabel 'tangkap sebagai e'. Berlaku seperti teks, plus e.pesan dan e.jenis.
type TeksKesalahan struct {
	Teks  string
	Jenis string
}

type Daftar struct{ Elemen []any }

type Modul struct {
	Nama   string
	Isi    map[string]any
	Urutan []string
}

type Kelas struct {
	Nama    string
	Induk   *Kelas
	Metode  map[string]*Fungsi
	Atribut *Kamus // nama → nilai bawaan, berurutan
}

func (k *Kelas) cariMetode(nama string) *Fungsi {
	for kl := k; kl != nil; kl = kl.Induk {
		if f, ada := kl.Metode[nama]; ada {
			return f
		}
	}
	return nil
}

type Instansi struct {
	Kelas   *Kelas
	Atribut *Kamus
}

type MetodeTerikat struct {
	Instansi *Instansi
	Fungsi   *Fungsi
}

type Induk struct {
	Instansi *Instansi
	Kelas    *Kelas
}

// teksDari: nilai teks (string atau TeksKesalahan).
func teksDari(v any) (string, bool) {
	switch x := v.(type) {
	case string:
		return x, true
	case *TeksKesalahan:
		return x.Teks, true
	}
	return "", false
}

// ---- Tampilan (_ke_teks) ----

func keTeks(v any) string {
	var b strings.Builder
	tulisTeks(&b, v, 0)
	return b.String()
}

const batasBersarang = 10000

var errBersarang = kesalahanTanpaLokasi(KTumpukan,
	"Program bertumpuk terlalu dalam (mis. ekspresi atau rekursi yang sangat bersarang)")

func tulisTeks(b *strings.Builder, v any, kedalaman int) {
	if kedalaman > batasBersarang {
		panic(errBersarang)
	}
	switch x := v.(type) {
	case nil:
		b.WriteString("kosong")
	case bool:
		if x {
			b.WriteString("benar")
		} else {
			b.WriteString("salah")
		}
	case int:
		b.WriteString(strconv.Itoa(x))
	case *big.Int:
		b.WriteString(x.String())
	case float64:
		b.WriteString(teksDesimal(x))
	case string:
		b.WriteString(x)
	case *TeksKesalahan:
		b.WriteString(x.Teks)
	case *Daftar:
		b.WriteByte('[')
		for i, e := range x.Elemen {
			if i > 0 {
				b.WriteString(", ")
			}
			tulisTeks(b, e, kedalaman+1)
		}
		b.WriteByte(']')
	case *Kamus:
		b.WriteByte('{')
		for i := range x.kunci {
			if i > 0 {
				b.WriteString(", ")
			}
			tulisTeks(b, x.kunci[i], kedalaman+1)
			b.WriteString(": ")
			tulisTeks(b, x.nilai[i], kedalaman+1)
		}
		b.WriteByte('}')
	case *Fungsi:
		b.WriteString("<fungsi " + x.Nama + ">")
	case *FungsiBawaan:
		b.WriteString("<fungsi bawaan>")
	case *Kelas:
		b.WriteString("<kelas " + x.Nama + ">")
	case *Instansi:
		b.WriteString("<" + x.Kelas.Nama + " instansi>")
	case *MetodeTerikat:
		b.WriteString("<metode " + x.Fungsi.Nama + " dari " + x.Instansi.Kelas.Nama + ">")
	case *Induk:
		b.WriteString("<induk " + x.Kelas.Nama + ">")
	case *Modul:
		b.WriteString("<modul " + x.Nama + ">")
	default:
		b.WriteString("?")
	}
}

// jenisNilai sama dengan _jenis().
func jenisNilai(v any) string {
	switch v.(type) {
	case nil:
		return "kosong"
	case bool:
		return "logika"
	case int, *big.Int:
		return "bilangan"
	case float64:
		return "desimal"
	case string, *TeksKesalahan:
		return "teks"
	case *Daftar:
		return "daftar"
	case *Kamus:
		return "kamus"
	case *Kelas:
		return "kelas"
	case *Modul:
		return "modul"
	case *Instansi:
		return "objek"
	case *Fungsi, *FungsiBawaan, *MetodeTerikat:
		return "fungsi"
	}
	return "objek"
}

// benarkah: nilai kebenaran ala Python; daftar & kamus kosong bernilai salah.
func benarkah(v any) bool {
	switch x := v.(type) {
	case nil:
		return false
	case bool:
		return x
	case int:
		return x != 0
	case *big.Int:
		return x.Sign() != 0
	case float64:
		return x != 0
	case string:
		return x != ""
	case *TeksKesalahan:
		return x.Teks != ""
	case *Daftar:
		return len(x.Elemen) > 0
	case *Kamus:
		return x.Panjang() > 0
	}
	return true
}

// samaDengan: == Python. Daftar, kamus, dan objek lain sama hanya bila objeknya sama.
func samaDengan(a, b any) bool {
	if adalahAngkaNilai(a) && adalahAngkaNilai(b) {
		return bandingAngka(a, b) == 0
	}
	if sa, ok := teksDari(a); ok {
		sb, ok := teksDari(b)
		return ok && sa == sb
	}
	if a == nil || b == nil {
		return a == nil && b == nil
	}
	switch x := a.(type) {
	case bool, int, *big.Int, float64, string, *TeksKesalahan:
		return false
	case *FungsiBawaan:
		// Metode terikat Python sama bila pemilik dan fungsinya sama: d.tambahkan == d.tambahkan
		if y, ok := b.(*FungsiBawaan); ok && x.terikat != nil {
			return x.terikat == y.terikat && x.Nama == y.Nama
		}
	}
	return a == b
}

// kunciHash: kunci peta Go untuk kunci kamus, mengikuti hash() Python (1 == 1.0 == benar).
type kunciHash struct {
	jenis uint8
	n     int64
	s     string
	p     any
}

func buatKunciHash(v any) kunciHash {
	switch x := v.(type) {
	case nil:
		return kunciHash{jenis: 1}
	case bool:
		if x {
			return kunciHash{jenis: 2, n: 1}
		}
		return kunciHash{jenis: 2}
	case int:
		return kunciHash{jenis: 2, n: int64(x)}
	case *big.Int:
		return kunciHash{jenis: 3, s: x.String()}
	case float64:
		if x == math.Trunc(x) && !math.IsInf(x, 0) {
			if math.Abs(x) < 1<<62 {
				return kunciHash{jenis: 2, n: int64(x)}
			}
			b, _ := new(big.Float).SetFloat64(x).Int(nil)
			if b.IsInt64() {
				return kunciHash{jenis: 2, n: b.Int64()}
			}
			return kunciHash{jenis: 3, s: b.String()}
		}
		return kunciHash{jenis: 4, n: int64(math.Float64bits(x))}
	case string:
		return kunciHash{jenis: 5, s: x}
	case *TeksKesalahan:
		return kunciHash{jenis: 5, s: x.Teks}
	}
	return kunciHash{jenis: 6, p: v}
}

// Kamus: dictionary yang menjaga urutan masuk, dengan kunci ala Python.
type Kamus struct {
	kunci  []any
	nilai  []any
	indeks map[kunciHash]int
}

func kamusBaru() *Kamus { return &Kamus{indeks: map[kunciHash]int{}} }

func (k *Kamus) Ambil(kunci any) (any, bool) {
	if i, ada := k.indeks[buatKunciHash(kunci)]; ada {
		return k.nilai[i], true
	}
	return nil, false
}

func (k *Kamus) Setel(kunci, nilai any) {
	h := buatKunciHash(kunci)
	if i, ada := k.indeks[h]; ada {
		k.nilai[i] = nilai // kunci lama tetap dipakai, seperti dict Python
		return
	}
	k.indeks[h] = len(k.kunci)
	k.kunci = append(k.kunci, kunci)
	k.nilai = append(k.nilai, nilai)
}

func (k *Kamus) Ada(kunci any) bool {
	_, ada := k.indeks[buatKunciHash(kunci)]
	return ada
}

func (k *Kamus) Hapus(kunci any) bool {
	i, ada := k.indeks[buatKunciHash(kunci)]
	if !ada {
		return false
	}
	k.kunci = append(k.kunci[:i:i], k.kunci[i+1:]...)
	k.nilai = append(k.nilai[:i:i], k.nilai[i+1:]...)
	k.indeks = make(map[kunciHash]int, len(k.kunci))
	for j, kunci := range k.kunci {
		k.indeks[buatKunciHash(kunci)] = j
	}
	return true
}

func (k *Kamus) Panjang() int { return len(k.kunci) }

func (k *Kamus) salin() *Kamus {
	baru := &Kamus{
		kunci:  append([]any(nil), k.kunci...),
		nilai:  append([]any(nil), k.nilai...),
		indeks: make(map[kunciHash]int, len(k.indeks)),
	}
	for h, i := range k.indeks {
		baru.indeks[h] = i
	}
	return baru
}

// ---- Urutan (<, >) ----

// banding: urutan dua nilai (<0, 0, >0); ok=false bila tidak bisa dibandingkan (TypeError).
func banding(a, b any) (hasil int, ok bool) {
	if adalahAngkaNilai(a) && adalahAngkaNilai(b) {
		return bandingAngka(a, b), true
	}
	sa, ok1 := teksDari(a)
	sb, ok2 := teksDari(b)
	if ok1 && ok2 {
		return strings.Compare(sa, sb), true
	}
	return 0, false
}
