"""
pustaka.py — Pustaka standar (modul bawaan) bahasa pemrograman Indonesia.

Modul dimuat dengan 'impor':

    impor matematika
    tampilkan matematika.akar(16)

    dari acak impor bilangan
    tampilkan bilangan(1, 6)
"""

import math
import os
import random
from decimal import Decimal, ROUND_HALF_UP

from src.bk_types import BKDaftar, BKModul
from src.builtins import _ke_teks, _pastikan_angka, baca_waktu, tunggu
from src.errors import KesalahanBerkas, KesalahanNilai, KesalahanTipe


def _pastikan_bulat(x, nama: str) -> int:
    if isinstance(x, bool) or not isinstance(x, int):
        raise KesalahanTipe(f"'{nama}' membutuhkan bilangan bulat, bukan '{_ke_teks(x)}'")
    return x


# ============================================================
# matematika
# ============================================================

def _rapikan(x: float) -> float:
    """Buang galat pembulatan, mis. sinus 30 derajat = 0.49999999999999994 → 0.5."""
    return round(x, 12) + 0.0  # + 0.0 mengubah -0.0 menjadi 0.0


def _akar(x):
    _pastikan_angka(x, "akar")
    if x < 0:
        raise KesalahanNilai("Tidak bisa menghitung akar dari bilangan negatif")
    return math.sqrt(x)


def _pangkat(x, n):
    hasil = _pastikan_angka(x, "pangkat") ** _pastikan_angka(n, "pangkat")
    if isinstance(hasil, complex):
        raise KesalahanNilai("Pangkat pecahan dari bilangan negatif tidak bisa dihitung")
    return hasil


def _bulatkan(x, digit=0):
    """Pembulatan seperti di sekolah: 2.5 → 3, 2.45 (1 digit) → 2.5."""
    _pastikan_angka(x, "bulatkan")
    _pastikan_bulat(digit, "bulatkan")
    hasil = Decimal(str(x)).quantize(Decimal(1).scaleb(-digit), rounding=ROUND_HALF_UP)
    return int(hasil) if digit <= 0 else float(hasil)


def _sudut(nama: str, fungsi):
    def hitung(derajat):
        _pastikan_angka(derajat, nama)
        return _rapikan(fungsi(math.radians(derajat)))
    return hitung


def _tangen(derajat):
    _pastikan_angka(derajat, "tangen")
    radian = math.radians(derajat)
    if abs(math.cos(radian)) < 1e-12:
        raise KesalahanNilai(f"Tangen {_ke_teks(derajat)} derajat tidak terdefinisi")
    return _rapikan(math.tan(radian))


def _logaritma(x, basis=10):
    _pastikan_angka(x, "logaritma")
    _pastikan_angka(basis, "logaritma")
    if x <= 0:
        raise KesalahanNilai("Logaritma hanya untuk bilangan lebih dari 0")
    if basis <= 0 or basis == 1:
        raise KesalahanNilai("Basis logaritma harus lebih dari 0 dan bukan 1")
    return _rapikan(math.log(x, basis))


def _ln(x):
    _pastikan_angka(x, "ln")
    if x <= 0:
        raise KesalahanNilai("Logaritma hanya untuk bilangan lebih dari 0")
    return math.log(x)


def _faktorial(n):
    _pastikan_bulat(n, "faktorial")
    if n < 0:
        raise KesalahanNilai("Faktorial hanya untuk bilangan 0 atau lebih")
    return math.factorial(n)


def _fpb(*angka):
    """FPB (Faktor Persekutuan Terbesar): fpb(12, 18) → 6."""
    if len(angka) < 2:
        raise KesalahanNilai("fpb membutuhkan paling sedikit dua bilangan")
    return math.gcd(*(_pastikan_bulat(a, "fpb") for a in angka))


def _kpk(*angka):
    """KPK (Kelipatan Persekutuan Terkecil): kpk(4, 6) → 12."""
    if len(angka) < 2:
        raise KesalahanNilai("kpk membutuhkan paling sedikit dua bilangan")
    return math.lcm(*(_pastikan_bulat(a, "kpk") for a in angka))


def _modul_matematika() -> BKModul:
    bawah = lambda x: math.floor(_pastikan_angka(x, "bulatkan_bawah"))
    atas = lambda x: math.ceil(_pastikan_angka(x, "bulatkan_atas"))
    return BKModul("matematika", {
        "pi": math.pi,
        "e": math.e,
        "akar": _akar,
        "pangkat": _pangkat,
        "mutlak": lambda x: abs(_pastikan_angka(x, "mutlak")),
        "bulatkan": _bulatkan,
        "bulatkan_bawah": bawah,
        "bulatkan_atas": atas,
        "lantai": bawah,
        "langit": atas,
        "sinus": _sudut("sinus", math.sin),
        "kosinus": _sudut("kosinus", math.cos),
        "tangen": _tangen,
        "logaritma": _logaritma,
        "ln": _ln,
        "faktorial": _faktorial,
        "fpb": _fpb,
        "kpk": _kpk,
    })


