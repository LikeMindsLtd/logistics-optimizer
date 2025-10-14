import os
from dotenv import load_dotenv

load_dotenv() 

class Config:

    db_user = os.environ.get("DB_USER")
    db_password = os.environ.get("DB_PASSWORD")
    db_host = os.environ.get("DB_HOST")
    db_name = os.environ.get("DB_NAME")

    SQLALCHEMY_DATABASE_URI = (
        f"postgresql://{db_user}:{db_password}@{db_host}/{db_name}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False


class DevConfig(Config):
    DEBUG = True
