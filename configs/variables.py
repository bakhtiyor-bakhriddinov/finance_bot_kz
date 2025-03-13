from dotenv import load_dotenv
import os

load_dotenv()


# Set up the logging
# logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
# logging.info('Starting Bot ...')


BOT_TOKEN = os.environ.get("BOT_TOKEN")
BASE_URL = os.environ.get("BASE_URL")
FRONT_URL = os.environ.get("FRONT_URL")
ACCESS_TOKEN = os.environ.get("ACCESS_TOKEN")
JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY")
ALGORITHM = os.environ.get("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = os.environ.get("ACCESS_TOKEN_EXPIRE_MINUTES")
BOT_USER = os.environ.get("BOT_USER")
BOT_PASSWORD = os.environ.get("BOT_PASSWORD")

