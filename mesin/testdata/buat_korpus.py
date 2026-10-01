#!/usr/bin/env python3
"""
buat_korpus.py — Membuat korpus pembanding mesin Go dari interpreter Python (acuan).

Potongan kode yang dijalankan tes Python (tests/), semua program di contoh/ dan tes_kesesuaian/,
serta program tambahan di mesin/testdata/tambahan/ dijalankan dengan interpreter Python dalam
keadaan yang bisa diulang: benih acak tetap, jam palsu, masukan tetap, dan tanpa menunggu.
Hasilnya (tampilan layar, pesan kesalahan lengkap, dan nilai terakhir seperti di REPL) disimpan
di korpus.json. Tes Go (korpus_test.go) memeriksa bahwa mesin Go menghasilkan hal yang sama persis.

    python mesin/testdata/buat_korpus.py            # tulis ulang korpus.json
    python mesin/testdata/buat_korpus.py --periksa  # gagal bila korpus.json sudah tidak sesuai
"""

import argparse
import builtins
import hashlib
import json
import os
import random
import shutil
import signal
import sys
import tempfile
import time
from contextlib import redirect_stdout
from datetime import datetime
from io import StringIO
from pathlib import Path

AKAR = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(AKAR))
KORPUS = Path(__file__).resolve().parent / "korpus.json"

# Sama dengan nilai di korpus_test.go.
MASUKAN = ["42", "Budi", "7", "3,5", "tidak", "ya", "0", "100", "-5", "abc", "", "10"]
BENIH = 12345
JAM = datetime(2026, 10, 1, 14, 30, 45)  # Kamis
BATAS_DETIK = 10


class _WaktuPalsu(datetime):
    @classmethod
    def now(cls, tz=None):
        return JAM


class _WaktuHabis(Exception):
    pass


def kumpulkan_dari_tes() -> set:
    """Semua teks yang pernah dibaca lexer selama tes Python berjalan."""
    import pytest
    from src import lexer

    kode = set()
    asli = lexer.Lexer.__init__

    def rekam(self, kode_sumber, *args, **kwargs):
        kode.add(kode_sumber)
        asli(self, kode_sumber, *args, **kwargs)

    class Perekam:
        def pytest_configure(self, config):
            lexer.Lexer.__init__ = rekam

        def pytest_unconfigure(self, config):
            lexer.Lexer.__init__ = asli

    os.environ.pop("MESIN_INDONESIA", None)
    with redirect_stdout(StringIO()):
        kode_keluar = pytest.main(
            ["-q", "-p", "no:cacheprovider", str(AKAR / "tests"), "-k", "not kesesuaian and not cli"],
            plugins=[Perekam()],
        )
    if kode_keluar != 0:
        sys.exit("Tes Python gagal; perbaiki dulu sebelum membuat korpus.")
    return kode


def kumpulkan_berkas() -> list:
    kasus = []
    for folder in ("contoh", "tes_kesesuaian", "mesin/testdata/tambahan"):
        for berkas in sorted((AKAR / folder).rglob("*.id")):
            kode = berkas.read_text(encoding="utf-8").replace("\r\n", "\n")
            masukan = berkas.with_suffix(".masukan")
            jawaban = masukan.read_text(encoding="utf-8").splitlines() if masukan.exists() else MASUKAN
            kasus.append({"nama": berkas.relative_to(AKAR).as_posix(), "kode": kode, "masukan": jawaban})
    for berkas in sorted((AKAR / "mesin/testdata/tambahan").glob("*.kasus")):
        kasus.extend(pecah_kasus(berkas))
    return kasus


def pecah_kasus(berkas: Path) -> list:
    """Berkas .kasus berisi banyak program kecil, masing-masing diawali baris '=== nama'.
    Baris pertama '#masukan: a|b|c' (boleh tidak ada) berisi jawaban untuk tanya/masukan."""
    kasus, nama, baris = [], None, []

    def simpan():
        if nama is None:
            return
        while baris and not baris[-1].strip():
            baris.pop()
        masukan = MASUKAN
        if baris and baris[0].startswith("#masukan:"):
            isi = baris[0][len("#masukan:"):].strip()
            masukan = isi.split("|") if isi else []
        kasus.append({"nama": f"{berkas.stem}/{nama}", "kode": "\n".join(baris) + "\n", "masukan": masukan})

    for b in berkas.read_text(encoding="utf-8").splitlines():
        if b.startswith("=== "):
            simpan()
            nama, baris = b[4:].strip(), []
        else:
            baris.append(b)
    simpan()
    return kasus


