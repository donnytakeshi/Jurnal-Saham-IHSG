from flask import Flask, jsonify, request, Response, stream_with_context
from flask_cors import CORS
import yfinance as yf
import requests
import json
import re
import uuid
import os
import time
import base64
from datetime import datetime, timedelta
from functools import wraps
from collections import OrderedDict
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

    quote = fetch_quote_with_fallback(symbol)
    price = quote['price']

    # UBAH: 10 baris orderbook (dari 3 menjadi 10)
    bids = [int(price - i) for i in range(1, 11)]
    asks = [int(price + i) for i in range(1, 11)]
    bid_lots = [int(price * 100 * (0.8 + i*0.05)) for i in range(10)]
    ask_lots = [int(price * 100 * (0.7 + i*0.05)) for i in range(10)]
    bid_freq = [3, 15, 12, 8, 5, 4, 6, 7, 9, 10]
    ask_freq = [10, 9, 5, 6, 7, 8, 4, 5, 6, 7]

    order_book = []
    for i in range(10):
        order_book.append({
            'bid_freq': bid_freq[i],
            'bid_lot': bid_lots[i],
            'bid_price': bids[i],
            'ask_price': asks[i],
            'ask_lot': ask_lots[i],
            'ask_freq': ask_freq[i]
        })

    result = {
        'symbol': symbol,
        'order_book': order_book,
        'last_price': price,
        'source': quote.get('source', 'unknown')
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

# ============ NEW ENDPOINT: FOREIGN TRANSACTION HISTORY ============
@app.route('/foreigntransaction/history', methods=['GET'])
def get_foreign_transaction_history():
    symbol = request.args.get('symbol', '').upper()
    period = request.args.get('period', '5d')
    
    quote = fetch_quote_with_fallback(symbol)
    price = quote['price']
    
    # Generate historical data based on period
    if period == '5d':
        dates = ['20 May', '21 May', '22 May', '23 May', '24 May']
        net_values = [25.5, -12.3, 38.7, -8.2, 45.1]
        volumes = [850, 620, 1200, 450, 980]
    elif period == '1m':
        dates = ['Week 1', 'Week 2', 'Week 3', 'Week 4']
        net_values = [18.2, -5.7, 42.3, -15.8]
        volumes = [2100, 1800, 3200, 1500]
    else:  # ytd
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

# ============ NEW ENDPOINT: SPARKLINE DATA ============
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
        
        # Normalize to 0-100 range for chart
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

# ============ BATCH ENDPOINTS ============
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
        
        # UBAH: 10 baris orderbook untuk bulk endpoint juga
        bids = [int(price - i) for i in range(1, 11)]
        asks = [int(price + i) for i in range(1, 11)]
        bid_lots = [int(price * 100 * (0.8 + i*0.05)) for i in range(10)]
        ask_lots = [int(price * 100 * (0.7 + i*0.05)) for i in range(10)]
        bid_freq = [3, 15, 12, 8, 5, 4, 6, 7, 9, 10]
        ask_freq = [10, 9, 5, 6, 7, 8, 4, 5, 6, 7]
        
        order_book = []
        for i in range(10):
            order_book.append({
                'bid_freq': bid_freq[i],
                'bid_lot': bid_lots[i],
                'bid_price': bids[i],
                'ask_price': asks[i],
                'ask_lot': ask_lots[i],
                'ask_freq': ask_freq[i]
            })
        results[symbol] = {'order_book': order_book, 'last_price': price}
    return jsonify({'success': True, 'count': len(results), 'data': results, 'timestamp': datetime.now().isoformat()})

if __name__ == '__main__':
    print("=" * 60)
    print("API Server Starting...")
    print("Finnhub + Alpha Vantage + yfinance (fallback)")
    print("Supported: PDF, DOCX, TXT, CSV")
    print("Images: NOT processed (OCR disabled)")
    print("Response format: SHORT and STRUCTURED")
    print("Cache: Quote 15s, Orderbook 30s")
    print("NEW: Orderbook now shows 10 levels")
    print("NEW: Sparkline endpoint /sparkline added")
    print("NEW: Bulk endpoint /bulk/foreigntransaction added")
    print("NEW: History endpoint /foreigntransaction/history added")
    print("=" * 60)
    app.run(host='0.0.0.0', port=5001, debug=True, threaded=True)