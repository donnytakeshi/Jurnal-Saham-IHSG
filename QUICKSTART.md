# 🚀 QUICK START GUIDE

Panduan cepat untuk memulai menggunakan Jurnal Screening Saham IHSG.

## 1️⃣ Setup Awal (Hanya Sekali)

Setup sudah selesai! Virtual environment sudah dibuat dan semua dependencies terinstall.

Jika ingin verify, jalankan:
```bash
source venv/bin/activate
pip list
```

## 2️⃣ Jalankan AI Agent

**Opsi A: Menggunakan Shell Script (Recommended)**
```bash
./run.sh
```

**Opsi B: Manual dengan Virtual Environment**
```bash
source venv/bin/activate
python ai_agent.py
```

## 3️⃣ Perintah Dasar

Setelah AI Agent berjalan, cobalah perintah-perintah ini:

### Lihat bantuan
```
Anda: help
```

### Jalankan screening saham
```
Anda: scan
```
Ini akan menganalisis 30+ saham IHSG dan menyimpan hasilnya ke `data/screening_results/`

### Cek detail saham tertentu
```
Anda: cek BBCA
Anda: cek BBNI
Anda: cek UNTR
```

### Lihat rekomendasi
```
Anda: rekomendasi
```

### Buka dashboard
```
Anda: jalankan dashboard
```
atau langsung di terminal:
```bash
./dashboard.sh
```

Dashboard akan terbuka di `http://localhost:8501`

### Cek status aplikasi
```
Anda: status
```

### Pelajari coding
```
Anda: belajar
```

### Keluar
```
Anda: keluar
```

## 📊 Memahami Output

### Fase Saham

🟢 **ACCUMULATION** - Saham dalam fase akumulasi, bandar membeli
- Entry: Cocok untuk swing trading
- Target: +3% hingga +5%
- Stop Loss: -3%

🔴 **DISTRIBUTION** - Saham dalam fase distribusi, bandar menjual
- Entry: Hindari, tunggu koreksi
- Signal: SELL atau HOLD

🟡 **ABSORBING** - Pasar konsolidasi
- Signal: HOLD dan tunggu breakout

### Signal Trading

- **STRONG_BUY**: Sangat bullish, masuk sekarang
- **BUY**: Bullish, bisa masuk dengan stop loss ketat
- **NEUTRAL**: Belum ada sinyal jelas
- **SELL**: Bearish, pertimbangkan jual
- **STRONG_SELL**: Sangat bearish, jual sekarang

## 📂 File Penting

- **ai_agent.py** - Main application file
- **app.py** - Streamlit dashboard
- **daily_automation.py** - Scheduler untuk screening harian
- **modules/** - Logic untuk data fetching dan analisis
- **data/screening_results/** - Hasil scan disimpan di sini
- **venv/** - Virtual environment

## 🔧 Troubleshooting

### "command not found: python3"
Pastikan Python 3 installed di Mac Anda.
```bash
brew install python@3.11
```

### "No module named 'pandas'" 
Aktivasi virtual environment dulu:
```bash
source venv/bin/activate
```

### Dashboard tidak bisa akses
Biasanya port 8501 sudah digunakan. Kematikan dashboard lama:
```bash
lsof -i :8501  # Lihat process ID
kill -9 <PID>
```

### Reset semua
Jika ingin fresh start:
```bash
rm -rf venv data/screening_results/*
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## 📝 Tips

1. **Jalankan scan setiap hari** - Data terbaru = rekomendasi lebih akurat
2. **Cross-check dengan berita** - Jangan blind trust ke automated system
3. **Gunakan stop loss** - Risk management adalah kunci
4. **Catat setiap transaksi** - Untuk analisis dan improvement
5. **Jangan FOMO** - Ada logic di balik setiap signal

## 🎯 Next Steps

- [ ] Buka `README.md` untuk dokumentasi lengkap
- [ ] Jalankan `./run.sh` untuk mulai
- [ ] Ketik `help` untuk melihat semua perintah
- [ ] Coba `scan` untuk screening pertama kali
- [ ] Buka dashboard dengan `jalankan dashboard`

---

**Happy Trading! 📈 Remember: Manajemen Risiko adalah Segalanya! 🎯**
