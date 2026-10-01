#!/usr/bin/env python3
"""
indonesia.py — CLI entry point untuk bahasa pemrograman Indonesia.

Penggunaan:
    python indonesia.py program.id         # Jalankan file .id
    python indonesia.py repl               # Masuk ke mode interaktif (REPL)
    python indonesia.py -e "tampilkan 42"  # Jalankan kode langsung
    python indonesia.py bantu              # Tampilkan bantuan ini
    python indonesia.py versi              # Tampilkan versi
"""

import sys
import os

if sys.version_info < (3, 11):
    sys.exit(
        "❌ Bahasa Pemrograman Indonesia membutuhkan Python 3.11 atau yang lebih baru "
        f"(yang terpasang: Python {sys.version_info.major}.{sys.version_info.minor})."
    )

# Tambahkan root ke path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.lexer import tokenisasi
from src.parser import parse
from src.interpreter import Interpreter
from src.builtins import _ke_teks
from src.errors import KesalahanIndonesia, KesalahanSintaks
from src.ast_nodes import (
    NodeAngka, NodeTeks, NodeTeksFormat, NodeLogika, NodeKosong, NodeIdentifier,
    NodeWaktuSekarang, NodeAngkaAcak, NodeTanya, NodeOperasiBiner, NodeOperasiUnari,
    NodePanggilFungsi, NodeDaftar, NodeKamus, NodeAksesDaftar, NodeIrisanDaftar, NodeAksesAtribut,
)


VERSI = "0.3.0"

BANNER = f"""
╔════════════════════════════════════════════╗
║  🇮🇩  Bahasa Pemrograman Indonesia v{VERSI}  ║
║  Ketik 'keluar' untuk keluar              ║
╚════════════════════════════════════════════╝
Blok (jika, selama, fungsi, ...) diakhiri dengan baris kosong.
"""

# Di REPL, hanya hasil ekspresi yang ditampilkan ("5 lebih dari 3" → benar),
# bukan hasil perintah seperti "buat x = 5".
_NODE_EKSPRESI = (
    NodeAngka, NodeTeks, NodeTeksFormat, NodeLogika, NodeKosong, NodeIdentifier,
    NodeWaktuSekarang, NodeAngkaAcak, NodeTanya, NodeOperasiBiner, NodeOperasiUnari,
    NodePanggilFungsi, NodeDaftar, NodeKamus, NodeAksesDaftar, NodeIrisanDaftar, NodeAksesAtribut,
)


def _jalankan(kode: str):
    """Jalankan kode sebuah program; keluar dengan pesan yang jelas bila gagal."""
    try:
        tree = parse(tokenisasi(kode), kode)
        Interpreter().jalankan(tree)
    except KesalahanIndonesia as e:
        print(e, file=sys.stderr)
        sys.exit(1)
    except KeyboardInterrupt:
        print("\nProgram dihentikan.", file=sys.stderr)
        sys.exit(130)
    except BrokenPipeError:
        # Keluaran dipotong, mis. dialirkan ke 'head': berhenti tanpa pesan
        os.dup2(os.open(os.devnull, os.O_WRONLY), sys.stdout.fileno())
        sys.exit(1)
    except Exception as e:
        print(f"❌ Kesalahan internal: {e}", file=sys.stderr)
        print("   Ini kemungkinan besar bug pada interpreter. Mohon laporkan di GitHub.", file=sys.stderr)
        sys.exit(1)


def jalankan_berkas(path: str):
    """Baca dan jalankan file .id"""
    if not os.path.exists(path):
        print(f"❌ Berkas tidak ditemukan: '{path}'")
        sys.exit(1)

    with open(path, "r", encoding="utf-8") as f:
        _jalankan(f.read())


def jalankan_ekspresi(kode: str):
    """Jalankan kode langsung dari flag -e"""
    _jalankan(kode)


def _belum_selesai(kode: str) -> bool:
    """Apakah kode di REPL belum lengkap, mis. baru menulis 'jika x > 5:' atau 'buat d = ['?"""
    try:
        parse(tokenisasi(kode), kode)
    except KesalahanSintaks as e:
        return getattr(e, "belum_selesai", False)
    return False


def _baca_perintah() -> str:
    """Baca satu perintah; bila belum lengkap, terus baca sampai baris kosong."""
    kode = input(">>> ")
    if kode.strip() and _belum_selesai(kode):
        while True:
            lanjutan = input("... ")
            if not lanjutan.strip():
                break
            kode += "\n" + lanjutan
    return kode


def mode_interaktif():
    """REPL — Read-Eval-Print Loop."""
    print(BANNER)
    interpreter = Interpreter()

    while True:
        try:
            kode = _baca_perintah()
        except EOFError:
            print("\nSampai jumpa! 👋")
            break
        except KeyboardInterrupt:
            print("\n(dibatalkan)")
            continue

        if not kode.strip():
            continue
        if kode.strip() in ("keluar", "exit", "quit"):
            print("Sampai jumpa! 👋")
            break

        try:
            tree = parse(tokenisasi(kode), kode)
            hasil = interpreter.jalankan(tree)
            if tree.pernyataan and isinstance(tree.pernyataan[-1], _NODE_EKSPRESI) and hasil is not None:
                print(_ke_teks(hasil))  # benar/salah/kosong, bukan True/False/None
        except KesalahanIndonesia as e:
            print(e)
        except KeyboardInterrupt:
            print("\nDihentikan.")
        except Exception as e:
            print(f"❌ Kesalahan internal: {e}")


def main():
    args = sys.argv[1:]

    if not args or args[0] == "repl":
        mode_interaktif()
        return

    if args[0] in ("versi", "--versi", "--version", "-v"):
        print(f"Indonesia v{VERSI}")
        return

    if args[0] in ("bantu", "bantuan", "--bantu", "--bantuan", "--help", "-h"):
        print(__doc__)
        return

    if args[0] in ("-e", "--eval") and len(args) > 1:
        jalankan_ekspresi(args[1])
        return

    jalankan_berkas(args[0])


if __name__ == "__main__":
    main()
