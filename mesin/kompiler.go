package mesin

import (
	"math/big"
	"strings"
)

// Jenis entri pada tumpukan "lepas": apa yang perlu dirapikan saat keluar lebih awal dari sebuah blok
// (berhenti, lewati, kembalikan).
const (
	ueLingkup    = iota // perlu opLingkupKeluar
	uePenangan          // perlu opCobaSelesai
	ueAkhirnya          // isi 'akhirnya' disalin di jalur keluar
	ueBuangNilai        // ada nilai kesalahan di tumpukan yang perlu dibuang
	uePerulangan        // tujuan berhenti/lewati
	ueFungsi            // batas fungsi (tujuan kembalikan)
)

type infoPerulangan struct {
	berhenti []int // instruksi lompat yang menunggu alamat akhir perulangan
	lanjut   []int // instruksi lompat yang menunggu alamat lanjutan perulangan
}

type entriLepas struct {
	jenis    int
	akhirnya []Node
	putaran  *infoPerulangan
}

type kompiler struct {
	m          *Mesin
	kode       *Kode
	lepas      []entriLepas
	indeksTeks map[string]int32
}

func (m *Mesin) kompilerBaru(nama string, batasFungsi bool) *kompiler {
	k := &kompiler{m: m, kode: &Kode{Nama: nama}, indeksTeks: map[string]int32{}}
	if batasFungsi {
		k.lepas = []entriLepas{{jenis: ueFungsi}}
	}
	return k
}

// kompilasi mengubah program menjadi bytecode. Bila repl benar dan perintah terakhir berupa
// ekspresi, nilainya disimpan agar bisa ditampilkan.
func (m *Mesin) kompilasi(program *NodeProgram, repl bool) *Kode {
	k := m.kompilerBaru("<program>", false)
	for i, stmt := range program.Pernyataan {
		if repl && i == len(program.Pernyataan)-1 && adalahEkspresiREPL(stmt) {
			k.ekspresi(stmt)
			k.emit(opSimpanHasil, 0, 0, nil)
			continue
		}
		k.pernyataan(stmt)
	}
	k.emit(opKosong, 0, 0, nil)
	k.emit(opKembalikan, 0, 0, nil)
	return k.kode
}

// adalahEkspresiREPL sama dengan _NODE_EKSPRESI di indonesia.py.
func adalahEkspresiREPL(n Node) bool {
	switch n.(type) {
	case *NodeAngka, *NodeTeks, *NodeTeksFormat, *NodeLogika, *NodeKosong, *NodeIdentifier,
		*NodeWaktuSekarang, *NodeAngkaAcak, *NodeTanya, *NodeOperasiBiner, *NodeOperasiUnari,
		*NodePanggilFungsi, *NodeDaftar, *NodeKamus, *NodeAksesDaftar, *NodeIrisanDaftar, *NodeAksesAtribut:
		return true
	}
	return false
}

func (k *kompiler) emit(op Op, a, b int, n Node) int {
	var baris, kolom int
	if n != nil {
		baris, kolom = n.posisi()
	}
	k.kode.ins = append(k.kode.ins, instruksi{op, int32(a), int32(b), int32(baris), int32(kolom)})
	return len(k.kode.ins) - 1
}

func (k *kompiler) alamat() int { return len(k.kode.ins) }

func (k *kompiler) tambal(i int) { k.kode.ins[i].a = int32(k.alamat()) }

func (k *kompiler) tambalB(i int) { k.kode.ins[i].b = int32(k.alamat()) }

func (k *kompiler) konstanta(v any) int {
	if s, ok := v.(string); ok {
		if i, ada := k.indeksTeks[s]; ada {
			return int(i)
		}
		k.indeksTeks[s] = int32(len(k.kode.konstanta))
	}
	k.kode.konstanta = append(k.kode.konstanta, v)
	return len(k.kode.konstanta) - 1
}

func (k *kompiler) simbol(nama string) int { return int(k.m.simbolUntuk(nama)) }

