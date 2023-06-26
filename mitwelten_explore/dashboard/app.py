from dash import (
    Dash,
    dcc,
    html,
    no_update,
    ctx,
    Input,
    Output,
    State,
    ALL,
    MATCH,
    page_container,
)
from dash.exceptions import PreventUpdate
import dash_mantine_components as dmc
import flask
from configuration import *
from dashboard.components.navbar import nav_bar, ThemeSwitchAIO
from dashboard.components.modals import confirm_dialog
from dashboard.components.notifications import generate_notification
from dashboard.utils.communication import get_user_from_cookies
from dashboard.api_clients.userdata_client import update_collection, get_collection
from dashboard.models import to_typed_dataset

app = Dash(
    __name__,
    use_pages=True,
    suppress_callback_exceptions=True,
    requests_pathname_prefix=PATH_PREFIX,
    external_stylesheets=[HLJS_STYLESHEET],
)

notification_provider = dmc.NotificationsProvider(
    html.Div(id="noti_container"),
)

app.layout = dmc.MantineProvider(
    theme={"colorScheme": "light"},
    id="mt-provider",
    children=[
        dmc.Container(
            [
                dcc.Interval(id="keepalive_interval", interval=30 * 1000),
                dcc.Store(id="traces_store", data=None, storage_type="memory"),
                dcc.Store(id="trace_add_store", data=None, storage_type="memory"),
                html.Div(id="keepalive_div"),
                dcc.Location("url", refresh=True),
                nav_bar,
                notification_provider,
                dmc.Container([page_container], fluid=True, className="pt-2"),
            ],
            fluid=True,
            className="p-0",
        )
    ],
)

# sync traces store
@app.callback(
    Output("traces_store", "data", allow_duplicate=True),
    Output("trace_add_store", "data", allow_duplicate=True),
    Output("noti_container", "children", allow_duplicate=True),
    Input("traces_store", "modified_timestamp"),
    State("traces_store", "data"),
    Input("trace_add_store", "modified_timestamp"),
    Input("trace_add_store", "data"),
    prevent_initial_call=True,
)
def sync_collection(ts, data, data_add_ts, data_add):
    trg = ctx.triggered_id
    if trg == "traces_store":

        if data is None:

            collection = get_collection(auth_cookie=flask.request.cookies.get("auth"))
            return collection, no_update, no_update
        if data is not None:
            update_collection(
                datasets=data, auth_cookie=flask.request.cookies.get("auth")
            )
            raise PreventUpdate
    elif trg == "trace_add_store" and data_add is not None:
        if data is None:
            raise PreventUpdate
        if isinstance(data_add, list) and len(data_add) > 0:
            data_add = data_add[0]
        ds = to_typed_dataset(data_add)
        if data_add in data:
            return (
                no_update,
                None,
                generate_notification(
                    title=f"{ds.get_title()} is already in your collection",
                    message="the selected dataset is already stored in your collection",
                    color="orange",
                    icon="mdi:information-outline",
                ),
            )
        else:

            data.append(data_add)
            update_collection(
                datasets=data, auth_cookie=flask.request.cookies.get("auth")
            )
            return (
                data,
                None,
                generate_notification(
                    title=f"{ds.get_title()} added to collection",
                    message="the selected dataset was added to your collection",
                    color="green",
                    icon="material-symbols:check-circle-outline",
                ),
            )

    raise PreventUpdate


@app.callback(
    Output("username_nav", "children"),
    Output("fullname_nav", "children"),
    Output("avatar_nav", "children"),
    Input("url", "href"),
    prevent_initial_call=True,
)
def update_hello_message(href):
    cookies = flask.request.cookies
    user = get_user_from_cookies(cookies)
    if user.username:
        return user.username, user.full_name, user.initials
    raise PreventUpdate


@app.callback(
    Output("mt-provider", "theme"), Input(ThemeSwitchAIO.ids.switch("theme"), "value")
)
def update_mt_theme(value):
    if value is None:
        return no_update
    if value:
        return {"colorScheme": "light"}
    else:
        return {"colorScheme": "dark"}


@app.callback(
    Output("sidebar_selected_trace_number", "children"),
    Input("traces_store", "data"),
    prevent_initial_call=True,
)
def update_sidebar(data):
    if data is None:
        return "0"
    n_traces = len(data)

    return str(n_traces)


@app.callback(
    Output("keepalive_div", "children"),
    Input("keepalive_interval", "n_intervals"),
    Input("clear_collection_button", "n_clicks"),
    prevent_initial_call=True,
)
def clear_collection_modal(ni, nc):
    if ctx.triggered_id == "clear_collection_button":
        if nc is not None:
            return confirm_dialog(
                id="delete_collection_modal",
                submit_id="confirm_delete_collection_btn",
                text="This will delete all datasets from your collection",
                title="You are about to clear your collection",
            )
    return no_update


@app.callback(
    Output("traces_store", "data", allow_duplicate=True),
    Output("delete_collection_modal", "opened"),
    Input("confirm_delete_collection_btn", "n_clicks"),
    prevent_initial_call=True,
)
def clear_collection(nc):
    print(nc, type(nc))
    if nc > 0:
        return [], False
    raise PreventUpdate
