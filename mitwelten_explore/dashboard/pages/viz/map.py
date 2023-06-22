import dash
from dash import dcc, callback, Input, Output, State, ctx, html, no_update, ALL
from dash.exceptions import PreventUpdate
import flask
import dash_mantine_components as dmc
from dashboard.aio_components.aio_hexbinmap_component import (
    H3HexBinMapMultiAIO,
    LocationData,
)
from dashboard.aio_components.aio_texteditor_component import TextEditorAIO

from dashboard.aio_components.aio_time_range_picker_component import TimeRangeAIO
from dashboard.components.modals import (
    viz_compare_select_modal,
    generate_viz_map_select_modal_children,
    dataset_config_modal,
    share_modal,
)
from dashboard.components.affix import affix_menu, affix_button

from dashboard.components.cards import dataset_info_card
from dashboard.data_handler import load_map_data
from dashboard.models import (
    UrlSearchArgs,
    to_typed_dataset,
    default_view_config,
    DatasetType,
    Annotation,
)
from dashboard.utils.communication import (
    parse_nested_qargs,
    qargs_to_dict,
    urlencode_dict,
    get_user_from_cookies,
)
from dashboard.utils.geo_utils import validate_coordinates
from dashboard.api_clients.bird_results_client import get_detection_locations
from dashboard.api_clients.sensordata_client import get_pax_locations
from dashboard.api_clients.pollinator_results_client import (
    POLLINATOR_IDS,
    get_polli_detection_locations_by_id,
)
from dashboard.api_clients.gbif_cache_client import get_gbif_detection_locations
from dashboard.api_clients.userdata_client import post_annotation
from dashboard.styles import (
    icons,
    get_icon,
    SEQUENTIAL_COLORSCALES,
    MULTI_VIZ_COLORSCALE,
    MULTI_VIZ_COLORSCALE_MT,
)
from uuid import uuid4
import json
import datetime
from configuration import PATH_PREFIX, DEFAULT_TR_START


class PageIds(object):
    url = str(uuid4())
    ds1_visible = str(uuid4())
    ds2_visible = str(uuid4())
    ds_visible_role = str(uuid4())
    select_modal = str(uuid4())
    modal_select_checkbox_role = str(uuid4())
    apply_selection_btn = str(uuid4())
    dataset_card_stack = str(uuid4())
    dataset_config_role = str(uuid4())
    config_modal_div = str(uuid4())
    config_modal = str(uuid4())
    apply_config_role = str(uuid4())
    confidence_select = str(uuid4())
    agg_select = str(uuid4())
    switch_datasets = str(uuid4())
    share_modal_div = str(uuid4())
    play_switch = str(uuid4())
    show_scatter = str(uuid4())
    affix_share = str(uuid4())
    colorscale_slider_1 = str(uuid4())
    colorscale_slider_2 = str(uuid4())
    map_config_stack = str(uuid4())
    map_type_control = str(uuid4())


ids = PageIds()


def resp_to_locationdata(resp, name=None):
    lat = []
    lon = []
    values = []
    ids = []
    for r in resp:
        latitude = r.get("location").get("lat")
        longitude = r.get("location").get("lon")
        if validate_coordinates(latitude, longitude):
            lat.append(latitude)
            lon.append(longitude)
            if "detections" in r:
                values.append(r.get("detections"))
            elif "pax" in r:
                values.append(r.get("pax"))
            try:
                ids.append(r.get("deployment_id"))
            except:
                ids.append(str(uuid4()))
    return LocationData(lat=lat, lon=lon, ids=ids, values=values, name=name)


def add_datapoints_to_locationdata(data: LocationData, resp):
    for r in resp:
        latitude = r.get("location").get("lat")
        longitude = r.get("location").get("lon")
        if validate_coordinates(latitude, longitude):
            value = None
            if "detections" in r:
                value = r.get("detections")
            elif "pax" in r:
                value = r.get("pax")
            try:
                id = r.get("deployment_id")
            except:
                id = str(uuid4())
            if value is not None:
                data.add_datapoint(lat=latitude, lon=longitude, value=value, id=id)


