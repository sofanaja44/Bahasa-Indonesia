package mesin

// Versi bahasa dan mesin ini.
const Versi = "0.4.0"

// KeTeks mengubah nilai menjadi teks seperti yang ditampilkan 'tampilkan' (benar, kosong, [1, 2], ...).
func KeTeks(v any) string { return keTeks(v) }

// PotongSpasi membuang spasi di awal dan akhir teks (str.strip() Python).
func PotongSpasi(s string) string { return potongSpasi(s) }

// BelumSelesai: apakah kode di REPL belum lengkap, mis. baru menulis 'jika x > 5:' atau 'buat d = ['.
func BelumSelesai(kode string) bool {
	if err := Parsel(kode); err != nil {
		return err.Jenis == KSintaks && err.BelumSelesai
	}
	return false
}

// BuatKesalahan membuat kesalahan tanpa lokasi; dipakai IO (mis. masukan yang gagal dibaca).
// Mesin menambahkan baris dan kolom perintah yang sedang berjalan.
func BuatKesalahan(jenis, pesan string) *Kesalahan { return kesalahanTanpaLokasi(jenis, pesan) }

// AturBenih sama dengan acak.atur_benih(n): deret angka acak berikutnya bisa diulang.
func (m *Mesin) AturBenih(n int64) { m.acak.aturBenih(int(n)) }
