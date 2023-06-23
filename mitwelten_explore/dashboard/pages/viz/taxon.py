import dash
from dash import dcc, callback, Input, Output, State, ctx, html, no_update
from dash.exceptions import PreventUpdate
import flask
import dash_mantine_components as dmc

from dashboard.aio_components.aio_hexbinmap_component import H3HexBinMapAIO
from dashboard.aio_components.aio_time_range_picker_component import TimeRangeAIO
from dashboard.aio_components.aio_texteditor_component import TextEditorAIO
from dashboard.components.navbar import ThemeSwitchAIO
from uuid import uuid4
import datetime
from dashboard.components.affix import affix_menu, affix_button
from dashboard.components.selects import (
    confidence_threshold_select,
    time_bucket_select,
)
from dashboard.components.cards import taxon_stat_card, taxon_viz_info_card
from dashboard.components.tables import taxon_species_detections_table
from dashboard.api_clients.bird_results_client import (
    get_species_detection_count_by_parent,
    get_detection_dates,
    get_detection_locations,
    get_detection_time_of_day,
)
from dashboard.api_clients.pollinator_results_client import (
    POLLINATOR_IDS,
    get_polli_detection_dates_by_id,
    get_polli_detection_locations_by_id,
    get_polli_detection_tod_by_id,
)
from dashboard.api_clients.gbif_cache_client import (
    get_gbif_detection_dates,
    get_gbif_detection_locations,
    get_gbif_detection_time_of_day,
)

from dashboard.api_clients.taxonomy_client import get_taxon
from dashboard.api_clients.userdata_client import post_annotation
from dashboard.utils.communication import (
    parse_nested_qargs,
    qargs_to_dict,
    urlencode_dict,
    get_user_from_cookies,
)
from dashboard.utils.ts import merge_detections_dicts
from dashboard.utils.geo_utils import validate_coordinates
from dashboard.charts.time_series_charts import (
    generate_ts_figure,
    no_data_figure,
    generate_time_of_day_scatter,
    empty_figure,
)
from dashboard.components.chart_configuration import (
    timeseries_chart_config_menu,
    reload_control,
)
from dashboard.components.overlays import chart_loading_overlay
from dashboard.components.modals import share_modal
from dashboard.models import UrlSearchArgs, Annotation

from dashboard.styles import icons, SINGLE_CHART_COLOR
from configuration import DEFAULT_TR_START, DEFAULT_TOD_BUCKET_WIDTH, PATH_PREFIX

dash.register_page(__name__, path_template="/viz/taxon/<taxon_id>")


class PageIds(object):
    url = str(uuid4())
    conf_select = str(uuid4())
    bucket_select = str(uuid4())
    share_modal_div = str(uuid4())
    affix_share = str(uuid4())
    affix_annotate = str(uuid4())
    title = str(uuid4())
    total_det_txt = str(uuid4())
    n_depl_txt = str(uuid4())
    time_bucket_indicator = str(uuid4())
    time_series_chart = str(uuid4())
    time_series_chart_type = str(uuid4())
    time_series_chart_reload = str(uuid4())
    time_of_day_chart = str(uuid4())
    tod_bucket_indicator = str(uuid4())
    tod_chart_type = str(uuid4())
    subspecies_list = str(uuid4())
    taxon_card_div = str(uuid4())
    data_src_select = str(uuid4())


ids = PageIds()

stat_card = taxon_stat_card(ids.total_det_txt, ids.n_depl_txt)

traio = TimeRangeAIO(dates=[None, None])
hexbinmap = H3HexBinMapAIO(
    graph_props=dict(
        config=dict(fillFrame=False, displayModeBar=False),
        responsive=True,
        style=dict(height="45vh"),
    ),
)
annot_editor = TextEditorAIO()


affix = affix_menu(
    [
        affix_button(ids.affix_share, icons.share),
        affix_button(
            annot_editor.ids.open_annot_window_actionicon(annot_editor.aio_id),
            icons.add_annotation,
        ),
    ]
)


def data_src_select(id, mitwelten=True, gbif=False):
    options = ["Mitwelten", "GBIF"]
    values = []
    if mitwelten:
        values.append("mitwelten")
    if gbif:
        values.append("gbif")
    return dmc.Group(
        [
            dmc.Text("Source", size="sm"),
            dmc.ChipGroup(
                [
                    dmc.Chip(x, value=x.lower(), variant="outline", color="teal.6")
                    for x in options
                ],
                id=id,
                value=values,
                multiple=True,
            ),
        ],
        spacing="xs",
    )


