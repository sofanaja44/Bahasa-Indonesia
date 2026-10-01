// tes_editor.mjs — Uji editor web di Chromium sungguhan (Playwright).
//
//   python web/bangun.py
//   node --test web/tes/tes_editor.mjs

import { after, before, describe, test } from "node:test";
import assert from "node:assert/strict";
import { fileURLToPath } from "node:url";
import { chromium } from "playwright";
import { sajikan } from "./penyaji.mjs";

const SITUS = fileURLToPath(new URL("../situs/", import.meta.url));
const BATAS_MUAT = 120_000;

let server;
let browser;
let konteks; // satu konteks bersama: service worker dan cache mesin dipakai ulang antar-tes

before(async () => {
  server = await sajikan(SITUS);
  browser = await chromium.launch();
  konteks = await browser.newContext({ permissions: ["clipboard-read", "clipboard-write"] });
});

after(async () => {
  await browser?.close();
  await server?.tutup();
});

async function bukaEditor({ hash = "", konteksSendiri } = {}) {
  const page = await (konteksSendiri ?? konteks).newPage();
  const galat = [];
  page.on("pageerror", (e) => galat.push(e.message));
  await page.goto(server.url + hash);
  await tungguStatus(page, "Siap", BATAS_MUAT);
  return { page, galat };
}

function tungguStatus(page, awalan, timeout = 15_000) {
  return page.waitForFunction((a) => document.getElementById("status").textContent.startsWith(a), awalan, {
    timeout,
  });
}

async function tulisKode(page, kode) {
  await page.evaluate((k) => {
    const ta = document.getElementById("kode");
    ta.value = k;
    ta.dispatchEvent(new Event("input"));
  }, kode);
}

async function jalankan(page, kode) {
  if (kode !== undefined) await tulisKode(page, kode);
  await page.click("#tombol-jalankan");
}

async function jawab(page, teks) {
  await page.waitForSelector(".form-masukan input");
  await page.fill(".form-masukan input", teks);
  await page.keyboard.press("Enter");
}

const keluaran = (page) => page.textContent("#keluaran");

describe("menjalankan program", () => {
  test("keluaran tampil di panel keluaran", async () => {
    const { page, galat } = await bukaEditor();
    await jalankan(page, 'tampilkan 1 ditambah 2\ncetak "tanpa "\ntampilkan "pindah baris"');
    await tungguStatus(page, "Selesai");
    assert.equal(await keluaran(page), "3\ntanpa pindah baris\n");
    assert.deepEqual(galat, []);
    await page.close();
  });

  test("tanya menunggu jawaban dari kotak masukan", async () => {
    const { page } = await bukaEditor();
    await jalankan(page, 'buat nama adalah tanya "Siapa namamu? "\ntampilkan format"Halo, {nama}!"');
    await jawab(page, "Sari");
    await tungguStatus(page, "Selesai");
    assert.equal(await keluaran(page), "Siapa namamu? Sari\nHalo, Sari!\n");
    await page.close();
  });

  test("tanya angka bertanya ulang sampai jawabannya angka", async () => {
    const { page } = await bukaEditor();
    await jalankan(page, 'buat umur adalah tanya angka "Umur? "\ntampilkan umur ditambah 1');
    await jawab(page, "sepuluh");
    await jawab(page, "10");
    await tungguStatus(page, "Selesai");
    assert.equal(await keluaran(page), "Umur? sepuluh\nTolong jawab dengan angka.\nUmur? 10\n11\n");
    await page.close();
  });

  test("tunggu benar-benar menunggu", async () => {
    const { page } = await bukaEditor();
    const mulai = Date.now();
    await jalankan(page, 'tampilkan "a"\ntunggu 0.5 detik\ntampilkan "b"');
    await tungguStatus(page, "Selesai");
    assert.ok(Date.now() - mulai >= 500, "seharusnya menunggu setengah detik");
    assert.equal(await keluaran(page), "a\nb\n");
    await page.close();
  });

  test("berkas bisa ditulis lalu dibaca kembali", async () => {
    const { page } = await bukaEditor();
    await jalankan(page, 'impor berkas\nberkas.tulis("catatan.txt", "Halo berkas")\ntampilkan berkas.baca("catatan.txt")');
    await tungguStatus(page, "Selesai");
    assert.equal(await keluaran(page), "Halo berkas\n");
    await page.close();
  });

  test("keluaran yang sangat banyak tidak membuat halaman macet", async () => {
    const { page } = await bukaEditor();
    await jalankan(page, 'untuk i dari 1 sampai 30000:\n    tampilkan "baris nomor", i');
    await tungguStatus(page, "Selesai", 60_000);
    const teks = await keluaran(page);
    assert.ok(teks.endsWith("baris nomor 30000\n"));
    assert.ok(teks.length <= 220_000, `keluaran di layar seharusnya dipangkas (${teks.length} karakter)`);
    await page.close();
  });
});

