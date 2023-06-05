import requests
import datetime
from urllib.parse import urlencode
from dashboard.models import (
    RankEnum,
    Taxon,
    UrlSearchArgs,
    MeteoDataset,
    PaxDataset,
    DatasetType,
    ViewConfiguration,
    to_typed_dataset,
    PollinatorDataset,
)
from dashboard.utils.communication import CachedRequest, construct_url

from dashboard.api_clients.meteodata_client import (
    get_meteo_datasets,
    get_meteo_measurements,
    get_meteo_parameters,
    get_meteo_stations,
    get_meteo_statsagg,
    get_meteo_time_of_day,
)
from dashboard.api_clients.sensordata_client import (
    get_pax_timeseries,
    get_pax_tod,
    get_env_timeseries,
    get_env_tod,
)
from dashboard.api_clients.deployments_client import get_deployment_location

from dashboard.api_clients.bird_results_client import (
    get_detection_dates,
    get_detection_locations,
    get_detection_count,
    get_detection_time_of_day,
)
from dashboard.api_clients.pollinator_results_client import (
    get_polli_detection_dates,
    get_polli_detection_tod,
    get_polli_detection_locations
)



def get_time_series_from_query_args(qargs_dict, auth_cookie=None):
    args = UrlSearchArgs(**qargs_dict)
    vc = args.view_config
    ds = to_typed_dataset(args.dataset)
    return load_ts_data(ds, vc,vc, auth_cookie=auth_cookie)


def get_time_of_day_from_qargs(qargs_dict, auth_cookie=None):
    args = UrlSearchArgs(**qargs_dict)
    vc = args.view_config
    ds = to_typed_dataset(args.dataset)
    return load_tod_data(ds, vc,vc, auth_cookie=auth_cookie)




def get_locations_from_qargs(qargs_dict):
    args = UrlSearchArgs(**qargs_dict)
    if args.dataset is None:
        return None
    vc = args.view_config
    ds = to_typed_dataset(args.dataset)
    return load_map_data(ds, vc,vc)



def get_statsagg_from_qargs(qargs_dict, auth_cookie=None):
    args = UrlSearchArgs(**qargs_dict)
    if args.dataset is None:
        return None
    vc = args.view_config
    ds = to_typed_dataset(args.dataset)
    return load_statsagg_data(ds, vc,vc, auth_cookie=auth_cookie)

    args = UrlSearchArgs(**qargs_dict)
    if args.dataset is None:
        return None
    vc = args.view_config
    if args.dataset.get("type") == "meteodata":
        meteodataset = MeteoDataset(**args.dataset)
        return get_meteo_statsagg(
            station_id=meteodataset.station_id,
            param_id=meteodataset.param_id,
            time_from=vc.time_from,
            time_to=vc.time_to,
            auth_cookie=auth_cookie,
        )

    elif args.dataset.get("type") == "birds":
        taxon = Taxon(**args.dataset)
        return {
            "total_detections": get_detection_count(
                taxon_id=taxon.datum_id,
                confidence=vc.confidence,
                time_from=vc.time_from,
                time_to=vc.time_to,
            )
        }
    elif args.dataset.get("type") == "pax":
        paxds = PaxDataset(**args.dataset)
        pax_values = get_pax_timeseries(paxds.deployment_id, bucket_width="1d")
        if pax_values is not None:
            total_count = sum(pax_values.get("pax"))
        else:
            total_count = 0
        return {"total_detections": total_count}
    elif args.dataset.get("type") == DatasetType.pollinators:
        ds = PollinatorDataset(**args.dataset)
        polli_detections = get_polli_detection_dates(
            ds.pollinator_class,
            deployment_ids=ds.deployment_id,
            confidence=vc.confidence,
            bucket_width=vc.bucket,
            time_from=vc.time_from,
            time_to=vc.time_to,
        )
        if polli_detections is not None:
            total_count = sum(polli_detections.get("detections"))
        else:
            total_count = 0
        return {"total_detections": total_count}
    else:
        return {}


