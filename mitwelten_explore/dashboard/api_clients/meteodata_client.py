from dashboard.utils.communication import CachedRequest, construct_url
from configuration import DATA_API_URL

cr = CachedRequest("meteo_cache", 60 * 60)


def get_meteo_stations(station_id=None):
    url = f"{DATA_API_URL}meteo/station"
    if station_id:
        url += f"?station_id={station_id}"
    res = cr.get(url)
    if res.status_code == 200:

        data = res.json()
        return data
    return []


def get_meteo_parameters():
    url = f"{DATA_API_URL}meteo/parameter"
    res = cr.get(url)
    if res.status_code == 200:

        data = res.json()
        return data
    return []


def get_meteo_datasets(station_id=None, unit=None):
    url = construct_url("meteo/dataset", dict(station_id=station_id, unit=unit))
    res = cr.get(url)
    if res.status_code == 200:

        data = res.json()
        return data
    return []


def get_meteo_measurements(
    station_id,
    param_id,
    bucket_width,
    aggregation,
    time_from=None,
    time_to=None,
    auth_cookie=None,
):
    url = construct_url(
        f"meteo/measurements/{station_id}/{param_id}",
        {
            "bucket_width": bucket_width,
            "aggregation": aggregation,
            "from": time_from,
            "to": time_to,
        },
    )
    if auth_cookie:
        res = cr.get(url, headers={"Authorization": f"Bearer {auth_cookie}"})
        if res.status_code == 200:

            data = res.json()
            return data
    return []


def get_meteo_time_of_day(
    station_id,
    param_id,
    bucket_width_m,
    aggregation,
    time_from=None,
    time_to=None,
    auth_cookie=None,
):
    url = construct_url(
        f"meteo/measurements_time_of_day/{station_id}/{param_id}",
        {
            "bucket_width_m": bucket_width_m,
            "aggregation": aggregation,
            "from": time_from,
            "to": time_to,
        },
    )
    if auth_cookie:
        res = cr.get(url, headers={"Authorization": f"Bearer {auth_cookie}"})
        if res.status_code == 200:

            data = res.json()
            return data
    return []


def get_meteo_statsagg(
    station_id, param_id, time_from=None, time_to=None, auth_cookie=None
):
    url = construct_url(
        f"meteo/summary/{station_id}/{param_id}", {"from": time_from, "to": time_to}
    )
    if auth_cookie:
        res = cr.get(url, headers={"Authorization": f"Bearer {auth_cookie}"})
        if res.status_code == 200:

            data = res.json()
            return data
    return {}
