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
from concurrent.futures import ThreadPoolExecutor, as_completed

app = Flask(__name__)
CORS(app)

# ============ API KEYS ============
FINNHUB_KEY = "d7st6j9r01qorsvju63gd7st6j9r01qorsvju640"
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

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def is_image_file(filename): return filename.rsplit('.', 1)[1].lower() in ['png','jpg','jpeg','gif','bmp','tiff']

def file_to_base64(file_path):
    with open(file_path, 'rb') as f: return base64.b64encode(f.read()).decode('utf-8')

def extract_text_from_pdf(file_path):
    try:
        text = ""
        with open(file_path, 'rb') as f:
            reader = PyPDF2.PdfReader(f)
            for page in reader.pages:
                page_text = page.extract_text()
                if page_text: text += page_text + "\n"
        return text.strip()
    except Exception as e: return None

def extract_text_from_docx(file_path):
    try:
        doc = docx.Document(file_path)
        return "\n".join([para.text for para in doc.paragraphs]).strip()
    except Exception as e: return None

def extract_text_from_csv(file_path):
    try:
        text = ""
        with open(file_path, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            for row in reader: text += ", ".join(row) + "\n"
        return text.strip()
    except Exception as e: return None

def extract_text_from_txt(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as f: return f.read().strip()
    except Exception as e: return None

def extract_text_from_file(file_path, filename):
    ext = filename.rsplit('.', 1)[1].lower()
    if ext == 'pdf': return extract_text_from_pdf(file_path)
    elif ext in ['doc','docx']: return extract_text_from_docx(file_path)
    elif ext == 'csv': return extract_text_from_csv(file_path)
    elif ext == 'txt': return extract_text_from_txt(file_path)
    elif ext == 'json':
        with open(file_path, 'r', encoding='utf-8') as f: return f.read().strip()
    return None

# ============ SIMPLE CACHE SYSTEM ============
class SimpleCache:
    def __init__(self, ttl=15):
        self.cache = OrderedDict()
        self.ttl = ttl
    def get(self, key):
        if key in self.cache:
            data, timestamp = self.cache[key]
            if datetime.now() - timestamp < timedelta(seconds=self.ttl): return data
            else: del self.cache[key]
        return None
    def set(self, key, value):
        if len(self.cache) > 100: self.cache.popitem(last=False)
        self.cache[key] = (value, datetime.now())
    def clear(self): self.cache.clear()

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
            with open(MEMORY_FILE, 'r') as f: conversation_memory = json.load(f)
        except: conversation_memory = {}
def save_memory():
    with open(MEMORY_FILE, 'w') as f: json.dump(conversation_memory, f)
load_memory()

def get_session_history(session_id):
    if session_id not in conversation_memory: conversation_memory[session_id] = []
    return conversation_memory[session_id]

def add_to_history(session_id, role, content):
    history = get_session_history(session_id)
    history.append({"role": role, "content": content, "timestamp": datetime.now().isoformat()})
    if len(history) > 20: conversation_memory[session_id] = history[-20:]
    save_memory()

def clear_session_history(session_id): conversation_memory[session_id] = []; save_memory()

def build_messages_with_history(session_id, system_prompt, user_message):
    history = get_session_history(session_id)
    messages = [{"role": "system", "content": system_prompt}]
    recent_history = history[-10:] if len(history) > 10 else history
    messages.extend(recent_history)
    messages.append({"role": "user", "content": user_message})
    return messages

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
        "RAJA": "PT Rukun Raharja Tbk.", "BUMI": "PT Bumi Resources Tbk."
    }
    return names.get(symbol, symbol)

def get_stock_sector(symbol):
    sectors = {
        "BBCA": "Finance", "BBRI": "Finance", "BMRI": "Finance", "BRIS": "Finance", "BBNI": "Finance",
        "TLKM": "Technology", "GOTO": "Technology", "TOWR": "Technology", "ERAA": "Technology",
        "ADRO": "Energy", "MEDC": "Energy", "PGAS": "Energy", "HRUM": "Energy", "MDKA": "Energy",
        "CPIN": "Consumer", "ICBP": "Consumer", "INDF": "Consumer", "UNVR": "Consumer", "SIDO": "Consumer", "JPFA": "Consumer",
        "ASII": "Consumer", "SMGR": "Consumer", "ANTM": "Consumer", "INKP": "Consumer", "TKIM": "Consumer",
        "UNTR": "Consumer", "WIKA": "Consumer", "AMMN": "Energy", "RAJA": "Energy", "BUMI": "Energy"
    }
    return sectors.get(symbol, "IDX: Others")

def get_avg_volume(symbol):
    quote = fetch_quote_with_fallback(symbol)
    price = quote.get('price', 5000)
    if price > 10000: return 2000000
    elif price < 1000: return 5000000
    return 3000000

# ============ MARKET DATA FETCHERS ============
def fetch_from_finnhub(symbol):
    try:
        url = f"https://finnhub.io/api/v1/quote?symbol={symbol}.JK&token={FINNHUB_KEY}"
        response = requests.get(url, timeout=5)
        data = response.json()
        if data.get('c') and data['c'] > 0:
            return {'success': True, 'source': 'finnhub', 'price': data['c'], 'changePercent': data['dp'], 'volume': data.get('v', 0)}
        return {'success': False}
    except: return {'success': False}

def fetch_from_alpha_vantage(symbol):
    try:
        url = f"https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={symbol}.JK&apikey={ALPHA_VANTAGE_KEY}"
        response = requests.get(url, timeout=5)
        data = response.json()
        quote = data.get('Global Quote', {})
        if quote.get('05. price'):
            return {
                'success': True, 'source': 'alphavantage',
                'price': float(quote['05. price']),
                'changePercent': float(quote['10. change percent'].replace('%', '')) if quote.get('10. change percent') else 0,
                'volume': int(quote.get('06. volume', 0))
            }
        return {'success': False}
    except: return {'success': False}

def fetch_from_yfinance(symbol):
    try:
        yf_symbol = f"{symbol}.JK"
        ticker = yf.Ticker(yf_symbol)
        info = ticker.info
        price = info.get('regularMarketPrice', 0)
        prev_close = info.get('previousClose', price)
        return {
            'success': True, 'source': 'yfinance',
            'price': price if price else prev_close,
            'changePercent': info.get('regularMarketChangePercent', 0),
            'volume': info.get('regularMarketVolume', 0)
        }
    except: return {'success': False}

def fetch_quote_with_fallback(symbol):
    cache_key = f"quote_{symbol}"
    cached = quote_cache.get(cache_key)
    if cached:
        cached['cached'] = True
        return cached
    for fetcher in [fetch_from_yfinance, fetch_from_finnhub, fetch_from_alpha_vantage]:
        result = fetcher(symbol)
        if result['success']:
            result['cached'] = False
            quote_cache.set(cache_key, result)
            return result
    return {'success': True, 'source': 'simulated', 'cached': False, 'price': 5000, 'changePercent': 0, 'volume': 1000000}

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
        'symbol': symbol, 'price': price, 'changePercent': change_pct, 'isClosed': is_closed,
        'prev': prev_close, 'open': quote.get('open', price), 'high': quote.get('high', price),
        'low': quote.get('low', price), 'lot': lot, 'ara': ara, 'arb': arb, 'val': val,
        'name': get_stock_name(symbol), 'sector': get_stock_sector(symbol), 'source': quote.get('source', 'unknown')
    }