def layout(taxon_id=None, **qargs):
    query_args = parse_nested_qargs(qargs)
    if query_args.get("bucket") is None:
        query_args["bucket"] = "1w"
    args = UrlSearchArgs(**query_args)
    vc = args.view_config
    tb_select = time_bucket_select(id=ids.bucket_select, value=vc.bucket)
    conf_select = confidence_threshold_select(id=ids.conf_select, value=vc.confidence)
    if args.mw_data is None and args.gbif_data is None:
        mitwelten = True
        gbif = False
    else:
        mitwelten = args.mw_data if args.mw_data is not None else False
        gbif = args.gbif_data if args.gbif_data is not None else False
    src_select = data_src_select(ids.data_src_select, mitwelten=mitwelten, gbif=gbif)
    return dmc.Container(
        [
            html.Div(id=ids.share_modal_div),
            annot_editor,
            affix,
            dcc.Location(ids.url, refresh=False),
            dmc.Grid(
                [
                    dmc.Col(
                        dmc.Group(
                            [
                                html.Div(id=ids.title),
                            ]
                        ),
                        className="col-xl-3",
                    ),
                    dmc.Col(
                        dmc.Group(
                            [
                                dmc.Group(
                                    [
                                        src_select,
                                        conf_select,
                                        tb_select,
                                    ]
                                ),
                                traio,
                            ],
                            position="right",
                            noWrap=False,
                        ),
                        className="col-xl-9",
                    ),
                ]
            ),
            dmc.Space(h=12),
            dmc.Grid(
                [
                    dmc.Col(
                        [
                            dmc.Card(
                                children=[
                                    dmc.Group(
                                        [
                                            dmc.Group(
                                                [
                                                    dmc.Text("Time Series", weight=600),
                                                    dmc.Code(
                                                        id=ids.time_bucket_indicator,
                                                        children="1w",
                                                    ),
                                                ]
                                            ),
                                            dmc.Group(
                                                [
                                                    reload_control(
                                                        ids.time_series_chart_reload
                                                    ),
                                                    timeseries_chart_config_menu(
                                                        chart_type_id=ids.time_series_chart_type,
                                                        default_chart_type_index=2,
                                                        position="left-end",
                                                    ),
                                                ]
                                            ),
                                        ],
                                        position="apart",
                                    ),
                                    dmc.CardSection(
                                        chart_loading_overlay(
                                            dcc.Graph(
                                                figure=no_data_figure(annotation=None),
                                                id=ids.time_series_chart,
                                                style={"height": "30vh"},
                                                config=dict(displayModeBar=False),
                                            ),
                                            position="right",
                                        ),
                                    ),
                                ],
                                withBorder=True,
                                shadow="sm",
                            ),
                            dmc.Space(h=8),
                            dmc.Grid(
                                [
                                    dmc.Col(
                                        dmc.Card(
                                            children=dmc.CardSection(
                                                chart_loading_overlay(
                                                    hexbinmap,
                                                ),
                                            ),
                                            withBorder=True,
                                            shadow="sm",
                                        ),
                                        className="col-md-6",
                                    ),
                                    dmc.Col(
                                        dmc.Card(
                                            children=[
                                                dmc.Group(
                                                    [
                                                        dmc.Group(
                                                            [
                                                                dmc.Text(
                                                                    "Time Of Day",
                                                                    weight=600,
                                                                ),
                                                                dmc.Code(
                                                                    id=ids.tod_bucket_indicator,
                                                                    children="20 min",
                                                                ),
                                                            ]
                                                        ),
                                                        dmc.Group(
                                                            [
                                                                timeseries_chart_config_menu(
                                                                    chart_type_id=ids.tod_chart_type,
                                                                    position="left-end",
                                                                ),
                                                            ]
                                                        ),
                                                    ],
                                                    position="apart",
                                                ),
                                                dmc.CardSection(
                                                    chart_loading_overlay(
                                                        dcc.Graph(
                                                            figure=no_data_figure(
                                                                annotation=None
                                                            ),
                                                            id=ids.time_of_day_chart,
                                                            config=dict(
                                                                displayModeBar=False,
                                                            ),
                                                            style={"height": "100%"},
                                                        ),
                                                        position="right",
                                                    ),
                                                ),
                                            ],
                                            withBorder=True,
                                            shadow="sm",
                                            style={"height": "100%"},
                                        ),
                                        className="col-md-6",
                                    ),
                                ],
                                gutter="xs",
                            ),
                        ],
                        className="col-lg-9",
                    ),
                    dmc.Col(
                        [
                            stat_card,
                            dmc.ScrollArea(
                                [
                                    dmc.Space(h=4),
                                    html.Div(id=ids.taxon_card_div),
                                    dmc.Space(h=4),
                                    dmc.Card(
                                        id=ids.subspecies_list,
                                        withBorder=True,
                                        shadow="sm",
                                    ),
                                ],
                                style={"height": "90%"},
                            ),
                        ],
                        className="col-lg-3",
                        style={"maxHeight": "90vh"},
                    ),
                ],
                gutter="xs",
            ),
        ],
        fluid=True,
    )


