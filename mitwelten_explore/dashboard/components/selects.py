import dash_mantine_components as dmc
from dashboard.styles import get_icon
from dashboard.components.overlays import tooltip

# TODO: move icons to styles.icons


def confidence_threshold_select(id, value=None, visible=True, **kwargs):
    return tooltip(
        dmc.Select(
            placeholder="Confidence",
            id=id,
            value=value,
            data=[{"value": i / 20, "label": f"{i*5} %"} for i in range(1, 20)]
            + [
                {"value": i, "label": f"{int(i*100)} %"}
                for i in [0.96, 0.97, 0.98, 0.99]
            ],
            style={"minWidth": 120} if visible else {"display": "none"},
            icon=get_icon(icon="fluent:math-formula-20-filled"),
            **kwargs,
        ),
        "Minimum Confidence",
        position="bottom",
    )


def agg_fcn_select(id, value=None, visible=True, **kwargs):
    return tooltip(
        dmc.Select(
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
            icon=get_icon(icon="fluent:math-formula-20-filled"),
            **kwargs,
        ),
        "Aggregation Function",
        position="bottom",
    )


def time_bucket_select(id, value=None, **kwargs):
    return tooltip(
        dmc.Select(
            placeholder="Time Bucket",
            id=id,
            value=value,
            data=[
                {"value": "10min", "label": "10 Minutes"},
                {"value": "30min", "label": "30 Minutes"},
                {"value": "1h", "label": "1 Hour"},
                {"value": "2h", "label": "2 Hour"},
                {"value": "3h", "label": "3 Hour"},
                {"value": "6h", "label": "6 Hour"},
                {"value": "12h", "label": "12 Hour"},
                {"value": "1d", "label": "1 Day"},
                {"value": "2d", "label": "2 Days"},
                {"value": "1w", "label": "1 Week"},
                {"value": "4w", "label": "4 Weeks"},
            ],
            style={"minWidth": 120},
            icon=get_icon(icon="ic:round-access-time"),
            **kwargs,
        ),
        "Time Bucket Width",
        position="bottom",
    )
