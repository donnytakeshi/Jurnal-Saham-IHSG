"""AI Chat Tab - POLISH & FUNCTIONAL"""

from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.graphics import Color, Rectangle, RoundedRectangle

from app.theme import ThemeConfig, ui_dp, ui_sp

class ChatMessage(BoxLayout):
    def __init__(self, text, is_user=True, **kwargs):
        super().__init__(orientation='horizontal', size_hint_y=None, height=ui_dp(50), padding=ui_dp(10), spacing=ui_dp(10), **kwargs)
        
        if is_user:
            self.add_widget(BoxLayout())  # Spacer
            msg_box = BoxLayout(size_hint_x=0.75)
        else:
            msg_box = BoxLayout(size_hint_x=0.75)
            self.add_widget(BoxLayout())  # Spacer
        
        with msg_box.canvas.before:
            if is_user:
                Color(*ThemeConfig.ACCENT)
            else:
                Color(*ThemeConfig.SURFACE)
            msg_box.bg_rect = RoundedRectangle(pos=msg_box.pos, size=msg_box.size, radius=[ui_dp(12)])
        
        msg_box.bind(pos=lambda *a: setattr(msg_box.bg_rect, 'pos', msg_box.pos), size=lambda *a: setattr(msg_box.bg_rect, 'size', msg_box.size))
        
        label = Label(
            text=text,
            text_size=(None, None),
            size_hint_y=None,
            color=ThemeConfig.TEXT_BRIGHT if is_user else ThemeConfig.TEXT_DEFAULT,
            font_size=ui_sp(10),
            padding=ui_dp(8)
        )
        label.bind(texture_size=label.setter('size'))
        msg_box.add_widget(label)
        self.add_widget(msg_box)
        
        # Auto height based on content
        self.height = max(ui_dp(40), label.texture_size[1] + ui_dp(16))

class AIChatTab(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(orientation='vertical', **kwargs)
        
        # Header
        header = BoxLayout(size_hint_y=None, height=ui_dp(60), padding=ui_dp(16))
        header.add_widget(Label(text='[b]🤖 AI Chat[/b]', markup=True, font_size=ui_sp(18), color=ThemeConfig.TEXT_BRIGHT))
        self.add_widget(header)
        
        # Chat area
        self.chat_scroll = ScrollView()
        self.chat_list = GridLayout(cols=1, size_hint_y=None, spacing=ui_dp(8), padding=ui_dp(10))
        self.chat_list.bind(minimum_height=self.chat_list.setter('height'))
        
        # Sample messages
        sample_messages = [
            ('Halo! Ada yang bisa dibantu tentang saham?', False),
            ('Apa prediksi untuk BBCA minggu depan?', True),
            ('Berdasarkan analisis teknikal, BBCA menunjukkan breakout dari resistance level 9.850. Support ada di 9.650. Momentum masih bullish dengan RSI di 62.', False),
            ('Terima kasih. Bagaimana dengan ASII?', True),
            ('ASII masih dalam trend downtrend jangka pendek. Tunggu bounce dari level 8.000 sebelum entry.', False),
        ]
        
        for text, is_user in sample_messages:
            self.chat_list.add_widget(ChatMessage(text, is_user=is_user))
        
        self.chat_scroll.add_widget(self.chat_list)
        self.add_widget(self.chat_scroll)
        
        # Input area
        input_box = BoxLayout(orientation='horizontal', size_hint_y=None, height=ui_dp(60), spacing=ui_dp(8), padding=ui_dp(10))
        
        self.text_input = TextInput(
            hint_text='Tanya AI tentang saham...',
            multiline=False,
            background_color=ThemeConfig.SURFACE,
            foreground_color=ThemeConfig.TEXT_BRIGHT,
            hint_text_color=ThemeConfig.TEXT_MUTED,
            size_hint_x=0.85
        )
        input_box.add_widget(self.text_input)
        
        send_btn = Button(
            text='📤',
            size_hint_x=0.15,
            background_color=ThemeConfig.ACCENT,
            color=ThemeConfig.TEXT_BUTTON,
            bold=True,
            font_size=ui_sp(16)
        )
        send_btn.bind(on_press=self._on_send_message)
        input_box.add_widget(send_btn)
        
        self.add_widget(input_box)
    
    def _on_send_message(self, instance):
        text = self.text_input.text.strip()
        if text:
            # Add user message
            self.chat_list.add_widget(ChatMessage(text, is_user=True))
            self.text_input.text = ''
            
            # Simulate AI response (placeholder)
            ai_response = 'Pertanyaan Anda sedang diproses oleh AI. Fitur ini akan terintegrasi dengan backend nantinya.'
            self.chat_list.add_widget(ChatMessage(ai_response, is_user=False))
            
            # Scroll to bottom
            self.chat_scroll.scroll_y = 0
