#!/usr/bin/env python3
"""
bangun.py — Membangun editor web Bahasa Indonesia ke folder web/situs/.

    python web/bangun.py              # bangun situs
    python web/bangun.py --sajikan    # bangun, lalu buka di http://localhost:8000

Isi situs:
    index.html, gaya.css, *.js     dari folder web/
    interpreter.zip                src/*.py + web/jembatan.py, dimuat ke Pyodide
    kosakata.json                  kata kunci untuk pewarnaan kode (dari src/token_types.py)
    contoh.json                    program di folder contoh/
    pyodide/                       Python dalam WebAssembly, diunduh dari registri npm

Hanya butuh Python; tidak perlu Node.js.
"""

from __future__ import annotations

import argparse
import base64
import hashlib
import http.server
import io
import json
import re
import shutil
import sys
import tarfile
import urllib.request
import zipfile
from functools import partial
from pathlib import Path

WEB = Path(__file__).resolve().parent
AKAR = WEB.parent
SITUS = WEB / "situs"
CACHE = WEB / ".cache"

sys.path.insert(0, str(AKAR))

from src.builtins import daftar_fungsi_bawaan  # noqa: E402
from src.token_types import FRASA_KATA_KUNCI, KATA_KUNCI  # noqa: E402

# Versi Pyodide dan sidik jarinya (dist.integrity di registri npm).
# Untuk memperbarui: npm view pyodide@VERSI dist.integrity
PYODIDE_VERSI = "314.0.7"
PYODIDE_INTEGRITAS = "sha512-0YvXxEhfEdpLfb/XkM2BFAeMROq0iMUX2bzzH9pOttyMcWkwq+HbE5uyuGD82LN7y2q+SNvi/6V5JEsOlD2R1A=="
BERKAS_PYODIDE = ["pyodide.mjs", "pyodide.asm.mjs", "pyodide.asm.wasm", "python_stdlib.zip", "pyodide-lock.json"]

# Berkas statis yang disalin apa adanya (selain sw.js yang diisi daftar berkas).
BERKAS_STATIS = [
    "index.html", "gaya.css", "aplikasi.js", "sorotan.js", "pekerja.js",
    "manifest.webmanifest", "ikon.svg", "ikon-192.png", "ikon-512.png",
]

# Urutan dan judul contoh di menu; contoh lain menyusul sesuai abjad.
JUDUL_CONTOH = {
    "halo_dunia": "Halo Dunia",
    "tebak_angka": "Permainan Tebak Angka",
    "jam_digital": "Cerita Jam Digital",
    "cerita": "Cerita Petualangan",
    "demo_lengkap": "Tur Lengkap Bahasa",
}

# Kelas warna untuk pewarnaan kode, berdasarkan jenis token.
_KELAS_TOKEN = {
    "nilai": {"BENAR", "SALAH", "KOSONG", "WAKTU_SEKARANG", "ANGKA_ACAK", "DIRI", "SUPER"},
    "tipe": {"BILANGAN", "TEKS_TIPE", "LOGIKA_TIPE", "DESIMAL_TIPE"},
    "operator": {
        "DAN", "ATAU", "BUKAN", "ADA", "TIDAK_ADA", "DITAMBAH", "DIKURANG", "DIKALI", "DIBAGI",
        "PANGKAT_KK", "SISA_BAGI", "HABIS_DIBAGI", "TIDAK_HABIS_DIBAGI", "SAMA_DENGAN_OP", "TIDAK_SAMA_OP",
        "LEBIH_DARI", "KURANG_DARI", "TIDAK_KURANG_DARI", "TIDAK_LEBIH_DARI",
    },
}

# Kata kerja natural yang tidak dicadangkan; diwarnai hanya di awal perintah,
# bersama kata sambungannya (lihat sorotan.js).
KATA_PERINTAH = {
    "ubah": ["menjadi"],
    "tambahkan": ["ke"],
    "kurangi": ["dengan", "dari"],
    "kalikan": ["dengan"],
    "bagi": ["dengan"],
    "tunggu": ["detik", "menit"],
}


def _kelas(tipe) -> str:
    for kelas, nama in _KELAS_TOKEN.items():
        if tipe.name in nama:
            return kelas
    return "kunci"


def kosakata() -> dict:
    return {
        "kata_kunci": {kata: _kelas(tipe) for kata, tipe in sorted(KATA_KUNCI.items())},
        "frasa": {" ".join(frasa): _kelas(tipe) for frasa, tipe in sorted(FRASA_KATA_KUNCI.items())},
        "kata_perintah": KATA_PERINTAH,
        "fungsi_bawaan": sorted(daftar_fungsi_bawaan()),
    }


def daftar_contoh() -> list:
    urutan = list(JUDUL_CONTOH)
    berkas = sorted((AKAR / "contoh").glob("*.id"),
                    key=lambda p: (urutan.index(p.stem) if p.stem in urutan else len(urutan), p.stem))
    return [
        {"id": p.stem, "judul": JUDUL_CONTOH.get(p.stem, p.stem.replace("_", " ").title()),
         "kode": p.read_text(encoding="utf-8").replace("\r\n", "\n")}
        for p in berkas
    ]


