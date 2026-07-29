#!/usr/bin/env python3
"""Portfolio server with contact form backend (Mailgun email relay) and AI chatbot."""
import http.server
import json
import os
import urllib.parse
import urllib.request

PORT = 9015
DIR = os.path.dirname(os.path.abspath(__file__))

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
- Education: Bachelor of Science in Information Technology
- Email: piolo.avenido123@gmail.com
- LinkedIn: https://www.linkedin.com/in/piolo-rafael-avenido-3324333b3/
- Portfolio: https://piolo.betamaxgroup.tech

SKILLS:
- Programming: Python, FastAPI, JavaScript, React, Next.js, SQL, MySQL, HTML/CSS
- Automation & AI: LLM Integration, Prompt Engineering, RAG (Retrieval-Augmented Generation), Embeddings & Vector Search, n8n Automation, Workflow Automation, Docker & Deployment
- Web & CRM: WordPress (Elementor), WordPress (WP Bakery), GHL Funnel Building, Salesforce Administration, Caddy & Cloudflare

PROJECTS:
1. Zimmy POS — Web-based point-of-sale system with inventory, transactions, customer rewards, multi-branch management. Collaborative team project. Tech: Next.js, React, PostgreSQL, Prisma, Docker.
2. n8n Automation Workflows — Custom automation workflows in n8n for lead capture, email sequences, data sync, report generation. Collaborative team project.
3. Relay Task — Funnel website for a VA services company (relaytask.com). Collaborative team project. Built with GHL Funnel Builder.
4. Deskline.co — Web chatbot SaaS platform for automated customer support (deskline.co). Collaborative team project.
5. Relatask HOA (Unified Resident) — HOA management platform for resident communications, payments, service requests (unifiedresident.com). Collaborative team project.
6. AI Resume Analyzer — Solo project. Upload a resume + job description, get AI-powered ATS analysis with match score, missing keywords, strengths, weaknesses, and suggestions. Built with Python, FastAPI, PyMuPDF, LLM API, Docker. Live at https://resume.betamaxgroup.tech
7. AI Document Q&A (RAG) — Solo project. Upload any PDF or text document, ask questions, get AI-generated answers with source citations and relevance scores. Uses retrieval-augmented generation: local sentence-transformers embeddings (all-MiniLM-L6-v2), cosine similarity vector search, and deepseek-v4-flash for answer generation. Built with Python, FastAPI, PyMuPDF, sentence-transformers, Docker. Live at https://docqa.betamaxgroup.tech
8. PioloBot Chatbot — Solo project. An AI chatbot embedded on this portfolio website that answers visitor questions about Piolo's skills, projects, and experience. Built with Python, deepseek-v4-flash via Ollama Cloud.

CAPSTONE:
- Web-Based POS System — Led as Project Manager during BS IT capstone. Multi-branch management, inventory & BOM tracking, rewards & redemptions, revenue monitoring, cross-device accessible.

EXPERIENCE:
- 3+ years experience, 8+ projects built (3 solo AI projects), 10+ certifications
- Started in front-end development building funnel websites, expanded into AI automation and workflow engineering
- Currently freelancing while pursuing AI engineering opportunities
- Solo AI projects: AI Resume Analyzer (LLM + prompt engineering), AI Document Q&A (RAG + embeddings + vector search), and PioloBot (embedded AI chatbot)

RULES:
- Be friendly, concise, and helpful. Keep responses under 150 words unless the visitor asks for detail.
- Speak in first person about Piolo (e.g., "Piolo has experience with..." not "The portfolio owner has...").
- If asked about hiring or contacting Piolo, point them to the contact form on the page or piolo.avenido123@gmail.com.
- If asked something you don't know about Piolo, say you're not sure and suggest they contact Piolo directly.
- Don't make up information not listed above.
- You are NOT Piolo himself — you are an AI assistant that knows about him."""


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

        # Call LLM proxy
        try:
            payload = json.dumps({
                "model": LLM_MODEL,
                "messages": [
                    {"role": "system", "content": CHATBOT_SYSTEM_PROMPT},
                    {"role": "user", "content": message}
                ],
                "max_tokens": 300,
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
    server = http.server.HTTPServer(("127.0.0.1", PORT), Handler)
    print(f"Serving portfolio on http://127.0.0.1:{PORT}")
    server.serve_forever()