"""
Module untuk analisis Bandarmology
Menganalisis perilaku bandar (institusi besar) dalam trading saham
"""

import pandas as pd
import numpy as np
from datetime import datetime

class BandarmologyAnalyzer:
    """
    Analis Bandarmology untuk mendeteksi fase akumulasi, distribusi, dan absorbing
    """
    
    def __init__(self, ohlcv_data):
        """
        Parameters:
        -----------
        ohlcv_data : pd.DataFrame
            Data OHLCV dari yfinance
        """
        self.data = ohlcv_data.copy()
        self._prepare_data()
    
    def _prepare_data(self):
        """Menyiapkan data untuk analisis"""
        # Pastikan ada kolom yang diperlukan
        required_cols = ['Open', 'High', 'Low', 'Close', 'Volume']
        for col in required_cols:
            if col not in self.data.columns:
                raise ValueError(f"Data harus memiliki kolom {col}")
        
        # Hitung VWAP (Volume Weighted Average Price)
        self.data['VWAP'] = self._calculate_vwap()
        
        # Hitung moving averages
        self.data['SMA20'] = self.data['Close'].rolling(window=20).mean()
        self.data['SMA50'] = self.data['Close'].rolling(window=50).mean()
        
        # Hitung volatilitas
        self.data['Volatility'] = self.data['Close'].rolling(window=20).std()
        
    def _calculate_vwap(self):
        """Menghitung VWAP (Volume Weighted Average Price)"""
        data = self.data.copy()
        data['TP'] = (data['High'] + data['Low'] + data['Close']) / 3
        data['TPV'] = data['TP'] * data['Volume']
        data['CumTPV'] = data['TPV'].cumsum()
        data['CumVol'] = data['Volume'].cumsum()
        return data['CumTPV'] / data['CumVol']
    
    def detect_phase(self):
        """
        Mendeteksi fase bandar: ACCUMULATION, DISTRIBUTION, atau ABSORBING
        
        Returns:
        --------
        dict : Informasi fase dengan struktur:
            {
                'phase': str,
                'current_price': float,
                'vwap': float,
                'distance_pct': float,
                'signal': str,
                'strength': float
            }
        """
        if len(self.data) < 20:
            return None
        
        current_price = self.data['Close'].iloc[-1]
        vwap = self.data['VWAP'].iloc[-1]
        sma20 = self.data['SMA20'].iloc[-1]
        sma50 = self.data['SMA50'].iloc[-1] if pd.notna(self.data['SMA50'].iloc[-1]) else sma20
        
        # Hitung jarak dari VWAP
        distance_pct = ((current_price - vwap) / vwap) * 100
        
        # Hitung volume trend
        vol_20day_avg = self.data['Volume'].tail(20).mean()
        current_vol = self.data['Volume'].iloc[-1]
        vol_ratio = current_vol / vol_20day_avg if vol_20day_avg > 0 else 1
        
        # Analisis fase
        phase = self._determine_phase(current_price, vwap, sma20, sma50, vol_ratio)
        
        # Generate signal
        signal = self._generate_signal(phase, distance_pct, vol_ratio)
        
        # Hitung kekuatan signal
        strength = self._calculate_strength(phase, distance_pct, vol_ratio)
        
        return {
            'phase': phase,
            'current_price': current_price,
            'vwap': vwap,
            'sma20': sma20,
            'sma50': sma50,
            'distance_pct': distance_pct,
            'signal': signal,
            'strength': strength,
            'volume_ratio': vol_ratio
        }
    
    def _determine_phase(self, price, vwap, sma20, sma50, vol_ratio):
        """Menentukan fase berdasarkan indikator"""
        # ACCUMULATION: Harga di bawah VWAP dengan volume tinggi
        if price < vwap and vol_ratio > 1.2 and price > sma50:
            return 'ACCUMULATION'
        
        # DISTRIBUTION: Harga di atas VWAP dengan volume tinggi
        elif price > vwap and vol_ratio > 1.2 and price < sma50:
            return 'DISTRIBUTION'
        
        # ABSORBING: Harga stabil di sekitar VWAP
        elif abs(price - vwap) < (vwap * 0.02) and vol_ratio < 1.5:
            return 'ABSORBING'
        
        # Default: berdasarkan posisi harga terhadap VWAP
        elif price < vwap:
            return 'ACCUMULATION'
        else:
            return 'DISTRIBUTION'
    
    def _generate_signal(self, phase, distance_pct, vol_ratio):
        """Generate trading signal"""
        if phase == 'ACCUMULATION':
            if distance_pct < -3 and vol_ratio > 1.5:
                return 'STRONG_BUY'
            elif distance_pct < 0 and vol_ratio > 1.0:
                return 'BUY'
            else:
                return 'NEUTRAL'
        
        elif phase == 'DISTRIBUTION':
            if distance_pct > 3 and vol_ratio > 1.5:
                return 'STRONG_SELL'
            elif distance_pct > 0 and vol_ratio > 1.0:
                return 'SELL'
            else:
                return 'NEUTRAL'
        
        else:  # ABSORBING
            return 'HOLD'
    
    def _calculate_strength(self, phase, distance_pct, vol_ratio):
        """Hitung kekuatan signal (0-100)"""
        strength = 50  # Neutral
        
        # Faktor jarak dari VWAP
        if abs(distance_pct) > 5:
            strength += 30
        elif abs(distance_pct) > 2:
            strength += 15
        
        # Faktor volume
        if vol_ratio > 2:
            strength += 25
        elif vol_ratio > 1.5:
            strength += 15
        elif vol_ratio < 0.8:
            strength -= 10
        
        return min(100, max(0, strength))
    
    def detect_divergence(self):
        """
        Mendeteksi divergence antara harga dan volume
        
        Returns:
        --------
        str : 'BULLISH' jika harga turun tapi volume naik (buying opportunity)
              'BEARISH' jika harga naik tapi volume turun (warning)
              'NEUTRAL' jika tidak ada divergence
        """
        if len(self.data) < 2:
            return 'NEUTRAL'
        
        # Bandingkan 2 candle terakhir
        prev_close = self.data['Close'].iloc[-2]
        curr_close = self.data['Close'].iloc[-1]
        prev_vol = self.data['Volume'].iloc[-2]
        curr_vol = self.data['Volume'].iloc[-1]
        
        # BULLISH divergence: harga turun tapi volume naik
        if curr_close < prev_close and curr_vol > prev_vol:
            return 'BULLISH'
        
        # BEARISH divergence: harga naik tapi volume turun
        elif curr_close > prev_close and curr_vol < prev_vol:
            return 'BEARISH'
        
        else:
            return 'NEUTRAL'
    
    def analyze_trend(self, window=20):
        """
        Analisis trend jangka pendek
        
        Parameters:
        -----------
        window : int
            Jumlah hari untuk analisis
            
        Returns:
        --------
        dict : Analisis trend
        """
        if len(self.data) < window:
            return None
        
        recent = self.data.tail(window)
        high = recent['High'].max()
        low = recent['Low'].min()
        
        current_price = self.data['Close'].iloc[-1]
        position = (current_price - low) / (high - low) if low != high else 0.5
        
        # Trend direction
        sma_short = self.data['Close'].tail(5).mean()
        sma_long = self.data['Close'].tail(window).mean()
        
        if sma_short > sma_long:
            trend = 'UPTREND'
        elif sma_short < sma_long:
            trend = 'DOWNTREND'
        else:
            trend = 'SIDEWAYS'
        
        return {
            'trend': trend,
            'high': high,
            'low': low,
            'price_position': position,  # 0 = near low, 1 = near high
            'current_price': current_price
        }
    
    def calculate_support_resistance(self, window=20):
        """
        Hitung level support dan resistance sederhana
        
        Parameters:
        -----------
        window : int
            Jumlah periode untuk perhitungan
            
        Returns:
        --------
        dict : Level support dan resistance
        """
        if len(self.data) < window:
            return None
        
        recent = self.data.tail(window)
        
        support = recent['Low'].min()
        resistance = recent['High'].max()
        
        # Pivot level
        high = recent['High'].iloc[-1]
        low = recent['Low'].iloc[-1]
        close = recent['Close'].iloc[-1]
        
        pivot = (high + low + close) / 3
        support1 = (2 * pivot) - high
        resistance1 = (2 * pivot) - low
        
        return {
            'support': support,
            'resistance': resistance,
            'pivot': pivot,
            'support1': support1,
            'resistance1': resistance1
        }
