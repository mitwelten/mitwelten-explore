import dash
from dash import callback, Input, Output, State, no_update, ctx, dcc, html
from dash.exceptions import PreventUpdate
import flask
import datetime
from dashboard.aio_components.aio_time_range_picker_component import TimeRangeAIO
from dashboard.aio_components.aio_list_component import SearchableListAIO
from dashboard.aio_components.aio_texteditor_component import (
    TextEditorAIO,
    from_base64,
)
from dashboard.utils.communication import (
    parse_nested_qargs,
    urlencode_dict,
    qargs_to_dict,
    get_user_from_cookies,
)
import dash_mantine_components as dmc
from dashboard.components.modals import (
    viz_single_dataset_select_modal,
    generate_viz_timeseries_select_modal_children,
)
from dashboard.common_callbacks import share_modal_callback, publish_annotation_callback
from dashboard.components.selects import (
    confidence_threshold_select,
    agg_fcn_select,
    time_bucket_select,
)
from dashboard.components.tables import statsagg_table
from dashboard.data_handler import (
    get_time_series_from_query_args,
    get_time_of_day_from_qargs,
    get_locations_from_qargs,
    get_statsagg_from_qargs,
    get_data_sources,
)
from dashboard.components.chart_configuration import (
    timeseries_chart_config_menu,
    reload_control,
)
from dashboard.components.affix import affix_menu, affix_button, datasource_affix
from dashboard.components.dataset_presentation import dataset_title
from dashboard.components.navbar import ThemeSwitchAIO
from dashboard.components.notifications import generate_notification
from dashboard.components.overlays import chart_loading_overlay, datasource_indicator
from dashboard.styles import icons
from configuration import PATH_PREFIX, DEFAULT_CONFIDENCE, DEFAULT_TR_START
from dashboard.charts.time_series_charts import (
    generate_ts_figure,
    generate_time_of_day_scatter,
    empty_figure,
)
from dashboard.charts.map_charts import generate_scatter_map_plot
from dashboard.charts.analytic_charts import fft_single
from dashboard.models import UrlSearchArgs, DatasetType, Annotation, to_typed_dataset
from dashboard.utils.ts import compute_fft, create_fft_bins

from uuid import uuid4


class PageIds(object):
    conf_select = str(uuid4())
    agg_select = str(uuid4())
    bucket_select = str(uuid4())
    select_dataset_modal = str(uuid4())
    url = str(uuid4())
    store_ts_data = str(uuid4())
    store_tod_data = str(uuid4())
    store_map_data = str(uuid4())
    store_statsagg_data = str(uuid4())
    title = str(uuid4())
    affix_share = str(uuid4())
    affix_annotate = str(uuid4())
    share_modal_div = str(uuid4())
    main_chart = str(uuid4())
    main_chart_type = str(uuid4())
    main_chart_sync = str(uuid4())
    statsagg_card = str(uuid4())
    tod_chart = str(uuid4())
    tod_chart_type = str(uuid4())
    map_chart = str(uuid4())
    fft_chart = str(uuid4())
    datasource_indicator = str(uuid4())
    tabs_selector = str(uuid4())


ids = PageIds()

TABS_CARD_STYLE = {
    "borderTop": "0px",
    "borderTopLeftRadius": "0px",
    "borderTopRightRadius": "0px",
}
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

traio = TimeRangeAIO(dates=[None, None])


dash.register_page(__name__, path_template="/viz/timeseries")