def zip_interpreter() -> bytes:
    """src/*.py dan jembatan.py dalam satu zip; isinya sama → zip-nya sama (stempel waktu tetap)."""
    berkas = [(f"src/{p.name}", p) for p in sorted((AKAR / "src").glob("*.py"))]
    berkas.append(("jembatan.py", WEB / "jembatan.py"))
    keluaran = io.BytesIO()
    with zipfile.ZipFile(keluaran, "w", zipfile.ZIP_DEFLATED) as z:
        for nama, path in berkas:
            info = zipfile.ZipInfo(nama, date_time=(2026, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            z.writestr(info, path.read_bytes())
    return keluaran.getvalue()


def versi_bahasa() -> str:
    cocok = re.search(r'^VERSI = "([^"]+)"', (AKAR / "indonesia.py").read_text(encoding="utf-8"), re.M)
    return cocok.group(1) if cocok else "?"


def ambil_pyodide(tujuan: Path) -> None:
    """Unduh paket Pyodide dari registri npm (sekali, lalu disimpan di web/.cache/) dan periksa sidik jarinya."""
    arsip = CACHE / f"pyodide-{PYODIDE_VERSI}.tgz"
    if not arsip.exists():
        url = f"https://registry.npmjs.org/pyodide/-/pyodide-{PYODIDE_VERSI}.tgz"
        print(f"Mengunduh Pyodide {PYODIDE_VERSI} ...")
        with urllib.request.urlopen(url, timeout=120) as respons:
            data = respons.read()
        CACHE.mkdir(exist_ok=True)
        sementara = arsip.with_suffix(".unduhan")
        sementara.write_bytes(data)
        sementara.replace(arsip)
    data = arsip.read_bytes()
    algoritma, harapan = PYODIDE_INTEGRITAS.split("-", 1)
    if base64.b64encode(hashlib.new(algoritma, data).digest()).decode() != harapan:
        arsip.unlink()
        sys.exit(f"❌ Sidik jarinya tidak cocok: {arsip.name} rusak atau bukan Pyodide {PYODIDE_VERSI}. Coba lagi.")
    tujuan.mkdir(parents=True)
    with tarfile.open(fileobj=io.BytesIO(data)) as tar:
        for nama in BERKAS_PYODIDE:
            (tujuan / nama).write_bytes(tar.extractfile(f"package/{nama}").read())


def bangun() -> None:
    if SITUS.exists():
        shutil.rmtree(SITUS)
    SITUS.mkdir()

    hasil = {
        "interpreter.zip": zip_interpreter(),
        "kosakata.json": json.dumps(kosakata(), ensure_ascii=False, separators=(",", ":")).encode(),
        "contoh.json": json.dumps(daftar_contoh(), ensure_ascii=False, separators=(",", ":")).encode(),
    }
    for nama in BERKAS_STATIS:
        hasil[nama] = (WEB / nama).read_bytes()

    # Satu versi untuk semua berkas aplikasi: dipakai sebagai ?v=... dan nama cache service worker,
    # sehingga pembaruan situs selalu berganti serentak.
    sidik = hashlib.sha256()
    for nama in sorted(hasil):
        sidik.update(nama.encode() + b"\0" + hasil[nama] + b"\0")
    versi = sidik.hexdigest()[:12]

    for nama, isi in hasil.items():
        if nama.endswith((".html", ".js")):
            isi = (isi.decode("utf-8")
                   .replace("__VERSI__", versi)
                   .replace("__VERSI_BAHASA__", versi_bahasa())
                   .replace("__VERSI_PYODIDE__", PYODIDE_VERSI)).encode("utf-8")
        (SITUS / nama).write_bytes(isi)

    pakai_versi = {"gaya.css", "aplikasi.js", "sorotan.js", "pekerja.js",
                   "interpreter.zip", "kosakata.json", "contoh.json"}
    berkas_cache = ["./"] + [f"{n}?v={versi}" if n in pakai_versi else n
                             for n in sorted(hasil) if n != "index.html"]
    sw = ((WEB / "sw.js").read_text(encoding="utf-8")
          .replace("__VERSI__", versi)
          .replace("__VERSI_PYODIDE__", PYODIDE_VERSI)
          .replace('["__BERKAS__"]', json.dumps(berkas_cache)))
    (SITUS / "sw.js").write_text(sw, encoding="utf-8")

    ambil_pyodide(SITUS / "pyodide")
    print(f"✅ Situs selesai dibangun di {SITUS.relative_to(AKAR)} (versi {versi}, Pyodide {PYODIDE_VERSI})")


class _Penyaji(http.server.SimpleHTTPRequestHandler):
    extensions_map = {
        **http.server.SimpleHTTPRequestHandler.extensions_map,
        ".js": "text/javascript", ".mjs": "text/javascript", ".wasm": "application/wasm",
        ".json": "application/json", ".webmanifest": "application/manifest+json",
    }


def sajikan(port: int) -> None:
    penyaji = partial(_Penyaji, directory=str(SITUS))
    with http.server.ThreadingHTTPServer(("localhost", port), penyaji) as server:
        print(f"Buka http://localhost:{port} di browser. Tekan Ctrl+C untuk berhenti.")
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            pass


if __name__ == "__main__":
    pengurai = argparse.ArgumentParser(description="Bangun editor web Bahasa Indonesia.")
    pengurai.add_argument("--sajikan", action="store_true", help="sajikan situs di localhost setelah dibangun")
    pengurai.add_argument("--port", type=int, default=8000)
    argumen = pengurai.parse_args()
    bangun()
    if argumen.sajikan:
        sajikan(argumen.port)
