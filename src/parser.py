"""
parser.py — Recursive descent parser untuk bahasa pemrograman Indonesia.

Mengubah daftar token (dari lexer) menjadi Abstract Syntax Tree (AST).
Selain gaya simbolik (`buat x = 5`, `jika x > 3:`), parser juga memahami
gaya natural yang terbaca seperti kalimat biasa:

    buat umur adalah 17
    jika umur paling sedikit 17, maka tampilkan "Boleh membuat KTP"
    jika tidak, tampilkan "Belum boleh"
    tambahkan "mangga" ke keranjang
    ulangi 3 kali: tampilkan "Hore!"
"""

from __future__ import annotations
import difflib
from typing import List, Optional

from src.token_types import TokenType, KATA_KUNCI, jelaskan_tipe
from src.lexer import Token
from src.errors import KesalahanSintaks
from src.ast_nodes import (
    NodeProgram, NodeAngka, NodeTeks, NodeTeksFormat, NodeLogika, NodeKosong,
    NodeIdentifier, NodeWaktuSekarang, NodeAngkaAcak, NodeTanya, NodeOperasiBiner, NodeOperasiUnari,
    NodeDeklarasiVariabel, NodeKonstanta, NodePenugasan, NodePenugasanGabungan,
    NodeTambahkan, NodeTampilkan, NodeTunggu, NodeJika, NodePilih, NodeSelama, NodeUntuk,
    NodeUntukSetiap, NodeUlangi, NodeUlangiKali, NodeBerhenti, NodeLewati,
    NodeFungsi, NodeFungsiAnonim, NodePanggilFungsi, NodeKembalikan, NodeDaftar,
    NodeKamus, NodeAksesDaftar, NodeIrisanDaftar, NodeAksesAtribut,
    NodeKelas, NodeImpor, NodeDariImpor, NodeCoba, NodeLempar,
)


# Tipe token kata kunci — boleh dipakai sebagai nama atribut setelah titik
_TIPE_KATA_KUNCI = set(KATA_KUNCI.values())

# Kata yang mungkin dimaksud saat sebuah perintah salah ketik, mis. "tampilkn" → "tampilkan"
_KATA_PERINTAH = sorted(set(KATA_KUNCI) | {
    "ubah", "tambahkan", "kurangi", "kalikan", "bagi", "tunggu", "tanya",
})


def _petunjuk_kata_awal(tok: Token) -> str:
    """Petunjuk bila kata pertama sebuah perintah mirip kata kunci: 'Jika' atau 'tampilkn'."""
    if tok.tipe != TokenType.IDENTIFIER:
        return ""
    kata = tok.nilai
    if kata != kata.lower() and kata.lower() in KATA_KUNCI:
        return f"\n  Petunjuk: kata kunci ditulis dengan huruf kecil. Tulis '{kata.lower()}', bukan '{kata}'."
    mirip = difflib.get_close_matches(kata.lower(), _KATA_PERINTAH, n=1, cutoff=0.75)
    if mirip:
        return f"\n  Petunjuk: maksud Anda '{mirip[0]}'?"
    return ""


