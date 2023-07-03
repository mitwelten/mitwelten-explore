import dash_mantine_components as dmc
from dash import dcc
from dashboard.api_clients.taxonomy_client import get_parent_taxonomy
from dashboard.styles import icons, MULTI_VIZ_COLORSCALE, get_icon
from dashboard.components.labels import badge_de, badge_en
from dashboard.api_clients.third_party_clients import (
    generate_wiki_link,
    get_wiki_summary,
    generate_image_attribution,
)
from dashboard.models import UrlSearchArgs, to_typed_dataset
from configuration import PATH_PREFIX
from dashboard.utils.text_utils import format_datetime
from dashboard.charts.map_charts import generate_scatter_map_plot


def taxon_stat_card(total_det_id, n_deployments_id):
    return dmc.Card(
        children=dmc.Group(
            [
                dmc.Stack(
                    [
                        dmc.LoadingOverlay(
                            dmc.Text(
                                id=total_det_id,
                                size=32,
                                weight=700,
                                color="teal.6",
                            )
                        ),
                        dmc.Text("Total Detections", size="md"),
                    ],
                    spacing=1,
                    justify="space-between",
                ),
                dmc.Stack(
                    [
                        dmc.Text(
                            id=n_deployments_id,
                            size=32,
                            weight=700,
                            color="teal.6",
                        ),
                        dmc.Text("Deployments", size="md"),
                    ],
                    spacing=1,
                    justify="space-between",
                ),
            ],
            position="apart",
            align="start",
        ),
        withBorder=True,
        shadow="sm",
    )


def taxon_viz_info_card(taxon_id):
    taxon_tree = get_parent_taxonomy(taxon_key=taxon_id)
    taxon_tree.sort()
    selected_taxon = min(taxon_tree)
    rank_badges = []
    parent_taxons = taxon_tree[1:]
    parent_taxons.reverse()
    for i in range(len(parent_taxons)):
        arrow = get_icon(icon=icons.arrow_subdir) if i > 0 else None
        space = dmc.Space(w=(i - 1) * 12) if i > 1 else None
        rank_badges.append(
            dmc.Group(
                [
                    space,
                    arrow,
                    dmc.Anchor(
                        dmc.Badge(
                            dmc.Group(
                                [
                                    dmc.Badge(
                                        parent_taxons[i].rank[0],
                                        radius=0,
                                        variant="filled",
                                        color="teal.9",
                                        size="md",
                                    ),
                                    dmc.Text(parent_taxons[i].label_sci),
                                ]
                            ),
                            radius="xs",
                            variant="outline",
                            pl=0,
                            color="teal.9",
                            size="md",
                        ),
                        href=f"{PATH_PREFIX}viz/taxon/{parent_taxons[i].datum_id}",
                    ),
                ],
                spacing=0,
            )
        )

    label_de = (
        dmc.Group([badge_de, dmc.Text(selected_taxon.label_de)], spacing=3)
        if selected_taxon.label_de
        else None
    )
    label_en = (
        dmc.Group([badge_en, dmc.Text(selected_taxon.label_en)], spacing=3)
        if selected_taxon.label_en
        else None
    )
    rank_badge = dmc.Badge(
        selected_taxon.rank,
        radius="xs",
        color="gray",
        variant="outline",
    )
    summary = get_wiki_summary(selected_taxon.label_sci, char_limit=800, lang="en")
    extract = summary.get("extract")
    if extract is not None:
        extract += " *[Wikipedia]({})*".format(
            generate_wiki_link(selected_taxon.label_sci)
        )

    return dmc.Card(
        [
            dmc.Text(selected_taxon.label_sci, weight=700, size="lg"),
            dmc.Group(
                [
                    label_de,
                    label_en,
                ]
            ),
            dmc.Space(h=8),
            dmc.Tabs(
                [
                    dmc.TabsList(
                        [
                            dmc.Tab("Image", value="image"),
                            dmc.Tab("Taxonomy", value="taxonomy"),
                            dmc.Tab("Description", value="description"),
                        ]
                    ),
                    dmc.Space(h=16),
                    dmc.TabsPanel(
                        dmc.Stack(
                            [
                                dmc.Image(
                                    src=selected_taxon.image_url,
                                    fit="contain",
                                    radius="md",
                                ),
                                dcc.Markdown(
                                    generate_image_attribution(
                                        selected_taxon.image_url
                                    ),
                                    link_target="_blank",
                                    style={
                                        "fontSize": "0.8rem",
                                    },
                                ),
                            ],
                            spacing=0,
                        ),
                        value="image",
                    ),
                    dmc.TabsPanel(
                        dmc.Stack(rank_badges, spacing="sm", align="flex-start"),
                        value="taxonomy",
                    ),
                    dmc.TabsPanel(
                        dcc.Markdown(
                            extract,
                            className="lh-md",
                            link_target="_blank",
                            style={
                                "fontFamily": "Times New Roman",
                                "fontSize": "16px",
                            },
                        ),
                        value="description",
                    ),
                ],
                color="teal.6",
                value="image",
            ),
        ],
        withBorder=True,
        shadow="sm",
    )


