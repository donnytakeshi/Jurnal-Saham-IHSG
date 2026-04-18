"""
SQLite Database module untuk Jurnal Saham IHSG
Manages portfolio, journal, dan screening results
"""

import sqlite3
import json
from datetime import datetime
from pathlib import Path
import csv

class JournalDatabase:
    """SQLite database untuk jurnal trading dengan support multiple users"""
    
    def __init__(self, db_path='data/saham_journal.db', user_id=None):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.conn = None
        self.user_id = user_id  # Current logged-in user
        self.init_db()

    def _effective_user_id(self, user_id=None):
        """Return a usable user id.

        Some frontends (e.g., Kivy native) operate without login. In that case we
        store data under a default local user id.
        """

        return user_id or self.user_id or 1
    
    def connect(self):
        """Connect to database"""
        self.conn = sqlite3.connect(str(self.db_path))
        self.conn.row_factory = sqlite3.Row
        return self.conn
    
    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.commit()
            self.conn.close()
            self.conn = None
    
    def init_db(self):
        """Initialize database tables"""
        conn = self.connect()
        cursor = conn.cursor()
        
        # Portfolio table - dengan user_id
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS portfolio (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                symbol TEXT NOT NULL,
                company_name TEXT,
                quantity INTEGER DEFAULT 0,
                avg_price REAL DEFAULT 0,
                current_price REAL DEFAULT 0,
                total_invested REAL DEFAULT 0,
                total_current_value REAL DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(user_id, symbol)
            )
        ''')
        
        # Journal/Transaction table - dengan user_id
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS journal (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                symbol TEXT NOT NULL,
                date DATE NOT NULL,
                action TEXT NOT NULL,
                quantity INTEGER NOT NULL,
                price REAL NOT NULL,
                total REAL NOT NULL,
                current_price REAL,
                profit_loss REAL,
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Lightweight migration: add missing columns for older DB files.
        try:
            cursor.execute("PRAGMA table_info(journal)")
            existing_cols = {row[1] for row in cursor.fetchall()}
            if "current_price" not in existing_cols:
                cursor.execute("ALTER TABLE journal ADD COLUMN current_price REAL")
            if "profit_loss" not in existing_cols:
                cursor.execute("ALTER TABLE journal ADD COLUMN profit_loss REAL")
        except Exception as e:
            print(f"Warning migrating journal schema: {e}")
        
        # Screening results cache - dengan user_id
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS screening_results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                symbol TEXT NOT NULL,
                company TEXT,
                price REAL,
                vwap REAL,
                distance REAL,
                phase TEXT,
                signal TEXT,
                divergence TEXT,
                strength REAL,
                scan_date DATE DEFAULT CURRENT_DATE,
                UNIQUE(user_id, symbol, scan_date)
            )
        ''')
        
        # Price history untuk tracking - dengan user_id
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS price_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                symbol TEXT NOT NULL,
                date DATE NOT NULL,
                open REAL,
                high REAL,
                low REAL,
                close REAL,
                volume INTEGER,
                UNIQUE(user_id, symbol, date)
            )
        ''')
        
        conn.commit()
        self.close()
    
    # ===== PORTFOLIO FUNCTIONS =====
    def add_portfolio_item(self, symbol, company_name, quantity=0, avg_price=0, user_id=None):
        """Add or update portfolio item"""
        user_id = self._effective_user_id(user_id)
        
        conn = self.connect()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT OR REPLACE INTO portfolio 
                (user_id, symbol, company_name, quantity, avg_price, updated_at)
                VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            ''', (user_id, symbol.upper(), company_name, quantity, avg_price))
            
            conn.commit()
            return True
        except Exception as e:
            print(f"Error adding portfolio item: {e}")
            return False
        finally:
            self.close()
    
    def get_portfolio(self, user_id=None):
        """Get all portfolio items for user"""
        user_id = self._effective_user_id(user_id)
        
        conn = self.connect()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM portfolio WHERE user_id = ? AND quantity > 0', (user_id,))
        rows = cursor.fetchall()
        self.close()
        
        return [dict(row) for row in rows]
    
    def get_portfolio_item(self, symbol, user_id=None):
        """Get specific portfolio item"""
        user_id = self._effective_user_id(user_id)
        
        conn = self.connect()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM portfolio WHERE user_id = ? AND symbol = ?', (user_id, symbol.upper()))
        row = cursor.fetchone()
        self.close()
        
        return dict(row) if row else None
    
    def update_portfolio_price(self, symbol, current_price, user_id=None):
        """Update current price for a portfolio item."""

        user_id = self._effective_user_id(user_id)
        conn = self.connect()
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE portfolio 
            SET current_price = ?, 
                total_current_value = quantity * ?,
                updated_at = CURRENT_TIMESTAMP
            WHERE user_id = ? AND symbol = ?
        ''', (current_price, current_price, user_id, symbol.upper()))
        
        conn.commit()
        self.close()
    
    def delete_portfolio_item(self, symbol, user_id=None):
        """Delete a portfolio item."""

        user_id = self._effective_user_id(user_id)
        conn = self.connect()
        cursor = conn.cursor()
        
        cursor.execute('DELETE FROM portfolio WHERE user_id = ? AND symbol = ?', (user_id, symbol.upper()))
        conn.commit()
        self.close()
    
    # ===== JOURNAL FUNCTIONS =====
    def add_journal_entry(
        self,
        symbol,
        date,
        action,
        quantity,
        price,
        notes='',
        user_id=None,
        current_price=None,
        profit_loss=None,
    ):
        """Add journal/transaction entry.

        Returns inserted row id on success, or False on failure.
        """

        user_id = self._effective_user_id(user_id)
        conn = self.connect()
        cursor = conn.cursor()
        
        # Normalize date to string for SQLite (avoids deprecated default adapters).
        try:
            if isinstance(date, datetime):
                date_value = date.date().isoformat()
            elif hasattr(date, "isoformat"):
                date_value = date.isoformat()
            else:
                date_value = date
        except Exception:
            date_value = date

        total = quantity * price
        
        try:
            cursor.execute('''
                INSERT INTO journal 
                (user_id, symbol, date, action, quantity, price, total, current_price, profit_loss, notes)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                user_id,
                symbol.upper(),
                date_value,
                action.upper(),
                quantity,
                price,
                total,
                current_price,
                profit_loss,
                notes,
            ))
            
            conn.commit()
            return cursor.lastrowid
        except Exception as e:
            print(f"Error adding journal entry: {e}")
            return False
        finally:
            self.close()
    
    def get_journal(self, symbol=None, limit=50, user_id=None):
        """Get journal entries."""

        user_id = self._effective_user_id(user_id)
        conn = self.connect()
        cursor = conn.cursor()
        
        if symbol:
            cursor.execute('''
                SELECT * FROM journal 
                WHERE user_id = ? AND symbol = ? 
                ORDER BY date DESC 
                LIMIT ?
            ''', (user_id, symbol.upper(), limit))
        else:
            cursor.execute('''
                SELECT * FROM journal 
                WHERE user_id = ?
                ORDER BY date DESC 
                LIMIT ?
            ''', (user_id, limit))
        
        rows = cursor.fetchall()
        self.close()
        
        return [dict(row) for row in rows]
    
    def delete_journal_entry(self, entry_id, user_id=None):
        """Delete journal entry."""

        user_id = self._effective_user_id(user_id)
        conn = self.connect()
        cursor = conn.cursor()
        
        cursor.execute('DELETE FROM journal WHERE user_id = ? AND id = ?', (user_id, entry_id))
        conn.commit()
        self.close()
    
    # ===== SCREENING RESULTS =====
    def save_screening_results(self, results_df, scan_date=None, user_id=None):
        """Save screening results to database."""

        user_id = self._effective_user_id(user_id)
        if scan_date is None:
            scan_date = datetime.now().date()
        
        conn = self.connect()
        cursor = conn.cursor()
        
        for _, row in results_df.iterrows():
            try:
                cursor.execute('''
                    INSERT OR REPLACE INTO screening_results
                    (user_id, symbol, company, price, vwap, distance, phase, signal, divergence, strength, scan_date)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    user_id,
                    row.get('symbol', '').upper(),
                    row.get('company', ''),
                    float(row.get('price', 0)),
                    float(row.get('vwap', 0)),
                    float(row.get('distance', 0)),
                    row.get('phase', ''),
                    row.get('signal', ''),
                    row.get('divergence', ''),
                    float(row.get('strength', 0)),
                    scan_date
                ))
            except Exception as e:
                print(f"Error saving screening result for {row.get('symbol')}: {e}")
        
        conn.commit()
        self.close()
    
    def get_screening_results(self, scan_date=None, phase=None, user_id=None):
        """Get screening results."""

        user_id = self._effective_user_id(user_id)
        conn = self.connect()
        cursor = conn.cursor()
        
        if scan_date is None:
            scan_date = datetime.now().date()
        
        if phase:
            cursor.execute('''
                SELECT * FROM screening_results 
                WHERE user_id = ? AND scan_date = ? AND phase = ? 
                ORDER BY distance DESC
            ''', (user_id, scan_date, phase))
        else:
            cursor.execute('''
                SELECT * FROM screening_results 
                WHERE user_id = ? AND scan_date = ? 
                ORDER BY distance DESC
            ''', (user_id, scan_date))
        
        rows = cursor.fetchall()
        self.close()
        
        return [dict(row) for row in rows]

    def get_latest_screening_date(self, user_id=None):
        """Return the latest scan_date available in screening_results (or None)."""

        user_id = self._effective_user_id(user_id)
        conn = self.connect()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT MAX(scan_date) AS max_date FROM screening_results WHERE user_id = ?",
            (user_id,),
        )
        row = cursor.fetchone()
        self.close()
        if not row:
            return None
        try:
            return row["max_date"]
        except Exception:
            return row[0]

    def get_screening_results_for_symbols(self, symbols, scan_date=None, user_id=None):
        """Get screening results for a subset of symbols.

        This is useful for lightweight UI refresh (e.g., Watchlist) without
        loading the entire day's screening table.
        """

        user_id = self._effective_user_id(user_id)
        conn = self.connect()
        cursor = conn.cursor()

        if scan_date is None:
            scan_date = datetime.now().date()

        try:
            syms = []
            for s in (symbols or []):
                if s is None:
                    continue
                sym = str(s).strip().upper()
                if sym and sym not in syms:
                    syms.append(sym)
        except Exception:
            syms = []

        if not syms:
            self.close()
            return []

        placeholders = ",".join(["?"] * len(syms))
        cursor.execute(
            f"SELECT * FROM screening_results WHERE user_id = ? AND scan_date = ? AND symbol IN ({placeholders})",
            (user_id, scan_date, *syms),
        )

        rows = cursor.fetchall()
        self.close()
        return [dict(row) for row in rows]
    
    # ===== EXPORT/IMPORT FUNCTIONS =====
    def export_to_csv(self, output_path='exports'):
        """Export portfolio and journal to CSV files"""
        Path(output_path).mkdir(exist_ok=True)
        
        # Export portfolio
        portfolio = self.get_portfolio()
        if portfolio:
            portfolio_file = f"{output_path}/portfolio_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            with open(portfolio_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=list(portfolio[0].keys()))
                writer.writeheader()
                writer.writerows(portfolio)
            print(f"✅ Portfolio exported: {portfolio_file}")
        
        # Export journal
        journal = self.get_journal(limit=10000)
        if journal:
            journal_file = f"{output_path}/journal_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            with open(journal_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=list(journal[0].keys()))
                writer.writeheader()
                writer.writerows(journal)
            print(f"✅ Journal exported: {journal_file}")
    
    def export_to_json(self, output_path='exports'):
        """Export all data to JSON"""
        Path(output_path).mkdir(exist_ok=True)
        
        data = {
            'portfolio': self.get_portfolio(),
            'journal': self.get_journal(limit=10000),
            'exported_at': datetime.now().isoformat()
        }
        
        json_file = f"{output_path}/backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(json_file, 'w') as f:
            json.dump(data, f, indent=2, default=str)
        
        print(f"✅ Data exported to JSON: {json_file}")
        return json_file
    
    def import_from_json(self, json_file):
        """Import data from JSON backup"""
        try:
            with open(json_file, 'r') as f:
                data = json.load(f)
            
            # Import portfolio
            for item in data.get('portfolio', []):
                self.add_portfolio_item(
                    item['symbol'],
                    item.get('company_name', ''),
                    item.get('quantity', 0),
                    item.get('avg_price', 0)
                )
            
            # Import journal
            for entry in data.get('journal', []):
                self.add_journal_entry(
                    entry['symbol'],
                    entry['date'],
                    entry['action'],
                    entry['quantity'],
                    entry['price'],
                    entry.get('notes', '')
                )
            
            print(f"✅ Data imported from: {json_file}")
            return True
        except Exception as e:
            print(f"❌ Error importing from JSON: {e}")
            return False

