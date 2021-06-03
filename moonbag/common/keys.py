from dotenv import load_dotenv
import os

load_dotenv()


WALES_API_KEY = os.getenv("WALES_API_KEY") or "Enter your key"
CC_API_KEY = os.getenv("CC_API_KEY") or "Enter your key"

REDDIT_CLIENT_ID = os.getenv('REDDIT_CLIENT_ID') or "Enter your client id"
REDDIT_CLIENT_SECRET = os.getenv('REDDIT_CLIENT_SECRET') or "Enter your client secret"
REDDIT_USER_AGENT = os.getenv('REDDIT_USER_AGENT') or "Enter your client user agent"
CRYPTO_PANIC_API = os.getenv('CRYPTO_PANIC_API') or "Visit https://cryptopanic.com/developers/api/ for key"
