"""Custom Widgets & Components - DARI desktop_app_bak.py (LOGIC TETAP ASLI)"""

import random
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.widget import Widget
from kivy.uix.button import Button
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.behaviors import ButtonBehavior
from kivy.properties import ListProperty, NumericProperty
from kivy.graphics import Color, Rectangle, RoundedRectangle, Line, Ellipse
from kivy.clock import Clock
from kivy.utils import platform as _kivy_platform

from app.theme import ThemeConfig, ui_dp, ui_sp

# ============================================================================
# CUSTOM WIDGETS (LOGIC ASLI - TIDAK BERUBAH)
# ============================================================================

class ClickableBehavior(ButtonBehavior):
    pass

class ClickableLabel(ClickableBehavior, Label):
    pass

class ClickableRow(ClickableBehavior, BoxLayout):
    pass

class SparklineWidget(Widget):
    values = ListProperty([])
    line_color = ListProperty([0.11, 0.75, 0.36, 1])

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.bind(pos=self._redraw, size=self._redraw, values=self._redraw, line_color=self._redraw)

    def _redraw(self, *args):
        self.canvas.clear()
        if not self.values or len(self.values) < 2:
            return
        try:
            w = max(1.0, float(self.width))
            h = max(1.0, float(self.height))
            pad = ui_dp(2)
            xs = []
            vmin = min(self.values)
            vmax = max(self.values)
            flat = (vmax - vmin) == 0
            denom = (vmax - vmin) if not flat else 1.0
            for i, v in enumerate(self.values):
                x = self.x + pad + (w - pad * 2) * (i / (len(self.values) - 1))
                y_norm = 0.5 if flat else ((v - vmin) / denom)
                y = self.y + pad + (h - pad * 2) * y_norm
                xs.extend([x, y])
            with self.canvas:
                Color(*self.line_color)
                Line(points=xs, width=ui_dp(1.2), cap='round', joint='round')
        except Exception:
            return

