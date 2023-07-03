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
    GBIFTaxon,
    BirdDataset,
)
from dashboard.utils.communication import CachedRequest, construct_url
from dashboard.utils.ts import merge_detections_dicts
from dashboard.utils.geo_utils import validate_coordinates

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
    get_detection_list_by_deployment,
)
from dashboard.api_clients.gbif_cache_client import (
    get_gbif_detection_dates,
    get_gbif_detection_locations,
    get_gbif_detection_time_of_day,
    get_gbif_detection_count,
    get_gbif_datasets,
)
from dashboard.api_clients.pollinator_results_client import (
    get_polli_detection_dates,
    get_polli_detection_tod,
    get_polli_detection_locations,
    get_polli_detection_dates_by_id,
    get_polli_detection_locations_by_id,
    get_polli_detection_tod_by_id,
    get_polli_detection_count_by_id,
    POLLINATOR_IDS,
)
from configuration import DEFAULT_TOD_BUCKET_WIDTH


def get_time_series_from_query_args(qargs_dict, auth_cookie=None):
    args = UrlSearchArgs(**qargs_dict)
    vc = args.view_config
    ds = to_typed_dataset(args.dataset)
    return load_ts_data(ds, vc, vc, auth_cookie=auth_cookie)


def get_time_of_day_from_qargs(qargs_dict, auth_cookie=None):
    args = UrlSearchArgs(**qargs_dict)
    vc = args.view_config
    ds = to_typed_dataset(args.dataset)
    return load_tod_data(ds, vc, vc, auth_cookie=auth_cookie)


def get_locations_from_qargs(qargs_dict):
    args = UrlSearchArgs(**qargs_dict)
    if args.dataset is None:
        return None
    vc = args.view_config
    ds = to_typed_dataset(args.dataset)
    return load_map_data(ds, vc, vc)


def get_statsagg_from_qargs(qargs_dict, auth_cookie=None):
    args = UrlSearchArgs(**qargs_dict)
    if args.dataset is None:
        return None
    vc = args.view_config
    ds = to_typed_dataset(args.dataset)
    return load_statsagg_data(ds, vc, vc, auth_cookie=auth_cookie)


