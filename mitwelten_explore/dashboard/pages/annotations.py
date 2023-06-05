import dash
import dash_mantine_components as dmc
from dash import dcc, callback, Input, Output, no_update, State, html, ALL, ctx
from dash.exceptions import PreventUpdate
import flask
from configuration import PATH_PREFIX
from dashboard.aio_components.aio_list_component import PagedListSearchableAIO
from dashboard.api_clients.userdata_client import (
    get_annotations,
    get_annotation,
    get_annotation_by_user,
    delete_annotation,
)
from dashboard.api_clients.taxonomy_client import get_taxon
from dashboard.models import UrlSearchArgs, to_typed_dataset, Annotation, DatasetType
from dashboard.styles import icons, get_icon
from dashboard.utils.communication import (
    parse_nested_qargs,
    qargs_to_dict,
    get_user_from_cookies,
)
from dashboard.utils.text_utils import beautify_timedelta, markdown_to_plain_text
import datetime
from uuid import uuid4

dash.register_page(__name__, path="/annotations")


class PageIds(object):
    url = str(uuid4())
    annot_container = str(uuid4())
    delete_annot_role = str(uuid4())
    modal_div = str(uuid4())
    confirm_delete_role = str(uuid4())


ids = PageIds()


def get_dataset_types(annot: Annotation):
    ds_types = []
    if annot.url is not None:
        if "?" in annot.url:
            search_args = annot.url.split("?")[1]
            args = UrlSearchArgs(**parse_nested_qargs(qargs_to_dict(search_args)))
            if args.datasets is not None:
                for ds in args.datasets:
                    ds_types.append(to_typed_dataset(ds).type)
            elif args.dataset is not None:
                ds_types.append(to_typed_dataset(args.dataset).type)
        if len(ds_types)==0:
            if annot.url.startswith("viz/taxon/"):
                ds_types.append(DatasetType.birds)
                #taxon_id = annot.url.split("viz/taxon/")[1].split("?")[0]
                #taxon = get_taxon(int(taxon_id))
                #ds_types.append(taxon.get_title())
    return ds_types


def get_dashboard_type(annot: Annotation):
    if annot.url is not None:
        if "?" in annot.url:
            pn = annot.url.split("?")[0]
            if "viz/" in pn:
                if pn.startswith("viz/taxon/"):
                    return "taxon"

                return pn.split("viz/")[1]
        return None


def get_dataset_time_range(annot: Annotation):
    if annot.url is not None:
        try:
            search_args = annot.url.split("?")[1]
            args = UrlSearchArgs(**parse_nested_qargs(qargs_to_dict(search_args)))
            time_from = args.view_config.time_from
            time_to = args.view_config.time_to
            return [
                time_from.strftime("%d.%m.%Y")
                if isinstance(time_from, datetime.datetime)
                else "any",
                time_to.strftime("%d.%m.%Y")
                if isinstance(time_to, datetime.datetime)
                else "any",
            ]
        except:
            return None
    return None


