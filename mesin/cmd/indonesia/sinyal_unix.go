//go:build unix

package main

import (
	"os"
	"syscall"
)

// sinyalDiabaikan: SIGPIPE ditangkap agar penulisan ke pipa yang sudah ditutup (mis. ke 'head')
// gagal biasa dan ditangani keluaran.tulis, bukan menghentikan program dengan sinyal.
var sinyalDiabaikan = []os.Signal{syscall.SIGPIPE}
