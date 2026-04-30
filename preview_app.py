import flet as ft

def main(page: ft.Page):
    # Setup page
    page.title = "Jurnal Saham IHSG - Preview"
    page.theme_mode = ft.ThemeMode.DARK
    page.padding = 20

    # Header
    header = ft.Text("📈 JURNAL SAHAM IHSG",
                     size=28,
                     weight="bold",
                     color="#159D91")

    # Navigation bar
    nav = ft.Tabs(
        selected_index=0,
        tabs=[
            ft.Tab(text="📈 Watchlist"),
            ft.Tab(text="🏆 Top 10"),
            ft.Tab(text="📊 Jurnal"),
            ft.Tab(text="🔍 Screening"),
            ft.Tab(text="🏢 Cek Emiten"),
            ft.Tab(text="🤖 AI Chat"),
        ]
    )

    # Content area
    content = ft.Container(
        content=ft.Column([
            ft.Text("Preview Aplikasi Modular", size=20),
            ft.Text("• 6 Tab Navigation", color="grey"),
            ft.Text("• Dark Theme", color="grey"),
            ft.Text("• Flet Framework", color="grey"),
            ft.Text("• Hybrid: Flet + WebView", color="#159D91"),
        ]),
        padding=20,
        border=ft.border.all(1, "#2d3432"),
        border_radius=10,
    )

    # Footer
    footer = ft.Text("🚀 Ready for APK Build",
                     size=12,
                     color="grey",
                     italic=True)

    # Assemble
    page.add(
        header,
        ft.Divider(height=20, color="transparent"),
        nav,
        ft.Divider(height=20, color="transparent"),
        content,
        ft.Divider(height=20, color="transparent"),
        footer
    )

if __name__ == "__main__":
    ft.app(target=main)
