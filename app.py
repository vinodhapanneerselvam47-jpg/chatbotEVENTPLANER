"""
app.py

Flask backend for the Event Planner AI Chatbot.
Serves the chat UI and forwards user messages to the Gemini API,
using the system prompt defined in chatbot_config.py to keep the
bot focused on event-planning topics only.
"""

import os

from dotenv import load_dotenv
from flask import Flask, render_template, request, jsonify
from google import genai
from google.genai import types

from chatbot_config import SYSTEM_PROMPT

# Load environment variables from .env
load_dotenv()

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
GEMINI_MODEL = os.environ.get("GEMINI_MODEL", "gemini-3.1-flash-lite")

if not GEMINI_API_KEY:
    raise RuntimeError(
        "GEMINI_API_KEY is not set. Please add it to your .env file."
    )

client = genai.Client(api_key=GEMINI_API_KEY)

app = Flask(__name__)


@app.route("/")
def index():
    """Render the chat UI."""
    return render_template("index.html")


@app.route("/api/chat", methods=["POST"])
def chat():
    """Receive a user message and return the Gemini model's reply."""
    data = request.get_json(silent=True) or {}
    user_message = (data.get("message") or "").strip()

    if not user_message:
        return jsonify({"error": "Message cannot be empty."}), 400

    try:
        response = client.models.generate_content(
            model=GEMINI_MODEL,
            contents=user_message,
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_PROMPT,
            ),
        )
        reply_text = response.text or (
            "Sorry, I couldn't generate a response. Please try again."
        )
        return jsonify({"reply": reply_text})

    except Exception as exc:  # noqa: BLE001
        app.logger.error("Gemini API error: %s", exc)
        return jsonify(
            {"error": "Something went wrong while contacting the assistant."}
        ), 500


if __name__ == "__main__":
    app.run(debug=True)
