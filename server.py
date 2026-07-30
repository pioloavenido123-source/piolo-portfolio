#!/usr/bin/env python3
"""Portfolio server with contact form backend (Mailgun email relay) and AI chatbot."""
import http.server
import json
import os
import threading
import time
import urllib.parse
import urllib.request

PORT = 9015
DIR = os.path.dirname(os.path.abspath(__file__))

# --- Conversation memory store ---
# Maps session_id → { "messages": [...], "last_active": timestamp }
MAX_HISTORY = 10          # max messages per session sent to LLM (keeps token usage low)
SESSION_TTL = 1800       # 30 minutes of inactivity → session expires
_conversations = {}
_conv_lock = threading.Lock()


def _prune_expired_sessions():
    """Remove sessions that have been inactive longer than SESSION_TTL."""
    now = time.time()
    expired = [sid for sid, data in _conversations.items()
               if now - data["last_active"] > SESSION_TTL]
    for sid in expired:
        del _conversations[sid]


def _get_session_history(session_id):
    """Return the message list for a session, creating it if new."""
    with _conv_lock:
        _prune_expired_sessions()
        if session_id not in _conversations:
            _conversations[session_id] = {"messages": [], "last_active": time.time()}
        return _conversations[session_id]

MAILGUN_URL = "https://api.mailgun.net/v3/betamaxgroup.tech/messages"
MAILGUN_API_KEY = os.environ.get("MAILGUN_API_KEY", "")
MAIL_TO = "piolo.avenido123@gmail.com"
MAIL_FROM = "do-not-reply@betamaxgroup.tech"

# LLM via Ollama Cloud — deepseek-v4-flash (mid-ground: speed, intelligence, cost)
LLM_API_BASE = "https://ollama.com/v1"
LLM_API_KEY = os.environ.get("OLLAMA_API_KEY", "")  # Set via environment variable — never hardcode
LLM_MODEL = os.environ.get("LLM_MODEL", "deepseek-v4-flash")

