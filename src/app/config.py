import os
from dotenv import load_dotenv

# Load values from the .env file in the project root
load_dotenv()

APP_ENV = os.getenv("APP_ENV", "dev")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")