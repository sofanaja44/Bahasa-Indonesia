// tes_pyodide.mjs — Jalankan semua tes kesesuaian di Pyodide (Node.js), lewat jembatan.py yang
// sama dengan editor browser. Menjamin keluaran di browser sama dengan di komputer.
//
//   python web/bangun.py
//   node web/tes/tes_pyodide.mjs

import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const SITUS = fileURLToPath(new URL("../situs/", import.meta.url));
const FOLDER_TES = fileURLToPath(new URL("../../tes_kesesuaian/", import.meta.url));

const { loadPyodide } = await import(path.join(SITUS, "pyodide", "pyodide.mjs"));
const pyodide = await loadPyodide({ indexURL: path.join(SITUS, "pyodide") + path.sep });
pyodide.unpackArchive(new Uint8Array(fs.readFileSync(path.join(SITUS, "interpreter.zip"))), "zip", { extractDir: "/app" });

// Pengganti fungsi pekerja.js yang dipanggil jembatan.py
let layar = "";
let sisaMasukan = [];
globalThis.tulisKeluaran = (saluran, teks) => {
  if (saluran === "keluaran") layar += teks;
  return false;
};
globalThis.mintaMasukan = () =>
  JSON.stringify(sisaMasukan.length ? { teks: sisaMasukan.shift() } : { gagal: "Tidak ada lagi masukan yang bisa dibaca" });
globalThis.tidur = () => false;

pyodide.runPython("import sys\nsys.path.insert(0, '/app')");
const jalankan = pyodide.pyimport("jembatan").jalankan;

function jalankanProgram(kode, masukan = []) {
  layar = "";
  sisaMasukan = [...masukan];
  return { hasil: JSON.parse(jalankan(kode)), layar };
}

const baca = (berkas) => fs.readFileSync(berkas, "utf8").replace(/\r\n/g, "\n");
const program = fs
  .readdirSync(FOLDER_TES, { recursive: true })
  .filter((f) => f.endsWith(".id"))
  .sort()
  .map((f) => path.join(FOLDER_TES, f));

const gagal = [];
for (const berkas of program) {
  const nama = path.relative(FOLDER_TES, berkas);
  const dasar = berkas.slice(0, -".id".length);
  const masukan = fs.existsSync(`${dasar}.masukan`) ? baca(`${dasar}.masukan`).split("\n") : [];
  if (masukan.at(-1) === "") masukan.pop();
  const { hasil, layar: keluaran } = jalankanProgram(baca(berkas), masukan);

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

// Khusus Pyodide: tumpukan WebAssembly jauh lebih kecil daripada di komputer.
const khusus = [
  ["rekursi 2.900 tingkat", "fungsi t(n):\n    jika n == 0:\n        kembalikan 0\n    kembalikan 1 + t(n - 1)\ntampilkan t(2900)", (h, l) => !h.jenis && l === "2900\n"],
  ["rekursi tak berujung", "fungsi f(n):\n    kembalikan f(n + 1)\nf(0)", (h) => h.jenis === "KesalahanTumpukan"],
  ["Python tetap sehat sesudahnya", 'tampilkan "sehat"', (h, l) => !h.jenis && l === "sehat\n"],
];
for (const [nama, kode, benar] of khusus) {
  const { hasil, layar: keluaran } = jalankanProgram(kode);
  if (!benar(hasil, keluaran)) gagal.push(`✖ ${nama}\n    ${JSON.stringify(hasil)} ${JSON.stringify(keluaran)}`);
}

const jumlah = program.length + khusus.length;
if (gagal.length) {
  console.log(gagal.join("\n"));
  console.log(`\n${gagal.length} dari ${jumlah} tes gagal di Pyodide ${pyodide.version}.`);
  process.exit(1);
}
console.log(`✅ ${jumlah} tes lulus di Pyodide ${pyodide.version}.`);
