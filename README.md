# Raspberry Pi System Monitor

Sistema di monitoraggio per Raspberry Pi che raccoglie dati di sistema (CPU, RAM, disco, connettività), li invia a un'API REST con autenticazione Bearer e li salva localmente con rotazione automatica dei log.

## 🎯 Cosa Monitora

- **Disco**: Spazio totale, usato, libero (GB) e percentuale
- **Ethernet**: Stato connessione, interfaccia, IP
- **WiFi**: Stato, IP e intensità segnale (dBm)
- **CPU**: Percentuale max e media nel periodo
- **RAM**: Percentuale max e media + snapshot corrente

## ⚙️ Funzionalità

- ✅ Invio dati REST API POST con Bearer Token
- ✅ Log locale con rotazione (10MB × 5 file)
- ✅ Riavvio automatico se Internet assente > K minuti (default 15)
- ✅ Servizio systemd con avvio automatico al boot
- ✅ Virtual environment Python isolato

---

## 🚀 Installazione Rapida

```bash
# 1. Clona il repository
git clone <repository-url>
cd zerocamMonitor

# 2. Installa il servizio
chmod +x install.sh
sudo ./install.sh

# 3. Configura API URL e Bearer Token
sudo nano /etc/raspberry-monitor/config.json

# 4. Avvia il servizio
sudo systemctl start raspberry-monitor
sudo systemctl status raspberry-monitor
```

### Configurazione Minima Richiesta

File `/etc/raspberry-monitor/config.json`:

```json
{
    "device_id": "webcam-001",
    "api_url": "https://api.tuoserver.com/monitoring",
    "api_bearer_token": "YOUR_TOKEN_HERE",
    "check_period_minutes": 1,
    "sample_interval_seconds": 5,
    "reboot_timeout_minutes": 15
}
```

**Parametri:**
- `device_id`: **ID univoco del dispositivo/webcam** (es: "webcam-villar", "cam-001")
- `api_url`: URL dell'API REST
- `api_bearer_token`: Token di autenticazione
- `check_period_minutes`: Ogni quanto inviare i dati (default: 1)
- `sample_interval_seconds`: Intervallo campionamento (default: 5)
- `reboot_timeout_minutes`: Minuti senza Internet prima del riboot (default: 15)

---

## � Payload API REST

### Endpoint
```
POST {api_url}
Authorization: Bearer {api_bearer_token}
Content-Type: application/json
```

### Struttura Dati Inviati

```json
{
    "device_id": "webcam-001",
    "timestamp": "2025-11-24T10:30:00.123456",
    "period_seconds": 60,
    "samples_count": 12,
    
    "disk": {
        "total_gb": 29.72,
        "used_gb": 5.43,
        "free_gb": 22.79,
        "percent": 19.2
    },
    
    "ethernet": {
        "interface": "eth0",           // o null se non disponibile
        "connected": true,
        "ip_address": "192.168.1.100"  // o null
    },
    
    "wifi": {
        "interface": "wlan0",          // o null
        "connected": true,
        "ip_address": "192.168.1.101", // o null
        "signal_strength_dbm": -45     // o null (da -30 ottimo a -90 pessimo)
    },
    
    "cpu": {
        "max_percent": 45.2,           // Massimo nel periodo
        "avg_percent": 23.5,           // Media nel periodo
        "samples": 12
    },
    
    "memory": {
        "max_percent": 62.3,           // Massimo nel periodo
        "avg_percent": 58.7,           // Media nel periodo
        "current": {                   // Snapshot attuale
            "total_mb": 3892.45,
            "used_mb": 2245.32,
            "available_mb": 1647.13,
            "percent": 57.7
        },
        "samples": 12
    }
}
```

### Campi Principali

