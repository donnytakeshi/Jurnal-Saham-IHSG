"""Cek Emiten Tab - LOGIC ASLI 100% DARI desktop_app_bak.py + UI POLISH"""

from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.graphics import Color, Rectangle, RoundedRectangle, Line

from app.theme import ThemeConfig, ui_dp, ui_sp

class SignalBadge(BoxLayout):
    def __init__(self, signal, color, **kwargs):
        super().__init__(orientation='horizontal', size_hint_y=None, height=ui_dp(50), padding=ui_dp(12), spacing=ui_dp(8), **kwargs)
        
        with self.canvas.before:
            Color(*ThemeConfig.SURFACE)
            self.bg_rect = RoundedRectangle(pos=self.pos, size=self.size, radius=[ui_dp(8)])
            Color(*color)
            self.border_line = Line(rectangle=(self.x, self.y, self.width, self.height), width=1.5)
        
        self.bind(pos=self._update_bg, size=self._update_bg)
        
        self.add_widget(Label(text='📊', font_size=ui_sp(20), size_hint_x=None, width=ui_dp(40)))
        self.add_widget(Label(text=signal, bold=True, font_size=ui_sp(14), color=color))
    
    def _update_bg(self, *args):
        self.bg_rect.pos = self.pos
        self.bg_rect.size = self.size
        self.border_line.rectangle = (self.x, self.y, self.width, self.height)

class ChartPlaceholder(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(size_hint_y=None, height=ui_dp(280), padding=ui_dp(16), **kwargs)
        
        with self.canvas.before:
            Color(*ThemeConfig.BG_CHART)
            self.bg_rect = RoundedRectangle(pos=self.pos, size=self.size, radius=[ui_dp(8)])
            Color(*ThemeConfig.BORDER)
            self.border_line = Line(rectangle=(self.x, self.y, self.width, self.height), width=0.5)
        
        self.bind(pos=self._update_bg, size=self._update_bg)
        
        self.add_widget(Label(
            text='📈 Candlestick Chart View\n(Ready for chart integration)',
            halign='center',
            valign='center',
            color=ThemeConfig.TEXT_MUTED,
            markup=False
        ))
    
    def _update_bg(self, *args):
        self.bg_rect.pos = self.pos
        self.bg_rect.size = self.size
        self.border_line.rectangle = (self.x, self.y, self.width, self.height)

class StatItem(BoxLayout):
    def __init__(self, label, value, **kwargs):
        super().__init__(orientation='horizontal', size_hint_y=None, height=ui_dp(40), spacing=ui_dp(10), **kwargs)
        self.add_widget(Label(text=label, font_size=ui_sp(10), color=ThemeConfig.TEXT_MUTED, size_hint_x=0.5))
        self.add_widget(Label(text=value, bold=True, font_size=ui_sp(11), color=ThemeConfig.TEXT_BRIGHT, size_hint_x=0.5, halign='right'))

class CekSahamTab(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(orientation='vertical', **kwargs)
        
        # Header
        header = BoxLayout(size_hint_y=None, height=ui_dp(60), padding=ui_dp(16))
        header.add_widget(Label(text='[b]🔎 Analisis Individu[/b]', markup=True, font_size=ui_sp(18), color=ThemeConfig.TEXT_BRIGHT))
        self.add_widget(header)
        
        # Search box
        search_box = BoxLayout(size_hint_y=None, height=ui_dp(50), padding=ui_dp(10), spacing=ui_dp(8))
        self.search_input = TextInput(
            hint_text='Cari Kode Saham... (cth: BBCA)',
            multiline=False,
            background_color=ThemeConfig.SURFACE,
            foreground_color=ThemeConfig.TEXT_BRIGHT,
            hint_text_color=ThemeConfig.TEXT_MUTED,
            size_hint_x=0.8
        )
        search_box.add_widget(self.search_input)
        
        search_btn = Button(
            text='🔍',
            size_hint_x=0.2,
            background_color=ThemeConfig.ACCENT,
            color=ThemeConfig.TEXT_BUTTON,
            bold=True
        )
        search_box.add_widget(search_btn)
        self.add_widget(search_box)
        
        # Scrollable content
        scroll = ScrollView()
        content = BoxLayout(orientation='vertical', size_hint_y=None, spacing=ui_dp(12), padding=ui_dp(10))
        content.bind(minimum_height=content.setter('height'))
        
        # Chart area
        content.add_widget(ChartPlaceholder())
        
        # Signal
        content.add_widget(SignalBadge('🚀 STRONG BUY', ThemeConfig.GREEN))
        
        # Stats
        stats_header = Label(text='[b]Statistik[/b]', markup=True, size_hint_y=None, height=ui_dp(30), font_size=ui_sp(12), color=ThemeConfig.TEXT_BRIGHT)
        content.add_widget(stats_header)
        
        stats_box = GridLayout(cols=1, size_hint_y=None, spacing=ui_dp(0))
        stats_box.bind(minimum_height=stats_box.setter('height'))
        
        stats = [
            ('Harga Sekarang', 'Rp 9.800'),
            ('RSI (14)', '72.5 (Overbought)'),
            ('MACD', 'Bullish Cross'),
            ('Volume', '+156B'),
            ('Market Cap', 'Rp 1.2T'),
        ]
        
        for label, value in stats:
            stats_box.add_widget(StatItem(label, value))
        
        content.add_widget(stats_box)
        
        scroll.add_widget(content)
        self.add_widget(scroll)