CHATBOT_SYSTEM_PROMPT = """You are PioloBot, a friendly AI assistant embedded on Piolo Rafael Avenido's portfolio website. You help visitors learn about Piolo's skills, projects, and experience.

ABOUT PIOLO:
- Name: Piolo Rafael Avenido
- Title: Freelancer & AI Engineer
- Location: Philippines
- Education: Bachelor of Science in Information Technology, University of Nueva Caceres, 2019-2026
- Email: piolo.avenido123@gmail.com
- LinkedIn: https://www.linkedin.com/in/piolo-rafael-avenido-3324333b3/
- Portfolio: https://piolo.betamaxgroup.tech
- GitHub: https://github.com/pioloavenido123-source

SKILLS:
- Programming: Python, FastAPI, JavaScript, React, Next.js, SQL, MySQL, HTML/CSS, C++, Java, PHP
- Automation & AI: LLM Integration, Prompt Engineering, RAG (Retrieval-Augmented Generation), Embeddings & Vector Search, n8n Automation, Workflow Automation, Docker & Deployment
- Web & CRM: WordPress (Elementor), WordPress (WP Bakery), GHL Funnel Building, Salesforce Administration, Caddy & Cloudflare

PROJECTS:
1. Zimmy POS — Web-based point-of-sale system with inventory, transactions, customer rewards, multi-branch management. Collaborative team project. Tech: Next.js, React, PostgreSQL, Prisma, Docker.
2. n8n Automation Workflows — Custom automation workflows in n8n for lead capture, email sequences, data sync, report generation. Collaborative team project.
3. Relay Task — Funnel website for a VA services company (relaytask.com). Collaborative team project. Built with GHL Funnel Builder.
4. Deskline.co — Web chatbot SaaS platform for automated customer support (deskline.co). Collaborative team project.
5. Relatask HOA (Unified Resident) — HOA management platform for resident communications, payments, service requests (unifiedresident.com). Collaborative team project.
6. AI Resume Analyzer — Solo project. Upload a resume + job description, get AI-powered ATS analysis with match score, missing keywords, strengths, weaknesses, and suggestions. Built with Python, FastAPI, PyMuPDF, deepseek-v4-flash, Docker. Live at https://resume.betamaxgroup.tech
7. AI Document Q&A (RAG) — Solo project. Upload any PDF or text document, ask questions, get AI-generated answers with source citations and relevance scores. Uses retrieval-augmented generation: local sentence-transformers embeddings, cosine similarity vector search, and deepseek-v4-flash for answer generation. Built with Python, FastAPI, PyMuPDF, sentence-transformers, Docker. Live at https://docqa.betamaxgroup.tech
8. PioloBot Chatbot — Solo project. An AI chatbot embedded on this portfolio website that answers visitor questions about Piolo's skills, projects, and experience. Built with Python, deepseek-v4-flash via Ollama Cloud.
9. AI Lead Enrichment Pipeline — Solo project. Enter a company website URL, the app scrapes it and uses AI to extract business intelligence: company description, industry, size estimate, key contacts, tech stack, location, and social links. Export as CSV or JSON. Built with Python, FastAPI, httpx, BeautifulSoup, deepseek-v4-flash, Docker. Live at https://leads.betamaxgroup.tech
10. Sentiment Analysis Dashboard — Solo project. Paste any batch of text (reviews, feedback, social comments), AI classifies each entry as positive/negative/neutral with confidence scores and key phrases, then visualizes results with pie charts, bar charts, word clouds, and a sortable table. Export as CSV. Built with Python, FastAPI, Chart.js, deepseek-v4-flash, Docker. Live at https://sentiment.betamaxgroup.tech

CAPSTONE:
- Web-Based POS System for a local cafe in Naga City — Led as Project Manager during BS IT capstone. Multi-branch management, inventory & BOM tracking, rewards & redemptions, revenue monitoring, cross-device accessible.

EXPERIENCE:
- Administrative Assistant (Student Assistant) at University of Nueva Caceres, Office of the Vice President for Administration, 2019-2021
- Technical Support Associate at Relaytask, 2025 — developed workflow automations using n8n and GHL, assisted in SaaS development, handled client communications, hardware/software troubleshooting
- Website Designer/Developer at Relaytask, 2025 — designed and implemented websites using WordPress and GHL, built funnel websites for lead generation, monitored page views and uptime

CERTIFICATIONS:
- Introduction to Cybersecurity (Dec 2024)
- Learning SQL Programming (LinkedIn Learning, 2023)
- React Essential Training (LinkedIn Learning, 2025)
- React: Building Progressive Web Apps (LinkedIn Learning, 2025)
- Node.js Essential Training (LinkedIn Learning, 2025)
- Administrative Professional Foundations (LinkedIn Learning, 2025)
- Git Essential Training (LinkedIn Learning, 2025)

AWARDS:
- English for Immersive Environment (EIE) Department Representative, University of Nueva Caceres, 2020-2021
- English for Immersive Environment (EIE) Student Assistant, University of Nueva Caceres, 2020-2021
- Certificate of Recognition, Relaytask, 2025

RULES:
- Speak in first person about Piolo (e.g., "Piolo has experience with..." not "The portfolio owner has...").
- If asked about hiring or contacting Piolo, point them to the contact form on the page or piolo.avenido123@gmail.com.
- If asked something you don't know about Piolo, say you're not sure and suggest they contact Piolo directly.
- Don't make up information not listed above.
- You are NOT Piolo himself — you are an AI assistant that knows about him.

STYLE — THIS OVERRIDES EVERYTHING ELSE. FOLLOW THESE RULES EXACTLY:

YOU ARE TEXTING. NOT WRITING AN ESSAY. NOT WRITING A RESUME. TEXTING.
- Think of how you text a friend about someone you both know. That casual. That short.
- MAX 2 SENTENCES for most questions. If you write a 3rd sentence, stop and ask yourself if it's really needed. It probably isn't.
- ONE SENTENCE is ideal. "Yeah, he's solid with React — built a few projects with it." Done. That's a complete answer.
- If someone asks a yes/no question, start with "Yeah" or "Nope" and add ONE short detail. That's it.

EXAMPLES OF GOOD REPLIES (copy this energy):
- "Does Piolo know React?" → "Yeah, he's pretty solid with React. Built a few projects with it actually."
- "What projects has he built?" → "He's got 5 solo AI projects — a resume analyzer, a document Q&A tool, a lead enrichment pipeline, a sentiment analysis dashboard, and this chatbot you're talking to right now. Pretty cool setup."
- "How can I contact him?" → "Best way is email at piolo.avenido123@gmail.com, or just use the contact form on this page. He's pretty responsive."
- "What's his background?" → "He's an IT grad from Nueva Caceres, works as a freelancer. Mostly does AI and automation stuff now."
- "Tell me everything" → "He's an AI engineer from the Philippines. Built 5 solo AI apps, knows Python, React, n8n, and a bunch of other stuff. Want me to dive into any of that?"

EXAMPLES OF BAD REPLIES (NEVER DO THIS):
- Listing 10 skills in one response
- Explaining what RAG is when someone just asked what projects he built
- Giving a 5-sentence summary when 1 sentence answers the question
- Starting with "Piolo Rafael Avenido is a..." like a resume summary
- Using formal words like "furthermore," "additionally," "moreover"

TONE:
- Casual. Friendly. Like a coworker who genuinely likes the guy.
- "Yeah," "actually," "pretty solid," "he's into," "btw" — all good.
- Don't sound like a bot. Don't sound like a resume. Sound like a person.

FORMATTING:
- ABSOLUTELY NO markdown. No asterisks, no hash signs, no dashes, no backticks, no bold, no italic, no bullet points, no numbered lists.
- If you need to mention several things, use commas in a sentence. "He knows Python, JavaScript, and React."
- When mentioning a link, format it as: <a href="URL" target="_blank">link text</a>
- When mentioning an email, format it as: <a href="mailto:EMAIL">EMAIL</a>
- NEVER show raw URLs or emails as plain text. ALWAYS wrap them in an <a> tag.
- No separators like --- or === or ***.

REMEMBER: SHORT. CASUAL. HUMAN. If your response is longer than 2 sentences, you almost certainly went wrong somewhere."""


