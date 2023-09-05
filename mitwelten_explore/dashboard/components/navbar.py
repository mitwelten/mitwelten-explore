from dash import html
import dash_mantine_components as dmc
import dash_bootstrap_components as dbc
from dash_bootstrap_templates import ThemeSwitchAIO
from configuration import *
from dashboard.styles import icons, get_icon

theme_switch = ThemeSwitchAIO(
    aio_id="theme",
    themes=[dbc.themes.BOOTSTRAP, dbc.themes.SLATE],
    switch_props={"persistence": True, "persistence_type": "local"},
)

NAV_TARGET_PADDING_X = 12
nav_style_inactive = {
    "cursor": "pointer",
    "height": "39px",
    "borderTop": "3px solid rgba(0,0,0,0)",
}


nav_logo_target = dmc.Anchor(
    dmc.Group(
        [
            html.Img(src=MITWELTEN_LOGO, height="36px"),
            dmc.MediaQuery(
                dmc.Text("MITWELTEN EXPLORE", weight=700, lts=0),
                smallerThan="lg",
                styles={"display": "none"},
            ),
        ],
        spacing=2,
        style=nav_style_inactive,
        id="nav_header_home",
    ),
    href=PATH_PREFIX,
    variant="text",
)

nav_dataset_target = dmc.Menu(
    [
        dmc.MenuTarget(
            dmc.Group(
                [
                    dmc.MediaQuery(
                        dmc.Text("Datasets", weight=500),
                        smallerThan="lg",
                        styles={"display": "none"},
                    ),
                    dmc.MediaQuery(
                        get_icon(icon=icons.database, width=24),
                        largerThan="lg",
                        styles={"display": "none"},
                    ),
                    dmc.MediaQuery(
                        get_icon(icon=icons.arrow_down_expand, width=16),
                        smallerThan="lg",
                        styles={"display": "none"},
                    ),
                ],
                spacing=4,
                style=nav_style_inactive,
                # id={"role":"navbar_target", "index":"select"},
                id="nav_header_select",
                px=NAV_TARGET_PADDING_X,
            ),
        ),
        dmc.MenuDropdown(
            [
                dmc.MenuLabel("Datasets"),
                dmc.MenuItem(
                    "Detections by Taxonomy",
                    icon=get_icon(icons.hierarchy, 24),
                    href=PATH_PREFIX + "select/taxon",
                ),
                dmc.MenuItem(
                    "Mitwelten Pollinators",
                    icon=get_icon(icons.bee, 24),
                    href=PATH_PREFIX + "select/pollinator",
                ),
                dmc.MenuItem(
                    "Mitwelten Bird Diversity",
                    icon=get_icon(icons.bird, 24),
                    href=PATH_PREFIX + "select/bird",
                ),
                dmc.MenuItem(
                    "Meteodata",
                    icon=get_icon(icons.meteoswiss, 24),
                    href=PATH_PREFIX + "select/meteo",
                ),
                dmc.MenuItem(
                    "Mitwelten PAX",
                    icon=get_icon(icons.pax_counter, 24),
                    href=PATH_PREFIX + "select/pax",
                ),
                dmc.MenuDivider(),
                dmc.MenuItem(
                    "All Datasets",
                    icon=get_icon(icons.database, 24),
                    href=PATH_PREFIX + "select",
                ),
            ]
        ),
    ],
    trigger="hover",
    zIndex=500,
)

nav_collection_target = dmc.Anchor(
    dmc.Group(
        [
            dmc.MediaQuery(
                dmc.Text("Collection", weight=500),
                smallerThan="lg",
                styles={"display": "none"},
            ),
            dmc.MediaQuery(
                get_icon(icon=icons.bookmark, width=24),
                largerThan="lg",
                styles={"display": "none"},
            ),
            dmc.MediaQuery(
                dmc.Badge(
                    "0",
                    size="md",
                    variant="filled",
                    color="red",
                    w=20,
                    h=20,
                    p=0,
                    id="sidebar_selected_trace_number",
                ),
                smallerThan="sm",
                styles={"display": "none"},
            ),
        ],
        spacing=4,
        id="nav_header_collection",
        style=nav_style_inactive,
        px=NAV_TARGET_PADDING_X,
        noWrap=True,
    ),
    href=PATH_PREFIX + "collection",
    variant="text",
    target="_self",
)

