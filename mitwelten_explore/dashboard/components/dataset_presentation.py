import dash_mantine_components as dmc
from dashboard.styles import icons, get_icon
from dashboard.models import (
    Taxon,
    PaxDataset,
    EnvHumiDataset,
    EnvTempDataset,
    EnvMoistDataset,
    PollinatorDataset,
    BirdDataset,
    to_typed_dataset,
)
from dash import html
import json
from configuration import PATH_PREFIX
from dashboard.utils.communication import urlencode_dict
from dashboard.components.tables import deployments_table
from dashboard.components.labels import badge_de, badge_en


def dataset_title(dataset: dict):
    ds = to_typed_dataset(dataset)

    return dmc.Group(
        [
            dmc.Text(ds.get_title(), size="md", weight=500),
            dmc.Badge(ds.get_unit(), size="md", color="indigo"),
            dmc.Group(
                [
                    get_icon(icon=icons.location_marker),
                    dmc.Text(ds.get_location(), size="sm"),
                ],
                spacing=2,
            ),
        ],
        style={"rowGap": "2px"},
    )


def taxon_list_card(taxon: Taxon, id_role):
    title = dmc.Text(taxon.label_sci, weight=500)
    label_de = (
        dmc.Group([badge_de, dmc.Text(taxon.label_de)], spacing=3)
        if taxon.label_de
        else None
    )
    label_en = (
        dmc.Group([badge_en, dmc.Text(taxon.label_en)], spacing=3)
        if taxon.label_en
        else None
    )
    rank_badge = dmc.Badge(
        taxon.rank,
        radius="xs",
        color="gray",
        variant="outline",
    )
    return html.Div(
        dmc.Card(
            dmc.Grid(
                [
                    dmc.Col(dmc.Group([title, rank_badge]), className="col-lg-4"),
                    dmc.Col(dmc.Group([label_de, label_en]), className="col-md-7"),
                    dmc.Col(
                        dmc.Badge(
                            str(taxon.datum_id),
                            size="sm",
                            variant="outline",
                            color="gray",
                        ),
                        className="col-md-1 d-flex justify-content-end align-items-center",
                    ),
                ],
                style={"rowGap": "4px"},
            ),
            withBorder=True,
            style={"cursor": "pointer"},
            py=8,
        ),
        id={
            "role": id_role,
            "index": taxon.datum_id,
        },
    )


def pax_deployment_select_card(deployment: dict, id_role="pax_deployment_add"):
    node = deployment.get("node")
    node_label = node.get("node_label")
    description = deployment.get("description")
    deployment_id = deployment.get("deployment_id")
    time_from = deployment.get("period").get("start")
    time_to = deployment.get("period").get("end")
    pax_dataset = PaxDataset(
        deployment_id=deployment_id,
        node_label=node_label,
        period_from=time_from,
        period_to=time_to,
    )
    time_to = "Active" if time_to is None else time_to
    node_type = node.get("type")
    node_platform = node.get("platform")
    node_connectivity = node.get("connectivity")
    return dmc.Card(
        dmc.Grid(
            [
                dmc.Col(
                    dmc.Stack(
                        [
                            dmc.Group(
                                [
                                    dmc.Text(node_type, weight=500),
                                    dmc.Group(
                                        [
                                            get_icon(icon=icons.location_marker),
                                            dmc.Text(
                                                f"deployment #{deployment_id}",
                                                weight=500,
                                            ),
                                        ],
                                        spacing=3,
                                    ),
                                    dmc.Badge(
                                        f"{time_from} - {time_to}",
                                        color="indigo",
                                        variant="outline",
                                        size="md",
                                    ),
                                ]
                            ),
                            dmc.Group(
                                [
                                    dmc.Text(
                                        f"Node {node_label}", weight=400, size="sm"
                                    ),
                                    dmc.Badge(
                                        node_platform, color="gray", variant="outline"
                                    ),
                                    dmc.Badge(
                                        node_connectivity,
                                        color="gray",
                                        variant="outline",
                                    )
                                    if node_connectivity
                                    else None,
                                    dmc.Text(description, size="sm"),
                                ]
                            ),
                        ],
                        spacing=4,
                    ),
                    className="col-lg-9",
                ),
                dmc.Col(
                    [
                        dmc.Group(
                            [
                                dmc.Anchor(
                                    dmc.Button(
                                        "Viz",
                                        leftIcon=get_icon(
                                            icon=icons.line_chart, width=20
                                        ),
                                        color="indigo.6",
                                        variant="outline",
                                    ),
                                    href=f"{PATH_PREFIX}viz/timeseries?{urlencode_dict(dict(trace=pax_dataset.to_dataset()))}",
                                    target="_blank",
                                ),
                                dmc.Button(
                                    # "Collect",
                                    get_icon(
                                        icon=icons.bookmark,
                                        width=20,
                                    ),
                                    color="indigo.6",
                                    variant="subtle",
                                    px=4,
                                    # compact=True,
                                    id={
                                        "role": id_role,
                                        "index": json.dumps(pax_dataset.to_dataset()),
                                    },
                                ),
                            ],
                            spacing="xs",
                        )
                    ],
                    className="col-xl-3 d-flex justify-content-end align-items-center",
                ),
            ]
        ),
        withBorder=True,
    )


