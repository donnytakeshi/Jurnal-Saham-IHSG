# 📦 Build Instructions - Jurnal Saham IHSG

Panduan lengkap untuk membuat aplikasi standalone untuk Windows, macOS, dan Android.

---

## 🖥️ **Opsi A: QUICK BUILD (Recommended untuk Windows/Mac)**

Untuk non-technical users yang ingin langsung jalan tanpa compile.

### **Windows**
1. **Download file executable** yang sudah ada di `bin/` folder
2. **Double-click** `Jurnal-Saham-IHSG.exe`
3. Browser otomatis membuka di `http://localhost:8503`
4. ✅ Done! Tidak perlu install Python

### **macOS**
1. **Download** `Jurnal-Saham-IHSG.app` dari `bin/` folder
2. **Buka Finder** → arahkan ke Downloads
3. **Double-click** aplikasi atau tarik ke Applications folder
4. Browser otomatis membuka
5. ✅ Done!

### **Android**
1. [Download APK](bin/jurnal-saham-ihsg.apk) ke device
2. Buka File Manager → cari file APK
3. Tap untuk install
4. Buka aplikasi dari home screen
5. ✅ App membuka Streamlit di WebView

---

## 🔧 **Opsi B: MANUAL BUILD (Untuk Development/Custom)**

### **Prerequisites**
Pastikan sudah install:
```bash
# macOS / Linux
pip install pyinstaller buildozer cython

# Windows
pip install pyinstaller
```

### **Untuk Windows**
```bash
# 1. Install PyInstaller
pip install pyinstaller

# 2. Prepare files
# - Pastikan app.py, launcher.py, .streamlit/ ada di folder ini
# - Siapkan icon.ico (opsional)

# 3. Build executable
pyinstaller launcher.py \
  --name "Jurnal-Saham-IHSG" \
  --onefile \
  --windowed \
  --add-data "app.py:." \
  --add-data ".streamlit:.streamlit" \
  --add-data "modules:modules" \
  --hidden-import=streamlit \
  --hidden-import=pandas \
  --hidden-import=yfinance \
  --icon=icon.ico

# 4. Output
# File executable ada di: dist/Jurnal-Saham-IHSG.exe
```

### **Untuk macOS**
```bash
# 1. Install dependencies
pip install pyinstaller

# 2. Build app bundle
pyinstaller launcher.py \
  --name "Jurnal Saham IHSG" \
  --onefile \
  --windowed \
  --add-data "app.py:." \
  --add-data ".streamlit:.streamlit" \
  --add-data "modules:modules" \
  --hidden-import=streamlit \
  --hidden-import=pandas \
  --hidden-import=yfinance

# 3. Code sign (opsional, untuk distribution)
codesign --deep --force --verify --verbose \
  --sign "Developer ID Application" \
  dist/"Jurnal\ Saham\ IHSG.app"

# 4. Create DMG installer
hdiutil create -volname "Jurnal Saham IHSG" \
  -srcfolder dist \
  -ov -format UDZO jurnal-saham-ihsg.dmg
```

### **Untuk Android (Buildozer)**
```bash
# 1. Install Buildozer & dependencies
pip install buildozer
# Jika di Mac, perlu Android SDK juga:
# brew install android-sdk

# 2. Edit buildozer.spec sesuai kebutuhan

# 3. Build APK (pertama kali butuh waktu lama)
./build_android.sh

# 4. Output APK
# File ada di: bin/jurnalsaham-0.1.0-arm64-v8a_armeabi-v7a-debug.apk

# 5. Untuk release APK
./build_android_release.sh
# File: bin/jurnalsaham-0.1.0-arm64-v8a_armeabi-v7a-release.apk
```

---

## 📱 **Struktur File untuk Build**

```
jurnal-saham-ihsg/
├── launcher.py              # Entry point
├── kivy_app.py              # Android wrapper
├── app.py                   # Main Streamlit app
├── app.spec                 # PyInstaller config
├── buildozer.spec           # Android build config
├── .streamlit/
│   └── config.toml          # Streamlit config (dark theme)
├── modules/
│   ├── __init__.py
│   ├── data_fetcher.py
│   ├── bandarmology.py
│   └── stockbit_fetcher.py
├── assets/                  # Icons & splash (untuk Android)
│   ├── icon.png             # 512x512 PNG
│   └── presplash.png        # Splash screen
├── bin/                     # Output folder
│   ├── Jurnal-Saham-IHSG.exe
│   ├── Jurnal-Saham-IHSG.app
│   └── jurnalsaham.apk
└── requirements.txt
```

---

## 🎯 **Troubleshooting**

### **Windows: "tidak bisa dibuka"**
- Klik kanan → Properties → Unblock checkbox
- Atau: buka dari Command Prompt untuk lihat error: 
  ```bash
  "Jurnal-Saham-IHSG.exe"
  ```

### **macOS: "aplikasi tidak bisa dibuka"**
- Klik kanan → Open → Allow
- Atau di System Preferences → Security & Privacy

### **Android: Build error**
```bash
# Jika ada error, coba:
buildozer android debug -- --permission INTERNET
buildozer android debug -- --permission WRITE_EXTERNAL_STORAGE

# Atau clear cache:
buildozer clean
buildozer android debug
```

### **App startup slowness**
- Pertama kali buka agak lama karena proses Streamlit
- Reloads lebih cepat (cache system)
- Normal behavior

---

## 📊 **File Size Reference**

| Platform | Size | Dependencies |
|----------|------|--------------|
| Windows .exe | ~150-200 MB | Python + libraries bundled |
| macOS .app | ~200-250 MB | Self-contained |
| Android APK | ~80-120 MB | Optimized for mobile |

---

## 🚀 **Distribution**

### **Windows**
- Buat installer menggunakan NSIS atau InnoSetup
- Upload .exe ke GitHub Releases
- Atau buat .msi (Microsoft Installer)

### **macOS**
- Distribusi sebagai `.dmg` file
- Atau `.app` dalam ZIP
- Notarize untuk Gatekeeper (Apple requirement)

### **Android**
- Publish ke Google Play Store (perlu dev account)
- Atau distribute sebagai `.apk` file langsung
- Signer dengan release key untuk production

---

## 🔐 **Security Notes**

- Data trading journal tersimpan lokal di device
- Tidak ada data yang dikirim ke server
- Hanya fetch harga saham dari yfinance (public API)
- Internet diperlukan untuk real-time price updates

---

## 💡 **Tips**

1. **Test locally dulu**: `python launcher.py` atau `python kivy_app.py`
2. **Verify dependencies**: `pip list | grep -E "streamlit|pandas|yfinance"`
3. **Keep app.spec & buildozer.spec updated** saat ada perubahan code
4. **Untuk production**: gunakan release build dengan signing key

---

## 📞 **Need Help?**

- **PyInstaller errors**: Check hidden-import list
- **Buildozer issues**: Update Android SDK/NDK
- **Streamlit behavior**: Modify `.streamlit/config.toml`

