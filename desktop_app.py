# --- Stockbit-style Bottom Navigation App ---

from kivy.app import App
from kivy.uix.anchorlayout import AnchorLayout

def ui_dp(value: float) -> float:
  return dp(value * UI_SCALE)

def ui_sp(value: float) -> float:
  return sp(value * UI_SCALE)

# Prefer Roboto (bundled with Kivy) for consistent look.
try:
  from kivy.core.text import LabelBase
  from kivy.resources import resource_find

  _roboto_regular = resource_find('data/fonts/Roboto-Regular.ttf')
  _roboto_medium = resource_find('data/fonts/Roboto-Medium.ttf')
  _roboto_bold = resource_find('data/fonts/Roboto-Bold.ttf')
  if _roboto_regular:
    LabelBase.register(
      name='SBRoboto',
      fn_regular=_roboto_regular,
      fn_bold=_roboto_bold or _roboto_regular,
      fn_italic=_roboto_regular,
      fn_bolditalic=_roboto_bold or _roboto_regular,
    )
    DEFAULT_FONT = 'SBRoboto'
  else:
    DEFAULT_FONT = None
except Exception:
  DEFAULT_FONT = None

def _font_kwargs():
  return {'font_name': DEFAULT_FONT} if DEFAULT_FONT else {}

# Android entry point: launch Kivy app
from desktop_app_bak import MainStockbitApp

if __name__ == '__main__':
    MainStockbitApp().run()