def load_ts_data(dataset, cfg, vc: ViewConfiguration, auth_cookie=None):
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
        # include pollinators
        res = get_detection_dates(
            ds.datum_id,
            confidence=cfg.confidence,
            bucket_width=vc.bucket,
            time_from=vc.time_from,
            time_to=vc.time_to,
        )
        if int(ds.datum_id) in POLLINATOR_IDS:
            res_polli = get_polli_detection_dates_by_id(
                ds.datum_id,
                deployment_ids=None,
                confidence=cfg.confidence,
                bucket_width=vc.bucket,
                time_from=vc.time_from,
                time_to=vc.time_to,
            )
            res = merge_detections_dicts(res, res_polli)
        if res is not None:
            dates = res.get("bucket")
            values = res.get("detections")
            if cfg.normalize:
                values = [
                    (v - min(values)) / (max(values) - min(values)) for v in values
                ]
            return dates, values

    elif ds.type == DatasetType.distinct_species:
        res = get_detection_dates(
            212,
            confidence=cfg.confidence,
            bucket_width=vc.bucket,
            time_from=vc.time_from,
            time_to=vc.time_to,
            deployment_ids=ds.deployment_id,
            distinctspecies=True,
        )
        if res is not None:
            dates = res.get("bucket")
            values = res.get("detections")
            if cfg.normalize:
                values = [
                    (v - min(values)) / (max(values) - min(values)) for v in values
                ]
            return dates, values
    elif ds.type == DatasetType.gbif_observations:
        res = get_gbif_detection_dates(
            ds.datum_id,
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
            pollinator_class=ds.pollinator_class.value
            if ds.pollinator_class is not None
            else None,
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
                values = [
                    (v - min(values)) / (max(values) - min(values)) for v in values
                ]
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
                values = [
                    (v - min(values)) / (max(values) - min(values)) for v in values
                ]
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
                values = [
                    (v - min(values)) / (max(values) - min(values)) for v in values
                ]
            return dates, values

    return


def load_tod_data(
    dataset,
    cfg,
    vc: ViewConfiguration,
    auth_cookie=None,
    bucket_width_m=DEFAULT_TOD_BUCKET_WIDTH,
):
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

        if int(ds.datum_id) in POLLINATOR_IDS:
            res_polli = get_polli_detection_tod_by_id(
                ds.datum_id,
                deployment_ids=None,
                confidence=cfg.confidence,
                bucket_width_m=bucket_width_m,
                time_from=vc.time_from,
                time_to=vc.time_to,
            )
            res = merge_detections_dicts(
                res, res_polli, time_key="minuteOfDay", value_key="detections"
            )
        minutes_of_day = res.get("minuteOfDay")
        values = res.get("detections")
        if cfg.normalize:
            values = [(v - min(values)) / (max(values) - min(values)) for v in values]
        return minutes_of_day, values

    elif ds.type == DatasetType.distinct_species:
        res = get_detection_time_of_day(
            taxon_id=212,
            confidence=cfg.confidence,
            time_from=vc.time_from,
            time_to=vc.time_to,
            distinctspecies=True,
            deployment_ids=ds.deployment_id,
        )
        if res is not None:
            minutes_of_day = res.get("minuteOfDay")
            values = res.get("detections")
            if cfg.normalize:
                values = [
                    (v - min(values)) / (max(values) - min(values)) for v in values
                ]
            return minutes_of_day, values
    elif ds.type == DatasetType.gbif_observations:
        res = get_gbif_detection_time_of_day(
            taxon_id=ds.datum_id,
            bucket_width_m=bucket_width_m,
            time_from=vc.time_from,
            time_to=vc.time_to,
        )
        minutes_of_day = res.get("minuteOfDay")
        values = res.get("detections")
        if cfg.normalize:
            values = [(v - min(values)) / (max(values) - min(values)) for v in values]
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
            return [], []
        minutes_of_day = res.get("minute_of_day")
        values = res.get("value")
        if values is None:
            return [], []

        if cfg.normalize:
            values = [(v - min(values)) / (max(values) - min(values)) for v in values]
        return minutes_of_day, values

    elif ds.type == DatasetType.pollinators:
        res = get_polli_detection_tod(
            pollinator_class=ds.pollinator_class.value
            if ds.pollinator_class is not None
            else None,
            deployment_ids=ds.deployment_id,
            confidence=vc.confidence,
            bucket_width_m=bucket_width_m,
            time_from=vc.time_from,
            time_to=vc.time_to,
        )
        minutes_of_day = res.get("minuteOfDay")
        values = res.get("detections")
        if cfg.normalize:
            values = [(v - min(values)) / (max(values) - min(values)) for v in values]
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
            values = [(v - min(values)) / (max(values) - min(values)) for v in values]
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
            values = [(v - min(values)) / (max(values) - min(values)) for v in values]
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
            values = [(v - min(values)) / (max(values) - min(values)) for v in values]
        return minutes_of_day, values
    else:
        return [], []


def load_map_data(dataset, cfg, vc: ViewConfiguration, auth_cookie=None):
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
            pollinator_class=ds.pollinator_class.value
            if ds.pollinator_class is not None
            else None,
            deployment_ids=ds.deployment_id,
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

    elif ds.type == DatasetType.birds:
        loc_dict = {"latitude": [], "longitude": [], "name": [], "id": []}
        locations = get_detection_locations(
            ds.datum_id,
            confidence=cfg.confidence,
            time_from=vc.time_from,
            time_to=vc.time_to,
        )
        locations_polli = None
        if int(ds.datum_id) in POLLINATOR_IDS:
            locations_polli = get_polli_detection_locations_by_id(
                ds.datum_id,
                deployment_ids=None,
                confidence=cfg.confidence,
                time_from=vc.time_from,
                time_to=vc.time_to,
            )

        if locations is not None:
            for l in locations:
                latitude = l.get("location").get("lat")
                longitude = l.get("location").get("lon")
                if validate_coordinates(latitude, longitude):
                    loc_dict["latitude"].append(latitude)
                    loc_dict["longitude"].append(longitude)
                    loc_dict["name"].append(f'deplpoyment {l.get("deployment_id")}')
                    loc_dict["id"].append(l.get("deployment_id"))
        if locations_polli is not None:
            for l in locations_polli:
                latitude = l.get("location").get("lat")
                longitude = l.get("location").get("lon")
                if validate_coordinates(latitude, longitude):
                    loc_dict["latitude"].append(latitude)
                    loc_dict["longitude"].append(longitude)
                    loc_dict["name"].append(f'deplpoyment {l.get("deployment_id")}')
                    loc_dict["id"].append(l.get("deployment_id"))
        return loc_dict

    elif ds.type == DatasetType.distinct_species:
        loc_dict = {"latitude": [], "longitude": [], "name": [], "id": []}
        locations = get_detection_locations(
            212,
            confidence=cfg.confidence,
            time_from=vc.time_from,
            time_to=vc.time_to,
            distinctspecies=True,
            deployment_ids=ds.deployment_id,
        )
        if locations is not None:
            for l in locations:
                latitude = l.get("location").get("lat")
                longitude = l.get("location").get("lon")
                if validate_coordinates(latitude, longitude):
                    loc_dict["latitude"].append(latitude)
                    loc_dict["longitude"].append(longitude)
                    loc_dict["name"].append(f'deplpoyment {l.get("deployment_id")}')
                    loc_dict["id"].append(l.get("deployment_id"))

        return loc_dict
    elif ds.type == DatasetType.gbif_observations:
        locations = get_gbif_detection_locations(
            ds.datum_id,
            time_from=vc.time_from,
            time_to=vc.time_to,
        )
        if locations:
            response = {
                "latitude": [l.get("location").get("lat") for l in locations],
                "longitude": [l.get("location").get("lon") for l in locations],
                "name": [f"observation" for l in locations],
                "id": [i for i in range(len(locations))],
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


def load_statsagg_data(dataset, cfg, vc: ViewConfiguration = None, auth_cookie=None):
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
        total_detections = 0
        bird_detections = get_detection_count(
            taxon_id=ds.datum_id,
            confidence=cfg.confidence,
            time_from=vc.time_from,
            time_to=vc.time_to,
        )
        total_detections = 0 if bird_detections is None else bird_detections
        if int(ds.datum_id) in POLLINATOR_IDS:
            polli_detection_count = get_polli_detection_count_by_id(
                taxon_id=ds.datum_id,
                confidence=cfg.confidence,
                time_from=vc.time_from,
                time_to=vc.time_to,
            )
            total_detections = (
                total_detections
                if polli_detection_count is None
                else total_detections + polli_detection_count
            )

        return {"total_detections": total_detections}

    elif ds.type == DatasetType.distinct_species:
        detected_species = get_detection_list_by_deployment(
            deployment_ids=ds.deployment_id,
            confidence=cfg.confidence,
            time_from=vc.time_from,
            time_to=vc.time_to,
            limit=1000,
        )
        if isinstance(detected_species, list) and len(detected_species) > 0:
            stats = {"distinct species": len(detected_species)}
            stats.update(
                {d.get("label_sci"): d.get("count") for d in detected_species[:10]}
            )
            return stats

        return {}

    elif ds.type == DatasetType.gbif_observations:
        return {
            "total_detections": get_gbif_detection_count(
                taxon_id=ds.datum_id,
                time_from=vc.time_from,
                time_to=vc.time_to,
            )
        }
    elif ds.type == DatasetType.pax:
        pax_values = get_pax_timeseries(
            ds.deployment_id,
            bucket_width=vc.bucket,
            time_from=cfg.time_from,
            time_to=cfg.time_to,
        )
        if pax_values is not None:
            total_count = sum(pax_values.get("pax"))
        else:
            total_count = 0
        return {"total_detections": total_count}

    elif ds.type == DatasetType.pollinators:

        polli_detections = get_polli_detection_dates(
            pollinator_class=ds.pollinator_class.value
            if ds.pollinator_class is not None
            else None,
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
        return {"no data": True}


def get_data_sources(args: UrlSearchArgs):
    datasets = []
    if args.datasets is not None:
        for ds in args.datasets:
            datasets.append(to_typed_dataset(ds))
    if args.dataset is not None:
        datasets.append(to_typed_dataset(args.dataset))
    dataset_types = list(set([ds.type for ds in datasets]))
    mitwelten_datasets = []
    meteoswiss_datasets = []
    gbif_datasets = []
    for ds in datasets:
        if ds.type == DatasetType.gbif_observations:
            for datasource in get_gbif_datasets(
                ds.datum_id, args.view_config.time_from, args.view_config.time_to
            ):
                if datasource not in gbif_datasets:
                    gbif_datasets.append(datasource)
        elif ds.type == DatasetType.meteodata:
            if len(meteoswiss_datasets) == 0:
                meteoswiss_datasets.append(
                    dict(
                        name="MeteoSchweiz",
                        reference="https://www.meteoschweiz.admin.ch/",
                    )
                )
        else:
            if len(mitwelten_datasets) == 0:
                mitwelten_datasets.append(
                    dict(name="Mitwelten", reference="https://www.mitwelten.org")
                )
    datasource_dict = {}
    if len(mitwelten_datasets) > 0:
        datasource_dict["SNF Mitwelten"] = mitwelten_datasets
    if len(meteoswiss_datasets) > 0:
        datasource_dict["MeteoSchweiz"] = meteoswiss_datasets
    if len(gbif_datasets) > 0:
        datasource_dict["GBIF Datasets"] = gbif_datasets
    return datasource_dict
