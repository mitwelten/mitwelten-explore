import dash
from dash import html, dcc, callback, Input, Output, no_update
import flask
import dash_mantine_components as dmc
from configuration import PATH_PREFIX
from dashboard.styles import icons, get_icon, icon_urls
from dashboard.api_clients.userdata_client import get_annotations
from dashboard.utils.text_utils import beautify_timedelta
import datetime

dash.register_page(__name__, path="/")


class DashboardCard:
    def __init__(self, title, subtitle, icon, url, color="#38D9A9"):
        self.title = title
        self.subtitle = subtitle
        self.icon = icon
        self.url = url
        self.color = color

    def get_card(self):
        return dmc.Anchor(
            [
                dmc.Card(
                    [
                        dmc.Group(
                            [
                                dmc.MediaQuery(
                                    get_icon(icon=self.icon, width="1.5rem"),
                                    smallerThan="xl",
                                    styles={"display": "none"},
                                ),
                                dmc.Stack(
                                    [
                                        dmc.Text(
                                            self.title,
                                            size="1.2rem",
                                            weight=500,
                                        ),
                                        dmc.Text(
                                            self.subtitle,
                                            size="1rem",
                                            italic=True,
                                            weight=300,
                                        ),
                                    ],
                                    spacing=0,
                                ),
                            ],
                            style={"rowGap": "1px"},
                        ),
                    ],
                    withBorder=True,
                    style={"borderColor": self.color, "borderWidth": "2px"},
                    shadow="sm",
                    py=8,
                )
            ],
            href=PATH_PREFIX + self.url,
            target="_blank",
        )


taxon_dashboard_data = [
    DashboardCard(
        title="Eisvogel",
        subtitle="Alcedo atthis",
        icon=icons.bird,
        url="viz/taxon/2475532",
    ),
    DashboardCard(
        title="Hummeln",
        subtitle="Bombus",
        icon=icons.bee,
        url="viz/taxon/1340278",
    ),
    DashboardCard(
        title="Mauersegler",
        subtitle="Apus apus",
        icon=icons.bird,
        url="viz/taxon/5228676",
    ),
    DashboardCard(
        title="Insekten",
        subtitle="Insecta",
        icon=icons.bee,
        url="viz/taxon/216",
    ),
    DashboardCard(
        title="Schwebfliege (GBIF)",
        subtitle="Syrphidae",
        icon=icon_urls.gbif,
        url="viz/taxon/6920?gbif_data=true",
    ),
]