def jelaskan_token(tok: Token) -> str:
    """Deskripsi token yang ditemukan, untuk pesan kesalahan yang mudah dipahami."""
    if tok.tipe == TokenType.IDENTIFIER:
        return f"kata '{tok.nilai}'"
    if tok.tipe in (TokenType.ANGKA, TokenType.DESIMAL):
        return f"angka {tok.nilai}"
    if tok.tipe == TokenType.TEKS:
        return f'teks "{tok.nilai}"'
    if tok.tipe in (TokenType.TEKS_FORMAT, TokenType.INDENT, TokenType.DEDENT,
                    TokenType.BARIS_BARU, TokenType.EOF):
        return jelaskan_tipe(tok.tipe)
    if isinstance(tok.nilai, str) and tok.nilai[:1].isalpha():
        return f"kata '{tok.nilai}'"
    return f"tanda '{tok.nilai}'"


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

    def intip(self, offset: int = 1) -> Token:
        """Lihat token di posisi pos + offset tanpa memajukan posisi."""
        return self.tokens[min(self.pos + offset, len(self.tokens) - 1)]

    def periksa(self, *tipe: TokenType) -> bool:
        return self.saat_ini().tipe in tipe

    def periksa_kata(self, *kata: str) -> bool:
        """Cek kata penghubung yang bukan kata kunci, mis. 'kali' pada 'ulangi 3 kali'."""
        tok = self.saat_ini()
        return tok.tipe == TokenType.IDENTIFIER and tok.nilai in kata

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
        if not pesan and tipe == TokenType.IDENTIFIER and tok.tipe in _TIPE_KATA_KUNCI \
                and isinstance(tok.nilai, str) and tok.nilai.isidentifier():
            pesan = (f"'{tok.nilai}' adalah kata kunci, jadi tidak bisa dipakai sebagai nama. "
                     f"Coba nama lain, misalnya '{tok.nilai}_saya'.")
        if not pesan:
            pesan = f"Diharapkan {jelaskan_tipe(tipe)}, tetapi yang ditemukan {jelaskan_token(tok)}"
        self._error(pesan, tok)

    def lewati_baris_baru(self):
        while self.periksa(TokenType.BARIS_BARU):
            self.maju()

    def _error(self, pesan: str, tok: Token = None):
        if tok is None:
            tok = self.saat_ini()
        baris_kode = self.daftar_baris[tok.baris - 1] if tok.baris - 1 < len(self.daftar_baris) else ""
        kesalahan = KesalahanSintaks(pesan, baris=tok.baris, kolom=tok.kolom, baris_kode=baris_kode)
        # Kesalahan di akhir masukan berarti kodenya belum selesai ditulis (dipakai REPL multi-baris).
        # Sesudah token terakhir hanya ada penutup blok (DEDENT), baris baru, dan EOF.
        sisa = self.tokens[self.pos:] if tok is self.saat_ini() else [tok]
        kesalahan.belum_selesai = all(
            t.tipe in (TokenType.DEDENT, TokenType.BARIS_BARU, TokenType.EOF) for t in sisa
        )
        raise kesalahan

    def _harapkan_akhir_pernyataan(self, awal: int):
        """Pastikan perintah yang dimulai di token `awal` berakhir di sini."""
        if self.periksa(TokenType.BARIS_BARU, TokenType.DEDENT, TokenType.EOF):
            return
        # Perintah yang diakhiri blok menjorok (jika, selama, ...) sudah menelan baris barunya
        if self.pos > 0 and self.tokens[self.pos - 1].tipe in (TokenType.BARIS_BARU, TokenType.DEDENT):
            return
        self._error(
            f"Perintah seharusnya berakhir di sini, tetapi masih ada {jelaskan_token(self.saat_ini())}. "
            "Tulis setiap perintah di barisnya sendiri."
            + _petunjuk_kata_awal(self.tokens[awal])
        )

    # ============================
    # Program
    # ============================

    def parse(self) -> NodeProgram:
        pernyataan = []
        self.lewati_baris_baru()
        while not self.periksa(TokenType.EOF):
            awal = self.pos
            stmt = self.parse_pernyataan()
            if stmt is not None:
                pernyataan.append(stmt)
            self._harapkan_akhir_pernyataan(awal)
            self.lewati_baris_baru()
        return NodeProgram(pernyataan)

    def parse_ekspresi_tunggal(self):
        """Parse tepat satu ekspresi sampai akhir input (untuk isi {...} pada teks format)."""
        self.lewati_baris_baru()
        ekspresi = self.parse_ekspresi()
        self.lewati_baris_baru()
        if not self.periksa(TokenType.EOF):
            self._error(
                "Isi {...} pada teks format harus berupa satu nilai atau perhitungan, "
                f"tetapi masih ada {jelaskan_token(self.saat_ini())}"
            )
        return ekspresi

    # ============================
    # Blok (indented block)
    # ============================

    def parse_blok(self) -> list:
        """Parse isi blok setelah kepala perintah (jika, selama, fungsi, ...).

        Pembuka blok boleh ':' atau gaya natural 'maka' / 'lakukan', boleh juga
        didahului koma. Isinya satu perintah di baris yang sama, atau blok
        menjorok di baris-baris berikutnya:

            jika hujan: tampilkan "Bawa payung"
            jika hujan, maka tampilkan "Bawa payung"
            jika hujan, tampilkan "Bawa payung"
            selama lapar lakukan:
                makan()
        """
        ada_koma = self.cocok(TokenType.KOMA)
        ada_kata = self.cocok(TokenType.MAKA, TokenType.LAKUKAN)
        ada_titik_dua = self.cocok(TokenType.TITIK_DUA)
        if not (ada_koma or ada_kata or ada_titik_dua):
            self._error(
                "Diharapkan tanda ':' (atau kata 'maka' / 'lakukan') untuk memulai blok, "
                f"tetapi yang ditemukan {jelaskan_token(self.saat_ini())}"
            )
        if not self.periksa(TokenType.BARIS_BARU, TokenType.EOF):
            stmt = self.parse_pernyataan()
            return [stmt] if stmt else []
        if ada_koma and not (ada_kata or ada_titik_dua):
            self._error("Setelah koma, tulis perintahnya di baris yang sama, atau akhiri dengan 'maka:' / 'lakukan:'")
        self.lewati_baris_baru()
        self.harapkan(TokenType.INDENT, "Isi blok harus ditulis menjorok ke dalam (diawali spasi) di baris berikutnya")
        stmts = []
        while not self.periksa(TokenType.DEDENT, TokenType.EOF):
            self.lewati_baris_baru()
            if self.periksa(TokenType.DEDENT, TokenType.EOF):
                break
            awal = self.pos
            stmt = self.parse_pernyataan()
            if stmt is not None:
                stmts.append(stmt)
            self._harapkan_akhir_pernyataan(awal)
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
        if t == TokenType.INDENT:
            self._error("Baris ini menjorok ke dalam, padahal tidak sedang berada di dalam blok. Hapus spasi di awal baris.")
        if t == TokenType.IDENTIFIER:
            kalimat = self._coba_kalimat_natural()
            if kalimat is not None:
                return kalimat
        return self.parse_penugasan_atau_ekspresi()

    # ============================
    # Deklarasi
    # ============================

    def parse_deklarasi_buat(self):
        tok = self.maju()  # BUAT
        nama = self.harapkan(TokenType.IDENTIFIER).nilai
        self._harapkan_pengisian()
        ekspresi = self.parse_ekspresi()
        return NodeDeklarasiVariabel(nama, ekspresi, baris=tok.baris, kolom=tok.kolom)

    def parse_konstanta(self):
        tok = self.maju()  # TETAP
        nama = self.harapkan(TokenType.IDENTIFIER).nilai
        self._harapkan_pengisian()
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
        self._harapkan_pengisian()
        ekspresi = self.parse_ekspresi()
        return NodeDeklarasiVariabel(nama, ekspresi, tipe_eksplisit=tipe, baris=tok.baris, kolom=tok.kolom)

    def _harapkan_pengisian(self):
        """Tanda pengisian nilai pada deklarasi: '=' atau gaya natural 'adalah'."""
        if self.cocok(TokenType.SAMA_DENGAN, TokenType.ADALAH):
            return
        self._error(
            f"Setelah nama variabel, tulis '=' atau 'adalah', tetapi yang ditemukan "
            f"{jelaskan_token(self.saat_ini())}. Contoh: buat umur adalah 17"
        )

    # ============================
    # Penugasan / Ekspresi Statement
    # ============================

    def parse_penugasan_atau_ekspresi(self):
        # Gaya natural: "umur adalah 18" di awal kalimat berarti mengisi nilai,
        # sama seperti "umur = 18". Di dalam kondisi, "adalah" berarti "==".
        if self.periksa(TokenType.IDENTIFIER, TokenType.DIRI):
            awal = self.pos
            try:
                target = self.parse_postfix()
            except KesalahanSintaks:
                target = None
            if target is not None and self._bisa_diisi(target) and self.periksa(TokenType.ADALAH):
                tok = self.maju()
                nilai = self.parse_ekspresi()
                return NodePenugasan(target, nilai, baris=tok.baris, kolom=tok.kolom)
            self.pos = awal

        tok_awal = self.saat_ini()
        ekspresi = self.parse_ekspresi()
        if self.periksa(TokenType.SAMA_DENGAN):
            tok = self.maju()
            self._pastikan_bisa_diisi(ekspresi, tok_awal)
            nilai = self.parse_ekspresi()
            return NodePenugasan(ekspresi, nilai, baris=tok.baris, kolom=tok.kolom)
        if self.periksa(TokenType.TAMBAH_SAMA, TokenType.KURANG_SAMA, TokenType.KALI_SAMA,
                        TokenType.BAGI_SAMA, TokenType.MODULO_SAMA):
            tok = self.maju()
            self._pastikan_bisa_diisi(ekspresi, tok_awal)
            nilai = self.parse_ekspresi()
            return NodePenugasanGabungan(ekspresi, tok.nilai, nilai, baris=tok.baris, kolom=tok.kolom)
        return ekspresi

    @staticmethod
    def _bisa_diisi(node) -> bool:
        return isinstance(node, (NodeIdentifier, NodeAksesDaftar, NodeAksesAtribut))

    def _pastikan_bisa_diisi(self, node, tok: Token):
        if not self._bisa_diisi(node):
            self._error(
                "Bagian ini tidak bisa diberi nilai. Yang bisa diberi nilai hanyalah variabel, "
                "elemen daftar (mis. d[0]), atau atribut objek (mis. diri.nama).",
                tok,
            )

    # ============================
    # Kalimat perintah natural
    # ============================

    # Kata kerja pembuka kalimat → kata penghubung yang dikenali. Kata-kata ini
    # sengaja tidak dijadikan kata kunci, jadi "tambahkan(5)" atau "bagi = 2"
    # tetap dibaca sebagai pemanggilan fungsi / variabel biasa.
    _KALIMAT_NATURAL = {
        "ubah": ("menjadi", "jadi"),
        "tambahkan": ("ke", "dengan"),
        "kurangi": ("dari", "dengan"),
        "kalikan": ("dengan",),
        "bagi": ("dengan",),
    }
    _CONTOH_KALIMAT = {
        "ubah": "ubah umur menjadi 18",
        "tambahkan": "tambahkan 1 ke skor",
        "kurangi": "kurangi nyawa dengan 1",
        "kalikan": "kalikan harga dengan 2",
        "bagi": "bagi total dengan 4",
    }
    _OPERATOR_KALIMAT = {"kurangi": "-=", "kalikan": "*=", "bagi": "/="}

    # Token yang pasti memulai sebuah nilai dan tidak mungkin melanjutkan ekspresi
    _AWAL_NILAI = (
        TokenType.IDENTIFIER, TokenType.WAKTU_SEKARANG, TokenType.ANGKA_ACAK,
        TokenType.DIRI, TokenType.SUPER, TokenType.ANGKA,
        TokenType.DESIMAL, TokenType.TEKS, TokenType.TEKS_FORMAT, TokenType.BENAR,
        TokenType.SALAH, TokenType.KOSONG, TokenType.KURAWAL_BUKA, TokenType.FUNGSI,
        TokenType.MASUKAN, TokenType.MASUKAN_ANGKA, TokenType.MASUKAN_DESIMAL,
    )

    # Satuan untuk "tunggu 1 detik"; tanpa satuan berarti detik
    _SATUAN_WAKTU = {"detik": 1, "milidetik": 0.001, "menit": 60, "jam": 3600}

    def _coba_kalimat_tunggu(self):
        """Parse "tunggu 1 detik" / "tunggu 2 menit". None jika 'tunggu' dipakai biasa, mis. tunggu(1)."""
        tok = self.saat_ini()
        berikut = self.intip()
        if berikut.tipe in (TokenType.KURUNG_BUKA, TokenType.KURANG):
            if self._cari_penghubung(tuple(self._SATUAN_WAKTU), self.pos + 1) is None:
                return None
        elif berikut.tipe not in self._AWAL_NILAI:
            return None
        self.maju()  # tunggu
        lama = self.parse_ekspresi()
        faktor = 1
        if self.periksa_kata(*self._SATUAN_WAKTU):
            faktor = self._SATUAN_WAKTU[self.maju().nilai]
        return NodeTunggu(lama, faktor, baris=tok.baris, kolom=tok.kolom)

    def _coba_kalimat_natural(self):
        """Parse kalimat seperti "tambahkan 1 ke skor". None jika bukan kalimat natural."""
        tok = self.saat_ini()
        if tok.nilai == "tunggu":
            return self._coba_kalimat_tunggu()
        penghubung = self._KALIMAT_NATURAL.get(tok.nilai)
        if penghubung is None:
            return None
        berikut = self.intip()
        if berikut.tipe in (TokenType.KURUNG_BUKA, TokenType.SIKU_BUKA, TokenType.KURANG):
            # "tambahkan(5)" = panggil fungsi; "tambahkan (a + b) ke total" = kalimat
            if self._cari_penghubung(penghubung, self.pos + 1) is None:
                return None
        elif berikut.tipe not in self._AWAL_NILAI:
            return None  # mis. "bagi = 2": variabel biasa bernama 'bagi'

        self.maju()  # kata kerja
        kata = self._cari_penghubung(penghubung, self.pos)
        if kata is None:
            self._error(f"Kalimat '{tok.nilai}' belum lengkap. Contoh: {self._CONTOH_KALIMAT[tok.nilai]}", tok)

        if kata in ("ke", "dari"):
            # Nilai lebih dulu: "tambahkan 1 ke skor", "kurangi 5 dari uang"
            nilai = self.parse_ekspresi()
            self._harapkan_penghubung(kata, tok)
            if kata == "ke":
                self.cocok(TokenType.DALAM)  # "ke dalam keranjang"
            target = self._parse_target()
        else:
            # Target lebih dulu: "ubah umur menjadi 18", "kurangi nyawa dengan 1"
            target = self._parse_target()
            self._harapkan_penghubung(kata, tok)
            nilai = self.parse_ekspresi()

        if tok.nilai == "ubah":
            return NodePenugasan(target, nilai, baris=tok.baris, kolom=tok.kolom)
        if tok.nilai == "tambahkan":
            return NodeTambahkan(nilai, target, baris=tok.baris, kolom=tok.kolom)
        return NodePenugasanGabungan(target, self._OPERATOR_KALIMAT[tok.nilai], nilai,
                                     baris=tok.baris, kolom=tok.kolom)

    def _cari_penghubung(self, penghubung: tuple, mulai: int) -> Optional[str]:
        """Cari kata penghubung pertama (di luar kurung) pada baris yang sama."""
        kedalaman = 0
        for tok in self.tokens[mulai:]:
            if tok.tipe in (TokenType.BARIS_BARU, TokenType.EOF):
                break
            if tok.tipe in (TokenType.KURUNG_BUKA, TokenType.SIKU_BUKA, TokenType.KURAWAL_BUKA):
                kedalaman += 1
            elif tok.tipe in (TokenType.KURUNG_TUTUP, TokenType.SIKU_TUTUP, TokenType.KURAWAL_TUTUP):
                kedalaman -= 1
            elif (kedalaman == 0 and tok.tipe in (TokenType.IDENTIFIER, TokenType.DARI)
                  and tok.nilai in penghubung):
                return tok.nilai
        return None

    def _harapkan_penghubung(self, kata: str, tok_kata_kerja: Token):
        tok = self.saat_ini()
        if tok.tipe in (TokenType.IDENTIFIER, TokenType.DARI) and tok.nilai == kata:
            self.maju()
            return
        self._error(
            f"Diharapkan kata '{kata}', tetapi yang ditemukan {jelaskan_token(tok)}. "
            f"Contoh: {self._CONTOH_KALIMAT[tok_kata_kerja.nilai]}"
        )

    def _parse_target(self):
        """Parse sesuatu yang bisa diberi nilai: variabel, elemen daftar, atau atribut."""
        tok = self.saat_ini()
        target = self.parse_postfix()
        self._pastikan_bisa_diisi(target, tok)
        return target

    # ============================
    # Tampilkan
    # ============================

    def parse_tampilkan(self):
        tok = self.maju()  # TAMPILKAN (tampilkan / tulis / cetak)
        baris_baru = tok.nilai != "cetak"  # 'cetak' tidak pindah baris
        args = []
        if not self.periksa(TokenType.BARIS_BARU, TokenType.DEDENT, TokenType.EOF):
            args.append(self.parse_ekspresi())
            while self.cocok(TokenType.KOMA):
                args.append(self.parse_ekspresi())
        return NodeTampilkan(args, baris=tok.baris, kolom=tok.kolom, baris_baru=baris_baru)

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
        elif self._adalah_jika_tidak():
            self.maju()  # jika / kalau
            self.maju()  # tidak
            blok_selainnya = self.parse_blok()
        return NodeJika(kondisi, blok_jika, cabang, blok_selainnya, baris=tok.baris, kolom=tok.kolom)

    def _adalah_jika_tidak(self) -> bool:
        """'jika tidak:' / 'kalau tidak, ...' berarti selainnya (else).

        Berbeda dengan 'jika tidak hujan:' yang merupakan kondisi baru.
        """
        kedua = self.intip(1)
        return (
            self.periksa(TokenType.JIKA)
            and kedua.tipe == TokenType.BUKAN and kedua.nilai == "tidak"
            and self.intip(2).tipe in (TokenType.TITIK_DUA, TokenType.KOMA, TokenType.MAKA)
        )

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
                nilai_kasus = self._parse_nilai_ketika()
                blok = self.parse_blok()
                kasus.append((nilai_kasus, blok))
            elif self.periksa(TokenType.BAWAAN, TokenType.SELAINNYA):
                self.maju()
                bawaan = self.parse_blok()
            else:
                self._error("Diharapkan 'ketika' atau 'bawaan' (boleh juga 'selainnya') dalam blok 'pilih'")
            self.lewati_baris_baru()
        if self.periksa(TokenType.DEDENT):
            self.maju()
        return NodePilih(ekspresi, kasus, bawaan, baris=tok.baris, kolom=tok.kolom)

    # Nilai yang boleh menyusul koma pada 'ketika "Sabtu", "Minggu"'. Selain ini, koma
    # dianggap pembuka blok satu baris: 'ketika "Senin", tampilkan "Awal pekan"'.
    _NILAI_SETELAH_KOMA = (
        TokenType.ANGKA, TokenType.DESIMAL, TokenType.TEKS,
        TokenType.BENAR, TokenType.SALAH, TokenType.KOSONG,
    )

    def _parse_nilai_ketika(self) -> list:
        """'ketika "Sabtu" atau "Minggu"' / 'ketika "Sabtu", "Minggu"' → cocok dengan salah satunya."""
        nilai = [self.parse_dan()]
        while True:
            if self.cocok(TokenType.ATAU):
                nilai.append(self.parse_dan())
            elif self.periksa(TokenType.KOMA) and self.intip().tipe in self._NILAI_SETELAH_KOMA:
                self.maju()
                nilai.append(self.parse_dan())
            else:
                return nilai

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
        if not self.periksa(TokenType.TITIK_DUA):
            # ulangi <jumlah> kali: ...
            jumlah = self.parse_ekspresi()
            if not self.periksa_kata("kali"):
                self._error("Setelah 'ulangi <jumlah>' diharapkan kata 'kali'. Contoh: ulangi 3 kali: ...")
            self.maju()  # kali
            blok = self.parse_blok()
            return NodeUlangiKali(jumlah, blok, baris=tok.baris, kolom=tok.kolom)

        # ulangi: ... selama <kondisi>   (ulangi selama kondisi benar)
        # ulangi: ... sampai <kondisi>   (ulangi sampai kondisi menjadi benar)
        blok = self.parse_blok()
        self.lewati_baris_baru()
        if self.cocok(TokenType.SELAMA):
            kondisi = self.parse_ekspresi()
        elif self.periksa(TokenType.SAMPAI):
            tok_sampai = self.maju()
            kondisi = NodeOperasiUnari("bukan", self.parse_ekspresi(),
                                       baris=tok_sampai.baris, kolom=tok_sampai.kolom)
        else:
            self._error("Blok 'ulangi:' harus ditutup dengan 'selama <kondisi>' atau 'sampai <kondisi>'")
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
        modul = self.harapkan(TokenType.IDENTIFIER, "Setelah 'impor' tulis nama modul, mis. impor matematika").nilai
        tok_akhir = None
        while self.cocok(TokenType.TITIK):
            tok_akhir = self.saat_ini()
            modul += "." + self._harapkan_nama_atribut()
        alias = None
        if self.cocok(TokenType.SEBAGAI):
            alias = self.harapkan(TokenType.IDENTIFIER).nilai
        elif tok_akhir is not None and tok_akhir.tipe != TokenType.IDENTIFIER:
            self._error(
                f"'{tok_akhir.nilai}' adalah kata kunci, jadi perlu nama lain. "
                f"Contoh: impor {modul} sebagai {tok_akhir.nilai}_saya",
                tok_akhir,
            )
        return NodeImpor(modul, alias, baris=tok.baris, kolom=tok.kolom)

    def parse_dari_impor(self):
        tok = self.maju()  # DARI
        modul = self.harapkan(TokenType.IDENTIFIER, "Setelah 'dari' tulis nama modul, mis. dari acak impor bilangan").nilai
        while self.cocok(TokenType.TITIK):
            modul += "." + self._harapkan_nama_atribut()
        self.harapkan(TokenType.IMPOR)
        tok_nama = self.saat_ini()
        nama = self._harapkan_nama_atribut()  # boleh kata kunci asal diberi nama lain
        alias = None
        if self.cocok(TokenType.SEBAGAI):
            alias = self.harapkan(TokenType.IDENTIFIER).nilai
        elif tok_nama.tipe != TokenType.IDENTIFIER:
            self._error(
                f"'{nama}' adalah kata kunci, jadi perlu nama lain. "
                f"Contoh: dari {modul} impor {nama} sebagai {nama}_{modul}, atau pakai {modul}.{nama}(...)",
                tok_nama,
            )
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
        TokenType.ADALAH: "==",
        TokenType.TIDAK_SAMA_OP: "!=",
        TokenType.LEBIH_DARI: ">",
        TokenType.KURANG_DARI: "<",
        TokenType.TIDAK_KURANG_DARI: ">=",
        TokenType.TIDAK_LEBIH_DARI: "<=",
    }
    _OPS_SIMBOL = (TokenType.SAMA, TokenType.TIDAK_SAMA, TokenType.LEBIH_BESAR,
                   TokenType.LEBIH_KECIL, TokenType.LEBIH_BESAR_SAMA, TokenType.LEBIH_KECIL_SAMA)

    def parse_perbandingan(self):
        kiri = self.parse_penjumlahan()
        while True:
            tok = self.saat_ini()
            if tok.tipe in (TokenType.ADA, TokenType.TIDAK_ADA):
                # "apel" ada dalam keranjang / "apel" tidak ada dalam keranjang
                self.maju()
                self.harapkan(TokenType.DALAM, f"Setelah '{tok.nilai}' diharapkan kata 'dalam', "
                                               f"mis. \"apel\" {tok.nilai} dalam keranjang")
                op = "ada dalam" if tok.tipe == TokenType.ADA else "tidak ada dalam"
                kanan = self.parse_penjumlahan()
                kiri = NodeOperasiBiner(kiri, op, kanan, baris=tok.baris, kolom=tok.kolom)
            elif tok.tipe in (TokenType.HABIS_DIBAGI, TokenType.TIDAK_HABIS_DIBAGI):
                # "x habis dibagi y" → x % y == 0
                self.maju()
                kanan = self.parse_penjumlahan()
                sisa = NodeOperasiBiner(kiri, "%", kanan, baris=tok.baris, kolom=tok.kolom)
                op = "==" if tok.tipe == TokenType.HABIS_DIBAGI else "!="
                nol = NodeAngka(0, baris=tok.baris, kolom=tok.kolom)
                kiri = NodeOperasiBiner(sisa, op, nol, baris=tok.baris, kolom=tok.kolom)
            else:
                if tok.tipe in self._OPS_SIMBOL:
                    op = tok.nilai
                elif tok.tipe in self._OP_TEKS_KE_SIMBOL:
                    op = self._OP_TEKS_KE_SIMBOL[tok.tipe]
                elif tok.tipe == TokenType.BUKAN and tok.nilai == "bukan":
                    op = "!="  # hari bukan "Minggu"
                else:
                    break
                self.maju()
                kanan = self.parse_penjumlahan()
                kiri = NodeOperasiBiner(kiri, op, kanan, baris=tok.baris, kolom=tok.kolom)
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
            eksponen = self.parse_pangkat()  # asosiatif kanan: 2 pangkat 3 pangkat 2 = 2 pangkat 9
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
                attr = self._harapkan_nama_atribut()
                node = NodeAksesAtribut(node, attr, baris=node.baris, kolom=node.kolom)
            else:
                break
        return node

    def _harapkan_nama_atribut(self) -> str:
        """Nama atribut/metode setelah titik. Kata kunci juga boleh (acak.pilih, berkas.tulis)."""
        tok = self.saat_ini()
        if tok.tipe == TokenType.IDENTIFIER or (
            tok.tipe in _TIPE_KATA_KUNCI and isinstance(tok.nilai, str) and tok.nilai.isidentifier()
        ):
            return self.maju().nilai
        return self.harapkan(
            TokenType.IDENTIFIER,
            f"Setelah tanda '.' diharapkan nama atribut atau metode, tetapi yang ditemukan {jelaskan_token(tok)}",
        ).nilai

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

        # tanya "Siapa namamu?" / tanya angka "Berapa umurmu?" — harus dicek sebelum nama biasa.
        # Hanya bila langsung diikuti teks, agar variabel bernama 'tanya' tetap aman.
        teks = (TokenType.TEKS, TokenType.TEKS_FORMAT)
        if tok.tipe == TokenType.IDENTIFIER and tok.nilai == "tanya" and (
            self.intip().tipe in teks
            or (self.intip().tipe == TokenType.IDENTIFIER and self.intip().nilai == "angka"
                and self.intip(2).tipe in teks)
        ):
            self.maju()
            jenis = "teks"
            if self.periksa_kata("angka"):
                self.maju()
                jenis = "angka"
            pertanyaan = self.parse_postfix()
            return NodeTanya(pertanyaan, jenis, baris=tok.baris, kolom=tok.kolom)

        # Identifier
        if tok.tipe == TokenType.IDENTIFIER:
            self.maju()
            return NodeIdentifier(tok.nilai, baris=tok.baris, kolom=tok.kolom)

        # jam sekarang / waktu sekarang / hari ini / tanggal hari ini / bulan ini / tahun ini
        if tok.tipe == TokenType.WAKTU_SEKARANG:
            self.maju()
            return NodeWaktuSekarang(tok.nilai.split()[0], baris=tok.baris, kolom=tok.kolom)

        # angka acak dari 1 sampai 6
        if tok.tipe == TokenType.ANGKA_ACAK:
            self.maju()
            contoh = "Contoh: angka acak dari 1 sampai 6"
            self.harapkan(TokenType.DARI, f"Setelah 'angka acak' diharapkan kata 'dari'. {contoh}")
            minimum = self.parse_penjumlahan()
            self.harapkan(TokenType.SAMPAI, f"Diharapkan kata 'sampai' untuk batas atas. {contoh}")
            maksimum = self.parse_penjumlahan()
            return NodeAngkaAcak(minimum, maksimum, baris=tok.baris, kolom=tok.kolom)

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

        self._error(f"Di sini diharapkan sebuah nilai (angka, teks, nama, dll.), tetapi yang ditemukan {jelaskan_token(tok)}")

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
        self.cocok(TokenType.KEMBALIKAN)  # "fungsi(x): kembalikan x * x" juga boleh
        ekspresi = self.parse_ekspresi()
        return NodeFungsiAnonim(params, ekspresi, baris=tok.baris, kolom=tok.kolom)


# ============================
# Fungsi utilitas
# ============================

def parse(tokens: List[Token], kode_sumber: str = "") -> NodeProgram:
    """Shortcut: parse daftar token menjadi AST."""
    parser = Parser(tokens, kode_sumber)
    return parser.parse()
