"""
mobile_ui.py - Jurnal Saham IHSG Mobile App
Version: 4.0 - Fully Responsive + DeepSeek AI + .env Support
"""

import json
import os
import threading
import traceback
import random
import requests
from datetime import datetime
from functools import partial

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.uix.widget import Widget
from kivy.uix.textinput import TextInput
from kivy.uix.behaviors import ButtonBehavior
from kivy.properties import ListProperty, StringProperty, BooleanProperty
from kivy.event import EventDispatcher
from kivy.utils import get_color_from_hex, platform as _kivy_platform
from kivy.clock import Clock
from kivy.graphics import Color, Rectangle, RoundedRectangle, Line
from kivy.core.window import Window
from kivy.metrics import dp, sp


# ============================================================================
# RESPONSIVE HELPERS (FIX OVERLAPPING ISSUES)
# ============================================================================
def rdp(value):
    """Responsive dp - scales with screen width to prevent overlapping"""
    try:
        screen_width = Window.width
        if screen_width < 400:      # Small phone (e.g., iPhone SE)
            return dp(value * 0.75)
        elif screen_width < 550:    # Normal phone
            return dp(value)
        elif screen_width < 800:    # Large phone / small tablet
            return dp(value * 1.1)
        else:                       # Tablet
            return dp(value * 1.25)
    except:
        return dp(value)


def rsp(value):
    """Responsive sp - scales font sizes properly"""
    try:
        screen_width = Window.width
        if screen_width < 400:
            return sp(value * 0.85)
        elif screen_width < 550:
            return sp(value)
        elif screen_width < 800:
            return sp(value * 1.1)
        else:
            return sp(value * 1.2)
    except:
        return sp(value)


# ============================================================================
# UI HELPERS (Legacy compatibility)
# ============================================================================
def ui_dp(v): return rdp(v)
def ui_sp(v): return rsp(v)


# ============================================================================
# LOAD .ENV FILE (from your VS Code version)
# ============================================================================
env_path = os.path.join(os.path.dirname(__file__), '.env')
if os.path.exists(env_path):
    try:
        with open(env_path, 'r') as _f:
            for _line in _f:
                _line = _line.strip()
                if not _line or _line.startswith('#'):
                    continue
                if '=' in _line:
                    _k, _v = _line.split('=', 1)
                    os.environ.setdefault(_k.strip(), _v.strip())
    except Exception:
        pass


# ============================================================================
# THEME CONFIG (RESPONSIVE)
# ============================================================================
class ThemeConfig:
    # Colors
    BG_MAIN = get_color_from_hex('#0a0c0e')
    SURFACE = get_color_from_hex('#14171a')
    SURFACE_BRIGHT = get_color_from_hex('#1c2024')
    ACCENT = get_color_from_hex('#00d4aa')
    ACCENT_LIGHT = get_color_from_hex('#67d9cb')
    RED = get_color_from_hex('#ff6b6b')
    GREEN = get_color_from_hex('#00d4aa')
    YELLOW = get_color_from_hex('#feca57')
    TEXT_BRIGHT = get_color_from_hex('#ffffff')
    TEXT_DIM = get_color_from_hex('#a0aab5')
    TEXT_MUTED = get_color_from_hex('#5a6670')
    
    # Sizes
    ROUNDNESS = rdp(12)
    NAV_HEIGHT = rdp(60)
    HEADER_HEIGHT = rdp(50)
    BUTTON_HEIGHT = rdp(48)  # Minimum touch target
    CARD_PADDING = rdp(12)
    CARD_SPACING = rdp(10)


# ============================================================================
# DEEPSEEK AI CONFIGURATION (from your VS Code version)
# ============================================================================
class DeepSeekConfig:
    API_URL = "https://api.deepseek.com/v1/chat/completions"
    MODEL = "deepseek-chat"
    API_KEY = 'YOUR_DEEPSEEK_API_KEY_HERE'
    
    # Try keyring
    try:
        import keyring
        _kr = keyring.get_password('jurnalsaham', 'deepseek_api_key')
        if _kr:
            API_KEY = _kr
    except Exception:
        pass
    
    # Try environment variable
    if API_KEY == 'YOUR_DEEPSEEK_API_KEY_HERE':
        _env = os.environ.get('DEEPSEEK_API_KEY')
        if _env:
            API_KEY = _env
    
    # Try config file
    if API_KEY == 'YOUR_DEEPSEEK_API_KEY_HERE':
        cfg_path = os.path.expanduser('~/.config/jurnalsaham/credentials.json')
        if os.path.exists(cfg_path):
            try:
                with open(cfg_path, 'r') as _cf:
                    _data = json.load(_cf)
                    if isinstance(_data, dict) and _data.get('DEEPSEEK_API_KEY'):
                        API_KEY = _data.get('DEEPSEEK_API_KEY')
            except Exception:
                pass
    
    STOCK_CONTEXT = """
    Anda adalah asisten analis saham IHSG Indonesia. Berikan analisis:
    - Teknikal: support/resistance, tren, volume
    - Fundamental: PER, PBV, ROE, dividen
    - Rekomendasi: BUY/SELL/HOLD dengan alasan jelas
    Gunakan format rapi dan sertakan disclaimer.
    """


