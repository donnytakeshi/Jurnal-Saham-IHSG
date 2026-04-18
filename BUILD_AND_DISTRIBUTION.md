# 📦 Build & Distribution Guide

## Current Status

### ✅ macOS
- **Status**: ✅ **READY TO DOWNLOAD**
- **File**: `bin/Jurnal-Saham-IHSG.dmg` (86 MB)
- **Type**: Installer (.dmg) + App Bundle (.app)
- **What it is**: Streamlit-based web app (browser-based)

### ⚙️ Windows
- **Status**: 🔄 **Can be built** (not pre-built)
- **Instructions**: See "Build Windows" below
- **Time**: ~15 minutes to build

### 🤖 Android
- **Status**: 🔄 **Can be built** (requires special setup)
- **Instructions**: See "Build Android" below
- **Time**: ~30+ minutes, needs Java/Gradle

### 🖥️ Desktop App (NEW)
- **Status**: ✅ **Source code ready** (Python files)
- **Type**: Kivy desktop app (standalone, no browser)
- **How to use**: `python3 desktop_app.py` or `./run_desktop.sh`

---

## 🍎 macOS - Download & Install

### What You Get
- **Jurnal-Saham-IHSG.dmg** - Installer file
- Auto-opens Streamlit app in browser
- Works offline after first setup

### Download Options

#### Option 1: Direct Download (Recommended)
```bash
# Navigate to bin/ folder
cd bin/

# Download/copy the DMG file
# File: Jurnal-Saham-IHSG.dmg (86 MB)
```

#### Option 2: Command Line Download
```bash
# From project root
cp bin/Jurnal-Saham-IHSG.dmg ~/Downloads/

# Or share/upload to cloud:
# - Google Drive
# - Dropbox
# - GitHub Releases
```

### Installation Steps

1. **Download DMG file**
   - Location: `bin/Jurnal-Saham-IHSG.dmg`

2. **Double-click to mount**
   - DMG mounts as virtual drive
   - Shows app icon

3. **Drag app to Applications**
   - Open Finder
   - Drag `Jurnal-Saham-IHSG` to Applications folder

4. **Run app**
   - Applications → Jurnal-Saham-IHSG
   - Or spotlight: Cmd+Space → "Jurnal Saham"

5. **First Launch**
   - App starts Streamlit server
   - Browser opens automatically
   - ✅ Ready to use!

### System Requirements
- macOS 10.13+
- ~500 MB disk space
- 4+ GB RAM (recommended)
- Internet (optional, mostly works offline)

---

## 🪟 Windows - Build Instructions

### What You'll Get
- `Jurnal-Saham-IHSG.exe` - Standalone executable
- Single file, easy to distribute
- No Python installation needed

### Prerequisites
```
✅ Python 3.10+ (from python.org)
✅ pip (comes with Python)
✅ Git (optional, for downloading code)
```

### Build Steps (Windows)

#### 1. Prepare Project
```bash
# Clone/download project
cd C:\Users\YourName\Desktop
git clone <project-url>
cd jurnal-saham-ihsg

# Or if you have the folder already:
cd jurnal-saham-ihsg
```

#### 2. Create Virtual Environment
```bash
python -m venv venv
venv\Scripts\activate
```

#### 3. Install Dependencies
```bash
pip install --upgrade pip
pip install -r requirements.txt
pip install pyinstaller
```

#### 4. Run Build
```bash
python build.py
```

#### 5. Get Your Executable
```
Output folder: bin\Jurnal-Saham-IHSG.exe
Size: ~150-200 MB
```

#### 6. Test It
```bash
# Single click from Explorer, or:
.\bin\Jurnal-Saham-IHSG.exe
```

### Distribution
```bash
# Share the file:
- Email attachment
- Google Drive link
- DropBox
- GitHub Releases
- USB drive
```

### Troubleshooting Windows Build

**Error: "python is not recognized"**
```bash
# Make sure Python is in PATH
python --version

# If not found, reinstall Python with "Add to PATH" checked
```

