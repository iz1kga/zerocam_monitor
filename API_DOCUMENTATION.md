# API Documentation - Raspberry Pi Monitor

## 📡 Endpoint REST

### POST `/monitoring` (o il tuo endpoint configurato)

Riceve i dati di monitoraggio dal Raspberry Pi.

---

## 🔐 Autenticazione

L'API richiede autenticazione tramite **Bearer Token** nell'header HTTP:

```
Authorization: Bearer YOUR_TOKEN_HERE
```

### Esempio Header Completo

```http
POST /monitoring HTTP/1.1
Host: api.example.com
Content-Type: application/json
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
Content-Length: 1234
```

---

## 📦 Request Payload

### Struttura Completa

```json
{
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
        "interface": "eth0",
        "connected": true,
        "ip_address": "192.168.1.100"
    },
    "wifi": {
        "interface": "wlan0",
        "connected": true,
        "ip_address": "192.168.1.101",
        "signal_strength_dbm": -45
    },
    "cpu": {
        "max_percent": 45.2,
        "avg_percent": 23.5,
        "samples": 12
    },
    "memory": {
        "max_percent": 62.3,
        "avg_percent": 58.7,
        "current": {
            "total_mb": 3892.45,
            "used_mb": 2245.32,
            "available_mb": 1647.13,
            "percent": 57.7
        },
        "samples": 12
    }
}
```

---

## 📋 Descrizione Campi

### Livello Root

| Campo | Tipo | Descrizione |
|-------|------|-------------|
| `timestamp` | string (ISO 8601) | Data e ora dell'invio dei dati aggregati |
| `period_seconds` | integer | Durata del periodo di controllo in secondi |
| `samples_count` | integer | Numero totale di campioni raccolti nel periodo |

### Oggetto `disk`

