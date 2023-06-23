import dash_mantine_components as dmc


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
            withArrow=arrow,
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
