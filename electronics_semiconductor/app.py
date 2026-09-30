import os
from flask import Flask, jsonify, request, send_file
from dotenv import load_dotenv
from google import genai
from google.genai import types
from chatbot_config import CHATBOT_CONFIG

load_dotenv()

app = Flask(__name__)
app.config["JSON_SORT_KEYS"] = False

MODEL_NAME = os.getenv("GEMINI_MODEL", "gemini-3.1-flash-lite")
API_KEY = os.getenv("GEMINI_API_KEY")

if not API_KEY:
    raise RuntimeError("GEMINI_API_KEY is not set. Add it to your .env file.")

client = genai.Client(api_key=API_KEY)

SYSTEM_INSTRUCTION = CHATBOT_CONFIG["system_prompt"]

@app.get("/")
def index():
    return send_file("index.html")

@app.get("/api/config")
def config():
    return jsonify({
        "title": CHATBOT_CONFIG["title"],
        "icon": CHATBOT_CONFIG["icon"],
        "focus": CHATBOT_CONFIG["focus"],
        "model": MODEL_NAME,
    })

@app.post("/api/chat")
def chat():
    data = request.get_json(silent=True) or {}
    message = str(data.get("message", "")).strip()
    history = data.get("history", [])

    if not message:
        return jsonify({"error": "Please enter a question."}), 400

    # Keep the client-controlled history bounded. The system prompt remains authoritative.
    safe_history = []
    for item in history[-12:]:
        role = item.get("role") if isinstance(item, dict) else None
        content = item.get("content") if isinstance(item, dict) else None
        if role in {"user", "model"} and isinstance(content, str) and content.strip():
            safe_history.append({"role": role, "parts": [{"text": content[:6000]}]})

    contents = safe_history + [{"role": "user", "parts": [{"text": message[:12000]}]}]

    try:
        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=contents,
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_INSTRUCTION,
                temperature=0.25,
                max_output_tokens=1200,
                thinking_config=types.ThinkingConfig(thinking_level="minimal"),
            ),
        )
        answer = (response.text or "I could not generate a response. Please try again.").strip()
        return jsonify({"answer": answer})
    except Exception as exc:
        app.logger.exception("Gemini request failed")
        return jsonify({"error": "The AI service could not process your request right now. Check your API key and model access."}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", "5000")), debug=os.getenv("FLASK_DEBUG", "false").lower() == "true")
