import dash_mantine_components as dmc
from dashboard.styles import icons, get_icon
import uuid


def affix_br(children, horizontal=False):
    return dmc.Affix(
        dmc.Group(children=children) if horizontal else dmc.Stack(children=children),
        position={"bottom": 20, "right": 20},
    )


def affix_button(id, icon):
    return dmc.ActionIcon(
        get_icon(icon=icon, height=30),
        variant="filled",
        radius="xl",
        size="xl",
        color="teal",
        id=id,
    )

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