# ============================================================================
# CUSTOM WIDGETS (RESPONSIVE - NO OVERLAPPING)
# ============================================================================
class StyledCard(BoxLayout):
    """Card with rounded corners - responsive sizing"""
    def __init__(self, bg_color=None, radius=None, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.padding = [ThemeConfig.CARD_PADDING] * 4
        self.spacing = ThemeConfig.CARD_SPACING
        self.size_hint_y = None
        self.height = rdp(80)  # Default, will be adjusted
        
        bg_color = bg_color or ThemeConfig.SURFACE
        radius = radius or ThemeConfig.ROUNDNESS
        with self.canvas.before:
            Color(*bg_color)
            self.rect = RoundedRectangle(pos=self.pos, size=self.size, radius=[radius])
        self.bind(pos=self._update_rect, size=self._update_rect)
    
    def _update_rect(self, *args):
        if hasattr(self, 'rect'):
            self.rect.pos = self.pos
            self.rect.size = self.size


class ModernButton(Button):
    """Button with proper touch target (min 48dp) - NO OVERLAPPING"""
    def __init__(self, bg_color=None, **kwargs):
        super().__init__(**kwargs)
        self.background_normal = ''
        self.background_color = [0, 0, 0, 0]
        self.color = ThemeConfig.TEXT_BRIGHT
        self.bold = True
        self.font_size = rsp(13)
        self.size_hint_y = None
        self.height = ThemeConfig.BUTTON_HEIGHT
        self.padding = [rdp(12), rdp(8)]
        
        bg_color = bg_color or ThemeConfig.ACCENT
        with self.canvas.before:
            Color(*bg_color)
            self.rect = RoundedRectangle(pos=self.pos, size=self.size, radius=[rdp(8)])
        self.bind(pos=self._update_rect, size=self._update_rect)
    
    def _update_rect(self, *args):
        if hasattr(self, 'rect'):
            self.rect.pos = self.pos
            self.rect.size = self.size


class SparklineWidget(Widget):
    """Mini chart widget - responsive"""
    values = ListProperty([])
    line_color = ListProperty([0, 0.83, 0.67, 1])

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.bind(pos=self._redraw, size=self._redraw, values=self._redraw)

    def _redraw(self, *args):
        self.canvas.clear()
        if not self.values or len(self.values) < 2:
            return
        try:
            w = max(1.0, float(self.width))
            h = max(1.0, float(self.height))
            pad = rdp(2)
            xs = []
            vmin = min(self.values)
            vmax = max(self.values)
            flat = (vmax - vmin) == 0
            denom = (vmax - vmin) if not flat else 1.0
            for i, v in enumerate(self.values):
                x = self.x + pad + (w - pad * 2) * (i / (len(self.values) - 1))
                y_norm = 0.5 if flat else ((v - vmin) / denom)
                y = self.y + pad + (h - pad * 2) * y_norm
                xs.extend([x, y])
            with self.canvas:
                Color(*self.line_color)
                Line(points=xs, width=rdp(1.5), cap='round', joint='round')
        except Exception:
            pass


class ChatBubble(BoxLayout):
    """Chat bubble for AI - responsive"""
    text = StringProperty('')
    is_user = BooleanProperty(False)
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.padding = [rdp(12), rdp(8), rdp(12), rdp(8)]
        self.size_hint_y = None
        self.spacing = rdp(4)
        
        if self.is_user:
            bg_color = ThemeConfig.ACCENT
            halign = 'right'
        else:
            bg_color = ThemeConfig.SURFACE_BRIGHT
            halign = 'left'
        
        with self.canvas.before:
            Color(*bg_color)
            self.rect = RoundedRectangle(pos=self.pos, size=self.size, radius=[rdp(16)])
        self.bind(pos=self._update_rect, size=self._update_rect)
        
        self.msg_label = Label(
            text=self.text,
            font_size=rsp(13),
            color=ThemeConfig.TEXT_BRIGHT,
            halign=halign,
            valign='middle',
            size_hint_y=None
        )
        self.msg_label.bind(
            texture_size=self.msg_label.setter('size'),
            size=lambda s, v: setattr(s, 'text_size', (s.width, None))
        )
        self.add_widget(self.msg_label)
        self.bind(minimum_height=self.setter('height'))
    
    def _update_rect(self, *args):
        if hasattr(self, 'rect'):
            self.rect.pos = self.pos
            self.rect.size = self.size


class StockRow(BoxLayout):
    """Single stock row - properly sized, NO OVERLAPPING"""
    def __init__(self, symbol, price, change_pct, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'horizontal'
        self.size_hint_y = None
        self.height = rdp(70)
        self.padding = [rdp(8), rdp(6)]
        self.spacing = rdp(8)
        
        # Background
        with self.canvas.before:
            Color(*ThemeConfig.SURFACE_BRIGHT)
            self.rect = Rectangle(pos=self.pos, size=self.size)
        self.bind(pos=self._update_bg, size=self._update_bg)
        
        # Symbol (left)
        sym_label = Label(
            text=symbol,
            font_size=rsp(16),
            bold=True,
            color=ThemeConfig.TEXT_BRIGHT,
            size_hint_x=0.28,
            halign='left',
            valign='middle'
        )
        sym_label.bind(size=lambda s, v: setattr(s, 'text_size', (s.width, None)))
        self.add_widget(sym_label)
        
        # Price and change (center)
        price_col = BoxLayout(orientation='vertical', size_hint_x=0.44, spacing=rdp(2))
        
        price_label = Label(
            text=f"Rp {price:,.0f}",
            font_size=rsp(15),
            color=ThemeConfig.TEXT_BRIGHT,
            halign='right',
            valign='middle',
            size_hint_y=0.5
        )
        price_label.bind(size=lambda s, v: setattr(s, 'text_size', (s.width, None)))
        price_col.add_widget(price_label)
        
        change_color = ThemeConfig.GREEN if change_pct >= 0 else ThemeConfig.RED
        change_label = Label(
            text=f"{change_pct:+.2f}%",
            font_size=rsp(12),
            bold=True,
            color=change_color,
            halign='right',
            valign='middle',
            size_hint_y=0.5
        )
        change_label.bind(size=lambda s, v: setattr(s, 'text_size', (s.width, None)))
        price_col.add_widget(change_label)
        
        self.add_widget(price_col)
        
        # Mini sparkline (right)
        spark_vals = self._generate_spark(price, change_pct)
        self.spark = SparklineWidget(values=spark_vals, size_hint_x=0.28)
        self.add_widget(self.spark)
    
    def _generate_spark(self, price, change):
        base = price
        vals = [base]
        for i in range(9):
            change_pct = random.uniform(-0.015, 0.015) * abs(change) + 0.001
            base = base * (1 + change_pct)
            vals.append(base)
        return vals
    
    def _update_bg(self, *args):
        if hasattr(self, 'rect'):
            self.rect.pos = self.pos
            self.rect.size = self.size


# ============================================================================
# DATA FETCHER (REALTIME with yfinance)
# ============================================================================
class DataFetcher:
    IHSG_STOCKS = ['BBCA', 'BBRI', 'BBNI', 'BMRI', 'ASII', 'TLKM', 'UNVR', 'ADRO', 'CPIN', 'INCO']
    
    @staticmethod
    def fetch_realtime_price(symbol):
        try:
            import yfinance as yf
            ticker = yf.Ticker(f"{symbol}.JK")
            data = ticker.history(period='1d', interval='5m')
            if not data.empty:
                latest = data.iloc[-1]
                prev = ticker.history(period='2d')
                prev_close = prev.iloc[-2]['Close'] if len(prev) >= 2 else latest['Close']
                return {
                    'symbol': symbol,
                    'price': latest['Close'],
                    'change_pct': ((latest['Close'] - prev_close) / prev_close) * 100,
                    'volume': latest['Volume'],
                    'high': latest['High'],
                    'low': latest['Low']
                }
        except Exception as e:
            print(f"Error {symbol}: {e}")
        return None
    
    @staticmethod
    def fetch_all_prices(limit=12):
        results = []
        for symbol in DataFetcher.IHSG_STOCKS[:limit]:
            data = DataFetcher.fetch_realtime_price(symbol)
            if data:
                results.append(data)
            import time
            time.sleep(0.05)
        return results


# ============================================================================
# TAB 1: HOME / DASHBOARD
# ============================================================================
class HomeTab(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(orientation='vertical', **kwargs)
        self.padding = [rdp(12), rdp(8), rdp(12), rdp(8)]
        self.spacing = rdp(12)
        
        # Header
        header = BoxLayout(size_hint_y=None, height=ThemeConfig.HEADER_HEIGHT)
        header.add_widget(Label(
            text='JURNAL SAHAM IHSG',
            font_size=rsp(18),
            bold=True,
            color=ThemeConfig.ACCENT
        ))
        self.add_widget(header)
        
        # IHSG Summary Card
        summary = StyledCard(bg_color=ThemeConfig.SURFACE_BRIGHT)
        summary.height = rdp(100)
        summary.add_widget(Label(
            text='IHSG MARKET SUMMARY',
            font_size=rsp(10),
            bold=True,
            color=ThemeConfig.ACCENT_LIGHT,
            size_hint_y=None,
            height=rdp(20)
        ))
        
        row = BoxLayout(orientation='horizontal', size_hint_y=None, height=rdp(50))
        self.ihsg_value = Label(
            text='Loading...',
            font_size=rsp(28),
            bold=True,
            color=ThemeConfig.TEXT_BRIGHT,
            size_hint_x=0.6,
            halign='left'
        )
        self.ihsg_change = Label(
            text='',
            font_size=rsp(16),
            bold=True,
            size_hint_x=0.4,
            halign='right'
        )
        row.add_widget(self.ihsg_value)
        row.add_widget(self.ihsg_change)
        summary.add_widget(row)
        self.add_widget(summary)
        
        # Quick Actions
        actions = BoxLayout(size_hint_y=None, height=ThemeConfig.BUTTON_HEIGHT, spacing=rdp(10))
        actions.add_widget(ModernButton(text='📊 SCREENING', bg_color=ThemeConfig.SURFACE))
        actions.add_widget(ModernButton(text='🤖 TANYA AI', bg_color=ThemeConfig.SURFACE))
        self.add_widget(actions)
        
        # Top Movers Section
        self.add_widget(Label(
            text='🔥 TOP MOVERS',
            font_size=rsp(14),
            bold=True,
            size_hint_y=None,
            height=rdp(30)
        ))
        
        scroll = ScrollView(bar_width=0)
        self.movers_list = GridLayout(cols=1, spacing=rdp(8), size_hint_y=None)
        self.movers_list.bind(minimum_height=self.movers_list.setter('height'))
        scroll.add_widget(self.movers_list)
        self.add_widget(scroll)
        
        Clock.schedule_once(lambda dt: self.load_data(), 0.5)
    
    def load_data(self):
        def worker():
            data = DataFetcher.fetch_all_prices(limit=10)
            Clock.schedule_once(lambda dt: self.update_ui(data), 0)
        threading.Thread(target=worker, daemon=True).start()
    
    def update_ui(self, data):
        self.movers_list.clear_widgets()
        if not data:
            self.movers_list.add_widget(Label(text='No data', color=ThemeConfig.RED))
            return
        
        if data:
            avg_change = sum(s['change_pct'] for s in data[:5]) / 5
            self.ihsg_value.text = '7,321'
            self.ihsg_change.text = f'{avg_change:+.2f}%'
            self.ihsg_change.color = ThemeConfig.GREEN if avg_change >= 0 else ThemeConfig.RED
        
        sorted_data = sorted(data, key=lambda x: abs(x['change_pct']), reverse=True)[:5]
        for stock in sorted_data:
            self.movers_list.add_widget(StockRow(
                stock['symbol'], stock['price'], stock['change_pct']
            ))


# ============================================================================
# TAB 2: WATCHLIST
# ============================================================================
class WatchlistTab(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(orientation='vertical', **kwargs)
        self.padding = [rdp(12), rdp(8)]
        self.spacing = rdp(12)
        
        header = BoxLayout(orientation='horizontal', size_hint_y=None, height=rdp(45), spacing=rdp(8))
        header.add_widget(Label(
            text='WATCHLIST',
            font_size=rsp(16),
            bold=True,
            color=ThemeConfig.TEXT_BRIGHT,
            size_hint_x=0.7,
            halign='left'
        ))
        refresh_btn = ModernButton(text='🔄', bg_color=ThemeConfig.SURFACE, size_hint_x=0.3)
        refresh_btn.bind(on_release=lambda x: self.refresh_data())
        header.add_widget(refresh_btn)
        self.add_widget(header)
        
        scroll = ScrollView(bar_width=0)
        self.list = GridLayout(cols=1, spacing=rdp(8), size_hint_y=None)
        self.list.bind(minimum_height=self.list.setter('height'))
        scroll.add_widget(self.list)
        self.add_widget(scroll)
        
        self.watchlist_symbols = ['BBCA', 'BBRI', 'ASII', 'TLKM', 'UNVR']
        Clock.schedule_once(lambda dt: self.refresh_data(), 0.5)
    
    def refresh_data(self):
        self.list.clear_widgets()
        loading = Label(text='Loading...', color=ThemeConfig.TEXT_DIM, size_hint_y=None, height=rdp(50))
        self.list.add_widget(loading)
        
        def worker():
            data = []
            for sym in self.watchlist_symbols:
                d = DataFetcher.fetch_realtime_price(sym)
                if d:
                    data.append(d)
                import time
                time.sleep(0.05)
            Clock.schedule_once(lambda dt: self.update_list(data), 0)
        threading.Thread(target=worker, daemon=True).start()
    
    def update_list(self, data):
        self.list.clear_widgets()
        if not data:
            self.list.add_widget(Label(text='Failed to load', color=ThemeConfig.RED))
            return
        
        for stock in data:
            self.list.add_widget(StockRow(stock['symbol'], stock['price'], stock['change_pct']))


# ============================================================================
# TAB 3: JURNAL / PORTFOLIO
# ============================================================================
class JurnalTab(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(orientation='vertical', **kwargs)
        self.padding = [rdp(12), rdp(8)]
        self.spacing = rdp(12)
        
        self.add_widget(Label(
            text='PORTFOLIO',
            font_size=rsp(16),
            bold=True,
            color=ThemeConfig.TEXT_BRIGHT,
            size_hint_y=None,
            height=rdp(40),
            halign='left'
        ))
        
        # Summary Card
        summary = StyledCard(bg_color=ThemeConfig.SURFACE_BRIGHT)
        summary.height = rdp(90)
        summary.add_widget(Label(
            text='TOTAL VALUE',
            font_size=rsp(10),
            color=ThemeConfig.TEXT_DIM,
            size_hint_y=None,
            height=rdp(20)
        ))
        self.total_value = Label(
            text='Rp 0',
            font_size=rsp(24),
            bold=True,
            color=ThemeConfig.ACCENT,
            size_hint_y=None,
            height=rdp(40)
        )
        summary.add_widget(self.total_value)
        self.add_widget(summary)
        
        # Add Transaction Form
        form = StyledCard()
        form.height = rdp(250)
        form.add_widget(Label(text='➕ ADD TRANSACTION', font_size=rsp(12), bold=True))
        
        self.symbol_input = TextInput(
            hint_text='Symbol (BBCA)',
            size_hint_y=None,
            height=rdp(45),
            background_color=ThemeConfig.SURFACE_BRIGHT,
            foreground_color=ThemeConfig.TEXT_BRIGHT,
            font_size=rsp(14)
        )
        form.add_widget(self.symbol_input)
        
        self.qty_input = TextInput(
            hint_text='Quantity (lot)',
            size_hint_y=None,
            height=rdp(45),
            background_color=ThemeConfig.SURFACE_BRIGHT,
            foreground_color=ThemeConfig.TEXT_BRIGHT,
            font_size=rsp(14),
            input_filter='int'
        )
        form.add_widget(self.qty_input)
        
        add_btn = ModernButton(text='ADD TO PORTFOLIO')
        add_btn.bind(on_release=self.add_transaction)
        form.add_widget(add_btn)
        self.add_widget(form)
        
        # History
        self.add_widget(Label(
            text='📋 RECENT',
            font_size=rsp(12),
            bold=True,
            size_hint_y=None,
            height=rdp(30)
        ))
        self.history_label = Label(
            text='No transactions yet',
            color=ThemeConfig.TEXT_DIM,
            size_hint_y=None,
            height=rdp(100),
            halign='left',
            valign='top'
        )
        self.history_label.bind(size=lambda s, v: setattr(s, 'text_size', (s.width, None)))
        self.add_widget(self.history_label)
        
        self.transactions = []
    
    def add_transaction(self, *args):
        symbol = self.symbol_input.text.strip().upper()
        qty = self.qty_input.text.strip()
        if not symbol or not qty:
            return
        try:
            qty_int = int(qty)
            total = qty_int * 100 * 10000
            self.total_value.text = f"Rp {total:,}"
            self.transactions.insert(0, f"• BUY {symbol} {qty_int} lot")
            self.history_label.text = '\n'.join(self.transactions[:5])
            self.symbol_input.text = ''
            self.qty_input.text = ''
        except:
            pass


# ============================================================================
# TAB 4: AI CHAT (DEEPSEEK)
# ============================================================================
class AIChatTab(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(orientation='vertical', **kwargs)
        self.padding = [rdp(12), rdp(8)]
        self.spacing = rdp(12)
        
        header = BoxLayout(size_hint_y=None, height=rdp(45))
        header.add_widget(Label(
            text='🤖 TANYA AI (DeepSeek)',
            font_size=rsp(16),
            bold=True,
            color=ThemeConfig.ACCENT,
            halign='left'
        ))
        self.add_widget(header)
        
        # Chat History
        self.chat_history = ScrollView(bar_width=0)
        self.chat_list = GridLayout(cols=1, spacing=rdp(10), size_hint_y=None)
        self.chat_list.bind(minimum_height=self.chat_list.setter('height'))
        self.chat_history.add_widget(self.chat_list)
        self.add_widget(self.chat_history)
        
        # Welcome
        self.add_message("Halo! Saya asisten AI saham IHSG. Tanyakan analisis saham, prediksi, atau rekomendasi trading.\n\nContoh:\n• Analisis BBCA\n• Prospek sektor perbankan\n• Prediksi IHSG hari ini", is_user=False)
        
        # Input
        input_box = BoxLayout(size_hint_y=None, height=rdp(55), spacing=rdp(8))
        self.text_input = TextInput(
            hint_text='Tanyakan tentang saham...',
            multiline=False,
            background_color=ThemeConfig.SURFACE_BRIGHT,
            foreground_color=ThemeConfig.TEXT_BRIGHT,
            font_size=rsp(14),
            padding=[rdp(12), rdp(12)]
        )
        self.text_input.bind(on_text_validate=self.on_send)
        send_btn = ModernButton(text='KIRIM', size_hint_x=None, width=rdp(80))
        send_btn.bind(on_release=self.on_send)
        input_box.add_widget(self.text_input)
        input_box.add_widget(send_btn)
        self.add_widget(input_box)
        
        self.loading_label = Label(text='', size_hint_y=None, height=rdp(0))
        self.add_widget(self.loading_label)
    
    def add_message(self, text, is_user=False):
        bubble = ChatBubble(text=text, is_user=is_user)
        self.chat_list.add_widget(bubble)
        Clock.schedule_once(lambda dt: setattr(self.chat_history, 'scroll_y', 0), 0.1)
    
    def show_loading(self, show):
        self.loading_label.text = 'DeepSeek sedang berpikir... 🤔' if show else ''
        self.loading_label.height = rdp(30) if show else 0
    
    def on_send(self, *args):
        query = self.text_input.text.strip()
        if not query:
            return
        self.add_message(query, is_user=True)
        self.text_input.text = ''
        self.show_loading(True)
        threading.Thread(target=self.call_deepseek, args=(query,), daemon=True).start()
    
    def call_deepseek(self, query):
        if DeepSeekConfig.API_KEY == 'YOUR_DEEPSEEK_API_KEY_HERE':
            response = self.offline_response(query)
            Clock.schedule_once(lambda dt: self.add_message(response, is_user=False), 0)
            Clock.schedule_once(lambda dt: self.show_loading(False), 0)
            return
        
        try:
            headers = {"Authorization": f"Bearer {DeepSeekConfig.API_KEY}", "Content-Type": "application/json"}
            messages = [{"role": "system", "content": DeepSeekConfig.STOCK_CONTEXT}, {"role": "user", "content": query}]
            payload = {"model": DeepSeekConfig.MODEL, "messages": messages, "temperature": 0.7, "max_tokens": 800}
            response = requests.post(DeepSeekConfig.API_URL, headers=headers, json=payload, timeout=30)
            if response.status_code == 200:
                ai_response = response.json()['choices'][0]['message']['content']
            else:
                ai_response = f"⚠️ API Error\n\n{self.offline_response(query)}"
        except Exception as e:
            ai_response = f"❌ Error: {str(e)[:100]}\n\n{self.offline_response(query)}"
        
        Clock.schedule_once(lambda dt: self.add_message(ai_response, is_user=False), 0)
        Clock.schedule_once(lambda dt: self.show_loading(False), 0)
    
    def offline_response(self, query):
        q = query.lower()
        if 'bbc' in q:
            return "📊 **BBCA**\n• Support: 9.500, Resistance: 10.500\n• PER: 18x, PBV: 3.2x\n• Rekomendasi: HOLD"
        elif 'bbri' in q:
            return "📊 **BBRI**\n• Support: 4.000, Resistance: 4.800\n• PER: 7.5x, Div Yield: 8%\n• Rekomendasi: BUY"
        elif 'ihsg' in q:
            return "📈 **IHSG**\n• Support: 6.800, Resistance: 7.200\n• Tren: Sideways\n• Strategi: Akumulasi bertahap"
        else:
            return f"🤖 Analisis untuk '{query}': Gunakan API Key DeepSeek untuk jawaban realtime.\n\nDapatkan di platform.deepseek.com"


# ============================================================================
# MAIN APP
# ============================================================================
class JurnalSahamApp(App):
    def build(self):
        Window.clearcolor = ThemeConfig.BG_MAIN
        
        if _kivy_platform not in ("android", "ios"):
            Window.size = (400, 750)
        
        root = BoxLayout(orientation='vertical')
        
        self.content = BoxLayout()
        self.tabs = [HomeTab(), WatchlistTab(), JurnalTab(), AIChatTab()]
        self.current_tab = 0
        self.content.add_widget(self.tabs[0])
        
        # Bottom Navigation
        nav = BoxLayout(
            size_hint_y=None,
            height=ThemeConfig.NAV_HEIGHT,
            padding=[rdp(8), rdp(4)],
            spacing=rdp(4)
        )
        with nav.canvas.before:
            Color(*ThemeConfig.SURFACE)
            Rectangle(pos=nav.pos, size=nav.size)
        
        nav_items = [('🏠', 'HOME'), ('⭐', 'WATCH'), ('📊', 'JURNAL'), ('🤖', 'AI')]
        
        self.nav_buttons = []
        for i, (icon, text) in enumerate(nav_items):
            btn = Button(
                text=f'{icon}\n{text}',
                background_color=[0,0,0,0],
                color=ThemeConfig.TEXT_DIM,
                font_size=rsp(11),
                bold=True,
                size_hint_x=1
            )
            btn.bind(on_release=lambda x, idx=i: self.switch_tab(idx))
            nav.add_widget(btn)
            self.nav_buttons.append(btn)
        
        self.update_nav_colors()
        
        root.add_widget(self.content)
        root.add_widget(nav)
        return root
    
    def switch_tab(self, idx):
        self.current_tab = idx
        self.content.clear_widgets()
        self.content.add_widget(self.tabs[idx])
        self.update_nav_colors()
    
    def update_nav_colors(self):
        for i, btn in enumerate(self.nav_buttons):
            btn.color = ThemeConfig.ACCENT if i == self.current_tab else ThemeConfig.TEXT_DIM


# ============================================================================
# BACKWARDS COMPATIBILITY (for main.py)
# ============================================================================
MainStockbitApp = JurnalSahamApp


# ============================================================================
# ENTRY POINT
# ============================================================================
if __name__ == '__main__':
    _orig_bind = EventDispatcher.bind
    def _safe_bind(self, *args, **kwargs):
        try:
            return _orig_bind(self, *args, **kwargs)
        except AssertionError:
            filtered = {k: v for k, v in kwargs.items() if v is not None}
            return _orig_bind(self, **filtered) if filtered else None
    
    try:
        EventDispatcher.bind = _safe_bind
    except:
        pass
    
    try:
        JurnalSahamApp().run()
    except Exception as e:
        traceback.print_exc()
        try:
            with open('/sdcard/error_log.txt', 'w') as f:
                f.write(traceback.format_exc())
        except:
            pass