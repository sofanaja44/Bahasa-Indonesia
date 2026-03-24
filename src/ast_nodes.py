"""
ast_nodes.py — Definisi semua node AST untuk bahasa pemrograman Indonesia.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Optional


# === Literal ===

@dataclass
class NodeAngka:
    nilai: int | float
    baris: int = 0
    kolom: int = 0

@dataclass
class NodeTeks:
    nilai: str
    baris: int = 0
    kolom: int = 0

@dataclass
class NodeTeksFormat:
    template: str
    baris: int = 0
    kolom: int = 0

@dataclass
class NodeLogika:
    nilai: bool
    baris: int = 0
    kolom: int = 0

@dataclass
class NodeKosong:
    baris: int = 0
    kolom: int = 0

@dataclass
class NodeIdentifier:
    nama: str
    baris: int = 0
    kolom: int = 0


# === Operasi ===

@dataclass
class NodeOperasiBiner:
    kiri: Any
    operator: str
    kanan: Any
    baris: int = 0
    kolom: int = 0

@dataclass
class NodeOperasiUnari:
    operator: str
    operand: Any
    baris: int = 0
    kolom: int = 0


# === Deklarasi & Penugasan ===

@dataclass
class NodeDeklarasiVariabel:
    nama: str
    ekspresi: Any
    tipe_eksplisit: Optional[str] = None
    baris: int = 0
    kolom: int = 0

@dataclass
class NodeKonstanta:
    nama: str
    ekspresi: Any
    baris: int = 0
    kolom: int = 0

@dataclass
class NodePenugasan:
    target: Any
    ekspresi: Any
    baris: int = 0
    kolom: int = 0

@dataclass
class NodePenugasanGabungan:
    target: Any
    operator: str
    ekspresi: Any
    baris: int = 0
    kolom: int = 0


# === I/O ===

@dataclass
class NodeTampilkan:
    ekspresi_list: list = field(default_factory=list)
    baris: int = 0
    kolom: int = 0


# === Kondisi ===

@dataclass
class NodeJika:
    kondisi: Any = None
    blok_jika: list = field(default_factory=list)
    cabang_atau_jika: list = field(default_factory=list)
    blok_selainnya: Optional[list] = None
    baris: int = 0
    kolom: int = 0

@dataclass
class NodePilih:
    ekspresi: Any = None
    kasus: list = field(default_factory=list)
    bawaan: Optional[list] = None
    baris: int = 0
    kolom: int = 0


# === Perulangan ===

@dataclass
class NodeSelama:
    kondisi: Any = None
    blok: list = field(default_factory=list)
    baris: int = 0
    kolom: int = 0

@dataclass
class NodeUntuk:
    variabel: str = ""
    dari_expr: Any = None
    sampai_expr: Any = None
    langkah_expr: Any = None
    blok: list = field(default_factory=list)
    baris: int = 0
    kolom: int = 0

@dataclass
class NodeUntukSetiap:
    variabel: str = ""
    iterable: Any = None
    blok: list = field(default_factory=list)
    baris: int = 0
    kolom: int = 0

@dataclass
class NodeUlangi:
    blok: list = field(default_factory=list)
    kondisi: Any = None
    baris: int = 0
    kolom: int = 0

@dataclass
class NodeBerhenti:
    baris: int = 0
    kolom: int = 0

@dataclass
class NodeLewati:
    baris: int = 0
    kolom: int = 0


# === Fungsi ===

@dataclass
class NodeFungsi:
    nama: str = ""
    parameter: list = field(default_factory=list)
    blok: list = field(default_factory=list)
    baris: int = 0
    kolom: int = 0

@dataclass
class NodeFungsiAnonim:
    parameter: list = field(default_factory=list)
    ekspresi: Any = None
    baris: int = 0
    kolom: int = 0

@dataclass
class NodePanggilFungsi:
    fungsi: Any = None
    argumen: list = field(default_factory=list)
    baris: int = 0
    kolom: int = 0

@dataclass
class NodeKembalikan:
    ekspresi: Any = None
    baris: int = 0
    kolom: int = 0


# === Koleksi ===

@dataclass
class NodeDaftar:
    elemen: list = field(default_factory=list)
    baris: int = 0
    kolom: int = 0

@dataclass
class NodeKamus:
    pasangan: list = field(default_factory=list)
    baris: int = 0
    kolom: int = 0

@dataclass
class NodeAksesDaftar:
    objek: Any = None
    indeks: Any = None
    baris: int = 0
    kolom: int = 0

@dataclass
class NodeIrisanDaftar:
    objek: Any = None
    awal: Any = None
    akhir: Any = None
    baris: int = 0
    kolom: int = 0

@dataclass
class NodeAksesAtribut:
    objek: Any = None
    atribut: str = ""
    baris: int = 0
    kolom: int = 0


# === OOP ===

@dataclass
class NodeKelas:
    nama: str = ""
    induk: Optional[str] = None
    blok: list = field(default_factory=list)
    baris: int = 0
    kolom: int = 0


# === Modul ===

@dataclass
class NodeImpor:
    modul: str = ""
    alias: Optional[str] = None
    baris: int = 0
    kolom: int = 0

@dataclass
class NodeDariImpor:
    modul: str = ""
    nama: str = ""
    alias: Optional[str] = None
    baris: int = 0
    kolom: int = 0


# === Error Handling ===

@dataclass
class NodeCoba:
    blok_coba: list = field(default_factory=list)
    penangkap: list = field(default_factory=list)
    blok_akhirnya: Optional[list] = None
    baris: int = 0
    kolom: int = 0

@dataclass
class NodeLempar:
    ekspresi: Any = None
    baris: int = 0
    kolom: int = 0


# === Program ===

@dataclass
class NodeProgram:
    pernyataan: list = field(default_factory=list)
