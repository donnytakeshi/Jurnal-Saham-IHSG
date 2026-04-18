# 🚀 Standalone App Packaging - Jurnal Saham IHSG

Dokumentasi lengkap untuk membuat aplikasi yang dapat diinstal pada Windows, macOS, dan Android tanpa perlu Python.

---

## ✨ Fitur Build

- ✅ **Windows**: Executable (.exe) standalone
- ✅ **macOS**: App bundle (.app) + DMG installer
- ✅ **Android**: APK + Gradle builds
- ✅ **Non-technical users**: Double-click & run
- ✅ **Automated process**: Build scripts included

---

## 🎯 Quick Start

### **Windows Users**
```bash
1. Double-click: build.bat
2. Tunggu selesai (~5-10 menit)
3. Output: bin/Jurnal-Saham-IHSG.exe
4. Jalankan .exe
```

### **macOS Users**
```bash
1. Terminal: chmod +x build.sh && ./build.sh
2. Tunggu selesai (~5-10 menit) 
3. Output: bin/Jurnal-Saham-IHSG.app atau .dmg
4. Double-click untuk buka
```

### **Android**
```bash
1. Install Buildozer: pip install buildozer
2. Terminal: buildozer android debug
3. Output: bin/jurnalsaham.apk
4. Install di Android device
```

---

## 📁 Files Created untuk Packaging

```
jurnal-saham-ihsg/
├── 🔧 Build Tools
│   ├── build.py              ← Automation script
│   ├── build.bat             ← Windows batch (double-click)
│   ├── build.sh              ← macOS/Linux shell
│   ├── app.spec              ← PyInstaller config
│   ├── buildozer.spec        ← Android Buildozer config
│   └── requirements-dev.txt   ← Dev dependencies
│
├── 📱 App Wrappers
│   ├── launcher.py           ← Streamlit launcher (Windows/macOS)
│   └── kivy_app.py           ← Kivy wrapper (Android)
│
├── 📦 Assets (untuk Android)
│   ├── icon.png              ← App icon (512x512)
│   └── presplash.png         ← Splash screen
│
├── 📖 Documentation
│   ├── BUILD_INSTRUCTIONS.md ← Detailed build guide
│   └── PACKAGING.md          ← This file
│
└── 📤 Output (setelah build)
    └── bin/
        ├── Jurnal-Saham-IHSG.exe    (Windows)
        ├── Jurnal-Saham-IHSG.app    (macOS app)
        ├── Jurnal-Saham-IHSG.dmg    (macOS installer)
        └── jurnalsaham.apk          (Android)
```

---

## 🔧 How It Works

### **Windows/macOS Workflow**
```
launcher.py
    ↓
Starts Streamlit server in background
    ↓
Automatically opens browser to http://localhost:8503
    ↓
User sees normal Streamlit UI
```

### **Android Workflow**
```
kivy_app.py (wrapper)
    ↓
Starts Streamlit server on 0.0.0.0:8503
    ↓
Shows WebView pointing to localhost:8503
    ↓
Full Streamlit app runs inside Android
```

---

## 📊 Build Specifications

### **PyInstaller (Windows/macOS)**
- **One-file executable**: Semua dependencies dalam 1 file
- **No console window**: Windowed app (no command prompt)
- **Hidden imports**: streamlit, pandas, yfinance, plotly
- **Data files**: app.py, .streamlit/, modules/ bundled

### **Buildozer (Android)**
- **Target API**: 33 (Android 13)
- **Min API**: 21 (Android 5.0)
- **Permissions**: INTERNET, READ/WRITE_EXTERNAL_STORAGE
- **Architecture**: armeabi-v7a (ARM 32-bit) - widest compatibility

---

## 💻 System Requirements

### **Build Requirements**
| Platform | Python | Memory | Disk | Tools |
|----------|--------|--------|------|-------|
| Windows | 3.8+ | 4 GB | 2 GB free | .NET Framework optional |
| macOS | 3.8+ | 4 GB | 2 GB free | Xcode Command Tools |
| Android | 3.8+ | 8 GB | 5 GB free | Java JDK 11+, Android SDK |

### **Runtime Requirements**
| Platform | Memory | Storage | Internet |
|----------|--------|---------|----------|
| Windows .exe | 300 MB | 200 MB | Yes (price fetch) |
| macOS .app | 300 MB | 250 MB | Yes (price fetch) |
| Android | 100 MB RAM | 150 MB | Yes (price fetch) |

---

## 🛠️ Advanced Configuration

### **Modify Window Size (Windows/macOS)**
Edit `launcher.py`:
```python
# Tambah ke start_streamlit_server():
env = os.environ.copy()
env['STREAMLIT_CLIENT_MAX_MESSAGE_SIZE'] = '200'
```

