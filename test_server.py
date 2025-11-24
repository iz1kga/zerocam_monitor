#!/usr/bin/env python3
"""
Server Flask di esempio per ricevere i dati dal monitor
Utile per testare il sistema senza avere un'API vera
"""

from flask import Flask, request, jsonify
from datetime import datetime
import json

app = Flask(__name__)

# Token di esempio (usa lo stesso nel config.json)
VALID_TOKEN = "test-bearer-token-123456"


@app.route('/monitoring', methods=['POST'])
def receive_monitoring_data():
    """Endpoint che riceve i dati di monitoraggio"""
    
    # Verifica autenticazione Bearer
    auth_header = request.headers.get('Authorization', '')
    
    if not auth_header.startswith('Bearer '):
        return jsonify({'error': 'Missing or invalid Authorization header'}), 401
    
    token = auth_header.replace('Bearer ', '')
    
    if token != VALID_TOKEN:
        return jsonify({'error': 'Invalid token'}), 401
    
    # Ottieni i dati JSON
    try:
        data = request.get_json()
    except Exception as e:
        return jsonify({'error': f'Invalid JSON: {str(e)}'}), 400
    
    # Stampa i dati ricevuti
    print("\n" + "=" * 80)
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] DATI RICEVUTI DAL RASPBERRY PI")
    print("=" * 80)
    print(json.dumps(data, indent=2, ensure_ascii=False))
    print("=" * 80)
    print()
    
    # Salva in un file (opzionale)
    with open('received_data.jsonl', 'a') as f:
        f.write(json.dumps(data) + '\n')
    
    # Risposta di successo
    return jsonify({
        'status': 'success',
        'message': 'Data received successfully',
        'timestamp': datetime.now().isoformat()
    }), 200


@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'Raspberry Monitor Test API',
        'timestamp': datetime.now().isoformat()
    }), 200


if __name__ == '__main__':
    print("\n" + "=" * 80)
    print("SERVER API DI TEST PER RASPBERRY PI MONITOR")
    print("=" * 80)
    print()
    print("Il server è in ascolto su: http://0.0.0.0:5000")
    print()
    print("Configurazione da usare nel Raspberry Pi:")
    print("-" * 80)
    print('  "api_url": "http://<IP_DI_QUESTO_SERVER>:5000/monitoring"')
    print(f'  "api_bearer_token": "{VALID_TOKEN}"')
    print("-" * 80)
    print()
    print("Endpoints disponibili:")
    print("  POST /monitoring  - Riceve i dati di monitoraggio")
    print("  GET  /health      - Health check")
    print()
    print("I dati ricevuti verranno salvati in: received_data.jsonl")
    print("=" * 80)
    print()
    
    app.run(host='0.0.0.0', port=5000, debug=True)
