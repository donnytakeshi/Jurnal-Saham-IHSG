from flask import Flask, jsonify, request, Response, stream_with_context
from flask_cors import CORS
import yfinance as yf
import requests
from bs4 import BeautifulSoup
import json
import re
import uuid
import os
import time
import base64
import random
import logging
from datetime import datetime, timedelta
from functools import wraps
from collections import OrderedDict
from typing import Dict, List, Optional, Tuple
from fake_useragent import UserAgent
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import PyPDF2
import docx
import csv
import tempfile
from werkzeug.utils import secure_filename

app = Flask(__name__)
CORS(app)

# ============ API KEYS ============
FINNHUB_KEY = "d7gr8j1r01qmqj46en20d7gr8j1r01qmqj46en2g"
ALPHA_VANTAGE_KEY = "KJ32W2P0SGKC4E19"
DEEPSEEK_API_KEY = "sk-0422844a615144caabf1fd149087463e"
DEEPSEEK_API_URL = "https://api.deepseek.com/v1/chat/completions"

# ============ UPLOAD CONFIGURATION ============
UPLOAD_FOLDER = "uploads"
ALLOWED_EXTENSIONS = {
    'txt', 'pdf', 'doc', 'docx', 'csv', 'json',
    'png', 'jpg', 'jpeg', 'gif', 'bmp', 'tiff'
}
MAX_FILE_SIZE = 10 * 1024 * 1024

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# ============ LOGGING SETUP ============
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def is_image_file(filename):
    ext = filename.rsplit('.', 1)[1].lower()
    return ext in ['png', 'jpg', 'jpeg', 'gif', 'bmp', 'tiff']

def file_to_base64(file_path):
    with open(file_path, 'rb') as f:
        return base64.b64encode(f.read()).decode('utf-8')

def extract_text_from_pdf(file_path):
    try:
        text = ""
        with open(file_path, 'rb') as f:
            reader = PyPDF2.PdfReader(f)
            for page in reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
        return text.strip()
    except Exception as e:
        print(f"PDF extraction error: {e}")
        return None

def extract_text_from_docx(file_path):
    try:
        doc = docx.Document(file_path)
        text = "\n".join([para.text for para in doc.paragraphs])
        return text.strip()
    except Exception as e:
        print(f"DOCX extraction error: {e}")
        return None

