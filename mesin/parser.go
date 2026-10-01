package mesin

import (
	"sort"
	"strings"
	"unicode"
)

// Parser recursive descent; sama dengan src/parser.py, termasuk pesan kesalahannya.
type parser struct {
	tokens          []Token
	pos             int
	daftarBaris     []string
	dalamPerulangan int // berhenti/lewati hanya boleh di dalam perulangan
	dalamFungsi     int // kembalikan hanya boleh di dalam fungsi
	kedalaman       int // sarang ekspresi & blok yang sedang dibaca
}

// batasSarang: batas aturan tata bahasa yang sedang bersarang (satu tingkat kurung memakai
// beberapa aturan, jadi ±1.000 tingkat kurung). Interpreter Python sudah gagal di sekitar 80
// tingkat kurung; batas ini menjaga tumpukan Go (juga di WebAssembly) agar tidak habis.
const batasSarang = 4000

func (p *parser) masuk() {
	p.kedalaman++
	if p.kedalaman > batasSarang {
		panic(kesalahanTanpaLokasi(KTumpukan,
			"Program bertumpuk terlalu dalam (mis. ekspresi atau rekursi yang sangat bersarang)"))
	}
}

func (p *parser) keluar() { p.kedalaman-- }

// Parse mengubah token menjadi AST. Kesalahan sintaks dikembalikan sebagai *Kesalahan.
func Parse(tokens []Token, kode string) (program *NodeProgram, err *Kesalahan) {
	defer tangkapKesalahan(&err)
	p := &parser{tokens: tokens}
	if kode != "" {
		p.daftarBaris = strings.Split(kode, "\n")
	}
	return p.parse(), nil
}

// parseEkspresiTunggal untuk isi {...} pada teks format.
func parseEkspresiTunggal(tokens []Token, kode string) (n Node, err *Kesalahan) {
	defer tangkapKesalahan(&err)
	p := &parser{tokens: tokens, daftarBaris: strings.Split(kode, "\n")}
	p.lewatiBarisBaru()
	n = p.parseEkspresi()
	p.lewatiBarisBaru()
	if !p.periksa(EOF) {
		p.galat("Isi {...} pada teks format harus berupa satu nilai atau perhitungan, "+
			"tetapi masih ada "+jelaskanToken(p.saatIni()), p.pos)
	}
	return n, nil
}

// ---- Helper ----

func (p *parser) saatIni() Token { return p.tokens[p.pos] }

func (p *parser) intip(offset int) Token {
	return p.tokens[min(p.pos+offset, len(p.tokens)-1)]
}

func (p *parser) periksa(tipe ...TipeToken) bool {
	t := p.saatIni().Tipe
	for _, x := range tipe {
		if t == x {
			return true
		}
	}
	return false
}

func (p *parser) periksaKata(kata ...string) bool {
	tok := p.saatIni()
	if tok.Tipe != IDENTIFIER {
		return false
	}
	for _, k := range kata {
		if tok.Nilai == k {
			return true
		}
	}
	return false
}

func (p *parser) cocok(tipe ...TipeToken) bool {
	if p.periksa(tipe...) {
		p.maju()
		return true
	}
	return false
}

// maju mengembalikan indeks token saat ini, lalu maju (tidak melewati token terakhir).
func (p *parser) maju() int {
	i := p.pos
	if p.pos < len(p.tokens)-1 {
		p.pos++
	}
	return i
}

func (p *parser) majuToken() Token { return p.tokens[p.maju()] }

func adalahPengenal(s string) bool {
	if s == "" {
		return false
	}
	for i, r := range s {
		if r == '_' || unicode.IsLetter(r) || (i > 0 && unicode.IsNumber(r)) {
			continue
		}
		return false
	}
	return true
}

func (p *parser) harapkan(tipe TipeToken, pesan string) Token {
	if p.periksa(tipe) {
		return p.majuToken()
	}
	tok := p.saatIni()
	if pesan == "" && tipe == IDENTIFIER && tipeKataKunci[tok.Tipe] && adalahPengenal(tok.teksNilai()) {
		pesan = "'" + tok.teksNilai() + "' adalah kata kunci, jadi tidak bisa dipakai sebagai nama. " +
			"Coba nama lain, misalnya '" + tok.teksNilai() + "_saya'."
	}
	if pesan == "" {
		pesan = "Diharapkan " + jelaskanTipe(tipe) + ", tetapi yang ditemukan " + jelaskanToken(tok)
	}
	p.galat(pesan, p.pos)
	return Token{}
}

func (p *parser) lewatiBarisBaru() {
	for p.periksa(BARIS_BARU) {
		p.maju()
	}
}

// galat melempar KesalahanSintaks pada token berindeks idx.
func (p *parser) galat(pesan string, idx int) {
	tok := p.tokens[idx]
	barisKode := ""
	if tok.Baris-1 < len(p.daftarBaris) {
		barisKode = p.daftarBaris[tok.Baris-1]
	}
	sisa := []Token{tok}
	if idx == p.pos {
		sisa = p.tokens[p.pos:]
	}
	belumSelesai := true
	for _, t := range sisa {
		if t.Tipe != DEDENT && t.Tipe != BARIS_BARU && t.Tipe != EOF {
			belumSelesai = false
			break
		}
	}
	panic(&Kesalahan{
		Jenis: KSintaks, Pesan: pesan, Baris: tok.Baris, Kolom: tok.Kolom,
		BarisKode: barisKode, AdaBarisKode: true, BelumSelesai: belumSelesai,
	})
}

func (p *parser) galatDiSini(pesan string) { p.galat(pesan, p.pos) }

