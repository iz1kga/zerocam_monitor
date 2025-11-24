"""
Gestione della configurazione per il sistema di monitoraggio
"""

import json
import os
from pathlib import Path
from typing import Optional


class Config:
    """Gestisce la configurazione del sistema di monitoraggio"""
    
    DEFAULT_CONFIG = {
        'check_period_minutes': 1,  # Periodo di controllo in minuti
        'sample_interval_seconds': 5,  # Intervallo tra i campioni in secondi
        'reboot_timeout_minutes': 15,  # Minuti senza internet prima del riavvio
        'api_url': 'https://api.example.com/monitoring',  # URL dell'API REST
        'api_bearer_token': '',  # Token Bearer per l'autenticazione
        'log_dir': '/var/log/raspberry-monitor'  # Directory dei log
    }
    
    def __init__(self, config_file: Optional[str] = None):
        """
        Inizializza la configurazione
        
        Args:
            config_file: Path al file di configurazione JSON. 
                        Se None, cerca config.json nella directory corrente o in /etc
        """
        if config_file is None:
            # Cerca il file di configurazione in diverse posizioni
            possible_paths = [
                Path(__file__).parent / 'config.json',
                Path('/etc/raspberry-monitor/config.json'),
                Path.home() / '.raspberry-monitor' / 'config.json'
            ]
            
            for path in possible_paths:
                if path.exists():
                    config_file = str(path)
                    break
        
        self.config_file = config_file
        self.config = self.DEFAULT_CONFIG.copy()
        
        if config_file and Path(config_file).exists():
            self.load_config()
        else:
            # Se non esiste, crea un file di configurazione di esempio
            if config_file:
                self.save_config()
    
    def load_config(self):
        """Carica la configurazione dal file JSON"""
        try:
            with open(self.config_file, 'r') as f:
                user_config = json.load(f)
                self.config.update(user_config)
        except Exception as e:
            print(f"Errore nel caricamento della configurazione: {e}")
            print("Utilizzo della configurazione di default")
    
    def save_config(self):
        """Salva la configurazione corrente nel file JSON"""
        try:
            config_path = Path(self.config_file)
            config_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(self.config_file, 'w') as f:
                json.dump(self.config, f, indent=4)
            
            print(f"Configurazione salvata in: {self.config_file}")
        except Exception as e:
            print(f"Errore nel salvataggio della configurazione: {e}")
    
    @property
    def check_period_minutes(self) -> int:
        """Periodo di controllo in minuti"""
        return self.config['check_period_minutes']
    
    @property
    def sample_interval_seconds(self) -> int:
        """Intervallo tra i campioni in secondi"""
        return self.config['sample_interval_seconds']
    
    @property
    def reboot_timeout_minutes(self) -> int:
        """Minuti senza internet prima del riavvio"""
        return self.config['reboot_timeout_minutes']
    
    @property
    def api_url(self) -> str:
        """URL dell'API REST"""
        return self.config['api_url']
    
    @property
    def api_bearer_token(self) -> str:
        """Token Bearer per l'autenticazione"""
        return self.config['api_bearer_token']
    
    @property
    def log_dir(self) -> str:
        """Directory dei log"""
        return self.config['log_dir']
