"""
test_lexer.py — Unit test untuk Lexer bahasa Indonesia.
"""

import pytest
from src.lexer import Lexer, tokenisasi, Token
from src.token_types import TokenType
from src.errors import KesalahanSintaks


# ============================================================
# Helper
# ============================================================

def tipe_token(kode: str) -> list[TokenType]:
    """Tokenisasi kode dan kembalikan daftar tipe token (tanpa BARIS_BARU, INDENT, DEDENT, EOF)."""
    tokens = tokenisasi(kode)
    return [
        t.tipe for t in tokens
        if t.tipe not in (TokenType.BARIS_BARU, TokenType.INDENT, TokenType.DEDENT, TokenType.EOF)
    ]


def nilai_token(kode: str) -> list:
    """Tokenisasi kode dan kembalikan daftar nilai token (tanpa BARIS_BARU, INDENT, DEDENT, EOF)."""
    tokens = tokenisasi(kode)
    return [
        t.nilai for t in tokens
        if t.tipe not in (TokenType.BARIS_BARU, TokenType.INDENT, TokenType.DEDENT, TokenType.EOF)
    ]


# ============================================================
# Test: Angka
# ============================================================

class TestAngka:
    def test_integer(self):
        assert tipe_token("42") == [TokenType.ANGKA]
        assert nilai_token("42") == [42]

    def test_integer_nol(self):
        assert nilai_token("0") == [0]

    def test_integer_besar(self):
        assert nilai_token("1000000") == [1000000]

    def test_desimal(self):
        assert tipe_token("3.14") == [TokenType.DESIMAL]
        assert nilai_token("3.14") == [3.14]

    def test_desimal_awal_nol(self):
        assert nilai_token("0.5") == [0.5]

    def test_beberapa_angka(self):
        tipe = tipe_token("10 20 30")
        assert tipe == [TokenType.ANGKA, TokenType.ANGKA, TokenType.ANGKA]
        assert nilai_token("10 20 30") == [10, 20, 30]


# ============================================================
# Test: Teks / String
# ============================================================

class TestTeks:
    def test_kutip_ganda(self):
        assert tipe_token('"Halo"') == [TokenType.TEKS]
        assert nilai_token('"Halo"') == ["Halo"]

    def test_kutip_tunggal(self):
        assert nilai_token("'Dunia'") == ["Dunia"]

    def test_string_kosong(self):
        assert nilai_token('""') == [""]

    def test_escape_newline(self):
        assert nilai_token(r'"baris\nsatu"') == ["baris\nsatu"]

    def test_escape_tab(self):
        assert nilai_token(r'"tab\tsini"') == ["tab\tsini"]

    def test_escape_backslash(self):
        assert nilai_token(r'"path\\file"') == ["path\\file"]

    def test_escape_kutip(self):
        assert nilai_token(r'"dia berkata \"halo\""') == ['dia berkata "halo"']

    def test_string_tidak_ditutup(self):
        with pytest.raises(KesalahanSintaks):
            tokenisasi('"halo')

    def test_string_multiline_error(self):
        with pytest.raises(KesalahanSintaks):
            tokenisasi('"halo\ndunia"')


# ============================================================
# Test: Format String (format"..." dan f"...")
# ============================================================

class TestFormatString:
    def test_fstring_sederhana(self):
        """f\"...\" tetap didukung untuk backward compatibility."""
        assert tipe_token('f"Halo {nama}"') == [TokenType.TEKS_FORMAT]
        assert nilai_token('f"Halo {nama}"') == ["Halo {nama}"]

    def test_format_string_sederhana(self):
        """format\"...\" adalah sintaks baru yang direkomendasikan."""
        assert tipe_token('format"Halo {nama}"') == [TokenType.TEKS_FORMAT]
        assert nilai_token('format"Halo {nama}"') == ["Halo {nama}"]

    def test_format_string_banyak_ekspresi(self):
        assert nilai_token('format"Umur {umur}, Kota {kota}"') == ["Umur {umur}, Kota {kota}"]

    def test_fstring_banyak_ekspresi(self):
        assert nilai_token('f"Umur {umur}, Kota {kota}"') == ["Umur {umur}, Kota {kota}"]

    def test_format_string_kutip_tunggal(self):
        assert nilai_token("format'Hasil: {x + y}'") == ["Hasil: {x + y}"]

    def test_fstring_kutip_tunggal(self):
        assert nilai_token("f'Hasil: {x + y}'") == ["Hasil: {x + y}"]


# ============================================================
# Test: Operator
# ============================================================

