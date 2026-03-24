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
    JIKA = auto()            # jika (if)
    ATAU_JIKA = auto()       # atau jika (else if)
    SELAINNYA = auto()       # selainnya (else)
    PILIH = auto()           # pilih (switch)
    KETIKA = auto()          # ketika (case)
    BAWAAN = auto()          # bawaan (default)

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
    BUKAN = auto()           # bukan (not)

    # --- Operator "ada dalam" ---
    ADA = auto()             # ada (exists, bagian dari "ada dalam")

    # --- Operator teks Indonesia (alternatif simbol) ---
    SAMA_DENGAN_OP = auto()   # sama dengan (==)
    TIDAK_SAMA_OP = auto()    # tidak sama (!=)
    LEBIH_DARI = auto()       # lebih dari (>)
    KURANG_DARI = auto()      # kurang dari (<)
    TIDAK_KURANG_DARI = auto() # tidak kurang dari (>=)
    TIDAK_LEBIH_DARI = auto()  # tidak lebih dari (<=)
    SISA_BAGI = auto()        # sisa bagi (%)
    PANGKAT_KK = auto()       # pangkat (**) — sebagai kata kunci infix
    DITAMBAH = auto()         # ditambah (+)
    DIKURANG = auto()         # dikurang (-)
    DIKALI = auto()           # dikali (*)
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
    "selainnya": TokenType.SELAINNYA,
    "pilih": TokenType.PILIH,
    "ketika": TokenType.KETIKA,
    "bawaan": TokenType.BAWAAN,

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

    # Keberadaan
    "ada": TokenType.ADA,
    "setiap": TokenType.IDENTIFIER,    # handled via look-ahead dari "untuk"

    # Kata kunci untuk operator teks (look-ahead di lexer)
    # "sama", "tidak", "lebih", "kurang", "dengan", "sisa" — diproses via look-ahead
    # Tidak didaftarkan sebagai standalone karena bisa jadi identifier biasa

    # Operator aritmatika teks
    "ditambah": TokenType.DITAMBAH,
    "dikurang": TokenType.DIKURANG,
    "dikali": TokenType.DIKALI,
    "dibagi": TokenType.DIBAGI,
}

# ============================================================
# Kata kunci multi-kata — di-handle dengan look-ahead di lexer
# ============================================================
# "atau jika"   → ATAU_JIKA  (ketika lexer melihat "atau", cek apakah next = "jika")
# "untuk setiap" → UNTUK_SETIAP (ketika lexer melihat "untuk", cek apakah next = "setiap")
# "ada dalam"   → handled di parser (ADA + DALAM)

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