def get_annotation_list(annotations):
    if len(annotations) < 1:
        return [dmc.Alert("No Annotations found")]
    items = []
    for annot in annotations:
        timestamp = annot.timestamp
        time_diff = (
            datetime.datetime.now().astimezone(datetime.timezone.utc) - timestamp
        )
        content = markdown_to_plain_text(annot.md_content)

        items.append(
            dmc.Card(
                children=dmc.Anchor(
                    [
                        dmc.Container(
                            [
                                dmc.Tooltip(
                                    label=annot.user.full_name,
                                    position="right-start",
                                    color="indigo",
                                    offset=3,
                                    children=[
                                        dmc.Avatar(
                                            f"{annot.user.initials}",
                                            radius="xl",
                                            color="blue",
                                            m=4,
                                            mr=12,
                                        ),
                                        html.Div(annot.user.full_name, hidden=True),
                                        html.Div(annot.user.username, hidden=True),
                                    ],
                                ),
                                dmc.Stack(
                                    [
                                        dmc.Group(
                                            [
                                                dmc.Text(
                                                    annot.title,
                                                    weight=500,
                                                    size="lg",
                                                ),
                                                dmc.Group(
                                                    [
                                                        dmc.Text(
                                                            annot.time_str,
                                                            size="md",
                                                        ),
                                                        dmc.Badge(
                                                            beautify_timedelta(
                                                                time_diff
                                                            ),
                                                            color="teal",
                                                        ),
                                                    ]
                                                ),
                                            ],
                                            spacing="xl",
                                            position="apart",
                                        ),
                                        dmc.Grid(
                                            [
                                                dmc.Col(
                                                    [
                                                        dmc.Text(
                                                            content,
                                                            size="md",
                                                            lineClamp=2,
                                                        ),
                                                    ],
                                                    className="col-md-9",
                                                ),
                                                dmc.Col(
                                                    dmc.Group(
                                                        [
                                                            dmc.Badge(
                                                                get_dashboard_type(
                                                                    annot
                                                                )
                                                            ),
                                                        ]
                                                        + [
                                                            dmc.Badge(
                                                                ds_type,
                                                                variant="outline",
                                                            )
                                                            for ds_type in get_dataset_types(
                                                                annot
                                                            )
                                                        ],
                                                        style={"rowGap": 8},
                                                        spacing=8,
                                                        position="center",
                                                    ),
                                                    className="col-md-3",
                                                ),
                                            ]
                                        ),
                                    ],
                                    spacing=4,
                                    className="flex-grow-1",
                                ),
                            ],
                            fluid=True,
                            className="d-flex",
                            pl=4,
                            pr=12,
                        ),
                    ],
                    href=f"{PATH_PREFIX}annotations?annot_id={annot.id}",
                    variant="text",
                ),
                radius=0,
                px=0,
                py=12,
                withBorder=True,
                style={
                    "borderLeft": "0px",
                    "borderRight": "0px",
                    "borderTop": "0px",
                },
            )
        )
    return items


