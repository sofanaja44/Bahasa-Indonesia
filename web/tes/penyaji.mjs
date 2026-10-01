// penyaji.mjs — Server statis kecil untuk menguji web/situs/ di localhost.
import http from "node:http";
import fs from "node:fs";
import path from "node:path";

const JENIS = {
  ".html": "text/html; charset=utf-8",
  ".js": "text/javascript; charset=utf-8",
  ".mjs": "text/javascript; charset=utf-8",
  ".css": "text/css; charset=utf-8",
  ".json": "application/json",
  ".webmanifest": "application/manifest+json",
  ".wasm": "application/wasm",
  ".zip": "application/zip",
  ".svg": "image/svg+xml",
  ".png": "image/png",
};

/** Sajikan folder `akar`; hasilnya {url, tutup(), permintaan} (permintaan: daftar jalur yang diminta). */
export function sajikan(akar) {
  const permintaan = [];
  const server = http.createServer((req, res) => {
    const jalur = decodeURIComponent(new URL(req.url, "http://x").pathname);
    permintaan.push(jalur);
    let berkas = path.join(akar, jalur);
    if (!berkas.startsWith(akar)) return res.writeHead(403).end();
    if (jalur.endsWith("/")) berkas = path.join(berkas, "index.html");
    fs.readFile(berkas, (galat, isi) => {
      if (galat) return res.writeHead(404, { "Content-Type": "text/plain" }).end("Tidak ditemukan");
      res.writeHead(200, { "Content-Type": JENIS[path.extname(berkas)] ?? "application/octet-stream" }).end(isi);
    });
  });
  return new Promise((selesai) => {
    server.listen(0, "127.0.0.1", () => {
      selesai({
        url: `http://localhost:${server.address().port}/`,
        permintaan,
        tutup: () => new Promise((ok) => server.close(ok)),
      });
    });
  });
}
