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


# ============================================================
# Gaya Natural
# ============================================================

class TestGayaNaturalDeklarasi:
    def test_buat_adalah(self):
        node = ast("buat umur adalah 17").pernyataan[0]
        assert isinstance(node, NodeDeklarasiVariabel)
        assert node.nama == "umur"
        assert node.ekspresi.nilai == 17

    def test_tetap_adalah(self):
        assert isinstance(ast("tetap PI adalah 3.14").pernyataan[0], NodeKonstanta)

    def test_tipe_eksplisit_adalah(self):
        assert ast("bilangan umur adalah 17").pernyataan[0].tipe_eksplisit == "bilangan"

    def test_adalah_di_awal_kalimat_mengisi_nilai(self):
        node = ast("umur adalah 18").pernyataan[0]
        assert isinstance(node, NodePenugasan)
        assert node.target.nama == "umur"

    def test_adalah_pada_atribut_dan_elemen(self):
        assert isinstance(ast("diri.nama adalah nama").pernyataan[0].target, NodeAksesAtribut)
        assert isinstance(ast("d[0] adalah 5").pernyataan[0].target, NodeAksesDaftar)

    def test_adalah_dalam_kondisi_membandingkan(self):
        node = ast('jika nama adalah "Budi":\n    tampilkan nama').pernyataan[0]
        assert node.kondisi.operator == "=="

    def test_buat_tanpa_pengisian_error(self):
        with pytest.raises(KesalahanSintaks, match="'adalah'"):
            ast("buat umur 17")


class TestGayaNaturalKalimat:
    def test_ubah_menjadi(self):
        node = ast("ubah umur menjadi 18").pernyataan[0]
        assert isinstance(node, NodePenugasan)
        assert node.target.nama == "umur"
        assert node.ekspresi.nilai == 18

    def test_ubah_jadi(self):
        assert isinstance(ast("ubah umur jadi 18").pernyataan[0], NodePenugasan)

    def test_tambahkan_ke(self):
        node = ast("tambahkan 10 ke skor").pernyataan[0]
        assert isinstance(node, NodeTambahkan)
        assert node.nilai.nilai == 10
        assert node.target.nama == "skor"

    def test_tambahkan_ke_dalam(self):
        assert ast('tambahkan "apel" ke dalam keranjang').pernyataan[0].target.nama == "keranjang"

    def test_tambahkan_ekspresi_dalam_kurung(self):
        node = ast("tambahkan (harga dikali 2) ke total").pernyataan[0]
        assert isinstance(node, NodeTambahkan)
        assert node.nilai.operator == "*"

    def test_kurangi_dengan_dan_dari(self):
        for kode in ("kurangi nyawa dengan 1", "kurangi 1 dari nyawa"):
            node = ast(kode).pernyataan[0]
            assert isinstance(node, NodePenugasanGabungan)
            assert node.operator == "-="
            assert node.target.nama == "nyawa"
            assert node.ekspresi.nilai == 1

    def test_kalikan_dan_bagi(self):
        assert ast("kalikan harga dengan 2").pernyataan[0].operator == "*="
        assert ast("bagi total dengan 4").pernyataan[0].operator == "/="

    def test_kata_kerja_tetap_bisa_jadi_nama(self):
        """Kompatibilitas: 'tambahkan(5)', 'bagi(10, 2)', 'ubah = 3' bukan kalimat natural."""
        assert isinstance(ast("tambahkan(5)").pernyataan[0], NodePanggilFungsi)
        assert isinstance(ast("bagi(10, 2)").pernyataan[0], NodePanggilFungsi)
        assert isinstance(ast("ubah = 3").pernyataan[0], NodePenugasan)

    def test_kalimat_tidak_lengkap_error(self):
        with pytest.raises(KesalahanSintaks, match="ubah umur menjadi 18"):
            ast("ubah umur ke 18")

    def test_target_harus_bisa_diisi(self):
        with pytest.raises(KesalahanSintaks, match="tidak bisa diberi nilai"):
            ast("ubah 5 menjadi 3")


