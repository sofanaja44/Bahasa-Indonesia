"""
test_interpreter.py — Unit test untuk Interpreter bahasa Indonesia.
"""

import pytest
from io import StringIO
from contextlib import redirect_stdout
from pathlib import Path

from src.interpreter import jalankan_kode, Interpreter
from src.lexer import tokenisasi
from src.parser import parse
from src.errors import (
    KesalahanNama, KesalahanTipe, KesalahanBagiNol,
    KesalahanIndeks, KesalahanNilai, KesalahanIndonesia, KesalahanBerkas, KesalahanTumpukan,
    KesalahanSintaks,
)
from src.bk_types import BKDaftar, BKKamus


def tangkap_output(kode: str) -> str:
    """Jalankan kode dan tangkap stdout."""
    buf = StringIO()
    with redirect_stdout(buf):
        jalankan_kode(kode)
    return buf.getvalue().strip()


def eval_kode(kode: str):
    """Jalankan kode dan kembalikan hasil terakhir."""
    return jalankan_kode(kode)


# ============================================================
# Literal & Ekspresi
# ============================================================

class TestLiteral:
    def test_angka(self):
        assert eval_kode("42") == 42

    def test_desimal(self):
        assert eval_kode("3.14") == 3.14

    def test_teks(self):
        assert eval_kode('"Halo"') == "Halo"

    def test_benar(self):
        assert eval_kode("benar") is True

    def test_salah(self):
        assert eval_kode("salah") is False

    def test_kosong(self):
        assert eval_kode("kosong") is None


class TestAritmatika:
    def test_penjumlahan(self):
        assert eval_kode("5 + 3") == 8

    def test_pengurangan(self):
        assert eval_kode("10 - 4") == 6

    def test_perkalian(self):
        assert eval_kode("3 * 7") == 21

    def test_pembagian(self):
        assert eval_kode("15 / 3") == 5.0

    def test_modulo(self):
        assert eval_kode("10 % 3") == 1

    def test_pangkat(self):
        assert eval_kode("2 ** 10") == 1024

    def test_preseden(self):
        assert eval_kode("2 + 3 * 4") == 14

    def test_kurung(self):
        assert eval_kode("(2 + 3) * 4") == 20

    def test_negatif(self):
        assert eval_kode("-5") == -5

    def test_gabungan_string(self):
        assert eval_kode('"Halo" + " " + "Dunia"') == "Halo Dunia"

    def test_kali_string(self):
        assert eval_kode('"ha" * 3') == "hahaha"


class TestPerbandingan:
    def test_sama(self):
        assert eval_kode("5 == 5") is True

    def test_tidak_sama(self):
        assert eval_kode("5 != 3") is True

    def test_lebih_besar(self):
        assert eval_kode("10 > 5") is True

    def test_lebih_kecil(self):
        assert eval_kode("3 < 7") is True

    def test_lebih_besar_sama(self):
        assert eval_kode("5 >= 5") is True

    def test_lebih_kecil_sama(self):
        assert eval_kode("3 <= 5") is True


class TestLogika:
    def test_dan(self):
        assert eval_kode("benar dan benar") is True
        assert eval_kode("benar dan salah") is False

    def test_atau(self):
        assert eval_kode("salah atau benar") is True
        assert eval_kode("salah atau salah") is False

    def test_bukan(self):
        assert eval_kode("bukan salah") is True
        assert eval_kode("bukan benar") is False


# ============================================================
# Deklarasi & Penugasan
# ============================================================

class TestDeklarasi:
    def test_buat_variabel(self):
        output = tangkap_output("buat x = 42\ntampilkan x")
        assert output == "42"

    def test_deklarasi_tipe(self):
        output = tangkap_output('bilangan umur = 17\ntampilkan umur')
        assert output == "17"

    def test_teks_tipe(self):
        output = tangkap_output('teks nama = "Budi"\ntampilkan nama')
        assert output == "Budi"

    def test_konstanta(self):
        output = tangkap_output("tetap PI = 3.14\ntampilkan PI")
        assert output == "3.14"

    def test_konstanta_tidak_bisa_diubah(self):
        with pytest.raises(KesalahanNama, match="konstanta"):
            jalankan_kode("tetap X = 5\nX = 10")

    def test_penugasan(self):
        output = tangkap_output("buat x = 5\nx = 10\ntampilkan x")
        assert output == "10"

    def test_penugasan_gabungan(self):
        output = tangkap_output("buat x = 10\nx += 5\ntampilkan x")
        assert output == "15"

    def test_penugasan_kurang(self):
        output = tangkap_output("buat x = 10\nx -= 3\ntampilkan x")
        assert output == "7"

    def test_variabel_tidak_ada(self):
        with pytest.raises(KesalahanNama, match="belum dideklarasikan"):
            jalankan_kode("tampilkan y")


# ============================================================
# Tampilkan
# ============================================================

class TestTampilkan:
    def test_tampilkan_angka(self):
        assert tangkap_output("tampilkan 42") == "42"

    def test_tampilkan_teks(self):
        assert tangkap_output('tampilkan "Halo Dunia"') == "Halo Dunia"

    def test_tampilkan_banyak(self):
        assert tangkap_output("tampilkan 1, 2, 3") == "1 2 3"

    def test_tampilkan_benar(self):
        assert tangkap_output("tampilkan benar") == "benar"

    def test_tampilkan_kosong(self):
        assert tangkap_output("tampilkan kosong") == "kosong"

    def test_cetak_sinonim(self):
        assert tangkap_output('cetak "OK"') == "OK"  # cetak captured by redirect_stdout

    def test_tulis_sinonim(self):
        assert tangkap_output('tulis "Halo"') == "Halo"


# ============================================================
# Kondisi
# ============================================================