// jelaskanToken: deskripsi token yang ditemukan, untuk pesan kesalahan.
func jelaskanToken(tok Token) string {
	switch tok.Tipe {
	case IDENTIFIER:
		return "kata '" + tok.teksNilai() + "'"
	case ANGKA, DESIMAL:
		return "angka " + reprNilai(tok.Nilai)
	case TEKS:
		return "teks \"" + tok.teksNilai() + "\""
	case TEKS_FORMAT, INDENT, DEDENT, BARIS_BARU, EOF:
		return jelaskanTipe(tok.Tipe)
	}
	if s, ok := tok.Nilai.(string); ok && s != "" && unicode.IsLetter([]rune(s)[0]) {
		return "kata '" + s + "'"
	}
	return "tanda '" + tok.teksNilai() + "'"
}

var kataPerintah = func() []string {
	ada := map[string]bool{}
	for k := range kataKunci {
		ada[k] = true
	}
	for _, k := range []string{"ubah", "tambahkan", "kurangi", "kalikan", "bagi", "tunggu", "tanya"} {
		ada[k] = true
	}
	hasil := make([]string, 0, len(ada))
	for k := range ada {
		hasil = append(hasil, k)
	}
	sort.Strings(hasil)
	return hasil
}()

// petunjukKataAwal: petunjuk bila kata pertama sebuah perintah mirip kata kunci.
func petunjukKataAwal(tok Token) string {
	if tok.Tipe != IDENTIFIER {
		return ""
	}
	kata := tok.teksNilai()
	kecil := strings.ToLower(kata)
	if kata != kecil {
		if _, ada := kataKunci[kecil]; ada {
			return "\n  Petunjuk: kata kunci ditulis dengan huruf kecil. Tulis '" + kecil + "', bukan '" + kata + "'."
		}
	}
	if m := palingMirip(kecil, kataPerintah, 0.75); m != "" {
		return "\n  Petunjuk: maksud Anda '" + m + "'?"
	}
	return ""
}

func (p *parser) harapkanAkhirPernyataan(awal int) {
	if p.periksa(BARIS_BARU, DEDENT, EOF) {
		return
	}
	if p.pos > 0 {
		if t := p.tokens[p.pos-1].Tipe; t == BARIS_BARU || t == DEDENT {
			return
		}
	}
	p.galatDiSini("Perintah seharusnya berakhir di sini, tetapi masih ada " + jelaskanToken(p.saatIni()) +
		". Tulis setiap perintah di barisnya sendiri." + petunjukKataAwal(p.tokens[awal]))
}

// ---- Program & blok ----

func (p *parser) parse() *NodeProgram {
	var pernyataan []Node
	p.lewatiBarisBaru()
	for !p.periksa(EOF) {
		awal := p.pos
		if stmt := p.parsePernyataan(); stmt != nil {
			pernyataan = append(pernyataan, stmt)
		}
		p.harapkanAkhirPernyataan(awal)
		p.lewatiBarisBaru()
	}
	return &NodeProgram{pernyataan}
}

func (p *parser) parseBlok() []Node {
	p.masuk()
	defer p.keluar()
	adaKoma := p.cocok(KOMA)
	adaKata := p.cocok(MAKA, LAKUKAN)
	adaTitikDua := p.cocok(TITIK_DUA)
	if !(adaKoma || adaKata || adaTitikDua) {
		p.galatDiSini("Diharapkan tanda ':' (atau kata 'maka' / 'lakukan') untuk memulai blok, " +
			"tetapi yang ditemukan " + jelaskanToken(p.saatIni()))
	}
	if !p.periksa(BARIS_BARU, EOF) {
		if stmt := p.parsePernyataan(); stmt != nil {
			return []Node{stmt}
		}
		return nil
	}
	if adaKoma && !(adaKata || adaTitikDua) {
		p.galatDiSini("Setelah koma, tulis perintahnya di baris yang sama, atau akhiri dengan 'maka:' / 'lakukan:'")
	}
	p.lewatiBarisBaru()
	p.harapkan(INDENT, "Isi blok harus ditulis menjorok ke dalam (diawali spasi) di baris berikutnya")
	var stmts []Node
	for !p.periksa(DEDENT, EOF) {
		p.lewatiBarisBaru()
		if p.periksa(DEDENT, EOF) {
			break
		}
		awal := p.pos
		if stmt := p.parsePernyataan(); stmt != nil {
			stmts = append(stmts, stmt)
		}
		p.harapkanAkhirPernyataan(awal)
		p.lewatiBarisBaru()
	}
	if p.periksa(DEDENT) {
		p.maju()
	}
	return stmts
}

// ---- Pernyataan ----