**Error: "permission denied"**
```bash
# Run Command Prompt as Administrator
# Then run: python build.py
```

**Build takes too long**
```bash
# Normal: 5-15 minutes
# Check: disk space (need 2+ GB temp)
# Solution: Remove build/ folder and retry
```

**Antivirus blocks .exe**
```bash
# Whitelist build process
# Or sign .exe with certificate (advanced)
```

---

## 🤖 Android - Build Instructions

### What You Get
- `Jurnal-Saham-IHSG.apk` - Android app
- Install on phones/tablets

### Prerequisites (Complex Setup!)
```
✅ Python 3.10+
✅ Java Development Kit (JDK) 11+
✅ Android SDK
✅ Buildozer
✅ Cython
✅ Kivy
```

### Quick Setup (For Android)

#### 1. Install Build Tools (macOS/Linux only)
```bash
# On macOS:
brew install openjdk@11

# On Linux:
sudo apt-get install openjdk-11-jdk

# On Windows: Download from oracle.com
```

#### 2. Install Buildozer
```bash
pip install buildozer
pip install cython
pip install kivy
```

#### 3. Setup Android SDK (First time only)
```bash
# This will download ~2-3 GB of SDK
buildozer android debug
```

#### 4. Build APK
```bash
# From project root
buildozer android debug
```

#### 5. Get APK
```
Output: bin/jurnalsaham-0.1.0-arm64-v8a_armeabi-v7a-debug.apk
Size: ~50 MB (approximate)
```

#### 6. Install on Phone
```bash
# Connect phone via USB
# Enable USB debugging on phone

# Option A: Copy to phone
adb install -r bin/jurnalsaham-0.1.0-arm64-v8a_armeabi-v7a-debug.apk

# Option B: Manual
# Copy APK to phone storage
# Tap to install
```

### Android Requirements
- Phone: Android 5.0+ (API 21+)
- Storage: ~100 MB
- RAM: 2+ GB recommended

### Android Known Issues

⚠️ **Buildozer is complex**
- Requires JDK, Gradle, Android SDK
- Long first setup (30+ min)
- Platform-specific errors

✅ **Better Alternatives**
Use the **release-signed APK** for wider distribution/updates:
```bash
./build_android_release.sh
ls -lh bin/*release*.apk
```

---

## 📊 Comparison: Which Version?

| Version | Windows | macOS | Android | iOS |
|---------|---------|-------|---------|-----|
| **Web App** | ✅ (after build) | ✅ (DMG ready) | 📱 (browser) | 📱 (browser) |
| **Desktop App** | ✅ (Python install) | ✅ (Python install) | ❌ | ❌ |
| **Standalone** | ✅ (after build) | ✅ (DMG ready) | ✅ (after build) | N/A |
| **Ease** | Medium | Easy | Hard | N/A |

### Recommendation
- **macOS users**: Download DMG ✅ (easiest)
- **Windows users**: Run web version or build EXE
- **Android users**: Use web version in browser (easiest)
- **Developer**: Use source code + Python

---

## 🚀 Distribution Checklist

### For macOS (Ready Now!)
- [x] DMG file created ✅
- [x] Ready to share ✅
- [ ] Code sign (optional)
- [ ] Notarize (for Monterey+)

### For Windows (Build First)
- [ ] Build EXE (`python build.py`)
- [ ] Test on Windows machine
- [ ] Create installer (optional)
- [ ] Upload to GitHub Releases

### For Android (Build First)
- [ ] Install Buildozer
- [ ] Build APK (`buildozer android debug`)
- [ ] Test on phone
- [ ] Sign for release (optional)

---

## 📥 How to Share Builds

### Option 1: GitHub Releases
```bash
# Create release on GitHub
# Upload .dmg, .exe, .apk files
# Users can download from releases page
```

### Option 2: Cloud Storage
```
Google Drive   → Share link
Dropbox        → Public link
Microsoft 365  → File sharing
```

