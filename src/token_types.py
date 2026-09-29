"""
token_types.py — Definisi tipe token dan kata kunci untuk bahasa pemrograman Indonesia.
"""

from enum import Enum, auto


class TokenType(Enum):
    """Semua tipe token yang dikenali oleh lexer."""

    # --- Literal ---
    ANGKA = auto()           # 42
    DESIMAL = auto()         # 3.14
    TEKS = auto()            # "halo"
    TEKS_FORMAT = auto()     # f"halo {nama}"

    # --- Identifier ---
    IDENTIFIER = auto()      # nama_variabel

    # --- Kata kunci deklarasi ---
    BUAT = auto()            # buat (deklarasi variabel)
    TETAP = auto()           # tetap (konstanta)
    ADALAH = auto()          # adalah (pengisian nilai; di dalam kondisi berarti ==)

    # --- Tipe data eksplisit ---
    BILANGAN = auto()        # bilangan
    DESIMAL_TIPE = auto()    # desimal (tipe data)
    TEKS_TIPE = auto()       # teks (tipe data)
    LOGIKA_TIPE = auto()     # logika (tipe data)

    # --- Nilai literal kata kunci ---
    BENAR = auto()           # benar (True)
    SALAH = auto()           # salah (False)
    KOSONG = auto()          # kosong (None)

    # --- Kondisi ---
    JIKA = auto()            # jika / kalau (if)
    ATAU_JIKA = auto()       # atau jika / atau kalau (else if)
    SELAINNYA = auto()       # selainnya (else)
    PILIH = auto()           # pilih (switch)
    KETIKA = auto()          # ketika (case)
    BAWAAN = auto()          # bawaan (default)
    MAKA = auto()            # maka (then) — pembuka blok kondisi

    # --- Perulangan ---
    SELAMA = auto()          # selama (while)
    UNTUK = auto()           # untuk (for)
    UNTUK_SETIAP = auto()    # untuk setiap (for each)
    DARI = auto()            # dari (from, in for range)
    SAMPAI = auto()          # sampai (to, in for range)
    LANGKAH = auto()         # langkah (step)
    DALAM = auto()           # dalam (in)
    ULANGI = auto()          # ulangi (do/repeat)
    BERHENTI = auto()        # berhenti (break)
    LEWATI = auto()          # lewati (continue)
    LAKUKAN = auto()         # lakukan (do) — pembuka blok perulangan

    # --- Fungsi ---
    FUNGSI = auto()          # fungsi (function)
    KEMBALIKAN = auto()      # kembalikan (return)

    # --- OOP ---
    KELAS = auto()           # kelas (class)
    MEWARISI = auto()        # mewarisi (extends)
    DIRI = auto()            # diri (self/this)
    SUPER = auto()           # super
    PRIBADI = auto()         # pribadi (private)
    STATIS = auto()          # statis (static)

    # --- Modul ---
    IMPOR = auto()           # impor (import)
    SEBAGAI = auto()         # sebagai (as)

    # --- Error handling ---
    COBA = auto()            # coba (try)
    TANGKAP = auto()         # tangkap (catch)
    AKHIRNYA = auto()        # akhirnya (finally)
    LEMPAR = auto()          # lempar (throw)

    # --- I/O (sebagai kata kunci statement) ---
    TAMPILKAN = auto()       # tampilkan / cetak / tulis (print)
    MASUKAN = auto()         # masukan (input)
    MASUKAN_ANGKA = auto()   # masukan_angka
    MASUKAN_DESIMAL = auto() # masukan_desimal

    # --- Operasi logika ---
    DAN = auto()             # dan (and)
    ATAU = auto()            # atau (or)
    BUKAN = auto()           # bukan / tidak (not); "x bukan y" berarti !=

    # --- Operator "ada dalam" ---
    ADA = auto()             # ada (exists, bagian dari "ada dalam")
    TIDAK_ADA = auto()       # tidak ada (bagian dari "tidak ada dalam")

    # --- Operator teks Indonesia (alternatif simbol) ---
    SAMA_DENGAN_OP = auto()   # sama dengan (==)
    TIDAK_SAMA_OP = auto()    # tidak sama (dengan) (!=)
    LEBIH_DARI = auto()       # lebih dari / lebih besar dari (>)
    KURANG_DARI = auto()      # kurang dari / lebih kecil dari (<)
    TIDAK_KURANG_DARI = auto() # tidak kurang dari / paling sedikit (>=)
    TIDAK_LEBIH_DARI = auto()  # tidak lebih dari / paling banyak (<=)
    SISA_BAGI = auto()        # sisa bagi (%)
    HABIS_DIBAGI = auto()     # habis dibagi (x % y == 0)
    TIDAK_HABIS_DIBAGI = auto() # tidak habis dibagi (x % y != 0)
    PANGKAT_KK = auto()       # pangkat / dipangkatkan (**) — sebagai kata kunci infix
    DITAMBAH = auto()         # ditambah (+)
    DIKURANG = auto()         # dikurang / dikurangi (-)
    DIKALI = auto()           # dikali / dikalikan (*)
    DIBAGI = auto()           # dibagi (/)

    # --- Operator aritmatika ---
    TAMBAH = auto()          # +
    KURANG = auto()          # -
    KALI = auto()            # *
    BAGI = auto()            # /
    MODULO = auto()          # %
    PANGKAT = auto()         # **

    # --- Operator penugasan ---
    SAMA_DENGAN = auto()     # =
    TAMBAH_SAMA = auto()     # +=
    KURANG_SAMA = auto()     # -=
    KALI_SAMA = auto()       # *=
    BAGI_SAMA = auto()       # /=
    MODULO_SAMA = auto()     # %=

    # --- Operator perbandingan ---
    SAMA = auto()            # ==
    TIDAK_SAMA = auto()      # !=
    LEBIH_BESAR = auto()     # >
    LEBIH_KECIL = auto()     # <
    LEBIH_BESAR_SAMA = auto()  # >=
    LEBIH_KECIL_SAMA = auto()  # <=

    # --- Tanda baca ---
    TITIK_DUA = auto()       # :
    KOMA = auto()            # ,
    TITIK = auto()           # .
    KURUNG_BUKA = auto()     # (
    KURUNG_TUTUP = auto()    # )
    SIKU_BUKA = auto()       # [
    SIKU_TUTUP = auto()      # ]
    KURAWAL_BUKA = auto()    # {
    KURAWAL_TUTUP = auto()   # }

    # --- Indentasi ---
    INDENT = auto()          # Penambahan level indentasi
    DEDENT = auto()          # Pengurangan level indentasi
    BARIS_BARU = auto()      # Akhir baris / newline

    # --- Khusus ---
    EOF = auto()             # Akhir file


