package mesin

import (
	"fmt"
	"math"
	"math/big"
	"strings"
	"time"
)

// BatasRekursi: paling banyak sekian panggilan fungsi bertumpuk.
const BatasRekursi = 3000

// IO menghubungkan mesin dengan dunia luar (layar, papan ketik, jam).
type IO struct {
	Tulis    func(teks string)                  // tampilkan teks di layar
	Baca     func(prompt string) (string, bool) // baca satu baris; false bila masukan habis
	Tidur    func(detik float64)                // berhenti sejenak
	Berhenti func() bool                        // diperiksa berkala: benar bila program harus dihentikan
	Sekarang func() time.Time
	Berkas   SistemBerkas // tempat modul 'berkas' membaca & menulis (nil: berkas di komputer)
}

// ErrDihentikan: program dihentikan dari luar (Ctrl+C atau tombol Hentikan). Tidak bisa ditangkap 'coba'.
type galatBerhenti struct{}

func (galatBerhenti) Error() string { return "Program dihentikan." }

var ErrDihentikan error = galatBerhenti{}

// GalatInternal: kemungkinan besar bug pada mesin.
type GalatInternal struct{ Pesan string }

func (g *GalatInternal) Error() string { return g.Pesan }

type entriLingkup struct {
	sym   int32
	tetap bool
	nilai any
}

// Lingkup adalah satu tingkat variabel (blok, fungsi). Lingkup global disimpan terpisah di Mesin.
// Tiga variabel pertama disimpan di dalam struct itu sendiri, jadi kebanyakan lingkup cukup
// satu alokasi memori.
type Lingkup struct {
	induk *Lingkup
	isi   []entriLingkup
	kecil [3]entriLingkup
}

func lingkupBaru(induk *Lingkup) *Lingkup {
	l := &Lingkup{induk: induk}
	l.isi = l.kecil[:0]
	return l
}

// bersihkan menghapus semua variabel lingkup ini (dipakai ulang tanpa alokasi baru).
func (l *Lingkup) bersihkan() {
	for i := range l.isi {
		l.isi[i] = entriLingkup{}
	}
	l.isi = l.isi[:0]
}

func (l *Lingkup) cari(s int32) int {
	for i := range l.isi {
		if l.isi[i].sym == s {
			return i
		}
	}
	return -1
}

func (l *Lingkup) definisikan(s int32, v any, tetap bool) {
	if i := l.cari(s); i >= 0 {
		l.isi[i].nilai = v
		if tetap {
			l.isi[i].tetap = true
		}
		return
	}
	l.isi = append(l.isi, entriLingkup{s, tetap, v})
}

type penangan struct {
	ip      int
	tinggi  int
	lingkup *Lingkup
}

type bingkai struct {
	kode     *Kode
	ip       int
	lingkup  *Lingkup
	dasar    int
	penangan []penangan
	instansi *Instansi // pemanggilan 'inisialisasi': hasilnya instansi ini
	daur     *Lingkup  // lingkup pemanggilan yang boleh dipakai ulang setelah bingkai ini selesai
	hitung   bool      // dihitung dalam batas rekursi
	batas    bool      // putaran mesin berhenti ketika bingkai ini selesai
}

// galatTerbang: kesalahan yang sedang ditangani, disimpan di tumpukan selama 'tangkap'/'akhirnya'.
type galatTerbang struct{ err error }

type iterator struct {
	daftar *Daftar
	isi    []any
	i      int
}

// Mesin menjalankan program Bahasa Indonesia.
type Mesin struct {
	io          IO
	simbol      map[string]int32
	namaSimbol  []string
	globalNilai []any
	globalAda   []bool
	globalTetap []bool
	tumpukan    []any
	bingkai     []*bingkai
	kedalaman   int
	acak        *acakPython
	cadangan    []*bingkai // bingkai bekas yang bisa dipakai ulang
	cadanganL   []*Lingkup // lingkup pemanggilan bekas (fungsi tanpa closure)
	hasil       any
	adaHasil    bool
	langkah     uint32
}

// Baru membuat mesin baru dengan fungsi bawaan.
func Baru(io IO) *Mesin {
	if io.Tulis == nil {
		io.Tulis = func(string) {}
	}
	if io.Baca == nil {
		io.Baca = func(string) (string, bool) { return "", false }
	}
	if io.Tidur == nil {
		io.Tidur = func(d float64) { time.Sleep(time.Duration(d * float64(time.Second))) }
	}
	if io.Sekarang == nil {
		io.Sekarang = time.Now
	}
	m := &Mesin{io: io, simbol: map[string]int32{}, acak: acakBaru()}
	for _, b := range daftarFungsiBawaan() {
		m.definisikanGlobal(m.simbolUntuk(b.nama), b.fn, false)
	}
	return m
}

func (m *Mesin) simbolUntuk(nama string) int32 {
	if s, ada := m.simbol[nama]; ada {
		return s
	}
	s := int32(len(m.namaSimbol))
	m.simbol[nama] = s
	m.namaSimbol = append(m.namaSimbol, nama)
	return s
}

func (m *Mesin) pastikanGlobal(s int32) {
	for int(s) >= len(m.globalAda) {
		m.globalNilai = append(m.globalNilai, nil)
		m.globalAda = append(m.globalAda, false)
		m.globalTetap = append(m.globalTetap, false)
	}
}

func (m *Mesin) definisikanGlobal(s int32, v any, tetap bool) {
	m.pastikanGlobal(s)
	m.globalNilai[s] = v
	m.globalAda[s] = true
	if tetap {
		m.globalTetap[s] = true
	}
}

// ---- API ----

// Jalankan menjalankan kode sumber di lingkup global mesin ini.
func (m *Mesin) Jalankan(kode string) error {
	_, _, err := m.jalankanSumber(kode, false)
	return err
}

// JalankanREPL seperti Jalankan, tetapi juga mengembalikan nilai ekspresi terakhir (bila ada).
func (m *Mesin) JalankanREPL(kode string) (any, bool, error) {
	return m.jalankanSumber(kode, true)
}