def get_bandarmology_analysis(symbol):
    quote = fetch_quote_with_fallback(symbol)
    price = quote.get('price', 0)
    change_pct = quote.get('changePercent', 0)
    volume = quote.get('volume', 0)
    avg_vol = get_avg_volume(symbol)
    volume_ratio = min(volume / avg_vol if avg_vol > 0 else 1, 3.0)
    is_accumulation = volume_ratio > 1.2 and change_pct > 0
    is_breakout = change_pct > 2 and volume_ratio > 1.5
    potential = abs(change_pct) * 1.5
    if is_accumulation: potential = max(potential, 6)
    if is_breakout: potential = max(potential, 8)
    return {
        'symbol': symbol, 'name': get_stock_name(symbol), 'price': price,
        'changePercent': round(change_pct, 2), 'volumeRatio': round(volume_ratio, 1),
        'isAccumulation': is_accumulation, 'isBreakout': is_breakout, 'potentialGain': round(potential, 1),
        'signal': 'ACCUMULATION' if is_accumulation else ('BREAKOUT' if is_breakout else 'NEUTRAL'),
        'recommendation': 'BUY' if (is_accumulation or is_breakout) and change_pct > 0 else 'HOLD',
        'source': quote.get('source', 'unknown')
    }

def get_top_predictions(limit=8):
    top_symbols = ["BBCA","BBRI","BMRI","TLKM","ASII","ADRO","UNVR","GOTO","RAJA","BUMI"]
    results = []
    for symbol in top_symbols:
        analysis = get_bandarmology_analysis(symbol)
        if analysis.get('price',0) > 0: results.append(analysis)
    results.sort(key=lambda x: x.get('potentialGain',0), reverse=True)
    return results[:limit]

# ============ DAFTAR SAHAM IHSG (80 saham likuid) ============
IHSG_STOCKS = [
    "BBCA", "BBRI", "BMRI", "TLKM", "ASII", "GOTO", "UNVR", "ADRO",
    "CPIN", "ICBP", "INDF", "MEDC", "PGAS", "SMGR", "ANTM", "HRUM",
    "TOWR", "ERAA", "SIDO", "JPFA", "MDKA", "INKP", "TKIM", "BRIS",
    "BBNI", "UNTR", "WIKA", "AMMN", "RAJA", "BUMI", "PTRO", "ACES",
    "ADMF", "AGII", "AKRA", "AMRT", "APLN", "ARTO", "ASSA", "BFIN",
    "BHIT", "BIRD", "BISI", "BNGA", "BNII", "BSDE", "BTPS", "BUKA",
    "BULL", "BWPT", "CAMP", "CBMF", "CENT", "CFIN", "CINT", "CITA",
    "CLPI", "CMNP", "CNKO", "COAL", "CPRO", "CSAP", "CTRA", "DART",
    "DIVA", "DMAS", "DNET", "DOOH", "DPNS", "DSSA", "DSNG", "DTLA"
]

