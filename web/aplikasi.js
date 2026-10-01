// aplikasi.js — Editor web Bahasa Indonesia: editor kode, keluaran, contoh, dan tautan berbagi.
//
// Program dijalankan oleh pekerja.js (mesin WebAssembly di Web Worker). Jawaban "tanya" dan tombol
// Hentikan dikirim lewat service worker (sw.js), karena pekerja sedang sibuk menjalankan program.

import { buatPenyorot } from "./sorotan.js?v=__VERSI__";

const VERSI = "__VERSI__";
const KUNCI_DRAF = "bahasa-indonesia:draf";
const MAKS_KELUARAN = 200_000; // karakter; keluaran yang lebih lama dibuang dari layar
const KODE_AWAL = `# Selamat datang di editor Bahasa Indonesia!
# Tekan ▶ Jalankan (atau Ctrl+Enter) untuk menjalankan program ini.

buat nama adalah tanya "Siapa namamu? "
tampilkan format"Halo, {nama}! Selamat belajar pemrograman."

buat umur adalah tanya angka "Berapa umurmu? "
jika umur paling sedikit 17, maka tampilkan "Kamu sudah boleh membuat KTP."
jika tidak, tampilkan "Masih", 17 dikurangi umur, "tahun lagi sampai boleh membuat KTP."

ulangi 3 kali:
    tampilkan "Hore!"
`;

const $ = (id) => document.getElementById(id);
const el = {
  kode: $("kode"),
  sorotan: $("sorotan"),
  keluaran: $("keluaran"),
  status: $("status"),
  jalankan: $("tombol-jalankan"),
  hentikan: $("tombol-hentikan"),
  bagikan: $("tombol-bagikan"),
  bersihkan: $("tombol-bersihkan"),
  contoh: $("pilih-contoh"),
  pemberitahuan: $("pemberitahuan"),
};

function simpan(kunci, nilai) {
  try {
    localStorage.setItem(kunci, nilai);
  } catch {
    // Penyimpanan tidak tersedia (mis. mode penyamaran): draf tidak disimpan.
  }
}

function baca(kunci) {
  try {
    return localStorage.getItem(kunci);
  } catch {
    return null;
  }
}

function setStatus(pesan, galat = false) {
  el.status.textContent = pesan;
  el.status.classList.toggle("galat", galat);
}

let pengaturPemberitahuan = 0;
function beritahu(pesan, { tombol, aksi, lama = 5000 } = {}) {
  clearTimeout(pengaturPemberitahuan);
  el.pemberitahuan.replaceChildren(pesan);
  if (tombol) {
    const b = document.createElement("button");
    b.type = "button";
    b.textContent = tombol;
    b.addEventListener("click", aksi);
    el.pemberitahuan.append(b);
  }
  el.pemberitahuan.hidden = false;
  if (lama) pengaturPemberitahuan = setTimeout(() => (el.pemberitahuan.hidden = true), lama);
}

// =====================================================================
// Editor
// =====================================================================

