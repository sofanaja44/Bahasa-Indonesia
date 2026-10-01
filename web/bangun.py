#!/usr/bin/env python3
"""
bangun.py — Membangun editor web Bahasa Indonesia ke folder web/situs/.

    python web/bangun.py              # bangun situs
    python web/bangun.py --sajikan    # bangun, lalu buka di http://localhost:8000

Isi situs:
    index.html, gaya.css, *.js     dari folder web/
    mesin.wasm                     mesin Bahasa Indonesia (Go, mesin/cmd/wasm) dalam WebAssembly
    wasm_exec.js                   penghubung WebAssembly milik Go, dari instalasi Go
    kosakata.json                  kata kunci untuk pewarnaan kode (dari src/kosakata.py)
    contoh.json                    program di folder contoh/

Butuh Python dan Go 1.22 atau yang lebih baru (https://go.dev/dl/); tidak perlu Node.js.
"""

from __future__ import annotations

import argparse
import hashlib
import http.server
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from functools import partial
from pathlib import Path

WEB = Path(__file__).resolve().parent
AKAR = WEB.parent
SITUS = WEB / "situs"
MESIN = AKAR / "mesin"

sys.path.insert(0, str(AKAR))

from src.kosakata import kosakata  # noqa: E402

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

def daftar_contoh() -> list:
    urutan = list(JUDUL_CONTOH)
    berkas = sorted((AKAR / "contoh").glob("*.id"),
                    key=lambda p: (urutan.index(p.stem) if p.stem in urutan else len(urutan), p.stem))
    return [
        {"id": p.stem, "judul": JUDUL_CONTOH.get(p.stem, p.stem.replace("_", " ").title()),
         "kode": p.read_text(encoding="utf-8").replace("\r\n", "\n")}
        for p in berkas
    ]


def versi_bahasa() -> str:
    cocok = re.search(r'^const Versi = "([^"]+)"', (MESIN / "api.go").read_text(encoding="utf-8"), re.M)
    return cocok.group(1) if cocok else "?"


def bangun_mesin() -> tuple[bytes, bytes]:
    """Kompilasi mesin Go ke WebAssembly; hasilnya mesin.wasm dan wasm_exec.js yang sepasang."""
    go = shutil.which("go")
    if not go:
        sys.exit("❌ Go tidak ditemukan. Pasang Go 1.22 atau yang lebih baru dari https://go.dev/dl/, lalu coba lagi.")
    with tempfile.TemporaryDirectory() as folder:
        keluaran = Path(folder) / "mesin.wasm"
        subprocess.run(
            [go, "build", "-trimpath", "-ldflags=-s -w", "-o", str(keluaran), "./cmd/wasm"],
            cwd=MESIN, env={**os.environ, "GOOS": "js", "GOARCH": "wasm"}, check=True,
        )
        wasm = keluaran.read_bytes()
    goroot = Path(subprocess.run([go, "env", "GOROOT"], capture_output=True, text=True, check=True).stdout.strip())
    for jalur in ("lib/wasm/wasm_exec.js", "misc/wasm/wasm_exec.js"):  # Go 1.24+ / sebelumnya
        if (goroot / jalur).exists():
            return wasm, (goroot / jalur).read_bytes()
    sys.exit(f"❌ wasm_exec.js tidak ditemukan di {goroot}.")


def bangun() -> None:
    if SITUS.exists():
        shutil.rmtree(SITUS)
    SITUS.mkdir()

    wasm, wasm_exec = bangun_mesin()
    # Versi mesin.wasm dihitung sendiri: bila mesinnya tidak berubah, pembaruan situs tidak
    # membuat pengguna mengunduh ulang berkas terbesar ini.
    versi_mesin = hashlib.sha256(wasm).hexdigest()[:12]
    (SITUS / "mesin.wasm").write_bytes(wasm)

    hasil = {
        "wasm_exec.js": wasm_exec,
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
    sidik.update(versi_mesin.encode())
    versi = sidik.hexdigest()[:12]

    for nama, isi in hasil.items():
        if nama.endswith((".html", ".js")) and nama != "wasm_exec.js":
            isi = (isi.decode("utf-8")
                   .replace("__VERSI__", versi)
                   .replace("__VERSI_BAHASA__", versi_bahasa())
                   .replace("__VERSI_MESIN__", versi_mesin)).encode("utf-8")
        (SITUS / nama).write_bytes(isi)

    pakai_versi = {"gaya.css", "aplikasi.js", "sorotan.js", "pekerja.js",
                   "wasm_exec.js", "kosakata.json", "contoh.json"}
    berkas_cache = ["./"] + [f"{n}?v={versi}" if n in pakai_versi else n
                             for n in sorted(hasil) if n != "index.html"]
    sw = ((WEB / "sw.js").read_text(encoding="utf-8")
          .replace("__VERSI__", versi)
          .replace("__VERSI_MESIN__", versi_mesin)
          .replace('["__BERKAS__"]', json.dumps(berkas_cache)))
    (SITUS / "sw.js").write_text(sw, encoding="utf-8")
    ukuran = len(wasm) / 1e6
    print(f"✅ Situs selesai dibangun di {SITUS.relative_to(AKAR)} (versi {versi}, mesin {versi_mesin}, {ukuran:.1f} MB)")


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
