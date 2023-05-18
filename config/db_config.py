import os

from dotenv import load_dotenv

load_dotenv(verbose=True)

id = os.getenv("DB_ID")
pw = os.getenv("DB_PW")
host = os.getenv("DB_HOST")
port = os.getenv("DB_PORT")
table_name = os.getenv("DB_TABLE_NAME")
