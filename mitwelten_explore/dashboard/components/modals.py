import dash_mantine_components as dmc
from dashboard.utils.communication import urlencode_dict
from dashboard.api_clients.third_party_clients import (
    generate_wiki_link,
    get_wiki_summary,
    generate_image_attribution,
)
from dashboard.api_clients.taxonomy_client import get_parent_taxonomy
from dashboard.api_clients.bird_results_client import get_detection_count
from dashboard.api_clients.pollinator_results_client import (
    get_polli_detection_count_by_id,
)
from dashboard.api_clients.gbif_cache_client import get_gbif_detection_count
from dashboard.api_clients.environment_entries_client import get_legend
from dashboard.components.dataset_presentation import deployment_info_spoiler
from dashboard.components.labels import badge_de, badge_en
from dashboard.components.selects import agg_fcn_select, confidence_threshold_select

from dashboard.models import (
    Taxon,
    GBIFTaxon,
    RankEnum,
    DatasetType,
    ViewConfiguration,
    PollinatorDataset,
    to_typed_dataset,
    MultiPaxDataset,
    LocationEnvironmentDataset,
)
from dashboard.styles import icons, get_icon
from dash import dcc
from configuration import PATH_PREFIX, DEFAULT_CONFIDENCE
import uuid


# TODO: move icons to styles.icons


def viz_single_dataset_select_modal(opened, id="select_ts_modal"):
    return dmc.Modal(
        title=dmc.Text("Select a dataset from your collection", weight=500),
        opened=opened,
        id=id,
        size="80%",
        withCloseButton=False,
        closeOnClickOutside=False,
        closeOnEscape=False,
        overlayBlur=8,
    )


def generate_viz_timeseries_select_modal_children(store_data):
    if store_data is None:
        return []

    list_entries = []
    for i in range(len(store_data)):
        data = store_data[i]
        ds = to_typed_dataset(store_data[i])

        if not ds.type in [
            DatasetType.meteodata,
            DatasetType.birds,
            DatasetType.distinct_species,
            DatasetType.gbif_observations,
            DatasetType.pax,
            DatasetType.pollinators,
            DatasetType.env_humi,
            DatasetType.env_temp,
            DatasetType.env_moist,
        ]:
            continue

        location_name = dmc.Group(
            [
                get_icon(icon=icons.location_marker),
                dmc.Text(ds.get_location(), size="md"),
            ],
            spacing=2,
        )
        if ds.type in [
            DatasetType.distinct_species,
            DatasetType.pollinators,
            DatasetType.pax,
            DatasetType.multi_pax,
            DatasetType.env_humi,
            DatasetType.env_moist,
            DatasetType.env_temp,
        ]:
            if ds.deployment_id is not None:
                location_name = deployment_info_spoiler(ds.deployment_id, location_name)

        single_viz_url = (
            f"{PATH_PREFIX}viz/timeseries?{urlencode_dict(dict(trace=data))}"
        )
        if i > 0:
            list_entries.append(dmc.Divider())
        list_entries.append(
            dmc.Grid(
                [
                    dmc.Col(
                        dmc.Anchor(
                            dmc.Grid(
                                [
                                    dmc.Col(
                                        dmc.Group(
                                            [
                                                get_icon(ds.get_icon(), width=32),
                                                dmc.Code(ds.get_id()),
                                            ]
                                        ),
                                        span=3,
                                    ),
                                    dmc.Col(
                                        dmc.Group(
                                            [
                                                dmc.Text(ds.get_title(), size="md"),
                                                dmc.Badge(ds.get_unit(), color="teal"),
                                            ]
                                        ),
                                        span=9,
                                    ),
                                ]
                            ),
                            href=single_viz_url,
                            variant="text",
                        ),
                        span=6,
                    ),
                    dmc.Col(
                        dmc.Group(
                            [
                                location_name,
                            ],
                            spacing=4,
                        ),
                        span=6,
                    ),
                ]
            )
        )
    return list_entries


def viz_compare_select_modal(
    id, title="Select two or more datasets from your collection"
):
    return dmc.Modal(
        title=dmc.Text(title, weight=500),
        id=id,
        opened=True,
        size="80%",
        withCloseButton=False,
        closeOnClickOutside=False,
        closeOnEscape=False,
        overlayBlur=8,
    )