# ============================================================
# Mapping kata kunci tunggal → TokenType
# ============================================================
KATA_KUNCI = {
    # Deklarasi
    "buat": TokenType.BUAT,
    "tetap": TokenType.TETAP,
    "adalah": TokenType.ADALAH,

    # Tipe data
    "bilangan": TokenType.BILANGAN,
    "teks": TokenType.TEKS_TIPE,
    "logika": TokenType.LOGIKA_TIPE,

    # Nilai literal
    "benar": TokenType.BENAR,
    "salah": TokenType.SALAH,
    "kosong": TokenType.KOSONG,

    # Kondisi
    "jika": TokenType.JIKA,
    "kalau": TokenType.JIKA,            # sinonim
    "selainnya": TokenType.SELAINNYA,
    "pilih": TokenType.PILIH,
    "ketika": TokenType.KETIKA,
    "bawaan": TokenType.BAWAAN,
    "maka": TokenType.MAKA,

    # Perulangan
    "selama": TokenType.SELAMA,
    "untuk": TokenType.UNTUK,
    "dari": TokenType.DARI,
    "sampai": TokenType.SAMPAI,
    "langkah": TokenType.LANGKAH,
    "dalam": TokenType.DALAM,
    "ulangi": TokenType.ULANGI,
    "berhenti": TokenType.BERHENTI,
    "lewati": TokenType.LEWATI,
    "lakukan": TokenType.LAKUKAN,

    # Fungsi
    "fungsi": TokenType.FUNGSI,
    "kembalikan": TokenType.KEMBALIKAN,

    # OOP
    "kelas": TokenType.KELAS,
    "mewarisi": TokenType.MEWARISI,
    "diri": TokenType.DIRI,
    "super": TokenType.SUPER,
    "pribadi": TokenType.PRIBADI,
    "statis": TokenType.STATIS,

    # Modul
    "impor": TokenType.IMPOR,
    "sebagai": TokenType.SEBAGAI,

    # Error handling
    "coba": TokenType.COBA,
    "tangkap": TokenType.TANGKAP,
    "akhirnya": TokenType.AKHIRNYA,
    "lempar": TokenType.LEMPAR,

    # I/O
    "tampilkan": TokenType.TAMPILKAN,
    "cetak": TokenType.TAMPILKAN,       # sinonim
    "tulis": TokenType.TAMPILKAN,       # sinonim
    "masukan": TokenType.MASUKAN,
    "masukan_angka": TokenType.MASUKAN_ANGKA,
    "masukan_desimal": TokenType.MASUKAN_DESIMAL,

    # Logika
    "dan": TokenType.DAN,
    "atau": TokenType.ATAU,
    "bukan": TokenType.BUKAN,
    "tidak": TokenType.BUKAN,           # sinonim: "jika tidak hujan"

    # Keberadaan ("ada dalam" digabung di parser: ADA + DALAM)
    "ada": TokenType.ADA,

    # Kata seperti "sama", "lebih", "kurang", "paling", "sisa", "habis" hanya
    # menjadi kata kunci sebagai bagian dari frasa (lihat FRASA_KATA_KUNCI),
    # sehingga tetap bisa dipakai sebagai nama variabel biasa.

    # Operator aritmatika teks
    "ditambah": TokenType.DITAMBAH,
    "dikurang": TokenType.DIKURANG,
    "dikurangi": TokenType.DIKURANG,    # bentuk baku
    "dikali": TokenType.DIKALI,
    "dikalikan": TokenType.DIKALI,
    "dibagi": TokenType.DIBAGI,
    "pangkat": TokenType.PANGKAT_KK,
    "dipangkatkan": TokenType.PANGKAT_KK,
}

