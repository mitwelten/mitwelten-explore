from dashboard.utils.communication import CachedRequest, construct_url

cr = CachedRequest("gbif_cache", 2 * 60 * 60)


def get_gbif_detection_dates(taxon_id, bucket_width, time_from=None, time_to=None):
    url = construct_url(
        f"gbif/{taxon_id}/date",
        {"bucket_width": bucket_width, "from": time_from, "to": time_to},
    )
    res = cr.get(url)
    if res.status_code == 200:

        data = res.json()
        return data
    return None


def get_gbif_detection_locations(taxon_id, time_from=None, time_to=None):
    url = construct_url(f"gbif/{taxon_id}/location", {"from": time_from, "to": time_to})
    res = cr.get(url)
    if res.status_code == 200:

        data = res.json()
        return data
    return None


def get_gbif_detection_time_of_day(
    taxon_id, bucket_width_m=20, time_from=None, time_to=None
):
    url = construct_url(
        f"gbif/{taxon_id}/time_of_day",
        {"bucket_width_m": bucket_width_m, "from": time_from, "to": time_to},
    )
    res = cr.get(url)
    if res.status_code == 200:

        data = res.json()
        return data
    return None


def get_gbif_detection_count(taxon_id, time_from=None, time_to=None):
    url = construct_url(f"gbif/{taxon_id}/count", {"from": time_from, "to": time_to})
    res = cr.get(url)
    if res.status_code == 200:

        data = res.json()
        return data
    return None


def get_gbif_datasets(taxon_id, time_from=None, time_to=None):
    url = construct_url(f"gbif/{taxon_id}/datasets", {"from": time_from, "to": time_to})
    res = cr.get(url)
    if res.status_code == 200:

        data = res.json()
        return data
    return None


def get_gbif_occurence_list(
    taxon_id, time_from=None, time_to=None, limit=100, offset=0
):
    url = construct_url(
        f"gbif/{taxon_id}/occurences",
        {"from": time_from, "to": time_to, "limit": limit, "offset": offset},
    )
    res = cr.get(url)
    if res.status_code == 200:

        data = res.json()
        return data
    return None
