from dashboard.utils.communication import CachedRequest, construct_url
from configuration import DATA_API_URL

cr = CachedRequest("deployments_cache", 60 * 60)


def get_deployments(type_query=None, deployment_id=None):
    url = f"{DATA_API_URL}deployments"
    res = cr.get(url)
    if res.status_code == 200:
        deployments = res.json()
        if deployment_id:
            deployments = [
                d for d in deployments if d.get("deployment_id") == deployment_id
            ]
        if type_query:
            filtered_deployments = [
                d
                for d in deployments
                if type_query in d.get("node").get("type").lower()
            ]
            return filtered_deployments
        return deployments
    return []


def get_deployment_location(deployment_id):
    deployment = get_deployments(deployment_id=deployment_id)
    if isinstance(deployment, list):
        deployment = deployment[0]
    if deployment is None:
        return None
    return {
        "latitude": deployment.get("location").get("lat"),
        "longitude": deployment.get("location").get("lon"),
    }


def get_deployment_info(deployment_id):
    url = f"{DATA_API_URL}deployment/{deployment_id}"
    res = cr.get(url)
    if res.status_code == 200:
        return res.json()
    return None


def get_total_image_count(deployment_ids=None, time_from=None, time_to=None):
    url = construct_url(
        "statistics/image/count",
        {
            "from": time_from,
            "to": time_to,
        },
    )
    if deployment_ids is not None:
        if isinstance(deployment_ids, list) and len(deployment_ids) > 0:
            for d in deployment_ids:
                url += f"&deployment_ids={d}"
        else:
            url += f"&deployment_ids={deployment_ids}"
    res = cr.get(url)
    if res.status_code == 200:
        return res.json()
    return None


def get_total_audio_duration(deployment_ids=None, time_from=None, time_to=None):
    url = construct_url(
        "statistics/audio/total_duration",
        {
            "from": time_from,
            "to": time_to,
        },
    )
    if deployment_ids is not None:
        if isinstance(deployment_ids, list) and len(deployment_ids) > 0:
            for d in deployment_ids:
                url += f"&deployment_ids={d}"
        else:
            url += f"&deployment_ids={deployment_ids}"
    res = cr.get(url)
    if res.status_code == 200:
        return res.json()
    return None


def get_daily_audio_duration(deployment_ids=None, time_from=None, time_to=None):
    url = construct_url(
        "statistics/audio/daily_recordings",
        {
            "from": time_from,
            "to": time_to,
        },
    )
    if deployment_ids is not None:
        if isinstance(deployment_ids, list) and len(deployment_ids) > 0:
            for d in deployment_ids:
                url += f"&deployment_ids={d}"
        else:
            url += f"&deployment_ids={deployment_ids}"
    res = cr.get(url)
    if res.status_code == 200:
        return res.json()
    return None


def get_daily_image_captures(deployment_ids=None, time_from=None, time_to=None):
    url = construct_url(
        "statistics/image/daily_image_count",
        {
            "from": time_from,
            "to": time_to,
        },
    )
    if deployment_ids is not None:
        if isinstance(deployment_ids, list) and len(deployment_ids) > 0:
            for d in deployment_ids:
                url += f"&deployment_ids={d}"
        else:
            url += f"&deployment_ids={deployment_ids}"
    res = cr.get(url)
    if res.status_code == 200:
        return res.json()
    return None
