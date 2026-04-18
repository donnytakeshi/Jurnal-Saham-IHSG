"""
Module untuk mengambil data saham dari yfinance
"""

import warnings
warnings.filterwarnings('ignore')

# Prefer TradingView snapshot fetcher when available
try:
    from modules.tradingview_fetcher import fetch_tradingview_snapshot
except Exception:
    fetch_tradingview_snapshot = None


class DataFetcher:
    """Ambil data harga saham dari TradingView"""
    def __init__(self):
        self.sample_stocks = [
            {'symbol': 'BBCA', 'company_name': 'Bank Central Asia'},
            {'symbol': 'BBRI', 'company_name': 'Bank Rakyat Indonesia'},
            {'symbol': 'TLKM', 'company_name': 'Telkom Indonesia'},
            {'symbol': 'BMRI', 'company_name': 'Bank Mandiri'},
            {'symbol': 'BBNI', 'company_name': 'Bank Negara Indonesia'},
        ]

    def fetch_all_data(self):
        # Try fast bulk snapshot from our TradingView scanner wrapper
        symbols = [s['symbol'] for s in self.sample_stocks]
        if fetch_tradingview_snapshot:
            try:
                snap = fetch_tradingview_snapshot(symbols)
                results = []
                for s in self.sample_stocks:
                    sym = s['symbol']
                    info = snap.get(sym) or {}
                    price = info.get('price') if info else '-'
                    results.append({
                        'symbol': sym,
                        'company_name': s['company_name'],
                        'last_close': price
                    })
                return results
            except Exception as e:
                print('fetch_tradingview_snapshot failed:', e)

        # Fallback: try using tradingview_ta handler per-symbol
        try:
            from tradingview_ta import TA_Handler, Interval
            results = []
            for stock in self.sample_stocks:
                try:
                    handler = TA_Handler(
                        symbol=f"{stock['symbol']}JK",
                        screener="indonesia",
                        exchange="IDX",
                        interval=Interval.INTERVAL_1_DAY
                    )
                    analysis = handler.get_analysis()
                    price = analysis.indicators.get('close')
                    results.append({
                        'symbol': stock['symbol'],
                        'company_name': stock['company_name'],
                        'last_close': price
                    })
                except Exception as e:
                    print(f"TradingView TA error {stock['symbol']}: {e}")
                    results.append({
                        'symbol': stock['symbol'],
                        'company_name': stock['company_name'],
                        'last_close': '-'
                    })
            return results
        except Exception:
            # Final fallback: return placeholder values
            results = []
            for stock in self.sample_stocks:
                results.append({
                    'symbol': stock['symbol'],
                    'company_name': stock['company_name'],
                    'last_close': '-'
                })
            return results
    
    def fetch_stock_data(self, stock_code, period='3mo'):
        """
        Mengambil data satu saham
        
        Parameters:
        -----------
        stock_code : str
            Kode saham (contoh: 'BBCA')
        period : str
            Period data yang diambil
            
        Returns:
        --------
        pd.DataFrame : OHLCV data
        """
        if not stock_code.endswith('.JK'):
            stock_code = f"{stock_code}.JK"
        
        ticker = yf.Ticker(stock_code)
        return ticker.history(period=period)
    
    def fetch_intraday_data(self, stock_code, interval='5m'):
        """
        Mengambil data intraday
        
        Parameters:
        -----------
        stock_code : str
            Kode saham
        interval : str
            Interval data ('1m', '5m', '15m', '1h', dst)
            
        Returns:
        --------
        pd.DataFrame : Intraday OHLCV data
        """
        if not stock_code.endswith('.JK'):
            stock_code = f"{stock_code}.JK"
        
        ticker = yf.Ticker(stock_code)
        return ticker.history(period='1d', interval=interval)
    
    def get_quarter_data(self, stock_code):
        """
        Mengambil data fundamental per kuartal
        
        Parameters:
        -----------
        stock_code : str
            Kode saham
            
        Returns:
        --------
        dict : Data fundamental
        """
        if not stock_code.endswith('.JK'):
            stock_code = f"{stock_code}.JK"
        
        ticker = yf.Ticker(stock_code)
        return {
            'info': ticker.info,
            'quarterly_financials': ticker.quarterly_financials,
            'quarterly_balance_sheet': ticker.quarterly_balance_sheet
        }
