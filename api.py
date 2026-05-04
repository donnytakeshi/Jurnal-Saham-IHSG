from flask import Flask, jsonify, request, Response, stream_with_context
from flask_cors import CORS
import yfinance as yf
import requests
import json
import re
import time

app = Flask(__name__)
CORS(app)

DEEPSEEK_API_KEY = "sk-0422844a615144caabf1fd149087463e"
DEEPSEEK_API_URL = "https://api.deepseek.com/v1/chat/completions"

# ============ DAFTAR SAHAM ============
SECONDLINE_STOCKS = {
    "CPIN": "Charoen Pokphand",
    "ICBP": "Indofood CBP",
    "INDF": "Indofood",
    "MEDC": "Medco Energi",
    "PGAS": "Perusahaan Gas Negara",
    "SMGR": "Semen Indonesia",
    "ANTM": "Aneka Tambang",
    "HRUM": "Harum Energy",
    "TOWR": "Sarana Menara Nusantara",
    "ERAA": "Erajaya Swasembada",
    "SIDO": "Sido Muncul",
    "JPFA": "Japfa Comfeed",
    "MDKA": "Merdeka Copper Gold",
    "INKP": "Indah Kiat Pulp",
    "TKIM": "Pabrik Kertas Tjiwi Kimia",
    "BRIS": "Bank BRISyariah",
    "BBNI": "Bank BNI",
    "UNTR": "United Tractors",
    "WIKA": "Wijaya Karya",
    "AMMN": "Amman Mineral",
    "ACES": "Ace Hardware",
    "ARTO": "Bank Artos",
    "BUKA": "Bukalapak",
    "MTDL": "Metrodata Electronics",
    "MAPI": "Mitra Adiperkasa",
    "MPMX": "Mitra Pinasthika Mustika",
    "MYOR": "Mayora Indah",
    "PSAB": "J Resources Asia",
    "PWON": "Pakuwon Jati",
    "SCMA": "Surya Citra Media",
    "SMRA": "Summarecon Agung",
}

ALL_STOCKS = {
    "BBCA": "Bank Central Asia",
    "BBRI": "Bank Rakyat Indonesia",
    "BMRI": "Bank Mandiri",
    "TLKM": "Telkom Indonesia",
    "ASII": "Astra International",
    "GOTO": "GoTo Gojek Tokopedia",
    "UNVR": "Unilever Indonesia",
    "ADRO": "Adaro Energy",
    **SECONDLINE_STOCKS
}

# ============ FUNGSI BANDARMOLOGY ============
def get_bandarmology_analysis(symbol):
    """Analisis bandarmology lengkap untuk satu saham"""
    yf_symbol = f"{symbol}.JK"
    try:
        ticker = yf.Ticker(yf_symbol)
        info = ticker.info
        
        price = info.get('regularMarketPrice', 0)
        prev_close = info.get('previousClose', price)
        change = price - prev_close if prev_close else 0
        change_pct = (change / prev_close * 100) if prev_close else 0
        volume = info.get('regularMarketVolume', 0)
        avg_volume = info.get('averageVolume', 1)
        bid = info.get('bid', price * 0.998 if price else 0)
        ask = info.get('ask', price * 1.002 if price else 0)
        
        volume_ratio = volume / avg_volume if avg_volume > 0 else 1
        spread = (ask - bid) / price * 100 if price else 0
        is_bid_greater = bid > ask * 0.95
        
        is_accumulation = volume_ratio > 1.2 and change_pct > 0
        is_distribution = volume_ratio > 1.2 and change_pct < 0
        is_breakout = change_pct > 2 and volume_ratio > 1.5
        
        potential_gain = 0
        if is_accumulation and change_pct > 0:
            potential_gain = min(change_pct * 2, 15)
        elif is_breakout:
            potential_gain = min(change_pct * 1.5, 12)
        elif change_pct > 0:
            potential_gain = change_pct * 1.2
        else:
            potential_gain = max(change_pct * 0.5, -5)
        
        return {
            'symbol': symbol,
            'name': ALL_STOCKS.get(symbol, symbol),
            'price': price,
            'changePercent': change_pct,
            'volumeRatio': volume_ratio,
            'isAccumulation': is_accumulation,
            'isBreakout': is_breakout,
            'potentialGain': potential_gain,
            'signal': 'ACCUMULATION' if is_accumulation else ('BREAKOUT' if is_breakout else ('DISTRIBUTION' if is_distribution else 'NEUTRAL')),
            'recommendation': 'BUY' if (is_accumulation or is_breakout) and change_pct > 0 else 'HOLD'
        }
    except Exception as e:
        return {'error': str(e)}

