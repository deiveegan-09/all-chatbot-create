# Agriculture & Environment

A focused LLM study assistant built with Flask and the Google Gemini API.

## Scope
- Main focus: Agriculture, Horticulture
- The system prompt instructs the model to answer only educational/study questions related to this domain.
- Casual greetings are allowed; unrelated requests receive a short scope message.

## Setup
1. Create a virtual environment.
2. Install dependencies: `pip install -r requirements.txt`
3. Put your Gemini API key in `.env`.
4. Run: `python app.py`
5. Open `http://localhost:5000`.

## Production
Use Gunicorn, for example: `gunicorn --bind 0.0.0.0:8000 app:app`

## Model
Default model: `gemini-3.1-flash-lite`. Change `GEMINI_MODEL` in `.env` if needed.