# ============================================================
# acak
# ============================================================

def bilangan_acak(minimum, maksimum):
    """Bilangan bulat acak dari minimum sampai maksimum (keduanya termasuk)."""
    _pastikan_bulat(minimum, "bilangan acak")
    _pastikan_bulat(maksimum, "bilangan acak")
    if minimum > maksimum:
        raise KesalahanNilai(f"Batas bawah ({minimum}) tidak boleh lebih besar dari batas atas ({maksimum})")
    return random.randint(minimum, maksimum)


def _pilih(koleksi):
    if isinstance(koleksi, BKDaftar):
        isi = koleksi.elemen
    elif isinstance(koleksi, str):
        isi = koleksi
    else:
        raise KesalahanTipe(f"'pilih' membutuhkan daftar atau teks, bukan '{_ke_teks(koleksi)}'")
    if not isi:
        raise KesalahanNilai("Tidak bisa memilih dari daftar yang kosong")
    return random.choice(isi)


def _kocok(daftar):
    if not isinstance(daftar, BKDaftar):
        raise KesalahanTipe(f"'kocok' membutuhkan daftar, bukan '{_ke_teks(daftar)}'")
    random.shuffle(daftar.elemen)


def _modul_acak() -> BKModul:
    return BKModul("acak", {
        "bilangan": bilangan_acak,
        "angka": random.random,
        "pilih": _pilih,
        "kocok": _kocok,
        "atur_benih": lambda benih: random.seed(benih),
    })


# ============================================================
# waktu
# ============================================================

def _modul_waktu() -> BKModul:
    return BKModul("waktu", {
        "jam": lambda: baca_waktu("jam"),
        "menit": lambda: baca_waktu("menit"),
        "detik": lambda: baca_waktu("detik"),
        "sekarang": lambda: baca_waktu("waktu"),
        "hari": lambda: baca_waktu("hari"),
        "tanggal_lengkap": lambda: f"{baca_waktu('hari')}, {baca_waktu('tanggal')}",
        "nama_bulan": lambda: baca_waktu("bulan"),
        "tahun": lambda: baca_waktu("tahun"),
        "tunggu": lambda detik: tunggu(detik),
    })


# ============================================================
# berkas
# ============================================================

def _buka(nama, mode: str, isi=None):
    if not isinstance(nama, str):
        raise KesalahanTipe(f"Nama berkas harus berupa teks, bukan '{_ke_teks(nama)}'")
    try:
        with open(nama, mode, encoding="utf-8") as f:
            if isi is None:
                return f.read()
            f.write(_ke_teks(isi))
    except FileNotFoundError:
        raise KesalahanBerkas(f"Berkas '{nama}' tidak ditemukan")
    except IsADirectoryError:
        raise KesalahanBerkas(f"'{nama}' adalah folder, bukan berkas")
    except PermissionError:
        raise KesalahanBerkas(f"Tidak punya izin untuk membuka berkas '{nama}'")
    except UnicodeDecodeError:
        raise KesalahanBerkas(f"Berkas '{nama}' bukan berkas teks")


def _hapus_berkas(nama):
    if not isinstance(nama, str):
        raise KesalahanTipe(f"Nama berkas harus berupa teks, bukan '{_ke_teks(nama)}'")
    try:
        os.remove(nama)
    except FileNotFoundError:
        raise KesalahanBerkas(f"Berkas '{nama}' tidak ditemukan")
    except (IsADirectoryError, PermissionError):
        raise KesalahanBerkas(f"Berkas '{nama}' tidak bisa dihapus")


def _modul_berkas() -> BKModul:
    return BKModul("berkas", {
        "baca": lambda nama: _buka(nama, "r"),
        "baca_baris": lambda nama: BKDaftar(_buka(nama, "r").splitlines()),
        "tulis": lambda nama, isi: _buka(nama, "w", isi),
        "tambahkan": lambda nama, isi: _buka(nama, "a", isi),
        "ada": lambda nama: isinstance(nama, str) and os.path.isfile(nama),
        "hapus": _hapus_berkas,
    })


# ============================================================
# Daftar modul
# ============================================================

MODUL = {
    "matematika": _modul_matematika,
    "acak": _modul_acak,
    "waktu": _modul_waktu,
    "berkas": _modul_berkas,
}


def muat_modul(nama: str) -> BKModul:
    """Muat modul pustaka standar. KeyError jika tidak ada."""
    return MODUL[nama]()