def load_ts_data(dataset, cfg,  vc: ViewConfiguration, auth_cookie=None):
    if not isinstance(cfg, ViewConfiguration):
        cfg = ViewConfiguration(**cfg)
    if isinstance(dataset, dict):
        ds = to_typed_dataset(dataset)
    else:
        ds = dataset
    if ds.type == DatasetType.pax:
        res = get_pax_timeseries(
            ds.deployment_id,
            bucket_width=vc.bucket,
            time_from=vc.time_from,
            time_to=vc.time_to,
        )
        if res is not None:
            dates = res.get("buckets")
            values = res.get("pax")
            if cfg.normalize:
                values = [
                    (v - min(values)) / (max(values) - min(values)) for v in values
                ]
            return dates, values
    elif ds.type == DatasetType.birds:
        res = get_detection_dates(
            ds.datum_id,
            confidence=cfg.confidence,
            bucket_width=vc.bucket,
            time_from=vc.time_from,
            time_to=vc.time_to,
        )
        if res is not None:
            dates = res.get("bucket")
            values = res.get("detections")
            if cfg.normalize:
                values = [
                    (v - min(values)) / (max(values) - min(values)) for v in values
                ]
            return dates, values
    elif ds.type == DatasetType.meteodata:
        res = get_meteo_measurements(
            station_id=ds.station_id,
            param_id=ds.param_id,
            bucket_width=vc.bucket,
            aggregation=cfg.agg,
            time_from=vc.time_from,
            time_to=vc.time_to,
            auth_cookie=auth_cookie,
        )
        dates = res.get("time")
        values = res.get("value")

        if cfg.normalize:
            values = [(v - min(values)) / (max(values) - min(values)) for v in values]
        return dates, values
    elif ds.type == DatasetType.pollinators:
        res = get_polli_detection_dates(
            pollinator_class=ds.pollinator_class,
            deployment_ids=ds.deployment_id,
            confidence=cfg.confidence,
            bucket_width=vc.bucket,
            time_from=vc.time_from,
            time_to=vc.time_to,
        )
        dates = res.get("bucket")
        values = res.get("detections")

        if cfg.normalize:
            values = [(v - min(values)) / (max(values) - min(values)) for v in values]
        return dates, values   
    elif ds.type == DatasetType.env_temp:
        res = get_env_timeseries(
            ds.deployment_id,
            measurement_type="temperature",
            aggregation=cfg.agg,
            bucket_width=vc.bucket,
            time_from=vc.time_from,
            time_to=vc.time_to,
        )
        if res is not None:
            dates = res.get("time")
            values = res.get("value")
            if cfg.normalize:
                values = [(v - min(values)) / (max(values) - min(values)) for v in values]
            return dates, values
    elif ds.type == DatasetType.env_humi:
        res = get_env_timeseries(
            ds.deployment_id,
            measurement_type="humidity",
            aggregation=cfg.agg,
            bucket_width=vc.bucket,
            time_from=vc.time_from,
            time_to=vc.time_to,
        )
        if res is not None:
            dates = res.get("time")
            values = res.get("value")
            if cfg.normalize:
                values = [(v - min(values)) / (max(values) - min(values)) for v in values]
            return dates, values
    elif ds.type == DatasetType.env_moist:
        res = get_env_timeseries(
            ds.deployment_id,
            measurement_type="moisture",
            aggregation=cfg.agg,
            bucket_width=vc.bucket,
            time_from=vc.time_from,
            time_to=vc.time_to,
        )
        if res is not None:
            dates = res.get("time")
            values = res.get("value")
            if cfg.normalize:
                values = [(v - min(values)) / (max(values) - min(values)) for v in values]
            return dates, values

   
    return


