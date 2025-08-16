# AI Assistant

An AI-powered email assistant that monitors incoming emails and responds automatically using an AI agent.

## Features

- Connects to IMAP email server to monitor new unseen emails.
- Sends email content to an AI agent (using Perplexity API) for generating responses.
- Parses and executes commands returned by the AI.
- Configurable via a simple GUI with connection settings and start prompt.
- Asynchronous task management.

## Requirements

- Python 3.8+
- PyQt6
- asyncio
- Additional dependencies listed in `requirements.txt`.

## Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/andriyqz/ai_assistant.git
   cd ai_assistant
   ```

2. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

## Usage

Run the application GUI:

```bash
python main.py
```

- Enter your Perplexity API token and email credentials.
- Set the start prompt for the AI assistant.
- Use **Start** to begin monitoring emails.
- Use **Stop** to halt monitoring.
- Use **Save Settings** to persist your configuration.

## Configuration

The app uses a `config.json` file to store settings:

```json
{
  "perplexity_api_token": "your_api_token_here",
  "admin_email": "admin@example.com",
  "assistant_email": "assistant@example.com",
  "assistant_email_password": "password",
  "imap_server": "imap.example.com",
  "smtp_server": "smtp.example.com",
  "smtp_port": 587,
  "start_prompt": "Your assistant start prompt here."
}
```
