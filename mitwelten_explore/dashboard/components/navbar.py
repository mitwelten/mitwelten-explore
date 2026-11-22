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
            dmc.Box(
                dmc.Text("MITWELTEN EXPLORE", fw=700, lts=0),
                visibleFrom="lg",
            ),
        ],
        gap=2,
        style=nav_style_inactive,
        id="nav_header_home",
    ),
    href=PATH_PREFIX,
    c="inherit",
)

nav_dataset_target = dmc.Menu(
    [
        dmc.MenuTarget(
            dmc.Group(
                [
                    dmc.Box(
                        dmc.Text("Datasets", fw=500),
                        visibleFrom="lg",
                    ),
                    dmc.Box(
                        get_icon(icon=icons.database, width=24),
                        hiddenFrom="lg",
                    ),
                    dmc.Box(
                        get_icon(icon=icons.arrow_down_expand, width=16),
                        visibleFrom="lg",
                    ),
                ],
                gap=4,
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
                    leftSection=get_icon(icons.hierarchy, 24),
                    href=PATH_PREFIX + "select/taxon",
                ),
                dmc.MenuItem(
                    "Mitwelten Pollinators",
                    leftSection=get_icon(icons.bee, 24),
                    href=PATH_PREFIX + "select/pollinator",
                ),
                dmc.MenuItem(
                    "Mitwelten Bird Diversity",
                    leftSection=get_icon(icons.bird, 24),
                    href=PATH_PREFIX + "select/bird",
                ),
                dmc.MenuItem(
                    "Meteodata",
                    leftSection=get_icon(icons.meteoswiss, 24),
                    href=PATH_PREFIX + "select/meteo",
                ),
                dmc.MenuItem(
                    "Mitwelten PAX",
                    leftSection=get_icon(icons.pax_counter, 24),
                    href=PATH_PREFIX + "select/pax",
                ),
                dmc.MenuDivider(),
                dmc.MenuItem(
                    "All Datasets",
                    leftSection=get_icon(icons.database, 24),
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
            dmc.Box(
                dmc.Text("Collection", fw=500),
                visibleFrom="lg",
            ),
            dmc.Box(
                get_icon(icon=icons.bookmark, width=24),
                hiddenFrom="lg",
            ),
            dmc.Box(
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
                visibleFrom="sm",
            ),
        ],
        gap=4,
        id="nav_header_collection",
        style=nav_style_inactive,
        px=NAV_TARGET_PADDING_X,
        wrap="nowrap",
    ),
    href=PATH_PREFIX + "collection",
    c="inherit",
    target="_self",
)

nav_viz_target = dmc.Menu(
    [
        dmc.MenuTarget(
            dmc.Group(
                [
                    dmc.Box(
                        dmc.Text("Visualize", fw=500),
                        visibleFrom="lg",
                    ),
                    dmc.Box(
                        get_icon(icon=icons.scatter_chart, width=24),
                        hiddenFrom="lg",
                    ),
                    dmc.Box(
                        get_icon(icon=icons.arrow_down_expand, width=16),
                        visibleFrom="lg",
                    ),
                ],
                gap=4,
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
                    leftSection=get_icon(icons.single_chart, 16),
                    href=PATH_PREFIX + "viz/timeseries",
                ),
                dmc.MenuItem(
                    "Compare Datasets",
                    leftSection=get_icon(icons.multi_chart, 16),
                    href=PATH_PREFIX + "viz/compare",
                ),
                dmc.MenuItem(
                    "Map",
                    leftSection=get_icon(icons.map_chart, 16),
                    href=PATH_PREFIX + "viz/map",
                ),
                dmc.MenuItem(
                    "Deployment",
                    leftSection=get_icon(icons.location_poi, 16),
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
            dmc.Box(
                dmc.Text("Annotations", fw=500),
                visibleFrom="lg",
            ),
            dmc.Box(
                get_icon(icon=icons.annotation_bank, width=24),
                hiddenFrom="lg",
            ),
        ],
        gap="xs",
        id="nav_header_annotations",
        px=NAV_TARGET_PADDING_X,
        style=nav_style_inactive,
    ),
    href=PATH_PREFIX + "annotations",
    c="inherit",
)

nav_docs_target = dmc.Anchor(
    dmc.Group(
        [
            dmc.Box(
                dmc.Text("Docs", fw=500),
                visibleFrom="lg",
            ),
            dmc.Box(
                get_icon(icons.info, width=24),
                hiddenFrom="lg",
            ),
        ],
        gap="xs",
        style=nav_style_inactive,
        id="nav_header_docs",
        px=NAV_TARGET_PADDING_X,
    ),
    href=PATH_PREFIX + "docs",
    c="inherit",
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
                dmc.Group(theme_switch, justify="center"),
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
                            dmc.Box(
                                dmc.Stack(
                                    [
                                        dmc.Text(
                                            "",
                                            id="username_nav",
                                            fw=600,
                                            size="sm",
                                        ),
                                        dmc.Text(
                                            "",
                                            size="xs",
                                            id="fullname_nav",
                                        ),
                                    ],
                                    gap=0,
                                ),
                                visibleFrom="lg",
                            ),
                            dmc.Box(
                                get_icon(icon=icons.arrow_down_expand, width=16),
                                visibleFrom="sm",
                            ),
                        ],
                        gap=6,
                        style={"cursor": "pointer"},
                    ),
                ),
                dmc.MenuDropdown(
                    [
                        dmc.MenuItem(
                            "My Annotations",
                            leftSection=get_icon(icon=icons.annotation_bank, width=16),
                            href=PATH_PREFIX + "annotations?my_annotations=true",
                        ),
                        dmc.MenuItem(
                            dmc.Button(
                                "Clear collection",
                                id="clear_collection_button",
                                variant="subtle",
                                size="compact-sm",
                                color="red",
                                pl=0,
                            ),
                            leftSection=get_icon(icon=icons.trash, width=16),
                        ),
                        dmc.MenuDivider(),
                        dmc.MenuItem(
                            "Logout",
                            leftSection=get_icon(icons.logout, width=16),
                            href="/logout",
                            refresh=True,
                        ),
                    ]
                ),
            ],
            trigger="hover",
        ),
    ],
    gap=0,
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
            gap=0,
            wrap="nowrap",
            mt=1,
        ),
        dmc.Group(
            [
                nav_docs_target,
                nav_settings_target,
                nav_user_element,
            ],
            gap=0,
            wrap="nowrap",
            mt=1,
        ),
    ],
    style={"width": "100%", "height": "45px"},
    className="shadow-sm",
    justify="space-between",
    gap="xs",
    wrap="nowrap",
)
