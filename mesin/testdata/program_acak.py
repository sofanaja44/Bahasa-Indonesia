#!/usr/bin/env python3
"""
program_acak.py — Membuat banyak program acak untuk membandingkan mesin Go dengan interpreter Python.

Setiap program berisi beberapa baris 'tampilkan <ekspresi acak>' yang dibungkus coba/tangkap,
sehingga kesalahan pun ikut dibandingkan (jenis dan pesannya). Hasilnya ditulis dalam format
korpus.json, lalu dijalankan oleh tes Go:

    python mesin/testdata/program_acak.py 3000 /tmp/acak.json [benih] [ekspresi|kontrol]
    cd mesin && KORPUS=/tmp/acak.json go test -run TestKorpusPembanding .
"""

import json
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from buat_korpus import MASUKAN, jalankan  # noqa: E402

TEKS = ['"halo"', '"Halo Dunia"', '""', '" a b "', '"é ü"', '"123"', '"3,5"', '"abc"', '"x,y,z"', "'kutip'", '"A"']
ANGKA = ["0", "1", "2", "3", "7", "10", "-1", "-5", "100", "2 ** 64", "-(2 ** 70)", "9223372036854775807"]
DESIMAL = ["0.5", "1.5", "-2.5", "0.1", "3.0", "2.675", "0.001", "0.0", "-0.0", "123.456", "1 / 3", "10.0 ** 20"]
LAIN = ["benar", "salah", "kosong", "[]", "[1, 2, 3]", '["b", "a"]', "[1.5, -2]", "{}", '{"a": 1, "b": 2}',
        "{1: 2}", "[[1], [2, 3]]", "d", "k", "t", "f", "K", "obj"]
OP = ["+", "-", "*", "/", "%", "**", "==", "!=", "<", ">", "<=", ">=", "dan", "atau", "ada dalam",
      "tidak ada dalam", "ditambah", "dikurangi", "dikali", "dibagi", "sisa bagi", "lebih dari", "kurang dari",
      "paling sedikit", "paling banyak", "sama dengan", "tidak sama dengan"]
BAWAAN = ["panjang", "jenis", "ubah_teks", "ubah_angka", "ubah_desimal", "ubah_logika", "mutlak", "maksimum",
          "minimum", "jumlah", "diurutkan", "dibalik", "rentang", "Kesalahan"]
METODE_TEKS = ["panjang()", "huruf_besar()", "huruf_kecil()", "huruf_awal_besar()", "potong_spasi()", "belah()",
               'belah(",")', "balik()", "berupa_angka()", 'berisi("a")', 'cari("l")', 'ganti("a", "o")',
               'diawali("h")', 'diakhiri("o")', "belah(1)", 'ganti("", "-")']
METODE_DAFTAR = ["panjang()", "salin()", 'gabung(", ")', "gabung()", "cari(2)", "urutkan()", "balik()",
                 "tambahkan(9)", "hapusPosisi(0)", "hapusPosisi(-1)", "sisipkan(1, 0)", "hapus(1)", "kosongkan()"]
METODE_KAMUS = ["kunci()", "nilai()", "pasang()", 'adaKunci("a")', 'dapatkan("a")', 'dapatkan("z", 0)',
                'hapusKunci("a")']
MATEMATIKA = ["akar", "mutlak", "bulatkan", "bulatkan_bawah", "bulatkan_atas", "sinus", "kosinus", "tangen",
              "logaritma", "ln", "faktorial"]

PEMBUKA = """impor matematika
impor acak
acak.atur_benih({benih})
buat d adalah [3, 1, 2]
buat k adalah {{"a": 1, "b": 2}}
buat t adalah "Halo"
fungsi f(x, y = 2):
    kembalikan x * y
kelas K:
    buat n adalah 1
    fungsi gandakan():
        kembalikan diri.n * 2
buat obj adalah K()
"""


def nilai(r: random.Random) -> str:
    return r.choice(r.choice([TEKS, ANGKA, DESIMAL, LAIN]))


SISIPAN = ["d", "k", "t", "obj.n", "f(2)", "1 / 3", "2 ** 70", "benar", "kosong", "d[0]", "-2.5", "k['a']",
           "t.huruf_besar()", "x", "1 +", "[1, 'a']"]


