import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Telegram
    TOKEN = os.getenv("TELEGRAM_TOKEN")
    
    # Plisio
    PLISIO_API_KEY = os.getenv("PLISIO_API_KEY")
    PLISIO_SECRET = os.getenv("PLISIO_SECRET")
    WEBHOOK_URL = os.getenv("WEBHOOK_URL")
    
    # Database
    DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///shop.db")
    
    # Product
    DEFAULT_CURRENCY = "USDT"