| Campo | Tipo | Descrizione |
|-------|------|-------------|
| `device_id` | string | **ID univoco del dispositivo/webcam** |
| `timestamp` | string | ISO 8601 timestamp dell'invio |
| `period_seconds` | int | Durata periodo di raccolta dati |
| `samples_count` | int | Numero campioni raccolti |
| **disk** | | |
| `total_gb`, `used_gb`, `free_gb` | float | Spazio disco in GB |
| `percent` | float | Percentuale utilizzo disco |
| **ethernet** | | |
| `interface` | string\|null | Nome interfaccia (es: "eth0") |
| `connected` | bool | Stato connessione |
| `ip_address` | string\|null | Indirizzo IPv4 |
| **wifi** | | |
| `signal_strength_dbm` | int\|null | Intensità segnale (-30=ottimo, -90=pessimo) |
| **cpu** | | |
| `max_percent`, `avg_percent` | float | CPU massima e media nel periodo |
| **memory** | | |
| `max_percent`, `avg_percent` | float | RAM massima e media nel periodo |
| `current.total_mb` | float | RAM totale installata |
| `current.used_mb` | float | RAM in uso |
| `current.available_mb` | float | RAM disponibile |

### Response Attesa

```json
{
    "status": "success",
    "message": "Data received successfully",
    "timestamp": "2025-11-24T10:30:45.123456"
}
```

### Esempio Server (Python/Flask)

```python
from flask import Flask, request, jsonify

app = Flask(__name__)
VALID_TOKEN = "your-token-here"

@app.route('/monitoring', methods=['POST'])
def receive_monitoring():
    # Verifica autenticazione
    auth = request.headers.get('Authorization', '')
    if not auth.startswith('Bearer ') or auth.replace('Bearer ', '') != VALID_TOKEN:
        return jsonify({'error': 'Unauthorized'}), 401
    
    # Ricevi dati
    data = request.get_json()
    device_id = data.get('device_id', 'unknown')
    print(f"Dati ricevuti da {device_id}: {data['timestamp']}")
    
    # Salva nel database usando device_id come chiave...
    
    return jsonify({'status': 'success'}), 200
```

> 📖 **Documentazione API completa**: [API_DOCUMENTATION.md](API_DOCUMENTATION.md)  
> Include: schema JSON, esempi Node.js/PHP, test cURL, validazione

---

## 🔧 Comandi Utili

```bash
# Gestione servizio
sudo systemctl start|stop|restart|status raspberry-monitor
sudo systemctl enable|disable raspberry-monitor

# Visualizza log in tempo reale
sudo journalctl -u raspberry-monitor -f
sudo tail -f /var/log/raspberry-monitor/monitor.log

# Estrai solo i dati JSON dai log
sudo grep "DATA:" /var/log/raspberry-monitor/monitor.log

# Test prima dell'installazione
./dev-test.sh

# Disinstallazione
sudo ./uninstall.sh
```

---

## 🐛 Troubleshooting

| Problema | Soluzione |
|----------|-----------|
| Servizio non si avvia | `sudo journalctl -u raspberry-monitor -n 50` |
| Errori API | Verifica URL, token e che il server accetti POST JSON |
| Segnale WiFi non disponibile | Installa `wireless-tools`: `sudo apt-get install wireless-tools` |
| Sistema non si riavvia | Verifica permessi root e log connettività |

---

## 📚 Documentazione Completa

- **[API_DOCUMENTATION.md](API_DOCUMENTATION.md)** - Documentazione API dettagliata con esempi server Node.js/PHP, schema JSON, test cURL
- **File installati**:
  - `/opt/raspberry-monitor/` - Programma e virtualenv
  - `/etc/raspberry-monitor/config.json` - Configurazione
  - `/var/log/raspberry-monitor/monitor.log` - Log con rotazione automatica

---

## ⚡ Info Tecniche

**Risorse utilizzate:**
- CPU: < 1% | RAM: ~30-50 MB | Disco: ~50 MB | Network: ~1-5 KB/periodo

**Compatibilità:**
- Raspberry Pi Zero/W, 2/3/4/5 e dispositivi ARM con Linux

**Controllo Connettività:**
- Metodo: HTTP Request a 8.8.8.8, 1.1.1.1, google.com
- Alternative disponibili: Ping ICMP, DNS, Socket TCP (vedi documentazione)
