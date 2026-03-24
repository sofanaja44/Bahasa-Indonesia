"""
test_parser.py — Unit test untuk Parser bahasa Indonesia.
"""

import pytest
from src.lexer import tokenisasi
from src.parser import parse
from src.ast_nodes import *
from src.errors import KesalahanSintaks


def ast(kode: str):
    tokens = tokenisasi(kode)
    return parse(tokens, kode)


# ============================================================
# Literal
# ============================================================

class TestLiteral:
    def test_angka(self):
        tree = ast("42")
        assert isinstance(tree.pernyataan[0], NodeAngka)
        assert tree.pernyataan[0].nilai == 42

    def test_desimal(self):
        tree = ast("3.14")
        assert isinstance(tree.pernyataan[0], NodeAngka)
        assert tree.pernyataan[0].nilai == 3.14

    def test_teks(self):
        tree = ast('"Halo"')
        assert isinstance(tree.pernyataan[0], NodeTeks)
        assert tree.pernyataan[0].nilai == "Halo"

    def test_benar(self):
        tree = ast("benar")
        assert isinstance(tree.pernyataan[0], NodeLogika)
        assert tree.pernyataan[0].nilai is True

    def test_salah(self):
        tree = ast("salah")
        assert isinstance(tree.pernyataan[0], NodeLogika)
        assert tree.pernyataan[0].nilai is False

    def test_kosong(self):
        tree = ast("kosong")
        assert isinstance(tree.pernyataan[0], NodeKosong)

    def test_format_teks(self):
        tree = ast('format"Halo {nama}"')
        assert isinstance(tree.pernyataan[0], NodeTeksFormat)
        assert tree.pernyataan[0].template == "Halo {nama}"

    def test_fstring_tetap_didukung(self):
        """f\"...\" tetap didukung untuk backward compatibility."""
        tree = ast('f"Halo {nama}"')
        assert isinstance(tree.pernyataan[0], NodeTeksFormat)
        assert tree.pernyataan[0].template == "Halo {nama}"


# ============================================================
# Ekspresi Aritmatika
# ============================================================

class TestAritmatika:
    def test_tambah(self):
        tree = ast("5 + 3")
        node = tree.pernyataan[0]
        assert isinstance(node, NodeOperasiBiner)
        assert node.operator == "+"
        assert node.kiri.nilai == 5
        assert node.kanan.nilai == 3

    def test_preseden_kali_sebelum_tambah(self):
        tree = ast("2 + 3 * 4")
        node = tree.pernyataan[0]
        assert isinstance(node, NodeOperasiBiner)
        assert node.operator == "+"
        assert node.kiri.nilai == 2
        assert isinstance(node.kanan, NodeOperasiBiner)
        assert node.kanan.operator == "*"

    def test_kurung_mengubah_preseden(self):
        tree = ast("(2 + 3) * 4")
        node = tree.pernyataan[0]
        assert isinstance(node, NodeOperasiBiner)
        assert node.operator == "*"
        assert isinstance(node.kiri, NodeOperasiBiner)
        assert node.kiri.operator == "+"

    def test_pangkat(self):
        tree = ast("5 ** 2")
        node = tree.pernyataan[0]
        assert isinstance(node, NodeOperasiBiner)
        assert node.operator == "**"

    def test_unari_negatif(self):
        tree = ast("-5")
        node = tree.pernyataan[0]
        assert isinstance(node, NodeOperasiUnari)
        assert node.operator == "-"
        assert node.operand.nilai == 5

    def test_modulo(self):
        tree = ast("10 % 3")
        node = tree.pernyataan[0]
        assert node.operator == "%"


# ============================================================
# Perbandingan & Logika
# ============================================================

class TestPerbandingan:
    def test_sama(self):
        tree = ast("x == 5")
        node = tree.pernyataan[0]
        assert isinstance(node, NodeOperasiBiner)
        assert node.operator == "=="

    def test_tidak_sama(self):
        tree = ast("x != 5")
        assert tree.pernyataan[0].operator == "!="

    def test_lebih_besar(self):
        tree = ast("x > 5")
        assert tree.pernyataan[0].operator == ">"

    def test_dan(self):
        tree = ast("x > 0 dan y > 0")
        node = tree.pernyataan[0]
        assert node.operator == "dan"

    def test_atau(self):
        tree = ast("x > 0 atau y > 0")
        node = tree.pernyataan[0]
        assert node.operator == "atau"

    def test_bukan(self):
        tree = ast("bukan benar")
        node = tree.pernyataan[0]
        assert isinstance(node, NodeOperasiUnari)
        assert node.operator == "bukan"

    def test_ada_dalam(self):
        tree = ast('"apel" ada dalam buah')
        node = tree.pernyataan[0]
        assert node.operator == "ada dalam"