def load_tod_data(dataset, cfg,  vc: ViewConfiguration, auth_cookie=None, bucket_width_m = 60):
    if not isinstance(cfg, ViewConfiguration):
        cfg = ViewConfiguration(**cfg)
    if isinstance(dataset, dict):
        ds = to_typed_dataset(dataset)
    else:
        ds = dataset
    if ds.type == DatasetType.pax:
        res = get_pax_tod(
            ds.deployment_id,
            bucket_width_m=bucket_width_m,
            time_from=vc.time_from,
            time_to=vc.time_to,
        )
        if res is not None:
            minutes_of_day = res.get("minuteOfDay")
            values = res.get("pax")
            if cfg.normalize:
                values = [
                    (v - min(values)) / (max(values) - min(values)) for v in values
                ]
            return minutes_of_day, values
    elif ds.type == DatasetType.birds:
        res = get_detection_time_of_day(
            taxon_id=ds.datum_id,
            confidence=cfg.confidence,
            bucket_width_m=bucket_width_m,
            time_from=vc.time_from,
            time_to=vc.time_to,
        )
        minutes_of_day = res.get("minuteOfDay")
        values = res.get("detections")
        if cfg.normalize:
            values = [
                (v - min(values)) / (max(values) - min(values)) for v in values
            ]
        return minutes_of_day, values
    
    elif ds.type == DatasetType.meteodata:
        res = get_meteo_time_of_day(
            station_id=ds.station_id,
            param_id=ds.param_id,
            aggregation=cfg.agg,
            bucket_width_m=bucket_width_m,
            time_from=vc.time_from,
            time_to=vc.time_to,
            auth_cookie=auth_cookie,
        )
        if isinstance(res, list):
            return [],[]
        minutes_of_day = res.get("minute_of_day")
        values = res.get("value")
        if values is None:
            return [],[]

        if cfg.normalize:
            values = [
                (v - min(values)) / (max(values) - min(values)) for v in values
            ]
        return minutes_of_day, values


    elif ds.type == DatasetType.pollinators:
        res = get_polli_detection_tod(
            ds.pollinator_class,
            deployment_ids=ds.deployment_id,
            confidence=vc.confidence,
            bucket_width_m=bucket_width_m,
            time_from=vc.time_from,
            time_to=vc.time_to,
        )
        minutes_of_day = res.get("minuteOfDay")
        values = res.get("detections")
        if cfg.normalize:
            values = [
                (v - min(values)) / (max(values) - min(values)) for v in values
            ]
        return minutes_of_day, values
    
    elif ds.type == DatasetType.env_temp:
        res = get_env_tod(
            deployment_id=ds.deployment_id,
            measurement_type="temperature",
            aggregation=cfg.agg,
            bucket_width_m=bucket_width_m,
            time_from=vc.time_from,
            time_to=vc.time_to,
        )
        minutes_of_day = res.get("minuteOfDay")
        values = res.get("value")
        if cfg.normalize:
            values = [
                (v - min(values)) / (max(values) - min(values)) for v in values
            ]
        return minutes_of_day, values
    
    elif ds.type == DatasetType.env_humi:
        res = get_env_tod(
            deployment_id=ds.deployment_id,
            measurement_type="humidity",
            aggregation=cfg.agg,
            bucket_width_m=bucket_width_m,
            time_from=vc.time_from,
            time_to=vc.time_to,
        )
        minutes_of_day = res.get("minuteOfDay")
        values = res.get("value")
        if cfg.normalize:
            values = [
                (v - min(values)) / (max(values) - min(values)) for v in values
            ]
        return minutes_of_day, values
    
    elif ds.type == DatasetType.env_moist:
        res = get_env_tod(
            deployment_id=ds.deployment_id,
            measurement_type="moisture",
            aggregation=cfg.agg,
            bucket_width_m=bucket_width_m,
            time_from=vc.time_from,
            time_to=vc.time_to,
        )
        minutes_of_day = res.get("minuteOfDay")
        values = res.get("value")
        if cfg.normalize:
            values = [
                (v - min(values)) / (max(values) - min(values)) for v in values
            ]
        return minutes_of_day, values
    