def jalankan(kode: str, masukan: list) -> dict | None:
    """Jalankan satu program dengan interpreter Python. None bila terlalu lama (dilewati)."""
    from indonesia import _NODE_EKSPRESI
    from src import builtins as bawaan
    from src.builtins import _ke_teks
    from src.errors import KesalahanIndonesia
    from src.interpreter import Interpreter
    from src.lexer import tokenisasi
    from src.parser import parse

    layar = StringIO()
    sisa = list(masukan)

    def masukan_palsu(pertanyaan=""):
        layar.write(str(pertanyaan))
        if not sisa:
            raise EOFError
        return sisa.pop(0)

    def waktu_habis(*_):
        raise _WaktuHabis

    asli = (builtins.input, time.sleep, bawaan.datetime)
    builtins.input, time.sleep, bawaan.datetime = masukan_palsu, (lambda detik: None), _WaktuPalsu
    random.seed(BENIH)
    folder_asal, folder = os.getcwd(), tempfile.mkdtemp()
    os.chdir(folder)
    signal.signal(signal.SIGALRM, waktu_habis)
    signal.alarm(BATAS_DETIK)
    hasil = {"keluaran": "", "kesalahan": None, "hasil": None}
    try:
        with redirect_stdout(layar):
            sys.setrecursionlimit(1000)  # seperti saat indonesia.py baru dijalankan
            tree = parse(tokenisasi(kode), kode)
            nilai = Interpreter().jalankan(tree)
            if tree.pernyataan and isinstance(tree.pernyataan[-1], _NODE_EKSPRESI) and nilai is not None:
                hasil["hasil"] = _ke_teks(nilai)
    except KesalahanIndonesia as e:
        hasil["kesalahan"] = str(e)
    except _WaktuHabis:
        return None
    except BaseException as e:  # bug interpreter Python: tidak dibandingkan dengan mesin Go
        hasil["kesalahan"] = f"INTERNAL {type(e).__name__}: {e}"
        hasil["internal"] = True
    finally:
        signal.alarm(0)
        builtins.input, time.sleep, bawaan.datetime = asli
        os.chdir(folder_asal)
        shutil.rmtree(folder, ignore_errors=True)
    hasil["keluaran"] = layar.getvalue()
    return hasil


def buat_korpus() -> list:
    kasus = kumpulkan_berkas()
    sudah = {k["kode"] for k in kasus}
    for kode in sorted(kumpulkan_dari_tes() - sudah):
        nama = "tes/" + hashlib.sha1(kode.encode("utf-8", "surrogatepass")).hexdigest()[:12]
        kasus.append({"nama": nama, "kode": kode, "masukan": MASUKAN})
    korpus = []
    for k in kasus:
        hasil = jalankan(k["kode"], k["masukan"])
        if hasil is None:
            print(f"dilewati (terlalu lama): {k['nama']}", file=sys.stderr)
            continue
        if k["masukan"] == MASUKAN:
            k = {**k, "masukan": None}
        korpus.append({**k, **hasil})
    korpus.sort(key=lambda k: k["nama"])
    return korpus


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--periksa", action="store_true", help="bandingkan dengan korpus.json tanpa menulis")
    args = parser.parse_args()
    teks = json.dumps(buat_korpus(), ensure_ascii=False, indent=1) + "\n"
    if args.periksa:
        if not KORPUS.exists() or KORPUS.read_text(encoding="utf-8") != teks:
            sys.exit("korpus.json tidak sesuai dengan interpreter Python; jalankan buat_korpus.py lalu commit.")
        print("korpus.json sesuai.")
        return
    KORPUS.write_text(teks, encoding="utf-8")
    jumlah = len(json.loads(teks))
    print(f"{jumlah} kasus ditulis ke {KORPUS.relative_to(AKAR)}")


if __name__ == "__main__":
    main()
