import os
from dotenv import load_dotenv
import logging

logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv(override=True)

SPLIT_API_KEY = os.getenv("SPLIT_API_KEY")
USER_ID = os.getenv("USER_ID")

if not SPLIT_API_KEY:
    logger.error("SPLIT_API_KEY not found in environment variables")
    raise ValueError("SPLIT_API_KEY must be set in .env file")

if not USER_ID:
    logger.error("USER_ID not found in environment variables")
    raise ValueError("USER_ID must be set in .env file")