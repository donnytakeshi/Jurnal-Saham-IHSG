# theme.py - Quant Edge Theme (Fixed - removed letter_spacing)
import flet as ft

class ThemeConfig:
    # Background & Surface
    BG_MAIN = "#0c141b"
    SURFACE = "#181c21"
    SURFACE_LIGHT = "#232b32"
    SURFACE_VARIANT = "#2e363d"
    
    # Accent & Status
    ACCENT = "#159D91"
    GREEN = "#67d9cb"
    RED = "#ff5e5e"
    NEUTRAL = "#8b919b"
    
    # Text Colors
    TEXT_BRIGHT = "#ffffff"
    TEXT_DEFAULT = "#dbe3ed"
    TEXT_MUTED = "#8b919b"
    
    # Border & Spacing
    BORDER_COLOR = "#ffffff0d"
    BORDER_RADIUS = 12
    
    # Font Sizes
    FONT_HEADLINE_LG = 20
    FONT_HEADLINE_MD = 16
    FONT_BODY_MD = 14
    FONT_BODY_SM = 13
    FONT_LABEL_MD = 12

def apply_theme(page: ft.Page):
    """Apply theme to Flet page"""
    page.theme_mode = ft.ThemeMode.DARK
    page.bgcolor = ThemeConfig.BG_MAIN
    page.padding = 0
    page.fonts = {
        "Inter": "https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700",
    }
    page.theme = ft.Theme(
        font_family="Inter",
        color_scheme_seed=ThemeConfig.ACCENT,
    )