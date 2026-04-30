
import flet as ft
def main(page: ft.Page):
    page.title = "Jurnal Saham IHSG"
    page.theme_mode = ft.ThemeMode.DARK
    page.add(
        ft.Text("✅ APLIKASI BERJALAN!", size=28, weight="bold", color="#159D91"),
        ft.Text("Flet 0.84.0 - Arsitektur Baru", size=20),
        ft.Text("6 Tab Modular Navigation", size=16, color="grey"),
    )
ft.app(target=main)

