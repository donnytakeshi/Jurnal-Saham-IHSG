"""Theme Config & UI Helpers - DARI desktop_app_bak.py (LOGIC TETAP ASLI)"""

from kivy.utils import get_color_from_hex
from kivy.metrics import dp, sp

# ============================================================================
# THEME CONFIG (LOGIC ASLI - TIDAK BERUBAH)
# ============================================================================
class ThemeConfig:
    SPARKLINE = [0.11, 0.75, 0.36, 1]
    BG_CARD = get_color_from_hex('#181c21')
    BG_MAIN = get_color_from_hex('#101419')
    SURFACE = get_color_from_hex('#181c21')
    SURFACE_LIGHT = get_color_from_hex('#1c2127')
    ACCENT = get_color_from_hex('#159D91')
    GREEN = get_color_from_hex('#67d9cb')
    RED = get_color_from_hex('#ff5e5e')
    YELLOW = get_color_from_hex('#f2d18f')
    BORDER = get_color_from_hex('#2d3432')
    TEXT_BRIGHT = get_color_from_hex('#ffffff')
    TEXT_DEFAULT = get_color_from_hex('#bcc9c6')
    TEXT_MUTED = get_color_from_hex('#41493e')
    ROUNDNESS = 12
    FONT_HEADER = 18
    TEXT_HEADER = get_color_from_hex('#ffffff')
    BG_NAV = get_color_from_hex('#181c21')
    BG_NAV_LINE = get_color_from_hex('#23272c')
    BUTTON_BG = get_color_from_hex('#23272c')
    FONT_NAV = 15
    TEXT_ACTIVE = get_color_from_hex('#67d9cb')
    BG_HEADER = get_color_from_hex('#181c21')
    RADIUS_CARD = 12
    BG_CHART = get_color_from_hex('#0F1419')
    FONT_SIGNAL = 16
    TEXT_SIGNAL = get_color_from_hex('#67d9cb')
    RADIUS_BTN = 8
    TEXT_BUTTON = get_color_from_hex('#ffffff')
    DELETE_BTN_BG = get_color_from_hex('#8B0000')
    TEXT_DELETE = get_color_from_hex('#ffffff')


# ============================================================================
# UI HELPERS (LOGIC ASLI - TIDAK BERUBAH)
# ============================================================================
def ui_dp(v): 
    return dp(v)

def ui_sp(v): 
    return sp(v)

def _log_info(tag, msg):
    try:
        print(f"[INFO] {tag}: {msg}")
    except:
        pass

def _log_exception(tag, msg):
    try:
        print(f"[ERROR] {tag}: {msg}")
    except:
        pass

def _to_float(value, default=0.0):
    try:
        if value is None:
            return default
        if isinstance(value, (int, float)):
            return float(value)
        s = str(value).strip().replace(',', '')
        return float(s)
    except Exception:
        return default

def _format_id_number(value, decimals=0):
    try:
        n = float(value)
        fmt = f"{{:,.{decimals}f}}".format(n)
        result = fmt.replace(',', 'X').replace('.', ',').replace('X', '.')
        if decimals == 0:
            result = result.replace(',00', '')
        return result
    except Exception:
        return str(value)

def _format_price(value):
    if value in (None, '', '-'):
        return '-'
    n = _to_float(value, default=None)
    if n is None:
        return str(value)
    return _format_id_number(n, decimals=0)

def _format_change_pair(change_abs, change_pct):
    if change_abs in (None, '', '-') and change_pct in (None, '', '-'):
        return '-'
    ca = _to_float(change_abs, default=0.0)
    cp = _to_float(change_pct, default=0.0)
    sign = '+' if ca > 0 else ''
    abs_txt = _format_id_number(ca, decimals=0)
    pct_txt = _format_id_number(cp, decimals=2)
    return f"{sign}{abs_txt} ({sign if cp>0 else ''}{pct_txt}%)"

def _format_compact_number(value):
    if value in (None, '', '-'):
        return '-'
    n = _to_float(value, default=None)
    if n is None:
        return str(value)
    abs_n = abs(n)
    if abs_n >= 1_000_000_000:
        return f"{n/1_000_000_000:.2f}B".rstrip('0').rstrip('.')
    if abs_n >= 1_000_000:
        return f"{n/1_000_000:.2f}M".rstrip('0').rstrip('.')
    if abs_n >= 1_000:
        return f"{n/1_000:.2f}K".rstrip('0').rstrip('.')
    return _format_id_number(n, decimals=0)

def _is_idx_market_open(now=None) -> bool:
    from datetime import datetime
    try:
        if now is None:
            now = datetime.now()
        if now.weekday() >= 5:
            return False
        h = now.hour + (now.minute / 60.0)
        return 9.0 <= h <= 16.0
    except Exception:
        return False

def _spark_values_for(symbol: str, chg_val: float, n: int = 14):
    import random
    rng = random.Random(symbol)
    base = rng.random() * 0.2 + 0.4
    noise = [rng.uniform(-0.08, 0.08) for _ in range(n)]
    trend = 0.18 if chg_val >= 0 else -0.18
    vals = []
    for i in range(n):
        t = i / max(1, n - 1)
        vals.append(base + trend * (t - 0.5) + noise[i])
    return vals

def _autosize_button_to_text(btn, extra_w=0):
    try:
        btn.texture_update()
        btn.width = btn.texture_size[0] + extra_w
    except:
        pass

def _make_styled_popup(content, title="", size_hint=(0.9, None), height=400, auto_dismiss=True):
    from kivy.uix.popup import Popup
    popup = Popup(title=title, content=content, size_hint=size_hint, auto_dismiss=auto_dismiss)
    if height:
        popup.height = height
    return popup
