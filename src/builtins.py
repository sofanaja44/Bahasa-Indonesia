"""
builtins.py — Fungsi bawaan (built-in) untuk bahasa pemrograman Indonesia.

Fungsi di sini melempar KesalahanNilai/KesalahanTipe berbahasa Indonesia;
interpreter menambahkan nomor baris dan kolom pemanggilnya.
"""

import math
import time
from datetime import datetime

from src.bk_types import BKDaftar, BKKamus, BKFungsi, BKKelas, BKInstansi, BKModul, BKMetodeTerikat
from src.errors import KesalahanNilai, KesalahanTipe

NAMA_HARI = ["Senin", "Selasa", "Rabu", "Kamis", "Jumat", "Sabtu", "Minggu"]
NAMA_BULAN = [
    "Januari", "Februari", "Maret", "April", "Mei", "Juni",
    "Juli", "Agustus", "September", "Oktober", "November", "Desember",
]


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
        "tanya": lambda pertanyaan="": tanya(pertanyaan),  # bentuk natural: tanya "Siapa namamu?"
        # Konversi tipe
        "ubah_angka": _ubah_angka,
        "ubah_desimal": _ubah_desimal,
        "ubah_teks": lambda x: _ke_teks(x),
        "ubah_logika": lambda x: bool(x),
        # Utilitas
        "panjang": _panjang,
        "jenis": _jenis,
        "rentang": _rentang,
        "mutlak": lambda x: abs(_pastikan_angka(x, "mutlak")),
        "maksimum": lambda *args: _ekstrem(max, "maksimum", args),
        "minimum": lambda *args: _ekstrem(min, "minimum", args),
        "jumlah": _jumlah,
        "diurutkan": _diurutkan,
        "dibalik": lambda x: BKDaftar(list(reversed(_isi_koleksi(x, "dibalik")))),
        # Waktu (bentuk natural: "tunggu 1 detik")
        "tunggu": lambda detik: tunggu(detik),
        # Pesan kesalahan untuk 'lempar': lempar Kesalahan("Pembagi tidak boleh nol!")
        "Kesalahan": _kesalahan,
        "Error": _kesalahan,
    }


# ============================================================
# Tampilan nilai
# ============================================================

def _ke_teks(nilai) -> str:
    """Konversi nilai ke representasi teks."""
    if nilai is None:
        return "kosong"
    if isinstance(nilai, bool):
        return "benar" if nilai else "salah"
    if isinstance(nilai, float):
        return _teks_desimal(nilai)
    if isinstance(nilai, BKDaftar):
        items = ", ".join(_ke_teks(e) for e in nilai.elemen)
        return f"[{items}]"
    if isinstance(nilai, BKKamus):
        pairs = ", ".join(f"{_ke_teks(k)}: {_ke_teks(v)}" for k, v in nilai.data.items())
        return "{" + pairs + "}"
    if isinstance(nilai, str):
        return nilai
    if callable(nilai):
        return "<fungsi bawaan>"
    return str(nilai)


def _teks_desimal(x: float) -> str:
    """5.0 tampil "5"; galat pembulatan kecil dibuang: 0.1 + 0.2 tampil "0.3"."""
    x = float(f"{x:.12g}")
    if x.is_integer():
        return str(int(x))
    return repr(x)


def teks_ke_angka(teks: str):
    """"12" → 12, "3.5" atau "3,5" → 3.5. None jika teks bukan angka."""
    t = teks.strip()
    if "," in t and "." not in t:
        t = t.replace(",", ".")  # koma desimal ala Indonesia
    try:
        return int(t)
    except ValueError:
        pass
    try:
        x = float(t)
    except ValueError:
        return None
    return x if math.isfinite(x) else None


# ============================================================
# Validasi
# ============================================================

def _pastikan_angka(x, nama: str):
    if isinstance(x, bool) or not isinstance(x, (int, float)):
        raise KesalahanTipe(f"'{nama}' membutuhkan angka, bukan '{_ke_teks(x)}'")
    return x


def _isi_koleksi(x, nama: str) -> list:
    if isinstance(x, BKDaftar):
        return x.elemen
    if isinstance(x, str):
        return list(x)
    raise KesalahanTipe(f"'{nama}' membutuhkan daftar, bukan '{_ke_teks(x)}'")


# ============================================================
# I/O
# ============================================================

def _tampilkan(*args):
    """Print dengan newline."""
    print(" ".join(_ke_teks(a) for a in args))


def _cetak(*args):
    """Print tanpa newline."""
    print(" ".join(_ke_teks(a) for a in args), end="", flush=True)


def _baca_masukan(prompt) -> str:
    try:
        return input(_ke_teks(prompt) if prompt else "")
    except EOFError:
        raise KesalahanNilai("Tidak ada lagi masukan yang bisa dibaca")


def _masukan(prompt=""):
    """Input string."""
    return _baca_masukan(prompt)


def _masukan_angka(prompt=""):
    """Input bilangan bulat."""
    teks = _baca_masukan(prompt)
    angka = teks_ke_angka(teks)
    if isinstance(angka, float) and angka.is_integer():
        angka = int(angka)
    if not isinstance(angka, int):
        raise KesalahanNilai(f"Masukan '{teks}' bukan bilangan bulat")
    return angka


def _masukan_desimal(prompt=""):
    """Input angka desimal."""
    teks = _baca_masukan(prompt)
    angka = teks_ke_angka(teks)
    if angka is None:
        raise KesalahanNilai(f"Masukan '{teks}' bukan angka")
    return float(angka)


