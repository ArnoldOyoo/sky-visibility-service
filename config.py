import os
from dotenv import load_dotenv

load_dotenv()

WEATHER_API_KEY = os.getenv("WEATHER_API_KEY", "")
WEATHER_PROVIDER = os.getenv("WEATHER_PROVIDER", "weatherapi")