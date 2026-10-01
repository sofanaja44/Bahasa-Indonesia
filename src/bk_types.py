"""
bk_types.py — Tipe data native untuk bahasa pemrograman Indonesia.
"""

from __future__ import annotations
import string
from typing import Any, Optional

from src.errors import KesalahanIndeks, KesalahanKunci, KesalahanNilai, KesalahanTipe, nama_jenis


def _teks(nilai) -> str:
    from src.builtins import _ke_teks  # impor di sini agar tidak melingkar
    return _ke_teks(nilai)


# ============================================================
# Sinyal kontrol (bukan error, tapi sinyal internal)
# ============================================================

class SinyalKembalikan(Exception):
    """Sinyal untuk return dari fungsi."""
    def __init__(self, nilai: Any = None):
        self.nilai = nilai

class SinyalBerhenti(Exception):
    """Sinyal untuk break dari loop."""
    pass

class SinyalLewati(Exception):
    """Sinyal untuk continue dalam loop."""
    pass


class TeksKesalahan(str):
    """Isi variabel di 'tangkap sebagai e': pesan kesalahannya sebagai teks, plus e.pesan dan e.jenis."""

    def __new__(cls, kesalahan: BaseException):
        pesan = getattr(kesalahan, "pesan", None) or str(kesalahan)
        obj = super().__new__(cls, pesan)
        obj.pesan = pesan
        obj.jenis = nama_jenis(kesalahan)
        return obj


# ============================================================
# BKDaftar — List/Array
# ============================================================

class BKDaftar:
    """Tipe daftar (list) dengan method Bahasa Indonesia."""

    def __init__(self, elemen: list = None):
        self.elemen = list(elemen) if elemen else []

    def __repr__(self):
        return str(self.elemen)

    def __len__(self):
        return len(self.elemen)

    def __getitem__(self, key):
        return self.elemen[key]

    def __setitem__(self, key, value):
        self.elemen[key] = value

    def __contains__(self, item):
        return item in self.elemen

    def __iter__(self):
        return iter(self.elemen)

    def tambahkan(self, item):
        self.elemen.append(item)

    def hapus(self, item):
        if item not in self.elemen:
            raise KesalahanNilai(f"'{_teks(item)}' tidak ada di dalam daftar")
        self.elemen.remove(item)

    def hapusPosisi(self, indeks):
        if isinstance(indeks, bool) or not isinstance(indeks, int):
            raise KesalahanTipe(f"Posisi harus bilangan bulat, bukan '{_teks(indeks)}'")
        if not -len(self.elemen) <= indeks < len(self.elemen):
            raise KesalahanIndeks(f"Posisi {indeks} di luar batas daftar (panjangnya {len(self.elemen)})")
        return self.elemen.pop(indeks)

    def sisipkan(self, indeks, item):
        if isinstance(indeks, bool) or not isinstance(indeks, int):
            raise KesalahanTipe(f"Posisi harus bilangan bulat, bukan '{_teks(indeks)}'")
        self.elemen.insert(indeks, item)

    def panjang(self):
        return len(self.elemen)

    def urutkan(self):
        try:
            self.elemen.sort()
        except TypeError:
            raise KesalahanTipe("Isi daftar tidak bisa diurutkan karena jenis datanya berbeda-beda")

    def gabung(self, pemisah=" "):
        """["apel", "jeruk"].gabung(", ") → "apel, jeruk"."""
        return _teks(pemisah).join(_teks(e) for e in self.elemen)

    def balik(self):
        self.elemen.reverse()

    def cari(self, item):
        return self.elemen.index(item) if item in self.elemen else -1

    def salin(self):
        return BKDaftar(self.elemen[:])

    def kosongkan(self):
        self.elemen.clear()

    def semua_metode(self) -> dict:
        return {
            "tambahkan": self.tambahkan, "hapus": self.hapus,
            "hapusPosisi": self.hapusPosisi, "sisipkan": self.sisipkan,
            "panjang": self.panjang, "urutkan": self.urutkan,
            "balik": self.balik, "cari": self.cari,
            "salin": self.salin, "kosongkan": self.kosongkan,
            "gabung": self.gabung,
        }

    def metode(self, nama: str):
        """Ambil method berdasarkan nama."""
        return self.semua_metode().get(nama)


# ============================================================
# BKKamus — Dictionary/Map
# ============================================================

class BKKamus:
    """Tipe kamus (dictionary) dengan method Bahasa Indonesia."""

    def __init__(self, data: dict = None):
        self.data = dict(data) if data else {}

    def __repr__(self):
        return str(self.data)

    def __contains__(self, key):
        return key in self.data

    def __iter__(self):
        """'untuk setiap kunci dalam kamus' menelusuri kunci-kuncinya."""
        return iter(self.data)

    def __getitem__(self, key):
        return self.data[key]

    def __setitem__(self, key, value):
        self.data[key] = value

    def kunci(self):
        return BKDaftar(list(self.data.keys()))

    def nilai(self):
        return BKDaftar(list(self.data.values()))

    def pasang(self):
        return BKDaftar([BKDaftar([k, v]) for k, v in self.data.items()])

    def adaKunci(self, kunci):
        return kunci in self.data

    def hapusKunci(self, kunci):
        if kunci not in self.data:
            raise KesalahanKunci(f"Kunci '{_teks(kunci)}' tidak ditemukan di kamus")
        del self.data[kunci]

    def dapatkan(self, kunci, default=None):
        return self.data.get(kunci, default)

    def semua_metode(self) -> dict:
        return {
            "kunci": self.kunci, "nilai": self.nilai,
            "pasang": self.pasang, "adaKunci": self.adaKunci,
            "hapusKunci": self.hapusKunci, "dapatkan": self.dapatkan,
        }

    def metode(self, nama: str):
        return self.semua_metode().get(nama)


