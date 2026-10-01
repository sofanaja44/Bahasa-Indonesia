// extension.js — Ekstensi VS Code untuk Bahasa Pemrograman Indonesia.
// Pewarnaan kode, potongan kode, dan pengaturan jorokan ada di package.json;
// berkas ini menambahkan perintah "Jalankan Program" (tombol ▶ di pojok editor, atau Ctrl+F5).

const vscode = require("vscode");

const NAMA_TERMINAL = "Bahasa Indonesia";

function terminal() {
  return vscode.window.terminals.find((t) => t.name === NAMA_TERMINAL && t.exitStatus === undefined)
    ?? vscode.window.createTerminal(NAMA_TERMINAL);
}

async function jalankan(uri) {
  const dokumen = uri instanceof vscode.Uri
    ? await vscode.workspace.openTextDocument(uri)
    : vscode.window.activeTextEditor?.document;
  if (!dokumen) {
    vscode.window.showWarningMessage("Buka berkas program .id terlebih dahulu.");
    return;
  }
  if (dokumen.isUntitled) {
    vscode.window.showWarningMessage("Simpan program sebagai berkas .id terlebih dahulu.");
    return;
  }
  if (dokumen.isDirty && !(await dokumen.save())) return;

  const perintah = vscode.workspace.getConfiguration("bahasaIndonesia").get("perintah") || "indonesia";
  const t = terminal();
  t.show(true);
  t.sendText(`${perintah} "${dokumen.uri.fsPath}"`);
}

function activate(context) {
  context.subscriptions.push(vscode.commands.registerCommand("bahasaIndonesia.jalankan", jalankan));
}

function deactivate() {}

module.exports = { activate, deactivate };
