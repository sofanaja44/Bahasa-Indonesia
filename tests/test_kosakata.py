"""
test_kosakata.py — Alat bantu (editor web, VS Code) harus mengikuti kosakata bahasa.
"""

import importlib.util
from pathlib import Path

from src.kosakata import kosakata
from src.token_types import FRASA_KATA_KUNCI, KATA_KUNCI

AKAR = Path(__file__).resolve().parent.parent


def _muat(path: Path):
    spec = importlib.util.spec_from_file_location(path.stem, path)
    modul = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(modul)
    return modul


def test_semua_kata_kunci_dan_frasa_punya_warna():
    kosa = kosakata()
    assert set(kosa["kata_kunci"]) == set(KATA_KUNCI)
    assert set(kosa["frasa"]) == {" ".join(f) for f in FRASA_KATA_KUNCI}
    assert set(kosa["kata_kunci"].values()) | set(kosa["frasa"].values()) <= {"kunci", "operator", "nilai", "tipe"}


def test_grammar_vscode_tidak_tertinggal():
    bangun = _muat(AKAR / "vscode" / "bangun.py")
    tersimpan = bangun.BERKAS_GRAMMAR.read_text(encoding="utf-8")
    assert tersimpan == bangun.teks_grammar(), "Kosakata berubah: jalankan  python vscode/bangun.py"