// butuhLingkup: apakah sebuah blok mendefinisikan nama secara langsung, sehingga perlu lingkup sendiri.
func butuhLingkup(blok []Node) bool {
	for _, s := range blok {
		switch s.(type) {
		case *NodeDeklarasiVariabel, *NodeKonstanta, *NodeFungsi, *NodeKelas, *NodeImpor, *NodeDariImpor:
			return true
		}
	}
	return false
}

// blok mengompilasi isi blok, di lingkup anak bila blok itu mendefinisikan nama.
func (k *kompiler) blok(stmts []Node) {
	perlu := butuhLingkup(stmts)
	if perlu {
		k.emit(opLingkupMasuk, 0, 0, nil)
		k.lepas = append(k.lepas, entriLepas{jenis: ueLingkup})
	}
	for _, s := range stmts {
		k.pernyataan(s)
	}
	if perlu {
		k.lepas = k.lepas[:len(k.lepas)-1]
		k.emit(opLingkupKeluar, 0, 0, nil)
	}
}

// lepasSampai merapikan entri dari atas sampai entri yang memenuhi `tujuan` (tidak termasuk).
// Untuk kembalikan, nilai kembalian ada di puncak tumpukan, jadi nilai kesalahan tidak dibuang.
func (k *kompiler) lepasSampai(tujuan func(entriLepas) bool, kembalikan bool) int {
	for i := len(k.lepas) - 1; i >= 0; i-- {
		e := k.lepas[i]
		if tujuan(e) {
			return i
		}
		switch e.jenis {
		case ueLingkup:
			k.emit(opLingkupKeluar, 0, 0, nil)
		case uePenangan:
			k.emit(opCobaSelesai, 0, 0, nil)
		case ueBuangNilai:
			if !kembalikan {
				k.emit(opBuang, 0, 0, nil)
			}
		case ueAkhirnya:
			simpan := k.lepas
			k.lepas = append([]entriLepas(nil), k.lepas[:i]...)
			k.blok(e.akhirnya)
			k.lepas = simpan
		}
	}
	return -1
}

func (k *kompiler) perulanganTerdekat() *infoPerulangan {
	i := k.lepasSampai(func(e entriLepas) bool { return e.jenis == uePerulangan }, false)
	return k.lepas[i].putaran
}

// mulaiPerulangan/akhiriPerulangan mengelola tujuan berhenti & lewati.
func (k *kompiler) mulaiPerulangan() *infoPerulangan {
	info := &infoPerulangan{}
	k.lepas = append(k.lepas, entriLepas{jenis: uePerulangan, putaran: info})
	return info
}

func (k *kompiler) akhiriPerulangan(info *infoPerulangan, alamatLanjut int) {
	k.lepas = k.lepas[:len(k.lepas)-1]
	for _, i := range info.lanjut {
		k.kode.ins[i].a = int32(alamatLanjut)
	}
	for _, i := range info.berhenti {
		k.tambal(i)
	}
}

// isiPerulangan: isi satu putaran di lingkup baru (seperti env.anak di Python).
func (k *kompiler) isiPerulangan(stmts []Node, variabel string) {
	perlu := variabel != "" || butuhLingkup(stmts)
	if perlu {
		k.emit(opLingkupMasuk, 0, 0, nil)
		k.lepas = append(k.lepas, entriLepas{jenis: ueLingkup})
	}
	if variabel != "" {
		k.emit(opDefinisikan, k.simbol(variabel), 0, nil)
	}
	for _, s := range stmts {
		k.pernyataan(s)
	}
	if perlu {
		k.lepas = k.lepas[:len(k.lepas)-1]
		k.emit(opLingkupKeluar, 0, 0, nil)
	}
}

// ---- Pernyataan ----