class TestOperator:
    def test_aritmatika(self):
        tipe = tipe_token("+ - * / % **")
        assert tipe == [
            TokenType.TAMBAH, TokenType.KURANG, TokenType.KALI,
            TokenType.BAGI, TokenType.MODULO, TokenType.PANGKAT,
        ]

    def test_perbandingan(self):
        tipe = tipe_token("== != > < >= <=")
        assert tipe == [
            TokenType.SAMA, TokenType.TIDAK_SAMA,
            TokenType.LEBIH_BESAR, TokenType.LEBIH_KECIL,
            TokenType.LEBIH_BESAR_SAMA, TokenType.LEBIH_KECIL_SAMA,
        ]

    def test_penugasan(self):
        tipe = tipe_token("= += -= *= /= %=")
        assert tipe == [
            TokenType.SAMA_DENGAN, TokenType.TAMBAH_SAMA,
            TokenType.KURANG_SAMA, TokenType.KALI_SAMA,
            TokenType.BAGI_SAMA, TokenType.MODULO_SAMA,
        ]

    def test_pangkat_vs_kali(self):
        """** harus dikenali sebelum * """
        tipe = tipe_token("5 ** 2")
        assert tipe == [TokenType.ANGKA, TokenType.PANGKAT, TokenType.ANGKA]


# ============================================================
# Test: Operator Teks Indonesia
# ============================================================

class TestOperatorTeksIndonesia:
    def test_sama_dengan(self):
        tipe = tipe_token("x sama dengan y")
        assert TokenType.SAMA_DENGAN_OP in tipe

    def test_tidak_sama(self):
        tipe = tipe_token("x tidak sama y")
        assert TokenType.TIDAK_SAMA_OP in tipe

    def test_lebih_dari(self):
        tipe = tipe_token("x lebih dari y")
        assert TokenType.LEBIH_DARI in tipe

    def test_kurang_dari(self):
        tipe = tipe_token("x kurang dari y")
        assert TokenType.KURANG_DARI in tipe

    def test_tidak_kurang_dari(self):
        tipe = tipe_token("x tidak kurang dari y")
        assert TokenType.TIDAK_KURANG_DARI in tipe

    def test_tidak_lebih_dari(self):
        tipe = tipe_token("x tidak lebih dari y")
        assert TokenType.TIDAK_LEBIH_DARI in tipe

    def test_sisa_bagi(self):
        tipe = tipe_token("10 sisa bagi 3")
        assert TokenType.SISA_BAGI in tipe

    def test_pangkat_kata_kunci(self):
        tipe = tipe_token("2 pangkat 10")
        assert TokenType.PANGKAT_KK in tipe


# ============================================================
# Test: Tanda Baca
# ============================================================

class TestTandaBaca:
    def test_semua_tanda_baca(self):
        tipe = tipe_token(": , . ( ) [ ] { }")
        assert tipe == [
            TokenType.TITIK_DUA, TokenType.KOMA, TokenType.TITIK,
            TokenType.KURUNG_BUKA, TokenType.KURUNG_TUTUP,
            TokenType.SIKU_BUKA, TokenType.SIKU_TUTUP,
            TokenType.KURAWAL_BUKA, TokenType.KURAWAL_TUTUP,
        ]


# ============================================================
# Test: Kata Kunci
# ============================================================

class TestKataKunci:
    def test_buat(self):
        tipe = tipe_token("buat x = 5")
        assert tipe == [
            TokenType.BUAT, TokenType.IDENTIFIER,
            TokenType.SAMA_DENGAN, TokenType.ANGKA,
        ]

    def test_tetap(self):
        assert tipe_token("tetap PI = 3.14")[0] == TokenType.TETAP

    def test_jika_selainnya(self):
        tipe = tipe_token("jika selainnya")
        assert tipe == [TokenType.JIKA, TokenType.SELAINNYA]

    def test_selama(self):
        assert tipe_token("selama")[0] == TokenType.SELAMA

    def test_fungsi(self):
        assert tipe_token("fungsi")[0] == TokenType.FUNGSI

    def test_kembalikan(self):
        assert tipe_token("kembalikan")[0] == TokenType.KEMBALIKAN

    def test_kelas(self):
        assert tipe_token("kelas")[0] == TokenType.KELAS

    def test_benar_salah(self):
        tipe = tipe_token("benar salah")
        assert tipe == [TokenType.BENAR, TokenType.SALAH]

    def test_kosong(self):
        assert tipe_token("kosong")[0] == TokenType.KOSONG

    def test_dan_atau_bukan(self):
        tipe = tipe_token("dan atau bukan")
        assert tipe == [TokenType.DAN, TokenType.ATAU, TokenType.BUKAN]

    def test_sinonim_tampilkan(self):
        """cetak dan tulis harus menghasilkan token TAMPILKAN."""
        assert tipe_token("tampilkan")[0] == TokenType.TAMPILKAN
        assert tipe_token("cetak")[0] == TokenType.TAMPILKAN
        assert tipe_token("tulis")[0] == TokenType.TAMPILKAN

    def test_impor(self):
        tipe = tipe_token("impor matematika")
        assert tipe == [TokenType.IMPOR, TokenType.IDENTIFIER]

    def test_coba_tangkap(self):
        tipe = tipe_token("coba tangkap akhirnya")
        assert tipe == [TokenType.COBA, TokenType.TANGKAP, TokenType.AKHIRNYA]