def env_deployment_select_cards(deployment: dict, id_role):
    node = deployment.get("node")
    node_label = node.get("node_label")
    description = deployment.get("description")
    deployment_id = deployment.get("deployment_id")
    time_from = deployment.get("period").get("start")
    time_to = deployment.get("period").get("end")
    node_type = node.get("type")
    node_platform = node.get("platform")
    node_connectivity = node.get("connectivity")
    temp_dataset = EnvTempDataset(
        deployment_id=deployment_id,
        node_label=node_label,
        period_from=time_from,
        period_to=time_to,
    )
    moist_dataset = EnvMoistDataset(
        deployment_id=deployment_id,
        node_label=node_label,
        period_from=time_from,
        period_to=time_to,
    )
    humi_dataset = EnvHumiDataset(
        deployment_id=deployment_id,
        node_label=node_label,
        period_from=time_from,
        period_to=time_to,
    )
    time_to = "Active" if time_to is None else time_to
    cards = [
        dmc.Card(
            dmc.Grid(
                [
                    dmc.Col(
                        dmc.Stack(
                            [
                                dmc.Group(
                                    [
                                        dmc.Text(ds.param_desc, weight=500),
                                        dmc.Badge(
                                            ds.unit,
                                            color="indigo",
                                            variant="outline",
                                        ),
                                        dmc.Group(
                                            [
                                                get_icon(icon=icons.location_marker),
                                                dmc.Text(
                                                    f"deployment #{deployment_id}",
                                                    weight=500,
                                                ),
                                            ],
                                            spacing=3,
                                        ),
                                        dmc.Badge(
                                            f"{time_from} - {time_to}",
                                            color="indigo",
                                            variant="outline",
                                            size="md",
                                        ),
                                    ]
                                ),
                                dmc.Group(
                                    [
                                        dmc.Text(
                                            f"Node {node_label}", weight=400, size="sm"
                                        ),
                                        dmc.Badge(
                                            node_platform,
                                            color="gray",
                                            variant="outline",
                                        ),
                                        dmc.Badge(
                                            node_connectivity,
                                            color="gray",
                                            variant="outline",
                                        )
                                        if node_connectivity
                                        else None,
                                        dmc.Text(description, size="sm"),
                                    ]
                                ),
                            ],
                            spacing=4,
                        ),
                        className="col-lg-9",
                    ),
                    dmc.Col(
                        [
                            dmc.Group(
                                [
                                    dmc.Anchor(
                                        dmc.Button(
                                            "Viz",
                                            leftIcon=get_icon(
                                                icon=icons.line_chart, width=20
                                            ),
                                            color="indigo.6",
                                            variant="outline",
                                        ),
                                        href=f"{PATH_PREFIX}viz/timeseries?{urlencode_dict(dict(trace=ds.to_dataset()))}",
                                        target="_blank",
                                    ),
                                    dmc.Button(
                                        # "Collect",
                                        get_icon(
                                            icon=icons.bookmark,
                                            width=20,
                                        ),
                                        color="indigo.6",
                                        variant="subtle",
                                        px=4,
                                        # compact=True,
                                        id={
                                            "role": id_role,
                                            "index": json.dumps(ds.to_dataset()),
                                        },
                                    ),
                                ],
                                spacing="xs",
                            )
                        ],
                        className="col-xl-3 d-flex justify-content-end align-items-center",
                    ),
                ]
            ),
            withBorder=True,
        )
        for ds in [temp_dataset, humi_dataset, moist_dataset]
    ]
    return cards


