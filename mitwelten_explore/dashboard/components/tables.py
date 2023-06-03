from dash import html
import dash_mantine_components as dmc
import numpy as np
from dashboard.api_clients.deployments_client import get_deployments
from configuration import PATH_PREFIX


def statsagg_table(summary):

    header = [
        html.Thead(
            html.Tr(
                [
                    html.Th("aggregation", colSpan=2),
                ],
                draggable=True,
            )
        )
    ]
    rows = []
    for key in summary.keys():
        value = summary[key]
        if isinstance(value, float):
            value = round(value, 3)

        rows.append(
            html.Tr(
                [
                    html.Td(dmc.Code(key)),
                    html.Td(dmc.Text(value, className="font-monospace")),
                ]
            )
        )
    return [
        dmc.Text("Statistical Aggregates", weight=500),
        dmc.Space(h=12),
        dmc.Table(
            [html.Tbody(rows)],
            striped=True,
            verticalSpacing=4,
        ),
    ]


def taxon_species_detections_table(
    species_count: dict, confidence, selected_species_id
):
    labels_sci = []
    counts = []
    species_ids = []
    for sp in species_count:
        labels_sci.append(sp.get("label_sci"))
        counts.append(int(sp.get("detections", 0)))
        species_ids.append(sp.get("datum_id"))
    normalized_counts = np.sqrt(counts)
    count_percents = [(c / max(normalized_counts)) * 100 for c in normalized_counts]
    table_header = [
        html.Thead(
            html.Tr(
                [
                    html.Th("Species", style=dict(width="30%")),
                    html.Th(
                        dmc.Group(
                            [
                                dmc.Text("Detections"),
                                dmc.Code(f"conf ≥ {confidence}"),
                            ],
                            spacing="md",
                        )
                    ),
                ]
            )
        )
    ]
    table_rows = []
    for i in range(len(counts)):
        table_rows.append(
            html.Tr(
                [
                    html.Td(
                        dmc.Anchor(
                            dmc.Text(labels_sci[i]),
                            href=f"{PATH_PREFIX}viz/taxon/{species_ids[i]}",
                        )
                        if species_ids[i] != int(selected_species_id)
                        else dmc.Text(labels_sci[i])
                    ),
                    html.Td(
                        dmc.Grid(
                            [
                                dmc.Col(
                                    dmc.Text(
                                        f"{counts[i]:,}".replace(",", "'"), weight=500
                                    ),
                                    span=3,
                                ),
                                dmc.Col(
                                    dmc.Progress(
                                        value=count_percents[i],
                                        size="xl",
                                        color="teal.9",
                                        className="bg-transparent",
                                    ),
                                    span=9,
                                ),
                            ]
                        )
                    ),
                ]
            )
        )

    return dmc.Table(
        table_header + [html.Tbody(table_rows)], style=dict(width="100%"), striped=True
    )


def deployments_table(deployment_ids):
    deployments = []
    for d in deployment_ids:
        deployments.append(get_deployments(deployment_id=d)[0])

    header = [
        html.Thead(
            html.Tr(
                [
                    html.Th("Deployment"),
                    html.Th("Node Label"),
                    html.Th("Period"),
                ],
                draggable=True,
            )
        )
    ]
    rows = []
    for d in deployments:

        rows.append(
            html.Tr(
                [
                    html.Td(dmc.Code(d.get("deployment_id"))),
                    html.Td(
                        dmc.Text(
                            d.get("node").get("node_label"), className="font-monospace"
                        )
                    ),
                    html.Td(
                        dmc.Text(
                            f'{d.get("period").get("start")} - {d.get("period").get("end") if d.get("period").get("end") is not None else "Active" }',
                            className="font-monospace",
                        )
                    ),
                ]
            )
        )
    return dmc.Table(
        header + [html.Tbody(rows)],
        striped=True,
        verticalSpacing=4,
    )
