from dash import dcc, html
import dash_mantine_components as dmc
from dashboard.styles import icons, get_icon
from dashboard.models import to_typed_dataset, DatasetType, UrlSearchArgs
from configuration import PATH_PREFIX
from dashboard.utils.communication import urlencode_dict


def loading_overlay(children, id=None, style=None, overlay_opacity=0.75, custom_spinner=None):
    """Show a loader on top of `children` while a callback updates them.

    Replaces the wrapper-style `dmc.LoadingOverlay` of DMC 0.12, which no longer
    takes children (DMC >= 0.14 only has a controlled `visible` overlay).
    `overlay_opacity` is the opacity of the white cover (0 = children stay fully visible).
    If `id` is given, it is set on an inner div so that callbacks can keep writing
    to `Output(id, "children")`.
    """
    if id is not None:
        children = html.Div(children, id=id)
    return dcc.Loading(
        children,
        parent_style={"position": "relative", **(style or {})},
        overlay_style={"visibility": "visible", "opacity": 1 - overlay_opacity}
        if overlay_opacity < 1
        else None,
        custom_spinner=custom_spinner if custom_spinner is not None else dmc.Loader(),
        delay_show=100,
    )


def chart_loading_overlay(children, position="left", style=None):
    return loading_overlay(
        children,
        style=style,
        overlay_opacity=0,
        custom_spinner=dmc.Card(
            dmc.Group(
                [
                    dmc.Loader(
                        size="sm",
                        color="teal.5",
                    ),
                    dmc.Text(
                        "Loading",
                        c="gray.9",
                        fw=500,
                        size="md",
                    ),
                ],
            ),
            style={
                "position": "absolute",
                "bottom": 10,
                position: 10,
                "backgroundColor": "rgba(245, 245, 245,0.8)",
            },
            py=3,
            px=5,
        ),
    )


def tooltip(
    children,
    text,
    position="left",
    floating=False,
    arrow=True,
    opendelay=100,
    color="indigo.9",
):
    if floating:
        return dmc.FloatingTooltip(
            children=children,
            label=text,
            position=position,
            color=color,
        )
    else:
        return dmc.Tooltip(
            children=children,
            label=dmc.Text(text, fw=300),
            position=position,
            withArrow=arrow,
            openDelay=opendelay,
            color=color,
        )


def datasource_indicator(datasources: dict, url_args: UrlSearchArgs = None):
    children = []
    titles = []

    for key in datasources.keys():
        titles.append(key)
        for ds in datasources[key]:
            children.append(
                dmc.Anchor(
                    dmc.Text(
                        [ds.get("name"), " ", get_icon(icons.open_in_new_tab)],
                        size="xs",
                    ),
                    href=ds.get("reference"),
                    target="_blank",
                )
            )
    original_records = None
    if url_args is not None:
        datasets = url_args.datasets
        if isinstance(datasets, list):
            for dataset_item in datasets:
                ds = to_typed_dataset(dataset_item)
                if ds.type == DatasetType.gbif_observations:
                    original_records = dmc.Anchor(
                        dmc.Text(
                            ["List of observations ", get_icon(icons.open_in_new_tab)],
                            fw=500,
                        ),
                        href=f"{PATH_PREFIX}reference/gbif?{urlencode_dict(dict(dataset=ds.to_dataset(), time_from=url_args.view_config.time_from,time_to=url_args.view_config.time_to))}",
                        target="_blank",
                    )

        elif isinstance(datasets, dict):
            ds = to_typed_dataset(datasets)
            if ds.type == DatasetType.gbif_observations:
                original_records = dmc.Anchor(
                    dmc.Text(
                        ["List of observations ", get_icon(icons.open_in_new_tab)],
                        fw=500,
                    ),
                    href=f"{PATH_PREFIX}reference/gbif?{urlencode_dict(dict(dataset=ds.to_dataset()))}",
                    target="_blank",
                )
        else:
            original_records = None
    else:
        original_records = None

    return dmc.HoverCard(
        withArrow=False,
        shadow="md",
        position="top-start",
        children=[
            dmc.HoverCardTarget(
                dmc.Group(
                    [
                        dmc.Group(
                            [
                                # get_icon(icons.copyright),
                                get_icon(icons.database),
                            ],
                            gap=1,
                        ),
                    ]
                    + [dmc.Text(" | ".join(titles), size="xs", c="dimmed")],
                    gap=4,
                    style={"cursor": "pointer"},
                )
            ),
            dmc.HoverCardDropdown(
                [
                    dmc.Group(
                        [dmc.Text("Data Sources", fw=500), original_records],
                        justify="space-between",
                    ),
                    dmc.Stack(
                        children,
                        gap=3,
                        style={
                            "maxHeight": "60vh",
                            "maxWidth": "50vw",
                            "overflowY": "auto",
                        },
                    ),
                ],
            ),
        ],
    )
