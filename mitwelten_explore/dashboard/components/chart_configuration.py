import dash_mantine_components as dmc
from dash_iconify import DashIconify
from dashboard.styles import icons

TS_CHART_TYPES = [
    ["line", dmc.Group([DashIconify(icon=icons.line_chart, width=20), "Line"])],
    [
        "scatter",
        dmc.Group([DashIconify(icon=icons.scatter_chart, width=20), "Scatter"]),
    ],
    ["bar", dmc.Group([DashIconify(icon=icons.bar_chart, width=20), "Bar"])],
    ["area", dmc.Group([DashIconify(icon=icons.area_chart, width=20), "Area"])],
]

TS_CHART_LAYOUTS = [
    ["single", dmc.Group([DashIconify(icon=icons.layout_rect, width=20), "Overlay"])],
    ["subplots", dmc.Group([DashIconify(icon=icons.layout_row, width=20), "Subplots"])],
]


def reload_control(reload_on_zoom_id):
    return dmc.Switch(
        onLabel=DashIconify(icon=icons.sync_on, width=16),
        offLabel=DashIconify(icon=icons.sync_off, width=16),
        color="teal.6",
        checked=True,
        id=reload_on_zoom_id,
        persistence=True,
    )


def timeseries_chart_config_menu(
    chart_type_id=None, reload_on_zoom_id=None, layout_type_id=None, **kwargs
):
    menu_dd_children = []
    if chart_type_id:
        type_radiogroup = dmc.RadioGroup(
            [dmc.Radio(l, value=k) for k, l in TS_CHART_TYPES],
            id=chart_type_id,
            persistence=True,
            value=TS_CHART_TYPES[0][0],
            orientation="vertical",
            size="sm",
            spacing="xs",
            pl=8,
            pb=8,
        )
        menu_dd_children.append(dmc.MenuLabel("Chart Type"))
        menu_dd_children.append(type_radiogroup)
    if reload_on_zoom_id:
        reload_switch = dmc.Switch(
            onLabel=DashIconify(icon=icons.sync_on, width=16),
            offLabel=DashIconify(icon=icons.sync_off, width=16),
            color="indigo.9",
            checked=True,
            id=reload_on_zoom_id,
            persistence=True,
            p=8,
        )
        menu_dd_children.append(dmc.MenuDivider())
        menu_dd_children.append(dmc.MenuLabel("Apply Time Range on Zoom"))
        menu_dd_children.append(reload_switch)

    if layout_type_id:
        layout_type_radiogroup = dmc.RadioGroup(
            [dmc.Radio(l, value=k) for k, l in TS_CHART_LAYOUTS],
            id=layout_type_id,
            persistence=True,
            value=TS_CHART_LAYOUTS[1][0],
            orientation="vertical",
            size="sm",
            spacing="xs",
            pl=8,
            pb=8,
        )

        menu_dd_children.append(dmc.MenuDivider())
        menu_dd_children.append(dmc.MenuLabel("Layout"))
        menu_dd_children.append(layout_type_radiogroup)

    return dmc.Menu(
        [
            dmc.MenuTarget(
                dmc.ActionIcon(
                    DashIconify(
                        icon=icons.burger_menu,
                        width=20,
                    ),
                    variant="subtle",
                    color="teal",
                    size=24,
                )
            ),
            dmc.MenuDropdown(menu_dd_children),
        ],
        **kwargs
    )