class TestKondisi:
    def test_jika_benar(self):
        kode = 'buat x = 10\njika x > 5:\n    tampilkan "besar"'
        assert tangkap_output(kode) == "besar"

    def test_jika_salah(self):
        kode = 'buat x = 3\njika x > 5:\n    tampilkan "besar"'
        assert tangkap_output(kode) == ""

    def test_jika_selainnya(self):
        kode = 'buat x = 3\njika x > 5:\n    tampilkan "besar"\nselainnya:\n    tampilkan "kecil"'
        assert tangkap_output(kode) == "kecil"

    def test_jika_atau_jika(self):
        kode = (
            'buat x = 85\n'
            'jika x > 90:\n'
            '    tampilkan "A"\n'
            'atau jika x > 80:\n'
            '    tampilkan "B"\n'
            'selainnya:\n'
            '    tampilkan "C"'
        )
        assert tangkap_output(kode) == "B"


# ============================================================
# Perulangan
# ============================================================

class TestPerulangan:
    def test_selama(self):
        kode = 'buat x = 0\nbuat hasil = 0\nselama x < 5:\n    hasil += x\n    x += 1\ntampilkan hasil'
        assert tangkap_output(kode) == "10"

    def test_untuk(self):
        kode = 'buat total = 0\nuntuk i dari 1 sampai 5:\n    total += i\ntampilkan total'
        assert tangkap_output(kode) == "15"

    def test_untuk_langkah(self):
        kode = 'buat total = 0\nuntuk i dari 0 sampai 10 langkah 2:\n    total += i\ntampilkan total'
        assert tangkap_output(kode) == "30"

    def test_untuk_setiap(self):
        kode = 'buat buah = ["apel", "jeruk", "mangga"]\nuntuk setiap b dalam buah:\n    tampilkan b'
        output = tangkap_output(kode)
        assert "apel" in output
        assert "jeruk" in output
        assert "mangga" in output

    def test_berhenti(self):
        kode = (
            'buat x = 0\n'
            'selama benar:\n'
            '    jika x >= 3:\n'
            '        berhenti\n'
            '    x += 1\n'
            'tampilkan x'
        )
        assert tangkap_output(kode) == "3"

    def test_lewati(self):
        kode = (
            'buat genap = 0\n'
            'untuk i dari 1 sampai 10:\n'
            '    jika i % 2 != 0:\n'
            '        lewati\n'
            '    genap += 1\n'
            'tampilkan genap'
        )
        assert tangkap_output(kode) == "5"


# ============================================================
# Fungsi
# ============================================================

class TestFungsi:
    def test_fungsi_sederhana(self):
        kode = 'fungsi sapa(nama):\n    tampilkan "Halo " + nama\nsapa("Budi")'
        assert tangkap_output(kode) == "Halo Budi"

    def test_kembalikan(self):
        kode = 'fungsi tambah(a, b):\n    kembalikan a + b\nbuat h = tambah(3, 4)\ntampilkan h'
        assert tangkap_output(kode) == "7"

    def test_default_param(self):
        kode = (
            'fungsi sapa(nama, sapaan = "Halo"):\n'
            '    tampilkan sapaan + " " + nama\n'
            'sapa("Budi")\n'
            'sapa("Siti", "Hai")'
        )
        output = tangkap_output(kode)
        assert "Halo Budi" in output
        assert "Hai Siti" in output

    def test_rekursi(self):
        kode = (
            'fungsi faktorial(n):\n'
            '    jika n <= 1:\n'
            '        kembalikan 1\n'
            '    kembalikan n * faktorial(n - 1)\n'
            'tampilkan faktorial(5)'
        )
        assert tangkap_output(kode) == "120"

    def test_closure(self):
        kode = (
            'fungsi pembuat_penghitung():\n'
            '    buat hitung = 0\n'
            '    fungsi tambah():\n'
            '        kembalikan 1\n'
            '    kembalikan tambah()\n'
            'tampilkan pembuat_penghitung()'
        )
        assert tangkap_output(kode) == "1"


# ============================================================
# Koleksi
# ============================================================

class TestKoleksi:
    def test_daftar(self):
        kode = 'buat d = [1, 2, 3]\ntampilkan d'
        output = tangkap_output(kode)
        assert "1" in output

    def test_daftar_akses(self):
        kode = 'buat d = [10, 20, 30]\ntampilkan d[1]'
        assert tangkap_output(kode) == "20"

    def test_daftar_tambahkan(self):
        kode = 'buat d = [1, 2]\nd.tambahkan(3)\ntampilkan d[2]'
        assert tangkap_output(kode) == "3"

    def test_daftar_panjang(self):
        kode = 'buat d = [1, 2, 3, 4, 5]\ntampilkan panjang(d)'
        assert tangkap_output(kode) == "5"

    def test_kamus(self):
        kode = 'buat k = {"nama": "Budi", "umur": 20}\ntampilkan k["nama"]'
        assert tangkap_output(kode) == "Budi"

    def test_ada_dalam_daftar(self):
        kode = 'buat k = [1, 2, 3]\ntampilkan 2 ada dalam k'
        assert tangkap_output(kode) == "benar"

    def test_ada_dalam_teks(self):
        kode = 'tampilkan "hello" ada dalam "hello world"'
        assert tangkap_output(kode) == "benar"

    def test_irisan(self):
        kode = 'buat d = [1, 2, 3, 4, 5]\nbuat h = d[1:3]\ntampilkan panjang(h)'
        assert tangkap_output(kode) == "2"


# ============================================================
# OOP
# ============================================================

class TestOOP:
    def test_kelas_sederhana(self):
        kode = (
            'kelas Hewan:\n'
            '    fungsi inisialisasi(diri, nama):\n'
            '        diri.nama = nama\n'
            '    fungsi suara(diri):\n'
            '        kembalikan diri.nama + " bersuara"\n'
            'buat h = Hewan("Kucing")\n'
            'tampilkan h.suara()'
        )
        assert tangkap_output(kode) == "Kucing bersuara"

    def test_kelas_dengan_atribut(self):
        kode = (
            'kelas Orang:\n'
            '    fungsi inisialisasi(diri, nama, umur):\n'
            '        diri.nama = nama\n'
            '        diri.umur = umur\n'
            'buat o = Orang("Budi", 25)\n'
            'tampilkan o.nama'
        )
        assert tangkap_output(kode) == "Budi"

    def test_pewarisan(self):
        kode = (
            'kelas Hewan:\n'
            '    fungsi inisialisasi(diri, nama):\n'
            '        diri.nama = nama\n'
            '    fungsi info(diri):\n'
            '        kembalikan diri.nama\n'
            'kelas Anjing mewarisi Hewan:\n'
            '    fungsi gonggong(diri):\n'
            '        kembalikan diri.nama + ": Guk!"\n'
            'buat a = Anjing("Rex")\n'
            'tampilkan a.gonggong()'
        )
        assert tangkap_output(kode) == "Rex: Guk!"


