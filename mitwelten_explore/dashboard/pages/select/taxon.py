import dash
from dash import callback, Input, Output, State, no_update, ctx, ALL, html
from dash.exceptions import PreventUpdate
import dash_mantine_components as dmc
from dashboard.aio_components.aio_list_component import PagedListSearchableAIO
from dashboard.models import RankEnum
from dashboard.api_clients.taxonomy_client import (
    get_taxon_by_level,
    get_parent_taxonomy,
    get_taxon_dataset,
    get_gbif_taxon_dataset,
)
from dashboard.components.dataset_presentation import taxon_list_card
from dashboard.components.modals import taxon_select_modal
from dashboard.styles import icons, get_icon
from configuration import PATH_PREFIX
import uuid
import json

plaio = PagedListSearchableAIO(
    # aio_id="plaio_species_select",
    height="85vh",
    items=[],
    items_per_page=25,
)


class PageIds(object):
    level_select_rg = str(uuid.uuid4())
    list_role = str(uuid.uuid4())
    species_modal = str(uuid.uuid4())
    modal_div = str(uuid.uuid4())
    add_dataset_role = str(uuid.uuid4())
    add_gbif_dataset_role = str(uuid.uuid4())


ids = PageIds()

dash.register_page(__name__, path="/select/taxon")


level_select_radiogroup = dmc.RadioGroup(
    [
        dmc.Radio(dmc.Text(str(l).title(), weight=500), value=l, color="teal")
        for l in reversed([e.value for e in RankEnum])
    ],
    id=ids.level_select_rg,
    value=RankEnum.species,
    # label="Select a level",
    size="sm",
    offset=4
)

title_group = dmc.Group(
    [
        dmc.Stack(
            [
                dmc.Group(
                    [
                        dmc.Text("Taxon Detections", weight=700, size="lg"),
                        dmc.Anchor(
                            get_icon(icons.help, width=18),
                            href=f"{PATH_PREFIX}docs#datasets",
                            variant="text",
                            target="_blank",
                        ),
                    ],
                    align="top",
                ),
                dmc.Text("Detections of Birds and Insects"),
            ],
            spacing=0,
        ),
        dmc.Stack(
            [
                dmc.Text("Select a level", size="sm", weight=500),
                level_select_radiogroup,
            ],
            spacing=0,
        ),
    ],
    spacing="5rem",
)


def layout(**qargs):
    return dmc.Container(
        [
            html.Div(id=ids.modal_div),
            title_group,
            dmc.Space(h=12),
            plaio,
        ],
        fluid=True,
    )


@callback(
    Output(plaio.ids.store(plaio.aio_id), "data"), Input(ids.level_select_rg, "value")
)
def taxon_level_callback(level):
    if level is not None:
        try:
            level = RankEnum(level)
        except:
            raise PreventUpdate
        taxons = get_taxon_by_level(level)
        return [taxon_list_card(t, ids.list_role) for t in taxons]
    return no_update


@callback(
    Output(ids.modal_div, "children"),
    Input({"role": ids.list_role, "index": ALL}, "n_clicks"),
    prevent_initial_call=True,
)
def update_modal(buttons):
    if not any(buttons):
        raise PreventUpdate
    trg = ctx.triggered_id
    datum_id = trg.get("index")
    return taxon_select_modal(datum_id, ids.add_dataset_role, ids.add_gbif_dataset_role)


@callback(
    Output("trace_add_store", "data", allow_duplicate=True),
    Input({"role": ids.add_dataset_role, "index": ALL}, "n_clicks"),
    State("trace_add_store", "data"),
    prevent_initial_call=True,
)
def update_modal(buttons, collection):
    if not any(buttons):
        raise PreventUpdate
    if collection is None:
        collection = []
    trg = ctx.triggered_id
    taxon_key = trg.get("index")
    try:
        dataset = get_taxon_dataset(taxon_key)
        if dataset is None:
            raise PreventUpdate

        if not dataset in collection:
            collection.append(dataset)
            return collection  # , generate_notification(title="Added to collection",message="the selected dataset was added to your collection",color="green",icon="material-symbols:check-circle-outline")
        raise PreventUpdate
    except:
        print("failed to load!")
        return no_update  # , generate_notification(title="Already in collection",message="the selected dataset is already stored in your collection",color="orange",icon="mdi:information-outline")


@callback(
    Output("trace_add_store", "data", allow_duplicate=True),
    Input({"role": ids.add_gbif_dataset_role, "index": ALL}, "n_clicks"),
    State("trace_add_store", "data"),
    prevent_initial_call=True,
)
def add_gbif_trace(buttons, collection):
    if not any(buttons):
        raise PreventUpdate
    if collection is None:
        collection = []
    trg = ctx.triggered_id
    taxon_key = trg.get("index")
    try:
        dataset = get_gbif_taxon_dataset(taxon_key)
        if dataset is None:
            raise PreventUpdate

        if not dataset in collection:
            collection.append(dataset)
            return collection  # , generate_notification(title="Added to collection",message="the selected dataset was added to your collection",color="green",icon="material-symbols:check-circle-outline")
        raise PreventUpdate
    except:
        print("failed to load!")
        return no_update  # , generate_notification(title="Already in collection",message="the selected dataset is already stored in your collection",color="orange",icon="mdi:information-outline")
