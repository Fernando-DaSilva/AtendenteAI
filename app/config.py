import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    TWILIO_SID = os.getenv("TWILIO_SID")
    TWILIO_TOKEN = os.getenv("TWILIO_TOKEN")
    TWILIO_WHATSAPP = os.getenv("TWILIO_WHATSAPP")
    GOOGLE_CREDENTIALS = os.getenv("GOOGLE_CREDENTIALS")
    DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://atendente:atendente@db:5432/atendente")
    REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379/0")

settings = Settings()
