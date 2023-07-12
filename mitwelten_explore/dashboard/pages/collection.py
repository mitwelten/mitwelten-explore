import dash
from dash import html, dcc, callback, Input, Output, no_update, State, ALL, ctx
import flask
from dash.exceptions import PreventUpdate
import dash_mantine_components as dmc
import json
from dashboard.aio_components.aio_list_component import (
    PagedListAIO,
    PagedListSearchableAIO,
)
from dashboard.components.lists import generate_selected_data_list
from dashboard.components.notifications import generate_notification
from dashboard.styles import get_icon, icons
from configuration import PATH_PREFIX

dash.register_page(
    __name__,
)
list_legend = dmc.Card(
    [
        dmc.Grid(
            [
                dmc.Col(dmc.Text("Type", size="sm", weight=500), span=1),
                dmc.Col(
                    dmc.Text("Name  Unit  Location", size="sm", weight=500), span=5
                ),
                dmc.Col(
                    dmc.Group(
                        [
                            dmc.Group(
                                [
                                    get_icon(
                                        icon=icons.location_poi,
                                        width=20,
                                        color=dmc.theme.DEFAULT_COLORS["grape"][6],
                                    ),
                                    dmc.Text(
                                        "Deployment Dashboard",
                                        color="grape.6",
                                        size="sm",
                                        weight=500,
                                    ),
                                ],
                                spacing=3,
                            ),
                            dmc.Group(
                                [
                                    get_icon(
                                        icon=icons.map_chart,
                                        width=20,
                                        color=dmc.theme.DEFAULT_COLORS["cyan"][6],
                                    ),
                                    dmc.Text(
                                        "Map Dashboard",
                                        color="cyan.6",
                                        size="sm",
                                        weight=500,
                                    ),
                                ],
                                spacing=3,
                            ),
                            dmc.Group(
                                [
                                    get_icon(
                                        icon=icons.dashboard,
                                        width=20,
                                        color=dmc.theme.DEFAULT_COLORS["teal"][6],
                                    ),
                                    dmc.Text(
                                        "Taxon Dashboard",
                                        color="teal.6",
                                        size="sm",
                                        weight=500,
                                    ),
                                ],
                                spacing=3,
                            ),
                            dmc.Group(
                                [
                                    get_icon(
                                        icon=icons.line_chart,
                                        width=20,
                                        color=dmc.theme.DEFAULT_COLORS["indigo"][6],
                                    ),
                                    dmc.Text(
                                        "Time Series Dashboard",
                                        color="indigo.6",
                                        size="sm",
                                        weight=500,
                                    ),
                                ],
                                spacing=3,
                            ),
                        ],
                        position="right",
                    ),
                    span=6,
                ),
            ]
        )
    ],
    px=0,
    pt=4,
    pb=12,
)

list_skeleton = dmc.Skeleton(width="100%", height=60)

plaio = PagedListSearchableAIO(
    items=[list_skeleton, dmc.Divider()] * 10, legend=list_legend
)


def layout(**qargs):
    return dmc.Container(
        [
            dmc.Group(
                [
                    dmc.Text("Collected Datasets", weight=600, size="lg"),
                    dmc.Anchor(
                        get_icon(icons.help, width=18),
                        href=f"{PATH_PREFIX}docs#collection",
                        variant="text",
                        target="_blank",
                    ),
                ],
                align="top",
            ),
            dmc.Space(h=8),
            plaio,
        ],
        fluid=True,
    )


@callback(Output(plaio.ids.store(plaio.aio_id), "data"), Input("traces_store", "data"))
def update_sel_tr(data):
    if data is not None:
        return generate_selected_data_list(data)
    raise PreventUpdate


@callback(
    Output("traces_store", "data", allow_duplicate=True),
    Output("noti_container", "children", allow_duplicate=True),
    Input({"role": "remove_from_collection_btn", "index": ALL}, "n_clicks"),
    State("traces_store", "data"),
    prevent_initial_call=True,
)
def remove_trace(buttons, data):
    if not any(buttons):
        raise PreventUpdate
    trg = ctx.triggered_id
    index_to_remove = trg.get("index")
    if index_to_remove is not None:
        ds_to_remove = json.loads(index_to_remove)
        if ds_to_remove in data:
            data.remove(ds_to_remove)

            return data, generate_notification(
                title="Item removed from collection",
                message="the dataset was removed from your collection",
                color="indigo",
                icon="mdi:trash-can-outline",
            )
    raise PreventUpdate
