from dotenv import load_dotenv
import logging
import os


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("techlinebot.log", encoding="utf-8"),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)


load_dotenv()


BOT_TOKEN = os.getenv('TOKEN')