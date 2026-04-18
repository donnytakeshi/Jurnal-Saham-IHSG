"""
Stockbit Web Scraper untuk mengambil bid/offer data real-time
Scraping dari halaman publik Stockbit.com
"""

import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
import time
from pathlib import Path
import json
import warnings

warnings.filterwarnings('ignore')

class StockbitScraper:
    """Scrape real-time stock data dari Stockbit.com"""
    
    def __init__(self, use_cache=True, cache_ttl_minutes=5):
        """
        Parameters:
        -----------
        use_cache : bool
            Cache hasil scraping untuk avoid overloading Stockbit
        cache_ttl_minutes : int
            Berapa menit cache tetap valid
        """
        self.base_url = "https://stockbit.com"
        self.use_cache = use_cache
        self.cache_ttl_minutes = cache_ttl_minutes
        self.cache_dir = Path("data/stockbit_scrape_cache")
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        # Headers untuk appear sebagai browser normal
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/*,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9,id;q=0.8',
            'Referer': 'https://stockbit.com/',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        }
        
        self.session = requests.Session()
        self.session.headers.update(self.headers)
    
    def is_cache_valid(self, cache_file):
        """Check if cache file is still valid"""
        if not cache_file.exists():
            return False
        
        file_time = datetime.fromtimestamp(cache_file.stat().st_mtime)
        age_minutes = (datetime.now() - file_time).total_seconds() / 60
        return age_minutes < self.cache_ttl_minutes
    
    def get_cache_file(self, stock_code):
        """Get cache file path for a stock"""
        return self.cache_dir / f"{stock_code}_data.json"
    
    def scrape_stock_page(self, stock_code):
        """
        Scrape data dari halaman stock Stockbit
        URL: https://stockbit.com/stocks/BBCA
        
        Parameters:
        -----------
        stock_code : str
            Kode saham (contoh: BBCA)
            
        Returns:
        --------
        dict : Data stock dengan struktur:
            {
                'symbol': str,
                'current_price': float,
                'price_change': float,
                'price_change_pct': float,
                'bid_price': float,
                'bid_volume': int,
                'ask_price': float,
                'ask_volume': int,
                'volume': int,
                'timestamp': str,
                'source': 'stockbit_scrape'
            }
        """
        
        # Check cache dulu
        cache_file = self.get_cache_file(stock_code)
        if self.use_cache and self.is_cache_valid(cache_file):
            try:
                with open(cache_file, 'r') as f:
                    return json.load(f)
            except:
                pass
        
        try:
            # Request halaman stock Stockbit
            url = f"{self.base_url}/stocks/{stock_code}"
            print(f"🔄 Scraping {stock_code} dari {url}...")
            
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            # Parse HTML
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract data dari berbagai selector CSS / struktur HTML
            data = self._extract_stock_data(soup, stock_code)
            
            # Cek validitas data
            if data and data.get('current_price', 0) > 0:
                # Save to cache
                if self.use_cache:
                    with open(cache_file, 'w') as f:
                        json.dump(data, f)
                
                print(f"✅ {stock_code}: Harga {data['current_price']}, Bid {data['bid_volume']}, Ask {data['ask_volume']}")
                return data
            else:
                print(f"⚠️ {stock_code}: Data tidak lengkap atau halaman structure berubah")
                return None
        
        except Exception as e:
            print(f"❌ Error scraping {stock_code}: {e}")
            return None
    
    def _extract_stock_data(self, soup, stock_code):
        """Extract data dari HTML Stockbit"""
        try:
            data = {
                'symbol': stock_code,
                'current_price': 0,
                'price_change': 0,
                'price_change_pct': 0,
                'bid_price': 0,
                'bid_volume': 0,
                'ask_price': 0,
                'ask_volume': 0,
                'volume': 0,
                'timestamp': datetime.now().isoformat(),
                'source': 'stockbit_scrape'
            }
            
            # Try berbagai selector untuk extract price
            # Selector 1: Cari div dengan class yang contain "price"
            price_elements = soup.find_all(['span', 'div'], class_=lambda x: x and ('price' in x.lower() or 'harga' in x.lower()))
            
            if price_elements:
                # Ambil element pertama yang punya angka
                for elem in price_elements:
                    text = elem.get_text(strip=True)
                    try:
                        price = float(text.replace(',', '').replace('.', '').replace('Rp', '').strip())
                        if price > 100:  # Valid price
                            data['current_price'] = price
                            break
                    except:
                        continue
            
            # Try extract bid/ask dari data attributes atau text yang mengandung "Bid", "Ask"
            text_content = soup.get_text()
            
            # Cari pattern untuk bid volume
            if 'Bid' in text_content or 'bid' in text_content:
                # Cari angka setelah "Bid"
                bid_pattern = soup.find(text=lambda x: x and 'Bid' in x)
                if bid_pattern:
                    # Extract number yg muncul setelah
                    try:
                        parent = bid_pattern.parent
                        volume_text = parent.get_text()
                        # Simple extraction - cari angka yang paling besar
                        import re
                        numbers = re.findall(r'\d+(?:[.,]\d{3})*', volume_text)
                        if numbers:
                            data['bid_volume'] = int(numbers[-1].replace(',', '').replace('.', ''))
                    except:
                        pass
            
            # Cari pattern untuk ask volume
            if 'Ask' in text_content or 'ask' in text_content or 'Penawaran' in text_content:
                ask_pattern = soup.find(text=lambda x: x and ('Ask' in x or 'ask' in x or 'Penawaran' in x))
                if ask_pattern:
                    try:
                        parent = ask_pattern.parent
                        volume_text = parent.get_text()
                        import re
                        numbers = re.findall(r'\d+(?:[.,]\d{3})*', volume_text)
                        if numbers:
                            data['ask_volume'] = int(numbers[-1].replace(',', '').replace('.', ''))
                    except:
                        pass
            
            # Try extract volume dari text yang contain "Volume"
            volume_text = soup.find(text=lambda x: x and 'Volume' in x)
            if volume_text:
                try:
                    parent = volume_text.parent
                    vol_str = parent.get_text()
                    import re
                    numbers = re.findall(r'\d+(?:[.,]\d{3})*', vol_str)
                    if numbers:
                        data['volume'] = int(numbers[-1].replace(',', '').replace('.', ''))
                except:
                    pass
            
            # Fallback: cari data dalam JSON/script tags
            scripts = soup.find_all('script')
            for script in scripts:
                if script.string and 'price' in script.string.lower():
                    try:
                        # Attempt to extract JSON data dari script
                        json_match = script.string
                        if '{' in json_match and '}' in json_match:
                            # Sederhana: cari angka yang mungkin harga
                            import re
                            prices = re.findall(r'"price":\s*(\d+(?:\.\d{2})?)', json_match, re.IGNORECASE)
                            if prices:
                                data['current_price'] = float(prices[0])
                    except:
                        pass
            
            return data
        
        except Exception as e:
            print(f"Error extracting data: {e}")
            return None
    
    def scrape_multiple_stocks(self, stock_codes):
        """
        Scrape multiple stocks sekaligus
        
        Parameters:
        -----------
        stock_codes : list
            List kode saham
            
        Returns:
        --------
        pd.DataFrame : DataFrame dengan data semua stocks
        """
        results = []
        
        for stock_code in stock_codes:
            data = self.scrape_stock_page(stock_code)
            if data:
                results.append(data)
            
            # Jangan stress server Stockbit - tunggu beberapa detik
            time.sleep(1)
        
        if results:
            return pd.DataFrame(results)
        return pd.DataFrame()
    
    def get_daily_stocks_data(self, stock_codes=None):
        """
        Get data untuk daily screening
        
        Parameters:
        -----------
        stock_codes : list, optional
            List kode saham. Jika None, gunakan list populer
            
        Returns:
        --------
        pd.DataFrame : Stock data dengan bid/ask
        """
        if stock_codes is None:
            # Default: saham paling populer
            stock_codes = [
                'BBCA', 'BBRI', 'BMRI', 'ASII', 'TLKM',
                'JSMR', 'INTP', 'UNTR', 'GGRM', 'HMSP',
                'EXCL', 'BSDE', 'CPIN', 'SMGR', 'INCO',
                'ITMG', 'PGAS', 'MEDC', 'BFIN', 'CLPI'
            ]
        
        print(f"🔄 Scraping {len(stock_codes)} saham dari Stockbit...")
        return self.scrape_multiple_stocks(stock_codes)
    
    def clear_cache(self):
        """Clear semua cache"""
        import shutil
        if self.cache_dir.exists():
            shutil.rmtree(self.cache_dir)
            self.cache_dir.mkdir(parents=True, exist_ok=True)
            print("✅ Cache cleared")


# Deprecated: API scraper (untuk reference jika ada endpoint baru)
class StockbitAPIFallback:
    """Fallback scraper jika API endpoint berubah"""
    
    @staticmethod
    def try_alternative_endpoints():
        """
        Try berbagai endpoint API yang mungkin aktif
        Returns list dari endpoints yang responsive
        """
        endpoints = [
            "https://api.stockbit.com/v2/quotes/realtime",
            "https://api.stockbit.com/v1/quotes",
            "https://api.stockbit.com/market/realtime",
            "https://data.stockbit.com/api/quotes",
            "https://stockbit.com/api/stocks",
        ]
        
        working_endpoints = []
        for endpoint in endpoints:
            try:
                r = requests.get(endpoint, timeout=3)
                if r.status_code != 405:  # Jika bukan "Method Not Allowed"
                    working_endpoints.append(endpoint)
            except:
                pass
        
        return working_endpoints
