from openai import OpenAI
from ..config import OPENAI_API_KEY

# Create a single OpenAI client instance using your API key
client = OpenAI(api_key=OPENAI_API_KEY)


def simple_chat(message: str) -> str:
    """
    Send a user message to OpenAI and return the assistant's reply as plain text.
    """
    if not OPENAI_API_KEY:
        # Helpful error if you forgot to set the key
        raise RuntimeError("OPENAI_API_KEY is not set in the environment.")

    response = client.chat.completions.create(
        model="gpt-4o-mini",  # good, fast default model
        messages=[
            {"role": "system", "content": "You are a helpful, concise assistant."},
            {"role": "user", "content": message},
        ],
    )

    # Return the text of the first choice
    return response.choices[0].message.content or ""