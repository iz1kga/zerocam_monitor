#!/usr/bin/env python3
"""
Script di test per verificare che il sistema di monitoraggio funzioni correttamente
Esegui questo script prima di installare il servizio
"""

import sys
import json
from pathlib import Path

# Aggiungi la directory corrente al path
sys.path.insert(0, str(Path(__file__).parent))

from config import Config
from monitor import SystemMonitor


def test_config():
    """Test della configurazione"""
    print("=" * 60)
    print("TEST CONFIGURAZIONE")
    print("=" * 60)
    
    try:
        config = Config()
        print("✓ Configurazione caricata con successo")
        print(f"  - Periodo di controllo: {config.check_period_minutes} minuti")
        print(f"  - Intervallo campionamento: {config.sample_interval_seconds} secondi")
        print(f"  - Timeout riavvio: {config.reboot_timeout_minutes} minuti")
        print(f"  - API URL: {config.api_url}")
        print(f"  - Bearer Token: {'***' + config.api_bearer_token[-10:] if len(config.api_bearer_token) > 10 else '[NON CONFIGURATO]'}")
        print(f"  - Directory log: {config.log_dir}")
        
        if not config.api_bearer_token or config.api_bearer_token == "YOUR_BEARER_TOKEN_HERE":
            print("\n⚠️  ATTENZIONE: Bearer Token non configurato!")
            
        return True
    except Exception as e:
        print(f"✗ Errore nel caricamento della configurazione: {e}")
        return False


