#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🤖 AI Agent untuk Jurnal Screening Saham IHSG
Asisten pribadi yang bisa diajak ngobrol untuk mengelola aplikasi screening saham
"""

import os
import sys
import subprocess
import threading
import time
import json
from datetime import datetime
from pathlib import Path

# Lazy imports for dependencies
MODULES_AVAILABLE = False
DataFetcher = None
BandarmologyAnalyzer = None
OrderbookAnalyzer = None
pd = None
np = None

def load_dependencies():
    """Load all dependencies if available"""
    global MODULES_AVAILABLE, DataFetcher, BandarmologyAnalyzer, OrderbookAnalyzer, pd, np
    
    try:
        import pandas
        import numpy
        pd = pandas
        np = numpy
        
        from modules.data_fetcher import DataFetcher as DF
        from modules.bandarmology import BandarmologyAnalyzer as BA
        from modules.orderbook_analyzer import OrderbookAnalyzer as OA
        
        DataFetcher = DF
        BandarmologyAnalyzer = BA
        OrderbookAnalyzer = OA
        MODULES_AVAILABLE = True
    except ImportError as e:
        MODULES_AVAILABLE = False
        print(f"⚠️  Modules belum tersedia: {e}")
        print("   Jalankan 'python3 ai_agent.py setup' dulu untuk inisialisasi")

# Tambahkan path untuk import modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

class AIAgent:
    """
    AI Agent untuk membantu screening saham IHSG
    Bisa diajak ngobrol, menjalankan perintah, dan memberikan analisis
    """
    
    def __init__(self):
        self.name = "SahamBot 🤖"
        self.version = "1.0.0"
        self.commands = {
            "help": "Menampilkan daftar perintah",
            "list": "Daftar saham populer yang bisa di-cek",
            "scan": "Menjalankan screening saham",
            "rekomendasi": "Menampilkan rekomendasi hari ini",
            "cek [kode]": "Melihat detail saham (contoh: cek BBCA)",
            "cek [kode1,kode2,...]": "Cek multiple saham (contoh: cek BBCA,BBNI,UNTR)",
            "stockbit [kode]": "Ambil data dari Stockbit (contoh: stockbit BBCA)",
            "jalankan dashboard": "Membuka dashboard Streamlit",
            "status": "Cek status aplikasi",
            "belajar": "Tips belajar coding saham",
            "keluar": "Keluar dari AI Agent"
        }
        self.popular_stocks = [
            ('BBCA', 'Bank Central Asia'),
            ('BBNI', 'Bank Negara Indonesia'),
            ('BBRI', 'Bank Rakyat Indonesia'),
            ('BMRI', 'Bank Mandiri'),
            ('INTP', 'Indocement Tunggal Perkasa'),
            ('GGRM', 'Gudang Garam'),
            ('CPIN', 'Charoen Pokphand Indonesia'),
            ('UNTR', 'United Tractors'),
            ('TLKM', 'Telekomunikasi Indonesia'),
            ('PGAS', 'Perusahaan Gas Negara'),
        ]
        self.running = True
        self.dashboard_process = None
        self.last_scan = None
        
    def speak(self, text):
        """Bicara dengan user"""
        print(f"\n{self.name}: {text}")
        
    def listen(self):
        """Mendengar perintah user"""
        return input("\nAnda: ").strip().lower()
    
    def run_command(self, command):
        """Menjalankan perintah"""
        
        if command == "help" or command == "?":
            self.show_help()
            
        elif command == "list":
            self.show_stock_list()
            
        elif command == "scan":
            self.run_scan()
            
        elif command == "rekomendasi":
            self.show_recommendations()
            
        elif command.startswith("cek "):
            stock_codes = command[4:].upper().split(',')
            for stock_code in stock_codes:
                stock_code = stock_code.strip()
                self.check_stock(stock_code)
            
        elif command.startswith("stockbit "):
            stock_code = command[9:].upper()
            self.check_stockbit(stock_code)
            
        elif command == "jalankan dashboard" or command == "dashboard":
            self.launch_dashboard()
            
        elif command == "status":
            self.show_status()
            
        elif command == "belajar":
            self.teach_coding()
            
        elif command == "keluar" or command == "exit" or command == "quit":
            self.speak("Sampai jumpa! Selalu ingat manajemen risiko! 📈")
            self.running = False
            
        else:
            self.speak(f"Maaf, saya tidak mengerti '{command}'. Ketik 'help' untuk bantuan.")
    
    def show_help(self):
        """Menampilkan bantuan"""
        self.speak("Berikut perintah yang bisa digunakan:")
        print("\n📋 DAFTAR PERINTAH:")
        for cmd, desc in self.commands.items():
            print(f"   • {cmd:<30} - {desc}")
        print("\n💡 Tips: Gunakan bahasa Indonesia atau Inggris, saya mengerti keduanya!")
        print("        Ketik 'list' untuk lihat saham populer yang bisa di-cek")
    
    def show_stock_list(self):
        """Menampilkan daftar saham populer"""
        self.speak("Berikut saham populer yang bisa Anda cek:")
        print("\n📊 DAFTAR SAHAM POPULER IHSG:")
        print("\nBanking:")
        for code, name in self.popular_stocks[:4]:
            print(f"   • {code:<6} - {name}")
        
        print("\nManufacturing & Others:")
        for code, name in self.popular_stocks[4:]:
            print(f"   • {code:<6} - {name}")
        
        print("\n💡 Contoh penggunaan:")
        print("   • cek BBCA           - Check 1 saham")
        print("   • cek BBCA,BBNI,UNTR - Check 3 saham sekaligus")
        print("   • stockbit BBCA      - Data dari Stockbit")
    
    def run_scan(self):
        """Menjalankan screening"""
        load_dependencies()
        
        self.speak("Memulai screening saham IHSG...")
        
        if not MODULES_AVAILABLE:
            self.speak("Module belum siap. Jalankan 'python3 ai_agent.py setup' dulu.")
            return
        
        try:
            # Ambil data
            fetcher = DataFetcher()
            stock_data = fetcher.fetch_all_data()
            
            if not stock_data:
                self.speak("Tidak ada data yang bisa diambil. Cek koneksi internet Anda.")
                return
            
            self.speak(f"Berhasil mengambil {len(stock_data)} saham")
            
            # Analisis
            results = []
            for stock in stock_data:
                analyzer = BandarmologyAnalyzer(stock['data'])
                phase = analyzer.detect_phase()
                divergence = analyzer.detect_divergence()
                
                if phase:
                    results.append({
                        'symbol': stock['symbol'],
                        'company': stock['company_name'],
                        'price': phase['current_price'],
                        'vwap': phase['vwap'],
                        'distance': phase['distance_pct'],
                        'phase': phase['phase'],
                        'signal': phase['signal'],
                        'divergence': divergence
                    })
            
            # Simpan hasil
            df = pd.DataFrame(results)
            
            # Buat folder jika belum ada
            Path("data/screening_results").mkdir(parents=True, exist_ok=True)
            
            # Simpan dengan timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"data/screening_results/scan_{timestamp}.csv"
            df.to_csv(filename, index=False)
            
            self.last_scan = {
                'time': datetime.now(),
                'file': filename,
                'total': len(results),
                'accumulation': len(df[df['phase'] == 'ACCUMULATION']),
                'distribution': len(df[df['phase'] == 'DISTRIBUTION'])
            }
            
            self.speak(f"Screening selesai! Hasil disimpan di {filename}")
            self.speak(f"Ditemukan {self.last_scan['accumulation']} saham dalam fase akumulasi")
            
            # Tampilkan ringkasan
            self.show_scan_summary(results)
            
        except Exception as e:
            self.speak(f"Error saat screening: {e}")
            print("\n🔧 Troubleshooting:")
            print("   1. Cek koneksi internet")
            print("   2. Pastikan yfinance bisa mengakses data")
            print("   3. Coba jalankan ulang")
    
    def show_scan_summary(self, results):
        """Tampilkan ringkasan hasil scan"""
        df = pd.DataFrame(results)
        
        if df.empty:
            return
        
        # Hitung statistik
        accumulation = df[df['phase'] == 'ACCUMULATION']
        distribution = df[df['phase'] == 'DISTRIBUTION']
        absorbing = df[df['phase'] == 'ABSORBING']
        
        print("\n📊 RINGKASAN SCREENING:")
        print(f"   Total saham dianalisis: {len(df)}")
        print(f"   🟢 Akumulasi: {len(accumulation)}")
        print(f"   🔴 Distribusi: {len(distribution)}")
        print(f"   🟡 Absorbing: {len(absorbing)}")
        
        if not accumulation.empty:
            print("\n🎯 5 SAHAM AKUMULASI TERBAIK:")
            top5 = accumulation.nlargest(5, 'distance')
            for _, row in top5.iterrows():
                print(f"   • {row['symbol']}: {row['company'][:30]:<30} "
                      f"Rp{row['price']:>8,.0f} (VWAP: Rp{row['vwap']:>8,.0f})")
    
    def show_recommendations(self):
        """Menampilkan rekomendasi dari hasil scan terakhir"""
        if not self.last_scan:
            self.speak("Belum ada data screening. Jalankan 'scan' dulu.")
            return
        
        try:
            df = pd.read_csv(self.last_scan['file'])
            
            # Filter rekomendasi
            recommendations = df[df['phase'] == 'ACCUMULATION']
            
            if recommendations.empty:
                self.speak("Tidak ada rekomendasi hari ini.")
                return
            
            self.speak(f"Ditemukan {len(recommendations)} rekomendasi:")
            print("\n" + "="*80)
            
            for idx, row in recommendations.iterrows():
                print(f"\n📈 {row['symbol']} - {row['company']}")
                print(f"   Harga: Rp{row['price']:,.0f}")
                print(f"   VWAP (Rata-rata Bandar): Rp{row['vwap']:,.0f}")
                print(f"   Jarak dari VWAP: {row['distance']:.2f}%")
                print(f"   Status: {row['phase']}")
                print(f"   Signal: {row['signal']}")
                print(f"   Divergence: {row['divergence']}")
                print("-" * 50)
                
                # Beri rekomendasi entry
                target = row['price'] * 1.05
                stoploss = row['price'] * 0.97
                print(f"   💡 Target: Rp{target:,.0f} (+5%)")
                print(f"   🛑 Stop Loss: Rp{stoploss:,.0f} (-3%)")
            
        except Exception as e:
            self.speak(f"Error membaca hasil: {e}")
    
    def check_stock(self, stock_code):
        """Cek detail satu saham"""
        load_dependencies()
        
        self.speak(f"Mencari data {stock_code}...")
        
        try:
            # Format kode
            if not stock_code.endswith('.JK'):
                yf_code = f"{stock_code}.JK"
            else:
                yf_code = stock_code
                stock_code = stock_code.replace('.JK', '')
            
            # Ambil data
            import yfinance as yf
            ticker = yf.Ticker(yf_code)
            hist = ticker.history(period="2mo")
            
            if hist.empty:
                self.speak(f"Data {stock_code} tidak ditemukan. Periksa kode saham.")
                return
            
            # Info perusahaan
            info = ticker.info
            
            print(f"\n{'='*60}")
            print(f"📊 ANALISIS {stock_code}")
            print(f"{'='*60}")
            
            # Info umum
            print(f"\n🏢 Perusahaan: {info.get('longName', 'N/A')}")
            print(f"   Sektor: {info.get('sector', 'N/A')}")
            print(f"   Industri: {info.get('industry', 'N/A')}")
            
            # Harga
            current = hist['Close'].iloc[-1]
            prev_close = hist['Close'].iloc[-2] if len(hist) > 1 else current
            change = ((current - prev_close) / prev_close) * 100
            
            print(f"\n💰 Harga: Rp{current:,.0f}")
            print(f"   Perubahan: {change:+.2f}%")
            print(f"   Volume: {hist['Volume'].iloc[-1]:,.0f}")
            print(f"   Rata2 Volume 20 hari: {hist['Volume'].tail(20).mean():,.0f}")
            
            # Analisis teknikal sederhana
            sma20 = hist['Close'].tail(20).mean()
            sma50 = hist['Close'].tail(50).mean() if len(hist) >= 50 else None
            
            print(f"\n📈 INDIKATOR:")
            print(f"   SMA 20: Rp{sma20:,.0f} ({'DI ATAS' if current > sma20 else 'DI BAWAH'} harga saat ini)")
            if sma50:
                print(f"   SMA 50: Rp{sma50:,.0f} ({'DI ATAS' if current > sma50 else 'DI BAWAH'} harga saat ini)")
            
            # Analisis bandarmology
            analyzer = BandarmologyAnalyzer(hist)
            phase = analyzer.detect_phase()
            divergence = analyzer.detect_divergence()
            
            if phase:
                print(f"\n🎯 ANALISIS BANDARMOLOGY:")
                print(f"   Fase: {phase['phase']}")
                print(f"   VWAP: Rp{phase['vwap']:,.0f}")
                print(f"   Jarak dari VWAP: {phase['distance_pct']:.2f}%")
                print(f"   Signal: {phase['signal']}")
                print(f"   Divergence: {divergence}")
            
            # Rekomendasi
            print(f"\n💡 REKOMENDASI:")
            if phase and phase['phase'] == 'ACCUMULATION':
                print("   ✅ Masuk dalam fase akumulasi - Cocok untuk swing trading")
                print(f"   🎯 Target 1: Rp{current * 1.03:,.0f} (+3%)")
                print(f"   🎯 Target 2: Rp{current * 1.05:,.0f} (+5%)")
                print(f"   🛑 Stop Loss: Rp{current * 0.97:,.0f} (-3%)")
            elif phase and phase['phase'] == 'DISTRIBUTION':
                print("   ⚠️  Dalam fase distribusi - Hindari beli, tunggu koreksi")
            else:
                print("   ⏳ Fase absorbing - Tunggu konfirmasi lebih lanjut")
            
        except Exception as e:
            self.speak(f"Error: {e}")
    
    def check_stockbit(self, stock_code):
        """Cek data saham dari Stockbit"""
        load_dependencies()
        
        self.speak(f"Mencari data {stock_code} dari Stockbit...")
        
        try:
            from modules.stockbit_fetcher import StockbitFetcher
            
            fetcher = StockbitFetcher()
            analysis = fetcher.fetch_stock_analysis(stock_code)
            
            if not analysis:
                self.speak(f"Tidak bisa mengambil data {stock_code} dari Stockbit")
                return
            
            print(f"\n{'='*60}")
            print(f"📊 DATA STOCKBIT - {stock_code}")
            print(f"{'='*60}")
            
            # Data dasar
            print(f"\n💰 HARGA & PERUBAHAN:")
            print(f"   Harga Saat Ini: Rp{analysis.get('current_price', 0):,.0f}")
            print(f"   Perubahan: {analysis.get('change_pct', 0):+.2f}%")
            print(f"   Volume: {analysis.get('volume', 0):,.0f}")
            
            # Valuasi
            print(f"\n📈 VALUASI:")
            print(f"   Market Cap: {analysis.get('market_cap', 'N/A')}")
            print(f"   P/E Ratio: {analysis.get('pe_ratio', 'N/A')}")
            print(f"   Dividend Yield: {analysis.get('dividend_yield', 'N/A')}%")
            
            # Rating
            print(f"\n🎯 RATING STOCKBIT:")
            print(f"   Rekomendasi: {analysis.get('recommendation', 'NEUTRAL')}")
            print(f"   Technical: {analysis.get('technical_rating', 'NEUTRAL')}")
            print(f"   Fundamental: {analysis.get('fundamental_rating', 'NEUTRAL')}")
            
            # Signal
            print(f"\n📊 SIGNAL:")
            print(f"   Buy Signal: {analysis.get('buy_signal_count', 0)}")
            print(f"   Sell Signal: {analysis.get('sell_signal_count', 0)}")
            
            # Compare
            comparison = fetcher.compare_with_yfinance(stock_code)
            if comparison is not None:
                print(f"\n🔄 PERBANDINGAN DATA:")
                print(comparison.to_string(index=False))
            
            print(f"\n⏰ Update: {analysis.get('timestamp', 'N/A')}")
            
        except ImportError:
            self.speak("Error: Module stockbit_fetcher belum tersedia")
        except Exception as e:
            self.speak(f"Error: {e}")
    
    def launch_dashboard(self):
        """Menjalankan dashboard Streamlit"""
        if self.dashboard_process and self.dashboard_process.poll() is None:
            self.speak("Dashboard sudah berjalan di http://localhost:8501")
            return
        
        self.speak("Menjalankan dashboard...")
        
        try:
            self.dashboard_process = subprocess.Popen([
                "streamlit", "run", "app.py",
                "--server.port", "8501",
                "--server.address", "0.0.0.0"
            ])
            
            # Tunggu sebentar
            time.sleep(3)
            
            self.speak("Dashboard siap! Buka browser di:")
            print("   • Local: http://localhost:8501")
            
            # Cari IP untuk akses dari HP
            try:
                ip = subprocess.check_output(["ifconfig"]).decode()
                for line in ip.split('\n'):
                    if 'inet ' in line and '127.0.0.1' not in line:
                        ip_address = line.strip().split()[1]
                        print(f"   • Dari HP: http://{ip_address}:8501")
                        break
            except:
                pass
            
        except Exception as e:
            self.speak(f"Gagal menjalankan dashboard: {e}")
    
    def show_status(self):
        """Menampilkan status aplikasi"""
        self.speak("Memeriksa status...")
        
        print(f"\n{'='*50}")
        print(f"STATUS APLIKASI - {datetime.now().strftime('%d %B %Y %H:%M')}")
        print(f"{'='*50}")
        
        # Cek folder
        print("\n📁 STRUKTUR FOLDER:")
        folders = ['modules', 'data', 'data/screening_results', 'output']
        for folder in folders:
            status = "✅" if os.path.exists(folder) else "❌"
            print(f"   {status} {folder}/")
        
        # Cek file penting
        print("\n📄 FILE PENTING:")
        files = ['app.py', 'daily_automation.py', 'requirements.txt']
        for file in files:
            status = "✅" if os.path.exists(file) else "❌"
            print(f"   {status} {file}")
        
        # Cek modules
        print("\n🔧 MODULES:")
        print(f"   {'✅' if MODULES_AVAILABLE else '❌'} Modules siap digunakan")
        
        # Cek hasil screening terakhir
        if self.last_scan:
            print(f"\n📊 SCREENING TERAKHIR:")
            print(f"   Waktu: {self.last_scan['time'].strftime('%d %B %Y %H:%M')}")
            print(f"   File: {self.last_scan['file']}")
            print(f"   Total saham: {self.last_scan['total']}")
            print(f"   Akumulasi: {self.last_scan['accumulation']}")
        else:
            print("\n📊 SCREENING TERAKHIR:")
            print("   Belum pernah screening")
        
        # Cek dashboard
        if self.dashboard_process and self.dashboard_process.poll() is None:
            print("\n🌐 DASHBOARD: ✅ Running di port 8501")
        else:
            print("\n🌐 DASHBOARD: ❌ Tidak running")
    
    def teach_coding(self):
        """Memberi tips belajar coding untuk analisis saham"""
        self.speak("Saya bantu Anda belajar coding untuk analisis saham!")
        
        print("\n" + "="*60)
        print("📚 BELAJAR CODING UNTUK ANALISIS SAHAM")
        print("="*60)
        
        print("\n🎯 LANGKAH AWAL:")
        print("   1. Belajar Python dasar (1-2 minggu)")
        print("   2. Pahami pandas untuk manipulasi data")
        print("   3. Pelajari yfinance untuk ambil data saham")
        print("   4. Eksplorasi visualisasi dengan plotly")
        
        print("\n📖 SUMBER BELAJAR GRATIS:")
        print("   • Python: python.org/about/gettingstarted")
        print("   • Pandas: pandas.pydata.org/docs/getting_started")
        print("   • YouTube: 'Python untuk Pemula' oleh Indonesia Belajar")
        print("   • Buku: 'Python untuk Analisis Saham' (cari di Google Books)")
        
        print("\n💡 PROYEK LATIHAN:")
        print("   1. Buat script untuk ambil data saham favorit")
        print("   2. Hitung moving average sederhana")
        print("   3. Plot chart harga dengan matplotlib")
        print("   4. Buat screening sederhana seperti aplikasi ini")
        
        print("\n🚀 TIPS SUKSES:")
        print("   • Mulai dari yang kecil, jangan langsung ambil semua saham")
        print("   • Debug error dengan membaca pesan errornya")
        print("   • Bergabung dengan komunitas (Facebook: Python Indonesia)")
        print("   • Praktek setiap hari, minimal 30 menit")
        
        print("\n❓ ADA PERTANYAAN?")
        print("   Tanya saya langsung dengan 'cek [kode]' untuk lihat contoh analisis")
    
    def run(self):
        """Menjalankan AI Agent"""
        print("\n" + "="*60)
        print(f"🤖 {self.name} v{self.version} - Asisten Analisis Saham IHSG")
        print("="*60)
        print("\nHalo! Saya siap membantu analisis saham Anda.")
        print("Ketik 'help' untuk melihat perintah, atau langsung tanya!")
        
        while self.running:
            try:
                command = self.listen()
                if command:
                    self.run_command(command)
            except KeyboardInterrupt:
                print("\n")
                self.speak("Terima kasih! Sampai jumpa lagi.")
                break
            except Exception as e:
                self.speak(f"Terjadi error: {e}")
                print("Coba lagi atau ketik 'help' untuk bantuan.")

# File setup untuk inisialisasi awal
class Setup:
    """Setup awal aplikasi"""
    
    @staticmethod
    def run():
        print("🚀 Setup Aplikasi Jurnal Screening Saham")
        print("="*50)
        
        # Buat folder
        print("\n📁 Membuat struktur folder...")
        folders = ['modules', 'data', 'data/screening_results', 'output']
        for folder in folders:
            Path(folder).mkdir(parents=True, exist_ok=True)
            print(f"   ✅ {folder}/")
        
        # Buat file __init__.py
        with open('modules/__init__.py', 'w') as f:
            f.write('# Modules package\n')
        print("   ✅ modules/__init__.py")
        
        # Cek requirements
        print("\n📦 Memeriksa dependencies...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
            print("   ✅ Semua library terinstall")
        except Exception as e:
            print(f"   ⚠️  Gagal install: {e}")
            print("      Jalankan manual: pip3 install -r requirements.txt")
        
        print("\n" + "="*50)
        print("✅ SETUP SELESAI!")
        print("\nJalankan agent dengan: python3 ai_agent.py")
        print("Kemudian coba perintah:")
        print("   • scan          - screening saham")
        print("   • dashboard     - buka dashboard")
        print("   • cek BBCA      - lihat detail BBCA")

if __name__ == "__main__":
    # Cek argumen untuk setup
    if len(sys.argv) > 1 and sys.argv[1] == "setup":
        Setup.run()
    else:
        # Jalankan agent
        load_dependencies()
        
        if not MODULES_AVAILABLE:
            print("⚠️  Modules belum lengkap. Jalankan 'python3 ai_agent.py setup' dulu.")
            sys.exit(1)
        
        agent = AIAgent()
        agent.run()
