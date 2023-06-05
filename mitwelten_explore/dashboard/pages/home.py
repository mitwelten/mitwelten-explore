import dash
from dash import html, dcc, callback, Input, Output, no_update
import flask
import dash_mantine_components as dmc
from configuration import PATH_PREFIX
from dashboard.styles import icons, get_icon
from dashboard.api_clients.userdata_client import get_annotations
from dashboard.utils.text_utils import beautify_timedelta
import datetime

dash.register_page(__name__, path="/")


not_yet_func_alert = dmc.Alert(
    dmc.Text(
        "This website is currently under development and is not yet functional.",
    ),
    title=dmc.Text("Work in progress", size="1.1rem"),
    color="yellow",
    withCloseButton=True,
)
polli_card = dmc.Anchor(
    [
        dmc.Alert(
            title=dmc.Group(
                [
                    get_icon(icon=icons.bee, width="1.5rem"),
                    dmc.Text("Compare Pollinator results", size="1.2rem"),
                ]
            ),
            children=[
                dmc.Text(
                    "Go to the dataset comparison dashboard to analyze pollinator classes"
                )
            ],
            color="teal",
            variant="text",
        )
    ],
    href=PATH_PREFIX
    + "viz/compare?datasets=%5B%7B%27type%27%3A+%27pollinators%27%2C+%27deployment_id%27%3A+None%2C+%27pollinator_class%27%3A+%27fliege%27%7D%2C+%7B%27type%27%3A+%27pollinators%27%2C+%27deployment_id%27%3A+None%2C+%27pollinator_class%27%3A+%27wildbiene%27%7D%2C+%7B%27type%27%3A+%27pollinators%27%2C+%27deployment_id%27%3A+None%2C+%27pollinator_class%27%3A+%27schwebfliege%27%7D%2C+%7B%27type%27%3A+%27pollinators%27%2C+%27deployment_id%27%3A+None%2C+%27pollinator_class%27%3A+%27hummel%27%7D%2C+%7B%27type%27%3A+%27pollinators%27%2C+%27deployment_id%27%3A+None%2C+%27pollinator_class%27%3A+%27honigbiene%27%7D%5D&cfg=%5B%7B%27confidence%27%3A+0.6%2C+%27normalize%27%3A+False%7D%2C+%7B%27confidence%27%3A+0.6%2C+%27normalize%27%3A+False%7D%2C+%7B%27confidence%27%3A+0.6%2C+%27normalize%27%3A+False%7D%2C+%7B%27confidence%27%3A+0.6%2C+%27normalize%27%3A+False%7D%2C+%7B%27confidence%27%3A+0.6%2C+%27normalize%27%3A+False%7D%5D&bucket=1d&from=2021-05-26T04%3A08%3A16&to=2022-10-18T05%3A47%3A35",
    target="_blank",
)
pax_insektenkiosk = dmc.Anchor(
    [
        dmc.Alert(
            title=dmc.Group(
                [
                    get_icon(icon=icons.pax_counter, width="1.5rem"),
                    dmc.Text("PAX Counter Insektenkiosk", size="1.2rem"),
                ]
            ),
            children=[
                dmc.Text(
                    "Explore PAX Counter data (Insektenkiosk) in the timeseries dashboard"
                )
            ],
            color="blue",
            variant="text",
        )
    ],
    href=PATH_PREFIX
    + "viz/timeseries?trace=%7B%27type%27%3A+%27pax%27%2C+%27deployment_id%27%3A+865%2C+%27node_label%27%3A+%279231-7621%27%2C+%27period_from%27%3A+%272023-04-20T22%3A00%3A00%2B00%3A00%27%2C+%27period_to%27%3A+None%7D&agg=None&bucket=2h&from=2023-04-30T02%3A41%3A27",
    target="_blank",
)
apus_apus = dmc.Anchor(
    [
        dmc.Alert(
            title=dmc.Group(
                [
                    get_icon(icon=icons.bird, width="1.5rem"),
                    dmc.Text("Apus Apus Detections", size="1.2rem"),
                ]
            ),
            children=[
                dmc.Text(
                    "Explore Apus Apus (Mauersegler)  detections in the Taxon dashboard"
                )
            ],
            color="lime",
            variant="text",
        )
    ],
    href=PATH_PREFIX
    + "viz/taxon/5228676?bucket=1w&from=2020-08-01T00%3A00%3A00&to=2023-05-09T10%3A35%3A02.103073&confidence=0.7",
    target="_blank",
)