class TestGayaNaturalKondisi:
    def test_maka_satu_baris(self):
        node = ast("jika hujan maka tampilkan 1").pernyataan[0]
        assert isinstance(node, NodeJika)
        assert isinstance(node.blok_jika[0], NodeTampilkan)

    def test_koma_maka_blok(self):
        node = ast("jika hujan, maka:\n    tampilkan 1\n    tampilkan 2").pernyataan[0]
        assert len(node.blok_jika) == 2

    def test_koma_saja_satu_baris(self):
        assert len(ast("jika hujan, tampilkan 1").pernyataan[0].blok_jika) == 1

    def test_jika_tidak_sebagai_selainnya(self):
        tree = ast("jika hujan:\n    tampilkan 1\njika tidak:\n    tampilkan 2")
        assert len(tree.pernyataan) == 1
        assert tree.pernyataan[0].blok_selainnya is not None

    def test_kalau_tidak_koma(self):
        tree = ast("kalau hujan, tampilkan 1\nkalau tidak, tampilkan 2")
        assert len(tree.pernyataan) == 1
        assert len(tree.pernyataan[0].blok_selainnya) == 1

    def test_jika_tidak_dengan_kondisi_adalah_jika_baru(self):
        """'jika tidak lapar:' adalah kondisi baru (bukan lapar), bukan selainnya."""
        tree = ast("jika kenyang:\n    tampilkan 1\njika tidak lapar:\n    tampilkan 2")
        assert len(tree.pernyataan) == 2
        assert tree.pernyataan[1].kondisi.operator == "bukan"

    def test_atau_kalau(self):
        node = ast("kalau x > 1:\n    tampilkan 1\natau kalau x > 0:\n    tampilkan 2").pernyataan[0]
        assert len(node.cabang_atau_jika) == 1

    def test_bukan_sebagai_tidak_sama(self):
        assert ast('jika hari bukan "Minggu": tampilkan 1').pernyataan[0].kondisi.operator == "!="

    def test_habis_dibagi(self):
        node = ast("x habis dibagi 3").pernyataan[0]
        assert node.operator == "=="
        assert node.kiri.operator == "%"
        assert node.kanan.nilai == 0

    def test_tidak_ada_dalam(self):
        assert ast("x tidak ada dalam d").pernyataan[0].operator == "tidak ada dalam"

    def test_selainnya_di_pilih(self):
        node = ast("pilih x:\n    ketika 1: tampilkan 1\n    selainnya: tampilkan 0").pernyataan[0]
        assert node.bawaan is not None

    def test_tanpa_pembuka_blok_error_ramah(self):
        with pytest.raises(KesalahanSintaks) as info:
            ast("jika x > 5\n    tampilkan x")
        assert "':'" in info.value.pesan
        assert "TITIK_DUA" not in info.value.pesan


class TestGayaNaturalPerulangan:
    def test_ulangi_kali(self):
        node = ast("ulangi 3 kali:\n    tampilkan 1").pernyataan[0]
        assert isinstance(node, NodeUlangiKali)
        assert node.jumlah.nilai == 3

    def test_ulangi_kali_satu_baris(self):
        assert isinstance(ast("ulangi 3 kali, tampilkan 1").pernyataan[0], NodeUlangiKali)

    def test_ulangi_tanpa_kali_error(self):
        with pytest.raises(KesalahanSintaks, match="kali"):
            ast("ulangi 3:\n    tampilkan 1")

    def test_ulangi_sampai(self):
        node = ast("ulangi:\n    x += 1\nsampai x adalah 3").pernyataan[0]
        assert isinstance(node, NodeUlangi)
        assert node.kondisi.operator == "bukan"  # sampai X = ulangi selama bukan X

    def test_selama_lakukan(self):
        assert isinstance(ast("selama x kurang dari 3, lakukan:\n    x += 1").pernyataan[0], NodeSelama)

    def test_tunggu_detik(self):
        node = ast("tunggu 2 menit").pernyataan[0]
        assert isinstance(node, NodeTunggu)
        assert node.lama.nilai == 2
        assert node.faktor == 60

    def test_tunggu_sebagai_panggilan_fungsi(self):
        assert isinstance(ast("tunggu(1)").pernyataan[0], NodePanggilFungsi)

    def test_waktu_sekarang_sebagai_nilai(self):
        node = ast("jika detik sekarang habis dibagi 2: tampilkan 1").pernyataan[0]
        assert isinstance(node.kondisi.kiri.kiri, NodeWaktuSekarang)
        assert node.kondisi.kiri.kiri.bagian == "detik"

    def test_untuk_setiap_di_dalam(self):
        assert isinstance(ast("untuk setiap b di dalam buah, tampilkan b").pernyataan[0], NodeUntukSetiap)