Informazioni sullo spazio disco (istantanee al momento dell'invio).

| Campo | Tipo | Unità | Descrizione |
|-------|------|-------|-------------|
| `total_gb` | float | GB | Capacità totale del disco |
| `used_gb` | float | GB | Spazio utilizzato |
| `free_gb` | float | GB | Spazio libero disponibile |
| `percent` | float | % | Percentuale di utilizzo |

**Esempio:**
```json
{
    "total_gb": 29.72,
    "used_gb": 5.43,
    "free_gb": 22.79,
    "percent": 19.2
}
```

### Oggetto `ethernet`

Stato della connessione Ethernet.

| Campo | Tipo | Descrizione |
|-------|------|-------------|
| `interface` | string \| null | Nome dell'interfaccia (es: "eth0", "enp0s3") |
| `connected` | boolean | `true` se l'interfaccia è attiva e ha un IP |
| `ip_address` | string \| null | Indirizzo IP assegnato (IPv4) |

**Possibili Valori:**

```json
// Connesso
{
    "interface": "eth0",
    "connected": true,
    "ip_address": "192.168.1.100"
}

// Non connesso
{
    "interface": "eth0",
    "connected": false,
    "ip_address": null
}

// Interfaccia non trovata
{
    "interface": null,
    "connected": false,
    "ip_address": null
}

// Errore (campo opzionale)
{
    "interface": null,
    "connected": false,
    "ip_address": null,
    "error": "Permission denied"
}
```

### Oggetto `wifi`

Stato della connessione WiFi con intensità del segnale.

| Campo | Tipo | Descrizione |
|-------|------|-------------|
| `interface` | string \| null | Nome dell'interfaccia WiFi (es: "wlan0", "wlp3s0") |
| `connected` | boolean | `true` se connesso e ha un IP |
| `ip_address` | string \| null | Indirizzo IP assegnato (IPv4) |
| `signal_strength_dbm` | integer \| null | Intensità del segnale in dBm |

**Note sul Segnale WiFi:**
- **Valori tipici**: da -30 dBm (eccellente) a -90 dBm (pessimo)
- **-30 a -50 dBm**: Segnale eccellente
- **-50 a -60 dBm**: Segnale buono
- **-60 a -70 dBm**: Segnale discreto
- **-70 a -80 dBm**: Segnale debole
- **-80 a -90 dBm**: Segnale molto debole
- **< -90 dBm**: Segnale insufficiente
- **`null`**: Segnale non disponibile (iwconfig non installato/non supportato)

**Possibili Valori:**

```json
// Connesso con segnale
{
    "interface": "wlan0",
    "connected": true,
    "ip_address": "192.168.1.101",
    "signal_strength_dbm": -45
}

// Connesso ma segnale non disponibile
{
    "interface": "wlan0",
    "connected": true,
    "ip_address": "192.168.1.101",
    "signal_strength_dbm": null
}

// Non connesso
{
    "interface": "wlan0",
    "connected": false,
    "ip_address": null,
    "signal_strength_dbm": null
}

// WiFi non disponibile
{
    "interface": null,
    "connected": false,
    "ip_address": null,
    "signal_strength_dbm": null
}
```

### Oggetto `cpu`

Statistiche di utilizzo CPU aggregate sul periodo di controllo.

| Campo | Tipo | Unità | Descrizione |
|-------|------|-------|-------------|
| `max_percent` | float | % | Massimo utilizzo CPU registrato nel periodo |
| `avg_percent` | float | % | Utilizzo medio CPU nel periodo |
| `samples` | integer | - | Numero di campioni usati per il calcolo |

**Esempio:**
```json
{
    "max_percent": 45.2,
    "avg_percent": 23.5,
    "samples": 12
}
```

**Note:**
- I valori sono percentuali tra 0.0 e 100.0
- Con CPU multi-core, il valore può superare 100% (es: 200% su dual-core)
- Il campionamento avviene ogni `sample_interval_seconds` (default: 5 secondi)

### Oggetto `memory`

Statistiche di utilizzo RAM aggregate sul periodo di controllo.

| Campo | Tipo | Descrizione |
|-------|------|-------------|
| `max_percent` | float | Massima percentuale di RAM usata nel periodo |
| `avg_percent` | float | Percentuale media di RAM usata nel periodo |
| `current` | object | Snapshot corrente della memoria |
| `samples` | integer | Numero di campioni usati per il calcolo |

**Sottooggetto `current`:**

| Campo | Tipo | Unità | Descrizione |
|-------|------|-------|-------------|
| `total_mb` | float | MB | RAM totale installata |
| `used_mb` | float | MB | RAM attualmente in uso |
| `available_mb` | float | MB | RAM disponibile per nuove applicazioni |
| `percent` | float | % | Percentuale di utilizzo attuale |

**Esempio:**
```json
{
    "max_percent": 62.3,
    "avg_percent": 58.7,
    "current": {
        "total_mb": 3892.45,
        "used_mb": 2245.32,
        "available_mb": 1647.13,
        "percent": 57.7
    },
    "samples": 12
}
```

**Note:**
- `available_mb` non è semplicemente `total_mb - used_mb`
- Include memoria che può essere liberata (cache, buffer)
- Su Linux, la cache è considerata "disponibile"

---

## 📊 Esempi Completi

### Esempio 1: Raspberry Pi Connesso via Ethernet

```json
{
    "timestamp": "2025-11-24T15:30:45.123456",
    "period_seconds": 60,
    "samples_count": 12,
    "disk": {
        "total_gb": 29.72,
        "used_gb": 5.43,
        "free_gb": 22.79,
        "percent": 19.2
    },
    "ethernet": {
        "interface": "eth0",
        "connected": true,
        "ip_address": "192.168.1.100"
    },
    "wifi": {
        "interface": null,
        "connected": false,
        "ip_address": null,
        "signal_strength_dbm": null
    },
    "cpu": {
        "max_percent": 25.8,
        "avg_percent": 12.3,
        "samples": 12
    },
    "memory": {
        "max_percent": 45.2,
        "avg_percent": 42.1,
        "current": {
            "total_mb": 3892.45,
            "used_mb": 1638.54,
            "available_mb": 2253.91,
            "percent": 42.1
        },
        "samples": 12
    }
}
```

### Esempio 2: Raspberry Pi Connesso via WiFi

```json
{
    "timestamp": "2025-11-24T15:35:45.654321",
    "period_seconds": 300,
    "samples_count": 60,
    "disk": {
        "total_gb": 14.86,
        "used_gb": 3.21,
        "free_gb": 10.92,
        "percent": 23.5
    },
    "ethernet": {
        "interface": null,
        "connected": false,
        "ip_address": null
    },
    "wifi": {
        "interface": "wlan0",
        "connected": true,
        "ip_address": "192.168.1.150",
        "signal_strength_dbm": -52
    },
    "cpu": {
        "max_percent": 78.5,
        "avg_percent": 34.2,
        "samples": 60
    },
    "memory": {
        "max_percent": 68.9,
        "avg_percent": 62.5,
        "current": {
            "total_mb": 925.67,
            "used_mb": 637.82,
            "available_mb": 287.85,
            "percent": 68.9
        },
        "samples": 60
    }
}
```

### Esempio 3: Raspberry Pi Zero (risorse limitate)

```json
{
    "timestamp": "2025-11-24T15:40:00.789012",
    "period_seconds": 60,
    "samples_count": 12,
    "disk": {
        "total_gb": 7.29,
        "used_gb": 2.15,
        "free_gb": 4.75,
        "percent": 31.2
    },
    "ethernet": {
        "interface": null,
        "connected": false,
        "ip_address": null
    },
    "wifi": {
        "interface": "wlan0",
        "connected": true,
        "ip_address": "192.168.1.200",
        "signal_strength_dbm": -67
    },
    "cpu": {
        "max_percent": 95.3,
        "avg_percent": 67.8,
        "samples": 12
    },
    "memory": {
        "max_percent": 89.2,
        "avg_percent": 85.4,
        "current": {
            "total_mb": 432.18,
            "used_mb": 385.67,
            "available_mb": 46.51,
            "percent": 89.2
        },
        "samples": 12
    }
}
```

---

## ✅ Response Attesa

### Success Response (200 OK)

Il server dovrebbe rispondere con un successo quando i dati sono ricevuti correttamente.

**Formato suggerito:**
```json
{
    "status": "success",
    "message": "Data received successfully",
    "timestamp": "2025-11-24T15:30:45.123456"
}
```

### Error Responses

#### 401 Unauthorized
Token Bearer mancante o non valido.

```json
{
    "error": "Unauthorized",
    "message": "Invalid or missing Bearer token"
}
```

#### 400 Bad Request
Payload JSON malformato.

```json
{
    "error": "Bad Request",
    "message": "Invalid JSON payload"
}
```

#### 500 Internal Server Error
Errore del server.

```json
{
    "error": "Internal Server Error",
    "message": "Failed to process monitoring data"
}
```

---

## 🔍 Validazione del Payload

### Schema JSON (Draft 7)

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "Raspberry Pi Monitoring Data",
  "type": "object",
  "required": ["timestamp", "period_seconds", "samples_count", "disk", "ethernet", "wifi", "cpu", "memory"],
  "properties": {
    "timestamp": {
      "type": "string",
      "format": "date-time",
      "description": "ISO 8601 timestamp"
    },
    "period_seconds": {
      "type": "integer",
      "minimum": 1
    },
    "samples_count": {
      "type": "integer",
      "minimum": 1
    },
    "disk": {
      "type": "object",
      "required": ["total_gb", "used_gb", "free_gb", "percent"],
      "properties": {
        "total_gb": {"type": "number", "minimum": 0},
        "used_gb": {"type": "number", "minimum": 0},
        "free_gb": {"type": "number", "minimum": 0},
        "percent": {"type": "number", "minimum": 0, "maximum": 100}
      }
    },
    "ethernet": {
      "type": "object",
      "required": ["interface", "connected", "ip_address"],
      "properties": {
        "interface": {"type": ["string", "null"]},
        "connected": {"type": "boolean"},
        "ip_address": {"type": ["string", "null"], "format": "ipv4"}
      }
    },
    "wifi": {
      "type": "object",
      "required": ["interface", "connected", "ip_address", "signal_strength_dbm"],
      "properties": {
        "interface": {"type": ["string", "null"]},
        "connected": {"type": "boolean"},
        "ip_address": {"type": ["string", "null"], "format": "ipv4"},
        "signal_strength_dbm": {"type": ["integer", "null"]}
      }
    },
    "cpu": {
      "type": "object",
      "required": ["max_percent", "avg_percent", "samples"],
      "properties": {
        "max_percent": {"type": "number", "minimum": 0},
        "avg_percent": {"type": "number", "minimum": 0},
        "samples": {"type": "integer", "minimum": 1}
      }
    },
    "memory": {
      "type": "object",
      "required": ["max_percent", "avg_percent", "current", "samples"],
      "properties": {
        "max_percent": {"type": "number", "minimum": 0, "maximum": 100},
        "avg_percent": {"type": "number", "minimum": 0, "maximum": 100},
        "samples": {"type": "integer", "minimum": 1},
        "current": {
          "type": "object",
          "required": ["total_mb", "used_mb", "available_mb", "percent"],
          "properties": {
            "total_mb": {"type": "number", "minimum": 0},
            "used_mb": {"type": "number", "minimum": 0},
            "available_mb": {"type": "number", "minimum": 0},
            "percent": {"type": "number", "minimum": 0, "maximum": 100}
          }
        }
      }
    }
  }
}
```

---

## 💾 Esempi di Implementazione Server

### Python (Flask)

```python
from flask import Flask, request, jsonify
from datetime import datetime

