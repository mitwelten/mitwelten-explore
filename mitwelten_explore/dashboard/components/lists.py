import dash_mantine_components as dmc
from dash_iconify import DashIconify
from configuration import PATH_PREFIX
from dashboard.utils.communication import urlencode_dict
from dashboard.styles import icons
from dashboard.models import DatasetType, PollinatorDataset, to_typed_dataset



def generate_selected_data_list(store_data):
    if store_data is None:
        return []

    list_entries = []
    for i in range(len(store_data)):
        data = store_data[i]
        ds = to_typed_dataset(data)
        trace_type = data.get("type")
        trace_id = None
        icon = None
        description = None
        location_name = None
        single_viz_url = None
        taxon_dashboard_button = None
        if ds.type == DatasetType.meteodata:
            trace_id = dmc.Text(data.get("param_id"), weight=600)
            icon = DashIconify(icon=icons.meteoswiss, width=32)
            description = dmc.Group(
                [
                    dmc.Text(data.get("param_desc"), size="md"),
                    dmc.Badge(data.get("unit"), color="teal"),
                ]
            )
            location_name = dmc.Text(data.get("station_name"), size="sm")

        elif ds.type == DatasetType.birds:
            trace_id = dmc.Text(data.get("datum_id"), weight=600)
            icon = DashIconify(icon="game-icons:seagull", width=32)
            description = dmc.Group(
                [
                    dmc.Text(data.get("label_sci"), size="md"),
                    dmc.Badge(data.get("rank"), color="teal"),
                ]
            )
            location_name = dmc.Text("Mitwelten Deployments", size="sm")
            taxon_dashboard_button = dmc.Anchor(
                dmc.Button(
                    "Taxon Dashboard",
                    color="teal.6",
                    variant="outline",
                    leftIcon=DashIconify(icon="ic:outline-space-dashboard", width=24),
                ),
                href=f"{PATH_PREFIX}viz/taxon/{data.get('datum_id')}",
            )
        elif ds.type == DatasetType.pax:
            trace_id = dmc.Text(data.get("node_label"), weight=600)
            icon = DashIconify(icon=icons.pax_counter, width=32)
            description = dmc.Group(
                [
                    dmc.Text("Pax Counter", size="md"),
                    dmc.Badge("PAX", color="teal"),
                ]
            )
            location_name = dmc.Text(f'mw-deployment #{data.get("deployment_id")}', size="sm")
        elif ds.type in [DatasetType.env_temp , DatasetType.env_humi , DatasetType.env_moist]:
            trace_id = dmc.Text(data.get("node_label"), weight=600)
            icon = DashIconify(icon=icons.env_sensors, width=32)
            description = dmc.Group(
                [
                    dmc.Text(trace_type, size="md"),
                    dmc.Badge(data.get("unit"), color="teal"),
                ]
            )
            location_name = dmc.Text(f'mw-deployment #{data.get("deployment_id")}', size="sm")
        elif ds.type == DatasetType.pollinators:
            ds = PollinatorDataset(**data)
            trace_id = dmc.Text(ds.get_unit(), weight=600)
            icon = DashIconify(icon=icons.bee, width=32)
            description = dmc.Group(
                [
                    dmc.Text(ds.get_title(), size="md"),
                    dmc.Badge(ds.get_unit(), color="teal"),
                ]
            )
            location_name = dmc.Text(ds.get_location(), size="sm")
            
        
        single_viz_url = (
            f"{PATH_PREFIX}viz/timeseries?{urlencode_dict(dict(trace=data))}"
        )

        list_entries.append(
            dmc.Card(
                dmc.Grid(
                    [
                        dmc.Col(
                            [icon, trace_id],
                            span=2,
                        ),
                        dmc.Col(
                            [
                                description,
                                dmc.Group(
                                    [
                                        DashIconify(
                                            icon="material-symbols:location-on-outline"
                                        ),
                                        location_name,
                                    ]
                                ),
                            ],
                            span=6,
                        ),
                        dmc.Col(
                            [
                                dmc.Group(
                                    [
                                        taxon_dashboard_button,
                                        dmc.Anchor(
                                            dmc.Button(
                                                "Explore Time Series",
                                                color="indigo.6",
                                                variant="outline",
                                                leftIcon=DashIconify(
                                                    icon="ph:chart-scatter", width=24
                                                ),
                                            ),
                                            href=single_viz_url,
                                            target="_blank",
                                        ),
                                        dmc.Button(
                                            "Remove",
                                            leftIcon=DashIconify(
                                                icon="mdi:trash-can-outline", width=24
                                            ),
                                            color="red",
                                            id={
                                                "role": "remove_from_collection_btn",
                                                "index": i,
                                            },
                                        ),
                                    ]
                                )
                            ],
                            span=4,
                            className="d-flex justify-content-end",
                        ),
                    ],
                ),
                withBorder=True,
            )
        )

    return list_entries
