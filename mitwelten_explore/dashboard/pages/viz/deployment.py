import dash
from dash import dcc, callback, Input, Output, State, ctx, html, no_update, ALL
from dash.exceptions import PreventUpdate
import flask
import dash_mantine_components as dmc
from dashboard.models import UrlSearchArgs, to_typed_dataset, Annotation, DatasetType
from dashboard.styles import icons, get_icon
from dashboard.components.navbar import ThemeSwitchAIO
from uuid import uuid4
from dashboard.aio_components.aio_time_range_picker_component import TimeRangeAIO
from dashboard.aio_components.aio_list_component import (
    PagedListSearchableAIO,
    SearchableListAIO,
)
from dashboard.aio_components.aio_texteditor_component import TextEditorAIO
from dashboard.components.overlays import chart_loading_overlay, datasource_indicator
from dashboard.api_clients.bird_results_client import get_detection_list_by_deployment
from dashboard.api_clients.pollinator_results_client import (
    get_polli_detection_list_by_deployment,
)
from dashboard.api_clients.deployments_client import (
    get_daily_image_captures,
    get_daily_audio_duration,
)
from dashboard.api_clients.environment_entries_client import (
    get_environment_entries_nearby,
    get_legend,
)
from dashboard.components.selects import confidence_threshold_select
from dashboard.components.labels import badge_de, badge_en
from dashboard.components.dataset_presentation import dataset_title
from dashboard.components.modals import (
    viz_single_dataset_select_modal,
    generate_viz_deployment_select_modal_children,
)
from dashboard.common_callbacks import share_modal_callback, publish_annotation_callback

from dashboard.components.affix import affix_menu, affix_button, datasource_affix
from configuration import PATH_PREFIX, DEFAULT_CONFIDENCE, DEFAULT_TR_START
from dashboard.charts.basic_charts import pie_chart, no_data_figure, spider_chart
from dashboard.charts.map_charts import (
    generate_empty_map,
    deployment_location_map,
)
from dashboard.charts.time_series_charts import data_collection_bar_chart
from dashboard.data_handler import get_locations_from_qargs, get_data_sources
from dashboard.utils.communication import (
    parse_nested_qargs,
    qargs_to_dict,
    urlencode_dict,
    get_user_from_cookies,
)
import numpy as np
import datetime


class SpeciesListItem:
    def __init__(
        self,
        datum_id=None,
        label_sci=None,
        count=None,
        label_de=None,
        label_en=None,
        **kwargs,
    ):
        self.datum_id = datum_id
        self.label_sci = label_sci
        self.count = count
        self.label_de = label_de
        self.label_en = label_en
        if "class" in kwargs:
            self.label_de = kwargs.get("class")
            self.label_sci = kwargs.get("class")


class PageIds(object):
    url = str(uuid4())
    conf_select = str(uuid4())
    pie_chart = str(uuid4())
    map = str(uuid4())
    select_modal = str(uuid4())
    detection_stats_group = str(uuid4())
    data_stats_indicator = str(uuid4())
    affix_share = str(uuid4())
    affix_annotate = str(uuid4())
    datasource_indicator = str(uuid4())
    share_modal_div = str(uuid4())
    spider_chart = str(uuid4())
    data_bar_chart = str(uuid4())


ids = PageIds()
traio = TimeRangeAIO(dates=[None, None])
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

plaio_legend = dmc.Grid(
    [
        dmc.Col(
            dmc.Text("Detections", size="sm"),
            span=2,
        ),
        dmc.Col(
            dmc.Text("Name", size="sm"),
            span=8,
        ),
        dmc.Col(
            dmc.Group(
                dmc.Text(
                    "Dashboard",
                    weight=400,
                    size="sm",
                ),
                position="right",
            ),
            span=2,
        ),
    ],
)


def value_indicator_group(value, text):
    return dmc.Group(
        [
            dmc.Text(
                value,
                size="1.5rem",
                color="teal.5",
                weight=600,
            ),
            dmc.Text(
                text,
                size="md",
            ),
        ],
        spacing="xs",
        p=0,
    )


plaio = PagedListSearchableAIO(
    height="85vh",
    items_per_page=30,
    use_loadingoverlay=False,
    items=[dmc.Skeleton(width="100%", height=30)] * 10,  # get_dataset_list(),
    legend=plaio_legend,
)


