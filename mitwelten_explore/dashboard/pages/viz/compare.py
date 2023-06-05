import dash
from dash import dcc, callback, Input, Output, State, ALL, ctx, no_update, html
from dash.exceptions import PreventUpdate
from uuid import uuid4
import datetime
import time
import json
import flask
import dash_mantine_components as dmc

from dashboard.aio_components.aio_time_range_picker_component import TimeRangeAIO
from dashboard.aio_components.aio_texteditor_component import TextEditorAIO
from dashboard.components.navbar import ThemeSwitchAIO

from dashboard.utils.communication import (
    parse_nested_qargs,
    qargs_to_dict,
    urlencode_dict,
    get_user_from_cookies,
)
from dashboard.components.modals import (
    viz_compare_select_modal,
    generate_viz_compare_select_modal_children,
    dataset_config_modal,
    share_modal,
)
from dashboard.components.selects import time_bucket_select, agg_fcn_select
from dashboard.components.dataset_presentation import dataset_title
from dashboard.models import (
    UrlSearchArgs,
    to_typed_dataset,
    default_view_config,
    Annotation,
)
from dashboard.api_clients.userdata_client import post_annotation

from dashboard.data_handler import (
    load_ts_data,
    load_tod_data,
    load_map_data,
    load_statsagg_data,
)
from dashboard.components.cards import dataset_info_cards
from dashboard.charts.time_series_charts import (
    generate_multi_ts_figure,
    generate_multi_time_of_day_scatter,
)
from dashboard.charts.map_charts import (
    generate_empty_map,
    generate_multi_scatter_map_plot,
)
from dashboard.charts.analytic_charts import correlation_matrix_heatmap, fft_multi
from dashboard.components.chart_configuration import (
    timeseries_chart_config_menu,
    reload_control,
)
from dashboard.components.affix import affix_menu, affix_button
from dashboard.components.tables import statsagg_table
from dashboard.utils.ts import correlation_matrix, compute_fft, create_fft_bins
from dashboard.styles import MULTI_VIZ_COLORSCALE, icons


from configuration import PATH_PREFIX, DEFAULT_TR_START

dash.register_page(__name__, path_template="/viz/compare")


class PageIds(object):
    url = str(uuid4())
    select_modal = str(uuid4())
    modal_select_checkbox_role = str(uuid4())
    apply_selection_btn = str(uuid4())
    dataset_card_stack = str(uuid4())
    main_chart = str(uuid4())
    timebucket_select = str(uuid4())
    dataset_config_role = str(uuid4())
    config_modal_div = str(uuid4())
    config_modal = str(uuid4())
    apply_config_role = str(uuid4())
    confidence_select = str(uuid4())
    agg_select = str(uuid4())
    normalize_checkbox = str(uuid4())
    ts_store = str(uuid4())
    tod_store = str(uuid4())
    stats_store = str(uuid4())
    map_store = str(uuid4())
    main_chart_type = str(uuid4())
    main_chart_sync = str(uuid4())
    main_chart_layout_type = str(uuid4())
    stats_card = str(uuid4())
    tod_chart = str(uuid4())
    tod_chart_type = str(uuid4())
    tod_chart_layout = str(uuid4())
    map_chart = str(uuid4())
    affix_share = str(uuid4())
    affix_annotate = str(uuid4())
    share_modal_div = str(uuid4())
    corr_matrix_card = str(uuid4())
    fft_card = str(uuid4())


ids = PageIds()
traio = TimeRangeAIO()
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


