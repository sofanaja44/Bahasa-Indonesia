#!/usr/bin/env python3
"""
indonesia.py — CLI entry point untuk bahasa pemrograman Indonesia.

Penggunaan:
    python indonesia.py                    # Masuk ke mode REPL
    python indonesia.py program.id         # Jalankan file .id
    python indonesia.py -e "tampilkan 42"  # Jalankan kode langsung
"""

import sys
import os

# Tambahkan root ke path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.lexer import tokenisasi
from src.parser import parse
from src.interpreter import Interpreter
from src.errors import KesalahanIndonesia


VERSI = "0.3.0"

BANNER = f"""
╔════════════════════════════════════════════╗
║  🇮🇩  Bahasa Pemrograman Indonesia v{VERSI}  ║
║  Ketik 'keluar' untuk keluar              ║
╚════════════════════════════════════════════╝
"""


def jalankan_berkas(path: str):
    """Baca dan jalankan file .id"""
    if not os.path.exists(path):
        print(f"❌ Berkas tidak ditemukan: '{path}'")
        sys.exit(1)

    with open(path, "r", encoding="utf-8") as f:
        kode = f.read()

    try:
        tokens = tokenisasi(kode)
        tree = parse(tokens, kode)
        interpreter = Interpreter()
        interpreter.jalankan(tree)
    except KesalahanIndonesia as e:
        print(e, file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"❌ Kesalahan internal: {e}", file=sys.stderr)
        sys.exit(1)


def jalankan_ekspresi(kode: str):
    """Jalankan kode langsung dari flag -e"""
    try:
        tokens = tokenisasi(kode)
        tree = parse(tokens, kode)
        interpreter = Interpreter()
        interpreter.jalankan(tree)
    except KesalahanIndonesia as e:
        print(e, file=sys.stderr)
        sys.exit(1)


def mode_interaktif():
    """REPL — Read-Eval-Print Loop."""
    print(BANNER)
    interpreter = Interpreter()

    while True:
        try:
            baris = input(">>> ")
        except (EOFError, KeyboardInterrupt):
            print("\nSampai jumpa! 👋")
            break

        baris = baris.strip()
        if not baris:
            continue
        if baris in ("keluar", "exit", "quit"):
            print("Sampai jumpa! 👋")
            break

        try:
            tokens = tokenisasi(baris)
            tree = parse(tokens, baris)
            hasil = interpreter.jalankan(tree)
            if hasil is not None:
                print(hasil)
        except KesalahanIndonesia as e:
            print(e)
        except Exception as e:
            print(f"❌ Kesalahan: {e}")


def main():
    args = sys.argv[1:]

    if not args:
        mode_interaktif()
        return

    if args[0] in ("--versi", "--version", "-v"):
        print(f"Indonesia v{VERSI}")
        return

    if args[0] in ("--bantuan", "--help", "-h"):
        print(__doc__)
        return

    if args[0] in ("-e", "--eval") and len(args) > 1:
        jalankan_ekspresi(args[1])
        return

    jalankan_berkas(args[0])


if __name__ == "__main__":
    main()