# ============================================================
# Operator Teks Indonesia (dinormalisasi ke simbol)
# ============================================================

class TestOperatorTeksIndonesia:
    def test_sama_dengan(self):
        """'sama dengan' dinormalisasi ke '=='"""
        tree = ast("buat x = 5\njika x sama dengan 5:\n    tampilkan x")
        node = tree.pernyataan[1]
        assert node.kondisi.operator == "=="

    def test_tidak_sama(self):
        """'tidak sama' dinormalisasi ke '!='"""
        tree = ast("buat x = 5\njika x tidak sama 3:\n    tampilkan x")
        node = tree.pernyataan[1]
        assert node.kondisi.operator == "!="

    def test_lebih_dari(self):
        """'lebih dari' dinormalisasi ke '>'"""
        tree = ast("buat x = 10\njika x lebih dari 5:\n    tampilkan x")
        node = tree.pernyataan[1]
        assert node.kondisi.operator == ">"

    def test_kurang_dari(self):
        """'kurang dari' dinormalisasi ke '<'"""
        tree = ast("buat x = 3\njika x kurang dari 5:\n    tampilkan x")
        node = tree.pernyataan[1]
        assert node.kondisi.operator == "<"

    def test_tidak_kurang_dari(self):
        """'tidak kurang dari' dinormalisasi ke '>='"""
        tree = ast("buat x = 5\njika x tidak kurang dari 5:\n    tampilkan x")
        node = tree.pernyataan[1]
        assert node.kondisi.operator == ">="

    def test_tidak_lebih_dari(self):
        """'tidak lebih dari' dinormalisasi ke '<='"""
        tree = ast("buat x = 5\njika x tidak lebih dari 10:\n    tampilkan x")
        node = tree.pernyataan[1]
        assert node.kondisi.operator == "<="

    def test_sisa_bagi(self):
        """'sisa bagi' dinormalisasi ke '%'"""
        tree = ast("10 sisa bagi 3")
        node = tree.pernyataan[0]
        assert isinstance(node, NodeOperasiBiner)
        assert node.operator == "%"

    def test_pangkat_kata_kunci(self):
        """'pangkat' dinormalisasi ke '**'"""
        tree = ast("2 pangkat 10")
        node = tree.pernyataan[0]
        assert isinstance(node, NodeOperasiBiner)
        assert node.operator == "**"

    def test_aritmatika_dasar_teks(self):
        """'ditambah', 'dikurang', 'dikali', 'dibagi' dinormalisasi ke simbol dasar aritmatika"""
        tree = ast("1 ditambah 2 dikurang 3 dikali 4 dibagi 5")
        
        # Tes parse_penjumlahan memanggil parse_perkalian => +, - ada di parse_penjumlahan dll.
        # memastikan operator dinormalisasi dengan benar
        # Pohon sintaks bisa kompleks, tapi secara individual:
        
        assert ast("1 ditambah 1").pernyataan[0].operator == "+"
        assert ast("2 dikurang 1").pernyataan[0].operator == "-"
        assert ast("3 dikali 4").pernyataan[0].operator == "*"
        assert ast("10 dibagi 2").pernyataan[0].operator == "/"


# ============================================================
# Deklarasi
# ============================================================

class TestDeklarasi:
    def test_buat(self):
        tree = ast("buat x = 5")
        node = tree.pernyataan[0]
        assert isinstance(node, NodeDeklarasiVariabel)
        assert node.nama == "x"
        assert node.ekspresi.nilai == 5
        assert node.tipe_eksplisit is None

    def test_buat_teks(self):
        tree = ast('buat nama = "Budi"')
        node = tree.pernyataan[0]
        assert node.nama == "nama"
        assert node.ekspresi.nilai == "Budi"

    def test_tetap(self):
        tree = ast("tetap PI = 3.14")
        node = tree.pernyataan[0]
        assert isinstance(node, NodeKonstanta)
        assert node.nama == "PI"

    def test_deklarasi_bilangan(self):
        tree = ast("bilangan umur = 17")
        node = tree.pernyataan[0]
        assert isinstance(node, NodeDeklarasiVariabel)
        assert node.tipe_eksplisit == "bilangan"

    def test_deklarasi_teks(self):
        tree = ast('teks nama = "Siti"')
        node = tree.pernyataan[0]
        assert node.tipe_eksplisit == "teks"

    def test_penugasan(self):
        tree = ast("x = 10")
        node = tree.pernyataan[0]
        assert isinstance(node, NodePenugasan)
        assert node.target.nama == "x"

    def test_penugasan_gabungan(self):
        tree = ast("x += 5")
        node = tree.pernyataan[0]
        assert isinstance(node, NodePenugasanGabungan)
        assert node.operator == "+="


