# 🚀 Quick Start - Multi-User Jurnal Saham v2.0

## 5-Minute Setup

### 1️⃣ Install Dependencies
```bash
pip install -r requirements.txt
```

### 2️⃣ Start Desktop App
```bash
python desktop_app_v2.py
```

### 3️⃣ Create Account
- Click "✍️ Daftar"
- Enter: username, email, password
- Click "✅ Daftar"

### 4️⃣ Add Portfolio
- Go to "💼 Portfolio" tab
- Enter stock symbol (e.g., BBCA)
- Enter quantity dan average price
- Click "➕ Add"

### 5️⃣ Record Transactions
- Go to "📝 Journal" tab
- Select action (BUY/SELL/HOLD)
- Enter quantity, price
- Click "📝 Add"

### 6️⃣ Enable Cloud Sync
- Go to "⚙️ Settings"
- Click "☁️ Cloud Sync"
- Data sekarang ter-backup ke cloud!

---

## ✨ Key Features

### 🔐 Secure Login
```
Username: yourname
Email: you@example.com
Password: secure123
```
✅ Password di-hash securely
✅ Multi-device access
✅ Account isolation

### 📊 Portfolio Management
- Track holdings dari berbagai saham
- Monitor profit/loss real-time
- View portfolio statistics

### 📝 Transaction Journal
- Record setiap BUY/SELL transaction
- Track entry prices
- Complete history tersimpan

### ☁️ Cloud Sync
- Auto-backup ke cloud
- Access dari device manapun
- Data tidak hilang

---

## 💡 Pro Tips

### Backup Data Locally
```
⚙️ Settings → 💾 Export Portfolio
⚙️ Settings → 📊 Export Journal
⚙️ Settings → 📦 Full Backup
```

### Sync Interval
Di Settings:
- Default: 3600 detik (1 jam)
- Bisa diubah sesuai kebutuhan

### Change Password
Settings > 🔐 Change Password
- Masukkan old password
- Input new password 2x

### View Profile
Settings > 👤 Profile
- Lihat account info
- Email verification
- Member since date

---

## 🎨 UI Color Guide

| Color | Meaning |
|-------|---------|
| 🟦 Blue | Primary action (Login, Add) |
| 🟩 Green | Success (Save, Export) |
| 🟨 Yellow | Warning (Modify, Settings) |
| 🟥 Red | Danger (Delete, Logout) |
| 🟦 Teal | Secondary (Sync, Cloud) |

---

## 📱 Multi-Device Workflow

**Setup Device 1:**
```
1. Install app
2. Signup: john_investor
3. Add portfolio
4. Enable cloud sync ✅
```

**Setup Device 2:**
```
1. Install app
2. Login: john_investor (same account)
3. Data auto-restores from cloud ✅
4. Continue from where you left off
```

**Data Sync:**
```
Device 1 → Sync → Cloud ← Sync ← Device 2
```

---

## ❓ FAQ

**Q: Bisakah reset password?**
A: Belum ada reset password. Gunakan Change Password di Settings.

**Q: Data aman di cloud?**
A: Ya, Supabase menggunakan HTTPS encryption dan authentication.

**Q: Bisa ganti email?**
A: Belum support. Buat akun baru dengan email baru.

**Q: Bisa delete akun?**
A: Delete all data di Settings, lalu delete database file.

**Q: Offline mode?**
A: Ya! App bekerja offline, sync ke cloud saat online.

---

## 🛠️ Commands Reference

### Via Python Console
```python
# Setup
from modules.auth import AuthManager
from modules.database import JournalDatabase
from modules.cloud_sync import CloudSync

# Create user
auth = AuthManager()
success, msg = auth.signup("user", "email@example.com", "pwd")

# Login
success, user = auth.login("user", "pwd")

# Use database
db = JournalDatabase(user_id=user['user_id'])
db.add_portfolio_item("BBCA", "BCA", 100, 15000)

# Get portfolio
portfolio = db.get_portfolio()
```

---

## 📸 Screenshot Guide

### Login Screen
```
┌─────────────────────────────────┐
│   📊 JURNAL SAHAM IHSG         │
│ Kelola Portfolio Saham Anda     │
│                                 │
│ Username/Email: [input]        │
│ Password:       [input]        │
│                                 │
│ [🔓 Login] [✍️ Daftar]         │
└─────────────────────────────────┘
```

### Main App
```
┌─────────────────────────────────────────────────────┐
│ 👤 john | 📊 Jurnal Saham IHSG  [💾][☁️][⚙️][🚪]  │
├─────────────────────────────────────────────────────┤
│ [💼 Portfolio] [📝 Journal] [📊 Stats] [⚙️ Settings] │
├─────────────────────────────────────────────────────┤
│                                                     │
│ Symbol: [BBCA]  Qty: [100]  Price: [15000] [Add]  │
│                                                     │
│ Symbol │ Qty  │ Price │ Current │ Profit │ Action │
│ BBCA   │ 100  │ 15000 │ 16500   │ 150M   │ [Del]  │
│ BBNI   │  50  │ 14000 │ 15200   │  60M   │ [Del]  │
│                                                     │
└─────────────────────────────────────────────────────┘
```

---

## 🎯 Common Tasks

### Add New Stock to Portfolio
1. Go to Portfolio tab
2. Enter: BBCA (stock code)
3. Enter: 100 (quantity)
4. Enter: 15000 (average price)
5. Click "Add"

### Record Buy Transaction
1. Go to Journal tab
2. Symbol: BBCA
3. Action: BUY
4. Qty: 100
5. Price: 15500
6. Click "Add"

### Export Data as CSV
1. Go to Settings
2. Click "Export Portfolio"
3. Check Downloads folder

### Restore from Backup
1. Previous backup saved as JSON
2. File di: `output/backup_*.json`
3. Settings > Import (coming soon)

---

## 📞 Need Help?

**Module Documentation:**
- Authentication: `modules/auth.py`
- Database: `modules/database.py`
- Cloud Sync: `modules/cloud_sync.py`

**Configuration Files:**
- Database: `data/saham_journal.db`
- User DB: `data/users.db`
- Backups: `data/sync/`

---

Version: 2.0.0 | Last Updated: Feb 2026 | Status: ✅ Production Ready