def generate_list_items(species):
    if len(species) == 0:
        return []
    max_count_norm = max([np.sqrt(s.count) for s in species])

    items = []
    for s in species:
        normalized_count = np.sqrt(s.count)
        count_percent = (normalized_count / max_count_norm) * 100
        label_de = (
            dmc.Group([badge_de, dmc.Text(s.label_de, size="sm")], spacing=3)
            if s.label_de
            else None
        )
        label_en = (
            dmc.Group([badge_en, dmc.Text(s.label_en, size="sm")], spacing=3)
            if s.label_en
            else None
        )
        items.append(
            dmc.Card(
                dmc.Grid(
                    [
                        dmc.Col(
                            [
                                dmc.Text(
                                    s.count,
                                    weight=600,
                                ),
                                dmc.Progress(
                                    value=count_percent,
                                    size="md",
                                    color="teal.6",
                                    className="bg-transparent",
                                    radius=0,
                                ),
                            ],
                            span=2,
                        ),
                        dmc.Col(
                            dmc.Group(
                                [
                                    dmc.Text(s.label_sci, weight=500),
                                    label_de,
                                    label_en,
                                ],
                                style={"rowGap": 2},
                            ),
                            span=9,
                        ),
                        dmc.Col(
                            dmc.Group(
                                dmc.Anchor(
                                    dmc.Button(
                                        get_icon(icon=icons.dashboard, width=24),
                                        color="teal.6",
                                        variant="subtle",
                                        p=4,
                                    ),
                                    href=f"{PATH_PREFIX}viz/taxon/{s.datum_id}?mw_data=true",
                                    target="_blank",
                                ),
                                position="right",
                            ),
                            span=1,
                        ),
                    ]
                ),
                withBorder=True,
                p=4,
                radius=0,
                style={
                    "borderTop": "0px",
                    "borderLeft": "0px",
                    "borderRight": "0px",
                },
                className="bg-transparent",
            )
        )
    return items


dash.register_page(__name__, path_template="/viz/deployment")


