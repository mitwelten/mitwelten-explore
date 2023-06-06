from dashboard.utils.communication import CachedRequest, construct_url
import json
with open("dashboard/data/pollinator_mapping.json","r") as f:
    pollinator_mapping = json.loads(f.read())

cr = CachedRequest("pollinator_cache",2*60*60)

def get_polli_detection_dates_by_id(taxon_id, deployment_ids, confidence, bucket_width,  time_from=None, time_to = None):
    # lookup
    if str(taxon_id) in pollinator_mapping:
        pollinator_classes = pollinator_mapping[str(taxon_id)]
        url = construct_url(f"pollinators/date", {"bucket_width":bucket_width, "conf":confidence,"from":time_from,"to":time_to})
        if isinstance(deployment_ids, list) and len(deployment_ids)>0:
            for d in deployment_ids:
                url+=f'&deployment_ids={d}'
        if isinstance(pollinator_classes, list) and len(pollinator_classes)>0:
            for pc in pollinator_classes:
                url+=f'&pollinator_class={pc}'
        print(url)
        
        res = cr.get(url)
        if res.status_code == 200:

            data =  res.json()
            return data
    return None

def get_polli_detection_dates(pollinator_class,deployment_ids, confidence, bucket_width,  time_from=None, time_to = None):
    url = construct_url(f"pollinators/date", {"pollinator_class":pollinator_class,"bucket_width":bucket_width, "conf":confidence,"from":time_from,"to":time_to})
    if isinstance(deployment_ids, list) and len(deployment_ids)>0:
        for d in deployment_ids:
            url+=f'&deployment_ids={d}'
    print(url)
    
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