compare_dashboard_data = [
    DashboardCard(
        title="Pax Counters",
        subtitle="Reinacherheide",
        icon=icons.multi_chart,
        color="#748FFC",
        url="viz/compare?datasets=%5B%7B%27type%27%3A+%27pax%27%2C+%27deployment_id%27%3A+1571%2C+%27node_label%27%3A+%272858-2292%27%7D%2C+%7B%27type%27%3A+%27pax%27%2C+%27deployment_id%27%3A+1540%2C+%27node_label%27%3A+%273816-0674%27%7D%2C+%7B%27type%27%3A+%27pax%27%2C+%27deployment_id%27%3A+1491%2C+%27node_label%27%3A+%274133-4945%27%7D%2C+%7B%27type%27%3A+%27pax%27%2C+%27deployment_id%27%3A+1464%2C+%27node_label%27%3A+%270859-4643%27%7D%2C+%7B%27type%27%3A+%27pax%27%2C+%27deployment_id%27%3A+1431%2C+%27node_label%27%3A+%272371-0262%27%7D%2C+%7B%27type%27%3A+%27pax%27%2C+%27deployment_id%27%3A+1406%2C+%27node_label%27%3A+%270872-2989%27%7D%5D&cfg=%5B%7B%27normalize%27%3A+False%7D%2C+%7B%27normalize%27%3A+False%7D%2C+%7B%27normalize%27%3A+False%7D%2C+%7B%27normalize%27%3A+False%7D%2C+%7B%27normalize%27%3A+False%7D%2C+%7B%27normalize%27%3A+False%7D%5D&bucket=1h&from=2023-06-09T12%3A53%3A55",
    ),
    DashboardCard(
        title="Pollinators",
        subtitle="Compare Classes",
        icon=icons.multi_chart,
        color="#748FFC",
        url="viz/compare?datasets=%5B%7B%27type%27%3A+%27pollinators%27%2C+%27deployment_id%27%3A+None%2C+%27pollinator_class%27%3A+%27fliege%27%7D%2C+%7B%27type%27%3A+%27pollinators%27%2C+%27deployment_id%27%3A+None%2C+%27pollinator_class%27%3A+%27wildbiene%27%7D%2C+%7B%27type%27%3A+%27pollinators%27%2C+%27deployment_id%27%3A+None%2C+%27pollinator_class%27%3A+%27schwebfliege%27%7D%2C+%7B%27type%27%3A+%27pollinators%27%2C+%27deployment_id%27%3A+None%2C+%27pollinator_class%27%3A+%27hummel%27%7D%2C+%7B%27type%27%3A+%27pollinators%27%2C+%27deployment_id%27%3A+None%2C+%27pollinator_class%27%3A+%27honigbiene%27%7D%5D&cfg=%5B%7B%27confidence%27%3A+0.6%2C+%27normalize%27%3A+False%7D%2C+%7B%27confidence%27%3A+0.6%2C+%27normalize%27%3A+False%7D%2C+%7B%27confidence%27%3A+0.6%2C+%27normalize%27%3A+False%7D%2C+%7B%27confidence%27%3A+0.6%2C+%27normalize%27%3A+False%7D%2C+%7B%27confidence%27%3A+0.6%2C+%27normalize%27%3A+False%7D%5D&bucket=1w&from=2021-05-26T04%3A08%3A16",
    ),
    DashboardCard(
        title="Lufttemperatur & Honigbienen",
        subtitle="",
        icon=icons.multi_chart,
        color="#748FFC",
        url="viz/compare?datasets=%5B%7B%27type%27%3A+%27birds%27%2C+%27datum_id%27%3A+1334757%2C+%27label_de%27%3A+%27Honigbienen%27%2C+%27label_en%27%3A+%27Honey+Bee%27%2C+%27label_sci%27%3A+%27Apis%27%2C+%27rank%27%3A+%27GENUS%27%2C+%27deployment_filter%27%3A+%5B%5D%7D%2C+%7B%27type%27%3A+%27meteodata%27%2C+%27param_id%27%3A+%27tre200h0%27%2C+%27station_id%27%3A+%27KAARL%27%2C+%27param_desc%27%3A+%27Lufttemperatur+2+m+über+Boden%3AStundenmittel%27%2C+%27unit%27%3A+%27°C%27%2C+%27station_name%27%3A+%27Arlesheim%27%7D%5D&cfg=%5B%7B%27confidence%27%3A+0.6%2C+%27normalize%27%3A+False%7D%2C+%7B%27agg%27%3A+%27mean%27%2C+%27normalize%27%3A+False%7D%5D&bucket=3h&from=2022-05-11T14%3A44%3A31&to=2022-09-06T18%3A41%3A43",
    ),
    DashboardCard(
        title="Niederschlag & Insekten",
        subtitle="",
        icon=icons.multi_chart,
        color="#748FFC",
        url="viz/compare?datasets=%5B%7B%27type%27%3A+%27birds%27%2C+%27datum_id%27%3A+216%2C+%27label_de%27%3A+%27Insekten%27%2C+%27label_en%27%3A+%27Insect%27%2C+%27label_sci%27%3A+%27Insecta%27%2C+%27rank%27%3A+%27CLASS%27%2C+%27deployment_filter%27%3A+%5B%5D%7D%2C+%7B%27type%27%3A+%27meteodata%27%2C+%27param_id%27%3A+%27rre150h0%27%2C+%27station_id%27%3A+%27KADER%27%2C+%27param_desc%27%3A+%27Niederschlag%3AStundensumme%27%2C+%27unit%27%3A+%27mm%27%2C+%27station_name%27%3A+%27Basel+%2F+Dreispitz%27%7D%5D&cfg=%5B%7B%27confidence%27%3A+0.6%2C+%27normalize%27%3A+False%7D%2C+%7B%27agg%27%3A+%27sum%27%2C+%27normalize%27%3A+False%7D%5D&bucket=2h&from=2022-06-20T21%3A30%3A50&to=2022-06-25T11%3A24%3A11",
    ),
]