def layout(**qargs):
    query_args = parse_nested_qargs(qargs)
    args = UrlSearchArgs(**query_args)
    if args.dataset is None:
        return dmc.Container(
            [
                viz_single_dataset_select_modal(
                    True,
                    id=ids.select_modal,
                ),
                dcc.Location(ids.url, refresh=True),
            ],
        )

    conf_select = confidence_threshold_select(
        id=ids.conf_select, value=args.view_config.confidence
    )
    title = dataset_title(args.dataset)

    return dmc.Container(
        [
            dcc.Location(id=ids.url, refresh=False),
            html.Div(id=ids.share_modal_div),
            annot_editor,
            datasource_affix(ids.datasource_indicator),
            affix,
            dmc.Group(
                [
                    title,
                    dmc.Group([conf_select, traio]),
                ],
                position="apart",
                pb=12,
            ),
            dmc.Grid(
                [
                    dmc.Col(
                        [
                            dmc.AccordionMultiple(
                                [
                                    dmc.AccordionItem(
                                        [
                                            dmc.AccordionControl(
                                                dmc.Text(
                                                    "Detections", weight=500, size="sm"
                                                ),
                                                py=8,
                                            ),
                                            dmc.AccordionPanel(
                                                [
                                                    dmc.Group(
                                                        id=ids.detection_stats_group,
                                                        position="center",
                                                        p=0,
                                                    ),
                                                    dmc.LoadingOverlay(
                                                        dcc.Graph(
                                                            id=ids.pie_chart,
                                                            figure=no_data_figure(
                                                                annotation=""
                                                            ),
                                                            config=dict(
                                                                displayModeBar=False,
                                                            ),
                                                        ),
                                                        transitionDuration=400,
                                                    ),
                                                ]
                                            ),
                                        ],
                                        value="detections",
                                        className="bg-transparent",
                                    ),
                                    dmc.AccordionItem(
                                        [
                                            dmc.AccordionControl(
                                                dmc.Text("Map", weight=500, size="sm"),
                                                py=8,
                                            ),
                                            dmc.AccordionPanel(
                                                dcc.Graph(
                                                    id=ids.map,
                                                    figure=generate_empty_map(),
                                                    config=dict(
                                                        displayModeBar=False,
                                                    ),
                                                ),
                                            ),
                                        ],
                                        value="map",
                                        className="bg-transparent",
                                    ),
                                    dmc.AccordionItem(
                                        [
                                            dmc.AccordionControl(
                                                dmc.Text(
                                                    "Collected data",
                                                    weight=500,
                                                    size="sm",
                                                ),
                                                py=8,
                                            ),
                                            dmc.AccordionPanel(
                                                [
                                                    dmc.Group(
                                                        id=ids.data_stats_indicator,
                                                        position="center",
                                                    ),
                                                    dmc.LoadingOverlay(
                                                        dcc.Graph(
                                                            id=ids.data_bar_chart,
                                                            figure=no_data_figure(
                                                                annotation=""
                                                            ),
                                                            config=dict(
                                                                displayModeBar=False,
                                                            ),
                                                        ),
                                                        transitionDuration=400,
                                                    ),
                                                ]
                                            ),
                                        ],
                                        value="statistics",
                                        className="bg-transparent",
                                    ),
                                    dmc.AccordionItem(
                                        [
                                            dmc.AccordionControl(
                                                dmc.Text(
                                                    "Environment",
                                                    weight=500,
                                                    size="sm",
                                                ),
                                                py=8,
                                            ),
                                            dmc.AccordionPanel(
                                                dcc.Graph(
                                                    id=ids.spider_chart,
                                                    config=dict(
                                                        displayModeBar=False,
                                                    ),
                                                )
                                            ),
                                        ],
                                        value="environment",
                                        className="bg-transparent",
                                    ),
                                ],
                                variant="contained",
                                value=["detections"],
                                # value="detections",
                                styles={"content": {"padding": 0}},
                            ),
                        ],
                        className="col-lg-5",
                    ),
                    dmc.Col(
                        dmc.LoadingOverlay(plaio, transitionDuration=400),
                        className="col-lg-7",
                    ),
                ],
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
    Input(ids.conf_select, "value"),
    Input(traio.ids.store(traio.aio_id), "modified_timestamp"),
    State(traio.ids.store(traio.aio_id), "data"),
    State(ids.url, "search"),
)
def update_url_location(conf, dr_trg, dr, search_args):
    query_args = parse_nested_qargs(qargs_to_dict(search_args))

    if isinstance(dr, list) and dr[0] is not None and dr[1] is not None:
        dr_s = dr[0]
        dr_e = dr[1]
        query_args["from"] = dr_s
        query_args["to"] = dr_e
        if conf:
            query_args["confidence"] = conf

        return f"?{urlencode_dict(query_args)}"

    return no_update


# update select modal
@callback(
    Output(ids.select_modal, "children"),
    Input(ids.select_modal, "opened"),
    State("traces_store", "data"),
)
def update_select_modal(is_open, data):
    if is_open:
        collected_traces = generate_viz_deployment_select_modal_children(data)
        if len(collected_traces) == 0:
            collected_traces = [
                dmc.Alert(
                    children=dmc.Group(
                        [
                            dmc.Text(
                                "It looks like you have not collected any bird datasets yet."
                            ),
                            dmc.Anchor(
                                "Select Datasets", href=PATH_PREFIX + "select/bird"
                            ),
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


# update result list
@callback(
    Output(plaio.ids.store(plaio.aio_id), "data"),
    Output(ids.pie_chart, "figure"),
    Output(ids.detection_stats_group, "children"),
    Input(ids.url, "href"),
    Input(ids.url, "search"),
    Input(ThemeSwitchAIO.ids.switch("theme"), "value"),
)
def update_list(href, search, theme):

    query_args = UrlSearchArgs(**parse_nested_qargs(qargs_to_dict(search)))
    if (
        query_args.dataset is None
        or query_args.view_config.time_from is None
        or query_args.view_config.time_to is None
    ):
        raise PreventUpdate
    ds = to_typed_dataset(query_args.dataset)
    if ds.type == DatasetType.distinct_species:
        data = get_detection_list_by_deployment(
            confidence=query_args.view_config.confidence,
            deployment_ids=ds.deployment_id,
            time_from=query_args.view_config.time_from,
            time_to=query_args.view_config.time_to,
        )
        species = [SpeciesListItem(**d) for d in data]
    elif ds.type == DatasetType.pollinators:
        data = get_polli_detection_list_by_deployment(
            confidence=query_args.view_config.confidence,
            deployment_ids=ds.deployment_id,
            time_from=query_args.view_config.time_from,
            time_to=query_args.view_config.time_to,
        )
        species = [SpeciesListItem(**d) for d in data]
    else:
        species = []
    return (
        generate_list_items(species),
        pie_chart([s.label_sci for s in species], [s.count for s in species], theme),
        [
            value_indicator_group(f"{len(data)}", "Species"),
            value_indicator_group(
                f"{sum([s.count for s in species]):,}".replace(",", "'"), "Detections"
            ),
        ],
    )


# update map plot
@callback(
    Output(ids.map, "figure"),
    Output(ids.spider_chart, "figure"),
    State(ids.url, "search"),
    Input(ThemeSwitchAIO.ids.switch("theme"), "value"),
)
def update_map_plot(search_args, theme):
    if search_args is not None:
        query_args = parse_nested_qargs(qargs_to_dict(search_args))
        if query_args.get("dataset") is None:
            raise PreventUpdate
        location_info = get_locations_from_qargs(query_args)
        lats = location_info.get("latitude")
        lons = location_info.get("longitude")
        names = location_info.get("name")
        deployment_ids = location_info.get("id")

        if isinstance(lats, list):
            if len(lats) == 0:
                raise PreventUpdate
            elif len(lats) == 1:
                mean_lats = lats[0]
                mean_lons = lons[0]
            else:

                mean_lats = np.mean(lats)
                mean_lons = np.mean(lons)
            legend = get_legend()
            entries = get_environment_entries_nearby(
                lat=mean_lats, lon=mean_lons, limit=3
            )
            if entries is not None:
                labels = [l.get("label") for l in legend.values()]
                keys = list(legend.keys())
                spider = spider_chart(labels, keys, entries, theme)
                elats = [e.get("location").get("lat") for e in entries]
                elons = [e.get("location").get("lon") for e in entries]
                eids = [e.get("environment_id") for e in entries]
                map = deployment_location_map(
                    lats, lons, deployment_ids, elats=elats, elons=elons, enames=eids
                )
            else:
                spider = no_data_figure(
                    annotation="No measurements nearby", light_mode=theme
                )

        else:
            spider = no_data_figure(
                annotation="No measurements nearby", light_mode=theme
            )
            map = deployment_location_map(lats, lons, deployment_ids)

        return map, spider


# update data acquisition chart
@callback(
    Output(ids.data_bar_chart, "figure"),
    Output(ids.data_stats_indicator, "children"),
    Input(ids.url, "search"),
    Input(ids.url, "href"),
    Input(ThemeSwitchAIO.ids.switch("theme"), "value"),
)
def update_bar_chart(search, href, theme):
    if search is not None:
        query_args = UrlSearchArgs(**parse_nested_qargs(qargs_to_dict(search)))
        if query_args.dataset is None:
            raise PreventUpdate
        ds = to_typed_dataset(query_args.dataset)
        if ds.type == DatasetType.distinct_species:
            durations = get_daily_audio_duration(
                ds.deployment_id,
                time_from=query_args.view_config.time_from,
                time_to=query_args.view_config.time_to,
            )
            if isinstance(durations, list):
                times = [d.get("bucket") for d in durations]
                values_s = [d.get("recording_seconds") for d in durations]
                total_duration = sum(values_s)
                td = (
                    datetime.timedelta(seconds=total_duration)
                    if total_duration is not None
                    else 0
                )
                values = [d / 3600 for d in values_s]
                return data_collection_bar_chart(
                    times,
                    values,
                    title="Recording duration per day",
                    unit="h",
                    light_mode=theme,
                ), value_indicator_group(f"{td}", "Total recording time")

        elif ds.type == DatasetType.pollinators:
            images = get_daily_image_captures(
                ds.deployment_id,
                time_from=query_args.view_config.time_from,
                time_to=query_args.view_config.time_to,
            )
            if isinstance(images, list):
                times = [i.get("bucket") for i in images]
                values = [i.get("image_count") for i in images]
                total_images = sum(values) if values is not None else 0
                return data_collection_bar_chart(
                    times,
                    values,
                    title="Images per day",
                    unit="captures",
                    light_mode=theme,
                ), value_indicator_group(
                    f"{total_images:,}".replace(",", "'"), "Captured images"
                )
    raise PreventUpdate


# update datasource indicator
@callback(
    Output(ids.datasource_indicator, "children"),
    Input(ids.url, "search"),
    State(ids.url, "pathname"),
)
def update_datasource(search, pn):
    if not "viz/deployment" in pn or len(search) < 2:
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
