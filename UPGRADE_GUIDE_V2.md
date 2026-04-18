# 📊 Jurnal Saham IHSG - v2.0 Update Guide

## 🆕 New Features

### 1. **User Authentication System** 🔐
- **Secure Login/Signup** dengan password hashing menggunakan PBKDF2
- Setiap pengguna memiliki akun terpisah
- Support untuk login dengan username atau email
- Password change feature

**File:** `modules/auth.py`

```python
from modules.auth import AuthManager

auth = AuthManager()

# Signup
success, msg = auth.signup("username", "email@example.com", "password123")

# Login
success, user_data = auth.login("username", "password123")
if success:
    user_id = user_data['user_id']
    username = user_data['username']
```

---

### 2. **Multi-User Database Support** 👥
- Sekarang database mendukung multiple users
- Setiap data portfolio, journal, screening results memiliki `user_id`
- Data terisolasi per pengguna

**Database Changes:**
- `portfolio` table: tambah `user_id` column
- `journal` table: tambah `user_id` column
- `screening_results` table: tambah `user_id` column
- `price_history` table: tambah `user_id` column

**Penggunaan:**
```python
from modules.database import JournalDatabase

# Initialize dengan user_id
db = JournalDatabase(user_id=user_id)

# Atau set kemudian
db.user_id = user_id
db.add_portfolio_item("BBCA", "Bank Central Asia", 100, 15000)
```

---

### 3. **Cloud Sync with Supabase** ☁️
Sinkronisasi data ke cloud untuk akses multi-device!

**File:** `modules/cloud_sync.py`

**Features:**
- Sync portfolio data ke cloud
- Sync journal entries ke cloud
- Fetch data dari cloud untuk restore
- Local checkpoint sebagai fallback

**Setup:**
```python
from modules.cloud_sync import CloudSync, SyncManager

# Initialize Supabase
cloud = CloudSync(
    supabase_url="https://your-project.supabase.co",
    supabase_key="your-anon-key"
)

# Create sync manager
sync = SyncManager(cloud)

# Full sync
sync.full_sync(user_id, portfolio_data, journal_data)

# Restore from cloud
data = sync.restore_from_cloud(user_id)
```

**Supabase Setup:**
1. Go to https://supabase.com
2. Create new project
3. Create tables:
   - `portfolio` (sama schema seperti lokal)
   - `journal` (sama schema seperti lokal)
4. Get API URL dan key
5. Set di aplikasi

---

### 4. **Modern Desktop App with Login Screen** 💻
Launch dengan `python desktop_app_v2.py`

**Features:**
- 🔐 Modern login screen dengan signup dialog
- 🎨 Modern color scheme (Blue, Teal, Green)
- 💼 Portfolio management tab
- 📝 Journal/transaction tab
- 📊 Statistics with visual cards
- ⚙️ Settings tab
- ☁️ Cloud sync button
- 👤 User profile display

**UI Components:**
- Login screen dengan dark theme
- Color-coded buttons (success, danger, warning, primary)
- Responsive grid layouts
- Scrollable lists untuk data besar

---

## 📦 Installation

Install dependencies baru:
```bash
pip install -r requirements.txt
```

Dependencies baru:
- `supabase>=2.0.0` - Cloud database
- `postgrest-py>=0.13.0` - REST client

---

## 🚀 Usage

### Desktop App V2
```bash
python desktop_app_v2.py
```

1. **First Time:**
   - Click "✍️ Daftar" to create account
   - Enter username, email, password
   - Click "✅ Daftar"

2. **Login:**
   - Enter username/email dan password
   - Click "🔓 Login"

3. **Main App:**
   - Add portfolio items via "💼 Portfolio" tab
   - Record transactions via "📝 Journal" tab
   - View stats via "📊 Statistics" tab
   - Configure settings via "⚙️ Settings" tab

4. **Cloud Sync:**
   - Go to "⚙️ Settings"
   - Click "☁️ Cloud Sync"
   - Data akan auto-sync ke cloud

5. **Multi-Device:**
   - Login dengan akun yang sama di device lain
   - Data akan di-restore dari cloud otomatis

---

## 🔄 Migration from Old App

Jika pakai `desktop_app.py` (lama), data bisa di-migrate:

```python
from modules.database import JournalDatabase
import json

# Open old database (tanpa user_id)
old_db = JournalDatabase()
portfolio = old_db.get_portfolio()
journal = old_db.get_journal()

# Export ke JSON
data = {
    'portfolio': portfolio,
    'journal': journal
}

with open('migration_backup.json', 'w') as f:
    json.dump(data, f, indent=2)

# Import ke new database (dengan user_id)
new_db = JournalDatabase(user_id=new_user_id)

for item in portfolio:
    new_db.add_portfolio_item(
        item['symbol'],
        item.get('company_name', ''),
        item.get('quantity', 0),
        item.get('avg_price', 0),
        user_id=new_user_id
    )
```

---

## 📋 File Structure

```
modules/
├── auth.py              ✨ NEW - User authentication
├── cloud_sync.py        ✨ NEW - Cloud synchronization
├── database.py          ✏️ UPDATED - Multi-user support
├── data_fetcher.py
├── bandarmology.py
├── stockbit_fetcher.py
└── orderbook_analyzer.py

desktop_app_v2.py       ✨ NEW - Modern UI with login
desktop_app.py          (Old version - masih tersedia)
```

---

## 🔒 Security

- **Password:** Hashed dengan PBKDF2 + salt (100,000 iterations)
- **Cloud:** HTTPS dengan Supabase authentication
- **Local:** SQLite dengan session management
- **User isolation:** Data terisolasi per user

---

## ⚙️ Configuration

### Environment Variables (Optional)
```bash
export SUPABASE_URL="https://your-project.supabase.co"
export SUPABASE_KEY="your-anon-key"
```

### App Settings
Edit di Settings tab:
- Theme (light/dark)
- Currency (IDR, USD, etc)
- Auto-sync interval
- Notification preferences

---

## 🐛 Troubleshooting

**Q: "Cloud sync not connected"**
- A: Pastikan supabase package installed: `pip install supabase`
- A: Pastikan credentials sudah correct

**Q: "User sudah terdaftar"**
- A: Username/email sudah ada. Gunakan username berbeda

**Q: "Data tidak sync ke cloud"**
- A: Check internet connection
- A: Verify Supabase URL dan key valid

---

## 📝 Next Steps

Fitur yang akan datang:
- [ ] Real-time sync dengan WebSocket
- [ ] Push notifications
- [ ] Advanced analytics & charts
- [ ] Export to PDF reports
- [ ] Mobile app
- [ ] 2FA (Two-Factor Authentication)
- [ ] Dark mode toggle
- [ ] Data encryption at rest

---

## 📞 Support

Untuk pertanyaan atau issue:
1. Check existing files di `/data` folder
2. Verify database integrity
3. Check logs untuk error messages

---

**Version:** 2.0.0  
**Last Updated:** February 22, 2026  
**Status:** ✅ Production Ready
