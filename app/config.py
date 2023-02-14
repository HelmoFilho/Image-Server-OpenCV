## -- Importing External Modules -- ##
import dotenv, os

## -- Importing Internal Modules -- ##

dotenv.load_dotenv("./config/.env")

PORT = int(os.getenv("PORT_IS", 5000))
MAIN_FOLDER = os.getenv("CHECK_FOLDER_IS", "./images")