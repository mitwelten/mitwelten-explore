from dash import Dash, Output, Input, State, html, dcc, callback, MATCH, ctx, no_update
import uuid
from dash.exceptions import PreventUpdate
import dash_mantine_components as dmc
import math
from dash_iconify import DashIconify
import datetime


class TimeRangeAIO(html.Div):
    class ids:
        store = lambda aio_id: {
            "component": "TimeRangeAIO",
            "subcomponent": "store",
            "aio_id": aio_id,
        }
        store_set = lambda aio_id: {
            "component": "TimeRangeAIO",
            "subcomponent": "store_set",
            "aio_id": aio_id,
        }
        date_range_picker = lambda aio_id: {
            "component": "TimeRangeAIO",
            "subcomponent": "date_range_picker",
            "aio_id": aio_id,
        }
        date_step_left = lambda aio_id: {
            "component": "TimeRangeAIO",
            "subcomponent": "date_step_left",
            "aio_id": aio_id,
        }
        date_step_right = lambda aio_id: {
            "component": "TimeRangeAIO",
            "subcomponent": "date_step_right",
            "aio_id": aio_id,
        }
        date_zoom_in = lambda aio_id: {
            "component": "TimeRangeAIO",
            "subcomponent": "date_zoom_in",
            "aio_id": aio_id,
        }
        date_zoom_out = lambda aio_id: {
            "component": "TimeRangeAIO",
            "subcomponent": "date_zoom_out",
            "aio_id": aio_id,
        }

    ids = ids

    def __init__(
        self,
        dates=["2020-05-01", str(datetime.datetime.now().date())],
        store_props= None,#dict(storage_type="local"),
        aio_id=None,
    ):
        self.aio_id = aio_id if aio_id is not None else str(uuid.uuid4())
        self.store_props = store_props.copy() if store_props else {}

        super().__init__(
            [
                dcc.Store(
                    data=dates,
                    id=self.ids.store(self.aio_id),
                    **self.store_props,
                ),
                dcc.Store(
                    data=None,
                    id=self.ids.store_set(self.aio_id),
                    **self.store_props,
                ),
                dmc.Group(
                    [
                        dmc.ActionIcon(
                            DashIconify(icon="material-symbols:arrow-left", height=30),
                            size=36,
                            variant="default",
                            radius=0,
                            id=self.ids.date_step_left(self.aio_id),
                            style={
                                "border-top-left-radius": "4px",
                                "border-bottom-left-radius": "4px",
                                "border-right": "none",
                            },
                        ),
                        dmc.DateRangePicker(
                            id=self.ids.date_range_picker(self.aio_id),
                            value=dates,
                            style={"minWidth": 260},
                            icon=DashIconify(
                                icon="material-symbols:date-range-outline"
                            ),
                            clearable=False,
                            radius=0,
                        ),
                        dmc.ActionIcon(
                            DashIconify(icon="material-symbols:arrow-right", height=30),
                            size=36,
                            variant="default",
                            radius=0,
                            id=self.ids.date_step_right(self.aio_id),
                            className="border-start-0",
                            style={
                                "border-top-right-radius": "4px",
                                "border-bottom-right-radius": "4px",
                                "border-left": "none",
                            },
                        ),
                        dmc.Space(w=8),
                        dmc.ActionIcon(
                            DashIconify(icon="bi:zoom-out"),
                            size=36,
                            variant="default",
                            radius=0,
                            id=self.ids.date_zoom_out(self.aio_id),
                            style={
                                "border-top-left-radius": "4px",
                                "border-bottom-left-radius": "4px",
                            },
                        ),
                        dmc.ActionIcon(
                            DashIconify(icon="bi:zoom-in"),
                            size=36,
                            variant="default",
                            radius=0,
                            id=self.ids.date_zoom_in(self.aio_id),
                            style={
                                "border-top-right-radius": "4px",
                                "border-bottom-right-radius": "4px",
                                "border-left": "none",
                            },
                        ),
                    ],
                    spacing=0,
                    noWrap=True
                ),
            ]
        )
    @callback(
        Output(ids.store(MATCH), "data"),
        Input(ids.date_range_picker(MATCH), "value"),
    )
    def update_store_on_change(dr):
        if dr is not None:
            try:
                dr_s = datetime.datetime.fromisoformat(dr[0])
                dr_e = datetime.datetime.fromisoformat(dr[1])
            except:
                dr_s = datetime.datetime.strptime(dr[0], "%Y-%m-%d")
                dr_e = datetime.datetime.strptime(dr[1], "%Y-%m-%d")
            return [dr_s.isoformat(),dr_e.isoformat()]
        

    @callback(
        Output(ids.date_range_picker(MATCH), "value"),
        Input(ids.date_step_left(MATCH), "n_clicks"),
        Input(ids.date_step_right(MATCH), "n_clicks"),
        Input(ids.date_zoom_out(MATCH), "n_clicks"),
        Input(ids.date_zoom_in(MATCH), "n_clicks"),
        Input(ids.store_set(MATCH), "data"),
        State(ids.date_range_picker(MATCH), "value"),
    )
    def update_dr_from_controls(left, right, zoom_out, zoom_in,store_data, dr):
        trg = ctx.triggered_id
        if trg is not None:
            trg = trg.subcomponent
            if trg == "store_set":
                if store_data is not None:
                    return store_data
            try:
                dr_s = datetime.datetime.strptime(dr[0], "%Y-%m-%d")
                dr_e = datetime.datetime.strptime(dr[1], "%Y-%m-%d")
            except:
                dr_s = datetime.datetime.fromisoformat(dr[0])
                dr_e = datetime.datetime.fromisoformat(dr[1])
            td = dr_e - dr_s
            step_days = max(1, math.ceil(td.days / 7))
            if trg == "date_step_left":
                return [
                    dr_s.date() - datetime.timedelta(days=step_days),
                    dr_e.date() - datetime.timedelta(days=step_days),
                ]

            elif trg == "date_step_right":
                return [
                    dr_s.date() + datetime.timedelta(days=step_days),
                    dr_e.date() + datetime.timedelta(days=step_days),
                ]
            elif trg == "date_zoom_out":
                return [
                    dr_s.date() - datetime.timedelta(days=step_days),
                    dr_e.date() + datetime.timedelta(days=step_days),
                ]
            elif trg == "date_zoom_in":
                if math.ceil(td.days) >= 3:
                    return [
                        dr_s.date() + datetime.timedelta(days=step_days),
                        dr_e.date() - datetime.timedelta(days=step_days),
                    ]

                if math.ceil(td.days) == 2:

                    return [dr_s.date(), dr_e.date() - datetime.timedelta(days=step_days)]
                else:
                    return no_update
        return no_update