// Parsel memeriksa sintaks kode tanpa menjalankannya.
func Parsel(kode string) *Kesalahan {
	tokens, err := Tokenisasi(kode)
	if err != nil {
		return err
	}
	_, err = Parse(tokens, kode)
	return err
}

func (m *Mesin) jalankanSumber(kode string, repl bool) (hasil any, ada bool, err error) {
	tokens, kErr := Tokenisasi(kode)
	if kErr != nil {
		return nil, false, kErr
	}
	program, kErr := Parse(tokens, kode)
	if kErr != nil {
		return nil, false, kErr
	}
	defer func() {
		if r := recover(); r != nil {
			switch e := r.(type) {
			case *Kesalahan:
				err = e
			case galatBerhenti:
				err = e
			default:
				err = &GalatInternal{fmt.Sprint(r)}
			}
			m.tumpukan = m.tumpukan[:0]
			m.bingkai = m.bingkai[:0]
			m.kedalaman = 0
		}
	}()
	m.hasil, m.adaHasil = nil, false
	m.jalankanKode(m.kompilasi(program, repl), nil)
	return m.hasil, m.adaHasil, nil
}

// jalankanKode menjalankan kode sampai selesai dan mengembalikan nilai kembaliannya.
func (m *Mesin) jalankanKode(kode *Kode, lingkup *Lingkup) any {
	f := m.bingkaiBaru()
	f.kode, f.lingkup, f.dasar, f.batas = kode, lingkup, len(m.tumpukan), true
	m.bingkai = append(m.bingkai, f)
	batas := len(m.bingkai) - 1
	for {
		hasil, err := m.cobaPutar()
		if err == nil {
			return hasil
		}
		if !m.tangani(err, batas) {
			panic(err)
		}
	}
}

func (m *Mesin) cobaPutar() (hasil any, err error) {
	defer func() {
		if r := recover(); r != nil {
			switch e := r.(type) {
			case *Kesalahan:
				err = e
			case galatBerhenti:
				err = e
			case galatPython: // seharusnya sudah diterjemahkan di tempat terjadinya
				err = kesalahanTanpaLokasi(KNilai, "Hasil perhitungan terlalu besar")
			default:
				panic(r)
			}
		}
	}()
	return m.putar(), nil
}

// tangani mencari penangan (coba/akhirnya) untuk kesalahan; false bila tidak ada sampai bingkai batas.
func (m *Mesin) tangani(err error, batas int) bool {
	for len(m.bingkai)-1 >= batas {
		f := m.bingkai[len(m.bingkai)-1]
		if n := len(f.penangan); n > 0 {
			p := f.penangan[n-1]
			f.penangan = f.penangan[:n-1]
			m.tumpukan = append(m.tumpukan[:p.tinggi], &galatTerbang{err})
			f.lingkup = p.lingkup
			f.ip = p.ip
			return true
		}
		m.lepasBingkai(f)
	}
	return false
}

func (m *Mesin) lepasBingkai(f *bingkai) {
	if f.hitung {
		m.kedalaman--
	}
	m.tumpukan = m.tumpukan[:f.dasar]
	m.bingkai[len(m.bingkai)-1] = nil
	m.bingkai = m.bingkai[:len(m.bingkai)-1]
	if l := f.daur; l != nil && len(m.cadanganL) < 256 {
		l.bersihkan()
		l.induk = nil
		m.cadanganL = append(m.cadanganL, l)
	}
	*f = bingkai{penangan: f.penangan[:0]}
	m.cadangan = append(m.cadangan, f)
}

// lingkupPanggilan: lingkup baru untuk memanggil fn, dari cadangan bila fungsi itu tanpa closure.
func (m *Mesin) lingkupPanggilan(fn *Fungsi, induk *Lingkup) *Lingkup {
	if fn.proto.daurUlang {
		if n := len(m.cadanganL); n > 0 {
			l := m.cadanganL[n-1]
			m.cadanganL = m.cadanganL[:n-1]
			l.induk = induk
			return l
		}
	}
	return lingkupBaru(induk)
}

func (m *Mesin) bingkaiBaru() *bingkai {
	if n := len(m.cadangan); n > 0 {
		f := m.cadangan[n-1]
		m.cadangan = m.cadangan[:n-1]
		return f
	}
	return &bingkai{}
}

func (m *Mesin) dorong(v any) { m.tumpukan = append(m.tumpukan, v) }

func (m *Mesin) ambilAtas() any {
	n := len(m.tumpukan) - 1
	v := m.tumpukan[n]
	m.tumpukan = m.tumpukan[:n]
	return v
}

func (m *Mesin) atas() any { return m.tumpukan[len(m.tumpukan)-1] }

func galatDi(jenis, pesan string, ins *instruksi) *Kesalahan {
	return kesalahan(jenis, pesan, int(ins.baris), int(ins.kolom))
}

func galatDiBaris(jenis, pesan string, ins *instruksi) *Kesalahan {
	return kesalahan(jenis, pesan, int(ins.baris), tanpaPosisi)
}

// ---- Variabel ----

func (m *Mesin) semuaNama(l *Lingkup) []string {
	ada := map[string]bool{}
	for ; l != nil; l = l.induk {
		for _, e := range l.isi {
			ada[m.namaSimbol[e.sym]] = true
		}
	}
	for s, a := range m.globalAda {
		if a {
			ada[m.namaSimbol[s]] = true
		}
	}
	return kunciUrut(ada)
}

func (m *Mesin) ambilVariabel(f *bingkai, s int32, ins *instruksi) any {
	for l := f.lingkup; l != nil; l = l.induk {
		for i := range l.isi {
			if l.isi[i].sym == s {
				return l.isi[i].nilai
			}
		}
	}
	if int(s) < len(m.globalAda) && m.globalAda[s] {
		return m.globalNilai[s]
	}
	nama := m.namaSimbol[s]
	panic(galatDi(KNama, "Variabel '"+nama+"' belum dideklarasikan."+saranNama(nama, m.semuaNama(f.lingkup)), ins))
}