def annot_container(annot: Annotation, current_user_sub=None):
    ds_types = get_dataset_types(annot)
    time_range = get_dataset_time_range(annot)
    dashboard_time_range = (
        dmc.Text(f"{time_range[0]} - {time_range[1]}")
        if time_range is not None
        else None
    )

    delete_btn = None
    if current_user_sub == annot.user_sub:
        delete_btn = dmc.Button(
            color="red",
            children="Delete Annotation",
            id={"role": ids.delete_annot_role, "index": annot.id},
        )
    return dmc.Container(
        [
            dmc.Anchor(
                dmc.Group(
                    [
                        get_icon(icon=icons.arrow_back),
                        dmc.Text("Annotations", weight=500),
                    ]
                ),
                href=f"{PATH_PREFIX}annotations",
            ),
            dmc.Space(h=20),
            dmc.Container(
                [
                    dmc.Grid(
                        [
                            dmc.Col(
                                dmc.Card(
                                    [
                                        dmc.Text(annot.title, weight=700, size="2rem"),
                                        dmc.Space(h=2),
                                        dmc.Divider(),
                                        dmc.Space(h=6),
                                        dmc.Group(
                                            [
                                                dcc.Markdown(annot.md_content),
                                            ],
                                            noWrap=True,
                                        ),
                                    ],
                                    withBorder=True,
                                ),
                                className="col-md-9",
                            ),
                            dmc.Col(
                                [
                                    dmc.Card(
                                        [
                                            dmc.Stack(
                                                [
                                                    dmc.Stack(
                                                        [
                                                            dmc.Text(
                                                                "Author",
                                                                color="dimmed",
                                                                size="sm",
                                                            ),
                                                            dmc.Anchor(
                                                                [
                                                                    dmc.Group(
                                                                        [
                                                                            dmc.Avatar(
                                                                                annot.user.initials,
                                                                                radius="xl",
                                                                                color="blue",
                                                                            ),
                                                                            dmc.Stack(
                                                                                [
                                                                                    dmc.Text(
                                                                                        annot.user.username,
                                                                                        size="sm",
                                                                                        weight=500,
                                                                                    ),
                                                                                    dmc.Text(
                                                                                        annot.user.full_name,
                                                                                        size="sm",
                                                                                    ),
                                                                                ],
                                                                                spacing=0,
                                                                            ),
                                                                        ],
                                                                        spacing="xs",
                                                                    ),
                                                                ],
                                                                href=f"{PATH_PREFIX}annotations?q={annot.user.username}",
                                                                variant="text",
                                                            ),
                                                        ],
                                                        spacing=4,
                                                    ),
                                                    dmc.Stack(
                                                        [
                                                            dmc.Text(
                                                                "Created at",
                                                                color="dimmed",
                                                                size="sm",
                                                            ),
                                                            dmc.Text(
                                                                annot.time_str,
                                                                size="sm",
                                                            ),
                                                        ],
                                                        spacing=4,
                                                    ),
                                                    dmc.Stack(
                                                        [
                                                            dmc.Text(
                                                                "Dashboard Reference",
                                                                color="dimmed",
                                                                size="sm",
                                                            ),
                                                            dmc.Anchor(
                                                                dmc.Button(
                                                                    "Open Dashboard",
                                                                    color="teal",
                                                                    variant="outline",
                                                                    rightIcon=get_icon(
                                                                        icon=icons.open_in_new_tab
                                                                    ),
                                                                ),
                                                                target="_blank",
                                                                href=f"{PATH_PREFIX}{annot.url}",
                                                                variant="text",
                                                            ),
                                                        ],
                                                        spacing=4,
                                                    ),
                                                    dmc.Stack(
                                                        [
                                                            dmc.Text(
                                                                "Datasets",
                                                                color="dimmed",
                                                                size="sm",
                                                            ),
                                                            dmc.Group(
                                                                [
                                                                    dmc.Badge(
                                                                        t.value,
                                                                        variant="outline",
                                                                    )
                                                                    for t in ds_types
                                                                ],
                                                                spacing=8,
                                                                style={"rowGap": 8},
                                                            ),
                                                        ],
                                                        spacing=4,
                                                    ),
                                                    dmc.Stack(
                                                        [
                                                            dmc.Text(
                                                                "Dashboard Time Range",
                                                                color="dimmed",
                                                                size="sm",
                                                            ),
                                                            dashboard_time_range,
                                                        ],
                                                        spacing=4,
                                                    ),
                                                    dmc.Group(delete_btn),
                                                ]
                                            )
                                        ],
                                        withBorder=False,
                                        bg="transparent",
                                    )
                                ],
                                className="col-lg-3",
                            ),
                        ]
                    )
                ],
                # className="container-xl"
                fluid=True,
            ),
        ],
        fluid=True,
    )


annotation_skeleton = dmc.Card(
    children=dmc.Container(
        [
            dmc.Skeleton(height=38, circle=True, mr=12),
            dmc.Stack(
                [
                    dmc.Group(
                        [
                            dmc.Skeleton(height=18, width="30%"),
                            dmc.Skeleton(height=18, width="10%"),
                        ],
                        spacing="xl",
                        position="apart",
                    ),
                    dmc.Grid(
                        [
                            dmc.Col(
                                [
                                    dmc.Skeleton(height=32),
                                ],
                                className="col-md-9",
                            ),
                            dmc.Col(
                                dmc.Group(
                                    [
                                        dmc.Skeleton(height=18, width="20%"),
                                        dmc.Skeleton(height=18, width="20%"),
                                        dmc.Skeleton(height=18, width="20%"),
                                    ],
                                    spacing="md",
                                    position="center",
                                ),
                                className="col-md-3",
                            ),
                        ]
                    ),
                ],
                spacing=12,
                className="flex-grow-1",
            ),
        ],
        fluid=True,
        className="d-flex",
        pl=4,
        pr=12,
    ),
    radius=0,
    px=0,
    py=8,
)


plaio = PagedListSearchableAIO(
    items=[
        annotation_skeleton,
        dmc.Divider(),
        annotation_skeleton,
        dmc.Divider(),
        annotation_skeleton,
        dmc.Divider(),
        annotation_skeleton,
        dmc.Divider(),
        annotation_skeleton,
        dmc.Divider(),
        annotation_skeleton,
    ]
)