# ============================================================
# Error handling
# ============================================================

class TestErrorHandling:
    def test_bagi_nol(self):
        with pytest.raises(KesalahanBagiNol):
            jalankan_kode("buat x = 10 / 0")

    def test_tipe_error(self):
        with pytest.raises(KesalahanTipe):
            jalankan_kode('"abc" - 5')

    def test_indeks_error(self):
        with pytest.raises(KesalahanIndeks):
            jalankan_kode("buat d = [1, 2]\ntampilkan d[10]")

    def test_coba_tangkap(self):
        kode = (
            'coba:\n'
            '    buat x = 10 / 0\n'
            'tangkap sebagai e:\n'
            '    tampilkan "Tertangkap"'
        )
        assert tangkap_output(kode) == "Tertangkap"

    def test_tangkap_kesalahan_menangkap_semua(self):
        kode = 'coba:\n    tampilkan tidak_ada\ntangkap Kesalahan:\n    tampilkan "tertangkap"'
        assert tangkap_output(kode) == "tertangkap"

    def test_tangkap_kesalahan_huruf_kecil_menyimpan_pesan(self):
        kode = 'coba:\n    buat x = 1 / 0\ntangkap kesalahan:\n    tampilkan "Ups:", kesalahan'
        assert tangkap_output(kode) == "Ups: Tidak bisa membagi dengan nol"

    def test_contoh_prd_nama_python(self):
        kode = (
            "coba:\n    buat hasil = 10 / 0\n"
            "tangkap ZeroDivisionError sebagai e:\n    tampilkan \"Error: Tidak bisa dibagi nol!\"\n"
            "tangkap sebagai e:\n    tampilkan \"Error tidak diketahui: \" + e.pesan\n"
            "akhirnya:\n    tampilkan \"Selesai dieksekusi\""
        )
        assert tangkap_output(kode) == "Error: Tidak bisa dibagi nol!\nSelesai dieksekusi"

    def test_pesan_dan_jenis_kesalahan(self):
        kode = (
            'coba:\n    lempar "Baterai habis"\n'
            'tangkap sebagai e:\n    tampilkan e.pesan, "|", e.jenis, "|", e.huruf_besar()'
        )
        assert tangkap_output(kode) == "Baterai habis | KesalahanNilai | BATERAI HABIS"

    def test_jenis_tidak_cocok_diteruskan(self):
        kode = "coba:\n    buat x = 1 / 0\ntangkap KesalahanNama:\n    tampilkan 1"
        with pytest.raises(KesalahanBagiNol):
            jalankan_kode(kode)

    def test_penangkap_pertama_yang_cocok_dipakai(self):
        kode = (
            "coba:\n    tampilkan [1][5]\n"
            "tangkap KesalahanBagiNol:\n    tampilkan \"bagi\"\n"
            "tangkap kesalahanindeks:\n    tampilkan \"indeks\"\n"
            "tangkap:\n    tampilkan \"lain\""
        )
        assert tangkap_output(kode) == "indeks"

    @pytest.mark.parametrize("kode, potongan", [
        ("coba:\n    tampilkan 1\ntangkap e:\n    tampilkan e", "tulis: tangkap sebagai e"),
        ("coba:\n    tampilkan 1\ntangkap KesalahanBagiNoll:\n    tampilkan 2", "Maksud Anda 'KesalahanBagiNol'?"),
    ])
    def test_jenis_kesalahan_tidak_dikenal(self, kode, potongan):
        with pytest.raises(KesalahanSintaks, match=potongan):
            jalankan_kode(kode)


# ============================================================
# Built-in Functions
# ============================================================

class TestBuiltinFungsi:
    def test_panjang_teks(self):
        assert tangkap_output('tampilkan panjang("Halo")') == "4"

    def test_jenis_angka(self):
        assert tangkap_output("tampilkan jenis(42)") == "bilangan"

    def test_jenis_teks(self):
        assert tangkap_output('tampilkan jenis("abc")') == "teks"

    def test_jenis_logika(self):
        assert tangkap_output("tampilkan jenis(benar)") == "logika"

    def test_mutlak(self):
        assert tangkap_output("tampilkan mutlak(-5)") == "5"

    def test_ubah_angka(self):
        assert tangkap_output('tampilkan ubah_angka("42")') == "42"

    def test_ubah_teks(self):
        assert tangkap_output('tampilkan ubah_teks(123)') == "123"


# ============================================================
# Format Teks (format"..." dan f"...")
# ============================================================

class TestFormatTeks:
    def test_format_teks_sederhana(self):
        kode = 'buat nama = "Budi"\ntampilkan format"Halo {nama}"'
        assert tangkap_output(kode) == "Halo Budi"

    def test_format_teks_ekspresi(self):
        kode = 'buat x = 5\ntampilkan format"Hasil: {x * 2}"'
        assert tangkap_output(kode) == "Hasil: 10"

    def test_fstring_backward_compatible(self):
        """f\"...\" tetap didukung untuk backward compatibility."""
        kode = 'buat nama = "Budi"\ntampilkan f"Halo {nama}"'
        assert tangkap_output(kode) == "Halo Budi"


# ============================================================
# Operator Teks Indonesia
# ============================================================

