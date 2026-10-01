"""
interpreter.py — Tree-walking interpreter untuk bahasa pemrograman Indonesia.
"""

from __future__ import annotations
import re
import sys
from typing import Any

from src.ast_nodes import *
from src.environment import Lingkungan, saran_nama
from src.bk_types import (
    BKDaftar, BKKamus, BKFungsi, BKKelas, BKInstansi, BKMetodeTerikat, BKInduk, BKModul,
    SinyalKembalikan, SinyalBerhenti, SinyalLewati, semua_metode_teks,
)
from src.builtins import daftar_fungsi_bawaan, _ke_teks, _jenis, baca_waktu, tanya, tunggu
from src.pustaka import MODUL, bilangan_acak, muat_modul
from src.errors import (
    KesalahanIndonesia, KesalahanTipe, KesalahanBagiNol,
    KesalahanIndeks, KesalahanNama, KesalahanNilai, KesalahanKunci, KesalahanTumpukan,
)

# Paling banyak sekian panggilan fungsi bertumpuk; lebih dari itu dianggap rekursi tak berujung.
BATAS_REKURSI = 3000
# Satu panggilan fungsi di bahasa ini memakai beberapa frame Python sekaligus.
_FRAME_PYTHON_PER_PANGGILAN = 10


def _dengan_lokasi(kesalahan: KesalahanIndonesia, node) -> KesalahanIndonesia:
    """Tambahkan baris & kolom node bila kesalahan (mis. dari fungsi bawaan) belum punya lokasi."""
    if kesalahan.baris is not None:
        return kesalahan
    return type(kesalahan)(kesalahan.pesan, baris=node.baris, kolom=node.kolom)


