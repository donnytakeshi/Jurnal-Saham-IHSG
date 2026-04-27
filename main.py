# --- Jurnal Saham IHSG - App Shell / Wrapper (Stitch Design) ---
# File: main.py
# Purpose: Main entry point and UI Shell with 6 tabs including AI

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.widget import Widget
from kivy.properties import ObjectProperty, ListProperty
from kivy.utils import get_color_from_hex
from kivy.core.window import Window
from kivy.graphics import Color, Rectangle, Line
from kivy.metrics import dp, sp

# Import all tabs
from app.tabs import WatchlistTab, DashboardTab, JurnalTab, ScreeningTab, CekSahamTab, AIChatTab

# --- THEME CONFIG ---
class ThemeConfig:
    BG_MAIN = get_color_from_hex('#0c141b')
    SURFACE = get_color_from_hex('#141c23')
    ACCENT = get_color_from_hex('#1F6AA5')
    BORDER = get_color_from_hex('#2D3339')
    TEXT_BRIGHT = get_color_from_hex('#ffffff')
    TEXT_DIM = get_color_from_hex('#bcc9c6')
    TEXT_MUTED = get_color_from_hex('#5b6871')

def ui_dp(v): return dp(v)
def ui_sp(v): return sp(v)

# --- REUSABLE COMPONENTS ---

class AppHeader(BoxLayout):
    def __init__(self, title="JURNAL SAHAM IHSG", **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'horizontal'
        self.size_hint_y = None
        self.height = ui_dp(56)
        self.padding = [ui_dp(16), 0]
        self.spacing = ui_dp(10)
        
        with self.canvas.before:
            Color(rgb=ThemeConfig.SURFACE)
            self.bg_rect = Rectangle(pos=self.pos, size=self.size)
            Color(rgb=ThemeConfig.BORDER)
            self.border_line = Line(points=[self.x, self.y, self.x + self.width, self.y], width=0.5)
            
        self.bind(pos=self._update, size=self._update)
        self.add_widget(Label(text=title, bold=True, font_size=ui_sp(16), color=ThemeConfig.TEXT_BRIGHT, halign='left', valign='middle', size_hint_x=0.7))
        self.add_widget(Label(text='🔔', font_size=ui_sp(18), size_hint_x=None, width=ui_dp(40)))
        self.add_widget(Label(text='👤', font_size=ui_sp(18), size_hint_x=None, width=ui_dp(40)))

    def _update(self, *_):
        self.bg_rect.pos = self.pos
        self.bg_rect.size = self.size
        self.border_line.points = [self.x, self.y, self.x + self.width, self.y]

class BottomNavBar(BoxLayout):
    def __init__(self, on_nav_change, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'horizontal'
        self.size_hint_y = None
        self.height = ui_dp(64)
        self.padding = ui_dp(4)
        self.spacing = ui_dp(2)
        self.on_nav_change = on_nav_change
        
        with self.canvas.before:
            Color(rgb=ThemeConfig.SURFACE)
            self.bg_rect = Rectangle(pos=self.pos, size=self.size)
            Color(rgb=ThemeConfig.BORDER)
            self.border_line = Line(points=[self.x, self.y + self.height, self.x + self.width, self.y + self.height], width=0.5)
            
        self.bind(pos=self._update, size=self._update)
        
        self.nav_items = [
            ('Watchlist', '📊'),
            ('Top 10', '📈'),
            ('Jurnal', '📚'),
            ('Screening', '🔍'),
            ('Cek Emiten', '🔎'),
            ('AI Chat', '🤖')
        ]
        
        self.btns = []
        for i, (label, icon) in enumerate(self.nav_items):
            btn = Button(text=f"{icon}\n{label}", background_color=(0,0,0,0), color=ThemeConfig.TEXT_DIM, font_size=ui_sp(9), halign='center', valign='middle', bold=True)
            btn.bind(on_release=lambda x, idx=i: self._handle_press(idx))
            self.btns.append(btn)
            self.add_widget(btn)
        self._set_active(0)

    def _handle_press(self, idx):
        self._set_active(idx)
        if self.on_nav_change: self.on_nav_change(idx)

    def _set_active(self, idx):
        for i, btn in enumerate(self.btns):
            btn.color = ThemeConfig.ACCENT if i == idx else ThemeConfig.TEXT_DIM

    def _update(self, *_):
        self.bg_rect.pos = self.pos
        self.bg_rect.size = self.size
        self.border_line.points = [self.x, self.y + self.height, self.x + self.width, self.y + self.height]

class AppShell(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.add_widget(AppHeader())
        self.content_area = BoxLayout()
        
        # Initialize tabs
        self.tabs = [
            WatchlistTab(),
            DashboardTab(),
            JurnalTab(),
            ScreeningTab(),
            CekSahamTab(),
            AIChatTab()
        ]
        
        self.switch_tab(0)
        self.add_widget(self.content_area)
        self.add_widget(BottomNavBar(on_nav_change=self.switch_tab))

    def switch_tab(self, idx):
        """Switch ke tab dengan index"""
        self.content_area.clear_widgets()
        if 0 <= idx < len(self.tabs):
            self.content_area.add_widget(self.tabs[idx])

class StockJournalApp(App):
    def build(self):
        Window.clearcolor = ThemeConfig.BG_MAIN
        if Window.size[0] > Window.size[1]: 
            Window.size = (380, 720)
        return AppShell()

if __name__ == '__main__':
    StockJournalApp().run()