describe("tombol Hentikan", () => {
  test("menghentikan program yang sedang menunggu (tunggu)", async () => {
    const { page } = await bukaEditor();
    await jalankan(page, 'selama benar lakukan:\n    tampilkan "tik"\n    tunggu 1 detik');
    await page.waitForFunction(() => document.getElementById("keluaran").textContent.includes("tik"));
    const mulai = Date.now();
    await page.click("#tombol-hentikan");
    await tungguStatus(page, "Program dihentikan.", 3000);
    assert.ok(Date.now() - mulai < 1000, "berhenti seketika, tanpa menunggu 1 detik penuh");
    assert.match(await keluaran(page), /tik\n⏹ Program dihentikan\.\n$/);
    assert.equal(await page.isVisible("#tombol-jalankan"), true);
    await page.close();
  });

  test("menghentikan program yang menunggu jawaban tanya", async () => {
    const { page } = await bukaEditor();
    await jalankan(page, 'buat x adalah tanya "Jawab: "');
    await page.waitForSelector(".form-masukan input");
    await page.click("#tombol-hentikan");
    await tungguStatus(page, "Program dihentikan.", 3000);
    assert.equal(await page.$(".form-masukan"), null);
    await page.close();
  });

  test("menghentikan perulangan yang terus menampilkan keluaran", async () => {
    const { page } = await bukaEditor();
    await jalankan(page, 'selama benar lakukan:\n    tampilkan "lagi"');
    await page.waitForFunction(() => document.getElementById("keluaran").textContent.length > 1000);
    await page.click("#tombol-hentikan");
    await tungguStatus(page, "Program dihentikan.", 3000);
    await page.close();
  });

  test("menghentikan perulangan tanpa keluaran tanpa menyiapkan ulang mesin", async () => {
    const { page } = await bukaEditor();
    await jalankan(page, "buat x adalah 0\nselama benar lakukan:\n    ubah x menjadi x ditambah 1");
    await page.waitForTimeout(300);
    const mulai = Date.now();
    await page.click("#tombol-hentikan");
    await tungguStatus(page, "Program dihentikan.", 3000);
    assert.ok(Date.now() - mulai < 1000, "mesin memeriksa tombol Hentikan sendiri, tanpa dihentikan paksa");
    assert.equal(await page.textContent("#status"), "Program dihentikan.");
    await jalankan(page, 'tampilkan "jalan lagi"');
    await tungguStatus(page, "Selesai");
    assert.equal(await keluaran(page), "jalan lagi\n");
    await page.close();
  });

  test("perhitungan yang sangat lama dihentikan paksa, lalu mesin disiapkan ulang", async () => {
    const { page } = await bukaEditor();
    // Satu perhitungan bilangan raksasa tidak sempat memeriksa tombol Hentikan.
    await jalankan(page, "impor matematika\nbuat x adalah matematika.faktorial(1000000)\ntampilkan panjang(ubah_teks(x))");
    await page.waitForTimeout(300);
    await page.click("#tombol-hentikan");
    await tungguStatus(page, "Program dihentikan", 5000);
    await tungguStatus(page, "Siap", BATAS_MUAT);
    await jalankan(page, 'tampilkan "jalan lagi"');
    await tungguStatus(page, "Selesai");
    assert.equal(await keluaran(page), "jalan lagi\n");
    await page.close();
  });
});

describe("kesalahan", () => {
  test("pesan kesalahan tampil dan barisnya ditandai di editor", async () => {
    const { page } = await bukaEditor();
    await jalankan(page, 'tampilkan "satu"\ntampilkan "dua"\ntampilkan skor');
    await tungguStatus(page, "Program berhenti: KesalahanNama di baris 3");
    const teks = await keluaran(page);
    assert.match(teks, /satu\ndua\n❌ KesalahanNama pada baris 3/);
    const ditandai = () => page.$$eval("#sorotan .b", (b) => b.map((e, i) => e.classList.contains("galat") && i + 1).filter(Boolean));
    assert.deepEqual(await ditandai(), [3]);

    await page.click(".tombol-baris");
    const kursor = await page.$eval("#kode", (e) => e.value.slice(0, e.selectionStart).split("\n").length);
    assert.equal(kursor, 3);

    await page.type("#kode", "x"); // mengubah kode menghapus tanda kesalahan
    assert.deepEqual(await ditandai(), []);
    await page.close();
  });

  test("rekursi tak berujung tidak merusak mesin di browser", async () => {
    const { page } = await bukaEditor();
    await jalankan(page, "fungsi f(n):\n    kembalikan f(n ditambah 1)\nf(1)");
    await tungguStatus(page, "Program berhenti: KesalahanTumpukan");
    await jalankan(page, 'tampilkan "masih sehat"');
    await tungguStatus(page, "Selesai");
    assert.equal(await keluaran(page), "masih sehat\n");
    await page.close();
  });
});

