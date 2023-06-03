import dash_quill
from dash import (
    Dash,
    Output,
    Input,
    State,
    html,
    dcc,
    callback,
    MATCH,
    ctx,
    no_update,
    clientside_callback,
    ClientsideFunction,
)
import bleach
from dash_iconify import DashIconify
import datetime
import uuid
import dash_mantine_components as dmc
import dash_bootstrap_components as dbc
from markdownify import markdownify
from dash.exceptions import PreventUpdate
import base64

# TODO: Move html to md converting to utils

DEFAULT_OK_TAGS = [
    "h1",
    "h2",
    "a",
    "img",
    "strong",
    "b",
    "em",
    "i",
    "",
    "ul",
    "li",
    "p",
    "br",
    "ol",
    "blockquote",
    "code",
    "u",
]
DEFAULT_OK_ATTRIBUTES = {"a": ["href", "rel", "target"], "img": ["src", "alt", "title"]}

DEFAULT_TOOLBAR_MODS = [
    [{"header": "1"}, {"header": "2"}, "bold", "italic"],
    [
        {"list": "ordered"},
        {"list": "bullet"},
    ],
    ["link"],
]


def to_base64(content):
    return base64.b64encode(content.encode()).decode()


def from_base64(encoded_content):
    return base64.b64decode(encoded_content.encode()).decode()


def to_markdown(html_content):
    clean_value = bleach.clean(
        html_content, tags=DEFAULT_OK_TAGS, attributes=DEFAULT_OK_ATTRIBUTES
    )
    return markdownify(clean_value, heading_style="ATX")