func (m *Mesin) setelVariabel(f *bingkai, s int32, v any, ins *instruksi) {
	nama := func() string { return m.namaSimbol[s] }
	for l := f.lingkup; l != nil; l = l.induk {
		if i := l.cari(s); i >= 0 {
			if l.isi[i].tetap {
				panic(galatDi(KNama, "Tidak bisa mengubah konstanta '"+nama()+"'", ins))
			}
			l.isi[i].nilai = v
			return
		}
	}
	if int(s) < len(m.globalAda) && m.globalAda[s] {
		if m.globalTetap[s] {
			panic(galatDi(KNama, "Tidak bisa mengubah konstanta '"+nama()+"'", ins))
		}
		m.globalNilai[s] = v
		return
	}
	saran := saranNama(nama(), m.semuaNama(f.lingkup))
	if saran == "" {
		saran = " Untuk membuat variabel baru, tulis: buat " + nama() + " adalah ..."
	}
	panic(galatDi(KNama, "Variabel '"+nama()+"' belum dideklarasikan."+saran, ins))
}

func (m *Mesin) definisikan(f *bingkai, s int32, v any, tetap bool) {
	if f.lingkup != nil {
		f.lingkup.definisikan(s, v, tetap)
	} else {
		m.definisikanGlobal(s, v, tetap)
	}
}

// ---- Putaran utama ----

