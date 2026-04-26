# Modular HTML Architecture

## Struktur Project

```
assets/
├── index.html              # WRAPPER UTAMA - orchestrator tabs
├── lib/
│   └── config.js           # Shared state, API calls, utilities
└── components/
    ├── home.html           # Tab Home
    ├── watchlist.html      # Tab Watchlist
    ├── journal.html        # Tab Journal
    ├── screening.html      # Tab Screening
    ├── cek-emiten.html     # Tab Cek Emiten
    └── ai-chat.html        # Tab AI Chat
```

## Cara Kerja

1. **index.html** memuat:
   - CSS Tailwind + styling shared
   - Header, Navigation, Main content area
   - lib/config.js (shared state)
   - Semua component files

2. **lib/config.js** menyediakan:
   - Global state (stockData, portfolio, watchlist, etc)
   - API functions (fetchStock, fetchIHSG, refreshAllData)
   - Utility functions (showToast, switchTab, etc)
   - LocalStorage management

3. **components/*.html** berisi:
   - renderXxx() function yang render tab content
   - Component-specific functions
   - Completely independent dari component lain

## Cara Menambah Tab Baru

### Step 1: Buat File Component
Misal: `assets/components/portfolio.html`

```html
<!-- Portfolio Tab Component -->
<script>
function renderPortfolio() {
    const html = `<div class="space-y-6">
        <h1 class="font-headline-lg">Portfolio Analysis</h1>
        <!-- Your content here -->
    </div>`;
    document.getElementById('tab-portfolio').innerHTML = html;
}
</script>
```

### Step 2: Update index.html

Tambahkan di section `<!-- Main Content -->`:
```html
<div id="tab-portfolio" class="tab-content"></div>
```

Tambahkan di Bottom Navigation:
```html
<div class="nav-item flex flex-col items-center justify-center text-slate-500 hover:text-primary transition-all" data-tab="portfolio" onclick="switchTab('portfolio')">
    <span class="material-symbols-outlined">wallet</span>
    <span class="font-['Work_Sans'] text-[10px] font-medium uppercase tracking-wider mt-1">Portfolio</span>
</div>
```

Tambahkan di Script Loading:
```html
<script src="components/portfolio.html"></script>
```

## Rules untuk Membuat Component

1. **Function naming**: `render{TabName}()` - misal `renderPortfolio()`
2. **DOM target**: `document.getElementById('tab-{tabname}')` - misal `tab-portfolio`
3. **Use global state**: stockData, watchlist, portfolio, etc dari config.js
4. **Use utility functions**: switchTab(), showToast(), savePortfolio(), etc
5. **Styling**: Gunakan class Tailwind dari config, jangan hardcode CSS

## Tab Checklist

- [x] home.html - Home Dashboard
- [x] watchlist.html - Watchlist Manager
- [ ] journal.html - Portfolio & Transactions
- [ ] screening.html - Market Scanner
- [ ] cek-emiten.html - Stock Analysis
- [ ] ai-chat.html - AI Chat Assistant

## Update Flow

Ketika ada permintaan "Tambahkan fitur X ke tab Y":

1. I create/update `components/y.html` dengan fitur X
2. Update `index.html` jika perlu (DOM, navigation)
3. Component automatically integrated via renderY() call

No file conflicts, no duplicate code, clean and modular!