map_dashboard_data = [
    DashboardCard(
        title="Eisvogel & Mauersegler",
        subtitle="",
        icon=icons.map_chart,
        color="#69DB7C",
        url="viz/map?datasets=%5B%7B%27type%27%3A+%27birds%27%2C+%27datum_id%27%3A+2475532%2C+%27label_de%27%3A+%27Eisvogel%27%2C+%27label_en%27%3A+%27Common+Kingfisher%27%2C+%27label_sci%27%3A+%27Alcedo+atthis%27%2C+%27rank%27%3A+%27SPECIES%27%2C+%27deployment_filter%27%3A+%5B%5D%7D%2C+%7B%27type%27%3A+%27birds%27%2C+%27datum_id%27%3A+5228676%2C+%27label_de%27%3A+%27Mauersegler%27%2C+%27label_en%27%3A+%27Common+Swift%27%2C+%27label_sci%27%3A+%27Apus+apus%27%2C+%27rank%27%3A+%27SPECIES%27%2C+%27deployment_filter%27%3A+%5B%5D%7D%5D&cfg=%5B%7B%27confidence%27%3A+0.6%2C+%27normalize%27%3A+False%7D%2C+%7B%27confidence%27%3A+0.6%2C+%27normalize%27%3A+False%7D%5D&from=2020-08-01T00%3A00%3A00&to=2023-06-20T13%3A36%3A24.143343",
    ),
    DashboardCard(
        title="All PAX Counters",
        subtitle="",
        icon=icons.map_chart,
        color="#69DB7C",
        url="viz/map?datasets=%5B%7B%27type%27%3A+%27multi_pax%27%2C+%27deployment_id%27%3A+None%7D%5D&cfg=%5B%7B%7D%5D&from=2021-01-01T00%3A00%3A00&maptype=bubble",
    ),
    DashboardCard(
        title="Bienen & Fliegen",
        subtitle="",
        icon=icons.map_chart,
        color="#69DB7C",
        url="viz/map?datasets=%5B%7B%27type%27%3A+%27birds%27%2C+%27datum_id%27%3A+4334%2C+%27label_de%27%3A+%27Echte+Bienen%27%2C+%27label_en%27%3A+%27Euglossine%27%2C+%27label_sci%27%3A+%27Apidae%27%2C+%27rank%27%3A+%27FAMILY%27%2C+%27deployment_filter%27%3A+%5B%5D%7D%2C+%7B%27type%27%3A+%27birds%27%2C+%27datum_id%27%3A+5564%2C+%27label_de%27%3A+None%2C+%27label_en%27%3A+%27House+Fly%27%2C+%27label_sci%27%3A+%27Muscidae%27%2C+%27rank%27%3A+%27FAMILY%27%2C+%27deployment_filter%27%3A+%5B%5D%7D%5D&cfg=%5B%7B%27confidence%27%3A+0.6%2C+%27normalize%27%3A+False%7D%2C+%7B%27confidence%27%3A+0.6%2C+%27normalize%27%3A+False%7D%5D&from=2020-08-01T00%3A00%3A00",
    ),
]

ts_dashboard_data = [
    DashboardCard(
        title="PAX Counter",
        subtitle="Insektenkiosk",
        icon=icons.pax_counter,
        color="#A9E34B",
        url="viz/timeseries?trace=%7B%27type%27%3A+%27pax%27%2C+%27deployment_id%27%3A+865%2C+%27node_label%27%3A+%279231-7621%27%2C+%27period_from%27%3A+%272023-04-20T22%3A00%3A00%2B00%3A00%27%2C+%27period_to%27%3A+None%7D&agg=None&bucket=2h&from=2023-04-30T02%3A41%3A27",
    ),
    DashboardCard(
        title="Bird Detections",
        subtitle="All Deployments",
        icon=icons.bird,
        color="#A9E34B",
        url="viz/timeseries?trace=%7B%27type%27%3A+%27birds%27%2C+%27datum_id%27%3A+212%2C+%27label_de%27%3A+None%2C+%27label_en%27%3A+%27Bird%27%2C+%27label_sci%27%3A+%27Aves%27%2C+%27rank%27%3A+%27CLASS%27%2C+%27deployment_filter%27%3A+%5B%5D%7D&agg=None&bucket=1d&from=2021-03-04T19%3A07%3A36&confidence=0.7",
    ),
    DashboardCard(
        title="Globalstrahlung",
        subtitle="Binningen",
        icon=icons.single_chart,
        color="#A9E34B",
        url="viz/timeseries?trace=%7B%27type%27%3A+%27meteodata%27%2C+%27param_id%27%3A+%27gre000h0%27%2C+%27station_id%27%3A+%27BAS%27%2C+%27param_desc%27%3A+%27Globalstrahlung%3AStundenmittel%27%2C+%27unit%27%3A+%27W%2Fm²%27%2C+%27station_name%27%3A+%27Basel+%2F+Binningen%27%7D&agg=mean&bucket=1d&from=2020-08-01T00%3A00%3A00&to=2023-06-24T12%3A40%3A29.829610",
    ),
    DashboardCard(
        title="Pollenkonzentration",
        subtitle="Buche",
        icon=icons.single_chart,
        color="#A9E34B",
        url="viz/timeseries?trace=%7B%27type%27%3A+%27meteodata%27%2C+%27param_id%27%3A+%27kafagud0%27%2C+%27station_id%27%3A+%27PBS%27%2C+%27param_desc%27%3A+%27Buche%3Amittlere+tägliche+Pollenkonzentration%27%2C+%27unit%27%3A+%27No%2Fm³%27%2C+%27station_name%27%3A+%27Basel%27%7D&agg=mean&bucket=1d&from=2023-03-18T11%3A52%3A44",
    ),
]

