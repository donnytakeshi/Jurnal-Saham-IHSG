# --- Jurnal Saham IHSG - Kivy Mobile App (FIXED for py_compile) ---

import json
import csv
import os
import threading
import traceback
import random
import sys
from datetime import datetime

# Kivy imports
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
from kivy.properties import ListProperty, NumericProperty, StringProperty
from kivy.event import EventDispatcher
from kivy.utils import get_color_from_hex, platform as _kivy_platform
from kivy.clock import Clock
from kivy.graphics import Color, Rectangle, RoundedRectangle, Line, Ellipse
from kivy.core.window import Window
from kivy.metrics import dp, sp
from kivy.animation import Animation
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.recycleview import RecycleView
from kivy.uix.recycleview.views import RecycleDataViewBehavior
from kivy.uix.recycleboxlayout import RecycleBoxLayout


# ============================================================================
# UI HELPERS
# ============================================================================
def ui_dp(v): 
    return dp(v)

def ui_sp(v): 
    return sp(v)

def _log_info(tag, msg):
    try:
        print(f"[INFO] {tag}: {msg}")
    except:
        pass

def _log_exception(tag, msg):
    try:
        print(f"[ERROR] {tag}: {msg}")
    except:
        pass

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
        fmt = f"{{:,.{decimals}f}}".format(n)
        result = fmt.replace(',', 'X').replace('.', ',').replace('X', '.')
        if decimals == 0:
            result = result.replace(',00', '')
        return result
    except Exception:
        return str(value)

def _format_price(value):
    if value in (None, '', '-'):
        return '-'
    n = _to_float(value, default=None)
    if n is None:
        return str(value)
    return _format_id_number(n, decimals=0)

def _format_change_pair(change_abs, change_pct):
    if change_abs in (None, '', '-') and change_pct in (None, '', '-'):
        return '-'
    ca = _to_float(change_abs, default=0.0)
    cp = _to_float(change_pct, default=0.0)
    sign = '+' if ca > 0 else ''
    abs_txt = _format_id_number(ca, decimals=0)
    pct_txt = _format_id_number(cp, decimals=2)
    return f"{sign}{abs_txt} ({sign if cp>0 else ''}{pct_txt}%)"

def _format_compact_number(value):
    if value in (None, '', '-'):
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
    try:
        if now is None:
            now = datetime.now()
        if now.weekday() >= 5:
            return False
        h = now.hour + (now.minute / 60.0)
        return 9.0 <= h <= 16.0
    except Exception:
        return False

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

def _autosize_button_to_text(btn, extra_w=0):
    try:
        btn.texture_update()
        btn.width = btn.texture_size[0] + extra_w
    except:
        pass

def _make_styled_popup(content, title="", size_hint=(0.9, None), height=400, auto_dismiss=True):
    popup = Popup(title=title, content=content, size_hint=size_hint, auto_dismiss=auto_dismiss)
    if height:
        popup.height = height
    return popup


# ============================================================================
# THEME CONFIG
# ============================================================================
class ThemeConfig:
    SPARKLINE = [0.11, 0.75, 0.36, 1]
    BG_CARD = get_color_from_hex('#181c21')
    BG_MAIN = get_color_from_hex('#101419')
    SURFACE = get_color_from_hex('#181c21')
    SURFACE_LIGHT = get_color_from_hex('#1c2127')
    ACCENT = get_color_from_hex('#159D91')
    GREEN = get_color_from_hex('#67d9cb')
    RED = get_color_from_hex('#ff5e5e')
    YELLOW = get_color_from_hex('#f2d18f')
    BORDER = get_color_from_hex('#2d3432')
    TEXT_BRIGHT = get_color_from_hex('#ffffff')
    TEXT_DEFAULT = get_color_from_hex('#bcc9c6')
    TEXT_MUTED = get_color_from_hex('#41493e')
    ROUNDNESS = 12
    FONT_HEADER = 18
    TEXT_HEADER = get_color_from_hex('#ffffff')
    BG_NAV = get_color_from_hex('#181c21')
    BG_NAV_LINE = get_color_from_hex('#23272c')
    BUTTON_BG = get_color_from_hex('#23272c')
    FONT_NAV = 15
    TEXT_ACTIVE = get_color_from_hex('#67d9cb')
    BG_HEADER = get_color_from_hex('#181c21')
    RADIUS_CARD = 12
    BG_CHART = get_color_from_hex('#0F1419')
    FONT_SIGNAL = 16
    TEXT_SIGNAL = get_color_from_hex('#67d9cb')
    RADIUS_BTN = 8
    TEXT_BUTTON = get_color_from_hex('#ffffff')
    DELETE_BTN_BG = get_color_from_hex('#8B0000')
    TEXT_DELETE = get_color_from_hex('#ffffff')