func (k *kompiler) pernyataan(n Node) {
	switch n := n.(type) {
	case *NodeDeklarasiVariabel:
		k.ekspresi(n.Ekspresi)
		if n.TipeEksplisit != "" {
			k.emit(opKonversi, k.konstanta(n.TipeEksplisit), 0, n)
		}
		k.emit(opDefinisikan, k.simbol(n.Nama), 0, n)
	case *NodeKonstanta:
		k.ekspresi(n.Ekspresi)
		k.emit(opDefinisikan, k.simbol(n.Nama), 1, n)
	case *NodePenugasan:
		k.ekspresi(n.Ekspresi)
		k.simpanTarget(n.Target, n)
	case *NodePenugasanGabungan:
		k.ekspresi(n.Target)
		k.ekspresi(n.Ekspresi)
		k.emit(opBiner, kodeOperator[strings.TrimSuffix(n.Operator, "=")], 0, n)
		k.simpanTarget(n.Target, n)
	case *NodeTambahkan:
		k.ekspresi(n.Nilai)
		k.ekspresi(n.Target)
		j := k.emit(opTambahkan, 0, 0, n)
		k.simpanTarget(n.Target, n)
		k.tambal(j)
	case *NodeTampilkan:
		for _, e := range n.Ekspresi {
			k.ekspresi(e)
		}
		baru := 0
		if n.BarisBaru {
			baru = 1
		}
		k.emit(opTampilkan, len(n.Ekspresi), baru, n)
	case *NodeTunggu:
		k.ekspresi(n.Lama)
		k.emit(opTunggu, k.konstanta(n.Faktor), 0, n)
	case *NodeJika:
		k.jika(n)
	case *NodePilih:
		k.pilih(n)
	case *NodeSelama:
		info := k.mulaiPerulangan()
		kepala := k.alamat()
		k.ekspresi(n.Kondisi)
		jSelesai := k.emit(opLompatSalah, 0, 0, nil)
		k.isiPerulangan(n.Blok, "")
		k.emit(opLompat, kepala, 0, nil)
		k.tambal(jSelesai)
		k.akhiriPerulangan(info, kepala)
	case *NodeUntuk:
		k.ekspresi(n.Dari)
		k.ekspresi(n.Sampai)
		if n.Langkah != nil {
			k.ekspresi(n.Langkah)
		} else {
			k.emit(opKonstanta, k.konstanta(1), 0, nil)
		}
		k.emit(opUntukSiapkan, 0, 0, n)
		info := k.mulaiPerulangan()
		kepala := k.alamat()
		jSelesai := k.emit(opUntukCek, 0, 0, n)
		k.emit(opUntukNilai, 0, 0, nil)
		k.isiPerulangan(n.Blok, n.Variabel)
		lanjut := k.alamat()
		k.emit(opUntukLangkah, 0, 0, n)
		k.emit(opLompat, kepala, 0, nil)
		k.tambal(jSelesai)
		k.akhiriPerulangan(info, lanjut)
		k.emit(opBuangN, 3, 0, nil)
	case *NodeUntukSetiap:
		k.ekspresi(n.Iterable)
		k.emit(opIterBuat, 0, 0, n)
		info := k.mulaiPerulangan()
		kepala := k.alamat()
		jSelesai := k.emit(opIterLanjut, 0, 0, nil)
		k.isiPerulangan(n.Blok, n.Variabel)
		k.emit(opLompat, kepala, 0, nil)
		k.tambal(jSelesai)
		k.akhiriPerulangan(info, kepala)
		k.emit(opBuang, 0, 0, nil)
	case *NodeUlangi:
		info := k.mulaiPerulangan()
		mulai := k.alamat()
		k.isiPerulangan(n.Blok, "")
		lanjut := k.alamat()
		k.ekspresi(n.Kondisi)
		jSelesai := k.emit(opLompatSalah, 0, 0, nil)
		k.emit(opLompat, mulai, 0, nil)
		k.tambal(jSelesai)
		k.akhiriPerulangan(info, lanjut)
	case *NodeUlangiKali:
		k.ekspresi(n.Jumlah)
		k.emit(opKaliSiapkan, 0, 0, n)
		info := k.mulaiPerulangan()
		kepala := k.alamat()
		jSelesai := k.emit(opKaliLanjut, 0, 0, nil)
		k.isiPerulangan(n.Blok, "")
		k.emit(opLompat, kepala, 0, nil)
		k.tambal(jSelesai)
		k.akhiriPerulangan(info, kepala)
		k.emit(opBuang, 0, 0, nil)
	case *NodeBerhenti:
		info := k.perulanganTerdekat()
		info.berhenti = append(info.berhenti, k.emit(opLompat, 0, 0, nil))
	case *NodeLewati:
		info := k.perulanganTerdekat()
		info.lanjut = append(info.lanjut, k.emit(opLompat, 0, 0, nil))
	case *NodeFungsi:
		proto := k.kompilasiFungsi(n.Nama, n.Parameter, n.Blok, nil)
		k.emit(opFungsi, k.konstanta(proto), 0, n)
		k.emit(opDefinisikan, k.simbol(n.Nama), 0, n)
	case *NodeKembalikan:
		if n.Ekspresi != nil {
			k.ekspresi(n.Ekspresi)
		} else {
			k.emit(opKosong, 0, 0, nil)
		}
		k.lepasSampai(func(e entriLepas) bool { return e.jenis == ueFungsi }, true)
		k.emit(opKembalikan, 0, 0, n)
	case *NodeKelas:
		k.kelas(n)
	case *NodeImpor:
		alias := -1
		if n.Alias != "" {
			alias = k.konstanta(n.Alias)
		}
		k.emit(opImpor, k.konstanta(n.Modul), alias, n)
	case *NodeDariImpor:
		k.emit(opDariImpor, k.konstanta([3]string{n.Modul, n.Nama, n.Alias}), 0, n)
	case *NodeCoba:
		k.coba(n)
	case *NodeLempar:
		k.ekspresi(n.Ekspresi)
		k.emit(opLempar, 0, 0, n)
	default:
		k.ekspresi(n)
		k.emit(opBuang, 0, 0, nil)
	}
}

