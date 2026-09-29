"""
interpreter.py — Tree-walking interpreter untuk bahasa pemrograman Indonesia.
"""

from __future__ import annotations
import re
from typing import Any

from src.ast_nodes import *
from src.environment import Lingkungan
from src.bk_types import (
    BKDaftar, BKKamus, BKFungsi, BKKelas, BKInstansi, BKMetodeTerikat, BKInduk,
    SinyalKembalikan, SinyalBerhenti, SinyalLewati,
)
from src.builtins import daftar_fungsi_bawaan, _ke_teks
from src.errors import (
    KesalahanIndonesia, KesalahanTipe, KesalahanBagiNol,
    KesalahanIndeks, KesalahanNama, KesalahanNilai, KesalahanKunci,
)


class Interpreter:
    """Tree-walking interpreter untuk bahasa Indonesia."""

    def __init__(self):
        self.global_env = Lingkungan(nama="global")
        # Daftarkan fungsi bawaan
        for nama, fungsi in daftar_fungsi_bawaan().items():
            self.global_env.definisikan(nama, fungsi)

    def jalankan(self, program: NodeProgram):
        """Jalankan seluruh program."""
        return self._jalankan_blok(program.pernyataan, self.global_env)

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
            print(" ".join(_ke_teks(a) for a in args))
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

        # Modul (placeholder)
        if isinstance(node, NodeImpor):
            return None
        if isinstance(node, NodeDariImpor):
            return None

        raise KesalahanTipe(f"Node tidak dikenal: {nama_kelas}")

    # ============================
    # Format Teks (format"...")
    # ============================

    def _eval_format_teks(self, node: NodeTeksFormat, env: Lingkungan) -> str:
        template = node.template
        def ganti(match):
            expr_str = match.group(1).strip()
            from src.lexer import tokenisasi
            from src.parser import Parser
            tokens = tokenisasi(expr_str)
            if len(tokens) == 1:  # hanya EOF, mis. "{ }"
                return ""
            # Dibaca sebagai ekspresi, bukan perintah: "{x adalah 5}" membandingkan, tidak mengisi
            ekspresi = Parser(tokens, expr_str).parse_ekspresi_tunggal()
            return _ke_teks(self._eval(ekspresi, env))
        return re.sub(r"\{([^}]+)\}", ganti, template)

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
            if op == "**": return kiri ** kanan
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

        raise KesalahanTipe(f"Operator tidak dikenal: '{op}'", baris=node.baris)

    def _eval_unari(self, node: NodeOperasiUnari, env: Lingkungan):
        operand = self._eval(node.operand, env)
        if node.operator == "-":
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
        for kasus_expr, blok in node.kasus:
            kasus_val = self._eval(kasus_expr, env)
            if nilai == kasus_val:
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
            except KesalahanIndonesia:
                raise
            except Exception as e:
                raise KesalahanNilai(str(e), baris=node.baris, kolom=node.kolom)

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

    def _panggil_fungsi(self, fungsi: BKFungsi, args: list, node) -> Any:
        func_env = fungsi.lingkungan.anak(fungsi.nama)
        # Bind parameters
        for i, (param_nama, default) in enumerate(fungsi.parameter):
            if i < len(args):
                func_env.definisikan(param_nama, args[i])
            elif default is not None:
                val = self._eval(default, fungsi.lingkungan)
                func_env.definisikan(param_nama, val)
            else:
                raise KesalahanNilai(
                    f"Fungsi '{fungsi.nama}' membutuhkan parameter '{param_nama}'",
                    baris=node.baris, kolom=node.kolom,
                )
        try:
            self._jalankan_blok(fungsi.blok, func_env)
        except SinyalKembalikan as ret:
            return ret.nilai
        return None

    def _panggil_metode(self, metode: BKMetodeTerikat, args: list, node) -> Any:
        func_env = metode.fungsi.lingkungan.anak(metode.fungsi.nama)
        func_env.definisikan("diri", metode.instansi)
        kelas_pemilik = metode.fungsi.kelas
        if kelas_pemilik is not None and kelas_pemilik.induk is not None:
            # induk.inisialisasi(...) — "super" tetap didukung sebagai sinonim
            induk = BKInduk(metode.instansi, kelas_pemilik.induk)
            func_env.definisikan("induk", induk)
            func_env.definisikan("super", induk)
        for i, (param_nama, default) in enumerate(metode.fungsi.parameter):
            if param_nama == "diri":
                continue
            idx = i
            # Skip 'diri' parameter in counting
            arg_idx = idx if metode.fungsi.parameter[0][0] != "diri" else idx - 1
            if arg_idx >= 0 and arg_idx < len(args):
                func_env.definisikan(param_nama, args[arg_idx])
            elif default is not None:
                val = self._eval(default, metode.fungsi.lingkungan)
                func_env.definisikan(param_nama, val)
        try:
            self._jalankan_blok(metode.fungsi.blok, func_env)
        except SinyalKembalikan as ret:
            return ret.nilai
        return None

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
            raise KesalahanKunci(f"Kunci '{idx}' tidak ditemukan", baris=node.baris, kolom=node.kolom)
        raise KesalahanTipe("Tidak bisa mengakses indeks pada tipe ini", baris=node.baris)

    def _eval_irisan(self, node: NodeIrisanDaftar, env: Lingkungan):
        obj = self._eval(node.objek, env)
        awal = self._eval(node.awal, env) if node.awal else None
        akhir = self._eval(node.akhir, env) if node.akhir else None
        if isinstance(obj, BKDaftar):
            return BKDaftar(obj.elemen[awal:akhir])
        if isinstance(obj, str):
            return obj[awal:akhir]
        raise KesalahanTipe("Irisan hanya bisa dilakukan pada daftar atau teks", baris=node.baris)

    def _eval_akses_atribut(self, node: NodeAksesAtribut, env: Lingkungan):
        obj = self._eval(node.objek, env)
        nama = node.atribut

        if isinstance(obj, BKInstansi):
            val = obj.dapatkan(nama)
            if val is not None:
                return val
            raise KesalahanNama(f"Atribut '{nama}' tidak ditemukan pada {obj.kelas.nama}", baris=node.baris)

        if isinstance(obj, BKInduk):
            val = obj.dapatkan(nama)
            if val is not None:
                return val
            raise KesalahanNama(f"Kelas induk {obj.kelas.nama} tidak memiliki metode '{nama}'", baris=node.baris)

        if isinstance(obj, BKDaftar):
            m = obj.metode(nama)
            if m is not None:
                return m
            raise KesalahanNama(f"Daftar tidak memiliki metode '{nama}'", baris=node.baris)

        if isinstance(obj, BKKamus):
            m = obj.metode(nama)
            if m is not None:
                return m
            raise KesalahanNama(f"Kamus tidak memiliki metode '{nama}'", baris=node.baris)

        if isinstance(obj, str):
            raise KesalahanNama(f"Teks tidak memiliki metode '{nama}'", baris=node.baris)

        raise KesalahanTipe(f"Tidak bisa mengakses atribut '{nama}'", baris=node.baris)

    # ============================
    # Error handling
    # ============================

    def _eval_coba(self, node: NodeCoba, env: Lingkungan):
        try:
            return self._jalankan_blok(node.blok_coba, env.anak("coba"))
        except SinyalKembalikan:
            raise
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
