import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    # API Keys
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
    OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")
    
    # Twilio Config
    TWILIO_SID = os.getenv("TWILIO_SID", "")
    TWILIO_TOKEN = os.getenv("TWILIO_TOKEN", "")
    TWILIO_WHATSAPP = os.getenv("TWILIO_WHATSAPP", "")
    
    # Google Config
    GOOGLE_CREDENTIALS = os.getenv("GOOGLE_CREDENTIALS", "")
    
    # Database Config
    DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://atendente:atendente@db:5432/atendente")
    
    # Redis Config
    REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379/0")
    
    # LLM Config
    LLM_MODEL = os.getenv("LLM_MODEL", "openrouter/auto")  # openrouter/auto, gpt-4, etc.
    LLM_PROVIDER = os.getenv("LLM_PROVIDER", "openrouter")  # openrouter or openai

settings = Settings()