def ekspresi(r: random.Random, kedalaman: int = 0) -> str:
    if kedalaman > 2 or r.random() < 0.3:
        return nilai(r)
    pilihan = r.random()
    if pilihan < 0.35:
        return f"({ekspresi(r, kedalaman + 1)}) {r.choice(OP)} ({ekspresi(r, kedalaman + 1)})"
    if pilihan < 0.42:
        return f"{r.choice(['-', 'bukan '])}({ekspresi(r, kedalaman + 1)})"
    if pilihan < 0.55:
        args = ", ".join(ekspresi(r, kedalaman + 1) for _ in range(r.choice([0, 1, 1, 1, 2, 3])))
        return f"{r.choice(BAWAAN)}({args})"
    if pilihan < 0.63:
        return f"({r.choice(TEKS)}).{r.choice(METODE_TEKS)}"
    if pilihan < 0.70:
        return f"({r.choice(['[3, 1, 2]', '[1, 2, 3]', '[]', 'd', '[2, 1, 2]'])}).{r.choice(METODE_DAFTAR)}"
    if pilihan < 0.75:
        return f"({r.choice(['{}', 'k', '{\"a\": 5}'])}).{r.choice(METODE_KAMUS)}"
    if pilihan < 0.83:
        args = ", ".join(ekspresi(r, kedalaman + 1) for _ in range(r.choice([1, 1, 2])))
        return f"matematika.{r.choice(MATEMATIKA)}({args})"
    if pilihan < 0.88:
        return f"({ekspresi(r, kedalaman + 1)})[{ekspresi(r, kedalaman + 1)}]"
    if pilihan < 0.92:
        return f"({ekspresi(r, kedalaman + 1)})[{r.choice(['1', '-1', '', '0'])}:{r.choice(['2', '-1', '', '10'])}]"
    if pilihan < 0.93:
        return f'format"nilai {{{r.choice(SISIPAN)}}} dan {{{r.choice(SISIPAN)}}}!"'
    if pilihan < 0.96:
        return f"f({ekspresi(r, kedalaman + 1)})"
    return f"acak.bilangan({r.choice(ANGKA)}, {r.choice(ANGKA)})"


def program(r: random.Random) -> str:
    baris = [PEMBUKA.format(benih=r.randint(0, 10**6))]
    for _ in range(r.randint(3, 10)):
        baris.append(f"coba:\n    tampilkan {ekspresi(r)}\ntangkap sebagai e:\n    tampilkan e.jenis, e\n")
    if r.random() < 0.3:
        baris.append(ekspresi(r) + "\n")  # nilai terakhir seperti di REPL
    return "".join(baris)


# ---- Program acak dengan alur kontrol bersarang (menguji kompiler: berhenti, lewati, kembalikan,
# akhirnya, lingkup variabel) ----

