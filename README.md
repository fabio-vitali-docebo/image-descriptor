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
2. La frase "Ecco la descrizione dell'immagine:"
3. **Riconoscimento eventi**: Se l'immagine contiene un annuncio di evento, estrae automaticamente:
   - Nome dell'evento
   - Descrizione breve
   - Date e orari
   - Luogo/venue
   - Organizzatore
   - Informazioni sui biglietti
   - Contatti
4. Una descrizione dettagliata in italiano dell'immagine

## Project Structure

```
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

## Setup Locale

1. Clona il repository:
```bash
git clone <your-repo-url>
cd image-descriptor
```

2. Crea un ambiente virtuale:
```bash
python -m venv venv
source venv/bin/activate  # Su Windows: venv\Scripts\activate
```

3. Installa le dipendenze:
```bash
pip install -r requirements.txt
```

4. Crea un file `.env` nella root del progetto:
```bash
TELEGRAM_TOKEN=your_telegram_bot_token_here
OPENAI_API_KEY=your_openai_api_key_here
```

5. Esegui il bot localmente:
```bash
PYTHONPATH=. python src/local.py
```

## Deploy su AWS

1. Configura le credenziali AWS
2. Aggiorna le variabili in `terraform/variables.tf`
3. Esegui Terraform:
```bash
cd terraform
terraform init
terraform plan
terraform apply
```

## Configurazione API Keys

Le API key vengono memorizzate in AWS SSM Parameter Store:
- `/image-descriptor/telegram-token`
- `/image-descriptor/openai-api-key` 