class _NavIcon(Widget):
    icon_type = ''
    color = ListProperty(ThemeConfig.TEXT_DEFAULT)

    def __init__(self, icon_type='', **kwargs):
        super().__init__(**kwargs)
        self.icon_type = str(icon_type or '').strip().lower()
        self.bind(pos=self._redraw, size=self._redraw, color=self._redraw)

    def _redraw(self, *args):
        self.canvas.clear()
        w = max(1.0, float(self.width))
        h = max(1.0, float(self.height))
        pad = ui_dp(2)
        cx = self.x + w / 2.0
        cy = self.y + h / 2.0
        col = list(self.color or [0.70, 0.70, 0.70, 1])
        t = ui_dp(1.7)
        with self.canvas:
            Color(*col)
            it = self.icon_type
            if it == 'watchlist':
                left = self.x + pad + ui_dp(2)
                right = self.x + w - pad
                y1 = self.y + h * 0.7
                y2 = self.y + h * 0.5
                y3 = self.y + h * 0.3
                Line(points=[left + ui_dp(6), y1, right, y1], width=t)
                Line(points=[left + ui_dp(6), y2, right, y2], width=t)
                Line(points=[left + ui_dp(6), y3, right, y3], width=t)
                r = ui_dp(2.2)
                Ellipse(pos=(left - r * 0.5, y1 - r * 0.5), size=(r, r))
                Ellipse(pos=(left - r * 0.5, y2 - r * 0.5), size=(r, r))
                Ellipse(pos=(left - r * 0.5, y3 - r * 0.5), size=(r, r))
            elif it == 'top10':
                base_y = self.y + pad
                x0 = self.x + pad
                step = (w - pad * 2) / 4.0
                Line(points=[x0, base_y, x0, base_y + h * 0.35], width=t)
                Line(points=[x0 + step, base_y, x0 + step, base_y + h * 0.55], width=t)
                Line(points=[x0 + 2 * step, base_y, x0 + 2 * step, base_y + h * 0.80], width=t)
                ax = x0 + 2 * step
                ay = base_y + h * 0.80
                Line(points=[ax, ay, ax + ui_dp(4), ay + ui_dp(6)], width=t)
                Line(points=[ax, ay, ax - ui_dp(4), ay + ui_dp(6)], width=t)
            elif it == 'jurnal':
                rw = w - pad * 2
                rh = h - pad * 2
                Line(rounded_rectangle=(self.x + pad, self.y + pad, rw, rh, ui_dp(3)), width=t)
                Line(points=[self.x + pad + rw * 0.22, self.y + pad + rh * 0.72, self.x + pad + rw * 0.78, self.y + pad + rh * 0.72], width=t)
            elif it == 'screening':
                r = min(w, h) * 0.32
                Ellipse(pos=(cx - r, cy - r), size=(2 * r, 2 * r))
                hx1 = cx + r * 0.6
                hy1 = cy - r * 0.1
                hx2 = hx1 + ui_dp(6)
                hy2 = hy1 - ui_dp(6)
                Line(points=[hx1, hy1, hx2, hy2], width=t)
            elif it == 'cek':
                bw = w * 0.55
                bh = h * 0.60
                bx = cx - bw / 2.0
                by = cy - bh / 2.0
                Line(rectangle=(bx, by, bw, bh), width=t)
                wx = bx + bw * 0.25
                wy = by + bh * 0.65
                s = ui_dp(2.2)
                Ellipse(pos=(wx - s / 2.0, wy - s / 2.0), size=(s, s))
                Ellipse(pos=(wx + bw * 0.3 - s / 2.0, wy - s / 2.0), size=(s, s))
                Ellipse(pos=(wx - s / 2.0, wy - bh * 0.35 - s / 2.0), size=(s, s))
                Ellipse(pos=(wx + bw * 0.3 - s / 2.0, wy - bh * 0.35 - s / 2.0), size=(s, s))
                Line(points=[bx - ui_dp(2), by - ui_dp(2), bx + bw + ui_dp(2), by - ui_dp(2)], width=t)
            else:
                r = min(w, h) * 0.35
                Ellipse(pos=(cx - r, cy - r), size=(2 * r, 2 * r))

