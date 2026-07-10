# constants.py

import os
import logging
import dotenv

logger = logging.getLogger("wifind-my-friends")

if os.path.exists(".env"): logger.info("Loading env variables from .env file.")
dotenv.load_dotenv()

MASTER_API_TOKEN = os.environ['MASTER_API_TOKEN']