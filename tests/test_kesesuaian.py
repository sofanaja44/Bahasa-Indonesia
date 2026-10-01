"""
test_kesesuaian.py — Menjalankan tes kesesuaian di folder tes_kesesuaian/.

Format berkasnya dijelaskan di tes_kesesuaian/README.md. Tes ini tidak bergantung
pada detail interpreter Python, sehingga mesin lain bisa memakai berkas yang sama.
Mesin lain dijalankan sebagai program terpisah lewat variabel lingkungan MESIN_INDONESIA,
mis. aplikasi hasil PyInstaller atau mesin Go di Tahap 3:

    MESIN_INDONESIA="dist/indonesia" python -m pytest tests/test_kesesuaian.py
"""

import os
import re
import shlex
import subprocess
import sys
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path

import pytest

from src.errors import KesalahanIndonesia
from src.interpreter import jalankan_kode

FOLDER = Path(__file__).resolve().parent.parent / "tes_kesesuaian"
PROGRAM = sorted(FOLDER.rglob("*.id"))
MESIN = os.environ.get("MESIN_INDONESIA")


def _baca(berkas: Path) -> str:
    return berkas.read_text(encoding="utf-8").replace("\r\n", "\n")


def test_ada_tes_kesesuaian():
    assert len(PROGRAM) >= 25


def _jalankan_di_sini(program: Path, masukan: str, monkeypatch):
    """Jalankan dengan interpreter Python di proses ini. Hasilnya (layar, jenis kesalahan, pesan)."""
    # Masukan: pertanyaan ditulis ke layar tanpa pindah baris, jawaban tidak ikut tampil
    sisa_masukan = masukan.splitlines()

    def masukan_palsu(pertanyaan=""):
        sys.stdout.write(pertanyaan)
        if not sisa_masukan:
            raise EOFError
        return sisa_masukan.pop(0)

    monkeypatch.setattr("builtins.input", masukan_palsu)
    monkeypatch.setattr("time.sleep", lambda detik: None)

    layar = StringIO()
    with redirect_stdout(layar):
        try:
            jalankan_kode(_baca(program))
        except KesalahanIndonesia as e:
            return layar.getvalue(), type(e).__name__, e.pesan
    return layar.getvalue(), None, None


def _jalankan_mesin(program: Path, masukan: str):
    """Jalankan dengan mesin di MESIN_INDONESIA; kesalahan dibaca dari stderr (❌ NamaKesalahan ...)."""
    perintah = shlex.split(MESIN, posix=os.name != "nt") + [str(program)]
    if Path(perintah[0]).is_file():
        perintah[0] = str(Path(perintah[0]).resolve())
    hasil = subprocess.run(
        perintah, input=masukan, capture_output=True, text=True, encoding="utf-8", timeout=60,
        env={**os.environ, "PYTHONIOENCODING": "utf-8"},
    )
    if hasil.returncode == 0:
        return hasil.stdout, None, None
    jenis = re.search(r"(Kesalahan\w*)", hasil.stderr)
    return hasil.stdout, jenis.group(1) if jenis else "?", hasil.stderr


@pytest.mark.parametrize("program", PROGRAM, ids=lambda p: p.relative_to(FOLDER).as_posix())
def test_kesesuaian(program: Path, monkeypatch):
    berkas_masukan = program.with_suffix(".masukan")
    berkas_keluaran = program.with_suffix(".keluaran")
    berkas_kesalahan = program.with_suffix(".kesalahan")
    assert berkas_keluaran.exists() or berkas_kesalahan.exists(), \
        "setiap program butuh berkas .keluaran atau .kesalahan"

    masukan = _baca(berkas_masukan) if berkas_masukan.exists() else ""
    if MESIN:
        layar, jenis, pesan = _jalankan_mesin(program, masukan)
    else:
        layar, jenis, pesan = _jalankan_di_sini(program, masukan, monkeypatch)

    if berkas_keluaran.exists():
        assert layar == _baca(berkas_keluaran)

    if berkas_kesalahan.exists():
        nama_kesalahan, *potongan_pesan = _baca(berkas_kesalahan).strip().splitlines()
        assert jenis is not None, "program seharusnya berhenti dengan kesalahan"
        assert jenis == nama_kesalahan, pesan
        for potongan in potongan_pesan:
            assert potongan in pesan
    else:
        assert jenis is None, f"kesalahan yang tidak diharapkan: {pesan}"
