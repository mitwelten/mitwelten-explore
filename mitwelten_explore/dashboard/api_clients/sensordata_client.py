from dashboard.utils.communication import CachedRequest, construct_url

cr = CachedRequest("sensordata_client",30*60)

def get_pax_timeseries(deployment_id,bucket_width,  time_from=None, time_to = None):
    url = construct_url(f"sensordata/pax/{deployment_id}", {"bucket_width":bucket_width, "from":time_from,"to":time_to})
    res = cr.get(url)
    if res.status_code == 200:
        return res.json()
       
    return None

def get_pax_tod(deployment_id,bucket_width_m,  time_from=None, time_to = None):
    url = construct_url(f"sensordata/pax/{deployment_id}/time_of_day", {"bucket_width_m":bucket_width_m, "from":time_from,"to":time_to})
    res = cr.get(url)
    if res.status_code == 200:
        return res.json()
       
    return None

def get_env_timeseries(deployment_id,measurement_type, aggregation, bucket_width,  time_from=None, time_to = None):
    url = construct_url(f"sensordata/{measurement_type}/{deployment_id}", {"aggregation":aggregation,"bucket_width":bucket_width, "from":time_from,"to":time_to})
    res = cr.get(url)
    if res.status_code == 200:
        return res.json()
       
    return None

def get_env_tod(deployment_id,measurement_type, aggregation, bucket_width_m,  time_from=None, time_to = None):
    url = construct_url(f"sensordata/{measurement_type}/{deployment_id}/time_of_day", {"aggregation":aggregation,"bucket_width_m":bucket_width_m, "from":time_from,"to":time_to})
    res = cr.get(url)
    if res.status_code == 200:
        return res.json()
       
    return None
