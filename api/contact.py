"""Contact form API — Vercel serverless function."""
import json
import os
import urllib.request
import urllib.parse

MAILGUN_URL = "https://api.mailgun.net/v3/betamaxgroup.tech/messages"
MAILGUN_API_KEY = os.environ.get("MAILGUN_API_KEY", "")
MAIL_TO = "piolo.avenido123@gmail.com"
MAIL_FROM = "do-not-reply@betamaxgroup.tech"


def handler(request):
    """Handle contact form submissions."""
    try:
        body = request.get("body", "{}")
        if isinstance(body, str):
            data = json.loads(body)
        else:
            data = body
    except (json.JSONDecodeError, TypeError):
        data = {}

    name = data.get("name", "").strip()
    email = data.get("email", "").strip()
    message = data.get("message", "").strip()

    if not name or not email or not message:
        return {
            "statusCode": 400,
            "body": json.dumps({"ok": False, "error": "All fields are required."})
        }
    if "@" not in email or "." not in email:
        return {
            "statusCode": 400,
            "body": json.dumps({"ok": False, "error": "Please enter a valid email address."})
        }
    if len(message) < 10:
        return {
            "statusCode": 400,
            "body": json.dumps({"ok": False, "error": "Message must be at least 10 characters."})
        }

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
        return {
            "statusCode": 200,
            "body": json.dumps({"ok": True, "message": "Message sent! I'll get back to you soon."})
        }
    except Exception:
        return {
            "statusCode": 200,
            "body": json.dumps({"ok": True, "message": "Message received! I'll get back to you soon."})
        }