deployment_dashboard_data = [
    DashboardCard(
        title="Audio Logger 679",
        subtitle="Reinacherheide",
        icon=icons.bird,
        color="#3BC9DB",
        url="viz/deployment?dataset=%7B%27type%27%3A+%27birds_by_depl%27%2C+%27deployment_id%27%3A+%5B679%5D%7D",
    ),
    DashboardCard(
        title="Pollinator Cams",
        subtitle="Merian Gärten",
        icon=icons.bee,
        color="#3BC9DB",
        url="viz/deployment?dataset=%7B%27type%27%3A+%27pollinators%27%2C+%27deployment_id%27%3A+%5B33%2C+35%2C+37%2C+39%2C+40%2C+41%2C+88%2C+43%2C+44%2C+45%2C+47%2C+48%2C+51%2C+56%2C+57%2C+58%2C+59%2C+60%5D%2C+%27pollinator_class%27%3A+None%7D",
    ),
    DashboardCard(
        title="Audio Logger 64",
        subtitle="Gundeli",
        icon=icons.bird,
        color="#3BC9DB",
        url="viz/deployment?dataset=%7B%27type%27%3A+%27birds_by_depl%27%2C+%27deployment_id%27%3A+%5B64%5D%7D",
    ),
]

not_yet_func_alert = dmc.Alert(
    dmc.Text(
        "This website is currently under development and is not yet functional.",
    ),
    title=dmc.Text("Work in progress", size="1.1rem"),
    color="yellow",
    withCloseButton=True,
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
            className="shadow-sm",
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
            className="shadow-sm",
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

SHOW_MORE_LABEL = "Show More"
SPOILER_MAH = 83


def layout(**kwargs):
    return dmc.Container(
        [
            dcc.Location("annots_url", refresh=False),
            dmc.Space(h=12),
            dmc.Stack(
                [
                    dmc.Title("MITWELTEN EXPLORE"),
                    dmc.Group(
                        [
                            dmc.Text(
                                "Explore the Biodiversity in and around",
                                size="xl",
                                weight=300,
                            ),
                            dmc.Text("Basel", size="xl", color="teal.5", weight=400),
                        ],
                        spacing=4,
                    ),
                ],
                spacing=4,
            ),
            dmc.Space(h=18),
            dmc.Grid(
                [
                    dmc.Col(
                        [
                            dmc.Stack(
                                [
                                    dmc.Text(
                                        "Selected Dashboards", size="1.2rem", weight=500
                                    ),
                                    dmc.Divider(),
                                    dmc.Group(
                                        [
                                            dmc.Text(
                                                "Taxon Dashboards",
                                                size="1rem",
                                                weight=500,
                                            ),
                                            dmc.Text(
                                                "Explore the detections of a taxon",
                                                size="md",
                                                weight=300,
                                            ),
                                        ]
                                    ),
                                    dmc.Spoiler(
                                        children=[
                                            dmc.SimpleGrid(
                                                children=[
                                                    d.get_card()
                                                    for d in taxon_dashboard_data
                                                ],
                                                cols=3,
                                                breakpoints=[
                                                    {
                                                        "maxWidth": 500,
                                                        "cols": 2,
                                                        "spacing": "sm",
                                                    },
                                                ],
                                            ),
                                            dmc.Space(h=8),
                                        ],
                                        showLabel=SHOW_MORE_LABEL,
                                        hideLabel="Hide",
                                        maxHeight=SPOILER_MAH,
                                    ),
                                    dmc.Group(
                                        [
                                            dmc.Text(
                                                "Comparison Dashboards",
                                                size="1rem",
                                                weight=500,
                                            ),
                                            dmc.Text(
                                                "Compare multiple datasets",
                                                size="md",
                                                weight=300,
                                            ),
                                        ]
                                    ),
                                    dmc.Spoiler(
                                        children=[
                                            dmc.SimpleGrid(
                                                children=[
                                                    d.get_card()
                                                    for d in compare_dashboard_data
                                                ],
                                                cols=2,
                                            ),
                                            dmc.Space(h=8),
                                        ],
                                        showLabel=SHOW_MORE_LABEL,
                                        hideLabel="Hide",
                                        maxHeight=SPOILER_MAH,
                                    ),
                                    dmc.Group(
                                        [
                                            dmc.Text(
                                                "Map Dashboards",
                                                size="1rem",
                                                weight=500,
                                            ),
                                            dmc.Text(
                                                "Explore the spatial distribution",
                                                size="md",
                                                weight=300,
                                            ),
                                        ]
                                    ),
                                    dmc.Spoiler(
                                        children=[
                                            dmc.SimpleGrid(
                                                children=[
                                                    d.get_card()
                                                    for d in map_dashboard_data
                                                ],
                                                cols=2,
                                            ),
                                            dmc.Space(h=8),
                                        ],
                                        showLabel=SHOW_MORE_LABEL,
                                        hideLabel="Hide",
                                        maxHeight=55,
                                    ),
                                    dmc.Group(
                                        [
                                            dmc.Text(
                                                "Timeseries Dashboards",
                                                size="1rem",
                                                weight=500,
                                            ),
                                            dmc.Text(
                                                "Analyze a single dataset",
                                                size="md",
                                                weight=300,
                                            ),
                                        ]
                                    ),
                                    dmc.Spoiler(
                                        children=[
                                            dmc.SimpleGrid(
                                                children=[
                                                    d.get_card()
                                                    for d in ts_dashboard_data
                                                ],
                                                cols=3,
                                                pb=12,
                                                breakpoints=[
                                                    {
                                                        "maxWidth": 900,
                                                        "cols": 2,
                                                        "spacing": "sm",
                                                    },
                                                ],
                                            ),
                                            dmc.Space(h=8),
                                        ],
                                        showLabel=SHOW_MORE_LABEL,
                                        hideLabel="Hide",
                                        maxHeight=SPOILER_MAH,
                                    ),
                                    dmc.Group(
                                        [
                                            dmc.Text(
                                                "Deployment Dashboards",
                                                size="1rem",
                                                weight=500,
                                            ),
                                            dmc.Text(
                                                "Explore the Biodiversity in a specific area",
                                                size="md",
                                                weight=300,
                                            ),
                                        ]
                                    ),
                                    dmc.Spoiler(
                                        children=[
                                            dmc.SimpleGrid(
                                                children=[
                                                    d.get_card()
                                                    for d in deployment_dashboard_data
                                                ],
                                                cols=2,
                                                pb=12,
                                            ),
                                            dmc.Space(h=8),
                                        ],
                                        showLabel=SHOW_MORE_LABEL,
                                        hideLabel="Hide",
                                        maxHeight=SPOILER_MAH,
                                    ),
                                ],
                                spacing="sm",
                                pr=12,
                            )
                        ],
                        className="col-md-8",
                    ),
                    dmc.Col(
                        [
                            dmc.Stack(
                                [
                                    dmc.Text(
                                        "Documentation", size="1.2rem", weight=500
                                    ),
                                    dmc.Divider(),
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
                                    dmc.Divider(),
                                    dmc.Stack(id="annots_card_stack", spacing="sm"),
                                ],
                                spacing="sm",
                            ),
                            dmc.Space(h=30),
                        ],
                        className="col-md-4",
                    ),
                ],
                gutter="xl",
            ),
            dmc.Affix(not_yet_func_alert, position={"bottom": 30, "right": 30}),
        ],
        className="container-xl",
    )


@callback(Output("annots_card_stack", "children"), Input("annots_url", "href"))
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
                        shadow="sm",
                    )
                ],
                href=PATH_PREFIX + f"annotations?annot_id={annots[i].id}",
                target="_blank",
                variant="text",
            )
        )
    return annot_cards