def analyze_bandarmology_complete(symbol):
    """Analisis bandarmology lengkap dengan broker sentiment"""
    base = get_bandarmology_analysis(symbol)
    if 'error' in base:
        return base
    
    if base['volumeRatio'] > 1.5:
        broker_activity = "AGGRESSIVE"
    elif base['volumeRatio'] > 0.8:
        broker_activity = "NORMAL"
    else:
        broker_activity = "LOW"
    
    if base['isAccumulation']:
        broker_sentiment = "ACCUMULATION (BUY)"
    elif base['isBreakout']:
        broker_sentiment = "BREAKOUT (BULLISH)"
    elif base['changePercent'] > 0:
        broker_sentiment = "POSITIVE"
    else:
        broker_sentiment = "NEUTRAL"
    
    base['brokerActivity'] = broker_activity
    base['brokerSentiment'] = broker_sentiment
    return base

def get_secondline_predictions():
    """Cari saham secondline dengan potensi kenaikan minimal 6%"""
    results = []
    for symbol in SECONDLINE_STOCKS.keys():
        analysis = analyze_bandarmology_complete(symbol)
        if 'error' not in analysis:
            # Filter saham dengan potensi menarik
            if (analysis['potentialGain'] >= 6 or 
                analysis['isAccumulation'] or 
                analysis['isBreakout'] or
                (analysis['changePercent'] > 1 and analysis['volumeRatio'] > 1.2)):
                results.append(analysis)
    
    results.sort(key=lambda x: x['potentialGain'], reverse=True)
    return results[:10]

def generate_prediction_table(predictions):
    """Generate HTML table untuk prediksi"""
    if not predictions:
        return "<div class='text-slate-400 p-3 text-center'>Belum ada data prediksi yang cukup. Coba lagi nanti.</div>"
    
    html = '<div class="overflow-x-auto my-3"><table style="width:100%; border-collapse:collapse; font-size:12px;"><thead><tr style="border-bottom:1px solid rgba(255,255,255,0.1);">'
    html += '<th style="text-align:left; padding:8px 4px; color:#8b919b;">Kode</th><th style="text-align:left; padding:8px 4px; color:#8b919b;">Nama</th>'
    html += '<th style="text-align:right; padding:8px 4px; color:#8b919b;">Harga</th><th style="text-align:right; padding:8px 4px; color:#8b919b;">Perubahan</th>'
    html += '<th style="text-align:right; padding:8px 4px; color:#8b919b;">Volume</th><th style="text-align:left; padding:8px 4px; color:#8b919b;">Signal</th>'
    html += '<th style="text-align:right; padding:8px 4px; color:#8b919b;">Potensi</th></tr></thead><tbody>'
    
    for s in predictions[:8]:
        change_class = 'style="color:#67d9cb;"' if s['changePercent'] >= 0 else 'style="color:#ff5e5e;"'
        potential_class = 'style="color:#67d9cb; font-weight:bold;"' if s['potentialGain'] >= 6 else 'style="color:#f2d18f;"'
        signal_color = '#67d9cb' if 'ACCUMULATION' in s['signal'] or 'BREAKOUT' in s['signal'] else ('#ff5e5e' if 'DISTRIBUTION' in s['signal'] else '#8b919b')
        
        html += f'''
            <tr style="border-bottom:1px solid rgba(255,255,255,0.05);">
                <td style="padding:8px 4px; font-weight:bold; color:white;">{s['symbol']}</td>
                <td style="padding:8px 4px; color:#bcc9c6; font-size:10px;">{s['name'][:20]}</td>
                <td style="padding:8px 4px; text-align:right; color:white;">{s['price']:,.0f}</td>
                <td style="padding:8px 4px; text-align:right; {change_class}">{s['changePercent']:+.2f}%</td>
                <td style="padding:8px 4px; text-align:right; color:white;">{s['volumeRatio']:.1f}x</td>
                <td style="padding:8px 4px; color:{signal_color};">{s['signal']}</td>
                <td style="padding:8px 4px; text-align:right; {potential_class}">{s['potentialGain']:+.1f}%</td>
            </tr>
        '''
    
    html += '</tbody></table></div>'
    return html

# ============ DETEKSI PERTANYAAN ============
def is_prediction_question(message):
    keywords = ['naik', 'turun', 'besok', 'prediksi', 'rekomendasi', 'beli', 'jual',
                'secondline', '6%', 'fluktuatif', 'saham apa', 'yg bagus', 'cuan']
    msg = message.lower()
    if 'prediksi' in msg and ('naik' in msg or 'besok' in msg):
        return True
    return any(kw in msg for kw in keywords)

def is_secondline_request(message):
    msg = message.lower()
    return ('secondline' in msg or 'minimal 6%' in msg or 
            '6%' in msg or 'fluktuatif' in msg or
            ('prediksi' in msg and 'naik' in msg))

# ============ ENDPOINTS ============
@app.route('/quote', methods=['GET'])
def get_quote():
    symbol = request.args.get('symbol', '').upper()
    if not symbol:
        return jsonify({'error': 'No symbol'}), 400
    
    yf_symbol = f"{symbol}.JK"
    try:
        ticker = yf.Ticker(yf_symbol)
        info = ticker.info
        price = info.get('regularMarketPrice')
        prev_close = info.get('previousClose')
        market_state = info.get('marketState', 'CLOSED')
        change_pct = info.get('regularMarketChangePercent', 0)
        
        is_closed = (market_state == 'CLOSED' or price is None)
        if is_closed and prev_close:
            price = prev_close
            change_pct = 0
        
        return jsonify({'symbol': symbol, 'price': price, 'changePercent': change_pct, 'isClosed': is_closed})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/predict', methods=['GET'])
