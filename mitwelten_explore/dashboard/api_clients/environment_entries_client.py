from dashboard.utils.communication import CachedRequest, construct_url
from configuration import DATA_API_URL

cr = CachedRequest("environment_cache", 60 * 60)


def get_legend():
    url = f"{DATA_API_URL}environment/legend"
    res = cr.get(url)
    if res.status_code == 200:
        return res.json()
    return None


def get_environment_entries():
    url = f"{DATA_API_URL}environment/entries"
    res = cr.get(url)
    if res.status_code == 200:
        return res.json()
    return []


def get_environment_attribute(attribute_id):
    url = f"{DATA_API_URL}environment/attribute/{attribute_id}"
    res = cr.get(url)
    if res.status_code == 200:
        return res.json()
    return []


def get_environment_entries_nearby(lat, lon, limit):
    url = construct_url(
        f"environment/nearest", {"lat": lat, "lon": lon, "limit": limit}
    )
    res = cr.get(url)
    if res.status_code == 200:
        return res.json()
    return []
