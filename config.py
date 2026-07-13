from dotenv import load_dotenv
import os

load_dotenv()

INDEXER_HOST = os.getenv("INDEXER_HOST")
INDEXER_USER = os.getenv("INDEXER_USER")
INDEXER_PASSWORD = os.getenv("INDEXER_PASSWORD")