func (m *Mesin) putar() any {
	f := m.bingkai[len(m.bingkai)-1]
	for {
		ins := &f.kode.ins[f.ip]
		f.ip++
		m.langkah++
		if m.langkah&1023 == 0 && m.io.Berhenti != nil && m.io.Berhenti() {
			panic(ErrDihentikan)
		}
		switch ins.op {
		case opKonstanta:
			m.dorong(f.kode.konstanta[ins.a])
		case opKosong:
			m.dorong(nil)
		case opBenar:
			m.dorong(true)
		case opSalah:
			m.dorong(false)
		case opBuang:
			m.tumpukan = m.tumpukan[:len(m.tumpukan)-1]
		case opBuangN:
			m.tumpukan = m.tumpukan[:len(m.tumpukan)-int(ins.a)]
		case opSalin:
			m.dorong(m.atas())
		case opAmbil:
			m.dorong(m.ambilVariabel(f, ins.a, ins))
		case opDefinisikan:
			m.definisikan(f, ins.a, m.ambilAtas(), ins.b == 1)
		case opSetel:
			m.setelVariabel(f, ins.a, m.ambilAtas(), ins)
		case opLingkupMasuk:
			f.lingkup = lingkupBaru(f.lingkup)
		case opLingkupKeluar:
			f.lingkup = f.lingkup.induk
		case opLingkupBersihkan:
			f.lingkup.bersihkan()
		case opBiner:
			b := m.ambilAtas()
			a := m.ambilAtas()
			m.dorong(m.hitungBiner(int(ins.a), a, b, ins))
		case opBukan:
			m.dorong(!benarkah(m.ambilAtas()))
		case opNegasi:
			m.dorong(negasi(m.ambilAtas(), ins))
		case opLompat:
			f.ip = int(ins.a)
		case opLompatSalah:
			if !benarkah(m.ambilAtas()) {
				f.ip = int(ins.a)
			}
		case opLompatSalahAtauBuang:
			if !benarkah(m.atas()) {
				f.ip = int(ins.a)
			} else {
				m.tumpukan = m.tumpukan[:len(m.tumpukan)-1]
			}
		case opLompatBenarAtauBuang:
			if benarkah(m.atas()) {
				f.ip = int(ins.a)
			} else {
				m.tumpukan = m.tumpukan[:len(m.tumpukan)-1]
			}
		case opPanggil:
			m.panggil(f, ins)
			f = m.bingkai[len(m.bingkai)-1]
		case opKembalikan:
			hasil := m.ambilAtas()
			if f.instansi != nil {
				hasil = f.instansi
			}
			batas := f.batas
			m.lepasBingkai(f)
			if batas {
				return hasil
			}
			m.dorong(hasil)
			f = m.bingkai[len(m.bingkai)-1]
		case opDaftar:
			n := int(ins.a)
			elemen := make([]any, n)
			copy(elemen, m.tumpukan[len(m.tumpukan)-n:])
			m.tumpukan = m.tumpukan[:len(m.tumpukan)-n]
			m.dorong(&Daftar{elemen})
		case opKamus:
			n := int(ins.a)
			k := kamusBaru()
			isi := m.tumpukan[len(m.tumpukan)-2*n:]
			for i := 0; i < n; i++ {
				k.Setel(isi[2*i], isi[2*i+1])
			}
			m.tumpukan = m.tumpukan[:len(m.tumpukan)-2*n]
			m.dorong(k)
		case opAmbilIndeks:
			idx := m.ambilAtas()
			obj := m.ambilAtas()
			m.dorong(ambilIndeks(obj, idx, ins))
		case opSetelIndeks:
			idx := m.ambilAtas()
			obj := m.ambilAtas()
			setelIndeks(obj, idx, m.ambilAtas(), ins)
		case opIrisan:
			m.irisan(ins)
		case opAmbilAtribut:
			obj := m.ambilAtas()
			m.dorong(m.ambilAtribut(f, obj, f.kode.konstanta[ins.a].(string), ins))
		case opSetelAtribut:
			obj := m.ambilAtas()
			nilai := m.ambilAtas()
			inst, ok := obj.(*Instansi)
			if !ok {
				panic(galatDiBaris(KTipe, "Tidak bisa menyetel atribut pada tipe ini", ins))
			}
			inst.Atribut.Setel(f.kode.konstanta[ins.a].(string), nilai)
		case opTampilkan:
			m.tampilkan(int(ins.a), ins.b == 1)
		case opTunggu:
			lama := m.ambilAtas()
			faktor := f.kode.konstanta[ins.a].(float64)
			m.lindungi(ins, func() any { m.tungguDetik(lama, faktor); return nil })
		case opWaktu:
			m.dorong(m.bacaWaktu(f.kode.konstanta[ins.a].(string)))
		case opAcak:
			maks := m.ambilAtas()
			minimum := m.ambilAtas()
			m.dorong(m.lindungi(ins, func() any { return m.bilanganAcak(minimum, maks) }))
		case opTanya:
			pertanyaan := m.ambilAtas()
			jenis := "teks"
			if ins.a == 1 {
				jenis = "angka"
			}
			m.dorong(m.lindungi(ins, func() any { return m.tanya(pertanyaan, jenis) }))
		case opKeTeks:
			m.tumpukan[len(m.tumpukan)-1] = keTeks(m.atas())
		case opGabungTeks:
			n := int(ins.a)
			var b strings.Builder
			for _, v := range m.tumpukan[len(m.tumpukan)-n:] {
				b.WriteString(v.(string))
			}
			m.tumpukan = m.tumpukan[:len(m.tumpukan)-n]
			m.dorong(b.String())
		case opGalat:
			panic(f.kode.konstanta[ins.a].(*Kesalahan))
		case opFungsi:
			proto := f.kode.konstanta[ins.a].(*KodeFungsi)
			m.dorong(&Fungsi{Nama: proto.Nama, proto: proto, lingkup: f.lingkup})
		case opKelas:
			m.dorong(m.buatKelas(f.kode.konstanta[ins.a].(*KodeKelas), ins))
		case opImpor:
			alias := ""
			if ins.b >= 0 {
				alias = f.kode.konstanta[ins.b].(string)
			}
			m.impor(f, f.kode.konstanta[ins.a].(string), alias, ins)
		case opDariImpor:
			d := f.kode.konstanta[ins.a].([3]string)
			modul := m.muatModul(d[0], ins)
			nama := d[2]
			if nama == "" {
				nama = d[1]
			}
			m.definisikan(f, m.simbolUntuk(nama), isiModul(modul, d[1], ins), false)
		case opKonversi:
			m.dorong(konversiTipe(m.ambilAtas(), f.kode.konstanta[ins.a].(string), ins))
		case opTambahkan:
			wadah := m.ambilAtas()
			nilai := m.ambilAtas()
			switch w := wadah.(type) {
			case *Daftar:
				w.Elemen = append(w.Elemen, nilai)
				f.ip = int(ins.a)
			case *Kamus:
				panic(galatDi(KTipe, "Tidak bisa 'tambahkan' ke kamus. Gunakan kamus[kunci] = nilai", ins))
			default:
				m.dorong(m.hitungBiner(biTambah, wadah, nilai, ins))
			}
		case opUntukSiapkan:
			n := len(m.tumpukan)
			for i, bagian := range []string{"dari", "sampai", "langkah"} {
				if v := m.tumpukan[n-3+i]; !adalahAngkaMurni(v) {
					panic(galatDi(KTipe, "Nilai '"+bagian+"' pada perulangan 'untuk' harus angka, bukan '"+keTeks(v)+"'", ins))
				}
			}
		case opUntukCek:
			n := len(m.tumpukan)
			i, sampai, langkah := m.tumpukan[n-3], m.tumpukan[n-2], m.tumpukan[n-1]
			arah := bandingAngka(langkah, 0)
			c := bandingAngka(i, sampai)
			if !((arah == 1 && (c == -1 || c == 0)) || (arah == -1 && (c == 1 || c == 0))) {
				f.ip = int(ins.a)
			}
		case opUntukNilai:
			m.dorong(m.tumpukan[len(m.tumpukan)-3])
		case opUntukLangkah:
			n := len(m.tumpukan)
			m.tumpukan[n-3] = m.hitungBiner(biTambah, m.tumpukan[n-3], m.tumpukan[n-1], ins)
		case opIterBuat:
			m.dorong(buatIterator(m.ambilAtas(), ins))
		case opIterLanjut:
			it := m.atas().(*iterator)
			if it.daftar != nil {
				if it.i >= len(it.daftar.Elemen) {
					f.ip = int(ins.a)
					continue
				}
				m.dorong(it.daftar.Elemen[it.i])
			} else {
				if it.i >= len(it.isi) {
					f.ip = int(ins.a)
					continue
				}
				m.dorong(it.isi[it.i])
			}
			it.i++
		case opKaliSiapkan:
			m.dorong(jumlahPerulangan(m.ambilAtas(), ins))
		case opKaliLanjut:
			n := len(m.tumpukan) - 1
			sisa := m.tumpukan[n]
			if bandingAngka(sisa, 0) != 1 {
				f.ip = int(ins.a)
				continue
			}
			m.tumpukan[n] = kurangBulat(sisa, 1)
		case opCobaMulai:
			f.penangan = append(f.penangan, penangan{int(ins.a), len(m.tumpukan), f.lingkup})
		case opCobaSelesai:
			f.penangan = f.penangan[:len(f.penangan)-1]
		case opCocokTangkap:
			gt := m.atas().(*galatTerbang)
			k, ok := gt.err.(*Kesalahan)
			if !ok || (ins.a >= 0 && !cocokTangkap(k.Jenis, f.kode.konstanta[ins.a].(string))) {
				f.ip = int(ins.b)
			}
		case opTeksKesalahan:
			k := m.ambilAtas().(*galatTerbang).err.(*Kesalahan)
			pesan := k.Pesan
			if pesan == "" {
				pesan = k.Teks()
			}
			m.dorong(&TeksKesalahan{Teks: pesan, Jenis: k.Jenis})
		case opLemparUlang:
			panic(m.ambilAtas().(*galatTerbang).err)
		case opLempar:
			v := m.ambilAtas()
			pesan, ok := teksDari(v)
			if !ok {
				pesan = keTeks(v)
			}
			panic(galatDi(KNilai, pesan, ins))
		case opSimpanHasil:
			m.hasil, m.adaHasil = m.ambilAtas(), true
		default:
			panic(fmt.Sprintf("instruksi tidak dikenal: %d", ins.op))
		}
	}
}

// ---- Pemanggilan ----