def layout(**qargs):
    query_args = parse_nested_qargs(qargs)
    if len(query_args) == 0:

        return dmc.Container(
            [
                viz_compare_select_modal(id=ids.select_modal),
                dcc.Location(ids.url, refresh=True),
                dcc.Store(id=ids.tod_store),  # , storage_type="local"),
                dcc.Store(id=ids.ts_store),  # , storage_type="local"),
                dcc.Store(id=ids.stats_store),
                dcc.Store(id=ids.map_store, data=None),
            ],
        )
    args = UrlSearchArgs(**query_args)
    return dmc.Container(
        [
            dcc.Location(ids.url, refresh=False),
            dcc.Store(id=ids.ts_store),  # , storage_type="local"),
            dcc.Store(id=ids.tod_store),  # , storage_type="local"),
            dcc.Store(id=ids.stats_store),
            dcc.Store(id=ids.map_store),
            html.Div(id=ids.config_modal_div),
            html.Div(id=ids.share_modal_div),
            affix,
            annot_editor,
            dmc.Group(
                [
                    dmc.Text("Compare Datasets", weight=600),
                    dmc.Group(
                        [
                            time_bucket_select(
                                id=ids.timebucket_select,
                                value=args.view_config.bucket
                                if args.view_config.bucket
                                else "1d",
                            ),
                            traio,
                        ]
                    ),
                ],
                position="apart",
            ),
            dmc.Space(h=8),
            dmc.Card(
                [
                    dmc.CardSection(
                        [
                            dmc.Group(
                                [
                                    dmc.Text(
                                        "Time Series Chart",
                                        weight=500,
                                    ),
                                    dmc.Group(
                                        [
                                            reload_control(ids.main_chart_sync),
                                            timeseries_chart_config_menu(
                                                chart_type_id=ids.main_chart_type,
                                                # reload_on_zoom_id=ids.main_chart_sync,
                                                layout_type_id=ids.main_chart_layout_type,
                                                position="left-end",
                                            ),
                                        ]
                                    ),
                                ],
                                pl=4,
                                position="apart",
                            )
                        ]
                    ),
                    dmc.CardSection(
                        [
                            dmc.LoadingOverlay(
                                [
                                    dcc.Graph(
                                        id=ids.main_chart,
                                        style={
                                            "height": "42vh",
                                        },
                                        config=dict(
                                            displayModeBar=False,
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
                                ]
                            ),
                        ]
                    ),
                ],
                className="border-bottom",
                radius=0,
            ),
            dmc.Space(h=12),
            dmc.Grid(
                [
                    dmc.Col(
                        children=dmc.AccordionMultiple(
                            children=[
                                dmc.AccordionItem(
                                    [
                                        dmc.AccordionControl(
                                            dmc.Text("Time Of Day", weight=500)
                                        ),
                                        dmc.AccordionPanel(
                                            dmc.Card(
                                                dmc.CardSection(
                                                    [
                                                        dmc.Group(
                                                            timeseries_chart_config_menu(
                                                                chart_type_id=ids.tod_chart_type,
                                                                layout_type_id=ids.tod_chart_layout,
                                                                position="left-end",
                                                            ),
                                                            pl=2,
                                                            pt=2,
                                                            className="position-absolute",
                                                            style={
                                                                "zIndex": 1000,
                                                                "right": 0,
                                                            },
                                                            # position="right"
                                                        ),
                                                        dcc.Graph(
                                                            id=ids.tod_chart,
                                                            style={
                                                                "height": "30vh"
                                                            },  # "width":"50%"},
                                                            className="compare_tod_chart",
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
                                                    ]
                                                ),
                                            ),
                                            p=0,
                                        ),
                                    ],
                                    value="tod",
                                ),
                                dmc.AccordionItem(
                                    [
                                        dmc.AccordionControl(
                                            dmc.Text("Stats", weight=500)
                                        ),
                                        dmc.AccordionPanel(
                                            dmc.Card(
                                                id=ids.stats_card,
                                                withBorder=True,
                                            ),
                                        ),
                                    ],
                                    value="stats",
                                ),
                                dmc.AccordionItem(
                                    [
                                        dmc.AccordionControl(
                                            dmc.Text("Analysis", weight=500)
                                        ),
                                        dmc.AccordionPanel(
                                            dmc.Group(
                                                [
                                                    dmc.Card(
                                                        id=ids.corr_matrix_card,
                                                        withBorder=False,
                                                    ),
                                                    dmc.Card(
                                                        id=ids.fft_card,
                                                        withBorder=False,
                                                    ),
                                                ],
                                                grow=True,
                                            )
                                        ),
                                    ],
                                    value="calcs",
                                ),
                                dmc.AccordionItem(
                                    [
                                        dmc.AccordionControl(
                                            dmc.Text("Map", weight=500)
                                        ),
                                        dmc.AccordionPanel(
                                            dmc.Card(
                                                dcc.Graph(
                                                    figure=generate_empty_map(),
                                                    id=ids.map_chart,
                                                    className="p-0",
                                                    style={"height": "60vh"},
                                                ),
                                                p=0,
                                            ),
                                        ),
                                    ],
                                    value="map",
                                ),
                            ],
                            value=["tod"],
                            styles={
                                "control": {
                                    "padding": 4,
                                    "paddingTop": 4,
                                    "paddingBottom": 4,
                                },
                                "content": {
                                    "padding": 0,
                                },
                                "item": {
                                    "border": None,  # "5px solid red"
                                    "borderRadius": 0,
                                    "&[data-active]": {},
                                    "marginTop": "4px",
                                },
                            },
                        ),
                        className="col-lg-10",
                    ),
                    dmc.Col(
                        [
                            dmc.Text("Datasets", weight=500, px=4),
                            dmc.Stack(id=ids.dataset_card_stack, spacing="xs"),
                        ],
                        className="col-lg-2",
                    ),
                ],
                gutter="xs",
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
        collected_traces = generate_viz_compare_select_modal_children(
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
                            "Compare",
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
    if trg:
        n_selected = sum(checkboxes)
        checked_elements = [i for i, x in enumerate(checkboxes) if x]
        if trg == ids.apply_selection_btn:

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
            )  # initial_dataset_configs

        return (n_selected < 2) or (n_selected > 5), no_update  # , no_update
    return no_update, no_update  # , no_update


# update dataset cards
@callback(
    Output(ids.dataset_card_stack, "children"),
    Input(ids.url, "search"),
    Input(ids.url, "pathname"),
)
def update_dataset_cards(search, pn):
    if not "viz/compare" in pn:
        raise PreventUpdate
    args = UrlSearchArgs(**parse_nested_qargs(qargs_to_dict(search)))
    return dataset_info_cards(args=args, config_btn_role=ids.dataset_config_role)


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
                raise PreventUpdate
                # return query_args_dr

            if (
                relayout_event is not None
                and "xaxis.range[0]" in relayout_event
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
    Input(ids.timebucket_select, "value"),
    Input(traio.ids.store(traio.aio_id), "modified_timestamp"),
    State(traio.ids.store(traio.aio_id), "data"),
    State(ids.url, "search"),
)
def update_url_location(tb, dr_trg, dr, search_args):
    query_args = parse_nested_qargs(qargs_to_dict(search_args))

    if isinstance(dr, list) and dr[0] is not None and dr[1] is not None:
        dr_s = dr[0]
        dr_e = dr[1]
        query_args["bucket"] = tb
        query_args["from"] = dr_s
        query_args["to"] = dr_e

        return f"?{urlencode_dict(query_args)}"

    return no_update


# update ts_store
@callback(
    Output(ids.ts_store, "data"),
    Input(ids.url, "search"),
    Input(ids.url, "pathname"),
    State(ids.ts_store, "data"),
    prevent_initial_call=True,
)
def update_ts_store(search, pn, ts_data):
    if not "viz/compare" in pn:
        raise PreventUpdate
    args = UrlSearchArgs(**parse_nested_qargs(qargs_to_dict(search)))
    datasets = args.datasets
    if args.cfg is None:
        raise PreventUpdate
    configurations = [c.to_dict() for c in args.cfg]
    if ts_data is None:
        ts_data = [None for i in range(len(configurations))]

    cookies = flask.request.cookies
    auth_cookie = cookies.get("auth")

    for i in range(len(datasets)):

        times, values = load_ts_data(
            dataset=datasets[i],
            cfg=configurations[i],
            vc=args.view_config,
            auth_cookie=auth_cookie,
        )
        ts_data[i] = [times, values]
    correlation_matrix(ts_data)
    return ts_data


# update main chart
@callback(
    Output(ids.main_chart, "figure"),
    Input(ids.ts_store, "data"),
    Input(traio.ids.store(traio.aio_id), "data"),
    Input(ids.main_chart_type, "value"),
    Input(ids.main_chart_layout_type, "value"),
    Input(ThemeSwitchAIO.ids.switch("theme"), "value"),
)
def update_ts_chart(data, tr, chart_type, chart_layout, theme):
    if tr is None or data is None:
        raise PreventUpdate
    return generate_multi_ts_figure(
        data=data,
        date_from=tr[0],
        date_to=tr[1],
        light_mode=theme,
        chart_type=chart_type,
        layout_type=chart_layout,
    )


# update tod_store
@callback(
    Output(ids.tod_store, "data"),
    Input(ids.url, "search"),
    Input(ids.url, "pathname"),
    State(ids.tod_store, "data"),
    prevent_initial_call=True,
)
def update_tod_store(search, pn, tod_data):
    if not "viz/compare" in pn:
        raise PreventUpdate
    args = UrlSearchArgs(**parse_nested_qargs(qargs_to_dict(search)))
    datasets = args.datasets
    if args.cfg is None:
        raise PreventUpdate
    configurations = [c.to_dict() for c in args.cfg]
    if tod_data is None:
        tod_data = [None for i in range(len(configurations))]

    cookies = flask.request.cookies
    auth_cookie = cookies.get("auth")
    for i in range(len(datasets)):

        times, values = load_tod_data(
            dataset=datasets[i],
            cfg=configurations[i],
            vc=args.view_config,
            auth_cookie=auth_cookie,
        )
        tod_data[i] = [times, values]
    return tod_data


# update tod chart
@callback(
    Output(ids.tod_chart, "figure"),
    Input(ids.tod_store, "data"),
    Input(ids.tod_chart_layout, "value"),
    Input(ids.tod_chart_type, "value"),
    Input(ThemeSwitchAIO.ids.switch("theme"), "value"),
)
def update_ts_chart(data, chart_layout, chart_type, theme):
    if data is None:
        raise PreventUpdate
    return generate_multi_time_of_day_scatter(
        data=data, light_mode=theme, layout_type=chart_layout, chart_type=chart_type
    )


# update statsagg_store
@callback(
    Output(ids.stats_store, "data"),
    Input(ids.url, "search"),
    Input(ids.url, "pathname"),
    prevent_initial_call=True,
)
def update_stats_store(search, pn):
    if not "viz/compare" in pn:
        raise PreventUpdate
    args = UrlSearchArgs(**parse_nested_qargs(qargs_to_dict(search)))
    datasets = args.datasets
    if args.cfg is None:
        raise PreventUpdate
    configurations = [c.to_dict() for c in args.cfg]
    stats_data = []
    cookies = flask.request.cookies
    auth_cookie = cookies.get("auth")
    for i in range(len(datasets)):

        stats_dict = load_statsagg_data(
            dataset=datasets[i],
            cfg=configurations[i],
            vc=args.view_config,
            auth_cookie=auth_cookie,
        )
        stats_data.append(stats_dict)
    return stats_data


# update map_store
@callback(
    Output(ids.map_store, "data"),
    Input(ids.url, "search"),
    Input(ids.url, "pathname"),
    State(ids.map_store, "data"),
    prevent_initial_call=True,
)
def update_map_store(search, pn, map_data):
    if not "viz/compare" in pn:
        raise PreventUpdate
    args = UrlSearchArgs(**parse_nested_qargs(qargs_to_dict(search)))
    datasets = args.datasets
    if args.cfg is None:
        raise PreventUpdate
    configurations = [c.to_dict() for c in args.cfg]
    if map_data is None:
        map_data = []
    map_data = []

    cookies = flask.request.cookies
    auth_cookie = cookies.get("auth")
    for i in range(len(datasets)):

        location_data = load_map_data(
            dataset=datasets[i],
            cfg=configurations[i],
            vc=args.view_config,
            auth_cookie=auth_cookie,
        )
        map_data.append(location_data)
    return map_data


# update map chart
@callback(
    Output(ids.map_chart, "figure"),
    Input(ids.map_store, "data"),
)
def update_ts_chart(data):
    if data is None or len(data) == 0:
        raise PreventUpdate
    return generate_multi_scatter_map_plot(
        data=data,
    )


# update analysis
@callback(
    Output(ids.corr_matrix_card, "children"),
    Output(ids.fft_card, "children"),
    Input(ids.ts_store, "data"),
    Input(ids.url, "search"),
    Input(ids.url, "pathname"),
    Input(ThemeSwitchAIO.ids.switch("theme"), "value"),
)
def update_analysis(data, search, pn, theme):
    if data is None:
        raise PreventUpdate
    if not "viz/compare" in pn or len(search) < 2:
        raise PreventUpdate
    args = UrlSearchArgs(**parse_nested_qargs(qargs_to_dict(search)))

    datasets = [to_typed_dataset(ds) for ds in args.datasets]
    labels = [d.get_title() for d in datasets]
    matrix = correlation_matrix(data)
    ffts = []
    t0 = time.time()
    values = []
    seconds = []
    for d in data:
        if len(d[1]) > 24 and len(d[0]) > 24:
            try:
                fft, periods = compute_fft(amplitude=d[1], times=d[0])
                values, seconds = create_fft_bins(fft, periods)
                ffts.append([seconds, values])
            except:
                ffts.append([[0], [None]])

        else:
            ffts.append([[0], [None]])
    return dcc.Graph(
        figure=correlation_matrix_heatmap(matrix, labels, light_mode=theme),
        config=dict(
            displayModeBar=False,
        ),
    ), dcc.Graph(
        figure=fft_multi(ffts, dataset_names=labels, light_mode=theme),
        config=dict(
            displayModeBar=False,
        ),
    )


# update stats
@callback(
    Output(ids.stats_card, "children"),
    Input(ids.stats_store, "data"),
    Input(ids.url, "search"),
    Input(ids.url, "pathname"),
)
def update_stats(data, search, pn):
    if data is None or search is None:
        raise PreventUpdate
    if not "viz/compare" in pn:
        raise PreventUpdate
    if len(search) < 1:
        raise PreventUpdate
    args = UrlSearchArgs(**parse_nested_qargs(qargs_to_dict(search)))

    datasets = [to_typed_dataset(ds) for ds in args.datasets]

    entries = []
    for i in range(len(data)):
        title, sp, table = statsagg_table(data[i])
        entries.append(
            dmc.Card(
                children=[
                    dmc.ScrollArea(
                        [
                            dmc.Text(
                                size="sm",
                                className="text-nowrap",
                                children=datasets[i].get_title(),
                            ),
                            dmc.Space(h=12),
                        ]
                    ),
                    table,
                ],
                withBorder=True,
                style={
                    "border": f"1px solid {MULTI_VIZ_COLORSCALE[i]}",
                    "borderTop": f"6px solid {MULTI_VIZ_COLORSCALE[i]}",
                },
            )
        )
    return dmc.Group(entries, grow=True, align="start")


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
            normalize_id=ids.normalize_checkbox,
        )
    raise PreventUpdate


# apply config and close modal
@callback(
    Output(ids.url, "search", allow_duplicate=True),
    Output(ids.config_modal, "opened"),
    Input({"role": ids.apply_config_role, "index": ALL}, "n_clicks"),
    State(ids.confidence_select, "value"),
    State(ids.agg_select, "value"),
    State(ids.normalize_checkbox, "checked"),
    State(ids.url, "search"),
    prevent_initial_call=True,
)
def apply_dataset_configuration(apply_btns, confidence, agg, norm, search):
    if any(apply_btns):
        dataset_index = ctx.triggered_id.get("index")
        new_cfg = {}
        if confidence:
            new_cfg["confidence"] = confidence
        if agg:
            new_cfg["agg"] = agg
        if norm:
            new_cfg["normalize"] = True
        else:
            new_cfg["normalize"] = False

        query_args = parse_nested_qargs(qargs_to_dict(search))

        query_args["cfg"][dataset_index] = new_cfg
        # query_args["cfg"] = initial_dataset_configs

        # return no_update, f"?{urlencode_dict(query_args)}"
        return f"?{urlencode_dict(query_args)}", False
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
