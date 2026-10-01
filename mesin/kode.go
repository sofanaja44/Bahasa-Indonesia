package mesin

// Op adalah instruksi bytecode.
type Op uint8

const (
	opKonstanta            Op = iota // A: indeks konstanta
	opKosong                         // dorong kosong
	opBenar                          // dorong benar
	opSalah                          // dorong salah
	opBuang                          // buang nilai teratas
	opSalin                          // salin nilai teratas
	opAmbil                          // A: simbol; dorong nilai variabel
	opDefinisikan                    // A: simbol, B: 1 = tetap; definisikan di lingkup saat ini
	opSetel                          // A: simbol; ubah variabel yang sudah ada
	opLingkupMasuk                   // buat lingkup anak
	opLingkupKeluar                  // kembali ke lingkup induk
	opBiner                          // A: kode operator
	opBukan                          // bukan x
	opNegasi                         // -x
	opLompat                         // A: tujuan
	opLompatSalah                    // A: tujuan bila nilai teratas salah (nilai dibuang)
	opLompatSalahAtauBuang           // A: 'dan' — lompat dan simpan nilai bila salah, selain itu buang
	opLompatBenarAtauBuang           // A: 'atau' — lompat dan simpan nilai bila benar, selain itu buang
	opPanggil                        // A: jumlah argumen, B: konstanta nama pemanggilan
	opKembalikan                     // kembalikan nilai teratas
	opDaftar                         // A: jumlah elemen
	opKamus                          // A: jumlah pasangan
	opAmbilIndeks                    // objek[indeks]
	opSetelIndeks                    // [nilai, objek, indeks] → objek[indeks] = nilai
	opIrisan                         // A: bit 1 = ada awal, bit 2 = ada akhir
	opAmbilAtribut                   // A: konstanta nama
	opSetelAtribut                   // A: konstanta nama; [nilai, objek]
	opTampilkan                      // A: jumlah nilai, B: 1 = pindah baris
	opTunggu                         // A: konstanta faktor
	opWaktu                          // A: konstanta bagian
	opAcak                           // [minimum, maksimum]
	opTanya                          // A: 0 = teks, 1 = angka
	opKeTeks                         // nilai → teks tampilan
	opGabungTeks                     // A: jumlah teks
	opGalat                          // A: konstanta *Kesalahan; lempar
	opFungsi                         // A: konstanta *KodeFungsi; buat closure
	opKelas                          // A: konstanta *KodeKelas
	opImpor                          // A: konstanta nama modul, B: konstanta alias (-1 bila tidak ada)
	opDariImpor                      // A: konstanta [3]string{modul, nama, alias}
	opKonversi                       // A: konstanta nama tipe (bilangan/desimal/teks/logika)
	opTambahkan                      // A: tujuan bila nilai sudah dimasukkan ke daftar
	opUntukSiapkan                   // [dari, sampai, langkah] → periksa jenisnya
	opUntukCek                       // A: tujuan bila perulangan selesai
	opUntukNilai                     // dorong nilai penghitung
	opUntukLangkah                   // penghitung += langkah
	opIterBuat                       // nilai → penelusur
	opIterLanjut                     // A: tujuan bila habis; selain itu dorong isi berikutnya
	opKaliSiapkan                    // jumlah → penghitung
	opKaliLanjut                     // A: tujuan bila habis
	opCobaMulai                      // A: alamat penangan
	opCobaSelesai                    // lepas penangan teratas
	opCocokTangkap                   // A: konstanta jenis, B: tujuan bila tidak cocok
	opTeksKesalahan                  // kesalahan → TeksKesalahan
	opLemparUlang                    // lempar ulang kesalahan teratas
	opLempar                         // lempar nilai sebagai KesalahanNilai
	opSimpanHasil                    // simpan nilai teratas sebagai hasil (REPL)
	opBuangN                         // A: jumlah nilai yang dibuang
	opLingkupBersihkan               // kosongkan lingkup saat ini (lingkup perulangan yang dipakai ulang)
)

// Kode operator untuk opBiner.
const (
	biTambah = iota
	biKurang
	biKali
	biBagi
	biSisa
	biPangkat
	biSama
	biTidakSama
	biLebih
	biKurangDari
	biLebihSama
	biKurangSama
	biAdaDalam
	biTidakAdaDalam
)

var kodeOperator = map[string]int{
	"+": biTambah, "-": biKurang, "*": biKali, "/": biBagi, "%": biSisa, "**": biPangkat,
	"==": biSama, "!=": biTidakSama, ">": biLebih, "<": biKurangDari, ">=": biLebihSama,
	"<=": biKurangSama, "ada dalam": biAdaDalam, "tidak ada dalam": biTidakAdaDalam,
}

var namaOperator = func() map[int]string {
	m := map[int]string{}
	for s, k := range kodeOperator {
		m[k] = s
	}
	return m
}()

type instruksi struct {
	op           Op
	a, b         int32
	baris, kolom int32
}

// Kode adalah hasil kompilasi satu fungsi atau program.
type Kode struct {
	Nama      string
	ins       []instruksi
	konstanta []any
}

// KodeFungsi adalah fungsi yang belum terikat lingkup.
type KodeFungsi struct {
	Nama      string
	Parameter []string
	simbol    []int32
	Bawaan    []*Kode // nilai bawaan parameter, dihitung saat pemanggilan (nil bila tidak ada)
	Kode      *Kode
	// daurUlang: isi fungsi tidak membuat fungsi/kelas, jadi lingkup pemanggilannya tidak mungkin
	// ditangkap closure dan boleh dipakai ulang setelah fungsi selesai.
	daurUlang bool
}

// Fungsi adalah fungsi buatan pengguna beserta lingkup tempat ia dibuat (closure).
type Fungsi struct {
	Nama    string
	proto   *KodeFungsi
	lingkup *Lingkup
	Kelas   *Kelas // kelas pemilik bila fungsi ini metode
}

type anggotaKelas struct {
	nama   string
	metode bool
}

// KodeKelas menjelaskan susunan nilai di tumpukan untuk opKelas.
type KodeKelas struct {
	Nama     string
	AdaInduk bool
	Anggota  []anggotaKelas
}
