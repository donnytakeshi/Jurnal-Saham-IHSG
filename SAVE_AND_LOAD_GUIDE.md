# 💾 Save & Load Features - Complete Guide

## Overview

Desktop app punya **3 layer** save system untuk keamanan maksimal:

1. **Auto-Save** - Realtime ke database
2. **Manual Export** - CSV untuk spreadsheet
3. **Full Backup** - JSON untuk restore

---

## 1️⃣ Auto-Save (Automatic)

### What Happens
- Setiap kali Anda add/update portfolio atau journal
- Data **instantly saved** ke SQLite database
- Tidak perlu klik tombol apapun

### Where
```
data/saham_journal.db
```

### Safety
✅ Database-level consistency
✅ Atomic transactions
✅ Auto-recovery on crash

### Example
```
1. Add BBCA ke portfolio
   [System] Instantly saves to DB
2. Close app
3. Open app lagi
   [System] BBCA masih ada! ✅
```

---

## 2️⃣ Export to CSV

### What It Does
Converts portfolio & journal to Excel-compatible CSV

### Where to Find
```
Settings Tab
  → 💾 Export Portfolio (CSV)
  → 📊 Export Journal (CSV)
```

### Output Location
```
exports/portfolio_backup_YYYYMMDD_HHMMSS.csv
exports/journal_backup_YYYYMMDD_HHMMSS.csv
```

### Use Cases
- ✅ Open di Excel/Google Sheets
- ✅ Share dengan teman
- ✅ Backup di external drive
- ✅ Import ke aplikasi lain

### Format

**Portfolio CSV:**
```
id,symbol,company_name,quantity,avg_price,current_price,total_invested,total_current_value,created_at,updated_at
1,BBCA,Bank Central Asia,100,10500,10680,1050000,1068000,2026-02-22 07:00:45,2026-02-22 07:00:45
2,BBNI,Bank Negara Indonesia,50,8000,8150,400000,407500,2026-02-22 07:00:45,2026-02-22 07:00:45
```

**Journal CSV:**
```
id,symbol,date,action,quantity,price,total,notes,created_at
1,BBCA,2026-02-22,BUY,100,10500,1050000,Accumulation phase,2026-02-22 07:00:45
2,BBNI,2026-02-22,SELL,25,8100,202500,Profit taking,2026-02-22 07:00:45
```

### Advantages
- 📊 Open anywhere
- 🔄 Easy share
- ✅ Human-readable

### Disadvantages
- ⚠️ Manual process
- ⚠️ Need 2 files (portfolio + journal)
- ⚠️ Can't import back (one-way)

---

## 3️⃣ Full Backup (JSON)

### What It Does
Complete backup of portfolio + journal dalam 1 file JSON

### Where to Find
```
Settings Tab → 📦 Full Backup (JSON)
```

### Output Location
```
exports/backup_YYYYMMDD_HHMMSS.json
```

### Format

```json
{
  "portfolio": [
    {
      "id": 1,
      "symbol": "BBCA",
      "company_name": "Bank Central Asia",
      "quantity": 100,
      "avg_price": 10500.0,
      "current_price": 10680.0,
      "total_invested": 1050000.0,
      "total_current_value": 1068000.0,
      "created_at": "2026-02-22 07:00:45",
      "updated_at": "2026-02-22 07:00:45"
    }
  ],
  "journal": [
    {
      "id": 1,
      "symbol": "BBCA",
      "date": "2026-02-22",
      "action": "BUY",
      "quantity": 100,
      "price": 10500.0,
      "total": 1050000.0,
      "notes": "Accumulation phase",
      "created_at": "2026-02-22 07:00:45"
    }
  ],
  "exported_at": "2026-02-22T07:00:45.123456"
}
```

### Use Cases
- ✅ Complete recovery
- ✅ Multiple backups
- ✅ Version control
- ✅ Disaster recovery

### Advantages
- 💯 Complete data
- 🔄 Bidirectional (can restore)
- 📦 Single file
- 🔍 Human-readable (JSON)

---

## 4️⃣ Load from Backup (Restore)

### Where to Find
```
Click 📂 Load button di header
```

### Steps
1. Click **📂 Load** button
2. File chooser opens
3. Navigate to `exports/` folder
4. Select `backup_*.json` file
5. Click **📂 Load**
6. Confirmation popup
7. ✅ Data restored!

### What Happens
- Reads JSON backup
- Imports all portfolio items
- Imports all journal entries
- Verifies & confirms
- Shows "✅ Data loaded successfully!"

### Example
```
Scenario:
1. Laptop rusak, data hilang 😱
2. Punya backup_20260222_070045.json
3. Install app di laptop baru
4. Click Load
5. Select backup file
6. Semua data restored! ✅
```

### Recovery Cases
- ✅ Restore after database reset
- ✅ Move to different computer
- ✅ Restore accidental delete
- ✅ Version rollback

---

## 🛡️ Recommended Workflow

### Daily
```
1. Add transactions via app
2. Auto-save happens automatically ✅
3. Go home happy
```

