import flet as ft

def main(page: ft.Page):
    page.title = "TradingView Test"
    page.theme_mode = ft.ThemeMode.DARK
    page.bgcolor = "#101419"
    
    # Tambahkan WebView
    tv_chart = ft.WebView(
        url="https://www.tradingview.com/chart/",
        width=page.width,
        height=600,
    )
    
    page.add(tv_chart)
    page.update()

ft.app(target=main)
