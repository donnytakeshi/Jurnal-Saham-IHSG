import flet as ft

# Theme Quant Edge
BG_MAIN = "#0c141b"
SURFACE = "#181c21"
ACCENT = "#159D91"
GREEN = "#67d9cb"
RED = "#ff5e5e"
TEXT_BRIGHT = "#ffffff"
TEXT_MUTED = "#8b919b"

def main(page: ft.Page):
    page.title = "Jurnal Saham IHSG - QuantFlow"
    page.theme_mode = ft.ThemeMode.DARK
    page.bgcolor = BG_MAIN
    page.padding = 0
    
    # Data saham
    watchlist_data = [
        {"code": "BBCA", "name": "Bank Central Asia", "price": 10250, "change": 2.45},
        {"code": "BBRI", "name": "Bank Rakyat Indonesia", "price": 5425, "change": -0.82},
        {"code": "BMRI", "name": "Bank Mandiri", "price": 6850, "change": 1.12},
        {"code": "TLKM", "name": "Telkom Indonesia", "price": 3940, "change": 0.00},
        {"code": "ASII", "name": "Astra International", "price": 5125, "change": -1.92},
        {"code": "GOTO", "name": "GoTo Gojek Tokopedia", "price": 68, "change": 4.62},
    ]
    
    def build_watchlist():
        stock_cards = []
        for stock in watchlist_data:
            change_color = GREEN if stock["change"] > 0 else (RED if stock["change"] < 0 else TEXT_MUTED)
            change_sign = "+" if stock["change"] > 0 else ""
            price_formatted = f"{stock['price']:,}".replace(",", ".")
            
            card = ft.Container(
                content=ft.Row([
                    ft.Column([
                        ft.Text(stock["code"], size=16, weight="bold", color=TEXT_BRIGHT),
                        ft.Text(stock["name"], size=11, color=TEXT_MUTED),
                    ], spacing=2),
                    ft.Container(expand=True),
                    ft.Column([
                        ft.Text(price_formatted, size=14, weight="bold", color=TEXT_BRIGHT, text_align="right"),
                        ft.Text(f"{change_sign}{stock['change']}%", size=12, color=change_color, text_align="right"),
                    ], spacing=2, horizontal_alignment="end"),
                ]),
                padding=12,
                bgcolor=SURFACE,
                border_radius=12,
                margin=ft.Margin(0, 0, 0, 8),
            )
            stock_cards.append(card)
        
        # Summary banners (tanpa icon)
        summary = ft.Row([
            ft.Container(
                content=ft.Column([
                    ft.Text("PORTFOLIO VALUE", size=10, color=TEXT_MUTED),
                    ft.Text("Rp 142.5M", size=22, weight="bold", color=TEXT_BRIGHT),
                    ft.Row([ft.Text("📈", size=14), ft.Text("+1.2% Today", size=11, color=GREEN)], spacing=4),
                ]),
                padding=12,
                bgcolor=SURFACE,
                border_radius=12,
                expand=True,
            ),
            ft.Container(
                content=ft.Column([
                    ft.Text("IHSG INDEX", size=10, color=TEXT_MUTED),
                    ft.Text("7,245.12", size=22, weight="bold", color=TEXT_BRIGHT),
                    ft.Row([ft.Text("📉", size=14), ft.Text("-0.45%", size=11, color=RED)], spacing=4),
                ]),
                padding=12,
                bgcolor=SURFACE,
                border_radius=12,
                expand=True,
            ),
        ], spacing=12)
        
        return ft.Container(
            content=ft.Column([
                summary,
                ft.Text("Watchlist", size=18, weight="bold", color=TEXT_BRIGHT, margin=ft.Margin(0, 16, 0, 8)),
                ft.Column(stock_cards, spacing=0),
            ], scroll=ft.ScrollMode.ALWAYS),
            padding=ft.Padding(16, 12, 16, 12),
            expand=True,
        )
    
    def build_placeholder(title):
        return ft.Container(
            content=ft.Column([
                ft.Text(title, size=24, weight="bold", color=ACCENT),
                ft.Text("Content coming soon...", size=14, color=TEXT_MUTED, margin=ft.Margin(0, 20, 0, 0)),
            ], horizontal_alignment="center"),
            alignment=ft.alignment.center,
            expand=True,
        )
    
    # Area konten
    content_area = ft.Container(expand=True)
    content_area.content = build_watchlist()
    
    # Bottom navigation (tanpa icon, pakai teks biasa dulu)
    nav_items = [
        {"label": "Watchlist", "content": build_watchlist},
        {"label": "Top 10", "content": lambda: build_placeholder("Top 10 IHSG")},
        {"label": "Jurnal", "content": lambda: build_placeholder("Jurnal Transaksi")},
        {"label": "Screening", "content": lambda: build_placeholder("Screening Saham")},
        {"label": "Cek Emiten", "content": lambda: build_placeholder("Cek Emiten")},
        {"label": "AI Chat", "content": lambda: build_placeholder("AI Trading Assistant")},
    ]
    
    nav_buttons = []
    
    def change_tab(index):
        content_area.content = nav_items[index]["content"]()
        for i, btn in enumerate(nav_buttons):
            if i == index:
                btn.bgcolor = ACCENT
                btn.content.controls[0].color = TEXT_BRIGHT
            else:
                btn.bgcolor = ft.colors.TRANSPARENT
                btn.content.controls[0].color = TEXT_MUTED
        page.update()
    
    for i, item in enumerate(nav_items):
        btn = ft.Container(
            content=ft.Text(item["label"], size=12, color=ACCENT if i == 0 else TEXT_MUTED),
            padding=ft.Padding(0, 12, 0, 12),
            border_radius=ft.border_radius.only(top_left=12, top_right=12),
            bgcolor=ACCENT if i == 0 else ft.colors.TRANSPARENT,
            expand=True,
            alignment=ft.alignment.center,
            on_click=lambda e, idx=i: change_tab(idx),
        )
        nav_buttons.append(btn)
    
    nav_bar = ft.Container(
        content=ft.Row(controls=nav_buttons, spacing=0),
        height=50,
        bgcolor=SURFACE,
        border=ft.border.only(top=ft.BorderSide(1, "#ffffff0d")),
    )
    
    page.add(ft.Column([content_area, nav_bar], spacing=0, expand=True))

# Gunakan run() sesuai deprecation warning
if __name__ == "__main__":
    ft.app(target=main)