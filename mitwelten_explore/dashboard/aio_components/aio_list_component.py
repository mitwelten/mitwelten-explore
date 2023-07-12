from dash import Dash, Output, Input, State, html, dcc, callback, MATCH, ctx, no_update
import uuid
from dash.exceptions import PreventUpdate
import dash_mantine_components as dmc
import math
from dash_iconify import DashIconify

ITEMS_PER_PAGE = 50
STACK_SPACING = 3
MIN_CHARS = 1


def get_children_fields(d):
    if isinstance(d, list):
        for di in d:
            yield from get_children_fields(di)

    elif isinstance(d, dict):
        for k in d.keys():
            if k == "props":
                yield from get_children_fields(d[k])
            elif k == "children":
                if isinstance(d[k], str):

                    yield d[k]
                else:
                    yield from get_children_fields(d[k])
    elif isinstance(d, str):
        yield d


def is_in_text(text: str, keyword: str):
    if keyword.lower() in text.lower():
        return True
    return False


def is_keyword_in_component(comp, keyword):
    for text in get_children_fields(comp):
        if is_in_text(text, keyword):
            return True
            break
    return False


def filter_data(data, keyword):
    return list(filter(lambda d: is_keyword_in_component(d, keyword), data))


class PagedListSearchableAIO(html.Div):
    class ids:
        store = lambda aio_id: {
            "component": "PagedListSearchableAIO",
            "subcomponent": "store",
            "aio_id": aio_id,
        }
        config_store = lambda aio_id: {
            "component": "PagedListSearchableAIO",
            "subcomponent": "config_store",
            "aio_id": aio_id,
        }
        pager = lambda aio_id: {
            "component": "PagedListSearchableAIO",
            "subcomponent": "pager",
            "aio_id": aio_id,
        }
        scroll_area = lambda aio_id: {
            "component": "PagedListSearchableAIO",
            "subcomponent": "scroll_area",
            "aio_id": aio_id,
        }
        search_input = lambda aio_id: {
            "component": "PagedListSearchableAIO",
            "subcomponent": "search_input",
            "aio_id": aio_id,
        }
        search_input_store = lambda aio_id: {
            "component": "PagedListSearchableAIO",
            "subcomponent": "search_input_store",
            "aio_id": aio_id,
        }
        clear_input_btn = lambda aio_id: {
            "component": "PagedListSearchableAIO",
            "subcomponent": "clear_input_btn",
            "aio_id": aio_id,
        }

    ids = ids

    def __init__(
        self,
        items=["Hello", "Dash"],
        scrollable=True,
        items_per_page=20,
        legend=None,
        store_props=None,  # dict(storage_type="local"),
        pager_props=None,
        aio_id=None,
        height="90vh",
        use_loadingoverlay=True,
    ):
        self.aio_id = aio_id if aio_id is not None else str(uuid.uuid4())
        self.store_props = store_props.copy() if store_props else {}
        self.pager_props = pager_props.copy() if pager_props else {}
        n_pages = math.ceil(len(items) / items_per_page)
        scrollarea = dmc.ScrollArea(
            className="flex-grow-1",
            id=self.ids.scroll_area(self.aio_id),
            children=dmc.Stack(items[:items_per_page], spacing=STACK_SPACING),
        )
        if use_loadingoverlay:
            scrollarea = dmc.ScrollArea(
                className="flex-grow-1",
                children=dmc.LoadingOverlay(
                    id=self.ids.scroll_area(self.aio_id),
                    children=dmc.Stack(items[:items_per_page], spacing=STACK_SPACING),
                ),
            )

        super().__init__(
            [  # Equivalent to `html.Div([...])`
                dcc.Store(
                    data=items,
                    id=self.ids.store(self.aio_id),
                    **self.store_props,
                ),
                dcc.Store(
                    data=items_per_page,
                    id=self.ids.config_store(self.aio_id),
                ),
                dcc.Store(
                    data=None,
                    id=self.ids.search_input_store(self.aio_id),
                ),
                dmc.Container(
                    dmc.Stack(
                        [
                            dmc.TextInput(
                                # label="Search in Results",
                                id=self.ids.search_input(self.aio_id),
                                icon=DashIconify(icon="ic:sharp-search"),
                                rightSection=dmc.ActionIcon(
                                    DashIconify(icon="ic:outline-clear"),
                                    variant="transparent",
                                    id=self.ids.clear_input_btn(self.aio_id),
                                ),
                            ),
                            legend,
                            scrollarea,
                            dmc.Pagination(
                                total=n_pages,
                                siblings=1,
                                page=1,
                                id=self.ids.pager(self.aio_id),
                                grow=False,
                                position="center",
                            ),
                        ],
                        style=dict(height=height),
                        className="d-flex w-100",
                    ),
                    fluid=True,
                    px=0,
                ),
            ]
        )

    @callback(
        Output(ids.pager(MATCH), "page"),
        Output(ids.pager(MATCH), "total"),
        Output(ids.scroll_area(MATCH), "children"),
        Output(ids.search_input(MATCH), "value"),
        Input(ids.pager(MATCH), "page"),
        Input(ids.store(MATCH), "modified_timestamp"),
        Input(ids.search_input(MATCH), "value"),
        Input(ids.clear_input_btn(MATCH), "n_clicks"),
        State(ids.store(MATCH), "data"),
        State(ids.config_store(MATCH), "data"),
        Input(ids.search_input_store(MATCH), "data"),
    )
    def update_pager_on_new_data(
        page, ts, query, clear_btn, data, items_per_page, search_input_store
    ):
        trg = ctx.triggered_id
        if trg is not None:
            items_per_page = items_per_page if items_per_page else 20
            trg = trg.subcomponent
            if trg == "store":
                search_input = ""
                if search_input_store is not None:
                    search_input = search_input_store
                    data = filter_data(data, search_input_store)

                n_pages = math.ceil(len(data) / items_per_page)
                data = data[:items_per_page]
                return 1, n_pages, dmc.Stack(data, spacing=STACK_SPACING), search_input
            elif trg == "pager":
                if query is not None:
                    if len(query) >= MIN_CHARS:
                        data = filter_data(data, query)
                return (
                    no_update,
                    no_update,
                    dmc.Stack(
                        data[(page - 1) * items_per_page : page * items_per_page],
                        spacing=STACK_SPACING,
                    ),
                    no_update,
                )
            elif trg == "search_input":
                if query is not None:
                    if len(query) >= MIN_CHARS:

                        data = filter_data(data, query)
                        # print(data[0])
                n_pages = math.ceil(len(data) / items_per_page)
                return (
                    1,
                    n_pages,
                    dmc.Stack(data[:items_per_page], spacing=STACK_SPACING),
                    no_update,
                )
            elif trg == "clear_input_btn":
                n_pages = math.ceil(len(data) / items_per_page)
                return (
                    1,
                    n_pages,
                    dmc.Stack(data[:items_per_page], spacing=STACK_SPACING),
                    "",
                )
            elif trg == "search_input_store":
                if search_input_store is not None:

                    data = filter_data(data, search_input_store)
                n_pages = math.ceil(len(data) / items_per_page)
                return (
                    1,
                    n_pages,
                    dmc.Stack(data[:items_per_page], spacing=STACK_SPACING),
                    no_update,
                )

        raise PreventUpdate