# ============ ULTRA RESILIENT ORDER BOOK SCRAPER ============
class UltraResilientOrderBookScraper:
    def __init__(self, use_proxy: bool = False, proxy_list: List[str] = None):
        self.session = self._create_session()
        self.ua = UserAgent()
        self.use_proxy = use_proxy
        self.proxy_list = proxy_list or []
        self.cache = {}
        self.request_count = 0
        self.last_request_time = 0
        self.min_request_interval = 1
        self.sources = [self._get_from_yfinance, self._get_from_idx_website, self._get_from_investing_com]
    def _create_session(self):
        session = requests.Session()
        retry = Retry(total=3, read=3, connect=3, backoff_factor=0.5, status_forcelist=[500,502,503,504])
        adapter = HTTPAdapter(max_retries=retry)
        session.mount('http://', adapter)
        session.mount('https://', adapter)
        return session
    def _get_headers(self):
        return {'User-Agent': self.ua.random, 'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5', 'Accept-Encoding': 'gzip, deflate', 'Connection': 'keep-alive'}
    def _get_proxy(self):
        if self.use_proxy and self.proxy_list:
            return {'http': random.choice(self.proxy_list), 'https': random.choice(self.proxy_list)}
        return None
    def _rate_limit(self):
        elapsed = time.time() - self.last_request_time
        if elapsed < self.min_request_interval: time.sleep(self.min_request_interval - elapsed)
        self.last_request_time = time.time()
    def _exponential_backoff(self, attempt): return min(2**attempt, 10) + random.uniform(0,1)
    def _get_from_yfinance(self, stock_code):
        try:
            logger.info(f"Attempting Yahoo Finance for {stock_code}")
            ticker = yf.Ticker(f"{stock_code}.JK")
            info = ticker.info
            if not info: return None
            orderbook = {'source':'Yahoo Finance','bid_price':info.get('bid',0),'bid_size':info.get('bidSize',0),
                         'ask_price':info.get('ask',0),'ask_size':info.get('askSize',0),
                         'last_price':info.get('regularMarketPrice',0),'volume':info.get('volume',0),
                         'timestamp':datetime.now().isoformat()}
            hist = ticker.history(period="1d", interval="1m")
            if not hist.empty:
                orderbook['open'] = hist['Open'].iloc[-1]
                orderbook['high'] = hist['High'].iloc[-1]
                orderbook['low'] = hist['Low'].iloc[-1]
            if orderbook['bid_price']>0 or orderbook['ask_price']>0: return orderbook
            return None
        except Exception as e: logger.warning(f"Yahoo Finance error: {e}"); return None
    def _get_from_idx_website(self, stock_code):
        try:
            logger.info(f"Attempting IDX for {stock_code}")
            self._rate_limit()
            url = f"https://www.idx.co.id/primary/StockSummary/GetStockSummary?kodeEmiten={stock_code}"
            response = self.session.get(url, headers=self._get_headers(), proxies=self._get_proxy(), timeout=10)
            if response.status_code == 200:
                data = response.json()
                if data and len(data)>0:
                    stock_data = data[0]
                    orderbook = {'source':'IDX Official','stock_code':stock_code,'last_price':stock_data.get('LastPrice',0),
                                 'open_price':stock_data.get('OpenPrice',0),'close_price':stock_data.get('ClosePrice',0),
                                 'volume':stock_data.get('Volume',0),'value':stock_data.get('Value',0),
                                 'frequency':stock_data.get('Frequency',0),'timestamp':datetime.now().isoformat()}
                    depth_url = f"https://www.idx.co.id/primary/MarketDepth/GetMarketDepth?kodeEmiten={stock_code}"
                    depth_response = self.session.get(depth_url, headers=self._get_headers(), proxies=self._get_proxy(), timeout=10)
                    if depth_response.status_code == 200:
                        depth_data = depth_response.json()
                        if depth_data:
                            bids = []
                            asks = []
                            for item in depth_data:
                                if item.get('Side') == 'B':
                                    bids.append({'price':item.get('Price',0),'volume':item.get('Volume',0),'freq':item.get('Frequency',random.randint(1,20))})
                                elif item.get('Side') == 'S':
                                    asks.append({'price':item.get('Price',0),'volume':item.get('Volume',0),'freq':item.get('Frequency',random.randint(1,20))})
                            orderbook['bids'] = bids[:10]
                            orderbook['asks'] = asks[:10]
                            orderbook['bid_count'] = len(bids)
                            orderbook['ask_count'] = len(asks)
                    return orderbook
            return None
        except Exception as e: logger.warning(f"IDX error: {e}"); return None
    def _get_from_investing_com(self, stock_code):
        try:
            logger.info(f"Attempting Investing.com for {stock_code}")
            self._rate_limit()
            url = f"https://www.investing.com/equities/{stock_code.lower()}"
            response = self.session.get(url, headers=self._get_headers(), proxies=self._get_proxy(), timeout=10)
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                bid = soup.find('span', {'data-test':'bid-price'})
                ask = soup.find('span', {'data-test':'ask-price'})
                if bid and ask:
                    return {'source':'Investing.com', 'bid_price':float(bid.text.replace(',','')),
                            'ask_price':float(ask.text.replace(',','')), 'timestamp':datetime.now().isoformat()}
            return None
        except Exception as e: logger.warning(f"Investing.com error: {e}"); return None
    def fetch_orderbook(self, stock_code: str, max_retries: int = 3):
        stock_code = stock_code.upper().replace('.JK','')
        cache_key = f"{stock_code}_{int(time.time()/5)}"
        if cache_key in self.cache: return self.cache[cache_key]
        for source_idx, source_func in enumerate(self.sources):
            for attempt in range(max_retries):
                try:
                    result = source_func(stock_code)
                    if result and (result.get('bid_price',0)>0 or result.get('asks') or result.get('last_price',0)>0):
                        result['stock_code'] = stock_code
                        result['attempt'] = attempt+1
                        result['source_priority'] = source_idx+1
                        result['scrape_timestamp'] = datetime.now().isoformat()
                        self.cache[cache_key] = result
                        self.request_count += 1
                        return result
                    if attempt < max_retries-1:
                        time.sleep(self._exponential_backoff(attempt))
                except Exception as e: logger.error(f"Error: {e}"); time.sleep(self._exponential_backoff(attempt))
        return {'stock_code':stock_code,'error':'No data','timestamp':datetime.now().isoformat()}
    def get_stats(self): return {'total_requests':self.request_count,'cache_size':len(self.cache),'session_active':self.session is not None,
                                 'proxy_enabled':self.use_proxy, 'sources_available':len(self.sources)}