# ============================================================
# Tampilkan
# ============================================================

class TestTampilkan:
    def test_tampilkan_teks(self):
        tree = ast('tampilkan "Halo"')
        node = tree.pernyataan[0]
        assert isinstance(node, NodeTampilkan)
        assert len(node.ekspresi_list) == 1
        assert node.ekspresi_list[0].nilai == "Halo"

    def test_tampilkan_banyak(self):
        tree = ast("tampilkan x, y, z")
        node = tree.pernyataan[0]
        assert len(node.ekspresi_list) == 3

    def test_cetak_sinonim(self):
        tree = ast('cetak "Halo"')
        node = tree.pernyataan[0]
        assert isinstance(node, NodeTampilkan)


# ============================================================
# Kondisi
# ============================================================

class TestKondisi:
    def test_jika_sederhana(self):
        tree = ast("jika x > 5:\n    tampilkan x")
        node = tree.pernyataan[0]
        assert isinstance(node, NodeJika)
        assert node.kondisi.operator == ">"
        assert len(node.blok_jika) == 1

    def test_jika_selainnya(self):
        tree = ast("jika x > 5:\n    tampilkan x\nselainnya:\n    tampilkan 0")
        node = tree.pernyataan[0]
        assert node.blok_selainnya is not None
        assert len(node.blok_selainnya) == 1

    def test_jika_atau_jika_selainnya(self):
        kode = "jika x > 90:\n    tampilkan 1\natau jika x > 80:\n    tampilkan 2\nselainnya:\n    tampilkan 3"
        tree = ast(kode)
        node = tree.pernyataan[0]
        assert len(node.cabang_atau_jika) == 1
        assert node.blok_selainnya is not None

    def test_jika_satu_baris(self):
        tree = ast("jika x > 5: tampilkan x")
        node = tree.pernyataan[0]
        assert isinstance(node, NodeJika)
        assert len(node.blok_jika) == 1


# ============================================================
# Perulangan
# ============================================================

class TestPerulangan:
    def test_selama(self):
        tree = ast("selama x > 0:\n    x = x - 1")
        node = tree.pernyataan[0]
        assert isinstance(node, NodeSelama)
        assert node.kondisi.operator == ">"

    def test_untuk(self):
        tree = ast("untuk i dari 1 sampai 10:\n    tampilkan i")
        node = tree.pernyataan[0]
        assert isinstance(node, NodeUntuk)
        assert node.variabel == "i"
        assert node.dari_expr.nilai == 1
        assert node.sampai_expr.nilai == 10

    def test_untuk_dengan_langkah(self):
        tree = ast("untuk i dari 0 sampai 100 langkah 5:\n    tampilkan i")
        node = tree.pernyataan[0]
        assert node.langkah_expr is not None
        assert node.langkah_expr.nilai == 5

    def test_untuk_setiap(self):
        tree = ast("untuk setiap buah dalam daftar:\n    tampilkan buah")
        node = tree.pernyataan[0]
        assert isinstance(node, NodeUntukSetiap)
        assert node.variabel == "buah"

    def test_berhenti(self):
        tree = ast("berhenti")
        assert isinstance(tree.pernyataan[0], NodeBerhenti)

    def test_lewati(self):
        tree = ast("lewati")
        assert isinstance(tree.pernyataan[0], NodeLewati)


# ============================================================
# Fungsi
# ============================================================

class TestFungsi:
    def test_fungsi_sederhana(self):
        tree = ast("fungsi sapa(nama):\n    tampilkan nama")
        node = tree.pernyataan[0]
        assert isinstance(node, NodeFungsi)
        assert node.nama == "sapa"
        assert len(node.parameter) == 1
        assert node.parameter[0][0] == "nama"

    def test_fungsi_banyak_param(self):
        tree = ast("fungsi tambah(a, b):\n    kembalikan a + b")
        node = tree.pernyataan[0]
        assert len(node.parameter) == 2

    def test_fungsi_default_param(self):
        kode = 'fungsi sapa(nama, kota = "Jakarta"):\n    tampilkan nama'
        tree = ast(kode)
        node = tree.pernyataan[0]
        assert node.parameter[1][1] is not None  # default value exists

    def test_kembalikan(self):
        tree = ast("kembalikan 42")
        node = tree.pernyataan[0]
        assert isinstance(node, NodeKembalikan)
        assert node.ekspresi.nilai == 42

    def test_panggil_fungsi(self):
        tree = ast("sapa(nama)")
        node = tree.pernyataan[0]
        assert isinstance(node, NodePanggilFungsi)
        assert node.fungsi.nama == "sapa"