class Kontrol:
    def __init__(self, r: random.Random):
        self.r = r
        self.nomor = 0
        self.fungsi = []  # (nama, jumlah parameter)

    def label(self) -> str:
        self.nomor += 1
        return f'"L{self.nomor}"'

    def nilai(self, nama: list) -> str:
        r = self.r
        pilihan = list(nama) + ["1", "2", "3", '"a"', "benar", "0"]
        a = r.choice(pilihan)
        if r.random() < 0.3:
            return f"{a} {r.choice(['+', '-', '*', '/', '%', '==', '<', 'dan', 'atau'])} {r.choice(pilihan)}"
        return a

    def kondisi(self, nama: list) -> str:
        return self.r.choice(["benar", "salah", f"{self.nilai(nama)}", f"{self.nilai(nama)} > 1"])

    def blok(self, kedalaman: int, loop: bool, fungsi: bool, nama: list, indent: str) -> list:
        baris = []
        for _ in range(self.r.randint(1, 4)):
            baris.extend(self.pernyataan(kedalaman, loop, fungsi, nama, indent))
        return baris

    def pernyataan(self, kedalaman: int, loop: bool, fungsi: bool, nama: list, indent: str) -> list:
        r, i = self.r, indent
        dalam = i + "    "
        pilihan = ["tampil"] * 6 + ["buat"] * 3 + ["ubah"]
        if r.random() < 0.15:
            pilihan += ["lempar", "galat"]
        if kedalaman < 3:
            pilihan += ["jika", "untuk", "setiap", "kali", "selama", "coba", "coba", "ulangi"]
        if loop:
            pilihan += ["berhenti", "lewati"]
        if fungsi:
            pilihan += ["kembalikan"]
        if self.fungsi:
            pilihan += ["panggil"]
        jenis = r.choice(pilihan)
        if jenis == "tampil":
            return [f"{i}tampilkan {self.label()}, {self.nilai(nama)}"]
        if jenis == "buat":
            v = r.choice(["v1", "v2", "v3"])
            nama.append(v)
            return [f"{i}buat {v} adalah {self.nilai(nama)}"]
        if jenis == "ubah":
            return [f"{i}{r.choice(['v1', 'v2', 'v3'])} adalah {self.nilai(nama)}"]
        if jenis == "lempar":
            return [f"{i}lempar {self.label()}"]
        if jenis == "galat":
            return [f"{i}tampilkan {r.choice(['1 / 0', 'x_tidak_ada', '[1][5]', '1 + kosong'])}"]
        if jenis == "berhenti":
            return [f"{i}jika {self.kondisi(nama)}:", f"{dalam}berhenti"]
        if jenis == "lewati":
            return [f"{i}jika {self.kondisi(nama)}:", f"{dalam}lewati"]
        if jenis == "kembalikan":
            return [f"{i}kembalikan {self.nilai(nama)}"]
        if jenis == "panggil":
            nm, n = r.choice(self.fungsi)
            args = ", ".join(self.nilai(nama) for _ in range(n))
            return [f"{i}tampilkan {self.label()}, {nm}({args})"]
        k = kedalaman + 1
        if jenis == "jika":
            baris = [f"{i}jika {self.kondisi(nama)}:"] + self.blok(k, loop, fungsi, list(nama), dalam)
            if r.random() < 0.4:
                baris += [f"{i}atau jika {self.kondisi(nama)}:"] + self.blok(k, loop, fungsi, list(nama), dalam)
            if r.random() < 0.5:
                baris += [f"{i}selainnya:"] + self.blok(k, loop, fungsi, list(nama), dalam)
            return baris
        if jenis == "untuk":
            v = f"i{k}"
            return [f"{i}untuk {v} dari 1 sampai {r.randint(0, 3)}:"] + self.blok(k, True, fungsi, nama + [v], dalam)
        if jenis == "setiap":
            v = f"x{k}"
            return [f"{i}untuk setiap {v} dalam [1, \"b\", 3]:"] + self.blok(k, True, fungsi, nama + [v], dalam)
        if jenis == "kali":
            return [f"{i}ulangi {r.randint(0, 3)} kali:"] + self.blok(k, True, fungsi, list(nama), dalam)
        if jenis == "selama":
            c = f"c{k}"
            return [f"{i}buat {c} adalah 0", f"{i}selama {c} < 3:", f"{dalam}tambahkan 1 ke {c}"] + \
                self.blok(k, True, fungsi, nama + [c], dalam)
        if jenis == "ulangi":
            c = f"u{k}"
            return [f"{i}buat {c} adalah 0", f"{i}ulangi:", f"{dalam}tambahkan 1 ke {c}"] + \
                self.blok(k, True, fungsi, nama + [c], dalam) + [f"{i}sampai {c} paling sedikit 2"]
        # coba
        baris = [f"{i}coba:"] + self.blok(k, loop, fungsi, list(nama), dalam)
        jumlah_tangkap = r.choice([0, 1, 1, 2])
        for _ in range(jumlah_tangkap):
            jenis_k = r.choice(["", "KesalahanBagiNol ", "KesalahanNama ", "KesalahanNilai ", "Kesalahan "])
            var = r.choice(["", "sebagai e"])
            kepala = f"{i}tangkap {jenis_k}{var}".rstrip() + ":"
            isi = self.blok(k, loop, fungsi, list(nama) + (["e"] if var else []), dalam)
            baris += [kepala] + isi
        if jumlah_tangkap == 0 or r.random() < 0.5:
            baris += [f"{i}akhirnya:"] + self.blok(k, loop, fungsi, list(nama), dalam)
        return baris

    def program(self) -> str:
        r = self.r
        baris = []
        for f in range(r.randint(0, 3)):
            n = r.randint(0, 2)
            params = [f"p{j}" for j in range(n)]
            baris.append(f"fungsi f{f}({', '.join(params)}):")
            baris += self.blok(1, False, True, list(params), "    ")
            self.fungsi.append((f"f{f}", n))
        for _ in range(r.randint(1, 3)):
            baris += ["coba:"] + self.blok(1, False, False, [], "    ") + ["tangkap sebagai e:", "    tampilkan \"!\", e.jenis, e"]
        return "\n".join(baris) + "\n"


def main():
    jumlah = int(sys.argv[1]) if len(sys.argv) > 1 else 1000
    keluaran = Path(sys.argv[2] if len(sys.argv) > 2 else "/tmp/program_acak.json")
    benih = int(sys.argv[3]) if len(sys.argv) > 3 else 1
    mode = sys.argv[4] if len(sys.argv) > 4 else "ekspresi"  # "ekspresi" atau "kontrol"
    r = random.Random(benih)
    korpus = []
    for i in range(jumlah):
        kode = Kontrol(r).program() if mode == "kontrol" else program(r)
        hasil = jalankan(kode, MASUKAN)
        if hasil is None or hasil.get("internal"):
            continue
        korpus.append({"nama": f"acak/{benih}-{i}", "kode": kode, "masukan": None, **hasil})
    keluaran.write_text(json.dumps(korpus, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"{len(korpus)} program ditulis ke {keluaran}")


if __name__ == "__main__":
    main()
