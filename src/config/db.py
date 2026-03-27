import os
from sqlmodel import create_engine
from dotenv import load_dotenv

load_dotenv()

MYSQL_SERVER = os.getenv("MYSQL_SERVER")

if not MYSQL_SERVER:
    url = "sqlite:///./database.db"
else:

    MYSQL_USER = os.getenv("MYSQL_USER", "root")
    MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD","")
    MYSQL_DB = os.getenv("MYSQL_DB", "logitrack_db")
    MYSQL_PORT = os.getenv("MYSQL_PORT", "3306")
    url = f"mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_SERVER}:{MYSQL_PORT}/{MYSQL_DB}"
    
engine = create_engine(url)