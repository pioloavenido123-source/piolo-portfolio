"""Feedback API — Vercel serverless function."""
import json
import time


def handler(request):
    """Handle chatbot feedback (stateless — just accept it)."""
    try:
        body = request.get("body", "{}")
        if isinstance(body, str):
            data = json.loads(body)
        else:
            data = body
    except (json.JSONDecodeError, TypeError):
        data = {}

    session_id = data.get("session_id", "").strip()
    rating = data.get("rating", "").strip()

    if not session_id:
        return {
            "statusCode": 400,
            "body": json.dumps({"error": "Valid session_id is required."})
        }
    if rating not in ("up", "down"):
        return {
            "statusCode": 400,
            "body": json.dumps({"error": "Rating must be 'up' or 'down'."})
        }

    return {
        "statusCode": 200,
        "body": json.dumps({"status": "ok"})
    }