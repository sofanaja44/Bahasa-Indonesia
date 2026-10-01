"""
environment.py — Manajemen scope/lingkungan variabel untuk bahasa Indonesia.
"""

from __future__ import annotations
import difflib
from typing import Any, Optional
from src.errors import KesalahanNama


def saran_nama(nama: str, kandidat) -> str:
    """" Maksud Anda 'nama'?" bila ada nama yang mirip, selain itu teks kosong."""
    mirip = difflib.get_close_matches(nama, list(kandidat), n=1, cutoff=0.7)
    return f" Maksud Anda '{mirip[0]}'?" if mirip else ""


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
        env = self
        while env is not None:
            if nama in env.variabel:
                return env.variabel[nama]
            env = env.induk
        raise KesalahanNama(
            f"Variabel '{nama}' belum dideklarasikan.{saran_nama(nama, self.semua_nama())}",
            baris=baris, kolom=kolom,
        )

    def setel(self, nama: str, nilai: Any, baris: int = 0, kolom: int = 0):
        """Ubah nilai variabel yang sudah ada."""
        env = self
        while env is not None:
            if nama in env.variabel:
                if nama in env.konstanta:
                    raise KesalahanNama(
                        f"Tidak bisa mengubah konstanta '{nama}'",
                        baris=baris, kolom=kolom,
                    )
                env.variabel[nama] = nilai
                return
            env = env.induk
        saran = saran_nama(nama, self.semua_nama()) or f" Untuk membuat variabel baru, tulis: buat {nama} adalah ..."
        raise KesalahanNama(f"Variabel '{nama}' belum dideklarasikan.{saran}", baris=baris, kolom=kolom)

    def semua_nama(self) -> set:
        """Semua nama yang terlihat dari scope ini (untuk saran salah ketik)."""
        nama = set()
        env = self
        while env is not None:
            nama.update(env.variabel)
            env = env.induk
        return nama

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