### Option 3: Direct Download
```
Website with download links:
jurnal-saham.example.com/download

Files:
- Jurnal-Saham-IHSG-macOS.dmg
- Jurnal-Saham-IHSG-Windows.exe
- Jurnal-Saham-IHSG-Android.apk
```

### Option 4: Package Manager
```
Windows: Windows Store
macOS: Mac App Store / Homebrew
Android: Google Play Store
```

---

## 🔄 Version Control

### Current Builds
```
Version: 0.1.0
Date: Feb 22, 2026
Status: Beta

Files:
✅ bin/Jurnal-Saham-IHSG.dmg (macOS)
❌ bin/Jurnal-Saham-IHSG.exe (Windows - not built yet)
❌ bin/Jurnal-Saham-IHSG.apk (Android - not built yet)
```

### Update Builds
```bash
# When code changes:
1. Make code changes
2. Bump version in buildozer.spec / build.py
3. Rebuild all platforms
4. Upload new versions
5. Announce updates
```

---

## 📝 Next Steps (If You Want)

### Build Windows Version
```bash
# On a Windows PC or VM:
python build.py
# Output: bin/Jurnal-Saham-IHSG.exe
```

### Build Android Version
```bash
# On macOS/Linux with JDK installed:
buildozer android debug
# Output: bin/Jurnal-Saham-IHSG.apk
```

### Create GitHub Release
```bash
# Upload all 3 builds to GitHub Releases
# Make it easy for users to download
```

---

## ❓ FAQ

**Q: Dimana download macOS version?**
A: `bin/Jurnal-Saham-IHSG.dmg` (86 MB)
   Atau copy dari folder project

**Q: Apakah EXE (Windows) sudah tersedia?**
A: Belum. Harus di-build dulu dengan `python build.py`

**Q: Apakah APK (Android) sudah tersedia?**
A: Belum. Harus di-build dulu dengan `buildozer android debug`

**Q: Bisa jalankan langsung tanpa build?**
A: Ya! Download source code, install Python, run:
   - Web: `streamlit run app.py`
   - Desktop: `python3 desktop_app.py`
   - CLI: `python3 ai_agent.py`

**Q: Berapa file size masing-masing?**
A: - macOS DMG: ~86 MB
   - Windows EXE: ~150-200 MB (est. after build)
   - Android APK: ~50 MB (est. after build)

**Q: Apakah Windows build bisa di-jalankan tanpa instalasi?**
A: Ya! EXE standalone, double-click langsung jalan.

**Q: Bagaimana cara update ke versi baru?**
A: Download versi baru dari release page, install ulang.

---

## 🔗 Quick Links

- **macOS Download**: `bin/Jurnal-Saham-IHSG.dmg` ✅
- **Windows Build**: `python build.py`
- **Android Build**: `buildozer android debug`
- **Source Code**: All Python files in project

---

## 📞 Troubleshooting

### "File not found" when building
```bash
# Make sure you're in project root:
ls build.py   # Should exist

# If not:
cd jurnal-saham-ihsg
ls build.py   # Now try again
```

### "Module not found" errors
```bash
pip install -r requirements.txt
pip install pyinstaller buildozer
```

### Build process stuck
```bash
# Check disk space (need 2+ GB free)
# Kill process: Ctrl+C
# Remove build/ folder
# Try again
```

---

## 🎯 Summary

**Status:**
- ✅ macOS: Ready to download (DMG file)
- 🔄 Windows: Can build (15 min)
- 🔄 Android: Can build (30+ min, complex)
- ✅ Source code: Always available

**Easy Path:**
1. macOS → Download DMG ✅
2. Windows → Run Python version or build EXE
3. Android → Use web version in browser

**Developer Path:**
1. Clone project
2. Install Python
3. `streamlit run app.py` (web)
4. Or `python3 desktop_app.py` (GUI)

---

**Happy deploying! 🚀**
