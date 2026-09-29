"""
builtins.py — Fungsi bawaan (built-in) untuk bahasa pemrograman Indonesia.
"""

import time
from datetime import datetime

from src.bk_types import BKDaftar, BKKamus


def daftar_fungsi_bawaan() -> dict:
    """Kembalikan dictionary fungsi bawaan."""
    return {
        # I/O
        "tampilkan": _tampilkan,
        "cetak": _cetak,
        "tulis": _tampilkan,
        "masukan": _masukan,
        "masukan_angka": _masukan_angka,
        "masukan_desimal": _masukan_desimal,
        # Konversi tipe
        "ubah_angka": lambda x: int(x) if not isinstance(x, bool) else int(x),
        "ubah_desimal": lambda x: float(x),
        "ubah_teks": lambda x: _ke_teks(x),
        "ubah_logika": lambda x: bool(x),
        # Utilitas
        "panjang": _panjang,
        "jenis": _jenis,
        "rentang": _rentang,
        "mutlak": lambda x: abs(x),
        "maksimum": lambda *args: max(args) if len(args) > 1 else max(args[0]) if isinstance(args[0], (list, BKDaftar)) else args[0],
        "minimum": lambda *args: min(args) if len(args) > 1 else min(args[0]) if isinstance(args[0], (list, BKDaftar)) else args[0],
        "jumlah": lambda x: sum(x.elemen if isinstance(x, BKDaftar) else x),
        "diurutkan": lambda x: BKDaftar(sorted(x.elemen if isinstance(x, BKDaftar) else x)),
        "dibalik": lambda x: BKDaftar(list(reversed(x.elemen if isinstance(x, BKDaftar) else x))),
        # Waktu (bentuk natural: "tunggu 1 detik")
        "tunggu": lambda detik: tunggu(detik),
        # Pesan kesalahan untuk 'lempar': lempar Kesalahan("Pembagi tidak boleh nol!")
        "Kesalahan": _kesalahan,
        "Error": _kesalahan,
    }


def _ke_teks(nilai) -> str:
    """Konversi nilai ke representasi teks."""
    if nilai is None:
        return "kosong"
    if isinstance(nilai, bool):
        return "benar" if nilai else "salah"
    if isinstance(nilai, BKDaftar):
        items = ", ".join(_ke_teks(e) for e in nilai.elemen)
        return f"[{items}]"
    if isinstance(nilai, BKKamus):
        pairs = ", ".join(f"{_ke_teks(k)}: {_ke_teks(v)}" for k, v in nilai.data.items())
        return "{" + pairs + "}"
    if isinstance(nilai, str):
        return nilai
    return str(nilai)


def _tampilkan(*args):
    """Print dengan newline."""
    print(" ".join(_ke_teks(a) for a in args))


def _cetak(*args):
    """Print tanpa newline."""
    print(" ".join(_ke_teks(a) for a in args), end="")


def _kesalahan(pesan=""):
    """Buat pesan kesalahan; 'lempar' mengubahnya menjadi error yang bisa ditangkap."""
    return _ke_teks(pesan)


def baca_waktu(bagian: str):
    """Nilai 'jam/menit/detik sekarang' (angka) atau 'waktu sekarang' (teks "JJ:MM:DD")."""
    sekarang = datetime.now()
    if bagian == "jam":
        return sekarang.hour
    if bagian == "menit":
        return sekarang.minute
    if bagian == "detik":
        return sekarang.second
    return sekarang.strftime("%H:%M:%S")


def tunggu(lama, faktor=1):
    """Berhenti sejenak selama `lama` × `faktor` detik."""
    if isinstance(lama, bool) or not isinstance(lama, (int, float)):
        raise ValueError(f"'tunggu' membutuhkan angka sebagai lamanya menunggu, bukan '{_ke_teks(lama)}'")
    if lama < 0:
        raise ValueError("Lama menunggu tidak boleh negatif")
    time.sleep(lama * faktor)


def _masukan(prompt=""):
    """Input string."""
    return input(_ke_teks(prompt) if prompt else "")


def _masukan_angka(prompt=""):
    """Input integer."""
    return int(input(_ke_teks(prompt) if prompt else ""))


def _masukan_desimal(prompt=""):
    """Input float."""
    return float(input(_ke_teks(prompt) if prompt else ""))


def _panjang(x):
    """Kembalikan panjang objek."""
    if isinstance(x, BKDaftar):
        return len(x.elemen)
    if isinstance(x, BKKamus):
        return len(x.data)
    if isinstance(x, str):
        return len(x)
    raise TypeError(f"Tidak bisa menghitung panjang tipe {type(x).__name__}")


def _jenis(x) -> str:
    """Kembalikan nama tipe data dalam Bahasa Indonesia."""
    if x is None:
        return "kosong"
    if isinstance(x, bool):
        return "logika"
    if isinstance(x, int):
        return "bilangan"
    if isinstance(x, float):
        return "desimal"
    if isinstance(x, str):
        return "teks"
    if isinstance(x, BKDaftar):
        return "daftar"
    if isinstance(x, BKKamus):
        return "kamus"
    return "objek"


def _rentang(*args):
    """Buat daftar angka (seperti range)."""
    if len(args) == 1:
        return BKDaftar(list(range(args[0])))
    if len(args) == 2:
        return BKDaftar(list(range(args[0], args[1])))
    if len(args) == 3:
        return BKDaftar(list(range(args[0], args[1], args[2])))
    raise ValueError("rentang membutuhkan 1-3 argumen")
