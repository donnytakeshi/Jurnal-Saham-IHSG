from __future__ import annotations

import argparse
import sys
from pathlib import Path

# Allow running as a standalone script: make workspace root importable
WORKSPACE_ROOT = Path(__file__).resolve().parents[1]
if str(WORKSPACE_ROOT) not in sys.path:
    sys.path.insert(0, str(WORKSPACE_ROOT))

from modules.orderbook_override import parse_pasted_orderbook_text, save_override_json


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(
        description=(
            'Convert copy/pasted orderbook text into data/orderbook_overrides/<SYMBOL>.json\n\n'
            'Expected per-row format (header optional):\n'
            '  Freq  Lot  Bid  Ask  Lot  Freq\n'
            'Paste your rows into stdin, then press Ctrl+D.'
        )
    )
    p.add_argument('--symbol', required=True, help='Ticker symbol, e.g. BBCA')
    p.add_argument('--levels', type=int, default=5, help='Number of levels to keep (default: 5)')
    p.add_argument('--file', type=str, default='', help='Read paste text from file instead of stdin')
    args = p.parse_args(argv)

    if args.file:
        text = Path(args.file).read_text(encoding='utf-8')
    else:
        text = sys.stdin.read()

    parsed = parse_pasted_orderbook_text(text, levels=args.levels)
    if not parsed.bid_orders and not parsed.ask_orders:
        print('No orderbook rows detected. Paste rows like: Freq Lot Bid Ask Lot Freq', file=sys.stderr)
        return 2

    out_path = save_override_json(args.symbol, parsed)
    print(str(out_path))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
