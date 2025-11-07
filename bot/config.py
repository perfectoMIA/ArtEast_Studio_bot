import os
from dotenv import load_dotenv

load_dotenv()
BOT_TOKEN = os.getenv('BOT_TOKEN')
CHAT_ID = os.getenv('CHAT_ID_TEST')
DB_PATH = os.getenv('DB_PATH')
RECEIPT_RECIPIENT = os.getenv('RECEIPT_RECIPIENT')
