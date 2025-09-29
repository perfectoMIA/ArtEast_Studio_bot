import os
from dotenv import load_dotenv

load_dotenv()
BOT_TOKEN = os.getenv('BOT_TOKEN')
ADMINS_ID = os.getenv('ADMINS_ID')
CHAT_ID = os.getenv('CHAT_ID_TEST')
