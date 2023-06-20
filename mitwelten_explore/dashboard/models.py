import datetime
from enum import Enum
from configuration import DEFAULT_AGGREGATION, DEFAULT_CONFIDENCE
from dashboard.styles import icons, icon_urls


class AppUser:
    def __init__(self, decoded_cookie: dict):

        self.username = decoded_cookie.get("preferred_username")
        self.full_name = decoded_cookie.get("name")
        names = self.full_name.split(" ")
        self.initials = names[0][0] + names[1][0] if len(names) > 1 else names[0][0]
        self.sub = decoded_cookie.get("sub")


class Annotation:
    def __init__(
        self,
        title,
        md_content,
        timestamp,
        user: AppUser,
        url,
        id=None,
        traces=None,
        **kwargs,
    ):
        self.title = title
        self.md_content = md_content
        self.user = user
        self.user_sub = user.sub
        self.timestamp = (
            timestamp
            if isinstance(timestamp, datetime.datetime)
            else datetime.datetime.fromisoformat(timestamp)
        )
        self.time_str = f'{self.timestamp.strftime("%d.%m.%Y %H:%M")} UTC'
        self.url = url
        self.traces = traces
        self.id = id

    def to_dict(self):
        timestamp = self.timestamp.isoformat()
        return dict(
            title=self.title,
            content=self.md_content,
            user_sub=self.user_sub,
            created_at=timestamp,
            updated_at=timestamp,
            url=self.url,
        )

    def __gt__(self, other):
        if not isinstance(other, Annotation):
            return NotImplemented
        return self.timestamp < other.timestamp


class DatasetType(str, Enum):
    meteodata = "meteodata"
    birds = "birds"
    flowers = "flowers"
    gbif_observations = "gbif"
    pollinators = "pollinators"
    pax = "pax"
    multi_pax = "multi_pax"
    location = "location"
    env_temp = "env_temp"
    env_humi = "env_humi"
    env_moist = "env_moist"


rank_hierarchy_list = [
    "KINGDOM",
    "PHYLUM",
    "CLASS",
    "ORDER",
    "FAMILY",
    "GENUS",
    "SPECIES",
]


class RankEnum(str, Enum):
    kingdom = "KINGDOM"
    phylum = "PHYLUM"
    _class = "CLASS"
    order = "ORDER"
    family = "FAMILY"
    genus = "GENUS"
    species = "SPECIES"

    def __gt__(self, other):
        if not isinstance(other, RankEnum):
            return NotImplemented
        return rank_hierarchy_list.index(self.value) < rank_hierarchy_list.index(
            other.value
        )


class Taxon:
    def __init__(
        self,
        datum_id=None,
        label_sci=None,
        label_de=None,
        label_en=None,
        image_url=None,
        rank=None,
        **kwargs,
    ):
        self.datum_id = datum_id
        self.label_de = label_de
        self.label_en = label_en
        self.label_sci = label_sci
        self.image_url = image_url
        self.rank = RankEnum(rank)
        self.type = DatasetType.birds

    def __gt__(self, other):
        if not isinstance(other, Taxon):
            return NotImplemented
        return self.rank > other.rank

    def to_dataset(self):
        return dict(
            type="birds",
            datum_id=self.datum_id,
            label_de=self.label_de,
            label_en=self.label_en,
            label_sci=self.label_sci,
            rank=self.rank.value,
            deployment_filter=[],
        )

    def get_unit(self):
        return self.rank

    def get_title(self):
        return self.label_sci

    def get_location(self):
        return "Mitwelten Deployments"

    def get_icon(self):
        return icons.hierarchy

    def get_id(self):
        return self.datum_id


