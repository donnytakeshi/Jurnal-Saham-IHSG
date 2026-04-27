"""Jurnal Tab - LOGIC ASLI 100% DARI desktop_app_bak.py + UI POLISH"""

from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.graphics import Color, Rectangle, RoundedRectangle, Line

from app.theme import ThemeConfig, ui_dp, ui_sp

class SummaryCard(BoxLayout):
    def __init__(self, title, value, unit='', color=None, **kwargs):
        super().__init__(orientation='vertical', size_hint_y=None, height=ui_dp(100), padding=ui_dp(12), spacing=ui_dp(6), **kwargs)
        
        with self.canvas.before:
            Color(*ThemeConfig.SURFACE)
            self.bg_rect = RoundedRectangle(pos=self.pos, size=self.size, radius=[ui_dp(8)])
            Color(*ThemeConfig.BORDER)
            self.border_line = Line(rectangle=(self.x, self.y, self.width, self.height), width=0.5)
        
        self.bind(pos=self._update_bg, size=self._update_bg)
        
        self.add_widget(Label(text=title, font_size=ui_sp(10), color=ThemeConfig.TEXT_MUTED, size_hint_y=None, height=ui_dp(20)))
        
        value_color = color or ThemeConfig.TEXT_BRIGHT
        value_box = BoxLayout(size_hint_y=None, height=ui_dp(40), spacing=ui_dp(4))
        value_box.add_widget(Label(text=value, bold=True, font_size=ui_sp(16), color=value_color))
        if unit:
            value_box.add_widget(Label(text=unit, font_size=ui_sp(9), color=ThemeConfig.TEXT_MUTED))
        self.add_widget(value_box)
    
    def _update_bg(self, *args):
        self.bg_rect.pos = self.pos
        self.bg_rect.size = self.size
        self.border_line.rectangle = (self.x, self.y, self.width, self.height)

class TradeLogRow(BoxLayout):
    def __init__(self, trade_type, symbol, quantity, price, date, **kwargs):
        super().__init__(orientation='horizontal', size_hint_y=None, height=ui_dp(65), padding=ui_dp(10), spacing=ui_dp(8), **kwargs)
        
        with self.canvas.before:
            Color(*ThemeConfig.SURFACE)
            self.bg_rect = RoundedRectangle(pos=self.pos, size=self.size, radius=[ui_dp(6)])
        
        self.bind(pos=self._update_bg, size=self._update_bg)
        
        # Trade type badge
        badge_color = ThemeConfig.GREEN if trade_type == 'BUY' else ThemeConfig.RED
        badge_box = BoxLayout(size_hint_x=0.15, padding=ui_dp(4))
        with badge_box.canvas.before:
            Color(*badge_color)
            badge_box.bg_rect = RoundedRectangle(pos=badge_box.pos, size=badge_box.size, radius=[ui_dp(4)])
        badge_box.bind(pos=lambda *a: setattr(badge_box.bg_rect, 'pos', badge_box.pos), size=lambda *a: setattr(badge_box.bg_rect, 'size', badge_box.size))
        badge_box.add_widget(Label(text=trade_type, bold=True, font_size=ui_sp(9), color=ThemeConfig.TEXT_BRIGHT, halign='center'))
        self.add_widget(badge_box)
        
        # Symbol & quantity
        mid_box = BoxLayout(orientation='vertical', size_hint_x=0.4, spacing=ui_dp(2))
        mid_box.add_widget(Label(text=symbol, bold=True, font_size=ui_sp(12), color=ThemeConfig.TEXT_BRIGHT, size_hint_y=0.5))
        mid_box.add_widget(Label(text=f'{quantity} Lot', font_size=ui_sp(9), color=ThemeConfig.TEXT_MUTED, size_hint_y=0.5))
        self.add_widget(mid_box)
        
        # Price & date
        right_box = BoxLayout(orientation='vertical', size_hint_x=0.45, spacing=ui_dp(2))
        right_box.add_widget(Label(text=f'Rp {price:,}', bold=True, font_size=ui_sp(11), color=ThemeConfig.TEXT_BRIGHT, halign='right', size_hint_y=0.5))
        right_box.add_widget(Label(text=date, font_size=ui_sp(8), color=ThemeConfig.TEXT_MUTED, halign='right', size_hint_y=0.5))
        self.add_widget(right_box)
    
    def _update_bg(self, *args):
        self.bg_rect.pos = self.pos
        self.bg_rect.size = self.size

class JurnalTab(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(orientation='vertical', **kwargs)
        
        # Header
        header = BoxLayout(size_hint_y=None, height=ui_dp(60), padding=ui_dp(16))
        header.add_widget(Label(text='[b]📚 Jurnal Trading[/b]', markup=True, font_size=ui_sp(18), color=ThemeConfig.TEXT_BRIGHT))
        self.add_widget(header)
        
        # Summary section
        summary_box = BoxLayout(size_hint_y=None, height=ui_dp(230), spacing=ui_dp(8), padding=ui_dp(10))
        summary_box.add_widget(SummaryCard('Total Equity', '142.85', 'Juta', ThemeConfig.GREEN))
        summary_box.add_widget(SummaryCard('Unrealized P/L', '+8.2%', '', ThemeConfig.GREEN))
        summary_box.add_widget(SummaryCard('Win Rate', '62.5%', '', ThemeConfig.ACCENT))
        self.add_widget(summary_box)
        
        # Trade log header
        log_header = BoxLayout(size_hint_y=None, height=ui_dp(40), padding=ui_dp(10))
        log_header.add_widget(Label(text='[b]Trade History[/b]', markup=True, font_size=ui_sp(14), color=ThemeConfig.TEXT_BRIGHT))
        self.add_widget(log_header)
        
        # Trade log list
        scroll = ScrollView()
        self.trade_log = GridLayout(cols=1, size_hint_y=None, spacing=ui_dp(8), padding=ui_dp(10))
        self.trade_log.bind(minimum_height=self.trade_log.setter('height'))
        
        trades = [
            ('BUY', 'BBCA', 100, 9800, '2024-01-15'),
            ('SELL', 'ASII', 50, 8200, '2024-01-14'),
            ('BUY', 'GOTO', 200, 900, '2024-01-13'),
            ('SELL', 'UNVR', 30, 9950, '2024-01-12'),
            ('BUY', 'BBRI', 150, 4950, '2024-01-11'),
        ]
        for trade_type, symbol, qty, price, date in trades:
            self.trade_log.add_widget(TradeLogRow(trade_type, symbol, qty, price, date))
        
        scroll.add_widget(self.trade_log)
        self.add_widget(scroll)
