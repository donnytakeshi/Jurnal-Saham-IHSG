// Home Component
const STOCK_DATA = [
  {
    symbol: "BBCA",
    name: "Bank Central Asia",
    price: "9.850",
    change: "+3,45%",
    logo: "https://lh3.googleusercontent.com/aida-public/AB6AXuD2hUhgjN6u82dn_Bd93frWmcyrkjU9JEQIxc39m7Sr44inVBGX3SWjLJEtpkLKIQVQWMaTL2eQmFmxwXI7QLeaXjQVIFZa7dxpKhXE-LjR6rebsxttEb6nTR9uEL9uvWdt6RsCfaPGu8RfEea5kxBh4kHABcTNNmgXAb7jWQ8E3XacczgefGGarQ-E1-Bc5aVaMOgw8HpWCQK4rzq-ESNd0Mblnp0VOgxtTtRZap3D9MJ8fVObSuDvVy_dcyJYb0JGX8l4715LkL1D"
  },
  {
    symbol: "TLKM",
    name: "Telkom Indonesia",
    price: "3.920",
    change: "+2,81%",
    logo: "https://lh3.googleusercontent.com/aida-public/AB6AXuA6qDc1tWzaEErDcAM8SkCv1eSq7ASr1eNeNu2KLbgdHf6WXgWKu9nLyKf1l42Z1QjmyocSwqs6t68AuAPYkX4TIYccXCh33hjflvzrDDOzqS6H20Q8ohPl6PRXjQrWrfYEPf24FyHpsbWGiqoI3l8nC0IzBVcTAOdriNcqATCjsx-eGPqLRl5A62W_-NIdUl-FFAoE2KxsKBqcJLjAPhFRkCEfAE1O3TLQKshD7PTc7QtWQax9y0jg4LegP_3nxTBUI5o7V6epUJ_u"
  },
  {
    symbol: "GOTO",
    name: "GoTo Gojek Tokopedia",
    price: "65",
    change: "+1,56%",
    logo: "https://lh3.googleusercontent.com/aida-public/AB6AXuC8eyyH-EiW42vJo4vlnkN9baithwYd7XuijUS2Dsb9XmOlRT98VoQ-amJ6sp2Q4SfbTDaCIsAcxphxXCijhUGR3Nz5O8M6Q_KiJAELKWE4qWpz_KoNS8KNoSuGL2jCvToDcWApa5yZVfGvtmLxThnad-ykMGUOOvDOAoX3kifMWEuzr-clHCzthqRZCNYo9a7_p3tXC0oxmIUhnE1QzM2bkBqO3g5pWyHhUuPPhNDZ3EPke2iEuBaf736XPpjr7KfoMKX2FhGDg87T"
  }
];

function renderStockItem(stock) {
  return `
    <div class="bg-[#181c21] p-4 rounded-xl border border-white/5 flex items-center justify-between hover:bg-white/5 transition-all">
      <div class="flex items-center gap-4">
        <div class="w-10 h-10 rounded-lg bg-[#232930] flex items-center justify-center p-2">
          <img alt="${stock.symbol}" class="w-full h-full object-contain" src="${stock.logo}" />
        </div>
        <div>
          <p class="font-bold text-white font-body-lg text-body-lg">${stock.symbol}</p>
          <p class="text-slate-500 font-label-md text-label-md">${stock.name}</p>
        </div>
      </div>
      <div class="text-right">
        <p class="font-numeric-data text-numeric-data text-white">${stock.price}</p>
        <p class="text-primary font-numeric-data text-[12px]">${stock.change}</p>
      </div>
    </div>
  `;
}

function renderChart() {
  const heights = [40, 45, 42, 55, 65, 60, 75, 90, 85, 100];
  return heights.map(h => `<div class="flex-1 bg-primary/${Math.round((h / 100) * 80)} h-[${h}%] rounded-t-sm"></div>`).join("");
}