# ============================================================
# Test: Kata Kunci Multi-Kata
# ============================================================

class TestKataKunciMultiKata:
    def test_atau_jika(self):
        tipe = tipe_token("atau jika")
        assert tipe == [TokenType.ATAU_JIKA]

    def test_untuk_setiap(self):
        tipe = tipe_token("untuk setiap")
        assert tipe == [TokenType.UNTUK_SETIAP]

    def test_atau_tanpa_jika(self):
        """'atau' sendiri harus tetap ATAU (logical OR)."""
        tipe = tipe_token("atau")
        assert tipe == [TokenType.ATAU]

    def test_untuk_tanpa_setiap(self):
        """'untuk' sendiri harus tetap UNTUK (for range)."""
        tipe = tipe_token("untuk i dari 1 sampai 10")
        assert tipe[0] == TokenType.UNTUK

    def test_atau_jika_dalam_konteks(self):
        kode = "jika x == 1:\n    tampilkan x\natau jika x == 2:\n    tampilkan x"
        tokens = tokenisasi(kode)
        tipe = [t.tipe for t in tokens if t.tipe not in (
            TokenType.BARIS_BARU, TokenType.INDENT, TokenType.DEDENT, TokenType.EOF
        )]
        assert TokenType.ATAU_JIKA in tipe


# ============================================================
# Test: Komentar
# ============================================================

class TestKomentar:
    def test_komentar_satu_baris(self):
        """Komentar # harus diabaikan."""
        tipe = tipe_token("buat x = 5 # ini komentar")
        assert tipe == [
            TokenType.BUAT, TokenType.IDENTIFIER,
            TokenType.SAMA_DENGAN, TokenType.ANGKA,
        ]

    def test_baris_hanya_komentar(self):
        tipe = tipe_token("# komentar saja")
        assert tipe == []

    def test_komentar_multibaris(self):
        kode = '"""\nIni komentar\npanjang\n"""\nbuat x = 1'
        tipe = tipe_token(kode)
        assert TokenType.BUAT in tipe

    def test_komentar_multibaris_tidak_ditutup(self):
        with pytest.raises(KesalahanSintaks):
            tokenisasi('"""\nini tidak ditutup')


# ============================================================
# Test: Identifier
# ============================================================

class TestIdentifier:
    def test_identifier_sederhana(self):
        assert tipe_token("nama") == [TokenType.IDENTIFIER]
        assert nilai_token("nama") == ["nama"]

    def test_identifier_dengan_underscore(self):
        assert nilai_token("nama_depan") == ["nama_depan"]

    def test_identifier_dengan_angka(self):
        assert nilai_token("x1") == ["x1"]

    def test_identifier_mulai_underscore(self):
        assert nilai_token("_privat") == ["_privat"]


# ============================================================
# Test: Pelacakan Posisi
# ============================================================

class TestPosisi:
    def test_posisi_baris(self):
        tokens = tokenisasi("buat x = 5\nbuat y = 10")
        buat_tokens = [t for t in tokens if t.tipe == TokenType.BUAT]
        assert buat_tokens[0].baris == 1
        assert buat_tokens[1].baris == 2

    def test_posisi_kolom(self):
        tokens = tokenisasi("buat x = 5")
        # "buat" dimulai di kolom 1
        assert tokens[0].kolom == 1
        # "x" dimulai di kolom 6 (setelah "buat ")
        x_token = [t for t in tokens if t.tipe == TokenType.IDENTIFIER][0]
        assert x_token.kolom == 6


# ============================================================
# Test: Indentasi
# ============================================================

