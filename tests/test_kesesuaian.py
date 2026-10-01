"""
test_kesesuaian.py — Menjalankan tes kesesuaian di folder tes_kesesuaian/.

Format berkasnya dijelaskan di tes_kesesuaian/README.md. Tes ini tidak bergantung
pada detail interpreter Python, sehingga mesin lain (mis. versi Go) bisa memakai
berkas yang sama.
"""

import sys
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path

import pytest

from src.errors import KesalahanIndonesia
from src.interpreter import jalankan_kode

FOLDER = Path(__file__).resolve().parent.parent / "tes_kesesuaian"
PROGRAM = sorted(FOLDER.rglob("*.id"))


def _baca(berkas: Path) -> str:
    return berkas.read_text(encoding="utf-8").replace("\r\n", "\n")


def test_ada_tes_kesesuaian():
    assert len(PROGRAM) >= 25


@pytest.mark.parametrize("program", PROGRAM, ids=lambda p: p.relative_to(FOLDER).as_posix())
def test_kesesuaian(program: Path, monkeypatch):
    berkas_masukan = program.with_suffix(".masukan")
    berkas_keluaran = program.with_suffix(".keluaran")
    berkas_kesalahan = program.with_suffix(".kesalahan")
    assert berkas_keluaran.exists() or berkas_kesalahan.exists(), \
        "setiap program butuh berkas .keluaran atau .kesalahan"

    # Masukan: pertanyaan ditulis ke layar tanpa pindah baris, jawaban tidak ikut tampil
    sisa_masukan = _baca(berkas_masukan).splitlines() if berkas_masukan.exists() else []

    def masukan_palsu(pertanyaan=""):
        sys.stdout.write(pertanyaan)
        if not sisa_masukan:
            raise EOFError
        return sisa_masukan.pop(0)

    monkeypatch.setattr("builtins.input", masukan_palsu)
    monkeypatch.setattr("time.sleep", lambda detik: None)

    layar = StringIO()
    kesalahan = None
    with redirect_stdout(layar):
        try:
            jalankan_kode(_baca(program))
        except KesalahanIndonesia as e:
            kesalahan = e

    if berkas_keluaran.exists():
        assert layar.getvalue() == _baca(berkas_keluaran)

    if berkas_kesalahan.exists():
        nama_kesalahan, *potongan_pesan = _baca(berkas_kesalahan).strip().splitlines()
        assert kesalahan is not None, "program seharusnya berhenti dengan kesalahan"
        assert type(kesalahan).__name__ == nama_kesalahan, kesalahan.pesan
        for potongan in potongan_pesan:
            assert potongan in kesalahan.pesan
    else:
        assert kesalahan is None, f"kesalahan yang tidak diharapkan: {kesalahan}"