class GBIFTaxon:
    def __init__(
        self,
        datum_id=None,
        label_sci=None,
        label_de=None,
        label_en=None,
        image_url=None,
        rank=None,
        lat_range=None,
        lon_range=None,
        **kwargs,
    ):
        self.datum_id = datum_id
        self.label_de = label_de
        self.label_en = label_en
        self.label_sci = label_sci
        self.image_url = image_url
        self.rank = RankEnum(rank)
        self.type = DatasetType.gbif_observations
        self.lat_range = lat_range
        self.lon_range = lon_range

    def __gt__(self, other):
        if not isinstance(other, Taxon):
            return NotImplemented
        return self.rank > other.rank

    def to_dataset(self):
        return dict(
            type="gbif",
            datum_id=self.datum_id,
            label_de=self.label_de,
            label_en=self.label_en,
            label_sci=self.label_sci,
            rank=self.rank.value,
            lat_range=self.lat_range,
            lon_range=self.lon_range,
        )

    def get_unit(self):
        return self.rank

    def get_title(self):
        return f"{self.label_sci} (GBIF)"

    def get_location(self):
        return "GBIF: Basel Area"

    def get_icon(self):
        return icon_urls.gbif

    def get_id(self):
        return self.datum_id


class MeteoDataset:
    def __init__(
        self,
        param_id=None,
        station_id=None,
        param_desc=None,
        unit=None,
        station_name=None,
        **kwargs,
    ) -> None:
        self.param_id = param_id
        self.station_id = station_id
        self.param_desc = param_desc
        self.unit = unit
        self.station_name = station_name
        self.type = DatasetType.meteodata

    def to_dataset(self):
        return dict(
            type="meteodata",
            param_id=self.param_id,
            station_id=self.station_id,
            param_desc=self.param_desc,
            unit=self.unit,
            station_name=self.station_name,
        )

    def get_unit(self):
        return self.unit

    def get_title(self):
        return self.param_desc

    def get_location(self):
        return self.station_name

    def get_icon(self):
        return icon_urls.meteoswiss

    def get_id(self):
        return self.param_id


class PaxDataset:
    def __init__(
        self,
        deployment_id=None,
        node_label=None,
        period_from=None,
        period_to=None,
        **kwargs,
    ):
        self.deployment_id = deployment_id
        self.node_label = node_label
        self.period_from = period_from
        self.period_to = period_to
        self.type = DatasetType.pax
        self.param_desc = "PAX Counter"
        self.unit = "PAX"

    def to_dataset(self):
        return dict(
            type="pax",
            deployment_id=self.deployment_id,
            node_label=self.node_label,
        )

    def get_unit(self):
        return self.unit

    def get_title(self):
        return f"{self.param_desc} {self.node_label}"

    def get_location(self):
        return f"Mitwelten Deployment {self.deployment_id}"

    def get_icon(self):
        return icons.pax_counter

    def get_id(self):
        return self.node_label

class MultiPaxDataset:
    def __init__(self, deployment_id = None, **kwargs):
        self.deployment_id = deployment_id
        self.type = DatasetType.multi_pax
        self.param_desc = "PAX Counter"
        self.unit = "PAX"
        
        
    def get_location(self):
        if isinstance(self.deployment_id, list):
            if len(self.deployment_id) == 0:
                return "Mitwelten Deployments"

            if len(self.deployment_id) == 1:
                return f"Mitwelten Deployment {self.deployment_id[0]}"
            else:
                return f"{len(self.deployment_id)} Mitwelten Deployments"
        else:
            return "Mitwelten Deployments"
    def to_dataset(self):
        return dict(
            type=self.type.value,
            deployment_id=self.deployment_id,
        )
    def get_unit(self):
        return self.unit

    def get_title(self):
        return f"{self.param_desc} (s)"

    def get_icon(self):
        return icons.pax_counter

    def get_id(self):
        return "pax"

class PollinatorClass(str, Enum):
    fliege = "fliege"
    wildbiene = "wildbiene"
    schwebfliege = "schwebfliege"
    honigbiene = "honigbiene"
    hummel = "hummel"


