import yfinance as yf
import pandas as pd
import numpy as np
import time
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

class VolumePatternScanner:
    def __init__(self):
        # Indian stocks with sectors
        self.stocks = {
            "RELIANCE.NS": {"sector": "Energy", "patterns": []},
            "TCS.NS": {"sector": "IT", "patterns": []},
            "INFY.NS": {"sector": "IT", "patterns": []},
            "HDFCBANK.NS": {"sector": "Banking", "patterns": []},
            "ICICIBANK.NS": {"sector": "Banking", "patterns": []},
            "SBIN.NS": {"sector": "Banking", "patterns": []},
            "BHARTIARTL.NS": {"sector": "Telecom", "patterns": []},
            "KOTAKBANK.NS": {"sector": "Banking", "patterns": []},
            "ITC.NS": {"sector": "FMCG", "patterns": []},
            "ASIANPAINT.NS": {"sector": "Paint", "patterns": []}
        }
        
        # Pattern definitions
        self.pattern_definitions = {
            'V-Pattern': 'Volume spike followed by price reversal',
            'U-Pattern': 'Gradual volume accumulation',
            '3+3 Pattern': '3 days high volume, 3 days low volume',
            'Pyramid': 'Volume increases then decreases symmetrically',
            'Increasing': 'Consistently rising volume',
            'Decreasing': 'Consistently falling volume'
        }
    
    def fetch_historical_data(self, symbol, years=2):
        """Fetch 2 years of historical data"""
        try:
            stock = yf.Ticker(symbol)
            
            # Get 2 years data for pattern analysis
            end_date = datetime.now()
            start_date = end_date - timedelta(days=years*365)
            
            df = stock.history(start=start_date, end=end_date, interval='1d')
            
            if df.empty or len(df) < 100:  # Need at least 100 trading days
                return None
            
            # Calculate indicators
            df['Volume_MA20'] = df['Volume'].rolling(window=20).mean()
            df['Price_Change'] = df['Close'].pct_change() * 100
            df['Volume_Change'] = df['Volume'].pct_change() * 100
            df['Volume_Ratio'] = df['Volume'] / df['Volume_MA20']
            
            # Add rolling patterns detection
            df = self.detect_patterns_in_dataframe(df)
            
            return df
            
        except Exception as e:
            print(f"Error fetching {symbol}: {e}")
            return None
    
    def detect_patterns_in_dataframe(self, df):
        """Add pattern detection columns to DataFrame"""
        if df is None or len(df) < 30:
            return df
        
        # Initialize pattern columns
        for pattern in self.pattern_definitions.keys():
            df[f'{pattern}_flag'] = 0
        
        # Scan through the data with a rolling window
        for i in range(10, len(df)):
            window = df.iloc[i-10:i]
            
            # V-Pattern (days 0-2: normal, days 3-5: spike, days 6-9: recovery)
            if len(window) >= 10:
                middle_volumes = window['Volume'].iloc[3:6].mean()
                avg_volume = window['Volume'].mean()
                if middle_volumes > avg_volume * 1.8:
                    df.at[df.index[i-1], 'V-Pattern_flag'] = 1
            
            # U-Pattern (ends high, middle low)
            if len(window) >= 7:
                start_vol = window['Volume'].iloc[0]
                end_vol = window['Volume'].iloc[-1]
                middle_vol = window['Volume'].iloc[2:5].mean()
                if middle_vol < start_vol * 0.6 and middle_vol < end_vol * 0.6:
                    df.at[df.index[i-1], 'U-Pattern_flag'] = 1
            
            # 3+3 Pattern
            if len(window) >= 6:
                first_half = window['Volume'].iloc[:3].mean()
                second_half = window['Volume'].iloc[3:6].mean()
                if (first_half > second_half * 2.0) or (second_half > first_half * 2.0):
                    df.at[df.index[i-1], '3+3 Pattern_flag'] = 1
            
            # Pyramid Pattern (5-day symmetry)
            if len(window) >= 5:
                volumes = window['Volume'].iloc[:5].values
                if volumes[0] < volumes[1] < volumes[2] > volumes[3] > volumes[4]:
                    df.at[df.index[i-1], 'Pyramid_flag'] = 1
            
            # Increasing Pattern (last 3 days)
            if len(window) >= 3:
                last_3 = window['Volume'].iloc[-3:].values
                if last_3[0] < last_3[1] < last_3[2]:
                    df.at[df.index[i-1], 'Increasing_flag'] = 1
            
            # Decreasing Pattern (last 3 days)
            if len(window) >= 3:
                last_3 = window['Volume'].iloc[-3:].values
                if last_3[0] > last_3[1] > last_3[2]:
                    df.at[df.index[i-1], 'Decreasing_flag'] = 1
        
        return df
    
    def get_recent_patterns(self, df, days_lookback=180):
        """Get patterns from last 6 months"""
        if df is None or len(df) < days_lookback/5:  # Approx trading days
            return []
        
        recent_data = df.tail(int(days_lookback/5))  # Last ~6 months
        
        patterns_found = []
        
        for pattern in self.pattern_definitions.keys():
            flag_col = f'{pattern}_flag'
            if flag_col in recent_data.columns:
                pattern_dates = recent_data[recent_data[flag_col] == 1].index
                
                for date in pattern_dates:
                    idx = df.index.get_loc(date)
                    
                    # Get price performance after pattern
                    if idx + 5 < len(df):
                        price_at_pattern = df.iloc[idx]['Close']
                        price_5_days_later = df.iloc[idx + 5]['Close']
                        performance = ((price_5_days_later - price_at_pattern) / price_at_pattern) * 100
                    else:
                        performance = None
                    
                    patterns_found.append({
                        'pattern': pattern,
                        'date': date.strftime('%Y-%m-%d'),
                        'price_at_pattern': round(float(df.iloc[idx]['Close']), 2),
                        'volume_at_pattern': int(df.iloc[idx]['Volume']),
                        'performance_5d': round(float(performance), 2) if performance is not None else 'N/A',
                        'current_price': round(float(df.iloc[-1]['Close']), 2),
                        'days_ago': (datetime.now() - date).days
                    })
        
        return patterns_found
    
    def get_stock_summary(self, symbol):
        """Get comprehensive stock analysis"""
        df = self.fetch_historical_data(symbol, years=2)
        
        if df is None or df.empty:
            return None
        
        latest = df.iloc[-1]
        prev = df.iloc[-2] if len(df) > 1 else latest
        
        price_change = 0
        if prev['Close'] > 0:
            price_change = ((latest['Close'] - prev['Close']) / prev['Close']) * 100
        
        # Get recent patterns
        recent_patterns = self.get_recent_patterns(df, days_lookback=180)
        
        # Count total patterns in history
        total_patterns = {}
        for pattern in self.pattern_definitions.keys():
            flag_col = f'{pattern}_flag'
            if flag_col in df.columns:
                total_patterns[pattern] = int(df[flag_col].sum())
        
        return {
            'symbol': symbol.replace('.NS', ''),
            'current_price': round(float(latest['Close']), 2),
            'volume': int(latest['Volume']),
            'change': round(float(price_change), 2),
            'sector': self.stocks[symbol]['sector'],
            'total_patterns_found': total_patterns,
            'recent_patterns': recent_patterns[:10],  # Last 10 patterns
            'total_pattern_count': sum(total_patterns.values()),
            'data_period': f"{(datetime.now() - df.index[0]).days} days",
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M')
        }
    
    # SCAN METHODS - Now showing historical patterns
    
    def scan_v_patterns(self, limit=10):
        """Show V-Patterns from last 6 months"""
        results = []
        
        for symbol in list(self.stocks.keys())[:limit]:
            summary = self.get_stock_summary(symbol)
            
            if summary and summary['recent_patterns']:
                # Filter for V-Patterns only
                v_patterns = [p for p in summary['recent_patterns'] if p['pattern'] == 'V-Pattern']
                
                if v_patterns:
                    # Get most recent V-Pattern
                    latest_v = v_patterns[0]
                    
                    results.append({
                        'symbol': summary['symbol'],
                        'pattern': 'V-Pattern',
                        'last_occurrence': latest_v['date'],
                        'days_ago': latest_v['days_ago'],
                        'price_then': latest_v['price_at_pattern'],
                        'current_price': summary['current_price'],
                        'performance': latest_v['performance_5d'],
                        'total_occurrences': summary['total_patterns_found'].get('V-Pattern', 0)
                    })
            
            time.sleep(0.3)
        
        return results
    
    def scan_u_patterns(self, limit=10):
        """Show U-Patterns from last 6 months"""
        results = []
        
        for symbol in list(self.stocks.keys())[:limit]:
            summary = self.get_stock_summary(symbol)
            
            if summary and summary['recent_patterns']:
                u_patterns = [p for p in summary['recent_patterns'] if p['pattern'] == 'U-Pattern']
                
                if u_patterns:
                    latest_u = u_patterns[0]
                    
                    results.append({
                        'symbol': summary['symbol'],
                        'pattern': 'U-Pattern',
                        'last_occurrence': latest_u['date'],
                        'days_ago': latest_u['days_ago'],
                        'price_then': latest_u['price_at_pattern'],
                        'current_price': summary['current_price'],
                        'performance': latest_u['performance_5d'],
                        'total_occurrences': summary['total_patterns_found'].get('U-Pattern', 0)
                    })
            
            time.sleep(0.3)
        
        return results
    
    # Add similar methods for other patterns...
    
    def scan_3plus3_patterns(self, limit=10):
        results = []
        
        for symbol in list(self.stocks.keys())[:limit]:
            summary = self.get_stock_summary(symbol)
            
            if summary and summary['recent_patterns']:
                patterns = [p for p in summary['recent_patterns'] if p['pattern'] == '3+3 Pattern']
                
                if patterns:
                    latest = patterns[0]
                    
                    results.append({
                        'symbol': summary['symbol'],
                        'pattern': '3+3 Pattern',
                        'last_occurrence': latest['date'],
                        'days_ago': latest['days_ago'],
                        'price_then': latest['price_at_pattern'],
                        'current_price': summary['current_price'],
                        'performance': latest['performance_5d'],
                        'total_occurrences': summary['total_patterns_found'].get('3+3 Pattern', 0)
                    })
            
            time.sleep(0.3)
        
        return results
    
    def scan_pyramid_patterns(self, limit=10):
        results = []
        
        for symbol in list(self.stocks.keys())[:limit]:
            summary = self.get_stock_summary(symbol)
            
            if summary and summary['recent_patterns']:
                patterns = [p for p in summary['recent_patterns'] if p['pattern'] == 'Pyramid']
                
                if patterns:
                    latest = patterns[0]
                    
                    results.append({
                        'symbol': summary['symbol'],
                        'pattern': 'Pyramid',
                        'last_occurrence': latest['date'],
                        'days_ago': latest['days_ago'],
                        'price_then': latest['price_at_pattern'],
                        'current_price': summary['current_price'],
                        'performance': latest['performance_5d'],
                        'total_occurrences': summary['total_patterns_found'].get('Pyramid', 0)
                    })
            
            time.sleep(0.3)
        
        return results
    
    def scan_increasing_patterns(self, limit=10):
        results = []
        
        for symbol in list(self.stocks.keys())[:limit]:
            summary = self.get_stock_summary(symbol)
            
            if summary and summary['recent_patterns']:
                patterns = [p for p in summary['recent_patterns'] if p['pattern'] == 'Increasing']
                
                if patterns:
                    latest = patterns[0]
                    
                    results.append({
                        'symbol': summary['symbol'],
                        'pattern': 'Increasing',
                        'last_occurrence': latest['date'],
                        'days_ago': latest['days_ago'],
                        'price_then': latest['price_at_pattern'],
                        'current_price': summary['current_price'],
                        'performance': latest['performance_5d'],
                        'total_occurrences': summary['total_patterns_found'].get('Increasing', 0)
                    })
            
            time.sleep(0.3)
        
        return results
    
    def scan_decreasing_patterns(self, limit=10):
        results = []
        
        for symbol in list(self.stocks.keys())[:limit]:
            summary = self.get_stock_summary(symbol)
            
            if summary and summary['recent_patterns']:
                patterns = [p for p in summary['recent_patterns'] if p['pattern'] == 'Decreasing']
                
                if patterns:
                    latest = patterns[0]
                    
                    results.append({
                        'symbol': summary['symbol'],
                        'pattern': 'Decreasing',
                        'last_occurrence': latest['date'],
                        'days_ago': latest['days_ago'],
                        'price_then': latest['price_at_pattern'],
                        'current_price': summary['current_price'],
                        'performance': latest['performance_5d'],
                        'total_occurrences': summary['total_patterns_found'].get('Decreasing', 0)
                    })
            
            time.sleep(0.3)
        
        return results
    
    def quick_scan_all(self, limit=5):
        """Quick scan showing stocks with recent patterns"""
        results = []
        
        for symbol in list(self.stocks.keys())[:limit]:
            summary = self.get_stock_summary(symbol)
            
            if summary and summary['recent_patterns']:
                # Get unique recent patterns
                recent_pattern_types = list(set([p['pattern'] for p in summary['recent_patterns'][:3]]))
                
                if recent_pattern_types:
                    results.append({
                        'symbol': summary['symbol'],
                        'current_price': summary['current_price'],
                        'change': summary['change'],
                        'recent_patterns': recent_pattern_types,
                        'last_pattern_date': summary['recent_patterns'][0]['date'] if summary['recent_patterns'] else 'N/A',
                        'total_patterns_history': summary['total_pattern_count']
                    })
            
            time.sleep(0.3)
        
        return results