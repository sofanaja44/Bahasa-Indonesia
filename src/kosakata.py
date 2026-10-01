"""
kosakata.py — Kosakata bahasa untuk alat bantu: pewarnaan kode di editor web dan di VS Code.

Dibuat dari token_types.py dan fungsi bawaan, sehingga alat bantu selalu mengikuti bahasanya.
"""

from src.builtins import daftar_fungsi_bawaan
from src.token_types import FRASA_KATA_KUNCI, KATA_KUNCI

# Golongan warna berdasarkan jenis token; selain ini termasuk golongan "kunci".
_GOLONGAN = {
    "nilai": {"BENAR", "SALAH", "KOSONG", "WAKTU_SEKARANG", "ANGKA_ACAK", "DIRI", "SUPER"},
    "tipe": {"BILANGAN", "TEKS_TIPE", "LOGIKA_TIPE", "DESIMAL_TIPE"},
    "operator": {
        "DAN", "ATAU", "BUKAN", "ADA", "TIDAK_ADA", "DITAMBAH", "DIKURANG", "DIKALI", "DIBAGI",
        "PANGKAT_KK", "SISA_BAGI", "HABIS_DIBAGI", "TIDAK_HABIS_DIBAGI", "SAMA_DENGAN_OP", "TIDAK_SAMA_OP",
        "LEBIH_DARI", "KURANG_DARI", "TIDAK_KURANG_DARI", "TIDAK_LEBIH_DARI",
    },
}

# Kata kerja natural yang tidak dicadangkan, beserta kata sambungannya. Alat bantu mewarnainya
# hanya di awal perintah, sebab kata-kata ini tetap boleh dipakai sebagai nama.
KATA_PERINTAH = {
    "ubah": ["menjadi"],
    "tambahkan": ["ke"],
    "kurangi": ["dengan", "dari"],
    "kalikan": ["dengan"],
    "bagi": ["dengan"],
    "tunggu": ["detik", "menit"],
}


def golongan(tipe) -> str:
    """Golongan warna sebuah jenis token: 'kunci', 'operator', 'nilai', atau 'tipe'."""
    for nama, jenis in _GOLONGAN.items():
        if tipe.name in jenis:
            return nama
    return "kunci"


def kosakata() -> dict:
    return {
        "kata_kunci": {kata: golongan(tipe) for kata, tipe in sorted(KATA_KUNCI.items())},
        "frasa": {" ".join(frasa): golongan(tipe) for frasa, tipe in sorted(FRASA_KATA_KUNCI.items())},
        "kata_perintah": KATA_PERINTAH,
        "fungsi_bawaan": sorted(daftar_fungsi_bawaan()),
    }