func (k *kompiler) simpanTarget(target Node, stmt Node) {
	switch t := target.(type) {
	case *NodeIdentifier:
		k.emit(opSetel, k.simbol(t.Nama), 0, t)
	case *NodeAksesDaftar:
		k.ekspresi(t.Objek)
		k.ekspresi(t.Indeks)
		k.emit(opSetelIndeks, 0, 0, stmt)
	case *NodeAksesAtribut:
		k.ekspresi(t.Objek)
		k.emit(opSetelAtribut, k.konstanta(t.Atribut), 0, stmt)
	default:
		k.emit(opBuang, 0, 0, nil)
		k.emit(opGalat, k.konstanta(kesalahan(KTipe, "Bagian ini tidak bisa diberi nilai", posisiBaris(stmt), posisiKolom(stmt))), 0, stmt)
	}
}

func posisiBaris(n Node) int { b, _ := n.posisi(); return b }
func posisiKolom(n Node) int { _, kl := n.posisi(); return kl }

func (k *kompiler) jika(n *NodeJika) {
	var keAkhir []int
	k.ekspresi(n.Kondisi)
	jLanjut := k.emit(opLompatSalah, 0, 0, nil)
	k.blok(n.BlokJika)
	keAkhir = append(keAkhir, k.emit(opLompat, 0, 0, nil))
	k.tambal(jLanjut)
	for _, c := range n.Cabang {
		k.ekspresi(c.Kondisi)
		jLanjut = k.emit(opLompatSalah, 0, 0, nil)
		k.blok(c.Blok)
		keAkhir = append(keAkhir, k.emit(opLompat, 0, 0, nil))
		k.tambal(jLanjut)
	}
	if n.AdaSelainnya {
		k.blok(n.BlokSelainnya)
	}
	for _, j := range keAkhir {
		k.tambal(j)
	}
}