func (m *Mesin) panggil(f *bingkai, ins *instruksi) {
	argc := int(ins.a)
	n := len(m.tumpukan)
	callee := m.tumpukan[n-argc-1]
	args := m.tumpukan[n-argc : n]
	switch c := callee.(type) {
	case *Fungsi:
		lingkup := m.lingkupPanggilan(c, c.lingkup)
		m.ikatParameter(c, args, lingkup, false, ins)
		m.tumpukan = m.tumpukan[:n-argc-1]
		m.mulaiFungsi(c, lingkup, nil, ins)
	case *MetodeTerikat:
		lingkup := m.lingkupMetode(c)
		m.ikatParameter(c.Fungsi, args, lingkup, true, ins)
		m.tumpukan = m.tumpukan[:n-argc-1]
		m.mulaiFungsi(c.Fungsi, lingkup, nil, ins)
	case *Kelas:
		inst := &Instansi{Kelas: c, Atribut: c.Atribut.salin()}
		if c.Induk != nil {
			for i, k := range c.Induk.Atribut.kunci {
				if !inst.Atribut.Ada(k) {
					inst.Atribut.Setel(k, c.Induk.Atribut.nilai[i])
				}
			}
		}
		init := c.cariMetode("inisialisasi")
		if init == nil {
			if argc > 0 {
				panic(galatDi(KTipe, "Kelas '"+c.Nama+"' tidak punya fungsi 'inisialisasi', jadi tidak menerima argumen", ins))
			}
			m.tumpukan = append(m.tumpukan[:n-argc-1], inst)
			return
		}
		metode := &MetodeTerikat{inst, init}
		lingkup := m.lingkupMetode(metode)
		m.ikatParameter(init, args, lingkup, true, ins)
		m.tumpukan = m.tumpukan[:n-argc-1]
		m.mulaiFungsi(init, lingkup, inst, ins)
	case *FungsiBawaan:
		nama := f.kode.konstanta[ins.b].(string)
		if argc < c.min || (c.max >= 0 && argc > c.max) {
			panic(galatDi(KTipe, "'"+nama+"' dipanggil dengan argumen yang tidak sesuai", ins))
		}
		salinan := append([]any(nil), args...)
		hasil := m.panggilBawaan(c, salinan, nama, ins)
		m.tumpukan = append(m.tumpukan[:n-argc-1], hasil)
	default:
		panic(galatDi(KTipe, "'"+keTeks(callee)+"' bukan fungsi dan tidak bisa dipanggil", ins))
	}
}

func (m *Mesin) lingkupMetode(metode *MetodeTerikat) *Lingkup {
	lingkup := m.lingkupPanggilan(metode.Fungsi, metode.Fungsi.lingkup)
	lingkup.definisikan(m.simbolUntuk("diri"), metode.Instansi, false)
	if k := metode.Fungsi.Kelas; k != nil && k.Induk != nil {
		induk := &Induk{metode.Instansi, k.Induk}
		lingkup.definisikan(m.simbolUntuk("induk"), induk, false)
		lingkup.definisikan(m.simbolUntuk("super"), induk, false)
	}
	return lingkup
}

// ikatParameter sama dengan _ikat_parameter(); pada metode, parameter 'diri' dilewati.
func (m *Mesin) ikatParameter(fn *Fungsi, args []any, lingkup *Lingkup, metode bool, ins *instruksi) {
	proto := fn.proto
	var urut []int
	for i, nama := range proto.Parameter {
		if !(metode && nama == "diri") {
			urut = append(urut, i)
		}
	}
	if len(args) > len(urut) {
		panic(galatDi(KTipe, fmt.Sprintf("Fungsi '%s' menerima %d argumen, tetapi diberi %d", fn.Nama, len(urut), len(args)), ins))
	}
	for j, i := range urut {
		switch {
		case j < len(args):
			lingkup.definisikan(proto.simbol[i], args[j], false)
		case proto.Bawaan[i] != nil:
			lingkup.definisikan(proto.simbol[i], m.jalankanKode(proto.Bawaan[i], fn.lingkup), false)
		default:
			panic(galatDi(KNilai, "Fungsi '"+fn.Nama+"' membutuhkan parameter '"+proto.Parameter[i]+"'", ins))
		}
	}
}

func (m *Mesin) mulaiFungsi(fn *Fungsi, lingkup *Lingkup, inst *Instansi, ins *instruksi) {
	if m.kedalaman >= BatasRekursi {
		panic(galatDi(KTumpukan, fmt.Sprintf("Fungsi '%s' dipanggil bertumpuk lebih dari 3.000 kali. "+
			"Mungkin fungsi ini terus memanggil dirinya sendiri tanpa berhenti; "+
			"pastikan ada kondisi untuk berhenti.", fn.Nama), ins))
	}
	m.kedalaman++
	f := m.bingkaiBaru()
	f.kode, f.lingkup, f.dasar, f.instansi, f.hitung = fn.proto.Kode, lingkup, len(m.tumpukan), inst, true
	if fn.proto.daurUlang {
		f.daur = lingkup
	}
	m.bingkai = append(m.bingkai, f)
}

// panggilBawaan menjalankan fungsi bawaan dan menerjemahkan kesalahannya, seperti _eval_panggil().
func (m *Mesin) panggilBawaan(fb *FungsiBawaan, args []any, nama string, ins *instruksi) (hasil any) {
	defer func() {
		if r := recover(); r != nil {
			switch e := r.(type) {
			case *Kesalahan:
				panic(e.denganLokasi(int(ins.baris), int(ins.kolom)))
			case galatPython:
				if e.jenis == "TypeError" {
					panic(galatDi(KTipe, "'"+nama+"' dipanggil dengan argumen yang tidak sesuai", ins))
				}
				panic(galatDi(KNilai, "'"+nama+"' tidak bisa menghitung dengan nilai ini", ins))
			default:
				panic(r)
			}
		}
	}()
	return fb.fn(m, args)
}

