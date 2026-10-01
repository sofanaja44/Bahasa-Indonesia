package mesin

import "testing"

// Tolok ukur kecepatan mesin: go test -run XXX -bench .
var programTolokUkur = map[string]string{
	"Fibonacci": `fungsi fib(n):
    jika n < 2:
        kembalikan n
    kembalikan fib(n - 1) + fib(n - 2)
tampilkan fib(22)
`,
	"Perulangan": `buat total adalah 0
untuk i dari 1 sampai 200000:
    tambahkan i ke total
tampilkan total
`,
	"Prima": `fungsi prima(n):
    jika n < 2:
        kembalikan salah
    buat i adalah 2
    selama i * i <= n:
        jika n habis dibagi i:
            kembalikan salah
        tambahkan 1 ke i
    kembalikan benar
buat hitung adalah 0
untuk x dari 1 sampai 20000:
    jika prima(x):
        tambahkan 1 ke hitung
tampilkan hitung
`,
	"DaftarKamus": `buat d adalah []
untuk i dari 1 sampai 50000:
    d.tambahkan(i * i % 1000)
buat k adalah {}
untuk setiap x dalam d:
    jika x ada dalam k:
        k[x] adalah k[x] + 1
    selainnya:
        k[x] adalah 1
tampilkan panjang(k), jumlah(d)
`,
	"TeksFormat": `buat kata adalah []
untuk i dari 1 sampai 20000:
    kata.tambahkan(format"angka {i} kuadrat {i * i}")
tampilkan panjang(kata.gabung(","))
`,
}

func BenchmarkProgram(b *testing.B) {
	for nama, kode := range programTolokUkur {
		b.Run(nama, func(b *testing.B) {
			for i := 0; i < b.N; i++ {
				if err := Baru(IO{Tulis: func(string) {}}).Jalankan(kode); err != nil {
					b.Fatal(err)
				}
			}
		})
	}
}
