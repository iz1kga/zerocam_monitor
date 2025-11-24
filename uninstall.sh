#!/bin/bash
# Script di disinstallazione per il servizio di monitoraggio Raspberry Pi

set -e

echo "=========================================="
echo "Disinstallazione Raspberry Pi Monitor"
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

echo "1. Fermando il servizio..."
systemctl stop raspberry-monitor || true

echo "2. Disabilitazione del servizio..."
systemctl disable raspberry-monitor || true

echo "3. Rimozione del file del servizio..."
rm -f /etc/systemd/system/raspberry-monitor.service

echo "4. Ricaricamento systemd..."
systemctl daemon-reload

echo "5. Rimozione dei file del programma..."
rm -rf "$INSTALL_DIR"

echo
read -p "Vuoi rimuovere anche i file di configurazione? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "6. Rimozione della configurazione..."
    rm -rf "$CONFIG_DIR"
else
    echo "6. Configurazione mantenuta in $CONFIG_DIR"
fi

echo
read -p "Vuoi rimuovere anche i file di log? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "7. Rimozione dei log..."
    rm -rf "$LOG_DIR"
else
    echo "7. Log mantenuti in $LOG_DIR"
fi

echo
echo "=========================================="
echo "Disinstallazione completata!"
echo "=========================================="
echo