# update timerangeaio from url
@callback(
    Output(traio.ids.store_set(traio.aio_id), "data"),
    Input(ids.url, "pathname"),
    State(ids.url, "search"),
    Input(ids.time_series_chart, "relayoutData"),
    State(ids.time_series_chart_reload, "checked"),
)
def update_tr_store(pn, search_args, relayout_event, reload_enabled):
    if pn is not None:
        query_args = qargs_to_dict(search_args)
        query_args_dr = [
            query_args.get("from", str(DEFAULT_TR_START.isoformat())),
            query_args.get("to", str(datetime.datetime.now().isoformat())),
        ]

        trg = ctx.triggered_id
        if trg == ids.time_series_chart:
            if not reload_enabled:
                return query_args_dr
            if (
                "xaxis.range[0]" in relayout_event
                and "xaxis.range[1]" in relayout_event
            ):
                try:
                    ts_0 = datetime.datetime.fromisoformat(
                        relayout_event.get("xaxis.range[0]").split(".")[0]
                    ).isoformat()
                    ts_1 = datetime.datetime.fromisoformat(
                        relayout_event.get("xaxis.range[1]").split(".")[0]
                    ).isoformat()
                    return [ts_0, ts_1]
                except:
                    return query_args_dr
        return query_args_dr
    raise PreventUpdate


# update search
@callback(
    Output(ids.url, "search"),
    Input(ids.bucket_select, "value"),
    Input(ids.conf_select, "value"),
    Input(ids.data_src_select, "value"),
    Input(traio.ids.store(traio.aio_id), "modified_timestamp"),
    State(traio.ids.store(traio.aio_id), "data"),
    State(ids.url, "search"),
)
def update_url_location(tb, conf, src, dr_trg, dr, search_args):
    query_args = parse_nested_qargs(qargs_to_dict(search_args))

    if isinstance(dr, list) and dr[0] is not None and dr[1] is not None:
        dr_s = dr[0]
        dr_e = dr[1]
        query_args["bucket"] = tb
        query_args["from"] = dr_s
        query_args["to"] = dr_e
        if conf:
            query_args["confidence"] = conf
        if isinstance(src, list):
            if "mitwelten" in src:
                query_args["mw_data"] = True
            else:
                query_args["mw_data"] = False
            if "gbif" in src:
                query_args["gbif_data"] = True
            else:
                query_args["gbif_data"] = False

        return f"?{urlencode_dict(query_args)}"
    raise PreventUpdate


# update title and taxon info card from url
@callback(
    Output(ids.title, "children"),
    Output(ids.taxon_card_div, "children"),
    Input(ids.url, "pathname"),
)
def update_title(pn):
    if pn is not None and "viz/taxon" in pn:
        taxon_id = pn.split("/")[-1]
        selected_taxon = get_taxon(taxon_key=taxon_id)
        return (
            dmc.Group(
                [
                    dmc.Text(selected_taxon.label_sci, weight=700, size="xl"),
                    dmc.Badge(
                        selected_taxon.rank,
                        color="gray",
                        radius="xs",
                        variant="outline",
                    ),
                ]
            ),
            taxon_viz_info_card(taxon_id),
        )
    raise PreventUpdate