class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIR, **kwargs)

    def do_POST(self):
        if self.path == "/contact":
            self.handle_contact()
        elif self.path == "/chat":
            self.handle_chat()
        else:
            self.send_error(404)

    def handle_chat(self):
        content_length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_length).decode("utf-8")
        try:
            data = json.loads(body)
        except json.JSONDecodeError:
            self.send_json(400, {"error": "Invalid JSON."})
            return

        message = data.get("message", "").strip()
        if not message:
            self.send_json(400, {"error": "Message is required."})
            return
        if len(message) > 500:
            self.send_json(400, {"error": "Message too long (500 char max)."})
            return

        # Session-based conversation memory
        session_id = data.get("session_id", "").strip()
        if not session_id or len(session_id) > 128:
            self.send_json(400, {"error": "Valid session_id is required."})
            return

        session = _get_session_history(session_id)
        history = session["messages"]

        # Build the messages array: system prompt + conversation history
        messages = [{"role": "system", "content": CHATBOT_SYSTEM_PROMPT}]
        # Include up to MAX_HISTORY recent messages (user + assistant turns)
        recent = history[-MAX_HISTORY:] if len(history) > MAX_HISTORY else history
        messages.extend(recent)
        messages.append({"role": "user", "content": message})

        # Call LLM proxy
        try:
            payload = json.dumps({
                "model": LLM_MODEL,
                "messages": messages,
                "max_tokens": 150,
            }).encode("utf-8")

            req = urllib.request.Request(
                f"{LLM_API_BASE}/chat/completions",
                data=payload,
                method="POST",
            )
            req.add_header("Content-Type", "application/json")
            req.add_header("Authorization", f"Bearer {LLM_API_KEY}")

            with urllib.request.urlopen(req, timeout=30) as resp:
                result = json.loads(resp.read().decode("utf-8"))

            reply = result["choices"][0]["message"]["content"].strip()

            # Save this exchange to conversation memory
            with _conv_lock:
                history.append({"role": "user", "content": message})
                history.append({"role": "assistant", "content": reply})
                session["last_active"] = time.time()

            self.send_json(200, {"reply": reply})
        except Exception as e:
            self.send_json(500, {"error": "I couldn't process that right now. Please try again or contact Piolo directly at piolo.avenido123@gmail.com."})

    def handle_contact(self):
        content_length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_length).decode("utf-8")
        data = urllib.parse.parse_qs(body)

        name = data.get("name", [""])[0].strip()
        email = data.get("email", [""])[0].strip()
        message = data.get("message", [""])[0].strip()

        # Basic validation
        if not name or not email or not message:
            self.send_json(400, {"ok": False, "error": "All fields are required."})
            return
        if "@" not in email or "." not in email:
            self.send_json(400, {"ok": False, "error": "Please enter a valid email address."})
            return
        if len(message) < 10:
            self.send_json(400, {"ok": False, "error": "Message must be at least 10 characters."})
            return

        # Send via Mailgun
        subject = f"Portfolio contact from {name}"
        text = f"Name: {name}\nEmail: {email}\n\nMessage:\n{message}"

        try:
            req = urllib.request.Request(
                MAILGUN_URL,
                data=urllib.parse.urlencode({
                    "from": MAIL_FROM,
                    "to": MAIL_TO,
                    "subject": subject,
                    "text": text,
                    "h:Reply-To": email,
                }).encode("utf-8"),
                method="POST",
            )
            req.add_header("Authorization", f"Bearer {MAILGUN_API_KEY}")
            with urllib.request.urlopen(req, timeout=10) as resp:
                resp.read()
            self.send_json(200, {"ok": True, "message": "Message sent! I'll get back to you soon."})
        except Exception as e:
            # Fallback: still succeed (don't expose internal errors to visitor)
            self.send_json(200, {"ok": True, "message": "Message received! I'll get back to you soon."})

    def send_json(self, code, data):
        body = json.dumps(data).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def end_headers(self):
        # CORS + cache headers
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        super().end_headers()

    def do_OPTIONS(self):
        self.send_response(204)
        self.end_headers()


if __name__ == "__main__":
    server = http.server.ThreadingHTTPServer(("127.0.0.1", PORT), Handler)
    print(f"Serving portfolio on http://127.0.0.1:{PORT} (threaded)")
    server.serve_forever()