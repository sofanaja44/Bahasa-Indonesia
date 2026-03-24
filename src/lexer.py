"""
lexer.py — Tokenizer untuk bahasa pemrograman Indonesia.

Mengubah kode sumber (.id) menjadi daftar token yang siap di-parse.
Mendukung:
  - Angka (integer & desimal)
  - Teks/string (kutip ganda & tunggal) + escape sequences
  - F-string: f"Halo {nama}"
  - Identifier & kata kunci (termasuk multi-kata: "atau jika", "untuk setiap")
  - Operator & tanda baca
  - Komentar (#) dan komentar multi-baris (triple quote)
  - Indentasi berbasis spasi (INDENT / DEDENT)
  - Pelacakan posisi (baris, kolom) untuk pesan error
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import List

from src.token_types import TokenType, KATA_KUNCI, OPERATORS, PUNCTUATION
from src.errors import KesalahanSintaks


# ============================================================
# Token
# ============================================================

@dataclass
class Token:
    """Representasi satu token."""
    tipe: TokenType
    nilai: object       # str, int, float, atau None
    baris: int          # nomor baris (1-indexed)
    kolom: int          # nomor kolom (1-indexed)

    def __repr__(self):
        return f"Token({self.tipe.name}, {self.nilai!r}, baris={self.baris}, kolom={self.kolom})"


# ============================================================
# Lexer
# ============================================================

class Lexer:
    """Tokenizer untuk bahasa Indonesia."""

    def __init__(self, kode_sumber: str, nama_file: str = "<masukan>"):
        self.sumber = kode_sumber
        self.nama_file = nama_file
        self.pos = 0                # posisi karakter saat ini
        self.baris = 1              # nomor baris saat ini
        self.kolom = 1              # nomor kolom saat ini
        self.tokens: List[Token] = []
        self.indent_stack: List[int] = [0]  # stack level indentasi
        self.awal_baris = True      # apakah kita di awal baris baru?
        self.daftar_baris = kode_sumber.split("\n")

    # ----------------------------------------------------------
    # Karakter helpers
    # ----------------------------------------------------------

    @property
    def karakter(self) -> str | None:
        """Karakter saat ini, atau None jika sudah di akhir."""
        if self.pos < len(self.sumber):
            return self.sumber[self.pos]
        return None

    def intip(self, offset: int = 1) -> str | None:
        """Lihat karakter di posisi pos + offset tanpa memajukan posisi."""
        idx = self.pos + offset
        if idx < len(self.sumber):
            return self.sumber[idx]
        return None

    def maju(self) -> str | None:
        """Majukan posisi satu karakter dan kembalikan karakter sebelumnya."""
        ch = self.karakter
        if ch is None:
            return None
        self.pos += 1
        if ch == "\n":
            self.baris += 1
            self.kolom = 1
            self.awal_baris = True
        else:
            self.kolom += 1
        return ch

    def _baris_kode(self, nomor_baris: int) -> str:
        """Ambil teks baris tertentu untuk pesan error."""
        idx = nomor_baris - 1
        if 0 <= idx < len(self.daftar_baris):
            return self.daftar_baris[idx]
        return ""

    def _error(self, pesan: str, baris: int | None = None, kolom: int | None = None):
        b = baris if baris is not None else self.baris
        k = kolom if kolom is not None else self.kolom
        raise KesalahanSintaks(
            pesan,
            baris=b,
            kolom=k,
            baris_kode=self._baris_kode(b),
        )

    # ----------------------------------------------------------
    # Tambah token helper
    # ----------------------------------------------------------

    def _tambah(self, tipe: TokenType, nilai: object, baris: int, kolom: int):
        self.tokens.append(Token(tipe, nilai, baris, kolom))

    # ----------------------------------------------------------
    # Tokenisasi utama
    # ----------------------------------------------------------

    def tokenisasi(self) -> List[Token]:
        """Proses seluruh kode sumber → daftar token."""
        while self.karakter is not None:
            # === Awal baris → proses indentasi ===
            if self.awal_baris:
                self._proses_indentasi()
                if self.karakter is None:
                    break
                # Setelah proses indentasi, jika baris kosong / hanya komentar, lanjut
                if self.karakter == "\n":
                    self.maju()
                    continue

            ch = self.karakter

            # === Newline ===
            if ch == "\n":
                self._tambah(TokenType.BARIS_BARU, "\\n", self.baris, self.kolom)
                self.maju()
                continue

            # === Spasi / tab di tengah baris (skip) ===
            if ch in (" ", "\t", "\r"):
                self.maju()
                continue

            # === Komentar # ===
            if ch == "#":
                self._lewati_komentar_baris()
                continue

            # === Komentar multi-baris """ ===
            if ch == '"' and self.intip(1) == '"' and self.intip(2) == '"':
                self._lewati_komentar_multibaris()
                continue

            # === Angka ===
            if ch.isdigit():
                self._baca_angka()
                continue

            # === F-string: f"..." atau format"..." ===
            if ch == "f" and self.intip(1) in ('"', "'"):
                self._baca_fstring()
                continue

            # === format"..." ===
            if ch == "f" and self._intip_kata_dari_pos() == "format":
                # Cek apakah setelah 'format' langsung ada kutip
                idx = self.pos + 6  # len("format")
                if idx < len(self.sumber) and self.sumber[idx] in ('"', "'"):
                    self._baca_format_string()
                    continue

            # === String / teks ===
            if ch in ('"', "'"):
                self._baca_teks()
                continue

            # === Identifier / kata kunci ===
            if ch.isalpha() or ch == "_":
                self._baca_identifier()
                continue

            # === Operator (multi-char harus dicek duluan) ===
            if self._coba_operator():
                continue

            # === Tanda baca ===
            if ch in PUNCTUATION:
                self._tambah(PUNCTUATION[ch], ch, self.baris, self.kolom)
                self.maju()
                continue

            # === Karakter tidak dikenal ===
            self._error(f"Karakter tidak dikenal: '{ch}'")

        # === Akhir file: tutup semua indentasi yang masih terbuka ===
        while len(self.indent_stack) > 1:
            self.indent_stack.pop()
            self._tambah(TokenType.DEDENT, None, self.baris, self.kolom)

        self._tambah(TokenType.EOF, None, self.baris, self.kolom)
        return self.tokens

    # ----------------------------------------------------------
    # Indentasi
    # ----------------------------------------------------------

    def _proses_indentasi(self):
        """Hitung spasi awal baris dan keluarkan INDENT / DEDENT."""
        self.awal_baris = False

        # Jangan proses indentasi jika baris kosong atau hanya komentar
        simpan_pos = self.pos
        simpan_baris = self.baris
        simpan_kolom = self.kolom

        level = 0
        while self.karakter is not None and self.karakter in (" ", "\t"):
            if self.karakter == "\t":
                level += 4  # tab = 4 spasi
            else:
                level += 1
            self.maju()

        # Jika baris kosong atau hanya komentar → abaikan indentasi baris ini
        if self.karakter is None or self.karakter == "\n" or self.karakter == "#":
            return

        # Jika komentar multi-baris di awal baris
        if self.karakter == '"' and self.intip(1) == '"' and self.intip(2) == '"':
            return

        saat_ini = self.indent_stack[-1]
        baris_token = simpan_baris
        kolom_token = 1

        if level > saat_ini:
            self.indent_stack.append(level)
            self._tambah(TokenType.INDENT, None, baris_token, kolom_token)
        elif level < saat_ini:
            while len(self.indent_stack) > 1 and self.indent_stack[-1] > level:
                self.indent_stack.pop()
                self._tambah(TokenType.DEDENT, None, baris_token, kolom_token)
            if self.indent_stack[-1] != level:
                self._error(
                    f"Level indentasi tidak konsisten (diharapkan {self.indent_stack[-1]} spasi, ditemukan {level})",
                    baris=baris_token,
                    kolom=kolom_token,
                )

    # ----------------------------------------------------------
    # Komentar
    # ----------------------------------------------------------

    def _lewati_komentar_baris(self):
        """Lewati komentar mulai dari # sampai akhir baris."""
        while self.karakter is not None and self.karakter != "\n":
            self.maju()

    def _lewati_komentar_multibaris(self):
        """Lewati komentar triple-quote: \"\"\" ... \"\"\" """
        baris_awal = self.baris
        # Lewati pembuka """
        self.maju()  # "
        self.maju()  # "
        self.maju()  # "

        while self.karakter is not None:
            if (
                self.karakter == '"'
                and self.intip(1) == '"'
                and self.intip(2) == '"'
            ):
                self.maju()  # "
                self.maju()  # "
                self.maju()  # "
                return
            self.maju()

        self._error(
            "Komentar multi-baris tidak ditutup (diharapkan \"\"\")",
            baris=baris_awal,
        )

    # ----------------------------------------------------------
    # Angka
    # ----------------------------------------------------------

    def _baca_angka(self):
        """Baca literal angka (integer atau desimal)."""
        baris_awal = self.baris
        kolom_awal = self.kolom
        bagian = []
        ada_titik = False

        while self.karakter is not None and (self.karakter.isdigit() or self.karakter == "."):
            if self.karakter == ".":
                # Cek apakah ini titik desimal atau titik akses atribut
                next_ch = self.intip(1)
                if next_ch is not None and next_ch.isdigit():
                    if ada_titik:
                        self._error(
                            "Angka desimal tidak boleh memiliki lebih dari satu titik",
                            baris=baris_awal,
                            kolom=kolom_awal,
                        )
                    ada_titik = True
                else:
                    break  # Ini titik untuk akses atribut, bukan desimal
            bagian.append(self.karakter)
            self.maju()

        teks_angka = "".join(bagian)

        if ada_titik:
            self._tambah(TokenType.DESIMAL, float(teks_angka), baris_awal, kolom_awal)
        else:
            self._tambah(TokenType.ANGKA, int(teks_angka), baris_awal, kolom_awal)

    # ----------------------------------------------------------
    # Teks / String
    # ----------------------------------------------------------

    def _baca_teks(self):
        """Baca literal string yang diapit kutip ganda atau tunggal."""
        baris_awal = self.baris
        kolom_awal = self.kolom
        pembuka = self.karakter  # " atau '
        self.maju()  # lewati pembuka

        bagian = []
        while self.karakter is not None and self.karakter != pembuka:
            if self.karakter == "\n":
                self._error(
                    "Teks tidak ditutup sebelum akhir baris",
                    baris=baris_awal,
                    kolom=kolom_awal,
                )
            if self.karakter == "\\":
                self.maju()
                escape = self.karakter
                if escape is None:
                    self._error("Escape sequence tidak lengkap", baris=baris_awal)
                peta_escape = {
                    "n": "\n", "t": "\t", "\\": "\\",
                    "'": "'", '"': '"', "r": "\r",
                }
                bagian.append(peta_escape.get(escape, "\\" + escape))
                self.maju()
            else:
                bagian.append(self.karakter)
                self.maju()

        if self.karakter is None:
            self._error(
                f"Teks tidak ditutup (diharapkan {pembuka})",
                baris=baris_awal,
                kolom=kolom_awal,
            )

        self.maju()  # lewati penutup
        self._tambah(TokenType.TEKS, "".join(bagian), baris_awal, kolom_awal)

    # ----------------------------------------------------------
    # F-string
    # ----------------------------------------------------------

    def _baca_fstring(self):
        """Baca f-string: f\"Halo {nama}, umurmu {umur}\" """
        baris_awal = self.baris
        kolom_awal = self.kolom
        self.maju()  # lewati 'f'
        pembuka = self.karakter  # " atau '
        self.maju()  # lewati pembuka

        # Kumpulkan seluruh isi f-string sebagai teks mentah
        bagian = []
        while self.karakter is not None and self.karakter != pembuka:
            if self.karakter == "\n":
                self._error("F-string tidak ditutup sebelum akhir baris", baris=baris_awal)
            if self.karakter == "\\":
                self.maju()
                escape = self.karakter
                if escape is None:
                    self._error("Escape sequence tidak lengkap", baris=baris_awal)
                peta_escape = {
                    "n": "\n", "t": "\t", "\\": "\\",
                    "'": "'", '"': '"', "r": "\r",
                    "{": "{", "}": "}",
                }
                bagian.append(peta_escape.get(escape, "\\" + escape))
                self.maju()
            else:
                bagian.append(self.karakter)
                self.maju()

        if self.karakter is None:
            self._error(f"F-string tidak ditutup (diharapkan {pembuka})", baris=baris_awal)

        self.maju()  # lewati penutup
        self._tambah(TokenType.TEKS_FORMAT, "".join(bagian), baris_awal, kolom_awal)

    # ----------------------------------------------------------
    # Format string (format"...")
    # ----------------------------------------------------------

    def _baca_format_string(self):
        """Baca format\"Halo {nama}\" — alternatif dari f-string."""
        baris_awal = self.baris
        kolom_awal = self.kolom
        # Lewati 'format'
        for _ in range(6):  # len("format")
            self.maju()
        pembuka = self.karakter  # " atau '
        self.maju()  # lewati pembuka

        bagian = []
        while self.karakter is not None and self.karakter != pembuka:
            if self.karakter == "\n":
                self._error("Format string tidak ditutup sebelum akhir baris", baris=baris_awal)
            if self.karakter == "\\":
                self.maju()
                escape = self.karakter
                if escape is None:
                    self._error("Escape sequence tidak lengkap", baris=baris_awal)
                peta_escape = {
                    "n": "\n", "t": "\t", "\\": "\\",
                    "'": "'", '"': '"', "r": "\r",
                    "{": "{", "}": "}",
                }
                bagian.append(peta_escape.get(escape, "\\" + escape))
                self.maju()
            else:
                bagian.append(self.karakter)
                self.maju()

        if self.karakter is None:
            self._error(f"Format string tidak ditutup (diharapkan {pembuka})", baris=baris_awal)

        self.maju()  # lewati penutup
        self._tambah(TokenType.TEKS_FORMAT, "".join(bagian), baris_awal, kolom_awal)

    # ----------------------------------------------------------
    # Identifier / kata kunci
    # ----------------------------------------------------------

    def _baca_identifier(self):
        """Baca identifier atau kata kunci, termasuk kata kunci multi-kata."""
        baris_awal = self.baris
        kolom_awal = self.kolom
        bagian = []

        while self.karakter is not None and (self.karakter.isalnum() or self.karakter == "_"):
            bagian.append(self.karakter)
            self.maju()

        kata = "".join(bagian)

        # === Look-ahead untuk kata kunci multi-kata ===

        # "atau jika" → ATAU_JIKA
        if kata == "atau":
            kata_kedua = self._intip_kata_depan()
            if kata_kedua == "jika":
                self._lewati_spasi_horizontal()
                self._konsumsi_kata("jika")
                self._tambah(TokenType.ATAU_JIKA, "atau jika", baris_awal, kolom_awal)
                return

        # "untuk setiap" → UNTUK_SETIAP
        if kata == "untuk":
            kata_kedua = self._intip_kata_depan()
            if kata_kedua == "setiap":
                self._lewati_spasi_horizontal()
                self._konsumsi_kata("setiap")
                self._tambah(TokenType.UNTUK_SETIAP, "untuk setiap", baris_awal, kolom_awal)
                return

        # "sama dengan" → SAMA_DENGAN_OP (==)
        if kata == "sama":
            kata_kedua = self._intip_kata_depan()
            if kata_kedua == "dengan":
                self._lewati_spasi_horizontal()
                self._konsumsi_kata("dengan")
                self._tambah(TokenType.SAMA_DENGAN_OP, "sama dengan", baris_awal, kolom_awal)
                return

        # "tidak sama" / "tidak kurang dari" / "tidak lebih dari"
        if kata == "tidak":
            kata_kedua = self._intip_kata_depan()
            if kata_kedua == "sama":
                self._lewati_spasi_horizontal()
                self._konsumsi_kata("sama")
                self._tambah(TokenType.TIDAK_SAMA_OP, "tidak sama", baris_awal, kolom_awal)
                return
            if kata_kedua == "kurang":
                simpan_pos2 = self.pos
                simpan_baris2 = self.baris
                simpan_kolom2 = self.kolom
                self._lewati_spasi_horizontal()
                self._konsumsi_kata("kurang")
                kata_ketiga = self._intip_kata_depan()
                if kata_ketiga == "dari":
                    self._lewati_spasi_horizontal()
                    self._konsumsi_kata("dari")
                    self._tambah(TokenType.TIDAK_KURANG_DARI, "tidak kurang dari", baris_awal, kolom_awal)
                    return
                # Rollback jika bukan "tidak kurang dari"
                self.pos = simpan_pos2
                self.baris = simpan_baris2
                self.kolom = simpan_kolom2
            if kata_kedua == "lebih":
                simpan_pos2 = self.pos
                simpan_baris2 = self.baris
                simpan_kolom2 = self.kolom
                self._lewati_spasi_horizontal()
                self._konsumsi_kata("lebih")
                kata_ketiga = self._intip_kata_depan()
                if kata_ketiga == "dari":
                    self._lewati_spasi_horizontal()
                    self._konsumsi_kata("dari")
                    self._tambah(TokenType.TIDAK_LEBIH_DARI, "tidak lebih dari", baris_awal, kolom_awal)
                    return
                # Rollback jika bukan "tidak lebih dari"
                self.pos = simpan_pos2
                self.baris = simpan_baris2
                self.kolom = simpan_kolom2

        # "lebih dari" → LEBIH_DARI (>)
        if kata == "lebih":
            kata_kedua = self._intip_kata_depan()
            if kata_kedua == "dari":
                self._lewati_spasi_horizontal()
                self._konsumsi_kata("dari")
                self._tambah(TokenType.LEBIH_DARI, "lebih dari", baris_awal, kolom_awal)
                return

        # "kurang dari" → KURANG_DARI (<)
        if kata == "kurang":
            kata_kedua = self._intip_kata_depan()
            if kata_kedua == "dari":
                self._lewati_spasi_horizontal()
                self._konsumsi_kata("dari")
                self._tambah(TokenType.KURANG_DARI, "kurang dari", baris_awal, kolom_awal)
                return

        # "sisa bagi" → SISA_BAGI (%)
        if kata == "sisa":
            kata_kedua = self._intip_kata_depan()
            if kata_kedua == "bagi":
                self._lewati_spasi_horizontal()
                self._konsumsi_kata("bagi")
                self._tambah(TokenType.SISA_BAGI, "sisa bagi", baris_awal, kolom_awal)
                return

        # "pangkat" → PANGKAT_KK (**) sebagai kata kunci infix
        if kata == "pangkat":
            self._tambah(TokenType.PANGKAT_KK, "pangkat", baris_awal, kolom_awal)
            return

        # Cek apakah kata adalah kata kunci
        if kata in KATA_KUNCI:
            self._tambah(KATA_KUNCI[kata], kata, baris_awal, kolom_awal)
        else:
            self._tambah(TokenType.IDENTIFIER, kata, baris_awal, kolom_awal)

    def _intip_kata_depan(self) -> str | None:
        """Intip kata berikutnya tanpa memajukan posisi.

        Melewati spasi horizontal (spasi/tab) lalu membaca kata
        alfanumerik berikutnya. Mengembalikan None jika tidak ada kata.
        """
        idx = self.pos
        # Lewati spasi horizontal
        while idx < len(self.sumber) and self.sumber[idx] in (" ", "\t"):
            idx += 1
        # Baca kata
        mulai = idx
        while idx < len(self.sumber) and (self.sumber[idx].isalnum() or self.sumber[idx] == "_"):
            idx += 1
        if idx == mulai:
            return None
        return self.sumber[mulai:idx]

    def _lewati_spasi_horizontal(self):
        """Lewati spasi dan tab (bukan newline)."""
        while self.karakter is not None and self.karakter in (" ", "\t"):
            self.maju()

    def _konsumsi_kata(self, kata: str):
        """Konsumsi kata tertentu dari posisi saat ini."""
        for ch in kata:
            if self.karakter != ch:
                self._error(f"Diharapkan '{kata}' tapi ditemukan '{self.karakter}'")
            self.maju()

    def _intip_kata_dari_pos(self) -> str | None:
        """Intip kata yang dimulai dari posisi saat ini (tanpa memajukan)."""
        idx = self.pos
        mulai = idx
        while idx < len(self.sumber) and (self.sumber[idx].isalnum() or self.sumber[idx] == "_"):
            idx += 1
        if idx == mulai:
            return None
        return self.sumber[mulai:idx]

    # ----------------------------------------------------------
    # Operator
    # ----------------------------------------------------------

    def _coba_operator(self) -> bool:
        """Coba cocokkan operator multi-char terlebih dahulu, lalu single-char.

        Mengembalikan True jika berhasil, False jika bukan operator.
        """
        ch = self.karakter
        ch2 = self.intip(1)

        # Coba operator 2 karakter dulu
        if ch2 is not None:
            dua_char = ch + ch2
            if dua_char in OPERATORS:
                baris_awal = self.baris
                kolom_awal = self.kolom
                self.maju()
                self.maju()
                self._tambah(OPERATORS[dua_char], dua_char, baris_awal, kolom_awal)
                return True

        # Coba operator 1 karakter
        if ch in OPERATORS:
            baris_awal = self.baris
            kolom_awal = self.kolom
            self.maju()
            self._tambah(OPERATORS[ch], ch, baris_awal, kolom_awal)
            return True

        return False


# ============================================================
# Fungsi utilitas
# ============================================================

def tokenisasi(kode_sumber: str, nama_file: str = "<masukan>") -> List[Token]:
    """Fungsi shortcut untuk tokenisasi kode sumber."""
    lexer = Lexer(kode_sumber, nama_file)
    return lexer.tokenisasi()
