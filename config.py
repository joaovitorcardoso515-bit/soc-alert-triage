from dotenv import load_dotenv
import os

load_dotenv()

WAZUH_HOST = os.getenv("WAZUH_HOST")
WAZUH_USER = os.getenv("WAZUH_USER")
WAZUH_PASSWORD = os.getenv("WAZUH_PASSWORD")