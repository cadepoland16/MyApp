from openai import OpenAI
from app.config import OPENAI_API_KEY, APP_ENV

# Create a single OpenAI client instance using your API key
client = OpenAI(api_key=OPENAI_API_KEY)


def simple_chat(message: str) -> str:
    """
    Send a user message to OpenAI and return the assistant's reply as plain text.
    In mock mode (APP_ENV=mock), return a fake reply without calling the API.
    """

    # 🔹 MOCK MODE: no network calls, no cost
    if APP_ENV == "mock":
        return f"[MOCK REPLY] You said: {message}"

    # 🔹 REAL MODE: this part will only run when you change APP_ENV in the future
    if not OPENAI_API_KEY:
        raise RuntimeError("OPENAI_API_KEY is not set in the environment.")

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a helpful, concise assistant."},
            {"role": "user", "content": message},
        ],
    )

    return response.choices[0].message.content or ""