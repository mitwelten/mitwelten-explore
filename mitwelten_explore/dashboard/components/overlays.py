import dash_mantine_components as dmc
from dashboard.styles import icons, get_icon


def chart_loading_overlay(children, position="left"):
    return dmc.LoadingOverlay(
        children,
        overlayOpacity=0,
        transitionDuration=400,
        loader=dmc.Card(
            dmc.Group(
                [
                    dmc.Loader(
                        size="sm",
                        color="teal.5",
                    ),
                    dmc.Text(
                        "Loading",
                        color="gray.9",
                        weight=500,
                        size="md",
                    ),
                ],
            ),
            style={
                "position": "absolute",
                "bottom": 10,
                position: 10,
                "backgroundColor": "rgba(245, 245, 245,0.8)",
            },
            py=3,
            px=5,
        ),
    )


def tooltip(
    children,
    text,
    position="left",
    floating=False,
    arrow=True,
    opendelay=100,
    color="indigo.9",
):
    if floating:
        return dmc.FloatingTooltip(
            children=children,
            label=text,
            position=position,
            color=color,
        )
    else:
        return dmc.Tooltip(
            children=children,
            label=dmc.Text(text, weight=300),
            position=position,
            withArrow=arrow,
            openDelay=opendelay,
            color=color,
        )


def datasource_indicator(datasources: dict):
    children = []
    titles = []
    for key in datasources.keys():
        titles.append(key)
        for ds in datasources[key]:
            children.append(
                dmc.Anchor(
                    dmc.Text(
                        [ds.get("name"), " ", get_icon(icons.open_in_new_tab)],
                        size="xs",
                    ),
                    href=ds.get("reference"),
                    target="_blank",
                )
            )

    return dmc.HoverCard(
        withArrow=False,
        shadow="md",
        position="top-start",
        children=[
            dmc.HoverCardTarget(
                dmc.Group(
                    [
                        dmc.Group(
                            [
                                # get_icon(icons.copyright),
                                get_icon(icons.database),
                            ],
                            spacing=1,
                        ),
                    ]
                    + [dmc.Text(" | ".join(titles), size="xs", color="dimmed")],
                    spacing=4,
                    style={"cursor": "pointer"},
                )
            ),
            dmc.HoverCardDropdown(
                [
                    dmc.Text("Data Sources", weight=500),
                    dmc.Stack(
                        children,
                        spacing=3,
                        style={
                            "maxHeight": "60vh",
                            "maxWidth": "50vw",
                            "overflowY": "auto",
                        },
                    ),
                ],
            ),
        ],
    )