class TestOperatorTeksIndonesia:
    def test_sama_dengan(self):
        kode = 'buat x = 5\njika x sama dengan 5:\n    tampilkan "benar"'
        assert tangkap_output(kode) == "benar"

    def test_tidak_sama(self):
        kode = 'buat x = 5\njika x tidak sama 3:\n    tampilkan "benar"'
        assert tangkap_output(kode) == "benar"

    def test_lebih_dari(self):
        kode = 'buat x = 10\njika x lebih dari 5:\n    tampilkan "benar"'
        assert tangkap_output(kode) == "benar"

    def test_kurang_dari(self):
        kode = 'buat x = 3\njika x kurang dari 5:\n    tampilkan "benar"'
        assert tangkap_output(kode) == "benar"

    def test_tidak_kurang_dari(self):
        kode = 'buat x = 5\njika x tidak kurang dari 5:\n    tampilkan "benar"'
        assert tangkap_output(kode) == "benar"

    def test_tidak_lebih_dari(self):
        kode = 'buat x = 5\njika x tidak lebih dari 10:\n    tampilkan "benar"'
        assert tangkap_output(kode) == "benar"

    def test_sisa_bagi(self):
        assert eval_kode("10 sisa bagi 3") == 1

    def test_pangkat_kata_kunci(self):
        assert eval_kode("2 pangkat 10") == 1024

    def test_operator_teks_dan_simbol_sama_hasil(self):
        """Operator teks dan simbol harus menghasilkan hasil yang sama."""
        assert eval_kode("10 sisa bagi 3") == eval_kode("10 % 3")
        assert eval_kode("2 pangkat 10") == eval_kode("2 ** 10")
        assert eval_kode("10 ditambah 5") == eval_kode("10 + 5")
        assert eval_kode("10 dikurang 5") == eval_kode("10 - 5")
        assert eval_kode("10 dikali 5") == eval_kode("10 * 5")
        assert eval_kode("10 dibagi 5") == eval_kode("10 / 5")


# ============================================================
# Program Lengkap
# ============================================================

class TestProgramLengkap:
    def test_halo_dunia(self):
        assert tangkap_output('tampilkan "Halo Dunia!"') == "Halo Dunia!"

    def test_kalkulator(self):
        kode = (
            'fungsi kali(a, b):\n'
            '    kembalikan a * b\n'
            'tampilkan kali(6, 7)'
        )
        assert tangkap_output(kode) == "42"

    def test_fibonacci(self):
        kode = (
            'fungsi fib(n):\n'
            '    jika n <= 1:\n'
            '        kembalikan n\n'
            '    kembalikan fib(n - 1) + fib(n - 2)\n'
            'tampilkan fib(10)'
        )
        assert tangkap_output(kode) == "55"

    def test_fizzbuzz(self):
        kode = (
            'buat hasil = ""\n'
            'untuk i dari 1 sampai 15:\n'
            '    jika i % 15 == 0:\n'
            '        hasil = hasil + "FizzBuzz "\n'
            '    atau jika i % 3 == 0:\n'
            '        hasil = hasil + "Fizz "\n'
            '    atau jika i % 5 == 0:\n'
            '        hasil = hasil + "Buzz "\n'
            '    selainnya:\n'
            '        hasil = hasil + ubah_teks(i) + " "\n'
            'tampilkan hasil'
        )
        output = tangkap_output(kode)
        assert "FizzBuzz" in output
        assert "Fizz" in output
        assert "Buzz" in output


# ============================================================
# Gaya Natural (Bercerita)
# ============================================================

class TestGayaNaturalNilai:
    def test_buat_adalah(self):
        assert tangkap_output('buat nama adalah "Budi"\ntampilkan nama') == "Budi"

    def test_adalah_mengisi_ulang(self):
        assert tangkap_output("buat x adalah 1\nx adalah x ditambah 1\ntampilkan x") == "2"

    def test_ubah_menjadi(self):
        kode = "buat umur adalah 17\nubah umur menjadi umur ditambah 1\ntampilkan umur"
        assert tangkap_output(kode) == "18"

    def test_adalah_membandingkan_dalam_kondisi(self):
        kode = 'buat nama adalah "Budi"\njika nama adalah "Budi", maka tampilkan "halo Budi"'
        assert tangkap_output(kode) == "halo Budi"

    def test_adalah_dalam_teks_format_tidak_mengisi(self):
        kode = 'buat x adalah 1\ntampilkan format"{x adalah 5}"\ntampilkan x'
        assert tangkap_output(kode) == "salah\n1"

    def test_tambahkan_ke_angka(self):
        assert tangkap_output("buat skor adalah 10\ntambahkan 5 ke skor\ntampilkan skor") == "15"

    def test_tambahkan_ke_daftar(self):
        kode = 'buat keranjang adalah ["apel"]\ntambahkan "mangga" ke keranjang\ntampilkan keranjang'
        assert tangkap_output(kode) == "[apel, mangga]"

    def test_tambahkan_ke_teks(self):
        kode = 'buat kalimat adalah "Halo"\ntambahkan "!" ke kalimat\ntampilkan kalimat'
        assert tangkap_output(kode) == "Halo!"

    def test_tambahkan_ke_kamus_error(self):
        with pytest.raises(KesalahanTipe, match="kamus"):
            jalankan_kode("buat k adalah {}\ntambahkan 1 ke k")

    def test_kurangi_kalikan_bagi(self):
        kode = (
            "buat uang adalah 100\n"
            "kurangi uang dengan 30\n"
            "kurangi 10 dari uang\n"
            "kalikan uang dengan 3\n"
            "bagi uang dengan 2\n"
            "tampilkan uang"
        )
        assert tangkap_output(kode) == "90"  # desimal bulat tampil tanpa .0

    def test_kalimat_pada_atribut_objek(self):
        kode = (
            "kelas Pemain:\n"
            "    fungsi inisialisasi():\n"
            "        diri.skor adalah 0\n"
            "buat p adalah Pemain()\n"
            "tambahkan 7 ke p.skor\n"
            "tampilkan p.skor"
        )
        assert tangkap_output(kode) == "7"

    def test_kalimat_dalam_blok_satu_baris(self):
        assert tangkap_output("buat x adalah 0\nulangi 4 kali, tambahkan 2 ke x\ntampilkan x") == "8"


