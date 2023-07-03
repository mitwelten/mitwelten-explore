import dash
from dash import html, dcc, callback, Input, Output, State
from dash.exceptions import PreventUpdate
import dash_mantine_components as dmc
from dashboard.api_clients.deployments_client import get_deployment_info
from dashboard.utils.communication import parse_nested_qargs, qargs_to_dict
from dashboard.components.cards import deployment_info_card

dash.register_page(__name__, path_template="/reference/deployment")


def layout(**qargs):
    qargs_dict = parse_nested_qargs(qargs)
    ids = qargs_dict.get("ids")
    if ids is None:
        return dmc.Container(dmc.Alert(title="ID not found."))
    elif isinstance(ids, int):
        ids = [ids]
    if not isinstance(ids, list):
        return dmc.Container(dmc.Alert(title="ID not found."))
    show_map = len(ids) <= 10
    return dmc.Container(
        dmc.Grid(
            [
                dmc.Col(
                    deployment_info_card(
                        get_deployment_info(ids[i]), show_map=show_map
                    ),
                    span=4,
                )
                for i in range(len(ids))
            ],
        ),
        className="container-xl",
    )