class PagedListAIO(html.Div):
    class ids:
        store = lambda aio_id: {
            "component": "PagedListAIO",
            "subcomponent": "store",
            "aio_id": aio_id,
        }
        config_store = lambda aio_id: {
            "component": "PagedListAIO",
            "subcomponent": "config_store",
            "aio_id": aio_id,
        }
        pager = lambda aio_id: {
            "component": "PagedListAIO",
            "subcomponent": "pager",
            "aio_id": aio_id,
        }
        scroll_area = lambda aio_id: {
            "component": "PagedListAIO",
            "subcomponent": "scroll_area",
            "aio_id": aio_id,
        }

    ids = ids

    def __init__(
        self,
        items=["Hello", "Dash"],
        scrollable=True,
        items_per_page=20,
        legend=None,
        store_props=None,  # dict(storage_type="local"),
        pager_props=None,
        aio_id=None,
        height="90vh",
    ):
        self.aio_id = aio_id if aio_id is not None else str(uuid.uuid4())
        self.store_props = store_props.copy() if store_props else {}
        self.pager_props = pager_props.copy() if pager_props else {}
        n_pages = math.ceil(len(items) / items_per_page)

        super().__init__(
            [  # Equivalent to `html.Div([...])`
                dcc.Store(
                    data=items,
                    id=self.ids.store(self.aio_id),
                    **self.store_props,
                ),
                dcc.Store(
                    data=items_per_page,
                    id=self.ids.config_store(self.aio_id),
                ),
                dmc.Container(
                    dmc.Stack(
                        [
                            legend,
                            dmc.ScrollArea(
                                className="flex-grow-1",
                                # id=self.ids.scroll_area(self.aio_id),
                                # children=dmc.Stack(items[:ITEMS_PER_PAGE]),
                                children=dmc.LoadingOverlay(
                                    id=self.ids.scroll_area(self.aio_id),
                                    children=dmc.Stack(
                                        items[:items_per_page], spacing=STACK_SPACING
                                    ),
                                ),
                            ),
                            dmc.Pagination(
                                total=n_pages,
                                siblings=1,
                                page=1,
                                id=self.ids.pager(self.aio_id),
                                grow=False,
                                position="center",
                            ),
                        ],
                        style=dict(height=height),
                        className="d-flex w-100",
                    ),
                    fluid=True,
                ),
            ]
        )

    @callback(
        Output(ids.pager(MATCH), "page"),
        Output(ids.pager(MATCH), "total"),
        Output(ids.scroll_area(MATCH), "children"),
        Input(ids.pager(MATCH), "page"),
        Input(ids.store(MATCH), "modified_timestamp"),
        State(ids.store(MATCH), "data"),
        State(ids.config_store(MATCH), "data"),
    )
    def update_pager_on_new_data(page, ts, data, items_per_page):
        trg = ctx.triggered_id
        if trg is not None:
            items_per_page = items_per_page if items_per_page else 20
            trg = trg.subcomponent
            if trg == "store":

                n_pages = math.ceil(len(data) / items_per_page)
                data = data[:items_per_page]
                return 1, n_pages, dmc.Stack(data, spacing=STACK_SPACING)
            elif trg == "pager":

                return (
                    no_update,
                    no_update,
                    dmc.Stack(
                        data[(page - 1) * items_per_page : page * items_per_page],
                        spacing=STACK_SPACING,
                    ),
                )

        raise PreventUpdate


