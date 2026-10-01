// pekerja.js — Web Worker yang menjalankan interpreter Bahasa Indonesia di Pyodide.
//
// Program berjalan sinkron di sini, jadi halaman tetap lancar. Selama program berjalan,
// pekerja ini tidak bisa menerima pesan biasa; masukan (tanya), tunggu, dan tombol Hentikan
// karena itu lewat "saluran": permintaan XHR sinkron yang dijawab oleh service worker (sw.js).

import { loadPyodide } from "./pyodide/pyodide.mjs";

const SALURAN = new URL("__saluran__/", self.location.href);
const VERSI = new URL(self.location.href).searchParams.get("v") ?? "";
const PESAN_TANPA_SALURAN =
  "Masukan belum bisa dipakai di browser ini. Muat ulang halaman, atau buka editor di Chrome, " +
  "Firefox, Edge, atau Safari versi terbaru (bukan mode penyamaran).";

let jalankanProgram = null;
let saluranSiap = false;
let sesi = "";
let berhenti = false;
let idMasukan = 0;
let penyangga = "";
let saluranPenyangga = "keluaran";
let kirimTerakhir = 0;

function kirimPenyangga() {
  if (penyangga) {
    postMessage({ jenis: "keluaran", saluran: saluranPenyangga, teks: penyangga });
    penyangga = "";
  }
  kirimTerakhir = performance.now();
}

/** Permintaan sinkron ke service worker; pekerja ini menunggu sampai dijawab. */
function minta(jalur, parameter = {}) {
  const url = new URL(jalur, SALURAN);
  url.searchParams.set("sesi", sesi);
  for (const [kunci, nilai] of Object.entries(parameter)) url.searchParams.set(kunci, String(nilai));
  const xhr = new XMLHttpRequest();
  xhr.open("GET", url.href, false);
  xhr.send();
  if (xhr.status !== 200 || !(xhr.getResponseHeader("Content-Type") ?? "").includes("json")) {
    throw new Error(`saluran tidak tersedia (status ${xhr.status})`);
  }
  return JSON.parse(xhr.responseText);
}

function periksaBerhenti() {
  if (!berhenti && saluranSiap) {
    try {
      berhenti = minta("periksa").berhenti === true;
    } catch {
      // Saluran sesaat tidak tersedia: tombol Hentikan tetap bisa menghentikan pekerja ini.
    }
  }
  return berhenti;
}

// ---- Dipanggil dari jembatan.py ----

self.tulisKeluaran = (saluran, teks) => {
  if (berhenti) return true;
  if (saluran !== saluranPenyangga) {
    kirimPenyangga();
    saluranPenyangga = saluran;
  }
  penyangga += teks;
  // Kirim berkelompok, paling lama tiap 40 ms, agar halaman tidak kebanjiran pesan.
  if (penyangga.length > 8192 || performance.now() - kirimTerakhir > 40) {
    kirimPenyangga();
    return periksaBerhenti();
  }
  return false;
};

self.mintaMasukan = () => {
  kirimPenyangga();
  if (berhenti) return JSON.stringify({ berhenti: true });
  if (!saluranSiap) return JSON.stringify({ gagal: PESAN_TANPA_SALURAN });
  const id = ++idMasukan;
  postMessage({ jenis: "minta-masukan", id });
  for (;;) {
    let jawaban;
    try {
      jawaban = minta("masukan", { id });
    } catch {
      return JSON.stringify({ gagal: PESAN_TANPA_SALURAN });
    }
    if (jawaban.berhenti) {
      berhenti = true;
      return JSON.stringify({ berhenti: true });
    }
    if (typeof jawaban.teks === "string") {
      postMessage({ jenis: "masukan-diterima", id });
      return JSON.stringify({ teks: jawaban.teks });
    }
    // { ulang: true }: belum dijawab, tunggu lagi.
  }
};

self.tidur = (milidetik) => {
  kirimPenyangga();
  if (berhenti) return true;
  const selesai = performance.now() + milidetik;
  for (let sisa = milidetik; sisa > 0; sisa = selesai - performance.now()) {
    if (!saluranSiap) {
      while (performance.now() < selesai) {
        // Tanpa service worker tidak ada cara tidur yang lain.
      }
      return false;
    }
    try {
      if (minta("tidur", { ms: Math.ceil(Math.min(sisa, 20000)) }).berhenti) {
        berhenti = true;
        return true;
      }
    } catch {
      saluranSiap = false;
    }
  }
  return periksaBerhenti();
};

// ---- Persiapan dan perintah dari halaman ----

async function siapkan() {
  const pyodide = await loadPyodide({ indexURL: new URL("pyodide/", self.location.href).href });
  const respons = await fetch(new URL(`interpreter.zip?v=${VERSI}`, self.location.href));
  if (!respons.ok) throw new Error(`interpreter.zip tidak bisa dimuat (status ${respons.status})`);
  pyodide.unpackArchive(await respons.arrayBuffer(), "zip", { extractDir: "/app" });
  pyodide.runPython("import sys\nsys.path.insert(0, '/app')");
  jalankanProgram = pyodide.pyimport("jembatan").jalankan;
  try {
    saluranSiap = minta("periksa").ok === true;
  } catch {
    saluranSiap = false;
  }
  postMessage({ jenis: "siap", saluran: saluranSiap });
}

const persiapan = siapkan().catch((e) => {
  postMessage({ jenis: "gagal-muat", pesan: String(e?.message ?? e) });
});

self.onmessage = async ({ data }) => {
  if (data.jenis !== "jalankan") return;
  await persiapan;
  if (!jalankanProgram) return;
  sesi = data.sesi;
  berhenti = false;
  idMasukan = 0;
  penyangga = "";
  saluranPenyangga = "keluaran";
  kirimTerakhir = performance.now();
  const mulai = performance.now();
  let hasil;
  try {
    hasil = JSON.parse(jalankanProgram(data.kode));
  } catch (e) {
    // Mis. Pyodide kehabisan memori: pekerja ini tidak bisa dipakai lagi.
    hasil = { jenis: "fatal", pesan: String(e?.message ?? e) };
  }
  kirimPenyangga();
  postMessage({ jenis: "selesai", hasil, durasi: performance.now() - mulai });
};