func (p *parser) parsePernyataan() Node {
	tok := p.saatIni()
	switch tok.Tipe {
	case BUAT:
		return p.parseDeklarasi("")
	case TETAP:
		return p.parseKonstanta()
	case BILANGAN, DESIMAL_TIPE, TEKS_TIPE, LOGIKA_TIPE:
		peta := map[TipeToken]string{BILANGAN: "bilangan", DESIMAL_TIPE: "desimal", TEKS_TIPE: "teks", LOGIKA_TIPE: "logika"}
		return p.parseDeklarasi(peta[tok.Tipe])
	case TAMPILKAN:
		return p.parseTampilkan()
	case JIKA:
		return p.parseJika()
	case PILIH:
		return p.parsePilih()
	case SELAMA:
		t := p.majuToken()
		kondisi := p.parseEkspresi()
		return &NodeSelama{pos{t.Baris, t.Kolom}, kondisi, p.parseBlokPerulangan()}
	case UNTUK:
		return p.parseUntuk()
	case UNTUK_SETIAP:
		t := p.majuToken()
		nama := p.harapkan(IDENTIFIER, "").teksNilai()
		p.harapkan(DALAM, "")
		iterable := p.parseEkspresi()
		return &NodeUntukSetiap{pos{t.Baris, t.Kolom}, nama, iterable, p.parseBlokPerulangan()}
	case ULANGI:
		return p.parseUlangi()
	case FUNGSI:
		return p.parseFungsi()
	case KEMBALIKAN:
		idx := p.maju()
		t := p.tokens[idx]
		if p.dalamFungsi == 0 {
			p.galat("'kembalikan' hanya bisa dipakai di dalam fungsi.", idx)
		}
		var ekspresi Node
		if !p.periksa(BARIS_BARU, DEDENT, EOF) {
			ekspresi = p.parseEkspresi()
		}
		return &NodeKembalikan{pos{t.Baris, t.Kolom}, ekspresi}
	case BERHENTI, LEWATI:
		idx := p.maju()
		t := p.tokens[idx]
		if p.dalamPerulangan == 0 {
			p.galat("'"+t.teksNilai()+"' hanya bisa dipakai di dalam perulangan (selama, untuk, ulangi).", idx)
		}
		if t.Tipe == BERHENTI {
			return &NodeBerhenti{pos{t.Baris, t.Kolom}}
		}
		return &NodeLewati{pos{t.Baris, t.Kolom}}
	case KELAS:
		return p.parseKelas()
	case IMPOR:
		return p.parseImpor()
	case DARI:
		return p.parseDariImpor()
	case COBA:
		return p.parseCoba()
	case LEMPAR:
		t := p.majuToken()
		return &NodeLempar{pos{t.Baris, t.Kolom}, p.parseEkspresi()}
	case INDENT:
		p.galatDiSini("Baris ini menjorok ke dalam, padahal tidak sedang berada di dalam blok. Hapus spasi di awal baris.")
	case IDENTIFIER:
		if kalimat := p.cobaKalimatNatural(); kalimat != nil {
			return kalimat
		}
	}
	return p.parsePenugasanAtauEkspresi()
}

func (p *parser) parseDeklarasi(tipe string) Node {
	t := p.majuToken()
	nama := p.harapkan(IDENTIFIER, "").teksNilai()
	p.harapkanPengisian()
	return &NodeDeklarasiVariabel{pos{t.Baris, t.Kolom}, nama, p.parseEkspresi(), tipe}
}

func (p *parser) parseKonstanta() Node {
	t := p.majuToken()
	nama := p.harapkan(IDENTIFIER, "").teksNilai()
	p.harapkanPengisian()
	return &NodeKonstanta{pos{t.Baris, t.Kolom}, nama, p.parseEkspresi()}
}

func (p *parser) harapkanPengisian() {
	if p.cocok(SAMA_DENGAN, ADALAH) {
		return
	}
	p.galatDiSini("Setelah nama variabel, tulis '=' atau 'adalah', tetapi yang ditemukan " +
		jelaskanToken(p.saatIni()) + ". Contoh: buat umur adalah 17")
}

func bisaDiisi(n Node) bool {
	switch n.(type) {
	case *NodeIdentifier, *NodeAksesDaftar, *NodeAksesAtribut:
		return true
	}
	return false
}

func (p *parser) pastikanBisaDiisi(n Node, idx int) {
	if !bisaDiisi(n) {
		p.galat("Bagian ini tidak bisa diberi nilai. Yang bisa diberi nilai hanyalah variabel, "+
			"elemen daftar (mis. d[0]), atau atribut objek (mis. diri.nama).", idx)
	}
}

// cobaParse menjalankan f; bila terjadi kesalahan sintaks, hasilnya nil (untuk mundur).
func (p *parser) cobaParse(f func() Node) (n Node) {
	defer func() {
		if r := recover(); r != nil {
			if _, ok := r.(*Kesalahan); !ok {
				panic(r)
			}
			n = nil
		}
	}()
	return f()
}

func (p *parser) parsePenugasanAtauEkspresi() Node {
	// "umur adalah 18" di awal kalimat berarti mengisi nilai; di dalam kondisi "adalah" berarti "==".
	if p.periksa(IDENTIFIER, DIRI) {
		awal := p.pos
		target := p.cobaParse(p.parsePostfix)
		if target != nil && bisaDiisi(target) && p.periksa(ADALAH) {
			t := p.majuToken()
			return &NodePenugasan{pos{t.Baris, t.Kolom}, target, p.parseEkspresi()}
		}
		p.pos = awal
	}
	idxAwal := p.pos
	ekspresi := p.parseEkspresi()
	if p.periksa(SAMA_DENGAN) {
		t := p.majuToken()
		p.pastikanBisaDiisi(ekspresi, idxAwal)
		return &NodePenugasan{pos{t.Baris, t.Kolom}, ekspresi, p.parseEkspresi()}
	}
	if p.periksa(TAMBAH_SAMA, KURANG_SAMA, KALI_SAMA, BAGI_SAMA, MODULO_SAMA) {
		t := p.majuToken()
		p.pastikanBisaDiisi(ekspresi, idxAwal)
		return &NodePenugasanGabungan{pos{t.Baris, t.Kolom}, ekspresi, t.teksNilai(), p.parseEkspresi()}
	}
	return ekspresi
}

// ---- Kalimat perintah natural ----

var kalimatNatural = map[string][]string{
	"ubah":      {"menjadi", "jadi"},
	"tambahkan": {"ke", "dengan"},
	"kurangi":   {"dari", "dengan"},
	"kalikan":   {"dengan"},
	"bagi":      {"dengan"},
}