def dataset_info_card(
    args: UrlSearchArgs,
    index,
    config_btn_role,
    visible_btn_id,
    trace_icon=icons.hexagon_filled,
    icon_color="gray",
):
    if args.datasets is None or args.cfg is None:
        return None
    if len(args.datasets) < index - 1:
        return None
    if not len(args.datasets) == len(args.cfg):
        return None
    ds = to_typed_dataset(args.datasets[index])
    config = args.cfg[index]
    visibility_btn = dmc.Chip(
        "Visible", color="teal", id=visible_btn_id, checked=True, size="xs"
    )
    cfg_indicator_codes = [visibility_btn]
    if config.confidence:
        cfg_indicator_codes.append(dmc.Code(f"confidence >= {config.confidence}"))
    if config.agg:
        cfg_indicator_codes.append(dmc.Code(f"{config.agg}()"))
    if config.normalize:
        cfg_indicator_codes.append(dmc.Code("normalized"))

    config_button = dmc.ActionIcon(
        get_icon(icon=icons.edit_pen),
        id={"role": config_btn_role, "index": index},
        variant="subtle",
    )

    return dmc.Card(
        dmc.Stack(
            [
                dmc.Stack(
                    [
                        dmc.ScrollArea(
                            [
                                dmc.Group(
                                    [
                                        get_icon(
                                            trace_icon, width="1.5rem", color=icon_color
                                        ),
                                        dmc.Text(
                                            [
                                                ds.get_title(),
                                            ],
                                            weight=500,
                                            size="sm",
                                            className="text-nowrap",
                                        ),
                                    ],
                                    noWrap=True,
                                    spacing=2,
                                ),
                                dmc.Space(h=3),
                            ],
                            style={"width": "99%"},
                            scrollbarSize=6,
                        ),
                        dmc.Group(
                            [
                                dmc.Group(
                                    [
                                        get_icon(icon=icons.location_marker),
                                        dmc.Text(ds.get_location(), size="xs"),
                                        dmc.Badge(
                                            ds.get_unit(),
                                            color="indigo",
                                            size="sm",
                                        ),
                                    ],
                                    spacing=2,
                                ),
                                config_button,
                            ],
                            spacing=4,
                            position="apart",
                        ),
                    ],
                    spacing=2,
                ),
                dmc.Group(cfg_indicator_codes),
            ],
            spacing=2,
        ),
        withBorder=True,
        radius=0,
        p=6,
        style={
            # "borderColor": MULTI_VIZ_COLORSCALE[index],
            "border": f"1px solid {MULTI_VIZ_COLORSCALE[index]}",
            "borderLeft": f"6px solid {MULTI_VIZ_COLORSCALE[index]}",
        },
    )


