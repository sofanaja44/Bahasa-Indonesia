package mesin

import (
	"math/big"
	"strconv"
	"strings"
	"unicode"
)

const habis rune = -1 // akhir kode (None di Python)

// lexer mengubah kode menjadi token; sama dengan src/lexer.py, termasuk pesan kesalahannya.
type lexer struct {
	sumber          []rune
	pos             int
	baris, kolom    int
	tokens          []Token
	tumpukanIndent  []int
	awalBaris       bool
	kedalamanKurung int
	daftarBaris     []string
}

// Tokenisasi mengubah kode sumber menjadi daftar token. Kesalahan dilempar sebagai *Kesalahan.
func Tokenisasi(kode string) (tokens []Token, err *Kesalahan) {
	defer tangkapKesalahan(&err)
	lx := &lexer{
		sumber:         []rune(kode),
		baris:          1,
		kolom:          1,
		tumpukanIndent: []int{0},
		awalBaris:      true,
		daftarBaris:    strings.Split(kode, "\n"),
	}
	return lx.tokenisasi(), nil
}

// tangkapKesalahan mengubah panic(*Kesalahan) menjadi nilai kembalian.
func tangkapKesalahan(err **Kesalahan) {
	if r := recover(); r != nil {
		if k, ok := r.(*Kesalahan); ok {
			*err = k
			return
		}
		panic(r)
	}
}

func (lx *lexer) karakter() rune {
	if lx.pos < len(lx.sumber) {
		return lx.sumber[lx.pos]
	}
	return habis
}

func (lx *lexer) intip(offset int) rune {
	if i := lx.pos + offset; i < len(lx.sumber) {
		return lx.sumber[i]
	}
	return habis
}

func (lx *lexer) maju() rune {
	ch := lx.karakter()
	if ch == habis {
		return habis
	}
	lx.pos++
	if ch == '\n' {
		lx.baris++
		lx.kolom = 1
		lx.awalBaris = true
	} else {
		lx.kolom++
	}
	return ch
}

func (lx *lexer) barisKode(nomor int) string {
	if i := nomor - 1; i >= 0 && i < len(lx.daftarBaris) {
		return lx.daftarBaris[i]
	}
	return ""
}

func (lx *lexer) galat(pesan string, baris, kolom int) {
	panic(&Kesalahan{
		Jenis: KSintaks, Pesan: pesan, Baris: baris, Kolom: kolom,
		BarisKode: lx.barisKode(baris), AdaBarisKode: true,
	})
}

func (lx *lexer) galatDiSini(pesan string) { lx.galat(pesan, lx.baris, lx.kolom) }

func (lx *lexer) tambah(tipe TipeToken, nilai any, baris, kolom int) {
	lx.tokens = append(lx.tokens, Token{tipe, nilai, baris, kolom})
}

func adalahHuruf(r rune) bool      { return r != habis && unicode.IsLetter(r) }
func adalahAngka(r rune) bool      { return r != habis && unicode.IsDigit(r) }
func adalahHurufAngka(r rune) bool { return r != habis && (unicode.IsLetter(r) || unicode.IsNumber(r)) }
func adalahKarakterNama(r rune) bool {
	return r == '_' || adalahHurufAngka(r)
}

