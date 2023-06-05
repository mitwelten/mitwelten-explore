from dash import Dash, Output, Input, State, html, dcc, callback, MATCH, ctx
from dash.exceptions import PreventUpdate
import numpy as np
import uuid
from dashboard.charts.map_charts import generate_empty_map, generate_h3hexbin_map
from configuration import DEFAULT_LAT, DEFAULT_LON, DEFAULT_ZOOM


class H3HexBinMapAIO(html.Div):
    class ids:
        graph = lambda aio_id: {
            "component": "H3HexBinMapAIO",
            "subcomponent": "graph",
            "aio_id": aio_id,
        }
        store = lambda aio_id: {
            "component": "H3HexBinMapAIO",
            "subcomponent": "store",
            "aio_id": aio_id,
        }

    ids = ids

    def __init__(
        self,
        latitudes: list = None,
        longitudes: list = None,
        values: list = None,
        ids: list = None,
        agg_fcn=np.sum,
        default_zoomlevel=DEFAULT_ZOOM,
        graph_props=dict(
            config=dict(fillFrame=False, displayModeBar=False),
            responsive=True,
            style=dict(height="55vh"),
        ),
        store_props=None,
        store_clicked_props=None,
        aio_id=None,
    ):
        self.aio_id = aio_id if aio_id is not None else str(uuid.uuid4())
        self.graph_props = (
            graph_props.copy() if graph_props else {}
        )  # copy the dict so as to not mutate the user's dict
        self.store_props = store_props.copy() if store_props else {}

        self.default_zoom = default_zoomlevel

        data = None
        figure = generate_empty_map(
            clat=DEFAULT_LAT, clon=DEFAULT_LON, zoom=default_zoomlevel
        )

        if latitudes and longitudes and values:
            data = {
                "latitude": latitudes,
                "longitude": longitudes,
                "val": values,
                "id": ids if ids else [i for i in range(len(latitudes))],
            }
            figure = generate_h3hexbin_map(
                latitudes,
                longitudes,
                values,
                data.get("id"),
                # ids if ids else range(len(latitudes)),
                self.default_zoom,
            )

        super().__init__(
            [  # Equivalent to `html.Div([...])`
                dcc.Store(
                    data=data, id=self.ids.store(self.aio_id), **self.store_props
                ),
                dcc.Graph(
                    figure=figure, id=self.ids.graph(self.aio_id),  **self.graph_props
                ),
            ]
        )

    @callback(
        Output(ids.graph(MATCH), "figure"),
        Input(ids.graph(MATCH), "relayoutData"),
        Input(ids.store(MATCH), "data"),
        State(ids.store(MATCH), "data"),
        # prevent_initial_callbacks=True,
    )
    def update_hexbins(event_data, data_input, data):
        if ctx.triggered_id is None or data is None:
            raise PreventUpdate

        trg_subcomponents = [
            v.get("subcomponent") for v in list(ctx.triggered_prop_ids.values())
        ]

        if "store" in trg_subcomponents:
            return generate_h3hexbin_map(
                data.get("latitude"),
                data.get("longitude"),
                data.get("val"),
                data.get("id"),
            )
        elif "graph" in trg_subcomponents:
            if event_data.get("autosize") == True:
                return  generate_h3hexbin_map(
                data.get("latitude"),
                data.get("longitude"),
                data.get("val"),
                data.get("id"),
                )


            zoomlvl = event_data.get("mapbox.zoom")
            center_coords = event_data.get("mapbox.center")
            if None in [zoomlvl, center_coords]:
                raise PreventUpdate
            center = (center_coords.get("lat"), center_coords.get("lon"))

            return generate_h3hexbin_map(
                data.get("latitude"),
                data.get("longitude"),
                data.get("val"),
                data.get("id"),
                zoom=zoomlvl,
                clat=center[0],
                clon=center[1],
            )

        raise PreventUpdate