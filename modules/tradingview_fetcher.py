import requests

TRADINGVIEW_SCAN_URL = "https://scanner.tradingview.com/indonesia/scan"

# Contoh: fetch_tradingview_snapshot(["BBCA", "BBRI", "TLKM"])
def fetch_tradingview_snapshot(symbols):
    """
    Ambil snapshot harga saham dari TradingView (OHLCV, change, dsb).
    symbols: list kode saham, misal ["BBCA", "BBRI"]
    Return: dict { 'BBCA': {...}, ... }
    """
    if not symbols:
        return {}
    tickers = [f"IDX:{s.upper()}" for s in symbols]
    payload = {
        "symbols": {"tickers": tickers, "query": {"types": []}},
        "columns": [
            "name", "open", "high", "low", "close", "volume", "change", "change_abs"
        ],
    }
    headers = {
        "User-Agent": "Mozilla/5.0 (Android) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120 Safari/537.36",
        "Accept": "application/json",
        "Content-Type": "application/json",
    }
    try:
        resp = requests.post(TRADINGVIEW_SCAN_URL, json=payload, headers=headers, timeout=15)
        resp.raise_for_status()
        data = resp.json() or {}
    except Exception as e:
        print('fetch_tradingview_snapshot error:', e)
        return {}
    rows = data.get("data") or []
    out = {}
    for r in rows:
        try:
            sym = (r.get("s") or "").upper().strip()
            d = r.get("d") or []
            base = sym.split(":", 1)[1] if ":" in sym else sym
            base = base.split(".", 1)[0]
            if not base:
                continue
            o = float(d[1]) if len(d) > 1 and d[1] is not None else None
            h = float(d[2]) if len(d) > 2 and d[2] is not None else None
            l = float(d[3]) if len(d) > 3 and d[3] is not None else None
            c = float(d[4]) if len(d) > 4 and d[4] is not None else None
            vol = float(d[5]) if len(d) > 5 and d[5] is not None else None
            chg = float(d[6]) if len(d) > 6 and d[6] is not None else None
            chg_abs = float(d[7]) if len(d) > 7 and d[7] is not None else None
            if c is None or c <= 0:
                continue
            out[base] = {
                "price": float(c),
                "open": float(o) if o is not None else float(c),
                "high": float(h) if h is not None else float(c),
                "low": float(l) if l is not None else float(c),
                "close": float(c),
                "volume": float(vol) if vol is not None else 0.0,
                "change": float(chg) if chg is not None else None,
                "change_abs": float(chg_abs) if chg_abs is not None else None,
            }
        except Exception:
            continue
    return out


def fetch_tradingview_idx_market_aggregate(max_rows: int = 500):
    """Best-effort aggregate for IDX market from TradingView screener.

    Returns dict with keys: lot, value, freq, symbols.
    - lot: sum(volume)/100
    - value: sum(close*volume)
    - freq: sum(trades/transactions) if column exists, else None
    - symbols: number of rows used

    Notes:
    - TradingView scanner fields differ by market; this function is defensive.
    - This is an approximation intended for UI summary cards.
    """
    try:
        max_rows = int(max_rows)
    except Exception:
        max_rows = 500
    max_rows = max(50, min(2000, max_rows))

    headers = {
        "User-Agent": "Mozilla/5.0 (Android) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120 Safari/537.36",
        "Accept": "application/json",
        "Content-Type": "application/json",
    }

    # NOTE: On the Indonesia scanner endpoint, unknown fields cause HTTP 400.
    # Keep columns minimal/safe to avoid breaking the welcome page.
    columns = ["name", "close", "volume"]

    payload = {
        "symbols": {"query": {"types": ["stock"]}},
        "columns": columns,
        "sort": {"sortBy": "volume", "sortOrder": "desc"},
        "range": [0, max_rows],
    }

    try:
        resp = requests.post(TRADINGVIEW_SCAN_URL, json=payload, headers=headers, timeout=20)
        resp.raise_for_status()
        data = resp.json() or {}
    except Exception:
        return {"lot": None, "value": None, "freq": None, "symbols": 0}

    if not isinstance(data, dict) or not data.get("data"):
        return {"lot": None, "value": None, "freq": None, "symbols": 0}

    rows = data.get("data") or []
    close_i = 1
    vol_i = 2
    vol_sum = 0.0
    value_sum = 0.0
    used = 0

    for r in rows:
        try:
            d = r.get("d") or []
            c = d[close_i] if len(d) > close_i else None
            v = d[vol_i] if len(d) > vol_i else None
            if c is None or v is None:
                continue
            c = float(c)
            v = float(v)
            if c <= 0 or v <= 0:
                continue
            used += 1
            vol_sum += v
            value_sum += (c * v)
        except Exception:
            continue

    lot = (vol_sum / 100.0) if vol_sum > 0 else None
    value = value_sum if value_sum > 0 else None
    return {"lot": lot, "value": value, "freq": None, "symbols": int(used)}


def fetch_tradingview_idx_penny_gainers(limit: int = 15, price_max: float = 500.0, change_min: float = 2.0, scan_rows: int = 650):
    """Fetch a list of cheap gainers from IDX via TradingView screener.

    Best-effort:
    - Uses TradingView Indonesia scan endpoint.
    - Sorts by percent change descending.
    - Filters rows where close <= price_max and change >= change_min.

    Returns: list of dicts [{symbol, close, change}]

    Notes:
    - TradingView `change` reflects the latest session change vs prev close.
      If the market is closed, this typically corresponds to the previous trading day.
    """
    try:
        limit = int(limit)
    except Exception:
        limit = 15
    limit = max(1, min(50, limit))

    try:
        price_max = float(price_max)
    except Exception:
        price_max = 500.0

    try:
        change_min = float(change_min)
    except Exception:
        change_min = 2.0

    try:
        scan_rows = int(scan_rows)
    except Exception:
        scan_rows = 650
    scan_rows = max(50, min(2000, scan_rows))

    headers = {
        "User-Agent": "Mozilla/5.0 (Android) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120 Safari/537.36",
        "Accept": "application/json",
        "Content-Type": "application/json",
    }

    payload = {
        "symbols": {"query": {"types": ["stock"]}},
        "columns": ["name", "close", "change"],
        "sort": {"sortBy": "change", "sortOrder": "desc"},
        "range": [0, scan_rows],
    }

    try:
        resp = requests.post(TRADINGVIEW_SCAN_URL, json=payload, headers=headers, timeout=20)
        resp.raise_for_status()
        data = resp.json() or {}
    except Exception:
        return []

    rows = data.get("data") or []
    out = []
    for r in rows:
        if len(out) >= limit:
            break
        try:
            s = (r.get("s") or "").upper().strip()
            d = r.get("d") or []
            if not s or len(d) < 3:
                continue
            base = s.split(":", 1)[1] if ":" in s else s
            base = base.split(".", 1)[0]
            close = float(d[1])
            chg = float(d[2])
            if close <= 0:
                continue
            if close > price_max:
                continue
            if chg < change_min:
                continue
            out.append({"symbol": base, "close": close, "change": chg})
        except Exception:
            continue
    return out
