# --- Jurnal Saham IHSG - PRO UNIFIED KIVY APP ---
# Includes: Equity Curve, Win/Loss Ratio, Technical Alerts UI, and Candlestick + Volume Chart.
# Design System: Quant Edge (Dark Mode & Teal)

import json
import random
from datetime import datetime

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.uix.widget import Widget
from kivy.uix.textinput import TextInput
from kivy.uix.behaviors import ButtonBehavior
from kivy.properties import ListProperty, NumericProperty, StringProperty
from kivy.utils import get_color_from_hex
from kivy.clock import Clock
from kivy.graphics import Color, Rectangle, RoundedRectangle, Line, Ellipse
from kivy.core.window import Window

# --- CONFIG & THEME (Quant Edge) ---
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

# --- UI HELPERS ---
def ui_dp(v):
    from kivy.metrics import dp
    return dp(v)

def ui_sp(v):
    from kivy.metrics import sp
    return sp(v)

def format_id(v):
    try:
        return "{:,.0f}".format(v).replace(',', '.')
    except: return str(v)

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
        self.height = ui_dp(22)
        self.padding = (ui_dp(10), ui_dp(4))
        with self.canvas.before:
            Color(rgb=bg_color)
            self.rect = RoundedRectangle(pos=self.pos, size=self.size, radius=[ui_dp(11)])
        self.bind(pos=self._update, size=self._update)
        self._update_width()

    def _update(self, *_):
        self.rect.pos = self.pos
        self.rect.size = self.size

    def _update_width(self, *_):
        self.texture_update()
        self.width = self.texture_size[0] + ui_dp(20)

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
            Line(points=points, width=ui_dp(1.8), cap='round', joint='round')

class ProgressBar(Widget):
    value = NumericProperty(0.5) # 0.0 to 1.0
    bg_color = ListProperty(ThemeConfig.RED)
    fill_color = ListProperty(ThemeConfig.GREEN)
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.size_hint_y = None
        self.height = ui_dp(8)
        self.bind(pos=self._draw, size=self._draw, value=self._draw)
    def _draw(self, *_):
        self.canvas.clear()
        with self.canvas:
            # Background
            Color(*self.bg_color)
            RoundedRectangle(pos=self.pos, size=self.size, radius=[ui_dp(4)])
            # Fill
            Color(*self.fill_color)
            RoundedRectangle(pos=self.pos, size=(self.width * self.value, self.height), radius=[ui_dp(4)])