class Interpreter:
    """Tree-walking interpreter untuk bahasa Indonesia."""

    def __init__(self):
        self.global_env = Lingkungan(nama="global")
        self.kedalaman = 0  # jumlah panggilan fungsi yang sedang bertumpuk
        # Daftarkan fungsi bawaan
        for nama, fungsi in daftar_fungsi_bawaan().items():
            self.global_env.definisikan(nama, fungsi)

    def jalankan(self, program: NodeProgram):
        """Jalankan seluruh program."""
        batas_python = BATAS_REKURSI * _FRAME_PYTHON_PER_PANGGILAN + 1000
        if sys.getrecursionlimit() < batas_python:
            sys.setrecursionlimit(batas_python)
        self.kedalaman = 0
        try:
            return self._jalankan_blok(program.pernyataan, self.global_env)
        except RecursionError:
            raise KesalahanTumpukan(
                "Program bertumpuk terlalu dalam (mis. ekspresi atau rekursi yang sangat bersarang)"
            ) from None

    def _jalankan_blok(self, blok: list, env: Lingkungan):
        hasil = None
        for stmt in blok:
            hasil = self._eval(stmt, env)
        return hasil

    # ============================
    # Evaluasi utama (dispatch)
    # ============================

    def _eval(self, node, env: Lingkungan) -> Any:
        nama_kelas = type(node).__name__

        # Literal
        if isinstance(node, NodeAngka):
            return node.nilai
        if isinstance(node, NodeTeks):
            return node.nilai
        if isinstance(node, NodeTeksFormat):
            return self._eval_format_teks(node, env)
        if isinstance(node, NodeLogika):
            return node.nilai
        if isinstance(node, NodeKosong):
            return None
        if isinstance(node, NodeIdentifier):
            return env.dapatkan(node.nama, node.baris, node.kolom)

        # Operasi
        if isinstance(node, NodeOperasiBiner):
            return self._eval_biner(node, env)
        if isinstance(node, NodeOperasiUnari):
            return self._eval_unari(node, env)

        # Deklarasi & penugasan
        if isinstance(node, NodeDeklarasiVariabel):
            return self._eval_deklarasi(node, env)
        if isinstance(node, NodeKonstanta):
            return self._eval_konstanta(node, env)
        if isinstance(node, NodePenugasan):
            return self._eval_penugasan(node, env)
        if isinstance(node, NodePenugasanGabungan):
            return self._eval_penugasan_gabungan(node, env)
        if isinstance(node, NodeTambahkan):
            return self._eval_tambahkan(node, env)

        # I/O
        if isinstance(node, NodeTampilkan):
            args = [self._eval(e, env) for e in node.ekspresi_list]
            teks = " ".join(_ke_teks(a) for a in args)
            if node.baris_baru:
                print(teks)
            else:
                print(teks, end="", flush=True)  # cetak: tetap di baris yang sama
            return None
        if isinstance(node, NodeTunggu):
            try:
                tunggu(self._eval(node.lama, env), node.faktor)
            except KesalahanIndonesia as e:
                raise _dengan_lokasi(e, node) from None
            return None

        # Kondisi
        if isinstance(node, NodeJika):
            return self._eval_jika(node, env)
        if isinstance(node, NodePilih):
            return self._eval_pilih(node, env)

        # Perulangan
        if isinstance(node, NodeSelama):
            return self._eval_selama(node, env)
        if isinstance(node, NodeUntuk):
            return self._eval_untuk(node, env)
        if isinstance(node, NodeUntukSetiap):
            return self._eval_untuk_setiap(node, env)
        if isinstance(node, NodeUlangi):
            return self._eval_ulangi(node, env)
        if isinstance(node, NodeUlangiKali):
            return self._eval_ulangi_kali(node, env)
        if isinstance(node, NodeBerhenti):
            raise SinyalBerhenti()
        if isinstance(node, NodeLewati):
            raise SinyalLewati()

        # Fungsi
        if isinstance(node, NodeFungsi):
            return self._eval_def_fungsi(node, env)
        if isinstance(node, NodeFungsiAnonim):
            return BKFungsi("<anonim>", node.parameter, [NodeKembalikan(node.ekspresi)], env)
        if isinstance(node, NodePanggilFungsi):
            return self._eval_panggil(node, env)
        if isinstance(node, NodeKembalikan):
            nilai = self._eval(node.ekspresi, env) if node.ekspresi else None
            raise SinyalKembalikan(nilai)

        # Koleksi
        if isinstance(node, NodeDaftar):
            return BKDaftar([self._eval(e, env) for e in node.elemen])
        if isinstance(node, NodeKamus):
            data = {}
            for k, v in node.pasangan:
                data[self._eval(k, env)] = self._eval(v, env)
            return BKKamus(data)
        if isinstance(node, NodeAksesDaftar):
            return self._eval_akses_daftar(node, env)
        if isinstance(node, NodeIrisanDaftar):
            return self._eval_irisan(node, env)
        if isinstance(node, NodeAksesAtribut):
            return self._eval_akses_atribut(node, env)

        # OOP
        if isinstance(node, NodeKelas):
            return self._eval_def_kelas(node, env)

        # Error handling
        if isinstance(node, NodeCoba):
            return self._eval_coba(node, env)
        if isinstance(node, NodeLempar):
            return self._eval_lempar(node, env)

        # Modul
        if isinstance(node, NodeImpor):
            return self._eval_impor(node, env)
        if isinstance(node, NodeDariImpor):
            return self._eval_dari_impor(node, env)

        # Waktu, angka acak, dan masukan (jarang dipakai, jadi diperiksa paling akhir)
        if isinstance(node, NodeWaktuSekarang):
            return baca_waktu(node.bagian)
        if isinstance(node, NodeAngkaAcak):
            try:
                return bilangan_acak(self._eval(node.minimum, env), self._eval(node.maksimum, env))
            except KesalahanIndonesia as e:
                raise _dengan_lokasi(e, node) from None
        if isinstance(node, NodeTanya):
            try:
                return tanya(self._eval(node.pertanyaan, env), node.jenis)
            except KesalahanIndonesia as e:
                raise _dengan_lokasi(e, node) from None

        raise KesalahanTipe(f"Node tidak dikenal: {nama_kelas}")

    # ============================
    # Modul (impor)
    # ============================

    def _muat_modul(self, nama: str, node) -> BKModul:
        if nama not in MODUL:
            daftar = ", ".join(MODUL)
            raise KesalahanNama(
                f"Modul '{nama}' tidak ada.{saran_nama(nama, MODUL)} Modul yang tersedia: {daftar}",
                baris=node.baris, kolom=node.kolom,
            )
        return muat_modul(nama)

    def _isi_modul(self, modul: BKModul, nama: str, node):
        if nama not in modul.isi:
            raise KesalahanNama(
                f"Modul '{modul.nama}' tidak memiliki '{nama}'.{saran_nama(nama, modul.isi)}",
                baris=node.baris, kolom=node.kolom,
            )
        return modul.isi[nama]

    def _eval_impor(self, node: NodeImpor, env: Lingkungan):
        """impor matematika / impor matematika sebagai m / impor matematika.akar sebagai akar"""
        nama_modul, *bagian = node.modul.split(".")
        nilai = self._muat_modul(nama_modul, node)
        for sebelumnya, nama in zip([nama_modul, *bagian], bagian):
            if not isinstance(nilai, BKModul):
                raise KesalahanNama(f"'{sebelumnya}' bukan modul, jadi tidak punya '{nama}'",
                                    baris=node.baris, kolom=node.kolom)
            nilai = self._isi_modul(nilai, nama, node)
        if node.alias:
            env.definisikan(node.alias, nilai)
        elif bagian:
            env.definisikan(bagian[-1], nilai)
        else:
            env.definisikan(nama_modul, nilai)
        return None

    def _eval_dari_impor(self, node: NodeDariImpor, env: Lingkungan):
        """dari matematika impor akar / dari acak impor bilangan sebagai dadu"""
        modul = self._muat_modul(node.modul, node)
        env.definisikan(node.alias or node.nama, self._isi_modul(modul, node.nama, node))
        return None

    # ============================
    # Format Teks (format"...")
    # ============================

    def _eval_format_teks(self, node: NodeTeksFormat, env: Lingkungan) -> str:
        from src.lexer import tokenisasi
        from src.parser import Parser
        template = node.template
        # Perulangan biasa (bukan re.sub dengan callback) agar rekursi di dalam {...}
        # tidak menumpuk di tumpukan C Python.
        bagian, akhir_sebelumnya = [], 0
        for cocok in re.finditer(r"\{([^}]+)\}", template):
            bagian.append(template[akhir_sebelumnya:cocok.start()])
            expr_str = cocok.group(1).strip()
            tokens = tokenisasi(expr_str)
            if len(tokens) > 1:  # "{ }" (hanya EOF) menjadi teks kosong
                # Dibaca sebagai ekspresi, bukan perintah: "{x adalah 5}" membandingkan, tidak mengisi
                ekspresi = Parser(tokens, expr_str).parse_ekspresi_tunggal()
                bagian.append(_ke_teks(self._eval(ekspresi, env)))
            akhir_sebelumnya = cocok.end()
        bagian.append(template[akhir_sebelumnya:])
        return "".join(bagian)

    # ============================
    # Operasi biner
    # ============================

    def _eval_biner(self, node: NodeOperasiBiner, env: Lingkungan):
        # Short-circuit untuk logika
        if node.operator == "dan":
            kiri = self._eval(node.kiri, env)
            return kiri and self._eval(node.kanan, env)
        if node.operator == "atau":
            kiri = self._eval(node.kiri, env)
            return kiri or self._eval(node.kanan, env)

        kiri = self._eval(node.kiri, env)
        kanan = self._eval(node.kanan, env)
        return self._hitung_biner(node.operator, kiri, kanan, node)

    def _hitung_biner(self, op: str, kiri, kanan, node):
        """Hitung operasi biner pada dua nilai yang sudah dievaluasi."""
        try:
            if op in ("ada dalam", "tidak ada dalam"):
                if not isinstance(kanan, (BKDaftar, BKKamus, str)):
                    raise KesalahanTipe(f"Operasi '{op}' membutuhkan daftar, kamus, atau teks", baris=node.baris)
                ada = kiri in kanan
                return ada if op == "ada dalam" else not ada
            if op == "+":
                if isinstance(kiri, str) and isinstance(kanan, str):
                    return kiri + kanan
                if isinstance(kiri, str) or isinstance(kanan, str):
                    return _ke_teks(kiri) + _ke_teks(kanan)
                return kiri + kanan
            if op == "-": return kiri - kanan
            if op == "*":
                if isinstance(kiri, str) and isinstance(kanan, int):
                    return kiri * kanan
                return kiri * kanan
            if op == "/":
                if kanan == 0:
                    raise KesalahanBagiNol("Tidak bisa membagi dengan nol", baris=node.baris, kolom=node.kolom)
                return kiri / kanan
            if op == "%":
                if kanan == 0:
                    raise KesalahanBagiNol("Tidak bisa membagi dengan nol", baris=node.baris, kolom=node.kolom)
                return kiri % kanan
            if op == "**":
                hasil = kiri ** kanan
                if isinstance(hasil, complex):
                    raise KesalahanNilai("Pangkat pecahan dari bilangan negatif tidak bisa dihitung",
                                         baris=node.baris, kolom=node.kolom)
                return hasil
            if op == "==": return kiri == kanan
            if op == "!=": return kiri != kanan
            if op == ">": return kiri > kanan
            if op == "<": return kiri < kanan
            if op == ">=": return kiri >= kanan
            if op == "<=": return kiri <= kanan
        except KesalahanIndonesia:
            raise
        except TypeError as e:
            raise KesalahanTipe(
                f"Tipe data tidak cocok untuk operasi '{op}': {_ke_teks(kiri)} dan {_ke_teks(kanan)}",
                baris=node.baris, kolom=node.kolom,
            )
        except ZeroDivisionError:
            raise KesalahanBagiNol("Tidak bisa membagi dengan nol", baris=node.baris, kolom=node.kolom) from None
        except (OverflowError, MemoryError):
            raise KesalahanNilai("Hasil perhitungan terlalu besar", baris=node.baris, kolom=node.kolom) from None

        raise KesalahanTipe(f"Operator tidak dikenal: '{op}'", baris=node.baris)

    def _eval_unari(self, node: NodeOperasiUnari, env: Lingkungan):
        operand = self._eval(node.operand, env)
        if node.operator == "-":
            if isinstance(operand, bool) or not isinstance(operand, (int, float)):
                raise KesalahanTipe(f"Tanda minus hanya untuk angka, bukan '{_ke_teks(operand)}'",
                                    baris=node.baris, kolom=node.kolom)
            return -operand
        if node.operator == "bukan":
            return not operand
        raise KesalahanTipe(f"Operator unari tidak dikenal: '{node.operator}'", baris=node.baris)

    # ============================
    # Deklarasi & penugasan
    # ============================

    def _eval_deklarasi(self, node: NodeDeklarasiVariabel, env: Lingkungan):
        nilai = self._eval(node.ekspresi, env)
        if node.tipe_eksplisit:
            nilai = self._konversi_tipe(nilai, node.tipe_eksplisit, node.baris, node.kolom)
        env.definisikan(node.nama, nilai)
        return nilai

    def _eval_konstanta(self, node: NodeKonstanta, env: Lingkungan):
        nilai = self._eval(node.ekspresi, env)
        env.definisikan(node.nama, nilai, konstanta=True)
        return nilai

    def _konversi_tipe(self, nilai, tipe: str, baris: int, kolom: int):
        try:
            if tipe == "bilangan": return int(nilai) if not isinstance(nilai, bool) else int(nilai)
            if tipe == "desimal": return float(nilai)
            if tipe == "teks": return str(nilai)
            if tipe == "logika": return bool(nilai)
        except (ValueError, TypeError):
            raise KesalahanTipe(f"Tidak bisa mengubah nilai ke tipe '{tipe}'", baris=baris, kolom=kolom)
        return nilai

    def _eval_penugasan(self, node: NodePenugasan, env: Lingkungan):
        nilai = self._eval(node.ekspresi, env)
        self._setel_target(node.target, nilai, env, node)
        return nilai

    def _setel_target(self, target, nilai, env: Lingkungan, node):
        """Simpan nilai ke variabel, elemen daftar/kamus, atau atribut objek."""
        if isinstance(target, NodeIdentifier):
            env.setel(target.nama, nilai, target.baris, target.kolom)
        elif isinstance(target, NodeAksesDaftar):
            obj = self._eval(target.objek, env)
            idx = self._eval(target.indeks, env)
            if not isinstance(obj, (BKDaftar, BKKamus)):
                raise KesalahanTipe("Tidak bisa mengakses indeks pada tipe ini", baris=node.baris)
            try:
                obj[idx] = nilai
            except IndexError:
                raise KesalahanIndeks(f"Indeks {idx} di luar batas daftar", baris=node.baris, kolom=node.kolom)
            except TypeError:
                raise KesalahanTipe(f"Indeks daftar harus berupa bilangan bulat, bukan '{_ke_teks(idx)}'",
                                    baris=node.baris, kolom=node.kolom)
        elif isinstance(target, NodeAksesAtribut):
            obj = self._eval(target.objek, env)
            if isinstance(obj, BKInstansi):
                obj.setel(target.atribut, nilai)
            else:
                raise KesalahanTipe("Tidak bisa menyetel atribut pada tipe ini", baris=node.baris)
        else:
            raise KesalahanTipe("Bagian ini tidak bisa diberi nilai", baris=node.baris, kolom=node.kolom)

    def _eval_penugasan_gabungan(self, node: NodePenugasanGabungan, env: Lingkungan):
        lama = self._eval(node.target, env)
        kanan = self._eval(node.ekspresi, env)
        op = {"+=": "+", "-=": "-", "*=": "*", "/=": "/", "%=": "%"}[node.operator]
        baru = self._hitung_biner(op, lama, kanan, node)
        self._setel_target(node.target, baru, env, node)
        return baru

    def _eval_tambahkan(self, node: NodeTambahkan, env: Lingkungan):
        """tambahkan X ke Y: masukkan X ke daftar Y, atau Y = Y + X untuk angka/teks."""
        nilai = self._eval(node.nilai, env)
        wadah = self._eval(node.target, env)
        if isinstance(wadah, BKDaftar):
            wadah.tambahkan(nilai)
            return wadah
        if isinstance(wadah, BKKamus):
            raise KesalahanTipe("Tidak bisa 'tambahkan' ke kamus. Gunakan kamus[kunci] = nilai",
                                baris=node.baris, kolom=node.kolom)
        baru = self._hitung_biner("+", wadah, nilai, node)
        self._setel_target(node.target, baru, env, node)
        return baru

    # ============================
    # Kondisi
    # ============================

    def _eval_jika(self, node: NodeJika, env: Lingkungan):
        if self._eval(node.kondisi, env):
            return self._jalankan_blok(node.blok_jika, env.anak("jika"))
        for kondisi, blok in node.cabang_atau_jika:
            if self._eval(kondisi, env):
                return self._jalankan_blok(blok, env.anak("atau_jika"))
        if node.blok_selainnya is not None:
            return self._jalankan_blok(node.blok_selainnya, env.anak("selainnya"))
        return None

    def _eval_pilih(self, node: NodePilih, env: Lingkungan):
        nilai = self._eval(node.ekspresi, env)
        for daftar_nilai, blok in node.kasus:
            # ketika "Sabtu" atau "Minggu": cocok bila sama dengan salah satunya
            for kasus_expr in daftar_nilai:
                if nilai == self._eval(kasus_expr, env):
                    return self._jalankan_blok(blok, env.anak("ketika"))
        if node.bawaan is not None:
            return self._jalankan_blok(node.bawaan, env.anak("bawaan"))
        return None

    # ============================
    # Perulangan
    # ============================

    def _eval_selama(self, node: NodeSelama, env: Lingkungan):
        while self._eval(node.kondisi, env):
            try:
                self._jalankan_blok(node.blok, env.anak("selama"))
            except SinyalBerhenti:
                break
            except SinyalLewati:
                continue
        return None

    def _eval_untuk(self, node: NodeUntuk, env: Lingkungan):
        dari = self._eval(node.dari_expr, env)
        sampai = self._eval(node.sampai_expr, env)
        langkah = self._eval(node.langkah_expr, env) if node.langkah_expr else 1
        for bagian, nilai in (("dari", dari), ("sampai", sampai), ("langkah", langkah)):
            if isinstance(nilai, bool) or not isinstance(nilai, (int, float)):
                raise KesalahanTipe(f"Nilai '{bagian}' pada perulangan 'untuk' harus angka, bukan '{_ke_teks(nilai)}'",
                                    baris=node.baris, kolom=node.kolom)
        i = dari
        while (langkah > 0 and i <= sampai) or (langkah < 0 and i >= sampai):
            loop_env = env.anak("untuk")
            loop_env.definisikan(node.variabel, i)
            try:
                self._jalankan_blok(node.blok, loop_env)
            except SinyalBerhenti:
                break
            except SinyalLewati:
                pass
            i += langkah
        return None

    def _eval_untuk_setiap(self, node: NodeUntukSetiap, env: Lingkungan):
        iterable = self._eval(node.iterable, env)
        if not isinstance(iterable, (BKDaftar, BKKamus, str)):
            raise KesalahanTipe(
                f"'untuk setiap' hanya bisa menelusuri daftar, kamus, atau teks, bukan '{_ke_teks(iterable)}'",
                baris=node.baris, kolom=node.kolom,
            )
        items = iterable.elemen if isinstance(iterable, BKDaftar) else iterable
        for item in items:
            loop_env = env.anak("untuk_setiap")
            loop_env.definisikan(node.variabel, item)
            try:
                self._jalankan_blok(node.blok, loop_env)
            except SinyalBerhenti:
                break
            except SinyalLewati:
                continue
        return None

    def _eval_ulangi(self, node: NodeUlangi, env: Lingkungan):
        while True:
            try:
                self._jalankan_blok(node.blok, env.anak("ulangi"))
            except SinyalBerhenti:
                break
            except SinyalLewati:
                pass
            if not self._eval(node.kondisi, env):
                break
        return None

    def _eval_ulangi_kali(self, node: NodeUlangiKali, env: Lingkungan):
        jumlah = self._eval(node.jumlah, env)
        if isinstance(jumlah, float) and jumlah.is_integer():
            jumlah = int(jumlah)  # hasil pembagian seperti 6 / 2 tetap boleh
        if isinstance(jumlah, bool) or not isinstance(jumlah, int):
            raise KesalahanTipe(
                f"Jumlah perulangan harus bilangan bulat, bukan '{_ke_teks(jumlah)}'",
                baris=node.baris, kolom=node.kolom,
            )
        for _ in range(jumlah):
            try:
                self._jalankan_blok(node.blok, env.anak("ulangi"))
            except SinyalBerhenti:
                break
            except SinyalLewati:
                continue
        return None

    # ============================
    # Fungsi
    # ============================

    def _eval_def_fungsi(self, node: NodeFungsi, env: Lingkungan):
        fungsi = BKFungsi(node.nama, node.parameter, node.blok, env, node)
        env.definisikan(node.nama, fungsi)
        return fungsi

    def _eval_panggil(self, node: NodePanggilFungsi, env: Lingkungan):
        callee = self._eval(node.fungsi, env)
        args = [self._eval(a, env) for a in node.argumen]

        # Built-in function (Python callable)
        if callable(callee) and not isinstance(callee, (BKFungsi, BKKelas, BKMetodeTerikat)):
            try:
                return callee(*args)
            except KesalahanIndonesia as e:
                raise _dengan_lokasi(e, node) from None
            except TypeError:
                # Biasanya jumlah argumen salah, mis. mutlak(1, 2)
                raise KesalahanTipe(
                    f"'{self._nama_pemanggilan(node.fungsi)}' dipanggil dengan argumen yang tidak sesuai",
                    baris=node.baris, kolom=node.kolom,
                ) from None
            except (ValueError, ArithmeticError, LookupError, OSError) as e:
                raise KesalahanNilai(
                    f"'{self._nama_pemanggilan(node.fungsi)}' tidak bisa menghitung dengan nilai ini",
                    baris=node.baris, kolom=node.kolom,
                ) from e

        # User-defined function
        if isinstance(callee, BKFungsi):
            return self._panggil_fungsi(callee, args, node)

        # Bound method
        if isinstance(callee, BKMetodeTerikat):
            return self._panggil_metode(callee, args, node)

        # Class instantiation
        if isinstance(callee, BKKelas):
            return self._buat_instansi(callee, args, node)

        raise KesalahanTipe(
            f"'{_ke_teks(callee)}' bukan fungsi dan tidak bisa dipanggil",
            baris=node.baris, kolom=node.kolom,
        )

    @staticmethod
    def _nama_pemanggilan(node) -> str:
        """Nama yang dipanggil untuk pesan kesalahan: 'akar', 'matematika.akar', ..."""
        if isinstance(node, NodeIdentifier):
            return node.nama
        if isinstance(node, NodeAksesAtribut):
            return f"{Interpreter._nama_pemanggilan(node.objek)}.{node.atribut}"
        return "fungsi"

    def _ikat_parameter(self, fungsi: BKFungsi, args: list, func_env: Lingkungan, node, metode: bool = False):
        """Isi parameter fungsi dengan argumen; pada metode, parameter 'diri' dilewati."""
        parameter = [(nama, bawaan) for nama, bawaan in fungsi.parameter if not (metode and nama == "diri")]
        if len(args) > len(parameter):
            raise KesalahanTipe(
                f"Fungsi '{fungsi.nama}' menerima {len(parameter)} argumen, tetapi diberi {len(args)}",
                baris=node.baris, kolom=node.kolom,
            )
        for i, (nama, bawaan) in enumerate(parameter):
            if i < len(args):
                func_env.definisikan(nama, args[i])
            elif bawaan is not None:
                func_env.definisikan(nama, self._eval(bawaan, fungsi.lingkungan))
            else:
                raise KesalahanNilai(
                    f"Fungsi '{fungsi.nama}' membutuhkan parameter '{nama}'",
                    baris=node.baris, kolom=node.kolom,
                )

    def _jalankan_isi_fungsi(self, fungsi: BKFungsi, func_env: Lingkungan, node) -> Any:
        if self.kedalaman >= BATAS_REKURSI:
            batas = f"{BATAS_REKURSI:,}".replace(",", ".")
            raise KesalahanTumpukan(
                f"Fungsi '{fungsi.nama}' dipanggil bertumpuk lebih dari {batas} kali. "
                "Mungkin fungsi ini terus memanggil dirinya sendiri tanpa berhenti; "
                "pastikan ada kondisi untuk berhenti.",
                baris=node.baris, kolom=node.kolom,
            )
        self.kedalaman += 1
        try:
            self._jalankan_blok(fungsi.blok, func_env)
        except SinyalKembalikan as ret:
            return ret.nilai
        finally:
            self.kedalaman -= 1
        return None

    def _panggil_fungsi(self, fungsi: BKFungsi, args: list, node) -> Any:
        func_env = fungsi.lingkungan.anak(fungsi.nama)
        self._ikat_parameter(fungsi, args, func_env, node)
        return self._jalankan_isi_fungsi(fungsi, func_env, node)

    def _panggil_metode(self, metode: BKMetodeTerikat, args: list, node) -> Any:
        func_env = metode.fungsi.lingkungan.anak(metode.fungsi.nama)
        func_env.definisikan("diri", metode.instansi)
        kelas_pemilik = metode.fungsi.kelas
        if kelas_pemilik is not None and kelas_pemilik.induk is not None:
            # induk.inisialisasi(...) — "super" tetap didukung sebagai sinonim
            induk = BKInduk(metode.instansi, kelas_pemilik.induk)
            func_env.definisikan("induk", induk)
            func_env.definisikan("super", induk)
        self._ikat_parameter(metode.fungsi, args, func_env, node, metode=True)
        return self._jalankan_isi_fungsi(metode.fungsi, func_env, node)

    # ============================
    # OOP
    # ============================

    def _eval_def_kelas(self, node: NodeKelas, env: Lingkungan):
        induk_kelas = None
        if node.induk:
            induk_kelas = env.dapatkan(node.induk, node.baris, node.kolom)

        metode = {}
        atribut = {}
        kelas_env = env.anak(node.nama)

        for stmt in node.blok:
            if isinstance(stmt, NodeFungsi):
                f = BKFungsi(stmt.nama, stmt.parameter, stmt.blok, kelas_env, stmt)
                metode[stmt.nama] = f
            elif isinstance(stmt, NodeDeklarasiVariabel):
                atribut[stmt.nama] = self._eval(stmt.ekspresi, kelas_env)

        kelas = BKKelas(node.nama, induk_kelas, metode, atribut)
        for f in metode.values():
            f.kelas = kelas
        env.definisikan(node.nama, kelas)
        return kelas

    def _buat_instansi(self, kelas: BKKelas, args: list, node) -> BKInstansi:
        instansi = BKInstansi(kelas)
        # Copy parent attributes
        if kelas.induk and kelas.induk.atribut:
            for k, v in kelas.induk.atribut.items():
                if k not in instansi.atribut:
                    instansi.atribut[k] = v
        # Call inisialisasi if exists
        init = kelas.cari_metode("inisialisasi")
        if init:
            metode = BKMetodeTerikat(instansi, init)
            self._panggil_metode(metode, args, node)
        elif args:
            raise KesalahanTipe(
                f"Kelas '{kelas.nama}' tidak punya fungsi 'inisialisasi', jadi tidak menerima argumen",
                baris=node.baris, kolom=node.kolom,
            )
        return instansi

    # ============================
    # Akses koleksi & atribut
    # ============================

    def _eval_akses_daftar(self, node: NodeAksesDaftar, env: Lingkungan):
        obj = self._eval(node.objek, env)
        idx = self._eval(node.indeks, env)
        try:
            if isinstance(obj, (BKDaftar, BKKamus, str, list, dict)):
                return obj[idx]
        except IndexError:
            raise KesalahanIndeks(f"Indeks {idx} di luar batas daftar", baris=node.baris, kolom=node.kolom)
        except KeyError:
            raise KesalahanKunci(f"Kunci '{_ke_teks(idx)}' tidak ditemukan", baris=node.baris, kolom=node.kolom)
        except TypeError:
            raise KesalahanTipe(f"Indeks {_jenis(obj)} harus berupa bilangan bulat, bukan '{_ke_teks(idx)}'",
                                baris=node.baris, kolom=node.kolom)
        raise KesalahanTipe(f"Tidak bisa mengambil isi dengan indeks dari {_jenis(obj)}", baris=node.baris)

    def _eval_irisan(self, node: NodeIrisanDaftar, env: Lingkungan):
        obj = self._eval(node.objek, env)
        awal = self._eval(node.awal, env) if node.awal else None
        akhir = self._eval(node.akhir, env) if node.akhir else None
        for batas in (awal, akhir):
            if batas is not None and (isinstance(batas, bool) or not isinstance(batas, int)):
                raise KesalahanTipe(f"Batas irisan harus bilangan bulat, bukan '{_ke_teks(batas)}'",
                                    baris=node.baris, kolom=node.kolom)
        if isinstance(obj, BKDaftar):
            return BKDaftar(obj.elemen[awal:akhir])
        if isinstance(obj, str):
            return obj[awal:akhir]
        raise KesalahanTipe("Irisan hanya bisa dilakukan pada daftar atau teks", baris=node.baris)

    def _eval_akses_atribut(self, node: NodeAksesAtribut, env: Lingkungan):
        obj = self._eval(node.objek, env)
        nama = node.atribut

        if isinstance(obj, BKInstansi):
            if nama in obj.atribut:  # termasuk atribut yang bernilai kosong
                return obj.atribut[nama]
            val = obj.dapatkan(nama)
            if val is not None:
                return val
            kandidat = set(obj.atribut) | self._nama_metode_kelas(obj.kelas)
            raise KesalahanNama(f"Atribut '{nama}' tidak ditemukan pada {obj.kelas.nama}.{saran_nama(nama, kandidat)}",
                                baris=node.baris, kolom=node.kolom)

        if isinstance(obj, BKInduk):
            val = obj.dapatkan(nama)
            if val is not None:
                return val
            raise KesalahanNama(f"Kelas induk {obj.kelas.nama} tidak memiliki metode '{nama}'", baris=node.baris)

        if isinstance(obj, BKModul):
            return self._isi_modul(obj, nama, node)

        if isinstance(obj, (BKDaftar, BKKamus, str)):
            semua = semua_metode_teks(obj) if isinstance(obj, str) else obj.semua_metode()
            if nama in semua:
                return semua[nama]
            raise KesalahanNama(
                f"{_jenis(obj).capitalize()} tidak memiliki metode '{nama}'.{saran_nama(nama, semua)}",
                baris=node.baris, kolom=node.kolom,
            )

        raise KesalahanTipe(f"Tidak bisa mengakses atribut '{nama}' pada {_jenis(obj)}", baris=node.baris)

    @staticmethod
    def _nama_metode_kelas(kelas: BKKelas) -> set:
        nama = set()
        while kelas is not None:
            nama.update(kelas.metode)
            kelas = kelas.induk
        return nama

    # ============================
    # Error handling
    # ============================

    def _eval_coba(self, node: NodeCoba, env: Lingkungan):
        try:
            return self._jalankan_blok(node.blok_coba, env.anak("coba"))
        except (SinyalKembalikan, SinyalBerhenti, SinyalLewati):
            raise  # kembalikan/berhenti/lewati di dalam 'coba' bukan kesalahan
        except Exception as e:
            for tipe_error, variabel, blok in node.penangkap:
                # Match error type if specified
                if tipe_error and not type(e).__name__.endswith(tipe_error) and tipe_error != type(e).__name__:
                    continue
                catch_env = env.anak("tangkap")
                if variabel:
                    err_msg = e.pesan if hasattr(e, 'pesan') else str(e)
                    catch_env.definisikan(variabel, err_msg)
                return self._jalankan_blok(blok, catch_env)
            raise
        finally:
            if node.blok_akhirnya:
                self._jalankan_blok(node.blok_akhirnya, env.anak("akhirnya"))

    def _eval_lempar(self, node: NodeLempar, env: Lingkungan):
        nilai = self._eval(node.ekspresi, env)
        if isinstance(nilai, str):
            raise KesalahanNilai(nilai, baris=node.baris, kolom=node.kolom)
        raise KesalahanNilai(_ke_teks(nilai), baris=node.baris, kolom=node.kolom)


# ============================
# Fungsi utilitas
# ============================

def jalankan_kode(kode_sumber: str) -> Any:
    """Shortcut: parse dan jalankan kode sumber."""
    from src.lexer import tokenisasi
    from src.parser import parse
    tokens = tokenisasi(kode_sumber)
    tree = parse(tokens, kode_sumber)
    interpreter = Interpreter()
    return interpreter.jalankan(tree)