# ============================================================
# Frasa kata kunci (multi-kata) → TokenType
# ============================================================
# Lexer mencocokkan frasa TERPANJANG lebih dulu: "tidak sama dengan" menang
# atas "tidak sama", dan "lebih dari atau sama dengan" menang atas "lebih dari".
FRASA_KATA_KUNCI = {
    # Kondisi & perulangan
    ("atau", "jika"): TokenType.ATAU_JIKA,
    ("atau", "kalau"): TokenType.ATAU_JIKA,
    ("untuk", "setiap"): TokenType.UNTUK_SETIAP,
    ("di", "dalam"): TokenType.DALAM,

    # Keberadaan: "x tidak ada dalam daftar"
    ("tidak", "ada"): TokenType.TIDAK_ADA,

    # Aritmatika
    ("sisa", "bagi"): TokenType.SISA_BAGI,
    ("habis", "dibagi"): TokenType.HABIS_DIBAGI,
    ("tidak", "habis", "dibagi"): TokenType.TIDAK_HABIS_DIBAGI,

    # Perbandingan == dan !=
    ("sama", "dengan"): TokenType.SAMA_DENGAN_OP,
    ("tidak", "sama"): TokenType.TIDAK_SAMA_OP,
    ("tidak", "sama", "dengan"): TokenType.TIDAK_SAMA_OP,

    # Perbandingan >= dan <= tanpa kata "dari"
    ("paling", "sedikit"): TokenType.TIDAK_KURANG_DARI,
    ("paling", "banyak"): TokenType.TIDAK_LEBIH_DARI,
    ("lebih", "besar", "atau", "sama", "dengan"): TokenType.TIDAK_KURANG_DARI,
    ("lebih", "kecil", "atau", "sama", "dengan"): TokenType.TIDAK_LEBIH_DARI,
    ("lebih", "besar", "sama", "dengan"): TokenType.TIDAK_KURANG_DARI,
    ("lebih", "kecil", "sama", "dengan"): TokenType.TIDAK_LEBIH_DARI,
}

# Perbandingan yang memakai kata "dari". Setiap frasa juga didaftarkan dengan
# "daripada", mis. "lebih besar daripada", "kurang daripada".
_FRASA_PERBANDINGAN_DARI = {
    ("lebih", "dari"): TokenType.LEBIH_DARI,
    ("lebih", "besar", "dari"): TokenType.LEBIH_DARI,
    ("kurang", "dari"): TokenType.KURANG_DARI,
    ("lebih", "kecil", "dari"): TokenType.KURANG_DARI,
    ("tidak", "kurang", "dari"): TokenType.TIDAK_KURANG_DARI,
    ("tidak", "lebih", "dari"): TokenType.TIDAK_LEBIH_DARI,
    ("lebih", "dari", "atau", "sama", "dengan"): TokenType.TIDAK_KURANG_DARI,
    ("lebih", "besar", "dari", "atau", "sama", "dengan"): TokenType.TIDAK_KURANG_DARI,
    ("kurang", "dari", "atau", "sama", "dengan"): TokenType.TIDAK_LEBIH_DARI,
    ("lebih", "kecil", "dari", "atau", "sama", "dengan"): TokenType.TIDAK_LEBIH_DARI,
}
for _frasa, _tipe in _FRASA_PERBANDINGAN_DARI.items():
    FRASA_KATA_KUNCI[_frasa] = _tipe
    FRASA_KATA_KUNCI[tuple("daripada" if k == "dari" else k for k in _frasa)] = _tipe

