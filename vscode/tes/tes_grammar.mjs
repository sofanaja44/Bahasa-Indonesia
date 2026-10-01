// tes_grammar.mjs — Uji grammar pewarnaan kode dengan mesin TextMate yang sama dengan VS Code.
//
//   cd vscode && npm ci && node --test tes/tes_grammar.mjs

import { test } from "node:test";
import assert from "node:assert/strict";
import fs from "node:fs";
import { createRequire } from "node:module";
import { fileURLToPath } from "node:url";

const require = createRequire(import.meta.url);
const vsctm = require("vscode-textmate");
const oniguruma = require("vscode-oniguruma");

const BERKAS = fileURLToPath(new URL("../syntaxes/indonesia.tmLanguage.json", import.meta.url));
await oniguruma.loadWASM(fs.readFileSync(require.resolve("vscode-oniguruma/release/onig.wasm")).buffer);
const registri = new vsctm.Registry({
  onigLib: Promise.resolve({
    createOnigScanner: (pola) => new oniguruma.OnigScanner(pola),
    createOnigString: (teks) => new oniguruma.OnigString(teks),
  }),
  loadGrammar: async (nama) =>
    nama === "source.indonesia" ? vsctm.parseRawGrammar(fs.readFileSync(BERKAS, "utf8"), BERKAS) : null,
});
const grammar = await registri.loadGrammar("source.indonesia");

/** Daftar [teks, cakupan terdalam] untuk setiap token. */
function token(kode) {
  let keadaan = vsctm.INITIAL;
  const hasil = [];
  for (const baris of kode.split("\n")) {
    const r = grammar.tokenizeLine(baris, keadaan);
    for (const t of r.tokens) hasil.push([baris.slice(t.startIndex, t.endIndex), t.scopes.at(-1)]);
    keadaan = r.ruleStack;
  }
  return hasil;
}

function cakupan(kode, potongan, ke = 0) {
  const cocok = token(kode).filter(([teks]) => teks === potongan || teks.trim() === potongan);
  assert.ok(cocok[ke], `token "${potongan}" tidak ditemukan di: ${JSON.stringify(token(kode))}`);
  return cocok[ke][1];
}

test("kata kunci, angka, dan nilai", () => {
  assert.equal(cakupan("buat umur adalah 17", "buat"), "storage.type.indonesia");
  assert.equal(cakupan("buat umur adalah 17", "adalah"), "keyword.control.indonesia");
  assert.equal(cakupan("buat umur adalah 17", "17"), "constant.numeric.indonesia");
  assert.equal(cakupan("buat umur adalah 17", "umur"), "source.indonesia");
  assert.equal(cakupan("jika hujan adalah benar, maka berhenti", "benar"), "constant.language.indonesia");
  assert.equal(cakupan("tampilkan diri.nama", "diri"), "variable.language.indonesia");
  assert.equal(cakupan("bilangan umur = 17", "bilangan"), "support.type.indonesia");
});

test("frasa dibaca sebagai satu kesatuan, yang terpanjang lebih dulu", () => {
  const kode = 'jika umur lebih dari atau sama dengan 17, maka tampilkan "KTP"';
  assert.equal(cakupan(kode, "lebih dari atau sama dengan"), "keyword.operator.word.indonesia");
  assert.equal(cakupan("atau jika nilai kurang dari 5:", "atau jika"), "keyword.control.indonesia");
  assert.equal(cakupan("buat jam adalah jam sekarang", "jam sekarang"), "constant.language.indonesia");
  assert.equal(cakupan("buat jam adalah jam sekarang", "jam"), "source.indonesia");
  assert.equal(cakupan("untuk setiap buah dalam keranjang, lakukan:", "untuk setiap"), "keyword.control.indonesia");
});

test("kata kerja natural hanya diwarnai di awal perintah", () => {
  assert.equal(cakupan("ubah umur menjadi umur ditambah 1", "ubah"), "keyword.control.indonesia");
  assert.equal(cakupan("ubah umur menjadi umur ditambah 1", "menjadi"), "keyword.control.indonesia");
  assert.equal(cakupan("ubah umur menjadi umur ditambah 1", "ditambah"), "keyword.operator.word.indonesia");
  assert.equal(cakupan("    tambahkan 1 ke skor", "ke"), "keyword.control.indonesia");
  assert.equal(cakupan("tunggu 1 detik", "detik"), "keyword.control.indonesia");
  assert.equal(cakupan("ulangi 3 kali:", "kali"), "keyword.control.indonesia");
  assert.equal(cakupan("buat menjadi adalah 1", "menjadi"), "source.indonesia");
  assert.equal(cakupan("buat ke adalah 2", "ke"), "source.indonesia");
});

test("tanya dan tanya angka", () => {
  const kode = 'buat umur adalah tanya angka "Berapa umurmu? "';
  assert.equal(cakupan(kode, "tanya"), "keyword.control.indonesia");
  assert.equal(cakupan(kode, "angka"), "keyword.control.indonesia");
  assert.equal(cakupan("buat tanya adalah 3", "tanya"), "source.indonesia");
});

test("teks, teks format, dan komentar", () => {
  assert.equal(cakupan('tampilkan "Halo # bukan komentar"', '"'), "punctuation.definition.string.begin.indonesia");
  assert.equal(cakupan('tampilkan "Halo # bukan komentar"', "Halo # bukan komentar"), "string.quoted.double.indonesia");
  assert.equal(cakupan('tampilkan f"Halo {nama}!"', "f"), "storage.type.string.indonesia");
  assert.equal(cakupan('tampilkan format"Halo {nama}!"', "nama"), "meta.interpolation.indonesia");
  assert.equal(cakupan('tampilkan "a\\nb"', "\\n"), "constant.character.escape.indonesia");
  assert.equal(cakupan("tampilkan 1 # catatan", "# catatan"), "comment.line.number-sign.indonesia");
  const blok = '"""\nkomentar beberapa baris\n"""\ntampilkan 1';
  assert.equal(cakupan(blok, "komentar beberapa baris"), "comment.block.indonesia");
  assert.equal(cakupan(blok, "tampilkan"), "keyword.control.indonesia");
});

test("definisi fungsi dan kelas, serta fungsi bawaan", () => {
  assert.equal(cakupan("fungsi sapa(nama):", "sapa"), "entity.name.function.indonesia");
  assert.equal(cakupan("kelas Hewan:", "Hewan"), "entity.name.type.class.indonesia");
  assert.equal(cakupan("tampilkan panjang(daftar)", "panjang"), "support.function.builtin.indonesia");
  assert.equal(cakupan("buat panjang adalah 3", "panjang"), "source.indonesia");
});