class SwipeToDeleteRow(Widget):
    dx = NumericProperty(0)

    def __init__(self, content, on_delete=None, on_tap=None, delete_width=110, scrollview=None, tap_widget=None, tap_filter=None, **kwargs):
        super().__init__(**kwargs)
        try:
            self._is_android = (str(_kivy_platform).lower() == 'android')
        except:
            self._is_android = False
        self.size_hint_y = None
        self.height = kwargs.get('height', ui_dp(86))
        self._delete_width = ui_dp(delete_width)
        self._on_delete = on_delete
        self._on_tap = on_tap
        self._tap_widget = tap_widget
        self._tap_filter = tap_filter
        self._scrollview = scrollview
        self._touch_start = None
        self._start_dx = 0
        self._start_scroll_y = None
        self._mode = None
        self._root = FloatLayout()
        self.add_widget(self._root)
        self._delete_btn = Button(
            text='Hapus',
            size_hint=(None, 1),
            width=self._delete_width,
            pos_hint={'right': 1, 'y': 0},
            background_normal='',
            background_down='',
            background_color=ThemeConfig.DELETE_BTN_BG,
            color=ThemeConfig.TEXT_DELETE,
            padding=(0, 0)
        )
        self._root.add_widget(self._delete_btn)
        self._content = content
        self._content.size_hint = (None, None)
        self._content.height = self.height
        self._root.add_widget(self._content)

        def _sync_layout(*_args):
            self._root.pos = self.pos
            self._root.size = self.size
            pad_x = ui_dp(4)
            self._delete_btn.height = self.height
            self._delete_btn.x = self.x + self.width - self._delete_width
            self._delete_btn.y = self.y
            content_w = max(0, self.width - pad_x * 2)
            self._content.size = (content_w, self.height)
            self._content.pos = (self.x + pad_x + self.dx, self.y)
            try:
                if self._is_android:
                    self._delete_btn.disabled = True
                    self._delete_btn.opacity = 0.0
                    self._delete_btn.width = 0
                else:
                    open_enough = (self.dx <= -self._delete_width * 0.8)
                    self._delete_btn.disabled = not open_enough
                    self._delete_btn.opacity = 1.0 if open_enough else 0.0
            except:
                pass

        self.bind(pos=_sync_layout, size=_sync_layout, dx=_sync_layout)
        _sync_layout()

        def _do_delete(_instance):
            if callable(self._on_delete):
                try:
                    self._on_delete()
                except:
                    pass
        self._delete_btn.bind(on_press=_do_delete)

    def on_touch_down(self, touch):
        if getattr(self, '_is_android', False):
            return super().on_touch_down(touch)
        if not self.collide_point(*touch.pos):
            return super().on_touch_down(touch)
        try:
            if self._delete_btn.collide_point(*touch.pos) and (self.dx <= -self._delete_width * 0.8):
                return super().on_touch_down(touch)
        except:
            pass
        self._touch_start = (touch.x, touch.y)
        self._start_dx = self.dx
        try:
            self._start_scroll_y = self._scrollview.scroll_y if self._scrollview is not None else None
        except:
            self._start_scroll_y = None
        self._mode = None
        touch.grab(self)
        return True

    def on_touch_move(self, touch):
        if getattr(self, '_is_android', False):
            return super().on_touch_move(touch)
        if touch.grab_current is not self:
            return super().on_touch_move(touch)
        if not self._touch_start:
            return True
        start_x, start_y = self._touch_start
        dx = touch.x - start_x
        dy = touch.y - start_y
        thresh = ui_dp(10)
        if self._mode is None:
            if abs(dx) > thresh and abs(dx) > abs(dy) * 1.2:
                self._mode = 'swipe'
            elif abs(dy) > thresh and abs(dy) > abs(dx) * 1.2:
                self._mode = 'scroll'
        if self._mode == 'swipe':
            new_dx = self._start_dx + dx
            if new_dx > 0:
                new_dx = 0
            if new_dx < -self._delete_width:
                new_dx = -self._delete_width
            self.dx = new_dx
            return True
        if self._mode == 'scroll' and self._scrollview is not None and self._start_scroll_y is not None:
            try:
                viewport = self._scrollview.children[0]
                scroll_range = max(1.0, float(viewport.height - self._scrollview.height))
                new_scroll_y = float(self._start_scroll_y) + (dy / scroll_range)
                if new_scroll_y < 0:
                    new_scroll_y = 0
                if new_scroll_y > 1:
                    new_scroll_y = 1
                self._scrollview.scroll_y = new_scroll_y
            except:
                pass
            return True
        return True

    def on_touch_up(self, touch):
        if getattr(self, '_is_android', False):
            return super().on_touch_up(touch)
        if touch.grab_current is not self:
            return super().on_touch_up(touch)
        touch.ungrab(self)
        try:
            start_x, start_y = self._touch_start or (None, None)
            if start_x is not None and start_y is not None:
                dx = float(touch.x - start_x)
                dy = float(touch.y - start_y)
                thresh = ui_dp(10)
                if abs(dx) < thresh and abs(dy) < thresh:
                    if self.dx < 0:
                        self.dx = 0
                    else:
                        allow = True
                        try:
                            if callable(self._tap_filter):
                                allow = bool(self._tap_filter(touch))
                            elif self._tap_widget is not None:
                                allow = bool(self._tap_widget.collide_point(*touch.pos))
                        except:
                            allow = True
                        if allow and callable(self._on_tap):
                            try:
                                self._on_tap()
                            except:
                                pass
        except:
            pass
        if self._mode == 'swipe':
            if self.dx < -self._delete_width * 0.4:
                self.dx = -self._delete_width
            else:
                self.dx = 0
        self._touch_start = None
        self._start_scroll_y = None
        self._mode = None
        return True

class PullToRefreshScrollView(Widget):
    """Placeholder - dari desktop_app_bak.py"""
    pass