def layout(**qargs):
    query_args = parse_nested_qargs(qargs)
    args = UrlSearchArgs(**query_args)
    if args.dataset is None:
        return dmc.Container(
            viz_single_dataset_select_modal(True, id=ids.select_dataset_modal)
        )
    vc = args.view_config
    ds = to_typed_dataset(args.dataset)
    if ds.type in [
        DatasetType.meteodata,
        DatasetType.env_humi,
        DatasetType.env_temp,
        DatasetType.env_moist,
    ]:
        agg_select = agg_fcn_select(id=ids.agg_select, value=vc.agg)
        tb_select = time_bucket_select(id=ids.bucket_select, value=vc.bucket)
        conf_select = confidence_threshold_select(id=ids.conf_select, visible=False)
    elif ds.type in [
        DatasetType.birds,
        DatasetType.pollinators,
        DatasetType.distinct_species,
    ]:
        agg_select = agg_fcn_select(id=ids.agg_select, value=None, visible=False)
        tb_select = time_bucket_select(id=ids.bucket_select, value=vc.bucket)
        conf_select = confidence_threshold_select(
            id=ids.conf_select, value=vc.confidence
        )
    elif ds.type in [DatasetType.pax, DatasetType.gbif_observations]:
        agg_select = agg_fcn_select(id=ids.agg_select, value=None, visible=False)
        tb_select = time_bucket_select(id=ids.bucket_select, value=vc.bucket)
        conf_select = confidence_threshold_select(
            id=ids.conf_select, value=None, visible=False
        )
    else:
        return dmc.Container(
            viz_single_dataset_select_modal(True, id=ids.select_dataset_modal)
        )
    return dmc.Container(
        [
            dcc.Location(id=ids.url, refresh=False),
            dcc.Store(ids.store_map_data),
            dcc.Store(ids.store_statsagg_data),
            html.Div(id=ids.share_modal_div),
            annot_editor,
            datasource_affix(ids.datasource_indicator),
            affix,
            # Header: name and filters
            dmc.Grid(
                [
                    dmc.Col(
                        id=ids.title,
                        className="col-xl-4",
                    ),
                    dmc.Col(
                        dmc.Group(
                            [
                                dmc.Group(
                                    [
                                        conf_select,
                                        agg_select,
                                        tb_select,
                                    ]
                                ),
                                traio,
                            ],
                            position="right",
                            noWrap=False,
                        ),
                        className="col-xl-8",
                    ),
                ]
            ),
            dmc.Space(h=12),
            # Main Chart
            dmc.Card(
                [
                    dmc.Group(
                        [
                            dmc.Text("Time Series", weight=500),
                            dmc.Group(
                                [
                                    reload_control(ids.main_chart_sync),
                                    timeseries_chart_config_menu(
                                        chart_type_id=ids.main_chart_type,
                                        position="left-end",
                                    ),
                                ],
                            ),
                        ],
                        position="apart",
                    ),
                    chart_loading_overlay(
                        [
                            dcc.Store(ids.store_ts_data),
                            dcc.Graph(
                                id=ids.main_chart,
                                figure=empty_figure(),
                                style={
                                    "height": "40vh",
                                },
                            ),
                        ],
                        position="right",
                    ),
                ],
                withBorder=True,
                #className="bg-transparent",
            ),
            dmc.Space(h=12),
            dmc.Grid(
                [
                    # time of day card
                    dmc.Col(
                        [
                            dmc.Tabs(
                                color="teal",
                                value="tod",
                                variant="outline",
                                children=[
                                    dmc.TabsList(
                                        [
                                            dmc.Tab(
                                                dmc.Text("Time of Day", weight=500),
                                                value="tod",
                                            ),
                                        ]
                                    ),
                                    dmc.TabsPanel(
                                        value="tod",
                                        children=dmc.Card(
                                            [
                                                chart_loading_overlay(
                                                    [
                                                        dcc.Store(ids.store_tod_data),
                                                        dmc.Group(
                                                            timeseries_chart_config_menu(
                                                                chart_type_id=ids.tod_chart_type,
                                                                position="left-end",
                                                            ),
                                                            position="right",
                                                            style={
                                                                "position": "absolute",
                                                                "right": 4,
                                                                "top": 4,
                                                                "zIndex": 1000,
                                                            },
                                                        ),
                                                        dcc.Graph(
                                                            id=ids.tod_chart,
                                                            style={"height": "35vh"},
                                                            figure=empty_figure(),
                                                            className="ts_tod_chart",
                                                            config=dict(
                                                                displaylogo=False,
                                                                modeBarButtonsToRemove=[
                                                                    "pan",
                                                                    "select",
                                                                    "lasso",
                                                                    "zoom",
                                                                    "dragmode",
                                                                    "autoscale",
                                                                    "zoomin",
                                                                    "zoomout",
                                                                ],
                                                            ),
                                                        ),
                                                    ],
                                                    position="right",
                                                    style={"height": "100%"},
                                                ),
                                            ],
                                            withBorder=True,
                                            style=TABS_CARD_STYLE,
                                            p=0,
                                        ),
                                    ),
                                ],
                            ),
                        ],
                        className="col-xl-6",
                        style={"height": "42vh"},
                    ),
                    dmc.Col(
                        style={"height": "42vh"},
                        className="col-xl-6",
                        children=[
                            dmc.Tabs(
                                id=ids.tabs_selector,
                                color="teal",
                                value="map",
                                variant="outline",
                                h="100%",
                                maw="100%",
                                children=[
                                    dmc.TabsList(
                                        [
                                            dmc.Tab(
                                                dmc.Text("Map", weight=500),
                                                value="map",
                                            ),
                                            dmc.Tab(
                                                dmc.Text("Stats", weight=500),
                                                value="stats",
                                            ),
                                            dmc.Tab(
                                                dmc.Text("FFT", weight=500),
                                                value="fft",
                                            ),
                                        ],
                                    ),
                                    dmc.TabsPanel(
                                        value="map",
                                        children=dmc.Card(
                                            dcc.Graph(
                                                className="p-0",
                                                id=ids.map_chart,
                                                style={"height": "35vh"},
                                            ),
                                            withBorder=True,
                                            style=TABS_CARD_STYLE,
                                            p=0,
                                            h="100%",
                                        ),
                                    ),
                                    dmc.TabsPanel(
                                        value="stats",
                                        children=dmc.Card(
                                            children=dmc.ScrollArea(
                                                id=ids.statsagg_card,
                                                h="100%",
                                                type="scroll",
                                            ),
                                            withBorder=True,
                                            style=TABS_CARD_STYLE,
                                            h="35vh",
                                        ),
                                    ),
                                    dmc.TabsPanel(
                                        value="fft",
                                        children=dmc.Card(
                                            dmc.CardSection(
                                                chart_loading_overlay(
                                                    [
                                                        dcc.Graph(
                                                            className="p-0",
                                                            id=ids.fft_chart,
                                                            responsive=True,
                                                            style={"height": "35vh"},
                                                            figure=empty_figure(),
                                                        )
                                                    ],
                                                    position="right",
                                                ),
                                            ),
                                            withBorder=True,
                                            style=TABS_CARD_STYLE,
                                            p=0,
                                        ),
                                    ),
                                ],
                            ),
                        ],
                    ),
                ],
            ),
        ],
        fluid=True,
    )