var contohKalimat = map[string]string{
	"ubah":      "ubah umur menjadi 18",
	"tambahkan": "tambahkan 1 ke skor",
	"kurangi":   "kurangi nyawa dengan 1",
	"kalikan":   "kalikan harga dengan 2",
	"bagi":      "bagi total dengan 4",
}

var operatorKalimat = map[string]string{"kurangi": "-=", "kalikan": "*=", "bagi": "/="}

var awalNilai = []TipeToken{
	IDENTIFIER, WAKTU_SEKARANG, ANGKA_ACAK, DIRI, SUPER, ANGKA, DESIMAL, TEKS, TEKS_FORMAT,
	BENAR, SALAH, KOSONG, KURAWAL_BUKA, FUNGSI, MASUKAN, MASUKAN_ANGKA, MASUKAN_DESIMAL,
}

func adalahAwalNilai(t TipeToken) bool {
	for _, x := range awalNilai {
		if t == x {
			return true
		}
	}
	return false
}

var satuanWaktu = map[string]float64{"detik": 1, "milidetik": 0.001, "menit": 60, "jam": 3600}

func (p *parser) cobaKalimatTunggu() Node {
	tok := p.saatIni()
	berikut := p.intip(1)
	if berikut.Tipe == KURUNG_BUKA || berikut.Tipe == KURANG {
		if p.cariPenghubung([]string{"detik", "milidetik", "menit", "jam"}, p.pos+1) == "" {
			return nil
		}
	} else if !adalahAwalNilai(berikut.Tipe) {
		return nil
	}
	p.maju()
	lama := p.parseEkspresi()
	faktor := 1.0
	if p.periksaKata("detik", "milidetik", "menit", "jam") {
		faktor = satuanWaktu[p.majuToken().teksNilai()]
	}
	return &NodeTunggu{pos{tok.Baris, tok.Kolom}, lama, faktor}
}

func (p *parser) cobaKalimatNatural() Node {
	tok := p.saatIni()
	idxKataKerja := p.pos
	kataKerja := tok.teksNilai()
	if kataKerja == "tunggu" {
		return p.cobaKalimatTunggu()
	}
	penghubung, ada := kalimatNatural[kataKerja]
	if !ada {
		return nil
	}
	berikut := p.intip(1)
	if berikut.Tipe == KURUNG_BUKA || berikut.Tipe == SIKU_BUKA || berikut.Tipe == KURANG {
		// "tambahkan(5)" = panggil fungsi; "tambahkan (a + b) ke total" = kalimat
		if p.cariPenghubung(penghubung, p.pos+1) == "" {
			return nil
		}
	} else if !adalahAwalNilai(berikut.Tipe) {
		return nil // mis. "bagi = 2": variabel biasa bernama 'bagi'
	}
	p.maju()
	kata := p.cariPenghubung(penghubung, p.pos)
	if kata == "" {
		p.galat("Kalimat '"+kataKerja+"' belum lengkap. Contoh: "+contohKalimat[kataKerja], idxKataKerja)
	}
	var target, nilai Node
	if kata == "ke" || kata == "dari" {
		nilai = p.parseEkspresi()
		p.harapkanPenghubung(kata, kataKerja)
		if kata == "ke" {
			p.cocok(DALAM) // "ke dalam keranjang"
		}
		target = p.parseTarget()
	} else {
		target = p.parseTarget()
		p.harapkanPenghubung(kata, kataKerja)
		nilai = p.parseEkspresi()
	}
	posisi := pos{tok.Baris, tok.Kolom}
	switch kataKerja {
	case "ubah":
		return &NodePenugasan{posisi, target, nilai}
	case "tambahkan":
		return &NodeTambahkan{posisi, nilai, target}
	}
	return &NodePenugasanGabungan{posisi, target, operatorKalimat[kataKerja], nilai}
}

// cariPenghubung: kata penghubung pertama (di luar kurung) pada baris yang sama, atau "".
func (p *parser) cariPenghubung(penghubung []string, mulai int) string {
	kedalaman := 0
	for _, tok := range p.tokens[mulai:] {
		switch tok.Tipe {
		case BARIS_BARU, EOF:
			return ""
		case KURUNG_BUKA, SIKU_BUKA, KURAWAL_BUKA:
			kedalaman++
		case KURUNG_TUTUP, SIKU_TUTUP, KURAWAL_TUTUP:
			kedalaman--
		case IDENTIFIER, DARI:
			if kedalaman == 0 {
				for _, k := range penghubung {
					if tok.Nilai == k {
						return k
					}
				}
			}
		}
	}
	return ""
}

func (p *parser) harapkanPenghubung(kata, kataKerja string) {
	tok := p.saatIni()
	if (tok.Tipe == IDENTIFIER || tok.Tipe == DARI) && tok.Nilai == kata {
		p.maju()
		return
	}
	p.galatDiSini("Diharapkan kata '" + kata + "', tetapi yang ditemukan " + jelaskanToken(tok) +
		". Contoh: " + contohKalimat[kataKerja])
}

func (p *parser) parseTarget() Node {
	idx := p.pos
	target := p.parsePostfix()
	p.pastikanBisaDiisi(target, idx)
	return target
}

// ---- Tampilkan & kondisi ----

func (p *parser) parseTampilkan() Node {
	t := p.majuToken()
	var args []Node
	if !p.periksa(BARIS_BARU, DEDENT, EOF) {
		args = append(args, p.parseEkspresi())
		for p.cocok(KOMA) {
			args = append(args, p.parseEkspresi())
		}
	}
	return &NodeTampilkan{pos{t.Baris, t.Kolom}, args, t.teksNilai() != "cetak"}
}

