package mesin

// Node AST; sama dengan src/ast_nodes.py.
type Node interface {
	posisi() (int, int)
}

type pos struct{ Baris, Kolom int }

func (p pos) posisi() (int, int) { return p.Baris, p.Kolom }

type (
	NodeAngka struct {
		pos
		Nilai any // int, *big.Int, atau float64
	}
	NodeTeks struct {
		pos
		Nilai string
	}
	NodeTeksFormat struct {
		pos
		Template string
	}
	NodeLogika struct {
		pos
		Nilai bool
	}
	NodeKosong     struct{ pos }
	NodeIdentifier struct {
		pos
		Nama string
	}
	NodeWaktuSekarang struct {
		pos
		Bagian string // jam, menit, detik, waktu, hari, tanggal, bulan, tahun
	}
	NodeAngkaAcak struct {
		pos
		Minimum, Maksimum Node
	}
	NodeTanya struct {
		pos
		Pertanyaan Node
		Jenis      string // "teks" atau "angka"
	}
	NodeOperasiBiner struct {
		pos
		Kiri     Node
		Operator string
		Kanan    Node
	}
	NodeOperasiUnari struct {
		pos
		Operator string
		Operand  Node
	}
	NodeDeklarasiVariabel struct {
		pos
		Nama          string
		Ekspresi      Node
		TipeEksplisit string
	}
	NodeKonstanta struct {
		pos
		Nama     string
		Ekspresi Node
	}
	NodePenugasan struct {
		pos
		Target, Ekspresi Node
	}
	NodePenugasanGabungan struct {
		pos
		Target   Node
		Operator string
		Ekspresi Node
	}
	NodeTambahkan struct {
		pos
		Nilai, Target Node
	}
	NodeTampilkan struct {
		pos
		Ekspresi  []Node
		BarisBaru bool
	}
	NodeTunggu struct {
		pos
		Lama   Node
		Faktor float64
	}
	NodeJika struct {
		pos
		Kondisi       Node
		BlokJika      []Node
		Cabang        []CabangJika
		BlokSelainnya []Node
		AdaSelainnya  bool
	}
	NodePilih struct {
		pos
		Ekspresi  Node
		Kasus     []KasusPilih
		Bawaan    []Node
		AdaBawaan bool
	}
	NodeSelama struct {
		pos
		Kondisi Node
		Blok    []Node
	}
	NodeUntuk struct {
		pos
		Variabel              string
		Dari, Sampai, Langkah Node // Langkah nil bila tidak ditulis
		Blok                  []Node
	}
	NodeUntukSetiap struct {
		pos
		Variabel string
		Iterable Node
		Blok     []Node
	}
	NodeUlangi struct {
		pos
		Blok    []Node
		Kondisi Node
	}
	NodeUlangiKali struct {
		pos
		Jumlah Node
		Blok   []Node
	}
	NodeBerhenti struct{ pos }
	NodeLewati   struct{ pos }
	NodeFungsi   struct {
		pos
		Nama      string
		Parameter []Parameter
		Blok      []Node
	}
	NodeFungsiAnonim struct {
		pos
		Parameter []Parameter
		Ekspresi  Node
	}
	NodePanggilFungsi struct {
		pos
		Fungsi  Node
		Argumen []Node
	}
	NodeKembalikan struct {
		pos
		Ekspresi Node // nil bila tanpa nilai
	}
	NodeDaftar struct {
		pos
		Elemen []Node
	}
	NodeKamus struct {
		pos
		Pasangan [][2]Node
	}
	NodeAksesDaftar struct {
		pos
		Objek, Indeks Node
	}
	NodeIrisanDaftar struct {
		pos
		Objek, Awal, Akhir Node // Awal/Akhir nil bila kosong
	}
	NodeAksesAtribut struct {
		pos
		Objek   Node
		Atribut string
	}
	NodeKelas struct {
		pos
		Nama, Induk string
		AdaInduk    bool
		Blok        []Node
	}
	NodeImpor struct {
		pos
		Modul, Alias string
	}
	NodeDariImpor struct {
		pos
		Modul, Nama, Alias string
	}
	NodeCoba struct {
		pos
		BlokCoba     []Node
		Penangkap    []Penangkap
		BlokAkhirnya []Node
	}
	NodeLempar struct {
		pos
		Ekspresi Node
	}
)

type CabangJika struct {
	Kondisi Node
	Blok    []Node
}

type KasusPilih struct {
	Nilai []Node
	Blok  []Node
}

type Parameter struct {
	Nama   string
	Bawaan Node // nil bila tanpa nilai bawaan
}

type Penangkap struct {
	Jenis, Variabel string // "" bila tidak ditulis
	Blok            []Node
}

type NodeProgram struct {
	Pernyataan []Node
}