app = Flask(__name__)
VALID_TOKEN = "your-bearer-token-here"

@app.route('/monitoring', methods=['POST'])
def receive_monitoring():
    # Verifica autenticazione
    auth = request.headers.get('Authorization', '')
    if not auth.startswith('Bearer ') or auth.replace('Bearer ', '') != VALID_TOKEN:
        return jsonify({'error': 'Unauthorized'}), 401
    
    # Ottieni dati
    data = request.get_json()
    
    # Salva nel database o processa
    print(f"Ricevuti dati da Raspberry Pi: {data['timestamp']}")
    
    # Risposta
    return jsonify({
        'status': 'success',
        'timestamp': datetime.now().isoformat()
    }), 200
```

### Node.js (Express)

```javascript
const express = require('express');
const app = express();

const VALID_TOKEN = 'your-bearer-token-here';

app.use(express.json());

app.post('/monitoring', (req, res) => {
    // Verifica autenticazione
    const auth = req.headers.authorization || '';
    const token = auth.replace('Bearer ', '');
    
    if (!auth.startsWith('Bearer ') || token !== VALID_TOKEN) {
        return res.status(401).json({ error: 'Unauthorized' });
    }
    
    // Ottieni dati
    const data = req.body;
    
    // Salva nel database o processa
    console.log(`Ricevuti dati da Raspberry Pi: ${data.timestamp}`);
    
    // Risposta
    res.json({
        status: 'success',
        timestamp: new Date().toISOString()
    });
});