func (p *parser) parseJika() Node {
	t := p.majuToken()
	n := &NodeJika{pos: pos{t.Baris, t.Kolom}}
	n.Kondisi = p.parseEkspresi()
	n.BlokJika = p.parseBlok()
	p.lewatiBarisBaru()
	for p.periksa(ATAU_JIKA) {
		p.maju()
		k := p.parseEkspresi()
		n.Cabang = append(n.Cabang, CabangJika{k, p.parseBlok()})
		p.lewatiBarisBaru()
	}
	if p.cocok(SELAINNYA) {
		n.BlokSelainnya, n.AdaSelainnya = p.parseBlok(), true
	} else if p.adalahJikaTidak() {
		p.maju()
		p.maju()
		n.BlokSelainnya, n.AdaSelainnya = p.parseBlok(), true
	}
	return n
}

// adalahJikaTidak: 'jika tidak:' / 'kalau tidak, ...' berarti selainnya; 'jika tidak hujan:' tidak.
func (p *parser) adalahJikaTidak() bool {
	kedua := p.intip(1)
	ketiga := p.intip(2).Tipe
	return p.periksa(JIKA) && kedua.Tipe == BUKAN && kedua.Nilai == "tidak" &&
		(ketiga == TITIK_DUA || ketiga == KOMA || ketiga == MAKA)
}

func (p *parser) parsePilih() Node {
	t := p.majuToken()
	n := &NodePilih{pos: pos{t.Baris, t.Kolom}}
	n.Ekspresi = p.parseEkspresi()
	p.harapkan(TITIK_DUA, "")
	p.lewatiBarisBaru()
	p.harapkan(INDENT, "")
	for !p.periksa(DEDENT, EOF) {
		p.lewatiBarisBaru()
		if p.periksa(DEDENT, EOF) {
			break
		}
		if p.periksa(KETIKA) {
			p.maju()
			nilai := p.parseNilaiKetika()
			n.Kasus = append(n.Kasus, KasusPilih{nilai, p.parseBlok()})
		} else if p.periksa(BAWAAN, SELAINNYA) {
			p.maju()
			n.Bawaan, n.AdaBawaan = p.parseBlok(), true
		} else {
			p.galatDiSini("Diharapkan 'ketika' atau 'bawaan' (boleh juga 'selainnya') dalam blok 'pilih'")
		}
		p.lewatiBarisBaru()
	}
	if p.periksa(DEDENT) {
		p.maju()
	}
	return n
}

func (p *parser) parseNilaiKetika() []Node {
	nilai := []Node{p.parseDan()}
	for {
		if p.cocok(ATAU) {
			nilai = append(nilai, p.parseDan())
			continue
		}
		if p.periksa(KOMA) {
			switch p.intip(1).Tipe {
			case ANGKA, DESIMAL, TEKS, BENAR, SALAH, KOSONG:
				p.maju()
				nilai = append(nilai, p.parseDan())
				continue
			}
		}
		return nilai
	}
}

// ---- Perulangan, fungsi, kelas ----

func (p *parser) parseUntuk() Node {
	t := p.majuToken()
	n := &NodeUntuk{pos: pos{t.Baris, t.Kolom}}
	n.Variabel = p.harapkan(IDENTIFIER, "").teksNilai()
	p.harapkan(DARI, "")
	n.Dari = p.parseEkspresi()
	p.harapkan(SAMPAI, "")
	n.Sampai = p.parseEkspresi()
	if p.cocok(LANGKAH) {
		n.Langkah = p.parseEkspresi()
	}
	n.Blok = p.parseBlokPerulangan()
	return n
}

func (p *parser) parseBlokPerulangan() []Node {
	p.dalamPerulangan++
	defer func() { p.dalamPerulangan-- }()
	return p.parseBlok()
}

func (p *parser) parseUlangi() Node {
	t := p.majuToken()
	posisi := pos{t.Baris, t.Kolom}
	if !p.periksa(TITIK_DUA) {
		jumlah := p.parseEkspresi()
		if !p.periksaKata("kali") {
			p.galatDiSini("Setelah 'ulangi <jumlah>' diharapkan kata 'kali'. Contoh: ulangi 3 kali: ...")
		}
		p.maju()
		return &NodeUlangiKali{posisi, jumlah, p.parseBlokPerulangan()}
	}
	blok := p.parseBlokPerulangan()
	p.lewatiBarisBaru()
	var kondisi Node
	if p.cocok(SELAMA) {
		kondisi = p.parseEkspresi()
	} else if p.periksa(SAMPAI) {
		ts := p.majuToken()
		kondisi = &NodeOperasiUnari{pos{ts.Baris, ts.Kolom}, "bukan", p.parseEkspresi()}
	} else {
		p.galatDiSini("Blok 'ulangi:' harus ditutup dengan 'selama <kondisi>' atau 'sampai <kondisi>'")
	}
	return &NodeUlangi{posisi, blok, kondisi}
}

func (p *parser) parseFungsi() Node {
	t := p.majuToken()
	nama := p.harapkan(IDENTIFIER, "").teksNilai()
	p.harapkan(KURUNG_BUKA, "")
	params := p.parseParameter()
	p.harapkan(KURUNG_TUTUP, "")
	// berhenti/lewati di dalam fungsi tidak bisa menghentikan perulangan di luar fungsi
	simpan := p.dalamPerulangan
	p.dalamPerulangan = 0
	p.dalamFungsi++
	defer func() { p.dalamFungsi--; p.dalamPerulangan = simpan }()
	return &NodeFungsi{pos{t.Baris, t.Kolom}, nama, params, p.parseBlok()}
}

