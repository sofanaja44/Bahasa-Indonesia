// sw.js — Service worker editor Bahasa Indonesia.
//
// 1. Saluran untuk pekerja.js. Program yang sedang berjalan menunggu di sini secara sinkron:
//      __saluran__/masukan?sesi=..&id=..  sampai halaman mengirim jawaban "tanya"
//      __saluran__/tidur?sesi=..&ms=..     selama "tunggu", atau sampai tombol Hentikan ditekan
//      __saluran__/periksa?sesi=..         apakah tombol Hentikan sudah ditekan?
// 2. Cache, agar editor tetap bisa dibuka tanpa internet setelah kunjungan pertama.
//
// Nilai __...__ diisi oleh bangun.py.

const VERSI = "__VERSI__";
const BERKAS_APLIKASI = ["__BERKAS__"];
const CACHE_APLIKASI = `aplikasi-${VERSI}`;
const CACHE_MESIN = "mesin-__VERSI_MESIN__"; // mesin.wasm: hanya diunduh ulang bila mesinnya berubah
const BATAS_TUNGGU = 20000; // ms; permintaan yang lebih lama dijawab {ulang: true} lalu diulang
const UMUR_SESI = 60 * 60 * 1000;

const masukanMenunggu = new Map(); // "sesi/id" → fungsi penjawab
const jawabanMasuk = new Map(); //    "sesi/id" → {teks, waktu}, bila jawaban tiba sebelum permintaannya
const tidurMenunggu = new Map(); //   sesi → Set fungsi pembangun
const dihentikan = new Map(); //      sesi → waktu tombol Hentikan ditekan

function json(data) {
  return new Response(JSON.stringify(data), {
    headers: { "Content-Type": "application/json", "Cache-Control": "no-store" },
  });
}

function bersihkanSesiLama() {
  const batas = Date.now() - UMUR_SESI;
  for (const [sesi, waktu] of dihentikan) if (waktu < batas) dihentikan.delete(sesi);
  for (const [kunci, jawaban] of jawabanMasuk) if (jawaban.waktu < batas) jawabanMasuk.delete(kunci);
}

async function tanganiSaluran(url) {
  const jenis = url.pathname.slice(url.pathname.lastIndexOf("/") + 1);
  const sesi = url.searchParams.get("sesi") ?? "";

  if (jenis === "periksa") return json({ ok: true, berhenti: dihentikan.has(sesi) });

  if (jenis === "tidur") {
    if (dihentikan.has(sesi)) return json({ berhenti: true });
    const lama = Math.min(Number(url.searchParams.get("ms")) || 0, BATAS_TUNGGU);
    const berhenti = await new Promise((selesai) => {
      const pembangun = tidurMenunggu.get(sesi) ?? new Set();
      tidurMenunggu.set(sesi, pembangun);
      const bangun = (hasil) => {
        clearTimeout(pengatur);
        pembangun.delete(bangun);
        if (pembangun.size === 0) tidurMenunggu.delete(sesi);
        selesai(hasil);
      };
      const pengatur = setTimeout(() => bangun(false), lama);
      pembangun.add(bangun);
    });
    return json({ berhenti });
  }

  if (jenis === "masukan") {
    if (dihentikan.has(sesi)) return json({ berhenti: true });
    const kunci = `${sesi}/${url.searchParams.get("id")}`;
    if (jawabanMasuk.has(kunci)) {
      const { teks } = jawabanMasuk.get(kunci);
      jawabanMasuk.delete(kunci);
      return json({ teks });
    }
    return json(
      await new Promise((selesai) => {
        const pengatur = setTimeout(() => {
          masukanMenunggu.delete(kunci);
          selesai({ ulang: true });
        }, BATAS_TUNGGU);
        masukanMenunggu.set(kunci, (hasil) => {
          clearTimeout(pengatur);
          masukanMenunggu.delete(kunci);
          selesai(hasil);
        });
      }),
    );
  }

  return new Response("Saluran tidak dikenal", { status: 404 });
}

self.addEventListener("message", (event) => {
  const pesan = event.data ?? {};
  if (pesan.jenis === "jawab") {
    const kunci = `${pesan.sesi}/${pesan.id}`;
    const penjawab = masukanMenunggu.get(kunci);
    if (penjawab) penjawab({ teks: pesan.teks });
    else jawabanMasuk.set(kunci, { teks: pesan.teks, waktu: Date.now() });
  } else if (pesan.jenis === "berhenti") {
    dihentikan.set(pesan.sesi, Date.now());
    for (const [kunci, penjawab] of masukanMenunggu) {
      if (kunci.startsWith(`${pesan.sesi}/`)) penjawab({ berhenti: true });
    }
    for (const bangun of tidurMenunggu.get(pesan.sesi) ?? []) bangun(true);
  } else if (pesan.jenis === "mulai") {
    bersihkanSesiLama();
  } else if (pesan.jenis === "klaim") {
    // Halaman yang dimuat dengan Shift+Muat ulang tidak dikendalikan service worker.
    event.waitUntil(self.clients.claim());
  }
});

// ---- Cache ----

self.addEventListener("install", (event) => {
  event.waitUntil(
    caches
      .open(CACHE_APLIKASI)
      .then((cache) => cache.addAll(BERKAS_APLIKASI))
      .then(() => self.skipWaiting()),
  );
});

self.addEventListener("activate", (event) => {
  event.waitUntil(
    (async () => {
      for (const nama of await caches.keys()) {
        if (nama !== CACHE_APLIKASI && nama !== CACHE_MESIN) await caches.delete(nama);
      }
      await self.clients.claim();
    })(),
  );
});

async function dariCacheDulu(permintaan, namaCache) {
  const cache = await caches.open(namaCache);
  const tersimpan = await cache.match(permintaan);
  if (tersimpan) return tersimpan;
  const respons = await fetch(permintaan);
  if (respons.ok) await cache.put(permintaan, respons.clone());
  return respons;
}

self.addEventListener("fetch", (event) => {
  const url = new URL(event.request.url);
  if (url.origin !== self.location.origin) return;
  if (url.pathname.includes("/__saluran__/")) {
    event.respondWith(tanganiSaluran(url));
    return;
  }
  if (event.request.method !== "GET") return;
  if (url.pathname.endsWith("/mesin.wasm")) {
    event.respondWith(dariCacheDulu(event.request, CACHE_MESIN));
    return;
  }
  if (event.request.mode === "navigate" && /\/(index\.html)?$/.test(url.pathname)) {
    // Tautan berbagi memakai #kode, jadi setiap kunjungan memakai index.html yang sama.
    event.respondWith(
      caches
        .open(CACHE_APLIKASI)
        .then((cache) => cache.match(new URL("./", self.registration.scope)))
        .then((tersimpan) => tersimpan ?? fetch(event.request)),
    );
    return;
  }
  event.respondWith(
    caches
      .open(CACHE_APLIKASI)
      .then((cache) => cache.match(event.request))
      .then((tersimpan) => tersimpan ?? fetch(event.request)),
  );
});