def pollinator_dataset_card(id_role, deployment_ids=None, pollinator_class=None):
    ds = PollinatorDataset(
        deployment_id=deployment_ids, pollinator_class=pollinator_class
    )
    title = (
        "All Pollinator Classes"
        if pollinator_class is None
        else pollinator_class.title()
    )
    title_group = dmc.Group([get_icon(icon=icons.bee), dmc.Text(title, weight=500)])
    btn_group = dmc.Group(
        [
            dmc.Anchor(
                dmc.Button(
                    "Viz",
                    leftIcon=get_icon(icon=icons.line_chart, width=20),
                    color="indigo.6",
                    variant="outline",
                ),
                href=f"{PATH_PREFIX}viz/timeseries?{urlencode_dict(dict(trace=ds.to_dataset()))}",
                target="_blank",
            ),
            dmc.Button(
                # "Collect",
                get_icon(
                    icon=icons.bookmark,
                    width=20,
                ),
                color="indigo.6",
                variant="subtle",
                px=4,
                # compact=True,
                id={
                    "role": id_role,
                    "index": json.dumps(ds.to_dataset()),
                },
            ),
        ],
        position="right",
    )

    if deployment_ids is None or len(deployment_ids) == 0:
        location = "All Deployments"
        location_group = dmc.Group(
            [get_icon(icon=icons.location_marker), dmc.Text(location)]
        )
    else:
        location_group = deployments_table(deployment_ids)

    return dmc.Card(
        [
            title_group,
            dmc.Spoiler(
                showLabel="Show All",
                hideLabel="Hide",
                maxHeight=150,
                children=[
                    location_group,
                ],
            ),
            btn_group,
        ],
        withBorder=True,
    )


def bird_dataset_card(id_role, deployment_ids=None):
    ds = BirdDataset(deployment_id=deployment_ids)
    title = "Distinct Species"
    title_group = dmc.Group([get_icon(icon=icons.bird), dmc.Text(title, weight=500)])
    btn_group = dmc.Group(
        [
            dmc.Anchor(
                dmc.Button(
                    "Explore detected Species",
                    leftIcon=get_icon(icon=icons.bird, width=20),
                    color="indigo.6",
                    variant="outline",
                ),
                href=f"{PATH_PREFIX}viz/deployment?{urlencode_dict(dict(dataset=ds.to_dataset()))}",
                target="_blank",
            ),
            dmc.Button(
                # "Collect",
                get_icon(
                    icon=icons.bookmark,
                    width=20,
                ),
                color="indigo.6",
                variant="subtle",
                px=4,
                # compact=True,
                id={
                    "role": id_role,
                    "index": json.dumps(ds.to_dataset()),
                },
            ),
        ],
        position="right",
    )

    if deployment_ids is None or len(deployment_ids) == 0:
        location = "All Deployments"
        location_group = dmc.Group(
            [get_icon(icon=icons.location_marker), dmc.Text(location)]
        )
    else:
        location_group = deployments_table(deployment_ids)

    return dmc.Card(
        [
            title_group,
            dmc.Spoiler(
                showLabel="Show All",
                hideLabel="Hide",
                maxHeight=150,
                children=[
                    location_group,
                ],
            ),
            btn_group,
        ],
        withBorder=True,
    )