def test_system_info():
    """Test della raccolta informazioni di sistema"""
    print("\n" + "=" * 60)
    print("TEST RACCOLTA DATI DI SISTEMA")
    print("=" * 60)
    
    try:
        config = Config()
        monitor = SystemMonitor(config)
        
        # Test disco
        print("\n1. SPAZIO DISCO:")
        disk = monitor.get_disk_usage()
        print(f"   ✓ Totale: {disk['total_gb']} GB")
        print(f"   ✓ Usato: {disk['used_gb']} GB ({disk['percent']}%)")
        print(f"   ✓ Libero: {disk['free_gb']} GB")
        
        # Test ethernet
        print("\n2. ETHERNET:")
        eth = monitor.get_ethernet_status()
        if eth['connected']:
            print(f"   ✓ Connesso ({eth['interface']})")
            print(f"   ✓ IP: {eth['ip_address']}")
        else:
            print(f"   ⚠  Non connesso o non disponibile")
        
        # Test WiFi
        print("\n3. WIFI:")
        wifi = monitor.get_wifi_status()
        if wifi['connected']:
            print(f"   ✓ Connesso ({wifi['interface']})")
            print(f"   ✓ IP: {wifi['ip_address']}")
            if wifi['signal_strength_dbm']:
                print(f"   ✓ Segnale: {wifi['signal_strength_dbm']} dBm")
            else:
                print(f"   ⚠  Segnale non disponibile (iwconfig non disponibile?)")
        else:
            print(f"   ⚠  Non connesso o non disponibile")
        
        # Test RAM
        print("\n4. MEMORIA RAM:")
        mem = monitor.get_memory_usage()
        print(f"   ✓ Totale: {mem['total_mb']} MB")
        print(f"   ✓ Usata: {mem['used_mb']} MB ({mem['percent']}%)")
        print(f"   ✓ Disponibile: {mem['available_mb']} MB")
        
        # Test CPU
        print("\n5. CPU:")
        cpu = monitor.get_cpu_usage()
        print(f"   ✓ Utilizzo: {cpu}%")
        
        return True
        
    except Exception as e:
        print(f"✗ Errore nella raccolta dati: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_internet():
    """Test della connettività Internet"""
    print("\n" + "=" * 60)
    print("TEST CONNETTIVITÀ INTERNET")
    print("=" * 60)
    
    try:
        config = Config()
        monitor = SystemMonitor(config)
        
        print("Verifica connessione Internet...")
        has_internet = monitor.check_internet_connectivity()
        
        if has_internet:
            print("✓ Connessione Internet disponibile")
        else:
            print("✗ Connessione Internet NON disponibile")
            print("  Verifica la tua connessione di rete")
        
        return has_internet
        
    except Exception as e:
        print(f"✗ Errore nel test di connettività: {e}")
        return False


def test_aggregation():
    """Test dell'aggregazione dati"""
    print("\n" + "=" * 60)
    print("TEST AGGREGAZIONE DATI")
    print("=" * 60)
    
    try:
        config = Config()
        monitor = SystemMonitor(config)
        
        # Raccogli alcuni campioni
        print("Raccolta di 3 campioni di test...")
        for i in range(3):
            monitor.collect_sample()
            print(f"  Campione {i+1} raccolto")
        
        # Aggrega
        print("\nAggregazione dati...")
        data = monitor.aggregate_samples()
        
        print(f"✓ Dati aggregati correttamente")
        print(f"  - Campioni raccolti: {data['samples_count']}")
        print(f"  - CPU max: {data['cpu']['max_percent']}%")
        print(f"  - CPU media: {data['cpu']['avg_percent']}%")
        print(f"  - RAM max: {data['memory']['max_percent']}%")
        print(f"  - RAM media: {data['memory']['avg_percent']}%")
        
        print("\n📋 ESEMPIO DATI JSON DA INVIARE:")
        print("-" * 60)
        print(json.dumps(data, indent=2, ensure_ascii=False))
        print("-" * 60)
        
        return True
        
    except Exception as e:
        print(f"✗ Errore nell'aggregazione: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_api():
    """Test dell'invio all'API"""
    print("\n" + "=" * 60)
    print("TEST INVIO API")
    print("=" * 60)
    
    try:
        config = Config()
        
        if not config.api_bearer_token or config.api_bearer_token == "YOUR_BEARER_TOKEN_HERE":
            print("⚠️  SALTATO: Bearer Token non configurato")
            print("   Configura il token in config.json per testare l'API")
            return None
        
        monitor = SystemMonitor(config)
        
        # Raccogli e aggrega dati
        monitor.collect_sample()
        data = monitor.aggregate_samples()
        
        print(f"Invio dati a: {config.api_url}")
        success = monitor.send_to_api(data)
        
        if success:
            print("✓ Dati inviati con successo all'API")
            return True
        else:
            print("✗ Errore nell'invio all'API")
            print("  Verifica:")
            print("  - URL dell'API corretto")
            print("  - Bearer Token valido")
            print("  - API raggiungibile e funzionante")
            return False
            
    except Exception as e:
        print(f"✗ Errore nel test API: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Esegue tutti i test"""
    print("\n")
    print("╔" + "=" * 58 + "╗")
    print("║" + " " * 10 + "RASPBERRY PI MONITOR - TEST SUITE" + " " * 13 + "║")
    print("╚" + "=" * 58 + "╝")
    print()
    
    results = {
        'config': test_config(),
        'system_info': test_system_info(),
        'internet': test_internet(),
        'aggregation': test_aggregation(),
        'api': test_api()
    }
    
    # Riepilogo
    print("\n" + "=" * 60)
    print("RIEPILOGO TEST")
    print("=" * 60)
    
    for test_name, result in results.items():
        if result is True:
            status = "✓ PASS"
        elif result is False:
            status = "✗ FAIL"
        else:
            status = "⊘ SKIP"
        
        print(f"{test_name.upper():20} {status}")
    
    # Conclusione
    print("\n" + "=" * 60)
    
    failed = sum(1 for r in results.values() if r is False)
    passed = sum(1 for r in results.values() if r is True)
    skipped = sum(1 for r in results.values() if r is None)
    
    if failed == 0:
        print("✓ TUTTI I TEST COMPLETATI CON SUCCESSO")
        if skipped > 0:
            print(f"  ({skipped} test saltati)")
        print("\nPuoi procedere con l'installazione del servizio:")
        print("  sudo ./install.sh")
    else:
        print(f"✗ {failed} TEST FALLITI")
        print("\nCorreggi gli errori prima di procedere con l'installazione")
    
    print("=" * 60)
    print()
    
    return 0 if failed == 0 else 1


if __name__ == '__main__':
    sys.exit(main())