class TestGayaNaturalKondisi:
    def test_jika_maka_jika_tidak(self):
        kode = (
            "buat umur adalah 15\n"
            'jika umur paling sedikit 17, maka tampilkan "dewasa"\n'
            'jika tidak, tampilkan "anak-anak"'
        )
        assert tangkap_output(kode) == "anak-anak"

    def test_kalau_atau_kalau(self):
        kode = (
            "buat n adalah 75\n"
            'kalau n paling sedikit 90: tampilkan "A"\n'
            'atau kalau n paling sedikit 70: tampilkan "B"\n'
            'kalau tidak: tampilkan "C"'
        )
        assert tangkap_output(kode) == "B"

    def test_tidak_sebagai_bukan(self):
        kode = 'buat hujan adalah salah\njika tidak hujan maka tampilkan "cerah"'
        assert tangkap_output(kode) == "cerah"

    def test_perbandingan_natural(self):
        assert eval_kode("5 tidak sama dengan 3") is True
        assert eval_kode("5 lebih besar dari 3") is True
        assert eval_kode("5 lebih kecil dari 3") is False
        assert eval_kode("5 lebih besar daripada 3") is True
        assert eval_kode("5 lebih dari atau sama dengan 5") is True
        assert eval_kode("5 kurang dari atau sama dengan 4") is False
        assert eval_kode("5 paling sedikit 5") is True
        assert eval_kode("5 paling banyak 4") is False
        assert eval_kode("5 adalah 5") is True
        assert eval_kode("5 bukan 5") is False

    def test_habis_dibagi(self):
        assert eval_kode("12 habis dibagi 4") is True
        assert eval_kode("12 habis dibagi 5") is False
        assert eval_kode("12 tidak habis dibagi 5") is True

    def test_tidak_ada_dalam(self):
        kode = 'buat buah adalah ["apel"]\ntampilkan "durian" tidak ada dalam buah'
        assert tangkap_output(kode) == "benar"

    def test_ada_di_dalam(self):
        assert tangkap_output('tampilkan "a" ada di dalam ["a", "b"]') == "benar"

    def test_fizzbuzz_gaya_natural(self):
        kode = (
            "untuk angka dari 1 sampai 15, lakukan:\n"
            '    jika angka habis dibagi 15, maka tampilkan "FizzBuzz"\n'
            '    atau jika angka habis dibagi 3, maka tampilkan "Fizz"\n'
            '    atau jika angka habis dibagi 5, maka tampilkan "Buzz"\n'
            "    jika tidak, tampilkan angka"
        )
        baris = tangkap_output(kode).split("\n")
        assert baris[:5] == ["1", "2", "Fizz", "4", "Buzz"]
        assert baris[14] == "FizzBuzz"


class TestGayaNaturalPerulangan:
    def test_ulangi_kali(self):
        assert tangkap_output('ulangi 3 kali:\n    tampilkan "hore"') == "hore\nhore\nhore"

    def test_ulangi_kali_dengan_berhenti(self):
        kode = (
            "buat n adalah 0\n"
            "ulangi 10 kali:\n"
            "    tambahkan 1 ke n\n"
            "    jika n adalah 4, maka berhenti\n"
            "tampilkan n"
        )
        assert tangkap_output(kode) == "4"

    def test_ulangi_kali_hasil_bagi_bulat(self):
        assert tangkap_output("ulangi 4 dibagi 2 kali, tampilkan 1") == "1\n1"

    def test_ulangi_kali_bukan_bilangan_error(self):
        with pytest.raises(KesalahanTipe, match="bilangan bulat"):
            jalankan_kode('ulangi "tiga" kali: tampilkan 1')

    def test_ulangi_sampai(self):
        kode = (
            "buat hitung adalah 3\n"
            "ulangi:\n"
            "    tampilkan hitung\n"
            "    kurangi hitung dengan 1\n"
            "sampai hitung adalah 0"
        )
        assert tangkap_output(kode) == "3\n2\n1"

    def test_selama_lakukan(self):
        kode = "buat x adalah 0\nselama x kurang dari 3, lakukan:\n    tambahkan 1 ke x\ntampilkan x"
        assert tangkap_output(kode) == "3"

    def test_untuk_setiap_kamus(self):
        kode = 'buat harga adalah {"apel": 1, "jeruk": 2}\nuntuk setiap buah dalam harga, tampilkan buah'
        assert tangkap_output(kode) == "apel\njeruk"

    def test_untuk_setiap_bukan_koleksi_error(self):
        with pytest.raises(KesalahanTipe, match="untuk setiap"):
            jalankan_kode("untuk setiap x dalam 5: tampilkan x")


# ============================================================
# Perbaikan bug
# ============================================================