class SearchableListAIO(html.Div):
    class ids:
        store = lambda aio_id: {
            "component": "SearchableListAIO",
            "subcomponent": "store",
            "aio_id": aio_id,
        }

        scroll_area = lambda aio_id: {
            "component": "SearchableListAIO",
            "subcomponent": "scroll_area",
            "aio_id": aio_id,
        }
        search_input = lambda aio_id: {
            "component": "SearchableListAIO",
            "subcomponent": "search_input",
            "aio_id": aio_id,
        }
        search_input_store = lambda aio_id: {
            "component": "SearchableListAIO",
            "subcomponent": "search_input_store",
            "aio_id": aio_id,
        }
        clear_input_btn = lambda aio_id: {
            "component": "SearchableListAIO",
            "subcomponent": "clear_input_btn",
            "aio_id": aio_id,
        }

    ids = ids

    def __init__(
        self,
        items=[],
        legend=None,
        store_props=None,  # dict(storage_type="local"),
        aio_id=None,
        height="90vh",
        use_loadingoverlay=True,
    ):
        self.aio_id = aio_id if aio_id is not None else str(uuid.uuid4())
        self.store_props = store_props.copy() if store_props else {}

        if use_loadingoverlay:
            scrollarea = dmc.ScrollArea(
                className="flex-grow-1",
                children=dmc.LoadingOverlay(
                    id=self.ids.scroll_area(self.aio_id),
                    children=dmc.Stack(items, spacing=STACK_SPACING),
                ),
                type="scroll",
            )
        else:
            scrollarea = dmc.ScrollArea(
                className="flex-grow-1",
                id=self.ids.scroll_area(self.aio_id),
                children=dmc.Stack(items, spacing=STACK_SPACING),
                type="scroll",
            )

        super().__init__(
            [
                dcc.Store(
                    data=items,
                    id=self.ids.store(self.aio_id),
                    **self.store_props,
                ),
                dcc.Store(
                    data=None,
                    id=self.ids.search_input_store(self.aio_id),
                ),
                dmc.Container(
                    dmc.Stack(
                        [
                            dmc.TextInput(
                                # label="Search in Results",
                                id=self.ids.search_input(self.aio_id),
                                icon=DashIconify(icon="ic:sharp-search"),
                                rightSection=dmc.ActionIcon(
                                    DashIconify(icon="ic:outline-clear"),
                                    variant="transparent",
                                    id=self.ids.clear_input_btn(self.aio_id),
                                ),
                            ),
                            legend,
                            scrollarea,
                        ],
                        style=dict(height=height),
                        className="d-flex w-100",
                    ),
                    fluid=True,
                    px=0,
                ),
            ]
        )

    @callback(
        # Output(ids.pager(MATCH), "page"),
        # Output(ids.pager(MATCH), "total"),
        Output(ids.scroll_area(MATCH), "children"),
        Output(ids.search_input(MATCH), "value"),
        Input(ids.store(MATCH), "modified_timestamp"),
        Input(ids.search_input(MATCH), "value"),
        Input(ids.clear_input_btn(MATCH), "n_clicks"),
        State(ids.store(MATCH), "data"),
        Input(ids.search_input_store(MATCH), "data"),
    )
    def update_pager_on_new_data(ts, query, clear_btn, data, search_input_store):
        trg = ctx.triggered_id
        if trg is not None:
            trg = trg.subcomponent
            if trg == "store":
                search_input = ""
                if search_input_store is not None:
                    search_input = search_input_store
                    data = filter_data(data, search_input_store)

                return dmc.Stack(data, spacing=STACK_SPACING), search_input
            elif trg == "search_input":
                if query is not None:
                    if len(query) >= MIN_CHARS:

                        data = filter_data(data, query)
                return dmc.Stack(data, spacing=STACK_SPACING), no_update

            elif trg == "clear_input_btn":
                return dmc.Stack(data, spacing=STACK_SPACING), ""

            elif trg == "search_input_store":
                if search_input_store is not None:

                    data = filter_data(data, search_input_store)
                return dmc.Stack(data, spacing=STACK_SPACING), no_update

        raise PreventUpdate