// lindungi: kesalahan tanpa lokasi mendapat lokasi instruksi ini (_dengan_lokasi).
func (m *Mesin) lindungi(ins *instruksi, f func() any) (hasil any) {
	defer func() {
		if r := recover(); r != nil {
			switch e := r.(type) {
			case *Kesalahan:
				panic(e.denganLokasi(int(ins.baris), int(ins.kolom)))
			case galatPython:
				panic(galatDi(KNilai, "Hasil perhitungan terlalu besar", ins))
			}
			panic(r)
		}
	}()
	return f()
}

func (m *Mesin) buatKelas(desk *KodeKelas, ins *instruksi) *Kelas {
	n := len(desk.Anggota)
	isi := m.tumpukan[len(m.tumpukan)-n:]
	kelas := &Kelas{Nama: desk.Nama, Metode: map[string]*Fungsi{}, Atribut: kamusBaru()}
	for i, a := range desk.Anggota {
		if a.metode {
			fn := isi[i].(*Fungsi)
			fn.Kelas = kelas
			kelas.Metode[a.nama] = fn
		} else {
			kelas.Atribut.Setel(a.nama, isi[i])
		}
	}
	m.tumpukan = m.tumpukan[:len(m.tumpukan)-n]
	if desk.AdaInduk {
		induk, ok := m.ambilAtas().(*Kelas)
		if !ok {
			panic(galatDi(KTipe, "Kelas induk dari '"+desk.Nama+"' harus berupa kelas", ins))
		}
		kelas.Induk = induk
	}
	return kelas
}

// ---- Operasi ----

func negasi(v any, ins *instruksi) any {
	switch x := v.(type) {
	case int:
		if x == math.MinInt64 {
			return normalBulat(new(big.Int).Neg(big.NewInt(int64(x))))
		}
		return -x
	case *big.Int:
		return normalBulat(new(big.Int).Neg(x))
	case float64:
		return -x
	}
	panic(galatDi(KTipe, "Tanda minus hanya untuk angka, bukan '"+keTeks(v)+"'", ins))
}

// hitungBiner sama dengan _hitung_biner(). Jalur cepat untuk dua bilangan bulat 64 bit atau dua
// desimal; kasus lain (bilangan besar, teks, kesalahan) lewat hitungBinerUmum.
func (m *Mesin) hitungBiner(op int, kiri, kanan any, ins *instruksi) any {
	switch a := kiri.(type) {
	case int:
		b, ok := kanan.(int)
		if !ok {
			break
		}
		switch op {
		case biTambah:
			if s := a + b; (s > a) == (b > 0) {
				return s
			}
		case biKurang:
			if s := a - b; (s < a) == (b > 0) {
				return s
			}
		case biKali:
			return kaliBulat(a, b)
		case biSisa:
			if b != 0 && b != -1 {
				r := a % b
				if r != 0 && (r < 0) != (b < 0) {
					r += b
				}
				return r
			}
		case biBagi:
			if b != 0 && a <= 1<<53 && a >= -(1<<53) && b <= 1<<53 && b >= -(1<<53) {
				return float64(a) / float64(b)
			}
		case biSama:
			return a == b
		case biTidakSama:
			return a != b
		case biLebih:
			return a > b
		case biKurangDari:
			return a < b
		case biLebihSama:
			return a >= b
		case biKurangSama:
			return a <= b
		}
	case float64:
		b, ok := kanan.(float64)
		if !ok {
			break
		}
		switch op {
		case biTambah:
			return a + b
		case biKurang:
			return a - b
		case biKali:
			return a * b
		case biBagi:
			if b != 0 {
				return a / b
			}
		case biSama:
			return a == b
		case biTidakSama:
			return a != b
		case biLebih:
			return a > b
		case biKurangDari:
			return a < b
		case biLebihSama:
			return a >= b
		case biKurangSama:
			return a <= b
		}
	}
	return m.hitungBinerUmum(op, kiri, kanan, ins)
}

func (m *Mesin) hitungBinerUmum(op int, kiri, kanan any, ins *instruksi) (hasil any) {
	defer func() {
		if r := recover(); r != nil {
			if g, ok := r.(galatPython); ok {
				switch g.jenis {
				case "TypeError":
					panic(galatTipeBiner(op, kiri, kanan, ins))
				case "ZeroDivisionError":
					panic(galatDi(KBagiNol, "Tidak bisa membagi dengan nol", ins))
				case "complex":
					panic(galatDi(KNilai, "Pangkat pecahan dari bilangan negatif tidak bisa dihitung", ins))
				default:
					panic(galatDi(KNilai, "Hasil perhitungan terlalu besar", ins))
				}
			}
			panic(r)
		}
	}()
	switch op {
	case biAdaDalam, biTidakAdaDalam:
		ada := adaDalam(kiri, kanan, op, ins)
		return ada == (op == biAdaDalam)
	case biTambah:
		sa, aTeks := teksDari(kiri)
		sb, bTeks := teksDari(kanan)
		if aTeks && bTeks {
			return sa + sb
		}
		if aTeks || bTeks {
			return keTeks(kiri) + keTeks(kanan)
		}
		return tambahAngka(kiri, kanan)
	case biKurang:
		if adalahBulat(kiri) && adalahBulat(kanan) {
			return kurangBulat(kiri, kanan)
		}
		return opFloat(kiri, kanan, func(a, b float64) float64 { return a - b })
	case biKali:
		if s, ok := teksDari(kiri); ok && adalahBulat(kanan) {
			return ulangiTeks(s, kanan)
		}
		if s, ok := teksDari(kanan); ok && adalahBulat(kiri) {
			return ulangiTeks(s, kiri)
		}
		if adalahBulat(kiri) && adalahBulat(kanan) {
			return kaliBulat(kiri, kanan)
		}
		return opFloat(kiri, kanan, func(a, b float64) float64 { return a * b })
	case biBagi:
		if samaDengan(kanan, 0) {
			panic(galatDi(KBagiNol, "Tidak bisa membagi dengan nol", ins))
		}
		if !adalahAngkaNilai(kiri) || !adalahAngkaNilai(kanan) {
			panic(galatPython{"TypeError"})
		}
		return bagiBenar(kiri, kanan)
	case biSisa:
		if _, ok := teksDari(kiri); ok {
			panic(galatPython{"TypeError"})
		}
		if samaDengan(kanan, 0) {
			panic(galatDi(KBagiNol, "Tidak bisa membagi dengan nol", ins))
		}
		if adalahBulat(kiri) && adalahBulat(kanan) {
			return modBulat(kiri, kanan)
		}
		return opFloat(kiri, kanan, modFloat)
	case biPangkat:
		if !adalahAngkaNilai(kiri) || !adalahAngkaNilai(kanan) {
			panic(galatPython{"TypeError"})
		}
		return pangkat(kiri, kanan)
	case biSama:
		return samaDengan(kiri, kanan)
	case biTidakSama:
		return !samaDengan(kiri, kanan)
	}
	c, ok := banding(kiri, kanan)
	if !ok {
		panic(galatPython{"TypeError"})
	}
	switch op {
	case biLebih:
		return c == 1
	case biKurangDari:
		return c == -1
	case biLebihSama:
		return c == 1 || c == 0
	default:
		return c == -1 || c == 0
	}
}

