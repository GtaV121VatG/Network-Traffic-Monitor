from flask import Flask, jsonify
from flask_cors import CORS
from monitor import NetworkMonitor
import threading
import time

app = Flask(__name__)
CORS(app)

monitor = NetworkMonitor()

latest_data = {
    'summary': {},
    'history': []
}

def background_monitoring():
    global latest_data
    
    while True:
        try:
            summary = monitor.get_summary()
            latest_data['summary'] = summary
            
            latest_data['history'].append({
                'timestamp': summary['timestamp'],
                'active_connections': summary['active_connections'],
                'total_alerts': summary['total_alerts']
            })
            
            if len(latest_data['history']) > 50:
                latest_data['history'].pop(0)
                
        except Exception:
            pass
        
        time.sleep(2)

@app.route('/api/status', methods=['GET'])
def get_status():
    return jsonify({
        'status': 'active',
        'message': 'Network monitoring is running'
    })

@app.route('/api/summary', methods=['GET'])
def get_summary():
    return jsonify(latest_data['summary'])

@app.route('/api/connections', methods=['GET'])
def get_connections():
    summary = latest_data.get('summary', {})
    return jsonify({
        'connections': summary.get('connections', []),
        'count': summary.get('active_connections', 0)
    })

@app.route('/api/alerts', methods=['GET'])
def get_alerts():
    summary = latest_data.get('summary', {})
    return jsonify({
        'alerts': summary.get('alerts', []),
        'count': summary.get('total_alerts', 0)
    })

@app.route('/api/history', methods=['GET'])
def get_history():
    return jsonify(latest_data['history'])

@app.route('/api/stats', methods=['GET'])
def get_stats():
    summary = latest_data.get('summary', {})
    return jsonify({
        'active_connections': summary.get('active_connections', 0),
        'total_alerts': summary.get('total_alerts', 0),
        'suspicious_ips': summary.get('suspicious_ips', 0),
        'network_stats': summary.get('network_stats', {}),
        'network_info': summary.get('network_info', []),
        'device_type': summary.get('device_type', 'Unknown')
    })

if __name__ == '__main__':
    monitor_thread = threading.Thread(target=background_monitoring, daemon=True)
    monitor_thread.start()
    app.run(debug=True, host='0.0.0.0', port=5000, use_reloader=False)