PROXY_LIST = ['http://185.199.228.220:80','http://188.166.190.47:8080']
orderbook_scraper = UltraResilientOrderBookScraper(use_proxy=True, proxy_list=PROXY_LIST)

# ============ ENDPOINTS ============
@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files: return jsonify({'error': 'No file provided'}), 400
    file = request.files['file']
    if file.filename == '': return jsonify({'error': 'No file selected'}), 400
    if not allowed_file(file.filename): return jsonify({'error': f'File type not allowed'}), 400
    file.seek(0, os.SEEK_END); file_size = file.tell(); file.seek(0)
    if file_size > MAX_FILE_SIZE: return jsonify({'error': f'File too large'}), 400
    filename = secure_filename(file.filename)
    filepath = os.path.join(UPLOAD_FOLDER, filename)
    file.save(filepath)
    is_image = is_image_file(filename)
    result = {'success': True, 'filename': filename, 'is_image': is_image, 'size': file_size}
    if is_image:
        result['content'] = None
        result['image_base64'] = None
        result['message'] = 'Image received (OCR disabled)'
    else:
        text_content = extract_text_from_file(filepath, filename)
        if text_content is None:
            os.remove(filepath)
            return jsonify({'error': 'Failed to extract text'}), 500
        if len(text_content) > 50000: text_content = text_content[:50000] + "\n\n[Truncated]"
        result['content'] = text_content
        result['message'] = 'Text extracted successfully'
    os.remove(filepath)
    return jsonify(result)

@app.route('/quote', methods=['GET'])
def get_quote():
    symbol = request.args.get('symbol', '').upper()
    if not symbol: return jsonify({'error': 'No symbol'}), 400
    data = fetch_quote_with_fallback(symbol)
    now = datetime.now()
    is_trading = (9 <= now.hour < 16) and now.weekday() < 5
    return jsonify({'symbol':symbol,'price':data['price'],'changePercent':data.get('changePercent',0),
                    'isClosed':not is_trading,'open':data.get('open',data['price']),'high':data.get('high',data['price']),
                    'low':data.get('low',data['price']),'volume':data.get('volume',0),
                    'previousClose':data.get('prevClose',data['price']),'source':data.get('source','unknown'),
                    'cached':data.get('cached',False)})

@app.route('/keystats', methods=['GET'])
def get_keystats():
    symbol = request.args.get('symbol', '').upper()
    if not symbol: return jsonify({'error': 'No symbol'}), 400
    return jsonify(get_keystats_data(symbol))

@app.route('/orderbook', methods=['GET'])
def get_orderbook():
    symbol = request.args.get('symbol', '').upper()
    cache_key = f"orderbook_{symbol}"
    cached = orderbook_cache.get(cache_key)
    if cached: return jsonify(cached)
    try:
        scraped = orderbook_scraper.fetch_orderbook(symbol)
        if scraped and 'error' not in scraped:
            order_book = []
            if 'bids' in scraped and 'asks' in scraped:
                bids = scraped['bids'][:10]
                asks = scraped['asks'][:10]
                for i in range(max(len(bids),len(asks))):
                    bid = bids[i] if i<len(bids) else {'price':0,'volume':0,'freq':0}
                    ask = asks[i] if i<len(asks) else {'price':0,'volume':0,'freq':0}
                    order_book.append({'bid_freq':bid.get('freq',0),'bid_lot':bid.get('volume',0),'bid_price':bid.get('price',0),
                                       'ask_price':ask.get('price',0),'ask_lot':ask.get('volume',0),'ask_freq':ask.get('freq',0)})
            else:
                bid_price = scraped.get('bid_price',0)
                ask_price = scraped.get('ask_price',0)
                bid_size = scraped.get('bid_size',0)
                ask_size = scraped.get('ask_size',0)
                for i in range(10):
                    multiplier = 1 - i*0.02
                    order_book.append({'bid_freq':random.randint(1,20),
                                       'bid_lot':int(bid_size*(1-i*0.05)) if bid_size>0 else random.randint(10000,100000),
                                       'bid_price':int(bid_price*multiplier) if bid_price>0 else 0,
                                       'ask_price':int(ask_price*(1+i*0.02)) if ask_price>0 else 0,
                                       'ask_lot':int(ask_size*(1-i*0.05)) if ask_size>0 else random.randint(10000,100000),
                                       'ask_freq':random.randint(1,20)})
            result = {'symbol':symbol,'order_book':order_book,'last_price':scraped.get('last_price',0),
                      'source':scraped.get('source','scraper'),'scrape_timestamp':scraped.get('scrape_timestamp')}
            orderbook_cache.set(cache_key, result)
            return jsonify(result)
    except Exception as e: logger.error(f"Scraper error: {e}")
    quote = fetch_quote_with_fallback(symbol)
    price = quote['price']
    bids = [int(price - i) for i in range(1,11)]
    asks = [int(price + i) for i in range(1,11)]
    bid_lots = [int(price*100*(0.8 + i*0.05)) for i in range(10)]
    ask_lots = [int(price*100*(0.7 + i*0.05)) for i in range(10)]
    bid_freqs = [3,15,12,8,5,4,6,7,9,10]
    ask_freqs = [10,9,5,6,7,8,4,5,6,7]
    order_book = [{'bid_freq':bid_freqs[i],'bid_lot':bid_lots[i],'bid_price':bids[i],
                   'ask_price':asks[i],'ask_lot':ask_lots[i],'ask_freq':ask_freqs[i]} for i in range(10)]
    result = {'symbol':symbol,'order_book':order_book,'last_price':price,'source':'simulated (fallback)'}
    orderbook_cache.set(cache_key, result)
    return jsonify(result)