dash.register_page(__name__, path_template="/viz/map")

annot_editor = TextEditorAIO()
traio = TimeRangeAIO(dates=[None, None])


multihexmap = H3HexBinMapMultiAIO(
    graph_props=dict(
        config=dict(fillFrame=False, displayModeBar=False),
        responsive=True,
        style=dict(height="85vh"),
    ),
)
affix = affix_menu(
    [
        affix_button(ids.affix_share, icons.share),
        affix_button(
            annot_editor.ids.open_annot_window_actionicon(annot_editor.aio_id),
            icons.add_annotation,
        ),
    ]
)


def map_type_control(value="hexbin"):
    return dmc.SegmentedControl(
        id=ids.map_type_control,
        value=value,
        data=[
            {"value": "hexbin", "label": "Hexagons"},
            {"value": "bubble", "label": "Bubbles"},
        ],
    )


def layout(**qargs):
    query_args = parse_nested_qargs(qargs)
    if len(query_args) == 0:
        return dmc.Container(
            [
                viz_compare_select_modal(id=ids.select_modal, title="Select one or two datasets from the list"),
                dcc.Location(ids.url, refresh=True),
            ],
        )
    bubble_map = query_args.get("maptype") == "bubble"
    if bubble_map:
        map_type_ctl = map_type_control("bubble")
    else:
        map_type_ctl = map_type_control()
    
    single_dataset = len(query_args.get("datasets"))==1

    return dmc.Container(
        [
            dcc.Location(ids.url, refresh=False),
            html.Div(id=ids.config_modal_div),
            html.Div(id=ids.share_modal_div),
            affix,
            annot_editor,
            # dcc.Interval(id=ids.interval,interval=5000, n_intervals=0),
            dmc.Group(
                [
                    dmc.Text("Spatial exploration", size="lg", weight=600),
                    traio,
                ],
                position="apart",
            ),
            dmc.Space(h=8),
            dmc.Grid(
                [
                    dmc.Col(
                        dmc.LoadingOverlay(
                            multihexmap,
                            overlayOpacity=0,
                            transitionDuration=400,
                            loader=dmc.Card(
                                dmc.Group(
                                    [
                                        dmc.Loader(
                                            size="sm",
                                            # variant="dots",
                                            color="teal.5",
                                            # color="gray.0",
                                        ),
                                        dmc.Text(
                                            "Loading",
                                            color="gray.9",
                                            weight=500,
                                            size="md",
                                        ),
                                    ],
                                ),
                                style={
                                    "position": "absolute",
                                    # "top": 10,
                                    "bottom": 10,
                                    # "left": "50%",
                                    "left": 10,
                                    "backgroundColor": "rgba(245, 245, 245,0.8)",
                                },
                                py=3,
                                px=5,
                            ),
                        ),
                        className="col-md-10",
                    ),
                    dmc.Col(
                        [
                            dmc.Text("Datasets", weight=500),
                            dmc.Space(h=4),
                            dmc.Stack(id=ids.dataset_card_stack),
                            dmc.Space(h=4),
                            dmc.Center(
                                dmc.Anchor(
                                    id=ids.switch_datasets,
                                    children=dmc.Button(
                                        "Switch Positions",
                                        leftIcon=get_icon(icons.switch_arrows),
                                        variant="subtle",
                                    ),
                                    href=None,
                                    refresh=False,
                                ),
                                style={"display": "none"} if single_dataset else None,

                            ),
                            dmc.Space(h=12),
                            dmc.Stack(
                                [
                                    dmc.Divider(),
                                    dmc.Text("Map Type", weight=500),
                                    map_type_ctl,
                                ]
                            ),
                            dmc.Space(h=12),
                            dmc.Stack(
                                id=ids.map_config_stack,
                                style={"display": "none"} if bubble_map else None,
                                children=[
                                    dmc.Text("Map configuration", weight=500),
                                    dmc.Checkbox(
                                        label="Show Scatter Markers",
                                        id=ids.show_scatter,
                                        checked=False,
                                    ),
                                    dmc.Space(h=8),
                                    dmc.Text("Colorscale Finetuning", size="14px"),
                                    dmc.Center(
                                        get_icon(
                                            icons.hexagon_filled,
                                            width="1.5rem",
                                            color=MULTI_VIZ_COLORSCALE[0],
                                        ),
                                    ),
                                    dmc.RangeSlider(
                                        id=ids.colorscale_slider_1,
                                        value=[0, 100],
                                        minRange=0.1,
                                        step=0.1,
                                        min=0,
                                        max=100,
                                        precision=2,
                                        color=MULTI_VIZ_COLORSCALE_MT[0],
                                        marks=[
                                            {"value": 20, "label": "20%"},
                                            {"value": 50, "label": "50%"},
                                            {"value": 80, "label": "80%"},
                                        ],
                                        mb=20,
                                    ),
                                    dmc.Center(
                                        get_icon(
                                            icons.hexagon_outline,
                                            width="1.5rem",
                                            color=MULTI_VIZ_COLORSCALE[1],
                                        ),
                                        style={"display": "none"} if single_dataset else None,

                                    ),
                                    dmc.RangeSlider(
                                        id=ids.colorscale_slider_2,
                                        value=[0, 100],
                                        minRange=1,
                                        min=0,
                                        step=0.1,
                                        precision=2,
                                        max=100,
                                        color=MULTI_VIZ_COLORSCALE_MT[1],
                                        mb=20,
                                        marks=[
                                            {"value": 20, "label": "20%"},
                                            {"value": 50, "label": "50%"},
                                            {"value": 80, "label": "80%"},
                                        ],
                                        style={"display": "none"} if single_dataset else None,

                                    ),
                                ],
                            ),
                        ],
                        className="col-md-2",
                    ),
                ]
            ),
        ],
        fluid=True,
        px=4,
    )


