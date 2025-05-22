import os
from datetime import datetime

BOT_TOKEN = os.getenv("BOT_TOKEN", "6743476235:AAEA813MZG-wW01ZnpEEJhRzLCfFRpN6wNk")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME")

# Дата мероприятия (можно изменять)
EVENT_DATE = datetime(2025, 5, 23, 17, 0)  # YYYY-MM-DD HH:MM

# Администраторы (Telegram ID)
ADMIN_IDS = [5036565297]