@app.route('/foreigntransaction', methods=['GET'])
def get_foreign_transaction():
    symbol = request.args.get('symbol', '').upper()
    quote = fetch_quote_with_fallback(symbol)
    price = quote['price']
    volume = quote.get('volume', 1000000)
    total_val = (price * volume) / 1_000_000_000 if price and volume else 0
    random.seed(hash(symbol) % 10000)
    net_flow_pct = random.uniform(-0.3,0.3)
    total_buy = total_val * (0.5 + net_flow_pct/2)
    total_sell = total_val * (0.5 - net_flow_pct/2)
    broker_names = ["Credit Suisse","Morgan Stanley","Goldman Sachs","KZ","RX","UBS","J.P. Morgan","Deutsche Bank","ZP","CC"]
    random.seed(hash(symbol) % 10000 + 1)
    buyers = random.sample(broker_names,5)
    sellers = random.sample(broker_names,5)
    buyer_allocs = [total_buy * w for w in [random.random() for _ in range(5)]]
    seller_allocs = [total_sell * w for w in [random.random() for _ in range(5)]]
    buyer_allocs = [w/sum(buyer_allocs)*total_buy for w in buyer_allocs]
    seller_allocs = [w/sum(seller_allocs)*total_sell for w in seller_allocs]
    buyers_data = [{'name':n,'avg':round(price*random.uniform(0.995,0.999)),'val':round(v,1)} for n,v in zip(buyers,buyer_allocs)]
    sellers_data = [{'name':n,'avg':round(price*random.uniform(1.001,1.005)),'val':round(v,1)} for n,v in zip(sellers,seller_allocs)]
    buyers_data.sort(key=lambda x:x['val'], reverse=True)
    sellers_data.sort(key=lambda x:x['val'], reverse=True)
    return jsonify({'symbol':symbol,'buyers':buyers_data[:5],'sellers':sellers_data[:5]})

@app.route('/bandarmology', methods=['GET'])
def get_bandarmology():
    symbol = request.args.get('symbol', '').upper()
    if not symbol: return jsonify({'error':'No symbol'}),400
    return jsonify(get_bandarmology_analysis(symbol))

@app.route('/predict', methods=['GET'])
def predict(): return jsonify({'predictions': get_top_predictions()})

@app.route('/foreigntransaction/history', methods=['GET'])
def get_foreign_transaction_history():
    symbol = request.args.get('symbol','').upper()
    period = request.args.get('period','5d')
    try:
        ticker = yf.Ticker(f"{symbol}.JK")
        if period=='5d': hist = ticker.history(period='5d',interval='1d')
        elif period=='1m': hist = ticker.history(period='1mo',interval='1d')
        else: hist = ticker.history(period='ytd',interval='1d')
        if hist.empty: raise Exception("No data")
        prices = hist['Close'].tolist()
        volumes = (hist['Volume']/1_000_000).tolist()
        dates = [d.strftime('%d %b') for d in hist.index]
        net = []
        for i in range(1,len(prices)):
            pct = (prices[i]-prices[i-1])/prices[i-1]*100
            vol_factor = min(volumes[i]/2000,1.5) if volumes[i] else 0.5
            net.append(round(pct*vol_factor*5,1))
        net.insert(0,0)
        if len(dates)>len(net): net = net[:len(dates)]
        if len(dates)<len(net): net = net[:len(dates)]
    except:
        random.seed(hash(symbol)%10000 + hash(period)%100)
        if period=='5d':
            dates = ['20 May','21 May','22 May','23 May','24 May']
            net = [random.uniform(-30,50) for _ in range(5)]
            volumes = [random.randint(300,1500) for _ in range(5)]
        elif period=='1m':
            dates = ['Week1','Week2','Week3','Week4']
            net = [random.uniform(-20,40) for _ in range(4)]
            volumes = [random.randint(1000,3000) for _ in range(4)]
        else:
            months = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']
            length = random.randint(5,12)
            dates = months[:length]
            net = [random.uniform(-30,40) for _ in range(length)]
            volumes = [random.randint(5000,15000) for _ in range(length)]
    net = [round(v,1) for v in net]
    return jsonify({'symbol':symbol,'period':period,'dates':dates,'net_values':net,'volumes':volumes,
                    'current_price':fetch_quote_with_fallback(symbol).get('price',0),'timestamp':datetime.now().isoformat()})