# generate modal content if modal is opened (no datasets in url)
@callback(
    Output(ids.select_modal, "children"),
    Input(ids.select_modal, "opened"),
    State("traces_store", "data"),
)
def update_select_modal(is_open, data):
    if is_open:
        collected_traces = generate_viz_map_select_modal_children(
            data, id_role=ids.modal_select_checkbox_role
        )
        if len(collected_traces) == 0:
            collected_traces = [
                dmc.Alert("It looks like you have not collected any datasets yet.")
            ]
        return dmc.Stack(
            [
                dmc.ScrollArea(
                    dmc.Stack(collected_traces),
                    offsetScrollbars=True,
                    type="scroll",
                    style={"height": "60vh"},
                ),
                dmc.Group(
                    [
                        dmc.Anchor(
                            dmc.Button("Cancel", color="indigo", variant="outline"),
                            href=PATH_PREFIX + "select",
                        ),
                        dmc.Button(
                            "Go",
                            color="teal",
                            id=ids.apply_selection_btn,
                            disabled=True,
                        ),
                    ],
                    position="right",
                ),
            ]
        )
    raise PreventUpdate


# enable button in modal to apply selection, redirect to url with search args, store default config
@callback(
    Output(ids.apply_selection_btn, "disabled"),
    Output(ids.url, "search", allow_duplicate=True),
    Input({"role": ids.modal_select_checkbox_role, "index": ALL}, "checked"),
    Input(ids.apply_selection_btn, "n_clicks"),
    State(ids.url, "search"),
    prevent_initial_call="initial_duplicate",
)
def generate_link(checkboxes, nc, search):
    trg = ctx.triggered_id
    if trg is not None:
        n_selected = sum(checkboxes)
        checked_elements = [i for i, x in enumerate(checkboxes) if x]
        if trg == ids.apply_selection_btn and nc is not None:

            input_ids = ctx.inputs_list[0]
            traces = []
            initial_dataset_configs = []
            for i in checked_elements:
                index_str = input_ids[i].get("id").get("index")
                index_str = index_str.replace("'", '"').replace("None", "null")
                index_dict = json.loads(index_str)

                traces.append(index_dict)
                initial_dataset_configs.append(default_view_config(index_dict))
            try:
                query_args = parse_nested_qargs(qargs_to_dict(search))
            except:
                query_args = {}
            query_args["datasets"] = traces
            query_args["cfg"] = initial_dataset_configs

            return (
                no_update,
                f"?{urlencode_dict(query_args)}",
            )

        return n_selected not in [1,2], no_update
    return no_update, no_update


