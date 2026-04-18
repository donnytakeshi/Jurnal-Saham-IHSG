from __future__ import annotations

import json
from dataclasses import dataclass, asdict
from datetime import date
from pathlib import Path
from typing import Any, Iterable


DATA_DIR = Path("data") / "jurnal"
TX_FILE = DATA_DIR / "transactions.json"
HOLD_FILE = DATA_DIR / "holdings_override.json"
DIV_FILE = DATA_DIR / "dividends.json"

# IDX stocks: 1 lot = 100 shares
LOT_SIZE = 100


@dataclass(frozen=True)
class Transaction:
    tx_date: str  # YYYY-MM-DD
    symbol: str
    side: str  # BUY|SELL
    qty: float
    price: float

    @property
    def value(self) -> float:
        # qty is stored in LOT
        return float(self.qty) * float(LOT_SIZE) * float(self.price)


@dataclass(frozen=True)
class Dividend:
    div_date: str  # YYYY-MM-DD
    symbol: str
    amount: float


@dataclass(frozen=True)
class HoldingOverride:
    symbol: str
    qty: float  # LOT
    avg_price: float


@dataclass(frozen=True)
class Position:
    symbol: str
    qty: float  # LOT
    avg_price: float


def _ensure_dir() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)


def _atomic_write_json(path: Path, payload: Any) -> None:
    _ensure_dir()
    tmp = path.with_suffix(path.suffix + ".tmp")
    with tmp.open("w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)
    tmp.replace(path)


def load_transactions() -> list[Transaction]:
    try:
        if not TX_FILE.exists():
            return []
        with TX_FILE.open("r", encoding="utf-8") as f:
            raw = json.load(f)
        if not isinstance(raw, list):
            return []
        items: list[Transaction] = []
        for it in raw:
            if not isinstance(it, dict):
                continue
            try:
                tx = Transaction(
                    tx_date=str(it.get("tx_date") or ""),
                    symbol=str(it.get("symbol") or "").upper().strip(),
                    side=str(it.get("side") or "").upper().strip(),
                    qty=float(it.get("qty") or 0.0),
                    price=float(it.get("price") or 0.0),
                )
            except Exception:
                continue
            if not tx.tx_date:
                continue
            if not tx.symbol:
                continue
            if tx.side not in {"BUY", "SELL"}:
                continue
            if tx.qty <= 0 or tx.price <= 0:
                continue
            items.append(tx)
        return items
    except Exception:
        return []


def save_transactions(items: Iterable[Transaction]) -> None:
    payload = [asdict(x) for x in items]
    _atomic_write_json(TX_FILE, payload)


def delete_transaction(tx: Transaction) -> bool:
    items = load_transactions()
    try:
        items.remove(tx)
    except ValueError:
        return False
    save_transactions(items)
    return True


def replace_transaction(old: Transaction, new: Transaction) -> bool:
    items = load_transactions()
    try:
        idx = items.index(old)
    except ValueError:
        return False
    items[idx] = new
    save_transactions(items)
    return True


def load_holdings_override() -> dict[str, HoldingOverride]:
    try:
        if not HOLD_FILE.exists():
            return {}
        with HOLD_FILE.open("r", encoding="utf-8") as f:
            raw = json.load(f)
        if not isinstance(raw, list):
            return {}
        out: dict[str, HoldingOverride] = {}
        for it in raw:
            if not isinstance(it, dict):
                continue
            sym = str(it.get("symbol") or "").upper().strip()
            try:
                qty = float(it.get("qty") or 0.0)
                avg = float(it.get("avg_price") or 0.0)
            except Exception:
                continue
            if not sym or qty < 0 or avg < 0:
                continue
            out[sym] = HoldingOverride(symbol=sym, qty=qty, avg_price=avg)
        return out
    except Exception:
        return {}


def save_holdings_override(items: Iterable[HoldingOverride]) -> None:
    payload = [asdict(x) for x in items]
    _atomic_write_json(HOLD_FILE, payload)


def set_holding_override(*, symbol: str, qty: float, avg_price: float) -> HoldingOverride:
    sym = str(symbol).upper().strip()
    ov = HoldingOverride(symbol=sym, qty=float(qty), avg_price=float(avg_price))
    items = load_holdings_override()
    items[sym] = ov
    save_holdings_override(items.values())
    return ov


def delete_holding_override(symbol: str) -> bool:
    sym = str(symbol).upper().strip()
    items = load_holdings_override()
    if sym not in items:
        return False
    del items[sym]
    save_holdings_override(items.values())
    return True


def compute_positions_from_transactions(transactions: Iterable[Transaction]) -> dict[str, Position]:
    # Average-cost method (weighted average). SELL reduces qty; avg stays.
    qty_shares: dict[str, float] = {}
    avg_price: dict[str, float] = {}
    for tx in transactions:
        sym = tx.symbol
        q = float(tx.qty) * float(LOT_SIZE)
        p = float(tx.price)
        cur_q = float(qty_shares.get(sym, 0.0) or 0.0)
        cur_avg = float(avg_price.get(sym, 0.0) or 0.0)
        if tx.side == "BUY":
            new_q = cur_q + q
            if new_q > 0:
                new_avg = ((cur_q * cur_avg) + (q * p)) / new_q
            else:
                new_avg = 0.0
            qty_shares[sym] = new_q
            avg_price[sym] = new_avg
        else:  # SELL
            new_q = max(0.0, cur_q - q)
            qty_shares[sym] = new_q
            if new_q <= 0:
                avg_price[sym] = 0.0

    out: dict[str, Position] = {}
    for sym, qshares in qty_shares.items():
        out[sym] = Position(
            symbol=sym,
            qty=float(qshares) / float(LOT_SIZE),
            avg_price=float(avg_price.get(sym, 0.0) or 0.0),
        )
    return out


def compute_portfolio(*, transactions: Iterable[Transaction], overrides: dict[str, HoldingOverride] | None = None) -> dict[str, Position]:
    base = compute_positions_from_transactions(transactions)
    if overrides:
        for sym, ov in overrides.items():
            base[sym] = Position(symbol=sym, qty=float(ov.qty), avg_price=float(ov.avg_price))
    return base


def add_transaction(
    *,
    symbol: str,
    side: str,
    qty: float,
    price: float,
    tx_date: str | None = None,
) -> Transaction:
    if tx_date is None:
        tx_date = date.today().isoformat()

    tx = Transaction(
        tx_date=str(tx_date),
        symbol=str(symbol).upper().strip(),
        side=str(side).upper().strip(),
        qty=float(qty),
        price=float(price),
    )

    items = load_transactions()
    items.append(tx)
    save_transactions(items)
    return tx


def _parse_tx_date(s: str) -> date | None:
    try:
        if not s:
            return None
        parts = str(s).split("-")
        if len(parts) != 3:
            return None
        y, m, d = int(parts[0]), int(parts[1]), int(parts[2])
        return date(y, m, d)
    except Exception:
        return None


def filter_transactions_by_month(transactions: Iterable[Transaction], year: int, month: int) -> list[Transaction]:
    out: list[Transaction] = []
    for tx in transactions:
        dt = _parse_tx_date(tx.tx_date)
        if not dt:
            continue
        if dt.year == int(year) and dt.month == int(month):
            out.append(tx)
    return out


def load_dividends() -> list[Dividend]:
    try:
        if not DIV_FILE.exists():
            return []
        with DIV_FILE.open("r", encoding="utf-8") as f:
            raw = json.load(f)
        if not isinstance(raw, list):
            return []

        items: list[Dividend] = []
        for it in raw:
            if not isinstance(it, dict):
                continue
            try:
                d = Dividend(
                    div_date=str(it.get("div_date") or ""),
                    symbol=str(it.get("symbol") or "").upper().strip(),
                    amount=float(it.get("amount") or 0.0),
                )
            except Exception:
                continue
            if not d.div_date:
                continue
            if not d.symbol:
                continue
            if d.amount <= 0:
                continue
            if _parse_tx_date(d.div_date) is None:
                continue
            items.append(d)
        return items
    except Exception:
        return []


def save_dividends(items: Iterable[Dividend]) -> None:
    payload = [asdict(x) for x in items]
    _atomic_write_json(DIV_FILE, payload)


def add_dividend(*, symbol: str, amount: float, div_date: str | None = None) -> Dividend:
    if div_date is None:
        div_date = date.today().isoformat()
    d = Dividend(
        div_date=str(div_date),
        symbol=str(symbol).upper().strip(),
        amount=float(amount),
    )
    items = load_dividends()
    items.append(d)
    save_dividends(items)
    return d


def filter_dividends_by_month(dividends: Iterable[Dividend], year: int, month: int) -> list[Dividend]:
    out: list[Dividend] = []
    for d in dividends:
        dt = _parse_tx_date(d.div_date)
        if not dt:
            continue
        if dt.year == int(year) and dt.month == int(month):
            out.append(d)
    return out


def compute_monthly_performance(transactions: Iterable[Transaction], year: int, month: int) -> dict[str, float]:
    """Compute realized PnL + win rate for a month.

    Assumptions:
    - qty is LOT; 1 lot = LOT_SIZE shares
    - average-cost method for cost basis
    - a 'trade' is counted on each SELL execution within the month
    """
    txs = list(transactions)
    txs.sort(key=lambda t: (t.tx_date, t.symbol, t.side))

    # Track shares + avg cost per share.
    shares: dict[str, float] = {}
    avg_cost: dict[str, float] = {}

    realized_pnl = 0.0
    trade_count = 0.0
    win_count = 0.0

    target_y = int(year)
    target_m = int(month)
    last_dt_in_month: date | None = None

    for tx in txs:
        dt = _parse_tx_date(tx.tx_date)
        if not dt:
            continue
        if dt.year > target_y or (dt.year == target_y and dt.month > target_m):
            # stop after month ends (inputs are sorted)
            break

        sym = tx.symbol
        q_shares = float(tx.qty) * float(LOT_SIZE)
        price = float(tx.price)
        cur_sh = float(shares.get(sym, 0.0) or 0.0)
        cur_avg = float(avg_cost.get(sym, 0.0) or 0.0)

        if tx.side == "BUY":
            new_sh = cur_sh + q_shares
            if new_sh > 0:
                new_avg = ((cur_sh * cur_avg) + (q_shares * price)) / new_sh
            else:
                new_avg = 0.0
            shares[sym] = new_sh
            avg_cost[sym] = new_avg
        else:  # SELL
            sell_sh = min(cur_sh, q_shares)
            if sell_sh > 0:
                pnl = (price - cur_avg) * sell_sh
                new_sh = cur_sh - sell_sh
                shares[sym] = new_sh
                if new_sh <= 0:
                    avg_cost[sym] = 0.0

                if dt.year == target_y and dt.month == target_m:
                    realized_pnl += pnl
                    trade_count += 1.0
                    if pnl > 0:
                        win_count += 1.0

        if dt.year == target_y and dt.month == target_m:
            if last_dt_in_month is None or dt > last_dt_in_month:
                last_dt_in_month = dt

    # holding count at end of month
    holding_count = 0.0
    for sym, sh in shares.items():
        if sh > 0:
            holding_count += 1.0

    win_rate = (win_count / trade_count) * 100.0 if trade_count > 0 else 0.0
    return {
        "realized_pnl": float(realized_pnl),
        "win_rate": float(win_rate),
        "holding_count": float(holding_count),
        "trade_count": float(trade_count),
        "win_count": float(win_count),
    }
