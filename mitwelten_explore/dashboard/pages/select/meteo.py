import dash
from dash import dcc, callback, Input, Output, State, ctx, no_update, ALL
from dash.exceptions import PreventUpdate
import dash_mantine_components as dmc
from dashboard.styles import get_icon, icons
from dashboard.aio_components.aio_list_component import PagedListSearchableAIO
from dashboard.data_handler import (
    get_meteo_stations,
    get_meteo_parameters,
    get_meteo_datasets,
)
from dashboard.charts.map_charts import generate_scatter_map_plot
from dashboard.utils.communication import urlencode_dict
from dashboard.utils.text_utils import format_datetime
from dashboard.components.overlays import tooltip
from dashboard.models import MeteoDataset
from configuration import PATH_PREFIX
import json
from uuid import uuid4

dash.register_page(
    __name__,
)


class PageIds(object):
    meteo_stn_select = str(uuid4())
    meteo_unit_select = str(uuid4())
    map = str(uuid4())
    select_btn_role = str(uuid4())


ids = PageIds()


def get_station_select_data():
    stations = get_meteo_stations()
    data = []
    for stn in stations:
        data.append({"value": stn.get("station_id"), "label": stn.get("station_name")})
    return data


def get_unit_select_data():
    unit_options = list(set([p.get("unit") for p in get_meteo_parameters()]))
    unit_options.sort()
    return [{"value": u, "label": u} for u in unit_options]


def generate_station_map_plot(selected=None):
    stations = get_meteo_stations()
    names = []
    ids = []
    lats = []
    lons = []
    for stn in stations:
        lats.append(stn.get("location").get("lat"))
        lons.append(stn.get("location").get("lon"))
        names.append(stn.get("station_name"))
        ids.append(stn.get("station_id"))
    return generate_scatter_map_plot(lats, lons, names, ids, selected)


def get_dataset_list(station_id=None, unit=None):
    parameters = get_meteo_datasets(station_id=station_id, unit=unit)
    idx_stn_id = "not_defined" if not station_id else station_id

    list_entries = []
    for i in range(len(parameters)):

        param = parameters[i]
        trace_dict = MeteoDataset(
            param_id=param.get("param_id"),
            station_id=param.get("station_id"),
            param_desc=param.get("description"),
            unit=param.get("unit"),
            station_name=param.get("station_name"),
        ).to_dataset()
        last_measurement = param.get("last_measurement")
        last_measurement_str = format_datetime(last_measurement)
        single_viz_url = (
            f"{PATH_PREFIX}viz/timeseries?{urlencode_dict(dict(trace=trace_dict))}"
        )
        stn_badge = dmc.Group(
            [
                get_icon(icon=icons.location_marker),
                dmc.Text(param.get("station_name"), size="md"),
            ],
            spacing=0,
        )
        list_entries.append(
            dmc.Card(
                dmc.Grid(
                    [
                        dmc.Col(
                            # get_icon(icon="arcticons:meteoswiss", width=32),
                            dmc.Group(
                                [
                                    dmc.Text(
                                        param.get("description"),
                                        size="md",
                                        weight=500,
                                    ),
                                    dmc.Badge(
                                        param.get("unit"),
                                        color="indigo",
                                        variant="outline",
                                    ),
                                    stn_badge,
                                    dmc.Text(
                                        param.get("param_id"), size="xs", color="dimmed"
                                    ),
                                    dmc.Text(
                                        f"Last Datapoint: {last_measurement_str}",
                                        size="xs",
                                        color="dimmed",
                                    ),
                                ],
                                style={"rowGap": "4px"},
                            ),
                            className="col-lg-9",
                        ),
                        dmc.Col(
                            [
                                dmc.Group(
                                    [
                                        tooltip(
                                            dmc.Anchor(
                                                dmc.Button(
                                                    "Viz",
                                                    leftIcon=get_icon(
                                                        icon=icons.line_chart, width=20
                                                    ),
                                                    color="indigo.6",
                                                    variant="outline",
                                                ),
                                                href=single_viz_url,
                                                target="_blank",
                                            ),
                                            "Explore this dataset",
                                        ),
                                        tooltip(
                                            dmc.Button(
                                                get_icon(
                                                    icon=icons.bookmark,
                                                    width=20,
                                                ),
                                                color="indigo.6",
                                                variant="subtle",
                                                px=4,
                                                id={
                                                    "role": ids.select_btn_role,
                                                    "index": json.dumps(trace_dict),
                                                },
                                            ),
                                            "Add dataset to your collection",
                                        ),
                                    ],
                                    spacing="xs",
                                )
                            ],
                            className="col-xl-3 d-flex justify-content-end align-items-center",
                        ),
                    ],
                ),
                withBorder=True,
                py=4,
            )
        )

    return list_entries