func (lx *lexer) tokenisasi() []Token {
	for lx.karakter() != habis {
		if lx.awalBaris && lx.kedalamanKurung > 0 {
			lx.awalBaris = false // lanjutan isi kurung: indentasinya tidak berarti apa-apa
		} else if lx.awalBaris {
			lx.prosesIndentasi()
			if lx.karakter() == habis {
				break
			}
			if lx.karakter() == '\n' {
				lx.maju()
				continue
			}
		}

		ch := lx.karakter()
		switch {
		case ch == '\n':
			if lx.kedalamanKurung == 0 {
				lx.tambah(BARIS_BARU, "\\n", lx.baris, lx.kolom)
			}
			lx.maju()
		case ch == ' ' || ch == '\t' || ch == '\r':
			lx.maju()
		case ch == '#':
			for lx.karakter() != habis && lx.karakter() != '\n' {
				lx.maju()
			}
		case ch == '"' && lx.intip(1) == '"' && lx.intip(2) == '"':
			lx.lewatiKomentarMultibaris()
		case adalahAngka(ch):
			lx.bacaAngka()
		case ch == 'f' && (lx.intip(1) == '"' || lx.intip(1) == '\''):
			lx.bacaTeksFormat(1, "F-string")
		case ch == 'f' && lx.intipKataDariPos() == "format" && lx.pos+6 < len(lx.sumber) &&
			(lx.sumber[lx.pos+6] == '"' || lx.sumber[lx.pos+6] == '\''):
			lx.bacaTeksFormat(6, "Format string")
		case ch == '"' || ch == '\'':
			lx.bacaTeks()
		case ch == '_' || adalahHuruf(ch):
			lx.bacaIdentifier()
		case lx.cobaOperator():
		default:
			if tipe, ada := tandaBaca[ch]; ada {
				if ch == '(' || ch == '[' || ch == '{' {
					lx.kedalamanKurung++
				} else if ch == ')' || ch == ']' || ch == '}' {
					lx.kedalamanKurung = max(0, lx.kedalamanKurung-1)
				}
				lx.tambah(tipe, string(ch), lx.baris, lx.kolom)
				lx.maju()
				continue
			}
			lx.galatDiSini("Karakter tidak dikenal: '" + string(ch) + "'")
		}
	}
	for len(lx.tumpukanIndent) > 1 {
		lx.tumpukanIndent = lx.tumpukanIndent[:len(lx.tumpukanIndent)-1]
		lx.tambah(DEDENT, nil, lx.baris, lx.kolom)
	}
	lx.tambah(EOF, nil, lx.baris, lx.kolom)
	return lx.tokens
}

func (lx *lexer) prosesIndentasi() {
	lx.awalBaris = false
	barisToken := lx.baris
	level := 0
	for c := lx.karakter(); c == ' ' || c == '\t'; c = lx.karakter() {
		if c == '\t' {
			level += 4 // tab = 4 spasi
		} else {
			level++
		}
		lx.maju()
	}
	c := lx.karakter()
	if c == habis || c == '\n' || c == '#' {
		return // baris kosong atau hanya komentar
	}
	if c == '"' && lx.intip(1) == '"' && lx.intip(2) == '"' {
		return
	}
	saatIni := lx.tumpukanIndent[len(lx.tumpukanIndent)-1]
	if level > saatIni {
		lx.tumpukanIndent = append(lx.tumpukanIndent, level)
		lx.tambah(INDENT, nil, barisToken, 1)
	} else if level < saatIni {
		for len(lx.tumpukanIndent) > 1 && lx.tumpukanIndent[len(lx.tumpukanIndent)-1] > level {
			lx.tumpukanIndent = lx.tumpukanIndent[:len(lx.tumpukanIndent)-1]
			lx.tambah(DEDENT, nil, barisToken, 1)
		}
		if atas := lx.tumpukanIndent[len(lx.tumpukanIndent)-1]; atas != level {
			lx.galat("Level indentasi tidak konsisten (diharapkan "+strconv.Itoa(atas)+
				" spasi, ditemukan "+strconv.Itoa(level)+")", barisToken, 1)
		}
	}
}

func (lx *lexer) lewatiKomentarMultibaris() {
	barisAwal := lx.baris
	lx.maju()
	lx.maju()
	lx.maju()
	for lx.karakter() != habis {
		if lx.karakter() == '"' && lx.intip(1) == '"' && lx.intip(2) == '"' {
			lx.maju()
			lx.maju()
			lx.maju()
			return
		}
		lx.maju()
	}
	lx.galat("Komentar multi-baris tidak ditutup (diharapkan \"\"\")", barisAwal, lx.kolom)
}

