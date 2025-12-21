from flask import Flask, render_template, jsonify, request
from scanner_integration import VolumePatternScanner
import time

app = Flask(__name__)
scanner = VolumePatternScanner()

@app.route('/')
def home():
    return render_template('index.html')

# NEW TEST ROUTE - ADD THIS
@app.route('/api/test-yfinance')
def test_yfinance():
    try:
        import yfinance as yf
        ticker = yf.Ticker("RELIANCE.NS")
        data = ticker.history(period="1d")
        return jsonify({
            'success': not data.empty,
            'data_length': len(data),
            'columns': list(data.columns) if not data.empty else [],
            'sample_data': data.to_dict() if not data.empty else {}
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/scan/<pattern_type>')
def scan_pattern(pattern_type):
    try:
        if pattern_type == 'v_pattern':
            results = scanner.scan_v_patterns(limit=15)
        elif pattern_type == 'u_pattern':
            results = scanner.scan_u_patterns(limit=15)
        elif pattern_type == '3plus3':
            results = scanner.scan_3plus3_patterns(limit=15)
        elif pattern_type == 'pyramid':
            results = scanner.scan_pyramid_patterns(limit=15)
        elif pattern_type == 'increasing':
            results = scanner.scan_increasing_patterns(limit=15)
        elif pattern_type == 'decreasing':
            results = scanner.scan_decreasing_patterns(limit=15)
        elif pattern_type == 'quick':
            results = scanner.quick_scan_all(limit=10)
        else:
            return jsonify({'error': 'Invalid pattern type'}), 400
        
        return jsonify(results)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/status')
def status():
    return jsonify({
        'status': 'online',
        'patterns': ['V-Pattern', 'U-Pattern', '3+3 Pattern', 'Pyramid', 'Increasing', 'Decreasing']
    })

@app.route('/health')
def health():
    return jsonify({'status': 'healthy'})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)