class PollinatorDataset:
    def __init__(self, deployment_id=None, pollinator_class=None, **kwargs):
        self.deployment_id = deployment_id
        self.pollinator_class = (
            PollinatorClass(pollinator_class) if pollinator_class is not None else None
        )
        self.type = DatasetType.pollinators
        self.param_desc = "Detected Pollinators"
        self.unit = "Pollinators"

    def to_dataset(self):
        return dict(
            type=self.type.value,
            deployment_id=self.deployment_id,
            pollinator_class=self.pollinator_class.value
            if self.pollinator_class
            else None,
        )

    def get_unit(self):
        return self.unit

    def get_title(self):
        if self.pollinator_class is None:
            return "All Pollinators"
        else:
            return self.pollinator_class.value.title()

    def get_location(self):
        if isinstance(self.deployment_id, list):
            if len(self.deployment_id) == 0:
                return "Mitwelten Deployments"

            if len(self.deployment_id) == 1:
                return f"Mitwelten Deployment {self.deployment_id[0]}"
            else:
                return f"{len(self.deployment_id)} Mitwelten Deployments"
        else:
            return "Mitwelten Deployments"

    def get_icon(self):
        return icons.bee

    def get_id(self):
        return "polli"


class EnvHumiDataset:
    def __init__(
        self,
        deployment_id=None,
        node_label=None,
        period_from=None,
        period_to=None,
        **kwargs,
    ):
        self.deployment_id = deployment_id
        self.node_label = node_label
        self.period_from = period_from
        self.period_to = period_to
        self.type = DatasetType.env_humi
        self.unit = "%"
        self.param_desc = "Relative Air Humidity"

    def to_dataset(self):
        return dict(
            type=self.type.value,
            deployment_id=self.deployment_id,
            node_label=self.node_label,
            period_from=self.period_from,
            period_to=self.period_to,
            unit=self.unit,
            param_desc=self.param_desc,
        )

    def get_unit(self):
        return self.unit

    def get_title(self):
        return self.param_desc

    def get_location(self):
        return f"Mitwelten Deployment {self.deployment_id}"

    def get_icon(self):
        return icons.env_sensors

    def get_id(self):
        return self.node_label


class EnvTempDataset:
    def __init__(
        self,
        deployment_id=None,
        node_label=None,
        period_from=None,
        period_to=None,
        **kwargs,
    ):
        self.deployment_id = deployment_id
        self.node_label = node_label
        self.period_from = period_from
        self.period_to = period_to
        self.type = DatasetType.env_temp
        self.unit = "°C"
        self.param_desc = "Air Temperature"

    def to_dataset(self):
        return dict(
            type=self.type.value,
            deployment_id=self.deployment_id,
            node_label=self.node_label,
            period_from=self.period_from,
            period_to=self.period_to,
            unit=self.unit,
            param_desc=self.param_desc,
        )

    def get_unit(self):
        return self.unit

    def get_title(self):
        return self.param_desc

    def get_location(self):
        return f"Mitwelten Deployment {self.deployment_id}"

    def get_icon(self):
        return icons.env_sensors

    def get_id(self):
        return self.node_label


class EnvMoistDataset:
    def __init__(
        self,
        deployment_id=None,
        node_label=None,
        period_from=None,
        period_to=None,
        **kwargs,
    ):
        self.deployment_id = deployment_id
        self.node_label = node_label
        self.period_from = period_from
        self.period_to = period_to
        self.type = DatasetType.env_moist
        self.unit = "AnalogValue"
        self.param_desc = "Soil Moisture"

    def to_dataset(self):
        return dict(
            type=self.type.value,
            deployment_id=self.deployment_id,
            node_label=self.node_label,
            period_from=self.period_from,
            period_to=self.period_to,
            unit=self.unit,
            param_desc=self.param_desc,
        )

    def get_unit(self):
        return self.unit

    def get_title(self):
        return self.param_desc

    def get_location(self):
        return f"Mitwelten Deployment {self.deployment_id}"

    def get_icon(self):
        return icons.env_sensors

    def get_id(self):
        return self.node_label


