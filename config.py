from dotenv import load_dotenv
import os

load_dotenv()

WORLD_CUP_API_BASE = "https://worldcup26.ir"

TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_WHATSAPP_NUMBER = os.getenv("TWILIO_WHATSAPP_NUMBER")

CACHE_TTL_SECONDS = 60