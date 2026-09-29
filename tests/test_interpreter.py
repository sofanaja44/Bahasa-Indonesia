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
    KesalahanIndeks, KesalahanNilai,
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
        assert tangkap_output(kode) == "90.0"

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
# Semua program contoh harus berjalan tanpa error
# ============================================================

FOLDER_CONTOH = Path(__file__).resolve().parent.parent / "contoh"


@pytest.mark.parametrize("berkas", sorted(FOLDER_CONTOH.glob("*.id")), ids=lambda p: p.name)
def test_program_contoh_berjalan(berkas):
    kode = berkas.read_text(encoding="utf-8")
    buf = StringIO()
    with redirect_stdout(buf):
        jalankan_kode(kode)
    assert buf.getvalue().strip()