describe("editor", () => {
  test("Enter menjaga jorokan dan menambahnya setelah titik dua", async () => {
    const { page } = await bukaEditor();
    await tulisKode(page, "");
    await page.click("#kode");
    await page.keyboard.type("jika benar:");
    await page.keyboard.press("Enter");
    await page.keyboard.type("tampilkan 1");
    await page.keyboard.press("Enter");
    await page.keyboard.type("tampilkan 2");
    assert.equal(await page.inputValue("#kode"), "jika benar:\n    tampilkan 1\n    tampilkan 2");
    await page.keyboard.press("Shift+Tab");
    assert.equal(await page.inputValue("#kode"), "jika benar:\n    tampilkan 1\ntampilkan 2");
    await page.close();
  });

  test("pewarnaan kode sejajar dengan teks yang diketik", async () => {
    const { page } = await bukaEditor();
    await tulisKode(page, 'jika umur lebih dari 17, maka tampilkan "dewasa"');
    const warna = await page.$$eval("#sorotan span", (s) => s.map((e) => [e.className, e.textContent]));
    assert.deepEqual(warna.slice(0, 3), [
      ["s-kunci", "jika"],
      ["s-operator", "lebih dari"],
      ["s-angka", "17"],
    ]);
    const baris = await page.$$eval("#sorotan .b", (b) => b.map((e) => e.textContent));
    assert.equal(baris.join("\n"), await page.inputValue("#kode"));

    // Baris panjang terbungkus di posisi yang sama: tinggi isi textarea = tinggi lapisan warna.
    // (Isinya dibuat lebih tinggi dari kotak editor, karena scrollHeight paling kecil setinggi kotaknya.)
    const panjang = `tampilkan "${"kata ".repeat(80)}"\n# ${"komentar ".repeat(40)}\n\n`;
    await tulisKode(page, `${panjang.repeat(6)}selesai`);
    const [isiTextarea, isiWarna] = await page.evaluate(() => {
      const ta = document.getElementById("kode");
      const gaya = getComputedStyle(ta);
      return [ta.scrollHeight - parseFloat(gaya.paddingTop) - parseFloat(gaya.paddingBottom),
              document.getElementById("sorotan").offsetHeight];
    });
    assert.ok(Math.abs(isiTextarea - isiWarna) <= 1, `textarea ${isiTextarea}px, warna ${isiWarna}px`);
    await page.close();
  });

  test("contoh program bisa dibuka dari menu", async () => {
    const { page } = await bukaEditor();
    await tulisKode(page, "");
    await page.selectOption("#pilih-contoh", "tebak_angka");
    assert.match(await page.inputValue("#kode"), /angka acak dari 1 sampai 100/);
    await page.close();
  });

  test("draf tersimpan dan muncul lagi setelah halaman dimuat ulang", async () => {
    const { page } = await bukaEditor();
    await page.fill("#kode", 'tampilkan "draf saya"');
    await page.waitForTimeout(500);
    await page.reload();
    await tungguStatus(page, "Siap", BATAS_MUAT);
    assert.equal(await page.inputValue("#kode"), 'tampilkan "draf saya"');
    await page.close();
  });

  test("tidak ada gulir ke samping di layar HP", async () => {
    const hp = await browser.newContext({ viewport: { width: 360, height: 740 }, isMobile: true, hasTouch: true });
    const { page } = await bukaEditor({ konteksSendiri: hp });
    const lebar = await page.evaluate(() => [document.documentElement.scrollWidth, innerWidth]);
    assert.ok(lebar[0] <= lebar[1], `halaman lebih lebar dari layar: ${lebar}`);
    assert.equal(await page.isVisible(".bilah-ketik"), true);
    await hp.close();
  });
});

describe("berbagi dan tanpa internet", () => {
  test("tautan berbagi memuat program yang sama tanpa menimpa draf", async () => {
    const kode = 'buat buah adalah ["mangga", "rambutan"]\ntampilkan "Aku suka", buah[0] # 🥭';
    const { page } = await bukaEditor();
    await page.fill("#kode", 'tampilkan "draf lama"');
    await page.waitForTimeout(500);
    await tulisKode(page, kode);
    await page.click("#tombol-bagikan");
    await page.waitForFunction(() => location.hash.startsWith("#z="));
    const url = await page.evaluate(() => navigator.clipboard.readText());
    assert.ok(url.includes("#z="), url);
    await tulisKode(page, 'tampilkan "draf lama"'); // kembalikan draf sebelum membuka tautan
    await page.waitForTimeout(500);

    const { page: halaman2 } = await bukaEditor({ hash: new URL(url).hash });
    assert.equal(await halaman2.inputValue("#kode"), kode);
    const draf = await halaman2.evaluate(() => localStorage.getItem("bahasa-indonesia:draf"));
    assert.equal(draf, 'tampilkan "draf lama"');
    await page.close();
    await halaman2.close();
  });

  test("editor tetap bisa dibuka dan menjalankan program tanpa internet", async () => {
    const sendiri = await browser.newContext();
    const { page } = await bukaEditor({ konteksSendiri: sendiri });
    await sendiri.setOffline(true);
    await page.reload();
    await tungguStatus(page, "Siap", BATAS_MUAT);
    await jalankan(page, 'tampilkan "tanpa internet"');
    await tungguStatus(page, "Selesai");
    assert.equal(await keluaran(page), "tanpa internet\n");
    await sendiri.close();
  });
});