func (p *parser) parseParameter() []Parameter {
	var params []Parameter
	if p.periksa(KURUNG_TUTUP) {
		return params
	}
	for {
		nama := p.harapkanNamaParam()
		var bawaan Node
		if p.cocok(SAMA_DENGAN) {
			bawaan = p.parseEkspresi()
		}
		params = append(params, Parameter{nama, bawaan})
		if !p.cocok(KOMA) {
			return params
		}
	}
}

func (p *parser) harapkanNamaParam() string {
	if p.periksa(IDENTIFIER, DIRI) {
		return p.majuToken().teksNilai()
	}
	return p.harapkan(IDENTIFIER, "").teksNilai()
}

func (p *parser) parseKelas() Node {
	t := p.majuToken()
	n := &NodeKelas{pos: pos{t.Baris, t.Kolom}}
	n.Nama = p.harapkan(IDENTIFIER, "").teksNilai()
	if p.cocok(MEWARISI) {
		n.Induk, n.AdaInduk = p.harapkan(IDENTIFIER, "").teksNilai(), true
	}
	n.Blok = p.parseBlok()
	return n
}

// ---- Modul ----

func (p *parser) parseImpor() Node {
	t := p.majuToken()
	modul := p.harapkan(IDENTIFIER, "Setelah 'impor' tulis nama modul, mis. impor matematika").teksNilai()
	idxAkhir := -1
	for p.cocok(TITIK) {
		idxAkhir = p.pos
		modul += "." + p.harapkanNamaAtribut()
	}
	alias := ""
	if p.cocok(SEBAGAI) {
		alias = p.harapkan(IDENTIFIER, "").teksNilai()
	} else if idxAkhir >= 0 && p.tokens[idxAkhir].Tipe != IDENTIFIER {
		nama := p.tokens[idxAkhir].teksNilai()
		p.galat("'"+nama+"' adalah kata kunci, jadi perlu nama lain. Contoh: impor "+modul+" sebagai "+nama+"_saya", idxAkhir)
	}
	return &NodeImpor{pos{t.Baris, t.Kolom}, modul, alias}
}

func (p *parser) parseDariImpor() Node {
	t := p.majuToken()
	modul := p.harapkan(IDENTIFIER, "Setelah 'dari' tulis nama modul, mis. dari acak impor bilangan").teksNilai()
	for p.cocok(TITIK) {
		modul += "." + p.harapkanNamaAtribut()
	}
	p.harapkan(IMPOR, "")
	idxNama := p.pos
	nama := p.harapkanNamaAtribut()
	alias := ""
	if p.cocok(SEBAGAI) {
		alias = p.harapkan(IDENTIFIER, "").teksNilai()
	} else if p.tokens[idxNama].Tipe != IDENTIFIER {
		p.galat("'"+nama+"' adalah kata kunci, jadi perlu nama lain. Contoh: dari "+modul+" impor "+nama+
			" sebagai "+nama+"_"+modul+", atau pakai "+modul+"."+nama+"(...)", idxNama)
	}
	return &NodeDariImpor{pos{t.Baris, t.Kolom}, modul, nama, alias}
}

// ---- Penanganan kesalahan ----

func (p *parser) parseCoba() Node {
	t := p.majuToken()
	n := &NodeCoba{pos: pos{t.Baris, t.Kolom}}
	n.BlokCoba = p.parseBlok()
	p.lewatiBarisBaru()
	for p.periksa(TANGKAP) {
		p.maju()
		jenis, variabel := "", ""
		if p.periksa(IDENTIFIER) {
			idxJenis := p.maju()
			jenis = p.tokens[idxJenis].teksNilai()
			if _, ada := semuaNamaTangkap()[strings.ToLower(jenis)]; !ada {
				p.galat(pesanJenisKesalahanAsing(jenis), idxJenis)
			}
		}
		if p.cocok(SEBAGAI) {
			variabel = p.harapkan(IDENTIFIER, "").teksNilai()
		} else if adalahNamaSemuaKesalahan(jenis) {
			variabel = jenis // 'tangkap kesalahan:' — pesannya ada di variabel 'kesalahan'
		}
		n.Penangkap = append(n.Penangkap, Penangkap{jenis, variabel, p.parseBlok()})
		p.lewatiBarisBaru()
	}
	if p.cocok(AKHIRNYA) {
		n.BlokAkhirnya = p.parseBlok()
	}
	return n
}

func pesanJenisKesalahanAsing(nama string) string {
	dikenal := semuaNamaTangkap()
	if m := palingMirip(strings.ToLower(nama), kunciUrut(dikenal), 0.75); m != "" {
		return "'" + nama + "' bukan jenis kesalahan yang dikenal. Maksud Anda '" + dikenal[m] + "'?"
	}
	return "'" + nama + "' bukan jenis kesalahan yang dikenal. " +
		"Untuk menyimpan pesan kesalahan ke variabel, tulis: tangkap sebagai " + nama
}

// ---- Ekspresi ----

func (p *parser) parseEkspresi() Node {
	p.masuk()
	defer p.keluar()
	return p.parseAtau()
}

func (p *parser) parseAtau() Node {
	kiri := p.parseDan()
	for p.periksa(ATAU) {
		t := p.majuToken()
		kiri = &NodeOperasiBiner{pos{t.Baris, t.Kolom}, kiri, "atau", p.parseDan()}
	}
	return kiri
}

func (p *parser) parseDan() Node {
	kiri := p.parseBukan()
	for p.periksa(DAN) {
		t := p.majuToken()
		kiri = &NodeOperasiBiner{pos{t.Baris, t.Kolom}, kiri, "dan", p.parseBukan()}
	}
	return kiri
}