def generate_viz_map_select_modal_children(store_data, id_role):
    if store_data is None:
        return []
    list_entries = []
    for i in range(len(store_data)):
        ds = to_typed_dataset(store_data[i])
        if not ds.type in [
            DatasetType.birds,
            DatasetType.distinct_species,
            DatasetType.gbif_observations,
        ]:
            continue

        location_name = dmc.Group(
            [
                get_icon(icon=icons.location_marker),
                dmc.Text(ds.get_location(), size="md"),
            ],
            spacing=2,
        )
        if ds.type in [
            DatasetType.distinct_species,
            DatasetType.pollinators,
            DatasetType.pax,
            DatasetType.env_humi,
            DatasetType.env_moist,
            DatasetType.env_temp,
        ]:
            if ds.deployment_id is not None:
                location_name = deployment_info_spoiler(ds.deployment_id, location_name)

        list_entries.append(
            dmc.Grid(
                [
                    dmc.Col(
                        dmc.Group(
                            [
                                dmc.Checkbox(
                                    color="teal",
                                    id={
                                        "role": id_role,
                                        "index": str(store_data[i]),
                                    },
                                    checked=False,
                                ),
                                get_icon(ds.get_icon(), width=32),
                                dmc.Code(ds.get_id()),
                            ]
                        ),
                        span=2,
                    ),
                    dmc.Col(
                        dmc.Group(
                            [
                                dmc.Text(ds.get_title()),
                                dmc.Badge(ds.get_unit(), color="teal"),
                            ]
                        ),
                        span=5,
                    ),
                    dmc.Col(
                        location_name,
                        span=5,
                    ),
                ]
            )
        )
        if i > 0:
            list_entries.append(dmc.Divider())

    environment_legend = get_legend()
    default_datasets = [MultiPaxDataset()]
    for key in environment_legend.keys():
        default_datasets.append(
            LocationEnvironmentDataset(
                attribute=key,
                label=environment_legend[key].get("label"),
                description_min=environment_legend[key].get("description")[0],
                description_max=environment_legend[key].get("description")[-1],
            )
        )

    list_entries.append(dmc.Text("Default Datasets", weight=500, align="center"))
    for ds in default_datasets:
        list_entries.append(
            dmc.Grid(
                [
                    dmc.Col(
                        dmc.Group(
                            [
                                dmc.Checkbox(
                                    color="teal",
                                    id={
                                        "role": id_role,
                                        "index": str(ds.to_dataset()),
                                    },
                                    checked=False,
                                ),
                                get_icon(ds.get_icon(), width=32),
                                dmc.Code(ds.get_id()),
                            ]
                        ),
                        span=2,
                    ),
                    dmc.Col(
                        dmc.Group(
                            [
                                dmc.Text(ds.get_title(), size="md"),
                                dmc.Badge(ds.get_unit(), color="teal"),
                            ]
                        ),
                        span=5,
                    ),
                    dmc.Col(
                        dmc.Group(
                            [
                                get_icon(icon=icons.location_marker),
                                dmc.Text(ds.get_location(), size="sm"),
                            ],
                            spacing=4,
                        ),
                        span=5,
                    ),
                ]
            )
        )
        list_entries.append(dmc.Divider())
    return list_entries


def generate_viz_compare_select_modal_children(store_data, id_role):
    if store_data is None:
        return []
    list_entries = []
    for i in range(len(store_data)):
        ds = to_typed_dataset(store_data[i])
        if not ds.type in [
            DatasetType.pollinators,
            DatasetType.pax,
            DatasetType.meteodata,
            DatasetType.birds,
            DatasetType.gbif_observations,
            DatasetType.distinct_species,
            DatasetType.env_humi,
            DatasetType.env_temp,
            DatasetType.env_moist,
        ]:
            continue
        location_name = dmc.Group(
            [
                get_icon(icon=icons.location_marker),
                dmc.Text(ds.get_location(), size="md"),
            ],
            spacing=2,
        )
        if ds.type in [
            DatasetType.distinct_species,
            DatasetType.pollinators,
            DatasetType.pax,
            DatasetType.env_humi,
            DatasetType.env_moist,
            DatasetType.env_temp,
        ]:
            if ds.deployment_id is not None:
                location_name = deployment_info_spoiler(ds.deployment_id, location_name)

        if i > 0:
            list_entries.append(dmc.Divider())
        list_entries.append(
            dmc.Grid(
                [
                    dmc.Col(
                        dmc.Group(
                            [
                                dmc.Checkbox(
                                    color="teal",
                                    id={"role": id_role, "index": str(store_data[i])},
                                    checked=False,
                                ),
                                get_icon(icon=ds.get_icon(), width=32),
                                dmc.Code(ds.get_id()),
                            ]
                        ),
                        span=2,
                    ),
                    dmc.Col(
                        dmc.Group(
                            [
                                dmc.Text(ds.get_title(), size="md"),
                                dmc.Badge(ds.get_unit(), color="teal"),
                            ]
                        ),
                        span=5,
                    ),
                    dmc.Col(
                        location_name,
                        span=5,
                    ),
                ]
            )
        )
    return list_entries


