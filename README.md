# PioloBot — AI Chatbot Widget

An AI-powered chatbot embedded on Piolo Avenido's portfolio website. Visitors can ask questions about Piolo's skills, projects, and experience. The bot uses a system prompt containing all portfolio information and responds as "PioloBot."

Live on: https://piolo.betamaxgroup.tech (click the chat icon in the bottom-right corner)

## Features

- Floating chat button with notification dot
- Chat panel with gradient header matching portfolio theme
- Quick-start suggestion chips
- Typing indicator while AI is thinking
- Context-aware responses about skills, projects, experience, and contact info
- 500-character message limit, 300-token max response

## Tech Stack

- **Backend:** Python stdlib HTTP server (no frameworks — just `http.server`)
- **AI:** deepseek-v4-flash via Ollama Cloud
- **Frontend:** Vanilla HTML/CSS/JS widget injected into portfolio page
- **Email:** Mailgun SMTP for contact form
- **Deployment:** Bare-metal Python process, Caddy reverse proxy, Cloudflare TLS

## How It Works

```
Visitor types message → POST /chat on portfolio server
→ server.py forwards to Ollama Cloud (deepseek-v4-flash)
→ System prompt contains all of Piolo's portfolio info
→ AI responds as "PioloBot" → Frontend renders response
```

## Setup

1. Clone the repo
2. Copy `.env.example` to `.env` and fill in your API keys
3. Run the server:
   ```bash
   OLLAMA_API_KEY=your-key python3 server.py
   ```
4. The server runs on port 9015

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `OLLAMA_API_KEY` | Ollama Cloud API key | Required |
| `LLM_MODEL` | Model name | `deepseek-v4-flash` |
| `MAILGUN_API_KEY` | Mailgun API key for contact form | Optional |
| `MAILGUN_DOMAIN` | Mailgun domain | `betamaxgroup.tech` |

## Author

Piolo Rafael Avenido — [GitHub](https://github.com/pioloavenido123-source) — [Portfolio](https://piolo.betamaxgroup.tech)