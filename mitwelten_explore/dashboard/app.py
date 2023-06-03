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
from dashboard.utils.communication import get_user_from_cookies
from dashboard.api_clients.userdata_client import update_collection, get_collection

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


# sync traces store
@app.callback(
    Output("traces_store", "data", allow_duplicate=True),
    Input("traces_store", "modified_timestamp"),
    State("traces_store", "data"),
    prevent_initial_call=True,
)
def sync_collection(ts, data):
    if data is None:

        collection = get_collection(auth_cookie=flask.request.cookies.get("auth"))
        return collection
    if data is not None:
        update_collection(datasets=data, auth_cookie=flask.request.cookies.get("auth"))
    raise PreventUpdate


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
