import os
import sys
from dotenv import load_dotenv

# Принудительно устанавливаем UTF-8 кодировку для предотвращения ошибок с кириллицей в Windows
sys.stdout.reconfigure(encoding='utf-8')

# Загружаем переменные из .env
load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
OWNER_ID = int(os.getenv("OWNER_ID", "0"))
TIMEZONE = os.getenv("TIMEZONE", "Europe/Moscow")

# Валидация критических параметров до старта бота
if not BOT_TOKEN:
    raise ValueError("КРИТИЧЕСКАЯ ОШИБКА: Токен бота BOT_TOKEN не указан в файле .env!")

if OWNER_ID == 0:
    raise ValueError("КРИТИЧЕСКАЯ ОШИБКА: OWNER_ID не указан в файле .env!")