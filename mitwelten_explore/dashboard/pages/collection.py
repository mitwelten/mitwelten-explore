import dash
from dash import html, dcc, callback, Input, Output, no_update, State, ALL, ctx
import flask
from dash.exceptions import PreventUpdate
import dash_mantine_components as dmc
import json
from dashboard.aio_components.aio_list_component import PagedListAIO, PagedListSearchableAIO
from dashboard.components.lists import generate_selected_data_list
from dashboard.components.notifications import generate_notification


dash.register_page(
    __name__,
)

plaio = PagedListSearchableAIO(items=[])


def layout(**qargs):
    return dmc.Container(
        [
            dmc.Text("Collected Datasets", weight=600, size="lg"),
            dmc.Space(h=8),
            plaio,
        ],
        fluid=True,
    )


@callback(Output(plaio.ids.store(plaio.aio_id), "data"), Input("traces_store", "data"))
def update_sel_tr(data):
    if data is not None:
        return generate_selected_data_list(data)
    raise PreventUpdate


@callback(
    Output("traces_store", "data", allow_duplicate=True),
    Output("noti_container", "children", allow_duplicate=True),
    Input({"role": "remove_from_collection_btn", "index": ALL}, "n_clicks"),
    State("traces_store", "data"),
    prevent_initial_call=True,
)
def remove_trace(buttons, data):
    if not any(buttons):
        raise PreventUpdate
    trg = ctx.triggered_id
    index_to_remove = trg.get("index")
    if index_to_remove is not None:
        del data[index_to_remove]
    
    return data, generate_notification(
        title="Item removed from collection",
        message="the dataset was removed from your collection",
        color="indigo",
        icon="mdi:trash-can-outline"
    )