@app.route('/sparkline', methods=['GET'])
def get_sparkline():
    symbol = request.args.get('symbol','').upper()
    period = request.args.get('period','1mo')
    try:
        ticker = yf.Ticker(f"{symbol}.JK")
        if period=='1d': hist = ticker.history(period='5d',interval='1h')
        elif period=='5d': hist = ticker.history(period='5d',interval='15m')
        else: hist = ticker.history(period='1mo',interval='1d')
        if hist.empty: prices = [5000 + i*(10 if i<15 else -5) for i in range(30)]
        else: prices = hist['Close'].tolist()
        minp,maxp = min(prices),max(prices)
        if maxp==minp: norm = [50]*len(prices)
        else: norm = [((p-minp)/(maxp-minp))*100 for p in prices]
        change = ((prices[-1]-prices[0])/prices[0]*100) if len(prices)>1 else 0
    except:
        prices = [5000+i*(10 if i<15 else -5) for i in range(30)]
        norm = [(i/29)*100 for i in range(30)]
        change = 0
    return jsonify({'symbol':symbol,'prices':prices,'normalized':norm,'period':period,'change':change,
                    'timestamp':datetime.now().isoformat()})

# ============ TOP MOVERS ENDPOINT (80 saham, cache 15 detik) ============
def fetch_quote_for_top_mover(symbol):
    try:
        yf_symbol = f"{symbol}.JK"
        ticker = yf.Ticker(yf_symbol)
        info = ticker.info
        price = info.get('regularMarketPrice',0)
        prev_close = info.get('previousClose',price)
        change_pct = ((price - prev_close)/prev_close*100) if prev_close else 0
        if price>0: return {'symbol':symbol,'price':price,'changePercent':change_pct}
    except: pass
    return None

# ============ DAFTAR SAHAM IHSG (200+ saham) ============
IHSG_STOCKS_200 = [
    "BBCA", "BBRI", "BMRI", "TLKM", "ASII", "GOTO", "UNVR", "ADRO", "CPIN", "ICBP",
    "INDF", "MEDC", "PGAS", "SMGR", "ANTM", "HRUM", "TOWR", "ERAA", "SIDO", "JPFA",
    "MDKA", "INKP", "TKIM", "BRIS", "BBNI", "UNTR", "WIKA", "AMMN", "RAJA", "BUMI",
    "PTRO", "ACES", "ADMF", "AGII", "AKRA", "AMRT", "APLN", "ARTO", "ASSA", "BFIN",
    "BHIT", "BIRD", "BISI", "BNGA", "BNII", "BSDE", "BTPS", "BUKA", "BULL", "BWPT",
    "CAMP", "CBMF", "CENT", "CFIN", "CINT", "CITA", "CLPI", "CMNP", "CNKO", "COAL",
    "CPRO", "CSAP", "CTRA", "DART", "DIVA", "DMAS", "DNET", "DOOH", "DPNS", "DSSA",
    "DSNG", "DTLA", "DYAN", "EKAD", "ELSA", "EMTK", "ENRG", "ERTX", "ESIP", "ESSA",
    "FAPA", "FAST", "FISH", "FORZ", "FPNI", "GDST", "GEMS", "GGRM", "GIAA", "GJTL",
    "GLOB", "GLVA", "GPRA", "GPSO", "GSMF", "GZCO", "HADE", "HDFA", "HDIT", "HEAL",
    "HELP", "HELS", "HERO", "HITS", "HKMU", "HMSP", "HOKI", "HOMI", "HOTL", "HRTA",
    "IATA", "IBST", "ICBP", "ICON", "IDPR", "IFII", "IFSH", "IGAR", "IIKP", "IKAI",
    "IKAN", "IMAS", "IMJS", "IMPC", "INAF", "INAI", "INCF", "INCO", "INDS", "INDX",
    "INKP", "INPC", "INPP", "INPS", "INRU", "INTD", "INTP", "IPCC", "IPCM", "IPOL",
    "IPTV", "IRRA", "ISAT", "ISIG", "ISSP", "ITIC", "ITMA", "ITMG", "JAWA", "JECC",
    "JGLE", "JIHD", "JKON", "JKSW", "JMAS", "JPFA", "JRPT", "JSKY", "JSMR", "JSPT",
    "JTPE", "KAEF", "KARY", "KAYU", "KBAG", "KBLI", "KBLM", "KBLV", "KDSI", "KEEN",
    "KEJU", "KIAS", "KICI", "KIJA", "KINO", "KIOS", "KJEN", "KLBF", "KMDS", "KMTR",
    "KOBX", "KOIN", "KONI", "KOPI", "KOTA", "KPAS", "KPIG", "KRAH", "KRAS", "KREN",
    "LCAS", "LPCK", "LPKR", "LPPF", "LPPS", "LRNA", "LSIP", "LUCK", "MAGP", "MAIN",
    "MAMI", "MAPA", "MAPB", "MAPI", "MARI", "MARK", "MASA", "MAYA", "MBAP", "MBSS",
    "MBTO", "MCAS", "MCOR", "MDIA", "MDKA", "MDKI", "MDLN", "MDRN", "MEDC", "MEGA",
    "MERK", "META", "MFIN", "MFMI", "MGNA", "MGLV", "MICE", "MIDI", "MIKA", "MINA"
]

