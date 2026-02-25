import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_ID = os.getenv("CHANNEL_ID")
HUGGINGFACE_API_KEY = os.getenv("HUGGINGFACE_API_KEY")