"""
jembatan.py — Penghubung interpreter Bahasa Indonesia dengan editor web.

Berjalan di Pyodide (Python dalam WebAssembly) di dalam Web Worker. Keluaran,
masukan (tanya), dan tunggu diteruskan ke fungsi JavaScript di pekerja.js:

    tulisKeluaran(saluran, teks) -> bool   benar bila tombol Hentikan ditekan
    mintaMasukan() -> str (JSON)           {"teks": ...}, {"berhenti": true}, atau {"gagal": pesan}
    tidur(milidetik) -> bool               benar bila tombol Hentikan ditekan
"""

import builtins
import json
import sys
import time

import js

from src.errors import KesalahanIndonesia, KesalahanNilai
from src.interpreter import Interpreter
from src.lexer import tokenisasi
from src.parser import parse


class ProgramDihentikan(KeyboardInterrupt):
    """Tombol Hentikan ditekan. Turunan KeyboardInterrupt, jadi tidak bisa ditangkap 'coba'."""


def _periksa(berhenti) -> None:
    if berhenti:
        raise ProgramDihentikan


class _Saluran:
    """Pengganti sys.stdout dan sys.stderr yang mengirim teks ke halaman editor."""

    encoding = "utf-8"

    def __init__(self, nama: str):
        self.nama = nama

    def write(self, teks: str) -> int:
        _periksa(js.tulisKeluaran(self.nama, teks))
        return len(teks)

    def flush(self) -> None:
        pass

    def isatty(self) -> bool:
        return False


def _masukan(pertanyaan="") -> str:
    if pertanyaan:
        sys.stdout.write(str(pertanyaan))
    jawaban = json.loads(js.mintaMasukan())
    if jawaban.get("berhenti"):
        raise ProgramDihentikan
    if "gagal" in jawaban:
        raise KesalahanNilai(jawaban["gagal"])
    return jawaban["teks"]


def _tidur(detik) -> None:
    _periksa(js.tidur(max(0.0, float(detik)) * 1000))


sys.stdout = _Saluran("keluaran")
sys.stderr = _Saluran("galat")
builtins.input = _masukan
time.sleep = _tidur


def jalankan(kode: str) -> str:
    """Jalankan satu program. Hasilnya JSON: {} bila berhasil, selain itu keterangan kesalahannya."""
    try:
        Interpreter().jalankan(parse(tokenisasi(kode), kode))
    except KesalahanIndonesia as e:
        return json.dumps({"jenis": type(e).__name__, "pesan": str(e), "baris": e.baris, "kolom": e.kolom})
    except KeyboardInterrupt:
        return json.dumps({"jenis": "dihentikan"})
    except Exception as e:  # kemungkinan besar bug pada interpreter
        return json.dumps({"jenis": "internal", "pesan": f"{type(e).__name__}: {e}"})
    return "{}"
