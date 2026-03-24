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
