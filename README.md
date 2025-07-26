# Telegram Image Description Bot

A Telegram bot that automatically provides detailed descriptions of images posted in a channel using OpenAI's Vision API.

## Features

- Automatically detects and processes images posted in a Telegram channel
- Generates detailed descriptions using OpenAI Vision API (gpt-4o-mini)
- Extensible architecture for easy integration of different multimodal LLMs
- Serverless deployment on AWS Lambda
- Infrastructure as Code using Terraform

## Prerequisites

- Python 3.9+
- Terraform 1.0+
- AWS CLI configured with appropriate permissions
- Telegram Bot Token (from [@BotFather](https://t.me/botfather))
- OpenAI API Key

## Project Structure

```
.
├── src/
│   ├── bot/            # Telegram bot implementation
│   ├── services/       # Vision services implementation
│   └── handlers/       # AWS Lambda handlers
├── terraform/          # Infrastructure as Code
├── tests/             # Unit and integration tests
├── requirements.txt   # Python dependencies
└── README.md         # This file
```

## Setup Instructions

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/telegram-image-descriptor
   cd telegram-image-descriptor
   ```

2. **Create and activate virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: .\venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure AWS SSM Parameters**
   
   Create the following parameters in AWS SSM:
   - `/telegram-bot/prod/telegram-token`
   - `/telegram-bot/prod/openai-api-key`

5. **Deploy Infrastructure**
   ```bash
   cd terraform
   terraform init
   terraform plan
   terraform apply
   ```

## Local Development

1. **Set up environment variables**
   ```bash
   # Create .env file in project root
   echo "TELEGRAM_TOKEN=your_telegram_token" > .env
   echo "OPENAI_API_KEY=your_openai_api_key" >> .env
   ```

2. **Run the bot locally**
   ```bash
   PYTHONPATH=. python src/local.py
   ```

## Testing

```bash
pytest tests/
```

## Deployment

The bot is automatically deployed to AWS Lambda when changes are pushed to the main branch.

## Architecture

The bot uses a serverless architecture:
- AWS API Gateway receives webhook updates from Telegram
- AWS Lambda processes the updates and calls OpenAI Vision API
- AWS SSM Parameter Store securely stores API keys
- Terraform manages all AWS resources

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details. 