// Perintah indonesia menjalankan program Bahasa Pemrograman Indonesia.
//
//	indonesia program.id         # Jalankan berkas .id
//	indonesia repl               # Masuk ke mode interaktif (REPL)
//	indonesia -e "tampilkan 42"  # Jalankan kode langsung
package main

import (
	"bufio"
	"errors"
	"fmt"
	"io"
	"os"
	"os/signal"
	"strings"
	"sync"
	"syscall"
	"time"
	"unicode/utf8"

	"github.com/sofanaja44/Bahasa-Indonesia/mesin"
)

const bantuan = `
indonesia — Bahasa Pemrograman Indonesia.

Penggunaan:
    indonesia program.id         # Jalankan berkas .id
    indonesia repl               # Masuk ke mode interaktif (REPL)
    indonesia -e "tampilkan 42"  # Jalankan kode langsung
    indonesia bantu              # Tampilkan bantuan ini
    indonesia versi              # Tampilkan versi
`

var banner = `
╔════════════════════════════════════════════╗
║  🇮🇩  Bahasa Pemrograman Indonesia v` + mesin.Versi + `  ║
║  Ketik 'keluar' untuk keluar              ║
╚════════════════════════════════════════════╝
Blok (jika, selama, fungsi, ...) diakhiri dengan baris kosong.
`

// ---- Keluaran ----

// keluaran menulis ke layar. Bila layar bukan terminal (dialihkan ke berkas atau pipa),
// tulisan ditampung dulu agar cepat, dan dikirim sebelum membaca masukan, menunggu, atau keluar.
type keluaran struct {
	mu  sync.Mutex
	buf *bufio.Writer
}

func adalahTerminal(f *os.File) bool {
	info, err := f.Stat()
	return err == nil && info.Mode()&os.ModeCharDevice != 0
}

func keluaranBaru() *keluaran {
	ukuran := 64 << 10
	if adalahTerminal(os.Stdout) {
		ukuran = 0
	}
	if ukuran == 0 {
		return &keluaran{}
	}
	return &keluaran{buf: bufio.NewWriterSize(os.Stdout, ukuran)}
}

func (k *keluaran) tulis(s string) {
	k.mu.Lock()
	defer k.mu.Unlock()
	var err error
	if k.buf != nil {
		_, err = k.buf.WriteString(s)
	} else {
		_, err = os.Stdout.WriteString(s)
	}
	if err != nil {
		os.Exit(1) // keluaran dipotong, mis. dialirkan ke 'head': berhenti tanpa pesan
	}
}

func (k *keluaran) kirim() {
	k.mu.Lock()
	defer k.mu.Unlock()
	if k.buf != nil && k.buf.Flush() != nil {
		os.Exit(1)
	}
}

// ---- Masukan ----

var errBatal = errors.New("dibatalkan")

// masukan membaca baris dari stdin di goroutine terpisah, agar menunggu masukan bisa dibatalkan Ctrl+C.
type masukan struct {
	sekali sync.Once
	baris  chan string
}

func (m *masukan) mulai() {
	m.baris = make(chan string)
	go func() {
		pembaca := bufio.NewReader(os.Stdin)
		for {
			s, err := pembaca.ReadString('\n')
			if s != "" {
				s = strings.TrimSuffix(strings.TrimSuffix(s, "\n"), "\r")
				m.baris <- s
			}
			if err != nil {
				close(m.baris)
				return
			}
		}
	}()
}

// baca menunggu satu baris; io.EOF bila masukan habis, errBatal bila Ctrl+C ditekan.
func (m *masukan) baca(h *henti) (string, error) {
	m.sekali.Do(m.mulai)
	select {
	case s, ok := <-m.baris:
		if !ok {
			return "", io.EOF
		}
		return s, nil
	case <-h.saluran():
		return "", errBatal
	}
}

// ---- Ctrl+C ----

type henti struct {
	mu    sync.Mutex
	aktif bool
	ch    chan struct{}
}

func (h *henti) minta() {
	h.mu.Lock()
	defer h.mu.Unlock()
	if !h.aktif {
		h.aktif = true
		close(h.ch)
	}
}

func (h *henti) diminta() bool {
	h.mu.Lock()
	defer h.mu.Unlock()
	return h.aktif
}

func (h *henti) saluran() <-chan struct{} {
	h.mu.Lock()
	defer h.mu.Unlock()
	return h.ch
}

func (h *henti) aturUlang() {
	h.mu.Lock()
	defer h.mu.Unlock()
	h.aktif = false
	h.ch = make(chan struct{})
}

// ---- Program ----

type cli struct {
	keluar  *keluaran
	masuk   *masukan
	henti   *henti
	interak bool // mode REPL
}

func (c *cli) io() mesin.IO {
	return mesin.IO{
		Tulis: c.keluar.tulis,
		Baca: func(prompt string) (string, bool) {
			c.keluar.tulis(prompt)
			c.keluar.kirim()
			s, err := c.masuk.baca(c.henti)
			return s, err == nil
		},
		Tidur: func(detik float64) {
			c.keluar.kirim()
			if detik <= 0 {
				return
			}
			select {
			case <-time.After(time.Duration(detik * float64(time.Second))):
			case <-c.henti.saluran():
			}
		},
		Berhenti: c.henti.diminta,
	}
}

