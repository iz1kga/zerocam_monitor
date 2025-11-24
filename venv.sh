#!/bin/bash
# Script helper per gestire il virtual environment

INSTALL_DIR="/opt/raspberry-monitor"
VENV_DIR="$INSTALL_DIR/venv"

# Colori per output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

function print_usage() {
    echo "Uso: $0 [comando]"
    echo ""
    echo "Comandi disponibili:"
    echo "  activate    - Mostra il comando per attivare il virtualenv"
    echo "  install     - Installa/aggiorna le dipendenze dal requirements.txt"
    echo "  list        - Lista i pacchetti installati nel virtualenv"
    echo "  pip         - Esegue pip nel virtualenv (es: ./venv.sh pip install requests)"
    echo "  python      - Esegue python nel virtualenv (es: ./venv.sh python script.py)"
    echo "  test        - Esegue lo script di test nel virtualenv"
    echo ""
}

function check_venv() {
    if [ ! -d "$VENV_DIR" ]; then
        echo -e "${RED}Errore: Virtual environment non trovato in $VENV_DIR${NC}"
        echo "Esegui prima l'installazione con: sudo ./install.sh"
        exit 1
    fi
}

case "$1" in
    activate)
        check_venv
        echo -e "${GREEN}Per attivare il virtual environment, esegui:${NC}"
        echo "source $VENV_DIR/bin/activate"
        echo ""
        echo -e "${YELLOW}Per disattivare:${NC}"
        echo "deactivate"
        ;;
    
    install)
        check_venv
        echo -e "${GREEN}Installazione/aggiornamento dipendenze...${NC}"
        "$VENV_DIR/bin/pip" install --upgrade pip
        "$VENV_DIR/bin/pip" install -r "$INSTALL_DIR/requirements.txt"
        echo -e "${GREEN}Fatto!${NC}"
        ;;
    
    list)
        check_venv
        echo -e "${GREEN}Pacchetti installati nel virtualenv:${NC}"
        "$VENV_DIR/bin/pip" list
        ;;
    
    pip)
        check_venv
        shift
        "$VENV_DIR/bin/pip" "$@"
        ;;
    
    python)
        check_venv
        shift
        "$VENV_DIR/bin/python" "$@"
        ;;
    
    test)
        check_venv
        echo -e "${GREEN}Esecuzione test nel virtualenv...${NC}"
        "$VENV_DIR/bin/python" "$INSTALL_DIR/../test.py"
        ;;
    
    *)
        print_usage
        exit 1
        ;;
esac