class ViewConfiguration:
    def __init__(
        self,
        bucket=None,
        agg=None,
        confidence=None,
        time_from=None,
        time_to=None,
        normalize=False,
        **kwargs,
    ) -> None:
        self.agg = agg
        self.bucket = bucket
        self.time_from = kwargs.get("from") if "from" in kwargs else time_from
        self.time_to = kwargs.get("to") if "to" in kwargs else time_to
        self.confidence = float(confidence) if confidence else None
        self.normalize = normalize
        if isinstance(self.time_from, str):
            self.time_from = datetime.datetime.fromisoformat(self.time_from)
        if isinstance(time_to, str):
            self.time_to = datetime.datetime.fromisoformat(self.time_to)

    def to_dict(self):
        cfg_dict = {}
        if self.confidence:
            cfg_dict["confidence"] = self.confidence
        if self.agg:
            cfg_dict["agg"] = self.agg
        if self.normalize:
            cfg_dict["normalize"] = True
        else:
            cfg_dict["normalize"] = False
        return cfg_dict


class UrlSearchArgs:
    def __init__(
        self,
        dataset=None,
        trace=None,
        datasets=None,
        cfg=None,
        bucket=None,
        agg=None,
        confidence=None,
        time_from=None,
        time_to=None,
        mw_data=None,
        gbif_data=None,
        **kwargs,
    ) -> None:
        self.dataset = dataset if dataset is not None else trace
        self.datasets = datasets
        self.agg = agg if agg else "mean"
        self.bucket = bucket if bucket else "1d"
        self.time_from = kwargs.get("from") if "from" in kwargs else time_from
        self.time_to = kwargs.get("to") if "to" in kwargs else time_to
        self.confidence = float(confidence) if confidence else 0.7
        self.mw_data = "true" in mw_data.lower() if mw_data is not None else None
        self.gbif_data = "true" in gbif_data.lower() if gbif_data is not None else None
        if isinstance(self.time_from, str):
            self.time_from = datetime.datetime.fromisoformat(self.time_from)
        if isinstance(time_to, str):
            self.time_to = datetime.datetime.fromisoformat(self.time_to)
        self.cfg = [ViewConfiguration(**c) for c in cfg] if cfg else None
        self.view_config = ViewConfiguration(
            agg=self.agg,
            confidence=self.confidence,
            bucket=self.bucket,
            time_from=self.time_from,
            time_to=self.time_to,
            **kwargs,
        )


def to_typed_dataset(dataset: dict):
    dataset_type = dataset.get("type")
    if dataset_type == DatasetType.meteodata:
        return MeteoDataset(**dataset)
    elif dataset_type == DatasetType.birds:
        return Taxon(**dataset)
    elif dataset_type == DatasetType.pax:
        return PaxDataset(**dataset)
    elif dataset_type == DatasetType.env_humi:
        return EnvHumiDataset(**dataset)
    elif dataset_type == DatasetType.env_moist:
        return EnvMoistDataset(**dataset)
    elif dataset_type == DatasetType.env_temp:
        return EnvTempDataset(**dataset)
    elif dataset_type == DatasetType.pollinators:
        return PollinatorDataset(**dataset)
    elif dataset_type == DatasetType.gbif_observations:
        return GBIFTaxon(**dataset)
    elif dataset_type == DatasetType.multi_pax:
        return MultiPaxDataset(**dataset)
    else:
        return None


def default_view_config(dataset: dict):
    dataset_type = dataset.get("type")
    if dataset_type in [
        DatasetType.birds,
        DatasetType.pollinators,
        DatasetType.flowers,
    ]:
        return dict(confidence=DEFAULT_CONFIDENCE, normalize=False)
    elif dataset_type in [
        DatasetType.meteodata,
        DatasetType.env_humi,
        DatasetType.env_moist,
        DatasetType.env_temp,
    ]:
        return dict(agg=DEFAULT_AGGREGATION, normalize=False)
    elif dataset_type == DatasetType.pax:
        return dict(normalize=False)

    else:
        return {}
