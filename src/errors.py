"""
errors.py — Kelas-kelas error dalam Bahasa Indonesia untuk bahasa pemrograman Indonesia.
"""


class KesalahanIndonesia(Exception):
    """Base class untuk semua error bahasa Indonesia."""

    def __init__(self, pesan, baris=None, kolom=None, baris_kode=None):
        self.pesan = pesan
        self.baris = baris
        self.kolom = kolom
        self.baris_kode = baris_kode
        super().__init__(self.format_pesan())

    def format_pesan(self):
        nama = self.__class__.__name__
        header = f"❌ {nama}"
        if self.baris is not None:
            header += f" pada baris {self.baris}"
            if self.kolom is not None:
                header += f", kolom {self.kolom}"
        header += ":"

        bagian = [header, ""]
        if self.baris_kode is not None:
            bagian.append(f"    {self.baris_kode}")
            if self.kolom is not None and self.kolom > 0:
                bagian.append("    " + " " * (self.kolom - 1) + "^")
            bagian.append("")
        bagian.append(f"  {self.pesan}")
        return "\n".join(bagian)


class KesalahanSintaks(KesalahanIndonesia):
    """SyntaxError — kesalahan pada penulisan kode."""
    pass


class KesalahanNama(KesalahanIndonesia):
    """NameError — variabel atau fungsi tidak ditemukan."""
    pass


class KesalahanTipe(KesalahanIndonesia):
    """TypeError — operasi pada tipe data yang tidak cocok."""
    pass


class KesalahanIndeks(KesalahanIndonesia):
    """IndexError — indeks di luar batas daftar."""
    pass


class KesalahanBagiNol(KesalahanIndonesia):
    """ZeroDivisionError — pembagian dengan nol."""
    pass


class KesalahanBerkas(KesalahanIndonesia):
    """FileNotFoundError — berkas tidak ditemukan."""
    pass


class KesalahanKunci(KesalahanIndonesia):
    """KeyError — kunci tidak ditemukan di kamus."""
    pass


class KesalahanNilai(KesalahanIndonesia):
    """ValueError — nilai tidak valid."""
    pass


class KesalahanTumpukan(KesalahanIndonesia):
    """StackOverflowError — rekursi terlalu dalam."""
    pass


# ============================================================
# Nama jenis kesalahan untuk 'tangkap NAMA'
# ============================================================

# Padanan nama Python (Inggris), agar contoh seperti 'tangkap ZeroDivisionError' juga berjalan.
_PADANAN_PYTHON = {
    "KesalahanSintaks": "SyntaxError",
    "KesalahanNama": "NameError",
    "KesalahanTipe": "TypeError",
    "KesalahanIndeks": "IndexError",
    "KesalahanBagiNol": "ZeroDivisionError",
    "KesalahanBerkas": "FileNotFoundError",
    "KesalahanKunci": "KeyError",
    "KesalahanNilai": "ValueError",
    "KesalahanTumpukan": "RecursionError",
}
_PADANAN = {**_PADANAN_PYTHON, **{inggris: indonesia for indonesia, inggris in _PADANAN_PYTHON.items()}}

# 'tangkap Kesalahan' menangkap kesalahan jenis apa pun.
NAMA_SEMUA_KESALAHAN = {"kesalahan", "kesalahanindonesia", "error", "exception"}


def nama_tangkap(kelas: type) -> set:
    """Nama (huruf kecil) yang cocok di 'tangkap NAMA' untuk kesalahan berkelas ini.

    Contoh untuk KesalahanBagiNol: 'kesalahanbaginol', 'zerodivisionerror', dan
    nama yang menangkap semua kesalahan seperti 'kesalahan'.
    """
    nama = set(NAMA_SEMUA_KESALAHAN)
    for k in kelas.__mro__:
        if k in (BaseException, object):
            break
        nama.add(k.__name__.lower())
        if k.__name__ in _PADANAN:
            nama.add(_PADANAN[k.__name__].lower())
    return nama


def semua_nama_tangkap() -> dict:
    """Semua nama jenis kesalahan yang dikenal: huruf kecil → penulisan baku."""
    nama = {n: "Kesalahan" for n in NAMA_SEMUA_KESALAHAN}
    for kelas in KesalahanIndonesia.__subclasses__():
        nama[kelas.__name__.lower()] = kelas.__name__
        if kelas.__name__ in _PADANAN_PYTHON:
            nama[_PADANAN_PYTHON[kelas.__name__].lower()] = _PADANAN_PYTHON[kelas.__name__]
    return nama


def nama_jenis(kesalahan: BaseException) -> str:
    """Nama jenis kesalahan dalam bahasa Indonesia, mis. 'KesalahanBagiNol'."""
    nama = type(kesalahan).__name__
    if isinstance(kesalahan, KesalahanIndonesia):
        return nama
    return _PADANAN.get(nama, "Kesalahan")