class TestKetegasanParser:
    def test_dua_perintah_satu_baris_error(self):
        """Dulu 'tampilkan 1 tampilkan 2' diam-diam dibaca sebagai dua perintah."""
        with pytest.raises(KesalahanSintaks, match="berakhir di sini"):
            ast("tampilkan 1 tampilkan 2")

    def test_penugasan_ke_pemanggilan_fungsi_error(self):
        with pytest.raises(KesalahanSintaks, match="tidak bisa diberi nilai"):
            ast("f(x) = 5")

    def test_kata_kunci_sebagai_nama_atribut(self):
        assert ast("acak.pilih(d)").pernyataan[0].fungsi.atribut == "pilih"

    def test_pangkat_asosiatif_kanan(self):
        node = ast("2 pangkat 3 pangkat 2").pernyataan[0]
        assert node.kiri.nilai == 2
        assert node.kanan.operator == "**"

    def test_kamus_multi_baris(self):
        node = ast('buat m = {\n    "nama": "Budi",\n    "umur": 20,\n}').pernyataan[0]
        assert len(node.ekspresi.pasangan) == 2

    def test_indentasi_tak_terduga_error(self):
        with pytest.raises(KesalahanSintaks, match="menjorok"):
            ast("tampilkan 1\n    tampilkan 2")


# ============================================================
# Tahap 1: kosakata baru dan pesan kesalahan
# ============================================================

class TestKosakataBaru:
    def test_angka_acak(self):
        node = ast("buat dadu adalah angka acak dari 1 sampai 6").pernyataan[0]
        assert isinstance(node.ekspresi, NodeAngkaAcak)
        assert node.ekspresi.maksimum.nilai == 6

    def test_angka_acak_tanpa_dari_error(self):
        with pytest.raises(KesalahanSintaks, match="angka acak dari 1 sampai 6"):
            ast("buat dadu adalah angka acak 6")

    def test_tanya(self):
        teks = ast('buat nama adalah tanya "Siapa? "').pernyataan[0].ekspresi
        angka = ast('buat umur adalah tanya angka "Umur? "').pernyataan[0].ekspresi
        assert isinstance(teks, NodeTanya) and teks.jenis == "teks"
        assert isinstance(angka, NodeTanya) and angka.jenis == "angka"

    def test_tanya_dengan_kurung_adalah_panggilan_fungsi(self):
        assert isinstance(ast('tanya("Siapa? ")').pernyataan[0], NodePanggilFungsi)

    def test_cetak_tidak_pindah_baris(self):
        assert ast('cetak "a"').pernyataan[0].baris_baru is False
        assert ast('tampilkan "a"').pernyataan[0].baris_baru is True

    def test_ketika_beberapa_nilai(self):
        node = ast('pilih x:\n    ketika "a" atau "b", "c": tampilkan 1').pernyataan[0]
        nilai, blok = node.kasus[0]
        assert [n.nilai for n in nilai] == ["a", "b", "c"]

    def test_waktu_tanggal(self):
        node = ast("tampilkan hari ini, tanggal hari ini, bulan ini, tahun ini").pernyataan[0]
        assert [e.bagian for e in node.ekspresi_list] == ["hari", "tanggal", "bulan", "tahun"]

    def test_impor_kata_kunci_butuh_nama_lain(self):
        with pytest.raises(KesalahanSintaks, match="sebagai pilih_acak"):
            ast("dari acak impor pilih")
        assert isinstance(ast("dari acak impor pilih sebagai pilih_acak").pernyataan[0], NodeDariImpor)


class TestPesanKesalahanParser:
    def test_kata_kunci_sebagai_nama(self):
        with pytest.raises(KesalahanSintaks, match="'lempar' adalah kata kunci"):
            ast("buat lempar adalah 5")

    def test_petunjuk_huruf_kecil(self):
        with pytest.raises(KesalahanSintaks, match="Tulis 'tampilkan', bukan 'Tampilkan'"):
            ast('Tampilkan "halo"')

    def test_petunjuk_salah_ketik(self):
        with pytest.raises(KesalahanSintaks, match="maksud Anda 'jika'"):
            ast("jka x > 5: tampilkan x")

    @pytest.mark.parametrize("kode", ["jika x > 5:", "buat d = [1,", "fungsi f(n):\n    kembalikan n dikali", "ulangi 3 kali:"])
    def test_belum_selesai_di_akhir_masukan(self, kode):
        with pytest.raises(KesalahanSintaks) as info:
            ast(kode)
        assert info.value.belum_selesai is True

    def test_kesalahan_biasa_bukan_belum_selesai(self):
        with pytest.raises(KesalahanSintaks) as info:
            ast("tampilkan 1 tampilkan 2")
        assert info.value.belum_selesai is False