class CandlestickVolumeChart(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(orientation='vertical', spacing=ui_dp(4), **kwargs)
        self.canvas_box = Widget(size_hint_y=0.7)
        self.volume_box = Widget(size_hint_y=0.3)
        self.add_widget(self.canvas_box)
        self.add_widget(self.volume_box)
        self.bind(pos=self._draw, size=self._draw)
        
    def _draw(self, *_):
        self.canvas_box.canvas.clear()
        self.volume_box.canvas.clear()
        # Mocking complex chart visual
        with self.canvas_box.canvas:
            Color(rgb=get_color_from_hex('#0F1419'))
            Rectangle(pos=self.canvas_box.pos, size=self.canvas_box.size)
            # Grid
            Color(0.2, 0.2, 0.2, 0.5)
            for i in range(1, 5):
                y = self.canvas_box.y + (self.canvas_box.height / 5) * i
                Line(points=[self.canvas_box.x, y, self.canvas_box.right, y], width=ui_dp(0.5))
            # Mock Candlesticks
            for i in range(15):
                cx = self.canvas_box.x + (self.canvas_box.width / 16) * (i + 1)
                h = self.canvas_box.height * 0.4
                base_y = self.canvas_box.y + self.canvas_box.height * 0.3 + (random.random() * 20)
                is_up = random.random() > 0.4
                Color(*(ThemeConfig.GREEN if is_up else ThemeConfig.RED))
                Rectangle(pos=(cx - ui_dp(4), base_y), size=(ui_dp(8), h * random.random()))
                Line(points=[cx, base_y - 10, cx, base_y + 40], width=ui_dp(1))

        with self.volume_box.canvas:
            # Volume Bars
            for i in range(15):
                cx = self.volume_box.x + (self.volume_box.width / 16) * (i + 1)
                vol_h = self.volume_box.height * 0.8 * random.random()
                Color(0.4, 0.4, 0.4, 0.6)
                Rectangle(pos=(cx - ui_dp(4), self.volume_box.y), size=(ui_dp(8), vol_h))

# --- TAB CONTENT CLASSES ---

class WatchlistTab(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(orientation='vertical', padding=ui_dp(8), spacing=ui_dp(10), **kwargs)
        self.add_widget(Label(text='Watchlist', font_size=ui_sp(20), bold=True, size_hint_y=None, height=ui_dp(40), color=ThemeConfig.TEXT_BRIGHT))
        
        sv = ScrollView(bar_width=0)
        list_grid = GridLayout(cols=1, spacing=ui_dp(8), size_hint_y=None)
        list_grid.bind(minimum_height=list_grid.setter('height'))
        
        stocks = ['BBCA', 'BBRI', 'BMRI', 'TLKM', 'ASII', 'GOTO', 'UNVR', 'AMRT']
        for s in stocks:
            row = Card(bg_color=ThemeConfig.SURFACE_LIGHT, size_hint_y=None, height=ui_dp(70), orientation='horizontal', padding=ui_dp(10))
            left = BoxLayout(orientation='vertical')
            left.add_widget(Label(text=s, bold=True, halign='left', font_size=ui_sp(16)))
            left.add_widget(Label(text='Emiten Corp', font_size=ui_sp(11), color=ThemeConfig.TEXT_MUTED))
            
            mid = Sparkline(values=[random.random() for _ in range(12)], size_hint_x=0.4)
            
            right = BoxLayout(orientation='vertical')
            right.add_widget(Label(text='10.250', bold=True, halign='right'))
            right.add_widget(Label(text='+2.45%', color=ThemeConfig.GREEN, halign='right'))
            
            row.add_widget(left) row.add_widget(mid) row.add_widget(right)
            list_grid.add_widget(row)
            
        sv.add_widget(list_grid)
        self.add_widget(sv)

class JurnalTab(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(orientation='vertical', padding=ui_dp(12), spacing=ui_dp(12), **kwargs)
        
        # Header Metrics
        metrics = BoxLayout(size_hint_y=None, height=ui_dp(80), spacing=ui_dp(10))
        c1 = Card()
        c1.add_widget(Label(text='TOTAL EQUITY', font_size=ui_sp(10), color=ThemeConfig.TEXT_MUTED))
        c1.add_widget(Label(text='IDR 142.8M', font_size=ui_sp(18), bold=True))
        
        c2 = Card()
        c2.add_widget(Label(text='REALIZED P/L', font_size=ui_sp(10), color=ThemeConfig.TEXT_MUTED))
        c2.add_widget(Label(text='+IDR 12.4M', font_size=ui_sp(18), bold=True, color=ThemeConfig.GREEN))
        
        metrics.add_widget(c1) metrics.add_widget(c2)
        self.add_widget(metrics)
        
        # EQUITY CURVE (Requested Enhancement)
        curve_card = Card(size_hint_y=None, height=ui_dp(240))
        curve_card.add_widget(Label(text='EQUITY GROWTH', font_size=ui_sp(12), bold=True, color=ThemeConfig.TEXT_BRIGHT, size_hint_y=None, height=ui_dp(30)))
        curve_card.add_widget(Sparkline(values=[10, 12, 11, 15, 14, 18, 22, 20, 25], line_color=ThemeConfig.ACCENT))
        self.add_widget(curve_card)
        
        # WIN/LOSS RATIO (Requested Enhancement)
        wl_card = Card(size_hint_y=None, height=ui_dp(100))
        wl_header = BoxLayout(size_hint_y=None, height=ui_dp(30))
        wl_header.add_widget(Label(text='WIN/LOSS RATIO', font_size=ui_sp(12), bold=True, halign='left'))
        wl_header.add_widget(Label(text='68%', font_size=ui_sp(16), bold=True, color=ThemeConfig.GREEN, halign='right'))
        wl_card.add_widget(wl_header)
        wl_card.add_widget(ProgressBar(value=0.68))
        footer = BoxLayout(size_hint_y=None, height=ui_dp(20))
        footer.add_widget(Label(text='42 WINS', font_size=ui_sp(10), color=ThemeConfig.GREEN))
        footer.add_widget(Label(text='20 LOSSES', font_size=ui_sp(10), color=ThemeConfig.RED, halign='right'))
        wl_card.add_widget(footer)
        self.add_widget(wl_card)
        
        self.add_widget(Widget()) # Spacer

class ScreeningTab(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(orientation='vertical', padding=ui_dp(8), spacing=ui_dp(8), **kwargs)
        header = BoxLayout(size_hint_y=None, height=ui_dp(40))
        header.add_widget(Label(text='Screening Live', font_size=ui_sp(18), bold=True, color=ThemeConfig.TEXT_BRIGHT))
        header.add_widget(Widget())
        header.add_widget(Badge('LIVE', bg_color=ThemeConfig.RED))
        self.add_widget(header)
        
        table_hdr = BoxLayout(size_hint_y=None, height=ui_dp(30), padding=(ui_dp(10), 0))
        for h in ['SAHAM', 'PRICE', 'RVOL', 'STRENGTH']:
            table_hdr.add_widget(Label(text=h, font_size=ui_sp(10), bold=True, color=ThemeConfig.TEXT_MUTED))
        self.add_widget(table_hdr)
        
        sv = ScrollView(bar_width=0)
        grid = GridLayout(cols=1, spacing=ui_dp(2), size_hint_y=None)
        grid.bind(minimum_height=grid.setter('height'))
        for s in ['BBRI', 'ASII', 'BBNI', 'GOTO', 'UNVR']:
            row = Card(bg_color=ThemeConfig.SURFACE_LIGHT, size_hint_y=None, height=ui_dp(60), orientation='horizontal')
            row.add_widget(Label(text=s, bold=True))
            row.add_widget(Label(text='6.125', color=ThemeConfig.GREEN))
            row.add_widget(Label(text='2.4x', color=ThemeConfig.YELLOW))
            row.add_widget(Sparkline(values=[random.random() for _ in range(6)], size_hint_x=0.3))
            grid.add_widget(row)
        sv.add_widget(grid)
        self.add_widget(sv)

class CekEmitenTab(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(orientation='vertical', padding=ui_dp(12), spacing=ui_dp(12), **kwargs)
        
        # Header Info
        header = BoxLayout(size_hint_y=None, height=ui_dp(60))
        title = BoxLayout(orientation='vertical')
        title.add_widget(Label(text='BBRI', font_size=ui_sp(28), bold=True, halign='left'))
        title.add_widget(Label(text='Bank Rakyat Indonesia', font_size=ui_sp(12), color=ThemeConfig.TEXT_MUTED))
        header.add_widget(title)
        
        price = BoxLayout(orientation='vertical', size_hint_x=None, width=ui_dp(120))
        price.add_widget(Label(text='4.780', font_size=ui_sp(24), bold=True, color=ThemeConfig.GREEN, halign='right'))
        price.add_widget(Label(text='+2.58%', font_size=ui_sp(14), color=ThemeConfig.GREEN, halign='right'))
        header.add_widget(price)
        self.add_widget(header)
        
        # TECHNICAL ALERT SYSTEM (Requested Enhancement)
        alert_btn = Button(text='🔔 SET PRICE ALERTS', size_hint_y=None, height=ui_dp(48), background_normal='', background_color=ThemeConfig.RED, color=ThemeConfig.TEXT_BRIGHT, bold=True)
        alert_btn.background_color = (0.2, 0.1, 0.1, 1) # Dark red hue
        self.add_widget(alert_btn)
        
        # ENHANCED CHART WITH VOLUME (Requested Enhancement)
        self.add_widget(CandlestickVolumeChart(size_hint_y=None, height=ui_dp(320)))
        
        # Bandarmology Card
        bandar = Card(size_hint_y=None, height=ui_dp(120))
        bandar.add_widget(Label(text='BANDARMOLOGY FLOW', font_size=ui_sp(10), bold=True, color=ThemeConfig.TEXT_MUTED))
        f_row = BoxLayout()
        f_row.add_widget(Label(text='FOREIGN NET BUY', font_size=ui_sp(12)))
        f_row.add_widget(Label(text='+452.8B', color=ThemeConfig.GREEN, bold=True))
        bandar.add_widget(f_row)
        self.add_widget(bandar)
        
        self.add_widget(Widget())

# --- APP ROOT ---
class MainApp(App):
    def build(self):
        Window.clearcolor = ThemeConfig.BG_MAIN
        self.root = BoxLayout(orientation='vertical')
        
        # Content Area
        self.content_area = BoxLayout()
        self.tabs = [WatchlistTab(), JurnalTab(), ScreeningTab(), CekEmitenTab()]
        self.switch_tab(0)
        
        # Bottom Navigation
        nav = BoxLayout(size_hint_y=None, height=ui_dp(65), padding=ui_dp(4))
        with nav.canvas.before:
            Color(rgb=ThemeConfig.SURFACE)
            Rectangle(pos=nav.pos, size=nav.size)
            Color(rgb=ThemeConfig.BORDER)
            Line(points=[0, ui_dp(65), Window.width, ui_dp(65)], width=1)
            
        self.nav_btns = []
        labels = ['Watchlist', 'Jurnal', 'Screening', 'Cek Emiten']
        for i, text in enumerate(labels):
            btn = Button(text=text, background_color=(0,0,0,0), color=ThemeConfig.TEXT_DEFAULT, font_size=ui_sp(10))
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
            btn.color = ThemeConfig.ACCENT if i == idx else ThemeConfig.TEXT_DEFAULT

if __name__ == '__main__':
    MainApp().run()