def load_map_data(dataset, cfg,  vc: ViewConfiguration, auth_cookie=None):
    if not isinstance(cfg, ViewConfiguration):
        cfg = ViewConfiguration(**cfg)
    if isinstance(dataset, dict):
        ds = to_typed_dataset(dataset)
    else:
        ds = dataset
    if ds.type == DatasetType.meteodata:
        station_info = get_meteo_stations(ds.station_id)
        if isinstance(station_info, list):
            station_info = station_info[0]
        response = {
            "latitude": [station_info.get("location").get("lat")],
            "longitude": [station_info.get("location").get("lon")],
            "name": [station_info.get("station_name")],
            "id": [ds.station_id],
        }
        return response
    elif ds.type == DatasetType.pollinators:
        locations = get_polli_detection_locations(
            pollinator_class=ds.pollinator_class,
            deployment_ids=ds.deployment_id,
            confidence=cfg.confidence,
            time_from=vc.time_from,
            time_to=vc.time_to
        )
        if locations:
            response = {
                "latitude": [l.get("location").get("lat") for l in locations],
                "longitude": [l.get("location").get("lon") for l in locations],
                "name": [f'deplpoyment {l.get("deployment_id")}' for l in locations],
                "id": [l.get("deployment_id") for l in locations],
            }
            return response
    
    elif ds.type == DatasetType.birds:
        locations = get_detection_locations(
            ds.datum_id,
            confidence=cfg.confidence,
            time_from=vc.time_from,
            time_to=vc.time_to,
        )
        if locations:
            response = {
                "latitude": [l.get("location").get("lat") for l in locations],
                "longitude": [l.get("location").get("lon") for l in locations],
                "name": [f'deplpoyment {l.get("deployment_id")}' for l in locations],
                "id": [l.get("deployment_id") for l in locations],
            }
            return response
    elif ds.type in [
        DatasetType.pax,
        DatasetType.env_humi,
        DatasetType.env_moist,
        DatasetType.env_temp,
    ]:

        locations = get_deployment_location(ds.deployment_id)
        if locations:
            response = {
                "latitude": [locations.get("latitude")],
                "longitude": [locations.get("longitude")],
                "name": [f"deplpoyment {ds.deployment_id}"],
                "id": [ds.deployment_id],
            }
            return response
    return {"latitude": [], "longitude": [], "name": [], "id": []}


def load_statsagg_data(dataset, cfg, vc:ViewConfiguration = None, auth_cookie=None):
    if not isinstance(cfg, ViewConfiguration):
        cfg = ViewConfiguration(**cfg)
    ds = dataset if not isinstance(dataset, dict) else to_typed_dataset(dataset)
        
    if ds.type == DatasetType.meteodata:
        return get_meteo_statsagg(
            station_id=ds.station_id,
            param_id=ds.param_id,
            time_from=vc.time_from,
            time_to=vc.time_to,
            auth_cookie=auth_cookie,
        )
    
    elif ds.type == DatasetType.birds:
        return {
            "total_detections": get_detection_count(
                taxon_id=ds.datum_id,
                confidence=cfg.confidence,
                time_from=vc.time_from,
                time_to=vc.time_to,
            )
        }
    elif ds.type == DatasetType.pax:
        pax_values = get_pax_timeseries(ds.deployment_id, bucket_width=vc.bucket, time_from=cfg.time_from, time_to=cfg.time_to)
        if pax_values is not None:
            total_count = sum(pax_values.get("pax"))
        else:
            total_count = 0
        return {"total_detections": total_count}

    elif ds.type == DatasetType.pollinators:
        
        polli_detections = get_polli_detection_dates(
            ds.pollinator_class,
            deployment_ids=ds.deployment_id,
            confidence=cfg.confidence,
            bucket_width=vc.bucket,
            time_from=vc.time_from,
            time_to=vc.time_to,
        )
        if polli_detections is not None:
            total_count = sum(polli_detections.get("detections"))
        else:
            total_count = 0
        return {"total_detections": total_count}

    else:
        return {"no data":True}