listitem_skeleton = dmc.Card(
    dmc.Grid(
        [
            dmc.Col(
                [
                    dmc.Skeleton(
                        width="100%",
                        height=18,
                    ),
                    dmc.Space(h=4),
                    dmc.Skeleton(width="35%", height=11),
                ],
                span=11,
            ),
            dmc.Col(dmc.Skeleton(width="100%", height=32), span=1),
        ],
    ),
    withBorder=True,
    radius=0,
    style=dict(borderBottom="0px", borderLeft="0px", borderRight="0px"),
    py=6,
)

plaio_meteo = PagedListSearchableAIO(
    height="90vh",
    items_per_page=30,
    use_loadingoverlay=False,
    items=[listitem_skeleton] * 10,  # get_dataset_list(),
)


def layout(**qargs):
    return dmc.Container(
        [
            dmc.Grid(
                [
                    dmc.Col(
                        children=[
                            dmc.Text("Meteo Datasets", weight=700, size="lg"),
                            dmc.Space(h=12),
                            dmc.Grid(
                                [
                                    dmc.Col(
                                        dmc.Select(
                                            id=ids.meteo_stn_select,
                                            label="Meteo Station",
                                            data=get_station_select_data(),
                                            searchable=True,
                                            clearable=True,
                                            icon=get_icon(icon=icons.location_marker),
                                            placeholder="Station",
                                        ),
                                        className="col-sm-6",
                                    ),
                                    dmc.Col(
                                        dmc.Select(
                                            data=get_unit_select_data(),
                                            searchable=True,
                                            clearable=True,
                                            placeholder="Unit",
                                            label="Unit",
                                            id=ids.meteo_unit_select,
                                        ),
                                        className="col-sm-6",
                                    ),
                                ]
                            ),
                            dmc.Space(h=20),
                            dmc.Accordion(
                                [
                                    dmc.AccordionItem(
                                        [
                                            dmc.AccordionControl(
                                                dmc.Text("Map", weight=500, size="sm"),
                                                pl=0,
                                                pb=8,
                                                pt=4,
                                            ),
                                            dmc.AccordionPanel(
                                                dcc.Graph(
                                                    figure=generate_station_map_plot(),
                                                    id=ids.map,
                                                    config=dict(
                                                        displayModeBar=True,
                                                        # scrollZoom=False,
                                                        modeBarButtonsToRemove=[
                                                            "pan",
                                                            "select",
                                                            "toImage",
                                                            "lasso",
                                                        ],
                                                        displaylogo=False,
                                                    ),
                                                ),
                                            ),
                                        ],
                                        value="meteo_map_acc",
                                    )
                                ],
                                variant="default",
                                value="meteo_map_acc",
                            ),
                        ],
                        # span=4,
                        className="col-lg-5",
                    ),
                    dmc.Col(
                        [
                            dmc.Space(h=12),
                            dmc.LoadingOverlay(
                                plaio_meteo, transitionDuration=200, overlayOpacity=0
                            ),
                        ],
                        className="col-lg-7",
                    ),
                ]
            ),
        ],
        fluid=True,
    )


@callback(
    Output(ids.meteo_stn_select, "value"),
    Input(ids.map, "clickData"),
)
def show_clicked(cd):
    if cd is not None:
        if "points" in cd:
            points = cd.get("points")
            if isinstance(points, list):
                point = points[0]
                station_id = point.get("customdata")
                if station_id is not None:
                    return station_id
    raise PreventUpdate


@callback(
    Output(ids.map, "figure"),
    Input(ids.meteo_stn_select, "value"),
)
def highlight_selected(value):
    if value is not None:
        return generate_station_map_plot(value)
    return generate_station_map_plot()


@callback(
    Output(plaio_meteo.ids.store(plaio_meteo.aio_id), "data"),
    Input(ids.meteo_stn_select, "value"),
    Input(ids.meteo_unit_select, "value"),
)
def update_dataset_list(stn, unit):
    return get_dataset_list(station_id=stn, unit=unit)


@callback(
    Output("trace_add_store", "data", allow_duplicate=True),
    Input({"role": ids.select_btn_role, "index": ALL}, "n_clicks"),
    State("trace_add_store", "data"),
    prevent_initial_call=True,
)
def add_dataset(buttons, collection):
    if not any(buttons):
        raise PreventUpdate
    if collection is None:
        collection = []
    trg = ctx.triggered_id
    try:
        collection_str = trg.get("index")
        trace = json.loads(collection_str)
        if not trace in collection:
            collection.append(trace)
            return collection
        raise PreventUpdate
    except:
        print("failed to load!")
        return no_update

    raise PreventUpdate