# update main chart
@callback(
    Output(ids.time_series_chart, "figure"),
    Output(ids.time_bucket_indicator, "children"),
    Input(ids.url, "pathname"),
    Input(ids.url, "search"),
    Input(ThemeSwitchAIO.ids.switch("theme"), "value"),
    Input(ids.time_series_chart_type, "value"),
    prevent_initial_call=True,
)
def update_ts_chart(pn, search, theme, chart_type):
    if pn is not None and "viz/taxon" in pn:
        query_args = parse_nested_qargs(qargs_to_dict(search))
        args = UrlSearchArgs(**query_args)
        vc = args.view_config
        taxon_id = pn.split("/")[-1]
        det_dates = None
        if args.mw_data:
            det_dates = get_detection_dates(
                taxon_id=taxon_id,
                confidence=vc.confidence,
                bucket_width=vc.bucket,
                time_from=vc.time_from,
                time_to=vc.time_to,
            )
            if int(taxon_id) in POLLINATOR_IDS:
                det_dates_polli = get_polli_detection_dates_by_id(
                    taxon_id=taxon_id,
                    deployment_ids=None,
                    confidence=vc.confidence,
                    bucket_width=vc.bucket,
                    time_from=vc.time_from,
                    time_to=vc.time_to,
                )
                det_dates = merge_detections_dicts(det_dates, det_dates_polli)
        if args.gbif_data:
            gbif_det_dates = get_gbif_detection_dates(
                taxon_id=taxon_id,
                bucket_width=vc.bucket,
                time_from=vc.time_from,
                time_to=vc.time_to,
            )
            det_dates = merge_detections_dicts(det_dates, gbif_det_dates)

        if det_dates is not None:
            return (
                generate_ts_figure(
                    times=det_dates.get("bucket"),
                    values=det_dates.get("detections"),
                    date_from=vc.time_from,
                    date_to=vc.time_to,
                    chart_type=chart_type,
                    marker_color=SINGLE_CHART_COLOR,
                    light_mode=theme,
                ),
                f"bucket: {vc.bucket}",
            )
        return (
            generate_ts_figure(
                times=[],
                values=[],
                date_from=vc.time_from,
                date_to=vc.time_to,
                chart_type=chart_type,
                marker_color=SINGLE_CHART_COLOR,
                light_mode=theme,
            ),
            f"bucket: {vc.bucket}",
        )
    raise PreventUpdate


# update hexbinmap & stat from controls
@callback(
    Output(hexbinmap.ids.store(hexbinmap.aio_id), "data"),
    Output(ids.total_det_txt, "children"),
    Output(ids.n_depl_txt, "children"),
    Input(ids.conf_select, "value"),
    Input(traio.ids.store(traio.aio_id), "data"),
    Input(ids.url, "pathname"),
    Input(ids.url, "search"),
)
def update_map_stats(conf, time_range, pn, search):
    if pn is not None and "viz/taxon" in pn:
        taxon_id = pn.split("/")[-1]
        if conf is None or time_range is None or time_range[0] is None:
            raise PreventUpdate
        query_args = parse_nested_qargs(qargs_to_dict(search))
        args = UrlSearchArgs(**query_args)
        hexbin_data = {
            "latitude": [],
            "longitude": [],
            "val": [],
            "id": [],
        }
        n_deployments = 0
        if args.mw_data:
            locations = get_detection_locations(
                taxon_id=taxon_id,
                confidence=conf,
                time_from=time_range[0],
                time_to=time_range[1],
            )
            if isinstance(locations, list):
                for l in locations:
                    latitude = l.get("location").get("lat")
                    longitude = l.get("location").get("lon")
                    if validate_coordinates(latitude, longitude):
                        hexbin_data["latitude"].append(latitude)
                        hexbin_data["longitude"].append(longitude)
                        hexbin_data["val"].append(l.get("detections"))
                        hexbin_data["id"].append(l.get("deployment_id"))
            if int(taxon_id) in POLLINATOR_IDS:
                locations_polli = get_polli_detection_locations_by_id(
                    taxon_id=taxon_id,
                    deployment_ids=None,
                    confidence=conf,
                    time_from=time_range[0],
                    time_to=time_range[1],
                )
                if isinstance(locations_polli, list):
                    for l in locations_polli:
                        latitude = l.get("location").get("lat")
                        longitude = l.get("location").get("lon")
                        if validate_coordinates(latitude, longitude):
                            hexbin_data["latitude"].append(latitude)
                            hexbin_data["longitude"].append(longitude)
                            hexbin_data["val"].append(l.get("detections"))
                            hexbin_data["id"].append(l.get("deployment_id"))
            n_deployments = len(hexbin_data["id"])
        if args.gbif_data:
            gbif_locations = get_gbif_detection_locations(
                taxon_id=taxon_id,
                time_from=time_range[0],
                time_to=time_range[1],
            )
            if isinstance(gbif_locations, list):
                for l in gbif_locations:
                    latitude = l.get("location").get("lat")
                    longitude = l.get("location").get("lon")
                    if validate_coordinates(latitude, longitude):
                        hexbin_data["latitude"].append(latitude)
                        hexbin_data["longitude"].append(longitude)
                        hexbin_data["val"].append(l.get("detections"))
                        hexbin_data["id"].append(0)
        return hexbin_data, sum(hexbin_data.get("val")), n_deployments
    raise PreventUpdate


