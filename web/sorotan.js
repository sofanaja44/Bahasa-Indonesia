// sorotan.js — Pewarnaan kode Bahasa Indonesia untuk editor web.
//
// sorot(kode) menghasilkan HTML dengan baris baru yang sama seperti kodenya; tidak ada tag
// yang melewati baris baru, sehingga hasilnya aman dipecah per baris.
// Kosakata (kata kunci, frasa, fungsi bawaan) dibuat oleh bangun.py dari src/token_types.py,
// sehingga pewarnaan selalu mengikuti bahasanya. Aturan membaca kode sama dengan src/lexer.py:
// komentar # dan """...""", teks "..." / '...' / f"..." / format"...", serta frasa terpanjang.

const ESCAPE = { "&": "&amp;", "<": "&lt;", ">": "&gt;" };
const escape = (teks) => teks.replace(/[&<>]/g, (c) => ESCAPE[c]);

export function buatPenyorot(kosakata) {
  const kataKunci = new Map(Object.entries(kosakata.kata_kunci));
  const frasa = new Map(Object.entries(kosakata.frasa));
  const awalanFrasa = new Set([...frasa.keys()].map((f) => f.split(" ")[0]));
  const panjangFrasaMaks = Math.max(1, ...[...frasa.keys()].map((f) => f.split(" ").length));
  const kataPerintah = new Map(
    Object.entries(kosakata.kata_perintah).map(([kata, sambungan]) => [kata, new Set(sambungan)]),
  );
  const fungsiBawaan = new Set(kosakata.fungsi_bawaan);

  return function sorot(kode) {
    const POLA =
      /("""[\s\S]*?(?:"""|$)|#[^\n]*)|((?:f|format)?(?:"(?:[^"\\\n]|\\.)*"?|'(?:[^'\\\n]|\\.)*'?))|(\d+(?:\.\d+)?)|([\p{L}_][\p{L}\p{N}_]*)|(\n)|([^\n\p{L}\p{N}_"'#]+|[^\n])/uy;
    const KATA_LANJUT = /[ \t]+([\p{L}_][\p{L}\p{N}_]*)/uy;
    const SETELAH_TANYA = /[ \t]*(angka[ \t]+)?["']/uy;
    const KARAKTER_BERIKUT = /[ \t]*([^ \t])/uy;
    const intip = (pola, posisi) => {
      pola.lastIndex = posisi;
      return pola.exec(kode);
    };
    // Komentar """ bisa beberapa baris: setiap baris dibungkus sendiri, agar hasilnya bisa dipecah per baris.
    const bungkus = (kelas, teks) =>
      teks
        .split("\n")
        .map((t) => (t ? `<span class="s-${kelas}">${escape(t)}</span>` : ""))
        .join("\n");

    let html = "";
    let awalBaris = true; // belum ada token di baris ini
    let kataPertama = null; // kata pertama di baris ini
    let sambungan = null; // kata sambungan kata kerja natural di awal baris, mis. "menjadi" untuk "ubah"
    let sebelumnya = ""; // karakter terakhir yang bukan spasi
    let kataSebelumnya = "";
    let angkaTanya = false; // "tanya angka ...": kata "angka" ikut diwarnai

    let m;
    POLA.lastIndex = 0;
    while (POLA.lastIndex < kode.length && (m = POLA.exec(kode))) {
      const [, komentar, teks, angka, kata, barisBaru, lain] = m;
      if (barisBaru) {
        html += "\n";
        awalBaris = true;
        kataPertama = sambungan = null;
        sebelumnya = kataSebelumnya = "";
        continue;
      }
      if (lain) {
        html += escape(lain);
        const isi = lain.trim();
        if (isi) {
          awalBaris = false;
          sebelumnya = isi.at(-1);
        }
        continue;
      }
      if (komentar) {
        html += bungkus("komentar", komentar);
        continue;
      }
      if (teks || angka) {
        html += bungkus(teks ? "teks" : "angka", teks || angka);
        awalBaris = false;
        sebelumnya = (teks || angka).at(-1);
        continue;
      }

      // Kata: kata kunci, frasa, kata kerja natural, fungsi bawaan, atau nama biasa.
      const pertama = awalBaris;
      const setelahTitik = sebelumnya === ".";
      awalBaris = false;
      sebelumnya = "a";
      let akhir = POLA.lastIndex;
      let kataTerakhir = kata;
      let kelas = null;

      if (!setelahTitik && awalanFrasa.has(kata)) {
        const kataKata = [kata];
        const ujung = [akhir];
        for (let lanjut; kataKata.length < panjangFrasaMaks && (lanjut = intip(KATA_LANJUT, ujung.at(-1))); ) {
          kataKata.push(lanjut[1]);
          ujung.push(KATA_LANJUT.lastIndex);
        }
        for (let n = kataKata.length; n >= 2; n--) {
          const f = kataKata.slice(0, n).join(" ");
          if (frasa.has(f)) {
            kelas = frasa.get(f);
            akhir = ujung[n - 1];
            kataTerakhir = kataKata[n - 1];
            break;
          }
        }
      }

      if (kelas || setelahTitik) {
        // frasa sudah ditemukan, atau nama atribut/metode seperti daftar.tambahkan
      } else if (pertama && kataPerintah.has(kata)) {
        kelas = "kunci";
        sambungan = kataPerintah.get(kata);
      } else if (sambungan?.has(kata) || (kata === "kali" && kataPertama === "ulangi")) {
        kelas = "kunci";
      } else if (kata === "tanya" && intip(SETELAH_TANYA, akhir)) {
        kelas = "kunci";
        angkaTanya = Boolean(intip(SETELAH_TANYA, akhir)[1]);
      } else if (kata === "angka" && angkaTanya) {
        kelas = "kunci";
      } else if (kataKunci.has(kata)) {
        kelas = kataKunci.get(kata);
      } else if (kataSebelumnya === "fungsi" || kataSebelumnya === "kelas") {
        kelas = "definisi";
      } else if (fungsiBawaan.has(kata) && intip(KARAKTER_BERIKUT, akhir)?.[1] === "(") {
        kelas = "fungsi";
      }
      if (kata !== "tanya") angkaTanya = false;
      if (pertama) kataPertama = kata;
      kataSebelumnya = kataTerakhir;

      const potongan = kode.slice(m.index, akhir);
      html += kelas ? bungkus(kelas, potongan) : escape(potongan);
      POLA.lastIndex = akhir;
    }
    return html;
  };
}