# ============================================================================
# MOCK DATA FETCHER (Replace with your real modules)
# ============================================================================
class DataFetcher:
    sample_stocks = [
        {'symbol': 'BBRI', 'company_name': 'Bank Rakyat Indonesia'},
        {'symbol': 'ASII', 'company_name': 'Astra International'},
        {'symbol': 'BBNI', 'company_name': 'Bank Negara Indonesia'},
        {'symbol': 'GOTO', 'company_name': 'Goto Gojek Tokopedia'},
        {'symbol': 'UNVR', 'company_name': 'Unilever Indonesia'},
    ]


# ============================================================================
# CUSTOM WIDGETS
# ============================================================================
class ClickableBehavior(ButtonBehavior):
    pass

class ClickableLabel(ClickableBehavior, Label):
    pass

class ClickableRow(ClickableBehavior, BoxLayout):
    pass

class SparklineWidget(Widget):
    values = ListProperty([])
    line_color = ListProperty([0.11, 0.75, 0.36, 1])

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.bind(pos=self._redraw, size=self._redraw, values=self._redraw, line_color=self._redraw)

    def _redraw(self, *args):
        self.canvas.clear()
        if not self.values or len(self.values) < 2:
            return
        try:
            w = max(1.0, float(self.width))
            h = max(1.0, float(self.height))
            pad = ui_dp(2)
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
                Line(points=xs, width=ui_dp(1.2), cap='round', joint='round')
        except Exception:
            return

