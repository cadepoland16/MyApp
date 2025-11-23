import os
from dotenv import load_dotenv

# Load the .env file
load_dotenv()

APP_ENV = os.getenv("APP_ENV", "dev")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")