"""
parser.py — Recursive descent parser untuk bahasa pemrograman Indonesia.

Mengubah daftar token (dari lexer) menjadi Abstract Syntax Tree (AST).
"""

from __future__ import annotations
from typing import List, Optional

from src.token_types import TokenType
from src.lexer import Token
from src.errors import KesalahanSintaks
from src.ast_nodes import (
    NodeProgram, NodeAngka, NodeTeks, NodeTeksFormat, NodeLogika, NodeKosong,
    NodeIdentifier, NodeOperasiBiner, NodeOperasiUnari,
    NodeDeklarasiVariabel, NodeKonstanta, NodePenugasan, NodePenugasanGabungan,
    NodeTampilkan, NodeJika, NodePilih, NodeSelama, NodeUntuk, NodeUntukSetiap,
    NodeUlangi, NodeBerhenti, NodeLewati, NodeFungsi, NodeFungsiAnonim,
    NodePanggilFungsi, NodeKembalikan, NodeDaftar, NodeKamus,
    NodeAksesDaftar, NodeIrisanDaftar, NodeAksesAtribut,
    NodeKelas, NodeImpor, NodeDariImpor, NodeCoba, NodeLempar,
)


class Parser:
    """Recursive descent parser untuk bahasa Indonesia."""

    def __init__(self, tokens: List[Token], kode_sumber: str = ""):
        self.tokens = tokens
        self.pos = 0
        self.kode_sumber = kode_sumber
        self.daftar_baris = kode_sumber.split("\n") if kode_sumber else []

    # ============================
    # Helpers
    # ============================

    def saat_ini(self) -> Token:
        return self.tokens[self.pos]

    def periksa(self, *tipe: TokenType) -> bool:
        return self.saat_ini().tipe in tipe

    def cocok(self, *tipe: TokenType) -> bool:
        if self.periksa(*tipe):
            self.maju()
            return True
        return False

    def maju(self) -> Token:
        tok = self.saat_ini()
        if self.pos < len(self.tokens) - 1:
            self.pos += 1
        return tok

    def harapkan(self, tipe: TokenType, pesan: str = "") -> Token:
        if self.periksa(tipe):
            return self.maju()
        tok = self.saat_ini()
        if not pesan:
            pesan = f"Diharapkan {tipe.name} tapi ditemukan {tok.tipe.name} ('{tok.nilai}')"
        baris_kode = self.daftar_baris[tok.baris - 1] if tok.baris - 1 < len(self.daftar_baris) else ""
        raise KesalahanSintaks(pesan, baris=tok.baris, kolom=tok.kolom, baris_kode=baris_kode)

    def lewati_baris_baru(self):
        while self.periksa(TokenType.BARIS_BARU):
            self.maju()

    def _error(self, pesan: str, tok: Token = None):
        if tok is None:
            tok = self.saat_ini()
        baris_kode = self.daftar_baris[tok.baris - 1] if tok.baris - 1 < len(self.daftar_baris) else ""
        raise KesalahanSintaks(pesan, baris=tok.baris, kolom=tok.kolom, baris_kode=baris_kode)

    # ============================
    # Program
    # ============================

    def parse(self) -> NodeProgram:
        pernyataan = []
        self.lewati_baris_baru()
        while not self.periksa(TokenType.EOF):
            stmt = self.parse_pernyataan()
            if stmt is not None:
                pernyataan.append(stmt)
            self.lewati_baris_baru()
        return NodeProgram(pernyataan)

    # ============================
    # Blok (indented block)
    # ============================

    def parse_blok(self) -> list:
        self.harapkan(TokenType.TITIK_DUA)
        if not self.periksa(TokenType.BARIS_BARU):
            stmt = self.parse_pernyataan()
            return [stmt] if stmt else []
        self.lewati_baris_baru()
        self.harapkan(TokenType.INDENT)
        stmts = []
        while not self.periksa(TokenType.DEDENT, TokenType.EOF):
            self.lewati_baris_baru()
            if self.periksa(TokenType.DEDENT, TokenType.EOF):
                break
            stmt = self.parse_pernyataan()
            if stmt is not None:
                stmts.append(stmt)
            self.lewati_baris_baru()
        if self.periksa(TokenType.DEDENT):
            self.maju()
        return stmts

    # ============================
    # Pernyataan (Statement)
    # ============================

    def parse_pernyataan(self):
        t = self.saat_ini().tipe
        if t == TokenType.BUAT:
            return self.parse_deklarasi_buat()
        if t == TokenType.TETAP:
            return self.parse_konstanta()
        if t in (TokenType.BILANGAN, TokenType.DESIMAL_TIPE, TokenType.TEKS_TIPE, TokenType.LOGIKA_TIPE):
            return self.parse_deklarasi_tipe()
        if t == TokenType.TAMPILKAN:
            return self.parse_tampilkan()
        if t == TokenType.JIKA:
            return self.parse_jika()
        if t == TokenType.PILIH:
            return self.parse_pilih()
        if t == TokenType.SELAMA:
            return self.parse_selama()
        if t == TokenType.UNTUK:
            return self.parse_untuk()
        if t == TokenType.UNTUK_SETIAP:
            return self.parse_untuk_setiap()
        if t == TokenType.ULANGI:
            return self.parse_ulangi()
        if t == TokenType.FUNGSI:
            return self.parse_fungsi()
        if t == TokenType.KEMBALIKAN:
            return self.parse_kembalikan()
        if t == TokenType.BERHENTI:
            tok = self.maju()
            return NodeBerhenti(baris=tok.baris, kolom=tok.kolom)
        if t == TokenType.LEWATI:
            tok = self.maju()
            return NodeLewati(baris=tok.baris, kolom=tok.kolom)
        if t == TokenType.KELAS:
            return self.parse_kelas()
        if t == TokenType.IMPOR:
            return self.parse_impor()
        if t == TokenType.DARI:
            return self.parse_dari_impor()
        if t == TokenType.COBA:
            return self.parse_coba()
        if t == TokenType.LEMPAR:
            return self.parse_lempar()
        return self.parse_penugasan_atau_ekspresi()

    # ============================
    # Deklarasi
    # ============================

    def parse_deklarasi_buat(self):
        tok = self.maju()  # BUAT
        nama = self.harapkan(TokenType.IDENTIFIER).nilai
        self.harapkan(TokenType.SAMA_DENGAN)
        ekspresi = self.parse_ekspresi()
        return NodeDeklarasiVariabel(nama, ekspresi, baris=tok.baris, kolom=tok.kolom)

    def parse_konstanta(self):
        tok = self.maju()  # TETAP
        nama = self.harapkan(TokenType.IDENTIFIER).nilai
        self.harapkan(TokenType.SAMA_DENGAN)
        ekspresi = self.parse_ekspresi()
        return NodeKonstanta(nama, ekspresi, baris=tok.baris, kolom=tok.kolom)

    def parse_deklarasi_tipe(self):
        tok = self.maju()  # BILANGAN / DESIMAL_TIPE / TEKS_TIPE / LOGIKA_TIPE
        tipe_map = {
            TokenType.BILANGAN: "bilangan", TokenType.DESIMAL_TIPE: "desimal",
            TokenType.TEKS_TIPE: "teks", TokenType.LOGIKA_TIPE: "logika",
        }
        tipe = tipe_map[tok.tipe]
        nama = self.harapkan(TokenType.IDENTIFIER).nilai
        self.harapkan(TokenType.SAMA_DENGAN)
        ekspresi = self.parse_ekspresi()
        return NodeDeklarasiVariabel(nama, ekspresi, tipe_eksplisit=tipe, baris=tok.baris, kolom=tok.kolom)

    # ============================
    # Penugasan / Ekspresi Statement
    # ============================

    def parse_penugasan_atau_ekspresi(self):
        ekspresi = self.parse_ekspresi()
        if self.periksa(TokenType.SAMA_DENGAN):
            tok = self.maju()
            nilai = self.parse_ekspresi()
            return NodePenugasan(ekspresi, nilai, baris=tok.baris, kolom=tok.kolom)
        if self.periksa(TokenType.TAMBAH_SAMA, TokenType.KURANG_SAMA, TokenType.KALI_SAMA,
                        TokenType.BAGI_SAMA, TokenType.MODULO_SAMA):
            tok = self.maju()
            nilai = self.parse_ekspresi()
            return NodePenugasanGabungan(ekspresi, tok.nilai, nilai, baris=tok.baris, kolom=tok.kolom)
        return ekspresi

    # ============================
    # Tampilkan
    # ============================

    def parse_tampilkan(self):
        tok = self.maju()  # TAMPILKAN
        args = [self.parse_ekspresi()]
        while self.cocok(TokenType.KOMA):
            args.append(self.parse_ekspresi())
        return NodeTampilkan(args, baris=tok.baris, kolom=tok.kolom)

    # ============================
    # Kondisi
    # ============================

    def parse_jika(self):
        tok = self.maju()  # JIKA
        kondisi = self.parse_ekspresi()
        blok_jika = self.parse_blok()
        cabang = []
        blok_selainnya = None
        self.lewati_baris_baru()
        while self.periksa(TokenType.ATAU_JIKA):
            self.maju()
            k = self.parse_ekspresi()
            b = self.parse_blok()
            cabang.append((k, b))
            self.lewati_baris_baru()
        if self.cocok(TokenType.SELAINNYA):
            blok_selainnya = self.parse_blok()
        return NodeJika(kondisi, blok_jika, cabang, blok_selainnya, baris=tok.baris, kolom=tok.kolom)

    def parse_pilih(self):
        tok = self.maju()  # PILIH
        ekspresi = self.parse_ekspresi()
        self.harapkan(TokenType.TITIK_DUA)
        self.lewati_baris_baru()
        self.harapkan(TokenType.INDENT)
        kasus = []
        bawaan = None
        while not self.periksa(TokenType.DEDENT, TokenType.EOF):
            self.lewati_baris_baru()
            if self.periksa(TokenType.DEDENT, TokenType.EOF):
                break
            if self.periksa(TokenType.KETIKA):
                self.maju()
                k_expr = self.parse_ekspresi()
                blok = self.parse_blok()
                kasus.append((k_expr, blok))
            elif self.periksa(TokenType.BAWAAN):
                self.maju()
                bawaan = self.parse_blok()
            else:
                self._error("Diharapkan 'ketika' atau 'bawaan' dalam blok 'pilih'")
            self.lewati_baris_baru()
        if self.periksa(TokenType.DEDENT):
            self.maju()
        return NodePilih(ekspresi, kasus, bawaan, baris=tok.baris, kolom=tok.kolom)

    # ============================
    # Perulangan
    # ============================

    def parse_selama(self):
        tok = self.maju()  # SELAMA
        kondisi = self.parse_ekspresi()
        blok = self.parse_blok()
        return NodeSelama(kondisi, blok, baris=tok.baris, kolom=tok.kolom)

    def parse_untuk(self):
        tok = self.maju()  # UNTUK
        nama = self.harapkan(TokenType.IDENTIFIER).nilai
        self.harapkan(TokenType.DARI)
        dari_expr = self.parse_ekspresi()
        self.harapkan(TokenType.SAMPAI)
        sampai_expr = self.parse_ekspresi()
        langkah = None
        if self.cocok(TokenType.LANGKAH):
            langkah = self.parse_ekspresi()
        blok = self.parse_blok()
        return NodeUntuk(nama, dari_expr, sampai_expr, langkah, blok, baris=tok.baris, kolom=tok.kolom)

    def parse_untuk_setiap(self):
        tok = self.maju()  # UNTUK_SETIAP
        nama = self.harapkan(TokenType.IDENTIFIER).nilai
        self.harapkan(TokenType.DALAM)
        iterable = self.parse_ekspresi()
        blok = self.parse_blok()
        return NodeUntukSetiap(nama, iterable, blok, baris=tok.baris, kolom=tok.kolom)

    def parse_ulangi(self):
        tok = self.maju()  # ULANGI
        blok = self.parse_blok()
        self.lewati_baris_baru()
        self.harapkan(TokenType.SELAMA)
        kondisi = self.parse_ekspresi()
        return NodeUlangi(blok, kondisi, baris=tok.baris, kolom=tok.kolom)

    # ============================
    # Fungsi
    # ============================

    def parse_fungsi(self):
        tok = self.maju()  # FUNGSI
        nama = self.harapkan(TokenType.IDENTIFIER).nilai
        self.harapkan(TokenType.KURUNG_BUKA)
        params = self._parse_parameter()
        self.harapkan(TokenType.KURUNG_TUTUP)
        blok = self.parse_blok()
        return NodeFungsi(nama, params, blok, baris=tok.baris, kolom=tok.kolom)

    def _parse_parameter(self) -> list:
        params = []
        if self.periksa(TokenType.KURUNG_TUTUP):
            return params
        nama = self._harapkan_nama_param()
        default = None
        if self.cocok(TokenType.SAMA_DENGAN):
            default = self.parse_ekspresi()
        params.append((nama, default))
        while self.cocok(TokenType.KOMA):
            nama = self._harapkan_nama_param()
            default = None
            if self.cocok(TokenType.SAMA_DENGAN):
                default = self.parse_ekspresi()
            params.append((nama, default))
        return params

    def _harapkan_nama_param(self) -> str:
        """Accept IDENTIFIER or DIRI as parameter name."""
        if self.periksa(TokenType.IDENTIFIER):
            return self.maju().nilai
        if self.periksa(TokenType.DIRI):
            return self.maju().nilai
        return self.harapkan(TokenType.IDENTIFIER).nilai

    def parse_kembalikan(self):
        tok = self.maju()  # KEMBALIKAN
        ekspresi = None
        if not self.periksa(TokenType.BARIS_BARU, TokenType.DEDENT, TokenType.EOF):
            ekspresi = self.parse_ekspresi()
        return NodeKembalikan(ekspresi, baris=tok.baris, kolom=tok.kolom)

    # ============================
    # Kelas
    # ============================

    def parse_kelas(self):
        tok = self.maju()  # KELAS
        nama = self.harapkan(TokenType.IDENTIFIER).nilai
        induk = None
        if self.cocok(TokenType.MEWARISI):
            induk = self.harapkan(TokenType.IDENTIFIER).nilai
        blok = self.parse_blok()
        return NodeKelas(nama, induk, blok, baris=tok.baris, kolom=tok.kolom)

    # ============================
    # Modul
    # ============================

    def parse_impor(self):
        tok = self.maju()  # IMPOR
        modul = self.harapkan(TokenType.IDENTIFIER).nilai
        while self.cocok(TokenType.TITIK):
            modul += "." + self.harapkan(TokenType.IDENTIFIER).nilai
        alias = None
        if self.cocok(TokenType.SEBAGAI):
            alias = self.harapkan(TokenType.IDENTIFIER).nilai
        return NodeImpor(modul, alias, baris=tok.baris, kolom=tok.kolom)

    def parse_dari_impor(self):
        tok = self.maju()  # DARI
        modul = self.harapkan(TokenType.IDENTIFIER).nilai
        while self.cocok(TokenType.TITIK):
            modul += "." + self.harapkan(TokenType.IDENTIFIER).nilai
        self.harapkan(TokenType.IMPOR)
        nama = self.harapkan(TokenType.IDENTIFIER).nilai
        alias = None
        if self.cocok(TokenType.SEBAGAI):
            alias = self.harapkan(TokenType.IDENTIFIER).nilai
        return NodeDariImpor(modul, nama, alias, baris=tok.baris, kolom=tok.kolom)

    # ============================
    # Error Handling
    # ============================

    def parse_coba(self):
        tok = self.maju()  # COBA
        blok_coba = self.parse_blok()
        penangkap = []
        self.lewati_baris_baru()
        while self.periksa(TokenType.TANGKAP):
            self.maju()
            tipe_error = None
            variabel = None
            if self.periksa(TokenType.IDENTIFIER):
                tipe_error = self.maju().nilai
            if self.cocok(TokenType.SEBAGAI):
                variabel = self.harapkan(TokenType.IDENTIFIER).nilai
            blok = self.parse_blok()
            penangkap.append((tipe_error, variabel, blok))
            self.lewati_baris_baru()
        blok_akhirnya = None
        if self.cocok(TokenType.AKHIRNYA):
            blok_akhirnya = self.parse_blok()
        return NodeCoba(blok_coba, penangkap, blok_akhirnya, baris=tok.baris, kolom=tok.kolom)

    def parse_lempar(self):
        tok = self.maju()  # LEMPAR
        ekspresi = self.parse_ekspresi()
        return NodeLempar(ekspresi, baris=tok.baris, kolom=tok.kolom)

    # ============================
    # Ekspresi — Precedence Climbing
    # ============================

    def parse_ekspresi(self):
        return self.parse_atau()

    def parse_atau(self):
        kiri = self.parse_dan()
        while self.periksa(TokenType.ATAU):
            tok = self.maju()
            kanan = self.parse_dan()
            kiri = NodeOperasiBiner(kiri, "atau", kanan, baris=tok.baris, kolom=tok.kolom)
        return kiri

    def parse_dan(self):
        kiri = self.parse_bukan()
        while self.periksa(TokenType.DAN):
            tok = self.maju()
            kanan = self.parse_bukan()
            kiri = NodeOperasiBiner(kiri, "dan", kanan, baris=tok.baris, kolom=tok.kolom)
        return kiri

    def parse_bukan(self):
        if self.periksa(TokenType.BUKAN):
            tok = self.maju()
            operand = self.parse_bukan()
            return NodeOperasiUnari("bukan", operand, baris=tok.baris, kolom=tok.kolom)
        return self.parse_perbandingan()

    # Mapping operator teks Indonesia → simbol standar
    _OP_TEKS_KE_SIMBOL = {
        TokenType.SAMA_DENGAN_OP: "==",
        TokenType.TIDAK_SAMA_OP: "!=",
        TokenType.LEBIH_DARI: ">",
        TokenType.KURANG_DARI: "<",
        TokenType.TIDAK_KURANG_DARI: ">=",
        TokenType.TIDAK_LEBIH_DARI: "<=",
    }

    def parse_perbandingan(self):
        kiri = self.parse_penjumlahan()
        ops_simbol = (TokenType.SAMA, TokenType.TIDAK_SAMA, TokenType.LEBIH_BESAR,
                      TokenType.LEBIH_KECIL, TokenType.LEBIH_BESAR_SAMA, TokenType.LEBIH_KECIL_SAMA)
        ops_teks = (TokenType.SAMA_DENGAN_OP, TokenType.TIDAK_SAMA_OP,
                    TokenType.LEBIH_DARI, TokenType.KURANG_DARI,
                    TokenType.TIDAK_KURANG_DARI, TokenType.TIDAK_LEBIH_DARI)
        while self.periksa(*ops_simbol, *ops_teks) or self.periksa(TokenType.ADA):
            if self.periksa(TokenType.ADA):
                tok = self.maju()  # ADA
                self.harapkan(TokenType.DALAM)
                kanan = self.parse_penjumlahan()
                kiri = NodeOperasiBiner(kiri, "ada dalam", kanan, baris=tok.baris, kolom=tok.kolom)
            elif self.periksa(*ops_teks):
                tok = self.maju()
                op_simbol = self._OP_TEKS_KE_SIMBOL[tok.tipe]
                kanan = self.parse_penjumlahan()
                kiri = NodeOperasiBiner(kiri, op_simbol, kanan, baris=tok.baris, kolom=tok.kolom)
            else:
                tok = self.maju()
                kanan = self.parse_penjumlahan()
                kiri = NodeOperasiBiner(kiri, tok.nilai, kanan, baris=tok.baris, kolom=tok.kolom)
        return kiri

    def parse_penjumlahan(self):
        kiri = self.parse_perkalian()
        while self.periksa(TokenType.TAMBAH, TokenType.KURANG, TokenType.DITAMBAH, TokenType.DIKURANG):
            tok = self.maju()
            op = "+" if tok.tipe == TokenType.DITAMBAH else "-" if tok.tipe == TokenType.DIKURANG else tok.nilai
            kanan = self.parse_perkalian()
            kiri = NodeOperasiBiner(kiri, op, kanan, baris=tok.baris, kolom=tok.kolom)
        return kiri

    def parse_perkalian(self):
        kiri = self.parse_pangkat()
        while self.periksa(TokenType.KALI, TokenType.BAGI, TokenType.MODULO, TokenType.SISA_BAGI, TokenType.DIKALI, TokenType.DIBAGI):
            tok = self.maju()
            # Normalisasi operator teks
            op = "%" if tok.tipe == TokenType.SISA_BAGI else \
                 "*" if tok.tipe == TokenType.DIKALI else \
                 "/" if tok.tipe == TokenType.DIBAGI else tok.nilai
            kanan = self.parse_pangkat()
            kiri = NodeOperasiBiner(kiri, op, kanan, baris=tok.baris, kolom=tok.kolom)
        return kiri

    def parse_pangkat(self):
        basis = self.parse_unari()
        if self.periksa(TokenType.PANGKAT, TokenType.PANGKAT_KK):
            tok = self.maju()
            eksponen = self.parse_unari()
            return NodeOperasiBiner(basis, "**", eksponen, baris=tok.baris, kolom=tok.kolom)
        return basis

    def parse_unari(self):
        if self.periksa(TokenType.KURANG):
            tok = self.maju()
            operand = self.parse_unari()
            return NodeOperasiUnari("-", operand, baris=tok.baris, kolom=tok.kolom)
        return self.parse_postfix()

    # ============================
    # Postfix: call, subscript, attribute
    # ============================

    def parse_postfix(self):
        node = self.parse_primer()
        while True:
            if self.periksa(TokenType.KURUNG_BUKA):
                self.maju()
                args = []
                if not self.periksa(TokenType.KURUNG_TUTUP):
                    args.append(self.parse_ekspresi())
                    while self.cocok(TokenType.KOMA):
                        args.append(self.parse_ekspresi())
                tok_tutup = self.harapkan(TokenType.KURUNG_TUTUP)
                node = NodePanggilFungsi(node, args, baris=node.baris, kolom=node.kolom)
            elif self.periksa(TokenType.SIKU_BUKA):
                self.maju()
                node = self._parse_subscript(node)
            elif self.periksa(TokenType.TITIK):
                self.maju()
                # Accept both IDENTIFIER and keyword tokens as attribute names
                if self.periksa(TokenType.IDENTIFIER):
                    attr = self.maju().nilai
                elif self.periksa(TokenType.DIRI):
                    attr = self.maju().nilai
                else:
                    attr = self.harapkan(TokenType.IDENTIFIER).nilai
                node = NodeAksesAtribut(node, attr, baris=node.baris, kolom=node.kolom)
            else:
                break
        return node

    def _parse_subscript(self, objek):
        """Parse [index] or [start:end] slice."""
        awal = None
        if self.periksa(TokenType.TITIK_DUA):
            self.maju()
            akhir = None
            if not self.periksa(TokenType.SIKU_TUTUP):
                akhir = self.parse_ekspresi()
            self.harapkan(TokenType.SIKU_TUTUP)
            return NodeIrisanDaftar(objek, None, akhir, baris=objek.baris, kolom=objek.kolom)
        awal = self.parse_ekspresi()
        if self.periksa(TokenType.TITIK_DUA):
            self.maju()
            akhir = None
            if not self.periksa(TokenType.SIKU_TUTUP):
                akhir = self.parse_ekspresi()
            self.harapkan(TokenType.SIKU_TUTUP)
            return NodeIrisanDaftar(objek, awal, akhir, baris=objek.baris, kolom=objek.kolom)
        self.harapkan(TokenType.SIKU_TUTUP)
        return NodeAksesDaftar(objek, awal, baris=objek.baris, kolom=objek.kolom)

    # ============================
    # Primer (Primary expressions)
    # ============================

    def parse_primer(self):
        tok = self.saat_ini()

        # Angka
        if tok.tipe == TokenType.ANGKA:
            self.maju()
            return NodeAngka(tok.nilai, baris=tok.baris, kolom=tok.kolom)
        if tok.tipe == TokenType.DESIMAL:
            self.maju()
            return NodeAngka(tok.nilai, baris=tok.baris, kolom=tok.kolom)

        # Teks
        if tok.tipe == TokenType.TEKS:
            self.maju()
            return NodeTeks(tok.nilai, baris=tok.baris, kolom=tok.kolom)
        if tok.tipe == TokenType.TEKS_FORMAT:
            self.maju()
            return NodeTeksFormat(tok.nilai, baris=tok.baris, kolom=tok.kolom)

        # Logika
        if tok.tipe == TokenType.BENAR:
            self.maju()
            return NodeLogika(True, baris=tok.baris, kolom=tok.kolom)
        if tok.tipe == TokenType.SALAH:
            self.maju()
            return NodeLogika(False, baris=tok.baris, kolom=tok.kolom)

        # Kosong
        if tok.tipe == TokenType.KOSONG:
            self.maju()
            return NodeKosong(baris=tok.baris, kolom=tok.kolom)

        # Identifier
        if tok.tipe == TokenType.IDENTIFIER:
            self.maju()
            return NodeIdentifier(tok.nilai, baris=tok.baris, kolom=tok.kolom)

        # diri / super as identifier
        if tok.tipe in (TokenType.DIRI, TokenType.SUPER):
            self.maju()
            return NodeIdentifier(tok.nilai, baris=tok.baris, kolom=tok.kolom)

        # masukan / masukan_angka / masukan_desimal as callable identifier
        if tok.tipe in (TokenType.MASUKAN, TokenType.MASUKAN_ANGKA, TokenType.MASUKAN_DESIMAL):
            self.maju()
            return NodeIdentifier(tok.nilai, baris=tok.baris, kolom=tok.kolom)

        # Error class name in expressions (e.g., Error("pesan"))
        if tok.tipe == TokenType.IDENTIFIER:
            self.maju()
            return NodeIdentifier(tok.nilai, baris=tok.baris, kolom=tok.kolom)

        # Grouped expression: (expr)
        if tok.tipe == TokenType.KURUNG_BUKA:
            self.maju()
            expr = self.parse_ekspresi()
            self.harapkan(TokenType.KURUNG_TUTUP)
            return expr

        # List literal: [1, 2, 3]
        if tok.tipe == TokenType.SIKU_BUKA:
            return self.parse_daftar_literal()

        # Dict literal: {"k": "v"}
        if tok.tipe == TokenType.KURAWAL_BUKA:
            return self.parse_kamus_literal()

        # Anonymous function: fungsi(x): kembalikan x * x
        if tok.tipe == TokenType.FUNGSI:
            return self.parse_fungsi_anonim()

        self._error(f"Ekspresi tidak valid: '{tok.nilai}' ({tok.tipe.name})")

    # ============================
    # Collection literals
    # ============================

    def parse_daftar_literal(self):
        tok = self.maju()  # [
        elemen = []
        if not self.periksa(TokenType.SIKU_TUTUP):
            elemen.append(self.parse_ekspresi())
            while self.cocok(TokenType.KOMA):
                if self.periksa(TokenType.SIKU_TUTUP):
                    break
                elemen.append(self.parse_ekspresi())
        self.harapkan(TokenType.SIKU_TUTUP)
        return NodeDaftar(elemen, baris=tok.baris, kolom=tok.kolom)

    def parse_kamus_literal(self):
        tok = self.maju()  # {
        pasangan = []
        if not self.periksa(TokenType.KURAWAL_TUTUP):
            kunci = self.parse_ekspresi()
            self.harapkan(TokenType.TITIK_DUA)
            nilai = self.parse_ekspresi()
            pasangan.append((kunci, nilai))
            while self.cocok(TokenType.KOMA):
                if self.periksa(TokenType.KURAWAL_TUTUP):
                    break
                kunci = self.parse_ekspresi()
                self.harapkan(TokenType.TITIK_DUA)
                nilai = self.parse_ekspresi()
                pasangan.append((kunci, nilai))
        self.harapkan(TokenType.KURAWAL_TUTUP)
        return NodeKamus(pasangan, baris=tok.baris, kolom=tok.kolom)

    def parse_fungsi_anonim(self):
        tok = self.maju()  # FUNGSI
        self.harapkan(TokenType.KURUNG_BUKA)
        params = self._parse_parameter()
        self.harapkan(TokenType.KURUNG_TUTUP)
        self.harapkan(TokenType.TITIK_DUA)
        ekspresi = self.parse_ekspresi()
        return NodeFungsiAnonim(params, ekspresi, baris=tok.baris, kolom=tok.kolom)


# ============================
# Fungsi utilitas
# ============================

def parse(tokens: List[Token], kode_sumber: str = "") -> NodeProgram:
    """Shortcut: parse daftar token menjadi AST."""
    parser = Parser(tokens, kode_sumber)
    return parser.parse()
