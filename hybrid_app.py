import flet as ft

def main(page: ft.Page):
    page.title = "Jurnal Saham IHSG - Hybrid"
    page.theme_mode = ft.ThemeMode.DARK

    # Navigation tabs
    tabs = ft.Tabs(
        selected_index=0,
        tabs=[
            ft.Tab(
                text="📈 Chart",
                content=ft.Column([
                    ft.Text("Trading Chart akan muncul di sini", size=20),
                    ft.Text("(WebView untuk TradingView)", color="grey"),
                ])
            ),
            ft.Tab(
                text="📊 Watchlist",
                content=ft.Column([
                    ft.Text("Watchlist Saham", size=24, weight="bold"),
                    ft.ListView([
                        ft.ListTile(
                            title=ft.Text("BBCA - Bank Central Asia"),
                            subtitle=ft.Text("Rp 10.250 (+2.45%)"),
                            trailing=ft.Icon(ft.icons.ARROW_FORWARD_IOS),
                        ),
                        ft.ListTile(
                            title=ft.Text("BBRI - Bank BRI"),
                            trailing=ft.Icon(ft.icons.ARROW_FORWARD_IOS),
                        ),
                    ], expand=True)
                ])
            ),
        ],
        expand=True,
    )

    page.add(tabs)

if __name__ == "__main__":
    ft.app(target=main)
