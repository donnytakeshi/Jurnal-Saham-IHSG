"""
Module untuk analisis Order Book
Menganalisis kedalaman pasar dan kekuatan bid/ask
"""

import pandas as pd
import numpy as np

class OrderbookAnalyzer:
    """
    Analis Order Book untuk memahami tekanan beli/jual
    """
    
    def __init__(self, orderbook_data=None):
        """
        Parameters:
        -----------
        orderbook_data : dict
            Data order book dengan struktur:
            {
                'bids': [[price, volume], ...],
                'asks': [[price, volume], ...]
            }
        """
        self.orderbook_data = orderbook_data or {'bids': [], 'asks': []}
    
    def analyze_depth(self, bid_volume=None, ask_volume=None):
        """
        Analisis kedalaman pasar (market depth)
        
        Parameters:
        -----------
        bid_volume : float
            Total volume bid
        ask_volume : float
            Total volume ask
            
        Returns:
        --------
        dict : Analisis kedalaman
        """
        if not bid_volume or not ask_volume:
            return self._analyze_from_orderbook()
        
        # Hitung imbalance
        imbalance = (bid_volume - ask_volume) / (bid_volume + ask_volume)
        
        # Hitung strength
        strength = abs(imbalance) * 100
        pressure = 'BUY' if imbalance > 0 else 'SELL'
        
        return {
            'bid_volume': bid_volume,
            'ask_volume': ask_volume,
            'imbalance': imbalance,
            'pressure': pressure,
            'strength': strength
        }
    
    def _analyze_from_orderbook(self):
        """Analisis dari data order book tersimpan"""
        if not self.orderbook_data['bids'] or not self.orderbook_data['asks']:
            return None
        
        bids = pd.DataFrame(self.orderbook_data['bids'], columns=['price', 'volume'])
        asks = pd.DataFrame(self.orderbook_data['asks'], columns=['price', 'volume'])
        
        bid_volume = bids['volume'].sum()
        ask_volume = asks['volume'].sum()
        
        return self.analyze_depth(bid_volume, ask_volume)
    
    def detect_wall(self, threshold_pct=0.05):
        """
        Deteksi wall (large order concentration)
        
        Parameters:
        -----------
        threshold_pct : float
            Threshold untuk mendeteksi wall (% dari total volume)
            
        Returns:
        --------
        dict : Informasi wall
        """
        if not self.orderbook_data['bids'] or not self.orderbook_data['asks']:
            return None
        
        bids = pd.DataFrame(self.orderbook_data['bids'], columns=['price', 'volume'])
        asks = pd.DataFrame(self.orderbook_data['asks'], columns=['price', 'volume'])
        
        total_bid = bids['volume'].sum()
        total_ask = asks['volume'].sum()
        
        # Cari bid wall
        bid_wall = None
        if not bids.empty:
            max_bid_idx = bids['volume'].idxmax()
            if bids.loc[max_bid_idx, 'volume'] > total_bid * threshold_pct:
                bid_wall = {
                    'price': bids.loc[max_bid_idx, 'price'],
                    'volume': bids.loc[max_bid_idx, 'volume'],
                    'strength': (bids.loc[max_bid_idx, 'volume'] / total_bid) * 100
                }
        
        # Cari ask wall
        ask_wall = None
        if not asks.empty:
            max_ask_idx = asks['volume'].idxmax()
            if asks.loc[max_ask_idx, 'volume'] > total_ask * threshold_pct:
                ask_wall = {
                    'price': asks.loc[max_ask_idx, 'price'],
                    'volume': asks.loc[max_ask_idx, 'volume'],
                    'strength': (asks.loc[max_ask_idx, 'volume'] / total_ask) * 100
                }
        
        return {
            'bid_wall': bid_wall,
            'ask_wall': ask_wall
        }
    
    def calculate_spread(self):
        """
        Hitung bid-ask spread
        
        Returns:
        --------
        dict : Spread information
        """
        if not self.orderbook_data['bids'] or not self.orderbook_data['asks']:
            return None
        
        best_bid = self.orderbook_data['bids'][0][0]  # Highest bid
        best_ask = self.orderbook_data['asks'][0][0]  # Lowest ask
        
        spread = best_ask - best_bid
        spread_pct = (spread / best_bid) * 100
        mid_price = (best_bid + best_ask) / 2
        
        return {
            'best_bid': best_bid,
            'best_ask': best_ask,
            'spread': spread,
            'spread_pct': spread_pct,
            'mid_price': mid_price
        }
    
    def estimate_liquidity(self):
        """
        Estimasi likuiditas pasar
        
        Returns:
        --------
        str : 'HIGH', 'MEDIUM', atau 'LOW'
        """
        if not self.orderbook_data['bids'] or not self.orderbook_data['asks']:
            return 'UNKNOWN'
        
        bids = pd.DataFrame(self.orderbook_data['bids'], columns=['price', 'volume'])
        asks = pd.DataFrame(self.orderbook_data['asks'], columns=['price', 'volume'])
        
        total_volume = bids['volume'].sum() + asks['volume'].sum()
        
        if total_volume > 1000000:
            return 'HIGH'
        elif total_volume > 100000:
            return 'MEDIUM'
        else:
            return 'LOW'
    
    def analyze_momentum(self, price_change, volume_change):
        """
        Analisis momentum berdasarkan perubahan harga dan volume
        
        Parameters:
        -----------
        price_change : float
            Perubahan harga (%)
        volume_change : float
            Perubahan volume (%)
            
        Returns:
        --------
        dict : Momentum analysis
        """
        # Hitung indeks momentum
        momentum = price_change * (1 + volume_change / 100)
        
        if momentum > 5:
            direction = 'STRONG_BUY'
        elif momentum > 0:
            direction = 'BUY'
        elif momentum < -5:
            direction = 'STRONG_SELL'
        elif momentum < 0:
            direction = 'SELL'
        else:
            direction = 'NEUTRAL'
        
        return {
            'momentum': momentum,
            'price_change': price_change,
            'volume_change': volume_change,
            'direction': direction,
            'strength': abs(momentum)
        }
