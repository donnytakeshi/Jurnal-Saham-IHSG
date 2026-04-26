"""
main_webview.py - WebView untuk menampilkan HTML dari StitchWithGoogle
"""

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.clock import Clock
from kivy.utils import platform


class WebViewApp(App):
    def build(self):
        self.root = BoxLayout()
        
        if platform == 'android':
            from android.runnable import run_on_ui_thread
            from jnius import autoclass
            
            self.WebView = autoclass('android.webkit.WebView')
            self.WebViewClient = autoclass('android.webkit.WebViewClient')
            self.activity = autoclass('org.kivy.android.PythonActivity').mActivity
            
            Clock.schedule_once(self.create_webview, 0.1)
        else:
            from kivy.uix.label import Label
            self.root.add_widget(Label(text="WebView hanya berjalan di Android\nGunakan browser untuk preview HTML"))
        
        return self.root
    
    @run_on_ui_thread
    def create_webview(self, dt):
        webview = self.WebView(self.activity)
        settings = webview.getSettings()
        settings.setJavaScriptEnabled(True)
        settings.setDomStorageEnabled(True)
        webview.setWebViewClient(self.WebViewClient())
        
        # Load HTML dari assets
        webview.loadUrl("file:///android_asset/index.html")
        self.activity.setContentView(webview)


if __name__ == '__main__':
    WebViewApp().run()