class TestIndentasi:
    def test_indent_sederhana(self):
        kode = "jika benar:\n    tampilkan 1"
        tokens = tokenisasi(kode)
        tipe = [t.tipe for t in tokens]
        assert TokenType.INDENT in tipe

    def test_dedent_di_akhir(self):
        kode = "jika benar:\n    tampilkan 1\ntampilkan 2"
        tokens = tokenisasi(kode)
        tipe = [t.tipe for t in tokens]
        assert TokenType.DEDENT in tipe

    def test_nested_indent(self):
        kode = "jika benar:\n    jika salah:\n        tampilkan 1"
        tokens = tokenisasi(kode)
        tipe = [t.tipe for t in tokens]
        indent_count = tipe.count(TokenType.INDENT)
        assert indent_count == 2

    def test_auto_dedent_eof(self):
        """Semua indent harus di-DEDENT sebelum EOF."""
        kode = "jika benar:\n    tampilkan 1"
        tokens = tokenisasi(kode)
        tipe = [t.tipe for t in tokens]
        assert tipe.count(TokenType.INDENT) == tipe.count(TokenType.DEDENT)

    def test_baris_kosong_diabaikan(self):
        kode = "buat x = 1\n\nbuat y = 2"
        tokens = tokenisasi(kode)
        buat_count = sum(1 for t in tokens if t.tipe == TokenType.BUAT)
        assert buat_count == 2


# ============================================================
# Test: Error / Karakter Tidak Dikenal
# ============================================================

class TestError:
    def test_karakter_tidak_dikenal(self):
        with pytest.raises(KesalahanSintaks):
            tokenisasi("buat x = @")

    def test_error_punya_baris(self):
        try:
            tokenisasi("buat x = @")
        except KesalahanSintaks as e:
            assert e.baris == 1
            assert e.kolom is not None


# ============================================================
# Test: Program Lengkap
# ============================================================

class TestProgramLengkap:
    def test_halo_dunia(self):
        kode = 'tampilkan "Halo Dunia!"'
        tipe = tipe_token(kode)
        assert tipe == [TokenType.TAMPILKAN, TokenType.TEKS]

    def test_deklarasi_variabel(self):
        kode = 'buat nama = "Budi"\nbuat umur = 20'
        tipe = tipe_token(kode)
        assert tipe == [
            TokenType.BUAT, TokenType.IDENTIFIER, TokenType.SAMA_DENGAN, TokenType.TEKS,
            TokenType.BUAT, TokenType.IDENTIFIER, TokenType.SAMA_DENGAN, TokenType.ANGKA,
        ]

    def test_kondisi_lengkap(self):
        kode = (
            "jika nilai >= 90:\n"
            '    tampilkan "A"\n'
            "atau jika nilai >= 80:\n"
            '    tampilkan "B"\n'
            "selainnya:\n"
            '    tampilkan "C"'
        )
        tokens = tokenisasi(kode)
        tipe = [t.tipe for t in tokens if t.tipe not in (
            TokenType.BARIS_BARU, TokenType.INDENT, TokenType.DEDENT, TokenType.EOF
        )]
        assert TokenType.JIKA in tipe
        assert TokenType.ATAU_JIKA in tipe
        assert TokenType.SELAINNYA in tipe

    def test_perulangan_untuk(self):
        kode = "untuk i dari 1 sampai 10:\n    tampilkan i"
        tipe = tipe_token(kode)
        assert TokenType.UNTUK in tipe
        assert TokenType.DARI in tipe
        assert TokenType.SAMPAI in tipe

    def test_perulangan_untuk_setiap(self):
        kode = "untuk setiap buah dalam daftar:\n    tampilkan buah"
        tipe = tipe_token(kode)
        assert TokenType.UNTUK_SETIAP in tipe
        assert TokenType.DALAM in tipe

    def test_fungsi_definisi(self):
        kode = "fungsi sapa(nama):\n    tampilkan nama"
        tipe = tipe_token(kode)
        assert TokenType.FUNGSI in tipe
        assert TokenType.KURUNG_BUKA in tipe
        assert TokenType.KURUNG_TUTUP in tipe

    def test_ekspresi_aritmatika(self):
        kode = "buat hasil = (5 + 3) * 2 - 1"
        tipe = tipe_token(kode)
        assert TokenType.KURUNG_BUKA in tipe
        assert TokenType.TAMBAH in tipe
        assert TokenType.KALI in tipe
        assert TokenType.KURANG in tipe


# ============================================================
# Test: Frasa Natural (multi-kata)
# ============================================================

