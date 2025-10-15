import os
from dotenv import load_dotenv


load_dotenv()

os.environ["TF_CPP_MIN_LOG_LEVEL"] = "0"

class Config:
    
    MODEL_PATH = os.path.join(os.path.dirname(__file__), "models")
    CACHE_DIR = os.path.join(os.path.dirname(__file__), "cache")
    
class DevConfig(Config):
    DEBUG = True
    PORT = 6000
