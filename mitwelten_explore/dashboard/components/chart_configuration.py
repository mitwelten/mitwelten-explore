import dash_mantine_components as dmc
from dashboard.styles import icons, get_icon
from dashboard.components.overlays import tooltip

TS_CHART_TYPES = [
    ["line", dmc.Group([get_icon(icon=icons.line_chart, width=20), "Line"])],
    [
        "scatter",
        dmc.Group([get_icon(icon=icons.scatter_chart, width=20), "Scatter"]),
    ],
    ["bar", dmc.Group([get_icon(icon=icons.bar_chart, width=20), "Bar"])],
    ["area", dmc.Group([get_icon(icon=icons.area_chart, width=20), "Area"])],
]

TS_CHART_LAYOUTS = [
    ["single", dmc.Group([get_icon(icon=icons.layout_rect, width=20), "Overlay"])],
    ["subplots", dmc.Group([get_icon(icon=icons.layout_row, width=20), "Subplots"])],
]


def reload_control(reload_on_zoom_id):
    return tooltip(
        dmc.Switch(
            onLabel=get_icon(icon=icons.sync_on, width=16),
            offLabel=get_icon(icon=icons.sync_off, width=16),
            color="teal.6",
            checked=True,
            id=reload_on_zoom_id,
            persistence=True,
        ),
        "Update time range on zoom-in",
        color="teal.6",
        position="left-start",
    )


def timeseries_chart_config_menu(
    chart_type_id=None,
    reload_on_zoom_id=None,
    layout_type_id=None,
    default_chart_type_index: int = None,
    **kwargs
):
    menu_dd_children = []
    if chart_type_id:
        type_radiogroup = dmc.RadioGroup(
            [dmc.Radio(l, value=k) for k, l in TS_CHART_TYPES],
            id=chart_type_id,
            persistence=True,
            value=TS_CHART_TYPES[0][0]
            if default_chart_type_index is None
            else TS_CHART_TYPES[default_chart_type_index][0],
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
            onLabel=get_icon(icon=icons.sync_on, width=16),
            offLabel=get_icon(icon=icons.sync_off, width=16),
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

    return tooltip(
        dmc.Menu(
            [
                dmc.MenuTarget(
                    dmc.ActionIcon(
                        get_icon(
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
        ),
        "Chart Configuration",
        color="teal.6",
        position="bottom-end",
    )