func (k *kompiler) pilih(n *NodePilih) {
	k.ekspresi(n.Ekspresi)
	var keAkhir []int
	for _, kasus := range n.Kasus {
		var keBlok []int
		for _, nilai := range kasus.Nilai {
			k.emit(opSalin, 0, 0, nil)
			k.ekspresi(nilai)
			k.emit(opBiner, biSama, 0, nil)
			jTidak := k.emit(opLompatSalah, 0, 0, nil)
			keBlok = append(keBlok, k.emit(opLompat, 0, 0, nil))
			k.tambal(jTidak)
		}
		jKasusBerikut := k.emit(opLompat, 0, 0, nil)
		for _, j := range keBlok {
			k.tambal(j)
		}
		k.emit(opBuang, 0, 0, nil)
		k.blok(kasus.Blok)
		keAkhir = append(keAkhir, k.emit(opLompat, 0, 0, nil))
		k.tambal(jKasusBerikut)
	}
	k.emit(opBuang, 0, 0, nil)
	if n.AdaBawaan {
		k.blok(n.Bawaan)
	}
	for _, j := range keAkhir {
		k.tambal(j)
	}
}

func (k *kompiler) kelas(n *NodeKelas) {
	desk := &KodeKelas{Nama: n.Nama, AdaInduk: n.AdaInduk}
	if n.AdaInduk {
		k.emit(opAmbil, k.simbol(n.Induk), 0, n)
	}
	for _, s := range n.Blok {
		switch s := s.(type) {
		case *NodeFungsi:
			proto := k.kompilasiFungsi(s.Nama, s.Parameter, s.Blok, nil)
			k.emit(opFungsi, k.konstanta(proto), 0, s)
			desk.Anggota = append(desk.Anggota, anggotaKelas{s.Nama, true})
		case *NodeDeklarasiVariabel:
			k.ekspresi(s.Ekspresi)
			desk.Anggota = append(desk.Anggota, anggotaKelas{s.Nama, false})
		}
	}
	k.emit(opKelas, k.konstanta(desk), 0, n)
	k.emit(opDefinisikan, k.simbol(n.Nama), 0, n)
}

// coba: penangan dalam untuk 'tangkap', penangan luar untuk 'akhirnya' di jalur kesalahan.
func (k *kompiler) coba(n *NodeCoba) {
	adaAkhirnya := len(n.BlokAkhirnya) > 0
	adaTangkap := len(n.Penangkap) > 0
	jAkhirnyaGalat, jTangkap := -1, -1
	if adaAkhirnya {
		jAkhirnyaGalat = k.emit(opCobaMulai, 0, 0, nil)
		k.lepas = append(k.lepas, entriLepas{jenis: ueAkhirnya, akhirnya: n.BlokAkhirnya}, entriLepas{jenis: uePenangan})
	}
	if adaTangkap {
		jTangkap = k.emit(opCobaMulai, 0, 0, nil)
		k.lepas = append(k.lepas, entriLepas{jenis: uePenangan})
	}
	k.blok(n.BlokCoba)
	if adaTangkap {
		k.lepas = k.lepas[:len(k.lepas)-1]
		k.emit(opCobaSelesai, 0, 0, nil)
		keAkhir := []int{k.emit(opLompat, 0, 0, nil)}
		k.tambal(jTangkap)
		for _, pen := range n.Penangkap {
			jenis := -1
			if pen.Jenis != "" {
				jenis = k.konstanta(pen.Jenis)
			}
			jTidakCocok := k.emit(opCocokTangkap, jenis, 0, nil)
			perlu := pen.Variabel != "" || butuhLingkup(pen.Blok)
			if perlu {
				k.emit(opLingkupMasuk, 0, 0, nil)
				k.lepas = append(k.lepas, entriLepas{jenis: ueLingkup})
			}
			if pen.Variabel != "" {
				k.emit(opTeksKesalahan, 0, 0, nil)
				k.emit(opDefinisikan, k.simbol(pen.Variabel), 0, nil)
			} else {
				k.emit(opBuang, 0, 0, nil)
			}
			for _, s := range pen.Blok {
				k.pernyataan(s)
			}
			if perlu {
				k.lepas = k.lepas[:len(k.lepas)-1]
				k.emit(opLingkupKeluar, 0, 0, nil)
			}
			keAkhir = append(keAkhir, k.emit(opLompat, 0, 0, nil))
			k.tambalB(jTidakCocok)
		}
		k.emit(opLemparUlang, 0, 0, nil)
		for _, j := range keAkhir {
			k.tambal(j)
		}
	}
	if adaAkhirnya {
		k.lepas = k.lepas[:len(k.lepas)-2]
		k.emit(opCobaSelesai, 0, 0, nil)
		k.blok(n.BlokAkhirnya)
		jSelesai := k.emit(opLompat, 0, 0, nil)
		k.tambal(jAkhirnyaGalat)
		k.lepas = append(k.lepas, entriLepas{jenis: ueBuangNilai})
		k.blok(n.BlokAkhirnya)
		k.lepas = k.lepas[:len(k.lepas)-1]
		k.emit(opLemparUlang, 0, 0, nil)
		k.tambal(jSelesai)
	}
}

