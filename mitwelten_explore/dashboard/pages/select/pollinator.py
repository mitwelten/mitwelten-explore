import dash
from dash import callback, Input, Output, State, no_update, ctx, ALL, html, dcc
from dash.exceptions import PreventUpdate
import dash_mantine_components as dmc
from uuid import uuid4
import json
from dashboard.styles import icons, get_icon
from dashboard.aio_components.aio_list_component import PagedListSearchableAIO
from dashboard.components.dataset_presentation import pollinator_dataset_card
from dashboard.api_clients.deployments_client import get_deployments
from dashboard.charts.map_charts import generate_scatter_map_plot

dash.register_page(__name__, path="/select/pollinator")


class PageIds(object):
    deployment_select = str(uuid4())
    map = str(uuid4())
    add_trace = str(uuid4())
    plaio_id = str(uuid4())
    polli_class_select = str(uuid4())
    dataset_card_div = str(uuid4())
    add_dataset_role = str(uuid4())


ids = PageIds()


def get_deployment_select_data():
    deployments = get_deployments(type_query="pollinator")
    return [
        {
            "value": d.get("deployment_id"),
            "label": f"deployment-{d.get('deployment_id')}",
        }
        for d in deployments
    ]


def generate_station_map_plot(selected=None):
    deployments = get_deployments(type_query="pollinator")
    names = []
    ids = []
    lats = []
    lons = []
    for d in deployments:
        lats.append(d.get("location").get("lat"))
        lons.append(d.get("location").get("lon"))
        names.append(f"{d.get('deployment_id')} ({d.get('node').get('node_label')})")
        ids.append(d.get("deployment_id"))
    return generate_scatter_map_plot(lats, lons, names, ids, selected)


def layout(**qargs):
    return dmc.Container(
        [
            dmc.Grid(
                [
                    dmc.Col(
                        children=[
                            dmc.Text("Pollinator Datasets", weight=700, size="lg"),
                            dmc.Space(h=12),
                            dmc.MultiSelect(
                                id=ids.deployment_select,
                                label="Deployment",
                                data=get_deployment_select_data(),
                                searchable=True,
                                clearable=True,
                                icon=get_icon(icon=icons.location_marker),
                                placeholder="Deployment",
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
                                                            # "select",
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
                            dmc.Space(h=12),
                            dmc.Select(
                                id=ids.polli_class_select,
                                label="Pollinator Class",
                                data=[
                                    {"label": p.title(), "value": p}
                                    for p in [
                                        "fliege",
                                        "wildbiene",
                                        "schwebfliege",
                                        "honigbiene",
                                        "hummel",
                                    ]
                                ],
                                searchable=True,
                                clearable=True,
                                icon=get_icon(icon=icons.bee),
                                placeholder="Include All",
                            ),
                        ],
                        # span=4,
                        className="col-lg-5",
                    ),
                    dmc.Col(
                        [dmc.Space(h=12), html.Div(id=ids.dataset_card_div)],
                        className="col-lg-7",
                    ),
                ]
            ),
        ],
        fluid=True,
    )


@callback(
    Output(ids.deployment_select, "value"),
    Input(ids.map, "selectedData"),
    State(ids.deployment_select, "value"),
)
def show_clicked(select_event, selected):
    if select_event is not None:
        if "points" in select_event:
            points = select_event.get("points")
            if selected is None:
                selected = []
            if isinstance(points, list):
                deployment_ids = [point.get("customdata") for point in points]
                for deployment_id in list(set(deployment_ids)):
                    if deployment_id is not None:
                        if not deployment_id in selected:
                            selected.append(deployment_id)
                        else:
                            selected.remove(deployment_id)
            return selected
    raise PreventUpdate


@callback(
    Output(ids.map, "figure"),
    Input(ids.deployment_select, "value"),
)
def highlight_selected(value):
    if value is not None:
        return generate_station_map_plot(value)
    return generate_station_map_plot()


@callback(
    Output(ids.dataset_card_div, "children"),
    Input(ids.deployment_select, "value"),
    Input(ids.polli_class_select, "value"),
)
def update_ds_card(deployments, polli_class):
    return pollinator_dataset_card(
        id_role=ids.add_trace, deployment_ids=deployments, pollinator_class=polli_class
    )


@callback(
    Output("trace_add_store", "data", allow_duplicate=True),
    Input({"role": ids.add_trace, "index": ALL}, "n_clicks"),
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
            return collection  # , generate_notification(title="Added to collection",message="the selected dataset was added to your collection",color="green",icon="material-symbols:check-circle-outline")
        raise PreventUpdate
    except:
        return no_update  # , generate_notification(title="Already in collection",message="the selected dataset is already stored in your collection",color="orange",icon="mdi:information-outline")
