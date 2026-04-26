// Cek Saham Component - Stock Analysis Detail Page
function renderCekSaham() {
  return `
<main class="p-5 pb-32 max-w-5xl mx-auto space-y-4">
  <!-- Header Section: Ticker Info -->
  <section class="flex flex-col md:flex-row md:items-end justify-between gap-2 mb-6">
    <div>
      <div class="flex items-center gap-2">
        <h1 class="font-headline-lg text-headline-lg text-on-surface">BBCA</h1>
        <span class="bg-primary/10 text-primary px-2 py-0.5 rounded-sm text-label-md font-label-md">LQ45</span>
      </div>
      <p class="text-slate-400 font-body-md text-body-md">PT Bank Central Asia Tbk.</p>
    </div>
    <div class="text-right">
      <div class="flex items-baseline justify-end gap-1">
        <span class="font-numeric-data text-headline-md text-on-surface">10,225</span>
        <span class="text-secondary font-numeric-data text-body-lg">+175</span>
      </div>
      <div class="flex items-center justify-end gap-1 text-secondary">
        <span class="material-symbols-outlined text-sm" style="font-variation-settings: 'FILL' 1;">arrow_drop_up</span>
        <span class="font-numeric-data text-body-md">+1.74%</span>
      </div>
    </div>
  </section>

  <!-- Bento Grid Layout -->
  <div class="grid grid-cols-1 md:grid-cols-12 gap-4">
    <!-- Bid-Offer (Level 2) - Large Card -->
    <div class="md:col-span-7 bg-[#181c21] rounded-xl border border-white/5 overflow-hidden flex flex-col">
      <div class="p-4 border-b border-white/5 flex justify-between items-center bg-white/2">
        <h3 class="font-headline-md text-body-lg text-on-surface">Order Book</h3>
        <span class="text-label-md text-slate-500 font-label-md">Live Depth</span>
      </div>
      <div class="grid grid-cols-2 text-label-md font-label-md uppercase tracking-wider text-slate-500 py-2 px-4 border-b border-white/5">
        <div class="grid grid-cols-3">
          <span>Lot</span>
          <span class="text-right">Bid</span>
        </div>
        <div class="grid grid-cols-3">
          <span class="col-span-1 pl-4">Offer</span>
          <span class="col-span-2 text-right">Lot</span>
        </div>
      </div>
      <div class="flex-grow">
        <!-- Bid Side -->
        <div class="grid grid-cols-2 font-numeric-data text-numeric-data">
          <div class="flex flex-col border-r border-white/5">
            <!-- 5 Rows of Bid -->
            <div class="relative grid grid-cols-3 px-4 py-2 hover:bg-white/5">
              <div class="absolute inset-y-1 right-0 bg-secondary/10 w-3/4 pointer-events-none"></div>
              <span class="z-10 text-slate-300">42.1K</span>
              <span class="z-10 col-span-2 text-right text-secondary">10,200</span>
            </div>
            <div class="relative grid grid-cols-3 px-4 py-2 hover:bg-white/5">
              <div class="absolute inset-y-1 right-0 bg-secondary/10 w-full pointer-events-none"></div>
              <span class="z-10 text-slate-300">105.8K</span>
              <span class="z-10 col-span-2 text-right text-secondary">10,175</span>
            </div>
            <div class="relative grid grid-cols-3 px-4 py-2 hover:bg-white/5">
              <div class="absolute inset-y-1 right-0 bg-secondary/10 w-1/2 pointer-events-none"></div>
              <span class="z-10 text-slate-300">28.4K</span>
              <span class="z-10 col-span-2 text-right text-secondary">10,150</span>
            </div>
            <div class="relative grid grid-cols-3 px-4 py-2 hover:bg-white/5">
              <div class="absolute inset-y-1 right-0 bg-secondary/10 w-1/4 pointer-events-none"></div>
              <span class="z-10 text-slate-300">12.9K</span>
              <span class="z-10 col-span-2 text-right text-secondary">10,125</span>
            </div>
            <div class="relative grid grid-cols-3 px-4 py-2 hover:bg-white/5 border-b border-white/5">
              <div class="absolute inset-y-1 right-0 bg-secondary/10 w-2/3 pointer-events-none"></div>
              <span class="z-10 text-slate-300">55.2K</span>
              <span class="z-10 col-span-2 text-right text-secondary">10,100</span>
            </div>
          </div>
          <!-- Offer Side -->
          <div class="flex flex-col">
            <!-- 5 Rows of Offer -->
            <div class="relative grid grid-cols-3 px-4 py-2 hover:bg-white/5">
              <div class="absolute inset-y-1 left-0 bg-error-container/10 w-1/3 pointer-events-none"></div>
              <span class="z-10 text-error pl-4">10,225</span>
              <span class="z-10 col-span-2 text-right text-slate-300">15.4K</span>
            </div>
            <div class="relative grid grid-cols-3 px-4 py-2 hover:bg-white/5">
              <div class="absolute inset-y-1 left-0 bg-error-container/10 w-2/3 pointer-events-none"></div>
              <span class="z-10 text-error pl-4">10,250</span>
              <span class="z-10 col-span-2 text-right text-slate-300">62.8K</span>
            </div>
            <div class="relative grid grid-cols-3 px-4 py-2 hover:bg-white/5">
              <div class="absolute inset-y-1 left-0 bg-error-container/10 w-full pointer-events-none"></div>
              <span class="z-10 text-error pl-4">10,275</span>
              <span class="z-10 col-span-2 text-right text-slate-300">110.2K</span>
            </div>
            <div class="relative grid grid-cols-3 px-4 py-2 hover:bg-white/5">
              <div class="absolute inset-y-1 left-0 bg-error-container/10 w-1/2 pointer-events-none"></div>
              <span class="z-10 text-error pl-4">10,300</span>
              <span class="z-10 col-span-2 text-right text-slate-300">44.1K</span>
            </div>
            <div class="relative grid grid-cols-3 px-4 py-2 hover:bg-white/5 border-b border-white/5">
              <div class="absolute inset-y-1 left-0 bg-error-container/10 w-1/4 pointer-events-none"></div>
              <span class="z-10 text-error pl-4">10,325</span>
              <span class="z-10 col-span-2 text-right text-slate-300">22.8K</span>
            </div>
          </div>
        </div>
      </div>
      <div class="p-4 flex justify-between items-center text-label-md">
        <span class="text-slate-400">Total Bid: <span class="text-on-surface font-semibold">244.4K</span></span>
        <span class="text-slate-400">Total Offer: <span class="text-on-surface font-semibold">255.3K</span></span>
      </div>
    </div>

    <!-- Right Column -->
    <div class="md:col-span-5 space-y-4">
      <!-- Bandarmology Summary -->
      <div class="bg-[#181c21] rounded-xl border border-white/5 p-4 space-y-4">
        <div class="flex justify-between items-start">
          <div>
            <h3 class="font-headline-md text-body-lg text-on-surface">Bandarmology</h3>
            <p class="text-label-md text-slate-400 font-label-md">Analysis: Last 5 Days</p>
          </div>
          <span class="bg-secondary/10 text-secondary border border-secondary/20 px-3 py-1 rounded-full text-label-md font-bold uppercase tracking-tight">Big Accumulation</span>
        </div>
        <!-- Gauge/Progress Visual -->
        <div class="space-y-2">
          <div class="flex justify-between text-label-md text-slate-500 font-label-md">
            <span>Distribution</span>
            <span>Neutral</span>
            <span>Accumulation</span>
          </div>
          <div class="h-3 w-full bg-surface-container-highest rounded-full overflow-hidden flex">
            <div class="h-full bg-error/30" style="width: 20%"></div>
            <div class="h-full bg-slate-700/30" style="width: 30%"></div>
            <div class="h-full bg-secondary" style="width: 50%"></div>
          </div>
          <div class="flex justify-center">
            <span class="material-symbols-outlined text-secondary text-sm">arrow_drop_up</span>
          </div>
        </div>
        <div class="grid grid-cols-2 gap-2 pt-2 border-t border-white/5">
          <div class="bg-white/2 p-2 rounded-lg text-center">
            <span class="text-label-md text-slate-400 block">Bandar Power</span>
            <span class="text-numeric-data text-secondary">0.82</span>
          </div>
          <div class="bg-white/2 p-2 rounded-lg text-center">
            <span class="text-label-md text-slate-400 block">Retail Power</span>
            <span class="text-numeric-data text-error">-0.45</span>
          </div>
        </div>
      </div>

      <!-- Broker Summary Action -->
      <div class="bg-[#181c21] rounded-xl border border-white/5 overflow-hidden">
        <div class="p-4 border-b border-white/5 flex justify-between items-center">
          <h3 class="font-headline-md text-body-lg text-on-surface">Broker Action</h3>
          <div class="flex gap-1">
            <span class="px-2 py-0.5 rounded bg-white/10 text-[10px] font-bold">1D</span>
            <span class="px-2 py-0.5 rounded bg-secondary text-on-primary text-[10px] font-bold">5D</span>
          </div>
        </div>
        <div class="p-4 space-y-6">
          <!-- Top Buyers -->
          <div class="space-y-2">
            <h4 class="text-label-md font-bold text-secondary uppercase tracking-widest flex items-center gap-1">
              <span class="material-symbols-outlined text-xs">trending_up</span> Top Net Buyers
            </h4>
            <div class="space-y-1">
              <div class="flex items-center justify-between font-numeric-data py-1 text-sm">
                <div class="flex items-center gap-2">
                  <span class="w-8 h-6 bg-secondary/10 text-secondary text-[10px] flex items-center justify-center rounded font-bold">AK</span>
                  <span class="text-slate-300">UBS Sekuritas</span>
                </div>
                <span class="text-on-surface">124.5B</span>
              </div>
              <div class="flex items-center justify-between font-numeric-data py-1 text-sm">
                <div class="flex items-center gap-2">
                  <span class="w-8 h-6 bg-secondary/10 text-secondary text-[10px] flex items-center justify-center rounded font-bold">RX</span>
                  <span class="text-slate-300">Macquarie</span>
                </div>
                <span class="text-on-surface">88.2B</span>
              </div>
              <div class="flex items-center justify-between font-numeric-data py-1 text-sm">
                <div class="flex items-center gap-2">
                  <span class="w-8 h-6 bg-secondary/10 text-secondary text-[10px] flex items-center justify-center rounded font-bold">ZP</span>
                  <span class="text-slate-300">Maybank</span>
                </div>
                <span class="text-on-surface">45.1B</span>
              </div>
            </div>
          </div>

          <!-- Top Sellers -->
          <div class="space-y-2">
            <h4 class="text-label-md font-bold text-error uppercase tracking-widest flex items-center gap-1">
              <span class="material-symbols-outlined text-xs">trending_down</span> Top Net Sellers
            </h4>
            <div class="space-y-1">
              <div class="flex items-center justify-between font-numeric-data py-1 text-sm">
                <div class="flex items-center gap-2">
                  <span class="w-8 h-6 bg-error/10 text-error text-[10px] flex items-center justify-center rounded font-bold">PD</span>
                  <span class="text-slate-300">Indo Premier</span>
                </div>
                <span class="text-on-surface">92.4B</span>
              </div>
              <div class="flex items-center justify-between font-numeric-data py-1 text-sm">
                <div class="flex items-center gap-2">
                  <span class="w-8 h-6 bg-error/10 text-error text-[10px] flex items-center justify-center rounded font-bold">YP</span>
                  <span class="text-slate-300">Mirae Asset</span>
                </div>
                <span class="text-on-surface">71.0B</span>
              </div>
              <div class="flex items-center justify-between font-numeric-data py-1 text-sm">
                <div class="flex items-center gap-2">
                  <span class="w-8 h-6 bg-error/10 text-error text-[10px] flex items-center justify-center rounded font-bold">CC</span>
                  <span class="text-slate-300">Mandiri Sek</span>
                </div>
                <span class="text-on-surface">34.5B</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>

  <!-- Mini Insights Card -->
  <section class="bg-gradient-to-r from-[#159D91]/10 to-transparent border border-white/5 rounded-xl p-4 flex items-center gap-4">
    <div class="bg-primary p-4 rounded-full">
      <span class="material-symbols-outlined text-on-primary">psychology</span>
    </div>
    <div>
      <h4 class="font-headline-md text-body-lg text-on-surface">AI Market Sentiment</h4>
      <p class="text-slate-400 font-body-md text-body-md">Foreign flow detected on BBCA with strong technical support at 10,150. Potential breakout target at 10,500.</p>
    </div>
  </section>
</main>
  `;
}