def predict():
    predictions = get_secondline_predictions()
    return jsonify({'predictions': predictions})

@app.route('/chat', methods=['POST'])
def chat():
    data = request.json
    user_message = data.get('message', '')
    if not user_message:
        return jsonify({'error': 'No message'}), 400
    
    is_pred = is_prediction_question(user_message)
    is_second = is_secondline_request(user_message)
    
    prediction_table = ""
    predictions_data = []
    
    if is_second:
        predictions_data = get_secondline_predictions()
        prediction_table = generate_prediction_table(predictions_data)
    
    stock_codes = re.findall(r'\b([A-Z]{4})\b', user_message.upper())
    stock_analysis = {}
    for code in stock_codes[:3]:
        stock_analysis[code] = get_bandarmology_analysis(code)
    
    # SYSTEM PROMPT YANG NATURAL (TIDAK KAKU)
    system_prompt = """Lo adalah asisten analis saham IHSG yang asik diajak ngobrol. Panggil diri lo "gue" dan panggil user "lo". Boleh pake kata "nih", "dong", "deh" biar ga kaku.

Lo punya data real-time dari pasar: harga, perubahan persen, volume, dan sinyal bandarmology.

**KALAU USER MINTA PREDIKSI SAHAM (yg mau naik besok, secondline, dll):**
- Lihat data tabel yang udah gue kasih
- Pilih 2-3 saham dengan potensi paling gede
- Jelasin alasannya pake data (harga naik, volume gede, sinyal accumulation)
- Tampilkan tabelnya biar user liat
- Kasih prediksi lo, tapi ingetin juga ini bukan rekomendasi investasi ya

**KALAU USER TANYA HAL LAIN (di luar prediksi saham):**
Lo bebas jawab sesuai pengetahuan lo. Ga perlu pake data saham kalo ga relevan.

Contoh gaya jawaban yang bener:
"Nah dari data nih, yang paling kelihatan menarik itu BBCA sama ADRO. BBCA harganya naik 2.5% tadi dengan volume 1.8x di atas rata-rata, ini sinyal accumulation. Buat besok, ada potensi lanjut naik ke Rp10.800an. ADRO juga menarik dengan volume 2.1x. Tapi inget ya, ini cuma analisa, bukan rekomendasi beli."

JANGAN JAWAB PAKAI TEMPLATE YANG KAKU! Jawab kayak lagi ngobrol santai. Dan jangan lupa disclaimernya."""

    # Context dengan data
    context = ""
    if is_second and prediction_table:
        context += f"\n\nINI DATA REAL-TIME SAHAM SECONDLINE (WAJIB DIPAKE BUAT JAWAB):\n{prediction_table}\n\n"
        context += "TUGAS LO: Pilih 3 saham terbaik dari tabel di atas, jelasin kenapa bagus, dan kasih prediksi buat besok. Tampilkan tabelnya juga ya.\n"
    
    if stock_analysis:
        context += "\nDATA SAHAM YANG DISEBUT USER:\n"
        for code, analysis in stock_analysis.items():
            if 'error' not in analysis:
                context += f"- {code}: Rp{analysis['price']:,.0f} ({analysis['changePercent']:+.2f}%), Volume {analysis['volumeRatio']:.1f}x rata-rata, Sinyal: {analysis['signal']}\n"
    
    # Payload ke DeepSeek
    headers = {"Authorization": f"Bearer {DEEPSEEK_API_KEY}", "Content-Type": "application/json"}
    payload = {
        "model": "deepseek-chat",
        "messages": [
            {"role": "system", "content": system_prompt + context},
            {"role": "user", "content": user_message}
        ],
        "temperature": 0.85,
        "max_tokens": 1200,
        "stream": True
    }
    
    def generate():
        try:
            response = requests.post(DEEPSEEK_API_URL, headers=headers, json=payload, stream=True)
            for line in response.iter_lines():
                if line:
                    line = line.decode('utf-8')
                    if line.startswith('data: '):
                        data_str = line[6:]
                        if data_str.strip() == '[DONE]':
                            break
                        try:
                            chunk = json.loads(data_str)
                            if 'choices' in chunk and len(chunk['choices']) > 0:
                                delta = chunk['choices'][0].get('delta', {})
                                if 'content' in delta:
                                    yield f"data: {json.dumps({'content': delta['content']})}\n\n"
                        except:
                            pass
            yield "data: [DONE]\n\n"
        except Exception as e:
            yield f"data: {json.dumps({'error': str(e)})}\n\n"
    
    return Response(stream_with_context(generate()), mimetype='text/event-stream')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True, threaded=True)