class_aves = dmc.Anchor(
    [
        dmc.Alert(
            title=dmc.Group(
                [
                    get_icon(icon=icons.bird, width="1.5rem"),
                    dmc.Text("Aves Detections", size="1.2rem"),
                ]
            ),
            children=[
                dmc.Text(
                    "Explore detections of all birds (class Aves) in the Timeseries dashboard"
                )
            ],
            color="lime",
            variant="text",
        )
    ],
    href=PATH_PREFIX
    + "viz/timeseries?trace=%7B%27type%27%3A+%27birds%27%2C+%27datum_id%27%3A+212%2C+%27label_de%27%3A+None%2C+%27label_en%27%3A+%27Bird%27%2C+%27label_sci%27%3A+%27Aves%27%2C+%27rank%27%3A+%27CLASS%27%2C+%27deployment_filter%27%3A+%5B%5D%7D&agg=None&bucket=1d&from=2021-03-04T19%3A07%3A36&confidence=0.7",
    target="_blank",
)


quickstart_card = dmc.Anchor(
    [
        dmc.Alert(
            title=dmc.Group(
                [
                    get_icon(icon=icons.quickstart_rocket, width="1.5rem"),
                    dmc.Text("Quickstart", size="1.2rem"),
                ]
            ),
            children=[
                dmc.Text("Follow a simple tutorial to learn how to use this tool")
            ],
            color="indigo",
            variant="text",
        )
    ],
    href=PATH_PREFIX + "docs#quickstart",
    target="_blank",
)
doc_card = dmc.Anchor(
    [
        dmc.Alert(
            title=dmc.Group(
                [
                    get_icon(icon=icons.docs_book, width="1.5rem"),
                    dmc.Text("Datasets", size="1.2rem"),
                ]
            ),
            children=[dmc.Text("Learn about the datasets in this tool")],
            color="indigo",
            variant="text",
        )
    ],
    href=PATH_PREFIX + "docs#datasets",
    target="_blank",
)

annots_card = dmc.Anchor(
    [
        dmc.Alert(
            title=dmc.Group(
                [
                    get_icon(icon=icons.annotation_bank, width="1.5rem"),
                    dmc.Text("Annotations", size="1.2rem"),
                ]
            ),
            children=[dmc.Text("See what users have discovered")],
            color="cyan",
            variant="text",
        )
    ],
    href=PATH_PREFIX + "annotations",
    target="_blank",
)


def layout(**kwargs):
    return dmc.Container(
        [
            dcc.Location("url", refresh=False),
            dmc.Title("Mitwelten Explore"),
            dmc.Space(h=40),
            dmc.Grid(
                [
                    dmc.Col(
                        [
                            dmc.Stack(
                                [
                                    dmc.Text(
                                        "Selected Dashboards", size="1.2rem", weight=500
                                    ),
                                    polli_card,
                                    pax_insektenkiosk,
                                    apus_apus,
                                    class_aves,
                                ],
                                spacing="sm",
                            )
                        ],
                        className="col-md-6",
                    ),
                    dmc.Col(
                        [
                            dmc.Stack(
                                [
                                    dmc.Text(
                                        "Documentation", size="1.2rem", weight=500
                                    ),
                                    quickstart_card,
                                    doc_card,
                                ],
                                spacing="sm",
                            ),
                            dmc.Space(h=30),
                            dmc.Stack(
                                [
                                    dmc.Group(
                                        [
                                            dmc.Text(
                                                "Latest Annotations",
                                                size="1.2rem",
                                                weight=500,
                                            ),
                                            dmc.Anchor(
                                                dmc.Text(
                                                    "See all", size="1.2rem", weight=500
                                                ),
                                                href=PATH_PREFIX + "annotations",
                                            ),
                                        ],
                                        position="apart",
                                    ),
                                    dmc.Stack(id="annots_card_stack", spacing="sm"),
                                ],
                                spacing="sm",
                            ),
                            dmc.Space(h=30),
                        ],
                        className="col-md-6",
                    ),
                ],
                gutter="xl",
            ),
            dmc.Affix(not_yet_func_alert, position={"bottom": 30, "right": 30}),
        ],
        fluid=False,
    )


@callback(Output("annots_card_stack", "children"), Input("url", "href"))
def update_latest_annots(href):
    annots = get_annotations(auth_cookie=flask.request.cookies.get("auth"))
    annot_cards = []
    for i in range(min(4, len(annots))):
        annot_cards.append(
            dmc.Anchor(
                [
                    dmc.Card(
                        children=[
                            dmc.Group(
                                [
                                    dmc.Group(
                                        [
                                            dmc.Avatar(
                                                annots[i].user.initials,
                                                radius="xl",
                                                color="blue",
                                            ),
                                            dmc.Text(
                                                annots[i].user.full_name, weight=500
                                            ),
                                        ]
                                    ),
                                    dmc.Badge(
                                        beautify_timedelta(
                                            datetime.datetime.now().astimezone(
                                                datetime.timezone.utc
                                            )
                                            - annots[i].timestamp
                                        ),
                                        color="teal",
                                    ),
                                ],
                                position="apart",
                            ),
                            dmc.Text(annots[i].title[:80]),
                        ],
                        withBorder=True,
                    )
                ],
                href=PATH_PREFIX + f"annotations?annot_id={annots[i].id}",
                target="_blank",
                variant="text",
            )
        )
    return annot_cards
