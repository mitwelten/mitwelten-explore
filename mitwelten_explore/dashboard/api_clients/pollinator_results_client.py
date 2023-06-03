from dashboard.utils.communication import CachedRequest, construct_url

cr = CachedRequest("pollinator_cache",2*60*60)


def get_polli_detection_dates(pollinator_class,deployment_ids, confidence, bucket_width,  time_from=None, time_to = None):
    url = construct_url(f"pollinators/date", {"pollinator_class":pollinator_class,"bucket_width":bucket_width, "conf":confidence,"from":time_from,"to":time_to})
    print(url)
    if isinstance(deployment_ids, list) and len(deployment_ids)>0:
        for d in deployment_ids:
            url+=f'&deployment_ids={d}'
    
    res = cr.get(url)
    if res.status_code == 200:

        data =  res.json()
        return data
    return None


def get_polli_detection_locations(pollinator_class,deployment_ids, confidence,time_from=None, time_to = None):
    url = construct_url(f"pollinators/location", {"pollinator_class":pollinator_class, "conf":confidence,"from":time_from,"to":time_to})
    if isinstance(deployment_ids, list) and len(deployment_ids)>0:
        for d in deployment_ids:
            url+=f'&deployment_ids={d}'
    res = cr.get(url)
    if res.status_code == 200:

        data =  res.json()
        return data
    return None

def get_polli_detection_tod(pollinator_class,deployment_ids, confidence, bucket_width_m=20,  time_from=None, time_to = None):
    url = construct_url(f"pollinators/time_of_day", {"pollinator_class":pollinator_class,"bucket_width_m":bucket_width_m, "conf":confidence,"from":time_from,"to":time_to})
    if isinstance(deployment_ids, list) and len(deployment_ids)>0:
        for d in deployment_ids:
            url+=f'&deployment_ids={d}'
    res = cr.get(url)
    if res.status_code == 200:

        data =  res.json()
        return data
    return None