# update select modal
@callback(
    Output(ids.select_dataset_modal, "children"),
    Input(ids.select_dataset_modal, "opened"),
    State("traces_store", "data"),
)
def update_select_modal(is_open, data):
    if is_open:
        collected_traces = generate_viz_timeseries_select_modal_children(data)
        if len(collected_traces) == 0:
            collected_traces = [
                dmc.Alert(
                    children=dmc.Group(
                        [
                            dmc.Text(
                                "It looks like you have not collected any datasets yet."
                            ),
                            dmc.Anchor("Select Datasets", href=PATH_PREFIX + "select"),
                        ],
                        position="apart",
                    )
                )
            ]
        return dmc.Stack(
            [
                SearchableListAIO(items=collected_traces, height="60vh"),
                dmc.Group(
                    dmc.Anchor(
                        dmc.Button("Cancel", color="gray", variant="outline"),
                        href=PATH_PREFIX + "select",
                    ),
                    position="right",
                ),
            ]
        )
    return no_update


# update timerangeaio from url
@callback(
    Output(traio.ids.store_set(traio.aio_id), "data"),
    Input(ids.url, "pathname"),
    State(ids.url, "search"),
    Input(ids.main_chart, "relayoutData"),
    State(ids.main_chart_sync, "checked"),
)
def update_tr_store(pn, search_args, relayout_event, reload_enabled):
    if search_args is not None:
        query_args = qargs_to_dict(search_args)
        query_args_dr = [
            query_args.get("from", str(DEFAULT_TR_START.isoformat())),
            query_args.get("to", str(datetime.datetime.now().isoformat())),
        ]
        trg = ctx.triggered_id
        if trg == ids.main_chart:
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
    return no_update


