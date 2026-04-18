from __future__ import annotations

from dataclasses import dataclass
from typing import Any


def normalize_symbol(sym: str) -> str:
    s = (sym or "").strip().upper()
    if s.endswith(":IDX"):
        s = s.split(":", 1)[0]
    if s.endswith(".JK"):
        s = s[:-3]
    s = "".join(ch for ch in s if ch.isalnum() or ch in ("-", "_"))
    return s


@dataclass(frozen=True)
class Quote:
    symbol: str
    price: float | None = None
    prev_close: float | None = None
    open: float | None = None
    high: float | None = None
    low: float | None = None
    volume: float | None = None
    change_pct: float | None = None
    change_abs: float | None = None
    source: str = ""

    def as_dict(self) -> dict[str, Any]:
        return {
            "symbol": self.symbol,
            "price": self.price,
            "prev_close": self.prev_close,
            "open": self.open,
            "high": self.high,
            "low": self.low,
            "volume": self.volume,
            "change": self.change_pct,
            "change_abs": self.change_abs,
            "source": self.source,
        }


def _quote_from_tradingview(sym: str, d: dict[str, Any]) -> Quote | None:
    try:
        s = normalize_symbol(sym)
        if not s:
            return None
        price = d.get("price")
        open_ = d.get("open")
        high = d.get("high")
        low = d.get("low")
        volume = d.get("volume")
        change_pct = d.get("change")
        change_abs = d.get("change_abs")

        price_f = float(price) if price not in (None, "", "-") else None
        open_f = float(open_) if open_ not in (None, "", "-") else None
        high_f = float(high) if high not in (None, "", "-") else None
        low_f = float(low) if low not in (None, "", "-") else None
        vol_f = float(volume) if volume not in (None, "", "-") else None
        chg_pct_f = float(change_pct) if change_pct not in (None, "", "-") else None
        chg_abs_f = float(change_abs) if change_abs not in (None, "", "-") else None

        prev_close = None
        if price_f is not None and chg_abs_f is not None:
            prev_close = price_f - chg_abs_f

        if price_f is None:
            return None

        return Quote(
            symbol=s,
            price=price_f,
            prev_close=prev_close,
            open=open_f,
            high=high_f,
            low=low_f,
            volume=vol_f,
            change_pct=chg_pct_f,
            change_abs=chg_abs_f,
            source="tradingview",
        )
    except Exception:
        return None


def fetch_quotes_tradingview(symbols: list[str]) -> dict[str, Quote]:
    if not symbols:
        return {}
    try:
        from modules.tradingview_fetcher import fetch_tradingview_snapshot

        snap = fetch_tradingview_snapshot([normalize_symbol(s) for s in symbols if s])
    except Exception:
        snap = {}

    out: dict[str, Quote] = {}
    if not isinstance(snap, dict):
        return out

    for sym, d in snap.items():
        if not isinstance(d, dict):
            continue
        q = _quote_from_tradingview(sym, d)
        if q is None:
            continue
        out[q.symbol] = q
    return out


def fetch_quotes_yfinance(symbols: list[str]) -> dict[str, Quote]:
    if not symbols:
        return {}

    # yfinance expects IDX tickers as .JK
    syms = [normalize_symbol(s) for s in symbols if s]
    tickers = [f"{s}.JK" for s in syms if s]
    if not tickers:
        return {}

    out: dict[str, Quote] = {}

    try:
        import yfinance as yf

        df = yf.download(
            tickers=tickers,
            period="5d",
            interval="1d",
            group_by="ticker",
            auto_adjust=False,
            threads=True,
            progress=False,
        )
    except Exception:
        return out

    # df can be:
    # - MultiIndex columns when many tickers (ticker -> OHLCV)
    # - Single ticker columns when one ticker
    try:
        import pandas as pd

        if df is None or getattr(df, "empty", True):
            return out

        if isinstance(df.columns, pd.MultiIndex):
            for t in tickers:
                if t not in df.columns.get_level_values(0):
                    continue
                sub = df[t].dropna(how="all")
                if sub is None or sub.empty:
                    continue
                _apply_yf_frame(out, t, sub)
        else:
            # single ticker
            sub = df.dropna(how="all")
            if sub is not None and not sub.empty:
                _apply_yf_frame(out, tickers[0], sub)

    except Exception:
        return out

    return out


def _apply_yf_frame(out: dict[str, Quote], ticker: str, sub) -> None:
    try:
        import math

        base = normalize_symbol(ticker.replace(".JK", ""))
        if not base:
            return

        # Use last available row as current.
        last = sub.iloc[-1]
        prev = sub.iloc[-2] if len(sub.index) >= 2 else None

        close = float(last.get("Close")) if last.get("Close") is not None else None
        open_ = float(last.get("Open")) if last.get("Open") is not None else None
        high = float(last.get("High")) if last.get("High") is not None else None
        low = float(last.get("Low")) if last.get("Low") is not None else None
        vol = float(last.get("Volume")) if last.get("Volume") is not None else None

        prev_close = None
        if prev is not None:
            try:
                prev_close = float(prev.get("Close")) if prev.get("Close") is not None else None
            except Exception:
                prev_close = None

        change_abs = None
        change_pct = None
        if close is not None and prev_close not in (None, 0):
            change_abs = close - float(prev_close)
            change_pct = (change_abs / float(prev_close)) * 100.0

        # Guard against NaN
        def _nan_to_none(x):
            try:
                if x is None:
                    return None
                if isinstance(x, float) and math.isnan(x):
                    return None
                return x
            except Exception:
                return None

        q = Quote(
            symbol=base,
            price=_nan_to_none(close),
            prev_close=_nan_to_none(prev_close),
            open=_nan_to_none(open_),
            high=_nan_to_none(high),
            low=_nan_to_none(low),
            volume=_nan_to_none(vol),
            change_pct=_nan_to_none(change_pct),
            change_abs=_nan_to_none(change_abs),
            source="yfinance",
        )

        if q.price is None:
            return
        out[q.symbol] = q
    except Exception:
        return


def fetch_quotes(symbols: list[str]) -> dict[str, dict[str, Any]]:
    """Fetch best-effort quotes.

    Strategy:
    - TradingView for all symbols (fast)
    - yfinance only for missing symbols

    Returns: dict {SYM: {price/open/low/high/volume/change/change_abs/prev_close/source}}
    """

    syms = [normalize_symbol(s) for s in (symbols or []) if s]
    syms = [s for s in syms if s]
    if not syms:
        return {}

    tv = fetch_quotes_tradingview(syms)
    missing = [s for s in syms if s not in tv]
    yf = fetch_quotes_yfinance(missing) if missing else {}

    merged: dict[str, dict[str, Any]] = {}
    for s in syms:
        q = tv.get(s) or yf.get(s)
        if q is None:
            continue
        merged[s] = q.as_dict()
    return merged