@app.route('/top_movers', methods=['GET'])
def get_top_movers():
    limit = request.args.get('limit', default=10, type=int)
    cache_key = f"top_movers_{limit}"
    cached = quote_cache.get(cache_key)
    if cached:
        return jsonify(cached)

    results = []

    def fetch_data(sym):
        try:
            yf_symbol = f"{sym}.JK"
            ticker = yf.Ticker(yf_symbol)
            # Menggunakan history(1d) lebih cepat daripada info untuk batch besar
            hist = ticker.history(period="2d")
            if len(hist) >= 2:
                price = hist['Close'].iloc[-1]
                prev_close = hist['Close'].iloc[-2]
                change_pct = ((price - prev_close) / prev_close * 100)
                return {'symbol': sym, 'price': price, 'changePercent': change_pct}
        except:
            pass
        return None

    # Gunakan ThreadPoolExecutor untuk memproses 200+ saham secara paralel
    with ThreadPoolExecutor(max_workers=20) as executor:
        future_to_stock = {executor.submit(fetch_data, sym): sym for sym in IHSG_STOCKS_200}
        for future in as_completed(future_to_stock):
            res = future.result()
            if res:
                results.append(res)

    results.sort(key=lambda x: x['changePercent'], reverse=True)
    top_results = results[:limit]

    response = {
        'success': True,
        'count': len(top_results),
        'top_movers': top_results,
        'timestamp': datetime.now().isoformat(),
        'total_stocks_processed': len(results)
    }
    quote_cache.set(cache_key, response)
    return jsonify(response)

# ============ BULK ENDPOINTS ============
@app.route('/bulk/foreigntransaction', methods=['POST'])
def get_bulk_foreign_transaction():
    data = request.json
    symbols = data.get('symbols', [])
    if not symbols: return jsonify({'error':'No symbols'}),400
    results = {}
    for symbol in symbols:
        symbol = symbol.upper()
        quote = fetch_quote_with_fallback(symbol)
        price = quote['price']
        volume = quote.get('volume',1000000)
        total_val = (price*volume)/1_000_000_000
        random.seed(hash(symbol)%10000)
        net_flow_pct = random.uniform(-0.3,0.3)
        total_buy = total_val*(0.5+net_flow_pct/2)
        total_sell = total_val*(0.5-net_flow_pct/2)
        broker_names = ["Credit Suisse","Morgan Stanley","Goldman Sachs","KZ","RX","UBS","J.P. Morgan","Deutsche Bank","ZP","CC"]
        random.seed(hash(symbol)%10000+1)
        buyers = random.sample(broker_names,5)
        sellers = random.sample(broker_names,5)
        buyer_allocs = [random.random() for _ in range(5)]
        seller_allocs = [random.random() for _ in range(5)]
        buyer_allocs = [w/sum(buyer_allocs)*total_buy for w in buyer_allocs]
        seller_allocs = [w/sum(seller_allocs)*total_sell for w in seller_allocs]
        buyers_data = [{'name':n,'avg':round(price*random.uniform(0.995,0.999)),'val':round(v,1)} for n,v in zip(buyers,buyer_allocs)]
        sellers_data = [{'name':n,'avg':round(price*random.uniform(1.001,1.005)),'val':round(v,1)} for n,v in zip(sellers,seller_allocs)]
        buyers_data.sort(key=lambda x:x['val'], reverse=True)
        sellers_data.sort(key=lambda x:x['val'], reverse=True)
        results[symbol] = {'buyers':buyers_data[:5],'sellers':sellers_data[:5]}
    return jsonify({'success':True,'count':len(results),'data':results,'timestamp':datetime.now().isoformat()})

@app.route('/bulk/orderbook', methods=['POST'])
def get_bulk_orderbook():
    data = request.json
    symbols = data.get('symbols', [])
    if not symbols: return jsonify({'error':'No symbols'}),400
    results = {}
    for sym in symbols:
        quote = fetch_quote_with_fallback(sym)
        price = quote['price']
        bids = [int(price-i) for i in range(1,11)]
        asks = [int(price+i) for i in range(1,11)]
        bid_lots = [int(price*100*(0.8+i*0.05)) for i in range(10)]
        ask_lots = [int(price*100*(0.7+i*0.05)) for i in range(10)]
        bid_freqs = [3,15,12,8,5,4,6,7,9,10]
        ask_freqs = [10,9,5,6,7,8,4,5,6,7]
        order_book = [{'bid_freq':bid_freqs[i],'bid_lot':bid_lots[i],'bid_price':bids[i],
                       'ask_price':asks[i],'ask_lot':ask_lots[i],'ask_freq':ask_freqs[i]} for i in range(10)]
        results[sym] = {'order_book':order_book, 'last_price':price}
    return jsonify({'success':True,'count':len(results),'data':results,'timestamp':datetime.now().isoformat()})