# update search
@callback(
    Output(ids.url, "search"),
    Input(ids.agg_select, "value"),
    Input(ids.bucket_select, "value"),
    Input(ids.conf_select, "value"),
    Input(traio.ids.store(traio.aio_id), "modified_timestamp"),
    State(traio.ids.store(traio.aio_id), "data"),
    State(ids.url, "search"),
)
def update_url_location(af, tb, conf, dr_trg, dr, search_args):
    query_args = parse_nested_qargs(qargs_to_dict(search_args))

    if isinstance(dr, list) and dr[0] is not None and dr[1] is not None:
        dr_s = dr[0]
        dr_e = dr[1]
        query_args["agg"] = af
        query_args["bucket"] = tb
        query_args["from"] = dr_s
        query_args["to"] = dr_e
        if conf:
            query_args["confidence"] = conf

        return f"?{urlencode_dict(query_args)}"

    return no_update


# update title
@callback(Output(ids.title, "children"), Input(ids.url, "search"))
def update_title(search_args):
    query_args = parse_nested_qargs(qargs_to_dict(search_args))
    trace = query_args.get("trace")
    if trace is None:
        raise PreventUpdate

    return dataset_title(trace)


# update local trace store
@callback(
    Output(ids.store_ts_data, "data"),
    Input(ids.url, "search"),
)
def update_time_series_store(search_args):
    query_args = parse_nested_qargs(qargs_to_dict(search_args))
    if query_args.get("trace") is None:
        raise PreventUpdate
    if query_args.get("from") is None or query_args.get("to") is None:
        raise PreventUpdate
    cookies = flask.request.cookies
    auth_cookie = cookies.get("auth")
    if auth_cookie is None:
        raise PreventUpdate
    times, values = get_time_series_from_query_args(query_args, auth_cookie)
    return {"times": times, "values": values}


# update time of day store
@callback(
    Output(ids.store_tod_data, "data"),
    Input(ids.url, "search"),
    prevent_initial_call=True,
)
def update_tod_store(search_args):
    query_args = parse_nested_qargs(qargs_to_dict(search_args))
    if query_args.get("trace") is None:
        raise PreventUpdate
    if query_args.get("from") is None or query_args.get("to") is None:
        raise PreventUpdate
    cookies = flask.request.cookies
    auth_cookie = cookies.get("auth")
    if auth_cookie is None:
        raise PreventUpdate
    minutes_of_day, values = get_time_of_day_from_qargs(query_args, auth_cookie)
    return {"minutes_of_day": minutes_of_day, "values": values}


# update statsagg store
@callback(
    Output(ids.store_statsagg_data, "data"),
    Input(ids.url, "search"),
)
def update_statsagg_store(search_args):
    query_args = parse_nested_qargs(qargs_to_dict(search_args))
    trace = query_args.get("trace")
    if trace is None:
        raise PreventUpdate
    if query_args.get("from") is None or query_args.get("to") is None:
        raise PreventUpdate
    cookies = flask.request.cookies
    auth_cookie = cookies.get("auth")
    if auth_cookie is None:
        raise PreventUpdate
    statsagg = get_statsagg_from_qargs(query_args, auth_cookie)
    return statsagg


# update main chart
@callback(
    Output(ids.main_chart, "figure"),
    Input(ids.url, "search"),  # state --> duplicated execution?
    Input(ThemeSwitchAIO.ids.switch("theme"), "value"),
    Input(ids.main_chart_type, "value"),
    # Input(ids.store_ts_data, "modified_timestamp"),
    Input(ids.store_ts_data, "data"),
)
def update_time_series_chart(search_args, theme, chart_type, data):
    query_args = parse_nested_qargs(qargs_to_dict(search_args))
    if query_args.get("trace") is None or data is None:
        raise PreventUpdate
    if query_args.get("from") is None or query_args.get("to") is None:
        raise PreventUpdate

    times = data.get("times", [])
    values = data.get("values", [])
    time_from = query_args.get("from")
    time_to = query_args.get("to")
    return generate_ts_figure(
        times,
        values,
        time_from,
        time_to,
        theme,
        marker_color="#15AABF",
        chart_type=chart_type,
    )


