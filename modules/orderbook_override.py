from __future__ import annotations

import json
import re
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def _workspace_root() -> Path:
    # modules/ -> workspace root
    return Path(__file__).resolve().parents[1]


def default_override_dir() -> Path:
    return _workspace_root() / 'data' / 'orderbook_overrides'


def _digits_int(value: Any) -> int | None:
    if value is None:
        return None
    if isinstance(value, bool):
        return int(value)
    if isinstance(value, int):
        return value
    if isinstance(value, float):
        return int(value)
    s = str(value).strip()
    if not s:
        return None
    digits = ''.join(ch for ch in s if ch.isdigit())
    if not digits:
        return None
    try:
        return int(digits)
    except Exception:
        return None


def _to_level_dict(obj: Any) -> dict[str, int | None]:
    # Normalize to {price, volume, freq}
    if obj is None:
        return {'price': None, 'volume': None, 'freq': None}
    if isinstance(obj, dict):
        return {
            'price': _digits_int(obj.get('price')),
            'volume': _digits_int(obj.get('volume', obj.get('lot'))),
            'freq': _digits_int(obj.get('freq', obj.get('count', obj.get('orders')))),
        }
    if isinstance(obj, (list, tuple)):
        return {
            'price': _digits_int(obj[0]) if len(obj) > 0 else None,
            'volume': _digits_int(obj[1]) if len(obj) > 1 else None,
            'freq': _digits_int(obj[2]) if len(obj) > 2 else None,
        }
    return {'price': None, 'volume': None, 'freq': None}


def load_orderbook_override(symbol: str, override_dir: str | Path | None = None) -> dict[str, Any] | None:
    """Load manual orderbook override for a symbol.

    Expected file path:
      data/orderbook_overrides/<SYMBOL>.json

    Returns a dict compatible with the UI renderer in desktop_app.py.bak:
      {"bid_orders": [...], "ask_orders": [...]}
    """

    s = (symbol or '').strip().upper()
    if not s:
        return None

    base = Path(override_dir) if override_dir is not None else default_override_dir()
    path = base / f'{s}.json'
    if not path.exists() or not path.is_file():
        return None

    try:
        raw = json.loads(path.read_text(encoding='utf-8'))
    except Exception:
        return None

    if not isinstance(raw, dict):
        return None

    bids_raw = raw.get('bid_orders') or raw.get('bids') or raw.get('bid') or []
    asks_raw = raw.get('ask_orders') or raw.get('asks') or raw.get('ask') or []

    if not isinstance(bids_raw, list) or not isinstance(asks_raw, list):
        return None

    bid_orders = [_to_level_dict(x) for x in bids_raw]
    ask_orders = [_to_level_dict(x) for x in asks_raw]

    # Drop empty levels (all None)
    bid_orders = [x for x in bid_orders if any(v is not None for v in x.values())]
    ask_orders = [x for x in ask_orders if any(v is not None for v in x.values())]

    if not bid_orders and not ask_orders:
        return None

    return {
        'source': 'override',
        'symbol': s,
        'bid_orders': bid_orders,
        'ask_orders': ask_orders,
        'as_of': raw.get('as_of') or raw.get('timestamp') or None,
    }


_NUM_RE = re.compile(r'\d[\d.,]*')


@dataclass(frozen=True)
class ParsedOrderbook:
    bid_orders: list[dict[str, int | None]]
    ask_orders: list[dict[str, int | None]]


def parse_pasted_orderbook_text(text: str, levels: int = 5) -> ParsedOrderbook:
    """Parse copy/pasted orderbook rows.

    Supports common 6-column format per row (header optional):
      Freq  Lot  Bid  Ask  Lot  Freq

    Each row should contain 6 numbers. If a leading level index exists (7 numbers),
    it will be ignored.
    """

    lines = [ln.strip() for ln in (text or '').splitlines()]
    lines = [ln for ln in lines if ln]

    bid_orders: list[dict[str, int | None]] = []
    ask_orders: list[dict[str, int | None]] = []

    for ln in lines:
        nums = _NUM_RE.findall(ln)
        if not nums:
            continue

        # Heuristic: drop a leading level index (1..20) if present.
        if len(nums) == 7:
            maybe_idx = _digits_int(nums[0])
            if maybe_idx is not None and 1 <= maybe_idx <= 50:
                nums = nums[1:]

        if len(nums) < 6:
            continue
        if len(nums) > 6:
            nums = nums[-6:]

        left_freq = _digits_int(nums[0])
        bid_lot = _digits_int(nums[1])
        bid_px = _digits_int(nums[2])
        ask_px = _digits_int(nums[3])
        ask_lot = _digits_int(nums[4])
        right_freq = _digits_int(nums[5])

        bid_orders.append({'price': bid_px, 'volume': bid_lot, 'freq': left_freq})
        ask_orders.append({'price': ask_px, 'volume': ask_lot, 'freq': right_freq})

        if len(bid_orders) >= int(levels) and len(ask_orders) >= int(levels):
            break

    return ParsedOrderbook(bid_orders=bid_orders[: int(levels)], ask_orders=ask_orders[: int(levels)])


def save_override_json(
    symbol: str,
    parsed: ParsedOrderbook,
    override_dir: str | Path | None = None,
    source: str = 'manual_paste',
) -> Path:
    s = (symbol or '').strip().upper()
    if not s:
        raise ValueError('symbol is required')

    base = Path(override_dir) if override_dir is not None else default_override_dir()
    base.mkdir(parents=True, exist_ok=True)
    path = base / f'{s}.json'

    payload = {
        'symbol': s,
        'source': source,
        'as_of': datetime.now(timezone.utc).isoformat(),
        'bid_orders': parsed.bid_orders,
        'ask_orders': parsed.ask_orders,
    }
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding='utf-8')
    return path
