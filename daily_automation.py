"""
Script untuk automasi screening saham harian
Dijalankan otomatis setiap hari pukul jam tertentu
"""

import schedule
import time
import subprocess
import sys
import os
from datetime import datetime
from pathlib import Path

# Tambahkan path untuk import modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from modules.data_fetcher import DataFetcher
from modules.bandarmology import BandarmologyAnalyzer
import pandas as pd
import numpy as np

def log_message(message):
    """Log message dengan timestamp"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {message}")

def run_daily_scan():
    """Menjalankan screening harian"""
    log_message("🚀 Memulai daily screening...")
    
    try:
        # Buat folder output jika belum ada
        Path("data/screening_results").mkdir(parents=True, exist_ok=True)
        
        # Ambil data
        log_message("📊 Mengambil data saham...")
        fetcher = DataFetcher()
        stock_data = fetcher.fetch_all_data()
        
        if not stock_data:
            log_message("❌ Gagal mengambil data")
            return
        
        log_message(f"✅ Berhasil mengambil {len(stock_data)} saham")
        
        # Analisis
        log_message("🔍 Melakukan analisis...")
        results = []
        
        for i, stock in enumerate(stock_data):
            try:
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
                        'divergence': divergence,
                        'strength': phase['strength']
                    })
                
                # Progress
                if (i + 1) % 5 == 0:
                    log_message(f"   Progress: {i + 1}/{len(stock_data)} saham")
            
            except Exception as e:
                log_message(f"   ⚠️  Error menganalisis {stock['symbol']}: {e}")
                continue
        
        if not results:
            log_message("❌ Tidak ada hasil analisis")
            return
        
        # Simpan hasil
        log_message("💾 Menyimpan hasil...")
        df = pd.DataFrame(results)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"data/screening_results/scan_{timestamp}.csv"
        df.to_csv(filename, index=False)
        
        log_message(f"✅ Hasil disimpan ke {filename}")
        
        # Statistik
        accumulation = len(df[df['phase'] == 'ACCUMULATION'])
        distribution = len(df[df['phase'] == 'DISTRIBUTION'])
        absorbing = len(df[df['phase'] == 'ABSORBING'])
        
        log_message(f"""\n📊 RINGKASAN SCREENING:
   Total: {len(df)} saham
   🟢 Akumulasi: {accumulation}
   🔴 Distribusi: {distribution}
   🟡 Absorbing: {absorbing}
""")
        
        # Tampilkan top akumulasi
        if accumulation > 0:
            log_message("🎯 TOP 5 SAHAM AKUMULASI:")
            top5 = df[df['phase'] == 'ACCUMULATION'].nlargest(5, 'distance')
            for _, row in top5.iterrows():
                log_message(f"   • {row['symbol']}: Rp{row['price']:,.0f} "
                           f"(VWAP: Rp{row['vwap']:,.0f})")
        
        log_message("✨ Daily screening selesai!\n")
        
    except Exception as e:
        log_message(f"❌ Error: {e}")

def send_notification(title, message):
    """Kirim notifikasi (untuk implementasi di kemudian hari)"""
    # TODO: Implementasi email/Telegram notification
    log_message(f"📧 {title}: {message}")

def schedule_daily_scans():
    """Schedule screening harian pada jam-jam tertentu"""
    
    # Screening pagi jam 09:00
    schedule.every().day.at("09:00").do(run_daily_scan)
    
    # Screening siang jam 13:00
    schedule.every().day.at("13:00").do(run_daily_scan)
    
    # Screening sore jam 17:00
    schedule.every().day.at("17:00").do(run_daily_scan)
    
    log_message("📅 Schedule screening harian:")
    log_message("   • Pagi: 09:00")
    log_message("   • Siang: 13:00")
    log_message("   • Sore: 17:00")
    log_message("\nTekan Ctrl+C untuk berhenti\n")
    
    # Keep scheduler running
    while True:
        try:
            schedule.run_pending()
            time.sleep(60)  # Check setiap menit
        except KeyboardInterrupt:
            log_message("\n👋 Automation dihentikan")
            break

def run_once():
    """Jalankan screening sekali saja"""
    log_message("Menjalankan single screening...\n")
    run_daily_scan()

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "run":
        # Jalankan sekali
        run_once()
    else:
        # Jalankan scheduler
        schedule_daily_scans()