def dataset_info_cards(args: UrlSearchArgs, config_btn_role):
    if args.datasets is None or args.cfg is None:
        return []
    if not len(args.datasets) == len(args.cfg):
        return []
    cards = []
    for i in range(len(args.datasets)):
        ds = to_typed_dataset(args.datasets[i])
        config = args.cfg[i]
        cfg_indicator_codes = []
        if config.confidence:
            cfg_indicator_codes.append(dmc.Code(f"confidence >= {config.confidence}"))
        if config.agg:
            cfg_indicator_codes.append(dmc.Code(f"{config.agg}()"))
        if config.normalize:
            cfg_indicator_codes.append(dmc.Code("normalized"))
        config_button = dmc.ActionIcon(
            get_icon(icon=icons.edit_pen),
            id={"role": config_btn_role, "index": i},
            variant="subtle",
        )
        cards.append(
            dmc.Card(
                dmc.Stack(
                    [
                        dmc.Stack(
                            [
                                dmc.ScrollArea(
                                    [
                                        dmc.Text(
                                            ds.get_title(),
                                            weight=500,
                                            size="sm",
                                            className="text-nowrap",
                                        ),
                                        dmc.Space(h=3),
                                    ],
                                    style={"width": "99%"},
                                    scrollbarSize=6,
                                ),
                                dmc.Group(
                                    [
                                        dmc.Group(
                                            [
                                                get_icon(icon=icons.location_marker),
                                                dmc.Text(ds.get_location(), size="xs"),
                                                dmc.Badge(
                                                    ds.get_unit(),
                                                    color="indigo",
                                                    size="sm",
                                                ),
                                            ],
                                            spacing=2,
                                        ),
                                        config_button,
                                    ],
                                    spacing=4,
                                    position="apart",
                                ),
                            ],
                            spacing=2,
                        ),
                        dmc.Group(cfg_indicator_codes),
                    ],
                    spacing=2,
                ),
                withBorder=True,
                radius=0,
                p=6,
                style={
                    # "borderColor": MULTI_VIZ_COLORSCALE[i],
                    "border": f"1px solid {MULTI_VIZ_COLORSCALE[i]}",
                    "borderLeft": f"6px solid {MULTI_VIZ_COLORSCALE[i]}",
                },
            )
        )

    return cards


def deployment_info_card(deployment_info: dict, show_map=False):
    id = deployment_info.get("deployment_id")
    desc = deployment_info.get("description")
    node_label = deployment_info.get("node").get("node_label")
    node_type = deployment_info.get("node").get("type")
    period = deployment_info.get("period")
    period_start = format_datetime(period.get("start"))
    period_end = (
        format_datetime(period.get("end"))
        if period.get("end") is not None
        else "Active"
    )

    tags = (
        [t.get("name") for t in deployment_info.get("tags")]
        if deployment_info.get("tags") is not None
        else []
    )
    location = deployment_info.get("location")
    lat = location.get("lat")
    lon = location.get("lon")

    edit_link = dmc.Anchor(
        dmc.Button(
            "Edit",
            leftIcon=get_icon(icons.edit_pen),
            rightIcon=get_icon(icon=icons.open_in_new_tab),
            variant="subtle",
        ),
        href=f"https://deploy.mitwelten.org/deployments/edit/{id}",
        target="_blank",
    )
    map = (
        dmc.CardSection(
            dcc.Graph(
                figure=generate_scatter_map_plot(
                    lats=[lat], lons=[lon], ids=[id], names=[f"Deployment {id}"]
                ),
                config=dict(
                    displayModeBar=False,
                ),
                style=dict(height="20vh"),
            )
        )
        if show_map
        else dmc.Text()
    )
    return dmc.Card(
        [
            dmc.Stack(
                [
                    dmc.Group(
                        [
                            dmc.Text(f"Deployment {id}", weight=500),
                            dmc.Code(node_label),
                            edit_link,
                        ],
                        position="apart",
                    ),
                    dmc.Divider(),
                    dmc.Stack(
                        [
                            dmc.Group(
                                [dmc.Text("Type:", weight=300), dmc.Text(node_type)],
                            ),
                            dmc.Group(
                                [dmc.Text("Description:", weight=300), dmc.Text(desc)],
                                style={"rowGap": 2},
                            ),
                            dmc.Group(
                                [
                                    dmc.Text("Period:", weight=300),
                                    dmc.Text(f"{period_start} - {period_end}"),
                                ],
                            ),
                            dmc.Group(
                                [dmc.Text("Tags:", weight=300)]
                                + [dmc.Badge(t) for t in tags]
                            ),
                        ],
                        spacing=4,
                    ),
                    dmc.Space(h=12),
                ]
            ),
            map,
        ],
        withBorder=True,
    )
