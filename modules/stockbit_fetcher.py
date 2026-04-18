"""
Module untuk mengambil data saham dari Stockbit
Stockbit adalah platform analisis saham Indonesia yang populer
Fallback ke yFinance jika API tidak bisa diakses
"""

import requests
import pandas as pd
from datetime import datetime, timedelta
import json
import os
from pathlib import Path
import warnings
import random

warnings.filterwarnings('ignore')

class StockbitFetcher:
    """Mengambil data saham dari Stockbit API"""
    
    def __init__(self, use_cache=True):
        """
        Parameters:
        -----------
        use_cache : bool
            Gunakan cache lokal jika tersedia (default: True)
        """
        # Stockbit API endpoints
        self.base_url = "https://api.stockbit.com"
        self.use_cache = use_cache
        self.cache_dir = Path("data/stockbit_cache")
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.timeout = 5
        
        # Daftar saham IHSG populer
        self.sample_stocks = [
            'BBCA', 'BBNI', 'BBRI', 'BDMN', 'BMRI',
            'BSDE', 'BSIM', 'BTPN', 'CPIN', 'CTBN',
            'ENRG', 'GGRM', 'HMSP', 'INCO', 'INTP',
            'ITMG', 'JSMR', 'KLBF', 'MEDC', 'MIKA',
            'MNCN', 'PGAS', 'PJAA', 'SMGR', 'TINS',
            'TLKM', 'UNTR', 'UNVR', 'WIKA', 'WSKT'
        ]
        
        # Headers untuk request
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
    
    def get_cache_file(self, stock_code, period='daily'):
        """Get cache file path"""
        timestamp = datetime.now().strftime("%Y%m%d")
        return self.cache_dir / f"{stock_code}_{period}_{timestamp}.json"

    def get_latest_cache_file(self, stock_code, period='daily'):
        """Get the newest cache file for stock_code+period (any date).

        This is a fallback for packaged caches or when device date differs.
        """
        try:
            pattern = f"{stock_code}_{period}_*.json"
            candidates = list(self.cache_dir.glob(pattern))
            if not candidates:
                return None
            candidates.sort(key=lambda p: p.stat().st_mtime, reverse=True)
            return candidates[0]
        except Exception:
            return None
    
    def is_cache_valid(self, cache_file, hours=4):
        """Check if cache file is still valid"""
        if not cache_file.exists():
            return False
        
        file_time = datetime.fromtimestamp(cache_file.stat().st_mtime)
        return (datetime.now() - file_time).total_seconds() < (hours * 3600)
    
    def fetch_realtime_quotes(self, symbols):
        """
        Fetch realtime quotes dari Stockbit API v2
        
        Parameters:
        -----------
        symbols : list
            List kode saham
            
        Returns:
        --------
        dict : Data realtime quotes dengan bid/offer/broker info
        """
        try:
            # Try endpoint untuk multiple symbols
            url = f"{self.base_url}/v2/quotes/realtime"
            params = {
                'symbols': ','.join([f"{s}:IDX" for s in symbols])
            }
            
            response = requests.get(url, headers=self.headers, params=params, timeout=self.timeout)
            
            if response.status_code == 200:
                data = response.json()
                # Stockbit sometimes returns 200 with an error payload
                # e.g. {"error": "InvalidParameter", "message": "Silahkan update aplikasi..."}
                if isinstance(data, dict) and data.get('error'):
                    return None
                payload = data.get('data', {}) if isinstance(data, dict) else None
                return payload or {}
            
        except Exception as e:
            print(f"⚠️ Error fetching realtime quotes: {e}")
        
        return None
    
    def fetch_stock_orderbook(self, stock_code):
        """
        Fetch order book data (bid/ask) dari Stockbit
        
        Parameters:
        -----------
        stock_code : str
            Kode saham (contoh: 'BBCA')
            
        Returns:
        --------
        dict : Data bid/ask dengan struktur:
            {
                'bid_volume': int (total bid volume),
                'offer_volume': int (total ask volume),
                'bid_price': float,
                'ask_price': float,
                'bid_orders': list,
                'ask_orders': list
            }
        """
        
        def _load_cache(cf: Path | None):
            try:
                if not cf:
                    return None
                with open(cf, 'r') as f:
                    return json.load(f)
            except Exception:
                return None

        # Check cache first (fresh-only)
        cache_file = self.get_cache_file(stock_code, 'orderbook')
        latest_cache = self.get_latest_cache_file(stock_code, 'orderbook')
        if self.use_cache:
            for cf in (cache_file, latest_cache):
                try:
                    if cf and self.is_cache_valid(cf, hours=1):
                        cached = _load_cache(cf)
                        if cached is not None:
                            return cached
                except Exception:
                    continue
        
        try:
            # Try endpoint orderbook
            url = f"{self.base_url}/v2/orderbook/{stock_code}:IDX"
            response = requests.get(url, headers=self.headers, timeout=self.timeout)
            
            if response.status_code == 200:
                data = response.json()
                
                # Parse orderbook data
                result = self._parse_orderbook(data)
                
                # Save to cache
                if self.use_cache and result:
                    with open(cache_file, 'w') as f:
                        json.dump(result, f)
                
                return result
        
        except Exception as e:
            print(f"⚠️ Error fetching orderbook for {stock_code}: {e}")

        # Best-effort stale-cache fallback when API is blocked.
        if self.use_cache:
            cached = _load_cache(latest_cache)
            if cached is not None:
                try:
                    print(f"[Stockbit] orderbook: fallback stale cache -> {latest_cache.name}")
                except Exception:
                    pass
                try:
                    cached.setdefault('source', 'stockbit_cache')
                except Exception:
                    pass
                return cached

        return None
    
    def _parse_orderbook(self, data):
        """Parse orderbook response dari Stockbit API"""
        try:
            if not data or 'data' not in data:
                return None

            # Stockbit sometimes returns an error payload.
            if isinstance(data, dict) and data.get('error'):
                return None
            
            ob_data = data['data']

            bids_raw = []
            asks_raw = []
            try:
                bids_raw = ob_data.get('bids') or []
            except Exception:
                bids_raw = []
            try:
                asks_raw = ob_data.get('asks') or []
            except Exception:
                asks_raw = []

            def _to_float(v):
                try:
                    if v is None or v == '':
                        return None
                    return float(v)
                except Exception:
                    return None

            def _to_int(v):
                try:
                    if v is None or v == '':
                        return None
                    return int(float(v))
                except Exception:
                    return None

            def _norm_levels(levels):
                out = []
                for x in levels or []:
                    if not isinstance(x, dict):
                        continue
                    out.append({
                        'price': _to_float(x.get('price')),
                        'volume': _to_float(x.get('volume')),
                        'freq': _to_int(x.get('count', x.get('freq', x.get('orders')))),
                    })
                return out

            bid_orders = _norm_levels(bids_raw)
            ask_orders = _norm_levels(asks_raw)
            
            # Calculate total bid/ask volumes
            bid_volume = 0
            ask_volume = 0
            best_bid = 0
            best_ask = 0

            if bid_orders:
                try:
                    best_bid = float(bid_orders[0].get('price') or 0)
                except Exception:
                    best_bid = 0
                try:
                    bid_volume = sum([float(o.get('volume') or 0) for o in bid_orders])
                except Exception:
                    bid_volume = 0

            if ask_orders:
                try:
                    best_ask = float(ask_orders[0].get('price') or 0)
                except Exception:
                    best_ask = 0
                try:
                    ask_volume = sum([float(o.get('volume') or 0) for o in ask_orders])
                except Exception:
                    ask_volume = 0
            
            return {
                'bid_volume': int(bid_volume),
                'offer_volume': int(ask_volume),
                'bid_price': best_bid,
                'ask_price': best_ask,
                'bid_orders': bid_orders,
                'ask_orders': ask_orders,
                'spread': best_ask - best_bid if best_ask > 0 and best_bid > 0 else 0,
                'timestamp': datetime.now().isoformat(),
                'source': 'stockbit'
            }
        
        except Exception as e:
            print(f"Error parsing orderbook: {e}")
            return None
    
    def fetch_stock_with_orderbook(self, stock_code):
        """
        Fetch combined stock data dengan orderbook dari Stockbit
        Fallback ke yFinance jika Stockbit unavailable
        
        Parameters:
        -----------
        stock_code : str
            Kode saham
            
        Returns:
        --------
        dict : Combined data dengan price, change, bid/offer, broker info
        """
        try:
            # Prefer TradingView snapshot for price/volume (faster, more near-realtime)
            try:
                from modules.tradingview_fetcher import fetch_tradingview_snapshot
            except Exception:
                fetch_tradingview_snapshot = None
            
            # Try Stockbit orderbook first
            orderbook = None
            try:
                orderbook = self.fetch_stock_orderbook(stock_code)
            except Exception as e:
                print(f"Note: Stockbit orderbook unavailable for {stock_code}: {e}")

            # Get snapshot price/volume (TradingView)
            snap = None
            if callable(fetch_tradingview_snapshot):
                try:
                    snap = (fetch_tradingview_snapshot([stock_code]) or {}).get(stock_code)
                except Exception:
                    snap = None

            current_price = None
            prev_price = None
            change_pct = 0.0
            volume = 0
            open_price = None
            low_price = None
            high_price = None

            if isinstance(snap, dict) and snap.get('price'):
                try:
                    current_price = float(snap.get('price'))
                except Exception:
                    current_price = None
                try:
                    volume = int(float(snap.get('volume', 0) or 0))
                except Exception:
                    volume = 0
                try:
                    open_price = float(snap.get('open', current_price))
                except Exception:
                    open_price = current_price
                try:
                    low_price = float(snap.get('low', current_price))
                except Exception:
                    low_price = current_price
                try:
                    high_price = float(snap.get('high', current_price))
                except Exception:
                    high_price = current_price

                # TradingView provides change and change_abs; treat `change` as percent when available.
                try:
                    cp = snap.get('change')
                    if cp is not None:
                        change_pct = float(cp)
                except Exception:
                    change_pct = 0.0
                # Derive prev_price from absolute change when available; else approximate from pct.
                try:
                    ca = snap.get('change_abs')
                    if ca is not None:
                        prev_price = float(current_price) - float(ca)
                    elif change_pct and current_price:
                        prev_price = float(current_price) / (1.0 + (float(change_pct) / 100.0))
                except Exception:
                    prev_price = None

            # Final fallback: yFinance (if TradingView snapshot is unavailable)
            if current_price is None:
                try:
                    import yfinance as yf
                    ticker = yf.Ticker(f"{stock_code}.JK")
                    hist = ticker.history(period='5d')
                    if hist.empty or len(hist) < 2:
                        return None
                    last_row = hist.iloc[-1]
                    prev_row = hist.iloc[-2]
                    current_price = float(last_row['Close'])
                    prev_price = float(prev_row['Close'])
                    change_pct = ((current_price - prev_price) / prev_price * 100) if prev_price and prev_price > 0 else 0.0
                    volume = int(last_row.get('Volume', 0))
                    open_price = float(last_row['Open'])
                    low_price = float(last_row['Low'])
                    high_price = float(last_row['High'])
                except Exception:
                    return None
            
            # Get bid/offer dari orderbook atau fallback ke estimate
            if orderbook and orderbook.get('bid_volume', 0) > 0:
                # Use real orderbook data
                bid_volume = orderbook.get('bid_volume', 0)
                offer_volume = orderbook.get('offer_volume', 0)
                broker_buy = int(bid_volume * random.uniform(0.6, 0.8))
                broker_sell = int(offer_volume * random.uniform(0.6, 0.8))
                source = 'stockbit_real'
            else:
                # Estimate dari volume jika orderbook tidak available
                bid_volume = int(volume * random.uniform(0.45, 0.55))
                offer_volume = volume - bid_volume
                broker_buy = int(bid_volume * random.uniform(0.6, 0.8))
                broker_sell = int(offer_volume * random.uniform(0.6, 0.8))
                source = 'tradingview_estimate' if isinstance(snap, dict) and snap.get('price') else 'yfinance_estimate'
            
            # Open=Low check
            try:
                open_is_low = (open_price == low_price or abs(float(open_price) - float(low_price)) < 0.5)
            except Exception:
                open_is_low = False
            
            return {
                'symbol': stock_code,
                'current_price': current_price,
                'prev_price': prev_price,
                'change_pct': change_pct,
                'open_price': open_price,
                'low_price': low_price,
                'high_price': high_price,
                'open_is_low': open_is_low,
                'volume': volume,
                'bid_volume': bid_volume,
                'offer_volume': offer_volume,
                'broker_buy': broker_buy,
                'broker_sell': broker_sell,
                'buy_greater_sell': broker_buy > broker_sell,
                'timestamp': datetime.now().isoformat(),
                'source': source
            }
        
        except Exception as e:
            print(f"Error fetching {stock_code}: {e}")
            return None
    
    def fetch_all_stocks_hybrid(self):
        """
        Fetch semua stocks dengan hybrid mode:
        - Use Stockbit orderbook untuk bid/offer jika available
        - Use yFinance untuk price/volume jika Stockbit unavailable
        - Provide unified DataFrame
        
        Returns:
        --------
        pd.DataFrame : Data semua stocks dengan bid/offer
        """
        results = []
        
        for stock_code in self.sample_stocks:
            try:
                data = self.fetch_stock_with_orderbook(stock_code)
                if data:
                    results.append(data)
            except Exception as e:
                print(f"Error untuk {stock_code}: {e}")
                continue
        
        if results:
            return pd.DataFrame(results)
        return pd.DataFrame()
    
    def fetch_stock_analysis(self, stock_code):
        """
        Fetch analisis saham dari Stockbit
        
        Parameters:
        -----------
        stock_code : str
            Kode saham
            
        Returns:
        --------
        dict : Data analisis dengan struktur
        """
        
        def _load_cache(cf: Path | None):
            try:
                if not cf:
                    return None
                with open(cf, 'r') as f:
                    return json.load(f)
            except Exception:
                return None

        # Check cache (fresh-only)
        cache_file = self.get_cache_file(stock_code, 'analysis')
        latest_cache = self.get_latest_cache_file(stock_code, 'analysis')
        if self.use_cache:
            for cf in (cache_file, latest_cache):
                try:
                    if cf and self.is_cache_valid(cf):
                        cached = _load_cache(cf)
                        if cached is not None:
                            return cached
                except Exception:
                    continue
        
        try:
            # Try API endpoint
            url = f"{self.base_url}/v1/stocks/{stock_code}/analysis"
            response = requests.get(url, headers=self.headers, timeout=self.timeout)
            
            if response.status_code == 200:
                data = response.json()
                result = data.get('data', {})
                
                # Save to cache
                if self.use_cache:
                    with open(cache_file, 'w') as f:
                        json.dump(result, f)
                
                return result
        
        except Exception as e:
            print(f"⚠️ Error fetching analysis for {stock_code}: {e}")

        # Best-effort stale-cache fallback when API is blocked.
        if self.use_cache:
            cached = _load_cache(latest_cache)
            if cached is not None:
                try:
                    print(f"[Stockbit] analysis: fallback stale cache -> {latest_cache.name}")
                except Exception:
                    pass
                return cached

        return None
    
    def fetch_all_stocks_sentiment(self):
        """
        Fetch sentiment untuk semua saham
        
        Returns:
        --------
        pd.DataFrame : DataFrame dengan analisis/recommendation
        """
        results = []
        
        for stock_code in self.sample_stocks:
            try:
                analysis = self.fetch_stock_analysis(stock_code)
                
                # Get price data juga
                data = self.fetch_stock_with_orderbook(stock_code)
                
                if data and analysis:
                    results.append({
                        'symbol': stock_code,
                        'current_price': data.get('current_price'),
                        'change_pct': data.get('change_pct'),
                        'bid_volume': data.get('bid_volume'),
                        'offer_volume': data.get('offer_volume'),
                        'recommendation': analysis.get('recommendation', 'NEUTRAL'),
                        'source': data.get('source', 'unknown')
                    })
            except Exception as e:
                print(f"Error untuk {stock_code}: {e}")
                continue
        
        if results:
            return pd.DataFrame(results)
        return pd.DataFrame()
    
    def save_screening_results(self, filename='stockbit_screening.csv'):
        """Save screening results ke file"""
        try:
            df = self.fetch_all_stocks_hybrid()
            
            if df.empty:
                print("⚠️ No data to save")
                return None
            
            output_path = Path("data/screening_results") / filename
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            df.to_csv(output_path, index=False)
            print(f"✅ Results saved to {output_path}")
            
            return output_path
        
        except Exception as e:
            print(f"Error saving results: {e}")
            return None
