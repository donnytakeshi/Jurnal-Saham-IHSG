# tabs/watchlist_tab.py - FIXED (no 'name=' parameter)
import flet as ft
from theme import ThemeConfig

def build(page: ft.Page):
    """Return Watchlist tab content exactly like Stitch design"""
    
    # Data saham
    stocks_data = [
        {"code": "BBCA", "name": "Bank Central Asia", "price": 10250, "change": 2.45, "trend": "up", "sparkline": [25, 20, 22, 10, 15, 5]},
        {"code": "BBRI", "name": "Bank Rakyat Indonesia", "price": 5425, "change": -0.82, "trend": "down", "sparkline": [5, 15, 10, 25, 30, 20]},
        {"code": "BMRI", "name": "Bank Mandiri", "price": 6850, "change": 1.12, "trend": "up", "sparkline": [30, 25, 15, 12, 8, 2]},
        {"code": "TLKM", "name": "Telkom Indonesia", "price": 3940, "change": 0.00, "trend": "flat", "sparkline": [16, 18, 15, 17, 16, 16]},
        {"code": "ASII", "name": "Astra International", "price": 5125, "change": -1.92, "trend": "down", "sparkline": [2, 5, 12, 18, 25, 30]},
        {"code": "GOTO", "name": "GoTo Gojek Tokopedia", "price": 68, "change": 4.62, "trend": "up", "sparkline": [30, 30, 25, 20, 5, 2]},
    ]
    
    def format_price(price):
        if price >= 1000:
            return f"{price:,.0f}".replace(",", ".")
        return str(price)
    
    def get_change_color(change):
        if change > 0:
            return ThemeConfig.GREEN
        elif change < 0:
            return ThemeConfig.RED
        return ThemeConfig.NEUTRAL
    
    def get_change_sign(change):
        if change > 0:
            return f"+{change}%"
        elif change < 0:
            return f"{change}%"
        return "0.00%"
    
    # Build stock cards
    stock_cards = []
    for stock in stocks_data:
        sparkline_values = stock["sparkline"]
        min_val = min(sparkline_values)
        max_val = max(sparkline_values)
        range_val = max_val - min_val if max_val != min_val else 1
        
        stock_card = ft.Container(
            content=ft.Row(
                [
                    ft.Column(
                        [
                            ft.Text(stock["code"], size=ThemeConfig.FONT_HEADLINE_MD, weight="bold", color=ThemeConfig.TEXT_BRIGHT),
                            ft.Text(stock["name"], size=ThemeConfig.FONT_BODY_SM, color=ThemeConfig.TEXT_MUTED),
                        ],
                        spacing=4,
                    ),
                    ft.Container(expand=True),
                    # Sparkline chart
                    ft.Container(
                        content=ft.Row(
                            [
                                ft.Container(
                                    width=4,
                                    height=20 + (val - min_val) / range_val * 20,
                                    bgcolor=ThemeConfig.GREEN if stock["trend"] == "up" else (ThemeConfig.RED if stock["trend"] == "down" else ThemeConfig.NEUTRAL),
                                    border_radius=2,
                                ) for val in sparkline_values
                            ],
                            spacing=2,
                            alignment="end",
                        ),
                        width=80,
                        height=32,
                    ),
                    ft.Column(
                        [
                            ft.Text(format_price(stock["price"]), size=ThemeConfig.FONT_HEADLINE_MD, weight="bold", color=ThemeConfig.TEXT_BRIGHT, text_align="right"),
                            ft.Text(get_change_sign(stock["change"]), size=ThemeConfig.FONT_BODY_SM, weight="bold", color=get_change_color(stock["change"]), text_align="right"),
                        ],
                        spacing=4,
                        horizontal_alignment="end",
                    ),
                ],
                alignment="spaceBetween",
            ),
            padding=16,
            bgcolor=ThemeConfig.SURFACE,
            border_radius=ThemeConfig.BORDER_RADIUS,
            border=ft.border.all(1, ThemeConfig.BORDER_COLOR),
            margin=ft.margin.only(bottom=10),
        )
        stock_cards.append(stock_card)
    
    # Summary Banners - FIXED: tanpa 'name='
    summary_row = ft.Row(
        [
            ft.Container(
                content=ft.Column(
                    [
                        ft.Text("PORTFOLIO VALUE", size=ThemeConfig.FONT_LABEL_MD, color=ThemeConfig.TEXT_MUTED),
                        ft.Text("Rp 142.5M", size=ThemeConfig.FONT_HEADLINE_LG + 4, weight="bold", color=ThemeConfig.TEXT_BRIGHT),
                        ft.Row(
                            [
                                ft.Icon(ft.Icons.TRENDING_UP, size=14, color=ThemeConfig.GREEN),
                                ft.Text("+1.2% Today", size=ThemeConfig.FONT_BODY_SM, color=ThemeConfig.GREEN),
                            ],
                            spacing=4,
                        ),
                    ],
                    spacing=4,
                ),
                padding=16,
                bgcolor=ThemeConfig.SURFACE,
                border_radius=ThemeConfig.BORDER_RADIUS,
                border=ft.border.all(1, ThemeConfig.BORDER_COLOR),
                expand=True,
            ),
            ft.Container(
                content=ft.Column(
                    [
                        ft.Text("IHSG INDEX", size=ThemeConfig.FONT_LABEL_MD, color=ThemeConfig.TEXT_MUTED),
                        ft.Text("7,245.12", size=ThemeConfig.FONT_HEADLINE_LG + 4, weight="bold", color=ThemeConfig.TEXT_BRIGHT),
                        ft.Row(
                            [
                                ft.Icon(ft.Icons.TRENDING_DOWN, size=14, color=ThemeConfig.RED),
                                ft.Text("-0.45%", size=ThemeConfig.FONT_BODY_SM, color=ThemeConfig.RED),
                            ],
                            spacing=4,
                        ),
                    ],
                    spacing=4,
                ),
                padding=16,
                bgcolor=ThemeConfig.SURFACE,
                border_radius=ThemeConfig.BORDER_RADIUS,
                border=ft.border.all(1, ThemeConfig.BORDER_COLOR),
                expand=True,
            ),
        ],
        spacing=12,
    )
    
    # Market Insights Section
    market_insights = ft.Container(
        content=ft.Column(
            [
                ft.Text("Market Insights", size=ThemeConfig.FONT_HEADLINE_MD, weight="bold", color=ThemeConfig.TEXT_BRIGHT),
                ft.Container(
                    content=ft.Column(
                        [
                            ft.Text("TECH ANALYSIS", size=10, weight="bold", color=ThemeConfig.ACCENT),
                            ft.Text("IHSG Resistance Level at 7,300", size=ThemeConfig.FONT_HEADLINE_MD, weight="bold", color=ThemeConfig.TEXT_BRIGHT),
                            ft.Text(
                                "Volume remains low as investors await interest rate decisions from the central bank...",
                                size=ThemeConfig.FONT_BODY_SM,
                                color=ThemeConfig.TEXT_MUTED,
                            ),
                        ],
                        spacing=8,
                    ),
                    padding=16,
                    bgcolor=ThemeConfig.SURFACE,
                    border_radius=ThemeConfig.BORDER_RADIUS,
                    border=ft.border.all(1, ThemeConfig.BORDER_COLOR),
                ),
            ],
            spacing=12,
        ),
        margin=ft.margin.only(top=24),
    )
    
    # Main content
    content = ft.Container(
        content=ft.Column(
            [
                summary_row,
                ft.Text("Watchlist", size=ThemeConfig.FONT_HEADLINE_LG, weight="bold", color=ThemeConfig.TEXT_BRIGHT),
                ft.Column(stock_cards, spacing=0),
                market_insights,
            ],
            spacing=16,
            scroll=ft.ScrollMode.ALWAYS,
        ),
        padding=ft.padding.symmetric(horizontal=20, vertical=16),
        expand=True,
    )
    
    return content