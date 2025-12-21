import yfinance as yf
import pandas as pd
import numpy as np
import time
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

class VolumePatternScanner:
    def __init__(self):
        # Indian stocks with their sectors
        self.stocks = {
            "RELIANCE.NS": "Energy",
            "TCS.NS": "IT",
            "INFY.NS": "IT", 
            "HDFCBANK.NS": "Banking",
            "ICICIBANK.NS": "Banking",
            "SBIN.NS": "Banking",
            "BHARTIARTL.NS": "Telecom",
            "KOTAKBANK.NS": "Banking",
            "ITC.NS": "FMCG",
            "ASIANPAINT.NS": "Paint"
        }
        
        # Real current prices (update periodically)
        self.current_prices = {
            "RELIANCE.NS": 2565.10,
            "TCS.NS": 3282.00,
            "INFY.NS": 1492.34,
            "HDFCBANK.NS": 1679.07,
            "ICICIBANK.NS": 989.01,
            "SBIN.NS": 580.67,
            "BHARTIARTL.NS": 1139.69,
            "KOTAKBANK.NS": 1746.72,
            "ITC.NS": 442.89,
            "ASIANPAINT.NS": 3162.35
        }
    
    def fetch_stock_data(self, symbol, days=20):
        """Fetch stock data with caching"""
        try:
            stock = yf.Ticker(symbol)
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)
            
            # Fetch data
            df = stock.history(start=start_date, end=end_date, interval='1d')
            
            if df.empty or len(df) < 10:
                return None
            
            # Calculate indicators
            df['Volume_MA5'] = df['Volume'].rolling(window=5).mean()
            df['Volume_MA20'] = df['Volume'].rolling(window=20).mean()
            df['Price_Change'] = df['Close'].pct_change() * 100
            df['Volume_Change'] = df['Volume'].pct_change() * 100
            df['Volume_Ratio'] = df['Volume'] / df['Volume_MA20']
            
            return df
        except Exception as e:
            print(f"Error fetching {symbol}: {e}")
            return None
    
    def analyze_patterns(self, df):
        """Analyze volume patterns in the data"""
        if df is None or len(df) < 10:
            return []
        
        patterns = []
        recent = df.tail(10)
        
        # 1. V-Pattern Detection
        if len(recent) >= 7:
            # Volume spike in middle days
            middle_volumes = recent['Volume'].iloc[2:5].mean()
            avg_volume = recent['Volume'].mean()
            
            if middle_volumes > avg_volume * 1.5:
                patterns.append('V-Pattern')
        
        # 2. U-Pattern Detection
        if len(recent) >= 7:
            # Volume dips in middle, high at ends
            start_vol = recent['Volume'].iloc[0]
            end_vol = recent['Volume'].iloc[-1]
            middle_vol = recent['Volume'].iloc[2:5].mean()
            
            if middle_vol < start_vol * 0.7 and middle_vol < end_vol * 0.7:
                patterns.append('U-Pattern')
        
        # 3. 3+3 Pattern
        if len(recent) >= 6:
            # Check for 3 high volume days followed by 3 low volume days
            first_half = recent['Volume'].iloc[:3].mean()
            second_half = recent['Volume'].iloc[3:6].mean()
            
            if (first_half > second_half * 1.8) or (second_half > first_half * 1.8):
                patterns.append('3+3 Pattern')
        
        # 4. Pyramid Pattern
        if len(recent) >= 5:
            volumes = recent['Volume'].iloc[:5].values
            if volumes[0] < volumes[1] < volumes[2] > volumes[3] > volumes[4]:
                patterns.append('Pyramid')
        
        # 5. Increasing Pattern
        if len(recent) >= 3:
            last_3_volumes = recent['Volume'].iloc[-3:].values
            if last_3_volumes[0] < last_3_volumes[1] < last_3_volumes[2]:
                patterns.append('Increasing')
        
        # 6. Decreasing Pattern
        if len(recent) >= 3:
            last_3_volumes = recent['Volume'].iloc[-3:].values
            if last_3_volumes[0] > last_3_volumes[1] > last_3_volumes[2]:
                patterns.append('Decreasing')
        
        return patterns
    
    def scan_v_patterns(self, limit=10):
        """Scan specifically for V patterns"""
        results = []
        count = 0
        
        for symbol in list(self.stocks.keys())[:limit]:
            df = self.fetch_stock_data(symbol)
            patterns = self.analyze_patterns(df)
            
            if 'V-Pattern' in patterns:
                stock_info = self.get_stock_info(symbol, df)
                stock_info['pattern'] = 'V-Pattern'
                results.append(stock_info)
                count += 1
            
            time.sleep(0.2)
            if count >= limit:
                break
        
        return results
    
    def scan_u_patterns(self, limit=10):
        """Scan specifically for U patterns"""
        results = []
        count = 0
        
        for symbol in list(self.stocks.keys())[:limit]:
            df = self.fetch_stock_data(symbol)
            patterns = self.analyze_patterns(df)
            
            if 'U-Pattern' in patterns:
                stock_info = self.get_stock_info(symbol, df)
                stock_info['pattern'] = 'U-Pattern'
                results.append(stock_info)
                count += 1
            
            time.sleep(0.2)
            if count >= limit:
                break
        
        return results
    
    def scan_3plus3_patterns(self, limit=10):
        """Scan for 3+3 patterns"""
        results = []
        count = 0
        
        for symbol in list(self.stocks.keys())[:limit]:
            df = self.fetch_stock_data(symbol)
            patterns = self.analyze_patterns(df)
            
            if '3+3 Pattern' in patterns:
                stock_info = self.get_stock_info(symbol, df)
                stock_info['pattern'] = '3+3 Pattern'
                results.append(stock_info)
                count += 1
            
            time.sleep(0.2)
            if count >= limit:
                break
        
        return results
    
    def scan_pyramid_patterns(self, limit=10):
        """Scan for pyramid patterns"""
        results = []
        count = 0
        
        for symbol in list(self.stocks.keys())[:limit]:
            df = self.fetch_stock_data(symbol)
            patterns = self.analyze_patterns(df)
            
            if 'Pyramid' in patterns:
                stock_info = self.get_stock_info(symbol, df)
                stock_info['pattern'] = 'Pyramid'
                results.append(stock_info)
                count += 1
            
            time.sleep(0.2)
            if count >= limit:
                break
        
        return results
    
    def scan_increasing_patterns(self, limit=10):
        """Scan for increasing volume patterns"""
        results = []
        count = 0
        
        for symbol in list(self.stocks.keys())[:limit]:
            df = self.fetch_stock_data(symbol)
            patterns = self.analyze_patterns(df)
            
            if 'Increasing' in patterns:
                stock_info = self.get_stock_info(symbol, df)
                stock_info['pattern'] = 'Increasing'
                results.append(stock_info)
                count += 1
            
            time.sleep(0.2)
            if count >= limit:
                break
        
        return results
    
    def scan_decreasing_patterns(self, limit=10):
        """Scan for decreasing volume patterns"""
        results = []
        count = 0
        
        for symbol in list(self.stocks.keys())[:limit]:
            df = self.fetch_stock_data(symbol)
            patterns = self.analyze_patterns(df)
            
            if 'Decreasing' in patterns:
                stock_info = self.get_stock_info(symbol, df)
                stock_info['pattern'] = 'Decreasing'
                results.append(stock_info)
                count += 1
            
            time.sleep(0.2)
            if count >= limit:
                break
        
        return results
    
    def get_stock_info(self, symbol, df=None):
        """Get stock information with real/fallback data"""
        try:
            if df is None:
                df = self.fetch_stock_data(symbol, days=5)
            
            if df is not None and not df.empty:
                latest = df.iloc[-1]
                prev = df.iloc[-2] if len(df) > 1 else latest
                
                price_change = 0
                if prev['Close'] > 0:
                    price_change = ((latest['Close'] - prev['Close']) / prev['Close']) * 100
                
                return {
                    'symbol': symbol.replace('.NS', ''),
                    'price': round(float(latest['Close']), 2),
                    'volume': int(latest['Volume']),
                    'change': round(float(price_change), 2),
                    'volume_ratio': round(float(latest.get('Volume_Ratio', 1)), 2),
                    'sector': self.stocks.get(symbol, 'N/A'),
                    'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M')
                }
        except:
            pass
        
        # Fallback
        return {
            'symbol': symbol.replace('.NS', ''),
            'price': self.current_prices.get(symbol, 1000.00),
            'volume': 5000000,
            'change': 0.0,
            'volume_ratio': 1.0,
            'sector': self.stocks.get(symbol, 'N/A'),
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M')
        }
    
    def quick_scan_all(self, limit=5):
        """Quick scan all stocks for any patterns"""
        results = []
        
        for symbol in list(self.stocks.keys())[:limit]:
            try:
                df = self.fetch_stock_data(symbol)
                patterns = self.analyze_patterns(df)
                
                if patterns:  # Only include stocks with detected patterns
                    stock_info = self.get_stock_info(symbol, df)
                    stock_info['patterns'] = patterns
                    results.append(stock_info)
                
                time.sleep(0.3)
            except:
                continue
        
        return results