# update timerangeaio from url
@callback(
    Output(traio.ids.store_set(traio.aio_id), "data"),
    Input(ids.url, "pathname"),
    State(ids.url, "search"),
)
def update_tr_store(pn, search_args):
    if search_args is not None:
        query_args = qargs_to_dict(search_args)
        query_args_dr = [
            query_args.get("from", str(DEFAULT_TR_START.isoformat())),
            query_args.get("to", str(datetime.datetime.now().isoformat())),
        ]
        return query_args_dr
    return no_update


# update search
@callback(
    Output(ids.url, "search"),
    Input(traio.ids.store(traio.aio_id), "modified_timestamp"),
    State(traio.ids.store(traio.aio_id), "data"),
    State(ids.url, "search"),
    Input(ids.map_type_control, "value"),
)
def update_url_location(dr_trg, dr, search_args, map_type):
    query_args = parse_nested_qargs(qargs_to_dict(search_args))
    if isinstance(dr, list) and dr[0] is not None and dr[1] is not None:
        dr_s = dr[0]
        dr_e = dr[1]
        query_args["from"] = dr_s
        query_args["to"] = dr_e
        if map_type is not None:
            query_args["maptype"] = map_type
        return f"?{urlencode_dict(query_args)}"
    return no_update


@callback(
    Output(multihexmap.ids.config_store(multihexmap.aio_id), "data"),
    Input(ids.show_scatter, "checked"),
    Input(ids.colorscale_slider_1, "value"),
    Input(ids.colorscale_slider_2, "value"),
    Input(ids.map_type_control, "value"),
)
def set_scatter_config(checked, range0, range1, type):
    if type is not None:
        bubble = type == "bubble"
        return {
            "scatter": checked,
            "range0": range0,
            "range1": range1,
            "bubble": bubble,
        }


# load map data
@callback(
    Output(multihexmap.ids.store(multihexmap.aio_id), "data", allow_duplicate=True),
    Input(ids.url, "search"),
    Input(ids.url, "pathname"),
    prevent_initial_call=True,
)
def update_map_store(search, pn):
    if not "viz/map" in pn or len(search) < 2:
        raise PreventUpdate
    args = UrlSearchArgs(**parse_nested_qargs(qargs_to_dict(search)))
    datasets = args.datasets
    if args.cfg is None:
        raise PreventUpdate
    # load dataset0
    locationdata = []
    for i in range(len(datasets)):
        ds = to_typed_dataset(datasets[i])
        if ds.type == DatasetType.birds:
            locations = get_detection_locations(
                taxon_id=ds.datum_id,
                confidence=args.cfg[i].confidence,
                time_from=args.view_config.time_from,
                time_to=args.view_config.time_to,
            )
            ds_location = resp_to_locationdata(locations, name=ds.get_title())
            if int(ds.datum_id) in POLLINATOR_IDS:
                locations_polli = get_polli_detection_locations_by_id(
                    taxon_id=ds.datum_id,
                    deployment_ids=None,
                    confidence=args.cfg[i].confidence,
                    time_from=args.view_config.time_from,
                    time_to=args.view_config.time_to,
                )
                if locations_polli is not None:
                    add_datapoints_to_locationdata(ds_location, locations_polli)
            locationdata.append(ds_location)
        elif ds.type == DatasetType.multi_pax:
            pax_locations = get_pax_locations(
                deployment_id=ds.deployment_id,
                time_from=args.view_config.time_from,
                time_to=args.view_config.time_to,
            )
            if pax_locations is not None:

                locationdata.append(resp_to_locationdata(pax_locations, ds.get_title()))
        elif ds.type == DatasetType.gbif_observations:
            gbif_locations = get_gbif_detection_locations(
                taxon_id=ds.datum_id,
                time_from=args.view_config.time_from,
                time_to=args.view_config.time_to,
            )
            if gbif_locations is not None:

                locationdata.append(
                    resp_to_locationdata(gbif_locations, ds.get_title())
                )

        else:
            locationdata.append(LocationData())
    return [l.to_dict() for l in locationdata]