// kompilasiFungsi: isi fungsi (atau fungsi anonim bila ekspresi != nil) menjadi KodeFungsi.
func (k *kompiler) kompilasiFungsi(nama string, params []Parameter, blok []Node, ekspresi Node) *KodeFungsi {
	proto := &KodeFungsi{Nama: nama}
	for _, p := range params {
		proto.Parameter = append(proto.Parameter, p.Nama)
		proto.simbol = append(proto.simbol, k.m.simbolUntuk(p.Nama))
		var bawaan *Kode
		if p.Bawaan != nil {
			anak := k.m.kompilerBaru(nama, true)
			anak.ekspresi(p.Bawaan)
			anak.emit(opKembalikan, 0, 0, nil)
			bawaan = anak.kode
		}
		proto.Bawaan = append(proto.Bawaan, bawaan)
	}
	anak := k.m.kompilerBaru(nama, true)
	if ekspresi != nil {
		anak.ekspresi(ekspresi)
		anak.emit(opKembalikan, 0, 0, nil)
	} else {
		for _, s := range blok {
			anak.pernyataan(s)
		}
		anak.emit(opKosong, 0, 0, nil)
		anak.emit(opKembalikan, 0, 0, nil)
	}
	proto.Kode = anak.kode
	return proto
}

// ---- Ekspresi ----

func namaPemanggilan(n Node) string {
	switch n := n.(type) {
	case *NodeIdentifier:
		return n.Nama
	case *NodeAksesAtribut:
		return namaPemanggilan(n.Objek) + "." + n.Atribut
	}
	return "fungsi"
}