def generate_viz_deployment_select_modal_children(store_data):
    if store_data is None:
        return []

    list_entries = []
    for i in range(len(store_data)):
        ds = to_typed_dataset(store_data[i])
        if ds.type in [DatasetType.distinct_species, DatasetType.pollinators]:

            location_name = dmc.Group(
                [
                    get_icon(icon=icons.location_marker),
                    dmc.Text(ds.get_location(), size="md"),
                ],
                spacing=2,
            )
            if ds.deployment_id is not None:
                location_name = deployment_info_spoiler(ds.deployment_id, location_name)

            deployment_viz_url = f"{PATH_PREFIX}viz/deployment?{urlencode_dict(dict(dataset=ds.to_dataset()))}"
            if i > 0:
                list_entries.append(dmc.Divider())
            list_entries.append(
                dmc.Grid(
                    [
                        dmc.Col(
                            dmc.Anchor(
                                dmc.Grid(
                                    [
                                        dmc.Col(
                                            dmc.Group(
                                                [
                                                    get_icon(
                                                        icon=ds.get_icon(), width=32
                                                    ),
                                                    dmc.Code(ds.get_id()),
                                                ]
                                            ),
                                            span=3,
                                        ),
                                        dmc.Col(
                                            dmc.Group(
                                                [
                                                    dmc.Text(ds.get_title(), size="md"),
                                                    dmc.Badge(
                                                        ds.get_unit(), color="teal"
                                                    ),
                                                ]
                                            ),
                                            span=9,
                                        ),
                                    ]
                                ),
                                href=deployment_viz_url,
                                variant="text",
                            ),
                            span=6,
                        ),
                        dmc.Col(
                            location_name,
                            span=6,
                        ),
                    ]
                )
            )
        else:
            continue
    return list_entries


def share_modal(url):
    temp_id = str(uuid.uuid4())
    return dmc.Modal(
        dmc.Stack(
            [
                dmc.ScrollArea(
                    [
                        dmc.Text(
                            id=temp_id,
                            size="sm",
                            className="text-nowrap",
                            children=url,
                        ),
                        dmc.Space(h=12),
                    ]
                ),
                dmc.Group(
                    [
                        dcc.Clipboard(
                            target_id=temp_id,
                            title="copy",
                            style={
                                "display": "inline-block",
                                "fontSize": 20,
                                "verticalAlign": "top",
                            },
                        ),
                        dmc.Text("Copy to Clipboard"),
                    ]
                ),
            ],
        ),
        opened=True,
        title="Share this view",
        zIndex=1000,
        size="55%",
    )


