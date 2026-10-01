"""
test_cli.py — Test perintah baris (CLI) indonesia.py.
"""

import os
import shlex
import subprocess
import sys
from pathlib import Path

AKAR = Path(__file__).resolve().parent.parent
# Mesin lain (mis. mesin Go) bisa diuji dengan tes yang sama: MESIN_INDONESIA="mesin/indonesia"
MESIN = os.environ.get("MESIN_INDONESIA")


def jalankan_cli(*args, masukan=""):
    if MESIN:
        perintah = shlex.split(MESIN, posix=os.name != "nt")
        if Path(perintah[0]).is_file():
            perintah[0] = str(Path(perintah[0]).resolve())
    else:
        perintah = [sys.executable, str(AKAR / "indonesia.py")]
    return subprocess.run(
        [*perintah, *args],
        input=masukan, capture_output=True, text=True, encoding="utf-8", timeout=30,
        env={**os.environ, "PYTHONIOENCODING": "utf-8"},
    )


def test_versi():
    hasil = jalankan_cli("versi")
    assert hasil.returncode == 0
    assert hasil.stdout.startswith("Indonesia v")


def test_bantu():
    """README menyuruh 'python indonesia.py bantu' — dulu dianggap nama berkas."""
    hasil = jalankan_cli("bantu")
    assert hasil.returncode == 0
    assert "Penggunaan" in hasil.stdout


def test_repl_menampilkan_hasil_dalam_bahasa_indonesia():
    hasil = jalankan_cli("repl", masukan="5 lebih dari 3\nkeluar\n")
    assert hasil.returncode == 0
    assert "benar" in hasil.stdout
    assert "True" not in hasil.stdout


def test_jalankan_berkas():
    hasil = jalankan_cli(str(AKAR / "contoh" / "halo_dunia.id"))
    assert hasil.returncode == 0
    assert hasil.stdout.strip() == "Halo Dunia!"


def test_berkas_tidak_ditemukan():
    hasil = jalankan_cli("tidak_ada.id")
    assert hasil.returncode == 1
    assert "tidak ditemukan" in hasil.stdout


def test_repl_blok_beberapa_baris():
    masukan = "buat x adalah 7\njika x habis dibagi 7:\n    tampilkan \"tujuh\"\n    tampilkan \"selesai\"\n\nx\nkeluar\n"
    hasil = jalankan_cli("repl", masukan=masukan)
    assert "tujuh\nselesai" in hasil.stdout
    assert ">>> 7" in hasil.stdout.replace("... ", "")  # ekspresi 'x' ditampilkan
    assert "Kesalahan" not in hasil.stdout


def test_repl_tidak_menampilkan_hasil_deklarasi():
    hasil = jalankan_cli("repl", masukan="buat nama adalah \"Budi\"\nkeluar\n")
    assert "Budi" not in hasil.stdout


def test_eval_kesalahan_keluar_dengan_kode_1():
    hasil = jalankan_cli("-e", "tampilkan 1 dibagi 0")
    assert hasil.returncode == 1
    assert "KesalahanBagiNol" in hasil.stderr
