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
        ds = to_typed_dataset(store_data[i])
        dashboard_buttons = []
        if ds.type == DatasetType.birds:
            dashboard_buttons.append(
                dmc.Anchor(
                    dmc.Button(
                        "Taxon Dashboard",
                        color="teal.6",
                        variant="outline",
                        leftIcon=DashIconify(icon=icons.dashboard, width=24),
                    ),
                    href=f"{PATH_PREFIX}viz/taxon/{ds.datum_id}",
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
        ]:
            dashboard_buttons.append(
                dmc.Anchor(
                    dmc.Button(
                        "Time Series Dashboard",
                        color="indigo.6",
                        variant="outline",
                        leftIcon=DashIconify(icon=icons.line_chart, width=24),
                    ),
                    href=f"{PATH_PREFIX}viz/timeseries?{urlencode_dict(dict(trace=ds.to_dataset()))}",
                    target="_blank",
                )
            )

        list_entries.append(
            dmc.Card(
                dmc.Grid(
                    [
                        dmc.Col(
                            dmc.Stack(
                                [
                                    DashIconify(icon=ds.get_icon(), width=32),
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
                                        dmc.Group(
                                            [
                                                DashIconify(icon=icons.location_marker),
                                                dmc.Text(ds.get_location(), size="md"),
                                            ],
                                            spacing=2,
                                        ),
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
                                        dmc.Button(
                                            DashIconify(icon=icons.trash, width=24),
                                            color="red",
                                            px=4,
                                            id={
                                                "role": "remove_from_collection_btn",
                                                "index": i,
                                            },
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
                withBorder=False,
                radius=0,
                px=6,
                style={"borderBottom": "1px solid gray"},
            )
        )

    return list_entries
