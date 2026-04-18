# Cleanup Guide

Tujuan: rapihin workspace biar tidak bingung antara project APK (Android) dan versi web/desktop.

## Prinsip

- Script ini **tidak menyentuh**:
  - `.buildozer/` (biar rebuild Android tetap cepat)
  - `data/` (hasil screening & cache user tetap aman)
- Default mode itu **aman**: dipindahkan ke `_archive/<timestamp>/` (bukan dihapus).

## Cara pakai

### Via VS Code Task

Kalau kamu pakai VS Code, kamu bisa jalankan:

- `Terminal` → `Run Task…` → pilih `cleanup: safe (archive)` atau `cleanup: hard (delete)`.

### Mode aman (recommended)

```bash
python3 scripts/cleanup_project.py
```

Hasilnya:
- Folder/berkas artifact (decompile/repack/tmp/log) dipindahkan ke `_archive/`
- `bin/` dipangkas, hanya menyisakan APK terbaru
- `__pycache__/` dan `*.pyc` dihapus

### Mode hard (hapus permanen)

```bash
python3 scripts/cleanup_project.py --hard
```

Catatan:
- Mode ini menghapus folder/berkas artifact (bukan memindahkan).
- Tetap tidak menyentuh `.buildozer/` dan `data/`.

## Folder penting

- `bin/` : output APK terbaru
- `.buildozer/` : cache build Android (jangan dihapus kalau mau build cepat)
- `data/` : hasil screening + cache runtime
- `_archive/` : tempat penyimpanan artifact lama yang sudah dipindahkan