def taxon_select_modal(taxon_id, id_role, gbif_add_id_role):
    taxon_tree = get_parent_taxonomy(taxon_key=taxon_id)
    taxon_tree.sort()
    selected_taxon = min(taxon_tree)
    rank_badges = []
    for t in reversed(taxon_tree[1:]):
        if len(rank_badges) > 0:
            rank_badges.append(
                dmc.Text(
                    get_icon(icon=icons.arrow_right, height="1.5rem"),
                    color="teal.9",
                )
            )
        rank_badges.append(
            dmc.Badge(
                dmc.Group(
                    [
                        dmc.Badge(
                            t.rank.value[0],
                            radius=0,
                            variant="filled",
                            color="teal.9",
                        ),
                        dmc.Text(t.label_sci),
                    ]
                ),
                radius="xs",
                variant="outline",
                pl=0,
                color="teal.9",
            )
        )

    mw_bird_detections = get_detection_count(
        selected_taxon.datum_id, DEFAULT_CONFIDENCE
    )
    polli_detections = get_polli_detection_count_by_id(
        selected_taxon.datum_id, DEFAULT_CONFIDENCE
    )
    mw_detections = mw_bird_detections if mw_bird_detections is not None else 0
    if polli_detections is not None:
        mw_detections += polli_detections
    gbif_detections = get_gbif_detection_count(selected_taxon.datum_id)

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
    return dmc.Modal(
        title=dmc.Group(
            [dmc.Text(selected_taxon.label_sci, weight=700, size="xl"), rank_badge],
            align="center",
        ),
        opened=True,
        children=[
            dmc.Stack(
                [
                    dmc.Group(
                        [
                            dmc.Group([label_de, label_en]),
                            dmc.Group(
                                [
                                    dmc.Badge(
                                        f"{mw_detections} Mitwelten Detections",
                                        radius="xs",
                                        color="teal.6" if mw_detections > 0 else "gray",
                                        variant="outline",
                                        size="lg",
                                    ),
                                    dmc.Badge(
                                        f"{gbif_detections} GBIF Observations",
                                        radius="xs",
                                        color="green"
                                        if gbif_detections > 0
                                        else "gray",
                                        variant="outline",
                                        size="lg",
                                    ),
                                ]
                            ),
                        ],
                        position="apart",
                    ),
                    dmc.Group(rank_badges, spacing=1),
                    dmc.Divider(variant="solid"),
                    dmc.Grid(
                        [
                            dmc.Col(
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
                                className="col-md-4"
                                if selected_taxon.image_url
                                else "col-md-auto",
                            ),
                            dmc.Col(
                                [
                                    dcc.Markdown(
                                        extract,
                                        className="lh-md",
                                        link_target="_blank",
                                        style={
                                            "fontFamily": "Times New Roman",
                                            "fontSize": "1.1rem",
                                        },
                                    ),
                                ],
                                className="col-md-8"
                                if selected_taxon.image_url
                                else "col-md-auto",
                                # pl=40,
                            ),
                        ],
                        gutter="lg",
                    ),
                    dmc.Group(
                        [
                            dmc.Button(
                                "Add Mitwelten Detections to Collection",
                                color="teal.6",
                                leftIcon=get_icon(icon=icons.bookmark, height=25),
                                id={
                                    "role": id_role,
                                    "index": selected_taxon.datum_id,
                                },
                            ),
                            dmc.Button(
                                "Add GBIF Observations to Collection",
                                color="lime",
                                leftIcon=get_icon(icon=icons.bookmark, height=25),
                                id={
                                    "role": gbif_add_id_role,
                                    "index": selected_taxon.datum_id,
                                },
                            ),
                            dmc.Anchor(
                                dmc.Button(
                                    "Go to Taxon Dashboard",
                                    color="teal.6",
                                    leftIcon=get_icon(icon=icons.dashboard, height=25),
                                    rightIcon=get_icon(icon=icons.open_in_new_tab),
                                ),
                                href=f"{PATH_PREFIX}viz/taxon/{selected_taxon.datum_id}",
                                target="_blank",
                            ),
                        ],
                        position="right",
                    ),
                ],
                spacing="xs",
            )
        ],
        size="80%",
    )


def dataset_config_modal(
    dataset,
    cfg: ViewConfiguration,
    index,
    id,
    apply_btn_role,
    confidence_select_id=None,
    agg_select_id=None,
    normalize_id=None,
):
    children = []
    if cfg.agg:
        children.append(agg_fcn_select(id=agg_select_id, value=cfg.agg))
    else:
        children.append(agg_fcn_select(id=agg_select_id, value=None, visible=False))

    if cfg.confidence:
        children.append(
            confidence_threshold_select(id=confidence_select_id, value=cfg.confidence)
        )
    else:
        children.append(
            confidence_threshold_select(
                id=confidence_select_id, value=None, visible=False
            )
        )
    if normalize_id:
        children.append(
            dmc.Checkbox(label="Normalize", checked=cfg.normalize, id=normalize_id),
        )
    children.append(
        dmc.Group(
            dmc.Button(
                "Apply", color="teal", id={"role": apply_btn_role, "index": index}
            ),
            position="right",
        )
    )
    return dmc.Modal(
        title=dataset.get_title(),
        size="30%",
        opened=True,
        children=dmc.Stack(children),
        id=id,
    )


def confirm_dialog(id, submit_id, text=None, title="Are you sure you want to continue"):
    return dmc.Modal(
        id=id,
        children=[
            dmc.Text(text),
            dmc.Space(h=20),
            dmc.Group(
                [
                    dmc.Button(
                        "Confirm",
                        color="red",
                        variant="outline",
                        id=submit_id,
                        n_clicks=0,
                    )
                ],
                position="right",
            ),
        ],
        title=dmc.Text(title, weight=500),
        opened=True,
    )