# ============================================================
# Metode teks: "halo".huruf_besar(), kalimat.belah(" "), ...
# ============================================================

def _pastikan_teks(nilai, nama_metode: str) -> str:
    if not isinstance(nilai, str):
        raise KesalahanTipe(f"Metode teks '{nama_metode}' membutuhkan teks, bukan '{_teks(nilai)}'")
    return nilai


def semua_metode_teks(teks: str) -> dict:
    """Metode yang bisa dipanggil pada sebuah teks."""
    return {
        "panjang": lambda: len(teks),
        "huruf_besar": lambda: teks.upper(),
        "huruf_kecil": lambda: teks.lower(),
        "huruf_awal_besar": lambda: string.capwords(teks),
        "potong_spasi": lambda: teks.strip(),
        "belah": lambda pemisah=None: BKDaftar(
            teks.split(_pastikan_teks(pemisah, "belah") if pemisah is not None else None)
        ),
        "ganti": lambda lama, baru: teks.replace(_pastikan_teks(lama, "ganti"), _teks(baru)),
        "berisi": lambda bagian: _pastikan_teks(bagian, "berisi") in teks,
        "diawali": lambda awalan: teks.startswith(_pastikan_teks(awalan, "diawali")),
        "diakhiri": lambda akhiran: teks.endswith(_pastikan_teks(akhiran, "diakhiri")),
        "cari": lambda bagian: teks.find(_pastikan_teks(bagian, "cari")),
        "balik": lambda: teks[::-1],
        "berupa_angka": lambda: _teks_ke_angka(teks) is not None,
        # Nama dari TASKS.md
        "mulai_dengan": lambda awalan: teks.startswith(_pastikan_teks(awalan, "mulai_dengan")),
        "akhir_dengan": lambda akhiran: teks.endswith(_pastikan_teks(akhiran, "akhir_dengan")),
        "temukan": lambda bagian: teks.find(_pastikan_teks(bagian, "temukan")),
    }


def _teks_ke_angka(teks: str):
    from src.builtins import teks_ke_angka  # impor di sini agar tidak melingkar
    return teks_ke_angka(teks)


# ============================================================
# BKModul — modul pustaka standar (matematika, acak, ...)
# ============================================================

class BKModul:
    """Modul yang dimuat dengan 'impor': isinya fungsi dan nilai."""

    def __init__(self, nama: str, isi: dict):
        self.nama = nama
        self.isi = isi

    def __repr__(self):
        return f"<modul {self.nama}>"


# ============================================================
# BKFungsi — Function
# ============================================================

class BKFungsi:
    """Representasi fungsi yang didefinisikan pengguna."""

    def __init__(self, nama: str, parameter: list, blok: list, lingkungan, node=None):
        self.nama = nama
        self.parameter = parameter  # list of (nama, default_value)
        self.blok = blok
        self.lingkungan = lingkungan  # closure scope
        self.node = node
        self.kelas = None  # kelas pemilik, jika fungsi ini adalah metode

    def __repr__(self):
        return f"<fungsi {self.nama}>"


# ============================================================
# BKKelas — Class
# ============================================================

class BKKelas:
    """Representasi kelas yang didefinisikan pengguna."""

    def __init__(self, nama: str, induk: Optional[BKKelas], metode: dict, atribut: dict):
        self.nama = nama
        self.induk = induk
        self.metode = metode    # dict of nama -> BKFungsi
        self.atribut = atribut  # dict of nama -> default value

    def __repr__(self):
        return f"<kelas {self.nama}>"

    def cari_metode(self, nama: str) -> Optional[BKFungsi]:
        if nama in self.metode:
            return self.metode[nama]
        if self.induk is not None:
            return self.induk.cari_metode(nama)
        return None


# ============================================================
# BKInstansi — Class Instance
# ============================================================

class BKInstansi:
    """Representasi instansi (objek) dari kelas."""

    def __init__(self, kelas: BKKelas):
        self.kelas = kelas
        self.atribut: dict[str, Any] = {}
        # Copy default attributes
        if kelas.atribut:
            self.atribut.update(kelas.atribut)

    def __repr__(self):
        return f"<{self.kelas.nama} instansi>"

    def dapatkan(self, nama: str):
        if nama in self.atribut:
            return self.atribut[nama]
        metode = self.kelas.cari_metode(nama)
        if metode is not None:
            return BKMetodeTerikat(self, metode)
        return None

    def setel(self, nama: str, nilai: Any):
        self.atribut[nama] = nilai


class BKMetodeTerikat:
    """Method yang terikat ke instansi tertentu."""

    def __init__(self, instansi: BKInstansi, fungsi: BKFungsi):
        self.instansi = instansi
        self.fungsi = fungsi

    def __repr__(self):
        return f"<metode {self.fungsi.nama} dari {self.instansi.kelas.nama}>"


class BKInduk:
    """Akses metode kelas induk dari dalam metode: induk.inisialisasi(...)."""

    def __init__(self, instansi: BKInstansi, kelas: BKKelas):
        self.instansi = instansi
        self.kelas = kelas  # kelas induk, tempat pencarian metode dimulai

    def __repr__(self):
        return f"<induk {self.kelas.nama}>"

    def dapatkan(self, nama: str):
        metode = self.kelas.cari_metode(nama)
        if metode is not None:
            return BKMetodeTerikat(self.instansi, metode)
        return None
