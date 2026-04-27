"""Tabs package - Import semua tabs"""

from app.tabs.watchlist import WatchlistTab
from app.tabs.top10 import DashboardTab
from app.tabs.jurnal import JurnalTab
from app.tabs.screening import ScreeningTab
from app.tabs.cek_emiten import CekSahamTab
from app.tabs.ai_chat import AIChatTab

__all__ = ['WatchlistTab', 'DashboardTab', 'JurnalTab', 'ScreeningTab', 'CekSahamTab', 'AIChatTab']