nav_viz_target = dmc.Menu(
    [
        dmc.MenuTarget(
            dmc.Group(
                [
                    dmc.MediaQuery(
                        dmc.Text("Visualize", weight=500),
                        smallerThan="lg",
                        styles={"display": "none"},
                    ),
                    dmc.MediaQuery(
                        get_icon(icon=icons.scatter_chart, width=24),
                        largerThan="lg",
                        styles={"display": "none"},
                    ),
                    dmc.MediaQuery(
                        get_icon(icon=icons.arrow_down_expand, width=16),
                        smallerThan="lg",
                        styles={"display": "none"},
                    ),
                ],
                spacing=4,
                style=nav_style_inactive,
                px=NAV_TARGET_PADDING_X,
                id="nav_header_viz",
            ),
        ),
        dmc.MenuDropdown(
            [
                dmc.MenuLabel("Visualize"),
                dmc.MenuItem(
                    "Single Time Series",
                    icon=get_icon(icons.single_chart, 16),
                    href=PATH_PREFIX + "viz/timeseries",
                ),
                dmc.MenuItem(
                    "Compare Datasets",
                    icon=get_icon(icons.multi_chart, 16),
                    href=PATH_PREFIX + "viz/compare",
                ),
                dmc.MenuItem(
                    "Map",
                    icon=get_icon(icons.map_chart, 16),
                    href=PATH_PREFIX + "viz/map",
                ),
                dmc.MenuItem(
                    "Deployment",
                    icon=get_icon(icons.location_poi, 16),
                    href=PATH_PREFIX + "viz/deployment",
                ),
            ]
        ),
    ],
    trigger="hover",
    zIndex=500,
)

nav_annotations_target = dmc.Anchor(
    dmc.Group(
        [
            dmc.MediaQuery(
                dmc.Text("Annotations", weight=500),
                smallerThan="lg",
                styles={"display": "none"},
            ),
            dmc.MediaQuery(
                get_icon(icon=icons.annotation_bank, width=24),
                largerThan="lg",
                styles={"display": "none"},
            ),
        ],
        spacing="xs",
        id="nav_header_annotations",
        px=NAV_TARGET_PADDING_X,
        style=nav_style_inactive,
    ),
    href=PATH_PREFIX + "annotations",
    variant="text",
)

nav_docs_target = dmc.Anchor(
    dmc.Group(
        [
            dmc.MediaQuery(
                dmc.Text("Docs", weight=500),
                smallerThan="lg",
                styles={"display": "none"},
            ),
            dmc.MediaQuery(
                get_icon(icons.info, width=24),
                largerThan="lg",
                styles={"display": "none"},
            ),
        ],
        spacing="xs",
        style=nav_style_inactive,
        id="nav_header_docs",
        px=NAV_TARGET_PADDING_X,
    ),
    href=PATH_PREFIX + "docs",
    variant="text",
)


nav_settings_target = dmc.Menu(
    [
        dmc.MenuTarget(
            dmc.Group(
                [
                    get_icon(icons.theme, width=22),
                ],
                px=NAV_TARGET_PADDING_X,
                style={"cursor": "pointer"},
                h="39px",
            ),
        ),
        dmc.MenuDropdown(
            [
                dmc.MenuLabel("Theme"),
                dmc.Group(theme_switch, position="center"),
            ]
        ),
    ],
    trigger="hover",
    zIndex=500,
)

nav_user_element = dmc.Group(
    [
        dmc.Menu(
            [
                dmc.MenuTarget(
                    dmc.Group(
                        [
                            dmc.Avatar(
                                id="avatar_nav",
                                radius="xl",
                                size=32,
                                color="indigo.6",
                                variant="filled",
                            ),
                            dmc.MediaQuery(
                                dmc.Stack(
                                    [
                                        dmc.Text(
                                            "",
                                            id="username_nav",
                                            weight=600,
                                            size="sm",
                                        ),
                                        dmc.Text(
                                            "",
                                            size="xs",
                                            id="fullname_nav",
                                        ),
                                    ],
                                    spacing=0,
                                ),
                                smallerThan="lg",
                                styles={"display": "none"},
                            ),
                            dmc.MediaQuery(
                                get_icon(icon=icons.arrow_down_expand, width=16),
                                smallerThan="sm",
                                styles={"display": "none"},
                            ),
                        ],
                        spacing=6,
                        style={"cursor": "pointer"},
                    ),
                ),
                dmc.MenuDropdown(
                    [
                        dmc.MenuItem(
                            "My Annotations",
                            icon=get_icon(icon=icons.annotation_bank, width=16),
                            href=PATH_PREFIX + "annotations?my_annotations=true",
                        ),
                        dmc.MenuItem(
                            dmc.Button(
                                "Clear collection",
                                id="clear_collection_button",
                                variant="subtle",
                                compact=True,
                                color="red",
                                pl=0,
                            ),
                            icon=get_icon(icon=icons.trash, width=16),
                        ),
                        dmc.MenuDivider(),
                        dmc.MenuItem(
                            "Logout",
                            icon=get_icon(icons.logout, width=16),
                            href="/logout",
                            refresh=True,
                        ),
                    ]
                ),
            ],
            trigger="hover",
        ),
    ],
    spacing=0,
    pr=8,
    pl=NAV_TARGET_PADDING_X,
)

nav_bar = dmc.Group(
    [
        nav_logo_target,
        dmc.Group(
            [
                nav_dataset_target,
                nav_collection_target,
                nav_viz_target,
                nav_annotations_target,
            ],
            spacing=0,
            noWrap=True,
            mt=1,
        ),
        dmc.Group(
            [
                nav_docs_target,
                nav_settings_target,
                nav_user_element,
            ],
            spacing=0,
            noWrap=True,
            mt=1,
        ),
    ],
    style={"width": "100%", "height": "45px"},
    className="shadow-sm",
    position="apart",
    spacing="xs",
    noWrap=True,
)
