## -- Importing External Modules -- ##
import dotenv, os

## -- Importing Internal Modules -- ##

dotenv.load_dotenv("./config/.env")

SERVER = os.getenv("SERVER_IS", "development").lower()
PORT = int(os.getenv("PORT_IS", 5000))
MAIN_FOLDER = os.getenv("CHECK_FOLDER_IS", "./images")

THREADS = int(os.getenv("THREAD_IS", 4))
CONNECTION_LIMIT = int(os.getenv("CONNECTION_LIMIT_IS", 4))
CLEANUP_INTERVAL = int(os.getenv("CLEANUP_INTERVAL_IS", 4))
CHANNEL_TIMEOUT = int(os.getenv("CHANNEL_TIMEOUT_IS", 4))