class _NavIcon(Widget):
    icon_type = ''
    color = ListProperty(ThemeConfig.TEXT_DEFAULT)

    def __init__(self, icon_type='', **kwargs):
        super().__init__(**kwargs)
        self.icon_type = str(icon_type or '').strip().lower()
        self.bind(pos=self._redraw, size=self._redraw, color=self._redraw)

    def _redraw(self, *args):
        self.canvas.clear()
        w = max(1.0, float(self.width))
        h = max(1.0, float(self.height))
        pad = ui_dp(2)
        cx = self.x + w / 2.0
        cy = self.y + h / 2.0
        col = list(self.color or [0.70, 0.70, 0.70, 1])
        t = ui_dp(1.7)
        with self.canvas:
            Color(*col)
            it = self.icon_type
            if it == 'watchlist':
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
                base_y = self.y + pad
                x0 = self.x + pad
                step = (w - pad * 2) / 4.0
                Line(points=[x0, base_y, x0, base_y + h * 0.35], width=t)
                Line(points=[x0 + step, base_y, x0 + step, base_y + h * 0.55], width=t)
                Line(points=[x0 + 2 * step, base_y, x0 + 2 * step, base_y + h * 0.80], width=t)
                ax = x0 + 2 * step
                ay = base_y + h * 0.80
                Line(points=[ax, ay, ax + ui_dp(4), ay + ui_dp(6)], width=t)
                Line(points=[ax, ay, ax - ui_dp(4), ay + ui_dp(6)], width=t)
            elif it == 'jurnal':
                rw = w - pad * 2
                rh = h - pad * 2
                Line(rounded_rectangle=(self.x + pad, self.y + pad, rw, rh, ui_dp(3)), width=t)
                Line(points=[self.x + pad + rw * 0.22, self.y + pad + rh * 0.72, self.x + pad + rw * 0.78, self.y + pad + rh * 0.72], width=t)
            elif it == 'screening':
                r = min(w, h) * 0.32
                Ellipse(pos=(cx - r, cy - r), size=(2 * r, 2 * r))
                hx1 = cx + r * 0.6
                hy1 = cy - r * 0.1
                hx2 = hx1 + ui_dp(6)
                hy2 = hy1 - ui_dp(6)
                Line(points=[hx1, hy1, hx2, hy2], width=t)
            elif it == 'cek':
                bw = w * 0.55
                bh = h * 0.60
                bx = cx - bw / 2.0
                by = cy - bh / 2.0
                Line(rectangle=(bx, by, bw, bh), width=t)
                wx = bx + bw * 0.25
                wy = by + bh * 0.65
                s = ui_dp(2.2)
                Ellipse(pos=(wx - s / 2.0, wy - s / 2.0), size=(s, s))
                Ellipse(pos=(wx + bw * 0.3 - s / 2.0, wy - s / 2.0), size=(s, s))
                Ellipse(pos=(wx - s / 2.0, wy - bh * 0.35 - s / 2.0), size=(s, s))
                Ellipse(pos=(wx + bw * 0.3 - s / 2.0, wy - bh * 0.35 - s / 2.0), size=(s, s))
                Line(points=[bx - ui_dp(2), by - ui_dp(2), bx + bw + ui_dp(2), by - ui_dp(2)], width=t)
            else:
                r = min(w, h) * 0.35
                Ellipse(pos=(cx - r, cy - r), size=(2 * r, 2 * r))

class SwipeToDeleteRow(Widget):
    dx = NumericProperty(0)

    def __init__(self, content, on_delete=None, on_tap=None, delete_width=110, scrollview=None, tap_widget=None, tap_filter=None, **kwargs):
        super().__init__(**kwargs)
        try:
            self._is_android = (str(_kivy_platform).lower() == 'android')
        except:
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
        self._mode = None
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
            padding=(0, 0)
        )
        self._root.add_widget(self._delete_btn)
        self._content = content
        self._content.size_hint = (None, None)
        self._content.height = self.height
        self._root.add_widget(self._content)

        def _sync_layout(*_args):
            self._root.pos = self.pos
            self._root.size = self.size
            pad_x = ui_dp(4)
            self._delete_btn.height = self.height
            self._delete_btn.x = self.x + self.width - self._delete_width
            self._delete_btn.y = self.y
            content_w = max(0, self.width - pad_x * 2)
            self._content.size = (content_w, self.height)
            self._content.pos = (self.x + pad_x + self.dx, self.y)
            try:
                if self._is_android:
                    self._delete_btn.disabled = True
                    self._delete_btn.opacity = 0.0
                    self._delete_btn.width = 0
                else:
                    open_enough = (self.dx <= -self._delete_width * 0.8)
                    self._delete_btn.disabled = not open_enough
                    self._delete_btn.opacity = 1.0 if open_enough else 0.0
            except:
                pass

        self.bind(pos=_sync_layout, size=_sync_layout, dx=_sync_layout)
        _sync_layout()

        def _do_delete(_instance):
            if callable(self._on_delete):
                try:
                    self._on_delete()
                except:
                    pass
        self._delete_btn.bind(on_press=_do_delete)

    def on_touch_down(self, touch):
        if getattr(self, '_is_android', False):
            return super().on_touch_down(touch)
        if not self.collide_point(*touch.pos):
            return super().on_touch_down(touch)
        try:
            if self._delete_btn.collide_point(*touch.pos) and (self.dx <= -self._delete_width * 0.8):
                return super().on_touch_down(touch)
        except:
            pass
        self._touch_start = (touch.x, touch.y)
        self._start_dx = self.dx
        try:
            self._start_scroll_y = self._scrollview.scroll_y if self._scrollview is not None else None
        except:
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
                new_scroll_y = float(self._start_scroll_y) + (dy / scroll_range)
                if new_scroll_y < 0:
                    new_scroll_y = 0
                if new_scroll_y > 1:
                    new_scroll_y = 1
                self._scrollview.scroll_y = new_scroll_y
            except:
                pass
            return True
        return True

    def on_touch_up(self, touch):
        if getattr(self, '_is_android', False):
            return super().on_touch_up(touch)
        if touch.grab_current is not self:
            return super().on_touch_up(touch)
        touch.ungrab(self)
        try:
            start_x, start_y = self._touch_start or (None, None)
            if start_x is not None and start_y is not None:
                dx = float(touch.x - start_x)
                dy = float(touch.y - start_y)
                thresh = ui_dp(10)
                if abs(dx) < thresh and abs(dy) < thresh:
                    if self.dx < 0:
                        self.dx = 0
                    else:
                        allow = True
                        try:
                            if callable(self._tap_filter):
                                allow = bool(self._tap_filter(touch))
                            elif self._tap_widget is not None:
                                allow = bool(self._tap_widget.collide_point(*touch.pos))
                        except:
                            allow = True
                        if allow and callable(self._on_tap):
                            try:
                                self._on_tap()
                            except:
                                pass
        except:
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