class TextEditorAIO(html.Div):
    class ids:
        store = lambda aio_id: {
            "component": "TextEditorAIO",
            "subcomponent": "store",
            "aio_id": aio_id,
        }
        annot_md_store = lambda aio_id: {
            "component": "TextEditorAIO",
            "subcomponent": "annot_md_store",
            "aio_id": aio_id,
        }
        annot_published_store = lambda aio_id: {
            "component": "TextEditorAIO",
            "subcomponent": "annot_published_store",
            "aio_id": aio_id,
        }
        editor_input = lambda aio_id: {
            "component": "TextEditorAIO",
            "subcomponent": "editor_input",
            "aio_id": aio_id,
        }
        title_input = lambda aio_id: {
            "component": "TextEditorAIO",
            "subcomponent": "title_input",
            "aio_id": aio_id,
        }
        minimize = lambda aio_id: {
            "component": "TextEditorAIO",
            "subcomponent": "minimize",
            "aio_id": aio_id,
        }
        preview_text = lambda aio_id: {
            "component": "TextEditorAIO",
            "subcomponent": "preview_text",
            "aio_id": aio_id,
        }
        preview_title = lambda aio_id: {
            "component": "TextEditorAIO",
            "subcomponent": "preview_title",
            "aio_id": aio_id,
        }
        preview_time = lambda aio_id: {
            "component": "TextEditorAIO",
            "subcomponent": "preview_time",
            "aio_id": aio_id,
        }
        preview_header = lambda aio_id: {
            "component": "TextEditorAIO",
            "subcomponent": "preview_header",
            "aio_id": aio_id,
        }
        annotation_toast = lambda aio_id: {
            "component": "TextEditorAIO",
            "subcomponent": "annotation_toast",
            "aio_id": aio_id,
        }
        open_annot_window_actionicon = lambda aio_id: {
            "component": "TextEditorAIO",
            "subcomponent": "open_annot_window_actionicon",
            "aio_id": aio_id,
        }
        publish_btn = lambda aio_id: {
            "component": "TextEditorAIO",
            "subcomponent": "publish_btn",
            "aio_id": aio_id,
        }

    ids = ids

    def __init__(
        self,
        allowed_tags=DEFAULT_OK_TAGS,
        allowed_attributes=DEFAULT_OK_ATTRIBUTES,
        toolbar_mods=DEFAULT_TOOLBAR_MODS,
        store_props=dict(storage_type="local"),
        aio_id=None,
    ):
        self.aio_id = aio_id if aio_id is not None else str(uuid.uuid4())
        self.store_props = store_props.copy() if store_props else {}

        default_html = """<p>describe what you have found...</p><br><br><br>"""
        tabs = dmc.Tabs(
            [
                dmc.Space(h=12),
                dmc.Group(
                    [
                        dmc.TabsList(
                            [
                                dmc.Tab("Text Editor", value="edit_annot"),
                                dmc.Tab("Preview", value="preview_annot"),
                                dmc.ActionIcon(
                                    DashIconify(
                                        icon="tabler:window-minimize", height="1.2rem"
                                    ),
                                    id=self.ids.minimize(self.aio_id),
                                    ml="auto",
                                ),
                            ],
                            grow=False,
                        ),
                    ],
                    grow=True,
                ),
                dmc.TabsPanel(
                    [
                        dmc.Space(h=12),
                        dmc.TextInput(
                            placeholder="My discovery",
                            id=self.ids.title_input(self.aio_id),
                            label="Title"
                            # debounce=100
                        ),
                        dmc.Space(h=4),
                        dash_quill.Quill(
                            id=self.ids.editor_input(self.aio_id),
                            value=default_html,
                            maxLength=10000,
                            modules={
                                "toolbar": toolbar_mods,
                                "clipboard": {
                                    "matchVisual": True,
                                },
                            },
                        ),
                        dmc.Space(h=12),
                        dmc.Group(
                            dmc.Button(
                                "Publish",
                                leftIcon=DashIconify(
                                    icon="material-symbols:send-outline"
                                ),
                                color="green",
                                disabled=True,
                                id=self.ids.publish_btn(self.aio_id),
                            ),
                            position="right",
                        ),
                    ],
                    value="edit_annot",
                ),
                dmc.TabsPanel(
                    [
                        dmc.Space(h=12),
                        dmc.Container(
                            [
                                dmc.Card(
                                    dmc.Stack(
                                        [
                                            dmc.Group(
                                                position="apart",
                                                id=self.ids.preview_header(self.aio_id),
                                            ),
                                            dmc.Divider(),
                                            html.Div(
                                                id=self.ids.preview_text(self.aio_id),
                                                style={
                                                    "overflowY": "auto",
                                                    "maxHeight": "35vh",
                                                },
                                            ),
                                        ],
                                        spacing="xs",
                                    ),
                                    withBorder=True,
                                    pt=12,
                                ),
                            ],
                            fluid=True,
                            p=0,
                        ),
                    ],
                    value="preview_annot",
                ),
                dmc.Space(h=12),
            ],
            color="blue",
            orientation="horizontal",
            value="edit_annot",
        )
        super().__init__(
            [
                dcc.Store(
                    data=None,
                    id=self.ids.store(self.aio_id),
                    **self.store_props,
                ),
                dcc.Store(
                    data=None,
                    id=self.ids.annot_md_store(self.aio_id),
                    **self.store_props,
                ),
                dcc.Store(
                    data=None,
                    id=self.ids.annot_published_store(self.aio_id),
                ),
                dbc.Toast(
                    id=self.ids.annotation_toast(self.aio_id),
                    style={
                        "width": "40vw",
                        "minWidth": "400px",
                        "resize": "both",
                        "overflow": "auto",
                        "height": "60vh",
                        # "background": "white",
                        # "backgroundOpacity": 1,
                        "zIndex": 1050,
                        "position": "fixed",
                        "bottom": "10px",
                        "right": "90px",
                    },
                    header=dmc.Group(
                        [
                            DashIconify(icon="mdi:drag", width=21, inline=True),
                            dmc.Text("Edit annotation"),
                        ],
                        spacing="sm",
                    ),
                    header_style={"cursor": "move"},
                    children=[dmc.Group([], spacing="sm", position="right"), tabs],
                    body_class_name="py-0",
                    class_name="annotation_editor",
                    is_open=False,
                ),
            ],
        )

    # validate title
    @callback(
        Output(ids.title_input(MATCH), "error"),
        Input(ids.title_input(MATCH), "value"),
    )
    def update_title_error(value):
        if value is not None:
            if len(value) > 0:
                return None
        return "Enter a Title"

    # enable publish_btn
    @callback(
        Output(ids.publish_btn(MATCH), "disabled"),
        Input(ids.title_input(MATCH), "value"),
    )
    def update_publish_btn(title):
        if title is not None and len(title) > 0:
            return False
        return True

    # update store
    @callback(
        Output(ids.store(MATCH), "data"),
        Input(ids.editor_input(MATCH), "value"),
        Input(ids.title_input(MATCH), "value"),
    )
    def update_store(value, title):
        if value is not None:
            md = to_markdown(value)
            b64_val = to_base64(value)
            time_now = datetime.datetime.utcnow()
            return {
                "content": b64_val,
                "timestamp": time_now,
                "title": title,
                "md_content": md,
            }

        raise PreventUpdate

    # open and close editor
    @callback(
        Output(ids.annotation_toast(MATCH), "is_open"),
        Input(ids.open_annot_window_actionicon(MATCH), "n_clicks"),
        Input(ids.minimize(MATCH), "n_clicks"),
        Input(ids.publish_btn(MATCH), "n_clicks"),
        State(ids.annotation_toast(MATCH), "is_open"),
        prevent_initial_call=True,
    )
    def open_toast(nc, nc_min, nc_publish, is_open):
        if nc is None and nc_min is None and nc_publish is None:
            return no_update
        return not is_open

    # update preview
    @callback(
        Output(ids.preview_text(MATCH), "children"),
        Output(ids.preview_header(MATCH), "children"),
        Output(ids.annot_md_store(MATCH), "data"),
        Input(ids.store(MATCH), "data"),
    )
    def update_preview(data):
        if data is not None:
            valueb64 = data.get("content")
            if valueb64 is not None:
                value = from_base64(valueb64)

                clean_value = bleach.clean(
                    value, tags=DEFAULT_OK_TAGS, attributes=DEFAULT_OK_ATTRIBUTES
                )
                h = markdownify(clean_value, heading_style="ATX")
                mod_time = data.get("time")
                time_str = None
                if mod_time is not None:
                    time_str = (
                        datetime.datetime.fromisoformat(mod_time).strftime(
                            "%d.%m.%Y %H:%M"
                        )
                        + " UTC"
                    )
                title = data.get("title")
                header = [
                    dmc.Text(title, size="lg", weight=700),
                    dmc.Text(time_str, size="sm"),
                ]

                return (dcc.Markdown(h, link_target="_blank"), header, h)
        raise PreventUpdate

    # clear store on publish
    @callback(
        Output(ids.title_input(MATCH), "value"),
        Output(ids.editor_input(MATCH), "value"),
        Output(ids.annot_published_store(MATCH), "data", allow_duplicate=True),
        Input(ids.annot_published_store(MATCH), "modified_timestamp"),
        State(ids.annot_published_store(MATCH), "data"),
        prevent_initial_call=True,
    )
    def clear_input_fields(ts, data):
        if data is not None:
            print(data)
            return "", "", None
        raise PreventUpdate

    clientside_callback(
        ClientsideFunction(
            namespace="clientside", function_name="make_toast_draggable"
        ),
        Output(
            ids.annotation_toast(MATCH), "className"
        ),  # the attribute here will not be updated, it is just used as a dummy
        [Input(ids.annotation_toast(MATCH), "is_open")],
        [State(ids.annotation_toast(MATCH), "id")],
    )
