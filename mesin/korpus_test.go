package mesin

import (
	"encoding/json"
	"os"
	"strings"
	"testing"
	"time"
)

// Korpus pembanding dibuat dari interpreter Python (testdata/buat_korpus.py). Mesin Go harus
// menghasilkan tampilan layar, pesan kesalahan, dan nilai terakhir yang sama persis.

type kasusKorpus struct {
	Nama      string   `json:"nama"`
	Kode      string   `json:"kode"`
	Masukan   []string `json:"masukan"`
	Keluaran  string   `json:"keluaran"`
	Kesalahan *string  `json:"kesalahan"`
	Hasil     *string  `json:"hasil"`
	Internal  bool     `json:"internal"`
}

// Sama dengan nilai di testdata/buat_korpus.py.
var masukanKorpus = []string{"42", "Budi", "7", "3,5", "tidak", "ya", "0", "100", "-5", "abc", "", "10"}

const benihKorpus = 12345

type hasilJalan struct {
	keluaran  string
	kesalahan *string
	hasil     *string
}

// jalankanTetap menjalankan kode dalam keadaan yang bisa diulang (benih, jam, masukan tetap).
func jalankanTetap(t testing.TB, kode string, masukan []string) hasilJalan {
	var layar strings.Builder
	sisa := append([]string(nil), masukan...)
	langkah := 0
	m := Baru(IO{
		Tulis: func(s string) { layar.WriteString(s) },
		Baca: func(prompt string) (string, bool) {
			layar.WriteString(prompt)
			if len(sisa) == 0 {
				return "", false
			}
			s := sisa[0]
			sisa = sisa[1:]
			return s, true
		},
		Tidur:    func(float64) {},
		Sekarang: func() time.Time { return time.Date(2026, 10, 1, 14, 30, 45, 0, time.Local) },
		Berhenti: func() bool { langkah++; return langkah > 500_000 }, // ±500 juta instruksi
		Berkas:   NewBerkasMemori(),
	})
	m.acak.aturBenih(benihKorpus)
	nilai, ada, err := m.JalankanREPL(kode)
	h := hasilJalan{keluaran: layar.String()}
	switch e := err.(type) {
	case nil:
		if ada && nilai != nil {
			s := keTeks(nilai)
			h.hasil = &s
		}
	case *Kesalahan:
		s := e.Teks()
		h.kesalahan = &s
	default:
		s := "GALAT " + err.Error()
		h.kesalahan = &s
	}
	return h
}

func teksAtauKosong(s *string) string {
	if s == nil {
		return "<tidak ada>"
	}
	return *s
}

func TestKorpusPembanding(t *testing.T) {
	data, err := os.ReadFile("testdata/korpus.json")
	if err != nil {
		t.Fatal(err)
	}
	var korpus []kasusKorpus
	if err := json.Unmarshal(data, &korpus); err != nil {
		t.Fatal(err)
	}
	if len(korpus) < 100 {
		t.Fatalf("korpus terlalu kecil: %d kasus", len(korpus))
	}
	for _, k := range korpus {
		k := k
		t.Run(k.Nama, func(t *testing.T) {
			if k.Internal {
				t.Skip("interpreter Python sendiri gagal di sini")
			}
			masukan := k.Masukan
			if masukan == nil {
				masukan = masukanKorpus
			}
			h := jalankanTetap(t, k.Kode, masukan)
			if h.keluaran != k.Keluaran {
				t.Errorf("keluaran berbeda\nkode:\n%s\n--- Python:\n%s\n--- Go:\n%s", k.Kode, k.Keluaran, h.keluaran)
			}
			if teksAtauKosong(h.kesalahan) != teksAtauKosong(k.Kesalahan) {
				t.Errorf("kesalahan berbeda\nkode:\n%s\n--- Python:\n%s\n--- Go:\n%s", k.Kode,
					teksAtauKosong(k.Kesalahan), teksAtauKosong(h.kesalahan))
			}
			if teksAtauKosong(h.hasil) != teksAtauKosong(k.Hasil) {
				t.Errorf("nilai terakhir berbeda\nkode:\n%s\n--- Python: %s\n--- Go: %s", k.Kode,
					teksAtauKosong(k.Hasil), teksAtauKosong(h.hasil))
			}
		})
	}
}
