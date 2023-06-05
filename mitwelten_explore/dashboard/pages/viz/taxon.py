import dash
from dash import dcc, callback, Input, Output, State, ctx, html
from dash.exceptions import PreventUpdate
import dash_mantine_components as dmc

from dashboard.aio_components.aio_hexbinmap_component import H3HexBinMapAIO
from dashboard.aio_components.aio_time_range_picker_component import TimeRangeAIO
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
from dashboard.api_clients.taxonomy_client import get_taxon
from dashboard.utils.communication import (
    parse_nested_qargs,
    qargs_to_dict,
    urlencode_dict,
)

from dashboard.charts.time_series_charts import (
    generate_ts_figure,
    no_data_figure,
    generate_time_of_day_scatter,
)
from dashboard.components.chart_configuration import (
    timeseries_chart_config_menu,
    reload_control,
)
from dashboard.models import UrlSearchArgs
from dashboard.components.navbar import ThemeSwitchAIO

from dashboard.styles import icons, SINGLE_CHART_COLOR
from configuration import DEFAULT_TR_START, DEFAULT_TOD_BUCKET_WIDTH

dash.register_page(__name__, path_template="/viz/taxon/<taxon_id>")


class PageIds(object):
    url = str(uuid4())
    conf_select = str(uuid4())
    bucket_select = str(uuid4())
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
    subspecies_list = str(uuid4())
    taxon_card_div = str(uuid4())


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

affix = affix_menu(
    [
        affix_button(ids.affix_share, icons.share),
        affix_button(ids.affix_annotate, icons.add_annotation),
    ]
)


def layout(taxon_id=None, **qargs):
    query_args = parse_nested_qargs(qargs)
    if query_args.get("bucket") is None:
        query_args["bucket"] = "1w"
    args = UrlSearchArgs(**query_args)
    vc = args.view_config
    tb_select = time_bucket_select(id=ids.bucket_select, value=vc.bucket)
    conf_select = confidence_threshold_select(id=ids.conf_select, value=vc.confidence)
    return dmc.Container(
        [
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
                                        dmc.LoadingOverlay(
                                            dcc.Graph(
                                                figure=no_data_figure(annotation=None),
                                                id=ids.time_series_chart,
                                                style={"height": "30vh"},
                                                config=dict(displayModeBar=False),
                                            )
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
                                                hexbinmap,
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
                                                        dmc.Text(
                                                            "Time Of Day", weight=600
                                                        ),
                                                        dmc.Code(
                                                            id=ids.tod_bucket_indicator,
                                                            children="20 min",
                                                        ),
                                                    ]
                                                ),
                                                dmc.CardSection(
                                                    dmc.LoadingOverlay(
                                                        dcc.Graph(
                                                            figure=no_data_figure(
                                                                annotation=None
                                                            ),
                                                            id=ids.time_of_day_chart,
                                                            config=dict(
                                                                displayModeBar=False,
                                                            ),
                                                            style={"height": "100%"},
                                                        )
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
)
def update_tr_store(pn, search_args):
    if pn is not None:
        query_args = qargs_to_dict(search_args)
        args = UrlSearchArgs(**query_args)
        vc = args.view_config
        if vc.time_from and vc.time_to:
            return [vc.time_from, vc.time_to]
        else:
            return [
                str(DEFAULT_TR_START.isoformat()),
                str(datetime.datetime.now().isoformat()),
            ]
    raise PreventUpdate


# update search
@callback(
    Output(ids.url, "search"),
    Input(ids.bucket_select, "value"),
    Input(ids.conf_select, "value"),
    Input(traio.ids.store(traio.aio_id), "modified_timestamp"),
    State(traio.ids.store(traio.aio_id), "data"),
    State(ids.url, "search"),
)
def update_url_location(tb, conf, dr_trg, dr, search_args):
    query_args = parse_nested_qargs(qargs_to_dict(search_args))

    if isinstance(dr, list) and dr[0] is not None and dr[1] is not None:
        dr_s = dr[0]
        dr_e = dr[1]
        query_args["bucket"] = tb
        query_args["from"] = dr_s
        query_args["to"] = dr_e
        if conf:
            query_args["confidence"] = conf
        return f"?{urlencode_dict(query_args)}"
    raise PreventUpdate


# update title and taxon info card from url
@callback(
    Output(ids.title, "children"),
    Output(ids.taxon_card_div, "children"),
    Input(ids.url, "pathname"),
)
def update_title(pn):
    if pn is not None:
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
    query_args = parse_nested_qargs(qargs_to_dict(search))
    args = UrlSearchArgs(**query_args)
    vc = args.view_config
    taxon_id = pn.split("/")[-1]
    det_dates = get_detection_dates(
        taxon_id=taxon_id,
        confidence=vc.confidence,
        bucket_width=vc.bucket,
        time_from=vc.time_from,
        time_to=vc.time_to,
    )
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


# update hexbinmap & stat from controls
@callback(
    Output(hexbinmap.ids.store(hexbinmap.aio_id), "data"),
    Output(ids.total_det_txt, "children"),
    Output(ids.n_depl_txt, "children"),
    Input(ids.conf_select, "value"),
    Input(traio.ids.store(traio.aio_id), "data"),
    Input(ids.url, "pathname"),
)
def update_map_stats(conf, time_range, pn):
    if pn is not None:
        taxon_id = pn.split("/")[-1]
        if conf is None or time_range is None or time_range[0] is None:
            raise PreventUpdate
        locations = get_detection_locations(
            taxon_id=taxon_id,
            confidence=conf,
            time_from=time_range[0],
            time_to=time_range[1],
        )
        hexbin_data = {
            "latitude": [],
            "longitude": [],
            "val": [],
            "id": [],
        }
        if isinstance(locations, list):
            for l in locations:
                hexbin_data["latitude"].append(l.get("location").get("lat"))
                hexbin_data["longitude"].append(l.get("location").get("lon"))
                hexbin_data["val"].append(l.get("detections"))
                hexbin_data["id"].append(l.get("deployment_id"))
            return hexbin_data, sum(hexbin_data.get("val")), len(hexbin_data["id"])
    raise PreventUpdate


# update time_of_day chart
@callback(
    Output(ids.time_of_day_chart, "figure"),
    Output(ids.tod_bucket_indicator, "children"),
    Input(ids.conf_select, "value"),
    Input(traio.ids.store(traio.aio_id), "data"),
    State(ids.url, "pathname"),
    Input(ThemeSwitchAIO.ids.switch("theme"), "value"),
    prevent_initial_call=True,
)
def update_time_of_day_chart(conf, tr, pn, theme):
    if isinstance(tr, list) and len(tr) == 2 and pn is not None:
        taxon_id = pn.split("/")[-1]
        tod_res = get_detection_time_of_day(
            taxon_id=taxon_id,
            confidence=conf,
            bucket_width_m=DEFAULT_TOD_BUCKET_WIDTH,
            time_from=tr[0],
            time_to=tr[1],
        )
        return (
            generate_time_of_day_scatter(
                minutes_of_day=tod_res.get("minuteOfDay"),
                values=tod_res.get("detections"),
                light_mode=theme,
                marker_color=SINGLE_CHART_COLOR,
                spike=True,
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
    if pn is not None:
        taxon_id = pn.split("/")[-1]
        species_counts = get_species_detection_count_by_parent(
            taxon_id=taxon_id, confidence=conf
        )
        return taxon_species_detections_table(
            species_counts, confidence=conf, selected_species_id=taxon_id
        )

    raise PreventUpdate