// nilaiDigit: nilai angka desimal Unicode (bukan hanya 0-9), seperti int() di Python.
func nilaiDigit(r rune) rune {
	if r >= '0' && r <= '9' {
		return r - '0'
	}
	if r >= 0x1D7CE && r <= 0x1D7FF { // angka matematika: lima deret berurutan
		return (r - 0x1D7CE) % 10
	}
	nol := r
	for nol-1 >= 0 && unicode.IsDigit(nol-1) && r-nol < 9 {
		nol--
	}
	return r - nol
}

func keDigitAscii(s string) string {
	return strings.Map(func(r rune) rune {
		if unicode.IsDigit(r) {
			return '0' + nilaiDigit(r)
		}
		return r
	}, s)
}

func (lx *lexer) bacaAngka() {
	barisAwal, kolomAwal := lx.baris, lx.kolom
	var bagian []rune
	adaTitik := false
	for c := lx.karakter(); adalahAngka(c) || c == '.'; c = lx.karakter() {
		if c == '.' {
			if !adalahAngka(lx.intip(1)) {
				break // titik untuk akses atribut, bukan desimal
			}
			if adaTitik {
				lx.galat("Angka desimal tidak boleh memiliki lebih dari satu titik", barisAwal, kolomAwal)
			}
			adaTitik = true
		}
		bagian = append(bagian, c)
		lx.maju()
	}
	teks := keDigitAscii(string(bagian))
	if adaTitik {
		f, _ := strconv.ParseFloat(teks, 64)
		lx.tambah(DESIMAL, f, barisAwal, kolomAwal)
		return
	}
	lx.tambah(ANGKA, bulatDariTeks(teks), barisAwal, kolomAwal)
}

// bulatDariTeks: angka bulat sebagai int, atau *big.Int bila terlalu besar.
func bulatDariTeks(teks string) any {
	if n, err := strconv.ParseInt(teks, 10, 64); err == nil {
		return int(n)
	}
	b, _ := new(big.Int).SetString(teks, 10)
	return normalBulat(b)
}

var petaEscape = map[rune]string{'n': "\n", 't': "\t", '\\': "\\", '\'': "'", '"': "\"", 'r': "\r"}

func (lx *lexer) bacaTeks() {
	barisAwal, kolomAwal := lx.baris, lx.kolom
	pembuka := lx.karakter()
	lx.maju()
	var b strings.Builder
	for lx.karakter() != habis && lx.karakter() != pembuka {
		c := lx.karakter()
		if c == '\n' {
			lx.galat("Teks tidak ditutup sebelum akhir baris", barisAwal, kolomAwal)
		}
		if c == '\\' {
			lx.maju()
			esc := lx.karakter()
			if esc == habis {
				lx.galat("Escape sequence tidak lengkap", barisAwal, lx.kolom)
			}
			if pengganti, ada := petaEscape[esc]; ada {
				b.WriteString(pengganti)
			} else {
				b.WriteRune('\\')
				b.WriteRune(esc)
			}
			lx.maju()
		} else {
			b.WriteRune(c)
			lx.maju()
		}
	}
	if lx.karakter() == habis {
		lx.galat("Teks tidak ditutup (diharapkan "+string(pembuka)+")", barisAwal, kolomAwal)
	}
	lx.maju()
	lx.tambah(TEKS, b.String(), barisAwal, kolomAwal)
}