class TestPerbaikanBug:
    def test_penugasan_gabungan_pada_atribut(self):
        """Dulu 'a.skor += 10' dihitung tetapi tidak pernah disimpan."""
        kode = (
            "kelas A:\n"
            "    fungsi inisialisasi():\n"
            "        diri.skor = 1\n"
            "buat a = A()\n"
            "a.skor += 10\n"
            "tampilkan a.skor"
        )
        assert tangkap_output(kode) == "11"

    def test_penugasan_gabungan_pada_elemen_daftar(self):
        assert tangkap_output("buat d = [1, 2]\nd[0] += 10\ntampilkan d") == "[11, 2]"

    def test_penugasan_indeks_di_luar_batas(self):
        with pytest.raises(KesalahanIndeks):
            jalankan_kode("buat d = [1]\nd[10] = 1")

    def test_induk_memanggil_metode_kelas_induk(self):
        kode = (
            "kelas Hewan:\n"
            "    fungsi inisialisasi(nama, suara):\n"
            "        diri.nama = nama\n"
            "        diri.suara = suara\n"
            "kelas Anjing mewarisi Hewan:\n"
            "    fungsi inisialisasi(nama):\n"
            '        induk.inisialisasi(nama, "Guk!")\n'
            'buat a = Anjing("Rex")\n'
            "tampilkan a.nama, a.suara"
        )
        assert tangkap_output(kode) == "Rex Guk!"

    def test_super_tetap_didukung(self):
        kode = (
            "kelas A:\n"
            "    fungsi info():\n"
            '        kembalikan "A"\n'
            "kelas B mewarisi A:\n"
            "    fungsi info():\n"
            '        kembalikan super.info() + "B"\n'
            "tampilkan B().info()"
        )
        assert tangkap_output(kode) == "AB"

    def test_lempar_kesalahan(self):
        kode = 'coba:\n    lempar Kesalahan("Pembagi nol!")\ntangkap sebagai e:\n    tampilkan e'
        assert tangkap_output(kode) == "Pembagi nol!"

    def test_lempar_error_seperti_prd(self):
        kode = 'coba:\n    lempar Error("Pembagi nol!")\ntangkap sebagai e:\n    tampilkan e'
        assert tangkap_output(kode) == "Pembagi nol!"

    def test_fungsi_anonim_dengan_kembalikan(self):
        assert tangkap_output("buat kuadrat = fungsi(x): kembalikan x * x\ntampilkan kuadrat(4)") == "16"

    def test_teks_format_dengan_spasi(self):
        assert tangkap_output('buat x = 3\ntampilkan format"{ x }"') == "3"

    def test_tampilkan_tanpa_nilai_mencetak_baris_kosong(self):
        buf = StringIO()
        with redirect_stdout(buf):
            jalankan_kode('tampilkan "a"\ntampilkan\ntampilkan "b"')
        assert buf.getvalue() == "a\n\nb\n"


# ============================================================
# Fungsi waktu
# ============================================================

@pytest.fixture
def jam_palsu(monkeypatch):
    """Jam palsu mulai 23:59:57 yang maju hanya ketika program 'tunggu'."""
    import datetime as dt

    sekarang = [dt.datetime(2026, 1, 1, 23, 59, 57)]

    class WaktuPalsu(dt.datetime):
        @classmethod
        def now(cls, tz=None):
            return sekarang[0]

    def tidur(detik):
        sekarang[0] += dt.timedelta(seconds=detik)

    monkeypatch.setattr("src.builtins.datetime", WaktuPalsu)
    monkeypatch.setattr("time.sleep", tidur)
    return sekarang


class TestWaktu:
    def test_jam_menit_detik_sekarang(self, jam_palsu):
        assert tangkap_output("tampilkan jam sekarang, menit sekarang, detik sekarang") == "23 59 57"

    def test_waktu_sekarang_dua_digit(self, jam_palsu):
        assert tangkap_output("tunggu 3 detik\ntampilkan waktu sekarang") == "00:00:00"

    def test_waktu_dalam_kondisi(self, jam_palsu):
        assert tangkap_output('jika jam sekarang paling sedikit 18, maka tampilkan "malam"') == "malam"

    def test_tunggu_dengan_satuan(self, monkeypatch):
        dicatat = []
        monkeypatch.setattr("time.sleep", dicatat.append)
        jalankan_kode("tunggu 2 detik\ntunggu 1 menit\ntunggu 500 milidetik\ntunggu 3\nbuat jeda adalah 4\ntunggu jeda detik")
        assert dicatat == [2, 60, pytest.approx(0.5), 3, 4]

    def test_tunggu_sebagai_fungsi_tetap_bisa(self, monkeypatch):
        dicatat = []
        monkeypatch.setattr("time.sleep", dicatat.append)
        jalankan_kode("tunggu(1)\ntunggu(0.5)")
        assert dicatat == [1, 0.5]

    def test_tunggu_negatif_error(self):
        with pytest.raises(KesalahanNilai, match="negatif"):
            jalankan_kode("tunggu -1 detik")

    def test_tunggu_bukan_angka_error(self):
        with pytest.raises(KesalahanNilai, match="angka"):
            jalankan_kode('tunggu "sebentar"')

    def test_jam_digital_berganti_hari(self, jam_palsu):
        """Contoh jam digital: sapaan malam, 23:59:59 ke 00:00:00, dan alarm lima detik kemudian."""
        output = tangkap_output((FOLDER_CONTOH / "jam_digital.id").read_text(encoding="utf-8"))
        assert "Selamat malam, Budi!" in output
        assert "[ 23:59:59 ] tok" in output
        assert "[ 00:00:00 ] tik" in output
        assert "[ 00:00:02 ] tik\n   KRING!" in output
        assert "[ 00:00:06 ] tik" in output
        assert "Baterai jam habis" in output


# ============================================================
# Semua program contoh harus berjalan tanpa error
# ============================================================

FOLDER_CONTOH = Path(__file__).resolve().parent.parent / "contoh"


# Jawaban untuk program contoh yang interaktif
JAWABAN_CONTOH = {"tebak_angka.id": ["50", "25", "42"]}


def _main_contoh(berkas, monkeypatch, jawaban):
    """Jalankan program contoh dengan jawaban palsu dan angka acak yang selalu 42."""
    sisa = list(jawaban)

    def masukan_palsu(pertanyaan=""):
        print(pertanyaan, end="")
        if not sisa:
            raise EOFError
        return sisa.pop(0)

    monkeypatch.setattr("time.sleep", lambda detik: None)  # jam_digital.id tidak perlu benar-benar menunggu
    monkeypatch.setattr("random.randint", lambda a, b: 42 if a <= 42 <= b else a)
    monkeypatch.setattr("builtins.input", masukan_palsu)
    buf = StringIO()
    with redirect_stdout(buf):
        jalankan_kode(berkas.read_text(encoding="utf-8"))
    return buf.getvalue()


@pytest.mark.parametrize("berkas", sorted(FOLDER_CONTOH.glob("*.id")), ids=lambda p: p.name)
def test_program_contoh_berjalan(berkas, monkeypatch):
    assert _main_contoh(berkas, monkeypatch, JAWABAN_CONTOH.get(berkas.name, [])).strip()