def extract_text_from_csv(file_path):
    try:
        text = ""
        with open(file_path, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            for row in reader:
                text += ", ".join(row) + "\n"
        return text.strip()
    except Exception as e:
        print(f"CSV extraction error: {e}")
        return None

def extract_text_from_txt(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read().strip()
    except Exception as e:
        print(f"TXT extraction error: {e}")
        return None

def extract_text_from_file(file_path, filename):
    ext = filename.rsplit('.', 1)[1].lower()
    
    if ext == 'pdf':
        return extract_text_from_pdf(file_path)
    elif ext in ['doc', 'docx']:
        return extract_text_from_docx(file_path)
    elif ext == 'csv':
        return extract_text_from_csv(file_path)
    elif ext == 'txt':
        return extract_text_from_txt(file_path)
    elif ext == 'json':
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read().strip()
    
    return None

# ============ SIMPLE CACHE SYSTEM ============
class SimpleCache:
    def __init__(self, ttl=15):
        self.cache = OrderedDict()
        self.ttl = ttl

    def get(self, key):
        if key in self.cache:
            data, timestamp = self.cache[key]
            if datetime.now() - timestamp < timedelta(seconds=self.ttl):
                return data
            else:
                del self.cache[key]
        return None

    def set(self, key, value):
        if len(self.cache) > 100:
            self.cache.popitem(last=False)
        self.cache[key] = (value, datetime.now())

    def clear(self):
        self.cache.clear()

quote_cache = SimpleCache(ttl=15)
fundamental_cache = SimpleCache(ttl=300)
orderbook_cache = SimpleCache(ttl=30)

# ============ MEMORY STORAGE ============
conversation_memory = {}
MEMORY_FILE = "conversation_memory.json"

def load_memory():
    global conversation_memory
    if os.path.exists(MEMORY_FILE):
        try:
            with open(MEMORY_FILE, 'r') as f:
                conversation_memory = json.load(f)
        except:
            conversation_memory = {}

def save_memory():
    with open(MEMORY_FILE, 'w') as f:
        json.dump(conversation_memory, f)

def get_session_history(session_id):
    if session_id not in conversation_memory:
        conversation_memory[session_id] = []
    return conversation_memory[session_id]

def add_to_history(session_id, role, content):
    history = get_session_history(session_id)
    history.append({
        "role": role,
        "content": content,
        "timestamp": datetime.now().isoformat()
    })
    if len(history) > 20:
        conversation_memory[session_id] = history[-20:]
    save_memory()

def clear_session_history(session_id):
    if session_id in conversation_memory:
        conversation_memory[session_id] = []
        save_memory()

def build_messages_with_history(session_id, system_prompt, user_message):
    history = get_session_history(session_id)
    messages = [{"role": "system", "content": system_prompt}]
    recent_history = history[-10:] if len(history) > 10 else history
    messages.extend(recent_history)
    messages.append({"role": "user", "content": user_message})
    return messages

load_memory()

# ============ HELPER FUNCTIONS ============
def get_stock_name(symbol):
    names = {
        "BBCA": "PT Bank Central Asia Tbk.", "BBRI": "PT Bank Rakyat Indonesia Tbk.",
        "BMRI": "PT Bank Mandiri Tbk.", "TLKM": "PT Telkom Indonesia Tbk.",
        "ASII": "PT Astra International Tbk.", "GOTO": "PT GoTo Gojek Tokopedia Tbk.",
        "UNVR": "PT Unilever Indonesia Tbk.", "ADRO": "PT Adaro Energy Tbk.",
        "CPIN": "PT Charoen Pokphand Indonesia Tbk.", "ICBP": "PT Indofood CBP Tbk.",
        "INDF": "PT Indofood Sukses Makmur Tbk.", "MEDC": "PT Medco Energi Internasional Tbk.",
        "PGAS": "PT Perusahaan Gas Negara Tbk.", "SMGR": "PT Semen Indonesia Tbk.",
        "ANTM": "PT Aneka Tambang Tbk.", "HRUM": "PT Harum Energy Tbk.",
        "TOWR": "PT Sarana Menara Nusantara Tbk.", "ERAA": "PT Erajaya Swasembada Tbk.",
        "SIDO": "PT Sido Muncul Tbk.", "JPFA": "PT Japfa Comfeed Tbk.",
        "MDKA": "PT Merdeka Copper Gold Tbk.", "INKP": "PT Indah Kiat Pulp & Paper Tbk.",
        "TKIM": "PT Pabrik Kertas Tjiwi Kimia Tbk.", "BRIS": "PT Bank BRISyariah Tbk.",
        "BBNI": "PT Bank Negara Indonesia Tbk.", "UNTR": "PT United Tractors Tbk.",
        "WIKA": "PT Wijaya Karya Tbk.", "AMMN": "PT Amman Mineral Internasional Tbk.",
        "RAJA": "PT Rukun Raharja Tbk.",
        "BUMI": "PT Bumi Resources Tbk."
    }
    return names.get(symbol, symbol)

def get_stock_sector(symbol):
    sectors = {
        "BBCA": "Finance", "BBRI": "Finance", "BMRI": "Finance", "BRIS": "Finance", "BBNI": "Finance",
        "TLKM": "Technology", "GOTO": "Technology", "TOWR": "Technology", "ERAA": "Technology",
        "ADRO": "Energy", "MEDC": "Energy", "PGAS": "Energy", "HRUM": "Energy", "MDKA": "Energy",
        "CPIN": "Consumer", "ICBP": "Consumer", "INDF": "Consumer", "UNVR": "Consumer", "SIDO": "Consumer", "JPFA": "Consumer",
        "ASII": "Consumer", "SMGR": "Consumer", "ANTM": "Consumer", "INKP": "Consumer", "TKIM": "Consumer",
        "UNTR": "Consumer", "WIKA": "Consumer", "AMMN": "Energy",
        "RAJA": "Energy", "BUMI": "Energy"
    }
    return sectors.get(symbol, "IDX: Others")

def get_avg_volume(symbol):
    quote = fetch_quote_with_fallback(symbol)
    price = quote.get('price', 5000)
    if price > 10000:
        return 2000000
    elif price < 1000:
        return 5000000
    return 3000000

# ============ MARKET DATA FETCHERS ============
def fetch_from_finnhub(symbol):
    try:
        url = f"https://finnhub.io/api/v1/quote?symbol={symbol}.JK&token={FINNHUB_KEY}"
        response = requests.get(url, timeout=5)
        data = response.json()
        if data.get('c') and data['c'] > 0:
            return {
                'success': True,
                'source': 'finnhub',
                'price': data['c'],
                'changePercent': data['dp'],
                'volume': data.get('v', 0)
            }
        return {'success': False}
    except Exception as e:
        return {'success': False}

def fetch_from_alpha_vantage(symbol):
    try:
        url = f"https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={symbol}.JK&apikey={ALPHA_VANTAGE_KEY}"
        response = requests.get(url, timeout=5)
        data = response.json()
        quote = data.get('Global Quote', {})
        if quote.get('05. price'):
            return {
                'success': True,
                'source': 'alphavantage',
                'price': float(quote['05. price']),
                'changePercent': float(quote['10. change percent'].replace('%', '')) if quote.get('10. change percent') else 0,
                'volume': int(quote.get('06. volume', 0))
            }
        return {'success': False}
    except Exception as e:
        return {'success': False}

def fetch_from_yfinance(symbol):
    try:
        yf_symbol = f"{symbol}.JK"
        ticker = yf.Ticker(yf_symbol)
        info = ticker.info
        price = info.get('regularMarketPrice', 0)
        prev_close = info.get('previousClose', price)
        return {
            'success': True,
            'source': 'yfinance',
            'price': price if price else prev_close,
            'changePercent': info.get('regularMarketChangePercent', 0),
            'volume': info.get('regularMarketVolume', 0)
        }
    except Exception as e:
        return {'success': False}

def fetch_quote_with_fallback(symbol):
    cache_key = f"quote_{symbol}"
    cached = quote_cache.get(cache_key)
    if cached:
        cached['cached'] = True
        return cached

    for fetcher in [fetch_from_finnhub, fetch_from_alpha_vantage, fetch_from_yfinance]:
        result = fetcher(symbol)
        if result['success']:
            result['cached'] = False
            quote_cache.set(cache_key, result)
            return result

    return {
        'success': True,
        'source': 'simulated',
        'cached': False,
        'price': 5000,
        'changePercent': 0,
        'volume': 1000000
    }

def get_keystats_data(symbol):
    quote = fetch_quote_with_fallback(symbol)
    price = quote.get('price', 0)
    volume = quote.get('volume', 0)
    prev_close = quote.get('prevClose', price) if quote.get('prevClose') else price
    change_pct = quote.get('changePercent', 0)

    lot = int(volume / 100) if volume > 0 else 0
    ara = prev_close * 1.25 if prev_close else 0
    arb = prev_close * 0.75 if prev_close else 0
    val = (price * volume) / 1000000000 if price and volume else 0

    now = datetime.now()
    is_trading = (9 <= now.hour < 16) and now.weekday() < 5
    is_closed = not is_trading

    return {
        'symbol': symbol,
        'price': price,
        'changePercent': change_pct,
        'isClosed': is_closed,
        'prev': prev_close,
        'open': quote.get('open', price),
        'high': quote.get('high', price),
        'low': quote.get('low', price),
        'lot': lot,
        'ara': ara,
        'arb': arb,
        'val': val,
        'name': get_stock_name(symbol),
        'sector': get_stock_sector(symbol),
        'source': quote.get('source', 'unknown')
    }

def get_bandarmology_analysis(symbol):
    quote = fetch_quote_with_fallback(symbol)
    price = quote.get('price', 0)
    change_pct = quote.get('changePercent', 0)
    volume = quote.get('volume', 0)
    avg_vol = get_avg_volume(symbol)
    volume_ratio = volume / avg_vol if avg_vol > 0 else 1
    volume_ratio = min(volume_ratio, 3.0)

    is_accumulation = volume_ratio > 1.2 and change_pct > 0
    is_breakout = change_pct > 2 and volume_ratio > 1.5

    potential = abs(change_pct) * 1.5
    if is_accumulation:
        potential = max(potential, 6)
    if is_breakout:
        potential = max(potential, 8)

    return {
        'symbol': symbol,
        'name': get_stock_name(symbol),
        'price': price,
        'changePercent': round(change_pct, 2),
        'volumeRatio': round(volume_ratio, 1),
        'isAccumulation': is_accumulation,
        'isBreakout': is_breakout,
        'potentialGain': round(potential, 1),
        'signal': 'ACCUMULATION' if is_accumulation else ('BREAKOUT' if is_breakout else 'NEUTRAL'),
        'recommendation': 'BUY' if (is_accumulation or is_breakout) and change_pct > 0 else 'HOLD',
        'source': quote.get('source', 'unknown')
    }

def get_top_predictions(limit=8):
    results = []
    top_symbols = ["BBCA", "BBRI", "BMRI", "TLKM", "ASII", "ADRO", "UNVR", "GOTO", "RAJA", "BUMI"]
    for symbol in top_symbols:
        analysis = get_bandarmology_analysis(symbol)
        if analysis.get('price', 0) > 0:
            results.append(analysis)
    results.sort(key=lambda x: x.get('potentialGain', 0), reverse=True)
    return results[:limit]

# ============ ULTRA RESILIENT ORDER BOOK SCRAPER ============

class UltraResilientOrderBookScraper:
    """Ultra resilient scraper for IHSG order book data"""
    
    def __init__(self, use_proxy: bool = False, proxy_list: List[str] = None):
        self.session = self._create_session()
        self.ua = UserAgent()
        self.use_proxy = use_proxy
        self.proxy_list = proxy_list or []
        self.cache = {}
        self.request_count = 0
        self.last_request_time = 0
        self.min_request_interval = 1
        
        self.sources = [
            self._get_from_yfinance,
            self._get_from_idx_website,
            self._get_from_investing_com
        ]
    
    def _create_session(self) -> requests.Session:
        session = requests.Session()
        retry = Retry(
            total=3,
            read=3,
            connect=3,
            backoff_factor=0.5,
            status_forcelist=[500, 502, 503, 504]
        )
        adapter = HTTPAdapter(max_retries=retry)
        session.mount('http://', adapter)
        session.mount('https://', adapter)
        return session
    
    def _get_headers(self) -> Dict:
        return {
            'User-Agent': self.ua.random,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
        }
    
    def _get_proxy(self) -> Optional[Dict]:
        if self.use_proxy and self.proxy_list:
            proxy = random.choice(self.proxy_list)
            return {'http': proxy, 'https': proxy}
        return None
    
    def _rate_limit(self):
        elapsed = time.time() - self.last_request_time
        if elapsed < self.min_request_interval:
            time.sleep(self.min_request_interval - elapsed)
        self.last_request_time = time.time()
    
    def _exponential_backoff(self, attempt: int) -> float:
        return min(2 ** attempt, 10) + random.uniform(0, 1)
    
    def _get_from_yfinance(self, stock_code: str) -> Optional[Dict]:
        try:
            logger.info(f"Attempting Yahoo Finance for {stock_code}")
            ticker = yf.Ticker(f"{stock_code}.JK")
            info = ticker.info
            
            if not info:
                return None
            
            orderbook = {
                'source': 'Yahoo Finance',
                'bid_price': info.get('bid', 0),
                'bid_size': info.get('bidSize', 0),
                'ask_price': info.get('ask', 0),
                'ask_size': info.get('askSize', 0),
                'last_price': info.get('regularMarketPrice', 0),
                'volume': info.get('volume', 0),
                'timestamp': datetime.now().isoformat()
            }
            
            hist = ticker.history(period="1d", interval="1m")
            if not hist.empty:
                orderbook['open'] = hist['Open'].iloc[-1]
                orderbook['high'] = hist['High'].iloc[-1]
                orderbook['low'] = hist['Low'].iloc[-1]
            
            if orderbook['bid_price'] > 0 or orderbook['ask_price'] > 0:
                return orderbook
            return None
            
        except Exception as e:
            logger.warning(f"Yahoo Finance error for {stock_code}: {str(e)}")
            return None
    
    def _get_from_idx_website(self, stock_code: str) -> Optional[Dict]:
        try:
            logger.info(f"Attempting IDX website for {stock_code}")
            self._rate_limit()
            
            url = f"https://www.idx.co.id/primary/StockSummary/GetStockSummary?kodeEmiten={stock_code}"
            
            response = self.session.get(
                url, 
                headers=self._get_headers(),
                proxies=self._get_proxy(),
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                if data and len(data) > 0:
                    stock_data = data[0]
                    
                    orderbook = {
                        'source': 'IDX Official',
                        'stock_code': stock_code,
                        'last_price': stock_data.get('LastPrice', 0),
                        'open_price': stock_data.get('OpenPrice', 0),
                        'close_price': stock_data.get('ClosePrice', 0),
                        'volume': stock_data.get('Volume', 0),
                        'value': stock_data.get('Value', 0),
                        'frequency': stock_data.get('Frequency', 0),
                        'timestamp': datetime.now().isoformat()
                    }
                    
                    depth_url = f"https://www.idx.co.id/primary/MarketDepth/GetMarketDepth?kodeEmiten={stock_code}"
                    depth_response = self.session.get(
                        depth_url,
                        headers=self._get_headers(),
                        proxies=self._get_proxy(),
                        timeout=10
                    )
                    
                    if depth_response.status_code == 200:
                        depth_data = depth_response.json()
                        if depth_data:
                            bids = []
                            asks = []
                            
                            for item in depth_data:
                                if item.get('Side') == 'B':
                                    bids.append({
                                        'price': item.get('Price', 0),
                                        'volume': item.get('Volume', 0),
                                        'freq': item.get('Frequency', random.randint(1, 20))
                                    })
                                elif item.get('Side') == 'S':
                                    asks.append({
                                        'price': item.get('Price', 0),
                                        'volume': item.get('Volume', 0),
                                        'freq': item.get('Frequency', random.randint(1, 20))
                                    })
                            
                            orderbook['bids'] = bids[:10]
                            orderbook['asks'] = asks[:10]
                            orderbook['bid_count'] = len(bids)
                            orderbook['ask_count'] = len(asks)
                    
                    return orderbook
            return None
            
        except Exception as e:
            logger.warning(f"IDX website error for {stock_code}: {str(e)}")
            return None
    
    def _get_from_investing_com(self, stock_code: str) -> Optional[Dict]:
        try:
            logger.info(f"Attempting Investing.com for {stock_code}")
            self._rate_limit()
            
            url = f"https://www.investing.com/equities/{stock_code.lower()}"
            
            response = self.session.get(
                url,
                headers=self._get_headers(),
                proxies=self._get_proxy(),
                timeout=10
            )
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                
                bid_element = soup.find('span', {'data-test': 'bid-price'})
                ask_element = soup.find('span', {'data-test': 'ask-price'})
                
                if bid_element and ask_element:
                    orderbook = {
                        'source': 'Investing.com',
                        'bid_price': float(bid_element.text.replace(',', '')),
                        'ask_price': float(ask_element.text.replace(',', '')),
                        'timestamp': datetime.now().isoformat()
                    }
                    return orderbook
            return None
            
        except Exception as e:
            logger.warning(f"Investing.com error for {stock_code}: {str(e)}")
            return None
    
    def fetch_orderbook(self, stock_code: str, max_retries: int = 3) -> Dict:
        stock_code = stock_code.upper().replace('.JK', '')
        
        cache_key = f"{stock_code}_{int(time.time() / 5)}"
        if cache_key in self.cache:
            logger.info(f"Returning cached data for {stock_code}")
            return self.cache[cache_key]
        
        for source_idx, source_func in enumerate(self.sources):
            for attempt in range(max_retries):
                try:
                    result = source_func(stock_code)
                    
                    if result and (
                        result.get('bid_price', 0) > 0 or 
                        result.get('asks') or 
                        result.get('last_price', 0) > 0
                    ):
                        result['stock_code'] = stock_code
                        result['attempt'] = attempt + 1
                        result['source_priority'] = source_idx + 1
                        result['scrape_timestamp'] = datetime.now().isoformat()
                        
                        self.cache[cache_key] = result
                        self.request_count += 1
                        
                        logger.info(f"✅ Successfully fetched {stock_code} from {result['source']}")
                        return result
                    
                    if attempt < max_retries - 1:
                        wait_time = self._exponential_backoff(attempt)
                        logger.warning(f"Retry {attempt+1}/{max_retries} for {stock_code} in {wait_time:.1f}s")
                        time.sleep(wait_time)
                        
                except Exception as e:
                    logger.error(f"Source {source_idx+1}, Attempt {attempt+1} failed for {stock_code}: {str(e)}")
                    if attempt < max_retries - 1:
                        time.sleep(self._exponential_backoff(attempt))
        
        logger.error(f"❌ All sources failed for {stock_code}")
        return {
            'stock_code': stock_code,
            'error': 'No data available from any source',
            'timestamp': datetime.now().isoformat()
        }
    
    def get_stats(self) -> Dict:
        return {
            'total_requests': self.request_count,
            'cache_size': len(self.cache),
            'session_active': self.session is not None,
            'proxy_enabled': self.use_proxy,
            'sources_available': len(self.sources)
        }


# ============ INITIALIZE SCRAPER WITH PROXY ============
# Proxy list sesuai permintaan
PROXY_LIST = ['http://185.199.228.220:80', 'http://188.166.190.47:8080']

# Inisialisasi scraper dengan proxy
orderbook_scraper = UltraResilientOrderBookScraper(
    use_proxy=True, 
    proxy_list=PROXY_LIST
)

# ============ UPLOAD ENDPOINT ============
@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    if not allowed_file(file.filename):
        return jsonify({'error': f'File type not allowed. Allowed: {", ".join(ALLOWED_EXTENSIONS)}'}), 400
    
    file.seek(0, os.SEEK_END)
    file_size = file.tell()
    file.seek(0)
    
    if file_size > MAX_FILE_SIZE:
        return jsonify({'error': f'File too large. Max size: {MAX_FILE_SIZE // (1024*1024)}MB'}), 400
    
    filename = secure_filename(file.filename)
    filepath = os.path.join(UPLOAD_FOLDER, filename)
    file.save(filepath)
    
    is_image = is_image_file(filename)
    
    result = {
        'success': True,
        'filename': filename,
        'is_image': is_image,
        'size': file_size
    }
    
    if is_image:
        result['content'] = None
        result['image_base64'] = None
        result['message'] = 'Image received (OCR disabled)'
    else:
        text_content = extract_text_from_file(filepath, filename)
        if text_content is None:
            os.remove(filepath)
            return jsonify({'error': 'Failed to extract text from file'}), 500
        if len(text_content) > 50000:
            text_content = text_content[:50000] + "\n\n[File content truncated due to length]"
        result['content'] = text_content
        result['message'] = 'Text extracted successfully'
    
    os.remove(filepath)
    return jsonify(result)

# ============ SINGLE ENDPOINTS ============
@app.route('/quote', methods=['GET'])
def get_quote():
    symbol = request.args.get('symbol', '').upper()
    if not symbol:
        return jsonify({'error': 'No symbol'}), 400

    data = fetch_quote_with_fallback(symbol)
    now = datetime.now()
    is_trading = (9 <= now.hour < 16) and now.weekday() < 5

    return jsonify({
        'symbol': symbol,
        'price': data['price'],
        'changePercent': data.get('changePercent', 0),
        'isClosed': not is_trading,
        'open': data.get('open', data['price']),
        'high': data.get('high', data['price']),
        'low': data.get('low', data['price']),
        'volume': data.get('volume', 0),
        'previousClose': data.get('prevClose', data['price']),
        'source': data.get('source', 'unknown'),
        'cached': data.get('cached', False)
    })

@app.route('/keystats', methods=['GET'])
def get_keystats():
    symbol = request.args.get('symbol', '').upper()
    if not symbol:
        return jsonify({'error': 'No symbol'}), 400
    return jsonify(get_keystats_data(symbol))

@app.route('/orderbook', methods=['GET'])
def get_orderbook():
    symbol = request.args.get('symbol', '').upper()
    cache_key = f"orderbook_{symbol}"
    cached = orderbook_cache.get(cache_key)
    if cached:
        return jsonify(cached)

    # Try to get real order book from scraper
    try:
        scraped_data = orderbook_scraper.fetch_orderbook(symbol)
        
        if scraped_data and 'error' not in scraped_data:
            # Format data untuk frontend
            order_book = []
            
            # Jika ada bids dan asks dari IDX
            if 'bids' in scraped_data and 'asks' in scraped_data:
                bids = scraped_data['bids'][:10]
                asks = scraped_data['asks'][:10]
                
                for i in range(max(len(bids), len(asks))):
                    bid = bids[i] if i < len(bids) else {'price': 0, 'volume': 0, 'freq': 0}
                    ask = asks[i] if i < len(asks) else {'price': 0, 'volume': 0, 'freq': 0}
                    
                    order_book.append({
                        'bid_freq': bid.get('freq', 0),
                        'bid_lot': bid.get('volume', 0),
                        'bid_price': bid.get('price', 0),
                        'ask_price': ask.get('price', 0),
                        'ask_lot': ask.get('volume', 0),
                        'ask_freq': ask.get('freq', 0)
                    })
            else:
                # Format dari Yahoo Finance atau sumber lain
                bid_price = scraped_data.get('bid_price', 0)
                ask_price = scraped_data.get('ask_price', 0)
                bid_size = scraped_data.get('bid_size', 0)
                ask_size = scraped_data.get('ask_size', 0)
                
                # Generate simulated depth based on bid/ask
                for i in range(10):
                    multiplier = 1 - (i * 0.02)
                    order_book.append({
                        'bid_freq': random.randint(1, 20),
                        'bid_lot': int(bid_size * (1 - i * 0.05)) if bid_size > 0 else random.randint(10000, 100000),
                        'bid_price': int(bid_price * multiplier) if bid_price > 0 else 0,
                        'ask_price': int(ask_price * (1 + i * 0.02)) if ask_price > 0 else 0,
                        'ask_lot': int(ask_size * (1 - i * 0.05)) if ask_size > 0 else random.randint(10000, 100000),
                        'ask_freq': random.randint(1, 20)
                    })
            
            result = {
                'symbol': symbol,
                'order_book': order_book,
                'last_price': scraped_data.get('last_price', 0),
                'source': scraped_data.get('source', 'scraper'),
                'scrape_timestamp': scraped_data.get('scrape_timestamp')
            }
            orderbook_cache.set(cache_key, result)
            return jsonify(result)
            
    except Exception as e:
        logger.error(f"Orderbook scraper error for {symbol}: {str(e)}")
    
    # FALLBACK: Data dummy jika scraper gagal
    quote = fetch_quote_with_fallback(symbol)
    price = quote['price']
    
    bids = [int(price - i) for i in range(1, 11)]
    asks = [int(price + i) for i in range(1, 11)]
    bid_lots = [int(price * 100 * (0.8 + i*0.05)) for i in range(10)]
    ask_lots = [int(price * 100 * (0.7 + i*0.05)) for i in range(10)]
    bid_freqs = [3, 15, 12, 8, 5, 4, 6, 7, 9, 10]
    ask_freqs = [10, 9, 5, 6, 7, 8, 4, 5, 6, 7]
    
    order_book = []
    for i in range(10):
        order_book.append({
            'bid_freq': bid_freqs[i],
            'bid_lot': bid_lots[i],
            'bid_price': bids[i],
            'ask_price': asks[i],
            'ask_lot': ask_lots[i],
            'ask_freq': ask_freqs[i]
        })
    
    result = {
        'symbol': symbol,
        'order_book': order_book,
        'last_price': price,
        'source': 'simulated (fallback)'
    }
    orderbook_cache.set(cache_key, result)
    return jsonify(result)

@app.route('/foreigntransaction', methods=['GET'])
def get_foreign_transaction():
    symbol = request.args.get('symbol', '').upper()
    quote = fetch_quote_with_fallback(symbol)
    price = quote['price']
    volume = quote.get('volume', 1000000)
    total_val = (price * volume) / 1000000000 if price and volume else 0

    return jsonify({
        'symbol': symbol,
        'buyers': [
            {'name': 'Credit Suisse', 'avg': round(price * 0.998, 0), 'val': round(total_val * 0.25, 1)},
            {'name': 'Morgan Stanley', 'avg': round(price * 0.999, 0), 'val': round(total_val * 0.18, 1)},
            {'name': 'Goldman Sachs', 'avg': round(price * 0.997, 0), 'val': round(total_val * 0.15, 1)},
            {'name': 'KZ', 'avg': round(price * 0.996, 0), 'val': round(total_val * 0.12, 1)},
            {'name': 'RX', 'avg': round(price * 0.995, 0), 'val': round(total_val * 0.10, 1)}
        ],
        'sellers': [
            {'name': 'J.P. Morgan', 'avg': round(price * 1.002, 0), 'val': round(total_val * 0.22, 1)},
            {'name': 'UBS', 'avg': round(price * 1.003, 0), 'val': round(total_val * 0.16, 1)},
            {'name': 'Deutsche Bank', 'avg': round(price * 1.004, 0), 'val': round(total_val * 0.14, 1)},
            {'name': 'ZP', 'avg': round(price * 1.005, 0), 'val': round(total_val * 0.11, 1)},
            {'name': 'CC', 'avg': round(price * 1.006, 0), 'val': round(total_val * 0.09, 1)}
        ]
    })

@app.route('/bandarmology', methods=['GET'])
def get_bandarmology():
    symbol = request.args.get('symbol', '').upper()
    if not symbol:
        return jsonify({'error': 'No symbol'}), 400
    return jsonify(get_bandarmology_analysis(symbol))

@app.route('/predict', methods=['GET'])
def predict():
    return jsonify({'predictions': get_top_predictions()})

# ============ ENDPOINT: FOREIGN TRANSACTION HISTORY ============
@app.route('/foreigntransaction/history', methods=['GET'])
def get_foreign_transaction_history():
    symbol = request.args.get('symbol', '').upper()
    period = request.args.get('period', '5d')
    
    quote = fetch_quote_with_fallback(symbol)
    price = quote['price']
    
    if period == '5d':
        dates = ['20 May', '21 May', '22 May', '23 May', '24 May']
        net_values = [25.5, -12.3, 38.7, -8.2, 45.1]
        volumes = [850, 620, 1200, 450, 980]
    elif period == '1m':
        dates = ['Week 1', 'Week 2', 'Week 3', 'Week 4']
        net_values = [18.2, -5.7, 42.3, -15.8]
        volumes = [2100, 1800, 3200, 1500]
    else:
        dates = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
        net_values = [12.5, 8.3, -22.1, 35.6, 18.9, -5.2, 28.4, 42.1, -12.7, 15.3, 22.8, 30.5]
        volumes = [8500, 7200, 6400, 8900, 7800, 6600, 9500, 11000, 7100, 8200, 9100, 10500]
    
    return jsonify({
        'symbol': symbol,
        'period': period,
        'dates': dates,
        'net_values': net_values,
        'volumes': volumes,
        'current_price': price,
        'timestamp': datetime.now().isoformat()
    })

# ============ ENDPOINT: SPARKLINE DATA ============
@app.route('/sparkline', methods=['GET'])
def get_sparkline():
    symbol = request.args.get('symbol', '').upper()
    period = request.args.get('period', '1mo')
    
    try:
        yf_symbol = f"{symbol}.JK"
        ticker = yf.Ticker(yf_symbol)
        
        if period == '1d':
            hist = ticker.history(period='5d', interval='1h')
        elif period == '5d':
            hist = ticker.history(period='5d', interval='15m')
        else:
            hist = ticker.history(period='1mo', interval='1d')
        
        if hist.empty:
            prices = [5000 + i * (10 if i < 15 else -5) for i in range(30)]
        else:
            prices = hist['Close'].tolist()
        
        min_price = min(prices)
        max_price = max(prices)
        if max_price == min_price:
            normalized = [50] * len(prices)
        else:
            normalized = [((p - min_price) / (max_price - min_price)) * 100 for p in prices]
        
        return jsonify({
            'symbol': symbol,
            'prices': prices,
            'normalized': normalized,
            'period': period,
            'change': ((prices[-1] - prices[0]) / prices[0] * 100) if prices and len(prices) > 1 else 0,
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        print(f"Sparkline error: {e}")
        prices = [5000 + i * (10 if i < 15 else -5) for i in range(30)]
        normalized = [(i / 29) * 100 for i in range(30)]
        return jsonify({
            'symbol': symbol,
            'prices': prices,
            'normalized': normalized,
            'period': period,
            'change': 0,
            'timestamp': datetime.now().isoformat()
        })

# ============ BULK ENDPOINT FOR FOREIGN TRANSACTION ============
@app.route('/bulk/foreigntransaction', methods=['POST'])
def get_bulk_foreign_transaction():
    data = request.json
    symbols = data.get('symbols', [])
    if not symbols:
        return jsonify({'error': 'No symbols provided'}), 400
    
    results = {}
    for symbol in symbols:
        symbol = symbol.upper()
        quote = fetch_quote_with_fallback(symbol)
        price = quote['price']
        volume = quote.get('volume', 1000000)
        total_val = (price * volume) / 1000000000 if price and volume else 0
        
        results[symbol] = {
            'buyers': [
                {'name': 'Credit Suisse', 'avg': round(price * 0.998, 0), 'val': round(total_val * 0.25, 1)},
                {'name': 'Morgan Stanley', 'avg': round(price * 0.999, 0), 'val': round(total_val * 0.18, 1)},
                {'name': 'Goldman Sachs', 'avg': round(price * 0.997, 0), 'val': round(total_val * 0.15, 1)},
                {'name': 'KZ', 'avg': round(price * 0.996, 0), 'val': round(total_val * 0.12, 1)},
                {'name': 'RX', 'avg': round(price * 0.995, 0), 'val': round(total_val * 0.10, 1)}
            ],
            'sellers': [
                {'name': 'J.P. Morgan', 'avg': round(price * 1.002, 0), 'val': round(total_val * 0.22, 1)},
                {'name': 'UBS', 'avg': round(price * 1.003, 0), 'val': round(total_val * 0.16, 1)},
                {'name': 'Deutsche Bank', 'avg': round(price * 1.004, 0), 'val': round(total_val * 0.14, 1)},
                {'name': 'ZP', 'avg': round(price * 1.005, 0), 'val': round(total_val * 0.11, 1)},
                {'name': 'CC', 'avg': round(price * 1.006, 0), 'val': round(total_val * 0.09, 1)}
            ]
        }
    
    return jsonify({
        'success': True, 
        'count': len(results), 
        'data': results,
        'timestamp': datetime.now().isoformat()
    })

# ============ BULK ORDERBOOK ENDPOINT ============
@app.route('/bulk/orderbook', methods=['POST'])
def get_bulk_orderbook():
    data = request.json
    symbols = data.get('symbols', [])
    if not symbols:
        return jsonify({'error': 'No symbols provided'}), 400

    results = {}
    for symbol in symbols:
        quote = fetch_quote_with_fallback(symbol)
        price = quote['price']
        
        bids = [int(price - i) for i in range(1, 11)]
        asks = [int(price + i) for i in range(1, 11)]
        bid_lots = [int(price * 100 * (0.8 + i*0.05)) for i in range(10)]
        ask_lots = [int(price * 100 * (0.7 + i*0.05)) for i in range(10)]
        bid_freqs = [3, 15, 12, 8, 5, 4, 6, 7, 9, 10]
        ask_freqs = [10, 9, 5, 6, 7, 8, 4, 5, 6, 7]
        
        order_book = []
        for i in range(10):
            order_book.append({
                'bid_freq': bid_freqs[i],
                'bid_lot': bid_lots[i],
                'bid_price': bids[i],
                'ask_price': asks[i],
                'ask_lot': ask_lots[i],
                'ask_freq': ask_freqs[i]
            })
        results[symbol] = {'order_book': order_book, 'last_price': price}
    
    return jsonify({'success': True, 'count': len(results), 'data': results, 'timestamp': datetime.now().isoformat()})

# ============ BULK OTHER ENDPOINTS ============
@app.route('/bulk', methods=['POST'])
def get_bulk():
    data = request.json
    symbols = data.get('symbols', [])
    if not symbols:
        return jsonify({'error': 'No symbols provided'}), 400

    results = {}
    for symbol in symbols:
        quote = fetch_quote_with_fallback(symbol)
        results[symbol] = {
            'price': quote.get('price', 0),
            'changePercent': quote.get('changePercent', 0),
            'source': quote.get('source', 'unknown')
        }
    return jsonify({'success': True, 'count': len(results), 'data': results, 'timestamp': datetime.now().isoformat()})

@app.route('/bulk/keystats', methods=['POST'])
def get_bulk_keystats():
    data = request.json
    symbols = data.get('symbols', [])
    if not symbols:
        return jsonify({'error': 'No symbols provided'}), 400

    results = {}
    for symbol in symbols:
        results[symbol] = get_keystats_data(symbol)
    return jsonify({'success': True, 'count': len(results), 'data': results, 'timestamp': datetime.now().isoformat()})

@app.route('/bulk/bandarmology', methods=['POST'])
def get_bulk_bandarmology():
    data = request.json
    symbols = data.get('symbols', [])
    if not symbols:
        return jsonify({'error': 'No symbols provided'}), 400

    results = {}
    for symbol in symbols:
        analysis = get_bandarmology_analysis(symbol)
        results[symbol] = {
            'price': analysis.get('price', 0),
            'changePercent': analysis.get('changePercent', 0),
            'signal': analysis.get('signal', 'NEUTRAL'),
            'recommendation': analysis.get('recommendation', 'HOLD'),
            'potentialGain': analysis.get('potentialGain', 0),
            'volumeRatio': analysis.get('volumeRatio', 1.0),
            'name': analysis.get('name', symbol)
        }
    return jsonify({'success': True, 'count': len(results), 'data': results, 'timestamp': datetime.now().isoformat()})

# ============ CHAT ENDPOINT ============
@app.route('/chat', methods=['POST'])
def chat():
    data = request.json
    user_message = data.get('message', '')
    session_id = data.get('session_id')
    file_content = data.get('file_content')
    file_name = data.get('file_name')
    image_base64 = data.get('image_base64')

    if not session_id:
        session_id = str(uuid.uuid4())

    if not user_message and not file_content and not image_base64:
        return jsonify({'error': 'No message or file content provided'}), 400

    add_to_history(session_id, "user", user_message if user_message else ("[Uploaded Image]" if image_base64 else "[Uploaded File]"))

    mentioned_symbols = re.findall(r'\b([A-Z]{4})\b', user_message.upper())
    if not mentioned_symbols and ('saham' in user_message.lower() or 'rekomendasi' in user_message.lower()):
        mentioned_symbols = ["BBCA", "BBRI", "BMRI"]

    stock_data_list = []
    for sym in mentioned_symbols[:5]:
        quote = fetch_quote_with_fallback(sym)
        avg_vol = get_avg_volume(sym)
        volume_ratio = quote.get('volume', 0) / avg_vol if avg_vol > 0 else 1
        volume_ratio = min(volume_ratio, 3.0)
        
        bandarmology_signal = "NEUTRAL"
        if volume_ratio > 1.5 and quote.get('changePercent', 0) > 0:
            bandarmology_signal = "ACCUMULATION"
        elif volume_ratio > 1.5 and quote.get('changePercent', 0) < 0:
            bandarmology_signal = "DISTRIBUTION"
        elif volume_ratio > 1.2 and quote.get('changePercent', 0) > 0:
            bandarmology_signal = "WEAK ACCUMULATION"
        elif volume_ratio > 1.2 and quote.get('changePercent', 0) < 0:
            bandarmology_signal = "WEAK DISTRIBUTION"
        
        stock_data_list.append({
            'code': sym,
            'name': get_stock_name(sym),
            'price': quote.get('price', 0),
            'change_percent': quote.get('changePercent', 0),
            'volume': quote.get('volume', 0),
            'volume_ratio': volume_ratio,
            'signal': bandarmology_signal,
            'source': quote.get('source', 'unknown')
        })

    data_text = ""
    for s in stock_data_list:
        direction = "UP" if s['change_percent'] >= 0 else "DOWN"
        data_text += f"""
[{s['code']}]
Price: Rp{s['price']:,.0f} ({s['change_percent']:+.2f}%, {direction})
Volume: {(s['volume']/1000000):.1f}M ({s['volume_ratio']:.1f}x avg)
Signal: {s['signal']}
"""

    system_prompt = f"""You are a stock assistant for IHSG. Answer VERY BRIEFLY and follow the EXACT format below.

REAL-TIME DATA:
{data_text if data_text else "No stock data mentioned. Ask user to provide stock code."}

STRICT FORMAT - COPY THIS EXACTLY:

=== SUMMARY ===
(One short sentence)

--- STOCK: CODE ---
- Price: RpX (X%)
- Volume: XM (Xx avg)
- Signal: X
- View: X

=== CONCLUSION ===
(One short sentence)

DISCLAIMER: Not investment advice.

RULES:
- NO long paragraphs
- NO explanations
- Keep each line SHORT
- Total response under 200 words

If no data available, just say: "Please provide a stock code (e.g., BBCA, BUMI, RAJA)."

Now answer using the EXACT format above. Be BRIEF."""

    messages = build_messages_with_history(session_id, system_prompt, user_message if user_message else "Please analyze the data.")

    headers = {"Authorization": f"Bearer {DEEPSEEK_API_KEY}", "Content-Type": "application/json"}
    payload = {
        "model": "deepseek-chat",
        "messages": messages,
        "temperature": 0.5,
        "max_tokens": 500,
        "stream": True
    }

    def generate():
        full_response = ""
        try:
            resp = requests.post(DEEPSEEK_API_URL, headers=headers, json=payload, stream=True, timeout=60)
            for line in resp.iter_lines():
                if line:
                    line = line.decode('utf-8')
                    if line.startswith('data: '):
                        data = line[6:]
                        if data == '[DONE]':
                            break
                        try:
                            chunk = json.loads(data)
                            if 'choices' in chunk and len(chunk['choices']) > 0:
                                delta = chunk['choices'][0].get('delta', {})
                                content = delta.get('content', '')
                                if content:
                                    full_response += content
                                    yield f"data: {json.dumps({'content': content})}\n\n"
                        except:
                            pass
            if full_response:
                add_to_history(session_id, "assistant", full_response)
            yield "data: [DONE]\n\n"
        except Exception as e:
            print(f"Chat error: {e}")
            yield f"data: {json.dumps({'error': str(e)})}\n\n"
            yield "data: [DONE]\n\n"
    
    return Response(stream_with_context(generate()), mimetype='text/event-stream')

# ============ CLEAR SESSION ============
@app.route('/clear_session', methods=['POST'])
def clear_session():
    data = request.json
    session_id = data.get('session_id')
    if session_id:
        clear_session_history(session_id)
        return jsonify({'success': True})
    return jsonify({'error': 'No session_id'}), 400

if __name__ == '__main__':
    print("=" * 60)
    print("API Server Starting...")
    print("Finnhub + Alpha Vantage + yfinance (fallback)")
    print("Supported: PDF, DOCX, TXT, CSV")
    print("Images: NOT processed (OCR disabled)")
    print("Response format: SHORT and STRUCTURED")
    print("Cache: Quote 15s, Orderbook 30s")
    print("=" * 60)
    print("ORDER BOOK SCRAPER CONFIGURATION:")
    print(f"  - Proxy Enabled: YES")
    print(f"  - Proxy List: {PROXY_LIST}")
    print(f"  - Sources: Yahoo Finance, IDX Official, Investing.com")
    print("=" * 60)
    app.run(host='0.0.0.0', port=5002, debug=True, threaded=True)