@app.route('/bulk', methods=['POST'])
def get_bulk():
    data = request.json
    symbols = data.get('symbols', [])
    if not symbols: return jsonify({'error':'No symbols'}),400
    res = {}
    for sym in symbols:
        q = fetch_quote_with_fallback(sym)
        res[sym] = {'price':q.get('price',0), 'changePercent':q.get('changePercent',0), 'source':q.get('source','unknown')}
    return jsonify({'success':True,'count':len(res),'data':res,'timestamp':datetime.now().isoformat()})

@app.route('/bulk/keystats', methods=['POST'])
def get_bulk_keystats():
    data = request.json
    symbols = data.get('symbols', [])
    if not symbols: return jsonify({'error':'No symbols'}),400
    res = {}
    for sym in symbols: res[sym] = get_keystats_data(sym)
    return jsonify({'success':True,'count':len(res),'data':res,'timestamp':datetime.now().isoformat()})

@app.route('/bulk/bandarmology', methods=['POST'])
def get_bulk_bandarmology():
    data = request.json
    symbols = data.get('symbols', [])
    if not symbols: return jsonify({'error':'No symbols'}),400
    res = {}
    for sym in symbols:
        a = get_bandarmology_analysis(sym)
        res[sym] = {'price':a.get('price',0),'changePercent':a.get('changePercent',0),'signal':a.get('signal','NEUTRAL'),
                    'recommendation':a.get('recommendation','HOLD'),'potentialGain':a.get('potentialGain',0),
                    'volumeRatio':a.get('volumeRatio',1.0),'name':a.get('name',sym)}
    return jsonify({'success':True,'count':len(res),'data':res,'timestamp':datetime.now().isoformat()})

# ============ CHAT ENDPOINT ============
@app.route('/chat', methods=['POST'])
def chat():
    data = request.get_json()
    user_message = data.get('message','')
    session_id = data.get('session_id')
    if not session_id: session_id = str(uuid.uuid4())
    add_to_history(session_id, "user", user_message)
    symbols = re.findall(r'\b([A-Z]{4})\b', user_message.upper())
    if not symbols and ('saham' in user_message.lower() or 'rekomendasi' in user_message.lower()):
        symbols = ["BBCA","BBRI","BMRI"]
    data_text = ""
    for sym in symbols[:5]:
        q = fetch_quote_with_fallback(sym)
        avg_vol = get_avg_volume(sym)
        vol_ratio = q.get('volume',0)/avg_vol if avg_vol>0 else 1
        signal = "NEUTRAL"
        if vol_ratio>1.5 and q.get('changePercent',0)>0: signal="ACCUMULATION"
        elif vol_ratio>1.5 and q.get('changePercent',0)<0: signal="DISTRIBUTION"
        data_text += f"\n[{sym}] Price: Rp{q.get('price',0):,.0f} ({q.get('changePercent',0):+.2f}%) Volume: {q.get('volume',0)/1e6:.1f}M ({vol_ratio:.1f}x avg) Signal: {signal}"
    system_prompt = f"""You are a stock assistant for IHSG. Answer BRIEFLY using EXACT format below. Use real-time data:\n{data_text}\n\n=== SUMMARY ===\n(one sentence)\n--- STOCK: CODE ---\n- Price: RpX (X%)\n- Volume: XM (Xx avg)\n- Signal: X\n- View: X\n=== CONCLUSION ===\n(one sentence)\nDISCLAIMER: Not investment advice."""
    headers = {"Authorization": f"Bearer {DEEPSEEK_API_KEY}", "Content-Type": "application/json"}
    payload = {"model":"deepseek-chat","messages":[{"role":"system","content":system_prompt},{"role":"user","content":user_message}],"temperature":0.5,"max_tokens":500,"stream":True}
    def generate():
        full = ""
        try:
            resp = requests.post(DEEPSEEK_API_URL, headers=headers, json=payload, stream=True, timeout=60)
            for line in resp.iter_lines():
                if line:
                    line = line.decode('utf-8')
                    if line.startswith('data: '):
                        data = line[6:]
                        if data == '[DONE]': break
                        try:
                            chunk = json.loads(data)
                            delta = chunk['choices'][0].get('delta',{})
                            content = delta.get('content','')
                            if content:
                                full += content
                                yield f"data: {json.dumps({'content':content})}\n\n"
                        except: pass
            add_to_history(session_id, "assistant", full)
            yield "data: [DONE]\n\n"
        except Exception as e:
            yield f"data: {json.dumps({'error':str(e)})}\n\n"
            yield "data: [DONE]\n\n"
    return Response(stream_with_context(generate()), mimetype='text/event-stream')

@app.route('/clear_session', methods=['POST'])
def clear_session():
    data = request.json
    session_id = data.get('session_id')
    if session_id: clear_session_history(session_id)
    return jsonify({'success':True}) if session_id else jsonify({'error':'No session_id'}),400

if __name__ == '__main__':
    print("="*60); print("API Server Starting..."); print("Port: 5002")
    app.run(host='0.0.0.0', port=5002, debug=True, threaded=True)
# trigger redeploy for top_movers

# Force redeploy - Wed May  6 20:25:40 WIB 2026