class TestTebakAngka:
    BERKAS = FOLDER_CONTOH / "tebak_angka.id"

    def test_menang(self, monkeypatch):
        keluaran = _main_contoh(self.BERKAS, monkeypatch, ["50", "25", "42"])
        assert "Terlalu besar! Sisa kesempatan: 6" in keluaran
        assert "Terlalu kecil! Sisa kesempatan: 5" in keluaran
        assert "Hebat! Angkanya memang 42" in keluaran

    def test_kalah(self, monkeypatch):
        keluaran = _main_contoh(self.BERKAS, monkeypatch, ["1"] * 7)
        assert keluaran.count("Terlalu kecil!") == 7
        assert "Kesempatan habis. Angka rahasianya adalah 42" in keluaran

    def test_jawaban_bukan_angka_tidak_mengurangi_kesempatan(self, monkeypatch):
        keluaran = _main_contoh(self.BERKAS, monkeypatch, ["empat puluh dua", "42"])
        assert "Tolong jawab dengan angka." in keluaran
        assert "Hebat!" in keluaran


# ============================================================
# Pustaka standar
# ============================================================

class TestPustakaStandar:
    def test_impor_sebagai(self):
        assert tangkap_output("impor matematika sebagai m\ntampilkan m.faktorial(4)") == "24"

    def test_bulatkan_seperti_di_sekolah(self):
        kode = "impor matematika\ntampilkan matematika.bulatkan(2.675, 2), matematika.bulatkan(-2.5), matematika.bulatkan(1234, -2)"
        assert tangkap_output(kode) == "2.68 -3 1200"

    @pytest.mark.parametrize("kode, pesan", [
        ("matematika.akar(-1)", "negatif"),
        ("matematika.faktorial(-1)", "0 atau lebih"),
        ("matematika.tangen(90)", "tidak terdefinisi"),
        ("matematika.logaritma(0)", "lebih dari 0"),
        ("matematika.fpb(4)", "dua bilangan"),
    ])
    def test_matematika_kesalahan(self, kode, pesan):
        with pytest.raises(KesalahanIndonesia, match=pesan):
            jalankan_kode(f"impor matematika\n{kode}")

    def test_acak_bisa_diulang_dengan_benih(self):
        kode = "impor acak\nacak.atur_benih(7)\nbuat a adalah angka acak dari 1 sampai 1000\nacak.atur_benih(7)\ntampilkan a adalah angka acak dari 1 sampai 1000"
        assert tangkap_output(kode) == "benar"

    @pytest.mark.parametrize("kode, pesan", [
        ("angka acak dari 10 sampai 1", "tidak boleh lebih besar"),
        ("acak.pilih([])", "kosong"),
        ("acak.bilangan(1.5, 3)", "bilangan bulat"),
    ])
    def test_acak_kesalahan(self, kode, pesan):
        with pytest.raises(KesalahanIndonesia, match=pesan):
            jalankan_kode(f"impor acak\n{kode}")

    def test_berkas_tulis_baca(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        kode = (
            "impor berkas\n"
            'berkas.tulis("catatan.txt", "baris 1\\n")\n'
            'berkas.tambahkan("catatan.txt", "baris 2")\n'
            'tampilkan berkas.baca_baris("catatan.txt"), berkas.ada("catatan.txt")\n'
            'berkas.hapus("catatan.txt")\n'
            'tampilkan berkas.ada("catatan.txt")'
        )
        assert tangkap_output(kode) == "[baris 1, baris 2] benar\nsalah"

    def test_berkas_tidak_ditemukan(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        with pytest.raises(KesalahanBerkas, match="tidak ditemukan") as info:
            jalankan_kode('impor berkas\nberkas.baca("tidak_ada.txt")')
        assert info.value.baris == 2  # baris pemanggilnya ikut dilaporkan

    def test_waktu_tanggal_indonesia(self, jam_palsu):
        kode = "impor waktu\ntampilkan hari ini, tanggal hari ini, bulan ini, tahun ini\ntampilkan waktu.tanggal_lengkap()"
        assert tangkap_output(kode) == "Kamis 1 Januari 2026 Januari 2026\nKamis, 1 Januari 2026"


# ============================================================
# Masukan
# ============================================================

class TestMasukan:
    def test_tanya_angka_mengulang_sampai_berupa_angka(self, monkeypatch):
        jawaban = iter(["dua belas", "3,5"])
        monkeypatch.setattr("builtins.input", lambda pertanyaan="": next(jawaban))
        assert tangkap_output('buat x adalah tanya angka "Angka? "\ntampilkan x dikali 2') == "Tolong jawab dengan angka.\n7"

    def test_masukan_angka_bukan_angka(self, monkeypatch):
        monkeypatch.setattr("builtins.input", lambda pertanyaan="": "abc")
        with pytest.raises(KesalahanNilai, match="bukan bilangan bulat"):
            jalankan_kode('masukan_angka("Umur? ")')

    def test_masukan_habis(self, monkeypatch):
        def habis(pertanyaan=""):
            raise EOFError
        monkeypatch.setattr("builtins.input", habis)
        with pytest.raises(KesalahanNilai, match="masukan"):
            jalankan_kode('tanya "Nama? "')

    def test_ubah_desimal_koma_indonesia(self):
        assert eval_kode('ubah_desimal("3,5")') == 3.5


# ============================================================
# Keputusan desain
# ============================================================

class TestKeputusanDesain:
    @pytest.mark.parametrize("kode, tampil", [
        ("tampilkan 10 dibagi 2", "5"),
        ("tampilkan 7 dibagi 2", "3.5"),
        ("tampilkan 0.1 ditambah 0.2", "0.3"),
        ("tampilkan 1 dibagi 3", "0.333333333333"),
        ("tampilkan -0.0", "0"),
    ])
    def test_tampilan_desimal(self, kode, tampil):
        assert tangkap_output(kode) == tampil

    def test_cetak_tanpa_pindah_baris(self):
        buf = StringIO()
        with redirect_stdout(buf):
            jalankan_kode('cetak "a"\ncetak "b", "c"\ntampilkan "d"')
        assert buf.getvalue() == "ab cd\n"

    def test_ketika_atau_dengan_nama(self):
        kode = (
            "tetap SABTU adalah 6\ntetap MINGGU adalah 7\nbuat hari adalah 7\n"
            "pilih hari:\n    ketika SABTU atau MINGGU: tampilkan \"libur\"\n    bawaan: tampilkan \"kerja\""
        )
        assert tangkap_output(kode) == "libur"


# ============================================================
# Kesalahan yang rapi
# ============================================================

class TestKesalahanRapi:
    @pytest.mark.parametrize("kode", [
        '-"a"',
        'buat d adalah [1]\nd["x"]',
        'buat d adalah [1, 2]\nd[0:"a"]',
        '"abc"[1.5]',
        'untuk i dari "a" sampai 3: tampilkan i',
        "mutlak(1, 2)",
        'jumlah(["a"])',
        'rentang("a")',
        'diurutkan([1, "a"])',
        "5 ada dalam 3",
        '"a" kurang dari 1',
        "5()",
        '{"a": 1}.hapusKunci("b")',
        "[].hapusPosisi(0)",
        'buat d adalah [2, "a"]\nd.urutkan()',
        'tunggu "sebentar"',
        'bilangan x adalah "abc"',
        "impor matematika\nmatematika.akar(\"a\")",
        "impor berkas\nberkas.baca(5)",
        "impor waktu\nwaktu.tidak_ada()",
        'buat d adalah [1]\nd.tambah(2)',
        '"halo".huruf_besar(1)',
        '"halo".ganti(1, 2)',
        "fungsi f(a, b):\n    kembalikan a\nf(1)",
        "kelas A:\n    buat x adalah 1\nA(5)",
        "ulangi \"tiga\" kali: tampilkan 1",
        "tampilkan kosong ditambah 1",
        "impor matematika.pi.x",
        "tampilkan 0 pangkat -1",
        "tampilkan 2.0 pangkat 10000",
        "tampilkan (-8) pangkat 0.5",
    ])
    def test_tidak_ada_error_python_mentah(self, kode):
        """Setiap kesalahan harus berupa kesalahan berbahasa Indonesia, bukan error Python."""
        with pytest.raises(KesalahanIndonesia):
            jalankan_kode(kode)

    def test_rekursi_dalam_berhasil(self):
        kode = "fungsi turun(n):\n    jika n adalah 0, maka kembalikan 0\n    kembalikan turun(n dikurangi 1)\ntampilkan turun(2500)"
        assert tangkap_output(kode) == "0"

    def test_rekursi_tak_berujung_bisa_ditangkap(self):
        kode = (
            "fungsi f(n):\n    kembalikan f(n ditambah 1)\n"
            "coba:\n    f(1)\ntangkap KesalahanTumpukan:\n    tampilkan \"tertangkap\"\n"
            "fungsi g(n):\n    jika n adalah 0, maka kembalikan 0\n    kembalikan g(n dikurangi 1)\n"
            "tampilkan g(2000)"  # kedalaman kembali normal setelah kesalahan
        )
        assert tangkap_output(kode) == "tertangkap\n0"

    def test_traceback_rekursi_gagal_tetap_pendek(self):
        # Traceback puluhan ribu frame membuat Pyodide (editor browser) kehabisan tumpukan saat dibebaskan.
        with pytest.raises(KesalahanTumpukan) as info:
            jalankan_kode("fungsi f(n):\n    kembalikan f(n + 1)\nf(0)")
        tb, panjang = info.value.__traceback__, 0
        while tb is not None:
            panjang, tb = panjang + 1, tb.tb_next
        assert panjang < 100

    def test_konversi_teks_berbahasa_indonesia(self):
        assert tangkap_output("teks a = benar\nteks b = kosong\nteks c = 2.0\ntampilkan a, b, c") == "benar kosong 2"

    def test_kamus_kosong_bernilai_salah(self):
        assert tangkap_output("buat k = {}\njika k: tampilkan 1\njika tidak: tampilkan 2") == "2"
        assert tangkap_output("tampilkan ubah_logika({}), ubah_logika({1: 2})") == "salah benar"

    def test_jenis_metode_adalah_fungsi(self):
        kode = "kelas A:\n    fungsi f(diri):\n        kembalikan 1\ntampilkan jenis(A().f), jenis([].tambahkan)"
        assert tangkap_output(kode) == "fungsi fungsi"

    def test_fungsi_bawaan_ditampilkan_rapi(self):
        assert tangkap_output("tampilkan panjang") == "<fungsi bawaan>"

    def test_kamus_boleh_diubah_saat_ditelusuri(self):
        kode = "buat k = {1: 1, 2: 2}\nuntuk setiap x dalam k:\n    k[x ditambah 10] = 0\ntampilkan panjang(k)"
        assert tangkap_output(kode) == "4"

    def test_teks_tidak_bisa_dipakai_dengan_sisa_bagi(self):
        with pytest.raises(KesalahanTipe):
            jalankan_kode('tampilkan "nilai %d" % 5')

    def test_bilangan_sangat_panjang_tetap_tampil(self):
        assert len(tangkap_output("tampilkan 10 pangkat 5000")) == 5001

    def test_pangkat_pecahan_bilangan_negatif(self):
        with pytest.raises(KesalahanNilai, match="Pangkat pecahan"):
            jalankan_kode("impor matematika\ntampilkan matematika.pangkat(-8, 0.5)")

    def test_parameter_diri_pada_fungsi_biasa(self):
        assert tangkap_output("fungsi f(diri):\n    kembalikan diri\ntampilkan f(3)") == "3"

    def test_saran_atribut_objek(self):
        kode = "kelas A:\n    fungsi inisialisasi():\n        diri.nilai adalah 1\ntampilkan A().nilia"
        with pytest.raises(KesalahanNama, match="Maksud Anda 'nilai'"):
            jalankan_kode(kode)