func (k *kompiler) ekspresi(n Node) {
	switch n := n.(type) {
	case *NodeAngka:
		if b, ok := n.Nilai.(*big.Int); ok {
			k.emit(opKonstanta, k.konstanta(b), 0, nil)
		} else {
			k.emit(opKonstanta, k.konstanta(n.Nilai), 0, nil)
		}
	case *NodeTeks:
		k.emit(opKonstanta, k.konstanta(n.Nilai), 0, nil)
	case *NodeTeksFormat:
		k.teksFormat(n)
	case *NodeLogika:
		if n.Nilai {
			k.emit(opBenar, 0, 0, nil)
		} else {
			k.emit(opSalah, 0, 0, nil)
		}
	case *NodeKosong:
		k.emit(opKosong, 0, 0, nil)
	case *NodeIdentifier:
		k.emit(opAmbil, k.simbol(n.Nama), 0, n)
	case *NodeOperasiBiner:
		switch n.Operator {
		case "dan", "atau":
			k.ekspresi(n.Kiri)
			op := opLompatSalahAtauBuang
			if n.Operator == "atau" {
				op = opLompatBenarAtauBuang
			}
			j := k.emit(op, 0, 0, nil)
			k.ekspresi(n.Kanan)
			k.tambal(j)
		default:
			k.ekspresi(n.Kiri)
			k.ekspresi(n.Kanan)
			k.emit(opBiner, kodeOperator[n.Operator], 0, n)
		}
	case *NodeOperasiUnari:
		k.ekspresi(n.Operand)
		if n.Operator == "-" {
			k.emit(opNegasi, 0, 0, n)
		} else {
			k.emit(opBukan, 0, 0, n)
		}
	case *NodePanggilFungsi:
		k.ekspresi(n.Fungsi)
		for _, a := range n.Argumen {
			k.ekspresi(a)
		}
		k.emit(opPanggil, len(n.Argumen), k.konstanta(namaPemanggilan(n.Fungsi)), n)
	case *NodeDaftar:
		for _, e := range n.Elemen {
			k.ekspresi(e)
		}
		k.emit(opDaftar, len(n.Elemen), 0, n)
	case *NodeKamus:
		for _, p := range n.Pasangan {
			k.ekspresi(p[0])
			k.ekspresi(p[1])
		}
		k.emit(opKamus, len(n.Pasangan), 0, n)
	case *NodeAksesDaftar:
		k.ekspresi(n.Objek)
		k.ekspresi(n.Indeks)
		k.emit(opAmbilIndeks, 0, 0, n)
	case *NodeIrisanDaftar:
		k.ekspresi(n.Objek)
		flag := 0
		if n.Awal != nil {
			k.ekspresi(n.Awal)
			flag |= 1
		}
		if n.Akhir != nil {
			k.ekspresi(n.Akhir)
			flag |= 2
		}
		k.emit(opIrisan, flag, 0, n)
	case *NodeAksesAtribut:
		k.ekspresi(n.Objek)
		k.emit(opAmbilAtribut, k.konstanta(n.Atribut), 0, n)
	case *NodeWaktuSekarang:
		k.emit(opWaktu, k.konstanta(n.Bagian), 0, n)
	case *NodeAngkaAcak:
		k.ekspresi(n.Minimum)
		k.ekspresi(n.Maksimum)
		k.emit(opAcak, 0, 0, n)
	case *NodeTanya:
		k.ekspresi(n.Pertanyaan)
		jenis := 0
		if n.Jenis == "angka" {
			jenis = 1
		}
		k.emit(opTanya, jenis, 0, n)
	case *NodeFungsiAnonim:
		proto := k.kompilasiFungsi("<anonim>", n.Parameter, nil, n.Ekspresi)
		k.emit(opFungsi, k.konstanta(proto), 0, n)
	default:
		panic("ekspresi tidak dikenal")
	}
}

// teksFormat: format"Halo {nama}". Isi {...} dibaca saat program berjalan, sama seperti Python:
// kesalahan sintaks di dalamnya baru muncul ketika teks itu dihitung.
func (k *kompiler) teksFormat(n *NodeTeksFormat) {
	teks := []rune(n.Template)
	bagian := 0
	tambahTeks := func(s string) {
		k.emit(opKonstanta, k.konstanta(s), 0, nil)
		bagian++
	}
	sebelum, p := 0, 0
	for p < len(teks) {
		buka := indeksRune(teks, '{', p)
		if buka < 0 {
			break
		}
		tutup := indeksRune(teks, '}', buka+1)
		if tutup < 0 {
			break
		}
		if tutup == buka+1 { // "{}" bukan sisipan
			p = buka + 1
			continue
		}
		tambahTeks(string(teks[sebelum:buka]))
		isi := potongSpasi(string(teks[buka+1 : tutup]))
		k.sisipan(isi)
		bagian++
		sebelum, p = tutup+1, tutup+1
	}
	tambahTeks(string(teks[sebelum:]))
	k.emit(opGabungTeks, bagian, 0, nil)
}

func indeksRune(teks []rune, r rune, mulai int) int {
	for i := mulai; i < len(teks); i++ {
		if teks[i] == r {
			return i
		}
	}
	return -1
}

func (k *kompiler) sisipan(isi string) {
	tokens, err := Tokenisasi(isi)
	if err != nil {
		k.emit(opGalat, k.konstanta(err), 0, nil)
		k.emit(opKonstanta, k.konstanta(""), 0, nil)
		return
	}
	if len(tokens) <= 1 { // "{ }" menjadi teks kosong
		k.emit(opKonstanta, k.konstanta(""), 0, nil)
		return
	}
	ekspresi, err := parseEkspresiTunggal(tokens, isi)
	if err != nil {
		k.emit(opGalat, k.konstanta(err), 0, nil)
		k.emit(opKonstanta, k.konstanta(""), 0, nil)
		return
	}
	k.ekspresi(ekspresi)
	k.emit(opKeTeks, 0, 0, nil)
}
