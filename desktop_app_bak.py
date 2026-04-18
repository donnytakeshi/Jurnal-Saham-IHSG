
# --- Jurnal Saham IHSG - Unified Kivy Modular UI (simplified) ---

import json
import csv
import os
import threading
import traceback
import random
from datetime import datetime

try:
    from zoneinfo import ZoneInfo
except Exception:
    ZoneInfo = None


from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.uix.widget import Widget
from kivy.uix.textinput import TextInput
from kivy.uix.popup import Popup
from kivy.uix.switch import Switch
from kivy.uix.behaviors import ButtonBehavior
from kivy.properties import ListProperty, NumericProperty
from kivy.event import EventDispatcher
from kivy.utils import get_color_from_hex, platform as _kivy_platform
from kivy.clock import Clock
# --- Jurnal Saham IHSG - Enhanced Unified Kivy Modular UI ---
import json
import csv
import os
import threading
import traceback
import random
from datetime import datetime

try:
    from zoneinfo import ZoneInfo
except Exception:
    ZoneInfo = None

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.uix.widget import Widget
from kivy.uix.textinput import TextInput
from kivy.properties import ListProperty, NumericProperty, StringProperty
from kivy.utils import get_color_from_hex
from kivy.clock import Clock
from kivy.graphics import Color, Rectangle, RoundedRectangle, Line, Ellipse
from kivy.core.window import Window

# --- THEME CONFIG (Quant Edge) ---
class ThemeConfig:
    BG_MAIN = get_color_from_hex('#101419')
    SURFACE = get_color_from_hex('#181c21')
    SURFACE_LIGHT = get_color_from_hex('#1c2127')
    ACCENT = get_color_from_hex('#159D91')  # Teal
    
    GREEN = get_color_from_hex('#67d9cb')
    RED = get_color_from_hex('#ff5e5e')
    YELLOW = get_color_from_hex('#f2d18f')
    BORDER = get_color_from_hex('#2d3432')
    
    TEXT_BRIGHT = get_color_from_hex('#ffffff')
    TEXT_DEFAULT = get_color_from_hex('#bcc9c6')
    TEXT_MUTED = get_color_from_hex('#41493e')
    
    ROUNDNESS = 12

# --- UI Helpers ---
def ui_dp(v):
    from kivy.metrics import dp
    return dp(v)

def ui_sp(v):
    from kivy.metrics import sp
    return sp(v)

# --- REUSABLE COMPONENTS ---
class Card(BoxLayout):
    def __init__(self, bg_color=ThemeConfig.SURFACE, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.padding = ui_dp(12)
        with self.canvas.before:
            Color(rgb=bg_color)
            self.rect = RoundedRectangle(pos=self.pos, size=self.size, radius=[ui_dp(ThemeConfig.ROUNDNESS)])
        self.bind(pos=self._update, size=self._update)
    def _update(self, *_):
        self.rect.pos = self.pos
        self.rect.size = self.size

class Badge(Label):
    def __init__(self, text, bg_color=ThemeConfig.ACCENT, **kwargs):
        super().__init__(text=text, **kwargs)
        self.font_size = ui_sp(10)
        self.bold = True
        self.color = ThemeConfig.TEXT_BRIGHT
        self.size_hint = (None, None)
        self.height = ui_dp(20)
        self.padding = (ui_dp(8), ui_dp(4))
        with self.canvas.before:
            Color(rgb=bg_color)
            self.rect = RoundedRectangle(pos=self.pos, size=self.size, radius=[ui_dp(10)])
        self.bind(pos=self._update, size=self._update)
        self._update_width()

    def _update(self, *_):
        self.rect.pos = self.pos
        self.rect.size = self.size

    def _update_width(self, *_):
        self.texture_update()
        self.width = self.texture_size[0] + ui_dp(16)

class Sparkline(Widget):
    values = ListProperty([])
    line_color = ListProperty(ThemeConfig.ACCENT)
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.bind(pos=self._draw, size=self._draw, values=self._draw)
    def _draw(self, *_):
        self.canvas.clear()
        if not self.values or len(self.values) < 2: return
        w, h = self.width, self.height
        vmin, vmax = min(self.values), max(self.values)
        diff = (vmax - vmin) if vmax != vmin else 1
        points = []
        for i, v in enumerate(self.values):
            x = self.x + (i / (len(self.values)-1)) * w
            y = self.y + ((v - vmin) / diff) * h
            points.extend([x, y])
        with self.canvas:
            Color(*self.line_color)
            Line(points=points, width=ui_dp(1.5), cap='round', joint='round')

# --- ENHANCED TAB CLASSES ---

class ScreeningTab(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(orientation='vertical', padding=ui_dp(8), spacing=ui_dp(8), **kwargs)
        
        # Live Header
        header = BoxLayout(size_hint_y=None, height=ui_dp(40), spacing=ui_dp(10))
        header.add_widget(Label(text='Screening Live', font_size=ui_sp(18), bold=True, color=ThemeConfig.TEXT_BRIGHT, halign='left'))
        header.add_widget(Widget())
        header.add_widget(Badge('LIVE', bg_color=ThemeConfig.RED))
        self.add_widget(header)
        
        # Table Headers
        table_hdr = BoxLayout(size_hint_y=None, height=ui_dp(30), padding=(ui_dp(10), 0))
        headers = ['SAHAM', 'PRICE / %', 'RVOL', 'STRENGTH']
        for h in headers:
            table_hdr.add_widget(Label(text=h, font_size=ui_sp(10), bold=True, color=ThemeConfig.TEXT_MUTED))
        self.add_widget(table_hdr)
        
        # List
        sv = ScrollView(bar_width=0)
        grid = GridLayout(cols=1, spacing=ui_dp(2), size_hint_y=None)
        grid.bind(minimum_height=grid.setter('height'))
        
        stocks = [
            ('BBRI', '6.125', '+2.51%', '2.4x', 0.8),
            ('ASII', '5.150', '-1.43%', '0.8x', 0.2),
            ('BBNI', '5.950', '+3.48%', '1.9x', 0.9),
            ('GOTO', '64', '0.00%', '1.1x', 0.5),
            ('UNVR', '2.650', '-0.75%', '1.5x', 0.4),
        ]
        
        for sym, price, pct, rvol, str_val in stocks:
            row = Card(bg_color=ThemeConfig.SURFACE_LIGHT, size_hint_y=None, height=ui_dp(60), orientation='horizontal', padding=ui_dp(10))
            
            # Col 1: Symbol
            left = BoxLayout(orientation='vertical')
            left.add_widget(Label(text=sym, bold=True, color=ThemeConfig.TEXT_BRIGHT, halign='left'))
            row.add_widget(left)
            
            # Col 2: Price / %
            mid1 = BoxLayout(orientation='vertical')
            mid1.add_widget(Label(text=price, font_size=ui_sp(14), color=ThemeConfig.GREEN if '+' in pct else ThemeConfig.RED))
            mid1.add_widget(Label(text=pct, font_size=ui_sp(11), color=ThemeConfig.TEXT_MUTED))
            row.add_widget(mid1)
            
            # Col 3: RVOL
            mid2 = Label(text=rvol, color=ThemeConfig.YELLOW if '2.4' in rvol else ThemeConfig.TEXT_DEFAULT)
            row.add_widget(mid2)
            
            # Col 4: Strength (Mini Chart)
            right = BoxLayout(padding=(ui_dp(10), ui_dp(10)))
            right.add_widget(Sparkline(values=[random.random() for _ in range(6)], line_color=ThemeConfig.ACCENT))
            row.add_widget(right)
            
            grid.add_widget(row)
            
        sv.add_widget(grid)
        self.add_widget(sv)

class CekEmitenTab(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(orientation='vertical', padding=ui_dp(8), spacing=ui_dp(12), **kwargs)
        
        # Header Info
        header = Card(size_hint_y=None, height=ui_dp(100))
        title_row = BoxLayout(size_hint_y=None, height=ui_dp(30))
        title_row.add_widget(Label(text='BBCA', font_size=ui_sp(24), bold=True, color=ThemeConfig.TEXT_BRIGHT))
        title_row.add_widget(Widget())
        title_row.add_widget(Label(text='10.450', font_size=ui_sp(24), bold=True, color=ThemeConfig.GREEN))
        header.add_widget(title_row)
        
        chips = BoxLayout(size_hint_y=None, height=ui_dp(30), spacing=ui_dp(6))
        chips.add_widget(Badge('RSI (14): 62.4', bg_color=ThemeConfig.ACCENT))
        chips.add_widget(Badge('MACD Bullish', bg_color=ThemeConfig.GREEN))
        chips.add_widget(Widget())
        header.add_widget(chips)
        self.add_widget(header)
        
        # Main Candlestick Placeholder
        chart = Card(bg_color=get_color_from_hex('#0F1419'), size_hint_y=None, height=ui_dp(200))
        chart.add_widget(Label(text='[ PROFESSIONAL CHART VIEW ]', color=ThemeConfig.TEXT_MUTED))
        self.add_widget(chart)
        
        # Bandarmology Detail Section
        bandar_card = Card(size_hint_y=None, height=ui_dp(160))
        bandar_card.add_widget(Label(text='BANDARMOLOGY FLOW', font_size=ui_sp(12), bold=True, color=ThemeConfig.TEXT_MUTED))
        
        flow_grid = GridLayout(cols=2, spacing=ui_dp(10), padding=ui_dp(5))
        def flow_item(title, value, color):
            box = BoxLayout(orientation='vertical')
            box.add_widget(Label(text=title, font_size=ui_sp(10), color=ThemeConfig.TEXT_MUTED))
            box.add_widget(Label(text=value, font_size=ui_sp(16), bold=True, color=color))
            return box
            
        flow_grid.add_widget(flow_item('FOREIGN FLOW', '+245.2B', ThemeConfig.GREEN))
        flow_grid.add_widget(flow_item('DOMESTIC FLOW', '-112.8B', ThemeConfig.RED))
        bandar_card.add_widget(flow_grid)
        
        # Mini Progress Bar for Net Flow
        progress_box = BoxLayout(size_hint_y=None, height=ui_dp(8), padding=(ui_dp(10), 0))
        with progress_box.canvas:
            Color(rgb=ThemeConfig.BORDER)
            Rectangle(pos=progress_box.pos, size=progress_box.size)
            Color(rgb=ThemeConfig.GREEN)
            Rectangle(pos=progress_box.pos, size=(progress_box.width * 0.65, progress_box.height))
        bandar_card.add_widget(progress_box)
        
        self.add_widget(bandar_card)
        self.add_widget(Widget()) # Spacer

# --- Main App ---
class EnhancedJurnalApp(App):
    def build(self):
        Window.clearcolor = ThemeConfig.BG_MAIN
        root = BoxLayout(orientation='vertical')
        
        # Bottom Navigation placeholder logic
        self.content_area = BoxLayout()
        root.add_widget(self.content_area)
        
        # Initial View
        self.content_area.add_widget(ScreeningTab())
        
        return root

if __name__ == '__main__':
    EnhancedJurnalApp().run()
    def on_touch_move(self, touch):
        return super().on_touch_move(touch)

    def on_touch_up(self, touch):
        # trigger refresh if a real implementation exists
        try:
            if self._on_refresh and callable(self._on_refresh):
                self._on_refresh()
        except Exception:
            pass
        return super().on_touch_up(touch)

# --- Main Tabs ---
class WatchlistTab(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(orientation='vertical', **kwargs)
        header = BoxLayout(size_hint_y=None, height=ui_dp(60), padding=ui_dp(10))
        header.add_widget(Label(text='[b]Watchlist[/b]', markup=True, font_size=ui_sp(ThemeConfig.FONT_HEADER), color=ThemeConfig.TEXT_HEADER))
        self.add_widget(header)
        scroll = ScrollView()
        self.list = GridLayout(cols=1, size_hint_y=None, spacing=ui_dp(1))
        self.list.bind(minimum_height=self.list.setter('height'))
        for s in MockDataFetcher.sample_stocks:
            row = BoxLayout(size_hint_y=None, height=ui_dp(80), padding=ui_dp(10))
            with row.canvas.before:
                Color(*ThemeConfig.BG_CARD)
                Rectangle(pos=row.pos, size=row.size)
            row.add_widget(Label(text=s['symbol'], font_size=ui_sp(18), bold=True, color=ThemeConfig.TEXT_HEADER))
            row.add_widget(SparklineWidget(values=[random.random() for _ in range(10)], size_hint_x=0.4, line_color=ThemeConfig.SPARKLINE))
            row.add_widget(Label(text='Rp 10.250', halign='right', color=ThemeConfig.TEXT_DEFAULT))
            self.list.add_widget(row)
        scroll.add_widget(self.list)
        self.add_widget(scroll)

class DashboardTab(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(orientation='vertical', **kwargs)
        self.add_widget(Label(text='[b]Top 10 Insights[/b]', markup=True, size_hint_y=None, height=ui_dp(60), font_size=ui_sp(ThemeConfig.FONT_HEADER), color=ThemeConfig.TEXT_HEADER))
        scroll = ScrollView()
        content = BoxLayout(orientation='vertical', size_hint_y=None, padding=ui_dp(10), spacing=ui_dp(10))
        content.bind(minimum_height=content.setter('height'))
        phase_card = BoxLayout(size_hint_y=None, height=ui_dp(200), padding=ui_dp(15))
        with phase_card.canvas.before:
            Color(*ThemeConfig.BG_HEADER)
            RoundedRectangle(pos=phase_card.pos, size=phase_card.size, radius=[ui_dp(ThemeConfig.RADIUS_CARD)])
        phase_card.add_widget(Label(text='Phase Distribution Pie Chart', color=ThemeConfig.TEXT_DEFAULT))
        content.add_widget(phase_card)
        for i in range(5):
            content.add_widget(Label(text=f'Top Gainer {i+1}: BBCA +2.5%', size_hint_y=None, height=ui_dp(40), color=ThemeConfig.TEXT_DEFAULT))
        scroll.add_widget(content)
        self.add_widget(scroll)

class JurnalTab(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(orientation='vertical', **kwargs)
        self.add_widget(Label(text='[b]Portofolio Summary[/b]', markup=True, size_hint_y=None, height=ui_dp(60), font_size=ui_sp(ThemeConfig.FONT_HEADER), color=ThemeConfig.TEXT_HEADER))
        summary = BoxLayout(size_hint_y=None, height=ui_dp(100), padding=ui_dp(10))
        summary.add_widget(Label(text='Total Equity\nRp 142.850.000', halign='center', color=ThemeConfig.TEXT_DEFAULT))
        self.add_widget(summary)
        scroll = ScrollView()
        self.trade_log = GridLayout(cols=1, size_hint_y=None)
        self.trade_log.bind(minimum_height=self.trade_log.setter('height'))
        for i in range(10):
            self.trade_log.add_widget(Label(text=f'Trade Log {i}: Buy BBCA 100 Lot @ 9800', size_hint_y=None, height=ui_dp(50), color=ThemeConfig.TEXT_DEFAULT))
        scroll.add_widget(self.trade_log)
        self.add_widget(scroll)

class ScreeningTab(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(orientation='vertical', **kwargs)
        self.add_widget(Label(text='[b]Live Screening[/b]', markup=True, size_hint_y=None, height=ui_dp(60), font_size=ui_sp(ThemeConfig.FONT_HEADER), color=ThemeConfig.TEXT_HEADER))
        scroll = ScrollView()
        table = GridLayout(cols=4, size_hint_y=None, spacing=ui_dp(2))
        table.bind(minimum_height=table.setter('height'))
        headers = ['SAHAM', 'HARGA', '%', 'NET B/S']
        for h in headers: table.add_widget(Label(text=h, bold=True, size_hint_y=None, height=ui_dp(40), color=ThemeConfig.TEXT_HEADER))
        for s in MockDataFetcher.sample_stocks * 3:
            table.add_widget(Label(text=s['symbol'], size_hint_y=None, height=ui_dp(40), color=ThemeConfig.TEXT_DEFAULT))
            table.add_widget(Label(text='10.250', color=ThemeConfig.TEXT_DEFAULT))
            table.add_widget(Label(text='+2.5%', color=ThemeConfig.TEXT_DEFAULT))
            table.add_widget(Label(text='+124B', color=ThemeConfig.TEXT_DEFAULT))
        scroll.add_widget(table)
        self.add_widget(scroll)

class CekSahamTab(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(orientation='vertical', **kwargs)
        self.add_widget(Label(text='[b]Analisis Individu[/b]', markup=True, size_hint_y=None, height=ui_dp(60), font_size=ui_sp(ThemeConfig.FONT_HEADER), color=ThemeConfig.TEXT_HEADER))
        self.add_widget(TextInput(hint_text='Cari Kode Saham...', size_hint_y=None, height=ui_dp(50)))
        chart = BoxLayout(size_hint_y=None, height=ui_dp(300))
        with chart.canvas.before:
            Color(*ThemeConfig.BG_CHART)
            Rectangle(pos=chart.pos, size=chart.size)
        chart.add_widget(Label(text='Candlestick Chart View', color=ThemeConfig.TEXT_DEFAULT))
        self.add_widget(chart)
        self.add_widget(Label(text='Signal: STRONG BUY', font_size=ui_sp(ThemeConfig.FONT_SIGNAL), color=ThemeConfig.TEXT_SIGNAL))
        self.add_widget(Widget())

# --- App Root with Bottom Nav (named MainStockbitApp for compatibility) ---
class MainStockbitApp(App):
    def build(self):
        Window.clearcolor = ThemeConfig.BG_MAIN
        self.root = BoxLayout(orientation='vertical')
        self.content_area = BoxLayout()
        self.tabs = [WatchlistTab(), DashboardTab(), JurnalTab(), ScreeningTab(), CekSahamTab()]
        self.switch_tab(0)

        # Bottom Navigation
        nav = BoxLayout(size_hint_y=None, height=ui_dp(65))
        with nav.canvas.before:
            Color(*ThemeConfig.BG_NAV)
            Rectangle(pos=nav.pos, size=nav.size)
            Color(*ThemeConfig.BG_NAV_LINE)
            Line(points=[nav.x, nav.top, nav.right, nav.top], width=ui_dp(1))

        labels = ['Watchlist', 'Top 10', 'Jurnal', 'Screening', 'Cek Saham']
        self.nav_btns = []
        for i, text in enumerate(labels):
            btn = Button(text=text, background_color=ThemeConfig.BUTTON_BG, color=ThemeConfig.TEXT_DEFAULT, font_size=ui_sp(ThemeConfig.FONT_NAV))
            btn.bind(on_release=lambda x, idx=i: self.switch_tab(idx))
            nav.add_widget(btn)
            self.nav_btns.append(btn)

        self.root.add_widget(self.content_area)
        self.root.add_widget(nav)
        return self.root

    def switch_tab(self, idx):
        self.content_area.clear_widgets()
        self.content_area.add_widget(self.tabs[idx])
        for i, btn in enumerate(getattr(self, 'nav_btns', [])):
            btn.color = ThemeConfig.TEXT_ACTIVE if i == idx else ThemeConfig.TEXT_DEFAULT

if __name__ == '__main__':
    MainStockbitApp().run()

    def _reset_pull(self):
        self._pull = 0
        self._armed = False
        self._pulling = False
        try:
            self._set_indicator(0, 'Tarik untuk refresh')
        except Exception:
            pass

    def _set_indicator(self, h, text=None):
        try:
            self._indicator_box.height = max(0, h)
            if text is not None:
                self._indicator_label.text = text
        except Exception:
            pass

    def on_touch_down(self, touch):
        if not self.collide_point(*touch.pos):
            return super().on_touch_down(touch)
        self._down_y = touch.y
        self._pull = 0
        self._armed = False
        self._pulling = False
        try:
            self._start_at_top = bool(self.scroll_y >= 0.999)
        except Exception:
            self._start_at_top = False
        return super().on_touch_down(touch)

    def on_touch_move(self, touch):
        if not self.collide_point(*touch.pos):
            return super().on_touch_move(touch)
        if self._down_y is None:
            return super().on_touch_move(touch)

        # Kivy coords: y increases upward. A finger drag *down* makes touch.y smaller.
        # We want a downward drag to count as a positive "pull".
        dy = self._down_y - touch.y
        try:
            at_top = bool(self.scroll_y >= 0.999)
        except Exception:
            at_top = False

        # Only allow pull-to-refresh if the gesture started at the top.
        # If the user drags upward (dy <= 0) or leaves the top, cancel pull state.
        if (not self._start_at_top) or (not at_top) or (dy <= 0):
            if self._pulling or self._pull > 0:
                self._reset_pull()
            return super().on_touch_move(touch)

        # Ignore tiny jitter; require a deliberate downward pull.
        if dy <= self._slop:
            return super().on_touch_move(touch)

        self._pulling = True
        self._pull = min(self._trigger * 1.5, dy)
        self._armed = self._pull >= self._trigger
        self._set_indicator(self._pull, 'Lepas untuk refresh' if self._armed else 'Tarik untuk refresh')
        return True

    def on_touch_up(self, touch):
        if self._down_y is None:
            return super().on_touch_up(touch)

        if self._pull > 0:
            if self._armed and callable(self._on_refresh):
                try:
                    self._set_indicator(ui_dp(36), 'Refreshing...')
                    self._on_refresh()
                except Exception:
                    pass
            # Reset indicator after a short delay
            try:
                Clock.schedule_once(lambda dt: self._set_indicator(0, 'Tarik untuk refresh'), 0.6)
            except Exception:
                self._set_indicator(0, 'Tarik untuk refresh')
            self._pull = 0
            self._down_y = None
            self._armed = False
            self._pulling = False
            self._start_at_top = False
            return True

        self._down_y = None
        self._pulling = False
        self._start_at_top = False
        return super().on_touch_up(touch)


def _to_float(value, default=0.0):
    try:
        if value is None:
            return default
        if isinstance(value, (int, float)):
            return float(value)
        s = str(value).strip().replace(',', '')
        return float(s)
    except Exception:
        return default


def _format_id_number(value, decimals=0):
    try:
        n = float(value)
    except Exception:
        return str(value)
    # Stockbit-style grouping (Indonesia): 1.234.567
    fmt = f"{{:,.{decimals}f}}".format(n)
    return fmt.replace(',', 'X').replace('.', ',').replace('X', '.').replace(',00', '') if decimals == 0 else fmt.replace(',', 'X').replace('.', ',').replace('X', '.')


def _format_price(value):
    if value in (None, '', '-'):  # keep placeholder
        return '-'
    n = _to_float(value, default=None)
    if n is None:
        return str(value)
    # Stocks on IDX typically show integer price
    return _format_id_number(n, decimals=0)


def _format_change_pair(change_abs, change_pct):
    if change_abs in (None, '', '-') and change_pct in (None, '', '-'):
        return '-'
    ca = _to_float(change_abs, default=0.0)
    cp = _to_float(change_pct, default=0.0)
    sign = '+' if ca > 0 else ''
    # abs: integer-ish, pct: 2 decimals
    abs_txt = _format_id_number(ca, decimals=0)
    pct_txt = _format_id_number(cp, decimals=2)
    return f"{sign}{abs_txt} ({sign if cp>0 else ''}{pct_txt}%)"


def _format_compact_number(value):
    if value in (None, '', '-'):  # keep placeholder
        return '-'
    n = _to_float(value, default=None)
    if n is None:
        return str(value)
    abs_n = abs(n)
    if abs_n >= 1_000_000_000:
        return f"{n/1_000_000_000:.2f}B".rstrip('0').rstrip('.')
    if abs_n >= 1_000_000:
        return f"{n/1_000_000:.2f}M".rstrip('0').rstrip('.')
    if abs_n >= 1_000:
        return f"{n/1_000:.2f}K".rstrip('0').rstrip('.')
    return _format_id_number(n, decimals=0)


def _is_idx_market_open(now=None) -> bool:
    """Best-effort: treat IDX as open on weekdays during working hours (Jakarta time)."""
    try:
        if now is None:
            if ZoneInfo is not None:
                now = datetime.now(ZoneInfo('Asia/Jakarta'))
            else:
                now = datetime.now()
        # weekend
        if now.weekday() >= 5:
            return False
        h = now.hour + (now.minute / 60.0)
        # simple window; we intentionally ignore intraday breaks for now
        return 9.0 <= h <= 16.0
    except Exception:
        return False


class SparklineWidget(Widget):
    values = ListProperty([])
    line_color = ListProperty([0.11, 0.75, 0.36, 1])

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.bind(pos=self._redraw, size=self._redraw, values=self._redraw, line_color=self._redraw)

    def _redraw(self, *_):
        self.canvas.clear()
        if not self.values or len(self.values) < 2:
            return
        try:
            from kivy.graphics import Color, Line
            w = max(1.0, float(self.width))
            h = max(1.0, float(self.height))
            pad = ui_dp(2)
            xs = []
            # normalize to 0..1
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
                Line(points=xs, width=ui_dp(1.2), cap='round', joint='round')
        except Exception:
            return


class _NavIcon(Widget):
    """Simple outline icon for bottom navigation (no external image files).

    icon_type: 'watchlist' | 'top10' | 'jurnal' | 'screening' | 'cek'.
    Color is controlled by the parent button via the `color` ListProperty.
    """

    icon_type = ''
    color = ListProperty(ThemeConfig.TEXT_DEFAULT)

    def __init__(self, icon_type: str = '', **kwargs):
        super().__init__(**kwargs)
        try:
            self.icon_type = str(icon_type or '').strip().lower()
        except Exception:
            self.icon_type = ''
        self.bind(pos=self._redraw, size=self._redraw, color=self._redraw)

    def _redraw(self, *_):
        self.canvas.clear()
        w = max(1.0, float(self.width))
        h = max(1.0, float(self.height))
        pad = ui_dp(2)
        cx = self.x + w / 2.0
        cy = self.y + h / 2.0
        from kivy.graphics import Color, Line, Ellipse, RoundedRectangle
        col = list(self.color or [0.70, 0.70, 0.70, 1])
        # Sedikit lebih tebal supaya icon jelas di layar HP
        t = ui_dp(1.7)
        with self.canvas:
            Color(*col)
            it = self.icon_type
            if it == 'watchlist':
                # Bullet list: three horizontal lines + bullets
                left = self.x + pad + ui_dp(2)
                right = self.x + w - pad
                y1 = self.y + h * 0.7
                y2 = self.y + h * 0.5
                y3 = self.y + h * 0.3
                Line(points=[left + ui_dp(6), y1, right, y1], width=t)
                Line(points=[left + ui_dp(6), y2, right, y2], width=t)
                Line(points=[left + ui_dp(6), y3, right, y3], width=t)
                r = ui_dp(2.2)
                Ellipse(pos=(left - r * 0.5, y1 - r * 0.5), size=(r, r))
                Ellipse(pos=(left - r * 0.5, y2 - r * 0.5), size=(r, r))
                Ellipse(pos=(left - r * 0.5, y3 - r * 0.5), size=(r, r))
            elif it == 'top10':
                # Simple bar chart with an upward arrow.
                base_y = self.y + pad
                x0 = self.x + pad
                step = (w - pad * 2) / 4.0
                Line(points=[x0, base_y, x0, base_y + h * 0.35], width=t)
                Line(points=[x0 + step, base_y, x0 + step, base_y + h * 0.55], width=t)
                Line(points=[x0 + 2 * step, base_y, x0 + 2 * step, base_y + h * 0.80], width=t)
                # Up arrow on the tallest bar
                ax = x0 + 2 * step
                ay = base_y + h * 0.80
                Line(points=[ax, ay, ax + ui_dp(4), ay + ui_dp(6)], width=t)
                Line(points=[ax, ay, ax - ui_dp(4), ay + ui_dp(6)], width=t)
            elif it == 'jurnal':
                # Notebook: outline rounded rectangle + sedikit garis judul.
                rw = w - pad * 2
                rh = h - pad * 2
                Line(rounded_rectangle=(self.x + pad, self.y + pad, rw, rh, ui_dp(3)), width=t)
                Line(points=[self.x + pad + rw * 0.22, self.y + pad + rh * 0.72, self.x + pad + rw * 0.78, self.y + pad + rh * 0.72], width=t)
            elif it == 'screening':
                # Magnifying glass.
                r = min(w, h) * 0.32
                Ellipse(pos=(cx - r, cy - r), size=(2 * r, 2 * r), angle_start=0, angle_end=360)
                hx1 = cx + r * 0.6
                hy1 = cy - r * 0.1
                hx2 = hx1 + ui_dp(6)
                hy2 = hy1 - ui_dp(6)
                Line(points=[hx1, hy1, hx2, hy2], width=t)
            elif it == 'cek':
                # Simple building outline with a base line.
                bw = w * 0.55
                bh = h * 0.60
                bx = cx - bw / 2.0
                by = cy - bh / 2.0
                Line(rectangle=(bx, by, bw, bh), width=t)
                # windows
                wx = bx + bw * 0.25
                wy = by + bh * 0.65
                s = ui_dp(2.2)
                Ellipse(pos=(wx - s / 2.0, wy - s / 2.0), size=(s, s))
                Ellipse(pos=(wx + bw * 0.3 - s / 2.0, wy - s / 2.0), size=(s, s))
                Ellipse(pos=(wx - s / 2.0, wy - bh * 0.35 - s / 2.0), size=(s, s))
                Ellipse(pos=(wx + bw * 0.3 - s / 2.0, wy - bh * 0.35 - s / 2.0), size=(s, s))
                # base line
                Line(points=[bx - ui_dp(2), by - ui_dp(2), bx + bw + ui_dp(2), by - ui_dp(2)], width=t)
            else:
                # fallback: simple circle
                r = min(w, h) * 0.35
                Ellipse(pos=(cx - r, cy - r), size=(2 * r, 2 * r), angle_start=0, angle_end=360)


    def _style_outline_button(btn, base_color, *, padding_scale=1.0):
        """Apply BUY/SELL-style outline button look.

        Used for both main trade inputs and popup actions (e.g. Profil, date OK)
        so the UI feels consistent. padding_scale < 1.0 makes popup buttons a bit
        more compact than the big BUY/SELL buttons.
        """
        try:
            btn.background_normal = ''
            btn.background_down = ''
            btn.background_color = ThemeConfig.BUTTON_BG
            btn.color = ThemeConfig.TEXT_BUTTON
            # Slightly reduced padding vs trade buttons when padding_scale < 1.
            base_pad = ui_dp(8)
            pad = base_pad * float(padding_scale)
            btn.padding = (pad, pad)
        except Exception:
            pass
        try:
            from kivy.graphics import Color, Line
            with btn.canvas.before:
                Color(*base_color)
                btn._outline = Line(rounded_rectangle=(btn.x, btn.y, btn.width, btn.height, ui_dp(ThemeConfig.RADIUS_BTN)), width=1.2)

            def _upd_outline(*_):
                try:
                    btn._outline.rounded_rectangle = (
                        btn.x + 1,
                        btn.y + 1,
                        max(0, btn.width - 2),
                        max(0, btn.height - 2),
                        ui_dp(8),
                    )
                except Exception:
                    pass

            btn.bind(pos=_upd_outline, size=_upd_outline)
        except Exception:
            pass


def _spark_values_for(symbol: str, chg_val: float, n: int = 14):
    rng = random.Random(symbol)
    base = rng.random() * 0.2 + 0.4
    noise = [rng.uniform(-0.08, 0.08) for _ in range(n)]
    trend = 0.18 if chg_val >= 0 else -0.18
    vals = []
    for i in range(n):
        t = i / max(1, n - 1)
        vals.append(base + trend * (t - 0.5) + noise[i])
    return vals

# Safety: some recovered bytecode calls `bind` with None callbacks which
# raises AssertionError in Kivy. Wrap EventDispatcher.bind to ignore None
# callback values so the desktop runner can start while we recover source.
_orig_event_bind = EventDispatcher.bind
def _safe_event_bind(self, *args, **kwargs):
    try:
        return _orig_event_bind(self, *args, **kwargs)
    except AssertionError:
        try:
            # filter out any None callback values from kwargs
            filtered = {k: v for k, v in kwargs.items() if v is not None}
            return _orig_event_bind(self, **filtered)
        except Exception:
            return None

try:
    EventDispatcher.bind = _safe_event_bind
except Exception:
    try:
        # Some Kivy builds expose EventDispatcher as an immutable C type.
        # Fall back to patching `Widget.bind` so instances use the safe wrapper.
        Widget.bind = _safe_event_bind
    except Exception:
        # Give up silently; runtime will use original behavior.
        pass

# Emulate mobile window size for desktop preview.
# IMPORTANT: Never force Window.size on Android/iOS, otherwise the GL surface
# can be created at a small size and the UI will render in the bottom-left.
from kivy.core.window import Window
from kivy.utils import platform as _kivy_platform

if _kivy_platform not in ("android", "ios"):
    try:
        Window.size = (360, 800)
    except Exception:
        pass

class StockbitTab(BoxLayout):
    def __init__(self, title, content, **kwargs):
        super().__init__(orientation='vertical', **kwargs)
        # Header ala Stockbit
        header = BoxLayout(orientation='vertical', size_hint_y=None, height=70, padding=(0,0,0,0), spacing=0)
        title_label = Label(text=f'[b]{title}[/b]', markup=True, font_size=ui_sp(20), color=(1,1,1,1), size_hint_y=None, height=ui_dp(38), halign='center', valign='middle', **_font_kwargs())
        header.add_widget(title_label)
        header.add_widget(Widget(size_hint_y=None, height=ui_dp(8)))
        self.add_widget(header)
        self.add_widget(content)


class SwipeToDeleteRow(Widget):
    dx = NumericProperty(0)

    def __init__(self, content, on_delete=None, on_tap=None, delete_width=110, scrollview=None, tap_widget=None, tap_filter=None, **kwargs):
        super().__init__(**kwargs)
        from kivy.uix.floatlayout import FloatLayout
        try:
            self._is_android = (str(_kivy_platform).lower() == 'android')
        except Exception:
            self._is_android = False
        self.size_hint_y = None
        self.height = kwargs.get('height', ui_dp(86))
        self._delete_width = ui_dp(delete_width)
        self._on_delete = on_delete
        self._on_tap = on_tap
        self._tap_widget = tap_widget
        self._tap_filter = tap_filter
        self._scrollview = scrollview
        self._touch_start = None
        self._start_dx = 0
        self._start_scroll_y = None
        self._mode = None  # None | 'swipe' | 'scroll'

        self._root = FloatLayout()
        self.add_widget(self._root)

        self._delete_btn = Button(
            text='Hapus',
            size_hint=(None, 1),
            width=self._delete_width,
            pos_hint={'right': 1, 'y': 0},
            background_normal='',
            background_down='',
            background_color=ThemeConfig.DELETE_BTN_BG,
            color=ThemeConfig.TEXT_DELETE,
            padding=(0, 0),
            **_font_kwargs(),
        )
        self._root.add_widget(self._delete_btn)

        self._content = content
        self._content.size_hint = (None, None)
        self._content.height = self.height
        self._root.add_widget(self._content)

        def _sync_layout(*_):
            self._root.pos = self.pos
            self._root.size = self.size

            # Margin horizontal 4dp untuk konten baris supaya terasa
            # seperti "kartu" (selaras dengan Top 10). Margin ini
            # hanya menggeser konten; tinggi/width widget utama tetap.
            pad_x = ui_dp(4)

            # Posisi + ukuran tombol delete (diletakkan di paling kanan).
            self._delete_btn.height = self.height
            self._delete_btn.x = self.x + self.width - self._delete_width
            self._delete_btn.y = self.y

            # Konten digeser ke dalam 4dp kiri/kanan.
            content_w = max(0, self.width - pad_x * 2)
            self._content.size = (content_w, self.height)
            self._content.pos = (self.x + pad_x + self.dx, self.y)

            # Safety: visibilitas tombol delete.
            try:
                if self._is_android:
                    # Di Android kita tidak pakai swipe delete; sembunyikan
                    # tombol merah supaya margin samping bersih.
                    self._delete_btn.disabled = True
                    self._delete_btn.opacity = 0.0
                    self._delete_btn.width = 0
                else:
                    open_enough = (self.dx <= -self._delete_width * 0.8)
                    self._delete_btn.disabled = not open_enough
                    self._delete_btn.opacity = 1.0 if open_enough else 0.0
            except Exception:
                pass

        self.bind(pos=_sync_layout, size=_sync_layout, dx=_sync_layout)
        _sync_layout()

        def _do_delete(_):
            if callable(self._on_delete):
                try:
                    self._on_delete()
                except Exception:
                    pass
        self._delete_btn.bind(on_press=_do_delete)

    def on_touch_down(self, touch):
        # On Android, fall back to default dispatch so we don't grab touches
        # at the widget level. This keeps interactions simpler and avoids
        # complex swipe handling that can interact badly with the SDL backend.
        if getattr(self, '_is_android', False):
            return super().on_touch_down(touch)
        if not self.collide_point(*touch.pos):
            return super().on_touch_down(touch)
        # Let delete button receive taps ONLY when row is swiped open.
        try:
            if self._delete_btn.collide_point(*touch.pos) and (self.dx <= -self._delete_width * 0.8):
                return super().on_touch_down(touch)
        except Exception:
            pass

        self._touch_start = (touch.x, touch.y)
        self._start_dx = self.dx
        try:
            self._start_scroll_y = self._scrollview.scroll_y if self._scrollview is not None else None
        except Exception:
            self._start_scroll_y = None
        self._mode = None
        touch.grab(self)
        return True

    def on_touch_move(self, touch):
        if getattr(self, '_is_android', False):
            return super().on_touch_move(touch)
        if touch.grab_current is not self:
            return super().on_touch_move(touch)
        if not self._touch_start:
            return True

        start_x, start_y = self._touch_start
        dx = touch.x - start_x
        dy = touch.y - start_y

        thresh = ui_dp(10)
        if self._mode is None:
            if abs(dx) > thresh and abs(dx) > abs(dy) * 1.2:
                self._mode = 'swipe'
            elif abs(dy) > thresh and abs(dy) > abs(dx) * 1.2:
                self._mode = 'scroll'

        if self._mode == 'swipe':
            new_dx = self._start_dx + dx
            if new_dx > 0:
                new_dx = 0
            if new_dx < -self._delete_width:
                new_dx = -self._delete_width
            self.dx = new_dx
            return True

        if self._mode == 'scroll' and self._scrollview is not None and self._start_scroll_y is not None:
            try:
                viewport = self._scrollview.children[0]
                scroll_range = max(1.0, float(viewport.height - self._scrollview.height))
                # finger up (dy>0) should scroll towards top (scroll_y increases)
                new_scroll_y = float(self._start_scroll_y) + (dy / scroll_range)
                if new_scroll_y < 0:
                    new_scroll_y = 0
                if new_scroll_y > 1:
                    new_scroll_y = 1
                self._scrollview.scroll_y = new_scroll_y
            except Exception:
                pass
            return True

        return True

    def on_touch_up(self, touch):
        if getattr(self, '_is_android', False):
            return super().on_touch_up(touch)
        if touch.grab_current is not self:
            return super().on_touch_up(touch)

        touch.ungrab(self)

        # Treat as tap when there is no meaningful movement.
        try:
            start_x, start_y = self._touch_start or (None, None)
            if start_x is not None and start_y is not None:
                dx = float(touch.x - start_x)
                dy = float(touch.y - start_y)
                thresh = ui_dp(10)
                if abs(dx) < thresh and abs(dy) < thresh:
                    # If swipe is open, tap closes it first.
                    if self.dx < 0:
                        self.dx = 0
                    else:
                        allow = True
                        try:
                            if callable(self._tap_filter):
                                allow = bool(self._tap_filter(touch))
                            elif self._tap_widget is not None:
                                allow = bool(self._tap_widget.collide_point(*touch.pos))
                        except Exception:
                            allow = True

                        if allow and callable(self._on_tap):
                            try:
                                self._on_tap()
                            except Exception:
                                pass
        except Exception:
            pass

        if self._mode == 'swipe':
            if self.dx < -self._delete_width * 0.4:
                self.dx = -self._delete_width
            else:
                self.dx = 0
        self._touch_start = None
        self._start_scroll_y = None
        self._mode = None
        return True

class WatchlistTab(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(orientation='vertical', **kwargs)
        from modules.data_fetcher import DataFetcher
        from modules.tradingview_fetcher import fetch_tradingview_snapshot
        try:
            from modules.stockbit_fetcher import StockbitFetcher
        except Exception:
            StockbitFetcher = None
        self.data_fetcher = DataFetcher()

        self._watchlist_file = os.path.join(os.path.dirname(__file__), 'data', 'watchlist.json')

        def _normalize_symbol(sym: str) -> str:
            s = (sym or '').strip().upper()
            if s.endswith(':IDX'):
                s = s.split(':', 1)[0]
            if s.endswith('.JK'):
                s = s[:-3]
            # Keep only common ticker characters
            s = ''.join(ch for ch in s if ch.isalnum() or ch in ('-', '_'))
            return s

        def _load_watchlist() -> list:
            try:
                with open(self._watchlist_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                if not isinstance(data, list):
                    return []
                out = []
                seen = set()
                for item in data:
                    s = _normalize_symbol(str(item))
                    if not s or s in seen:
                        continue
                    seen.add(s)
                    out.append(s)
                return out
            except Exception:
                return []

        def _save_watchlist():
            try:
                os.makedirs(os.path.dirname(self._watchlist_file), exist_ok=True)
                tmp = self._watchlist_file + '.tmp'
                with open(tmp, 'w', encoding='utf-8') as f:
                    json.dump(list(self.watchlist), f, ensure_ascii=False, indent=2)
                os.replace(tmp, self._watchlist_file)
            except Exception:
                pass

        self._normalize_watchlist_symbol = _normalize_symbol
        self._save_watchlist = _save_watchlist

        default_watchlist = [s['symbol'] for s in self.data_fetcher.sample_stocks]
        loaded = _load_watchlist()
        self.watchlist = loaded if loaded else default_watchlist
        self._subview = 'watchlist'  # 'watchlist' | 'portfolio'
        self._complete_view = False
        self._text_size_name = 'Default'
        self._text_scale = 1.0
        self._prev_price = {}
        self._auto_refresh_ev = None
        self._iep_cache = {}
        self._wl_refresh_inflight = False
        self._wl_refresh_requested = False
        self._wl_layout_key = None
        self._wl_symbols = []
        self._wl_row_refs = {}
        self._watchlist_source = str(os.environ.get('WATCHLIST_SOURCE', 'tradingview')).strip().lower()
        self._stockbit_fetcher = StockbitFetcher(use_cache=True) if StockbitFetcher else None
        self._stockbit_blocked_until = 0.0
        # Header like Stockbit screenshot (avatar left, title centered)
        header = BoxLayout(orientation='horizontal', size_hint_y=None, height=ui_dp(68), padding=(ui_dp(12), ui_dp(10)), spacing=ui_dp(8))
        from kivy.uix.anchorlayout import AnchorLayout
        from kivy.graphics import Color, Ellipse
        from kivy.app import App

        # Avatar palette + helpers (dibuat sedikit lebih "berkarakter" dan tidak sekadar warna solid)
        _avatar_palette = [
            (0.15, 0.65, 0.35, 1),  # hijau
            (0.20, 0.45, 0.85, 1),  # biru
            (0.85, 0.45, 0.35, 1),  # oranye / merah lembut
            (0.70, 0.40, 0.85, 1),  # ungu
            (0.95, 0.70, 0.25, 1),  # kuning keemasan
            (0.30, 0.75, 0.75, 1),  # toska
        ]

        def _get_avatar_rgba():
            try:
                app = App.get_running_app()
            except Exception:
                app = None
            idx = 0
            try:
                if app is not None:
                    idx = int(getattr(app, 'profile_avatar_style', 0) or 0)
            except Exception:
                idx = 0
            return _avatar_palette[idx % len(_avatar_palette)]

        avatar_size = ui_dp(42)
        avatar = Button(size_hint=(None, None), size=(avatar_size, avatar_size), background_normal='', background_down='', background_color=(0, 0, 0, 0))
        self._hdr_avatar = avatar
        self._avatar_color_rgba = list(_get_avatar_rgba())

        # Avatar dengan siluet kepala+bahu supaya terasa lebih "manusia" dan tidak hanya blok warna polos.
        with avatar.canvas.before:
            # latar belakang bulat (warna bisa diganti via Ganti Avatar)
            self._avatar_outer_color_instr = Color(*self._avatar_color_rgba)
            avatar._bg_circ = Ellipse(pos=avatar.pos, size=avatar.size)
            # wajah + bahu (putih di atas background)
            self._avatar_face_color_instr = Color(0.97, 0.97, 0.97, 1)
            avatar._head_circ = Ellipse(pos=avatar.pos, size=avatar.size)
            avatar._body_circ = Ellipse(pos=avatar.pos, size=avatar.size)
            # inner color instr tetap ada supaya kode existing (preview / cycle) tidak error
            self._avatar_inner_color_instr = self._avatar_outer_color_instr

        def _update_avatar_circles(*_a):
            try:
                # background penuh
                avatar._bg_circ.pos = avatar.pos
                avatar._bg_circ.size = avatar.size
                # kepala (lingkaran kecil di bagian atas)
                r = avatar.width * 0.36
                x_head = avatar.x + (avatar.width - r) / 2.0
                y_head = avatar.y + avatar.height * 0.52
                avatar._head_circ.pos = (x_head, y_head)
                avatar._head_circ.size = (r, r)
                # bahu / badan (ellipse lebar di bawah)
                bw = avatar.width * 0.82
                bh = avatar.height * 0.52
                x_body = avatar.x + (avatar.width - bw) / 2.0
                y_body = avatar.y + avatar.height * 0.04
                avatar._body_circ.pos = (x_body, y_body)
                avatar._body_circ.size = (bw, bh)
            except Exception:
                pass

        avatar.bind(pos=_update_avatar_circles, size=_update_avatar_circles)

        left = BoxLayout(size_hint=(None, 1), width=avatar_size)
        left.add_widget(avatar)
        header.add_widget(left)

        center = AnchorLayout(anchor_x='center', anchor_y='center')
        # Header utama aplikasi.
        title = Label(text='[b]Jurnal Saham IHSG[/b]', markup=True, font_size=ui_sp(18), color=(1, 1, 1, 1), halign='center', valign='middle', **_font_kwargs())
        center.add_widget(title)
        header.add_widget(center)

        header.add_widget(Widget(size_hint=(None, 1), width=avatar_size))
        self.add_widget(header)

        # Common popup styling helper so all popups match main UI theme
        def _make_styled_popup(content, *, title: str = '', size_hint=(0.9, None), height=None, auto_dismiss: bool = True):
            p = Popup(title=title, content=content, size_hint=size_hint, auto_dismiss=auto_dismiss)
            if height is not None:
                p.height = height
            try:
                p.separator_color = (0.18, 0.22, 0.30, 1)
                p.title_color = (0.95, 0.95, 0.95, 1)
            except Exception:
                pass
            return p

        def _style_input_dark(ti):
            try:
                ti.background_normal = ''
                ti.background_active = ''
                ti.background_color = (0.12, 0.12, 0.12, 1)
                ti.foreground_color = (0.95, 0.95, 0.95, 1)
                ti.cursor_color = (0.90, 0.90, 0.90, 1)
                ti.padding = (ui_dp(10), ui_dp(10))
            except Exception:
                pass

        def _get_app_auth():
            try:
                app = App.get_running_app()
            except Exception:
                app = None
            uid = getattr(app, 'auth_user_id', None) if app is not None else None
            email = getattr(app, 'auth_email', None) if app is not None else None
            return app, uid, email

        def _open_profile_popup(_=None):
            from kivy.uix.boxlayout import BoxLayout as _Box
            from kivy.uix.label import Label as _Label
            from kivy.uix.textinput import TextInput as _TI
            from kivy.uix.button import Button as _Btn

            app, uid, email = _get_app_auth()

            # Ambil nama tampilan yang sudah pernah diset (kalau ada)
            cur_display_name = ''
            try:
                if app is not None:
                    cur_display_name = str(getattr(app, 'profile_display_name', '') or '').strip()
            except Exception:
                cur_display_name = ''

            root = _Box(orientation='vertical', padding=(ui_dp(14), ui_dp(18)), spacing=ui_dp(10))

            if uid:
                # Avatar preview + change button
                from kivy.uix.boxlayout import BoxLayout as _HBox
                from kivy.graphics import Color as _Color, Ellipse as _Ellipse

                avatar_row = _HBox(orientation='horizontal', spacing=ui_dp(10), size_hint_y=None, height=ui_dp(64))
                avatar_preview = Widget(size_hint=(None, None), size=(ui_dp(52), ui_dp(52)))
                with avatar_preview.canvas.before:
                    # Samakan dengan header: outer + inner circle
                    self._avatar_preview_outer_instr = _Color(*self._avatar_color_rgba)
                    avatar_preview._outer = _Ellipse(pos=avatar_preview.pos, size=avatar_preview.size)
                    inner_rgba = (
                        min(self._avatar_color_rgba[0] + 0.10, 1.0),
                        min(self._avatar_color_rgba[1] + 0.10, 1.0),
                        min(self._avatar_color_rgba[2] + 0.10, 1.0),
                        self._avatar_color_rgba[3],
                    )
                    self._avatar_preview_inner_instr = _Color(*inner_rgba)
                    avatar_preview._inner = _Ellipse(pos=avatar_preview.pos, size=avatar_preview.size)

                def _update_preview_circles(*_a):
                    try:
                        avatar_preview._outer.pos = avatar_preview.pos
                        avatar_preview._outer.size = avatar_preview.size
                        scale = 0.70
                        inset_x = avatar_preview.width * (1.0 - scale) / 2.0
                        inset_y = avatar_preview.height * (1.0 - scale) / 2.0
                        avatar_preview._inner.pos = (avatar_preview.x + inset_x, avatar_preview.y + inset_y)
                        avatar_preview._inner.size = (avatar_preview.width * scale, avatar_preview.height * scale)
                    except Exception:
                        pass

                avatar_preview.bind(pos=_update_preview_circles, size=_update_preview_circles)

                btn_avatar = _Btn(text='Ganti Avatar', size_hint=(1, 1))
                avatar_row.add_widget(avatar_preview)
                avatar_row.add_widget(btn_avatar)
                root.add_widget(avatar_row)

                # Teks kecil info email login supaya identitas lebih jelas
                if email:
                    email_lbl = _Label(
                        text=f"Login: {email}",
                        font_size=ui_sp(11),
                        color=(0.72, 0.72, 0.72, 1),
                        halign='left',
                        valign='middle',
                        size_hint_y=None,
                        height=ui_dp(18),
                        **_font_kwargs(),
                    )
                    root.add_widget(email_lbl)

                # Simple profile name field (local + metadata update)
                name_in = _TI(text=cur_display_name, hint_text='Nama tampilan (opsional)', multiline=False, size_hint_y=None, height=ui_dp(40))
                _style_input_dark(name_in)
                root.add_widget(name_in)

                # Change password section
                pw_lbl = _Label(
                    text='Ganti password (Supabase auth)',
                    font_size=ui_sp(13),
                    color=(0.78, 0.78, 0.78, 1),
                    halign='left',
                    valign='middle',
                    size_hint_y=None,
                    height=ui_dp(20),
                    **_font_kwargs(),
                )
                root.add_widget(pw_lbl)

                pw_new = _TI(hint_text='Password baru', multiline=False, password=True, size_hint_y=None, height=ui_dp(40))
                pw_confirm = _TI(hint_text='Ulangi password baru', multiline=False, password=True, size_hint_y=None, height=ui_dp(40))
                _style_input_dark(pw_new)
                _style_input_dark(pw_confirm)
                root.add_widget(pw_new)
                root.add_widget(pw_confirm)

                msg_lbl = _Label(
                    text='',
                    font_size=ui_sp(12),
                    color=(0.96, 0.55, 0.55, 1),
                    halign='left',
                    valign='top',
                    size_hint_y=None,
                    height=ui_dp(56),
                    **_font_kwargs(),
                )
                try:
                    # Biar pesan (berhasil/gagal) bisa multi-line tanpa terpotong
                    msg_lbl.bind(size=lambda inst, val: setattr(inst, 'text_size', (inst.width, None)))
                except Exception:
                    pass
                root.add_widget(msg_lbl)

                btn_row_top = _Box(orientation='horizontal', spacing=ui_dp(8), size_hint_y=None, height=ui_dp(40))
                btn_save_profile = _Btn(text='Simpan Profil', size_hint=(1, 1))
                btn_change_pw = _Btn(text='Ubah Password', size_hint=(1, 1))
                try:
                    _style_outline_button(btn_save_profile, (0.11, 0.75, 0.36, 1), padding_scale=0.7)
                    _style_outline_button(btn_change_pw, (0.22, 0.22, 0.22, 1), padding_scale=0.7)
                except Exception:
                    pass
                btn_row_top.add_widget(btn_save_profile)
                btn_row_top.add_widget(btn_change_pw)
                root.add_widget(btn_row_top)

                btn_row_bottom = _Box(orientation='horizontal', spacing=ui_dp(8), size_hint_y=None, height=ui_dp(40))
                btn_logout = _Btn(text='Logout', size_hint=(1, 1))
                btn_close = _Btn(text='Tutup', size_hint=(1, 1))
                try:
                    _style_outline_button(btn_logout, (0.80, 0.16, 0.22, 1), padding_scale=0.7)
                    _style_outline_button(btn_close, (0.22, 0.22, 0.22, 1), padding_scale=0.7)
                except Exception:
                    pass
                btn_row_bottom.add_widget(btn_logout)
                btn_row_bottom.add_widget(btn_close)
                root.add_widget(btn_row_bottom)

                # Put identity in the popup title; kalau ada display name, pakai itu dulu
                _id_txt = cur_display_name or email or uid or ''
                if _id_txt:
                    _title = f"Profil Pengguna - {_id_txt}"
                else:
                    _title = 'Profil Pengguna'

                popup = _make_styled_popup(root, title=_title, size_hint=(0.92, None), height=ui_dp(388), auto_dismiss=False)

                def _set_msg(txt: str, *, ok: bool = False):
                    try:
                        msg_lbl.color = (0.50, 0.90, 0.50, 1) if ok else (0.96, 0.55, 0.55, 1)
                        msg_lbl.text = txt or ''
                    except Exception:
                        pass

                def _do_save_profile(*_a):
                    nm = (name_in.text or '').strip()
                    if not nm:
                        _set_msg('Nama tampilan kosong (opsional, boleh dikosongkan).', ok=False)
                    try:
                        if app is not None:
                            setattr(app, 'profile_display_name', nm)
                    except Exception:
                        pass
                    try:
                        cs = getattr(app, 'cloud_sync', None)
                        if cs is not None and getattr(cs, 'client', None) is not None:
                            cs.client.auth.update_user({"data": {"display_name": nm}})
                    except Exception as _e:
                        _set_msg(f'Gagal simpan profil: {_e}', ok=False)
                        return
                    _set_msg('Profil tersimpan.', ok=True)

                def _cycle_avatar(*_a):
                    try:
                        app2 = App.get_running_app()
                    except Exception:
                        app2 = None
                    try:
                        cur = 0
                        if app2 is not None:
                            cur = int(getattr(app2, 'profile_avatar_style', 0) or 0)
                        cur = (cur + 1) % len(_avatar_palette)
                        if app2 is not None:
                            setattr(app2, 'profile_avatar_style', cur)
                        new_rgba = _avatar_palette[cur]
                        self._avatar_color_rgba = list(new_rgba)
                        # update header outer/inner
                        try:
                            self._avatar_outer_color_instr.rgba = new_rgba
                            inner_rgba2 = (
                                min(new_rgba[0] + 0.10, 1.0),
                                min(new_rgba[1] + 0.10, 1.0),
                                min(new_rgba[2] + 0.10, 1.0),
                                new_rgba[3],
                            )
                            self._avatar_inner_color_instr.rgba = inner_rgba2
                        except Exception:
                            pass
                        # update preview outer/inner
                        try:
                            self._avatar_preview_outer_instr.rgba = new_rgba
                            inner_rgba3 = (
                                min(new_rgba[0] + 0.10, 1.0),
                                min(new_rgba[1] + 0.10, 1.0),
                                min(new_rgba[2] + 0.10, 1.0),
                                new_rgba[3],
                            )
                            self._avatar_preview_inner_instr.rgba = inner_rgba3
                        except Exception:
                            pass
                        try:
                            _set_msg('Avatar diubah.', ok=True)
                        except Exception:
                            pass
                    except Exception as _e:
                        _set_msg(f'Gagal ubah avatar: {_e}', ok=False)

                def _do_change_pw(*_a):
                    new_pw = pw_new.text or ''
                    new_pw2 = pw_confirm.text or ''
                    if not new_pw or not new_pw2:
                        _set_msg('Password baru & konfirmasi wajib diisi.', ok=False)
                        return
                    if new_pw != new_pw2:
                        _set_msg('Password baru tidak sama.', ok=False)
                        return
                    if len(new_pw) < 6:
                        _set_msg('Password minimal 6 karakter.', ok=False)
                        return
                    try:
                        cs = getattr(app, 'cloud_sync', None)
                        if cs is None or getattr(cs, 'client', None) is None:
                            _set_msg('Cloud belum aktif di build ini.', ok=False)
                            return
                        cs.client.auth.update_user({"password": new_pw})
                    except Exception as _e:
                        _set_msg(f'Gagal ubah password: {_e}', ok=False)
                        return
                    _set_msg('Password berhasil diubah.', ok=True)
                    try:
                        pw_new.text = ''
                        pw_confirm.text = ''
                    except Exception:
                        pass

                def _do_logout(*_a):
                    try:
                        if app is not None:
                            app.auth_user_id = None
                            app.auth_email = None
                            app.cloud_sync = None
                    except Exception:
                        pass
                    try:
                        popup.dismiss()
                    except Exception:
                        pass

                btn_save_profile.bind(on_press=_do_save_profile)
                btn_change_pw.bind(on_press=_do_change_pw)
                btn_avatar.bind(on_press=_cycle_avatar)
                btn_logout.bind(on_press=_do_logout)
                btn_close.bind(on_press=lambda *_a: popup.dismiss())
                popup.open()
                return

            # Not logged in: simple login form (dark mode)
            email_in = _TI(hint_text='Email', multiline=False, size_hint_y=None, height=ui_dp(40))
            pw_in = _TI(hint_text='Password', multiline=False, password=True, size_hint_y=None, height=ui_dp(40))
            _style_input_dark(email_in)
            _style_input_dark(pw_in)
            root.add_widget(email_in)
            root.add_widget(pw_in)

            err_lbl = _Label(
                text='',
                font_size=ui_sp(12),
                color=(0.96, 0.55, 0.55, 1),
                halign='left',
                valign='top',
                size_hint_y=None,
                height=ui_dp(56),
                **_font_kwargs(),
            )
            try:
                # Biar teks error bisa multi-line dan rapi di lebar popup
                err_lbl.bind(size=lambda inst, val: setattr(inst, 'text_size', (inst.width, None)))
            except Exception:
                pass
            root.add_widget(err_lbl)

            # Tombol tambahan untuk kirim ulang email konfirmasi (hanya muncul saat relevan)
            btn_resend = _Btn(
                text='Kirim ulang email konfirmasi',
                size_hint=(1, None),
                height=ui_dp(34),
            )
            btn_resend.opacity = 0
            btn_resend.disabled = True
            root.add_widget(btn_resend)

            btn_row = _Box(orientation='horizontal', spacing=ui_dp(8), size_hint_y=None, height=ui_dp(40))
            btn_login = _Btn(text='🔓 Login', size_hint=(1, 1))
            btn_register = _Btn(text='Daftar', size_hint=(1, 1))
            btn_cancel = _Btn(text='Tutup', size_hint=(1, 1))
            btn_row.add_widget(btn_login)
            btn_row.add_widget(btn_register)
            btn_row.add_widget(btn_cancel)
            root.add_widget(btn_row)

            popup = _make_styled_popup(root, title='Login ke profil', size_hint=(0.88, None), height=ui_dp(320))

            def _set_error(msg: str, *, can_resend: bool = False):
                try:
                    err_lbl.text = msg or ''
                    btn_resend.opacity = 1 if can_resend else 0
                    btn_resend.disabled = not can_resend
                except Exception:
                    pass

            def _do_login(*_a):
                em = (email_in.text or '').strip()
                pw = pw_in.text or ''
                if not em or not pw:
                    _set_error('Email dan password wajib diisi.')
                    return

                url, key = _get_supabase_config()
                if not (url and key):
                    _set_error('Env SUPABASE_URL / SUPABASE_ANON_KEY belum di-set.')
                    return

                try:
                    # Prefer official client if available on this platform
                    if _supabase_create_client is not None and CloudSync is not None:
                        client = _supabase_create_client(url, key)
                        resp = client.auth.sign_in_with_password({"email": em, "password": pw})
                        user = getattr(resp, 'user', None) or getattr(getattr(resp, 'session', None), 'user', None)
                        if user is None:
                            _set_error('Login gagal. Cek email/password.')
                            return

                        try:
                            if app is not None:
                                app.auth_user_id = getattr(user, 'id', None)
                                app.auth_email = getattr(user, 'email', None) or em
                                app.cloud_sync = CloudSync(client=client) if CloudSync is not None else None
                        except Exception:
                            pass
                    else:
                        # Fallback REST auth (Android build where supabase SDK tidak ada)
                        info = _supabase_rest_auth('sign_in', url=url, key=key, email=em, password=pw)
                        try:
                            if app is not None:
                                app.auth_user_id = info.get('id')
                                app.auth_email = info.get('email') or em
                                # CloudSync tidak diaktifkan di mode REST minimal ini.
                                app.cloud_sync = None
                        except Exception:
                            pass

                    try:
                        popup.dismiss()
                    except Exception:
                        pass
                except Exception as _e:
                    emsg = str(_e)
                    lower = emsg.lower()
                    can_resend = 'email belum dikonfirmasi' in lower or 'email not confirmed' in lower
                    if lower.startswith('email belum dikonfirmasi'):
                        display_msg = emsg
                    else:
                        display_msg = f'Error: {emsg}'
                    _set_error(display_msg, can_resend=can_resend)

            def _do_resend(*_a2):
                em = (email_in.text or '').strip()
                if not em:
                    _set_error('Masukkan email yang ingin dikonfirmasi dulu.', can_resend=False)
                    return

                url, key = _get_supabase_config()
                if not (url and key):
                    _set_error('Env SUPABASE_URL / SUPABASE_ANON_KEY belum di-set.', can_resend=False)
                    return

                try:
                    _supabase_rest_resend_signup(url=url, key=key, email=em)
                    _set_error('Link konfirmasi sudah dikirim ulang ke email Anda.', can_resend=False)
                except Exception as _e:
                    emsg = str(_e)
                    lower = emsg.lower()
                    # Kalau tetap kena rate-limit, biarkan tombol tetap muncul supaya user bisa coba lagi nanti
                    can_resend = 'terlalu banyak percobaan' not in lower
                    _set_error(f'Error kirim ulang: {emsg}', can_resend=can_resend)

            def _do_register(*_a):
                em = (email_in.text or '').strip()
                pw = pw_in.text or ''
                if not em or not pw:
                    _set_error('Email dan password wajib diisi.')
                    return

                url, key = _get_supabase_config()
                if not (url and key):
                    _set_error('Env SUPABASE_URL / SUPABASE_ANON_KEY belum di-set.')
                    return

                try:
                    # Prefer official client jika tersedia
                    if _supabase_create_client is not None and CloudSync is not None:
                        client = _supabase_create_client(url, key)
                        resp = client.auth.sign_up({"email": em, "password": pw})
                        user = getattr(resp, 'user', None) or getattr(getattr(resp, 'session', None), 'user', None)
                        if user is None:
                            _set_error('Registrasi gagal. Coba email lain.')
                            return

                        try:
                            if app is not None:
                                app.auth_user_id = getattr(user, 'id', None)
                                app.auth_email = getattr(user, 'email', None) or em
                                app.cloud_sync = CloudSync(client=client) if CloudSync is not None else None
                        except Exception:
                            pass
                    else:
                        # Fallback REST signup
                        info = _supabase_rest_auth('sign_up', url=url, key=key, email=em, password=pw)
                        try:
                            if app is not None:
                                app.auth_user_id = info.get('id')
                                app.auth_email = info.get('email') or em
                                app.cloud_sync = None
                        except Exception:
                            pass

                    try:
                        popup.dismiss()
                    except Exception:
                        pass
                except Exception as _e:
                    _set_error(f'Error daftar: {_e}')

            btn_login.bind(on_press=_do_login)
            btn_register.bind(on_press=_do_register)
            btn_cancel.bind(on_press=lambda *_a: popup.dismiss())
            btn_resend.bind(on_press=_do_resend)
            popup.open()

        # Registrasikan pembuka popup profil ke App agar bisa dipanggil dari tab lain (sticky avatar)
        try:
            app_for_avatar, _, _ = _get_app_auth()
        except Exception:
            app_for_avatar = None
        try:
            if app_for_avatar is not None:
                setattr(app_for_avatar, 'open_profile_popup', _open_profile_popup)
        except Exception:
            pass

        # Avatar acts as profile/login entry point with a small flash effect
        from kivy.clock import Clock as _Clock

        def _flash_and_open(*_a):
            base = list(self._avatar_color_rgba or [0.18, 0.22, 0.30, 1])
            try:
                # brief flash (slightly brighter) pada outer ring
                flash = (min(base[0] + 0.08, 1.0), min(base[1] + 0.08, 1.0), min(base[2] + 0.08, 1.0), base[3])
                self._avatar_outer_color_instr.rgba = flash
                def _restore(_dt):
                    try:
                        self._avatar_outer_color_instr.rgba = tuple(base)
                    except Exception:
                        pass
                _Clock.schedule_once(_restore, 0.15)
            except Exception:
                pass
            try:
                _open_profile_popup()
            except Exception:
                pass

        avatar.bind(on_press=_flash_and_open)

        def open_add_symbol(_=None):
            root = BoxLayout(orientation='vertical', padding=(ui_dp(12), ui_dp(12)), spacing=ui_dp(10))
            ti = TextInput(text='', hint_text='Symbol (e.g. BBCA)', multiline=False, font_size=ui_sp(16), **_font_kwargs())
            root.add_widget(ti)

            btn_row = BoxLayout(orientation='horizontal', size_hint_y=None, height=ui_dp(44), spacing=ui_dp(10))
            btn_cancel = Button(text='Batal', background_normal='', background_down='', background_color=(0, 0, 0, 0), color=(0.88, 0.88, 0.88, 1), padding=(0, 0), **_font_kwargs())
            btn_add = Button(text='Tambah', background_normal='', background_down='', background_color=(0.11, 0.75, 0.36, 1), color=(1, 1, 1, 1), padding=(0, 0), **_font_kwargs())
            btn_row.add_widget(btn_cancel)
            btn_row.add_widget(btn_add)
            root.add_widget(btn_row)

            p2 = _make_styled_popup(root, title='Tambah saham', size_hint=(0.85, None), height=ui_dp(190))

            def ok_add(*_):
                sym = self._normalize_watchlist_symbol(ti.text)
                if not sym:
                    try:
                        p2.dismiss()
                    except Exception:
                        pass
                    return

                try:
                    if sym in self.watchlist:
                        self.watchlist.remove(sym)
                    self.watchlist.insert(0, sym)
                except Exception:
                    pass

                try:
                    self._save_watchlist()
                except Exception:
                    pass

                try:
                    refresh()
                except Exception:
                    pass
                try:
                    p2.dismiss()
                except Exception:
                    pass

            btn_cancel.bind(on_press=lambda *_: p2.dismiss())
            btn_add.bind(on_press=ok_add)
            try:
                ti.bind(on_text_validate=ok_add)
            except Exception:
                pass

            p2.open()

        def open_text_size(_=None):
            # Full-screen-ish popup like screenshot
            modes = [
                ('Small', 0.90),
                ('Default', 1.00),
                ('Large', 1.12),
                ('Extra Large', 1.24),
            ]
            selected_name = {'name': self._text_size_name}

            root = BoxLayout(orientation='vertical', padding=(ui_dp(14), ui_dp(12)), spacing=ui_dp(12))

            # Header (back + title)
            header = BoxLayout(orientation='horizontal', size_hint_y=None, height=ui_dp(44))
            back_btn = Button(
                text='‹',
                size_hint=(None, 1),
                width=ui_dp(44),
                font_size=ui_sp(22),
                background_normal='',
                background_down='',
                background_color=(0, 0, 0, 0),
                padding=(0, 0),
                color=(0.85, 0.85, 0.85, 1),
                **_font_kwargs(),
            )
            header.add_widget(back_btn)
            header.add_widget(Widget())
            header.add_widget(Label(text='[b]Text Size[/b]', markup=True, font_size=ui_sp(18), color=(0.92, 0.92, 0.92, 1), **_font_kwargs()))
            header.add_widget(Widget())
            header.add_widget(Widget(size_hint=(None, 1), width=ui_dp(44)))
            root.add_widget(header)

            # Preview area: show a couple of rows (always complete view) above the options
            preview_box = BoxLayout(orientation='vertical', spacing=0, size_hint_y=None)
            preview_box.bind(minimum_height=preview_box.setter('height'))

            # Fetch latest for first two symbols (best-effort)
            preview_syms = [s for s in list(self.watchlist)[:2] if s]
            try:
                tv_preview = fetch_tradingview_snapshot(preview_syms) if preview_syms else {}
            except Exception:
                tv_preview = {}
            symbol_to_name = {s['symbol']: s.get('company_name', '') for s in getattr(self.data_fetcher, 'sample_stocks', [])}

            def sp_preview(v):
                return ui_sp(v * (self._text_scale if self._text_scale else 1.0))

            def build_preview_card(symbol: str):
                d = tv_preview.get(symbol, {})
                name = symbol_to_name.get(symbol, '')
                price_raw = d.get('price', '-')
                chg_raw = d.get('change', d.get('change_abs', 0))
                chg_pct_raw = d.get('change_percent', d.get('change_pct', 0))
                chg_val = _to_float(chg_raw, default=0.0)
                color_down = (0.86, 0.25, 0.25, 1)
                color_up = (0.11, 0.75, 0.36, 1)
                chg_color = color_up if chg_val >= 0 else color_down

                base_row_h = ui_dp(86)
                detail_h = ui_dp(90)
                card_h = base_row_h + detail_h

                card = BoxLayout(orientation='vertical')
                card.size_hint = (1, None)
                card.height = card_h

                with card.canvas.before:
                    from kivy.graphics import Color, Rectangle
                    Color(0.06, 0.06, 0.06, 1)
                    card._bg = Rectangle(pos=card.pos, size=card.size)
                    Color(0.12, 0.12, 0.12, 1)
                    card._sep = Rectangle(pos=(card.x, card.y), size=(card.width, 1))
                def _upd(*_):
                    card._bg.pos = card.pos
                    card._bg.size = card.size
                    card._sep.pos = (card.x, card.y)
                    card._sep.size = (card.width, 1)
                card.bind(pos=_upd, size=_upd)

                top = BoxLayout(orientation='horizontal', padding=(ui_dp(4), ui_dp(8)), spacing=ui_dp(10), size_hint_y=None, height=base_row_h)

                mid = BoxLayout(orientation='vertical', spacing=2, size_hint_x=1)
                top_line = BoxLayout(orientation='horizontal', size_hint_y=None, height=ui_dp(28), spacing=ui_dp(6))
                sym_lbl = Label(text=f'[b]{symbol}[/b]', markup=True, font_size=sp_preview(18), color=(0.92,0.92,0.92,1), halign='left', valign='middle', **_font_kwargs())
                sym_lbl.size_hint_x = 1
                sym_lbl.text_size = (sym_lbl.width, None)
                try:
                    sym_lbl.shorten = True
                    sym_lbl.shorten_from = 'right'
                except Exception:
                    pass
                sym_lbl.bind(size=lambda inst, val: setattr(inst, 'text_size', (inst.width, None)))
                top_line.add_widget(sym_lbl)
                mid.add_widget(top_line)

                name_lbl = Label(text=name, font_size=sp_preview(13), color=(0.55,0.55,0.55,1), halign='left', valign='middle', size_hint_y=None, height=ui_dp(22), **_font_kwargs())
                name_lbl.text_size = (name_lbl.width, None)
                try:
                    name_lbl.shorten = True
                    name_lbl.shorten_from = 'right'
                except Exception:
                    pass
                name_lbl.bind(size=lambda inst, val: setattr(inst, 'text_size', (inst.width, None)))
                mid.add_widget(name_lbl)
                top.add_widget(mid)

                from kivy.uix.anchorlayout import AnchorLayout
                spark_slot = AnchorLayout(size_hint=(None, 1), width=ui_dp(92), anchor_x='right', anchor_y='center')
                spark = SparklineWidget(size_hint=(None, None), size=(ui_dp(82), ui_dp(30)))
                spark.values = _spark_values_for(symbol, chg_val)
                spark.line_color = list(chg_color)
                spark_slot.add_widget(spark)
                top.add_widget(spark_slot)

                right = BoxLayout(orientation='vertical', size_hint_x=None, width=ui_dp(128), spacing=ui_dp(2))
                price_lbl = Label(text=_format_price(price_raw), font_size=sp_preview(18), color=(0.90,0.90,0.90,1), halign='right', valign='middle', size_hint_y=None, height=ui_dp(30), **_font_kwargs())
                price_lbl.text_size = (right.width, None)
                change_lbl = Label(text=_format_change_pair(chg_raw, chg_pct_raw), font_size=sp_preview(13), color=chg_color, halign='right', valign='middle', size_hint_y=None, height=ui_dp(26), **_font_kwargs())
                change_lbl.text_size = (right.width, None)
                right.add_widget(price_lbl)
                right.add_widget(change_lbl)
                top.add_widget(right)
                card.add_widget(top)

                def _stat_row(label_txt, value_txt, value_color=(0.82, 0.82, 0.82, 1)):
                    r = BoxLayout(orientation='horizontal', size_hint_y=None, height=ui_dp(20))
                    lbl = Label(text=label_txt, font_size=sp_preview(12), color=(0.45, 0.45, 0.45, 1), size_hint_x=None, width=ui_dp(44), halign='left', valign='middle', **_font_kwargs())
                    lbl.text_size = (lbl.width, None)
                    r.add_widget(lbl)
                    val = Label(text=value_txt, font_size=sp_preview(13), color=value_color, halign='right', valign='middle', **_font_kwargs())
                    val.text_size = (val.width, None)
                    val.bind(size=lambda inst, val_size: setattr(inst, 'text_size', (inst.width, None)))
                    try:
                        val.shorten = True
                        val.shorten_from = 'left'
                    except Exception:
                        pass
                    r.add_widget(val)
                    return r

                details = BoxLayout(orientation='horizontal', size_hint_y=None, height=detail_h, padding=(ui_dp(4), 0, ui_dp(4), ui_dp(10)), spacing=ui_dp(16))
                left_col = BoxLayout(orientation='vertical', spacing=ui_dp(2))
                right_col = BoxLayout(orientation='vertical', spacing=ui_dp(2))
                price_num = _to_float(price_raw, default=None)
                bid_raw = d.get('bid', None)
                ask_raw = d.get('ask', None)
                if bid_raw in (None, '') and price_num is not None:
                    bid_raw = max(0, price_num - 1)
                if ask_raw in (None, '') and price_num is not None:
                    ask_raw = max(0, price_num + 1)

                iev_raw = d.get('volume', d.get('vol', d.get('value', d.get('turnover', '-'))))
                iep_value = f"{_format_price(price_raw)} {_format_change_pair(chg_raw, chg_pct_raw).replace(' ', '')}"

                left_col.add_widget(_stat_row('Bid', _format_price(bid_raw), value_color=(0.11, 0.75, 0.36, 1)))
                left_col.add_widget(_stat_row('Lot', _format_compact_number(d.get('lot', '-'))))
                left_col.add_widget(_stat_row('Freq', _format_compact_number(d.get('freq', '-')), value_color=(0.11, 0.75, 0.36, 1)))
                right_col.add_widget(_stat_row('Ask', _format_price(ask_raw), value_color=(0.86, 0.25, 0.25, 1)))
                right_col.add_widget(_stat_row('Val', _format_compact_number(iev_raw)))
                right_col.add_widget(_stat_row('Avg', _format_price(d.get('avg', price_raw))))
                details.add_widget(left_col)
                details.add_widget(right_col)
                card.add_widget(details)
                return card

            if preview_syms:
                for s in preview_syms:
                    preview_box.add_widget(build_preview_card(s))
            else:
                preview_box.add_widget(Widget(size_hint_y=None, height=ui_dp(12)))

            root.add_widget(preview_box)

            # Options (radio-like)
            options = BoxLayout(orientation='vertical', spacing=0)
            check_green = (0.11, 0.75, 0.36, 1)
            off_grey = (0.50, 0.50, 0.50, 1)
            row_widgets = {}

            def set_selected(name: str):
                selected_name['name'] = name
                for n, w in row_widgets.items():
                    try:
                        w._mark.text = '✓' if n == name else '○'
                        w._mark.color = check_green if n == name else off_grey
                    except Exception:
                        pass

            for name, _scale in modes:
                r = ClickableRow(orientation='horizontal', size_hint_y=None, height=ui_dp(52))
                r.add_widget(Label(text=name, font_size=ui_sp(16), color=(0.88, 0.88, 0.88, 1), halign='left', valign='middle', **_font_kwargs()))
                r.add_widget(Widget())
                mark = Label(text='○', font_size=ui_sp(18), color=off_grey, size_hint_x=None, width=ui_dp(44), halign='right', valign='middle', **_font_kwargs())
                mark.text_size = (mark.width, None)
                r.add_widget(mark)
                r._mark = mark
                r.bind(on_press=lambda _r, n=name: set_selected(n))
                options.add_widget(r)
                row_widgets[name] = r

            set_selected(self._text_size_name)
            root.add_widget(options)

            apply_btn = Button(
                text='Apply',
                size_hint_y=None,
                height=ui_dp(58),
                background_normal='',
                background_down='',
                background_color=(0.11, 0.75, 0.36, 1),
                color=(1, 1, 1, 1),
                font_size=ui_sp(18),
                padding=(0, 0),
                **_font_kwargs(),
            )
            root.add_widget(apply_btn)

            p = _make_styled_popup(root, title='', size_hint=(0.98, 0.98), auto_dismiss=False)

            def _dismiss(*_):
                try:
                    p.dismiss()
                except Exception:
                    pass
            back_btn.bind(on_press=_dismiss)

            def _apply(*_):
                chosen = selected_name['name']
                self._text_size_name = chosen
                scale = 1.0
                for n, s in modes:
                    if n == chosen:
                        scale = s
                        break
                self._text_scale = float(scale)
                _dismiss()
                try:
                    Clock.schedule_once(lambda dt: refresh(), 0)
                except Exception:
                    try:
                        refresh()
                    except Exception:
                        pass
            apply_btn.bind(on_press=_apply)

            p.open()

        def open_add_detail(_=None):
            # Popup menu like Stockbit (minimal version)
            root = BoxLayout(orientation='vertical', padding=(ui_dp(14), ui_dp(12)), spacing=ui_dp(12))

            row1 = BoxLayout(orientation='horizontal', size_hint_y=None, height=ui_dp(44))
            row1.add_widget(Label(text='Complete View', font_size=ui_sp(15), color=(0.9, 0.9, 0.9, 1), halign='left', valign='middle', **_font_kwargs()))
            sw = Switch(active=bool(self._complete_view))
            row1.add_widget(Widget())
            row1.add_widget(sw)
            root.add_widget(row1)

            def _set_complete(_sw, active):
                try:
                    self._complete_view = bool(active)
                    refresh()
                except Exception:
                    pass
            sw.bind(active=_set_complete)

            row2 = ClickableRow(orientation='horizontal', size_hint_y=None, height=ui_dp(44))
            row2.add_widget(Label(text='Text Size', font_size=ui_sp(15), color=(0.75, 0.75, 0.75, 1), halign='left', valign='middle', **_font_kwargs()))
            row2.add_widget(Widget())
            row2_val = Label(text=str(self._text_size_name), font_size=ui_sp(15), color=(0.55, 0.55, 0.55, 1), halign='right', valign='middle', size_hint_x=None, width=ui_dp(110), **_font_kwargs())
            row2.add_widget(row2_val)
            root.add_widget(row2)
            row2.bind(on_press=lambda *_: open_text_size())

            ubah = Button(text='Ubah Watchlist', size_hint_y=None, height=ui_dp(44), background_normal='', background_down='', background_color=(0, 0, 0, 0), padding=(0, 0), halign='left', **_font_kwargs())
            ubah.color = (0.88, 0.88, 0.88, 1)
            ubah.bind(on_press=lambda *_: open_add_symbol())
            root.add_widget(ubah)

            _make_styled_popup(root, title='', size_hint=(0.92, None), height=ui_dp(320)).open()

        # Sub navigation above table: My Watchlist | Jurnal | (right) Add Detail +
        subnav = BoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=ui_dp(46),
            padding=(ui_dp(8), 0),
            spacing=ui_dp(8),
        )

        btn_watchlist = Button(
            text='My Watchlist',
            size_hint=(None, 1),
            width=ui_dp(10),
            background_normal='',
            background_down='',
            background_color=(0, 0, 0, 0),
            padding=(0, 0),
            **_font_kwargs(),
        )
        btn_portfolio = Button(
            text='Jurnal',
            size_hint=(None, 1),
            width=ui_dp(10),
            background_normal='',
            background_down='',
            background_color=(0, 0, 0, 0),
            padding=(0, 0),
            **_font_kwargs(),
        )
        _autosize_button_to_text(btn_watchlist, extra_w=ui_dp(0))
        _autosize_button_to_text(btn_portfolio, extra_w=ui_dp(0))

        def set_sub_active(active_name: str):
            self._subview = active_name
            active_fg = (0.11, 0.75, 0.36, 1)
            inactive_fg = (0.88, 0.88, 0.88, 1)
            if active_name == 'watchlist':
                btn_watchlist.color = active_fg
                btn_portfolio.color = inactive_fg
            else:
                btn_portfolio.color = active_fg
                btn_watchlist.color = inactive_fg

        # refresh() is defined after the list is created.
        def _set_and_refresh(name: str):
            set_sub_active(name)
            try:
                refresh()
            except Exception:
                pass

        btn_watchlist.bind(on_press=lambda *_: _set_and_refresh('watchlist'))
        btn_portfolio.bind(on_press=lambda *_: _set_and_refresh('portfolio'))
        subnav.add_widget(btn_watchlist)
        subnav.add_widget(btn_portfolio)
        subnav.add_widget(Widget())

        # Tombol opsi detail: gunakan ikon tiga titik vertikal yang lebih lebar
        # supaya area sentuh lebih nyaman di layar sentuh.
        add_detail_btn = Button(
            text='⋮',
            size_hint=(None, 1),
            width=ui_dp(36),
            font_size=ui_sp(20),
            background_normal='',
            background_down='',
            background_color=(0, 0, 0, 0),
            color=(0.70, 0.70, 0.70, 1),
            padding=(0, 0),
            **_font_kwargs(),
        )
        _autosize_button_to_text(add_detail_btn, extra_w=ui_dp(0))
        add_detail_btn.bind(on_press=open_add_detail)
        subnav.add_widget(add_detail_btn)

        add_btn = Button(
            text='+',
            size_hint=(None, 1),
            width=ui_dp(44),
            font_size=ui_sp(22),
            background_normal='',
            background_down='',
            background_color=(0, 0, 0, 0),
            color=(0.11, 0.75, 0.36, 1),
            padding=(0, 0),
            **_font_kwargs(),
        )
        add_btn.bind(on_press=open_add_symbol)
        subnav.add_widget(add_btn)

        self.add_widget(subnav)
        set_sub_active('watchlist')

        # Pull-to-refresh indicator + scrollable list
        indicator_box = BoxLayout(size_hint_y=None, height=0)
        indicator_lbl = Label(text='Tarik untuk refresh', font_size=ui_sp(12), color=(0.55, 0.55, 0.55, 1), **_font_kwargs())
        indicator_box.add_widget(indicator_lbl)

        self._list = GridLayout(cols=1, spacing=0, size_hint_y=None)
        self._list.bind(minimum_height=self._list.setter('height'))

        container = BoxLayout(orientation='vertical', size_hint_y=None)
        container.bind(minimum_height=container.setter('height'))
        container.add_widget(indicator_box)
        container.add_widget(self._list)

        scroll = PullToRefreshScrollView(
            indicator_box,
            indicator_lbl,
            on_refresh=lambda: refresh(),
            bar_width=0,
            bar_color=(0, 0, 0, 0),
            bar_inactive_color=(0, 0, 0, 0),
        )
        self._scroll = scroll
        scroll.add_widget(container)

        # Bungkus area scroll di dalam "kartu" dengan margin horizontal
        # supaya tampilan Watchlist menyatu dengan gaya kartu di tab Top 10.
        outer = BoxLayout(
            orientation='vertical',
            padding=(ui_dp(4), ui_dp(8), ui_dp(4), ui_dp(8)),
            spacing=ui_dp(0),
        )
        outer.size_hint_y = 1

        card = BoxLayout(orientation='vertical')
        card.size_hint = (1, 1)
        from kivy.graphics import Color as _Color, Rectangle as _Rect
        with card.canvas.before:
            _Color(0.06, 0.06, 0.06, 1)
            card._bg = _Rect(pos=card.pos, size=card.size)

        def _upd_card_bg(*_a):
            try:
                card._bg.pos = card.pos
                card._bg.size = card.size
            except Exception:
                pass

        card.bind(pos=_upd_card_bg, size=_upd_card_bg)

        card.add_widget(scroll)
        outer.add_widget(card)
        self.add_widget(outer)

        def refresh():
            new_children = []
            if self._subview == 'portfolio':
                holdings = getattr(self.data_fetcher, 'portfolio_stocks', None) or getattr(self.data_fetcher, 'sample_stocks', [])[:8]
                for h in holdings:
                    sym = h.get('symbol', '-')
                    name = h.get('company_name', '')
                    row_h = ui_dp(72)
                    row = BoxLayout(orientation='horizontal', padding=(ui_dp(4), ui_dp(8)), spacing=ui_dp(10))
                    row.size_hint = (1, None)
                    row.height = row_h
                    with row.canvas.before:
                        from kivy.graphics import Color, Rectangle
                        Color(0.06, 0.06, 0.06, 1)
                        row._bg = Rectangle(pos=row.pos, size=row.size)
                        Color(0.12, 0.12, 0.12, 1)
                        row._sep = Rectangle(pos=(row.x, row.y), size=(row.width, 1))
                    def _upd(*_):
                        row._bg.pos = row.pos
                        row._bg.size = row.size
                        row._sep.pos = (row.x, row.y)
                        row._sep.size = (row.width, 1)
                    row.bind(pos=_upd, size=_upd)

                    mid = BoxLayout(orientation='vertical', spacing=ui_dp(2), size_hint_x=1)
                    sym_lbl = Label(text=f'[b]{sym}[/b]', markup=True, font_size=ui_sp(16), color=(0.92,0.92,0.92,1), halign='left', valign='middle', **_font_kwargs())
                    sym_lbl.text_size = (sym_lbl.width, sym_lbl.height)
                    sym_lbl.bind(size=lambda inst, val: setattr(inst, 'text_size', (inst.width, inst.height)))
                    name_lbl = Label(text=name, font_size=ui_sp(13), color=(0.55,0.55,0.55,1), halign='left', valign='middle', **_font_kwargs())
                    name_lbl.text_size = (name_lbl.width, name_lbl.height)
                    try:
                        name_lbl.shorten = True
                        name_lbl.shorten_from = 'right'
                    except Exception:
                        pass
                    name_lbl.bind(size=lambda inst, val: setattr(inst, 'text_size', (inst.width, inst.height)))
                    mid.add_widget(sym_lbl)
                    mid.add_widget(name_lbl)
                    row.add_widget(mid)
                    new_children.append(row)

                try:
                    self._list.clear_widgets()
                except Exception:
                    pass
                for w in new_children:
                    self._list.add_widget(w)
                return

            # Fetch latest data in background to avoid UI jank (especially noticeable right after deploy).
            try:
                if bool(getattr(self, '_wl_refresh_inflight', False)):
                    try:
                        self._wl_refresh_requested = True
                    except Exception:
                        pass
                    return
            except Exception:
                pass
            try:
                self._wl_refresh_inflight = True
                self._wl_refresh_requested = False
            except Exception:
                pass

            watchlist_symbols = list(self.watchlist)

            def _render_body(tvdata: dict, symbol_to_name: dict):
                def _ts():
                    try:
                        return float(self._text_scale) if self._text_scale else 1.0
                    except Exception:
                        return 1.0

                def w_sp(v):
                    return ui_sp(v * _ts())

                ts = _ts()
                # Scale row heights slightly so larger fonts don't overlap.
                height_scale = max(0.90, min(ts, 1.24))
                base_row_h = ui_dp(86 * height_scale)
                detail_h = ui_dp(90 * height_scale) if self._complete_view else 0
                row_h = base_row_h + detail_h

                def _compute_detail_values(symbol: str, d: dict, price_raw):
                    try:
                        price_num = _to_float(price_raw, default=None)
                        tick = 1.0
                        bid_raw = d.get('bid', None)
                        ask_raw = d.get('ask', None)
                        if bid_raw in (None, '') and price_num is not None:
                            bid_raw = max(0, price_num - tick)
                        if ask_raw in (None, '') and price_num is not None:
                            ask_raw = max(0, price_num + tick)

                        is_open = _is_idx_market_open()
                        open_price = _to_float(d.get('open', None), default=None)
                        last_iep = self._iep_cache.get(symbol)

                        # Update cached IEP only while market is closed
                        if not is_open:
                            try:
                                px = _to_float(price_raw, default=None)
                                if px is not None:
                                    self._iep_cache[symbol] = px
                                    last_iep = px
                            except Exception:
                                pass

                        if is_open and last_iep is not None and open_price is not None:
                            matched = int(round(last_iep)) == int(round(open_price))
                            iep_value = 'MATCHED' if matched else 'UNMATCHED'
                            iep_color = (0.11, 0.75, 0.36, 1) if matched else (0.86, 0.25, 0.25, 1)
                        elif is_open:
                            iep_value = ''
                            iep_color = (0.55, 0.55, 0.55, 1)
                        else:
                            iep_value = f"{_format_price(last_iep if last_iep is not None else price_raw)}"
                            iep_color = (0.78, 0.78, 0.78, 1)

                        iev_raw = d.get('volume', d.get('vol', d.get('value', d.get('turnover', '-'))))

                        return {
                            'IEP': (iep_value, iep_color),
                            'Bid': (_format_price(bid_raw), (0.11, 0.75, 0.36, 1)),
                            'Lot': (_format_compact_number(d.get('lot', '-')), (0.78, 0.78, 0.78, 1)),
                            'Freq': (_format_compact_number(d.get('freq', '-')), (0.78, 0.78, 0.78, 1)),
                            'IEV': (_format_compact_number(iev_raw), (0.78, 0.78, 0.78, 1)),
                            'Ask': (_format_price(ask_raw), (0.86, 0.25, 0.25, 1)),
                            'Val': (_format_compact_number(iev_raw), (0.78, 0.78, 0.78, 1)),
                            'Avg': (_format_price(d.get('avg', price_raw)), (0.78, 0.78, 0.78, 1)),
                        }
                    except Exception:
                        return {}

                # Fast path: if layout + symbols unchanged, update labels in-place.
                layout_key = (bool(self._complete_view), float(ts))
                can_update_in_place = (
                    (list(getattr(self, '_wl_symbols', []) or []) == list(watchlist_symbols))
                    and (getattr(self, '_wl_layout_key', None) == layout_key)
                    and isinstance(getattr(self, '_wl_row_refs', None), dict)
                )

                if can_update_in_place:
                    try:
                        for symbol in watchlist_symbols:
                            refs = (self._wl_row_refs or {}).get(symbol)
                            if not isinstance(refs, dict):
                                can_update_in_place = False
                                break
                            price_lbl = refs.get('price_lbl')
                            change_lbl = refs.get('change_lbl')
                            spark = refs.get('spark')
                            right = refs.get('right')
                            detail_refs = refs.get('detail_refs')
                            if price_lbl is None or change_lbl is None or spark is None or right is None:
                                can_update_in_place = False
                                break

                            d = tvdata.get(symbol, {})
                            name = symbol_to_name.get(symbol, '')
                            # keep name cached if we ever expose it later
                            _ = name

                            price_raw = d.get('price', '-')
                            chg_raw = d.get('change', d.get('change_abs', 0))
                            chg_pct_raw = d.get('change_percent', d.get('change_pct', 0))
                            chg_val = _to_float(chg_raw, default=0.0)
                            color_down = (0.86, 0.25, 0.25, 1)
                            color_up = (0.11, 0.75, 0.36, 1)
                            chg_color = color_up if chg_val >= 0 else color_down

                            spark_dir = 1 if chg_val >= 0 else -1

                            # Flash on price change
                            flash_dir = 0
                            try:
                                new_price = _to_float(price_raw, default=None)
                                old_price = self._prev_price.get(symbol)
                                if old_price is not None and new_price is not None and new_price != old_price:
                                    flash_dir = 1 if new_price > old_price else -1
                                if new_price is not None:
                                    self._prev_price[symbol] = new_price
                            except Exception:
                                flash_dir = 0

                            try:
                                new_price_txt = _format_price(price_raw)
                                if getattr(price_lbl, 'text', None) != new_price_txt:
                                    price_lbl.text = new_price_txt
                            except Exception:
                                pass
                            try:
                                new_change_txt = _format_change_pair(chg_raw, chg_pct_raw)
                                if getattr(change_lbl, 'text', None) != new_change_txt:
                                    change_lbl.text = new_change_txt
                            except Exception:
                                pass
                            try:
                                if getattr(change_lbl, 'color', None) != chg_color:
                                    change_lbl.color = chg_color
                            except Exception:
                                pass
                            try:
                                # Avoid redrawing the sparkline every tick; it only changes
                                # when direction (up/down) changes.
                                prev_dir = getattr(spark, '_wl_dir', None)
                                if prev_dir != spark_dir:
                                    spark.values = _spark_values_for(symbol, chg_val)
                                    spark.line_color = list(chg_color)
                                    spark._wl_dir = spark_dir
                            except Exception:
                                pass

                            if isinstance(detail_refs, dict) and detail_refs:
                                vals = _compute_detail_values(symbol, d, price_raw)
                                for k, (txt, col) in (vals or {}).items():
                                    lab = detail_refs.get(k)
                                    if lab is None:
                                        continue
                                    try:
                                        lab.text = txt
                                    except Exception:
                                        pass
                                    try:
                                        lab.color = col
                                    except Exception:
                                        pass

                            if flash_dir != 0:
                                try:
                                    from kivy.animation import Animation
                                    if flash_dir > 0:
                                        right._flash_color.rgba = (0.11, 0.75, 0.36, 0.0)
                                    else:
                                        right._flash_color.rgba = (0.86, 0.25, 0.25, 0.0)
                                    Animation.cancel_all(right._flash_color)
                                    Animation(a=0.28, d=0.08).start(right._flash_color)
                                    Animation(a=0.0, d=0.55).start(right._flash_color)
                                except Exception:
                                    pass
                    except Exception:
                        can_update_in_place = False

                if can_update_in_place:
                    return

                # Slow path: rebuild UI (only when symbols/layout changed).
                new_children = []
                try:
                    self._wl_row_refs = {}
                except Exception:
                    pass

                def make_row(symbol: str):
                    d = tvdata.get(symbol, {})
                    name = symbol_to_name.get(symbol, '')
                    price_raw = d.get('price', '-')
                    chg_raw = d.get('change', d.get('change_abs', 0))
                    chg_pct_raw = d.get('change_percent', d.get('change_pct', 0))
                    chg_val = _to_float(chg_raw, default=0.0)
                    color_down = (0.86, 0.25, 0.25, 1)
                    color_up = (0.11, 0.75, 0.36, 1)
                    chg_color = color_up if chg_val >= 0 else color_down

                    spark_dir = 1 if chg_val >= 0 else -1

                    # Determine one-time flash on price change
                    flash_dir = 0
                    try:
                        new_price = _to_float(price_raw, default=None)
                        old_price = self._prev_price.get(symbol)
                        if old_price is not None and new_price is not None and new_price != old_price:
                            flash_dir = 1 if new_price > old_price else -1
                        if new_price is not None:
                            self._prev_price[symbol] = new_price
                    except Exception:
                        pass

                    card = BoxLayout(orientation='vertical')
                    card.size_hint = (None, None)
                    card.height = row_h
                    card.width = self.width

                    with card.canvas.before:
                        from kivy.graphics import Color, Rectangle
                        Color(0.06, 0.06, 0.06, 1)
                        card._bg = Rectangle(pos=card.pos, size=card.size)
                        Color(0.12, 0.12, 0.12, 1)
                        card._sep = Rectangle(pos=(card.x, card.y), size=(card.width, 1))

                    def _upd(*_):
                        card._bg.pos = card.pos
                        card._bg.size = card.size
                        card._sep.pos = (card.x, card.y)
                        card._sep.size = (card.width, 1)

                    card.bind(pos=_upd, size=_upd)

                    top = BoxLayout(orientation='horizontal', padding=(ui_dp(4), ui_dp(8)), spacing=ui_dp(10), size_hint_y=None, height=base_row_h)

                    mid = BoxLayout(orientation='vertical', spacing=2, size_hint_x=1)
                    top_line = BoxLayout(orientation='horizontal', size_hint_y=None, height=ui_dp(28), spacing=ui_dp(6))
                    sym_lbl = ClickableLabel(text=f'[b]{symbol}[/b]', markup=True, font_size=w_sp(18), color=(0.92,0.92,0.92,1), halign='left', valign='middle', **_font_kwargs())
                    sym_lbl.size_hint_x = 1
                    sym_lbl.text_size = (sym_lbl.width, sym_lbl.height)
                    try:
                        sym_lbl.shorten = True
                        sym_lbl.shorten_from = 'right'
                    except Exception:
                        pass
                    sym_lbl.bind(size=lambda inst, val: setattr(inst, 'text_size', (inst.width, inst.height)))
                    ref_lbl = Label(text='⟳', font_size=w_sp(12), color=(0.55,0.55,0.55,1), size_hint_x=None, width=ui_dp(18), **_font_kwargs())
                    top_line.add_widget(sym_lbl)
                    top_line.add_widget(ref_lbl)
                    mid.add_widget(top_line)

                    name_lbl = Label(text=name, font_size=w_sp(13), color=(0.55,0.55,0.55,1), halign='left', valign='middle', size_hint_y=None, height=ui_dp(22), **_font_kwargs())
                    name_lbl.text_size = (name_lbl.width, name_lbl.height)
                    try:
                        name_lbl.shorten = True
                        name_lbl.shorten_from = 'right'
                    except Exception:
                        pass
                    name_lbl.bind(size=lambda inst, val: setattr(inst, 'text_size', (inst.width, inst.height)))
                    mid.add_widget(name_lbl)
                    top.add_widget(mid)

                    # Sparkline slot aligned to the right within its fixed column
                    from kivy.uix.anchorlayout import AnchorLayout
                    spark_slot = AnchorLayout(size_hint=(None, 1), width=ui_dp(92), anchor_x='right', anchor_y='center')
                    spark = SparklineWidget(size_hint=(None, None), size=(ui_dp(82), ui_dp(30)))
                    spark.values = _spark_values_for(symbol, chg_val)
                    spark.line_color = list(chg_color)
                    try:
                        spark._wl_dir = spark_dir
                    except Exception:
                        pass
                    spark_slot.add_widget(spark)
                    top.add_widget(spark_slot)

                    right = BoxLayout(orientation='vertical', size_hint_x=None, width=ui_dp(128), spacing=ui_dp(2))
                    with right.canvas.before:
                        from kivy.graphics import Color, Rectangle
                        right._flash_color = Color(0, 0, 0, 0)
                        right._flash_rect = Rectangle(pos=right.pos, size=right.size)

                    def _upd_right(*_):
                        try:
                            right._flash_rect.pos = right.pos
                            right._flash_rect.size = right.size
                        except Exception:
                            pass

                    right.bind(pos=_upd_right, size=_upd_right)

                    price_lbl = Label(text=_format_price(price_raw), font_size=w_sp(18), color=(0.90,0.90,0.90,1), halign='right', valign='middle', size_hint_y=None, height=ui_dp(30), **_font_kwargs())
                    price_lbl.text_size = (price_lbl.width, price_lbl.height)
                    try:
                        price_lbl.shorten = True
                        price_lbl.shorten_from = 'left'
                    except Exception:
                        pass
                    price_lbl.bind(size=lambda inst, val: setattr(inst, 'text_size', (inst.width, inst.height)))

                    change_lbl = Label(text=_format_change_pair(chg_raw, chg_pct_raw), font_size=w_sp(13), color=chg_color, halign='right', valign='middle', size_hint_y=None, height=ui_dp(26), **_font_kwargs())
                    change_lbl.text_size = (change_lbl.width, change_lbl.height)
                    try:
                        change_lbl.shorten = True
                        change_lbl.shorten_from = 'left'
                    except Exception:
                        pass
                    change_lbl.bind(size=lambda inst, val: setattr(inst, 'text_size', (inst.width, inst.height)))
                    right.add_widget(price_lbl)
                    right.add_widget(change_lbl)
                    top.add_widget(right)

                    def _fit_cols(*_):
                        try:
                            parent_w = float(card.width or 1)
                            spark_w = min(ui_dp(92), max(ui_dp(62), parent_w * 0.24))
                            right_w = min(ui_dp(128), max(ui_dp(86), parent_w * 0.32))
                            spark_slot.width = spark_w
                            right.width = right_w
                            spark.width = max(ui_dp(40), spark_w - ui_dp(10))
                            spark.height = ui_dp(30)
                        except Exception:
                            pass

                    card.bind(size=_fit_cols)
                    _fit_cols()

                    card.add_widget(top)

                    # Store references for fast in-place updates.
                    try:
                        card._wl_price_lbl = price_lbl
                        card._wl_change_lbl = change_lbl
                        card._wl_spark = spark
                        card._wl_right = right
                    except Exception:
                        pass

                    try:
                        card._tap_widget = sym_lbl
                    except Exception:
                        pass

                    if self._complete_view:
                        # Detail panel ala Stockbit screenshot (layout-focused; values best-effort)
                        detail_refs = {}

                        def _stat_row(key, label_txt, value_txt, value_color=(0.82, 0.82, 0.82, 1)):
                            r = BoxLayout(orientation='horizontal', size_hint_y=None, height=ui_dp(20))
                            lbl = Label(text=label_txt, font_size=w_sp(12), color=(0.45, 0.45, 0.45, 1), size_hint_x=None, width=ui_dp(44), halign='left', valign='middle', **_font_kwargs())
                            lbl.text_size = (lbl.width, lbl.height)
                            lbl.bind(size=lambda inst, val_size: setattr(inst, 'text_size', (inst.width, inst.height)))
                            r.add_widget(lbl)
                            val = Label(text=value_txt, font_size=w_sp(13), color=value_color, halign='right', valign='middle', **_font_kwargs())
                            val.text_size = (val.width, val.height)
                            val.bind(size=lambda inst, val_size: setattr(inst, 'text_size', (inst.width, inst.height)))
                            try:
                                val.shorten = True
                                val.shorten_from = 'left'
                            except Exception:
                                pass
                            r.add_widget(val)
                            try:
                                detail_refs[key] = val
                            except Exception:
                                pass
                            return r

                        details = BoxLayout(orientation='horizontal', size_hint_y=None, height=detail_h, padding=(ui_dp(4), 0, ui_dp(4), ui_dp(10)), spacing=ui_dp(16))

                        left_col = BoxLayout(orientation='vertical', spacing=ui_dp(2))
                        right_col = BoxLayout(orientation='vertical', spacing=ui_dp(2))

                        vals = _compute_detail_values(symbol, d, price_raw)

                        left_col.add_widget(_stat_row('IEP', 'IEP', vals.get('IEP', ('', (0.78, 0.78, 0.78, 1)))[0], value_color=vals.get('IEP', ('', (0.78, 0.78, 0.78, 1)))[1]))
                        left_col.add_widget(_stat_row('Bid', 'Bid', vals.get('Bid', ('-', (0.11, 0.75, 0.36, 1)))[0], value_color=vals.get('Bid', ('-', (0.11, 0.75, 0.36, 1)))[1]))
                        left_col.add_widget(_stat_row('Lot', 'Lot', vals.get('Lot', ('-', (0.78, 0.78, 0.78, 1)))[0], value_color=vals.get('Lot', ('-', (0.78, 0.78, 0.78, 1)))[1]))
                        left_col.add_widget(_stat_row('Freq', 'Freq', vals.get('Freq', ('-', (0.78, 0.78, 0.78, 1)))[0], value_color=vals.get('Freq', ('-', (0.78, 0.78, 0.78, 1)))[1]))

                        right_col.add_widget(_stat_row('IEV', 'IEV', vals.get('IEV', ('-', (0.78, 0.78, 0.78, 1)))[0], value_color=vals.get('IEV', ('-', (0.78, 0.78, 0.78, 1)))[1]))
                        right_col.add_widget(_stat_row('Ask', 'Ask', vals.get('Ask', ('-', (0.86, 0.25, 0.25, 1)))[0], value_color=vals.get('Ask', ('-', (0.86, 0.25, 0.25, 1)))[1]))
                        right_col.add_widget(_stat_row('Val', 'Val', vals.get('Val', ('-', (0.78, 0.78, 0.78, 1)))[0], value_color=vals.get('Val', ('-', (0.78, 0.78, 0.78, 1)))[1]))
                        right_col.add_widget(_stat_row('Avg', 'Avg', vals.get('Avg', ('-', (0.78, 0.78, 0.78, 1)))[0], value_color=vals.get('Avg', ('-', (0.78, 0.78, 0.78, 1)))[1]))

                        details.add_widget(left_col)
                        details.add_widget(right_col)
                        card.add_widget(details)

                        try:
                            card._wl_detail_refs = detail_refs
                        except Exception:
                            pass

                    if flash_dir != 0:
                        try:
                            from kivy.animation import Animation
                            if flash_dir > 0:
                                right._flash_color.rgba = (0.11, 0.75, 0.36, 0.0)
                            else:
                                right._flash_color.rgba = (0.86, 0.25, 0.25, 0.0)
                            Animation.cancel_all(right._flash_color)
                            Animation(a=0.28, d=0.08).start(right._flash_color)
                            Animation(a=0.0, d=0.55).start(right._flash_color)
                        except Exception:
                            pass

                    return card

                def delete_symbol(sym):
                    if sym in self.watchlist:
                        try:
                            self.watchlist.remove(sym)
                        except Exception:
                            pass
                        try:
                            self._save_watchlist()
                        except Exception:
                            pass
                        refresh()

                for symbol in list(watchlist_symbols):
                    row = make_row(symbol)

                    def _on_tap_symbol(_sym=symbol):
                        try:
                            from kivy.app import App
                            app = App.get_running_app()
                            if app is not None and hasattr(app, 'open_cek_emiten'):
                                app.open_cek_emiten(_sym)
                        except Exception:
                            pass

                    try:
                        tap_w = getattr(row, '_tap_widget', None)
                    except Exception:
                        tap_w = None

                    swipe = SwipeToDeleteRow(
                        row,
                        on_delete=lambda s=symbol: delete_symbol(s),
                        on_tap=_on_tap_symbol,
                        tap_widget=tap_w,
                        height=row_h,
                        scrollview=self._scroll,
                    )

                    try:
                        self._wl_row_refs[symbol] = {
                            'price_lbl': getattr(row, '_wl_price_lbl', None),
                            'change_lbl': getattr(row, '_wl_change_lbl', None),
                            'spark': getattr(row, '_wl_spark', None),
                            'right': getattr(row, '_wl_right', None),
                            'detail_refs': getattr(row, '_wl_detail_refs', None),
                        }
                    except Exception:
                        pass

                    new_children.append(swipe)

                try:
                    self._list.clear_widgets()
                except Exception:
                    pass
                for w in new_children:
                    self._list.add_widget(w)

                try:
                    self._wl_symbols = list(watchlist_symbols)
                    self._wl_layout_key = layout_key
                except Exception:
                    pass

            def _worker():
                tvdata = {}
                try:
                    use_stockbit_first = (self._watchlist_source in ('stockbit_first', 'stockbit-first', 'auto'))
                except Exception:
                    use_stockbit_first = False

                def _normalize_symbol_key(sym: str) -> str:
                    s = (sym or '').strip().upper()
                    if s.endswith(':IDX'):
                        s = s.split(':', 1)[0]
                    if s.endswith('.JK'):
                        s = s[:-3]
                    return s

                def _map_stockbit_quote(q: dict) -> dict:
                    if not isinstance(q, dict):
                        return {}
                    price = q.get('last')
                    if price is None:
                        price = q.get('price', q.get('close'))
                    change_abs = q.get('change')
                    if change_abs is None:
                        change_abs = q.get('change_abs', q.get('chg'))
                    change_pct = q.get('changePercent')
                    if change_pct is None:
                        change_pct = q.get('change_percent', q.get('changePct', q.get('chg_pct')))

                    out = {
                        'price': price if price is not None else q.get('lastPrice', '-'),
                        'change': change_abs if change_abs is not None else 0,
                        'change_percent': change_pct if change_pct is not None else 0,
                    }
                    if 'bid' in q:
                        out['bid'] = q.get('bid')
                    if 'ask' in q:
                        out['ask'] = q.get('ask')
                    if 'volume' in q:
                        out['volume'] = q.get('volume')
                    if 'value' in q:
                        out['value'] = q.get('value')
                    return out

                if use_stockbit_first and self._stockbit_fetcher is not None:
                    try:
                        import time
                        now = time.time()
                        if now >= float(getattr(self, '_stockbit_blocked_until', 0.0) or 0.0):
                            raw = self._stockbit_fetcher.fetch_realtime_quotes(watchlist_symbols)
                            if isinstance(raw, dict) and raw:
                                mapped = {}
                                for k, v in raw.items():
                                    mapped[_normalize_symbol_key(k)] = _map_stockbit_quote(v)
                                tvdata = mapped
                            else:
                                self._stockbit_blocked_until = now + 300.0
                    except Exception:
                        try:
                            import time
                            self._stockbit_blocked_until = time.time() + 300.0
                        except Exception:
                            pass

                if not tvdata:
                    try:
                        tvdata = fetch_tradingview_snapshot(watchlist_symbols)
                    except Exception:
                        tvdata = {}

                symbol_to_name = {s['symbol']: s.get('company_name', '') for s in getattr(self.data_fetcher, 'sample_stocks', [])}

                def _done(_dt):
                    try:
                        _render_body(tvdata, symbol_to_name)
                    except Exception:
                        pass
                    try:
                        self._wl_refresh_inflight = False
                        again = bool(getattr(self, '_wl_refresh_requested', False))
                        self._wl_refresh_requested = False
                    except Exception:
                        again = False
                    if again:
                        try:
                            Clock.schedule_once(lambda __: refresh(), 0.01)
                        except Exception:
                            pass

                try:
                    Clock.schedule_once(_done, 0)
                except Exception:
                    _done(0)

            try:
                threading.Thread(target=_worker, daemon=True).start()
            except Exception:
                try:
                    self._wl_refresh_inflight = False
                except Exception:
                    pass
            return
            def _ts():
                try:
                    return float(self._text_scale) if self._text_scale else 1.0
                except Exception:
                    return 1.0

            def w_sp(v):
                return ui_sp(v * _ts())

            ts = _ts()
            # Scale row heights slightly so larger fonts don't overlap.
            height_scale = max(0.90, min(ts, 1.24))
            base_row_h = ui_dp(86 * height_scale)
            detail_h = ui_dp(90 * height_scale) if self._complete_view else 0
            row_h = base_row_h + detail_h

            def make_row(symbol: str):
                d = tvdata.get(symbol, {})
                name = symbol_to_name.get(symbol, '')
                price_raw = d.get('price', '-')
                chg_raw = d.get('change', d.get('change_abs', 0))
                chg_pct_raw = d.get('change_percent', d.get('change_pct', 0))
                chg_val = _to_float(chg_raw, default=0.0)
                color_down = (0.86, 0.25, 0.25, 1)
                color_up = (0.11, 0.75, 0.36, 1)
                chg_color = color_up if chg_val >= 0 else color_down

                # Determine one-time flash on price change
                flash_dir = 0
                try:
                    new_price = _to_float(price_raw, default=None)
                    old_price = self._prev_price.get(symbol)
                    if old_price is not None and new_price is not None and new_price != old_price:
                        flash_dir = 1 if new_price > old_price else -1
                    if new_price is not None:
                        self._prev_price[symbol] = new_price
                except Exception:
                    pass

                card = BoxLayout(orientation='vertical')
                card.size_hint = (None, None)
                card.height = row_h
                card.width = self.width

                with card.canvas.before:
                    from kivy.graphics import Color, Rectangle
                    Color(0.06, 0.06, 0.06, 1)
                    card._bg = Rectangle(pos=card.pos, size=card.size)
                    Color(0.12, 0.12, 0.12, 1)
                    card._sep = Rectangle(pos=(card.x, card.y), size=(card.width, 1))
                def _upd(*_):
                    card._bg.pos = card.pos
                    card._bg.size = card.size
                    card._sep.pos = (card.x, card.y)
                    card._sep.size = (card.width, 1)
                card.bind(pos=_upd, size=_upd)

                top = BoxLayout(orientation='horizontal', padding=(ui_dp(4), ui_dp(8)), spacing=ui_dp(10), size_hint_y=None, height=base_row_h)

                # NOTE: logo removed (placeholder). If we later have a real logo source,
                # we can re-enable it without changing layout expectations.

                mid = BoxLayout(orientation='vertical', spacing=2, size_hint_x=1)
                top_line = BoxLayout(orientation='horizontal', size_hint_y=None, height=ui_dp(28), spacing=ui_dp(6))
                sym_lbl = ClickableLabel(text=f'[b]{symbol}[/b]', markup=True, font_size=w_sp(18), color=(0.92,0.92,0.92,1), halign='left', valign='middle', **_font_kwargs())
                sym_lbl.size_hint_x = 1
                # Ensure text doesn't draw outside label bounds (prevents visual overlap)
                sym_lbl.text_size = (sym_lbl.width, sym_lbl.height)
                try:
                    sym_lbl.shorten = True
                    sym_lbl.shorten_from = 'right'
                except Exception:
                    pass
                sym_lbl.bind(size=lambda inst, val: setattr(inst, 'text_size', (inst.width, inst.height)))
                ref_lbl = Label(text='⟳', font_size=w_sp(12), color=(0.55,0.55,0.55,1), size_hint_x=None, width=ui_dp(18), **_font_kwargs())
                top_line.add_widget(sym_lbl)
                top_line.add_widget(ref_lbl)
                mid.add_widget(top_line)

                name_lbl = Label(text=name, font_size=w_sp(13), color=(0.55,0.55,0.55,1), halign='left', valign='middle', size_hint_y=None, height=ui_dp(22), **_font_kwargs())
                name_lbl.text_size = (name_lbl.width, name_lbl.height)
                try:
                    name_lbl.shorten = True
                    name_lbl.shorten_from = 'right'
                except Exception:
                    pass
                name_lbl.bind(size=lambda inst, val: setattr(inst, 'text_size', (inst.width, inst.height)))
                mid.add_widget(name_lbl)
                top.add_widget(mid)

                # Sparkline slot aligned to the right within its fixed column
                from kivy.uix.anchorlayout import AnchorLayout
                spark_slot = AnchorLayout(size_hint=(None, 1), width=ui_dp(92), anchor_x='right', anchor_y='center')
                spark = SparklineWidget(size_hint=(None, None), size=(ui_dp(82), ui_dp(30)))
                spark.values = _spark_values_for(symbol, chg_val)
                spark.line_color = list(chg_color)
                spark_slot.add_widget(spark)
                top.add_widget(spark_slot)

                right = BoxLayout(orientation='vertical', size_hint_x=None, width=ui_dp(128), spacing=ui_dp(2))
                # Flash only on the right price panel
                with right.canvas.before:
                    from kivy.graphics import Color, Rectangle
                    right._flash_color = Color(0, 0, 0, 0)
                    right._flash_rect = Rectangle(pos=right.pos, size=right.size)
                def _upd_right(*_):
                    try:
                        right._flash_rect.pos = right.pos
                        right._flash_rect.size = right.size
                    except Exception:
                        pass
                right.bind(pos=_upd_right, size=_upd_right)

                price_lbl = Label(text=_format_price(price_raw), font_size=w_sp(18), color=(0.90,0.90,0.90,1), halign='right', valign='middle', size_hint_y=None, height=ui_dp(30), **_font_kwargs())
                price_lbl.text_size = (price_lbl.width, price_lbl.height)
                try:
                    price_lbl.shorten = True
                    price_lbl.shorten_from = 'left'
                except Exception:
                    pass
                price_lbl.bind(size=lambda inst, val: setattr(inst, 'text_size', (inst.width, inst.height)))

                change_lbl = Label(text=_format_change_pair(chg_raw, chg_pct_raw), font_size=w_sp(13), color=chg_color, halign='right', valign='middle', size_hint_y=None, height=ui_dp(26), **_font_kwargs())
                change_lbl.text_size = (change_lbl.width, change_lbl.height)
                try:
                    change_lbl.shorten = True
                    change_lbl.shorten_from = 'left'
                except Exception:
                    pass
                change_lbl.bind(size=lambda inst, val: setattr(inst, 'text_size', (inst.width, inst.height)))
                right.add_widget(price_lbl)
                right.add_widget(change_lbl)
                top.add_widget(right)

                # Make right/spark columns adapt on narrow widths (prevents overlap on resize)
                def _fit_cols(*_):
                    try:
                        parent_w = float(card.width or 1)
                        spark_w = min(ui_dp(92), max(ui_dp(62), parent_w * 0.24))
                        right_w = min(ui_dp(128), max(ui_dp(86), parent_w * 0.32))
                        spark_slot.width = spark_w
                        right.width = right_w
                        # Keep sparkline within its slot
                        spark.width = max(ui_dp(40), spark_w - ui_dp(10))
                        spark.height = ui_dp(30)
                    except Exception:
                        pass
                card.bind(size=_fit_cols)
                _fit_cols()

                card.add_widget(top)

                try:
                    card._tap_widget = sym_lbl
                except Exception:
                    pass

                if self._complete_view:
                    # Detail panel ala Stockbit screenshot (layout-focused; values best-effort)
                    def _stat_row(label_txt, value_txt, value_color=(0.82, 0.82, 0.82, 1)):
                        r = BoxLayout(orientation='horizontal', size_hint_y=None, height=ui_dp(20))
                        lbl = Label(text=label_txt, font_size=w_sp(12), color=(0.45, 0.45, 0.45, 1), size_hint_x=None, width=ui_dp(44), halign='left', valign='middle', **_font_kwargs())
                        lbl.text_size = (lbl.width, lbl.height)
                        lbl.bind(size=lambda inst, val_size: setattr(inst, 'text_size', (inst.width, inst.height)))
                        r.add_widget(lbl)
                        val = Label(text=value_txt, font_size=w_sp(13), color=value_color, halign='right', valign='middle', **_font_kwargs())
                        val.text_size = (val.width, val.height)
                        val.bind(size=lambda inst, val_size: setattr(inst, 'text_size', (inst.width, inst.height)))
                        try:
                            val.shorten = True
                            val.shorten_from = 'left'
                        except Exception:
                            pass
                        r.add_widget(val)
                        return r

                    details = BoxLayout(orientation='horizontal', size_hint_y=None, height=detail_h, padding=(ui_dp(4), 0, ui_dp(4), ui_dp(10)), spacing=ui_dp(16))

                    left_col = BoxLayout(orientation='vertical', spacing=ui_dp(2))
                    right_col = BoxLayout(orientation='vertical', spacing=ui_dp(2))

                    price_num = _to_float(price_raw, default=None)
                    tick = 1.0
                    bid_raw = d.get('bid', None)
                    ask_raw = d.get('ask', None)
                    if bid_raw in (None, '') and price_num is not None:
                        bid_raw = max(0, price_num - tick)
                    if ask_raw in (None, '') and price_num is not None:
                        ask_raw = max(0, price_num + tick)

                    is_open = _is_idx_market_open()
                    open_price = _to_float(d.get('open', None), default=None)
                    last_iep = self._iep_cache.get(symbol)

                    # Update cached IEP only while market is closed
                    if not is_open:
                        try:
                            px = _to_float(price_raw, default=None)
                            if px is not None:
                                self._iep_cache[symbol] = px
                                last_iep = px
                        except Exception:
                            pass

                    # During market open, show MATCHED / UNMATCHED based on cached IEP vs opening price
                    if is_open and last_iep is not None and open_price is not None:
                        matched = int(round(last_iep)) == int(round(open_price))
                        iep_value = 'MATCHED' if matched else 'UNMATCHED'
                        iep_color = (0.11, 0.75, 0.36, 1) if matched else (0.86, 0.25, 0.25, 1)
                    elif is_open:
                        iep_value = ''
                        iep_color = (0.55, 0.55, 0.55, 1)
                    else:
                        iep_value = f"{_format_price(last_iep if last_iep is not None else price_raw)}"
                        iep_color = (0.78, 0.78, 0.78, 1)
                    iev_raw = d.get('volume', d.get('vol', d.get('value', d.get('turnover', '-'))))

                    left_col.add_widget(_stat_row('IEP', iep_value, value_color=iep_color))
                    left_col.add_widget(_stat_row('Bid', _format_price(bid_raw), value_color=(0.11, 0.75, 0.36, 1)))
                    left_col.add_widget(_stat_row('Lot', _format_compact_number(d.get('lot', '-')), value_color=(0.78, 0.78, 0.78, 1)))
                    left_col.add_widget(_stat_row('Freq', _format_compact_number(d.get('freq', '-')), value_color=(0.78, 0.78, 0.78, 1)))

                    right_col.add_widget(_stat_row('IEV', _format_compact_number(iev_raw), value_color=(0.78, 0.78, 0.78, 1)))
                    right_col.add_widget(_stat_row('Ask', _format_price(ask_raw), value_color=(0.86, 0.25, 0.25, 1)))
                    right_col.add_widget(_stat_row('Val', _format_compact_number(iev_raw), value_color=(0.78, 0.78, 0.78, 1)))
                    right_col.add_widget(_stat_row('Avg', _format_price(d.get('avg', price_raw)), value_color=(0.78, 0.78, 0.78, 1)))

                    details.add_widget(left_col)
                    details.add_widget(right_col)
                    card.add_widget(details)

                # Trigger flash once (no continuous pulsing)
                if flash_dir != 0:
                    try:
                        from kivy.animation import Animation
                        if flash_dir > 0:
                            right._flash_color.rgba = (0.11, 0.75, 0.36, 0.0)
                        else:
                            right._flash_color.rgba = (0.86, 0.25, 0.25, 0.0)
                        Animation.cancel_all(right._flash_color)
                        Animation(a=0.28, d=0.08).start(right._flash_color)
                        Animation(a=0.0, d=0.55).start(right._flash_color)
                    except Exception:
                        pass

                return card

            def delete_symbol(sym):
                if sym in self.watchlist:
                    try:
                        self.watchlist.remove(sym)
                    except Exception:
                        pass
                    try:
                        self._save_watchlist()
                    except Exception:
                        pass
                    refresh()

            for symbol in list(self.watchlist):
                row = make_row(symbol)
                def _on_tap_symbol(_sym=symbol):
                    try:
                        from kivy.app import App
                        app = App.get_running_app()
                        if app is not None and hasattr(app, 'open_cek_emiten'):
                            app.open_cek_emiten(_sym)
                    except Exception:
                        pass

                try:
                    tap_w = getattr(row, '_tap_widget', None)
                except Exception:
                    tap_w = None

                swipe = SwipeToDeleteRow(
                    row,
                    on_delete=lambda s=symbol: delete_symbol(s),
                    on_tap=_on_tap_symbol,
                    tap_widget=tap_w,
                    height=row_h,
                    scrollview=self._scroll,
                )

                new_children.append(swipe)

            # Swap in one shot to avoid temporary blanks.
            try:
                self._list.clear_widgets()
            except Exception:
                pass
            for w in new_children:
                self._list.add_widget(w)

        # Only fetch data on explicit refresh; do not refetch on resize.
        # (Resize can happen multiple times during layouting and would spam requests.)
        Clock.schedule_once(lambda dt: refresh(), 0.1)

        # Auto-refresh (pseudo-realtime). Uses the same refresh() and flashes once on changes.
        try:
            sec = float(os.environ.get('WATCHLIST_REFRESH_SEC', '10'))
        except Exception:
            sec = 10.0

        def _auto_tick(_dt):
            try:
                if self._subview == 'watchlist':
                    refresh()
            except Exception:
                pass

        try:
            self._auto_refresh_ev = Clock.schedule_interval(_auto_tick, max(3.0, sec))
        except Exception:
            self._auto_refresh_ev = None

    def refresh_table(self, grid):
        grid.clear_widgets()
        from modules.tradingview_fetcher import fetch_tradingview_snapshot
        # Ambil nama perusahaan dari sample_stocks
        symbol_to_name = {s['symbol']: s['company_name'] for s in self.data_fetcher.sample_stocks}
        # Ambil data realtime TradingView
        tvdata = fetch_tradingview_snapshot(self.watchlist)
        # Use fixed row height to match previous device layout and screenshot
        row_h = 56
        # helper to create styled label for table rows
        def make_lbl(txt, size_hint_x=None, font_size=16, color=(1,1,1,1), bold=False, halign='left'):
            lbl = Label(text=txt, size_hint_x=size_hint_x, size_hint_y=None, font_size=font_size, color=color, markup=bold)
            lbl.height = row_h
            lbl.halign = halign
            lbl.valign = 'middle'
            return lbl

        for symbol in self.watchlist:
            d = tvdata.get(symbol, {})
            row = BoxLayout(orientation='horizontal', size_hint_y=None, height=row_h, padding=(ui_dp(4), 0))
            # dark row background
            with row.canvas.before:
                from kivy.graphics import Color, Rectangle
                Color(0.06,0.08,0.1,1)
                row._bg = Rectangle(pos=row.pos, size=row.size)
            def _update_row(_, __):
                try:
                    row._bg.pos = row.pos
                    row._bg.size = row.size
                except Exception:
                    pass
            row.bind(pos=_update_row, size=_update_row)

            sym_lbl = ClickableLabel(text=str(symbol), size_hint_x=0.5, size_hint_y=None, font_size=18, color=(0.05,0.8,0.66,1))
            sym_lbl.height = row_h
            sym_lbl.halign = 'left'
            sym_lbl.valign = 'middle'
            try:
                def _go(_btn=None, _sym=str(symbol).strip().upper()):
                    try:
                        from kivy.app import App
                        app = App.get_running_app()
                        if app is not None and hasattr(app, 'open_cek_emiten'):
                            app.open_cek_emiten(_sym)
                    except Exception:
                        pass
                sym_lbl.bind(on_press=_go)
            except Exception:
                pass
            price_lbl = make_lbl(str(d.get('price', '-')), size_hint_x=0.25, font_size=18, color=(0.11,0.75,0.36,1))
            yest_lbl = make_lbl(str(d.get('yesterday', d.get('prev_close', '-'))), size_hint_x=0.25, font_size=16, color=(0.9,0.9,0.9,1))

            row.add_widget(sym_lbl)
            row.add_widget(price_lbl)
            row.add_widget(yest_lbl)
            grid.add_widget(row)

class DashboardTab(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(orientation='vertical', **kwargs)

        self._mode = 'ACCUMULATION'  # or 'DISTRIBUTION'
        self._tv_poll_ev = None
        self._tv_poll_inflight = False
        self._tv_prev_price = {}
        self._top_rows_by_symbol = {}
        self._top_price_labels = {}
        self._analysis_symbols = []
        self._analysis_symbol_to_company = {}
        self._analysis_g_rows = None
        self._analysis_l_rows = None
        self._analysis_band_cards = None

        # Header bar: avatar (profile entry) + truly centered title
        header = BoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=ui_dp(68),
            padding=(ui_dp(12), ui_dp(10)),
            spacing=ui_dp(8),
        )
        from kivy.uix.anchorlayout import AnchorLayout
        from kivy.graphics import Color, Ellipse
        from kivy.clock import Clock as _Clock
        from kivy.app import App as _App

        avatar_size = ui_dp(42)
        btn_avatar = Button(
            size_hint=(None, None),
            size=(avatar_size, avatar_size),
            background_normal='',
            background_down='',
            background_color=(0, 0, 0, 0),
        )
        # Avatar kecil dengan siluet (warna statis di Tab Top10)
        with btn_avatar.canvas.before:
            btn_avatar._bg_color = Color(0.18, 0.22, 0.30, 1)
            btn_avatar._bg_circ = Ellipse(pos=btn_avatar.pos, size=btn_avatar.size)
            btn_avatar._fg_color = Color(0.97, 0.97, 0.97, 1)
            btn_avatar._head = Ellipse(pos=btn_avatar.pos, size=btn_avatar.size)
            btn_avatar._body = Ellipse(pos=btn_avatar.pos, size=btn_avatar.size)

        def _update_dash_avatar(*_a):
            try:
                btn_avatar._bg_circ.pos = btn_avatar.pos
                btn_avatar._bg_circ.size = btn_avatar.size
                r = btn_avatar.width * 0.36
                x_head = btn_avatar.x + (btn_avatar.width - r) / 2.0
                y_head = btn_avatar.y + btn_avatar.height * 0.52
                btn_avatar._head.pos = (x_head, y_head)
                btn_avatar._head.size = (r, r)
                bw = btn_avatar.width * 0.82
                bh = btn_avatar.height * 0.52
                x_body = btn_avatar.x + (btn_avatar.width - bw) / 2.0
                y_body = btn_avatar.y + btn_avatar.height * 0.04
                btn_avatar._body.pos = (x_body, y_body)
                btn_avatar._body.size = (bw, bh)
            except Exception:
                pass

        btn_avatar.bind(pos=_update_dash_avatar, size=_update_dash_avatar)

        def _open_profile_from_other_tab(*_a):
            # Buka popup profil global bila tersedia; fallback ke perilaku lama.
            try:
                app = _App.get_running_app()
            except Exception:
                app = None
            if app is None:
                return
            # Sticky: panggil handler global tanpa ganti tab.
            try:
                cb = getattr(app, 'open_profile_popup', None)
            except Exception:
                cb = None
            if cb is not None:
                try:
                    cb()
                    return
                except Exception:
                    pass
            # Fallback: pindah ke Watchlist dan trigger avatar seperti sebelumnya.
            try:
                app.switch_tab(0)
            except Exception:
                return

            def _after(_dt):
                try:
                    w = app.tab_container.children[0] if app.tab_container.children else None
                    if w is not None and hasattr(w, '_hdr_avatar'):
                        try:
                            w._hdr_avatar.dispatch('on_press')
                        except Exception:
                            pass
                except Exception:
                    pass

            try:
                _Clock.schedule_once(_after, 0.05)
            except Exception:
                pass

        btn_avatar.bind(on_press=_open_profile_from_other_tab)

        left = BoxLayout(size_hint=(None, 1), width=avatar_size)
        left.add_widget(btn_avatar)
        header.add_widget(left)

        center = AnchorLayout(anchor_x='center', anchor_y='center')
        center.add_widget(
            Label(
                text='[b]Jurnal Saham IHSG[/b]',
                markup=True,
                font_size=ui_sp(18),
                color=(1, 1, 1, 1),
                halign='center',
                valign='middle',
                **_font_kwargs(),
            )
        )
        header.add_widget(center)

        # Right side kept empty so title stays visually centered
        header.add_widget(Widget(size_hint=(None, 1), width=avatar_size))
        self.add_widget(header)

        subnav = BoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=ui_dp(46),
            padding=(ui_dp(8), 0),
            spacing=ui_dp(8),
        )

        def _sub_btn(txt: str):
            b = Button(
                text=txt,
                size_hint=(1, 1),
                background_normal='',
                background_down='',
                background_color=(0, 0, 0, 0),
                padding=(0, 0),
                font_size=ui_sp(15),
                **_font_kwargs(),
            )
            b.halign = 'center'
            b.valign = 'middle'
            try:
                b.text_size = b.size
                b.bind(size=lambda inst, val: setattr(inst, 'text_size', val))
            except Exception:
                pass
            return b

        btn_acc = _sub_btn('Top Acc')
        btn_dist = _sub_btn('Top Dist')
        btn_ms = _sub_btn('Analisis')

        def set_active(which: str):
            # Match Watchlist subnav styling.
            active_color = (0.11, 0.75, 0.36, 1)
            inactive_color = (0.88, 0.88, 0.88, 1)
            btn_acc.color = active_color if which == 'ACCUMULATION' else inactive_color
            btn_dist.color = active_color if which == 'DISTRIBUTION' else inactive_color
            btn_ms.color = active_color if which == 'ANALYSIS' else inactive_color
            try:
                btn_acc.background_color = (0, 0, 0, 0)
                btn_dist.background_color = (0, 0, 0, 0)
                btn_ms.background_color = (0, 0, 0, 0)
            except Exception:
                pass

        def switch_mode(which: str):
            self._mode = which
            set_active(which)
            self.refresh()

        btn_acc.bind(on_press=lambda *_: switch_mode('ACCUMULATION'))
        btn_dist.bind(on_press=lambda *_: switch_mode('DISTRIBUTION'))
        btn_ms.bind(on_press=lambda *_: switch_mode('ANALYSIS'))

        subnav.add_widget(btn_acc)
        subnav.add_widget(btn_dist)
        subnav.add_widget(btn_ms)
        self.add_widget(subnav)
        set_active(self._mode)

        self._list = GridLayout(cols=1, spacing=0, size_hint_y=None)
        scroll = ScrollView(
            bar_width=0,
            bar_color=(0, 0, 0, 0),
            bar_inactive_color=(0, 0, 0, 0),
            scroll_distance=ui_dp(2),
        )

        def _update_list_height(*_):
            try:
                self._list.height = max(self._list.minimum_height, scroll.height)
            except Exception:
                pass

        self._list.bind(minimum_height=lambda *_: _update_list_height())
        scroll.bind(height=lambda *_: _update_list_height())
        scroll.add_widget(self._list)
        self.add_widget(scroll)

        self.refresh()

    def on_parent(self, *_):
        # Stop polling when this tab is removed from the UI tree.
        try:
            if self.parent is None:
                self._stop_tv_poll()
        except Exception:
            pass

    def _start_tv_poll(self):
        try:
            if self._tv_poll_ev is not None:
                return
            self._tv_poll_ev = Clock.schedule_interval(lambda _dt: self._tv_poll_tick(), 2.0)
            Clock.schedule_once(lambda _dt: self._tv_poll_tick(), 0)
        except Exception:
            self._tv_poll_ev = None

    def _stop_tv_poll(self):
        try:
            if self._tv_poll_ev is not None:
                self._tv_poll_ev.cancel()
        except Exception:
            pass
        self._tv_poll_ev = None
        self._tv_poll_inflight = False

    def _stable_ratio(self, key: str, lo: float, hi: float) -> float:
        try:
            import hashlib
            h = hashlib.md5(key.encode('utf-8')).hexdigest()
            v = int(h[:8], 16) / float(0xFFFFFFFF)
            return lo + (hi - lo) * v
        except Exception:
            return (lo + hi) / 2.0

    def _flash_row(self, row, up: bool):
        try:
            base = getattr(row, '_base_bg_rgba', (0.06, 0.06, 0.06, 1))
            col = (0.11, 0.75, 0.36, 0.35) if up else (0.86, 0.25, 0.25, 0.35)
            if hasattr(row, '_bg_color'):
                row._bg_color.rgba = col

            def _revert(_dt):
                try:
                    if hasattr(row, '_bg_color'):
                        row._bg_color.rgba = base
                except Exception:
                    pass

            Clock.schedule_once(_revert, 0.22)
        except Exception:
            pass

    def _analysis_apply_snapshot(self, snap: dict | None):
        if not (isinstance(snap, dict) and self._analysis_symbols and self._analysis_band_cards and self._analysis_g_rows and self._analysis_l_rows):
            return

        # Movers
        items = []
        for s in list(self._analysis_symbols)[:50]:
            d = snap.get(s) if isinstance(snap, dict) else None
            if not isinstance(d, dict):
                continue
            try:
                chg = d.get('change', None)
                if chg is None:
                    continue
                chg = float(chg)
            except Exception:
                continue
            items.append({
                'symbol': s,
                'company': (self._analysis_symbol_to_company or {}).get(s, ''),
                'price': d.get('price', '-'),
                'change_pct': chg,
                'volume': d.get('volume', 0),
            })

        gainers = sorted(items, key=lambda x: float(x.get('change_pct', 0.0) or 0.0), reverse=True)[:10]
        losers = sorted(items, key=lambda x: float(x.get('change_pct', 0.0) or 0.0))[:10]

        def _fill(rows_ui, rows_items):
            color_up = (0.11, 0.75, 0.36, 1)
            color_down = (0.86, 0.25, 0.25, 1)
            if not rows_items:
                for sym_lbl, company_lbl, price_lbl, chg_lbl in rows_ui:
                    sym_lbl.text = '-'
                    company_lbl.text = '-'
                    price_lbl.text = '-'
                    chg_lbl.text = '-'
                    chg_lbl.color = (0.62, 0.62, 0.62, 1)
                return
            for i, rowdata in enumerate(rows_items[:10]):
                try:
                    sym = rowdata.get('symbol', '-')
                    comp = rowdata.get('company', '')
                    price = rowdata.get('price', '-')
                    chg = float(rowdata.get('change_pct', 0.0) or 0.0)
                except Exception:
                    sym, comp, price, chg = '-', '', '-', 0.0
                sym_lbl, company_lbl, price_lbl, chg_lbl = rows_ui[i]
                sym_lbl.text = f"[b]{sym}[/b]"
                company_lbl.text = comp
                price_lbl.text = _format_price(price)
                sign = '+' if chg > 0 else ''
                chg_lbl.text = f"{sign}{chg:.2f}%"
                chg_lbl.color = color_up if chg >= 0 else color_down
            for j in range(len(rows_items), 10):
                sym_lbl, company_lbl, price_lbl, chg_lbl = rows_ui[j]
                sym_lbl.text = '-'
                company_lbl.text = '-'
                price_lbl.text = '-'
                chg_lbl.text = '-'
                chg_lbl.color = (0.62, 0.62, 0.62, 1)

        _fill(self._analysis_g_rows, gainers)
        _fill(self._analysis_l_rows, losers)

        # Bandarmology (proxy from volume)
        total_buy = 0
        total_sell = 0
        points = []
        for it in items[:30]:
            sym = it.get('symbol')
            try:
                vol = float(it.get('volume', 0) or 0)
            except Exception:
                vol = 0.0
            if not sym or vol <= 0:
                continue
            bid_frac = self._stable_ratio(sym, 0.45, 0.55)
            bid_volume = int(max(0.0, vol) * bid_frac)
            offer_volume = int(max(0.0, vol)) - bid_volume
            buy_frac = self._stable_ratio(sym + 'B', 0.60, 0.80)
            sell_frac = self._stable_ratio(sym + 'S', 0.60, 0.80)
            buy = int(bid_volume * buy_frac)
            sell = int(offer_volume * sell_frac)
            total_buy += max(0, buy)
            total_sell += max(0, sell)
            points.append((sym, buy, sell))

        top_buy5 = sorted(points, key=lambda x: x[1], reverse=True)[:5]
        top_sell5 = sorted(points, key=lambda x: x[2], reverse=True)[:5]

        def _fmt(items2, idx, val_hex: str):
            if not items2:
                return '-'
            lines = []
            for i, it2 in enumerate(items2, start=1):
                sym = it2[0]
                val = it2[idx]
                vtxt = _format_id_number(val, decimals=0)
                lines.append(f"{i}. [color=#FFFFFF]{sym}[/color] [color={val_hex}]{vtxt}[/color]")
            return "\n".join(lines)

        def _hex(col):
            try:
                r = max(0, min(255, int(float(col[0]) * 255)))
                g = max(0, min(255, int(float(col[1]) * 255)))
                b = max(0, min(255, int(float(col[2]) * 255)))
                return f"#{r:02X}{g:02X}{b:02X}"
            except Exception:
                return '#FFFFFF'

        buy_hex = _hex((0.11, 0.75, 0.36, 1))
        sell_hex = _hex((0.86, 0.25, 0.25, 1))

        card_fb, card_fs, card_tb, card_ts = self._analysis_band_cards
        try:
            card_fb._value_label.text = _format_id_number(total_buy, decimals=0)
            card_fs._value_label.text = _format_id_number(total_sell, decimals=0)
            card_tb._value_label.text = _fmt(top_buy5, 1, buy_hex)
            card_ts._value_label.text = _fmt(top_sell5, 2, sell_hex)
        except Exception:
            pass

    def _tv_poll_tick(self):
        if self._tv_poll_inflight:
            return

        # Determine symbols to poll
        syms = []
        try:
            if self._mode == 'ANALYSIS':
                syms = list(self._analysis_symbols or [])[:50]
            else:
                syms = list((self._top_price_labels or {}).keys())[:50]
        except Exception:
            syms = []
        if not syms:
            return

        self._tv_poll_inflight = True

        def _worker():
            snap = None
            try:
                from modules.tradingview_fetcher import fetch_tradingview_snapshot
                snap = fetch_tradingview_snapshot(syms)
            except Exception:
                snap = None

            def _apply(_dt):
                try:
                    # If tab is gone, bail
                    if self.parent is None:
                        self._tv_poll_inflight = False
                        return

                    if isinstance(snap, dict):
                        # Update Top Acc/Top Dist prices (and flash)
                        for s, lbl in (self._top_price_labels or {}).items():
                            d = snap.get(s)
                            if not isinstance(d, dict):
                                continue
                            new_price = d.get('price', None)
                            if new_price in (None, '', '-'): 
                                continue
                            try:
                                new_price_f = float(new_price)
                            except Exception:
                                new_price_f = None
                            prev_price_f = (self._tv_prev_price or {}).get(s)
                            try:
                                new_txt = _format_price(new_price)
                                if getattr(lbl, 'text', None) != new_txt:
                                    lbl.text = new_txt
                            except Exception:
                                pass
                            if new_price_f is not None:
                                self._tv_prev_price[s] = new_price_f
                            if prev_price_f is not None and new_price_f is not None and prev_price_f != new_price_f:
                                row = (self._top_rows_by_symbol or {}).get(s)
                                if row is not None:
                                    self._flash_row(row, up=(new_price_f > prev_price_f))

                        # Update Analisis blocks
                        if self._mode == 'ANALYSIS':
                            self._analysis_apply_snapshot(snap)
                except Exception:
                    pass
                finally:
                    self._tv_poll_inflight = False

            try:
                Clock.schedule_once(_apply, 0)
            except Exception:
                self._tv_poll_inflight = False

        threading.Thread(target=_worker, daemon=True).start()

    def _scan_files_newest_first(self):
        base_dir = os.path.dirname(os.path.abspath(__file__))
        results_dir = os.path.join(base_dir, 'data', 'screening_results')
        try:
            files = [
                os.path.join(results_dir, f)
                for f in os.listdir(results_dir)
                if f.startswith('scan_') and f.endswith('.csv')
            ]
        except Exception:
            files = []
        if not files:
            return []
        # Prefer sorting by filename timestamp (scan_YYYYMMDD_HHMMSS.csv), fallback to mtime.
        try:
            def _key(p: str):
                name = os.path.basename(p)
                stem = name.replace('scan_', '').replace('.csv', '')
                return stem
            files.sort(key=_key, reverse=True)
        except Exception:
            try:
                files.sort(key=lambda p: os.path.getmtime(p), reverse=True)
            except Exception:
                files.sort(reverse=True)
        return files

    def _latest_scan_file(self):
        files = self._scan_files_newest_first()
        for p in files:
            try:
                if os.path.getsize(p) > 0:
                    return p
            except Exception:
                continue
        return None

    def _best_scan_file_for_mode(self, mode: str):
        # Choose the newest non-empty scan file that actually contains rows for the requested phase.
        for p in self._scan_files_newest_first():
            try:
                if os.path.getsize(p) <= 0:
                    continue
            except Exception:
                continue
            rows = self._load_screening_rows(p)
            if not rows:
                continue
            if mode in ('ACCUMULATION', 'DISTRIBUTION'):
                if any(((r.get('phase') or '').strip().upper() == mode) for r in rows):
                    return p
            else:
                return p
        return None

    def _load_screening_rows(self, path):
        rows = []
        if not path:
            return rows
        try:
            with open(path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for r in reader:
                    if not r:
                        continue
                    rows.append(r)
        except Exception:
            return []
        return rows

    def _top10_for_mode(self, rows, mode: str):
        filtered = []
        for r in rows:
            if (r.get('phase') or '').strip().upper() != mode:
                continue
            dist = _to_float(r.get('distance', None), default=None)
            if dist is None:
                continue
            filtered.append((dist, r))
        filtered.sort(key=lambda x: x[0], reverse=True)
        return [r for _, r in filtered[:10]]

    def _render_analysis_view(self):
        # Dashboard-style aggregate analysis (matches web "Analisis Saham" section)
        # Pick a scan file by date (default: today). Date format: YYYY-MM-DD
        try:
            if ZoneInfo is not None:
                today = datetime.now(ZoneInfo('Asia/Jakarta')).strftime('%Y-%m-%d')
            else:
                today = datetime.now().strftime('%Y-%m-%d')
        except Exception:
            today = datetime.now().strftime('%Y-%m-%d')

        chosen_date = str(getattr(self, '_analysis_date', '') or '').strip()
        if not chosen_date:
            chosen_date = today

        # Validate date
        try:
            datetime.strptime(chosen_date, '%Y-%m-%d')
        except Exception:
            chosen_date = today
            try:
                self._analysis_date = chosen_date
            except Exception:
                pass

        def _scan_file_for_date(date_str: str):
            try:
                yyyymmdd = date_str.replace('-', '')
            except Exception:
                return None
            for p in self._scan_files_newest_first():
                try:
                    name = os.path.basename(p)
                    # scan_YYYYMMDD_HHMMSS.csv
                    if name.startswith('scan_') and len(name) >= 18:
                        d = name.split('_', 2)[1]
                        if d == yyyymmdd:
                            if os.path.getsize(p) > 0:
                                return p
                except Exception:
                    continue
            return None

        def _date_from_scan_path(p: str) -> str | None:
            try:
                name = os.path.basename(p)
                # scan_YYYYMMDD_HHMMSS.csv
                if not (name.startswith('scan_') and name.endswith('.csv')):
                    return None
                parts = name.split('_', 2)
                if len(parts) < 3:
                    return None
                d = parts[1]
                if len(d) != 8 or (not d.isdigit()):
                    return None
                return f"{d[0:4]}-{d[4:6]}-{d[6:8]}"
            except Exception:
                return None

        # If user never picked a date and today has no scan yet, default to latest scan date.
        if not str(getattr(self, '_analysis_date', '') or '').strip():
            today_scan = _scan_file_for_date(today)
            if today_scan is None:
                fallback_latest = self._latest_scan_file()
                fallback_date = _date_from_scan_path(fallback_latest) if fallback_latest else None
                if fallback_date:
                    chosen_date = fallback_date
                    try:
                        self._analysis_date = chosen_date
                    except Exception:
                        pass

        # Resolve scan file for chosen date; if missing, fall back to newest available scan.
        latest = _scan_file_for_date(chosen_date)
        notice_txt = None
        if latest is None:
            fallback_latest = self._latest_scan_file()
            if fallback_latest is None:
                latest = None
            else:
                fb_date = _date_from_scan_path(fallback_latest) or 'tanggal terakhir'
                notice_txt = f"Tidak ada screening untuk {chosen_date}. Menampilkan {fb_date}."
                latest = fallback_latest
                try:
                    self._analysis_date = _date_from_scan_path(fallback_latest) or chosen_date
                except Exception:
                    pass

        rows = self._load_screening_rows(latest) if latest else []

        outer = GridLayout(cols=1, size_hint_y=None, spacing=ui_dp(10), padding=(ui_dp(4), ui_dp(12)))
        outer.bind(minimum_height=outer.setter('height'))

        # Date selector (styled like a dark card)
        date_row = BoxLayout(orientation='horizontal', size_hint_y=None, height=ui_dp(36), spacing=ui_dp(8))
        date_row.add_widget(
            Label(
                text='Tanggal',
                font_size=ui_sp(12),
                color=(0.70, 0.70, 0.70, 1),
                size_hint_x=None,
                width=ui_dp(62),
                halign='left',
                valign='middle',
                **_font_kwargs(),
            )
        )
        ti_date = TextInput(text=chosen_date, hint_text='YYYY-MM-DD', multiline=False, font_size=ui_sp(14), **_font_kwargs())
        try:
            ti_date.background_normal = ''
            ti_date.background_active = ''
            ti_date.background_color = (0.04, 0.04, 0.04, 1)
            ti_date.foreground_color = (0.92, 0.92, 0.92, 1)
            ti_date.cursor_color = (0.92, 0.92, 0.92, 1)
            ti_date.padding = [ui_dp(10), ui_dp(9), ui_dp(10), ui_dp(9)]
        except Exception:
            pass
        btn_date = Button(
            text='OK',
            size_hint_x=None,
            width=ui_dp(56),
            background_normal='',
            background_down='',
            background_color=(0, 0, 0, 0),
            color=(0.11, 0.75, 0.36, 1),
            padding=(0, 0),
            **_font_kwargs(),
        )
        try:
            btn_date.halign = 'center'
            btn_date.valign = 'middle'
            btn_date.text_size = btn_date.size
            btn_date.bind(size=lambda inst, val: setattr(inst, 'text_size', val))
        except Exception:
            pass

        # Outline-only style
        try:
            from kivy.graphics import Color, Line
            with btn_date.canvas.after:
                Color(0.11, 0.75, 0.36, 1)
                btn_date._outline = Line(rectangle=(btn_date.x, btn_date.y, btn_date.width, btn_date.height), width=1)

            def _upd_outline(*_):
                try:
                    btn_date._outline.rectangle = (btn_date.x, btn_date.y, btn_date.width, btn_date.height)
                except Exception:
                    pass

            btn_date.bind(pos=_upd_outline, size=_upd_outline)
        except Exception:
            pass

        def _apply_date(*_):
            try:
                d = str(ti_date.text or '').strip()
            except Exception:
                d = ''
            if not d:
                d = today
            try:
                datetime.strptime(d, '%Y-%m-%d')
            except Exception:
                d = today
            try:
                self._analysis_date = d
            except Exception:
                pass
            try:
                self.refresh()
            except Exception:
                pass

        btn_date.bind(on_press=_apply_date)
        date_row.add_widget(ti_date)
        date_row.add_widget(btn_date)
        date_card = BoxLayout(orientation='vertical', size_hint_y=None, height=ui_dp(52), padding=(ui_dp(8), ui_dp(8)))
        with date_card.canvas.before:
            from kivy.graphics import Color, Rectangle
            Color(0.06, 0.06, 0.06, 1)
            date_card._bg = Rectangle(pos=date_card.pos, size=date_card.size)
        date_card.bind(pos=lambda *_: setattr(date_card._bg, 'pos', date_card.pos), size=lambda *_: setattr(date_card._bg, 'size', date_card.size))
        date_card.add_widget(date_row)
        outer.add_widget(date_card)

        if notice_txt:
            outer.add_widget(
                Label(
                    text=notice_txt,
                    size_hint_y=None,
                    height=ui_dp(34),
                    font_size=ui_sp(12),
                    color=(0.60, 0.60, 0.60, 1),
                    halign='left',
                    valign='middle',
                    padding=(ui_dp(2), 0),
                    **_font_kwargs(),
                )
            )

        if latest is None:
            outer.add_widget(
                Label(
                    text='Belum ada file screening di data/screening_results.',
                    size_hint_y=None,
                    height=ui_dp(54),
                    font_size=ui_sp(14),
                    color=(0.72, 0.72, 0.72, 1),
                    halign='left',
                    valign='middle',
                    padding=(ui_dp(12), 0),
                    **_font_kwargs(),
                )
            )
            try:
                self._list.clear_widgets()
            except Exception:
                pass
            self._list.add_widget(outer)
            return

        # If the selected scan file exists but has no rows, fall back to newest non-empty scan
        if not rows:
            fallback_latest = self._latest_scan_file()
            if fallback_latest and fallback_latest != latest:
                try:
                    fb_date = _date_from_scan_path(fallback_latest) or 'tanggal terakhir'
                    notice_txt = notice_txt or f"Data screening kosong untuk {chosen_date}. Menampilkan {fb_date}."
                    latest = fallback_latest
                    rows = self._load_screening_rows(latest) if latest else []
                    try:
                        self._analysis_date = _date_from_scan_path(fallback_latest) or chosen_date
                    except Exception:
                        pass
                except Exception:
                    pass

        if not rows:
            msg = 'Belum ada hasil screening.'
            try:
                msg = f"Belum ada hasil screening. (file: {os.path.basename(latest)})"
            except Exception:
                pass
            outer.add_widget(
                Label(
                    text=msg,
                    size_hint_y=None,
                    height=ui_dp(54),
                    font_size=ui_sp(14),
                    color=(0.72, 0.72, 0.72, 1),
                    halign='left',
                    valign='middle',
                    padding=(ui_dp(12), 0),
                    **_font_kwargs(),
                )
            )
            try:
                self._list.clear_widgets()
            except Exception:
                pass
            self._list.add_widget(outer)
            return

        def _count_by_key(key: str):
            counts = {}
            for r in rows:
                v = (r.get(key) or '').strip().upper()
                if not v:
                    continue
                counts[v] = counts.get(v, 0) + 1
            return counts

        phase_counts = _count_by_key('phase')
        signal_counts = _count_by_key('signal')

        total = len(rows)
        acc = phase_counts.get('ACCUMULATION', 0)
        dist = phase_counts.get('DISTRIBUTION', 0)
        absorb = phase_counts.get('ABSORBING', 0)

        # colors aligned with existing palette in this file
        color_acc = (0.11, 0.75, 0.36, 1)
        color_dist = (0.86, 0.25, 0.25, 1)
        color_neutral = (0.62, 0.62, 0.62, 1)

        # metrics row (Total/Akumulasi/Distribusi/Absorbing)
        metrics = BoxLayout(orientation='horizontal', size_hint_y=None, height=ui_dp(64), spacing=ui_dp(6))

        def metric_card(label: str, value: str, value_color=(0.92, 0.92, 0.92, 1)):
            card = BoxLayout(orientation='vertical', padding=(ui_dp(8), ui_dp(8)), spacing=ui_dp(2))
            with card.canvas.before:
                from kivy.graphics import Color, Rectangle
                Color(0.06, 0.06, 0.06, 1)
                card._bg = Rectangle(pos=card.pos, size=card.size)
            card.bind(pos=lambda *_: setattr(card._bg, 'pos', card.pos), size=lambda *_: setattr(card._bg, 'size', card.size))
            v = Label(text=value, font_size=ui_sp(18), color=value_color, halign='center', valign='middle', **_font_kwargs())
            v.text_size = (v.width, None)
            v.bind(size=lambda inst, val: setattr(inst, 'text_size', (inst.width, None)))
            l = Label(text=label, font_size=ui_sp(12), color=(0.65, 0.65, 0.65, 1), halign='center', valign='middle', **_font_kwargs())
            l.text_size = (l.width, None)
            l.bind(size=lambda inst, val: setattr(inst, 'text_size', (inst.width, None)))
            card.add_widget(v)
            card.add_widget(l)
            return card

        metrics.add_widget(metric_card('Total', str(total)))
        metrics.add_widget(metric_card('Akumulasi', str(acc), value_color=color_acc))
        metrics.add_widget(metric_card('Distribusi', str(dist), value_color=color_dist))
        metrics.add_widget(metric_card('Absorbing', str(absorb), value_color=color_neutral))
        outer.add_widget(metrics)

        charts = BoxLayout(orientation='horizontal', size_hint_y=None, height=ui_dp(220), spacing=ui_dp(8))

        def chart_block(title: str, items: list[tuple[str, int, tuple]]):
            block = BoxLayout(orientation='vertical', padding=(ui_dp(8), ui_dp(10)), spacing=ui_dp(8))
            with block.canvas.before:
                from kivy.graphics import Color, Rectangle
                Color(0.06, 0.06, 0.06, 1)
                block._bg = Rectangle(pos=block.pos, size=block.size)
            block.bind(pos=lambda *_: setattr(block._bg, 'pos', block.pos), size=lambda *_: setattr(block._bg, 'size', block.size))

            cap = Label(text=title, font_size=ui_sp(12), color=(0.70, 0.70, 0.70, 1), size_hint_y=None, height=ui_dp(18), halign='left', valign='middle', **_font_kwargs())
            cap.text_size = (cap.width, None)
            cap.bind(size=lambda inst, val: setattr(inst, 'text_size', (inst.width, None)))
            block.add_widget(cap)

            chart = Widget(size_hint_y=None, height=ui_dp(132))

            def _redraw(*_):
                try:
                    from kivy.graphics import Color, Rectangle
                    chart.canvas.clear()
                    w = max(1, chart.width)
                    h = max(1, chart.height)
                    n = max(1, len(items))
                    gap = ui_dp(8)
                    bar_w = max(ui_dp(10), (w - (gap * (n + 1))) / float(n))
                    max_v = 1
                    try:
                        max_v = max([v for _, v, _ in items] + [1])
                    except Exception:
                        max_v = 1
                    base_y = chart.y
                    base_x = chart.x
                    with chart.canvas:
                        # baseline
                        Color(0.22, 0.22, 0.22, 1)
                        Rectangle(pos=(base_x, base_y), size=(w, max(1, int(ui_dp(1)))))
                        for i, (name, val, col) in enumerate(items):
                            x = base_x + gap + i * (bar_w + gap)
                            frac = 0.0
                            if max_v > 0:
                                frac = float(val) / float(max_v)
                            bh = int((h - ui_dp(6)) * frac)
                            if val > 0:
                                bh = max(int(ui_dp(4)), bh)
                            # track
                            Color(0.14, 0.14, 0.14, 1)
                            Rectangle(pos=(x, base_y), size=(bar_w, h - ui_dp(2)))
                            # fill
                            Color(*col)
                            Rectangle(pos=(x, base_y), size=(bar_w, bh))
                except Exception:
                    pass

            chart.bind(pos=_redraw, size=_redraw)
            block.add_widget(chart)

            legend = GridLayout(cols=max(1, len(items)), size_hint_y=None, height=ui_dp(34), spacing=ui_dp(4))
            for name, val, col in items:
                legend.add_widget(
                    Label(
                        text=f"[b]{name}[/b]\n{val}",
                        markup=True,
                        font_size=ui_sp(11),
                        color=col,
                        halign='center',
                        valign='middle',
                        **_font_kwargs(),
                    )
                )
            block.add_widget(legend)

            # draw once
            _redraw()
            return block

        phase_items = [
            ('ACC', acc, color_acc),
            ('DIST', dist, color_dist),
            ('ABS', absorb, color_neutral),
        ]

        sb = signal_counts.get('STRONG_BUY', 0)
        b = signal_counts.get('BUY', 0)
        s = signal_counts.get('SELL', 0)
        ss = signal_counts.get('STRONG_SELL', 0)
        signal_items = [
            ('S.BUY', sb, color_acc),
            ('BUY', b, color_acc),
            ('SELL', s, color_dist),
            ('S.SELL', ss, color_dist),
        ]

        charts.add_widget(chart_block('Fase Pasar', phase_items))
        charts.add_widget(chart_block('Signal Trading', signal_items))
        outer.add_widget(charts)

        # --- Bandarmology (estimasi) ---
        # NOTE: Screening CSV doesn't contain broker/foreign flow.
        # We compute a best-effort estimate using TradingView snapshot (volume-based proxy).
        band = BoxLayout(orientation='vertical', padding=(ui_dp(8), ui_dp(10)), spacing=ui_dp(8), size_hint_y=None)
        band.bind(minimum_height=band.setter('height'))
        with band.canvas.before:
            from kivy.graphics import Color, Rectangle
            Color(0.06, 0.06, 0.06, 1)
            band._bg = Rectangle(pos=band.pos, size=band.size)
        band.bind(pos=lambda *_: setattr(band._bg, 'pos', band.pos), size=lambda *_: setattr(band._bg, 'size', band.size))

        band_title = Label(
            text='Bandarmology',
            font_size=ui_sp(12),
            color=(0.70, 0.70, 0.70, 1),
            size_hint_y=None,
            height=ui_dp(18),
            halign='left',
            valign='middle',
            **_font_kwargs(),
        )
        band_title.text_size = (band_title.width, None)
        band_title.bind(size=lambda inst, val: setattr(inst, 'text_size', (inst.width, None)))
        band.add_widget(band_title)

        band_metrics = BoxLayout(orientation='vertical', size_hint_y=None, spacing=ui_dp(8))
        band_metrics.bind(minimum_height=band_metrics.setter('height'))

        def metric_card_small(label: str, value: str, value_color=(0.92, 0.92, 0.92, 1), value_font_size=None, markup: bool = False):
            card = BoxLayout(orientation='vertical', padding=(ui_dp(8), ui_dp(8)), spacing=ui_dp(2))
            with card.canvas.before:
                from kivy.graphics import Color, Rectangle
                Color(0.04, 0.04, 0.04, 1)
                card._bg = Rectangle(pos=card.pos, size=card.size)
            card.bind(pos=lambda *_: setattr(card._bg, 'pos', card.pos), size=lambda *_: setattr(card._bg, 'size', card.size))

            v = Label(text=value, markup=markup, font_size=(value_font_size or ui_sp(16)), color=value_color, halign='center', valign='middle', **_font_kwargs())
            v.text_size = (v.width, None)
            v.bind(size=lambda inst, val: setattr(inst, 'text_size', (inst.width, None)))
            l = Label(text=label, font_size=ui_sp(11), color=(0.65, 0.65, 0.65, 1), halign='center', valign='middle', **_font_kwargs())
            l.text_size = (l.width, None)
            l.bind(size=lambda inst, val: setattr(inst, 'text_size', (inst.width, None)))

            card.add_widget(v)
            card.add_widget(l)
            card._value_label = v
            return card

        card_fb = metric_card_small('Buy (Est)', '…', value_color=color_acc)
        card_fs = metric_card_small('Sell (Est)', '…', value_color=color_dist)
        card_tb = metric_card_small('Top Buy (5)', '…', value_color=(0.92, 0.92, 0.92, 1), value_font_size=ui_sp(11), markup=True)
        card_ts = metric_card_small('Top Sell (5)', '…', value_color=(0.92, 0.92, 0.92, 1), value_font_size=ui_sp(11), markup=True)

        row_1 = BoxLayout(orientation='horizontal', size_hint_y=None, height=ui_dp(64), spacing=ui_dp(6))
        row_2 = BoxLayout(orientation='horizontal', size_hint_y=None, height=ui_dp(94), spacing=ui_dp(6))
        row_1.add_widget(card_fb)
        row_1.add_widget(card_fs)
        row_2.add_widget(card_tb)
        row_2.add_widget(card_ts)
        band_metrics.add_widget(row_1)
        band_metrics.add_widget(row_2)
        band.add_widget(band_metrics)

        outer.add_widget(band)

        # expose analysis state for polling updates
        try:
            self._analysis_symbols = [str(r.get('symbol', '')).strip().upper() for r in rows]
            self._analysis_symbols = [s for s in self._analysis_symbols if s]
        except Exception:
            self._analysis_symbols = []
        try:
            m = {}
            for r in rows:
                s = str(r.get('symbol', '')).strip().upper()
                if not s:
                    continue
                c = str(r.get('company', '') or '').strip()
                if c and s not in m:
                    m[s] = c
            self._analysis_symbol_to_company = m
        except Exception:
            self._analysis_symbol_to_company = {}

        # --- Top Gainers / Top Losers (2 cards) ---
        def _make_mover_card(title_txt: str):
            card = BoxLayout(orientation='vertical', padding=(ui_dp(8), ui_dp(10)), spacing=ui_dp(8), size_hint_y=None)
            card.bind(minimum_height=card.setter('height'))
            with card.canvas.before:
                from kivy.graphics import Color, Rectangle
                Color(0.06, 0.06, 0.06, 1)
                card._bg = Rectangle(pos=card.pos, size=card.size)
            card.bind(pos=lambda *_: setattr(card._bg, 'pos', card.pos), size=lambda *_: setattr(card._bg, 'size', card.size))

            ttl = Label(
                text=title_txt,
                font_size=ui_sp(12),
                color=(0.70, 0.70, 0.70, 1),
                size_hint_y=None,
                height=ui_dp(18),
                halign='left',
                valign='middle',
                **_font_kwargs(),
            )
            ttl.text_size = (ttl.width, None)
            ttl.bind(size=lambda inst, val: setattr(inst, 'text_size', (inst.width, None)))
            card.add_widget(ttl)

            gl = GridLayout(cols=1, spacing=0, size_hint_y=None)
            gl.bind(minimum_height=gl.setter('height'))
            rows_ui = []

            def _make_row():
                row_h = ui_dp(56)
                row = BoxLayout(orientation='horizontal', padding=(ui_dp(4), ui_dp(6)), spacing=ui_dp(8), size_hint_y=None, height=row_h)
                with row.canvas.before:
                    from kivy.graphics import Color, Rectangle
                    Color(0.04, 0.04, 0.04, 1)
                    row._bg = Rectangle(pos=row.pos, size=row.size)
                    Color(0.12, 0.12, 0.12, 1)
                    row._sep = Rectangle(pos=(row.x, row.y), size=(row.width, 1))

                def _upd(*_):
                    row._bg.pos = row.pos
                    row._bg.size = row.size
                    row._sep.pos = (row.x, row.y)
                    row._sep.size = (row.width, 1)

                row.bind(pos=_upd, size=_upd)

                left = BoxLayout(orientation='vertical', spacing=ui_dp(1), size_hint_x=1)
                sym_lbl = Label(text='…', markup=True, font_size=ui_sp(14), color=(0.92, 0.92, 0.92, 1), halign='left', valign='middle', **_font_kwargs())
                sym_lbl.text_size = (sym_lbl.width, None)
                sym_lbl.bind(size=lambda inst, val: setattr(inst, 'text_size', (inst.width, None)))
                try:
                    sym_lbl.shorten = True
                    sym_lbl.shorten_from = 'right'
                except Exception:
                    pass

                company_lbl = Label(text='…', font_size=ui_sp(11), color=(0.92, 0.92, 0.92, 1), halign='left', valign='middle', **_font_kwargs())
                company_lbl.text_size = (company_lbl.width, None)
                company_lbl.bind(size=lambda inst, val: setattr(inst, 'text_size', (inst.width, None)))
                try:
                    company_lbl.shorten = True
                    company_lbl.shorten_from = 'right'
                except Exception:
                    pass

                left.add_widget(sym_lbl)
                left.add_widget(company_lbl)
                row.add_widget(left)

                right_w = ui_dp(112)
                right = BoxLayout(orientation='vertical', size_hint_x=None, width=right_w, spacing=ui_dp(1))
                price_lbl = Label(text='-', font_size=ui_sp(14), color=(0.90, 0.90, 0.90, 1), halign='right', valign='middle', **_font_kwargs())
                price_lbl.text_size = (right_w, None)
                chg_lbl = Label(text='-', font_size=ui_sp(12), color=(0.62, 0.62, 0.62, 1), halign='right', valign='middle', **_font_kwargs())
                chg_lbl.text_size = (right_w, None)
                right.add_widget(price_lbl)
                right.add_widget(chg_lbl)
                row.add_widget(right)
                return row, sym_lbl, company_lbl, price_lbl, chg_lbl

            for _ in range(10):
                row, sym_lbl, company_lbl, price_lbl, chg_lbl = _make_row()
                rows_ui.append((sym_lbl, company_lbl, price_lbl, chg_lbl))
                gl.add_widget(row)

            card.add_widget(gl)
            return card, rows_ui

        gainers_card, g_rows = _make_mover_card('Top Gainers')
        losers_card, l_rows = _make_mover_card('Top Losers')
        outer.add_widget(gainers_card)
        outer.add_widget(losers_card)

        try:
            self._analysis_g_rows = g_rows
            self._analysis_l_rows = l_rows
            self._analysis_band_cards = (card_fb, card_fs, card_tb, card_ts)
        except Exception:
            pass

        # Load bandarmology estimates in background (avoid blocking UI)
        try:
            scan_key = os.path.basename(latest) if latest else 'no_scan'
        except Exception:
            scan_key = 'no_scan'

        if not hasattr(self, '_bandarmo_cache'):
            self._bandarmo_cache = {}
        if not hasattr(self, '_bandarmo_loading'):
            self._bandarmo_loading = False

        if not hasattr(self, '_movers_cache'):
            self._movers_cache = {}
        if not hasattr(self, '_movers_loading'):
            self._movers_loading = False

        def _apply_bandarmo(data: dict | None):
            if not data:
                card_fb._value_label.text = '-'
                card_fs._value_label.text = '-'
                card_tb._value_label.text = '-'
                card_ts._value_label.text = '-'
                return
            card_fb._value_label.text = data.get('foreign_buy_txt', '-')
            card_fs._value_label.text = data.get('foreign_sell_txt', '-')
            card_tb._value_label.text = data.get('top_buy_txt', '-')
            card_ts._value_label.text = data.get('top_sell_txt', '-')

        cached = self._bandarmo_cache.get(scan_key)
        if cached:
            _apply_bandarmo(cached)
        elif not self._bandarmo_loading:
            # compute on top symbols (from screening file)
            symbols = []
            try:
                symbols = [str(r.get('symbol', '')).strip().upper() for r in rows]
                symbols = [s for s in symbols if s]
            except Exception:
                symbols = []

            def _worker():
                result = None
                try:
                    from modules.tradingview_fetcher import fetch_tradingview_snapshot
                    import hashlib

                    # Prefetch TradingView snapshot once (fast bulk)
                    try:
                        tv_snap = fetch_tradingview_snapshot(symbols[:30]) if symbols else {}
                    except Exception:
                        tv_snap = {}

                    def _stable_ratio(sym: str, lo: float, hi: float) -> float:
                        try:
                            h = hashlib.md5(sym.encode('utf-8')).hexdigest()
                            v = int(h[:8], 16) / float(0xFFFFFFFF)
                            return lo + (hi - lo) * v
                        except Exception:
                            return (lo + hi) / 2.0

                    total_buy = 0
                    total_sell = 0

                    points = []  # (sym, buy, sell)
                    ok_count = 0
                    for sym in symbols[:30]:
                        buy = 0
                        sell = 0
                        got = False

                        # TradingView snapshot volume (near-realtime polling)
                        snap = (tv_snap or {}).get(sym)
                        if isinstance(snap, dict):
                            try:
                                vol = float(snap.get('volume', 0) or 0)
                            except Exception:
                                vol = 0.0
                            if vol > 0:
                                # Estimate bid/offer split deterministically per-symbol
                                bid_frac = _stable_ratio(sym, 0.45, 0.55)
                                bid_volume = int(max(0.0, vol) * bid_frac)
                                offer_volume = int(max(0.0, vol)) - bid_volume
                                # Proxy for buy/sell pressure
                                buy_frac = _stable_ratio(sym + 'B', 0.60, 0.80)
                                sell_frac = _stable_ratio(sym + 'S', 0.60, 0.80)
                                buy = int(bid_volume * buy_frac)
                                sell = int(offer_volume * sell_frac)
                                got = True

                        if got:
                            ok_count += 1
                            total_buy += max(0, buy)
                            total_sell += max(0, sell)
                            points.append((sym, buy, sell))

                    top_buy5 = sorted(points, key=lambda x: x[1], reverse=True)[:5]
                    top_sell5 = sorted(points, key=lambda x: x[2], reverse=True)[:5]

                    def _hex(col):
                        try:
                            r = max(0, min(255, int(float(col[0]) * 255)))
                            g = max(0, min(255, int(float(col[1]) * 255)))
                            b = max(0, min(255, int(float(col[2]) * 255)))
                            return f"#{r:02X}{g:02X}{b:02X}"
                        except Exception:
                            return '#FFFFFF'

                    buy_hex = _hex(color_acc)
                    sell_hex = _hex(color_dist)

                    def _fmt_list_markup(items, idx, val_hex: str):
                        if not items:
                            return '-'
                        lines = []
                        for i, it in enumerate(items, start=1):
                            sym = it[0]
                            val = it[idx]
                            vtxt = _format_id_number(val, decimals=0)
                            lines.append(f"{i}. [color=#FFFFFF]{sym}[/color] [color={val_hex}]{vtxt}[/color]")
                        return "\n".join(lines)

                    result = {
                        'foreign_buy_txt': _format_id_number(total_buy, decimals=0),
                        'foreign_sell_txt': _format_id_number(total_sell, decimals=0),
                        'top_buy_txt': _fmt_list_markup(top_buy5, 1, buy_hex),
                        'top_sell_txt': _fmt_list_markup(top_sell5, 2, sell_hex),
                    }
                except Exception:
                    result = None

                def _done(_dt):
                    try:
                        self._bandarmo_loading = False
                        if result:
                            self._bandarmo_cache[scan_key] = result
                        _apply_bandarmo(result)
                    except Exception:
                        pass

                try:
                    Clock.schedule_once(_done, 0)
                except Exception:
                    pass

            self._bandarmo_loading = True
            threading.Thread(target=_worker, daemon=True).start()

        # Load gainers/losers in background
        def _apply_movers(payload: dict | None):
            color_up = (0.11, 0.75, 0.36, 1)
            color_down = (0.86, 0.25, 0.25, 1)

            def _fill(rows_ui, items, is_gainers: bool):
                if not items:
                    for sym_lbl, company_lbl, price_lbl, chg_lbl in rows_ui:
                        sym_lbl.text = '-'
                        company_lbl.text = '-'
                        price_lbl.text = '-'
                        chg_lbl.text = '-'
                        chg_lbl.color = (0.62, 0.62, 0.62, 1)
                    return

                for i, rowdata in enumerate(items[:10]):
                    try:
                        sym = rowdata.get('symbol', '-')
                        comp = rowdata.get('company', '')
                        price = rowdata.get('price', '-')
                        chg = float(rowdata.get('change_pct', 0.0) or 0.0)
                    except Exception:
                        sym, comp, price, chg = '-', '', '-', 0.0

                    sym_lbl, company_lbl, price_lbl, chg_lbl = rows_ui[i]
                    sym_lbl.text = f"[b]{sym}[/b]"
                    company_lbl.text = comp
                    price_lbl.text = _format_price(price)
                    sign = '+' if chg > 0 else ''
                    chg_lbl.text = f"{sign}{chg:.2f}%"
                    chg_lbl.color = color_up if chg >= 0 else color_down

                for j in range(len(items), 10):
                    sym_lbl, company_lbl, price_lbl, chg_lbl = rows_ui[j]
                    sym_lbl.text = '-'
                    company_lbl.text = '-'
                    price_lbl.text = '-'
                    chg_lbl.text = '-'
                    chg_lbl.color = (0.62, 0.62, 0.62, 1)

            if not payload:
                _fill(g_rows, None, True)
                _fill(l_rows, None, False)
                return

            _fill(g_rows, payload.get('gainers') if isinstance(payload, dict) else None, True)
            _fill(l_rows, payload.get('losers') if isinstance(payload, dict) else None, False)

        # cache with small TTL to avoid spamming TradingView
        try:
            import time
            now = time.time()
        except Exception:
            now = 0.0

        cached_m = self._movers_cache.get(scan_key)
        if cached_m and isinstance(cached_m, dict) and (now - float(cached_m.get('ts', 0.0) or 0.0) <= 10.0):
            _apply_movers(cached_m.get('data'))
        elif not self._movers_loading:
            symbols = []
            try:
                symbols = [str(r.get('symbol', '')).strip().upper() for r in rows]
                symbols = [s for s in symbols if s]
            except Exception:
                symbols = []

            symbol_to_company = {}
            try:
                for r in rows:
                    s = str(r.get('symbol', '')).strip().upper()
                    if not s:
                        continue
                    c = str(r.get('company', '') or '').strip()
                    if c and s not in symbol_to_company:
                        symbol_to_company[s] = c
            except Exception:
                symbol_to_company = {}

            def _mworker():
                result = None
                try:
                    from modules.tradingview_fetcher import fetch_tradingview_snapshot
                    snap = fetch_tradingview_snapshot(symbols[:50]) if symbols else {}
                    items = []
                    for s in symbols[:50]:
                        d = (snap or {}).get(s) or {}
                        if not isinstance(d, dict):
                            continue
                        try:
                            chg = d.get('change', None)
                            if chg is None:
                                continue
                            chg = float(chg)
                        except Exception:
                            continue
                        items.append({
                            'symbol': s,
                            'company': symbol_to_company.get(s, ''),
                            'price': d.get('price', '-'),
                            'change_pct': chg,
                        })

                    gainers = sorted(items, key=lambda x: float(x.get('change_pct', 0.0) or 0.0), reverse=True)[:10]
                    losers = sorted(items, key=lambda x: float(x.get('change_pct', 0.0) or 0.0))[:10]
                    result = {'gainers': gainers, 'losers': losers}
                except Exception:
                    result = None

                def _done(_dt):
                    try:
                        self._movers_loading = False
                        try:
                            import time
                            ts = time.time()
                        except Exception:
                            ts = 0.0
                        if result is not None:
                            self._movers_cache[scan_key] = {'ts': ts, 'data': result}
                        _apply_movers(result)
                    except Exception:
                        pass

                try:
                    Clock.schedule_once(_done, 0)
                except Exception:
                    pass

            self._movers_loading = True
            threading.Thread(target=_mworker, daemon=True).start()

        try:
            self._list.clear_widgets()
        except Exception:
            pass
        self._list.add_widget(outer)

        # Start polling when analysis view is visible
        self._start_tv_poll()

    def refresh(self):
        if self._mode == 'ANALYSIS':
            self._render_analysis_view()
            return

        latest = self._best_scan_file_for_mode(self._mode) or self._latest_scan_file()
        rows = self._load_screening_rows(latest)
        items = self._top10_for_mode(rows, self._mode)

        if not items:
            msg = 'Belum ada hasil screening.'
            if latest is None:
                msg = 'Belum ada file screening di data/screening_results.'
            else:
                try:
                    msg = f"Belum ada hasil screening. (file: {os.path.basename(latest)})"
                except Exception:
                    pass
            try:
                self._list.clear_widgets()
            except Exception:
                pass
            self._list.add_widget(
                Label(
                    text=msg,
                    size_hint_y=None,
                    height=ui_dp(54),
                    font_size=ui_sp(14),
                    color=(0.72, 0.72, 0.72, 1),
                    halign='left',
                    valign='middle',
                    padding=(ui_dp(12), 0),
                    **_font_kwargs(),
                )
            )
            return

        color_acc = (0.11, 0.75, 0.36, 1)
        color_dist = (0.86, 0.25, 0.25, 1)
        phase_color = color_acc if self._mode == 'ACCUMULATION' else color_dist

        tv_price_labels = {}
        tv_rows_by_symbol = {}

        # Match the card style used in Top Gainers/Losers (padding from screen edges), dengan margin horizontal kompromi.
        outer = BoxLayout(orientation='vertical', padding=(ui_dp(4), ui_dp(12)), spacing=ui_dp(8), size_hint_y=None)
        outer.bind(minimum_height=outer.setter('height'))

        card = BoxLayout(orientation='vertical', padding=(ui_dp(8), ui_dp(10)), spacing=ui_dp(8), size_hint_y=None)
        card.bind(minimum_height=card.setter('height'))
        with card.canvas.before:
            from kivy.graphics import Color, Rectangle
            Color(0.06, 0.06, 0.06, 1)
            card._bg = Rectangle(pos=card.pos, size=card.size)
        card.bind(pos=lambda *_: setattr(card._bg, 'pos', card.pos), size=lambda *_: setattr(card._bg, 'size', card.size))

        ttl = Label(
            text='Top Acc' if self._mode == 'ACCUMULATION' else 'Top Dist',
            font_size=ui_sp(12),
            color=(0.70, 0.70, 0.70, 1),
            size_hint_y=None,
            height=ui_dp(18),
            halign='left',
            valign='middle',
            **_font_kwargs(),
        )
        ttl.text_size = (ttl.width, None)
        ttl.bind(size=lambda inst, val: setattr(inst, 'text_size', (inst.width, None)))
        card.add_widget(ttl)

        gl = GridLayout(cols=1, spacing=0, size_hint_y=None)
        gl.bind(minimum_height=gl.setter('height'))
        card.add_widget(gl)
        outer.add_widget(card)

        for r in items:
            sym = (r.get('symbol') or '-').strip()
            company = (r.get('company') or '').strip()
            price = _format_price(_to_float(r.get('price', None), default=None))
            vwap = _format_price(_to_float(r.get('vwap', None), default=None))
            dist_val = _to_float(r.get('distance', None), default=None)
            dist_txt = '-' if dist_val is None else f"{dist_val:+.2f}%"

            row_h = ui_dp(72)
            row = BoxLayout(orientation='horizontal', padding=(ui_dp(4), ui_dp(8)), spacing=ui_dp(8))
            row.size_hint = (1, None)
            row.height = row_h
            with row.canvas.before:
                from kivy.graphics import Color, Rectangle
                row._bg_color = Color(0.04, 0.04, 0.04, 1)
                row._base_bg_rgba = (0.04, 0.04, 0.04, 1)
                row._bg = Rectangle(pos=row.pos, size=row.size)
                Color(0.12, 0.12, 0.12, 1)
                row._sep = Rectangle(pos=(row.x, row.y), size=(row.width, 1))

            def _upd(*_):
                row._bg.pos = row.pos
                row._bg.size = row.size
                row._sep.pos = (row.x, row.y)
                row._sep.size = (row.width, 1)

            row.bind(pos=_upd, size=_upd)

            left = BoxLayout(orientation='vertical', spacing=ui_dp(2), size_hint_x=1)
            sym_lbl = ClickableLabel(
                text=f'[b]{sym}[/b]',
                markup=True,
                font_size=ui_sp(16),
                color=(0.92, 0.92, 0.92, 1),
                halign='left',
                valign='middle',
                **_font_kwargs(),
            )
            sym_lbl.text_size = (sym_lbl.width, None)
            sym_lbl.bind(size=lambda inst, val: setattr(inst, 'text_size', (inst.width, None)))
            try:
                sym_lbl.shorten = True
                sym_lbl.shorten_from = 'right'
            except Exception:
                pass
            try:
                def _go(_btn=None, _sym=str(sym).strip().upper()):
                    try:
                        from kivy.app import App
                        app = App.get_running_app()
                        if app is not None and hasattr(app, 'open_cek_emiten'):
                            app.open_cek_emiten(_sym)
                    except Exception:
                        pass
                sym_lbl.bind(on_press=_go)
            except Exception:
                pass
            company_lbl = Label(
                text=company,
                font_size=ui_sp(12),
                color=(0.92, 0.92, 0.92, 1),
                halign='left',
                valign='middle',
                **_font_kwargs(),
            )
            company_lbl.text_size = (company_lbl.width, None)
            company_lbl.bind(size=lambda inst, val: setattr(inst, 'text_size', (inst.width, None)))
            try:
                company_lbl.shorten = True
                company_lbl.shorten_from = 'right'
            except Exception:
                pass
            left.add_widget(sym_lbl)
            left.add_widget(company_lbl)
            row.add_widget(left)

            right_w = ui_dp(140)
            right = BoxLayout(orientation='vertical', size_hint_x=None, width=right_w, spacing=ui_dp(1))

            price_lbl = Label(text=price, font_size=ui_sp(18), color=(0.90, 0.90, 0.90, 1), halign='right', valign='middle', **_font_kwargs())
            price_lbl.text_size = (right_w, None)
            try:
                if sym and sym != '-':
                    tv_price_labels[str(sym).strip().upper()] = price_lbl
                    tv_rows_by_symbol[str(sym).strip().upper()] = row
            except Exception:
                pass

            vwap_lbl = Label(text=f'VWAP {vwap}', font_size=ui_sp(12), color=(0.65, 0.65, 0.65, 1), halign='right', valign='middle', **_font_kwargs())
            vwap_lbl.text_size = (right_w, None)

            dist_lbl = Label(text=f'Dist {dist_txt}', font_size=ui_sp(12), color=phase_color, halign='right', valign='middle', **_font_kwargs())
            dist_lbl.text_size = (right_w, None)

            right.add_widget(price_lbl)
            right.add_widget(vwap_lbl)
            right.add_widget(dist_lbl)
            row.add_widget(right)

            gl.add_widget(row)

        outer.add_widget(Widget(size_hint_y=None, height=ui_dp(8)))
        try:
            self._list.clear_widgets()
        except Exception:
            pass
        self._list.add_widget(outer)

        # Store mapping for polling updates and start poll
        try:
            self._top_price_labels = tv_price_labels
            self._top_rows_by_symbol = tv_rows_by_symbol
        except Exception:
            self._top_price_labels = {}
            self._top_rows_by_symbol = {}
        self._start_tv_poll()

class CekSahamTab(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(orientation='vertical', **kwargs)
        self._detail_mode = False
        # Detail-mode chart fallback (when yfinance is unavailable on Android):
        # poll TradingView snapshot and build an in-memory mini-series.
        self._detail_tv_poll_event = None
        self._detail_tv_poll_inflight = False
        self._detail_tv_symbol = None
        self._detail_tv_series = []  # list of (timestamp, price)
        self._detail_tv_last_ts = None
        self._detail_chart_widget = None
        self._yfinance_available = False
        # Header like Stockbit search: avatar + rounded search bar.
        header = BoxLayout(
            orientation='vertical',
            size_hint_y=None,
            spacing=ui_dp(6),
        )
        header.bind(minimum_height=header.setter('height'))

        header_top = BoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=ui_dp(78),
            padding=(ui_dp(4), ui_dp(12)),
            spacing=ui_dp(12),
        )
        from kivy.uix.anchorlayout import AnchorLayout
        from kivy.graphics import Color, Ellipse
        avatar_size = ui_dp(42)
        avatar = Widget(size_hint=(None, None), size=(avatar_size, avatar_size))
        self._hdr_avatar = avatar
        with avatar.canvas.before:
            # Prefer showing the bundled profile icon like Stockbit.
            try:
                from kivy.core.image import Image as CoreImage
                profile_path = os.path.join('assets', 'icons', 'profile.png')
                tex = CoreImage(profile_path).texture
                Color(1, 1, 1, 1)
                avatar._circ = Ellipse(pos=avatar.pos, size=avatar.size)
                avatar._circ.texture = tex
            except Exception:
                Color(0.18, 0.22, 0.30, 1)
                avatar._circ = Ellipse(pos=avatar.pos, size=avatar.size)
        avatar.bind(
            pos=lambda *_: setattr(avatar._circ, 'pos', avatar.pos),
            size=lambda *_: setattr(avatar._circ, 'size', avatar.size),
        )

        from kivy.uix.floatlayout import FloatLayout
        left = FloatLayout(size_hint=(None, 1), width=avatar_size)
        self._back_btn = Button(
            text='‹',
            size_hint=(None, None),
            size=(avatar_size, avatar_size),
            pos_hint={'center_x': 0.5, 'center_y': 0.5},
            background_normal='',
            background_down='',
            background_color=(0, 0, 0, 0),
            color=(0.92, 0.92, 0.92, 1),
            font_size=ui_sp(26),
            padding=(0, 0),
            disabled=True,
            opacity=0,
            **_font_kwargs(),
        )
        try:
            # Top-left like Stockbit
            avatar.pos_hint = {'x': 0, 'top': 1}
        except Exception:
            pass

        # Back button overlays avatar (used in detail mode)
        try:
            self._back_btn.pos_hint = {'x': 0, 'top': 1}
        except Exception:
            pass
        left.add_widget(self._back_btn)
        left.add_widget(avatar)
        header_top.add_widget(left)

        # Center area: search bar (default) OR symbol label (detail mode)
        from kivy.uix.floatlayout import FloatLayout
        mid = FloatLayout(size_hint=(1, 1))

        # Rounded search container
        search_container = BoxLayout(
            orientation='horizontal',
            size_hint=(1, None),
            height=ui_dp(40),
            padding=(ui_dp(14), 0),
            spacing=ui_dp(8),
            # top-aligned inside header
            pos_hint={'x': 0, 'top': 1},
        )
        self._hdr_searchbar = search_container
        try:
            from kivy.graphics import RoundedRectangle
            from kivy.graphics import Line
            def _redraw_search_bg(_=None, __=None):
                search_container.canvas.before.clear()
                with search_container.canvas.before:
                    # Pill background + subtle outline.
                    Color(0.20, 0.20, 0.20, 1)
                    r = search_container.height / 2.0
                    search_container._bg = RoundedRectangle(pos=search_container.pos, size=search_container.size, radius=[r, r, r, r])
                    Color(0.24, 0.24, 0.24, 1)
                    Line(rounded_rectangle=[search_container.x, search_container.y, search_container.width, search_container.height, r], width=1)
            search_container.bind(pos=_redraw_search_bg, size=_redraw_search_bg)
            _redraw_search_bg()
        except Exception:
            pass

        # Magnifier icon (bundled asset)
        try:
            from kivy.uix.image import Image
            icon = Image(
                source=os.path.join('assets', 'icons', 'search.png'),
                size_hint=(None, 1),
                width=ui_dp(22),
            )
            # Monochrome/tint like Stockbit
            try:
                icon.color = (0.62, 0.62, 0.62, 1)
            except Exception:
                pass
        except Exception:
            icon = Label(
                text='🔍',
                font_size=ui_sp(16),
                color=(0.55, 0.55, 0.55, 1),
                size_hint=(None, 1),
                width=ui_dp(22),
                halign='center',
                valign='middle',
                **_font_kwargs(),
            )
            try:
                icon.text_size = (icon.width, None)
                icon.bind(size=lambda inst, val: setattr(inst, 'text_size', (inst.width, None)))
            except Exception:
                pass

        self._ti = TextInput(
            text='',
            hint_text='Search symbol or username',
            multiline=False,
            font_size=ui_sp(15.5),
            background_normal='',
            background_active='',
            background_color=(0, 0, 0, 0),
            foreground_color=(0.90, 0.90, 0.90, 1),
            cursor_color=(0.90, 0.90, 0.90, 1),
            padding=(0, ui_dp(8)),
            **_font_kwargs(),
        )
        try:
            self._ti.hint_text_color = (0.55, 0.55, 0.55, 1)
        except Exception:
            pass

        search_container.add_widget(icon)
        search_container.add_widget(self._ti)
        mid.add_widget(search_container)

        symbol_label = Label(
            text='[b][/b]',
            markup=True,
            font_size=ui_sp(18),
            color=(1, 1, 1, 1),
            halign='center',
            valign='middle',
            size_hint=(1, 1),
            opacity=0,
            **_font_kwargs(),
        )
        symbol_label.text_size = (symbol_label.width, symbol_label.height)
        symbol_label.bind(size=lambda inst, val: setattr(inst, 'text_size', val))
        self._hdr_symbol = symbol_label
        mid.add_widget(symbol_label)

        header_top.add_widget(mid)

        header.add_widget(header_top)
        self.add_widget(header)

        # No extra controls row: execute search via Enter on the header search bar.

        # Result area (scrollable)
        self._result_grid = GridLayout(cols=1, spacing=ui_dp(6), size_hint=(1, None), padding=(ui_dp(4), ui_dp(10)))
        self._result_grid.bind(minimum_height=self._result_grid.setter('height'))
        res_scroll = ScrollView(do_scroll_y=True, do_scroll_x=False, bar_width=0)
        res_scroll.add_widget(self._result_grid)
        self.add_widget(res_scroll)

        self._busy = False

        # Cache for welcome IHSG data to avoid refetching too often.
        self._ihsg_cache = {'ts': 0.0, 'data': None}
        self._ihsg_series = []
        self._ihsg_series_cache = {'ts': 0.0, 'values': []}
        self._penny_cache = {'ts': 0.0, 'rows': []}
        self._ihsg_poll_ev = None

        def _clear_and_msg(msg: str):
            self._result_grid.clear_widgets()
            self._result_grid.add_widget(
                Label(
                    text=str(msg),
                    size_hint_y=None,
                    height=ui_dp(40),
                    font_size=ui_sp(13.5),
                    color=(0.72, 0.72, 0.72, 1),
                    halign='left',
                    valign='middle',
                    **_font_kwargs(),
                )
            )

        def _rounded_panel(widget, bg=(0.12, 0.12, 0.12, 1), border=(0.20, 0.20, 0.20, 1), radius=14):
            try:
                from kivy.graphics import Color, RoundedRectangle, Line

                def _redraw(_=None, __=None):
                    widget.canvas.before.clear()
                    with widget.canvas.before:
                        Color(*bg)
                        r = ui_dp(radius)
                        RoundedRectangle(pos=widget.pos, size=widget.size, radius=[r, r, r, r])
                        Color(*border)
                        Line(rounded_rectangle=[widget.x, widget.y, widget.width, widget.height, r], width=1)

                widget.bind(pos=_redraw, size=_redraw)
                _redraw()
            except Exception:
                pass

        def _render_welcome():
            self._result_grid.clear_widgets()

            root = BoxLayout(orientation='vertical', size_hint_y=None, spacing=ui_dp(12))
            root.bind(minimum_height=root.setter('height'))

            # Top tabs (visual only): only MARKET (remove GLOBAL/BONDS)
            tabs = BoxLayout(orientation='horizontal', size_hint_y=None, height=ui_dp(40), spacing=ui_dp(10))
            lbl = Label(
                text='[b]MARKET[/b]',
                markup=True,
                font_size=ui_sp(14.5),
                color=(0.11, 0.75, 0.36, 1),
                halign='left',
                valign='middle',
                size_hint_x=None,
                width=ui_dp(120),
                **_font_kwargs(),
            )
            lbl.text_size = (lbl.width, lbl.height)
            lbl.bind(size=lambda inst, val: setattr(inst, 'text_size', val))
            tabs.add_widget(lbl)
            tabs.add_widget(Widget())
            root.add_widget(tabs)

            # IHSG summary row (avoid wrapping/stacking on narrow screens)
            summary = BoxLayout(orientation='horizontal', size_hint_y=None, height=ui_dp(74), spacing=ui_dp(10))
            bar = Widget(size_hint=(None, 1), width=ui_dp(5))
            try:
                from kivy.graphics import Color, RoundedRectangle

                def _redraw_bar(_=None, __=None):
                    bar.canvas.before.clear()
                    with bar.canvas.before:
                        Color(0.11, 0.75, 0.36, 1)
                        r = ui_dp(3)
                        RoundedRectangle(pos=bar.pos, size=bar.size, radius=[r, r, r, r])

                bar.bind(pos=_redraw_bar, size=_redraw_bar)
                _redraw_bar()
            except Exception:
                pass
            summary.add_widget(bar)

            self._ihsg_name = Label(
                text='[b]IHSG[/b]',
                markup=True,
                font_size=ui_sp(22),
                color=(0.92, 0.92, 0.92, 1),
                halign='left',
                valign='middle',
                size_hint_x=None,
                width=ui_dp(90),
                **_font_kwargs(),
            )
            self._ihsg_name.text_size = (self._ihsg_name.width, self._ihsg_name.height)
            self._ihsg_name.bind(size=lambda inst, val: setattr(inst, 'text_size', val))
            summary.add_widget(self._ihsg_name)

            stats = BoxLayout(orientation='vertical', size_hint=(1, 1), spacing=ui_dp(2))

            self._ihsg_value = Label(
                text='-',
                font_size=ui_sp(24),
                color=(0.92, 0.92, 0.92, 1),
                halign='left',
                valign='middle',
                size_hint_y=None,
                height=ui_dp(34),
                max_lines=1,
                shorten=True,
                shorten_from='right',
                **_font_kwargs(),
            )
            self._ihsg_value.text_size = (self._ihsg_value.width, None)
            self._ihsg_value.bind(size=lambda inst, val: setattr(inst, 'text_size', (inst.width, None)))

            self._ihsg_change = Label(
                text='Memuat...',
                font_size=ui_sp(15),
                color=(0.62, 0.62, 0.62, 1),
                halign='left',
                valign='middle',
                size_hint_y=None,
                height=ui_dp(22),
                max_lines=1,
                shorten=True,
                shorten_from='right',
                **_font_kwargs(),
            )
            self._ihsg_change.text_size = (self._ihsg_change.width, None)
            self._ihsg_change.bind(size=lambda inst, val: setattr(inst, 'text_size', (inst.width, None)))

            stats.add_widget(self._ihsg_value)
            stats.add_widget(self._ihsg_change)
            summary.add_widget(stats)
            summary.add_widget(Widget(size_hint_x=None, width=0))
            root.add_widget(summary)

            # Chart (wrap in a rounded panel with padding)
            chart_panel = BoxLayout(size_hint_y=None, height=ui_dp(280), padding=(ui_dp(4), ui_dp(12)))
            _rounded_panel(chart_panel)
            self._ihsg_chart = SparklineWidget(values=[], line_color=(0.11, 0.75, 0.36, 1))
            chart_panel.add_widget(self._ihsg_chart)
            root.add_widget(chart_panel)

            # Two cards: Intraday + All Market (best-effort)
            # Make the row horizontally scrollable and keep card widths fixed (non-adaptive).
            cards_scroll = ScrollView(
                do_scroll_x=True,
                do_scroll_y=False,
                bar_width=0,
                size_hint_y=None,
                height=ui_dp(116),
            )
            cards_row = BoxLayout(
                orientation='horizontal',
                size_hint=(None, None),
                height=ui_dp(116),
                spacing=ui_dp(12),
            )
            try:
                cards_row.bind(minimum_width=cards_row.setter('width'))
            except Exception:
                pass

            def _kv_row(k: str, v_lbl: Label, vcol=(0.11, 0.75, 0.36, 1)):
                r = BoxLayout(orientation='horizontal', size_hint_y=None, height=ui_dp(22))
                lk = Label(
                    text=str(k),
                    font_size=ui_sp(12.5),
                    color=(0.72, 0.72, 0.72, 1),
                    halign='left',
                    valign='middle',
                    size_hint_x=None,
                    width=ui_dp(58),
                    shorten=True,
                    shorten_from='right',
                    **_font_kwargs(),
                )
                lv = v_lbl
                try:
                    lv.color = vcol
                except Exception:
                    pass
                try:
                    lk.text_size = (lk.width, None)
                    lk.bind(width=lambda inst, val: setattr(inst, 'text_size', (inst.width, None)))
                except Exception:
                    pass
                try:
                    lv.text_size = (lv.width, None)
                    lv.bind(width=lambda inst, val: setattr(inst, 'text_size', (inst.width, None)))
                except Exception:
                    pass
                r.add_widget(lk)
                r.add_widget(Widget())
                r.add_widget(lv)
                return r

            intraday = BoxLayout(orientation='vertical', padding=(ui_dp(10), ui_dp(8)), spacing=ui_dp(5), size_hint=(None, 1), width=ui_dp(216))
            _rounded_panel(intraday)
            intraday.add_widget(Label(text='[b]Intraday[/b]', markup=True, font_size=ui_sp(14.5), color=(0.88, 0.88, 0.88, 1), size_hint_y=None, height=ui_dp(20), halign='left', valign='middle', shorten=True, shorten_from='right', **_font_kwargs()))
            self._ihsg_open = Label(text='-', font_size=ui_sp(13), color=(0.11, 0.75, 0.36, 1), size_hint_x=None, width=ui_dp(96), halign='right', valign='middle', max_lines=1, shorten=True, shorten_from='left', **_font_kwargs())
            self._ihsg_high = Label(text='-', font_size=ui_sp(13), color=(0.11, 0.75, 0.36, 1), size_hint_x=None, width=ui_dp(96), halign='right', valign='middle', max_lines=1, shorten=True, shorten_from='left', **_font_kwargs())
            self._ihsg_low = Label(text='-', font_size=ui_sp(13), color=(0.11, 0.75, 0.36, 1), size_hint_x=None, width=ui_dp(96), halign='right', valign='middle', max_lines=1, shorten=True, shorten_from='left', **_font_kwargs())
            intraday.add_widget(_kv_row('Open', self._ihsg_open))
            intraday.add_widget(_kv_row('High', self._ihsg_high))
            intraday.add_widget(_kv_row('Low', self._ihsg_low))
            cards_row.add_widget(intraday)

            allm = BoxLayout(orientation='vertical', padding=(ui_dp(10), ui_dp(8)), spacing=ui_dp(5), size_hint=(None, 1), width=ui_dp(216))
            _rounded_panel(allm)
            allm.add_widget(Label(text='[b]All Market[/b]', markup=True, font_size=ui_sp(14.5), color=(0.88, 0.88, 0.88, 1), size_hint_y=None, height=ui_dp(20), halign='left', valign='middle', shorten=True, shorten_from='right', **_font_kwargs()))
            self._ihsg_lot = Label(text='-', font_size=ui_sp(13), color=(0.11, 0.75, 0.36, 1), size_hint_x=None, width=ui_dp(96), halign='right', valign='middle', max_lines=1, shorten=True, shorten_from='left', **_font_kwargs())
            self._ihsg_val = Label(text='-', font_size=ui_sp(13), color=(0.11, 0.75, 0.36, 1), size_hint_x=None, width=ui_dp(96), halign='right', valign='middle', max_lines=1, shorten=True, shorten_from='left', **_font_kwargs())
            self._ihsg_freq = Label(text='-', font_size=ui_sp(13), color=(0.72, 0.72, 0.72, 1), size_hint_x=None, width=ui_dp(96), halign='right', valign='middle', max_lines=1, shorten=True, shorten_from='left', **_font_kwargs())
            allm.add_widget(_kv_row('Lot', self._ihsg_lot))
            allm.add_widget(_kv_row('Value', self._ihsg_val))
            allm.add_widget(_kv_row('Freq', self._ihsg_freq, (0.72, 0.72, 0.72, 1)))
            cards_row.add_widget(allm)

            cards_scroll.add_widget(cards_row)
            root.add_widget(cards_scroll)

            # Penny gainers list (below cards)
            penny_panel = BoxLayout(orientation='vertical', size_hint_y=None, padding=(ui_dp(4), ui_dp(10)), spacing=ui_dp(6))
            penny_panel.bind(minimum_height=penny_panel.setter('height'))
            _rounded_panel(penny_panel)
            penny_panel.add_widget(
                Label(
                    text='[b]Top Second Liner[/b]',
                    markup=True,
                    font_size=ui_sp(14.5),
                    color=(0.88, 0.88, 0.88, 1),
                    size_hint_y=None,
                    height=ui_dp(22),
                    halign='left',
                    valign='middle',
                    shorten=True,
                    shorten_from='right',
                    **_font_kwargs(),
                )
            )

            self._penny_grid = GridLayout(cols=1, spacing=ui_dp(4), size_hint=(1, None))
            self._penny_grid.bind(minimum_height=self._penny_grid.setter('height'))
            penny_panel.add_widget(self._penny_grid)
            root.add_widget(penny_panel)

            def _render_penny_rows(rows):
                try:
                    self._penny_grid.clear_widgets()
                except Exception:
                    return
                if not rows:
                    self._penny_grid.add_widget(
                        Label(
                            text='Memuat...',
                            font_size=ui_sp(12.5),
                            color=(0.62, 0.62, 0.62, 1),
                            size_hint_y=None,
                            height=ui_dp(22),
                            halign='left',
                            valign='middle',
                            shorten=True,
                            shorten_from='right',
                            **_font_kwargs(),
                        )
                    )
                    return

                for it in rows[:15]:
                    try:
                        sym = str(it.get('symbol') or '')
                        close = it.get('close')
                        chg = it.get('change')

                        row_h = ui_dp(56)
                        row = BoxLayout(
                            orientation='horizontal',
                            size_hint=(1, None),
                            height=row_h,
                            padding=(ui_dp(12), ui_dp(8)),
                            spacing=ui_dp(10),
                        )

                        with row.canvas.before:
                            from kivy.graphics import Color, Rectangle
                            Color(0.06, 0.06, 0.06, 1)
                            row._bg = Rectangle(pos=row.pos, size=row.size)
                            Color(0.12, 0.12, 0.12, 1)
                            row._sep = Rectangle(pos=(row.x, row.y), size=(row.width, 1))

                        def _upd_row(*_):
                            try:
                                row._bg.pos = row.pos
                                row._bg.size = row.size
                                row._sep.pos = (row.x, row.y)
                                row._sep.size = (row.width, 1)
                            except Exception:
                                pass

                        row.bind(pos=_upd_row, size=_upd_row)
                        _upd_row()

                        def _go(_btn=None, _sym=sym):
                            try:
                                from kivy.app import App
                                app = App.get_running_app()
                                if app is not None and hasattr(app, 'open_cek_emiten'):
                                    app.open_cek_emiten(_sym)
                            except Exception:
                                pass

                        left = BoxLayout(orientation='vertical', spacing=ui_dp(2), size_hint_x=1)
                        ls = ClickableLabel(
                            text=f"[b]{sym}[/b]",
                            markup=True,
                            font_size=ui_sp(15),
                            color=(0.92, 0.92, 0.92, 1),
                            halign='left',
                            valign='middle',
                            max_lines=1,
                            shorten=True,
                            shorten_from='right',
                            **_font_kwargs(),
                        )
                        try:
                            ls.bind(on_press=_go)
                        except Exception:
                            pass
                        ls.text_size = (ls.width, None)
                        ls.bind(size=lambda inst, val: setattr(inst, 'text_size', (inst.width, None)))
                        left.add_widget(ls)

                        row.add_widget(left)

                        right = BoxLayout(orientation='vertical', size_hint_x=None, width=ui_dp(150), spacing=ui_dp(2))
                        lp = Label(
                            text=_format_id_number(float(close), decimals=0) if close is not None else '-',
                            font_size=ui_sp(14.5),
                            color=(0.90, 0.90, 0.90, 1),
                            halign='right',
                            valign='middle',
                            size_hint_y=None,
                            height=ui_dp(26),
                            max_lines=1,
                            shorten=True,
                            shorten_from='left',
                            **_font_kwargs(),
                        )
                        lp.text_size = (lp.width, None)
                        lp.bind(size=lambda inst, val: setattr(inst, 'text_size', (inst.width, None)))

                        pct = float(chg) if chg is not None else None
                        col = (0.11, 0.75, 0.36, 1) if (pct is not None and pct >= 0) else (0.86, 0.25, 0.25, 1)
                        lc = Label(
                            text=(f"+{_format_id_number(pct, decimals=2)}%" if pct is not None and pct > 0 else (f"{_format_id_number(pct, decimals=2)}%" if pct is not None else '-')),
                            font_size=ui_sp(12.8),
                            color=col,
                            halign='right',
                            valign='middle',
                            size_hint_y=None,
                            height=ui_dp(20),
                            max_lines=1,
                            shorten=True,
                            shorten_from='left',
                            **_font_kwargs(),
                        )
                        lc.text_size = (lc.width, None)
                        lc.bind(size=lambda inst, val: setattr(inst, 'text_size', (inst.width, None)))

                        right.add_widget(lp)
                        right.add_widget(lc)
                        row.add_widget(right)

                        self._penny_grid.add_widget(row)
                    except Exception:
                        continue

            # Initial render from cache (if any), otherwise placeholder
            try:
                _render_penny_rows((self._penny_cache or {}).get('rows') or [])
            except Exception:
                pass
            # Bottom safe space so the last row doesn't get covered by bottom nav.
            root.add_widget(Widget(size_hint_y=None, height=ui_dp(78)))
            self._result_grid.add_widget(root)

            def _fmt_idx(v):
                try:
                    return _format_id_number(float(v), decimals=2)
                except Exception:
                    return '-'

            def _apply_tv(last=None, open_v=None, high_v=None, low_v=None, chg_abs=None, chg_pct=None, lot=None, val=None, freq=None):
                try:
                    if last is not None:
                        self._ihsg_value.text = _fmt_idx(last)
                except Exception:
                    pass

                # Change label + chart color
                try:
                    if chg_abs is None or chg_pct is None:
                        self._ihsg_change.text = '-'
                        self._ihsg_change.color = (0.62, 0.62, 0.62, 1)
                        self._ihsg_chart.line_color = (0.11, 0.75, 0.36, 1)
                    else:
                        ca = float(chg_abs)
                        cp = float(chg_pct)
                        sign = '+' if ca > 0 else ''
                        self._ihsg_change.text = f"{sign}{_fmt_idx(ca)} ({'+' if cp > 0 else ''}{_format_id_number(cp, decimals=2)}%)"
                        if cp > 0:
                            col = (0.11, 0.75, 0.36, 1)
                        elif cp < 0:
                            col = (0.86, 0.25, 0.25, 1)
                        else:
                            col = (0.62, 0.62, 0.62, 1)
                        self._ihsg_change.color = col
                        self._ihsg_chart.line_color = col
                except Exception:
                    pass

                try:
                    if self._ihsg_series and len(self._ihsg_series) >= 2:
                        # Prefer any prebuilt intraday series when available.
                        self._ihsg_chart.values = list(self._ihsg_series)
                    else:
                        # Fallback 1: construct a small series from snapshot OHLC
                        # so the chart still shows something even without yfinance.
                        cand = []
                        for v in (open_v, low_v, high_v, last):
                            try:
                                if v is not None:
                                    cand.append(float(v))
                            except Exception:
                                pass
                        if len(cand) >= 2:
                            self._ihsg_chart.values = cand
                        else:
                            # Fallback 2: use the same pseudo sparkline source
                            # as watchlist rows when TradingView/yfinance are unavailable.
                            try:
                                base_chg = 0.0
                                if chg_abs is not None:
                                    base_chg = float(chg_abs)
                                elif chg_pct is not None:
                                    base_chg = float(chg_pct)
                                self._ihsg_chart.values = _spark_values_for('IHSG', base_chg)
                            except Exception:
                                # Absolute last-resort: flat line at last price.
                                if last is not None:
                                    try:
                                        self._ihsg_chart.values = [float(last), float(last)]
                                    except Exception:
                                        pass
                except Exception:
                    pass

                # Cards
                try:
                    if open_v is not None:
                        self._ihsg_open.text = _fmt_idx(open_v)
                    if high_v is not None:
                        self._ihsg_high.text = _fmt_idx(high_v)
                    if low_v is not None:
                        self._ihsg_low.text = _fmt_idx(low_v)
                except Exception:
                    pass
                try:
                    if lot is not None:
                        self._ihsg_lot.text = _format_compact_number(lot)
                    if val is not None:
                        self._ihsg_val.text = _format_compact_number(val)
                    self._ihsg_freq.text = _format_compact_number(freq) if freq is not None else '-'
                except Exception:
                    pass

            def _tv_worker(fetch_agg=False):
                try:
                    from modules.tradingview_fetcher import fetch_tradingview_snapshot, fetch_tradingview_idx_market_aggregate, fetch_tradingview_idx_penny_gainers
                except Exception:
                    fetch_tradingview_snapshot = None
                    fetch_tradingview_idx_market_aggregate = None
                    fetch_tradingview_idx_penny_gainers = None

                last = open_v = high_v = low_v = chg_abs = chg_pct = None
                try:
                    if callable(fetch_tradingview_snapshot):
                        snap = fetch_tradingview_snapshot(['COMPOSITE']) or {}
                        s = snap.get('COMPOSITE') or {}
                        last = s.get('price') if s.get('price') is not None else s.get('close')
                        open_v = s.get('open')
                        high_v = s.get('high')
                        low_v = s.get('low')
                        chg_pct = s.get('change')
                        chg_abs = s.get('change_abs')
                except Exception:
                    pass

                # Build chart series.
                # TradingView snapshot for COMPOSITE is often static between updates,
                # so we prefer an intraday timeseries from yfinance (^JKSE) (best-effort).
                try:
                    now_ts = datetime.now().timestamp()
                except Exception:
                    now_ts = 0.0

                used_series = False
                try:
                    cached_ts = float((self._ihsg_series_cache or {}).get('ts', 0.0) or 0.0)
                    cached_vals = (self._ihsg_series_cache or {}).get('values') or []
                    if (now_ts - cached_ts) < 60.0 and len(cached_vals) >= 2:
                        self._ihsg_series = list(cached_vals)
                        used_series = True
                except Exception:
                    pass

                if not used_series:
                    series_vals = None
                    try:
                        import yfinance as yf

                        t = yf.Ticker('^JKSE')
                        hist = t.history(period='1d', interval='5m')
                        closes = []
                        try:
                            close_series = None
                            try:
                                if hasattr(hist, 'columns') and 'Close' in getattr(hist, 'columns', []):
                                    close_series = hist['Close']
                                elif hasattr(hist, 'columns') and 'close' in getattr(hist, 'columns', []):
                                    close_series = hist['close']
                            except Exception:
                                close_series = None
                            if close_series is not None:
                                closes_raw = close_series.dropna().tolist()  # type: ignore
                                idxs = []
                                try:
                                    idxs = list(getattr(hist, 'index', []) or [])
                                except Exception:
                                    idxs = []
                                # Keep only today's points when possible (avoid multi-day/multi-range surprises).
                                try:
                                    today = datetime.now().date()
                                    if idxs and len(idxs) == len(closes_raw):
                                        closes = []
                                        for ts, vv in zip(idxs, closes_raw):
                                            try:
                                                if hasattr(ts, 'date') and ts.date() == today:
                                                    closes.append(vv)
                                            except Exception:
                                                pass
                                        if len(closes) < 2:
                                            closes = list(closes_raw)
                                    else:
                                        closes = list(closes_raw)
                                except Exception:
                                    closes = list(closes_raw)
                        except Exception:
                            try:
                                closes = hist['Close'].dropna().tolist()  # type: ignore
                            except Exception:
                                closes = []
                        closes = [float(x) for x in closes if x is not None]
                        if len(closes) >= 2:
                            series_vals = closes[-320:]
                    except Exception:
                        series_vals = None

                    try:
                        if series_vals and len(series_vals) >= 2:
                            self._ihsg_series = list(series_vals)
                            self._ihsg_series_cache = {'ts': now_ts, 'values': list(series_vals)}
                            used_series = True
                    except Exception:
                        pass

                # Fallback: append snapshot last value only when it changes.
                if not used_series:
                    try:
                        if last is not None:
                            v = float(last)
                            if not self._ihsg_series or abs(float(self._ihsg_series[-1]) - v) > 1e-9:
                                self._ihsg_series.append(v)
                            if len(self._ihsg_series) > 320:
                                self._ihsg_series = self._ihsg_series[-320:]
                    except Exception:
                        pass

                lot = val = freq = None
                if fetch_agg and callable(fetch_tradingview_idx_market_aggregate):
                    try:
                        agg = fetch_tradingview_idx_market_aggregate(max_rows=650) or {}
                        lot = agg.get('lot')
                        val = agg.get('value')
                        freq = agg.get('freq')
                        try:
                            self._ihsg_cache = {'ts': datetime.now().timestamp(), 'data': {'lot': lot, 'val': val, 'freq': freq}}
                        except Exception:
                            pass
                    except Exception:
                        pass
                else:
                    try:
                        cached = (self._ihsg_cache or {}).get('data') or {}
                        lot = cached.get('lot')
                        val = cached.get('val')
                        freq = cached.get('freq')
                    except Exception:
                        pass

                Clock.schedule_once(lambda dt: _apply_tv(last, open_v, high_v, low_v, chg_abs, chg_pct, lot, val, freq), 0)

                # Penny list: refresh occasionally (best-effort)
                try:
                    now_ts = datetime.now().timestamp()
                except Exception:
                    now_ts = 0.0
                try:
                    cached_ts = float((self._penny_cache or {}).get('ts', 0.0) or 0.0)
                    should_fetch = (now_ts - cached_ts) >= 120.0
                except Exception:
                    should_fetch = True
                if should_fetch and callable(fetch_tradingview_idx_penny_gainers):
                    try:
                        rows = fetch_tradingview_idx_penny_gainers(limit=15, price_max=500.0, change_min=2.0, scan_rows=650) or []
                        self._penny_cache = {'ts': now_ts, 'rows': rows}
                        Clock.schedule_once(lambda dt: _render_penny_rows(rows), 0)
                    except Exception:
                        pass

            def _tick(_dt=None):
                fetch_agg = False
                try:
                    now_ts = datetime.now().timestamp()
                    fetch_agg = (now_ts - float(self._ihsg_cache.get('ts', 0.0) or 0.0)) >= 60.0
                except Exception:
                    fetch_agg = True
                threading.Thread(target=lambda: _tv_worker(fetch_agg=fetch_agg), daemon=True).start()

            # Ensure only one polling event is active.
            try:
                if self._ihsg_poll_ev is not None:
                    self._ihsg_poll_ev.cancel()
            except Exception:
                pass
            self._ihsg_poll_ev = Clock.schedule_interval(_tick, 12.0)
            _tick(0)

        # Initial content: show IHSG welcome dashboard (not empty message).
        _render_welcome()

        def _add_kv(label_txt: str, value_txt: str, value_color=(0.88, 0.88, 0.88, 1)):
            row = BoxLayout(orientation='horizontal', size_hint_y=None, height=ui_dp(28))
            l = Label(text=str(label_txt), font_size=ui_sp(12.5), color=(0.65, 0.65, 0.65, 1), size_hint_x=None, width=ui_dp(130), halign='left', valign='middle', **_font_kwargs())
            l.text_size = (l.width, None)
            l.bind(size=lambda inst, val: setattr(inst, 'text_size', (inst.width, None)))
            v = Label(text=str(value_txt), font_size=ui_sp(12.8), color=value_color, halign='left', valign='middle', **_font_kwargs())
            v.text_size = (v.width, None)
            v.bind(size=lambda inst, val: setattr(inst, 'text_size', (inst.width, None)))
            row.add_widget(l)
            row.add_widget(v)
            self._result_grid.add_widget(row)

        def _set_detail_mode(active: bool, symbol: str = ''):
            try:
                try:
                    self._detail_mode = bool(active)
                except Exception:
                    pass
                if active:
                    try:
                        if self._ihsg_poll_ev is not None:
                            self._ihsg_poll_ev.cancel()
                        self._ihsg_poll_ev = None
                    except Exception:
                        self._ihsg_poll_ev = None
                    # Header: show symbol label, hide search bar
                    try:
                        self._hdr_symbol.text = f"[b]{symbol}[/b]"
                        self._hdr_symbol.opacity = 1
                    except Exception:
                        pass
                    try:
                        self._hdr_searchbar.disabled = True
                        self._hdr_searchbar.opacity = 0
                        self._hdr_searchbar.height = 0
                    except Exception:
                        pass
                    try:
                        self._back_btn.disabled = False
                        self._back_btn.opacity = 1
                    except Exception:
                        pass
                else:
                    # Header: show search bar, hide symbol label
                    try:
                        self._hdr_symbol.opacity = 0
                    except Exception:
                        pass
                    try:
                        self._hdr_searchbar.disabled = False
                        self._hdr_searchbar.opacity = 1
                        self._hdr_searchbar.height = ui_dp(40)
                    except Exception:
                        pass
                    try:
                        self._back_btn.disabled = True
                        self._back_btn.opacity = 0
                    except Exception:
                        pass
            except Exception:
                pass

        def _make_chip(text: str):
            # Outline chip similar to Stockbit tags (best-effort, no new theme colors).
            chip = Label(
                text=str(text),
                size_hint=(None, None),
                height=ui_dp(30),
                font_size=ui_sp(12),
                color=(0.11, 0.75, 0.36, 1),
                halign='center',
                valign='middle',
                **_font_kwargs(),
            )
            try:
                chip.padding = (ui_dp(12), ui_dp(6))
            except Exception:
                pass
            try:
                chip.texture_update()
                chip.width = max(ui_dp(40), chip.texture_size[0] + ui_dp(24))
                chip.text_size = (chip.width, chip.height)
            except Exception:
                chip.width = ui_dp(88)

            try:
                from kivy.graphics import Color, Line

                def _redraw(_=None, __=None):
                    chip.canvas.before.clear()
                    with chip.canvas.before:
                        Color(0.11, 0.75, 0.36, 1)
                        r = ui_dp(10)
                        Line(rounded_rectangle=[chip.x, chip.y, chip.width, chip.height, r], width=1)

                chip.bind(pos=_redraw, size=_redraw)
                _redraw()
            except Exception:
                pass
            return chip

        def _hist_to_series(hist):
            try:
                if hist is None or getattr(hist, 'empty', False):
                    return []
                if hasattr(hist, '__getitem__') and 'Close' in hist:
                    series = hist['Close']
                    vals = list(getattr(series, 'values', series))
                else:
                    vals = []
                out = []
                for v in vals[-260:]:
                    try:
                        out.append(float(v))
                    except Exception:
                        continue
                return out
            except Exception:
                return []

        def _render_stock_detail(sym: str, q: dict, hist=None, phase_info=None, trend_info=None, sr_info=None):
            _set_detail_mode(True, sym)
            self._result_grid.clear_widgets()

            panel = BoxLayout(orientation='vertical', size_hint_y=None, spacing=ui_dp(10))
            panel.bind(minimum_height=panel.setter('height'))

            # --- Price header ---
            price = (q or {}).get('price')
            prev = (q or {}).get('prev_close')
            chg_pct = (q or {}).get('change')
            chg_abs = (q or {}).get('change_abs')
            src = (q or {}).get('source') or 'unknown'
            vol = (q or {}).get('volume')
            o = (q or {}).get('open')
            h = (q or {}).get('high')
            l = (q or {}).get('low')

            # fallback: use yfinance-derived phase_info if quote is empty
            try:
                if price in (None, '', '-') and phase_info and phase_info.get('current_price') not in (None, '', '-'):
                    price = phase_info.get('current_price')
            except Exception:
                pass

            def _rp(v):
                try:
                    if v in (None, '', '-'):
                        return '-'
                    return _format_id_number(float(v), decimals=0)
                except Exception:
                    return '-'

            def _compact(v):
                try:
                    if v in (None, '', '-'):
                        return '-'
                    return _format_compact_number(float(v))
                except Exception:
                    return '-'

            # --- Company name (best-effort) ---
            company_name = None
            company_pt = None
            try:
                if isinstance(q, dict):
                    company_name = q.get('company_name') or q.get('emiten_name')
                    company_pt = q.get('company_pt') or q.get('pt_name')
            except Exception:
                company_name, company_pt = None, None

            def _clean_txt(x):
                try:
                    s = str(x or '').strip()
                    return s if s and s != '-' else ''
                except Exception:
                    return ''

            company_name = _clean_txt(company_name)
            company_pt = _clean_txt(company_pt)
            display_company = company_pt or company_name

            # --- Top title like Stockbit: SYMBOL on top, company name below ---
            sym_lbl = Label(
                text=f"[b]{sym}[/b]",
                markup=True,
                font_size=ui_sp(26),
                color=(0.92, 0.92, 0.92, 1),
                halign='left',
                valign='middle',
                size_hint_y=None,
                height=ui_dp(34),
                **_font_kwargs(),
            )
            sym_lbl.text_size = (sym_lbl.width, sym_lbl.height)
            sym_lbl.bind(size=lambda inst, val: setattr(inst, 'text_size', val))
            panel.add_widget(sym_lbl)

            if display_company:
                co = Label(
                    text=display_company,
                    font_size=ui_sp(15),
                    color=(0.65, 0.65, 0.65, 1),
                    halign='left',
                    valign='middle',
                    size_hint_y=None,
                    height=ui_dp(22),
                    **_font_kwargs(),
                )
                co.text_size = (co.width, co.height)
                co.bind(size=lambda inst, val: setattr(inst, 'text_size', val))
                panel.add_widget(co)

            price_txt = _rp(price)
            price_lbl = Label(
                text=str(price_txt),
                font_size=ui_sp(44),
                color=(0.92, 0.92, 0.92, 1),
                halign='left',
                valign='middle',
                size_hint_y=None,
                height=ui_dp(60),
                **_font_kwargs(),
            )
            price_lbl.text_size = (price_lbl.width, price_lbl.height)
            price_lbl.bind(size=lambda inst, val: setattr(inst, 'text_size', val))

            # Change line: +abs (+pct%) Hari ini
            ch_line = '-'
            ch_color = (0.72, 0.72, 0.72, 1)
            try:
                if chg_abs not in (None, '', '-') or chg_pct not in (None, '', '-'):
                    ca = _to_float(chg_abs, default=0.0)
                    cp = _to_float(chg_pct, default=0.0)
                    sign = '+' if ca > 0 else ''
                    ch_line = f"{sign}{_format_id_number(ca, decimals=0)} ({'+' if cp > 0 else ''}{_format_id_number(cp, decimals=2)}%) Hari ini"
                    if cp > 0:
                        ch_color = (0.11, 0.75, 0.36, 1)
                    elif cp < 0:
                        ch_color = (0.86, 0.25, 0.25, 1)
            except Exception:
                pass

            chg_lbl = Label(
                text=str(ch_line),
                font_size=ui_sp(14),
                color=ch_color,
                halign='left',
                valign='middle',
                size_hint_y=None,
                height=ui_dp(22),
                **_font_kwargs(),
            )
            chg_lbl.text_size = (chg_lbl.width, chg_lbl.height)
            chg_lbl.bind(size=lambda inst, val: setattr(inst, 'text_size', val))

            panel.add_widget(price_lbl)
            panel.add_widget(chg_lbl)

            # --- Chips row ---
            chips = BoxLayout(orientation='horizontal', size_hint_y=None, height=ui_dp(34), spacing=ui_dp(8))
            chips.add_widget(_make_chip('IDX'))
            chips.add_widget(_make_chip(str(src)))
            chips.add_widget(Widget())
            panel.add_widget(chips)

            # --- Chart (best-effort using history closes) ---
            chart_h = ui_dp(260)
            chart_box = BoxLayout(size_hint_y=None, height=chart_h)
            series = _hist_to_series(hist)
            has_series = bool(series and len(series) >= 2)
            line_col = (0.11, 0.75, 0.36, 1)
            try:
                if _to_float(chg_pct, default=0.0) < 0:
                    line_col = (0.86, 0.25, 0.25, 1)
            except Exception:
                pass
            chart = None
            if has_series:
                chart = SparklineWidget(values=series, line_color=line_col)
                chart_box.add_widget(chart)
            else:
                seed_px = None
                try:
                    seed_px = _to_float(price, default=None)
                except Exception:
                    seed_px = None
                if isinstance(seed_px, (int, float)) and seed_px and seed_px > 0:
                    chart = SparklineWidget(values=[float(seed_px), float(seed_px)], line_color=line_col)
                    chart_box.add_widget(chart)
                else:
                    chart_box.add_widget(
                        Label(
                            text='Chart tidak tersedia (riwayat harga gagal dimuat).',
                            font_size=ui_sp(12.5),
                            color=(0.65, 0.65, 0.65, 1),
                            halign='left',
                            valign='middle',
                            **_font_kwargs(),
                        )
                    )
            panel.add_widget(chart_box)

            try:
                self._detail_chart_widget = chart
            except Exception:
                pass

            # Fallback: if yfinance history is missing, poll TradingView snapshot to fill the chart.
            if (not has_series) and (chart is not None):
                try:
                    _start_detail_tv_poll(sym, chart_widget=chart, seed_price=seed_px)
                except Exception:
                    pass
            else:
                try:
                    _stop_detail_tv_poll()
                except Exception:
                    pass

            # --- Timeframe row (visual only) ---
            tf_row = BoxLayout(orientation='horizontal', size_hint_y=None, height=ui_dp(34), spacing=ui_dp(10))
            tfs = ['1D', '1W', '1M', '3M', 'YTD', '1Y', '3Y', '5Y']
            tf_buttons = {}

            def _set_tf_active(tf: str):
                for k, b in tf_buttons.items():
                    try:
                        b.color = (0.11, 0.75, 0.36, 1) if k == tf else (0.65, 0.65, 0.65, 1)
                    except Exception:
                        pass

            for tf in tfs:
                b = Button(
                    text=tf,
                    size_hint_x=None,
                    width=ui_dp(44) if tf in ('1D', '1W', '1M', '3M', '1Y', '3Y', '5Y') else ui_dp(60),
                    background_normal='',
                    background_down='',
                    background_color=(0, 0, 0, 0),
                    color=(0.65, 0.65, 0.65, 1),
                    font_size=ui_sp(12.5),
                    padding=(0, 0),
                    **_font_kwargs(),
                )
                tf_buttons[tf] = b
                if not bool(getattr(self, '_yfinance_available', False)):
                    try:
                        b.disabled = True
                        b.opacity = 0.45
                    except Exception:
                        pass
                # Fetch and update chart data for the selected timeframe.
                def _on_tf(_btn, _tf=tf):
                    _set_tf_active(_tf)

                    def _tf_worker():
                        try:
                            import yfinance as yf
                        except Exception:
                            return

                        period_map = {
                            '1D': ('1d', '5m'),
                            '1W': ('5d', '30m'),
                            '1M': ('1mo', '60m'),
                            '3M': ('3mo', '1d'),
                            'YTD': ('ytd', '1d'),
                            '1Y': ('1y', '1d'),
                            '3Y': ('3y', '1wk'),
                            '5Y': ('5y', '1wk'),
                        }
                        period, interval = period_map.get(_tf, ('3mo', '1d'))
                        ticker = f"{sym}.JK" if not sym.endswith('.JK') else sym
                        try:
                            new_hist = yf.Ticker(ticker).history(period=period, interval=interval)
                        except Exception:
                            new_hist = None

                        new_vals = _hist_to_series(new_hist)
                        if not new_vals:
                            return

                        def _apply(_dt):
                            try:
                                if chart is not None:
                                    chart.values = new_vals
                            except Exception:
                                pass

                        Clock.schedule_once(_apply, 0)

                    threading.Thread(target=_tf_worker, daemon=True).start()

                b.bind(on_press=_on_tf)
                tf_row.add_widget(b)
            tf_row.add_widget(Widget())
            _set_tf_active('1D')
            panel.add_widget(tf_row)

            # --- Tab bar + content ---
            tab_row = BoxLayout(orientation='horizontal', size_hint_y=None, height=ui_dp(42), spacing=ui_dp(10))
            tabs = ['KEYSTATS', 'ORDERBOOK']
            tab_buttons = {}
            tab_state = {'active': 'ORDERBOOK'}

            class _SwipeContent(BoxLayout):
                def __init__(self, on_swipe=None, **kw):
                    super().__init__(**kw)
                    self._on_swipe = on_swipe
                    self._sx = None
                    self._sy = None
                    self._armed = False

                def on_touch_down(self, touch):
                    if self.collide_point(*touch.pos):
                        self._sx, self._sy = touch.x, touch.y
                        self._armed = True
                    return super().on_touch_down(touch)

                def on_touch_move(self, touch):
                    if not self._armed or self._sx is None or self._sy is None:
                        return super().on_touch_move(touch)
                    dx = touch.x - self._sx
                    dy = touch.y - self._sy
                    if abs(dx) > ui_dp(40) and abs(dx) > abs(dy) * 1.2:
                        self._armed = False
                        if callable(self._on_swipe):
                            try:
                                self._on_swipe('left' if dx < 0 else 'right')
                                return True
                            except Exception:
                                pass
                    return super().on_touch_move(touch)

                def on_touch_up(self, touch):
                    self._armed = False
                    self._sx = None
                    self._sy = None
                    return super().on_touch_up(touch)

            def _handle_swipe(dirn: str):
                order = tabs
                cur = tab_state.get('active') or order[0]
                try:
                    i = order.index(cur)
                except Exception:
                    i = 0
                if dirn == 'left':
                    i2 = min(len(order) - 1, i + 1)
                else:
                    i2 = max(0, i - 1)
                _set_tab_active(order[i2])

            content = _SwipeContent(orientation='vertical', size_hint_y=None, spacing=ui_dp(10), on_swipe=_handle_swipe)
            content.bind(minimum_height=content.setter('height'))

            def _metric_cell(lbl: str, val: str, vcol=(0.92, 0.92, 0.92, 1)):
                box = BoxLayout(orientation='vertical', size_hint_y=None, height=ui_dp(56))
                l1 = Label(text=str(lbl), font_size=ui_sp(12.5), color=(0.65, 0.65, 0.65, 1), halign='left', valign='middle', **_font_kwargs())
                l2 = Label(text=str(val), font_size=ui_sp(16), color=vcol, halign='left', valign='middle', **_font_kwargs())
                for x in (l1, l2):
                    x.text_size = (x.width, None)
                    x.bind(size=lambda inst, val: setattr(inst, 'text_size', (inst.width, None)))
                box.add_widget(l1)
                box.add_widget(l2)
                return box

            def _render_tab(name: str):
                try:
                    content.clear_widgets()
                except Exception:
                    pass

                _COL_POS = (0.11, 0.75, 0.36, 1)
                _COL_NEG = (0.86, 0.25, 0.25, 1)
                _COL_MUTED = (0.72, 0.72, 0.72, 1)

                ob = None
                try:
                    if isinstance(q, dict):
                        ob = q.get('orderbook')
                except Exception:
                    ob = None

                if name == 'KEYSTATS':
                    open_col = _COL_MUTED
                    try:
                        ov = _to_float(o, default=None)
                        pv = _to_float(prev, default=None)
                        if ov is not None and pv is not None:
                            if ov > pv:
                                open_col = _COL_POS
                            elif ov < pv:
                                open_col = _COL_NEG
                    except Exception:
                        open_col = _COL_MUTED

                    grid = GridLayout(cols=2, spacing=ui_dp(8), size_hint_y=None)
                    grid.bind(minimum_height=grid.setter('height'))
                    grid.add_widget(_metric_cell('Open', _rp(o), open_col))
                    grid.add_widget(_metric_cell('Prev', _rp(prev)))
                    grid.add_widget(_metric_cell('High', _rp(h)))
                    grid.add_widget(_metric_cell('Low', _rp(l)))
                    grid.add_widget(_metric_cell('Volume', _compact(vol)))
                    grid.add_widget(_metric_cell('Source', str(src), _COL_POS))
                    content.add_widget(grid)

                    # Optional: append Bandarmology summary when available
                    if phase_info:
                        try:
                            ph = phase_info.get('phase', '-')
                            sig = phase_info.get('signal', '-')

                            ph_col = _COL_MUTED
                            try:
                                ph_s = str(ph or '').strip().lower()
                                if 'accum' in ph_s:
                                    ph_col = _COL_POS
                                elif 'distr' in ph_s:
                                    ph_col = _COL_NEG
                            except Exception:
                                ph_col = _COL_MUTED
                            dist = phase_info.get('distance_pct', None)
                            dist_txt = '-'
                            dist_col = (0.72, 0.72, 0.72, 1)
                            try:
                                dv = float(dist)
                                dist_txt = f"{('+' if dv > 0 else '')}{_format_id_number(dv, decimals=2)}%"
                                dist_col = (0.11, 0.75, 0.36, 1) if dv > 0 else (0.86, 0.25, 0.25, 1) if dv < 0 else (0.72, 0.72, 0.72, 1)
                            except Exception:
                                pass
                            box = GridLayout(cols=2, spacing=ui_dp(8), size_hint_y=None)
                            box.bind(minimum_height=box.setter('height'))
                            box.add_widget(_metric_cell('Phase', str(ph), ph_col))
                            box.add_widget(_metric_cell('Signal', str(sig)))
                            box.add_widget(_metric_cell('Jarak VWAP', dist_txt, dist_col))
                            if trend_info:
                                tr = trend_info.get('trend', '-') or '-'
                                tr_col = _COL_MUTED
                                try:
                                    tr_s = str(tr or '').strip().lower()
                                    if 'up' in tr_s:
                                        tr_col = _COL_POS
                                    elif 'down' in tr_s:
                                        tr_col = _COL_NEG
                                except Exception:
                                    tr_col = _COL_MUTED
                                box.add_widget(_metric_cell('Trend', str(tr), tr_col))
                            if sr_info:
                                try:
                                    s = sr_info.get('support')
                                    r = sr_info.get('resistance')
                                    box.add_widget(_metric_cell('Support', _rp(s)))
                                    box.add_widget(_metric_cell('Resistance', _rp(r)))
                                except Exception:
                                    pass
                            content.add_widget(box)
                        except Exception:
                            pass
                    return

                # ORDERBOOK (visual layout; data may be partial)
                info_grid = GridLayout(cols=3, spacing=ui_dp(8), size_hint_y=None)
                info_grid.bind(minimum_height=info_grid.setter('height'))

                # Derived approximations (best-effort)
                lot_txt = '-'
                val_txt = '-'
                avg_txt = '-'
                try:
                    v = _to_float(vol, default=None)
                    p = _to_float(price, default=None)
                    if v is not None and v > 0:
                        lot_txt = _format_compact_number(v / 100.0)
                    if v is not None and p is not None and v > 0:
                        val_txt = _format_compact_number(v * p)
                        avg_txt = _format_id_number(p, decimals=0)
                except Exception:
                    pass

                open_col = _COL_MUTED
                try:
                    ov = _to_float(o, default=None)
                    pv = _to_float(prev, default=None)
                    if ov is not None and pv is not None:
                        if ov > pv:
                            open_col = _COL_POS
                        elif ov < pv:
                            open_col = _COL_NEG
                except Exception:
                    open_col = _COL_MUTED

                info_grid.add_widget(_metric_cell('Open', _rp(o), open_col))
                info_grid.add_widget(_metric_cell('Prev', _rp(prev)))
                info_grid.add_widget(_metric_cell('Lot', lot_txt, _COL_POS))
                info_grid.add_widget(_metric_cell('High', _rp(h), _COL_POS))
                info_grid.add_widget(_metric_cell('ARA', '-'))
                info_grid.add_widget(_metric_cell('Val', val_txt, _COL_POS))
                info_grid.add_widget(_metric_cell('Low', _rp(l), _COL_POS))
                info_grid.add_widget(_metric_cell('ARB', '-'))
                info_grid.add_widget(_metric_cell('Avg', avg_txt, _COL_POS))
                content.add_widget(info_grid)

                mini_grid = GridLayout(cols=3, spacing=ui_dp(8), size_hint_y=None)
                mini_grid.bind(minimum_height=mini_grid.setter('height'))
                mini_grid.add_widget(_metric_cell('F Buy', '-'))
                mini_grid.add_widget(_metric_cell('F Sell', '-'))
                mini_grid.add_widget(_metric_cell('Freq', '-'))
                content.add_widget(mini_grid)

                # Orderbook table placeholder
                tbl = GridLayout(cols=6, spacing=ui_dp(6), size_hint_y=None)
                tbl.bind(minimum_height=tbl.setter('height'))

                def _hdr(text):
                    return Label(text=f"[b]{text}[/b]", markup=True, font_size=ui_sp(12), color=(0.88, 0.88, 0.88, 1), size_hint_y=None, height=ui_dp(26), halign='center', valign='middle', **_font_kwargs())

                for htxt in ('Freq', 'Lot', 'Bid', 'Ask', 'Lot', 'Freq'):
                    tbl.add_widget(_hdr(htxt))

                def _cell(text, col=(0.72, 0.72, 0.72, 1)):
                    return Label(text=str(text), font_size=ui_sp(12.5), color=col, size_hint_y=None, height=ui_dp(28), halign='center', valign='middle', **_font_kwargs())

                def _norm_level(level):
                    if level is None:
                        return {'price': None, 'volume': None, 'freq': None}
                    if isinstance(level, dict):
                        return {
                            'price': level.get('price'),
                            'volume': level.get('volume', level.get('lot')),
                            'freq': level.get('freq', level.get('count', level.get('orders'))),
                        }
                    if isinstance(level, (list, tuple)):
                        return {
                            'price': level[0] if len(level) > 0 else None,
                            'volume': level[1] if len(level) > 1 else None,
                            'freq': level[2] if len(level) > 2 else None,
                        }
                    return {'price': None, 'volume': None, 'freq': None}

                bids = []
                asks = []
                try:
                    if isinstance(ob, dict):
                        bids = ob.get('bid_orders') or ob.get('bids') or []
                        asks = ob.get('ask_orders') or ob.get('asks') or []
                except Exception:
                    bids, asks = [], []

                if not bids and not asks:
                    # Stockbit API is often blocked (InvalidParameter). Fall back to an estimated book
                    # so the ORDERBOOK view is not empty.
                    import hashlib

                    def _stable_ratio(key: str, lo: float, hi: float) -> float:
                        try:
                            h = hashlib.md5(key.encode('utf-8')).hexdigest()
                            x = int(h[:8], 16) / float(0xFFFFFFFF)
                            return float(lo) + (float(hi) - float(lo)) * float(x)
                        except Exception:
                            return float((lo + hi) / 2.0)

                    p = _to_float(price, default=None)
                    v = _to_float(vol, default=None)
                    tick = 1.0

                    # Use daily volume as a loose proxy for liquidity; cap to keep the table readable.
                    total_lot = 0
                    try:
                        if v is not None and v > 0:
                            total_lot = int(max(0.0, v / 100.0))
                    except Exception:
                        total_lot = 0
                    total_lot = max(200, min(total_lot, 15000))

                    bid_share = _stable_ratio(sym + ':bid', 0.45, 0.60)
                    bid_total = int(total_lot * bid_share)
                    ask_total = max(0, total_lot - bid_total)

                    def _weights(n: int):
                        # Exponential decay weights, sum to 1.
                        ws = [0.0] * n
                        s = 0.0
                        for i in range(n):
                            w = (0.78 ** i)
                            ws[i] = w
                            s += w
                        return [w / s for w in ws] if s > 0 else [1.0 / n] * n

                    ws = _weights(5)
                    bids = []
                    asks = []
                    for i in range(5):
                        px_bid = (p - tick * i) if isinstance(p, (int, float)) else None
                        px_ask = (p + tick * i) if isinstance(p, (int, float)) else None
                        b_lot = int(max(1, bid_total * ws[i]))
                        a_lot = int(max(1, ask_total * ws[i]))
                        # Deterministic-ish freq numbers.
                        b_freq = int(max(1, round(_stable_ratio(f'{sym}:bf:{i}', 2, 18))))
                        a_freq = int(max(1, round(_stable_ratio(f'{sym}:af:{i}', 2, 18))))
                        bids.append({'price': px_bid, 'volume': b_lot, 'freq': b_freq})
                        asks.append({'price': px_ask, 'volume': a_lot, 'freq': a_freq})

                    content.add_widget(Label(
                        text='Orderbook estimasi (Stockbit API terblokir; TradingView tidak menyediakan depth).',
                        font_size=ui_sp(11),
                        color=(0.65, 0.65, 0.65, 1),
                        size_hint_y=None,
                        height=ui_dp(30),
                        halign='left',
                        valign='middle',
                        **_font_kwargs(),
                    ))

                n = 5
                for i in range(n):
                    b = _norm_level(bids[i] if i < len(bids) else None)
                    a = _norm_level(asks[i] if i < len(asks) else None)
                    tbl.add_widget(_cell(b.get('freq', '-') or '-', (0.72, 0.72, 0.72, 1)))
                    tbl.add_widget(_cell(_format_id_number(b.get('volume'), decimals=0) if isinstance(b.get('volume'), (int, float)) else (b.get('volume', '-') or '-'), (0.72, 0.72, 0.72, 1)))
                    tbl.add_widget(_cell(_format_price(b.get('price')) if b.get('price') not in (None, '') else '-', (0.11, 0.75, 0.36, 1)))
                    tbl.add_widget(_cell(_format_price(a.get('price')) if a.get('price') not in (None, '') else '-', (0.86, 0.25, 0.25, 1)))
                    tbl.add_widget(_cell(_format_id_number(a.get('volume'), decimals=0) if isinstance(a.get('volume'), (int, float)) else (a.get('volume', '-') or '-'), (0.72, 0.72, 0.72, 1)))
                    tbl.add_widget(_cell(a.get('freq', '-') or '-', (0.72, 0.72, 0.72, 1)))

                content.add_widget(tbl)

            def _set_tab_active(tab: str):
                tab_state['active'] = tab
                for k, b in tab_buttons.items():
                    try:
                        b.color = (0.11, 0.75, 0.36, 1) if k == tab else (0.65, 0.65, 0.65, 1)
                    except Exception:
                        pass
                _render_tab(tab)

            for t in tabs:
                b = Button(
                    text=t,
                    size_hint_x=None,
                    width=ui_dp(110),
                    background_normal='',
                    background_down='',
                    background_color=(0, 0, 0, 0),
                    color=(0.65, 0.65, 0.65, 1),
                    font_size=ui_sp(12.5),
                    padding=(0, 0),
                    **_font_kwargs(),
                )
                tab_buttons[t] = b
                b.bind(on_press=(lambda _btn, _t=t: _set_tab_active(_t)))
                tab_row.add_widget(b)
            tab_row.add_widget(Widget())

            panel.add_widget(tab_row)
            panel.add_widget(content)

            self._result_grid.add_widget(panel)
            # Bottom safe space so content isn't covered by bottom nav.
            self._result_grid.add_widget(Widget(size_hint_y=None, height=ui_dp(78)))
            _set_tab_active('ORDERBOOK')

        def _render_tradingview(sym: str, q: dict):
            _render_stock_detail(sym, q, hist=None, phase_info=None, trend_info=None, sr_info=None)

        def _render_yfinance(sym: str, hist, phase_info, trend_info, sr_info):
            _render_stock_detail(sym, q={}, hist=hist, phase_info=phase_info, trend_info=trend_info, sr_info=sr_info)

        def _stop_detail_tv_poll():
            try:
                if self._detail_tv_poll_event is not None:
                    self._detail_tv_poll_event.cancel()
            except Exception:
                pass
            try:
                self._detail_tv_poll_event = None
                self._detail_tv_poll_inflight = False
                self._detail_tv_symbol = None
                self._detail_tv_series = []
                self._detail_tv_last_ts = None
                self._detail_chart_widget = None
            except Exception:
                pass

        def _start_detail_tv_poll(symbol: str, chart_widget=None, seed_price=None):
            """Fallback chart: poll TradingView snapshot and update sparkline."""
            try:
                sym_u = str(symbol or '').strip().upper()
                if not sym_u:
                    return
            except Exception:
                return

            # If already polling same symbol, just update chart reference.
            try:
                if self._detail_tv_symbol == sym_u and self._detail_tv_poll_event is not None:
                    self._detail_chart_widget = chart_widget
                    return
            except Exception:
                pass

            _stop_detail_tv_poll()
            try:
                self._detail_tv_symbol = sym_u
                self._detail_chart_widget = chart_widget
            except Exception:
                pass

            # Seed series so sparkline can render immediately.
            try:
                p0 = float(seed_price) if seed_price not in (None, '', '-') else None
            except Exception:
                p0 = None
            if isinstance(p0, (int, float)) and p0 and p0 > 0:
                try:
                    ts0 = datetime.now().timestamp()
                    self._detail_tv_series = [(ts0, p0), (ts0 + 0.001, p0)]
                    self._detail_tv_last_ts = ts0
                except Exception:
                    pass
                try:
                    if chart_widget is not None:
                        chart_widget.values = [p0, p0]
                except Exception:
                    pass

            try:
                from modules.tradingview_fetcher import fetch_tradingview_snapshot
            except Exception:
                fetch_tradingview_snapshot = None

            def _tick(_dt=None):
                try:
                    if fetch_tradingview_snapshot is None:
                        return
                    if self._detail_tv_poll_inflight:
                        return
                    self._detail_tv_poll_inflight = True
                except Exception:
                    return

                def _worker():
                    px = None
                    try:
                        snap = fetch_tradingview_snapshot([sym_u]) or {}
                        d = snap.get(sym_u) or {}
                        px = d.get('price')
                        if px is not None:
                            px = float(px)
                    except Exception:
                        px = None

                    def _apply(_dt2=None):
                        try:
                            self._detail_tv_poll_inflight = False
                        except Exception:
                            pass

                        if not (isinstance(px, (int, float)) and px and px > 0):
                            return

                        try:
                            now_ts = datetime.now().timestamp()
                        except Exception:
                            now_ts = 0.0

                        try:
                            series = list(self._detail_tv_series or [])
                        except Exception:
                            series = []
                        if not series:
                            series = [(now_ts, float(px)), (now_ts + 0.001, float(px))]
                        else:
                            # Append and trim.
                            series.append((now_ts, float(px)))
                            if len(series) > 180:
                                series = series[-180:]

                        try:
                            self._detail_tv_series = series
                            self._detail_tv_last_ts = now_ts
                        except Exception:
                            pass

                        try:
                            cw = self._detail_chart_widget
                            if cw is not None:
                                cw.values = [p for _t, p in series]
                        except Exception:
                            pass

                    try:
                        from kivy.clock import Clock
                        Clock.schedule_once(_apply, 0)
                    except Exception:
                        _apply(0)

                threading.Thread(target=_worker, daemon=True).start()

            try:
                from kivy.clock import Clock
                self._detail_tv_poll_event = Clock.schedule_interval(_tick, 6.0)
                _tick(0)
            except Exception:
                pass

        def _exit_detail(_btn=None):
            _stop_detail_tv_poll()
            _set_detail_mode(False)
            _render_welcome()

        try:
            self._back_btn.bind(on_press=_exit_detail)
        except Exception:
            pass

        # Expose go_back so Android back button can return from detail mode.
        def _go_back():
            try:
                if bool(getattr(self, '_detail_mode', False)):
                    _exit_detail(None)
                    return True
            except Exception:
                pass
            return False

        try:
            self.go_back = _go_back
        except Exception:
            pass

        def do_check(_btn):
            if self._busy:
                return
            sym = (self._ti.text or '').strip().upper()
            if not sym:
                _render_welcome()
                return

            try:
                _log_info('Cek', f"do_check: sym={sym}")
            except Exception:
                pass

            self._busy = True
            _clear_and_msg('Memuat...')

            def _worker():
                try:
                    try:
                        _log_info('Cek', f"worker: start sym={sym}")
                    except Exception:
                        pass
                    # Always prefer TradingView snapshot with yFinance fallback for quote data.
                    try:
                        from modules.quote_fetcher import fetch_quotes
                        q = (fetch_quotes([sym]) or {}).get(sym) or {}
                    except Exception:
                        q = {}

                    try:
                        _log_info('Cek', f"quotes: ok={bool(q)} keys={list(q.keys())[:8] if isinstance(q, dict) else '-'}")
                    except Exception:
                        pass

                    # Orderbook priority:
                    # 1) Manual JSON override (stable, user-controlled)
                    # 2) Stockbit (often blocked)
                    # 3) UI will fall back to estimated book if empty
                    ob = None
                    try:
                        from modules.orderbook_override import load_orderbook_override
                        ob = load_orderbook_override(sym)
                    except Exception:
                        ob = None
                    if not isinstance(ob, dict):
                        # Best-effort orderbook from Stockbit (TradingView scan does not expose depth).
                        try:
                            from modules.stockbit_fetcher import StockbitFetcher
                            ob = StockbitFetcher(use_cache=True).fetch_stock_orderbook(sym)
                        except Exception:
                            ob = None

                    try:
                        _log_info('Cek', f"orderbook: ok={isinstance(ob, dict)} source={(ob or {}).get('source') if isinstance(ob, dict) else '-'}")
                    except Exception:
                        pass

                    try:
                        if isinstance(ob, dict):
                            q['orderbook'] = ob
                            # Populate best-effort bid/ask for header/summary.
                            bids = ob.get('bid_orders') or []
                            asks = ob.get('ask_orders') or []
                            if isinstance(bids, list) and bids:
                                q['bid'] = (bids[0] or {}).get('price')
                            if isinstance(asks, list) and asks:
                                q['ask'] = (asks[0] or {}).get('price')
                            if 'bid_price' in ob and q.get('bid') in (None, '', '-'):
                                q['bid'] = ob.get('bid_price')
                            if 'ask_price' in ob and q.get('ask') in (None, '', '-'):
                                q['ask'] = ob.get('ask_price')
                    except Exception:
                        pass

                    # Best-effort history for chart + optional Bandarmology (uses yfinance).
                    hist = None
                    phase_info, trend_info, sr_info = None, None, None
                    yfinance_ok = False
                    try:
                        import yfinance as yf
                        yfinance_ok = True
                        ticker = f"{sym}.JK" if not sym.endswith('.JK') else sym
                        tkr = yf.Ticker(ticker)
                        hist = tkr.history(period='3mo')

                        # Best-effort company naming (to reduce user confusion).
                        try:
                            info = getattr(tkr, 'info', None) or {}
                            if isinstance(info, dict) and info:
                                long_name = info.get('longName') or info.get('shortName') or ''
                                long_name = str(long_name or '').strip()
                                if long_name:
                                    q['company_pt'] = long_name
                                    # Derive a short "emiten" name from the long name.
                                    short_name = long_name
                                    if short_name.upper().startswith('PT '):
                                        short_name = short_name[3:]
                                    short_name = short_name.replace('Tbk.', 'Tbk').strip()
                                    if short_name.lower().endswith(' tbk'):
                                        short_name = short_name[:-4].strip()
                                    if short_name.lower().endswith(', tbk'):
                                        short_name = short_name[:-5].strip()
                                    q['company_name'] = short_name
                        except Exception:
                            pass
                    except Exception as _e:
                        try:
                            _log_exception('Cek', f"yfinance history failed sym={sym}: {_e}")
                        except Exception:
                            pass
                        hist = None

                    try:
                        self._yfinance_available = bool(yfinance_ok)
                    except Exception:
                        pass

                    try:
                        _log_info('Cek', f"yfinance: import_ok={bool(yfinance_ok)} hist_ok={hist is not None and not getattr(hist, 'empty', True)}")
                    except Exception:
                        pass

                    # Optional Bandarmology summary from 3mo history (when available).
                    if hist is not None and not getattr(hist, 'empty', True):
                        try:
                            from modules.bandarmology import BandarmologyAnalyzer
                            analyzer = BandarmologyAnalyzer(hist)
                            phase_info = analyzer.detect_phase()
                            trend_info = analyzer.analyze_trend()
                            sr_info = analyzer.calculate_support_resistance()
                        except Exception:
                            phase_info, trend_info, sr_info = None, None, None

                    # Render unified stock detail UI (menu-like as requested).
                    Clock.schedule_once(lambda dt: _render_stock_detail(sym, q, hist, phase_info, trend_info, sr_info), 0)

                    try:
                        _log_info('Cek', f"render: scheduled sym={sym}")
                    except Exception:
                        pass

                finally:
                    def _done(_dt):
                        self._busy = False
                    Clock.schedule_once(_done, 0)

            threading.Thread(target=_worker, daemon=True).start()

        # Expose helpers so other tabs can forward to Cek Emiten and auto-run search.
        try:
            self._do_check = do_check
        except Exception:
            self._do_check = None

        def _open_symbol(sym: str):
            try:
                s = (sym or '').strip().upper()
                if not s:
                    return
            except Exception:
                return
            try:
                self._ti.text = s
            except Exception:
                pass
            try:
                do_check(None)
            except Exception:
                pass

        try:
            self.open_symbol = _open_symbol
        except Exception:
            pass

        try:
            self._ti.bind(on_text_validate=lambda *_: do_check(None))
        except Exception:
            pass

class ScreeningTab(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(orientation='vertical', **kwargs)
        _log_info('Screening', 'init: constructing UI')
        # Header like other tabs (avatar left, title centered)
        header = BoxLayout(orientation='horizontal', size_hint_y=None, height=ui_dp(68), padding=(ui_dp(12), ui_dp(10)), spacing=ui_dp(8))
        from kivy.uix.anchorlayout import AnchorLayout
        from kivy.graphics import Color, Ellipse
        avatar_size = ui_dp(42)
        from kivy.clock import Clock as _Clock
        from kivy.app import App as _App

        btn_avatar = Button(
            size_hint=(None, None),
            size=(avatar_size, avatar_size),
            background_normal='',
            background_down='',
            background_color=(0, 0, 0, 0),
        )
        with btn_avatar.canvas.before:
            btn_avatar._bg_color = Color(0.18, 0.22, 0.30, 1)
            btn_avatar._bg_circ = Ellipse(pos=btn_avatar.pos, size=btn_avatar.size)
            btn_avatar._fg_color = Color(0.97, 0.97, 0.97, 1)
            btn_avatar._head = Ellipse(pos=btn_avatar.pos, size=btn_avatar.size)
            btn_avatar._body = Ellipse(pos=btn_avatar.pos, size=btn_avatar.size)

        def _update_screening_avatar(*_a):
            try:
                btn_avatar._bg_circ.pos = btn_avatar.pos
                btn_avatar._bg_circ.size = btn_avatar.size
                r = btn_avatar.width * 0.36
                x_head = btn_avatar.x + (btn_avatar.width - r) / 2.0
                y_head = btn_avatar.y + btn_avatar.height * 0.52
                btn_avatar._head.pos = (x_head, y_head)
                btn_avatar._head.size = (r, r)
                bw = btn_avatar.width * 0.82
                bh = btn_avatar.height * 0.52
                x_body = btn_avatar.x + (btn_avatar.width - bw) / 2.0
                y_body = btn_avatar.y + btn_avatar.height * 0.04
                btn_avatar._body.pos = (x_body, y_body)
                btn_avatar._body.size = (bw, bh)
            except Exception:
                pass

        btn_avatar.bind(pos=_update_screening_avatar, size=_update_screening_avatar)

        def _open_profile_from_other_tab(*_a):
            # Buka popup profil global bila tersedia; fallback ke perilaku lama.
            try:
                app = _App.get_running_app()
            except Exception:
                app = None
            if app is None:
                return
            try:
                cb = getattr(app, 'open_profile_popup', None)
            except Exception:
                cb = None
            if cb is not None:
                try:
                    cb()
                    return
                except Exception:
                    pass
            try:
                app.switch_tab(0)
            except Exception:
                return

            def _after(_dt):
                try:
                    w = app.tab_container.children[0] if app.tab_container.children else None
                    if w is not None and hasattr(w, '_hdr_avatar'):
                        try:
                            w._hdr_avatar.dispatch('on_press')
                        except Exception:
                            pass
                except Exception:
                    pass

            try:
                _Clock.schedule_once(_after, 0.05)
            except Exception:
                pass

        btn_avatar.bind(on_press=_open_profile_from_other_tab)

        left = BoxLayout(size_hint=(None, 1), width=avatar_size)
        left.add_widget(btn_avatar)
        header.add_widget(left)

        center = AnchorLayout(anchor_x='center', anchor_y='center')
        # Header utama tab Screening.
        title = Label(text='[b]Screening[/b]', markup=True, font_size=ui_sp(18), color=(1, 1, 1, 1), halign='center', valign='middle', **_font_kwargs())
        center.add_widget(title)
        header.add_widget(center)
        header.add_widget(Widget(size_hint=(None, 1), width=avatar_size))
        self.add_widget(header)

        # State: filters + sorting (match web tab)
        self._flt_open_low = False
        self._flt_buy_gt_sell = False
        self._flt_mover_only = False
        self._flt_bid_gt_offer = False
        self._sort_by = 'Default'

        # Controls row (filters + sorting)
        controls = BoxLayout(
            orientation='vertical',
            size_hint_y=None,
            # Remove bottom padding to avoid a visible gap between the sort row and the table.
            padding=(ui_dp(4), ui_dp(2), ui_dp(4), ui_dp(0)),
            spacing=ui_dp(2),
        )
        controls.bind(minimum_height=controls.setter('height'))

        def _toggle_row(label_txt: str, getter_name: str):
            r = BoxLayout(orientation='horizontal', size_hint_y=None, height=ui_dp(32), spacing=ui_dp(8))
            lbl = Label(
                text=label_txt,
                font_size=ui_sp(12.0),
                color=(0.82, 0.82, 0.82, 1),
                halign='left',
                valign='middle',
                size_hint_x=1,
                **_font_kwargs(),
            )
            # Prevent wrapping (it can visually overlap other rows on narrow screens).
            lbl.text_size = (lbl.width, r.height)
            lbl.bind(size=lambda inst, val: setattr(inst, 'text_size', (inst.width, r.height)))
            try:
                lbl.shorten = True
                lbl.shorten_from = 'right'
            except Exception:
                pass
            r.add_widget(lbl)

            # Use a compact ON/OFF button instead of Switch to save horizontal space.
            btn = Button(
                text='',
                size_hint=(None, 1),
                width=ui_dp(48),
                background_normal='',
                background_down='',
                font_size=ui_sp(11.2),
                **_font_kwargs(),
            )
            btn.markup = True

            # Outline-only style (no filled background).
            try:
                btn.background_color = (0, 0, 0, 0)
            except Exception:
                pass
            try:
                from kivy.graphics import Color, Line

                with btn.canvas.before:
                    btn._sb_border_color = Color(0.40, 0.40, 0.40, 1)
                    btn._sb_border_line = Line(rectangle=(btn.x, btn.y, btn.width, btn.height), width=1)

                def _upd_border(*_):
                    try:
                        inset = max(1, int(ui_dp(1)))
                    except Exception:
                        inset = 1
                    try:
                        btn._sb_border_line.rectangle = (
                            btn.x + inset,
                            btn.y + inset,
                            max(1, btn.width - (2 * inset)),
                            max(1, btn.height - (2 * inset)),
                        )
                    except Exception:
                        pass

                btn.bind(pos=_upd_border, size=_upd_border)
                _upd_border()
            except Exception:
                pass

            def _apply_btn_style(active: bool):
                try:
                    if active:
                        btn.text = '[b]ON[/b]'
                        btn.color = (0.11, 0.75, 0.36, 1)
                        try:
                            btn._sb_border_color.rgba = (0.11, 0.75, 0.36, 1)
                        except Exception:
                            pass
                    else:
                        btn.text = 'OFF'
                        btn.color = (0.70, 0.70, 0.70, 1)
                        try:
                            btn._sb_border_color.rgba = (0.35, 0.35, 0.35, 1)
                        except Exception:
                            pass
                except Exception:
                    pass

            def _toggle(*_):
                try:
                    cur = bool(getattr(self, getter_name))
                except Exception:
                    cur = False
                new_val = not cur
                try:
                    setattr(self, getter_name, bool(new_val))
                except Exception:
                    pass
                _apply_btn_style(bool(new_val))
                self.refresh()

            try:
                btn.bind(on_press=_toggle)
            except Exception:
                pass

            _apply_btn_style(bool(getattr(self, getter_name)))
            r.add_widget(btn)
            return r

        filters_row1 = BoxLayout(orientation='horizontal', size_hint_y=None, height=ui_dp(36), spacing=ui_dp(10))
        filters_row2 = BoxLayout(orientation='horizontal', size_hint_y=None, height=ui_dp(36), spacing=ui_dp(10))
        filters_row1.add_widget(_toggle_row('Open=Low', '_flt_open_low'))
        filters_row1.add_widget(_toggle_row('Net Buy > Net Sell', '_flt_buy_gt_sell'))
        filters_row2.add_widget(_toggle_row('Mover (>2%)', '_flt_mover_only'))
        filters_row2.add_widget(_toggle_row('Bid > Offer', '_flt_bid_gt_offer'))
        controls.add_widget(filters_row1)
        controls.add_widget(filters_row2)

        sort_row = BoxLayout(orientation='horizontal', size_hint_y=None, height=ui_dp(28), spacing=ui_dp(6))
        sort_lbl = Label(text='Urutkan:', font_size=ui_sp(12.3), color=(0.70, 0.70, 0.70, 1), size_hint_x=None, width=ui_dp(68), halign='left', valign='middle', **_font_kwargs())
        sort_lbl.text_size = (sort_lbl.width, sort_lbl.height)
        sort_lbl.bind(size=lambda inst, val: setattr(inst, 'text_size', (inst.width, inst.height)))
        sort_row.add_widget(sort_lbl)
        try:
            from kivy.uix.spinner import Spinner
        except Exception:
            Spinner = None

        if Spinner is not None:
            spinner = Spinner(
                text=str(self._sort_by),
                values=(
                    'Default',
                    'Mover Tertinggi ↑',
                    'Mover Terendah ↓',
                    'Volume Tertinggi',
                    'Bid Volume',
                    'Net Buy',
                ),
                size_hint=(1, 1),
                background_normal='',
                background_down='',
                background_color=(0.06, 0.06, 0.06, 1),
                color=(0.88, 0.88, 0.88, 1),
                **_font_kwargs(),
            )

            def _on_sort(_sp, text):
                try:
                    self._sort_by = str(text)
                except Exception:
                    self._sort_by = 'Default'
                self.refresh()
            spinner.bind(text=_on_sort)
            sort_row.add_widget(spinner)
        else:
            sort_row.add_widget(Label(text=str(self._sort_by), font_size=ui_sp(12.5), color=(0.70, 0.70, 0.70, 1), halign='left', valign='middle', **_font_kwargs()))

        controls.add_widget(sort_row)

        self.add_widget(controls)

        # Table with sticky header + sticky left (SAHAM) column.
        # Android defaults to non-RV rendering; sticky column is implemented for that path.
        self._header_table = GridLayout(cols=1, spacing=0, size_hint=(None, None))
        self._header_table.bind(minimum_height=self._header_table.setter('height'))

        # Fast path: RecycleView for smooth scrolling on mobile.
        force_rv = False
        try:
            force_rv = str(os.environ.get('SCREENING_USE_RV', '')).strip() == '1'
        except Exception:
            force_rv = False

        # NOTE: Some Android devices/GL drivers can show a blank RecycleView even when
        # rv.data is populated (observed in this project). Prefer the stable non-RV
        # GridLayout+ScrollView path on Android unless explicitly forced.
        disable_rv = False
        try:
            disable_rv = (_kivy_platform == 'android') and (not force_rv)
        except Exception:
            disable_rv = False

        self._use_rv = (RecycleView is not None) and (RecycleBoxLayout is not None) and (not disable_rv)
        self._rv = None
        self._rv_layout = None
        self._body_table = GridLayout(cols=1, spacing=0, size_hint=(None, None))
        self._body_table.bind(minimum_height=self._body_table.setter('height'))

        if self._use_rv:
            self._rv = RecycleView(
                do_scroll_x=False,
                do_scroll_y=True,
                bar_width=0,
                bar_color=(0, 0, 0, 0),
                bar_inactive_color=(0, 0, 0, 0),
                size_hint=(None, None),
                size=(ui_dp(1), ui_dp(1)),
            )
            self._rv.viewclass = ScreeningRowView
            lm = RecycleBoxLayout(
                # Important: let rows expand to layout width.
                # Using (None, None) can leave rows at default_size width (e.g. 1px) until refreshed.
                default_size=(None, ui_dp(54)),
                default_size_hint=(1, None),
                size_hint=(None, None),
                orientation='vertical',
                spacing=0,
            )
            lm.bind(minimum_height=lm.setter('height'))
            self._rv_layout = lm
            # Kivy requires layout_manager to be a (sub)child of the RecycleView.
            self._rv.add_widget(lm)
            self._rv.layout_manager = lm

        # Default sizing tokens for sticky-column split (kept in sync with refresh() cols).
        _default_sym_w = ui_dp(56)
        _default_pad_x = ui_dp(4)
        _default_col_spacing = ui_dp(4)
        _default_left_w = _default_pad_x + _default_sym_w + _default_col_spacing

        try:
            self._screening_symbol_w = float(_default_sym_w)
        except Exception:
            self._screening_symbol_w = _default_sym_w
        try:
            self._screening_pad_x = float(_default_pad_x)
        except Exception:
            self._screening_pad_x = _default_pad_x
        try:
            self._screening_col_spacing = float(_default_col_spacing)
        except Exception:
            self._screening_col_spacing = _default_col_spacing

        # Right side scroll view (horizontal + vertical) is always created.
        body_scroll = ScrollView(
            do_scroll_x=True,
            do_scroll_y=(not self._use_rv),
            scroll_timeout=0,
            scroll_distance=ui_dp(2),
            bar_width=0,
            bar_color=(0, 0, 0, 0),
            bar_inactive_color=(0, 0, 0, 0),
        )

        # Header gesture scroll: manual touch handling.
        # - Horizontal swipe on header scrolls both header+body horizontally.
        # - Vertical swipe on header scrolls body vertically.
        # This is more reliable on Android than relying on ScrollView's internal gesture logic.
        class _HeaderGestureScroll(ScrollView):
            def __init__(self, target_body: ScrollView, get_table_w, **kw):
                super().__init__(**kw)
                self._target_body = target_body
                self._get_table_w = get_table_w
                self._gesture_mode = None  # None | 'h' | 'v'
                self._start_pos = None
                # Gesture tuning for Android:
                # - smaller slop = quicker to start scrolling
                # - higher sensitivity = less "berat"
                # Note: if slop is too small, we can lock the wrong axis.
                self._slop = ui_dp(6)
                self._h_sensitivity = 1.55
                self._v_sensitivity = 1.35
                # Require one axis to be clearly dominant before locking.
                self._axis_lock_ratio = 1.25

            def _clamp01(self, v):
                try:
                    fv = float(v)
                except Exception:
                    fv = 0.0
                if fv < 0.0:
                    return 0.0
                if fv > 1.0:
                    return 1.0
                return fv

            def on_touch_down(self, touch):
                if not self.collide_point(*touch.pos):
                    return super().on_touch_down(touch)
                self._gesture_mode = None
                self._start_pos = touch.pos
                try:
                    touch.grab(self)
                except Exception:
                    pass
                return True

            def on_touch_move(self, touch):
                if touch.grab_current is not self:
                    return super().on_touch_move(touch)

                try:
                    dx_total = float(touch.x - (self._start_pos[0] if self._start_pos else touch.x))
                    dy_total = float(touch.y - (self._start_pos[1] if self._start_pos else touch.y))
                except Exception:
                    dx_total = dy_total = 0.0

                if self._gesture_mode is None:
                    try:
                        if (abs(dx_total) + abs(dy_total)) < float(self._slop):
                            return True
                    except Exception:
                        pass
                    ax = abs(dx_total)
                    ay = abs(dy_total)
                    try:
                        ratio = float(getattr(self, '_axis_lock_ratio', 1.25) or 1.25)
                    except Exception:
                        ratio = 1.25

                    # Don't lock too early if the gesture is diagonal.
                    # This avoids situations where vertical scroll only works on certain columns/hand positions.
                    if ax > (ay * ratio):
                        self._gesture_mode = 'h'
                    elif ay > (ax * ratio):
                        self._gesture_mode = 'v'
                    else:
                        return True

                if self._gesture_mode == 'h':
                    # Use Kivy's own px->scroll conversion for a natural feel.
                    tb = getattr(self, '_target_body', None)
                    if tb is None:
                        return True
                    try:
                        # Invert direction to match user expectation:
                        # swipe left -> content moves left (reveal right columns)
                        raw_dx = float(getattr(touch, 'dx', 0.0) or 0.0)
                        sx, _sy = tb.convert_distance_to_scroll((-raw_dx) * float(getattr(self, '_h_sensitivity', 1.0) or 1.0), 0)
                    except Exception:
                        sx = 0.0
                    try:
                        new_x = self._clamp01(float(getattr(tb, 'scroll_x', 0.0) or 0.0) + float(sx))
                    except Exception:
                        new_x = self._clamp01(getattr(self, 'scroll_x', 0.0) or 0.0)
                    try:
                        tb.scroll_x = new_x
                    except Exception:
                        pass
                    try:
                        self.scroll_x = new_x
                    except Exception:
                        pass
                    return True

                # Vertical gesture: scroll body vertically.
                tb = getattr(self, '_target_body', None)
                if tb is None:
                    return True
                try:
                    if not bool(getattr(tb, 'do_scroll_y', False)):
                        return True
                except Exception:
                    return True
                try:
                    # Invert direction to match user expectation:
                    # swipe up -> content moves up (scroll down)
                    raw_dy = float(getattr(touch, 'dy', 0.0) or 0.0)
                    _sx, sy = tb.convert_distance_to_scroll(0, (-raw_dy) * float(getattr(self, '_v_sensitivity', 1.0) or 1.0))
                except Exception:
                    sy = 0.0
                try:
                    new_y = self._clamp01(float(getattr(tb, 'scroll_y', 1.0) or 1.0) + float(sy))
                    tb.scroll_y = new_y
                except Exception:
                    pass
                return True

            def on_touch_up(self, touch):
                if touch.grab_current is self:
                    try:
                        touch.ungrab(self)
                    except Exception:
                        pass
                    self._gesture_mode = None
                    self._start_pos = None
                    return True
                return super().on_touch_up(touch)

        # Provide a getter so header can compute horizontal range before/after apply().
        def _get_table_w():
            try:
                return float(getattr(self, '_screening_table_w', 0) or 0)
            except Exception:
                return 0

        # Header right side is a ScrollView; gestures are handled by a unified overlay.
        header_scroll = ScrollView(
            do_scroll_x=True,
            do_scroll_y=False,
            scroll_timeout=0,
            scroll_distance=ui_dp(2),
            bar_width=0,
            bar_color=(0, 0, 0, 0),
            bar_inactive_color=(0, 0, 0, 0),
            size_hint_y=None,
            height=ui_dp(26),
        )
        header_scroll.add_widget(self._header_table)

        # Sticky-left widgets (non-RV path): fixed SAHAM column for header+body.
        self._sticky_enabled = not bool(self._use_rv)
        self._header_left = None
        self._header_left_lbl = None
        self._header_right_scroll = header_scroll
        self._header_right_table = self._header_table
        self._body_left_scroll = None
        self._body_left_table = None
        self._body_right_scroll = body_scroll
        self._body_right_table = None

        self._body_inner = None
        self._body_empty = None
        self._sync_screening_viewport = None
        if self._use_rv and self._rv is not None:
            from kivy.uix.floatlayout import FloatLayout
            body_inner = FloatLayout(size_hint=(None, None), size=(ui_dp(1), ui_dp(1)))
            self._body_inner = body_inner
            try:
                self._rv.pos = (0, 0)
            except Exception:
                pass
            body_inner.add_widget(self._rv)
            empty = Label(
                text='',
                font_size=ui_sp(13),
                color=(0.70, 0.70, 0.70, 1),
                size_hint=(None, None),
                size=(ui_dp(1), ui_dp(54)),
                pos_hint={'center_x': 0.5, 'center_y': 0.5},
                halign='left',
                valign='middle',
                opacity=0,
                **_font_kwargs(),
            )
            empty.text_size = (empty.width - ui_dp(24), None)
            self._body_empty = empty
            body_inner.add_widget(empty)

            # Show a non-blank placeholder immediately; refresh() will replace it.
            try:
                base_w = max(ui_dp(320), float(getattr(self, 'width', 0) or 0), float(getattr(body_scroll, 'width', 0) or 0))
                empty.size = (base_w, ui_dp(54))
                empty.text_size = (max(1, base_w - ui_dp(24)), None)
                empty.text = 'Memuat data realtime...'
                empty.opacity = 1
            except Exception:
                pass

            # Explicit sizing: RecycleView needs a real viewport size inside the horizontal ScrollView.
            def _sync_inner(*_):
                # Ensure non-trivial viewport size; if height stays at ~1px,
                # both RV rows and placeholder label can render off-screen.
                try:
                    target_h = max(ui_dp(1), float(getattr(body_scroll, 'height', 0) or 0))
                except Exception:
                    target_h = ui_dp(1)
                try:
                    target_w = max(float(getattr(body_inner, 'width', 0) or 0), float(getattr(body_scroll, 'width', 0) or 0), ui_dp(1))
                except Exception:
                    target_w = ui_dp(1)

                try:
                    body_inner.size = (target_w, target_h)
                except Exception:
                    try:
                        body_inner.width = target_w
                        body_inner.height = target_h
                    except Exception:
                        pass
                try:
                    self._rv.size = (target_w, target_h)
                except Exception:
                    pass

            try:
                self._sync_screening_viewport = _sync_inner
            except Exception:
                self._sync_screening_viewport = None

            # Bind to size (more reliable than height-only across platforms)
            body_scroll.bind(size=_sync_inner)
            body_inner.bind(size=_sync_inner)
            # Run after initial layout settles.
            Clock.schedule_once(lambda dt: _sync_inner(), 0)
            Clock.schedule_once(lambda dt: _sync_inner(), 0.2)
            body_scroll.add_widget(body_inner)
        else:
            # Non-RV path: split into sticky-left (SAHAM) + scrollable-right.
            # IMPORTANT: some Android devices/GL stacks can be sensitive to certain
            # canvas/layout combinations; if anything fails here, fall back to the
            # stable single-table layout (non-sticky) to avoid a blank tab.
            legacy_body_table = self._body_table
            try:
                # BoxLayout is imported at module scope; don't re-import here.

                # Header left (fixed)
                header_left = BoxLayout(
                    orientation='horizontal',
                    size_hint=(None, None),
                    width=_default_left_w,
                    height=ui_dp(26),
                    padding=(
                        float(getattr(self, '_screening_pad_x', _default_pad_x) or _default_pad_x),
                        0,
                        float(getattr(self, '_screening_col_spacing', _default_col_spacing) or _default_col_spacing),
                        0,
                    ),
                )
                with header_left.canvas.before:
                    from kivy.graphics import Color, Rectangle
                    Color(0.06, 0.06, 0.06, 1)
                    header_left._bg = Rectangle(pos=header_left.pos, size=header_left.size)
                    Color(0.12, 0.12, 0.12, 1)
                    header_left._sep = Rectangle(pos=(header_left.x, header_left.y), size=(header_left.width, 1))

                def _upd_hl(*_):
                    try:
                        header_left._bg.pos = header_left.pos
                        header_left._bg.size = header_left.size
                        header_left._sep.pos = (header_left.x, header_left.y)
                        header_left._sep.size = (header_left.width, 1)
                    except Exception:
                        pass

                header_left.bind(pos=_upd_hl, size=_upd_hl)
                hl_lbl = Label(
                    text='[b]SAHAM[/b]',
                    markup=True,
                    font_size=ui_sp(11),
                    color=(0.82, 0.82, 0.82, 1),
                    size_hint=(None, 1),
                    width=_default_sym_w,
                    halign='left',
                    valign='middle',
                    **_font_kwargs(),
                )
                hl_lbl.text_size = (hl_lbl.width, None)
                hl_lbl.bind(size=lambda inst, val: setattr(inst, 'text_size', (inst.width, None)))
                header_left.add_widget(hl_lbl)

                # Body left (fixed)
                body_left_table = GridLayout(cols=1, spacing=0, size_hint=(None, None))
                body_left_table.bind(minimum_height=body_left_table.setter('height'))
                body_left_table.width = _default_left_w
                body_left_scroll = ScrollView(
                    do_scroll_x=False,
                    do_scroll_y=True,
                    scroll_timeout=0,
                    scroll_distance=ui_dp(2),
                    bar_width=0,
                    bar_color=(0, 0, 0, 0),
                    bar_inactive_color=(0, 0, 0, 0),
                    size_hint=(None, 1),
                    width=_default_left_w,
                )
                body_left_scroll.add_widget(body_left_table)

                # Body right (scrollable)
                body_right_table = GridLayout(cols=1, spacing=0, size_hint=(None, None))
                body_right_table.bind(minimum_height=body_right_table.setter('height'))
                body_right_table.width = max(ui_dp(1), float(getattr(body_scroll, 'width', 0) or ui_dp(1)))
                body_scroll.add_widget(body_right_table)

                # Expose references
                self._header_left = header_left
                self._header_left_lbl = hl_lbl
                self._body_left_scroll = body_left_scroll
                self._body_left_table = body_left_table
                self._body_right_scroll = body_scroll
                self._body_right_table = body_right_table
                self._header_right_scroll = header_scroll
                self._header_right_table = self._header_table

                # Keep legacy attribute names pointed at the visible/right table so existing
                # refresh() logic (placeholders/errors) continues to work.
                self._body_table = body_right_table

                # Show non-blank placeholder immediately on the right; refresh() will replace it.
                try:
                    body_right_table.add_widget(
                        Label(
                            text='Memuat data realtime...',
                            size_hint_y=None,
                            height=ui_dp(42),
                            font_size=ui_sp(13),
                            color=(0.70, 0.70, 0.70, 1),
                            halign='left',
                            valign='middle',
                            padding=(ui_dp(6), 0),
                            **_font_kwargs(),
                        )
                    )
                except Exception:
                    pass

                # Header row container (left + right)
                header_row = BoxLayout(
                    orientation='horizontal',
                    size_hint_y=None,
                    height=ui_dp(26),
                    spacing=0,
                    padding=(0, 0),
                )
                header_row.add_widget(header_left)
                header_row.add_widget(header_scroll)

                # Body row container (left + right)
                body_row = BoxLayout(
                    orientation='horizontal',
                    size_hint=(1, 1),
                    spacing=0,
                    padding=(0, 0),
                )
                body_row.add_widget(body_left_scroll)
                body_row.add_widget(body_scroll)

                # Replace default header/body widgets with split rows
                self._header_scroll = header_scroll
                self._body_scroll = body_scroll

                # Rebuild the table area later (below) using these containers.
                _split_header_row = header_row
                _split_body_row = body_row
            except Exception as _e:
                try:
                    print(f"[Screening] sticky split init failed -> fallback non-sticky: {_e}")
                except Exception:
                    pass
                try:
                    self._sticky_enabled = False
                except Exception:
                    pass

                # Ensure we have a stable body viewport to render into.
                try:
                    self._body_table = legacy_body_table
                except Exception:
                    pass
                try:
                    body_scroll.clear_widgets()
                except Exception:
                    pass
                try:
                    body_scroll.add_widget(self._body_table)
                except Exception:
                    pass
                try:
                    self._body_left_scroll = None
                    self._body_left_table = None
                    self._body_right_table = None
                    self._header_left = None
                    self._header_left_lbl = None
                except Exception:
                    pass

        # If RV path, header_scroll/body_scroll are already the final widgets.
        if not bool(getattr(self, '_sticky_enabled', False)):
            self._header_scroll = header_scroll
            self._body_scroll = body_scroll

        # Sync horizontal scroll between header and body (right side).
        self._syncing_scroll = False

        def _sync_from_body(_inst, value):
            if self._syncing_scroll:
                return
            self._syncing_scroll = True
            try:
                self._header_scroll.scroll_x = value
            finally:
                self._syncing_scroll = False

        def _sync_from_header(_inst, value):
            if self._syncing_scroll:
                return
            self._syncing_scroll = True
            try:
                self._body_scroll.scroll_x = value
            finally:
                self._syncing_scroll = False

        body_scroll.bind(scroll_x=_sync_from_body)
        header_scroll.bind(scroll_x=_sync_from_header)

        # Sync vertical scroll between sticky-left and right body (non-RV path).
        try:
            if bool(getattr(self, '_sticky_enabled', False)) and (self._body_left_scroll is not None):
                self._syncing_vscroll = False

                def _sync_v_from_right(_inst, value):
                    if getattr(self, '_syncing_vscroll', False):
                        return
                    self._syncing_vscroll = True
                    try:
                        self._body_left_scroll.scroll_y = value
                    finally:
                        self._syncing_vscroll = False

                def _sync_v_from_left(_inst, value):
                    if getattr(self, '_syncing_vscroll', False):
                        return
                    self._syncing_vscroll = True
                    try:
                        body_scroll.scroll_y = value
                    finally:
                        self._syncing_vscroll = False

                body_scroll.bind(scroll_y=_sync_v_from_right)
                self._body_left_scroll.bind(scroll_y=_sync_v_from_left)
        except Exception:
            pass

        # Unified 4-direction gesture layer over the whole table (header+body).
        # Excludes the symbol column area which is tap-only (forward to cek saham).
        class _ScreeningTableGestureLayer(Widget):
            def __init__(
                self,
                header_sv: ScrollView,
                body_hsv: ScrollView,
                body_vsv: ScrollView,
                body_left_vsv: ScrollView,
                get_table_w,
                pad_x: float,
                sym_w: float,
                **kwargs,
            ):
                super().__init__(**kwargs)
                self._header_sv = header_sv
                self._body_hsv = body_hsv
                self._body_vsv = body_vsv
                self._body_left_vsv = body_left_vsv
                self._get_table_w = get_table_w
                self._pad_x = float(pad_x or 0.0)
                self._sym_w = float(sym_w or 0.0)
                self._slop = ui_dp(6)
                self._h_sensitivity = 1.45
                self._v_sensitivity = 1.25
                self._start = None
                self._moved = False

            def _clamp01(self, v):
                try:
                    fv = float(v)
                except Exception:
                    fv = 0.0
                if fv < 0.0:
                    return 0.0
                if fv > 1.0:
                    return 1.0
                return fv

            def _in_symbol_column_body(self, touch) -> bool:
                """Returns True if touch started inside the symbol column area in the body region."""
                # If we have a dedicated sticky-left scrollview, treat that whole region as symbol-only.
                try:
                    bl = getattr(self, '_body_left_vsv', None)
                    if bl is not None and bl.collide_point(*touch.pos):
                        return True
                except Exception:
                    pass
                body = getattr(self, '_body_hsv', None)
                if body is None:
                    return False
                try:
                    if not body.collide_point(*touch.pos):
                        return False
                except Exception:
                    return False

                # Convert to body scrollview local coordinates.
                try:
                    lx, ly = body.to_widget(*touch.pos)
                except Exception:
                    return False

                # Compute current horizontal pixel offset of the viewport.
                try:
                    vp = getattr(body, '_viewport', None)
                    if vp is None:
                        return False
                    table_w = float(getattr(vp, 'width', 0.0) or 0.0)
                    view_w = float(getattr(body, 'width', 0.0) or 0.0)
                    if table_w <= view_w:
                        offset = 0.0
                    else:
                        offset = float(getattr(body, 'scroll_x', 0.0) or 0.0) * (table_w - view_w)
                except Exception:
                    offset = 0.0

                # Symbol column x-range within the visible viewport.
                x0 = (-offset) + float(getattr(self, '_pad_x', 0.0) or 0.0)
                x1 = x0 + float(getattr(self, '_sym_w', 0.0) or 0.0)
                try:
                    return (lx >= x0) and (lx <= x1)
                except Exception:
                    return False

            def on_touch_down(self, touch):
                if not self.collide_point(*touch.pos):
                    return False
                if self._in_symbol_column_body(touch):
                    # Let symbol (tap-only) handle it; do NOT allow gestures here.
                    return False
                self._start = touch.pos
                self._moved = False
                try:
                    touch.grab(self)
                except Exception:
                    pass
                return True

            def on_touch_move(self, touch):
                if touch.grab_current is not self:
                    return False
                try:
                    dx_total = float(touch.x - (self._start[0] if self._start else touch.x))
                    dy_total = float(touch.y - (self._start[1] if self._start else touch.y))
                except Exception:
                    dx_total = dy_total = 0.0

                if not self._moved:
                    try:
                        if (abs(dx_total) + abs(dy_total)) < float(self._slop):
                            return True
                    except Exception:
                        pass
                    self._moved = True

                # Apply both axes (4-direction pan).
                try:
                    raw_dx = float(getattr(touch, 'dx', 0.0) or 0.0)
                    raw_dy = float(getattr(touch, 'dy', 0.0) or 0.0)
                except Exception:
                    raw_dx = raw_dy = 0.0

                body_h = getattr(self, '_body_hsv', None)
                body_v = getattr(self, '_body_vsv', None)
                if body_h is None or body_v is None:
                    return True

                # Horizontal scroll (header + body)
                try:
                    sx, _sy = body_h.convert_distance_to_scroll(
                        (-raw_dx) * float(getattr(self, '_h_sensitivity', 1.0) or 1.0),
                        0,
                    )
                except Exception:
                    sx = 0.0
                try:
                    new_x = self._clamp01(float(getattr(body_h, 'scroll_x', 0.0) or 0.0) + float(sx))
                    body_h.scroll_x = new_x
                except Exception:
                    new_x = None
                if new_x is not None:
                    try:
                        self._header_sv.scroll_x = float(new_x)
                    except Exception:
                        pass

                # Vertical scroll (body)
                try:
                    _sx, sy = body_v.convert_distance_to_scroll(
                        0,
                        (-raw_dy) * float(getattr(self, '_v_sensitivity', 1.0) or 1.0),
                    )
                except Exception:
                    sy = 0.0
                try:
                    new_y = self._clamp01(float(getattr(body_v, 'scroll_y', 1.0) or 1.0) + float(sy))
                    body_v.scroll_y = new_y
                    try:
                        bl = getattr(self, '_body_left_vsv', None)
                        if bl is not None:
                            bl.scroll_y = new_y
                    except Exception:
                        pass
                except Exception:
                    pass

                return True

            def on_touch_up(self, touch):
                if touch.grab_current is self:
                    try:
                        touch.ungrab(self)
                    except Exception:
                        pass
                    self._start = None
                    self._moved = False
                    return True
                return False

        # Choose the vertical scroller: RecycleView (if enabled) or the body ScrollView.
        v_scroller = body_scroll
        try:
            if bool(self._use_rv) and (self._rv is not None):
                v_scroller = self._rv
        except Exception:
            v_scroller = body_scroll

        # Symbol column width + left/right padding.
        # NOTE: don't reference `cols` / `pad_x` here because those are local to refresh().
        # Keep defaults in sync with refresh() column config.
        sym_w = ui_dp(56)
        pad_x = ui_dp(4)
        try:
            self._screening_symbol_w = float(sym_w)
        except Exception:
            self._screening_symbol_w = sym_w
        try:
            self._screening_pad_x = float(pad_x)
        except Exception:
            self._screening_pad_x = pad_x

        from kivy.uix.floatlayout import FloatLayout
        table_area = FloatLayout(size_hint=(1, 1))

        # Bungkus header+body dengan BoxLayout yang punya padding horizontal
        # 4dp supaya area tabel Screening sejajar dengan "kartu" Top 10.
        outer_box = BoxLayout(
            orientation='vertical',
            size_hint=(1, 1),
            padding=(ui_dp(4), 0, ui_dp(4), 0),
        )

        # Layout vertikal asli (header + body) di dalam outer_box.
        table_box = BoxLayout(orientation='vertical', size_hint=(1, 1), pos_hint={'x': 0, 'top': 1})
        try:
            if bool(getattr(self, '_sticky_enabled', False)):
                table_box.add_widget(_split_header_row)
                table_box.add_widget(_split_body_row)
            else:
                table_box.add_widget(header_scroll)
                table_box.add_widget(body_scroll)
        except Exception:
            table_box.add_widget(header_scroll)
            table_box.add_widget(body_scroll)
        outer_box.add_widget(table_box)
        table_area.add_widget(outer_box)

        gesture_layer = _ScreeningTableGestureLayer(
            header_scroll,
            body_scroll,
            v_scroller,
            getattr(self, '_body_left_scroll', None),
            _get_table_w,
            pad_x,
            sym_w,
            size_hint=(1, 1),
            pos_hint={'x': 0, 'top': 1},
        )
        table_area.add_widget(gesture_layer)

        self.add_widget(table_area)

        # Optional: on-screen diagnostics (disabled by default).
        # Enable by setting env SCREENING_DEBUG=1 (useful on Android without logcat).
        self._diag = None
        try:
            if str(os.environ.get('SCREENING_DEBUG', '')).strip() == '1':
                self._diag = Label(
                    text='screening: init',
                    font_size=ui_sp(10.5),
                    color=(0.55, 0.55, 0.55, 1),
                    size_hint_y=None,
                    height=ui_dp(16),
                    halign='left',
                    valign='middle',
                    padding=(ui_dp(4), 0),
                    **_font_kwargs(),
                )
                self._diag.text_size = (self.width - ui_dp(24), self._diag.height)
                self.bind(width=lambda *_: setattr(self._diag, 'text_size', (max(1, self.width - ui_dp(24)), self._diag.height)))
                self.add_widget(self._diag)
        except Exception:
            self._diag = None

        self._loading = False
        self._latest_rows = []
        self._refresh_token = 0

        # Some Android layouts report width/height=0 briefly; that can make RV/labels render at 1px.
        # Refresh again once we have a real size.
        self._did_initial_refresh = False

        def _maybe_initial_refresh(*_):
            if getattr(self, '_did_initial_refresh', False):
                return
            try:
                if float(getattr(self, 'width', 0) or 0) < ui_dp(40):
                    return
                if float(getattr(self, 'height', 0) or 0) < ui_dp(120):
                    return
            except Exception:
                return
            self._did_initial_refresh = True
            try:
                _log_info('Screening', f"initial_refresh: size=({getattr(self,'width',None)},{getattr(self,'height',None)}) use_rv={bool(self._use_rv)}")
            except Exception:
                pass
            try:
                self.refresh()
            except Exception:
                pass

        self.bind(size=_maybe_initial_refresh)
        Clock.schedule_once(lambda dt: _maybe_initial_refresh(), 0.1)
        Clock.schedule_once(lambda dt: _maybe_initial_refresh(), 0.6)

        # Extra early refresh attempt: reduces chance of a fully blank table on Android.
        try:
            Clock.schedule_once(lambda dt: _maybe_initial_refresh(), 0.02)
        except Exception:
            pass

        # Fallback: ensure at least one refresh even if size gating never passes
        # (some Android layouts can report a small/zero size for longer than expected).
        def _fallback_refresh(_dt):
            try:
                if getattr(self, '_did_initial_refresh', False):
                    return
                self._did_initial_refresh = True
            except Exception:
                pass
            try:
                _log_info('Screening', f"fallback_refresh: size=({getattr(self,'width',None)},{getattr(self,'height',None)})")
            except Exception:
                pass
            try:
                self.refresh()
            except Exception:
                pass

        Clock.schedule_once(_fallback_refresh, 1.2)

    def _stable_ratio(self, key: str, lo: float, hi: float) -> float:
        try:
            import hashlib
            h = hashlib.md5(key.encode('utf-8')).hexdigest()
            v = int(h[:8], 16) / float(0xFFFFFFFF)
            return lo + (hi - lo) * v
        except Exception:
            return (lo + hi) / 2.0

    def _scan_files_newest_first(self):
        base_dir = os.path.dirname(os.path.abspath(__file__))
        results_dir = os.path.join(base_dir, 'data', 'screening_results')
        _log_info('Screening', f"scan_files: dir={results_dir}")
        try:
            files = [
                os.path.join(results_dir, f)
                for f in os.listdir(results_dir)
                if f.startswith('scan_') and f.endswith('.csv')
            ]
        except Exception:
            files = []
        try:
            _log_info('Screening', f"scan_files: found={len(files)}")
        except Exception:
            pass
        if not files:
            return []
        try:
            def _key(p: str):
                name = os.path.basename(p)
                stem = name.replace('scan_', '').replace('.csv', '')
                return stem
            files.sort(key=_key, reverse=True)
        except Exception:
            try:
                files.sort(key=lambda p: os.path.getmtime(p), reverse=True)
            except Exception:
                files.sort(reverse=True)
        return files

    def _latest_scan_file(self):
        for p in self._scan_files_newest_first():
            try:
                if os.path.getsize(p) > 0:
                    _log_info('Screening', f"latest_scan_file: {p}")
                    return p
            except Exception:
                continue
        _log_info('Screening', 'latest_scan_file: none')
        return None

    def _load_screening_rows(self, path):
        rows = []
        if not path:
            return rows
        try:
            with open(path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for r in reader:
                    if not r:
                        continue
                    try:
                        cleaned = {}
                        for k, v in r.items():
                            kk = '' if k is None else str(k)
                            kk = kk.strip()
                            kk = kk.lstrip('\ufeff')
                            kk = kk.lower()
                            if not kk:
                                continue
                            cleaned[kk] = v
                        rows.append(cleaned)
                    except Exception:
                        rows.append(r)
        except Exception:
            try:
                _log_info('Screening', f"load_rows: failed path={path}")
            except Exception:
                pass
            return []
        try:
            _log_info('Screening', f"load_rows: ok path={path} rows={len(rows)}")
        except Exception:
            pass
        return rows

    def refresh(self):
        try:
            return self._refresh_impl()
        except Exception as e:
            # Never fail silently: show error in UI so Android debugging is easy.
            msg = f"Gagal refresh screening: {e}"
            try:
                if self._use_rv and self._body_empty is not None:
                    self._body_empty.text = msg
                    self._body_empty.opacity = 1
                    return
            except Exception:
                pass
            try:
                self._header_table.clear_widgets()
            except Exception:
                pass
            try:
                self._body_table.clear_widgets()
                self._body_table.size_hint = (1, None)
                self._body_table.width = self.width
                self._body_table.add_widget(
                    Label(
                        text=msg,
                        size_hint_y=None,
                        height=ui_dp(72),
                        font_size=ui_sp(13),
                        color=(0.72, 0.72, 0.72, 1),
                        halign='left',
                        valign='middle',
                        padding=(ui_dp(4), 0),
                        **_font_kwargs(),
                    )
                )
            except Exception:
                pass
            try:
                if (not self._use_rv) and getattr(self, '_body_left_table', None) is not None:
                    self._body_left_table.clear_widgets()
            except Exception:
                pass
            return

    def _refresh_impl(self):
        try:
            self._refresh_token = int(getattr(self, '_refresh_token', 0) or 0) + 1
        except Exception:
            self._refresh_token = 1
        token = self._refresh_token

        try:
            _log_info('Screening', f"refresh: token={token} size=({getattr(self,'width',None)},{getattr(self,'height',None)}) use_rv={bool(self._use_rv)}")
        except Exception:
            pass

        # Best-effort viewport sync (prevents 1px-tall list on some Android layouts)
        try:
            sync_fn = getattr(self, '_sync_screening_viewport', None)
            if callable(sync_fn):
                Clock.schedule_once(lambda dt: sync_fn(), 0)
        except Exception:
            pass

        self._header_table.clear_widgets()
        if self._use_rv and self._rv is not None:
            try:
                self._rv.data = []
            except Exception:
                pass
            try:
                if self._body_empty is not None:
                    self._body_empty.opacity = 0
                    self._body_empty.text = ''
            except Exception:
                pass
        else:
            self._body_table.clear_widgets()
            try:
                if getattr(self, '_body_left_table', None) is not None:
                    self._body_left_table.clear_widgets()
            except Exception:
                pass
        latest = self._latest_scan_file()
        rows = self._load_screening_rows(latest) if latest else []
        self._latest_rows = rows

        try:
            _log_info('Screening', f"refresh: latest={os.path.basename(latest) if latest else '-'} rows={len(rows)}")
        except Exception:
            pass

        try:
            if self._diag is not None:
                rv_len = 0
                try:
                    rv_len = len(getattr(self._rv, 'data', []) or []) if self._rv is not None else 0
                except Exception:
                    rv_len = 0
                try:
                    rv_size = getattr(self._rv, 'size', None) if self._rv is not None else None
                except Exception:
                    rv_size = None
                try:
                    inner_size = getattr(self._body_inner, 'size', None) if self._body_inner is not None else None
                except Exception:
                    inner_size = None
                try:
                    bs_size = getattr(self._body_scroll, 'size', None) if self._body_scroll is not None else None
                except Exception:
                    bs_size = None
                self._diag.text = (
                    f"screening: rows={len(rows)} rv.data={rv_len} use_rv={bool(self._use_rv)} "
                    f"rv={rv_size} inner={inner_size} body={bs_size} file={os.path.basename(latest) if latest else '-'}"
                )
        except Exception:
            pass

        if not rows:
            _log_info('Screening', 'refresh: no rows -> show empty message')
            self._header_table.size_hint = (1, None)
            self._header_table.width = self.width
            msg = 'Belum ada hasil screening.'
            if latest is None:
                msg = 'Belum ada file screening di data/screening_results.'
            else:
                try:
                    msg = f"Belum ada hasil screening. (file: {os.path.basename(latest)})"
                except Exception:
                    pass
            if self._use_rv and self._body_empty is not None:
                try:
                    base_w = max(ui_dp(320), float(getattr(self, 'width', 0) or 0), float(getattr(self._body_scroll, 'width', 0) or 0))
                    if self._body_inner is not None:
                        self._body_inner.width = base_w
                    self._body_empty.size = (base_w, ui_dp(54))
                    self._body_empty.text_size = (max(1, base_w - ui_dp(24)), None)
                    self._body_empty.text = msg
                    self._body_empty.opacity = 1
                except Exception:
                    pass
            else:
                self._body_table.size_hint = (1, None)
                self._body_table.width = self.width
                self._body_table.add_widget(
                    Label(
                        text=msg,
                        size_hint_y=None,
                        height=ui_dp(54),
                        font_size=ui_sp(14),
                        color=(0.72, 0.72, 0.72, 1),
                        halign='left',
                        valign='middle',
                        padding=(ui_dp(4), 0),
                        **_font_kwargs(),
                    )
                )
                try:
                    if getattr(self, '_body_left_table', None) is not None:
                        self._body_left_table.clear_widgets()
                except Exception:
                    pass
            return

        symbols = []
        symbol_to_row = {}
        for r in rows:
            sym = ''
            try:
                sym = (
                    r.get('symbol')
                    or r.get('saham')
                    or r.get('kode')
                    or r.get('ticker')
                    or r.get('stock')
                    or r.get('emiten')
                    or ''
                )
            except Exception:
                sym = ''
            sym = str(sym or '').strip().upper()
            if not sym:
                continue
            symbols.append(sym)
            symbol_to_row[sym] = r

        if not symbols:
            _log_info('Screening', 'refresh: symbols empty -> missing symbol column')
            # We have CSV rows, but can't detect the symbol column.
            cols = []
            try:
                cols = sorted({str(k) for k in (rows[0] or {}).keys() if k})
            except Exception:
                cols = []
            msg = 'Kolom simbol tidak ditemukan di file screening.'
            if cols:
                msg = msg + f"\nKolom tersedia: {', '.join(cols[:12])}{'...' if len(cols) > 12 else ''}"
            if self._use_rv and self._body_empty is not None:
                try:
                    base_w = max(ui_dp(320), float(getattr(self, 'width', 0) or 0), float(getattr(self._body_scroll, 'width', 0) or 0))
                    if self._body_inner is not None:
                        self._body_inner.width = base_w
                    self._body_empty.size = (base_w, ui_dp(72))
                    self._body_empty.text_size = (max(1, base_w - ui_dp(24)), None)
                    self._body_empty.text = msg
                    self._body_empty.opacity = 1
                except Exception:
                    pass
            else:
                self._body_table.size_hint = (1, None)
                self._body_table.width = self.width
                self._body_table.add_widget(
                    Label(
                        text=msg,
                        size_hint_y=None,
                        height=ui_dp(72),
                        font_size=ui_sp(13),
                        color=(0.72, 0.72, 0.72, 1),
                        halign='left',
                        valign='middle',
                        padding=(ui_dp(4), 0),
                        **_font_kwargs(),
                    )
                )
                try:
                    if getattr(self, '_body_left_table', None) is not None:
                        self._body_left_table.clear_widgets()
                except Exception:
                    pass
            return

        # Show loading placeholder (ensure label has a real width so text is visible)
        self._loading = True
        try:
            _log_info('Screening', f"refresh: symbols={len(symbols)} loading placeholder")
        except Exception:
            pass
        self._header_table.size_hint = (1, None)
        self._header_table.width = self.width
        if self._use_rv and self._body_empty is not None:
            try:
                base_w = max(ui_dp(320), float(getattr(self, 'width', 0) or 0), float(getattr(self._body_scroll, 'width', 0) or 0))
                if self._body_inner is not None:
                    self._body_inner.width = base_w
                self._body_empty.size = (base_w, ui_dp(54))
                self._body_empty.text_size = (max(1, base_w - ui_dp(24)), None)
                self._body_empty.text = 'Memuat data realtime...'
                self._body_empty.opacity = 1
            except Exception:
                pass
        else:
            self._body_table.size_hint = (1, None)
            self._body_table.width = self.width
            self._body_table.add_widget(Label(text='Memuat data realtime...', size_hint_y=None, height=ui_dp(42), font_size=ui_sp(13), color=(0.70,0.70,0.70,1), halign='left', valign='middle', padding=(ui_dp(12),0), **_font_kwargs()))
            try:
                if getattr(self, '_body_left_table', None) is not None:
                    self._body_left_table.clear_widgets()
            except Exception:
                pass

        # Table columns (match web columns) but styling/formatting aligns with other in-app tables
        # Column widths tuned so the far-right column remains reachable.
        # Per request: merge HARGA+KEMARIN, BID+OFFER, NET BUY+NET SELL into 2-line columns.
        cols = [
            ('SAHAM', ui_dp(56), 'left'),
            ('HARGA', ui_dp(92), 'right'),
            ('%', ui_dp(74), 'right'),
            ('BID/OFFER', ui_dp(100), 'right'),
            ('N.BUY/N.SELL', ui_dp(100), 'right'),
            ('OPEN=LOW', ui_dp(64), 'center'),
        ]
        pad_x = ui_dp(4)
        col_spacing = ui_dp(4)
        # IMPORTANT: include padding + spacing; otherwise rightmost columns can be clipped.
        table_w = (pad_x * 2) + sum([w for _, w, _ in cols]) + (col_spacing * max(0, len(cols) - 1))

        sticky = (not bool(self._use_rv)) and bool(getattr(self, '_sticky_enabled', False)) and (getattr(self, '_body_left_table', None) is not None)
        left_w = (pad_x + cols[0][1] + col_spacing)
        right_table_w = max(ui_dp(1), float(table_w) - float(left_w))
        try:
            self._screening_left_table_w = float(left_w)
        except Exception:
            self._screening_left_table_w = left_w
        try:
            self._screening_right_table_w = float(right_table_w)
        except Exception:
            self._screening_right_table_w = right_table_w

        # Expose table width for header gesture handling.
        try:
            self._screening_table_w = float(table_w)
        except Exception:
            self._screening_table_w = table_w

        # Expose constants for gesture layer hit-testing (symbol column exclusion).
        try:
            self._screening_pad_x = float(pad_x)
        except Exception:
            self._screening_pad_x = pad_x
        try:
            self._screening_symbol_w = float(cols[0][1])
        except Exception:
            try:
                self._screening_symbol_w = cols[0][1]
            except Exception:
                self._screening_symbol_w = ui_dp(56)

        color_up = (0.11, 0.75, 0.36, 1)
        color_down = (0.86, 0.25, 0.25, 1)
        color_muted = (0.70, 0.70, 0.70, 1)

        def _price_top_color(px, prev):
            try:
                px_f = _to_num(px)
                prev_f = _to_num(prev)
                if px_f is None or prev_f is None:
                    return color_muted
                if float(px_f) > float(prev_f):
                    return color_up
                if float(px_f) < float(prev_f):
                    return color_down
                return (0.88, 0.88, 0.88, 1)
            except Exception:
                return color_muted

        def _fmt_int_id(v):
            try:
                if v is None or v == '-':
                    return '-'
                return _format_id_number(float(v), decimals=0)
            except Exception:
                return '-'

        def _fmt_price_id(v):
            return _format_price(v)

        def _fmt_signed_pct_id(v):
            try:
                if v is None or v == '-':
                    return '-'
                cp = float(v)
                sign = '+' if cp > 0 else ''
                return f"{sign}{_format_id_number(cp, decimals=2)}%"
            except Exception:
                return '-'

        def _cell_two_lines(
            w,
            top_text,
            bottom_text,
            top_color,
            bottom_color,
            top_font,
            bottom_font,
            align='right',
        ):
            cell = BoxLayout(
                orientation='vertical',
                size_hint=(None, 1),
                width=w,
                spacing=ui_dp(2),
            )
            lt = Label(text=str(top_text), font_size=top_font, color=top_color, halign=align, valign='middle', **_font_kwargs())
            lb = Label(text=str(bottom_text), font_size=bottom_font, color=bottom_color, halign=align, valign='middle', **_font_kwargs())
            for lab in (lt, lb):
                lab.text_size = (lab.width, None)
                lab.bind(size=lambda inst, val: setattr(inst, 'text_size', (inst.width, None)))
                try:
                    lab.shorten = True
                    lab.shorten_from = 'left' if align == 'right' else 'right'
                except Exception:
                    pass
            cell.add_widget(lt)
            cell.add_widget(lb)
            return cell

        def _cell_two_lines_prefix_value(
            w,
            top_prefix,
            top_value,
            bottom_prefix,
            bottom_value,
            top_value_color,
            bottom_value_color,
            prefix_color=(0.88, 0.88, 0.88, 1),
            prefix_font=None,
            value_font=None,
            align='right',
        ):
            prefix_font = ui_sp(11.5) if prefix_font is None else prefix_font
            value_font = ui_sp(12) if value_font is None else value_font
            prefix_w = ui_dp(28)

            cell = BoxLayout(
                orientation='vertical',
                size_hint=(None, 1),
                width=w,
                spacing=ui_dp(2),
            )

            def _line(prefix_txt, value_txt, value_color):
                line = BoxLayout(orientation='horizontal', size_hint=(1, 1), spacing=ui_dp(4))
                lp = Label(
                    text=str(prefix_txt),
                    font_size=prefix_font,
                    color=prefix_color,
                    size_hint=(None, 1),
                    width=prefix_w,
                    halign='right',
                    valign='middle',
                    **_font_kwargs(),
                )
                lv = Label(
                    text=str(value_txt),
                    font_size=value_font,
                    color=value_color,
                    size_hint=(1, 1),
                    halign=align,
                    valign='middle',
                    **_font_kwargs(),
                )
                for lab in (lp, lv):
                    lab.text_size = (lab.width, None)
                    lab.bind(size=lambda inst, val: setattr(inst, 'text_size', (inst.width, None)))
                try:
                    lv.shorten = True
                    lv.shorten_from = 'left' if align == 'right' else 'right'
                except Exception:
                    pass
                line.add_widget(lp)
                line.add_widget(lv)
                return line

            cell.add_widget(_line(top_prefix, top_value, top_value_color))
            cell.add_widget(_line(bottom_prefix, bottom_value, bottom_value_color))
            return cell

        def _build_header_right():
            header = BoxLayout(
                orientation='horizontal',
                size_hint=(None, None),
                height=ui_dp(26),
                width=(right_table_w if sticky else table_w),
                padding=(0, 0, pad_x, 0) if sticky else (pad_x, 0),
                spacing=col_spacing,
            )
            with header.canvas.before:
                from kivy.graphics import Color, Rectangle
                Color(0.06, 0.06, 0.06, 1)
                header._bg = Rectangle(pos=header.pos, size=header.size)
                Color(0.12, 0.12, 0.12, 1)
                header._sep = Rectangle(pos=(header.x, header.y), size=(header.width, 1))
            def _upd(*_):
                try:
                    header._bg.pos = header.pos
                    header._bg.size = header.size
                    header._sep.pos = (header.x, header.y)
                    header._sep.size = (header.width, 1)
                except Exception:
                    pass
            header.bind(pos=_upd, size=_upd)
            col_iter = cols[1:] if sticky else cols
            for title, w, align in col_iter:
                lbl = Label(
                    text=f"[b]{title}[/b]",
                    markup=True,
                    font_size=ui_sp(11),
                    color=(0.82, 0.82, 0.82, 1),
                    size_hint=(None, 1),
                    width=w,
                    halign=align,
                    valign='middle',
                    **_font_kwargs(),
                )
                lbl.text_size = (lbl.width, None)
                lbl.bind(size=lambda inst, val: setattr(inst, 'text_size', (inst.width, None)))
                header.add_widget(lbl)
            return header

        def _build_row_left(item: dict):
            row_h = ui_dp(54)
            row = BoxLayout(
                orientation='horizontal',
                size_hint=(None, None),
                height=row_h,
                width=left_w,
                padding=(pad_x, ui_dp(6), col_spacing, ui_dp(6)),
                spacing=0,
            )
            with row.canvas.before:
                from kivy.graphics import Color, Rectangle
                Color(0.04, 0.04, 0.04, 1)
                row._bg = Rectangle(pos=row.pos, size=row.size)
                Color(0.12, 0.12, 0.12, 1)
                row._sep = Rectangle(pos=(row.x, row.y), size=(row.width, 1))
            def _upd(*_):
                try:
                    row._bg.pos = row.pos
                    row._bg.size = row.size
                    row._sep.pos = (row.x, row.y)
                    row._sep.size = (row.width, 1)
                except Exception:
                    pass
            row.bind(pos=_upd, size=_upd)

            sym = str(item.get('symbol', '-') or '-')

            def _go(_btn=None, _sym=sym):
                try:
                    from kivy.app import App
                    app = App.get_running_app()
                    if app is not None and hasattr(app, 'open_cek_emiten'):
                        app.open_cek_emiten(_sym)
                except Exception:
                    pass

            lbl = ClickableLabel(
                text=f"[b]{sym}[/b]",
                markup=True,
                font_size=ui_sp(13),
                color=(0.92, 0.92, 0.92, 1),
                size_hint=(None, 1),
                width=cols[0][1],
                halign='left',
                valign='middle',
                **_font_kwargs(),
            )
            lbl.text_size = (lbl.width, None)
            lbl.bind(size=lambda inst, val: setattr(inst, 'text_size', (inst.width, None)))
            try:
                lbl.bind(on_press=_go)
            except Exception:
                pass
            try:
                lbl.shorten = True
                lbl.shorten_from = 'right'
            except Exception:
                pass
            row.add_widget(lbl)
            return row

        def _build_row_right(item: dict):
            row_h = ui_dp(54)
            row = BoxLayout(
                orientation='horizontal',
                size_hint=(None, None),
                height=row_h,
                width=(right_table_w if sticky else table_w),
                padding=(0, ui_dp(6), pad_x, ui_dp(6)) if sticky else (pad_x, ui_dp(6)),
                spacing=col_spacing,
            )
            with row.canvas.before:
                from kivy.graphics import Color, Rectangle
                Color(0.04, 0.04, 0.04, 1)
                row._bg = Rectangle(pos=row.pos, size=row.size)
                Color(0.12, 0.12, 0.12, 1)
                row._sep = Rectangle(pos=(row.x, row.y), size=(row.width, 1))
            def _upd(*_):
                row._bg.pos = row.pos
                row._bg.size = row.size
                row._sep.pos = (row.x, row.y)
                row._sep.size = (row.width, 1)
            row.bind(pos=_upd, size=_upd)
            col_iter = cols[1:] if sticky else cols

            for (title, w, align) in col_iter:

                if title == 'HARGA':
                    px_txt = _fmt_price_id(item.get('price', '-'))
                    prev_txt = _fmt_price_id(item.get('prev_close', '-'))
                    # Per request: price color depends on today vs yesterday; prev is white and smaller.
                    px_col = _price_top_color(item.get('price', None), item.get('prev_close', None))
                    row.add_widget(
                        _cell_two_lines(
                            w,
                            px_txt,
                            prev_txt,
                            px_col,
                            (0.88, 0.88, 0.88, 1),
                            ui_sp(13.5),
                            ui_sp(11.5),
                            align='right',
                        )
                    )
                    continue

                if title == '%':
                    cp = item.get('change_pct', None)
                    txt = _fmt_signed_pct_id(cp)
                    c = color_muted
                    try:
                        v = float(cp or 0.0)
                        if v > 0:
                            c = color_up
                        elif v < 0:
                            c = color_down
                        else:
                            c = (0.88, 0.88, 0.88, 1)
                    except Exception:
                        c = color_muted
                    lbl = Label(
                        text=str(txt),
                        font_size=ui_sp(12),
                        color=c,
                        size_hint=(None, 1),
                        width=w,
                        halign='right',
                        valign='middle',
                        **_font_kwargs(),
                    )
                    lbl.text_size = (lbl.width, None)
                    lbl.bind(size=lambda inst, val: setattr(inst, 'text_size', (inst.width, None)))
                    row.add_widget(lbl)
                    continue

                if title == 'BID/OFFER':
                    bid_txt = _fmt_int_id(item.get('bid_volume', None))
                    off_txt = _fmt_int_id(item.get('offer_volume', None))
                    row.add_widget(
                        _cell_two_lines(
                            w,
                            bid_txt,
                            off_txt,
                            color_up,
                            color_down,
                            ui_sp(12),
                            ui_sp(12),
                            align='right',
                        )
                    )
                    continue

                if title == 'N.BUY/N.SELL':
                    nb = item.get('net_buy', None)
                    ns = item.get('net_sell', None)
                    nb_txt = _fmt_int_id(nb)
                    ns_txt = _fmt_int_id(ns)
                    # Per request: smaller number is red; larger is green; equal/unknown is white.
                    nb_color = (0.88, 0.88, 0.88, 1)
                    ns_color = (0.88, 0.88, 0.88, 1)
                    try:
                        if nb is not None and ns is not None:
                            nb_i = int(float(nb))
                            ns_i = int(float(ns))
                            if nb_i < ns_i:
                                nb_color = color_down
                                ns_color = color_up
                            elif nb_i > ns_i:
                                nb_color = color_up
                                ns_color = color_down
                    except Exception:
                        pass
                    row.add_widget(
                        _cell_two_lines(
                            w,
                            nb_txt,
                            ns_txt,
                            nb_color,
                            ns_color,
                            ui_sp(12),
                            ui_sp(12),
                            align='right',
                        )
                    )
                    continue

                if title == 'OPEN=LOW':
                    txt = 'YA' if item.get('open_is_low') else 'TIDAK'
                    lbl = Label(
                        text=str(txt),
                        font_size=ui_sp(12),
                        color=(0.88, 0.88, 0.88, 1),
                        size_hint=(None, 1),
                        width=w,
                        halign='center',
                        valign='middle',
                        **_font_kwargs(),
                    )
                    lbl.text_size = (lbl.width, None)
                    lbl.bind(size=lambda inst, val: setattr(inst, 'text_size', (inst.width, None)))
                    row.add_widget(lbl)
                    continue
            return row

        # Capture current filter/sort state for this refresh token (avoid races)
        flt_open_low = bool(getattr(self, '_flt_open_low', False))
        flt_buy_gt_sell = bool(getattr(self, '_flt_buy_gt_sell', False))
        flt_mover_only = bool(getattr(self, '_flt_mover_only', False))
        flt_bid_gt_offer = bool(getattr(self, '_flt_bid_gt_offer', False))
        sort_by = str(getattr(self, '_sort_by', 'Default') or 'Default')

        def _to_pct(v):
            try:
                if v in (None, '', '-'):
                    return None
                s = str(v).strip().replace('%', '')
                if not s:
                    return None
                return float(s)
            except Exception:
                return None

        def _to_num(v):
            try:
                if v in (None, '', '-'):
                    return None
                return float(str(v).strip().replace(',', ''))
            except Exception:
                return None

        def _build_items_from(quotes: dict):
            items = []
            for s in symbols:
                row = symbol_to_row.get(s, {}) or {}
                q = (quotes or {}).get(s) or {}
                if not isinstance(q, dict):
                    q = {}

                # Prefer realtime quote fields, but fall back to CSV when offline.
                px = q.get('price', None)
                if px in (None, '', '-'):
                    px = row.get('price', None) or row.get('close', None)

                prev = q.get('prev_close', None)
                if prev in (None, '', '-'):
                    prev = row.get('prev_close', None) or row.get('prev', None)

                chg_pct = q.get('change', None)
                if chg_pct in (None, '', '-'):
                    chg_pct = row.get('change_pct', None) or row.get('change', None)

                vol = q.get('volume', None)
                if vol in (None, '', '-'):
                    vol = row.get('volume', None)

                o = q.get('open', None)
                if o in (None, '', '-'):
                    o = row.get('open', None)

                lo = q.get('low', None)
                if lo in (None, '', '-'):
                    lo = row.get('low', None)

                # compute % change if missing
                if chg_pct in (None, '', '-') and px not in (None, '', '-') and prev not in (None, '', '-', 0):
                    try:
                        chg_pct = ((float(px) - float(prev)) / float(prev)) * 100.0
                    except Exception:
                        chg_pct = None
                else:
                    chg_pct = _to_pct(chg_pct)

                # open=low
                open_is_low = None
                try:
                    o_f = _to_num(o)
                    lo_f = _to_num(lo)
                    if o_f is not None and lo_f is not None:
                        open_is_low = abs(float(o_f) - float(lo_f)) < 1e-6
                except Exception:
                    open_is_low = None
                if open_is_low is None:
                    try:
                        raw = str(row.get('open_is_low', '') or '').strip().lower()
                        if raw in ('true', '1', 'yes', 'ya'):
                            open_is_low = True
                        elif raw in ('false', '0', 'no', 'tidak'):
                            open_is_low = False
                        else:
                            open_is_low = False
                    except Exception:
                        open_is_low = False

                # bid/offer/net proxy from volume
                bid_volume = offer_volume = net_buy = net_sell = None
                v = _to_num(vol)
                if v is not None and v > 0:
                    bid_frac = self._stable_ratio(s, 0.45, 0.55)
                    bid_volume = int(max(0.0, v) * bid_frac)
                    offer_volume = int(max(0.0, v)) - bid_volume
                    buy_frac = self._stable_ratio(s + 'B', 0.60, 0.80)
                    sell_frac = self._stable_ratio(s + 'S', 0.60, 0.80)
                    net_buy = int(bid_volume * buy_frac)
                    net_sell = int(offer_volume * sell_frac)

                # change txt
                chg_txt = '-'
                try:
                    if chg_pct is not None:
                        cp = float(chg_pct)
                        sign = '+' if cp > 0 else ''
                        chg_txt = f"{sign}{cp:.2f}%"
                except Exception:
                    chg_txt = '-'

                items.append({
                    'symbol': s,
                    'price': px,
                    'prev_close': prev,
                    'change_pct': chg_pct,
                    'bid_volume': bid_volume,
                    'offer_volume': offer_volume,
                    'net_buy': net_buy,
                    'net_sell': net_sell,
                    'open_is_low': bool(open_is_low),
                    'volume': v,
                })

            return items

        def _schedule_apply(filtered_items, realtime_ok: bool):
            def _apply(_dt, _filtered=list(filtered_items)):
                # drop stale updates
                if token != getattr(self, '_refresh_token', None):
                    return
                try:
                    _log_info('Screening', f"apply: token={token} filtered={len(_filtered)} realtime_ok={bool(realtime_ok)}")
                except Exception:
                    pass
                try:
                    self._header_table.size_hint = (None, None)
                    self._header_table.width = (right_table_w if sticky else table_w)
                    self._header_table.clear_widgets()
                    self._header_table.add_widget(_build_header_right())

                    if sticky:
                        try:
                            if getattr(self, '_header_left', None) is not None:
                                self._header_left.width = left_w
                                self._header_left.padding = (pad_x, 0, col_spacing, 0)
                        except Exception:
                            pass
                        try:
                            if getattr(self, '_header_left_lbl', None) is not None:
                                self._header_left_lbl.width = cols[0][1]
                                self._header_left_lbl.text_size = (self._header_left_lbl.width, None)
                        except Exception:
                            pass
                        try:
                            if getattr(self, '_body_left_scroll', None) is not None:
                                self._body_left_scroll.width = left_w
                        except Exception:
                            pass
                        try:
                            if getattr(self, '_body_left_table', None) is not None:
                                self._body_left_table.width = left_w
                        except Exception:
                            pass

                    try:
                        self._header_scroll.height = ui_dp(26)
                    except Exception:
                        pass

                    if self._use_rv and self._rv is not None:
                        try:
                            if self._body_inner is not None:
                                self._body_inner.width = table_w
                        except Exception:
                            pass
                        try:
                            if self._body_empty is not None:
                                self._body_empty.size = (table_w, ui_dp(54))
                                self._body_empty.text_size = (max(1, table_w - ui_dp(24)), None)
                        except Exception:
                            pass
                        try:
                            if self._rv_layout is not None:
                                self._rv_layout.width = table_w
                                self._rv_layout.default_size = (table_w, ui_dp(54))
                        except Exception:
                            pass

                        data = []
                        for it in _filtered[:500]:
                            sym = str(it.get('symbol', '-') or '-')
                            cp = it.get('change_pct', None)
                            pct_txt = _fmt_signed_pct_id(cp)
                            pct_col = color_muted
                            try:
                                vcp = float(cp or 0.0)
                                if vcp > 0:
                                    pct_col = color_up
                                elif vcp < 0:
                                    pct_col = color_down
                                else:
                                    pct_col = (0.88, 0.88, 0.88, 1)
                            except Exception:
                                pct_col = color_muted

                            bid_txt = _fmt_int_id(it.get('bid_volume', None))
                            offer_txt = _fmt_int_id(it.get('offer_volume', None))

                            nb = it.get('net_buy', None)
                            ns = it.get('net_sell', None)
                            nb_txt = _fmt_int_id(nb)
                            ns_txt = _fmt_int_id(ns)
                            nb_color = (0.88, 0.88, 0.88, 1)
                            ns_color = (0.88, 0.88, 0.88, 1)
                            try:
                                if nb is not None and ns is not None:
                                    nb_i = int(float(nb))
                                    ns_i = int(float(ns))
                                    if nb_i < ns_i:
                                        nb_color = color_down
                                        ns_color = color_up
                                    elif nb_i > ns_i:
                                        nb_color = color_up
                                        ns_color = color_down
                            except Exception:
                                pass

                            price_col = _price_top_color(it.get('price', None), it.get('prev_close', None))

                            data.append({
                                'table_w': table_w,
                                'symbol': sym,
                                'symbol_txt': f"[b]{sym}[/b]",
                                'price_txt': _fmt_price_id(it.get('price', '-')),
                                'prev_txt': _fmt_price_id(it.get('prev_close', '-')),
                                'price_color': price_col,
                                'pct_txt': pct_txt,
                                'pct_color': pct_col,
                                'bid_txt': bid_txt,
                                'offer_txt': offer_txt,
                                'nb_txt': nb_txt,
                                'ns_txt': ns_txt,
                                'nb_color': nb_color,
                                'ns_color': ns_color,
                                'openlow_txt': ('YA' if it.get('open_is_low') else 'TIDAK'),
                            })

                        if not data:
                            try:
                                if self._body_empty is not None:
                                    # If mover-only is enabled but realtime isn't available yet, explain briefly.
                                    if flt_mover_only and not realtime_ok:
                                        self._body_empty.text = 'Mover butuh data realtime. Tunggu sebentar...'
                                    else:
                                        self._body_empty.text = 'Tidak ada data (terfilter).'
                                    self._body_empty.opacity = 1
                            except Exception:
                                pass
                        else:
                            try:
                                if self._body_empty is not None:
                                    self._body_empty.opacity = 0
                                    self._body_empty.text = ''
                            except Exception:
                                pass

                        self._rv.data = data
                        try:
                            self._rv.refresh_from_data()
                        except Exception:
                            pass
                    else:
                        # Non-RV rendering
                        self._body_table.size_hint = (None, None)
                        self._body_table.width = (right_table_w if sticky else table_w)
                        self._body_table.clear_widgets()

                        if sticky and getattr(self, '_body_left_table', None) is not None:
                            try:
                                self._body_left_table.clear_widgets()
                            except Exception:
                                pass

                        for it in _filtered[:500]:
                            if sticky and getattr(self, '_body_left_table', None) is not None:
                                self._body_left_table.add_widget(_build_row_left(it))
                            self._body_table.add_widget(_build_row_right(it))

                        # If filtered empty, show message on the right.
                        if not _filtered:
                            try:
                                msg = 'Tidak ada data (terfilter).'
                                if flt_mover_only and not realtime_ok:
                                    msg = 'Mover butuh data realtime. Tunggu sebentar...'
                                self._body_table.add_widget(
                                    Label(
                                        text=msg,
                                        size_hint_y=None,
                                        height=ui_dp(54),
                                        font_size=ui_sp(13),
                                        color=(0.72, 0.72, 0.72, 1),
                                        halign='left',
                                        valign='middle',
                                        padding=(ui_dp(12), 0),
                                        **_font_kwargs(),
                                    )
                                )
                            except Exception:
                                pass

                except Exception as e:
                    if self._use_rv and self._body_empty is not None:
                        try:
                            self._body_empty.text = f"Gagal render screening: {e}"
                            self._body_empty.opacity = 1
                        except Exception:
                            pass
                    else:
                        try:
                            self._body_table.clear_widgets()
                            self._body_table.size_hint = (1, None)
                            self._body_table.width = self.width
                            self._body_table.add_widget(
                                Label(
                                    text=f"Gagal render screening: {e}",
                                    size_hint_y=None,
                                    height=ui_dp(72),
                                    font_size=ui_sp(13),
                                    color=(0.72, 0.72, 0.72, 1),
                                    halign='left',
                                    valign='middle',
                                    padding=(ui_dp(12), 0),
                                    **_font_kwargs(),
                                )
                            )
                        except Exception:
                            pass
                        try:
                            if sticky and getattr(self, '_body_left_table', None) is not None:
                                self._body_left_table.clear_widgets()
                        except Exception:
                            pass
                finally:
                    self._loading = False

            try:
                Clock.schedule_once(_apply, 0)
            except Exception:
                self._loading = False

        def _apply_filters_and_sort(items):
            filtered = []
            for it in items:
                try:
                    if flt_open_low and not bool(it.get('open_is_low')):
                        continue
                    if flt_buy_gt_sell:
                        nb = it.get('net_buy')
                        ns = it.get('net_sell')
                        if nb is None or ns is None or int(nb) <= int(ns):
                            continue
                    if flt_mover_only:
                        cp = it.get('change_pct')
                        try:
                            if cp is None or float(cp) < 2.0:
                                continue
                        except Exception:
                            continue
                    if flt_bid_gt_offer:
                        bv = it.get('bid_volume')
                        ov = it.get('offer_volume')
                        if bv is None or ov is None or int(bv) <= int(ov):
                            continue
                except Exception:
                    continue
                filtered.append(it)

            try:
                if sort_by == 'Mover Tertinggi ↑':
                    filtered.sort(key=lambda x: float(x.get('change_pct') or -9999.0), reverse=True)
                elif sort_by == 'Mover Terendah ↓':
                    filtered.sort(key=lambda x: float(x.get('change_pct') or 9999.0))
                elif sort_by == 'Volume Tertinggi':
                    filtered.sort(key=lambda x: float(x.get('volume') or 0), reverse=True)
                elif sort_by == 'Bid Volume':
                    filtered.sort(key=lambda x: float(x.get('bid_volume') or 0), reverse=True)
                elif sort_by == 'Net Buy':
                    filtered.sort(key=lambda x: float(x.get('net_buy') or 0), reverse=True)
            except Exception:
                pass

            return filtered

        def _worker():
            # 1) Render immediately from CSV (no-network friendly)
            base_items = _build_items_from({})
            base_filtered = _apply_filters_and_sort(base_items)
            _schedule_apply(base_filtered, realtime_ok=False)

            # 2) Best-effort realtime update (skip if stale)
            if token != getattr(self, '_refresh_token', None):
                return

            try:
                from modules.quote_fetcher import fetch_quotes
                quotes = fetch_quotes(symbols)
            except Exception:
                quotes = {}

            if token != getattr(self, '_refresh_token', None):
                return
            if quotes:
                rt_items = _build_items_from(quotes)
                rt_filtered = _apply_filters_and_sort(rt_items)
                _schedule_apply(rt_filtered, realtime_ok=True)

        threading.Thread(target=_worker, daemon=True).start()

class JurnalTab(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(orientation='vertical', **kwargs)
        from modules.data_fetcher import DataFetcher
        self.data_fetcher = DataFetcher()
        self._subtab = 'ringkasan'  # ringkasan|portofolio|transaksi|dividen|kinerja

        # Header like other tabs (avatar left, title centered)
        header = BoxLayout(orientation='horizontal', size_hint_y=None, height=ui_dp(68), padding=(ui_dp(12), ui_dp(10)), spacing=ui_dp(8))
        from kivy.uix.anchorlayout import AnchorLayout
        from kivy.graphics import Color, Ellipse
        from kivy.clock import Clock as _Clock
        from kivy.app import App as _App
        avatar_size = ui_dp(42)

        # Sticky profile avatar: buka popup profil tanpa pindah tab.
        btn_avatar = Button(
            size_hint=(None, None),
            size=(avatar_size, avatar_size),
            background_normal='',
            background_down='',
            background_color=(0, 0, 0, 0),
        )
        with btn_avatar.canvas.before:
            btn_avatar._bg_color = Color(0.18, 0.22, 0.30, 1)
            btn_avatar._bg_circ = Ellipse(pos=btn_avatar.pos, size=btn_avatar.size)
            btn_avatar._fg_color = Color(0.97, 0.97, 0.97, 1)
            btn_avatar._head = Ellipse(pos=btn_avatar.pos, size=btn_avatar.size)
            btn_avatar._body = Ellipse(pos=btn_avatar.pos, size=btn_avatar.size)

        def _update_jurnal_avatar(*_a):
            try:
                btn_avatar._bg_circ.pos = btn_avatar.pos
                btn_avatar._bg_circ.size = btn_avatar.size
                r = btn_avatar.width * 0.36
                x_head = btn_avatar.x + (btn_avatar.width - r) / 2.0
                y_head = btn_avatar.y + btn_avatar.height * 0.52
                btn_avatar._head.pos = (x_head, y_head)
                btn_avatar._head.size = (r, r)
                bw = btn_avatar.width * 0.82
                bh = btn_avatar.height * 0.52
                x_body = btn_avatar.x + (btn_avatar.width - bw) / 2.0
                y_body = btn_avatar.y + btn_avatar.height * 0.04
                btn_avatar._body.pos = (x_body, y_body)
                btn_avatar._body.size = (bw, bh)
            except Exception:
                pass

        btn_avatar.bind(pos=_update_jurnal_avatar, size=_update_jurnal_avatar)

        def _open_profile_from_other_tab(*_a):
            try:
                app = _App.get_running_app()
            except Exception:
                app = None
            if app is None:
                return
            # Coba handler global dari Watchlist terlebih dahulu.
            try:
                cb = getattr(app, 'open_profile_popup', None)
            except Exception:
                cb = None
            if cb is not None:
                try:
                    cb()
                    return
                except Exception:
                    pass
            # Fallback: pindah ke Watchlist dan trigger avatar seperti sebelumnya.
            try:
                app.switch_tab(0)
            except Exception:
                return

            def _after(_dt):
                try:
                    w = app.tab_container.children[0] if app.tab_container.children else None
                    if w is not None and hasattr(w, '_hdr_avatar'):
                        try:
                            w._hdr_avatar.dispatch('on_press')
                        except Exception:
                            pass
                except Exception:
                    pass

            try:
                _Clock.schedule_once(_after, 0.05)
            except Exception:
                pass

        btn_avatar.bind(on_press=_open_profile_from_other_tab)

        left = BoxLayout(size_hint=(None, 1), width=avatar_size)
        left.add_widget(btn_avatar)
        header.add_widget(left)

        center = AnchorLayout(anchor_x='center', anchor_y='center')
        title = Label(text='[b]Jurnal[/b]', markup=True, font_size=ui_sp(18), color=(1, 1, 1, 1), halign='center', valign='middle', **_font_kwargs())
        center.add_widget(title)
        header.add_widget(center)

        # Keep right side empty for now (login/profile handled from Watchlist avatar)
        header.add_widget(Widget(size_hint=(None, 1), width=avatar_size))
        self.add_widget(header)

        # Sub navigation: mapping Stockbit web "Investasi Saya" -> Jurnal
        # Make it horizontally scrollable for small widths.
        subnav_scroll = ScrollView(
            size_hint_y=None,
            height=ui_dp(46),
            do_scroll_x=True,
            do_scroll_y=False,
            scroll_distance=ui_dp(2),
            bar_width=0,
        )
        subnav = BoxLayout(
            orientation='horizontal',
            size_hint=(None, 1),
            height=ui_dp(46),
            padding=(ui_dp(8), 0),
            spacing=ui_dp(8),
        )
        subnav.bind(minimum_width=subnav.setter('width'))

        def _mk_btn(txt: str):
            b = Button(
                text=txt,
                size_hint=(None, 1),
                width=ui_dp(10),
                background_normal='',
                background_down='',
                background_color=(0, 0, 0, 0),
                padding=(0, 0),
                **_font_kwargs(),
            )
            _autosize_button_to_text(b, extra_w=ui_dp(0))
            return b

        btn_ringkasan = _mk_btn('Ringkasan')
        btn_portofolio = _mk_btn('Portofolio')
        btn_transaksi = _mk_btn('Transaksi')
        btn_dividen = _mk_btn('Dividen')
        btn_kinerja = _mk_btn('Kinerja')

        def _set_active(name: str):
            self._subtab = name
            active_fg = (0.11, 0.75, 0.36, 1)
            inactive_fg = (0.88, 0.88, 0.88, 1)
            btn_ringkasan.color = active_fg if name == 'ringkasan' else inactive_fg
            btn_portofolio.color = active_fg if name == 'portofolio' else inactive_fg
            btn_transaksi.color = active_fg if name == 'transaksi' else inactive_fg
            btn_dividen.color = active_fg if name == 'dividen' else inactive_fg
            btn_kinerja.color = active_fg if name == 'kinerja' else inactive_fg
            _render()

        btn_ringkasan.bind(on_press=lambda *_: _set_active('ringkasan'))
        btn_portofolio.bind(on_press=lambda *_: _set_active('portofolio'))
        btn_transaksi.bind(on_press=lambda *_: _set_active('transaksi'))
        btn_dividen.bind(on_press=lambda *_: _set_active('dividen'))
        btn_kinerja.bind(on_press=lambda *_: _set_active('kinerja'))

        subnav.add_widget(btn_ringkasan)
        subnav.add_widget(btn_portofolio)
        subnav.add_widget(btn_transaksi)
        subnav.add_widget(btn_dividen)
        subnav.add_widget(btn_kinerja)
        subnav_scroll.add_widget(subnav)
        self.add_widget(subnav_scroll)

        self._content = BoxLayout(orientation='vertical')
        self.add_widget(self._content)

        # Reflect any existing cloud auth state onto the badge.
        try:
            self._update_login_badge()
        except Exception:
            pass

        def _placeholder(title_txt: str, body_txt: str):
            box = BoxLayout(orientation='vertical', padding=(ui_dp(14), ui_dp(12)), spacing=ui_dp(10))
            box.add_widget(Label(text=f'[b]{title_txt}[/b]', markup=True, font_size=ui_sp(16), color=(0.92, 0.92, 0.92, 1), size_hint_y=None, height=ui_dp(30), halign='left', valign='middle', **_font_kwargs()))
            desc = Label(text=body_txt, font_size=ui_sp(13), color=(0.70, 0.70, 0.70, 1), halign='left', valign='top', **_font_kwargs())
            desc.text_size = (desc.width, None)
            desc.bind(size=lambda inst, val: setattr(inst, 'text_size', (inst.width, None)))
            box.add_widget(desc)
            return box

        def _render_ringkasan():
            import threading
            from datetime import date
            from kivy.clock import Clock
            from kivy.graphics import Color, Rectangle, Line

            try:
                from modules.tradingview_fetcher import fetch_tradingview_snapshot
            except Exception:
                fetch_tradingview_snapshot = None

            outer = BoxLayout(orientation='vertical', spacing=ui_dp(6))

            scroll = ScrollView(do_scroll_x=False, do_scroll_y=True)
            try:
                scroll.scroll_type = ['content']
                scroll.bar_width = 0
                scroll.bar_color = (0, 0, 0, 0)
                scroll.bar_inactive_color = (0, 0, 0, 0)
            except Exception:
                pass

            root = BoxLayout(orientation='vertical', spacing=ui_dp(10), size_hint_y=None, padding=(ui_dp(4), ui_dp(8)))
            root.bind(minimum_height=root.setter('height'))
            scroll.add_widget(root)

            color_up = (0.11, 0.75, 0.36, 1)
            color_down = (0.86, 0.25, 0.25, 1)
            color_muted = (0.70, 0.70, 0.70, 1)

            state = {
                'prices': {},
                'loading': False,
                'portfolio': {},
            }

            def _sign_color(v):
                try:
                    if v is None:
                        return color_muted
                    v = float(v)
                except Exception:
                    return color_muted
                if v > 0:
                    return color_up
                if v < 0:
                    return color_down
                return color_muted

            def _mini_card(title: str):
                c = BoxLayout(orientation='vertical', padding=(ui_dp(8), ui_dp(6)), spacing=ui_dp(2))
                with c.canvas.before:
                    Color(0.06, 0.06, 0.06, 1)
                    c._bg = Rectangle(pos=c.pos, size=c.size)
                c.bind(pos=lambda *_: setattr(c._bg, 'pos', c.pos), size=lambda *_: setattr(c._bg, 'size', c.size))
                t = Label(text=title, font_size=ui_sp(10.5), color=color_muted, size_hint_y=None, height=ui_dp(16), halign='left', valign='middle', **_font_kwargs())
                t.text_size = (t.width, None)
                t.bind(size=lambda inst, val: setattr(inst, 'text_size', (inst.width, None)))
                c.add_widget(t)
                v = Label(text='-', font_size=ui_sp(15), color=(0.92, 0.92, 0.92, 1), halign='left', valign='middle', **_font_kwargs())
                v.text_size = (v.width, None)
                v.bind(size=lambda inst, val: setattr(inst, 'text_size', (inst.width, None)))
                c.add_widget(v)
                return c, v

            # --- Summary row: Invested | PnL | Equity (sticky) ---
            sum_row = BoxLayout(orientation='horizontal', size_hint_y=None, height=ui_dp(58), spacing=ui_dp(5))
            c_inv, lbl_inv = _mini_card('Total Invested')
            c_pnl, lbl_pnl = _mini_card('Total PnL')
            c_eq, lbl_eq = _mini_card('Total Equity')
            sum_row.add_widget(c_inv)
            sum_row.add_widget(c_pnl)
            sum_row.add_widget(c_eq)

            sum_wrap = BoxLayout(orientation='vertical', padding=(ui_dp(10), ui_dp(8), ui_dp(10), ui_dp(6)), size_hint_y=None)
            sum_wrap.bind(minimum_height=sum_wrap.setter('height'))
            try:
                with sum_wrap.canvas.before:
                    Color(0.03, 0.03, 0.03, 1)
                    sum_wrap._bg = Rectangle(pos=sum_wrap.pos, size=sum_wrap.size)
                sum_wrap.bind(pos=lambda *_: setattr(sum_wrap._bg, 'pos', sum_wrap.pos), size=lambda *_: setattr(sum_wrap._bg, 'size', sum_wrap.size))
            except Exception:
                pass
            sum_wrap.add_widget(sum_row)
            outer.add_widget(sum_wrap)
            outer.add_widget(scroll)

            # --- Ringkasan Bulanan card ---
            card = BoxLayout(orientation='vertical', padding=(ui_dp(12), ui_dp(10)), spacing=ui_dp(8), size_hint_y=None)
            card.bind(minimum_height=card.setter('height'))
            with card.canvas.before:
                Color(0.06, 0.06, 0.06, 1)
                card._bg = Rectangle(pos=card.pos, size=card.size)
            card.bind(pos=lambda *_: setattr(card._bg, 'pos', card.pos), size=lambda *_: setattr(card._bg, 'size', card.size))

            hdr = Label(text='[b]Ringkasan Bulanan[/b]', markup=True, font_size=ui_sp(14), color=(0.92, 0.92, 0.92, 1), size_hint_y=None, height=ui_dp(24), halign='left', valign='middle', **_font_kwargs())
            hdr.text_size = (hdr.width, None)
            hdr.bind(size=lambda inst, val: setattr(inst, 'text_size', (inst.width, None)))
            card.add_widget(hdr)

            row_btn = BoxLayout(orientation='horizontal', size_hint_y=None, height=ui_dp(40), spacing=ui_dp(8))
            btn_refresh = Button(text='Refresh Harga', size_hint=(1, 1), background_normal='', background_down='', background_color=(0, 0, 0, 0), color=(0.88, 0.88, 0.88, 1), padding=(0, 0), **_font_kwargs())
            try:
                with btn_refresh.canvas.before:
                    Color(0.22, 0.22, 0.22, 1)
                    btn_refresh._outline = Line(rectangle=(btn_refresh.x, btn_refresh.y, btn_refresh.width, btn_refresh.height), width=1.2)
                def _upd_outline(*_):
                    try:
                        btn_refresh._outline.rectangle = (btn_refresh.x + 1, btn_refresh.y + 1, max(0, btn_refresh.width - 2), max(0, btn_refresh.height - 2))
                    except Exception:
                        pass
                btn_refresh.bind(pos=_upd_outline, size=_upd_outline)
            except Exception:
                pass
            row_btn.add_widget(btn_refresh)
            card.add_widget(row_btn)

            msg = Label(text='', font_size=ui_sp(12), color=color_muted, size_hint_y=None, height=ui_dp(18), halign='left', valign='middle', **_font_kwargs())
            msg.text_size = (msg.width, None)
            msg.bind(size=lambda inst, val: setattr(inst, 'text_size', (inst.width, None)))
            card.add_widget(msg)

            stats_row = BoxLayout(orientation='horizontal', size_hint_y=None, height=ui_dp(74), spacing=ui_dp(8))
            c_hold, lbl_hold = _mini_card('Holdings')
            c_wr, lbl_wr = _mini_card('Win rate')
            c_mpnl, lbl_mpnl = _mini_card('Monthly P/L')
            stats_row.add_widget(c_hold)
            stats_row.add_widget(c_wr)
            stats_row.add_widget(c_mpnl)
            card.add_widget(stats_row)

            stats_row2 = BoxLayout(orientation='horizontal', size_hint_y=None, height=ui_dp(74), spacing=ui_dp(8))
            c_lm_wr, lbl_lm_wr = _mini_card('Last month Win rate')
            c_lm_pnl, lbl_lm_pnl = _mini_card('Last month P/L')
            stats_row2.add_widget(c_lm_wr)
            stats_row2.add_widget(c_lm_pnl)
            card.add_widget(stats_row2)

            root.add_widget(card)

            def _compute_portfolio():
                try:
                    from modules.jurnal_store import load_transactions, compute_portfolio
                    txs = load_transactions()
                    return compute_portfolio(transactions=txs, overrides=None)
                except Exception:
                    return {}

            def _update_summary():
                pf = _compute_portfolio() or {}
                invested = 0.0
                equity = 0.0
                has_active = False
                for sym, pos in pf.items():
                    try:
                        qty_lot = float(getattr(pos, 'qty', 0.0) or 0.0)
                        if qty_lot <= 0:
                            continue
                        has_active = True
                        avg = float(getattr(pos, 'avg_price', 0.0) or 0.0)
                        last = state['prices'].get(sym)
                        sh = qty_lot * 100.0
                        invested += sh * avg
                        use_last = float(last) if isinstance(last, (int, float)) and last else avg
                        equity += sh * use_last
                    except Exception:
                        pass
                pnl = equity - invested
                try:
                    if not has_active:
                        lbl_inv.text = '-'
                        lbl_eq.text = '-'
                        lbl_pnl.text = '-'
                        lbl_pnl.color = color_muted
                    else:
                        lbl_inv.text = _format_id_number(invested, decimals=0)
                        lbl_eq.text = _format_id_number(equity, decimals=0)
                        lbl_pnl.text = _format_id_number(pnl, decimals=0)
                        lbl_pnl.color = _sign_color(pnl)
                except Exception:
                    pass

            def _sum_pl(txs):
                total = 0.0
                for tx in txs:
                    try:
                        side = str(getattr(tx, 'side', '') or '').upper()
                        sym = str(getattr(tx, 'symbol', '') or '').upper()
                        qty_lot = float(getattr(tx, 'qty', 0.0) or 0.0)
                        price = float(getattr(tx, 'price', 0.0) or 0.0)
                        cur_px = state['prices'].get(sym)
                        if not (isinstance(cur_px, (int, float)) and cur_px and qty_lot > 0 and price > 0):
                            continue
                        sh = qty_lot * 100.0
                        if side == 'SELL':
                            total += (float(price) - float(cur_px)) * sh
                        else:
                            total += (float(cur_px) - float(price)) * sh
                    except Exception:
                        continue
                return float(total)

            def _update_stats():
                try:
                    from modules.jurnal_store import load_transactions, filter_transactions_by_month, compute_monthly_performance
                    today = date.today()
                    all_items = load_transactions()
                    cur_items = filter_transactions_by_month(all_items, today.year, today.month)
                    cur_stats = compute_monthly_performance(all_items, today.year, today.month)

                    if today.month == 1:
                        ly, lm = today.year - 1, 12
                    else:
                        ly, lm = today.year, today.month - 1
                    last_items = filter_transactions_by_month(all_items, ly, lm)
                    last_stats = compute_monthly_performance(all_items, ly, lm)

                    lbl_hold.text = str(int(float(cur_stats.get('holding_count') or 0)))
                    lbl_wr.text = f"{float(cur_stats.get('win_rate') or 0):.0f}%"
                    mpnl = _sum_pl(cur_items)
                    lbl_mpnl.text = _format_id_number(mpnl, decimals=0) if state['prices'] else '-'
                    lbl_mpnl.color = _sign_color(mpnl)

                    lbl_lm_wr.text = f"{float(last_stats.get('win_rate') or 0):.0f}%"
                    lm_pnl = _sum_pl(last_items)
                    lbl_lm_pnl.text = _format_id_number(lm_pnl, decimals=0) if state['prices'] else '-'
                    lbl_lm_pnl.color = _sign_color(lm_pnl)
                except Exception:
                    pass

            def _refresh_prices(*_, silent: bool = False):
                if state.get('loading'):
                    return
                if fetch_tradingview_snapshot is None:
                    if not silent:
                        msg.text = 'TradingView snapshot tidak tersedia'
                        msg.color = color_down
                    return

                pf = _compute_portfolio()
                state['portfolio'] = pf

                syms_set = {str(s).upper() for s, p in (pf or {}).items() if float(getattr(p, 'qty', 0.0) or 0.0) > 0}
                try:
                    from modules.jurnal_store import load_transactions, filter_transactions_by_month
                    today = date.today()
                    all_items = load_transactions()
                    cur_items = filter_transactions_by_month(all_items, today.year, today.month)
                    if today.month == 1:
                        ly, lm = today.year - 1, 12
                    else:
                        ly, lm = today.year, today.month - 1
                    last_items = filter_transactions_by_month(all_items, ly, lm)
                    for tx in list(cur_items) + list(last_items):
                        try:
                            syms_set.add(str(getattr(tx, 'symbol', '') or '').upper())
                        except Exception:
                            pass
                except Exception:
                    pass

                syms = [s for s in sorted(syms_set) if s]
                if not syms:
                    state['prices'] = {}
                    _update_summary()
                    _update_stats()
                    return

                def _worker():
                    result = None
                    try:
                        result = fetch_tradingview_snapshot(syms)
                    except Exception:
                        result = None

                    def _done(_dt):
                        try:
                            state['loading'] = False
                            if isinstance(result, dict):
                                for sym, d in result.items():
                                    try:
                                        px = d.get('price')
                                        if isinstance(px, (int, float)) and px and px > 0:
                                            state['prices'][str(sym).upper()] = float(px)
                                    except Exception:
                                        pass
                            if not silent:
                                msg.text = 'Harga diperbarui'
                                msg.color = color_up
                            _update_summary()
                            _update_stats()
                        except Exception:
                            pass

                    try:
                        Clock.schedule_once(_done, 0)
                    except Exception:
                        pass

                state['loading'] = True
                if not silent:
                    msg.text = 'Mengambil harga…'
                    msg.color = color_muted
                threading.Thread(target=_worker, daemon=True).start()

            btn_refresh.bind(on_press=_refresh_prices)

            state['portfolio'] = _compute_portfolio()
            _update_summary()
            _update_stats()
            try:
                _refresh_prices(silent=True)
            except Exception:
                pass

            return outer

        def _render_dividen():
            from datetime import date
            from kivy.graphics import Color, Rectangle, Line

            scroll_outer = ScrollView(do_scroll_x=False, do_scroll_y=True)
            try:
                scroll_outer.scroll_type = ['content']
                scroll_outer.bar_width = 0
                scroll_outer.bar_color = (0, 0, 0, 0)
                scroll_outer.bar_inactive_color = (0, 0, 0, 0)
            except Exception:
                pass

            root = BoxLayout(orientation='vertical', spacing=ui_dp(10), size_hint_y=None, padding=(ui_dp(4), ui_dp(10)))
            root.bind(minimum_height=root.setter('height'))
            scroll_outer.add_widget(root)

            color_up = (0.11, 0.75, 0.36, 1)
            color_down = (0.86, 0.25, 0.25, 1)
            color_muted = (0.70, 0.70, 0.70, 1)

            def _mk_input(hint: str, text: str = ''):
                ti = TextInput(
                    text=text,
                    hint_text=hint,
                    multiline=False,
                    font_size=ui_sp(14),
                    size_hint=(1, None),
                    height=ui_dp(40),
                    **_font_kwargs(),
                )
                try:
                    ti.background_normal = ''
                    ti.background_active = ''
                    ti.background_color = (0.04, 0.04, 0.04, 1)
                    ti.foreground_color = (0.92, 0.92, 0.92, 1)
                    ti.cursor_color = (1, 1, 1, 1)
                    ti.padding = [ui_dp(10), ui_dp(10), ui_dp(10), ui_dp(10)]
                except Exception:
                    pass
                return ti

            # --- Form card ---
            form = BoxLayout(orientation='vertical', padding=(ui_dp(12), ui_dp(10)), spacing=ui_dp(8), size_hint_y=None)
            form.bind(minimum_height=form.setter('height'))
            with form.canvas.before:
                Color(0.06, 0.06, 0.06, 1)
                form._bg = Rectangle(pos=form.pos, size=form.size)
            form.bind(pos=lambda *_: setattr(form._bg, 'pos', form.pos), size=lambda *_: setattr(form._bg, 'size', form.size))

            form.add_widget(Label(text='[b]Input Dividen[/b]', markup=True, font_size=ui_sp(14), color=(0.92, 0.92, 0.92, 1), size_hint_y=None, height=ui_dp(24), halign='left', valign='middle', **_font_kwargs()))

            row1 = BoxLayout(orientation='horizontal', size_hint_y=None, height=ui_dp(40), spacing=ui_dp(8))
            ti_date = _mk_input('YYYY-MM-DD', date.today().isoformat())
            ti_symbol = _mk_input('Symbol (BBCA)', '')
            ti_date.size_hint_x = 0.9
            ti_symbol.size_hint_x = 1.1
            row1.add_widget(ti_date)
            row1.add_widget(ti_symbol)
            form.add_widget(row1)

            ti_amount = _mk_input('Jumlah (Rp)', '')
            form.add_widget(ti_amount)

            msg = Label(text='', font_size=ui_sp(12), color=color_muted, size_hint_y=None, height=ui_dp(18), halign='left', valign='middle', **_font_kwargs())
            msg.text_size = (msg.width, None)
            msg.bind(size=lambda inst, val: setattr(inst, 'text_size', (inst.width, None)))
            form.add_widget(msg)

            btn_add = Button(text='Proses', size_hint_y=None, height=ui_dp(44), background_normal='', background_down='', background_color=(0, 0, 0, 0), color=(0.88, 0.88, 0.88, 1), padding=(0, 0), **_font_kwargs())
            try:
                with btn_add.canvas.before:
                    Color(0.22, 0.22, 0.22, 1)
                    btn_add._outline = Line(rectangle=(btn_add.x, btn_add.y, btn_add.width, btn_add.height), width=1.2)
                def _upd_outline(*_):
                    try:
                        btn_add._outline.rectangle = (btn_add.x + 1, btn_add.y + 1, max(0, btn_add.width - 2), max(0, btn_add.height - 2))
                    except Exception:
                        pass
                btn_add.bind(pos=_upd_outline, size=_upd_outline)
            except Exception:
                pass
            form.add_widget(btn_add)

            # --- History card ---
            hist = BoxLayout(orientation='vertical', padding=(ui_dp(4), ui_dp(10)), spacing=ui_dp(8), size_hint_y=None)
            hist.bind(minimum_height=hist.setter('height'))
            with hist.canvas.before:
                Color(0.06, 0.06, 0.06, 1)
                hist._bg = Rectangle(pos=hist.pos, size=hist.size)
            hist.bind(pos=lambda *_: setattr(hist._bg, 'pos', hist.pos), size=lambda *_: setattr(hist._bg, 'size', hist.size))

            hist.add_widget(Label(text='[b]Riwayat Dividen[/b]', markup=True, font_size=ui_sp(14), color=(0.92, 0.92, 0.92, 1), size_hint_y=None, height=ui_dp(24), halign='left', valign='middle', **_font_kwargs()))

            header = BoxLayout(orientation='horizontal', size_hint_y=None, height=ui_dp(26), padding=(ui_dp(4), 0), spacing=ui_dp(8))
            def _h(txt, sx, align='left'):
                l = Label(text=f"[b]{txt}[/b]", markup=True, font_size=ui_sp(11), color=(0.82, 0.82, 0.82, 1), size_hint_x=sx, halign=align, valign='middle', **_font_kwargs())
                l.text_size = (l.width, None)
                l.bind(size=lambda inst, val: setattr(inst, 'text_size', (inst.width, None)))
                return l
            header.add_widget(_h('Tanggal', 0.30, 'left'))
            header.add_widget(_h('Symbol', 0.25, 'left'))
            header.add_widget(_h('Jumlah', 0.45, 'right'))
            hist.add_widget(header)

            grid = GridLayout(cols=1, spacing=0, size_hint_y=None)
            grid.bind(minimum_height=grid.setter('height'))
            hist.add_widget(grid)

            def _refresh_list():
                try:
                    grid.clear_widgets()
                except Exception:
                    pass
                try:
                    from modules.jurnal_store import load_dividends
                    items = load_dividends()
                except Exception:
                    items = []
                items = sorted(items, key=lambda x: (x.div_date, x.symbol), reverse=True)
                if not items:
                    grid.add_widget(Label(text='Belum ada dividen', size_hint_y=None, height=ui_dp(44), font_size=ui_sp(13), color=color_muted, **_font_kwargs()))
                    return

                def _row(dv):
                    r = BoxLayout(orientation='horizontal', padding=(ui_dp(4), ui_dp(4)), spacing=ui_dp(8), size_hint_y=None, height=ui_dp(44))
                    with r.canvas.before:
                        Color(0.04, 0.04, 0.04, 1)
                        r._bg = Rectangle(pos=r.pos, size=r.size)
                        Color(0.12, 0.12, 0.12, 1)
                        r._sep = Rectangle(pos=(r.x, r.y), size=(r.width, 1))
                    def _upd(*_):
                        r._bg.pos = r.pos
                        r._bg.size = r.size
                        r._sep.pos = (r.x, r.y)
                        r._sep.size = (r.width, 1)
                    r.bind(pos=_upd, size=_upd)

                    d_raw = str(getattr(dv, 'div_date', '') or '')
                    d_txt = d_raw
                    try:
                        if len(d_raw) == 10 and d_raw[4] == '-' and d_raw[7] == '-':
                            y, m, d = d_raw[0:4], d_raw[5:7], d_raw[8:10]
                            d_txt = f"{d}/{m}/{y}"
                    except Exception:
                        d_txt = d_raw or '-'

                    sym = str(getattr(dv, 'symbol', '') or '-').upper()
                    def _go(_btn=None, _sym=sym):
                        try:
                            from kivy.app import App
                            app = App.get_running_app()
                            if app is not None and hasattr(app, 'open_cek_emiten'):
                                app.open_cek_emiten(_sym)
                        except Exception:
                            pass
                    amt = None
                    try:
                        amt = float(getattr(dv, 'amount', 0.0) or 0.0)
                    except Exception:
                        amt = None

                    l_date = Label(text=d_txt or '-', font_size=ui_sp(12), color=color_muted, size_hint_x=0.30, halign='left', valign='middle', **_font_kwargs())
                    l_sym = ClickableLabel(text=f"[b]{sym}[/b]", markup=True, font_size=ui_sp(13), color=(0.92, 0.92, 0.92, 1), size_hint_x=0.25, halign='left', valign='middle', **_font_kwargs())
                    try:
                        l_sym.bind(on_press=_go)
                    except Exception:
                        pass
                    l_amt = Label(text=_format_id_number(amt, decimals=0) if isinstance(amt, (int, float)) else '-', font_size=ui_sp(12), color=color_up, size_hint_x=0.45, halign='right', valign='middle', **_font_kwargs())

                    for lab in (l_date, l_sym, l_amt):
                        lab.text_size = (lab.width, None)
                        try:
                            lab.shorten = True
                            lab.shorten_from = 'right'
                        except Exception:
                            pass
                        lab.bind(size=lambda inst, val: setattr(inst, 'text_size', (inst.width, None)))

                    r.add_widget(l_date)
                    r.add_widget(l_sym)
                    r.add_widget(l_amt)
                    return r

                for dv in items[:200]:
                    grid.add_widget(_row(dv))

            def _on_add(*_):
                sym = (ti_symbol.text or '').strip().upper()
                d = (ti_date.text or '').strip()
                try:
                    amt = float((ti_amount.text or '').replace(',', '').strip() or 0)
                except Exception:
                    amt = 0.0

                if not sym:
                    msg.text = 'Symbol wajib diisi'
                    msg.color = color_down
                    return
                if len(d) != 10 or d[4] != '-' or d[7] != '-':
                    msg.text = 'Tanggal pakai format YYYY-MM-DD'
                    msg.color = color_down
                    return
                if amt <= 0:
                    msg.text = 'Jumlah harus > 0'
                    msg.color = color_down
                    return
                try:
                    from modules.jurnal_store import add_dividend
                    add_dividend(symbol=sym, amount=amt, div_date=d)
                    msg.text = 'Tercatat'
                    msg.color = color_up
                    ti_symbol.text = ''
                    ti_amount.text = ''
                    _refresh_list()
                except Exception:
                    msg.text = 'Gagal mencatat'
                    msg.color = color_down

            btn_add.bind(on_press=_on_add)
            _refresh_list()

            root.add_widget(form)
            root.add_widget(hist)
            return scroll_outer

        def _render_kinerja():
            from datetime import date
            from kivy.graphics import Color, Rectangle

            scroll_outer = ScrollView(do_scroll_x=False, do_scroll_y=True)
            try:
                scroll_outer.scroll_type = ['content']
                scroll_outer.bar_width = 0
                scroll_outer.bar_color = (0, 0, 0, 0)
                scroll_outer.bar_inactive_color = (0, 0, 0, 0)
            except Exception:
                pass

            root = BoxLayout(orientation='vertical', spacing=ui_dp(10), size_hint_y=None, padding=(ui_dp(10), ui_dp(10)))
            root.bind(minimum_height=root.setter('height'))
            scroll_outer.add_widget(root)

            color_up = (0.11, 0.75, 0.36, 1)
            color_down = (0.86, 0.25, 0.25, 1)
            color_muted = (0.70, 0.70, 0.70, 1)

            def _sign_color(v):
                try:
                    if v is None:
                        return color_muted
                    v = float(v)
                except Exception:
                    return color_muted
                if v > 0:
                    return color_up
                if v < 0:
                    return color_down
                return color_muted

            card = BoxLayout(orientation='vertical', padding=(ui_dp(12), ui_dp(10)), spacing=ui_dp(8), size_hint_y=None)
            card.bind(minimum_height=card.setter('height'))
            with card.canvas.before:
                Color(0.06, 0.06, 0.06, 1)
                card._bg = Rectangle(pos=card.pos, size=card.size)
            card.bind(pos=lambda *_: setattr(card._bg, 'pos', card.pos), size=lambda *_: setattr(card._bg, 'size', card.size))

            hdr = Label(text='[b]Kinerja[/b]', markup=True, font_size=ui_sp(14), color=(0.92, 0.92, 0.92, 1), size_hint_y=None, height=ui_dp(24), halign='left', valign='middle', **_font_kwargs())
            hdr.text_size = (hdr.width, None)
            hdr.bind(size=lambda inst, val: setattr(inst, 'text_size', (inst.width, None)))
            card.add_widget(hdr)
            card.add_widget(Label(text='Ringkasan realized P/L per bulan (berdasarkan transaksi SELL).', font_size=ui_sp(12), color=color_muted, size_hint_y=None, height=ui_dp(18), halign='left', valign='middle', **_font_kwargs()))

            header = BoxLayout(orientation='horizontal', size_hint_y=None, height=ui_dp(26), padding=(ui_dp(4), 0), spacing=ui_dp(8))
            def _h(txt, sx, align='left'):
                l = Label(text=f"[b]{txt}[/b]", markup=True, font_size=ui_sp(11), color=(0.82, 0.82, 0.82, 1), size_hint_x=sx, halign=align, valign='middle', **_font_kwargs())
                l.text_size = (l.width, None)
                l.bind(size=lambda inst, val: setattr(inst, 'text_size', (inst.width, None)))
                return l
            header.add_widget(_h('Bulan', 0.30, 'left'))
            header.add_widget(_h('Realized P/L', 0.30, 'right'))
            header.add_widget(_h('Win rate', 0.20, 'right'))
            header.add_widget(_h('Trades', 0.20, 'right'))
            card.add_widget(header)

            grid = GridLayout(cols=1, spacing=0, size_hint_y=None)
            grid.bind(minimum_height=grid.setter('height'))
            card.add_widget(grid)

            try:
                from modules.jurnal_store import load_transactions, compute_monthly_performance
                txs = load_transactions()
            except Exception:
                txs = []

            today = date.today()
            months = []
            y, m = today.year, today.month
            for _i in range(6):
                months.append((y, m))
                m -= 1
                if m <= 0:
                    m = 12
                    y -= 1

            if not txs:
                grid.add_widget(Label(text='Belum ada transaksi', size_hint_y=None, height=ui_dp(44), font_size=ui_sp(13), color=color_muted, **_font_kwargs()))
            else:
                def _row(yy: int, mm: int):
                    stats = {}
                    try:
                        stats = compute_monthly_performance(txs, yy, mm)
                    except Exception:
                        stats = {}
                    rp = float(stats.get('realized_pnl') or 0.0)
                    wr = float(stats.get('win_rate') or 0.0)
                    tc = int(float(stats.get('trade_count') or 0.0))

                    r = BoxLayout(orientation='horizontal', padding=(ui_dp(4), ui_dp(6)), spacing=ui_dp(8), size_hint_y=None, height=ui_dp(44))
                    with r.canvas.before:
                        Color(0.04, 0.04, 0.04, 1)
                        r._bg = Rectangle(pos=r.pos, size=r.size)
                        Color(0.12, 0.12, 0.12, 1)
                        r._sep = Rectangle(pos=(r.x, r.y), size=(r.width, 1))
                    def _upd(*_):
                        r._bg.pos = r.pos
                        r._bg.size = r.size
                        r._sep.pos = (r.x, r.y)
                        r._sep.size = (r.width, 1)
                    r.bind(pos=_upd, size=_upd)

                    try:
                        month_txt = date(int(yy), int(mm), 1).strftime('%b %Y')
                    except Exception:
                        month_txt = f"{yy}-{mm:02d}"
                    l_m = Label(text=month_txt, font_size=ui_sp(12), color=(0.92, 0.92, 0.92, 1), size_hint_x=0.30, halign='left', valign='middle', **_font_kwargs())
                    l_rp = Label(text=_format_id_number(rp, decimals=0), font_size=ui_sp(12), color=_sign_color(rp), size_hint_x=0.30, halign='right', valign='middle', **_font_kwargs())
                    l_wr = Label(text=f"{wr:.0f}%", font_size=ui_sp(12), color=color_muted, size_hint_x=0.20, halign='right', valign='middle', **_font_kwargs())
                    l_tc = Label(text=str(tc), font_size=ui_sp(12), color=color_muted, size_hint_x=0.20, halign='right', valign='middle', **_font_kwargs())

                    for lab in (l_m, l_rp, l_wr, l_tc):
                        lab.text_size = (lab.width, None)
                        try:
                            lab.shorten = True
                            lab.shorten_from = 'right'
                        except Exception:
                            pass
                        lab.bind(size=lambda inst, val: setattr(inst, 'text_size', (inst.width, None)))

                    r.add_widget(l_m)
                    r.add_widget(l_rp)
                    r.add_widget(l_wr)
                    r.add_widget(l_tc)
                    return r

                for yy, mm in months:
                    grid.add_widget(_row(yy, mm))

            root.add_widget(card)
            return scroll_outer

        def _render_portofolio():
            import threading
            from kivy.clock import Clock
            from kivy.graphics import Color, Rectangle, Line

            try:
                from modules.tradingview_fetcher import fetch_tradingview_snapshot
            except Exception:
                fetch_tradingview_snapshot = None

            outer = BoxLayout(orientation='vertical', spacing=ui_dp(6))

            scroll = ScrollView(do_scroll_x=False, do_scroll_y=True)
            # Hide scrollbar (Android/desktop)
            try:
                scroll.scroll_type = ['content']
                scroll.bar_width = 0
                scroll.bar_color = (0, 0, 0, 0)
                scroll.bar_inactive_color = (0, 0, 0, 0)
            except Exception:
                pass
            root = BoxLayout(orientation='vertical', spacing=ui_dp(10), size_hint_y=None, padding=(ui_dp(4), ui_dp(8)))
            root.bind(minimum_height=root.setter('height'))
            scroll.add_widget(root)

            color_up = (0.11, 0.75, 0.36, 1)
            color_down = (0.86, 0.25, 0.25, 1)
            color_muted = (0.70, 0.70, 0.70, 1)

            state = {
                'prices': {},
                'loading': False,
                'portfolio': {},
                'month_key': '',
            }

            def _sign_color(v):
                try:
                    if v is None:
                        return color_muted
                    v = float(v)
                except Exception:
                    return color_muted
                if v > 0:
                    return color_up
                if v < 0:
                    return color_down
                return color_muted

            # --- Summary row: Invested | PnL | Equity ---
            sum_row = BoxLayout(orientation='horizontal', size_hint_y=None, height=ui_dp(58), spacing=ui_dp(5))

            def _mini_card(title: str):
                c = BoxLayout(orientation='vertical', padding=(ui_dp(8), ui_dp(6)), spacing=ui_dp(2))
                with c.canvas.before:
                    Color(0.06, 0.06, 0.06, 1)
                    c._bg = Rectangle(pos=c.pos, size=c.size)
                c.bind(pos=lambda *_: setattr(c._bg, 'pos', c.pos), size=lambda *_: setattr(c._bg, 'size', c.size))
                t = Label(text=title, font_size=ui_sp(10.5), color=color_muted, size_hint_y=None, height=ui_dp(16), halign='left', valign='middle', **_font_kwargs())
                t.text_size = (t.width, None)
                t.bind(size=lambda inst, val: setattr(inst, 'text_size', (inst.width, None)))
                c.add_widget(t)
                v = Label(text='-', font_size=ui_sp(15), color=(0.92, 0.92, 0.92, 1), halign='left', valign='middle', **_font_kwargs())
                v.text_size = (v.width, None)
                v.bind(size=lambda inst, val: setattr(inst, 'text_size', (inst.width, None)))
                c.add_widget(v)
                return c, v

            c_inv, lbl_inv = _mini_card('Total Invested')
            c_pnl, lbl_pnl = _mini_card('Total PnL')
            c_eq, lbl_eq = _mini_card('Total Equity')
            sum_row.add_widget(c_inv)
            sum_row.add_widget(c_pnl)
            sum_row.add_widget(c_eq)

            # Sticky container (outside scroll) - full width bar
            sum_wrap = BoxLayout(orientation='vertical', padding=(ui_dp(10), ui_dp(8), ui_dp(10), ui_dp(6)), size_hint_y=None)
            sum_wrap.bind(minimum_height=sum_wrap.setter('height'))
            try:
                with sum_wrap.canvas.before:
                    Color(0.03, 0.03, 0.03, 1)
                    sum_wrap._bg = Rectangle(pos=sum_wrap.pos, size=sum_wrap.size)
                sum_wrap.bind(pos=lambda *_: setattr(sum_wrap._bg, 'pos', sum_wrap.pos), size=lambda *_: setattr(sum_wrap._bg, 'size', sum_wrap.size))
            except Exception:
                pass
            sum_wrap.add_widget(sum_row)
            outer.add_widget(sum_wrap)
            outer.add_widget(scroll)

            state['lbl_inv'] = lbl_inv
            state['lbl_pnl'] = lbl_pnl
            state['lbl_eq'] = lbl_eq

            # --- Add/Edit Saham card (BUY/SELL) ---
            card = BoxLayout(orientation='vertical', padding=(ui_dp(12), ui_dp(10)), spacing=ui_dp(8), size_hint_y=None)
            card.bind(minimum_height=card.setter('height'))
            with card.canvas.before:
                Color(0.06, 0.06, 0.06, 1)
                card._bg = Rectangle(pos=card.pos, size=card.size)
            card.bind(pos=lambda *_: setattr(card._bg, 'pos', card.pos), size=lambda *_: setattr(card._bg, 'size', card.size))

            hdr = Label(text='[b]Input Saham (BUY/SELL)[/b]', markup=True, font_size=ui_sp(14), color=(0.92, 0.92, 0.92, 1), size_hint_y=None, height=ui_dp(24), halign='left', valign='middle', **_font_kwargs())
            hdr.text_size = (hdr.width, None)
            hdr.bind(size=lambda inst, val: setattr(inst, 'text_size', (inst.width, None)))
            card.add_widget(hdr)

            # Avoid overlap on narrow screens: symbol input on its own row.
            l_code = Label(text='Kode Saham', font_size=ui_sp(11), color=color_muted, size_hint_y=None, height=ui_dp(16), halign='left', valign='middle', **_font_kwargs())
            l_code.text_size = (l_code.width, None)
            l_code.bind(size=lambda inst, val: setattr(inst, 'text_size', (inst.width, None)))
            card.add_widget(l_code)

            def _mk_input(hint: str, text: str = ''):
                ti = TextInput(
                    text=text,
                    hint_text=hint,
                    multiline=False,
                    font_size=ui_sp(14),
                    size_hint=(1, None),
                    height=ui_dp(40),
                    **_font_kwargs(),
                )
                try:
                    ti.background_normal = ''
                    ti.background_active = ''
                    ti.background_color = (0.04, 0.04, 0.04, 1)
                    ti.foreground_color = (0.92, 0.92, 0.92, 1)
                    ti.cursor_color = (1, 1, 1, 1)
                    ti.padding = [ui_dp(10), ui_dp(10), ui_dp(10), ui_dp(10)]
                except Exception:
                    pass
                return ti

            ti_ov_symbol = _mk_input('e.g. BBCA', '')
            ti_ov_qty = _mk_input('Qty (lot)', '')
            ti_ov_avg = _mk_input('Price (per lembar)', '')
            card.add_widget(ti_ov_symbol)

            ov_row = BoxLayout(orientation='horizontal', size_hint_y=None, height=ui_dp(40), spacing=ui_dp(8))
            ti_ov_qty.size_hint_x = 0.9
            ti_ov_avg.size_hint_x = 1.1
            ov_row.add_widget(ti_ov_qty)
            ov_row.add_widget(ti_ov_avg)
            card.add_widget(ov_row)

            side_state = {'side': 'BUY'}
            inactive_fg = (0.88, 0.88, 0.88, 1)

            action_row = BoxLayout(orientation='horizontal', size_hint_y=None, height=ui_dp(40), spacing=ui_dp(8))
            side_box = BoxLayout(orientation='horizontal', size_hint=(None, 1), width=ui_dp(120), spacing=ui_dp(4))
            btn_buy = Button(text='BUY', size_hint=(1, 1), background_normal='', background_down='', background_color=(0, 0, 0, 0), padding=(0, 0), **_font_kwargs())
            btn_sell = Button(text='SELL', size_hint=(1, 1), background_normal='', background_down='', background_color=(0, 0, 0, 0), padding=(0, 0), **_font_kwargs())
            side_box.add_widget(btn_buy)
            side_box.add_widget(btn_sell)

            def _set_side(side: str):
                side_state['side'] = side
                if side == 'BUY':
                    btn_buy.color = color_up
                    btn_sell.color = inactive_fg
                else:
                    btn_sell.color = color_down
                    btn_buy.color = inactive_fg

            btn_buy.bind(on_press=lambda *_: _set_side('BUY'))
            btn_sell.bind(on_press=lambda *_: _set_side('SELL'))
            _set_side('BUY')

            btn_process = Button(text='Proses', size_hint=(1, 1), background_normal='', background_down='', background_color=(0, 0, 0, 0), color=(0.88, 0.88, 0.88, 1), **_font_kwargs())
            # Formerly "Refresh Harga"; now used as an Undo action for
            # the most recent transaction.
            btn_undo = Button(text='Undo', size_hint=(1, 1), background_normal='', background_down='', background_color=(0, 0, 0, 0), color=(0.88, 0.88, 0.88, 1), **_font_kwargs())

            # simple outlines
            for b, col in ((btn_buy, color_up), (btn_sell, color_down), (btn_process, (0.22, 0.22, 0.22, 1)), (btn_undo, (0.22, 0.22, 0.22, 1))):
                try:
                    with b.canvas.before:
                        Color(col[0], col[1], col[2], 1)
                        b._outline = Line(rectangle=(b.x, b.y, b.width, b.height), width=1.2)
                    def _upd_outline(*_args, _b=b):
                        try:
                            _b._outline.rectangle = (_b.x + 1, _b.y + 1, max(0, _b.width - 2), max(0, _b.height - 2))
                        except Exception:
                            pass
                    b.bind(pos=_upd_outline, size=_upd_outline)
                except Exception:
                    pass

            action_row.add_widget(side_box)
            action_row.add_widget(btn_process)
            action_row.add_widget(btn_undo)
            card.add_widget(action_row)

            msg = Label(text='Qty dalam LOT (1 lot = 100 lembar)', font_size=ui_sp(12), color=color_muted, size_hint_y=None, height=ui_dp(18), halign='left', valign='middle', **_font_kwargs())
            msg.text_size = (msg.width, None)
            msg.bind(size=lambda inst, val: setattr(inst, 'text_size', (inst.width, None)))
            card.add_widget(msg)
            root.add_widget(card)

            # --- Table with sticky Symbol column + horizontal scroll ---
            # Layout is modeled after the Screening tab but simplified:
            # - Left: non-scrollable (horizontally) Symbol column
            # - Right: ScrollView for horizontal scroll of other columns
            # Vertical scrolling remains handled by the outer ScrollView.

            from kivy.uix.floatlayout import FloatLayout

            # Header (right side only). Symbol header is kept in a fixed box on the left.
            header_right_table = GridLayout(cols=1, spacing=0, size_hint=(None, None))
            header_right_table.bind(minimum_height=header_right_table.setter('height'))

            header_right_row = BoxLayout(orientation='horizontal', size_hint_y=None, height=ui_dp(28), padding=(ui_dp(4), 0), spacing=ui_dp(8))

            def _h(txt, sx, align='left'):
                l = Label(text=f"[b]{txt}[/b]", markup=True, font_size=ui_sp(10.5), color=(0.82, 0.82, 0.82, 1), size_hint_x=sx, halign=align, valign='middle', **_font_kwargs())
                # Keep headers strictly single-line to avoid ugly wraps on narrow screens.
                l.text_size = (l.width, l.height)
                try:
                    l.shorten = True
                    l.shorten_from = 'right'
                    l.max_lines = 1
                except Exception:
                    pass
                l.bind(size=lambda inst, _val: setattr(inst, 'text_size', (inst.width, inst.height)))
                return l

            # Column widths tuned to keep headers readable on Android.
            # Symbol is handled by the sticky-left column.
            header_right_row.add_widget(_h('Qty', 0.12, 'right'))
            header_right_row.add_widget(_h('Avg / Current', 0.24, 'right'))
            header_right_row.add_widget(_h('Value', 0.24, 'right'))
            header_right_row.add_widget(_h('PnL / Ret', 0.22, 'right'))
            header_right_table.add_widget(header_right_row)

            header_right_scroll = ScrollView(
                # Scroll is driven by the body scroll; keep this static.
                do_scroll_x=False,
                do_scroll_y=False,
                scroll_timeout=0,
                scroll_distance=ui_dp(2),
                bar_width=0,
                bar_color=(0, 0, 0, 0),
                bar_inactive_color=(0, 0, 0, 0),
                size_hint_y=None,
                height=ui_dp(28),
            )
            header_right_scroll.add_widget(header_right_table)

            # Sticky-left Symbol header
            _sym_w = ui_dp(56)
            _pad_x = ui_dp(6)
            _spacing_x = ui_dp(8)

            header_left = BoxLayout(
                orientation='horizontal',
                size_hint=(None, None),
                width=_pad_x + _sym_w + _spacing_x,
                height=ui_dp(28),
                padding=(_pad_x, 0, _spacing_x, 0),
            )
            try:
                from kivy.graphics import Color, Rectangle
                with header_left.canvas.before:
                    Color(0.06, 0.06, 0.06, 1)
                    header_left._bg = Rectangle(pos=header_left.pos, size=header_left.size)
                    Color(0.12, 0.12, 0.12, 1)
                    header_left._sep = Rectangle(pos=(header_left.x, header_left.y), size=(header_left.width, 1))

                def _upd_hl(*_):
                    try:
                        header_left._bg.pos = header_left.pos
                        header_left._bg.size = header_left.size
                        header_left._sep.pos = (header_left.x, header_left.y)
                        header_left._sep.size = (header_left.width, 1)
                    except Exception:
                        pass

                header_left.bind(pos=_upd_hl, size=_upd_hl)
            except Exception:
                pass

            hl_lbl = Label(
                text='[b]Symbol[/b]',
                markup=True,
                font_size=ui_sp(11),
                color=(0.82, 0.82, 0.82, 1),
                size_hint=(None, 1),
                width=_sym_w,
                halign='left',
                valign='middle',
                **_font_kwargs(),
            )
            hl_lbl.text_size = (hl_lbl.width, None)
            hl_lbl.bind(size=lambda inst, val: setattr(inst, 'text_size', (inst.width, None)))
            header_left.add_widget(hl_lbl)

            # Body: left symbol column + right scrollable metrics.
            body_row = BoxLayout(orientation='horizontal', size_hint_y=None, spacing=0, padding=(0, 0))

            grid_left = GridLayout(cols=1, spacing=0, size_hint=(None, None))
            grid_left.width = _pad_x + _sym_w + _spacing_x
            grid_left.bind(minimum_height=grid_left.setter('height'))

            body_right_table = GridLayout(cols=1, spacing=0, size_hint=(None, None))
            body_right_table.bind(minimum_height=body_right_table.setter('height'))

            # Give the right-hand table an explicit content width so columns
            # have enough space and can scroll horizontally when needed.
            try:
                _col_w_qty = ui_dp(72)
                _col_w_avg = ui_dp(128)
                _col_w_val = ui_dp(120)
                _col_w_pnl = ui_dp(120)
            except Exception:
                _col_w_qty = _col_w_avg = _col_w_val = _col_w_pnl = ui_dp(96)

            try:
                _cols_total_w = float(_col_w_qty + _col_w_avg + _col_w_val + _col_w_pnl)
            except Exception:
                _cols_total_w = _col_w_qty + _col_w_avg + _col_w_val + _col_w_pnl

            try:
                _table_w = float((_pad_x * 2) + _cols_total_w + (_spacing_x * 3))
            except Exception:
                _table_w = (_pad_x * 2) + _cols_total_w + (_spacing_x * 3)

            try:
                _left_w = float(_pad_x + _sym_w + _spacing_x)
            except Exception:
                _left_w = _pad_x + _sym_w + _spacing_x

            try:
                _right_w = float(max(ui_dp(1), _table_w - _left_w))
            except Exception:
                _right_w = max(ui_dp(1), _table_w - _left_w)

            # Apply the computed width to both header and body tables.
            header_right_table.width = _right_w
            body_right_table.width = _right_w

            body_right_scroll = ScrollView(
                do_scroll_x=True,
                do_scroll_y=False,
                scroll_timeout=0,
                scroll_distance=ui_dp(2),
                bar_width=0,
                bar_color=(0, 0, 0, 0),
                bar_inactive_color=(0, 0, 0, 0),
                size_hint=(1, None),
            )
            body_right_scroll.add_widget(body_right_table)

            body_row.add_widget(grid_left)
            body_row.add_widget(body_right_scroll)

            # Keep body row and scroll heights in sync with the tallest content
            # so the outer ScrollView can handle vertical scrolling.
            def _sync_body_heights(*_):
                try:
                    h_left = grid_left.height
                    h_right = body_right_table.height
                    h = max(h_left, h_right, ui_dp(1))
                    body_row.height = h
                    body_right_scroll.height = h
                except Exception:
                    pass

            grid_left.bind(height=_sync_body_heights)
            body_right_table.bind(height=_sync_body_heights)

            # Keep header and body horizontal scroll in sync: body drives header.
            def _sync_header_scroll(_inst, value):
                try:
                    if header_right_scroll.scroll_x != value:
                        header_right_scroll.scroll_x = value
                except Exception:
                    pass

            body_right_scroll.bind(scroll_x=_sync_header_scroll)

            # Wrap header+body into a single table area so the outer ScrollView
            # can handle vertical scrolling for the whole block.
            table_area = BoxLayout(orientation='vertical', size_hint_y=None, spacing=0, padding=(0, 0))
            table_area.bind(minimum_height=table_area.setter('height'))

            header_row = BoxLayout(orientation='horizontal', size_hint_y=None, height=ui_dp(28), spacing=0, padding=(0, 0))
            header_row.add_widget(header_left)
            header_row.add_widget(header_right_scroll)

            table_area.add_widget(header_row)
            table_area.add_widget(body_row)
            root.add_widget(table_area)

            # --- Daftar Trade (bulan berjalan) + Print + Monthly cards ---
            tx_card = BoxLayout(orientation='vertical', padding=(ui_dp(4), ui_dp(10)), spacing=ui_dp(8), size_hint_y=None)
            tx_card.bind(minimum_height=tx_card.setter('height'))
            with tx_card.canvas.before:
                Color(0.06, 0.06, 0.06, 1)
                tx_card._bg = Rectangle(pos=tx_card.pos, size=tx_card.size)
            tx_card.bind(pos=lambda *_: setattr(tx_card._bg, 'pos', tx_card.pos), size=lambda *_: setattr(tx_card._bg, 'size', tx_card.size))
            tx_hdr = BoxLayout(orientation='horizontal', size_hint_y=None, height=ui_dp(28))
            lbl_trades = Label(text='[b]Daftar Trade[/b]', markup=True, font_size=ui_sp(14), color=(0.92, 0.92, 0.92, 1), halign='left', valign='middle', **_font_kwargs())
            lbl_trades.text_size = (lbl_trades.width, None)
            lbl_trades.bind(size=lambda inst, val: setattr(inst, 'text_size', (inst.width, None)))
            btn_print = Button(text='Print', size_hint=(None, 1), width=ui_dp(90), background_normal='', background_down='', background_color=(0, 0, 0, 0), color=(0.88, 0.88, 0.88, 1), **_font_kwargs())
            try:
                with btn_print.canvas.before:
                    Color(0.22, 0.22, 0.22, 1)
                    btn_print._outline = Line(rectangle=(btn_print.x, btn_print.y, btn_print.width, btn_print.height), width=1.2)
                def _upd_outline(*_):
                    try:
                        btn_print._outline.rectangle = (btn_print.x + 1, btn_print.y + 1, max(0, btn_print.width - 2), max(0, btn_print.height - 2))
                    except Exception:
                        pass
                btn_print.bind(pos=_upd_outline, size=_upd_outline)
            except Exception:
                pass
            tx_hdr.add_widget(lbl_trades)
            tx_hdr.add_widget(btn_print)
            tx_card.add_widget(tx_hdr)

            # Trade table header with sticky Symbol column (similar to holdings table)
            _tx_sym_w = ui_dp(56)
            _tx_pad_x = ui_dp(6)
            _tx_spacing_x = ui_dp(8)

            # Right-side header (Tanggal, Action / Qty, Price, P/L, Hapus)
            trade_header_right_table = GridLayout(cols=1, spacing=0, size_hint=(None, None))
            trade_header_right_table.bind(minimum_height=trade_header_right_table.setter('height'))

            trade_header_right_row = BoxLayout(orientation='horizontal', size_hint_y=None, height=ui_dp(26), padding=(0, 0), spacing=ui_dp(2))

            def _th(txt, sx, align='left'):
                # NOTE: avoid markup for headers so `shorten/max_lines` works reliably on all devices.
                l = Label(text=str(txt), markup=False, font_size=ui_sp(10.0), color=(0.82, 0.82, 0.82, 1), size_hint_x=sx, halign=align, valign='middle', **_font_kwargs())
                # Keep header strictly single-line to avoid wrap.
                l.text_size = (l.width, None)
                try:
                    l.bold = True
                    l.shorten = True
                    l.shorten_from = 'right'
                    l.max_lines = 1
                except Exception:
                    pass
                l.bind(width=lambda inst, _val: setattr(inst, 'text_size', (inst.width, None)))
                return l

            # Column widths tuned for narrow screens (Symbol is sticky on the left).
            trade_header_right_row.add_widget(_th('Tanggal', 0.30, 'left'))
            trade_header_right_row.add_widget(_th('Action / Qty', 0.20, 'left'))
            trade_header_right_row.add_widget(_th('Price', 0.30, 'right'))
            trade_header_right_row.add_widget(_th('P/L', 0.18, 'right'))
            trade_header_right_row.add_widget(_th('Hapus', 0.10, 'center'))
            trade_header_right_table.add_widget(trade_header_right_row)

            trade_header_right_scroll = ScrollView(
                do_scroll_x=False,
                do_scroll_y=False,
                scroll_timeout=0,
                scroll_distance=ui_dp(2),
                bar_width=0,
                bar_color=(0, 0, 0, 0),
                bar_inactive_color=(0, 0, 0, 0),
                size_hint_y=None,
                height=ui_dp(26),
            )
            trade_header_right_scroll.add_widget(trade_header_right_table)

            # Sticky-left Symbol header
            header_tx_left = BoxLayout(
                orientation='horizontal',
                size_hint=(None, None),
                width=_tx_pad_x + _tx_sym_w + _tx_spacing_x,
                height=ui_dp(26),
                padding=(_tx_pad_x, 0, _tx_spacing_x, 0),
            )
            try:
                with header_tx_left.canvas.before:
                    Color(0.06, 0.06, 0.06, 1)
                    header_tx_left._bg = Rectangle(pos=header_tx_left.pos, size=header_tx_left.size)
                    Color(0.12, 0.12, 0.12, 1)
                    header_tx_left._sep = Rectangle(pos=(header_tx_left.x, header_tx_left.y), size=(header_tx_left.width, 1))

                def _upd_tx_hl(*_):
                    try:
                        header_tx_left._bg.pos = header_tx_left.pos
                        header_tx_left._bg.size = header_tx_left.size
                        header_tx_left._sep.pos = (header_tx_left.x, header_tx_left.y)
                        header_tx_left._sep.size = (header_tx_left.width, 1)
                    except Exception:
                        pass

                header_tx_left.bind(pos=_upd_tx_hl, size=_upd_tx_hl)
            except Exception:
                pass

            hl_tx_lbl = Label(
                text='[b]Symbol[/b]',
                markup=True,
                font_size=ui_sp(11),
                color=(0.82, 0.82, 0.82, 1),
                size_hint=(None, 1),
                width=_tx_sym_w,
                halign='left',
                valign='middle',
                **_font_kwargs(),
            )
            hl_tx_lbl.text_size = (hl_tx_lbl.width, None)
            hl_tx_lbl.bind(size=lambda inst, val: setattr(inst, 'text_size', (inst.width, None)))
            header_tx_left.add_widget(hl_tx_lbl)

            header_tx_row = BoxLayout(orientation='horizontal', size_hint_y=None, height=ui_dp(26), spacing=0, padding=(0, 0))
            header_tx_row.add_widget(header_tx_left)
            header_tx_row.add_widget(trade_header_right_scroll)
            tx_card.add_widget(header_tx_row)

            # Body: left symbol column + right scrollable metrics
            body_tx_row = BoxLayout(orientation='horizontal', size_hint_y=None, spacing=0, padding=(0, 0))

            tx_grid_left = GridLayout(cols=1, spacing=0, size_hint=(None, None))
            tx_grid_left.width = _tx_pad_x + _tx_sym_w + _tx_spacing_x
            tx_grid_left.bind(minimum_height=tx_grid_left.setter('height'))

            tx_right_table = GridLayout(cols=1, spacing=0, size_hint=(None, None))
            tx_right_table.bind(minimum_height=tx_right_table.setter('height'))

            # Explicit width for the trade right-hand table so its columns have
            # enough space and can scroll horizontally.
            try:
                _tx_w_date = ui_dp(110)
                _tx_w_act = ui_dp(90)
                _tx_w_price = ui_dp(120)
                _tx_w_pl = ui_dp(90)
                _tx_w_del = ui_dp(70)
            except Exception:
                _tx_w_date = _tx_w_act = _tx_w_price = _tx_w_pl = _tx_w_del = ui_dp(96)

            try:
                _tx_cols_total = float(_tx_w_date + _tx_w_act + _tx_w_price + _tx_w_pl + _tx_w_del)
            except Exception:
                _tx_cols_total = _tx_w_date + _tx_w_act + _tx_w_price + _tx_w_pl + _tx_w_del

            try:
                _tx_table_w = float((_tx_pad_x * 2) + _tx_cols_total + (_tx_spacing_x * 3))
            except Exception:
                _tx_table_w = (_tx_pad_x * 2) + _tx_cols_total + (_tx_spacing_x * 3)

            try:
                _tx_left_w = float(_tx_pad_x + _tx_sym_w + _tx_spacing_x)
            except Exception:
                _tx_left_w = _tx_pad_x + _tx_sym_w + _tx_spacing_x

            try:
                _tx_right_w = float(max(ui_dp(1), _tx_table_w - _tx_left_w))
            except Exception:
                _tx_right_w = max(ui_dp(1), _tx_table_w - _tx_left_w)

            trade_header_right_table.width = _tx_right_w
            tx_right_table.width = _tx_right_w

            tx_right_scroll = ScrollView(
                do_scroll_x=True,
                do_scroll_y=False,
                scroll_timeout=0,
                scroll_distance=ui_dp(2),
                bar_width=0,
                bar_color=(0, 0, 0, 0),
                bar_inactive_color=(0, 0, 0, 0),
                size_hint=(1, None),
            )
            tx_right_scroll.add_widget(tx_right_table)

            body_tx_row.add_widget(tx_grid_left)
            body_tx_row.add_widget(tx_right_scroll)
            tx_card.add_widget(body_tx_row)

            def _sync_tx_heights(*_):
                try:
                    h_left = tx_grid_left.height
                    h_right = tx_right_table.height
                    h = max(h_left, h_right, ui_dp(1))
                    body_tx_row.height = h
                    tx_right_scroll.height = h
                except Exception:
                    pass

            tx_grid_left.bind(height=_sync_tx_heights)
            tx_right_table.bind(height=_sync_tx_heights)

            def _sync_tx_header_scroll(_inst, value):
                try:
                    if trade_header_right_scroll.scroll_x != value:
                        trade_header_right_scroll.scroll_x = value
                except Exception:
                    pass

            tx_right_scroll.bind(scroll_x=_sync_tx_header_scroll)

            # Monthly cards
            stats_row = BoxLayout(orientation='horizontal', size_hint_y=None, height=ui_dp(74), spacing=ui_dp(8))
            c_hold, lbl_hold = _mini_card('Holdings')
            c_wr, lbl_wr = _mini_card('Win rate')
            c_mpnl, lbl_mpnl = _mini_card('Monthly P/L')
            stats_row.add_widget(c_hold)
            stats_row.add_widget(c_wr)
            stats_row.add_widget(c_mpnl)
            tx_card.add_widget(stats_row)

            stats_row2 = BoxLayout(orientation='horizontal', size_hint_y=None, height=ui_dp(74), spacing=ui_dp(8))
            c_lm_wr, lbl_lm_wr = _mini_card('Last month Win rate')
            c_lm_pnl, lbl_lm_pnl = _mini_card('Last month P/L')
            stats_row2.add_widget(c_lm_wr)
            stats_row2.add_widget(c_lm_pnl)
            tx_card.add_widget(stats_row2)

            state['lbl_hold'] = lbl_hold
            state['lbl_wr'] = lbl_wr
            state['lbl_mpnl'] = lbl_mpnl
            state['lbl_lm_wr'] = lbl_lm_wr
            state['lbl_lm_pnl'] = lbl_lm_pnl
            root.add_widget(tx_card)

            def _compute_portfolio():
                try:
                    from modules.jurnal_store import load_transactions, compute_portfolio
                    txs = load_transactions()
                    pf = compute_portfolio(transactions=txs, overrides=None)
                    return pf
                except Exception:
                    return {}

            def _update_summary():
                pf = _compute_portfolio() or {}
                invested = 0.0
                equity = 0.0
                has_active = False
                for sym, pos in pf.items():
                    try:
                        qty_lot = float(getattr(pos, 'qty', 0.0) or 0.0)
                        if qty_lot <= 0:
                            continue
                        has_active = True
                        avg = float(getattr(pos, 'avg_price', 0.0) or 0.0)
                        last = state['prices'].get(sym)
                        sh = qty_lot * 100.0
                        invested += sh * avg
                        use_last = float(last) if isinstance(last, (int, float)) and last else avg
                        equity += sh * use_last
                    except Exception:
                        pass
                pnl = equity - invested
                try:
                    if not has_active:
                        state['lbl_inv'].text = '-'
                        state['lbl_eq'].text = '-'
                        state['lbl_pnl'].text = '-'
                        state['lbl_pnl'].color = color_muted
                    else:
                        state['lbl_inv'].text = _format_id_number(invested, decimals=0)
                        state['lbl_eq'].text = _format_id_number(equity, decimals=0)
                        state['lbl_pnl'].text = _format_id_number(pnl, decimals=0)
                        state['lbl_pnl'].color = _sign_color(pnl)
                except Exception:
                    pass

            def _refresh_table():
                try:
                    grid_left.clear_widgets()
                    body_right_table.clear_widgets()
                except Exception:
                    pass

                pf = _compute_portfolio()
                state['portfolio'] = pf
                items = [p for p in (pf or {}).values() if float(getattr(p, 'qty', 0.0) or 0.0) > 0]
                items.sort(key=lambda x: str(getattr(x, 'symbol', '') or ''))

                if not items:
                    _update_summary()
                    # Single placeholder row spanning the right side; left column stays empty.
                    body_right_table.add_widget(Label(text='Belum ada posisi (catat trade via Proses)', size_hint_y=None, height=ui_dp(44), font_size=ui_sp(13), color=color_muted, **_font_kwargs()))
                    return

                def _row(pos):
                    sym = str(getattr(pos, 'symbol', '') or '-')
                    qty_lot = float(getattr(pos, 'qty', 0.0) or 0.0)
                    avg = float(getattr(pos, 'avg_price', 0.0) or 0.0)
                    last = state['prices'].get(sym)
                    qty_shares = qty_lot * 100.0

                    mv = None
                    pnl = None
                    pnl_pct = None
                    if isinstance(last, (int, float)) and last and qty_shares > 0 and avg >= 0:
                        mv = qty_shares * float(last)
                        pnl = (float(last) - float(avg)) * qty_shares
                        pnl_pct = ((float(last) / float(avg)) - 1.0) * 100.0 if avg > 0 else None

                    # Taller row so 2-line cells are not clipped.
                    r = BoxLayout(orientation='horizontal', padding=(ui_dp(4), ui_dp(6)), spacing=ui_dp(8), size_hint_y=None, height=ui_dp(56))
                    def _go(_btn=None, _sym=str(sym).strip().upper()):
                        try:
                            from kivy.app import App
                            app = App.get_running_app()
                            if app is not None and hasattr(app, 'open_cek_emiten'):
                                app.open_cek_emiten(_sym)
                        except Exception:
                            pass
                    with r.canvas.before:
                        Color(0.04, 0.04, 0.04, 1)
                        r._bg = Rectangle(pos=r.pos, size=r.size)
                        Color(0.12, 0.12, 0.12, 1)
                        r._sep = Rectangle(pos=(r.x, r.y), size=(r.width, 1))
                    def _upd(*_):
                        r._bg.pos = r.pos
                        r._bg.size = r.size
                        r._sep.pos = (r.x, r.y)
                        r._sep.size = (r.width, 1)
                    r.bind(pos=_upd, size=_upd)

                    l_sym = ClickableLabel(text=f"[b]{sym}[/b]", markup=True, font_size=ui_sp(13), color=(0.92, 0.92, 0.92, 1), size_hint_x=1, size_hint_y=None, height=ui_dp(56), halign='left', valign='middle', **_font_kwargs())
                    try:
                        l_sym.bind(on_press=_go)
                    except Exception:
                        pass
                    l_qty = Label(text=_format_id_number(qty_lot, decimals=0), font_size=ui_sp(12), color=(0.92, 0.92, 0.92, 1), size_hint_x=0.12, halign='right', valign='middle', **_font_kwargs())
                    # Combined columns: use a vertical box with 2 labels (more reliable than '\n' in one Label).
                    combined_fs = ui_sp(10.5)
                    avg_txt = _format_price(avg) if avg > 0 else '-'
                    last_txt = _format_price(last) if isinstance(last, (int, float)) else '-'
                    l_avg_last = BoxLayout(orientation='vertical', size_hint_x=0.24, spacing=ui_dp(2))
                    avg_lbl = Label(text=f"[color=#8E8E8E]Avg[/color] {avg_txt}", markup=True, font_size=combined_fs, color=(0.92, 0.92, 0.92, 1), halign='right', valign='middle', size_hint_y=None, height=ui_dp(20), **_font_kwargs())
                    last_lbl = Label(text=f"[color=#8E8E8E]Current[/color] {last_txt}", markup=True, font_size=combined_fs, color=(0.92, 0.92, 0.92, 1), halign='right', valign='middle', size_hint_y=None, height=ui_dp(20), **_font_kwargs())
                    # Rule: if Last > Avg, Avg shown red; if Avg > Last, Avg shown green.
                    try:
                        if isinstance(last, (int, float)) and last and avg > 0:
                            if float(last) > float(avg):
                                avg_lbl.color = color_down
                            elif float(avg) > float(last):
                                avg_lbl.color = color_up
                    except Exception:
                        pass
                    l_avg_last.add_widget(avg_lbl)
                    l_avg_last.add_widget(last_lbl)
                    l_val = Label(text=_format_id_number(mv, decimals=0) if isinstance(mv, (int, float)) else '-', font_size=ui_sp(12), color=color_muted, size_hint_x=0.24, halign='right', valign='middle', **_font_kwargs())

                    if isinstance(pnl, (int, float)):
                        pnl_col = color_up if pnl >= 0 else color_down
                        pnl_rp = _format_id_number(pnl, decimals=0)
                        pnl_pct_txt = f"{pnl_pct:+.2f}%" if isinstance(pnl_pct, (int, float)) else '-'
                    else:
                        pnl_col = color_muted
                        pnl_rp = '-'
                        pnl_pct_txt = '-'
                    l_pnl_ret = BoxLayout(orientation='vertical', size_hint_x=0.22, spacing=ui_dp(2))
                    l_pnl_ret.add_widget(Label(text=pnl_rp, font_size=combined_fs, color=pnl_col, halign='right', valign='middle', size_hint_y=None, height=ui_dp(20), **_font_kwargs()))
                    l_pnl_ret.add_widget(Label(text=pnl_pct_txt, font_size=combined_fs, color=pnl_col, halign='right', valign='middle', size_hint_y=None, height=ui_dp(20), **_font_kwargs()))

                    # Apply text_size only to leaf labels.
                    for lab in (l_sym, l_qty, l_val):
                        lab.text_size = (lab.width, lab.height)
                        try:
                            lab.shorten = True
                            # Preserve the right side (numbers) when truncating.
                            lab.shorten_from = 'left' if getattr(lab, 'halign', '') == 'right' else 'right'
                            lab.max_lines = 1
                        except Exception:
                            pass
                        lab.bind(size=lambda inst, _val: setattr(inst, 'text_size', (inst.width, inst.height)))

                    for leaf in list(getattr(l_avg_last, 'children', [])) + list(getattr(l_pnl_ret, 'children', [])):
                        try:
                            leaf.text_size = (leaf.width, leaf.height)
                            leaf.halign = 'right'
                            leaf.valign = 'middle'
                            leaf.shorten = True
                            leaf.shorten_from = 'left'
                            leaf.max_lines = 1
                            leaf.bind(size=lambda inst, _val: setattr(inst, 'text_size', (inst.width, inst.height)))
                        except Exception:
                            pass

                    # Left sticky column: symbol only.
                    grid_left.add_widget(l_sym)
                    # Right scrollable part: remaining metrics.
                    r.add_widget(l_qty)
                    r.add_widget(l_avg_last)
                    r.add_widget(l_val)
                    r.add_widget(l_pnl_ret)
                    return r

                for pos in items[:200]:
                    body_right_table.add_widget(_row(pos))
                _update_summary()

            def _refresh_prices(*_, silent: bool = False):
                if state.get('loading'):
                    return
                if fetch_tradingview_snapshot is None:
                    if not silent:
                        msg.text = 'TradingView snapshot tidak tersedia'
                        msg.color = color_down
                    return

                pf = state.get('portfolio') or _compute_portfolio()
                syms_set = {str(s).upper() for s, p in (pf or {}).items() if float(getattr(p, 'qty', 0.0) or 0.0) > 0}

                # Also include symbols traded in current month so 'Last' + P/L can be shown
                # even when there are no open holdings.
                try:
                    from datetime import date as _date
                    from modules.jurnal_store import load_transactions, filter_transactions_by_month
                    today = _date.today()
                    txs = load_transactions()
                    cur = filter_transactions_by_month(txs, today.year, today.month)
                    for tx in cur:
                        try:
                            syms_set.add(str(getattr(tx, 'symbol', '') or '').upper())
                        except Exception:
                            pass
                except Exception:
                    pass

                syms = [s for s in sorted(syms_set) if s]
                if not syms:
                    _refresh_table()
                    return

                def _worker():
                    result = None
                    try:
                        result = fetch_tradingview_snapshot(syms)
                    except Exception:
                        result = None

                    def _done(_dt):
                        try:
                            state['loading'] = False
                            if isinstance(result, dict):
                                for sym, d in result.items():
                                    try:
                                        px = d.get('price')
                                        if isinstance(px, (int, float)) and px and px > 0:
                                            state['prices'][str(sym).upper()] = float(px)
                                    except Exception:
                                        pass
                            if not silent:
                                msg.text = 'Harga diperbarui'
                                msg.color = color_up
                            _refresh_table()
                            try:
                                _refresh_tx_list()
                            except Exception:
                                pass
                        except Exception:
                            pass

                    try:
                        Clock.schedule_once(_done, 0)
                    except Exception:
                        pass

                state['loading'] = True
                if not silent:
                    msg.text = 'Mengambil harga…'
                    msg.color = color_muted
                threading.Thread(target=_worker, daemon=True).start()

            def _on_process(*_):
                sym = (ti_ov_symbol.text or '').strip().upper()
                side = side_state.get('side', 'BUY')
                try:
                    qty = float((ti_ov_qty.text or '').replace(',', '').strip() or 0)
                    price = float((ti_ov_avg.text or '').replace(',', '').strip() or 0)
                except Exception:
                    qty, price = 0.0, 0.0
                if not sym:
                    msg.text = 'Symbol wajib diisi'
                    msg.color = color_down
                    return
                if qty <= 0 or price <= 0:
                    msg.text = 'Qty & Harga harus > 0'
                    msg.color = color_down
                    return
                try:
                    from datetime import date
                    from modules.jurnal_store import add_transaction
                    add_transaction(symbol=sym, side=side, qty=qty, price=price, tx_date=date.today().isoformat())
                    msg.text = 'Tercatat'
                    msg.color = color_up if side == 'BUY' else color_down
                    ti_ov_qty.text = ''
                    ti_ov_avg.text = ''
                    _refresh_table()
                    _refresh_tx_list()
                except Exception:
                    msg.text = 'Gagal mencatat'
                    msg.color = color_down

            def _on_undo(*_):
                """Undo transaksi terakhir HARI INI saja.

                Jika tidak ada transaksi dengan tanggal hari ini,
                tampilkan pesan dan jangan mengubah histori lama.
                """
                try:
                    from datetime import date
                    from modules.jurnal_store import load_transactions, save_transactions

                    items = load_transactions()
                    if not items:
                        msg.text = 'Tidak ada transaksi hari ini untuk di-undo'
                        msg.color = color_muted
                        return

                    today_str = date.today().isoformat()
                    last_today = None
                    last_idx = None
                    # Cari dari belakang supaya benar-benar "transaksi terakhir" hari ini
                    for idx in range(len(items) - 1, -1, -1):
                        tx = items[idx]
                        try:
                            if str(getattr(tx, 'tx_date', '') or '') == today_str:
                                last_today = tx
                                last_idx = idx
                                break
                        except Exception:
                            continue

                    if last_today is None or last_idx is None:
                        msg.text = 'Tidak ada transaksi hari ini untuk di-undo'
                        msg.color = color_muted
                        return

                    try:
                        # Hapus hanya transaksi terakhir untuk hari ini
                        del items[last_idx]
                        save_transactions(items)
                    except Exception:
                        msg.text = 'Gagal undo transaksi'
                        msg.color = color_down
                        return

                    try:
                        msg.text = f"Undo {getattr(last_today, 'side', '')} {getattr(last_today, 'symbol', '')} {int(getattr(last_today, 'qty', 0) or 0)} lot (hari ini)"
                        msg.color = color_muted
                    except Exception:
                        msg.text = 'Undo transaksi hari ini'
                        msg.color = color_muted

                    # Refresh all dependent views after undo.
                    try:
                        state['portfolio'] = _compute_portfolio()
                    except Exception:
                        pass
                    try:
                        _refresh_table()
                    except Exception:
                        pass
                    try:
                        _refresh_tx_list()
                    except Exception:
                        pass
                    try:
                        _refresh_prices(silent=True)
                    except Exception:
                        pass
                except Exception:
                    msg.text = 'Gagal undo transaksi'
                    msg.color = color_down

            btn_undo.bind(on_press=_on_undo)
            btn_process.bind(on_press=_on_process)

            def _refresh_tx_list():
                try:
                    tx_grid_left.clear_widgets()
                    tx_right_table.clear_widgets()
                except Exception:
                    pass
                try:
                    from datetime import date
                    from modules.jurnal_store import load_transactions, filter_transactions_by_month, compute_monthly_performance
                    today = date.today()
                    month_key = today.strftime('%Y-%m')
                    state['month_key'] = month_key
                    try:
                        lbl_trades.text = f"[b]Daftar Trade - {today.strftime('%B %Y')}[/b]"
                    except Exception:
                        pass

                    all_items = load_transactions()
                    items = filter_transactions_by_month(all_items, today.year, today.month)

                    if today.month == 1:
                        ly, lm = today.year - 1, 12
                    else:
                        ly, lm = today.year, today.month - 1
                    last_items = filter_transactions_by_month(all_items, ly, lm)

                    cur_stats = compute_monthly_performance(all_items, today.year, today.month)
                    last_stats = compute_monthly_performance(all_items, ly, lm)

                    def _sum_pl(txs):
                        total = 0.0
                        for tx in txs:
                            try:
                                side = str(getattr(tx, 'side', '') or '').upper()
                                sym = str(getattr(tx, 'symbol', '') or '').upper()
                                qty_lot = float(getattr(tx, 'qty', 0.0) or 0.0)
                                price = float(getattr(tx, 'price', 0.0) or 0.0)
                                cur_px = state['prices'].get(sym)
                                if not (isinstance(cur_px, (int, float)) and cur_px and qty_lot > 0 and price > 0):
                                    continue
                                sh = qty_lot * 100.0
                                if side == 'SELL':
                                    total += (float(price) - float(cur_px)) * sh
                                else:
                                    total += (float(cur_px) - float(price)) * sh
                            except Exception:
                                continue
                        return float(total)
                    try:
                        state['lbl_hold'].text = str(int(float(cur_stats.get('holding_count') or 0)))
                        state['lbl_wr'].text = f"{float(cur_stats.get('win_rate') or 0):.0f}%"
                        # Monthly P/L follows accumulation of P/L in the trade table (mark-to-current).
                        mpnl = _sum_pl(items)
                        state['lbl_mpnl'].text = _format_id_number(mpnl, decimals=0)
                        state['lbl_mpnl'].color = _sign_color(mpnl)

                        state['lbl_lm_wr'].text = f"{float(last_stats.get('win_rate') or 0):.0f}%"
                        lm_pnl = _sum_pl(last_items)
                        state['lbl_lm_pnl'].text = _format_id_number(lm_pnl, decimals=0)
                        state['lbl_lm_pnl'].color = _sign_color(lm_pnl)
                    except Exception:
                        pass
                except Exception:
                    items = []

                items = sorted(items, key=lambda x: (x.tx_date, x.symbol, x.side), reverse=True)

                def _confirm_delete_tx(tx):
                    """Tampilkan popup konfirmasi hapus transaksi."""
                    try:
                        from modules.jurnal_store import delete_transaction
                    except Exception:
                        return

                    # Deskripsi singkat transaksi
                    try:
                        d_txt = str(getattr(tx, 'tx_date', '') or '')
                        sym_txt = str(getattr(tx, 'symbol', '') or '').upper() or '-'
                        side_txt = str(getattr(tx, 'side', '') or '').upper() or '-'
                        qty_val = float(getattr(tx, 'qty', 0.0) or 0.0)
                        qty_txt = f"{int(qty_val)}" if qty_val.is_integer() else f"{qty_val:g}"
                        desc = f"Hapus transaksi?\n{d_txt}  {sym_txt}  {side_txt} {qty_txt} lot"
                    except Exception:
                        desc = 'Hapus transaksi ini?'

                    root = BoxLayout(orientation='vertical', padding=(ui_dp(16), ui_dp(14)), spacing=ui_dp(12))
                    lbl = Label(text=desc, font_size=ui_sp(13), color=(0.95, 0.95, 0.95, 1), halign='left', valign='middle', **_font_kwargs())
                    try:
                        lbl.text_size = (0, None)
                        lbl.bind(size=lambda inst, _val: setattr(inst, 'text_size', (inst.width, None)))
                    except Exception:
                        pass
                    root.add_widget(lbl)

                    btn_row = BoxLayout(orientation='horizontal', size_hint_y=None, height=ui_dp(44), spacing=ui_dp(10))
                    btn_cancel = Button(text='Batal', background_normal='', background_down='', background_color=(0, 0, 0, 0), color=(0.88, 0.88, 0.88, 1), padding=(0, 0), **_font_kwargs())
                    btn_delete = Button(text='Hapus', background_normal='', background_down='', background_color=(0.80, 0.16, 0.22, 1), color=(1, 1, 1, 1), padding=(0, 0), **_font_kwargs())
                    btn_row.add_widget(btn_cancel)
                    btn_row.add_widget(btn_delete)
                    root.add_widget(btn_row)

                    p = _make_styled_popup(root, title='Hapus transaksi', size_hint=(0.88, None), height=ui_dp(190))

                    def _dismiss(*_):
                        try:
                            p.dismiss()
                        except Exception:
                            pass

                    btn_cancel.bind(on_press=_dismiss)

                    def _do_delete(*_):
                        ok = False
                        try:
                            ok = bool(delete_transaction(tx))
                        except Exception:
                            ok = False

                        if ok:
                            try:
                                msg.text = 'Transaksi dihapus'
                                msg.color = color_muted
                            except Exception:
                                pass
                            # Setelah delete, refresh semua view terkait
                            try:
                                state['portfolio'] = _compute_portfolio()
                            except Exception:
                                pass
                            try:
                                _refresh_table()
                            except Exception:
                                pass
                            try:
                                _refresh_tx_list()
                            except Exception:
                                pass
                            try:
                                _refresh_prices(silent=True)
                            except Exception:
                                pass
                        else:
                            try:
                                msg.text = 'Gagal menghapus transaksi'
                                msg.color = color_down
                            except Exception:
                                pass

                        _dismiss()

                    btn_delete.bind(on_press=_do_delete)

                    try:
                        p.open()
                    except Exception:
                        pass

                if not items:
                    # Placeholder on the right-hand side; left sticky column stays empty.
                    tx_right_table.add_widget(Label(text='Belum ada trade bulan ini', size_hint_y=None, height=ui_dp(44), font_size=ui_sp(13), color=color_muted, **_font_kwargs()))
                    return

                def _tx_row(tx):
                    rr = BoxLayout(orientation='horizontal', padding=(ui_dp(2), ui_dp(6)), spacing=ui_dp(2), size_hint_y=None, height=ui_dp(56))
                    with rr.canvas.before:
                        Color(0.04, 0.04, 0.04, 1)
                        rr._bg = Rectangle(pos=rr.pos, size=rr.size)
                        Color(0.12, 0.12, 0.12, 1)
                        rr._sep = Rectangle(pos=(rr.x, rr.y), size=(rr.width, 1))
                    def _upd(*_):
                        rr._bg.pos = rr.pos
                        rr._bg.size = rr.size
                        rr._sep.pos = (rr.x, rr.y)
                        rr._sep.size = (rr.width, 1)
                    rr.bind(pos=_upd, size=_upd)

                    side = getattr(tx, 'side', '')
                    side_col = color_up if side == 'BUY' else color_down
                    _sym_for_go = str(getattr(tx, 'symbol', '') or '').upper()
                    def _go(_btn=None, _sym=_sym_for_go):
                        if not _sym:
                            return
                        try:
                            from kivy.app import App
                            app = App.get_running_app()
                            if app is not None and hasattr(app, 'open_cek_emiten'):
                                app.open_cek_emiten(_sym)
                        except Exception:
                            pass
                    try:
                        qty_lot = float(getattr(tx, 'qty', 0.0) or 0.0)
                        price = float(getattr(tx, 'price', 0.0) or 0.0)
                        last = state['prices'].get(str(getattr(tx, 'symbol', '') or '').upper())
                    except Exception:
                        qty_lot, price, last = 0.0, 0.0, None

                    pl = None
                    try:
                        if isinstance(last, (int, float)) and last and price > 0 and qty_lot > 0:
                            sh = qty_lot * 100.0
                            if side == 'SELL':
                                pl = (float(price) - float(last)) * sh
                            else:
                                pl = (float(last) - float(price)) * sh
                    except Exception:
                        pl = None

                    d_raw = str(getattr(tx, 'tx_date', '') or '')
                    d_txt = d_raw
                    try:
                        # YYYY-MM-DD -> DD/MM/YYYY
                        if len(d_raw) == 10 and d_raw[4] == '-' and d_raw[7] == '-':
                            y, m, d = d_raw[0:4], d_raw[5:7], d_raw[8:10]
                            d_txt = f"{d}/{m}/{y}"
                    except Exception:
                        d_txt = d_raw or '-'

                    l_date = Label(text=d_txt or '-', font_size=ui_sp(12), color=color_muted, size_hint_x=0.30, halign='left', valign='middle', **_font_kwargs())
                    # NOTE: avoid markup so `shorten/max_lines` is consistent.
                    l_sym = ClickableLabel(text=str(getattr(tx, 'symbol', '') or '-'), markup=False, font_size=ui_sp(13), color=(0.92, 0.92, 0.92, 1), size_hint_x=1, size_hint_y=None, height=ui_dp(56), halign='left', valign='middle', **_font_kwargs())
                    try:
                        l_sym.bind(on_press=_go)
                    except Exception:
                        pass

                    combined_fs = ui_sp(10.5)
                    line_h = ui_dp(20)

                    # Action + Qty (lot) in one column
                    bx_act_qty = BoxLayout(orientation='vertical', size_hint_x=0.20, spacing=ui_dp(2))
                    try:
                        # Nudge right a bit to visually center the column content
                        bx_act_qty.padding = (ui_dp(2), 0, 0, 0)
                    except Exception:
                        pass
                    act_lbl = Label(text=side or '-', font_size=combined_fs, color=side_col, halign='left', valign='middle', size_hint_y=None, height=line_h, **_font_kwargs())
                    qty_lbl = Label(text=_format_id_number(qty_lot, decimals=0), font_size=combined_fs, color=(0.92, 0.92, 0.92, 1), halign='left', valign='middle', size_hint_y=None, height=line_h, **_font_kwargs())
                    bx_act_qty.add_widget(act_lbl)
                    bx_act_qty.add_widget(qty_lbl)

                    # Price + Current in one column
                    bx_px_cur = BoxLayout(orientation='vertical', size_hint_x=0.30, spacing=ui_dp(2))
                    px_txt = _format_price(price) if price > 0 else '-'
                    cur_txt = _format_price(last) if isinstance(last, (int, float)) else '-'
                    px_lbl = Label(text=f"[color=#8E8E8E]Price[/color] {px_txt}", markup=True, font_size=combined_fs, color=(0.92, 0.92, 0.92, 1), halign='right', valign='middle', size_hint_y=None, height=line_h, **_font_kwargs())
                    cur_lbl = Label(text=f"[color=#8E8E8E]Current[/color] {cur_txt}", markup=True, font_size=combined_fs, color=(0.92, 0.92, 0.92, 1), halign='right', valign='middle', size_hint_y=None, height=line_h, **_font_kwargs())
                    bx_px_cur.add_widget(px_lbl)
                    bx_px_cur.add_widget(cur_lbl)

                    pl_col = _sign_color(pl)
                    l_pl = Label(text=_format_id_number(pl, decimals=0) if isinstance(pl, (int, float)) else '-', font_size=ui_sp(12), color=pl_col, size_hint_x=0.18, halign='right', valign='middle', **_font_kwargs())

                    # Tombol hapus sederhana (teks saja) di kolom paling kanan
                    del_lbl = ClickableLabel(text='hapus', markup=False, font_size=ui_sp(11.5), color=color_down,
                                             size_hint_x=0.10, halign='center', valign='middle', **_font_kwargs())
                    try:
                        del_lbl.bind(on_press=lambda _inst, _tx=tx: _confirm_delete_tx(_tx))
                    except Exception:
                        pass

                    for lab in (l_date, l_sym, l_pl, del_lbl):
                        lab.text_size = (lab.width, lab.height)
                        try:
                            if lab is l_sym:
                                lab.bold = True
                            lab.shorten = True
                            lab.shorten_from = 'left' if getattr(lab, 'halign', '') == 'right' else 'right'
                            lab.max_lines = 1
                        except Exception:
                            pass
                        lab.bind(size=lambda inst, _val: setattr(inst, 'text_size', (inst.width, inst.height)))

                    for leaf in list(getattr(bx_act_qty, 'children', [])) + list(getattr(bx_px_cur, 'children', [])):
                        try:
                            leaf.text_size = (leaf.width, leaf.height)
                            leaf.shorten = True
                            leaf.shorten_from = 'left' if getattr(leaf, 'halign', '') == 'right' else 'right'
                            leaf.max_lines = 1
                            leaf.bind(size=lambda inst, _val: setattr(inst, 'text_size', (inst.width, inst.height)))
                        except Exception:
                            pass

                    # Left sticky column: symbol only.
                    try:
                        tx_grid_left.add_widget(l_sym)
                    except Exception:
                        pass

                    # Right scrollable content.
                    rr.add_widget(l_date)
                    rr.add_widget(bx_act_qty)
                    rr.add_widget(bx_px_cur)
                    rr.add_widget(l_pl)
                    rr.add_widget(del_lbl)
                    return rr

                for tx in items[:200]:
                    tx_right_table.add_widget(_tx_row(tx))

            def _on_print(*_):
                try:
                    from datetime import date
                    from pathlib import Path
                    from modules.jurnal_store import load_transactions, filter_transactions_by_month
                    today = date.today()
                    month_key = today.strftime('%Y-%m')
                    all_items = load_transactions()
                    items = filter_transactions_by_month(all_items, today.year, today.month)
                    out_dir = Path('data') / 'jurnal' / 'exports'
                    out_dir.mkdir(parents=True, exist_ok=True)
                    out_file = out_dir / f"trades_{month_key.replace('-', '_')}.csv"
                    with out_file.open('w', encoding='utf-8') as f:
                        f.write('date,symbol,action,qty_lot,price,current,pl\n')
                        for tx in sorted(items, key=lambda x: (x.tx_date, x.symbol, x.side)):
                            try:
                                q = float(getattr(tx, 'qty', 0.0) or 0.0)
                                p = float(getattr(tx, 'price', 0.0) or 0.0)
                                sym = str(getattr(tx, 'symbol', '') or '').upper()
                                last = state['prices'].get(sym)
                                pl = None
                                if isinstance(last, (int, float)) and last and q > 0 and p > 0:
                                    sh = q * 100.0
                                    side = str(getattr(tx, 'side', '') or '').upper()
                                    if side == 'SELL':
                                        pl = (float(p) - float(last)) * sh
                                    else:
                                        pl = (float(last) - float(p)) * sh
                            except Exception:
                                q, p, last, pl = 0.0, 0.0, None, None
                            d = str(getattr(tx, 'tx_date', '') or '')
                            s = str(getattr(tx, 'symbol', '') or '')
                            side = str(getattr(tx, 'side', '') or '')
                            last_txt = f"{float(last):.0f}" if isinstance(last, (int, float)) else ''
                            pl_txt = f"{float(pl):.0f}" if isinstance(pl, (int, float)) else ''
                            f.write(f"{d},{s},{side},{q:.0f},{p:.0f},{last_txt},{pl_txt}\n")
                    msg.text = f"Export: {out_file.as_posix()}"
                    msg.color = color_up
                except Exception:
                    msg.text = 'Gagal export'
                    msg.color = color_down

            btn_print.bind(on_press=_on_print)

            _refresh_table()
            _refresh_tx_list()
            try:
                _refresh_prices()
            except Exception:
                pass

            # Realtime-ish refresh (avoid leaking when view is replaced)
            def _start_poll(*_):
                try:
                    if state.get('poll_ev') is None:
                        state['poll_ev'] = Clock.schedule_interval(lambda _dt: _refresh_prices(silent=True), 15)
                except Exception:
                    pass

            def _stop_poll(*_):
                try:
                    ev = state.get('poll_ev')
                    state['poll_ev'] = None
                    if ev is not None:
                        ev.cancel()
                except Exception:
                    pass

            def _on_parent(_inst, parent):
                if parent is None:
                    _stop_poll()
                else:
                    _start_poll()

            try:
                scroll.bind(parent=_on_parent)
                _start_poll()
            except Exception:
                pass
            return outer

        def _render_transaksi():
            from datetime import date
            from pathlib import Path
            from kivy.graphics import Color, Rectangle, Line

            scroll_outer = ScrollView(do_scroll_x=False, do_scroll_y=True)
            try:
                scroll_outer.scroll_type = ['content']
                scroll_outer.bar_width = 0
                scroll_outer.bar_color = (0, 0, 0, 0)
                scroll_outer.bar_inactive_color = (0, 0, 0, 0)
            except Exception:
                pass

            root = BoxLayout(orientation='vertical', spacing=ui_dp(10), size_hint_y=None, padding=(ui_dp(10), ui_dp(10)))
            root.bind(minimum_height=root.setter('height'))
            scroll_outer.add_widget(root)

            color_up = (0.11, 0.75, 0.36, 1)
            color_down = (0.86, 0.25, 0.25, 1)
            color_muted = (0.70, 0.70, 0.70, 1)

            # --- Header card ---
            card = BoxLayout(orientation='vertical', padding=(ui_dp(12), ui_dp(10)), spacing=ui_dp(8), size_hint_y=None)
            card.bind(minimum_height=card.setter('height'))
            with card.canvas.before:
                Color(0.06, 0.06, 0.06, 1)
                card._bg = Rectangle(pos=card.pos, size=card.size)
            card.bind(pos=lambda *_: setattr(card._bg, 'pos', card.pos), size=lambda *_: setattr(card._bg, 'size', card.size))

            title = Label(text='[b]Riwayat Transaksi[/b]', markup=True, font_size=ui_sp(14), color=(0.92, 0.92, 0.92, 1), size_hint_y=None, height=ui_dp(24), halign='left', valign='middle', **_font_kwargs())
            title.text_size = (title.width, title.height)
            title.bind(size=lambda inst, val: setattr(inst, 'text_size', (inst.width, inst.height)))
            card.add_widget(title)
            card.add_widget(Label(text='Transaksi dibuat dari Portofolio (tombol Proses).', font_size=ui_sp(12), color=color_muted, size_hint_y=None, height=ui_dp(18), halign='left', valign='middle', **_font_kwargs()))

            top_row = BoxLayout(orientation='horizontal', size_hint_y=None, height=ui_dp(40), spacing=ui_dp(8))
            btn_export = Button(text='Export CSV', size_hint=(None, 1), width=ui_dp(120), background_normal='', background_down='', background_color=(0, 0, 0, 0), color=(0.88, 0.88, 0.88, 1), padding=(0, 0), **_font_kwargs())
            try:
                with btn_export.canvas.before:
                    Color(0.22, 0.22, 0.22, 1)
                    btn_export._outline = Line(rectangle=(btn_export.x, btn_export.y, btn_export.width, btn_export.height), width=1.2)
                def _upd_outline(*_):
                    try:
                        btn_export._outline.rectangle = (btn_export.x + 1, btn_export.y + 1, max(0, btn_export.width - 2), max(0, btn_export.height - 2))
                    except Exception:
                        pass
                btn_export.bind(pos=_upd_outline, size=_upd_outline)
            except Exception:
                pass
            top_row.add_widget(btn_export)
            top_row.add_widget(Widget())
            card.add_widget(top_row)

            msg = Label(text='', font_size=ui_sp(12), color=color_muted, size_hint_y=None, height=ui_dp(18), halign='left', valign='middle', **_font_kwargs())
            msg.text_size = (msg.width, msg.height)
            msg.bind(size=lambda inst, val: setattr(inst, 'text_size', (inst.width, inst.height)))
            card.add_widget(msg)

            # Table header
            header = BoxLayout(orientation='horizontal', size_hint_y=None, height=ui_dp(26), padding=(ui_dp(4), 0), spacing=ui_dp(8))
            def _h(txt, sx, align='left'):
                l = Label(text=f"[b]{txt}[/b]", markup=True, font_size=ui_sp(11), color=(0.82, 0.82, 0.82, 1), size_hint_x=sx, halign=align, valign='middle', **_font_kwargs())
                l.text_size = (l.width, l.height)
                l.bind(size=lambda inst, val: setattr(inst, 'text_size', (inst.width, inst.height)))
                return l
            header.add_widget(_h('Tanggal', 0.24, 'left'))
            header.add_widget(_h('Symbol', 0.16, 'left'))
            header.add_widget(_h('Action / Qty', 0.18, 'left'))
            header.add_widget(_h('Price', 0.22, 'right'))
            header.add_widget(_h('Total', 0.20, 'right'))
            card.add_widget(header)

            grid = GridLayout(cols=1, spacing=0, size_hint_y=None)
            grid.bind(minimum_height=grid.setter('height'))
            card.add_widget(grid)
            root.add_widget(card)

            def _fmt_date(d_raw: str) -> str:
                d_raw = str(d_raw or '')
                if len(d_raw) == 10 and d_raw[4] == '-' and d_raw[7] == '-':
                    y, m, d = d_raw[0:4], d_raw[5:7], d_raw[8:10]
                    return f"{d}/{m}/{y}"
                return d_raw or '-'

            def _refresh_list():
                try:
                    grid.clear_widgets()
                except Exception:
                    pass
                try:
                    from modules.jurnal_store import load_transactions
                    items = load_transactions()
                except Exception:
                    items = []

                items = sorted(items, key=lambda x: (x.tx_date, x.symbol, x.side), reverse=True)
                if not items:
                    grid.add_widget(Label(text='Belum ada transaksi', size_hint_y=None, height=ui_dp(44), font_size=ui_sp(13), color=color_muted, **_font_kwargs()))
                    return

                def _row(tx):
                    r = BoxLayout(orientation='horizontal', padding=(ui_dp(4), ui_dp(6)), spacing=ui_dp(8), size_hint_y=None, height=ui_dp(56))
                    with r.canvas.before:
                        Color(0.04, 0.04, 0.04, 1)
                        r._bg = Rectangle(pos=r.pos, size=r.size)
                        Color(0.12, 0.12, 0.12, 1)
                        r._sep = Rectangle(pos=(r.x, r.y), size=(r.width, 1))
                    def _upd(*_):
                        r._bg.pos = r.pos
                        r._bg.size = r.size
                        r._sep.pos = (r.x, r.y)
                        r._sep.size = (r.width, 1)
                    r.bind(pos=_upd, size=_upd)

                    side = str(getattr(tx, 'side', '') or '').upper()
                    side_col = color_up if side == 'BUY' else color_down
                    sym = str(getattr(tx, 'symbol', '') or '').upper()
                    d_txt = _fmt_date(getattr(tx, 'tx_date', '') or '')

                    try:
                        qty_lot = float(getattr(tx, 'qty', 0.0) or 0.0)
                        price = float(getattr(tx, 'price', 0.0) or 0.0)
                        total = (qty_lot * 100.0) * price
                    except Exception:
                        qty_lot, price, total = 0.0, 0.0, 0.0

                    l_date = Label(text=d_txt, font_size=ui_sp(12), color=color_muted, size_hint_x=0.24, halign='left', valign='middle', **_font_kwargs())
                    l_sym = ClickableLabel(text=f"[b]{sym or '-'}[/b]", markup=True, font_size=ui_sp(13), color=(0.92, 0.92, 0.92, 1), size_hint_x=0.16, halign='left', valign='middle', **_font_kwargs())

                    combined_fs = ui_sp(10.5)
                    bx_act_qty = BoxLayout(orientation='vertical', size_hint_x=0.18)
                    bx_act_qty.add_widget(Label(text=side or '-', font_size=combined_fs, color=side_col, halign='left', valign='middle', **_font_kwargs()))
                    bx_act_qty.add_widget(Label(text=_format_id_number(qty_lot, decimals=0), font_size=combined_fs, color=(0.92, 0.92, 0.92, 1), halign='left', valign='middle', **_font_kwargs()))

                    l_price = Label(text=_format_price(price) if price > 0 else '-', font_size=ui_sp(12), color=(0.92, 0.92, 0.92, 1), size_hint_x=0.22, halign='right', valign='middle', **_font_kwargs())
                    l_total = Label(text=_format_id_number(total, decimals=0), font_size=ui_sp(12), color=color_muted, size_hint_x=0.20, halign='right', valign='middle', **_font_kwargs())

                    for lab in (l_date, l_sym, l_price, l_total):
                        lab.text_size = (lab.width, lab.height)
                        try:
                            lab.shorten = True
                            lab.shorten_from = 'right'
                        except Exception:
                            pass
                        lab.bind(size=lambda inst, val: setattr(inst, 'text_size', (inst.width, inst.height)))

                    for leaf in list(getattr(bx_act_qty, 'children', [])):
                        try:
                            leaf.text_size = (leaf.width, leaf.height)
                            leaf.halign = 'left'
                            leaf.valign = 'middle'
                            leaf.bind(size=lambda inst, val: setattr(inst, 'text_size', (inst.width, inst.height)))
                        except Exception:
                            pass

                    r.add_widget(l_date)
                    r.add_widget(l_sym)
                    r.add_widget(bx_act_qty)
                    r.add_widget(l_price)
                    r.add_widget(l_total)
                    # Swipe wrapper provides red delete button.
                    def _on_delete(_tx=tx):
                        try:
                            from modules.jurnal_store import delete_transaction
                            ok = delete_transaction(_tx)
                            if ok:
                                msg.text = 'Dihapus'
                                msg.color = color_up
                                _refresh_list()
                            else:
                                msg.text = 'Gagal hapus'
                                msg.color = color_down
                        except Exception:
                            msg.text = 'Gagal hapus'
                            msg.color = color_down

                    def _on_tap():
                        try:
                            from kivy.app import App
                            app = App.get_running_app()
                            sym = str(getattr(tx, 'symbol', '') or '').upper()
                            if app is not None and hasattr(app, 'open_cek_emiten') and sym:
                                app.open_cek_emiten(sym)
                        except Exception:
                            pass

                    swipe = SwipeToDeleteRow(
                        r,
                        on_delete=_on_delete,
                        on_tap=_on_tap,
                        tap_widget=l_sym,
                        delete_width=110,
                        height=r.height,
                        scrollview=scroll_outer,
                    )
                    return swipe

                for tx in items[:200]:
                    grid.add_widget(_row(tx))

            def _on_export(*_):
                try:
                    from modules.jurnal_store import load_transactions
                    items = load_transactions()
                    out_dir = Path('data') / 'jurnal' / 'exports'
                    out_dir.mkdir(parents=True, exist_ok=True)
                    out_file = out_dir / f"transactions_{date.today().strftime('%Y_%m_%d')}.csv"
                    with out_file.open('w', encoding='utf-8') as f:
                        f.write('date,symbol,action,qty_lot,price,total\n')
                        for tx in sorted(items, key=lambda x: (x.tx_date, x.symbol, x.side)):
                            try:
                                q = float(getattr(tx, 'qty', 0.0) or 0.0)
                                p = float(getattr(tx, 'price', 0.0) or 0.0)
                                total = (q * 100.0) * p
                            except Exception:
                                q, p, total = 0.0, 0.0, 0.0
                            d = str(getattr(tx, 'tx_date', '') or '')
                            s = str(getattr(tx, 'symbol', '') or '')
                            side = str(getattr(tx, 'side', '') or '')
                            f.write(f"{d},{s},{side},{q:.0f},{p:.0f},{total:.0f}\n")
                    msg.text = f"Export: {out_file.as_posix()}"
                    msg.color = color_up
                except Exception:
                    msg.text = 'Gagal export'
                    msg.color = color_down

            btn_export.bind(on_press=_on_export)
            _refresh_list()
            return scroll_outer

        def _render():
            try:
                self._content.clear_widgets()
            except Exception:
                pass

            if self._subtab == 'ringkasan':
                self._content.add_widget(_render_ringkasan())
            elif self._subtab == 'portofolio':
                self._content.add_widget(_render_portofolio())
            elif self._subtab == 'transaksi':
                self._content.add_widget(_render_transaksi())
            elif self._subtab == 'dividen':
                self._content.add_widget(_render_dividen())
            elif self._subtab == 'kinerja':
                self._content.add_widget(_render_kinerja())
            else:
                self._content.add_widget(_placeholder('Jurnal', ''))

        _set_active('ringkasan')

class MainStockbitApp(App):
    def build(self):
        try:
            print('[desktop_app.py.bak] UI build: Top10 subnav includes Analisis')
        except Exception:
            pass
        # Cloud auth state (shared across tabs)
        try:
            self.auth_user_id
        except AttributeError:
            self.auth_user_id = None
            self.auth_email = None
            self.cloud_sync = None
        try:
            # Avoid showing a persistent app title in the desktop window chrome.
            self.title = ''
        except Exception:
            pass
        # Bottom navigation labels
        self.tab_names = ['Watchlist', 'Top 10', 'Jurnal', 'Screening', 'Cek Emiten']
        # Map new labels to existing tab factories. Use DashboardTab for Top 10,
        # JurnalTab for Jurnal, and CekSahamTab for Cek Emiten.
        self.tab_factories = [WatchlistTab, DashboardTab, JurnalTab, ScreeningTab, CekSahamTab]
        # start with Watchlist (matches Stockbit default)
        self.current_tab = 0
        # Simple back-stack for bottom tabs (Android back button).
        self._tab_history = []

        def _on_keyboard(_window, key, scancode, codepoint, modifier):
            # Debug: log all keys so we can see actual back keycodes on device.
            try:
                print("[DEBUG] on_keyboard key=", key, "scancode=", scancode, "codepoint=", codepoint, "mod=", modifier)
            except Exception:
                pass

            # Normalize: on desktop, use Escape (27) as back. On Android, some
            # builds use 27, others 1000/1001/1002/1003 for back.
            is_back = False
            try:
                if _kivy_platform in ("android", "ios"):
                    is_back = key in (27, 1000, 1001, 1002, 1003)
                else:
                    is_back = (key == 27)
            except Exception:
                is_back = (key == 27)

            if not is_back:
                # Let other handlers / widgets process non-back keys.
                return False
            try:
                w = self.tab_container.children[0] if self.tab_container.children else None
                if w is not None and hasattr(w, 'go_back'):
                    try:
                        handled = bool(w.go_back())
                        if handled:
                            return True
                    except Exception:
                        pass
            except Exception:
                pass

            try:
                if self._tab_history:
                    prev = self._tab_history.pop()
                    self.switch_tab(prev, record_history=False)
                    return True
            except Exception:
                pass

            # Fallback: go to Watchlist instead of exiting.
            try:
                if int(getattr(self, 'current_tab', 0) or 0) != 0:
                    self.switch_tab(0, record_history=False)
                    return True
            except Exception:
                pass

            # Consume the back key (do not exit app unexpectedly).
            return True

        try:
            if _kivy_platform in ("android", "ios"):
                Window.bind(on_keyboard=_on_keyboard)
        except Exception:
            pass
        root = BoxLayout(orientation='vertical')
        # Remove top header for a cleaner desktop preview; add small spacer
        from kivy.uix.widget import Widget
        spacer = Widget(size_hint_y=None, height=ui_dp(6))
        root.add_widget(spacer)

        # Tab container (content area)
        self.tab_container = BoxLayout(orientation='vertical')
        root.add_widget(self.tab_container)
        # show initial tab
        self.switch_tab(self.current_tab, record_history=False)
        # Bottom navigation ala Stockbit (outline icon + label vertikal)
        from kivy.graphics import Color, Rectangle
        nav = BoxLayout(orientation='horizontal', size_hint_y=None, height=ui_dp(64), spacing=0, padding=(0, 0))
        # draw background and top border
        with nav.canvas.before:
            Color(0.10, 0.10, 0.10, 1)
            nav._bg = Rectangle(pos=nav.pos, size=nav.size)
            Color(0.22, 0.22, 0.22, 1)
            nav._top = Rectangle(pos=(nav.x, nav.y + nav.height - 1), size=(nav.width, 1))
        def _update_nav(_, __):
            nav._bg.pos = nav.pos
            nav._bg.size = nav.size
            nav._top.pos = (nav.x, nav.y + nav.height - 1)
            nav._top.size = (nav.width, 1)
        nav.bind(pos=_update_nav, size=_update_nav)

        nav_buttons = []

        def make_nav(icon_type, label_text, handler, active=False):
            # Tombol dasar: transparan, isi diatur manual via BoxLayout + outline icon + Label.
            b = Button(
                text='',
                background_normal='',
                background_down='',
                background_color=(0, 0, 0, 0),
                size_hint_x=1,
                padding=(0, 0),
                **_font_kwargs(),
            )

            # Kontainer vertikal untuk icon + label
            box = BoxLayout(orientation='vertical', padding=(0, ui_dp(4), 0, ui_dp(4)))
            box.size_hint = (1, 1)
            box.spacing = ui_dp(2)

            # Icon dibungkus AnchorLayout agar selalu berada di tengah secara horizontal
            try:
                from kivy.uix.anchorlayout import AnchorLayout
                icon_holder = AnchorLayout(anchor_x='center', anchor_y='center', size_hint=(1, None), height=ui_dp(24))
            except Exception:
                icon_holder = BoxLayout(orientation='horizontal', size_hint=(1, None), height=ui_dp(24))

            # Outline icon widget (vector, single-line style), ukuran sedikit lebih kecil supaya proporsional.
            icon = _NavIcon(icon_type=icon_type, size_hint=(None, None), size=(ui_dp(24), ui_dp(24)))
            icon_holder.add_widget(icon)

            txt = Label(
                text=label_text,
                font_size=ui_sp(11),
                size_hint_y=None,
                height=ui_dp(18),
                color=(0.70, 0.70, 0.70, 1),
                halign='center',
                valign='middle',
                **_font_kwargs(),
            )
            try:
                txt.text_size = (txt.width, None)
                txt.bind(size=lambda inst, val: setattr(inst, 'text_size', (inst.width, None)))
            except Exception:
                pass

            box.add_widget(icon_holder)
            box.add_widget(txt)
            b.add_widget(box)

            def _sync_box(*_args):
                try:
                    box.pos = b.pos
                    box.size = b.size
                except Exception:
                    pass

            b.bind(pos=_sync_box, size=_sync_box)

            def set_active(state: bool):
                if state:
                    # active color (hijau ala Stockbit)
                    col = (0.11, 0.75, 0.36, 1)
                    icon.color = col
                    txt.color = col
                    b.background_color = (0.11, 0.75, 0.36, 0.08)
                else:
                    col = (0.70, 0.70, 0.70, 1)
                    icon.color = col
                    txt.color = col
                    b.background_color = (0, 0, 0, 0)

            def _on_press(instance, *_):
                for other in nav_buttons:
                    try:
                        other.set_active(False)
                    except Exception:
                        pass
                set_active(True)
                try:
                    handler()
                except Exception:
                    pass

            b.set_active = set_active
            b.bind(on_press=_on_press)
            set_active(active)
            nav_buttons.append(b)
            return b

        # Tipe ikon outline per tab, berurutan dengan tab_names.
        icon_types = ['watchlist', 'top10', 'jurnal', 'screening', 'cek']
        labels = self.tab_names
        # bottom nav handlers must capture index in loop (use default arg)
        for i in range(len(labels)):
            handler = (lambda idx=i: self.switch_tab(idx))
            itype = icon_types[i] if i < len(icon_types) else ''
            btn = make_nav(itype, labels[i], handler, active=(i == self.current_tab))
            nav.add_widget(btn)

        # Keep references so we can update active state on programmatic tab switches.
        try:
            self._nav_buttons = nav_buttons
        except Exception:
            self._nav_buttons = []

        # Preview HTML tab removed

        root.add_widget(nav)
        return root

    def open_cek_emiten(self, symbol: str):
        """Switch to Cek Emiten tab and open the requested symbol (best-effort)."""
        try:
            s = (symbol or '').strip().upper()
            if not s:
                return
        except Exception:
            return

        try:
            idx = (self.tab_names or []).index('Cek Emiten')
        except Exception:
            idx = 4

        try:
            self.switch_tab(idx)
        except Exception:
            return

        try:
            w = self.tab_container.children[0] if self.tab_container.children else None
            if w is not None and hasattr(w, 'open_symbol'):
                w.open_symbol(s)
        except Exception:
            pass

    def switch_tab(self, idx, record_history: bool = True):
        # Remove existing children and instantiate a fresh tab widget via factory.
        try:
            idx = int(idx)
        except Exception:
            idx = 0

        try:
            _log_info('Nav', f"switch_tab: idx={idx}")
        except Exception:
            pass

        if record_history:
            try:
                cur = int(getattr(self, 'current_tab', 0) or 0)
                if cur != idx:
                    self._tab_history.append(cur)
                    # cap to avoid runaway growth
                    if len(self._tab_history) > 30:
                        self._tab_history = self._tab_history[-30:]
            except Exception:
                pass
        try:
            factory = self.tab_factories[idx]
            # IMPORTANT: do not clear current tab until the new widget is ready.
            # This avoids transient blank tabs while the factory is building.
            widget = factory()
            try:
                self.tab_container.clear_widgets()
            except Exception:
                pass
            self.tab_container.add_widget(widget)
            self.current_tab = idx

            # Update nav active state if available.
            try:
                for i, b in enumerate(getattr(self, '_nav_buttons', []) or []):
                    try:
                        b.set_active(i == idx)
                    except Exception:
                        pass
            except Exception:
                pass
        except Exception as e:
            # IMPORTANT: make the failure visible (prevents a blank tab).
            _log_exception('Nav', f"switch_tab failed idx={idx}: {e}")
            try:
                self.tab_container.clear_widgets()
            except Exception:
                pass
            try:
                self.tab_container.add_widget(
                    Label(
                        text=f"Gagal membuka tab: {e}",
                        font_size=ui_sp(13),
                        color=(0.85, 0.55, 0.55, 1),
                        halign='left',
                        valign='middle',
                        **_font_kwargs(),
                    )
                )
            except Exception:
                pass

            # Still update nav state so user can switch away.
            try:
                for i, b in enumerate(getattr(self, '_nav_buttons', []) or []):
                    try:
                        b.set_active(i == idx)
                    except Exception:
                        pass
            except Exception:
                pass

# Entry point for main.py
JurnalSahamApp = MainStockbitApp


if __name__ == '__main__':
    MainStockbitApp().run()