app.listen(3000);
```

### PHP

```php
<?php
header('Content-Type: application/json');

$VALID_TOKEN = 'your-bearer-token-here';

// Verifica metodo
if ($_SERVER['REQUEST_METHOD'] !== 'POST') {
    http_response_code(405);
    echo json_encode(['error' => 'Method not allowed']);
    exit;
}

// Verifica autenticazione
$headers = getallheaders();
$auth = $headers['Authorization'] ?? '';
$token = str_replace('Bearer ', '', $auth);

if (!str_starts_with($auth, 'Bearer ') || $token !== $VALID_TOKEN) {
    http_response_code(401);
    echo json_encode(['error' => 'Unauthorized']);
    exit;
}

// Ottieni dati JSON
$data = json_decode(file_get_contents('php://input'), true);

if (!$data) {
    http_response_code(400);
    echo json_encode(['error' => 'Invalid JSON']);
    exit;
}

// Salva nel database o processa
error_log("Ricevuti dati da Raspberry Pi: " . $data['timestamp']);

// Risposta
http_response_code(200);
echo json_encode([
    'status' => 'success',
    'timestamp' => date('c')
]);
?>
```

---

## 🧪 Test con cURL

```bash
curl -X POST https://api.example.com/monitoring \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -d '{
    "timestamp": "2025-11-24T15:30:45.123456",
    "period_seconds": 60,
    "samples_count": 12,
    "disk": {
        "total_gb": 29.72,
        "used_gb": 5.43,
        "free_gb": 22.79,
        "percent": 19.2
    },
    "ethernet": {
        "interface": "eth0",
        "connected": true,
        "ip_address": "192.168.1.100"
    },
    "wifi": {
        "interface": null,
        "connected": false,
        "ip_address": null,
        "signal_strength_dbm": null
    },
    "cpu": {
        "max_percent": 45.2,
        "avg_percent": 23.5,
        "samples": 12
    },
    "memory": {
        "max_percent": 62.3,
        "avg_percent": 58.7,
        "current": {
            "total_mb": 3892.45,
            "used_mb": 2245.32,
            "available_mb": 1647.13,
            "percent": 57.7
        },
        "samples": 12
    }
}'
```

---

## 📌 Note Importanti

1. **Timestamp**: Sempre in formato ISO 8601 con timezone
2. **Campi Null**: Alcuni campi possono essere `null` se non disponibili
3. **Unità di Misura**: 
   - Disco: GB (Gigabyte)
   - RAM: MB (Megabyte)
   - Tempo: secondi
   - Segnale WiFi: dBm
4. **Frequenza**: Dipende dalla configurazione (`check_period_minutes`)
5. **Dimensione Payload**: Circa 500-800 bytes per richiesta

---

## 🔄 Versionamento

**Versione API**: 1.0
**Data**: 24 novembre 2025

Se in futuro il formato cambia, verrà aggiunto un campo `api_version` nel payload.