func galatTipeBiner(op int, kiri, kanan any, ins *instruksi) *Kesalahan {
	return galatDi(KTipe, "Tipe data tidak cocok untuk operasi '"+namaOperator[op]+"': "+keTeks(kiri)+" dan "+keTeks(kanan), ins)
}

func tambahAngka(a, b any) any {
	if adalahBulat(a) && adalahBulat(b) {
		return tambahBulat(a, b)
	}
	return opFloat(a, b, func(x, y float64) float64 { return x + y })
}

func opFloat(a, b any, f func(x, y float64) float64) any {
	if !adalahAngkaNilai(a) || !adalahAngkaNilai(b) {
		panic(galatPython{"TypeError"})
	}
	x, _ := keFloat(a)
	y, _ := keFloat(b)
	return f(x, y)
}

func ulangiTeks(s string, n any) any {
	kali, ok := bulatKeInt(n)
	if !ok {
		panic(galatPython{"OverflowError"})
	}
	if kali <= 0 || s == "" {
		return ""
	}
	if len(s)*kali > 1<<28 || kali > 1<<28 {
		panic(galatPython{"MemoryError"})
	}
	return strings.Repeat(s, kali)
}

func adaDalam(kiri, kanan any, op int, ins *instruksi) bool {
	switch w := kanan.(type) {
	case *Daftar:
		for _, e := range w.Elemen {
			if samaDengan(e, kiri) {
				return true
			}
		}
		return false
	case *Kamus:
		return w.Ada(kiri)
	}
	if s, ok := teksDari(kanan); ok {
		bagian, ok := teksDari(kiri)
		if !ok {
			panic(galatPython{"TypeError"})
		}
		return strings.Contains(s, bagian)
	}
	panic(galatDiBaris(KTipe, "Operasi '"+namaOperator[op]+"' membutuhkan daftar, kamus, atau teks", ins))
}

// indeksPython: indeks bulat (boleh negatif) → posisi dalam panjang n; false bila di luar batas.
func indeksPython(idx any, n int) (int, bool) {
	i, ok := bulatKeInt(idx)
	if !ok {
		return 0, false // *big.Int: pasti di luar batas
	}
	if i < 0 {
		i += n
	}
	return i, i >= 0 && i < n
}

func ambilIndeks(obj, idx any, ins *instruksi) any {
	switch o := obj.(type) {
	case *Daftar:
		if !adalahBulat(idx) {
			panic(galatDi(KTipe, "Indeks daftar harus berupa bilangan bulat, bukan '"+keTeks(idx)+"'", ins))
		}
		i, ok := indeksPython(idx, len(o.Elemen))
		if !ok {
			panic(galatDi(KIndeks, "Indeks "+reprNilai(idx)+" di luar batas daftar", ins))
		}
		return o.Elemen[i]
	case *Kamus:
		if v, ada := o.Ambil(idx); ada {
			return v
		}
		panic(galatDi(KKunci, "Kunci '"+keTeks(idx)+"' tidak ditemukan", ins))
	}
	if s, ok := teksDari(obj); ok {
		if !adalahBulat(idx) {
			panic(galatDi(KTipe, "Indeks teks harus berupa bilangan bulat, bukan '"+keTeks(idx)+"'", ins))
		}
		r := []rune(s)
		i, ok := indeksPython(idx, len(r))
		if !ok {
			panic(galatDi(KIndeks, "Indeks "+reprNilai(idx)+" di luar batas daftar", ins))
		}
		return string(r[i])
	}
	panic(galatDiBaris(KTipe, "Tidak bisa mengambil isi dengan indeks dari "+jenisNilai(obj), ins))
}

func setelIndeks(obj, idx, nilai any, ins *instruksi) {
	switch o := obj.(type) {
	case *Daftar:
		if !adalahBulat(idx) {
			panic(galatDi(KTipe, "Indeks daftar harus berupa bilangan bulat, bukan '"+keTeks(idx)+"'", ins))
		}
		i, ok := indeksPython(idx, len(o.Elemen))
		if !ok {
			panic(galatDi(KIndeks, "Indeks "+reprNilai(idx)+" di luar batas daftar", ins))
		}
		o.Elemen[i] = nilai
	case *Kamus:
		o.Setel(idx, nilai)
	default:
		panic(galatDiBaris(KTipe, "Tidak bisa mengakses indeks pada tipe ini", ins))
	}
}

// batasIrisan menghitung [awal:akhir] seperti Python (boleh negatif, dipangkas ke batas).
func batasIrisan(awal, akhir any, n int) (int, int) {
	pangkas := func(v any, bawaan int) int {
		if v == nil {
			return bawaan
		}
		i, ok := bulatKeInt(v)
		if !ok { // *big.Int
			if keBig(v).Sign() < 0 {
				return 0
			}
			return n
		}
		if i < 0 {
			i += n
			if i < 0 {
				i = 0
			}
		}
		if i > n {
			i = n
		}
		return i
	}
	a, b := pangkas(awal, 0), pangkas(akhir, n)
	if b < a {
		b = a
	}
	return a, b
}

