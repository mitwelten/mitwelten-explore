from dashboard.utils.communication import CachedRequest, construct_url
from configuration import DATA_API_URL

cr = CachedRequest("deployments_cache", 2 * 60 * 60)


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
