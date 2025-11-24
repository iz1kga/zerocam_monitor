#!/bin/bash
# Script per eseguire il test in modalità sviluppo (con virtualenv locale)

echo "=========================================="
echo "Test in modalità sviluppo"
echo "=========================================="
echo

# Directory corrente
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Verifica se esiste un virtualenv locale
if [ ! -d "$SCRIPT_DIR/venv" ]; then
    echo "Virtual environment non trovato. Creo venv locale per sviluppo..."
    python3 -m venv "$SCRIPT_DIR/venv"
    
    echo "Installazione dipendenze..."
    source "$SCRIPT_DIR/venv/bin/activate"
    pip install --upgrade pip
    pip install -r "$SCRIPT_DIR/requirements.txt"
    deactivate
fi

echo "Attivazione virtualenv e esecuzione test..."
source "$SCRIPT_DIR/venv/bin/activate"

# Esegui il test
python "$SCRIPT_DIR/test.py"

deactivate

echo ""
echo "Test completato!"
