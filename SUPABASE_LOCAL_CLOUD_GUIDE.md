# Supabase Cloud (Local App)

Tujuan: Aplikasi tetap jalan **lokal** (localhost), tetapi login via **email** dan data portfolio/journal disimpan ke **cloud** sehingga bisa dibuka dari device lain.

## 1) Buat Supabase Project
- Buat project di Supabase.
- Catat:
  - `SUPABASE_URL`
  - `SUPABASE_ANON_KEY`

## 2) Buat Table untuk menyimpan data
Gunakan SQL di Supabase SQL Editor:

```sql
create table if not exists public.user_data (
  user_id uuid primary key,
  data jsonb not null,
  updated_at timestamptz not null default now()
);

alter table public.user_data enable row level security;

-- User hanya boleh akses row miliknya sendiri
create policy "user_data_select_own" on public.user_data
  for select
  using (auth.uid() = user_id);

create policy "user_data_insert_own" on public.user_data
  for insert
  with check (auth.uid() = user_id);

create policy "user_data_update_own" on public.user_data
  for update
  using (auth.uid() = user_id)
  with check (auth.uid() = user_id);
```

## 3) Aktifkan Auth Email
Di Supabase Dashboard → Authentication:
- Aktifkan Email provider.
- Untuk mode paling mudah tanpa hosting: gunakan **Email + Password**.
- Jika ingin passwordless OTP, pastikan fitur **Email OTP** aktif (kalau project kamu mendukung).

## 4) Set environment variables
Di terminal sebelum menjalankan Streamlit:

```bash
export SUPABASE_URL="https://xxxxx.supabase.co"
export SUPABASE_ANON_KEY="your_anon_key"
```

## 5) Jalankan app

```bash
/Users/donnytakeshi/Documents/jurnal-saham-ihsg/.venv/bin/python -m streamlit run app.py
```

## 6) Cara pakai
- Sidebar → pilih **Cloud (Email)**.
- Login (email + password) → app akan mencoba **restore** data dari cloud.
- Perubahan portfolio/journal akan **auto-sync** ke cloud (toggle ada di sidebar).

## Catatan keamanan
- File token disimpan lokal di `data/auth/supabase_session.json` jika kamu centang “Ingat saya”.
- Anggap file ini setara password. Jika device hilang/terkompromi, lakukan **logout** dan **revoke sessions** dari Supabase.