# update tod chart
@callback(
    Output(ids.tod_chart, "figure"),
    Input(ThemeSwitchAIO.ids.switch("theme"), "value"),
    Input(ids.store_tod_data, "modified_timestamp"),
    State(ids.store_tod_data, "data"),
    Input(ids.tod_chart_type, "value"),
)
def update_time_series_chart(theme, ts, data, chart_type):
    if data is None:
        raise PreventUpdate

    minutes_of_day = data.get("minutes_of_day", [])
    values = data.get("values", [])
    return generate_time_of_day_scatter(
        minutes_of_day=minutes_of_day,
        values=values,
        light_mode=theme,
        marker_color="#15AABF",
        chart_type=chart_type,
    )


# update statsagg
@callback(
    Output(ids.statsagg_card, "children"),
    Input(ids.store_statsagg_data, "modified_timestamp"),
    State(ids.store_statsagg_data, "data"),
    Input(ids.tabs_selector, "value"),
    prevent_initial_call=True,
)
def update_statsagg_card(ts, data, tab):
    if data is None or "stats" not in tab:
        raise PreventUpdate
    return statsagg_table(data)


# update map plot
@callback(
    Output(ids.map_chart, "figure"),
    Input(ids.url, "search"),
    Input(ids.tabs_selector, "value"),
)
def update_map_plot(search_args, tab):
    if "map" not in tab:
        raise PreventUpdate
    if search_args is not None:
        query_args = parse_nested_qargs(qargs_to_dict(search_args))
        if query_args.get("trace") is None:
            raise PreventUpdate
        location_info = get_locations_from_qargs(query_args)
        return generate_scatter_map_plot(
            location_info.get("latitude"),
            location_info.get("longitude"),
            location_info.get("name"),
            location_info.get("id"),
        )
    raise PreventUpdate


# update fft
@callback(
    Output(ids.fft_chart, "figure"),
    Input(ids.url, "search"),  # state --> duplicated execution?
    Input(ThemeSwitchAIO.ids.switch("theme"), "value"),
    # Input(ids.store_ts_data, "modified_timestamp"),
    Input(ids.store_ts_data, "data"),
    Input(ids.tabs_selector, "value"),
)
def update_fft(search, theme, data, tab):
    if data is None or "fft" not in tab:
        raise PreventUpdate
    times = data.get("times")
    values = data.get("values")
    if isinstance(times, list) and isinstance(values, list):
        try:
            amplitude, periods = compute_fft(amplitude=values, times=times)
            binned_amplitude, seconds = create_fft_bins(amplitude, periods)
            return fft_single(
                amplitude=binned_amplitude, periods_s=seconds, light_mode=theme
            )
        except:
            return empty_figure()
    return empty_figure()


# update datasource indicator
@callback(
    Output(ids.datasource_indicator, "children"),
    Input(ids.url, "search"),
    State(ids.url, "pathname"),
)
def update_datasource(search, pn):
    if not "viz/timeseries" in pn or len(search) < 2:
        raise PreventUpdate
    query_args = parse_nested_qargs(qargs_to_dict(search))
    datasources = get_data_sources(UrlSearchArgs(**query_args))
    return datasource_indicator(datasources)


# share modal
@callback(
    Output(ids.share_modal_div, "children"),
    Input(ids.affix_share, "n_clicks"),
    State(ids.url, "search"),
    State(ids.url, "href"),
)
def share_modal(nc, search, href):
    return share_modal_callback(nc, search, href)


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
        return publish_annotation_callback(cookies, nc, search, pathname, data)
    raise PreventUpdate
