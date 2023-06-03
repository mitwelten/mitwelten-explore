import os
import datetime

if os.path.exists("../.env"):
    from dotenv import load_dotenv
    load_dotenv("../.env")

DATA_API_URL = "https://data.mitwelten.org/api/v3/"

PATH_PREFIX = "/app/"
MITWELTEN_LOGO = "https://raw.githubusercontent.com/mitwelten/mitwelten.github.io/master/favicons/android-36x36.png"
HLJS_STYLESHEET = "https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.8.0/styles/vs2015.min.css"
REFRESH_KEY_TIME_LEFT_S = 10 * 60

KC_SERVER_URL = os.environ['KC_SERVER_URL']
KC_CLIENT_ID = os.environ['KC_CLIENT_ID']
KC_REALM_NAME = os.environ['KC_REALM_NAME']
DOMAIN_NAME = os.environ['DOMAIN_NAME']
REDIS_HOST= os.environ.get("REDIS_HOST")
REDIS_PORT= os.environ.get("REDIS_PORT")

DEFAULT_CONFIDENCE = 0.6
DEFAULT_AGGREGATION="mean"
DEFAULT_TR_START = datetime.datetime(2020,8,1)
DEFAULT_TOD_BUCKET_WIDTH = 20

DEFAULT_LAT = 47.53522891224535
DEFAULT_LON = 7.606299048260731
DEFAULT_ZOOM = 11.5