function renderHome() {
  return `
<main class="py-10 px-5 max-w-2xl mx-auto space-y-6 min-h-screen">
  <div class="flex items-center justify-between">
    <div class="flex items-center gap-2 px-3 py-1 bg-surface-container-low rounded-full border border-white/5">
      <div class="w-2 h-2 bg-primary rounded-full pulsing-dot"></div>
      <span class="font-label-md text-label-md text-primary tracking-wider uppercase">MARKET OPEN • JAKARTA</span>
    </div>
    <span class="text-slate-500 font-label-md text-label-md">11:42 WIB</span>
  </div>

  <section class="glass-card rounded-xl p-5 relative overflow-hidden">
    <div class="relative z-10">
      <div class="flex justify-between items-start mb-4">
        <div>
          <p class="text-slate-400 font-label-md text-label-md uppercase tracking-widest">IHSG Composite</p>
          <h2 class="font-headline-lg text-headline-lg mt-1 text-white">7.321,05</h2>
        </div>
        <div class="flex flex-col items-end">
          <div class="flex items-center text-primary gap-1">
            <span class="material-symbols-outlined text-lg">trending_up</span>
            <span class="font-numeric-data text-numeric-data">+1,24%</span>
          </div>
          <p class="text-slate-500 text-[10px] mt-1">+89,42 Today</p>
        </div>
      </div>
      <div class="h-32 w-full mt-6 flex items-end gap-1">
        ${renderChart()}
      </div>
    </div>
    <div class="absolute -bottom-10 -right-10 w-48 h-48 bg-primary/10 blur-[60px] rounded-full"></div>
  </section>

  <section>
    <div class="flex overflow-x-auto gap-3 custom-scrollbar -mx-5 px-5">
      <button class="flex-none px-4 py-2 bg-primary text-on-primary font-label-md text-label-md rounded-full flex items-center gap-2">
        <span class="material-symbols-outlined text-sm">bolt</span>Quick Buy
      </button>
      <button class="flex-none px-4 py-2 bg-surface-container-high border border-white/5 text-on-surface font-label-md text-label-md rounded-full flex items-center gap-2 hover:bg-white/5 transition-colors">
        <span class="material-symbols-outlined text-sm">search_check</span>Market Scan
      </button>
      <button class="flex-none px-4 py-2 bg-surface-container-high border border-white/5 text-on-surface font-label-md text-label-md rounded-full flex items-center gap-2 hover:bg-white/5 transition-colors">
        <span class="material-symbols-outlined text-sm">verified</span>Expert Analysis
      </button>
      <button class="flex-none px-4 py-2 bg-surface-container-high border border-white/5 text-on-surface font-label-md text-label-md rounded-full flex items-center gap-2 hover:bg-white/5 transition-colors">
        <span class="material-symbols-outlined text-sm">list_alt</span>Top 10
      </button>
    </div>
  </section>

  <section class="space-y-4">
    <div class="flex justify-between items-center px-1">
      <h3 class="font-headline-md text-headline-md text-white">Top Gainers</h3>
      <button class="text-primary font-label-md text-label-md">See All</button>
    </div>
    <div class="space-y-2">
      ${STOCK_DATA.map(renderStockItem).join("")}
    </div>
  </section>

  <section class="mt-8 pb-10">
    <div class="bg-[#181c21] border-l-4 border-[#159D91] rounded-r-xl p-4 flex gap-4">
      <div class="flex-none">
        <div class="w-10 h-10 rounded-full bg-primary/10 flex items-center justify-center">
          <span class="material-symbols-outlined text-primary">smart_toy</span>
        </div>
      </div>
      <div class="space-y-1">
        <div class="flex items-center gap-2">
          <span class="font-bold text-white text-body-md">DeepSeek Insight</span>
          <span class="px-1.5 py-0.5 bg-primary/10 text-primary text-[8px] rounded uppercase tracking-tighter">AI Analysis</span>
        </div>
        <p class="text-slate-400 font-body-md text-body-md leading-relaxed">
          IHSG showing strong resistance at 7.350. Accumulate banking blue-chips as foreign flow increases in session 2. Watch for GOTO breakout.
        </p>
      </div>
    </div>
  </section>
</main>
  `;
}
