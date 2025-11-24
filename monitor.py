#!/usr/bin/env python3
"""
Sistema di monitoraggio per Raspberry Pi
Raccoglie dati di sistema e li invia a un'API REST con autenticazione Bearer
"""

import time
import json
import logging
import psutil
import requests
import subprocess
from datetime import datetime
from pathlib import Path
from logging.handlers import RotatingFileHandler
from typing import Dict, List, Optional
from config import Config


class SystemMonitor:
    """Monitora i parametri di sistema del Raspberry Pi"""
    
    def __init__(self, config: Config):
        self.config = config
        self.setup_logging()
        self.samples: List[Dict] = []
        self.last_internet_check = datetime.now()
        self.internet_down_since: Optional[datetime] = None
        
    def setup_logging(self):
        """Configura il logging con rotazione automatica"""
        log_dir = Path(self.config.log_dir)
        log_dir.mkdir(parents=True, exist_ok=True)
        
        # Configura il logger principale
        self.logger = logging.getLogger('RaspberryMonitor')
        self.logger.setLevel(logging.INFO)
        
        # Handler con rotazione (max 10MB per file, mantieni 5 file)
        handler = RotatingFileHandler(
            log_dir / 'monitor.log',
            maxBytes=10*1024*1024,  # 10MB
            backupCount=5
        )
        
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
        
        # Aggiungi anche output su console
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)
        
    def get_disk_usage(self) -> Dict:
        """Ottiene lo spazio su disco"""
        disk = psutil.disk_usage('/')
        return {
            'total_gb': round(disk.total / (1024**3), 2),
            'used_gb': round(disk.used / (1024**3), 2),
            'free_gb': round(disk.free / (1024**3), 2),
            'percent': disk.percent
        }
    
    def get_ethernet_status(self) -> Dict:
        """Verifica lo stato della connettività ethernet"""
        try:
            # Cerca interfacce ethernet (eth0, enp, etc.)
            stats = psutil.net_if_stats()
            addrs = psutil.net_if_addrs()
            
            # Trova interfaccia ethernet
            eth_interface = None
            for iface in stats.keys():
                if iface.startswith('eth') or iface.startswith('enp'):
                    eth_interface = iface
                    break
            
            if eth_interface and eth_interface in stats:
                is_up = stats[eth_interface].isup
                # Ottieni IP se disponibile
                ip_address = None
                if eth_interface in addrs:
                    for addr in addrs[eth_interface]:
                        if addr.family == 2:  # AF_INET
                            ip_address = addr.address
                            break
                
                return {
                    'interface': eth_interface,
                    'connected': is_up,
                    'ip_address': ip_address
                }
            else:
                return {
                    'interface': None,
                    'connected': False,
                    'ip_address': None
                }
        except Exception as e:
            self.logger.error(f"Errore nel controllo ethernet: {e}")
            return {
                'interface': None,
                'connected': False,
                'ip_address': None,
                'error': str(e)
            }
    
    def get_wifi_status(self) -> Dict:
        """Verifica lo stato della connettività WiFi e il segnale"""
        try:
            # Cerca interfacce wifi (wlan0, wlp, etc.)
            stats = psutil.net_if_stats()
            addrs = psutil.net_if_addrs()
            
            # Trova interfaccia wifi
            wifi_interface = None
            for iface in stats.keys():
                if iface.startswith('wlan') or iface.startswith('wlp'):
                    wifi_interface = iface
                    break
            
            if not wifi_interface:
                return {
                    'interface': None,
                    'connected': False,
                    'ip_address': None,
                    'signal_strength': None
                }
            
            is_up = stats[wifi_interface].isup
            
            # Ottieni IP
            ip_address = None
            if wifi_interface in addrs:
                for addr in addrs[wifi_interface]:
                    if addr.family == 2:  # AF_INET
                        ip_address = addr.address
                        break
            
            # Ottieni intensità del segnale WiFi usando iwconfig
            signal_strength = None
            try:
                result = subprocess.run(
                    ['iwconfig', wifi_interface],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                
                # Parsing dell'output di iwconfig
                for line in result.stdout.split('\n'):
                    if 'Signal level' in line:
                        # Estrae il valore del segnale (es: "Signal level=-45 dBm")
                        parts = line.split('Signal level=')
                        if len(parts) > 1:
                            signal = parts[1].split()[0]
                            signal_strength = int(signal)
                        break
            except Exception as e:
                self.logger.debug(f"Non è stato possibile ottenere il segnale WiFi: {e}")
            
            return {
                'interface': wifi_interface,
                'connected': is_up and ip_address is not None,
                'ip_address': ip_address,
                'signal_strength_dbm': signal_strength
            }
            
        except Exception as e:
            self.logger.error(f"Errore nel controllo WiFi: {e}")
            return {
                'interface': None,
                'connected': False,
                'ip_address': None,
                'signal_strength_dbm': None,
                'error': str(e)
            }
    
    def get_memory_usage(self) -> Dict:
        """Ottiene l'utilizzo della RAM"""
        mem = psutil.virtual_memory()
        return {
            'total_mb': round(mem.total / (1024**2), 2),
            'used_mb': round(mem.used / (1024**2), 2),
            'available_mb': round(mem.available / (1024**2), 2),
            'percent': mem.percent
        }
    
    def get_cpu_usage(self) -> float:
        """Ottiene la percentuale di utilizzo della CPU"""
        return psutil.cpu_percent(interval=0.1)
    
    def check_internet_connectivity(self) -> bool:
        """Verifica la connettività a Internet"""
        try:
            # Prova a connettersi a servizi affidabili
            for host in ['8.8.8.8', '1.1.1.1']:
                try:
                    response = requests.get(
                        f'http://{host}',
                        timeout=5
                    )
                    return True
                except:
                    continue
            
            # Prova anche con DNS
            try:
                response = requests.get(
                    'http://www.google.com',
                    timeout=5
                )
                return True
            except:
                pass
            
            return False
        except Exception as e:
            self.logger.error(f"Errore nel controllo connettività: {e}")
            return False
    
    def collect_sample(self):
        """Raccoglie un campione di dati"""
        sample = {
            'timestamp': datetime.now().isoformat(),
            'cpu_percent': self.get_cpu_usage(),
            'memory': self.get_memory_usage()
        }
        self.samples.append(sample)
    
    def aggregate_samples(self) -> Dict:
        """Aggrega i campioni raccolti nel periodo di controllo"""
        if not self.samples:
            return {}
        
        cpu_values = [s['cpu_percent'] for s in self.samples]
        mem_values = [s['memory']['percent'] for s in self.samples]
        
        aggregated = {
            'device_id': self.config.device_id,
            'timestamp': datetime.now().isoformat(),
            'period_seconds': self.config.check_period_minutes * 60,
            'samples_count': len(self.samples),
            
            # Dati disco (istantanei)
            'disk': self.get_disk_usage(),
            
            # Connettività
            'ethernet': self.get_ethernet_status(),
            'wifi': self.get_wifi_status(),
            
            # CPU (max e average)
            'cpu': {
                'max_percent': round(max(cpu_values), 2),
                'avg_percent': round(sum(cpu_values) / len(cpu_values), 2),
                'samples': len(cpu_values)
            },
            
            # RAM (max e average)
            'memory': {
                'max_percent': round(max(mem_values), 2),
                'avg_percent': round(sum(mem_values) / len(mem_values), 2),
                'current': self.get_memory_usage(),
                'samples': len(mem_values)
            }
        }
        
        return aggregated
    
    def send_to_api(self, data: Dict) -> bool:
        """Invia i dati all'API REST con autenticazione Bearer"""
        try:
            headers = {
                'Authorization': f'Bearer {self.config.api_bearer_token}',
                'Content-Type': 'application/json'
            }
            
            response = requests.post(
                self.config.api_url,
                json=data,
                headers=headers,
                timeout=30
            )
            
            response.raise_for_status()
            self.logger.info(f"Dati inviati con successo all'API (Status: {response.status_code})")
            return True
            
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Errore nell'invio dei dati all'API: {e}")
            return False
    
    def save_to_log(self, data: Dict):
        """Salva i dati aggregati nel log locale"""
        log_line = json.dumps(data, ensure_ascii=False)
        self.logger.info(f"DATA: {log_line}")
    
    def handle_internet_outage(self):
        """Gestisce la mancanza di connessione Internet"""
        has_internet = self.check_internet_connectivity()
        
        if has_internet:
            # Connessione ripristinata
            if self.internet_down_since:
                self.logger.info("Connessione Internet ripristinata")
                self.internet_down_since = None
        else:
            # Nessuna connessione
            if self.internet_down_since is None:
                # Prima volta che rileva la mancanza di connessione
                self.internet_down_since = datetime.now()
                self.logger.warning("Connessione Internet non disponibile")
            else:
                # Calcola per quanto tempo è mancata la connessione
                outage_duration = (datetime.now() - self.internet_down_since).total_seconds()
                outage_minutes = outage_duration / 60
                
                self.logger.warning(
                    f"Internet non disponibile da {outage_minutes:.1f} minuti "
                    f"(limite: {self.config.reboot_timeout_minutes} minuti)"
                )
                
                if outage_minutes >= self.config.reboot_timeout_minutes:
                    self.logger.critical(
                        f"Connessione Internet assente per {outage_minutes:.1f} minuti. "
                        f"RIAVVIO DEL SISTEMA!"
                    )
                    self.reboot_system()
    
    def reboot_system(self):
        """Riavvia il sistema"""
        try:
            subprocess.run(['sudo', 'reboot'], check=True)
        except Exception as e:
            self.logger.error(f"Errore nel riavvio del sistema: {e}")
    
    def run(self):
        """Loop principale del monitoraggio"""
        self.logger.info("Sistema di monitoraggio avviato")
        self.logger.info(f"Periodo di controllo: {self.config.check_period_minutes} minuti")
        self.logger.info(f"Intervallo campionamento: {self.config.sample_interval_seconds} secondi")
        self.logger.info(f"Timeout riavvio: {self.config.reboot_timeout_minutes} minuti")
        
        sample_interval = self.config.sample_interval_seconds
        check_period = self.config.check_period_minutes * 60
        
        last_check_time = time.time()
        last_internet_check_time = time.time()
        
        try:
            while True:
                current_time = time.time()
                
                # Raccogli campione
                self.collect_sample()
                
                # Controlla connessione Internet ogni minuto
                if current_time - last_internet_check_time >= 60:
                    self.handle_internet_outage()
                    last_internet_check_time = current_time
                
                # Verifica se è il momento di inviare i dati
                if current_time - last_check_time >= check_period:
                    # Aggrega i dati raccolti
                    aggregated_data = self.aggregate_samples()
                    
                    # Salva nel log locale
                    self.save_to_log(aggregated_data)
                    
                    # Invia all'API
                    self.send_to_api(aggregated_data)
                    
                    # Reset dei campioni e del timer
                    self.samples = []
                    last_check_time = current_time
                
                # Attendi prima del prossimo campione
                time.sleep(sample_interval)
                
        except KeyboardInterrupt:
            self.logger.info("Monitoraggio interrotto dall'utente")
        except Exception as e:
            self.logger.critical(f"Errore critico nel loop principale: {e}", exc_info=True)
            raise


def main():
    """Entry point principale"""
    config = Config()
    monitor = SystemMonitor(config)
    monitor.run()


if __name__ == '__main__':
    main()