def layout(**kwargs):
    if "annot_id" in kwargs:
        return dmc.Container(
            [
                dcc.Location(id=ids.url, refresh=True),
                html.Div(id=ids.modal_div),
                dmc.Container(id=ids.annot_container, fluid=True),
            ],
            fluid=True,
        )  # annot_container(annot)

    return dmc.Container(
        fluid=True,
        children=[
            dcc.Location(id=ids.url, refresh=True),
            dmc.Group(
                [
                    dmc.Text("Annotations", weight=600 ,size="lg"),
                    dmc.Anchor(
                        get_icon(icons.help, width=18),
                        href=f"{PATH_PREFIX}docs#annotations",
                        variant="text",
                        target="_blank",
                    ),
                ],
                align="center",
            ),
            dmc.Space(h=12),
            plaio,
        ],
    )


@callback(
    Output(plaio.ids.store(plaio.aio_id), "data"),
    Input(ids.url, "search"),
    Input(ids.url, "href"),
)
def update_annotation_list(search, href):

    if "annot_id" in search:
        raise PreventUpdate
    cookies = flask.request.cookies

    if "my_annotations" in search:
        current_user = get_user_from_cookies(cookies)
        annotations = get_annotation_by_user(current_user.sub, cookies.get("auth"))
        return get_annotation_list(annotations)
    if "user" in search:
        qargs_dict = qargs_to_dict(search)
        if "user" in qargs_dict:
            annotations = get_annotation_by_user(
                qargs_dict.get("user"), cookies.get("auth")
            )
            return get_annotation_list(annotations)
    else:
        annotations = get_annotations(auth_cookie=cookies.get("auth"))
        return get_annotation_list(annotations)
    raise PreventUpdate


@callback(
    Output(plaio.ids.search_input_store(plaio.aio_id), "data"),
    Input(ids.url, "search"),
    Input(ids.url, "href"),
)
def update_pagedlist_search(search, href):
    if search is not None:
        if "q=" in search:
            qargs_dict = qargs_to_dict(search)
            if "q" in qargs_dict:
                return qargs_dict.get("q")
    raise PreventUpdate


@callback(
    Output(ids.annot_container, "children"),
    Input(ids.url, "search"),
    Input(ids.url, "href"),
)
def update_annotation_container(search, href):
    if search is None:
        raise PreventUpdate
    if not "annot_id" in search:
        raise PreventUpdate
    qargs_dict = qargs_to_dict(search)
    annot_id = qargs_dict.get("annot_id")
    if annot_id is None:
        raise PreventUpdate
    cookies = flask.request.cookies
    current_user = get_user_from_cookies(cookies)
    annot = get_annotation(int(annot_id), cookies.get("auth"))
    return annot_container(annot, current_user_sub=current_user.sub)


@callback(
    Output(ids.modal_div, "children"),
    Output(ids.url, "search"),
    Input({"role": ids.delete_annot_role, "index": ALL}, "n_clicks"),
    Input({"role": ids.confirm_delete_role, "index": ALL}, "n_clicks"),
    prevent_initial_call=True,
)
def open_delete_confirm_modal(nc, nc_conf):
    if ctx.triggered_id is not None:
        if ctx.triggered_id.get("role") == ids.delete_annot_role:
            if isinstance(nc, list) and len(nc) > 0 and nc[0] is not None:
                annot_id = ctx.triggered_id.get("index")
                if annot_id is not None:
                    return (
                        dmc.Modal(
                            [
                                dmc.Text(
                                    "Are you sure you want to delete this annotation?",
                                    pb=20,
                                ),
                                dmc.Group(
                                    dmc.Button(
                                        "Delete",
                                        color="red",
                                        id={
                                            "role": ids.confirm_delete_role,
                                            "index": annot_id,
                                        },
                                    ),
                                    position="right",
                                ),
                            ],
                            title="Confirm your action",
                            opened=True,
                        ),
                        no_update,
                    )
        if ctx.triggered_id.get("role") == ids.confirm_delete_role:
            if (
                isinstance(nc_conf, list)
                and len(nc_conf) > 0
                and nc_conf[0] is not None
            ):
                annot_id = ctx.triggered_id.get("index")
                if annot_id is not None:
                    delete_annotation(
                        annot_id=annot_id, auth_cookie=flask.request.cookies.get("auth")
                    )
                    return [], ""
    raise PreventUpdate
