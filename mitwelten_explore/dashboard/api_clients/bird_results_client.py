from dashboard.utils.communication import CachedRequest, construct_url

cr = CachedRequest("bird_cache", 2 * 60 * 60)


def get_detection_dates(
    taxon_id, confidence, bucket_width, time_from=None, time_to=None
):
    url = construct_url(
        f"birds/{taxon_id}/date",
        {
            "bucket_width": bucket_width,
            "conf": confidence,
            "from": time_from,
            "to": time_to,
        },
    )
    res = cr.get(url)
    if res.status_code == 200:

        data = res.json()
        return data
    return None


def get_detection_locations(
    taxon_id,
    confidence,
    time_from=None,
    time_to=None,
    distinctspecies=False,
    deployment_ids=None,
):
    url = construct_url(
        f"birds/{taxon_id}/location",
        {
            "conf": confidence,
            "from": time_from,
            "to": time_to,
            "distinctspecies": distinctspecies,
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

        data = res.json()
        return data
    return None


def get_detection_time_of_day(
    taxon_id, confidence, bucket_width_m=20, time_from=None, time_to=None
):
    url = construct_url(
        f"birds/{taxon_id}/time_of_day",
        {
            "conf": confidence,
            "bucket_width_m": bucket_width_m,
            "from": time_from,
            "to": time_to,
        },
    )
    res = cr.get(url)
    if res.status_code == 200:

        data = res.json()
        return data
    return None


def get_detection_count(taxon_id, confidence, time_from=None, time_to=None):
    url = construct_url(
        f"birds/{taxon_id}/count",
        {"conf": confidence, "from": time_from, "to": time_to},
    )
    res = cr.get(url)
    if res.status_code == 200:

        data = res.json()
        return data
    return None


def get_species_detection_count_by_parent(taxon_id, confidence, limit=20):
    url = construct_url(
        f"species/parent_taxon/{taxon_id}/count", {"conf": confidence, "limit": limit}
    )
    res = cr.get(url)
    if res.status_code == 200:

        data = res.json()
        return data
    return None


def get_detection_list_by_deployment(
    confidence=0.6, deployment_ids=None, time_from=None, time_to=None, limit=1000
):
    url = construct_url(
        f"birds/detectionlist",
        {"conf": confidence, "limit": limit, "from": time_from, "to": time_to},
    )
    if isinstance(deployment_ids, list) and len(deployment_ids) > 0:
        for d in deployment_ids:
            url += f"&deployment_ids={d}"
    res = cr.get(url)
    if res.status_code == 200:

        data = res.json()
        return data
    return None