func (m *Mesin) irisan(ins *instruksi) {
	var awal, akhir any
	if ins.a&2 != 0 {
		akhir = m.ambilAtas()
	}
	if ins.a&1 != 0 {
		awal = m.ambilAtas()
	}
	obj := m.ambilAtas()
	for _, b := range []any{awal, akhir} {
		if b != nil {
			if _, isBool := b.(bool); isBool || !adalahBulat(b) {
				panic(galatDi(KTipe, "Batas irisan harus bilangan bulat, bukan '"+keTeks(b)+"'", ins))
			}
		}
	}
	switch o := obj.(type) {
	case *Daftar:
		a, b := batasIrisan(awal, akhir, len(o.Elemen))
		m.dorong(&Daftar{append([]any(nil), o.Elemen[a:b]...)})
		return
	}
	if s, ok := teksDari(obj); ok {
		r := []rune(s)
		a, b := batasIrisan(awal, akhir, len(r))
		m.dorong(string(r[a:b]))
		return
	}
	panic(galatDiBaris(KTipe, "Irisan hanya bisa dilakukan pada daftar atau teks", ins))
}

func (m *Mesin) ambilAtribut(f *bingkai, obj any, nama string, ins *instruksi) any {
	switch o := obj.(type) {
	case *Instansi:
		if v, ada := o.Atribut.Ambil(nama); ada {
			return v
		}
		if fn := o.Kelas.cariMetode(nama); fn != nil {
			return &MetodeTerikat{o, fn}
		}
		kandidat := map[string]bool{}
		for _, k := range o.Atribut.kunci {
			if s, ok := k.(string); ok {
				kandidat[s] = true
			}
		}
		for kl := o.Kelas; kl != nil; kl = kl.Induk {
			for nm := range kl.Metode {
				kandidat[nm] = true
			}
		}
		panic(galatDi(KNama, "Atribut '"+nama+"' tidak ditemukan pada "+o.Kelas.Nama+"."+saranNama(nama, kunciUrut(kandidat)), ins))
	case *Induk:
		if fn := o.Kelas.cariMetode(nama); fn != nil {
			return &MetodeTerikat{o.Instansi, fn}
		}
		panic(galatDiBaris(KNama, "Kelas induk "+o.Kelas.Nama+" tidak memiliki metode '"+nama+"'", ins))
	case *Modul:
		return isiModul(o, nama, ins)
	case *TeksKesalahan:
		switch nama {
		case "pesan":
			return o.Teks
		case "jenis":
			return o.Jenis
		}
	}
	switch obj.(type) {
	case *Daftar, *Kamus, string, *TeksKesalahan:
		fb, semua := ambilMetode(obj, nama)
		if fb != nil {
			return fb
		}
		jenis := jenisNilai(obj)
		panic(galatDi(KNama, strings.ToUpper(jenis[:1])+jenis[1:]+" tidak memiliki metode '"+nama+"'."+saranNama(nama, semua), ins))
	}
	panic(galatDiBaris(KTipe, "Tidak bisa mengakses atribut '"+nama+"' pada "+jenisNilai(obj), ins))
}

func (m *Mesin) tampilkan(n int, barisBaru bool) {
	var b strings.Builder
	for i, v := range m.tumpukan[len(m.tumpukan)-n:] {
		if i > 0 {
			b.WriteByte(' ')
		}
		tulisTeks(&b, v, 0)
	}
	m.tumpukan = m.tumpukan[:len(m.tumpukan)-n]
	if barisBaru {
		b.WriteByte('\n')
	}
	m.io.Tulis(b.String())
}

func konversiTipe(v any, tipe string, ins *instruksi) any {
	gagal := func() any { panic(galatDi(KTipe, "Tidak bisa mengubah nilai ke tipe '"+tipe+"'", ins)) }
	switch tipe {
	case "bilangan":
		switch x := v.(type) {
		case int, *big.Int:
			return x
		case bool:
			n, _ := bulatKeInt(x)
			return n
		case float64:
			if math.IsNaN(x) || math.IsInf(x, 0) {
				return gagal()
			}
			b, _ := new(big.Float).SetFloat64(math.Trunc(x)).Int(nil)
			return normalBulat(b)
		}
		if s, ok := teksDari(v); ok {
			if n, ok := intDariTeks(s); ok {
				return n
			}
		}
		return gagal()
	case "desimal":
		if adalahAngkaNilai(v) {
			f, _ := keFloat(v)
			return f
		}
		if s, ok := teksDari(v); ok {
			if f, ok := floatDariTeks(s); ok {
				return f
			}
		}
		return gagal()
	case "teks":
		return keTeks(v)
	case "logika":
		return benarkah(v)
	}
	return v
}

func buatIterator(v any, ins *instruksi) *iterator {
	switch x := v.(type) {
	case *Daftar:
		return &iterator{daftar: x}
	case *Kamus:
		return &iterator{isi: append([]any(nil), x.kunci...)}
	}
	if s, ok := teksDari(v); ok {
		var isi []any
		for _, r := range s {
			isi = append(isi, string(r))
		}
		return &iterator{isi: isi}
	}
	panic(galatDi(KTipe, "'untuk setiap' hanya bisa menelusuri daftar, kamus, atau teks, bukan '"+keTeks(v)+"'", ins))
}

func jumlahPerulangan(v any, ins *instruksi) any {
	if f, ok := v.(float64); ok && f == math.Trunc(f) && !math.IsInf(f, 0) {
		b, _ := new(big.Float).SetFloat64(f).Int(nil)
		v = normalBulat(b) // hasil pembagian seperti 6 / 2 tetap boleh
	}
	switch v.(type) {
	case int, *big.Int:
		return v
	}
	panic(galatDi(KTipe, "Jumlah perulangan harus bilangan bulat, bukan '"+keTeks(v)+"'", ins))
}