# ============================================================
# Koleksi
# ============================================================

class TestKoleksi:
    def test_daftar(self):
        tree = ast('[1, 2, 3]')
        node = tree.pernyataan[0]
        assert isinstance(node, NodeDaftar)
        assert len(node.elemen) == 3

    def test_daftar_kosong(self):
        tree = ast('[]')
        node = tree.pernyataan[0]
        assert isinstance(node, NodeDaftar)
        assert len(node.elemen) == 0

    def test_kamus(self):
        tree = ast('{"nama": "Budi", "umur": 20}')
        node = tree.pernyataan[0]
        assert isinstance(node, NodeKamus)
        assert len(node.pasangan) == 2

    def test_akses_daftar(self):
        tree = ast("buah[0]")
        node = tree.pernyataan[0]
        assert isinstance(node, NodeAksesDaftar)

    def test_irisan_daftar(self):
        tree = ast("buah[1:3]")
        node = tree.pernyataan[0]
        assert isinstance(node, NodeIrisanDaftar)

    def test_akses_atribut(self):
        tree = ast("diri.nama")
        node = tree.pernyataan[0]
        assert isinstance(node, NodeAksesAtribut)
        assert node.atribut == "nama"

    def test_panggil_metode(self):
        tree = ast('buah.tambahkan("apel")')
        node = tree.pernyataan[0]
        assert isinstance(node, NodePanggilFungsi)
        assert isinstance(node.fungsi, NodeAksesAtribut)


# ============================================================
# Kelas
# ============================================================

class TestKelas:
    def test_kelas_sederhana(self):
        kode = "kelas Hewan:\n    buat nama = \"\""
        tree = ast(kode)
        node = tree.pernyataan[0]
        assert isinstance(node, NodeKelas)
        assert node.nama == "Hewan"
        assert node.induk is None

    def test_kelas_mewarisi(self):
        kode = "kelas Anjing mewarisi Hewan:\n    buat jenis = \"\""
        tree = ast(kode)
        node = tree.pernyataan[0]
        assert node.induk == "Hewan"


# ============================================================
# Modul
# ============================================================

class TestModul:
    def test_impor(self):
        tree = ast("impor matematika")
        node = tree.pernyataan[0]
        assert isinstance(node, NodeImpor)
        assert node.modul == "matematika"

    def test_impor_sebagai(self):
        tree = ast("impor matematika.akar sebagai akar")
        node = tree.pernyataan[0]
        assert node.modul == "matematika.akar"
        assert node.alias == "akar"

    def test_dari_impor(self):
        tree = ast("dari waktu impor sekarang")
        node = tree.pernyataan[0]
        assert isinstance(node, NodeDariImpor)
        assert node.modul == "waktu"
        assert node.nama == "sekarang"


# ============================================================
# Error Handling
# ============================================================

class TestErrorHandling:
    def test_coba_tangkap(self):
        kode = 'coba:\n    tampilkan 1\ntangkap sebagai e:\n    tampilkan e'
        tree = ast(kode)
        node = tree.pernyataan[0]
        assert isinstance(node, NodeCoba)
        assert len(node.penangkap) == 1

    def test_lempar(self):
        tree = ast('lempar Error("Salah!")')
        node = tree.pernyataan[0]
        assert isinstance(node, NodeLempar)


# ============================================================
# Program Lengkap
# ============================================================

class TestProgramLengkap:
    def test_kalkulator(self):
        kode = (
            'buat a = 10\n'
            'buat b = 5\n'
            'tampilkan a + b'
        )
        tree = ast(kode)
        assert len(tree.pernyataan) == 3

    def test_fungsi_dan_panggil(self):
        kode = (
            "fungsi tambah(a, b):\n"
            "    kembalikan a + b\n"
            "buat hasil = tambah(3, 4)\n"
            "tampilkan hasil"
        )
        tree = ast(kode)
        assert len(tree.pernyataan) == 3
        assert isinstance(tree.pernyataan[0], NodeFungsi)
