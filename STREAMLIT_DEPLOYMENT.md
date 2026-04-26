# 🚀 Deployment Guide - Jurnal Saham IHSG (Streamlit)

## Deploy ke Streamlit Cloud (FREE & INSTANT)

### Step 1: Prepare Repository
```bash
# Sudah done! Files siap:
# - streamlit_app.py (entry point)
# - requirements.txt (dependencies)
# - .streamlit/config.toml (config)
# - app.py (main code)
```

### Step 2: Push ke GitHub
```bash
git add -A
git commit -m "Ready for Streamlit Cloud deployment"
git push origin build/apk-debug
```

### Step 3: Deploy di Streamlit Cloud

1. **Buka**: https://share.streamlit.io
2. **Login/Signup** dengan GitHub account
3. **New app** → Pilih repository ini
4. **Branch**: `build/apk-debug`
5. **Main file path**: `streamlit_app.py`
6. **Deploy!** ✅

Tunggu 2-3 menit, app langsung live di: `https://[username]-jurnal-saham-ihsg.streamlit.app`

---

## Environment Variables (untuk Supabase)

Jika ingin Supabase cloud sync:

1. Buka app settings (gear icon)
2. **Secrets** → Add:
```
SUPABASE_URL = "your-supabase-url"
SUPABASE_ANON_KEY = "your-anon-key"
```

Atau gunakan `.env` file lokal (tidak di-commit):
```bash
echo "SUPABASE_URL=..." >> .env
echo "SUPABASE_ANON_KEY=..." >> .env
```

---

## Local Development

### Setup
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Run
```bash
streamlit run streamlit_app.py
```

Buka: http://localhost:8501

---

## UI Polish TODO

- [ ] Update warna tema sesuai preferensi
- [ ] Optimize responsive layout untuk mobile
- [ ] Add loading animations
- [ ] Improve table styling
- [ ] Add dark mode toggle (optional)

---

## Troubleshooting

**Port 8501 sudah digunakan?**
```bash
streamlit run streamlit_app.py --server.port 8502
```

**Memory issue di cloud?**
- Streamlit Cloud gratis: 1GB RAM
- Limit screening ke 30 saham
- Cache hasil dengan @st.cache_data

**Data tidak sync?**
- Check Supabase credentials
- Verify internet connection
- Check browser console (F12)

---

## Production Checklist

- [x] Streamlit config setup
- [x] Requirements.txt fixed
- [x] .gitignore configured
- [ ] Push ke GitHub
- [ ] Deploy ke Streamlit Cloud
- [ ] Test semua fitur
- [ ] Setup Supabase (optional)
- [ ] Share link dengan teman

---

**Status**: ✅ Ready for deployment!
