#!/bin/bash
# Script di installazione per il servizio di monitoraggio Raspberry Pi

set -e

echo "=========================================="
echo "Installazione Raspberry Pi Monitor"
echo "=========================================="
echo

# Verifica se lo script viene eseguito come root
if [ "$EUID" -ne 0 ]; then 
    echo "ERRORE: Questo script deve essere eseguito come root (usa sudo)"
    exit 1
fi

# Directory di installazione
INSTALL_DIR="/opt/raspberry-monitor"
CONFIG_DIR="/etc/raspberry-monitor"
LOG_DIR="/var/log/raspberry-monitor"

echo "1. Creazione delle directory..."
mkdir -p "$INSTALL_DIR"
mkdir -p "$CONFIG_DIR"
mkdir -p "$LOG_DIR"

echo "2. Installazione dipendenze di sistema..."
apt-get update
apt-get install -y python3 python3-pip python3-venv wireless-tools

echo "3. Copia dei file del programma..."
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cp "$SCRIPT_DIR/monitor.py" "$INSTALL_DIR/"
cp "$SCRIPT_DIR/config.py" "$INSTALL_DIR/"
cp "$SCRIPT_DIR/requirements.txt" "$INSTALL_DIR/"

# Copia il file di configurazione se non esiste già
if [ ! -f "$CONFIG_DIR/config.json" ]; then
    echo "4. Creazione file di configurazione..."
    cp "$SCRIPT_DIR/config.json" "$CONFIG_DIR/config.json"
    echo "   IMPORTANTE: Modifica $CONFIG_DIR/config.json con le tue impostazioni!"
else
    echo "4. File di configurazione esistente mantenuto"
fi

# Crea un symlink alla configurazione nella directory di installazione
ln -sf "$CONFIG_DIR/config.json" "$INSTALL_DIR/config.json"

echo "5. Creazione del virtual environment..."
cd "$INSTALL_DIR"
python3 -m venv venv

echo "6. Attivazione virtualenv e installazione dipendenze Python..."
source "$INSTALL_DIR/venv/bin/activate"
pip install --upgrade pip
pip install -r requirements.txt
deactivate

echo "7. Installazione del servizio systemd..."
cp "$SCRIPT_DIR/raspberry-monitor.service" /etc/systemd/system/

echo "8. Ricaricamento della configurazione systemd..."
systemctl daemon-reload

echo "9. Abilitazione del servizio all'avvio..."
systemctl enable raspberry-monitor.service

echo
echo "=========================================="
echo "Installazione completata!"
echo "=========================================="
echo
echo "PROSSIMI PASSI:"
echo
echo "1. Modifica la configurazione:"
echo "   sudo nano $CONFIG_DIR/config.json"
echo
echo "2. Inserisci:"
echo "   - URL dell'API REST"
echo "   - Bearer Token per l'autenticazione"
echo "   - Altri parametri secondo le tue esigenze"
echo
echo "3. Avvia il servizio:"
echo "   sudo systemctl start raspberry-monitor"
echo
echo "4. Verifica lo stato:"
echo "   sudo systemctl status raspberry-monitor"
echo
echo "5. Visualizza i log:"
echo "   sudo journalctl -u raspberry-monitor -f"
echo "   oppure"
echo "   sudo tail -f $LOG_DIR/monitor.log"
echo
echo "Per fermare il servizio:"
echo "   sudo systemctl stop raspberry-monitor"
echo
echo "Per disabilitare l'avvio automatico:"
echo "   sudo systemctl disable raspberry-monitor"
echo
