from dash import dcc, no_update
from dash.exceptions import PreventUpdate
import dash_mantine_components as dmc
from dashboard.components.modals import share_modal
from dashboard.utils.communication import get_user_from_cookies
from dashboard.models import Annotation
from dashboard.api_clients.userdata_client import post_annotation
from dashboard.styles import icons, get_icon
from configuration import PATH_PREFIX


def share_modal_callback(nc, search, href):
    if nc is not None:
        base_path = href.split("?")[0]
        path_to_share = base_path + search
        return share_modal(path_to_share)
    raise PreventUpdate


def publish_annotation_callback(cookies, nc, search, pathname, data):
    if nc is not None:

        user = get_user_from_cookies(cookies)

        annot = Annotation(
            user=user, url=pathname.split(PATH_PREFIX)[1] + search, **data
        )
        title_row = dmc.Group(
            [
                dmc.Text(annot.title, weight=600, size="xl"),
                dmc.Group(
                    [
                        dmc.Text(annot.time_str, weight=300),
                        dmc.Text(f"by {user.username}"),
                    ]
                ),
            ],
            position="apart",
        )
        if post_annotation(annotation=annot, auth_cookie=cookies.get("auth")):

            return (
                dmc.Modal(
                    children=dmc.Card(
                        [
                            title_row,
                            dmc.Space(h=12),
                            dmc.Divider(pb=12),
                            dcc.Markdown(data.get("md_content")),
                        ],
                        withBorder=False,
                    ),
                    opened=True,
                    title=dmc.Group(
                        [
                            dmc.Text("Annotation published!", weight=500),
                            get_icon(
                                icons.success_round, width="1.5rem", color="green"
                            ),
                        ],
                        spacing="xs",
                    ),
                    size="60%",
                    zIndex=1000,
                ),
                1,
            )
        else:
            return (
                dmc.Modal(
                    children=dmc.Alert(
                        children="Something went wrong. Try again.", color="red"
                    ),
                    opened=True,
                    title="Annotation not published",
                    size="60%",
                    zIndex=1000,
                ),
                no_update,
            )

    raise PreventUpdate
