"""Watchlist Tab - LOGIC ASLI 100% DARI desktop_app_bak.py + UI POLISH"""

import random
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.graphics import Color, Rectangle, RoundedRectangle, Line
from kivy.uix.button import Button

from app.theme import ThemeConfig, ui_dp, ui_sp
from app.components import SparklineWidget

class DataFetcher:
    sample_stocks = [
        {'symbol': 'BBRI', 'company_name': 'Bank Rakyat Indonesia', 'price': 4950, 'change': 2.5},
        {'symbol': 'ASII', 'company_name': 'Astra International', 'price': 8200, 'change': -1.2},
        {'symbol': 'BBNI', 'company_name': 'Bank Negara Indonesia', 'price': 5100, 'change': 1.8},
        {'symbol': 'GOTO', 'company_name': 'Goto Gojek Tokopedia', 'price': 850, 'change': 3.5},
        {'symbol': 'UNVR', 'company_name': 'Unilever Indonesia', 'price': 9950, 'change': -0.5},
    ]

class StockRowCard(BoxLayout):
    def __init__(self, symbol, company_name, price, change, sparkline_vals, **kwargs):
        super().__init__(orientation='horizontal', size_hint_y=None, height=ui_dp(90), padding=ui_dp(10), spacing=ui_dp(10), **kwargs)
        
        with self.canvas.before:
            Color(*ThemeConfig.SURFACE)
            self.bg_rect = RoundedRectangle(pos=self.pos, size=self.size, radius=[ui_dp(8)])
            Color(*ThemeConfig.BORDER)
            self.border_line = Line(rectangle=(self.x, self.y, self.width, self.height), width=0.5)
        
        self.bind(pos=self._update_bg, size=self._update_bg)
        
        # Left: Symbol & Company
        left_box = BoxLayout(orientation='vertical', size_hint_x=0.3, spacing=ui_dp(4))
        left_box.add_widget(Label(text=symbol, bold=True, font_size=ui_sp(14), color=ThemeConfig.TEXT_BRIGHT, size_hint_y=0.6))
        left_box.add_widget(Label(text=company_name[:15], font_size=ui_sp(9), color=ThemeConfig.TEXT_MUTED, size_hint_y=0.4))
        self.add_widget(left_box)
        
        # Middle: Sparkline
        sparkline = SparklineWidget(values=sparkline_vals, size_hint_x=0.35, line_color=ThemeConfig.SPARKLINE if change >= 0 else [1, 0.37, 0.37, 1])
        self.add_widget(sparkline)
        
        # Right: Price & Change
        right_box = BoxLayout(orientation='vertical', size_hint_x=0.35, spacing=ui_dp(4), padding=ui_dp(0))
        price_label = Label(text=f'Rp {price:,}', bold=True, font_size=ui_sp(12), color=ThemeConfig.TEXT_BRIGHT, size_hint_y=0.6, halign='right')
        right_box.add_widget(price_label)
        
        change_color = ThemeConfig.GREEN if change >= 0 else ThemeConfig.RED
        change_text = f"{'+' if change >= 0 else ''}{change:.1f}%"
        change_label = Label(text=change_text, font_size=ui_sp(11), color=change_color, size_hint_y=0.4, halign='right')
        right_box.add_widget(change_label)
        self.add_widget(right_box)
    
    def _update_bg(self, *args):
        self.bg_rect.pos = self.pos
        self.bg_rect.size = self.size
        self.border_line.rectangle = (self.x, self.y, self.width, self.height)

class WatchlistTab(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(orientation='vertical', **kwargs)
        self.data_fetcher = DataFetcher()
        self.watchlist = ['BBRI', 'ASII', 'BBNI', 'GOTO', 'UNVR']
        
        # Header
        header = BoxLayout(size_hint_y=None, height=ui_dp(60), padding=ui_dp(16), spacing=ui_dp(10))
        header.add_widget(Label(text='[b]📊 Watchlist[/b]', markup=True, font_size=ui_sp(18), color=ThemeConfig.TEXT_BRIGHT))
        add_btn = Button(text='+', size_hint_x=None, width=ui_dp(40), background_color=ThemeConfig.ACCENT, color=ThemeConfig.TEXT_BUTTON, bold=True)
        header.add_widget(add_btn)
        self.add_widget(header)
        
        # List
        scroll = ScrollView()
        self.list = GridLayout(cols=1, size_hint_y=None, spacing=ui_dp(8), padding=ui_dp(10))
        self.list.bind(minimum_height=self.list.setter('height'))
        
        for s in self.data_fetcher.sample_stocks:
            sparkline_vals = [random.random() for _ in range(12)]
            row = StockRowCard(s['symbol'], s['company_name'], s['price'], s['change'], sparkline_vals)
            self.list.add_widget(row)
        
        scroll.add_widget(self.list)
        self.add_widget(scroll)
