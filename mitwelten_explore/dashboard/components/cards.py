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
                            spacing=0
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
        shadow="sm"
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
            cfg_indicator_codes.append(
                dmc.Code(f"confidence >= {config.confidence}")
            )
        if config.agg:
            cfg_indicator_codes.append(
                dmc.Code(f"{config.agg}()")
            )
        if config.normalize:
            cfg_indicator_codes.append(
                dmc.Code("normalized")
            )
        cards.append(
            dmc.Card(
                dmc.Stack(
                    [
                        dmc.Stack(
                            [
                                dmc.Group(
                                    [
                                        dmc.Text(ds.get_title(),weight=500,  size="sm"),
                                        dmc.Badge(ds.get_unit(), color="indigo", size="sm"),
                                    ], spacing=4
                                ),
                                dmc.Group(
                                    [
                                        get_icon(icon=icons.location_marker),
                                        dmc.Text(ds.get_location(), size="xs"),
                                    ],
                                    spacing=2,
                                ),
                            ],
                            spacing=2
                        ),
                        dmc.Group(
                            [
                                dmc.Group(
                                    cfg_indicator_codes
                                ),
                                dmc.ActionIcon(
                                    get_icon(icon=icons.edit_pen),
                                    id={"role": config_btn_role, "index": i},
                                    variant="subtle",
                                ),
                            ],
                            position="apart",
                        ),
                    ],
                    spacing=4
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
