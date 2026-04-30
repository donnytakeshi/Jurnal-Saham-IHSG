import flet as ft
try:
    import flet_webview as fwv
    HAS_WEBVIEW = True
except ImportError:
    HAS_WEBVIEW = False
    print("⚠️  flet-webview not installed, using placeholder")
def main(page: ft.Page):
    page.title = "WebView Test"
    
    if HAS_WEBVIEW:
        content = fwv.WebView(
            url="https://www.google.com",
            expand=True,
        )
    else:
        content = ft.Column([
            ft.Text("WebView would appear here", size=20),
            ft.Text("Install: pip install flet-webview", color="grey"),
        ])
    
    page.add(content)
if __name__ == "__main__":
    ft.app(target=main)
