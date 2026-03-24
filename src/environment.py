"""
environment.py — Manajemen scope/lingkungan variabel untuk bahasa Indonesia.
"""

from __future__ import annotations
from typing import Any, Optional
from src.errors import KesalahanNama


class Lingkungan:
    """Scope variabel dengan parent chain untuk nested scoping."""

    def __init__(self, induk: Optional[Lingkungan] = None, nama: str = "global"):
        self.variabel: dict[str, Any] = {}
        self.konstanta: set[str] = set()
        self.induk = induk
        self.nama = nama

    def definisikan(self, nama: str, nilai: Any, konstanta: bool = False):
        """Definisikan variabel baru di scope saat ini."""
        self.variabel[nama] = nilai
        if konstanta:
            self.konstanta.add(nama)

    def dapatkan(self, nama: str, baris: int = 0, kolom: int = 0) -> Any:
        """Cari variabel dari scope terdalam ke terluar."""
        if nama in self.variabel:
            return self.variabel[nama]
        if self.induk is not None:
            return self.induk.dapatkan(nama, baris, kolom)
        raise KesalahanNama(
            f"Variabel '{nama}' belum dideklarasikan",
            baris=baris, kolom=kolom,
        )

    def setel(self, nama: str, nilai: Any, baris: int = 0, kolom: int = 0):
        """Ubah nilai variabel yang sudah ada."""
        if nama in self.variabel:
            if nama in self.konstanta:
                raise KesalahanNama(
                    f"Tidak bisa mengubah konstanta '{nama}'",
                    baris=baris, kolom=kolom,
                )
            self.variabel[nama] = nilai
            return
        if self.induk is not None:
            self.induk.setel(nama, nilai, baris, kolom)
            return
        raise KesalahanNama(
            f"Variabel '{nama}' belum dideklarasikan",
            baris=baris, kolom=kolom,
        )

    def ada(self, nama: str) -> bool:
        """Cek apakah variabel ada di scope manapun."""
        if nama in self.variabel:
            return True
        if self.induk is not None:
            return self.induk.ada(nama)
        return False

    def anak(self, nama: str = "lokal") -> Lingkungan:
        """Buat scope anak."""
        return Lingkungan(induk=self, nama=nama)
