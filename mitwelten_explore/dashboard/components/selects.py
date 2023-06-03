import dash_mantine_components as dmc
from dash_iconify import DashIconify

# TODO: move icons to styles.icons

def confidence_threshold_select(id, value=None, visible=True, **kwargs):
    return dmc.Select(
        placeholder="Confidence",
        id=id,
        value=value,
        data=[{"value": i / 20, "label": f"{i*5} %"} for i in range(1, 20)],
        style={"minWidth": 120} if visible else {"display": "none"},
        icon=DashIconify(icon="fluent:math-formula-20-filled"),
        **kwargs,
    )


def agg_fcn_select(id, value=None, visible=True, **kwargs):
    return dmc.Select(
        placeholder="Aggregation",
        id=id,
        value=value,
        data=[
            {"value": "sum", "label": "sum()"},
            {"value": "mean", "label": "mean()"},
            {"value": "median", "label": "median()"},
            {"value": "max", "label": "max()"},
            {"value": "min", "label": "min()"},
        ],
        style={"minWidth": 120} if visible else {"display": "none"},
        icon=DashIconify(icon="fluent:math-formula-20-filled"),
        **kwargs,
    )


def time_bucket_select(id, value=None, **kwargs):
    return dmc.Select(
        placeholder="Time Bucket",
        id=id,
        value=value,
        data=[
            {"value": "10min", "label": "10 Minutes"},
            {"value": "30min", "label": "30 Minutes"},
            {"value": "1h", "label": "1 Hour"},
            {"value": "2h", "label": "2 Hour"},
            {"value": "6h", "label": "6 Hour"},
            {"value": "12h", "label": "12 Hour"},
            {"value": "1d", "label": "1 Day"},
            {"value": "2d", "label": "2 Days"},
            {"value": "1w", "label": "1 Week"},
            {"value": "4w", "label": "4 Weeks"},
        ],
        style={"minWidth": 120},
        icon=DashIconify(icon="ic:round-access-time"),
        **kwargs,
    )