func (p *parser) parseBukan() Node {
	p.masuk()
	defer p.keluar()
	if p.periksa(BUKAN) {
		t := p.majuToken()
		return &NodeOperasiUnari{pos{t.Baris, t.Kolom}, "bukan", p.parseBukan()}
	}
	return p.parsePerbandingan()
}

var opTeksKeSimbol = map[TipeToken]string{
	SAMA_DENGAN_OP: "==", ADALAH: "==", TIDAK_SAMA_OP: "!=", LEBIH_DARI: ">",
	KURANG_DARI: "<", TIDAK_KURANG_DARI: ">=", TIDAK_LEBIH_DARI: "<=",
}

func (p *parser) parsePerbandingan() Node {
	kiri := p.parsePenjumlahan()
	for {
		tok := p.saatIni()
		posisi := pos{tok.Baris, tok.Kolom}
		switch tok.Tipe {
		case ADA, TIDAK_ADA:
			p.maju()
			p.harapkan(DALAM, "Setelah '"+tok.teksNilai()+"' diharapkan kata 'dalam', mis. \"apel\" "+tok.teksNilai()+" dalam keranjang")
			op := "ada dalam"
			if tok.Tipe == TIDAK_ADA {
				op = "tidak ada dalam"
			}
			kiri = &NodeOperasiBiner{posisi, kiri, op, p.parsePenjumlahan()}
		case HABIS_DIBAGI, TIDAK_HABIS_DIBAGI:
			p.maju()
			sisa := &NodeOperasiBiner{posisi, kiri, "%", p.parsePenjumlahan()}
			op := "=="
			if tok.Tipe == TIDAK_HABIS_DIBAGI {
				op = "!="
			}
			kiri = &NodeOperasiBiner{posisi, sisa, op, &NodeAngka{posisi, 0}}
		default:
			var op string
			switch {
			case tok.Tipe == SAMA || tok.Tipe == TIDAK_SAMA || tok.Tipe == LEBIH_BESAR ||
				tok.Tipe == LEBIH_KECIL || tok.Tipe == LEBIH_BESAR_SAMA || tok.Tipe == LEBIH_KECIL_SAMA:
				op = tok.teksNilai()
			case opTeksKeSimbol[tok.Tipe] != "":
				op = opTeksKeSimbol[tok.Tipe]
			case tok.Tipe == BUKAN && tok.Nilai == "bukan":
				op = "!=" // hari bukan "Minggu"
			default:
				return kiri
			}
			p.maju()
			kiri = &NodeOperasiBiner{posisi, kiri, op, p.parsePenjumlahan()}
		}
	}
}

func (p *parser) parsePenjumlahan() Node {
	kiri := p.parsePerkalian()
	for p.periksa(TAMBAH, KURANG, DITAMBAH, DIKURANG) {
		t := p.majuToken()
		op := t.teksNilai()
		if t.Tipe == DITAMBAH {
			op = "+"
		} else if t.Tipe == DIKURANG {
			op = "-"
		}
		kiri = &NodeOperasiBiner{pos{t.Baris, t.Kolom}, kiri, op, p.parsePerkalian()}
	}
	return kiri
}

func (p *parser) parsePerkalian() Node {
	kiri := p.parsePangkat()
	for p.periksa(KALI, BAGI, MODULO, SISA_BAGI, DIKALI, DIBAGI) {
		t := p.majuToken()
		op := t.teksNilai()
		switch t.Tipe {
		case SISA_BAGI:
			op = "%"
		case DIKALI:
			op = "*"
		case DIBAGI:
			op = "/"
		}
		kiri = &NodeOperasiBiner{pos{t.Baris, t.Kolom}, kiri, op, p.parsePangkat()}
	}
	return kiri
}

func (p *parser) parsePangkat() Node {
	p.masuk()
	defer p.keluar()
	basis := p.parseUnari()
	if p.periksa(PANGKAT, PANGKAT_KK) {
		t := p.majuToken()
		return &NodeOperasiBiner{pos{t.Baris, t.Kolom}, basis, "**", p.parsePangkat()}
	}
	return basis
}

func (p *parser) parseUnari() Node {
	p.masuk()
	defer p.keluar()
	if p.periksa(KURANG) {
		t := p.majuToken()
		return &NodeOperasiUnari{pos{t.Baris, t.Kolom}, "-", p.parseUnari()}
	}
	return p.parsePostfix()
}

func (p *parser) parsePostfix() Node {
	node := p.parsePrimer()
	for {
		b, k := node.posisi()
		switch {
		case p.periksa(KURUNG_BUKA):
			p.maju()
			var args []Node
			if !p.periksa(KURUNG_TUTUP) {
				args = append(args, p.parseEkspresi())
				for p.cocok(KOMA) {
					args = append(args, p.parseEkspresi())
				}
			}
			p.harapkan(KURUNG_TUTUP, "")
			node = &NodePanggilFungsi{pos{b, k}, node, args}
		case p.periksa(SIKU_BUKA):
			p.maju()
			node = p.parseSubscript(node)
		case p.periksa(TITIK):
			p.maju()
			node = &NodeAksesAtribut{pos{b, k}, node, p.harapkanNamaAtribut()}
		default:
			return node
		}
	}
}

// harapkanNamaAtribut: nama setelah titik; kata kunci juga boleh (acak.pilih, berkas.tulis).
func (p *parser) harapkanNamaAtribut() string {
	tok := p.saatIni()
	if tok.Tipe == IDENTIFIER || (tipeKataKunci[tok.Tipe] && adalahPengenal(tok.teksNilai())) {
		return p.majuToken().teksNilai()
	}
	return p.harapkan(IDENTIFIER, "Setelah tanda '.' diharapkan nama atribut atau metode, tetapi yang ditemukan "+
		jelaskanToken(tok)).teksNilai()
}