PANJANG_FRASA_MAKS = max(len(frasa) for frasa in FRASA_KATA_KUNCI)
AWALAN_FRASA = {frasa[0] for frasa in FRASA_KATA_KUNCI}

# ============================================================
# Mapping operator → TokenType
# ============================================================
OPERATORS = {
    "**": TokenType.PANGKAT,
    "+=": TokenType.TAMBAH_SAMA,
    "-=": TokenType.KURANG_SAMA,
    "*=": TokenType.KALI_SAMA,
    "/=": TokenType.BAGI_SAMA,
    "%=": TokenType.MODULO_SAMA,
    "==": TokenType.SAMA,
    "!=": TokenType.TIDAK_SAMA,
    ">=": TokenType.LEBIH_BESAR_SAMA,
    "<=": TokenType.LEBIH_KECIL_SAMA,
    ">": TokenType.LEBIH_BESAR,
    "<": TokenType.LEBIH_KECIL,
    "+": TokenType.TAMBAH,
    "-": TokenType.KURANG,
    "*": TokenType.KALI,
    "/": TokenType.BAGI,
    "%": TokenType.MODULO,
    "=": TokenType.SAMA_DENGAN,
}

# ============================================================
# Mapping punctuation → TokenType
# ============================================================
PUNCTUATION = {
    ":": TokenType.TITIK_DUA,
    ",": TokenType.KOMA,
    ".": TokenType.TITIK,
    "(": TokenType.KURUNG_BUKA,
    ")": TokenType.KURUNG_TUTUP,
    "[": TokenType.SIKU_BUKA,
    "]": TokenType.SIKU_TUTUP,
    "{": TokenType.KURAWAL_BUKA,
    "}": TokenType.KURAWAL_TUTUP,
}

# Kata kunci "desimal" perlu perlakuan khusus karena bentrok dengan tipe token DESIMAL
# Ditangani di lexer: jika identifier == "desimal", cek konteks
KATA_KUNCI["desimal"] = TokenType.DESIMAL_TIPE


# ============================================================
# Deskripsi tipe token untuk pesan kesalahan yang mudah dipahami
# ============================================================
_DESKRIPSI_KHUSUS = {
    TokenType.IDENTIFIER: "nama (variabel/fungsi)",
    TokenType.ANGKA: "angka",
    TokenType.DESIMAL: "angka desimal",
    TokenType.TEKS: "teks",
    TokenType.TEKS_FORMAT: "teks format",
    TokenType.INDENT: "blok baru yang menjorok ke dalam",
    TokenType.DEDENT: "akhir blok",
    TokenType.BARIS_BARU: "akhir baris",
    TokenType.EOF: "akhir program",
}
_SIMBOL_UNTUK_TIPE = {tipe: simbol for simbol, tipe in {**OPERATORS, **PUNCTUATION}.items()}
_KATA_UNTUK_TIPE = {}
for _kata, _tipe in KATA_KUNCI.items():
    _KATA_UNTUK_TIPE.setdefault(_tipe, _kata)
for _frasa, _tipe in FRASA_KATA_KUNCI.items():
    _KATA_UNTUK_TIPE.setdefault(_tipe, " ".join(_frasa))


def jelaskan_tipe(tipe: TokenType) -> str:
    """Nama tipe token dalam bahasa sehari-hari, mis. TITIK_DUA → "tanda ':'"."""
    if tipe in _DESKRIPSI_KHUSUS:
        return _DESKRIPSI_KHUSUS[tipe]
    if tipe in _SIMBOL_UNTUK_TIPE:
        return f"tanda '{_SIMBOL_UNTUK_TIPE[tipe]}'"
    if tipe in _KATA_UNTUK_TIPE:
        return f"kata '{_KATA_UNTUK_TIPE[tipe]}'"
    return tipe.name
