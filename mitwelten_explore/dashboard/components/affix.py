import dash_mantine_components as dmc
from dashboard.styles import icons, get_icon
import uuid


def datasource_affix(id):
    return dmc.Affix(
        dmc.Loader(color="gray", size="xs", variant="dots"),
        id=id,
        position={"bottom": 1, "left": 20},
    )


def affix_button(id, icon, tooltip_text = None):
    actionicon =  dmc.ActionIcon(
        get_icon(icon=icon, height=30),
        variant="filled",
        radius="xl",
        size="xl",
        color="teal",
        id=id,
    )
    if tooltip_text is None:
        return actionicon
    else:
        return dmc.Tooltip(children=actionicon, label=tooltip_text,position="left",color="teal")


def affix_menu(menu_children, id=str(uuid.uuid4())):
    return dmc.Affix(
        dmc.Menu(
            [
                dmc.MenuTarget(affix_button(id, icons.more_3_dots)),
                dmc.MenuDropdown(
                    dmc.Stack(children=menu_children, spacing="md", pb=8),
                    m=0,
                    p=0,
                    className="bg-transparent border-0",
                ),
            ],
            closeOnClickOutside=False,
        ),
        position={"bottom": 20, "right": 20},
    )
