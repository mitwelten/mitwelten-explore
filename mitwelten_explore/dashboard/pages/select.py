import dash
from dash import html, dcc, callback, Input, Output, no_update
import flask
import dash_mantine_components as dmc
from dashboard.styles import icons, get_icon
from configuration import PATH_PREFIX

dash.register_page(__name__, path_template="/select")


class DSCard:
    def __init__(self, name, icon, text, url, color="indigo"):
        self.name = name
        self.icon = icon
        self.text = text
        self.url = url
        self.color = color

    def to_card(self):
        return dmc.Anchor(
            [
                dmc.Alert(
                    title=dmc.Group(
                        [
                            get_icon(icon=self.icon, width="1.5rem"),
                            dmc.Text(self.name, size="1.2rem"),
                        ]
                    ),
                    children=[dmc.Text(self.text)],
                    color=self.color,
                    variant="text",
                )
            ],
            href=PATH_PREFIX + self.url if self.url else None,
        )

    def to_card_no_link(self):
        return dmc.Alert(
            title=dmc.Group(
                [
                            get_icon(icon=self.icon, width="1.5rem"),
                            dmc.Text(self.name, size="1.2rem"),
                    dmc.Badge("Not yet available", color="pink"),
                ],
            ),
            children=[dmc.Text(self.text)],
            color=self.color,
            variant="text",
        )


cards = [
    DSCard(
        name="Mitwelten Pollinators",
        icon=icons.bee,
        text="Results of the Mitwelten Pollinator Study",
        url="select/pollinator",
        color="teal",
    ),
    DSCard(
        name="Mitwelten Birds",
        icon=icons.bird,
        text="Results of the Mitwelten Bird Study",
        url="select/taxon",
        color="teal",
    ),
    DSCard(
        name="Meteodata",
        icon=icons.meteoswiss,
        text="Meteodata provided by MeteoSchweiz",
        url="select/meteo",
        color="red",
    ),
    DSCard(
        name="PAX Data",
        icon=icons.pax_counter,
        text="Presence of Smartphones",
        url="select/pax",
        color="cyan",
    ),
    DSCard(
        name="Environment Sensor Data",
        icon=icons.env_sensors,
        text="Temperature, Humidity and Moisture measured with LoRa Sensor Nodes",
        url="select/env",
        color="lime",
    ),
]

cards_in_progress = [
    DSCard(
        name="GBIF Occurences",
        icon=icons.world_explore,
        text="Seen species by other institutions",
        url=None,
        color="gray",
    ),
    DSCard(
        name="Location Characteristics",
        icon=icons.search_location,
        text="Characteristics of the measurement locations",
        url=None,
        color="gray",
    ),
]


layout = dmc.Container(
    [
        dmc.Text(
            "Datasets",
            size="1.2rem",
            weight=500,
        ),
        dmc.Space(h=20),
        dmc.Divider(),
        dmc.Space(h=20),
        dmc.SimpleGrid(
            cols=2,
            children=[c.to_card() for c in cards]
            + [c.to_card_no_link() for c in cards_in_progress],
        ),
    ],
)
