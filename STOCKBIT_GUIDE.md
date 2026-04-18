# 📱 Stockbit Integration Guide

Panduan untuk menggunakan Stockbit sebagai sumber data alternatif untuk screening saham.

## 🎯 Apa itu Stockbit?

Stockbit adalah platform analisis saham Indonesia terpopuler yang menyediakan:
- Data pasar real-time
- Technical analysis
- Fundamental data
- Rekomendasi dari komunitas
- Screening tools

## 🚀 Cara Menggunakan

### 1. Check Data Saham dari Stockbit

Di AI Agent, gunakan perintah:
```
Anda: stockbit BBCA
Anda: stockbit BBNI
Anda: stockbit UNTR
```

Output akan menampilkan:
```
============================================================
📊 DATA STOCKBIT - BBCA
============================================================

💰 HARGA & PERUBAHAN:
   Harga Saat Ini: Rp{harga}
   Perubahan: {change_pct}%
   Volume: {volume}

📈 VALUASI:
   Market Cap: {market_cap}
   P/E Ratio: {pe_ratio}
   Dividend Yield: {dividend_yield}%

🎯 RATING STOCKBIT:
   Rekomendasi: {recommendation}
   Technical: {technical_rating}
   Fundamental: {fundamental_rating}

📊 SIGNAL:
   Buy Signal: {buy_signal_count}
   Sell Signal: {sell_signal_count}

🔄 PERBANDINGAN DATA:
   Source      | Current Price | Change %
   Stockbit    | ...          | ...
   yFinance    | ...          | ...
```

### 2. Gunakan Stockbit Fetcher di Python

```python
from modules.stockbit_fetcher import StockbitFetcher

# Create fetcher instance
fetcher = StockbitFetcher()

# Get analysis untuk 1 saham
analysis = fetcher.fetch_stock_analysis('BBCA')
print(analysis)

# Get sentiment untuk semua saham
df = fetcher.fetch_all_stocks_sentiment()
print(df)

# Get fundamental data
fundamentals = fetcher.get_stock_fundamentals('BBCA')
print(fundamentals)

# Compare dengan yfinance
comparison = fetcher.compare_with_yfinance('BBCA')
print(comparison)

# Save results
fetcher.save_screening_results()
```

## 📊 Data yang Bisa Diambil

### Stock Analysis
- `current_price` - Harga saat ini
- `change_pct` - Perubahan persentase
- `volume` - Volume trading
- `recommendation` - Rekomendasi (BUY/SELL/HOLD)
- `technical_rating` - Rating teknikal
- `fundamental_rating` - Rating fundamental
- `buy_signal_count` - Jumlah signal beli
- `sell_signal_count` - Jumlah signal jual

### Fundamental Data
- `pe_ratio` - Price to Earnings Ratio
- `pb_ratio` - Price to Book Ratio
- `roe` - Return on Equity
- `der` - Debt to Equity Ratio
- `eps` - Earnings per Share
- `dividend_yield` - Dividend Yield
- `market_cap` - Market Capitalization

## 🔄 Fitur Caching

Data Stockbit di-cache secara lokal untuk:
1. **Performa lebih cepat** - Tidak perlu request API setiap kali
2. **Mengurangi request** - Hindari rate limiting
3. **Offline access** - Bisa akses data yang sudah di-cache

### Folder Cache
```
data/
└── stockbit_cache/
    ├── BBCA_analysis_20260221.json
    ├── BBCA_fundamental_20260221.json
    ├── BBNI_analysis_20260221.json
    └── ...
```

### Lifetime Cache
- **Analysis**: 4 jam (cepat berubah)
- **Fundamental**: 24 jam (jarang berubah)

### Disable Cache (force refresh)
```python
fetcher = StockbitFetcher(use_cache=False)
```

## 🔍 Kombinasi dengan yFinance

StockbitFetcher bisa otomatis membandingkan data dengan yFinance:

```python
comparison = fetcher.compare_with_yfinance('BBCA')
# Hasilnya:
#        Source  Current Price   Change %
# 0   Stockbit       Rp14,500   +1.00%
# 1   yFinance       Rp14,480   +0.98%
```

Ini berguna untuk:
1. **Validasi data** - Pastikan data akurat
2. **Melihat perbedaan** - Stockbit vs yFinance
3. **Triangulasi** - Cross-check dengan multiple sources

## 📈 Integration dengan Screening

Kombinasikan Stockbit dengan Bandarmology analysis:

```python
from modules.stockbit_fetcher import StockbitFetcher
from modules.bandarmology import BandarmologyAnalyzer

fetcher = StockbitFetcher()
sentiment = fetcher.fetch_all_stocks_sentiment()

# Filter hanya yang recommended
buy_stocks = sentiment[sentiment['recommendation'] == 'BUY']

for stock_code in buy_stocks['symbol']:
    # Get historical data for bandarmology
    analysis = fetcher.fetch_stock_analysis(stock_code)
    
    # Print hasil
    print(f"{stock_code}: Recommendation={analysis['recommendation']}, "
          f"Technical={analysis['technical_rating']}")
```

## ⚙️ Konfigurasi API

Jika ingin menggunakan Stockbit API dengan authentication:

```python
# Belum diimplementasi, tapi bisa ditambahkan nanti
fetcher = StockbitFetcher(api_key='your_stockbit_api_key')
```

## 🛑 Limitation

1. **API terbatas** - Stockbit tidak punya public API lengkap
2. **Scraping fallback** - Jika API tidak bisa diakses, sistem akan scraping halaman web
3. **Rate limiting** - Batasi jumlah request untuk hindari blocking
4. **Cache expired** - Data dihapus setelah cache lifetime selesai

## 🔄 Web Scraping Fallback

Jika API Stockbit tidak tersedia, sistem akan:
1. Parse halaman web Stockbit menggunakan BeautifulSoup
2. Extract data dari HTML elements
3. Return hasil scraping

**Note**: Scraping lebih lambat dan bisa berubah jika Stockbit ganti struktur HTML.

## 🚀 Contoh Use Case

### 1. Find Buy Opportunities
```
Anda: stockbit BBCA
Anda: stockbit BBNI
Anda: stockbit INTP
```
Compare recommendation dari semua saham favorit Anda.

### 2. Monitor Sentiment Change
Jalankan screening rutin, simpan hasil, compare dengan hasil sebelumnya untuk track sentiment change.

### 3. Validation
Check hasil yFinance dengan Stockbit untuk memastikan data akurat sebelum trading.

## 📞 Troubleshooting

### "Error: API tidak tersedia"
- Stockbit API sedang down
- Sistem akan otomatis fallback ke scraping
- Coba lagi beberapa detik

### "BeautifulSoup belum diinstall"
```bash
pip install beautifulsoup4
```

### "Data outdated"
Cache terlalu tua, gunakan:
```python
fetcher = StockbitFetcher(use_cache=False)
```

### "Rate limit exceeded"
Terlalu banyak request. Tunggu beberapa menit atau gunakan cache yang disediakan.

## 📚 Next Steps

1. Coba perintah `stockbit BBCA` di AI Agent
2. Lihat output dan bandingkan dengan yFinance
3. Combine dengan `cek BBCA` (yFinance) untuk double-check
4. Gunakan di screening untuk tambah context

---

**Happy Trading dengan Stockbit Data! 📈**