### Weekly
```
1. Click 📦 Full Backup (JSON)
2. Move backup to cloud drive (Gdrive, Dropbox)
3. Done!
```

### Monthly
```
1. Click 📤 Export Portfolio (CSV)
2. Open di Google Sheets
3. Review performance
4. Keep CSV backup
```

### Before Major Changes
```
1. Click 📦 Full Backup (JSON)
2. Save dengan naming: backup_before_update_20260222.json
3. Now safe to make changes
```

---

## 🚨 Disaster Recovery Plan

### Lost Database File
```
Problem: data/saham_journal.db missing/corrupted
Solution: Click 📂 Load → select recent backup_*.json
Result: Everything restored! ✅
```

### Accidental Delete
```
Problem: Deleted BBCA dari portfolio
Solution: 
  1. Click ⚙️ Delete All Data
  2. App resets
  3. Click 📂 Load → select backup before delete
  4. Everything back! ✅
```

### Computer Crash
```
Problem: Laptop mati, database uncertain
Solution:
  1. Install app di laptop baru
  2. Copy backup_*.json dari external drive
  3. Click 📂 Load → select file
  4. All data restored! ✅
```

### Multi-Device Setup
```
1. Device A: Keep regular backups
2. Cloud: Store backup_*.json files
3. Device B: 
   - Install app
   - Load from cloud backup
4. Both devices synced! ✅
```

---

## 📊 Data Integrity

### Verification
```bash
# Check if JSON is valid
python3 -c "import json; json.load(open('backup.json'))"

# Must show no error ✅
```

### Checksums (Future)
```
backup_20260222_070045.json
backup_20260222_070045.json.sha256
```

---

## 🔐 Security

### Local Storage
- ✅ All data on your computer
- ✅ No cloud by default
- ✅ Full privacy

### Backup Security
- ✅ JSON adalah plain text
- ⚠️ Consider password-protecting files
- ⚠️ Don't share raw backups

### Recommended
```
1. Store backups on encrypted USB
2. Use cloud (Gdrive/Dropbox) dengan 2FA
3. Keep offline backup
```

---

## 🆚 Comparison

| Feature | Auto-Save | CSV Export | JSON Backup |
|---------|-----------|-----------|------------|
| Manual click | ❌ | ✅ | ✅ |
| Real-time | ✅ | - | - |
| Portable | ❌ | ✅ | ✅ |
| Restorable | ✅ | ❌ | ✅ |
| Format | DB | Spreadsheet | JSON |
| Share-able | ❌ | ✅ | ✅ |
| Speed | Fast | ⏱️ | ⏱️ |

---

## 🚀 Best Practices

### ✅ DO
- ✅ Regular backups (weekly)
- ✅ Multiple copies (cloud + local)
- ✅ Test restore occasionally
- ✅ CSV for analysis & sharing
- ✅ JSON for recovery

### ❌ DON'T
- ❌ Rely on 1 backup only
- ❌ Forgot to backup
- ❌ Assume database is unbreakable
- ❌ Share password-containing backups
- ❌ Delete backups immediately

---

## 🔄 Migration Guide

### Upgrade from Web App to Desktop
```bash
1. Export portfolio dari Streamlit
2. Manual entry dalam Desktop app
   (atau integration later)
3. Save/backup di Desktop app
```

### Multiple Devices
```bash
Device A:
  1. Use app, make backups

Cloud Storage:
  2. Upload backup_*.json

Device B:
  3. Click Load
  4. Select backup from cloud
  5. ✅ Synced!
```

---

## ❓ FAQ

**Q: Apakah auto-save selalu bekerja?**
A: Yes! Setiap operasi langsung ke database dengan atomic transactions.

**Q: CSV bisa di-import kembali?**
A: Tidak saat ini. Gunakan JSON untuk restore. CSV hanya untuk export.

**Q: Berapa besar backup file?**
A: Kecil! Typical: <100 KB untuk portfolio + journal.

**Q: Aman simpan di Dropbox?**
A: Yes! Semuanya encrypted. Tapi lebih aman jika Dropbox account protected dengan 2FA.

**Q: Bisa schedule backup otomatis?**
A: Di Desktop app: TODO untuk feature nanti. Saat ini: manual click.

**Q: Hapus backup yang lama?**
A: Yes, aman. Simpan paling recent 3 backups aja.

---

## 📝 Export File Naming

Format: `{type}_backup_{YYYYMMDD_HHMMSS}.{ext}`

Examples:
```
portfolio_backup_20260222_070045.csv
journal_backup_20260222_070045.csv
backup_20260222_070045.json
```

This allows:
- ✅ Chronological sorting
- ✅ Easy identification
- ✅ Multiple backups possible

---

## 🎯 Summary

**3 Ways to Keep Data Safe:**

1. **Auto-Save** - Relax, enjoy app
2. **CSV Export** - Share & analyze
3. **JSON Backup** - Complete recovery

**Recommended:** Combine 1 + 3 for peace of mind 💪

---

**Your data is safe! 🛡️**
