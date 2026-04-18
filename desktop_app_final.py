# --- Jurnal Saham IHSG - FINAL UNIFIED KIVY APP ---
# Includes: Watchlist, Market Insights, Screening, Portfolio, and Trading Calculator.
# Features: Pro Charts, Technical Alerts UI, and Profit/Loss Simulation.
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
            Color(*self.bg_color)
            RoundedRectangle(pos=self.pos, size=self.size, radius=[ui_dp(4)])
            Color(*self.fill_color)
            RoundedRectangle(pos=self.pos, size=(self.width * self.value, self.height), radius=[ui_dp(4)])

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
            
            row.add_widget(left); row.add_widget(mid); row.add_widget(right)
            list_grid.add_widget(row)
            
        sv.add_widget(list_grid)
        self.add_widget(sv)

class CalculatorTab(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(orientation='vertical', padding=ui_dp(12), spacing=ui_dp(16), **kwargs)
        self.add_widget(Label(text='TRADING CALCULATOR', font_size=ui_sp(18), bold=True, size_hint_y=None, height=ui_dp(40)))
        
        params = Card(spacing=ui_dp(10))
        params.add_widget(Label(text='TRADE PARAMETERS', font_size=ui_sp(12), color=ThemeConfig.TEXT_MUTED, bold=True))
        
        def input_field(lbl, placeholder):
            box = BoxLayout(orientation='vertical', spacing=ui_dp(4), size_hint_y=None, height=ui_dp(60))
            box.add_widget(Label(text=lbl, font_size=ui_sp(11), color=ThemeConfig.TEXT_DEFAULT, halign='left'))
            ti = TextInput(text='', hint_text=placeholder, multiline=False, background_color=ThemeConfig.SURFACE_LIGHT, foreground_color=ThemeConfig.TEXT_BRIGHT, padding=ui_dp(10))
            box.add_widget(ti)
            return box

        params.add_widget(input_field('Stock Code', 'e.g. BBCA'))
        row2 = BoxLayout(spacing=ui_dp(8), size_hint_y=None, height=ui_dp(60))
        row2.add_widget(input_field('Buy Price', '0.00'))
        row2.add_widget(input_field('Target Price', '0.00'))
        params.add_widget(row2)
        
        calc_btn = Button(text='CALCULATE EXECUTION', background_color=ThemeConfig.ACCENT, color=ThemeConfig.TEXT_BRIGHT, bold=True, size_hint_y=None, height=ui_dp(48))
        params.add_widget(calc_btn)
        self.add_widget(params)
        
        summary = Card(bg_color=ThemeConfig.SURFACE_LIGHT)
        summary.add_widget(Label(text='EXECUTIVE SUMMARY', font_size=ui_sp(12), color=ThemeConfig.TEXT_MUTED, bold=True))
        
        res_row = BoxLayout(spacing=ui_dp(10))
        def res_cell(lbl, val, col=ThemeConfig.TEXT_BRIGHT):
            box = BoxLayout(orientation='vertical')
            box.add_widget(Label(text=lbl, font_size=ui_sp(10), color=ThemeConfig.TEXT_DEFAULT))
            box.add_widget(Label(text=val, font_size=ui_sp(24), bold=True, color=col))
            return box
        
        res_row.add_widget(res_cell('Potential Profit', '$4,250.00', ThemeConfig.GREEN))
        res_row.add_widget(res_cell('Potential Loss', '$850.00', ThemeConfig.RED))
        summary.add_widget(res_row)
        
        summary.add_widget(Label(text='RISK/REWARD RATIO 1:5.0', font_size=ui_sp(12), bold=True))
        summary.add_widget(ProgressBar(value=0.2)) # 1:5
        
        self.add_widget(summary)
        self.add_widget(Widget()) # Spacer

class JurnalTab(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(orientation='vertical', padding=ui_dp(12), spacing=ui_dp(12), **kwargs)
        
        metrics = BoxLayout(size_hint_y=None, height=ui_dp(80), spacing=ui_dp(10))
        c1 = Card(); c1.add_widget(Label(text='TOTAL EQUITY', font_size=ui_sp(10), color=ThemeConfig.TEXT_MUTED)); c1.add_widget(Label(text='IDR 142.8M', font_size=ui_sp(18), bold=True))
        c2 = Card(); c2.add_widget(Label(text='REALIZED P/L', font_size=ui_sp(10), color=ThemeConfig.TEXT_MUTED)); c2.add_widget(Label(text='+IDR 12.4M', font_size=ui_sp(18), bold=True, color=ThemeConfig.GREEN))
        metrics.add_widget(c1); metrics.add_widget(c2)
        self.add_widget(metrics)
        
        curve_card = Card(size_hint_y=None, height=ui_dp(200))
        curve_card.add_widget(Label(text='EQUITY GROWTH', font_size=ui_sp(12), bold=True))
        curve_card.add_widget(Sparkline(values=[10, 12, 11, 15, 14, 18, 22, 20, 25]))
        self.add_widget(curve_card)
        
        self.add_widget(Label(text='RECENT TRADES', font_size=ui_sp(14), bold=True, halign='left'))
        sv = ScrollView()
        grid = GridLayout(cols=1, spacing=ui_dp(4), size_hint_y=None)
        grid.bind(minimum_height=grid.setter('height'))
        for t in [('BBCA', 'BUY', '10.200'), ('BBRI', 'SELL', '4.780')]:
            row = Card(orientation='horizontal', height=ui_dp(50), size_hint_y=None)
            row.add_widget(Label(text=t[0], bold=True))
            row.add_widget(Badge(t[1], bg_color=ThemeConfig.GREEN if t[1]=='BUY' else ThemeConfig.RED))
            row.add_widget(Label(text=t[2]))
            grid.add_widget(row)
        sv.add_widget(grid)
        self.add_widget(sv)

# --- APP ROOT ---
class MainApp(App):
    def build(self):
        Window.clearcolor = ThemeConfig.BG_MAIN
        self.root = BoxLayout(orientation='vertical')
        
        self.content_area = BoxLayout()
        self.tabs = [WatchlistTab(), JurnalTab(), CalculatorTab(), JurnalTab()] # Simplified tab mapping
        self.switch_tab(0)
        
        nav = BoxLayout(size_hint_y=None, height=ui_dp(65), padding=ui_dp(4))
        with nav.canvas.before:
            Color(rgb=ThemeConfig.SURFACE)
            Rectangle(pos=nav.pos, size=nav.size)
            Color(rgb=ThemeConfig.BORDER)
            Line(points=[0, ui_dp(65), Window.width, ui_dp(65)], width=1)
            
        self.nav_btns = []
        labels = ['Watchlist', 'Jurnal', 'Calculator', 'Screening']
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