def tanya(pertanyaan, jenis: str = "teks"):
    """'tanya "Siapa namamu?"' (teks) / 'tanya angka "Berapa umurmu?"' (angka).

    Untuk angka, pertanyaan diulang sampai jawabannya benar-benar angka.
    """
    while True:
        jawaban = _baca_masukan(pertanyaan)
        if jenis == "teks":
            return jawaban
        angka = teks_ke_angka(jawaban)
        if angka is not None:
            return angka
        print("Tolong jawab dengan angka.")


# ============================================================
# Konversi
# ============================================================

def _ubah_angka(x):
    if isinstance(x, bool):
        return int(x)
    if isinstance(x, (int, float)):
        return int(x)
    if isinstance(x, str):
        angka = teks_ke_angka(x)
        if isinstance(angka, int):
            return angka
        if isinstance(angka, float):
            raise KesalahanNilai(f"'{x}' bukan bilangan bulat; gunakan ubah_desimal")
    raise KesalahanNilai(f"Tidak bisa mengubah '{_ke_teks(x)}' menjadi bilangan")


def _ubah_desimal(x):
    if isinstance(x, (int, float)):
        return float(x)
    if isinstance(x, str):
        angka = teks_ke_angka(x)
        if angka is not None:
            return float(angka)
    raise KesalahanNilai(f"Tidak bisa mengubah '{_ke_teks(x)}' menjadi angka desimal")


# ============================================================
# Utilitas
# ============================================================

def _kesalahan(pesan=""):
    """Buat pesan kesalahan; 'lempar' mengubahnya menjadi error yang bisa ditangkap."""
    return _ke_teks(pesan)


def _panjang(x):
    """Kembalikan panjang objek."""
    if isinstance(x, BKDaftar):
        return len(x.elemen)
    if isinstance(x, BKKamus):
        return len(x.data)
    if isinstance(x, str):
        return len(x)
    raise KesalahanTipe(f"Tidak bisa menghitung panjang {_jenis(x)}")


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
    if isinstance(x, BKKelas):
        return "kelas"
    if isinstance(x, BKModul):
        return "modul"
    if isinstance(x, BKInstansi):
        return "objek"
    if isinstance(x, (BKFungsi, BKMetodeTerikat)) or callable(x):
        return "fungsi"
    return "objek"


def _rentang(*args):
    """Buat daftar angka (seperti range)."""
    if not 1 <= len(args) <= 3:
        raise KesalahanNilai("rentang membutuhkan 1 sampai 3 angka, mis. rentang(1, 10)")
    for a in args:
        if isinstance(a, bool) or not isinstance(a, int):
            raise KesalahanTipe(f"rentang membutuhkan bilangan bulat, bukan '{_ke_teks(a)}'")
    if len(args) == 3 and args[2] == 0:
        raise KesalahanNilai("Langkah rentang tidak boleh nol")
    return BKDaftar(list(range(*args)))


def _ekstrem(fungsi, nama: str, args: tuple):
    """maksimum(3, 7) / maksimum([3, 7])"""
    isi = list(args)
    if len(isi) == 1 and isinstance(isi[0], BKDaftar):
        isi = isi[0].elemen
    if not isi:
        raise KesalahanNilai(f"'{nama}' membutuhkan paling sedikit satu nilai")
    try:
        return fungsi(isi)
    except TypeError:
        raise KesalahanTipe(f"'{nama}' tidak bisa membandingkan nilai yang jenisnya berbeda-beda")


def _jumlah(x):
    isi = _isi_koleksi(x, "jumlah")
    for e in isi:
        _pastikan_angka(e, "jumlah")
    return sum(isi)


def _diurutkan(x):
    try:
        return BKDaftar(sorted(_isi_koleksi(x, "diurutkan")))
    except TypeError:
        raise KesalahanTipe("Isi daftar tidak bisa diurutkan karena jenis datanya berbeda-beda")


# ============================================================
# Waktu
# ============================================================

def baca_waktu(bagian: str):
    """Nilai untuk frasa waktu natural.

    jam/menit/detik sekarang → angka, waktu sekarang → "JJ:MM:DD",
    hari ini → "Kamis", tanggal hari ini → "1 Oktober 2026",
    bulan ini → "Oktober", tahun ini → 2026.
    """
    sekarang = datetime.now()
    if bagian == "jam":
        return sekarang.hour
    if bagian == "menit":
        return sekarang.minute
    if bagian == "detik":
        return sekarang.second
    if bagian == "hari":
        return NAMA_HARI[sekarang.weekday()]
    if bagian == "tanggal":
        return f"{sekarang.day} {NAMA_BULAN[sekarang.month - 1]} {sekarang.year}"
    if bagian == "bulan":
        return NAMA_BULAN[sekarang.month - 1]
    if bagian == "tahun":
        return sekarang.year
    return sekarang.strftime("%H:%M:%S")


def tunggu(lama, faktor=1):
    """Berhenti sejenak selama `lama` × `faktor` detik."""
    if isinstance(lama, bool) or not isinstance(lama, (int, float)):
        raise KesalahanNilai(f"'tunggu' membutuhkan angka sebagai lamanya menunggu, bukan '{_ke_teks(lama)}'")
    if lama < 0:
        raise KesalahanNilai("Lama menunggu tidak boleh negatif")
    time.sleep(lama * faktor)
