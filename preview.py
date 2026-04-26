"""
preview.py - Preview UI di desktop tanpa build APK
Jalankan: python preview.py
"""

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.core.window import Window
from kivy.utils import get_color_from_hex

# Set window size seperti HP
Window.size = (400, 750)
Window.clearcolor = get_color_from_hex('#0a0c0e')


class PreviewApp(App):
    def build(self):
        root = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        # Header
        header = BoxLayout(size_hint_y=None, height=50)
        header.add_widget(Label(text='JURNAL SAHAM IHSG', font_size=18, bold=True, color=get_color_from_hex('#159D91')))
        root.add_widget(header)
        
        # IHSG Card
        card = BoxLayout(orientation='vertical', padding=15, size_hint_y=None, height=120)
        with card.canvas.before:
            from kivy.graphics import Color, RoundedRectangle
            Color(*get_color_from_hex('#181c21'))
            RoundedRectangle(pos=card.pos, size=card.size, radius=[12])
        card.add_widget(Label(text='IHSG MARKET SUMMARY', font_size=10, color=get_color_from_hex('#67d9cb')))
        
        ihsg_row = BoxLayout(orientation='horizontal', size_hint_y=None, height=50)
        ihsg_row.add_widget(Label(text='7,321.05', font_size=28, bold=True, color=get_color_from_hex('#ffffff')))
        ihsg_row.add_widget(Label(text='+1.24%', font_size=14, color=get_color_from_hex('#67d9cb'), halign='right'))
        card.add_widget(ihsg_row)
        root.add_widget(card)
        
        # Top Movers
        root.add_widget(Label(text='🔥 TOP MOVERS', font_size=14, bold=True, size_hint_y=None, height=30))
        
        scroll = ScrollView()
        movers = GridLayout(cols=1, spacing=8, size_hint_y=None)
        movers.bind(minimum_height=movers.setter('height'))
        
        for symbol, price, change in [('BBCA', '10,250', '+2.5%'), ('BBRI', '5,425', '+1.8%'), ('TLKM', '3,210', '+0.9%')]:
            row = BoxLayout(orientation='horizontal', size_hint_y=None, height=60, padding=10)
            with row.canvas.before:
                Color(*get_color_from_hex('#181c21'))
                RoundedRectangle(pos=row.pos, size=row.size, radius=[8])
            row.add_widget(Label(text=symbol, font_size=16, bold=True, size_hint_x=0.3))
            row.add_widget(Label(text=f'Rp {price}', font_size=14, halign='right', size_hint_x=0.4))
            row.add_widget(Label(text=change, font_size=12, color=get_color_from_hex('#67d9cb'), halign='right', size_hint_x=0.3))
            movers.add_widget(row)
        
        scroll.add_widget(movers)
        root.add_widget(scroll)
        
        # Bottom Nav (placeholder)
        nav = BoxLayout(size_hint_y=None, height=55)
        for icon in ['🏠', '⭐', '📊', '🔍', '🤖']:
            nav.add_widget(Button(text=icon, background_color=[0,0,0,0], font_size=20))
        root.add_widget(nav)
        
        return root


if __name__ == '__main__':
    PreviewApp().run()
