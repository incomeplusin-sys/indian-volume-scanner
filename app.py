from flask import Flask, render_template, jsonify, request
from scanner_integration import VolumePatternScanner
import time
from datetime import datetime

from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)

app = Flask(__name__)
scanner = VolumePatternScanner()

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/api/test-yfinance')
def test_yfinance():
    """Test if yFinance is working correctly"""
    try:
        import yfinance as yf
        ticker = yf.Ticker("RELIANCE.NS")
        data = ticker.history(period="1d")
        
        # Also try to get current price
        info = ticker.info
        current_price = info.get('currentPrice') or info.get('regularMarketPrice')
        
        return jsonify({
            'success': not data.empty,
            'data_length': len(data),
            'current_price': current_price,
            'columns': list(data.columns) if not data.empty else [],
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/verify-prices')
def verify_prices():
    """Verify stock prices against real market prices"""
    test_stocks = ["RELIANCE.NS", "TCS.NS", "INFY.NS"]
    results = {}
    
    for symbol in test_stocks:
        try:
            import yfinance as yf
            ticker = yf.Ticker(symbol)
            info = ticker.info
            
            results[symbol] = {
                'currentPrice': info.get('currentPrice'),
                'regularMarketPrice': info.get('regularMarketPrice'),
                'previousClose': info.get('previousClose'),
                'open': info.get('open'),
                'dayHigh': info.get('dayHigh'),
                'dayLow': info.get('dayLow'),
                'volume': info.get('volume'),
                'data_source': 'yfinance'
            }
            
        except Exception as e:
            results[symbol] = {'error': str(e), 'data_source': 'failed'}
    
    return jsonify({
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'real_prices': {
            'RELIANCE.NS': 2565.10,
            'TCS.NS': 3282.00,
            'INFY.NS': 1492.34
        },
        'fetched': results
    })

@app.route('/api/scan/<pattern_type>')
def scan_pattern(pattern_type):
    """Main scanning endpoint for all pattern types"""
    try:
        start_time = time.time()
        
        if pattern_type == 'v_pattern':
            results = scanner.scan_v_patterns(limit=10)
        elif pattern_type == 'u_pattern':
            results = scanner.scan_u_patterns(limit=10)
        elif pattern_type == '3plus3':
            results = scanner.scan_3plus3_patterns(limit=10)
        elif pattern_type == 'pyramid':
            results = scanner.scan_pyramid_patterns(limit=10)
        elif pattern_type == 'increasing':
            results = scanner.scan_increasing_patterns(limit=10)
        elif pattern_type == 'decreasing':
            results = scanner.scan_decreasing_patterns(limit=10)
        elif pattern_type == 'quick':
            results = scanner.quick_scan_all(limit=10)
        else:
            return jsonify({
                'success': False,
                'error': 'Invalid pattern type',
                'pattern_type': pattern_type,
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }), 400
        
        scan_time = round(time.time() - start_time, 2)
        
        # Check if we got any results
        if not results:  # Empty list
            return jsonify({
                'success': True,
                'pattern_type': pattern_type,
                'count': 0,
                'scan_time_seconds': scan_time,
                'message': 'No patterns found in current market data',
                'data': [],
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            })
        
        return jsonify({
            'success': True,
            'pattern_type': pattern_type,
            'count': len(results),
            'scan_time_seconds': scan_time,
            'data': results,
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'pattern_type': pattern_type,
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }), 500

@app.route('/api/status')
def status():
    """API status endpoint"""
    return jsonify({
        'status': 'online',
        'service': 'Indian Volume Pattern Scanner',
        'patterns_available': ['v_pattern', 'u_pattern', '3plus3', 'pyramid', 'increasing', 'decreasing', 'quick'],
        'stocks_tracked': len(scanner.stocks),
        'version': '2.0',
        'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'endpoints': {
            '/': 'Home page',
            '/api/scan/{pattern}': 'Scan for patterns',
            '/api/status': 'This status page',
            '/api/test-yfinance': 'Test yFinance connection',
            '/api/verify-prices': 'Verify stock prices',
            '/health': 'Health check',
            '/api/stocks': 'List tracked stocks'
        }
    })

@app.route('/health')
def health():
    """Health check endpoint for Render"""
    return jsonify({
        'status': 'healthy',
        'service': 'Indian Volume Pattern Scanner',
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/stocks')
def get_stocks():
    """Get list of all tracked stocks"""
    return jsonify({
        'stocks': [{'symbol': s.replace('.NS', ''), 'sector': scanner.stocks.get(s, 'N/A')} 
                  for s in scanner.stocks.keys()],
        'count': len(scanner.stocks),
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    })

@app.route('/api/test-imports')
def test_imports():
    """Test all imports are working"""
    import_results = {}
    
    libraries = ['flask', 'pandas', 'numpy', 'yfinance', 'requests']
    
    for lib in libraries:
        try:
            module = __import__(lib)
            import_results[lib] = {
                'status': 'OK',
                'version': getattr(module, '__version__', 'Unknown')
            }
        except Exception as e:
            import_results[lib] = {
                'status': 'ERROR',
                'error': str(e)
            }
    
    return jsonify({
        'imports': import_results,
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    })

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint not found', 'status': 404}), 404

@app.errorhandler(500)
def server_error(error):
    return jsonify({'error': 'Internal server error', 'status': 500}), 500

if __name__ == '__main__':
    print("=" * 50)
    print("Indian Volume Pattern Scanner Starting...")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Stocks tracked: {len(scanner.stocks)}")
    print("Endpoints available:")
    print("  /              - Home page")
    print("  /api/scan/*    - Pattern scanning")
    print("  /api/status    - Service status")
    print("  /health        - Health check")
    print("=" * 50)
    
    app.run(host='0.0.0.0', port=5000, debug=False)