func (c *cli) keluarDengan(kode int) {
	c.keluar.kirim()
	os.Exit(kode)
}

func (c *cli) jalankan(kode string) {
	err := mesin.Baru(c.io()).Jalankan(kode)
	if err == nil {
		c.keluarDengan(0)
	}
	c.keluar.kirim()
	var k *mesin.Kesalahan
	switch {
	case errors.As(err, &k):
		fmt.Fprintln(os.Stderr, k.Teks())
		os.Exit(1)
	case errors.Is(err, mesin.ErrDihentikan):
		fmt.Fprintln(os.Stderr, "\nProgram dihentikan.")
		os.Exit(130)
	default:
		fmt.Fprintf(os.Stderr, "❌ Kesalahan internal: %v\n", err)
		fmt.Fprintln(os.Stderr, "   Ini kemungkinan besar bug pada interpreter. Mohon laporkan di GitHub.")
		os.Exit(1)
	}
}

func (c *cli) jalankanBerkas(jalur string) {
	info, err := os.Stat(jalur)
	if err != nil {
		c.keluar.tulis("❌ Berkas tidak ditemukan: '" + jalur + "'\n")
		c.keluarDengan(1)
	}
	if info.IsDir() {
		c.keluar.tulis("❌ '" + jalur + "' adalah folder, bukan berkas program\n")
		c.keluarDengan(1)
	}
	isi, err := os.ReadFile(jalur)
	if err != nil {
		c.keluar.tulis("❌ Berkas tidak bisa dibaca: '" + jalur + "'\n")
		c.keluarDengan(1)
	}
	if !utf8.Valid(isi) {
		c.keluar.tulis("❌ Berkas '" + jalur + "' bukan teks UTF-8\n")
		c.keluarDengan(1)
	}
	kode := strings.TrimPrefix(string(isi), "\uFEFF") // BOM dari sebagian editor di Windows
	kode = strings.ReplaceAll(strings.ReplaceAll(kode, "\r\n", "\n"), "\r", "\n")
	c.jalankan(kode)
}

// bacaPerintah membaca satu perintah REPL; bila belum lengkap, terus baca sampai baris kosong.
func (c *cli) bacaPerintah() (string, error) {
	c.keluar.tulis(">>> ")
	c.keluar.kirim()
	kode, err := c.masuk.baca(c.henti)
	if err != nil {
		return "", err
	}
	if mesin.PotongSpasi(kode) != "" && mesin.BelumSelesai(kode) {
		for {
			c.keluar.tulis("... ")
			c.keluar.kirim()
			lanjutan, err := c.masuk.baca(c.henti)
			if err != nil {
				return "", err
			}
			if mesin.PotongSpasi(lanjutan) == "" {
				break
			}
			kode += "\n" + lanjutan
		}
	}
	return kode, nil
}

func (c *cli) modeInteraktif() {
	c.interak = true
	c.keluar.tulis(banner + "\n")
	m := mesin.Baru(c.io())
	for {
		kode, err := c.bacaPerintah()
		if err == io.EOF {
			c.keluar.tulis("\nSampai jumpa! 👋\n")
			break
		}
		if err == errBatal {
			c.keluar.tulis("\n(dibatalkan)\n")
			c.henti.aturUlang()
			continue
		}
		perintah := mesin.PotongSpasi(kode)
		if perintah == "" {
			continue
		}
		if perintah == "keluar" || perintah == "exit" || perintah == "quit" {
			c.keluar.tulis("Sampai jumpa! 👋\n")
			break
		}
		hasil, ada, err := m.JalankanREPL(kode)
		var k *mesin.Kesalahan
		switch {
		case err == nil:
			if ada && hasil != nil {
				c.keluar.tulis(mesin.KeTeks(hasil) + "\n") // benar/salah/kosong, bukan true/false/nil
			}
		case errors.As(err, &k):
			c.keluar.tulis(k.Teks() + "\n")
		case errors.Is(err, mesin.ErrDihentikan):
			c.keluar.tulis("\nDihentikan.\n")
			c.henti.aturUlang()
		default:
			c.keluar.tulis("❌ Kesalahan internal: " + err.Error() + "\n")
		}
	}
	c.keluarDengan(0)
}

func main() {
	c := &cli{keluar: keluaranBaru(), masuk: &masukan{}, henti: &henti{ch: make(chan struct{})}}

	sinyal := make(chan os.Signal, 1)
	signal.Notify(sinyal, os.Interrupt, syscall.SIGPIPE)
	go func() {
		for s := range sinyal {
			if s == syscall.SIGPIPE {
				continue // penulisan yang gagal ditangani di keluaran.tulis
			}
			c.henti.minta()
		}
	}()

	args := os.Args[1:]
	if len(args) == 0 || args[0] == "repl" {
		c.modeInteraktif()
		return
	}
	switch args[0] {
	case "versi", "--versi", "--version", "-v":
		c.keluar.tulis("Indonesia v" + mesin.Versi + "\n")
		c.keluarDengan(0)
	case "bantu", "bantuan", "--bantu", "--bantuan", "--help", "-h":
		c.keluar.tulis(bantuan + "\n")
		c.keluarDengan(0)
	case "-e", "--eval":
		if len(args) > 1 {
			c.jalankan(args[1])
		}
	}
	c.jalankanBerkas(args[0])
}