class TestFrasaNatural:
    def test_tidak_sama_dengan_satu_token(self):
        """'tidak sama dengan' (tercantum di PRD) harus satu token, tanpa sisa 'dengan'."""
        assert tipe_token("x tidak sama dengan y") == [
            TokenType.IDENTIFIER, TokenType.TIDAK_SAMA_OP, TokenType.IDENTIFIER,
        ]

    def test_lebih_besar_kecil_dari(self):
        assert tipe_token("x lebih besar dari y")[1] == TokenType.LEBIH_DARI
        assert tipe_token("x lebih kecil dari y")[1] == TokenType.KURANG_DARI

    def test_varian_daripada(self):
        assert tipe_token("x lebih besar daripada y")[1] == TokenType.LEBIH_DARI
        assert tipe_token("x kurang daripada y")[1] == TokenType.KURANG_DARI

    def test_atau_sama_dengan(self):
        """Cara membaca ≥ dan ≤ di sekolah: 'lebih dari atau sama dengan'."""
        assert tipe_token("x lebih dari atau sama dengan y") == [
            TokenType.IDENTIFIER, TokenType.TIDAK_KURANG_DARI, TokenType.IDENTIFIER,
        ]
        assert tipe_token("x kurang dari atau sama dengan y")[1] == TokenType.TIDAK_LEBIH_DARI
        assert tipe_token("x lebih besar sama dengan y")[1] == TokenType.TIDAK_KURANG_DARI

    def test_paling_sedikit_banyak(self):
        assert tipe_token("x paling sedikit 17")[1] == TokenType.TIDAK_KURANG_DARI
        assert tipe_token("x paling banyak 17")[1] == TokenType.TIDAK_LEBIH_DARI

    def test_habis_dibagi(self):
        assert tipe_token("x habis dibagi 3")[1] == TokenType.HABIS_DIBAGI
        assert tipe_token("x tidak habis dibagi 3")[1] == TokenType.TIDAK_HABIS_DIBAGI

    def test_tidak_ada_di_dalam(self):
        assert tipe_token("x tidak ada di dalam d") == [
            TokenType.IDENTIFIER, TokenType.TIDAK_ADA, TokenType.DALAM, TokenType.IDENTIFIER,
        ]

    def test_nilai_dan_kolom_frasa(self):
        tokens = tokenisasi("x paling sedikit 1")
        assert tokens[1].nilai == "paling sedikit"
        assert tokens[1].kolom == 3

    def test_awal_frasa_tetap_boleh_jadi_nama(self):
        """Tanpa sisa frasanya, 'lebih', 'sama', 'paling', dst. adalah nama biasa."""
        for kata in ("lebih", "kurang", "sama", "paling", "habis", "di", "sisa"):
            assert tipe_token(f"buat {kata} = 1")[1] == TokenType.IDENTIFIER

    def test_frasa_tidak_menyeberang_baris(self):
        assert TokenType.SAMA_DENGAN_OP not in tipe_token("buat x = sama\ndengan = 1")


class TestKataKunciNatural:
    def test_adalah_maka_lakukan(self):
        assert tipe_token("adalah maka lakukan") == [
            TokenType.ADALAH, TokenType.MAKA, TokenType.LAKUKAN,
        ]

    def test_kalau_sinonim_jika(self):
        assert tipe_token("kalau")[0] == TokenType.JIKA
        assert tipe_token("atau kalau") == [TokenType.ATAU_JIKA]

    def test_tidak_sinonim_bukan(self):
        tokens = tokenisasi("tidak hujan")
        assert tokens[0].tipe == TokenType.BUKAN
        assert tokens[0].nilai == "tidak"

    def test_bentuk_baku_aritmatika(self):
        assert tipe_token("a dikurangi b dikalikan c dipangkatkan 2") == [
            TokenType.IDENTIFIER, TokenType.DIKURANG, TokenType.IDENTIFIER,
            TokenType.DIKALI, TokenType.IDENTIFIER, TokenType.PANGKAT_KK, TokenType.ANGKA,
        ]


class TestBarisDalamKurung:
    def test_daftar_multi_baris(self):
        """Baris baru dan indentasi di dalam kurung diabaikan."""
        tipe = [t.tipe for t in tokenisasi("buat d = [\n    1,\n    2,\n]")]
        assert TokenType.INDENT not in tipe
        assert TokenType.BARIS_BARU not in tipe

    def test_baris_baru_setelah_kurung_ditutup(self):
        tipe = [t.tipe for t in tokenisasi("buat d = [\n    1\n]\ntampilkan d")]
        assert tipe.count(TokenType.BARIS_BARU) == 1
