# Image Descriptor Bot

Un bot Telegram che fornisce descrizioni dettagliate delle immagini in italiano utilizzando OpenAI Vision API.

## Features

- Risponde automaticamente quando viene postata un'immagine nel canale
- Fornisce descrizioni dettagliate delle immagini in italiano
- Cita il post originale con l'immagine
- Architettura modulare per sostituire facilmente il modello multimodale
- Deployabile su AWS Lambda con API Gateway
- Gestione sicura delle API key tramite AWS SSM Parameter Store

## Prerequisites

- Python 3.9+
- AWS CLI configurato
- Terraform
- Account Telegram Bot (ottenuto tramite @BotFather)
- API key OpenAI

## Funzionalità del Bot

Il bot risponde alle immagini con:

1. Una citazione del messaggio originale
1. La frase "Ecco la descrizione dell'immagine:"
1. **Riconoscimento eventi**: Se l'immagine contiene un annuncio di evento, estrae automaticamente:
   - Nome dell'evento
   - Descrizione breve
   - Date e orari
   - Luogo/venue
   - Organizzatore
   - Informazioni sui biglietti
   - Contatti
1. Una descrizione dettagliata in italiano dell'immagine

## Project Structure

```text
image-descriptor/
├── src/
│   ├── bot/
│   │   └── telegram_bot.py      # Bot Telegram principale
│   ├── services/
│   │   └── vision_service.py    # Servizio di visione (OpenAI)
│   ├── handlers/
│   │   └── lambda_handler.py    # Handler AWS Lambda
│   └── local.py                 # Script per test locali
├── terraform/
│   ├── main.tf                  # Infrastruttura AWS
│   └── variables.tf             # Variabili Terraform
├── requirements.txt             # Dipendenze Python
└── README.md
```

## Quick Start with Make

Per un workflow di sviluppo più veloce, usa i comandi Make inclusi:

```bash
# Vedi tutti i comandi disponibili
make help

# Installa le dipendenze
make install

# Esegui tutti i test
make test

# Avvia il bot localmente (richiede file .env)
make run

# Esegui il linting del codice
make lint

# Pulisci i file temporanei
make clean
```

## Setup Locale

1. Clona il repository:

```bash
git clone <your-repo-url>
cd image-descriptor
```

1. Crea un ambiente virtuale:

```bash
python -m venv venv
source venv/bin/activate  # Su Windows: venv\Scripts\activate
```

1. Installa le dipendenze:

```bash
pip install -r requirements.txt
```

1. Crea un file `.env` nella root del progetto:

```bash
TELEGRAM_TOKEN=your_telegram_bot_token_here
OPENAI_API_KEY=your_openai_api_key_here
```

1. Esegui il bot localmente:

```bash
PYTHONPATH=. python src/local.py
```

## Deploy su AWS

1. Configura le credenziali AWS
1. Aggiorna le variabili in `terraform/variables.tf`
1. Esegui Terraform:

```bash
cd terraform
terraform init
terraform plan
terraform apply
```

## Test

Il progetto include una suite completa di test che può essere eseguita localmente.

### Eseguire i test

#### Quick Start

```bash
make test          # Esegui tutti i test (raccomandato per sviluppo)
make test-unit     # Esegui solo test rapidi unitari
make test-e2e      # Esegui solo test di integrazione completi
```

#### Make Commands (Raccomandato)

```bash
# Tutti i test
make test              # Esegui tutti i test
make test-all          # Alias per make test

# Test specifici per tipologia
make test-unit         # Solo test unitari
make test-integration  # Solo test di integrazione/e2e
make test-e2e          # Alias per test-integration

# Test con strumenti specifici
make test-pytest       # Usa pytest (solo test sincroni)
make test-coverage     # Test con report di copertura
```

#### Test Runner Diretto

```bash
# Test runner personalizzato (supporta tutti i test async/sync)
python test_runner.py                    # Tutti i test
python test_runner.py --type unit        # Solo test unitari
python test_runner.py --type e2e         # Solo test e2e
python test_runner.py --type integration # Solo test integrazione

# Test runner avanzato con più opzioni
python run_tests.py                              # Tutti i test (runner personalizzato)
python run_tests.py --type unit                  # Solo test unitari
python run_tests.py --type e2e                   # Solo test e2e
python run_tests.py --runner pytest              # Usa pytest
python run_tests.py --runner simple              # Usa runner personalizzato
python run_tests.py --coverage                   # Con coverage report
python run_tests.py --file tests/test_unit.py    # File specifico
```

### Tipologie di test

- **Test Unitari** (`tests/test_unit.py`): Testano i singoli componenti (vision service, bot handlers)
- **Test di Integrazione** (`tests/test_e2e.py`): Testano il flusso completo end-to-end
- **Test Componenti** (`tests/test_telegram_bot.py`, `tests/test_vision_service.py`): Test specifici per componenti
- **Test di Resilienza**: Testano la gestione degli errori e la robustezza

### Test Coverage

I test includono:

- ✅ **Test Unitari (12 test)**:
  - Inizializzazione servizi e bot
  - Importazione moduli
  - Validazione configurazioni
  
- ✅ **Test End-to-End (7 test)**:
  - Flusso completo elaborazione immagini
  - Riconoscimento e estrazione informazioni eventi
  - AWS Lambda handler completo
  - Test resilienza e recupero errori
  
- ✅ **Test Componenti**:
  - Telegram bot handlers (11 test)
  - Vision service con OpenAI (6 test)

- ✅ **Funzionalità Testate**:
  - Descrizioni in italiano
  - Citazioni dei messaggi originali
  - Gestione errori con messaggi in italiano
  - Elaborazione concorrente
  - Degradazione controllata

## Configurazione API Keys

Le API key vengono memorizzate in AWS SSM Parameter Store:

- `/image-descriptor/telegram-token`
- `/image-descriptor/openai-api-key`
