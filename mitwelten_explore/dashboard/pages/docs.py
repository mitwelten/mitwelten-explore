import dash
import dash_mantine_components as dmc
from dash import dcc, callback, Input, Output, no_update, State
from configuration import PATH_PREFIX

dash.register_page(__name__, path="/docs")

def get_doc_page(section):
    try:
        with open(f"dashboard/docs/{section}.md", "r") as f:
            content = f.read()
    except:
        content = "### This Page does not exist."
    return content


doc_pages = [
    "quickstart",
    "datasets",
    "collection",
    "dashboards",
    "charts",
    "annotations",
    "api",
    "about",
]


def layout(**kwargs):
    return dmc.Container(
        fluid=True,
        p=0,
        pt=12,
        style={
            "display": "flex",
            "height": "calc(100vh - 53px)",
        },
        children=[
            dcc.Location("docs_url", refresh=False),
            dmc.Container(
                [
                    dmc.Tabs(
                        [
                            dmc.TabsList(
                                [dmc.Tab(p.title(), value=p) for p in doc_pages],
                            ),
                        ],
                        orientation="vertical",
                        id="docs_tabs",
                        variant="pills",
                        color="teal",
                    ),
                ],
                className="flex-start",
                pl=0,
                fluid=True,
            ),
            dmc.Divider(
                orientation="vertical",
            ),
            dmc.ScrollArea(
                id="doc_content",
                className="flex-grow-1",
                p=12,
                pt=0,
                style={
                    "overflowY": "auto",
                    "height": "100%",
                    "display": "flex",
                    "flexDirection": "column",
                    "flexGrow": 1,
                },
            ),
        ],
    )


@callback(
    Output("docs_tabs", "value"),
    Input("docs_url", "pathname"),
    State("docs_url", "hash"),
)
def update_page_by_hash(pn, hash):
    if hash:
        return hash.split("#")[1]
    return "quickstart"


@callback(
    Output("doc_content", "children"),
    Output("docs_url", "hash"),
    Input("docs_tabs", "value"),
)
def render_docs_content(active):
    if active:
        return (
                dcc.Markdown(
                    get_doc_page(active),
                    link_target="_blank",
                    highlight_config={"theme": "dark"},
                    dangerously_allow_html=True,
                ),
            f"#{active}",
        )
    else:
        return no_update  