# update time_of_day chart
@callback(
    Output(ids.time_of_day_chart, "figure"),
    Output(ids.tod_bucket_indicator, "children"),
    State(ids.url, "pathname"),
    Input(ids.url, "search"),
    Input(ids.tod_chart_type, "value"),
    Input(ThemeSwitchAIO.ids.switch("theme"), "value"),
    prevent_initial_call=True,
)
def update_time_of_day_chart(pn, search, chart_type, theme):
    if pn is not None and "viz/taxon" in pn:
        taxon_id = pn.split("/")[-1]
        query_args = parse_nested_qargs(qargs_to_dict(search))
        args = UrlSearchArgs(**query_args)
        vc = args.view_config
        tod_res = None
        if args.mw_data:
            tod_res = get_detection_time_of_day(
                taxon_id=taxon_id,
                confidence=vc.confidence,
                bucket_width_m=DEFAULT_TOD_BUCKET_WIDTH,
                time_from=vc.time_from,
                time_to=vc.time_to,
            )
            if int(taxon_id) in POLLINATOR_IDS:
                tod_res_polli = get_polli_detection_tod_by_id(
                    taxon_id=taxon_id,
                    deployment_ids=None,
                    confidence=vc.confidence,
                    bucket_width_m=DEFAULT_TOD_BUCKET_WIDTH,
                    time_from=vc.time_from,
                    time_to=vc.time_to,
                )
                tod_res = merge_detections_dicts(
                    tod_res,
                    tod_res_polli,
                    time_key="minuteOfDay",
                    value_key="detections",
                )
        if args.gbif_data:
            gbif_tod_res = get_gbif_detection_time_of_day(
                taxon_id=taxon_id,
                bucket_width_m=DEFAULT_TOD_BUCKET_WIDTH,
                time_from=vc.time_from,
                time_to=vc.time_to,
            )
            tod_res = merge_detections_dicts(
                tod_res,
                gbif_tod_res,
                time_key="minuteOfDay",
                value_key="detections",
            )
        if tod_res is not None:
            return (
                generate_time_of_day_scatter(
                    minutes_of_day=tod_res.get("minuteOfDay"),
                    values=tod_res.get("detections"),
                    light_mode=theme,
                    marker_color=SINGLE_CHART_COLOR,
                    spike=True,
                    chart_type=chart_type,
                ),
                f"bucket: {DEFAULT_TOD_BUCKET_WIDTH}m",
            )
        return (
            generate_time_of_day_scatter(
                minutes_of_day=[],
                values=[],
                light_mode=theme,
                marker_color=SINGLE_CHART_COLOR,
                spike=True,
                chart_type=chart_type,
            ),
            f"bucket: {DEFAULT_TOD_BUCKET_WIDTH}m",
        )
    raise PreventUpdate


@callback(
    Output(ids.subspecies_list, "children"),
    Input(ids.conf_select, "value"),
    Input(ids.url, "pathname"),
)
def update_subspecies_list(conf, pn):
    if pn is not None and "viz/taxon" in pn:
        taxon_id = pn.split("/")[-1]
        species_counts = get_species_detection_count_by_parent(
            taxon_id=taxon_id, confidence=conf
        )
        return taxon_species_detections_table(
            species_counts, confidence=conf, selected_species_id=taxon_id
        )

    raise PreventUpdate


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
                        withBorder=True,
                        style={"border": "1px solid green"},
                    ),
                    opened=True,
                    title="Annotation published!",
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
                    title="Annotation published!",
                    size="60%",
                    zIndex=1000,
                ),
                no_update,
            )

    raise PreventUpdate