# update dataset cards
@callback(
    Output(ids.dataset_card_stack, "children"),
    Input(ids.url, "search"),
    Input(ids.url, "pathname"),
)
def update_dataset_cards(search, pn):
    if not "viz/map" in pn:
        raise PreventUpdate
    args = UrlSearchArgs(**parse_nested_qargs(qargs_to_dict(search)))
    if args.datasets is not None:

        ds_cards = [
            dataset_info_card(
                args=args,
                index=0,
                config_btn_role=ids.dataset_config_role,
                visible_btn_id=dict(role=ids.ds_visible_role,index=0),#ids.ds1_visible,
                trace_icon=icons.hexagon_filled,
                icon_color=SEQUENTIAL_COLORSCALES[0][
                    int(len(SEQUENTIAL_COLORSCALES[0]) / 2) + 1
                ],
            )]
        if len(args.datasets)==2:
            ds_cards.append(
                dataset_info_card(
                    args=args,
                    index=1,
                    config_btn_role=ids.dataset_config_role,
                    visible_btn_id=dict(role=ids.ds_visible_role,index=1),#ids.ds2_visible,
                    trace_icon=icons.hexagon_outline,
                    icon_color=SEQUENTIAL_COLORSCALES[1][
                        int(len(SEQUENTIAL_COLORSCALES[1]) / 2) + 1
                    ],
                )
            )
        return ds_cards
    raise PreventUpdate


# generate config modal
@callback(
    Output(ids.config_modal_div, "children"),
    Input({"role": ids.dataset_config_role, "index": ALL}, "n_clicks"),
    State(ids.url, "search"),
    prevent_initial_call=True,
)
def open_config_modal(buttons, search):
    if any(buttons) and ctx.triggered_id is not None:
        args = UrlSearchArgs(**parse_nested_qargs(qargs_to_dict(search)))
        btn_index = ctx.triggered_id.get("index")
        ds = to_typed_dataset(args.datasets[btn_index])
        cfg = args.cfg[btn_index]
        return dataset_config_modal(
            ds,
            cfg,
            index=btn_index,
            id=ids.config_modal,
            apply_btn_role=ids.apply_config_role,
            agg_select_id=ids.agg_select,
            confidence_select_id=ids.confidence_select,
        )
    raise PreventUpdate


# apply config and close modal
@callback(
    Output(ids.url, "search", allow_duplicate=True),
    Output(ids.config_modal, "opened"),
    Input({"role": ids.apply_config_role, "index": ALL}, "n_clicks"),
    State(ids.confidence_select, "value"),
    State(ids.agg_select, "value"),
    State(ids.url, "search"),
    prevent_initial_call=True,
)
def apply_dataset_configuration(apply_btns, confidence, agg, search):
    if any(apply_btns):
        dataset_index = ctx.triggered_id.get("index")
        new_cfg = {}
        if confidence:
            new_cfg["confidence"] = confidence
        if agg:
            new_cfg["agg"] = agg

        query_args = parse_nested_qargs(qargs_to_dict(search))
        query_args["cfg"][dataset_index] = new_cfg
        return f"?{urlencode_dict(query_args)}", False
    raise PreventUpdate


@callback(Output(ids.map_config_stack, "style"), Input(ids.map_type_control, "value"))
def hide_hexbinmap_control(value):
    if value is not None:
        if value == "bubble":
            return {"display": "none"}
        else:
            return None
    raise PreventUpdate