func (p *parser) parseSubscript(objek Node) Node {
	b, k := objek.posisi()
	if p.periksa(TITIK_DUA) {
		p.maju()
		var akhir Node
		if !p.periksa(SIKU_TUTUP) {
			akhir = p.parseEkspresi()
		}
		p.harapkan(SIKU_TUTUP, "")
		return &NodeIrisanDaftar{pos{b, k}, objek, nil, akhir}
	}
	awal := p.parseEkspresi()
	if p.periksa(TITIK_DUA) {
		p.maju()
		var akhir Node
		if !p.periksa(SIKU_TUTUP) {
			akhir = p.parseEkspresi()
		}
		p.harapkan(SIKU_TUTUP, "")
		return &NodeIrisanDaftar{pos{b, k}, objek, awal, akhir}
	}
	p.harapkan(SIKU_TUTUP, "")
	return &NodeAksesDaftar{pos{b, k}, objek, awal}
}

func (p *parser) parsePrimer() Node {
	tok := p.saatIni()
	posisi := pos{tok.Baris, tok.Kolom}
	switch tok.Tipe {
	case ANGKA, DESIMAL:
		p.maju()
		return &NodeAngka{posisi, tok.Nilai}
	case TEKS:
		p.maju()
		return &NodeTeks{posisi, tok.teksNilai()}
	case TEKS_FORMAT:
		p.maju()
		return &NodeTeksFormat{posisi, tok.teksNilai()}
	case BENAR, SALAH:
		p.maju()
		return &NodeLogika{posisi, tok.Tipe == BENAR}
	case KOSONG:
		p.maju()
		return &NodeKosong{posisi}
	case IDENTIFIER:
		// tanya "Siapa namamu?" / tanya angka "Berapa umurmu?" — hanya bila langsung diikuti teks.
		if tok.Nilai == "tanya" {
			t1, t2 := p.intip(1), p.intip(2)
			adalahTeks := func(t Token) bool { return t.Tipe == TEKS || t.Tipe == TEKS_FORMAT }
			if adalahTeks(t1) || (t1.Tipe == IDENTIFIER && t1.Nilai == "angka" && adalahTeks(t2)) {
				p.maju()
				jenis := "teks"
				if p.periksaKata("angka") {
					p.maju()
					jenis = "angka"
				}
				return &NodeTanya{posisi, p.parsePostfix(), jenis}
			}
		}
		p.maju()
		return &NodeIdentifier{posisi, tok.teksNilai()}
	case WAKTU_SEKARANG:
		p.maju()
		return &NodeWaktuSekarang{posisi, strings.Fields(tok.teksNilai())[0]}
	case ANGKA_ACAK:
		p.maju()
		contoh := "Contoh: angka acak dari 1 sampai 6"
		p.harapkan(DARI, "Setelah 'angka acak' diharapkan kata 'dari'. "+contoh)
		minimum := p.parsePenjumlahan()
		p.harapkan(SAMPAI, "Diharapkan kata 'sampai' untuk batas atas. "+contoh)
		return &NodeAngkaAcak{posisi, minimum, p.parsePenjumlahan()}
	case DIRI, SUPER, MASUKAN, MASUKAN_ANGKA, MASUKAN_DESIMAL:
		p.maju()
		return &NodeIdentifier{posisi, tok.teksNilai()}
	case KURUNG_BUKA:
		p.maju()
		ekspresi := p.parseEkspresi()
		p.harapkan(KURUNG_TUTUP, "")
		return ekspresi
	case SIKU_BUKA:
		return p.parseDaftarLiteral()
	case KURAWAL_BUKA:
		return p.parseKamusLiteral()
	case FUNGSI:
		return p.parseFungsiAnonim()
	}
	p.galatDiSini("Di sini diharapkan sebuah nilai (angka, teks, nama, dll.), tetapi yang ditemukan " + jelaskanToken(tok))
	return nil
}

func (p *parser) parseDaftarLiteral() Node {
	t := p.majuToken()
	var elemen []Node
	if !p.periksa(SIKU_TUTUP) {
		elemen = append(elemen, p.parseEkspresi())
		for p.cocok(KOMA) {
			if p.periksa(SIKU_TUTUP) {
				break
			}
			elemen = append(elemen, p.parseEkspresi())
		}
	}
	p.harapkan(SIKU_TUTUP, "")
	return &NodeDaftar{pos{t.Baris, t.Kolom}, elemen}
}

func (p *parser) parseKamusLiteral() Node {
	t := p.majuToken()
	var pasangan [][2]Node
	if !p.periksa(KURAWAL_TUTUP) {
		for {
			kunci := p.parseEkspresi()
			p.harapkan(TITIK_DUA, "")
			pasangan = append(pasangan, [2]Node{kunci, p.parseEkspresi()})
			if !p.cocok(KOMA) || p.periksa(KURAWAL_TUTUP) {
				break
			}
		}
	}
	p.harapkan(KURAWAL_TUTUP, "")
	return &NodeKamus{pos{t.Baris, t.Kolom}, pasangan}
}

func (p *parser) parseFungsiAnonim() Node {
	t := p.majuToken()
	p.harapkan(KURUNG_BUKA, "")
	params := p.parseParameter()
	p.harapkan(KURUNG_TUTUP, "")
	p.harapkan(TITIK_DUA, "")
	p.cocok(KEMBALIKAN) // "fungsi(x): kembalikan x * x" juga boleh
	return &NodeFungsiAnonim{pos{t.Baris, t.Kolom}, params, p.parseEkspresi()}
}