class PullToRefreshScrollView(ScrollView):
    def __init__(self, indicator_box, indicator_lbl, on_refresh=None, **kwargs):
        super().__init__(**kwargs)
        self._indicator_box = indicator_box
        self._indicator_label = indicator_lbl
        self._on_refresh = on_refresh
        self._down_y = None
        self._pull = 0
        self._trigger = ui_dp(50)
        self._armed = False
        self._pulling = False
        self._start_at_top = False

    def _reset_pull(self):
        self._pull = 0
        self._armed = False
        self._pulling = False
        self._set_indicator(0, 'Tarik untuk refresh')

    def _set_indicator(self, h, text=None):
        try:
            self._indicator_box.height = max(0, h)
            if text is not None:
                self._indicator_label.text = text
        except:
            pass

    def on_touch_down(self, touch):
        if not self.collide_point(*touch.pos):
            return super().on_touch_down(touch)
        self._down_y = touch.y
        self._pull = 0
        self._armed = False
        self._pulling = False
        self._start_at_top = bool(self.scroll_y >= 0.999)
        return super().on_touch_down(touch)

    def on_touch_move(self, touch):
        if not self.collide_point(*touch.pos):
            return super().on_touch_move(touch)
        if self._down_y is None:
            return super().on_touch_move(touch)
        dy = self._down_y - touch.y
        at_top = bool(self.scroll_y >= 0.999)
        if (not self._start_at_top) or (not at_top) or (dy <= 0):
            if self._pulling or self._pull > 0:
                self._reset_pull()
            return super().on_touch_move(touch)
        if dy <= self._trigger:
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
                except:
                    pass
            Clock.schedule_once(lambda dt: self._set_indicator(0, 'Tarik untuk refresh'), 0.6)
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


