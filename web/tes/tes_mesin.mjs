// tes_mesin.mjs — Jalankan mesin WebAssembly editor web (mesin/cmd/wasm) di Node.js dengan semua
// tes kesesuaian dan seluruh korpus pembanding (mesin/testdata/korpus.json). Menjamin hasil di
// browser sama persis dengan aplikasi di komputer.
//
//   python web/bangun.py
//   node web/tes/tes_mesin.mjs

import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const SITUS = fileURLToPath(new URL("../situs/", import.meta.url));
const AKAR = fileURLToPath(new URL("../../", import.meta.url));
const FOLDER_TES = path.join(AKAR, "tes_kesesuaian");

await import(path.join(SITUS, "wasm_exec.js"));
const go = new Go();
const { instance } = await WebAssembly.instantiate(fs.readFileSync(path.join(SITUS, "mesin.wasm")), go.importObject);
go.run(instance);

// Pengganti fungsi pekerja.js yang dipanggil mesin
let layar = "";
let sisaMasukan = [];
globalThis.tulisKeluaran = (saluran, teks) => {
  layar += teks;
  return false;
};
globalThis.mintaMasukan = () => JSON.stringify(sisaMasukan.length ? { teks: sisaMasukan.shift() } : {});
globalThis.tidur = () => false;
globalThis.periksaBerhenti = () => false;

function jalankan(kode, masukan = [], opsi = {}) {
  layar = "";
  sisaMasukan = [...masukan];
  const hasil = JSON.parse(globalThis.jalankanIndonesia(kode, JSON.stringify({ berkasBaru: true, ...opsi })));
  return { hasil, layar };
}

const gagal = [];
const baca = (berkas) => fs.readFileSync(berkas, "utf8").replace(/\r\n/g, "\n");

// 1. Tes kesesuaian
const program = fs
  .readdirSync(FOLDER_TES, { recursive: true })
  .filter((f) => f.endsWith(".id"))
  .sort()
  .map((f) => path.join(FOLDER_TES, f));
for (const berkas of program) {
  const nama = path.relative(FOLDER_TES, berkas);
  const dasar = berkas.slice(0, -".id".length);
  const masukan = fs.existsSync(`${dasar}.masukan`) ? baca(`${dasar}.masukan`).split("\n") : [];
  if (masukan.at(-1) === "") masukan.pop();
  const { hasil, layar: keluaran } = jalankan(baca(berkas), masukan);

  const masalah = [];
  if (fs.existsSync(`${dasar}.keluaran`) && keluaran !== baca(`${dasar}.keluaran`)) {
    masalah.push(`keluaran berbeda:\n${keluaran}`);
  }
  if (fs.existsSync(`${dasar}.kesalahan`)) {
    const [jenis, ...potongan] = baca(`${dasar}.kesalahan`).trim().split("\n");
    if (hasil.jenis !== jenis) masalah.push(`seharusnya ${jenis}, ternyata ${hasil.jenis ?? "tanpa kesalahan"}`);
    for (const p of potongan) if (!(hasil.pesan ?? "").includes(p)) masalah.push(`pesan tidak memuat "${p}"`);
  } else if (hasil.jenis) {
    masalah.push(`kesalahan yang tidak diharapkan: ${hasil.pesan}`);
  }
  if (masalah.length) gagal.push(`✖ ${nama}\n    ${masalah.join("\n    ")}`);
}

// 2. Korpus pembanding: keadaan yang sama dengan korpus_test.go (benih, jam, dan masukan tetap)
const MASUKAN = ["42", "Budi", "7", "3,5", "tidak", "ya", "0", "100", "-5", "abc", "", "10"];
const korpus = JSON.parse(fs.readFileSync(path.join(AKAR, "mesin", "testdata", "korpus.json"), "utf8"));
let diperiksa = 0;
for (const k of korpus) {
  if (k.internal) continue;
  diperiksa++;
  const { hasil, layar: keluaran } = jalankan(k.kode, k.masukan ?? MASUKAN, {
    benih: 12345,
    sekarang: "2026-10-01T14:30:45",
    repl: true,
  });
  const masalah = [];
  if (keluaran !== k.keluaran) masalah.push(`keluaran berbeda:\n${keluaran}\n--- seharusnya:\n${k.keluaran}`);
  const pesan = hasil.jenis ? hasil.pesan : null;
  if (pesan !== k.kesalahan) masalah.push(`kesalahan berbeda:\n${pesan}\n--- seharusnya:\n${k.kesalahan}`);
  if ((hasil.hasil ?? null) !== k.hasil) masalah.push(`nilai terakhir ${hasil.hasil}, seharusnya ${k.hasil}`);
  if (masalah.length) gagal.push(`✖ korpus ${k.nama}\n    ${masalah.join("\n    ")}`);
}

// 3. Mesin tetap sehat sesudah rekursi tak berujung
const khusus = [
  ["rekursi tak berujung", "fungsi f(n):\n    kembalikan f(n + 1)\nf(0)", (h) => h.jenis === "KesalahanTumpukan"],
  ["mesin tetap sehat sesudahnya", 'tampilkan "sehat"', (h, l) => !h.jenis && l === "sehat\n"],
];
for (const [nama, kode, benar] of khusus) {
  const { hasil, layar: keluaran } = jalankan(kode);
  if (!benar(hasil, keluaran)) gagal.push(`✖ ${nama}\n    ${JSON.stringify(hasil)} ${JSON.stringify(keluaran)}`);
}

const jumlah = program.length + diperiksa + khusus.length;
if (gagal.length) {
  console.log(gagal.slice(0, 20).join("\n"));
  console.log(`\n${gagal.length} dari ${jumlah} tes gagal di mesin WebAssembly v${globalThis.versiIndonesia}.`);
  process.exit(1);
}
console.log(`✅ ${jumlah} tes lulus di mesin WebAssembly v${globalThis.versiIndonesia} ` +
  `(${program.length} tes kesesuaian, ${diperiksa} kasus korpus).`);
process.exit(0);
