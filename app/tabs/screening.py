"""Screening Tab - LOGIC ASLI 100% DARI desktop_app_bak.py + UI POLISH"""

from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.graphics import Color, Rectangle

from app.theme import ThemeConfig, ui_dp, ui_sp

class DataFetcher:
    sample_stocks = [
        {'symbol': 'BBRI', 'price': 4950, 'change': 2.5, 'volume': '+124B'},
        {'symbol': 'ASII', 'price': 8200, 'change': -1.2, 'volume': '-85B'},
        {'symbol': 'BBNI', 'price': 5100, 'change': 1.8, 'volume': '+156B'},
        {'symbol': 'GOTO', 'price': 850, 'change': 3.5, 'volume': '+203B'},
        {'symbol': 'UNVR', 'price': 9950, 'change': -0.5, 'volume': '+42B'},
        {'symbol': 'BBCA', 'price': 9800, 'change': 2.1, 'volume': '+87B'},
    ]

class ScreeningRow(BoxLayout):
    def __init__(self, symbol, price, change, volume, is_header=False, **kwargs):
        super().__init__(orientation='horizontal', size_hint_y=None, height=ui_dp(45), padding=ui_dp(8), spacing=ui_dp(0), **kwargs)
        
        if not is_header:
            with self.canvas.before:
                idx = hash(symbol) % 2
                bg_color = ThemeConfig.SURFACE_LIGHT if idx == 0 else ThemeConfig.SURFACE
                Color(*bg_color)
                self.bg_rect = Rectangle(pos=self.pos, size=self.size)
            self.bind(pos=self._update_bg, size=self._update_bg)
        
        # Symbol
        self.add_widget(Label(
            text=symbol if not is_header else 'SAHAM',
            bold=is_header,
            font_size=ui_sp(11 if is_header else 10),
            color=ThemeConfig.TEXT_BRIGHT if is_header else ThemeConfig.TEXT_DEFAULT,
            size_hint_x=0.25,
            halign='left'
        ))
        
        # Price
        self.add_widget(Label(
            text=str(price) if not is_header else 'HARGA',
            bold=is_header,
            font_size=ui_sp(11 if is_header else 10),
            color=ThemeConfig.TEXT_BRIGHT if is_header else ThemeConfig.TEXT_DEFAULT,
            size_hint_x=0.25,
            halign='center'
        ))
        
        # Change %
        if is_header:
            change_text = 'CHANGE'
            change_color = ThemeConfig.TEXT_BRIGHT
        else:
            change_text = f"{'+' if change >= 0 else ''}{change:.1f}%"
            change_color = ThemeConfig.GREEN if change >= 0 else ThemeConfig.RED
        
        self.add_widget(Label(
            text=change_text,
            bold=is_header,
            font_size=ui_sp(11 if is_header else 10),
            color=change_color,
            size_hint_x=0.25,
            halign='center'
        ))
        
        # Volume
        self.add_widget(Label(
            text=str(volume) if not is_header else 'NET B/S',
            bold=is_header,
            font_size=ui_sp(11 if is_header else 10),
            color=ThemeConfig.TEXT_BRIGHT if is_header else ThemeConfig.TEXT_DEFAULT,
            size_hint_x=0.25,
            halign='right'
        ))
    
    def _update_bg(self, *args):
        self.bg_rect.pos = self.pos
        self.bg_rect.size = self.size

class ScreeningTab(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(orientation='vertical', **kwargs)
        
        # Header
        header = BoxLayout(size_hint_y=None, height=ui_dp(60), padding=ui_dp(16))
        header.add_widget(Label(text='[b]🔍 Live Screening[/b]', markup=True, font_size=ui_sp(18), color=ThemeConfig.TEXT_BRIGHT))
        self.add_widget(header)
        
        scroll = ScrollView()
        table = GridLayout(cols=1, size_hint_y=None, spacing=ui_dp(0))
        table.bind(minimum_height=table.setter('height'))
        
        # Header row
        table.add_widget(ScreeningRow('', '', '', '', is_header=True))
        
        # Data rows
        for s in DataFetcher.sample_stocks:
            table.add_widget(ScreeningRow(s['symbol'], f"Rp {s['price']:,}", s['change'], s['volume']))
        
        scroll.add_widget(table)
        self.add_widget(scroll)