# ============================================================================
# WATCHLIST TAB
# ============================================================================
class WatchlistTab(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(orientation='vertical', **kwargs)
        self.data_fetcher = DataFetcher()
        self._watchlist_file = os.path.join(os.path.dirname(__file__), 'data', 'watchlist.json')
        self.watchlist = ['BBRI', 'ASII', 'BBNI', 'GOTO', 'UNVR']
        self._prev_price = {}
        
        # Header
        header = BoxLayout(size_hint_y=None, height=ui_dp(60), padding=ui_dp(10))
        header.add_widget(Label(text='[b]Watchlist[/b]', markup=True, font_size=ui_sp(ThemeConfig.FONT_HEADER), color=ThemeConfig.TEXT_HEADER))
        self.add_widget(header)
        
        # List
        scroll = ScrollView()
        self.list = GridLayout(cols=1, size_hint_y=None, spacing=ui_dp(1))
        self.list.bind(minimum_height=self.list.setter('height'))
        
        for s in self.data_fetcher.sample_stocks:
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


# ============================================================================
# DASHBOARD TAB (Top 10)
# ============================================================================
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


# ============================================================================
# JURNAL TAB
# ============================================================================
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


# ============================================================================
# SCREENING TAB
# ============================================================================
class ScreeningRowView(RecycleDataViewBehavior, BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'horizontal'
        self.size_hint_y = None
        self.height = ui_dp(54)

    def refresh_view_attrs(self, rv, index, data):
        self.clear_widgets()
        if not data:
            return
        # Simplified row rendering
        self.add_widget(Label(text=data.get('symbol', '-'), size_hint_x=0.2))
        self.add_widget(Label(text=str(data.get('price', '-')), size_hint_x=0.2))
        self.add_widget(Label(text=str(data.get('change', '-')), size_hint_x=0.2))
        self.add_widget(Label(text=str(data.get('volume', '-')), size_hint_x=0.2))

class ScreeningTab(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(orientation='vertical', **kwargs)
        self.add_widget(Label(text='[b]Live Screening[/b]', markup=True, size_hint_y=None, height=ui_dp(60), font_size=ui_sp(ThemeConfig.FONT_HEADER), color=ThemeConfig.TEXT_HEADER))
        scroll = ScrollView()
        table = GridLayout(cols=4, size_hint_y=None, spacing=ui_dp(2))
        table.bind(minimum_height=table.setter('height'))
        headers = ['SAHAM', 'HARGA', '%', 'NET B/S']
        for h in headers:
            table.add_widget(Label(text=h, bold=True, size_hint_y=None, height=ui_dp(40), color=ThemeConfig.TEXT_HEADER))
        for s in DataFetcher.sample_stocks * 3:
            table.add_widget(Label(text=s['symbol'], size_hint_y=None, height=ui_dp(40), color=ThemeConfig.TEXT_DEFAULT))
            table.add_widget(Label(text='10.250', color=ThemeConfig.TEXT_DEFAULT))
            table.add_widget(Label(text='+2.5%', color=ThemeConfig.TEXT_DEFAULT))
            table.add_widget(Label(text='+124B', color=ThemeConfig.TEXT_DEFAULT))
        scroll.add_widget(table)
        self.add_widget(scroll)


# ============================================================================
# CEK SAHAM TAB
# ============================================================================
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


# ============================================================================
# MAIN APP
# ============================================================================
class MainStockbitApp(App):
    def build(self):
        Window.clearcolor = ThemeConfig.BG_MAIN
        
        # Set window size for desktop preview (NOT for Android)
        if _kivy_platform not in ("android", "ios"):
            try:
                Window.size = (360, 800)
            except:
                pass
        
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

    def open_cek_emiten(self, symbol: str):
        try:
            s = (symbol or '').strip().upper()
            if not s:
                return
        except:
            return
        try:
            idx = 4
            self.switch_tab(idx)
        except:
            return
        try:
            w = self.content_area.children[0] if self.content_area.children else None
            if w is not None and hasattr(w, 'open_symbol'):
                w.open_symbol(s)
        except:
            pass


# ============================================================================
# ENTRY POINT
# ============================================================================
if __name__ == '__main__':
    # Safety patch for EventDispatcher.bind
    _orig_event_bind = EventDispatcher.bind
    def _safe_event_bind(self, *args, **kwargs):
        try:
            return _orig_event_bind(self, *args, **kwargs)
        except AssertionError:
            try:
                filtered = {k: v for k, v in kwargs.items() if v is not None}
                return _orig_event_bind(self, **filtered)
            except Exception:
                return None
    try:
        EventDispatcher.bind = _safe_event_bind
    except Exception:
        try:
            Widget.bind = _safe_event_bind
        except Exception:
            pass
    
    # Run app
    try:
        MainStockbitApp().run()
    except Exception as e:
        traceback.print_exc()