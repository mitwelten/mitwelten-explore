import dash_mantine_components as dmc
from configuration import PATH_PREFIX
from dashboard.utils.communication import urlencode_dict
from dashboard.styles import icons, get_icon
from dashboard.models import (
    DatasetType,
    PollinatorDataset,
    to_typed_dataset,
    default_view_config,
    Deployment,
)
from dashboard.components.overlays import tooltip
from dashboard.components.dataset_presentation import deployment_info_spoiler
from dashboard.api_clients.deployments_client import get_deployments
import json


def generate_selected_data_list(store_data):
    if store_data is None:
        return []

    list_entries = []
    for i in range(len(store_data)):
        ds = to_typed_dataset(store_data[i])
        dashboard_buttons = []
        if ds.type in [
            DatasetType.birds,
            DatasetType.gbif_observations,
            DatasetType.distinct_species,
        ]:

            dashboard_buttons.append(
                tooltip(
                    dmc.Anchor(
                        dmc.Button(
                            get_icon(icon=icons.map_chart, width=24),
                            # "Map",
                            color="cyan.6",
                            variant="outline",
                            # leftIcon=get_icon(icon=icons.map_chart, width=24),
                        ),
                        href=f"{PATH_PREFIX}viz/map?{urlencode_dict(dict(datasets=[ds.to_dataset()],cfg=[default_view_config(ds.to_dataset())]))}",
                    ),
                    "Map Dashboard",
                    color="cyan.6",
                )
            )
        if ds.type in [DatasetType.distinct_species, DatasetType.pollinators]:
            dashboard_buttons.append(
                tooltip(
                    dmc.Anchor(
                        dmc.Button(
                            get_icon(icon=icons.location_poi, width=24),
                            # "Deployment",
                            color="grape.6",
                            variant="outline",
                            # leftIcon=get_icon(icon=icons.location_poi, width=24),
                        ),
                        href=f"{PATH_PREFIX}viz/deployment?{urlencode_dict(dict(dataset=ds.to_dataset()))}",
                    ),
                    "Deployment Dashboard",
                    color="grape.6",
                )
            )

        if ds.type == DatasetType.birds:
            dashboard_buttons.append(
                tooltip(
                    dmc.Anchor(
                        dmc.Button(
                            get_icon(icon=icons.dashboard, width=24),
                            # "Taxon Dashboard",
                            color="teal.6",
                            variant="outline",
                            # leftIcon=get_icon(icon=icons.dashboard, width=24),
                        ),
                        href=f"{PATH_PREFIX}viz/taxon/{ds.datum_id}?mw_data=true",
                    ),
                    "Taxon Dashboard",
                    color="teal.6",
                )
            )

        if ds.type == DatasetType.gbif_observations:
            dashboard_buttons.append(
                tooltip(
                    dmc.Anchor(
                        dmc.Button(
                            get_icon(icon=icons.dashboard, width=24),
                            # "Taxon Dashboard",
                            color="teal.6",
                            variant="outline",
                            # leftIcon=get_icon(icon=icons.dashboard, width=24),
                        ),
                        href=f"{PATH_PREFIX}viz/taxon/{ds.datum_id}?gbif_data=true",
                    ),
                    "Taxon Dashboard",
                    color="teal.6",
                )
            )
        if ds.type in [
            DatasetType.birds,
            DatasetType.env_humi,
            DatasetType.env_moist,
            DatasetType.env_temp,
            DatasetType.meteodata,
            DatasetType.pollinators,
            DatasetType.pax,
            DatasetType.gbif_observations,
            DatasetType.distinct_species,
        ]:
            dashboard_buttons.append(
                tooltip(
                    dmc.Anchor(
                        dmc.Button(
                            get_icon(icon=icons.line_chart, width=24),
                            # "Time Series Dashboard",
                            color="indigo.6",
                            variant="outline",
                            # leftIcon=get_icon(icon=icons.line_chart, width=24),
                        ),
                        href=f"{PATH_PREFIX}viz/timeseries?{urlencode_dict(dict(trace=ds.to_dataset()))}",
                        target="_blank",
                    ),
                    "Time Series Dashboard",
                    color="indigo.6",
                )
            )
        location_information = dmc.Group(
            [
                get_icon(icon=icons.location_marker),
                dmc.Text(ds.get_location(), size="md"),
            ],
            spacing=2,
        )
        if ds.type in [
            DatasetType.distinct_species,
            DatasetType.pollinators,
            DatasetType.pax,
            DatasetType.multi_pax,
            DatasetType.env_humi,
            DatasetType.env_moist,
            DatasetType.env_temp,
        ]:
            if ds.deployment_id is not None:
                location_information = deployment_info_spoiler(
                    ds.deployment_id, location_information
                )

        list_entries.append(
            dmc.Card(
                dmc.Grid(
                    [
                        dmc.Col(
                            dmc.Stack(
                                [
                                    get_icon(icon=ds.get_icon(), width=32),
                                    dmc.Text(ds.get_id(), color="dimmed", size="sm"),
                                ],
                                spacing=4,
                            ),
                            span=1,
                        ),
                        dmc.Col(
                            [
                                dmc.Stack(
                                    [
                                        dmc.Group(
                                            [
                                                dmc.Text(
                                                    ds.get_title(),
                                                    weight=500,
                                                    size="lg",
                                                ),
                                                dmc.Badge(
                                                    ds.get_unit(),
                                                    variant="outline",
                                                    color="teal",
                                                ),
                                            ]
                                        ),
                                        location_information,
                                    ],
                                    spacing=4,
                                ),
                            ],
                            span=6,
                        ),
                        dmc.Col(
                            [
                                dmc.Group(
                                    dashboard_buttons
                                    + [
                                        tooltip(
                                            dmc.Button(
                                                get_icon(icon=icons.trash, width=24),
                                                color="red",
                                                px=4,
                                                id={
                                                    "role": "remove_from_collection_btn",
                                                    "index": json.dumps(
                                                        ds.to_dataset()
                                                    ),
                                                },
                                            ),
                                            "Remove this dataset from your collection",
                                            color="red.9",
                                        ),
                                    ],
                                    pr=12,
                                )
                            ],
                            span=5,
                            className="d-flex justify-content-end",
                        ),
                    ],
                ),
                withBorder=True,
                radius=0,
                px=6,
                py=4,
                style={
                    "borderTop": "0px",
                    "borderLeft": "0px",
                    "borderRight": "0px",
                },
            )
        )

    return list_entries
