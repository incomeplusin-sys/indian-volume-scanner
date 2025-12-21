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
    
    def fetch_stock_data(self, symbol, days=20):
        """Fetch stock data - NO FALLBACK TO DEMO"""
        try:
            stock = yf.Ticker(symbol)
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)
            
            # Fetch data
            df = stock.history(start=start_date, end=end_date, interval='1d')
            
            if df.empty or len(df) < 10:
                return None  # NO DATA, NO DEMO
            
            # Calculate indicators
            df['Volume_MA5'] = df['Volume'].rolling(window=5).mean()
            df['Volume_MA20'] = df['Volume'].rolling(window=20).mean()
            df['Price_Change'] = df['Close'].pct_change() * 100
            df['Volume_Change'] = df['Volume'].pct_change() * 100
            df['Volume_Ratio'] = df['Volume'] / df['Volume_MA20']
            
            return df
        except Exception as e:
            print(f"Error fetching {symbol}: {e}")
            return None  # NO DATA, NO DEMO
    
    def analyze_patterns(self, df):
        """Analyze volume patterns in the data"""
        if df is None or len(df) < 10:
            return []  # NO PATTERNS, NOT RANDOM ONES
        
        patterns = []
        recent = df.tail(10)
        
        # 1. V-Pattern Detection
        if len(recent) >= 7:
            middle_volumes = recent['Volume'].iloc[2:5].mean()
            avg_volume = recent['Volume'].mean()
            if middle_volumes > avg_volume * 1.5:
                patterns.append('V-Pattern')
        
        # 2. U-Pattern Detection
        if len(recent) >= 7:
            start_vol = recent['Volume'].iloc[0]
            end_vol = recent['Volume'].iloc[-1]
            middle_vol = recent['Volume'].iloc[2:5].mean()
            if middle_vol < start_vol * 0.7 and middle_vol < end_vol * 0.7:
                patterns.append('U-Pattern')
        
        # 3. 3+3 Pattern
        if len(recent) >= 6:
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
    
    def get_stock_info(self, symbol, df):
        """Get REAL stock information - NO DEMO DATA"""
        if df is None or df.empty:
            return None  # NO DATA, NO DEMO
        
        try:
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
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M'),
                'data_source': 'real_yfinance'
            }
        except:
            return None  # NO DATA, NO DEMO
    
    # ALL SCAN METHODS UPDATED TO RETURN ONLY REAL DATA
    def scan_v_patterns(self, limit=10):
        """Scan for V patterns - REAL DATA ONLY"""
        results = []
        
        for symbol in list(self.stocks.keys())[:limit]:
            df = self.fetch_stock_data(symbol)
            patterns = self.analyze_patterns(df)
            
            if 'V-Pattern' in patterns:
                stock_info = self.get_stock_info(symbol, df)
                if stock_info:  # Only add if we have real data
                    stock_info['pattern'] = 'V-Pattern'
                    results.append(stock_info)
            
            time.sleep(0.2)
        
        return results  # Could be empty - NO DEMO DATA
    
    def scan_u_patterns(self, limit=10):
        """Scan for U patterns - REAL DATA ONLY"""
        results = []
        
        for symbol in list(self.stocks.keys())[:limit]:
            df = self.fetch_stock_data(symbol)
            patterns = self.analyze_patterns(df)
            
            if 'U-Pattern' in patterns:
                stock_info = self.get_stock_info(symbol, df)
                if stock_info:
                    stock_info['pattern'] = 'U-Pattern'
                    results.append(stock_info)
            
            time.sleep(0.2)
        
        return results
    
    def scan_3plus3_patterns(self, limit=10):
        """Scan for 3+3 patterns - REAL DATA ONLY"""
        results = []
        
        for symbol in list(self.stocks.keys())[:limit]:
            df = self.fetch_stock_data(symbol)
            patterns = self.analyze_patterns(df)
            
            if '3+3 Pattern' in patterns:
                stock_info = self.get_stock_info(symbol, df)
                if stock_info:
                    stock_info['pattern'] = '3+3 Pattern'
                    results.append(stock_info)
            
            time.sleep(0.2)
        
        return results
    
    def scan_pyramid_patterns(self, limit=10):
        """Scan for pyramid patterns - REAL DATA ONLY"""
        results = []
        
        for symbol in list(self.stocks.keys())[:limit]:
            df = self.fetch_stock_data(symbol)
            patterns = self.analyze_patterns(df)
            
            if 'Pyramid' in patterns:
                stock_info = self.get_stock_info(symbol, df)
                if stock_info:
                    stock_info['pattern'] = 'Pyramid'
                    results.append(stock_info)
            
            time.sleep(0.2)
        
        return results
    
    def scan_increasing_patterns(self, limit=10):
        """Scan for increasing patterns - REAL DATA ONLY"""
        results = []
        
        for symbol in list(self.stocks.keys())[:limit]:
            df = self.fetch_stock_data(symbol)
            patterns = self.analyze_patterns(df)
            
            if 'Increasing' in patterns:
                stock_info = self.get_stock_info(symbol, df)
                if stock_info:
                    stock_info['pattern'] = 'Increasing'
                    results.append(stock_info)
            
            time.sleep(0.2)
        
        return results
    
    def scan_decreasing_patterns(self, limit=10):
        """Scan for decreasing patterns - REAL DATA ONLY"""
        results = []
        
        for symbol in list(self.stocks.keys())[:limit]:
            df = self.fetch_stock_data(symbol)
            patterns = self.analyze_patterns(df)
            
            if 'Decreasing' in patterns:
                stock_info = self.get_stock_info(symbol, df)
                if stock_info:
                    stock_info['pattern'] = 'Decreasing'
                    results.append(stock_info)
            
            time.sleep(0.2)
        
        return results
    
    def quick_scan_all(self, limit=5):
        """Quick scan - REAL DATA ONLY"""
        results = []
        
        for symbol in list(self.stocks.keys())[:limit]:
            df = self.fetch_stock_data(symbol)
            patterns = self.analyze_patterns(df)
            
            if patterns:  # Only include stocks with detected patterns
                stock_info = self.get_stock_info(symbol, df)
                if stock_info:  # Only include if we have real data
                    stock_info['patterns'] = patterns
                    results.append(stock_info)
            
            time.sleep(0.3)
        
        return results  # Could be empty - NO DEMO DATA