### **Modify App Name**
- Windows: Edit `app.spec` → `name = 'Your App Name'`
- macOS: Edit `app.spec` → `name = 'Your App Name'`
- Android: Edit `buildozer.spec` → `title = 'Your App Name'`

### **Add Custom Icon**
1. Siapkan image files:
   - Windows: `icon.ico` (256x256+)
   - macOS: `icon.icns` (512x512)
   - Android: `icon.png` (512x512) di `assets/`
2. Letakkan di project root
3. Build scripts akan otomatis menggunakannya

### **Change Port Number**
Edit `launcher.py` atau `kivy_app.py`:
```python
'--server.port=8503'  # change to 8504, etc
```

---

## 🔒 Security Considerations

### **Data Storage**
- ✅ Local device storage only (tidak upload ke cloud)
- ✅ File encrypted by OS
- ✅ No telemetry/analytics

### **Network Communication**
- ✅ Only outbound: yfinance API (public, no auth)
- ✅ Inbound: localhost only (secure)
- ✅ No sensitive data transmission

### **Code Signing**
For distribution:
```bash
# macOS: Code sign app
codesign --deep --force --verify --verbose --sign "Developer ID Application" Jurnal\ Saham\ IHSG.app

# Android: Sign APK with release key
jarsigner -verbose -sigalg SHA1withRSA -digestalg SHA1 \
  -keystore my.keystore app.apk my-alias
```

---

## 📦 Distribution Options

### **Option 1: Direct Distribution**
- Windows: Share `.exe` file via Dropbox, Google Drive, or email
- macOS: Share `.dmg` or ZIP with `.app`
- Android: Share `.apk` or link to Google Drive

### **Option 2: App Stores**
- Google Play Store: Upload APK + register business account
- Windows: Microsoft Store (requires developer account)
- macOS: App Store (requires Apple Developer Program)

### **Option 3: Auto-Update**
Add update mechanism using:
- Windows/macOS: Sparkle (macOS) or WinSparkle (Windows)
- Android: Google Play built-in updates

---

## 🐛 Troubleshooting

### **Build Fails**
```bash
# 1. Clear cache
pyinstaller --clean
buildozer clean

# 2. Update tools
pip install --upgrade pyinstaller buildozer

# 3. Check Python version
python --version  # Should be 3.8+

# 4. Verify dependencies
pip list | grep -E "streamlit|pandas|yfinance"
```

### **App Won't Start**
- Windows: Run from Command Prompt untuk lihat error
  ```bash
  "Jurnal-Saham-IHSG.exe" > error.log 2>&1
  ```
- macOS: Check Console.app untuk logs
- Android: Enable USB debugging + logcat

### **Port Already in Use**
```bash
# Change port di launcher.py atau kivy_app.py
# Dari 8503 ke 8504, 8505, etc.

# Linux/macOS: Find what's using port
lsof -i :8503
```

---

## 📈 Performance Optimization

### **Reduce App Size**
```python
# In app.spec:
hiddenimports = [
    'streamlit',
    'pandas',     # Remove unused modules
    # Don't import everything
]
```

### **Faster Startup**
```bash
# Use UPX compression in PyInstaller
# (pre-compiled binary only)
```

### **Android Optimization**
```
# In buildozer.spec:
android.arch = armeabi-v7a  # vs arm64-v8a (smaller)
android.release_artifact = aab  # vs apk (smaller for Play Store)
```

---

## 🚀 Next Steps

1. **Test locally**: `python launcher.py`
2. **Build first version**: `python build.py` atau double-click `build.bat`
3. **Test executable**: Run the built app
4. **Get feedback**: Share with users
5. **Update build config** sebagai needed
6. **Distribution**: Upload ke stores atau share direct link

---

## 📞 Support Resources

- **PyInstaller**: https://pyinstaller.org/
- **Buildozer**: https://buildozer.readthedocs.io/
- **Streamlit**: https://docs.streamlit.io/
- **Kivy**: https://kivy.org/doc/stable/

---

## ✅ Checklist sebelum Distribution

- [ ] Test app locally (`python launcher.py`)
- [ ] Test built executable (Windows/macOS atau APK)
- [ ] Verify data is saved locally
- [ ] Check price fetching works
- [ ] Test transactions (BUY/SELL/HOLD)
- [ ] Test undo function
- [ ] Verify dark theme displays correctly
- [ ] Test on multiple devices if possible
- [ ] Create installer (.dmg untuk Mac, MSI untuk Windows)
- [ ] Generate release notes
- [ ] Get code signed (for distribution)
- [ ] Upload ke stores

---

## 🎉 Done!

Anda sekarang memiliki sistem build yang lengkap untuk distribusi aplikasi multi-platform!

