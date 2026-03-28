import os
from functools import lru_cache
from sqlmodel import create_engine
from dotenv import load_dotenv

load_dotenv()

MYSQL_SERVER = os.getenv("MYSQL_SERVER", "localhost")
MYSQL_USER = os.getenv("MYSQL_USER", "root")
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD", "")
MYSQL_DB = os.getenv("MYSQL_DB", "logitrack")
MYSQL_PORT = os.getenv("MYSQL_PORT", "3306")


@lru_cache()
def get_engine():
    url = f"mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_SERVER}:{MYSQL_PORT}/{MYSQL_DB}"
    return create_engine(url)


engine = get_engine()