// bacaTeksFormat membaca f"..." (lewati=1) atau format"..." (lewati=6).
func (lx *lexer) bacaTeksFormat(lewati int, nama string) {
	barisAwal, kolomAwal := lx.baris, lx.kolom
	for i := 0; i < lewati; i++ {
		lx.maju()
	}
	pembuka := lx.karakter()
	lx.maju()
	var b strings.Builder
	for lx.karakter() != habis && lx.karakter() != pembuka {
		c := lx.karakter()
		if c == '\n' {
			lx.galat(nama+" tidak ditutup sebelum akhir baris", barisAwal, lx.kolom)
		}
		if c == '\\' {
			lx.maju()
			esc := lx.karakter()
			if esc == habis {
				lx.galat("Escape sequence tidak lengkap", barisAwal, lx.kolom)
			}
			if pengganti, ada := petaEscape[esc]; ada {
				b.WriteString(pengganti)
			} else if esc == '{' || esc == '}' {
				b.WriteRune(esc)
			} else {
				b.WriteRune('\\')
				b.WriteRune(esc)
			}
			lx.maju()
		} else {
			b.WriteRune(c)
			lx.maju()
		}
	}
	if lx.karakter() == habis {
		lx.galat(nama+" tidak ditutup (diharapkan "+string(pembuka)+")", barisAwal, lx.kolom)
	}
	lx.maju()
	lx.tambah(TEKS_FORMAT, b.String(), barisAwal, kolomAwal)
}

func (lx *lexer) bacaIdentifier() {
	barisAwal, kolomAwal := lx.baris, lx.kolom
	mulai := lx.pos
	for adalahKarakterNama(lx.karakter()) {
		lx.maju()
	}
	kata := string(lx.sumber[mulai:lx.pos])
	if awalanFrasa[kata] && lx.cobaFrasa(kata, barisAwal, kolomAwal) {
		return
	}
	if tipe, ada := kataKunci[kata]; ada {
		lx.tambah(tipe, kata, barisAwal, kolomAwal)
	} else {
		lx.tambah(IDENTIFIER, kata, barisAwal, kolomAwal)
	}
}

// cobaFrasa mencocokkan frasa kata kunci terpanjang yang diawali kataPertama.
func (lx *lexer) cobaFrasa(kataPertama string, baris, kolom int) bool {
	kandidat := append([]string{kataPertama}, lx.intipKataBerikutnya(panjangFrasaMax-1)...)
	for panjang := len(kandidat); panjang > 1; panjang-- {
		f := strings.Join(kandidat[:panjang], " ")
		tipe, ada := frasaKataKunci[f]
		if !ada {
			continue
		}
		for _, kata := range kandidat[1:panjang] {
			for lx.karakter() == ' ' || lx.karakter() == '\t' {
				lx.maju()
			}
			for range []rune(kata) {
				lx.maju()
			}
		}
		lx.tambah(tipe, f, baris, kolom)
		return true
	}
	return false
}

// intipKataBerikutnya: hingga `jumlah` kata berikutnya di baris yang sama (hanya melewati spasi/tab).
func (lx *lexer) intipKataBerikutnya(jumlah int) []string {
	var kata []string
	i := lx.pos
	for len(kata) < jumlah {
		for i < len(lx.sumber) && (lx.sumber[i] == ' ' || lx.sumber[i] == '\t') {
			i++
		}
		mulai := i
		for i < len(lx.sumber) && adalahKarakterNama(lx.sumber[i]) {
			i++
		}
		if i == mulai {
			break
		}
		kata = append(kata, string(lx.sumber[mulai:i]))
	}
	return kata
}

func (lx *lexer) intipKataDariPos() string {
	i := lx.pos
	for i < len(lx.sumber) && adalahKarakterNama(lx.sumber[i]) {
		i++
	}
	return string(lx.sumber[lx.pos:i])
}

func (lx *lexer) cobaOperator() bool {
	ch, ch2 := lx.karakter(), lx.intip(1)
	if ch2 != habis {
		if tipe, ada := operator2[string([]rune{ch, ch2})]; ada {
			b, k := lx.baris, lx.kolom
			lx.maju()
			lx.maju()
			lx.tambah(tipe, string([]rune{ch, ch2}), b, k)
			return true
		}
	}
	if tipe, ada := operator1[ch]; ada {
		b, k := lx.baris, lx.kolom
		lx.maju()
		lx.tambah(tipe, string(ch), b, k)
		return true
	}
	return false
}
