"""
Bandarmology Realtime - Lightweight tanpa pandas
Menghitung akumulasi/distribusi bandar dari data realtime
"""

import math
from collections import deque


class VWAPCalculator:
    """Volume Weighted Average Price - Realtime"""
    
    def __init__(self):
        self.total_volume = 0
        self.total_value = 0
    
    def update(self, price, volume):
        """Update VWAP dengan data baru"""
        self.total_value += price * volume
        self.total_volume += volume
        return self.value
    
    @property
    def value(self):
        return self.total_value / self.total_volume if self.total_volume > 0 else 0
    
    def reset(self):
        self.total_volume = 0
        self.total_value = 0


class SimpleMovingAverage:
    """Moving Average tanpa numpy"""
    
    def __init__(self, period=20):
        self.period = period
        self.values = deque(maxlen=period)
        self._sum = 0
    
    def update(self, value):
        if len(self.values) == self.period:
            self._sum -= self.values[0]
        self.values.append(value)
        self._sum += value
        return self.value
    
    @property
    def value(self):
        if len(self.values) == 0:
            return 0
        return self._sum / len(self.values)
    
    def is_ready(self):
        return len(self.values) == self.period


class StandardDeviation:
    """Standard Deviation tanpa numpy"""
    
    def __init__(self, period=20):
        self.period = period
        self.values = deque(maxlen=period)
        self.sma = SimpleMovingAverage(period)
    
    def update(self, value):
        self.values.append(value)
        self.sma.update(value)
        return self.value
    
    @property
    def value(self):
        if len(self.values) < 2:
            return 0
        mean = self.sma.value
        variance = sum((x - mean) ** 2 for x in self.values) / len(self.values)
        return math.sqrt(variance)


class BollingerBands:
    """Bollinger Bands tanpa TA-Lib"""
    
    def __init__(self, period=20, std_dev=2):
        self.period = period
        self.std_dev = std_dev
        self.sma = SimpleMovingAverage(period)
        self.std = StandardDeviation(period)
        self.prices = deque(maxlen=period)
    
    def update(self, price):
        self.prices.append(price)
        self.sma.update(price)
        self.std.update(price)
        return {
            'upper': self.upper,
            'middle': self.middle,
            'lower': self.lower
        }
    
    @property
    def middle(self):
        return self.sma.value
    
    @property
    def upper(self):
        return self.middle + (self.std.value * self.std_dev)
    
    @property
    def lower(self):
        return self.middle - (self.std.value * self.std_dev)
    
    def is_ready(self):
        return len(self.prices) == self.period


class BandarmologyDetector:
    """
    Deteksi akumulasi/distribusi bandar secara realtime
    Berdasarkan VWAP, Volume Divergence, dan Price Action
    """
    
    def __init__(self, lookback=20, divergence_lookback=5):
        self.lookback = lookback
        self.divergence_lookback = divergence_lookback
        
        # Realtime indicators
        self.vwap = VWAPCalculator()
        self.bb = BollingerBands(period=lookback)
        
        # Volume tracking
        self.volumes = deque(maxlen=lookback)
        self.prices = deque(maxlen=lookback)
        
        # Trend detection
        self.price_trend = 0  # -1 downtrend, 0 neutral, 1 uptrend
        self.volume_trend = 0
        
        # Phase detection
        self.phase = "NEUTRAL"  # ACCUMULATION, DISTRIBUTION, ABSORBING
        self.signal = "HOLD"
        self.strength = 0
        
    def update(self, price, volume):
        """Update dengan data realtime - panggil setiap tick/menit"""
        
        # Update indicators
        self.vwap.update(price, volume)
        self.bb.update(price)
        self.volumes.append(volume)
        self.prices.append(price)
        
        # Hitung trend
        self._calculate_trends()
        
        # Deteksi fase bandarmology
        self._detect_phase()
        
        return self.get_result()
    
    def _calculate_trends(self):
        """Hitung tren harga dan volume"""
        if len(self.prices) < 3:
            return
        
        # Price trend (sederhana: bandingkan price terakhir vs rata-rata)
        price_ma = sum(list(self.prices)[-5:]) / 5 if len(self.prices) >= 5 else self.prices[-1]
        if self.prices[-1] > price_ma * 1.01:
            self.price_trend = 1  # Uptrend
        elif self.prices[-1] < price_ma * 0.99:
            self.price_trend = -1  # Downtrend
        else:
            self.price_trend = 0
        
        # Volume trend
        if len(self.volumes) >= 5:
            vol_ma = sum(list(self.volumes)[-5:]) / 5
            if self.volumes[-1] > vol_ma * 1.2:
                self.volume_trend = 1  # Volume up
            elif self.volumes[-1] < vol_ma * 0.8:
                self.volume_trend = -1  # Volume down
            else:
                self.volume_trend = 0
    
    def _detect_phase(self):
        """Deteksi fase akumulasi/distribusi bandar"""
        
        if not self.bb.is_ready() or self.vwap.value == 0:
            return
        
        price = self.prices[-1] if self.prices else 0
        vwap = self.vwap.value
        bb_lower = self.bb.lower
        bb_upper = self.bb.upper
        
        # Kondisi Akumulasi (Bandar beli)
        # 1. Harga di bawah VWAP
        # 2. Volume meningkat
        # 3. Harga mendekati lower BB
        if price < vwap and self.volume_trend > 0:
            self.phase = "ACCUMULATION"
            distance_pct = ((price - vwap) / vwap) * 100
            self.strength = min(100, abs(distance_pct) * 2)
            self.signal = "BUY" if self.strength > 30 else "ACCUMULATE"
        
        # Kondisi Distribusi (Bandar jual)
        # 1. Harga di atas VWAP
        # 2. Volume tinggi
        # 3. Harga mendekati upper BB
        elif price > vwap and self.volume_trend > 0:
            self.phase = "DISTRIBUTION"
            distance_pct = ((price - vwap) / vwap) * 100
            self.strength = min(100, abs(distance_pct) * 2)
            self.signal = "SELL" if self.strength > 30 else "DISTRIBUTE"
        
        # Kondisi Absorbing (Konsolidasi)
        # Harga mendekati VWAP, volume normal
        elif abs(price - vwap) / vwap < 0.01:
            self.phase = "ABSORBING"
            self.strength = 50
            self.signal = "HOLD"
        
        else:
            self.phase = "NEUTRAL"
            self.strength = 0
            self.signal = "WATCH"
    
    def get_result(self):
        """Return hasil analisis"""
        return {
            'phase': self.phase,
            'signal': self.signal,
            'strength': self.strength,
            'current_price': self.prices[-1] if self.prices else 0,
            'vwap': self.vwap.value,
            'distance_pct': ((self.prices[-1] - self.vwap.value) / self.vwap.value * 100) if self.vwap.value else 0,
            'bb_upper': self.bb.upper,
            'bb_middle': self.bb.middle,
            'bb_lower': self.bb.lower
        }


# Fungsi wrapper untuk kompatibilitas dengan kode lama
def analyze_bandarmology(price_data):
    """
    Wrapper untuk kompatibilitas dengan kode lama
    price_data: list of dict dengan key 'price' dan 'volume'
    """
    detector = BandarmologyDetector()
    results = []
    
    for tick in price_data:
        result = detector.update(tick['price'], tick['volume'])
        results.append(result)
    
    return results[-1] if results else None