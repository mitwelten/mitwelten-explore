import requests
from urllib.parse import urlencode
import jwt
from dashboard.models import AppUser
import datetime
import urllib
import json
from configuration import REDIS_HOST, REDIS_PORT, DATA_API_URL

if REDIS_HOST is not None and REDIS_PORT is not None:
    from redis import Redis
    from requests_cache import CachedSession, RedisCache

class CachedRequest:
    def __init__(self, cache_name, expire_after=15*60) -> None:
        self.connection = None
        self.backend = None
        self.session = None

        if REDIS_HOST is not None and REDIS_PORT is not None:
            self.connection = Redis(host=REDIS_HOST, port= REDIS_PORT)
            self.backend = RedisCache(connection=self.connection)
            self.session = CachedSession(cache_name, backend=self.backend, expire_after=expire_after)
    def get(self, url: str, params=None, **kwargs):
        if self.session:
            return self.session.get(url, params=params, **kwargs)
        else:
            return requests.get(url, params=params, **kwargs)
        

def construct_url(path:str, args:dict = None):
    url = f"{DATA_API_URL}{path}"
    if args:
        filtered_args = {k: v for k, v in args.items() if v is not None}
        if bool(filtered_args):
            encoded_args = urlencode(filtered_args)
            url+=f"?{encoded_args}"
    return url

def get_user_from_cookies(cookies):
    try:
        decoded_cookie = jwt.decode(
            cookies.get("auth"), options={"verify_signature": False}
        )
        return AppUser(decoded_cookie)

    except Exception as e:
        print("No user found!")
        return None


def urlencode_dict(data):
    return urllib.parse.urlencode(data, encoding='utf-8')

def string_to_dict(s:str):
    s = s.replace("'",'"').replace("None","null").replace("False","false").replace("True","true")
    return json.loads(s)

def parse_nested_qargs(qargs):
    if isinstance(qargs, dict):
        if "trace" in qargs:
            qargs["trace"] = string_to_dict(qargs["trace"])
        if "dataset" in qargs:
            qargs["dataset"] = string_to_dict(qargs["dataset"])
        if "traces" in qargs:
            qargs["traces"] = string_to_dict(qargs["traces"])
        if "datasets" in qargs:
            qargs["datasets"] = string_to_dict(qargs["datasets"])
        if "cfg" in qargs:
            qargs["cfg"] = string_to_dict(qargs["cfg"])
    return qargs

def qargs_to_dict(encoded_qargs):
    if encoded_qargs.startswith("?"):
        encoded_qargs = encoded_qargs[1:]

    return dict(urllib.parse.parse_qsl(encoded_qargs))