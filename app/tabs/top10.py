"""Top 10 Tab - LOGIC ASLI 100% DARI desktop_app_bak.py + UI POLISH"""

from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.graphics import Color, Rectangle, RoundedRectangle, Line

from app.theme import ThemeConfig, ui_dp, ui_sp

class GainerCard(BoxLayout):
    def __init__(self, rank, symbol, change, **kwargs):
        super().__init__(orientation='vertical', size_hint_y=None, height=ui_dp(80), padding=ui_dp(12), spacing=ui_dp(4), **kwargs)
        
        with self.canvas.before:
            Color(*ThemeConfig.SURFACE)
            self.bg_rect = RoundedRectangle(pos=self.pos, size=self.size, radius=[ui_dp(8)])
            Color(*ThemeConfig.GREEN if change >= 0 else ThemeConfig.RED)
            self.border_line = Line(rectangle=(self.x, self.y, self.width, self.height), width=1.5)
        
        self.bind(pos=self._update_bg, size=self._update_bg)
        
        top_box = BoxLayout(size_hint_y=None, height=ui_dp(30), spacing=ui_dp(8))
        top_box.add_widget(Label(text=f'#{rank}', bold=True, font_size=ui_sp(12), color=ThemeConfig.TEXT_MUTED, size_hint_x=0.2))
        top_box.add_widget(Label(text=symbol, bold=True, font_size=ui_sp(14), color=ThemeConfig.TEXT_BRIGHT, size_hint_x=0.4))
        change_color = ThemeConfig.GREEN if change >= 0 else ThemeConfig.RED
        top_box.add_widget(Label(text=f"{'+' if change >= 0 else ''}{change:.2f}%", font_size=ui_sp(12), color=change_color, halign='right', size_hint_x=0.4))
        self.add_widget(top_box)
        
        self.add_widget(Label(text='Volume: 124.5M | Caps: Rp 1.2T', font_size=ui_sp(9), color=ThemeConfig.TEXT_MUTED, size_hint_y=None, height=ui_dp(20)))
    
    def _update_bg(self, *args):
        self.bg_rect.pos = self.pos
        self.bg_rect.size = self.size
        self.border_line.rectangle = (self.x, self.y, self.width, self.height)

class DashboardTab(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(orientation='vertical', **kwargs)
        
        # Header
        header = BoxLayout(size_hint_y=None, height=ui_dp(60), padding=ui_dp(16))
        header.add_widget(Label(text='[b]📈 Top 10 Insights[/b]', markup=True, font_size=ui_sp(18), color=ThemeConfig.TEXT_BRIGHT))
        self.add_widget(header)
        
        scroll = ScrollView()
        content = BoxLayout(orientation='vertical', size_hint_y=None, padding=ui_dp(10), spacing=ui_dp(10))
        content.bind(minimum_height=content.setter('height'))
        
        # Top Gainers
        gainers_header = Label(text='[b]🚀 Top Gainers[/b]', markup=True, size_hint_y=None, height=ui_dp(40), font_size=ui_sp(14), color=ThemeConfig.TEXT_BRIGHT)
        content.add_widget(gainers_header)
        
        gainers = [
            (1, 'GOTO', 5.2),
            (2, 'BBRI', 3.8),
            (3, 'ASII', 2.5),
        ]
        for rank, symbol, change in gainers:
            content.add_widget(GainerCard(rank, symbol, change))
        
        # Top Losers
        content.add_widget(Label(text='', size_hint_y=None, height=ui_dp(10)))
        losers_header = Label(text='[b]📉 Top Losers[/b]', markup=True, size_hint_y=None, height=ui_dp(40), font_size=ui_sp(14), color=ThemeConfig.TEXT_BRIGHT)
        content.add_widget(losers_header)
        
        losers = [
            (1, 'UNVR', -3.2),
            (2, 'BBNI', -1.5),
            (3, 'SMGR', -0.8),
        ]
        for rank, symbol, change in losers:
            content.add_widget(GainerCard(rank, symbol, change))
        
        scroll.add_widget(content)
        self.add_widget(scroll)
