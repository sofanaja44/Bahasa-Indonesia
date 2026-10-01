#!/usr/bin/env python3
"""
bangun.py — Membuat grammar pewarnaan kode VS Code (syntaxes/indonesia.tmLanguage.json)
dari kosakata bahasa (src/kosakata.py).

    python vscode/bangun.py

Jalankan ulang setiap kali kata kunci bahasa berubah. tests/test_kosakata.py memastikan
grammar yang tersimpan di git tidak tertinggal.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

FOLDER = Path(__file__).resolve().parent
sys.path.insert(0, str(FOLDER.parent))

from src.kosakata import KATA_PERINTAH, kosakata  # noqa: E402

BERKAS_GRAMMAR = FOLDER / "syntaxes" / "indonesia.tmLanguage.json"

NAMA = r"[\p{L}_][\p{L}\p{N}_]*"
# Kata deklarasi diberi warna "storage" seperti 'def'/'class' di bahasa lain.
DEKLARASI = {"buat", "tetap", "fungsi", "kelas", "mewarisi", "pribadi", "statis"}
CAKUPAN = {
    "kunci": "keyword.control.indonesia",
    "operator": "keyword.operator.word.indonesia",
    "nilai": "constant.language.indonesia",
    "tipe": "support.type.indonesia",
}


def _kata(daftar) -> str:
    """Pola yang cocok dengan salah satu kata/frasa, yang terpanjang lebih dulu."""
    urut = sorted(daftar, key=lambda f: (-len(f.split()), -len(f), f))
    return r"\b(?:" + "|".join(r"[ \t]+".join(map(re.escape, f.split())) for f in urut) + r")\b"


def _per_golongan(kamus: dict) -> list:
    golongan = {}
    for kata, nama in kamus.items():
        cakupan = CAKUPAN[nama]
        if kata in DEKLARASI:
            cakupan = "storage.type.indonesia"
        elif kata in ("diri", "super"):
            cakupan = "variable.language.indonesia"
        golongan.setdefault(cakupan, []).append(kata)
    return [{"name": cakupan, "match": _kata(kata)} for cakupan, kata in sorted(golongan.items())]


def grammar() -> dict:
    kosa = kosakata()
    perintah_natural = [
        {
            "begin": rf"^[ \t]*({kata})\b",
            "beginCaptures": {"1": {"name": "keyword.control.indonesia"}},
            "end": "$",
            "patterns": [{"match": _kata(sambungan), "name": "keyword.control.indonesia"}, {"include": "#isi"}],
        }
        for kata, sambungan in KATA_PERINTAH.items()
    ]
    perintah_natural.append({
        # ulangi 3 kali:
        "begin": r"^[ \t]*(ulangi)\b",
        "beginCaptures": {"1": {"name": "keyword.control.indonesia"}},
        "end": "$",
        "patterns": [{"match": r"\bkali\b", "name": "keyword.control.indonesia"}, {"include": "#isi"}],
    })

    def teks(kutip: str, format_: bool) -> dict:
        nama = "double" if kutip == '"' else "single"
        aturan = {
            "name": f"string.quoted.{nama}{'.format' if format_ else ''}.indonesia",
            "begin": (r"\b(f|format)(" + kutip + ")") if format_ else kutip,
            "end": f"({kutip})|$",
            "endCaptures": {"1": {"name": "punctuation.definition.string.end.indonesia"}},
            "patterns": [{"include": "#escape"}] + ([{"include": "#sisipan"}] if format_ else []),
        }
        if format_:
            aturan["beginCaptures"] = {
                "1": {"name": "storage.type.string.indonesia"},
                "2": {"name": "punctuation.definition.string.begin.indonesia"},
            }
        else:
            aturan["beginCaptures"] = {"0": {"name": "punctuation.definition.string.begin.indonesia"}}
        return aturan

    return {
        "$schema": "https://raw.githubusercontent.com/martinring/tmlanguage/master/tmlanguage.json",
        "name": "Bahasa Indonesia",
        "scopeName": "source.indonesia",
        "comment": "Dibuat oleh vscode/bangun.py dari src/kosakata.py. Jangan diubah langsung.",
        "patterns": [{"include": "#perintah-natural"}, {"include": "#isi"}],
        "repository": {
            "isi": {"patterns": [{"include": f"#{n}"} for n in (
                "komentar", "teks", "angka", "definisi", "tanya", "frasa", "kata-kunci", "fungsi-bawaan",
            )]},
            "perintah-natural": {"patterns": perintah_natural},
            "komentar": {"patterns": [
                {"name": "comment.block.indonesia", "begin": '"""', "end": '"""'},
                {"name": "comment.line.number-sign.indonesia", "match": "#.*$"},
            ]},
            "teks": {"patterns": [teks('"', True), teks("'", True), teks('"', False), teks("'", False)]},
            "escape": {"name": "constant.character.escape.indonesia", "match": r"\\."},
            "sisipan": {
                "name": "meta.interpolation.indonesia",
                "begin": r"\{",
                "end": r"\}|$",
                "beginCaptures": {"0": {"name": "punctuation.section.interpolation.begin.indonesia"}},
                "endCaptures": {"0": {"name": "punctuation.section.interpolation.end.indonesia"}},
                "patterns": [{"include": "#isi"}],
            },
            "angka": {"name": "constant.numeric.indonesia", "match": r"\b\d+(?:\.\d+)?\b"},
            "definisi": {"patterns": [
                {"match": rf"\b(fungsi)[ \t]+({NAMA})", "captures": {
                    "1": {"name": "storage.type.function.indonesia"},
                    "2": {"name": "entity.name.function.indonesia"}}},
                {"match": rf"\b(kelas)[ \t]+({NAMA})", "captures": {
                    "1": {"name": "storage.type.class.indonesia"},
                    "2": {"name": "entity.name.type.class.indonesia"}}},
            ]},
            "tanya": {
                # tanya "Siapa namamu?" / tanya angka "Berapa umurmu?"
                "match": r"\b(tanya)(?:[ \t]+(angka))?(?=[ \t]*[\"'])",
                "captures": {"1": {"name": "keyword.control.indonesia"}, "2": {"name": "keyword.control.indonesia"}},
            },
            "frasa": {"patterns": _per_golongan(kosa["frasa"])},
            "kata-kunci": {"patterns": _per_golongan(kosa["kata_kunci"])},
            "fungsi-bawaan": {
                "match": r"\b(" + "|".join(sorted(kosa["fungsi_bawaan"], key=len, reverse=True)) + r")(?=[ \t]*\()",
                "name": "support.function.builtin.indonesia",
            },
        },
    }


def teks_grammar() -> str:
    return json.dumps(grammar(), ensure_ascii=False, indent=2) + "\n"


if __name__ == "__main__":
    BERKAS_GRAMMAR.parent.mkdir(exist_ok=True)
    BERKAS_GRAMMAR.write_text(teks_grammar(), encoding="utf-8")
    print(f"✅ {BERKAS_GRAMMAR.relative_to(FOLDER.parent)} diperbarui")
