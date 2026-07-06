import requests
import time
import config

CACHE = {}


def cached_get(endpoint, ttl=60):
    url = f"{config.WORLD_CUP_API_BASE}{endpoint}"

    now = time.time()

    if url in CACHE:
        cache_time, data = CACHE[url]
        if now - cache_time < ttl:
            return data

    try:
        response = requests.get(url, timeout=15)
        response.raise_for_status()

        data = response.json()
        CACHE[url] = (now, data)

        return data

    except Exception as e:
        return {
            "error": True,
            "message": str(e)
        }


def get_games():
    return cached_get("/get/games")


def get_groups():
    return cached_get("/get/groups")


def get_teams():
    return cached_get("/get/teams")