let sorot = (kode) => kode.replace(/[&<>]/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;" })[c]);
let bolehSimpan = true; // program dari tautan berbagi baru disimpan setelah diubah
let kodeTerakhirDimuat = "";
let pengaturSimpan = 0;

function perbaruiTampilan() {
  // Satu elemen per baris: nomor baris (CSS) dan tanda kesalahan menempel pada barisnya.
  const baris = sorot(el.kode.value).split("\n");
  el.sorotan.innerHTML = baris.map((b) => `<div class="b">${b}</div>`).join("");
  el.sorotan.parentElement.parentElement.style.setProperty("--digit", Math.max(2, String(baris.length).length));
  samakanGulir();
}

function samakanGulir() {
  el.sorotan.parentElement.scrollTop = el.kode.scrollTop;
}

function muatKode(kode, { simpanDraf }) {
  el.kode.value = kode;
  kodeTerakhirDimuat = kode;
  bolehSimpan = simpanDraf;
  if (simpanDraf) simpan(KUNCI_DRAF, kode);
  hapusTandaGalat();
  perbaruiTampilan();
  el.kode.scrollTop = 0;
  samakanGulir();
}

/** Sisipkan teks di posisi kursor; memakai execCommand agar tetap bisa dibatalkan (Ctrl+Z). */
function sisipkan(teks) {
  el.kode.focus();
  if (!document.execCommand("insertText", false, teks)) {
    el.kode.setRangeText(teks, el.kode.selectionStart, el.kode.selectionEnd, "end");
    el.kode.dispatchEvent(new Event("input"));
  }
}

/** Tambah atau kurangi jorokan (4 spasi) pada baris-baris yang dipilih. */
function ubahJorokan(tambah) {
  const ta = el.kode;
  const nilai = ta.value;
  const awal = nilai.lastIndexOf("\n", ta.selectionStart - 1) + 1;
  let akhir = ta.selectionEnd;
  if (akhir > ta.selectionStart && nilai[akhir - 1] === "\n") akhir--;
  const ujungBaris = nilai.indexOf("\n", akhir);
  const ujung = ujungBaris === -1 ? nilai.length : ujungBaris;
  const lama = nilai.slice(awal, ujung);
  const baru = lama
    .split("\n")
    .map((b) => (tambah ? `    ${b}` : b.replace(/^( {1,4}|\t)/, "")))
    .join("\n");
  if (baru === lama) return;
  const satuBaris = !lama.includes("\n");
  const posisiKursor = ta.selectionStart;
  ta.setSelectionRange(awal, ujung);
  sisipkan(baru);
  if (satuBaris) {
    const geser = baru.length - lama.length;
    const posisi = Math.max(awal, posisiKursor + geser);
    ta.setSelectionRange(posisi, posisi);
  } else {
    ta.setSelectionRange(awal, awal + baru.length);
  }
}

function tekanTab(mundur) {
  const ta = el.kode;
  const adaPilihanBanyakBaris = ta.value.slice(ta.selectionStart, ta.selectionEnd).includes("\n");
  if (mundur || adaPilihanBanyakBaris) {
    ubahJorokan(!mundur);
  } else {
    const kolom = ta.selectionStart - (ta.value.lastIndexOf("\n", ta.selectionStart - 1) + 1);
    sisipkan(" ".repeat(4 - (kolom % 4)));
  }
}

function tekanEnter() {
  const ta = el.kode;
  const awalBaris = ta.value.lastIndexOf("\n", ta.selectionStart - 1) + 1;
  const baris = ta.value.slice(awalBaris, ta.selectionStart);
  let jorokan = baris.match(/^[ \t]*/)[0];
  // Baris yang membuka blok ("jika ...:", "... maka", "... lakukan") → baris berikutnya menjorok.
  if (/(:|\bmaka|\blakukan)[ \t]*$/.test(baris.replace(/[ \t]*#[^"']*$/, ""))) jorokan += "    ";
  sisipkan(`\n${jorokan}`);
}

el.kode.addEventListener("input", () => {
  hapusTandaGalat();
  perbaruiTampilan();
  bolehSimpan = true;
  clearTimeout(pengaturSimpan);
  pengaturSimpan = setTimeout(() => bolehSimpan && simpan(KUNCI_DRAF, el.kode.value), 300);
});

el.kode.addEventListener("scroll", samakanGulir);

el.kode.addEventListener("keydown", (e) => {
  if (e.isComposing) return;
  if (e.key === "Tab" && !e.ctrlKey && !e.metaKey && !e.altKey) {
    e.preventDefault();
    tekanTab(e.shiftKey);
  } else if (e.key === "Enter" && !e.shiftKey && !e.ctrlKey && !e.metaKey && !e.altKey) {
    e.preventDefault();
    tekanEnter();
  } else if (e.key === "Escape") {
    el.kode.blur(); // agar tombol Tab bisa dipakai untuk pindah ke tombol lain
  }
});

for (const tombol of document.querySelectorAll(".bilah-ketik button")) {
  // Jangan pindahkan fokus dari editor, agar keyboard di layar tidak tertutup.
  tombol.addEventListener("pointerdown", (e) => e.preventDefault());
  tombol.addEventListener("click", () => {
    const sisip = tombol.dataset.sisip;
    if (sisip === "tab") tekanTab(false);
    else if (sisip === "untab") tekanTab(true);
    else sisipkan(sisip);
  });
}

// ---- Tanda baris yang salah ----

function tandaiGalat(baris) {
  hapusTandaGalat();
  el.sorotan.children[baris - 1]?.classList.add("galat");
}

function hapusTandaGalat() {
  for (const b of el.sorotan.querySelectorAll(".galat")) b.classList.remove("galat");
}

function lompatKeBaris(baris, kolom = 1) {
  const semua = el.kode.value.split("\n");
  const nomor = Math.min(Math.max(baris, 1), semua.length);
  let posisi = 0;
  for (let i = 0; i < nomor - 1; i++) posisi += semua[i].length + 1;
  posisi += Math.min(Math.max(kolom - 1, 0), semua[nomor - 1].length);
  el.kode.focus({ preventScroll: true });
  el.kode.setSelectionRange(posisi, posisi);
  el.kode.scrollTop = Math.max(0, el.sorotan.children[nomor - 1].offsetTop - el.kode.clientHeight / 3);
  samakanGulir();
}

// =====================================================================
// Keluaran
// =====================================================================

let panjangKeluaran = 0;
let formMasukan = null;

function diBawah() {
  const k = el.keluaran;
  return k.scrollHeight - k.scrollTop - k.clientHeight < 48;
}

function gulirKeBawah() {
  el.keluaran.scrollTop = el.keluaran.scrollHeight;
}

function tambahKeluaran(teks, kelas = "") {
  if (!teks) return;
  const keBawah = diBawah();
  const terakhir = formMasukan ? formMasukan.previousSibling : el.keluaran.lastChild;
  if (terakhir?.nodeType === 1 && terakhir.tagName === "SPAN" && terakhir.className === kelas) {
    terakhir.lastChild.appendData(teks);
  } else {
    const span = document.createElement("span");
    span.className = kelas;
    span.append(teks);
    el.keluaran.insertBefore(span, formMasukan);
  }
  panjangKeluaran += teks.length;
  pangkasKeluaran();
  if (keBawah) gulirKeBawah();
}

function pangkasKeluaran() {
  if (panjangKeluaran <= MAKS_KELUARAN) return;
  let lebih = panjangKeluaran - MAKS_KELUARAN * 0.8;
  for (let node = el.keluaran.firstChild; node && lebih > 0; ) {
    const berikut = node.nextSibling;
    if (node.tagName === "SPAN" && !node.classList.contains("info")) {
      const panjang = node.textContent.length;
      if (panjang <= lebih) {
        node.remove();
        lebih -= panjang;
        panjangKeluaran -= panjang;
      } else {
        node.textContent = node.textContent.slice(lebih);
        panjangKeluaran -= lebih;
        lebih = 0;
      }
    }
    node = berikut;
  }
  if (!el.keluaran.querySelector(".dipangkas")) {
    const info = document.createElement("span");
    info.className = "info dipangkas";
    info.textContent = "(keluaran yang lebih lama tidak ditampilkan)\n";
    el.keluaran.prepend(info);
  }
}

function pastikanBarisBaru() {
  const teks = el.keluaran.textContent;
  if (teks && !teks.endsWith("\n")) tambahKeluaran("\n");
}

function bersihkanKeluaran() {
  for (const node of [...el.keluaran.childNodes]) if (node !== formMasukan) node.remove();
  panjangKeluaran = 0;
}

// ---- Masukan untuk "tanya" ----

let jawabanTertunda = null;
let pengaturKirimUlang = 0;

function tampilkanFormMasukan(id) {
  hapusFormMasukan();
  const keBawah = diBawah();
  formMasukan = document.createElement("form");
  formMasukan.className = "form-masukan";
  const masukan = document.createElement("input");
  Object.assign(masukan, { type: "text", autocomplete: "off", spellcheck: false, enterKeyHint: "send" });
  masukan.setAttribute("autocapitalize", "off");
  masukan.setAttribute("aria-label", "Jawaban untuk program");
  const kirim = document.createElement("button");
  kirim.type = "submit";
  kirim.textContent = "Kirim";
  formMasukan.append(masukan, kirim);
  formMasukan.addEventListener("submit", (e) => {
    e.preventDefault();
    const teks = masukan.value;
    hapusFormMasukan();
    tambahKeluaran(`${teks}\n`, "jawaban");
    kirimJawaban(id, teks);
    setStatus("Berjalan…");
  });
  el.keluaran.append(formMasukan);
  masukan.focus({ preventScroll: true });
  if (keBawah) gulirKeBawah();
}

function hapusFormMasukan() {
  formMasukan?.remove();
  formMasukan = null;
}

function kirimJawaban(id, teks) {
  jawabanTertunda = { jenis: "jawab", sesi, id, teks };
  kirimKeServiceWorker(jawabanTertunda);
  // Kirim ulang sampai pekerja mengonfirmasi, kalau-kalau service worker sempat dimulai ulang browser.
  clearInterval(pengaturKirimUlang);
  pengaturKirimUlang = setInterval(() => jawabanTertunda && kirimKeServiceWorker(jawabanTertunda), 2000);
}

function lupakanJawaban() {
  jawabanTertunda = null;
  clearInterval(pengaturKirimUlang);
}

// =====================================================================
// Service worker dan pekerja (mesin WebAssembly)
// =====================================================================

let pekerja = null;
let siap = false;
let berjalan = false;
let sesi = "";
let saluranAda = false;
let pengaturPaksa = 0;

function kirimKeServiceWorker(pesan) {
  navigator.serviceWorker?.controller?.postMessage(pesan);
}

async function siapkanServiceWorker() {
  if (!("serviceWorker" in navigator) || !window.isSecureContext) return;
  let pengendali = navigator.serviceWorker.controller;
  navigator.serviceWorker.addEventListener("controllerchange", () => {
    // Kunjungan pertama juga memicu ini; yang diberitahukan hanya penggantian versi.
    if (pengendali) {
      beritahu("Versi baru editor sudah tersedia.", { tombol: "Muat ulang", aksi: () => location.reload(), lama: 0 });
    }
    pengendali = navigator.serviceWorker.controller;
  });
  try {
    const registrasi = await navigator.serviceWorker.register("sw.js");
    if (navigator.serviceWorker.controller) return;
    // Kunjungan pertama (atau Shift+Muat ulang): tunggu service worker mengambil alih halaman,
    // karena pekerja hanya bisa memakai saluran bila dibuat sesudahnya.
    await new Promise((selesai) => {
      navigator.serviceWorker.addEventListener("controllerchange", selesai, { once: true });
      registrasi.active?.postMessage({ jenis: "klaim" });
      setTimeout(selesai, 10000);
    });
  } catch (e) {
    console.warn("Service worker tidak bisa dipasang:", e);
  }
}

function perbaruiTombol() {
  el.jalankan.disabled = !siap || berjalan;
  el.jalankan.textContent = siap ? "▶ Jalankan" : "Memuat…";
  el.jalankan.hidden = berjalan;
  el.hentikan.hidden = !berjalan;
}

function buatPekerja() {
  siap = false;
  perbaruiTombol();
  pekerja = new Worker(`pekerja.js?v=${VERSI}`, { type: "module" });
  pekerja.addEventListener("message", ({ data }) => tanganiPesan(data));
  pekerja.addEventListener("error", (e) => {
    setStatus(`Editor gagal dimuat: ${e.message || "browser ini mungkin terlalu lama"}`, true);
  });
}

function tanganiPesan(pesan) {
  switch (pesan.jenis) {
    case "siap":
      siap = true;
      saluranAda = pesan.saluran;
      setStatus(saluranAda ? "Siap." : "Siap. (Di browser ini, perintah tanya belum bisa dipakai.)");
      perbaruiTombol();
      break;
    case "gagal-muat":
      setStatus("Mesin bahasa gagal dimuat. Periksa sambungan internet, lalu muat ulang halaman.", true);
      tambahKeluaran(`Mesin bahasa gagal dimuat: ${pesan.pesan}\n`, "galat");
      break;
    case "keluaran":
      tambahKeluaran(pesan.teks, pesan.saluran === "galat" ? "galat" : "");
      break;
    case "minta-masukan":
      tampilkanFormMasukan(pesan.id);
      setStatus("Program menunggu jawabanmu…");
      break;
    case "masukan-diterima":
      if (jawabanTertunda?.id === pesan.id) lupakanJawaban();
      break;
    case "selesai":
      programSelesai(pesan.hasil, pesan.durasi);
      break;
  }
}

function jalankan() {
  if (!siap || berjalan) return;
  bersihkanKeluaran();
  hapusTandaGalat();
  lupakanJawaban();
  sesi = `${Date.now().toString(36)}-${Math.random().toString(36).slice(2, 8)}`;
  kirimKeServiceWorker({ jenis: "mulai", sesi });
  berjalan = true;
  perbaruiTombol();
  setStatus("Berjalan…");
  pekerja.postMessage({ jenis: "jalankan", kode: el.kode.value, sesi });
}

function hentikan() {
  if (!berjalan) return;
  kirimKeServiceWorker({ jenis: "berhenti", sesi });
  setStatus("Menghentikan…");
  clearTimeout(pengaturPaksa);
  // Mesin memeriksa tombol Hentikan berkala lewat saluran. Bila tidak menjawab (tanpa saluran,
  // atau sedang menghitung sesuatu yang sangat besar), pekerjanya dihentikan paksa lalu disiapkan ulang.
  pengaturPaksa = setTimeout(hentikanPaksa, saluranAda ? 1500 : 0);
}

function hentikanPaksa() {
  if (!berjalan) return;
  pekerja.terminate();
  berjalan = false;
  hapusFormMasukan();
  lupakanJawaban();
  pastikanBarisBaru();
  tambahKeluaran("⏹ Program dihentikan.\n", "info");
  setStatus("Program dihentikan. Menyiapkan ulang mesin…");
  buatPekerja();
}

function programSelesai(hasil, durasi) {
  clearTimeout(pengaturPaksa);
  berjalan = false;
  hapusFormMasukan();
  lupakanJawaban();
  const detik = (durasi / 1000).toLocaleString("id-ID", { maximumFractionDigits: 2 });
  if (!hasil.jenis) {
    setStatus(`Selesai dalam ${detik} detik.`);
  } else if (hasil.jenis === "dihentikan") {
    pastikanBarisBaru();
    tambahKeluaran("⏹ Program dihentikan.\n", "info");
    setStatus("Program dihentikan.");
  } else if (hasil.jenis === "internal" || hasil.jenis === "fatal") {
    pastikanBarisBaru();
    tambahKeluaran(
      `❌ Kesalahan internal: ${hasil.pesan}\n   Ini kemungkinan besar bug pada interpreter. Mohon laporkan di GitHub.\n`,
      "galat",
    );
    setStatus("Terjadi kesalahan internal.", true);
    if (hasil.jenis === "fatal") {
      pekerja.terminate();
      buatPekerja();
    }
  } else {
    pastikanBarisBaru();
    tambahKeluaran(`${hasil.pesan}\n`, "galat");
    if (hasil.baris) {
      tandaiGalat(hasil.baris);
      const tombol = document.createElement("button");
      tombol.type = "button";
      tombol.className = "tombol-baris";
      tombol.textContent = `Lihat baris ${hasil.baris}`;
      tombol.addEventListener("click", () => lompatKeBaris(hasil.baris, hasil.kolom ?? 1));
      el.keluaran.append(tombol);
      gulirKeBawah();
    }
    setStatus(`Program berhenti: ${hasil.jenis}${hasil.baris ? ` di baris ${hasil.baris}` : ""}.`, true);
  }
  perbaruiTombol();
}

el.jalankan.addEventListener("click", jalankan);
el.hentikan.addEventListener("click", hentikan);
el.bersihkan.addEventListener("click", bersihkanKeluaran);
document.addEventListener("keydown", (e) => {
  if (e.key === "Enter" && (e.ctrlKey || e.metaKey)) {
    e.preventDefault();
    if (berjalan) hentikan();
    else jalankan();
  }
});

// =====================================================================
// Contoh program
// =====================================================================

let daftarContoh = [];

el.contoh.addEventListener("change", () => {
  const contoh = daftarContoh.find((c) => c.id === el.contoh.value);
  el.contoh.value = "";
  if (!contoh) return;
  const adaPerubahan = el.kode.value.trim() && el.kode.value !== kodeTerakhirDimuat;
  if (adaPerubahan && !confirm(`Ganti program di editor dengan contoh "${contoh.judul}"?`)) return;
  muatKode(contoh.kode, { simpanDraf: true });
  el.kode.focus({ preventScroll: true });
});

// =====================================================================
// Tautan berbagi: program dimampatkan ke dalam #z=... di alamat halaman
// =====================================================================

function keBase64Url(byte) {
  let biner = "";
  for (let i = 0; i < byte.length; i += 0x8000) biner += String.fromCharCode(...byte.subarray(i, i + 0x8000));
  return btoa(biner).replace(/\+/g, "-").replace(/\//g, "_").replace(/=+$/, "");
}

function dariBase64Url(teks) {
  return Uint8Array.from(atob(teks.replace(/-/g, "+").replace(/_/g, "/")), (c) => c.charCodeAt(0));
}

async function alirkan(byte, aliran) {
  return new Uint8Array(await new Response(new Blob([byte]).stream().pipeThrough(aliran)).arrayBuffer());
}

async function kodeKeHash(kode) {
  const byte = new TextEncoder().encode(kode);
  if (typeof CompressionStream === "function") {
    return `#z=${keBase64Url(await alirkan(byte, new CompressionStream("deflate-raw")))}`;
  }
  return `#k=${keBase64Url(byte)}`;
}

async function hashKeKode(hash) {
  let byte = dariBase64Url(hash.slice(3));
  if (hash.startsWith("#z=")) byte = await alirkan(byte, new DecompressionStream("deflate-raw"));
  return new TextDecoder("utf-8", { fatal: true }).decode(byte);
}

async function muatDariHash() {
  if (!/^#[zk]=./.test(location.hash)) return false;
  try {
    muatKode(await hashKeKode(location.hash), { simpanDraf: false });
    beritahu("Program dari tautan sudah dimuat. Tekan ▶ Jalankan untuk mencobanya.");
    return true;
  } catch {
    beritahu("Tautan program ini rusak atau tidak lengkap.");
    return false;
  }
}

async function bagikan() {
  const hash = await kodeKeHash(el.kode.value);
  const url = `${location.origin}${location.pathname}${hash}`;
  history.replaceState(null, "", hash);
  if (navigator.share && matchMedia("(pointer: coarse)").matches) {
    try {
      await navigator.share({ title: "Program Bahasa Indonesia", url });
      return;
    } catch (e) {
      if (e.name === "AbortError") return;
    }
  }
  try {
    await navigator.clipboard.writeText(url);
    beritahu("Tautan program sudah disalin. Tempelkan di mana saja untuk berbagi.");
  } catch {
    prompt("Salin tautan program ini:", url);
  }
}

el.bagikan.addEventListener("click", bagikan);
window.addEventListener("hashchange", muatDariHash);

// =====================================================================
// Mulai
// =====================================================================

async function ambilJson(nama) {
  const respons = await fetch(`${nama}?v=${VERSI}`);
  if (!respons.ok) throw new Error(`${nama}: status ${respons.status}`);
  return respons.json();
}

async function mulai() {
  if (!(await muatDariHash())) muatKode(baca(KUNCI_DRAF) ?? KODE_AWAL, { simpanDraf: false });

  const [kosakata, contoh] = await Promise.allSettled([ambilJson("kosakata.json"), ambilJson("contoh.json")]);
  if (kosakata.status === "fulfilled") {
    sorot = buatPenyorot(kosakata.value);
    perbaruiTampilan();
  }
  if (contoh.status === "fulfilled") {
    daftarContoh = contoh.value;
    for (const c of daftarContoh) el.contoh.add(new Option(c.judul, c.id));
  }

  await siapkanServiceWorker();
  buatPekerja();
}

mulai();