@callback(
    Output(multihexmap.ids.store(multihexmap.aio_id), "data", allow_duplicate=True),
    #Input(ids.ds1_visible, "checked"),
    #Input(ids.ds2_visible, "checked"),
    Input({"role":ids.ds_visible_role, "index":ALL},"checked"),
    #Input({"role":ids.ds_visible_role, "index":1},"checked"),
    State(multihexmap.ids.store(multihexmap.aio_id), "data"),
    prevent_initial_call=True,
)
def update_visibility(btns, data):
    if data is not None and btns is not None:
        if not len(btns)==len(data):
            raise PreventUpdate

        for i in range(len(data)):
            data[i]["visible"] = btns[i]
        return data

    raise PreventUpdate


# switch_datasets
@callback(
    Output(ids.switch_datasets, "href"),
    Input(ids.url, "search"),
    State(ids.url, "pathname"),
)
def update_switch_datasets_href(search, pn):
    if not "viz/map" in pn:
        raise PreventUpdate
    query_args = parse_nested_qargs(qargs_to_dict(search))
    datasets = query_args.get("datasets")
    cfg = query_args.get("cfg")
    if cfg is None or datasets is None:
        raise PreventUpdate
    datasets.reverse()
    cfg.reverse()
    query_args["datasets"] = datasets
    query_args["cfg"] = cfg
    return f"{pn}?{urlencode_dict(query_args)}"


# share modal
@callback(
    Output(ids.share_modal_div, "children"),
    Input(ids.affix_share, "n_clicks"),
    State(ids.url, "search"),
    State(ids.url, "href"),
)
def show_modal(nc, search, href):
    if nc is not None:
        base_path = href.split("?")[0]
        path_to_share = base_path + search
        return share_modal(path_to_share)
    return no_update


# post annotation
@callback(
    Output(ids.share_modal_div, "children", allow_duplicate=True),
    Output(
        annot_editor.ids.annot_published_store(annot_editor.aio_id),
        "data",
        allow_duplicate=True,
    ),
    Input(annot_editor.ids.publish_btn(annot_editor.aio_id), "n_clicks"),
    State(ids.url, "search"),
    State(ids.url, "pathname"),
    State(annot_editor.ids.store(annot_editor.aio_id), "data"),
    prevent_initial_call=True,
)
def publish_annotation(nc, search, pathname, data):
    if nc is not None:
        cookies = flask.request.cookies

        user = get_user_from_cookies(cookies)

        annot = Annotation(
            user=user, url=pathname.split(PATH_PREFIX)[1] + search, **data
        )
        title_row = dmc.Group(
            [
                dmc.Text(annot.title, weight=600, size="xl"),
                dmc.Group(
                    [
                        dmc.Text(annot.time_str, weight=300),
                        dmc.Text(f"by {user.username}"),
                    ]
                ),
            ],
            position="apart",
        )
        if post_annotation(annotation=annot, auth_cookie=cookies.get("auth")):

            return (
                dmc.Modal(
                    children=dmc.Card(
                        [
                            title_row,
                            dmc.Space(h=12),
                            dmc.Divider(pb=12),
                            dcc.Markdown(data.get("md_content")),
                        ],
                        withBorder=False,
                    ),
                    opened=True,
                    title=dmc.Group(
                        [
                            dmc.Text("Annotation published!", weight=500),
                            get_icon(
                                icons.success_round, width="1.5rem", color="green"
                            ),
                        ],
                        spacing="xs",
                    ),
                    size="60%",
                    zIndex=1000,
                ),
                1,
            )
        else:
            return (
                dmc.Modal(
                    children=dmc.Alert(
                        children="Something went wrong. Try again.", color="red"
                    ),
                    opened=True,
                    title="Annotation not published",
                    size="60%",
                    zIndex=1000,
                ),
                no_update,
            )

    raise PreventUpdate
