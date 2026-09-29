"""
bk_types.py — Tipe data native untuk bahasa pemrograman Indonesia.
"""

from __future__ import annotations
from typing import Any, Optional


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
        self.elemen.remove(item)

    def hapusPosisi(self, indeks):
        self.elemen.pop(indeks)

    def sisipkan(self, indeks, item):
        self.elemen.insert(indeks, item)

    def panjang(self):
        return len(self.elemen)

    def urutkan(self):
        self.elemen.sort()

    def balik(self):
        self.elemen.reverse()

    def cari(self, item):
        return self.elemen.index(item) if item in self.elemen else -1

    def salin(self):
        return BKDaftar(self.elemen[:])

    def kosongkan(self):
        self.elemen.clear()

    def metode(self, nama: str):
        """Ambil method berdasarkan nama."""
        metode_map = {
            "tambahkan": self.tambahkan, "hapus": self.hapus,
            "hapusPosisi": self.hapusPosisi, "sisipkan": self.sisipkan,
            "panjang": self.panjang, "urutkan": self.urutkan,
            "balik": self.balik, "cari": self.cari,
            "salin": self.salin, "kosongkan": self.kosongkan,
        }
        return metode_map.get(nama)


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
        del self.data[kunci]

    def dapatkan(self, kunci, default=None):
        return self.data.get(kunci, default)

    def metode(self, nama: str):
        metode_map = {
            "kunci": self.kunci, "nilai": self.nilai,
            "pasang": self.pasang, "adaKunci": self.adaKunci,
            "hapusKunci": self.hapusKunci, "dapatkan": self.dapatkan,
        }
        return metode_map.get(nama)


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
