import flet as ft
import flet_webview as ftwv
import os

# --- Konfigurasi Warna (Tetap) ---
BG_MAIN = "#0c141b"
SURFACE = "#181c21"
ACCENT = "#159D91"
TEXT_MUTED = "#8b919b"

def main(page: ft.Page):
    page.title = "Jurnal Saham IHSG - QuantFlow"
    page.theme_mode = ft.ThemeMode.DARK
    page.bgcolor = BG_MAIN
    page.padding = 0

    base_path = os.path.dirname(os.path.abspath(__file__))

    def get_html_path(filename):
        return f"file://{os.path.join(base_path, 'tabs_html', filename)}"

    # ========== 1. FUNGSI PEMBUAT HALAMAN ==========
    # Fungsi ini akan membuat dan mengembalikan sebuah tampilan halaman (ft.View)
    # untuk setiap tab yang diklik.
    def create_tab_view(tab_name, html_filename):
        # Buat WebView untuk halaman ini
        wv = ftwv.WebView(
            url=get_html_path(html_filename),
            expand=True,
        )

        # Tombol navigasi (Bottom Bar) untuk halaman ini
        def navigate_to_home(e):
            # Saat tombol ditekan, kita bersihkan riwayat dan kembali ke halaman Watchlist
            page.views.clear()
            page.views.append(create_tab_view("Watchlist", "watchlist.html"))
            page.update()

        # Definisikan Bottom Navigation Bar untuk halaman ini
        # Perhatikan: Tombol "Home" di sini
        nav_bar = ft.Container(
            content=ft.Row([
                ft.Container(
                    content=ft.Text("🏠 Home", size=14, color=ACCENT),
                    on_click=navigate_to_home,
                    padding=10,
                    expand=True,
                ),
                # Anda bisa menambahkan tombol lain di sini jika mau
            ], alignment=ft.MainAxisAlignment.CENTER),
            padding=10,
            bgcolor=SURFACE,
            border=ft.border.only(top=ft.BorderSide(1, "#2a2a2a")),
        )

        # Gabungkan WebView dan Bottom Bar ke dalam sebuah halaman (ft.View)
        return ft.View(
            route=f"/{tab_name.lower()}",
            controls=[
                # Header sederhana (opsional)
                ft.Container(
                    content=ft.Row([
                        ft.Text("QuantFlow", size=24, weight="bold", color=ACCENT),
                        ft.Text(tab_name, size=18, weight="bold", color="white"),
                    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                    padding=ft.padding.symmetric(horizontal=20, vertical=12),
                    bgcolor="#101419", 
                ),
                wv, # WebView sebagai konten utama
                nav_bar, # Bottom Navigation
            ],
            spacing=0,
            padding=0,
            vertical_alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        )

    # ========== 2. HALAMAN UTAMA (DASHBOARD DENGAN 6 TOMBOL) ==========
    # Halaman ini adalah 'launcher' yang berisi 6 tombol untuk membuka masing-masing tab.
    def go_to_tab(e, tab_name, html_file):
        page.views.append(create_tab_view(tab_name, html_file))
        page.update()

    # Tombol-tombol untuk 6 tab
    tab_buttons = ft.Column([
        ft.ElevatedButton("📈 Watchlist", on_click=lambda e: go_to_tab(e, "Watchlist", "watchlist.html"), bgcolor=ACCENT, color="white"),
        ft.ElevatedButton("📊 Top 10", on_click=lambda e: go_to_tab(e, "Top 10", "top10.html"), bgcolor=ACCENT, color="white"),
        ft.ElevatedButton("📋 Jurnal", on_click=lambda e: go_to_tab(e, "Jurnal", "portfolio.html"), bgcolor=ACCENT, color="white"),
        ft.ElevatedButton("⚡ Screening", on_click=lambda e: go_to_tab(e, "Screening", "screening.html"), bgcolor=ACCENT, color="white"),
        ft.ElevatedButton("🏛️ Cek Emiten", on_click=lambda e: go_to_tab(e, "Cek Emiten", "cek_emiten.html"), bgcolor=ACCENT, color="white"),
        ft.ElevatedButton("💬 AI Chat", on_click=lambda e: go_to_tab(e, "AI Chat", "ai_chat.html"), bgcolor=ACCENT, color="white"),
    ], spacing=15, horizontal_alignment="center")

    # Tampilan halaman utama (sebagai ganti status loading)
    page.views.clear()
    page.views.append(
        ft.View(
            route="/",
            controls=[
                ft.Container(
                    content=ft.Column([
                        ft.Text("QuantFlow", size=32, weight="bold", color=ACCENT),
                        ft.Text("Pilih Tab", size=20, color="white", margin=ft.margin.only(bottom=40)),
                        tab_buttons,
                    ], horizontal_alignment="center", spacing=20),
                    expand=True,
                    alignment=ft.alignment.center,
                )
            ],
            vertical_alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        )
    )
    page.update()


ft.app(target=main)