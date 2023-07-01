import dash
from dash import html, dcc, callback, Input, Output, State
from dash.exceptions import PreventUpdate
import dash_mantine_components as dmc
from dashboard.models import UrlSearchArgs, to_typed_dataset
from dashboard.styles import icons, get_icon
from dashboard.utils.communication import parse_nested_qargs, qargs_to_dict
from dashboard.utils.text_utils import format_datetime
from dashboard.api_clients.gbif_cache_client import (
    get_gbif_occurence_list,
    get_gbif_detection_count,
)
import json
from uuid import uuid4

dash.register_page(__name__, path_template="/reference/gbif")


class PageIds(object):
    url = str(uuid4())
    limit_select = str(uuid4())
    offset_select = str(uuid4())
    result_list_stack = str(uuid4())
    update_list_button = str(uuid4())


ids = PageIds()


def generate_table(occurences, limit=50, offset=0):
    children = []
    for o in occurences:
        name = o.get("label_sci")
        if name is None:
            name = dmc.Text("see occurence", color="dimmed", size="sm")
        else:
            name = dmc.Text(name, truncate=True)
        media = o.get("media")
        if media is not None:
            media = get_icon(icons.multimedia, width=22, color="gray")
        offset += 1
        index_text = dmc.Text(f"{offset}")

        children.append(
            dmc.Card(
                dmc.Grid(
                    [
                        dmc.Col(
                            dmc.Group(
                                [dmc.Group([index_text, name]), media], position="apart"
                            ),
                            span=5,
                        ),
                        dmc.Col([dmc.Text(format_datetime(o.get("time")))], span=2),
                        dmc.Col(
                            [
                                dmc.Text(
                                    o.get("datasetName"), truncate=True, size="sm"
                                ),
                            ],
                            span=4,
                        ),
                        dmc.Col(
                            dmc.Group(
                                [
                                    dmc.Anchor(
                                        get_icon(icons.open_in_new_tab),
                                        href=f"https://www.gbif.org/occurrence/{o.get('occurenceKey')}",
                                        target="_blank",
                                    )
                                ],
                                position="right",
                            ),
                            span=1,
                        ),
                    ]
                ),
                p=4,
                withBorder=True,
                radius=0,
                style={"borderTop": "0px", "borderLeft": "0px", "borderRight": "0px"},
            )
        )
    return children


list_legend = dmc.Card(
    dmc.Grid(
        [
            dmc.Col(
                dmc.Group(
                    [
                        dmc.Group(
                            [
                                dmc.Text("#", size="sm", weight=500),
                                dmc.Text("Name", size="sm", weight=500),
                            ]
                        ),
                        dmc.Text("Has Media", size="sm", weight=500),
                    ],
                    position="apart",
                ),
                span=5,
            ),
            dmc.Col([dmc.Text("Eventdate", size="sm", weight=500)], span=2),
            dmc.Col(
                [
                    dmc.Text("Dataset", size="sm", weight=500),
                ],
                span=4,
            ),
            dmc.Col(
                dmc.Group(
                    [
                        dmc.Text("Link", size="sm", weight=500),
                    ],
                    position="right",
                ),
                span=1,
            ),
        ]
    ),
    p=4,
    withBorder=True,
    radius=0,
    style={"borderTop": "0px", "borderLeft": "0px", "borderRight": "0px"},
)


def layout(**qargs):
    query_args = parse_nested_qargs(qargs)
    args = UrlSearchArgs(**query_args)
    if args.dataset is None:
        return dmc.Container(children=dmc.Text("No references found."))
    ds = to_typed_dataset(args.dataset)

    total_items = get_gbif_detection_count(
        ds.datum_id,
        args.view_config.time_from,
        args.view_config.time_to,
    )
    if total_items is not None:
        return dmc.Container(
            children=[
                dcc.Location(id=ids.url, refresh=False),
                dmc.Group(
                    [
                        dmc.Text("Occurence List", weight=500, size="lg"),
                        dmc.Text(f"{total_items} total occurences"),
                        dmc.Group(
                            [
                                dmc.Group(
                                    [
                                        dmc.Text(
                                            "Offset",
                                        ),
                                        dmc.NumberInput(
                                            value=0,
                                            min=0,
                                            step=50,
                                            max=total_items - 1,
                                            id=ids.offset_select,
                                            size="sm",
                                            debounce=400,
                                            error=None,
                                        ),
                                    ],
                                    spacing="xs",
                                ),
                                dmc.Group(
                                    [
                                        dmc.Text("Limit"),
                                        dmc.Select(
                                            data=[
                                                {"value": n, "label": f"{n}"}
                                                for n in [20, 50, 100, 200]
                                            ],
                                            value=50,
                                            id=ids.limit_select,
                                            size="sm",
                                            w=90,
                                        ),
                                    ],
                                    spacing="xs",
                                ),
                                dmc.Button(
                                    "Go",
                                    color="indigo",
                                    variant="outline",
                                    id=ids.update_list_button,
                                ),
                            ],
                            spacing="lg",
                        ),
                    ],
                    position="apart",
                ),
                dmc.Space(h=12),
                dmc.Stack(
                    [
                        list_legend,
                        dmc.LoadingOverlay(
                            dmc.Stack(spacing=2, id=ids.result_list_stack),
                        ),
                    ]
                ),
                dmc.Space(h=20),
            ],
            className="container-xl",
        )


@callback(
    Output(ids.result_list_stack, "children"),
    Input(ids.url, "pathname"),
    Input(ids.url, "search"),
    Input(ids.update_list_button, "n_clicks"),
    State(ids.offset_select, "value"),
    State(ids.limit_select, "value"),
)
def update_list(pn, search, nc, offset, limit):
    if not "reference/gbif" in pn:
        raise PreventUpdate
    args = UrlSearchArgs(**parse_nested_qargs(qargs_to_dict(search)))
    if args is not None:
        ds = to_typed_dataset(args.dataset)
        offset = 0 if offset is None else offset
        occ = get_gbif_occurence_list(
            ds.datum_id,
            args.view_config.time_from,
            args.view_config.time_to,
            limit=limit,
            offset=offset,
        )
        if occ is not None:
            return generate_table(occ, limit=limit, offset=offset)
    raise PreventUpdate
